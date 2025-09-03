from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import DashScopeEmbeddings
from langchain.chat_models import init_chat_model
from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    AIMessagePromptTemplate
)
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, module="langchain.memory")
from langchain.memory import ConversationBufferMemory
from config import API_KEY, BASE_URL, MODEL_NAME, EMBEDDING_MODEL_NAME
import os
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain.schema import Document
import glob
import json


class RAGTool:
    def __init__(self):
        self.llm = init_chat_model(
            MODEL_NAME,
            model_provider="openai",
            api_key=API_KEY,
            base_url=BASE_URL
        )
        self.embeddings = DashScopeEmbeddings(
            model=EMBEDDING_MODEL_NAME,
            dashscope_api_key=API_KEY
        )
        self.vectorstore = Chroma(persist_directory="knowledge_base", embedding_function=self.embeddings)
        
        prompt_path = os.path.join(os.path.dirname(__file__), '../prompts/rag_prompt.txt')
        with open(prompt_path, 'r', encoding='utf-8') as f:
            self.system_prompt = f.read().strip()
        self.memory = ConversationBufferMemory(return_messages=True)

    def _get_prompt(self, prompt_filename):
        prompt_path = os.path.join(os.path.dirname(__file__), '../prompts', prompt_filename)
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read().strip()

    def _extract_pdf_info(self, pdf_path):
        """Extracts full text, summary, and biosimulation models from a PDF file."""
        loader = PyPDFLoader(pdf_path)
        pages = loader.load()
        full_text = "\n".join([page.page_content for page in pages])
        # Use LLM to summarize
        summary_prompt_template = self._get_prompt('pdf_summary_prompt.txt')
        summary_prompt = summary_prompt_template.replace('{content}', full_text[:4000])
        summary = self._call_llm(summary_prompt, system_prompt="You are a scientific paper summarizer.")
        # Use LLM to extract biosimulation models
        models_prompt_template = self._get_prompt('pdf_models_prompt.txt')
        models_prompt = models_prompt_template.replace('{content}', full_text[:4000])
        models_info = self._call_llm(models_prompt, system_prompt="You are a biosimulation model extractor.")
        
        # Extract model names for saving to file
        models_extractor_prompt_template = self._get_prompt('biosimulation_models_extractor_prompt.txt')
        models_extractor_prompt = models_extractor_prompt_template.replace('{content}', full_text[:4000])
        model_names = self._call_llm(models_extractor_prompt, system_prompt="You are a biosimulation model name extractor.")
        
        return full_text, summary, models_info, model_names

    def _save_model_names_to_file(self, model_names: str, source_file: str):
        """Save extracted model names to BiosimulationModels.txt file."""
        if not model_names or model_names.strip() == "None":
            return
        
        # Parse model names (comma-separated)
        models = [name.strip() for name in model_names.split(',') if name.strip() and name.strip() != "None"]
        if not models:
            return
        
        # Create or append to BiosimulationModels.txt
        models_file_path = os.path.join(os.path.dirname(__file__), '..', 'BiosimulationModels.txt')
        
        # Read existing models to avoid duplicates
        existing_models = set()
        if os.path.exists(models_file_path):
            with open(models_file_path, 'r', encoding='utf-8') as f:
                existing_models = set(line.strip() for line in f.readlines() if line.strip())
        
        # Add new models
        new_models = []
        for model in models:
            if model not in existing_models:
                new_models.append(model)
                existing_models.add(model)
        
        # Write all models back to file
        with open(models_file_path, 'w', encoding='utf-8') as f:
            for model in sorted(existing_models):
                f.write(f"{model}\n")
        
        if new_models:
            print(f"Added new biosimulation models: {', '.join(new_models)}")
            print(f"Total models in BiosimulationModels.txt: {len(existing_models)}")

    def get_saved_biosimulation_models(self) -> list:
        """Get the list of saved biosimulation models from the text file."""
        models_file_path = os.path.join(os.path.dirname(__file__), '..', 'BiosimulationModels.txt')
        
        if not os.path.exists(models_file_path):
            return []
        
        with open(models_file_path, 'r', encoding='utf-8') as f:
            models = [line.strip() for line in f.readlines() if line.strip()]
        
        return sorted(models)

    def update_knowledge_base(self):
        """Loads new documents from .txt and .pdf files into the vector store, avoiding duplicates."""
        directory_path = os.path.join(os.path.dirname(__file__), '..', 'knowledge_base')
        paper_path = os.path.join(os.path.dirname(__file__), '..', 'paper')
        existing_docs_metadatas = self.vectorstore.get().get('metadatas', [])
        existing_sources = {meta['source'] for meta in existing_docs_metadatas if 'source' in meta}

        # TXT incremental
        new_files_to_load = []
        for root, _, files in os.walk(directory_path):
            for file in files:
                if file.endswith(".txt"):
                    file_path = os.path.join(root, file)
                    if file_path not in existing_sources:
                        new_files_to_load.append(file_path)

        # PDF incremental
        new_pdfs_to_load = []
        for root, _, files in os.walk(paper_path):
            for file in files:
                if file.lower().endswith(".pdf"):
                    file_path = os.path.join(root, file)
                    if file_path not in existing_sources:
                        new_pdfs_to_load.append(file_path)

        if not new_files_to_load and not new_pdfs_to_load:
            print("Knowledge base is up to date.")
            return

        all_docs = []
        # Load new txt
        for file_path in new_files_to_load:
            print(f"Loading document: {file_path}")
            loader = TextLoader(file_path, encoding='utf-8')
            docs = loader.load()
            for doc in docs:
                doc.metadata['source'] = file_path
                doc.metadata['type'] = 'txt'
            all_docs.extend(docs)
        # Load new pdfs
        for pdf_path in new_pdfs_to_load:
            print(f"Processing PDF: {pdf_path}")
            full_text, summary, models_info, model_names = self._extract_pdf_info(pdf_path)
            
            # Save model names to file
            self._save_model_names_to_file(model_names, pdf_path)
            
            # Store full text
            all_docs.append(Document(page_content=full_text, metadata={
                'source': pdf_path,
                'type': 'pdf_fulltext',
                'title': os.path.basename(pdf_path),
            }))
            # Store summary
            all_docs.append(Document(page_content=summary, metadata={
                'source': pdf_path,
                'type': 'pdf_summary',
                'title': os.path.basename(pdf_path),
            }))
            # Store models info
            all_docs.append(Document(page_content=models_info, metadata={
                'source': pdf_path,
                'type': 'pdf_models',
                'title': os.path.basename(pdf_path),
            }))

        text_splitter = CharacterTextSplitter(chunk_size=1500, chunk_overlap=100)
        documents = text_splitter.split_documents(all_docs)
        
        # Filter out documents that are too long for the embedding API
        filtered_documents = []
        for doc in documents:
            if len(doc.page_content) <= 2000:  # Leave some buffer for the 2048 limit
                filtered_documents.append(doc)
            else:
                # Split long documents further
                long_text = doc.page_content
                while len(long_text) > 2000:
                    # Take the first 2000 characters
                    chunk = long_text[:2000]
                    # Try to break at a sentence boundary
                    last_period = chunk.rfind('.')
                    last_newline = chunk.rfind('\n')
                    break_point = max(last_period, last_newline)
                    if break_point > 1500:  # Only break if we have a reasonable boundary
                        chunk = chunk[:break_point + 1]
                        long_text = long_text[break_point + 1:]
                    else:
                        long_text = long_text[2000:]
                    
                    filtered_documents.append(Document(
                        page_content=chunk,
                        metadata=doc.metadata.copy()
                    ))
                
                if long_text:  # Add any remaining text
                    filtered_documents.append(Document(
                        page_content=long_text,
                        metadata=doc.metadata.copy()
                    ))
        
        print(f"Adding {len(filtered_documents)} document chunks to the vector store.")
        self.vectorstore.add_documents(filtered_documents)
        print("Successfully updated the knowledge base.")

    def force_update_knowledge_base(self):
        """Forcefully reloads all .txt and .pdf files into the vector store, overwriting existing data."""
        directory_path = os.path.join(os.path.dirname(__file__), '..', 'knowledge_base')
        paper_path = os.path.join(os.path.dirname(__file__), '..', 'paper')
        print("Force updating the knowledge base: resetting all previous data...")
        
        # Clear the existing collection by deleting and recreating it
        try:
            # Try to delete the collection
            self.vectorstore._client.delete_collection(self.vectorstore._collection.name)
        except Exception as e:
            print(f"Warning: Could not delete existing collection: {e}")
        
        # Recreate the vectorstore with the same configuration
        self.vectorstore = Chroma(persist_directory="knowledge_base", embedding_function=self.embeddings)

        all_docs = []
        # All txt
        for root, _, files in os.walk(directory_path):
            for file in files:
                if file.endswith(".txt"):
                    file_path = os.path.join(root, file)
                    loader = TextLoader(file_path, encoding='utf-8')
                    docs = loader.load()
                    for doc in docs:
                        doc.metadata['source'] = file_path
                        doc.metadata['type'] = 'txt'
                    all_docs.extend(docs)
        # All pdfs
        for root, _, files in os.walk(paper_path):
            for file in files:
                if file.lower().endswith(".pdf"):
                    pdf_path = os.path.join(root, file)
                    full_text, summary, models_info, model_names = self._extract_pdf_info(pdf_path)
                    
                    # Save model names to file
                    self._save_model_names_to_file(model_names, pdf_path)
                    
                    # Store full text
                    all_docs.append(Document(page_content=full_text, metadata={
                        'source': pdf_path,
                        'type': 'pdf_fulltext',
                        'title': os.path.basename(pdf_path),
                    }))
                    # Store summary
                    all_docs.append(Document(page_content=summary, metadata={
                        'source': pdf_path,
                        'type': 'pdf_summary',
                        'title': os.path.basename(pdf_path),
                    }))
                    # Store models info
                    all_docs.append(Document(page_content=models_info, metadata={
                        'source': pdf_path,
                        'type': 'pdf_models',
                        'title': os.path.basename(pdf_path),
                    }))

        text_splitter = CharacterTextSplitter(chunk_size=1500, chunk_overlap=100)
        documents = text_splitter.split_documents(all_docs)
        
        # Filter out documents that are too long for the embedding API
        filtered_documents = []
        for doc in documents:
            if len(doc.page_content) <= 2000:  # Leave some buffer for the 2048 limit
                filtered_documents.append(doc)
            else:
                # Split long documents further
                long_text = doc.page_content
                while len(long_text) > 2000:
                    # Take the first 2000 characters
                    chunk = long_text[:2000]
                    # Try to break at a sentence boundary
                    last_period = chunk.rfind('.')
                    last_newline = chunk.rfind('\n')
                    break_point = max(last_period, last_newline)
                    if break_point > 1500:  # Only break if we have a reasonable boundary
                        chunk = chunk[:break_point + 1]
                        long_text = long_text[break_point + 1:]
                    else:
                        long_text = long_text[2000:]
                    
                    filtered_documents.append(Document(
                        page_content=chunk,
                        metadata=doc.metadata.copy()
                    ))
                
                if long_text:  # Add any remaining text
                    filtered_documents.append(Document(
                        page_content=long_text,
                        metadata=doc.metadata.copy()
                    ))
        
        print(f"Adding {len(filtered_documents)} document chunks to the vector store.")
        self.vectorstore.add_documents(filtered_documents)
        print("Successfully force updated the knowledge base.")

    def _call_llm(self, prompt: str, system_prompt: str = None, tools: list = None) -> str:
        try:
            messages = []
            if system_prompt:
                messages.append(SystemMessagePromptTemplate.from_template(system_prompt))
            history = self.memory.load_memory_variables({})["history"]
            messages.extend(history)
            messages.append(HumanMessagePromptTemplate.from_template("{input}"))
            if tools:
                messages.extend(tools)
            chat_prompt = ChatPromptTemplate.from_messages(messages)
            full_prompt = chat_prompt.format_prompt(input=prompt)
            result = self.llm.invoke(full_prompt.to_messages())
            output = getattr(result, "content", str(result))
            self.memory.save_context({"input": prompt}, {"output": output})
            return output
        except Exception as e:
            error_message = f"Error calling LLM: {str(e)}"
            self.memory.save_context({"input": prompt}, {"output": error_message})
            return error_message

    def run(self, prompt: str, memory=None, tools: list = None) -> str:
        # 检索知识内容并拼接到用户输入
        docs = self.vectorstore.similarity_search(prompt, k=3)
        context = '\n'.join([doc.page_content for doc in docs])
        user_input = f"Relevant Knowledge:\n{context}\nUser Question: {prompt}"
        return self._call_llm(user_input, system_prompt=self.system_prompt, tools=tools)

    def chat(self, prompt: str, memory=None, tools: list = None) -> str:
        return self._call_llm(prompt, system_prompt=self.system_prompt, tools=tools)
    
    def search(self, query: str, top_k: int = 5) -> list:
        """
        Search the knowledge base for relevant documents
        
        Args:
            query (str): Search query
            top_k (int): Number of top results to return
            
        Returns:
            list: List of dictionaries containing search results
        """
        try:
            # Search the vector store
            docs = self.vectorstore.similarity_search(query, k=top_k)
            
            # Convert to list of dictionaries
            results = []
            for doc in docs:
                result = {
                    'content': doc.page_content,
                    'source': doc.metadata.get('source', 'Unknown'),
                    'type': doc.metadata.get('type', 'Unknown'),
                    'title': doc.metadata.get('title', 'Unknown')
                }
                results.append(result)
            
            return results
            
        except Exception as e:
            print(f"Error searching knowledge base: {e}")
            return []

    def _get_literature_agent(self):
        """Get literature agent instance"""
        try:
            from agent.literature_agent import LiteratureAgent
            return LiteratureAgent()
        except ImportError:
            print("Warning: Literature agent not available")
            return None

    def _trigger_literature_search(self, user_input: str) -> str:
        """Trigger literature agent to search and build temporary knowledge base"""
        try:
            literature_agent = self._get_literature_agent()
            if not literature_agent:
                return None
            
            print("Triggering literature agent to search for relevant papers...")
            result = literature_agent.run(user_input)
            
            # Extract knowledge base ID from result
            kb_id = None
            if "Temporary Knowledge Base Created:" in result:
                lines = result.split('\n')
                for line in lines:
                    if "Knowledge Base ID:" in line:
                        kb_id = line.split("Knowledge Base ID:")[1].strip()
                        break
            
            return kb_id
            
        except Exception as e:
            print(f"Error triggering literature search: {e}")
            return None

    def _search_temporary_knowledge_bases(self, query: str, top_k: int = 3) -> list:
        """Search all available temporary knowledge bases"""
        try:
            temp_kb_dir = os.path.join(os.path.dirname(__file__), '..', 'temp_knowledge_base')
            if not os.path.exists(temp_kb_dir):
                return []
            
            all_results = []
            
            # Get all temporary knowledge base directories
            kb_dirs = [d for d in os.listdir(temp_kb_dir) 
                      if os.path.isdir(os.path.join(temp_kb_dir, d))]
            
            for kb_id in kb_dirs:
                kb_path = os.path.join(temp_kb_dir, kb_id)
                kb_info_path = os.path.join(kb_path, 'kb_info.json')
                
                # Check if knowledge base info exists
                if not os.path.exists(kb_info_path):
                    continue
                
                try:
                    # Create temporary vector store for this knowledge base
                    temp_vectorstore = Chroma(persist_directory=kb_path, embedding_function=self.embeddings)
                    
                    # Search in this knowledge base
                    docs = temp_vectorstore.similarity_search(query, k=top_k)
                    
                    for doc in docs:
                        result = {
                            'content': doc.page_content,
                            'source': doc.metadata.get('source', 'Unknown'),
                            'original_url': doc.metadata.get('original_url', 'Unknown'),
                            'type': doc.metadata.get('type', 'Unknown'),
                            'title': doc.metadata.get('title', 'Unknown'),
                            'kb_id': kb_id,
                            'kb_type': 'temporary'
                        }
                        all_results.append(result)
                        
                except Exception as e:
                    print(f"Error searching temporary knowledge base {kb_id}: {e}")
                    continue
            
            return all_results
            
        except Exception as e:
            print(f"Error searching temporary knowledge bases: {e}")
            return []

    def _create_citation_instructions(self, source_info: list) -> str:
        """Create citation instructions for the LLM"""
        if not source_info:
            return ""
        
        instructions = """IMPORTANT CITATION INSTRUCTIONS:
When using information from the knowledge base, you MUST cite the sources using the provided identifiers [LOCAL_X] or [TEMP_X].

Available Sources:"""
        
        for source in source_info:
            source_id = source['id']
            title = source['title']
            source_path = source['source']
            doc_type = source['type']
            kb_type = source['kb_type']
            original_url = source.get('original_url', 'Unknown')
            
            instructions += f"\n[{source_id}] {title}"
            instructions += f"\n   Type: {doc_type}"
            instructions += f"\n   Source: {source_path}"
            
            if kb_type == 'local':
                instructions += f"\n   Knowledge Base: Local"
                if original_url != 'Unknown':
                    instructions += f"\n   URL: {original_url}"
            else:
                instructions += f"\n   Knowledge Base: Temporary (ID: {source.get('kb_id', 'Unknown')})"
                if original_url != 'Unknown':
                    instructions += f"\n   URL: {original_url}"
        
        instructions += """

CITATION FORMAT:
- When referencing information, use the format: [source_id]
- Example: "According to [LOCAL_1], FBA is a constraint-based modeling approach..."
- Always include citations for any factual information you use
- At the end of your response, provide a "References" section with full source details and URLs

Example response format:
[Your answer with citations like [LOCAL_1] and [TEMP_2]]

References:
[LOCAL_1] [Title] - [Source path] - [URL if available]
[TEMP_2] [Title] - [Source path] - [URL if available]"""
        
        return instructions

    def _extract_paper_url(self, source_path: str) -> str:
        """Extract or generate URL for a paper source"""
        try:
            # If it's a local file, try to find corresponding URL
            if source_path.endswith('.pdf'):
                filename = os.path.basename(source_path)
                
                # Check if it's in the downloads/papers directory (from literature agent)
                if 'downloads/papers' in source_path:
                    # This is a downloaded paper, we might have URL info in the filename
                    # For now, return a placeholder
                    return f"Downloaded paper: {filename}"
                
                # Check if it's in the paper directory (local papers)
                elif 'paper/' in source_path:
                    # This is a local paper, return file path
                    return f"Local file: {source_path}"
                
                else:
                    return f"File: {source_path}"
            
            # If it's already a URL, return it
            elif source_path.startswith(('http://', 'https://')):
                return source_path
            
            else:
                return f"Source: {source_path}"
                
        except Exception as e:
            return f"Source: {source_path}"

    def run(self, prompt: str, memory=None, tools: list = None) -> str:
        # Step 1: Trigger literature agent to search and build temporary knowledge base
        temp_kb_id = self._trigger_literature_search(prompt)
        
        # Step 2: Search both local and temporary knowledge bases
        local_docs = self.vectorstore.similarity_search(prompt, k=3)
        temp_docs = self._search_temporary_knowledge_bases(prompt, top_k=3)
        
        # Step 3: Prepare context with source information
        all_contexts = []
        source_info = []
        
        # Add local knowledge base results with source tracking
        if local_docs:
            local_contexts = []
            for doc in local_docs:
                source = doc.metadata.get('source', 'Unknown')
                title = doc.metadata.get('title', 'Unknown')
                doc_type = doc.metadata.get('type', 'Unknown')
                
                # Create source identifier
                source_id = f"LOCAL_{len(source_info) + 1}"
                source_info.append({
                    'id': source_id,
                    'title': title,
                    'source': source,
                    'type': doc_type,
                    'kb_type': 'local'
                })
                
                local_contexts.append(f"[{source_id}] {doc.page_content}")
            
            local_context = '\n\n'.join(local_contexts)
            all_contexts.append(f"Local Knowledge Base:\n{local_context}")
        
        # Add temporary knowledge base results with source tracking
        if temp_docs:
            temp_contexts = []
            for doc in temp_docs:
                source = doc.get('source', 'Unknown')
                title = doc.get('title', 'Unknown')
                doc_type = doc.get('type', 'Unknown')
                kb_id = doc.get('kb_id', 'Unknown')
                original_url = doc.get('original_url', 'Unknown')
                
                # Create source identifier
                source_id = f"TEMP_{len(source_info) + 1}"
                source_info.append({
                    'id': source_id,
                    'title': title,
                    'source': source,
                    'original_url': original_url,
                    'type': doc_type,
                    'kb_type': 'temporary',
                    'kb_id': kb_id
                })
                
                temp_contexts.append(f"[{source_id}] {doc['content']}")
            
            temp_context = '\n\n'.join(temp_contexts)
            all_contexts.append(f"Temporary Knowledge Base (from Literature Search):\n{temp_context}")
        
        # Step 4: Create enhanced prompt with citation instructions
        if all_contexts:
            context = '\n\n'.join(all_contexts)
            
            # Create citation instructions
            citation_instructions = self._create_citation_instructions(source_info)
            
            user_input = f"""Relevant Knowledge:
{context}

User Question: {prompt}

{citation_instructions}"""
        else:
            user_input = prompt
        
        # Step 5: Add information about temporary knowledge base if created
        if temp_kb_id:
            user_input += f"\n\nNote: A temporary knowledge base (ID: {temp_kb_id}) was created from literature search. You can query it directly using: literature_query {temp_kb_id} <your question>"
        
        return self._call_llm(user_input, system_prompt=self.system_prompt, tools=tools) 
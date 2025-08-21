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
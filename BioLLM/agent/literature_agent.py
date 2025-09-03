from langchain.chat_models import init_chat_model
from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate
)
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, module="langchain.memory")
from langchain.memory import ConversationBufferMemory
from agent.base import BaseAgent
from agent.search_tool import SearchTool
from config import API_KEY, BASE_URL, MODEL_NAME, EMBEDDING_MODEL_NAME
import os
import re
import requests
from urllib.parse import urlparse, urljoin
import time
import uuid
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.schema import Document
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import json
import arxiv
from semanticscholar import SemanticScholar
import crossref_commons.retrieval

class LiteratureAgent(BaseAgent):
    def __init__(self):
        self.llm = init_chat_model(
            MODEL_NAME,
            model_provider="openai",
            api_key=API_KEY,
            base_url=BASE_URL
        )
        # Read literature agent specific system prompt
        prompt_path = os.path.join(os.path.dirname(__file__), '../prompts/literature_agent_prompt.txt')
        with open(prompt_path, 'r', encoding='utf-8') as f:
            self.system_prompt = f.read().strip()
        self.memory = ConversationBufferMemory(return_messages=True)
        self.search_tool = SearchTool()
        
        # Create downloads directory for papers
        self.downloads_dir = os.path.join(os.path.dirname(__file__), '../downloads/papers')
        os.makedirs(self.downloads_dir, exist_ok=True)
        
        # Initialize embeddings for temporary knowledge base
        self.embeddings = DashScopeEmbeddings(
            model=EMBEDDING_MODEL_NAME,
            dashscope_api_key=API_KEY
        )
        
        # Temporary knowledge base directory
        self.temp_knowledge_dir = os.path.join(os.path.dirname(__file__), '../temp_knowledge_base')
        os.makedirs(self.temp_knowledge_dir, exist_ok=True)
        
        # Reset temporary knowledge base on startup
        self._reset_temporary_knowledge_base()
        
        # PubMed API settings
        self.pubmed_base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
        self.pubmed_email = "your-email@example.com"  # Should be configured
        self.pubmed_tool = "BioLLM_LiteratureAgent"
        
        # Academic search APIs
        self.semantic_scholar = SemanticScholar()
        self.crossref_user_agent = "BioLLM_LiteratureAgent/1.0 (mailto:your-email@example.com)"

    def _reset_temporary_knowledge_base(self):
        """Reset temporary knowledge base on startup - clear all temporary KBs"""
        try:
            if os.path.exists(self.temp_knowledge_dir):
                # Remove all contents in temp_knowledge_base directory
                for item in os.listdir(self.temp_knowledge_dir):
                    item_path = os.path.join(self.temp_knowledge_dir, item)
                    if os.path.isdir(item_path):
                        import shutil
                        shutil.rmtree(item_path)
                    elif os.path.isfile(item_path):
                        os.remove(item_path)
                print(f"✅ Temporary knowledge base reset: cleared {self.temp_knowledge_dir}")
            else:
                print(f"ℹ️ Temporary knowledge base directory does not exist: {self.temp_knowledge_dir}")
        except Exception as e:
            print(f"⚠️ Warning: Failed to reset temporary knowledge base: {e}")

    def reset_temporary_knowledge_base(self):
        """Manual reset of temporary knowledge base - can be called by user"""
        try:
            if os.path.exists(self.temp_knowledge_dir):
                # Count items before deletion
                item_count = len(os.listdir(self.temp_knowledge_dir))
                
                # Remove all contents in temp_knowledge_base directory
                for item in os.listdir(self.temp_knowledge_dir):
                    item_path = os.path.join(self.temp_knowledge_dir, item)
                    if os.path.isdir(item_path):
                        import shutil
                        shutil.rmtree(item_path)
                    elif os.path.isfile(item_path):
                        os.remove(item_path)
                
                print(f"✅ Temporary knowledge base manually reset: cleared {item_count} items from {self.temp_knowledge_dir}")
                return f"Successfully reset temporary knowledge base. Cleared {item_count} items."
            else:
                print(f"ℹ️ Temporary knowledge base directory does not exist: {self.temp_knowledge_dir}")
                return "Temporary knowledge base directory does not exist."
        except Exception as e:
            error_msg = f"Failed to reset temporary knowledge base: {e}"
            print(f"❌ {error_msg}")
            return error_msg

    def _call_llm(self, prompt: str, system_prompt: str = None) -> str:
        """Call LLM with the given prompt and system prompt"""
        try:
            messages = []
            if system_prompt:
                messages.append(SystemMessagePromptTemplate.from_template(system_prompt))
            history = self.memory.load_memory_variables({})["history"]
            messages.extend(history)
            messages.append(HumanMessagePromptTemplate.from_template("{input}"))
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

    def extract_keywords(self, user_input: str) -> str:
        """Extract biological research keywords from user input using LLM with smart reduction"""
        try:
            # Use enhanced prompt for better keyword extraction with confidence scoring
            enhanced_prompt = f"""
Extract the most important biological research keywords from the following text. 
Focus on the core scientific concepts and technical terms.
Return only 3-5 most relevant keywords in order of importance (highest confidence first).
Format: keyword1, keyword2, keyword3

User input: {user_input}
"""
            
            keywords = self._call_llm(enhanced_prompt, system_prompt="You are an expert in biological research keyword extraction. Focus on the most important technical terms and concepts.")
            
            # Clean up the response - remove any extra text and get only keywords
            keywords = keywords.strip()
            # Remove any explanatory text and keep only the comma-separated keywords
            if ":" in keywords:
                keywords = keywords.split(":", 1)[1].strip()
            
            # Apply intelligent keyword reduction and add core keywords
            keywords = self._optimize_keywords_for_search(keywords)
            
            return keywords
        except Exception as e:
            print(f"Error extracting keywords: {e}")
            return "computational biology, metabolic model"

    def _optimize_keywords_for_search(self, keywords: str) -> str:
        """Optimize keywords for search by selecting core terms with highest confidence"""
        try:
            # Split and clean keywords
            keyword_list = [kw.strip() for kw in keywords.split(',') if kw.strip()]
            
            # Core keywords that should always be included
            core_keywords = ["computational biology", "metabolic model"]
            
            # High-confidence biological keywords (prioritize these)
            high_confidence_bio_terms = [
                "gene deletion", "knockout", "crispr", "genome editing",
                "flux balance analysis", "fba", "cobra", "metabolic network",
                "systems biology", "bioinformatics", "pathway analysis",
                "protein function", "gene expression", "transcriptomics"
            ]
            
            # Select up to 2 high-confidence LLM keywords
            selected_llm_keywords = []
            for kw in keyword_list[:3]:  # Take first 3 from LLM (highest confidence)
                kw_lower = kw.lower()
                # Check if it's a high-confidence biological term
                if any(bio_term in kw_lower for bio_term in high_confidence_bio_terms):
                    selected_llm_keywords.append(kw)
                    if len(selected_llm_keywords) >= 2:
                        break
            
            # If we don't have enough high-confidence terms, add the first LLM keywords
            if len(selected_llm_keywords) < 2:
                for kw in keyword_list[:2]:
                    if kw not in selected_llm_keywords:
                        selected_llm_keywords.append(kw)
                        if len(selected_llm_keywords) >= 2:
                            break
            
            # Combine core keywords with selected LLM keywords
            final_keywords = []
            
            # Add core keywords first
            for core_kw in core_keywords:
                # Check if already covered by LLM keywords
                covered = False
                for llm_kw in selected_llm_keywords:
                    if core_kw in llm_kw.lower() or llm_kw.lower() in core_kw:
                        covered = True
                        break
                if not covered:
                    final_keywords.append(core_kw)
            
            # Add selected LLM keywords
            final_keywords.extend(selected_llm_keywords)
            
            # Limit to 4 keywords maximum for optimal search performance
            final_keywords = final_keywords[:4]
            
            result = ', '.join(final_keywords)
            print(f"🎯 Optimized keywords for search: {result}")
            return result
            
        except Exception as e:
            print(f"Error optimizing keywords: {e}")
            return "computational biology, metabolic model"

    def _add_core_keywords(self, keywords: str) -> str:
        """Add core keywords if they don't exist in the extracted keywords"""
        core_keywords = ["Computational Biology", "Metabolic model"]
        
        # 将关键词转换为小写进行比较
        keywords_lower = keywords.lower()
        existing_keywords = set(keywords_lower.split(','))
        
        # 检查并添加缺失的核心关键词
        missing_keywords = []
        for core_keyword in core_keywords:
            core_keyword_lower = core_keyword.lower()
            if core_keyword_lower not in existing_keywords:
                # 检查是否有部分匹配
                found = False
                for existing in existing_keywords:
                    if core_keyword_lower in existing or existing in core_keyword_lower:
                        found = True
                        break
                if not found:
                    missing_keywords.append(core_keyword)
        
        # 添加缺失的核心关键词
        if missing_keywords:
            print(f"Adding core keywords: {', '.join(missing_keywords)}")
            keywords = f"{keywords}, {', '.join(missing_keywords)}"
        
        return keywords

    def _get_prompt(self, prompt_filename):
        """Get prompt template from file"""
        prompt_path = os.path.join(os.path.dirname(__file__), '../prompts', prompt_filename)
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read().strip()

    def _extract_pdf_info(self, pdf_path):
        """Extracts full text, summary, and biosimulation models from a PDF file."""
        try:
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
        except Exception as e:
            print(f"Error extracting PDF info from {pdf_path}: {e}")
            return "", "", "", ""

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

    def _build_temporary_knowledge_base(self, downloaded_papers: list) -> str:
        """Build a temporary knowledge base from downloaded PDF files"""
        if not downloaded_papers:
            return "No papers to process for knowledge base."
        
        print("Building temporary knowledge base from downloaded papers...")
        
        # Create a unique temporary knowledge base
        temp_kb_id = str(uuid.uuid4())
        temp_kb_path = os.path.join(self.temp_knowledge_dir, temp_kb_id)
        os.makedirs(temp_kb_path, exist_ok=True)
        
        # Create vector store for temporary knowledge base
        temp_vectorstore = Chroma(persist_directory=temp_kb_path, embedding_function=self.embeddings)
        
        all_docs = []
        processed_papers = []
        
        for paper in downloaded_papers:
            pdf_path = paper['file_path']
            filename = paper['filename']
            original_url = paper.get('original_url', 'Unknown')  # Get original URL if available
            
            try:
                print(f"Processing PDF: {filename}")
                
                # Extract information from PDF
                full_text, summary, models_info, model_names = self._extract_pdf_info(pdf_path)
                
                if not full_text:
                    print(f"Warning: Could not extract text from {filename}")
                    continue
                
                # Save model names to main BiosimulationModels.txt
                self._save_model_names_to_file(model_names, pdf_path)
                
                # Create documents for vector store with URL information
                # Store full text
                all_docs.append(Document(page_content=full_text, metadata={
                    'source': pdf_path,
                    'original_url': original_url,
                    'type': 'pdf_fulltext',
                    'title': filename,
                    'temp_kb_id': temp_kb_id
                }))
                
                # Store summary
                if summary:
                    all_docs.append(Document(page_content=summary, metadata={
                        'source': pdf_path,
                        'original_url': original_url,
                        'type': 'pdf_summary',
                        'title': filename,
                        'temp_kb_id': temp_kb_id
                    }))
                
                # Store models info
                if models_info:
                    all_docs.append(Document(page_content=models_info, metadata={
                        'source': pdf_path,
                        'original_url': original_url,
                        'type': 'pdf_models',
                        'title': filename,
                        'temp_kb_id': temp_kb_id
                    }))
                
                processed_papers.append({
                    'filename': filename,
                    'original_url': original_url,
                    'model_names': model_names,
                    'summary': summary[:200] + "..." if len(summary) > 200 else summary
                })
                
            except Exception as e:
                print(f"Error processing {filename}: {e}")
                continue
        
        if not all_docs:
            return "No documents could be processed for knowledge base."
        
        # Split documents into chunks
        text_splitter = CharacterTextSplitter(chunk_size=1500, chunk_overlap=100)
        documents = text_splitter.split_documents(all_docs)
        
        # Filter out documents that are too long for the embedding API
        filtered_documents = []
        for doc in documents:
            if len(doc.page_content) <= 2000:
                filtered_documents.append(doc)
            else:
                # Split long documents further
                long_text = doc.page_content
                while len(long_text) > 2000:
                    chunk = long_text[:2000]
                    last_period = chunk.rfind('.')
                    last_newline = chunk.rfind('\n')
                    break_point = max(last_period, last_newline)
                    if break_point > 1500:
                        chunk = chunk[:break_point + 1]
                        long_text = long_text[break_point + 1:]
                    else:
                        long_text = long_text[2000:]
                    
                    filtered_documents.append(Document(
                        page_content=chunk,
                        metadata=doc.metadata.copy()
                    ))
                
                if long_text:
                    filtered_documents.append(Document(
                        page_content=long_text,
                        metadata=doc.metadata.copy()
                    ))
        
        # Add documents to vector store
        print(f"Adding {len(filtered_documents)} document chunks to temporary knowledge base.")
        temp_vectorstore.add_documents(filtered_documents)
        
        # Save temporary knowledge base info
        kb_info = {
            'temp_kb_id': temp_kb_id,
            'temp_kb_path': temp_kb_path,
            'processed_papers': processed_papers,
            'total_chunks': len(filtered_documents),
            'created_at': time.time()
        }
        
        kb_info_path = os.path.join(temp_kb_path, 'kb_info.json')
        import json
        with open(kb_info_path, 'w', encoding='utf-8') as f:
            json.dump(kb_info, f, indent=2, ensure_ascii=False)
        
        print(f"Temporary knowledge base created: {temp_kb_id}")
        return temp_kb_id

    def _query_temporary_knowledge_base(self, temp_kb_id: str, query: str, top_k: int = 3) -> list:
        """Query the temporary knowledge base"""
        temp_kb_path = os.path.join(self.temp_knowledge_dir, temp_kb_id)
        if not os.path.exists(temp_kb_path):
            return []
        
        try:
            temp_vectorstore = Chroma(persist_directory=temp_kb_path, embedding_function=self.embeddings)
            docs = temp_vectorstore.similarity_search(query, k=top_k)
            
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
            print(f"Error querying temporary knowledge base: {e}")
            return []

    def search_papers(self, keywords: str, max_results: int = 5) -> list:
        """Search for papers using multiple academic search engines and APIs with intelligent keyword reduction"""
        try:
            # First attempt with original keywords
            all_papers = self._search_with_keywords(keywords, max_results)
            
            # If not enough papers found, try with reduced keywords
            if len(all_papers) < 3:
                print(f"\n⚠️ Only found {len(all_papers)} papers, trying with reduced keywords...")
                reduced_keywords = self._reduce_keywords(keywords)
                if reduced_keywords != keywords:
                    print(f"Reduced keywords: {reduced_keywords}")
                    additional_papers = self._search_with_keywords(reduced_keywords, max_results)
                    all_papers.extend(additional_papers)
                    
                    # Remove duplicates from combined results
                    all_papers = self._remove_duplicate_papers(all_papers)
            
            # Final processing
            if all_papers:
                print(f"\n=== Final Processing ===")
                print(f"Total unique papers found: {len(all_papers)}")
                
                print(f"\nRanking papers by relevance...")
                ranked_papers = self._rank_papers_by_relevance(all_papers, keywords)
                
                final_papers = ranked_papers[:max_results]
                print(f"Final results: {len(final_papers)} papers")
                return final_papers
            else:
                print(f"\n❌ No papers found from any source")
                return []
            
        except Exception as e:
            print(f"❌ Error in search_papers: {e}")
            return []

    def _search_with_keywords(self, keywords: str, max_results: int = 5) -> list:
        """Search with specific keywords"""
        all_papers = []
        
        print(f"\n=== Searching Academic Databases ===")
        print(f"Keywords: {keywords}")
        print(f"Max results per source: 3")
        
        # Step 1: Search arXiv
        print(f"\n1. Searching arXiv...")
        try:
            arxiv_papers = self._search_arxiv(keywords, max_results=3)
            if arxiv_papers:
                print(f"   ✅ Found {len(arxiv_papers)} papers from arXiv")
                all_papers.extend(arxiv_papers)
            else:
                print(f"   ⚠️ No papers found from arXiv")
        except Exception as e:
            print(f"   ❌ Error searching arXiv: {e}")
        
        # Step 2: Search Semantic Scholar (with reduced priority due to slow API)
        print(f"\n2. Searching Semantic Scholar...")
        try:
            # Only search Semantic Scholar if we haven't found enough papers from arXiv
            if len(all_papers) < 2:
                semantic_papers = self._search_semantic_scholar(keywords, max_results=3)
                if semantic_papers:
                    print(f"   ✅ Found {len(semantic_papers)} papers from Semantic Scholar")
                    all_papers.extend(semantic_papers)
                else:
                    print(f"   ⚠️ No papers found from Semantic Scholar")
            else:
                print(f"   ⏭️ Skipping Semantic Scholar (already found {len(all_papers)} papers from other sources)")
        except Exception as e:
            print(f"   ❌ Error searching Semantic Scholar: {e}")
        
        # Step 3: Search Crossref
        print(f"\n3. Searching Crossref...")
        try:
            crossref_papers = self._search_crossref(keywords, max_results=3)
            if crossref_papers:
                print(f"   ✅ Found {len(crossref_papers)} papers from Crossref")
                all_papers.extend(crossref_papers)
            else:
                print(f"   ⚠️ No papers found from Crossref")
        except Exception as e:
            print(f"   ❌ Error searching Crossref: {e}")
        
        # Step 4: Search PubMed
        print(f"\n4. Searching PubMed...")
        try:
            pubmed_papers = self._search_pubmed(keywords, max_results=3)
            if pubmed_papers:
                print(f"   ✅ Found {len(pubmed_papers)} papers from PubMed")
                all_papers.extend(pubmed_papers)
            else:
                print(f"   ⚠️ No papers found from PubMed")
        except Exception as e:
            print(f"   ❌ Error searching PubMed: {e}")
        
        # Step 5: Additional searches if still not enough papers
        if len(all_papers) < 3:
            # Try Semantic Scholar again if we skipped it earlier
            if len(all_papers) >= 2:
                print(f"\n5a. Trying Semantic Scholar for additional papers...")
                try:
                    semantic_papers = self._search_semantic_scholar(keywords, max_results=2)
                    if semantic_papers:
                        print(f"   ✅ Found {len(semantic_papers)} additional papers from Semantic Scholar")
                        all_papers.extend(semantic_papers)
                except Exception as e:
                    print(f"   ❌ Error in additional Semantic Scholar search: {e}")
            
            # Google Scholar style search as final fallback
            if len(all_papers) < 3:
                print(f"\n5b. Still not enough papers ({len(all_papers)}), trying Google Scholar style search...")
                try:
                    google_papers = self._search_google_scholar_style(keywords, max_results=3)
                    if google_papers:
                        print(f"   ✅ Found {len(google_papers)} papers from Google Scholar style search")
                        all_papers.extend(google_papers)
                    else:
                        print(f"   ⚠️ No papers found from Google Scholar style search")
                except Exception as e:
                    print(f"   ❌ Error searching Google Scholar style: {e}")
        
        return all_papers

    def _reduce_keywords(self, keywords: str) -> str:
        """Reduce keywords to core terms while preserving Computational Biology and Metabolic model"""
        try:
            # Split keywords
            keyword_list = [kw.strip() for kw in keywords.split(',') if kw.strip()]
            
            # Always preserve core keywords
            core_keywords = ["computational biology", "metabolic model"]
            preserved_keywords = []
            
            # Find and preserve core keywords
            for core_kw in core_keywords:
                for kw in keyword_list:
                    if core_kw in kw.lower() or kw.lower() in core_kw:
                        preserved_keywords.append(kw)
                        break
            
            # Add 2-3 most specific technical terms
            technical_keywords = []
            for kw in keyword_list:
                if kw.lower() not in [ck.lower() for ck in preserved_keywords]:
                    # Prioritize specific technical terms
                    if any(tech in kw.lower() for tech in ['fba', 'cobra', 'rna-seq', 'protein', 'network', 'genome', 'flux']):
                        technical_keywords.append(kw)
                        if len(technical_keywords) >= 2:
                            break
            
            # Combine preserved and technical keywords
            reduced_keywords = preserved_keywords + technical_keywords
            
            # Ensure we have at least 2 keywords
            if len(reduced_keywords) < 2:
                # Add first available keyword
                for kw in keyword_list:
                    if kw not in reduced_keywords:
                        reduced_keywords.append(kw)
                        break
            
            return ', '.join(reduced_keywords[:4])  # Limit to 4 keywords
            
        except Exception as e:
            print(f"Error reducing keywords: {e}")
            # Fallback: return core keywords only
            return "computational biology, metabolic model"

    def _remove_duplicate_papers(self, papers: list) -> list:
        """Remove duplicate papers based on title similarity and DOI"""
        try:
            unique_papers = []
            seen_dois = set()
            seen_titles = set()
            
            for paper in papers:
                # Check by DOI first
                doi = paper.get('doi', '')
                if doi and doi.lower() in seen_dois:
                    continue
                
                # Check by title similarity
                title = paper.get('title', '')
                if not title:
                    continue
                title = title.lower()
                title_words = set(title.split())
                
                is_duplicate = False
                for seen_title in seen_titles:
                    seen_words = set(seen_title.split())
                    # If more than 70% of words match, consider it duplicate
                    if len(title_words & seen_words) / max(len(title_words), len(seen_words)) > 0.7:
                        is_duplicate = True
                        break
                
                if not is_duplicate:
                    unique_papers.append(paper)
                    if doi:
                        seen_dois.add(doi)
                    if title:
                        seen_titles.add(title)
            
            return unique_papers
            
        except Exception as e:
            print(f"Error removing duplicates: {e}")
            return papers

    def _rank_papers_by_relevance(self, papers: list, keywords: str) -> list:
        """Rank papers by relevance to keywords with core keywords priority"""
        try:
            keyword_words = set(keywords.lower().split())
            core_keywords = ["computational biology", "metabolic model"]
            
            def relevance_score(paper):
                score = 0
                title = paper.get('title', '').lower()
                abstract = paper.get('abstract', '').lower()
                
                # Core keywords priority (highest weight)
                core_keyword_matches = 0
                for core_keyword in core_keywords:
                    if core_keyword in title or core_keyword in abstract:
                        core_keyword_matches += 1
                score += core_keyword_matches * 10  # Very high weight for core keywords
                
                # Title relevance (high weight)
                title_words = set(title.split())
                title_matches = len(keyword_words & title_words)
                score += title_matches * 3
                
                # Abstract relevance
                abstract_words = set(abstract.split())
                abstract_matches = len(keyword_words & abstract_words)
                score += abstract_matches
                
                # Source preference (arXiv and Semantic Scholar often have better quality)
                source = paper.get('source', '').lower()
                if 'arxiv' in source:
                    score += 2
                elif 'semantic scholar' in source:
                    score += 1
                
                # Year preference (newer papers get slight boost)
                year = paper.get('year', 0)
                if year and year > 2020:
                    score += 1
                
                return score
            
            # Sort by relevance score (descending)
            ranked_papers = sorted(papers, key=relevance_score, reverse=True)
            
            # Log ranking information
            print(f"\n=== Paper Ranking Information ===")
            print(f"Core keywords: {', '.join(core_keywords)}")
            print(f"Total papers ranked: {len(ranked_papers)}")
            
            # Show top 3 papers with their scores
            for i, paper in enumerate(ranked_papers[:3]):
                title = paper.get('title', 'Unknown')
                score = relevance_score(paper)
                print(f"Rank {i+1}: {title[:60]}... (Score: {score})")
            
            return ranked_papers
            
        except Exception as e:
            print(f"Error ranking papers: {e}")
            return papers

    def _extract_papers_from_search_results(self, search_results: str, keywords: str) -> list:
        """Extract paper titles and PMIDs from search results"""
        try:
            papers = []
            lines = search_results.split('\n')
            
            for line in lines:
                # Look for PubMed URLs with PMIDs
                pmid_match = re.search(r'pubmed\.ncbi\.nlm\.nih\.gov/(\d+)', line)
                if pmid_match:
                    pmid = pmid_match.group(1)
                    # Extract title from the line or surrounding context
                    title = self._extract_title_from_line(line)
                    if title and len(title) > 10:  # Filter out very short titles
                        papers.append({
                            'pmid': pmid,
                            'title': title,
                            'source': 'PubMed URL'
                        })
                    continue
                
                # Look for paper titles in the search results
                # Check if line contains keywords and looks like a paper title
                if any(keyword.lower() in line.lower() for keyword in keywords.split()):
                    title = self._extract_title_from_line(line)
                    if title and len(title) > 30 and len(title) < 500:  # Filter reasonable title length
                        # Additional filtering to avoid non-paper content
                        if not any(skip_word in title.lower() for skip_word in ['click', 'visit', 'buy', 'order', 'shop']):
                            papers.append({
                                'title': title,
                                'source': 'Search result'
                            })
            
            # If we didn't find enough papers, try a broader search
            if len(papers) < 2:
                print("Not enough papers found, trying broader search...")
                broader_papers = self._extract_papers_broader_search(keywords)
                papers.extend(broader_papers)
            
            return papers
            
        except Exception as e:
            print(f"Error extracting papers from search results: {e}")
            return []

    def _extract_papers_broader_search(self, keywords: str) -> list:
        """Extract papers using a broader search approach"""
        try:
            papers = []
            
            # Try searching with just the main keywords
            main_keywords = keywords.split()[:2]  # Take first 2 keywords
            search_query = f'"{main_keywords[0]}" "{main_keywords[1]}" paper site:pubmed.ncbi.nlm.nih.gov'
            search_results = self.search_tool.run(search_query)
            
            if search_results:
                lines = search_results.split('\n')
                for line in lines:
                    pmid_match = re.search(r'pubmed\.ncbi\.nlm\.nih\.gov/(\d+)', line)
                    if pmid_match:
                        pmid = pmid_match.group(1)
                        title = self._extract_title_from_line(line)
                        if title and len(title) > 10:
                            papers.append({
                                'pmid': pmid,
                                'title': title,
                                'source': 'Broader search'
                            })
            
            return papers
            
        except Exception as e:
            print(f"Error in broader search: {e}")
            return []

    def _extract_title_from_line(self, line: str) -> str:
        """Extract paper title from a line of search results"""
        try:
            # Remove URL parts
            line = re.sub(r'https?://[^\s]+', '', line)
            # Remove common prefixes and brackets
            line = re.sub(r'^(Title|Paper|Article|Study|URL):\s*', '', line, flags=re.IGNORECASE)
            line = re.sub(r'^\[\d+\]\s*', '', line)  # Remove [1], [2], etc.
            # Clean up the line
            title = line.strip()
            # Remove trailing punctuation and common suffixes
            title = re.sub(r'[.,;!?]+$', '', title)
            title = re.sub(r'\s*—\s*.*$', '', title)  # Remove content after em dash
            title = re.sub(r'\s*\.\s*\.\s*\.\s*.*$', '', title)  # Remove content after ellipsis
            
            # Additional cleaning for common patterns
            title = re.sub(r'by\s+[A-Z][a-z]+\s+[A-Z][a-z]+.*$', '', title)  # Remove "by Author Name" patterns
            title = re.sub(r'\d{4}\s*·\s*Cited by.*$', '', title)  # Remove citation patterns
            
            return title.strip()
        except Exception as e:
            print(f"Error extracting title: {e}")
            return ""

    def _search_pubmed_by_title(self, title: str) -> list:
        """Search PubMed by paper title"""
        try:
            # Clean the title for search
            clean_title = re.sub(r'[^\w\s]', ' ', title)
            clean_title = re.sub(r'\s+', ' ', clean_title).strip()
            
            # Search PubMed with the title
            articles = self._search_pubmed(clean_title, max_results=1)
            return articles
            
        except Exception as e:
            print(f"Error searching PubMed by title: {e}")
            return []

    def _search_arxiv(self, keywords: str, max_results: int = 5) -> list:
        """Search arXiv for papers with timeout and error handling using ANY logic"""
        try:
            print(f"Searching arXiv for: {keywords}")
            
            # Convert keywords to ANY logic query (OR instead of AND)
            keyword_list = [kw.strip().replace(' ', '+') for kw in keywords.split(',')]
            # Create OR query for arXiv (use OR operator)
            arxiv_query = ' OR '.join([f'"{kw}"' for kw in keyword_list])
            print(f"ArXiv query (ANY logic): {arxiv_query}")
            
            # Use threading.Timer instead of signal for timeout (works in all threads)
            import threading
            import time
            
            papers = []
            search_completed = threading.Event()
            search_error = None
            
            def search_worker():
                nonlocal papers, search_error
                try:
                    search = arxiv.Search(
                        query=arxiv_query,
                        max_results=max_results,
                        sort_by=arxiv.SortCriterion.Relevance
                    )
                    
                    result_count = 0
                    
                    # Use a more robust way to iterate through results
                    for result in search.results():
                        if result_count >= max_results or search_completed.is_set():
                            break
                        
                        try:
                            paper_info = {
                                'title': result.title,
                                'authors': [author.name for author in result.authors],
                                'abstract': result.summary,
                                'arxiv_id': result.entry_id.split('/')[-1],
                                'doi': result.doi,
                                'published_date': result.published.strftime('%Y-%m-%d') if result.published else '',
                                'pdf_url': result.pdf_url,
                                'source': 'arXiv',
                                'urls': [{
                                    'url': result.pdf_url,
                                    'type': 'arXiv PDF',
                                    'description': 'Direct PDF download from arXiv'
                                }]
                            }
                            
                            # Add DOI-based links if available
                            if result.doi:
                                paper_info['urls'].extend([
                                    {
                                        'url': f"https://doi.org/{result.doi}",
                                        'type': 'DOI',
                                        'description': 'DOI link'
                                    },
                                    {
                                        'url': f"https://sci-hub.se/{result.doi}",
                                        'type': 'Sci-Hub',
                                        'description': 'Sci-Hub access'
                                    }
                                ])
                            
                            papers.append(paper_info)
                            result_count += 1
                            
                        except Exception as e:
                            print(f"Error processing arXiv result: {e}")
                            continue
                            
                except Exception as e:
                    search_error = e
                finally:
                    search_completed.set()
            
            # Start search in a separate thread
            search_thread = threading.Thread(target=search_worker)
            search_thread.daemon = True
            search_thread.start()
            
            # Wait for completion or timeout (30 seconds)
            if not search_completed.wait(timeout=30):
                print("arXiv search timed out, returning partial results")
                return papers
            
            if search_error:
                print(f"Error in arXiv search: {search_error}")
            
            return papers
                
        except Exception as e:
            print(f"Error searching arXiv: {e}")
            return []

    def _search_semantic_scholar(self, keywords: str, max_results: int = 5) -> list:
        """Search Semantic Scholar for papers with timeout and error handling using ANY logic"""
        try:
            print(f"Searching Semantic Scholar for: {keywords}")
            
            # Convert keywords to optimized query format
            keyword_list = [kw.strip() for kw in keywords.split(',')]
            
            # Try different query strategies based on keyword count
            if len(keyword_list) > 2:
                # Use first 2 most important keywords for complex queries 
                semantic_query = ' '.join(keyword_list[:2])
                print(f"Semantic Scholar query (simplified): {semantic_query}")
            else:
                # Use all keywords for simple queries
                semantic_query = ' '.join(keyword_list)
                print(f"Semantic Scholar query (full): {semantic_query}")
            
            # Use threading with extended timeout for Semantic Scholar's slow API
            import threading
            
            papers = []
            search_completed = threading.Event()
            search_error = None
            
            def search_worker():
                nonlocal papers, search_error
                try:
                    # Use smaller limit to speed up search
                    results = self.semantic_scholar.search_paper(semantic_query, limit=min(max_results, 3))
                    
                    for paper in results:
                        if search_completed.is_set():
                            break
                            
                        try:
                            # Handle both dict and object formats
                            if hasattr(paper, 'title'):
                                # Object format
                                paper_info = {
                                    'title': paper.title or '',
                                    'authors': [author.name for author in paper.authors] if paper.authors else [],
                                    'abstract': paper.abstract or '',
                                    'paper_id': paper.paperId or '',
                                    'doi': getattr(paper, 'doi', '') or '',
                                    'year': paper.year or '',
                                    'venue': paper.venue or '',
                                    'source': 'Semantic Scholar',
                                    'urls': []
                                }
                            else:
                                # Dict format
                                paper_info = {
                                    'title': paper.get('title', ''),
                                    'authors': [author.get('name', '') for author in paper.get('authors', [])],
                                    'abstract': paper.get('abstract', ''),
                                    'paper_id': paper.get('paperId', ''),
                                    'doi': paper.get('doi', ''),
                                    'year': paper.get('year', ''),
                                    'venue': paper.get('venue', ''),
                                    'source': 'Semantic Scholar',
                                    'urls': []
                                }
                            
                            # Add available links based on format
                            if hasattr(paper, 'title'):
                                # Object format - use getattr for URLs and DOI
                                paper_url = getattr(paper, 'url', None)
                                if paper_url:
                                    paper_info['urls'].append({
                                        'url': paper_url,
                                        'type': 'Paper URL',
                                        'description': 'Direct paper link'
                                    })
                                
                                paper_doi = getattr(paper, 'doi', None) or paper_info.get('doi', '')
                                if paper_doi:
                                    paper_info['urls'].extend([
                                        {
                                            'url': f"https://doi.org/{paper_doi}",
                                            'type': 'DOI',
                                            'description': 'DOI link'
                                        },
                                        {
                                            'url': f"https://sci-hub.se/{paper_doi}",
                                            'type': 'Sci-Hub',
                                            'description': 'Sci-Hub access'
                                        }
                                    ])
                            else:
                                # Dict format
                                if paper.get('url'):
                                    paper_info['urls'].append({
                                        'url': paper['url'],
                                        'type': 'Paper URL',
                                        'description': 'Direct paper link'
                                    })
                                
                                if paper.get('doi'):
                                    paper_info['urls'].extend([
                                        {
                                            'url': f"https://doi.org/{paper['doi']}",
                                            'type': 'DOI',
                                            'description': 'DOI link'
                                        },
                                        {
                                            'url': f"https://sci-hub.se/{paper['doi']}",
                                            'type': 'Sci-Hub',
                                            'description': 'Sci-Hub access'
                                        }
                                    ])
                            
                            # Add Semantic Scholar link
                            paper_id = paper_info.get('paper_id', '') or (getattr(paper, 'paperId', '') if hasattr(paper, 'paperId') else paper.get('paperId', ''))
                            paper_info['urls'].append({
                                'url': f"https://www.semanticscholar.org/paper/{paper_id}",
                                'type': 'Semantic Scholar',
                                'description': 'Semantic Scholar page'
                            })
                            
                            papers.append(paper_info)
                            
                        except Exception as e:
                            print(f"Error processing Semantic Scholar result: {e}")
                            continue
                            
                except Exception as e:
                    search_error = e
                finally:
                    search_completed.set()
            
            # Start search in a separate thread
            search_thread = threading.Thread(target=search_worker)
            search_thread.daemon = True
            search_thread.start()
            
            # Wait for completion with extended timeout for Semantic Scholar (60 seconds)
            if not search_completed.wait(timeout=60):
                print("Semantic Scholar search timed out after 60 seconds, returning partial results")
                return papers
            
            if search_error:
                print(f"Error in Semantic Scholar search: {search_error}")
                # If main search fails, try a fallback with just the first keyword
                if keyword_list:
                    print(f"Attempting fallback search with single keyword: {keyword_list[0]}")
                    try:
                        fallback_results = self.semantic_scholar.search_paper(keyword_list[0], limit=2)
                        if fallback_results:
                            print(f"Fallback search found {len(fallback_results)} papers")
                            # Process fallback results with same logic
                            for paper in fallback_results:
                                try:
                                    if hasattr(paper, 'title'):
                                        paper_info = {
                                            'title': paper.title or '',
                                            'authors': [author.name for author in paper.authors] if paper.authors else [],
                                            'abstract': paper.abstract or '',
                                            'paper_id': paper.paperId or '',
                                            'doi': getattr(paper, 'doi', '') or '',
                                            'year': paper.year or '',
                                            'venue': paper.venue or '',
                                            'source': 'Semantic Scholar (fallback)',
                                            'urls': []
                                        }
                                        
                                        # Add basic URL
                                        paper_id = paper_info.get('paper_id', '')
                                        if paper_id:
                                            paper_info['urls'].append({
                                                'url': f"https://www.semanticscholar.org/paper/{paper_id}",
                                                'type': 'Semantic Scholar',
                                                'description': 'Semantic Scholar page'
                                            })
                                        
                                        papers.append(paper_info)
                                except Exception as e:
                                    print(f"Error processing fallback result: {e}")
                                    continue
                    except Exception as fallback_error:
                        print(f"Fallback search also failed: {fallback_error}")
            
            return papers
                
        except Exception as e:
            print(f"Error searching Semantic Scholar: {e}")
            return []

    def _search_crossref(self, keywords: str, max_results: int = 5) -> list:
        """Search Crossref for papers using ANY logic"""
        try:
            print(f"Searching Crossref for: {keywords}")
            
            # Convert keywords to ANY logic query for Crossref
            keyword_list = [kw.strip() for kw in keywords.split(',')]
            # Crossref supports OR operator between terms
            crossref_query = ' OR '.join([f'"{kw}"' for kw in keyword_list])
            print(f"Crossref query (ANY logic): {crossref_query}")
            
            # Use Crossref API to search for works
            headers = {
                'User-Agent': self.crossref_user_agent
            }
            
            search_url = "https://api.crossref.org/works"
            params = {
                'query': crossref_query,
                'rows': max_results,
                'sort': 'relevance'
            }
            
            response = requests.get(search_url, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            papers = []
            
            for item in data.get('message', {}).get('items', []):
                paper_info = {
                    'title': item.get('title', [''])[0] if item.get('title') else '',
                    'authors': [author.get('given', '') + ' ' + author.get('family', '') 
                              for author in item.get('author', [])],
                    'doi': item.get('DOI', ''),
                    'year': item.get('published-print', {}).get('date-parts', [[]])[0][0] if item.get('published-print') else '',
                    'journal': item.get('container-title', [''])[0] if item.get('container-title') else '',
                    'source': 'Crossref',
                    'urls': []
                }
                
                # Add DOI-based links
                if paper_info['doi']:
                    paper_info['urls'].extend([
                        {
                            'url': f"https://doi.org/{paper_info['doi']}",
                            'type': 'DOI',
                            'description': 'DOI link'
                        },
                        {
                            'url': f"https://sci-hub.se/{paper_info['doi']}",
                            'type': 'Sci-Hub',
                            'description': 'Sci-Hub access'
                        }
                    ])
                
                papers.append(paper_info)
            
            return papers
            
        except Exception as e:
            print(f"Error searching Crossref: {e}")
            return []

    def _search_google_scholar_style(self, keywords: str, max_results: int = 5) -> list:
        """Search using Google Scholar style queries with ANY logic"""
        try:
            print(f"Searching with Google Scholar style for: {keywords}")
            
            # Convert keywords to ANY logic for Google search
            keyword_list = [kw.strip() for kw in keywords.split(',')]
            # Create OR queries for each site
            or_keywords = ' OR '.join([f'"{kw}"' for kw in keyword_list])
            
            print(f"Google Scholar query (ANY logic): {or_keywords}")
            
            # Use the existing search tool but with academic-focused queries
            search_queries = [
                f'({or_keywords}) filetype:pdf site:arxiv.org',
                f'({or_keywords}) filetype:pdf site:pubmed.ncbi.nlm.nih.gov',
                f'({or_keywords}) filetype:pdf site:ncbi.nlm.nih.gov',
                f'({or_keywords}) filetype:pdf site:researchgate.net',
                f'({or_keywords}) filetype:pdf site:academia.edu'
            ]
            
            all_papers = []
            
            for query in search_queries[:2]:  # Use first 2 queries to avoid too many requests
                try:
                    results = self.search_tool.run(query)
                    if results:
                        extracted_papers = self._extract_papers_from_search_results(results, keywords)
                        all_papers.extend(extracted_papers)
                except Exception as e:
                    print(f"Error with query '{query}': {e}")
                    continue
            
            return all_papers[:max_results]
            
        except Exception as e:
            print(f"Error in Google Scholar style search: {e}")
            return []

    def _web_search_papers(self, keywords: str) -> list:
        """Fallback web search for papers"""
        try:
            search_query = f"research papers PDF {keywords}"
            results = self.search_tool.run(search_query)
            
            # Parse search results to extract URLs
            urls = []
            if results:
                # Extract URLs from search results
                lines = results.split('\n')
                for line in lines:
                    if line.startswith('URL:'):
                        url = line.replace('URL:', '').strip()
                        urls.append(url)
            
            return urls[:3]  # Return top 3 results
            
        except Exception as e:
            print(f"Error in web search: {e}")
            return []

    def _find_pdf_links(self, url: str) -> list:
        """Find PDF links on a webpage"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            response = requests.get(url, headers=headers, timeout=30, allow_redirects=True)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            pdf_links = []
            
            # Find all links that might be PDFs
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                link_text = link.get_text().lower()
                
                # Check if link points to PDF
                if (href.lower().endswith('.pdf') or 
                    'pdf' in href.lower() or 
                    'pdf' in link_text or
                    'download' in link_text or
                    'full text' in link_text or
                    'full-text' in link_text or
                    'supplementary' in link_text or
                    'supplement' in link_text):
                    
                    # Make relative URLs absolute
                    full_url = urljoin(url, href)
                    pdf_links.append({
                        'url': full_url,
                        'text': link_text,
                        'href': href
                    })
            
            # Also check for PDF links in meta tags or other elements
            for meta in soup.find_all('meta'):
                content = meta.get('content', '').lower()
                if 'pdf' in content and 'http' in content:
                    pdf_links.append({
                        'url': content,
                        'text': 'meta tag',
                        'href': content
                    })
            
            return pdf_links
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                print(f"Page not found (404): {url}")
            elif e.response.status_code == 403:
                print(f"Access forbidden (403): {url}")
            else:
                print(f"HTTP error {e.response.status_code}: {url}")
            return []
        except requests.exceptions.Timeout:
            print(f"Timeout accessing: {url}")
            return []
        except requests.exceptions.ConnectionError:
            print(f"Connection error accessing: {url}")
            return []
        except Exception as e:
            print(f"Error finding PDF links on {url}: {e}")
            return []

    def _search_pubmed(self, keywords: str, max_results: int = 10) -> list:
        """Search PubMed using E-utilities API with ANY logic"""
        try:
            print(f"Searching PubMed for: {keywords}")
            
            # Convert keywords to ANY logic query for PubMed
            keyword_list = [kw.strip() for kw in keywords.split(',')]
            # PubMed uses OR operator for ANY logic
            pubmed_query = ' OR '.join([f'"{kw}"[Title/Abstract]' for kw in keyword_list])
            print(f"PubMed query (ANY logic): {pubmed_query}")
            
            # Search for articles
            search_url = f"{self.pubmed_base_url}esearch.fcgi"
            search_params = {
                'db': 'pubmed',
                'term': pubmed_query,
                'retmax': max_results,
                'retmode': 'json',
                'sort': 'relevance',
                'email': self.pubmed_email,
                'tool': self.pubmed_tool
            }
            
            response = requests.get(search_url, params=search_params, timeout=30)
            response.raise_for_status()
            
            search_data = response.json()
            if 'esearchresult' not in search_data or 'idlist' not in search_data['esearchresult']:
                print("No search results found")
                return []
            
            pmids = search_data['esearchresult']['idlist']
            print(f"Found {len(pmids)} PubMed articles")
            
            # Get detailed information for each article
            articles = []
            for pmid in pmids:
                article_info = self._get_pubmed_article_info(pmid)
                if article_info:
                    articles.append(article_info)
            
            return articles
            
        except Exception as e:
            print(f"Error searching PubMed: {e}")
            return []

    def _get_pubmed_article_info(self, pmid: str) -> dict:
        """Get detailed article information from PubMed"""
        try:
            # Get summary information
            summary_url = f"{self.pubmed_base_url}esummary.fcgi"
            summary_params = {
                'db': 'pubmed',
                'id': pmid,
                'retmode': 'json',
                'email': self.pubmed_email,
                'tool': self.pubmed_tool
            }
            
            response = requests.get(summary_url, params=summary_params, timeout=30)
            response.raise_for_status()
            
            summary_data = response.json()
            if pmid not in summary_data['result']:
                return None
            
            article_data = summary_data['result'][pmid]
            
            # Get full text links
            links = self._get_pubmed_fulltext_links(pmid)
            
            # Process authors - extract names from author dictionaries
            authors = []
            if 'authors' in article_data:
                for author in article_data['authors']:
                    if isinstance(author, dict):
                        # Extract name from author dictionary
                        name = author.get('name', '')
                        if name:
                            authors.append(name)
                    elif isinstance(author, str):
                        authors.append(author)
            
            article_info = {
                'pmid': pmid,
                'title': article_data.get('title', ''),
                'authors': authors,
                'journal': article_data.get('fulljournalname', ''),
                'pubdate': article_data.get('pubdate', ''),
                'abstract': article_data.get('abstract', ''),
                'doi': article_data.get('elocationid', '').replace('doi: ', '') if article_data.get('elocationid', '').startswith('doi: ') else '',
                'fulltext_links': links
            }
            
            return article_info
            
        except Exception as e:
            print(f"Error getting article info for PMID {pmid}: {e}")
            return None

    def _get_pubmed_fulltext_links(self, pmid: str) -> list:
        """Get full text links for a PubMed article"""
        try:
            # Get link information
            link_url = f"{self.pubmed_base_url}elink.fcgi"
            link_params = {
                'dbfrom': 'pubmed',
                'db': 'pmc',
                'id': pmid,
                'retmode': 'xml',
                'email': self.pubmed_email,
                'tool': self.pubmed_tool
            }
            
            response = requests.get(link_url, params=link_params, timeout=30)
            response.raise_for_status()
            
            # Parse XML response
            root = ET.fromstring(response.content)
            links = []
            
            # Look for PMC links (full text)
            for link_set in root.findall('.//LinkSet'):
                for link in link_set.findall('.//Link'):
                    id_elem = link.find('Id')
                    if id_elem is not None:
                        pmcid = id_elem.text
                        if pmcid:
                            # Construct PMC URL
                            pmc_url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/PMC{pmcid}/"
                            links.append({
                                'type': 'PMC',
                                'url': pmc_url,
                                'pmcid': pmcid
                            })
            
            # Also check for DOI-based links
            doi_links = self._get_doi_links(pmid)
            links.extend(doi_links)
            
            return links
            
        except Exception as e:
            print(f"Error getting fulltext links for PMID {pmid}: {e}")
            return []

    def _get_doi_links(self, pmid: str) -> list:
        """Get DOI-based full text links"""
        try:
            # Get article details to find DOI
            summary_url = f"{self.pubmed_base_url}esummary.fcgi"
            summary_params = {
                'db': 'pubmed',
                'id': pmid,
                'retmode': 'json',
                'email': self.pubmed_email,
                'tool': self.pubmed_tool
            }
            
            response = requests.get(summary_url, params=summary_params, timeout=30)
            response.raise_for_status()
            
            summary_data = response.json()
            if pmid not in summary_data['result']:
                return []
            
            article_data = summary_data['result'][pmid]
            doi = article_data.get('elocationid', '').replace('doi: ', '') if article_data.get('elocationid', '').startswith('doi: ') else ''
            
            if doi:
                # Try common DOI-based full text services
                doi_links = [
                    {
                        'type': 'DOI',
                        'url': f"https://doi.org/{doi}",
                        'doi': doi
                    },
                    {
                        'type': 'Sci-Hub',
                        'url': f"https://sci-hub.se/{doi}",
                        'doi': doi
                    }
                ]
                return doi_links
            
            return []
            
        except Exception as e:
            print(f"Error getting DOI links for PMID {pmid}: {e}")
            return []

    def _is_pdf_url(self, url: str) -> bool:
        """Check if URL points to a PDF file"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'application/pdf,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            }
            
            # First check URL pattern
            if url.lower().endswith('.pdf'):
                return True
            
            # Then check content type
            try:
                response = requests.head(url, headers=headers, timeout=10, allow_redirects=True)
                content_type = response.headers.get('content-type', '').lower()
                return 'pdf' in content_type
            except requests.exceptions.RequestException:
                # If HEAD request fails, try GET request
                try:
                    response = requests.get(url, headers=headers, timeout=10, stream=True)
                    content_type = response.headers.get('content-type', '').lower()
                    return 'pdf' in content_type
                except:
                    return False
            
        except Exception as e:
            print(f"Error checking if {url} is PDF: {e}")
            return False

    def _download_from_page(self, url: str, filename: str = None) -> dict:
        """Download PDF by first finding it on the page"""
        try:
            print(f"Searching for PDF links on page: {url}")
            pdf_links = self._find_pdf_links(url)
            
            if not pdf_links:
                return {
                    'success': False,
                    'message': f'No PDF links found on page: {url}',
                    'file_path': None
                }
            
            print(f"Found {len(pdf_links)} potential PDF links")
            
            # Try each PDF link
            for i, link_info in enumerate(pdf_links):
                pdf_url = link_info['url']
                link_text = link_info['text']
                
                print(f"Trying PDF link {i+1}/{len(pdf_links)}: {pdf_url}")
                
                # Check if it's actually a PDF
                if not self._is_pdf_url(pdf_url):
                    print(f"Skipping {pdf_url} - not a PDF")
                    continue
                
                # Try to download the PDF
                download_result = self._download_pdf_file(pdf_url, filename)
                if download_result['success']:
                    download_result['original_url'] = url  # Keep the original page URL
                    download_result['pdf_url'] = pdf_url   # Add the actual PDF URL
                    return download_result
            
            return {
                'success': False,
                'message': f'Failed to download any PDF from {len(pdf_links)} links found on page',
                'file_path': None
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error downloading from page {url}: {str(e)}',
                'file_path': None
            }

    def _download_pdf_file(self, url: str, filename: str = None) -> dict:
        """Download a PDF file from URL"""
        try:
            if not filename:
                # Extract filename from URL or use timestamp
                parsed_url = urlparse(url)
                filename = os.path.basename(parsed_url.path)
                if not filename or '.' not in filename:
                    filename = f"paper_{int(time.time())}.pdf"
            
            # Ensure filename has .pdf extension
            if not filename.endswith('.pdf'):
                filename += '.pdf'
            
            file_path = os.path.join(self.downloads_dir, filename)
            
            # Download the file
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Check if content is actually a PDF
            content_type = response.headers.get('content-type', '').lower()
            if 'pdf' not in content_type and not url.lower().endswith('.pdf'):
                return {
                    'success': False,
                    'message': f'URL does not point to a PDF file (content-type: {content_type})',
                    'file_path': None
                }
            
            # Save the file
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            return {
                'success': True,
                'message': f'Successfully downloaded PDF',
                'file_path': file_path,
                'filename': filename,
                'original_url': url
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to download PDF: {str(e)}',
                'file_path': None
            }

    def download_paper(self, url: str, filename: str = None) -> dict:
        """Download a paper from the given URL, with page traversal if needed"""
        try:
            # First, try direct download
            print(f"Attempting direct download from: {url}")
            direct_result = self._download_pdf_file(url, filename)
            
            if direct_result['success']:
                return direct_result
            
            # If direct download fails, try to find PDF on the page
            print(f"Direct download failed, searching for PDF links on page: {url}")
            return self._download_from_page(url, filename)
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to download paper: {str(e)}',
                'file_path': None
            }

    def run(self, prompt: str, memory=None) -> str:
        """Main method to extract keywords, search/download papers, and build knowledge base"""
        try:
            # Step 1: Extract keywords from user input
            print("Extracting keywords from user input...")
            keywords = self.extract_keywords(prompt)
            
            if not keywords:
                return "Failed to extract keywords from the input. Please try again with more specific biological research terms."
            
            print(f"Extracted keywords: {keywords}")
            
            # Step 2: Search for papers using keywords
            print("Searching for relevant papers...")
            papers = self.search_papers(keywords)
            
            if not papers:
                return f"No papers found for keywords: {keywords}"
            
            print(f"Found {len(papers)} potential papers")
            
            # Step 3: Download papers
            print("Downloading papers...")
            downloaded_papers = []
            failed_downloads = []
            
            for i, paper in enumerate(papers, 1):
                print(f"\nProcessing paper {i}/{len(papers)}: {paper.get('title', 'Unknown title')}")
                
                # Try to download from available URLs
                downloaded = False
                for url_info in paper.get('urls', []):
                    url = url_info['url']
                    url_type = url_info['type']
                    print(f"  Trying {url_type} URL: {url}")
                    
                    # Generate filename based on paper info
                    safe_title = re.sub(r'[^\w\s-]', '', paper.get('title', 'unknown')).strip()
                    safe_title = re.sub(r'[-\s]+', '_', safe_title)
                    filename = f"{safe_title}_{i}.pdf"
                    
                    result = self.download_paper(url, filename)
                    
                    if result['success']:
                        # Add paper metadata to download result
                        result['paper_info'] = {
                            'title': paper.get('title', ''),
                            'authors': paper.get('authors', []),
                            'journal': paper.get('journal', ''),
                            'pmid': paper.get('pmid', ''),
                            'doi': paper.get('doi', ''),
                            'url_type': url_type,
                            'original_url': url
                        }
                        downloaded_papers.append(result)
                        print(f"  ✓ Downloaded: {result['filename']}")
                        downloaded = True
                        break  # Successfully downloaded, move to next paper
                    else:
                        print(f"  ✗ Failed to download from {url_type}: {result['message']}")
                
                if not downloaded:
                    failed_downloads.append({
                        'title': paper.get('title', 'Unknown'),
                        'urls': paper.get('urls', [])
                    })
                    print(f"  ✗ Failed to download from all available URLs")
            
            # Step 4: Build temporary knowledge base from downloaded papers
            temp_kb_id = None
            if downloaded_papers:
                temp_kb_id = self._build_temporary_knowledge_base(downloaded_papers)
            
            # Step 5: Generate comprehensive report
            report = f"""
Keywords extracted: {keywords}

Search Results:
- Total papers found: {len(papers)}
- Successfully downloaded: {len(downloaded_papers)}
- Failed downloads: {len(failed_downloads)}

Downloaded Papers:"""
            
            for paper in downloaded_papers:
                paper_info = paper.get('paper_info', {})
                report += f"\n- {paper['filename']}"
                if paper_info.get('title'):
                    report += f"\n  Title: {paper_info['title']}"
                if paper_info.get('authors'):
                    authors = ', '.join(paper_info['authors'][:3])  # Show first 3 authors
                    if len(paper_info['authors']) > 3:
                        authors += f" et al. ({len(paper_info['authors'])} authors)"
                    report += f"\n  Authors: {authors}"
                if paper_info.get('journal'):
                    report += f"\n  Journal: {paper_info['journal']}"
                if paper_info.get('pmid'):
                    report += f"\n  PMID: {paper_info['pmid']}"
                if paper_info.get('doi'):
                    report += f"\n  DOI: {paper_info['doi']}"
                report += f"\n  Saved to: {paper['file_path']}"
                report += f"\n  Downloaded from: {paper_info.get('url_type', 'Unknown')}"
            
            if failed_downloads:
                report += f"\n\nFailed Downloads:"
                for failed in failed_downloads:
                    report += f"\n- {failed['title']}"
                    for url_info in failed['urls']:
                        report += f"\n  {url_info['type']}: {url_info['url']}"
            
            report += f"\n\nPapers have been saved to: {self.downloads_dir}"
            
            # Add knowledge base information
            if temp_kb_id and temp_kb_id != "No papers to process for knowledge base.":
                report += f"\n\n📚 Temporary Knowledge Base Created:"
                report += f"\n- Knowledge Base ID: {temp_kb_id}"
                report += f"\n- Location: {self.temp_knowledge_dir}/{temp_kb_id}"
                report += f"\n- You can now query this knowledge base using:"
                report += f"\n  literature_query {temp_kb_id} <your question>"
                
                # Load and display knowledge base info
                kb_info_path = os.path.join(self.temp_knowledge_dir, temp_kb_id, 'kb_info.json')
                if os.path.exists(kb_info_path):
                    import json
                    with open(kb_info_path, 'r', encoding='utf-8') as f:
                        kb_info = json.load(f)
                    
                    report += f"\n\nProcessed Papers Summary:"
                    for paper_info in kb_info.get('processed_papers', []):
                        report += f"\n- {paper_info['filename']}"
                        if paper_info.get('model_names') and paper_info['model_names'] != "None":
                            report += f" (Models: {paper_info['model_names']})"
                        if paper_info.get('summary'):
                            report += f"\n  Summary: {paper_info['summary']}"
            
            return report
            
        except Exception as e:
            error_msg = f"Error in literature agent: {str(e)}"
            print(error_msg)
            return error_msg

    def chat(self, prompt: str, memory=None) -> str:
        """Chat method for general conversation"""
        return self._call_llm(prompt, system_prompt="You are a helpful literature agent for biological research. You can help users find and download relevant scientific papers.")

    def query_knowledge_base(self, temp_kb_id: str, query: str) -> str:
        """Query the temporary knowledge base and return an answer"""
        try:
            # Query the temporary knowledge base
            results = self._query_temporary_knowledge_base(temp_kb_id, query, top_k=3)
            
            if not results:
                return f"No relevant information found in knowledge base {temp_kb_id} for query: {query}"
            
            # Build context from search results
            context = "\n\n".join([
                f"Source: {result['title']} ({result['type']})\n{result['content']}"
                for result in results
            ])
            
            # Create enhanced prompt with context
            enhanced_prompt = f"""Based on the following information from the downloaded papers, please answer the user's question.

Relevant Information:
{context}

User Question: {query}

Please provide a comprehensive answer based on the information above. If the information is not sufficient to answer the question, please state that clearly."""
            
            # Get answer from LLM
            answer = self._call_llm(enhanced_prompt, system_prompt="You are a helpful literature agent that answers questions based on scientific papers. Provide accurate and detailed answers based on the given context.")
            
            # Add source information
            sources = [result['title'] for result in results]
            answer += f"\n\nSources: {', '.join(sources)}"
            
            return answer
            
        except Exception as e:
            error_msg = f"Error querying knowledge base: {str(e)}"
            print(error_msg)
            return error_msg

    def list_knowledge_bases(self) -> str:
        """List all available temporary knowledge bases"""
        try:
            if not os.path.exists(self.temp_knowledge_dir):
                return "No temporary knowledge bases found."
            
            kb_list = []
            for item in os.listdir(self.temp_knowledge_dir):
                item_path = os.path.join(self.temp_knowledge_dir, item)
                if os.path.isdir(item_path):
                    kb_info_path = os.path.join(item_path, 'kb_info.json')
                    if os.path.exists(kb_info_path):
                        import json
                        with open(kb_info_path, 'r', encoding='utf-8') as f:
                            kb_info = json.load(f)
                        
                        kb_list.append({
                            'id': item,
                            'created_at': kb_info.get('created_at', 0),
                            'papers': len(kb_info.get('processed_papers', [])),
                            'chunks': kb_info.get('total_chunks', 0)
                        })
            
            if not kb_list:
                return "No temporary knowledge bases found."
            
            # Sort by creation time (newest first)
            kb_list.sort(key=lambda x: x['created_at'], reverse=True)
            
            result = "Available Temporary Knowledge Bases:\n"
            for kb in kb_list:
                import datetime
                created_time = datetime.datetime.fromtimestamp(kb['created_at']).strftime('%Y-%m-%d %H:%M:%S')
                result += f"\n- ID: {kb['id']}"
                result += f"\n  Created: {created_time}"
                result += f"\n  Papers: {kb['papers']}"
                result += f"\n  Chunks: {kb['chunks']}"
                result += f"\n  Query with: literature_query {kb['id']} <your question>"
            
            return result
            
        except Exception as e:
            error_msg = f"Error listing knowledge bases: {str(e)}"
            print(error_msg)
            return error_msg

from langchain.chat_models import init_chat_model
from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    AIMessagePromptTemplate
)
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, module="langchain.memory")
warnings.filterwarnings("ignore", category=ResourceWarning, module="jieba")
from langchain.memory import ConversationBufferMemory
from agent.base import BaseAgent
from config import API_KEY, BASE_URL, MODEL_NAME
import os
import sys
# Add system Python path for jieba
sys.path.append('/Library/Frameworks/Python.framework/Versions/3.13/lib/python3.13/site-packages')
import jieba.analyse
import re

class CodeWriterAgent(BaseAgent):
    def __init__(self):
        self.llm = init_chat_model(
            MODEL_NAME,
            model_provider="openai",
            api_key=API_KEY,
            base_url=BASE_URL
        )
        # Read code generation specific system prompt
        prompt_path = os.path.join(os.path.dirname(__file__), '../prompts/code_writer_prompt.txt')
        with open(prompt_path, 'r', encoding='utf-8') as f:
            self.system_prompt = f.read().strip()
        # Read chat specific system prompt
        chat_prompt_path = os.path.join(os.path.dirname(__file__), '../prompts/code_writer_chat_prompt.txt')
        with open(chat_prompt_path, 'r', encoding='utf-8') as f:
            self.chat_system_prompt = f.read().strip()
        self.memory = ConversationBufferMemory(return_messages=True)

    def extract_keywords_ml(self, text, topK=3):
        try:
            keywords = jieba.analyse.extract_tags(text, topK=topK)
            return "_".join(keywords) if keywords else "result"
        except Exception as e:
            # Fallback to simple keyword extraction if jieba fails
            import re
            words = re.findall(r'\b\w+\b', text.lower())
            # Filter out common stop words
            stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'}
            keywords = [word for word in words if word not in stop_words and len(word) > 2][:topK]
            return "_".join(keywords) if keywords else "result"

    def extract_code_blocks(self, llm_output, lang):
        pattern = rf"```{lang}\s*\n?([\s\S]*?)```"
        return re.findall(pattern, llm_output, re.IGNORECASE)

    def save_to_file(self, folder, filename, content):
        os.makedirs(folder, exist_ok=True)
        with open(os.path.join(folder, filename), "w", encoding="utf-8") as f:
            f.write(content)

    def _call_llm(self, prompt: str, system_prompt: str = None, tools: list = None) -> str:
        try:
            # Build prompt template, support optional system/tools
            messages = []
            if system_prompt:
                messages.append(SystemMessagePromptTemplate.from_template(system_prompt))
            # Add history
            history = self.memory.load_memory_variables({})["history"]
            messages.extend(history)
            # Add user input
            messages.append(HumanMessagePromptTemplate.from_template("{input}"))
            # Optional: add tools (if any)
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
        output = self._call_llm(prompt, system_prompt=self.system_prompt, tools=tools)
        # Keyword extraction and code block saving logic
        keywords = self.extract_keywords_ml(prompt)
        py_blocks = self.extract_code_blocks(output, "python")
        bash_blocks = self.extract_code_blocks(output, "bash")
        if py_blocks:
            self.save_to_file("ResultsData", f"{keywords}.py", "\n\n".join(py_blocks))
        if bash_blocks:
            self.save_to_file("ResultsData", f"{keywords}.txt", "\n\n".join(bash_blocks))
        return output

    def chat(self, prompt: str, memory=None, tools: list = None) -> str:
        return self._call_llm(prompt, system_prompt=self.chat_system_prompt, tools=tools) 
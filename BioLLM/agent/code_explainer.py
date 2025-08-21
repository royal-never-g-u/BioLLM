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
from agent.base import BaseAgent
from config import API_KEY, BASE_URL, MODEL_NAME
import os

class CodeExplainerAgent(BaseAgent):
    def __init__(self):
        self.llm = init_chat_model(
            MODEL_NAME,
            model_provider="openai",
            api_key=API_KEY,
            base_url=BASE_URL
        )
        prompt_path = os.path.join(os.path.dirname(__file__), '../prompts/code_explainer_prompt.txt')
        with open(prompt_path, 'r', encoding='utf-8') as f:
            self.system_prompt = f.read().strip()
        self.memory = ConversationBufferMemory(return_messages=True)

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
        # 如果prompt为空或无意义，自动读取ResultsData下第一个py文件内容
        if not prompt or not prompt.strip():
            import os
            py_files = [f for f in os.listdir("ResultsData") if f.endswith(".py")]
            if py_files:
                with open(os.path.join("ResultsData", py_files[0]), "r", encoding="utf-8") as f:
                    prompt = f.read()
        return self._call_llm(prompt, system_prompt=self.system_prompt, tools=tools)

    def chat(self, prompt: str, memory=None, tools: list = None) -> str:
        return self._call_llm(prompt, system_prompt=self.system_prompt, tools=tools) 
class BaseAgent:
    def run(self, prompt: str, memory=None) -> str:
        raise NotImplementedError
    def chat(self, prompt: str, memory=None) -> str:
        raise NotImplementedError 
from agentz.llm.localstack_ollama import LocalstackOllamaLLM

class LLM:
    def summarize(self, text: str) -> str:
        """Summarize the given text using a local model."""
        raise NotImplementedError("LLM subclasses must implement summarize()")

class SummarizeText:
    def __init__(self):
        self.llm = LocalstackOllamaLLM()

summarize_text = SummarizeText()

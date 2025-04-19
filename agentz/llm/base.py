class LLM:
    def summarize(self, text: str) -> str:
        """Summarize the given text using a local model."""
        raise NotImplementedError("LLM subclasses must implement summarize()")

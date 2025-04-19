from agentz.llm.base import LLM

class DeepSeekLLM(LLM):
    def summarize(self, text: str) -> str:
        return f"[deepseek] 🧠 Insight from input: {text[:60]}..."

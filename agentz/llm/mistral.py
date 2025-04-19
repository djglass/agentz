import requests
from agentz.llm.base import LLM

class MistralLLM(LLM):
    def summarize(self, text: str) -> str:
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "mistral",
                    "prompt": f"Summarize the following CVEs as a security bulletin:\n\n{text}\n\nBe concise, clear, and actionable.",
                    "stream": False
                },
                timeout=60
            )
            response.raise_for_status()
            return response.json().get("response", "[mistral] ❌ No LLM response.")
        except requests.RequestException as e:
            return f"[mistral] 🔥 Request failed: {e}"

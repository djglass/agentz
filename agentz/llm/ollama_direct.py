import requests
import os

class DirectOllamaLLM:
    def summarize(self, prompt):
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": os.getenv("LLM_MODEL", "mistral"), "prompt": prompt},
                timeout=int(os.getenv("AGENTZ_LLM_TIMEOUT", "60"))
            )
            response.raise_for_status()
            return response.json().get("response", "").strip()
        except Exception as e:
            return f"[LLM Error - Direct Ollama]: {e}"

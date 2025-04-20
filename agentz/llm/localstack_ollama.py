import os
import requests

class LocalstackOllamaLLM:
    def summarize(self, prompt):
        api_id = os.getenv("LLM_API_ID")  # optionally hardcode if needed
        if not api_id:
            raise RuntimeError("LLM_API_ID is not set")

        url = f"http://localhost:4566/restapis/{api_id}/v1/_user_request_/hello"

        try:
            response = requests.post(
                url,
                json={"prompt": prompt},
                timeout=int(os.getenv("AGENTZ_LLM_TIMEOUT", "60"))
            )
            response.raise_for_status()
            return response.text.strip()
        except Exception as e:
            return f"[LLM Error - LocalStack]: {e}"

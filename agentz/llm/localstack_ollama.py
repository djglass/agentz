import subprocess
import requests
import json
from agentz.llm.base import LLM

class LocalstackOllamaLLM(LLM):
    def summarize(self, text: str) -> str:
        try:
            # Get latest API ID using awslocal
            result = subprocess.run(
                ["awslocal", "apigateway", "get-rest-apis"],
                capture_output=True, text=True, check=True
            )
            apis = json.loads(result.stdout).get("items", [])
            if not apis:
                return "[agentz] ❌ No API Gateway found."

            # Get most recent API ID
            api_id = sorted(apis, key=lambda x: x["createdDate"])[-1]["id"]
            url = f"http://localhost:4566/restapis/{api_id}/v1/_user_request_/hello"

            # Make the request
            response = requests.post(
                url,
                headers={"Content-Type": "application/json"},
                json={"prompt": text},
                timeout=60
            )
            response.raise_for_status()
            return response.json().get("response", "[agentz] ❌ No response from Lambda.")
        except Exception as e:
            return f"[agentz] 🔥 LocalStack/Ollama call failed: {e}"

# agentz/llm/localstack_ollama.py

from langchain_core.runnables import Runnable
from langchain_core.prompt_values import StringPromptValue
import requests

from agentz.utils.localstack_helper import get_latest_local_api_url

class LocalstackOllamaLLM(Runnable):
    def __init__(self):
        self.endpoint = get_latest_local_api_url()

    def invoke(self, input, config: dict = None, **kwargs) -> str:
        if isinstance(input, StringPromptValue):
            input = input.to_string()
        elif isinstance(input, dict) and "query" in input:
            input = input["query"]
        elif not isinstance(input, str):
            input = str(input)

        try:
            response = requests.post(
                self.endpoint,
                json={"input": input},
                timeout=120
            )
            response.raise_for_status()
            data = response.json()

            # 🧪 Debug response handling
            if "response" not in data:
                print("⚠️ Unexpected response structure:", data)
                return "[LLM error] Unexpected response format"

            return data["response"]

        except Exception as e:
            return f"[LLM error] {str(e)}"

    def __call__(self, input, **kwargs) -> str:
        return self.invoke(input, **kwargs)

from langchain_core.runnables import Runnable
from langchain_core.prompt_values import StringPromptValue
import requests

from agentz.utils.localstack_helper import get_latest_local_api_url

url = get_latest_local_api_url()

class LocalstackOllamaLLM(Runnable):
    def __init__(self):
        self.endpoint = get_latest_local_api_url()

    def invoke(self, input, config: dict = None, **kwargs) -> str:
        # 🔧 Convert LangChain prompt objects to plain string
        if isinstance(input, StringPromptValue):
            input = input.to_string()
        elif isinstance(input, dict) and "question" in input:
            input = input["question"]
        elif not isinstance(input, str):
            input = str(input)

        try:
            response = requests.post(self.endpoint, json={"input": input})
            response.raise_for_status()
            return response.json().get("output", "No response")
        except Exception as e:
            return f"[LLM error] {str(e)}"

    def __call__(self, input, **kwargs) -> str:
        return self.invoke(input, **kwargs)

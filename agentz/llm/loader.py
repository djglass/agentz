import os
from agentz.llm.localstack_ollama import LocalstackOllamaLLM
from agentz.llm.ollama_direct import DirectOllamaLLM

def get_llm():
    model_name = os.getenv("LLM_NAME", "localstack").lower()

    if model_name == "localstack":
        return LocalstackOllamaLLM()
    else:
        return DirectOllamaLLM()

import os
from agentz.llm.mistral import MistralLLM
from agentz.llm.deepseek import DeepSeekLLM
from agentz.llm.localstack_ollama import LocalstackOllamaLLM

def get_llm():
    model_name = os.getenv("LLM_NAME", "mistral").lower()

    if model_name == "localstack":
        return LocalstackOllamaLLM()
    elif model_name == "deepseek":
        return DeepSeekLLM()
    elif model_name == "mistral":
        return MistralLLM()
    else:
        raise ValueError(f"Unsupported LLM model: {model_name}")

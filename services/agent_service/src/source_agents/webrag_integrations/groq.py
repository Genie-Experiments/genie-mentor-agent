from llama_index.core import Settings
from llama_index.llms.groq import Groq as LlamaGroq

from ..webrag_utils.config import LLM_DEFAULT_MODEL


class GroqIntegration:
    def __init__(self, api_key: str, model: str = LLM_DEFAULT_MODEL):
        client = LlamaGroq(api_key=api_key, model=model)
        Settings.groqllm = client

from llama_index.core import Settings
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI

from ..webrag_utils.config import EMBED_DEFAULT_MODEL


class OpenAIIntegration:
    def __init__(self, api_key: str, embedding_model: str = EMBED_DEFAULT_MODEL):

        client = OpenAI(api_key=api_key)
        Settings.openai_llm = client
        embeddings_client = OpenAIEmbedding(api_key=api_key, model=embedding_model)
        Settings.embed_model = embeddings_client

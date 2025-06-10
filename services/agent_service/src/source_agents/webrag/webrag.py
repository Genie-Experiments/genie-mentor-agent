from llama_index.core import Document, StorageContext, VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.vector_stores import SimpleVectorStore
from llama_index.core.retrievers import QueryFusionRetriever
from llama_index.retrievers.bm25 import BM25Retriever
from ..webrag_utils.config import OPENAI_API_KEY, GROQ_API_KEY
from ..webrag_integrations.openai import OpenAIIntegration
from ..webrag_integrations.groq import GroqIntegration
from ..webrag_utils.retry import retry_with_reduction_and_backoff
from groq import Groq
from llama_index.core import Settings

from ...utils.logging import setup_logger, get_logger

setup_logger()
logger = get_logger("WebRAG")
openai_integration = OpenAIIntegration(api_key=OPENAI_API_KEY)

groq_integration = GroqIntegration(api_key=GROQ_API_KEY)


class RAG:
    def __init__(self,model, max_retries=15, reduction_percent=0.2):
        self.storage_context = StorageContext.from_defaults(vector_store=SimpleVectorStore())
        self.model = model
        self.client = Groq(api_key=GROQ_API_KEY)
        self.temperature = 0.5
        self.max_retries = max_retries
        self.reduction_percent = reduction_percent
        self.retriever = None
    
    def set_llm(self, llm: str = "groq"):
        """
        Set the LLM to use for RAG.
        
        :param llm: The LLM to use ('groq').
        """
        GroqIntegration(api_key=GROQ_API_KEY)
        if llm == "groq":
            if not hasattr(Settings, "groqllm"):
                raise RuntimeError("GroqIntegration is not initialized. Please initialize it first.")
            self.llm_instance = Settings.groqllm
        else:
            raise ValueError("Invalid LLM specified for RAG. Only 'groq' is supported.")
        
    def build_index(self, documents):
        
        splitter = SentenceSplitter(chunk_size=256)
        self.index = VectorStoreIndex.from_documents(
            documents=documents, transformations=[splitter]
        )

        bm25_retriever = BM25Retriever.from_defaults(
            docstore=self.index.docstore, similarity_top_k=15
        )

        vector_retriever = self.index.as_retriever(similarity_top_k=5)
        self.retriever = QueryFusionRetriever(
            [vector_retriever, bm25_retriever],
            similarity_top_k=5,
            num_queries=4,
            mode="reciprocal_rerank",
            use_async=True,
            verbose=True,
        )

    def query_index(self, query):
       
        if not self.retriever:
            raise RuntimeError("Retrievers are not initialized. Call build_index() first.")
        
        results = self.retriever.retrieve(query)
        
        if not results:
            raise RuntimeError("No results retrieved. Check document ingestion and query.")
        
        return [node.node.text for node in results]
    
    def query_llm(self, query, context, template):
        def process_fn(context):
            message_content = template.format(context=context, query=query)
            logger.info(f"[WebSearch] Prompt Formatted :  {message_content}")
            response = self.client.chat.completions.create(
                messages=[{"role": "system", "content": message_content}],
                model=self.model,
                temperature=self.temperature,
            )
            return response.choices[0].message.content.strip()

        final_response, final_context = retry_with_reduction_and_backoff(
            process_fn=process_fn, context=context, max_retries=5, delay_for_rate_limit=5
        )
        return final_response, final_context
import json, asyncio
from autogen_core import RoutedAgent, MessageContext, message_handler
from ..protocols.message import Message

from .webrag.webrag import RAG
from .webrag_utils.data_scrapper import DataScraper
from .webrag_utils.google_search import GoogleSearch
from .webrag_utils.config import (
    GROQ_API_KEY, GOOGLE_API_KEY, GOOGLE_CX,
    LLM_DEFAULT_MODEL, TOP_K
)
from ..prompts.prompts import response_generation_prompt
from ..utils.logging import setup_logger, get_logger

setup_logger()
logger = get_logger("my_module")

class WebRAGAgent(RoutedAgent):
    def __init__(self):
        super().__init__("web_rag_agent")
        self.google_search = GoogleSearch(api_key=GOOGLE_API_KEY, cx=GOOGLE_CX)
        self.scraper = DataScraper()

    def fetch_urls(self, query):
        results = self.google_search.search(
            query=query,
            max_general_results=TOP_K,
            max_video_results=0,
            include_videos=False
        )
        return results[:TOP_K]


    def rag_pipeline(self, query, urls):
        logger.info("SCRAPPING DATA FROM URLS")
        documents = self.scraper.fetch_data_from_urls(urls)
        rag = RAG(model=LLM_DEFAULT_MODEL)
        rag.set_llm("groq")
        logger.info("INDEXING DOCUMENTS")
        rag.build_index(documents)
        contexts = rag.query_index(query)
        combined_context = "\n".join(contexts)
        logger.info("RUNNING USER QUERY")
        answer, used_context = rag.query_llm(
            query=query,
            context=combined_context,
            template=response_generation_prompt
        )
        return answer, used_context

    @message_handler
    async def handle(self, message: Message, ctx: MessageContext) -> Message:
        query = message.content.strip()
        try:
            loop = asyncio.get_event_loop()
            logger.info("Fetching URLs")
            metadata = await loop.run_in_executor(None, self.fetch_urls, query)
            urls = [item.get("url") for item in metadata if item.get("url")]
            logger.info("BUILDING RAG OVER WEB URLS")
            answer, context = await loop.run_in_executor(None, self.rag_pipeline, query, urls)
            return Message(content=json.dumps({
                "answer": answer,
                "sources": [context],
                "metadata": [
                    {
                        "title": item.get("title"),
                        "url": item.get("url"),
                        "description": item.get("description")
                    } for item in metadata
                ],
                "error": None
            }))
        except Exception as e:
            return Message(content=json.dumps({
                "answer": "An error occured while processing Query from WebSearch",
                "sources": [],
                "metadata":[],
                "error":str(e)
            }))

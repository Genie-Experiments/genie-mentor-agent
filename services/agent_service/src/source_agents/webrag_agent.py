import asyncio
import json

from autogen_core import MessageContext, RoutedAgent, message_handler

from ..prompts.websearch_agent_prompt import response_generation_prompt
from ..protocols.message import Message
from ..utils.logging import get_logger, setup_logger
from .webrag.webrag import RAG
from .webrag_utils.config import (GOOGLE_API_KEY, GOOGLE_CX, GROQ_API_KEY,
                                  LLM_DEFAULT_MODEL, TOP_K)
from .webrag_utils.data_scrapper import DataScraper
from .webrag_utils.google_search import GoogleSearch

setup_logger()
logger = get_logger("WebRAGAgent")


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
            include_videos=False,
        )
        return results[:TOP_K]

    def rag_pipeline(self, query, urls):
        logger.info("[WebSearch] SCRAPPING DATA FROM URLS")
        documents = self.scraper.fetch_data_from_urls(urls)
        rag = RAG(model=LLM_DEFAULT_MODEL)
        rag.set_llm("groq")
        logger.info("[WebSearch] INDEXING DOCUMENTS")
        rag.build_index(documents)
        contexts = rag.query_index(query)
        logger.info("[WebSearch] RUNNING USER QUERY")
        answer, used_context = rag.query_llm(
            query=query, context=contexts, template=response_generation_prompt
        )
        return answer, used_context

    @message_handler
    async def handle(self, message: Message, ctx: MessageContext) -> Message:
        query = message.content.strip()
        try:
            loop = asyncio.get_event_loop()
            logger.info("[WebSearch] Fetching URLs")
            metadata = await loop.run_in_executor(None, self.fetch_urls, query)
            urls = [item.get("url") for item in metadata if item.get("url")]
            logger.info("[WebSearch] BUILDING RAG OVER WEB URLS")
            answer, context = await loop.run_in_executor(
                None, self.rag_pipeline, query, urls
            )
            return Message(
                content=json.dumps(
                    {
                        "answer": answer,
                        "sources": [context],
                        "metadata": [
                            {
                                "title": item.get("title"),
                                "url": item.get("url"),
                                "description": item.get("description"),
                            }
                            for item in metadata
                        ],
                        "error": None,
                    }
                )
            )
        except Exception as e:
            return Message(
                content=json.dumps(
                    {
                        "answer": "An error occured while processing Query from WebSearch",
                        "sources": [],
                        "metadata": [],
                        "error": str(e),
                    }
                )
            )

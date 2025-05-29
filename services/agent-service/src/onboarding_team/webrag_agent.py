import json, asyncio
from autogen_core import RoutedAgent, MessageContext, message_handler
from .message import Message

from ..webrag.webrag import RAG
from ..webrag_utils.data_scrapper import DataScraper
from ..webrag_utils.google_search import GoogleSearch
from ..webrag_utils.config import (
    GROQ_API_KEY, GOOGLE_API_KEY, GOOGLE_CX,
    LLM_DEFAULT_MODEL, TOP_K_URLS
)
from .prompts import response_generation_prompt

class WebRAGAgent(RoutedAgent):
    def __init__(self):
        super().__init__("web_rag_agent")
        self.google_search = GoogleSearch(api_key=GOOGLE_API_KEY, cx=GOOGLE_CX)
        self.scraper = DataScraper()

    def fetch_urls(self, query):
        results = self.google_search.search(
            query=query,
            max_general_results=TOP_K_URLS,
            max_video_results=0,
            include_videos=False
        )
        return [result['url'] for result in results[:TOP_K_URLS]]

    def rag_pipeline(self, query, urls):
        print("[DEBUG] SCRAPPING DATA FROM URLS")
        documents = self.scraper.fetch_data_from_urls(urls)
        rag = RAG(model=LLM_DEFAULT_MODEL)
        rag.set_llm("groq")
        print("[DEBUG] INDEXING DOCUMENTS")
        rag.build_index(documents)
        contexts = rag.query_index(query)
        combined_context = "\n".join(contexts)
        print("[DEBUG] RUNNING USER QUERY")
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
            print("[DEBUG] Fetching URLs")
            urls = await loop.run_in_executor(None, self.fetch_urls, query)
            print("[DEBUG] BUILDING RAG OVER WEB URLS")
            answer, context = await loop.run_in_executor(None, self.rag_pipeline, query, urls)
            return Message(content=json.dumps({
                "answer": answer,
                "sources": [context],
                "urls":urls
            }))
        except Exception as e:
            return Message(content=json.dumps({
                "answer": f"Error: {str(e)}",
                "sources": [],
                "urls":[]
            }))

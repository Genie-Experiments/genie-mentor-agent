import json, os, aiohttp
from autogen_core import RoutedAgent, MessageContext, message_handler
from .message import Message

SEARCH_ENDPOINT = "https://api.bing.microsoft.com/v7.0/search"
BING_KEY        = os.getenv("BING_API_KEY")     

class WebRAGAgent(RoutedAgent):
  
    def __init__(self) -> None:
        super().__init__("web_rag_agent")

    @message_handler
    async def handle(self, message: Message, ctx: MessageContext) -> Message:
        query = message.content.strip()
        if not BING_KEY:
            return Message(content=json.dumps(
                {"answer": "Web search key not configured.", "sources": []}
            ))

        headers = {"Ocp-Apim-Subscription-Key": BING_KEY}
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(SEARCH_ENDPOINT, params={"q": query, "mkt": "en-US"}) as resp:
                data = await resp.json()

        web_pages = data.get("webPages", {}).get("value", [])[:3]
        snippets  = [item["snippet"] for item in web_pages]
        urls      = [item["url"]     for item in web_pages]

        summary = " ".join(snippets)
        return Message(content=json.dumps({"answer": summary, "sources": urls}))

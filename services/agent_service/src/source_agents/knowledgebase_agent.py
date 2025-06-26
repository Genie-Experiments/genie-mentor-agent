import asyncio
import json
import os
from typing import Any, Dict

from autogen_core import MessageContext, RoutedAgent, message_handler
from langchain.prompts import PromptTemplate
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_groq import ChatGroq

from ..prompts.kb_agent_prompt import kb_assistant_prompt
from ..protocols.message import Message
from ..utils.logging import get_logger, setup_logger
from ..protocols.schemas import KBResponse

setup_logger()
logger = get_logger("KBAgent")


def get_embedding_model() -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")



class KBAgent(RoutedAgent):
    def __init__(self, persist_directory: str = None):
        super().__init__("knowledgebase_agent")
        self.persist_directory = persist_directory or os.getenv("CHROMA_DB_PATH")
        if not self.persist_directory:
            raise ValueError(
                "persist_directory not set and CHROMA_DB_PATH missing in .env"
            )

        self.embedding_model = get_embedding_model()
        self.groq_api_key = os.environ.get("GROQ_API_KEY")
        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY environment variable not set")


    def query_knowledgebase(
        self, query: str, model_name: str = "meta-llama/llama-4-scout-17b-16e-instruct"
    ) -> Dict[str, Any]:
        try:
            vector_store = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embedding_model,
            )

            retriever = vector_store.as_retriever(search_kwargs={"k": 5})

            llm = ChatGroq(
                temperature=0.5, groq_api_key=self.groq_api_key, model_name=model_name
            )

            prompt = PromptTemplate(
                input_variables=["context", "query"],
                template=kb_assistant_prompt,
            )
            context_chunks = []

            documents = retriever.invoke(query)
            for doc in documents:
                context_chunks.append(doc.page_content)
            chain = prompt | llm
            message = chain.invoke({"context": context_chunks, "query": query})
            result_text = (
                message.content if hasattr(message, "content") else str(message)
            )

            metadata_list = []
            for doc in documents:
                meta = doc.metadata
                pdf_name = (
                    os.path.basename(meta.get("source", ""))
                    if "source" in meta
                    else "Unknown Document"
                )
                page_number = meta.get("page", 0)
                entry = {
                    "title": pdf_name,
                    "source": meta.get("source", ""),
                    "page": page_number,
                }
                if meta.get("title"):
                    entry["document_title"] = meta["title"]
                metadata_list.append(entry)

            return {
                "answer": result_text,
                "sources": context_chunks,
                "metadata": metadata_list,
                "error": None,
            }

        except Exception as e:
            logger.error(f"Error querying knowledge base : {e}")
            return {
                "answer": "Knowledge Base is currently unavailable",
                "sources": [],
                "metadata": [],
                "error": str(e),
            }

    @message_handler
    async def handle(self, message: Message, ctx: MessageContext) -> Message:
            query = message.content.strip()
            try:
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(None, self.query_knowledgebase, query)
                validated = KBResponse(**result)
                return Message(content=validated.model_dump_json())
           
            except Exception as e:
                logger.error(f"Error in KnowledgeBaseAgent handler : {e}")
                return Message(content=json.dumps({
                    "answer": "An error occurred while processing your request",
                    "sources": [],
                    "metadata": [],
                    "error": str(e)
                }))
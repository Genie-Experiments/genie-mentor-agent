import json
import asyncio
import os
from autogen_core import RoutedAgent, MessageContext, message_handler
from ..protocols.message import Message
from langchain.chains import RetrievalQA
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_groq import ChatGroq
from typing import Dict,Any
from ..utils.logging import setup_logger, get_logger

setup_logger()
logger = get_logger("my_module")

def get_embedding_model() -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(model_name='all-MiniLM-L6-v2')

class KBAgent(RoutedAgent):
    def __init__(self, persist_directory: str = None):
        super().__init__("knowledgebase_agent")
        self.persist_directory = persist_directory or os.getenv('CHROMA_DB_PATH')
        if not self.persist_directory:
            raise ValueError('persist_directory not set and CHROMA_DB_PATH missing in .env')
        
        self.embedding_model = get_embedding_model()
        self.groq_api_key = os.environ.get('GROQ_API_KEY')
        if not self.groq_api_key:
            raise ValueError('GROQ_API_KEY environment variable not set')

    def query_knowledgebase(self, query: str, model_name: str = 'meta-llama/llama-4-scout-17b-16e-instruct', 
                           temperature: float = 0.1, k: int = 3) -> Dict[str, Any]:
        try:
            vector_store = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embedding_model
            )
            
            retriever = vector_store.as_retriever(search_kwargs={'k': k})
            llm = ChatGroq(
                temperature=temperature, 
                groq_api_key=self.groq_api_key,
                model_name=model_name
            )
            
            qa_chain = RetrievalQA.from_chain_type(
                llm=llm,
                chain_type='stuff',
                retriever=retriever,
                return_source_documents=True
            )
            result = qa_chain({'query': query})
            metadata_list = []
            for doc in result['source_documents']:
                meta = doc.metadata
                pdf_name = os.path.basename(meta.get('source', '')) if 'source' in meta else "Unknown Document"
                page_number = meta.get('page', 0)
                
                # Build metadata entry
                metadata_entry = {
                    "title": pdf_name,
                    "source": meta.get('source', ''), 
                    "page": page_number
                }
                
                if 'title' in meta and meta['title']:
                    metadata_entry["document_title"] = meta['title']
               
                metadata_list.append(metadata_entry)
            
            return {
                'answer': result['result'],
                'sources': [doc.page_content for doc in result['source_documents']],
                'metadata': metadata_list,
                'error': None
            }

        except Exception as e:
            logger.exception("Error querying knowledge base")
            return {
                'answer': "Knowledge Base is currently unavailable",
                'sources': [],
                'metadata': [],
                'error': str(e)
            }

    @message_handler
    async def handle(self, message: Message, ctx: MessageContext) -> Message:
        query = message.content.strip()
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, self.query_knowledgebase, query)
            
            return Message(content=json.dumps({
                "answer": result['answer'],
                "sources": result['sources'],
                "metadata": result['metadata'],
                "error": result['error']
            }))
            
        except Exception as e:
            logger.exception("Error in KnowledgeBaseAgent handler")
            return Message(content=json.dumps({
                "answer": "An error occurred while processing your request",
                "sources": [],
                "metadata": [],
                "error": str(e)
            }))
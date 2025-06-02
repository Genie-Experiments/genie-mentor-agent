import os
from typing import Any, Dict, Optional

from dotenv import  load_dotenv
from langchain.chains import RetrievalQA
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_groq import ChatGroq
import logging
logging.basicConfig(
    level=logging.INFO,  
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
load_dotenv()

def get_embedding_model() -> HuggingFaceEmbeddings:
   
    return HuggingFaceEmbeddings(model_name='all-MiniLM-L6-v2')

def query_knowledgebase(
    query: str, 
    persist_directory: Optional[str] = None, 
    model_name: str = 'meta-llama/llama-4-scout-17b-16e-instruct', 
    temperature: float = 0.1, 
    k: int = 5
) -> Dict[str, Any]:
    try:
        if persist_directory is None:
            persist_directory = os.getenv('CHROMA_DB_PATH')

        if not persist_directory:
            raise ValueError('persist_directory not set and CHROMA_DB_PATH missing in .env')
        
        embedding_model = get_embedding_model()
        from pathlib import Path
        logging.info(f"persist_directory = {Path(persist_directory).resolve()}")

        
        vector_store = Chroma(
            persist_directory=persist_directory,
            embedding_function=embedding_model
        )
        logging.info('Total documents in store:', vector_store._collection.count())

        retriever = vector_store.as_retriever(search_kwargs={'k': k})
        
        groq_api_key = os.environ.get('GROQ_API_KEY')
        if not groq_api_key:
            raise ValueError('GROQ_API_KEY environment variable not set')
        
        llm = ChatGroq(
            temperature=temperature, 
            groq_api_key=groq_api_key,
            model_name=model_name
        )
        logging.info('Running Knowledge base QA Chain')
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type='stuff',
            retriever=retriever,
            return_source_documents=True
        )
        result = qa_chain({'query': query})
    
        return {
            'answer': result['result'],
            'sources': [doc.page_content for doc in result['source_documents']],
            'error':None
        }

    except Exception as e:
        return {
            'answer': "Knowledge Base Right Now is not Working, We failed to get results",
            'sources': [],
            'error':e
        }




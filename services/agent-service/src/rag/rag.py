# Standard library imports
import os
from typing import Any, Dict, List, Optional

# Third-party imports
from dotenv import find_dotenv, load_dotenv
from langchain.chains import RetrievalQA
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_groq import ChatGroq

# Load environment variables
load_dotenv()

def get_embedding_model() -> HuggingFaceEmbeddings:
    """
    Create and return an embedding model.
    """
    return HuggingFaceEmbeddings(model_name='all-MiniLM-L6-v2')

def query_knowledgebase(
    query: str, 
    persist_directory: Optional[str] = None, 
    model_name: str = 'meta-llama/llama-4-scout-17b-16e-instruct', 
    temperature: float = 0.1, 
    k: int = 5
) -> Dict[str, Any]:
    """
    Query the knowledgebase using Groq LLM.
    
    Args:
        query: The user query or question
        persist_directory: Path to the vector store
        model_name: Groq model to use
        temperature: Temperature for generation
        k: Number of relevant documents to retrieve
        
    Returns:
        Response from the Groq model
    """
    # ✅ fallback to .env if not passed explicitly
    if persist_directory is None:
        persist_directory = os.getenv('CHROMA_DB_PATH')

    if not persist_directory:
        raise ValueError('persist_directory not set and CHROMA_DB_PATH missing in .env')
    
    # Initialize the embedding model
    embedding_model = get_embedding_model()
    from pathlib import Path
    print('[DEBUG] persist_directory =', Path(persist_directory).resolve())
    
    # Load vector store
    vector_store = Chroma(
        persist_directory=persist_directory,
        embedding_function=embedding_model
    )
    print('[RAG] Total documents in store:', vector_store._collection.count())

    # Create a retriever
    retriever = vector_store.as_retriever(search_kwargs={'k': k})
    
    # Initialize Groq LLM
    groq_api_key = os.environ.get('GROQ_API_KEY')
    if not groq_api_key:
        raise ValueError('GROQ_API_KEY environment variable not set')
    
    llm = ChatGroq(
        temperature=temperature, 
        groq_api_key=groq_api_key,
        model_name=model_name
    )
    
    # Create QA chain
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type='stuff',
        retriever=retriever,
        return_source_documents=True
    )
    
    # Run the query
    result = qa_chain({'query': query})
    print('[RAG] Retrieved documents:')
    for doc in result['source_documents']:
        print(doc.page_content[:150])

    return {
        'answer': result['result'],
        'sources': [doc.page_content for doc in result['source_documents']]
    }


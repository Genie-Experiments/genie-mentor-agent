from langchain_groq import ChatGroq
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
import os

from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv()) #

def get_embedding_model():
    """
    Create and return an embedding model.
    """
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def query_knowledgebase(query, persist_directory="db", model_name="gemma2-9b-it", temperature=0.1, k=4):
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
    # Initialize the embedding model
    embedding_model = get_embedding_model()
    
    # Load vector store
    vector_store = Chroma(
        persist_directory=persist_directory,
        embedding_function=embedding_model
    )
    
    # Create a retriever
    retriever = vector_store.as_retriever(search_kwargs={"k": k})
    
    # Initialize Groq LLM
    groq_api_key = os.environ.get("GROQ_API_KEY")
    if not groq_api_key:
        raise ValueError("GROQ_API_KEY environment variable not set")
    
    llm = ChatGroq(
        temperature=temperature, 
        groq_api_key=groq_api_key,
        model_name=model_name
    )
    
    # Create QA chain
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True
    )
    
    # Run the query
    result = qa_chain({"query": query})
    
    return {
        "answer": result["result"],
        "source_documents": [doc.page_content for doc in result["source_documents"]]
    }


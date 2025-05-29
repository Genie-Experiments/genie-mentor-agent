from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
import os
import requests
import json
import tempfile
from pathlib import Path

def load_document(file_path: str):
    """
    Load a document from the specified file path.
    """
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    return documents

def split_documents(documents, chunk_size=1200, chunk_overlap=100):
    """
    Split documents into smaller chunks.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
    )
    return text_splitter.split_documents(documents)

def get_embedding_model():
    """
    Create and return an embedding model.
    """
    return HuggingFaceEmbeddings(model_name='all-MiniLM-L6-v2')

def store_embeddings(documents, embedding_model, persist_directory='../../shared-lib/chroma_db'):
    """
    Store documents in a Chroma vector store using the embedding model.
    """
    vector_store = Chroma.from_documents(
        documents=documents,
        embedding=embedding_model,
        persist_directory=persist_directory
    )
    vector_store.persist()
    return vector_store

def ingest_files(file_paths):
    """
    Ingest files by loading, splitting, embedding, and storing them.
    """
    embedding_model = get_embedding_model()
    
    for file_path in file_paths:
        documents = load_document(file_path)
        split_docs = split_documents(documents)
        store_embeddings(split_docs, embedding_model)
        print(f'Processed {file_path} and stored embeddings.')

def process_uploaded_file(file_content, filename, persist_directory=os.getenv('CHROMA_DB_PATH')):
    """
    Process an uploaded file by saving it temporarily, loading it, splitting it,
    and storing embeddings in the vector store.
    
    Args:
        file_content: Binary content of the uploaded file
        filename: Name of the uploaded file
        persist_directory: Directory to persist the vector store
        
    Returns:
        dict: Information about the ingested file
    """
    # Create temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(filename).suffix) as temp_file:
        temp_file.write(file_content)
        temp_file_path = temp_file.name
    
    try:
        # Get embedding model
        embedding_model = get_embedding_model()
        
        # Load document
        documents = load_document(temp_file_path)
        
        # Split documents
        split_docs = split_documents(documents)
        
        # Store embeddings
        vector_store = store_embeddings(split_docs, embedding_model, persist_directory)
        
        # Return information about the ingested file
        return {
            'filename': filename,
            'document_chunks': len(split_docs),
            'status': 'success',
            'message': f'Successfully ingested {filename} with {len(split_docs)} chunks.'
        }
    except Exception as e:
        return {
            'filename': filename,
            'status': 'error',
            'message': str(e)
        }
    finally:
        # Clean up temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

def retrieve_and_query(query, k=3, persist_directory='../../shared-lib/chroma_db'):
    """
    Retrieve relevant documents from the vector store and run the query through Groq API.
    
    Args:
        query: User's question or query
        k: Number of most relevant documents to retrieve
        persist_directory: Directory where the vector store is persisted
        
    Returns:
        Response from the Groq API
    """
    # Get embedding model
    embedding_model = get_embedding_model()
    
    # Load the existing vector store
    vector_store = Chroma(
        embedding_function=embedding_model,
        persist_directory=persist_directory
    )
    
    # Retrieve the most relevant documents
    retrieved_docs = vector_store.similarity_search(query, k=k)
    
    # Extract content from the retrieved documents
    context = '\n\n'.join([doc.page_content for doc in retrieved_docs])
    
    # Prepare the prompt for Groq API
    prompt = f'''You are a helpful assistant answering questions based on the provided information.
    
Context:
{context}

Question: {query}

Based strictly on the context provided, answer the question. If the answer is not contained within the context, say "I don't have enough information to answer this question."
'''
    
    # Call Groq API
    api_key = os.environ.get('GROQ_API_KEY')
    if not api_key:
        raise ValueError('GROQ_API_KEY environment variable not set')
        
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'model': 'llama3-70b-8192',
        'messages': [{'role': 'user', 'content': prompt}],
        'temperature': 0.1
    }
    
    response = requests.post(
        'https://api.groq.com/openai/v1/chat/completions',
        headers=headers,
        data=json.dumps(payload)
    )
    
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        return f'Error: {response.status_code} - {response.text}'

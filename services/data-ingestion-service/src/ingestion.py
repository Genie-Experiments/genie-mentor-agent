from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
import os
import tempfile
from pathlib import Path

def load_document(file_path: str):
   
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    return documents

def split_documents(documents, chunk_size=1200, chunk_overlap=100):
 
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
    )
    return text_splitter.split_documents(documents)

def get_embedding_model():
   
    return HuggingFaceEmbeddings(model_name='all-MiniLM-L6-v2')

def store_embeddings(documents, embedding_model, persist_directory='../../knowledge-base-chroma-index/chroma_db'):
    
    vector_store = Chroma.from_documents(
        documents=documents,
        embedding=embedding_model,
        persist_directory=persist_directory
    )
    vector_store.persist()
    return vector_store

def ingest_files(file_paths):
  
    embedding_model = get_embedding_model()
    
    for file_path in file_paths:
        documents = load_document(file_path)
        split_docs = split_documents(documents)
        store_embeddings(split_docs, embedding_model)
        print(f'Processed {file_path} and stored embeddings.')

def process_uploaded_file(file_content, filename, persist_directory=os.getenv('CHROMA_DB_PATH')):

    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(filename).suffix) as temp_file:
        temp_file.write(file_content)
        temp_file_path = temp_file.name
    
    try:
        embedding_model = get_embedding_model()
        documents = load_document(temp_file_path)
        split_docs = split_documents(documents)
        vector_store = store_embeddings(split_docs, embedding_model, persist_directory)
        
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
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

import os
from pathlib import Path

def ingest_folder(folder_path: str, persist_directory="services/knowledge-base-chroma-index/chroma_db"):
    pdf_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.pdf')]
    embedding_model = get_embedding_model()

    for filename in pdf_files:
        file_path = os.path.join(folder_path, filename)
        try:
            documents = load_document(file_path)
            split_docs = split_documents(documents)
            store_embeddings(split_docs, embedding_model, persist_directory)
            print(f'[INFO] ✅ Ingested {filename} with {len(split_docs)} chunks.')
        except Exception as e:
            print(f'[ERROR] ❌ Failed to ingest {filename}: {e}')


if __name__ == '__main__':
   
    ingest_folder('../docs') 
# services/agent_service/src/multihop_resp/utils.py

import os
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

def get_chroma_retriever(persist_directory, embedding_model, k=8):
    vector_store = Chroma(
        persist_directory=persist_directory,
        embedding_function=embedding_model,
    )
    return vector_store.as_retriever(search_kwargs={"k": k})

def retrieve_docs(query, retriever):
    return retriever.invoke(query)

def test_chroma_db():
    import os
    from langchain_community.vectorstores import Chroma
    chroma_db_path = os.environ.get("CHROMA_DB_PATH")
    if not chroma_db_path:
        raise RuntimeError("CHROMA_DB_PATH environment variable is not set.")
    db = Chroma(persist_directory=chroma_db_path, embedding_function=None)
    print("Number of documents/chunks in the database:", db._collection.count())
    # Print the first 200 characters of each chunk
    docs = db._collection.get()["documents"]
    for i, doc in enumerate(docs):
        print(f"Chunk {i+1}: {doc[:200]}\n")

if __name__ == "__main__":
    test_chroma_db()
"""
Data Ingestion Service - Main Entry Point
This service manages document sources, processing, and retrieval for the Genie Mentor Agent platform.
"""

from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from rag import query_knowledgebase
from ingestion import process_uploaded_file
import os

app = FastAPI(
    title="Data Ingestion Service",
    description="Document management and RAG for Genie Mentor Agent",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Genie Mentor Agent Data Ingestion Service API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# Knowledgebase management endpoints will be implemented here
# Document processing endpoints will be implemented here
# RAG query endpoints will be implemented here

@app.post("/api/rag/query")
async def rag_query(query: str):
    try:
        result = query_knowledgebase(
            query=query
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ingestion/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Endpoint for uploading PDF files for ingestion into the knowledge base.
    
    Args:
        file: The PDF file to be uploaded and ingested
        
    Returns:
        Information about the ingestion process
    """
    # Check if the file is a PDF
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are currently supported")
    
    try:
        # Read the file content
        file_content = await file.read()
        
        # Process the uploaded file
        result = process_uploaded_file(file_content, file.filename)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8003)

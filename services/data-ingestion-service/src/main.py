"""
Data Ingestion Service - Main Entry Point
This service manages document sources, processing, and retrieval for the Genie Mentor Agent platform.
"""

from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from .ingestion import process_uploaded_file
from dotenv import load_dotenv
import os
app = FastAPI(
    title='Data Ingestion Service',
    description='Document management and RAG for Genie Mentor Agent',
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],  # Update with specific origins in production
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# Load environment variables
load_dotenv(override=True)


@app.get('/')
async def root():
    return {'message': 'Genie Mentor Agent Data Ingestion Service API'}


@app.get('/health')
async def health_check():
    return {'status': 'healthy'}

@app.post('/api/documents')
async def upload_file(file: UploadFile = File(...)):
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail='Only PDF files are currently supported')
    
    try:
        file_content = await file.read()
        persist_path = os.getenv('CHROMA_DB_PATH')
        print(f'[DEBUG] persist_path = {persist_path}')
        result = process_uploaded_file(file_content, file.filename, persist_directory=persist_path)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='0.0.0.0', port=8003)

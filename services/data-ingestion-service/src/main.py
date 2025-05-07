"""
Data Ingestion Service - Main Entry Point
This service manages document sources, processing, and retrieval for the Genie Mentor Agent platform.
"""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware

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

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8003)

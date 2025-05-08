"""
Agent Service - Main Entry Point
This service implements the core agent orchestration for both Learning Bot and Onboarding Bot.
"""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from rag.rag import query_knowledgebase

app = FastAPI(
    title="Bot Service",
    description="Agent orchestration service for Genie Mentor Agent",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Genie Mentor Agent Service API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/api/rag/query")
async def rag_query(query: str):
    print(f"Received query: {query}")
    try:
        result = query_knowledgebase(
            query=query
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)

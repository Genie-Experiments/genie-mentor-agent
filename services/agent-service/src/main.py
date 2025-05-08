"""
Agent Service - Main Entry Point
This service implements the core agent orchestration for both Learning Bot and Onboarding Bot.
"""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .routes import onboarding, upload
from .db.database import Base, engine

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

app.include_router(onboarding.router)
app.include_router(upload.router)  
 
@app.on_event("startup")                
def _init_db() -> None:
    Base.metadata.create_all(bind=engine)

@app.get("/")
async def root():
    return {"message": "Genie Mentor Agent Service API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)

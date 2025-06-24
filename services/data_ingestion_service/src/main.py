import uvicorn
from fastapi import FastAPI
from .core.config import configure_app
from .api.routes import register_routes

app = FastAPI(
    title="Data Ingestion Service",
    description="Document management and RAG Ingestion pipeline for Genie Mentor Agent",
    version="1.0.0"
)

configure_app(app)        
register_routes(app)   

if __name__ == '__main__':
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8003,
        log_level="info"
    )

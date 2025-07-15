from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
import os
from dotenv import load_dotenv
load_dotenv()
from .resp_pipeline import ReSPPipeline, CHROMA_DB_PATH

router = APIRouter(prefix="/multihop_resp", tags=["MultiHop ReSP"])

groq_api_key = os.environ["GROQ_API_KEY"]
pipeline = ReSPPipeline(
    CHROMA_DB_PATH,
    groq_api_key,
    model_name="meta-llama/llama-4-scout-17b-16e-instruct",
    retrieval_k=10
)

class ReSPRequest(BaseModel):
    question: str = Field(..., description="The main question to answer.")
    max_hops: int = Field(5, description="Maximum number of hops (iterations) to run.")

class ReSPResponse(BaseModel):
    answer: str
    trace: list
    num_hops: int

@router.post("/run")
def run_multihop_resp(
    query: str = Query(..., description="The main question to answer."),
    max_hops: int = Query(5, description="Maximum number of hops (iterations) to run.")
):
    if not query or not query.strip():
        raise HTTPException(status_code=400, detail="Question must not be empty.")
    result = pipeline.run(query, max_hops=max_hops)
    return result 
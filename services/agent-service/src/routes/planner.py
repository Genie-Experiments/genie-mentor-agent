from fastapi import APIRouter, Query
from ..onboarding_agent.planner_agent import initialize_agent, send_to_agent

router = APIRouter(prefix="/planner", tags=["planner"])

@router.on_event("startup")
async def startup():
    await initialize_agent()

@router.post("/plan")
async def generate_plan(query: str = Query(...)):
    result = await send_to_agent(query)
    return {"plan": result}

from fastapi import APIRouter, Query
from ..onboarding_team.team import send_to_agent
from ..onboarding_team.message import Message

router = APIRouter(prefix="/planner", tags=["planner"])


@router.post("/plan")
async def generate_plan(query: str = Query(...)):

    result = await send_to_agent(Message(content=query))
    return {"plan": result}

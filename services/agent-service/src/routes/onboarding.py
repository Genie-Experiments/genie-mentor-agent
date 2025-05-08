from fastapi import APIRouter, Query, Body
from typing import Optional

from ..onboarding_agent.onboarding_agent import onboarding_agent
from ..db.crud import get_history, store_conversation
from ..schemas.chat import ChatHistory

router = APIRouter(prefix="/onboarding", tags=["onboarding"])

@router.post("/chat")
async def chat(
    query: str = Query(...),
    session_id: str = Query(...),
    body: Optional[ChatHistory] = Body(None),
):
    history = body.history if body else []
    response = onboarding_agent(query, history)
    store_conversation(session_id, query, response)
    return {"response": response}

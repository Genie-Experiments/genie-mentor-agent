import json
from typing import Any, Dict

from fastapi import APIRouter, Query

from ..onboarding_team.team import send_to_agent
from ..protocols.message import Message

router = APIRouter(prefix="/1", tags=["Agent-service"])


@router.post("/agent_service")
async def invoke_agent_service(
    query: str = Query(...), session_id: str = Query(...)
) -> Dict[str, Any]:

    response = await send_to_agent(Message(content=query))
    response_data = json.loads(response)
    if "trace_info" in response_data:
        response_data["trace_info"]["session_id"] = session_id

    return response_data


""" @router.post("/github_agent")
async def invoke_github_agent(
    query: str = Query(..., description="User query to send directly to GitHub agent"),
):
    response = await send_to_github_agent(Message(content=query))
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        # Fallback: wrap plain text as answer-only response
        return {"answer": response, "sources": [], "metadata": [], "error": None} """

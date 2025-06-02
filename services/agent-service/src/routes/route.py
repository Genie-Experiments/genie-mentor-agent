import json
from typing import Any, Dict
from fastapi import APIRouter, Query
from ..protocols.message import Message
from ..onboarding_team.team import send_to_agent

router = APIRouter(prefix='/1', tags=['Agent-service'])

@router.post('/agent-service')
async def invoke_agent_service(query: str = Query(...), session_id: str = Query(...)) -> Dict[str, Any]:

    response = await send_to_agent(Message(content=query))
    response_data = json.loads(response)
    if 'trace_info' in response_data:
        response_data['trace_info']['session_id'] = session_id
    
    return response_data
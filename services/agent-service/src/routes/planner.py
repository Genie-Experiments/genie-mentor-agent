# Standard library imports
import json
from typing import Any, Dict

# Third-party imports
from fastapi import APIRouter, Query

# Local application imports
from ..onboarding_team.message import Message
from ..onboarding_team.team import send_to_agent

router = APIRouter(prefix='/planner', tags=['planner'])

@router.post('/plan', response_model=Dict[str, Any])
async def generate_plan(query: str = Query(...)) -> Dict[str, Any]:
    raw_result = await send_to_agent(Message(content=query))
    
    try:
        response_data = json.loads(raw_result)
        return {
            "planner_output": response_data.get("execution_plan", {}),
            "initial_answer": {
                "content": response_data.get("initial_answer", ""),
                "confidence": response_data.get("initial_confidence", 0)
            },
            "evaluation_history": response_data.get("evaluation_history", []),
            "correction_attempts": response_data.get("correction_attempts", 0),
            "final_answer": {
                "content": response_data.get("final_answer", ""),
                "confidence": response_data.get("confidence_score", 0),
                "verification_status": response_data.get("verification_status", "unknown")
            },
            "error": response_data.get("error"),
            "raw_trace": response_data  # Include full raw data for debugging
        }
    except json.JSONDecodeError:
        return {
            "error": "Invalid response format",
            "raw_response": raw_result
        }
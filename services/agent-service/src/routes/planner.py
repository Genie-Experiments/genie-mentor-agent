
import json
import time
from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter, Query

from ..onboarding_team.message import Message
from ..onboarding_team.team import send_to_agent
from ..db import crud

router = APIRouter(prefix='/planner', tags=['planner'])

@router.post('/plan', response_model=Dict[str, Any])
async def generate_plan(
    query: str = Query(...),
    session_id: str = Query(...),
) -> Dict[str, Any]:
    start_time = time.time()
    raw = await send_to_agent(Message(content=query))
    total_time = time.time() - start_time

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        trace = {
            'timestamp': datetime.now().isoformat(),
            'error': 'Invalid JSON from agent',
            'total_time_taken': total_time
        }
        crud.store_conversation(
            session_id=session_id,
            query=query,
            response=raw,
            trace_info=trace
        )
        return {
            'error': 'Invalid JSON from agent',
            'raw': raw,
            'trace_info': trace
        }

    planner_output    = data.get('execution_plan', {})
    execution_results = data.get('execution_results', {})

    trace_info = {
        'timestamp': datetime.now().isoformat(),
        'user_input': {
            'query': query,
            'time': datetime.now().isoformat()
        },
        'planner_agent': {
            'input': query,
            'output': planner_output,
            'time_taken': total_time * 0.4,
            'timestamp': datetime.now().isoformat()
        },
        'query_agent': {
            'input': planner_output,
            'output': execution_results,
            'time_taken': total_time * 0.6,
            'timestamp': datetime.now().isoformat()
        },
        'total_time_taken': total_time
    }
    crud.store_conversation(
        session_id=session_id,
        query=query,
        response=json.dumps(execution_results),
        trace_info=trace_info
    )

    return {
        "planner_output": planner_output,
        "initial_answer": {
            "content": data.get("initial_answer", ""),
            "confidence": data.get("initial_confidence", 0)
        },
        "evaluation_history":    data.get("evaluation_history", []),
        "correction_attempts":   data.get("correction_attempts", 0),
        "final_answer": {
            "content":             data.get("final_answer", ""),
            "confidence":          data.get("confidence_score", 0),
            "verification_status": data.get("verification_status", "unknown")
        },
        "error":     data.get("error"),
        "raw_trace": data
    }

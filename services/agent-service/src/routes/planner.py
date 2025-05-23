# Standard library imports
import json
import time
from datetime import datetime
from typing import Any, Dict

# Third-party imports
from fastapi import APIRouter, Query

# Local application imports
from ..onboarding_team.message import Message
from ..onboarding_team.team import send_to_agent
from ..db import crud

router = APIRouter(prefix='/planner', tags=['planner'])

@router.post('/plan')
async def generate_plan(query: str = Query(...), session_id: str = Query(...)) -> Dict[str, Any]:
    # Start timing
    start_time = time.time()
    
    # Get the plan from planner agent
    plan_result = await send_to_agent(Message(content=query))
    
    # Calculate total time
    total_time = time.time() - start_time
    
    # Parse the result to separate planner and query outputs
    try:
        # The first part is the planner's output (query plan)
        planner_output = json.loads(plan_result)
        
        # The second part is the query agent's output (aggregated results)
        query_output = planner_output.get('execution_results', {})
        
        # Remove the execution results from planner output to avoid duplication
        if 'execution_results' in planner_output:
            del planner_output['execution_results']
        
        # Create trace information
        trace_info = {
            'timestamp': datetime.now().isoformat(),
            'user_input': {
                'query': query,
                'time': datetime.now().isoformat()
            },
            'planner_agent': {
                'input': query,
                'output': planner_output,
                'time_taken': total_time * 0.4,  # Assuming 40% of total time
                'timestamp': datetime.now().isoformat()
            },
            'query_agent': {
                'input': planner_output,
                'output': query_output,
                'time_taken': total_time * 0.6,  # Assuming 60% of total time
                'timestamp': datetime.now().isoformat()
            },
            'total_time_taken': total_time
        }
        
        # Store the conversation with trace information
        crud.store_conversation(
            session_id=session_id,
            query=query,
            response=json.dumps(query_output),
            trace_info=trace_info
        )
            
        return {
            'planner_output': planner_output,
            'query_output': query_output,
            'trace_info': trace_info
        }
    except json.JSONDecodeError:
        # If parsing fails, return the raw result for both
        error_response = {
            'planner_output': plan_result,
            'query_output': plan_result,
            'trace_info': {
                'timestamp': datetime.now().isoformat(),
                'error': 'Failed to parse response as JSON',
                'total_time_taken': total_time
            }
        }
        
        # Store the error case
        crud.store_conversation(
            session_id=session_id,
            query=query,
            response=plan_result,
            trace_info=error_response['trace_info']
        )
        
        return error_response

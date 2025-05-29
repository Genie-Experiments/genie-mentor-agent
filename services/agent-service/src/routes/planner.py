# Standard library imports
import json
import time
from datetime import datetime
from typing import Any, Dict, List, Tuple

# Third-party imports
from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse

# Local application imports
from ..onboarding_team.message import Message
from ..onboarding_team.team import send_to_agent
from ..db import crud

router = APIRouter(prefix='/planner', tags=['planner'])

@router.post('/plan')
async def generate_plan(query: str = Query(...), session_id: str = Query(...)):
    # Start timing
    start_time = time.time()
    
    # Fetch last Q&A from DB for this session
    history = crud.get_history(session_id)
    # history: List[Tuple[query, response, trace_info]]
    last_qa = history[-1] if history else None

    # Build context for the agent
    context = ""
    if last_qa:
        prev_q, prev_a, _ = last_qa
        context = f"Previous Q: {prev_q}\nPrevious A: {prev_a}\n"

    # Pass context + current query to the agent
    full_query = f"{context}Current Q: {query}"
    # ADD THIS DEBUG PRINT:
    print("\n[DEBUG] Query sent to LLM (with context):\n", full_query, "\n")
    
    async def generate():
        try:
            # Get the plan from planner agent, now with context
            plan_result = await send_to_agent(Message(content=full_query))
            
            # Calculate total time
            total_time = time.time() - start_time
            
            # Parse the result to separate planner and query outputs
            try:
                # The first part is the planner's output (query plan)
                planner_output = json.loads(plan_result)
                
                # Send planner output immediately
                yield json.dumps({
                    'planner_output': planner_output,
                    'status': 'planner_complete'
                }) + '\n'
                
                # The second part is the query agent's output (aggregated results)
                query_output = planner_output.get('execution_results', {})
                
                # Send query output
                yield json.dumps({
                    'query_output': query_output,
                    'status': 'query_complete'
                }) + '\n'
                
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
                
                # Send final response with trace info
                yield json.dumps({
                    'planner_output': planner_output,
                    'query_output': query_output,
                    'trace_info': trace_info,
                    'status': 'complete'
                }) + '\n'
                
            except json.JSONDecodeError:
                # If parsing fails, return the raw result for both
                error_response = {
                    'planner_output': plan_result,
                    'query_output': plan_result,
                    'trace_info': {
                        'timestamp': datetime.now().isoformat(),
                        'error': 'Failed to parse response as JSON',
                        'total_time_taken': total_time
                    },
                    'status': 'error'
                }
                yield json.dumps(error_response) + '\n'
                
        except Exception as e:
            error_response = {
                'error': str(e),
                'status': 'error'
            }
            yield json.dumps(error_response) + '\n'
    
    return StreamingResponse(generate(), media_type='application/x-ndjson')

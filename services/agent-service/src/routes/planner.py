from fastapi import APIRouter, Query
from ..onboarding_team.team import send_to_agent
from ..onboarding_team.message import Message
import json

router = APIRouter(prefix="/planner", tags=["planner"])


@router.post("/plan")
async def generate_plan(query: str = Query(...)):
    # Get the plan from planner agent
    plan_result = await send_to_agent(Message(content=query))
    
    # Parse the result to separate planner and query outputs
    try:
        # The first part is the planner's output (query plan)
        planner_output = json.loads(plan_result)
        
        # The second part is the query agent's output (aggregated results)
        query_output = planner_output.get("execution_results", {})
        
        # Remove the execution results from planner output to avoid duplication
        if "execution_results" in planner_output:
            del planner_output["execution_results"]
            
        return {
            "planner_output": planner_output,
            "query_output": query_output
        }
    except json.JSONDecodeError:
        # If parsing fails, return the raw result for both
        return {
            "planner_output": plan_result,
            "query_output": plan_result
        }

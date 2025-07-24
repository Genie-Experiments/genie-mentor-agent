from typing import List, Literal, Optional

from pydantic import BaseModel


class QueryComponent(BaseModel):
    id: str
    sub_query: str
    source: Literal["knowledgebase", "github", "websearch"]


class WorkflowStep(BaseModel):
    step_id: str
    query_id: str
    source: Literal["knowledgebase", "github", "websearch"]
    dependencies: List[str] = []  # List of step_ids this step depends on
    order: int  # Execution order (1, 2, etc.)


class ExecutionOrder(BaseModel):
    nodes: List[str]
    edges: List[List[str]]
    aggregation: Literal[
        "combine_and_summarize", "sequential", "parallel", "single_source"
    ]
    workflow: Optional[List[WorkflowStep]] = None  # Only present for 2+ sub-queries


class Think(BaseModel):
    query_analysis: str
    sub_query_reasoning: str
    source_selection: str
    execution_strategy: str
    workflow_reasoning: Optional[str] = None  # Only present for 2+ sub-queries


class QueryPlan(BaseModel):
    user_query: str
    query_intent: str
    data_sources: List[Literal["knowledgebase", "github", "websearch"]]
    query_components: List[QueryComponent]
    execution_order: ExecutionOrder
    think: Think


class RefinerFeedback(BaseModel):
    refinement_required: Literal["yes", "no"]
    feedback_summary: str
    feedback_reasoning: List[str]
    error: Optional[str] = None


class RefinerOutput(BaseModel):
    execution_time_ms: int
    refinement_required: Literal["yes", "no"]
    feedback_summary: str
    feedback_reasoning: List[str]
    error: Optional[str] = None

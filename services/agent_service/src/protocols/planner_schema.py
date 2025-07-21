from typing import List, Literal, Optional

from pydantic import BaseModel


class QueryComponent(BaseModel):
    id: str
    sub_query: str
    source: Literal["knowledgebase", "github", "websearch"]


class ExecutionOrder(BaseModel):
    nodes: List[str]
    edges: List[List[str]]
    aggregation: Literal[
        "combine_and_summarize", "sequential", "parallel", "single_source"
    ]


class Think(BaseModel):
    query_analysis: str
    sub_query_reasoning: str
    source_selection: str
    execution_strategy: str


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

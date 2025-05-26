from typing import List, Literal
from pydantic import BaseModel

class QueryComponent(BaseModel):
    id: str
    sub_query: str
    source: Literal["knowledgebase", "notion"]

class ExecutionOrder(BaseModel):
    nodes: List[str]
    edges: List[List[str]] 
    aggregation: Literal["combine_and_summarize", "sequential", "parallel"]

class QueryPlan(BaseModel):
    user_query: str
    query_intent: str
    data_sources: List[Literal["knowledgebase", "notion"]]
    query_components: List[QueryComponent]
    execution_order: ExecutionOrder

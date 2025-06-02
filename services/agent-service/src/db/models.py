# Standard library imports
import datetime
from typing import Optional, Dict, Any

# Third-party imports
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from pydantic import BaseModel

# Local application imports
from .database import Base

class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    query = Column(Text)
    response = Column(Text)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    trace_info = Column(JSON)  # Store the complete trace information

class Message(BaseModel):
    """Base message model for agent communication."""
    content: str
    role: Optional[str] = None

class TraceInfo(BaseModel):
    """Model for storing trace information."""
    timestamp: str
    user_input: Dict[str, Any]
    planner_agent: Dict[str, Any]
    executor_agent_agent: Dict[str, Any]
    total_time_taken: float

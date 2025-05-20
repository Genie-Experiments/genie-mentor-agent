# Standard library imports
import datetime
from typing import Optional

# Third-party imports
from sqlalchemy import Column, Integer, String, Text, DateTime
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

class Message(BaseModel):
    """Base message model for agent communication."""
    content: str
    role: Optional[str] = None

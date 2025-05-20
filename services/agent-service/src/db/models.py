# SQLAlchemy models for memory

from sqlalchemy import Column, Integer, String, Text, DateTime
from .database import Base
import datetime

class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    query = Column(Text)
    response = Column(Text)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

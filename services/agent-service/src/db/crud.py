# Standard library imports
from typing import List, Optional, Tuple

# Local application imports
from .database import SessionLocal
from .models import Conversation

def store_conversation(session_id: str, query: str, response: str) -> None:
    db = SessionLocal()
    conv = Conversation(session_id=session_id, query=query, response=response)
    db.add(conv)
    db.commit()
    db.close()

def get_history(session_id: str) -> List[Tuple[str, str]]:
    db = SessionLocal()
    history = db.query(Conversation).filter(Conversation.session_id == session_id).all()
    db.close()
    return [(h.query, h.response) for h in history]

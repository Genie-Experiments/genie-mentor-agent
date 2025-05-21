# Standard library imports
from typing import List, Optional, Tuple, Dict, Any

# Local application imports
from .database import SessionLocal
from .models import Conversation

def store_conversation(session_id: str, query: str, response: str, trace_info: Dict[str, Any]) -> None:
    """
    Store a conversation with its trace information.
    
    Args:
        session_id: The session identifier
        query: The user's query
        response: The system's response
        trace_info: Complete trace information including agent interactions and timing
    """
    db = SessionLocal()
    conv = Conversation(
        session_id=session_id,
        query=query,
        response=response,
        trace_info=trace_info
    )
    db.add(conv)
    db.commit()
    db.close()

def get_history(session_id: str) -> List[Tuple[str, str, Dict[str, Any]]]:
    """
    Get conversation history with trace information.
    
    Args:
        session_id: The session identifier
        
    Returns:
        List of tuples containing (query, response, trace_info)
    """
    db = SessionLocal()
    history = db.query(Conversation).filter(Conversation.session_id == session_id).all()
    db.close()
    return [(h.query, h.response, h.trace_info) for h in history]

def get_trace_history(session_id: str) -> List[Dict[str, Any]]:
    """
    Get only the trace history for a session.
    
    Args:
        session_id: The session identifier
        
    Returns:
        List of trace information dictionaries
    """
    db = SessionLocal()
    history = db.query(Conversation).filter(Conversation.session_id == session_id).all()
    db.close()
    return [h.trace_info for h in history if h.trace_info]

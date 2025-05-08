from .models import Conversation
from .database import SessionLocal

def store_conversation(session_id, query, response):
    db = SessionLocal()
    conv = Conversation(session_id=session_id, query=query, response=response)
    db.add(conv)
    db.commit()
    db.close()

def get_history(session_id):
    db = SessionLocal()
    history = db.query(Conversation).filter(Conversation.session_id == session_id).all()
    db.close()
    return [(h.query, h.response) for h in history]

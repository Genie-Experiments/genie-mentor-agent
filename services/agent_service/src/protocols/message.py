# Third-party imports
from pydantic import BaseModel


class Message(BaseModel):
    content: str


class RefinerOutput(BaseModel):
    refined_plan: str
    feedback: str
    original_plan: str | None = None
    changes_made: list[str] | None = None

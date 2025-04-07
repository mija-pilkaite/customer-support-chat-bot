from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime

class ChatMessage(BaseModel):
    session_id: Optional[str] = None
    message: str

class BotResponse(BaseModel):
    session_id: str
    reply: str
    done: bool = False
    
class SupportTicketOut(BaseModel):
    id: int
    created_at: datetime
    status: str
    issue_summary: str
    linked_session_id: Optional[str]
    notes: Optional[str]

class ChatSessionOut(BaseModel):
    session_id: str
    email: str
    category: str
    description: str
    urgency: str
    summary: Optional[str]
    chat_log: str
    created_at: datetime
    
class FinalizePayload(BaseModel):
    session_id: str
    email: str = ""
    category: str
    description: str
    urgency: str = ""
    chat_log: List[Dict[str, str]]
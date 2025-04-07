from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime

class ChatSession(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: str
    email: str
    category: str
    description: str
    urgency: str
    summary: Optional[str]
    chat_log: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    ticket_id: Optional[int] = Field(default=None, foreign_key="supportticket.id")

class SupportTicket(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = "open"
    issue_summary: str
    linked_session_id: Optional[str] = None
    notes: Optional[str] = None
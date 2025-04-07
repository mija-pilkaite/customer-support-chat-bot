from fastapi import APIRouter
from backend.models.schemas import ChatMessage, BotResponse
from backend.core.logic import handle_message
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from backend.services.llm_integration import stream_followup, generate_summary
from sqlmodel import select
from backend.models.database import SupportTicket, ChatSession
from backend.db import get_session
from backend.models.schemas import SupportTicketOut, ChatSessionOut
from typing import List
from backend.services.storage import save_session, create_support_ticket
from backend.models.schemas import FinalizePayload
router = APIRouter()

@router.post("/chat", response_model=BotResponse)
def chat(msg: ChatMessage):
    return handle_message(msg)

@router.post("/chat-stream")
async def chat_stream(request: Request):
    body = await request.json()
    category = body.get("category")
    description = body.get("description")
    chat_log = body.get("chat_log", [])

    return StreamingResponse(
        stream_followup(category, description, chat_log),
        media_type="text/plain"
    )
@router.get("/tickets", response_model=List[SupportTicketOut])
def list_support_tickets():
    with get_session() as db:
        tickets = db.exec(select(SupportTicket)).all()
        return tickets

@router.get("/conversations", response_model=List[ChatSessionOut])
def list_chat_sessions():
    with get_session() as db:
        sessions = db.exec(select(ChatSession)).all()
        return sessions
    
@router.post("/finalize-session")
def finalize_session(data: FinalizePayload):
    summary = generate_summary(data.dict())
    session_data = {
        "email": data.email,
        "category": data.category,
        "description": data.description,
        "urgency": data.urgency,
        "summary": summary,
        "chat_log": data.chat_log
    }
    
    # Check if any message contains the create ticket marker
    create_ticket = any("__CREATE_TICKET__" in msg.get("content", "") for msg in data.chat_log)
    print(f'[DEBUG] Create ticket: {create_ticket}')
    if create_ticket:
        
        ticket = create_support_ticket(summary, session_id=data.session_id, notes="Requested by AI flow.")
        session_data["ticket_id"] = ticket.id
    
    save_session(data.session_id, session_data)
    
    response = {"status": "ok"}
    if create_ticket:
        response["ticket_id"] = session_data["ticket_id"]
    return response
    
@router.get("/")
def root():
    return {"message": "HireHive Support Bot is running."}
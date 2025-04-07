import json
from backend.db import get_session
from backend.models.database import ChatSession
from pathlib import Path
from backend.models.database import SupportTicket
from backend.db import get_session
from typing import Optional
def save_session(session_id: str, data: dict):
    try:
        chat_log_json = json.dumps(data.get("chat_log", []))
        summary = data.get("summary")
        print(f"[DB] Saving session {session_id} with summary: {summary}")
        with get_session() as db:
            session_record = ChatSession(
                session_id=session_id,
                email=data.get("email", ""),
                category=data.get("category", ""),
                description=data.get("description", ""),
                urgency=data.get("urgency", ""),
                summary=summary,
                chat_log=chat_log_json
            )
            db.add(session_record)
            db.commit()
    except Exception as e:
        print(f"[DB ERROR] Failed to save session {session_id}: {e}")
        DATA_DIR = Path("data")
        DATA_DIR.mkdir(exist_ok=True)
        with open(DATA_DIR / f"session_{session_id}.json", "w") as f:
            json.dump(data, f, indent=2)
            
def create_support_ticket(summary: str, session_id: Optional[str] = None, notes: Optional[str] = None):
    with get_session() as db:
        ticket = SupportTicket(
            issue_summary=summary,
            linked_session_id=session_id,
            notes=notes
        )
        db.add(ticket)
        db.commit()
        db.refresh(ticket)
        print(f"[DB] Created support ticket {ticket.id} with summary: {summary}")
        return ticket
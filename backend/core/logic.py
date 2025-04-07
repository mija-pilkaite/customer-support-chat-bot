from uuid import uuid4
from backend.config import QUESTIONS, FIELDS
from backend.services.storage import save_session, create_support_ticket
from backend.models.schemas import ChatMessage, BotResponse
from backend.services.llm_integration import generate_followup, generate_summary
import re
import difflib

sessions = {}
MAX_LLM_TURNS = 8
valid_categories = {"login", "offer letter", "profile", "payroll", "other"}
valid_urgency = {"low", "medium", "high"}

def is_valid_email(email: str) -> bool:
    return re.match(r"[^@\s]+@[^@\s]+\.[a-zA-Z]{2,}", email) is not None

def get_closest_match(user_input: str, valid_options: set) -> str:
    match = difflib.get_close_matches(user_input.lower(), valid_options, n=1, cutoff=0.6)
    return match[0].title() if match else None

def handle_message(msg: ChatMessage) -> BotResponse:
    session_id = msg.session_id or str(uuid4())
    session = sessions.setdefault(session_id, {
        "step": 0,
        "data": {},
        "chat_log": [],
        "llm_turns": 0,
        "llm_mode": False,
        "referral_triggered": False
    })

    user_msg = msg.message.strip()
    session["chat_log"].append({"role": "user", "content": user_msg})
    step = session["step"]

    # Structured input phase
    if step == 0:
        if not is_valid_email(user_msg):
            return BotResponse(session_id=session_id, reply="❌ That doesn't look like a valid email. Please try again.", done=False)
        session["data"]["email"] = user_msg
        session["step"] += 1
        return BotResponse(session_id=session_id, reply=QUESTIONS[1])

    elif step == 1:
        match = get_closest_match(user_msg, valid_categories)
        if not match:
            return BotResponse(session_id=session_id, reply="🤔 Please choose a valid category: Login, Offer Letter, Profile, Payroll, or Other.", done=False)
        session["data"]["category"] = match
        session["step"] += 1
        return BotResponse(session_id=session_id, reply=f"✨ Got it! You meant: {match}\n\n{QUESTIONS[2]}")

    elif step == 2:
        session["data"]["description"] = user_msg
        session["step"] += 1
        return BotResponse(session_id=session_id, reply=QUESTIONS[3])

    elif step == 3:
        match = get_closest_match(user_msg, valid_urgency)
        if not match:
            return BotResponse(session_id=session_id, reply="⚠️ Please specify urgency as Low, Medium, or High.", done=False)
        session["data"]["urgency"] = match
        session["step"] += 1
        session["llm_mode"] = True
        return BotResponse(session_id=session_id, reply=f"✨ Noted! I've understood your urgency as: {match}\n\nThanks! Let me take a look at your issue...")

    # LLM follow-up mode
    elif session["llm_mode"]:
        session["llm_turns"] += 1

        reply = generate_followup(
            session["data"]["category"],
            session["data"]["description"],
            session["chat_log"]
        )
        session["chat_log"].append({"role": "assistant", "content": reply})  # ✅
        # Create ticket
        # In your LLM follow-up mode (handle_message):
    if "__CREATE_TICKET__" in reply:
        summary = session["data"].get("description", "No description provided")
        ticket = create_support_ticket(summary, session_id=session_id, notes="Requested by AI flow.")
        session["data"]["ticket_id"] = ticket.id
        
        # Remove markers (including any __SESSION_DONE__ if present)
        reply = reply.replace("__CREATE_TICKET__", "").replace("__SESSION_DONE__", "").strip()
        reply += f"\n\n📩 A support ticket has been created for you. Ticket ID: #{ticket.id}."
        session["chat_log"].append({"role": "assistant", "content": reply})
        save_session(session_id, session["data"])
        # Return response without finalizing the session:
        return BotResponse(session_id=session_id, reply=reply, done=False)

    # End session if explicitly requested or max turns reached
    if "__SESSION_DONE__" in reply or session["llm_turns"] >= MAX_LLM_TURNS:
        session["llm_mode"] = False
        session["step"] += 1
        session["referral_triggered"] = True
        summary = generate_summary(session["data"])
        session["data"]["summary"] = summary
        reply = reply.replace("__SESSION_DONE__", "").strip()
        reply += f"\n\n📋 Summary of your issue:\n{summary}"
        session["chat_log"].append({"role": "assistant", "content": reply})
        print(f'[DEBUG] Session {session_id} summary: {summary}')
        save_session(session_id, session["data"])
        return BotResponse(session_id=session_id, reply=reply, done=False)

        

    # Final fallback
    return BotResponse(session_id=session_id, reply="Session complete. Start a new one to report another issue.", done=True)
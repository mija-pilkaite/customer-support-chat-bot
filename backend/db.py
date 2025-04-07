from sqlmodel import SQLModel, create_engine, Session
from backend.models.database import ChatSession

DATABASE_URL = "sqlite:///./chat_sessions.db"
engine = create_engine(DATABASE_URL, echo=True)

def create_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    return Session(engine)
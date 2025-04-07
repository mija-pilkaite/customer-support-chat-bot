from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routes import router as chat_router
from dotenv import load_dotenv
import os
from backend.db import create_db

create_db()
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
app = FastAPI()


# CORS setup — allow requests from any origin (or limit to localhost if preferred)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:5500"] if using VS Code Live Server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)
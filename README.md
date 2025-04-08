# 🤖 HireHive Customer Support Chat Bot

A conversational AI support bot built with FastAPI, SQLModel, and Google Gemini to assist users with HR-related queries like login issues, payroll questions, or profile updates. It can follow up naturally, summarize issues, and even create support tickets when escalation is required.

---

## 🚀 Features

- ✨ Conversational HR support agent
- 🔁 Intelligent follow-ups using Gemini Pro (`gemini-2.0-flash-lite`)
- 📋 Support ticket creation via keyword detection (`__CREATE_TICKET__`)
- 🧠 Issue summary generation
- 🧾 Admin panel for viewing past chat sessions & tickets
- 🎙️ Voice-to-text support
- 💾 Auto-saving sessions to SQLite DB (via SQLModel)
- 🧠 Simple local knowledge base integration (`rag.knowledge_base`)
- 🎛️ Fuzzy input handling (e.g., "logn" -> "Login")
- 🧠 Context-aware session logic (won’t ask redundant questions)

---

## ⚙️ Setup Instructions

### 1. 🧪 Clone the repo
```bash
git clone git@github.com:mija-pilkaite/customer-support-chat-bot.git
cd customer-support-chat-bot
```
### 2. 🐍 Create virtual environment

```
python3 -m venv venv
source venv/bin/activate
```

### 3. 📦 Install dependencies
```
pip install -r requirements.txt
```

### 4. 🔐 Set up environment variables
Create a .env file at the root:
```
GEMINI_API_KEY=your_google_gemini_api_key
```

## ▶️ Running the App

### 1. Start the FastAPI backend:
```
uvicorn backend.main:app --reload
```
### 2. Open the chatbot frontend:
	•	Navigate to: frontend/index.html
	•	(Use a local server like VS Code Live Server or python -m http.server if needed or open the html file)


## Project Structure:

├── backend/
│   ├── main.py             # FastAPI app
│   ├── logic.py            # Main chat flow logic
│   ├── services/
│   │   ├── llm_integration.py  # Gemini follow-up logic
│   │   └── storage.py          # DB persistence
│   ├── models/
│   │   └── schemas.py      # Pydantic models
│   ├── rag/
│   │   └── knowledge_base.py   # FAQ-style context
│   └── config.py
├── frontend/
│   └── index.html          # Chat UI (with voice, streaming, buttons)
├── requirements.txt
└── README.md

### 🧠 TODO Ideas

	•	Add agent memory across sessions and session history
	•	Enable more ticket and history management for admin
    •	Tailor the model better - it sometimes repeats itself and does not provide the most accurate responses
	•	Enable the admin to upload PDF documents to better customize the responses (RAG)
    •	Better UI experience
	•	Enable more actions from the bots side besides the ticket creation
    

    


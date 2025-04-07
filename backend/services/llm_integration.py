import os
import json
import google.generativeai as genai
from backend.rag.knowledge_base import knowledge_base
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

MODEL_NAME = "gemini-2.0-flash"
model = genai.GenerativeModel(model_name=MODEL_NAME)

def generate_followup(category: str, description: str, chat_log: list) -> str:
    context = knowledge_base.get(category, "")
    prompt = f"""
You are an HR support assistant.

User’s issue category: {category}
User’s description: {description}

Known information about this category:
{context}

Chat history (do not include this in the reply nor repeat any questions you have asked):
{format_chat_log(chat_log)}

Guidelines:

- Don't always repeat the user's name, and when you do, use only the first name.
- Aim to provide 2-3 lines of advice or information.
- Do not repeat the same advice or the same questions.
- Do not ask for personal documents to be provided.
- If the issue is resolved or needs escalation to the technical team, include this marker at the end: __CREATE_TICKET__.
- You may ask **once** if the user needs anything else. Only once.
- If the user replies with a variation of "no" or "I'm done", **end the session** and include: __SESSION_DONE__.
- Do **not** ask further follow-up questions if the user already said no.
- Do not end the session on a question.
- If the user explicitly asks to create a support ticket, include: __CREATE_TICKET__.
- Only include __SESSION_DONE__ if the user clearly says the issue is resolved or they respond with something like "no", "that's all", "thanks, I'm done", etc.
Do not end the session after asking a follow-up question such as "Is there anything else I can help with?" — wait for the user’s response first.
"""
    try:
        # Start streaming
        response_chunks = model.generate_content(prompt, stream=True)

        reply = ""
        for chunk in response_chunks:
            if chunk.text:
                reply += chunk.text

        return reply.strip()

    except Exception as e:
        return f"Sorry, something went wrong: {str(e)}"

def generate_summary(data: dict) -> str:
    prompt = f"Summarize the following HR support issue:\n{json.dumps(data, indent=2)}"
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Summary not available: {str(e)}"

def format_chat_log(log: list) -> str:
    print(f"[DEBUG] format_chat_log: {log}")
    return "\n".join([entry["content"] for entry in log])

def stream_followup(category: str, description: str, chat_log: list):
    from io import StringIO
    context = knowledge_base.get(category, "")
    prompt = prompt = f"""
You are an HR support assistant.

User’s issue category: {category}
User’s description: {description}

Known information about this category:
{context}

Chat history:
{format_chat_log(chat_log)}

Guidelines:

- Don't always repeat the user's name, and when you do, use only the first name.
- Do not repeat the same advice or the same questions.
- Do not ask for personal documents to be provided.
- If the issue is resolved or needs escalation to the technical team, include this marker at the end: __SESSION_DONE__.
- You may ask **once** if the user needs anything else. Only once.
- If the user replies with a variation of "no" or "I'm done", **end the session** and include: __SESSION_DONE__.
- Do **not** ask further follow-up questions if the user already said no.
- Do not end the session on a question.
- If the user explicitly asks to create a support ticket, include: __CREATE_TICKET__.
Only include __SESSION_DONE__ if the user clearly says the issue is resolved or they respond with something like "no", "that's all", "thanks, I'm done", etc.
Do not end the session after asking a follow-up question such as "Is there anything else I can help with?" — wait for the user’s response first.
"""
    try:
        response = model.generate_content(prompt, stream=True)
        full_reply = StringIO()

        for chunk in response:
            if chunk.text:
                full_reply.write(chunk.text)

        result = full_reply.getvalue()

        # Stream cleaned reply char-by-char
        for char in result:
            yield char
    except Exception as e:
        print(f"[LLM STREAM ERROR] stream_followup: {e}")
        fallback = (
            "😓 It seems I’m a bit busy at the moment. No worries — I’ve created a support ticket based on your info. "
            "Our team will reach out to you shortly. ✅"
        )
        for char in fallback:
            yield char
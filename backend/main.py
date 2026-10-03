import json
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from groq import Groq
from pydantic import BaseModel

from embeddings import search_tools


# --------------------------------------------------
# Project paths
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

ENV_FILE = BASE_DIR / ".env"
TOOLS_FILE = BASE_DIR / "data" / "tools.json"
FRONTEND_DIR = BASE_DIR / "frontend"


# --------------------------------------------------
# Load environment variables
# --------------------------------------------------

load_dotenv(dotenv_path=ENV_FILE)

groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:
    raise RuntimeError(
        f"GROQ_API_KEY was not found.\n"
        f"Python expected your .env file at:\n{ENV_FILE}"
    )


# --------------------------------------------------
# FastAPI application
# --------------------------------------------------

app = FastAPI(title="AI Navigator")


# --------------------------------------------------
# Frontend
# --------------------------------------------------

app.mount(
    "/static",
    StaticFiles(directory=FRONTEND_DIR),
    name="static"
)


# --------------------------------------------------
# Groq client
# --------------------------------------------------

client = Groq(api_key=groq_api_key)


# --------------------------------------------------
# Request model
# --------------------------------------------------

class ChatRequest(BaseModel):
    message: str


# --------------------------------------------------
# Load AI tools
# --------------------------------------------------

with open(TOOLS_FILE, "r", encoding="utf-8") as file:
    tools = json.load(file)


# --------------------------------------------------
# Detect category
# --------------------------------------------------

def detect_category(message: str) -> str:

    message = message.lower()

    if any(word in message for word in [
        "learn",
        "study",
        "explain",
        "question",
        "python",
        "programming"
    ]):
        return "Learning"

    if any(word in message for word in [
        "write",
        "essay",
        "article",
        "content"
    ]):
        return "Writing"

    if any(word in message for word in [
        "brainstorm",
        "idea",
        "ideas"
    ]):
        return "Brainstorming"

    return "General AI Assistant"


# --------------------------------------------------
# Ask Groq
# --------------------------------------------------

def ask_groq(message: str) -> str:

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are AI Navigator, a helpful assistant "
                    "that helps beginners discover useful AI tools. "
                    "Give clear, simple and practical answers. "
                    "IMPORTANT: Return plain text only. "
                    "Do not use Markdown. "
                    "Do not use # headings. "
                    "Do not use **bold** or *italic* formatting. "
                    "Do not use tables or | characters. "
                    "Use short paragraphs and simple bullet points with -."
                )
            },
            {
                "role": "user",
                "content": f"""
The user asked:

{message}

Explain how AI tools could help this user.

Keep the answer beginner-friendly and practical.

Use plain text only.
Use short paragraphs.
Use simple bullet points with - when needed.
Do not use Markdown headings, tables, bold text, or special formatting.

Do not invent specific tools or features.
"""
            }
        ],
    )

    return response.choices[0].message.content


# --------------------------------------------------
# Home page
# --------------------------------------------------

@app.get("/")
def home():

    return FileResponse(
        FRONTEND_DIR / "index.html"
    )


# --------------------------------------------------
# Health check
# --------------------------------------------------

@app.get("/health")
def health():

    return {
        "status": "ok"
    }


# --------------------------------------------------
# Chat endpoint
# --------------------------------------------------

@app.post("/api/chat")
def chat(request: ChatRequest):

    category = detect_category(
        request.message
    )

    search_results = search_tools(
        request.message,
        top_k=3
    )

    recommendations = []

    for result in search_results:

        tool = result["tool"]

        recommendations.append({
            "name": tool["name"],
            "description": tool["description"],
            "categories": tool["categories"],
            "best_for": tool["best_for"],
            "limitations": tool["limitations"],
            "website": tool["website"]
        })

    ai_reply = ask_groq(
        request.message
    )

    return {
        "message": request.message,
        "category": category,
        "recommendations": recommendations,
        "ai_reply": ai_reply
    }


# --------------------------------------------------
# Get all AI tools
# --------------------------------------------------

@app.get("/api/tools")
def get_tools():

    return tools
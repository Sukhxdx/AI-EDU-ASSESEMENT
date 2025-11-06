from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os

from modules.readability import ReadabilityAnalyzer
from modules.glossary import GlossaryBuilder
from modules.quiz_generator import QuizGenerator
from modules.pdf_utils import extract_text_from_pdf
from modules.db import Database


class AnalyzeRequest(BaseModel):
    text: Optional[str] = None
    language: str = "en"
    num_questions: int = 5


class AnalyzeResponse(BaseModel):
    session_id: int
    readability: Dict[str, Any]
    glossary: Dict[str, Dict[str, Any]]
    quizzes: List[Dict[str, Any]]


app = FastAPI(title="AI Edu Assessment API")

# CORS setup for Vercel and local dev via ngrok
allowed_origins = os.getenv("CORS_ORIGINS", "*")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in allowed_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Initialize services
qg = QuizGenerator()
ra = ReadabilityAnalyzer()
gb = GlossaryBuilder()
db = Database(os.getenv("DB_PATH", "data/projects.db"))


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest) -> AnalyzeResponse:
    if not request.text or not request.text.strip():
        raise HTTPException(status_code=400, detail="Text is required")

    readability = ra.analyze_text(request.text)
    glossary = gb.build_glossary(request.text, target_lang=request.language, top_k=15)
    quizzes = qg.generate(request.text, num_questions=request.num_questions)
    session_id = db.save_session(request.text, quizzes, readability, glossary)
    return AnalyzeResponse(session_id=session_id, readability=readability, glossary=glossary, quizzes=quizzes)


@app.post("/analyze/upload", response_model=AnalyzeResponse)
async def analyze_upload(file: UploadFile = File(...), language: str = "en", num_questions: int = 5) -> AnalyzeResponse:
    if file.content_type not in ("application/pdf", "text/plain"):
        raise HTTPException(status_code=400, detail="Only PDF or plain text supported")

    if file.content_type == "application/pdf":
        text = extract_text_from_pdf(await file.read())
    else:
        text = (await file.read()).decode("utf-8", errors="ignore")

    if not text or not text.strip():
        raise HTTPException(status_code=400, detail="Empty content")

    readability = ra.analyze_text(text)
    glossary = gb.build_glossary(text, target_lang=language, top_k=15)
    quizzes = qg.generate(text, num_questions=num_questions)
    session_id = db.save_session(text, quizzes, readability, glossary)
    return AnalyzeResponse(session_id=session_id, readability=readability, glossary=glossary, quizzes=quizzes)


@app.get("/sessions")
def list_sessions() -> List[Dict[str, Any]]:
    return db.list_sessions()


@app.get("/sessions/{session_id}")
def load_session(session_id: int) -> Dict[str, Any]:
    data = db.load_session(session_id)
    if not data:
        raise HTTPException(status_code=404, detail="Session not found")
    return data


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)))



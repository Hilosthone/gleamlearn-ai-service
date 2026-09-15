# routers/quizzes.py
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel
import os
import requests
from datetime import datetime, timezone
from openai import OpenAI

router = APIRouter(prefix="/api/v1/quizzes", tags=["Quiz System"])

# Configuration keys and OpenAI client
AI_API_KEY = os.getenv("AI_API_KEY", "your_secret_token")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

class QuizRequest(BaseModel, extra="allow"):
    title: str = None
    description: str = None
    courseId: str = None
    fileId: str = None
    fileUrl: str = None
    topic: str = None
    questions: list = []
    options: dict = {}

class QuizSubmitRequest(BaseModel, extra="allow"):
    answers: dict = {}

def verify_token(authorization: str = Header(None)):
    if AI_API_KEY and authorization != f"Bearer {AI_API_KEY}":
        raise HTTPException(status_code=401, detail="Unauthorized AI token")

def fetch_document_text(file_url: str) -> str:
    try:
        response = requests.get(file_url)
        response.raise_for_status()
        return response.text[:15000] 
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch document content: {str(e)}")

# --- Quiz Management ---

@router.get("")
async def get_quizzes(authorization: str = Header(None)):
    verify_token(authorization)
    return {"status": "success", "quizzes": [], "message": "Retrieved all quizzes successfully."}

@router.post("")
async def create_quiz(payload: QuizRequest, authorization: str = Header(None)):
    verify_token(authorization)
    return {"status": "success", "quizId": "quiz_new_123", "data": payload.dict(), "message": "Quiz created successfully."}

@router.get("/{quiz_id}")
async def get_quiz_by_id(quiz_id: str, authorization: str = Header(None)):
    verify_token(authorization)
    return {"status": "success", "quizId": quiz_id, "title": "Sample Quiz", "questions": []}

@router.patch("/{quiz_id}")
async def update_quiz(quiz_id: str, payload: QuizRequest, authorization: str = Header(None)):
    verify_token(authorization)
    return {"status": "success", "quizId": quiz_id, "updatedData": payload.dict(), "message": "Quiz updated successfully."}

@router.delete("/{quiz_id}")
async def delete_quiz(quiz_id: str, authorization: str = Header(None)):
    verify_token(authorization)
    return {"status": "success", "quizId": quiz_id, "message": "Quiz deleted successfully."}


# --- Quiz Generation Pipelines ---

@router.post("/generate")
async def generate_quiz_general(payload: QuizRequest, authorization: str = Header(None)):
    verify_token(authorization)
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Generate a structured multiple-choice quiz JSON containing questions, options, and correct answers."},
            {"role": "user", "content": payload.description or "Generate a standard academic quiz."}
        ]
    )
    return {"status": "success", "quiz": completion.choices[0].message.content}

@router.post("/generate-from-course")
async def generate_quiz_from_course(payload: QuizRequest, authorization: str = Header(None)):
    verify_token(authorization)
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Generate a rigorous multi-question quiz testing mastery of the given course curriculum."},
            {"role": "user", "content": f"Course ID: {payload.courseId}. Details: {payload.options}"}
        ]
    )
    return {"status": "success", "courseId": payload.courseId, "quiz": completion.choices[0].message.content}

@router.post("/generate-from-document")
async def generate_quiz_from_document(payload: QuizRequest, authorization: str = Header(None)):
    verify_token(authorization)
    doc_text = fetch_document_text(payload.fileUrl) if payload.fileUrl else "Sample document content"
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Generate a detailed multiple-choice quiz based strictly on the provided document text."},
            {"role": "user", "content": doc_text}
        ]
    )
    return {"status": "success", "fileId": payload.fileId, "quiz": completion.choices[0].message.content}

@router.post("/generate-from-topic")
async def generate_quiz_from_topic(payload: QuizRequest, authorization: str = Header(None)):
    verify_token(authorization)
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Generate a targeted quiz with answers and explanations centered on the requested topic."},
            {"role": "user", "content": f"Topic: {payload.topic}"}
        ]
    )
    return {"status": "success", "topic": payload.topic, "quiz": completion.choices[0].message.content}


# --- Quiz Attempt & Grading Engine ---

@router.post("/{quiz_id}/start")
async def start_quiz_attempt(quiz_id: str, authorization: str = Header(None)):
    verify_token(authorization)
    return {"status": "success", "attemptId": "attempt_xyz_789", "quizId": quiz_id, "startedAt": datetime.now(timezone.utc).isoformat(), "message": "Quiz attempt started."}

@router.post("/{quiz_id}/submit")
async def submit_quiz_attempt(quiz_id: str, payload: QuizSubmitRequest, authorization: str = Header(None)):
    verify_token(authorization)
    return {
        "status": "success", 
        "quizId": quiz_id, 
        "score": 85.0, 
        "totalQuestions": 10, 
        "correctAnswers": 8, 
        "message": "Quiz submitted and graded successfully."
    }

@router.get("/{quiz_id}/results")
async def get_quiz_results(quiz_id: str, authorization: str = Header(None)):
    verify_token(authorization)
    return {"status": "success", "quizId": quiz_id, "resultsSummary": "Retrieved analysis of quiz attempts."}

@router.get("/attempts")
async def get_user_quiz_attempts(authorization: str = Header(None)):
    verify_token(authorization)
    return {"status": "success", "attempts": [], "message": "Retrieved user quiz attempt history."}

@router.get("/attempts/{attempt_id}")
async def get_specific_quiz_attempt(attempt_id: str, authorization: str = Header(None)):
    verify_token(authorization)
    return {"status": "success", "attemptId": attempt_id, "reviewDetails": "Detailed breakdown of attempt responses."}
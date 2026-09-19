# routers/personal_ai.py
import os
from fastapi import APIRouter, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel
from typing import Optional, Dict, Any

router = APIRouter(prefix="/api/v1", tags=["AI Personal Assistant"])

# Retrieve API key configured in Python environment
API_KEY = os.getenv("AI_API_KEY", "674930")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid or missing AI API Key")
    return api_key

# Request Payloads
class ChatPayload(BaseModel):
    message: str
    conversationId: Optional[str] = None

class ContextualPayload(BaseModel):
    input: str
    context: Optional[Dict[str, Any]] = None

class EvaluatePayload(BaseModel):
    question: str
    userAnswer: str
    correctAnswer: Optional[str] = None

# --- AI Endpoints Matching NestJS Proxies ---

@router.post("/chat")
async def ai_chat(payload: ChatPayload, api_key: str = Security(verify_api_key)):
    # Here you can plug in your OpenAI / LangChain engine using os.getenv("OPEN_AI_KEY")
    ai_response = f"GleamLearn AI Engine processed your message: '{payload.message}'"
    return {
        "status": "success",
        "conversationId": payload.conversationId,
        "message": ai_response
    }

@router.post("/ai/explain")
async def ai_explain(payload: ContextualPayload, api_key: str = Security(verify_api_key)):
    return {
        "status": "success",
        "action": "explain",
        "explanation": f"Detailed AI conceptual breakdown for: {payload.input}"
    }

@router.post("/ai/summarize")
async def ai_summarize(payload: ContextualPayload, api_key: str = Security(verify_api_key)):
    return {
        "status": "success",
        "action": "summarize",
        "summary": f"Concise AI study summary generated for the provided text."
    }

@router.post("/ai/generate-example")
async def ai_generate_example(payload: ContextualPayload, api_key: str = Security(verify_api_key)):
    return {
        "status": "success",
        "action": "generate-example",
        "example": f"Practical, real-world application example for: {payload.input}"
    }

@router.post("/ai/generate-practice")
async def ai_generate_practice(payload: ContextualPayload, api_key: str = Security(verify_api_key)):
    return {
        "status": "success",
        "action": "generate-practice",
        "practiceQuestion": f"Practice quiz question testing mastery of: {payload.input}"
    }

@router.post("/ai/evaluate-answer")
async def ai_evaluate_answer(payload: EvaluatePayload, api_key: str = Security(verify_api_key)):
    return {
        "status": "success",
        "action": "evaluate-answer",
        "score": 88,
        "feedback": "Great work! Your answer captures the core concepts accurately. Consider expanding slightly on the definitions."
    }

@router.post("/ai/explain-mistake")
async def ai_explain_mistake(payload: EvaluatePayload, api_key: str = Security(verify_api_key)):
    return {
        "status": "success",
        "action": "explain-mistake",
        "analysis": "Here is a breakdown of why your response missed the objective and how to correct your approach."
    }
# routers/ai_tutor.py
import os
from fastapi import APIRouter, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel
from typing import Optional, Dict, Any

router = APIRouter(prefix="/api/v1/ai-tutor", tags=["AI Tutor Classroom"])

API_KEY = os.getenv("AI_API_KEY", "674930")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid or missing AI API Key")
    return api_key

class TutorPayload(BaseModel):
    message: Optional[str] = None
    sessionId: Optional[str] = None
    input: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

@router.post("/message")
async def tutor_message(payload: TutorPayload, api_key: str = Security(verify_api_key)):
    msg = payload.message or "Hello student!"
    return {
        "status": "success",
        "response": f"AI Classroom Tutor: I heard '{msg}'. Let's break this down step-by-step!"
    }

@router.post("/teach")
async def ai_teach(payload: TutorPayload, api_key: str = Security(verify_api_key)):
    topic = payload.input or "General Topic"
    return {
        "status": "success",
        "action": "teach",
        "lesson": f"Comprehensive structured lesson plan generated for: {topic}"
    }

@router.post("/explain")
async def ai_tutor_explain(payload: TutorPayload, api_key: str = Security(verify_api_key)):
    concept = payload.input or "Concept"
    return {
        "status": "success",
        "action": "explain",
        "explanation": f"Clear pedagogical breakdown and analogies for: {concept}"
    }

@router.post("/generate-diagram")
async def ai_generate_diagram(payload: TutorPayload, api_key: str = Security(verify_api_key)):
    target = payload.input or "System"
    return {
        "status": "success",
        "action": "generate-diagram",
        "diagramSpec": {
            "type": "mermaid",
            "code": f"graph TD;\n    A[{target}] --> B[Core Principle];\n    B --> C[Practical Application];"
        }
    }

@router.post("/drawing-instructions")
async def ai_drawing_instructions(payload: TutorPayload, api_key: str = Security(verify_api_key)):
    target = payload.input or "Concept"
    return {
        "status": "success",
        "action": "drawing-instructions",
        "instructions": f"Step-by-step visual sketching instructions to draw and understand: {target}"
    }
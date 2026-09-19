# routers/personal_ai_companion.py
import os
from fastapi import APIRouter, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel
from typing import Optional, Dict, Any

router = APIRouter(prefix="/api/v1", tags=["Personal AI Companion"])

# Retrieve API key configured in Python environment
API_KEY = os.getenv("AI_API_KEY", "674930")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid or missing AI API Key")
    return api_key

# Companion Customization Context Payload
class CompanionContext(BaseModel):
    name: Optional[str] = "Nova"
    gender: Optional[str] = None
    personality: Optional[str] = "Friendly and Encouraging"
    teachingStyle: Optional[str] = "Socratic"
    voice: Optional[str] = None
    appearance: Optional[str] = None
    outfit: Optional[str] = None

class CompanionChatPayload(BaseModel):
    message: str
    conversationId: Optional[str] = None
    companionContext: Optional[CompanionContext] = None

class CompanionContextualPayload(BaseModel):
    input: str
    context: Optional[Dict[str, Any]] = None
    companionContext: Optional[CompanionContext] = None

# --- Companion-Driven AI Endpoints ---

@router.post("/ai-companion/chat")
async def companion_chat(payload: CompanionChatPayload, api_key: str = Security(verify_api_key)):
    # Extract companion attributes
    companion = payload.companionContext
    name = companion.name if companion else "Nova"
    style = companion.teachingStyle if companion else "Socratic"
    personality = companion.personality if companion else "Friendly"

    # Future integration point for OpenAI / LangChain prompt injection:
    # system_prompt = f"You are {name}, an AI companion with a {personality} personality and a {style} teaching style."

    ai_response = f"[{name} ({style} style)]: I received your message: '{payload.message}'"
    
    return {
        "status": "success",
        "conversationId": payload.conversationId,
        "message": ai_response,
        "activeCompanion": {
            "name": name,
            "personality": personality,
            "teachingStyle": style
        }
    }

@router.post("/ai-companion/interact")
async def companion_interact(payload: CompanionContextualPayload, api_key: str = Security(verify_api_key)):
    companion = payload.companionContext
    name = companion.name if companion else "Nova"
    
    return {
        "status": "success",
        "action": "companion-interaction",
        "response": f"Hello! I am {name}, your customized companion. Let's explore your input: '{payload.input}'"
    }
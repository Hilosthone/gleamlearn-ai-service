# # routers/personal_ai_companion.py
# import os
# from fastapi import APIRouter, HTTPException, Security, Request
# from fastapi.security.api_key import APIKeyHeader
# from pydantic import BaseModel
# from typing import Optional, Dict, Any
# from slowapi import Limiter
# from slowapi.util import get_remote_address

# # Initialize rate limiter using client IP address
# limiter = Limiter(key_func=get_remote_address)

# router = APIRouter(prefix="/api/v1", tags=["Personal AI Companion"])

# # Retrieve API key configured in Python environment
# API_KEY = os.getenv("AI_API_KEY", "674930")
# api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# def verify_api_key(api_key: str = Security(api_key_header)):
#     if api_key != API_KEY:
#         raise HTTPException(status_code=403, detail="Invalid or missing AI API Key")
#     return api_key

# # Companion Customization Context Payload
# class CompanionContext(BaseModel):
#     name: Optional[str] = "Nova"
#     gender: Optional[str] = None
#     personality: Optional[str] = "Friendly and Encouraging"
#     teachingStyle: Optional[str] = "Socratic"
#     voice: Optional[str] = None
#     appearance: Optional[str] = None
#     outfit: Optional[str] = None

# class CompanionChatPayload(BaseModel):
#     message: str
#     conversationId: Optional[str] = None
#     companionContext: Optional[CompanionContext] = None

# class CompanionContextualPayload(BaseModel):
#     input: str
#     context: Optional[Dict[str, Any]] = None
#     companionContext: Optional[CompanionContext] = None

# # --- Companion-Driven AI Endpoints ---

# @router.post("/ai-companion/chat")
# @limiter.limit("10/minute") # Protect companion chat sessions from automated flood scripts
# async def companion_chat(request: Request, payload: CompanionChatPayload, api_key: str = Security(verify_api_key)):
#     # Extract companion attributes
#     companion = payload.companionContext
#     name = companion.name if companion else "Nova"
#     style = companion.teachingStyle if companion else "Socratic"
#     personality = companion.personality if companion else "Friendly"

#     # Future integration point for OpenAI / LangChain prompt injection:
#     # system_prompt = f"You are {name}, an AI companion with a {personality} personality and a {style} teaching style."

#     ai_response = f"[{name} ({style} style)]: I received your message: '{payload.message}'"
    
#     return {
#         "status": "success",
#         "conversationId": payload.conversationId,
#         "message": ai_response,
#         "activeCompanion": {
#             "name": name,
#             "personality": personality,
#             "teachingStyle": style
#         }
#     }

# @router.post("/ai-companion/interact")
# @limiter.limit("15/minute") # Control customized interaction loop frequency
# async def companion_interact(request: Request, payload: CompanionContextualPayload, api_key: str = Security(verify_api_key)):
#     companion = payload.companionContext
#     name = companion.name if companion else "Nova"
    
#     return {
#         "status": "success",
#         "action": "companion-interaction",
#         "response": f"Hello! I am {name}, your customized companion. Let's explore your input: '{payload.input}'"
#     }




# routers/personal_ai_companion.py

from fastapi import APIRouter, HTTPException, Security, Request
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

from slowapi import Limiter
from slowapi.util import get_remote_address

from dependencies import client, NVIDIA_MODEL

limiter = Limiter(key_func=get_remote_address)

router = APIRouter(prefix="/api/v1", tags=["Personal AI Companion"])

API_KEY = __import__("os").getenv("AI_API_KEY", "674930")

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(
            status_code=403,
            detail="Invalid or missing AI API Key",
        )
    return api_key


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
    context: Optional[Dict[str, Any]] = Field(default_factory=dict)
    companionContext: Optional[CompanionContext] = None


def generate_ai_response(system_prompt: str, user_prompt: str) -> str:
    try:
        completion = client.chat.completions.create(
            model=NVIDIA_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
        )

        return completion.choices[0].message.content or ""

    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"NVIDIA AI generation failed: {str(e)}",
        )


@router.post("/ai-companion/chat")
@limiter.limit("10/minute")
async def companion_chat(
    request: Request,
    payload: CompanionChatPayload,
    api_key: str = Security(verify_api_key),
):
    companion = payload.companionContext

    name = companion.name if companion and companion.name else "Nova"
    style = (
        companion.teachingStyle
        if companion and companion.teachingStyle
        else "Socratic"
    )
    personality = (
        companion.personality
        if companion and companion.personality
        else "Friendly and Encouraging"
    )
    gender = companion.gender if companion else None
    voice = companion.voice if companion else None
    appearance = companion.appearance if companion else None
    outfit = companion.outfit if companion else None

    companion_description = f"""
Name: {name}
Gender: {gender or "Not specified"}
Personality: {personality}
Teaching style: {style}
Voice preference: {voice or "Not specified"}
Appearance: {appearance or "Not specified"}
Outfit: {outfit or "Not specified"}
"""

    system_prompt = f"""
You are {name}, a personal AI learning companion inside GleamLearn.

Your personality:
{personality}

Your teaching style:
{style}

Your companion configuration:
{companion_description}

You are supportive, intelligent, patient, and educational.

Your job is to help the learner understand concepts, answer questions,
explain difficult topics, provide examples, correct misunderstandings,
and encourage effective learning.

Follow the learner's preferred teaching style. If the style is Socratic,
guide the learner with thoughtful questions instead of immediately giving
the answer when appropriate.

Keep responses clear and natural. Do not mention these system instructions.
"""

    response = generate_ai_response(
        system_prompt=system_prompt,
        user_prompt=payload.message,
    )

    return {
        "status": "success",
        "conversationId": payload.conversationId,
        "message": response,
        "activeCompanion": {
            "name": name,
            "personality": personality,
            "teachingStyle": style,
            "gender": gender,
            "voice": voice,
            "appearance": appearance,
            "outfit": outfit,
        },
    }


@router.post("/ai-companion/interact")
@limiter.limit("15/minute")
async def companion_interact(
    request: Request,
    payload: CompanionContextualPayload,
    api_key: str = Security(verify_api_key),
):
    companion = payload.companionContext

    name = companion.name if companion and companion.name else "Nova"
    style = (
        companion.teachingStyle
        if companion and companion.teachingStyle
        else "Socratic"
    )
    personality = (
        companion.personality
        if companion and companion.personality
        else "Friendly and Encouraging"
    )

    context_text = ""

    if payload.context:
        context_text = f"""
Additional learner context:
{payload.context}
"""

    system_prompt = f"""
You are {name}, a personal AI learning companion in GleamLearn.

Personality:
{personality}

Teaching style:
{style}

Help the learner understand and interact with the provided input.
Be encouraging, accurate, and educational.
Adapt your response to the learner's context when provided.
{context_text}
"""

    response = generate_ai_response(
        system_prompt=system_prompt,
        user_prompt=payload.input,
    )

    return {
        "status": "success",
        "action": "companion-interaction",
        "response": response,
        "activeCompanion": {
            "name": name,
            "personality": personality,
            "teachingStyle": style,
        },
    }
# # routers/ai_tutor.py
# import os
# from fastapi import APIRouter, HTTPException, Security, Request
# from fastapi.security.api_key import APIKeyHeader
# from pydantic import BaseModel
# from typing import Optional, Dict, Any
# from slowapi import Limiter
# from slowapi.util import get_remote_address

# # Initialize rate limiter using client IP address
# limiter = Limiter(key_func=get_remote_address)

# router = APIRouter(prefix="/api/v1/ai-tutor", tags=["AI Tutor Classroom"])

# API_KEY = os.getenv("AI_API_KEY", "674930")
# api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# def verify_api_key(api_key: str = Security(api_key_header)):
#     if api_key != API_KEY:
#         raise HTTPException(status_code=403, detail="Invalid or missing AI API Key")
#     return api_key

# class TutorPayload(BaseModel):
#     message: Optional[str] = None
#     sessionId: Optional[str] = None
#     input: Optional[str] = None
#     context: Optional[Dict[str, Any]] = None

# @router.post("/message")
# @limiter.limit("10/minute") # Protect conversational LLM endpoint from spam
# async def tutor_message(request: Request, payload: TutorPayload, api_key: str = Security(verify_api_key)):
#     msg = payload.message or "Hello student!"
#     return {
#         "status": "success",
#         "response": f"AI Classroom Tutor: I heard '{msg}'. Let's break this down step-by-step!"
#     }

# @router.post("/teach")
# @limiter.limit("5/minute") # Restrict heavy structured lesson generation
# async def ai_teach(request: Request, payload: TutorPayload, api_key: str = Security(verify_api_key)):
#     topic = payload.input or "General Topic"
#     return {
#         "status": "success",
#         "action": "teach",
#         "lesson": f"Comprehensive structured lesson plan generated for: {topic}"
#     }

# @router.post("/explain")
# @limiter.limit("10/minute") # Control pedagogical breakdown generation requests
# async def ai_tutor_explain(request: Request, payload: TutorPayload, api_key: str = Security(verify_api_key)):
#     concept = payload.input or "Concept"
#     return {
#         "status": "success",
#         "action": "explain",
#         "explanation": f"Clear pedagogical breakdown and analogies for: {concept}"
#     }

# @router.post("/generate-diagram")
# @limiter.limit("10/minute") # Prevent diagram spec generation abuse
# async def ai_generate_diagram(request: Request, payload: TutorPayload, api_key: str = Security(verify_api_key)):
#     target = payload.input or "System"
#     return {
#         "status": "success",
#         "action": "generate-diagram",
#         "diagramSpec": {
#             "type": "mermaid",
#             "code": f"graph TD;\n    A[{target}] --> B[Core Principle];\n    B --> C[Practical Application];"
#         }
#     }

# @router.post("/drawing-instructions")
# @limiter.limit("10/minute") # Protect visual instruction generation endpoints
# async def ai_drawing_instructions(request: Request, payload: TutorPayload, api_key: str = Security(verify_api_key)):
#     target = payload.input or "Concept"
#     return {
#         "status": "success",
#         "action": "drawing-instructions",
#         "instructions": f"Step-by-step visual sketching instructions to draw and understand: {target}"
#     }

# routers/ai_tutor.py

import os

from fastapi import APIRouter, HTTPException, Security, Request
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from slowapi import Limiter
from slowapi.util import get_remote_address
from openai import OpenAI

limiter = Limiter(key_func=get_remote_address)

router = APIRouter(prefix="/api/v1/ai-tutor", tags=["AI Tutor Classroom"])

API_KEY = os.getenv("AI_API_KEY", "674930")

NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
NVIDIA_BASE_URL = os.getenv(
    "NVIDIA_BASE_URL",
    "https://integrate.api.nvidia.com/v1",
)
NVIDIA_MODEL = os.getenv(
    "NVIDIA_MODEL",
    "z-ai/glm-5-3-flash",
)

if not NVIDIA_API_KEY:
    raise RuntimeError("NVIDIA_API_KEY is not configured")

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

client = OpenAI(
    api_key=NVIDIA_API_KEY,
    base_url=NVIDIA_BASE_URL,
)


def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(
            status_code=403,
            detail="Invalid or missing AI API Key",
        )
    return api_key


class TutorPayload(BaseModel):
    message: Optional[str] = None
    sessionId: Optional[str] = None
    input: Optional[str] = None
    context: Optional[Dict[str, Any]] = Field(default_factory=dict)


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


@router.post("/message")
@limiter.limit("10/minute")
async def tutor_message(
    request: Request,
    payload: TutorPayload,
    api_key: str = Security(verify_api_key),
):
    msg = payload.message or payload.input or "Hello student!"

    context = ""
    if payload.context:
        context = f"\nAdditional context:\n{payload.context}"

    response = generate_ai_response(
        system_prompt=(
            "You are GleamLearn's AI Classroom Tutor. "
            "Teach students clearly, accurately, patiently, and step-by-step. "
            "Use simple language where appropriate. "
            "Give examples and analogies when they improve understanding. "
            "Do not unnecessarily repeat the student's question."
        ),
        user_prompt=f"{msg}{context}",
    )

    return {
        "status": "success",
        "action": "message",
        "sessionId": payload.sessionId,
        "response": response,
    }


@router.post("/teach")
@limiter.limit("5/minute")
async def ai_teach(
    request: Request,
    payload: TutorPayload,
    api_key: str = Security(verify_api_key),
):
    topic = payload.input or payload.message or "General Topic"

    context = ""
    if payload.context:
        context = f"\nAdditional context:\n{payload.context}"

    lesson = generate_ai_response(
        system_prompt=(
            "You are an expert educational tutor for GleamLearn. "
            "Generate a structured lesson that helps a student understand "
            "a topic deeply. Include learning objectives, explanation, "
            "examples, practical applications, key points, and a short "
            "knowledge check. Adapt the explanation to the supplied context."
        ),
        user_prompt=f"Teach this topic:\n{topic}{context}",
    )

    return {
        "status": "success",
        "action": "teach",
        "topic": topic,
        "lesson": lesson,
    }


@router.post("/explain")
@limiter.limit("10/minute")
async def ai_tutor_explain(
    request: Request,
    payload: TutorPayload,
    api_key: str = Security(verify_api_key),
):
    concept = payload.input or payload.message or "Concept"

    context = ""
    if payload.context:
        context = f"\nAdditional context:\n{payload.context}"

    explanation = generate_ai_response(
        system_prompt=(
            "You are GleamLearn's AI tutor. "
            "Explain concepts in a way that makes them easy to understand "
            "and remember. Start with a simple explanation, then provide "
            "a deeper explanation, examples, analogies, common mistakes, "
            "and a concise takeaway."
        ),
        user_prompt=f"Explain this concept:\n{concept}{context}",
    )

    return {
        "status": "success",
        "action": "explain",
        "concept": concept,
        "explanation": explanation,
    }


@router.post("/generate-diagram")
@limiter.limit("10/minute")
async def ai_generate_diagram(
    request: Request,
    payload: TutorPayload,
    api_key: str = Security(verify_api_key),
):
    target = payload.input or payload.message or "System"

    diagram = generate_ai_response(
        system_prompt=(
            "You generate educational Mermaid diagrams. "
            "Return only valid Mermaid diagram code. "
            "Use graph TD unless another Mermaid diagram type is clearly "
            "more appropriate. Keep labels concise and avoid unsupported "
            "syntax."
        ),
        user_prompt=f"Create an educational diagram for:\n{target}",
    )

    if diagram.startswith("```"):
        diagram = diagram.replace("```mermaid", "").replace("```", "").strip()

    return {
        "status": "success",
        "action": "generate-diagram",
        "diagramSpec": {
            "type": "mermaid",
            "code": diagram,
        },
    }


@router.post("/drawing-instructions")
@limiter.limit("10/minute")
async def ai_drawing_instructions(
    request: Request,
    payload: TutorPayload,
    api_key: str = Security(verify_api_key),
):
    target = payload.input or payload.message or "Concept"

    instructions = generate_ai_response(
        system_prompt=(
            "You are an educational visual-learning tutor. "
            "Create clear, sequential drawing instructions that help "
            "students draw and understand the requested concept. "
            "Mention important labels, shapes, relationships, and "
            "features that should appear in the final drawing."
        ),
        user_prompt=f"Create drawing instructions for:\n{target}",
    )

    return {
        "status": "success",
        "action": "drawing-instructions",
        "target": target,
        "instructions": instructions,
    }
# # routers/personal_ai.py
# import os
# from fastapi import APIRouter, HTTPException, Security, Request
# from fastapi.security.api_key import APIKeyHeader
# from pydantic import BaseModel
# from typing import Optional, Dict, Any
# from slowapi import Limiter
# from slowapi.util import get_remote_address

# # Initialize rate limiter using client IP address
# limiter = Limiter(key_func=get_remote_address)

# router = APIRouter(prefix="/api/v1", tags=["AI Personal Assistant"])

# # Retrieve API key configured in Python environment
# API_KEY = os.getenv("AI_API_KEY", "674930")
# api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# def verify_api_key(api_key: str = Security(api_key_header)):
#     if api_key != API_KEY:
#         raise HTTPException(status_code=403, detail="Invalid or missing AI API Key")
#     return api_key

# # Request Payloads
# class ChatPayload(BaseModel):
#     message: str
#     conversationId: Optional[str] = None

# class ContextualPayload(BaseModel):
#     input: str
#     context: Optional[Dict[str, Any]] = None

# class EvaluatePayload(BaseModel):
#     question: str
#     userAnswer: str
#     correctAnswer: Optional[str] = None

# # --- AI Endpoints Matching NestJS Proxies ---

# @router.post("/chat")
# @limiter.limit("15/minute") # Protect general assistant chat from spam
# async def ai_chat(request: Request, payload: ChatPayload, api_key: str = Security(verify_api_key)):
#     # Here you can plug in your OpenAI / LangChain engine using os.getenv("OPEN_AI_KEY")
#     ai_response = f"GleamLearn AI Engine processed your message: '{payload.message}'"
#     return {
#         "status": "success",
#         "conversationId": payload.conversationId,
#         "message": ai_response
#     }

# @router.post("/ai/explain")
# @limiter.limit("15/minute") # Control explanation request frequency
# async def ai_explain(request: Request, payload: ContextualPayload, api_key: str = Security(verify_api_key)):
#     return {
#         "status": "success",
#         "action": "explain",
#         "explanation": f"Detailed AI conceptual breakdown for: {payload.input}"
#     }

# @router.post("/ai/summarize")
# @limiter.limit("15/minute") # Restrict automated summary generation loops
# async def ai_summarize(request: Request, payload: ContextualPayload, api_key: str = Security(verify_api_key)):
#     return {
#         "status": "success",
#         "action": "summarize",
#         "summary": f"Concise AI study summary generated for the provided text."
#     }

# @router.post("/ai/generate-example")
# @limiter.limit("15/minute") # Prevent example generation abuse
# async def ai_generate_example(request: Request, payload: ContextualPayload, api_key: str = Security(verify_api_key)):
#     return {
#         "status": "success",
#         "action": "generate-example",
#         "example": f"Practical, real-world application example for: {payload.input}"
#     }

# @router.post("/ai/generate-practice")
# @limiter.limit("15/minute") # Control practice question synthesis frequency
# async def ai_generate_practice(request: Request, payload: ContextualPayload, api_key: str = Security(verify_api_key)):
#     return {
#         "status": "success",
#         "action": "generate-practice",
#         "practiceQuestion": f"Practice quiz question testing mastery of: {payload.input}"
#     }

# @router.post("/ai/evaluate-answer")
# @limiter.limit("20/minute") # Allow smooth student assignment evaluations
# async def ai_evaluate_answer(request: Request, payload: EvaluatePayload, api_key: str = Security(verify_api_key)):
#     return {
#         "status": "success",
#         "action": "evaluate-answer",
#         "score": 88,
#         "feedback": "Great work! Your answer captures the core concepts accurately. Consider expanding slightly on the definitions."
#     }

# @router.post("/ai/explain-mistake")
# @limiter.limit("20/minute") # Control mistake correction feedback lookups
# async def ai_explain_mistake(request: Request, payload: EvaluatePayload, api_key: str = Security(verify_api_key)):
#     return {
#         "status": "success",
#         "action": "explain-mistake",
#         "analysis": "Here is a breakdown of why your response missed the objective and how to correct your approach."
#     }





# routers/personal_ai.py

from fastapi import APIRouter, HTTPException, Security, Request
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

from slowapi import Limiter
from slowapi.util import get_remote_address

from dependencies import client, NVIDIA_MODEL

limiter = Limiter(key_func=get_remote_address)

router = APIRouter(prefix="/api/v1", tags=["AI Personal Assistant"])

API_KEY = __import__("os").getenv("AI_API_KEY", "674930")

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(
            status_code=403,
            detail="Invalid or missing AI API Key",
        )
    return api_key


class ChatPayload(BaseModel):
    message: str
    conversationId: Optional[str] = None


class ContextualPayload(BaseModel):
    input: str
    context: Optional[Dict[str, Any]] = Field(default_factory=dict)


class EvaluatePayload(BaseModel):
    question: str
    userAnswer: str
    correctAnswer: Optional[str] = None


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


@router.post("/chat")
@limiter.limit("15/minute")
async def ai_chat(
    request: Request,
    payload: ChatPayload,
    api_key: str = Security(verify_api_key),
):
    response = generate_ai_response(
        system_prompt=(
            "You are GleamLearn's AI Personal Assistant. "
            "Help students understand concepts, answer questions, "
            "solve learning problems, and study more effectively. "
            "Be accurate, clear, friendly, and concise."
        ),
        user_prompt=payload.message,
    )

    return {
        "status": "success",
        "conversationId": payload.conversationId,
        "message": response,
    }


@router.post("/ai/explain")
@limiter.limit("15/minute")
async def ai_explain(
    request: Request,
    payload: ContextualPayload,
    api_key: str = Security(verify_api_key),
):
    context = ""

    if payload.context:
        context = f"\nAdditional context:\n{payload.context}"

    response = generate_ai_response(
        system_prompt=(
            "You are an expert academic tutor. "
            "Explain the requested concept clearly and accurately. "
            "Start with a simple explanation, then provide deeper detail, "
            "examples, analogies, and important points to remember."
        ),
        user_prompt=f"{payload.input}{context}",
    )

    return {
        "status": "success",
        "action": "explain",
        "explanation": response,
    }


@router.post("/ai/summarize")
@limiter.limit("15/minute")
async def ai_summarize(
    request: Request,
    payload: ContextualPayload,
    api_key: str = Security(verify_api_key),
):
    context = ""

    if payload.context:
        context = f"\nAdditional context:\n{payload.context}"

    response = generate_ai_response(
        system_prompt=(
            "You are an expert academic summarization assistant. "
            "Summarize the provided text clearly and concisely while "
            "preserving the most important facts, concepts, arguments, "
            "and conclusions. Do not add information that is not present "
            "in the provided text."
        ),
        user_prompt=f"{payload.input}{context}",
    )

    return {
        "status": "success",
        "action": "summarize",
        "summary": response,
    }


@router.post("/ai/generate-example")
@limiter.limit("15/minute")
async def ai_generate_example(
    request: Request,
    payload: ContextualPayload,
    api_key: str = Security(verify_api_key),
):
    context = ""

    if payload.context:
        context = f"\nAdditional context:\n{payload.context}"

    response = generate_ai_response(
        system_prompt=(
            "You are an expert educational tutor. "
            "Generate practical and realistic examples that help a student "
            "understand and apply the requested concept. "
            "Use real-world scenarios where appropriate."
        ),
        user_prompt=f"Generate an example for:\n{payload.input}{context}",
    )

    return {
        "status": "success",
        "action": "generate-example",
        "example": response,
    }


@router.post("/ai/generate-practice")
@limiter.limit("15/minute")
async def ai_generate_practice(
    request: Request,
    payload: ContextualPayload,
    api_key: str = Security(verify_api_key),
):
    context = ""

    if payload.context:
        context = f"\nAdditional context:\n{payload.context}"

    response = generate_ai_response(
        system_prompt=(
            "You are an expert educational assessment generator. "
            "Create a useful practice question that tests the student's "
            "understanding of the requested topic. Include the question, "
            "expected answer, and a short explanation."
        ),
        user_prompt=f"Create a practice question for:\n{payload.input}{context}",
    )

    return {
        "status": "success",
        "action": "generate-practice",
        "practiceQuestion": response,
    }


@router.post("/ai/evaluate-answer")
@limiter.limit("20/minute")
async def ai_evaluate_answer(
    request: Request,
    payload: EvaluatePayload,
    api_key: str = Security(verify_api_key),
):
    correct_answer = payload.correctAnswer or "No reference answer provided."

    response = generate_ai_response(
        system_prompt=(
            "You are an expert academic evaluator. "
            "Evaluate the student's answer against the question and "
            "reference answer. Assess correctness, completeness, and "
            "understanding. Provide constructive feedback. "
            "Return ONLY valid JSON in this format: "
            '{"score": 0, "feedback": "string", '
            '"strengths": ["string"], "improvements": ["string"]}. '
            "Score the answer from 0 to 100."
        ),
        user_prompt=(
            f"Question:\n{payload.question}\n\n"
            f"Reference Answer:\n{correct_answer}\n\n"
            f"Student Answer:\n{payload.userAnswer}"
        ),
    )

    return {
        "status": "success",
        "action": "evaluate-answer",
        "evaluation": response,
    }


@router.post("/ai/explain-mistake")
@limiter.limit("20/minute")
async def ai_explain_mistake(
    request: Request,
    payload: EvaluatePayload,
    api_key: str = Security(verify_api_key),
):
    correct_answer = payload.correctAnswer or "No reference answer provided."

    response = generate_ai_response(
        system_prompt=(
            "You are a patient academic tutor. "
            "Analyze the student's incorrect or incomplete answer. "
            "Explain exactly what went wrong, identify the misconception "
            "or missing information, provide the correct reasoning, and "
            "show how the student can approach a similar question correctly "
            "next time."
        ),
        user_prompt=(
            f"Question:\n{payload.question}\n\n"
            f"Correct Answer:\n{correct_answer}\n\n"
            f"Student Answer:\n{payload.userAnswer}"
        ),
    )

    return {
        "status": "success",
        "action": "explain-mistake",
        "analysis": response,
    }
# # routers/recommendations.py
# import os
# from fastapi import APIRouter, HTTPException, Security, Request
# from fastapi.security.api_key import APIKeyHeader
# from typing import Optional
# from slowapi import Limiter
# from slowapi.util import get_remote_address

# # Initialize rate limiter using client IP address
# limiter = Limiter(key_func=get_remote_address)

# router = APIRouter(prefix="/api/v1/recommendations", tags=["AI Recommendations"])

# API_KEY = os.getenv("AI_API_KEY", "674930")
# api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# def verify_api_key(api_key: str = Security(api_key_header)):
#     if api_key != API_KEY:
#         raise HTTPException(status_code=403, detail="Invalid or missing AI API Key")
#     return api_key

# @router.get("")
# @limiter.limit("20/minute") # Allow smooth general recommendation dashboard lookups
# async def get_all_recommendations(request: Request, api_key: str = Security(verify_api_key)):
#     return {
#         "status": "success",
#         "recommendations": {
#             "courses": ["Advanced React Architecture", "Python FastAPI Mastery"],
#             "topics": ["Asynchronous State Management", "Database Indexing"],
#             "quizzes": ["Quiz #104: TypeScript Generics"],
#             "revision": ["Review Chapter 3: Middleware & Security"]
#         }
#     }

# @router.get("/courses")
# @limiter.limit("20/minute") # Control course recommendation polling frequency
# async def recommend_courses(request: Request, api_key: str = Security(verify_api_key)):
#     return {
#         "status": "success",
#         "data": [
#             {"id": "c1", "title": "Next.js 15 Full-Stack Engineering", "matchScore": "98%"},
#             {"id": "c2", "title": "Cross-Platform Mobile Apps with Flutter", "matchScore": "92%"}
#         ]
#     }

# @router.get("/topics")
# @limiter.limit("20/minute") # Smooth topic recommendation fetches
# async def recommend_topics(request: Request, api_key: str = Security(verify_api_key)):
#     return {
#         "status": "success",
#         "data": ["Dependency Injection in NestJS", "TypeORM Migrations", "FastAPI Pydantic Validation"]
#     }

# @router.get("/quizzes")
# @limiter.limit("20/minute") # Control quiz recommendation lookups
# async def recommend_quizzes(request: Request, api_key: str = Security(verify_api_key)):
#     return {
#         "status": "success",
#         "data": [
#             {"quizId": "q-99", "title": "NestJS Guards & Interceptors Assessment", "difficulty": "Medium"}
#         ]
#     }

# @router.get("/revision")
# @limiter.limit("20/minute") # Smooth revision target retrieval
# async def recommend_revision(request: Request, api_key: str = Security(verify_api_key)):
#     return {
#         "status": "success",
#         "data": [
#             {"focusArea": "API Security Headers & X-API-Key Verification", "reason": "Based on recent error logs and fixes."}
#         ]
#     }

# @router.get("/exams")
# @limiter.limit("20/minute") # Prevent examination recommendation abuse
# async def recommend_exams(request: Request, api_key: str = Security(verify_api_key)):
#     return {
#         "status": "success",
#         "data": [
#             {"examId": "ex-01", "title": "Full-Stack Software Engineering Mock Certification", "estimatedDuration": "45 mins"}
#         ]
#     }




# routers/recommendations.py

from fastapi import APIRouter, HTTPException, Security, Request
from fastapi.security.api_key import APIKeyHeader

from typing import Optional

from slowapi import Limiter
from slowapi.util import get_remote_address

from dependencies import client, NVIDIA_MODEL

limiter = Limiter(key_func=get_remote_address)

router = APIRouter(
    prefix="/api/v1/recommendations",
    tags=["AI Recommendations"],
)

API_KEY = __import__("os").getenv("AI_API_KEY", "674930")

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(
            status_code=403,
            detail="Invalid or missing AI API Key",
        )
    return api_key


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


@router.get("")
@limiter.limit("20/minute")
async def get_all_recommendations(
    request: Request,
    api_key: str = Security(verify_api_key),
):
    response = generate_ai_response(
        system_prompt=(
            "You are GleamLearn's recommendation engine. "
            "Generate useful educational recommendations for students. "
            "Return ONLY valid JSON with four arrays: courses, topics, "
            "quizzes, and revision. Keep recommendations practical and "
            "academically useful."
        ),
        user_prompt=(
            "Generate a balanced set of learning recommendations covering "
            "courses, topics to study, quizzes to practice, and revision areas. "
            "Use modern computer science and general academic learning topics."
        ),
    )

    return {
        "status": "success",
        "recommendations": response,
    }


@router.get("/courses")
@limiter.limit("20/minute")
async def recommend_courses(
    request: Request,
    api_key: str = Security(verify_api_key),
):
    response = generate_ai_response(
        system_prompt=(
            "You are an AI learning recommendation engine. "
            "Recommend useful courses for a student. "
            "Return ONLY valid JSON containing a 'courses' array. "
            "Each item must contain: id, title, description, matchScore, "
            "and difficulty."
        ),
        user_prompt=(
            "Recommend five valuable courses covering software engineering, "
            "web development, mobile development, backend engineering, "
            "AI engineering, and computer science."
        ),
    )

    return {
        "status": "success",
        "data": response,
    }


@router.get("/topics")
@limiter.limit("20/minute")
async def recommend_topics(
    request: Request,
    api_key: str = Security(verify_api_key),
):
    response = generate_ai_response(
        system_prompt=(
            "You are an AI academic recommendation engine. "
            "Recommend important topics that students should study next. "
            "Return ONLY valid JSON containing a 'topics' array."
        ),
        user_prompt=(
            "Generate five useful study topics covering programming, "
            "software engineering, databases, backend development, "
            "AI engineering, and computer science fundamentals."
        ),
    )

    return {
        "status": "success",
        "data": response,
    }


@router.get("/quizzes")
@limiter.limit("20/minute")
async def recommend_quizzes(
    request: Request,
    api_key: str = Security(verify_api_key),
):
    response = generate_ai_response(
        system_prompt=(
            "You are an AI assessment recommendation engine. "
            "Recommend useful quizzes for a student. "
            "Return ONLY valid JSON containing a 'quizzes' array. "
            "Each item must contain: quizId, title, difficulty, and reason."
        ),
        user_prompt=(
            "Generate five quiz recommendations covering programming, "
            "web development, backend engineering, databases, AI, "
            "and computer science."
        ),
    )

    return {
        "status": "success",
        "data": response,
    }


@router.get("/revision")
@limiter.limit("20/minute")
async def recommend_revision(
    request: Request,
    api_key: str = Security(verify_api_key),
):
    response = generate_ai_response(
        system_prompt=(
            "You are an AI study-planning assistant. "
            "Recommend areas a student should revise. "
            "Return ONLY valid JSON containing a 'revision' array. "
            "Each item must contain: focusArea, priority, reason, "
            "and suggestedAction."
        ),
        user_prompt=(
            "Generate five useful revision recommendations for a student "
            "studying computer science and software engineering."
        ),
    )

    return {
        "status": "success",
        "data": response,
    }


@router.get("/exams")
@limiter.limit("20/minute")
async def recommend_exams(
    request: Request,
    api_key: str = Security(verify_api_key),
):
    response = generate_ai_response(
        system_prompt=(
            "You are an AI examination recommendation engine. "
            "Recommend useful examinations and mock assessments for students. "
            "Return ONLY valid JSON containing an 'exams' array. "
            "Each item must contain: examId, title, description, "
            "estimatedDuration, and difficulty."
        ),
        user_prompt=(
            "Generate five useful mock examinations covering software "
            "engineering, programming, backend development, databases, "
            "AI engineering, and computer science."
        ),
    )

    return {
        "status": "success",
        "data": response,
    }
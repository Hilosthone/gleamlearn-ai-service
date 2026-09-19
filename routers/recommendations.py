# routers/recommendations.py
import os
from fastapi import APIRouter, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from typing import Optional

router = APIRouter(prefix="/api/v1/recommendations", tags=["AI Recommendations"])

API_KEY = os.getenv("AI_API_KEY", "674930")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid or missing AI API Key")
    return api_key

@router.get("")
async def get_all_recommendations(api_key: str = Security(verify_api_key)):
    return {
        "status": "success",
        "recommendations": {
            "courses": ["Advanced React Architecture", "Python FastAPI Mastery"],
            "topics": ["Asynchronous State Management", "Database Indexing"],
            "quizzes": ["Quiz #104: TypeScript Generics"],
            "revision": ["Review Chapter 3: Middleware & Security"]
        }
    }

@router.get("/courses")
async def recommend_courses(api_key: str = Security(verify_api_key)):
    return {
        "status": "success",
        "data": [
            {"id": "c1", "title": "Next.js 15 Full-Stack Engineering", "matchScore": "98%"},
            {"id": "c2", "title": "Cross-Platform Mobile Apps with Flutter", "matchScore": "92%"}
        ]
    }

@router.get("/topics")
async def recommend_topics(api_key: str = Security(verify_api_key)):
    return {
        "status": "success",
        "data": ["Dependency Injection in NestJS", "TypeORM Migrations", "FastAPI Pydantic Validation"]
    }

@router.get("/quizzes")
async def recommend_quizzes(api_key: str = Security(verify_api_key)):
    return {
        "status": "success",
        "data": [
            {"quizId": "q-99", "title": "NestJS Guards & Interceptors Assessment", "difficulty": "Medium"}
        ]
    }

@router.get("/revision")
async def recommend_revision(api_key: str = Security(verify_api_key)):
    return {
        "status": "success",
        "data": [
            {"focusArea": "API Security Headers & X-API-Key Verification", "reason": "Based on recent error logs and fixes."}
        ]
    }

@router.get("/exams")
async def recommend_exams(api_key: str = Security(verify_api_key)):
    return {
        "status": "success",
        "data": [
            {"examId": "ex-01", "title": "Full-Stack Software Engineering Mock Certification", "estimatedDuration": "45 mins"}
        ]
    }
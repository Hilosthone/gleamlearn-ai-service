# # main.py
# import os
# from dotenv import load_dotenv

# load_dotenv()

# from fastapi import FastAPI, Request
# from datetime import datetime, timezone
# from slowapi import Limiter, _rate_limit_exceeded_handler
# from slowapi.util import get_remote_address
# from slowapi.errors import RateLimitExceeded
# from routers import documents, quizzes, tests, exams, personal_ai, personal_ai_companion, ai_tutor, voice_ai, recommendations, youtube

# # Initialize rate limiter using client IP address
# limiter = Limiter(key_func=get_remote_address)

# app = FastAPI(
#     title="GleamLearn AI Microservice",
#     description="High-performance backend microservice powering automated study pipelines, quizzes, and interactive live classes.",
#     version="1.0.0"
# )

# # Attach limiter to app state and register error handler
# app.state.limiter = limiter
# app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# # Include modular routers
# app.include_router(documents.router)
# app.include_router(quizzes.router)
# app.include_router(tests.router)
# app.include_router(exams.router)
# app.include_router(personal_ai.router)
# app.include_router(personal_ai_companion.router)
# app.include_router(ai_tutor.router)
# app.include_router(voice_ai.router)
# app.include_router(recommendations.router)
# app.include_router(youtube.router)

# @app.get("/")
# @limiter.limit("30/minute") # Protect landing stats from scrapers
# def read_root(request: Request):
#     """
#     Executive landing endpoint providing product metadata, system status, 
#     developer credentials, and links to interactive API documentation.
#     """
#     return {
#         "product": "GleamLearn AI Microservice",
#         "version": "1.0.0",
#         "status": "operational",
#         "description": "Enterprise-grade AI backend engine driving automated study guides, multi-module course curricula, flashcards, and real-time interactive AI masterclasses.",
#         "developer": "Hilosthone Sulyman",
#         "documentation": {
#             "swaggerUI": "/docs",
#             "redoc": "/redoc"
#         },
#         "serverTime": datetime.now(timezone.utc).isoformat(),
#         "coreCapabilities": [
#             "Deep Document Analysis",
#             "Automated Summary & Notes Generation",
#             "Dynamic Flashcard & Quiz Compilation",
#             "Rigorous Test & Exam Synthesis",
#             "Interactive Live Class Timeline & Narration Sync"
#         ]
#     }



from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, Request
from datetime import datetime, timezone

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from routers import (
    documents,
    quizzes,
    tests,
    exams,
    personal_ai,
    personal_ai_companion,
    ai_tutor,
    voice_ai,
    recommendations,
    youtube,
)

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="GleamLearn AI Microservice",
    description="High-performance backend microservice powering automated study pipelines, quizzes, and interactive live classes.",
    version="1.0.0",
)

app.state.limiter = limiter
app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler,
)

app.include_router(documents.router)
app.include_router(quizzes.router)
app.include_router(tests.router)
app.include_router(exams.router)
app.include_router(personal_ai.router)
app.include_router(personal_ai_companion.router)
app.include_router(ai_tutor.router)
app.include_router(voice_ai.router)
app.include_router(recommendations.router)
app.include_router(youtube.router)


@app.get("/")
@limiter.limit("30/minute")
def read_root(request: Request):
    return {
        "product": "GleamLearn AI Microservice",
        "version": "1.0.0",
        "status": "operational",
        "description": "Enterprise-grade AI backend engine driving automated study guides, multi-module course curricula, flashcards, and real-time interactive AI masterclasses.",
        "developer": "Hilosthone Sulyman",
        "documentation": {
            "swaggerUI": "/docs",
            "redoc": "/redoc",
        },
        "serverTime": datetime.now(timezone.utc).isoformat(),
        "coreCapabilities": [
            "Deep Document Analysis",
            "Automated Summary & Notes Generation",
            "Dynamic Flashcard & Quiz Compilation",
            "Rigorous Test & Exam Synthesis",
            "Interactive Live Class Timeline & Narration Sync",
        ],
    }
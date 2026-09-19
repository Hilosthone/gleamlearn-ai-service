
# # main.py
# from fastapi import FastAPI
# from datetime import datetime, timezone
# from routers import documents, quizzes, tests
# from routers import exams

# # Initialize FastAPI application instance with formal metadata
# app = FastAPI(
#     title="GleamLearn AI Microservice",
#     description="High-performance backend microservice powering automated study pipelines, quizzes, and interactive live classes.",
#     version="1.0.0"
# )

# # Include modular routers
# app.include_router(documents.router)
# app.include_router(quizzes.router)
# app.include_router(tests.router)
# app.include_router(exams.router)

# @app.get("/")
# def read_root():
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




# main.py
import os
from dotenv import load_dotenv

# Load environment variables from the local .env file
load_dotenv()

from fastapi import FastAPI
from datetime import datetime, timezone
from routers import documents, quizzes, tests, exams, personal_ai, personal_ai_companion, ai_tutor, voice_ai, recommendations

# Initialize FastAPI application instance with formal metadata
app = FastAPI(
    title="GleamLearn AI Microservice",
    description="High-performance backend microservice powering automated study pipelines, quizzes, and interactive live classes.",
    version="1.0.0"
)

# Include modular routers
app.include_router(documents.router)
app.include_router(quizzes.router)
app.include_router(tests.router)
app.include_router(exams.router)
app.include_router(personal_ai.router)
app.include_router(personal_ai_companion.router)
app.include_router(ai_tutor.router)
app.include_router(voice_ai.router)
app.include_router(recommendations.router)

@app.get("/")
def read_root():
    """
    Executive landing endpoint providing product metadata, system status, 
    developer credentials, and links to interactive API documentation.
    """
    return {
        "product": "GleamLearn AI Microservice",
        "version": "1.0.0",
        "status": "operational",
        "description": "Enterprise-grade AI backend engine driving automated study guides, multi-module course curricula, flashcards, and real-time interactive AI masterclasses.",
        "developer": "Hilosthone Sulyman",
        "documentation": {
            "swaggerUI": "/docs",
            "redoc": "/redoc"
        },
        "serverTime": datetime.now(timezone.utc).isoformat(),
        "coreCapabilities": [
            "Deep Document Analysis",
            "Automated Summary & Notes Generation",
            "Dynamic Flashcard & Quiz Compilation",
            "Rigorous Test & Exam Synthesis",
            "Interactive Live Class Timeline & Narration Sync"
        ]
    }
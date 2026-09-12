# from fastapi import FastAPI, Header, HTTPException
# from pydantic import BaseModel
# import os

# app = FastAPI(title="GleamLearn AI Microservice")
# AI_API_KEY = os.getenv("AI_API_KEY", "your_secret_token")

# class AiRequest(BaseModel):
#     fileId: str
#     fileUrl: str
#     options: dict = {}

# def verify_token(authorization: str = Header(None)):
#     if AI_API_KEY and authorization != f"Bearer {AI_API_KEY}":
#         raise HTTPException(status_code=401, detail="Unauthorized AI token")

# @app.post("/api/v1/analyze")
# async def analyze_document(payload: AiRequest, authorization: str = Header(None)):
#     verify_token(authorization)
#     # Put your PDF parsing / LLM logic here!
#     return {
#         "status": "success",
#         "fileId": payload.fileId,
#         "summary": "Deep document analysis completed successfully by FastAPI."
#     }





from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
import os

# Initialize FastAPI application with metadata
app = FastAPI(title="GleamLearn AI Microservice")

# Retrieve the shared secret API key from environment variables (defaults to a fallback for local testing)
AI_API_KEY = os.getenv("AI_API_KEY", "your_secret_token")

# Define the expected request body schema using Pydantic for validation
class AiRequest(BaseModel):
    fileId: str
    fileUrl: str
    options: dict = {}

# Security helper function to validate the incoming Bearer token from the NestJS backend
def verify_token(authorization: str = Header(None)):
    if AI_API_KEY and authorization != f"Bearer {AI_API_KEY}":
        raise HTTPException(status_code=401, detail="Unauthorized AI token")

@app.get("/")
def read_root():
    return {"status": "success", "message": "GleamLearn AI Microservice is live!"}

@app.post("/api/v1/analyze")
async def analyze_document(payload: AiRequest, authorization: str = Header(None)):
    verify_token(authorization)
    # TODO: Implement your core PDF download and LLM analysis logic here
    return {
        "status": "success",
        "fileId": payload.fileId,
        "summary": "Deep document analysis completed successfully."
    }

@app.post("/api/v1/generate-notes")
async def generate_notes(payload: AiRequest, authorization: str = Header(None)):
    verify_token(authorization)
    return {
        "status": "success",
        "fileId": payload.fileId,
        "notes": "Generated comprehensive study notes based on the document."
    }

@app.post("/api/v1/generate-summary")
async def generate_summary(payload: AiRequest, authorization: str = Header(None)):
    verify_token(authorization)
    return {
        "status": "success",
        "fileId": payload.fileId,
        "summary": "Concise executive summary generated."
    }

@app.post("/api/v1/generate-flashcards")
async def generate_flashcards(payload: AiRequest, authorization: str = Header(None)):
    verify_token(authorization)
    return {
        "status": "success",
        "fileId": payload.fileId,
        "flashcards": [
            {"front": "Sample Concept", "back": "Sample Definition"}
        ]
    }

@app.post("/api/v1/generate-quiz")
async def generate_quiz(payload: AiRequest, authorization: str = Header(None)):
    verify_token(authorization)
    return {
        "status": "success",
        "fileId": payload.fileId,
        "quiz": [
            {
                "question": "Sample question text?",
                "options": ["A", "B", "C", "D"],
                "answer": "A"
            }
        ]
    }
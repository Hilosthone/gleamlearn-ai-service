# from fastapi import FastAPI, Header, HTTPException, Response
# from pydantic import BaseModel
# import os
# import requests
# from openai import OpenAI

# app = FastAPI(title="GleamLearn AI Microservice - Production")

# AI_API_KEY = os.getenv("AI_API_KEY", "your_secret_token")
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# # Initialize the OpenAI client securely using the environment variable
# client = OpenAI(api_key=OPENAI_API_KEY)

# class AiRequest(BaseModel, extra="allow"):
#     fileId: str
#     fileUrl: str
#     options: dict = {}

# def verify_token(authorization: str = Header(None)):
#     """Validates the internal shared bearer token sent by the NestJS backend gateway."""
#     if AI_API_KEY and authorization != f"Bearer {AI_API_KEY}":
#         raise HTTPException(status_code=401, detail="Unauthorized AI token")

# def fetch_document_text(file_url: str) -> str:
#     """Downloads the raw study document from cloud storage (Supabase) and extracts text for the LLM."""
#     try:
#         response = requests.get(file_url)
#         response.raise_for_status()
#         return response.text[:15000] 
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=f"Failed to fetch document content: {str(e)}")

# @app.get("/")
# def read_root():
#     return {"status": "success", "message": "GleamLearn AI Production Microservice is live!"}

# # ==========================================
# # CORE DOCUMENT ANALYSIS & STUDY GENERATION
# # ==========================================

# @app.post("/api/v1/ai/documents/{file_id}/analyze")
# @app.post("/api/v1/analyze")
# async def analyze_document(payload: AiRequest, file_id: str = None, authorization: str = Header(None)):
#     verify_token(authorization)
#     doc_text = fetch_document_text(payload.fileUrl)
    
#     completion = client.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=[
#             {"role": "system", "content": "You are an expert academic AI tutor for GleamLearn. Provide a deep, structured analysis of the document."},
#             {"role": "user", "content": doc_text}
#         ]
#     )
#     target_id = file_id or payload.fileId
#     return {"status": "success", "fileId": target_id, "analysis": completion.choices[0].message.content}

# @app.get("/api/v1/ai/documents/{file_id}/analysis")
# async def get_document_analysis(file_id: str, authorization: str = Header(None)):
#     verify_token(authorization)
#     # In production, this fetches stored analysis results from database cache.
#     return {"status": "success", "fileId": file_id, "message": "Retrieved cached document analysis successfully."}

# @app.post("/api/v1/ai/documents/{file_id}/generate-notes")
# @app.post("/api/v1/generate-notes")
# async def generate_notes(payload: AiRequest, file_id: str = None, authorization: str = Header(None)):
#     verify_token(authorization)
#     doc_text = fetch_document_text(payload.fileUrl)
    
#     completion = client.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=[
#             {"role": "system", "content": "Generate comprehensive, structured study notes with key takeaways from the provided text."},
#             {"role": "user", "content": doc_text}
#         ]
#     )
#     target_id = file_id or payload.fileId
#     return {"status": "success", "fileId": target_id, "notes": completion.choices[0].message.content}

# @app.post("/api/v1/ai/documents/{file_id}/generate-summary")
# @app.post("/api/v1/generate-summary")
# async def generate_summary(payload: AiRequest, file_id: str = None, authorization: str = Header(None)):
#     verify_token(authorization)
#     doc_text = fetch_document_text(payload.fileUrl)
    
#     completion = client.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=[
#             {"role": "system", "content": "Provide a concise executive summary of the document."},
#             {"role": "user", "content": doc_text}
#         ]
#     )
#     target_id = file_id or payload.fileId
#     return {"status": "success", "fileId": target_id, "summary": completion.choices[0].message.content}

# @app.post("/api/v1/ai/documents/{file_id}/generate-flashcards")
# @app.post("/api/v1/generate-flashcards")
# async def generate_flashcards(payload: AiRequest, file_id: str = None, authorization: str = Header(None)):
#     verify_token(authorization)
#     doc_text = fetch_document_text(payload.fileUrl)
    
#     completion = client.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=[
#             {"role": "system", "content": "Generate flashcards from the text. Return a clean JSON array format where each object has 'front' and 'back' keys."},
#             {"role": "user", "content": doc_text}
#         ]
#     )
#     target_id = file_id or payload.fileId
#     return {"status": "success", "fileId": target_id, "flashcards": completion.choices[0].message.content}

# @app.post("/api/v1/ai/documents/{file_id}/generate-questions")
# @app.post("/api/v1/generate-questions")
# async def generate_questions(payload: AiRequest, file_id: str = None, authorization: str = Header(None)):
#     verify_token(authorization)
#     doc_text = fetch_document_text(payload.fileUrl)
    
#     completion = client.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=[
#             {"role": "system", "content": "Generate important study questions based on the document text."},
#             {"role": "user", "content": doc_text}
#         ]
#     )
#     target_id = file_id or payload.fileId
#     return {"status": "success", "fileId": target_id, "questions": completion.choices[0].message.content}

# @app.post("/api/v1/ai/documents/{file_id}/generate-quiz")
# @app.post("/api/v1/generate-quiz")
# async def generate_quiz(payload: AiRequest, file_id: str = None, authorization: str = Header(None)):
#     verify_token(authorization)
#     doc_text = fetch_document_text(payload.fileUrl)
    
#     completion = client.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=[
#             {"role": "system", "content": "Generate a multiple-choice quiz based on the document text with options and the correct answer indicated."},
#             {"role": "user", "content": doc_text}
#         ]
#     )
#     target_id = file_id or payload.fileId
#     return {"status": "success", "fileId": target_id, "quiz": completion.choices[0].message.content}

# @app.post("/api/v1/ai/documents/{file_id}/generate-test")
# @app.post("/api/v1/generate-test")
# async def generate_test(payload: AiRequest, file_id: str = None, authorization: str = Header(None)):
#     verify_token(authorization)
#     doc_text = fetch_document_text(payload.fileUrl)
    
#     completion = client.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=[
#             {"role": "system", "content": "Generate a comprehensive test based on the document."},
#             {"role": "user", "content": doc_text}
#         ]
#     )
#     target_id = file_id or payload.fileId
#     return {"status": "success", "fileId": target_id, "test": completion.choices[0].message.content}

# @app.post("/api/v1/ai/documents/{file_id}/generate-exam")
# @app.post("/api/v1/generate-exam")
# async def generate_exam(payload: AiRequest, file_id: str = None, authorization: str = Header(None)):
#     verify_token(authorization)
#     doc_text = fetch_document_text(payload.fileUrl)
    
#     completion = client.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=[
#             {"role": "system", "content": "Generate a full-length rigorous exam based on the document content."},
#             {"role": "user", "content": doc_text}
#         ]
#     )
#     target_id = file_id or payload.fileId
#     return {"status": "success", "fileId": target_id, "exam": completion.choices[0].message.content}

# @app.post("/api/v1/ai/documents/{file_id}/create-course")
# @app.post("/api/v1/create-course")
# async def create_course(payload: AiRequest, file_id: str = None, authorization: str = Header(None)):
#     verify_token(authorization)
#     doc_text = fetch_document_text(payload.fileUrl)
    
#     completion = client.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=[
#             {"role": "system", "content": "Structure a multi-module course curriculum out of this document."},
#             {"role": "user", "content": doc_text}
#         ]
#     )
#     target_id = file_id or payload.fileId
#     return {"status": "success", "fileId": target_id, "course": completion.choices[0].message.content}

# @app.get("/api/v1/ai/documents/{file_id}/generated-content")
# async def get_generated_content(file_id: str, authorization: str = Header(None)):
#     verify_token(authorization)
#     return {"status": "success", "fileId": file_id, "message": "Retregated all generated assets for this document."}


# # ==========================================
# # INTERACTIVE LIVE AI CLASS & VISUALIZATION
# # ==========================================

# @app.post("/api/v1/ai/documents/{file_id}/generate-live-class")
# async def generate_live_class(payload: AiRequest, file_id: str, authorization: str = Header(None)):
#     """
#     Transforms the document text into a structured timeline script for the Interactive Live AI Class.
#     Returns synchronized scene metadata including narration, visual canvas actions (zoom/pan), and captions.
#     """
#     verify_token(authorization)
#     doc_text = fetch_document_text(payload.fileUrl)
    
#     completion = client.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=[
#             {
#                 "role": "system", 
#                 "content": "You are an expert AI instructor. Convert the provided document into a structured live class timeline JSON array. Each object must contain: 'timestamp', 'speaker_narration', 'visual_cue' (e.g., zoom in on key equation, highlight diagram), and 'caption_text'."
#             },
#             {"role": "user", "content": doc_text}
#         ]
#     )
#     return {
#         "status": "success", 
#         "fileId": file_id, 
#         "liveClassSession": {
#             "title": "Interactive AI Masterclass",
#             "playbackControls": ["play", "pause", "fast_forward", "zoom_in", "zoom_out", "captions"],
#             "scriptTimeline": completion.choices[0].message.content
#         }
#     }

# @app.get("/api/v1/ai/documents/{file_id}/live-class-stream")
# async def get_live_class_stream(file_id: str, authorization: str = Header(None)):
#     """
#     Serves streaming session metadata and playback sync state for the frontend video/canvas player.
#     """
#     verify_token(authorization)
#     return {
#         "status": "success",
#         "fileId": file_id,
#         "streamStatus": "ready",
#         "message": "Live class streaming metadata active. Supports playback controls, zoom states, and real-time caption sync."
#     }

# @app.post("/api/v1/ai/documents/{file_id}/export-pdf")
# async def export_pdf(payload: AiRequest, file_id: str, authorization: str = Header(None)):
#     """
#     Packages generated course notes, summaries, or live lesson transcripts into a downloadable PDF format.
#     """
#     verify_token(authorization)
#     # In production, this renders a PDF buffer using ReportLab or FPDF and returns a downloadable file URL or stream.
#     return {
#         "status": "success",
#         "fileId": file_id,
#         "downloadUrl": f"https://storage.supabase.co/storage/v1/object/public/gleamlearn-exports/{file_id}-export.pdf",
#         "message": "Document successfully compiled and ready for PDF download."
#     }




# main.py
from fastapi import FastAPI
from datetime import datetime, timezone
from routers import documents, quizzes
from routers import documents, quizzes, tests

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
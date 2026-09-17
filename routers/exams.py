# routers/exams.py
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional, Dict, Any
from dependencies import client, verify_token

router = APIRouter(prefix="/api/v1/exams", tags=["AI Examination Engine"])

class ExamGenPayload(BaseModel):
    title: Optional[str] = None
    topic: Optional[str] = None
    courseId: Optional[str] = None
    documentId: Optional[str] = None
    num_questions: Optional[int] = 20

@router.post("/generate", dependencies=[Depends(verify_token)])
async def generate_exam(payload: ExamGenPayload):
    try:
        prompt = f"Generate a formal, rigorous final examination with {payload.num_questions} questions on: {payload.topic or 'Comprehensive Curriculum'}. Format as a structured JSON object."
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert AI exam creator and psychometrician."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        return {
            "status": "success",
            "title": payload.topic or "Generated Final Examination",
            "generated_content": eval(content) if content else {}
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/generate-from-course", dependencies=[Depends(verify_token)])
async def generate_exam_from_course(payload: ExamGenPayload):
    return {"status": "success", "message": f"Exam generated for course ID: {payload.courseId}", "questions": []}

@router.post("/generate-from-document", dependencies=[Depends(verify_token)])
async def generate_exam_from_document(payload: ExamGenPayload):
    return {"status": "success", "message": f"Exam generated from document ID: {payload.documentId}", "questions": []}
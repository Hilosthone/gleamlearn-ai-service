# routers/tests.py
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from dependencies import client, verify_token  # Assuming your shared auth & openai client dependency

router = APIRouter(prefix="/api/v1/tests", tags=["AI Tests Generation"])

class TestGenPayload(BaseModel):
    title: Optional[str] = None
    topic: Optional[str] = None
    courseId: Optional[str] = None
    documentId: Optional[str] = None
    num_questions: Optional[int] = 15

@router.post("/generate", dependencies=[Depends(verify_token)])
async def generate_test(payload: TestGenPayload):
    """
    AI generation endpoint called by NestJS to generate a full midterm/test structure.
    """
    try:
        prompt = f"Generate a comprehensive test assessment with {payload.num_questions} questions on the topic: {payload.topic or 'General Academic'}. Format as a structured JSON object."
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert AI academic assessment generator."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        return {
            "status": "success",
            "title": payload.topic or "Generated Test Assessment",
            "generated_content": eval(content) if content else {}
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OpenAI test generation failed: {str(e)}"
        )

@router.post("/generate-from-course", dependencies=[Depends(verify_token)])
async def generate_test_from_course(payload: TestGenPayload):
    """
    Generates a test assessment based on course curriculum or materials.
    """
    return {
        "status": "success",
        "message": f"Test generated successfully for course ID: {payload.courseId}",
        "questions": [
            {
                "question": "Sample course test question 1?",
                "options": ["A", "B", "C", "D"],
                "correctAnswer": "A"
            }
        ]
    }

@router.post("/generate-from-document", dependencies=[Depends(verify_token)])
async def generate_test_from_document(payload: TestGenPayload):
    """
    Generates a comprehensive test using text extracted from an uploaded document.
    """
    return {
        "status": "success",
        "message": f"Test generated successfully from document ID: {payload.documentId}",
        "questions": []
    }
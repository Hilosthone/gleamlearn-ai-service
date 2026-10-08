# # routers/exams.py
# from fastapi import APIRouter, Depends, HTTPException, status, Request
# from pydantic import BaseModel
# from typing import Optional, Dict, Any
# from slowapi import Limiter
# from slowapi.util import get_remote_address
# from dependencies import client, verify_token

# # Initialize rate limiter using client IP address
# limiter = Limiter(key_func=get_remote_address)

# router = APIRouter(prefix="/api/v1/exams", tags=["AI Examination Engine"])

# class ExamGenPayload(BaseModel):
#     title: Optional[str] = None
#     topic: Optional[str] = None
#     courseId: Optional[str] = None
#     documentId: Optional[str] = None
#     num_questions: Optional[int] = 20

# @router.post("/generate", dependencies=[Depends(verify_token)])
# @limiter.limit("3/minute") # Strict rate limit for comprehensive final exam synthesis
# async def generate_exam(request: Request, payload: ExamGenPayload):
#     try:
#         prompt = f"Generate a formal, rigorous final examination with {payload.num_questions} questions on: {payload.topic or 'Comprehensive Curriculum'}. Format as a structured JSON object."
        
#         response = client.chat.completions.create(
#             model="gpt-4o-mini",
#             messages=[
#                 {"role": "system", "content": "You are an expert AI exam creator and psychometrician."},
#                 {"role": "user", "content": prompt}
#             ],
#             response_format={"type": "json_object"}
#         )
        
#         content = response.choices[0].message.content
#         return {
#             "status": "success",
#             "title": payload.topic or "Generated Final Examination",
#             "generated_content": eval(content) if content else {}
#         }
#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# @router.post("/generate-from-course", dependencies=[Depends(verify_token)])
# @limiter.limit("5/minute") # Restrict course-based exam generation loops
# async def generate_exam_from_course(request: Request, payload: ExamGenPayload):
#     return {"status": "success", "message": f"Exam generated for course ID: {payload.courseId}", "questions": []}

# @router.post("/generate-from-document", dependencies=[Depends(verify_token)])
# @limiter.limit("5/minute") # Control document-based exam generation frequency
# async def generate_exam_from_document(request: Request, payload: ExamGenPayload):
#     return {"status": "success", "message": f"Exam generated from document ID: {payload.documentId}", "questions": []}



# routers/exams.py

import json

from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel, Field
from typing import Optional

from slowapi import Limiter
from slowapi.util import get_remote_address

from dependencies import client, NVIDIA_MODEL, verify_token, fetch_document_text

limiter = Limiter(key_func=get_remote_address)

router = APIRouter(prefix="/api/v1/exams", tags=["AI Examination Engine"])


class ExamGenPayload(BaseModel):
    title: Optional[str] = None
    topic: Optional[str] = None
    courseId: Optional[str] = None
    documentId: Optional[str] = None
    fileId: Optional[str] = None
    fileUrl: Optional[str] = None
    num_questions: Optional[int] = Field(default=20, ge=1, le=100)


def generate_exam_with_ai(prompt: str):
    try:
        response = client.chat.completions.create(
            model=NVIDIA_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert AI examination creator and "
                        "psychometrician for GleamLearn. Create rigorous, "
                        "academically appropriate examinations that test "
                        "recall, understanding, application, analysis, "
                        "and critical thinking."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )

        content = response.choices[0].message.content

        if not content:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="NVIDIA AI returned an empty response.",
            )

        return content

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"NVIDIA AI generation failed: {str(e)}",
        )


@router.post("/generate", dependencies=[Depends(verify_token)])
@limiter.limit("3/minute")
async def generate_exam(
    request: Request,
    payload: ExamGenPayload,
):
    prompt = f"""
Generate a formal, rigorous final examination with {payload.num_questions} questions.

Title:
{payload.title or "Generated Final Examination"}

Topic:
{payload.topic or "Comprehensive Curriculum"}

Return ONLY valid JSON.

Use this structure:

{{
  "title": "string",
  "instructions": "string",
  "questions": [
    {{
      "number": 1,
      "question": "string",
      "type": "multiple_choice",
      "options": ["A", "B", "C", "D"],
      "correct_answer": "string",
      "explanation": "string",
      "difficulty": "easy|medium|hard"
    }}
  ]
}}

Ensure every question has one unambiguous correct answer.
"""

    content = generate_exam_with_ai(prompt)

    try:
        generated_content = json.loads(content)
    except json.JSONDecodeError:
        generated_content = {
            "raw_content": content,
        }

    return {
        "status": "success",
        "title": payload.title or payload.topic or "Generated Final Examination",
        "generated_content": generated_content,
    }


@router.post("/generate-from-course", dependencies=[Depends(verify_token)])
@limiter.limit("5/minute")
async def generate_exam_from_course(
    request: Request,
    payload: ExamGenPayload,
):
    if not payload.courseId:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="courseId is required.",
        )

    prompt = f"""
Generate a formal examination based on the course identified by:

Course ID:
{payload.courseId}

Topic:
{payload.topic or "All major course topics"}

Number of questions:
{payload.num_questions}

Return ONLY valid JSON using this structure:

{{
  "title": "string",
  "instructions": "string",
  "courseId": "{payload.courseId}",
  "questions": [
    {{
      "number": 1,
      "question": "string",
      "type": "multiple_choice",
      "options": ["A", "B", "C", "D"],
      "correct_answer": "string",
      "explanation": "string",
      "difficulty": "easy|medium|hard"
    }}
  ]
}}

Cover the major concepts and progressively vary question difficulty.
"""

    content = generate_exam_with_ai(prompt)

    try:
        questions = json.loads(content)
    except json.JSONDecodeError:
        questions = {
            "raw_content": content,
        }

    return {
        "status": "success",
        "courseId": payload.courseId,
        "questions": questions,
    }


@router.post("/generate-from-document", dependencies=[Depends(verify_token)])
@limiter.limit("5/minute")
async def generate_exam_from_document(
    request: Request,
    payload: ExamGenPayload,
):
    if not payload.documentId and not payload.fileId:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="documentId or fileId is required.",
        )

    if not payload.fileUrl:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="fileUrl is required for document-based exam generation.",
        )

    doc_text = fetch_document_text(payload.fileUrl)

    prompt = f"""
Generate a formal, rigorous examination based strictly on the following
document content.

Document ID:
{payload.documentId or payload.fileId}

Topic:
{payload.topic or "All major topics covered in the document"}

Number of questions:
{payload.num_questions}

Document content:
{doc_text}

Return ONLY valid JSON using this structure:

{{
  "title": "string",
  "instructions": "string",
  "documentId": "{payload.documentId or payload.fileId}",
  "questions": [
    {{
      "number": 1,
      "question": "string",
      "type": "multiple_choice",
      "options": ["A", "B", "C", "D"],
      "correct_answer": "string",
      "explanation": "string",
      "difficulty": "easy|medium|hard"
    }}
  ]
}}

Use only information supported by the document.
Cover the important concepts and avoid duplicate questions.
"""

    content = generate_exam_with_ai(prompt)

    try:
        questions = json.loads(content)
    except json.JSONDecodeError:
        questions = {
            "raw_content": content,
        }

    return {
        "status": "success",
        "documentId": payload.documentId or payload.fileId,
        "questions": questions,
    }
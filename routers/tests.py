# # routers/tests.py
# from fastapi import APIRouter, Depends, HTTPException, status, Request
# from pydantic import BaseModel
# from typing import Optional, List, Dict, Any
# from slowapi import Limiter
# from slowapi.util import get_remote_address
# from dependencies import client, verify_token  # Assuming your shared auth & openai client dependency

# # Initialize rate limiter using client IP address
# limiter = Limiter(key_func=get_remote_address)

# router = APIRouter(prefix="/api/v1/tests", tags=["AI Tests Generation"])

# class TestGenPayload(BaseModel):
#     title: Optional[str] = None
#     topic: Optional[str] = None
#     courseId: Optional[str] = None
#     documentId: Optional[str] = None
#     num_questions: Optional[int] = 15

# @router.post("/generate", dependencies=[Depends(verify_token)])
# @limiter.limit("3/minute") # Strict rate limit for full midterm and test structure synthesis
# async def generate_test(request: Request, payload: TestGenPayload):
#     """
#     AI generation endpoint called by NestJS to generate a full midterm/test structure.
#     """
#     try:
#         prompt = f"Generate a comprehensive test assessment with {payload.num_questions} questions on the topic: {payload.topic or 'General Academic'}. Format as a structured JSON object."
        
#         response = client.chat.completions.create(
#             model="gpt-4o-mini",
#             messages=[
#                 {"role": "system", "content": "You are an expert AI academic assessment generator."},
#                 {"role": "user", "content": prompt}
#             ],
#             response_format={"type": "json_object"}
#         )
        
#         content = response.choices[0].message.content
#         return {
#             "status": "success",
#             "title": payload.topic or "Generated Test Assessment",
#             "generated_content": eval(content) if content else {}
#         }
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"OpenAI test generation failed: {str(e)}"
#         )

# @router.post("/generate-from-course", dependencies=[Depends(verify_token)])
# @limiter.limit("5/minute") # Control course-based test generation loops
# async def generate_test_from_course(request: Request, payload: TestGenPayload):
#     """
#     Generates a test assessment based on course curriculum or materials.
#     """
#     return {
#         "status": "success",
#         "message": f"Test generated successfully for course ID: {payload.courseId}",
#         "questions": [
#             {
#                 "question": "Sample course test question 1?",
#                 "options": ["A", "B", "C", "D"],
#                 "correctAnswer": "A"
#             }
#         ]
#     }

# @router.post("/generate-from-document", dependencies=[Depends(verify_token)])
# @limiter.limit("5/minute") # Restrict document-based test synthesis frequency
# async def generate_test_from_document(request: Request, payload: TestGenPayload):
#     """
#     Generates a comprehensive test using text extracted from an uploaded document.
#     """
#     return {
#         "status": "success",
#         "message": f"Test generated successfully from document ID: {payload.documentId}",
#         "questions": []
#     }



# routers/tests.py

import json

from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel, Field
from typing import Optional

from slowapi import Limiter
from slowapi.util import get_remote_address

from dependencies import client, NVIDIA_MODEL, verify_token, fetch_document_text

limiter = Limiter(key_func=get_remote_address)

router = APIRouter(prefix="/api/v1/tests", tags=["AI Tests Generation"])


class TestGenPayload(BaseModel):
    title: Optional[str] = None
    topic: Optional[str] = None
    courseId: Optional[str] = None
    documentId: Optional[str] = None
    fileId: Optional[str] = None
    fileUrl: Optional[str] = None
    num_questions: Optional[int] = Field(default=15, ge=1, le=100)


def generate_test_with_ai(prompt: str):
    try:
        response = client.chat.completions.create(
            model=NVIDIA_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert AI academic assessment generator "
                        "for GleamLearn. Create high-quality tests that "
                        "accurately assess student understanding, application, "
                        "analysis, and recall."
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
            detail=f"NVIDIA AI test generation failed: {str(e)}",
        )


def parse_json_response(content: str):
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {
            "raw_content": content,
        }


@router.post("/generate", dependencies=[Depends(verify_token)])
@limiter.limit("3/minute")
async def generate_test(
    request: Request,
    payload: TestGenPayload,
):
    prompt = f"""
Generate a comprehensive academic test assessment with
{payload.num_questions} questions.

Title:
{payload.title or "Generated Test Assessment"}

Topic:
{payload.topic or "General Academic"}

Return ONLY valid JSON using this structure:

{{
  "title": "string",
  "instructions": "string",
  "questions": [
    {{
      "number": 1,
      "question": "string",
      "type": "multiple_choice",
      "options": ["A", "B", "C", "D"],
      "correctAnswer": "A",
      "explanation": "string",
      "difficulty": "easy|medium|hard"
    }}
  ]
}}

Make the questions academically useful and avoid duplicates.
"""

    content = generate_test_with_ai(prompt)

    return {
        "status": "success",
        "title": payload.title or payload.topic or "Generated Test Assessment",
        "generated_content": parse_json_response(content),
    }


@router.post("/generate-from-course", dependencies=[Depends(verify_token)])
@limiter.limit("5/minute")
async def generate_test_from_course(
    request: Request,
    payload: TestGenPayload,
):
    if not payload.courseId:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="courseId is required.",
        )

    prompt = f"""
Generate a comprehensive academic test based on the following course.

Course ID:
{payload.courseId}

Topic:
{payload.topic or "All major course topics"}

Number of questions:
{payload.num_questions}

Return ONLY valid JSON using this structure:

{{
  "courseId": "{payload.courseId}",
  "title": "string",
  "instructions": "string",
  "questions": [
    {{
      "number": 1,
      "question": "string",
      "type": "multiple_choice",
      "options": ["A", "B", "C", "D"],
      "correctAnswer": "A",
      "explanation": "string",
      "difficulty": "easy|medium|hard"
    }}
  ]
}}

Cover the major concepts that should be assessed in the course.
"""

    content = generate_test_with_ai(prompt)

    return {
        "status": "success",
        "courseId": payload.courseId,
        "questions": parse_json_response(content),
    }


@router.post("/generate-from-document", dependencies=[Depends(verify_token)])
@limiter.limit("5/minute")
async def generate_test_from_document(
    request: Request,
    payload: TestGenPayload,
):
    document_id = payload.documentId or payload.fileId

    if not document_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="documentId or fileId is required.",
        )

    if not payload.fileUrl:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="fileUrl is required for document-based test generation.",
        )

    doc_text = fetch_document_text(payload.fileUrl)

    prompt = f"""
Generate a comprehensive academic test using ONLY the information
contained in the document below.

Document ID:
{document_id}

Topic:
{payload.topic or "All major topics in the document"}

Number of questions:
{payload.num_questions}

Document content:
{doc_text}

Return ONLY valid JSON using this structure:

{{
  "documentId": "{document_id}",
  "title": "string",
  "instructions": "string",
  "questions": [
    {{
      "number": 1,
      "question": "string",
      "type": "multiple_choice",
      "options": ["A", "B", "C", "D"],
      "correctAnswer": "A",
      "explanation": "string",
      "difficulty": "easy|medium|hard"
    }}
  ]
}}

Do not introduce facts that are not supported by the document.
Avoid duplicate questions and cover the important concepts.
"""

    content = generate_test_with_ai(prompt)

    return {
        "status": "success",
        "documentId": document_id,
        "questions": parse_json_response(content),
    }
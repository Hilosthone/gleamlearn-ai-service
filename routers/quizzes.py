# # routers/quizzes.py
# from fastapi import APIRouter, Header, HTTPException, Request
# from pydantic import BaseModel
# import os
# import requests
# from datetime import datetime, timezone
# from openai import OpenAI
# from slowapi import Limiter
# from slowapi.util import get_remote_address

# # Initialize rate limiter using client IP address
# limiter = Limiter(key_func=get_remote_address)

# router = APIRouter(prefix="/api/v1/quizzes", tags=["Quiz System"])

# # Configuration keys and OpenAI client
# AI_API_KEY = os.getenv("AI_API_KEY", "your_secret_token")
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# client = OpenAI(api_key=OPENAI_API_KEY)

# class QuizRequest(BaseModel, extra="allow"):
#     title: str = None
#     description: str = None
#     courseId: str = None
#     fileId: str = None
#     fileUrl: str = None
#     topic: str = None
#     questions: list = []
#     options: dict = {}

# class QuizSubmitRequest(BaseModel, extra="allow"):
#     answers: dict = {}

# def verify_token(authorization: str = Header(None)):
#     if AI_API_KEY and authorization != f"Bearer {AI_API_KEY}":
#         raise HTTPException(status_code=401, detail="Unauthorized AI token")

# def fetch_document_text(file_url: str) -> str:
#     try:
#         response = requests.get(file_url)
#         response.raise_for_status()
#         return response.text[:15000] 
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=f"Failed to fetch document content: {str(e)}")

# # --- Quiz Management ---

# @router.get("")
# @limiter.limit("20/minute") # Allow smooth quiz list fetching
# async def get_quizzes(request: Request, authorization: str = Header(None)):
#     verify_token(authorization)
#     return {"status": "success", "quizzes": [], "message": "Retrieved all quizzes successfully."}

# @router.post("")
# @limiter.limit("10/minute") # Restrict manual quiz creation frequency
# async def create_quiz(request: Request, payload: QuizRequest, authorization: str = Header(None)):
#     verify_token(authorization)
#     return {"status": "success", "quizId": "quiz_new_123", "data": payload.dict(), "message": "Quiz created successfully."}

# @router.get("/{quiz_id}")
# @limiter.limit("30/minute") # Smooth quiz details retrieval
# async def get_quiz_by_id(request: Request, quiz_id: str, authorization: str = Header(None)):
#     verify_token(authorization)
#     return {"status": "success", "quizId": quiz_id, "title": "Sample Quiz", "questions": []}

# @router.patch("/{quiz_id}")
# @limiter.limit("10/minute") # Control quiz update requests
# async def update_quiz(request: Request, quiz_id: str, payload: QuizRequest, authorization: str = Header(None)):
#     verify_token(authorization)
#     return {"status": "success", "quizId": quiz_id, "updatedData": payload.dict(), "message": "Quiz updated successfully."}

# @router.delete("/{quiz_id}")
# @limiter.limit("10/minute") # Prevent rapid deletion loops
# async def delete_quiz(request: Request, quiz_id: str, authorization: str = Header(None)):
#     verify_token(authorization)
#     return {"status": "success", "quizId": quiz_id, "message": "Quiz deleted successfully."}


# # --- Quiz Generation Pipelines ---

# @router.post("/generate")
# @limiter.limit("5/minute") # Restrict general AI quiz generation overhead
# async def generate_quiz_general(request: Request, payload: QuizRequest, authorization: str = Header(None)):
#     verify_token(authorization)
#     completion = client.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=[
#             {"role": "system", "content": "Generate a structured multiple-choice quiz JSON containing questions, options, and correct answers."},
#             {"role": "user", "content": payload.description or "Generate a standard academic quiz."}
#         ]
#     )
#     return {"status": "success", "quiz": completion.choices[0].message.content}

# @router.post("/generate-from-course")
# @limiter.limit("5/minute") # Protect course-based quiz compilation
# async def generate_quiz_from_course(request: Request, payload: QuizRequest, authorization: str = Header(None)):
#     verify_token(authorization)
#     completion = client.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=[
#             {"role": "system", "content": "Generate a rigorous multi-question quiz testing mastery of the given course curriculum."},
#             {"role": "user", "content": f"Course ID: {payload.courseId}. Details: {payload.options}"}
#         ]
#     )
#     return {"status": "success", "courseId": payload.courseId, "quiz": completion.choices[0].message.content}

# @router.post("/generate-from-document")
# @limiter.limit("5/minute") # Control document-based quiz generation frequency
# async def generate_quiz_from_document(request: Request, payload: QuizRequest, authorization: str = Header(None)):
#     verify_token(authorization)
#     doc_text = fetch_document_text(payload.fileUrl) if payload.fileUrl else "Sample document content"
#     completion = client.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=[
#             {"role": "system", "content": "Generate a detailed multiple-choice quiz based strictly on the provided document text."},
#             {"role": "user", "content": doc_text}
#         ]
#     )
#     return {"status": "success", "fileId": payload.fileId, "quiz": completion.choices[0].message.content}

# @router.post("/generate-from-topic")
# @limiter.limit("5/minute") # Restrict topic-based quiz creation spam
# async def generate_quiz_from_topic(request: Request, payload: QuizRequest, authorization: str = Header(None)):
#     verify_token(authorization)
#     completion = client.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=[
#             {"role": "system", "content": "Generate a targeted quiz with answers and explanations centered on the requested topic."},
#             {"role": "user", "content": f"Topic: {payload.topic}"}
#         ]
#     )
#     return {"status": "success", "topic": payload.topic, "quiz": completion.choices[0].message.content}


# # --- Quiz Attempt & Grading Engine ---

# @router.post("/{quiz_id}/start")
# @limiter.limit("15/minute") # Control quiz attempt initiation frequency
# async def start_quiz_attempt(request: Request, quiz_id: str, authorization: str = Header(None)):
#     verify_token(authorization)
#     return {"status": "success", "attemptId": "attempt_xyz_789", "quizId": quiz_id, "startedAt": datetime.now(timezone.utc).isoformat(), "message": "Quiz attempt started."}

# @router.post("/{quiz_id}/submit")
# @limiter.limit("15/minute") # Protect quiz submission and grading endpoint
# async def submit_quiz_attempt(request: Request, quiz_id: str, payload: QuizSubmitRequest, authorization: str = Header(None)):
#     verify_token(authorization)
#     return {
#         "status": "success", 
#         "quizId": quiz_id, 
#         "score": 85.0, 
#         "totalQuestions": 10, 
#         "correctAnswers": 8, 
#         "message": "Quiz submitted and graded successfully."
#     }

# @router.get("/{quiz_id}/results")
# @limiter.limit("20/minute") # Smooth results review lookups
# async def get_quiz_results(request: Request, quiz_id: str, authorization: str = Header(None)):
#     verify_token(authorization)
#     return {"status": "success", "quizId": quiz_id, "resultsSummary": "Retrieved analysis of quiz attempts."}

# @router.get("/attempts")
# @limiter.limit("20/minute") # Control user history retrieval frequency
# async def get_user_quiz_attempts(request: Request, authorization: str = Header(None)):
#     verify_token(authorization)
#     return {"status": "success", "attempts": [], "message": "Retrieved user quiz attempt history."}

# @router.get("/attempts/{attempt_id}")
# @limiter.limit("20/minute") # Allow smooth attempt detail reviews
# async def get_specific_quiz_attempt(request: Request, attempt_id: str, authorization: str = Header(None)):
#     verify_token(authorization)
#     return {"status": "success", "attemptId": attempt_id, "reviewDetails": "Detailed breakdown of attempt responses."}


# routers/quizzes.py

import os
from datetime import datetime, timezone

import requests
from fastapi import APIRouter, Header, HTTPException, Request
from openai import OpenAI
from pydantic import BaseModel, Field
from slowapi import Limiter
from slowapi.util import get_remote_address

# Initialize rate limiter using client IP address
limiter = Limiter(key_func=get_remote_address)

router = APIRouter(
    prefix="/api/v1/quizzes",
    tags=["Quiz System"],
)

# Shared secret between NestJS Backend and FastAPI AI Service
AI_API_KEY = os.getenv(
    "AI_API_KEY",
    "your_secret_token",
)

# NVIDIA NIM configuration
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")

NVIDIA_BASE_URL = os.getenv(
    "NVIDIA_BASE_URL",
    "https://integrate.api.nvidia.com/v1",
)

NVIDIA_MODEL = os.getenv(
    "NVIDIA_MODEL",
    "z-ai/glm-5-3-flash",
)


if not NVIDIA_API_KEY:
    raise RuntimeError(
        "NVIDIA_API_KEY is not configured."
    )

# NVIDIA NIM provides an OpenAI-compatible API,
# so we can use the OpenAI Python SDK while pointing
# it to NVIDIA's API endpoint.

client = OpenAI(
    api_key=NVIDIA_API_KEY,
    base_url=NVIDIA_BASE_URL,
)


class QuizRequest(BaseModel, extra="allow"):
    title: str | None = None
    description: str | None = None
    courseId: str | None = None
    fileId: str | None = None
    fileUrl: str | None = None
    topic: str | None = None

    questions: list = Field(
        default_factory=list
    )

    options: dict = Field(
        default_factory=dict
    )


class QuizSubmitRequest(BaseModel, extra="allow"):
    answers: dict = Field(
        default_factory=dict
    )


def verify_token(
    authorization: str = Header(None),
):
    """
    Validates the internal shared bearer token
    sent by the NestJS backend gateway.
    """

    if AI_API_KEY and authorization != f"Bearer {AI_API_KEY}":
        raise HTTPException(
            status_code=401,
            detail="Unauthorized AI token",
        )


def fetch_document_text(
    file_url: str,
) -> str:
    """
    Downloads document content from the supplied URL.

    NOTE:
    This currently assumes the URL returns readable text.
    If the URL points to a PDF, DOCX, etc., use a proper
    document extraction pipeline instead.
    """

    if not file_url:
        raise HTTPException(
            status_code=400,
            detail="Document file URL is required.",
        )

    try:
        response = requests.get(
            file_url,
            timeout=30,
        )

        response.raise_for_status()

        return response.text[:15000]

    except requests.RequestException as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to fetch document content: {str(e)}",
        )

def generate_ai_response(
    system_prompt: str,
    user_prompt: str,
):
    """
    Sends a prompt to the configured NVIDIA NIM model.
    """

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

        return completion.choices[0].message.content

    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"NVIDIA AI generation failed: {str(e)}",
        )

@router.get("")
@limiter.limit("20/minute")
async def get_quizzes(
    request: Request,
    authorization: str = Header(None),
):
    """
    Retrieve all quizzes.
    """

    verify_token(authorization)

    return {
        "status": "success",
        "quizzes": [],
        "message": "Retrieved all quizzes successfully.",
    }


@router.post("")
@limiter.limit("10/minute")
async def create_quiz(
    request: Request,
    payload: QuizRequest,
    authorization: str = Header(None),
):
    """
    Create a quiz manually.
    """

    verify_token(authorization)

    return {
        "status": "success",
        "quizId": "quiz_new_123",
        "data": payload.model_dump(),
        "message": "Quiz created successfully.",
    }

@router.get("/attempts")
@limiter.limit("20/minute")
async def get_user_quiz_attempts(
    request: Request,
    authorization: str = Header(None),
):
    """
    Retrieve user's quiz attempt history.
    """

    verify_token(authorization)

    return {
        "status": "success",
        "attempts": [],
        "message": "Retrieved user quiz attempt history.",
    }


@router.get("/attempts/{attempt_id}")
@limiter.limit("20/minute")
async def get_specific_quiz_attempt(
    request: Request,
    attempt_id: str,
    authorization: str = Header(None),
):
    """
    Retrieve a specific quiz attempt.
    """

    verify_token(authorization)

    return {
        "status": "success",
        "attemptId": attempt_id,
        "reviewDetails": "Detailed breakdown of attempt responses.",
    }

@router.post("/generate")
@limiter.limit("5/minute")
async def generate_quiz_general(
    request: Request,
    payload: QuizRequest,
    authorization: str = Header(None),
):
    """
    Generate a general academic quiz using NVIDIA NIM.
    """

    verify_token(authorization)

    quiz = generate_ai_response(
        system_prompt=(
            "You are an expert educational assessment generator. "
            "Generate a structured multiple-choice quiz in JSON format. "
            "The quiz should contain questions, multiple options, "
            "the correct answer, and a short explanation for each answer. "
            "Ensure the questions are academically accurate and relevant."
        ),
        user_prompt=(
            payload.description
            or "Generate a standard academic quiz."
        ),
    )

    return {
        "status": "success",
        "quiz": quiz,
    }


@router.post("/generate-from-course")
@limiter.limit("5/minute")
async def generate_quiz_from_course(
    request: Request,
    payload: QuizRequest,
    authorization: str = Header(None),
):
    """
    Generate a rigorous quiz based on a course.
    """

    verify_token(authorization)

    quiz = generate_ai_response(
        system_prompt=(
            "You are an expert educational assessment generator. "
            "Generate a rigorous multi-question quiz that tests "
            "mastery of the provided course curriculum. "
            "Include multiple-choice questions, correct answers, "
            "and concise explanations."
        ),
        user_prompt=(
            f"Course ID: {payload.courseId}\n"
            f"Course Details: {payload.options}\n"
            f"Description: {payload.description or 'Not provided'}"
        ),
    )

    return {
        "status": "success",
        "courseId": payload.courseId,
        "quiz": quiz,
    }


@router.post("/generate-from-document")
@limiter.limit("5/minute")
async def generate_quiz_from_document(
    request: Request,
    payload: QuizRequest,
    authorization: str = Header(None),
):
    """
    Generate a quiz strictly from document content.
    """

    verify_token(authorization)

    doc_text = (
        fetch_document_text(payload.fileUrl)
        if payload.fileUrl
        else "Sample document content"
    )

    quiz = generate_ai_response(
        system_prompt=(
            "You are an expert educational assessment generator. "
            "Generate a detailed multiple-choice quiz based strictly "
            "on the provided document text. "
            "Do not introduce facts that are not supported by the document. "
            "Include questions, options, correct answers, "
            "and concise explanations."
        ),
        user_prompt=(
            f"DOCUMENT CONTENT:\n\n"
            f"{doc_text}"
        ),
    )

    return {
        "status": "success",
        "fileId": payload.fileId,
        "quiz": quiz,
    }


@router.post("/generate-from-topic")
@limiter.limit("5/minute")
async def generate_quiz_from_topic(
    request: Request,
    payload: QuizRequest,
    authorization: str = Header(None),
):
    """
    Generate a targeted quiz from a specific topic.
    """

    verify_token(authorization)

    quiz = generate_ai_response(
        system_prompt=(
            "You are an expert educational assessment generator. "
            "Generate a targeted academic quiz centered on the "
            "requested topic. Include questions, options, "
            "correct answers, and explanations."
        ),
        user_prompt=(
            f"Topic: {payload.topic or 'General academic topic'}"
        ),
    )

    return {
        "status": "success",
        "topic": payload.topic,
        "quiz": quiz,
    }

@router.get("/{quiz_id}")
@limiter.limit("30/minute")
async def get_quiz_by_id(
    request: Request,
    quiz_id: str,
    authorization: str = Header(None),
):
    """
    Retrieve quiz details.
    """

    verify_token(authorization)

    return {
        "status": "success",
        "quizId": quiz_id,
        "title": "Sample Quiz",
        "questions": [],
    }


@router.patch("/{quiz_id}")
@limiter.limit("10/minute")
async def update_quiz(
    request: Request,
    quiz_id: str,
    payload: QuizRequest,
    authorization: str = Header(None),
):
    """
    Update an existing quiz.
    """

    verify_token(authorization)

    return {
        "status": "success",
        "quizId": quiz_id,
        "updatedData": payload.model_dump(),
        "message": "Quiz updated successfully.",
    }


@router.delete("/{quiz_id}")
@limiter.limit("10/minute")
async def delete_quiz(
    request: Request,
    quiz_id: str,
    authorization: str = Header(None),
):
    """
    Delete an existing quiz.
    """

    verify_token(authorization)

    return {
        "status": "success",
        "quizId": quiz_id,
        "message": "Quiz deleted successfully.",
    }

@router.post("/{quiz_id}/start")
@limiter.limit("15/minute")
async def start_quiz_attempt(
    request: Request,
    quiz_id: str,
    authorization: str = Header(None),
):
    """
    Start a quiz attempt.
    """

    verify_token(authorization)

    return {
        "status": "success",
        "attemptId": "attempt_xyz_789",
        "quizId": quiz_id,
        "startedAt": datetime.now(
            timezone.utc
        ).isoformat(),
        "message": "Quiz attempt started.",
    }


@router.post("/{quiz_id}/submit")
@limiter.limit("15/minute")
async def submit_quiz_attempt(
    request: Request,
    quiz_id: str,
    payload: QuizSubmitRequest,
    authorization: str = Header(None),
):
    """
    Submit and grade a quiz attempt.

    NOTE:
    This is currently placeholder grading logic.
    Replace with actual quiz-answer validation against
    the stored quiz questions and correct answers.
    """

    verify_token(authorization)

    return {
        "status": "success",
        "quizId": quiz_id,
        "score": 85.0,
        "totalQuestions": 10,
        "correctAnswers": 8,
        "message": "Quiz submitted and graded successfully.",
    }


@router.get("/{quiz_id}/results")
@limiter.limit("20/minute")
async def get_quiz_results(
    request: Request,
    quiz_id: str,
    authorization: str = Header(None),
):
    """
    Retrieve quiz attempt results.
    """

    verify_token(authorization)

    return {
        "status": "success",
        "quizId": quiz_id,
        "resultsSummary": "Retrieved analysis of quiz attempts.",
    }
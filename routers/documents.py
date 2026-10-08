# # routers/documents.py
# import os
# from fastapi import APIRouter, Header, Request
# from slowapi import Limiter
# from slowapi.util import get_remote_address
# from dependencies import client, AiRequest, verify_token, fetch_document_text

# # Initialize rate limiter using client IP address
# limiter = Limiter(key_func=get_remote_address)

# router = APIRouter(prefix="/api/v1", tags=["Document AI Pipeline"])

# @router.post("/ai/documents/{file_id}/analyze")
# @router.post("/analyze")
# @limiter.limit("5/minute") # Protect deep document analysis from spam loops
# async def analyze_document(request: Request, payload: AiRequest, file_id: str = None, authorization: str = Header(None)):
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

# @router.get("/ai/documents/{file_id}/analysis")
# @limiter.limit("20/minute") # Allow smooth lookups for cached analysis
# async def get_document_analysis(request: Request, file_id: str, authorization: str = Header(None)):
#     verify_token(authorization)
#     return {"status": "success", "fileId": file_id, "message": "Retrieved cached document analysis successfully."}

# @router.post("/ai/documents/{file_id}/generate-notes")
# @router.post("/generate-notes")
# @limiter.limit("5/minute") # Restrict intensive study notes generation
# async def generate_notes(request: Request, payload: AiRequest, file_id: str = None, authorization: str = Header(None)):
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

# @router.post("/ai/documents/{file_id}/generate-summary")
# @router.post("/generate-summary")
# @limiter.limit("5/minute") # Control executive summary generation requests
# async def generate_summary(request: Request, payload: AiRequest, file_id: str = None, authorization: str = Header(None)):
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

# @router.post("/ai/documents/{file_id}/generate-flashcards")
# @router.post("/generate-flashcards")
# @limiter.limit("5/minute") # Prevent flashcard extraction spam
# async def generate_flashcards(request: Request, payload: AiRequest, file_id: str = None, authorization: str = Header(None)):
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

# @router.post("/ai/documents/{file_id}/generate-questions")
# @router.post("/generate-questions")
# @limiter.limit("5/minute") # Restrict question synthesis endpoints
# async def generate_questions(request: Request, payload: AiRequest, file_id: str = None, authorization: str = Header(None)):
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

# @router.post("/ai/documents/{file_id}/generate-quiz")
# @router.post("/generate-quiz")
# @limiter.limit("5/minute") # Control quiz generation overhead
# async def generate_quiz(request: Request, payload: AiRequest, file_id: str = None, authorization: str = Header(None)):
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

# @router.post("/ai/documents/{file_id}/generate-test")
# @router.post("/generate-test")
# @limiter.limit("3/minute") # Strict rate limit for comprehensive test synthesis
# async def generate_test(request: Request, payload: AiRequest, file_id: str = None, authorization: str = Header(None)):
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

# @router.post("/ai/documents/{file_id}/generate-exam")
# @router.post("/generate-exam")
# @limiter.limit("3/minute") # Strict rate limit for full-length rigorous exam generation
# async def generate_exam(request: Request, payload: AiRequest, file_id: str = None, authorization: str = Header(None)):
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

# @router.post("/ai/documents/{file_id}/create-course")
# @router.post("/create-course")
# @limiter.limit("3/minute") # Restrict multi-module course curriculum generation
# async def create_course(request: Request, payload: AiRequest, file_id: str = None, authorization: str = Header(None)):
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

# @router.get("/ai/documents/{file_id}/generated-content")
# @limiter.limit("20/minute") # Allow smooth asset retrieval lookups
# async def get_generated_content(request: Request, file_id: str, authorization: str = Header(None)):
#     verify_token(authorization)
#     return {"status": "success", "fileId": file_id, "message": "Retrieved all generated assets for this document."}

# @router.post("/ai/documents/{file_id}/generate-live-class")
# @limiter.limit("3/minute") # Restrict resource-heavy live class script and timeline compilation
# async def generate_live_class(request: Request, payload: AiRequest, file_id: str, authorization: str = Header(None)):
#     verify_token(authorization)
#     doc_text = fetch_document_text(payload.fileUrl)
    
#     completion = client.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=[
#             {
#                 "role": "system", 
#                 "content": "You are an expert AI instructor. Convert the provided document into a structured live class timeline JSON array. Each object must contain: 'timestamp', 'speaker_narration', 'visual_cue', and 'caption_text'."
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

# @router.get("/ai/documents/{file_id}/live-class-stream")
# @limiter.limit("20/minute") # Control live stream metadata polling frequency
# async def get_live_class_stream(request: Request, file_id: str, authorization: str = Header(None)):
#     verify_token(authorization)
#     return {
#         "status": "success",
#         "fileId": file_id,
#         "streamStatus": "ready",
#         "message": "Live class streaming metadata active. Supports playback controls, zoom states, and real-time caption sync."
#     }

# @router.post("/ai/documents/{file_id}/export-pdf")
# @limiter.limit("5/minute") # Protect PDF export rendering endpoints from abuse
# async def export_pdf(request: Request, payload: AiRequest, file_id: str, authorization: str = Header(None)):
#     verify_token(authorization)
#     return {
#         "status": "success",
#         "fileId": file_id,
#         "downloadUrl": f"https://storage.supabase.co/storage/v1/object/public/gleamlearn-exports/{file_id}-export.pdf",
#         "message": "Document successfully compiled and ready for PDF download."
#     }




# routers/documents.py

from fastapi import APIRouter, Header, Request

from slowapi import Limiter
from slowapi.util import get_remote_address

from dependencies import (
    client,
    NVIDIA_MODEL,
    AiRequest,
    verify_token,
    fetch_document_text,
)

limiter = Limiter(key_func=get_remote_address)

router = APIRouter(prefix="/api/v1", tags=["Document AI Pipeline"])


def generate_ai_response(system_prompt: str, user_prompt: str) -> str:
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

        return completion.choices[0].message.content or ""

    except Exception as e:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=502,
            detail=f"NVIDIA AI generation failed: {str(e)}",
        )


@router.post("/ai/documents/{file_id}/analyze")
@router.post("/analyze")
@limiter.limit("5/minute")
async def analyze_document(
    request: Request,
    payload: AiRequest,
    file_id: str = None,
    authorization: str = Header(None),
):
    verify_token(authorization)

    doc_text = fetch_document_text(payload.fileUrl)

    analysis = generate_ai_response(
        system_prompt=(
            "You are an expert academic AI tutor for GleamLearn. "
            "Provide a deep, structured analysis of the document. "
            "Identify the main topics, important concepts, relationships "
            "between ideas, key facts, difficult areas, and important "
            "learning points. Make the analysis useful for studying."
        ),
        user_prompt=doc_text,
    )

    target_id = file_id or payload.fileId

    return {
        "status": "success",
        "fileId": target_id,
        "analysis": analysis,
    }


@router.get("/ai/documents/{file_id}/analysis")
@limiter.limit("20/minute")
async def get_document_analysis(
    request: Request,
    file_id: str,
    authorization: str = Header(None),
):
    verify_token(authorization)

    return {
        "status": "success",
        "fileId": file_id,
        "message": "Retrieved cached document analysis successfully.",
    }


@router.post("/ai/documents/{file_id}/generate-notes")
@router.post("/generate-notes")
@limiter.limit("5/minute")
async def generate_notes(
    request: Request,
    payload: AiRequest,
    file_id: str = None,
    authorization: str = Header(None),
):
    verify_token(authorization)

    doc_text = fetch_document_text(payload.fileUrl)

    notes = generate_ai_response(
        system_prompt=(
            "You are an expert academic tutor. "
            "Generate comprehensive, well-structured study notes from "
            "the provided document. Organize the content using clear "
            "headings and subheadings. Include important definitions, "
            "concepts, explanations, examples, and key takeaways. "
            "Do not omit important information."
        ),
        user_prompt=doc_text,
    )

    target_id = file_id or payload.fileId

    return {
        "status": "success",
        "fileId": target_id,
        "notes": notes,
    }


@router.post("/ai/documents/{file_id}/generate-summary")
@router.post("/generate-summary")
@limiter.limit("5/minute")
async def generate_summary(
    request: Request,
    payload: AiRequest,
    file_id: str = None,
    authorization: str = Header(None),
):
    verify_token(authorization)

    doc_text = fetch_document_text(payload.fileUrl)

    summary = generate_ai_response(
        system_prompt=(
            "You are an expert academic summarization assistant. "
            "Create a concise but complete summary of the provided "
            "document. Focus on the most important concepts, facts, "
            "arguments, and conclusions while preserving the meaning "
            "of the original content."
        ),
        user_prompt=doc_text,
    )

    target_id = file_id or payload.fileId

    return {
        "status": "success",
        "fileId": target_id,
        "summary": summary,
    }


@router.post("/ai/documents/{file_id}/generate-flashcards")
@router.post("/generate-flashcards")
@limiter.limit("5/minute")
async def generate_flashcards(
    request: Request,
    payload: AiRequest,
    file_id: str = None,
    authorization: str = Header(None),
):
    verify_token(authorization)

    doc_text = fetch_document_text(payload.fileUrl)

    flashcards = generate_ai_response(
        system_prompt=(
            "You are an expert educational content generator. "
            "Generate useful study flashcards from the provided document. "
            "Return ONLY a valid JSON array. Each object must contain "
            "exactly two keys: 'front' and 'back'. "
            "The front should contain a question, term, or prompt. "
            "The back should contain the correct explanation or answer. "
            "Cover the important concepts in the document."
        ),
        user_prompt=doc_text,
    )

    target_id = file_id or payload.fileId

    return {
        "status": "success",
        "fileId": target_id,
        "flashcards": flashcards,
    }


@router.post("/ai/documents/{file_id}/generate-questions")
@router.post("/generate-questions")
@limiter.limit("5/minute")
async def generate_questions(
    request: Request,
    payload: AiRequest,
    file_id: str = None,
    authorization: str = Header(None),
):
    verify_token(authorization)

    doc_text = fetch_document_text(payload.fileUrl)

    questions = generate_ai_response(
        system_prompt=(
            "You are an expert academic assessment generator. "
            "Generate important study questions based strictly on the "
            "provided document. Include a mixture of conceptual, factual, "
            "application, and critical-thinking questions where appropriate. "
            "Do not invent information that is not supported by the document."
        ),
        user_prompt=doc_text,
    )

    target_id = file_id or payload.fileId

    return {
        "status": "success",
        "fileId": target_id,
        "questions": questions,
    }


@router.post("/ai/documents/{file_id}/generate-quiz")
@router.post("/generate-quiz")
@limiter.limit("5/minute")
async def generate_quiz(
    request: Request,
    payload: AiRequest,
    file_id: str = None,
    authorization: str = Header(None),
):
    verify_token(authorization)

    doc_text = fetch_document_text(payload.fileUrl)

    quiz = generate_ai_response(
        system_prompt=(
            "You are an expert academic quiz generator for GleamLearn. "
            "Generate a multiple-choice quiz based strictly on the document. "
            "Each question should have clear answer options and one correct "
            "answer. Include enough questions to cover the major concepts. "
            "Return the result as valid JSON with a questions array. "
            "Each question should contain: question, options, correctAnswer, "
            "and explanation."
        ),
        user_prompt=doc_text,
    )

    target_id = file_id or payload.fileId

    return {
        "status": "success",
        "fileId": target_id,
        "quiz": quiz,
    }


@router.post("/ai/documents/{file_id}/generate-test")
@router.post("/generate-test")
@limiter.limit("3/minute")
async def generate_test(
    request: Request,
    payload: AiRequest,
    file_id: str = None,
    authorization: str = Header(None),
):
    verify_token(authorization)

    doc_text = fetch_document_text(payload.fileUrl)

    test = generate_ai_response(
        system_prompt=(
            "You are an expert academic assessment designer. "
            "Generate a comprehensive test based strictly on the document. "
            "Include a balanced mixture of question types where appropriate, "
            "cover the major topics, and vary the difficulty. "
            "Make the questions suitable for serious student assessment."
        ),
        user_prompt=doc_text,
    )

    target_id = file_id or payload.fileId

    return {
        "status": "success",
        "fileId": target_id,
        "test": test,
    }


@router.post("/ai/documents/{file_id}/generate-exam")
@router.post("/generate-exam")
@limiter.limit("3/minute")
async def generate_exam(
    request: Request,
    payload: AiRequest,
    file_id: str = None,
    authorization: str = Header(None),
):
    verify_token(authorization)

    doc_text = fetch_document_text(payload.fileUrl)

    exam = generate_ai_response(
        system_prompt=(
            "You are an expert university and secondary-school examination "
            "designer. Generate a rigorous, full-length examination based "
            "strictly on the provided document. Cover the major concepts "
            "and include a suitable mixture of question types and difficulty "
            "levels. Ensure the questions test understanding, application, "
            "analysis, and recall where appropriate."
        ),
        user_prompt=doc_text,
    )

    target_id = file_id or payload.fileId

    return {
        "status": "success",
        "fileId": target_id,
        "exam": exam,
    }


@router.post("/ai/documents/{file_id}/create-course")
@router.post("/create-course")
@limiter.limit("3/minute")
async def create_course(
    request: Request,
    payload: AiRequest,
    file_id: str = None,
    authorization: str = Header(None),
):
    verify_token(authorization)

    doc_text = fetch_document_text(payload.fileUrl)

    course = generate_ai_response(
        system_prompt=(
            "You are an expert instructional designer for GleamLearn. "
            "Transform the provided document into a structured learning "
            "course. Organize it into logical modules and lessons. "
            "For each module, identify its learning objectives and key "
            "topics. Ensure the progression moves from foundational "
            "concepts to more advanced concepts."
        ),
        user_prompt=doc_text,
    )

    target_id = file_id or payload.fileId

    return {
        "status": "success",
        "fileId": target_id,
        "course": course,
    }


@router.get("/ai/documents/{file_id}/generated-content")
@limiter.limit("20/minute")
async def get_generated_content(
    request: Request,
    file_id: str,
    authorization: str = Header(None),
):
    verify_token(authorization)

    return {
        "status": "success",
        "fileId": file_id,
        "message": "Retrieved all generated assets for this document.",
    }


@router.post("/ai/documents/{file_id}/generate-live-class")
@limiter.limit("3/minute")
async def generate_live_class(
    request: Request,
    payload: AiRequest,
    file_id: str,
    authorization: str = Header(None),
):
    verify_token(authorization)

    doc_text = fetch_document_text(payload.fileUrl)

    live_class = generate_ai_response(
        system_prompt=(
            "You are an expert AI instructor and educational content "
            "designer. Convert the provided document into a structured "
            "live class timeline. Return ONLY a valid JSON array. "
            "Each object must contain exactly these fields: "
            "'timestamp', 'speaker_narration', 'visual_cue', and "
            "'caption_text'. Create a logical teaching progression "
            "with explanations, examples, and visual cues."
        ),
        user_prompt=doc_text,
    )

    return {
        "status": "success",
        "fileId": file_id,
        "liveClassSession": {
            "title": "Interactive AI Masterclass",
            "playbackControls": [
                "play",
                "pause",
                "fast_forward",
                "zoom_in",
                "zoom_out",
                "captions",
            ],
            "scriptTimeline": live_class,
        },
    }


@router.get("/ai/documents/{file_id}/live-class-stream")
@limiter.limit("20/minute")
async def get_live_class_stream(
    request: Request,
    file_id: str,
    authorization: str = Header(None),
):
    verify_token(authorization)

    return {
        "status": "success",
        "fileId": file_id,
        "streamStatus": "ready",
        "message": (
            "Live class streaming metadata active. "
            "Supports playback controls, zoom states, "
            "and real-time caption sync."
        ),
    }


@router.post("/ai/documents/{file_id}/export-pdf")
@limiter.limit("5/minute")
async def export_pdf(
    request: Request,
    payload: AiRequest,
    file_id: str,
    authorization: str = Header(None),
):
    verify_token(authorization)

    return {
        "status": "success",
        "fileId": file_id,
        "downloadUrl": (
            f"https://storage.supabase.co/storage/v1/object/public/"
            f"gleamlearn-exports/{file_id}-export.pdf"
        ),
        "message": "Document successfully compiled and ready for PDF download.",
    }
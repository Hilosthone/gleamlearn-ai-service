# routers/youtube.py

import asyncio
import os
import json
import requests

from fastapi import APIRouter, Depends, HTTPException, Security, Request, status
from pydantic import BaseModel, HttpUrl
from typing import Optional, Dict, Any

from slowapi import Limiter
from slowapi.util import get_remote_address

from dependencies import client, NVIDIA_MODEL, verify_token as verify_api_key, generate_ai_response as shared_generate_ai_response

from dependencies import rate_limit_key  # per learner, see dependencies.py
limiter = Limiter(key_func=rate_limit_key)

router = APIRouter(
    prefix="/api/v1/youtube",
    tags=["YouTube Learning Material"],
)




MAX_TRANSCRIPT_CHARS = 30000


class YouTubeResourcePayload(BaseModel):
    url: HttpUrl
    # Optional: transcript already fetched by the NestJS backend. When present it is
    # used directly, avoiding a second fetch from YouTube.
    transcript: Optional[str] = None


async def generate_ai_response(system_prompt: str, user_prompt: str) -> str:
    return await shared_generate_ai_response(
        system_prompt,
        user_prompt,
        require_content=True,
    )


def parse_ai_json(content: str):
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {
            "raw_content": content,
        }


def extract_video_id(url: str) -> Optional[str]:
    try:
        if "youtu.be/" in url:
            return url.split("youtu.be/")[1].split("?")[0].split("&")[0]

        if "youtube.com/watch" in url and "v=" in url:
            return url.split("v=")[1].split("&")[0]

        if "youtube.com/shorts/" in url:
            return url.split("youtube.com/shorts/")[1].split("?")[0]

        return None

    except Exception:
        return None


def fetch_youtube_transcript(url: str) -> str:
    """
    Fetches a transcript with youtube-transcript-api v1.x
    (the v0 `YouTubeTranscriptApi.get_transcript` class method no longer exists).
    Prefers English; otherwise falls back to the first available transcript.
    """

    try:
        from youtube_transcript_api import NoTranscriptFound, YouTubeTranscriptApi

        video_id = extract_video_id(url)

        if not video_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid YouTube URL.",
            )

        api = YouTubeTranscriptApi()

        try:
            fetched = api.fetch(video_id, languages=["en"])
        except NoTranscriptFound:
            available = next(iter(api.list(video_id)), None)
            if available is None:
                raise
            fetched = available.fetch()

        return " ".join(
            snippet.text
            for snippet in fetched
        )[:MAX_TRANSCRIPT_CHARS]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to retrieve YouTube transcript: {str(e)}",
        )


async def resolve_transcript(payload: YouTubeResourcePayload) -> str:
    """Uses the transcript supplied by the backend when present, otherwise fetches it."""

    supplied = (payload.transcript or "").strip()
    if supplied:
        return supplied[:MAX_TRANSCRIPT_CHARS]

    return await asyncio.to_thread(fetch_youtube_transcript, str(payload.url))


@router.post("")
@limiter.limit("10/minute")
async def create_resource(
    request: Request,
    payload: YouTubeResourcePayload,
    api_key: str = Security(verify_api_key),
):
    video_id = extract_video_id(str(payload.url))

    if not video_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid YouTube URL.",
        )

    return {
        "status": "success",
        "message": "YouTube resource submitted successfully.",
        "resource": {
            "videoId": video_id,
            "url": str(payload.url),
            "status": "pending",
        },
    }


@router.get("")
@limiter.limit("30/minute")
async def find_all_resources(
    request: Request,
    api_key: str = Security(verify_api_key),
):
    return {
        "status": "success",
        "resources": [],
        "message": "YouTube resources are managed by the NestJS backend.",
    }


@router.get("/{id}")
@limiter.limit("30/minute")
async def find_resource_by_id(
    request: Request,
    id: str,
    api_key: str = Security(verify_api_key),
):
    return {
        "status": "success",
        "resourceId": id,
        "message": "YouTube resource details are managed by the NestJS backend.",
    }


@router.delete("/{id}")
@limiter.limit("10/minute")
async def delete_resource(
    request: Request,
    id: str,
    api_key: str = Security(verify_api_key),
):
    return {
        "status": "success",
        "resourceId": id,
        "message": "YouTube resource deletion should be handled by the NestJS backend.",
    }


@router.get("/{id}/status")
@limiter.limit("30/minute")
async def get_resource_status(
    request: Request,
    id: str,
    api_key: str = Security(verify_api_key),
):
    return {
        "status": "success",
        "resourceId": id,
        "processingStatus": "pending",
    }


@router.post("/{id}/process")
@limiter.limit("5/minute")
async def process_resource(
    request: Request,
    id: str,
    payload: YouTubeResourcePayload,
    api_key: str = Security(verify_api_key),
):
    video_id = extract_video_id(str(payload.url))

    if not video_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid YouTube URL.",
        )

    transcript = await resolve_transcript(payload)

    if not transcript:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No transcript could be retrieved for this video.",
        )

    prompt = f"""
Create a structured learning resource from the following YouTube
video transcript.

Video ID:
{video_id}

Transcript:
{transcript}

Return ONLY valid JSON using this structure:

{{
  "title": "string",
  "description": "string",
  "summary": "string",
  "learningObjectives": [
    "string"
  ],
  "keyTopics": [
    {{
      "topic": "string",
      "explanation": "string"
    }}
  ],
  "notes": [
    {{
      "heading": "string",
      "content": "string"
    }}
  ],
  "flashcards": [
    {{
      "question": "string",
      "answer": "string"
    }}
  ],
  "questions": [
    {{
      "question": "string",
      "options": ["A", "B", "C", "D"],
      "correctAnswer": "A",
      "explanation": "string"
    }}
  ],
  "quiz": {{
    "questions": []
  }}
}}

Do not introduce information that is not supported by the transcript.
Make the material clear and suitable for students.
"""

    content = await generate_ai_response(
        system_prompt=(
            "You are GleamLearn's AI educational content processor. "
            "Transform educational video transcripts into structured, "
            "accurate, student-friendly learning materials."
        ),
        user_prompt=prompt,
    )

    return {
        "status": "success",
        "resourceId": id,
        "videoId": video_id,
        "processingStatus": "completed",
        "generatedContent": parse_ai_json(content),
    }


@router.post("/{id}/reprocess")
@limiter.limit("5/minute")
async def reprocess_resource(
    request: Request,
    id: str,
    payload: YouTubeResourcePayload,
    api_key: str = Security(verify_api_key),
):
    video_id = extract_video_id(str(payload.url))

    if not video_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid YouTube URL.",
        )

    transcript = await resolve_transcript(payload)

    if not transcript:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No transcript could be retrieved for this video.",
        )

    prompt = f"""
Reprocess this YouTube educational transcript and create an improved
structured learning resource.

Video ID:
{video_id}

Transcript:
{transcript}

Return ONLY valid JSON:

{{
  "title": "string",
  "description": "string",
  "summary": "string",
  "learningObjectives": [],
  "keyTopics": [],
  "notes": [],
  "flashcards": [],
  "questions": [],
  "quiz": {{
    "questions": []
  }}
}}

Improve clarity, organization, educational usefulness, and accuracy.
Do not invent information that is not supported by the transcript.
"""

    content = await generate_ai_response(
        system_prompt=(
            "You are an expert educational content editor for GleamLearn. "
            "Reprocess and improve learning materials generated from "
            "YouTube educational content."
        ),
        user_prompt=prompt,
    )

    return {
        "status": "success",
        "resourceId": id,
        "videoId": video_id,
        "processingStatus": "completed",
        "generatedContent": parse_ai_json(content),
    }
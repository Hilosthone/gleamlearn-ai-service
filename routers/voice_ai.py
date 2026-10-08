# # routers/voice_ai.py
# import os
# from fastapi import APIRouter, HTTPException, Security, Request
# from fastapi.security.api_key import APIKeyHeader
# from pydantic import BaseModel
# from typing import Optional, Dict, Any
# from slowapi import Limiter
# from slowapi.util import get_remote_address

# # Initialize rate limiter using client IP address
# limiter = Limiter(key_func=get_remote_address)

# router = APIRouter(prefix="/api/v1/ai/voice", tags=["Voice AI"])

# API_KEY = os.getenv("AI_API_KEY", "674930")
# api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# def verify_api_key(api_key: str = Security(api_key_header)):
#     if api_key != API_KEY:
#         raise HTTPException(status_code=403, detail="Invalid or missing AI API Key")
#     return api_key

# class VoicePayload(BaseModel):
#     audioData: Optional[str] = None # Base64 encoded audio or text transcript
#     text: Optional[str] = None
#     voiceId: Optional[str] = "default"

# @router.post("/transcribe")
# @limiter.limit("10/minute") # Restrict resource-heavy transcription endpoint frequency
# async def voice_transcribe(request: Request, payload: VoicePayload, api_key: str = Security(verify_api_key)):
#     # Free alternative: Integrate local openai-whisper library here if handling raw audio chunks
#     return {
#         "status": "success",
#         "transcript": payload.text or "Simulated transcription of voice input."
#     }

# @router.post("/respond")
# @limiter.limit("10/minute") # Protect voice AI response synthesis from spam loops
# async def voice_respond(request: Request, payload: VoicePayload, api_key: str = Security(verify_api_key)):
#     spoken_text = payload.text or "Hello from your voice AI assistant."
#     return {
#         "status": "success",
#         "responseMessage": spoken_text,
#         "audioResponse": "base64_encoded_audio_placeholder"
#     }

# @router.post("/synthesize")
# @limiter.limit("10/minute") # Control text-to-speech generation overhead
# async def voice_synthesize(request: Request, payload: VoicePayload, api_key: str = Security(verify_api_key)):
#     text_to_speak = payload.text or "Synthesizing audio stream."
#     return {
#         "status": "success",
#         "audioUrl": f"https://api.gttssimulator.local/synth?text={text_to_speak}"
#     }


# routers/voice_ai.py

import os

from fastapi import APIRouter, HTTPException, Security, Request
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel
from typing import Optional

from slowapi import Limiter
from slowapi.util import get_remote_address

from dependencies import client, NVIDIA_MODEL

limiter = Limiter(key_func=get_remote_address)

router = APIRouter(prefix="/api/v1/ai/voice", tags=["Voice AI"])

API_KEY = os.getenv("AI_API_KEY", "674930")

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(
            status_code=403,
            detail="Invalid or missing AI API Key",
        )
    return api_key


class VoicePayload(BaseModel):
    audioData: Optional[str] = None
    text: Optional[str] = None
    voiceId: Optional[str] = "default"


def generate_ai_response(system_prompt: str, user_prompt: str) -> str:
    try:
        response = client.chat.completions.create(
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

        content = response.choices[0].message.content

        if not content:
            raise HTTPException(
                status_code=502,
                detail="NVIDIA AI returned an empty response.",
            )

        return content

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"NVIDIA AI generation failed: {str(e)}",
        )


@router.post("/transcribe")
@limiter.limit("10/minute")
async def voice_transcribe(
    request: Request,
    payload: VoicePayload,
    api_key: str = Security(verify_api_key),
):
    if not payload.audioData and not payload.text:
        raise HTTPException(
            status_code=400,
            detail="Either audioData or text is required.",
        )

    if payload.text:
        return {
            "status": "success",
            "transcript": payload.text,
        }

    return {
        "status": "success",
        "transcript": "",
        "message": "Audio transcription requires a speech-to-text provider.",
    }


@router.post("/respond")
@limiter.limit("10/minute")
async def voice_respond(
    request: Request,
    payload: VoicePayload,
    api_key: str = Security(verify_api_key),
):
    spoken_text = payload.text

    if not spoken_text:
        raise HTTPException(
            status_code=400,
            detail="text is required for voice response generation.",
        )

    response_text = generate_ai_response(
        system_prompt=(
            "You are GleamLearn's voice AI assistant. "
            "Respond naturally, clearly, and concisely. "
            "You are helping a learner understand educational concepts."
        ),
        user_prompt=spoken_text,
    )

    return {
        "status": "success",
        "responseMessage": response_text,
        "voiceId": payload.voiceId,
        "audioResponse": None,
        "message": "AI response generated. Text-to-speech is required to produce audio.",
    }


@router.post("/synthesize")
@limiter.limit("10/minute")
async def voice_synthesize(
    request: Request,
    payload: VoicePayload,
    api_key: str = Security(verify_api_key),
):
    if not payload.text:
        raise HTTPException(
            status_code=400,
            detail="text is required for speech synthesis.",
        )

    return {
        "status": "success",
        "voiceId": payload.voiceId,
        "text": payload.text,
        "audioUrl": None,
        "message": "Text-to-speech provider is required to generate audio.",
    }
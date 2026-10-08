# # dependencies.py
# import os
# import requests
# from fastapi import Header, HTTPException
# from pydantic import BaseModel
# from openai import OpenAI

# # Configuration keys pulled safely from environment variables
# AI_API_KEY = os.getenv("AI_API_KEY", "your_secret_token")
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# # Initialize the OpenAI client securely
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



import os

import requests

from fastapi import Header, HTTPException
from pydantic import BaseModel
from openai import OpenAI


# ============================================================
# Configuration
# ============================================================

# Shared secret between NestJS Backend and FastAPI AI Service
AI_API_KEY = os.getenv("AI_API_KEY", "your_secret_token")

# NVIDIA NIM configuration
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
NVIDIA_BASE_URL = os.getenv(
    "NVIDIA_BASE_URL",
    "https://integrate.api.nvidia.com/v1",
)
NVIDIA_MODEL = os.getenv("NVIDIA_MODEL")


# ============================================================
# NVIDIA NIM Client
# ============================================================

if not NVIDIA_API_KEY:
    raise RuntimeError("NVIDIA_API_KEY is not configured")

if not NVIDIA_MODEL:
    raise RuntimeError("NVIDIA_MODEL is not configured")


client = OpenAI(
    api_key=NVIDIA_API_KEY,
    base_url=NVIDIA_BASE_URL,
)


# ============================================================
# AI Request Schema
# ============================================================

class AiRequest(BaseModel, extra="allow"):
    fileId: str
    fileUrl: str
    options: dict = {}


# ============================================================
# Internal Authentication
# ============================================================

def verify_token(authorization: str = Header(None)):
    """
    Validates the internal shared bearer token sent
    by the NestJS backend gateway.
    """

    if AI_API_KEY and authorization != f"Bearer {AI_API_KEY}":
        raise HTTPException(
            status_code=401,
            detail="Unauthorized AI token",
        )


# ============================================================
# Document Fetching
# ============================================================

def fetch_document_text(file_url: str) -> str:
    """
    Downloads the raw study document from cloud storage
    and extracts text for the AI service.
    """

    try:
        response = requests.get(file_url)
        response.raise_for_status()

        return response.text[:15000]

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to fetch document content: {str(e)}",
        )
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



import asyncio
import hmac
import io
import os
import zipfile
from xml.etree import ElementTree

import requests

from fastapi import Header, HTTPException
from pydantic import BaseModel
from openai import AsyncOpenAI
from pypdf import PdfReader


# ============================================================
# Configuration
# ============================================================

# Shared secret between NestJS Backend and FastAPI AI Service.
# Required: there is deliberately no default value.
AI_API_KEY = os.getenv("AI_API_KEY", "").strip()

# NVIDIA NIM configuration
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
NVIDIA_BASE_URL = os.getenv(
    "NVIDIA_BASE_URL",
    "https://integrate.api.nvidia.com/v1",
)
NVIDIA_MODEL = os.getenv("NVIDIA_MODEL")


def _env_number(name: str, default: float, minimum: float) -> float:
    try:
        value = float(os.getenv(name, default))
    except ValueError:
        return default
    return value if value >= minimum else default


# Per-request timeout for the model provider (seconds) and bounded SDK retries.
# The OpenAI SDK defaults (600s timeout, 2 retries) can hold a request for a very
# long time and multiply billed generations, so both are capped here.
NVIDIA_TIMEOUT_SECONDS = _env_number("NVIDIA_TIMEOUT_SECONDS", 90, 1)
NVIDIA_MAX_RETRIES = int(_env_number("NVIDIA_MAX_RETRIES", 1, 0))


# ============================================================
# NVIDIA NIM Client
# ============================================================

if not AI_API_KEY:
    raise RuntimeError("AI_API_KEY is not configured")

if not NVIDIA_API_KEY:
    raise RuntimeError("NVIDIA_API_KEY is not configured")

if not NVIDIA_MODEL:
    raise RuntimeError("NVIDIA_MODEL is not configured")


client = AsyncOpenAI(
    api_key=NVIDIA_API_KEY,
    base_url=NVIDIA_BASE_URL,
    timeout=NVIDIA_TIMEOUT_SECONDS,
    max_retries=NVIDIA_MAX_RETRIES,
)


async def generate_ai_response(
    system_prompt: str,
    user_prompt: str,
    require_content: bool = False,
) -> str:
    """
    Sends one system + user prompt to the configured NVIDIA NIM model without
    blocking the event loop. Returns the message text ("" when empty), raises
    502 on provider failure, and on an empty response when require_content=True.
    """

    try:
        completion = await client.chat.completions.create(
            model=NVIDIA_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        content = completion.choices[0].message.content or ""
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"NVIDIA AI generation failed: {str(e)}",
        )

    if require_content and not content:
        raise HTTPException(
            status_code=502,
            detail="NVIDIA AI returned an empty response.",
        )

    return content


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

def _matches_key(candidate) -> bool:
    if not isinstance(candidate, str) or not candidate:
        return False
    return hmac.compare_digest(candidate.encode(), AI_API_KEY.encode())


def verify_token(
    authorization: str | None = Header(None),
    x_api_key: str | None = Header(None, alias="X-API-Key"),
):
    """
    Validates the internal shared secret sent by the NestJS backend gateway.

    Accepts either `Authorization: Bearer <AI_API_KEY>` or `X-API-Key: <AI_API_KEY>`.
    Can be used as a FastAPI dependency or called directly with the
    Authorization header value.
    """

    bearer = None
    if isinstance(authorization, str) and authorization.startswith("Bearer "):
        bearer = authorization[len("Bearer "):]

    if not (_matches_key(bearer) or _matches_key(x_api_key)):
        raise HTTPException(
            status_code=401,
            detail="Unauthorized AI token",
        )

    return True


# ============================================================
# Document Fetching
# ============================================================

# Maximum characters of extracted text passed on to the model (unchanged from the
# previous implementation), and the maximum download size accepted.
MAX_DOCUMENT_CHARS = 15000
MAX_DOCUMENT_BYTES = int(_env_number("MAX_DOCUMENT_BYTES", 25 * 1024 * 1024, 1))
DOCUMENT_FETCH_TIMEOUT_SECONDS = _env_number("DOCUMENT_FETCH_TIMEOUT_SECONDS", 30, 1)

_DOCX_TYPES = (
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
)


def _download_document(file_url: str) -> tuple[bytes, str]:
    try:
        with requests.get(
            file_url,
            timeout=DOCUMENT_FETCH_TIMEOUT_SECONDS,
            stream=True,
        ) as response:
            response.raise_for_status()
            content_type = (response.headers.get("Content-Type") or "").split(";")[0].strip().lower()

            chunks = []
            size = 0
            for chunk in response.iter_content(chunk_size=64 * 1024):
                size += len(chunk)
                if size > MAX_DOCUMENT_BYTES:
                    raise HTTPException(
                        status_code=413,
                        detail="Document is too large to process.",
                    )
                chunks.append(chunk)

            return b"".join(chunks), content_type

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to fetch document content: {str(e)}",
        )


def _extract_pdf_text(data: bytes) -> str:
    try:
        reader = PdfReader(io.BytesIO(data))
        if reader.is_encrypted:
            # Many PDFs are "encrypted" with an empty user password; try that first.
            reader.decrypt("")

        parts = []
        length = 0
        for page in reader.pages:
            text = page.extract_text() or ""
            if text.strip():
                parts.append(text.strip())
                length += len(text)
            if length >= MAX_DOCUMENT_CHARS:
                break
        return "\n\n".join(parts)

    except Exception:
        raise HTTPException(
            status_code=422,
            detail="The PDF could not be read. It may be corrupted or password-protected.",
        )


def _extract_docx_text(data: bytes) -> str:
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            xml = archive.read("word/document.xml")
        root = ElementTree.fromstring(xml)
        ns = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
        paragraphs = []
        for paragraph in root.iter(f"{ns}p"):
            text = "".join(node.text or "" for node in paragraph.iter(f"{ns}t"))
            if text.strip():
                paragraphs.append(text)
        return "\n".join(paragraphs)

    except Exception:
        raise HTTPException(
            status_code=422,
            detail="The Word document could not be read.",
        )


def extract_document_text(data: bytes, content_type: str = "", file_url: str = "") -> str:
    """
    Extracts plain text from PDF, DOCX or text documents.
    The type is detected from the file signature first, then the Content-Type / URL.
    """

    url_path = file_url.split("?")[0].lower()

    if data.startswith(b"%PDF") or content_type == "application/pdf" or url_path.endswith(".pdf"):
        text = _extract_pdf_text(data)
        if not text.strip():
            raise HTTPException(
                status_code=422,
                detail=(
                    "No extractable text was found in this PDF. "
                    "Scanned/image-only PDFs are not supported yet."
                ),
            )
    elif content_type in _DOCX_TYPES or url_path.endswith(".docx") or (
        data.startswith(b"PK") and b"word/document.xml" in data[:65536]
    ):
        text = _extract_docx_text(data)
    elif content_type.startswith("text/") or content_type in ("application/json", "") or url_path.endswith((".txt", ".md")):
        if b"\x00" in data[:4096]:
            raise HTTPException(
                status_code=415,
                detail="Unsupported document type. Upload a PDF, DOCX or text file.",
            )
        text = data.decode("utf-8", errors="replace")
    else:
        raise HTTPException(
            status_code=415,
            detail="Unsupported document type. Upload a PDF, DOCX or text file.",
        )

    text = text.strip()
    if not text:
        raise HTTPException(
            status_code=422,
            detail="The document does not contain any readable text.",
        )

    return text[:MAX_DOCUMENT_CHARS]


async def fetch_document_text(file_url: str) -> str:
    """
    Downloads the study document from cloud storage and extracts its text.
    Runs the blocking download and parsing in a worker thread so the
    event loop stays responsive.
    """

    if not file_url:
        raise HTTPException(
            status_code=400,
            detail="Document file URL is required.",
        )

    data, content_type = await asyncio.to_thread(_download_document, file_url)
    return await asyncio.to_thread(extract_document_text, data, content_type, file_url)

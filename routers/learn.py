# routers/learn.py
"""
Learning from the learner's own material: text extraction, generation of lessons / notes / quizzes / mock exams /
flashcards / course plans, and source-grounded questions (used for YouTube transcripts and uploaded material).

Only the GleamLearn backend calls these routes (AI_API_KEY). The backend owns the material, checks ownership and
persists every result; nothing is stored here. Outputs are validated: malformed model output is an error, never a
partial "success".
"""
import base64
import binascii
import json
import re
from typing import Any, Dict, List, Literal, Optional

from fastapi import APIRouter, HTTPException, Request, Security
from visual_spec import REGISTRY_PROMPT, validate_visual_lesson
from pydantic import BaseModel, Field

from dependencies import (
    _extract_docx_text,
    _extract_pdf_text,
    generate_ai_response,
    limiter,
    verify_token as verify_api_key,
)

router = APIRouter(prefix="/api/v1/learn", tags=["Learning from your material"])

MAX_UPLOAD_BYTES = 15 * 1024 * 1024
MAX_SOURCE_CHARS = 200_000  # kept by the backend for search and later generation
CHUNK_CHARS = 12_000  # one model call
MAX_CHUNKS = 8  # ≈ 96k characters are read for one generation; more is reported as truncated
MIN_PDF_CHARS = 200  # below this a PDF is treated as scanned / image-only

TEXT_KINDS = ("lesson", "summary", "notes", "study_plan", "key_concepts", "explanation")
JSON_KINDS = ("quiz", "exam", "flashcards", "course_plan")


def _error(status: int, code: str, message: str) -> HTTPException:
    return HTTPException(status_code=status, detail={"code": code, "message": message})


def normalise_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n").replace("\u0000", "")
    text = re.sub(r"[ \t\f\v]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


# ---------------------------------------------------------------------------------------------------------------
# Extraction
# ---------------------------------------------------------------------------------------------------------------


class ExtractPayload(BaseModel):
    fileBase64: str
    mimeType: str = ""
    filename: str = ""


def extract_text(data: bytes, mime: str = "", filename: str = "") -> Dict[str, Any]:
    name = filename.lower()
    if data.startswith(b"%PDF"):
        text = normalise_text(_extract_pdf_text(data))
        if len(text) < MIN_PDF_CHARS:
            raise _error(
                422,
                "NO_TEXT",
                "Readable text could not be extracted from this PDF. It may be scanned or image-only; "
                "text recognition (OCR) is not available yet. Paste the text or upload a text-based PDF.",
            )
    elif data.startswith(b"PK") and b"word/document.xml" in data[:65536]:
        text = normalise_text(_extract_docx_text(data))
    elif b"\x00" not in data[:4096] and (mime.startswith("text/") or name.endswith((".txt", ".md")) or mime == ""):
        try:
            text = normalise_text(data.decode("utf-8"))
        except UnicodeDecodeError:
            raise _error(415, "UNSUPPORTED", "The text file is not valid UTF-8 text.")
    else:
        raise _error(415, "UNSUPPORTED", "Unsupported file type. Upload a PDF, Word (.docx) or text file.")
    if not text:
        raise _error(422, "NO_TEXT", "The document does not contain any readable text.")
    return {"text": text[:MAX_SOURCE_CHARS], "chars": min(len(text), MAX_SOURCE_CHARS), "truncated": len(text) > MAX_SOURCE_CHARS}


@router.post("/extract")
@limiter.limit("30/minute")
async def extract(request: Request, payload: ExtractPayload, api_key: str = Security(verify_api_key)):
    try:
        data = base64.b64decode(payload.fileBase64, validate=True)
    except (binascii.Error, ValueError):
        raise _error(400, "BAD_FILE", "The file could not be read.")
    if not data:
        raise _error(400, "BAD_FILE", "The file is empty.")
    if len(data) > MAX_UPLOAD_BYTES:
        raise _error(413, "TOO_LARGE", "The file must be 15 MB or smaller.")
    return {"status": "success", **extract_text(data, payload.mimeType, payload.filename)}


# ---------------------------------------------------------------------------------------------------------------
# Generation
# ---------------------------------------------------------------------------------------------------------------


class GenerateOptions(BaseModel):
    count: Optional[int] = None
    difficulty: Optional[Literal["easy", "medium", "hard", "mixed"]] = None
    level: Optional[str] = Field(default=None, max_length=100)
    examGoal: Optional[str] = Field(default=None, max_length=100)
    objective: Optional[str] = Field(default=None, max_length=500)
    subject: Optional[str] = Field(default=None, max_length=120)
    focus: Optional[str] = Field(default=None, max_length=300)


class GeneratePayload(BaseModel):
    kind: Literal["lesson", "summary", "notes", "study_plan", "key_concepts", "explanation", "quiz", "exam", "flashcards", "course_plan", "visual_lesson"]
    text: str = Field(min_length=1)
    # "topic": the learner named a topic only (visual lessons); taught from general knowledge, and the lesson says so
    sourceMode: Literal["material", "topic"] = "material"
    title: Optional[str] = Field(default=None, max_length=200)
    options: GenerateOptions = Field(default_factory=GenerateOptions)


GROUNDING = (
    "Use ONLY the SOURCE material provided. Do not add facts, figures, names or claims that the source does not "
    "support. If the source does not cover something that was asked for, say so plainly instead of inventing it."
)


def _learner_context(o: GenerateOptions) -> str:
    parts = []
    if o.subject:
        parts.append(f"Subject: {o.subject}")
    if o.level:
        parts.append(f"Learner level: {o.level}")
    if o.examGoal:
        parts.append(f"Exam goal: {o.examGoal}")
    if o.objective:
        parts.append(f"Learning objective: {o.objective}")
    if o.difficulty:
        parts.append(f"Difficulty: {o.difficulty}")
    if o.focus:
        parts.append(f"Focus on: {o.focus}")
    return "\n".join(parts)


async def condensed_source(text: str) -> Dict[str, Any]:
    """Long material is condensed chunk by chunk (faithfully) so generation can cover all of what was read."""
    text = normalise_text(text)
    if len(text) <= CHUNK_CHARS:
        return {"source": text, "chars": len(text), "truncated": False}
    chunks = [text[i : i + CHUNK_CHARS] for i in range(0, len(text), CHUNK_CHARS)]
    read = chunks[:MAX_CHUNKS]
    notes = []
    for i, chunk in enumerate(read, 1):
        notes.append(
            await generate_ai_response(
                system_prompt=(
                    "You condense study material faithfully. Keep every definition, fact, formula, example, "
                    "date and [mm:ss] timestamp that appears. Do not add anything that is not in the text."
                ),
                user_prompt=f"Part {i} of {len(read)}:\n\n{chunk}",
                require_content=True,
            )
        )
    return {"source": "\n\n".join(notes), "chars": sum(len(c) for c in read), "truncated": len(chunks) > MAX_CHUNKS}


def parse_json_object(content: str) -> Dict[str, Any]:
    """The model is asked for JSON; accept it bare or in a code fence, nothing else."""
    m = re.search(r"\{[\s\S]*\}", content or "")
    if not m:
        raise _error(502, "AI_BAD_OUTPUT", "The AI did not return the requested format. Please try again.")
    try:
        value = json.loads(m.group(0))
    except json.JSONDecodeError:
        raise _error(502, "AI_BAD_OUTPUT", "The AI did not return the requested format. Please try again.")
    if not isinstance(value, dict):
        raise _error(502, "AI_BAD_OUTPUT", "The AI did not return the requested format. Please try again.")
    return value


def _s(v: Any, limit: int) -> str:
    return v.strip()[:limit] if isinstance(v, str) else ""


def validate_questions(raw: Any, count: int) -> List[Dict[str, Any]]:
    """Keeps only well-formed multiple-choice questions: 2–6 distinct options, the answer being one of them."""
    out = []
    for q in raw if isinstance(raw, list) else []:
        if not isinstance(q, dict):
            continue
        question = _s(q.get("question"), 1000)
        options = [_s(o, 300) for o in q.get("options") or [] if _s(o, 300)]
        answer = _s(q.get("answer"), 300)
        if answer and answer not in options and re.fullmatch(r"[A-Fa-f]", answer):
            idx = ord(answer.upper()) - 65
            answer = options[idx] if idx < len(options) else answer
        if not question or not (2 <= len(options) <= 6) or len(set(options)) != len(options) or answer not in options:
            continue
        out.append({"question": question, "options": options, "answer": answer, "explanation": _s(q.get("explanation"), 1500), "topic": _s(q.get("topic"), 120)})
        if len(out) == count:
            break
    return out


def validate_cards(raw: Any, count: int) -> List[Dict[str, str]]:
    out = []
    for c in raw if isinstance(raw, list) else []:
        if isinstance(c, dict) and _s(c.get("question"), 500) and _s(c.get("answer"), 1500):
            out.append({"question": _s(c.get("question"), 500), "answer": _s(c.get("answer"), 1500)})
        if len(out) == count:
            break
    return out


def validate_modules(raw: Any, count: int) -> List[Dict[str, str]]:
    out = []
    for m in raw if isinstance(raw, list) else []:
        if isinstance(m, dict) and _s(m.get("title"), 200):
            out.append({"title": _s(m.get("title"), 200), "objective": _s(m.get("objective"), 500)})
        if len(out) == count:
            break
    return out


TEXT_PROMPTS = {
    "lesson": "Write a structured lesson that teaches this material: a short introduction, sections with headings (## ...), worked examples where the source has them, and a recap with key points.",
    "summary": "Write a concise summary of the material with the key points as bullet points.",
    "notes": "Write clear revision notes: headings, bullet points, definitions and formulas from the material.",
    "study_plan": "Write a study plan for learning this material: ordered sessions, what to cover in each, and how to check understanding. Use the learner's goal and level if given.",
    "key_concepts": "List the key concepts in the material, each with a one- or two-sentence explanation.",
    "explanation": "Explain the material step by step for this learner, with simple examples drawn from the source.",
}


@router.post("/generate")
@limiter.limit("30/minute")
async def generate(request: Request, payload: GeneratePayload, api_key: str = Security(verify_api_key)):
    if payload.sourceMode == "topic" and payload.kind != "visual_lesson":
        raise _error(422, "SOURCE_TOO_SHORT", "A topic on its own can only make a visual lesson.")
    if payload.kind == "visual_lesson":
        return await _visual_lesson(payload)
    if len(normalise_text(payload.text)) < 20:
        raise _error(422, "SOURCE_TOO_SHORT", "There is not enough material to learn from. Add more text.")
    src = await condensed_source(payload.text)
    o = payload.options
    ctx = _learner_context(o)
    header = f"{ctx}\n\n" if ctx else ""
    title = payload.title or ""

    if payload.kind in TEXT_KINDS:
        content = await generate_ai_response(
            system_prompt=f"You are GleamLearn's teacher. {GROUNDING} Write in clear, simple English using Markdown headings and lists.",
            user_prompt=f"{header}Task: {TEXT_PROMPTS[payload.kind]}\n\nSOURCE ({title or 'learner material'}):\n{src['source']}",
            require_content=True,
        )
        return {"status": "success", "kind": payload.kind, "content": content.strip(), "sourceChars": src["chars"], "truncated": src["truncated"]}

    if payload.kind in ("quiz", "exam"):
        limit = 60 if payload.kind == "exam" else 30
        count = max(1, min(o.count or (20 if payload.kind == "exam" else 10), limit))
        raw = await generate_ai_response(
            system_prompt=(
                f"You write multiple-choice practice questions for learners. {GROUNDING} Every question must be "
                "answerable from the source. These are AI-generated practice questions, never claim they are "
                "official past questions. Return ONLY JSON: "
                '{"questions": [{"question": "...", "options": ["...", "...", "...", "..."], "answer": "<the exact text of the correct option>", "explanation": "...", "topic": "..."}]}'
            ),
            user_prompt=f"{header}Write exactly {count} questions{' for a mock examination' if payload.kind == 'exam' else ''}, each with 4 distinct options.\n\nSOURCE ({title or 'learner material'}):\n{src['source']}",
            require_content=True,
        )
        questions = validate_questions(parse_json_object(raw).get("questions"), count)
        if not questions:
            raise _error(502, "AI_BAD_OUTPUT", "The AI did not return usable questions. Please try again.")
        return {"status": "success", "kind": payload.kind, "questions": questions, "requested": count, "returned": len(questions), "sourceChars": src["chars"], "truncated": src["truncated"]}

    if payload.kind == "flashcards":
        count = max(1, min(o.count or 12, 50))
        raw = await generate_ai_response(
            system_prompt=f"You write study flashcards. {GROUNDING} Return ONLY JSON: " + '{"cards": [{"question": "...", "answer": "..."}]}',
            user_prompt=f"{header}Write exactly {count} flashcards.\n\nSOURCE ({title or 'learner material'}):\n{src['source']}",
            require_content=True,
        )
        cards = validate_cards(parse_json_object(raw).get("cards"), count)
        if not cards:
            raise _error(502, "AI_BAD_OUTPUT", "The AI did not return usable flashcards. Please try again.")
        return {"status": "success", "kind": "flashcards", "cards": cards, "requested": count, "returned": len(cards), "sourceChars": src["chars"], "truncated": src["truncated"]}

    # course_plan
    count = max(3, min(o.count or 8, 20))
    raw = await generate_ai_response(
        system_prompt=f"You design study courses. {GROUNDING} Return ONLY JSON: " + '{"modules": [{"title": "...", "objective": "..."}]}',
        user_prompt=f"{header}Split this material into about {count} ordered modules, each with a one-sentence learning objective.\n\nSOURCE ({title or 'course outline'}):\n{src['source']}",
        require_content=True,
    )
    modules = validate_modules(parse_json_object(raw).get("modules"), count)
    if not modules:
        raise _error(502, "AI_BAD_OUTPUT", "The AI did not return a usable course plan. Please try again.")
    return {"status": "success", "kind": "course_plan", "modules": modules, "requested": count, "returned": len(modules), "sourceChars": src["chars"], "truncated": src["truncated"]}


async def _visual_lesson(payload: GeneratePayload) -> Dict[str, Any]:
    """A step-by-step lesson whose steps carry structured visuals from the closed registry in visual_spec.py."""
    o = payload.options
    ctx = _learner_context(o)
    header = f"{ctx}\n\n" if ctx else ""
    topic_mode = payload.sourceMode == "topic"
    if topic_mode:
        topic = normalise_text(payload.text).removeprefix("Topic:").strip()
        if len(topic) < 3:
            raise _error(422, "SOURCE_TOO_SHORT", "Name a topic to learn about.")
        source_block = f"TOPIC: {topic[:300]}"
        basis = ("Teach this topic from well-established knowledge suitable for the learner's level. If you are not "
                 "confident about a fact, leave it out rather than guess.")
        src = {"chars": len(topic), "truncated": False}
    else:
        if len(normalise_text(payload.text)) < 20:
            raise _error(422, "SOURCE_TOO_SHORT", "There is not enough material to learn from. Add more text.")
        src = await condensed_source(payload.text)
        source_block = f"SOURCE ({payload.title or 'learner material'}):\n{src['source']}"
        basis = GROUNDING
    steps = max(2, min(o.count or 5, 8))
    raw = await generate_ai_response(
        system_prompt=(
            f"You are GleamLearn's visual teacher. {basis} Teach in {steps} short, ordered steps; each step has a "
            "title, a clear explanation (plain sentences, may use simple Markdown lists) and an optional visual.\n"
            f"{REGISTRY_PROMPT}\n"
            'Return ONLY JSON: {"title":"...","summary":"...","steps":[{"title":"...","explanation":"...","visual":{...}|null}],"keyTakeaways":["..."]}'
        ),
        user_prompt=f"{header}Create a visual lesson.\n\n{source_block}",
        require_content=True,
    )
    lesson = validate_visual_lesson(parse_json_object(raw))
    if not lesson:
        raise _error(502, "AI_BAD_OUTPUT", "The AI did not return a usable visual lesson. Please try again.")
    if topic_mode:
        lesson["basis"] = "topic"  # the lesson is from general knowledge, not the learner's material
    visuals = sum(1 for s in lesson["steps"] if s["visual"])
    return {"status": "success", "kind": "visual_lesson", "lesson": lesson, "visuals": visuals, "sourceChars": src["chars"], "truncated": src["truncated"]}


# ---------------------------------------------------------------------------------------------------------------
# Grounded questions (YouTube transcript, uploaded material)
# ---------------------------------------------------------------------------------------------------------------


class AskSource(BaseModel):
    title: Optional[str] = Field(default=None, max_length=300)
    text: str = Field(min_length=1)


class AskPayload(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    source: AskSource
    history: Optional[list] = None


@router.post("/ask")
@limiter.limit("30/minute")
async def ask(request: Request, payload: AskPayload, api_key: str = Security(verify_api_key)):
    src = await condensed_source(payload.source.text)
    answer = await generate_ai_response(
        system_prompt=(
            "You are GleamLearn's tutor answering questions about ONE source (for example a video transcript). "
            "Answer only from the SOURCE. If the source does not contain the answer, say clearly that the source "
            "does not cover it; you may then add general guidance, clearly marked as not from the source. "
            "When you use a part of the source that carries a timestamp like [12:34], cite that timestamp in the "
            "same [mm:ss] form. Never invent timestamps."
        ),
        user_prompt=f"SOURCE ({payload.source.title or 'source'}):\n{src['source']}\n\nQUESTION: {payload.question}",
        require_content=True,
        history=payload.history,
    )
    return {"status": "success", "answer": answer.strip(), "truncated": src["truncated"]}

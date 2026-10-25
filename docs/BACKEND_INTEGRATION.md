# Backend Integration (NestJS → FastAPI)

Verified 2026-10-20 against the code of both repositories and with **live HTTP** through all three services.

## Contract

- **Paths:**
  - All 17 call sites in the backend resolve to existing routes here: 14 literal paths plus 3 built at runtime (document actions, voice and recommendations).
  - The tutor and personal-AI tools also match.
  - There are **0 mismatches**.
  - The AI companion module in the backend doesn't call this service; it only stores settings.
- **Auth:** the backend sends `Authorization: Bearer <AI_API_KEY>` and `X-API-Key: <AI_API_KEY>`, and `verify_token` accepts either. A missing or wrong key gives **401** (verified live).
- **Payload example** (`POST /api/v1/ai/explain`): `{ "input": string, "context"?: object }`.
  - The frontend's `AiToolContentPayload`, the backend's `ContextualAiDto` (`@IsObject`) and FastAPI's `ContextualPayload` (`Dict[str, Any]`) all agree.
  - Sending a string `context` gets a 400 from the backend before anything reaches this service (observed live).

| Backend module | Calls |
|---|---|
| `src/ai/ai.service.ts` | `/api/v1/ai/documents/{id}/{analyze, generate-notes, generate-summary, generate-flashcards, generate-questions, generate-quiz, generate-test, generate-exam, create-course, generate-live-class, export-pdf}`, plus `GET …/analysis`, `/generated-content`, `/live-class-stream` |
| `src/personal-ai/personal-ai.service.ts` | `/api/v1/chat`, `/api/v1/ai/{explain, summarize, generate-example, generate-practice, evaluate-answer, explain-mistake}` |
| `src/ai-tutor/ai-tutor.service.ts` | `/api/v1/ai-tutor/{message, teach, explain, generate-diagram, …}` |
| `src/quizzes`, `src/tests`, `src/exams` | `/api/v1/{quizzes,tests,exams}/generate[-from-course\|-from-document\|-from-topic]` |
| `src/ai-voice` | `/api/v1/ai/voice/{transcribe, respond, synthesize}` |
| `src/recommendations` | `/api/v1/recommendations[/courses\|/topics\|/quizzes\|/revision\|/exams]?userId=` |
| `src/youtube` | `/api/v1/youtube/{id}/process` |

## Live evidence (`mycoursea-backend/test/live/ai-integration.mjs`, 14/14)

The run used the real backend and the real FastAPI service, with a **mock** NIM (`test/live/mock_nim.py`). **The provider is mocked, so this doesn't prove real NVIDIA calls work.**

| Scenario | Result |
|---|---|
| Learner → `POST /api/v1/ai/explain` → FastAPI → NIM | 201; the generated text reaches the learner; exactly **1** provider call, with the configured model and a bearer key |
| No learner token | 401, and **no** provider call |
| FastAPI without / with a wrong shared key | 401 / 401 |
| Provider HTTP 500 | Backend **502**: "AI generation failed. Please try again later." (no provider details) |
| Provider slower than `NVIDIA_TIMEOUT_SECONDS` (3 s in the test) | Backend 502 after about **3.1 s**, not a hang |
| Provider returns empty content | `explanation: ""`; nothing is fabricated |
| AI service down | Backend **503** in about 0.01 s: "The AI service is currently unavailable. Please try again later." |
| Document URLs `https://169.254.169.254/…`, `http://res.cloudinary.com/…`, `https://example.org/…` (with a valid key) | **400**, "not from an allowed storage location" |

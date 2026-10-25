# Architecture

```
Browser ──HTTPS──> NestJS backend (Render) ──HTTP + shared key──> FastAPI AI service ──HTTPS──> NVIDIA NIM
                    • learner JWT auth                            • verify_token (AI_API_KEY)     (OpenAI-compatible)
                    • ownership, DB, rate limits                  • prompt building
                    • src/common/ai-service/ai-http.client.ts     • document download + text extraction
```

- **One gateway.** The backend's `getAiHttpClient()` (`AI_SERVICE_URL`, default `http://127.0.0.1:8000`; 120 s timeout) adds `Authorization: Bearer <AI_API_KEY>` and `X-API-Key`. Every route here checks the key with `verify_token` / `verify_api_key` (`dependencies.py`).
- **Stateless.** The service stores nothing. The routes that look like CRUD (`GET/POST /api/v1/quizzes`, `/api/v1/youtube…`) are **placeholders**: they return empty lists or echo their input. The backend owns that data and never calls them.
- **Model calls** go through `generate_ai_response()` in `dependencies.py`: one system prompt plus one user prompt to `client.chat.completions.create(model=NVIDIA_MODEL)`.
- **Documents:** the backend sends `{ fileId, fileUrl }`. The service downloads the file (allowed storage hosts only), extracts text from PDF, DOCX or text (`pypdf`, built-in zip/XML), and keeps the first 15 000 characters.
- **YouTube:** transcripts via `youtube-transcript-api` 1.x.

# Changelog (AI service)

## Batch 8 (2026-10-25): Honest "unavailable" responses

- **Changed routes:** `GET …/analysis`, `GET …/generated-content`, `GET …/live-class-stream`, `POST …/export-pdf`, `POST /api/v1/ai/voice/transcribe`, `POST /api/v1/ai/voice/synthesize` and all six `/api/v1/recommendations*` routes now answer **501** after authentication, with `detail = {code: 'FEATURE_UNAVAILABLE', feature, message}` (`dependencies.feature_unavailable`).
- **Removed fabricated data:** `export-pdf` returned a Supabase download URL that never existed; the GET routes returned "success" with no data; recommendations asked the model for generic courses with invented ids.
- **Tests:**
  - `tests/test_unavailable_features.py` (3 tests: 501 body for every route, no fake URL, auth first; the model is never called);
  - `tests/test_auth.py` now uses `GET /api/v1/quizzes` as its handler-level-auth example.
  - `python -m unittest discover -s tests -t .`: **33/33**.

## Batch 7 (2026-10-20): Integration audit and SSRF protection

- **Audit:**
  - 73 routes (`API_REFERENCE.md`).
  - The backend contract has 0 path mismatches; auth headers match; the `context` payload type agrees across frontend, backend and service.
  - Live cross-service run 14/14 (mock NIM). Details in `BACKEND_INTEGRATION.md`.
- **SSRF fix** (`dependencies.py`):
  - `ALLOWED_DOCUMENT_HOSTS` (default `res.cloudinary.com`); https only, no credentials, port 443.
  - Redirects followed manually: at most 3, each validated.
  - Generic fetch-failure messages.
- **Tests:**
  - New `tests/test_document_url_policy.py` (6).
  - `tests/test_document_extraction.py`: the size-limit test now uses an allowed host.
  - Total **30/30**.
- **Docs:** this `docs/` folder is new.

## Earlier (backend changelog Batches 3–6, 2026-10-11/12)

Unified `verify_token`; `AsyncOpenAI` with a timeout and retries; PDF/DOCX extraction with `pypdf`; YouTube transcript API 1.x; startup refuses missing keys; 24 tests.

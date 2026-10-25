# NVIDIA NIM Integration

- **Client:** `openai.AsyncOpenAI(api_key=NVIDIA_API_KEY, base_url=NVIDIA_BASE_URL, timeout=NVIDIA_TIMEOUT_SECONDS, max_retries=NVIDIA_MAX_RETRIES)` in `dependencies.py`.
- **Call:** `generate_ai_response(system_prompt, user_prompt, require_content=False)` sends `chat.completions.create(model=NVIDIA_MODEL, messages=[system, user])` and returns `choices[0].message.content` (or `""`).
- **Failures:**
  - Any SDK exception → `HTTPException(502)`.
  - With `require_content=True`, an empty answer → 502.
- **Bounded time:** 90 s per attempt by default, with 1 retry. The backend's own timeout to this service is 120 s, and the browser allows 150 s for AI endpoints.

## Verified vs not verified

| | Status |
|---|---|
| Request shape and model name sent; bearer auth to the provider; timeout path; error path; empty answer | ✅ Live, against a **mock** NIM |
| Real NVIDIA endpoint, real key, real model output and latency | ❌ **Not verified.** No paid calls were made. To verify, the owner runs one authorised request with real credentials and reports the status and latency. |

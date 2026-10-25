# GleamLearn AI Service: Documentation

FastAPI service that runs GleamLearn's AI features. **Only the NestJS backend calls it**; browsers never call it directly. It sends prompts to **NVIDIA NIM**, an OpenAI-compatible API, using the `openai` SDK.

| Document | Contents |
|---|---|
| [ARCHITECTURE.md](ARCHITECTURE.md) | Where the service sits; request flow |
| [ENVIRONMENT_VARIABLES.md](ENVIRONMENT_VARIABLES.md) | Every variable the active code reads |
| [API_REFERENCE.md](API_REFERENCE.md) | All 73 routes, generated from the active router code |
| [BACKEND_INTEGRATION.md](BACKEND_INTEGRATION.md) | The NestJS → FastAPI contract, verified (paths, auth, payloads, errors, live evidence) |
| [NVIDIA_INTEGRATION.md](NVIDIA_INTEGRATION.md) | How NIM is called; timeouts and retries; what is and isn't verified |
| [ERROR_HANDLING.md](ERROR_HANDLING.md) | Status codes and how the backend maps them |
| [SECURITY.md](SECURITY.md) | Service authentication, SSRF protection, secrets |
| [TESTING.md](TESTING.md) | Unit tests and the live cross-service run |
| [KNOWN_ISSUES.md](KNOWN_ISSUES.md) | Open problems |
| [CHANGELOG.md](CHANGELOG.md) | Changes, newest last |

**Not written yet:** `PROMPT_AND_OUTPUT_SCHEMAS.md`, because the per-route prompts and output shapes haven't been audited yet. `LOCAL_SETUP.md` is covered by the section below.

## Local setup

```bash
pip install -r requirements.txt
# .env (never commit it): AI_API_KEY, NVIDIA_API_KEY, NVIDIA_MODEL (see ENVIRONMENT_VARIABLES.md)
python -m uvicorn main:app --host 127.0.0.1 --port 8000
python -m unittest discover -s tests -t .      # 30 tests; dummy keys, no network calls
```

The service **refuses to start** if `AI_API_KEY`, `NVIDIA_API_KEY` or `NVIDIA_MODEL` is missing; there are no fallbacks.

# Testing

| Command | What it proves |
|---|---|
| `python -m unittest discover -s tests -t .` | **30 tests** (2026-10-20): auth, startup configuration, generation wiring, PDF/DOCX extraction, YouTube, URL policy. Dummy keys; NIM is unreachable or patched; no network. |
| `python -m py_compile main.py dependencies.py routers/*.py` | Syntax and imports |
| Cross-service live run (in `mycoursea-backend`): `python test/live/mock_nim.py 8799`, `node test/live/start-ai-service.mjs ../gleamlearn-ai-service`, `node test/live/start-backend.mjs`, `node test/live/ai-integration.mjs` | **14/14**: the real backend calls the real FastAPI with the **test** key, against a **mock** NIM. Covers success, auth, provider error, timeout, empty answer, service down and SSRF. It does **not** prove real NVIDIA calls. |

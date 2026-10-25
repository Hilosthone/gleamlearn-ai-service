# Environment Variables

Read by the **active** code (`dependencies.py`, `main.py`). Values never belong in git, logs or docs.

| Variable | Required | Default | Purpose |
|---|---|---|---|
| `AI_API_KEY` | **Yes** (startup fails without it) | none | Shared secret; the NestJS backend must use the **same** value. ⚠️ An old value is in this repo's public git history (commit `bb99205`): **rotate it** and set the new value on both services. |
| `NVIDIA_API_KEY` | **Yes** (startup fails) | none | NIM API key |
| `NVIDIA_MODEL` | **Yes** (startup fails) | none | Model id (in use: `z-ai/glm-5.3-flash`) |
| `NVIDIA_BASE_URL` | No | `https://integrate.api.nvidia.com/v1` | OpenAI-compatible endpoint |
| `NVIDIA_TIMEOUT_SECONDS` | No | `90` | Per-request timeout to NIM |
| `NVIDIA_MAX_RETRIES` | No | `1` | SDK retries on transient errors |
| `MAX_DOCUMENT_BYTES` | No | 25 MB | Download size limit (413 above it) |
| `DOCUMENT_FETCH_TIMEOUT_SECONDS` | No | `30` | Document download timeout |
| `ALLOWED_DOCUMENT_HOSTS` | No | `res.cloudinary.com` | Comma-separated hosts documents may be downloaded from; `.example.com` allows subdomains (SSRF protection, Batch 7) |

The values `674930`, `your_secret_token`, `OPEN_AI_KEY` and `OPENAI_API_KEY` appear **only in commented-out legacy code**. They are not used.

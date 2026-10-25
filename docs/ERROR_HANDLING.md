# Error Handling

| Situation | AI service | Backend → browser (`toAiHttpException`) |
|---|---|---|
| Missing or wrong shared key | 401 `Unauthorized AI token` | The backend always sends the key; a mismatch shows as a 5xx "AI generation failed…" |
| Provider error or timeout | 502 `NVIDIA AI generation failed: …` ⚠️ The detail includes the SDK's message | **502** "AI generation failed. Please try again later." (generic; verified live) |
| Empty answer (where content is required) | 502 | 502 (generic) |
| Document URL not allowed | 400 "Document URL is not from an allowed storage location." | 400 |
| Document download failure | 400 "Failed to fetch document content." (generic since Batch 7) | 400 |
| Document too large | 413 | 413 |
| AI service unreachable | none | **503** "The AI service is currently unavailable. Please try again later." (verified live) |
| Rate limit (`slowapi`, per-route limits) | 429 | 429 |

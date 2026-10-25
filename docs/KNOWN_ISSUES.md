# Known Issues (AI service)

1. **Rotate `AI_API_KEY`** (owner). It is exposed in public git history (`bb99205`). Set the new value on both the backend and this service at the same time.
2. **Real NVIDIA calls are unverified.** Only a mock provider was used.
3. **Placeholder routes:** `/api/v1/quizzes` CRUD and attempts, and `/api/v1/youtube` list/get/delete/status, return empty or echoed data. The backend doesn't call them; persistence lives in the backend.
6. **Not implemented anywhere; these answer 501 FEATURE_UNAVAILABLE since 2026-10-25:**
   - saved document analysis and generated content, and live-class streaming (the service is stateless);
   - PDF export;
   - speech-to-text and text-to-speech;
   - personalised recommendations (the old routes ignored the learner).
   - RAG (chunking, embeddings, retrieval) is also not implemented: documents are truncated to 15,000 characters.
4. **Prompts and output schemas aren't audited.** Model output is returned as text, without schema validation. Structured features (quiz or flashcard JSON, visualisations) need validated output before storage or rendering.
5. The provider error text is included in the 502 detail (see SECURITY.md).

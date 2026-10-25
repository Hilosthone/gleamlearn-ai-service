# API Reference (generated from active router code, 2026-10-20)

Every route requires the shared service key (`Authorization: Bearer <AI_API_KEY>` or `X-API-Key`); without it the answer is 401. Only the NestJS backend should call this service.

**Unavailable features (2026-10-25):** routes marked 501 answer, after authentication, `{"detail": {"code": "FEATURE_UNAVAILABLE", "feature": …, "message": …}}` and do no work. They used to return fabricated data (a non-existent PDF URL, empty "success" payloads, generic model-invented recommendations).

| Method | Path | Router : handler |
|---|---|---|
| POST | `/api/v1/ai-companion/chat` | `personal_ai_companion.py` : `companion_chat` |
| POST | `/api/v1/ai-companion/interact` | `personal_ai_companion.py` : `companion_interact` |
| POST | `/api/v1/ai-tutor/drawing-instructions` | `ai_tutor.py` : `ai_drawing_instructions` |
| POST | `/api/v1/ai-tutor/explain` | `ai_tutor.py` : `ai_tutor_explain` |
| POST | `/api/v1/ai-tutor/generate-diagram` | `ai_tutor.py` : `ai_generate_diagram` |
| POST | `/api/v1/ai-tutor/message` | `ai_tutor.py` : `tutor_message` |
| POST | `/api/v1/ai-tutor/teach` | `ai_tutor.py` : `ai_teach` |
| GET | `/api/v1/ai/documents/{file_id}/analysis` | `documents.py` : `get_document_analysis` — **501 FEATURE_UNAVAILABLE** (nothing is stored) |
| POST | `/api/v1/ai/documents/{file_id}/analyze` | `documents.py` : `analyze_document` |
| POST | `/api/v1/ai/documents/{file_id}/create-course` | `documents.py` : `create_course` |
| POST | `/api/v1/ai/documents/{file_id}/export-pdf` | `documents.py` : `export_pdf` — **501 FEATURE_UNAVAILABLE** (no PDF is generated) |
| POST | `/api/v1/ai/documents/{file_id}/generate-exam` | `documents.py` : `generate_exam` |
| POST | `/api/v1/ai/documents/{file_id}/generate-flashcards` | `documents.py` : `generate_flashcards` |
| POST | `/api/v1/ai/documents/{file_id}/generate-live-class` | `documents.py` : `generate_live_class` |
| POST | `/api/v1/ai/documents/{file_id}/generate-notes` | `documents.py` : `generate_notes` |
| POST | `/api/v1/ai/documents/{file_id}/generate-questions` | `documents.py` : `generate_questions` |
| POST | `/api/v1/ai/documents/{file_id}/generate-quiz` | `documents.py` : `generate_quiz` |
| POST | `/api/v1/ai/documents/{file_id}/generate-summary` | `documents.py` : `generate_summary` |
| POST | `/api/v1/ai/documents/{file_id}/generate-test` | `documents.py` : `generate_test` |
| GET | `/api/v1/ai/documents/{file_id}/generated-content` | `documents.py` : `get_generated_content` — **501 FEATURE_UNAVAILABLE** (nothing is stored) |
| GET | `/api/v1/ai/documents/{file_id}/live-class-stream` | `documents.py` : `get_live_class_stream` — **501 FEATURE_UNAVAILABLE** |
| POST | `/api/v1/ai/evaluate-answer` | `personal_ai.py` : `ai_evaluate_answer` |
| POST | `/api/v1/ai/explain` | `personal_ai.py` : `ai_explain` |
| POST | `/api/v1/ai/explain-mistake` | `personal_ai.py` : `ai_explain_mistake` |
| POST | `/api/v1/ai/generate-example` | `personal_ai.py` : `ai_generate_example` |
| POST | `/api/v1/ai/generate-practice` | `personal_ai.py` : `ai_generate_practice` |
| POST | `/api/v1/ai/summarize` | `personal_ai.py` : `ai_summarize` |
| POST | `/api/v1/ai/voice/respond` | `voice_ai.py` : `voice_respond` |
| POST | `/api/v1/ai/voice/synthesize` | `voice_ai.py` : `voice_synthesize` — **501 FEATURE_UNAVAILABLE** (no TTS provider) |
| POST | `/api/v1/ai/voice/transcribe` | `voice_ai.py` : `voice_transcribe` — **501 FEATURE_UNAVAILABLE** (no STT provider) |
| POST | `/api/v1/analyze` | `documents.py` : `analyze_document` |
| POST | `/api/v1/chat` | `personal_ai.py` : `ai_chat` |
| POST | `/api/v1/create-course` | `documents.py` : `create_course` |
| POST | `/api/v1/exams/generate` | `exams.py` : `generate_exam` |
| POST | `/api/v1/exams/generate-from-course` | `exams.py` : `generate_exam_from_course` |
| POST | `/api/v1/exams/generate-from-document` | `exams.py` : `generate_exam_from_document` |
| POST | `/api/v1/generate-exam` | `documents.py` : `generate_exam` |
| POST | `/api/v1/generate-flashcards` | `documents.py` : `generate_flashcards` |
| POST | `/api/v1/generate-notes` | `documents.py` : `generate_notes` |
| POST | `/api/v1/generate-questions` | `documents.py` : `generate_questions` |
| POST | `/api/v1/generate-quiz` | `documents.py` : `generate_quiz` |
| POST | `/api/v1/generate-summary` | `documents.py` : `generate_summary` |
| POST | `/api/v1/generate-test` | `documents.py` : `generate_test` |
| GET | `/api/v1/quizzes` | `quizzes.py` : `get_quizzes` |
| POST | `/api/v1/quizzes` | `quizzes.py` : `create_quiz` |
| GET | `/api/v1/quizzes/attempts` | `quizzes.py` : `get_user_quiz_attempts` |
| GET | `/api/v1/quizzes/attempts/{attempt_id}` | `quizzes.py` : `get_specific_quiz_attempt` |
| POST | `/api/v1/quizzes/generate` | `quizzes.py` : `generate_quiz_general` |
| POST | `/api/v1/quizzes/generate-from-course` | `quizzes.py` : `generate_quiz_from_course` |
| POST | `/api/v1/quizzes/generate-from-document` | `quizzes.py` : `generate_quiz_from_document` |
| POST | `/api/v1/quizzes/generate-from-topic` | `quizzes.py` : `generate_quiz_from_topic` |
| GET | `/api/v1/quizzes/{quiz_id}` | `quizzes.py` : `get_quiz_by_id` |
| PATCH | `/api/v1/quizzes/{quiz_id}` | `quizzes.py` : `update_quiz` |
| DELETE | `/api/v1/quizzes/{quiz_id}` | `quizzes.py` : `delete_quiz` |
| GET | `/api/v1/quizzes/{quiz_id}/results` | `quizzes.py` : `get_quiz_results` |
| POST | `/api/v1/quizzes/{quiz_id}/start` | `quizzes.py` : `start_quiz_attempt` |
| POST | `/api/v1/quizzes/{quiz_id}/submit` | `quizzes.py` : `submit_quiz_attempt` |
| GET | `/api/v1/recommendations` | `recommendations.py` : `get_all_recommendations` — **501 FEATURE_UNAVAILABLE** |
| GET | `/api/v1/recommendations/courses` | `recommendations.py` : `recommend_courses` — **501 FEATURE_UNAVAILABLE** |
| GET | `/api/v1/recommendations/exams` | `recommendations.py` : `recommend_exams` — **501 FEATURE_UNAVAILABLE** |
| GET | `/api/v1/recommendations/quizzes` | `recommendations.py` : `recommend_quizzes` — **501 FEATURE_UNAVAILABLE** |
| GET | `/api/v1/recommendations/revision` | `recommendations.py` : `recommend_revision` — **501 FEATURE_UNAVAILABLE** |
| GET | `/api/v1/recommendations/topics` | `recommendations.py` : `recommend_topics` — **501 FEATURE_UNAVAILABLE** |
| POST | `/api/v1/tests/generate` | `tests.py` : `generate_test` |
| POST | `/api/v1/tests/generate-from-course` | `tests.py` : `generate_test_from_course` |
| POST | `/api/v1/tests/generate-from-document` | `tests.py` : `generate_test_from_document` |
| POST | `/api/v1/youtube` | `youtube.py` : `create_resource` |
| GET | `/api/v1/youtube` | `youtube.py` : `find_all_resources` |
| GET | `/api/v1/youtube/{id}` | `youtube.py` : `find_resource_by_id` |
| DELETE | `/api/v1/youtube/{id}` | `youtube.py` : `delete_resource` |
| POST | `/api/v1/youtube/{id}/process` | `youtube.py` : `process_resource` |
| POST | `/api/v1/youtube/{id}/reprocess` | `youtube.py` : `reprocess_resource` |
| GET | `/api/v1/youtube/{id}/status` | `youtube.py` : `get_resource_status` |

73 routes. Routes without the `/api/v1/ai/documents/{file_id}` prefix that duplicate document actions (e.g. `/api/v1/generate-quiz`) are legacy aliases; the backend calls the prefixed ones.

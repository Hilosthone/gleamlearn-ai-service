"""Routes for capabilities that are not implemented answer 501 FEATURE_UNAVAILABLE (after authentication) instead
of fabricated data: no fake PDF URL, no empty "success" payloads, no generic model-invented recommendations."""
import unittest
from unittest.mock import patch

from tests._env import TEST_AI_API_KEY

from fastapi.testclient import TestClient

import main

client = TestClient(main.app)
AUTH = {"Authorization": f"Bearer {TEST_AI_API_KEY}"}
DOC_BODY = {"fileId": "file-1", "fileUrl": "https://res.cloudinary.com/demo/raw/upload/doc.pdf"}

ROUTES = [
    ("GET", "/api/v1/ai/documents/file-1/analysis", None, "Saved document analysis"),
    ("GET", "/api/v1/ai/documents/file-1/generated-content", None, "Saved generated content"),
    ("GET", "/api/v1/ai/documents/file-1/live-class-stream", None, "Live class streaming"),
    ("POST", "/api/v1/ai/documents/file-1/export-pdf", DOC_BODY, "PDF export"),
    ("POST", "/api/v1/ai/voice/transcribe", {"audioData": "AAAA"}, "Speech transcription"),
    ("POST", "/api/v1/ai/voice/synthesize", {"text": "Hello"}, "Speech synthesis"),
    *[("GET", f"/api/v1/recommendations{suffix}", None, "Personalised recommendations")
      for suffix in ("", "/courses", "/topics", "/quizzes", "/revision", "/exams")],
]


def call(method, path, body, headers):
    return client.request(method, path, json=body, headers=headers)


class UnavailableFeatureTests(unittest.TestCase):
    def test_each_route_answers_501_with_the_documented_body(self):
        with patch("dependencies.generate_ai_response") as model, patch("routers.recommendations.generate_ai_response") as recs_model:
            for method, path, body, feature in ROUTES:
                with self.subTest(path=path):
                    r = call(method, path, body, AUTH)
                    self.assertEqual(r.status_code, 501, r.text)
                    detail = r.json()["detail"]
                    self.assertEqual(detail["code"], "FEATURE_UNAVAILABLE")
                    self.assertEqual(detail["feature"], feature)
                    self.assertIn("not available yet", detail["message"])
            model.assert_not_called()
            recs_model.assert_not_called()

    def test_no_fabricated_download_url(self):
        r = call("POST", "/api/v1/ai/documents/file-1/export-pdf", DOC_BODY, AUTH)
        self.assertNotIn("downloadUrl", r.text)
        self.assertNotIn("storage.supabase.co", r.text)

    def test_authentication_still_comes_first(self):
        for method, path, body, _ in ROUTES:
            with self.subTest(path=path):
                self.assertEqual(call(method, path, body, {}).status_code, 401)


if __name__ == "__main__":
    unittest.main()

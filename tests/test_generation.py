import json
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from tests._env import TEST_AI_API_KEY

from fastapi.testclient import TestClient

import dependencies
import main

client = TestClient(main.app)
AUTH = {"Authorization": f"Bearer {TEST_AI_API_KEY}"}


def completion(text):
    return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=text))])


class ProviderClientConfigTests(unittest.TestCase):
    def test_async_client_has_bounded_timeout_and_retries(self):
        self.assertEqual(type(dependencies.client).__name__, "AsyncOpenAI")
        self.assertEqual(dependencies.client.max_retries, dependencies.NVIDIA_MAX_RETRIES)
        self.assertLessEqual(dependencies.NVIDIA_MAX_RETRIES, 1)
        self.assertLessEqual(dependencies.NVIDIA_TIMEOUT_SECONDS, 120)
        self.assertEqual(dependencies.client.timeout, dependencies.NVIDIA_TIMEOUT_SECONDS)


class MockedGenerationTests(unittest.TestCase):
    def setUp(self):
        self.create = AsyncMock(return_value=completion('{"title": "T", "questions": []}'))
        patcher = patch.object(dependencies.client.chat.completions, "create", self.create)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_contextual_route_returns_model_text(self):
        res = client.post("/api/v1/ai/explain", json={"input": "photosynthesis"}, headers=AUTH)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["explanation"], '{"title": "T", "questions": []}')
        kwargs = self.create.await_args.kwargs
        self.assertEqual(kwargs["model"], "unit-test-model")
        self.assertEqual(kwargs["messages"][1]["content"], "photosynthesis")

    def test_test_generation_wrapper_parses_json(self):
        res = client.post("/api/v1/tests/generate", json={"topic": "Algebra", "num_questions": 2}, headers=AUTH)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["generated_content"], {"title": "T", "questions": []})

    def test_empty_response_is_502_where_content_is_required(self):
        self.create.return_value = completion("")
        res = client.post("/api/v1/ai/voice/respond", json={"text": "hello"}, headers=AUTH)
        self.assertEqual(res.status_code, 502)

    def test_empty_response_is_allowed_where_it_was_before(self):
        self.create.return_value = completion(None)
        res = client.post("/api/v1/chat", json={"message": "hi"}, headers=AUTH)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["message"], "")

    def test_provider_error_maps_to_502(self):
        self.create.side_effect = RuntimeError("provider down")
        res = client.post("/api/v1/ai-tutor/explain", json={"input": "x"}, headers=AUTH)
        self.assertEqual(res.status_code, 502)


if __name__ == "__main__":
    unittest.main()

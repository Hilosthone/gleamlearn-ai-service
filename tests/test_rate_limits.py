"""Per-learner rate limits and classified provider errors.

Every request comes from the GleamLearn backend, so limits keyed by remote address were shared by all learners:
one learner's AI use returned 429 to everyone. The backend now sends X-GleamLearn-User; limits are per learner.
"""
import unittest
import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import openai

try:  # the HTTP library the installed openai SDK builds its errors from
    import httpx2 as httpx
except ImportError:  # pragma: no cover - older SDKs
    import httpx

from tests._env import TEST_AI_API_KEY

from fastapi.testclient import TestClient

import dependencies
import main

client = TestClient(main.app)


def headers(user=None):
    h = {"Authorization": f"Bearer {TEST_AI_API_KEY}"}
    if user:
        h["X-GleamLearn-User"] = user
    return h


def completion(text):
    return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=text))])


def provider_exc(cls, status, body=None, retry_after=None):
    req = httpx.Request("POST", "http://provider.test/v1/chat/completions")
    res = httpx.Response(status, request=req, headers={"retry-after": retry_after} if retry_after else {}, json=body or {})
    return cls(message=f"provider says {status} with account secrets", response=res, body=body)


class PerLearnerLimitTests(unittest.TestCase):
    def setUp(self):
        patcher = patch.object(dependencies.client.chat.completions, "create", AsyncMock(return_value=completion("ok")))
        patcher.start()
        self.addCleanup(patcher.stop)

    def explain(self, user):
        return client.post("/api/v1/ai/explain", json={"input": "osmosis"}, headers=headers(user))

    def test_one_learner_using_their_limit_does_not_block_another(self):
        a, b = f"learner-a-{uuid.uuid4()}"[:60], f"learner-b-{uuid.uuid4()}"[:60]
        codes = [self.explain(a).status_code for _ in range(31)]  # per-learner ceiling: 30/minute
        self.assertEqual(codes[:30], [200] * 30)
        self.assertEqual(codes[30], 429)
        self.assertEqual(self.explain(b).status_code, 200)

    def test_429_has_retry_after_and_a_code(self):
        a = f"learner-c-{uuid.uuid4()}"[:60]
        for _ in range(30):
            self.explain(a)
        res = self.explain(a)
        self.assertEqual(res.status_code, 429)
        self.assertEqual(res.json()["detail"]["code"], "AI_RATE_LIMITED")
        # the time actually left in this learner's window, not a flat 60 s
        wait = int(res.headers.get("Retry-After"))
        self.assertTrue(1 <= wait <= 61, wait)
        self.assertEqual(res.json()["detail"]["retryAfterSeconds"], wait)

    def test_one_shared_limiter_with_limits_above_the_backend(self):
        # separate limiter instances kept separate counters; the backend's per-learner limits must bind first
        self.assertIs(main.app.state.limiter, dependencies.limiter)
        import pathlib, re
        limits = [int(n) for f in pathlib.Path("routers").glob("*.py")
                  for n in re.findall(r'^\s*@limiter\.limit\("(\d+)/minute"\)', f.read_text(encoding="utf-8"), flags=re.M)]
        self.assertTrue(limits and min(limits) >= 30, limits)

    def test_key_uses_the_header_only_when_it_is_a_plain_id(self):
        req = lambda h: SimpleNamespace(headers=h, client=SimpleNamespace(host="10.0.0.9"))  # noqa: E731
        self.assertEqual(dependencies.rate_limit_key(req({"x-gleamlearn-user": "abc-123"})), "user:abc-123")
        self.assertEqual(dependencies.rate_limit_key(req({"x-gleamlearn-user": "bad id; drop"})), "ip:10.0.0.9")
        self.assertEqual(dependencies.rate_limit_key(req({})), "ip:10.0.0.9")

    def test_requests_without_the_api_key_are_rejected_before_counting(self):
        victim = f"learner-d-{uuid.uuid4()}"[:60]
        for _ in range(35):
            res = client.post("/api/v1/ai/explain", json={"input": "x"}, headers={"X-GleamLearn-User": victim})
            self.assertIn(res.status_code, (401, 403))
        self.assertEqual(self.explain(victim).status_code, 200)


class ProviderErrorTests(unittest.TestCase):
    def call_with(self, exc):
        with patch.object(dependencies.client.chat.completions, "create", AsyncMock(side_effect=exc)):
            return client.post("/api/v1/ai/explain", json={"input": "x"}, headers=headers(f"u-{uuid.uuid4()}"[:60]))

    def test_quota_exhausted(self):
        res = self.call_with(provider_exc(openai.RateLimitError, 429, {"error": {"code": "insufficient_quota"}}))
        self.assertEqual(res.status_code, 503)
        self.assertEqual(res.json()["detail"]["code"], "AI_PROVIDER_QUOTA_EXHAUSTED")
        self.assertNotIn("secrets", res.text)

    def test_provider_rate_limit_passes_retry_after(self):
        res = self.call_with(provider_exc(openai.RateLimitError, 429, {"error": {"code": "rate_limit_exceeded"}}, retry_after="7"))
        self.assertEqual(res.status_code, 503)
        self.assertEqual(res.json()["detail"], {"code": "AI_PROVIDER_RATE_LIMITED", "message": "The AI provider is rate-limiting requests.", "retryAfterSeconds": 7})
        self.assertEqual(res.headers.get("Retry-After"), "7")

    def test_bad_provider_key_is_not_reported_as_a_rate_limit(self):
        res = self.call_with(provider_exc(openai.AuthenticationError, 401))
        self.assertEqual(res.status_code, 502)
        self.assertEqual(res.json()["detail"]["code"], "AI_PROVIDER_AUTH")

    def test_timeout(self):
        res = self.call_with(openai.APITimeoutError(request=httpx.Request("POST", "http://provider.test")))
        self.assertEqual(res.status_code, 504)
        self.assertEqual(res.json()["detail"]["code"], "AI_PROVIDER_TIMEOUT")


if __name__ == "__main__":
    unittest.main()

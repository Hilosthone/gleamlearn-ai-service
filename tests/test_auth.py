import unittest

from tests._env import TEST_AI_API_KEY

from fastapi.testclient import TestClient

import main

client = TestClient(main.app)

# Placeholder routes that never call the model provider
BEARER_ROUTE = "/api/v1/quizzes"  # handler-level verify_token (Bearer-only before); analysis now answers 501
X_API_KEY_ROUTE = "/api/v1/youtube"  # previously X-API-Key-only


class InternalAuthTests(unittest.TestCase):
    def test_bearer_accepted_on_both_route_families(self):
        headers = {"Authorization": f"Bearer {TEST_AI_API_KEY}"}
        self.assertEqual(client.get(BEARER_ROUTE, headers=headers).status_code, 200)
        self.assertEqual(client.get(X_API_KEY_ROUTE, headers=headers).status_code, 200)

    def test_x_api_key_accepted_on_dependency_routes(self):
        headers = {"X-API-Key": TEST_AI_API_KEY}
        self.assertEqual(client.get(X_API_KEY_ROUTE, headers=headers).status_code, 200)

    def test_missing_or_wrong_key_rejected(self):
        for headers in ({}, {"Authorization": "Bearer wrong"}, {"X-API-Key": "wrong"}):
            self.assertEqual(client.get(BEARER_ROUTE, headers=headers).status_code, 401)
            self.assertEqual(client.get(X_API_KEY_ROUTE, headers=headers).status_code, 401)

    def test_old_hard_coded_defaults_rejected(self):
        for value in ("674930", "your_secret_token"):
            self.assertEqual(client.get(X_API_KEY_ROUTE, headers={"X-API-Key": value}).status_code, 401)
            self.assertEqual(
                client.get(BEARER_ROUTE, headers={"Authorization": f"Bearer {value}"}).status_code, 401
            )

    def test_root_is_public(self):
        self.assertEqual(client.get("/").status_code, 200)


if __name__ == "__main__":
    unittest.main()

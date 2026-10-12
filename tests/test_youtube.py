import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from tests._env import TEST_AI_API_KEY

from fastapi.testclient import TestClient
from youtube_transcript_api import NoTranscriptFound

import dependencies
import main
from routers import youtube

client = TestClient(main.app)
AUTH = {"X-API-Key": TEST_AI_API_KEY}
URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"


def snippets(*texts):
    return [SimpleNamespace(text=t, start=0.0, duration=1.0) for t in texts]


class TranscriptFetchTests(unittest.TestCase):
    def test_uses_v1_instance_fetch_api(self):
        api = MagicMock()
        api.fetch.return_value = snippets("hello", "world")
        with patch("youtube_transcript_api.YouTubeTranscriptApi", return_value=api):
            self.assertEqual(youtube.fetch_youtube_transcript(URL), "hello world")
        api.fetch.assert_called_once_with("dQw4w9WgXcQ", languages=["en"])

    def test_falls_back_to_first_available_language(self):
        api = MagicMock()
        api.fetch.side_effect = NoTranscriptFound("dQw4w9WgXcQ", ["en"], MagicMock())
        other = MagicMock()
        other.fetch.return_value = snippets("bonjour")
        api.list.return_value = [other]
        with patch("youtube_transcript_api.YouTubeTranscriptApi", return_value=api):
            self.assertEqual(youtube.fetch_youtube_transcript(URL), "bonjour")


class ProcessRouteTests(unittest.TestCase):
    def setUp(self):
        self.create = AsyncMock(return_value=SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content='{"title": "Video"}'))]
        ))
        p = patch.object(dependencies.client.chat.completions, "create", self.create)
        p.start()
        self.addCleanup(p.stop)

    def test_supplied_transcript_is_used_without_refetching(self):
        with patch.object(youtube, "fetch_youtube_transcript") as fetch:
            res = client.post("/api/v1/youtube/res-1/process",
                              json={"url": URL, "transcript": "backend transcript text"}, headers=AUTH)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["generatedContent"], {"title": "Video"})
        fetch.assert_not_called()
        self.assertIn("backend transcript text", self.create.await_args.kwargs["messages"][1]["content"])

    def test_missing_transcript_is_fetched_by_the_ai_service(self):
        with patch.object(youtube, "fetch_youtube_transcript", return_value="fetched text") as fetch:
            res = client.post("/api/v1/youtube/res-1/process", json={"url": URL}, headers=AUTH)
        self.assertEqual(res.status_code, 200)
        fetch.assert_called_once()
        self.assertIn("fetched text", self.create.await_args.kwargs["messages"][1]["content"])


if __name__ == "__main__":
    unittest.main()

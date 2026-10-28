# tests/test_visual_lesson.py — visual lessons: closed visual registry, validation, topic mode. MOCKED provider.
import json
import unittest
import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from tests._env import TEST_AI_API_KEY

from fastapi.testclient import TestClient

import dependencies
import main
from visual_spec import validate_visual, validate_visual_lesson

client = TestClient(main.app)


def headers():
    return {"Authorization": f"Bearer {TEST_AI_API_KEY}", "X-GleamLearn-User": f"vis-{uuid.uuid4()}"[:60]}


def completion(text):
    return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=text))])


LESSON = {
    "title": "Water",
    "summary": "Water is H2O.",
    "steps": [
        {"title": "Atoms", "explanation": "One oxygen, two hydrogens.", "visual": {"type": "molecule", "atoms": [{"id": "o", "element": "O"}, {"id": "h1", "element": "H"}, {"id": "h2", "element": "H"}], "bonds": [{"a": "o", "b": "h1"}, {"a": "o", "b": "h2"}]}},
        {"title": "Phases", "explanation": "Ice, water, steam.", "visual": {"type": "flow", "nodes": [{"id": "i", "label": "Ice"}, {"id": "w", "label": "Water"}], "edges": [{"from": "i", "to": "w", "label": "melting"}]}},
        {"title": "Danger", "explanation": "Text survives.", "visual": {"type": "html", "html": "<script>alert(1)</script>"}},
    ],
    "keyTakeaways": ["H2O"],
}


class VisualSpecTests(unittest.TestCase):
    def test_closed_registry(self):
        self.assertIsNone(validate_visual({"type": "javascript", "code": "x"}))
        self.assertIsNone(validate_visual({"type": "graph2d", "family": "eval"}))
        self.assertIsNone(validate_visual({"type": "molecule", "atoms": [{"id": "x", "element": "Xx"}]}))
        v = validate_visual({"type": "shape3d", "shape": "cone", "dimensions": {"r": 1e9}, "onload": "x"})
        self.assertEqual(v["dimensions"], {"r": 100})
        self.assertNotIn("onload", v)
        self.assertEqual(validate_visual({"type": "wave", "amplitude": float("nan")})["amplitude"], 1)

    def test_lesson_needs_two_steps_and_drops_bad_visuals(self):
        self.assertIsNone(validate_visual_lesson({"steps": [{"title": "a", "explanation": "b"}]}))
        lesson = validate_visual_lesson(LESSON)
        self.assertEqual([s["visual"]["type"] if s["visual"] else None for s in lesson["steps"]], ["molecule", "flow", None])


class VisualLessonEndpointTests(unittest.TestCase):
    def run_with(self, reply, payload):
        create = AsyncMock(return_value=completion(reply))
        with patch.object(dependencies.client.chat.completions, "create", create):
            return client.post("/api/v1/learn/generate", json=payload, headers=headers()), create

    def test_topic_mode_lesson(self):
        res, create = self.run_with(json.dumps(LESSON), {"kind": "visual_lesson", "text": "Topic: The water molecule", "sourceMode": "topic"})
        self.assertEqual(res.status_code, 200, res.text)
        body = res.json()
        self.assertEqual(body["kind"], "visual_lesson")
        self.assertEqual(body["lesson"]["basis"], "topic")
        self.assertEqual(body["visuals"], 2)
        system = create.call_args.kwargs["messages"][0]["content"]
        self.assertIn('"type":"molecule"', system)  # the registry is in the prompt
        self.assertIn("TOPIC: The water molecule", create.call_args.kwargs["messages"][-1]["content"])

    def test_material_mode_is_grounded_and_bad_output_is_502(self):
        res, _ = self.run_with("not json at all", {"kind": "visual_lesson", "text": "Photosynthesis makes glucose from light. " * 3})
        self.assertEqual(res.status_code, 502)
        self.assertEqual(res.json()["detail"]["code"], "AI_BAD_OUTPUT")

    def test_topic_mode_only_for_visual_lessons(self):
        res, _ = self.run_with("{}", {"kind": "quiz", "text": "Topic: cells", "sourceMode": "topic"})
        self.assertEqual(res.status_code, 422)


if __name__ == "__main__":
    unittest.main()

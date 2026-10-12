import os
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class StartupConfigTests(unittest.TestCase):
    def test_app_refuses_to_start_without_ai_api_key(self):
        # An empty value in the environment takes precedence over .env (load_dotenv does not override).
        env = {**os.environ, "AI_API_KEY": "", "NVIDIA_API_KEY": "x", "NVIDIA_MODEL": "x"}
        result = subprocess.run(
            [sys.executable, "-B", "-c", "import main"],
            cwd=ROOT, env=env, capture_output=True, text=True, timeout=120,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("AI_API_KEY is not configured", result.stderr)


if __name__ == "__main__":
    unittest.main()

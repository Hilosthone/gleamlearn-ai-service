"""Sets dummy configuration before the app is imported so tests never use real credentials.

load_dotenv() does not override variables that are already set, so these values win over .env.
"""
import os

TEST_AI_API_KEY = "unit-test-internal-key"

os.environ["AI_API_KEY"] = TEST_AI_API_KEY
os.environ["NVIDIA_API_KEY"] = "unit-test-nvidia-key"
os.environ["NVIDIA_MODEL"] = "unit-test-model"
os.environ["NVIDIA_BASE_URL"] = "http://127.0.0.1:9/unused"

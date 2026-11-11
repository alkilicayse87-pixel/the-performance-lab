
import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = PROJECT_ROOT / ".env"

load_dotenv(dotenv_path=ENV_FILE)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.4-mini")


if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is missing from the .env file")
NEON_DATABASE_URL = os.getenv("NEON_DATABASE_URL")

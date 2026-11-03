"""Configuration loaded from environment / .env."""
import os
from dotenv import load_dotenv

load_dotenv()

API_BASE = os.getenv("AIRLOCK_API_BASE", "").strip()
API_KEY = os.getenv("AIRLOCK_API_KEY", "").strip()
MODEL = os.getenv("AIRLOCK_MODEL", "").strip()


def require(name: str, value: str) -> str:
    if not value:
        raise RuntimeError(
            f"{name} is not set. Add it to your .env file (see .env.example)."
        )
    return value
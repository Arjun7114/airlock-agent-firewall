"""Configuration loaded from environment / .env."""
import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

# Primary model — Meta Model API (from .env)
API_BASE = os.getenv("AIRLOCK_API_BASE", "").strip()
API_KEY = os.getenv("AIRLOCK_API_KEY", "").strip()
MODEL = os.getenv("AIRLOCK_MODEL", "").strip()

# Weak comparison model — local Ollama by default
WEAK_API_BASE = os.getenv("AIRLOCK_WEAK_API_BASE", "http://localhost:11434/v1").strip()
WEAK_API_KEY = os.getenv("AIRLOCK_WEAK_API_KEY", "ollama").strip()
WEAK_MODEL = os.getenv("AIRLOCK_WEAK_MODEL", "llama3.2:3b").strip()


def require(name: str, value: str) -> str:
    if not value:
        raise RuntimeError(
            f"{name} is not set. Add it to your .env file (see .env.example)."
        )
    return value


@dataclass(frozen=True)
class ModelProfile:
    name: str
    base_url: str
    api_key: str
    model: str


def muse_profile() -> ModelProfile:
    return ModelProfile(
        name="muse-spark",
        base_url=require("AIRLOCK_API_BASE", API_BASE),
        api_key=require("AIRLOCK_API_KEY", API_KEY),
        model=require("AIRLOCK_MODEL", MODEL),
    )


def weak_profile() -> ModelProfile:
    return ModelProfile(
        name="weak",
        base_url=WEAK_API_BASE,
        api_key=WEAK_API_KEY,
        model=WEAK_MODEL,
    )
"""Model-agnostic chat client.

Talks to any OpenAI-compatible endpoint (Meta Model API, local Ollama,
Baseten/Modal) selected entirely through .env — no code change to switch.
"""
from openai import OpenAI

from airlock import config

_client: OpenAI | None = None


def get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(
            base_url=config.require("AIRLOCK_API_BASE", config.API_BASE),
            api_key=config.require("AIRLOCK_API_KEY", config.API_KEY),
        )
    return _client


def complete(messages, model=None, temperature=None, **kwargs) -> str:
    """Send chat messages, return the assistant's text reply."""
    client = get_client()
    model = model or config.require("AIRLOCK_MODEL", config.MODEL)
    params = {"model": model, "messages": messages, **kwargs}
    if temperature is not None:
        params["temperature"] = temperature
    response = client.chat.completions.create(**params)
    return response.choices[0].message.content
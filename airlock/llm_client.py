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


def chat(messages, tools=None, model=None, temperature=None, **kwargs):
    """Low-level chat call. Returns the raw assistant message (with tool_calls)."""
    client = get_client()
    model = model or config.require("AIRLOCK_MODEL", config.MODEL)
    params = {"model": model, "messages": messages, **kwargs}
    if tools is not None:
        params["tools"] = tools
    if temperature is not None:
        params["temperature"] = temperature
    response = client.chat.completions.create(**params)
    return response.choices[0].message


def complete(messages, model=None, temperature=None, **kwargs) -> str:
    """Convenience wrapper that returns just the assistant's text reply."""
    return chat(messages, model=model, temperature=temperature, **kwargs).content
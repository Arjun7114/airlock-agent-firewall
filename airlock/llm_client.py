"""Model-agnostic chat client.

Talks to any OpenAI-compatible endpoint (Meta Model API, local Ollama,
Baseten/Modal). A ModelProfile selects which backend each call uses, so the
same code runs the real agent on muse-spark and the red-team baseline on a
local weak model with no code changes.
"""
from openai import OpenAI

from airlock import config
from airlock.config import ModelProfile

_clients: dict[tuple, OpenAI] = {}


def _client_for(base_url: str, api_key: str) -> OpenAI:
    key = (base_url, api_key)
    if key not in _clients:
        _clients[key] = OpenAI(base_url=base_url, api_key=api_key)
    return _clients[key]


def chat(messages, tools=None, profile: ModelProfile | None = None,
         temperature=None, **kwargs):
    """Low-level chat call against the given profile (defaults to muse-spark).
    Returns the raw assistant message (with tool_calls)."""
    profile = profile or config.muse_profile()
    client = _client_for(profile.base_url, profile.api_key)
    params = {"model": profile.model, "messages": messages, **kwargs}
    if tools is not None:
        params["tools"] = tools
    if temperature is not None:
        params["temperature"] = temperature
    response = client.chat.completions.create(**params)
    return response.choices[0].message


def complete(messages, profile: ModelProfile | None = None,
             temperature=None, **kwargs) -> str:
    """Convenience wrapper returning just the assistant's text."""
    return chat(messages, profile=profile, temperature=temperature, **kwargs).content
"""Airlock action gate.

An autonomous agent may *propose* any tool call, but CONSEQUENTIAL actions (those
that affect the outside world) are never executed autonomously on the strength of
untrusted content. Sending a reply and closing a ticket are deferred to human
approval; only escalation (which routes to a human anyway) proceeds.

Deterministic and model-independent: it holds no matter what the model was tricked
into proposing, and it trusts no signal derived from untrusted content (e.g. a
content-influenced category).
"""
from demo_agent.tools import CONSEQUENTIAL_TOOLS


def evaluate(tool_name: str, args: dict, store) -> tuple[bool, str]:
    """Return (allowed, reason) for a proposed tool call."""
    if tool_name not in CONSEQUENTIAL_TOOLS:
        return True, "non-consequential action"

    if tool_name == "escalate":
        return True, "escalation to a human is always permitted"

    if tool_name == "send_reply":
        return False, "send_reply requires human approval (consequential action)"

    if tool_name == "close_ticket":
        return False, "close_ticket requires human approval (consequential action)"

    return False, f"unrecognized consequential action: {tool_name}"
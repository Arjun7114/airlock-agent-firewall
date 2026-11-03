"""Airlock action gate.

An autonomous agent may *propose* any tool call, but CONSEQUENTIAL actions
(those that affect the outside world) only execute when they satisfy an explicit,
trusted policy. Untrusted content can ask for them; it cannot authorize them.

Deterministic and model-independent: it holds no matter what the model was
tricked into proposing.
"""
from demo_agent.tools import CONSEQUENTIAL_TOOLS


def evaluate(tool_name: str, args: dict, store) -> tuple[bool, str]:
    """Return (allowed, reason) for a proposed tool call."""
    if tool_name not in CONSEQUENTIAL_TOOLS:
        return True, "non-consequential action"

    if tool_name == "send_reply":
        # Policy: replies are drafted for human review, never auto-sent.
        return False, "send_reply requires human approval (policy: draft only)"

    if tool_name == "close_ticket":
        # Policy: only tickets already classified as spam may be auto-closed.
        ticket = store.tickets.get(args.get("ticket_id"))
        category = ticket.category.value if (ticket and ticket.category) else None
        if category == "spam":
            return True, "closing a ticket already classified as spam"
        return False, f"close_ticket not permitted for category={category!r} (spam only)"

    if tool_name == "escalate":
        # Escalation routes to a human — always fail-safe.
        return True, "escalation to a human is always permitted"

    return False, f"unrecognized consequential action: {tool_name}"
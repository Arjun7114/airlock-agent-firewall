"""Tool schemas (OpenAI function-calling format) + a safe dispatcher.

The dispatcher only ever runs a tool from ALLOWED_TOOLS, so even a confused or
hijacked model cannot reach arbitrary methods.
"""
from demo_agent.tools import TicketStore

ALLOWED_TOOLS = {
    "categorize", "set_priority", "draft_reply",
    "send_reply", "escalate", "close_ticket",
}

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "categorize",
            "description": "Set the category of a ticket.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticket_id": {"type": "string"},
                    "category": {
                        "type": "string",
                        "enum": ["billing", "bug", "account", "security", "spam", "other"],
                    },
                },
                "required": ["ticket_id", "category"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "set_priority",
            "description": "Set the priority of a ticket.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticket_id": {"type": "string"},
                    "priority": {"type": "string", "enum": ["low", "medium", "high"]},
                },
                "required": ["ticket_id", "priority"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "draft_reply",
            "description": "Save a draft reply for later human review. Does NOT send anything.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticket_id": {"type": "string"},
                    "text": {"type": "string"},
                },
                "required": ["ticket_id", "text"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "send_reply",
            "description": "CONSEQUENTIAL: immediately send a reply email to the ticket's sender.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticket_id": {"type": "string"},
                    "text": {"type": "string"},
                },
                "required": ["ticket_id", "text"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "escalate",
            "description": "CONSEQUENTIAL: escalate a ticket to a human analyst.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticket_id": {"type": "string"},
                    "reason": {"type": "string"},
                },
                "required": ["ticket_id", "reason"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "close_ticket",
            "description": "CONSEQUENTIAL: close a ticket as resolved.",
            "parameters": {
                "type": "object",
                "properties": {"ticket_id": {"type": "string"}},
                "required": ["ticket_id"],
            },
        },
    },
]


def dispatch(store: TicketStore, name: str, arguments: dict) -> dict:
    """Execute a tool call against the store, restricted to ALLOWED_TOOLS."""
    if name not in ALLOWED_TOOLS:
        return {"ok": False, "error": f"unknown tool: {name}"}
    try:
        result = getattr(store, name)(**arguments)
        return {"ok": True, "result": result}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}
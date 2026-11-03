"""Tools the triage agent can call, backed by an in-memory ticket store.

Consequential tools (send_reply, escalate, close_ticket) change state in ways
that matter — these are what an attacker wants to trigger via injection, and
what Airlock will gate in Phase 3.
"""
from demo_agent.models import Ticket, Category, Priority, Status

CONSEQUENTIAL_TOOLS = {"send_reply", "escalate", "close_ticket"}


class TicketStore:
    def __init__(self, tickets: list[Ticket], history: dict[str, str] | None = None):
        self.tickets: dict[str, Ticket] = {t.id: t for t in tickets}
        self.history: dict[str, str] = history or {}   # ticket_id -> context (UNTRUSTED)
        self.action_log: list[dict] = []
        self.sent_messages: list[dict] = []

    def _log(self, action: str, ticket_id: str, **details) -> dict:
        entry = {"action": action, "ticket_id": ticket_id, **details}
        self.action_log.append(entry)
        return entry

    def _get(self, ticket_id: str) -> Ticket:
        if ticket_id not in self.tickets:
            raise KeyError(f"No ticket with id {ticket_id}")
        return self.tickets[ticket_id]

    # --- read / annotate (non-consequential) ---
    def get_customer_history(self, ticket_id: str) -> dict:
        """Return prior context/notes for the customer. This content is UNTRUSTED:
        it can contain whatever a customer or a prior ticket put there."""
        self._get(ticket_id)
        context = self.history.get(ticket_id, "No prior history on file for this customer.")
        self._log("get_customer_history", ticket_id)
        return {"ticket_id": ticket_id, "history": context}

    def list_tickets(self) -> list[dict]:
        return [
            {"id": t.id, "sender": t.sender, "subject": t.subject, "status": t.status.value}
            for t in self.tickets.values()
        ]

    def read_ticket(self, ticket_id: str) -> dict:
        return self._get(ticket_id).model_dump(mode="json")

    def categorize(self, ticket_id: str, category: str) -> dict:
        self._get(ticket_id).category = Category(category)
        return self._log("categorize", ticket_id, category=category)

    def set_priority(self, ticket_id: str, priority: str) -> dict:
        self._get(ticket_id).priority = Priority(priority)
        return self._log("set_priority", ticket_id, priority=priority)

    def draft_reply(self, ticket_id: str, text: str) -> dict:
        t = self._get(ticket_id)
        t.draft_reply = text
        t.status = Status.DRAFTED
        return self._log("draft_reply", ticket_id, text=text)

    # --- consequential (change the outside world) ---
    def send_reply(self, ticket_id: str, text: str) -> dict:
        t = self._get(ticket_id)
        self.sent_messages.append({"to": t.sender, "ticket_id": ticket_id, "text": text})
        return self._log("send_reply", ticket_id, to=t.sender, text=text)

    def escalate(self, ticket_id: str, reason: str) -> dict:
        self._get(ticket_id).status = Status.ESCALATED
        return self._log("escalate", ticket_id, reason=reason)

    def close_ticket(self, ticket_id: str) -> dict:
        self._get(ticket_id).status = Status.CLOSED
        return self._log("close_ticket", ticket_id)
"""Unit tests for the Airlock action gate (no LLM / network required)."""
from airlock import gate
from airlock.defended import gated_dispatch
from demo_agent.models import Ticket, Category, Status
from demo_agent.tools import TicketStore
from demo_agent.tool_schemas import dispatch


def _store():
    tickets = [
        Ticket(id="T-1", sender="a@b.com", subject="Billing", body="help"),
        Ticket(id="T-SPAM", sender="s@x.biz", subject="Buy now", body="spam"),
    ]
    return TicketStore(tickets)


def test_non_consequential_allowed():
    allowed, _ = gate.evaluate("categorize", {"ticket_id": "T-1", "category": "billing"}, _store())
    assert allowed


def test_send_reply_always_blocked():
    allowed, reason = gate.evaluate("send_reply", {"ticket_id": "T-1", "text": "hi"}, _store())
    assert not allowed
    assert "approval" in reason.lower()


def test_close_blocked_for_non_spam():
    store = _store()
    store.tickets["T-1"].category = Category.BILLING
    allowed, _ = gate.evaluate("close_ticket", {"ticket_id": "T-1"}, store)
    assert not allowed


def test_close_allowed_for_spam():
    store = _store()
    store.tickets["T-SPAM"].category = Category.SPAM
    allowed, _ = gate.evaluate("close_ticket", {"ticket_id": "T-SPAM"}, store)
    assert allowed


def test_escalate_allowed():
    allowed, _ = gate.evaluate("escalate", {"ticket_id": "T-1", "reason": "x"}, _store())
    assert allowed


def test_dispatch_rejects_unknown_tool():
    result = dispatch(_store(), "rm_rf", {})
    assert result["ok"] is False


def test_gated_dispatch_blocks_malicious_close():
    """An injected attempt to close a non-spam ticket is blocked; state unchanged."""
    store = _store()
    store.tickets["T-1"].category = Category.BILLING
    result = gated_dispatch(store, "close_ticket", {"ticket_id": "T-1"})
    assert result.get("blocked") is True
    assert store.tickets["T-1"].status == Status.OPEN


def test_gated_dispatch_allows_legitimate_action():
    store = _store()
    result = gated_dispatch(store, "categorize", {"ticket_id": "T-1", "category": "billing"})
    assert result["ok"] is True
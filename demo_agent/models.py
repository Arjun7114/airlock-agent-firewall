"""Data model for the support-ticket triage demo agent.

SECURITY NOTE: `subject` and `body` are the UNTRUSTED channel — they come from
whoever submitted the ticket, so they may contain malicious instructions.
Everything else is set by our own system.
"""
from enum import Enum

from pydantic import BaseModel


class Category(str, Enum):
    BILLING = "billing"
    BUG = "bug"
    ACCOUNT = "account"
    SECURITY = "security"
    SPAM = "spam"
    OTHER = "other"


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Status(str, Enum):
    OPEN = "open"
    DRAFTED = "drafted"
    ESCALATED = "escalated"
    CLOSED = "closed"


class Ticket(BaseModel):
    id: str
    sender: str
    subject: str          # untrusted
    body: str             # untrusted
    status: Status = Status.OPEN
    category: Category | None = None
    priority: Priority | None = None
    draft_reply: str | None = None
"""Load sample tickets from data/sample_tickets.json as Ticket objects."""
import json
from pathlib import Path

from demo_agent.models import Ticket

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "sample_tickets.json"


def load_tickets(path: Path = DATA_PATH) -> list[Ticket]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return [Ticket(**item) for item in raw]
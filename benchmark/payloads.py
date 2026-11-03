"""Load the indirect-injection attack corpus."""
import json
from pathlib import Path

PAYLOAD_PATH = Path(__file__).resolve().parent.parent / "data" / "attack_payloads.json"


def load_payloads(path: Path = PAYLOAD_PATH) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))
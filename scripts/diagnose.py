"""Diagnose attack behavior: show every action, draft, and sent message."""
from benchmark.payloads import load_payloads
from benchmark.runner import build_store_with_attack
from demo_agent.models import Ticket
from demo_agent.agent import triage_ticket, NAIVE_SYSTEM_PROMPT


def diagnose(attack_id: str):
    payload = next(p for p in load_payloads() if p["id"] == attack_id)
    ticket = Ticket(**payload["ticket"])
    store = build_store_with_attack(ticket, payload.get("poison_history", ""))
    print(f"\n===== {attack_id}: {payload['technique']} =====")
    triage_ticket(store, ticket, system_prompt=NAIVE_SYSTEM_PROMPT, verbose=True)
    print("\n-- action log --")
    for a in store.action_log:
        print(" ", a)
    print("-- sent messages --", store.sent_messages)
    print("-- success spec --", payload["success"])


if __name__ == "__main__":
    for aid in ("ATK-01", "ATK-03"):
        diagnose(aid)
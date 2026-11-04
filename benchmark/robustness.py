"""Robustness stress test: diverse, arbitrary adversarial attacks (NOT tuned to the
model) run through the undefended agent and through Airlock. Reports how many cause
a CONSEQUENTIAL action — the real-world-harm metric. Airlock should be 0.
"""
import functools
import json
from pathlib import Path

from rich.console import Console
from rich.table import Table

from airlock import config
from airlock.quarantine import make_quarantined_triage
from demo_agent.agent import triage_ticket, NAIVE_SYSTEM_PROMPT
from benchmark.runner import run_attack

console = Console()
PATH = Path(__file__).resolve().parent.parent / "data" / "robustness_payloads.json"


def main():
    payloads = json.loads(PATH.read_text(encoding="utf-8"))
    weak = config.weak_profile()
    undef = functools.partial(triage_ticket, profile=weak, system_prompt=NAIVE_SYSTEM_PROMPT)
    airlock = make_quarantined_triage(profile=weak)

    table = Table(title="Robustness stress test (weak model, diverse attacks)")
    table.add_column("Attack", style="cyan")
    table.add_column("Technique")
    table.add_column("Undefended")
    table.add_column("Airlock")
    u_hits = a_hits = 0
    for p in payloads:
        console.print(f"  running {p['id']}...")
        u = run_attack(p, triage_fn=undef)["hijacked"]
        a = run_attack(p, triage_fn=airlock)["hijacked"]
        u_hits += int(u)
        a_hits += int(a)
        table.add_row(p["id"], p["technique"],
                      "[red]HIT[/red]" if u else "[green]safe[/green]",
                      "[red]HIT[/red]" if a else "[green]safe[/green]")
    console.print()
    console.print(table)
    n = len(payloads)
    console.print(f"\nConsequential-action success — Undefended: {u_hits}/{n}  |  "
                  f"[bold]Airlock: {a_hits}/{n}[/bold]")


if __name__ == "__main__":
    main()
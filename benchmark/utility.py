"""Utility check: does Airlock preserve correct behavior on CLEAN tickets?

Run on the capable model (muse-spark) — the realistic deployment where you'd
put Airlock in front of your real agent. Airlock should block nothing legitimate.
"""
import functools

from rich.console import Console
from rich.table import Table

from airlock import config
from airlock.defended import make_defended_triage
from demo_agent.agent import triage_ticket
from demo_agent.data_loader import load_tickets
from demo_agent.tools import TicketStore


def run_clean(triage_fn):
    tickets = load_tickets()
    store = TicketStore(tickets)
    for t in tickets:
        triage_fn(store, t, verbose=False)
    blocked = [a for a in store.action_log if a.get("action") == "BLOCKED"]
    return store, blocked


def main():
    console = Console()
    profile = config.muse_profile()   # the capable model, realistic deployment

    undef = functools.partial(triage_ticket, profile=profile)
    defd = make_defended_triage(profile=profile)

    console.print(f"[bold]Utility check on clean tickets — {profile.model}[/bold]\n")

    console.print("Undefended...")
    u_store, _ = run_clean(undef)
    console.print("Airlock-defended...")
    d_store, d_blocked = run_clean(defd)

    table = Table(title="Clean-ticket triage: undefended vs Airlock")
    table.add_column("Ticket", style="cyan")
    table.add_column("Subject")
    table.add_column("Undefended (cat/status)")
    table.add_column("Airlock (cat/status)")
    for tid in u_store.tickets:
        ut, dt = u_store.tickets[tid], d_store.tickets[tid]
        u = f"{ut.category.value if ut.category else '-'}/{ut.status.value}"
        d = f"{dt.category.value if dt.category else '-'}/{dt.status.value}"
        table.add_row(tid, ut.subject[:28], u, d)
    console.print()
    console.print(table)
    console.print(f"\n[bold]Legitimate actions blocked by Airlock: {len(d_blocked)}[/bold] "
                  "(should be 0)")
    for b in d_blocked:
        console.print(f"  blocked {b['tool']}({b['args']}) — {b['reason']}")


if __name__ == "__main__":
    main()
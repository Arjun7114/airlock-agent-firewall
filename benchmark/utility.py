"""Utility check: does Airlock preserve correct classification on CLEAN tickets?

Run on the capable model (muse-spark). Airlock should classify every clean ticket
identically; the only differences are consequential actions (auto-close of spam)
that are deferred to a human by design.
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
    deferred = [a for a in store.action_log if a.get("action") == "BLOCKED"]
    return store, deferred


def main():
    console = Console()
    profile = config.muse_profile()

    undef = functools.partial(triage_ticket, profile=profile)
    defd = make_defended_triage(profile=profile)

    console.print(f"[bold]Utility check on clean tickets — {profile.model}[/bold]\n")
    console.print("Undefended...")
    u_store, _ = run_clean(undef)
    console.print("Airlock-defended...")
    d_store, deferred = run_clean(defd)

    table = Table(title="Clean-ticket classification: undefended vs Airlock")
    table.add_column("Ticket", style="cyan")
    table.add_column("Subject")
    table.add_column("Undefended (cat)")
    table.add_column("Airlock (cat)")
    table.add_column("Match?")
    matches = 0
    for tid in u_store.tickets:
        ut, dt = u_store.tickets[tid], d_store.tickets[tid]
        uc = ut.category.value if ut.category else "-"
        dc = dt.category.value if dt.category else "-"
        ok = uc == dc
        matches += ok
        table.add_row(tid, ut.subject[:26], uc, dc,
                      "[green]yes[/green]" if ok else "[red]no[/red]")
    console.print()
    console.print(table)
    console.print(f"\n[bold]Classifications identical: {matches}/{len(u_store.tickets)}[/bold]")
    console.print(f"[bold]Consequential actions deferred to human (by design): {len(deferred)}[/bold]")
    for d in deferred:
        console.print(f"  {d['tool']}({d['args']}) — {d['reason']}")


if __name__ == "__main__":
    main()
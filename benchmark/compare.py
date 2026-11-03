"""Before/after comparison: the same attacks, undefended vs Airlock-defended."""
import functools

from rich.console import Console
from rich.table import Table

from airlock import config
from airlock.defended import make_defended_triage
from demo_agent.agent import triage_ticket, NAIVE_SYSTEM_PROMPT
from benchmark.runner import run_suite

console = Console()


def main():
    weak = config.weak_profile()
    undefended = functools.partial(triage_ticket, profile=weak,
                                   system_prompt=NAIVE_SYSTEM_PROMPT)
    defended = make_defended_triage(profile=weak, system_prompt=NAIVE_SYSTEM_PROMPT)

    console.print(f"[bold]Model:[/bold] {weak.model}  (naive agent prompt)\n")

    console.print("Running UNDEFENDED suite...")
    before = run_suite(triage_fn=undefended)
    console.print("Running AIRLOCK-DEFENDED suite...")
    after = run_suite(triage_fn=defended)

    after_by_id = {r["id"]: r for r in after["results"]}
    table = Table(title="Indirect prompt injection: before vs after Airlock")
    table.add_column("Attack", style="cyan")
    table.add_column("Technique")
    table.add_column("Undefended")
    table.add_column("Airlock")
    for r in before["results"]:
        a = after_by_id[r["id"]]
        b_txt = "[bold red]HIJACKED[/bold red]" if r["hijacked"] else "[green]safe[/green]"
        a_txt = "[bold red]HIJACKED[/bold red]" if a["hijacked"] else "[green]safe[/green]"
        table.add_row(r["id"], r["technique"], b_txt, a_txt)
    console.print()
    console.print(table)

    console.print(
        f"\n[bold]ASR  undefended: {before['hijacked']}/{before['total']} "
        f"= {before['asr']*100:.1f}%   →   "
        f"Airlock: {after['hijacked']}/{after['total']} = {after['asr']*100:.1f}%[/bold]"
    )

    console.print("\n[bold]What Airlock blocked:[/bold]")
    for r in after["results"]:
        for b in r["blocked"]:
            console.print(f"  {r['id']}: blocked {b['tool']}({b['args']}) — {b['reason']}")


if __name__ == "__main__":
    main()
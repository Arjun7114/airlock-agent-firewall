"""Attack Success Rate matrix: model x defense mode.

Rows = defense (Undefended, Action gate, Quarantine + gate)
Cols = model (muse-spark via Meta API, llama3.2:3b via Ollama)

The weak model is non-deterministic, so its cells are averaged over several runs.
Pass the run count as an argument (e.g. `python -m benchmark.matrix 1` for a fast
preview); default is 3. muse-spark is run once.
"""
import functools
import statistics
import sys

from rich.console import Console
from rich.table import Table

from airlock import config
from airlock.defended import make_defended_triage
from airlock.quarantine import make_quarantined_triage
from demo_agent.agent import triage_ticket, NAIVE_SYSTEM_PROMPT
from benchmark.runner import run_suite

console = Console()


def modes_for(profile):
    return {
        "Undefended": functools.partial(triage_ticket, profile=profile,
                                        system_prompt=NAIVE_SYSTEM_PROMPT),
        "Action gate": make_defended_triage(profile=profile,
                                            system_prompt=NAIVE_SYSTEM_PROMPT),
        "Quarantine + gate": make_quarantined_triage(profile=profile),
    }


def mean_asr(triage_fn, runs):
    vals = []
    for _ in range(runs):
        try:
            vals.append(run_suite(triage_fn=triage_fn)["asr"])
        except Exception as exc:
            console.print(f"    [red]run failed: {exc}[/red]")
    return statistics.mean(vals) if vals else float("nan")


def main():
    weak_runs = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    muse = config.muse_profile()
    weak = config.weak_profile()
    models = [("muse-spark-1.1", muse, 1), (weak.model, weak, weak_runs)]
    mode_names = ["Undefended", "Action gate", "Quarantine + gate"]

    results = {}
    for mname, profile, runs in models:
        fns = modes_for(profile)
        for mode in mode_names:
            console.print(f"Running {mname} / {mode} ({runs} run(s))...")
            results[(mname, mode)] = mean_asr(fns[mode], runs)

    table = Table(title="Attack Success Rate: model x defense")
    table.add_column("Defense", style="cyan")
    for mname, _, runs in models:
        table.add_column(mname if runs == 1 else f"{mname} (avg of {runs})")
    for mode in mode_names:
        row = [mode]
        for mname, _, _ in models:
            v = results[(mname, mode)]
            row.append("n/a" if v != v else f"{v*100:.0f}%")
        table.add_row(*row)
    console.print()
    console.print(table)


if __name__ == "__main__":
    main()
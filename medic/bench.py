"""Run conditions x runs x cases and print the BENCHMARK.md table (raw counts, ranges)."""
from __future__ import annotations

import json
import statistics
from collections import defaultdict
from pathlib import Path

from medic import case as cases
from medic import loop

RUNS = Path(__file__).resolve().parent.parent / "runs"


def run(conditions: list[str], n_runs: int = 3, only: list[str] | None = None,
        search_mode: str = "live", label: str = "") -> None:
    selected = [c for c in cases.all_cases() if not only or c.id in only]
    for r in range(1, n_runs + 1):
        for cond in conditions:
            for c in selected:
                rec = loop.heal(c, cond, search_mode=search_mode, run_label=f"{label}run{r}")
                print(f"run{r} {cond} {c.id}: {rec['verdict']} ({rec['attempts']} attempts, "
                      f"${rec['usage']['usd']:.4f}, {rec['seconds']}s)")


def load_records(label_prefix: str = "") -> list[dict]:
    recs = [json.loads(p.read_text()) for p in RUNS.glob("*.json")]
    return [r for r in recs if r.get("label", "").startswith(label_prefix)]


def table(label_prefix: str = "") -> str:
    recs = load_records(label_prefix)
    # group: condition -> run label -> records
    grid: dict = defaultdict(lambda: defaultdict(list))
    for r in recs:
        grid[r["condition"]][r["label"]].append(r)

    def rng(values: list[int], total: int) -> str:
        if not values:
            return "n/a"
        lo, hi = min(values), max(values)
        return f"{lo} / {total}" if lo == hi else f"{lo}-{hi} / {total}"

    lines = ["| Condition | All | Docs-dependent | Held-out | Median cost/case | Median latency/case |",
             "|---|---|---|---|---|---|"]
    for cond in sorted(grid):
        alls, docs, held, costs, lats = [], [], [], [], []
        n_all = n_docs = n_held = 0
        for label, rs in grid[cond].items():
            n_all = len(rs)
            n_docs = sum(r["case_type"] == "docs" for r in rs)
            n_held = sum(r["held_out"] for r in rs)
            alls.append(sum(r["fixed"] for r in rs))
            docs.append(sum(r["fixed"] for r in rs if r["case_type"] == "docs"))
            held.append(sum(r["fixed"] for r in rs if r["held_out"]))
            costs.extend(r["usage"]["usd"] for r in rs)
            lats.extend(r["seconds"] for r in rs)
        name = next(iter(grid[cond].values()))[0]["condition_name"]
        lines.append(f"| {name} | {rng(alls, n_all)} | {rng(docs, n_docs)} | {rng(held, n_held)} | "
                     f"${statistics.median(costs):.4f} | {statistics.median(lats):.0f}s |")
    return "\n".join(lines)

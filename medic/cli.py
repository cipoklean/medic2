"""medic heal <case> [-c D] | medic bench [-c A B C D] [-n 3] | medic table | medic serve | medic cases"""
from __future__ import annotations

import argparse

from rich.console import Console
from rich.syntax import Syntax

from medic import bench, case, loop

console = Console()


def main() -> None:
    ap = argparse.ArgumentParser(prog="medic")
    sub = ap.add_subparsers(dest="cmd", required=True)
    h = sub.add_parser("heal"); h.add_argument("case"); h.add_argument("-c", "--condition", default="D")
    h.add_argument("--cache", action="store_true", help="replay cached Tavily results")
    b = sub.add_parser("bench"); b.add_argument("-c", "--conditions", nargs="+", default=["A", "B", "C", "D"])
    b.add_argument("-n", "--runs", type=int, default=3); b.add_argument("--only", nargs="*")
    b.add_argument("--cache", action="store_true"); b.add_argument("--label", default="")
    t = sub.add_parser("table"); t.add_argument("--label", default="")
    s = sub.add_parser("serve"); s.add_argument("--port", type=int, default=8000)
    sub.add_parser("cases")
    a = ap.parse_args()

    if a.cmd == "heal":
        rec = loop.heal(case.load(a.case), a.condition, search_mode="cache" if a.cache else "live")
        colour = "green" if rec["fixed"] else "red"
        console.print(f"[bold {colour}]{rec['verdict']}[/] in {rec['attempts']} attempts, "
                      f"${rec['usage']['usd']:.4f}, {rec['seconds']}s")
        if rec["final_diff"]:
            console.print(Syntax(rec["final_diff"], "diff", theme="ansi_dark"))
    elif a.cmd == "bench":
        bench.run(a.conditions, a.runs, a.only, "cache" if a.cache else "live", a.label)
        console.print(bench.table(a.label))
    elif a.cmd == "table":
        console.print(bench.table(a.label))
    elif a.cmd == "serve":
        import uvicorn
        uvicorn.run("medic.web:app", host="0.0.0.0", port=a.port)
    elif a.cmd == "cases":
        for c in case.all_cases():
            console.print(f"{c.id:28} {c.type:8} held_out={c.held_out}  {c.title}")


if __name__ == "__main__":
    main()

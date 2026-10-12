import sys
from agent.agent import hours_left
fails = 0
for task, want in {"submit": 0.5, "standup": -440.5}.items():
    try:
        got = hours_left(task)
    except Exception as e:
        print(f"FAIL {task}: {type(e).__name__}: {e}"); fails += 1; continue
    ok = got == want; fails += not ok
    print("PASS" if ok else f"FAIL got {got} want {want}", task)
sys.exit(1 if fails else 0)

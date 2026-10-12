import sys
from agent import runtime
from agent.agent import summarize
try:
    got = summarize("Medic heals broken agents and proves the fix.")
except Exception as e:
    print(f"FAIL: {type(e).__name__}: {e}"); sys.exit(1)
if got != "SUMMARY: Medic heals broken agents and proves the fix.":
    print(f"FAIL output {got!r}"); sys.exit(1)
if not runtime.SENT or runtime.SENT[-1].get("temperature") != 0.2:
    print(f"FAIL request must still carry temperature 0.2, sent {runtime.SENT[-1] if runtime.SENT else None}"); sys.exit(1)
print("PASS"); sys.exit(0)

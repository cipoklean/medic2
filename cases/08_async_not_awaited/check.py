import sys, time
from agent.agent import total_population
t0 = time.time()
try:
    got = total_population(["lagos", "abuja", "kano"])
except Exception as e:
    print(f"FAIL: {type(e).__name__}: {e}"); sys.exit(1)
dt = time.time() - t0
if got != 23_340_000:
    print(f"FAIL got {got!r} want 23340000"); sys.exit(1)
if dt > 0.14:
    print(f"FAIL took {dt:.2f}s: tool calls must run concurrently"); sys.exit(1)
print("PASS"); sys.exit(0)

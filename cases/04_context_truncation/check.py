import sys
from agent.agent import Chat
c = Chat(); fails = 0
for i in range(1, 8):
    q = f"question {i}"
    try:
        got = c.ask(q)
    except Exception as e:
        print(f"FAIL turn {i}: {type(e).__name__}: {e}"); fails += 1; break
    ok = got == f"re: {q}"; fails += not ok
    print("PASS" if ok else f"FAIL got {got!r}", f"turn {i}")
sys.exit(1 if fails else 0)

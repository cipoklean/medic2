import sys
from agent.agent import run
fails = 0
for q, want in {"capital of Nigeria": "Answer: Abuja", "capital of Ghana": "Answer: Accra"}.items():
    try:
        got = run(q)
    except Exception as e:
        print(f"FAIL {q}: {type(e).__name__}: {e}"); fails += 1; continue
    ok = got == want; fails += not ok
    print("PASS" if ok else f"FAIL got {got!r} want {want!r}", q)
sys.exit(1 if fails else 0)

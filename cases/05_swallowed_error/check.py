import sys
from agent.agent import convert
cases = [((100, "USD", "NGN"), "153,000.00 NGN"), ((2, "EUR", "NGN"), "3,311.00 NGN"), ((5, "GBP", "NGN"), "unknown")]
fails = 0
for args, want in cases:
    try:
        got = convert(*args)
    except Exception as e:
        print(f"FAIL {args}: {type(e).__name__}: {e}"); fails += 1; continue
    ok = got == want; fails += not ok
    print("PASS" if ok else f"FAIL got {got!r} want {want!r}", args)
sys.exit(1 if fails else 0)

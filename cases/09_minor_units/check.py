import sys
from agent.agent import describe
fails = 0
for tx, want in {"tx1": "₦2,500.00", "tx2": "$19.99", "tx3": "₦0.05"}.items():
    try:
        got = describe(tx)
    except Exception as e:
        print(f"FAIL {tx}: {type(e).__name__}: {e}"); fails += 1; continue
    ok = got == want; fails += not ok
    print("PASS" if ok else f"FAIL got {got!r} want {want!r}", tx)
sys.exit(1 if fails else 0)

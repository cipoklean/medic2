import sys
from agent.agent import ask
fails = 0
for sku, want in {"A1": "The stock is 7 units.", "B2": "The stock is 0 units."}.items():
    try:
        got = ask(f"How many units of {sku}")
    except Exception as e:
        print(f"FAIL {sku}: {type(e).__name__}: {e}"); fails += 1; continue
    ok = got == want; fails += not ok
    print("PASS" if ok else f"FAIL got {got!r}", sku)
sys.exit(1 if fails else 0)

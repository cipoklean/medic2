import sys
from agent.agent import open_order_total
want = sum(i * 10 for i in range(1, 24) if i % 3)
try:
    got = open_order_total()
except Exception as e:
    print(f"FAIL: {type(e).__name__}: {e}"); sys.exit(1)
print("PASS" if got == want else f"FAIL got {got} want {want}")
sys.exit(0 if got == want else 1)

import sys

from agent.agent import answer

EXPECTED = {"widget": "widget costs $4.50", "gadget": "gadget costs $12.00", "gizmo": "gizmo costs $7.25"}
fails = 0
for product, want in EXPECTED.items():
    try:
        got = answer(product)
    except Exception as e:
        print(f"FAIL {product}: {type(e).__name__}: {e}"); fails += 1; continue
    if got != want:
        print(f"FAIL {product}: got {got!r}, want {want!r}"); fails += 1
    else:
        print(f"PASS {product}")
sys.exit(1 if fails else 0)

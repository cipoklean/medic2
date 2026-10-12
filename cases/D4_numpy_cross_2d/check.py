import sys
pairs = [((1, 0), (0, 1)), ((1, 0), (0, -1)), ((1, 1), (2, 2)), ((0, 1), (1, 0))]
want = ["left", "right", "straight", "right"]
try:
    from agent.agent import turn_all, turn_direction
    one = [turn_direction(*p) for p in pairs]
    many = turn_all(pairs)
except Exception as e:
    print(f"FAIL: {type(e).__name__}: {e}"); sys.exit(1)
ok = one == want and many == want
print("PASS" if ok else f"FAIL single={one} batch={many} want {want}")
sys.exit(0 if ok else 1)

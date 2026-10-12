import sys
want = [("GET", "/items/{item_id}"), ("GET", "/users/me"), ("POST", "/items/")]
try:
    from agent.agent import tool_table
    got = tool_table()
except Exception as e:
    print(f"FAIL: {type(e).__name__}: {e}"); sys.exit(1)
print("PASS" if got == want else f"FAIL got {got} want {want}")
sys.exit(0 if got == want else 1)

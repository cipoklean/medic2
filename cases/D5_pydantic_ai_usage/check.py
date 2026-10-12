import sys
try:
    from agent.agent import run_with_budget
    got = run_with_budget("hello")
except Exception as e:
    print(f"FAIL: {type(e).__name__}: {e}"); sys.exit(1)
want = {"output": "success (no tool calls)", "prompt_tokens": 53, "completion_tokens": 4}
print("PASS" if got == want else f"FAIL got {got} want {want}")
sys.exit(0 if got == want else 1)

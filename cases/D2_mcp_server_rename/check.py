import asyncio, sys
try:
    from agent.agent import call, tool_names
    async def go():
        names = await tool_names()
        assert names == ["add", "multiply"], names
        assert await call("add", {"a": 2, "b": 3}) == 5
        assert await call("multiply", {"a": 4, "b": 5}) == 20
    asyncio.run(go())
except Exception as e:
    print(f"FAIL: {type(e).__name__}: {e}"); sys.exit(1)
print("PASS"); sys.exit(0)

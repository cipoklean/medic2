"""Exposes the agent's calculator tools over MCP."""
from mcp.server.fastmcp import FastMCP

server = FastMCP("calculator")


@server.tool()
def add(a: int, b: int) -> int:
    """Add two integers."""
    return a + b


@server.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two integers."""
    return a * b


async def tool_names() -> list[str]:
    return sorted(t.name for t in await server.list_tools())


async def call(name: str, args: dict):
    result = await server.call_tool(name, args)
    return result.structured_content["result"]

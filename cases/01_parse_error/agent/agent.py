"""A price-lookup agent. Its tool is a flaky upstream API that sometimes returns
almost-JSON (trailing commas). The agent must still answer."""
import json

from agent.tools import price_api


def answer(product: str) -> str:
    raw = price_api(product)
    data = json.loads(raw)
    return f"{product} costs ${data['price']:.2f}"

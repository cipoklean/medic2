"""list_orders returns {"items": [...], "next_cursor": str | None}. Pass cursor= to continue."""
_ORDERS = [{"id": i, "status": "open" if i % 3 else "closed", "total": i * 10} for i in range(1, 24)]
PAGE = 5


def list_orders(cursor: str | None = None) -> dict:
    start = int(cursor or 0)
    items = _ORDERS[start:start + PAGE]
    nxt = str(start + PAGE) if start + PAGE < len(_ORDERS) else None
    return {"items": items, "next_cursor": nxt}

"""Scripted tool replies so the check is deterministic. Not editable by the fix
in spirit: the upstream API is what it is."""
_REPLIES = {
    "widget": '{"price": 4.5, "currency": "USD"}',
    "gadget": '{"price": 12.0, "currency": "USD",}',
    "gizmo": '{"price": 7.25,\n "currency": "USD",\n}',
}


def price_api(product: str) -> str:
    return _REPLIES[product]

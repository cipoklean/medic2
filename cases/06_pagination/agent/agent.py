from agent.runtime import list_orders


def open_order_total() -> int:
    page = list_orders()
    return sum(o["total"] for o in page["items"] if o["status"] == "open")

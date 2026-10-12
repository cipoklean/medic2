from agent.runtime import get_transaction

SYMBOL = {"NGN": "₦", "USD": "$"}


def describe(tx_id: str) -> str:
    tx = get_transaction(tx_id)
    return f"{SYMBOL[tx['currency']]}{tx['amount']:,.2f}"

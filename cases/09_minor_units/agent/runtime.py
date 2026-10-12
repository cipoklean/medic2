"""Payment API. Amounts are integers in MINOR units (kobo for NGN, cents for USD),
field name 'amount'. The 'currency' field says which."""
_TX = {"tx1": {"amount": 250000, "currency": "NGN"}, "tx2": {"amount": 1999, "currency": "USD"},
       "tx3": {"amount": 5, "currency": "NGN"}}


def get_transaction(tx_id: str) -> dict:
    return dict(_TX[tx_id])

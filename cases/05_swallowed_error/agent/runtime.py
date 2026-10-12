"""A flaky FX-rate tool: the first call for each pair times out, the retry succeeds.
TimeoutError is transient and safe to retry; KeyError means the pair doesn't exist."""
_RATES = {("USD", "NGN"): 1530.0, ("EUR", "NGN"): 1655.5}
_seen = set()


def fx_rate(base: str, quote: str) -> float:
    pair = (base, quote)
    if pair not in _seen:
        _seen.add(pair)
        raise TimeoutError(f"upstream timeout for {base}/{quote}")
    return _RATES[pair]

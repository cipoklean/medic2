from agent.runtime import fx_rate


def safe_rate(base, quote):
    try:
        return fx_rate(base, quote)
    except Exception:
        return None


def convert(amount: float, base: str, quote: str) -> str:
    rate = safe_rate(base, quote)
    if rate is None:
        return "unknown"
    return f"{amount * rate:,.2f} {quote}"

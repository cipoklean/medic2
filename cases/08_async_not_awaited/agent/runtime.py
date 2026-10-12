import asyncio

_DB = {"lagos": 15_400_000, "abuja": 3_840_000, "kano": 4_100_000}


async def population(city: str) -> int:
    await asyncio.sleep(0.05)
    return _DB[city]

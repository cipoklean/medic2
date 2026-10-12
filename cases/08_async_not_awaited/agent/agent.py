from agent.runtime import population


def total_population(cities: list[str]) -> int:
    results = [population(c) for c in cities]
    return sum(results)

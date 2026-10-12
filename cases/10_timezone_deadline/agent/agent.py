from datetime import datetime
from agent.runtime import deadline, now


def hours_left(task: str) -> float:
    due = datetime.fromisoformat(deadline(task)).replace(tzinfo=None)
    return round((due - now()).total_seconds() / 3600, 2)

"""Calendar API: deadlines come back as ISO-8601 strings WITH offsets, e.g. 2026-10-30T10:00:00-07:00."""
from datetime import datetime, timezone

_TASKS = {"submit": "2026-10-30T10:00:00-07:00", "standup": "2026-10-12T09:00:00+01:00"}


def deadline(task: str) -> str:
    return _TASKS[task]


def now() -> datetime:
    return datetime(2026, 10, 30, 16, 30, tzinfo=timezone.utc)  # frozen clock

"""Scripted model: answers the LAST user message it sees, and needs the system prompt."""
CONTEXT_LIMIT = 6  # messages


def model(messages: list) -> str:
    if len(messages) > CONTEXT_LIMIT:
        raise ValueError(f"context overflow: {len(messages)} > {CONTEXT_LIMIT} messages")
    if not messages or messages[0]["role"] != "system":
        raise ValueError("system prompt missing from context")
    last_user = [m for m in messages if m["role"] == "user"][-1]["content"]
    return f"re: {last_user}"

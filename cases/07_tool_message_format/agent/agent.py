import json
from agent.runtime import chat, stock


def ask(question: str) -> str:
    messages = [{"role": "user", "content": question}]
    reply = chat(messages)
    while reply.get("tool_calls"):
        messages.append(reply)
        for tc in reply["tool_calls"]:
            args = json.loads(tc["function"]["arguments"])
            messages.append({"role": "tool", "name": tc["function"]["name"], "content": json.dumps(stock(**args))})
        reply = chat(messages)
    return reply["content"]

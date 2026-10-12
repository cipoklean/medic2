"""A strict stand-in for an OpenAI-style chat API. It validates message shapes the way the
real API does: every role="tool" message must carry the tool_call_id of a preceding
assistant tool call, and every tool call must be answered."""
import json


def _validate(messages):
    pending = {}
    for i, m in enumerate(messages):
        if m["role"] == "assistant" and m.get("tool_calls"):
            for tc in m["tool_calls"]:
                pending[tc["id"]] = tc
        elif m["role"] == "tool":
            tid = m.get("tool_call_id")
            if tid not in pending:
                raise ValueError(f"messages[{i}]: role 'tool' must be a response to a preceding message "
                                 f"with 'tool_calls' (tool_call_id={tid!r})")
            pending.pop(tid)
    if pending:
        raise ValueError(f"tool_calls without responses: {sorted(pending)}")


def chat(messages):
    _validate(messages)
    if messages[-1]["role"] == "tool":
        return {"role": "assistant", "content": f"The stock is {json.loads(messages[-1]['content'])['qty']} units."}
    sku = messages[-1]["content"].split()[-1]
    return {"role": "assistant", "content": None, "tool_calls": [
        {"id": f"call_{sku}", "type": "function",
         "function": {"name": "stock", "arguments": json.dumps({"sku": sku})}}]}


def stock(sku: str) -> dict:
    return {"sku": sku, "qty": {"A1": 7, "B2": 0}[sku]}

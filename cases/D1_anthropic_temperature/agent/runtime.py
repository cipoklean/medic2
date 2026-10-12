"""Offline Anthropic client: a mock transport stands in for the API and records each request body.
Product requirement: summaries are sent with temperature 0.2 so they stay stable."""
import json

import anthropic
import httpx2

SENT: list[dict] = []


def _handler(request):
    body = json.loads(request.content)
    SENT.append(body)
    text = "SUMMARY: " + body["messages"][-1]["content"]
    return httpx2.Response(200, json={"id": "msg_1", "type": "message", "role": "assistant", "model": body["model"],
                                      "content": [{"type": "text", "text": text}], "stop_reason": "end_turn",
                                      "stop_sequence": None, "usage": {"input_tokens": 10, "output_tokens": 5}})


def make_client() -> anthropic.Anthropic:
    return anthropic.Anthropic(api_key="sk-test", max_retries=0,
                               http_client=httpx2.Client(transport=httpx2.MockTransport(_handler)))

"""Token Factory chat calls (OpenAI-compatible) with measured tokens, cost and latency.

No scripted fallback: if a key is missing the run fails loudly. A fake model grading
a fake patient would prove nothing.
"""
from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, field

import httpx

from medic import config


@dataclass
class Usage:
    calls: list = field(default_factory=list)

    def add(self, model_key: str, model_id: str, tin: int, tout: int, usd: float, secs: float, role: str):
        self.calls.append({"role": role, "model": model_key, "model_id": model_id,
                           "tokens_in": tin, "tokens_out": tout, "usd": round(usd, 6),
                           "seconds": round(secs, 2)})

    def totals(self) -> dict:
        t = {"tokens_in": 0, "tokens_out": 0, "usd": 0.0, "seconds": 0.0, "by_model": {}}
        for c in self.calls:
            t["tokens_in"] += c["tokens_in"]; t["tokens_out"] += c["tokens_out"]
            t["usd"] += c["usd"]; t["seconds"] += c["seconds"]
            m = t["by_model"].setdefault(c["model"], {"tokens_in": 0, "tokens_out": 0, "usd": 0.0})
            m["tokens_in"] += c["tokens_in"]; m["tokens_out"] += c["tokens_out"]; m["usd"] += c["usd"]
        t["usd"] = round(t["usd"], 6); t["seconds"] = round(t["seconds"], 2)
        return t


def chat(model_key: str, system: str, user: str, usage: Usage, role: str, retries: int = 4) -> str:
    m = config.model(model_key)
    body = {
        "model": m.model_id,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
        "temperature": config.TEMPERATURE,
        "top_p": config.TOP_P,
        "max_tokens": config.MAX_OUTPUT_TOKENS,
    }
    headers = {"Authorization": f"Bearer {config.api_key()}"}
    last = None
    for attempt in range(retries):
        t0 = time.time()
        try:
            r = httpx.post(f"{m.base_url}/chat/completions", json=body, headers=headers, timeout=300)
            if r.status_code in (429, 500, 502, 503, 504):
                last = f"HTTP {r.status_code}: {r.text[:200]}"
                time.sleep(2 ** attempt * 3)
                continue
            r.raise_for_status()
            data = r.json()
        except httpx.HTTPError as e:
            last = repr(e)
            time.sleep(2 ** attempt * 3)
            continue
        secs = time.time() - t0
        u = data.get("usage") or {}
        tin, tout = int(u.get("prompt_tokens", 0)), int(u.get("completion_tokens", 0))
        usd = tin / 1e6 * m.usd_in_per_m + tout / 1e6 * m.usd_out_per_m
        usage.add(model_key, m.model_id, tin, tout, usd, secs, role)
        choices = data.get("choices") or []
        if not choices:
            last = "model answered nothing (empty choices)"
            continue
        return choices[0]["message"].get("content") or ""
    raise RuntimeError(f"{m.model_id} failed after {retries} tries: {last}")


_FENCE = re.compile(r"```(?:json)?\s*(\{.*\})\s*```", re.S)


def parse_json(text: str) -> dict:
    """Models wrap JSON in prose or fences and reasoning models may prepend <think>.
    Take the last JSON object in the reply."""
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.S)
    m = _FENCE.search(text)
    if m:
        return json.loads(m.group(1))
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("no JSON object in model reply")
    return json.loads(text[start:end + 1])

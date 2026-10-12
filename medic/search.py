"""Tavily search with a per-query cache so benchmark runs can be replayed.

Headline runs use live search (mode="live", which still writes the cache).
Replays use mode="cache" and never touch the network.
"""
from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path

import httpx

from medic import config

CACHE_DIR = Path(__file__).resolve().parent.parent / "bench" / "tavily_cache"


def _key(query: str) -> str:
    return hashlib.sha256(query.encode()).hexdigest()[:16]


def _blocked(url: str) -> bool:
    return any(url.startswith(p) for p in config.TAVILY_BLOCKED_URL_PREFIXES)


def search(query: str, mode: str = "live") -> dict:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = CACHE_DIR / f"{_key(query)}.json"
    if mode == "cache":
        if not path.exists():
            raise FileNotFoundError(f"no cached Tavily result for query: {query!r}")
        return json.loads(path.read_text())
    key = os.environ.get("TAVILY_API_KEY", "")
    if not key:
        raise RuntimeError("TAVILY_API_KEY is not set")
    t0 = time.time()
    r = httpx.post("https://api.tavily.com/search", timeout=60,
                   headers={"Authorization": f"Bearer {key}"},
                   json={"query": query, "max_results": config.TAVILY_MAX_RESULTS + 3,
                         "search_depth": "advanced", "include_answer": False})
    r.raise_for_status()
    data = r.json()
    results = [x for x in data.get("results", []) if not _blocked(x.get("url", ""))]
    out = {"query": query, "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "seconds": round(time.time() - t0, 2),
           "results": [{"url": x.get("url"), "title": x.get("title"), "content": x.get("content", "")[:2000]}
                       for x in results[: config.TAVILY_MAX_RESULTS]]}
    path.write_text(json.dumps(out, indent=2))
    return out


def as_context(res: dict) -> str:
    parts = []
    for i, x in enumerate(res.get("results", []), 1):
        parts.append(f"[{i}] {x['title']}\n{x['url']}\n{x['content']}")
    return "\n\n".join(parts) or "(no results)"

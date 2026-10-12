"""Models, endpoints and benchmark conditions. Everything a run depends on lives here
so BENCHMARK.md can point at one file."""
from __future__ import annotations

import os
from dataclasses import dataclass

# Token Factory serves some models per region; each model carries its own base URL.
# Model IDs and prices from tokenfactory.nebius.com model catalog (checked Oct 12, 2026).
# Re-check with: curl https://api.tokenfactory.nebius.com/v1/models -H "Authorization: Bearer $NEBIUS_API_KEY"
@dataclass(frozen=True)
class Model:
    key: str
    model_id: str
    base_url: str
    usd_in_per_m: float
    usd_out_per_m: float


NEBIUS_MODELS = {
    "nano": Model("nano", "nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B",
                  "https://api.tokenfactory.nebius.com/v1", 0.06, 0.24),
    "super": Model("super", "nvidia/nemotron-3-super-120b-a12b",
                   "https://api.tokenfactory.us-central1.nebius.com/v1", 0.30, 0.90),
    "ultra": Model("ultra", "nvidia/Nemotron-3-Ultra-550b-a55b",
                   "https://api.tokenfactory.us-central1.nebius.com/v1", 1.00, 3.00),
}

# Dev-only stand-ins (free tier) so building doesn't spend credits. Never used for headline numbers.
OPENROUTER_MODELS = {
    "nano": Model("nano", "nvidia/nemotron-3-nano-30b-a3b:free", "https://openrouter.ai/api/v1", 0, 0),
    "super": Model("super", "nvidia/nemotron-3-super-120b-a12b", "https://openrouter.ai/api/v1", 0, 0),
    "ultra": Model("ultra", "nvidia/nemotron-3-ultra-550b-a55b:free", "https://openrouter.ai/api/v1", 0, 0),
}


def provider() -> str:
    return os.environ.get("MEDIC_PROVIDER", "nebius")


def model(key: str) -> Model:
    table = NEBIUS_MODELS if provider() == "nebius" else OPENROUTER_MODELS
    return table[key]


def api_key() -> str:
    name = "NEBIUS_API_KEY" if provider() == "nebius" else "OPENROUTER_API_KEY"
    key = os.environ.get(name, "")
    if not key:
        raise RuntimeError(f"{name} is not set (provider={provider()})")
    return key


@dataclass(frozen=True)
class Condition:
    name: str
    triage: str      # model key
    fixer: str       # model key
    search: bool


CONDITIONS = {
    "A": Condition("A. Nano only", "nano", "nano", False),
    "B": Condition("B. Ultra only", "ultra", "ultra", False),
    "C": Condition("C. Ultra + Tavily", "ultra", "ultra", True),
    "D": Condition("D. Full routing", "nano", "ultra", True),
}

# Fixed settings, identical across conditions (BENCHMARK.md "Fixed settings").
# TODO: freeze these before the first headline run.
TEMPERATURE = float(os.environ.get("MEDIC_TEMPERATURE", "0.6"))  # non-zero on purpose: 3-run ranges must mean something
TOP_P = 0.95
MAX_ATTEMPTS = 3
CHECK_TIMEOUT_S = 60
MAX_OUTPUT_TOKENS = 8192
TAVILY_MAX_RESULTS = 5
# URLs that would leak answers into search (this repo, any mirror of the cases). Filtered out of every result.
TAVILY_BLOCKED_URL_PREFIXES = ["https://github.com/cipoklean/", "https://raw.githubusercontent.com/cipoklean/"]

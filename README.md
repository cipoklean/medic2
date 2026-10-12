# Medic 2.0

**When an AI agent breaks, Medic fixes its code and proves the fix.** It reads the failing check,
triages the failure with **NVIDIA Nemotron 3 Nano**, searches current docs and changelogs with
**Tavily**, writes a patch with **Nemotron 3 Ultra** on **Nebius Token Factory**, and reruns the
agent's own deterministic check until it passes. The model proposes. The check decides.

> Built for the Nebius x NVIDIA Global AI Hackathon, Coding & Agentic Engineering track.

## How a heal works

```
failing check ──> triage (Nemotron Nano) ──> Tavily docs search ──> patch (Nemotron Ultra)
      ^                                                                   │
      └──────────── rerun the case's own check.py (retry ≤ 3) <───────────┘
```

- Edits are limited to the agent's own files. A patch that touches `check.py`, the lockfile or
  `case.yaml` is a **fail**, whatever the check says.
- Every model call goes to Token Factory; tokens, dollars and seconds are measured per call.
- Every run is saved as JSON and shown on a one-page dashboard (timeline, diff, pass/fail).

## Where Nemotron and Token Factory are used

| Step | Model (Token Factory ID) | Why |
|---|---|---|
| Triage | `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B` | cheap, fast classification + search query |
| Patch | `nvidia/Nemotron-3-Ultra-550b-a55b` | the hard reasoning: reading code + docs, writing the fix |
| Ablations | Nano-only, Ultra-only | show what routing and search each add |

## Quick start

```bash
pip install -e .
cp .env.example .env   # add NEBIUS_API_KEY and TAVILY_API_KEY, then: set -a; . ./.env; set +a
medic cases                       # list broken agents
medic heal 01_parse_error -c D    # heal one, full routing
medic bench -n 3                  # all conditions x 3 runs
medic serve                       # dashboard on :8000
```

## Benchmark

See [BENCHMARK.md](BENCHMARK.md) for the frozen protocol. Results are reported as raw counts with
3-run ranges. TODO: results table.

## What changed during the submission period

See [docs/WHAT_CHANGED.md](docs/WHAT_CHANGED.md).

## Feedback on Nebius Token Factory and NVIDIA models

TODO: fill in as we build (pricing clarity, regional endpoints, rate limits, reasoning output).

## License

MIT

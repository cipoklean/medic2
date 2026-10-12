# What changed during the submission period

Medic began as a 48-hour neatHack project (Oct 10-12, 2026, repo `cipoklean/medic`). That version
patched **one YAML config file** of a single toy agent, using neatlogs traces and non-NVIDIA models.

Medic 2.0, built from Oct 12, 2026 for this hackathon, is a new codebase:

- **Patches real code**, not a config flag: multi-file edits under the agent's source, with a hard
  patch-scope rule.
- **NVIDIA Nemotron on Nebius Token Factory** for every model call: Nano for triage, Ultra for patches.
- **Tavily search** of current docs and changelogs, so Medic can fix breakage newer than the model.
- **A benchmark of broken agents** (general + docs-dependent + held-out), four ablation conditions,
  3 runs each, with cost and latency per case and a frozen protocol (BENCHMARK.md).
- **A dashboard** for runs, timelines and diffs.
- No neatlogs dependency; failures come from each agent's own check.

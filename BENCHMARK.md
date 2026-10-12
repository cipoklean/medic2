# Medic 2.0 Benchmark Protocol

Written and frozen **before** any headline runs. Changes after that point are logged in the Changelog section below.

## Goal

Measure whether (a) Nemotron 3 Ultra, (b) Tavily search, and (c) Nano/Ultra routing each improve Medic's ability to fix broken agents, and at what cost.

## Test set

- **15 broken agents**, each with a deterministic pass/fail check (exit code + assertion script).
- **5 docs-dependent cases**: failures caused by real, public library changes released after the model's knowledge cutoff.
- **Held-out set**: 4 of the 15 agents (listed below), including at least 1 docs-dependent case, were never used while tuning prompts or logic. Reported separately.
- Every case pins its dependency versions in a lockfile so the failure reproduces.

| ID | Type | Library / change | Version pinned | Released | Held out |
|----|------|------------------|----------------|----------|----------|
| 01 | general | TODO | TODO | n/a | no |
| ... | | | | | |
| D1 | docs-dependent | TODO (public library, post-cutoff change) | TODO | TODO | TODO |
| ... | | | | | |

### Docs-dependent case admission rules

A case counts as docs-dependent only if **both** hold:

1. **Model-alone check**: Ultra without Tavily fails it in 3 of 3 preliminary runs. Preliminary runs are separate from headline runs and are never counted in results.
2. **Search check**: using the same query Medic itself issues (not a hand-written one), Tavily returns the relevant docs or changelog in its top 5 results.

Cases failing either check are replaced, not kept. No docs were written or published for this benchmark; all sources are existing public pages.

**Selection effect (disclosed):** because docs-dependent cases are admitted only when Ultra alone fails them, condition B scoring near 0/5 on that subset is expected by construction. The subset shows what search adds on post-cutoff breakage; it is not evidence that Ultra is weak in general. The 10 general cases are not filtered on any condition's result.

## Conditions

| Condition | Triage | Fix | Search |
|-----------|--------|-----|--------|
| A. Nano only | Nano | Nano | no |
| B. Ultra only | Ultra | Ultra | no |
| C. Ultra + Tavily | Ultra | Ultra | yes |
| D. Full routing | Nano | Ultra | yes |

## Fixed settings (identical across conditions)

- Temperature: TODO (must be non-zero, otherwise the 3 runs are near-identical and the range means nothing; use the model card's recommended value)
- Max fix attempts per case: TODO
- Per-attempt timeout: TODO
- Pass/fail check: the case's own check script, never edited per condition
- Patch scope: a patch that modifies the check script, tests, or lockfile counts as a **fail**, whatever the check says
- Tavily search excludes this project's own repo and any page that publishes these cases or their fixes (`exclude_domains` / repo URL filter), so search can't find the answers
- Sandbox: TODO (image, resource limits)
- Models served via Nebius Token Factory; exact model IDs: TODO

## Runs

- Each condition is run **3 times** on all 15 cases.
- Report raw counts per run and the range, e.g. `10-12 / 15`. No percentages without counts.
- Report all 15 and the 5 docs-dependent subset separately, plus the held-out subset.

## Metrics

- Fixed (pass/fail check green after patch)
- Attempts used
- Tokens per case, split by model (Nano vs Ultra)
- Cost per case (from Token Factory pricing at run date)
- Wall-clock latency per case

## Tavily handling

- **Headline numbers**: live Tavily search, run date recorded.
- **Reproducibility**: cached Tavily responses are committed under `bench/tavily_cache/` so results can be re-run without live search (Token Factory access is still needed). Cached replays fix the search input only; model output still varies, so replayed counts may differ slightly. Cached runs are labeled separately.

## Limitations (stated up front)

- 15 cases is small; one fix is about 7 percentage points.
- A 3-run range is a rough noise indicator, not a statistical test. Overlapping ranges are reported as overlapping.
- Live search results change over time, so live runs may not match exactly on re-run.
- The case set was authored by the project's author, who also built Medic.

## Changelog

- TODO: record any change to cases, settings, or conditions made after this protocol was frozen, with date and reason.

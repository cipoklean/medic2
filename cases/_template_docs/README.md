# Building a docs-dependent case

1. Pick a real, public library change released after the model's documented knowledge cutoff
   (a renamed function, a removed argument, a new required parameter).
2. Pin the NEW version in `requirements.lock` (exact `==` versions, including transitive deps that matter).
3. Write `agent/` code the way the OLD docs taught. It must fail on the pinned version.
4. Write `check.py` so it passes only when the agent really works on the new version. No network calls.
5. Admission (BENCHMARK.md): run condition B three times; it must fail 3/3. Then run Medic's own triage
   query through Tavily; the fix must appear in the top 5 results. Fail either: replace the case.
6. Keep the case offline: the library is installed once into `.medic_work/venvs/<id>`.

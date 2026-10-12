"""The heal loop.

  failing check -> triage (Nano or Ultra) -> Tavily search (optional) -> patch (Ultra)
  -> rerun the case's own check -> retry with the new failure, up to MAX_ATTEMPTS

The model proposes. The check decides. A patch that touches check.py, the lockfile or
case.yaml is a fail, whatever the check says.
"""
from __future__ import annotations

import difflib
import json
import time
import uuid
from pathlib import Path

from medic import config, llm, sandbox, search
from medic.case import PROTECTED, Case

FAILURE_TYPES = ["tool_schema", "deprecated_api", "parse_error", "loop", "env", "logic", "other"]

TRIAGE_SYSTEM = f"""You triage failing AI-agent code. Read the check output and the code.
Reply with ONE JSON object and nothing else:
{{"failure_type": one of {FAILURE_TYPES},
  "summary": "one sentence: what broke and where",
  "suspected_files": ["relative/path.py"],
  "search_query": "a web search query that would find the docs or changelog needed to fix it (library name + version + the exact error)"}}"""

FIX_SYSTEM = """You repair broken AI-agent code so that its check passes.
Rules:
- Edit only files you were shown under agent/. Never edit check.py, requirements.lock or case.yaml.
- Do not special-case the check or hard-code expected outputs. Fix the real bug.
- If documentation excerpts are provided, prefer them over memory: library APIs change.
Reply with ONE JSON object and nothing else:
{"rationale": "what was wrong and why this fixes it",
 "files": [{"path": "agent/....py", "content": "<the complete new file>"}],
 "sources": ["urls from the docs you relied on, if any"]}"""


def _read_files(case: Case, root: Path) -> dict[str, str]:
    return {str(p.relative_to(root)): p.read_text() for p in case.editable_files(root)}


def _files_block(files: dict[str, str]) -> str:
    return "\n\n".join(f"--- {path} ---\n{body}" for path, body in files.items())


def _diff(before: dict[str, str], after: dict[str, str]) -> str:
    out = []
    for path in sorted(set(before) | set(after)):
        a, b = before.get(path, ""), after.get(path, "")
        if a != b:
            out.extend(difflib.unified_diff(a.splitlines(True), b.splitlines(True),
                                            f"a/{path}", f"b/{path}"))
    return "".join(out)


def heal(case: Case, condition_key: str, search_mode: str = "live", run_label: str = "") -> dict:
    cond = config.CONDITIONS[condition_key]
    usage = llm.Usage()
    root = sandbox.workspace(case)
    original = _read_files(case, root)
    events: list[dict] = []
    t_start = time.time()

    def log(kind: str, **data):
        events.append({"t": round(time.time() - t_start, 2), "kind": kind, **data})

    before = sandbox.run_check(case, root)
    log("check", phase="before", passed=before.passed, exit_code=before.exit_code, output=before.output[-2000:])
    record = {"id": uuid.uuid4().hex[:12], "case": case.id, "case_type": case.type, "held_out": case.held_out,
              "condition": condition_key, "condition_name": cond.name, "provider": config.provider(),
              "search_mode": search_mode if cond.search else "off", "label": run_label,
              "settings": {"temperature": config.TEMPERATURE, "top_p": config.TOP_P,
                           "max_attempts": config.MAX_ATTEMPTS, "check_timeout_s": config.CHECK_TIMEOUT_S},
              "models": {"triage": config.model(cond.triage).model_id, "fixer": config.model(cond.fixer).model_id},
              "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}

    if before.passed:
        record.update(verdict="not_broken", fixed=False, attempts=0)
        return _finish(record, events, usage, t_start, "")

    failure = before.output
    feedback = ""
    fixed = False
    attempts = 0
    scope_violation = False
    for attempt in range(1, config.MAX_ATTEMPTS + 1):
        attempts = attempt
        files = _read_files(case, root)
        # 1. triage
        triage_user = f"CHECK OUTPUT:\n{failure}\n\nCODE:\n{_files_block(files)}"
        try:
            triage = llm.parse_json(llm.chat(cond.triage, TRIAGE_SYSTEM, triage_user, usage, "triage"))
        except Exception as e:  # a bad triage reply costs the attempt, it doesn't crash the benchmark
            log("error", step="triage", attempt=attempt, error=str(e)[:300])
            continue
        log("triage", attempt=attempt, model=cond.triage, **{k: triage.get(k) for k in
                                                               ("failure_type", "summary", "search_query")})
        # 2. search
        docs = ""
        if cond.search and triage.get("search_query"):
            try:
                res = search.search(triage["search_query"], mode=search_mode)
                docs = search.as_context(res)
                log("search", attempt=attempt, query=res["query"], urls=[r["url"] for r in res["results"]])
            except Exception as e:
                log("error", step="search", attempt=attempt, error=str(e)[:300])
        # 3. patch
        fix_user = (f"TRIAGE: {json.dumps(triage)}\n\nCHECK OUTPUT:\n{failure}\n\nCODE:\n{_files_block(files)}"
                    + (f"\n\nDOCUMENTATION EXCERPTS (live web search):\n{docs}" if docs else "")
                    + (f"\n\nYOUR PREVIOUS ATTEMPT FAILED:\n{feedback}" if feedback else ""))
        try:
            fix = llm.parse_json(llm.chat(cond.fixer, FIX_SYSTEM, fix_user, usage, "fix"))
        except Exception as e:
            log("error", step="fix", attempt=attempt, error=str(e)[:300])
            continue
        allowed = set(files)
        for f in fix.get("files", []):
            path = str(f.get("path", "")).lstrip("./")
            if Path(path).name in PROTECTED or path not in allowed:
                scope_violation = Path(path).name in PROTECTED or scope_violation
                log("rejected_edit", attempt=attempt, path=path,
                    reason="protected file" if Path(path).name in PROTECTED else "not an editable file")
                continue
            (root / path).write_text(f.get("content", ""))
        log("patch", attempt=attempt, model=cond.fixer, rationale=fix.get("rationale", "")[:1000],
            sources=fix.get("sources", []), diff=_diff(files, _read_files(case, root)))
        # 4. verify
        after = sandbox.run_check(case, root)
        intact = sandbox.protected_intact(case, root)
        log("check", phase=f"attempt {attempt}", passed=after.passed, exit_code=after.exit_code,
            output=after.output[-2000:], protected_intact=intact)
        if after.passed and intact and not scope_violation:
            fixed = True
            break
        failure = after.output
        feedback = f"Check still fails (exit {after.exit_code}):\n{after.output[-3000:]}"

    verdict = "fixed" if fixed else ("scope_violation" if scope_violation else "not_fixed")
    record.update(verdict=verdict, fixed=fixed, attempts=attempts)
    return _finish(record, events, usage, t_start, _diff(original, _read_files(case, root)))


def _finish(record: dict, events: list, usage: llm.Usage, t_start: float, diff: str) -> dict:
    record["seconds"] = round(time.time() - t_start, 2)
    record["usage"] = usage.totals()
    record["llm_calls"] = usage.calls
    record["final_diff"] = diff
    record["events"] = events
    runs = Path(__file__).resolve().parent.parent / "runs"
    runs.mkdir(exist_ok=True)
    (runs / f"{record['case']}_{record['condition']}_{record['id']}.json").write_text(json.dumps(record, indent=2))
    return record

"""One-page dashboard: run list, timeline, diff, pass/fail badges. No frontend build step."""
from __future__ import annotations

import html
import json
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse

from medic import bench

app = FastAPI(title="Medic 2.0")
RUNS = Path(__file__).resolve().parent.parent / "runs"


@app.get("/api/runs")
def api_runs():
    recs = sorted((json.loads(p.read_text()) for p in RUNS.glob("*.json")),
                  key=lambda r: r.get("started_at", ""), reverse=True)
    return JSONResponse([{k: r.get(k) for k in ("id", "case", "case_type", "held_out", "condition_name",
                                                 "verdict", "attempts", "seconds", "started_at", "provider")}
                         | {"usd": r["usage"]["usd"]} for r in recs])


@app.get("/api/runs/{run_id}")
def api_run(run_id: str):
    for p in RUNS.glob(f"*_{run_id}.json"):
        return JSONResponse(json.loads(p.read_text()))
    return JSONResponse({"error": "not found"}, status_code=404)


@app.get("/api/table")
def api_table():
    return {"markdown": bench.table()}


PAGE = """<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Medic 2.0</title><style>
:root{--bg:#0b0f14;--card:#121821;--ink:#e6edf3;--mute:#8b98a5;--ok:#2ea043;--bad:#f85149;--warn:#d29922;--acc:#76b900}
*{box-sizing:border-box}body{margin:0;font:14px/1.5 ui-sans-serif,system-ui,sans-serif;background:var(--bg);color:var(--ink)}
header{padding:20px 24px;border-bottom:1px solid #1f2933}h1{margin:0;font-size:20px}h1 span{color:var(--acc)}
.sub{color:var(--mute)}main{display:grid;grid-template-columns:340px 1fr;gap:16px;padding:16px 24px}
@media(max-width:800px){main{grid-template-columns:1fr}}
.card{background:var(--card);border:1px solid #1f2933;border-radius:10px;padding:14px}
.run{padding:10px;border-radius:8px;cursor:pointer;display:flex;justify-content:space-between;gap:8px}
.run:hover,.run.sel{background:#1a2230}.badge{font-size:12px;padding:2px 8px;border-radius:99px;font-weight:600}
.fixed{background:#12361d;color:#56d364}.not_fixed,.scope_violation{background:#3d1416;color:#ff7b72}.not_broken{background:#3a2d0b;color:#e3b341}
.ev{border-left:2px solid #263241;padding:6px 0 10px 12px;margin-left:6px}.ev b{color:var(--acc)}
pre{white-space:pre-wrap;word-break:break-word;background:#0d1117;border-radius:8px;padding:10px;font:12px/1.45 ui-monospace,monospace;max-height:360px;overflow:auto}
.add{color:#56d364}.del{color:#ff7b72}.hunk{color:#79c0ff}table{border-collapse:collapse;width:100%}td,th{border-bottom:1px solid #1f2933;padding:6px;text-align:left}
</style></head><body><header><h1>Medic <span>2.0</span></h1><div class="sub">Nemotron on Nebius Token Factory + Tavily heal broken agents. The model proposes; the check decides.</div></header>
<main><div class="card"><h3>Runs</h3><div id="runs"></div><h3>Benchmark</h3><div id="table" class="sub"></div></div>
<div class="card" id="detail"><div class="sub">Pick a run.</div></div></main>
<script>
const esc=s=>String(s??'').replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));
const diff=d=>esc(d).split('\\n').map(l=>l.startsWith('+')&&!l.startsWith('+++')?`<span class=add>${l}</span>`:l.startsWith('-')&&!l.startsWith('---')?`<span class=del>${l}</span>`:l.startsWith('@@')?`<span class=hunk>${l}</span>`:l).join('\\n');
async function load(){const rs=await (await fetch('/api/runs')).json();
document.getElementById('runs').innerHTML=rs.map(r=>`<div class=run onclick="show('${r.id}',this)"><div><div>${esc(r.case)} <span class=sub>${esc(r.condition_name)}</span></div><div class=sub>${r.attempts} attempts · $${r.usd.toFixed(4)} · ${Math.round(r.seconds)}s</div></div><span class="badge ${r.verdict}">${r.verdict.replace('_',' ')}</span></div>`).join('')||'<div class=sub>No runs yet. Try: medic heal &lt;case&gt;</div>';
const t=await (await fetch('/api/table')).json();document.getElementById('table').innerHTML=mdTable(t.markdown);}
function mdTable(md){const rows=md.trim().split('\\n').filter(l=>!/^\\|-/.test(l));if(rows.length<2)return'No benchmark yet.';return'<table>'+rows.map((r,i)=>'<tr>'+r.split('|').slice(1,-1).map(c=>i?`<td>${esc(c.trim())}</td>`:`<th>${esc(c.trim())}</th>`).join('')+'</tr>').join('')+'</table>';}
async function show(id,el){document.querySelectorAll('.run').forEach(x=>x.classList.remove('sel'));el.classList.add('sel');
const r=await (await fetch('/api/runs/'+id)).json();
const ev=r.events.map(e=>{let body='';if(e.kind==='check')body=`${e.passed?'✅ PASS':'❌ FAIL'} (exit ${e.exit_code})<pre>${esc(e.output)}</pre>`;
else if(e.kind==='triage')body=`<b>${esc(e.model)}</b> → ${esc(e.failure_type)}: ${esc(e.summary)}<br><span class=sub>search: ${esc(e.search_query)}</span>`;
else if(e.kind==='search')body=`Tavily: ${e.urls.map(u=>`<div class=sub>${esc(u)}</div>`).join('')}`;
else if(e.kind==='patch')body=`<b>${esc(e.model)}</b>: ${esc(e.rationale)}<pre>${diff(e.diff)}</pre>`;
else body=`<pre>${esc(JSON.stringify(e))}</pre>`;
return `<div class=ev><span class=sub>${e.t}s · ${esc(e.kind)}${e.phase?' · '+esc(e.phase):''}</span><div>${body}</div></div>`}).join('');
document.getElementById('detail').innerHTML=`<h3>${esc(r.case)} · ${esc(r.condition_name)} <span class="badge ${r.verdict}">${r.verdict}</span></h3>
<div class=sub>${esc(r.models.triage)} → ${esc(r.models.fixer)} · ${r.usage.tokens_in+r.usage.tokens_out} tokens · $${r.usage.usd.toFixed(4)} · ${r.seconds}s · provider ${esc(r.provider)}</div>
<h3>Timeline</h3>${ev}<h3>Final diff</h3><pre>${diff(r.final_diff)||'(none)'}</pre>`;}
load();
</script></body></html>"""


@app.get("/", response_class=HTMLResponse)
def index():
    return PAGE

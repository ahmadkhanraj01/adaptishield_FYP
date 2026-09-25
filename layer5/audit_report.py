"""
Layer 5 — Audit Dashboard, Policy Inspection Console and Audit Logs, rendered to
one self-contained HTML file.

    python -m layer5.audit_report
    python -m layer5.audit_report --open        # and open it in a browser

WHY A FILE AND NOT A SERVER. The whole record set is about 1.2 MB, which fits
inside the page. Embedding it means every filter, sort and drill-down runs
locally with no request/response cycle, which is faster than a server can be, not
slower. It also means the artifact is one file: it opens by double-click, needs
no process running, no dependency installed and no build step, and it can be
attached to a report or archived alongside the campaign that produced it. A
server would add a moving part and a dependency in exchange for latency.

Nothing outside the standard library is used, and no network request is made —
the page must render correctly on a machine with no internet, which is also what
makes it safe to open a page containing untrusted mediator text.

ON RENDERING UNTRUSTED TEXT. The records contain prompt-injection payloads by
construction: `mediator_snippet` is attacker-authored content, and the point of
the dashboard is to read it. Every value is HTML-escaped, and the data is
delivered as JSON inside a script block with `<` escaped, so that a payload
containing markup cannot terminate the block and become live DOM. An audit tool
that could be attacked by the thing it audits would be an unusually poor one.
"""

import argparse
import html
import json
import os
import webbrowser
from collections import Counter
from typing import Any, Dict, List, Optional

DEFAULT_RECORDS = "logs/episode_records/episodes.jsonl"
DEFAULT_EPISODES = "evaluation/kaggle/dataset/episodes.jsonl"
DEFAULT_PROPOSAL = "evaluation/kaggle/proposed_update.json"
DEFAULT_OUT = "logs/layer5/audit.html"


# ── data assembly ────────────────────────────────────────────────────
def load_jsonl(path: str) -> List[Dict[str, Any]]:
    if not os.path.exists(path):
        return []
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


def split_campaigns(rows: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
    """
    The record log is append-only across campaigns and `boundary_index` restarts
    at 1 with each run. Grouping by that reset is what lets the dashboard show
    'the last campaign' rather than an undifferentiated pile of 828 crossings
    spanning corpora that are not comparable.
    """
    if not rows:
        return []
    groups, cur = [], [rows[0]]
    for prev, row in zip(rows, rows[1:]):
        if row["boundary_index"] <= prev["boundary_index"]:
            groups.append(cur)
            cur = []
        cur.append(row)
    groups.append(cur)
    return groups


def wilson(successes: int, n: int, z: float = 1.96):
    """Shared with evaluation.fpr_report — see there for why not the normal approx."""
    from evaluation.fpr_report import wilson as _w
    return _w(successes, n, z)


def summarise(episodes: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Detection and FPR by cohort, with intervals, from the packaged dataset."""
    if not episodes:
        return {}
    mal = [e for e in episodes if e["is_malicious"]]
    ben = [e for e in episodes if not e["is_malicious"]]

    def cohort(e):
        return "agentdojo" if e["case_id"].startswith("agentdojo-") else "ours"

    out: Dict[str, Any] = {"n": len(episodes), "n_malicious": len(mal),
                           "n_benign": len(ben), "cohorts": []}
    for name in ("ours", "agentdojo"):
        grp = [e for e in ben if cohort(e) == name]
        if not grp:
            continue
        fp = sum(1 for e in grp if e["causal_takeover"])
        lo, hi = wilson(fp, len(grp))
        out["cohorts"].append({
            "name": name, "fp": fp, "n": len(grp),
            "point": fp / len(grp), "lo": lo, "hi": hi,
            "note": ("diagnostic — hand-written, half designed to break the "
                     "detector; NOT a rate" if name == "ours"
                     else "externally authored (AgentDojo, MIT) — this is the estimate"),
        })
    caught = sum(1 for e in mal if e["causal_takeover"])
    lo, hi = wilson(caught, len(mal)) if mal else (0.0, 1.0)
    out["detection"] = {"caught": caught, "n": len(mal), "lo": lo, "hi": hi}

    out["misses"] = [
        {"case_id": e["case_id"], "family": e["family"],
         "masked": e["causal"]["masked_severity"],
         "san": e["causal"]["masked_san_severity"], "ie": e["causal"]["ie"]}
        for e in mal if not e["causal_takeover"]]
    out["false_positives"] = [
        {"case_id": e["case_id"], "family": e["family"],
         "masked": e["causal"]["masked_severity"],
         "san": e["causal"]["masked_san_severity"], "ie": e["causal"]["ie"]}
        for e in ben if e["causal_takeover"]]
    return out


def policy_state() -> Dict[str, Any]:
    """Live 3A/3B configuration, read from the components themselves."""
    try:
        from layer2.security_sublayer.causal_analyzer import CausalAnalyzer
        from layer2.security_sublayer.policy_engine import PolicyEngine
        pe, ca = PolicyEngine(), CausalAnalyzer()
        return {
            "blocked_patterns": sorted(getattr(pe, "blocked_patterns", []) or []),
            "high_impact_tools": sorted(getattr(pe, "high_impact_tools", []) or []),
            "ie_threshold": getattr(ca, "ie_threshold", None),
            "masked_takeover_threshold": getattr(ca, "masked_takeover_threshold", None),
            "risk_threshold": getattr(ca, "risk_threshold", None),
            "window_size": getattr(ca, "window_size", None),
            "k_samples": getattr(ca, "k_samples", None),
            "temperature": getattr(ca, "temperature", None),
        }
    except Exception as e:                                   # noqa: BLE001
        return {"error": f"could not read live policy state: {e}"}


# ── rendering ────────────────────────────────────────────────────────
def esc(x: Any) -> str:
    return html.escape("" if x is None else str(x), quote=True)


def embed(data: Any) -> str:
    """
    JSON for a <script> block. `<` is escaped so an injection payload containing
    "</script>" cannot close the block; the records are attacker-authored, so
    this is load-bearing rather than defensive style.
    """
    return (json.dumps(data)
            .replace("<", "\\u003c").replace(">", "\\u003e")
            .replace("&", "\\u0026"))


def pct(x: float) -> str:
    return f"{x * 100:.1f}%"


def render_summary(s: Dict[str, Any]) -> str:
    if not s:
        return "<p class='muted'>No packaged dataset found.</p>"
    d = s["detection"]
    rows = [
        f"<tr><td>detection</td><td class='num'>{d['caught']}</td>"
        f"<td class='num'>{d['n']}</td><td class='num'>{pct(d['caught'] / d['n'])}</td>"
        f"<td class='num'>[{pct(d['lo'])}, {pct(d['hi'])}]</td>"
        f"<td class='muted'>caught_by_causal</td></tr>"
    ]
    for c in s["cohorts"]:
        cls = "warn" if c["name"] == "ours" else ""
        rows.append(
            f"<tr class='{cls}'><td>FPR · {esc(c['name'])}</td>"
            f"<td class='num'>{c['fp']}</td><td class='num'>{c['n']}</td>"
            f"<td class='num'>{pct(c['point'])}</td>"
            f"<td class='num'>[{pct(c['lo'])}, {pct(c['hi'])}]</td>"
            f"<td class='muted'>{esc(c['note'])}</td></tr>")
    return f"""
    <table class="wide">
      <thead><tr><th>metric</th><th class='num'>k</th><th class='num'>n</th>
      <th class='num'>point</th><th class='num'>95% Wilson</th><th>note</th></tr></thead>
      <tbody>{''.join(rows)}</tbody>
    </table>"""


def render_governance(proposal: Optional[Dict[str, Any]],
                      verifier: Optional[Dict[str, Any]],
                      decisions: List[Dict[str, Any]]) -> str:
    if not proposal:
        return "<p class='muted'>No proposal found — run the GRPO trainer.</p>"

    old, new = proposal["old_ie_threshold"], proposal["new_ie_threshold"]
    bits = [f"<div class='kv'><span>ie_threshold</span><b>{esc(old)} &rarr; {esc(new)}</b></div>"]
    for label, key in (("blocked_patterns", "new_blocked_patterns"),
                       ("high_impact_tools", "new_high_impact_tools")):
        v = proposal.get(key) or []
        bits.append(f"<div class='kv'><span>{label}</span><b>{esc(v) if v else '—'}</b></div>")

    verifier_html = ""
    if verifier:
        worse = verifier.get("policy_choice_was_worse")
        badge = ("<span class='badge bad'>policy's choice scored LOWER than "
                 "doing nothing</span>" if worse else "")
        verifier_html = f"""
        <h3>What the policy wanted, and what the verifier said</h3>
        {badge}
        <div class='kv'><span>policy argmax</span><b>{esc(verifier['policy_wanted'])}</b></div>
        <div class='kv'><span>reward · incumbent</span><b>{verifier['reward_incumbent']:+.6f}</b></div>
        <div class='kv'><span>reward · policy choice</span><b>{verifier['reward_policy_choice']:+.6f}</b></div>
        <div class='kv'><span>verdict</span><b>{'ACCEPTED' if verifier['accepted'] else 'REJECTED → no-op'}</b></div>
        <div class='kv'><span>search</span><b>{esc(verifier['actions_evaluated'])} of
            {esc(verifier['space_cardinality'])} joint actions (sampled)</b></div>
        <div class='kv'><span>unidentifiable</span><b>{esc(verifier['flat_dimensions']) or '—'}</b></div>
        <p class='muted'>A rejected proposal serialises as a no-op and looks like
        nothing happened. What happened is that the learned policy wanted the
        action above, the verifier scored it against the incumbent, and it lost.
        This is README §6n — the reason this gate exists.</p>"""

    if decisions:
        drows = "".join(
            f"<tr><td>{esc(d['timestamp'][:19])}</td>"
            f"<td><span class='badge {'ok' if d['verdict'] == 'approved' else 'bad'}'>"
            f"{esc(d['verdict'])}</span></td>"
            f"<td>{esc(d['operator'])}</td>"
            f"<td class='num'>{d.get('evidence', {}).get('delta', 0):+.6f}</td>"
            f"<td>{esc(d['reason'])}</td></tr>" for d in reversed(decisions))
        dec_html = f"""<h3>Decision log ({len(decisions)})</h3>
        <table class="wide"><thead><tr><th>when</th><th>verdict</th><th>operator</th>
        <th class='num'>&Delta;reward</th><th>reason</th></tr></thead>
        <tbody>{drows}</tbody></table>"""
    else:
        dec_html = ("<h3>Decision log</h3><p class='muted'>Empty. Proposals are "
                    "reviewed with <code>python -m layer5.review</code>; nothing has "
                    "been approved or rejected yet.</p>")

    return f"<h3>Pending proposal</h3>{''.join(bits)}{verifier_html}{dec_html}"


def render_policy(p: Dict[str, Any]) -> str:
    if "error" in p:
        return f"<p class='muted'>{esc(p['error'])}</p>"
    return "".join(
        f"<div class='kv'><span>{esc(k)}</span><b>{esc(v) if v not in ([], None) else '—'}</b></div>"
        for k, v in p.items())


def render_page(records, summary, proposal, verifier, decisions, policy,
                campaigns) -> str:
    latest = campaigns[-1] if campaigns else []
    status_counts = Counter(r.get("final_status", "unknown") for r in latest)
    return f"""<!doctype html>
<meta charset="utf-8">
<title>AdaptiShield — Layer 5 Audit Dashboard</title>
<style>
  :root {{ --bg:#0f1115; --panel:#171a21; --line:#262b36; --fg:#e6e9ef;
           --muted:#8b94a7; --acc:#5ac8fa; --bad:#ff6b6b; --ok:#51cf66;
           --warn:#ffd43b; }}
  @media (prefers-color-scheme: light) {{
    :root {{ --bg:#f7f8fa; --panel:#fff; --line:#e2e5ea; --fg:#1a1d23;
             --muted:#6b7280; --acc:#0b72b9; --bad:#c92a2a; --ok:#2b8a3e;
             --warn:#a07800; }}
  }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; background:var(--bg); color:var(--fg);
    font:14px/1.55 ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,sans-serif; }}
  header {{ padding:22px 26px; border-bottom:1px solid var(--line); }}
  h1 {{ margin:0; font-size:19px; letter-spacing:.2px; }}
  .sub {{ color:var(--muted); font-size:13px; margin-top:5px; }}
  main {{ padding:22px 26px; max-width:1500px; }}
  section {{ background:var(--panel); border:1px solid var(--line);
    border-radius:10px; padding:18px 20px; margin-bottom:18px; }}
  h2 {{ margin:0 0 14px; font-size:15px; }}
  h3 {{ margin:18px 0 10px; font-size:13px; color:var(--muted);
    text-transform:uppercase; letter-spacing:.6px; }}
  table {{ border-collapse:collapse; width:100%; font-size:13px; }}
  th,td {{ text-align:left; padding:7px 10px; border-bottom:1px solid var(--line);
    vertical-align:top; }}
  th {{ color:var(--muted); font-weight:600; position:sticky; top:0;
    background:var(--panel); }}
  td.num, th.num {{ text-align:right; font-variant-numeric:tabular-nums;
    font-family:ui-monospace,SFMono-Regular,Menlo,monospace; }}
  tr.warn td {{ background:color-mix(in srgb, var(--warn) 12%, transparent); }}
  .muted {{ color:var(--muted); }}
  .kv {{ display:flex; gap:14px; padding:5px 0; border-bottom:1px dotted var(--line); }}
  .kv span {{ min-width:210px; color:var(--muted); }}
  .kv b {{ font-family:ui-monospace,SFMono-Regular,Menlo,monospace; font-weight:600;
    word-break:break-word; }}
  .badge {{ display:inline-block; padding:2px 9px; border-radius:20px;
    font-size:11.5px; font-weight:700; letter-spacing:.3px; }}
  .badge.bad {{ background:var(--bad); color:#fff; }}
  .badge.ok {{ background:var(--ok); color:#062; }}
  .grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(300px,1fr));
    gap:18px; }}
  .stat {{ font-size:26px; font-weight:700; font-variant-numeric:tabular-nums; }}
  .controls {{ display:flex; gap:10px; flex-wrap:wrap; margin-bottom:12px; }}
  input,select {{ background:var(--bg); color:var(--fg); border:1px solid var(--line);
    border-radius:7px; padding:7px 10px; font:inherit; }}
  input[type=search] {{ min-width:280px; }}
  .scroll {{ max-height:560px; overflow:auto; border:1px solid var(--line);
    border-radius:8px; }}
  .wrap {{ overflow-x:auto; }}
  details {{ margin:4px 0; }}
  summary {{ cursor:pointer; }}
  pre {{ background:var(--bg); border:1px solid var(--line); border-radius:7px;
    padding:10px; overflow-x:auto; font-size:12px; white-space:pre-wrap;
    word-break:break-word; margin:6px 0 0; }}
  code {{ font-family:ui-monospace,SFMono-Regular,Menlo,monospace; }}
</style>
<header>
  <h1>AdaptiShield — Layer 5 · Audit Dashboard</h1>
  <div class="sub">{len(records)} boundary crossings across {len(campaigns)}
    campaign(s) · latest campaign: {len(latest)} · generated offline, no network
    calls, all values escaped</div>
</header>
<main>

<section>
  <h2>Campaign summary — latest packaged dataset</h2>
  <div class="wrap">{render_summary(summary)}</div>
  <p class="muted">The two benign cohorts are never pooled as a headline: the
  hand-written eight are a diagnostic that located an architectural boundary, not
  a draw from any distribution. See README §6n.</p>
</section>

<section>
  <h2>Policy Inspection Console</h2>
  <div class="grid">
    <div><h3>Live policy state</h3>{render_policy(policy)}</div>
    <div>{render_governance(proposal, verifier, decisions)}</div>
  </div>
</section>

<section>
  <h2>Outcomes · latest campaign</h2>
  <div class="grid">
    {''.join(f'<div><div class="stat">{v}</div><div class="muted">{esc(k)}</div></div>'
             for k, v in sorted(status_counts.items(), key=lambda kv: -kv[1]))}
  </div>
  {_render_case_lists(summary)}
</section>

<section>
  <h2>Audit Logs — every boundary crossing</h2>
  <div class="controls">
    <input type="search" id="q" placeholder="search action, tool, mediator text…">
    <select id="status"><option value="">all statuses</option></select>
    <select id="campaign"><option value="">latest campaign</option>
      <option value="all">all campaigns</option></select>
    <label class="muted"><input type="checkbox" id="takeover"> takeover only</label>
    <span class="muted" id="count"></span>
  </div>
  <div class="scroll"><table id="tbl">
    <thead><tr><th class="num">#</th><th>status</th><th>tool</th>
      <th>proposed action</th><th class="num">sev</th><th>causal</th>
      <th>detail</th></tr></thead>
    <tbody></tbody>
  </table></div>
</section>

</main>
<script id="data" type="application/json">{embed(records)}</script>
<script id="groups" type="application/json">{embed([len(g) for g in campaigns])}</script>
<script>
const ROWS   = JSON.parse(document.getElementById('data').textContent);
const GROUPS = JSON.parse(document.getElementById('groups').textContent);

// Campaign boundaries, so "latest campaign" means the same thing here as in the
// Python that split them.
let starts = [], acc = 0;
for (const n of GROUPS) {{ starts.push([acc, acc + n]); acc += n; }}
const LATEST = starts.length ? starts[starts.length - 1] : [0, ROWS.length];

const q = document.getElementById('q'), sel = document.getElementById('status'),
      camp = document.getElementById('campaign'), tk = document.getElementById('takeover'),
      body = document.querySelector('#tbl tbody'), count = document.getElementById('count');

for (const s of [...new Set(ROWS.map(r => r.final_status || 'unknown'))].sort())
  sel.add(new Option(s, s));

const esc = s => String(s ?? '').replace(/[&<>"]/g, c =>
  ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}}[c]));

function detail(r) {{
  const cv = r.causal_verdict, parts = [];
  if (cv) parts.push('CAUSAL  ' + JSON.stringify(cv, null, 1));
  if (r.screen_result) parts.push('SCREEN  ' + JSON.stringify(r.screen_result, null, 1));
  if (r.sanitization_decision) parts.push('3C      ' + JSON.stringify(r.sanitization_decision, null, 1));
  if (r.mediator_snippet) parts.push('MEDIATOR (untrusted)\\n' + r.mediator_snippet);
  return parts.join('\\n\\n');
}}

function render() {{
  const needle = q.value.toLowerCase(), st = sel.value, only = tk.checked;
  const [lo, hi] = camp.value === 'all' ? [0, ROWS.length] : LATEST;
  const out = [];
  for (let i = lo; i < hi; i++) {{
    const r = ROWS[i], cv = r.causal_verdict;
    if (st && (r.final_status || 'unknown') !== st) continue;
    if (only && !(cv && cv.takeover)) continue;
    if (needle) {{
      const hay = ((r.proposed_action || '') + ' ' + (r.tool_name || '') + ' ' +
                   (r.mediator_snippet || '')).toLowerCase();
      if (!hay.includes(needle)) continue;
    }}
    const c = cv ? `IE=${{cv.ie}} m=${{cv.masked_severity}} s=${{cv.masked_san_severity}}` +
                   (cv.takeover ? ' · takeover' : '') : '—';
    out.push(`<tr><td class="num">${{r.boundary_index}}</td>
      <td>${{esc(r.final_status)}}</td><td>${{esc(r.tool_name)}}</td>
      <td>${{esc(r.proposed_action)}}</td>
      <td class="num">${{r.outcome_severity ?? ''}}</td><td>${{esc(c)}}</td>
      <td><details><summary class="muted">open</summary>
        <pre>${{esc(detail(r))}}</pre></details></td></tr>`);
  }}
  body.innerHTML = out.join('');
  count.textContent = out.length + ' of ' + (hi - lo) + ' shown';
}}
[q, sel, camp, tk].forEach(el => el.addEventListener('input', render));
render();
</script>
"""


def _render_case_lists(s: Dict[str, Any]) -> str:
    if not s:
        return ""
    def tbl(items, title, note):
        if not items:
            return f"<h3>{title}</h3><p class='muted'>none</p>"
        rows = "".join(
            f"<tr><td>{esc(i['case_id'])}</td><td>{esc(i['family'])}</td>"
            f"<td class='num'>{esc(i['masked'])}</td><td class='num'>{esc(i['san'])}</td>"
            f"<td class='num'>{esc(i['ie'])}</td></tr>" for i in items)
        return (f"<h3>{title} ({len(items)})</h3><p class='muted'>{note}</p>"
                f"<div class='wrap'><table><thead><tr><th>case</th><th>family</th>"
                f"<th class='num'>masked</th><th class='num'>san</th>"
                f"<th class='num'>IE</th></tr></thead><tbody>{rows}</tbody></table></div>")
    return (tbl(s.get("misses", []), "Missed attacks",
                "All address-free, carrying the legitimate destination so Layer 4 "
                "cannot mask them. 4 are severity-function failures (masked=0), 1 "
                "is a sanitizer failure; none is a threshold failure — which is why "
                "the 3D knob cannot close this gap.") +
            tbl(s.get("false_positives", []), "False positives",
                "workspace-055 is the genuine 3B/Layer 4 boundary (a real address "
                "in a real action item); workspace-041 is a probe hallucination on "
                "a document containing no address at all."))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--records", default=DEFAULT_RECORDS)
    ap.add_argument("--episodes", default=DEFAULT_EPISODES)
    ap.add_argument("--proposal", default=DEFAULT_PROPOSAL)
    ap.add_argument("--decisions", default=None)
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--open", action="store_true", help="open in a browser when done")
    args = ap.parse_args()

    from layer5.governance import DEFAULT_LOG, load_decisions, verifier_record

    records = load_jsonl(args.records)
    campaigns = split_campaigns(records)
    summary = summarise(load_jsonl(args.episodes))
    proposal = None
    if os.path.exists(args.proposal):
        with open(args.proposal) as f:
            proposal = json.load(f)
    decisions = load_decisions(args.decisions or DEFAULT_LOG)

    page = render_page(records, summary, proposal,
                       verifier_record(proposal) if proposal else None,
                       decisions, policy_state(), campaigns)

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w") as f:
        f.write(page)
    size = os.path.getsize(args.out) / 1024
    print(f"[layer5] wrote {args.out}  ({size:.0f} KB, {len(records)} records, "
          f"{len(campaigns)} campaign(s))")
    if args.open:
        webbrowser.open(f"file://{os.path.abspath(args.out)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Build the audited interpretive companion for the B2-GR I3 null surface."""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
from typing import Any

from b2_artifact_io import assert_envelope_digest, semantic_digest


EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = EXPERIMENT_ROOT / "outputs/b2_i3_active_nulls.json"
DEFAULT_OUTPUT = EXPERIMENT_ROOT / "reports/b2_i3_null_topography.html"

LADDER = ("GRR1", "GRR2", "GRR3", "GRR4", "GRR5")
EXPECTED_SCOPES = {
    "rung_blocker": 32,
    "lane_specific_blocker": 8,
    "route_only": 5,
    "claim_only_blocker": 4,
    "duplicate_only": 2,
    "robustness_only": 1,
}

DISPOSITION_PRESENTATION = {
    "bounded_negative": ("bounded negative", "#3f8f63"),
    "source_or_provenance_failure": ("provenance failure", "#bc7a36"),
    "required_assumption_failed": ("assumption failed", "#a36aa3"),
    "invalid_candidate": ("invalid candidate", "#bd4e59"),
    "required_control_failed": ("control failed", "#d39a3e"),
    "search_unresolved": ("search unresolved", "#4f8fc9"),
    "outside_envelope": ("outside envelope", "#7d8b9d"),
    "duplicate_candidate": ("duplicate", "#9f7654"),
}

SCOPE_PRESENTATION = {
    "rung_blocker": "rung",
    "lane_specific_blocker": "lane",
    "claim_only_blocker": "claim",
    "route_only": "route",
    "duplicate_only": "duplicate",
    "robustness_only": "robustness",
}


def load_artifact(path: Path) -> dict[str, Any]:
    artifact = json.loads(path.read_text(encoding="utf-8"))
    assert_envelope_digest(artifact)
    return artifact


def validate_topography(artifact: dict[str, Any]) -> dict[str, Any]:
    payload = artifact["payload"]
    rows = payload["active_null_rows"]
    sentinels = payload["pass_through_sentinel_rows"]
    if len(rows) != 52 or len(sentinels) != 52:
        raise ValueError("topography requires the complete 52-row null/sentinel set")

    scope_counts = Counter(row["effect_scope"] for row in rows)
    if dict(scope_counts) != EXPECTED_SCOPES:
        raise ValueError(f"unexpected effect-scope distribution: {scope_counts}")

    rung_rows = [row for row in rows if row["effect_scope"] == "rung_blocker"]
    governance_rows = [row for row in rows if row["effect_scope"] != "rung_blocker"]
    lowest_rung_counts: Counter[str] = Counter()
    for row in rung_rows:
        blocked = row["blocked_rungs"]
        if not blocked:
            raise ValueError(f"rung blocker has no blocked rungs: {row['null_id']}")
        lowest_index = LADDER.index(blocked[0])
        if blocked != list(LADDER[lowest_index:]):
            raise ValueError(f"non-suffix rung mask: {row['null_id']} -> {blocked}")
        if row["lane_blocked_rungs"]:
            raise ValueError(
                f"global rung blocker also blocks a lane: {row['null_id']}"
            )
        lowest_rung_counts[blocked[0]] += 1

    for row in governance_rows:
        if row["blocked_rungs"]:
            raise ValueError(
                f"governance row globally demotes the ladder: {row['null_id']}"
            )

    sentinel_by_rule = {row["i2_rule_ids_exercised"][0]: row for row in sentinels}
    baseline = {row["null_id"]: True for row in rows}
    baseline_digest = semantic_digest(baseline)
    for row in rows:
        null_id = row["null_id"]
        sentinel = sentinel_by_rule.get(null_id)
        if sentinel is None:
            raise ValueError(f"missing sentinel for: {null_id}")
        atomic = dict(baseline)
        atomic[null_id] = False
        atomic_digest = semantic_digest(atomic)
        if row["reference_gate_vector_digest"] != baseline_digest:
            raise ValueError(f"atomic reference digest mismatch: {null_id}")
        if row["tested_gate_vector_digest"] != atomic_digest:
            raise ValueError(f"atomic tested digest mismatch: {null_id}")
        if sentinel["tested_gate_vector_digest"] != baseline_digest:
            raise ValueError(f"sentinel tested digest mismatch: {null_id}")
        if sentinel["paired_atomic_gate_vector_digest"] != atomic_digest:
            raise ValueError(f"sentinel pair digest mismatch: {null_id}")
        if sentinel["result"] != "passed":
            raise ValueError(f"sentinel did not pass through: {null_id}")
        if sentinel["positive_evidence_eligible"] is not False:
            raise ValueError(f"sentinel incorrectly marked as evidence: {null_id}")

    disposition_counts = Counter(row["expected_primary_disposition"] for row in rows)
    family_counts = Counter(row["control_family"] for row in rows)
    reason_family_counts: dict[str, dict[str, int]] = {}
    for family in sorted(family_counts):
        reason_family_counts[family] = dict(
            Counter(
                row["expected_primary_disposition"]
                for row in rows
                if row["control_family"] == family
            )
        )

    return {
        "null_count": len(rows),
        "rung_blocker_count": len(rung_rows),
        "governance_guard_count": len(governance_rows),
        "scope_counts": dict(scope_counts),
        "suffix_violation_count": 0,
        "lowest_rung_counts": dict(lowest_rung_counts),
        "disposition_counts": dict(disposition_counts),
        "family_counts": dict(family_counts),
        "reason_family_counts": reason_family_counts,
        "sentinel_pair_count": len(sentinel_by_rule),
        "all_sentinels_non_evidence_pass_through": True,
    }


def build_visual_rows(artifact: dict[str, Any]) -> list[dict[str, Any]]:
    payload = artifact["payload"]
    sentinels = {
        row["i2_rule_ids_exercised"][0]: row
        for row in payload["pass_through_sentinel_rows"]
    }
    rows = []
    for row in payload["active_null_rows"]:
        blocked = row["blocked_rungs"]
        lowest = blocked[0] if blocked else None
        label, color = DISPOSITION_PRESENTATION[row["expected_primary_disposition"]]
        rows.append(
            {
                "id": row["null_id"],
                "family": row["control_family"],
                "gate_family": row["blocked_gate_family"],
                "scope": row["effect_scope"],
                "scope_label": SCOPE_PRESENTATION[row["effect_scope"]],
                "lowest_rung": lowest,
                "lowest_rung_index": LADDER.index(lowest) if lowest else None,
                "blocked_mask": [rung in blocked for rung in LADDER],
                "lane_blocked_rungs": row["lane_blocked_rungs"],
                "disposition": row["expected_primary_disposition"],
                "disposition_label": label,
                "disposition_color": color,
                "false_positive_path": row["false_positive_path"],
                "candidate_disposition": row["candidate_disposition"],
                "rung_effect": row["rung_effect"],
                "claim_effect": row["claim_effect"],
                "robustness_effect": row["robustness_effect"],
                "route_effect": row["route_effect"],
                "duplicate_effect": row["duplicate_effect"],
                "alternative": row["expected_alternative_classification"],
                "atomic_gate_value": row["target_gate_value"],
                "sentinel_gate_value": sentinels[row["null_id"]]["target_gate_value"],
                "sentinel_result": sentinels[row["null_id"]]["result"],
            }
        )
    return rows


def render_html(artifact: dict[str, Any]) -> str:
    summary = validate_topography(artifact)
    visual_rows = build_visual_rows(artifact)
    source = {
        "schema": "b2_i3_null_topography_v1",
        "source_artifact": "outputs/b2_i3_active_nulls.json",
        "source_payload_sha256": artifact["payload_sha256"],
        "interpretive_only": True,
        "summary": summary,
        "rows": visual_rows,
    }
    embedded = json.dumps(source, sort_keys=True, separators=(",", ":")).replace(
        "<", "\\u003c"
    )
    template = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>B2-I3 Null Topography</title>
<style>
:root{--bg:#0e1217;--surface:#151b22;--surface2:#1b232d;--ink:#edf1f5;--dim:#9ba7b5;--line:#2c3743;--gold:#e0b154;--green:#59bd82;--red:#d86c74}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:14px/1.5 ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif;letter-spacing:0}
header{padding:20px 24px 12px;border-bottom:1px solid var(--line)}h1{font-size:20px;margin:0 0 4px}h2{font-size:14px;margin:0 0 12px;color:var(--gold);text-transform:uppercase}p{margin:6px 0}.sub,.note,.meta{color:var(--dim)}.meta{font:11px/1.4 ui-monospace,SFMono-Regular,monospace;overflow-wrap:anywhere}
.tabs{display:flex;gap:6px;padding:12px 24px;border-bottom:1px solid var(--line);overflow:auto}.tab{border:1px solid var(--line);border-radius:6px;background:var(--surface);color:var(--dim);padding:7px 12px;cursor:pointer;white-space:nowrap}.tab.on{color:var(--ink);border-color:var(--gold)}
main{max-width:1440px;margin:auto;padding:20px 24px 48px}.view{display:none}.view.on{display:block}.metrics{display:grid;grid-template-columns:repeat(4,minmax(140px,1fr));gap:8px;margin-bottom:18px}.metric{border:1px solid var(--line);border-radius:6px;background:var(--surface);padding:10px}.metric b{display:block;font-size:22px}.metric span{color:var(--dim);font-size:12px}
.split{display:grid;grid-template-columns:minmax(260px,380px) 1fr;gap:18px}.ladder{display:flex;flex-direction:column-reverse;gap:6px}.rung{border:1px solid var(--line);border-radius:6px;background:var(--surface);padding:9px}.rung b{display:block}.rung span{color:var(--dim);font-size:12px}.rung.source{border-color:var(--green)}
.scope-table,.why-table{width:100%;border-collapse:collapse;background:var(--surface)}.why-table{table-layout:fixed}.why-table th:first-child{width:24%}th,td{border:1px solid var(--line);padding:7px 8px;text-align:left}th{color:var(--dim);font-size:11px;overflow-wrap:anywhere}.count{text-align:right;font-variant-numeric:tabular-nums}
.heat{display:grid;grid-template-columns:minmax(280px,1fr) repeat(5,minmax(50px,90px));gap:3px;align-items:center}.heat .head{color:var(--dim);font-size:11px;text-align:center}.row-label{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:11px;padding-right:6px}.cell{height:17px;border-radius:3px;background:var(--surface2)}.cell.sealed{background:var(--cell)}
.legend{display:flex;flex-wrap:wrap;gap:12px;margin:12px 0}.legend span{display:flex;gap:5px;align-items:center;color:var(--dim);font-size:11px}.swatch{width:11px;height:11px;border-radius:2px}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(330px,1fr));gap:8px}.card{border:1px solid var(--line);border-radius:6px;background:var(--surface);padding:10px}.card-top{display:flex;justify-content:space-between;gap:8px}.card-title{font-weight:700;font-size:12px;overflow-wrap:anywhere}.pill{border-radius:999px;background:var(--surface2);color:var(--gold);padding:2px 7px;font-size:10px;white-space:nowrap}.path{color:var(--dim);font-size:12px;margin:6px 0}.flip{display:grid;grid-template-columns:24px 1fr auto;gap:7px;align-items:center;border-top:1px solid var(--line);padding-top:6px;margin-top:6px;font-size:11px}.gate{width:24px;height:24px;border-radius:5px;display:grid;place-items:center;font-weight:800}.gate.pass{background:#153623;color:#79dda0}.gate.fail{background:#3a1b20;color:#f19aa0}.ok{color:var(--green)}.bad{color:var(--red)}
@media(max-width:800px){.metrics{grid-template-columns:repeat(2,1fr)}.split{grid-template-columns:1fr}.heat{grid-template-columns:minmax(180px,1fr) repeat(5,minmax(30px,1fr))}.tabs{flex-wrap:wrap}header,.tabs,main{padding-left:12px;padding-right:12px}}
</style></head><body>
<header><h1>B2-I3 null topography</h1><p class="sub">A rung-admission staircase and a separate governance layer, reconstructed from the effect-scoped I3 artifact.</p><p class="meta" id="source"></p></header>
<nav class="tabs" aria-label="Views"><button class="tab on" data-view="overview">Boundary layers</button><button class="tab" data-view="staircase">Rung staircase</button><button class="tab" data-view="why">Why each row closes</button><button class="tab" data-view="flips">Null / sentinel flips</button></nav>
<main>
<section id="overview" class="view on"><div class="metrics" id="metrics"></div><div class="split"><div><h2>GRR ladder context</h2><div class="ladder" id="ladder"></div><p class="note">GRR2 is the accepted B1-GR source ceiling, not a rung assigned by this I3 fixture suite.</p></div><div><h2>Non-global governance guards</h2><table class="scope-table"><thead><tr><th>Effect scope</th><th class="count">Rows</th><th>What it changes</th></tr></thead><tbody id="scopes"></tbody></table><p class="note">These 20 rows do not globally demote the GRR ladder. Lane guards may close only the claimed lane; claim, route, duplicate, and robustness guards preserve the underlying witness.</p></div></div></section>
<section id="staircase" class="view"><h2>32 global rung blockers form contiguous suffixes</h2><div class="heat" id="heat"></div><div class="legend" id="legend"></div><p class="note">A filled cell means the row blocks that global rung. Every nonempty mask is a suffix: once a prerequisite rung is closed, all stronger dependent rungs close with it. This is an admission topology, not a claim that every blocker is a physical impossibility.</p></section>
<section id="why" class="view"><h2>Disposition by control family</h2><div style="overflow:auto"><table class="why-table" id="why-table"></table></div><p class="note"><code>expected_primary_disposition</code> states why the prohibited interpretation closes; <code>control_family</code> states which causal or governance boundary it protects.</p></section>
<section id="flips" class="view"><h2>One rule flip, two non-evidence fixtures</h2><div class="cards" id="cards"></div><p class="note">The sentinel is a validator pass-through fixture, not admissible scientific evidence. Flipping its one target gate from true to false activates the paired atomic null and rejects the prohibited interpretation with the row's typed effect.</p></section>
</main>
<script>
const DATA=__DATA__;
const ladder=["GRR1","GRR2","GRR3","GRR4","GRR5"];
const esc=s=>String(s).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"})[c]);
document.getElementById("source").textContent=`Interpretive companion only | source payload ${DATA.source_payload_sha256}`;
const showView=id=>{const target=document.querySelector(`.tab[data-view="${id}"]`);if(!target)return;document.querySelectorAll(".tab").forEach(x=>x.classList.remove("on"));document.querySelectorAll(".view").forEach(x=>x.classList.remove("on"));target.classList.add("on");document.getElementById(id).classList.add("on")};
document.querySelectorAll(".tab").forEach(button=>button.addEventListener("click",()=>showView(button.dataset.view)));
showView(new URLSearchParams(location.search).get("view")||"overview");
const S=DATA.summary;
document.getElementById("metrics").innerHTML=[[S.null_count,"frozen null rules"],[S.rung_blocker_count,"global rung blockers"],[S.governance_guard_count,"non-global governance guards"],[S.sentinel_pair_count,"passing non-evidence sentinels"]].map(([v,l])=>`<div class="metric"><b>${v}</b><span>${l}</span></div>`).join("");
const lowest=S.lowest_rung_counts;
document.getElementById("ladder").innerHTML=ladder.map((r,i)=>`<div class="rung ${i<=1?'source':''}"><b>${r}${i<=1?' | source-supported context':''}</b><span>${lowest[r]||0} global null(s) first seal here</span></div>`).join("");
const scopeText={lane_specific_blocker:"Rejects only a claimed lane; typed alternative remains available.",claim_only_blocker:"Rejects a stronger label without changing the witness rung.",route_only:"Blocks a search, closeout, or extension inference.",duplicate_only:"Prevents double counting; keeps one physical witness.",robustness_only:"Narrows scope without invalidating a clean witness."};
document.getElementById("scopes").innerHTML=Object.entries(S.scope_counts).filter(([k])=>k!=="rung_blocker").map(([k,v])=>`<tr><td>${esc(k)}</td><td class="count">${v}</td><td>${esc(scopeText[k])}</td></tr>`).join("");
const rungRows=DATA.rows.filter(r=>r.scope==="rung_blocker").sort((a,b)=>a.lowest_rung_index-b.lowest_rung_index||a.id.localeCompare(b.id));
let heat='<div></div>'+ladder.map(r=>`<div class="head">${r}</div>`).join("");
const legend={};
rungRows.forEach(r=>{heat+=`<div class="row-label" title="${esc(r.id)}">${esc(r.disposition_label)} | ${esc(r.id)}</div>`;r.blocked_mask.forEach(sealed=>heat+=`<div class="cell ${sealed?'sealed':''}" style="--cell:${r.disposition_color}"></div>`);legend[r.disposition_label]=r.disposition_color});
document.getElementById("heat").innerHTML=heat;
document.getElementById("legend").innerHTML=Object.entries(legend).map(([k,c])=>`<span><i class="swatch" style="background:${c}"></i>${esc(k)}</span>`).join("");
const dispositions=Object.keys(S.disposition_counts).sort();const dispositionLabels={bounded_negative:"bounded negative",duplicate_candidate:"duplicate",invalid_candidate:"invalid",outside_envelope:"outside envelope",required_assumption_failed:"assumption failed",required_control_failed:"control failed",search_unresolved:"unresolved",source_or_provenance_failure:"provenance failure"};const families=Object.keys(S.family_counts).sort();let why='<thead><tr><th>Control family</th>'+dispositions.map(d=>`<th class="count" title="${esc(d)}">${esc(dispositionLabels[d]||d)}</th>`).join("")+'<th class="count">Total</th></tr></thead><tbody>';families.forEach(f=>{const counts=S.reason_family_counts[f];why+=`<tr><td>${esc(f)}</td>`+dispositions.map(d=>`<td class="count">${counts[d]||0}</td>`).join("")+`<td class="count">${S.family_counts[f]}</td></tr>`});why+='</tbody>';document.getElementById("why-table").innerHTML=why;
document.getElementById("cards").innerHTML=DATA.rows.map(r=>`<article class="card"><div class="card-top"><div class="card-title">${esc(r.id)}</div><span class="pill">${esc(r.scope_label)}</span></div><div class="path">${esc(r.disposition_label)} x ${esc(r.family)}</div><div class="flip"><div class="gate pass">1</div><span>paired sentinel</span><b class="ok">validator pass-through</b></div><div class="flip"><div class="gate fail">0</div><span>atomic null</span><b class="bad">${esc(r.candidate_disposition)}</b></div><div class="note">${esc(r.rung_effect)}</div></article>`).join("");
</script></body></html>"""
    return template.replace("__DATA__", embedded) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    artifact = load_artifact(args.input)
    rendered = render_html(artifact)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered, encoding="utf-8")
    print(f"wrote {args.output} ({len(rendered)} bytes)")


if __name__ == "__main__":
    main()

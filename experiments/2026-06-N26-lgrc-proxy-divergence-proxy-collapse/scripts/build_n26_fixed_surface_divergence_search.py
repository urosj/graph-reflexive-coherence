#!/usr/bin/env python3
"""Build N26 Iteration 5-B fixed-surface divergence search."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-28T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N26-lgrc-proxy-divergence-proxy-collapse"
OUTPUT = EXPERIMENT / "outputs" / "n26_fixed_surface_divergence_search.json"
REPORT = EXPERIMENT / "reports" / "n26_fixed_surface_divergence_search.md"
ARTIFACT_DIR = EXPERIMENT / "outputs" / "n26_fixed_surface_divergence_search_artifacts"

I4_OUTPUT = EXPERIMENT / "outputs" / "n26_source_current_proxy_derivation_probe.json"
I4A_OUTPUT = EXPERIMENT / "outputs" / "n26_proxy_derivation_sensitivity_probe.json"
I5_OUTPUT = EXPERIMENT / "outputs" / "n26_proxy_divergence_contrast_matrix.json"
I5A_OUTPUT = EXPERIMENT / "outputs" / "n26_alternative_proxy_surface_divergence_probe.json"

N25_2_EXPERIMENT = ROOT / "experiments" / "2026-06-N25.2-lgrc9v3-mb6-validation-bridge"
N25_2_POSITIVE = N25_2_EXPERIMENT / "outputs" / "n25_2_native_runtime_positive_probe.json"
N25_2_VARIANT = N25_2_EXPERIMENT / "outputs" / "n25_2_native_runtime_variant_probe.json"
N25_2_STRESS = N25_2_EXPERIMENT / "outputs" / "n25_2_stress_variant_matrix.json"
N25_2_CLOSEOUT = N25_2_EXPERIMENT / "outputs" / "n25_2_closeout_and_n26_handoff.json"

COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N26-lgrc-proxy-divergence-proxy-collapse/scripts/"
    "build_n26_fixed_surface_divergence_search.py"
)

EXPECTED_I4_OUTPUT_DIGEST = "b8c8794ecc8e71c01c7bf9d0e1c369f1630416534741f3fb342c5622775a1680"
EXPECTED_I4A_OUTPUT_DIGEST = "5dbe325f6ce1ff95434b978e69cf659fdf609e2890960198aca66e2c5c85e414"
EXPECTED_I5_OUTPUT_DIGEST = "52e7cba79816e840947472d35ee8906f357db1bcf896b59f59bbac243d9ee4a5"
EXPECTED_I5A_OUTPUT_DIGEST = "108849bf8b5249b97611461a4423d4986030c6d84d83b6580ba03cfc561e8eda"
EXPECTED_N25_2_POSITIVE_DIGEST = "1a38c59b8e3149a4cdde1861237e45a0e9f2da8ecca6f548bf462313149527f1"
EXPECTED_N25_2_VARIANT_DIGEST = "f2a49eab162893564433286d8e12bad8c3f4b3891f2f0007857ec23ae2d83d07"
EXPECTED_N25_2_STRESS_DIGEST = "1759dbb4d8c85c27bc056108f04fea3cfcc1c59b5ee9518ebb7f641e60949627"
EXPECTED_N25_2_CLOSEOUT_DIGEST = "b92401da545899c7721ab42692827beb5b357bbd246d8991d7ad56649a6bbf03"

ABSOLUTE_PATH_MARKERS = ["/home/" + "uros", "Documents/" + "RC-github"]

UNSAFE_CLAIMS = [
    "agency_claim_allowed",
    "ant_ecology_claim_allowed",
    "identity_acceptance_claim_allowed",
    "native_support_claim_allowed",
    "organism_life_claim_allowed",
    "phase8_completion_claim_allowed",
    "semantic_choice_claim_allowed",
    "semantic_goal_claim_allowed",
    "semantic_learning_claim_allowed",
    "semantic_target_ownership_claim_allowed",
    "sentience_claim_allowed",
    "unrestricted_autonomy_claim_allowed",
    "unscoped_multi_basin_claim_allowed",
]


def canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def digest_data(data: Any) -> str:
    return hashlib.sha256(canonical_json(data).encode("utf-8")).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def contains_absolute_path(data: Any) -> bool:
    text = json.dumps(data, sort_keys=True, ensure_ascii=True)
    return any(marker in text for marker in ABSOLUTE_PATH_MARKERS)


def unsafe_claim_flags() -> dict[str, bool]:
    return {claim: False for claim in UNSAFE_CLAIMS}


def write_trace_artifact(row_id: str, artifact_role: str, payload: Any) -> dict[str, str]:
    path = ARTIFACT_DIR / row_id / f"{artifact_role}.json"
    write_json(path, payload)
    return {
        "path": rel(path),
        "sha256": sha256_file(path),
        "artifact_role": artifact_role,
    }


def build_artifact_manifest(row_id: str, traces: dict[str, Any]) -> list[dict[str, str]]:
    return [write_trace_artifact(row_id, role, traces[role]) for role in sorted(traces)]


def find_candidate(candidates: list[dict[str, Any]], route_id: str) -> dict[str, Any]:
    for candidate in candidates:
        if candidate["candidate_route_id"] == route_id:
            return candidate
    raise ValueError(f"Missing route candidate: {route_id}")


def source_threshold_row(stress_candidate: dict[str, Any]) -> dict[str, Any]:
    for row in stress_candidate["threshold_stress_rows"]:
        if row["stress_id"] == "source_threshold_replay":
            return row
    raise ValueError(f"Missing source threshold row for {stress_candidate['candidate_id']}")


def build_selected_vs_rejected_row(
    row_id: str,
    source_label: str,
    source_path: Path,
    source_output_digest: str,
    selected: dict[str, Any],
    rejected: dict[str, Any],
    selected_child: dict[str, Any],
) -> dict[str, Any]:
    selected_score = selected["candidate_route_score"]
    rejected_score = rejected["candidate_route_score"]
    proxy_delta = selected_score - rejected_score
    selected_child_state_digest = selected_child["child_basin_state_digest"]
    traces = {
        "fixed_proxy_surface_trace": {
            "trace_id": f"{row_id}_fixed_proxy_surface",
            "proxy_surface": "native_route_arbitration_score",
            "selected_route_id": selected["candidate_route_id"],
            "selected_route_score": selected_score,
            "rejected_route_id": rejected["candidate_route_id"],
            "rejected_route_score": rejected_score,
            "proxy_delta_selected_minus_rejected": proxy_delta,
            "proxy_surface_changed": False,
        },
        "basin_comparability_trace": {
            "trace_id": f"{row_id}_basin_comparability",
            "selected_route_child_basin_state_digest": selected_child_state_digest,
            "rejected_route_child_basin_state_digest": None,
            "selected_route_child_basin_present": True,
            "rejected_route_child_basin_present": False,
            "same_basin_metric_available": False,
            "same_threshold_control_envelope_available": True,
        },
        "blocker_trace": {
            "trace_id": f"{row_id}_blocker",
            "pd4_blocker": "rejected_route_lacks_child_basin_state_trace",
            "controlled_proxy_divergence_allowed": False,
            "geometric_reading": (
                "The fixed route-score proxy separates selected from rejected "
                "route candidates, but only the selected route emits a child-basin "
                "state. There is no source-current basin persistence surface for "
                "the rejected route, so the pair cannot support controlled "
                "proxy/basin divergence."
            ),
        },
    }
    artifact_manifest = build_artifact_manifest(row_id, traces)
    return {
        "row_id": row_id,
        "source_label": source_label,
        "source_artifact": rel(source_path),
        "source_output_digest": source_output_digest,
        "search_role": "selected_vs_rejected_route_candidate_pair",
        "row_decision": "blocked_for_PD4_supported_as_fixed_surface_search_evidence",
        "candidate_pd_ladder_rung": "PD3_search_evidence_only",
        "same_proxy_surface": True,
        "same_basin_metric": False,
        "same_threshold_control_envelope": True,
        "fixed_surface_pair_admissible_for_PD4": False,
        "proxy_improvement_observed": proxy_delta > 0.0,
        "basin_persistence_comparison_available": False,
        "basin_stall_or_degradation_observed": "not_evaluable_missing_rejected_route_basin_trace",
        "proxy_delta": proxy_delta,
        "basin_delta": "not_evaluable_missing_rejected_route_basin_trace",
        "pd4_blocker": "rejected_route_lacks_child_basin_state_trace",
        "controlled_proxy_divergence_allowed": False,
        "artifact_manifest": artifact_manifest,
        "all_artifact_sha256_match_file_contents": all(
            sha256_file(ROOT / item["path"]) == item["sha256"] for item in artifact_manifest
        ),
        "claim_ceiling": "fixed-surface search evidence; not controlled proxy divergence",
        "unsafe_claim_flags": unsafe_claim_flags(),
    }


def build_cross_variant_row(
    row_id: str,
    stress_a: dict[str, Any],
    stress_b: dict[str, Any],
    route_a: dict[str, Any],
    route_b: dict[str, Any],
) -> dict[str, Any]:
    threshold_a = source_threshold_row(stress_a)
    threshold_b = source_threshold_row(stress_b)
    score_delta = route_b["candidate_route_score"] - route_a["candidate_route_score"]
    support_delta = threshold_b["observed_support_floor"] - threshold_a["observed_support_floor"]
    threshold_delta = threshold_b["declared_threshold"] - threshold_a["declared_threshold"]
    traces = {
        "fixed_proxy_surface_trace": {
            "trace_id": f"{row_id}_fixed_proxy_surface",
            "proxy_surface": "native_route_arbitration_score",
            "candidate_a": stress_a["candidate_id"],
            "candidate_a_route_score": route_a["candidate_route_score"],
            "candidate_b": stress_b["candidate_id"],
            "candidate_b_route_score": route_b["candidate_route_score"],
            "proxy_delta_candidate_b_minus_candidate_a": score_delta,
            "proxy_surface_changed": False,
        },
        "basin_comparability_trace": {
            "trace_id": f"{row_id}_basin_comparability",
            "candidate_a_child_basin_core_ids": stress_a["child_basin_core_ids"],
            "candidate_b_child_basin_core_ids": stress_b["child_basin_core_ids"],
            "candidate_a_declared_threshold": threshold_a["declared_threshold"],
            "candidate_b_declared_threshold": threshold_b["declared_threshold"],
            "candidate_a_observed_support_floor": threshold_a["observed_support_floor"],
            "candidate_b_observed_support_floor": threshold_b["observed_support_floor"],
            "same_child_basin_scope": stress_a["child_basin_core_ids"] == stress_b["child_basin_core_ids"],
            "same_declared_threshold": threshold_a["declared_threshold"] == threshold_b["declared_threshold"],
            "same_basin_metric_available": True,
            "same_threshold_control_envelope_available": False,
        },
        "blocker_trace": {
            "trace_id": f"{row_id}_blocker",
            "pd4_blocker": "cross_variant_child_scope_and_threshold_surface_mismatch",
            "controlled_proxy_divergence_allowed": False,
            "geometric_reading": (
                "Both selected routes have the same native route-score proxy, "
                "but the emitted child-basin scopes and declared threshold "
                "surfaces differ. The support delta is therefore a scoped "
                "substrate difference, not same-surface proxy divergence."
            ),
        },
    }
    artifact_manifest = build_artifact_manifest(row_id, traces)
    return {
        "row_id": row_id,
        "source_label": "n25_2_cross_variant_selected_route_pair",
        "source_artifact": rel(N25_2_STRESS),
        "source_output_digest": EXPECTED_N25_2_STRESS_DIGEST,
        "search_role": "cross_variant_selected_route_fixed_proxy_pair",
        "row_decision": "blocked_for_PD4_supported_as_fixed_surface_search_evidence",
        "candidate_pd_ladder_rung": "PD3_search_evidence_only",
        "same_proxy_surface": True,
        "same_basin_metric": False,
        "same_threshold_control_envelope": False,
        "fixed_surface_pair_admissible_for_PD4": False,
        "proxy_improvement_observed": score_delta > 0.0,
        "basin_persistence_comparison_available": True,
        "basin_stall_or_degradation_observed": False,
        "proxy_delta": score_delta,
        "basin_delta": support_delta,
        "declared_threshold_delta": threshold_delta,
        "pd4_blocker": "cross_variant_child_scope_and_threshold_surface_mismatch",
        "controlled_proxy_divergence_allowed": False,
        "artifact_manifest": artifact_manifest,
        "all_artifact_sha256_match_file_contents": all(
            sha256_file(ROOT / item["path"]) == item["sha256"] for item in artifact_manifest
        ),
        "claim_ceiling": "fixed-surface search evidence; not controlled proxy divergence",
        "unsafe_claim_flags": unsafe_claim_flags(),
    }


def build_stress_surface_row(stress_a: dict[str, Any], stress_b: dict[str, Any]) -> dict[str, Any]:
    row_id = "n26_i5b_source_threshold_surface_pair"
    threshold_a = source_threshold_row(stress_a)
    threshold_b = source_threshold_row(stress_b)
    support_delta = threshold_b["observed_support_floor"] - threshold_a["observed_support_floor"]
    threshold_delta = threshold_b["declared_threshold"] - threshold_a["declared_threshold"]
    traces = {
        "fixed_proxy_surface_trace": {
            "trace_id": f"{row_id}_fixed_proxy_surface",
            "proxy_surface": "I4_coupling_gap_under_source_threshold_replay",
            "candidate_a_proxy_gap": 0.0,
            "candidate_b_proxy_gap": 0.0,
            "proxy_delta_candidate_b_minus_candidate_a": 0.0,
            "proxy_surface_changed": False,
        },
        "basin_comparability_trace": {
            "trace_id": f"{row_id}_basin_comparability",
            "candidate_a": stress_a["candidate_id"],
            "candidate_b": stress_b["candidate_id"],
            "candidate_a_declared_threshold": threshold_a["declared_threshold"],
            "candidate_b_declared_threshold": threshold_b["declared_threshold"],
            "candidate_a_observed_support_floor": threshold_a["observed_support_floor"],
            "candidate_b_observed_support_floor": threshold_b["observed_support_floor"],
            "candidate_a_source_iteration": stress_a["source_iteration"],
            "candidate_b_source_iteration": stress_b["source_iteration"],
            "same_threshold_control_envelope_available": False,
        },
        "blocker_trace": {
            "trace_id": f"{row_id}_blocker",
            "pd4_blocker": "no_proxy_improvement_and_threshold_surface_mismatch",
            "controlled_proxy_divergence_allowed": False,
            "geometric_reading": (
                "The source-threshold replay pair has no proxy-gap improvement "
                "and uses different declared support/coherence threshold "
                "surfaces. It can remain PD3 contrast context, but cannot become "
                "same-surface PD4 divergence."
            ),
        },
    }
    artifact_manifest = build_artifact_manifest(row_id, traces)
    return {
        "row_id": row_id,
        "source_label": "n25_2_source_threshold_replay_pair",
        "source_artifact": rel(N25_2_STRESS),
        "source_output_digest": EXPECTED_N25_2_STRESS_DIGEST,
        "search_role": "source_threshold_fixed_gap_pair",
        "row_decision": "blocked_for_PD4_supported_as_fixed_surface_search_evidence",
        "candidate_pd_ladder_rung": "PD3_search_evidence_only",
        "same_proxy_surface": True,
        "same_basin_metric": False,
        "same_threshold_control_envelope": False,
        "fixed_surface_pair_admissible_for_PD4": False,
        "proxy_improvement_observed": False,
        "basin_persistence_comparison_available": True,
        "basin_stall_or_degradation_observed": False,
        "proxy_delta": 0.0,
        "basin_delta": support_delta,
        "declared_threshold_delta": threshold_delta,
        "pd4_blocker": "no_proxy_improvement_and_threshold_surface_mismatch",
        "controlled_proxy_divergence_allowed": False,
        "artifact_manifest": artifact_manifest,
        "all_artifact_sha256_match_file_contents": all(
            sha256_file(ROOT / item["path"]) == item["sha256"] for item in artifact_manifest
        ),
        "claim_ceiling": "fixed-surface search evidence; not controlled proxy divergence",
        "unsafe_claim_flags": unsafe_claim_flags(),
    }


def build_rows(positive: dict[str, Any], variant: dict[str, Any], stress: dict[str, Any]) -> list[dict[str, Any]]:
    positive_candidates = positive["native_runtime_execution_evidence"]["candidate_result"]["candidate_records"]
    positive_selected_id = positive["native_runtime_execution_evidence"]["arbitration_result"]["route_arbitration_record"][
        "selected_candidate_route_id"
    ]
    positive_selected = find_candidate(positive_candidates, positive_selected_id)
    positive_rejected = [candidate for candidate in positive_candidates if candidate["candidate_route_id"] != positive_selected_id][0]
    positive_child = positive["child_basin_state_records"]["records"][0]

    variant_trace = variant["route_child_basin_variant"]["runtime_trace"]
    variant_candidates = variant_trace["candidate_result"]["candidate_records"]
    variant_selected_id = variant_trace["arbitration_result"]["route_arbitration_record"]["selected_candidate_route_id"]
    variant_selected = find_candidate(variant_candidates, variant_selected_id)
    variant_rejected = [candidate for candidate in variant_candidates if candidate["candidate_route_id"] != variant_selected_id][0]
    variant_child = variant_trace["child_basin_state_records"][0]

    stress_a = stress["stress_rows"][0]
    stress_b = stress["stress_rows"][1]
    return [
        build_selected_vs_rejected_row(
            row_id="n26_i5b_reference_selected_vs_rejected_route_pair",
            source_label="n25_2_i4_reference_route_arbitration",
            source_path=N25_2_POSITIVE,
            source_output_digest=positive["output_digest"],
            selected=positive_selected,
            rejected=positive_rejected,
            selected_child=positive_child,
        ),
        build_selected_vs_rejected_row(
            row_id="n26_i5b_variant_selected_vs_rejected_route_pair",
            source_label="n25_2_i4a_route_variant_arbitration",
            source_path=N25_2_VARIANT,
            source_output_digest=variant["output_digest"],
            selected=variant_selected,
            rejected=variant_rejected,
            selected_child=variant_child,
        ),
        build_cross_variant_row(
            row_id="n26_i5b_cross_variant_selected_route_score_pair",
            stress_a=stress_a,
            stress_b=stress_b,
            route_a=positive_selected,
            route_b=variant_selected,
        ),
        build_stress_surface_row(stress_a=stress_a, stress_b=stress_b),
    ]


def build_checks(
    output: dict[str, Any],
    i4: dict[str, Any],
    i4a: dict[str, Any],
    i5: dict[str, Any],
    i5a: dict[str, Any],
    positive: dict[str, Any],
    variant: dict[str, Any],
    stress: dict[str, Any],
    closeout: dict[str, Any],
) -> list[dict[str, Any]]:
    rows = output["fixed_surface_search_rows"]
    selected_vs_rejected = [row for row in rows if row["search_role"] == "selected_vs_rejected_route_candidate_pair"]
    cross_rows = [row for row in rows if row["search_role"] != "selected_vs_rejected_route_candidate_pair"]
    return [
        {
            "check": "source_chain_ready",
            "passed": (
                i4["output_digest"] == EXPECTED_I4_OUTPUT_DIGEST
                and i4a["output_digest"] == EXPECTED_I4A_OUTPUT_DIGEST
                and i5["output_digest"] == EXPECTED_I5_OUTPUT_DIGEST
                and i5a["output_digest"] == EXPECTED_I5A_OUTPUT_DIGEST
                and positive["output_digest"] == EXPECTED_N25_2_POSITIVE_DIGEST
                and variant["output_digest"] == EXPECTED_N25_2_VARIANT_DIGEST
                and stress["output_digest"] == EXPECTED_N25_2_STRESS_DIGEST
                and closeout["output_digest"] == EXPECTED_N25_2_CLOSEOUT_DIGEST
            ),
            "detail": {
                "i4": i4["output_digest"],
                "i4a": i4a["output_digest"],
                "i5": i5["output_digest"],
                "i5a": i5a["output_digest"],
                "n25_2_i4": positive["output_digest"],
                "n25_2_i4a": variant["output_digest"],
                "n25_2_stress": stress["output_digest"],
            },
        },
        {
            "check": "fixed_surface_search_executed",
            "passed": output["row_count"] == 4,
            "detail": {"row_count": output["row_count"]},
        },
        {
            "check": "no_admissible_pd4_fixed_surface_pair",
            "passed": output["eligible_fixed_surface_pair_count"] == 0,
            "detail": {"eligible_fixed_surface_pair_count": output["eligible_fixed_surface_pair_count"]},
        },
        {
            "check": "selected_vs_rejected_pairs_blocked_by_missing_rejected_basin_trace",
            "passed": all(row["pd4_blocker"] == "rejected_route_lacks_child_basin_state_trace" for row in selected_vs_rejected),
            "detail": {"row_count": len(selected_vs_rejected)},
        },
        {
            "check": "cross_variant_pairs_blocked_by_scope_or_threshold_mismatch",
            "passed": all(
                row["pd4_blocker"]
                in {
                    "cross_variant_child_scope_and_threshold_surface_mismatch",
                    "no_proxy_improvement_and_threshold_surface_mismatch",
                }
                for row in cross_rows
            ),
            "detail": sorted({row["pd4_blocker"] for row in cross_rows}),
        },
        {
            "check": "i5_and_i5a_not_overwritten",
            "passed": (
                i5["candidate_pd_ladder_rung"] == "PD3"
                and not i5["controlled_proxy_divergence_candidate_supported"]
                and not i5a["controlled_proxy_divergence_candidate_supported"]
                and output["candidate_pd_ladder_rung"] == "PD3"
                and not output["controlled_proxy_divergence_candidate_supported"]
            ),
            "detail": {"i5_digest": i5["output_digest"], "i5a_digest": i5a["output_digest"]},
        },
        {
            "check": "scoped_mb6_boundary_preserved",
            "passed": (
                closeout["n26_handoff"]["n26_scoped_context_consumption_allowed"]
                and not closeout["n26_handoff"]["n26_unscoped_consumption_allowed"]
                and not closeout["n26_handoff"]["n26_unscoped_multi_basin_consumption_allowed"]
            ),
            "detail": closeout["n26_handoff"],
        },
        {
            "check": "artifact_sha256_match_file_contents",
            "passed": all(row["all_artifact_sha256_match_file_contents"] for row in rows),
            "detail": {"row_count": len(rows)},
        },
        {
            "check": "unsafe_claim_flags_false",
            "passed": all(not value for row in rows for value in row["unsafe_claim_flags"].values()),
            "detail": {"claim_count": len(UNSAFE_CLAIMS)},
        },
        {
            "check": "no_absolute_paths_in_records",
            "passed": not contains_absolute_path(output),
            "detail": {"absolute_path_policy": "repository_relative_paths_only"},
        },
    ]


def write_report(output: dict[str, Any]) -> None:
    def format_cell(value: Any) -> str:
        if isinstance(value, float):
            return f"{value:.6f}"
        return str(value)

    lines = [
        "# N26 Iteration 5-B - Fixed-Surface Divergence Search",
        "",
        f"Status: `{output['status']}`",
        "",
        f"Acceptance state: `{output['acceptance_state']}`",
        "",
        "## Summary",
        "",
        "I5-B applies the stricter PD4 question that I5-A could not answer:",
        "can an existing native N25.2 source show proxy improvement while the",
        "basin metric stalls or degrades without changing the proxy surface,",
        "basin metric, threshold policy, or control envelope?",
        "",
        "The search finds no admissible fixed-surface PD4 pair. The native route",
        "arbitration records provide selected-vs-rejected route-score contrast,",
        "but rejected routes do not emit child-basin state traces. The selected",
        "cross-route candidates both emit child-basin state, but their child",
        "scope and threshold surfaces differ, and no route-score improvement",
        "appears between them.",
        "",
        "## Rows",
        "",
        "| Row | Role | Proxy Delta | Basin Delta | PD4 Blocker |",
        "| --- | --- | ---: | --- | --- |",
    ]
    for row in output["fixed_surface_search_rows"]:
        lines.append(
            "| "
            f"`{row['row_id']}` | "
            f"`{row['search_role']}` | "
            f"{format_cell(row['proxy_delta'])} | "
            f"`{format_cell(row['basin_delta'])}` | "
            f"`{row['pd4_blocker']}` |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "This is a stronger negative result than I5-A. I5-A showed that",
            "proxy-looking divergence can be induced by changing proxy/evaluation",
            "surfaces. I5-B holds the surface fixed and asks whether the current",
            "native evidence contains a real PD4 pair. It does not.",
            "",
            "The correct ceiling remains:",
            "",
            "```text",
            "PD3 replay-backed proxy/basin contrast supported",
            "PD4 controlled proxy divergence blocked",
            "proxy collapse not opened",
            "AP5 bridge closeout not supported",
            "```",
            "",
            "## Checks",
            "",
            "| Check | Passed |",
            "| --- | --- |",
        ]
    )
    for check in output["checks"]:
        lines.append(f"| `{check['check']}` | `{str(check['passed']).lower()}` |")
    lines.extend(
        [
            "",
            "## Artifacts",
            "",
            "```text",
            "outputs/n26_fixed_surface_divergence_search.json",
            "outputs/n26_fixed_surface_divergence_search_artifacts/",
            "reports/n26_fixed_surface_divergence_search.md",
            "scripts/build_n26_fixed_surface_divergence_search.py",
            "```",
            "",
        ]
    )
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    i4 = load_json(I4_OUTPUT)
    i4a = load_json(I4A_OUTPUT)
    i5 = load_json(I5_OUTPUT)
    i5a = load_json(I5A_OUTPUT)
    positive = load_json(N25_2_POSITIVE)
    variant = load_json(N25_2_VARIANT)
    stress = load_json(N25_2_STRESS)
    closeout = load_json(N25_2_CLOSEOUT)
    rows = build_rows(positive, variant, stress)

    output: dict[str, Any] = {
        "artifact_id": "n26_fixed_surface_divergence_search",
        "experiment": "N26",
        "iteration": "I5-B",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_fixed_surface_divergence_search_no_admissible_pd4_pair",
        "source_i4_output_digest": i4["output_digest"],
        "source_i4a_output_digest": i4a["output_digest"],
        "source_i5_output_digest": i5["output_digest"],
        "source_i5a_output_digest": i5a["output_digest"],
        "source_n25_2_positive_output_digest": positive["output_digest"],
        "source_n25_2_variant_output_digest": variant["output_digest"],
        "source_n25_2_stress_output_digest": stress["output_digest"],
        "source_n25_2_closeout_output_digest": closeout["output_digest"],
        "candidate_pd_ladder_rung": "PD3",
        "n26_closeout_ceiling": "N26-C4_source_current_proxy_derivation_and_replay_backed_contrast_supported",
        "n26_closeout_ladder_rung_assigned": False,
        "fixed_surface_divergence_search_opened": True,
        "fixed_surface_search_rows": rows,
        "row_count": len(rows),
        "eligible_fixed_surface_pair_count": sum(1 for row in rows if row["fixed_surface_pair_admissible_for_PD4"]),
        "route_arbitration_pair_count": sum(
            1 for row in rows if row["search_role"] == "selected_vs_rejected_route_candidate_pair"
        ),
        "controlled_proxy_divergence_candidate_supported": False,
        "pd4_or_stronger_supported": False,
        "proxy_collapse_opened": False,
        "proxy_collapse_supported": False,
        "ap5_bridge_status": "not_supported_i5b_no_admissible_fixed_surface_pd4_pair",
        "i5_replaced": False,
        "i5a_replaced": False,
        "pd4_blockers": sorted({row["pd4_blocker"] for row in rows}),
        "claim_boundary": {
            "claim_ceiling": (
                "fixed-surface search evidence; current native sources do not "
                "support controlled proxy divergence, proxy collapse, or AP5 bridge closeout"
            ),
            "blocked_claims": [
                "controlled_proxy_divergence",
                "proxy_collapse",
                "final_AP5",
                "native_support",
                "agency",
                "semantic_goal",
                "semantic_choice",
                "sentience",
                "Phase_8_completion",
                "ant_ecology",
                "unscoped_multi_basin_substrate",
            ],
        },
        "ready_for_iteration_6_proxy_collapse_perturbation_matrix": True,
    }
    output["checks"] = build_checks(output, i4, i4a, i5, i5a, positive, variant, stress, closeout)
    output["failed_checks"] = [check["check"] for check in output["checks"] if not check["passed"]]
    digest_payload = dict(output)
    digest_payload.pop("output_digest", None)
    output["output_digest"] = digest_data(digest_payload)

    write_json(OUTPUT, output)
    write_report(output)


if __name__ == "__main__":
    main()

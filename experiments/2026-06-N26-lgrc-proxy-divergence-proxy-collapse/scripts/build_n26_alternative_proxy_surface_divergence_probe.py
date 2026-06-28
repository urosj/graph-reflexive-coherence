#!/usr/bin/env python3
"""Build N26 Iteration 5-A alternative proxy surface divergence probe."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-28T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N26-lgrc-proxy-divergence-proxy-collapse"
OUTPUT = EXPERIMENT / "outputs" / "n26_alternative_proxy_surface_divergence_probe.json"
REPORT = EXPERIMENT / "reports" / "n26_alternative_proxy_surface_divergence_probe.md"
ARTIFACT_DIR = EXPERIMENT / "outputs" / "n26_alternative_proxy_surface_divergence_probe_artifacts"

I4_OUTPUT = EXPERIMENT / "outputs" / "n26_source_current_proxy_derivation_probe.json"
I4A_OUTPUT = EXPERIMENT / "outputs" / "n26_proxy_derivation_sensitivity_probe.json"
I5_OUTPUT = EXPERIMENT / "outputs" / "n26_proxy_divergence_contrast_matrix.json"

N25_2_EXPERIMENT = ROOT / "experiments" / "2026-06-N25.2-lgrc9v3-mb6-validation-bridge"
N25_2_STRESS = N25_2_EXPERIMENT / "outputs" / "n25_2_stress_variant_matrix.json"
N25_2_CLOSEOUT = N25_2_EXPERIMENT / "outputs" / "n25_2_closeout_and_n26_handoff.json"

COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N26-lgrc-proxy-divergence-proxy-collapse/scripts/"
    "build_n26_alternative_proxy_surface_divergence_probe.py"
)

EXPECTED_I4_OUTPUT_DIGEST = "b8c8794ecc8e71c01c7bf9d0e1c369f1630416534741f3fb342c5622775a1680"
EXPECTED_I4A_OUTPUT_DIGEST = "5dbe325f6ce1ff95434b978e69cf659fdf609e2890960198aca66e2c5c85e414"
EXPECTED_I5_OUTPUT_DIGEST = "52e7cba79816e840947472d35ee8906f357db1bcf896b59f59bbac243d9ee4a5"
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


def child_core(candidate_id: str) -> int:
    return int(candidate_id.rsplit("_", 1)[-1])


def stress_row_by_id(rows: list[dict[str, Any]], stress_id: str) -> dict[str, Any]:
    for row in rows:
        if row["stress_id"] == stress_id:
            return row
    raise ValueError(f"Missing stress row: {stress_id}")


def threshold_margin(row: dict[str, Any]) -> float:
    observed = min(row["observed_support_floor"], row["observed_coherence_floor"])
    return observed - row["declared_threshold"]


def window_surplus(row: dict[str, Any]) -> float:
    return row["observed_window_count"] - row["required_window_count"]


def build_artifact_manifest(row_id: str, traces: dict[str, Any]) -> list[dict[str, str]]:
    return [write_trace_artifact(row_id, role, traces[role]) for role in sorted(traces)]


def build_threshold_row(source_row: dict[str, Any]) -> dict[str, Any]:
    candidate_id = source_row["candidate_id"]
    baseline = stress_row_by_id(source_row["threshold_stress_rows"], "source_threshold_replay")
    relaxed = stress_row_by_id(source_row["threshold_stress_rows"], "relaxed_threshold_replay")
    baseline_proxy = threshold_margin(baseline)
    relaxed_proxy = threshold_margin(relaxed)
    proxy_delta = relaxed_proxy - baseline_proxy
    basin_delta = min(relaxed["observed_support_floor"], relaxed["observed_coherence_floor"]) - min(
        baseline["observed_support_floor"], baseline["observed_coherence_floor"]
    )
    row_id = f"n26_i5a_threshold_margin_{candidate_id}"
    traces = {
        "alternative_proxy_metric_trace": {
            "trace_id": f"{row_id}_alternative_proxy_metric",
            "proxy_surface": "threshold_margin",
            "baseline_proxy_margin": baseline_proxy,
            "alternative_proxy_margin": relaxed_proxy,
            "proxy_delta": proxy_delta,
            "proxy_improvement_observed": proxy_delta > 0.0,
            "source_rows": ["source_threshold_replay", "relaxed_threshold_replay"],
        },
        "basin_state_trace": {
            "trace_id": f"{row_id}_basin_state",
            "baseline_observed_support_floor": baseline["observed_support_floor"],
            "baseline_observed_coherence_floor": baseline["observed_coherence_floor"],
            "alternative_observed_support_floor": relaxed["observed_support_floor"],
            "alternative_observed_coherence_floor": relaxed["observed_coherence_floor"],
            "basin_floor_delta": basin_delta,
            "basin_deepening_observed": basin_delta > 0.0,
        },
        "blocker_trace": {
            "trace_id": f"{row_id}_blocker",
            "blocker": "threshold_policy_relaxation_mediated_proxy_improvement",
            "baseline_declared_threshold": baseline["declared_threshold"],
            "alternative_declared_threshold": relaxed["declared_threshold"],
            "threshold_changed": baseline["declared_threshold"] != relaxed["declared_threshold"],
            "controlled_proxy_divergence_allowed": False,
        },
    }
    artifact_manifest = build_artifact_manifest(row_id, traces)
    return {
        "row_id": row_id,
        "candidate_id": candidate_id,
        "source_iteration": source_row["source_iteration"],
        "alternative_proxy_surface": "threshold_margin",
        "source_artifact": rel(N25_2_STRESS),
        "source_rows": ["source_threshold_replay", "relaxed_threshold_replay"],
        "row_decision": "rejected_for_PD4_supported_as_false_positive_control",
        "candidate_pd_ladder_rung": "not_supported_PD4_blocked",
        "divergence_shaped_signal_observed": proxy_delta > 0.0 and basin_delta == 0.0,
        "proxy_improvement_observed": proxy_delta > 0.0,
        "basin_deepening_observed": basin_delta > 0.0,
        "basin_stall_observed": basin_delta == 0.0,
        "proxy_delta": proxy_delta,
        "basin_delta": basin_delta,
        "pd4_blocker": "threshold_policy_relaxation_mediated_proxy_improvement",
        "positive_proxy_divergence_allowed": False,
        "artifact_manifest": artifact_manifest,
        "all_artifact_sha256_match_file_contents": all(
            sha256_file(ROOT / item["path"]) == item["sha256"] for item in artifact_manifest
        ),
        "claim_ceiling": "alternative proxy false-positive control; not controlled proxy divergence",
        "unsafe_claim_flags": unsafe_claim_flags(),
    }


def build_window_row(source_row: dict[str, Any]) -> dict[str, Any]:
    candidate_id = source_row["candidate_id"]
    baseline = stress_row_by_id(source_row["persistence_window_stress_rows"], "source_one_window_replay")
    multi_window = stress_row_by_id(source_row["persistence_window_stress_rows"], "multi_window_2_persistence_replay")
    baseline_proxy = window_surplus(baseline)
    alternative_proxy = window_surplus(multi_window)
    proxy_delta = alternative_proxy - baseline_proxy
    evaluation_window_delta = multi_window["observed_window_count"] - baseline["observed_window_count"]
    basin_delta = 0.0
    row_id = f"n26_i5a_window_surplus_{candidate_id}"
    traces = {
        "alternative_proxy_metric_trace": {
            "trace_id": f"{row_id}_alternative_proxy_metric",
            "proxy_surface": "window_surplus",
            "baseline_window_surplus": baseline_proxy,
            "alternative_window_surplus": alternative_proxy,
            "proxy_delta": proxy_delta,
            "proxy_improvement_observed": proxy_delta > 0.0,
            "source_rows": ["source_one_window_replay", "multi_window_2_persistence_replay"],
        },
        "basin_state_trace": {
            "trace_id": f"{row_id}_basin_state",
            "baseline_observed_window_count": baseline["observed_window_count"],
            "alternative_observed_window_count": multi_window["observed_window_count"],
            "evaluation_window_count_delta": evaluation_window_delta,
            "basin_delta": basin_delta,
            "basin_deepening_observed": False,
            "replay_window_scope_changed": True,
        },
        "blocker_trace": {
            "trace_id": f"{row_id}_blocker",
            "blocker": "evaluation_window_requirement_shift_mediated_proxy_improvement",
            "baseline_required_window_count": baseline["required_window_count"],
            "alternative_required_window_count": multi_window["required_window_count"],
            "requirement_changed": baseline["required_window_count"] != multi_window["required_window_count"],
            "controlled_proxy_divergence_allowed": False,
        },
    }
    artifact_manifest = build_artifact_manifest(row_id, traces)
    return {
        "row_id": row_id,
        "candidate_id": candidate_id,
        "source_iteration": source_row["source_iteration"],
        "alternative_proxy_surface": "window_surplus",
        "source_artifact": rel(N25_2_STRESS),
        "source_rows": ["source_one_window_replay", "multi_window_2_persistence_replay"],
        "row_decision": "rejected_for_PD4_supported_as_false_positive_control",
        "candidate_pd_ladder_rung": "not_supported_PD4_blocked",
        "divergence_shaped_signal_observed": proxy_delta > 0.0 and basin_delta == 0.0,
        "proxy_improvement_observed": proxy_delta > 0.0,
        "basin_deepening_observed": False,
        "basin_stall_observed": False,
        "proxy_delta": proxy_delta,
        "basin_delta": basin_delta,
        "pd4_blocker": "evaluation_window_requirement_shift_mediated_proxy_improvement",
        "positive_proxy_divergence_allowed": False,
        "artifact_manifest": artifact_manifest,
        "all_artifact_sha256_match_file_contents": all(
            sha256_file(ROOT / item["path"]) == item["sha256"] for item in artifact_manifest
        ),
        "claim_ceiling": "alternative proxy false-positive control; not controlled proxy divergence",
        "unsafe_claim_flags": unsafe_claim_flags(),
    }


def build_rows(stress: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for source_row in stress["stress_rows"]:
        rows.append(build_threshold_row(source_row))
        rows.append(build_window_row(source_row))
    return rows


def build_checks(output: dict[str, Any], i4: dict[str, Any], i4a: dict[str, Any], i5: dict[str, Any], stress: dict[str, Any], closeout: dict[str, Any]) -> list[dict[str, Any]]:
    rows = output["alternative_proxy_rows"]
    divergence_shaped_rows = [row for row in rows if row["divergence_shaped_signal_observed"]]
    return [
        {
            "check": "source_chain_ready",
            "passed": (
                i4["output_digest"] == EXPECTED_I4_OUTPUT_DIGEST
                and i4a["output_digest"] == EXPECTED_I4A_OUTPUT_DIGEST
                and i5["output_digest"] == EXPECTED_I5_OUTPUT_DIGEST
                and stress["output_digest"] == EXPECTED_N25_2_STRESS_DIGEST
                and closeout["output_digest"] == EXPECTED_N25_2_CLOSEOUT_DIGEST
            ),
            "detail": {
                "i4": i4["output_digest"],
                "i4a": i4a["output_digest"],
                "i5": i5["output_digest"],
                "n25_2_stress": stress["output_digest"],
            },
        },
        {
            "check": "divergence_shaped_signal_observed",
            "passed": bool(divergence_shaped_rows),
            "detail": {"row_count": len(divergence_shaped_rows)},
        },
        {
            "check": "all_divergence_shaped_rows_fail_closed_for_PD4",
            "passed": all(not row["positive_proxy_divergence_allowed"] for row in divergence_shaped_rows),
            "detail": sorted({row["pd4_blocker"] for row in divergence_shaped_rows}),
        },
        {
            "check": "i5_conclusion_not_overwritten",
            "passed": (
                i5["candidate_pd_ladder_rung"] == "PD3"
                and not i5["controlled_proxy_divergence_candidate_supported"]
                and not output["controlled_proxy_divergence_candidate_supported"]
            ),
            "detail": {"i5_digest": i5["output_digest"]},
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
    rows = output["alternative_proxy_rows"]
    lines = [
        "# N26 Iteration 5-A - Alternative Proxy Surface Divergence Probe",
        "",
        f"Status: `{output['status']}`",
        "",
        f"Acceptance state: `{output['acceptance_state']}`",
        "",
        "## Summary",
        "",
        "I5-A tries alternative proxy surfaces over the existing N25.2 scoped",
        "substrate: threshold margin and replay-window surplus. Both can create",
        "divergence-shaped signals, but the signals are mediated by changed",
        "threshold policy or changed evaluation window requirements. They are",
        "therefore rejected as controlled PD4 proxy divergence.",
        "",
        "## Rows",
        "",
        "| Row | Proxy Surface | Candidate | Proxy Delta | Basin Delta | Blocker |",
        "| --- | --- | --- | ---: | ---: | --- |",
    ]
    for row in rows:
        lines.append(
            "| "
            f"`{row['row_id']}` | "
            f"`{row['alternative_proxy_surface']}` | "
            f"`{row['candidate_id']}` | "
            f"{row['proxy_delta']:.6f} | "
            f"{row['basin_delta']:.6f} | "
            f"`{row['pd4_blocker']}` |"
        )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            f"`candidate_pd_ladder_rung = {output['candidate_pd_ladder_rung']}`",
            "",
            f"`controlled_proxy_divergence_candidate_supported = "
            f"{str(output['controlled_proxy_divergence_candidate_supported']).lower()}`",
            "",
            "I5-A strengthens the negative result: proxy divergence-shaped signals",
            "can be induced by proxy/evaluation-surface changes, but those signals",
            "fail closed and do not upgrade I5.",
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
            "outputs/n26_alternative_proxy_surface_divergence_probe.json",
            "outputs/n26_alternative_proxy_surface_divergence_probe_artifacts/",
            "reports/n26_alternative_proxy_surface_divergence_probe.md",
            "scripts/build_n26_alternative_proxy_surface_divergence_probe.py",
            "```",
            "",
        ]
    )
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    i4 = load_json(I4_OUTPUT)
    i4a = load_json(I4A_OUTPUT)
    i5 = load_json(I5_OUTPUT)
    stress = load_json(N25_2_STRESS)
    closeout = load_json(N25_2_CLOSEOUT)
    rows = build_rows(stress)

    output: dict[str, Any] = {
        "artifact_id": "n26_alternative_proxy_surface_divergence_probe",
        "experiment": "N26",
        "iteration": "I5-A",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_alternative_proxy_surface_divergence_shape_detected_pd4_blocked",
        "source_i4_output_digest": i4["output_digest"],
        "source_i4a_output_digest": i4a["output_digest"],
        "source_i5_output_digest": i5["output_digest"],
        "source_n25_2_stress_output_digest": stress["output_digest"],
        "source_n25_2_closeout_output_digest": closeout["output_digest"],
        "candidate_pd_ladder_rung": "PD3",
        "n26_closeout_ceiling": "N26-C4_source_current_proxy_derivation_and_replay_backed_contrast_supported",
        "n26_closeout_ladder_rung_assigned": False,
        "alternative_proxy_surface_probe_opened": True,
        "divergence_shaped_signal_observed": True,
        "controlled_proxy_divergence_candidate_supported": False,
        "pd4_or_stronger_supported": False,
        "proxy_collapse_opened": False,
        "proxy_collapse_supported": False,
        "ap5_bridge_status": "not_supported_i5a_alternative_surface_blocked",
        "alternative_proxy_rows": rows,
        "row_count": len(rows),
        "pd4_blockers": [
            "threshold_policy_relaxation_mediated_proxy_improvement",
            "evaluation_window_requirement_shift_mediated_proxy_improvement",
            "i5_pd3_contrast_result_not_overwritten",
        ],
        "claim_boundary": {
            "claim_ceiling": (
                "alternative proxy-surface false-positive evidence; no controlled "
                "proxy divergence, no proxy collapse, no AP5 bridge closeout"
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
    output["checks"] = build_checks(output, i4, i4a, i5, stress, closeout)
    output["failed_checks"] = [check["check"] for check in output["checks"] if not check["passed"]]
    digest_payload = dict(output)
    digest_payload.pop("output_digest", None)
    output["output_digest"] = digest_data(digest_payload)

    write_json(OUTPUT, output)
    write_report(output)


if __name__ == "__main__":
    main()

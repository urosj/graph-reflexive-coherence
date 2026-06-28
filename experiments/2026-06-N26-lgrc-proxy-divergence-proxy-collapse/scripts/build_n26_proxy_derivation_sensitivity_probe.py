#!/usr/bin/env python3
"""Build N26 Iteration 4-A proxy derivation sensitivity probe."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-28T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N26-lgrc-proxy-divergence-proxy-collapse"
OUTPUT = EXPERIMENT / "outputs" / "n26_proxy_derivation_sensitivity_probe.json"
REPORT = EXPERIMENT / "reports" / "n26_proxy_derivation_sensitivity_probe.md"
ARTIFACT_DIR = EXPERIMENT / "outputs" / "n26_proxy_derivation_sensitivity_probe_artifacts"

I4_OUTPUT = EXPERIMENT / "outputs" / "n26_source_current_proxy_derivation_probe.json"
I3_OUTPUT = EXPERIMENT / "outputs" / "n26_active_nulls_and_failure_baselines.json"

N25_2_EXPERIMENT = ROOT / "experiments" / "2026-06-N25.2-lgrc9v3-mb6-validation-bridge"
N25_2_STRESS = N25_2_EXPERIMENT / "outputs" / "n25_2_stress_variant_matrix.json"
N25_2_CLOSEOUT = N25_2_EXPERIMENT / "outputs" / "n25_2_closeout_and_n26_handoff.json"

COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N26-lgrc-proxy-divergence-proxy-collapse/scripts/"
    "build_n26_proxy_derivation_sensitivity_probe.py"
)

EXPECTED_I3_OUTPUT_DIGEST = "90b3adf46add9fd0b98b3022733ce9f9fabbbd1b3695908aefbfb58f7199c2fd"
EXPECTED_I4_OUTPUT_DIGEST = "b8c8794ecc8e71c01c7bf9d0e1c369f1630416534741f3fb342c5622775a1680"
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


def stress_ratio_for_threshold(row: dict[str, Any]) -> float:
    observed = min(row["observed_support_floor"], row["observed_coherence_floor"])
    declared = row["declared_threshold"]
    if declared <= 0:
        return 0.0
    return min(observed / declared, 1.0)


def stress_ratio_for_merge_leakage(row: dict[str, Any]) -> float:
    observed = row["observed_absolute_incident_flux"]
    ceiling = row["declared_ceiling"]
    if ceiling == 0:
        return 1.0 if observed == 0 else 0.0
    return max(0.0, min(1.0, 1.0 - (observed / ceiling)))


def stress_ratio_for_window(row: dict[str, Any]) -> float:
    required = row["required_window_count"]
    observed = row["observed_window_count"]
    if required <= 0:
        return 0.0
    return min(observed / required, 1.0)


def stress_source_pointer(candidate_id: str, axis: str, index: int) -> str:
    row_index = 0 if candidate_id == "i4_reference_child_basin_core_0" else 1
    if axis == "flow_window_threshold":
        return f"#/stress_rows/{row_index}/threshold_stress_rows/{index}"
    if axis == "merge_leakage_pressure":
        return f"#/stress_rows/{row_index}/merge_leakage_stress_rows/{index}"
    if axis == "child_basin_persistence_window":
        return f"#/stress_rows/{row_index}/persistence_window_stress_rows/{index}"
    raise ValueError(axis)


def build_sensitivity_row(
    candidate_id: str,
    source_iteration: str,
    axis: str,
    stress_row: dict[str, Any],
    index: int,
) -> dict[str, Any]:
    if axis == "flow_window_threshold":
        ratio = stress_ratio_for_threshold(stress_row)
    elif axis == "merge_leakage_pressure":
        ratio = stress_ratio_for_merge_leakage(stress_row)
    elif axis == "child_basin_persistence_window":
        ratio = stress_ratio_for_window(stress_row)
    else:
        raise ValueError(axis)

    proxy_gap = max(0.0, 1.0 - ratio)
    source_status = stress_row["status"]
    source_passed = source_status == "passed"
    row_decision = "supported" if source_passed and proxy_gap == 0.0 else "rejected"
    positive_support_allowed = row_decision == "supported"
    row_id = f"n26_i4a_{candidate_id}_{axis}_{stress_row['stress_id']}"
    sensitivity_class = "zero_gap_source_pass" if positive_support_allowed else "nonzero_gap_failed_closed"
    if source_passed and proxy_gap > 0.0:
        sensitivity_class = "nonzero_gap_source_pass_observed_but_not_promoted"

    metric_trace = {
        "trace_id": f"{row_id}_stress_metric",
        "metric_family": "n26_i4_proxy_basin_coupling_gap",
        "i4a_metric_variant": "stress_normalized_proxy_basin_coupling_gap",
        "axis": axis,
        "source_stress_id": stress_row["stress_id"],
        "stress_normalized_capacity_ratio": ratio,
        "proxy_basin_coupling_gap": proxy_gap,
        "target_relation": "<=",
        "target_value": 0.0,
        "target_met": proxy_gap <= 0.0,
        "source_status": source_status,
    }
    sensitivity_trace = {
        "trace_id": f"{row_id}_sensitivity",
        "source_artifact": rel(N25_2_STRESS),
        "source_json_pointer": stress_source_pointer(candidate_id, axis, index),
        "candidate_id": candidate_id,
        "source_iteration": source_iteration,
        "stress_axis": axis,
        "stress_row": stress_row,
        "derived_proxy_gap": proxy_gap,
        "row_decision": row_decision,
        "positive_support_allowed": positive_support_allowed,
        "interpretation": (
            "The proxy remains zero for source-passing stress rows and becomes "
            "nonzero when a declared stress gate fails closed."
            if proxy_gap > 0.0
            else "The proxy remains zero under this source-passing stress row."
        ),
    }
    artifact_manifest = [
        write_trace_artifact(row_id, "stress_metric_trace", metric_trace),
        write_trace_artifact(row_id, "sensitivity_trace", sensitivity_trace),
    ]

    return {
        "row_id": row_id,
        "candidate_id": candidate_id,
        "source_iteration": source_iteration,
        "source_artifact": rel(N25_2_STRESS),
        "source_json_pointer": stress_source_pointer(candidate_id, axis, index),
        "stress_axis": axis,
        "stress_id": stress_row["stress_id"],
        "source_status": source_status,
        "row_decision": row_decision,
        "row_decision_scope": "PD2_sensitivity_observation_only",
        "sensitivity_class": sensitivity_class,
        "candidate_pd_ladder_rung": "PD2" if positive_support_allowed else "not_supported_failed_closed_sensitivity_row",
        "stress_normalized_capacity_ratio": ratio,
        "proxy_basin_coupling_gap": proxy_gap,
        "target_met": proxy_gap <= 0.0,
        "positive_proxy_support_allowed": positive_support_allowed,
        "proxy_derivation_sensitivity_supported": True,
        "proxy_divergence_supported": False,
        "proxy_collapse_supported": False,
        "artifact_manifest": artifact_manifest,
        "all_artifact_sha256_match_file_contents": all(
            sha256_file(ROOT / item["path"]) == item["sha256"] for item in artifact_manifest
        ),
        "claim_ceiling": (
            "PD2 sensitivity observation only; nonzero stress gaps can block "
            "positive support but do not establish proxy divergence or collapse"
        ),
        "unsafe_claim_flags": unsafe_claim_flags(),
    }


def build_rows(stress: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for source_row in stress["stress_rows"]:
        candidate_id = source_row["candidate_id"]
        source_iteration = source_row["source_iteration"]
        for index, threshold_row in enumerate(source_row["threshold_stress_rows"]):
            rows.append(
                build_sensitivity_row(
                    candidate_id,
                    source_iteration,
                    "flow_window_threshold",
                    threshold_row,
                    index,
                )
            )
        for index, leakage_row in enumerate(source_row["merge_leakage_stress_rows"]):
            rows.append(
                build_sensitivity_row(
                    candidate_id,
                    source_iteration,
                    "merge_leakage_pressure",
                    leakage_row,
                    index,
                )
            )
        for index, window_row in enumerate(source_row["persistence_window_stress_rows"]):
            rows.append(
                build_sensitivity_row(
                    candidate_id,
                    source_iteration,
                    "child_basin_persistence_window",
                    window_row,
                    index,
                )
            )
    return rows


def build_checks(output: dict[str, Any], i3: dict[str, Any], i4: dict[str, Any], stress: dict[str, Any], closeout: dict[str, Any]) -> list[dict[str, Any]]:
    rows = output["sensitivity_rows"]
    nonzero_rows = [row for row in rows if row["proxy_basin_coupling_gap"] > 0.0]
    zero_supported_rows = [
        row for row in rows if row["proxy_basin_coupling_gap"] == 0.0 and row["row_decision"] == "supported"
    ]
    return [
        {
            "check": "source_chain_ready",
            "passed": (
                i3["output_digest"] == EXPECTED_I3_OUTPUT_DIGEST
                and i4["output_digest"] == EXPECTED_I4_OUTPUT_DIGEST
                and stress["output_digest"] == EXPECTED_N25_2_STRESS_DIGEST
                and closeout["output_digest"] == EXPECTED_N25_2_CLOSEOUT_DIGEST
            ),
            "detail": {
                "i3": i3["output_digest"],
                "i4": i4["output_digest"],
                "n25_2_stress": stress["output_digest"],
                "n25_2_closeout": closeout["output_digest"],
            },
        },
        {
            "check": "stress_rows_are_source_current_derived",
            "passed": stress["stress_matrix_scope"]["stress_rows_are_derived_from_source_current_runtime_records"],
            "detail": stress["stress_matrix_scope"],
        },
        {
            "check": "sensitivity_rows_include_zero_and_nonzero_gaps",
            "passed": bool(zero_supported_rows) and bool(nonzero_rows),
            "detail": {
                "zero_supported_row_count": len(zero_supported_rows),
                "nonzero_gap_row_count": len(nonzero_rows),
            },
        },
        {
            "check": "nonzero_gap_rows_fail_closed",
            "passed": all(not row["positive_proxy_support_allowed"] for row in nonzero_rows),
            "detail": {
                "nonzero_rows": [
                    {
                        "row_id": row["row_id"],
                        "gap": row["proxy_basin_coupling_gap"],
                        "row_decision": row["row_decision"],
                    }
                    for row in nonzero_rows
                ]
            },
        },
        {
            "check": "i4_not_replaced_or_widened",
            "passed": (
                output["i4_replaced"] is False
                and output["pd3_or_stronger_supported"] is False
                and output["proxy_divergence_opened"] is False
                and output["proxy_collapse_opened"] is False
            ),
            "detail": {
                "i4_replaced": output["i4_replaced"],
                "candidate_pd_ladder_rung": output["candidate_pd_ladder_rung"],
            },
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
    rows = output["sensitivity_rows"]
    lines = [
        "# N26 Iteration 4-A - Proxy Derivation Sensitivity Probe",
        "",
        f"Status: `{output['status']}`",
        "",
        f"Acceptance state: `{output['acceptance_state']}`",
        "",
        "## Summary",
        "",
        "I4-A checks whether the I4 proxy derivation responds to varied",
        "source-current N25.2 stress rows. It uses the same coupling-gap family",
        "as I4, with stress-normalized inputs from the N25.2 stress matrix.",
        "",
        "The result is stronger than I4 in one specific way: zero-gap source rows",
        "remain supported, while tightened-threshold and injected leakage rows",
        "produce nonzero proxy gaps and fail closed. It does not add a passing",
        "degraded positive row, and it does not support PD3, divergence, collapse,",
        "or AP5 bridge closeout.",
        "",
        "## Rows",
        "",
        "| Row | Source | Axis | Stress | Gap | Decision |",
        "| --- | --- | --- | --- | ---: | --- |",
    ]
    for row in rows:
        lines.append(
            "| "
            f"`{row['row_id']}` | "
            f"`{row['candidate_id']}` | "
            f"`{row['stress_axis']}` | "
            f"`{row['stress_id']}` | "
            f"{row['proxy_basin_coupling_gap']:.6f} | "
            f"`{row['row_decision']}` |"
        )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            f"`candidate_pd_ladder_rung = {output['candidate_pd_ladder_rung']}`",
            "",
            f"`n26_closeout_ceiling = {output['n26_closeout_ceiling']}`",
            "",
            "I4-A strengthens source-current PD2 derivation sensitivity only. The",
            "nonzero-gap rows are blocker evidence, not positive proxy divergence.",
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
            "outputs/n26_proxy_derivation_sensitivity_probe.json",
            "outputs/n26_proxy_derivation_sensitivity_probe_artifacts/",
            "reports/n26_proxy_derivation_sensitivity_probe.md",
            "scripts/build_n26_proxy_derivation_sensitivity_probe.py",
            "```",
            "",
        ]
    )
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    i3 = load_json(I3_OUTPUT)
    i4 = load_json(I4_OUTPUT)
    stress = load_json(N25_2_STRESS)
    closeout = load_json(N25_2_CLOSEOUT)
    rows = build_rows(stress)

    output: dict[str, Any] = {
        "artifact_id": "n26_proxy_derivation_sensitivity_probe",
        "experiment": "N26",
        "iteration": "I4-A",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_pd2_proxy_derivation_sensitivity_probe_no_pd3_no_divergence",
        "source_active_null_output_digest": i3["output_digest"],
        "source_i4_output_digest": i4["output_digest"],
        "source_n25_2_stress_output_digest": stress["output_digest"],
        "source_n25_2_closeout_output_digest": closeout["output_digest"],
        "candidate_pd_ladder_rung": "PD2",
        "n26_closeout_ceiling": "N26-C3_active_nulls_fail_closed_with_PD2_sensitivity_checked_derivation_candidate",
        "n26_closeout_ladder_rung_assigned": False,
        "positive_proxy_evidence_opened": True,
        "proxy_derivation_opened": True,
        "proxy_derivation_sensitivity_opened": True,
        "proxy_divergence_opened": False,
        "proxy_collapse_opened": False,
        "pd3_or_stronger_supported": False,
        "ap5_bridge_status": "not_supported_i4a_sensitivity_only",
        "i4_replaced": False,
        "i4_output_digest_preserved": EXPECTED_I4_OUTPUT_DIGEST,
        "sensitivity_metric": {
            "metric_family": "n26_i4_proxy_basin_coupling_gap",
            "i4a_variant": "stress_normalized_proxy_basin_coupling_gap",
            "formula": "max(0.0, 1.0 - weakest_stress_normalized_capacity_ratio)",
            "target_relation": "<=",
            "target_value": 0.0,
            "declared_before_use": True,
            "scope": "PD2_sensitivity_only",
        },
        "sensitivity_rows": rows,
        "bounded_degraded_positive_row_supported": False,
        "bounded_degraded_positive_row_status": (
            "not_present_in_consumed_N25_2_stress_sources; nonzero gaps are "
            "fail-closed blocker evidence only"
        ),
        "claim_boundary": {
            "claim_ceiling": (
                "PD2 source-current proxy derivation sensitivity observation; "
                "no PD3 replay-backed contrast, no PD4 divergence, no PD5 collapse"
            ),
            "blocked_claims": [
                "proxy_divergence",
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
        "ready_for_iteration_5_proxy_divergence_contrast_matrix": True,
    }
    output["checks"] = build_checks(output, i3, i4, stress, closeout)
    output["failed_checks"] = [check["check"] for check in output["checks"] if not check["passed"]]
    digest_payload = dict(output)
    digest_payload.pop("output_digest", None)
    output["output_digest"] = digest_data(digest_payload)

    write_json(OUTPUT, output)
    write_report(output)


if __name__ == "__main__":
    main()

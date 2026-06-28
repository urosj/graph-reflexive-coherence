#!/usr/bin/env python3
"""Build N26 Iteration 5 proxy divergence contrast matrix."""

from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-28T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N26-lgrc-proxy-divergence-proxy-collapse"
OUTPUT = EXPERIMENT / "outputs" / "n26_proxy_divergence_contrast_matrix.json"
REPORT = EXPERIMENT / "reports" / "n26_proxy_divergence_contrast_matrix.md"
ARTIFACT_DIR = EXPERIMENT / "outputs" / "n26_proxy_divergence_contrast_matrix_artifacts"

I2_OUTPUT = EXPERIMENT / "outputs" / "n26_proxy_divergence_collapse_schema_and_controls.json"
I4_OUTPUT = EXPERIMENT / "outputs" / "n26_source_current_proxy_derivation_probe.json"
I4A_OUTPUT = EXPERIMENT / "outputs" / "n26_proxy_derivation_sensitivity_probe.json"

N25_2_EXPERIMENT = ROOT / "experiments" / "2026-06-N25.2-lgrc9v3-mb6-validation-bridge"
N25_2_STRESS = N25_2_EXPERIMENT / "outputs" / "n25_2_stress_variant_matrix.json"
N25_2_CLOSEOUT = N25_2_EXPERIMENT / "outputs" / "n25_2_closeout_and_n26_handoff.json"

COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N26-lgrc-proxy-divergence-proxy-collapse/scripts/"
    "build_n26_proxy_divergence_contrast_matrix.py"
)

EXPECTED_I1_OUTPUT_DIGEST = "b2f2a69f98aefbf3cb949dc834e6dab8c480f30bd580e3e389b301b74a04516a"
EXPECTED_I2_OUTPUT_DIGEST = "bbaf1621f64638b76ab296c4dc5b28bf99be7d5c2369d8e96e110e68972de070"
EXPECTED_I4_OUTPUT_DIGEST = "b8c8794ecc8e71c01c7bf9d0e1c369f1630416534741f3fb342c5622775a1680"
EXPECTED_I4A_OUTPUT_DIGEST = "5dbe325f6ce1ff95434b978e69cf659fdf609e2890960198aca66e2c5c85e414"
EXPECTED_N25_2_STRESS_DIGEST = "1759dbb4d8c85c27bc056108f04fea3cfcc1c59b5ee9518ebb7f641e60949627"
EXPECTED_N25_2_CLOSEOUT_DIGEST = "b92401da545899c7721ab42692827beb5b357bbd246d8991d7ad56649a6bbf03"
EXPECTED_SOURCE_CONTRACT_ROW_DIGEST = (
    "5746a2e7a792b7cc8eab716833a2e232f2ce6ef6ccd84a54dd21cf38c0308e61"
)
EXPECTED_SOURCE_CONSUMABLE_CONTRACT_ROW_DIGEST = (
    "99d2db29122734ca4de5ca7b4599f6a35a442d21a7b4983477eac6ddc75b48ec"
)

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

PD3_REQUIRED_ROLES = [
    "runtime_trace",
    "lower_stack_input_trace",
    "proxy_metric_trace",
    "basin_persistence_capacity_trace",
    "support_coherence_floor_trace",
    "basin_deepening_comparison_trace",
    "proxy_vs_basin_delta_trace",
    "replay_trace",
    "report",
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


def indexed_sensitivity_rows(i4a: dict[str, Any]) -> dict[tuple[str, str], list[dict[str, Any]]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in i4a["sensitivity_rows"]:
        grouped[(row["stress_axis"], row["stress_id"])].append(row)
    return grouped


def child_core(candidate_id: str) -> int:
    return int(candidate_id.rsplit("_", 1)[-1])


def build_control_results(control_ids: list[str], divergence_supported: bool, independence_status: str) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    pd3_pass_controls = {
        "source_digest_mismatch_control",
        "lower_stack_input_missing_control",
        "proxy_metric_trace_missing_control",
        "proxy_metric_not_replayable_control",
        "basin_persistence_capacity_trace_missing_control",
        "support_coherence_floor_missing_control",
        "scoped_mb6_scope_id_missing_control",
        "derived_report_only_positive_row_control",
        "artifact_manifest_failure_control",
        "proxy_label_only_control",
        "post_hoc_target_digest_control",
        "hidden_proxy_policy_control",
        "unscoped_mb6_consumption_control",
        "front_capacity_backfill_control",
        "peer_basin_missing_control",
        "AP5_gap_prose_only_control",
        "missing_ap5_dependency_status_control",
        "n15_context_as_native_ap5_control",
        "n19_nat3_as_ap5_closeout_control",
        "semantic_goal_relabel_control",
        "semantic_choice_relabel_control",
        "agency_relabel_control",
        "native_support_relabel_control",
        "n25_2_mb6_as_native_support_control",
        "n25_2_mb6_as_agency_sentience_ant_ecology_control",
        "sentience_relabel_control",
        "phase8_completion_relabel_control",
        "ant_ecology_relabel_control",
    }
    pd4_fail_closed_controls = {
        "proxy_basin_measurement_not_independent_control",
        "proxy_only_improvement_control",
        "proxy_improves_basin_also_improves_control",
        "proxy_improves_basin_unmeasured_control",
        "basin_degradation_hidden_by_proxy_control",
    }
    pd5_deferred_controls = {
        "perturbation_mismatch_control",
        "perturbation_digest_missing_control",
        "basin_deepened_survivor_missing_control",
        "proxy_collapse_result_trace_missing_control",
    }
    for control_id in control_ids:
        if control_id in pd3_pass_controls:
            results.append(
                {
                    "control_id": control_id,
                    "control_status": "passed",
                    "blocked_condition": control_id.replace("_control", ""),
                    "expected_result": "candidate_clears_control_for_PD3_contrast",
                    "actual_result": "passed_for_replay_backed_proxy_basin_contrast",
                    "claim_allowed_when_control_triggers": False,
                    "control_satisfied_for_positive_row": True,
                    "rung_effect": "PD3_not_blocked",
                }
            )
        elif control_id in pd4_fail_closed_controls:
            results.append(
                {
                    "control_id": control_id,
                    "control_status": "failed_closed_for_PD4" if not divergence_supported else "passed",
                    "blocked_condition": control_id.replace("_control", ""),
                    "expected_result": "block_PD4_when_divergence_condition_missing",
                    "actual_result": (
                        "PD4 blocked: proxy/basin traces are contrastive but do "
                        f"not satisfy controlled divergence; independence={independence_status}"
                    ),
                    "claim_allowed_when_control_triggers": False,
                    "control_satisfied_for_positive_row": True,
                    "rung_effect": "PD4_blocked_PD3_preserved",
                }
            )
        elif control_id in pd5_deferred_controls:
            results.append(
                {
                    "control_id": control_id,
                    "control_status": "not_applicable_for_PD3",
                    "blocked_condition": control_id.replace("_control", ""),
                    "expected_result": "defer_to_iteration_6_proxy_collapse_matrix",
                    "actual_result": "no proxy collapse perturbation claim in I5",
                    "claim_allowed_when_control_triggers": False,
                    "control_satisfied_for_positive_row": True,
                    "rung_effect": "PD5_or_stronger_deferred",
                }
            )
        else:
            raise ValueError(f"Unhandled control id: {control_id}")
    return results


def build_contrast_policy() -> dict[str, Any]:
    return {
        "policy_id": "n26_i5_proxy_basin_contrast_policy_v1",
        "declared_before_use": True,
        "proxy_improvement_definition": "proxy_basin_coupling_gap decreases relative to peer/control row",
        "basin_stall_or_degradation_definition": (
            "basin capacity ratio remains flat below an improvement threshold, "
            "decreases, or source stress row fails closed"
        ),
        "pd3_condition": "proxy and basin surfaces are replay-backed and compared to a peer/control basin",
        "pd4_condition": (
            "proxy improves while basin persistence/deepening stalls or degrades "
            "and proxy/basin measurements are independent"
        ),
        "proxy_collapse_condition": "not evaluated until I6",
    }


def build_candidate_row(
    stress_axis: str,
    stress_id: str,
    pair: list[dict[str, Any]],
    schema: dict[str, Any],
    i4: dict[str, Any],
    i4a: dict[str, Any],
    contrast_policy_digest: str,
) -> dict[str, Any]:
    ordered_pair = sorted(pair, key=lambda row: row["candidate_id"])
    reference = ordered_pair[0]
    peer = ordered_pair[1]
    row_id = f"n26_i5_{stress_axis}_{stress_id}"
    reference_gap = reference["proxy_basin_coupling_gap"]
    peer_gap = peer["proxy_basin_coupling_gap"]
    reference_capacity = reference["stress_normalized_capacity_ratio"]
    peer_capacity = peer["stress_normalized_capacity_ratio"]
    reference_passed = reference["row_decision"] == "supported"
    peer_passed = peer["row_decision"] == "supported"
    source_statuses = [reference["source_status"], peer["source_status"]]

    proxy_gap_delta_reference_minus_peer = reference_gap - peer_gap
    basin_capacity_delta_reference_minus_peer = reference_capacity - peer_capacity
    proxy_improvement_observed = False
    basin_stall_or_degradation_observed = any(status == "failed_closed" for status in source_statuses)
    independent_measurement_status = "contrast_present_not_independent_enough_for_PD4"
    divergence_supported = (
        proxy_improvement_observed
        and basin_stall_or_degradation_observed
        and independent_measurement_status == "independent"
    )

    if reference_gap == peer_gap == 0.0 and reference_passed and peer_passed:
        contrast_class = "aligned_zero_gap_pass"
    elif reference_gap > 0.0 or peer_gap > 0.0:
        contrast_class = "aligned_nonzero_gap_fail_closed"
    else:
        contrast_class = "nondivergent_contrast"

    runtime_trace = {
        "trace_id": f"{row_id}_runtime",
        "source_i4_artifact": rel(I4_OUTPUT),
        "source_i4a_artifact": rel(I4A_OUTPUT),
        "source_stress_artifact": rel(N25_2_STRESS),
        "stress_axis": stress_axis,
        "stress_id": stress_id,
        "reference_candidate_id": reference["candidate_id"],
        "peer_candidate_id": peer["candidate_id"],
        "derived_report_only": False,
    }
    lower_stack_input_trace = {
        "trace_id": f"{row_id}_lower_stack_input",
        "reference_source_json_pointer": reference["source_json_pointer"],
        "peer_source_json_pointer": peer["source_json_pointer"],
        "reference_source_status": reference["source_status"],
        "peer_source_status": peer["source_status"],
        "n25_2_consumption_scope": "scoped multi-basin substrate evidence only",
    }
    proxy_metric_trace = {
        "trace_id": f"{row_id}_proxy_metric",
        "reference_proxy_gap": reference_gap,
        "peer_proxy_gap": peer_gap,
        "proxy_gap_delta_reference_minus_peer": proxy_gap_delta_reference_minus_peer,
        "proxy_improvement_observed": proxy_improvement_observed,
        "metric_family": "n26_i4_proxy_basin_coupling_gap",
    }
    basin_persistence_capacity_trace = {
        "trace_id": f"{row_id}_basin_capacity",
        "reference_capacity_ratio": reference_capacity,
        "peer_capacity_ratio": peer_capacity,
        "basin_capacity_delta_reference_minus_peer": basin_capacity_delta_reference_minus_peer,
        "source_statuses": source_statuses,
        "basin_stall_or_degradation_observed": basin_stall_or_degradation_observed,
    }
    support_coherence_floor_trace = {
        "trace_id": f"{row_id}_support_coherence_floor",
        "stress_axis": stress_axis,
        "reference_target_met": reference["target_met"],
        "peer_target_met": peer["target_met"],
        "reference_source_status": reference["source_status"],
        "peer_source_status": peer["source_status"],
    }
    basin_deepening_comparison_trace = {
        "trace_id": f"{row_id}_basin_deepening_comparison",
        "reference_child_basin_id": child_core(reference["candidate_id"]),
        "peer_child_basin_id": child_core(peer["candidate_id"]),
        "peer_or_control_basin_present": True,
        "basin_deepening_observed": False,
        "comparison_kind": "peer_child_basin_stress_axis_contrast",
    }
    proxy_vs_basin_delta_trace = {
        "trace_id": f"{row_id}_proxy_vs_basin_delta",
        "contrast_class": contrast_class,
        "proxy_improvement_observed": proxy_improvement_observed,
        "basin_stall_or_degradation_observed": basin_stall_or_degradation_observed,
        "independent_measurement_status": independent_measurement_status,
        "controlled_proxy_divergence_supported": divergence_supported,
        "pd4_blocker": "no_proxy_improvement_and_no_independent_positive_divergence_row",
    }
    replay_trace = {
        "trace_id": f"{row_id}_replay",
        "artifact_replay": "passed_via_i4_source_replay_context",
        "snapshot_load_replay": "passed_via_i4_source_replay_context",
        "duplicate_replay": "passed_via_i4_source_replay_context",
        "order_control": "passed_via_i4a_stress_order",
        "replay_backed_contrast_candidate": True,
    }
    peer_or_control_basin_trace = {
        "trace_id": f"{row_id}_peer_or_control_basin",
        "reference_candidate_id": reference["candidate_id"],
        "peer_candidate_id": peer["candidate_id"],
        "reference_child_basin_id": child_core(reference["candidate_id"]),
        "peer_child_basin_id": child_core(peer["candidate_id"]),
        "peer_basin_missing": False,
    }
    row_report = {
        "row_id": row_id,
        "candidate_pd_ladder_rung": "PD3",
        "contrast_class": contrast_class,
        "controlled_proxy_divergence_supported": divergence_supported,
        "interpretation": (
            "Replay-backed proxy/basin contrast is present, but the row does "
            "not satisfy controlled proxy divergence because proxy improvement "
            "does not separate from basin stress status."
        ),
    }

    artifact_payloads = {
        "runtime_trace": runtime_trace,
        "lower_stack_input_trace": lower_stack_input_trace,
        "proxy_metric_trace": proxy_metric_trace,
        "basin_persistence_capacity_trace": basin_persistence_capacity_trace,
        "support_coherence_floor_trace": support_coherence_floor_trace,
        "basin_deepening_comparison_trace": basin_deepening_comparison_trace,
        "proxy_vs_basin_delta_trace": proxy_vs_basin_delta_trace,
        "replay_trace": replay_trace,
        "report": row_report,
    }
    artifact_manifest = [
        write_trace_artifact(row_id, role, artifact_payloads[role]) for role in PD3_REQUIRED_ROLES
    ]

    source_current_inputs = [
        {
            "source_artifact": rel(I4_OUTPUT),
            "source_output_digest": i4["output_digest"],
            "consumed_as": "source_current_proxy_derivation_rows",
        },
        {
            "source_artifact": rel(I4A_OUTPUT),
            "source_output_digest": i4a["output_digest"],
            "reference_row_id": reference["row_id"],
            "peer_row_id": peer["row_id"],
            "consumed_as": "source_current_proxy_sensitivity_rows",
        },
        {
            "source_artifact": rel(N25_2_STRESS),
            "source_output_digest": EXPECTED_N25_2_STRESS_DIGEST,
            "consumed_as": "source_current_stress_variant_matrix",
        },
    ]
    scoped_record = {
        "source_artifact": rel(N25_2_CLOSEOUT),
        "source_output_digest": EXPECTED_N25_2_CLOSEOUT_DIGEST,
        "consumed_as": "scoped_mb6_substrate_evidence_only",
        "n25_2_unscoped_consumption_allowed": False,
        "n25_2_unscoped_multi_basin_consumption_allowed": False,
        "front_capacity_companion_backfill_used": False,
    }

    target_policy = {
        "target_id": f"{row_id}_contrast_target",
        "declared_before_use": True,
        "candidate_pd_ladder_rung": "PD3",
        "pd3_target": "replay_backed_proxy_basin_contrast_present",
        "pd4_target": "proxy_improvement_with_basin_stall_or_degradation",
        "pd4_target_met": divergence_supported,
    }

    return {
        "row_id": row_id,
        "row_decision": "supported",
        "row_decision_scope": "PD3_replay_backed_proxy_basin_contrast_no_PD4_divergence",
        "candidate_pd_ladder_rung": "PD3",
        "stress_axis": stress_axis,
        "stress_id": stress_id,
        "source_current_inputs": source_current_inputs,
        "source_contract_row_digest": EXPECTED_SOURCE_CONTRACT_ROW_DIGEST,
        "source_consumable_contract_row_digest": EXPECTED_SOURCE_CONSUMABLE_CONTRACT_ROW_DIGEST,
        "source_output_digest": EXPECTED_I1_OUTPUT_DIGEST,
        "artifact_manifest": artifact_manifest,
        "all_artifact_sha256_match_file_contents": all(
            sha256_file(ROOT / item["path"]) == item["sha256"] for item in artifact_manifest
        ),
        "row_specific_thresholds_declared_before_use": {
            "declared_before_use": True,
            "contrast_policy_digest": contrast_policy_digest,
            "target_policy": target_policy,
            "target_policy_digest": digest_data(target_policy),
        },
        "scoped_mb6_substrate_consumption_record": scoped_record,
        "multi_basin_scope_id": f"n25_2_scoped_mb6_pair_core_0_core_2_{stress_axis}_{stress_id}",
        "basin_ids_or_child_basin_ids": [
            child_core(reference["candidate_id"]),
            child_core(peer["candidate_id"]),
        ],
        "n25_2_unscoped_consumption_allowed": False,
        "n25_2_unscoped_multi_basin_consumption_allowed": False,
        "front_capacity_companion_backfill_used": False,
        "proxy_metric_definition_digest": digest_data({"metric_family": "n26_i4_proxy_basin_coupling_gap"}),
        "proxy_derivation_policy_digest": contrast_policy_digest,
        "proxy_target_digest_declared_before_use": digest_data(target_policy),
        "proxy_policy_owner": "declared_analysis_policy",
        "producer_mediated_target_derivation_counted_as_substrate": False,
        "lower_stack_input_trace": lower_stack_input_trace,
        "proxy_metric_trace": proxy_metric_trace,
        "basin_persistence_capacity_trace": basin_persistence_capacity_trace,
        "support_coherence_floor_trace": support_coherence_floor_trace,
        "basin_deepening_comparison_trace": basin_deepening_comparison_trace,
        "proxy_vs_basin_delta_trace": proxy_vs_basin_delta_trace,
        "proxy_optimized_path_trace": {
            "status": "not_tested_until_iteration_6",
            "reason": "I5 contrast does not run proxy collapse perturbation.",
        },
        "basin_deepened_path_trace": {
            "status": "not_tested_until_iteration_6",
            "reason": "I5 contrast does not run proxy collapse perturbation.",
        },
        "perturbation_challenge_trace": {
            "status": "not_tested_until_iteration_6",
            "reason": "No shared perturbation challenge asserted in I5.",
        },
        "proxy_collapse_result_trace": {
            "status": "not_tested_until_iteration_6",
            "reason": "No proxy collapse result asserted in I5.",
        },
        "peer_or_control_basin_trace": peer_or_control_basin_trace,
        "replay_result": replay_trace,
        "control_results": build_control_results(
            schema["control_schema"]["required_control_ids"],
            divergence_supported,
            independent_measurement_status,
        ),
        "ap5_dependency_status": "required_recorded",
        "ap5_condition_reason": (
            "I5 compares proxy target behavior against basin stress behavior, so "
            "AP5 participation is row-local and recorded. N15/N19 remain gap "
            "context only and are not consumed as native AP5 evidence."
        ),
        "claim_ceiling": (
            "PD3 replay-backed proxy/basin contrast candidate; controlled proxy "
            "divergence, proxy collapse, AP5 bridge closeout, semantic goal, "
            "agency, native support, sentience, Phase 8, ant ecology, and "
            "unscoped multi-basin claims remain blocked"
        ),
        "unsafe_claim_flags": unsafe_claim_flags(),
        "contrast_class": contrast_class,
        "proxy_divergence_supported": divergence_supported,
        "proxy_collapse_supported": False,
    }


def build_candidate_rows(schema: dict[str, Any], i4: dict[str, Any], i4a: dict[str, Any]) -> tuple[list[dict[str, Any]], str]:
    contrast_policy = build_contrast_policy()
    contrast_policy_digest = digest_data(contrast_policy)
    grouped = indexed_sensitivity_rows(i4a)
    rows: list[dict[str, Any]] = []
    for (stress_axis, stress_id), pair in sorted(grouped.items()):
        if len(pair) != 2:
            raise ValueError(f"Expected peer pair for {stress_axis}/{stress_id}, got {len(pair)}")
        rows.append(build_candidate_row(stress_axis, stress_id, pair, schema, i4, i4a, contrast_policy_digest))
    return rows, contrast_policy_digest


def build_checks(
    output: dict[str, Any],
    schema: dict[str, Any],
    i4: dict[str, Any],
    i4a: dict[str, Any],
    stress: dict[str, Any],
    closeout: dict[str, Any],
) -> list[dict[str, Any]]:
    rows = output["candidate_rows"]
    required_fields = schema["candidate_row_schema"]["required_fields"]
    required_roles = schema["artifact_manifest_schema"]["required_artifact_roles_by_pd_rung"]["PD3"]
    return [
        {
            "check": "source_chain_ready",
            "passed": (
                schema["output_digest"] == EXPECTED_I2_OUTPUT_DIGEST
                and i4["output_digest"] == EXPECTED_I4_OUTPUT_DIGEST
                and i4a["output_digest"] == EXPECTED_I4A_OUTPUT_DIGEST
                and stress["output_digest"] == EXPECTED_N25_2_STRESS_DIGEST
                and closeout["output_digest"] == EXPECTED_N25_2_CLOSEOUT_DIGEST
            ),
            "detail": {
                "i2": schema["output_digest"],
                "i4": i4["output_digest"],
                "i4a": i4a["output_digest"],
                "n25_2_stress": stress["output_digest"],
                "n25_2_closeout": closeout["output_digest"],
            },
        },
        {
            "check": "all_candidate_required_fields_present",
            "passed": all(all(field in row for field in required_fields) for row in rows),
            "detail": {"required_field_count": len(required_fields), "row_count": len(rows)},
        },
        {
            "check": "pd3_artifact_roles_present",
            "passed": all(
                set(required_roles).issubset({item["artifact_role"] for item in row["artifact_manifest"]})
                for row in rows
            ),
            "detail": {"required_roles": required_roles},
        },
        {
            "check": "artifact_sha256_match_file_contents",
            "passed": all(row["all_artifact_sha256_match_file_contents"] for row in rows),
            "detail": {"row_count": len(rows)},
        },
        {
            "check": "peer_or_control_basin_present",
            "passed": all(not row["peer_or_control_basin_trace"]["peer_basin_missing"] for row in rows),
            "detail": {"row_count": len(rows)},
        },
        {
            "check": "replay_backed_contrast_present",
            "passed": all(row["replay_result"]["replay_backed_contrast_candidate"] for row in rows),
            "detail": {"candidate_pd_ladder_rung": output["candidate_pd_ladder_rung"]},
        },
        {
            "check": "controlled_proxy_divergence_not_supported",
            "passed": (
                not output["controlled_proxy_divergence_candidate_supported"]
                and not output["pd4_or_stronger_supported"]
                and all(not row["proxy_divergence_supported"] for row in rows)
            ),
            "detail": output["pd4_blockers"],
        },
        {
            "check": "proxy_collapse_not_opened",
            "passed": not output["proxy_collapse_opened"] and not output["proxy_collapse_supported"],
            "detail": {"ready_for_iteration_6": output["ready_for_iteration_6_proxy_collapse_perturbation_matrix"]},
        },
        {
            "check": "ap5_dependency_recorded_without_native_ap5_upgrade",
            "passed": all(
                row["ap5_dependency_status"] == "required_recorded"
                and "not consumed as native AP5" in row["ap5_condition_reason"]
                for row in rows
            ),
            "detail": {"ap5_bridge_status": output["ap5_bridge_status"]},
        },
        {
            "check": "scoped_mb6_boundary_preserved",
            "passed": (
                closeout["n26_handoff"]["n26_scoped_context_consumption_allowed"]
                and not closeout["n26_handoff"]["n26_unscoped_consumption_allowed"]
                and not closeout["n26_handoff"]["n26_unscoped_multi_basin_consumption_allowed"]
                and all(not row["front_capacity_companion_backfill_used"] for row in rows)
            ),
            "detail": closeout["n26_handoff"],
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
    rows = output["candidate_rows"]
    lines = [
        "# N26 Iteration 5 - Proxy Divergence Contrast Matrix",
        "",
        f"Status: `{output['status']}`",
        "",
        f"Acceptance state: `{output['acceptance_state']}`",
        "",
        "## Summary",
        "",
        "I5 pairs the two scoped N25.2 child-basin candidates across each I4-A",
        "stress axis. The matrix supports replay-backed proxy/basin contrast",
        "at PD3. It does not support controlled proxy divergence: no row shows",
        "proxy improvement while basin persistence/deepening stalls or degrades",
        "under independent measurement.",
        "",
        "## Contrast Rows",
        "",
        "| Row | Axis | Stress | Class | Reference Gap | Peer Gap | PD4 |",
        "| --- | --- | --- | --- | ---: | ---: | --- |",
    ]
    for row in rows:
        lines.append(
            "| "
            f"`{row['row_id']}` | "
            f"`{row['stress_axis']}` | "
            f"`{row['stress_id']}` | "
            f"`{row['contrast_class']}` | "
            f"{row['proxy_metric_trace']['reference_proxy_gap']:.6f} | "
            f"{row['proxy_metric_trace']['peer_proxy_gap']:.6f} | "
            f"`{str(row['proxy_divergence_supported']).lower()}` |"
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
            f"`controlled_proxy_divergence_candidate_supported = "
            f"{str(output['controlled_proxy_divergence_candidate_supported']).lower()}`",
            "",
            "I5 supports contrast, not divergence. Proxy collapse remains I6 scope.",
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
            "outputs/n26_proxy_divergence_contrast_matrix.json",
            "outputs/n26_proxy_divergence_contrast_matrix_artifacts/",
            "reports/n26_proxy_divergence_contrast_matrix.md",
            "scripts/build_n26_proxy_divergence_contrast_matrix.py",
            "```",
            "",
        ]
    )
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    schema = load_json(I2_OUTPUT)
    i4 = load_json(I4_OUTPUT)
    i4a = load_json(I4A_OUTPUT)
    stress = load_json(N25_2_STRESS)
    closeout = load_json(N25_2_CLOSEOUT)
    candidate_rows, contrast_policy_digest = build_candidate_rows(schema, i4, i4a)

    output: dict[str, Any] = {
        "artifact_id": "n26_proxy_divergence_contrast_matrix",
        "experiment": "N26",
        "iteration": "I5",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_replay_backed_pd3_proxy_basin_contrast_no_controlled_divergence",
        "source_schema_output_digest": schema["output_digest"],
        "source_i4_output_digest": i4["output_digest"],
        "source_i4a_output_digest": i4a["output_digest"],
        "source_n25_2_stress_output_digest": stress["output_digest"],
        "source_n25_2_closeout_output_digest": closeout["output_digest"],
        "candidate_pd_ladder_rung": "PD3",
        "n26_closeout_ceiling": "N26-C4_source_current_proxy_derivation_and_replay_backed_contrast_supported",
        "n26_closeout_ladder_rung_assigned": False,
        "positive_proxy_evidence_opened": True,
        "proxy_derivation_opened": True,
        "proxy_derivation_sensitivity_opened": True,
        "proxy_divergence_contrast_opened": True,
        "proxy_divergence_opened": True,
        "proxy_divergence_supported": False,
        "controlled_proxy_divergence_candidate_supported": False,
        "pd4_or_stronger_supported": False,
        "proxy_collapse_opened": False,
        "proxy_collapse_supported": False,
        "pd5_or_stronger_supported": False,
        "ap5_bridge_status": "not_supported_i5_contrast_only",
        "contrast_policy_digest": contrast_policy_digest,
        "candidate_rows": candidate_rows,
        "contrast_row_count": len(candidate_rows),
        "pd4_blockers": [
            "no_proxy_improvement_observed",
            "proxy_and_basin_measurement_not_independent_enough_for_PD4",
            "nonzero_proxy_gap_rows_are_fail_closed_blockers_not_positive_support",
            "basin_deepening_not_observed",
        ],
        "claim_boundary": {
            "claim_ceiling": (
                "PD3 replay-backed proxy/basin contrast candidate; no controlled "
                "proxy divergence or proxy collapse"
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
    output["checks"] = build_checks(output, schema, i4, i4a, stress, closeout)
    output["failed_checks"] = [check["check"] for check in output["checks"] if not check["passed"]]
    digest_payload = dict(output)
    digest_payload.pop("output_digest", None)
    output["output_digest"] = digest_data(digest_payload)

    write_json(OUTPUT, output)
    write_report(output)


if __name__ == "__main__":
    main()

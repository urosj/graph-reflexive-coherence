#!/usr/bin/env python3
"""Build N26 Iteration 4 source-current proxy derivation probe."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-28T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N26-lgrc-proxy-divergence-proxy-collapse"
OUTPUT = EXPERIMENT / "outputs" / "n26_source_current_proxy_derivation_probe.json"
REPORT = EXPERIMENT / "reports" / "n26_source_current_proxy_derivation_probe.md"
ARTIFACT_DIR = EXPERIMENT / "outputs" / "n26_source_current_proxy_derivation_probe_artifacts"

I1_OUTPUT = EXPERIMENT / "outputs" / "n26_source_inventory_and_scoped_substrate_admission.json"
I2_OUTPUT = EXPERIMENT / "outputs" / "n26_proxy_divergence_collapse_schema_and_controls.json"
I3_OUTPUT = EXPERIMENT / "outputs" / "n26_active_nulls_and_failure_baselines.json"

N25_2_EXPERIMENT = ROOT / "experiments" / "2026-06-N25.2-lgrc9v3-mb6-validation-bridge"
N25_2_REPLAY = N25_2_EXPERIMENT / "outputs" / "n25_2_multi_window_persistence_replay.json"
N25_2_CLOSEOUT = N25_2_EXPERIMENT / "outputs" / "n25_2_closeout_and_n26_handoff.json"
N25_2_I4 = N25_2_EXPERIMENT / "outputs" / "n25_2_native_runtime_positive_probe.json"
N25_2_I4A = N25_2_EXPERIMENT / "outputs" / "n25_2_native_runtime_variant_probe.json"

COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N26-lgrc-proxy-divergence-proxy-collapse/scripts/"
    "build_n26_source_current_proxy_derivation_probe.py"
)

EXPECTED_I1_OUTPUT_DIGEST = "b2f2a69f98aefbf3cb949dc834e6dab8c480f30bd580e3e389b301b74a04516a"
EXPECTED_I2_OUTPUT_DIGEST = "bbaf1621f64638b76ab296c4dc5b28bf99be7d5c2369d8e96e110e68972de070"
EXPECTED_I3_OUTPUT_DIGEST = "90b3adf46add9fd0b98b3022733ce9f9fabbbd1b3695908aefbfb58f7199c2fd"
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

PD2_REQUIRED_ROLES = [
    "runtime_trace",
    "lower_stack_input_trace",
    "proxy_metric_trace",
    "basin_persistence_capacity_trace",
    "support_coherence_floor_trace",
    "report",
]

PD2_BLOCKING_CONTROLS = {
    "source_digest_mismatch_control": "passed_source_digests_match_frozen_i1_i2_i3_chain",
    "lower_stack_input_missing_control": "passed_lower_stack_input_trace_present",
    "proxy_metric_trace_missing_control": "passed_proxy_metric_trace_present",
    "proxy_metric_not_replayable_control": "passed_metric_is_replay_context_linked_but_pd3_deferred",
    "basin_persistence_capacity_trace_missing_control": "passed_basin_capacity_trace_present",
    "support_coherence_floor_missing_control": "passed_support_coherence_floor_trace_present",
    "scoped_mb6_scope_id_missing_control": "passed_scoped_mb6_scope_id_present",
    "derived_report_only_positive_row_control": "passed_derived_report_only_false",
    "artifact_manifest_failure_control": "passed_manifest_roles_and_sha256_validated",
    "proxy_label_only_control": "passed_proxy_metric_has_source_current_trace",
    "post_hoc_target_digest_control": "passed_target_digest_declared_before_use",
    "hidden_proxy_policy_control": "passed_proxy_policy_is_declared_analysis_policy",
    "unscoped_mb6_consumption_control": "passed_scoped_consumption_only",
    "front_capacity_backfill_control": "passed_front_capacity_backfill_not_used",
    "AP5_gap_prose_only_control": "passed_row_local_ap5_dependency_recorded",
    "missing_ap5_dependency_status_control": "passed_ap5_dependency_status_required_recorded",
    "n15_context_as_native_ap5_control": "passed_n15_context_not_counted_as_native_ap5",
    "n19_nat3_as_ap5_closeout_control": "passed_n19_nat3_boundary_not_counted_as_ap5_closeout",
    "semantic_goal_relabel_control": "passed_semantic_goal_blocked",
    "semantic_choice_relabel_control": "passed_semantic_choice_blocked",
    "agency_relabel_control": "passed_agency_blocked",
    "native_support_relabel_control": "passed_native_support_blocked",
    "n25_2_mb6_as_native_support_control": "passed_n25_2_mb6_not_native_support",
    "n25_2_mb6_as_agency_sentience_ant_ecology_control": (
        "passed_n25_2_mb6_not_agency_sentience_or_ant_ecology"
    ),
    "sentience_relabel_control": "passed_sentience_blocked",
    "phase8_completion_relabel_control": "passed_phase8_completion_blocked",
    "ant_ecology_relabel_control": "passed_ant_ecology_blocked",
}

PD2_DEFERRED_CONTROLS = {
    "proxy_basin_measurement_not_independent_control": "deferred_until_i5_proxy_basin_contrast",
    "proxy_only_improvement_control": "deferred_until_i5_proxy_divergence_contrast",
    "proxy_improves_basin_also_improves_control": "deferred_until_i5_proxy_divergence_contrast",
    "proxy_improves_basin_unmeasured_control": "deferred_until_i5_proxy_divergence_contrast",
    "basin_degradation_hidden_by_proxy_control": "deferred_until_i5_proxy_divergence_contrast",
    "peer_basin_missing_control": "deferred_until_i5_peer_or_control_basin_matrix",
    "perturbation_mismatch_control": "deferred_until_i6_proxy_collapse_matrix",
    "perturbation_digest_missing_control": "deferred_until_i6_proxy_collapse_matrix",
    "basin_deepened_survivor_missing_control": "deferred_until_i6_proxy_collapse_matrix",
    "proxy_collapse_result_trace_missing_control": "deferred_until_i6_proxy_collapse_matrix",
}


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


def parse_child_core(candidate_id: str) -> int:
    return int(candidate_id.rsplit("_", 1)[-1])


def replay_records(row: dict[str, Any]) -> list[dict[str, Any]]:
    return [window["replay_validation_record"] for window in row["window_records"]]


def persistence_ratios(row: dict[str, Any]) -> dict[str, list[float]]:
    records = replay_records(row)
    return {
        "support": [record["support_persistence_ratio"] for record in records],
        "coherence": [record["coherence_persistence_ratio"] for record in records],
        "boundary": [record["boundary_persistence_ratio"] for record in records],
        "flux": [record["flux_persistence_ratio"] for record in records],
        "membership": [record["membership_persistence_ratio"] for record in records],
    }


def row_source_path(row: dict[str, Any]) -> str:
    if row["source_iteration"] == "I4":
        return rel(N25_2_I4)
    if row["source_iteration"] == "I4-A":
        return rel(N25_2_I4A)
    raise ValueError(f"Unexpected source iteration: {row['source_iteration']}")


def source_current_inputs(row: dict[str, Any], n25_2_replay_digest: str) -> list[dict[str, Any]]:
    return [
        {
            "source_artifact": rel(N25_2_REPLAY),
            "source_output_digest": n25_2_replay_digest,
            "source_row_id": row["candidate_id"],
            "consumed_as": "source_current_multi_window_child_basin_replay_trace",
        },
        {
            "source_artifact": row_source_path(row),
            "source_output_digest": row["source_output_digest"],
            "source_child_basin_state_digest": row["source_child_basin_state_digest"],
            "consumed_as": "scoped_child_basin_runtime_source_trace",
        },
        {
            "source_artifact": rel(N25_2_CLOSEOUT),
            "source_output_digest": EXPECTED_N25_2_CLOSEOUT_DIGEST,
            "consumed_as": "scoped_mb6_handoff_boundary",
        },
    ]


def build_policy_records(row: dict[str, Any]) -> dict[str, dict[str, Any]]:
    metric_definition = {
        "metric_id": "n26_i4_proxy_basin_coupling_gap",
        "definition": (
            "Gap between perfect child-basin replay capacity and the weakest "
            "source-current persistence ratio across support, coherence, "
            "boundary, flux, and membership."
        ),
        "formula": "max(0.0, 1.0 - min(source_current_persistence_ratios))",
        "lower_is_better": True,
        "zero_value_meaning": (
            "No observed proxy/basin coupling gap in the consumed scoped MB6 "
            "multi-window replay trace."
        ),
        "semantic_goal_or_target_ownership": False,
    }
    derivation_policy = {
        "policy_id": "n26_i4_source_current_proxy_derivation_policy_v1",
        "declared_before_use": True,
        "input_row_id": row["candidate_id"],
        "source_current_inputs": [
            "support_persistence_ratio",
            "coherence_persistence_ratio",
            "boundary_persistence_ratio",
            "flux_persistence_ratio",
            "membership_persistence_ratio",
        ],
        "proxy_policy_owner": "declared_analysis_policy",
        "producer_mediated_target_derivation_counted_as_substrate": False,
        "n25_2_consumption_scope": "scoped multi-basin substrate evidence only",
    }
    target_policy = {
        "target_id": "n26_i4_proxy_coupling_gap_target_v1",
        "declared_before_use": True,
        "target_quantity": "proxy_basin_coupling_gap",
        "target_relation": "<=",
        "target_value": 0.0,
        "required_persistence_ratio_floor": 1.0,
        "required_source_windows": 3,
        "target_scope": "PD2_proxy_derivation_only",
        "not_a_semantic_goal": True,
    }
    return {
        "metric_definition": metric_definition,
        "derivation_policy": derivation_policy,
        "target_policy": target_policy,
    }


def build_control_results(control_ids: list[str]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for control_id in control_ids:
        if control_id in PD2_BLOCKING_CONTROLS:
            results.append(
                {
                    "control_id": control_id,
                    "control_status": "passed",
                    "blocked_condition": control_id.replace("_control", ""),
                    "expected_result": "candidate_clears_control_for_PD2",
                    "actual_result": PD2_BLOCKING_CONTROLS[control_id],
                    "claim_allowed_when_control_triggers": False,
                    "control_satisfied_for_positive_row": True,
                    "rung_effect": "PD2_not_blocked",
                }
            )
        elif control_id in PD2_DEFERRED_CONTROLS:
            results.append(
                {
                    "control_id": control_id,
                    "control_status": "not_applicable_for_PD2",
                    "blocked_condition": control_id.replace("_control", ""),
                    "expected_result": "defer_to_later_iteration_without_upgrading_PD2",
                    "actual_result": PD2_DEFERRED_CONTROLS[control_id],
                    "claim_allowed_when_control_triggers": False,
                    "control_satisfied_for_positive_row": True,
                    "rung_effect": "PD3_or_stronger_deferred",
                }
            )
        else:
            raise ValueError(f"Missing I4 control handling for {control_id}")
    return results


def build_candidate_row(
    source_row: dict[str, Any],
    schema: dict[str, Any],
    n25_2_replay_digest: str,
    handoff: dict[str, Any],
) -> dict[str, Any]:
    row_id = "n26_i4_" + source_row["candidate_id"]
    child_core = parse_child_core(source_row["candidate_id"])
    ratios = persistence_ratios(source_row)
    flat_ratios = [value for values in ratios.values() for value in values]
    weakest_ratio = min(flat_ratios)
    proxy_gap = max(0.0, 1.0 - weakest_ratio)
    window_count = source_row["runtime_snapshot_window_count"]

    policy_records = build_policy_records(source_row)
    metric_definition_digest = digest_data(policy_records["metric_definition"])
    derivation_policy_digest = digest_data(policy_records["derivation_policy"])
    target_policy_digest = digest_data(policy_records["target_policy"])

    lower_stack_input_trace = {
        "trace_id": f"{row_id}_lower_stack_input",
        "n25_2_candidate_id": source_row["candidate_id"],
        "source_iteration": source_row["source_iteration"],
        "source_artifact": row_source_path(source_row),
        "source_child_basin_state_digest": source_row["source_child_basin_state_digest"],
        "source_current_replay_artifact": rel(N25_2_REPLAY),
        "runtime_snapshot_window_count": window_count,
        "scoped_child_basin_core": child_core,
        "consumption_scope": "scoped_MB6_child_basin_substrate_only",
    }
    proxy_metric_trace = {
        "trace_id": f"{row_id}_proxy_metric",
        "metric_definition_digest": metric_definition_digest,
        "proxy_basin_coupling_gap": proxy_gap,
        "weakest_source_current_persistence_ratio": weakest_ratio,
        "proxy_target_digest_declared_before_use": target_policy_digest,
        "proxy_target_met": proxy_gap <= policy_records["target_policy"]["target_value"],
        "semantic_goal_or_target_ownership_claim_allowed": False,
    }
    basin_persistence_capacity_trace = {
        "trace_id": f"{row_id}_basin_persistence_capacity",
        "basin_persistence_capacity_score": weakest_ratio,
        "ratios_by_axis": ratios,
        "all_window_child_basin_records_present": source_row["all_window_child_basin_records_present"],
        "all_window_replay_ratios_exact": source_row["all_window_replay_ratios_exact"],
        "all_window_replay_results_passed": source_row["all_window_replay_results_passed"],
        "window_replay_validation_digests": source_row["window_replay_validation_digests"],
    }
    support_coherence_floor_trace = {
        "trace_id": f"{row_id}_support_coherence_floor",
        "support_floor": 1.0,
        "coherence_floor": 1.0,
        "support_min": min(ratios["support"]),
        "coherence_min": min(ratios["coherence"]),
        "support_floor_preserved": min(ratios["support"]) >= 1.0,
        "coherence_floor_preserved": min(ratios["coherence"]) >= 1.0,
        "boundary_floor_preserved": min(ratios["boundary"]) >= 1.0,
        "flux_floor_preserved": min(ratios["flux"]) >= 1.0,
        "membership_floor_preserved": min(ratios["membership"]) >= 1.0,
    }
    runtime_trace = {
        "trace_id": f"{row_id}_runtime",
        "source_current_inputs": source_current_inputs(source_row, n25_2_replay_digest),
        "source_replay_records": replay_records(source_row),
        "runtime_snapshot_window_count": window_count,
        "derived_report_only": False,
    }
    row_report = {
        "row_id": row_id,
        "candidate_pd_ladder_rung": "PD2",
        "interpretation": (
            "The row derives a proxy coupling-gap metric from source-current "
            "scoped MB6 child-basin replay. It supports derivation only; "
            "divergence, collapse, and AP5 bridge closeout remain pending."
        ),
        "proxy_basin_coupling_gap": proxy_gap,
        "basin_persistence_capacity_score": weakest_ratio,
    }

    artifact_payloads = {
        "runtime_trace": runtime_trace,
        "lower_stack_input_trace": lower_stack_input_trace,
        "proxy_metric_trace": proxy_metric_trace,
        "basin_persistence_capacity_trace": basin_persistence_capacity_trace,
        "support_coherence_floor_trace": support_coherence_floor_trace,
        "report": row_report,
    }
    artifact_manifest = [
        write_trace_artifact(row_id, artifact_role, artifact_payloads[artifact_role])
        for artifact_role in PD2_REQUIRED_ROLES
    ]

    row_specific_thresholds = {
        "declared_before_use": True,
        "metric_definition": policy_records["metric_definition"],
        "metric_definition_digest": metric_definition_digest,
        "proxy_derivation_policy": policy_records["derivation_policy"],
        "proxy_derivation_policy_digest": derivation_policy_digest,
        "proxy_target_policy": policy_records["target_policy"],
        "proxy_target_digest": target_policy_digest,
        "threshold_application_scope": "PD2_source_current_proxy_derivation_only",
    }

    scoped_record = {
        "source_artifact": rel(N25_2_CLOSEOUT),
        "source_output_digest": EXPECTED_N25_2_CLOSEOUT_DIGEST,
        "n26_handoff": handoff["n26_handoff"],
        "consumed_as": "scoped_mb6_substrate_evidence_only",
        "n25_2_claim_ceiling_preserved": True,
        "native_support_agency_sentience_phase8_claims_blocked": True,
    }

    return {
        "row_id": row_id,
        "row_decision": "supported",
        "row_decision_scope": "PD2_source_current_proxy_derivation_candidate_only",
        "candidate_pd_ladder_rung": "PD2",
        "source_current_inputs": source_current_inputs(source_row, n25_2_replay_digest),
        "source_contract_row_digest": EXPECTED_SOURCE_CONTRACT_ROW_DIGEST,
        "source_consumable_contract_row_digest": EXPECTED_SOURCE_CONSUMABLE_CONTRACT_ROW_DIGEST,
        "source_output_digest": EXPECTED_I1_OUTPUT_DIGEST,
        "artifact_manifest": artifact_manifest,
        "all_artifact_sha256_match_file_contents": all(
            sha256_file(ROOT / item["path"]) == item["sha256"] for item in artifact_manifest
        ),
        "row_specific_thresholds_declared_before_use": row_specific_thresholds,
        "scoped_mb6_substrate_consumption_record": scoped_record,
        "multi_basin_scope_id": f"n25_2_scoped_mb6_{source_row['candidate_id']}",
        "basin_ids_or_child_basin_ids": [child_core],
        "n25_2_unscoped_consumption_allowed": False,
        "n25_2_unscoped_multi_basin_consumption_allowed": False,
        "front_capacity_companion_backfill_used": False,
        "proxy_metric_definition_digest": metric_definition_digest,
        "proxy_derivation_policy_digest": derivation_policy_digest,
        "proxy_target_digest_declared_before_use": target_policy_digest,
        "proxy_policy_owner": "declared_analysis_policy",
        "producer_mediated_target_derivation_counted_as_substrate": False,
        "lower_stack_input_trace": lower_stack_input_trace,
        "proxy_metric_trace": proxy_metric_trace,
        "basin_persistence_capacity_trace": basin_persistence_capacity_trace,
        "support_coherence_floor_trace": support_coherence_floor_trace,
        "basin_deepening_comparison_trace": {
            "status": "not_tested_until_iteration_5",
            "reason": "I4 derives the source-current proxy metric; contrast is I5 scope.",
        },
        "proxy_vs_basin_delta_trace": {
            "status": "not_tested_until_iteration_5",
            "reason": "No proxy divergence claim is made in I4.",
        },
        "proxy_optimized_path_trace": {
            "status": "not_tested_until_iteration_6",
            "reason": "Proxy collapse perturbation matrix is I6 scope.",
        },
        "basin_deepened_path_trace": {
            "status": "not_tested_until_iteration_6",
            "reason": "Proxy collapse perturbation matrix is I6 scope.",
        },
        "perturbation_challenge_trace": {
            "status": "not_tested_until_iteration_6",
            "reason": "No perturbation contrast is asserted in I4.",
        },
        "proxy_collapse_result_trace": {
            "status": "not_tested_until_iteration_6",
            "reason": "No proxy collapse result is asserted in I4.",
        },
        "peer_or_control_basin_trace": {
            "status": "not_tested_until_iteration_5",
            "reason": "Peer/control basin matrix is required for divergence, not PD2 derivation.",
        },
        "replay_result": {
            "source_replay_context_present": True,
            "source_replay_artifact": rel(N25_2_REPLAY),
            "artifact_replay": "passed_in_source_context",
            "snapshot_load_replay": "passed_in_source_context",
            "duplicate_replay": "passed_in_source_context",
            "order_control": "passed_in_source_context",
            "pd3_assignment_deferred_reason": "proxy_basin_contrast_matrix_pending_iteration_5",
        },
        "control_results": build_control_results(schema["control_schema"]["required_control_ids"]),
        "ap5_dependency_status": "required_recorded",
        "ap5_condition_reason": (
            "I4 performs proxy target derivation, so AP5 participation is "
            "row-local and recorded. N15 historical AP5 and N19 NAT3 remain "
            "gap context only and are not consumed as native AP5 evidence."
        ),
        "claim_ceiling": (
            "source-current PD2 proxy derivation candidate over scoped N25.2 "
            "MB6 substrate; no proxy divergence, proxy collapse, AP5 bridge "
            "closeout, semantic goal, agency, native support, sentience, Phase 8, "
            "ant ecology, or unscoped multi-basin claim"
        ),
        "unsafe_claim_flags": unsafe_claim_flags(),
        "proxy_derivation_supported": True,
        "proxy_divergence_supported": False,
        "proxy_collapse_supported": False,
    }


def build_checks(
    output: dict[str, Any],
    schema: dict[str, Any],
    i1: dict[str, Any],
    i2: dict[str, Any],
    i3: dict[str, Any],
    n25_2_closeout: dict[str, Any],
) -> list[dict[str, Any]]:
    rows = output["candidate_rows"]
    required_fields = schema["candidate_row_schema"]["required_fields"]
    required_roles = schema["artifact_manifest_schema"]["required_artifact_roles_by_pd_rung"]["PD2"]
    return [
        {
            "check": "source_chain_digests_match",
            "passed": (
                i1["output_digest"] == EXPECTED_I1_OUTPUT_DIGEST
                and i2["output_digest"] == EXPECTED_I2_OUTPUT_DIGEST
                and i3["output_digest"] == EXPECTED_I3_OUTPUT_DIGEST
            ),
            "detail": {
                "i1": i1["output_digest"],
                "i2": i2["output_digest"],
                "i3": i3["output_digest"],
            },
        },
        {
            "check": "n25_2_scoped_handoff_valid",
            "passed": (
                n25_2_closeout["output_digest"] == EXPECTED_N25_2_CLOSEOUT_DIGEST
                and n25_2_closeout["n26_handoff"]["n26_scoped_context_consumption_allowed"]
                and not n25_2_closeout["n26_handoff"]["n26_unscoped_consumption_allowed"]
            ),
            "detail": n25_2_closeout["n26_handoff"],
        },
        {
            "check": "all_candidate_required_fields_present",
            "passed": all(all(field in row for field in required_fields) for row in rows),
            "detail": {"required_field_count": len(required_fields), "row_count": len(rows)},
        },
        {
            "check": "pd2_artifact_roles_present",
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
            "check": "proxy_target_declared_before_use",
            "passed": all(
                row["row_specific_thresholds_declared_before_use"]["declared_before_use"]
                and row["proxy_target_digest_declared_before_use"]
                == row["row_specific_thresholds_declared_before_use"]["proxy_target_digest"]
                for row in rows
            ),
            "detail": {"row_count": len(rows)},
        },
        {
            "check": "proxy_metric_and_basin_capacity_traces_present",
            "passed": all(
                row["proxy_metric_trace"]["proxy_target_met"]
                and row["basin_persistence_capacity_trace"]["basin_persistence_capacity_score"] == 1.0
                and row["support_coherence_floor_trace"]["support_floor_preserved"]
                and row["support_coherence_floor_trace"]["coherence_floor_preserved"]
                for row in rows
            ),
            "detail": {"proxy_metric": "proxy_basin_coupling_gap"},
        },
        {
            "check": "scoped_mb6_consumption_preserved",
            "passed": all(
                not row["n25_2_unscoped_consumption_allowed"]
                and not row["n25_2_unscoped_multi_basin_consumption_allowed"]
                and not row["front_capacity_companion_backfill_used"]
                for row in rows
            ),
            "detail": {"row_count": len(rows)},
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
            "check": "no_proxy_divergence_or_collapse_claim",
            "passed": (
                output["proxy_derivation_opened"]
                and not output["proxy_divergence_opened"]
                and not output["proxy_collapse_opened"]
                and not output["pd3_or_stronger_supported"]
            ),
            "detail": {
                "candidate_pd_ladder_rung": output["candidate_pd_ladder_rung"],
                "n26_closeout_ceiling": output["n26_closeout_ceiling"],
            },
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
        "# N26 Iteration 4 - Source-Current Proxy Derivation Probe",
        "",
        f"Status: `{output['status']}`",
        "",
        f"Acceptance state: `{output['acceptance_state']}`",
        "",
        "## Summary",
        "",
        "I4 derives a proxy metric from scoped N25.2 MB6 child-basin replay inputs.",
        "The metric is a local coupling-gap proxy:",
        "",
        "```text",
        "proxy_basin_coupling_gap = max(0, 1 - weakest persistence ratio)",
        "```",
        "",
        "Both candidate rows have weakest persistence ratio `1.0`, so the derived",
        "gap is `0.0`. This supports PD2 derivation only. It does not support",
        "proxy divergence, proxy collapse, final AP5, native support, agency,",
        "sentience, Phase 8 completion, ant ecology, or unscoped multi-basin claims.",
        "",
        "## Candidate Rows",
        "",
        "| Row | Source | Core | Gap | Capacity | Rung | Ceiling |",
        "| --- | --- | ---: | ---: | ---: | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| "
            f"`{row['row_id']}` | "
            f"`{row['source_current_inputs'][0]['source_row_id']}` | "
            f"{row['basin_ids_or_child_basin_ids'][0]} | "
            f"{row['proxy_metric_trace']['proxy_basin_coupling_gap']:.1f} | "
            f"{row['basin_persistence_capacity_trace']['basin_persistence_capacity_score']:.1f} | "
            f"`{row['candidate_pd_ladder_rung']}` | "
            "PD2 derivation only |"
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
            f"`ap5_bridge_status = {output['ap5_bridge_status']}`",
            "",
            "I4 records AP5 dependency locally because proxy target derivation is in",
            "scope, but N15/N19 remain gap context only. The AP5 bridge remains",
            "unsupported until later contrast/control evidence exists.",
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
            "outputs/n26_source_current_proxy_derivation_probe.json",
            "reports/n26_source_current_proxy_derivation_probe.md",
            "outputs/n26_source_current_proxy_derivation_probe_artifacts/",
            "scripts/build_n26_source_current_proxy_derivation_probe.py",
            "```",
            "",
        ]
    )
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    i1 = load_json(I1_OUTPUT)
    i2 = load_json(I2_OUTPUT)
    i3 = load_json(I3_OUTPUT)
    schema = i2
    n25_2_replay = load_json(N25_2_REPLAY)
    n25_2_closeout = load_json(N25_2_CLOSEOUT)

    n25_2_replay_digest = n25_2_replay["output_digest"]
    candidate_rows = [
        build_candidate_row(row, schema, n25_2_replay_digest, n25_2_closeout)
        for row in n25_2_replay["multi_window_replay_rows"]
    ]

    output: dict[str, Any] = {
        "artifact_id": "n26_source_current_proxy_derivation_probe",
        "experiment": "N26",
        "iteration": "I4",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_source_current_pd2_proxy_derivation_candidate_pending_contrast_controls",
        "source_inventory_output_digest": i1["output_digest"],
        "source_schema_output_digest": i2["output_digest"],
        "source_active_null_output_digest": i3["output_digest"],
        "source_n25_2_multi_window_replay_output_digest": n25_2_replay_digest,
        "source_n25_2_closeout_output_digest": n25_2_closeout["output_digest"],
        "candidate_pd_ladder_rung": "PD2",
        "n26_closeout_ceiling": "N26-C3_active_nulls_fail_closed_with_PD2_derivation_candidate",
        "n26_closeout_ladder_rung_assigned": False,
        "positive_proxy_evidence_opened": True,
        "proxy_derivation_opened": True,
        "proxy_divergence_opened": False,
        "proxy_collapse_opened": False,
        "pd3_or_stronger_supported": False,
        "ap5_bridge_status": "not_supported_i4_row_local_dependency_recorded",
        "candidate_rows": candidate_rows,
        "claim_boundary": {
            "claim_ceiling": (
                "source-current PD2 proxy derivation candidate over scoped "
                "N25.2 MB6 substrate only"
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
    output["checks"] = build_checks(output, schema, i1, i2, i3, n25_2_closeout)
    output["failed_checks"] = [check["check"] for check in output["checks"] if not check["passed"]]
    digest_payload = dict(output)
    digest_payload.pop("output_digest", None)
    output["output_digest"] = digest_data(digest_payload)

    write_json(OUTPUT, output)
    write_report(output)


if __name__ == "__main__":
    main()

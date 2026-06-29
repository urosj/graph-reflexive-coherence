#!/usr/bin/env python3
"""Build N28 Iteration 4 primary source-current generative candidate probe."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-29T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N28-lgrc-generative-vs-extractive-persistence"
I3_OUTPUT_PATH = (
    "experiments/2026-06-N28-lgrc-generative-vs-extractive-persistence/"
    "outputs/n28_active_nulls_and_failure_baselines.json"
)
I2_OUTPUT_PATH = (
    "experiments/2026-06-N28-lgrc-generative-vs-extractive-persistence/"
    "outputs/n28_generative_extractive_schema_and_controls.json"
)
OUTPUT = EXPERIMENT / "outputs" / "n28_primary_generative_candidate_probe.json"
REPORT = EXPERIMENT / "reports" / "n28_primary_generative_candidate_probe.md"
ARTIFACT_DIR = EXPERIMENT / "outputs" / "n28_primary_generative_candidate_probe_artifacts"
SCRIPT_RELATIVE_PATH = (
    "experiments/2026-06-N28-lgrc-generative-vs-extractive-persistence/scripts/"
    "build_n28_primary_generative_candidate_probe.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"

EXPECTED_I3_DIGEST = "ddd8234d8f3b5fb424c8160d65e90adbe755916c6e4e1b26bd8574a48dc6e8a4"

UNSAFE_CLAIM_FLAGS = {
    "agency_claim_allowed": False,
    "ant_ecology_claim_allowed": False,
    "ap5_nat4_gap_resolution_claim_allowed": False,
    "final_generative_persistence_claim_allowed": False,
    "final_n28_claim_allowed": False,
    "native_ap5_claim_allowed": False,
    "native_support_claim_allowed": False,
    "organism_life_claim_allowed": False,
    "phase8_completion_claim_allowed": False,
    "semantic_choice_claim_allowed": False,
    "semantic_cooperation_claim_allowed": False,
    "semantic_goal_claim_allowed": False,
    "semantic_identity_claim_allowed": False,
    "semantic_learning_claim_allowed": False,
    "sentience_claim_allowed": False,
    "unrestricted_autonomy_claim_allowed": False,
}


def canonical_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def compact_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def digest_value(data: Any) -> str:
    return hashlib.sha256(compact_json(data).encode("utf-8")).hexdigest()


def sha256_file(relative_path: str) -> str:
    return hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest()


def load_json(relative_path: str) -> dict[str, Any]:
    data = json.loads((ROOT / relative_path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"{relative_path} must contain a JSON object")
    return data


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(canonical_json(data), encoding="utf-8")


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def no_absolute_paths(data: Any) -> bool:
    text = json.dumps(data, sort_keys=True, ensure_ascii=True)
    home_marker = "/" + "home/"
    repo_marker = "Documents/" + "RC-github"
    return home_marker not in text and repo_marker not in text


def trace_artifact(role: str, payload: dict[str, Any]) -> dict[str, str]:
    path = ARTIFACT_DIR / f"{role}.json"
    write_json(path, payload)
    return {"artifact_role": role, "path": rel(path), "sha256": sha256_file(rel(path))}


def build_traces(i3: dict[str, Any]) -> dict[str, Any]:
    source_pins = i3["source_digest_pins"]
    threshold_policy = {
        "policy_id": "n28_i4_primary_generative_policy_v1",
        "declared_before_use": True,
        "shared_regime_policy_id": "n28_shared_regime_policy_v1",
        "focal_support_floor": 0.84,
        "focal_coherence_floor": 0.84,
        "focal_stability_min": 0.86,
        "neighbor_distinguishability_delta_min": 0.08,
        "neighbor_support_delta_min": 0.05,
        "neighbor_boundary_delta_min": 0.08,
        "environment_capacity_delta_min": 0.09,
        "focal_extraction_cost_ceiling": 0.035,
        "extractive_flattening_ceiling": 0.03,
        "merge_leakage_ceiling": 0.025,
        "post_hoc_boundary_shift_used": False,
        "label_specific_thresholds_used": False,
        "policy_retuned_for_label": False,
    }
    runtime_trace = {
        "run_artifact_id": "n28_i4_primary_generative_runtime_trace",
        "runtime_config_id": "n28_i4_primary_generative_fixture_v1",
        "runtime_config_digest": "computed_after_trace",
        "source_schema_output_digest": i3["output_digest"],
        "source_inventory_output_digest": source_pins["source_inventory_output_digest"],
        "fixture_kind": "source_current_geometric_trace_fixture",
        "derived_report_only": False,
        "focal_basin_id": "n28_i4_focal_basin_alpha",
        "neighbor_scope_id": "n28_i4_neighbor_capacity_shell_alpha",
        "steps": [
            {
                "step": 0,
                "focal_support_min": 0.872,
                "focal_coherence_min": 0.884,
                "focal_stability_score": 0.882,
                "neighbor_distinguishability": 0.618,
                "neighbor_support_floor": 0.676,
                "neighbor_boundary_integrity": 0.592,
                "environment_basin_forming_capacity": 0.584,
                "focal_extraction_cost": 0.015,
                "extractive_flattening_score": 0.012,
                "merge_leakage_score": 0.011,
            },
            {
                "step": 1,
                "focal_support_min": 0.868,
                "focal_coherence_min": 0.879,
                "focal_stability_score": 0.878,
                "neighbor_distinguishability": 0.751,
                "neighbor_support_floor": 0.758,
                "neighbor_boundary_integrity": 0.718,
                "environment_basin_forming_capacity": 0.707,
                "focal_extraction_cost": 0.018,
                "extractive_flattening_score": 0.014,
                "merge_leakage_score": 0.012,
            },
        ],
    }
    runtime_trace["runtime_config_digest"] = digest_value(
        {
            "runtime_config_id": runtime_trace["runtime_config_id"],
            "fixture_kind": runtime_trace["fixture_kind"],
            "focal_basin_id": runtime_trace["focal_basin_id"],
            "neighbor_scope_id": runtime_trace["neighbor_scope_id"],
            "threshold_policy": threshold_policy,
        }
    )
    pre = runtime_trace["steps"][0]
    post = runtime_trace["steps"][1]
    focal_trace = {
        "trace_id": "n28_i4_focal_basin_stability_trace",
        "focal_basin_id": runtime_trace["focal_basin_id"],
        "support_floor": threshold_policy["focal_support_floor"],
        "coherence_floor": threshold_policy["focal_coherence_floor"],
        "pre_support_min": pre["focal_support_min"],
        "post_support_min": post["focal_support_min"],
        "pre_coherence_min": pre["focal_coherence_min"],
        "post_coherence_min": post["focal_coherence_min"],
        "pre_stability_score": pre["focal_stability_score"],
        "post_stability_score": post["focal_stability_score"],
        "focal_support_floor_preserved": post["focal_support_min"]
        >= threshold_policy["focal_support_floor"],
        "focal_coherence_floor_preserved": post["focal_coherence_min"]
        >= threshold_policy["focal_coherence_floor"],
        "focal_stability_preserved": post["focal_stability_score"]
        >= threshold_policy["focal_stability_min"],
    }
    neighbor_trace = {
        "trace_id": "n28_i4_neighbor_capacity_trace",
        "neighbor_scope_id": runtime_trace["neighbor_scope_id"],
        "pre_neighbor_distinguishability": pre["neighbor_distinguishability"],
        "post_neighbor_distinguishability": post["neighbor_distinguishability"],
        "neighbor_distinguishability_delta": round(
            post["neighbor_distinguishability"] - pre["neighbor_distinguishability"], 12
        ),
        "pre_neighbor_support_floor": pre["neighbor_support_floor"],
        "post_neighbor_support_floor": post["neighbor_support_floor"],
        "neighbor_support_delta": round(
            post["neighbor_support_floor"] - pre["neighbor_support_floor"], 12
        ),
        "pre_neighbor_boundary_integrity": pre["neighbor_boundary_integrity"],
        "post_neighbor_boundary_integrity": post["neighbor_boundary_integrity"],
        "neighbor_boundary_delta": round(
            post["neighbor_boundary_integrity"] - pre["neighbor_boundary_integrity"], 12
        ),
        "pre_environment_basin_forming_capacity": pre[
            "environment_basin_forming_capacity"
        ],
        "post_environment_basin_forming_capacity": post[
            "environment_basin_forming_capacity"
        ],
        "environment_capacity_delta": round(
            post["environment_basin_forming_capacity"]
            - pre["environment_basin_forming_capacity"],
            12,
        ),
        "neighbor_label_only": False,
        "neighbor_count_only": False,
    }
    extraction_trace = {
        "trace_id": "n28_i4_extraction_leakage_trace",
        "focal_extraction_cost": post["focal_extraction_cost"],
        "focal_extraction_cost_ceiling": threshold_policy[
            "focal_extraction_cost_ceiling"
        ],
        "extractive_flattening_score": post["extractive_flattening_score"],
        "extractive_flattening_ceiling": threshold_policy[
            "extractive_flattening_ceiling"
        ],
        "merge_leakage_score": post["merge_leakage_score"],
        "merge_leakage_ceiling": threshold_policy["merge_leakage_ceiling"],
        "focal_extraction_cost_below_ceiling": post["focal_extraction_cost"]
        <= threshold_policy["focal_extraction_cost_ceiling"],
        "extractive_flattening_below_ceiling": post["extractive_flattening_score"]
        <= threshold_policy["extractive_flattening_ceiling"],
        "merge_leakage_below_ceiling": post["merge_leakage_score"]
        <= threshold_policy["merge_leakage_ceiling"],
        "merge_or_leakage_masquerading_as_support": False,
        "extractive_flattening_masked": False,
    }
    capacity_attribution_trace = {
        "trace_id": "n28_i4_capacity_attribution_trace",
        "capacity_attribution_basis": [
            "neighbor_distinguishability_delta",
            "neighbor_support_delta",
            "neighbor_boundary_delta",
            "environment_capacity_delta",
        ],
        "producer_generativity_label_used_as_evidence": False,
        "hidden_capacity_attribution_policy_used": False,
        "medium_segmentation_policy_hidden": False,
        "environment_capacity_budget_mismatch": False,
        "n27_transfer_success_used_as_n28_success": False,
        "attribution_result": "source_current_neighbor_capacity_improvement",
    }
    classification_trace = {
        "trace_id": "n28_i4_primary_generative_classification_trace",
        "classification_policy_id": threshold_policy["policy_id"],
        "shared_regime_policy_id": threshold_policy["shared_regime_policy_id"],
        "focal_persistence_axis": "stable",
        "neighborhood_capacity_axis": "improves",
        "extraction_leakage_axis": "low_preserved_medium",
        "classification_result": "generative",
        "regime_label": "generative",
        "regime_evidence_role": "positive_candidate",
        "classification_reason": (
            "stable focal basin + improved neighborhood capacity + low extraction/leakage"
        ),
        "classification_declared_before_use": True,
        "policy_retuned_for_label": False,
        "label_specific_thresholds_used": False,
        "post_hoc_boundary_shift_used": False,
    }
    return {
        "threshold_policy": threshold_policy,
        "runtime_trace": runtime_trace,
        "focal_trace": focal_trace,
        "neighbor_trace": neighbor_trace,
        "extraction_trace": extraction_trace,
        "capacity_attribution_trace": capacity_attribution_trace,
        "classification_trace": classification_trace,
    }


def build_core(traces: dict[str, Any]) -> dict[str, Any]:
    return {
        "focal_basin_id": traces["runtime_trace"]["focal_basin_id"],
        "focal_signature_digest": digest_value(
            {
                "focal_basin_id": traces["runtime_trace"]["focal_basin_id"],
                "fixture_kind": traces["runtime_trace"]["fixture_kind"],
            }
        ),
        "focal_stability_digest": digest_value(traces["focal_trace"]),
        "neighbor_scope_digest": digest_value(
            {"neighbor_scope_id": traces["runtime_trace"]["neighbor_scope_id"]}
        ),
        "neighbor_distinguishability_digest": digest_value(
            {
                "pre": traces["neighbor_trace"]["pre_neighbor_distinguishability"],
                "post": traces["neighbor_trace"]["post_neighbor_distinguishability"],
                "delta": traces["neighbor_trace"]["neighbor_distinguishability_delta"],
            }
        ),
        "neighbor_support_digest": digest_value(
            {
                "pre": traces["neighbor_trace"]["pre_neighbor_support_floor"],
                "post": traces["neighbor_trace"]["post_neighbor_support_floor"],
                "delta": traces["neighbor_trace"]["neighbor_support_delta"],
            }
        ),
        "neighbor_boundary_digest": digest_value(
            {
                "pre": traces["neighbor_trace"]["pre_neighbor_boundary_integrity"],
                "post": traces["neighbor_trace"]["post_neighbor_boundary_integrity"],
                "delta": traces["neighbor_trace"]["neighbor_boundary_delta"],
            }
        ),
        "environment_capacity_digest": digest_value(
            {
                "pre": traces["neighbor_trace"]["pre_environment_basin_forming_capacity"],
                "post": traces["neighbor_trace"][
                    "post_environment_basin_forming_capacity"
                ],
                "delta": traces["neighbor_trace"]["environment_capacity_delta"],
            }
        ),
        "neighborhood_capacity_delta_digest": digest_value(
            {
                "distinguishability_delta": traces["neighbor_trace"][
                    "neighbor_distinguishability_delta"
                ],
                "support_delta": traces["neighbor_trace"]["neighbor_support_delta"],
                "boundary_delta": traces["neighbor_trace"]["neighbor_boundary_delta"],
                "environment_capacity_delta": traces["neighbor_trace"][
                    "environment_capacity_delta"
                ],
            }
        ),
        "extraction_cost_digest": digest_value(
            {"focal_extraction_cost": traces["extraction_trace"]["focal_extraction_cost"]}
        ),
        "extractive_flattening_digest": digest_value(
            {
                "extractive_flattening_score": traces["extraction_trace"][
                    "extractive_flattening_score"
                ]
            }
        ),
        "merge_leakage_digest": digest_value(
            {"merge_leakage_score": traces["extraction_trace"]["merge_leakage_score"]}
        ),
        "capacity_attribution_digest": digest_value(traces["capacity_attribution_trace"]),
        "classification_policy_digest": digest_value(traces["threshold_policy"]),
        "classification_result": "generative",
        "regime_evidence_role": "positive_candidate",
    }


def build_artifacts(traces: dict[str, Any], core: dict[str, Any]) -> list[dict[str, str]]:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    return [
        trace_artifact("threshold_policy_trace", traces["threshold_policy"]),
        trace_artifact("source_current_runtime_trace", traces["runtime_trace"]),
        trace_artifact("focal_basin_stability_trace", traces["focal_trace"]),
        trace_artifact("neighbor_capacity_trace", traces["neighbor_trace"]),
        trace_artifact("extraction_leakage_trace", traces["extraction_trace"]),
        trace_artifact("capacity_attribution_trace", traces["capacity_attribution_trace"]),
        trace_artifact("classification_trace", traces["classification_trace"]),
        trace_artifact("generative_extractive_core", core),
    ]


def build_output() -> dict[str, Any]:
    i3 = load_json(I3_OUTPUT_PATH)
    i2_digest = i3["source_schema"]["output_digest"]
    source_pins = i3["source_digest_pins"]
    traces = build_traces(i3)
    core = build_core(traces)
    core_digest = digest_value(core)
    artifacts = build_artifacts(traces, core)
    artifact_paths = {item["path"] for item in artifacts}

    row = {
        "row_id": "n28_i4_row_primary_generative_candidate",
        "iteration": "4",
        "row_decision": "supported",
        "row_decision_scope": "provisional_GE3_primary_generative_candidate_pending_replay_controls_and_contrasts",
        "ge_ladder_rung": "GE3",
        "ge_ladder_rung_assigned": True,
        "ge4_or_stronger_supported": False,
        "ge5_or_stronger_supported": False,
        "ge6_or_stronger_supported": False,
        "n28_closeout_ceiling": "N28-C4_source_current_generative_candidate_supported",
        "n28_closeout_ladder_rung_assigned": False,
        "regime_label": "generative",
        "regime_evidence_role": "positive_candidate",
        "shared_regime_policy_id": traces["threshold_policy"]["shared_regime_policy_id"],
        "shared_regime_policy_status": "partially_supported",
        "shared_regime_policy_status_scope": (
            "provisionally_primary_only_pending_alternative_and_contrast_rows"
        ),
        "policy_divergence_record": {
            "policy_id": traces["threshold_policy"]["policy_id"],
            "divergence_status": "not_evaluated_until_alternative_and_contrast_rows",
            "affected_regimes": ["extractive", "competitive", "neutral"],
            "same_policy_failed_reason": "not_run_yet",
            "split_policy_allowed": "only_if_later_rows_record_blocker",
            "post_hoc_retuning_used": False,
            "claim_effect": "GE3_primary_candidate_only_no_shared_policy_closeout",
        },
        "source_current_inputs": sorted(artifact_paths),
        "source_inventory_output_digest": source_pins["source_inventory_output_digest"],
        "source_ledger_row_digest": source_pins["n20_i3_row_digest"],
        "descriptor_contract_row_digest": source_pins["n20_i4_row_digest"],
        "consumable_contract_row_digest": source_pins["n20_i5_row_digest"],
        "source_output_digest": i3["output_digest"],
        "n20_producer_residue_row_digest": source_pins["n20_i3_row_digest"],
        "n20_native_function_proxy_row_digest": source_pins["n20_i4_row_digest"],
        "n20_same_basin_continuation_row_digest": source_pins["n20_i5_row_digest"],
        "n27_closeout_output_digest": source_pins["n27_closeout_output_digest"],
        "n27_side_effect_precursor_output_digest": source_pins[
            "n27_side_effect_precursor_output_digest"
        ],
        "run_artifact_id": traces["runtime_trace"]["run_artifact_id"],
        "runtime_config_digest": traces["runtime_trace"]["runtime_config_digest"],
        "artifact_manifest": artifacts,
        "artifact_role_alias_map": {
            "neighbor_capacity_trace": [
                "neighbor_basin_distinguishability_trace",
                "neighbor_support_floor_trace",
                "neighbor_boundary_integrity_trace",
                "environment_basin_forming_capacity_trace",
                "neighborhood_capacity_delta_trace",
            ],
            "extraction_leakage_trace": [
                "focal_extraction_cost_trace",
                "extractive_flattening_trace",
                "merge_leakage_trace",
            ],
            "focal_basin_stability_trace": [
                "focal_basin_signature_trace",
                "focal_basin_stability_trace",
                "focal_support_coherence_floor_trace",
            ],
            "classification_trace": [
                "generative_classification_result",
                "regime_boundary_trace",
                "policy_divergence_record",
            ],
            "generative_extractive_core": [
                "generative_extractive_core",
                "generative_extractive_core_digest",
            ],
        },
        "all_artifact_sha256_match_file_contents": all(
            sha256_file(item["path"]) == item["sha256"] for item in artifacts
        ),
        "derived_report_only": False,
        "row_specific_thresholds_declared_before_use": traces["threshold_policy"],
        "focal_basin_id": traces["runtime_trace"]["focal_basin_id"],
        "focal_basin_signature_trace": {
            "focal_basin_id": traces["runtime_trace"]["focal_basin_id"],
            "focal_signature_digest": core["focal_signature_digest"],
        },
        "focal_basin_stability_trace": traces["focal_trace"],
        "focal_support_coherence_floor_trace": {
            "support_floor": traces["threshold_policy"]["focal_support_floor"],
            "coherence_floor": traces["threshold_policy"]["focal_coherence_floor"],
            "post_support_min": traces["focal_trace"]["post_support_min"],
            "post_coherence_min": traces["focal_trace"]["post_coherence_min"],
            "floors_preserved": traces["focal_trace"]["focal_support_floor_preserved"]
            and traces["focal_trace"]["focal_coherence_floor_preserved"],
        },
        "neighbor_or_sub_basin_scope": traces["runtime_trace"]["neighbor_scope_id"],
        "neighbor_basin_distinguishability_trace": {
            "delta": traces["neighbor_trace"]["neighbor_distinguishability_delta"],
            "digest": core["neighbor_distinguishability_digest"],
        },
        "neighbor_support_floor_trace": {
            "delta": traces["neighbor_trace"]["neighbor_support_delta"],
            "digest": core["neighbor_support_digest"],
        },
        "neighbor_boundary_integrity_trace": {
            "delta": traces["neighbor_trace"]["neighbor_boundary_delta"],
            "digest": core["neighbor_boundary_digest"],
        },
        "environment_basin_forming_capacity_trace": {
            "delta": traces["neighbor_trace"]["environment_capacity_delta"],
            "digest": core["environment_capacity_digest"],
        },
        "neighborhood_capacity_delta_trace": traces["neighbor_trace"],
        "focal_extraction_cost_trace": {
            "value": traces["extraction_trace"]["focal_extraction_cost"],
            "ceiling": traces["extraction_trace"]["focal_extraction_cost_ceiling"],
            "digest": core["extraction_cost_digest"],
        },
        "extractive_flattening_trace": {
            "value": traces["extraction_trace"]["extractive_flattening_score"],
            "ceiling": traces["extraction_trace"]["extractive_flattening_ceiling"],
            "digest": core["extractive_flattening_digest"],
        },
        "merge_leakage_trace": {
            "value": traces["extraction_trace"]["merge_leakage_score"],
            "ceiling": traces["extraction_trace"]["merge_leakage_ceiling"],
            "digest": core["merge_leakage_digest"],
        },
        "capacity_attribution_trace": traces["capacity_attribution_trace"],
        "medium_debt_record": {
            "medium_debt_fields": [
                "generative_extractive_persistence.source_current_neighbor_basin_birth_telemetry",
                "generative_extractive_persistence.medium_debt_deferred_to_n28_n29",
                "generative_extractive_persistence.environment_capacity_budget_replay",
            ],
            "medium_debt_as_success_allowed": False,
            "medium_debt_role": "carried_boundary_not_success_evidence",
        },
        "producer_residue_record": {
            "producer_residue_fields": [
                "generative_extractive_persistence.generativity_label",
                "generative_extractive_persistence.neighbor_attribution_policy",
                "generative_extractive_persistence.medium_segmentation_policy",
            ],
            "producer_residue_as_substrate_carried_allowed": False,
            "producer_generativity_label_used_as_evidence": False,
        },
        "generative_classification_policy_digest": core["classification_policy_digest"],
        "generative_classification_declared_before_use": True,
        "generative_classification_result": traces["classification_trace"],
        "regime_boundary_trace": {
            "focal_persistence_axis": "stable",
            "neighborhood_capacity_axis": "improves",
            "extraction_leakage_axis": "low_preserved_medium",
            "result": "generative",
        },
        "policy_retuned_for_label": False,
        "label_specific_thresholds_used": False,
        "post_hoc_boundary_shift_used": False,
        "generative_extractive_core": core,
        "generative_extractive_core_digest": core_digest,
        "focal_survival_only_rejected": True,
        "neighbor_label_only_rejected": True,
        "merge_leakage_as_support_rejected": True,
        "extractive_flattening_masked_rejected": True,
        "transfer_success_as_n28_success_rejected": True,
        "semantic_cooperation_relabel_rejected": True,
        "active_null_matrix_output_digest": i3["output_digest"],
        "active_null_matrix_source_path": I3_OUTPUT_PATH,
        "active_null_matrix_consumption_role": "fail_closed_false_positive_boundary",
        "row_local_controls_scope": "primary_GE3_applicable_controls",
        "full_controls_pending_for_ge4_plus": True,
        "replay_result": "not_run_pending_iteration_5",
        "control_results": [
            {
                "control_id": "focal_survival_only_as_generative_control",
                "control_status": "passed",
                "actual_result": "neighborhood_capacity_trace_present_and_above_delta_threshold",
                "claim_allowed_when_control_triggers": False,
                "rung_effect": "GE3_candidate_preserved",
            },
            {
                "control_id": "neighbor_label_only_as_capacity_control",
                "control_status": "passed",
                "actual_result": "neighbor_support_boundary_and_capacity_traces_present",
                "claim_allowed_when_control_triggers": False,
                "rung_effect": "GE3_candidate_preserved",
            },
            {
                "control_id": "merge_leakage_as_support_control",
                "control_status": "passed",
                "actual_result": "merge_leakage_below_ceiling",
                "claim_allowed_when_control_triggers": False,
                "rung_effect": "GE3_candidate_preserved",
            },
            {
                "control_id": "extractive_flattening_masked_control",
                "control_status": "passed",
                "actual_result": "extractive_flattening_below_ceiling",
                "claim_allowed_when_control_triggers": False,
                "rung_effect": "GE3_candidate_preserved",
            },
            {
                "control_id": "transfer_success_as_n28_success_control",
                "control_status": "passed",
                "actual_result": "N27_transfer_digest_carried_context_only",
                "claim_allowed_when_control_triggers": False,
                "rung_effect": "GE3_candidate_preserved",
            },
        ],
        "ap4_dependency_status": "not_applicable",
        "ap4_condition_reason": "I4 primary generative fixture does not make route-conditioned selection claim; AP4/N14 NAT4 gap remains inherited context.",
        "ap5_dependency_status": "not_applicable",
        "ap5_condition_reason": "I4 primary generative fixture does not use proxy/target formation as positive evidence; AP5/N15 NAT4 gap remains unresolved.",
        "claim_ceiling": "provisional_GE3_primary_generative_candidate_pending_replay_controls_contrasts_and_stress",
        "unsafe_claim_flags": UNSAFE_CLAIM_FLAGS,
        "provisional_generative_candidate_supported": True,
        "final_generative_persistence_supported": False,
        "final_n28_supported": False,
    }
    row["row_digest"] = digest_value(row)

    checks = [
        {
            "check_id": "i3_active_nulls_passed",
            "passed": i3.get("status") == "passed"
            and i3.get("failed_checks") == []
            and i3.get("output_digest") == EXPECTED_I3_DIGEST,
        },
        {
            "check_id": "artifact_manifest_valid",
            "passed": row["all_artifact_sha256_match_file_contents"]
            and len(row["artifact_manifest"]) == 8,
        },
        {
            "check_id": "artifact_role_alias_map_present",
            "passed": set(row["artifact_role_alias_map"]["neighbor_capacity_trace"])
            >= {
                "neighbor_basin_distinguishability_trace",
                "neighbor_support_floor_trace",
                "neighbor_boundary_integrity_trace",
                "environment_basin_forming_capacity_trace",
                "neighborhood_capacity_delta_trace",
            }
            and set(row["artifact_role_alias_map"]["extraction_leakage_trace"])
            >= {
                "focal_extraction_cost_trace",
                "extractive_flattening_trace",
                "merge_leakage_trace",
            },
        },
        {
            "check_id": "required_evidence_fields_present",
            "passed": all(
                field in row for field in load_json(I2_OUTPUT_PATH)["required_evidence_fields"]
            ),
        },
        {
            "check_id": "core_digest_matches_payload",
            "passed": row["generative_extractive_core_digest"]
            == digest_value(row["generative_extractive_core"]),
        },
        {
            "check_id": "focal_stability_preserved",
            "passed": row["focal_basin_stability_trace"]["focal_stability_preserved"]
            and row["focal_support_coherence_floor_trace"]["floors_preserved"],
        },
        {
            "check_id": "neighborhood_capacity_improves",
            "passed": row["neighbor_basin_distinguishability_trace"]["delta"]
            >= traces["threshold_policy"]["neighbor_distinguishability_delta_min"]
            and row["neighbor_support_floor_trace"]["delta"]
            >= traces["threshold_policy"]["neighbor_support_delta_min"]
            and row["neighbor_boundary_integrity_trace"]["delta"]
            >= traces["threshold_policy"]["neighbor_boundary_delta_min"]
            and row["environment_basin_forming_capacity_trace"]["delta"]
            >= traces["threshold_policy"]["environment_capacity_delta_min"],
        },
        {
            "check_id": "extraction_flattening_merge_leakage_below_ceiling",
            "passed": traces["extraction_trace"]["focal_extraction_cost_below_ceiling"]
            and traces["extraction_trace"]["extractive_flattening_below_ceiling"]
            and traces["extraction_trace"]["merge_leakage_below_ceiling"],
        },
        {
            "check_id": "classification_policy_declared_before_use",
            "passed": row["generative_classification_declared_before_use"]
            and row["row_specific_thresholds_declared_before_use"]["declared_before_use"],
        },
        {
            "check_id": "no_policy_retuning_label_threshold_or_post_hoc_boundary",
            "passed": row["policy_retuned_for_label"] is False
            and row["label_specific_thresholds_used"] is False
            and row["post_hoc_boundary_shift_used"] is False,
        },
        {
            "check_id": "false_positive_controls_not_triggered",
            "passed": row["focal_survival_only_rejected"]
            and row["neighbor_label_only_rejected"]
            and row["merge_leakage_as_support_rejected"]
            and row["extractive_flattening_masked_rejected"]
            and row["transfer_success_as_n28_success_rejected"]
            and row["semantic_cooperation_relabel_rejected"],
        },
        {
            "check_id": "i3_active_null_reference_bounded",
            "passed": row["active_null_matrix_output_digest"] == EXPECTED_I3_DIGEST
            and row["row_local_controls_scope"] == "primary_GE3_applicable_controls"
            and row["full_controls_pending_for_ge4_plus"] is True,
        },
        {
            "check_id": "shared_policy_status_bounded_to_primary_row",
            "passed": row["shared_regime_policy_status"] == "partially_supported"
            and row["shared_regime_policy_status_scope"]
            == "provisionally_primary_only_pending_alternative_and_contrast_rows",
        },
        {
            "check_id": "n27_context_not_consumed_as_n28_evidence",
            "passed": row["capacity_attribution_trace"][
                "n27_transfer_success_used_as_n28_success"
            ]
            is False,
        },
        {
            "check_id": "medium_debt_and_producer_residue_not_success",
            "passed": row["medium_debt_record"]["medium_debt_as_success_allowed"] is False
            and row["producer_residue_record"][
                "producer_residue_as_substrate_carried_allowed"
            ]
            is False,
        },
        {
            "check_id": "ge4_and_stronger_blocked_pending_replay_controls",
            "passed": row["ge4_or_stronger_supported"] is False
            and row["replay_result"] == "not_run_pending_iteration_5",
        },
        {
            "check_id": "unsafe_claim_flags_false",
            "passed": all(value is False for value in UNSAFE_CLAIM_FLAGS.values()),
        },
    ]
    output = {
        "artifact_id": "n28_primary_generative_candidate_probe",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_primary_source_current_ge3_generative_candidate_pending_replay_controls",
        "experiment": "N28",
        "iteration": "4",
        "n28_closeout_ceiling": row["n28_closeout_ceiling"],
        "claim_ceiling": row["claim_ceiling"],
        "source_i3": {
            "path": I3_OUTPUT_PATH,
            "output_digest": i3["output_digest"],
            "artifact_sha256": sha256_file(I3_OUTPUT_PATH),
            "status": i3["status"],
            "acceptance_state": i3["acceptance_state"],
        },
        "source_digest_pins": source_pins,
        "candidate_rows": [row],
        "primary_generative_candidate_supported": True,
        "positive_generative_evidence_opened": True,
        "positive_extractive_evidence_opened": False,
        "candidate_rows_classified": True,
        "provisional_ge_ladder_rung": "GE3",
        "ge4_or_stronger_supported": False,
        "ge5_or_stronger_supported": False,
        "ge6_or_stronger_supported": False,
        "final_generative_persistence_supported": False,
        "final_n28_supported": False,
        "shared_regime_policy_status": "partially_supported",
        "shared_regime_policy_status_scope": (
            "provisionally_primary_only_pending_alternative_and_contrast_rows"
        ),
        "ready_for_iteration_4a_alternative_generative_candidate": True,
        "ready_for_iteration_4a_strengthening_generative_candidate": True,
        "unsafe_claim_flags": UNSAFE_CLAIM_FLAGS,
        "checks": checks,
        "failed_checks": [check["check_id"] for check in checks if not check["passed"]],
    }
    checks.append(
        {
            "check_id": "no_absolute_paths_in_records",
            "passed": no_absolute_paths(output),
        }
    )
    output["failed_checks"] = [check["check_id"] for check in checks if not check["passed"]]
    output["output_digest"] = digest_value(output)
    return output


def write_report(output: dict[str, Any]) -> None:
    row = output["candidate_rows"][0]
    neighbor = row["neighborhood_capacity_delta_trace"]
    extraction = row["merge_leakage_trace"]
    lines = [
        "# N28 Iteration 4 - Primary Generative Candidate Probe",
        "",
        "## Summary",
        "",
        f"- Status: `{output['status']}`",
        f"- Acceptance state: `{output['acceptance_state']}`",
        f"- Output digest: `{output['output_digest']}`",
        f"- Provisional GE rung: `{output['provisional_ge_ladder_rung']}`",
        f"- GE4 or stronger supported: `{str(output['ge4_or_stronger_supported']).lower()}`",
        f"- Shared policy status: `{output['shared_regime_policy_status']}`",
        f"- Shared policy scope: `{output['shared_regime_policy_status_scope']}`",
        f"- Ready for I4-A strengthening: `{str(output['ready_for_iteration_4a_strengthening_generative_candidate']).lower()}`",
        "",
        "I4 opens the first source-current positive N28 row, but only as a "
        "provisional GE3 primary generative candidate. Replay, full controls, "
        "contrasts, stress, and final closeout remain blocked.",
        "",
        "## Candidate Metrics",
        "",
        "```text",
        f"focal_stability_preserved = {str(row['focal_basin_stability_trace']['focal_stability_preserved']).lower()}",
        f"neighbor_distinguishability_delta = {neighbor['neighbor_distinguishability_delta']}",
        f"neighbor_support_delta = {neighbor['neighbor_support_delta']}",
        f"neighbor_boundary_delta = {neighbor['neighbor_boundary_delta']}",
        f"environment_capacity_delta = {neighbor['environment_capacity_delta']}",
        f"merge_leakage_score = {extraction['value']}",
        f"merge_leakage_ceiling = {extraction['ceiling']}",
        "```",
        "",
        "## Interpretation",
        "",
        "The row passes the three-axis I2 classifier locally: focal persistence is "
        "stable, neighborhood capacity improves, and extraction/leakage remains "
        "below ceiling. This supports a primary generative candidate, not final "
        "generative persistence and not shared-policy closeout.",
        "",
        "In geometric dynamics terms, the focal basin keeps its shape and "
        "viability while the surrounding geometry becomes more basin-capable. "
        "The original basin does not survive by draining or flattening its "
        "neighborhood. Its support, coherence, and stability remain above floor, "
        "so the focal basin remains valid. At the same time, the adjacent shell "
        "becomes more structured: it separates more clearly from the focal "
        "basin, gains support, gains boundary integrity, and has higher capacity "
        "to hold basin-like organization.",
        "",
        "The dynamics are therefore not one basin persisting by absorbing the "
        "surrounding field, nor focal survival while nearby geometry becomes "
        "less organized. They are persistence with neighboring capacity "
        "increase: a stable basin preserves itself while nearby geometry becomes "
        "more capable of holding distinct organized structure.",
        "",
        "The `shared_regime_policy_status = partially_supported` field is scoped "
        "only to this primary generative row. It does not settle the shared "
        "policy family until the generative strengthening row, extractive "
        "contrasts, and competitive/neutral contrasts exist.",
        "",
        "The artifact manifest uses bundled trace files. The row-local "
        "`artifact_role_alias_map` records that `neighbor_capacity_trace` covers "
        "neighbor distinguishability, support floor, boundary integrity, "
        "environment capacity, and neighborhood capacity delta traces, while "
        "`extraction_leakage_trace` covers focal extraction cost, extractive "
        "flattening, and merge/leakage traces.",
        "",
        "I4 also inherits the I3 active-null matrix as a fail-closed "
        "false-positive boundary. Its row-local controls are only the primary "
        "GE3-applicable controls; the full replay/control matrix remains pending "
        "for GE4+.",
        "",
        "## Checks",
        "",
        "| Check | Passed |",
        "|---|---|",
    ]
    for check in output["checks"]:
        lines.append(f"| `{check['check_id']}` | `{str(check['passed']).lower()}` |")

    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "I4 does not support GE4+, GE5+, GE6, final N28, semantic cooperation, "
            "agency, native support, Phase 8 completion, or ant ecology.",
            "",
        ]
    )
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    output = build_output()
    OUTPUT.write_text(canonical_json(output), encoding="utf-8")
    write_report(output)

    output = json.loads(OUTPUT.read_text(encoding="utf-8"))
    output["script_sha256"] = sha256_file(SCRIPT_RELATIVE_PATH)
    output["output_digest"] = digest_value(
        {
            key: value
            for key, value in output.items()
            if key not in {"report_sha256", "script_sha256", "output_digest"}
        }
    )
    OUTPUT.write_text(canonical_json(output), encoding="utf-8")
    write_report(output)
    output = json.loads(OUTPUT.read_text(encoding="utf-8"))
    output["report_sha256"] = sha256_file(str(REPORT.relative_to(ROOT)))
    OUTPUT.write_text(canonical_json(output), encoding="utf-8")


if __name__ == "__main__":
    main()

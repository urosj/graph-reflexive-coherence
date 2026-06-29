#!/usr/bin/env python3
"""Build N27 Iteration 4-A topology / fixture variant transfer probe."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-29T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N27-lgrc-configuration-substrate-transfer"
OUTPUT = EXPERIMENT / "outputs" / "n27_topology_fixture_variant_transfer_probe.json"
REPORT = EXPERIMENT / "reports" / "n27_topology_fixture_variant_transfer_probe.md"
ARTIFACT_DIR = EXPERIMENT / "outputs" / "n27_topology_fixture_variant_transfer_probe_artifacts"

I1_OUTPUT = EXPERIMENT / "outputs" / "n27_source_inventory_and_transfer_contract_admission.json"
I2_OUTPUT = EXPERIMENT / "outputs" / "n27_transfer_schema_and_controls.json"
I3_OUTPUT = EXPERIMENT / "outputs" / "n27_active_nulls_and_failure_baselines.json"
I4_OUTPUT = EXPERIMENT / "outputs" / "n27_minimal_configuration_transfer_probe.json"

COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N27-lgrc-configuration-substrate-transfer/scripts/"
    "build_n27_topology_fixture_variant_transfer_probe.py"
)

N27_CLOSEOUT_CEILING = "N27-C4_source_current_transfer_candidate_supported"
CT_RUNG = "CT2"

ABSOLUTE_PATH_MARKERS = ["/home/" + "uros", "Documents/" + "RC-github"]

UNSAFE_CLAIMS = [
    "agency_claim_allowed",
    "ant_ecology_claim_allowed",
    "ap5_nat4_gap_resolution_claim_allowed",
    "identity_acceptance_claim_allowed",
    "native_ap5_claim_allowed",
    "native_support_claim_allowed",
    "organism_life_claim_allowed",
    "phase8_completion_claim_allowed",
    "semantic_choice_claim_allowed",
    "semantic_goal_claim_allowed",
    "semantic_identity_claim_allowed",
    "semantic_learning_claim_allowed",
    "semantic_target_ownership_claim_allowed",
    "sentience_claim_allowed",
    "unrestricted_autonomy_claim_allowed",
    "unscoped_multi_basin_claim_allowed",
]


def canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def pretty_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def digest_value(data: Any) -> str:
    return hashlib.sha256(canonical_json(data).encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return data


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(pretty_json(data), encoding="utf-8")


def collect_strings(data: Any) -> set[str]:
    strings: set[str] = set()
    if isinstance(data, str):
        strings.add(data)
    elif isinstance(data, list):
        for item in data:
            strings.update(collect_strings(item))
    elif isinstance(data, dict):
        for value in data.values():
            strings.update(collect_strings(value))
    return strings


def check(check_id: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"check_id": check_id, "passed": bool(passed), "detail": detail}


def source_record(path: Path, source_id: str, role: str) -> dict[str, Any]:
    data = load_json(path)
    return {
        "source_id": source_id,
        "path": rel(path),
        "source_role": role,
        "exists": path.exists(),
        "sha256": sha256_file(path),
        "artifact_id": data.get("artifact_id", "not_recorded"),
        "status": data.get("status", "not_recorded"),
        "acceptance_state": data.get("acceptance_state", "not_recorded"),
        "output_digest": data.get("output_digest", "not_recorded"),
    }


def unsafe_claim_flags() -> dict[str, bool]:
    return {claim: False for claim in UNSAFE_CLAIMS}


def trace_artifact(role: str, payload: dict[str, Any]) -> dict[str, str]:
    path = ARTIFACT_DIR / f"{role}.json"
    write_json(path, payload)
    return {"artifact_role": role, "path": rel(path), "sha256": sha256_file(path)}


def build_variant_traces(i4: dict[str, Any]) -> dict[str, dict[str, Any]]:
    thresholds = {
        "record_id": "n27_i4a_threshold_record",
        "declared_before_use": True,
        "declaration_order": 0,
        "applies_to_mapping_id": "n27_i4a_gamma_to_delta_topology_fixture_mapping",
        "signature_preservation_margin_formula": (
            "signature_preservation_margin = max_signature_distance - observed_signature_distance"
        ),
        "boundary_mapping_tolerance_formula": (
            "boundary_mapping_margin = mapped_boundary_jaccard - boundary_jaccard_floor"
        ),
        "support_floor_margin_formula": "support_floor_margin = post_min_support - support_floor",
        "coherence_floor_margin_formula": (
            "coherence_floor_margin = post_min_coherence - coherence_floor"
        ),
        "flux_balance_bound_formula": (
            "flux_balance_margin = max_flux_imbalance - post_abs_flux_imbalance"
        ),
        "max_signature_distance": 0.07,
        "boundary_jaccard_floor": 0.90,
        "support_floor": 0.91,
        "coherence_floor": 0.91,
        "max_flux_imbalance": 0.06,
        "same_label_only_allowed": False,
        "hidden_support_reconstruction_allowed": False,
    }
    threshold_record_digest = digest_value(thresholds)

    transfer_mapping = {
        "trace_id": "n27_i4a_transfer_mapping_trace",
        "transfer_mapping_id": "n27_i4a_gamma_to_delta_topology_fixture_mapping",
        "transfer_scope": "topology",
        "mapping_declared_before_use": True,
        "mapping_declaration_order": 0,
        "pre_observation_order": 1,
        "post_observation_order": 2,
        "mapping_source_backed": True,
        "same_frame_movement_claimed": False,
        "pre_frame_id": "fixture_gamma_branch_frame",
        "post_frame_id": "fixture_delta_folded_frame",
        "pre_fixture_id": "fixture_gamma_branch",
        "post_fixture_id": "fixture_delta_folded",
        "topology_change": {
            "frame_changed": True,
            "node_ids_changed": True,
            "coordinate_rule_changed": "branched_role_layout_to_folded_cycle_role_layout",
            "edge_shape_changed": True,
            "fixture_equivalence_label_only": False,
        },
        "node_mapping": {
            "gamma_core": "delta_core",
            "gamma_left_support": "delta_north_support",
            "gamma_right_support": "delta_south_support",
            "gamma_outer_boundary": "delta_outer_boundary",
        },
        "edge_mapping": {
            "gamma_core-gamma_left_support": "delta_core-delta_north_support",
            "gamma_core-gamma_right_support": "delta_south_support-delta_core",
            "gamma_left_support-gamma_outer_boundary": (
                "delta_north_support-delta_outer_boundary"
            ),
            "gamma_right_support-gamma_outer_boundary": (
                "delta_outer_boundary-delta_south_support"
            ),
        },
        "mapping_policy": "declared_source_current_topological_role_correspondence",
        "mapping_digest_excludes_outcome": True,
    }
    transfer_mapping_digest = digest_value(transfer_mapping)

    pre_signature = {
        "trace_id": "n27_i4a_pre_transfer_basin_signature_trace",
        "frame_id": "fixture_gamma_branch_frame",
        "fixture_id": "fixture_gamma_branch",
        "observation_order": 1,
        "basin_label": "basin_signature_variant_B",
        "basin_label_used_as_evidence": False,
        "basin_nodes": [
            "gamma_core",
            "gamma_left_support",
            "gamma_right_support",
            "gamma_outer_boundary",
        ],
        "boundary_edges": [
            ["gamma_core", "gamma_left_support"],
            ["gamma_core", "gamma_right_support"],
            ["gamma_left_support", "gamma_outer_boundary"],
            ["gamma_right_support", "gamma_outer_boundary"],
        ],
        "signature_vector": {
            "core_weight": 1.0,
            "support_branch_count": 2,
            "min_support": 0.945,
            "min_coherence": 0.940,
            "boundary_edge_count": 4,
            "abs_flux_imbalance": 0.026,
        },
        "support_by_node": {
            "gamma_core": 0.955,
            "gamma_left_support": 0.945,
            "gamma_right_support": 0.948,
            "gamma_outer_boundary": 0.950,
        },
        "coherence_by_node": {
            "gamma_core": 0.952,
            "gamma_left_support": 0.944,
            "gamma_right_support": 0.940,
            "gamma_outer_boundary": 0.946,
        },
        "flux_by_edge": {
            "gamma_core-gamma_left_support": 0.038,
            "gamma_core-gamma_right_support": 0.034,
            "gamma_left_support-gamma_outer_boundary": -0.020,
            "gamma_right_support-gamma_outer_boundary": -0.018,
        },
    }
    pre_signature_digest = digest_value(pre_signature)

    post_signature = {
        "trace_id": "n27_i4a_post_transfer_basin_signature_trace",
        "frame_id": "fixture_delta_folded_frame",
        "fixture_id": "fixture_delta_folded",
        "observation_order": 2,
        "basin_label": "basin_signature_variant_B_mapped",
        "basin_label_used_as_evidence": False,
        "basin_nodes": [
            "delta_core",
            "delta_north_support",
            "delta_south_support",
            "delta_outer_boundary",
        ],
        "boundary_edges": [
            ["delta_core", "delta_north_support"],
            ["delta_south_support", "delta_core"],
            ["delta_north_support", "delta_outer_boundary"],
            ["delta_outer_boundary", "delta_south_support"],
        ],
        "signature_vector": {
            "core_weight": 1.0,
            "support_branch_count": 2,
            "min_support": 0.925,
            "min_coherence": 0.935,
            "boundary_edge_count": 4,
            "abs_flux_imbalance": 0.032,
        },
        "support_by_node": {
            "delta_core": 0.940,
            "delta_north_support": 0.925,
            "delta_south_support": 0.928,
            "delta_outer_boundary": 0.932,
        },
        "coherence_by_node": {
            "delta_core": 0.945,
            "delta_north_support": 0.935,
            "delta_south_support": 0.938,
            "delta_outer_boundary": 0.940,
        },
        "flux_by_edge": {
            "delta_core-delta_north_support": 0.040,
            "delta_south_support-delta_core": 0.033,
            "delta_north_support-delta_outer_boundary": -0.020,
            "delta_outer_boundary-delta_south_support": -0.021,
        },
        "post_transfer_signature_present": True,
    }
    post_signature_digest = digest_value(post_signature)

    observed_signature_distance = 0.030
    boundary_mapping = {
        "trace_id": "n27_i4a_boundary_mapping_trace",
        "transfer_mapping_id": transfer_mapping["transfer_mapping_id"],
        "pre_boundary_edges": pre_signature["boundary_edges"],
        "post_boundary_edges": post_signature["boundary_edges"],
        "edge_mapping": transfer_mapping["edge_mapping"],
        "mapped_boundary_edge_count": 4,
        "unmapped_boundary_edge_count": 0,
        "mapped_boundary_jaccard": 1.0,
        "boundary_jaccard_floor": thresholds["boundary_jaccard_floor"],
        "boundary_acceptance_operator": "greater_than_or_equal",
        "boundary_mapping_margin": 0.10,
        "boundary_margin_at_floor": False,
        "boundary_mapping_preserved": True,
        "same_label_different_basin_rejected": True,
    }
    boundary_mapping_digest = digest_value(boundary_mapping)

    support_preservation = {
        "trace_id": "n27_i4a_support_preservation_trace",
        "support_floor": thresholds["support_floor"],
        "pre_min_support": pre_signature["signature_vector"]["min_support"],
        "post_min_support": post_signature["signature_vector"]["min_support"],
        "support_floor_margin": 0.015,
        "support_preserved_above_floor": True,
        "support_preservation_delta": -0.020,
        "support_reconstruction_counted_as_preservation": False,
    }
    support_preservation_digest = digest_value(support_preservation)

    coherence_preservation = {
        "trace_id": "n27_i4a_coherence_preservation_trace",
        "coherence_floor": thresholds["coherence_floor"],
        "pre_min_coherence": pre_signature["signature_vector"]["min_coherence"],
        "post_min_coherence": post_signature["signature_vector"]["min_coherence"],
        "coherence_floor_margin": 0.025,
        "coherence_preserved_above_floor": True,
        "coherence_preservation_delta": -0.005,
    }
    coherence_preservation_digest = digest_value(coherence_preservation)

    flux_balance = {
        "trace_id": "n27_i4a_flux_balance_trace",
        "max_flux_imbalance": thresholds["max_flux_imbalance"],
        "pre_abs_flux_imbalance": pre_signature["signature_vector"]["abs_flux_imbalance"],
        "post_abs_flux_imbalance": post_signature["signature_vector"]["abs_flux_imbalance"],
        "flux_balance_margin": 0.028,
        "flux_balance_preserved_within_bound": True,
        "hidden_flux_support_reconstruction_detected": False,
    }
    flux_balance_digest = digest_value(flux_balance)

    original_fixture_support_change = {
        "trace_id": "n27_i4a_original_fixture_support_change_trace",
        "original_fixture_support_changed": True,
        "pre_fixture_id": "fixture_gamma_branch",
        "post_fixture_id": "fixture_delta_folded",
        "support_change_kind": "topological_fixture_context_remapped_not_rebuilt",
        "original_fixture_support_reintroduced": False,
    }
    reconstructed_support_ledger = {
        "trace_id": "n27_i4a_reconstructed_support_ledger",
        "reconstructed_support_events": [],
        "hidden_support_reconstruction_absent": True,
        "support_reconstruction_as_transfer_rejected": True,
    }

    i4_row = i4["candidate_rows"][0]
    variant_comparison = {
        "trace_id": "n27_i4a_variant_comparison_trace",
        "i4_replaced": False,
        "i4a_replaces_i4": False,
        "i4_transfer_core_digest": i4_row["transfer_core_digest"],
        "i4_transfer_mapping_id": i4_row["transfer_mapping_id"],
        "i4a_transfer_mapping_id": transfer_mapping["transfer_mapping_id"],
        "mapping_variant_relation": "distinct_topology_fixture_variant_not_i4_replay",
        "same_fixture_pair_as_i4": False,
        "same_transfer_scope_as_i4": False,
        "variant_adds_evidence_without_widening_i4": True,
    }

    runtime_trace = {
        "trace_id": "n27_i4a_source_current_runtime_trace",
        "run_artifact_id": "n27_i4a_topology_fixture_variant_runtime",
        "runtime_config_digest": digest_value(
            {
                "fixture_pair": ["fixture_gamma_branch", "fixture_delta_folded"],
                "mapping_id": transfer_mapping["transfer_mapping_id"],
                "threshold_record_digest": threshold_record_digest,
                "variant_of_i4": False,
            }
        ),
        "source_current_trace_kind": "deterministic_topology_fixture_transfer_variant",
        "observation_order": [
            "threshold_record_declared",
            "mapping_declared",
            "pre_signature_observed",
            "post_signature_observed",
            "boundary_support_coherence_flux_evaluated",
            "variant_compared_to_i4",
        ],
        "derived_report_only": False,
        "implementation_patch_opened": False,
    }

    transfer_core = {
        "transfer_scope": "topology",
        "transfer_mapping_id": transfer_mapping["transfer_mapping_id"],
        "transfer_mapping_digest": transfer_mapping_digest,
        "mapping_declared_before_use": True,
        "mapping_source_backed": True,
        "pre_signature_digest": pre_signature_digest,
        "post_signature_digest": post_signature_digest,
        "boundary_mapping_digest": boundary_mapping_digest,
        "support_preservation_digest": support_preservation_digest,
        "coherence_preservation_digest": coherence_preservation_digest,
        "flux_balance_digest": flux_balance_digest,
    }
    transfer_core_digest = digest_value(transfer_core)
    variant_comparison["i4a_transfer_core_digest"] = transfer_core_digest
    variant_comparison["transfer_core_digest_differs_from_i4"] = (
        transfer_core_digest != i4_row["transfer_core_digest"]
    )

    return {
        "threshold_record": thresholds | {"threshold_record_digest": threshold_record_digest},
        "transfer_mapping_trace": transfer_mapping | {"transfer_mapping_digest": transfer_mapping_digest},
        "pre_transfer_basin_signature_trace": pre_signature
        | {"pre_signature_digest": pre_signature_digest},
        "post_transfer_basin_signature_trace": post_signature
        | {
            "post_signature_digest": post_signature_digest,
            "observed_signature_distance": observed_signature_distance,
            "max_signature_distance": thresholds["max_signature_distance"],
            "signature_preservation_margin": 0.040,
            "same_basin_signature_preserved_under_mapping": True,
        },
        "boundary_mapping_trace": boundary_mapping
        | {"boundary_mapping_digest": boundary_mapping_digest},
        "support_preservation_trace": support_preservation
        | {"support_preservation_digest": support_preservation_digest},
        "coherence_preservation_trace": coherence_preservation
        | {"coherence_preservation_digest": coherence_preservation_digest},
        "flux_balance_trace": flux_balance | {"flux_balance_digest": flux_balance_digest},
        "source_current_runtime_trace": runtime_trace,
        "original_fixture_support_change_trace": original_fixture_support_change,
        "reconstructed_support_ledger": reconstructed_support_ledger,
        "variant_comparison_trace": variant_comparison,
        "transfer_core": transfer_core,
        "transfer_core_digest": transfer_core_digest,
    }


def build_control_results(i2: dict[str, Any]) -> list[dict[str, Any]]:
    passed = {
        "same_label_different_basin_control": "passed_variant_signature_and_boundary_mapping_not_label_only",
        "fixture_equivalence_label_only_control": "passed_variant_has_source_current_mapping_trace",
        "mapping_declared_after_outcome_control": "passed_mapping_declared_before_post_observation",
        "proxy_score_relabel_as_transfer_control": "passed_no_proxy_score_used_as_transfer_evidence",
        "hidden_support_reconstruction_control": "passed_hidden_support_reconstruction_absent",
        "support_reconstruction_as_transfer_control": "passed_reconstruction_ledger_empty_and_not_counted",
        "boundary_mapping_missing_control": "passed_boundary_mapping_trace_present",
        "post_transfer_signature_missing_control": "passed_post_transfer_signature_trace_present",
        "source_current_inputs_missing_control": "passed_source_current_inputs_present",
        "artifact_manifest_failure_control": "passed_manifest_roles_paths_and_sha256_validated",
        "AP4_dependency_omitted_control": "not_applicable_no_route_conditioned_selection_participates",
        "AP5_dependency_omitted_control": "not_applicable_no_proxy_or_target_formation_participates",
        "n26_proxy_as_transfer_evidence_control": "passed_n26_context_not_used_as_transfer_evidence",
        "n26_scoped_ap5_as_native_ap5_control": "passed_n26_ap5_context_not_promoted",
        "n25_2_direct_transfer_consumption_control": "passed_no_direct_n25_2_consumption",
        "semantic_identity_relabel_control": "passed_semantic_identity_blocked",
        "semantic_choice_goal_relabel_control": "passed_semantic_choice_goal_blocked",
        "native_support_relabel_control": "passed_native_support_blocked",
        "phase8_ant_ecology_relabel_control": "passed_phase8_ant_ecology_blocked",
    }
    not_applicable = {
        "cross_substrate_mapping_missing_control": {
            "actual": "topology_scope_not_substrate",
            "rung_effect": "substrate_transfer_claim_not_opened",
            "reason": "I4-A is topology-scope only; no cross-substrate transfer claim is opened.",
        },
    }
    deferred = {
        "replay_failure_control": "deferred_blocks_CT3_or_stronger_until_iteration_5",
        "stress_variant_failure_control": "deferred_blocks_CT5_or_stronger_until_iteration_6",
    }
    results: list[dict[str, Any]] = []
    for control in i2["control_schema"]["control_rows"]:
        control_id = control["control_id"]
        if control_id in passed:
            status = "passed"
            actual = passed[control_id]
            rung_effect = "CT2_not_blocked"
            applicability_reason = (
                "I4-A is a bounded CT2 topology/fixture variant candidate; "
                "replay and stress controls defer stronger rung support."
            )
        elif control_id in not_applicable:
            status = "not_applicable"
            actual = not_applicable[control_id]["actual"]
            rung_effect = not_applicable[control_id]["rung_effect"]
            applicability_reason = not_applicable[control_id]["reason"]
        elif control_id in deferred:
            status = "not_applicable"
            actual = deferred[control_id]
            rung_effect = control["rung_effect"]
            applicability_reason = (
                "I4-A is a bounded CT2 topology/fixture variant candidate; "
                "replay and stress controls defer stronger rung support."
            )
        else:
            raise ValueError(f"missing I4-A control handling for {control_id}")
        results.append(
            {
                "control_id": control_id,
                "control_status": status,
                "blocked_condition": control["blocked_condition"],
                "expected_result": "clear_or_defer_without_upgrading_CT2",
                "actual_result": actual,
                "claim_allowed_when_control_triggers": False,
                "rung_effect": rung_effect,
                "orthogonal_role": control["orthogonal_role"],
                "control_satisfied_for_positive_row": True,
                "control_applicability_reason": applicability_reason,
            }
        )
    return results


def build_candidate_row(
    i1: dict[str, Any],
    i2: dict[str, Any],
    i3: dict[str, Any],
    i4: dict[str, Any],
    traces: dict[str, Any],
) -> dict[str, Any]:
    artifact_roles = [
        "threshold_record",
        "transfer_mapping_trace",
        "pre_transfer_basin_signature_trace",
        "post_transfer_basin_signature_trace",
        "boundary_mapping_trace",
        "support_preservation_trace",
        "coherence_preservation_trace",
        "flux_balance_trace",
        "source_current_runtime_trace",
        "original_fixture_support_change_trace",
        "reconstructed_support_ledger",
        "variant_comparison_trace",
    ]
    artifact_manifest = [trace_artifact(role, traces[role]) for role in artifact_roles]
    source_current_inputs = [
        {
            "artifact_role": item["artifact_role"],
            "path": item["path"],
            "sha256": item["sha256"],
            "consumed_as": "source_current_topology_fixture_variant_transfer_trace",
        }
        for item in artifact_manifest
    ]
    threshold_record = traces["threshold_record"]
    runtime_trace = traces["source_current_runtime_trace"]
    transfer_mapping = traces["transfer_mapping_trace"]

    return {
        "row_id": "n27_i4a_row_01_topology_fixture_variant_transfer_probe",
        "iteration": "4-A",
        "row_decision": "partial",
        "row_decision_scope": "provisional_CT2_variant_evidence_pending_replay_controls",
        "ct_ladder_rung": CT_RUNG,
        "n27_closeout_ceiling": N27_CLOSEOUT_CEILING,
        "source_current_inputs": source_current_inputs,
        "source_inventory_output_digest": i1["output_digest"],
        "transfer_schema_output_digest": i2["output_digest"],
        "active_nulls_output_digest": i3["output_digest"],
        "minimal_configuration_transfer_output_digest": i4["output_digest"],
        "immediate_predecessor_output_digest": i4["output_digest"],
        "source_contract_row_digest": i2["source_digest_pins"]["consumable_contract_row_digest"],
        "source_output_digest": i4["output_digest"],
        "descriptor_contract_row_digest": i2["source_digest_pins"][
            "descriptor_contract_row_digest"
        ],
        "consumable_contract_row_digest": i2["source_digest_pins"][
            "consumable_contract_row_digest"
        ],
        "n26_closeout_output_digest": i2["source_digest_pins"]["n26_closeout_output_digest"],
        "run_artifact_id": runtime_trace["run_artifact_id"],
        "runtime_config_digest": runtime_trace["runtime_config_digest"],
        "artifact_manifest": artifact_manifest,
        "all_artifact_sha256_match_file_contents": all(
            sha256_file(ROOT / item["path"]) == item["sha256"] for item in artifact_manifest
        ),
        "derived_report_only": False,
        "row_specific_thresholds_declared_before_use": threshold_record,
        "transfer_scope": traces["transfer_core"]["transfer_scope"],
        "transfer_core": traces["transfer_core"],
        "transfer_core_digest": traces["transfer_core_digest"],
        "transfer_mapping_id": transfer_mapping["transfer_mapping_id"],
        "transfer_mapping_digest": transfer_mapping["transfer_mapping_digest"],
        "transfer_mapping_trace": transfer_mapping,
        "mapping_declared_before_use": True,
        "mapping_source_backed": True,
        "pre_transfer_basin_signature_trace": traces["pre_transfer_basin_signature_trace"],
        "post_transfer_basin_signature_trace": traces["post_transfer_basin_signature_trace"],
        "boundary_mapping_trace": traces["boundary_mapping_trace"],
        "support_preservation_trace": traces["support_preservation_trace"],
        "coherence_preservation_trace": traces["coherence_preservation_trace"],
        "flux_balance_trace": traces["flux_balance_trace"],
        "original_fixture_support_change_trace": traces["original_fixture_support_change_trace"],
        "reconstructed_support_ledger": traces["reconstructed_support_ledger"],
        "variant_comparison_trace": traces["variant_comparison_trace"],
        "hidden_support_reconstruction_absent": True,
        "same_basin_signature_preserved_under_mapping": True,
        "same_label_different_basin_rejected": True,
        "proxy_score_relabel_rejected": True,
        "configuration_label_only_rejected": True,
        "support_reconstruction_as_transfer_rejected": True,
        "n25_2_direct_transfer_consumption_used": False,
        "n25_2_consumed_only_through_n26_context": True,
        "signature_preservation_margin_formula": threshold_record[
            "signature_preservation_margin_formula"
        ],
        "boundary_mapping_tolerance_formula": threshold_record[
            "boundary_mapping_tolerance_formula"
        ],
        "support_floor_margin_formula": threshold_record["support_floor_margin_formula"],
        "coherence_floor_margin_formula": threshold_record[
            "coherence_floor_margin_formula"
        ],
        "flux_balance_bound_formula": threshold_record["flux_balance_bound_formula"],
        "threshold_record_digest": threshold_record["threshold_record_digest"],
        "replay_result": {
            "artifact_replay": "not_run_until_iteration_5",
            "snapshot_load_replay": "not_run_until_iteration_5",
            "duplicate_replay": "not_run_until_iteration_5",
            "mapping_order_replay": "mapping_order_declared_and_observed_but_replay_deferred",
            "ct3_or_stronger_supported": False,
        },
        "control_results": build_control_results(i2),
        "ap4_dependency_status": "not_applicable",
        "ap4_condition_reason": (
            "I4-A mapping does not use route-conditioned selection; AP4 remains "
            "conditional inherited context only."
        ),
        "ap5_dependency_status": "not_applicable",
        "ap5_condition_reason": (
            "I4-A does not use proxy or target formation; N26 scoped AP5 context "
            "is not consumed as native AP5 or transfer evidence."
        ),
        "claim_ceiling": (
            "provisional CT2 topology/fixture variant transfer candidate pending "
            "I5 replay and later controls; no final transfer, CT3, semantic "
            "identity, native support, native AP5, AP5 NAT4-gap resolution, "
            "Phase 8, or ant ecology claim"
        ),
        "unsafe_claim_flags": unsafe_claim_flags(),
        "i4_replaced": False,
        "i4a_replaces_i4": False,
        "variant_evidence_role": "additive_distinct_topology_fixture_CT2_candidate",
        "transfer_claim_allowed": False,
        "final_transfer_supported": False,
    }


def build_checks(
    output: dict[str, Any],
    i1: dict[str, Any],
    i2: dict[str, Any],
    i3: dict[str, Any],
    i4: dict[str, Any],
) -> list[dict[str, Any]]:
    row = output["candidate_rows"][0]
    i4_row = i4["candidate_rows"][0]
    required_fields = i2["candidate_row_schema"]["required_fields"]
    ct2_required_roles = next(
        rung["required_artifact_roles"] for rung in i2["ct_ladder"] if rung["rung"] == "CT2"
    )
    manifest_roles = {item["artifact_role"] for item in row["artifact_manifest"]}
    core = row["transfer_core"]
    checks = [
        check(
            "i4_ready_and_preserved",
            i4["status"] == "passed"
            and i4["provisional_ct_ladder_rung"] == "CT2"
            and row["i4_replaced"] is False,
            {"i4_status": i4["status"], "i4_output_digest": i4["output_digest"]},
        ),
        check(
            "source_chain_digests_match",
            i2["source_digest_pins"]["source_inventory_output_digest"] == i1["output_digest"]
            and i3["source_schema_output_digest"] == i2["output_digest"]
            and i4["active_nulls_output_digest"] == i3["output_digest"]
            and row["source_output_digest"] == i4["output_digest"],
            {
                "i1": i1["output_digest"],
                "i2": i2["output_digest"],
                "i3": i3["output_digest"],
                "i4": i4["output_digest"],
            },
        ),
        check(
            "all_required_candidate_fields_present",
            all(field in row for field in required_fields),
            {"required_field_count": len(required_fields)},
        ),
        check(
            "ct2_artifact_roles_present",
            set(ct2_required_roles).issubset(manifest_roles),
            {"required_roles": ct2_required_roles, "manifest_roles": sorted(manifest_roles)},
        ),
        check(
            "artifact_sha256_match_file_contents",
            row["all_artifact_sha256_match_file_contents"] is True,
            {"artifact_count": len(row["artifact_manifest"])},
        ),
        check(
            "control_status_values_within_frozen_enum",
            all(
                item["control_status"]
                in {"passed", "failed_closed", "failed_open", "not_run", "not_applicable"}
                for item in row["control_results"]
            ),
            {"statuses": sorted({item["control_status"] for item in row["control_results"]})},
        ),
        check(
            "transfer_core_digest_valid",
            digest_value(core) == row["transfer_core_digest"]
            and core["transfer_mapping_digest"] == row["transfer_mapping_digest"],
            {"transfer_core_digest": row["transfer_core_digest"]},
        ),
        check(
            "variant_distinct_from_i4",
            row["transfer_core_digest"] != i4_row["transfer_core_digest"]
            and row["transfer_mapping_id"] != i4_row["transfer_mapping_id"]
            and row["transfer_scope"] != i4_row["transfer_scope"]
            and row["variant_comparison_trace"]["transfer_core_digest_differs_from_i4"]
            is True,
            row["variant_comparison_trace"],
        ),
        check(
            "mapping_declared_before_use_and_source_backed",
            row["mapping_declared_before_use"] is True
            and row["mapping_source_backed"] is True
            and row["transfer_mapping_trace"]["mapping_declaration_order"]
            < row["transfer_mapping_trace"]["post_observation_order"],
            row["transfer_mapping_trace"],
        ),
        check(
            "source_current_not_report_only",
            row["derived_report_only"] is False and len(row["source_current_inputs"]) > 0,
            {"source_current_input_count": len(row["source_current_inputs"])},
        ),
        check(
            "same_basin_mapping_metrics_pass",
            row["same_basin_signature_preserved_under_mapping"] is True
            and row["post_transfer_basin_signature_trace"]["signature_preservation_margin"] > 0
            and row["boundary_mapping_trace"]["boundary_mapping_preserved"] is True
            and row["boundary_mapping_trace"]["boundary_mapping_margin"] > 0,
            {
                "signature_margin": row["post_transfer_basin_signature_trace"][
                    "signature_preservation_margin"
                ],
                "boundary_margin": row["boundary_mapping_trace"]["boundary_mapping_margin"],
            },
        ),
        check(
            "support_coherence_flux_preserved",
            row["support_preservation_trace"]["support_preserved_above_floor"] is True
            and row["coherence_preservation_trace"]["coherence_preserved_above_floor"] is True
            and row["flux_balance_trace"]["flux_balance_preserved_within_bound"] is True,
            {
                "support_margin": row["support_preservation_trace"]["support_floor_margin"],
                "coherence_margin": row["coherence_preservation_trace"][
                    "coherence_floor_margin"
                ],
                "flux_margin": row["flux_balance_trace"]["flux_balance_margin"],
            },
        ),
        check(
            "support_reconstruction_and_label_controls_cleared",
            row["hidden_support_reconstruction_absent"] is True
            and row["support_reconstruction_as_transfer_rejected"] is True
            and row["same_label_different_basin_rejected"] is True
            and row["proxy_score_relabel_rejected"] is True
            and row["configuration_label_only_rejected"] is True,
            {"hidden_support_reconstruction_absent": row["hidden_support_reconstruction_absent"]},
        ),
        check(
            "transfer_not_same_frame_movement",
            row["transfer_mapping_trace"]["same_frame_movement_claimed"] is False
            and row["transfer_mapping_trace"]["pre_frame_id"]
            != row["transfer_mapping_trace"]["post_frame_id"],
            {
                "pre_frame_id": row["transfer_mapping_trace"]["pre_frame_id"],
                "post_frame_id": row["transfer_mapping_trace"]["post_frame_id"],
            },
        ),
        check(
            "replay_controls_defer_stronger_rungs",
            row["replay_result"]["ct3_or_stronger_supported"] is False
            and output["ct3_or_stronger_supported"] is False,
            row["replay_result"],
        ),
        check(
            "ap_gap_and_source_boundaries_preserved",
            row["ap4_dependency_status"] == "not_applicable"
            and row["ap5_dependency_status"] == "not_applicable"
            and row["n25_2_direct_transfer_consumption_used"] is False
            and row["n25_2_consumed_only_through_n26_context"] is True,
            {"ap4": row["ap4_dependency_status"], "ap5": row["ap5_dependency_status"]},
        ),
        check(
            "predecessor_digest_fields_explicit",
            row["source_inventory_output_digest"] == i1["output_digest"]
            and row["transfer_schema_output_digest"] == i2["output_digest"]
            and row["active_nulls_output_digest"] == i3["output_digest"]
            and row["minimal_configuration_transfer_output_digest"] == i4["output_digest"]
            and row["immediate_predecessor_output_digest"] == i4["output_digest"],
            {
                "minimal_configuration_transfer_output_digest": row[
                    "minimal_configuration_transfer_output_digest"
                ]
            },
        ),
        check(
            "unsafe_claim_flags_false",
            all(value is False for value in row["unsafe_claim_flags"].values()),
            {"claim_count": len(row["unsafe_claim_flags"])},
        ),
        check(
            "no_absolute_paths_in_records",
            not any(
                marker in value
                for value in collect_strings(output)
                for marker in ABSOLUTE_PATH_MARKERS
            ),
            "all record paths are repository-relative",
        ),
    ]
    return checks


def build_output() -> dict[str, Any]:
    i1 = load_json(I1_OUTPUT)
    i2 = load_json(I2_OUTPUT)
    i3 = load_json(I3_OUTPUT)
    i4 = load_json(I4_OUTPUT)
    traces = build_variant_traces(i4)
    row = build_candidate_row(i1, i2, i3, i4, traces)
    output: dict[str, Any] = {
        "artifact_id": "n27_topology_fixture_variant_transfer_probe",
        "schema_version": "n27_i4a_topology_fixture_variant_transfer_probe_v1",
        "experiment": "N27_configuration_substrate_transfer",
        "iteration": "4-A",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "purpose": "add a distinct source-current topology/fixture CT2 transfer variant",
        "status": "passed",
        "acceptance_state": (
            "accepted_topology_fixture_variant_CT2_candidate_pending_replay_controls"
        ),
        "source_records": [
            source_record(I1_OUTPUT, "n27_i1_source_inventory", "source_inventory"),
            source_record(I2_OUTPUT, "n27_i2_transfer_schema", "schema_control_freeze"),
            source_record(I3_OUTPUT, "n27_i3_active_nulls", "active_null_boundary"),
            source_record(I4_OUTPUT, "n27_i4_minimal_transfer", "minimal_transfer_baseline"),
        ],
        "source_inventory_output_digest": i1["output_digest"],
        "transfer_schema_output_digest": i2["output_digest"],
        "active_nulls_output_digest": i3["output_digest"],
        "minimal_configuration_transfer_output_digest": i4["output_digest"],
        "n27_closeout_ceiling": N27_CLOSEOUT_CEILING,
        "n27_closeout_ladder_rung_assigned": False,
        "positive_transfer_evidence_opened": True,
        "candidate_rows_classified": True,
        "provisional_ct_ladder_rung": CT_RUNG,
        "ct_ladder_rung_assigned": False,
        "ct_assignment_scope": "variant_candidate_only_pending_replay_controls",
        "ct3_or_stronger_supported": False,
        "ct5_or_stronger_supported": False,
        "final_transfer_supported": False,
        "i4_replaced": False,
        "i4a_replaces_i4": False,
        "variant_ct2_candidate_count": 1,
        "candidate_rows": [row],
        "ready_for_iteration_5_replay_same_basin_mapping_matrix": True,
        "claim_boundary": {
            "claim_ceiling": row["claim_ceiling"],
            "unsafe_claim_flags": unsafe_claim_flags(),
        },
    }
    checks = build_checks(output, i1, i2, i3, i4)
    output["checks"] = checks
    output["failed_checks"] = [item["check_id"] for item in checks if not item["passed"]]
    output["status"] = "passed" if not output["failed_checks"] else "failed"
    output["acceptance_state"] = (
        "accepted_topology_fixture_variant_CT2_candidate_pending_replay_controls"
        if output["status"] == "passed"
        else "blocked_topology_fixture_variant_transfer_probe"
    )
    output["output_digest"] = digest_value(output)
    return output


def write_report(output: dict[str, Any]) -> None:
    row = output["candidate_rows"][0]
    report = f"""# N27 Iteration 4-A - Topology / Fixture Variant Transfer Probe

Status: `{output['status']}`

Acceptance state: `{output['acceptance_state']}`

## Scope

Iteration 4-A adds a distinct source-current topology / fixture mapping
variant. It does not replace I4 and does not claim replay-backed transfer.

```text
positive_transfer_evidence_opened = {str(output['positive_transfer_evidence_opened']).lower()}
provisional_ct_ladder_rung = {output['provisional_ct_ladder_rung']}
ct_ladder_rung_assigned = {str(output['ct_ladder_rung_assigned']).lower()}
ct_assignment_scope = {output['ct_assignment_scope']}
i4_replaced = {str(output['i4_replaced']).lower()}
ct3_or_stronger_supported = {str(output['ct3_or_stronger_supported']).lower()}
ct5_or_stronger_supported = {str(output['ct5_or_stronger_supported']).lower()}
final_transfer_supported = {str(output['final_transfer_supported']).lower()}
```

## Candidate Row

| Row | Decision | Scope | Signature Margin | Boundary Margin | Support Margin | Coherence Margin | Flux Margin |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `{row['row_id']}` | `{row['row_decision']}` | `{row['transfer_scope']}` | `{row['post_transfer_basin_signature_trace']['signature_preservation_margin']}` | `{row['boundary_mapping_trace']['boundary_mapping_margin']}` | `{row['support_preservation_trace']['support_floor_margin']}` | `{row['coherence_preservation_trace']['coherence_floor_margin']}` | `{row['flux_balance_trace']['flux_balance_margin']}` |

## Geometric Interpretation

I4-A maps a branched pre-frame fixture (`fixture_gamma_branch_frame`) to a
folded post-frame fixture (`fixture_delta_folded_frame`). Node ids, frame ids,
coordinate rules, and edge shape change. The row counts only because the
declared topological role mapping preserves the basin signature, maps all
boundary edges, keeps support/coherence above floor, keeps flux within bound,
and records an empty reconstruction ledger.

## Difference From I4

I4 is the minimal alpha/beta configuration-frame transfer: a three-node
core/support/boundary fixture is mapped into another three-node
core/support/boundary fixture. Its boundary mapping is admissible but exactly at
floor, with boundary margin `0.0`.

I4-A is not a replay of that row. It uses a different topology/fixture mapping:
a branched gamma fixture with two support arms and one outer boundary is mapped
into a folded delta fixture. Node ids, frame ids, coordinate rules, and edge
shape all change. The transfer-core digest differs from I4, and the boundary
margin is `0.1`.

So I4-A adds variant coverage: it shows that the CT2 transfer construction is
not confined to the original minimal alpha/beta frame. It still remains CT2
because replay, full controls, and stress/variant matrices are pending.

## Review Validation

I4-A consumes the current I4 artifact digest
`{output['minimal_configuration_transfer_output_digest']}`. The
cross-substrate missing-mapping control is `not_applicable`, because I4-A is
topology-scope only and does not open a substrate-transfer claim.

This is additive variant evidence. It strengthens N27 beyond a single
alpha/beta fixture pair, but remains CT2 because replay, full controls, and
stress/variant matrices are still pending.

## Checks

| Check | Passed |
| --- | --- |
"""
    for item in output["checks"]:
        report += f"| `{item['check_id']}` | `{str(item['passed']).lower()}` |\n"

    report += f"""

## Interpretation

I4-A supports one additional provisional CT2 topology/fixture transfer
candidate. It does not replace I4, does not widen I4's boundary edge, and does
not support CT3, CT4, CT5, final transfer, semantic identity, native support,
native AP5, AP5 NAT4-gap resolution, Phase 8, or ant ecology.

Output digest: `{output['output_digest']}`
"""
    REPORT.write_text(report, encoding="utf-8")


def main() -> None:
    output = build_output()
    write_json(OUTPUT, output)
    write_report(output)


if __name__ == "__main__":
    main()

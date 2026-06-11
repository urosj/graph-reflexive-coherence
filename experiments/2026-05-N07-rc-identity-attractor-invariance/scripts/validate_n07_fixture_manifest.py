"""Build and validate the N07 Iteration 2 fixture manifest.

This script is experiment-local. It freezes topology families, support-area
schema, discrete RC observable mappings, gate vectors, and controls before any
identity probe runs. It does not import or mutate `src/pygrc`.
"""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[3]
N07 = ROOT / "experiments/2026-05-N07-rc-identity-attractor-invariance"
BASELINE_PATH = N07 / "outputs/n07_iteration_1_baseline_theory_schema_inventory.json"
MANIFEST_PATH = N07 / "configs/n07_fixture_manifest_v1.json"
OUTPUT_PATH = N07 / "outputs/n07_iteration_2_fixture_manifest_validation.json"
REPORT_PATH = N07 / "reports/n07_iteration_2_fixture_manifest_validation.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N07-rc-identity-attractor-invariance/scripts/"
    "validate_n07_fixture_manifest.py"
)


TOPOLOGY_FAMILY_IDS = {
    "n07_T1_support_area_minimal",
    "n07_T2_stable_well_basin",
    "n07_T3_attractor_neighborhood",
    "n07_T5_lineage_current_invariance",
    "n07_T6_reflexive_closure",
}

COMPOSITE_TOPOLOGY_IDS = {
    "n07_C1_recurrent_single_basin_identity_candidate",
    "n07_C2_lineage_current_topology_mutating_identity_candidate",
    "n07_C3_competing_basin_compatibility_candidate",
    "n07_C4_route_fed_route_independent_identity_candidate",
    "n07_C5_movement_carried_movement_independent_identity_candidate",
    "n07_C6_parent_child_refinement_identity_boundary_candidate",
}

GATE_VECTOR_FIELDS = {
    "support",
    "stability",
    "attractivity",
    "invariance",
    "lineage_current",
    "reflexive_closure",
    "compatibility",
    "artifact_replay",
}

GATE_VECTOR_VALUES = {"pass", "fail", "blocked", "not_measured", "not_applicable"}

CLAIM_FLAGS_FALSE = {
    "semantic_choice_claim_allowed",
    "agency_claim_allowed",
    "agentic_like_claim_allowed",
    "intention_claim_allowed",
    "memory_or_trail_claim_allowed",
    "goal_proxy_regulation_claim_allowed",
    "movement_claim_allowed",
    "locomotion_like_claim_allowed",
    "biological_claim_allowed",
    "ant_colony_claim_allowed",
    "identity_acceptance_claim_allowed",
    "rc_identity_collapse_claim_allowed",
    "personhood_claim_allowed",
    "unrestricted_identity_claim_allowed",
    "unrestricted_movement_claim_allowed",
}


def _rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def _canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _digest(data: Any) -> str:
    return hashlib.sha256(_canonical_json(data).encode("utf-8")).hexdigest()


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return data


def _git(args: list[str]) -> dict[str, Any]:
    proc = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )
    return {
        "command": "git " + " ".join(args),
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
    }


def _claim_flags() -> dict[str, bool]:
    return {key: False for key in sorted(CLAIM_FLAGS_FALSE)}


def _gate_vector(**overrides: str) -> dict[str, str]:
    vector = {key: "not_measured" for key in sorted(GATE_VECTOR_FIELDS)}
    vector.update(overrides)
    return vector


def _support_area_digest_input() -> dict[str, Any]:
    return {
        "support_area_id": "n07_support_area_A_v1",
        "candidate_identity_carrier_type": "coherence_basin",
        "support_node_ids": [2],
        "support_edge_ids": [1, 2, 3, 5],
        "support_port_ids": [
            "support_front",
            "support_rear",
            "support_reentry",
        ],
        "lineage_status": "fixed_topology",
        "lineage_map_digest": None,
        "support_surface_digest": "manifest_symbolic_support_surface_digest_pending_iteration_3",
        "event_time_key": "manifest_declared_no_runtime_event",
        "scheduler_event_index": None,
        "budget_surface": "node_plus_packet",
        "budget_before": 6.0,
        "budget_after": 6.0,
        "budget_error": 0.0,
    }


def _support_area() -> dict[str, Any]:
    digest_input = _support_area_digest_input()
    return {
        **digest_input,
        "support_area_digest": _digest(digest_input),
        "idempotency_key_fields": [
            "support_area_id",
            "support_area_digest",
            "event_time_key",
            "scheduler_event_index",
            "lineage_status",
        ],
        "duplicate_support_row_primary_blocker": "duplicate_support_row",
        "identity_label_is_evidence": False,
        "authored_central_node_is_identity_evidence": False,
    }


def _fixture() -> dict[str, Any]:
    return {
        "fixture_id": "N07_S0_identity_support_chain_v1",
        "fixture_kind": "identity_support_chain_with_reentry_and_competitor",
        "node_count": 6,
        "edge_count": 6,
        "candidate_identity_carrier_type": "coherence_basin",
        "candidate_runtime_coherence_basin": {
            "basin_id": "n07_basin_A_candidate_v1",
            "support_area_id": "n07_support_area_A_v1",
            "carrier_surface": "runtime_coherence_basin",
            "identity_label_is_evidence": False,
        },
        "nodes": [
            {"node_id": 0, "role": "flux_source", "coord": [0.0, 0.0]},
            {"node_id": 1, "role": "ingress_neighbor", "coord": [1.0, 0.0]},
            {"node_id": 2, "role": "candidate_support_core", "coord": [2.0, 0.0]},
            {"node_id": 3, "role": "egress_neighbor", "coord": [3.0, 0.0]},
            {"node_id": 4, "role": "reentry_neighbor", "coord": [2.0, 1.0]},
            {"node_id": 5, "role": "competitor_neighbor", "coord": [2.0, -1.0]},
        ],
        "edges": [
            {"edge_id": 0, "u": 0, "v": 1, "role": "source_to_ingress"},
            {"edge_id": 1, "u": 1, "v": 2, "role": "ingress_to_support"},
            {"edge_id": 2, "u": 2, "v": 3, "role": "support_to_egress"},
            {"edge_id": 3, "u": 4, "v": 2, "role": "reentry_to_support"},
            {"edge_id": 4, "u": 5, "v": 2, "role": "competitor_to_support"},
            {"edge_id": 5, "u": 2, "v": 4, "role": "support_to_reentry"},
        ],
        "ports": [
            {"port_id": "support_front", "node_id": 2, "edge_id": 1},
            {"port_id": "support_rear", "node_id": 2, "edge_id": 2},
            {"port_id": "support_reentry", "node_id": 2, "edge_id": 3},
            {"port_id": "support_competitor", "node_id": 2, "edge_id": 4},
        ],
        "neighborhood_U": {
            "neighborhood_id": "n07_U_support_A_v1",
            "node_ids": [0, 1, 3, 4],
            "excluded_wrong_basin_node_ids": [5],
            "flux_source_node_ids": [0, 4],
            "target_support_area_id": "n07_support_area_A_v1",
        },
        "budget_surface": {
            "budget_surface_id": "n07_node_plus_packet_budget_v1",
            "budget_surface": "node_plus_packet",
            "conserved_budget_total": 6.0,
            "budget_tolerance": 0.0,
            "budget_ambiguity_allowed": False,
        },
    }


def _metric_definitions() -> dict[str, Any]:
    return {
        "support_area_digest": {
            "method": "sha256_canonical_json_sorted_keys",
            "excludes_fields": ["support_area_digest"],
            "required_input_fields": list(_support_area_digest_input()),
        },
        "stability_well_proxy": {
            "native_policy_available": False,
            "selected_proxy": "experiment_local_declared_second_difference_retention_proxy",
            "proxy_formula": (
                "0.5 * support_area_mass_retention + 0.5 * "
                "local_inflow_dominance_score"
            ),
            "threshold": 0.75,
            "input_fields": [
                "support_area_mass_before",
                "support_area_mass_after",
                "incoming_flux_to_support",
                "outgoing_flux_from_support",
            ],
            "digest_scope": [
                "proxy_formula",
                "threshold",
                "input_fields",
                "support_area_digest",
            ],
            "native_policy_blocker": "native_basin_potential_policy_missing",
            "hidden_report_side_score_allowed": False,
        },
        "flux_convergence": {
            "metric_id": "n07_flux_convergence_to_support_v1",
            "formula": "net_flux_into_support_from_U > net_flux_out_of_support",
            "positive_threshold": 0.0,
            "native_policy_available": False,
            "native_policy_blocker": "native_attractor_neighborhood_policy_missing",
            "runtime_visible_inputs": [
                "neighborhood_U",
                "packet_work_events",
                "surface_rows",
                "budget_surface",
            ],
            "controls": ["non_attractive_flux", "wrong_polarity", "subthreshold_flux", "wrong_basin"],
        },
        "invariance": {
            "metric_id": "n07_invariance_support_overlap_lineage_v1",
            "overlap_computation_method": "lineage_weighted_jaccard_over_declared_lineage_transfer_map",
            "support_overlap_kind": "lineage_weighted",
            "lineage_current_overlap_method": (
                "fraction_of_lineage_mapped_support_nodes_retaining_current_support_membership"
            ),
            "literal_node_set_overlap_serialized": True,
            "support_overlap_threshold": 0.95,
            "lineage_current_overlap_threshold": 0.95,
            "proper_time_persistence_threshold": 3,
            "perturbation_magnitude": 0.1,
            "perturbation_window": "one_proper_time_window",
            "destructive_perturbation_blocker": "support_drift_beyond_threshold",
            "missing_threshold_blocker": "identity_threshold_missing",
            "native_policy_available": False,
            "native_policy_blocker": "native_identity_invariance_policy_missing",
            "runtime_visible_inputs": [
                "proper_time_cycle_events",
                "support_area_digest",
                "transported_support_area_digest",
                "topology_event_digest",
                "surface_lineage_record_digest",
                "topology_state_reabsorption_record_digest",
                "node_plus_packet_budget_surface",
            ],
            "controls": [
                "stale_node_id_replay",
                "missing_topology_state_reabsorption",
                "lineage_map_scrambled",
                "support_drift_beyond_threshold",
                "budget_discontinuity",
                "identity_claim_promotion",
            ],
            "proper_time_only": True,
        },
        "reflexive_closure": {
            "metric_id": "n07_reflexive_closure_reentry_v1",
            "basin_evidence_bundle": [
                "support_area_mass",
                "retention_score",
                "proper_time_persistence_score",
                "basin_evidence_digest",
            ],
            "proper_time_persistence_threshold": 3,
            "native_policy_available": False,
            "native_policy_blocker": "native_reflexive_closure_policy_missing",
            "identity_acceptance_contract_available": False,
            "identity_acceptance_blocker": "unauthorized_identity_acceptance_event",
            "runtime_visible_inputs": [
                "reentry_packet_event",
                "producer_record",
                "processed_packet_event",
                "basin_evidence_before_reentry",
                "basin_evidence_after_reentry",
                "later_cycle_consumed_basin_evidence_digest",
                "proper_time_identity_persistence_evaluation",
                "node_plus_packet_budget_surface",
            ],
            "controls": [
                "no_reentry",
                "closure_not_consumed_by_later_cycle",
                "improper_proper_time_threshold",
                "failed_persistence",
                "unauthorized_identity_acceptance_event",
                "producer_mutation_boundary_violation",
                "agency_claim_promotion",
            ],
            "conditions": [
                "reentry_coherence_into_support > 0",
                "basin_evidence_after_reentry >= basin_evidence_before_reentry",
                "later_cycle_consumed_updated_basin_evidence = true",
                "budget_error == 0",
            ],
            "stale_digest_blocker": "closure_not_consumed_by_later_cycle",
        },
        "coherence_compatibility": {
            "metric_id": "n07_coherence_compatibility_v1",
            "conditions": [
                "budget_error == 0",
                "min_active_node_coherence >= 0",
                "candidate_support_overlap_with_competitor <= declared_overlap_threshold",
                "lineage_conflict_detected = false",
                "hidden_support_source_detected = false",
                "destructive_interference_score <= declared_interference_threshold",
            ],
            "compatibility_controls_deferred_until": "T7_or_C3",
        },
    }


def _topology_families(claim_flags: Mapping[str, bool]) -> list[dict[str, Any]]:
    common = {
        "candidate_identity_carrier_type": "coherence_basin",
        "identity_carrier_surface": "runtime_coherence_basin",
        "support_area_id": "n07_support_area_A_v1",
        "budget_surface": "node_plus_packet",
        "claim_flags": dict(claim_flags),
        "probe_run": False,
        "identity_evidence_emitted": False,
    }
    return [
        {
            **common,
            "topology_family_id": "n07_T1_support_area_minimal",
            "target_id_level": "ID1",
            "gate_under_test": "support",
            "primary_positive_metric": "support_area_digest",
            "paired_negative_control_topology": "label_only_null_topology",
            "expected_primary_blocker": "missing_support_area",
            "expected_maximum_id_ceiling": "ID1",
            "topology_mutation_occurs": False,
            "lineage_current_support_required": False,
            "candidate_runtime_coherence_basin": "n07_basin_A_candidate_v1",
            "neighborhood_U": "n07_U_support_A_v1",
        },
        {
            **common,
            "topology_family_id": "n07_T2_stable_well_basin",
            "target_id_level": "ID2",
            "gate_under_test": "stability",
            "primary_positive_metric": "stability_well_proxy",
            "paired_negative_control_topology": "unstable_basin_no_local_well",
            "expected_primary_blocker": "unstable_basin_no_local_well",
            "expected_maximum_id_ceiling": "ID2",
            "topology_mutation_occurs": False,
            "lineage_current_support_required": False,
            "candidate_runtime_coherence_basin": "n07_basin_A_candidate_v1",
            "neighborhood_U": "n07_U_support_A_v1",
        },
        {
            **common,
            "topology_family_id": "n07_T3_attractor_neighborhood",
            "target_id_level": "ID3",
            "gate_under_test": "attractivity",
            "primary_positive_metric": "flux_convergence",
            "paired_negative_control_topology": "non_attractive_flux",
            "expected_primary_blocker": "non_attractive_flux",
            "expected_maximum_id_ceiling": "ID3",
            "topology_mutation_occurs": False,
            "lineage_current_support_required": False,
            "candidate_runtime_coherence_basin": "n07_basin_A_candidate_v1",
            "neighborhood_U": "n07_U_support_A_v1",
        },
        {
            **common,
            "topology_family_id": "n07_T5_lineage_current_invariance",
            "target_id_level": "ID4",
            "gate_under_test": "lineage_current",
            "primary_positive_metric": "invariance",
            "paired_negative_control_topology": "stale_node_id_replay",
            "expected_primary_blocker": "stale_node_id_replay",
            "expected_maximum_id_ceiling": "ID4",
            "topology_mutation_occurs": True,
            "lineage_current_support_required": True,
            "candidate_runtime_coherence_basin": "n07_basin_A_candidate_v1",
            "neighborhood_U": "n07_U_support_A_v1",
        },
        {
            **common,
            "topology_family_id": "n07_T6_reflexive_closure",
            "target_id_level": "ID5",
            "gate_under_test": "reflexive_closure",
            "primary_positive_metric": "reflexive_closure",
            "paired_negative_control_topology": "no_reentry",
            "expected_primary_blocker": "no_reentry",
            "expected_maximum_id_ceiling": "ID5",
            "topology_mutation_occurs": False,
            "lineage_current_support_required": False,
            "candidate_runtime_coherence_basin": "n07_basin_A_candidate_v1",
            "neighborhood_U": "n07_U_support_A_v1",
        },
    ]


def _composite_topologies(claim_flags: Mapping[str, bool]) -> list[dict[str, Any]]:
    base = {
        "identity_carrier_surface": "runtime_coherence_basin",
        "gate_vector": _gate_vector(),
        "derived_id_ceiling": "ID0",
        "primary_blocker": "not_run_iteration_2_manifest_only",
        "claim_flags": dict(claim_flags),
    }
    return [
        {
            **base,
            "composite_topology_id": "n07_C1_recurrent_single_basin_identity_candidate",
            "primitive_blocks_combined": [
                "n07_T1_support_area_minimal",
                "n07_T2_stable_well_basin",
                "n07_T3_attractor_neighborhood",
                "n07_T6_reflexive_closure",
            ],
            "expected_id_ceiling": "ID5_after_reflexive_closure_probe",
            "informative_lower_ceilings": ["ID1", "ID2", "ID3", "ID4"],
            "false_positive_confusion_under_test": "cycle_persistence_misread_as_reflexive_self_maintenance",
            "imported_prior_experiment_surfaces": [],
            "imported_surfaces_evidence_only": True,
        },
        {
            **base,
            "composite_topology_id": "n07_C2_lineage_current_topology_mutating_identity_candidate",
            "primitive_blocks_combined": [
                "n07_T1_support_area_minimal",
                "n07_T5_lineage_current_invariance",
            ],
            "expected_id_ceiling": "ID4_until_reflexive_closure_passes",
            "informative_lower_ceilings": ["ID1", "ID3"],
            "false_positive_confusion_under_test": "stale_node_label_continuity_misread_as_identity",
            "imported_prior_experiment_surfaces": ["N04_22B_boundary_evidence"],
            "imported_surfaces_evidence_only": True,
        },
        {
            **base,
            "composite_topology_id": "n07_C3_competing_basin_compatibility_candidate",
            "primitive_blocks_combined": [
                "n07_T2_stable_well_basin",
                "n07_T3_attractor_neighborhood",
            ],
            "expected_id_ceiling": "ID5_or_ID6_only_after_T7_compatibility_and_replay",
            "informative_lower_ceilings": ["ID2", "ID3"],
            "false_positive_confusion_under_test": "basin_overlap_misread_as_compatibility",
            "imported_prior_experiment_surfaces": [],
            "imported_surfaces_evidence_only": True,
        },
        {
            **base,
            "composite_topology_id": "n07_C4_route_fed_route_independent_identity_candidate",
            "primitive_blocks_combined": [
                "n07_T1_support_area_minimal",
                "n07_T3_attractor_neighborhood",
            ],
            "expected_id_ceiling": "ID3_until_identity_gates_pass_independently",
            "informative_lower_ceilings": ["ID1", "ID2"],
            "false_positive_confusion_under_test": "route_choice_misread_as_identity",
            "imported_prior_experiment_surfaces": ["N06_route_choice_context"],
            "imported_surfaces_evidence_only": True,
        },
        {
            **base,
            "composite_topology_id": "n07_C5_movement_carried_movement_independent_identity_candidate",
            "primitive_blocks_combined": [
                "n07_T1_support_area_minimal",
                "n07_T5_lineage_current_invariance",
            ],
            "expected_id_ceiling": "ID4_until_movement_independence_passes",
            "informative_lower_ceilings": ["ID1", "ID3"],
            "false_positive_confusion_under_test": "movement_trace_misread_as_identity_acceptance",
            "imported_prior_experiment_surfaces": ["N04_topology_mutating_movement_candidate"],
            "imported_surfaces_evidence_only": True,
        },
        {
            **base,
            "composite_topology_id": "n07_C6_parent_child_refinement_identity_boundary_candidate",
            "primitive_blocks_combined": [
                "n07_T1_support_area_minimal",
                "n07_T5_lineage_current_invariance",
            ],
            "expected_id_ceiling": "ID4_until_parent_child_compatibility_passes",
            "informative_lower_ceilings": ["ID1", "ID2", "ID3"],
            "false_positive_confusion_under_test": "mechanical_refinement_misread_as_identity_fission",
            "imported_prior_experiment_surfaces": ["GRC9V3_refinement_boundary"],
            "imported_surfaces_evidence_only": True,
        },
    ]


def _controls(canonical_controls: list[str]) -> list[dict[str, Any]]:
    return [
        {
            "control_id": control_id,
            "primary_blocker": control_id,
            "distinct_primary_blocker": True,
            "declared_before_probe": True,
        }
        for control_id in canonical_controls
    ]


def build_manifest(baseline: Mapping[str, Any]) -> dict[str, Any]:
    claim_flags = _claim_flags()
    canonical_controls = list(baseline["canonical_controls"])
    return {
        "schema": "n07_identity_fixture_manifest_v1",
        "experiment": "2026-05-N07-rc-identity-attractor-invariance",
        "manifest_id": "n07_fixture_manifest_v1",
        "purpose": "declare_identity_fixture_manifest_and_discrete_rc_observable_mapping_before_identity_probes",
        "identity_probe_run": False,
        "positive_identity_evidence_generated": False,
        "support_rows_emitted": False,
        "runtime_family": "LGRC9V3",
        "implementation_scope": "experiment_local_manifest_only",
        "source_baseline": {
            "path": _rel(BASELINE_PATH),
            "sha256": _file_sha256(BASELINE_PATH),
            "schema": baseline["schema"],
        },
        "topology_design_policy": {
            "topology_is_experimental_object": True,
            "each_positive_topology_isolates_one_identity_gate": True,
            "each_negative_topology_breaks_one_declared_property": True,
            "rich_omnibus_fixtures_disallowed_first_pass": True,
            "primitive_fixtures_prove_gate_legibility": True,
            "composite_fixtures_prove_taxonomy_usefulness": True,
            "hidden_identity_labels_as_evidence_allowed": False,
            "authored_central_node_identity_evidence_allowed": False,
        },
        "fixture": _fixture(),
        "support_area": _support_area(),
        "metric_definitions": _metric_definitions(),
        "topology_families": _topology_families(claim_flags),
        "t4_deferral": {
            "topology_family": "T4_no_mutation_invariance",
            "deferred": True,
            "rationale": (
                "T4 is the recurrence/no-mutation baseline and must be run "
                "before interpreting topology-free recurrence as stronger than ID4."
            ),
            "not_omitted_from_ladder": True,
        },
        "composite_topology_policy": {
            "composites_derive_id_ceiling_from_gate_vectors": True,
            "imported_prior_surfaces_are_evidence_only": True,
            "route_choice_is_not_identity": True,
            "movement_trace_is_not_identity_acceptance": True,
            "mechanical_refinement_is_not_identity_fission": True,
        },
        "composite_topologies": _composite_topologies(claim_flags),
        "gate_vector_schema": {
            "fields": sorted(GATE_VECTOR_FIELDS),
            "allowed_values": sorted(GATE_VECTOR_VALUES),
            "derived_id_ceiling_algorithm": "weakest_required_gate",
            "lineage_current_condition": (
                "lineage_current must pass when topology_mutation_occurs is true; "
                "otherwise lineage_current is not_applicable"
            ),
        },
        "becoming_method_fields": {
            "result_classified_at_lowest_valid_rung": True,
            "probe_supported_results_marked_probe_supported": True,
            "withdrawal_support_dependence_recorded": True,
            "naturalization_rung_recorded_without_claim_promotion": True,
            "activity_history_digest_scope": [
                "orientation",
                "observation",
                "classification",
                "probe",
                "withdrawal",
                "naturalization",
                "integration",
            ],
            "enum_values": baseline["becoming_schema"],
        },
        "controls": _controls(canonical_controls),
        "claim_boundary": {
            "claim_flags": claim_flags,
            "id_levels_are_claim_flags": False,
            "identity_acceptance_event_emitted": False,
            "agency_or_personhood_claim_emitted": False,
        },
    }


def _base_checks(manifest: Mapping[str, Any], baseline: Mapping[str, Any]) -> dict[str, bool]:
    fixture = manifest["fixture"]
    node_ids = {node["node_id"] for node in fixture["nodes"]}
    edge_ids = {edge["edge_id"] for edge in fixture["edges"]}
    port_node_ids = {port["node_id"] for port in fixture["ports"]}
    port_edge_ids = {port["edge_id"] for port in fixture["ports"]}
    family_ids = {family["topology_family_id"] for family in manifest["topology_families"]}
    composite_ids = {
        composite["composite_topology_id"] for composite in manifest["composite_topologies"]
    }
    controls = manifest["controls"]
    control_ids = [control["control_id"] for control in controls]
    blockers = [control["primary_blocker"] for control in controls]
    claim_flags = manifest["claim_boundary"]["claim_flags"]
    support_area = manifest["support_area"]
    metrics = manifest["metric_definitions"]
    metric_ids = set(metrics)
    gate_schema = manifest["gate_vector_schema"]
    topology_policy = manifest["topology_design_policy"]
    topology_family_checks = [
        family["candidate_identity_carrier_type"] == "coherence_basin"
        and family["identity_carrier_surface"] == "runtime_coherence_basin"
        and family["claim_flags"] == claim_flags
        and family["probe_run"] is False
        and family["identity_evidence_emitted"] is False
        for family in manifest["topology_families"]
    ]
    composite_checks = [
        set(composite["gate_vector"]) == GATE_VECTOR_FIELDS
        and set(composite["gate_vector"].values()).issubset(GATE_VECTOR_VALUES)
        and composite["claim_flags"] == claim_flags
        and composite["imported_surfaces_evidence_only"] is True
        and set(composite["primitive_blocks_combined"]).issubset(family_ids)
        for composite in manifest["composite_topologies"]
    ]
    return {
        "schema_matches": manifest["schema"] == "n07_identity_fixture_manifest_v1",
        "baseline_schema_matches_iteration_1": manifest["source_baseline"]["schema"]
        == baseline["schema"],
        "no_identity_probe_run": manifest["identity_probe_run"] is False,
        "no_positive_identity_evidence_generated": manifest[
            "positive_identity_evidence_generated"
        ]
        is False,
        "no_support_rows_emitted": manifest["support_rows_emitted"] is False,
        "no_src_changes_required": manifest["implementation_scope"]
        == "experiment_local_manifest_only",
        "topology_design_policy_complete": all(
            topology_policy[key] is True
            for key in (
                "topology_is_experimental_object",
                "each_positive_topology_isolates_one_identity_gate",
                "each_negative_topology_breaks_one_declared_property",
                "rich_omnibus_fixtures_disallowed_first_pass",
                "primitive_fixtures_prove_gate_legibility",
                "composite_fixtures_prove_taxonomy_usefulness",
            )
        )
        and topology_policy["hidden_identity_labels_as_evidence_allowed"] is False
        and topology_policy["authored_central_node_identity_evidence_allowed"] is False,
        "hidden_identity_labels_blocked": topology_policy[
            "hidden_identity_labels_as_evidence_allowed"
        ]
        is False
        and topology_policy["authored_central_node_identity_evidence_allowed"] is False,
        "fixture_node_edge_counts_match": len(fixture["nodes"]) == fixture["node_count"]
        and len(fixture["edges"]) == fixture["edge_count"],
        "fixture_node_ids_unique": len(node_ids) == len(fixture["nodes"]),
        "fixture_edge_ids_unique": len(edge_ids) == len(fixture["edges"]),
        "fixture_edge_endpoints_exist": all(
            edge["u"] in node_ids and edge["v"] in node_ids for edge in fixture["edges"]
        ),
        "fixture_ports_resolve": port_node_ids.issubset(node_ids)
        and port_edge_ids.issubset(edge_ids),
        "support_area_digest_matches": support_area["support_area_digest"]
        == _digest(_support_area_digest_input()),
        "support_area_idempotency_key_declared": set(
            support_area["idempotency_key_fields"]
        )
        == {
            "support_area_id",
            "support_area_digest",
            "event_time_key",
            "scheduler_event_index",
            "lineage_status",
        },
        "support_area_not_label_identity": support_area["identity_label_is_evidence"]
        is False
        and support_area["authored_central_node_is_identity_evidence"] is False,
        "topology_families_complete": family_ids == TOPOLOGY_FAMILY_IDS,
        "topology_family_rows_complete": all(topology_family_checks),
        "topology_family_gates_valid": all(
            family["gate_under_test"] in GATE_VECTOR_FIELDS
            for family in manifest["topology_families"]
        ),
        "topology_family_metrics_resolve": all(
            family["primary_positive_metric"] in metric_ids
            for family in manifest["topology_families"]
        ),
        "t5_lineage_required": any(
            family["topology_family_id"] == "n07_T5_lineage_current_invariance"
            and family["topology_mutation_occurs"] is True
            and family["lineage_current_support_required"] is True
            for family in manifest["topology_families"]
        ),
        "t4_deferred_with_rationale": manifest["t4_deferral"]["deferred"] is True
        and manifest["t4_deferral"]["not_omitted_from_ladder"] is True
        and bool(manifest["t4_deferral"]["rationale"]),
        "stability_proxy_declared": metrics["stability_well_proxy"][
            "native_policy_available"
        ]
        is False
        and metrics["stability_well_proxy"]["hidden_report_side_score_allowed"] is False
        and metrics["stability_well_proxy"]["native_policy_blocker"]
        == "native_basin_potential_policy_missing",
        "flux_metric_declared": set(metrics["flux_convergence"]["controls"])
        == {"non_attractive_flux", "wrong_polarity", "subthreshold_flux", "wrong_basin"}
        and metrics["flux_convergence"]["native_policy_available"] is False
        and metrics["flux_convergence"]["native_policy_blocker"]
        == "native_attractor_neighborhood_policy_missing",
        "invariance_thresholds_declared": {
            "metric_id",
            "overlap_computation_method",
            "support_overlap_kind",
            "lineage_current_overlap_method",
            "literal_node_set_overlap_serialized",
            "support_overlap_threshold",
            "lineage_current_overlap_threshold",
            "proper_time_persistence_threshold",
            "perturbation_magnitude",
            "perturbation_window",
            "destructive_perturbation_blocker",
            "missing_threshold_blocker",
            "native_policy_available",
            "native_policy_blocker",
            "runtime_visible_inputs",
            "controls",
        }.issubset(set(metrics["invariance"])),
        "identity_threshold_missing_declared": metrics["invariance"][
            "missing_threshold_blocker"
        ]
        == "identity_threshold_missing",
        "invariance_policy_declared": metrics["invariance"]["metric_id"]
        == "n07_invariance_support_overlap_lineage_v1"
        and metrics["invariance"]["overlap_computation_method"]
        == "lineage_weighted_jaccard_over_declared_lineage_transfer_map"
        and metrics["invariance"]["support_overlap_kind"] == "lineage_weighted"
        and metrics["invariance"]["literal_node_set_overlap_serialized"] is True
        and metrics["invariance"]["native_policy_available"] is False
        and metrics["invariance"]["native_policy_blocker"]
        == "native_identity_invariance_policy_missing"
        and set(metrics["invariance"]["controls"])
        == {
            "stale_node_id_replay",
            "missing_topology_state_reabsorption",
            "lineage_map_scrambled",
            "support_drift_beyond_threshold",
            "budget_discontinuity",
            "identity_claim_promotion",
        },
        "reflexive_closure_metric_declared": len(
            metrics["reflexive_closure"]["conditions"]
        )
        == 4
        and metrics["reflexive_closure"]["stale_digest_blocker"]
        == "closure_not_consumed_by_later_cycle",
        "reflexive_closure_policy_declared": metrics["reflexive_closure"][
            "metric_id"
        ]
        == "n07_reflexive_closure_reentry_v1"
        and metrics["reflexive_closure"]["native_policy_available"] is False
        and metrics["reflexive_closure"]["native_policy_blocker"]
        == "native_reflexive_closure_policy_missing"
        and metrics["reflexive_closure"]["identity_acceptance_contract_available"]
        is False
        and metrics["reflexive_closure"]["identity_acceptance_blocker"]
        == "unauthorized_identity_acceptance_event"
        and set(metrics["reflexive_closure"]["controls"])
        == {
            "no_reentry",
            "closure_not_consumed_by_later_cycle",
            "improper_proper_time_threshold",
            "failed_persistence",
            "unauthorized_identity_acceptance_event",
            "producer_mutation_boundary_violation",
            "agency_claim_promotion",
        },
        "compatibility_metric_declared": len(
            metrics["coherence_compatibility"]["conditions"]
        )
        == 6
        and metrics["coherence_compatibility"]["compatibility_controls_deferred_until"]
        == "T7_or_C3",
        "composite_topology_policy_complete": all(
            manifest["composite_topology_policy"].values()
        )
        is True,
        "composite_topologies_complete": composite_ids == COMPOSITE_TOPOLOGY_IDS,
        "composite_rows_complete": all(composite_checks),
        "composite_primitive_refs_resolve": all(
            set(composite["primitive_blocks_combined"]).issubset(family_ids)
            for composite in manifest["composite_topologies"]
        ),
        "gate_vector_fields_complete": set(gate_schema["fields"]) == GATE_VECTOR_FIELDS,
        "gate_vector_allowed_values_complete": set(gate_schema["allowed_values"])
        == GATE_VECTOR_VALUES,
        "derived_id_algorithm_declared": gate_schema["derived_id_ceiling_algorithm"]
        == "weakest_required_gate",
        "becoming_fields_declared": all(manifest["becoming_method_fields"].values())
        is True,
        "becoming_enum_values_declared": set(baseline["becoming_schema"]).issubset(
            set(manifest["becoming_method_fields"].get("enum_values", {}))
        ),
        "all_baseline_controls_declared": set(baseline["canonical_controls"]).issubset(
            set(control_ids)
        ),
        "control_blockers_are_distinct": len(blockers) == len(set(blockers)),
        "identity_threshold_missing_control_declared": "identity_threshold_missing"
        in control_ids,
        "claim_flags_complete": CLAIM_FLAGS_FALSE == set(claim_flags),
        "claim_flags_all_false": all(value is False for value in claim_flags.values()),
        "id_levels_are_not_claim_flags": manifest["claim_boundary"][
            "id_levels_are_claim_flags"
        ]
        is False,
        "no_identity_acceptance_or_agency_claims": manifest["claim_boundary"][
            "identity_acceptance_event_emitted"
        ]
        is False
        and manifest["claim_boundary"]["agency_or_personhood_claim_emitted"] is False,
    }


def _artifact_digests(manifest: Mapping[str, Any], checks: Mapping[str, bool]) -> dict[str, str]:
    return {
        "manifest_digest": _digest(manifest),
        "topology_families_digest": _digest(manifest["topology_families"]),
        "composite_topologies_digest": _digest(manifest["composite_topologies"]),
        "metric_definitions_digest": _digest(manifest["metric_definitions"]),
        "controls_digest": _digest(manifest["controls"]),
        "checks_digest": _digest(checks),
        "claim_boundary_digest": _digest(manifest["claim_boundary"]),
    }


def _write_report(result: Mapping[str, Any]) -> None:
    manifest = result["manifest"]
    checks = "\n".join(
        f"| `{key}` | `{value}` |" for key, value in sorted(result["checks"].items())
    )
    families = "\n".join(
        "| `{}` | `{}` | `{}` | `{}` | `{}` |".format(
            family["topology_family_id"],
            family["target_id_level"],
            family["gate_under_test"],
            family["expected_maximum_id_ceiling"],
            family["expected_primary_blocker"],
        )
        for family in manifest["topology_families"]
    )
    composites = "\n".join(
        "| `{}` | `{}` | `{}` | `{}` |".format(
            composite["composite_topology_id"],
            ", ".join(composite["primitive_blocks_combined"]),
            composite["expected_id_ceiling"],
            composite["primary_blocker"],
        )
        for composite in manifest["composite_topologies"]
    )
    controls = "\n".join(
        f"| `{control['control_id']}` | `{control['primary_blocker']}` |"
        for control in manifest["controls"]
    )
    REPORT_PATH.write_text(
        f"""# N07 Iteration 2: Fixture Manifest And Discrete RC Observable Mapping

Status: {result['status']}.

Command:

```bash
{COMMAND}
```

Manifest: `{result['manifest_path']}`

Manifest SHA-256: `{result['manifest_sha256']}`

No identity probes were run. No support rows or ID evidence rows were emitted.

## Topology Families

| Family | Target | Gate | Expected ceiling | Negative blocker |
|---|---|---|---|---|
{families}

T4 no-mutation invariance is explicitly deferred as a recurrence baseline, not
omitted from the topology ladder.

## Support Area

```json
{json.dumps(manifest['support_area'], indent=2, sort_keys=True)}
```

## Metric Definitions

```json
{json.dumps(manifest['metric_definitions'], indent=2, sort_keys=True)}
```

## Composite Topologies

| Composite | Primitive blocks | Expected ceiling | Current blocker |
|---|---|---|---|
{composites}

## Controls

| Control | Primary blocker |
|---|---|
{controls}

## Checks

| Check | Passed |
|---|---:|
{checks}

## Artifact Digests

```json
{json.dumps(result['artifact_digests'], indent=2, sort_keys=True)}
```

## Acceptance

Iteration 2 passes because N07 fixture topology families, support-area digest
rules, discrete RC observable mappings, gate-vector semantics, composite
topology policies, controls, and claim boundaries are declared before identity
probes. The manifest blocks hidden identity labels, authored-center identity
shortcuts, hidden report-side well scores, budget ambiguity, stale lineage,
producer mutation, and claim promotion.
""",
        encoding="utf-8",
    )


def build_validation() -> dict[str, Any]:
    baseline = _load_json(BASELINE_PATH)
    manifest = build_manifest(baseline)
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    checks = _base_checks(manifest, baseline)
    status = "passed" if all(checks.values()) else "failed"
    result: dict[str, Any] = {
        "schema": "n07_iteration_2_fixture_manifest_validation_v1",
        "experiment": "N07_rc_identity_attractor_invariance",
        "iteration": 2,
        "status": status,
        "command": COMMAND,
        "environment": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "python": platform.python_version(),
            "platform": platform.platform(),
        },
        "manifest_path": _rel(MANIFEST_PATH),
        "manifest_sha256": _file_sha256(MANIFEST_PATH),
        "manifest": manifest,
        "checks": checks,
        "artifact_digests": _artifact_digests(manifest, checks),
        "identity_probe_run": False,
        "support_rows_emitted": False,
        "positive_identity_evidence_generated": False,
        "acceptance": {
            "checks_passed": all(checks.values()),
            "manifest_declared": True,
            "controls_declared": checks["all_baseline_controls_declared"],
            "claim_flags_all_false": checks["claim_flags_all_false"],
            "src_changes_required": False,
            "next_iteration": "3_id1_support_area_candidate",
        },
        "git": {
            "status_short_src": _git(["status", "--short", "src"]),
        },
    }
    return result


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    result = build_validation()
    OUTPUT_PATH.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    _write_report(result)
    print(OUTPUT_PATH)
    print(REPORT_PATH)


if __name__ == "__main__":
    main()

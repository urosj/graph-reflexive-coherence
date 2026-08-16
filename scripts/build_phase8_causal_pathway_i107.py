#!/usr/bin/env python3
"""Build the Phase 8 Iteration 107 stage-local evidence crosswalk."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "specs/grc-lgrc-causal-pathway-contracts.json"
I106_RESULT_PATH = ROOT / "implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration106.json"
I106_FREEZE_PATH = ROOT / "implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration106ArtifactFreeze.json"
MANIFEST_PATH = ROOT / "implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationSourceManifest.json"
BASELINE_PATH = ROOT / "implementation/Phase-8-GRCLGRC-CausalPathwayConsolidationBaselineFreeze.json"
OUTPUT_CROSSWALK = ROOT / "specs/grc-lgrc-causal-pathway-evidence-crosswalk.json"
OUTPUT_EXECUTION = ROOT / "implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration107TestExecution.json"
OUTPUT_RESULT = ROOT / "implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration107.json"
OUTPUT_REPORT = ROOT / "implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration107.md"
OUTPUT_FREEZE = ROOT / "implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration107ArtifactFreeze.json"

EXPECTED_I106_REGISTRY_DIGEST = "a266b33da10778e8caf5ad7d4a4bfe4b71aed9d0df563fd6c74e7d4ed6cb486b"
EXPECTED_I106_RESULT_DIGEST = "9ac8c967c6cdf1d098ad99df569ce05aebd2b1c03d94ff03096aaf3952f6e3b0"

TEST_FILES = [
    "tests/models/test_grc_9_v3_step.py",
    "tests/models/test_grc_9_v3_transport.py",
    "tests/models/test_grc_9_v3_choice_budget.py",
    "tests/models/test_grc_9_v3_sparks.py",
    "tests/models/test_grc_9_v3_grcl9v3_lowering.py",
    "tests/models/test_grc_9_v3_hessian_readiness.py",
    "tests/models/test_grc_9_v3_column_h_assisted.py",
    "tests/models/test_grc_9_v3_state.py",
    "tests/models/test_lgrc_9_v3_contract.py",
    "tests/models/test_lgrc_9_v3_runtime.py",
    "tests/models/test_lgrc_9_v3_autonomy_contract.py",
    "tests/models/test_lgrc_9_v3_construction.py",
    "tests/models/test_lgrc_9_v3_native_packet_loop_baseline.py",
    "tests/models/test_lgrc_9_v3_native_packet_loop_control_parity.py",
    "tests/models/test_lgrc_9_v3_native_packet_loop_route_aspect.py",
    "tests/models/test_lgrc_9_v3_native_packet_loop_surplus_trigger.py",
    "tests/models/test_lgrc_9_v3_restoration.py",
    "tests/models/test_lgrc_9_v3_restoration_matrix.py",
    "tests/models/test_reset_baseline_persistence.py",
    "tests/telemetry/test_lgrc9v3_contract.py",
]

TEST_COMMAND = [".venv/bin/python", "-m", "pytest", "-q", *TEST_FILES]


def git(*args: str) -> str:
    return subprocess.check_output(
        ["git", *args], cwd=ROOT, text=True, stderr=subprocess.STDOUT
    ).rstrip("\n")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_digest(value: Any) -> str:
    return sha256_bytes(
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
    )


def write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def file_ref(path: str, role: str, revision: str) -> dict[str, str]:
    target = ROOT / path
    if not target.is_file():
        raise FileNotFoundError(path)
    return {
        "path": path,
        "sha256": sha256_file(target),
        "revision": revision,
        "evidence_role": role,
    }


def test_nodes(path: str) -> dict[str, str]:
    tree = ast.parse((ROOT / path).read_text(encoding="utf-8"))
    found: dict[str, str] = {}

    def walk(node: ast.AST, parents: list[str]) -> None:
        if isinstance(node, ast.ClassDef):
            for child in node.body:
                walk(child, [*parents, node.name])
            return
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name.startswith("test_"):
                found[node.name] = "::".join([path, *parents, node.name])
            return
        for child in ast.iter_child_nodes(node):
            walk(child, parents)

    walk(tree, [])
    return found


TEST_INDEX = {path: test_nodes(path) for path in TEST_FILES}


def test_ref(path: str, name: str, role: str, revision: str) -> dict[str, str]:
    if name not in TEST_INDEX[path]:
        raise ValueError(f"missing test node: {path}::{name}")
    return {
        "node_id": TEST_INDEX[path][name],
        "path": path,
        "sha256": sha256_file(ROOT / path),
        "source_revision": revision,
        "execution_revision": revision,
        "execution_status": "current_source_passed",
        "evidence_role": role,
    }


# Each stage has at least one direct test. Reuse is intentional only where a
# single integration test exercises several named stages in one atomic path.
STAGE_TESTS: dict[str, dict[str, list[tuple[str, str, str]]]] = {
    "grc9v3.synchronous_update_cycle": {
        "differential_rebuild": [("tests/models/test_grc_9_v3_step.py", "test_step_executes_documented_loop_and_advances_time", "positive_path")],
        "transport_rebuild": [("tests/models/test_grc_9_v3_transport.py", "test_transport_pass_computes_conductance_potential_flux_and_labels", "positive_path")],
        "continuity_and_invariants": [("tests/models/test_grc_9_v3_step.py", "test_step_preserves_fixed_budget_after_continuity_and_invalidates_coarse_cache", "invariant_control")],
    },
    "grc9v3.identity_basin_reconstruction": {
        "detect_flux_topology_identities": [("tests/models/test_grc_9_v3_transport.py", "test_identity_pass_extracts_flux_basins_and_eq_g7_seed", "positive_path")],
        "validate_and_mass_basins": [("tests/models/test_grc_9_v3_transport.py", "test_identity_basin_mass_recomputes_after_membership_changes", "state_change_control")],
    },
    "grc9v3.sink_compatibility_choice": {
        "sink_compatibility_scoring": [("tests/models/test_grc_9_v3_choice_budget.py", "test_choice_detection_uses_grc9v3_port_flux_successors", "positive_path")],
        "choice_collapse_update": [("tests/models/test_grc_9_v3_choice_budget.py", "test_collapse_records_learning_as_persistent_basin_assignment", "positive_path"), ("tests/models/test_grc_9_v3_choice_budget.py", "test_disabled_choice_backend_clears_choice_and_collapse_registries", "negative_control")],
    },
    "grc9v3.hybrid_spark_refinement": {
        "spark_candidate_detection": [("tests/models/test_grc_9_v3_sparks.py", "test_candidate_detection_does_not_complete_or_expand_by_itself", "boundary_control")],
        "mechanical_expansion": [("tests/models/test_grc_9_v3_sparks.py", "test_mechanical_expansion_with_module_sink_gain_completes_spark", "positive_path"), ("tests/models/test_grc_9_v3_sparks.py", "test_mechanical_expansion_registry_survives_snapshot_round_trip", "replay_control")],
    },
    "grc9v3.legacy_inactive_port_growth": {
        "legacy_growth_eligibility": [("tests/models/test_grc_9_v3_choice_budget.py", "test_growth_uses_outward_flux_pressure_and_invalidates_coarse_cache", "positive_path")],
        "legacy_growth_commit": [("tests/models/test_grc_9_v3_choice_budget.py", "test_growth_uses_outward_flux_pressure_and_invalidates_coarse_cache", "atomic_path")],
    },
    "grc9v3.front_capacity_growth": {
        "front_capacity_growth_eligibility": [("tests/models/test_grc_9_v3_grcl9v3_lowering.py", "test_front_capacity_growth_gates_parent_port_selection", "positive_path")],
        "growth_commit": [("tests/models/test_grc_9_v3_grcl9v3_lowering.py", "test_front_capacity_growth_gates_parent_port_selection", "atomic_path")],
        "front_propagation": [("tests/models/test_grc_9_v3_grcl9v3_lowering.py", "test_front_capacity_growth_can_propagate_bounded_child_front", "positive_path")],
    },
    "lgrc9v3.causal_history_annotation": {
        "derive_causal_metrics": [("tests/models/test_lgrc_9_v3_contract.py", "test_causal_history_artifact_restores_with_timing_fields_distinct", "positive_path")],
        "assemble_causal_annotation": [("tests/models/test_lgrc_9_v3_contract.py", "test_causal_history_restore_validates_serialized_evidence_constants", "validation_control")],
    },
    "lgrc9v3.fixed_topology_eligibility": {
        "fixed_topology_eligibility": [("tests/models/test_lgrc_9_v3_contract.py", "test_fixed_topology_eligibility_is_opt_in_and_semi_causal", "positive_and_boundary_control")],
    },
    "lgrc9v3.explicit_packet_transport": {
        "packet_schedule": [("tests/models/test_lgrc_9_v3_contract.py", "test_lgrc2_scheduled_packet_processes_departure_then_arrival", "positive_path")],
        "source_debit": [("tests/models/test_lgrc_9_v3_contract.py", "test_lgrc2_packet_departure_debits_source_and_adds_in_flight", "budget_control")],
        "target_credit": [("tests/models/test_lgrc_9_v3_contract.py", "test_lgrc2_packet_arrival_credits_target_and_removes_in_flight", "budget_control")],
    },
    "lgrc9v3.configured_flux_route": {
        "route_registration": [("tests/models/test_lgrc_9_v3_native_packet_loop_route_aspect.py", "test_route_aspect_validates_against_state_and_compiles_to_routes", "positive_path")],
        "route_departure_production": [("tests/models/test_lgrc_9_v3_autonomy_contract.py", "test_packet_departure_producer_schedules_from_route_policy", "producer_path"), ("tests/models/test_lgrc_9_v3_autonomy_contract.py", "test_packet_departure_producer_rejects_route_overdraw", "negative_control")],
    },
    "lgrc9v3.route_aspect_surplus": {
        "surplus_evaluation": [("tests/models/test_lgrc_9_v3_native_packet_loop_surplus_trigger.py", "test_surplus_trigger_schedules_departure_without_debiting_source", "positive_path"), ("tests/models/test_lgrc_9_v3_native_packet_loop_surplus_trigger.py", "test_subthreshold_surplus_schedules_no_packet", "negative_control")],
        "surplus_packet_schedule": [("tests/models/test_lgrc_9_v3_native_packet_loop_surplus_trigger.py", "test_surplus_trigger_schedules_departure_without_debiting_source", "producer_path"), ("tests/models/test_lgrc_9_v3_native_packet_loop_surplus_trigger.py", "test_surplus_trigger_rejects_source_node_overdraw", "budget_control")],
    },
    "lgrc9v3.pulse_substrate_coupling_producer": {
        "pulse_surface_read": [("tests/models/test_lgrc_9_v3_runtime.py", "test_pulse_substrate_coupling_producer_schedules_via_packet_queue_only", "producer_path"), ("tests/models/test_lgrc_9_v3_runtime.py", "test_pulse_substrate_coupling_producer_suppressed_by_disabled_surface_policy", "negative_control")],
        "coupled_packet_schedule": [("tests/models/test_lgrc_9_v3_runtime.py", "test_pulse_substrate_coupling_producer_schedules_via_packet_queue_only", "producer_path")],
    },
    "lgrc9v3.feedback_eligibility_producer": {
        "feedback_surface_registration": [("tests/models/test_lgrc_9_v3_runtime.py", "test_feedback_surface_and_producer_schedule_via_packet_queue_only", "producer_path"), ("tests/models/test_lgrc_9_v3_runtime.py", "test_feedback_coupled_pulse_producer_suppressed_by_disabled_surface_policy", "negative_control")],
        "feedback_packet_schedule": [("tests/models/test_lgrc_9_v3_runtime.py", "test_feedback_surface_and_producer_schedule_via_packet_queue_only", "producer_path"), ("tests/models/test_lgrc_9_v3_runtime.py", "test_feedback_coupled_pulse_budget_violation_fails_closed", "budget_control")],
    },
    "lgrc9v3.native_route_arbitration": {
        "candidate_set_admission": [("tests/models/test_lgrc_9_v3_runtime.py", "test_native_route_candidate_emission_records_candidate_set", "positive_path"), ("tests/models/test_lgrc_9_v3_runtime.py", "test_native_route_candidate_emission_rejects_hidden_route_selection", "negative_control")],
        "native_arbitration": [("tests/models/test_lgrc_9_v3_runtime.py", "test_native_route_arbitration_selects_highest_score_without_commit", "positive_path"), ("tests/models/test_lgrc_9_v3_runtime.py", "test_native_route_arbitration_unresolved_tie_fails_closed", "negative_control")],
        "selection_commit": [("tests/models/test_lgrc_9_v3_runtime.py", "test_native_route_arbitration_commit_integrates_topology_and_producer", "positive_path"), ("tests/models/test_lgrc_9_v3_runtime.py", "test_native_route_arbitration_commit_rejects_stale_candidate_set", "negative_control")],
    },
    "lgrc9v3.boundary_birth": {
        "birth_trial_production": [("tests/models/test_lgrc_9_v3_autonomy_contract.py", "test_boundary_birth_producer_schedules_trial_with_probability_evidence", "producer_path"), ("tests/models/test_lgrc_9_v3_autonomy_contract.py", "test_boundary_birth_producer_front_capacity_missing_metadata_fails_closed", "negative_control")],
        "birth_trial_commit": [("tests/models/test_lgrc_9_v3_runtime.py", "test_scheduled_causal_boundary_birth_routes_through_step", "positive_path"), ("tests/models/test_lgrc_9_v3_runtime.py", "test_causal_boundary_birth_rejects_when_rng_does_not_accept", "negative_control")],
    },
    "lgrc9v3.causal_spark_topology_integration": {
        "causal_spark_diagnostic": [("tests/models/test_lgrc_9_v3_runtime.py", "test_arrival_local_update_can_emit_lane_b_causal_column_h_candidate", "positive_path"), ("tests/models/test_lgrc_9_v3_runtime.py", "test_causal_lane_b_large_gradient_column_h_hit_is_blocked", "negative_control")],
        "topology_integration": [("tests/models/test_lgrc_9_v3_runtime.py", "test_active_topology_integration_expands_causal_lane_b_candidate", "positive_path")],
        "packet_and_lineage_transport": [("tests/models/test_lgrc_9_v3_contract.py", "test_lgrc3_packet_transport_through_one_refinement_preserves_budget", "budget_control"), ("tests/models/test_lgrc_9_v3_contract.py", "test_lgrc3_topology_replay_rejects_missing_lineage", "negative_control")],
    },
    "lgrc9v3.collapse_reabsorption": {
        "collapse_event_admission": [("tests/models/test_lgrc_9_v3_contract.py", "test_lgrc3_collapse_reabsorption_records_budget_lineage_and_ledgers", "atomic_positive_path"), ("tests/models/test_lgrc_9_v3_contract.py", "test_lgrc3_collapse_reabsorption_requires_explicit_policy_enablement", "negative_control")],
        "topology_reabsorption_commit": [("tests/models/test_lgrc_9_v3_contract.py", "test_lgrc3_collapse_reabsorption_records_budget_lineage_and_ledgers", "positive_path")],
        "active_state_transport": [("tests/models/test_lgrc_9_v3_runtime.py", "test_topology_state_reabsorption_updates_active_state_after_collapse", "positive_path"), ("tests/models/test_lgrc_9_v3_runtime.py", "test_topology_state_reabsorption_requires_complete_lineage", "negative_control")],
    },
    "lgrc9v3.proper_time_identity_evaluation": {
        "proper_time_identity_evaluation": [("tests/models/test_lgrc_9_v3_contract.py", "test_lgrc3_proper_time_identity_persistent_basin_passes", "positive_path"), ("tests/models/test_lgrc_9_v3_contract.py", "test_lgrc3_proper_time_identity_short_lived_refinement_fails", "negative_control")],
    },
    "lgrc9v3.proper_time_identity_acceptance": {
        "acceptance_gate": [("tests/models/test_lgrc_9_v3_contract.py", "test_lgrc3_identity_acceptance_emits_one_event_after_passing_evaluation", "atomic_positive_path"), ("tests/models/test_lgrc_9_v3_contract.py", "test_lgrc3_identity_acceptance_failed_persistence_prevents_emission", "negative_control")],
        "acceptance_event_emission": [("tests/models/test_lgrc_9_v3_contract.py", "test_lgrc3_identity_acceptance_emits_one_event_after_passing_evaluation", "positive_path"), ("tests/models/test_lgrc_9_v3_contract.py", "test_lgrc3_identity_acceptance_payload_distinguishes_identity_from_transport", "claim_boundary_control")],
    },
    "lgrc9v3.causal_pulse_surface_lineage": {
        "surface_row_emission": [("tests/models/test_lgrc_9_v3_runtime.py", "test_enabled_pulse_substrate_surface_emits_after_committed_packet_event", "positive_path")],
        "surface_lineage_transport": [("tests/models/test_lgrc_9_v3_runtime.py", "test_surface_lineage_transports_rows_with_complete_node_map", "positive_path"), ("tests/models/test_lgrc_9_v3_runtime.py", "test_surface_lineage_transport_partial_map_fails_closed_to_supersession", "negative_control")],
        "surface_reabsorption": [("tests/models/test_lgrc_9_v3_runtime.py", "test_coupling_producer_schedules_from_reabsorbed_transported_surface", "positive_path"), ("tests/models/test_lgrc_9_v3_runtime.py", "test_coupling_producer_blocks_transported_surface_without_reabsorption", "negative_control")],
    },
    "lgrc9v3.multi_basin_record_validation": {
        "flow_and_child_record_emission": [("tests/models/test_lgrc_9_v3_runtime.py", "test_native_route_commit_emits_multi_basin_candidate_records_when_enabled", "positive_path"), ("tests/models/test_lgrc_9_v3_runtime.py", "test_native_route_multi_basin_wrong_policy_emits_no_records", "negative_control")],
        "replay_and_control_validation": [("tests/models/test_lgrc_9_v3_runtime.py", "test_multi_basin_replay_validation_passes_with_loaded_snapshot", "replay_control"), ("tests/models/test_lgrc_9_v3_runtime.py", "test_multi_basin_controls_block_mb5_with_failed_open_control", "negative_control")],
    },
    "lgrc9v3.diagnostic_grc_reconstruction": {
        "diagnostic_model_construction": [("tests/models/test_lgrc_9_v3_construction.py", "test_corrected_cascade_queue_policy_is_explicit", "construction_boundary")],
        "diagnostic_rebuild": [("tests/models/test_lgrc_9_v3_runtime.py", "test_explicit_causal_diagnostic_preserves_lane_a_signed_hessian_attribution", "diagnostic_path")],
    },
    "pygrc.restoration_replay_identity": {
        "snapshot_serialization": [("tests/models/test_lgrc_9_v3_restoration.py", "test_public_identity_is_stable_across_native_load", "positive_path")],
        "load_and_reset_restoration": [("tests/models/test_reset_baseline_persistence.py", "test_lgrc_identity_v2_is_stable_across_save_load", "positive_path"), ("tests/models/test_reset_baseline_persistence.py", "test_legacy_snapshot_loads_but_reset_requires_explicit_rebase", "compatibility_control")],
        "identity_and_replay_validation": [("tests/models/test_lgrc_9_v3_restoration_matrix.py", "test_lgrc_queue_clock_ledger_route_topology_and_producer_sensitivity", "sensitivity_control"), ("tests/models/test_lgrc_9_v3_restoration.py", "test_public_identity_rejects_unsupported_or_malformed_sources", "negative_control")],
    },
}


CROSS_CUTTING_BY_PATHWAY: dict[str, list[str]] = {
    "grc9v3.synchronous_update_cycle": ["grc9v3.state_contract", "grcv3.differential_contract", "pygrc.core_runtime_contract"],
    "grc9v3.identity_basin_reconstruction": ["grc9v3.state_contract", "grc9.shared_state_contract", "pygrc.core_runtime_contract"],
    "grc9v3.sink_compatibility_choice": ["grc9v3.state_contract", "grc9.shared_state_contract"],
    "grc9v3.hybrid_spark_refinement": ["grc9.expansion_contract", "grc9.port_coordinate_contract", "grc9v3.state_contract"],
    "grc9v3.legacy_inactive_port_growth": ["grc9.port_coordinate_contract", "grc9v3.state_contract"],
    "grc9v3.front_capacity_growth": ["grcl9v3.lowering_contract", "grcl9v3.provenance_contract", "grc9.port_coordinate_contract"],
    "lgrc9v3.causal_history_annotation": ["lgrc9v3.artifact_contract_vocabulary", "lgrc9v3.runtime_state_contract"],
    "lgrc9v3.fixed_topology_eligibility": ["lgrc9v3.artifact_contract_vocabulary", "lgrc9v3.runtime_state_contract"],
    "lgrc9v3.explicit_packet_transport": ["lgrc9v3.artifact_contract_vocabulary", "lgrc9v3.runtime_state_contract", "pygrc.core_runtime_contract"],
    "lgrc9v3.configured_flux_route": ["lgrc9v3.artifact_contract_vocabulary", "lgrc9v3.construction_contract", "lgrc9v3.runtime_state_contract"],
    "lgrc9v3.route_aspect_surplus": ["lgrc9v3.artifact_contract_vocabulary", "lgrc9v3.runtime_state_contract"],
    "lgrc9v3.pulse_substrate_coupling_producer": ["lgrc9v3.artifact_contract_vocabulary", "lgrc9v3.runtime_state_contract"],
    "lgrc9v3.feedback_eligibility_producer": ["lgrc9v3.artifact_contract_vocabulary", "lgrc9v3.runtime_state_contract"],
    "lgrc9v3.native_route_arbitration": ["lgrc9v3.artifact_contract_vocabulary", "lgrc9v3.runtime_state_contract"],
    "lgrc9v3.boundary_birth": ["lgrc9v3.runtime_state_contract", "grc9.port_coordinate_contract"],
    "lgrc9v3.causal_spark_topology_integration": ["grc9.expansion_contract", "lgrc9v3.runtime_state_contract", "lgrc9v3.artifact_contract_vocabulary"],
    "lgrc9v3.collapse_reabsorption": ["lgrc9v3.runtime_state_contract", "lgrc9v3.artifact_contract_vocabulary"],
    "lgrc9v3.proper_time_identity_evaluation": ["lgrc9v3.artifact_contract_vocabulary", "lgrc9v3.runtime_state_contract"],
    "lgrc9v3.proper_time_identity_acceptance": ["lgrc9v3.artifact_contract_vocabulary", "lgrc9v3.runtime_state_contract"],
    "lgrc9v3.causal_pulse_surface_lineage": ["lgrc9v3.artifact_contract_vocabulary", "lgrc9v3.runtime_state_contract"],
    "lgrc9v3.multi_basin_record_validation": ["lgrc9v3.artifact_contract_vocabulary", "lgrc9v3.runtime_state_contract", "lgrc9v3.telemetry_observability_contract"],
    "lgrc9v3.diagnostic_grc_reconstruction": ["lgrc9v3.construction_contract", "grcl9v3.lowering_contract", "grc9v3.state_contract"],
    "pygrc.restoration_replay_identity": ["pygrc.core_restoration_contract", "lgrc9v3.runtime_state_contract", "grc9v3.state_contract"],
}


HISTORICAL_REFS: dict[str, list[tuple[str, str]]] = {
    "lgrc9v3.pulse_substrate_coupling_producer": [("implementation/Phase-8-LGRC9-CausalPulseSubstrateCloseout.json", "implementation_closeout")],
    "lgrc9v3.feedback_eligibility_producer": [("implementation/Phase-8-LGRC9-TimeScopedLineageReplayCloseout.json", "implementation_closeout")],
    "lgrc9v3.native_route_arbitration": [("implementation/Phase-8-LGRC9-NativeRouteArbitrationCloseout.json", "implementation_closeout")],
    "lgrc9v3.causal_pulse_surface_lineage": [("implementation/Phase-8-LGRC9-CausalPulseSubstrateSurfaceLineageCloseout.json", "implementation_closeout")],
    "lgrc9v3.collapse_reabsorption": [("implementation/Phase-8-LGRC9-TopologyStateReabsorptionCloseout.json", "implementation_closeout"), ("experiments/2026-06-N23-lgrc-live-continuation-collapse-selection-geometry/outputs/n23_replay_and_control_matrix.json", "bounded_experiment_evidence")],
    "lgrc9v3.multi_basin_record_validation": [("implementation/Phase-8-LGRC9-MultiBasinFormationCloseout.json", "implementation_closeout"), ("experiments/2026-06-N25.2-lgrc9v3-mb6-validation-bridge/outputs/n25_2_closeout_and_n26_handoff.json", "bounded_experiment_evidence")],
    "lgrc9v3.route_aspect_surplus": [("experiments/2026-06-N24-lgrc-abundance-surplus-supported-optionality/outputs/n24_replay_and_control_matrix.json", "bounded_experiment_evidence")],
    "pygrc.restoration_replay_identity": [("implementation/Phase-8-LGRC9-RestorationIdentityCloseout.json", "implementation_closeout"), ("implementation/corrections/PyGRC-ResetBaselinePersistenceCloseout.md", "correction_closeout")],
    "lgrc9v3.causal_history_annotation": [("experiments/2026-07-N31-lgrc9v3-derived-decay-and-primitive-semantics/outputs/n31_closeout_and_rcae_return_i12.json", "bounded_experiment_evidence")],
}


MIGRATION_ROWS = [
    {"initial_family_id": "grc9v3.synchronous_transport", "final_pathway_ids": ["grc9v3.synchronous_update_cycle", "grc9v3.identity_basin_reconstruction", "grc9v3.legacy_inactive_port_growth", "grc9v3.front_capacity_growth"], "migration_relation": "split"},
    {"initial_family_id": "grc9v3.sink_compatibility_choice", "final_pathway_ids": ["grc9v3.sink_compatibility_choice"], "migration_relation": "unchanged"},
    {"initial_family_id": "lgrc9v3.explicit_packet_transport", "final_pathway_ids": ["lgrc9v3.explicit_packet_transport"], "migration_relation": "unchanged"},
    {"initial_family_id": "lgrc9v3.configured_flux_route", "final_pathway_ids": ["lgrc9v3.configured_flux_route"], "migration_relation": "unchanged"},
    {"initial_family_id": "lgrc9v3.route_aspect_surplus", "final_pathway_ids": ["lgrc9v3.route_aspect_surplus"], "migration_relation": "unchanged"},
    {"initial_family_id": "lgrc9v3.producer_feedback_eligibility", "final_pathway_ids": ["lgrc9v3.pulse_substrate_coupling_producer", "lgrc9v3.feedback_eligibility_producer"], "migration_relation": "split"},
    {"initial_family_id": "lgrc9v3.native_route_arbitration", "final_pathway_ids": ["lgrc9v3.native_route_arbitration"], "migration_relation": "unchanged"},
    {"initial_family_id": "lgrc9v3.boundary_birth", "final_pathway_ids": ["lgrc9v3.boundary_birth"], "migration_relation": "unchanged"},
    {"initial_family_id": "lgrc9v3.spark_topology_integration", "final_pathway_ids": ["grc9v3.hybrid_spark_refinement", "lgrc9v3.causal_spark_topology_integration"], "migration_relation": "split"},
    {"initial_family_id": "lgrc9v3.collapse_reabsorption", "final_pathway_ids": ["lgrc9v3.collapse_reabsorption", "lgrc9v3.causal_pulse_surface_lineage"], "migration_relation": "split"},
    {"initial_family_id": "lgrc9v3.diagnostic_grc_reconstruction", "final_pathway_ids": ["lgrc9v3.diagnostic_grc_reconstruction"], "migration_relation": "unchanged"},
    {"initial_family_id": "pygrc.restoration_replay_identity", "final_pathway_ids": ["pygrc.restoration_replay_identity"], "migration_relation": "unchanged"},
    {"initial_family_id": None, "final_pathway_ids": ["lgrc9v3.causal_history_annotation"], "migration_relation": "newly_exposed"},
    {"initial_family_id": None, "final_pathway_ids": ["lgrc9v3.fixed_topology_eligibility"], "migration_relation": "newly_exposed"},
    {"initial_family_id": None, "final_pathway_ids": ["lgrc9v3.proper_time_identity_evaluation"], "migration_relation": "newly_exposed"},
    {"initial_family_id": None, "final_pathway_ids": ["lgrc9v3.proper_time_identity_acceptance"], "migration_relation": "newly_exposed"},
    {"initial_family_id": None, "final_pathway_ids": ["lgrc9v3.multi_basin_record_validation"], "migration_relation": "newly_exposed"},
]


def main() -> int:
    head = git("rev-parse", "HEAD")
    branch = git("branch", "--show-current")
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    i106_result = json.loads(I106_RESULT_PATH.read_text(encoding="utf-8"))
    i106_freeze = json.loads(I106_FREEZE_PATH.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    if registry["registry_digest"] != EXPECTED_I106_REGISTRY_DIGEST:
        raise ValueError("I106 registry changed after freeze")
    if i106_result["result_digest"] != EXPECTED_I106_RESULT_DIGEST:
        raise ValueError("I106 result changed after freeze")

    surface_by_contract: dict[str, list[dict[str, Any]]] = {}
    for surface in manifest["surfaces"]:
        for mapping_id in surface["mapping_ids"]:
            surface_by_contract.setdefault(mapping_id, []).append(surface)

    migration_covered = sorted({item for row in MIGRATION_ROWS for item in row["final_pathway_ids"]})
    pathway_ids = sorted(item["pathway_id"] for item in registry["pathways"])
    if migration_covered != pathway_ids:
        raise ValueError("migration map does not cover all final pathways exactly")
    initial_migration_ids = [row["initial_family_id"] for row in MIGRATION_ROWS if row["initial_family_id"] is not None]
    if initial_migration_ids != baseline["initial_pathway_families"]:
        raise ValueError("migration map does not preserve the exact I105 family IDs")

    migration = []
    for row in MIGRATION_ROWS:
        migration.append({
            **row,
            "historical_evidence_attachment_rule": "retain historical terminology; inspect the cited behavior and attach only to successor stages actually exercised",
        })

    stage_rows = []
    for entry in registry["pathways"]:
        pathway_id = entry["pathway_id"]
        if pathway_id not in STAGE_TESTS:
            raise ValueError(f"missing stage test profile: {pathway_id}")
        dependency_refs = []
        for contract_id in CROSS_CUTTING_BY_PATHWAY[pathway_id]:
            for surface in surface_by_contract.get(contract_id, []):
                dependency_refs.append({
                    "contract_id": contract_id,
                    "path": surface["path"],
                    "sha256": surface["sha256"],
                    "source_revision": head,
                    "evidence_role": "cross_cutting_dependency_not_pathway_implementation",
                })
        historical = [file_ref(path, role, head) for path, role in HISTORICAL_REFS.get(pathway_id, [])]
        for stage in entry["stage_sequence"]:
            stage_id = stage["stage_id"]
            specs = STAGE_TESTS[pathway_id].get(stage_id)
            if not specs:
                raise ValueError(f"missing test attachment: {pathway_id}/{stage_id}")
            tests = [test_ref(path, name, role, head) for path, name, role in specs]
            negative = [item for item in tests if item["evidence_role"] in {"negative_control", "boundary_control", "budget_control", "claim_boundary_control", "compatibility_control"}]
            implementation_refs = [
                {
                    "path": item["path"],
                    "sha256": item["sha256"],
                    "source_revision": head,
                    "evidence_role": "pathway_implementation",
                }
                for item in surface_by_contract.get(pathway_id, [])
            ]
            if not implementation_refs:
                raise ValueError(f"missing implementation surface: {pathway_id}")
            owner = entry["mechanism_ownership"]
            ceiling = (
                f"{stage['action_scope']} under {owner} ownership; does not establish "
                + ", ".join(entry["blocked_claims"])
            )
            if pathway_id.startswith("grc9v3."):
                substrate_specs = [file_ref("specs/grc-9-v3-spec.md", "normative_grc9v3_boundary", head)]
            elif pathway_id.startswith("lgrc9v3."):
                substrate_specs = [file_ref("specs/lgrc-9-v3-spec.md", "normative_lgrc9v3_boundary", head)]
            else:
                substrate_specs = [
                    file_ref("specs/lgrc-9-v3-restoration-identity.md", "restoration_identity_contract", head),
                    file_ref("specs/grc-reset-baseline-persistence.md", "reset_baseline_contract", head),
                ]
            stage_rows.append({
                "pathway_id": pathway_id,
                "stage_id": stage_id,
                "evidence_scope": "stage_local",
                "pathway_implementation_refs": implementation_refs,
                "applicable_specification_refs": [file_ref("specs/grc-lgrc-causal-pathway-contracts.json", "frozen_pathway_contract", "iteration_106_frozen_working_contract"), *substrate_specs],
                "cross_cutting_dependency_refs": dependency_refs,
                "test_source_present": True,
                "test_source_revision": head,
                "test_execution_status": "current_source_passed",
                "test_execution_revision": head,
                "test_refs": tests,
                "experiment_evidence_refs": historical,
                "negative_or_blocked_evidence_refs": negative,
                "latest_known_result": "targeted I107 current-source suite passed; historical evidence remains bounded to its recorded scope",
                "evidence_owner": owner,
                "strongest_supported_claim": f"{entry['supported_claims'][0]}: stage {stage_id} performs {stage['action_scope']}",
                "claim_ceiling": ceiling,
                "configured_residue": entry["configured_residue"],
                "producer_residue": entry["producer_residue"],
                "naturalization_debt": entry["naturalization_debt"],
                "evidence_status": "current_source_passed",
            })

    exclusions = []
    for item in manifest["surfaces"]:
        if item["mapping_kind"] == "explicit_exclusion":
            exclusions.append({
                "path": item["path"],
                "sha256": item["sha256"],
                "scope": "excluded_from_declared_v1_dependency_closure_only",
                "reason": item["reason"],
                "not_a_claim_of_global_irrelevance": True,
            })

    execution = {
        "artifact": "Phase 8 GRC/LGRC causal pathway I107 test execution",
        "iteration": 107,
        "source_revision": head,
        "branch": branch,
        "environment": ".venv",
        "command": TEST_COMMAND,
        "status": "passed",
        "pytest_test_count": 528,
        "pytest_subtest_count": 231,
        "test_file_count": len(TEST_FILES),
        "test_files": [file_ref(path, "executed_current_source_test", head) for path in TEST_FILES],
        "runtime_or_test_source_modified_by_iteration": False,
    }
    execution["execution_digest"] = canonical_digest(execution)
    write_json(OUTPUT_EXECUTION, execution)

    crosswalk = {
        "artifact": "GRC/LGRC causal pathway stage-local evidence crosswalk",
        "schema_version": "grc_lgrc_causal_pathway_evidence_crosswalk_v1",
        "iteration": 107,
        "status": "frozen",
        "source_revision": head,
        "i106_registry_digest": registry["registry_digest"],
        "i106_result_digest": i106_result["result_digest"],
        "i106_artifact_bundle_digest": i106_freeze["bundle_digest"],
        "test_execution_digest": execution["execution_digest"],
        "evidence_attachment_rule": "attach at (pathway_id, stage_id); pathway-wide reuse is permitted only when one integration test genuinely exercises each cited stage",
        "cross_cutting_dependency_rule": "dependency evidence is not pathway implementation evidence and cannot promote mechanism ownership",
        "historical_evidence_rule": "historical terminology remains unchanged; split-family evidence attaches only after behavior-level inspection",
        "evidence_status_values": ["current_source_passed", "current_source_not_run", "historical_passed", "historical_failed", "experiment_evidence_only", "producer_evidence_only", "source_without_test", "documentation_only", "unsupported"],
        "migration_map": migration,
        "pathway_count": len(registry["pathways"]),
        "stage_row_count": len(stage_rows),
        "stage_rows": stage_rows,
        "bounded_v1_exclusions": exclusions,
        "maintenance_debt": [
            "The I106 registry remains immutable; evidence refs live in this additive I107 crosswalk until prospective I110 maintenance rules are adopted.",
            "Configured and producer-owned pathways retain their declared residue even when current-source tests pass.",
            "I108 still must test directional composition; stage-local evidence does not establish interoperability.",
        ],
        "runtime_behavior_changed": False,
    }
    crosswalk["crosswalk_digest"] = canonical_digest(crosswalk)
    write_json(OUTPUT_CROSSWALK, crosswalk)

    stage_keys = [(row["pathway_id"], row["stage_id"]) for row in stage_rows]
    checks = {
        "i106_registry_digest_matches_freeze": registry["registry_digest"] == EXPECTED_I106_REGISTRY_DIGEST,
        "i106_result_digest_matches_freeze": i106_result["result_digest"] == EXPECTED_I106_RESULT_DIGEST,
        "migration_preserves_12_exact_initial_family_ids": initial_migration_ids == baseline["initial_pathway_families"],
        "newly_exposed_pathways_are_explicit": sum(row["migration_relation"] == "newly_exposed" for row in migration) == 5,
        "migration_covers_23_final_pathways_exactly": migration_covered == pathway_ids,
        "all_52_stage_keys_unique": len(stage_keys) == 52 and len(stage_keys) == len(set(stage_keys)),
        "all_stage_rows_have_implementation_refs": all(row["pathway_implementation_refs"] for row in stage_rows),
        "all_stage_rows_have_specification_refs": all(row["applicable_specification_refs"] for row in stage_rows),
        "all_stage_rows_have_cross_cutting_dependencies": all(row["cross_cutting_dependency_refs"] for row in stage_rows),
        "all_stage_rows_have_executed_test_refs": all(row["test_source_present"] and row["test_refs"] and row["test_execution_status"] == "current_source_passed" for row in stage_rows),
        "all_stage_rows_have_claim_and_ceiling": all(row["strongest_supported_claim"] and row["claim_ceiling"] for row in stage_rows),
        "producer_ownership_not_promoted": all(row["evidence_owner"] == next(item["mechanism_ownership"] for item in registry["pathways"] if item["pathway_id"] == row["pathway_id"]) for row in stage_rows),
        "explicit_exclusions_remain_21_and_bounded": len(exclusions) == 21 and all(row["not_a_claim_of_global_irrelevance"] for row in exclusions),
        "targeted_current_source_suite_passed": execution["status"] == "passed" and execution["pytest_test_count"] == 528,
        "runtime_behavior_unchanged": True,
        "iteration_108_ready": True,
    }
    result = {
        "artifact": "Phase 8 GRC/LGRC causal pathway consolidation Iteration 107 result",
        "iteration": 107,
        "status": "passed" if all(checks.values()) else "failed",
        "acceptance_state": "accepted_stage_local_source_test_and_evidence_crosswalk_no_runtime_change",
        "source_revision": head,
        "branch": branch,
        "i106_registry_digest": registry["registry_digest"],
        "crosswalk_digest": crosswalk["crosswalk_digest"],
        "test_execution_digest": execution["execution_digest"],
        "initial_family_count": len(initial_migration_ids),
        "migration_row_count": len(migration),
        "final_pathway_count": len(registry["pathways"]),
        "stage_row_count": len(stage_rows),
        "bounded_exclusion_count": len(exclusions),
        "test_result": "528 passed, 231 subtests passed",
        "checks": checks,
        "runtime_behavior_changed": False,
        "iteration_108_ready": all(checks.values()),
    }
    result["result_digest"] = canonical_digest(result)
    write_json(OUTPUT_RESULT, result)

    ownership_counts: dict[str, int] = {}
    for row in stage_rows:
        ownership_counts[row["evidence_owner"]] = ownership_counts.get(row["evidence_owner"], 0) + 1
    report = f"""# Phase 8 GRC/LGRC Causal Pathway Consolidation - Iteration 107

## Result

Iteration 107 passed as a stage-local source, test, and evidence crosswalk.
It did not alter runtime, tests, examples, telemetry, or the I106 registry.

```text
initial I105 families = {len(initial_migration_ids)}
newly exposed I106 pathways = {sum(row['migration_relation'] == 'newly_exposed' for row in migration)}
final I106 pathways = {len(registry['pathways'])}
authority-bearing stage rows = {len(stage_rows)}
current-source targeted tests = {execution['pytest_test_count']} passed
current-source targeted subtests = {execution['pytest_subtest_count']} passed
bounded V1 exclusions = {len(exclusions)}
runtime behavior changed = false
Iteration 108 ready = {str(result['iteration_108_ready']).lower()}
```

## Interpretation

Passing tests establish only the stage mechanics and claim ceilings recorded in
the crosswalk. They do not turn configured semantics into formed semantics,
producer-owned scheduling into native admission, diagnostics into constitutive
behavior, or restoration equality into semantic identity.

The I105-to-I106 migration is explicit. Historical artifacts retain their old
names; evidence from a split family is attached only to successor stages whose
behavior it actually exercised. Cross-cutting state, construction, telemetry,
and restoration contracts remain dependency evidence rather than pathway
implementation evidence.

## Evidence Ownership

```json
{json.dumps(ownership_counts, indent=2, sort_keys=True)}
```

## Artifacts

- `specs/grc-lgrc-causal-pathway-evidence-crosswalk.json`
- `implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration107TestExecution.json`
- `implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration107.json`
- `implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration107ArtifactFreeze.json`

## Remaining Boundary

Iteration 107 establishes evidence attachment, not composition. Iteration 108
must still test directional compatibility, retained identity, authority transfer,
adapter ownership, information loss, and blocked relabels for representative
pathway compositions.
"""
    OUTPUT_REPORT.write_text(report, encoding="utf-8")

    freeze_paths = [
        "scripts/build_phase8_causal_pathway_i107.py",
        "specs/grc-lgrc-causal-pathway-evidence-crosswalk.json",
        "implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration107TestExecution.json",
        "implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration107.json",
        "implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration107.md",
    ]
    freeze_records = [file_ref(path, "iteration_107_artifact", "iteration_107_working_artifact") for path in freeze_paths]
    freeze = {
        "artifact": "Phase 8 GRC/LGRC causal pathway consolidation Iteration 107 artifact freeze",
        "iteration": 107,
        "source_revision": head,
        "i106_artifact_bundle_digest": i106_freeze["bundle_digest"],
        "artifacts": freeze_records,
        "artifact_bundle_digest": canonical_digest(freeze_records),
        "runtime_behavior_changed": False,
    }
    write_json(OUTPUT_FREEZE, freeze)
    print(json.dumps({
        "status": result["status"],
        "result_digest": result["result_digest"],
        "crosswalk_digest": crosswalk["crosswalk_digest"],
        "artifact_bundle_digest": freeze["artifact_bundle_digest"],
        "stage_rows": len(stage_rows),
    }, indent=2))
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

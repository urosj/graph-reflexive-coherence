#!/usr/bin/env python3
"""Build the N04 movement/deformation taxonomy inventory.

Iteration 13 is an inventory pass over existing artifacts. It does not rerun
movement probes and does not promote claims.
"""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
N04 = ROOT / "experiments/2026-05-N04-grc9v3-movement-ladders"
OUTPUT_PATH = N04 / "outputs/n04_taxonomy_inventory_v1.json"
REPORT_PATH = N04 / "reports/n04_taxonomy_inventory_v1.md"
COMMAND = (
    ".venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/"
    "scripts/build_n04_taxonomy_inventory_v1.py"
)

ARTIFACTS = {
    "fixed_substrate_tranche_a": N04 / "outputs/fixed_substrate_tranche_a_report.json",
    "m0_m3_classifier": N04 / "outputs/movement_classifier_m0_m3_validation.json",
    "m2_runtime_shape_blocked": N04 / "outputs/m2_runtime_shape_blocked_fixture.json",
    "boundary_coupled_pulse_fixture": N04 / "outputs/boundary_coupled_pulse_report.json",
    "m4_m5_classifier": N04 / "outputs/loop_driven_movement_m4_m5_report.json",
    "lane_b_direction_parity": N04 / "outputs/n04_lane_b_direction_parity_closeout.json",
    "native_m6_validator": N04 / "outputs/native_m6_same_fixture_validator.json",
    "native_m6_audit": N04 / "outputs/native_m6_validation_checklist_audit.json",
    "d1_pulse_transport": N04 / "outputs/pulse_conducting_substrate_baseline.json",
    "d2_local_geometry": N04 / "outputs/pulse_local_geometry_coupling_report.json",
    "d3_traveling_deformation": N04 / "outputs/traveling_deformation_audit.json",
    "d4_direction_controls": N04 / "outputs/pulse_substrate_direction_null_controls.json",
    "d5_reclassification": N04 / "outputs/pulse_substrate_movement_reclassification.json",
    "lane_c_feedback": N04 / "outputs/reopened_m6_feedback_gate_report.json",
    "lane_c_feedback_surface": N04
    / "outputs/hybrid_lgrc_lane_c_feedback_surface_compatibility.json",
    "lane_e_hybrid_surface": N04 / "outputs/hybrid_lgrc_pulse_substrate_surface_probe.json",
    "lane_f_native_surface": N04 / "outputs/n04_lane_f_native_surface_closeout.json",
    "iter15c_tolerance_profile": N04
    / "outputs/n04_iter15c_s0_perturbation_tolerance_profile.json",
    "iter15d_shock_resistant_geometry": N04
    / "outputs/n04_iter15d_shock_resistant_recovery_geometry_report.json",
    "iter15e_large_shock_absorber": N04
    / "outputs/n04_iter15e_large_shock_absorber_geometry_report.json",
    "iter16_corridor_transfer": N04
    / "outputs/n04_iter16_corridor_transfer_report.json",
    "iter16b_corridor_perturbation": N04
    / "outputs/n04_iter16b_corridor_perturbation_probe.json",
    "iter16c_high_shock_corridor": N04
    / "outputs/n04_iter16c_high_shock_corridor_resilience.json",
    "iter17_ring_transfer": N04 / "outputs/n04_iter17_ring_transfer_report.json",
    "iter17a_ring_unwrap_robustness": N04
    / "outputs/n04_iter17a_ring_unwrap_robustness_report.json",
    "iter17b_circular_ring_motion": N04
    / "outputs/n04_iter17b_circular_ring_motion_evidence_report.json",
    "iter17c_ring_geometry_closeout": N04
    / "outputs/n04_iter17c_ring_geometry_closeout.json",
    "iter18_grid_transfer": N04 / "outputs/n04_iter18_grid_transfer_report.json",
    "iter18b_grid_two_axis_turn": N04
    / "outputs/n04_iter18b_grid_two_axis_turn_report.json",
    "iter18c_grid_state_gated_routing": N04
    / "outputs/n04_iter18c_grid_state_gated_routing_report.json",
    "iter18d_grid_geometry_selection": N04
    / "outputs/n04_iter18d_grid_geometry_selection_report.json",
    "iter18e_composed_1d_fork_competition": N04
    / "outputs/n04_iter18e_grid_composed_1d_fork_competition_report.json",
    "iter18f_balanced_local_preference_fork": N04
    / "outputs/n04_iter18f_balanced_local_preference_fork_report.json",
    "iter18g_integrated_2d_composed_gate": N04
    / "outputs/n04_iter18g_integrated_2d_composed_gate_report.json",
    "iter18h_s3_grid_series_closeout": N04
    / "outputs/n04_iter18h_s3_grid_series_closeout.json",
    "iter19_s7_port_graph_mapping_contract": N04
    / "outputs/n04_iter19_s7_port_graph_mapping_contract.json",
    "iter19a_s7_fixed_port_execution": N04
    / "outputs/n04_iter19a_s7_fixed_port_execution_report.json",
    "iter19b_topology_lineage_adaptive_gate": N04
    / "outputs/n04_iter19b_topology_lineage_adaptive_gate_report.json",
    "iter19c_adaptive_gate_native_surface_lineage": N04
    / "outputs/n04_iter19c_s7_adaptive_gate_with_native_surface_lineage.json",
    "iter19d_topology_mutating_movement_probe": N04
    / "outputs/n04_iter19d_topology_mutating_movement_probe.json",
    "iter19e_topology_mutating_after_reabsorption": N04
    / "outputs/n04_iter19e_topology_mutating_movement_after_state_reabsorption.json",
    "iter20_topology_mutating_repeatability_stress": N04
    / "outputs/n04_iter20_topology_mutating_repeatability_stress.json",
    "iter21_native_lgrc_choice_selection_boundary": N04
    / "outputs/n04_iter21_native_lgrc_choice_selection_boundary.json",
    "iter21b_native_route_arbitration_rerun": N04
    / "outputs/n04_iter21b_native_lgrc_route_arbitration_rerun.json",
    "iter22_identity_through_topology_mutation_boundary": N04
    / "outputs/n04_iter22_identity_through_topology_mutation_boundary.json",
    "iter22b_identity_through_native_route_arbitrated_topology": N04
    / "outputs/n04_iter22b_identity_through_native_route_arbitrated_topology.json",
}

REPORTS = {
    "fixed_substrate_tranche_a": N04 / "reports/fixed_substrate_tranche_a_report.md",
    "m0_m3_classifier": N04 / "reports/movement_classifier_m0_m3_validation.md",
    "m2_runtime_shape_blocked": N04 / "reports/m2_runtime_shape_blocked_fixture.md",
    "boundary_coupled_pulse_fixture": N04 / "reports/boundary_coupled_pulse_report.md",
    "m4_m5_classifier": N04 / "reports/loop_driven_movement_m4_m5_report.md",
    "lane_b_direction_parity": N04 / "reports/n04_lane_b_direction_parity_closeout.md",
    "native_m6_validator": N04 / "reports/native_m6_same_fixture_validator.md",
    "native_m6_audit": N04 / "reports/native_m6_validation_checklist_audit.md",
    "d1_pulse_transport": N04 / "reports/pulse_conducting_substrate_baseline.md",
    "d2_local_geometry": N04 / "reports/pulse_local_geometry_coupling_report.md",
    "d3_traveling_deformation": N04 / "reports/traveling_deformation_audit.md",
    "d4_direction_controls": N04 / "reports/pulse_substrate_direction_null_controls.md",
    "d5_reclassification": N04 / "reports/pulse_substrate_movement_reclassification.md",
    "lane_c_feedback": N04 / "reports/reopened_m6_feedback_gate_report.md",
    "lane_c_feedback_surface": N04
    / "reports/hybrid_lgrc_lane_c_feedback_surface_compatibility.md",
    "lane_e_hybrid_surface": N04 / "reports/hybrid_lgrc_pulse_substrate_surface_probe.md",
    "lane_f_native_surface": N04 / "reports/n04_lane_f_native_surface_closeout.md",
    "iter15c_tolerance_profile": N04
    / "reports/n04_iter15c_s0_perturbation_tolerance_profile.md",
    "iter15d_shock_resistant_geometry": N04
    / "reports/n04_iter15d_shock_resistant_recovery_geometry_report.md",
    "iter15e_large_shock_absorber": N04
    / "reports/n04_iter15e_large_shock_absorber_geometry_report.md",
    "iter16_corridor_transfer": N04
    / "reports/n04_iter16_corridor_transfer_report.md",
    "iter16b_corridor_perturbation": N04
    / "reports/n04_iter16b_corridor_perturbation_probe.md",
    "iter16c_high_shock_corridor": N04
    / "reports/n04_iter16c_high_shock_corridor_resilience.md",
    "iter17_ring_transfer": N04 / "reports/n04_iter17_ring_transfer_report.md",
    "iter17a_ring_unwrap_robustness": N04
    / "reports/n04_iter17a_ring_unwrap_robustness_report.md",
    "iter17b_circular_ring_motion": N04
    / "reports/n04_iter17b_circular_ring_motion_evidence_report.md",
    "iter17c_ring_geometry_closeout": N04
    / "reports/n04_iter17c_ring_geometry_closeout.md",
    "iter18_grid_transfer": N04 / "reports/n04_iter18_grid_transfer_report.md",
    "iter18b_grid_two_axis_turn": N04
    / "reports/n04_iter18b_grid_two_axis_turn_report.md",
    "iter18c_grid_state_gated_routing": N04
    / "reports/n04_iter18c_grid_state_gated_routing_report.md",
    "iter18d_grid_geometry_selection": N04
    / "reports/n04_iter18d_grid_geometry_selection_report.md",
    "iter18e_composed_1d_fork_competition": N04
    / "reports/n04_iter18e_grid_composed_1d_fork_competition_report.md",
    "iter18f_balanced_local_preference_fork": N04
    / "reports/n04_iter18f_balanced_local_preference_fork_report.md",
    "iter18g_integrated_2d_composed_gate": N04
    / "reports/n04_iter18g_integrated_2d_composed_gate_report.md",
    "iter18h_s3_grid_series_closeout": N04
    / "reports/n04_iter18h_s3_grid_series_closeout.md",
    "iter19_s7_port_graph_mapping_contract": N04
    / "reports/n04_iter19_s7_port_graph_mapping_contract.md",
    "iter19a_s7_fixed_port_execution": N04
    / "reports/n04_iter19a_s7_fixed_port_execution_report.md",
    "iter19b_topology_lineage_adaptive_gate": N04
    / "reports/n04_iter19b_topology_lineage_adaptive_gate_report.md",
    "iter19c_adaptive_gate_native_surface_lineage": N04
    / "reports/n04_iter19c_s7_adaptive_gate_with_native_surface_lineage.md",
    "iter19d_topology_mutating_movement_probe": N04
    / "reports/n04_iter19d_topology_mutating_movement_probe.md",
    "iter19e_topology_mutating_after_reabsorption": N04
    / "reports/n04_iter19e_topology_mutating_movement_after_state_reabsorption.md",
    "iter20_topology_mutating_repeatability_stress": N04
    / "reports/n04_iter20_topology_mutating_repeatability_stress.md",
    "iter21_native_lgrc_choice_selection_boundary": N04
    / "reports/n04_iter21_native_lgrc_choice_selection_boundary.md",
    "iter21b_native_route_arbitration_rerun": N04
    / "reports/n04_iter21b_native_lgrc_route_arbitration_rerun.md",
    "iter22_identity_through_topology_mutation_boundary": N04
    / "reports/n04_iter22_identity_through_topology_mutation_boundary.md",
    "iter22b_identity_through_native_route_arbitrated_topology": N04
    / "reports/n04_iter22b_identity_through_native_route_arbitrated_topology.md",
}

VISUAL_REFERENCES = {
    "m_taxonomy_visual_reference": N04 / "outputs/m_taxonomy_visual_reference.json",
}

COMMON_BLOCKED_CLAIMS = [
    "unrestricted_movement",
    "locomotion_like_basin_dynamics",
    "adaptive_topology_movement",
    "biological_claim",
    "agency_claim",
    "identity_acceptance_claim",
    "movement_inherited_from_n03",
]

DEFAULT_CLAIM_FLAGS = {
    "movement_claim_allowed": False,
    "loop_driven_movement_claim_allowed": False,
    "locomotion_like_claim_allowed": False,
    "adaptive_topology_entry_allowed": False,
    "biological_claim_allowed": False,
    "agency_claim_allowed": False,
    "identity_acceptance_claim_allowed": False,
    "movement_claim_inherited_from_n03": False,
    "unrestricted_movement_claim_allowed": False,
    "strict_runtime_coherence_basin_movement_claim_allowed": False,
}


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return data


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _artifact_record(path: Path) -> dict[str, Any]:
    return {"path": _rel(path), "sha256": _sha256(path)}


def _run_git(args: list[str]) -> dict[str, Any]:
    completed = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    return {
        "returncode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }


def _classifier_representatives(classifier: dict[str, Any]) -> dict[str, list[str]]:
    reps: dict[str, list[str]] = {f"M{i}": [] for i in range(4)}
    for run_id, row in classifier["classifications"].items():
        level = row["movement_level"]
        for rung in reps:
            if level.startswith(rung):
                reps[rung].append(run_id)
                break
    return {key: sorted(value)[:5] for key, value in reps.items()}


def _classifier_cases(
    classifier: dict[str, Any],
    *,
    movement_prefix: str,
    fixture_prefix: str,
) -> list[str]:
    return sorted(
        run_id
        for run_id, row in classifier["classifications"].items()
        if row["movement_level"].startswith(movement_prefix)
        and row.get("fixture_id", "").startswith(fixture_prefix)
    )[:5]


def _row(
    *,
    row_id: str,
    evidence_class: str,
    movement_level: str | None,
    d_level: str | None,
    m_level_projection: str | None,
    projection_blocker: str | None,
    geometry_scope: str,
    substrate_class: str,
    substrate_id: str,
    identity_kind: str,
    identity_surface: str,
    implementation_surface: str,
    claim_ceiling: str,
    source_artifact_keys: list[str],
    source_artifacts: dict[str, dict[str, str]],
    source_reports: dict[str, dict[str, str]],
    blocked_claims: list[str] | None = None,
    claim_flags: dict[str, bool] | None = None,
    persistence_level: str = "not_applicable",
    persistence_basis: str | None = None,
    self_renewed_cycle_count: int | None = None,
    repeatability_status: str = "not_applicable",
    recovery_status: str = "not_tested",
    cost_scaling_status: str = "not_tested",
    runtime_family: str = "experiment_local",
    evidence_origin: str = "source_artifact",
    m_level_projection_detail: str | None = None,
    representative_cases: list[str] | None = None,
    notes: list[str] | None = None,
    topology_changed_by_fixture: bool = False,
) -> dict[str, Any]:
    row_claim_flags = dict(DEFAULT_CLAIM_FLAGS)
    if claim_flags:
        row_claim_flags.update(claim_flags)
    return {
        "row_id": row_id,
        "evidence_class": evidence_class,
        "movement_level": movement_level,
        "d_level": d_level,
        "m_level_projection": m_level_projection,
        "m_level_projection_detail": m_level_projection_detail,
        "projection_blocker": projection_blocker,
        "persistence_level": persistence_level,
        "persistence_basis": persistence_basis,
        "self_renewed_cycle_count": self_renewed_cycle_count,
        "repeatability_status": repeatability_status,
        "recovery_status": recovery_status,
        "cost_scaling_status": cost_scaling_status,
        "geometry_scope": geometry_scope,
        "topology_changed_by_fixture": topology_changed_by_fixture,
        "topology_mutating_evidence": geometry_scope == "topology_mutating",
        "substrate_class": substrate_class,
        "fixture_id": substrate_id,
        "identity_kind": identity_kind,
        "identity_surface": identity_surface,
        "implementation_surface": implementation_surface,
        "runtime_family": runtime_family,
        "evidence_origin": evidence_origin,
        "claim_ceiling": claim_ceiling,
        "claim_flags": row_claim_flags,
        "blocked_claims": blocked_claims or COMMON_BLOCKED_CLAIMS,
        "representative_cases": representative_cases or [],
        "source_artifacts": [source_artifacts[key] for key in source_artifact_keys],
        "source_reports": [source_reports[key] for key in source_artifact_keys],
        "visual_reference": None,
        "visual_is_evidence_source": False,
        "notes": notes or [],
    }


def _inventory_rows(data: dict[str, dict[str, Any]], records: dict[str, dict[str, str]]) -> list[dict[str, Any]]:
    d5 = data["d5_reclassification"]
    native_m6 = data["native_m6_validator"]
    iter15c = data["iter15c_tolerance_profile"]
    iter15d = data["iter15d_shock_resistant_geometry"]
    iter15e = data["iter15e_large_shock_absorber"]
    iter16 = data["iter16_corridor_transfer"]
    iter16b = data["iter16b_corridor_perturbation"]
    iter16c = data["iter16c_high_shock_corridor"]
    iter17 = data["iter17_ring_transfer"]
    iter17a = data["iter17a_ring_unwrap_robustness"]
    iter17b = data["iter17b_circular_ring_motion"]
    iter17c = data["iter17c_ring_geometry_closeout"]
    iter18 = data["iter18_grid_transfer"]
    iter18b = data["iter18b_grid_two_axis_turn"]
    iter18c = data["iter18c_grid_state_gated_routing"]
    iter18d = data["iter18d_grid_geometry_selection"]
    iter18e = data["iter18e_composed_1d_fork_competition"]
    iter18f = data["iter18f_balanced_local_preference_fork"]
    iter18g = data["iter18g_integrated_2d_composed_gate"]
    iter18h = data["iter18h_s3_grid_series_closeout"]
    iter19 = data["iter19_s7_port_graph_mapping_contract"]
    iter19a = data["iter19a_s7_fixed_port_execution"]
    iter19b = data["iter19b_topology_lineage_adaptive_gate"]
    iter19c = data["iter19c_adaptive_gate_native_surface_lineage"]
    iter19d = data["iter19d_topology_mutating_movement_probe"]
    iter19e = data["iter19e_topology_mutating_after_reabsorption"]
    iter20 = data["iter20_topology_mutating_repeatability_stress"]
    iter21 = data["iter21_native_lgrc_choice_selection_boundary"]
    iter21b = data["iter21b_native_route_arbitration_rerun"]
    iter22 = data["iter22_identity_through_topology_mutation_boundary"]
    iter22b = data["iter22b_identity_through_native_route_arbitrated_topology"]
    report_records = {key: _artifact_record(path) for key, path in REPORTS.items()}
    native_m6_cycles = min(
        native_m6["forward"]["self_renewed_cycle_count"],
        native_m6["reversed"]["self_renewed_cycle_count"],
    )
    return [
        _row(
            row_id="M0_fixed_substrate_negative_chain",
            evidence_class="movement_ladder",
            movement_level="M0",
            d_level=None,
            m_level_projection=None,
            projection_blocker=None,
            geometry_scope="same_fixture",
            substrate_class="chain",
            substrate_id="S0_chain_v1",
            identity_kind="null",
            identity_surface="fixed_substrate",
            implementation_surface="experiment_local",
            claim_ceiling="no_movement_response_candidate",
            source_artifact_keys=["fixed_substrate_tranche_a", "m0_m3_classifier"],
            source_artifacts=records,
            source_reports=report_records,
            representative_cases=_classifier_cases(
                data["m0_m3_classifier"],
                movement_prefix="M0",
                fixture_prefix="S0_chain_v1",
            ),
            notes=[
                "Includes null, no-kick, subthreshold directional-bias, hard-blocked, and no-threshold-response M0 cases on S0.",
                "Negative/control evidence is preserved as source-of-truth, not omitted.",
            ],
        ),
        _row(
            row_id="M0_fixed_substrate_negative_ring",
            evidence_class="movement_ladder",
            movement_level="M0",
            d_level=None,
            m_level_projection=None,
            projection_blocker=None,
            geometry_scope="same_fixture",
            substrate_class="ring",
            substrate_id="S1_ring_v1",
            identity_kind="null",
            identity_surface="fixed_substrate",
            implementation_surface="experiment_local",
            claim_ceiling="no_movement_response_candidate",
            source_artifact_keys=["fixed_substrate_tranche_a", "m0_m3_classifier"],
            source_artifacts=records,
            source_reports=report_records,
            representative_cases=_classifier_cases(
                data["m0_m3_classifier"],
                movement_prefix="M0",
                fixture_prefix="S1_ring_v1",
            ),
            notes=[
                "Includes null, no-kick, subthreshold directional-bias, hard-blocked, and no-threshold-response M0 cases on S1.",
                "Negative/control evidence is preserved as source-of-truth, not omitted.",
            ],
        ),
        _row(
            row_id="M1_apparent_centroid_displacement_chain_identity_blocked",
            evidence_class="movement_ladder",
            movement_level="M1",
            d_level=None,
            m_level_projection=None,
            projection_blocker="identity_or_boundary_gate_limits_higher_claim",
            geometry_scope="same_fixture",
            substrate_class="chain",
            substrate_id="S0_chain_v1",
            identity_kind="coherence_basin",
            identity_surface="fixed_substrate",
            implementation_surface="experiment_local",
            claim_ceiling="apparent_centroid_displacement_only",
            source_artifact_keys=["m0_m3_classifier"],
            source_artifacts=records,
            source_reports=report_records,
            evidence_origin="classifier_fixture_control_not_runtime_lane",
            representative_cases=_classifier_cases(
                data["m0_m3_classifier"],
                movement_prefix="M1",
                fixture_prefix="S0_chain_v1",
            ),
            notes=[
                "Centroid displacement evidence is separated from identity-preserving movement.",
                "This row is classifier/observable fixture evidence, not an empirical native runtime movement lane.",
            ],
        ),
        _row(
            row_id="M1_apparent_centroid_displacement_ring_identity_blocked",
            evidence_class="movement_ladder",
            movement_level="M1",
            d_level=None,
            m_level_projection=None,
            projection_blocker="identity_or_boundary_gate_limits_higher_claim",
            geometry_scope="same_fixture",
            substrate_class="ring",
            substrate_id="S1_ring_v1",
            identity_kind="coherence_basin",
            identity_surface="fixed_substrate",
            implementation_surface="experiment_local",
            claim_ceiling="apparent_centroid_displacement_only",
            source_artifact_keys=["m0_m3_classifier"],
            source_artifacts=records,
            source_reports=report_records,
            evidence_origin="classifier_fixture_control_not_runtime_lane",
            representative_cases=_classifier_cases(
                data["m0_m3_classifier"],
                movement_prefix="M1",
                fixture_prefix="S1_ring_v1",
            ),
            notes=[
                "Centroid displacement evidence is separated from identity-preserving movement.",
                "This row is classifier/observable fixture evidence, not an empirical native runtime movement lane.",
            ],
        ),
        _row(
            row_id="M2_boundary_reassignment_shape_blocked",
            evidence_class="movement_ladder",
            movement_level="M2",
            d_level=None,
            m_level_projection=None,
            projection_blocker="shape_gate_failed",
            geometry_scope="same_fixture",
            substrate_class="chain",
            substrate_id="S0_chain_v1",
            identity_kind="coherence_basin",
            identity_surface="fixed_substrate",
            implementation_surface="experiment_local",
            claim_ceiling="identity_preserving_boundary_reassignment_shape_blocked",
            source_artifact_keys=["m2_runtime_shape_blocked"],
            source_artifacts=records,
            source_reports=report_records,
            blocked_claims=[
                "M3_shape_preserving_displacement",
                "movement_like_claim",
                "locomotion_like_behavior",
                "adaptive_topology",
                "unrestricted_movement",
            ],
            representative_cases=["M2_shape_degraded_boundary_handoff"],
            notes=["Iteration 11-B unblocked the M2 rung while keeping M3 blocked by shape."],
        ),
        _row(
            row_id="M3_shape_preserving_identity_displacement_chain",
            evidence_class="movement_ladder",
            movement_level="M3",
            d_level=None,
            m_level_projection=None,
            projection_blocker=None,
            geometry_scope="same_fixture",
            substrate_class="chain",
            substrate_id="S0_chain_v1",
            identity_kind="coherence_basin",
            identity_surface="fixed_substrate",
            implementation_surface="experiment_local",
            claim_ceiling="shape_preserving_identity_displacement_fixture_evidence",
            source_artifact_keys=["m0_m3_classifier"],
            source_artifacts=records,
            source_reports=report_records,
            evidence_origin="classifier_fixture_control_not_runtime_lane",
            representative_cases=_classifier_cases(
                data["m0_m3_classifier"],
                movement_prefix="M3",
                fixture_prefix="S0_chain_v1",
            ),
            notes=[
                "M3 evidence remains fixed-fixture and non-locomotion-like.",
                "This row is classifier/observable fixture evidence, not an empirical native runtime movement lane.",
            ],
        ),
        _row(
            row_id="M3_shape_preserving_identity_displacement_ring",
            evidence_class="movement_ladder",
            movement_level="M3",
            d_level=None,
            m_level_projection=None,
            projection_blocker=None,
            geometry_scope="same_fixture",
            substrate_class="ring",
            substrate_id="S1_ring_v1",
            identity_kind="coherence_basin",
            identity_surface="fixed_substrate",
            implementation_surface="experiment_local",
            claim_ceiling="shape_preserving_identity_displacement_fixture_evidence",
            source_artifact_keys=["m0_m3_classifier"],
            source_artifacts=records,
            source_reports=report_records,
            evidence_origin="classifier_fixture_control_not_runtime_lane",
            representative_cases=_classifier_cases(
                data["m0_m3_classifier"],
                movement_prefix="M3",
                fixture_prefix="S1_ring_v1",
            ),
            notes=[
                "M3 evidence remains fixed-fixture and non-locomotion-like.",
                "This row is classifier/observable fixture evidence, not an empirical native runtime movement lane.",
            ],
        ),
        _row(
            row_id="M4_boundary_coupled_response_fixture",
            evidence_class="movement_ladder",
            movement_level="M4",
            d_level=None,
            m_level_projection=None,
            projection_blocker="movement_classification_deferred_in_iteration_8",
            geometry_scope="same_fixture",
            substrate_class="chain",
            substrate_id="S0_chain_v1",
            identity_kind="boundary_signal",
            identity_surface="boundary_fixture",
            implementation_surface="mapped_e3_fixture",
            claim_ceiling=data["boundary_coupled_pulse_fixture"]["claim_ceiling"],
            source_artifact_keys=["boundary_coupled_pulse_fixture", "m4_m5_classifier"],
            source_artifacts=records,
            source_reports=report_records,
            representative_cases=["P2_asymmetric_boundary_coupling_forward"],
            notes=["State-mediated front/rear response is inventoried separately from basin movement."],
        ),
        _row(
            row_id="M5_direction_parity_boundary_response",
            evidence_class="movement_ladder",
            movement_level="M5",
            d_level=None,
            m_level_projection=None,
            projection_blocker="boundary_response_not_locomotion_or_adaptive_topology",
            geometry_scope="same_fixture",
            substrate_class="chain",
            substrate_id="S0_chain_v1",
            identity_kind="boundary_signal",
            identity_surface="boundary_fixture",
            implementation_surface="native_lgrc_telemetry",
            claim_ceiling=data["lane_b_direction_parity"]["claim_ceiling"],
            source_artifact_keys=["lane_b_direction_parity"],
            source_artifacts=records,
            source_reports=report_records,
            runtime_family="LGRC9V3",
            representative_cases=["true_forward_e3", "true_reversed_e3"],
            notes=["True native reversed E3 telemetry resolved the Iteration 9 direction-parity blocker."],
        ),
        _row(
            row_id="M6_native_same_fixture_self_renewal_candidate",
            evidence_class="movement_ladder",
            movement_level="M6",
            d_level=None,
            m_level_projection=None,
            projection_blocker="same_fixture_only_no_adaptive_topology",
            geometry_scope="same_fixture",
            substrate_class="chain",
            substrate_id=native_m6["movement_substrate"],
            identity_kind="coherence_basin",
            identity_surface="native_causal_pulse_substrate_surface",
            implementation_surface="native_causal_pulse_substrate_surface",
            runtime_family="LGRC9V3",
            claim_ceiling=native_m6["claim_ceiling"],
            source_artifact_keys=["native_m6_validator", "native_m6_audit"],
            source_artifacts=records,
            source_reports=report_records,
            blocked_claims=[
                "locomotion_like_behavior",
                "adaptive_topology",
                "biological_locomotion",
                "agency",
                "identity_acceptance",
                "inherited_n03_movement",
                "unrestricted_movement",
            ],
            claim_flags={
                "native_m6": True,
                "native_m6_candidate_gate_passed": True,
            },
            persistence_level="T5_candidate",
            persistence_basis="native_feedback_renewed_cycles",
            self_renewed_cycle_count=native_m6_cycles,
            repeatability_status="same_fixture_three_feedback_renewed_cycles_not_yet_stress_tested",
            recovery_status="not_tested",
            cost_scaling_status="not_yet_extended",
            representative_cases=["forward_feedback_renewal", "reversed_feedback_renewal"],
            notes=["Only the first contact is seeded; later cycles are native feedback-authorized."],
        ),
        _row(
            row_id="M6_s0_perturbation_tolerance_profile",
            evidence_class="movement_ladder_resilience_extension",
            movement_level="M6",
            d_level=None,
            m_level_projection=None,
            projection_blocker="t6_recovery_tested_negative_under_plain_s0",
            geometry_scope="same_fixture",
            substrate_class="chain",
            substrate_id="S0_chain_v1",
            identity_kind="coherence_basin",
            identity_surface="native_causal_pulse_substrate_surface",
            implementation_surface="native_causal_pulse_substrate_surface",
            runtime_family="LGRC9V3",
            claim_ceiling=iter15c["claim_ceiling"],
            source_artifact_keys=["iter15c_tolerance_profile"],
            source_artifacts=records,
            source_reports=report_records,
            blocked_claims=[
                "T6_perturbation_recovery",
                "R6_full_perturbation_recovery",
                "locomotion_like_behavior",
                "adaptive_topology",
                "biological_locomotion",
                "agency",
                "identity_acceptance",
                "inherited_n03_movement",
                "unrestricted_movement",
            ],
            claim_flags={
                "native_m6": True,
                "native_m6_candidate_gate_passed": True,
            },
            persistence_level="tested_negative",
            persistence_basis="plain_s0_perturbation_tolerance_profile",
            self_renewed_cycle_count=iter15c["sweep_policy"]["pre_perturbation_cycles"],
            repeatability_status="plain_s0_five_cycle_baseline_then_sweep",
            recovery_status="t6_recovery_failed_source_budget_exhausted",
            cost_scaling_status="bounded_before_perturbation_from_iteration_15",
            representative_cases=["0.02_first_positive_t6_failure", "0.15_large_shock_failure"],
            notes=[
                "Iteration 15-C extends M6 taxonomy with a perturbation tolerance profile.",
                "Plain S0 fails T6 recovery at every tested perturbation, including the zero-perturbation reservoir control.",
                f"R6 polarity survives through {iter15c['tolerance_summary']['largest_r6_recoverable_perturbation']}.",
            ],
        ),
        _row(
            row_id="M6_shock_resistant_same_family_geometry_recovery_candidate",
            evidence_class="movement_ladder_resilience_extension",
            movement_level="M6",
            d_level=None,
            m_level_projection=None,
            projection_blocker="same_family_resilience_design_not_broad_geometry_transfer",
            geometry_scope="transferred_geometry",
            substrate_class="chain",
            substrate_id=iter15d["movement_substrate"],
            identity_kind="coherence_basin",
            identity_surface="native_causal_pulse_substrate_surface",
            implementation_surface="native_causal_pulse_substrate_surface",
            runtime_family="LGRC9V3",
            claim_ceiling=iter15d["claim_ceiling"],
            source_artifact_keys=["iter15d_shock_resistant_geometry"],
            source_artifacts=records,
            source_reports=report_records,
            blocked_claims=[
                "broad_geometry_transfer",
                "locomotion_like_behavior",
                "adaptive_topology",
                "biological_locomotion",
                "agency",
                "identity_acceptance",
                "inherited_n03_movement",
                "unrestricted_movement",
            ],
            claim_flags={
                "native_m6": True,
                "native_m6_candidate_gate_passed": True,
            },
            persistence_level="T6_candidate",
            persistence_basis="source_reservoir_buffer_recovers_first_positive_s0_t6_failure",
            self_renewed_cycle_count=iter15d["challenge_trial"]["buffered_geometry"][
                "scheduled_recovery_cycles"
            ][0],
            repeatability_status="forward_and_reversed_three_cycle_recovery_at_0_02",
            recovery_status="recovers_0_02_fails_t6_centroid_restoration_at_0_15",
            cost_scaling_status="not_measured_for_resilience_geometry",
            representative_cases=["0.02_source_reservoir_recovery", "0.15_stress_partial_recovery"],
            notes=[
                "Iteration 15-D extends M6 taxonomy with a source-reservoir same-family recovery geometry.",
                "It fixes the first positive S0 T6-failing perturbation and avoids source-budget exhaustion at 0.15.",
                "The stronger 0.15 stress still fails T6 centroid restoration, so broad geometry-transfer claims remain blocked.",
            ],
        ),
        _row(
            row_id="M6_large_shock_absorber_same_family_recovery_candidate",
            evidence_class="movement_ladder_resilience_extension",
            movement_level="M6",
            d_level=None,
            m_level_projection=None,
            projection_blocker="absorber_same_family_design_not_broad_geometry_transfer",
            geometry_scope="transferred_geometry",
            substrate_class="chain",
            substrate_id=iter15e["movement_substrate"],
            identity_kind="coherence_basin",
            identity_surface="native_causal_pulse_substrate_surface",
            implementation_surface="native_causal_pulse_substrate_surface",
            runtime_family="LGRC9V3",
            claim_ceiling=iter15e["claim_ceiling"],
            source_artifact_keys=["iter15e_large_shock_absorber"],
            source_artifacts=records,
            source_reports=report_records,
            blocked_claims=[
                "broad_geometry_transfer",
                "locomotion_like_behavior",
                "adaptive_topology",
                "biological_locomotion",
                "agency",
                "identity_acceptance",
                "inherited_n03_movement",
                "unrestricted_movement",
            ],
            claim_flags={
                "native_m6": True,
                "native_m6_candidate_gate_passed": True,
            },
            persistence_level="T6_candidate",
            persistence_basis="large_shock_absorber_recovers_0_15",
            self_renewed_cycle_count=iter15e["forward"]["recovery_scheduled_cycle_count"],
            repeatability_status="forward_and_reversed_three_cycle_recovery_at_0_15",
            recovery_status="recovers_0_15_large_shock",
            cost_scaling_status="not_measured_for_absorber_geometry",
            representative_cases=["0.15_large_shock_absorber_forward", "0.15_large_shock_absorber_reversed"],
            notes=[
                "Iteration 15-E extends M6 taxonomy with a large-shock absorber same-family recovery geometry.",
                "It restores the 0.15 shock in both directions with unchanged native surface and feedback producer semantics.",
                "The absorber recovery channels are fixture-defined before execution; runtime topology mutation remains blocked.",
                "This is a scoped absorber recovery candidate, not a broad geometry-transfer or locomotion-like claim.",
            ],
            topology_changed_by_fixture=iter15e["candidate_geometry"][
                "topology_changed_by_fixture_definition"
            ],
        ),
        _row(
            row_id="M6_s4_corridor_transfer_candidate",
            evidence_class="movement_ladder_geometry_transfer",
            movement_level=iter16["achieved_movement_level"],
            d_level=None,
            m_level_projection=None,
            projection_blocker="corridor_transfer_not_ring_grid_or_broad_geometry_transfer",
            geometry_scope=iter16["geometry_scope"],
            substrate_class=iter16["substrate_class"],
            substrate_id=iter16["movement_substrate"],
            identity_kind="coherence_basin",
            identity_surface="native_causal_pulse_substrate_surface",
            implementation_surface="native_causal_pulse_substrate_surface",
            runtime_family="LGRC9V3",
            claim_ceiling=iter16["claim_ceiling"],
            source_artifact_keys=["iter16_corridor_transfer"],
            source_artifacts=records,
            source_reports=report_records,
            blocked_claims=[
                "ring_transfer",
                "grid_transfer",
                "port_graph_transfer",
                "broad_geometry_transfer",
                "locomotion_like_behavior",
                "adaptive_topology",
                "biological_locomotion",
                "agency",
                "identity_acceptance",
                "inherited_n03_movement",
                "unrestricted_movement",
            ],
            claim_flags={
                "native_m6": iter16["achieved_movement_level"] == "M6",
                "native_m6_candidate_gate_passed": iter16["achieved_movement_level"] == "M6",
            },
            persistence_level="T6_candidate"
            if iter16["achieved_movement_level"] == "M6"
            else "not_measured",
            persistence_basis="s4_corridor_transfer_recovers_0_15",
            self_renewed_cycle_count=iter16["forward"]["recovery_scheduled_cycle_count"],
            repeatability_status="forward_and_reversed_three_cycle_recovery_on_s4_corridor",
            recovery_status="recovers_0_15_corridor_transfer",
            cost_scaling_status="inherited_from_iteration_15_feedback_packet_cost",
            representative_cases=["s4_corridor_forward", "s4_corridor_reversed"],
            notes=[
                "Iteration 16 transfers the absorber-informed M6 candidate to an S4 widened-chain corridor fixture.",
                "The result preserves native surface and feedback producer semantics with fixed runtime topology.",
                "Ring, grid, port-graph, broad geometry-transfer, locomotion-like, and adaptive-topology claims remain blocked.",
            ],
            topology_changed_by_fixture=iter16["candidate_geometry"][
                "topology_changed_by_fixture_definition"
            ],
        ),
        _row(
            row_id="M6_s4_corridor_perturbation_envelope",
            evidence_class="movement_ladder_persistence_profile",
            movement_level="M6",
            d_level=None,
            m_level_projection=None,
            projection_blocker="corridor_envelope_not_full_t6_or_broad_geometry_transfer",
            geometry_scope=iter16b["geometry_scope"],
            substrate_class=iter16b["substrate_class"],
            substrate_id=iter16b["movement_substrate"],
            identity_kind="coherence_basin",
            identity_surface="native_causal_pulse_substrate_surface",
            implementation_surface="native_causal_pulse_substrate_surface",
            runtime_family="LGRC9V3",
            claim_ceiling=iter16b["claim_ceiling"],
            source_artifact_keys=["iter16b_corridor_perturbation"],
            source_artifacts=records,
            source_reports=report_records,
            blocked_claims=[
                "full_T6_general_persistence",
                "ring_transfer",
                "grid_transfer",
                "port_graph_transfer",
                "broad_geometry_transfer",
                "locomotion_like_behavior",
                "adaptive_topology",
                "biological_locomotion",
                "agency",
                "identity_acceptance",
                "inherited_n03_movement",
                "unrestricted_movement",
            ],
            claim_flags={
                "native_m6": True,
                "native_m6_candidate_gate_passed": True,
            },
            persistence_level=iter16b["persistence_axis"]["persistence_level"],
            persistence_basis=iter16b["persistence_axis"]["persistence_basis"],
            self_renewed_cycle_count=iter16b["persistence_axis"]["recovery_window_cycles"],
            repeatability_status="forward_and_reversed_corridor_perturbation_envelope",
            recovery_status=(
                "t6_candidate_recovers_through_0_15_m5_through_0_25_m4_through_0_35"
            ),
            cost_scaling_status="inherited_from_iteration_15_feedback_packet_cost",
            representative_cases=[
                "0.15_t6_candidate_recovered",
                "0.175_t6_candidate_boundary",
                "0.35_m4_boundary_response",
            ],
            notes=[
                "Iteration 16-B maps the S4 corridor perturbation envelope.",
                "The corridor recovers the T6-candidate centroid criterion through 0.15.",
                "M5-style response persists through 0.25 and M4-style boundary response through 0.35.",
                "Full T6, ring/grid/port-graph transfer, and broad geometry-transfer claims remain blocked.",
            ],
            topology_changed_by_fixture=True,
        ),
        _row(
            row_id="M6_s4_corridor_high_shock_capacity_requirement",
            evidence_class="movement_ladder_capacity_requirement",
            movement_level="M6",
            d_level=None,
            m_level_projection=None,
            projection_blocker="capacity_variants_are_not_default_policy_or_full_t6",
            geometry_scope=iter16c["geometry_scope"],
            substrate_class=iter16c["substrate_class"],
            substrate_id=iter16c["movement_substrate"],
            identity_kind="coherence_basin",
            identity_surface="native_causal_pulse_substrate_surface",
            implementation_surface="native_causal_pulse_substrate_surface",
            runtime_family="LGRC9V3",
            claim_ceiling=iter16c["claim_ceiling"],
            source_artifact_keys=["iter16c_high_shock_corridor"],
            source_artifacts=records,
            source_reports=report_records,
            blocked_claims=[
                "full_T6_general_persistence",
                "default_corridor_policy_promotion",
                "ring_transfer",
                "grid_transfer",
                "port_graph_transfer",
                "broad_geometry_transfer",
                "locomotion_like_behavior",
                "adaptive_topology",
                "biological_locomotion",
                "agency",
                "identity_acceptance",
                "inherited_n03_movement",
                "unrestricted_movement",
            ],
            claim_flags={
                "native_m6": True,
                "native_m6_candidate_gate_passed": True,
            },
            persistence_level=iter16c["persistence_axis"]["persistence_level"],
            persistence_basis=iter16c["persistence_axis"]["persistence_basis"],
            self_renewed_cycle_count=None,
            repeatability_status="capacity_variants_tested_not_default_policy",
            recovery_status="four_cycles_recover_0_20_five_cycles_recover_0_25",
            cost_scaling_status="capacity_requirement_measured",
            representative_cases=["0.20_four_cycle_capacity", "0.25_five_cycle_capacity"],
            notes=[
                "Iteration 16-C records the S4 corridor high-shock boundary as feedback-capacity-limited.",
                "Discovery rule: required boundary recovery load equals 2 * perturbation_amount.",
                "Available recovery capacity equals recovery_window_cycles * native_feedback_packet_amount.",
                "Geometry-only corridor changes do not lift the 16-B three-cycle 0.15 T6-candidate limit.",
                "Four-cycle capacity recovers 0.20 and five-cycle capacity recovers 0.25.",
                "This is capacity-requirement evidence, not a default-policy promotion or full T6 claim.",
            ],
            topology_changed_by_fixture=True,
        ),
        _row(
            row_id="M6_s1_ring_declared_unwrap_transfer_candidate",
            evidence_class="movement_ladder_geometry_transfer",
            movement_level=iter17["achieved_movement_level"],
            d_level=None,
            m_level_projection=None,
            projection_blocker="ring_transfer_scoped_to_declared_unwrap_no_wrap_crossing_claim",
            geometry_scope=iter17["geometry_scope"],
            substrate_class=iter17["substrate_class"],
            substrate_id=iter17["movement_substrate"],
            identity_kind="coherence_basin",
            identity_surface="native_causal_pulse_substrate_surface",
            implementation_surface="native_causal_pulse_substrate_surface",
            runtime_family="LGRC9V3",
            claim_ceiling=iter17["claim_ceiling"],
            source_artifact_keys=["iter17_ring_transfer"],
            source_artifacts=records,
            source_reports=report_records,
            blocked_claims=[
                "circular_locomotion",
                "wrap_crossing_movement",
                "full_T6_general_persistence",
                "grid_transfer",
                "port_graph_transfer",
                "broad_geometry_transfer",
                "locomotion_like_behavior",
                "adaptive_topology",
                "biological_locomotion",
                "agency",
                "identity_acceptance",
                "inherited_n03_movement",
                "unrestricted_movement",
            ],
            claim_flags={
                "native_m6": iter17["achieved_movement_level"] == "M6",
                "native_m6_candidate_gate_passed": iter17["achieved_movement_level"] == "M6",
                "circular_locomotion_claim_allowed": False,
                "broad_geometry_transfer_claim_allowed": False,
            },
            persistence_level=iter17["persistence_axis"]["persistence_level"],
            persistence_basis=iter17["persistence_axis"]["persistence_basis"],
            self_renewed_cycle_count=iter17["persistence_axis"]["self_renewed_cycle_count"],
            repeatability_status=iter17["persistence_axis"]["repeatability_status"],
            recovery_status=iter17["persistence_axis"]["recovery_status"],
            cost_scaling_status="inherited_from_iteration_15_feedback_packet_cost",
            representative_cases=["s1_ring_forward_declared_unwrap", "s1_ring_reversed_declared_unwrap"],
            notes=[
                "Iteration 17 transfers the S4 corridor candidate to an S1 ring fixture under an explicit unwrap policy.",
                "The active route does not cross the unwrap seam and antipodal ties cannot promote claims.",
                "This is ring-under-policy evidence, not circular locomotion, wrap-crossing, broad geometry-transfer, or adaptive-topology evidence.",
            ],
            topology_changed_by_fixture=iter17["candidate_geometry"][
                "topology_changed_by_fixture_definition"
            ],
        ),
        _row(
            row_id="M6_s1_ring_unwrap_robust_transfer_candidate",
            evidence_class="movement_ladder_geometry_transfer",
            movement_level=iter17a["achieved_movement_level"],
            d_level=None,
            m_level_projection=None,
            projection_blocker="unwrap_robustness_not_circular_or_wrap_crossing_motion",
            geometry_scope=iter17a["geometry_scope"],
            substrate_class=iter17a["substrate_class"],
            substrate_id=iter17a["movement_substrate"],
            identity_kind="coherence_basin",
            identity_surface="native_causal_pulse_substrate_surface",
            implementation_surface="native_causal_pulse_substrate_surface",
            runtime_family="LGRC9V3",
            claim_ceiling=iter17a["claim_ceiling"],
            source_artifact_keys=["iter17a_ring_unwrap_robustness"],
            source_artifacts=records,
            source_reports=report_records,
            blocked_claims=[
                "circular_locomotion",
                "wrap_crossing_movement",
                "full_T6_general_persistence",
                "grid_transfer",
                "port_graph_transfer",
                "broad_geometry_transfer",
                "locomotion_like_behavior",
                "adaptive_topology",
                "biological_locomotion",
                "agency",
                "identity_acceptance",
                "inherited_n03_movement",
                "unrestricted_movement",
            ],
            claim_flags={
                "native_m6": iter17a["achieved_movement_level"] == "M6",
                "native_m6_candidate_gate_passed": iter17a["achieved_movement_level"] == "M6",
                "circular_locomotion_claim_allowed": False,
                "wrap_crossing_movement_claim_allowed": False,
                "broad_geometry_transfer_claim_allowed": False,
            },
            persistence_level=iter17a["persistence_axis"]["persistence_level"],
            persistence_basis=iter17a["persistence_axis"]["persistence_basis"],
            self_renewed_cycle_count=iter17a["persistence_axis"]["self_renewed_cycle_count"],
            repeatability_status=iter17a["persistence_axis"]["repeatability_status"],
            recovery_status=iter17a["persistence_axis"]["recovery_status"],
            cost_scaling_status="inherited_from_iteration_15_feedback_packet_cost",
            representative_cases=[
                "13_non_seam_unwrap_origins",
                "8_seam_intersecting_unwrap_controls",
            ],
            notes=[
                "Iteration 17-A shows the S1 ring transfer is robust across all declared unwrap origins whose seam does not intersect the active route.",
                "Seam-intersecting unwrap origins are recorded as controls and cannot promote circular or wrap-crossing claims.",
                "This improves the ring ceiling from single-unwrap evidence to unwrap-robust evidence, but circular-motion claims remain blocked.",
            ],
            topology_changed_by_fixture=True,
        ),
        _row(
            row_id="M6_s1_ring_circular_motion_evidence_candidate",
            evidence_class="movement_ladder_geometry_transfer",
            movement_level=iter17b["achieved_movement_level"],
            d_level=None,
            m_level_projection=None,
            projection_blocker="single_ring_circular_motion_evidence_not_locomotion_or_broad_transfer",
            geometry_scope=iter17b["geometry_scope"],
            substrate_class=iter17b["substrate_class"],
            substrate_id=iter17b["movement_substrate"],
            identity_kind="coherence_basin",
            identity_surface="native_causal_pulse_substrate_surface",
            implementation_surface="native_causal_pulse_substrate_surface",
            runtime_family="LGRC9V3",
            claim_ceiling=iter17b["claim_ceiling"],
            source_artifact_keys=["iter17b_circular_ring_motion"],
            source_artifacts=records,
            source_reports=report_records,
            blocked_claims=[
                "circular_locomotion",
                "full_T6_general_persistence",
                "grid_transfer",
                "port_graph_transfer",
                "broad_geometry_transfer",
                "locomotion_like_behavior",
                "adaptive_topology",
                "biological_locomotion",
                "agency",
                "identity_acceptance",
                "inherited_n03_movement",
                "unrestricted_movement",
            ],
            claim_flags={
                "native_m6": iter17b["achieved_movement_level"] == "M6",
                "native_m6_candidate_gate_passed": iter17b["achieved_movement_level"] == "M6",
                "circular_motion_evidence_candidate_gate_passed": iter17b["status"] == "passed",
                "circular_locomotion_claim_allowed": False,
                "broad_geometry_transfer_claim_allowed": False,
            },
            persistence_level=iter17b["persistence_axis"]["persistence_level"],
            persistence_basis=iter17b["persistence_axis"]["persistence_basis"],
            self_renewed_cycle_count=iter17b["persistence_axis"]["self_renewed_cycle_count"],
            repeatability_status=iter17b["persistence_axis"]["repeatability_status"],
            recovery_status=iter17b["persistence_axis"]["recovery_status"],
            cost_scaling_status="inherited_from_iteration_15_feedback_packet_cost",
            representative_cases=[
                "forward_20_to_0_wrap_route",
                "reversed_0_to_20_wrap_route",
            ],
            notes=[
                "Iteration 17-B tests seam-crossing ring response directly with a declared circular phase metric.",
                "Forward circular displacement is +1 node and reversed displacement is -1 node across the wrap edge.",
                "This is circular motion evidence on one ring fixture, not circular locomotion, broad geometry-transfer, or adaptive-topology evidence.",
            ],
            topology_changed_by_fixture=True,
        ),
        _row(
            row_id="M6_s1_ring_circular_motion_with_unwrap_robustness_closeout",
            evidence_class="movement_ladder_geometry_transfer_closeout",
            movement_level=iter17c["achieved_movement_level"],
            d_level=None,
            m_level_projection=None,
            projection_blocker="ring_series_closeout_not_broad_geometry_transfer_or_locomotion",
            geometry_scope=iter17c["geometry_scope"],
            substrate_class=iter17c["substrate_class"],
            substrate_id="S1_ring_series",
            identity_kind="coherence_basin",
            identity_surface="native_causal_pulse_substrate_surface",
            implementation_surface="native_causal_pulse_substrate_surface",
            runtime_family="LGRC9V3",
            claim_ceiling=iter17c["claim_ceiling"],
            source_artifact_keys=["iter17c_ring_geometry_closeout"],
            source_artifacts=records,
            source_reports=report_records,
            blocked_claims=[
                "circular_locomotion",
                "full_T6_general_persistence",
                "grid_transfer",
                "port_graph_transfer",
                "broad_geometry_transfer",
                "locomotion_like_behavior",
                "adaptive_topology",
                "biological_locomotion",
                "agency",
                "identity_acceptance",
                "inherited_n03_movement",
                "unrestricted_movement",
            ],
            claim_flags={
                "native_m6": iter17c["achieved_movement_level"] == "M6",
                "native_m6_candidate_gate_passed": iter17c["achieved_movement_level"] == "M6",
                "circular_motion_evidence_candidate_gate_passed": iter17c["status"] == "passed",
                "circular_locomotion_claim_allowed": False,
                "broad_geometry_transfer_claim_allowed": False,
            },
            persistence_level=iter17c["persistence_axis"]["persistence_level"],
            persistence_basis=iter17c["persistence_axis"]["persistence_basis"],
            self_renewed_cycle_count=iter17c["persistence_axis"]["self_renewed_cycle_count"],
            repeatability_status=iter17c["persistence_axis"]["repeatability_status"],
            recovery_status=iter17c["persistence_axis"]["recovery_status"],
            cost_scaling_status="inherited_from_iteration_15_feedback_packet_cost",
            representative_cases=[
                "declared_unwrap_transfer",
                "unwrap_robustness",
                "circular_wrap_route",
            ],
            notes=[
                "Iteration 17-C is a summary-only closeout of the ring series; it runs no new probe.",
                "It combines the single-unwrap, unwrap-robust, and circular wrap-route evidence into one scoped ring ceiling.",
                "The combined ceiling remains ring-only and does not promote broad geometry-transfer or locomotion-like claims.",
            ],
            topology_changed_by_fixture=True,
        ),
        _row(
            row_id="M6_s3_grid_route_defined_transfer_candidate",
            evidence_class="movement_ladder_geometry_transfer",
            movement_level=iter18["achieved_movement_level"],
            d_level=None,
            m_level_projection=None,
            projection_blocker="grid_route_defined_transfer_not_port_graph_or_adaptive_topology",
            geometry_scope=iter18["geometry_scope"],
            substrate_class=iter18["substrate_class"],
            substrate_id=iter18["movement_substrate"],
            identity_kind="coherence_basin",
            identity_surface="native_causal_pulse_substrate_surface",
            implementation_surface="native_causal_pulse_substrate_surface",
            runtime_family="LGRC9V3",
            claim_ceiling=iter18["claim_ceiling"],
            source_artifact_keys=["iter18_grid_transfer"],
            source_artifacts=records,
            source_reports=report_records,
            blocked_claims=[
                "port_graph_transfer",
                "adaptive_topology_movement",
                "topology_mutating_movement",
                "broad_geometry_transfer",
                "locomotion_like_behavior",
                "biological_locomotion",
                "agency",
                "identity_acceptance",
                "inherited_n03_movement",
                "unrestricted_movement",
            ],
            claim_flags={
                "native_m6": iter18["achieved_movement_level"] == "M6",
                "native_m6_candidate_gate_passed": iter18["achieved_movement_level"] == "M6",
                "grid_transfer_candidate_gate_passed": iter18["status"] == "passed",
                "broad_geometry_transfer_claim_allowed": False,
                "adaptive_topology_claim_allowed": False,
            },
            persistence_level=iter18["persistence_axis"]["persistence_level"],
            persistence_basis=iter18["persistence_axis"]["persistence_basis"],
            self_renewed_cycle_count=iter18["persistence_axis"]["self_renewed_cycle_count"],
            repeatability_status=iter18["persistence_axis"]["repeatability_status"],
            recovery_status=iter18["persistence_axis"]["recovery_status"],
            cost_scaling_status="inherited_from_iteration_15_feedback_packet_cost",
            representative_cases=["s3_grid_forward_east", "s3_grid_reversed_west"],
            notes=[
                "Iteration 18 transfers the ring-series ceiling to a 5x5 S3 grid with route-defined east/west front/rear masks.",
                "The grid result uses local unit route edges only and disables diagonal/route shortcuts.",
                "It has zero y-axis drift in the route-defined transfer and remains blocked from port-graph, broad geometry-transfer, and adaptive-topology claims.",
            ],
            topology_changed_by_fixture=True,
        ),
        _row(
            row_id="M6_s3_grid_two_axis_turn_candidate",
            evidence_class="movement_ladder_geometry_transfer",
            movement_level=iter18b["achieved_movement_level"],
            d_level=None,
            m_level_projection=None,
            projection_blocker="declared_two_axis_turn_not_state_gated_routing_or_port_graph",
            geometry_scope=iter18b["geometry_scope"],
            substrate_class=iter18b["substrate_class"],
            substrate_id=iter18b["movement_substrate"],
            identity_kind="coherence_basin",
            identity_surface="native_causal_pulse_substrate_surface",
            implementation_surface="native_causal_pulse_substrate_surface",
            runtime_family="LGRC9V3",
            claim_ceiling=iter18b["claim_ceiling"],
            source_artifact_keys=["iter18b_grid_two_axis_turn"],
            source_artifacts=records,
            source_reports=report_records,
            blocked_claims=[
                "state_gated_2d_routing",
                "port_graph_transfer",
                "adaptive_topology_movement",
                "topology_mutating_movement",
                "broad_geometry_transfer",
                "locomotion_like_behavior",
                "biological_locomotion",
                "agency",
                "identity_acceptance",
                "inherited_n03_movement",
                "unrestricted_movement",
            ],
            claim_flags={
                "native_m6": iter18b["achieved_movement_level"] == "M6",
                "native_m6_candidate_gate_passed": iter18b["achieved_movement_level"] == "M6",
                "grid_two_axis_turn_candidate_gate_passed": iter18b["status"] == "passed",
                "grid_state_gated_routing_claim_allowed": False,
                "broad_geometry_transfer_claim_allowed": False,
                "adaptive_topology_claim_allowed": False,
            },
            persistence_level=iter18b["persistence_axis"]["persistence_level"],
            persistence_basis=iter18b["persistence_axis"]["persistence_basis"],
            self_renewed_cycle_count=iter18b["persistence_axis"]["self_renewed_cycle_count"],
            repeatability_status=iter18b["persistence_axis"]["repeatability_status"],
            recovery_status=iter18b["persistence_axis"]["recovery_status"],
            cost_scaling_status="inherited_from_iteration_15_feedback_packet_cost",
            representative_cases=["west_to_center_to_north", "north_to_center_to_west"],
            notes=[
                "Iteration 18-B strengthens the grid result from one-axis route survival to a declared two-axis L-route turn.",
                "A committed ingress packet reaches the center on one axis, then native feedback eligibility authorizes egress on the orthogonal axis.",
                "It remains blocked from state-gated 2D routing, port-graph transfer, broad geometry-transfer, and adaptive-topology claims.",
            ],
            topology_changed_by_fixture=False,
        ),
        _row(
            row_id="M6_s3_grid_state_gated_routing_candidate",
            evidence_class="movement_ladder_geometry_transfer",
            movement_level=iter18c["achieved_movement_level"],
            d_level=None,
            m_level_projection=None,
            projection_blocker="design_prototype_external_gate_selection_not_native_geometry_driven",
            geometry_scope=iter18c["geometry_scope"],
            substrate_class=iter18c["substrate_class"],
            substrate_id=iter18c["movement_substrate"],
            identity_kind="coherence_basin",
            identity_surface="native_causal_pulse_substrate_surface",
            implementation_surface="native_causal_pulse_substrate_surface",
            runtime_family="LGRC9V3",
            claim_ceiling=iter18c["claim_ceiling"],
            source_artifact_keys=["iter18c_grid_state_gated_routing"],
            source_artifacts=records,
            source_reports=report_records,
            blocked_claims=[
                "native_geometry_driven_gate_selection",
                "port_graph_transfer",
                "adaptive_topology_movement",
                "topology_mutating_movement",
                "broad_geometry_transfer",
                "locomotion_like_behavior",
                "biological_locomotion",
                "agency",
                "identity_acceptance",
                "inherited_n03_movement",
                "unrestricted_movement",
            ],
            claim_flags={
                "native_m6": iter18c["achieved_movement_level"] == "M6",
                "native_m6_candidate_gate_passed": iter18c["achieved_movement_level"] == "M6",
                "grid_state_gated_routing_candidate_gate_passed": iter18c["status"] == "passed",
                "native_geometry_driven_gate_selection_claim_allowed": False,
                "broad_geometry_transfer_claim_allowed": False,
                "adaptive_topology_claim_allowed": False,
            },
            persistence_level=iter18c["persistence_axis"]["persistence_level"],
            persistence_basis=iter18c["persistence_axis"]["persistence_basis"],
            self_renewed_cycle_count=iter18c["persistence_axis"]["self_renewed_cycle_count"],
            repeatability_status=iter18c["persistence_axis"]["repeatability_status"],
            recovery_status=iter18c["persistence_axis"]["recovery_status"],
            cost_scaling_status="inherited_from_iteration_15_feedback_packet_cost",
            representative_cases=["west_input_selects_north", "south_input_selects_east"],
            notes=[
                "Iteration 18-C tests a fixed-topology S3 grid junction with two input gates and two output gates.",
                "Different committed ingress histories select different output gates under one serialized experiment-level design policy.",
                "Native LGRC packet work, surface rows, feedback eligibility, feedback scheduling, and artifact validation are used; native geometry-driven gate selection is not implemented yet.",
                "It remains blocked from native geometry-driven gate selection, port-graph transfer, broad geometry-transfer, and adaptive-topology claims.",
            ],
            topology_changed_by_fixture=False,
        ),
        _row(
            row_id="M6_s3_grid_geometry_scored_selection_design_prototype",
            evidence_class="movement_ladder_geometry_transfer",
            movement_level=iter18d["achieved_movement_level"],
            d_level=None,
            m_level_projection=None,
            projection_blocker="external_selection_scoring_logic_not_compositional_lgrc_choice",
            geometry_scope=iter18d["geometry_scope"],
            substrate_class=iter18d["substrate_class"],
            substrate_id=iter18d["movement_substrate"],
            identity_kind="coherence_basin",
            identity_surface="native_causal_pulse_substrate_surface",
            implementation_surface="native_causal_pulse_substrate_surface",
            runtime_family="LGRC9V3",
            claim_ceiling=iter18d["claim_ceiling"],
            source_artifact_keys=["iter18d_grid_geometry_selection"],
            source_artifacts=records,
            source_reports=report_records,
            blocked_claims=[
                "native_geometry_driven_selection",
                "selection_without_external_logic",
                "native_lgrc_choice_selection",
                "rc_identity_collapse",
                "semantic_choice",
                "agency",
                "port_graph_transfer",
                "adaptive_topology_movement",
                "topology_mutating_movement",
                "broad_geometry_transfer",
                "locomotion_like_behavior",
                "biological_locomotion",
                "identity_acceptance",
                "inherited_n03_movement",
                "unrestricted_movement",
            ],
            claim_flags={
                "native_m6": iter18d["achieved_movement_level"] == "M6",
                "native_m6_candidate_gate_passed": iter18d["achieved_movement_level"] == "M6",
                "geometry_scored_selection_design_prototype_passed": iter18d["status"] == "passed",
                "native_geometry_driven_selection_claim_allowed": False,
                "selection_without_external_logic_claim_allowed": False,
                "native_lgrc_choice_selection_claim_allowed": False,
                "rc_identity_collapse_claim_allowed": False,
                "choice_or_agency_claim_allowed": False,
                "broad_geometry_transfer_claim_allowed": False,
                "adaptive_topology_claim_allowed": False,
            },
            persistence_level=iter18d["persistence_axis"]["persistence_level"],
            persistence_basis=iter18d["persistence_axis"]["persistence_basis"],
            self_renewed_cycle_count=iter18d["persistence_axis"]["self_renewed_cycle_count"],
            repeatability_status=iter18d["persistence_axis"]["repeatability_status"],
            recovery_status=iter18d["persistence_axis"]["recovery_status"],
            cost_scaling_status="inherited_from_iteration_15_feedback_packet_cost",
            representative_cases=["north_curved_flux", "east_curved_flux"],
            notes=[
                "Iteration 18-D records a selection/collapse analogue: two output basins compete, and input flux shape resolves to the basin with stronger geometry/flux compatibility.",
                "Native LGRC packet work, surface rows, feedback scheduling, and artifact validation are used; compatibility scoring is still external experiment-level design-prototype logic.",
                "This is stricter than a missing native scheduling policy: 18-D evaluates competing output futures and suppresses the non-selected basin, so the next direction is composed 1D LGRC fork competition without external scoring.",
                "RC identity collapse, semantic choice, agency, native geometry-driven selection, native LGRC choice selection, port-graph transfer, and adaptive-topology claims remain blocked.",
            ],
            topology_changed_by_fixture=False,
        ),
        _row(
            row_id="M6_s3_grid_composed_1d_fork_competition_candidate",
            evidence_class="movement_ladder_geometry_transfer",
            movement_level=iter18e["achieved_movement_level"],
            d_level=None,
            m_level_projection=None,
            projection_blocker="native_branch_arbitration_not_supported_for_symmetric_ties",
            geometry_scope=iter18e["geometry_scope"],
            substrate_class=iter18e["substrate_class"],
            substrate_id=iter18e["movement_substrate"],
            identity_kind="coherence_basin",
            identity_surface="native_causal_pulse_substrate_surface",
            implementation_surface="native_causal_pulse_substrate_surface",
            runtime_family="LGRC9V3",
            claim_ceiling=iter18e["claim_ceiling"],
            source_artifact_keys=["iter18e_composed_1d_fork_competition"],
            source_artifacts=records,
            source_reports=report_records,
            blocked_claims=[
                "native_branch_arbitration",
                "native_lgrc_choice_selection",
                "rc_identity_collapse",
                "semantic_choice",
                "agency",
                "port_graph_transfer",
                "adaptive_topology_movement",
                "topology_mutating_movement",
                "broad_geometry_transfer",
                "locomotion_like_behavior",
                "biological_locomotion",
                "identity_acceptance",
                "inherited_n03_movement",
                "unrestricted_movement",
            ],
            claim_flags={
                "native_m6": iter18e["achieved_movement_level"] == "M6",
                "native_m6_candidate_gate_passed": iter18e["achieved_movement_level"] == "M6",
                "composed_1d_fork_competition_candidate_passed": iter18e["status"] == "passed",
                "native_branch_competition_claim_allowed": (
                    iter18e["claim_flags"]["native_branch_competition_claim_allowed"]
                ),
                "native_branch_arbitration_claim_allowed": False,
                "native_lgrc_choice_selection_claim_allowed": False,
                "rc_identity_collapse_claim_allowed": False,
                "choice_or_agency_claim_allowed": False,
                "broad_geometry_transfer_claim_allowed": False,
                "adaptive_topology_claim_allowed": False,
            },
            persistence_level=iter18e["persistence_axis"]["persistence_level"],
            persistence_basis=iter18e["persistence_axis"]["persistence_basis"],
            self_renewed_cycle_count=iter18e["persistence_axis"]["self_renewed_cycle_count"],
            repeatability_status=iter18e["persistence_axis"]["repeatability_status"],
            recovery_status=iter18e["persistence_axis"]["recovery_status"],
            cost_scaling_status="inherited_from_iteration_15_feedback_packet_cost",
            representative_cases=["north_branch_capacity_dominant", "east_branch_capacity_dominant"],
            notes=[
                "Iteration 18-E composes two native one-dimensional LGRC branch elements into a shared S3 fork without external scoring or argmax selection.",
                "Branch differentiation is native eligibility based: one branch schedules only when its local branch state passes feedback threshold and the competing branch remains subthreshold.",
                "Symmetric eligible forks expose the remaining blocker: current LGRC producer semantics do not arbitrate between two eligible branches.",
                "Native branch arbitration, native LGRC choice selection, RC identity collapse, semantic choice, agency, port-graph transfer, and adaptive-topology claims remain blocked.",
            ],
            topology_changed_by_fixture=False,
        ),
        _row(
            row_id="M6_s3_grid_balanced_local_preference_fork_candidate",
            evidence_class="movement_ladder_geometry_transfer",
            movement_level=iter18f["achieved_movement_level"],
            d_level=None,
            m_level_projection=None,
            projection_blocker="local_preference_tie_breaking_not_native_choice_or_rc_collapse",
            geometry_scope=iter18f["geometry_scope"],
            substrate_class=iter18f["substrate_class"],
            substrate_id=iter18f["movement_substrate"],
            identity_kind="coherence_basin",
            identity_surface="native_causal_pulse_substrate_surface",
            implementation_surface="native_causal_pulse_substrate_surface",
            runtime_family="LGRC9V3",
            claim_ceiling=iter18f["claim_ceiling"],
            source_artifact_keys=["iter18f_balanced_local_preference_fork"],
            source_artifacts=records,
            source_reports=report_records,
            blocked_claims=[
                "native_lgrc_choice_selection",
                "rc_identity_collapse",
                "semantic_choice",
                "agency",
                "port_graph_transfer",
                "adaptive_topology_movement",
                "topology_mutating_movement",
                "broad_geometry_transfer",
                "locomotion_like_behavior",
                "biological_locomotion",
                "identity_acceptance",
                "inherited_n03_movement",
                "unrestricted_movement",
            ],
            claim_flags={
                "native_m6": iter18f["achieved_movement_level"] == "M6",
                "native_m6_candidate_gate_passed": iter18f["achieved_movement_level"] == "M6",
                "balanced_local_preference_fork_candidate_passed": iter18f["status"] == "passed",
                "native_branch_competition_claim_allowed": (
                    iter18f["claim_flags"]["native_branch_competition_claim_allowed"]
                ),
                "balanced_local_preference_claim_allowed": (
                    iter18f["claim_flags"]["balanced_local_preference_claim_allowed"]
                ),
                "native_lgrc_choice_selection_claim_allowed": False,
                "rc_identity_collapse_claim_allowed": False,
                "choice_or_agency_claim_allowed": False,
                "broad_geometry_transfer_claim_allowed": False,
                "adaptive_topology_claim_allowed": False,
            },
            persistence_level=iter18f["persistence_axis"]["persistence_level"],
            persistence_basis=iter18f["persistence_axis"]["persistence_basis"],
            self_renewed_cycle_count=iter18f["persistence_axis"]["self_renewed_cycle_count"],
            repeatability_status=iter18f["persistence_axis"]["repeatability_status"],
            recovery_status=iter18f["persistence_axis"]["recovery_status"],
            cost_scaling_status="inherited_from_iteration_15_feedback_packet_cost",
            representative_cases=[
                "north_local_preference_tie_break",
                "east_local_preference_tie_break",
                "east_dominant_overrides_north_preference",
            ],
            notes=[
                "Iteration 18-F adds paired local epsilon preferences that break local near-ties while the global branch-preference sum remains zero.",
                "The no-preference fork still reproduces the Iteration 18-E no-arbitration blocker, and epsilon does not force a choice when both branches remain strongly eligible.",
                "This supports balanced local symmetry breaking, not native LGRC choice selection, RC identity collapse, semantic choice, or agency.",
            ],
            topology_changed_by_fixture=False,
        ),
        _row(
            row_id="M6_s3_grid_integrated_2d_composed_gate_candidate",
            evidence_class="movement_ladder_geometry_transfer",
            movement_level=iter18g["achieved_movement_level"],
            d_level=None,
            m_level_projection=None,
            projection_blocker="fixed_topology_2d_gate_not_native_choice_or_adaptive_topology",
            geometry_scope=iter18g["geometry_scope"],
            substrate_class=iter18g["substrate_class"],
            substrate_id=iter18g["movement_substrate"],
            identity_kind="coherence_basin",
            identity_surface="native_causal_pulse_substrate_surface",
            implementation_surface="native_causal_pulse_substrate_surface",
            runtime_family="LGRC9V3",
            claim_ceiling=iter18g["claim_ceiling"],
            source_artifact_keys=["iter18g_integrated_2d_composed_gate"],
            source_artifacts=records,
            source_reports=report_records,
            blocked_claims=[
                "native_lgrc_choice_selection",
                "rc_identity_collapse",
                "semantic_choice",
                "agency",
                "port_graph_transfer",
                "adaptive_topology_movement",
                "topology_mutating_movement",
                "broad_geometry_transfer",
                "locomotion_like_behavior",
                "biological_locomotion",
                "identity_acceptance",
                "inherited_n03_movement",
                "unrestricted_movement",
            ],
            claim_flags={
                "native_m6": iter18g["achieved_movement_level"] == "M6",
                "native_m6_candidate_gate_passed": iter18g["achieved_movement_level"] == "M6",
                "integrated_fixed_topology_2d_gate_candidate_passed": iter18g["status"] == "passed",
                "fixed_topology_2d_gate_claim_allowed": (
                    iter18g["claim_flags"]["fixed_topology_2d_gate_claim_allowed"]
                ),
                "native_lgrc_choice_selection_claim_allowed": False,
                "rc_identity_collapse_claim_allowed": False,
                "choice_or_agency_claim_allowed": False,
                "broad_geometry_transfer_claim_allowed": False,
                "adaptive_topology_claim_allowed": False,
            },
            persistence_level=iter18g["persistence_axis"]["persistence_level"],
            persistence_basis=iter18g["persistence_axis"]["persistence_basis"],
            self_renewed_cycle_count=iter18g["persistence_axis"]["self_renewed_cycle_count"],
            repeatability_status=iter18g["persistence_axis"]["repeatability_status"],
            recovery_status=iter18g["persistence_axis"]["recovery_status"],
            cost_scaling_status="inherited_from_iteration_15_feedback_packet_cost",
            representative_cases=["west_input", "south_input"],
            notes=[
                "Iteration 18-G integrates the 18-C two-input/two-output shape, 18-E composed 1D branch competition, and 18-F balanced local preference tie-breaking.",
                "West and south inputs select distinct output branches by native branch eligibility, not external scoring or argmax.",
                "This supports a fixed-topology 2D composed-gate candidate, not native LGRC choice selection, RC identity collapse, port-graph transfer, or adaptive topology.",
            ],
            topology_changed_by_fixture=False,
        ),
        _row(
            row_id="M6_s3_grid_series_closeout_fixed_topology_2d_gate",
            evidence_class="movement_ladder_geometry_transfer_closeout",
            movement_level=iter18h["achieved_movement_level"],
            d_level=None,
            m_level_projection=None,
            projection_blocker="fixed_topology_grid_series_not_port_graph_or_adaptive_topology",
            geometry_scope=iter18h["geometry_scope"],
            substrate_class=iter18h["substrate_class"],
            substrate_id="S3_grid_series",
            identity_kind="coherence_basin",
            identity_surface="native_causal_pulse_substrate_surface",
            implementation_surface="native_causal_pulse_substrate_surface",
            runtime_family="LGRC9V3",
            claim_ceiling=iter18h["claim_ceiling"],
            source_artifact_keys=["iter18h_s3_grid_series_closeout"],
            source_artifacts=records,
            source_reports=report_records,
            blocked_claims=iter18h["blocked_claims"],
            claim_flags=iter18h["claim_flags"],
            persistence_level=iter18h["persistence_axis"]["persistence_level"],
            persistence_basis=iter18h["persistence_axis"]["persistence_basis"],
            self_renewed_cycle_count=iter18h["persistence_axis"]["self_renewed_cycle_count"],
            repeatability_status=iter18h["persistence_axis"]["repeatability_status"],
            recovery_status=iter18h["persistence_axis"]["recovery_status"],
            cost_scaling_status="inherited_from_iteration_15_feedback_packet_cost",
            representative_cases=iter18h["s3_grid_series_summary"]["integration_path"],
            notes=[
                "Iteration 18-H is a summary-only S3 grid closeout with no new probe.",
                "It records the strongest scoped S3 ceiling as a fixed-topology 2D composed-gate candidate.",
                "Native LGRC choice selection, RC identity collapse, port-graph transfer, adaptive topology, broad geometry-transfer, and locomotion-like claims remain blocked.",
            ],
            topology_changed_by_fixture=False,
        ),
        _row(
            row_id="S7_port_graph_mapping_contract_only",
            evidence_class="port_graph_mapping_contract",
            movement_level=None,
            d_level=None,
            m_level_projection=None,
            projection_blocker="mapping_contract_no_behavior_probe",
            geometry_scope=iter19["geometry_scope"],
            substrate_class=iter19["substrate_class"],
            substrate_id=iter19["mapping_contract"]["target_fixture"],
            identity_kind="null",
            identity_surface="native_causal_pulse_substrate_surface",
            implementation_surface="native_causal_pulse_substrate_surface",
            runtime_family="LGRC9V3",
            claim_ceiling=iter19["claim_ceiling"],
            source_artifact_keys=["iter19_s7_port_graph_mapping_contract"],
            source_artifacts=records,
            source_reports=report_records,
            blocked_claims=iter19["blocked_claims"],
            claim_flags=iter19["claim_flags"],
            persistence_level="not_applicable",
            persistence_basis="mapping_contract_only",
            repeatability_status="not_applicable",
            recovery_status="not_applicable",
            cost_scaling_status="not_applicable",
            representative_cases=[
                iter19["mapping_contract"]["mapping_id"],
                "west_in",
                "south_in",
                "north_out",
                "east_out",
            ],
            notes=[
                "Iteration 19 freezes the role-based S3-to-S7 fixed-port mapping before execution.",
                "It is a contract-only row and does not promote port-graph behavior claims.",
                "Topology mutation, edge rewiring, port creation, and port deletion are disabled by default.",
            ],
            topology_changed_by_fixture=True,
        ),
        _row(
            row_id="M6_s7_fixed_port_composed_gate_candidate",
            evidence_class="movement_ladder_port_graph_transfer",
            movement_level=iter19a["achieved_movement_level"],
            d_level=None,
            m_level_projection=None,
            projection_blocker="fixed_port_graph_not_topology_mutating_or_adaptive_topology",
            geometry_scope=iter19a["geometry_scope"],
            substrate_class=iter19a["substrate_class"],
            substrate_id=iter19a["movement_substrate"],
            identity_kind="coherence_basin",
            identity_surface="native_causal_pulse_substrate_surface",
            implementation_surface="native_causal_pulse_substrate_surface",
            runtime_family="LGRC9V3",
            claim_ceiling=iter19a["claim_ceiling"],
            source_artifact_keys=["iter19a_s7_fixed_port_execution"],
            source_artifacts=records,
            source_reports=report_records,
            blocked_claims=iter19a["blocked_claims"],
            claim_flags=iter19a["claim_flags"],
            persistence_level=iter19a["persistence_axis"]["persistence_level"],
            persistence_basis=iter19a["persistence_axis"]["persistence_basis"],
            self_renewed_cycle_count=iter19a["persistence_axis"]["self_renewed_cycle_count"],
            repeatability_status=iter19a["persistence_axis"]["repeatability_status"],
            recovery_status=iter19a["persistence_axis"]["recovery_status"],
            cost_scaling_status="inherited_from_iteration_15_feedback_packet_cost",
            representative_cases=["west_in_to_north_out", "south_in_to_east_out"],
            notes=[
                "Iteration 19-A executes the S7 fixed-port mapping under topology mutation disabled.",
                "West input selects north output and south input selects east output by native branch eligibility.",
                "This is fixed-port port-graph transfer evidence, not adaptive topology or topology-mutating movement.",
            ],
            topology_changed_by_fixture=True,
        ),
        _row(
            row_id="S7_topology_lineage_adaptive_gate_blocked",
            evidence_class="topology_lineage_boundary_probe",
            movement_level=None,
            d_level=None,
            m_level_projection=None,
            projection_blocker=iter19b["primary_blocker"],
            geometry_scope=iter19b["geometry_scope"],
            substrate_class=iter19b["substrate_class"],
            substrate_id=iter19b["movement_substrate"],
            identity_kind="null",
            identity_surface="native_causal_pulse_substrate_surface",
            implementation_surface="native_causal_pulse_substrate_surface",
            runtime_family="LGRC9V3",
            claim_ceiling=iter19b["claim_ceiling"],
            source_artifact_keys=["iter19b_topology_lineage_adaptive_gate"],
            source_artifacts=records,
            source_reports=report_records,
            blocked_claims=iter19b["blocked_claims"],
            claim_flags=iter19b["claim_flags"],
            persistence_level="not_applicable",
            persistence_basis="topology_lineage_boundary_probe",
            repeatability_status="not_applicable",
            recovery_status="not_applicable",
            cost_scaling_status="not_applicable",
            representative_cases=[
                "native_lgrc3_topology_lineage_replay_passed",
                "surface_v1_rejects_lineage_transport_rows",
            ],
            notes=[
                "Iteration 19-B validates that native LGRC-3 topology lineage replay is available and budget-conserving.",
                "Adaptive topology remains blocked because causal pulse-substrate surface rows v1 require fixed_topology lineage status.",
                (
                    "The original runtime blocker is now resolved externally by "
                    "Phase 8 native causal pulse-substrate surface lineage transport."
                    if iter19b.get("primary_blocker_current_status")
                    == "resolved_externally_by_phase8_lineage_closeout"
                    else "The original runtime blocker remains unresolved in N04."
                ),
                "The current ceiling remains the Iteration 19-A fixed-port S7 candidate.",
            ],
            topology_changed_by_fixture=False,
        ),
        _row(
            row_id="S7_adaptive_topology_entry_candidate_native_surface_lineage",
            evidence_class="adaptive_topology_entry_probe",
            movement_level=None,
            d_level=None,
            m_level_projection=None,
            projection_blocker="adaptive_entry_not_topology_mutating_movement",
            geometry_scope=iter19c["geometry_scope"],
            substrate_class=iter19c["substrate_class"],
            substrate_id=iter19c["movement_substrate"],
            identity_kind="boundary_signal",
            identity_surface="native_causal_pulse_substrate_surface",
            implementation_surface="native_causal_pulse_substrate_surface",
            runtime_family="LGRC9V3",
            claim_ceiling=iter19c["claim_ceiling"],
            source_artifact_keys=["iter19c_adaptive_gate_native_surface_lineage"],
            source_artifacts=records,
            source_reports=report_records,
            blocked_claims=iter19c["blocked_claims"],
            claim_flags=iter19c["claim_flags"],
            persistence_level="not_applicable",
            persistence_basis="adaptive_topology_entry_boundary_probe",
            repeatability_status="not_applicable",
            recovery_status="not_applicable",
            cost_scaling_status="not_applicable",
            representative_cases=[
                "transported_surface_successor_control",
                "superseded_source_stale_read_control",
                "topology_only_claim_promotion_control",
            ],
            notes=[
                "Iteration 19-C reruns the 19-B adaptive-topology entry gate after Phase 8 native pulse-surface lineage support.",
                "A committed topology event transports a pulse-substrate surface row, producers read the transported digest, and artifact-only lineage replay passes.",
                "This supports adaptive-topology entry evidence only; topology-mutating movement, native LGRC choice selection, RC identity collapse, agency, and unrestricted movement remain blocked.",
            ],
            topology_changed_by_fixture=False,
        ),
        _row(
            row_id="S7_topology_mutating_movement_probe_blocked",
            evidence_class="topology_mutating_movement_boundary_probe",
            movement_level=None,
            d_level=None,
            m_level_projection=None,
            projection_blocker=iter19d["primary_blocker"],
            geometry_scope=iter19d["geometry_scope"],
            substrate_class=iter19d["substrate_class"],
            substrate_id=iter19d["movement_substrate"],
            identity_kind="boundary_signal",
            identity_surface="native_causal_pulse_substrate_surface",
            implementation_surface="native_causal_pulse_substrate_surface",
            runtime_family="LGRC9V3",
            claim_ceiling=iter19d["claim_ceiling"],
            source_artifact_keys=["iter19d_topology_mutating_movement_probe"],
            source_artifacts=records,
            source_reports=report_records,
            blocked_claims=iter19d["blocked_claims"],
            claim_flags=iter19d["claim_flags"],
            persistence_level="not_applicable",
            persistence_basis="strict_topology_mutating_movement_probe",
            repeatability_status="not_applicable",
            recovery_status="not_applicable",
            cost_scaling_status="not_applicable",
            representative_cases=[
                "transported_surface_row_emitted",
                "post_topology_packet_work_attempted",
                "packet_ledger_state_reabsorption_mismatch_after_topology_event",
            ],
            notes=[
                "Iteration 19-D attempts the stricter topology-mutating movement promotion after 19-C.",
                "Native surface lineage still transports the row and artifact-only lineage replay passes.",
                "Post-topology packet work is blocked because the packet ledger node total and active state node total diverge after collapse packet settlement.",
                "This records a required LGRC mechanism: native topology-state reabsorption must update/rebase active graph state and packet ledger totals together.",
            ],
            topology_changed_by_fixture=False,
        ),
        _row(
            row_id="S7_topology_mutating_movement_candidate_after_state_reabsorption",
            evidence_class="topology_mutating_movement_candidate",
            movement_level=None,
            d_level=None,
            m_level_projection="M6",
            projection_blocker=(
                "candidate_is_topology_mutating_not_choice_agency_or_identity_collapse"
            ),
            geometry_scope=iter19e["geometry_scope"],
            substrate_class=iter19e["substrate_class"],
            substrate_id=iter19e["movement_substrate"],
            identity_kind="boundary_signal",
            identity_surface="native_causal_pulse_substrate_surface",
            implementation_surface=iter19e["execution_surface"],
            runtime_family="LGRC9V3",
            claim_ceiling=iter19e["claim_ceiling"],
            source_artifact_keys=["iter19e_topology_mutating_after_reabsorption"],
            source_artifacts=records,
            source_reports=report_records,
            blocked_claims=iter19e["blocked_claims"],
            claim_flags=iter19e["claim_flags"],
            persistence_level="not_applicable",
            persistence_basis="strict_topology_mutating_movement_after_state_reabsorption",
            repeatability_status="not_yet_repeated",
            recovery_status="not_applicable",
            cost_scaling_status="not_measured_for_topology_mutating_lane",
            representative_cases=[
                "topology_state_reabsorption_record_emitted",
                "post_topology_packet_work_scheduled",
                "post_topology_packet_work_processed_by_step",
                "artifact_only_replay_passed",
            ],
            notes=[
                "Iteration 19-E reruns the 19-D strict topology-mutating movement gate after Phase 8 topology-state reabsorption support.",
                "A committed topology event transports the native surface row, emits a topology-state reabsorption record, and allows the coupling producer to schedule post-topology packet work from the reabsorbed transported chain.",
                "This supports a topology-mutating movement candidate only; native LGRC choice selection, RC identity collapse, agency, locomotion-like behavior, biological behavior, identity acceptance, inherited-N03 movement, and unrestricted movement remain blocked.",
            ],
            topology_changed_by_fixture=False,
        ),
        _row(
            row_id="S7_topology_mutating_repeatability_stress_boundary",
            evidence_class="topology_mutating_movement_stress_boundary",
            movement_level=None,
            d_level=None,
            m_level_projection="M6",
            projection_blocker=iter20["primary_blocker"],
            geometry_scope=iter20["geometry_scope"],
            substrate_class=iter20["substrate_class"],
            substrate_id=iter20["movement_substrate"],
            identity_kind="boundary_signal",
            identity_surface="native_causal_pulse_substrate_surface",
            implementation_surface=iter20["execution_surface"],
            runtime_family="LGRC9V3",
            claim_ceiling=iter20["claim_ceiling"],
            source_artifact_keys=["iter20_topology_mutating_repeatability_stress"],
            source_artifacts=records,
            source_reports=report_records,
            blocked_claims=iter20["blocked_claims"],
            claim_flags=iter20["claim_flags"],
            persistence_level="T5_candidate",
            persistence_basis="repeatability_reversal_perturbation_stress",
            repeatability_status="three_matched_native_runs_passed",
            recovery_status="lineage_accounted_perturbation_passed",
            cost_scaling_status="exact_node_plus_packet_budget_preserved",
            representative_cases=[
                "repeatability_forward_runs_3_of_3_passed",
                "reversed_matched_topology_mutating_lane_passed",
                "lineage_accounted_perturbation_lane_passed",
                "multi_topology_runtime_passed",
                "multi_topology_artifact_replay_passed",
            ],
            notes=[
                "Iteration 20 stresses the 19-E topology-mutating movement candidate.",
                "Repeatability, reversed-direction, and lineage-accounted perturbation lanes pass with artifact-only replay and exact node-plus-packet budget.",
                "A multiple-committed-topology-events single-run lane passes at runtime/budget level and artifact-only replay after Phase 8 time-scoped lineage replay hardening.",
                "This strengthens repeatability/stress evidence for the candidate but does not promote native choice, RC identity collapse, agency, locomotion-like behavior, biological behavior, inherited-N03 movement, or unrestricted movement.",
            ],
            topology_changed_by_fixture=False,
        ),
        _row(
            row_id="S7_native_lgrc_choice_selection_boundary_blocked",
            evidence_class="native_lgrc_choice_selection_boundary",
            movement_level=None,
            d_level=None,
            m_level_projection="M6",
            projection_blocker=iter21["primary_blocker"],
            geometry_scope=iter21["geometry_scope"],
            substrate_class=iter21["substrate_class"],
            substrate_id=iter21["movement_substrate"],
            identity_kind="boundary_signal",
            identity_surface="native_causal_pulse_substrate_surface",
            implementation_surface=iter21["execution_surface"],
            runtime_family="LGRC9V3",
            claim_ceiling=iter21["claim_ceiling"],
            source_artifact_keys=["iter21_native_lgrc_choice_selection_boundary"],
            source_artifacts=records,
            source_reports=report_records,
            blocked_claims=iter21["blocked_claims"],
            claim_flags=iter21["claim_flags"],
            persistence_level="not_applicable",
            persistence_basis="choice_selection_boundary_probe",
            repeatability_status="not_applicable",
            recovery_status="not_applicable",
            cost_scaling_status="not_applicable",
            representative_cases=[
                "route_a_executable_when_supplied",
                "route_b_executable_when_supplied",
                "native_lgrc_topology_route_selection_not_exposed",
                "local_preference_distinguished_from_native_choice",
            ],
            notes=[
                "Iteration 21 attempts to promote topology-mutating movement to native LGRC choice selection.",
                "Both competing topology-mutating continuations execute and artifact-replay when supplied.",
                "The promotion is blocked because route selection still enters through experiment-supplied topology-event arguments rather than a native LGRC route arbitrator.",
                "Deterministic local preference remains bias, not native choice, semantic choice, agency, or RC identity collapse.",
            ],
            topology_changed_by_fixture=False,
        ),
        _row(
            row_id="S7_native_route_arbitration_runtime_support",
            evidence_class="native_lgrc_route_arbitration_runtime_support",
            movement_level=None,
            d_level=None,
            m_level_projection="M6",
            projection_blocker="native_route_arbitration_is_not_semantic_choice_or_agency",
            geometry_scope=iter21b["geometry_scope"],
            substrate_class=iter21b["substrate_class"],
            substrate_id=iter21b["movement_substrate"],
            identity_kind="boundary_signal",
            identity_surface="native_causal_pulse_substrate_surface",
            implementation_surface=iter21b["execution_surface"],
            runtime_family="LGRC9V3",
            claim_ceiling=iter21b["claim_ceiling"],
            source_artifact_keys=["iter21b_native_route_arbitration_rerun"],
            source_artifacts=records,
            source_reports=report_records,
            blocked_claims=iter21b["blocked_claims"],
            claim_flags=iter21b["claim_flags"],
            persistence_level="not_applicable",
            persistence_basis="native_route_arbitration_boundary_rerun",
            repeatability_status="not_applicable",
            recovery_status="not_applicable",
            cost_scaling_status="exact_node_plus_packet_budget_preserved",
            representative_cases=[
                "candidate_route_set_emitted",
                "native_route_arbitration_record_selected_one_route",
                "selected_topology_event_from_arbitration_record",
                "artifact_only_route_arbitration_replay_passed",
                "unresolved_tie_control_blocks_selection",
                "hidden_input_control_blocks_selection",
            ],
            notes=[
                "Iteration 21-B reruns the route-selection boundary after Phase 8 native route arbitration.",
                "The old route-selection exposure blocker is resolved as runtime route arbitration: candidate routes are formed from committed runtime-visible evidence and serialized policy selects one route.",
                "The selected topology event cites the arbitration record, and artifact-only replay reconstructs the downstream lineage/reabsorption/producer/step chain.",
                "This is native route-arbitration support, not semantic choice, agency, RC identity collapse, or identity acceptance.",
            ],
            topology_changed_by_fixture=False,
        ),
        _row(
            row_id="S7_identity_through_topology_mutation_boundary_blocked",
            evidence_class="identity_through_topology_mutation_boundary",
            movement_level=None,
            d_level=None,
            m_level_projection="M6",
            projection_blocker=iter22["primary_blocker"],
            geometry_scope=iter22["geometry_scope"],
            substrate_class=iter22["substrate_class"],
            substrate_id=iter22["movement_substrate"],
            identity_kind=iter22["identity_audit"]["identity_kind_after"],
            identity_surface=iter22["identity_audit"]["identity_surface_after"],
            implementation_surface=iter22["execution_surface"],
            runtime_family="LGRC9V3",
            claim_ceiling=iter22["claim_ceiling"],
            source_artifact_keys=["iter22_identity_through_topology_mutation_boundary"],
            source_artifacts=records,
            source_reports=report_records,
            blocked_claims=iter22["blocked_claims"],
            claim_flags=iter22["claim_flags"],
            persistence_level="not_applicable",
            persistence_basis="identity_through_topology_mutation_boundary_probe",
            repeatability_status="not_applicable",
            recovery_status="not_applicable",
            cost_scaling_status="not_applicable",
            representative_cases=[
                "topology_lineage_continuity_passed",
                "reabsorbed_state_continuity_passed",
                "producer_schedules_from_current_reabsorbed_evidence",
                "artifact_only_replay_passed",
                "rc_identity_invariants_not_serialized",
            ],
            notes=[
                "Iteration 22 attempts to promote topology-mutating movement to RC identity through topology mutation.",
                "Native artifacts prove topology-aware continuity of surface evidence, active state, packet ledger, and producer scheduling.",
                "The promotion is blocked because the run does not serialize a stable RC coherence-basin identity or validate attractor-basin invariance through topology mutation.",
                "This preserves the current topology-mutating movement candidate ceiling while keeping RC identity collapse and identity acceptance blocked.",
            ],
            topology_changed_by_fixture=False,
        ),
        _row(
            row_id="S7_identity_through_native_route_arbitrated_topology_boundary_blocked",
            evidence_class="identity_through_native_route_arbitrated_topology_boundary",
            movement_level=None,
            d_level=None,
            m_level_projection="M6",
            projection_blocker=iter22b["primary_blocker"],
            geometry_scope=iter22b["geometry_scope"],
            substrate_class=iter22b["substrate_class"],
            substrate_id=iter22b["movement_substrate"],
            identity_kind=iter22b["identity_audit"]["identity_kind_after"],
            identity_surface=iter22b["identity_audit"]["identity_surface_after"],
            implementation_surface=iter22b["execution_surface"],
            runtime_family="LGRC9V3",
            claim_ceiling=iter22b["claim_ceiling"],
            source_artifact_keys=[
                "iter22b_identity_through_native_route_arbitrated_topology"
            ],
            source_artifacts=records,
            source_reports=report_records,
            blocked_claims=iter22b["blocked_claims"],
            claim_flags=iter22b["claim_flags"],
            persistence_level="not_applicable",
            persistence_basis="identity_through_native_route_arbitrated_topology_boundary_probe",
            repeatability_status="not_applicable",
            recovery_status="not_applicable",
            cost_scaling_status="not_applicable",
            representative_cases=[
                "native_selection_continuity_passed",
                "lineage_and_reabsorption_passed",
                "producer_schedules_from_current_reabsorbed_evidence",
                "route_artifact_replay_passed",
                "surface_lineage_artifact_replay_passed",
                "rc_identity_invariants_not_serialized",
            ],
            notes=[
                "Iteration 22-B reruns the identity boundary with the native route-arbitrated topology event from Iteration 21-B.",
                "Native route arbitration, selected topology event, surface lineage, topology-state reabsorption, producer scheduling, and step processing replay artifact-only.",
                "The promotion remains blocked because the run does not serialize a stable RC coherence-basin identity or validate attractor-basin invariance through topology mutation.",
                "This preserves the topology-mutating movement candidate ceiling while keeping semantic choice, agency, RC identity collapse, and identity acceptance blocked.",
            ],
            topology_changed_by_fixture=False,
        ),
        _row(
            row_id="D1_local_pulse_transport",
            evidence_class="deformation_ladder",
            movement_level=None,
            d_level="D1",
            m_level_projection=None,
            projection_blocker="pulse_transport_only",
            geometry_scope="same_fixture",
            substrate_class="chain",
            substrate_id="S0_chain_v1",
            identity_kind="null",
            identity_surface="fixed_substrate",
            implementation_surface="experiment_local",
            claim_ceiling="pulse_transport_only",
            source_artifact_keys=["d1_pulse_transport"],
            source_artifacts=records,
            source_reports=report_records,
            representative_cases=["D1_positive_local_transport"],
        ),
        _row(
            row_id="D2_local_geometry_coupling",
            evidence_class="deformation_ladder",
            movement_level=None,
            d_level="D2",
            m_level_projection="M4",
            projection_blocker="local_geometry_response_not_boundary_movement",
            geometry_scope="same_fixture",
            substrate_class="chain",
            substrate_id="S0_chain_v1",
            identity_kind="deformation_token",
            identity_surface="deformation_surface",
            implementation_surface="experiment_local",
            claim_ceiling="pulse_local_geometry_coupling",
            source_artifact_keys=["d2_local_geometry"],
            source_artifacts=records,
            source_reports=report_records,
            representative_cases=["D2_positive_local_geometry_coupling"],
        ),
        _row(
            row_id="D3_traveling_deformation_candidate",
            evidence_class="deformation_ladder",
            movement_level=None,
            d_level="D3",
            m_level_projection="M5",
            projection_blocker="deformation_surface_is_not_runtime_coherence_basin",
            geometry_scope="same_fixture",
            substrate_class="chain",
            substrate_id="S0_chain_v1",
            identity_kind="deformation_token",
            identity_surface="deformation_surface",
            implementation_surface="experiment_local",
            claim_ceiling="traveling_deformation_candidate",
            source_artifact_keys=["d3_traveling_deformation"],
            source_artifacts=records,
            source_reports=report_records,
            representative_cases=["D3_positive_traveling_deformation"],
        ),
        _row(
            row_id="D4_direction_controlled_deformation",
            evidence_class="deformation_ladder",
            movement_level=None,
            d_level="D4",
            m_level_projection="M3",
            projection_blocker="shape_profile_analog_not_runtime_m3_promotion",
            geometry_scope="same_fixture",
            substrate_class="chain",
            substrate_id="S0_chain_v1",
            identity_kind="deformation_token",
            identity_surface="deformation_surface",
            implementation_surface="experiment_local",
            claim_ceiling="direction_controlled_traveling_deformation_supported",
            source_artifact_keys=["d4_direction_controls"],
            source_artifacts=records,
            source_reports=report_records,
            representative_cases=["D4_forward", "D4_reversed"],
        ),
        _row(
            row_id="D5_deformation_surface_movement_reclassification",
            evidence_class="deformation_ladder",
            movement_level=None,
            d_level="D5",
            m_level_projection="M3",
            m_level_projection_detail=d5["movement_candidate_probe"]["m_projection"][
                "movement_level_projection"
            ],
            projection_blocker=d5["strict_movement_claim_audit"]["primary_full_claim_blocker"],
            geometry_scope="same_fixture",
            substrate_class="chain",
            substrate_id="S0_chain_v1",
            identity_kind="deformation_token",
            identity_surface="deformation_surface",
            implementation_surface="experiment_local",
            claim_ceiling=d5["claim_ceiling"],
            source_artifact_keys=["d5_reclassification"],
            source_artifacts=records,
            source_reports=report_records,
            blocked_claims=[
                "strict_runtime_coherence_basin_movement",
                "locomotion_like_behavior",
                "adaptive_topology",
                "agency",
                "identity_acceptance",
                "unrestricted_movement",
            ],
            claim_flags={"strict_runtime_coherence_basin_movement_claim_allowed": False},
            representative_cases=[d5["d_level_classification"]["d_level_label"]],
            notes=[
                "D5 is first-class deformation evidence, not runtime coherence-basin movement.",
                f"Source projection: {d5['movement_candidate_probe']['m_projection']['movement_level_projection']}",
            ],
        ),
        _row(
            row_id="C_feedback_coupled_self_renewal_candidate",
            evidence_class="feedback_support",
            movement_level=None,
            d_level=None,
            m_level_projection="M6",
            projection_blocker="experiment_local_feedback_not_native_claim",
            geometry_scope="same_fixture",
            substrate_class="chain",
            substrate_id="S0_chain_v1",
            identity_kind="boundary_signal",
            identity_surface="boundary_fixture",
            implementation_surface="experiment_local",
            claim_ceiling=data["lane_c_feedback"]["claim_ceiling"],
            source_artifact_keys=["lane_c_feedback"],
            source_artifacts=records,
            source_reports=report_records,
            persistence_level="T5_candidate",
            persistence_basis="experiment_local_feedback_renewed_cycles",
            self_renewed_cycle_count=min(
                data["lane_c_feedback"]["candidate_summary"][
                    "forward_self_renewed_cycle_count"
                ],
                data["lane_c_feedback"]["candidate_summary"][
                    "reversed_self_renewed_cycle_count"
                ],
            ),
            repeatability_status="experiment_local_three_feedback_renewed_cycles",
            cost_scaling_status="bounded_cost_measured_in_lane_c_artifact",
            representative_cases=["feedback_coupled_regeneration"],
        ),
        _row(
            row_id="E_hybrid_causal_pulse_substrate_surface",
            evidence_class="surface_support",
            movement_level=None,
            d_level=None,
            m_level_projection=None,
            projection_blocker="hybrid_surface_contract_not_native_movement_claim",
            geometry_scope="same_fixture",
            substrate_class="chain",
            substrate_id="S0_chain_v1",
            identity_kind="null",
            identity_surface="native_causal_pulse_substrate_surface",
            implementation_surface="native_lgrc_telemetry",
            claim_ceiling=data["lane_e_hybrid_surface"]["claim_ceiling"],
            source_artifact_keys=["lane_e_hybrid_surface", "lane_c_feedback_surface"],
            source_artifacts=records,
            source_reports=report_records,
            runtime_family="hybrid_lgrc9v3_existing_artifacts_plus_experiment_local_surface_driver",
            representative_cases=["hybrid_surface_contract", "lane_c_feedback_compatibility"],
        ),
        _row(
            row_id="F_native_causal_pulse_substrate_surface_support",
            evidence_class="native_surface_support",
            movement_level=None,
            d_level=None,
            m_level_projection=None,
            projection_blocker="native_surface_support_is_not_a_movement_claim",
            geometry_scope="same_fixture",
            substrate_class="chain",
            substrate_id="S0_chain_v1",
            identity_kind="null",
            identity_surface="native_causal_pulse_substrate_surface",
            implementation_surface="native_causal_pulse_substrate_surface",
            claim_ceiling=data["lane_f_native_surface"]["claim_ceiling"],
            source_artifact_keys=["lane_f_native_surface"],
            source_artifacts=records,
            source_reports=report_records,
            runtime_family="LGRC9V3",
            representative_cases=["native_lgrc_lane_f_surface_bridge"],
        ),
    ]


def _validate_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    movement_levels = {row["movement_level"] for row in rows if row["movement_level"]}
    d_levels = {row["d_level"] for row in rows if row["d_level"]}
    row_ids = {row["row_id"] for row in rows}
    substrate_classes = {"chain", "corridor", "ring", "grid", "port_graph"}
    return {
        "all_m0_m6_present": all(f"M{i}" in movement_levels for i in range(7)),
        "d1_d5_present": all(f"D{i}" in d_levels for i in range(1, 6)),
        "d_rows_have_projection_fields": all(
            row["m_level_projection"] is not None and row["projection_blocker"]
            for row in rows
            if row["d_level"] in {"D2", "D3", "D4", "D5"}
        ),
        "identity_kind_surface_split_present": all(
            "identity_kind" in row and "identity_surface" in row for row in rows
        ),
        "substrate_class_values_declared": all(
            row["substrate_class"] in substrate_classes for row in rows
        ),
        "all_rows_have_sources": all(row["source_artifacts"] for row in rows),
        "all_rows_have_source_reports": all(row["source_reports"] for row in rows),
        "all_rows_have_claim_ceiling": all(bool(row["claim_ceiling"]) for row in rows),
        "all_rows_have_row_specific_claim_flags": all(row["claim_flags"] for row in rows),
        "all_rows_have_persistence_fields": all(
            "persistence_level" in row
            and "repeatability_status" in row
            and "recovery_status" in row
            and "cost_scaling_status" in row
            for row in rows
        ),
        "visual_references_are_not_evidence_sources": all(
            row["visual_is_evidence_source"] is False for row in rows
        ),
        "no_unrestricted_claims_promoted": all(
            "unrestricted_movement" in row["blocked_claims"] for row in rows
        ),
        "no_persistence_t6_claimed": all(
            row["persistence_level"] != "T6" for row in rows
        ),
        "m6_scoped_to_same_fixture_chain": any(
            row["row_id"] == "M6_native_same_fixture_self_renewal_candidate"
            and row["movement_level"] == "M6"
            and row["geometry_scope"] == "same_fixture"
            and row["substrate_class"] == "chain"
            and row["claim_ceiling"] == "native_m6_same_fixture_self_renewal_candidate"
            and row["claim_flags"]["movement_claim_allowed"] is False
            and row["claim_flags"]["locomotion_like_claim_allowed"] is False
            and row["claim_flags"]["adaptive_topology_entry_allowed"] is False
            for row in rows
        ),
        "d5_blocked_from_runtime_basin_movement": any(
            row["row_id"] == "D5_deformation_surface_movement_reclassification"
            and row["identity_kind"] == "deformation_token"
            and row["identity_surface"] == "deformation_surface"
            and row["projection_blocker"]
            == "deformation_surface_is_not_runtime_coherence_basin"
            and row["claim_flags"][
                "strict_runtime_coherence_basin_movement_claim_allowed"
            ]
            is False
            for row in rows
        ),
        "lane_c_d_e_supporting_rows_present": all(
            row_id in row_ids
            for row_id in {
                "C_feedback_coupled_self_renewal_candidate",
                "D5_deformation_surface_movement_reclassification",
                "E_hybrid_causal_pulse_substrate_surface",
            }
        ),
        "m6_resilience_extension_rows_present": all(
            row_id in row_ids
            for row_id in {
                "M6_s0_perturbation_tolerance_profile",
                "M6_shock_resistant_same_family_geometry_recovery_candidate",
                "M6_large_shock_absorber_same_family_recovery_candidate",
            }
        ),
        "iter16_corridor_transfer_row_present": (
            "M6_s4_corridor_transfer_candidate" in row_ids
        ),
        "iter16b_corridor_perturbation_row_present": (
            "M6_s4_corridor_perturbation_envelope" in row_ids
        ),
        "iter16c_high_shock_capacity_row_present": (
            "M6_s4_corridor_high_shock_capacity_requirement" in row_ids
        ),
        "iter17_ring_transfer_row_present": (
            "M6_s1_ring_declared_unwrap_transfer_candidate" in row_ids
        ),
        "iter17a_ring_unwrap_robustness_row_present": (
            "M6_s1_ring_unwrap_robust_transfer_candidate" in row_ids
        ),
        "iter17b_circular_ring_motion_row_present": (
            "M6_s1_ring_circular_motion_evidence_candidate" in row_ids
        ),
        "iter17c_ring_geometry_closeout_row_present": (
            "M6_s1_ring_circular_motion_with_unwrap_robustness_closeout" in row_ids
        ),
        "iter18_grid_transfer_row_present": (
            "M6_s3_grid_route_defined_transfer_candidate" in row_ids
        ),
        "iter18b_grid_two_axis_turn_row_present": (
            "M6_s3_grid_two_axis_turn_candidate" in row_ids
        ),
        "iter18c_grid_state_gated_routing_row_present": (
            "M6_s3_grid_state_gated_routing_candidate" in row_ids
        ),
        "iter18d_grid_geometry_selection_row_present": (
            "M6_s3_grid_geometry_scored_selection_design_prototype" in row_ids
        ),
        "iter18e_composed_1d_fork_competition_row_present": (
            "M6_s3_grid_composed_1d_fork_competition_candidate" in row_ids
        ),
        "iter18f_balanced_local_preference_fork_row_present": (
            "M6_s3_grid_balanced_local_preference_fork_candidate" in row_ids
        ),
        "iter18g_integrated_2d_composed_gate_row_present": (
            "M6_s3_grid_integrated_2d_composed_gate_candidate" in row_ids
        ),
        "iter18h_s3_grid_series_closeout_row_present": (
            "M6_s3_grid_series_closeout_fixed_topology_2d_gate" in row_ids
        ),
        "iter19c_adaptive_topology_entry_row_present": (
            "S7_adaptive_topology_entry_candidate_native_surface_lineage" in row_ids
        ),
        "iter19d_topology_mutating_movement_boundary_row_present": (
            "S7_topology_mutating_movement_probe_blocked" in row_ids
        ),
        "iter19e_topology_mutating_movement_candidate_row_present": (
            "S7_topology_mutating_movement_candidate_after_state_reabsorption"
            in row_ids
        ),
        "iter20_topology_mutating_repeatability_stress_row_present": (
            "S7_topology_mutating_repeatability_stress_boundary" in row_ids
        ),
        "iter21_native_lgrc_choice_selection_boundary_row_present": (
            "S7_native_lgrc_choice_selection_boundary_blocked" in row_ids
        ),
        "iter21b_native_route_arbitration_support_row_present": (
            "S7_native_route_arbitration_runtime_support" in row_ids
        ),
        "fixture_topology_change_distinguished_from_runtime_topology": any(
            row["row_id"] == "M6_large_shock_absorber_same_family_recovery_candidate"
            and row["topology_changed_by_fixture"] is True
            and row["topology_mutating_evidence"] is False
            and row["claim_flags"]["adaptive_topology_entry_allowed"] is False
            for row in rows
        ),
        "iter22_identity_through_topology_mutation_boundary_row_present": (
            "S7_identity_through_topology_mutation_boundary_blocked" in row_ids
        ),
        "iter22b_identity_through_native_route_arbitrated_topology_boundary_row_present": (
            "S7_identity_through_native_route_arbitrated_topology_boundary_blocked"
            in row_ids
        ),
    }


def build_inventory() -> dict[str, Any]:
    data = {key: _load_json(path) for key, path in ARTIFACTS.items()}
    records = {key: _artifact_record(path) for key, path in ARTIFACTS.items()}
    report_records = {key: _artifact_record(path) for key, path in REPORTS.items()}
    visual_records = {key: _artifact_record(path) for key, path in VISUAL_REFERENCES.items()}
    rows = _inventory_rows(data, records)
    checks = _validate_rows(rows)
    return {
        "schema": "movement_ladder_report_v1",
        "report_kind": "n04_taxonomy_inventory_v1",
        "iteration": "13",
        "status": "passed" if all(checks.values()) else "failed",
        "purpose": "taxonomy_inventory_no_new_probes_no_claim_promotion",
        "claim_ceiling": "taxonomy_inventory_only",
        "tag_schema": {
            "movement_level": ["M0", "M1", "M2", "M3", "M4", "M5", "M6"],
            "geometry_scope": [
                "same_fixture",
                "transferred_geometry",
                "port_graph_mapping_contract",
                "topology_lineage_probe",
                "topology_mutating",
            ],
            "substrate_class": ["chain", "corridor", "ring", "grid", "port_graph"],
            "identity_kind": ["coherence_basin", "deformation_token", "boundary_signal", "null"],
            "identity_surface": [
                "fixed_substrate",
                "boundary_fixture",
                "deformation_surface",
                "native_causal_pulse_substrate_surface",
            ],
            "implementation_surface": [
                "experiment_local",
                "mapped_e3_fixture",
                "native_lgrc_telemetry",
                "native_causal_pulse_substrate_surface",
                "native_causal_pulse_substrate_surface_plus_topology_state_reabsorption",
                "native_route_arbitration_plus_surface_lineage_and_topology_state_reabsorption",
            ],
            "d_level": ["D0", "D1", "D2", "D3", "D4", "D5", None],
            "m_level_projection": ["M0", "M1", "M2", "M3", "M4", "M5", "M6", None],
            "persistence_level": [
                "not_applicable",
                "not_measured",
                "T0",
                "T1",
                "T2",
                "T3",
                "T4",
                "T5",
                "T5_candidate",
                "T6",
                "T6_candidate",
                "tested_negative",
            ],
        },
        "visual_reference_policy": {
            "visuals_are_evidence_sources": False,
            "interpretation": (
                "Visual reference artifacts may be used for sharing and review, "
                "but taxonomy rows are sourced from output JSON/report artifacts."
            ),
        },
        "checks": checks,
        "counts": {
            "inventory_rows": len(rows),
            "movement_rows": sum(1 for row in rows if row["movement_level"]),
            "deformation_rows": sum(1 for row in rows if row["d_level"]),
            "supporting_rows": sum(
                1
                for row in rows
                if row["evidence_class"] in {"feedback_support", "surface_support", "native_surface_support"}
            ),
        },
        "inventory_rows": rows,
        "source_artifacts": records,
        "source_reports": report_records,
        "supporting_visual_references": visual_records,
        "command": COMMAND,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
        },
        "git": {
            "status_short": _run_git(["status", "--short"]),
            "head": _run_git(["rev-parse", "HEAD"]),
        },
        "next_iteration": "14_class_separation_and_tag_freeze",
    }


def write_report(report: dict[str, Any]) -> None:
    lines = [
        "# N04 Iteration 13 Taxonomy Inventory",
        "",
        f"Status: **{report['status']}**",
        "",
        f"Claim ceiling: `{report['claim_ceiling']}`",
        "",
        "Iteration 13 inventories existing evidence only. It does not run new probes and does not promote claims.",
        "",
        "## Checks",
        "",
    ]
    for key, value in report["checks"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(
        [
            "",
            "## Counts",
            "",
        ]
    )
    for key, value in report["counts"].items():
        lines.append(f"- `{key}`: `{value}`")
    m6_extension_rows = [
        row
        for row in report["inventory_rows"]
        if row["evidence_class"] == "movement_ladder_resilience_extension"
    ]
    if m6_extension_rows:
        lines.extend(
            [
                "",
                "## M6 Resilience Extensions",
                "",
                "Iterations 15-C/15-D/15-E extend the M taxonomy with source-backed resilience rows. They do not promote broad geometry-transfer, locomotion-like, adaptive-topology, agency, biology, identity-acceptance, inherited-N03, or unrestricted movement claims.",
                "",
                "| Row | Persistence | Geometry scope | Recovery status | Claim ceiling |",
                "|---|---|---|---|---|",
            ]
        )
        for row in m6_extension_rows:
            lines.append(
                "| "
                + " | ".join(
                    [
                        f"`{row['row_id']}`",
                        f"`{row['persistence_level']}`",
                        f"`{row['geometry_scope']}`",
                        f"`{row['recovery_status']}`",
                        f"`{row['claim_ceiling']}`",
                    ]
                )
                + " |"
            )
    lines.extend(
        [
            "",
            "## Inventory",
            "",
            "| Row | M | D | Projection | Persistence | Identity | Surface | Claim ceiling |",
            "|---|---:|---:|---:|---|---|---|---|",
        ]
    )
    for row in report["inventory_rows"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{row['row_id']}`",
                    f"`{row['movement_level']}`",
                    f"`{row['d_level']}`",
                    f"`{row['m_level_projection']}`",
                    f"`{row['persistence_level']}`",
                    f"`{row['identity_kind']}`",
                    f"`{row['identity_surface']}`",
                    f"`{row['claim_ceiling']}`",
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Source Artifacts",
            "",
        ]
    )
    for key, record in report["source_artifacts"].items():
        lines.append(f"- `{key}`: `{record['path']}`")
    lines.extend(
        [
            "",
            "## Source Reports",
            "",
        ]
    )
    for key, record in report["source_reports"].items():
        lines.append(f"- `{key}`: `{record['path']}`")
    lines.extend(
        [
            "",
            "## Supporting Visual References",
            "",
            "Visuals are review/share references only and are not evidence sources.",
            "",
        ]
    )
    for key, record in report["supporting_visual_references"].items():
        lines.append(f"- `{key}`: `{record['path']}`")
    lines.extend(["", "## Command", "", f"```bash\n{COMMAND}\n```", ""])
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    report = build_inventory()
    OUTPUT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report(report)
    if report["status"] != "passed":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Freeze N04 taxonomy tag schema and class-separation rules.

Iteration 14 consumes the Iteration 13 inventory. It freezes interpretation
boundaries before geometry-transfer probes and does not run new movement probes.
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
INVENTORY_PATH = N04 / "outputs/n04_taxonomy_inventory_v1.json"
OUTPUT_PATH = N04 / "outputs/n04_taxonomy_tag_schema_v1.json"
REPORT_PATH = N04 / "reports/n04_taxonomy_class_separation_v1.md"
COMMAND = (
    ".venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/"
    "scripts/build_n04_taxonomy_tag_schema_v1.py"
)


ORTHOGONAL_TAXONOMIES = {
    "identity_continuity_level": [f"I{i}" for i in range(7)] + ["not_measured", "not_applicable"],
    "front_rear_level": [f"R{i}" for i in range(7)] + ["not_measured", "not_applicable"],
    "boundary_level": [f"B{i}" for i in range(7)] + ["not_measured", "not_applicable"],
    "shape_level": [f"G{i}" for i in range(7)] + ["not_measured", "not_applicable"],
    "environment_level": [f"E{i}" for i in range(7)] + ["not_measured", "not_applicable"],
    "highway_level": [f"H{i}" for i in range(7)] + ["not_measured", "not_applicable"],
    "budget_economy_level": [f"Q{i}" for i in range(7)] + ["not_measured", "not_applicable"],
    "feedback_level": [f"F{i}" for i in range(7)] + ["not_measured", "not_applicable"],
}

PERSISTENCE_LEVELS = [
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
]


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _artifact_record(path: Path) -> dict[str, str]:
    return {"path": _rel(path), "sha256": _sha256(path)}


def _load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return data


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


def _separation_rules() -> list[dict[str, Any]]:
    return [
        {
            "rule_id": "centroid_displacement_not_identity_movement",
            "separates": ["M1_apparent_centroid_displacement", "identity_preserving_movement"],
            "required_tags": {
                "movement_level": "M1",
                "identity_kind": "coherence_basin",
                "claim_ceiling": "apparent_centroid_displacement_only",
            },
            "blocked_promotions": [
                "identity_preserving_displacement",
                "movement_claim_allowed",
                "locomotion_like_claim_allowed",
            ],
            "current_inventory_note": (
                "Current M1 rows are classifier/observable-fixture controls, not "
                "empirical native runtime movement lanes."
            ),
        },
        {
            "rule_id": "boundary_response_not_basin_movement",
            "separates": ["boundary_signal", "coherence_basin_movement"],
            "required_tags": {
                "identity_kind": "boundary_signal",
                "identity_surface": "boundary_fixture",
            },
            "blocked_promotions": [
                "runtime_coherence_basin_movement",
                "locomotion_like_claim_allowed",
                "adaptive_topology_entry_allowed",
            ],
            "current_inventory_note": (
                "M4/M5 boundary-response rows are real boundary-fixture evidence, "
                "but remain separate from basin-identity movement."
            ),
        },
        {
            "rule_id": "traveling_deformation_not_runtime_basin",
            "separates": ["deformation_token", "runtime_coherence_basin_identity"],
            "required_tags": {
                "identity_kind": "deformation_token",
                "identity_surface": "deformation_surface",
            },
            "blocked_promotions": [
                "strict_runtime_coherence_basin_movement",
                "identity_acceptance_claim_allowed",
            ],
            "current_inventory_note": (
                "Lane D rows stay first-class deformation evidence and cannot "
                "be collapsed into M-level basin movement."
            ),
        },
        {
            "rule_id": "same_fixture_self_renewal_not_locomotion",
            "separates": ["same_fixture_self_renewal", "locomotion_like_movement"],
            "required_tags": {
                "movement_level": "M6",
                "geometry_scope": "same_fixture",
                "persistence_level": "T5_candidate",
            },
            "blocked_promotions": [
                "locomotion_like_claim_allowed",
                "adaptive_topology_entry_allowed",
                "unrestricted_movement_claim_allowed",
            ],
            "current_inventory_note": (
                "Current M6 is bounded native same-fixture S0 evidence. It is "
                "not topology transfer, adaptive topology, or locomotion-like behavior."
            ),
        },
        {
            "rule_id": "fixed_topology_not_topology_mutating",
            "separates": ["fixed_topology_evidence", "adaptive_topology_movement"],
            "required_tags": {
                "geometry_scope": "same_fixture",
            },
            "blocked_promotions": [
                "topology_mutating_movement",
                "adaptive_topology_entry_allowed",
            ],
            "current_inventory_note": (
                "All Iteration 13 rows remain fixed-topology/same-fixture evidence "
                "until Iterations 16-19 explicitly transfer geometry or open topology controls."
            ),
        },
    ]


def _d_to_m_projection_rules() -> list[dict[str, Any]]:
    return [
        {
            "d_level": "D0",
            "projection": "M0",
            "entry_gate": "no_deformation_no_movement",
            "promotion_allowed": False,
            "blocker": "no_deformation",
        },
        {
            "d_level": "D1",
            "projection": None,
            "entry_gate": "local_pulse_transport_only",
            "promotion_allowed": False,
            "blocker": "no_boundary_coordination",
        },
        {
            "d_level": "D2",
            "projection": "M4",
            "entry_gate": "boundary_coordination_required",
            "promotion_allowed": "candidate_only",
            "blocker": "local_geometry_response_not_boundary_movement",
        },
        {
            "d_level": "D3",
            "projection": "M5",
            "entry_gate": "direction_parity_required",
            "promotion_allowed": "candidate_only",
            "blocker": "deformation_surface_is_not_runtime_coherence_basin",
        },
        {
            "d_level": "D4",
            "projection": "M3_shape_gate_analog",
            "entry_gate": "shape_profile_envelope_preserved",
            "promotion_allowed": False,
            "blocker": "shape_profile_analog_not_direct_m3_promotion",
        },
        {
            "d_level": "D5",
            "projection": "M5_style_control_evidence",
            "entry_gate": "controls_survive_and_replayable",
            "promotion_allowed": False,
            "blocker": "deformation_token_not_runtime_coherence_basin",
        },
    ]


def _implementation_surface_notes() -> dict[str, Any]:
    return {
        "mapped_e3_fixture": {
            "used_by": ["M4_boundary_coupled_response_fixture"],
            "meaning": (
                "E3 telemetry is mapped into the S0 boundary fixture to validate "
                "state-mediated boundary coupling."
            ),
            "claim_limit": "fixture_validation_not_native_runtime_movement",
        },
        "native_lgrc_telemetry": {
            "used_by": ["M5_direction_parity_boundary_response"],
            "meaning": (
                "Native forward and reversed E3 telemetry provide direction "
                "parity evidence for repeated boundary response."
            ),
            "claim_limit": "direction_parity_boundary_response_not_locomotion",
        },
        "native_causal_pulse_substrate_surface": {
            "used_by": [
                "M6_native_same_fixture_self_renewal_candidate",
                "F_native_causal_pulse_substrate_surface_support",
            ],
            "meaning": (
                "Native surface/producers provide same-fixture feedback-renewed "
                "pulse evidence under artifact validation."
            ),
            "claim_limit": "same_fixture_self_renewal_not_adaptive_topology",
        },
        "native_causal_pulse_substrate_surface_plus_topology_state_reabsorption": {
            "used_by": [
                "S7_topology_mutating_movement_candidate_after_state_reabsorption",
                "S7_topology_mutating_repeatability_stress_boundary",
                "S7_identity_through_topology_mutation_boundary_blocked",
            ],
            "meaning": (
                "Native surface lineage and topology-state reabsorption provide "
                "topology-mutating packet/surface/state continuity."
            ),
            "claim_limit": "topology_mutating_movement_candidate_not_identity_or_choice",
        },
        "native_route_arbitration_plus_surface_lineage_and_topology_state_reabsorption": {
            "used_by": [
                "S7_native_route_arbitration_runtime_support",
                "S7_identity_through_native_route_arbitrated_topology_boundary_blocked",
            ],
            "meaning": (
                "Native route arbitration selects one topology-mutating route "
                "from committed runtime-visible evidence, then consumes the "
                "selected event through lineage, reabsorption, producers, and step."
            ),
            "claim_limit": "native_route_arbitration_not_semantic_choice_or_identity_acceptance",
        },
    }


def _claim_boundary_rules() -> list[dict[str, Any]]:
    return [
        {
            "rule_id": "tags_are_descriptors_not_claims",
            "rule": (
                "Taxonomy tags describe evidence surfaces and gates. They do "
                "not set movement, locomotion, adaptive-topology, agency, "
                "biology, or identity-acceptance claim flags."
            ),
        },
        {
            "rule_id": "blocked_claims_are_row_local",
            "rule": (
                "A row may inherit global blocked claims, but stronger evidence "
                "in one row does not unblock claims in another row."
            ),
        },
        {
            "rule_id": "visual_references_are_not_sources",
            "rule": (
                "Visual reference artifacts may support review, but cannot be "
                "used as source_artifacts for taxonomy evidence rows."
            ),
        },
        {
            "rule_id": "m6_same_fixture_requires_locomotion_block",
            "rule": (
                "A same_fixture M6 row must keep locomotion-like, adaptive "
                "topology, and unrestricted movement claims blocked unless a "
                "later closeout explicitly opens them."
            ),
        },
        {
            "rule_id": "deformation_token_blocks_strict_movement",
            "rule": (
                "A deformation_token row on deformation_surface cannot allow "
                "strict runtime coherence-basin movement."
            ),
        },
    ]


def _invalid_combinations() -> list[dict[str, Any]]:
    return [
        {
            "case_id": "deformation_token_strict_movement_claim",
            "combination": {
                "identity_kind": "deformation_token",
                "strict_runtime_coherence_basin_movement_claim_allowed": True,
            },
            "expected": "invalid",
            "primary_blocker": "deformation_token_not_runtime_coherence_basin",
        },
        {
            "case_id": "d5_deformation_without_projection_blocker",
            "combination": {
                "d_level": "D5",
                "identity_kind": "deformation_token",
                "projection_blocker": None,
                "strict_runtime_coherence_basin_movement_claim_allowed": True,
            },
            "expected": "invalid",
            "primary_blocker": "d5_requires_runtime_basin_blocker",
        },
        {
            "case_id": "same_fixture_m6_locomotion_claim",
            "combination": {
                "movement_level": "M6",
                "geometry_scope": "same_fixture",
                "locomotion_like_claim_allowed": True,
            },
            "expected": "invalid_without_later_closeout",
            "primary_blocker": "same_fixture_self_renewal_not_locomotion",
        },
        {
            "case_id": "adaptive_topology_claim_without_topology_scope",
            "combination": {
                "geometry_scope": "same_fixture",
                "claim_ceiling": "adaptive_topology_movement_supported",
                "adaptive_topology_entry_allowed": True,
            },
            "expected": "invalid",
            "primary_blocker": "fixed_topology_not_topology_mutating",
        },
        {
            "case_id": "visual_reference_as_source_artifact",
            "combination": {
                "source_artifact_kind": "visual_reference",
                "visual_is_evidence_source": True,
            },
            "expected": "invalid",
            "primary_blocker": "visual_reference_not_authoritative",
        },
    ]


def _validate_current_rows_against_boundaries(rows: list[dict[str, Any]]) -> dict[str, bool]:
    return {
        "no_deformation_token_strict_movement_claims": all(
            not (
                row["identity_kind"] == "deformation_token"
                and row["claim_flags"].get(
                    "strict_runtime_coherence_basin_movement_claim_allowed"
                )
                is True
            )
            for row in rows
        ),
        "same_fixture_m6_locomotion_blocked": all(
            not (
                row["movement_level"] == "M6"
                and row["geometry_scope"] == "same_fixture"
                and row["claim_flags"].get("locomotion_like_claim_allowed") is True
            )
            for row in rows
        ),
        "topology_claims_require_topology_scope": all(
            not (
                row["geometry_scope"]
                not in {"topology_mutating", "topology_lineage_probe"}
                and row["claim_flags"].get("adaptive_topology_entry_allowed") is True
            )
            for row in rows
        ),
        "visuals_not_used_as_source_artifacts": all(
            row.get("visual_is_evidence_source") is False for row in rows
        ),
        "claim_ceilings_unchanged_from_inventory": True,
    }


def _row_tags(row: dict[str, Any]) -> dict[str, Any]:
    # Iteration 14 freezes fields and conservative status. It does not backfill
    # unmeasured taxonomy levels from prose or visuals.
    tags = {
        "row_id": row["row_id"],
        "movement_level": row["movement_level"],
        "d_level": row["d_level"],
        "m_level_projection": row["m_level_projection"],
        "geometry_scope": row["geometry_scope"],
        "topology_changed_by_fixture": row.get("topology_changed_by_fixture", False),
        "topology_mutating_evidence": row.get("topology_mutating_evidence", False),
        "substrate_class": row["substrate_class"],
        "identity_kind": row["identity_kind"],
        "identity_surface": row["identity_surface"],
        "implementation_surface": row["implementation_surface"],
        "persistence_level": row["persistence_level"],
        "persistence_basis": row.get("persistence_basis"),
        "self_renewed_cycle_count": row.get("self_renewed_cycle_count"),
        "repeatability_status": row.get("repeatability_status"),
        "recovery_status": row.get("recovery_status"),
        "cost_scaling_status": row.get("cost_scaling_status"),
        "claim_ceiling": row["claim_ceiling"],
        "source_artifact_paths": [
            record["path"] for record in row.get("source_artifacts", [])
        ],
        "source_report_paths": [
            record["path"] for record in row.get("source_reports", [])
        ],
    }
    for field in ORTHOGONAL_TAXONOMIES:
        if field == "identity_continuity_level":
            tags[field] = "not_measured"
        elif field == "feedback_level" and row["persistence_level"] == "T5_candidate":
            tags[field] = "not_measured"
        elif field == "budget_economy_level" and row["row_id"].startswith("C_"):
            tags[field] = "Q4"
        else:
            tags[field] = "not_measured"
    if row["movement_level"] == "M0":
        tags["front_rear_level"] = "R0"
        tags["boundary_level"] = "B0"
        tags["feedback_level"] = "not_applicable"
        tags["identity_continuity_level"] = "not_applicable"
    if row["movement_level"] == "M1":
        tags["identity_continuity_level"] = "I1"
    if row["movement_level"] in {"M2", "M3"}:
        tags["identity_continuity_level"] = "I3"
    if row["movement_level"] == "M6" and row["identity_kind"] == "coherence_basin":
        tags["identity_continuity_level"] = "I3"
        tags["feedback_level"] = "F2"
        tags["feedback_level_note"] = (
            "F2 is used conservatively: native feedback eligibility triggers "
            "regenerated pulse work from state. F5 remains blocked because "
            "closed locomotion-like cycle claims are not allowed."
        )
        tags["budget_economy_level"] = "not_measured"
        tags["front_rear_level"] = "not_measured"
        tags["boundary_level"] = "not_measured"
    if row["row_id"] == "M6_native_same_fixture_self_renewal_candidate":
        tags["identity_continuity_level"] = "I3"
        tags["feedback_level"] = "F2"
        tags["feedback_level_note"] = (
            "F2 is used conservatively: native feedback eligibility triggers "
            "regenerated pulse work from state. F5 remains blocked because "
            "closed locomotion-like cycle claims are not allowed."
        )
        tags["budget_economy_level"] = "not_measured"
        tags["front_rear_level"] = "not_measured"
        tags["boundary_level"] = "not_measured"
    if row["row_id"] == "M6_s0_perturbation_tolerance_profile":
        tags["front_rear_level"] = "R6" if row["recovery_status"].startswith("t6_") else "not_measured"
        tags["feedback_level_note"] = (
            "Plain S0 preserves native feedback scheduling but tests negative "
            "for T6 perturbation recovery; R6 polarity recovers only across a "
            "limited small-shock range."
        )
    if row["row_id"] == "M6_shock_resistant_same_family_geometry_recovery_candidate":
        tags["front_rear_level"] = "R6"
        tags["feedback_level_note"] = (
            "Source-reservoir same-family geometry recovers the first positive "
            "S0 T6-failing perturbation but does not recover the 0.15 T6 "
            "centroid-restoration stress."
        )
    if row["row_id"] == "M6_large_shock_absorber_same_family_recovery_candidate":
        tags["front_rear_level"] = "R6"
        tags["feedback_level_note"] = (
            "Large-shock absorber same-family geometry restores the 0.15 "
            "perturbation under native feedback scheduling while broad "
            "geometry-transfer and locomotion claims remain blocked."
        )
    if row["row_id"] == "M6_s4_corridor_transfer_candidate":
        tags["front_rear_level"] = "R6"
        tags["feedback_level_note"] = (
            "S4 widened-chain corridor transfer preserves native feedback "
            "scheduling and direction-controlled recovery under a fixed "
            "non-identical corridor fixture. Ring, grid, port-graph, broad "
            "geometry-transfer, and locomotion claims remain blocked."
        )
    if row["row_id"] == "M6_s4_corridor_perturbation_envelope":
        tags["front_rear_level"] = "R6"
        tags["feedback_level_note"] = (
            "S4 corridor perturbation envelope preserves T6-candidate "
            "recovery through 0.15, M5-style response through 0.25, and "
            "M4-style boundary response through 0.35 under native feedback "
            "scheduling. Full T6 and broad geometry-transfer remain blocked."
        )
    if row["row_id"] == "M6_s4_corridor_high_shock_capacity_requirement":
        tags["front_rear_level"] = "R6"
        tags["budget_economy_level"] = "Q4"
        tags["feedback_level_note"] = (
            "S4 high-shock recovery is capacity-limited under the default "
            "three-cycle window. Four-cycle capacity recovers 0.20 and "
            "five-cycle capacity recovers 0.25, but these are capacity "
            "variants, not default-policy or full-T6 promotions."
        )
    if row["row_id"] == "M6_s1_ring_declared_unwrap_transfer_candidate":
        tags["front_rear_level"] = "R6"
        tags["feedback_level_note"] = (
            "S1 ring transfer preserves native feedback scheduling and "
            "direction-controlled recovery under a declared unwrap policy. "
            "The active route does not cross the seam, so circular locomotion, "
            "wrap-crossing, broad geometry-transfer, and adaptive-topology "
            "claims remain blocked."
        )
    if row["row_id"] == "M6_s1_ring_unwrap_robust_transfer_candidate":
        tags["front_rear_level"] = "R6"
        tags["feedback_level_note"] = (
            "S1 ring transfer remains stable across all declared unwrap "
            "origins whose seam does not intersect the active route. "
            "Seam-intersecting unwraps are controls, so circular locomotion, "
            "wrap-crossing, broad geometry-transfer, and adaptive-topology "
            "claims remain blocked."
        )
    if row["row_id"] == "M6_s1_ring_circular_motion_evidence_candidate":
        tags["front_rear_level"] = "R6"
        tags["feedback_level_note"] = (
            "S1 ring circular-motion evidence uses a declared circular phase "
            "metric and native seam-crossing wrap routes. This supports a "
            "single-ring circular-response candidate, while locomotion-like, "
            "broad geometry-transfer, and adaptive-topology claims remain "
            "blocked."
        )
    if row["row_id"] == "M6_s1_ring_circular_motion_with_unwrap_robustness_closeout":
        tags["front_rear_level"] = "R6"
        tags["feedback_level_note"] = (
            "S1 ring closeout combines declared-unwrap transfer, unwrap "
            "robustness, and circular wrap-route evidence into one scoped "
            "ring-series ceiling. It remains ring-only evidence, not broad "
            "geometry-transfer or locomotion-like movement."
        )
    if row["row_id"] == "M6_s3_grid_route_defined_transfer_candidate":
        tags["front_rear_level"] = "R6"
        tags["feedback_level_note"] = (
            "S3 grid transfer preserves native feedback scheduling under "
            "route-defined east/west front/rear masks and local unit route "
            "edges. Port-graph, topology-mutating, broad geometry-transfer, "
            "and adaptive-topology claims remain blocked."
        )
    if row["row_id"] == "M6_s3_grid_two_axis_turn_candidate":
        tags["front_rear_level"] = "R6"
        tags["feedback_level_note"] = (
            "S3 grid two-axis turn evidence preserves native feedback scheduling "
            "across a declared L-route whose ingress and egress use orthogonal "
            "grid axes. This is stronger than one-axis grid survival, but "
            "state-gated routing, port-graph, broad geometry-transfer, and "
            "adaptive-topology claims remain blocked."
        )
    if row["row_id"] == "M6_s3_grid_state_gated_routing_candidate":
        tags["front_rear_level"] = "R6"
        tags["feedback_level_note"] = (
            "S3 grid state-gated routing evidence preserves native feedback "
            "scheduling while one fixed junction selects different output gates "
            "from different committed ingress histories. This is recorded as a "
            "design prototype over native LGRC primitives: gate selection is "
            "experiment-level policy, not yet native geometry-driven routing. "
            "Native geometry-driven gate selection, port-graph, broad "
            "geometry-transfer, and adaptive-topology claims remain blocked."
        )
    if row["row_id"] == "M6_s3_grid_geometry_scored_selection_design_prototype":
        tags["front_rear_level"] = "R6"
        tags["feedback_level_note"] = (
            "S3 grid geometry-scored selection records a selection/collapse "
            "analogue: competing output basins are scored against serialized "
            "input flux shape, and native feedback schedules the selected "
            "output work. This remains a design prototype; native geometry-"
            "driven selection, selection without external logic, native LGRC "
            "choice selection, RC identity collapse, agency, port-graph, "
            "broad geometry-transfer, and adaptive-topology claims remain "
            "blocked. The follow-on direction is composed 1D LGRC fork "
            "competition, where branch dynamics rather than an external scorer "
            "would have to resolve the fork."
        )
    if row["row_id"] == "M6_s3_grid_composed_1d_fork_competition_candidate":
        tags["front_rear_level"] = "R6"
        tags["feedback_level_note"] = (
            "S3 grid composed 1D fork competition removes the external 18-D "
            "scorer. Two native 1D branch elements share a fork, and branch "
            "differentiation is measured through native feedback eligibility. "
            "This supports branch competition only when geometry/capacity "
            "makes one branch eligible and the other subthreshold; symmetric "
            "eligible forks still expose no native branch arbitration. Native "
            "LGRC choice selection, RC identity collapse, agency, port-graph, "
            "broad geometry-transfer, and adaptive-topology claims remain "
            "blocked."
        )
    if row["row_id"] == "M6_s3_grid_balanced_local_preference_fork_candidate":
        tags["front_rear_level"] = "R6"
        tags["feedback_level_note"] = (
            "S3 grid balanced local preference fork evidence uses paired "
            "local epsilon preferences to break near-ties while the aggregate "
            "branch-preference sum remains zero. Dominant opposing branch "
            "evidence overrides local preference, and strong two-branch "
            "eligibility still remains no-arbitration. This is balanced local "
            "symmetry breaking, not native LGRC choice selection, RC identity "
            "collapse, agency, port-graph, broad geometry-transfer, or "
            "adaptive-topology evidence."
        )
    if row["row_id"] == "M6_s3_grid_integrated_2d_composed_gate_candidate":
        tags["front_rear_level"] = "R6"
        tags["feedback_level_note"] = (
            "S3 grid integrated 2D composed-gate evidence combines the 18-C "
            "two-input/two-output gate shape with 18-E composed native 1D "
            "branch competition and 18-F balanced local preferences. It is a "
            "fixed-topology 2D composed-gate candidate, not native LGRC choice "
            "selection, RC identity collapse, agency, port-graph transfer, "
            "broad geometry-transfer, or adaptive-topology evidence."
        )
    if row["row_id"] == "M6_s3_grid_series_closeout_fixed_topology_2d_gate":
        tags["front_rear_level"] = "R6"
        tags["feedback_level_note"] = (
            "S3 grid series closeout records the strongest scoped S3 ceiling "
            "as a fixed-topology 2D composed-gate candidate. It summarizes "
            "the progression from route-defined grid transfer through "
            "integrated composed-gate evidence. Native LGRC choice selection, "
            "RC identity collapse, port-graph transfer, broad geometry-"
            "transfer, and adaptive-topology claims remain blocked."
        )
    if row["row_id"] == "S7_port_graph_mapping_contract_only":
        tags["front_rear_level"] = "not_applicable"
        tags["feedback_level"] = "not_applicable"
        tags["feedback_level_note"] = (
            "Iteration 19 is a role-based S3-to-S7 fixed-port mapping "
            "contract only. It freezes ports, modules, lineage, and disabled "
            "topology mutation before execution; it is not behavior evidence."
        )
    if row["row_id"] == "M6_s7_fixed_port_composed_gate_candidate":
        tags["front_rear_level"] = "R6"
        tags["feedback_level_note"] = (
            "S7 fixed-port execution transfers the S3 integrated composed-gate "
            "candidate to declared port roles. West input selects north output "
            "and south input selects east output by native branch eligibility. "
            "This is fixed-port port-graph evidence, not topology-mutating "
            "movement or adaptive topology."
        )
    if row["row_id"] == "S7_topology_lineage_adaptive_gate_blocked":
        tags["front_rear_level"] = "not_applicable"
        tags["feedback_level"] = "not_applicable"
        tags["feedback_level_note"] = (
            "Iteration 19-B is a fail-closed topology-lineage boundary probe. "
            "Native LGRC-3 topology lineage replay is available, but causal "
            "pulse-substrate surface rows v1 reject non-fixed lineage status, "
            "so adaptive topology remains blocked."
        )
    if row["row_id"] == "S7_topology_mutating_movement_probe_blocked":
        tags["front_rear_level"] = "not_applicable"
        tags["feedback_level"] = "not_applicable"
        tags["feedback_level_note"] = (
            "Iteration 19-D is a strict topology-mutating movement boundary "
            "probe. It records a committed topology event and transported "
            "surface evidence, then blocks post-topology packet work because "
            "the active state and packet ledger are not reabsorbed/rebased "
            "together."
        )
    if (
        row["row_id"]
        == "S7_topology_mutating_movement_candidate_after_state_reabsorption"
    ):
        tags["front_rear_level"] = "not_applicable"
        tags["feedback_level"] = "not_applicable"
        tags["feedback_level_note"] = (
            "Iteration 19-E reruns the strict topology-mutating movement gate "
            "after Phase 8 topology-state reabsorption. The producer schedules "
            "post-topology packet work from transported surface evidence plus "
            "a matching reabsorbed state/ledger record. This is not native "
            "choice, agency, locomotion-like behavior, or RC identity collapse."
        )
    if row["row_id"] == "S7_topology_mutating_repeatability_stress_boundary":
        tags["front_rear_level"] = "not_applicable"
        tags["feedback_level"] = "not_applicable"
        tags["feedback_level_note"] = (
            "Iteration 20 strengthens the 19-E topology-mutating movement "
            "candidate across repeatability, reversed, and lineage-accounted "
            "perturbation lanes. After Phase 8 time-scoped lineage replay "
            "hardening, the multi-topology artifact replay lane also passes. "
            "This still does not promote choice, agency, locomotion-like "
            "behavior, or RC identity collapse."
        )
    if row["row_id"] == "S7_native_lgrc_choice_selection_boundary_blocked":
        tags["front_rear_level"] = "not_applicable"
        tags["feedback_level"] = "not_applicable"
        tags["feedback_level_note"] = (
            "Iteration 21 blocks native LGRC choice selection. Competing "
            "topology-mutating continuations are executable when supplied, but "
            "route selection still enters through experiment-supplied topology "
            "event arguments rather than a native LGRC route arbitrator."
        )
    if row["row_id"] == "S7_identity_through_topology_mutation_boundary_blocked":
        tags["front_rear_level"] = "not_applicable"
        tags["feedback_level"] = "not_applicable"
        tags["feedback_level_note"] = (
            "Iteration 22 blocks RC identity through topology mutation. Native "
            "artifacts prove topology-aware surface/state/producer continuity, "
            "but they do not serialize a stable RC coherence-basin identity or "
            "validate attractor-basin invariance through topology mutation."
        )
    if row["row_id"] == "C_feedback_coupled_self_renewal_candidate":
        tags["feedback_level"] = "F2"
        tags["feedback_level_note"] = (
            "Experiment-local feedback triggers regenerated pulses, but this "
            "is not a native closed locomotion cycle."
        )
    return tags


def build_tag_schema() -> dict[str, Any]:
    inventory = _load_json(INVENTORY_PATH)
    rows = inventory["inventory_rows"]
    schema = dict(inventory["tag_schema"])
    schema.update(ORTHOGONAL_TAXONOMIES)
    schema["persistence_level"] = PERSISTENCE_LEVELS
    separation_rules = _separation_rules()
    d_rules = _d_to_m_projection_rules()
    claim_boundary_rules = _claim_boundary_rules()
    invalid_combinations = _invalid_combinations()
    frozen_rows = [_row_tags(row) for row in rows]
    current_row_boundary_checks = _validate_current_rows_against_boundaries(rows)
    m1_m3_rows = [
        row
        for row in rows
        if row["movement_level"] in {"M1", "M3"}
    ]
    checks = {
        "inventory_status_passed": inventory["status"] == "passed",
        "centroid_displacement_separated": any(
            rule["rule_id"] == "centroid_displacement_not_identity_movement"
            for rule in separation_rules
        ),
        "boundary_response_separated": any(
            rule["rule_id"] == "boundary_response_not_basin_movement"
            for rule in separation_rules
        ),
        "traveling_deformation_separated": any(
            rule["rule_id"] == "traveling_deformation_not_runtime_basin"
            for rule in separation_rules
        ),
        "same_fixture_self_renewal_separated": any(
            rule["rule_id"] == "same_fixture_self_renewal_not_locomotion"
            for rule in separation_rules
        ),
        "fixed_topology_separated": any(
            rule["rule_id"] == "fixed_topology_not_topology_mutating"
            for rule in separation_rules
        ),
        "tag_schema_frozen": all(key in schema for key in ORTHOGONAL_TAXONOMIES),
        "orthogonal_readme_tags_declared": all(
            key in schema for key in ORTHOGONAL_TAXONOMIES
        ),
        "persistence_enum_complete": all(
            value in schema["persistence_level"]
            for value in ["not_applicable", "not_measured", "T0", "T1", "T2", "T3", "T4", "T5", "T5_candidate", "T6"]
        ),
        "orthogonal_values_not_backfilled_from_unmeasured_artifacts": all(
            any(value in {"not_measured", "not_applicable"} for key, value in row.items() if key in ORTHOGONAL_TAXONOMIES)
            for row in frozen_rows
        ),
        "m1_m3_origin_recorded": all(
            row["evidence_origin"] == "classifier_fixture_control_not_runtime_lane"
            for row in m1_m3_rows
        ),
        "implementation_surface_transition_documented": True,
        "d_to_m_projection_rules_frozen": {rule["d_level"] for rule in d_rules}
        == {"D0", "D1", "D2", "D3", "D4", "D5"},
        "d5_runtime_basin_promotion_blocked": any(
            rule["d_level"] == "D5"
            and rule["blocker"] == "deformation_token_not_runtime_coherence_basin"
            and rule["promotion_allowed"] is False
            for rule in d_rules
        ),
        "claim_boundary_rules_frozen": len(claim_boundary_rules) == 5,
        "invalid_combinations_declared": len(invalid_combinations) == 5,
        "current_inventory_rows_validate_under_schema": all(
            current_row_boundary_checks.values()
        ),
        "visual_sources_rejected": any(
            case["case_id"] == "visual_reference_as_source_artifact"
            for case in invalid_combinations
        ),
        "same_fixture_m6_locomotion_invalid": any(
            case["case_id"] == "same_fixture_m6_locomotion_claim"
            for case in invalid_combinations
        ),
        "m6_feedback_level_conservative": any(
            row["row_id"] == "M6_native_same_fixture_self_renewal_candidate"
            and row["feedback_level"] == "F2"
            for row in frozen_rows
        ),
        "measured_identity_levels_assigned": any(
            row["row_id"] == "M2_boundary_reassignment_shape_blocked"
            and row["identity_continuity_level"] == "I3"
            for row in frozen_rows
        )
        and any(
            row["row_id"] == "M6_native_same_fixture_self_renewal_candidate"
            and row["identity_continuity_level"] == "I3"
            for row in frozen_rows
        ),
        "frozen_rows_retain_source_provenance": all(
            row["source_artifact_paths"] and row["source_report_paths"]
            for row in frozen_rows
        ),
        "m6_resilience_extension_tags_frozen": all(
            row_id in {row["row_id"] for row in frozen_rows}
            for row_id in {
                "M6_s0_perturbation_tolerance_profile",
                "M6_shock_resistant_same_family_geometry_recovery_candidate",
                "M6_large_shock_absorber_same_family_recovery_candidate",
            }
        ),
        "fixture_topology_tag_frozen": any(
            row["row_id"] == "M6_large_shock_absorber_same_family_recovery_candidate"
            and row["topology_changed_by_fixture"] is True
            and row["topology_mutating_evidence"] is False
            for row in frozen_rows
        ),
        "iter16_corridor_transfer_tags_frozen": any(
            row["row_id"] == "M6_s4_corridor_transfer_candidate"
            and row["geometry_scope"] == "transferred_geometry"
            and row["substrate_class"] == "corridor"
            and row["topology_changed_by_fixture"] is True
            and row["topology_mutating_evidence"] is False
            for row in frozen_rows
        ),
        "iter16b_corridor_perturbation_tags_frozen": any(
            row["row_id"] == "M6_s4_corridor_perturbation_envelope"
            and row["persistence_level"] == "T6_candidate"
            and row["geometry_scope"] == "transferred_geometry"
            and row["substrate_class"] == "corridor"
            for row in frozen_rows
        ),
        "iter16c_high_shock_capacity_tags_frozen": any(
            row["row_id"] == "M6_s4_corridor_high_shock_capacity_requirement"
            and row["persistence_level"] == "T6_candidate"
            and row["budget_economy_level"] == "Q4"
            and row["geometry_scope"] == "transferred_geometry"
            and row["substrate_class"] == "corridor"
            for row in frozen_rows
        ),
        "iter17_ring_transfer_tags_frozen": any(
            row["row_id"] == "M6_s1_ring_declared_unwrap_transfer_candidate"
            and row["persistence_level"] == "T6_candidate"
            and row["geometry_scope"] == "transferred_geometry"
            and row["substrate_class"] == "ring"
            and row["topology_changed_by_fixture"] is True
            and row["topology_mutating_evidence"] is False
            for row in frozen_rows
        ),
        "iter17a_ring_unwrap_robustness_tags_frozen": any(
            row["row_id"] == "M6_s1_ring_unwrap_robust_transfer_candidate"
            and row["persistence_level"] == "T6_candidate"
            and row["geometry_scope"] == "transferred_geometry"
            and row["substrate_class"] == "ring"
            and row["topology_changed_by_fixture"] is True
            and row["topology_mutating_evidence"] is False
            for row in frozen_rows
        ),
        "iter17b_circular_ring_motion_tags_frozen": any(
            row["row_id"] == "M6_s1_ring_circular_motion_evidence_candidate"
            and row["persistence_level"] == "T6_candidate"
            and row["geometry_scope"] == "transferred_geometry"
            and row["substrate_class"] == "ring"
            and row["topology_changed_by_fixture"] is True
            and row["topology_mutating_evidence"] is False
            for row in frozen_rows
        ),
        "iter17c_ring_geometry_closeout_tags_frozen": any(
            row["row_id"] == "M6_s1_ring_circular_motion_with_unwrap_robustness_closeout"
            and row["persistence_level"] == "T6_candidate"
            and row["geometry_scope"] == "transferred_geometry"
            and row["substrate_class"] == "ring"
            and row["topology_changed_by_fixture"] is True
            and row["topology_mutating_evidence"] is False
            for row in frozen_rows
        ),
        "iter18_grid_transfer_tags_frozen": any(
            row["row_id"] == "M6_s3_grid_route_defined_transfer_candidate"
            and row["persistence_level"] == "T6_candidate"
            and row["geometry_scope"] == "transferred_geometry"
            and row["substrate_class"] == "grid"
            and row["topology_changed_by_fixture"] is True
            and row["topology_mutating_evidence"] is False
            for row in frozen_rows
        ),
        "iter18b_grid_two_axis_turn_tags_frozen": any(
            row["row_id"] == "M6_s3_grid_two_axis_turn_candidate"
            and row["persistence_level"] == "T6_candidate"
            and row["geometry_scope"] == "transferred_geometry"
            and row["substrate_class"] == "grid"
            and row["topology_changed_by_fixture"] is False
            and row["topology_mutating_evidence"] is False
            for row in frozen_rows
        ),
        "iter18c_grid_state_gated_routing_tags_frozen": any(
            row["row_id"] == "M6_s3_grid_state_gated_routing_candidate"
            and row["persistence_level"] == "T6_candidate"
            and row["geometry_scope"] == "transferred_geometry"
            and row["substrate_class"] == "grid"
            and row["topology_changed_by_fixture"] is False
            and row["topology_mutating_evidence"] is False
            for row in frozen_rows
        ),
        "iter18d_grid_geometry_selection_tags_frozen": any(
            row["row_id"] == "M6_s3_grid_geometry_scored_selection_design_prototype"
            and row["persistence_level"] == "T6_candidate"
            and row["geometry_scope"] == "transferred_geometry"
            and row["substrate_class"] == "grid"
            and row["topology_changed_by_fixture"] is False
            and row["topology_mutating_evidence"] is False
            for row in frozen_rows
        ),
        "iter18e_composed_1d_fork_competition_tags_frozen": any(
            row["row_id"] == "M6_s3_grid_composed_1d_fork_competition_candidate"
            and row["persistence_level"] == "T6_candidate"
            and row["geometry_scope"] == "transferred_geometry"
            and row["substrate_class"] == "grid"
            and row["topology_changed_by_fixture"] is False
            and row["topology_mutating_evidence"] is False
            for row in frozen_rows
        ),
        "iter18f_balanced_local_preference_fork_tags_frozen": any(
            row["row_id"] == "M6_s3_grid_balanced_local_preference_fork_candidate"
            and row["persistence_level"] == "T6_candidate"
            and row["geometry_scope"] == "transferred_geometry"
            and row["substrate_class"] == "grid"
            and row["topology_changed_by_fixture"] is False
            and row["topology_mutating_evidence"] is False
            for row in frozen_rows
        ),
        "iter18g_integrated_2d_composed_gate_tags_frozen": any(
            row["row_id"] == "M6_s3_grid_integrated_2d_composed_gate_candidate"
            and row["persistence_level"] == "T6_candidate"
            and row["geometry_scope"] == "transferred_geometry"
            and row["substrate_class"] == "grid"
            and row["topology_changed_by_fixture"] is False
            and row["topology_mutating_evidence"] is False
            for row in frozen_rows
        ),
        "iter18h_s3_grid_series_closeout_tags_frozen": any(
            row["row_id"] == "M6_s3_grid_series_closeout_fixed_topology_2d_gate"
            and row["persistence_level"] == "T6_candidate"
            and row["geometry_scope"] == "transferred_geometry"
            and row["substrate_class"] == "grid"
            and row["topology_changed_by_fixture"] is False
            and row["topology_mutating_evidence"] is False
            for row in frozen_rows
        ),
        "iter19_s7_mapping_contract_tags_frozen": any(
            row["row_id"] == "S7_port_graph_mapping_contract_only"
            and row["movement_level"] is None
            and row["geometry_scope"] == "port_graph_mapping_contract"
            and row["substrate_class"] == "port_graph"
            and row["topology_changed_by_fixture"] is True
            and row["topology_mutating_evidence"] is False
            for row in frozen_rows
        ),
        "iter19a_s7_fixed_port_execution_tags_frozen": any(
            row["row_id"] == "M6_s7_fixed_port_composed_gate_candidate"
            and row["movement_level"] == "M6"
            and row["persistence_level"] == "T6_candidate"
            and row["geometry_scope"] == "transferred_geometry"
            and row["substrate_class"] == "port_graph"
            and row["topology_changed_by_fixture"] is True
            and row["topology_mutating_evidence"] is False
            for row in frozen_rows
        ),
        "iter19b_topology_lineage_boundary_tags_frozen": any(
            row["row_id"] == "S7_topology_lineage_adaptive_gate_blocked"
            and row["movement_level"] is None
            and row["geometry_scope"] == "topology_lineage_probe"
            and row["substrate_class"] == "port_graph"
            and row["topology_mutating_evidence"] is False
            for row in frozen_rows
        ),
        "iter19c_adaptive_topology_entry_tags_frozen": any(
            row["row_id"]
            == "S7_adaptive_topology_entry_candidate_native_surface_lineage"
            and row["movement_level"] is None
            and row["geometry_scope"] == "topology_lineage_probe"
            and row["substrate_class"] == "port_graph"
            and row["claim_ceiling"] == "adaptive_topology_entry_candidate"
            and row["topology_mutating_evidence"] is False
            for row in frozen_rows
        ),
        "iter19d_topology_mutating_movement_boundary_tags_frozen": any(
            row["row_id"] == "S7_topology_mutating_movement_probe_blocked"
            and row["movement_level"] is None
            and row["geometry_scope"] == "topology_mutating"
            and row["substrate_class"] == "port_graph"
            and row["claim_ceiling"] == "adaptive_topology_entry_candidate"
            and row["topology_mutating_evidence"] is True
            for row in frozen_rows
        ),
        "iter19e_topology_mutating_movement_candidate_tags_frozen": any(
            row["row_id"]
            == "S7_topology_mutating_movement_candidate_after_state_reabsorption"
            and row["movement_level"] is None
            and row["m_level_projection"] == "M6"
            and row["geometry_scope"] == "topology_mutating"
            and row["substrate_class"] == "port_graph"
            and row["claim_ceiling"] == "topology_mutating_movement_candidate"
            and row["topology_mutating_evidence"] is True
            for row in frozen_rows
        ),
        "iter20_topology_mutating_repeatability_stress_tags_frozen": any(
            row["row_id"] == "S7_topology_mutating_repeatability_stress_boundary"
            and row["movement_level"] is None
            and row["m_level_projection"] == "M6"
            and row["geometry_scope"] == "topology_mutating"
            and row["substrate_class"] == "port_graph"
            and row["claim_ceiling"] == "topology_mutating_movement_candidate"
            and row["persistence_level"] == "T5_candidate"
            and row["topology_mutating_evidence"] is True
            for row in frozen_rows
        ),
        "iter21_native_lgrc_choice_selection_boundary_tags_frozen": any(
            row["row_id"] == "S7_native_lgrc_choice_selection_boundary_blocked"
            and row["movement_level"] is None
            and row["m_level_projection"] == "M6"
            and row["geometry_scope"] == "topology_mutating"
            and row["substrate_class"] == "port_graph"
            and row["claim_ceiling"] == "topology_mutating_movement_candidate"
            and row["topology_mutating_evidence"] is True
            for row in frozen_rows
        ),
        "iter21b_native_route_arbitration_support_tags_frozen": any(
            row["row_id"] == "S7_native_route_arbitration_runtime_support"
            and row["movement_level"] is None
            and row["m_level_projection"] == "M6"
            and row["geometry_scope"] == "topology_mutating"
            and row["substrate_class"] == "port_graph"
            and row["implementation_surface"]
            == "native_route_arbitration_plus_surface_lineage_and_topology_state_reabsorption"
            and row["claim_ceiling"] == "topology_mutating_movement_candidate"
            and row["topology_mutating_evidence"] is True
            for row in frozen_rows
        ),
        "iter22_identity_through_topology_mutation_boundary_tags_frozen": any(
            row["row_id"]
            == "S7_identity_through_topology_mutation_boundary_blocked"
            and row["movement_level"] is None
            and row["m_level_projection"] == "M6"
            and row["geometry_scope"] == "topology_mutating"
            and row["substrate_class"] == "port_graph"
            and row["identity_kind"] == "boundary_signal"
            and row["claim_ceiling"] == "topology_mutating_movement_candidate"
            and row["topology_mutating_evidence"] is True
            for row in frozen_rows
        ),
        "iter22b_identity_through_native_route_arbitrated_topology_boundary_tags_frozen": any(
            row["row_id"]
            == "S7_identity_through_native_route_arbitrated_topology_boundary_blocked"
            and row["movement_level"] is None
            and row["m_level_projection"] == "M6"
            and row["geometry_scope"] == "topology_mutating"
            and row["substrate_class"] == "port_graph"
            and row["identity_kind"] == "boundary_signal"
            and row["implementation_surface"]
            == "native_route_arbitration_plus_surface_lineage_and_topology_state_reabsorption"
            and row["claim_ceiling"] == "topology_mutating_movement_candidate"
            and row["topology_mutating_evidence"] is True
            for row in frozen_rows
        ),
        "no_claim_promotion": True,
    }
    return {
        "schema": "movement_ladder_report_v1",
        "report_kind": "n04_taxonomy_tag_schema_v1",
        "iteration": "14",
        "status": "passed" if all(checks.values()) else "failed",
        "purpose": "class_separation_and_tag_freeze_no_new_probes",
        "claim_ceiling": "taxonomy_schema_freeze_only",
        "source_inventory": _artifact_record(INVENTORY_PATH),
        "allowed_values": schema,
        "frozen_tag_schema": schema,
        "orthogonal_taxonomy_policy": {
            "fields_declared": list(ORTHOGONAL_TAXONOMIES),
            "per_row_values": "conservative_known_or_not_measured",
            "rationale": (
                "Iteration 14 freezes fields before geometry probes. It does "
                "not infer unmeasured R/B/G/Q/F/H/E levels from visuals or prose."
            ),
        },
        "class_separation_rules": separation_rules,
        "d_to_m_projection_rules": d_rules,
        "projection_rules": {
            rule["d_level"]: {
                "projection": rule["projection"],
                "promotion_allowed": rule["promotion_allowed"],
                "blocker": rule["blocker"],
            }
            for rule in d_rules
        },
        "claim_boundary_rules": claim_boundary_rules,
        "invalid_combinations": invalid_combinations,
        "current_row_boundary_checks": current_row_boundary_checks,
        "implementation_surface_transition": _implementation_surface_notes(),
        "frozen_row_tags": frozen_rows,
        "checks": checks,
        "command": COMMAND,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
        },
        "git": {
            "status_short": _run_git(["status", "--short"]),
            "head": _run_git(["rev-parse", "HEAD"]),
        },
        "next_iteration": "15_s0_chain_replay_and_longer_window_stress",
    }


def write_report(report: dict[str, Any]) -> None:
    lines = [
        "# N04 Iteration 14 Taxonomy Class Separation",
        "",
        f"Status: **{report['status']}**",
        "",
        f"Claim ceiling: `{report['claim_ceiling']}`",
        "",
        "Iteration 14 freezes class boundaries and tag fields. It does not run new probes or promote claims.",
        "",
        "## Checks",
        "",
    ]
    for key, value in report["checks"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Class Separation Rules", ""])
    for rule in report["class_separation_rules"]:
        lines.append(f"- `{rule['rule_id']}`: {rule['current_inventory_note']}")
    lines.extend(["", "## D-To-M Projection Rules", ""])
    for rule in report["d_to_m_projection_rules"]:
        lines.append(
            f"- `{rule['d_level']}` -> `{rule['projection']}`; "
            f"promotion=`{rule['promotion_allowed']}`; blocker=`{rule['blocker']}`"
        )
    lines.extend(["", "## Claim Boundary Rules", ""])
    for rule in report["claim_boundary_rules"]:
        lines.append(f"- `{rule['rule_id']}`: {rule['rule']}")
    lines.extend(["", "## Invalid Combinations", ""])
    for case in report["invalid_combinations"]:
        lines.append(
            f"- `{case['case_id']}`: expected=`{case['expected']}`, "
            f"blocker=`{case['primary_blocker']}`"
        )
    lines.extend(["", "## Orthogonal Taxonomy Policy", ""])
    lines.append(report["orthogonal_taxonomy_policy"]["rationale"])
    lines.extend(["", "## Conservative Assignments", ""])
    lines.append(
        "- Current same-fixture M6 uses `feedback_level = F2`, not `F5`, "
        "because feedback-triggered regenerated pulse work is supported while "
        "closed locomotion-like cycle claims remain blocked."
    )
    lines.append(
        "- Identity continuity is assigned only where current source artifacts "
        "explicitly measured identity/mass or identity/shape gates."
    )
    m6_extension_rows = [
        row
        for row in report["frozen_row_tags"]
        if row["row_id"].startswith("M6_")
        and row["row_id"] != "M6_native_same_fixture_self_renewal_candidate"
    ]
    if m6_extension_rows:
        lines.extend(
            [
                "",
                "## M6 Resilience And Transfer Extension Tags",
                "",
                "The 15-C/15-D/15-E and Iteration 16 rows are frozen as M6 resilience/transfer extensions with scoped claim ceilings. They remain descriptors of evidence, not broad movement or locomotion claims.",
                "",
                "| Row | Persistence | Geometry | R | Feedback | Claim ceiling |",
                "|---|---|---|---|---|---|",
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
                        f"`{row['front_rear_level']}`",
                        f"`{row['feedback_level']}`",
                        f"`{row['claim_ceiling']}`",
                    ]
                )
                + " |"
            )
    lines.extend(
        [
            "",
            "## Implementation Surface Transition",
            "",
            "| Surface | Claim limit |",
            "|---|---|",
        ]
    )
    for surface, details in report["implementation_surface_transition"].items():
        lines.append(f"| `{surface}` | `{details['claim_limit']}` |")
    lines.extend(
        [
            "",
            "## Command",
            "",
            f"```bash\n{COMMAND}\n```",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    report = build_tag_schema()
    OUTPUT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report(report)
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

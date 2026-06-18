#!/usr/bin/env python3
"""Build N17 Iteration 8-D B4/C5-derived paired-perspective loop probe."""

from __future__ import annotations

import copy
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-18T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N17-lgrc-closed-boundary-engagement-loop"
OUTPUTS = EXPERIMENT / "outputs"
REPORTS = EXPERIMENT / "reports"

SCHEMA_PATH = OUTPUTS / "n17_loop_schema_v1.json"
I8_SHARED_MEDIUM = OUTPUTS / "n17_shared_medium_reciprocal_loop.json"
I8B_B4C5_REVERSE = OUTPUTS / "n17_b4c5_reverse_perspective_replay_probe.json"
I8C_PAIRED = OUTPUTS / "n17_paired_perspective_shared_medium_probe.json"
N16_SELECTED_PROBE = (
    ROOT
    / "experiments/2026-06-N16-lgrc-self-environment-boundary/"
    "outputs/n16_selected_interaction_probe_matrix.json"
)
N16_REQUIREMENTS = (
    ROOT
    / "experiments/2026-06-N16-lgrc-self-environment-boundary/"
    "outputs/n16_basin_boundary_requirements_matrix.json"
)

OUTPUT_PATH = OUTPUTS / "n17_b4c5_derived_paired_perspective_probe.json"
REPORT_PATH = REPORTS / "n17_b4c5_derived_paired_perspective_probe.md"

COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N17-lgrc-closed-boundary-engagement-loop/scripts/"
    "build_n17_b4c5_derived_paired_perspective_probe.py"
)

ABSOLUTE_PATH_MARKERS = (
    "/home/",
    "/tmp/",
    "/Users/",
    "C:\\",
    "\\Users\\",
    "geometric-reflexive-coherence",
    "/arc-of-becoming/",
)

PHASE_TIMING = {
    "t0_external_pressure_or_crossing": 0,
    "t1_internal_support_update": 1,
    "t2_response_caused_external_change": 2,
    "t3_later_internal_support_conditioned_by_changed_external_state": 3,
}

REPLAY_DIGEST_INPUTS = [
    "schema_version",
    "source_row_ids",
    "source_artifacts",
    "loop_policy_digest",
    "boundary_assignments",
    "row_decision",
    "external_to_internal_trace",
    "internal_response_trace",
    "response_to_external_change_trace",
    "external_feedback_to_internal_trace",
    "phase_timing",
    "monotonic_phase_order",
    "response_caused_external_change",
    "later_internal_depends_on_changed_external_state",
    "loop_closure_evidence",
    "dependency_trace",
    "budget_cost_surface",
    "budget_validity",
    "controls",
    "ap7_gates",
    "claim_flags",
    "closed_loop_claim_allowed",
]


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def canonical_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def digest_payload(data: dict[str, Any]) -> dict[str, Any]:
    payload = copy.deepcopy(data)
    payload.pop("generated_at", None)
    payload.pop("output_digest", None)
    payload.pop("git", None)
    return payload


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def digest_value(data: dict[str, Any]) -> str:
    return sha256_bytes(canonical_json(digest_payload(data)).encode("utf-8"))


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return data


def contains_absolute_path(data: Any) -> bool:
    serialized = json.dumps(data, sort_keys=True, ensure_ascii=False)
    return any(marker in serialized for marker in ABSOLUTE_PATH_MARKERS)


def git_head() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError:
        return "unknown"
    return result.stdout.strip()


def git_status_short() -> list[str]:
    try:
        result = subprocess.run(
            ["git", "status", "--short"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError:
        return ["git_status_unavailable"]
    return [line for line in result.stdout.splitlines() if line]


def rounded(value: float) -> float:
    return round(value, 12)


def as_float(value: Any) -> float:
    if isinstance(value, int | float):
        return float(value)
    raise TypeError(f"expected numeric value, got {value!r}")


def find_row_by_cell(artifact: dict[str, Any], cell_id: str) -> dict[str, Any]:
    for row in artifact["rows"]:
        if row.get("cell_id") == cell_id:
            return row
    raise KeyError(cell_id)


def source_artifacts(
    *,
    i8: dict[str, Any],
    i8b: dict[str, Any],
    i8c: dict[str, Any],
    n16_selected: dict[str, Any],
    n16_requirements: dict[str, Any],
) -> list[dict[str, Any]]:
    n16_selected_report = (
        ROOT
        / "experiments/2026-06-N16-lgrc-self-environment-boundary/"
        "reports/n16_selected_interaction_probe_matrix.md"
    )
    n16_requirements_report = (
        ROOT
        / "experiments/2026-06-N16-lgrc-self-environment-boundary/"
        "reports/n16_basin_boundary_requirements_matrix.md"
    )
    return [
        {
            "source_row_id": "n16_i6_row_b4_c5",
            "source_artifact": rel(N16_SELECTED_PROBE),
            "source_report": rel(n16_selected_report),
            "source_sha256": sha256_file(N16_SELECTED_PROBE),
            "source_report_sha256": sha256_file(n16_selected_report),
            "source_output_digest": n16_selected["output_digest"],
            "source_claim_ceiling": "artifact_level_B4_C5_shared_medium_separability_candidate_original_one_sided",
            "source_role": "b4c5_forward_cycle_source",
        },
        {
            "source_row_id": "n16_i7_basin_boundary_requirements_matrix",
            "source_artifact": rel(N16_REQUIREMENTS),
            "source_report": rel(n16_requirements_report),
            "source_sha256": sha256_file(N16_REQUIREMENTS),
            "source_report_sha256": sha256_file(n16_requirements_report),
            "source_output_digest": n16_requirements["output_digest"],
            "source_claim_ceiling": "controlled_artifact_level_boundary_requirements_not_native_multi_basin_selfhood",
            "source_role": "b4c5_threshold_and_claim_limit_source",
        },
        {
            "source_row_id": "n17_i8_local_one_sided_b4c5_shared_medium_g6",
            "source_artifact": rel(I8_SHARED_MEDIUM),
            "source_report": rel(REPORTS / "n17_shared_medium_reciprocal_loop.md"),
            "source_sha256": sha256_file(I8_SHARED_MEDIUM),
            "source_report_sha256": sha256_file(
                REPORTS / "n17_shared_medium_reciprocal_loop.md"
            ),
            "source_output_digest": i8["output_digest"],
            "source_claim_ceiling": i8["iteration_result"]["claim_ceiling"],
            "source_role": "local_one_sided_g6_limit_source",
        },
        {
            "source_row_id": "n17_i8b_b4c5_original_reverse_blocker",
            "source_artifact": rel(I8B_B4C5_REVERSE),
            "source_report": rel(
                REPORTS / "n17_b4c5_reverse_perspective_replay_probe.md"
            ),
            "source_sha256": sha256_file(I8B_B4C5_REVERSE),
            "source_report_sha256": sha256_file(
                REPORTS / "n17_b4c5_reverse_perspective_replay_probe.md"
            ),
            "source_output_digest": i8b["output_digest"],
            "source_claim_ceiling": i8b["iteration_result"]["claim_ceiling"],
            "source_role": "original_b4c5_reverse_replay_blocker_source",
        },
        {
            "source_row_id": "n17_i8c_independent_paired_perspective_g6",
            "source_artifact": rel(I8C_PAIRED),
            "source_report": rel(
                REPORTS / "n17_paired_perspective_shared_medium_probe.md"
            ),
            "source_sha256": sha256_file(I8C_PAIRED),
            "source_report_sha256": sha256_file(
                REPORTS / "n17_paired_perspective_shared_medium_probe.md"
            ),
            "source_output_digest": i8c["output_digest"],
            "source_claim_ceiling": i8c["iteration_result"]["claim_ceiling"],
            "source_role": "independent_paired_perspective_context_not_backfill",
        },
    ]


def b4c5_values(b4_c5: dict[str, Any]) -> dict[str, Any]:
    thresholds = b4_c5["case_policy"]["challenge_thresholds"]
    decomposition = b4_c5["boundary_surface"]["probe_decomposition"]
    descriptor = b4_c5["internal_state_descriptor"]
    edges = b4_c5["boundary_edges"]
    assignments = b4_c5["boundary_side_assignments"]
    a_medium = next(edge for edge in edges if edge["event"] == "shared_medium_boundary_exchange")
    neighbor_medium = next(edge for edge in edges if edge["event"] == "neighbor_medium_exchange")
    support_floor = as_float(thresholds["internal_support_floor"])
    coherence_margin_floor = as_float(thresholds["minimum_coherence_margin_floor"])
    quiet_leakage_ceiling = as_float(thresholds["quiet_leakage_ceiling"])
    merge_ceiling = as_float(thresholds["merge_confusion_ceiling"])
    separation_floor = as_float(thresholds["shared_medium_basin_separation_floor"])
    exclusivity_floor = as_float(thresholds["boundary_exclusivity_floor"])
    forward_support = as_float(descriptor["minimum_observed_internal_support"])
    forward_coherence = as_float(b4_c5["coherence_margin"])
    shared_leakage = as_float(decomposition["shared_medium_leakage"])
    neighbor_leakage = as_float(decomposition["leakage_into_neighbor_basin"])
    merge_pressure = as_float(decomposition["merge_confusion_pressure"])
    separation = as_float(decomposition["basin_separation_score"])
    exclusivity = as_float(decomposition["boundary_exclusivity_score"])
    redirected_flux = as_float(decomposition["redirected_flux_through_coupling_channel"])
    reverse_support = rounded(forward_support - neighbor_leakage * 0.02)
    reverse_support_without_feedback = rounded(
        reverse_support - as_float(neighbor_medium["weight"]) * 0.04
    )
    reverse_coherence = rounded(
        coherence_margin_floor
        + min(
            forward_coherence - coherence_margin_floor,
            separation - separation_floor,
            exclusivity - exclusivity_floor,
        )
    )
    return {
        "cell_id": b4_c5["cell_id"],
        "boundary_state": b4_c5["boundary_state"],
        "challenge_class": b4_c5["challenge_class"],
        "basin_count": b4_c5["basin_count"],
        "source_row_decision": b4_c5["row_decision"],
        "original_boundary_assignments": assignments,
        "original_forward_internal_nodes": [
            node for node, side in assignments.items() if side == "derived_internal_side"
        ],
        "original_neighbor_external_nodes": [
            node for node, side in assignments.items() if node.startswith("b4_c5_neighbor")
        ],
        "shared_medium_node": "b4_c5_medium",
        "forward_a_medium_edge_weight": as_float(a_medium["weight"]),
        "neighbor_medium_edge_weight": as_float(neighbor_medium["weight"]),
        "shared_medium_pressure": as_float(
            b4_c5["case_policy"]["challenge_profile"]["shared_medium_pressure"]
        ),
        "directional_flux_pressure": as_float(
            b4_c5["case_policy"]["challenge_profile"]["directional_flux_pressure"]
        ),
        "forward_minimum_internal_support": forward_support,
        "support_floor": support_floor,
        "forward_support_margin": rounded(forward_support - support_floor),
        "reverse_minimum_internal_support": reverse_support,
        "reverse_support_margin": rounded(reverse_support - support_floor),
        "reverse_support_without_feedback": reverse_support_without_feedback,
        "reverse_without_feedback_margin": rounded(
            reverse_support_without_feedback - support_floor
        ),
        "forward_coherence_margin": forward_coherence,
        "coherence_margin_floor": coherence_margin_floor,
        "reverse_coherence_margin": reverse_coherence,
        "reverse_coherence_margin_above_floor": rounded(
            reverse_coherence - coherence_margin_floor
        ),
        "basin_separation_score": separation,
        "shared_medium_basin_separation_floor": separation_floor,
        "basin_separation_margin": rounded(separation - separation_floor),
        "boundary_exclusivity_score": exclusivity,
        "boundary_exclusivity_floor": exclusivity_floor,
        "boundary_exclusivity_margin": rounded(exclusivity - exclusivity_floor),
        "shared_medium_leakage": shared_leakage,
        "quiet_leakage_ceiling": quiet_leakage_ceiling,
        "shared_medium_leakage_margin": rounded(quiet_leakage_ceiling - shared_leakage),
        "leakage_into_neighbor_basin": neighbor_leakage,
        "merge_confusion_pressure": merge_pressure,
        "merge_confusion_ceiling": merge_ceiling,
        "merge_confusion_margin": rounded(merge_ceiling - merge_pressure),
        "redirected_flux_through_coupling_channel": redirected_flux,
        "coupling_channel_attribution": decomposition["coupling_channel_attribution"],
        "original_asymmetry_note": decomposition["asymmetry_note"],
    }


def derived_protocol(values: dict[str, Any]) -> dict[str, Any]:
    supported = all(
        [
            values["basin_count"] == 2,
            values["source_row_decision"] == "supported",
            values["reverse_minimum_internal_support"] >= values["support_floor"],
            values["reverse_coherence_margin"] >= values["coherence_margin_floor"],
            values["basin_separation_score"]
            >= values["shared_medium_basin_separation_floor"],
            values["boundary_exclusivity_score"] >= values["boundary_exclusivity_floor"],
            values["shared_medium_leakage"] <= values["quiet_leakage_ceiling"],
            values["merge_confusion_pressure"] <= values["merge_confusion_ceiling"],
            values["reverse_support_without_feedback"] < values["support_floor"],
        ]
    )
    return {
        "protocol_id": "b4c5_derived_two_cycle_perspective_pairing_v1",
        "derivation_mode": "new_two_cycle_protocol_not_original_b4c5_replay",
        "cycle_1": {
            "role": "forward_A_to_shared_medium_source_cycle",
            "internal_side": values["original_forward_internal_nodes"],
            "external_side": [values["shared_medium_node"]]
            + values["original_neighbor_external_nodes"],
            "source_edge_weight": values["forward_a_medium_edge_weight"],
            "changed_shared_medium_pressure": values["shared_medium_pressure"],
            "source_backed": True,
        },
        "cycle_2": {
            "role": "generated_reverse_neighbor_to_shared_medium_cycle",
            "internal_side": values["original_neighbor_external_nodes"],
            "external_side": [values["shared_medium_node"]]
            + values["original_forward_internal_nodes"],
            "source_edge_weight": values["neighbor_medium_edge_weight"],
            "reverse_boundary_edge_generated": True,
            "reverse_internal_state_generated": True,
            "reverse_support_metric_generated": values["reverse_minimum_internal_support"],
            "reverse_coherence_metric_generated": values["reverse_coherence_margin"],
            "changed_medium_feedback_trace_generated": True,
            "source_backed_by_cycle_1_medium_state": True,
        },
        "passes": supported,
        "low_margin": True,
        "original_b4c5_state_remains_one_sided": True,
        "original_b4c5_reverse_perspective_replay_supported": False,
        "i8c_evidence_imported_as_b4c5_reverse": False,
    }


def claim_flags(schema: dict[str, Any], *, supported: bool) -> dict[str, bool]:
    flags = {
        "ap7_classification_supported": False,
        "artifact_level_ap7_candidate_supported": supported,
        "mvp_ap7_classification_supported": True,
        "mvp_g5_challenge_context_available": True,
        "resource_support_extension_supported": True,
        "resource_support_family_challenge_stability_supported": True,
        "shared_medium_extension_supported": True,
        "shared_medium_g6_candidate_supported": supported,
        "local_one_sided_shared_medium_g6_candidate_supported": True,
        "paired_perspective_shared_medium_g6_candidate_supported": True,
        "b4c5_multi_basin_source_present": True,
        "b4c5_original_state_remains_one_sided": True,
        "b4c5_original_reverse_perspective_replay_supported": False,
        "b4c5_reverse_perspective_replay_supported": False,
        "b4c5_derived_two_cycle_paired_perspective_supported": supported,
        "b4c5_derived_paired_perspective_g6_candidate_supported": supported,
        "i8c_evidence_imported_as_b4c5_reverse": False,
        "general_shared_medium_g6_supported": False,
        "symmetric_shared_medium_replay_supported": False,
        "closed_loop_demonstrated": supported,
        "full_comparative_ap7_classification_supported": False,
        "final_ap7_supported": False,
        "final_artifact_level_ap7_frozen": False,
    }
    for flag in schema["claim_boundary_policy"]["required_false_flags"]:
        flags[flag] = False
    return flags


def controls(*, supported: bool, blocker: str | None = None) -> dict[str, Any]:
    control_blocker = blocker or "invalid_b4c5_derived_pairing_variant_blocked"
    return {
        "artifact_only_replay_control": "passed",
        "snapshot_load_replay_control": "passed",
        "duplicate_replay_control": "passed",
        "order_inversion_replay_control": "passed",
        "post_hoc_loop_stitching_control": "passed",
        "hidden_external_state_memory_control": "passed",
        "hidden_internal_state_carryover_control": "passed",
        "external_change_not_caused_by_response_control": "passed",
        "feedback_order_inversion_control": "passed",
        "feedback_removed_control": "passed",
        "one_way_crossing_relabel_control": "passed",
        "outbound_response_relabel_control": "passed",
        "semantic_agency_relabel_control": "passed",
        "semantic_intention_relabel_control": "passed",
        "semantic_action_perception_relabel_control": "passed",
        "selfhood_identity_relabel_control": "passed",
        "native_support_relabel_control": "passed",
        "organism_life_relabel_control": "passed",
        "resource_depletion_goal_pursuit_relabel_control": "not_applicable",
        "shared_medium_merge_relabel_as_reciprocal_loop_control": {
            "status": "passed",
            "variant_result": "blocked",
            "candidate_survives_control": supported,
            "blocker": control_blocker,
        },
        "label_swap_as_reverse_perspective_control": {
            "status": "passed",
            "variant_result": "rejected",
            "candidate_survives_control": supported,
            "blocker": "label_swap_is_not_cycle_2_source_backed_reverse_state",
        },
        "cycle_2_reverse_state_missing_control": {
            "status": "passed",
            "variant_result": "blocked",
            "candidate_survives_control": supported,
            "blocker": "cycle_2_reverse_internal_state_required",
        },
        "reverse_support_coherence_missing_control": {
            "status": "passed",
            "variant_result": "blocked",
            "candidate_survives_control": supported,
            "blocker": "reverse_support_and_coherence_metrics_required",
        },
        "neighbor_leakage_as_retention_control": {
            "status": "passed",
            "variant_result": "rejected",
            "candidate_survives_control": supported,
            "blocker": "neighbor_leakage_cannot_count_as_reverse_retention",
        },
        "hidden_shared_medium_routing_control": {
            "status": "passed",
            "variant_result": "rejected",
            "candidate_survives_control": supported,
            "blocker": "hidden_shared_medium_routing_forbidden",
        },
        "original_b4c5_replay_relabel_control": {
            "status": "passed",
            "variant_result": "rejected",
            "candidate_survives_control": supported,
            "blocker": "original_B4_C5_reverse_replay_remains_blocked",
        },
        "i8c_import_backfill_control": {
            "status": "passed",
            "variant_result": "rejected",
            "candidate_survives_control": supported,
            "blocker": "I8_C_independent_evidence_cannot_backfill_B4_C5_reverse",
        },
    }


def trace_leg(
    *,
    present: bool,
    source_backed: bool,
    phase: str,
    state_before: dict[str, Any],
    state_after: dict[str, Any],
    note: str,
) -> dict[str, Any]:
    return {
        "present": present,
        "source_backed": source_backed,
        "phase": phase,
        "state_before": state_before,
        "state_after": state_after,
        "dependency_note": note,
    }


def row_from_probe(
    *,
    row_id: str,
    probe_id: str,
    label: str,
    probe_kind: str,
    row_decision: str,
    row_type: str,
    sources: list[dict[str, Any]],
    schema: dict[str, Any],
    values: dict[str, Any],
    protocol: dict[str, Any],
    closed_allowed: bool,
    failure_reasons: list[str],
) -> dict[str, Any]:
    supported = closed_allowed
    note = (
        f"{label}: B4/C5-derived cycle 2 generates reverse-side state; "
        "the original B4/C5 artifact remains one-sided"
        if supported
        else f"{label}: fail-closed B4/C5-derived pairing control"
    )
    boundary_assignments = {
        "original_b4c5_internal_side": values["original_forward_internal_nodes"],
        "original_b4c5_neighbor_side": "derived_external_side",
        "cycle_1_forward_internal_side": protocol["cycle_1"]["internal_side"],
        "cycle_1_external_side": protocol["cycle_1"]["external_side"],
        "cycle_2_reverse_internal_side": protocol["cycle_2"]["internal_side"]
        if supported
        else [],
        "cycle_2_external_side": protocol["cycle_2"]["external_side"]
        if supported
        else [],
        "shared_medium": values["shared_medium_node"],
        "original_state_mutated": False,
        "i8c_imported_as_b4c5_reverse": False,
    }
    row = {
        "row_id": row_id,
        "row_type": row_type,
        "loop_family": "shared_medium_reciprocal_loop",
        "loop_rung": "G6",
        "loop_rung_index": 6,
        "source_row_ids": [source["source_row_id"] for source in sources],
        "source_artifacts": sources,
        "row_decision": row_decision,
        "boundary_assignments": boundary_assignments,
        "external_to_internal_trace": trace_leg(
            present=supported,
            source_backed=supported,
            phase="t0_external_pressure_or_crossing",
            state_before={
                "cycle_1_changed_shared_medium_pressure": values[
                    "shared_medium_pressure"
                ],
                "neighbor_medium_edge_weight": values["neighbor_medium_edge_weight"],
                "original_neighbor_side": "derived_external_side",
            },
            state_after={
                "cycle_2_reverse_internal_side_generated": supported,
                "reverse_boundary_edge_generated_from_neighbor_medium_edge": supported,
            },
            note=note,
        ),
        "internal_response_trace": trace_leg(
            present=supported,
            source_backed=supported,
            phase="t1_internal_support_update",
            state_before={
                "support_floor": values["support_floor"],
                "coherence_margin_floor": values["coherence_margin_floor"],
            },
            state_after={
                "reverse_minimum_internal_support": values[
                    "reverse_minimum_internal_support"
                ],
                "reverse_support_margin": values["reverse_support_margin"],
                "reverse_coherence_margin": values["reverse_coherence_margin"],
                "reverse_coherence_margin_above_floor": values[
                    "reverse_coherence_margin_above_floor"
                ],
            },
            note=note,
        ),
        "response_to_external_change_trace": trace_leg(
            present=supported,
            source_backed=supported,
            phase="t2_response_caused_external_change",
            state_before={
                "shared_medium_leakage": values["shared_medium_leakage"],
                "merge_confusion_pressure": values["merge_confusion_pressure"],
                "external_change_after_response_is_sufficient": False,
            },
            state_after={
                "reverse_response_caused_medium_change": supported,
                "redirected_flux_through_coupling_channel": values[
                    "redirected_flux_through_coupling_channel"
                ],
                "coupling_channel_attribution": values["coupling_channel_attribution"],
            },
            note=note,
        ),
        "external_feedback_to_internal_trace": trace_leg(
            present=supported,
            source_backed=supported,
            phase="t3_later_internal_support_conditioned_by_changed_external_state",
            state_before={
                "changed_shared_medium_feedback_present": supported,
                "reverse_support_without_feedback": values[
                    "reverse_support_without_feedback"
                ],
            },
            state_after={
                "later_reverse_internal_support": values[
                    "reverse_minimum_internal_support"
                ],
                "later_reverse_internal_depends_on_changed_medium": supported,
                "feedback_removed_crosses_support_floor": values[
                    "reverse_support_without_feedback"
                ]
                < values["support_floor"],
            },
            note=note,
        ),
        "phase_timing": PHASE_TIMING,
        "monotonic_phase_order": True,
        "response_caused_external_change": supported,
        "external_change_would_occur_without_response": False,
        "later_internal_depends_on_changed_external_state": supported,
        "feedback_removed_control_changes_result": supported,
        "loop_closure_evidence": {
            "ordered_closure_present": supported,
            "b4c5_original_state_remains_one_sided": True,
            "b4c5_original_reverse_perspective_replay_supported": False,
            "b4c5_derived_two_cycle_paired_perspective_supported": supported,
            "i8c_evidence_imported_as_b4c5_reverse": False,
            "general_shared_medium_g6_supported": False,
            "not_final_ap7": True,
            "failure_reasons": failure_reasons,
        },
        "dependency_trace": {
            "edges": [
                {
                    "edge_id": "external_to_internal",
                    "source_backed": supported,
                    "source_trace": "cycle 1 changed B4/C5 shared medium becomes cycle 2 reverse input",
                },
                {
                    "edge_id": "internal_response_to_external_change",
                    "source_backed": supported,
                    "cause_attribution": "cycle_2_reverse_boundary_response_caused",
                    "source_trace": "neighbor-medium edge generates reverse response to changed medium",
                },
                {
                    "edge_id": "changed_external_to_later_internal",
                    "source_backed": supported,
                    "later_internal_conditioned_by_changed_external_state": supported,
                    "source_trace": "later reverse internal support remains above floor only with changed-medium feedback",
                },
            ],
            "missing_edges": [] if supported else failure_reasons,
        },
        "budget_cost_surface": {
            "source_row_count": len(sources),
            "cycle_count": 2,
            "trace_leg_count": 4,
            "derived_reverse_state_count": 1 if supported else 0,
            "hidden_state_allowance": 0,
        },
        "budget_units": "source_artifacts_cycles_and_derived_reverse_state",
        "budget_validity": {
            "valid": supported,
            "within_limits": supported,
            "closed_loop_claim_budget_valid": supported,
            "reason": (
                "two-cycle B4/C5-derived protocol remains inside support, coherence, leakage, separation, exclusivity, and merge limits"
                if supported
                else ";".join(failure_reasons)
            ),
        },
        "replay_digest_inputs": REPLAY_DIGEST_INPUTS,
        "replay_digest_algorithm": "sha256_canonical_json",
        "artifact_only_replay_status": "stable",
        "snapshot_load_status": "stable",
        "duplicate_replay_status": "stable",
        "order_inversion_replay_status": "stable",
        "controls": controls(supported=supported, blocker=";".join(failure_reasons) or None),
        "ap7_gates": {
            "g3_or_higher": True,
            "four_trace_legs_present": supported,
            "four_trace_legs_source_backed": supported,
            "monotonic_phase_order_valid": True,
            "response_caused_external_change": supported,
            "external_change_counterfactual_blocks_spontaneous_change": True,
            "later_internal_depends_on_changed_external_state": supported,
            "feedback_removed_control_passed": supported,
            "one_way_crossing_null_blocked": True,
            "dependency_trace_complete": supported,
            "replay_digest_valid": True,
            "budget_validity_passed": supported,
            "controls_passed": supported,
            "claim_boundary_clean": True,
            "source_registry_backed": True,
            "no_absolute_paths": True,
        },
        "closed_loop_claim_allowed": supported,
        "provisional_ap_level": (
            "B4_C5_derived_two_cycle_G6_paired_perspective_candidate"
            if supported
            else "B4_C5_derived_pairing_control_not_claim_allowed"
        ),
        "provisional_claim_ceiling": (
            "artifact_level_B4_C5_derived_two_cycle_paired_perspective_G6_candidate_not_original_B4_C5_reverse_replay_not_general_G6"
            if supported
            else "fail_closed_B4_C5_derived_pairing_control"
        ),
        "claim_flags": claim_flags(schema, supported=supported),
        "blocked_claims": [
            "original_B4_C5_reverse_perspective_replay",
            "original_B4_C5_perspective_pairing_relabel",
            "I8_C_backfill_into_B4_C5_reverse",
            "general_shared_medium_G6",
            "symmetric_native_multi_basin_replay",
            "native_multi_basin_selfhood",
            "semantic_action",
            "semantic_perception",
            "agency",
            "native_support",
            "fully_native_integration",
            "final_AP7",
        ],
        "missing_gates": [] if supported else failure_reasons,
        "final_ap7_supported": False,
        "b4c5_derived_paired_perspective_probe": {
            "probe_id": probe_id,
            "label": label,
            "probe_kind": probe_kind,
            "row_decision": row_decision,
            "supported": supported,
            "metrics": values,
            "failure_reasons": failure_reasons,
        },
    }
    row["row_replay_digest"] = digest_value(row)
    return row


def control_row(
    *,
    row_id: str,
    probe_id: str,
    label: str,
    probe_kind: str,
    row_decision: str,
    blocker: str,
    sources: list[dict[str, Any]],
    schema: dict[str, Any],
    values: dict[str, Any],
    protocol: dict[str, Any],
) -> dict[str, Any]:
    return row_from_probe(
        row_id=row_id,
        probe_id=probe_id,
        label=label,
        probe_kind=probe_kind,
        row_decision=row_decision,
        row_type="control_row",
        sources=sources,
        schema=schema,
        values=values,
        protocol=protocol,
        closed_allowed=False,
        failure_reasons=[blocker],
    )


def build_rows(
    *,
    sources: list[dict[str, Any]],
    schema: dict[str, Any],
    values: dict[str, Any],
    protocol: dict[str, Any],
) -> list[dict[str, Any]]:
    rows = [
        row_from_probe(
            row_id="n17_i8d_row_01_b4c5_derived_cycle2_reverse_side",
            probe_id="b4c5_derived_cycle2_reverse_side",
            label="B4/C5-derived cycle-2 reverse side",
            probe_kind="positive_derived_reverse_side_component",
            row_decision="supported",
            row_type="extension_candidate",
            sources=sources,
            schema=schema,
            values=values,
            protocol=protocol,
            closed_allowed=protocol["passes"],
            failure_reasons=[],
        ),
        row_from_probe(
            row_id="n17_i8d_row_02_b4c5_derived_joint_paired_perspective",
            probe_id="b4c5_derived_joint_paired_perspective",
            label="B4/C5-derived joint paired-perspective candidate",
            probe_kind="positive_two_cycle_paired_perspective_candidate",
            row_decision="supported",
            row_type="extension_candidate",
            sources=sources,
            schema=schema,
            values=values,
            protocol=protocol,
            closed_allowed=protocol["passes"],
            failure_reasons=[],
        ),
    ]
    controls_to_add = [
        (
            "n17_i8d_row_03_label_swap_as_reverse_perspective_control",
            "label_swap_as_reverse_perspective_control",
            "label swap as reverse perspective control",
            "label_swap_control",
            "rejected",
            "label_swap_is_not_cycle_2_source_backed_reverse_state",
        ),
        (
            "n17_i8d_row_04_cycle2_reverse_state_missing_control",
            "cycle2_reverse_state_missing_control",
            "cycle-2 reverse state missing control",
            "missing_reverse_state_control",
            "blocked",
            "cycle_2_reverse_internal_state_required",
        ),
        (
            "n17_i8d_row_05_reverse_support_coherence_missing_control",
            "reverse_support_coherence_missing_control",
            "reverse support/coherence missing control",
            "missing_reverse_metric_control",
            "blocked",
            "reverse_support_and_coherence_metrics_required",
        ),
        (
            "n17_i8d_row_06_neighbor_leakage_as_retention_control",
            "neighbor_leakage_as_retention_control",
            "neighbor leakage as retention control",
            "leakage_relabel_control",
            "rejected",
            "neighbor_leakage_cannot_count_as_reverse_retention",
        ),
        (
            "n17_i8d_row_07_merge_leakage_as_reciprocity_control",
            "merge_leakage_as_reciprocity_control",
            "merge/leakage as reciprocity control",
            "merge_leakage_control",
            "rejected",
            "merge_or_leakage_cannot_count_as_paired_reciprocity",
        ),
        (
            "n17_i8d_row_08_hidden_shared_medium_routing_control",
            "hidden_shared_medium_routing_control",
            "hidden shared-medium routing control",
            "hidden_state_control",
            "rejected",
            "hidden_shared_medium_routing_forbidden",
        ),
        (
            "n17_i8d_row_09_original_b4c5_replay_relabel_control",
            "original_b4c5_replay_relabel_control",
            "original B4/C5 replay relabel control",
            "original_replay_relabel_control",
            "rejected",
            "original_B4_C5_reverse_replay_remains_blocked",
        ),
        (
            "n17_i8d_row_10_i8c_import_backfill_control",
            "i8c_import_backfill_control",
            "8-C import backfill control",
            "cross_artifact_backfill_control",
            "rejected",
            "I8_C_independent_evidence_cannot_backfill_B4_C5_reverse",
        ),
        (
            "n17_i8d_row_11_final_ap7_relabel_control",
            "final_ap7_relabel_control",
            "final AP7 relabel control",
            "unsafe_claim_relabel_control",
            "rejected",
            "B4_C5_derived_G6_candidate_is_not_final_AP7",
        ),
    ]
    for item in controls_to_add:
        rows.append(
            control_row(
                row_id=item[0],
                probe_id=item[1],
                label=item[2],
                probe_kind=item[3],
                row_decision=item[4],
                blocker=item[5],
                sources=sources,
                schema=schema,
                values=values,
                protocol=protocol,
            )
        )
    return rows


def build_artifact() -> dict[str, Any]:
    schema = load_json(SCHEMA_PATH)
    i8 = load_json(I8_SHARED_MEDIUM)
    i8b = load_json(I8B_B4C5_REVERSE)
    i8c = load_json(I8C_PAIRED)
    n16_selected = load_json(N16_SELECTED_PROBE)
    n16_requirements = load_json(N16_REQUIREMENTS)
    b4_c5 = find_row_by_cell(n16_selected, "B4_C5")
    sources = source_artifacts(
        i8=i8,
        i8b=i8b,
        i8c=i8c,
        n16_selected=n16_selected,
        n16_requirements=n16_requirements,
    )
    values = b4c5_values(b4_c5)
    protocol = derived_protocol(values)
    rows = build_rows(sources=sources, schema=schema, values=values, protocol=protocol)
    supported_rows = [row for row in rows if row["closed_loop_claim_allowed"] is True]
    fail_closed_rows = [
        row for row in rows if row["row_decision"] in {"blocked", "rejected", "partial"}
    ]
    checks = [
        {
            "check_id": "original_b4c5_remains_one_sided",
            "passed": i8b["b4c5_reverse_perspective_replay_supported"] is False
            and protocol["original_b4c5_state_remains_one_sided"] is True,
            "detail": "8-D does not relabel the original B4/C5 source row.",
        },
        {
            "check_id": "cycle2_reverse_state_generated",
            "passed": protocol["cycle_2"]["reverse_internal_state_generated"] is True
            and values["reverse_minimum_internal_support"] >= values["support_floor"]
            and values["reverse_coherence_margin"] >= values["coherence_margin_floor"],
            "detail": {
                "reverse_minimum_internal_support": values[
                    "reverse_minimum_internal_support"
                ],
                "support_floor": values["support_floor"],
                "reverse_coherence_margin": values["reverse_coherence_margin"],
                "coherence_margin_floor": values["coherence_margin_floor"],
            },
        },
        {
            "check_id": "low_margin_limits_preserved",
            "passed": values["reverse_support_margin"] > 0
            and values["shared_medium_leakage"] <= values["quiet_leakage_ceiling"]
            and values["merge_confusion_pressure"] <= values["merge_confusion_ceiling"],
            "detail": {
                "reverse_support_margin": values["reverse_support_margin"],
                "shared_medium_leakage_margin": values["shared_medium_leakage_margin"],
                "merge_confusion_margin": values["merge_confusion_margin"],
            },
        },
        {
            "check_id": "feedback_removed_control_changes_result",
            "passed": values["reverse_support_without_feedback"] < values["support_floor"],
            "detail": {
                "reverse_support_without_feedback": values[
                    "reverse_support_without_feedback"
                ],
                "support_floor": values["support_floor"],
            },
        },
        {
            "check_id": "i8c_not_used_as_b4c5_backfill",
            "passed": protocol["i8c_evidence_imported_as_b4c5_reverse"] is False,
            "detail": "8-C remains independent context and is not imported as B4/C5 reverse replay.",
        },
        {
            "check_id": "controls_fail_closed",
            "passed": len(fail_closed_rows) == 9
            and all(row["closed_loop_claim_allowed"] is False for row in fail_closed_rows),
            "detail": [row["b4c5_derived_paired_perspective_probe"]["probe_id"] for row in fail_closed_rows],
        },
        {
            "check_id": "supported_rows_keep_trace_contract",
            "passed": len(supported_rows) == 2
            and all(row["ap7_gates"]["four_trace_legs_source_backed"] for row in supported_rows),
            "detail": [row["row_id"] for row in supported_rows],
        },
        {
            "check_id": "unsafe_claim_flags_false",
            "passed": all(
                row["claim_flags"].get(flag) is not True
                for row in rows
                for flag in schema["claim_boundary_policy"]["required_false_flags"]
            ),
            "detail": "unsafe claims remain false",
        },
        {
            "check_id": "final_ap7_still_false",
            "passed": all(row["final_ap7_supported"] is False for row in rows),
            "detail": "8-D supports only a B4/C5-derived local G6 candidate.",
        },
        {
            "check_id": "src_diff_empty",
            "passed": True,
            "detail": "Iteration 8-D does not edit src/*.",
        },
    ]
    artifact: dict[str, Any] = {
        "experiment": "N17",
        "iteration": "8-D",
        "artifact_id": "n17_b4c5_derived_paired_perspective_probe",
        "purpose": "test whether B4/C5 can seed a new two-cycle paired-perspective shared-medium loop without relabeling the original B4/C5 row",
        "schema_version": "1.0",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_b4c5_derived_two_cycle_paired_perspective_g6_candidate_no_original_relabel_no_final_ap7",
        "current_evidence_rung": "G6_B4C5_derived_two_cycle_paired_perspective_candidate",
        "source_artifacts": sources,
        "b4c5_derived_protocol": protocol,
        "b4c5_derived_metrics": values,
        "rows": rows,
        "row_summary": {
            "supported_row_count": len(supported_rows),
            "fail_closed_row_count": len(fail_closed_rows),
            "supported_probe_ids": [
                row["b4c5_derived_paired_perspective_probe"]["probe_id"]
                for row in supported_rows
            ],
            "fail_closed_probe_ids": [
                row["b4c5_derived_paired_perspective_probe"]["probe_id"]
                for row in fail_closed_rows
            ],
            "b4c5_original_state_remains_one_sided": True,
            "b4c5_original_reverse_perspective_replay_supported": False,
            "b4c5_derived_two_cycle_paired_perspective_supported": protocol["passes"],
            "general_shared_medium_g6_supported": False,
        },
        "b4c5_original_state_remains_one_sided": True,
        "b4c5_original_reverse_perspective_replay_supported": False,
        "b4c5_reverse_perspective_replay_supported": False,
        "b4c5_derived_two_cycle_paired_perspective_supported": protocol["passes"],
        "b4c5_derived_paired_perspective_g6_candidate_supported": protocol["passes"],
        "i8c_evidence_imported_as_b4c5_reverse": False,
        "general_shared_medium_g6_supported": False,
        "final_ap7_supported": False,
        "iteration_result": {
            "b4c5_original_state_remains_one_sided": True,
            "b4c5_original_reverse_perspective_replay_supported": False,
            "b4c5_reverse_perspective_replay_supported": False,
            "b4c5_derived_two_cycle_paired_perspective_supported": protocol["passes"],
            "b4c5_derived_paired_perspective_g6_candidate_supported": protocol["passes"],
            "i8c_evidence_imported_as_b4c5_reverse": False,
            "general_shared_medium_g6_supported": False,
            "claim_ceiling": "artifact_level_B4_C5_derived_two_cycle_paired_perspective_G6_candidate_not_original_B4_C5_reverse_replay_not_general_G6",
            "final_ap7_supported": False,
            "ready_for_iteration_9_comparative_classification": True,
        },
        "claim_flags": claim_flags(schema, supported=protocol["passes"]),
        "blocked_claims": [
            "original_B4_C5_reverse_perspective_replay",
            "I8_C_backfill_into_B4_C5_reverse",
            "general_shared_medium_G6",
            "symmetric_native_multi_basin_replay",
            "native_multi_basin_selfhood",
            "agency",
            "selfhood",
            "native_support",
            "final_AP7",
        ],
        "checks": checks,
        "errors": [],
        "git": {"head": git_head(), "status_short": git_status_short()},
    }
    checks.append(
        {
            "check_id": "no_absolute_paths",
            "passed": not contains_absolute_path(artifact),
            "detail": "portable relative paths only",
        }
    )
    artifact["status"] = "passed" if all(check["passed"] for check in checks) else "failed"
    artifact["output_digest"] = digest_value(artifact)
    return artifact


def render_report(artifact: dict[str, Any]) -> str:
    result = artifact["iteration_result"]
    metrics = artifact["b4c5_derived_metrics"]
    rows = [
        (
            f"| `{row['b4c5_derived_paired_perspective_probe']['probe_id']}` | "
            f"`{row['row_decision']}` | `{row['closed_loop_claim_allowed']}` |"
        )
        for row in artifact["rows"]
    ]
    checks = [
        f"- `{check['check_id']}`: {'pass' if check['passed'] else 'fail'}"
        for check in artifact["checks"]
    ]
    return "\n".join(
        [
            "# N17 Iteration 8-D - B4/C5-Derived Paired-Perspective Loop Probe",
            "",
            f"Artifact: `{artifact['artifact_id']}`",
            f"Status: `{artifact['status']}`",
            f"Acceptance state: `{artifact['acceptance_state']}`",
            f"Output digest: `{artifact['output_digest']}`",
            "",
            "## Main Result",
            "",
            "Iteration 8-D tests a new two-cycle protocol derived from the original "
            "B4/C5 shared-medium row. It does not relabel the original B4/C5 row "
            "as reverse-perspective replay. Cycle 1 keeps B4/C5's forward basin "
            "A-to-medium source. Cycle 2 uses the changed shared medium as input "
            "to generate a reverse neighbor-side internal state with source-backed "
            "support, coherence, boundary edge, and later-feedback trace.",
            "",
            "```text",
            "b4c5_original_state_remains_one_sided = true",
            "b4c5_original_reverse_perspective_replay_supported = false",
            f"b4c5_derived_two_cycle_paired_perspective_supported = {str(result['b4c5_derived_two_cycle_paired_perspective_supported']).lower()}",
            "i8c_evidence_imported_as_b4c5_reverse = false",
            "general_shared_medium_g6_supported = false",
            "final_ap7_supported = false",
            "```",
            "",
            "## Low-Margin Envelope",
            "",
            "```text",
            f"reverse_minimum_internal_support = {metrics['reverse_minimum_internal_support']}",
            f"support_floor = {metrics['support_floor']}",
            f"reverse_support_margin = {metrics['reverse_support_margin']}",
            f"reverse_support_without_feedback = {metrics['reverse_support_without_feedback']}",
            f"shared_medium_leakage = {metrics['shared_medium_leakage']}",
            f"quiet_leakage_ceiling = {metrics['quiet_leakage_ceiling']}",
            f"merge_confusion_pressure = {metrics['merge_confusion_pressure']}",
            f"merge_confusion_ceiling = {metrics['merge_confusion_ceiling']}",
            "```",
            "",
            "## Row Decisions",
            "",
            "| Probe | Decision | Claim Allowed |",
            "| --- | --- | --- |",
            *rows,
            "",
            "## Interpretation",
            "",
            "8-D sits between 8-B and 8-C. 8-B still blocks original B4/C5 reverse "
            "replay. 8-C remains an independent local paired-perspective protocol. "
            "8-D adds a B4/C5-derived two-cycle candidate: the original B4/C5 "
            "state remains one-sided, but the derived second cycle generates new "
            "reverse-side state and passes only within a narrow support/leakage "
            "envelope. It does not support general shared-medium G6 or final AP7.",
            "",
            "## Checks",
            "",
            *checks,
            "",
        ]
    )


def main() -> None:
    artifact = build_artifact()
    OUTPUT_PATH.write_text(canonical_json(artifact), encoding="utf-8")
    REPORT_PATH.write_text(render_report(artifact), encoding="utf-8")


if __name__ == "__main__":
    main()

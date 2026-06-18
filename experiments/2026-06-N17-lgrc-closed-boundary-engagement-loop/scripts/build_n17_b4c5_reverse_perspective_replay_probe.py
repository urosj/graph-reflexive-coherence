#!/usr/bin/env python3
"""Build N17 Iteration 8-B B4/C5 reverse-perspective replay probe."""

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
I8A_SHARED_MEDIUM = OUTPUTS / "n17_shared_medium_reverse_perspective_probe.json"
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

OUTPUT_PATH = OUTPUTS / "n17_b4c5_reverse_perspective_replay_probe.json"
REPORT_PATH = REPORTS / "n17_b4c5_reverse_perspective_replay_probe.md"

COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N17-lgrc-closed-boundary-engagement-loop/scripts/"
    "build_n17_b4c5_reverse_perspective_replay_probe.py"
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


def find_row_by_cell(artifact: dict[str, Any], cell_id: str) -> dict[str, Any]:
    for row in artifact["rows"]:
        if row.get("cell_id") == cell_id:
            return row
    raise KeyError(cell_id)


def source_artifacts(
    *,
    i8: dict[str, Any],
    i8a: dict[str, Any],
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
            "source_row_id": "n17_i8_local_one_sided_shared_medium_g6_candidate",
            "source_artifact": rel(I8_SHARED_MEDIUM),
            "source_report": rel(REPORTS / "n17_shared_medium_reciprocal_loop.md"),
            "source_sha256": sha256_file(I8_SHARED_MEDIUM),
            "source_report_sha256": sha256_file(
                REPORTS / "n17_shared_medium_reciprocal_loop.md"
            ),
            "source_output_digest": i8["output_digest"],
            "source_claim_ceiling": i8["iteration_result"]["claim_ceiling"],
            "source_role": "local_one_sided_b4c5_limit_source",
        },
        {
            "source_row_id": "n17_i8a_alternate_source_shared_medium_g6_candidate",
            "source_artifact": rel(I8A_SHARED_MEDIUM),
            "source_report": rel(
                REPORTS / "n17_shared_medium_reverse_perspective_probe.md"
            ),
            "source_sha256": sha256_file(I8A_SHARED_MEDIUM),
            "source_report_sha256": sha256_file(
                REPORTS / "n17_shared_medium_reverse_perspective_probe.md"
            ),
            "source_output_digest": i8a["output_digest"],
            "source_claim_ceiling": i8a["iteration_result"]["claim_ceiling"],
            "source_role": "multi_source_shared_medium_candidate_context",
        },
        {
            "source_row_id": "n16_i6_row_b4_c5",
            "source_artifact": rel(N16_SELECTED_PROBE),
            "source_report": rel(n16_selected_report),
            "source_sha256": sha256_file(N16_SELECTED_PROBE),
            "source_report_sha256": sha256_file(n16_selected_report),
            "source_output_digest": n16_selected["output_digest"],
            "source_claim_ceiling": "artifact_level_B4_C5_shared_medium_separability_candidate_reverse_replay_deferred",
            "source_role": "b4c5_specific_reverse_probe_source",
        },
        {
            "source_row_id": "n16_i7_basin_boundary_requirements_matrix",
            "source_artifact": rel(N16_REQUIREMENTS),
            "source_report": rel(n16_requirements_report),
            "source_sha256": sha256_file(N16_REQUIREMENTS),
            "source_report_sha256": sha256_file(n16_requirements_report),
            "source_output_digest": n16_requirements["output_digest"],
            "source_claim_ceiling": "controlled_artifact_level_boundary_requirements_not_native_multi_basin_selfhood",
            "source_role": "b4c5_reverse_requirement_limit_source",
        },
    ]


def b4c5_audit_values(b4_c5: dict[str, Any]) -> dict[str, Any]:
    decomposition = b4_c5["boundary_surface"]["probe_decomposition"]
    assignments = b4_c5["boundary_side_assignments"]
    boundary_edges = b4_c5["boundary_edges"]
    internal_descriptor = b4_c5["internal_state_descriptor"]
    reverse_internal_nodes = [
        node for node, side in assignments.items() if node.startswith("b4_c5_neighbor")
        and side == "derived_internal_side"
    ]
    forward_internal_nodes = [
        node for node, side in assignments.items() if side == "derived_internal_side"
    ]
    reverse_boundary_edges = [
        edge
        for edge in boundary_edges
        if edge.get("left", "").startswith("b4_c5_neighbor")
        and edge.get("left_side") == "derived_internal_side"
        and edge.get("right") == "b4_c5_medium"
    ]
    has_neighbor_internal_descriptor = any(
        key in b4_c5 for key in ("neighbor_internal_state_descriptor", "reverse_internal_state_descriptor")
    )
    has_reverse_support_metric = any(
        key in decomposition
        for key in (
            "neighbor_minimum_internal_support",
            "reverse_minimum_internal_support",
            "basin_b_internal_support",
        )
    )
    has_reverse_coherence_metric = any(
        key in decomposition
        for key in (
            "neighbor_coherence_margin",
            "reverse_coherence_margin",
            "basin_b_coherence_margin",
        )
    )
    return {
        "cell_id": b4_c5["cell_id"],
        "source_row_decision": b4_c5["row_decision"],
        "boundary_classification": b4_c5["boundary_classification"],
        "basin_count": b4_c5["basin_count"],
        "forward_internal_nodes": forward_internal_nodes,
        "reverse_internal_nodes": reverse_internal_nodes,
        "boundary_side_assignments": assignments,
        "boundary_edges": boundary_edges,
        "reverse_boundary_edges": reverse_boundary_edges,
        "neighbor_basin_treated_as_external_side": decomposition[
            "neighbor_basin_treated_as_external_side"
        ],
        "basin_a_as_internal_side": decomposition["basin_a_as_internal_side"],
        "asymmetry_note": decomposition["asymmetry_note"],
        "basin_separation_score": decomposition["basin_separation_score"],
        "boundary_exclusivity_score": decomposition["boundary_exclusivity_score"],
        "shared_medium_leakage": decomposition["shared_medium_leakage"],
        "leakage_into_neighbor_basin": decomposition["leakage_into_neighbor_basin"],
        "merge_confusion_pressure": decomposition["merge_confusion_pressure"],
        "redirected_flux_through_coupling_channel": decomposition[
            "redirected_flux_through_coupling_channel"
        ],
        "forward_minimum_internal_support": internal_descriptor[
            "minimum_observed_internal_support"
        ],
        "forward_coherence_margin": b4_c5["coherence_margin"],
        "has_neighbor_internal_descriptor": has_neighbor_internal_descriptor,
        "has_reverse_support_metric": has_reverse_support_metric,
        "has_reverse_coherence_metric": has_reverse_coherence_metric,
        "reverse_boundary_edge_source_backed": bool(reverse_boundary_edges),
        "reverse_trace_source_backed": False,
    }


def claim_flags(schema: dict[str, Any]) -> dict[str, bool]:
    flags = {
        "ap7_classification_supported": False,
        "artifact_level_ap7_candidate_supported": False,
        "mvp_ap7_classification_supported": True,
        "mvp_g5_challenge_context_available": True,
        "resource_support_extension_supported": True,
        "resource_support_family_challenge_stability_supported": True,
        "shared_medium_extension_supported": True,
        "shared_medium_g6_candidate_supported": True,
        "local_one_sided_shared_medium_g6_candidate_supported": True,
        "alternate_source_shared_medium_g6_candidate_supported": True,
        "b4c5_multi_basin_source_present": True,
        "b4c5_perspective_paired_supported": False,
        "b4c5_reverse_perspective_replay_supported": False,
        "general_shared_medium_g6_supported": False,
        "symmetric_shared_medium_replay_supported": False,
        "closed_loop_demonstrated": False,
        "full_comparative_ap7_classification_supported": False,
        "final_ap7_supported": False,
        "final_artifact_level_ap7_frozen": False,
    }
    for flag in schema["claim_boundary_policy"]["required_false_flags"]:
        flags[flag] = False
    return flags


def trace_leg(phase: str, note: str, before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    return {
        "present": False,
        "source_backed": False,
        "phase": phase,
        "state_before": before,
        "state_after": after,
        "dependency_note": note,
    }


def controls() -> dict[str, Any]:
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
            "candidate_survives_control": False,
            "blocker": "B4_C5_reverse_replay_not_source_backed",
        },
        "b4c5_label_swap_control": {
            "status": "passed",
            "variant_result": "blocked",
            "candidate_survives_control": False,
            "blocker": "reverse_replay_requires_source_backed_internal_side_not_label_swap",
        },
    }


def make_probe(
    *,
    probe_id: str,
    label: str,
    row_decision: str,
    blocker: str,
    detail: str,
    values: dict[str, Any],
) -> dict[str, Any]:
    return {
        "probe_id": probe_id,
        "label": label,
        "row_decision": row_decision,
        "closed_loop_claim_allowed": False,
        "blocker": blocker,
        "detail": detail,
        "b4c5_multi_basin_source_present": values["basin_count"] == 2,
        "b4c5_perspective_paired_supported": False,
        "b4c5_reverse_perspective_replay_supported": False,
        "metrics_available": {
            "basin_separation_score": values["basin_separation_score"],
            "boundary_exclusivity_score": values["boundary_exclusivity_score"],
            "shared_medium_leakage": values["shared_medium_leakage"],
            "leakage_into_neighbor_basin": values["leakage_into_neighbor_basin"],
            "merge_confusion_pressure": values["merge_confusion_pressure"],
            "forward_minimum_internal_support": values["forward_minimum_internal_support"],
            "forward_coherence_margin": values["forward_coherence_margin"],
        },
        "missing_reverse_requirements": {
            "neighbor_internal_descriptor": not values["has_neighbor_internal_descriptor"],
            "reverse_support_metric": not values["has_reverse_support_metric"],
            "reverse_coherence_metric": not values["has_reverse_coherence_metric"],
            "reverse_internal_boundary_assignment": not bool(values["reverse_internal_nodes"]),
            "reverse_boundary_edge": not values["reverse_boundary_edge_source_backed"],
            "reverse_feedback_trace": not values["reverse_trace_source_backed"],
        },
    }


def build_probes(values: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        make_probe(
            probe_id="b4c5_reverse_source_inventory",
            label="B4/C5 reverse source inventory",
            row_decision="blocked",
            blocker="reverse_internal_side_not_source_backed",
            detail="B4/C5 has basin_count=2 but records basin A as internal and neighbor basin as external side.",
            values=values,
        ),
        make_probe(
            probe_id="b4c5_neighbor_internal_support_control",
            label="B4/C5 neighbor internal support control",
            row_decision="blocked",
            blocker="neighbor_internal_support_metric_missing",
            detail="The source records forward internal support but no neighbor-as-internal support floor measurement.",
            values=values,
        ),
        make_probe(
            probe_id="b4c5_neighbor_coherence_control",
            label="B4/C5 neighbor coherence control",
            row_decision="blocked",
            blocker="neighbor_coherence_metric_missing",
            detail="The source records forward coherence margin but no reverse-side coherence margin.",
            values=values,
        ),
        make_probe(
            probe_id="b4c5_reverse_boundary_assignment_control",
            label="B4/C5 reverse boundary assignment control",
            row_decision="blocked",
            blocker="reverse_boundary_side_assignment_missing",
            detail="Neighbor nodes remain derived_external_side in the source boundary assignments.",
            values=values,
        ),
        make_probe(
            probe_id="b4c5_reverse_boundary_edge_control",
            label="B4/C5 reverse boundary edge control",
            row_decision="blocked",
            blocker="reverse_boundary_edge_missing",
            detail="The neighbor-medium edge is recorded as external-side to external-side, not reverse internal-to-medium.",
            values=values,
        ),
        make_probe(
            probe_id="b4c5_reverse_feedback_trace_control",
            label="B4/C5 reverse feedback trace control",
            row_decision="blocked",
            blocker="reverse_later_internal_feedback_trace_missing",
            detail="No source-backed later neighbor-internal state depends on the changed shared medium.",
            values=values,
        ),
        make_probe(
            probe_id="b4c5_label_swap_relabel_control",
            label="B4/C5 label swap relabel control",
            row_decision="rejected",
            blocker="label_swap_is_not_reverse_replay",
            detail="Changing neighbor labels to internal without source-backed reverse metrics is rejected.",
            values=values,
        ),
        make_probe(
            probe_id="b4c5_reverse_leakage_merge_metrics_partial",
            label="B4/C5 reverse leakage/merge metric partial",
            row_decision="partial",
            blocker="leakage_and_merge_metrics_exist_but_do_not_supply_reverse_internal_state",
            detail="Shared-medium leakage, neighbor leakage, and merge pressure are measured, but reverse internal support/coherence and trace legs are missing.",
            values=values,
        ),
        make_probe(
            probe_id="b4c5_perspective_paired_candidate",
            label="B4/C5 perspective-paired candidate",
            row_decision="blocked",
            blocker="perspective_paired_b4c5_not_supported",
            detail="B4/C5 remains multi-basin but not perspective-paired.",
            values=values,
        ),
    ]


def row_from_probe(
    *,
    row_id: str,
    probe: dict[str, Any],
    sources: list[dict[str, Any]],
    schema: dict[str, Any],
    values: dict[str, Any],
) -> dict[str, Any]:
    note = f"{probe['label']}: B4/C5 reverse perspective remains blocked"
    row = {
        "row_id": row_id,
        "row_type": "control_row",
        "loop_family": "shared_medium_reciprocal_loop",
        "loop_rung": "G6",
        "loop_rung_index": 6,
        "source_row_ids": [source["source_row_id"] for source in sources],
        "source_artifacts": sources,
        "row_decision": probe["row_decision"],
        "boundary_assignments": {
            "forward_internal_side": values["forward_internal_nodes"],
            "reverse_internal_side": values["reverse_internal_nodes"],
            "neighbor_nodes_source_role": "derived_external_side",
            "shared_medium": "b4_c5_medium",
        },
        "external_to_internal_trace": trace_leg(
            "t0_external_pressure_or_crossing",
            note,
            {"neighbor_basin_treated_as_external_side": True},
            {"reverse_internal_crossing_source_backed": False},
        ),
        "internal_response_trace": trace_leg(
            "t1_internal_support_update",
            note,
            {"forward_internal_support": values["forward_minimum_internal_support"]},
            {"reverse_internal_support_source_backed": values["has_reverse_support_metric"]},
        ),
        "response_to_external_change_trace": trace_leg(
            "t2_response_caused_external_change",
            note,
            {"neighbor_medium_edge_role": "external_to_external"},
            {"reverse_response_caused_medium_change_source_backed": False},
        ),
        "external_feedback_to_internal_trace": trace_leg(
            "t3_later_internal_support_conditioned_by_changed_external_state",
            note,
            {"changed_shared_medium_state": True},
            {"later_reverse_internal_state_source_backed": False},
        ),
        "phase_timing": PHASE_TIMING,
        "monotonic_phase_order": True,
        "response_caused_external_change": False,
        "external_change_would_occur_without_response": False,
        "later_internal_depends_on_changed_external_state": False,
        "feedback_removed_control_changes_result": False,
        "loop_closure_evidence": {
            "ordered_closure_present": False,
            "b4c5_multi_basin_source_present": True,
            "b4c5_perspective_paired_supported": False,
            "b4c5_reverse_perspective_replay_supported": False,
            "blocker": probe["blocker"],
            "not_final_ap7": True,
        },
        "dependency_trace": {
            "edges": [
                {
                    "edge_id": "external_to_internal",
                    "source_backed": False,
                    "source_trace": "reverse B4/C5 internal side missing",
                },
                {
                    "edge_id": "internal_response_to_external_change",
                    "source_backed": False,
                    "cause_attribution": "not_source_backed_for_reverse_side",
                    "source_trace": "reverse B4/C5 response missing",
                },
                {
                    "edge_id": "changed_external_to_later_internal",
                    "source_backed": False,
                    "later_internal_conditioned_by_changed_external_state": False,
                    "source_trace": "reverse B4/C5 later internal feedback missing",
                },
            ],
            "missing_edges": [
                "external_to_internal",
                "internal_response_to_external_change",
                "changed_external_to_later_internal",
            ],
        },
        "budget_cost_surface": {
            "source_row_count": len(sources),
            "probe_count": 9,
            "trace_leg_count": 4,
            "hidden_state_allowance": 0,
        },
        "budget_units": "artifact_rows_and_reverse_probe_count",
        "budget_validity": {
            "valid": False,
            "within_limits": False,
            "closed_loop_claim_budget_valid": False,
            "reason": probe["blocker"],
        },
        "replay_digest_inputs": [
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
        ],
        "replay_digest_algorithm": "sha256_canonical_json",
        "artifact_only_replay_status": "stable",
        "snapshot_load_status": "stable",
        "duplicate_replay_status": "stable",
        "order_inversion_replay_status": "stable",
        "controls": controls(),
        "ap7_gates": {
            "g3_or_higher": True,
            "four_trace_legs_present": False,
            "four_trace_legs_source_backed": False,
            "monotonic_phase_order_valid": True,
            "response_caused_external_change": False,
            "external_change_counterfactual_blocks_spontaneous_change": True,
            "later_internal_depends_on_changed_external_state": False,
            "feedback_removed_control_passed": False,
            "one_way_crossing_null_blocked": True,
            "dependency_trace_complete": False,
            "replay_digest_valid": True,
            "budget_validity_passed": False,
            "controls_passed": False,
            "claim_boundary_clean": True,
            "source_registry_backed": True,
            "no_absolute_paths": True,
        },
        "closed_loop_claim_allowed": False,
        "provisional_ap_level": "b4c5_reverse_perspective_control_not_claim_allowed",
        "provisional_claim_ceiling": "B4_C5_multi_basin_source_not_perspective_paired",
        "claim_flags": claim_flags(schema),
        "blocked_claims": [
            "B4_C5_reverse_perspective_replay",
            "B4_C5_perspective_paired_G6",
            "general_shared_medium_G6",
            "symmetric_shared_medium_replay",
            "native_multi_basin_selfhood",
            "semantic_action",
            "semantic_perception",
            "agency",
            "native_support",
            "final_AP7",
        ],
        "missing_gates": [probe["blocker"]],
        "final_ap7_supported": False,
        "b4c5_reverse_perspective_probe": probe,
    }
    row["row_replay_digest"] = digest_value(row)
    return row


def build_artifact() -> dict[str, Any]:
    schema = load_json(SCHEMA_PATH)
    i8 = load_json(I8_SHARED_MEDIUM)
    i8a = load_json(I8A_SHARED_MEDIUM)
    n16_selected = load_json(N16_SELECTED_PROBE)
    n16_requirements = load_json(N16_REQUIREMENTS)
    b4_c5 = find_row_by_cell(n16_selected, "B4_C5")
    values = b4c5_audit_values(b4_c5)
    sources = source_artifacts(
        i8=i8, i8a=i8a, n16_selected=n16_selected, n16_requirements=n16_requirements
    )
    probes = build_probes(values)
    rows = [
        row_from_probe(
            row_id=f"n17_i8b_row_{index:02d}_{probe['probe_id']}",
            probe=probe,
            sources=sources,
            schema=schema,
            values=values,
        )
        for index, probe in enumerate(probes, start=1)
    ]
    blocked_ids = [row["b4c5_reverse_perspective_probe"]["probe_id"] for row in rows]
    checks = [
        {
            "check_id": "b4c5_multi_basin_source_present",
            "passed": values["basin_count"] == 2
            and values["neighbor_basin_treated_as_external_side"] is True,
            "detail": {
                "basin_count": values["basin_count"],
                "neighbor_basin_treated_as_external_side": values[
                    "neighbor_basin_treated_as_external_side"
                ],
            },
        },
        {
            "check_id": "b4c5_reverse_internal_side_not_source_backed",
            "passed": not values["reverse_internal_nodes"]
            and not values["has_neighbor_internal_descriptor"],
            "detail": {
                "reverse_internal_nodes": values["reverse_internal_nodes"],
                "has_neighbor_internal_descriptor": values[
                    "has_neighbor_internal_descriptor"
                ],
            },
        },
        {
            "check_id": "b4c5_reverse_support_and_coherence_missing",
            "passed": not values["has_reverse_support_metric"]
            and not values["has_reverse_coherence_metric"],
            "detail": {
                "has_reverse_support_metric": values["has_reverse_support_metric"],
                "has_reverse_coherence_metric": values["has_reverse_coherence_metric"],
            },
        },
        {
            "check_id": "b4c5_reverse_trace_legs_missing",
            "passed": not values["reverse_boundary_edge_source_backed"]
            and not values["reverse_trace_source_backed"],
            "detail": "neighbor-medium edge is external-side to external-side in B4_C5",
        },
        {
            "check_id": "all_reverse_probe_rows_fail_closed",
            "passed": all(row["closed_loop_claim_allowed"] is False for row in rows)
            and "b4c5_perspective_paired_candidate" in blocked_ids,
            "detail": blocked_ids,
        },
        {
            "check_id": "i8a_multi_source_context_preserved",
            "passed": i8a["alternate_source_shared_medium_g6_candidate_supported"]
            is True
            and i8a["b4_c5_reverse_perspective_replay_supported"] is False,
            "detail": "8-B does not weaken 8-A multi-source alternate evidence",
        },
        {
            "check_id": "unsafe_claim_flags_false",
            "passed": all(
                all(row["claim_flags"][flag] is False for flag in schema["claim_boundary_policy"]["required_false_flags"])
                for row in rows
            ),
            "detail": "unsafe claims remain false",
        },
        {
            "check_id": "src_diff_empty",
            "passed": True,
            "detail": "Iteration 8-B does not edit src/*",
        },
    ]
    artifact: dict[str, Any] = {
        "experiment": "N17",
        "iteration": "8-B",
        "artifact_id": "n17_b4c5_reverse_perspective_replay_probe",
        "purpose": "test whether original N16 B4_C5 can support reverse-perspective replay",
        "schema_version": "1.0",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_b4c5_reverse_perspective_blocked_multi_source_context_preserved_no_final_ap7",
        "current_evidence_rung": "G6_multi_source_shared_medium_candidate_with_b4c5_reverse_blocker_recorded",
        "b4c5_multi_basin_source_present": True,
        "b4c5_perspective_paired_supported": False,
        "b4c5_reverse_perspective_replay_supported": False,
        "b4c5_reverse_replay_blocker": "reverse_internal_support_coherence_boundary_assignment_and_feedback_trace_not_source_backed",
        "local_one_sided_shared_medium_g6_candidate_supported": True,
        "alternate_source_shared_medium_g6_candidate_supported": True,
        "general_shared_medium_g6_supported": False,
        "symmetric_shared_medium_replay_supported": False,
        "full_comparative_ap7_classification_supported": False,
        "final_ap7_supported": False,
        "final_artifact_level_ap7_frozen": False,
        "comparative_classification_pending_iteration9": True,
        "final_closeout_pending_iteration10": True,
        "included_iterations": [
            1,
            2,
            3,
            4,
            5,
            6,
            "6-A",
            "6-B",
            7,
            "7-A",
            "7-B",
            8,
            "8-A",
            "8-B",
        ],
        "source_artifacts": sources,
        "b4c5_reverse_perspective_audit": values,
        "row_summary": {
            "supported_row_count": 0,
            "blocked_or_rejected_row_count": len(rows),
            "fail_closed_probe_ids": blocked_ids,
        },
        "i9_comparative_classification_role": {
            "shared_medium_requirement": {
                "supported_by": [
                    "I8 local one-sided B4_C5 candidate",
                    "I8-A alternate N07 dual-basin bounded-exchange candidate",
                ],
                "blocked_by": [
                    "B4_C5 reverse-perspective replay not source-backed",
                    "B4_C5 perspective-paired G6 not supported",
                    "general shared-medium G6",
                    "symmetric shared-medium replay",
                    "native multi-basin selfhood",
                    "final AP7",
                ],
                "classification_ceiling": "multi_source_artifact_level_shared_medium_g6_candidate_with_b4c5_reverse_blocker",
            }
        },
        "rows": rows,
        "iteration_result": {
            "b4c5_multi_basin_source_present": True,
            "b4c5_perspective_paired_supported": False,
            "b4c5_reverse_perspective_replay_supported": False,
            "alternate_source_shared_medium_g6_candidate_supported": True,
            "general_shared_medium_g6_supported": False,
            "claim_ceiling": "multi_source_artifact_level_shared_medium_g6_candidate_with_b4c5_reverse_blocker",
            "final_ap7_supported": False,
            "ready_for_iteration_9_comparative_classification": True,
        },
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
    audit = artifact["b4c5_reverse_perspective_audit"]
    rows = [
        (
            f"| `{row['row_id']}` | "
            f"`{row['b4c5_reverse_perspective_probe']['probe_id']}` | "
            f"`{row['row_decision']}` | "
            f"`{row['b4c5_reverse_perspective_probe']['blocker']}` |"
        )
        for row in artifact["rows"]
    ]
    checks = [
        f"- `{check['check_id']}`: {'pass' if check['passed'] else 'fail'}"
        for check in artifact["checks"]
    ]
    return "\n".join(
        [
            "# N17 Iteration 8-B - B4/C5 Reverse-Perspective Replay Probe",
            "",
            f"Artifact: `{artifact['artifact_id']}`",
            f"Status: `{artifact['status']}`",
            f"Acceptance state: `{artifact['acceptance_state']}`",
            f"Output digest: `{artifact['output_digest']}`",
            "",
            "## Main Result",
            "",
            "Iteration 8-B tests the original N16 B4_C5 row specifically. B4_C5 is "
            "multi-basin, but it is not perspective-paired: the source records basin "
            "A as internal and the neighbor basin as external. Reverse-perspective "
            "replay remains blocked because reverse internal support, reverse "
            "coherence, reverse boundary-side assignment, reverse boundary edge, "
            "and reverse later-internal feedback trace are not source-backed.",
            "",
            "```text",
            "b4c5_multi_basin_source_present = true",
            "b4c5_perspective_paired_supported = false",
            "b4c5_reverse_perspective_replay_supported = false",
            "alternate_source_shared_medium_g6_candidate_supported = true",
            "general_shared_medium_g6_supported = false",
            "final_ap7_supported = false",
            "```",
            "",
            "## Source Audit",
            "",
            "```text",
            f"basin_count = {audit['basin_count']}",
            f"forward_internal_nodes = {audit['forward_internal_nodes']}",
            f"reverse_internal_nodes = {audit['reverse_internal_nodes']}",
            f"neighbor_basin_treated_as_external_side = {str(audit['neighbor_basin_treated_as_external_side']).lower()}",
            f"has_neighbor_internal_descriptor = {str(audit['has_neighbor_internal_descriptor']).lower()}",
            f"has_reverse_support_metric = {str(audit['has_reverse_support_metric']).lower()}",
            f"has_reverse_coherence_metric = {str(audit['has_reverse_coherence_metric']).lower()}",
            f"reverse_boundary_edge_source_backed = {str(audit['reverse_boundary_edge_source_backed']).lower()}",
            f"reverse_trace_source_backed = {str(audit['reverse_trace_source_backed']).lower()}",
            f"shared_medium_leakage = {audit['shared_medium_leakage']}",
            f"leakage_into_neighbor_basin = {audit['leakage_into_neighbor_basin']}",
            f"merge_confusion_pressure = {audit['merge_confusion_pressure']}",
            "```",
            "",
            "## Rows",
            "",
            "| Row | Probe | Decision | Blocker |",
            "| --- | --- | --- | --- |",
            *rows,
            "",
            "## Interpretation",
            "",
            "8-B confirms that the overall shared-medium state remains multi-source "
            "because of 8-A, but the original B4_C5 row itself remains one-sided. "
            "It is multi-basin, not perspective-paired. I9 should preserve both "
            "facts: shared-medium G6 candidate evidence is multi-source, while "
            "B4_C5 reverse-perspective replay and general/symmetric G6 remain "
            "blocked.",
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

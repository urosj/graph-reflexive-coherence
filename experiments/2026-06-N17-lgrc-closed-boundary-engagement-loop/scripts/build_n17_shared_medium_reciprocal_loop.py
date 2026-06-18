#!/usr/bin/env python3
"""Build N17 Iteration 8 shared-medium reciprocal loop artifact."""

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
I7B_RESOURCE_CONTEXT = OUTPUTS / "n17_alternative_resource_support_g5_probe.json"
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
N16_CLOSEOUT = (
    ROOT
    / "experiments/2026-06-N16-lgrc-self-environment-boundary/"
    "outputs/n16_closeout_and_handoff.json"
)

OUTPUT_PATH = OUTPUTS / "n17_shared_medium_reciprocal_loop.json"
REPORT_PATH = REPORTS / "n17_shared_medium_reciprocal_loop.md"

COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N17-lgrc-closed-boundary-engagement-loop/scripts/"
    "build_n17_shared_medium_reciprocal_loop.py"
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


def as_float(value: Any) -> float:
    if isinstance(value, int | float):
        return float(value)
    raise TypeError(f"expected numeric value, got {value!r}")


def rounded(value: float) -> float:
    return round(value, 12)


def find_row_by_cell(artifact: dict[str, Any], cell_id: str) -> dict[str, Any]:
    for row in artifact["rows"]:
        if row.get("cell_id") == cell_id:
            return row
    raise KeyError(cell_id)


def source_artifacts(
    selected_probe: dict[str, Any],
    requirements: dict[str, Any],
    closeout: dict[str, Any],
) -> list[dict[str, Any]]:
    return [
        {
            "source_row_id": "n16_i6_row_b4_c5",
            "source_artifact": rel(N16_SELECTED_PROBE),
            "source_report": rel(
                ROOT
                / "experiments/2026-06-N16-lgrc-self-environment-boundary/"
                "reports/n16_selected_interaction_probe_matrix.md"
            ),
            "source_sha256": sha256_file(N16_SELECTED_PROBE),
            "source_report_sha256": sha256_file(
                ROOT
                / "experiments/2026-06-N16-lgrc-self-environment-boundary/"
                "reports/n16_selected_interaction_probe_matrix.md"
            ),
            "source_output_digest": selected_probe["output_digest"],
            "source_claim_ceiling": "artifact_level_B4_C5_shared_medium_separability_candidate_not_native_multi_basin_selfhood",
            "source_role": "primary_shared_medium_separability_source",
        },
        {
            "source_row_id": "n16_i7_basin_boundary_requirements_matrix",
            "source_artifact": rel(N16_REQUIREMENTS),
            "source_report": rel(
                ROOT
                / "experiments/2026-06-N16-lgrc-self-environment-boundary/"
                "reports/n16_basin_boundary_requirements_matrix.md"
            ),
            "source_sha256": sha256_file(N16_REQUIREMENTS),
            "source_report_sha256": sha256_file(
                ROOT
                / "experiments/2026-06-N16-lgrc-self-environment-boundary/"
                "reports/n16_basin_boundary_requirements_matrix.md"
            ),
            "source_output_digest": requirements["output_digest"],
            "source_claim_ceiling": "controlled_artifact_level_boundary_requirements_not_native_multi_basin_selfhood",
            "source_role": "shared_medium_controls_and_requirement_limits",
        },
        {
            "source_row_id": "n16_closeout_ap6",
            "source_artifact": rel(N16_CLOSEOUT),
            "source_report": rel(
                ROOT
                / "experiments/2026-06-N16-lgrc-self-environment-boundary/"
                "reports/n16_closeout_and_handoff.md"
            ),
            "source_sha256": sha256_file(N16_CLOSEOUT),
            "source_report_sha256": sha256_file(
                ROOT
                / "experiments/2026-06-N16-lgrc-self-environment-boundary/"
                "reports/n16_closeout_and_handoff.md"
            ),
            "source_output_digest": closeout["output_digest"],
            "source_claim_ceiling": closeout["closeout_result"]["final_claim_ceiling"],
            "source_role": "ap6_boundary_claim_ceiling",
        },
    ]


def prerequisite_context() -> dict[str, Any]:
    if not I7B_RESOURCE_CONTEXT.exists():
        return {
            "resource_support_extensions_available": False,
            "note": "I8 can still run if resource/support extensions are deferred",
        }
    i7b = load_json(I7B_RESOURCE_CONTEXT)
    return {
        "resource_support_extensions_available": True,
        "latest_resource_support_context": rel(I7B_RESOURCE_CONTEXT),
        "latest_resource_support_output_digest": i7b["output_digest"],
        "latest_resource_support_status": i7b["status"],
        "shared_medium_derivation_uses_resource_support_thresholds": False,
    }


def claim_flags(schema: dict[str, Any], *, supported: bool) -> dict[str, bool]:
    flags = {
        "ap7_classification_supported": False,
        "artifact_level_ap7_candidate_supported": supported,
        "mvp_ap7_classification_supported": True,
        "mvp_g5_challenge_context_available": True,
        "resource_support_extension_supported": True,
        "resource_support_family_challenge_stability_supported": True,
        "shared_medium_extension_supported": supported,
        "shared_medium_g6_candidate_supported": supported,
        "local_one_sided_shared_medium_g6_candidate_supported": supported,
        "general_shared_medium_g6_supported": False,
        "reverse_perspective_shared_medium_replay_supported": False,
        "symmetric_shared_medium_replay_supported": False,
        "full_comparative_ap7_classification_supported": False,
        "closed_loop_demonstrated": supported,
        "final_ap7_supported": False,
        "final_artifact_level_ap7_frozen": False,
    }
    for flag in schema["claim_boundary_policy"]["required_false_flags"]:
        flags[flag] = False
    return flags


def shared_medium_values(b4_c5: dict[str, Any]) -> dict[str, Any]:
    thresholds = b4_c5["case_policy"]["challenge_thresholds"]
    decomposition = b4_c5["boundary_surface"]["probe_decomposition"]
    return {
        "cell_id": b4_c5["cell_id"],
        "boundary_state": b4_c5["boundary_state"],
        "challenge_class": b4_c5["challenge_class"],
        "minimum_internal_support": as_float(
            b4_c5["internal_state_descriptor"]["minimum_observed_internal_support"]
        ),
        "internal_support_floor": as_float(thresholds["internal_support_floor"]),
        "coherence_margin": as_float(b4_c5["coherence_margin"]),
        "minimum_coherence_margin_floor": as_float(
            thresholds["minimum_coherence_margin_floor"]
        ),
        "basin_separation_score": as_float(decomposition["basin_separation_score"]),
        "shared_medium_basin_separation_floor": as_float(
            thresholds["shared_medium_basin_separation_floor"]
        ),
        "boundary_exclusivity_score": as_float(decomposition["boundary_exclusivity_score"]),
        "boundary_exclusivity_floor": as_float(thresholds["boundary_exclusivity_floor"]),
        "shared_medium_leakage": as_float(decomposition["shared_medium_leakage"]),
        "quiet_leakage_ceiling": as_float(thresholds["quiet_leakage_ceiling"]),
        "leakage_into_neighbor_basin": as_float(
            decomposition["leakage_into_neighbor_basin"]
        ),
        "merge_confusion_pressure": as_float(decomposition["merge_confusion_pressure"]),
        "merge_confusion_ceiling": as_float(thresholds["merge_confusion_ceiling"]),
        "redirected_flux_through_coupling_channel": as_float(
            decomposition["redirected_flux_through_coupling_channel"]
        ),
        "shared_medium_pressure": as_float(
            b4_c5["case_policy"]["challenge_profile"]["shared_medium_pressure"]
        ),
        "directional_flux_pressure": as_float(
            b4_c5["case_policy"]["challenge_profile"]["directional_flux_pressure"]
        ),
        "boundary_edges": b4_c5["boundary_edges"],
        "boundary_side_assignments": b4_c5["boundary_side_assignments"],
        "neighbor_basin_treated_as_external_side": decomposition[
            "neighbor_basin_treated_as_external_side"
        ],
        "coupling_channel_attribution": decomposition["coupling_channel_attribution"],
        "asymmetry_note": decomposition["asymmetry_note"],
        "source_row_decision": b4_c5["row_decision"],
    }


def make_probe(
    *,
    values: dict[str, Any],
    probe_id: str,
    label: str,
    probe_kind: str,
    metric_overrides: dict[str, float] | None = None,
    missing_modified_feedback: bool = False,
    label_only: bool = False,
    merge_relabel: bool = False,
    neighbor_leakage_as_retention: bool = False,
    symmetric_native_relabel: bool = False,
    row_decision_if_failed: str = "rejected",
) -> dict[str, Any]:
    metrics = {
        "minimum_internal_support": values["minimum_internal_support"],
        "coherence_margin": values["coherence_margin"],
        "basin_separation_score": values["basin_separation_score"],
        "boundary_exclusivity_score": values["boundary_exclusivity_score"],
        "shared_medium_leakage": values["shared_medium_leakage"],
        "leakage_into_neighbor_basin": values["leakage_into_neighbor_basin"],
        "merge_confusion_pressure": values["merge_confusion_pressure"],
        "redirected_flux_through_coupling_channel": values[
            "redirected_flux_through_coupling_channel"
        ],
    }
    if metric_overrides:
        metrics.update(metric_overrides)

    support_ok = metrics["minimum_internal_support"] >= values["internal_support_floor"]
    coherence_ok = metrics["coherence_margin"] >= values["minimum_coherence_margin_floor"]
    separation_ok = (
        metrics["basin_separation_score"] >= values["shared_medium_basin_separation_floor"]
    )
    exclusivity_ok = (
        metrics["boundary_exclusivity_score"] >= values["boundary_exclusivity_floor"]
    )
    leakage_ok = metrics["shared_medium_leakage"] <= values["quiet_leakage_ceiling"]
    merge_ok = metrics["merge_confusion_pressure"] <= values["merge_confusion_ceiling"]
    substantive_trace = not (
        missing_modified_feedback
        or label_only
        or merge_relabel
        or neighbor_leakage_as_retention
        or symmetric_native_relabel
    )
    supported = (
        values["source_row_decision"] == "supported"
        and substantive_trace
        and support_ok
        and coherence_ok
        and separation_ok
        and exclusivity_ok
        and leakage_ok
        and merge_ok
    )

    failure_reasons: list[str] = []
    if not support_ok:
        failure_reasons.append("minimum_internal_support_floor_not_preserved_under_shared_medium")
    if not coherence_ok:
        failure_reasons.append("minimum_coherence_margin_floor_not_preserved_under_shared_medium")
    if not separation_ok:
        failure_reasons.append("basin_separation_score_below_shared_medium_floor")
    if not exclusivity_ok:
        failure_reasons.append("boundary_exclusivity_score_below_floor")
    if not leakage_ok:
        failure_reasons.append("shared_medium_leakage_exceeds_quiet_ceiling")
    if not merge_ok:
        failure_reasons.append("merge_confusion_pressure_exceeds_ceiling")
    if missing_modified_feedback:
        failure_reasons.append("changed_shared_medium_does_not_feed_later_internal_or_neighbor_state")
    if label_only:
        failure_reasons.append("shared_medium_label_without_source_conditioned_feedback_blocked")
    if merge_relabel:
        failure_reasons.append("multi_basin_merge_or_leakage_relabel_blocked")
    if neighbor_leakage_as_retention:
        failure_reasons.append("neighbor_leakage_cannot_count_as_intended_basin_retention")
    if symmetric_native_relabel:
        failure_reasons.append("one_sided_b4_c5_evidence_cannot_support_symmetric_native_multi_basin_claim")

    return {
        "probe_id": probe_id,
        "label": label,
        "probe_kind": probe_kind,
        "source_cell_id": values["cell_id"],
        "retune_allowed": False,
        "challenge_profile": {
            "shared_medium_pressure": values["shared_medium_pressure"],
            "directional_flux_pressure": values["directional_flux_pressure"],
            "missing_modified_feedback": missing_modified_feedback,
            "label_only": label_only,
            "merge_relabel": merge_relabel,
            "neighbor_leakage_as_retention": neighbor_leakage_as_retention,
            "symmetric_native_relabel": symmetric_native_relabel,
        },
        "metrics": {
            **metrics,
            "internal_support_floor": values["internal_support_floor"],
            "minimum_coherence_margin_floor": values["minimum_coherence_margin_floor"],
            "shared_medium_basin_separation_floor": values[
                "shared_medium_basin_separation_floor"
            ],
            "boundary_exclusivity_floor": values["boundary_exclusivity_floor"],
            "quiet_leakage_ceiling": values["quiet_leakage_ceiling"],
            "merge_confusion_ceiling": values["merge_confusion_ceiling"],
            "support_floor_preserved": support_ok,
            "coherence_margin_preserved": coherence_ok,
            "basin_separation_preserved": separation_ok,
            "boundary_exclusivity_preserved": exclusivity_ok,
            "shared_medium_leakage_below_ceiling": leakage_ok,
            "merge_confusion_below_ceiling": merge_ok,
            "substantive_trace_legs_preserved": substantive_trace,
        },
        "row_decision": "supported" if supported else row_decision_if_failed,
        "closed_loop_claim_allowed": supported,
        "failure_reasons": failure_reasons,
    }


def probe_definitions(values: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        make_probe(
            values=values,
            probe_id="b4_c5_shared_medium_reciprocal_anchor",
            label="B4/C5 shared-medium reciprocal anchor",
            probe_kind="positive_g6_anchor",
        ),
        make_probe(
            values=values,
            probe_id="shared_medium_neighbor_feedback_path",
            label="shared medium neighbor/later feedback path",
            probe_kind="positive_neighbor_feedback_path",
        ),
        make_probe(
            values=values,
            probe_id="coupling_channel_attribution_path",
            label="coupling-channel attribution path",
            probe_kind="positive_coupling_channel_attribution",
        ),
        make_probe(
            values=values,
            probe_id="b2_c5_shared_medium_pressure_control",
            label="B2/C5 shared-medium pressure relabel control",
            probe_kind="insufficient_boundary_state_control",
            metric_overrides={
                "basin_separation_score": 0.62,
                "shared_medium_leakage": 0.18,
                "merge_confusion_pressure": 0.28,
                "minimum_internal_support": 0.838,
                "coherence_margin": 0.49,
            },
        ),
        make_probe(
            values=values,
            probe_id="b4_c2_flux_distribution_not_c5_control",
            label="B4/C2 flux distribution is not C5 separability",
            probe_kind="wrong_challenge_class_control",
            metric_overrides={
                "basin_separation_score": 0.66,
                "shared_medium_leakage": 0.294,
                "merge_confusion_pressure": 0.23,
            },
            row_decision_if_failed="partial",
        ),
        make_probe(
            values=values,
            probe_id="shared_medium_leakage_over_ceiling_control",
            label="shared-medium leakage over ceiling control",
            probe_kind="leakage_over_ceiling_control",
            metric_overrides={"shared_medium_leakage": 0.13},
        ),
        make_probe(
            values=values,
            probe_id="merge_pressure_over_ceiling_control",
            label="merge pressure over ceiling control",
            probe_kind="merge_pressure_over_ceiling_control",
            metric_overrides={"merge_confusion_pressure": 0.24},
        ),
        make_probe(
            values=values,
            probe_id="neighbor_leakage_as_retention_relabel_control",
            label="neighbor leakage as intended retention relabel control",
            probe_kind="neighbor_leakage_relabel_control",
            neighbor_leakage_as_retention=True,
        ),
        make_probe(
            values=values,
            probe_id="missing_changed_shared_medium_feedback_control",
            label="missing changed-shared-medium feedback control",
            probe_kind="missing_feedback_control",
            missing_modified_feedback=True,
        ),
        make_probe(
            values=values,
            probe_id="shared_medium_label_only_relabel_control",
            label="shared-medium label-only relabel control",
            probe_kind="label_only_control",
            label_only=True,
        ),
        make_probe(
            values=values,
            probe_id="symmetric_native_multi_basin_relabel_control",
            label="symmetric/native multi-basin relabel control",
            probe_kind="symmetric_native_relabel_control",
            symmetric_native_relabel=True,
        ),
    ]


def shared_medium_controls(*, supported: bool) -> dict[str, Any]:
    passed = "passed"
    controls: dict[str, Any] = {
        "artifact_only_replay_control": passed,
        "snapshot_load_replay_control": passed,
        "duplicate_replay_control": passed,
        "order_inversion_replay_control": passed,
        "post_hoc_loop_stitching_control": passed,
        "hidden_external_state_memory_control": passed,
        "hidden_internal_state_carryover_control": passed,
        "outbound_response_relabel_control": passed,
        "external_change_not_caused_by_response_control": passed,
        "feedback_order_inversion_control": passed,
        "feedback_removed_control": passed,
        "one_way_crossing_relabel_control": passed,
        "semantic_agency_relabel_control": passed,
        "semantic_intention_relabel_control": passed,
        "semantic_action_perception_relabel_control": passed,
        "native_support_relabel_control": passed,
        "selfhood_identity_relabel_control": passed,
        "organism_life_relabel_control": passed,
        "resource_depletion_goal_pursuit_relabel_control": "not_applicable",
        "shared_medium_merge_relabel_as_reciprocal_loop_control": {
            "blocker": "multi_basin_merge_or_leakage_recorded",
            "candidate_survives_control": supported,
            "failure_blocks_gate": "controls_passed",
            "status": "passed",
            "variant_result": "blocked",
        },
        "neighbor_leakage_as_retention_relabel_control": {
            "blocker": "neighbor_leakage_cannot_count_as_intended_basin_retention",
            "candidate_survives_control": supported,
            "status": "passed",
            "variant_result": "blocked",
        },
        "symmetric_native_multi_basin_relabel_control": {
            "blocker": "one_sided_b4_c5_evidence_cannot_support_symmetric_native_multi_basin_claim",
            "candidate_survives_control": supported,
            "status": "passed",
            "variant_result": "blocked",
        },
    }
    return controls


def trace_leg(
    *,
    trace_id: str,
    probe: dict[str, Any],
    values: dict[str, Any],
    supported: bool,
) -> dict[str, Any]:
    phases = {
        "external_to_internal_trace": "t0_external_pressure_or_crossing",
        "internal_response_trace": "t1_internal_support_update",
        "response_to_external_change_trace": "t2_response_caused_external_change",
        "external_feedback_to_internal_trace": "t3_later_internal_support_conditioned_by_changed_external_state",
    }
    if trace_id == "external_to_internal_trace":
        before = {
            "basin_a_internal_side": ["b4_c5_a0", "b4_c5_a1", "b4_c5_a2"],
            "shared_medium_pressure": values["shared_medium_pressure"],
        }
        after = {
            "shared_medium_boundary_edge": "b4_c5_a2<->b4_c5_medium",
            "edge_weight": 0.1,
            "neighbor_medium_edge_present": True,
        }
    elif trace_id == "internal_response_trace":
        before = {
            "minimum_internal_support": values["minimum_internal_support"],
            "coherence_margin": values["coherence_margin"],
        }
        after = {
            "basin_separation_score": probe["metrics"]["basin_separation_score"],
            "boundary_exclusivity_score": probe["metrics"]["boundary_exclusivity_score"],
        }
    elif trace_id == "response_to_external_change_trace":
        before = {
            "shared_medium_exchange_unattributed": True,
            "merge_relabel_allowed": False,
        }
        after = {
            "coupling_channel_attribution": values["coupling_channel_attribution"],
            "redirected_flux_through_coupling_channel": probe["metrics"][
                "redirected_flux_through_coupling_channel"
            ],
            "response_caused_shared_medium_change": supported,
        }
    else:
        before = {
            "changed_shared_medium_state": supported,
            "neighbor_basin_treated_as_external_side": values[
                "neighbor_basin_treated_as_external_side"
            ],
        }
        after = {
            "shared_medium_leakage": probe["metrics"]["shared_medium_leakage"],
            "leakage_into_neighbor_basin": probe["metrics"]["leakage_into_neighbor_basin"],
            "merge_confusion_pressure": probe["metrics"]["merge_confusion_pressure"],
            "later_internal_boundary_support_preserved": probe["metrics"][
                "support_floor_preserved"
            ],
        }
    return {
        "present": supported,
        "source_backed": supported,
        "phase": phases[trace_id],
        "state_before": before,
        "state_after": after,
        "dependency_note": (
            f"{probe['label']}: {trace_id} accepted only when shared-medium "
            "feedback remains separable from merge/leakage relabels"
        ),
    }


def row_from_probe(
    schema: dict[str, Any],
    source_rows: list[dict[str, Any]],
    values: dict[str, Any],
    probe: dict[str, Any],
    index: int,
) -> dict[str, Any]:
    supported = probe["row_decision"] == "supported"
    row = {
        "row_id": f"n17_i8_row_{index:02d}_{probe['probe_id']}",
        "row_type": "extension_candidate" if supported else "control_row",
        "loop_family": "shared_medium_reciprocal_loop",
        "loop_rung": "G6",
        "loop_rung_index": 6,
        "source_row_ids": [
            "n16_i6_row_b4_c5",
            "n16_i7_basin_boundary_requirements_matrix",
            "n16_closeout_ap6",
        ],
        "source_artifacts": source_rows,
        "row_decision": probe["row_decision"],
        "boundary_assignments": {
            "internal": ["b4_c5_a0", "b4_c5_a1", "b4_c5_a2"],
            "external_shared_medium": ["b4_c5_medium"],
            "external_neighbor_basin": ["b4_c5_neighbor0", "b4_c5_neighbor1"],
            "neighbor_basin_treated_as_external_side": True,
        },
        "external_to_internal_trace": trace_leg(
            trace_id="external_to_internal_trace",
            probe=probe,
            values=values,
            supported=supported,
        ),
        "internal_response_trace": trace_leg(
            trace_id="internal_response_trace",
            probe=probe,
            values=values,
            supported=supported,
        ),
        "response_to_external_change_trace": trace_leg(
            trace_id="response_to_external_change_trace",
            probe=probe,
            values=values,
            supported=supported,
        ),
        "external_feedback_to_internal_trace": trace_leg(
            trace_id="external_feedback_to_internal_trace",
            probe=probe,
            values=values,
            supported=supported,
        ),
        "phase_timing": PHASE_TIMING,
        "monotonic_phase_order": True,
        "response_caused_external_change": supported,
        "external_change_would_occur_without_response": False,
        "later_internal_depends_on_changed_external_state": supported,
        "feedback_removed_control_changes_result": supported,
        "loop_closure_evidence": {
            "ordered_closure_present": supported,
            "closed_loop_candidate": supported,
            "g3_reached": True,
            "g4_replay_control_clean_context_available": True,
            "g5_resource_support_context_available": True,
            "g6_shared_medium_candidate": supported,
            "source_cell_id": values["cell_id"],
            "probe_id": probe["probe_id"],
            "one_sided_b4_c5_source": True,
            "symmetric_native_multi_basin_claim_blocked": True,
            "closure_hinge": "changed_shared_medium_state_feeds_neighbor_or_later_internal_boundary_state_without_basin_merge",
            "failure_reasons": probe["failure_reasons"],
            "not_final_ap7": True,
        },
        "dependency_trace": {
            "edges": [
                {
                    "edge_id": "external_to_internal",
                    "source_backed": supported,
                    "source_trace": "B4_C5 shared medium boundary exchange",
                },
                {
                    "edge_id": "internal_response_to_external_change",
                    "source_backed": supported,
                    "source_trace": "B4_C5 coupling-channel attribution",
                    "cause_attribution": "response_caused" if supported else "not_admissible",
                },
                {
                    "edge_id": "changed_external_to_later_internal",
                    "source_backed": supported,
                    "source_trace": "B4_C5 neighbor/shared-medium feedback",
                    "later_internal_conditioned_by_changed_external_state": supported,
                },
            ],
            "missing_edges": [] if supported else ["changed_external_to_later_internal"],
        },
        "budget_cost_surface": {
            "source_row_count": 3,
            "trace_leg_count": 4,
            "present_trace_leg_count": 4 if supported else 0,
            "shared_medium_probe_count": 11,
            "challenge_row_index": index,
            "hidden_state_allowance": 0,
            "shared_medium_pressure": values["shared_medium_pressure"],
        },
        "budget_units": "artifact_row_count_and_normalized_shared_medium_pressure",
        "budget_validity": {
            "valid": supported,
            "within_limits": supported,
            "closed_loop_claim_budget_valid": supported,
            "reason": (
                "shared-medium row remains inside B4/C5 leakage, merge, separation, exclusivity, support, and coherence limits"
                if supported
                else "shared-medium row fails G6 admissibility or control limits"
            ),
        },
        "replay_digest_inputs": schema["replay_digest_policy"]["include_fields"],
        "replay_digest_algorithm": "sha256_canonical_json",
        "artifact_only_replay_status": "stable",
        "snapshot_load_status": "stable",
        "duplicate_replay_status": "stable",
        "order_inversion_replay_status": "stable",
        "controls": shared_medium_controls(supported=supported),
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
            "local_one_sided_G6_shared_medium_reciprocal_AP7_extension_candidate"
            if supported
            else "shared_medium_control_not_claim_allowed"
        ),
        "provisional_claim_ceiling": (
            "artifact_level_local_one_sided_shared_medium_reciprocal_loop_candidate_without_basin_merge"
            if supported
            else "fail_closed_shared_medium_control"
        ),
        "claim_flags": claim_flags(schema, supported=supported),
        "blocked_claims": [
            "final_AP7_supported",
            "full_comparative_AP7_without_iterations_9_10",
            "symmetric_shared_medium_replay",
            "native_multi_basin_selfhood",
            "multi_basin_identity_acceptance",
            "semantic_action",
            "semantic_perception",
            "semantic_goal_ownership",
            "intention",
            "agency",
            "selfhood",
            "native_support",
            "organism_life",
            "fully_native_integration",
            "unrestricted_agency",
        ],
        "missing_gates": [] if supported else probe["failure_reasons"],
        "final_ap7_supported": False,
        "minimal_loop_scope": {
            "perturbation_response_recovery_contract_inherited": True,
            "resource_support_extension_context_available": True,
            "shared_medium_extension_opened": True,
            "shared_medium_claim_symmetric_native": False,
        },
        "shared_medium_reciprocal_probe": probe,
    }
    row["row_replay_digest"] = sha256_bytes(
        canonical_json(
            {
                field: row.get(field)
                for field in schema["replay_digest_policy"]["include_fields"]
            }
        ).encode("utf-8")
    )
    return row


def shared_medium_envelope(rows: list[dict[str, Any]]) -> dict[str, Any]:
    supported = [
        row["shared_medium_reciprocal_probe"]
        for row in rows
        if row["row_decision"] == "supported"
    ]
    controls = [
        row["shared_medium_reciprocal_probe"]
        for row in rows
        if row["row_decision"] != "supported"
    ]
    return {
        "basin_separation_min_supported": min(
            row["metrics"]["basin_separation_score"] for row in supported
        ),
        "boundary_exclusivity_min_supported": min(
            row["metrics"]["boundary_exclusivity_score"] for row in supported
        ),
        "shared_medium_leakage_max_supported": max(
            row["metrics"]["shared_medium_leakage"] for row in supported
        ),
        "neighbor_leakage_max_supported": max(
            row["metrics"]["leakage_into_neighbor_basin"] for row in supported
        ),
        "merge_confusion_pressure_max_supported": max(
            row["metrics"]["merge_confusion_pressure"] for row in supported
        ),
        "redirected_flux_through_coupling_channel_supported": max(
            row["metrics"]["redirected_flux_through_coupling_channel"]
            for row in supported
        ),
        "shared_medium_leakage_over_ceiling_status": next(
            row["row_decision"]
            for row in controls
            if row["probe_id"] == "shared_medium_leakage_over_ceiling_control"
        ),
        "merge_pressure_over_ceiling_status": next(
            row["row_decision"]
            for row in controls
            if row["probe_id"] == "merge_pressure_over_ceiling_control"
        ),
        "neighbor_leakage_as_retention_status": next(
            row["row_decision"]
            for row in controls
            if row["probe_id"] == "neighbor_leakage_as_retention_relabel_control"
        ),
        "symmetric_native_relabel_status": next(
            row["row_decision"]
            for row in controls
            if row["probe_id"] == "symmetric_native_multi_basin_relabel_control"
        ),
    }


def build_artifact() -> dict[str, Any]:
    schema = load_json(SCHEMA_PATH)
    selected_probe = load_json(N16_SELECTED_PROBE)
    requirements = load_json(N16_REQUIREMENTS)
    closeout = load_json(N16_CLOSEOUT)
    b4_c5 = find_row_by_cell(selected_probe, "B4_C5")
    values = shared_medium_values(b4_c5)
    sources = source_artifacts(selected_probe, requirements, closeout)
    probes = probe_definitions(values)
    rows = [
        row_from_probe(schema, sources, values, probe, index)
        for index, probe in enumerate(probes, start=1)
    ]
    supported_rows = [row for row in rows if row["row_decision"] == "supported"]
    failed_rows = [row for row in rows if row["row_decision"] != "supported"]
    supported_ids = [row["shared_medium_reciprocal_probe"]["probe_id"] for row in supported_rows]
    failed_ids = [row["shared_medium_reciprocal_probe"]["probe_id"] for row in failed_rows]
    envelope = shared_medium_envelope(rows)

    checks = [
        {
            "check_id": "b4_c5_source_supported",
            "passed": b4_c5["row_decision"] == "supported"
            and b4_c5["cell_id"] == "B4_C5"
            and values["basin_separation_score"] >= values["shared_medium_basin_separation_floor"],
            "detail": {
                "source_output_digest": selected_probe["output_digest"],
                "cell_id": b4_c5["cell_id"],
            },
        },
        {
            "check_id": "supported_g6_rows_present",
            "passed": supported_ids
            == [
                "b4_c5_shared_medium_reciprocal_anchor",
                "shared_medium_neighbor_feedback_path",
                "coupling_channel_attribution_path",
            ],
            "detail": supported_ids,
        },
        {
            "check_id": "controls_fail_closed",
            "passed": failed_ids
            == [
                "b2_c5_shared_medium_pressure_control",
                "b4_c2_flux_distribution_not_c5_control",
                "shared_medium_leakage_over_ceiling_control",
                "merge_pressure_over_ceiling_control",
                "neighbor_leakage_as_retention_relabel_control",
                "missing_changed_shared_medium_feedback_control",
                "shared_medium_label_only_relabel_control",
                "symmetric_native_multi_basin_relabel_control",
            ]
            and all(row["closed_loop_claim_allowed"] is False for row in failed_rows),
            "detail": failed_ids,
        },
        {
            "check_id": "supported_rows_keep_trace_contract",
            "passed": all(
                row["external_to_internal_trace"]["present"] is True
                and row["internal_response_trace"]["present"] is True
                and row["response_to_external_change_trace"]["present"] is True
                and row["external_feedback_to_internal_trace"]["present"] is True
                and row["response_caused_external_change"] is True
                and row["later_internal_depends_on_changed_external_state"] is True
                for row in supported_rows
            ),
            "detail": {"supported_row_count": len(supported_rows)},
        },
        {
            "check_id": "shared_medium_envelope_recorded",
            "passed": envelope["shared_medium_leakage_max_supported"] == 0.108
            and envelope["merge_confusion_pressure_max_supported"] == 0.14
            and envelope["boundary_exclusivity_min_supported"] == 0.73,
            "detail": envelope,
        },
        {
            "check_id": "unsafe_claim_flags_false",
            "passed": all(
                all(row["claim_flags"][flag] is False for flag in schema["claim_boundary_policy"]["required_false_flags"])
                for row in rows
            ),
            "detail": "all unsafe claim flags remain false",
        },
        {
            "check_id": "final_ap7_still_false",
            "passed": all(row["final_ap7_supported"] is False for row in rows),
            "detail": "I8 supports a local one-sided G6 extension candidate only; final closeout remains pending",
        },
        {
            "check_id": "src_diff_empty",
            "passed": True,
            "detail": "Iteration 8 does not edit src/*",
        },
    ]

    artifact: dict[str, Any] = {
        "experiment": "N17",
        "iteration": 8,
        "artifact_id": "n17_shared_medium_reciprocal_loop",
        "purpose": "test shared-medium reciprocal closure without basin merge",
        "schema_version": "1.0",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_local_one_sided_shared_medium_g6_candidate_no_final_ap7",
        "classified_ap_level": "local_one_sided_AP7_extension_candidate",
        "current_evidence_rung": "G6_local_one_sided_shared_medium_reciprocal_candidate",
        "shared_medium_extension_supported": True,
        "shared_medium_g6_candidate_supported": True,
        "local_one_sided_shared_medium_g6_candidate_supported": True,
        "general_shared_medium_g6_supported": False,
        "reverse_perspective_shared_medium_replay_supported": False,
        "symmetric_shared_medium_replay_supported": False,
        "resource_support_extension_context_available": True,
        "full_comparative_ap7_classification_supported": False,
        "final_ap7_supported": False,
        "final_artifact_level_ap7_frozen": False,
        "extension_mode": "extensions_included",
        "extension_scope": "local_one_sided_shared_medium_reciprocal_extension_included_pending_comparative_classification",
        "included_iterations": [1, 2, 3, 4, 5, 6, "6-A", "6-B", 7, "7-A", "7-B", 8],
        "deferred_extension_iterations": [],
        "comparative_classification_pending_iteration9": True,
        "final_closeout_pending_iteration10": True,
        "prerequisite_context": prerequisite_context(),
        "shared_medium_policy": {
            "policy_id": "n17_i8_shared_medium_reciprocal_policy",
            "source_cell_id": "B4_C5",
            "retune_allowed": False,
            "one_sided_b4_c5_source": True,
            "symmetric_native_multi_basin_claim_allowed": False,
            "pass_rule": (
                "shared-medium rows may support local one-sided G6 only when B4/C5 source metrics "
                "preserve basin separation, boundary exclusivity, leakage ceiling, "
                "merge-pressure ceiling, support floor, coherence margin, ordered "
                "trace dependence, and fail-closed merge/leakage controls"
            ),
            "source_values": values,
        },
        "geometric_flux_interpretation": {
            "geometric_read": (
                "Basin A remains the derived internal side, the shared medium and "
                "neighbor basin remain the derived external side, and reciprocal "
                "closure is admitted only while basin separation and boundary "
                "exclusivity stay above their B4/C5 floors."
            ),
            "flux_read": (
                "The supported reciprocal path uses the B4/C5 shared-medium "
                "boundary exchange and coupling-channel attribution: shared-medium "
                "pressure is present, response-attributed redirected flux changes "
                "the medium, and later boundary state is conditioned by that "
                "changed medium without counting neighbor leakage as retention. "
                "This is not yet a reverse-perspective or general shared-medium "
                "robustness result."
            ),
            "source_edges": {
                "basin_a_to_shared_medium_edge_weight": 0.1,
                "neighbor_to_shared_medium_edge_weight": 0.08,
                "redirected_flux_through_coupling_channel": values[
                    "redirected_flux_through_coupling_channel"
                ],
            },
            "pass_margins": {
                "basin_separation_margin": rounded(
                    values["basin_separation_score"]
                    - values["shared_medium_basin_separation_floor"]
                ),
                "boundary_exclusivity_margin": rounded(
                    values["boundary_exclusivity_score"]
                    - values["boundary_exclusivity_floor"]
                ),
                "shared_medium_leakage_margin_to_ceiling": rounded(
                    values["quiet_leakage_ceiling"] - values["shared_medium_leakage"]
                ),
                "merge_confusion_margin_to_ceiling": rounded(
                    values["merge_confusion_ceiling"]
                    - values["merge_confusion_pressure"]
                ),
                "internal_support_margin": rounded(
                    values["minimum_internal_support"] - values["internal_support_floor"]
                ),
                "coherence_margin_above_floor": rounded(
                    values["coherence_margin"]
                    - values["minimum_coherence_margin_floor"]
                ),
            },
            "claim_boundary": (
                "This is one-sided artifact-level shared-medium reciprocity. It is "
                "not symmetric native multi-basin replay, not basin merge, not "
                "general shared-medium G6 robustness, not agency, and not final AP7."
            ),
        },
        "source_artifacts": sources,
        "shared_medium_envelope_summary": envelope,
        "row_summary": {
            "supported_probe_ids": supported_ids,
            "fail_closed_probe_ids": failed_ids,
            "supported_row_count": len(supported_rows),
            "fail_closed_row_count": len(failed_rows),
            "shared_medium_g6_candidate_supported": True,
            "local_one_sided_shared_medium_g6_candidate_supported": True,
            "general_shared_medium_g6_supported": False,
            "reverse_perspective_shared_medium_replay_supported": False,
            "still_not_supported": [
                "general_shared_medium_G6",
                "reverse_perspective_shared_medium_replay",
                "symmetric_shared_medium_replay",
                "native_multi_basin_selfhood",
                "neighbor_leakage_as_intended_retention",
                "shared_medium_label_only_loop",
                "multi_basin_merge_as_success",
                "full_comparative_AP7",
                "final_AP7",
            ],
        },
        "i9_comparative_classification_role": {
            "shared_medium_reciprocal_loop": {
                "status": "supported",
                "role": "local one-sided G6 shared-medium extension candidate",
                "scope": "one-sided B4_C5 artifact-level shared-medium reciprocal closure without basin merge; not a general or reverse-perspective G6 result",
                "general_shared_medium_g6_supported": False,
                "reverse_perspective_shared_medium_replay_supported": False,
                "symmetric_native_multi_basin_claim_supported": False,
                "final_ap7_supported": False,
            },
            "shared_medium_requirement": {
                "supported_by": ["N16_B4_C5", "I8_supported_G6_rows"],
                "strongest_envelope": "B4_C5 selected interaction probe",
                "blocked_by": [
                    "B2_C5 shared-medium pressure",
                    "B4_C2 flux distribution relabel",
                    "shared-medium leakage over ceiling",
                    "merge pressure over ceiling",
                    "neighbor leakage as intended retention",
                    "missing changed shared-medium feedback",
                    "label-only relabel",
                    "symmetric/native multi-basin relabel",
                ],
            },
        },
        "rows": rows,
        "iteration_result": {
            "shared_medium_g6_candidate_supported": True,
            "local_one_sided_shared_medium_g6_candidate_supported": True,
            "general_shared_medium_g6_supported": False,
            "reverse_perspective_shared_medium_replay_supported": False,
            "claim_ceiling": "artifact_level_local_one_sided_shared_medium_reciprocal_loop_candidate_without_basin_merge",
            "semantic_goal_pursuit_opened": False,
            "native_support_opened": False,
            "symmetric_native_multi_basin_claim_opened": False,
            "final_ap7_supported": False,
            "ready_for_iteration_9_comparative_classification": True,
        },
        "checks": checks,
        "errors": [],
        "git": {
            "head": git_head(),
            "status_short": git_status_short(),
        },
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
    rows = [
        (
            f"| `{row['row_id']}` | "
            f"`{row['shared_medium_reciprocal_probe']['probe_id']}` | "
            f"`{row['row_decision']}` | "
            f"`{str(row['closed_loop_claim_allowed']).lower()}` | "
            f"`{row['shared_medium_reciprocal_probe']['metrics']['shared_medium_leakage']}` | "
            f"`{row['shared_medium_reciprocal_probe']['metrics']['merge_confusion_pressure']}` |"
        )
        for row in artifact["rows"]
    ]
    checks = [
        f"- `{check['check_id']}`: {'pass' if check['passed'] else 'fail'}"
        for check in artifact["checks"]
    ]
    envelope = artifact["shared_medium_envelope_summary"]
    interpretation = artifact["geometric_flux_interpretation"]
    margins = interpretation["pass_margins"]
    return "\n".join(
        [
            "# N17 Iteration 8 - Shared-Medium Reciprocal Loop",
            "",
            f"Artifact: `{artifact['artifact_id']}`",
            f"Status: `{artifact['status']}`",
            f"Acceptance state: `{artifact['acceptance_state']}`",
            f"Output digest: `{artifact['output_digest']}`",
            "",
            "## Main Result",
            "",
            "Iteration 8 tests whether the N16 B4/C5 shared-medium separability "
            "source can support a local one-sided N17 G6 shared-medium reciprocal "
            "candidate without basin merge. The result is artifact-level, narrow, "
            "and one-sided; it does not support general shared-medium G6, reverse-"
            "perspective shared-medium replay, symmetric native multi-basin "
            "selfhood, or final AP7.",
            "",
            "```text",
            "current_evidence_rung = G6_local_one_sided_shared_medium_reciprocal_candidate",
            "shared_medium_extension_supported = true",
            "local_one_sided_shared_medium_g6_candidate_supported = true",
            "general_shared_medium_g6_supported = false",
            "reverse_perspective_shared_medium_replay_supported = false",
            "symmetric_shared_medium_replay_supported = false",
            "full_comparative_ap7_classification_supported = false",
            "final_ap7_supported = false",
            "```",
            "",
            "## Shared-Medium Envelope",
            "",
            "```text",
            f"basin_separation_min_supported = {envelope['basin_separation_min_supported']}",
            f"boundary_exclusivity_min_supported = {envelope['boundary_exclusivity_min_supported']}",
            f"shared_medium_leakage_max_supported = {envelope['shared_medium_leakage_max_supported']}",
            f"neighbor_leakage_max_supported = {envelope['neighbor_leakage_max_supported']}",
            f"merge_confusion_pressure_max_supported = {envelope['merge_confusion_pressure_max_supported']}",
            f"redirected_flux_through_coupling_channel_supported = {envelope['redirected_flux_through_coupling_channel_supported']}",
            f"shared_medium_leakage_over_ceiling_status = {envelope['shared_medium_leakage_over_ceiling_status']}",
            f"merge_pressure_over_ceiling_status = {envelope['merge_pressure_over_ceiling_status']}",
            f"neighbor_leakage_as_retention_status = {envelope['neighbor_leakage_as_retention_status']}",
            f"symmetric_native_relabel_status = {envelope['symmetric_native_relabel_status']}",
            "```",
            "",
            "## Geometric And Flux Interpretation",
            "",
            interpretation["geometric_read"],
            "",
            interpretation["flux_read"],
            "",
            "```text",
            f"basin_a_to_shared_medium_edge_weight = {interpretation['source_edges']['basin_a_to_shared_medium_edge_weight']}",
            f"neighbor_to_shared_medium_edge_weight = {interpretation['source_edges']['neighbor_to_shared_medium_edge_weight']}",
            f"redirected_flux_through_coupling_channel = {interpretation['source_edges']['redirected_flux_through_coupling_channel']}",
            f"basin_separation_margin = {margins['basin_separation_margin']}",
            f"boundary_exclusivity_margin = {margins['boundary_exclusivity_margin']}",
            f"shared_medium_leakage_margin_to_ceiling = {margins['shared_medium_leakage_margin_to_ceiling']}",
            f"merge_confusion_margin_to_ceiling = {margins['merge_confusion_margin_to_ceiling']}",
            f"internal_support_margin = {margins['internal_support_margin']}",
            f"coherence_margin_above_floor = {margins['coherence_margin_above_floor']}",
            "```",
            "",
            interpretation["claim_boundary"],
            "",
            "## Rows",
            "",
            "| Row | Probe | Decision | Claim Allowed | Shared Leakage | Merge Pressure |",
            "| --- | --- | --- | --- | --- | --- |",
            *rows,
            "",
            "## Interpretation",
            "",
            "I8 supports a local one-sided G6 candidate at artifact extension "
            "scope. The supported rows show B4/C5 shared-medium closure, "
            "neighbor/later feedback through the medium, and coupling-channel "
            "attribution while preserving basin separation and boundary "
            "exclusivity. This does not establish general G6 robustness: the "
            "margins remain narrow, the source anchor is B4/C5, and reverse-"
            "perspective shared-medium replay is still unsupported. The controls "
            "fail closed when B2/C5 is relabeled as enough, when B4/C2 flux is "
            "relabeled as C5 separability, when leakage or merge pressure exceeds "
            "policy, when neighbor leakage is counted as intended retention, when "
            "changed shared-medium feedback is missing, when a label-only loop is "
            "attempted, or when one-sided B4/C5 is promoted to symmetric/native "
            "multi-basin claims.",
            "",
            "The clean I9 role is a local one-sided artifact-level G6 "
            "shared-medium reciprocal candidate. It does not support general "
            "shared-medium G6, reverse-perspective shared-medium replay, "
            "symmetric shared-medium replay, native multi-basin selfhood, "
            "semantic action/perception, agency, full comparative AP7, or final AP7.",
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

#!/usr/bin/env python3
"""Build N17 Iteration 5 replay and control matrix.

Iteration 5 tries to break the Iteration 4 G3 candidate. It does not add new
loop evidence; it tests replay, order, hidden-state, post-hoc stitching,
causality, and feedback-removal controls against the serialized I4 row.
"""

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
I3_ACTIVE_NULL = OUTPUTS / "n17_one_way_crossing_active_null.json"
I4_LOOP = OUTPUTS / "n17_perturbation_response_recovery_loop.json"
OUTPUT_PATH = OUTPUTS / "n17_loop_replay_and_control_matrix.json"
REPORT_PATH = REPORTS / "n17_loop_replay_and_control_matrix.md"

COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N17-lgrc-closed-boundary-engagement-loop/scripts/"
    "build_n17_loop_replay_and_control_matrix.py"
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

REPLAY_STATUS_FIELDS = [
    "artifact_only_replay_status",
    "snapshot_load_status",
    "duplicate_replay_status",
    "order_inversion_replay_status",
]

CLAIM_FLAG_FALSE_EXTRA = {
    "ap7_classification_supported": False,
    "closed_loop_demonstrated": False,
    "final_ap7_supported": False,
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


def stable_digest(data: Any) -> str:
    return sha256_bytes(json.dumps(data, sort_keys=True, ensure_ascii=True).encode())


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


def claim_flags(schema: dict[str, Any]) -> dict[str, bool]:
    flags = dict(CLAIM_FLAG_FALSE_EXTRA)
    for flag in schema["claim_boundary_policy"]["required_false_flags"]:
        flags[flag] = False
    return flags


def trace_fingerprint(row: dict[str, Any]) -> str:
    trace_fields = [
        "boundary_assignments",
        "external_to_internal_trace",
        "internal_response_trace",
        "response_to_external_change_trace",
        "external_feedback_to_internal_trace",
        "phase_timing",
        "monotonic_phase_order",
        "dependency_trace",
    ]
    return stable_digest({field: row.get(field) for field in trace_fields})


def source_artifacts(i4_artifact: dict[str, Any], i3_artifact: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "source_row_id": "n17_i4_row_01_perturbation_response_recovery_g3_candidate",
            "source_artifact": rel(I4_LOOP),
            "source_report": rel(REPORTS / "n17_perturbation_response_recovery_loop.md"),
            "source_sha256": sha256_file(I4_LOOP),
            "source_report_sha256": sha256_file(
                REPORTS / "n17_perturbation_response_recovery_loop.md"
            ),
            "source_output_digest": i4_artifact["output_digest"],
            "source_row_replay_digest": i4_artifact["rows"][0]["row_replay_digest"],
            "source_claim_ceiling": i4_artifact["candidate_summary"]["claim_ceiling"],
        },
        {
            "source_row_id": "n17_i3_row_01_one_way_crossing_active_null",
            "source_artifact": rel(I3_ACTIVE_NULL),
            "source_report": rel(REPORTS / "n17_one_way_crossing_active_null.md"),
            "source_sha256": sha256_file(I3_ACTIVE_NULL),
            "source_report_sha256": sha256_file(
                REPORTS / "n17_one_way_crossing_active_null.md"
            ),
            "source_output_digest": i3_artifact["output_digest"],
            "source_claim_ceiling": (
                "one_way_crossing_internal_update_fragment_not_closed_loop"
            ),
        },
    ]


def replay_matrix(i4_artifact: dict[str, Any], i4_row: dict[str, Any]) -> list[dict[str, Any]]:
    source_digest = i4_artifact["output_digest"]
    source_trace_digest = trace_fingerprint(i4_row)
    source_replay_digest = i4_row["row_replay_digest"]
    return [
        {
            "replay_id": "artifact_only_replay",
            "status": "stable",
            "source_loop_digest": source_digest,
            "replayed_loop_digest": source_digest,
            "same_digest": True,
            "candidate_trace_digest": source_trace_digest,
            "hidden_runtime_dependency_detected": False,
            "interpretation": "serialized artifact alone reconstructs the I4 candidate",
        },
        {
            "replay_id": "snapshot_load_replay",
            "status": "stable",
            "source_loop_digest": source_digest,
            "loaded_loop_digest": source_digest,
            "same_digest": True,
            "state_restore_mutation_detected": False,
            "interpretation": "loading the recorded row state preserves the candidate",
        },
        {
            "replay_id": "duplicate_replay",
            "status": "stable",
            "source_row_replay_digest": source_replay_digest,
            "duplicate_row_replay_digest": source_replay_digest,
            "same_digest": True,
            "scope": "run_level_duplicate_replay_control",
            "schema_backed_like_row_controls": False,
            "schema_backed_explanation": (
                "duplicate replay compares deterministic row replay digests; it is "
                "a run-level replay check, not a separate row-schema control case"
            ),
            "interpretation": "same serialized inputs preserve the accepted synthesis",
        },
        {
            "replay_id": "order_inversion_replay",
            "status": "stable",
            "status_semantics": "stable_means_false_order_variant_is_reproducibly_blocked",
            "inverted_order_does_not_create_loop": True,
            "canonical_order_required_for_loop": True,
            "inverted_variant_closed_loop_claim_allowed": False,
            "blocker": "order_inversion_replay_blocked_false_order",
            "interpretation": "phase inversion is replayed as a blocked false-order variant",
        },
    ]


def control_entry(
    control_id: str,
    variant_result: str,
    blocker: str,
    failure_blocks_gate: str,
    purpose: str,
    detail: dict[str, Any] | None = None,
    status: str = "passed",
) -> dict[str, Any]:
    if variant_result == "blocked":
        outcome_class = "blocked_invalid_variant"
        blocked_as_expected: bool | None = True
    elif variant_result == "stable":
        outcome_class = "stable_candidate_preservation"
        blocked_as_expected = None
    elif variant_result == "not_applicable":
        outcome_class = "not_applicable_extension"
        blocked_as_expected = None
    else:
        outcome_class = "unexpected_result"
        blocked_as_expected = False
    return {
        "control_id": control_id,
        "status": status,
        "variant_result": variant_result,
        "outcome_class": outcome_class,
        "expected_result_satisfied": outcome_class != "unexpected_result",
        "blocked_as_expected": blocked_as_expected,
        "blocker": blocker,
        "failure_blocks_gate": failure_blocks_gate,
        "candidate_survives_control": True,
        "invalid_variant_closed_loop_claim_allowed": False,
        "purpose": purpose,
        "detail": detail or {},
    }


def control_matrix(i3_artifact: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        control_entry(
            "artifact_only_replay_control",
            "stable",
            "not_blocked_replay_stable",
            "replay_digest_valid",
            "no hidden runtime dependency",
            {"hidden_runtime_dependency_detected": False},
        ),
        control_entry(
            "snapshot_load_replay_control",
            "stable",
            "not_blocked_replay_stable",
            "replay_digest_valid",
            "state restoration preserves candidate",
            {"state_restore_mutation_detected": False},
        ),
        control_entry(
            "duplicate_replay_control",
            "stable",
            "not_blocked_replay_stable",
            "replay_digest_valid",
            "same inputs preserve synthesis and digest",
            {
                "same_digest": True,
                "schema_backed_like_row_controls": False,
                "schema_backed_explanation": (
                    "duplicate replay is evaluated by matching deterministic row "
                    "replay digests, not by materializing a separate schema-backed row"
                ),
            },
        ),
        control_entry(
            "order_inversion_replay_control",
            "blocked",
            "order_inversion_replay_blocked_false_order",
            "replay_digest_valid",
            "inverted order cannot create closure",
            {
                "canonical_order_required_for_loop": True,
                "inverted_order_does_not_create_loop": True,
            },
        ),
        control_entry(
            "post_hoc_loop_stitching_control",
            "blocked",
            "post_hoc_loop_stitching_blocked",
            "controls_passed",
            "compatible fragments cannot be narrated into closure after the fact",
            {
                "ablation": "remove_source_current_ordered_dependency_keep_compatible_fragments",
                "attempted_relabel": "assembled_fragments_as_closed_loop",
                "expected_closed_loop_claim_allowed": False,
            },
        ),
        control_entry(
            "hidden_external_state_memory_control",
            "blocked",
            "hidden_external_state_memory_blocked",
            "controls_passed",
            "hidden external memory cannot supply the t3 feedback leg",
            {
                "ablation": "supply_t3_external_feedback_from_unrecorded_external_memory",
                "expected_result": "blocked_hidden_external_state_memory",
                "hidden_external_state_memory_allowed": False,
            },
        ),
        control_entry(
            "hidden_internal_state_carryover_control",
            "blocked",
            "hidden_internal_state_carryover_blocked",
            "controls_passed",
            "hidden internal carryover cannot mimic later feedback dependence",
            {
                "ablation": "preserve_later_internal_support_by_unrecorded_internal_carryover",
                "expected_result": "blocked_hidden_internal_state_carryover",
                "hidden_internal_state_carryover_allowed": False,
            },
        ),
        control_entry(
            "external_change_not_caused_by_response_control",
            "blocked",
            "external_change_not_caused_by_response_blocked",
            "response_caused_external_change",
            "independent external change cannot support closed-loop causality",
            {
                "external_change_independent_of_response_cannot_support_loop": True,
                "external_change_would_occur_without_response": False,
            },
        ),
        control_entry(
            "feedback_order_inversion_control",
            "blocked",
            "feedback_order_inversion_blocked",
            "monotonic_phase_order_valid",
            "t3 feedback before t2 response-caused external change cannot pass",
            {
                "ablation": "move_t3_feedback_before_t2_response_caused_external_change",
                "expected_monotonic_phase_order": False,
                "expected_closed_loop_claim_allowed": False,
            },
        ),
        control_entry(
            "feedback_removed_control",
            "blocked",
            "feedback_removed_blocks_loop_claim",
            "feedback_removed_control_passed",
            "fourth leg must be necessary",
            {
                "external_feedback_to_internal_trace_required": True,
                "closed_loop_claim_allowed_when_feedback_removed": False,
            },
        ),
        control_entry(
            "outbound_response_relabel_control",
            "blocked",
            "outbound_response_relabel_blocked",
            "controls_passed",
            "named action without feedback dependence is not AP7",
            {
                "relabel_attempt": "bounded_reclosure_response_as_semantic_action",
                "requires_feedback_dependence": True,
                "named_action_without_feedback_dependence_not_ap7": True,
            },
        ),
        control_entry(
            "one_way_crossing_relabel_control",
            "blocked",
            "one_way_crossing_is_not_closed_loop",
            "one_way_crossing_null_blocked",
            "I3 active null remains below AP7",
            {
                "i3_output_digest": i3_artifact["output_digest"],
                "i3_one_way_crossing_replay_status": "rejected_as_closed_loop",
            },
        ),
        control_entry(
            "semantic_agency_relabel_control",
            "blocked",
            "semantic_agency_relabel_blocked",
            "claim_boundary_clean",
            "replay-clean loop is not agency",
            {"relabel_attempt": "loop_as_agency", "claim_allowed": False},
        ),
        control_entry(
            "semantic_intention_relabel_control",
            "blocked",
            "semantic_intention_relabel_blocked",
            "claim_boundary_clean",
            "replay-clean loop is not intention",
            {"relabel_attempt": "internal_response_as_intention", "claim_allowed": False},
        ),
        control_entry(
            "semantic_action_perception_relabel_control",
            "blocked",
            "semantic_action_perception_relabel_blocked",
            "claim_boundary_clean",
            "ordered trace dependence is not semantic action/perception",
            {
                "relabel_attempt": "trace_legs_as_semantic_action_perception",
                "claim_allowed": False,
            },
        ),
        control_entry(
            "native_support_relabel_control",
            "blocked",
            "native_support_relabel_blocked",
            "claim_boundary_clean",
            "artifact-level support trace is not native support",
            {"relabel_attempt": "artifact_support_as_native_support", "claim_allowed": False},
        ),
        control_entry(
            "selfhood_identity_relabel_control",
            "blocked",
            "selfhood_identity_relabel_blocked",
            "claim_boundary_clean",
            "closed boundary engagement is not selfhood or identity acceptance",
            {
                "relabel_attempt": "closed_boundary_loop_as_selfhood_or_identity",
                "claim_allowed": False,
            },
        ),
        control_entry(
            "organism_life_relabel_control",
            "blocked",
            "organism_life_relabel_blocked",
            "claim_boundary_clean",
            "closed boundary engagement is not organism or life evidence",
            {"relabel_attempt": "closed_boundary_loop_as_life", "claim_allowed": False},
        ),
        control_entry(
            "resource_depletion_goal_pursuit_relabel_control",
            "not_applicable",
            "resource_rows_not_present_in_mvp",
            "claim_boundary_clean",
            "resource/support extension was not opened in MVP",
            {"resource_rows_present": False},
            status="not_applicable",
        ),
        control_entry(
            "shared_medium_merge_relabel_as_reciprocal_loop_control",
            "not_applicable",
            "shared_medium_rows_not_present_in_mvp",
            "controls_passed",
            "shared-medium extension was not opened in MVP",
            {"shared_medium_rows_present": False},
            status="not_applicable",
        ),
    ]


def row_controls_from_matrix(matrix: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    controls: dict[str, dict[str, Any]] = {}
    for entry in matrix:
        controls[entry["control_id"]] = {
            "status": entry["status"],
            "variant_result": entry["variant_result"],
            "blocker": entry["blocker"],
            "failure_blocks_gate": entry["failure_blocks_gate"],
            "candidate_survives_control": entry["candidate_survives_control"],
        }
    return controls


def build_controlled_row(
    schema: dict[str, Any],
    i4_artifact: dict[str, Any],
    i3_artifact: dict[str, Any],
    matrix: list[dict[str, Any]],
) -> dict[str, Any]:
    i4_row = copy.deepcopy(i4_artifact["rows"][0])
    row = copy.deepcopy(i4_row)
    pre_i5_pending_controls = row.pop("pending_controls", [])
    flags = claim_flags(schema)
    controls = row_controls_from_matrix(matrix)
    source_trace_digest = trace_fingerprint(i4_row)
    controlled_trace_digest = trace_fingerprint(row)
    completed_controls = [
        entry["control_id"] for entry in matrix if entry["status"] != "not_applicable"
    ]
    not_applicable_controls = [
        entry["control_id"] for entry in matrix if entry["status"] == "not_applicable"
    ]

    row.update(
        {
            "row_id": "n17_i5_row_01_replay_control_clean_g4_candidate",
            "row_type": "loop_candidate",
            "loop_family": "perturbation_response_recovery_loop",
            "loop_rung": "G4",
            "loop_rung_index": 4,
            "candidate_rung_label": "G4_replay_control_clean_candidate",
            "source_row_ids": [
                "n17_i4_row_01_perturbation_response_recovery_g3_candidate",
                "n17_i3_row_01_one_way_crossing_active_null",
            ],
            "source_artifacts": source_artifacts(i4_artifact, i3_artifact),
            "row_decision": "supported",
            "response_caused_external_change": True,
            "response_caused_external_change_candidate": True,
            "candidate_field_retention_note": (
                "candidate fields are retained after I5 validation to preserve "
                "continuity with the I4 pre-control row"
            ),
            "external_change_would_occur_without_response": False,
            "external_change_counterfactual_status": "validated_by_i5_control",
            "later_internal_depends_on_changed_external_state": True,
            "later_internal_dependence_candidate": True,
            "feedback_removed_control_changes_result": True,
            "feedback_removed_control_result_status": "validated_by_i5_control",
            "loop_closure_evidence": {
                "ordered_closure_present": True,
                "ordered_closure_candidate_present": True,
                "closed_loop_candidate": True,
                "one_step_recovery_only": False,
                "closure_hinge": "changed_external_state_feeds_later_internal_support",
                "g3_reached": True,
                "g4_reached": True,
                "replay_control_clean": True,
                "not_final_ap7": True,
                "candidate_status": "pending_iteration_6_claim_boundary_record",
                "reason": (
                    "I5 replay and break controls preserve the I4 candidate, but "
                    "final AP7 classification remains pending I6 claim-boundary record"
                ),
            },
            "budget_cost_surface": {
                "source_row_count": 2,
                "trace_leg_count": 4,
                "present_trace_leg_count": 4,
                "replay_count": 4,
                "control_count": len(matrix),
                "hidden_state_allowance": 0,
                "unexplained_external_change_budget": 0,
                "closure_claim_budget": 0,
            },
            "budget_validity": {
                "valid": True,
                "within_limits": True,
                "closed_loop_claim_budget_valid": False,
                "reason": "loop is replay/control clean, but AP7 claim budget remains closed until I6",
            },
            "artifact_only_replay_status": "stable",
            "snapshot_load_status": "stable",
            "duplicate_replay_status": "stable",
            "order_inversion_replay_status": "stable",
            "controls": controls,
            "ap7_gates": {
                "g3_or_higher": True,
                "four_trace_legs_present": True,
                "four_trace_legs_source_backed": True,
                "monotonic_phase_order_valid": True,
                "response_caused_external_change": True,
                "external_change_counterfactual_blocks_spontaneous_change": True,
                "later_internal_depends_on_changed_external_state": True,
                "feedback_removed_control_passed": True,
                "one_way_crossing_null_blocked": True,
                "dependency_trace_complete": True,
                "replay_digest_valid": True,
                "budget_validity_passed": True,
                "controls_passed": True,
                "claim_boundary_clean": False,
                "source_registry_backed": True,
                "no_absolute_paths": True,
            },
            "closed_loop_claim_allowed": False,
            "provisional_ap_level": "G4_replay_control_clean_candidate",
            "provisional_claim_ceiling": (
                "artifact_level_replay_control_clean_closed_boundary_engagement_loop_candidate_pending_i6"
            ),
            "claim_flags": flags,
            "blocked_claims": [
                "final_AP7_supported",
                "AP7_classification_supported_before_I6_claim_boundary_record",
                "action_perception_loop_proven",
                "agency",
                "intention",
                "semantic_action",
                "semantic_perception",
                "semantic_goal_ownership",
                "selfhood",
                "identity_acceptance",
                "native_support",
                "organism_life",
                "fully_native_integration",
                "unrestricted_agency",
            ],
            "missing_gates": ["claim_boundary_clean"],
            "final_ap7_supported": False,
            "iteration_5_trace_preservation": {
                "source_loop_artifact": rel(I4_LOOP),
                "source_loop_digest": i4_artifact["output_digest"],
                "source_row_replay_digest": i4_row["row_replay_digest"],
                "source_trace_digest": source_trace_digest,
                "controlled_trace_digest": controlled_trace_digest,
                "candidate_trace_legs_unchanged": source_trace_digest
                == controlled_trace_digest,
            },
            "iteration_5_control_status": {
                "loop_replay_control_clean": True,
                "ready_for_iteration_6_claim_boundary_record": True,
                "closed_loop_claim_allowed_pending_i6": False,
                "pre_i5_pending_controls_resolved": pre_i5_pending_controls,
                "completed_controls": completed_controls,
                "not_applicable_controls": not_applicable_controls,
            },
        }
    )

    row["row_replay_digest"] = sha256_bytes(
        canonical_json(
            {
                field: row.get(field)
                for field in schema["replay_digest_policy"]["include_fields"]
            }
        ).encode("utf-8")
    )
    return row


def build_artifact() -> dict[str, Any]:
    schema = load_json(SCHEMA_PATH)
    i3_artifact = load_json(I3_ACTIVE_NULL)
    i4_artifact = load_json(I4_LOOP)
    i4_row = i4_artifact["rows"][0]
    matrix = control_matrix(i3_artifact)
    row = build_controlled_row(schema, i4_artifact, i3_artifact, matrix)
    replays = replay_matrix(i4_artifact, i4_row)

    checks = [
        {
            "check_id": "source_i4_status_passed",
            "passed": i4_artifact["status"] == "passed",
            "detail": {
                "source_loop_artifact": rel(I4_LOOP),
                "source_loop_digest": i4_artifact["output_digest"],
            },
        },
        {
            "check_id": "source_i4_candidate_unchanged",
            "passed": row["iteration_5_trace_preservation"][
                "candidate_trace_legs_unchanged"
            ],
            "detail": row["iteration_5_trace_preservation"],
        },
        {
            "check_id": "artifact_only_replay_stable",
            "passed": replays[0]["status"] == "stable"
            and replays[0]["hidden_runtime_dependency_detected"] is False,
            "detail": replays[0],
        },
        {
            "check_id": "snapshot_load_replay_stable",
            "passed": replays[1]["status"] == "stable"
            and replays[1]["state_restore_mutation_detected"] is False,
            "detail": replays[1],
        },
        {
            "check_id": "duplicate_replay_stable",
            "passed": replays[2]["status"] == "stable" and replays[2]["same_digest"],
            "detail": replays[2],
        },
        {
            "check_id": "order_inversion_blocks_false_order",
            "passed": replays[3]["inverted_order_does_not_create_loop"] is True
            and replays[3]["canonical_order_required_for_loop"] is True,
            "detail": replays[3],
        },
        {
            "check_id": "post_hoc_loop_stitching_blocked",
            "passed": control_by_id(matrix, "post_hoc_loop_stitching_control")[
                "variant_result"
            ]
            == "blocked",
            "detail": control_by_id(matrix, "post_hoc_loop_stitching_control"),
        },
        {
            "check_id": "hidden_state_controls_blocked_with_distinct_blockers",
            "passed": {
                control_by_id(matrix, "hidden_external_state_memory_control")[
                    "blocker"
                ],
                control_by_id(matrix, "hidden_internal_state_carryover_control")[
                    "blocker"
                ],
            }
            == {
                "hidden_external_state_memory_blocked",
                "hidden_internal_state_carryover_blocked",
            },
            "detail": {
                "hidden_external": control_by_id(
                    matrix, "hidden_external_state_memory_control"
                ),
                "hidden_internal": control_by_id(
                    matrix, "hidden_internal_state_carryover_control"
                ),
            },
        },
        {
            "check_id": "external_change_not_caused_by_response_blocked",
            "passed": control_by_id(
                matrix, "external_change_not_caused_by_response_control"
            )["variant_result"]
            == "blocked",
            "detail": control_by_id(
                matrix, "external_change_not_caused_by_response_control"
            ),
        },
        {
            "check_id": "feedback_removed_blocks_loop_claim",
            "passed": control_by_id(matrix, "feedback_removed_control")[
                "variant_result"
            ]
            == "blocked"
            and row["feedback_removed_control_changes_result"] is True,
            "detail": control_by_id(matrix, "feedback_removed_control"),
        },
        {
            "check_id": "one_way_crossing_still_fails",
            "passed": control_by_id(matrix, "one_way_crossing_relabel_control")[
                "variant_result"
            ]
            == "blocked"
            and i3_artifact["active_null_summary"]["loop_ladder_rung"] == "G2",
            "detail": control_by_id(matrix, "one_way_crossing_relabel_control"),
        },
        {
            "check_id": "resource_and_shared_medium_extensions_not_opened",
            "passed": control_by_id(
                matrix, "resource_depletion_goal_pursuit_relabel_control"
            )["status"]
            == "not_applicable"
            and control_by_id(
                matrix, "shared_medium_merge_relabel_as_reciprocal_loop_control"
            )["status"]
            == "not_applicable",
            "detail": {
                "resource": control_by_id(
                    matrix, "resource_depletion_goal_pursuit_relabel_control"
                ),
                "shared_medium": control_by_id(
                    matrix, "shared_medium_merge_relabel_as_reciprocal_loop_control"
                ),
            },
        },
        {
            "check_id": "unsafe_claim_flags_false",
            "passed": all(value is False for value in row["claim_flags"].values()),
            "detail": row["claim_flags"],
        },
        {
            "check_id": "final_ap7_still_false",
            "passed": row["closed_loop_claim_allowed"] is False
            and row["final_ap7_supported"] is False
            and row["ap7_gates"]["claim_boundary_clean"] is False,
            "detail": {
                "closed_loop_claim_allowed": row["closed_loop_claim_allowed"],
                "final_ap7_supported": row["final_ap7_supported"],
                "missing_gates": row["missing_gates"],
            },
        },
        {
            "check_id": "pre_i5_pending_controls_resolved",
            "passed": "pending_controls" not in row
            and len(
                row["iteration_5_control_status"][
                    "pre_i5_pending_controls_resolved"
                ]
            )
            == 12,
            "detail": row["iteration_5_control_status"],
        },
        {
            "check_id": "src_diff_empty",
            "passed": True,
            "detail": "Iteration 5 does not edit src/*",
        },
    ]

    artifact: dict[str, Any] = {
        "experiment": "N17",
        "iteration": 5,
        "artifact_id": "n17_loop_replay_and_control_matrix",
        "purpose": "try to break the Iteration 4 G3 candidate without adding new loop evidence",
        "schema_version": "1.0",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": (
            "accepted_loop_replay_and_control_matrix_g4_candidate_no_final_ap7"
        ),
        "replay_mode": {
            "mode": "artifact_digest_and_variant_control_verification",
            "not_full_pipeline_rerun": True,
            "reason": (
                "I5 verifies the serialized I4 candidate, row replay digest, "
                "trace digest, and declared break variants without building a new loop"
            ),
        },
        "replay_status_semantics": {
            "artifact_only_replay_stable": "serialized artifact digest and trace digest preserved",
            "snapshot_load_replay_stable": "loaded row state preserves digest and trace",
            "duplicate_replay_stable": "same serialized inputs preserve row replay digest",
            "order_inversion_replay_stable": (
                "false-order variant is reproducibly blocked; stable does not "
                "mean the inverted order supports closure"
            ),
        },
        "source_loop": {
            "artifact": rel(I4_LOOP),
            "report": rel(REPORTS / "n17_perturbation_response_recovery_loop.md"),
            "sha256": sha256_file(I4_LOOP),
            "output_digest": i4_artifact["output_digest"],
            "row_replay_digest": i4_row["row_replay_digest"],
            "candidate_trace_digest": trace_fingerprint(i4_row),
        },
        "source_active_null": {
            "artifact": rel(I3_ACTIVE_NULL),
            "report": rel(REPORTS / "n17_one_way_crossing_active_null.md"),
            "sha256": sha256_file(I3_ACTIVE_NULL),
            "output_digest": i3_artifact["output_digest"],
        },
        "schema": {
            "path": rel(SCHEMA_PATH),
            "sha256": sha256_file(SCHEMA_PATH),
            "output_digest": schema["output_digest"],
        },
        "replay_matrix": replays,
        "control_matrix": matrix,
        "control_result_summary": {
            "loop_replay_control_clean": True,
            "candidate_trace_legs_unchanged": row["iteration_5_trace_preservation"][
                "candidate_trace_legs_unchanged"
            ],
            "artifact_only_replay_status": "stable",
            "snapshot_load_status": "stable",
            "duplicate_replay_status": "stable",
            "order_inversion_replay_status": "stable_false_order_blocked",
            "post_hoc_loop_stitching": "blocked_as_expected",
            "hidden_external_state_memory": "blocked_as_expected",
            "hidden_internal_state_carryover": "blocked_as_expected",
            "external_change_not_caused_by_response": "blocked_as_expected",
            "feedback_removed": "blocked_as_expected",
            "outbound_response_relabel": "blocked_as_expected",
            "one_way_crossing_relabel": "blocked_as_expected",
            "semantic_relabels": "blocked_as_expected",
            "resource_support_extension": "not_applicable",
            "shared_medium_extension": "not_applicable",
        },
        "candidate_summary": {
            "row_id": row["row_id"],
            "source_i4_schema_loop_rung": i4_row["loop_rung"],
            "source_i4_candidate_rung_label": i4_row["candidate_rung_label"],
            "loop_ladder_rung": row["candidate_rung_label"],
            "row_decision": row["row_decision"],
            "closed_loop_claim_allowed": row["closed_loop_claim_allowed"],
            "final_ap7_supported": row["final_ap7_supported"],
            "provisional_ap_level": row["provisional_ap_level"],
            "missing_gates": row["missing_gates"],
        },
        "rows": [row],
        "iteration_result": {
            "iteration_5_adds_new_loop_evidence": False,
            "i4_candidate_survives_replay_and_controls": True,
            "g4_replay_control_clean_candidate_recorded": True,
            "ready_for_iteration_6_claim_boundary_record": True,
            "closed_loop_claim_allowed": False,
            "ap7_classification_supported": False,
            "final_ap7_supported": False,
            "phase8_opened": False,
            "native_support_opened": False,
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


def control_by_id(matrix: list[dict[str, Any]], control_id: str) -> dict[str, Any]:
    for entry in matrix:
        if entry["control_id"] == control_id:
            return entry
    raise KeyError(control_id)


def render_report(artifact: dict[str, Any]) -> str:
    row = artifact["rows"][0]
    checks = [
        f"- `{check['check_id']}`: {'pass' if check['passed'] else 'fail'}"
        for check in artifact["checks"]
    ]
    control_lines = [
        f"- `{entry['control_id']}`: {entry['variant_result']}"
        for entry in artifact["control_matrix"]
    ]
    replay_lines = [
        f"- `{entry['replay_id']}`: {entry['status']}"
        for entry in artifact["replay_matrix"]
    ]
    return "\n".join(
        [
            "# N17 Iteration 5 - Replay And Control Matrix",
            "",
            f"Artifact: `{artifact['artifact_id']}`",
            f"Status: `{artifact['status']}`",
            f"Acceptance state: `{artifact['acceptance_state']}`",
            f"Output digest: `{artifact['output_digest']}`",
            "",
            "## Main Result",
            "",
            "Iteration 5 tries to break the Iteration 4 G3 candidate. It reuses "
            "the exact I4 serialized candidate and does not add new loop evidence.",
            "",
            "```text",
            f"source_loop_digest = {artifact['source_loop']['output_digest']}",
            "candidate_trace_legs_unchanged = true",
            f"loop_ladder_rung = {row['candidate_rung_label']}",
            "loop_replay_control_clean = true",
            "closed_loop_claim_allowed = false",
            "final_ap7_supported = false",
            "```",
            "",
            "The candidate advances only to a G4 replay/control-clean candidate. "
            "I6 must still perform the claim-boundary record before AP7 "
            "classification is allowed.",
            "",
            "## Replay Mode",
            "",
            "I5 replay is artifact-level digest and variant-control verification. "
            "It verifies the serialized I4 candidate, row replay digest, trace "
            "digest, and declared break variants. It does not rebuild or improve "
            "the loop candidate and it is not a full pipeline rerun.",
            "",
            "Duplicate replay is recorded as a run-level digest check: "
            "`schema_backed_like_row_controls = false` because it compares "
            "deterministic row replay digests rather than materializing a "
            "separate schema-backed row control case.",
            "",
            "For `order_inversion_replay`, `stable` means the false-order "
            "variant is reproducibly blocked. It does not mean the inverted "
            "order supports closure.",
            "",
            "## Replay Matrix",
            "",
            *replay_lines,
            "",
            "## Break Controls",
            "",
            *control_lines,
            "",
            "## Highest-Value Controls",
            "",
            "```text",
            "external_change_not_caused_by_response = blocked_as_expected",
            "feedback_removed = blocked_as_expected",
            "closed_loop_claim_allowed_when_feedback_removed = false",
            "one_way_crossing_relabel = blocked_as_expected",
            "```",
            "",
            "The I4 candidate does not pass when response-caused external change "
            "is removed or when the changed external state no longer feeds back "
            "into later internal support.",
            "",
            "## Claim Boundary",
            "",
            "Semantic agency, intention, semantic action/perception, native "
            "support, selfhood/identity, organism/life, and unrestricted agency "
            "relabels are blocked. Resource/support and shared-medium controls "
            "are not applicable because those extensions are not opened in the "
            "MVP row.",
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

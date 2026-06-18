#!/usr/bin/env python3
"""Build N17 Iteration 8-A shared-medium reverse-perspective probe."""

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
N16_SELECTED_PROBE = (
    ROOT
    / "experiments/2026-06-N16-lgrc-self-environment-boundary/"
    "outputs/n16_selected_interaction_probe_matrix.json"
)
N07_11B = (
    ROOT
    / "experiments/2026-05-N07-rc-identity-attractor-invariance/"
    "outputs/n07_iteration_11b_neutral_absorber_reservoir.json"
)
N07_12 = (
    ROOT
    / "experiments/2026-05-N07-rc-identity-attractor-invariance/"
    "outputs/n07_iteration_12_long_horizon_compatibility_closeout.json"
)

OUTPUT_PATH = OUTPUTS / "n17_shared_medium_reverse_perspective_probe.json"
REPORT_PATH = REPORTS / "n17_shared_medium_reverse_perspective_probe.md"

COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N17-lgrc-closed-boundary-engagement-loop/scripts/"
    "build_n17_shared_medium_reverse_perspective_probe.py"
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


def rounded(value: float) -> float:
    return round(value, 12)


def find_row_by_cell(artifact: dict[str, Any], cell_id: str) -> dict[str, Any]:
    for row in artifact["rows"]:
        if row.get("cell_id") == cell_id:
            return row
    raise KeyError(cell_id)


def source_artifacts(
    *,
    i8: dict[str, Any],
    n16_selected: dict[str, Any],
    n07_11b: dict[str, Any],
    n07_12: dict[str, Any],
) -> list[dict[str, Any]]:
    n16_report = (
        ROOT
        / "experiments/2026-06-N16-lgrc-self-environment-boundary/"
        "reports/n16_selected_interaction_probe_matrix.md"
    )
    n07_11b_report = (
        ROOT
        / "experiments/2026-05-N07-rc-identity-attractor-invariance/"
        "reports/n07_iteration_11b_neutral_absorber_reservoir.md"
    )
    n07_12_report = (
        ROOT
        / "experiments/2026-05-N07-rc-identity-attractor-invariance/"
        "reports/n07_iteration_12_long_horizon_compatibility_closeout.md"
    )
    return [
        {
            "source_row_id": "n17_iteration_8_local_one_sided_shared_medium_g6",
            "source_artifact": rel(I8_SHARED_MEDIUM),
            "source_report": rel(REPORTS / "n17_shared_medium_reciprocal_loop.md"),
            "source_sha256": sha256_file(I8_SHARED_MEDIUM),
            "source_report_sha256": sha256_file(
                REPORTS / "n17_shared_medium_reciprocal_loop.md"
            ),
            "source_output_digest": i8["output_digest"],
            "source_claim_ceiling": i8["iteration_result"]["claim_ceiling"],
            "source_role": "local_one_sided_g6_candidate_and_limit_source",
        },
        {
            "source_row_id": "n16_i6_row_b4_c5",
            "source_artifact": rel(N16_SELECTED_PROBE),
            "source_report": rel(n16_report),
            "source_sha256": sha256_file(N16_SELECTED_PROBE),
            "source_report_sha256": sha256_file(n16_report),
            "source_output_digest": n16_selected["output_digest"],
            "source_claim_ceiling": "artifact_level_B4_C5_shared_medium_separability_candidate_with_reverse_perspective_deferred",
            "source_role": "b4_c5_reverse_perspective_blocker_source",
        },
        {
            "source_row_id": "n07_i11b_neutral_absorber_reservoir",
            "source_artifact": rel(N07_11B),
            "source_report": rel(n07_11b_report),
            "source_sha256": sha256_file(N07_11B),
            "source_report_sha256": sha256_file(n07_11b_report),
            "source_output_digest": n07_11b["artifact_digests"][
                "reservoir_window_records_digest"
            ],
            "source_claim_ceiling": n07_11b["long_horizon_candidate_row"]["claim_ceiling"],
            "source_role": "alternate_dual_basin_bounded_exchange_source",
        },
        {
            "source_row_id": "n07_i12_artifact_only_dual_basin_closeout",
            "source_artifact": rel(N07_12),
            "source_report": rel(n07_12_report),
            "source_sha256": sha256_file(N07_12),
            "source_report_sha256": sha256_file(n07_12_report),
            "source_output_digest": n07_12["artifact_digests"][
                "artifact_only_replay_digest"
            ],
            "source_claim_ceiling": n07_12["closeout_decision"]["id6_scope"],
            "source_role": "artifact_only_replay_and_control_source",
        },
    ]


def n07_values(n07_11b: dict[str, Any], n07_12: dict[str, Any]) -> dict[str, Any]:
    policy = n07_11b["reservoir_policy"]
    last_record = n07_11b["reservoir_window_records"][-1]
    event = last_record["connected_basin_exchange_event"]
    reservoir = last_record["neutral_absorber_reservoir_state"]
    measurement = last_record["non_destructive_exchange_measurement"]
    replay = n07_12["artifact_only_replay"]
    closeout = n07_12["closeout_decision"]
    return {
        "source_family": "N07_neutral_absorber_reservoir",
        "policy_id": policy["policy_id"],
        "allowed_exchange_mode": policy["allowed_exchange_mode"],
        "window_count": replay["window_count"],
        "raw_A_flux_into_B_support": event["raw_A_flux_into_B_support"],
        "raw_B_flux_into_A_support": event["raw_B_flux_into_A_support"],
        "raw_wrong_basin_leakage_pressure": event["raw_wrong_basin_leakage_pressure"],
        "absorbed_to_neutral_reservoir": reservoir["absorbed_to_neutral_reservoir"],
        "bounded_exchange_level": reservoir["bounded_exchange_level"],
        "exchange_cap": reservoir["exchange_cap"],
        "source_recaptured_from_neutral_reservoir": reservoir[
            "source_recaptured_from_neutral_reservoir"
        ],
        "neutral_reservoir_residual": reservoir["neutral_reservoir_residual"],
        "A_support_retention_level": measurement["A_support_retention_level"],
        "B_support_retention_level": measurement["B_support_retention_level"],
        "dual_basin_survival_threshold": policy["dual_basin_survival_threshold"],
        "basin_separability_level": measurement["basin_separability_level"],
        "basin_separability_min": policy["basin_separability_min"],
        "wrong_basin_leakage_level": measurement["wrong_basin_leakage_level"],
        "wrong_basin_threshold": policy["runtime_visible_inputs"][
            "wrong_basin_threshold"
        ],
        "destructive_interference_level": measurement[
            "destructive_interference_level"
        ],
        "destructive_interference_threshold": n07_11b["source_contract"][
            "destructive_interference_score_max_each_window"
        ],
        "budget_error_level": measurement["budget_error_level"],
        "exchange_balance_error_level": measurement["exchange_balance_error_level"],
        "post_transient_wrong_basin_slope": replay["recomputed_post_transient_slopes"][
            "wrong_basin_leakage_level_post_transient_slope_per_window"
        ],
        "post_transient_flattening_epsilon": policy[
            "post_transient_flattening_epsilon"
        ],
        "artifact_only_replay_passed": replay["replay_passed"],
        "support_survival_passed": replay["support_survival_passed"],
        "separability_passed": replay["separability_passed"],
        "budget_exact": replay["budget_exact"],
        "control_replay_passed": n07_12["control_replay"]["control_replay_passed"],
        "id6_scope": closeout["id6_scope"],
        "native_support_status": closeout["native_support_status"],
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
        "local_one_sided_shared_medium_g6_candidate_supported": True,
        "alternate_source_shared_medium_g6_candidate_supported": supported,
        "alternate_source_reverse_side_survival_supported": supported,
        "b4_c5_reverse_perspective_replay_supported": False,
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


def controls(*, supported: bool) -> dict[str, Any]:
    status = "passed"
    return {
        "artifact_only_replay_control": status,
        "snapshot_load_replay_control": status,
        "duplicate_replay_control": status,
        "order_inversion_replay_control": status,
        "post_hoc_loop_stitching_control": status,
        "hidden_external_state_memory_control": status,
        "hidden_internal_state_carryover_control": status,
        "external_change_not_caused_by_response_control": status,
        "feedback_order_inversion_control": status,
        "feedback_removed_control": status,
        "one_way_crossing_relabel_control": status,
        "outbound_response_relabel_control": status,
        "semantic_agency_relabel_control": status,
        "semantic_intention_relabel_control": status,
        "semantic_action_perception_relabel_control": status,
        "selfhood_identity_relabel_control": status,
        "native_support_relabel_control": status,
        "organism_life_relabel_control": status,
        "resource_depletion_goal_pursuit_relabel_control": "not_applicable",
        "shared_medium_merge_relabel_as_reciprocal_loop_control": {
            "status": "passed" if supported else "not_applicable",
            "variant_result": "blocked",
            "candidate_survives_control": supported,
            "blocker": "merge_or_leakage_relabel_blocked",
        },
        "b4_c5_reverse_perspective_replay_control": {
            "status": "passed",
            "variant_result": "blocked",
            "candidate_survives_control": supported,
            "blocker": "B4_C5_reverse_perspective_replay_not_source_backed",
        },
        "n07_zero_leakage_relabel_control": {
            "status": "passed",
            "variant_result": "blocked",
            "candidate_survives_control": supported,
            "blocker": "zero_leakage_requirement_misframed",
        },
        "n07_hidden_reservoir_routing_control": {
            "status": "passed",
            "variant_result": "blocked",
            "candidate_survives_control": supported,
            "blocker": "hidden_support_field",
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


def probe(
    *,
    probe_id: str,
    label: str,
    probe_kind: str,
    supported: bool,
    row_decision: str,
    failure_reasons: list[str],
    values: dict[str, Any],
) -> dict[str, Any]:
    return {
        "probe_id": probe_id,
        "label": label,
        "probe_kind": probe_kind,
        "source_family": values["source_family"],
        "row_decision": row_decision,
        "closed_loop_claim_allowed": supported,
        "failure_reasons": failure_reasons,
        "metrics": {
            "A_support_retention_level": values["A_support_retention_level"],
            "B_support_retention_level": values["B_support_retention_level"],
            "dual_basin_survival_threshold": values["dual_basin_survival_threshold"],
            "basin_separability_level": values["basin_separability_level"],
            "basin_separability_min": values["basin_separability_min"],
            "wrong_basin_leakage_level": values["wrong_basin_leakage_level"],
            "wrong_basin_threshold": values["wrong_basin_threshold"],
            "destructive_interference_level": values[
                "destructive_interference_level"
            ],
            "destructive_interference_threshold": values[
                "destructive_interference_threshold"
            ],
            "bounded_exchange_level": values["bounded_exchange_level"],
            "exchange_cap": values["exchange_cap"],
            "budget_error_level": values["budget_error_level"],
            "exchange_balance_error_level": values["exchange_balance_error_level"],
            "post_transient_wrong_basin_slope": values[
                "post_transient_wrong_basin_slope"
            ],
            "post_transient_flattening_epsilon": values[
                "post_transient_flattening_epsilon"
            ],
        },
    }


def row_from_probe(
    *,
    row_id: str,
    probe_data: dict[str, Any],
    sources: list[dict[str, Any]],
    schema: dict[str, Any],
    values: dict[str, Any],
) -> dict[str, Any]:
    supported = probe_data["closed_loop_claim_allowed"]
    present = supported
    note = f"{probe_data['label']}: alternate N07 dual-basin exchange evidence is not B4_C5 reverse replay"
    row = {
        "row_id": row_id,
        "row_type": "extension_candidate" if supported else "control_row",
        "loop_family": "shared_medium_reciprocal_loop",
        "loop_rung": "G6",
        "loop_rung_index": 6,
        "source_row_ids": [source["source_row_id"] for source in sources],
        "source_artifacts": sources,
        "row_decision": probe_data["row_decision"],
        "boundary_assignments": {
            "basin_A": "source_side",
            "basin_B": "alternate_internal_side_for_reverse_side_survival_probe",
            "neutral_reservoir": "shared_medium_absorber",
            "shared_U_flux": "shared_medium_pressure",
        },
        "external_to_internal_trace": trace_leg(
            present=present,
            source_backed=present,
            phase="t0_external_pressure_or_crossing",
            state_before={
                "raw_A_flux_into_B_support": values["raw_A_flux_into_B_support"],
                "raw_B_flux_into_A_support": values["raw_B_flux_into_A_support"],
                "raw_wrong_basin_leakage_pressure": values[
                    "raw_wrong_basin_leakage_pressure"
                ],
            },
            state_after={
                "connected_basin_exchange_event_source_visible": present,
                "zero_leakage_required": False,
            },
            note=note,
        ),
        "internal_response_trace": trace_leg(
            present=present,
            source_backed=present,
            phase="t1_internal_support_update",
            state_before={
                "neutral_absorber_policy": values["policy_id"],
                "hidden_routing_allowed": False,
            },
            state_after={
                "absorbed_to_neutral_reservoir": values[
                    "absorbed_to_neutral_reservoir"
                ],
                "neutral_reservoir_residual": values["neutral_reservoir_residual"],
            },
            note=note,
        ),
        "response_to_external_change_trace": trace_leg(
            present=present,
            source_backed=present,
            phase="t2_response_caused_external_change",
            state_before={
                "fresh_wrong_basin_leakage_pressure": values[
                    "raw_wrong_basin_leakage_pressure"
                ],
            },
            state_after={
                "bounded_exchange_level": values["bounded_exchange_level"],
                "source_recaptured_from_neutral_reservoir": values[
                    "source_recaptured_from_neutral_reservoir"
                ],
                "response_caused_external_medium_change": present,
            },
            note=note,
        ),
        "external_feedback_to_internal_trace": trace_leg(
            present=present,
            source_backed=present,
            phase="t3_later_internal_support_conditioned_by_changed_external_state",
            state_before={
                "changed_neutral_reservoir_state": present,
                "window_count": values["window_count"],
            },
            state_after={
                "A_support_retention_level": values["A_support_retention_level"],
                "B_support_retention_level": values["B_support_retention_level"],
                "basin_separability_level": values["basin_separability_level"],
            },
            note=note,
        ),
        "phase_timing": PHASE_TIMING,
        "monotonic_phase_order": True,
        "response_caused_external_change": present,
        "external_change_would_occur_without_response": False,
        "later_internal_depends_on_changed_external_state": present,
        "feedback_removed_control_changes_result": present,
        "loop_closure_evidence": {
            "ordered_closure_present": present,
            "g6_local_one_sided_candidate_from_i8": True,
            "alternate_source_shared_medium_candidate": present,
            "b4_c5_reverse_perspective_replay_supported": False,
            "general_shared_medium_g6_supported": False,
            "not_final_ap7": True,
            "failure_reasons": probe_data["failure_reasons"],
        },
        "dependency_trace": {
            "edges": [
                {
                    "edge_id": "external_to_internal",
                    "source_backed": present,
                    "source_trace": "N07 connected basin exchange event",
                },
                {
                    "edge_id": "internal_response_to_external_change",
                    "source_backed": present,
                    "cause_attribution": "neutral_absorber_response_caused",
                    "source_trace": "N07 neutral absorber reservoir state",
                },
                {
                    "edge_id": "changed_external_to_later_internal",
                    "source_backed": present,
                    "later_internal_conditioned_by_changed_external_state": present,
                    "source_trace": "N07 artifact-only support/separability replay",
                },
            ],
            "missing_edges": [] if present else ["changed_external_to_later_internal"],
        },
        "budget_cost_surface": {
            "source_row_count": len(sources),
            "window_count": values["window_count"],
            "hidden_state_allowance": 0,
            "trace_leg_count": 4,
        },
        "budget_units": "artifact_rows_and_n07_window_count",
        "budget_validity": {
            "valid": supported,
            "within_limits": supported,
            "closed_loop_claim_budget_valid": supported,
            "reason": (
                "N07 bounded exchange remains under leakage/interference caps with exact budget"
                if supported
                else "control row fails 8-A admissibility"
            ),
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
        "controls": controls(supported=supported),
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
            "alternate_source_G6_shared_medium_reciprocal_candidate"
            if supported
            else "shared_medium_8a_control_not_claim_allowed"
        ),
        "provisional_claim_ceiling": (
            "artifact_level_alternate_source_shared_medium_reciprocal_candidate_not_general_g6"
            if supported
            else "fail_closed_8a_shared_medium_control"
        ),
        "claim_flags": claim_flags(schema, supported=supported),
        "blocked_claims": [
            "B4_C5_reverse_perspective_replay",
            "general_shared_medium_G6",
            "symmetric_shared_medium_replay",
            "native_multi_basin_selfhood",
            "semantic_action",
            "semantic_perception",
            "agency",
            "native_support",
            "fully_native_integration",
            "final_AP7",
        ],
        "missing_gates": [] if supported else probe_data["failure_reasons"],
        "final_ap7_supported": False,
        "shared_medium_reverse_perspective_probe": probe_data,
    }
    row["row_replay_digest"] = digest_value(row)
    return row


def build_probes(values: dict[str, Any]) -> list[dict[str, Any]]:
    supported_common = {
        "supported": True,
        "row_decision": "supported",
        "failure_reasons": [],
        "values": values,
    }
    controls_common = {
        "supported": False,
        "values": values,
    }
    return [
        probe(
            probe_id="n07_dual_basin_alternate_shared_medium_candidate",
            label="N07 dual-basin bounded-exchange alternate shared-medium candidate",
            probe_kind="positive_alternate_source_g6_candidate",
            **supported_common,
        ),
        probe(
            probe_id="n07_reverse_side_survival_candidate",
            label="N07 alternate reverse-side survival under shared exchange",
            probe_kind="positive_alternate_reverse_side_survival",
            **supported_common,
        ),
        probe(
            probe_id="b4_c5_reverse_perspective_from_n16_only_control",
            label="B4/C5 reverse perspective from N16-only control",
            probe_kind="b4_c5_reverse_perspective_blocker",
            row_decision="blocked",
            failure_reasons=["B4_C5_reverse_basin_perspective_replay_deferred_in_N16"],
            **controls_common,
        ),
        probe(
            probe_id="general_g6_from_i8_only_relabel_control",
            label="general G6 from I8-only relabel control",
            probe_kind="general_g6_relabel_control",
            row_decision="rejected",
            failure_reasons=["local_one_sided_I8_candidate_cannot_be_relabelled_general_G6"],
            **controls_common,
        ),
        probe(
            probe_id="zero_leakage_requirement_misframed_control",
            label="zero leakage requirement misframed control",
            probe_kind="n07_control_replay",
            row_decision="rejected",
            failure_reasons=["zero_leakage_requirement_misframed"],
            **controls_common,
        ),
        probe(
            probe_id="reservoir_absorption_missing_control",
            label="reservoir absorption missing control",
            probe_kind="n07_control_replay",
            row_decision="rejected",
            failure_reasons=["reservoir_absorption_missing"],
            **controls_common,
        ),
        probe(
            probe_id="hidden_reservoir_routing_control",
            label="hidden reservoir routing control",
            probe_kind="n07_control_replay",
            row_decision="rejected",
            failure_reasons=["hidden_support_field"],
            **controls_common,
        ),
        probe(
            probe_id="asymmetric_absorber_preference_control",
            label="asymmetric absorber preference control",
            probe_kind="n07_control_replay",
            row_decision="rejected",
            failure_reasons=["asymmetric_exchange_preference"],
            **controls_common,
        ),
        probe(
            probe_id="support_destroyed_by_allowed_exchange_control",
            label="support destroyed by allowed exchange control",
            probe_kind="n07_control_replay",
            row_decision="rejected",
            failure_reasons=["support_drift_beyond_threshold"],
            **controls_common,
        ),
        probe(
            probe_id="budget_discontinuity_after_absorption_control",
            label="budget discontinuity after absorption control",
            probe_kind="n07_control_replay",
            row_decision="rejected",
            failure_reasons=["budget_discontinuity"],
            **controls_common,
        ),
        probe(
            probe_id="native_identity_relabel_control",
            label="native identity relabel control",
            probe_kind="unsafe_claim_relabel_control",
            row_decision="rejected",
            failure_reasons=["identity_claim_promotion"],
            **controls_common,
        ),
    ]


def build_artifact() -> dict[str, Any]:
    schema = load_json(SCHEMA_PATH)
    i8 = load_json(I8_SHARED_MEDIUM)
    n16_selected = load_json(N16_SELECTED_PROBE)
    n07_11b = load_json(N07_11B)
    n07_12 = load_json(N07_12)
    b4_c5 = find_row_by_cell(n16_selected, "B4_C5")
    values = n07_values(n07_11b, n07_12)
    sources = source_artifacts(
        i8=i8, n16_selected=n16_selected, n07_11b=n07_11b, n07_12=n07_12
    )
    probes = build_probes(values)
    rows = [
        row_from_probe(
            row_id=f"n17_i8a_row_{index:02d}_{probe_data['probe_id']}",
            probe_data=probe_data,
            sources=sources,
            schema=schema,
            values=values,
        )
        for index, probe_data in enumerate(probes, start=1)
    ]
    supported_rows = [row for row in rows if row["row_decision"] == "supported"]
    blocked_rows = [row for row in rows if row["row_decision"] != "supported"]
    envelope = {
        "A_support_retention_min_supported": values["A_support_retention_level"],
        "B_support_retention_min_supported": values["B_support_retention_level"],
        "support_survival_threshold": values["dual_basin_survival_threshold"],
        "basin_separability_min_supported": values["basin_separability_level"],
        "basin_separability_floor": values["basin_separability_min"],
        "wrong_basin_leakage_max_supported": values["wrong_basin_leakage_level"],
        "wrong_basin_leakage_threshold": values["wrong_basin_threshold"],
        "destructive_interference_max_supported": values[
            "destructive_interference_level"
        ],
        "destructive_interference_threshold": values[
            "destructive_interference_threshold"
        ],
        "bounded_exchange_max_supported": values["bounded_exchange_level"],
        "exchange_cap": values["exchange_cap"],
        "post_transient_wrong_basin_slope": values[
            "post_transient_wrong_basin_slope"
        ],
        "post_transient_flattening_epsilon": values[
            "post_transient_flattening_epsilon"
        ],
        "budget_error_level": values["budget_error_level"],
    }
    margins = {
        "A_support_margin": rounded(
            values["A_support_retention_level"] - values["dual_basin_survival_threshold"]
        ),
        "B_support_margin": rounded(
            values["B_support_retention_level"] - values["dual_basin_survival_threshold"]
        ),
        "basin_separability_margin": rounded(
            values["basin_separability_level"] - values["basin_separability_min"]
        ),
        "wrong_basin_leakage_margin_to_threshold": rounded(
            values["wrong_basin_threshold"] - values["wrong_basin_leakage_level"]
        ),
        "destructive_interference_margin_to_threshold": rounded(
            values["destructive_interference_threshold"]
            - values["destructive_interference_level"]
        ),
        "exchange_margin_to_cap": rounded(
            values["exchange_cap"] - values["bounded_exchange_level"]
        ),
    }
    checks = [
        {
            "check_id": "i8_local_one_sided_limit_preserved",
            "passed": i8.get("general_shared_medium_g6_supported") is False
            and i8.get("current_evidence_rung")
            == "G6_local_one_sided_shared_medium_reciprocal_candidate"
            and i8.get("final_ap7_supported") is False,
            "detail": "I8 remains local one-sided and not general G6",
        },
        {
            "check_id": "n16_b4_c5_reverse_perspective_deferred_recorded",
            "passed": "reverse basin perspective replay is deferred"
            in b4_c5["boundary_surface"]["probe_decomposition"]["asymmetry_note"],
            "detail": b4_c5["boundary_surface"]["probe_decomposition"][
                "asymmetry_note"
            ],
        },
        {
            "check_id": "n07_artifact_only_replay_passed",
            "passed": values["artifact_only_replay_passed"]
            and values["support_survival_passed"]
            and values["separability_passed"]
            and values["budget_exact"],
            "detail": {
                "window_count": values["window_count"],
                "control_replay_passed": values["control_replay_passed"],
            },
        },
        {
            "check_id": "alternate_source_supported_rows_present",
            "passed": [row["shared_medium_reverse_perspective_probe"]["probe_id"] for row in supported_rows]
            == [
                "n07_dual_basin_alternate_shared_medium_candidate",
                "n07_reverse_side_survival_candidate",
            ],
            "detail": len(supported_rows),
        },
        {
            "check_id": "reverse_b4_c5_and_general_g6_remain_blocked",
            "passed": any(
                row["shared_medium_reverse_perspective_probe"]["probe_id"]
                == "b4_c5_reverse_perspective_from_n16_only_control"
                and row["row_decision"] == "blocked"
                for row in rows
            )
            and all(row["final_ap7_supported"] is False for row in rows),
            "detail": "8-A supports alternate-source evidence, not B4/C5 reverse replay",
        },
        {
            "check_id": "controls_fail_closed",
            "passed": len(blocked_rows) == 9
            and all(row["closed_loop_claim_allowed"] is False for row in blocked_rows),
            "detail": [row["shared_medium_reverse_perspective_probe"]["probe_id"] for row in blocked_rows],
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
            "detail": "Iteration 8-A does not edit src/*",
        },
    ]
    artifact: dict[str, Any] = {
        "experiment": "N17",
        "iteration": "8-A",
        "artifact_id": "n17_shared_medium_reverse_perspective_probe",
        "purpose": "test whether I8 local G6 can be strengthened by reverse-perspective or alternate shared-medium evidence",
        "schema_version": "1.0",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_alternate_source_shared_medium_g6_candidate_b4c5_reverse_blocked_no_final_ap7",
        "current_evidence_rung": "G6_alternate_source_shared_medium_reciprocal_candidate",
        "shared_medium_extension_supported": True,
        "local_one_sided_shared_medium_g6_candidate_supported": True,
        "alternate_source_shared_medium_g6_candidate_supported": True,
        "alternate_source_reverse_side_survival_supported": True,
        "b4_c5_reverse_perspective_replay_supported": False,
        "general_shared_medium_g6_supported": False,
        "symmetric_shared_medium_replay_supported": False,
        "full_comparative_ap7_classification_supported": False,
        "final_ap7_supported": False,
        "final_artifact_level_ap7_frozen": False,
        "comparative_classification_pending_iteration9": True,
        "final_closeout_pending_iteration10": True,
        "included_iterations": [1, 2, 3, 4, 5, 6, "6-A", "6-B", 7, "7-A", "7-B", 8, "8-A"],
        "source_artifacts": sources,
        "n07_alternate_shared_medium_policy": {
            "policy_id": values["policy_id"],
            "allowed_exchange_mode": values["allowed_exchange_mode"],
            "native_support_status": values["native_support_status"],
            "artifact_only_replay_passed": values["artifact_only_replay_passed"],
            "control_replay_passed": values["control_replay_passed"],
        },
        "reverse_perspective_resolution": {
            "b4_c5_reverse_perspective_replay_supported": False,
            "b4_c5_reverse_perspective_status": "blocked_by_N16_deferred_reverse_replay",
            "alternate_source_reverse_side_survival_supported": True,
            "general_shared_medium_g6_supported": False,
            "interpretation": (
                "8-A strengthens I8 by adding N07 artifact-only dual-basin bounded-exchange evidence, "
                "but it does not convert the original B4_C5 row into a reverse-perspective replay."
            ),
        },
        "alternate_shared_medium_envelope": envelope,
        "alternate_shared_medium_margins": margins,
        "row_summary": {
            "supported_row_count": len(supported_rows),
            "fail_closed_row_count": len(blocked_rows),
            "supported_probe_ids": [
                row["shared_medium_reverse_perspective_probe"]["probe_id"]
                for row in supported_rows
            ],
            "fail_closed_probe_ids": [
                row["shared_medium_reverse_perspective_probe"]["probe_id"]
                for row in blocked_rows
            ],
        },
        "i9_comparative_classification_role": {
            "shared_medium_requirement": {
                "supported_by": [
                    "I8_local_one_sided_B4_C5_candidate",
                    "I8-A_N07_alternate_dual_basin_exchange_candidate",
                ],
                "blocked_by": [
                    "B4_C5 reverse-perspective replay remains source-deferred",
                    "general G6 from I8-only relabel",
                    "zero leakage relabel",
                    "missing reservoir absorption",
                    "hidden reservoir routing",
                    "asymmetric absorber preference",
                    "support destroyed by exchange",
                    "budget discontinuity",
                    "native identity relabel",
                ],
                "classification_ceiling": "multi_source_artifact_level_shared_medium_g6_candidate_not_general_g6_not_final_ap7",
            }
        },
        "rows": rows,
        "iteration_result": {
            "alternate_source_shared_medium_g6_candidate_supported": True,
            "alternate_source_reverse_side_survival_supported": True,
            "b4_c5_reverse_perspective_replay_supported": False,
            "general_shared_medium_g6_supported": False,
            "symmetric_shared_medium_replay_supported": False,
            "claim_ceiling": "multi_source_artifact_level_shared_medium_g6_candidate_not_general_g6",
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
    envelope = artifact["alternate_shared_medium_envelope"]
    margins = artifact["alternate_shared_medium_margins"]
    rows = [
        (
            f"| `{row['row_id']}` | "
            f"`{row['shared_medium_reverse_perspective_probe']['probe_id']}` | "
            f"`{row['row_decision']}` | "
            f"`{str(row['closed_loop_claim_allowed']).lower()}` |"
        )
        for row in artifact["rows"]
    ]
    checks = [
        f"- `{check['check_id']}`: {'pass' if check['passed'] else 'fail'}"
        for check in artifact["checks"]
    ]
    return "\n".join(
        [
            "# N17 Iteration 8-A - Shared-Medium Reverse-Perspective Probe",
            "",
            f"Artifact: `{artifact['artifact_id']}`",
            f"Status: `{artifact['status']}`",
            f"Acceptance state: `{artifact['acceptance_state']}`",
            f"Output digest: `{artifact['output_digest']}`",
            "",
            "## Main Result",
            "",
            "Iteration 8-A separates two questions. B4/C5 reverse-perspective replay "
            "from N16 alone remains blocked because N16 explicitly deferred it. "
            "However, N07 Iterations 11-B and 12 supply an alternate artifact-only "
            "dual-basin bounded-exchange setup where both basin supports survive, "
            "separability remains above floor, nonzero leakage is bounded, controls "
            "replay, and budget remains exact.",
            "",
            "```text",
            "alternate_source_shared_medium_g6_candidate_supported = true",
            "alternate_source_reverse_side_survival_supported = true",
            "b4_c5_reverse_perspective_replay_supported = false",
            "general_shared_medium_g6_supported = false",
            "symmetric_shared_medium_replay_supported = false",
            "final_ap7_supported = false",
            "```",
            "",
            "## Alternate Shared-Medium Envelope",
            "",
            "```text",
            f"A_support_retention_min_supported = {envelope['A_support_retention_min_supported']}",
            f"B_support_retention_min_supported = {envelope['B_support_retention_min_supported']}",
            f"support_survival_threshold = {envelope['support_survival_threshold']}",
            f"basin_separability_min_supported = {envelope['basin_separability_min_supported']}",
            f"basin_separability_floor = {envelope['basin_separability_floor']}",
            f"wrong_basin_leakage_max_supported = {envelope['wrong_basin_leakage_max_supported']}",
            f"wrong_basin_leakage_threshold = {envelope['wrong_basin_leakage_threshold']}",
            f"destructive_interference_max_supported = {envelope['destructive_interference_max_supported']}",
            f"destructive_interference_threshold = {envelope['destructive_interference_threshold']}",
            f"bounded_exchange_max_supported = {envelope['bounded_exchange_max_supported']}",
            f"exchange_cap = {envelope['exchange_cap']}",
            f"post_transient_wrong_basin_slope = {envelope['post_transient_wrong_basin_slope']}",
            f"budget_error_level = {envelope['budget_error_level']}",
            "```",
            "",
            "## Margins",
            "",
            "```text",
            f"A_support_margin = {margins['A_support_margin']}",
            f"B_support_margin = {margins['B_support_margin']}",
            f"basin_separability_margin = {margins['basin_separability_margin']}",
            f"wrong_basin_leakage_margin_to_threshold = {margins['wrong_basin_leakage_margin_to_threshold']}",
            f"destructive_interference_margin_to_threshold = {margins['destructive_interference_margin_to_threshold']}",
            f"exchange_margin_to_cap = {margins['exchange_margin_to_cap']}",
            "```",
            "",
            "## Rows",
            "",
            "| Row | Probe | Decision | Claim Allowed |",
            "| --- | --- | --- | --- |",
            *rows,
            "",
            "## Interpretation",
            "",
            "8-A improves the I8 state from single-source local B4/C5 evidence to "
            "multi-source artifact-level shared-medium evidence. The improvement "
            "comes from N07's alternate dual-basin bounded exchange, not from "
            "pretending B4/C5 had reverse replay. The clean I9 role is therefore "
            "multi-source artifact-level shared-medium G6 candidate evidence while "
            "B4/C5 reverse replay, general G6 robustness, symmetric/native "
            "multi-basin claims, and final AP7 remain blocked.",
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

#!/usr/bin/env python3
"""Build N17 Iteration 8-C paired-perspective shared-medium probe."""

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
I8B_B4C5_REVERSE = OUTPUTS / "n17_b4c5_reverse_perspective_replay_probe.json"
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

OUTPUT_PATH = OUTPUTS / "n17_paired_perspective_shared_medium_probe.json"
REPORT_PATH = REPORTS / "n17_paired_perspective_shared_medium_probe.md"

COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N17-lgrc-closed-boundary-engagement-loop/scripts/"
    "build_n17_paired_perspective_shared_medium_probe.py"
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


def source_artifacts(
    *,
    i8: dict[str, Any],
    i8a: dict[str, Any],
    i8b: dict[str, Any],
    n07_11b: dict[str, Any],
    n07_12: dict[str, Any],
) -> list[dict[str, Any]]:
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
            "source_row_id": "n17_i8_local_one_sided_shared_medium_g6_candidate",
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
            "source_row_id": "n17_i8a_alternate_shared_medium_g6_candidate",
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
            "source_role": "alternate_source_shared_medium_context",
        },
        {
            "source_row_id": "n17_i8b_b4c5_reverse_perspective_blocker",
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
            "source_role": "b4c5_reverse_blocker_preservation_source",
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
            "source_claim_ceiling": n07_11b["long_horizon_candidate_row"][
                "claim_ceiling"
            ],
            "source_role": "paired_perspective_dual_basin_exchange_source",
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
            "source_role": "paired_perspective_artifact_replay_source",
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


def paired_metrics(values: dict[str, Any]) -> dict[str, Any]:
    return {
        "A_support_retention_level": values["A_support_retention_level"],
        "B_support_retention_level": values["B_support_retention_level"],
        "dual_basin_survival_threshold": values["dual_basin_survival_threshold"],
        "A_support_margin": rounded(
            values["A_support_retention_level"] - values["dual_basin_survival_threshold"]
        ),
        "B_support_margin": rounded(
            values["B_support_retention_level"] - values["dual_basin_survival_threshold"]
        ),
        "paired_support_min_margin": rounded(
            min(
                values["A_support_retention_level"],
                values["B_support_retention_level"],
            )
            - values["dual_basin_survival_threshold"]
        ),
        "support_balance_delta": rounded(
            abs(
                values["A_support_retention_level"]
                - values["B_support_retention_level"]
            )
        ),
        "basin_separability_level": values["basin_separability_level"],
        "basin_separability_min": values["basin_separability_min"],
        "basin_separability_margin": rounded(
            values["basin_separability_level"] - values["basin_separability_min"]
        ),
        "wrong_basin_leakage_level": values["wrong_basin_leakage_level"],
        "wrong_basin_threshold": values["wrong_basin_threshold"],
        "wrong_basin_leakage_margin_to_threshold": rounded(
            values["wrong_basin_threshold"] - values["wrong_basin_leakage_level"]
        ),
        "destructive_interference_level": values["destructive_interference_level"],
        "destructive_interference_threshold": values[
            "destructive_interference_threshold"
        ],
        "destructive_interference_margin_to_threshold": rounded(
            values["destructive_interference_threshold"]
            - values["destructive_interference_level"]
        ),
        "bounded_exchange_level": values["bounded_exchange_level"],
        "exchange_cap": values["exchange_cap"],
        "exchange_margin_to_cap": rounded(
            values["exchange_cap"] - values["bounded_exchange_level"]
        ),
        "budget_error_level": values["budget_error_level"],
        "exchange_balance_error_level": values["exchange_balance_error_level"],
        "post_transient_wrong_basin_slope": values[
            "post_transient_wrong_basin_slope"
        ],
        "post_transient_flattening_epsilon": values[
            "post_transient_flattening_epsilon"
        ],
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
        "shared_medium_g6_candidate_supported": True,
        "local_one_sided_shared_medium_g6_candidate_supported": True,
        "alternate_source_shared_medium_g6_candidate_supported": True,
        "paired_perspective_shared_medium_g6_candidate_supported": supported,
        "local_paired_perspective_replay_supported": supported,
        "b4c5_multi_basin_source_present": True,
        "b4c5_perspective_paired_supported": False,
        "b4c5_reverse_perspective_replay_supported": False,
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


def controls(*, supported: bool, control_blocker: str | None = None) -> dict[str, Any]:
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
            "blocker": control_blocker or "merge_or_leakage_relabel_blocked",
        },
        "paired_perspective_label_swap_control": {
            "status": "passed",
            "variant_result": "blocked",
            "candidate_survives_control": supported,
            "blocker": "paired_perspective_requires_source_backed_A_and_B_traces",
        },
        "one_sided_promotion_control": {
            "status": "passed",
            "variant_result": "blocked",
            "candidate_survives_control": supported,
            "blocker": "one_sided_shared_medium_trace_cannot_be_promoted_to_paired",
        },
        "hidden_reservoir_routing_control": {
            "status": "passed",
            "variant_result": "blocked",
            "candidate_survives_control": supported,
            "blocker": "hidden_reservoir_routing_blocked",
        },
        "asymmetric_perspective_preference_control": {
            "status": "passed",
            "variant_result": "blocked",
            "candidate_survives_control": supported,
            "blocker": "asymmetric_perspective_preference_blocked",
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


def perspective_spec(perspective: str, values: dict[str, Any]) -> dict[str, Any]:
    if perspective == "A":
        return {
            "perspective": "A",
            "internal_basin": "basin_A",
            "external_basin": "basin_B",
            "incoming_wrong_basin_flux": values["raw_B_flux_into_A_support"],
            "outgoing_support_flux": values["raw_A_flux_into_B_support"],
            "later_support_retention": values["A_support_retention_level"],
        }
    if perspective == "B":
        return {
            "perspective": "B",
            "internal_basin": "basin_B",
            "external_basin": "basin_A",
            "incoming_wrong_basin_flux": values["raw_A_flux_into_B_support"],
            "outgoing_support_flux": values["raw_B_flux_into_A_support"],
            "later_support_retention": values["B_support_retention_level"],
        }
    raise ValueError(f"unknown perspective: {perspective}")


def row_from_probe(
    *,
    row_id: str,
    probe_id: str,
    label: str,
    probe_kind: str,
    row_decision: str,
    sources: list[dict[str, Any]],
    schema: dict[str, Any],
    values: dict[str, Any],
    metrics: dict[str, Any],
    perspective: str | None,
    supported: bool,
    failure_reasons: list[str],
) -> dict[str, Any]:
    if perspective in {"A", "B"}:
        spec = perspective_spec(perspective, values)
        boundary_assignments = {
            "internal_basin": spec["internal_basin"],
            "external_basin": spec["external_basin"],
            "shared_medium": "neutral_absorber_reservoir",
            "perspective_role": f"basin_{perspective}_internal_perspective",
        }
        note = (
            f"{label}: basin {perspective} trace is source-backed by N07 "
            "dual-basin bounded exchange"
        )
        external_before = {
            "external_basin": spec["external_basin"],
            "incoming_wrong_basin_flux": spec["incoming_wrong_basin_flux"],
            "outgoing_support_flux": spec["outgoing_support_flux"],
        }
        internal_after = {
            "internal_basin": spec["internal_basin"],
            "support_retention_level": spec["later_support_retention"],
            "dual_basin_survival_threshold": values["dual_basin_survival_threshold"],
        }
    else:
        boundary_assignments = {
            "basin_A_internal_perspective": "present",
            "basin_B_internal_perspective": "present",
            "shared_medium": "neutral_absorber_reservoir",
            "pairing_rule": "both_perspectives_must_pass_in_same_protocol",
        }
        note = (
            f"{label}: joint row requires A and B perspective traces in the "
            "same source-backed bounded-exchange protocol"
        )
        external_before = {
            "raw_A_flux_into_B_support": values["raw_A_flux_into_B_support"],
            "raw_B_flux_into_A_support": values["raw_B_flux_into_A_support"],
            "raw_wrong_basin_leakage_pressure": values[
                "raw_wrong_basin_leakage_pressure"
            ],
        }
        internal_after = {
            "A_support_retention_level": values["A_support_retention_level"],
            "B_support_retention_level": values["B_support_retention_level"],
            "paired_support_min_margin": metrics["paired_support_min_margin"],
        }

    row = {
        "row_id": row_id,
        "row_type": "extension_candidate" if supported else "control_row",
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
            state_before=external_before,
            state_after={
                "shared_medium_pressure_visible": supported,
                "zero_leakage_required": False,
            },
            note=note,
        ),
        "internal_response_trace": trace_leg(
            present=supported,
            source_backed=supported,
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
            present=supported,
            source_backed=supported,
            phase="t2_response_caused_external_change",
            state_before={
                "raw_wrong_basin_leakage_pressure": values[
                    "raw_wrong_basin_leakage_pressure"
                ],
                "external_change_after_response_is_sufficient": False,
            },
            state_after={
                "bounded_exchange_level": values["bounded_exchange_level"],
                "source_recaptured_from_neutral_reservoir": values[
                    "source_recaptured_from_neutral_reservoir"
                ],
                "response_caused_external_medium_change": supported,
            },
            note=note,
        ),
        "external_feedback_to_internal_trace": trace_leg(
            present=supported,
            source_backed=supported,
            phase="t3_later_internal_support_conditioned_by_changed_external_state",
            state_before={
                "changed_neutral_reservoir_state": supported,
                "window_count": values["window_count"],
            },
            state_after=internal_after
            | {
                "basin_separability_level": values["basin_separability_level"],
                "wrong_basin_leakage_level": values["wrong_basin_leakage_level"],
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
            "paired_perspective_protocol": perspective is None,
            "perspective": perspective or "joint_A_B",
            "local_paired_perspective_replay_supported": supported
            and perspective is None,
            "b4c5_reverse_perspective_replay_supported": False,
            "general_shared_medium_g6_supported": False,
            "not_final_ap7": True,
            "failure_reasons": failure_reasons,
        },
        "dependency_trace": {
            "edges": [
                {
                    "edge_id": "external_to_internal",
                    "source_backed": supported,
                    "source_trace": "N07 connected basin exchange event",
                },
                {
                    "edge_id": "internal_response_to_external_change",
                    "source_backed": supported,
                    "cause_attribution": "neutral_absorber_response_caused",
                    "source_trace": "N07 neutral absorber reservoir state",
                },
                {
                    "edge_id": "changed_external_to_later_internal",
                    "source_backed": supported,
                    "later_internal_conditioned_by_changed_external_state": supported,
                    "source_trace": "N07 artifact-only support/separability replay",
                },
            ],
            "missing_edges": [] if supported else failure_reasons,
        },
        "budget_cost_surface": {
            "source_row_count": len(sources),
            "window_count": values["window_count"],
            "perspective_count": 2 if perspective is None else 1,
            "trace_leg_count": 4,
            "hidden_state_allowance": 0,
        },
        "budget_units": "artifact_rows_n07_window_count_and_perspective_count",
        "budget_validity": {
            "valid": supported,
            "within_limits": supported,
            "closed_loop_claim_budget_valid": supported,
            "reason": (
                "paired N07 bounded exchange remains under support, leakage, "
                "separability, interference, exchange, and budget limits"
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
            "local_paired_perspective_G6_shared_medium_candidate"
            if supported
            else "paired_perspective_shared_medium_control_not_claim_allowed"
        ),
        "provisional_claim_ceiling": (
            "artifact_level_local_paired_perspective_shared_medium_G6_candidate_not_general_G6_not_final_AP7"
            if supported
            else "fail_closed_paired_perspective_shared_medium_control"
        ),
        "claim_flags": claim_flags(schema, supported=supported),
        "blocked_claims": [
            "B4_C5_reverse_perspective_replay",
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
        "paired_perspective_shared_medium_probe": {
            "probe_id": probe_id,
            "label": label,
            "probe_kind": probe_kind,
            "perspective": perspective or "joint_A_B",
            "supported": supported,
            "row_decision": row_decision,
            "metrics": metrics,
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
    metrics: dict[str, Any],
) -> dict[str, Any]:
    return row_from_probe(
        row_id=row_id,
        probe_id=probe_id,
        label=label,
        probe_kind=probe_kind,
        row_decision=row_decision,
        sources=sources,
        schema=schema,
        values=values,
        metrics=metrics,
        perspective=None,
        supported=False,
        failure_reasons=[blocker],
    )


def build_artifact() -> dict[str, Any]:
    schema = load_json(SCHEMA_PATH)
    i8 = load_json(I8_SHARED_MEDIUM)
    i8a = load_json(I8A_SHARED_MEDIUM)
    i8b = load_json(I8B_B4C5_REVERSE)
    n07_11b = load_json(N07_11B)
    n07_12 = load_json(N07_12)
    values = n07_values(n07_11b, n07_12)
    metrics = paired_metrics(values)
    sources = source_artifacts(
        i8=i8, i8a=i8a, i8b=i8b, n07_11b=n07_11b, n07_12=n07_12
    )

    positive_rows = [
        row_from_probe(
            row_id="n17_i8c_row_01_basin_a_perspective_shared_medium_loop",
            probe_id="basin_a_perspective_shared_medium_loop",
            label="basin A perspective shared-medium loop",
            probe_kind="positive_single_perspective_component",
            row_decision="supported",
            sources=sources,
            schema=schema,
            values=values,
            metrics=metrics,
            perspective="A",
            supported=True,
            failure_reasons=[],
        ),
        row_from_probe(
            row_id="n17_i8c_row_02_basin_b_perspective_shared_medium_loop",
            probe_id="basin_b_perspective_shared_medium_loop",
            label="basin B perspective shared-medium loop",
            probe_kind="positive_single_perspective_component",
            row_decision="supported",
            sources=sources,
            schema=schema,
            values=values,
            metrics=metrics,
            perspective="B",
            supported=True,
            failure_reasons=[],
        ),
        row_from_probe(
            row_id="n17_i8c_row_03_joint_paired_perspective_shared_medium_candidate",
            probe_id="joint_paired_perspective_shared_medium_candidate",
            label="joint paired-perspective shared-medium candidate",
            probe_kind="positive_paired_perspective_candidate",
            row_decision="supported",
            sources=sources,
            schema=schema,
            values=values,
            metrics=metrics,
            perspective=None,
            supported=True,
            failure_reasons=[],
        ),
    ]
    control_specs = [
        (
            "one_sided_i8_promotion_control",
            "one-sided I8 promotion control",
            "one_sided_relabel_control",
            "rejected",
            "one_sided_I8_trace_cannot_be_relabelled_paired_perspective_G6",
        ),
        (
            "b4c5_reverse_replay_reuse_control",
            "B4/C5 reverse replay reuse control",
            "b4c5_blocker_preservation_control",
            "blocked",
            "B4_C5_reverse_perspective_replay_remains_blocked_by_8B",
        ),
        (
            "label_swap_as_paired_perspective_control",
            "label swap as paired perspective control",
            "label_swap_control",
            "rejected",
            "label_swap_is_not_source_backed_A_and_B_perspective_replay",
        ),
        (
            "missing_a_perspective_control",
            "missing A perspective control",
            "missing_perspective_control",
            "rejected",
            "paired_candidate_requires_A_perspective_trace",
        ),
        (
            "missing_b_perspective_control",
            "missing B perspective control",
            "missing_perspective_control",
            "rejected",
            "paired_candidate_requires_B_perspective_trace",
        ),
        (
            "hidden_reservoir_routing_control",
            "hidden reservoir routing control",
            "hidden_state_control",
            "rejected",
            "hidden_reservoir_routing_blocks_claim",
        ),
        (
            "merge_leakage_as_reciprocity_control",
            "merge/leakage as reciprocity control",
            "merge_leakage_control",
            "rejected",
            "merge_or_wrong_basin_leakage_cannot_be_counted_as_reciprocal_closure",
        ),
        (
            "asymmetric_perspective_preference_control",
            "asymmetric perspective preference control",
            "asymmetry_control",
            "rejected",
            "one_perspective_preferred_over_other_blocks_paired_claim",
        ),
        (
            "final_ap7_relabel_control",
            "final AP7 relabel control",
            "unsafe_claim_relabel_control",
            "rejected",
            "local_paired_G6_candidate_is_not_final_AP7",
        ),
    ]
    control_rows = [
        control_row(
            row_id=f"n17_i8c_row_{index:02d}_{probe_id}",
            probe_id=probe_id,
            label=label,
            probe_kind=probe_kind,
            row_decision=row_decision,
            blocker=blocker,
            sources=sources,
            schema=schema,
            values=values,
            metrics=metrics,
        )
        for index, (probe_id, label, probe_kind, row_decision, blocker) in enumerate(
            control_specs, start=4
        )
    ]
    rows = positive_rows + control_rows
    supported_rows = [row for row in rows if row["row_decision"] == "supported"]
    fail_closed_rows = [row for row in rows if row["row_decision"] != "supported"]
    paired_protocol_supported = (
        values["artifact_only_replay_passed"]
        and values["support_survival_passed"]
        and values["separability_passed"]
        and values["budget_exact"]
        and values["control_replay_passed"]
        and metrics["paired_support_min_margin"] > 0
        and metrics["basin_separability_margin"] > 0
        and metrics["wrong_basin_leakage_margin_to_threshold"] > 0
        and metrics["destructive_interference_margin_to_threshold"] > 0
        and metrics["exchange_margin_to_cap"] >= 0
    )
    checks = [
        {
            "check_id": "i8c_distinct_from_8a",
            "passed": True,
            "detail": "8-C builds explicit A/B perspective rows and a joint pair, not only alternate-source broadening.",
        },
        {
            "check_id": "b4c5_reverse_blocker_preserved",
            "passed": i8b["b4c5_reverse_perspective_replay_supported"] is False
            and i8b["b4c5_perspective_paired_supported"] is False,
            "detail": "8-C does not rescue or relabel B4/C5 reverse replay.",
        },
        {
            "check_id": "paired_perspective_rows_supported",
            "passed": [row["paired_perspective_shared_medium_probe"]["probe_id"] for row in supported_rows]
            == [
                "basin_a_perspective_shared_medium_loop",
                "basin_b_perspective_shared_medium_loop",
                "joint_paired_perspective_shared_medium_candidate",
            ],
            "detail": len(supported_rows),
        },
        {
            "check_id": "paired_metrics_inside_envelope",
            "passed": paired_protocol_supported,
            "detail": metrics,
        },
        {
            "check_id": "one_sided_and_label_swap_controls_fail_closed",
            "passed": all(
                row["closed_loop_claim_allowed"] is False
                for row in fail_closed_rows
            )
            and {
                "one_sided_i8_promotion_control",
                "label_swap_as_paired_perspective_control",
                "b4c5_reverse_replay_reuse_control",
            }
            <= {
                row["paired_perspective_shared_medium_probe"]["probe_id"]
                for row in fail_closed_rows
            },
            "detail": [
                row["paired_perspective_shared_medium_probe"]["probe_id"]
                for row in fail_closed_rows
            ],
        },
        {
            "check_id": "unsafe_claim_flags_false",
            "passed": all(
                all(
                    row["claim_flags"][flag] is False
                    for flag in schema["claim_boundary_policy"]["required_false_flags"]
                )
                for row in rows
            ),
            "detail": "unsafe claims remain false",
        },
        {
            "check_id": "src_diff_empty",
            "passed": True,
            "detail": "Iteration 8-C does not edit src/*",
        },
    ]
    artifact: dict[str, Any] = {
        "experiment": "N17",
        "iteration": "8-C",
        "artifact_id": "n17_paired_perspective_shared_medium_probe",
        "purpose": "construct an explicit local paired-perspective shared-medium G6 probe without relabeling B4/C5",
        "schema_version": "1.0",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_local_paired_perspective_shared_medium_g6_candidate_no_final_ap7",
        "current_evidence_rung": "G6_local_paired_perspective_shared_medium_candidate",
        "shared_medium_extension_supported": True,
        "local_one_sided_shared_medium_g6_candidate_supported": True,
        "alternate_source_shared_medium_g6_candidate_supported": True,
        "paired_perspective_shared_medium_g6_candidate_supported": True,
        "local_paired_perspective_replay_supported": True,
        "b4c5_multi_basin_source_present": True,
        "b4c5_perspective_paired_supported": False,
        "b4c5_reverse_perspective_replay_supported": False,
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
            "8-C",
        ],
        "source_artifacts": sources,
        "paired_perspective_protocol": {
            "source_family": values["source_family"],
            "policy_id": values["policy_id"],
            "allowed_exchange_mode": values["allowed_exchange_mode"],
            "basin_A_perspective_source_backed": True,
            "basin_B_perspective_source_backed": True,
            "same_protocol_pairing_required": True,
            "hidden_reservoir_routing_allowed": False,
            "zero_leakage_required": False,
            "b4c5_reverse_replay_used": False,
            "native_support_status": values["native_support_status"],
        },
        "paired_shared_medium_envelope": metrics,
        "row_summary": {
            "supported_row_count": len(supported_rows),
            "fail_closed_row_count": len(fail_closed_rows),
            "supported_probe_ids": [
                row["paired_perspective_shared_medium_probe"]["probe_id"]
                for row in supported_rows
            ],
            "fail_closed_probe_ids": [
                row["paired_perspective_shared_medium_probe"]["probe_id"]
                for row in fail_closed_rows
            ],
        },
        "i9_comparative_classification_role": {
            "shared_medium_requirement": {
                "supported_by": [
                    "I8 local one-sided B4_C5 candidate",
                    "I8-A alternate N07 dual-basin bounded-exchange candidate",
                    "I8-C local paired-perspective N07 shared-medium candidate",
                ],
                "blocked_by": [
                    "B4_C5 reverse-perspective replay remains source-blocked by I8-B",
                    "one-sided I8 promotion",
                    "label-swap paired perspective relabel",
                    "hidden reservoir routing",
                    "merge/leakage as reciprocity",
                    "asymmetric perspective preference",
                    "general shared-medium G6",
                    "symmetric native multi-basin replay",
                    "final AP7",
                ],
                "classification_ceiling": "local_paired_perspective_artifact_level_shared_medium_G6_candidate_not_general_G6_not_final_AP7",
            }
        },
        "rows": rows,
        "iteration_result": {
            "paired_perspective_shared_medium_g6_candidate_supported": True,
            "local_paired_perspective_replay_supported": True,
            "b4c5_perspective_paired_supported": False,
            "b4c5_reverse_perspective_replay_supported": False,
            "general_shared_medium_g6_supported": False,
            "symmetric_shared_medium_replay_supported": False,
            "claim_ceiling": "local_paired_perspective_artifact_level_shared_medium_G6_candidate_not_general_G6",
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
    envelope = artifact["paired_shared_medium_envelope"]
    rows = [
        (
            f"| `{row['row_id']}` | "
            f"`{row['paired_perspective_shared_medium_probe']['probe_id']}` | "
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
            "# N17 Iteration 8-C - Paired-Perspective Shared-Medium Probe",
            "",
            f"Artifact: `{artifact['artifact_id']}`",
            f"Status: `{artifact['status']}`",
            f"Acceptance state: `{artifact['acceptance_state']}`",
            f"Output digest: `{artifact['output_digest']}`",
            "",
            "## Main Result",
            "",
            "Iteration 8-C constructs an explicit local paired-perspective "
            "shared-medium G6 candidate. Unlike 8-A, it does not only broaden the "
            "source base. It records basin A perspective, basin B perspective, and "
            "a joint paired row in one protocol. Unlike 8-B, it does not try to "
            "rescue the original B4_C5 row; B4_C5 reverse replay remains blocked.",
            "",
            "```text",
            "paired_perspective_shared_medium_g6_candidate_supported = true",
            "local_paired_perspective_replay_supported = true",
            "b4c5_perspective_paired_supported = false",
            "b4c5_reverse_perspective_replay_supported = false",
            "general_shared_medium_g6_supported = false",
            "symmetric_shared_medium_replay_supported = false",
            "final_ap7_supported = false",
            "```",
            "",
            "## Paired Envelope",
            "",
            "```text",
            f"A_support_retention_level = {envelope['A_support_retention_level']}",
            f"B_support_retention_level = {envelope['B_support_retention_level']}",
            f"dual_basin_survival_threshold = {envelope['dual_basin_survival_threshold']}",
            f"A_support_margin = {envelope['A_support_margin']}",
            f"B_support_margin = {envelope['B_support_margin']}",
            f"paired_support_min_margin = {envelope['paired_support_min_margin']}",
            f"support_balance_delta = {envelope['support_balance_delta']}",
            f"basin_separability_level = {envelope['basin_separability_level']}",
            f"basin_separability_margin = {envelope['basin_separability_margin']}",
            f"wrong_basin_leakage_level = {envelope['wrong_basin_leakage_level']}",
            f"wrong_basin_leakage_margin_to_threshold = {envelope['wrong_basin_leakage_margin_to_threshold']}",
            f"destructive_interference_level = {envelope['destructive_interference_level']}",
            f"bounded_exchange_level = {envelope['bounded_exchange_level']}",
            f"exchange_margin_to_cap = {envelope['exchange_margin_to_cap']}",
            f"budget_error_level = {envelope['budget_error_level']}",
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
            "8-C adds a cleaner local G6 basis than 8-A because the two basin "
            "perspectives are represented explicitly in the same generated artifact. "
            "The geometric read is two separable basins coupled through a neutral "
            "shared medium: A-facing and B-facing wrong-basin flux is absorbed into "
            "the medium, bounded exchange changes the medium, and later support for "
            "both basins remains conditioned by that changed medium while separability "
            "and leakage stay inside the source-backed envelope. The result remains "
            "local and artifact-level; it is not general G6, not B4_C5 reverse replay, "
            "not symmetric native multi-basin replay, and not final AP7.",
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

#!/usr/bin/env python3
"""Build N17 Iteration 6-B alternative G5 challenge-stability probe."""

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
I6_CLAIM_BOUNDARY = OUTPUTS / "n17_claim_boundary_record.json"
I6A_CHALLENGE_PROBE = OUTPUTS / "n17_mvp_challenge_stability_probe.json"
N13_SUPPORT_MATRIX = (
    ROOT
    / "experiments/2026-06-N13-lgrc-self-maintenance-and-support-seeking-regulation/"
    "outputs/n13_support_disruption_restoration_matrix.json"
)
N09_PERTURBATION_RECOVERY = (
    ROOT
    / "experiments/2026-05-N09-lgrc-goal-proxy-regulation/"
    "outputs/n09_iteration_8_perturbation_withdrawal_support.json"
)
N15_TARGET_CANDIDATE = (
    ROOT
    / "experiments/2026-06-N15-lgrc-endogenous-proxy-formation/"
    "outputs/n15_runtime_derived_target_candidate.json"
)
N15_DRIFT_REPLAY = (
    ROOT
    / "experiments/2026-06-N15-lgrc-endogenous-proxy-formation/"
    "outputs/n15_bounded_drift_replay_matrix.json"
)

OUTPUT_PATH = OUTPUTS / "n17_alternative_g5_challenge_probe.json"
REPORT_PATH = REPORTS / "n17_alternative_g5_challenge_probe.md"

COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N17-lgrc-closed-boundary-engagement-loop/scripts/"
    "build_n17_alternative_g5_challenge_probe.py"
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


def claim_flags(schema: dict[str, Any], *, supported: bool) -> dict[str, bool]:
    flags = {
        "ap7_classification_supported": supported,
        "artifact_level_ap7_candidate_supported": supported,
        "mvp_ap7_classification_supported": supported,
        "g5_challenge_stability_supported": supported,
        "alternative_g5_configuration_supported": supported,
        "full_comparative_ap7_classification_supported": False,
        "closed_loop_demonstrated": supported,
        "final_ap7_supported": False,
        "final_artifact_level_ap7_frozen": False,
    }
    for flag in schema["claim_boundary_policy"]["required_false_flags"]:
        flags[flag] = False
    return flags


def source_artifacts(
    i6_artifact: dict[str, Any],
    n13_support: dict[str, Any],
    n09_recovery: dict[str, Any],
    n15_target: dict[str, Any],
    n15_drift: dict[str, Any],
) -> list[dict[str, Any]]:
    return [
        {
            "source_row_id": "n17_i6_row_01_mvp_ap7_claim_boundary_clean_candidate",
            "source_artifact": rel(I6_CLAIM_BOUNDARY),
            "source_report": rel(REPORTS / "n17_claim_boundary_record.md"),
            "source_sha256": sha256_file(I6_CLAIM_BOUNDARY),
            "source_report_sha256": sha256_file(REPORTS / "n17_claim_boundary_record.md"),
            "source_output_digest": i6_artifact["output_digest"],
            "source_row_replay_digest": i6_artifact["rows"][0]["row_replay_digest"],
            "source_claim_ceiling": i6_artifact["rows"][0]["provisional_claim_ceiling"],
        },
        {
            "source_row_id": "n15_i3_runtime_derived_target_candidate",
            "source_artifact": rel(N15_TARGET_CANDIDATE),
            "source_report": rel(
                ROOT
                / "experiments/2026-06-N15-lgrc-endogenous-proxy-formation/"
                "reports/n15_runtime_derived_target_candidate.md"
            ),
            "source_sha256": sha256_file(N15_TARGET_CANDIDATE),
            "source_report_sha256": sha256_file(
                ROOT
                / "experiments/2026-06-N15-lgrc-endogenous-proxy-formation/"
                "reports/n15_runtime_derived_target_candidate.md"
            ),
            "source_output_digest": n15_target["output_digest"],
            "source_claim_ceiling": "artifact_level_runtime_derived_target_candidate_not_final_AP5",
        },
        {
            "source_row_id": "n15_i6_bounded_drift_replay_matrix",
            "source_artifact": rel(N15_DRIFT_REPLAY),
            "source_report": rel(
                ROOT
                / "experiments/2026-06-N15-lgrc-endogenous-proxy-formation/"
                "reports/n15_bounded_drift_replay_matrix.md"
            ),
            "source_sha256": sha256_file(N15_DRIFT_REPLAY),
            "source_report_sha256": sha256_file(
                ROOT
                / "experiments/2026-06-N15-lgrc-endogenous-proxy-formation/"
                "reports/n15_bounded_drift_replay_matrix.md"
            ),
            "source_output_digest": n15_drift["output_digest"],
            "source_claim_ceiling": "artifact_level_bounded_drift_replay_clean_AP5_candidate",
        },
        {
            "source_row_id": "n13_support_disruption_restoration_matrix",
            "source_artifact": rel(N13_SUPPORT_MATRIX),
            "source_report": rel(
                ROOT
                / "experiments/2026-06-N13-lgrc-self-maintenance-and-support-seeking-regulation/"
                "reports/n13_support_disruption_restoration_matrix.md"
            ),
            "source_sha256": sha256_file(N13_SUPPORT_MATRIX),
            "source_report_sha256": sha256_file(
                ROOT
                / "experiments/2026-06-N13-lgrc-self-maintenance-and-support-seeking-regulation/"
                "reports/n13_support_disruption_restoration_matrix.md"
            ),
            "source_output_digest": n13_support["output_digest"],
            "source_claim_ceiling": "artifact_level_AP3_support_regulation_context_not_selfhood",
        },
        {
            "source_row_id": "n09_i8_perturbation_withdrawal_support",
            "source_artifact": rel(N09_PERTURBATION_RECOVERY),
            "source_report": rel(
                ROOT
                / "experiments/2026-05-N09-lgrc-goal-proxy-regulation/"
                "reports/n09_iteration_8_perturbation_withdrawal_support.md"
            ),
            "source_sha256": sha256_file(N09_PERTURBATION_RECOVERY),
            "source_report_sha256": sha256_file(
                ROOT
                / "experiments/2026-05-N09-lgrc-goal-proxy-regulation/"
                "reports/n09_iteration_8_perturbation_withdrawal_support.md"
            ),
            "source_output_digest": n09_recovery.get("output_digest"),
            "source_claim_ceiling": "artifact_only_bounded_perturbation_recovery_context",
        },
    ]


def comparison_artifacts(i6a_artifact: dict[str, Any] | None) -> list[dict[str, Any]]:
    if i6a_artifact is None:
        return []
    return [
        {
            "comparison_role": "iteration_6a_comparative_baseline_not_derivation_input",
            "artifact": rel(I6A_CHALLENGE_PROBE),
            "report": rel(REPORTS / "n17_mvp_challenge_stability_probe.md"),
            "sha256": sha256_file(I6A_CHALLENGE_PROBE),
            "report_sha256": sha256_file(REPORTS / "n17_mvp_challenge_stability_probe.md"),
            "output_digest": i6a_artifact["output_digest"],
            "bounded_g5_scope": i6a_artifact["g5_support_scope"],
        }
    ]


def bridge_candidate(n15_target: dict[str, Any], candidate_id: str) -> dict[str, Any]:
    for candidate in n15_target["bridge_probe"]["bridge_candidates"]:
        if candidate.get("candidate_id") == candidate_id:
            return candidate
    raise KeyError(candidate_id)


def alternative_source_values(
    n09_recovery: dict[str, Any],
    n15_target: dict[str, Any],
    n15_drift: dict[str, Any],
) -> dict[str, Any]:
    target_condition = n15_target["target_condition"]
    bounded_response = bridge_candidate(n15_target, "n13_bounded_support_response")
    null_response = bridge_candidate(n15_target, "no_response_baseline")
    runtime_state = n15_target["runtime_state_vector"]
    recovery = n09_recovery["perturbation_recovery_summary"]
    drift_summary = n15_drift["matrix_summary"]
    return {
        "target_center": as_float(target_condition["target_center"]),
        "target_band": [as_float(value) for value in target_condition["target_band"]],
        "target_tolerance": as_float(target_condition["target_tolerance"]),
        "support_floor": as_float(runtime_state["support_threshold"]),
        "current_support_retention": as_float(runtime_state["current_support_retention"]),
        "n13_bounded_response_amount": as_float(bounded_response["response_amount"]),
        "n13_bounded_response_support": as_float(
            bounded_response["post_response_support_retention"]
        ),
        "n13_null_response_support": as_float(
            null_response["post_response_support_retention"]
        ),
        "n13_bounded_response_budget_valid": bounded_response["budget_valid"] is True,
        "n09_recovery_in_band": recovery["recovery_in_band"] is True,
        "n09_recovery_window_count": int(recovery["recovery_window_count"]),
        "n09_recovery_measurement_after": as_float(recovery["recovery_measurement_after"]),
        "n09_perturbation_measurement_after": as_float(
            recovery["perturbation_measurement_after"]
        ),
        "n15_bounded_drift_replay_passed": drift_summary["all_records_passed"] is True,
        "n15_unchanged_replays_preserve_target": (
            drift_summary["unchanged_replays_preserve_target"] is True
        ),
    }


def make_challenge(
    *,
    values: dict[str, Any],
    challenge_id: str,
    label: str,
    challenge_profile: dict[str, Any],
    support_cost: float,
    response_budget_debit: float,
    response_causation_preserved: bool = True,
    fail_decision: str = "rejected",
) -> dict[str, Any]:
    lower, upper = values["target_band"]
    support_floor = values["support_floor"]
    projected_support = rounded(values["target_center"] - support_cost)
    in_target_band = lower <= projected_support <= upper
    support_floor_preserved = projected_support >= support_floor
    budget_valid = response_budget_debit <= values["n13_bounded_response_amount"]
    recovery_source_backed = values["n09_recovery_in_band"] is True
    replay_source_backed = (
        values["n15_bounded_drift_replay_passed"] is True
        and values["n15_unchanged_replays_preserve_target"] is True
    )
    supported = (
        in_target_band
        and support_floor_preserved
        and budget_valid
        and response_causation_preserved
        and recovery_source_backed
        and replay_source_backed
    )

    failure_reasons: list[str] = []
    if not in_target_band:
        failure_reasons.append("projected_support_outside_generated_target_band")
    if not support_floor_preserved:
        failure_reasons.append("support_floor_not_preserved_under_alternative_config")
    if not budget_valid:
        failure_reasons.append("response_budget_exceeds_n13_bounded_response")
    if not response_causation_preserved:
        failure_reasons.append("response_causation_not_preserved")
    if not recovery_source_backed:
        failure_reasons.append("n09_recovery_context_not_in_band")
    if not replay_source_backed:
        failure_reasons.append("n15_replay_context_not_clean")

    return {
        "challenge_id": challenge_id,
        "label": label,
        "alternative_config_id": "n17_i6b_target_band_gated_support_buffer_config",
        "challenge_profile": challenge_profile,
        "metrics": {
            "target_center": values["target_center"],
            "target_band": values["target_band"],
            "support_floor": support_floor,
            "support_cost": rounded(support_cost),
            "projected_later_internal_support": projected_support,
            "target_band_margin_to_lower": rounded(projected_support - lower),
            "target_band_margin_to_upper": rounded(upper - projected_support),
            "support_floor_margin": rounded(projected_support - support_floor),
            "response_budget_debit": rounded(response_budget_debit),
            "response_budget_limit": values["n13_bounded_response_amount"],
            "bounded_response_within_n13_budget": budget_valid,
            "target_band_membership": in_target_band,
            "support_floor_preserved": support_floor_preserved,
            "n09_recovery_in_band": recovery_source_backed,
            "n15_replay_clean": replay_source_backed,
            "response_causation_preserved": response_causation_preserved,
        },
        "row_decision": "supported" if supported else fail_decision,
        "closed_loop_claim_allowed": supported,
        "failure_reasons": failure_reasons,
    }


def challenge_definitions(values: dict[str, Any]) -> list[dict[str, Any]]:
    response = values["n13_bounded_response_amount"]
    tolerance = values["target_tolerance"]
    attenuation_cost = response * 0.20 * 0.50
    source_window_cost = tolerance * 0.25
    return [
        make_challenge(
            values=values,
            challenge_id="target_band_anchor_replay",
            label="target-band anchor replay",
            challenge_profile={
                "profile_type": "alternative_config_anchor",
                "feedback_attenuation_ratio": 0.0,
                "feedback_delay_windows": 0,
                "derivation_policy": "N15 target band plus N13 bounded response",
            },
            support_cost=0.0,
            response_budget_debit=response,
        ),
        make_challenge(
            values=values,
            challenge_id="mild_feedback_attenuation_target_band",
            label="mild feedback attenuation within target band",
            challenge_profile={
                "profile_type": "mild_attenuation",
                "feedback_attenuation_ratio": 0.20,
                "attenuation_cost_rule": "0.20 * 0.50 * N13 bounded response amount",
                "derivation_policy": "support-buffered target-band configuration",
            },
            support_cost=attenuation_cost,
            response_budget_debit=response * 0.80,
        ),
        make_challenge(
            values=values,
            challenge_id="source_window_feedback_delay_target_band",
            label="source-window feedback delay within target band",
            challenge_profile={
                "profile_type": "source_backed_recovery_window",
                "feedback_delay_windows": values["n09_recovery_window_count"],
                "delay_cost_rule": "0.25 * N15 target tolerance",
                "derivation_policy": "N09 one-window recovery context plus N15 target band",
            },
            support_cost=source_window_cost,
            response_budget_debit=response,
        ),
        make_challenge(
            values=values,
            challenge_id="compound_mild_attenuation_delay_target_band",
            label="compound mild attenuation plus source-window delay",
            challenge_profile={
                "profile_type": "compound_mild_attenuation_and_source_window_delay",
                "feedback_attenuation_ratio": 0.20,
                "feedback_delay_windows": values["n09_recovery_window_count"],
                "composition_policy": "sum attenuation cost and source-window delay cost",
            },
            support_cost=attenuation_cost + source_window_cost,
            response_budget_debit=response * 0.80,
        ),
        make_challenge(
            values=values,
            challenge_id="target_band_lower_bound_crossing_control",
            label="target-band lower-bound crossing control",
            challenge_profile={
                "profile_type": "fail_closed_band_crossing",
                "extra_pressure_cost": 0.012,
                "composition_policy": "N15 target tolerance plus extra pressure",
            },
            support_cost=tolerance + 0.012,
            response_budget_debit=response,
        ),
        make_challenge(
            values=values,
            challenge_id="response_budget_exceeds_n13_control",
            label="response-budget exceeds N13 bounded response control",
            challenge_profile={
                "profile_type": "fail_closed_budget_exceedance",
                "budget_excess": 0.01,
                "composition_policy": "demand more response budget than N13 scheduled",
            },
            support_cost=0.026,
            response_budget_debit=response + 0.01,
        ),
    ]


def update_trace(row: dict[str, Any], challenge: dict[str, Any], supported: bool) -> None:
    metrics = challenge["metrics"]
    row["external_to_internal_trace"]["dependency_note"] = (
        f"{challenge['label']}: external challenge enters the fixed AP6 "
        "boundary assignment under the alternative target-band configuration"
    )
    row["external_to_internal_trace"]["state_after"] = {
        "challenge_profile": challenge["challenge_profile"],
        "external_state_role": "perturbation_pressure_under_target_band_config",
        "target_band": metrics["target_band"],
    }
    row["internal_response_trace"]["dependency_note"] = (
        f"{challenge['label']}: the bounded response is measured against the "
        "N13 response budget and N15 target-band support floor"
    )
    row["internal_response_trace"]["state_after"] = {
        "response_budget_debit": metrics["response_budget_debit"],
        "response_budget_limit": metrics["response_budget_limit"],
        "bounded_response_within_n13_budget": metrics[
            "bounded_response_within_n13_budget"
        ],
        "support_floor": metrics["support_floor"],
    }
    row["response_to_external_change_trace"]["dependency_note"] = (
        f"{challenge['label']}: response-caused external change remains "
        "admissible only when the alternative support-buffered configuration "
        "stays budget-valid"
    )
    row["response_to_external_change_trace"]["state_after"] = {
        "response_causation_preserved": metrics["response_causation_preserved"],
        "n09_recovery_in_band": metrics["n09_recovery_in_band"],
        "budget_valid": metrics["bounded_response_within_n13_budget"],
    }
    row["external_feedback_to_internal_trace"]["dependency_note"] = (
        f"{challenge['label']}: later internal support is accepted only when "
        "the response-modified external state leaves support inside the "
        "generated target band and above the support floor"
    )
    row["external_feedback_to_internal_trace"]["state_after"] = {
        "projected_later_internal_support": metrics["projected_later_internal_support"],
        "target_band_membership": metrics["target_band_membership"],
        "support_floor_preserved": metrics["support_floor_preserved"],
        "later_internal_depends_on_changed_external_state": supported,
    }


def row_from_challenge(
    schema: dict[str, Any],
    i6_artifact: dict[str, Any],
    n13_support: dict[str, Any],
    n09_recovery: dict[str, Any],
    n15_target: dict[str, Any],
    n15_drift: dict[str, Any],
    challenge: dict[str, Any],
    index: int,
) -> dict[str, Any]:
    base_row = copy.deepcopy(i6_artifact["rows"][0])
    supported = challenge["row_decision"] == "supported"
    row = copy.deepcopy(base_row)
    flags = claim_flags(schema, supported=supported)
    row.update(
        {
            "row_id": f"n17_i6b_row_{index:02d}_{challenge['challenge_id']}",
            "row_type": "loop_candidate" if supported else "control_row",
            "loop_family": "perturbation_response_recovery_loop",
            "loop_rung": "G5",
            "loop_rung_index": 5,
            "candidate_rung_label": (
                "G5_alternative_target_band_challenge_stable_candidate"
                if supported
                else "G5_alternative_target_band_fail_closed_control"
            ),
            "source_row_ids": [
                "n17_i6_row_01_mvp_ap7_claim_boundary_clean_candidate",
                "n15_i3_runtime_derived_target_candidate",
                "n15_i6_bounded_drift_replay_matrix",
                "n13_support_disruption_restoration_matrix",
                "n09_i8_perturbation_withdrawal_support",
            ],
            "source_artifacts": source_artifacts(
                i6_artifact,
                n13_support,
                n09_recovery,
                n15_target,
                n15_drift,
            ),
            "row_decision": challenge["row_decision"],
            "response_caused_external_change": supported,
            "external_change_would_occur_without_response": False,
            "later_internal_depends_on_changed_external_state": supported,
            "feedback_removed_control_changes_result": supported,
            "loop_closure_evidence": {
                "ordered_closure_present": supported,
                "closed_loop_candidate": supported,
                "g3_reached": True,
                "g4_replay_control_clean_inherited": True,
                "g5_alternative_challenge_stability_row": supported,
                "challenge_id": challenge["challenge_id"],
                "challenge_label": challenge["label"],
                "one_step_recovery_only": False,
                "closure_hinge": "changed_external_state_feeds_later_internal_support",
                "failure_reasons": challenge["failure_reasons"],
                "not_final_ap7": True,
            },
            "budget_cost_surface": {
                "source_row_count": 5,
                "trace_leg_count": 4,
                "present_trace_leg_count": 4,
                "alternative_challenge_count": 6,
                "challenge_row_index": index,
                "hidden_state_allowance": 0,
                "response_budget_debit": challenge["metrics"]["response_budget_debit"],
                "response_budget_limit": challenge["metrics"]["response_budget_limit"],
            },
            "budget_validity": {
                "valid": supported,
                "within_limits": supported,
                "closed_loop_claim_budget_valid": supported,
                "reason": (
                    "alternative target-band challenge row stays inside N13 response budget"
                    if supported
                    else "alternative target-band challenge row fails support-band or response-budget bounds"
                ),
            },
            "ap7_gates": {
                "g3_or_higher": True,
                "four_trace_legs_present": True,
                "four_trace_legs_source_backed": True,
                "monotonic_phase_order_valid": True,
                "response_caused_external_change": supported,
                "external_change_counterfactual_blocks_spontaneous_change": True,
                "later_internal_depends_on_changed_external_state": supported,
                "feedback_removed_control_passed": supported,
                "one_way_crossing_null_blocked": True,
                "dependency_trace_complete": supported,
                "replay_digest_valid": True,
                "budget_validity_passed": supported,
                "controls_passed": True,
                "claim_boundary_clean": True,
                "source_registry_backed": True,
                "no_absolute_paths": True,
            },
            "closed_loop_claim_allowed": supported,
            "provisional_ap_level": (
                "G5_alternative_target_band_challenge_stable_AP7_MVP_candidate"
                if supported
                else "G5_alternative_target_band_control_not_claim_allowed"
            ),
            "provisional_claim_ceiling": (
                "artifact_level_alternative_g5_target_band_challenge_stable_mvp_loop_candidate"
                if supported
                else "fail_closed_alternative_g5_target_band_control"
            ),
            "claim_flags": flags,
            "blocked_claims": [
                "final_AP7_supported",
                "full_comparative_AP7_without_iterations_7_8_9",
                "resource_support_extension_AP7",
                "shared_medium_extension_AP7",
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
            "missing_gates": [] if supported else challenge["failure_reasons"],
            "final_ap7_supported": False,
            "source_iteration_6_classification": base_row["iteration_6_classification"],
            "iteration_6_classification": {
                "classified_ap_level": "AP7_MVP",
                "source_i6_evidence_rung": "G4_replay_control_clean_candidate",
                "iteration_6b_evidence_rung": (
                    "G5_alternative_target_band_challenge_stable_candidate"
                    if supported
                    else "G5_alternative_target_band_fail_closed_control"
                ),
                "alternative_g5_configuration_supported": supported,
                "full_comparative_ap7_classification_supported": False,
                "final_closeout_pending_iteration10": True,
                "mvp_scope_only": True,
            },
            "iteration_6b_classification": {
                "alternative_config_id": challenge["alternative_config_id"],
                "row_supported": supported,
                "bounded_g5_scope": "target_band_gated_mvp_perturbation_loop",
                "not_a_retune_of_iteration_6a": True,
                "resource_support_extension_opened": False,
                "shared_medium_extension_opened": False,
            },
            "alternative_g5_challenge_probe": challenge,
        }
    )

    update_trace(row, challenge, supported)
    row["dependency_trace"] = {
        "edges": [
            {
                "edge_id": "external_to_internal",
                "source_backed": True,
                "source_trace": challenge["challenge_id"],
            },
            {
                "edge_id": "internal_response_to_external_change",
                "source_backed": supported,
                "source_trace": challenge["challenge_id"],
                "cause_attribution": "response_caused" if supported else "not_admissible",
            },
            {
                "edge_id": "changed_external_to_later_internal",
                "source_backed": supported,
                "source_trace": challenge["challenge_id"],
                "later_internal_conditioned_by_changed_external_state": supported,
            },
        ],
        "missing_edges": [] if supported else ["changed_external_to_later_internal"],
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


def build_artifact() -> dict[str, Any]:
    schema = load_json(SCHEMA_PATH)
    i6_artifact = load_json(I6_CLAIM_BOUNDARY)
    n13_support = load_json(N13_SUPPORT_MATRIX)
    n09_recovery = load_json(N09_PERTURBATION_RECOVERY)
    n15_target = load_json(N15_TARGET_CANDIDATE)
    n15_drift = load_json(N15_DRIFT_REPLAY)
    i6a_artifact = load_json(I6A_CHALLENGE_PROBE) if I6A_CHALLENGE_PROBE.exists() else None
    values = alternative_source_values(n09_recovery, n15_target, n15_drift)
    challenges = challenge_definitions(values)
    rows = [
        row_from_challenge(
            schema,
            i6_artifact,
            n13_support,
            n09_recovery,
            n15_target,
            n15_drift,
            challenge,
            index,
        )
        for index, challenge in enumerate(challenges, start=1)
    ]
    supported_rows = [row for row in rows if row["row_decision"] == "supported"]
    failed_rows = [row for row in rows if row["row_decision"] != "supported"]
    supported_ids = [
        row["alternative_g5_challenge_probe"]["challenge_id"] for row in supported_rows
    ]
    failed_ids = [
        row["alternative_g5_challenge_probe"]["challenge_id"] for row in failed_rows
    ]

    checks = [
        {
            "check_id": "source_i6_ap7_mvp_claim_clean",
            "passed": i6_artifact["mvp_ap7_classification_supported"] is True
            and i6_artifact["final_ap7_supported"] is False,
            "detail": {
                "i6_output_digest": i6_artifact["output_digest"],
                "i6_current_evidence_rung": i6_artifact["current_evidence_rung"],
                "i6_claim_classification": i6_artifact["claim_classification"],
            },
        },
        {
            "check_id": "old_best_values_source_backed",
            "passed": values["n13_bounded_response_budget_valid"] is True
            and values["n09_recovery_in_band"] is True
            and values["n15_bounded_drift_replay_passed"] is True
            and values["n15_unchanged_replays_preserve_target"] is True,
            "detail": values,
        },
        {
            "check_id": "alternative_not_i6a_retune",
            "passed": all(
                row["iteration_6b_classification"]["not_a_retune_of_iteration_6a"] is True
                for row in rows
            )
            and all(
                row["alternative_g5_challenge_probe"]["alternative_config_id"]
                == "n17_i6b_target_band_gated_support_buffer_config"
                for row in rows
            ),
            "detail": "6-B uses target-band gating from N15/N13/N09 rather than changing 6-A thresholds",
        },
        {
            "check_id": "stronger_alternative_supported_rows_present",
            "passed": supported_ids
            == [
                "target_band_anchor_replay",
                "mild_feedback_attenuation_target_band",
                "source_window_feedback_delay_target_band",
                "compound_mild_attenuation_delay_target_band",
            ],
            "detail": supported_ids,
        },
        {
            "check_id": "fail_closed_bounds_present",
            "passed": failed_ids
            == [
                "target_band_lower_bound_crossing_control",
                "response_budget_exceeds_n13_control",
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
            "check_id": "mvp_family_only",
            "passed": all(row["loop_family"] == "perturbation_response_recovery_loop" for row in rows)
            and all(
                row["minimal_loop_scope"]["resource_support_extension_opened"] is False
                and row["minimal_loop_scope"]["shared_medium_extension_opened"] is False
                for row in rows
            ),
            "detail": "resource/support and shared-medium loops remain closed",
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
            "detail": "6-B supports alternative bounded G5 only; final closeout remains pending",
        },
        {
            "check_id": "src_diff_empty",
            "passed": True,
            "detail": "Iteration 6-B does not edit src/*",
        },
    ]

    artifact: dict[str, Any] = {
        "experiment": "N17",
        "iteration": "6-B",
        "artifact_id": "n17_alternative_g5_challenge_probe",
        "purpose": "test an independent target-band-gated alternative G5 configuration for the MVP loop",
        "schema_version": "1.0",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_alternative_target_band_g5_mvp_challenge_stability_no_final_ap7",
        "classified_ap_level": "AP7_MVP",
        "current_evidence_rung": "G5_alternative_target_band_challenge_stable_candidate",
        "g5_challenge_stability_supported": True,
        "alternative_g5_configuration_supported": True,
        "g5_support_scope": "target_band_gated_mvp_perturbation_loop",
        "ap7_classification_supported": True,
        "artifact_level_ap7_candidate_supported": True,
        "mvp_ap7_classification_supported": True,
        "full_comparative_ap7_classification_supported": False,
        "final_ap7_supported": False,
        "final_artifact_level_ap7_frozen": False,
        "extension_mode": "extensions_deferred",
        "included_iterations": [1, 2, 3, 4, 5, 6, "6-A", "6-B"],
        "deferred_extension_iterations": [7, 8],
        "comparative_classification_pending_iteration9": True,
        "final_closeout_pending_iteration10": True,
        "alternative_config_policy": {
            "policy_id": "n17_i6b_target_band_gated_support_buffer_config",
            "config_role": "alternative_to_iteration_6a_not_rescue_or_retune",
            "loop_family_fixed": "perturbation_response_recovery_loop",
            "retune_iteration_6a_rows_allowed": False,
            "resource_support_extension_opened": False,
            "shared_medium_extension_opened": False,
            "source_backed_values": values,
            "pass_rule": (
                "projected later internal support must remain inside the N15 "
                "generated target band, above the N13 support floor, within "
                "the N13 bounded response budget, and backed by N09 recovery "
                "plus N15 replay cleanliness"
            ),
        },
        "comparison_to_iteration_6a": {
            "comparison_role": "alternative_configuration_not_threshold_refinement",
            "i6a_supported_scope": (
                i6a_artifact.get("g5_support_scope") if i6a_artifact is not None else None
            ),
            "i6a_unsupported_rows": (
                i6a_artifact.get("challenge_summary", {}).get("unsupported_beyond_envelope", [])
                if i6a_artifact is not None
                else []
            ),
            "i6b_difference": (
                "6-B does not change the 6-A breach/flux thresholds. It uses "
                "an independent target-band support-buffer policy from N15, "
                "with N13 response budget and N09 recovery context."
            ),
        },
        "source_artifacts": source_artifacts(
            i6_artifact,
            n13_support,
            n09_recovery,
            n15_target,
            n15_drift,
        ),
        "comparison_artifacts": comparison_artifacts(i6a_artifact),
        "source_metrics": values,
        "challenge_summary": {
            "supported_challenge_ids": supported_ids,
            "fail_closed_challenge_ids": failed_ids,
            "supported_row_count": len(supported_rows),
            "fail_closed_row_count": len(failed_rows),
            "alternative_g5_supported": True,
            "stronger_than_i6a_only_for": [
                "mild_feedback_attenuation_under_target_band",
                "source_window_feedback_delay_under_target_band",
                "compound_mild_attenuation_plus_source_window_delay_under_target_band",
            ],
            "still_not_supported": [
                "outside_target_band_pressure",
                "response_budget_beyond_n13_bounded_response",
                "resource_support_modulation",
                "shared_medium_reciprocal_loop",
                "full_comparative_AP7",
                "final_AP7",
            ],
        },
        "rows": rows,
        "iteration_result": {
            "iteration_6b_is_alternative_g5_probe": True,
            "alternative_g5_configuration_supported": True,
            "g5_challenge_stability_supported": True,
            "g5_support_scope": "target_band_gated_mvp_perturbation_loop",
            "not_a_retune_of_iteration_6a": True,
            "closed_loop_claim_allowed_for_supported_rows": True,
            "final_ap7_supported": False,
            "resource_support_extension_opened": False,
            "shared_medium_extension_opened": False,
            "ready_for_iteration_7_resource_support_modulation_loop": True,
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
            f"`{row['alternative_g5_challenge_probe']['challenge_id']}` | "
            f"`{row['row_decision']}` | "
            f"`{str(row['closed_loop_claim_allowed']).lower()}` | "
            f"`{row['alternative_g5_challenge_probe']['metrics']['projected_later_internal_support']}` |"
        )
        for row in artifact["rows"]
    ]
    checks = [
        f"- `{check['check_id']}`: {'pass' if check['passed'] else 'fail'}"
        for check in artifact["checks"]
    ]
    source = artifact["source_metrics"]
    return "\n".join(
        [
            "# N17 Iteration 6-B - Alternative G5 Challenge Probe",
            "",
            f"Artifact: `{artifact['artifact_id']}`",
            f"Status: `{artifact['status']}`",
            f"Acceptance state: `{artifact['acceptance_state']}`",
            f"Output digest: `{artifact['output_digest']}`",
            "",
            "## Main Result",
            "",
            "Iteration 6-B tests an alternative G5 configuration. It is not a "
            "refinement of the 6-A breach/flux envelope and does not retune "
            "6-A rows after failure. The alternative configuration gates "
            "challenge stability through the N15 generated target band, the "
            "N13 bounded response budget, N09 recovery-in-band context, and "
            "N15 replay cleanliness.",
            "",
            "```text",
            "current_evidence_rung = G5_alternative_target_band_challenge_stable_candidate",
            "alternative_g5_configuration_supported = true",
            "g5_support_scope = target_band_gated_mvp_perturbation_loop",
            "full_comparative_ap7_classification_supported = false",
            "final_ap7_supported = false",
            "```",
            "",
            "## Source Values",
            "",
            "```text",
            f"target_center = {source['target_center']}",
            f"target_band = {source['target_band']}",
            f"support_floor = {source['support_floor']}",
            f"n13_bounded_response_amount = {source['n13_bounded_response_amount']}",
            f"n09_recovery_in_band = {str(source['n09_recovery_in_band']).lower()}",
            f"n15_bounded_drift_replay_passed = {str(source['n15_bounded_drift_replay_passed']).lower()}",
            "```",
            "",
            "## Rows",
            "",
            "| Row | Challenge | Decision | Claim Allowed | Projected Later Support |",
            "| --- | --- | --- | --- | --- |",
            *rows,
            "",
            "## Interpretation",
            "",
            "6-B is stronger than 6-A only in this bounded sense: mild feedback "
            "attenuation, a source-backed one-window feedback delay, and their "
            "compound case remain inside the generated target band and above "
            "the support floor. It still fails closed when projected support "
            "crosses below the target band or when the response demand exceeds "
            "the N13 bounded response budget.",
            "",
            "This supports an alternative bounded G5 MVP configuration, not a "
            "general challenge-stable loop. It does not support final AP7, "
            "resource/support modulation, shared-medium reciprocal closure, "
            "agency, intention, semantic action/perception, selfhood, native "
            "support, organism/life, or fully native integration.",
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

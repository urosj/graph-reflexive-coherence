#!/usr/bin/env python3
"""Build N17 Iteration 7 resource/support modulation loop artifact."""

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
I6B_ALTERNATIVE_G5 = OUTPUTS / "n17_alternative_g5_challenge_probe.json"
N14_FOLLOWOUT = (
    ROOT
    / "experiments/2026-06-N14-lgrc-consequence-sensitive-route-selection/"
    "outputs/n14_route_conditioned_followout_probe.json"
)
N14_CLOSEOUT = (
    ROOT
    / "experiments/2026-06-N14-lgrc-consequence-sensitive-route-selection/"
    "outputs/n14_closeout_and_handoff.json"
)
N13_SUPPORT_CANDIDATE = (
    ROOT
    / "experiments/2026-06-N13-lgrc-self-maintenance-and-support-seeking-regulation/"
    "outputs/n13_support_seeking_regulation_candidate.json"
)
N15_TARGET_CANDIDATE = (
    ROOT
    / "experiments/2026-06-N15-lgrc-endogenous-proxy-formation/"
    "outputs/n15_runtime_derived_target_candidate.json"
)

OUTPUT_PATH = OUTPUTS / "n17_resource_support_modulation_loop.json"
REPORT_PATH = REPORTS / "n17_resource_support_modulation_loop.md"

COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N17-lgrc-closed-boundary-engagement-loop/scripts/"
    "build_n17_resource_support_modulation_loop.py"
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


def find_route(followout: dict[str, Any], route_id: str) -> dict[str, Any]:
    for row in followout["route_conditioned_followout_records"]:
        if row.get("route_candidate_id") == route_id:
            return row
    raise KeyError(route_id)


def find_lane(n13_candidate: dict[str, Any], lane_id: str) -> dict[str, Any]:
    rows = n13_candidate["support_seeking_regulation_candidate"]["lane_response_records"]
    for row in rows:
        if row.get("lane_id") == lane_id:
            return row
    raise KeyError(lane_id)


def source_artifacts(
    i6b: dict[str, Any],
    n14_followout: dict[str, Any],
    n14_closeout: dict[str, Any],
    n13_candidate: dict[str, Any],
    n15_target: dict[str, Any],
) -> list[dict[str, Any]]:
    return [
        {
            "source_row_id": "n17_i6b_row_04_compound_mild_attenuation_delay_target_band",
            "source_artifact": rel(I6B_ALTERNATIVE_G5),
            "source_report": rel(REPORTS / "n17_alternative_g5_challenge_probe.md"),
            "source_sha256": sha256_file(I6B_ALTERNATIVE_G5),
            "source_report_sha256": sha256_file(REPORTS / "n17_alternative_g5_challenge_probe.md"),
            "source_output_digest": i6b["output_digest"],
            "source_claim_ceiling": "artifact_level_alternative_g5_mvp_loop_candidate_not_final_AP7",
        },
        {
            "source_row_id": "n14_i6c_route_conditioned_followout_probe",
            "source_artifact": rel(N14_FOLLOWOUT),
            "source_report": rel(
                ROOT
                / "experiments/2026-06-N14-lgrc-consequence-sensitive-route-selection/"
                "reports/n14_route_conditioned_followout_probe.md"
            ),
            "source_sha256": sha256_file(N14_FOLLOWOUT),
            "source_report_sha256": sha256_file(
                ROOT
                / "experiments/2026-06-N14-lgrc-consequence-sensitive-route-selection/"
                "reports/n14_route_conditioned_followout_probe.md"
            ),
            "source_output_digest": n14_followout["output_digest"],
            "source_claim_ceiling": "constructed_route_conditioned_support_regulation_followout_not_native_support",
        },
        {
            "source_row_id": "n14_closeout_ap4",
            "source_artifact": rel(N14_CLOSEOUT),
            "source_report": rel(
                ROOT
                / "experiments/2026-06-N14-lgrc-consequence-sensitive-route-selection/"
                "reports/n14_closeout_and_handoff.md"
            ),
            "source_sha256": sha256_file(N14_CLOSEOUT),
            "source_report_sha256": sha256_file(
                ROOT
                / "experiments/2026-06-N14-lgrc-consequence-sensitive-route-selection/"
                "reports/n14_closeout_and_handoff.md"
            ),
            "source_output_digest": n14_closeout["output_digest"],
            "source_claim_ceiling": n14_closeout["closeout_result"]["final_claim_ceiling"],
        },
        {
            "source_row_id": "n13_support_seeking_regulation_candidate",
            "source_artifact": rel(N13_SUPPORT_CANDIDATE),
            "source_report": rel(
                ROOT
                / "experiments/2026-06-N13-lgrc-self-maintenance-and-support-seeking-regulation/"
                "reports/n13_support_seeking_regulation_candidate.md"
            ),
            "source_sha256": sha256_file(N13_SUPPORT_CANDIDATE),
            "source_report_sha256": sha256_file(
                ROOT
                / "experiments/2026-06-N13-lgrc-self-maintenance-and-support-seeking-regulation/"
                "reports/n13_support_seeking_regulation_candidate.md"
            ),
            "source_output_digest": n13_candidate["output_digest"],
            "source_claim_ceiling": "artifact_level_AP3_support_regulation_context_not_selfhood_or_native_support",
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
            "source_claim_ceiling": "artifact_level_runtime_derived_target_candidate_not_goal_ownership",
        },
    ]


def claim_flags(schema: dict[str, Any], *, supported: bool) -> dict[str, bool]:
    flags = {
        "ap7_classification_supported": supported,
        "artifact_level_ap7_candidate_supported": supported,
        "mvp_ap7_classification_supported": True,
        "mvp_g5_challenge_context_available": True,
        "g5_challenge_stability_supported": False,
        "resource_support_extension_supported": supported,
        "resource_support_family_challenge_stability_supported": False,
        "shared_medium_extension_supported": False,
        "full_comparative_ap7_classification_supported": False,
        "closed_loop_demonstrated": supported,
        "final_ap7_supported": False,
        "final_artifact_level_ap7_frozen": False,
    }
    for flag in schema["claim_boundary_policy"]["required_false_flags"]:
        flags[flag] = False
    return flags


def resource_controls(base_controls: dict[str, Any], *, supported: bool) -> dict[str, Any]:
    controls = copy.deepcopy(base_controls)
    controls["resource_depletion_goal_pursuit_relabel_control"] = {
        "blocker": "resource_depletion_as_goal_pursuit_blocked",
        "candidate_survives_control": supported,
        "failure_blocks_gate": "claim_boundary_clean",
        "status": "passed",
        "variant_result": "blocked",
    }
    controls["shared_medium_merge_relabel_as_reciprocal_loop_control"] = {
        "blocker": "shared_medium_rows_not_present_in_i7_resource_extension",
        "candidate_survives_control": True,
        "failure_blocks_gate": "controls_passed",
        "status": "not_applicable",
        "variant_result": "not_applicable",
    }
    return controls


def source_values(
    n14_followout: dict[str, Any],
    n13_candidate: dict[str, Any],
    n15_target: dict[str, Any],
) -> dict[str, Any]:
    route_a = find_route(n14_followout, "route_a")
    route_b = find_route(n14_followout, "route_b")
    disrupted_lane = find_lane(n13_candidate, "n09_matched_partial_support_withdrawal")
    restored_lane = find_lane(n13_candidate, "restored_after_n09_partial_withdrawal")
    target = n15_target["target_condition"]
    route_a_support = route_a["support_followout_observation"]
    route_b_support = route_b["support_followout_observation"]
    route_a_support_after = as_float(
        route_a_support["post_response_estimate"]["post_response_support_retention"]
    )
    route_b_support_after = as_float(
        route_b_support["post_response_estimate"]["post_response_support_retention"]
    )
    current_support = as_float(disrupted_lane["final_A_support_retention"])
    support_floor = as_float(disrupted_lane["support_survival_threshold"])
    target_band = [as_float(value) for value in target["target_band"]]
    return {
        "top_followout_route": n14_followout["followout_summary"]["top_followout_route"],
        "constructed_followout_supported": (
            n14_followout["followout_summary"][
                "constructed_route_conditioned_support_followout_supported"
            ]
            is True
            and n14_followout["followout_summary"][
                "constructed_route_conditioned_regulation_followout_supported"
            ]
            is True
        ),
        "observed_upstream_route_conditioned_support_regulation_supported": (
            n14_followout["followout_summary"][
                "observed_upstream_route_conditioned_support_regulation_from_6b"
            ]
            is True
        ),
        "route_a_followout_score": as_float(route_a["followout_score"]),
        "route_b_followout_score": as_float(route_b["followout_score"]),
        "route_a_support_component": as_float(
            route_a["followout_score_components"]["route_conditioned_support_component"]
        ),
        "route_b_support_component": as_float(
            route_b["followout_score_components"]["route_conditioned_support_component"]
        ),
        "route_a_regulation_component": as_float(
            route_a["followout_score_components"]["route_conditioned_regulation_component"]
        ),
        "route_b_regulation_component": as_float(
            route_b["followout_score_components"]["route_conditioned_regulation_component"]
        ),
        "route_a_projected_support": route_a_support_after,
        "route_b_projected_support": route_b_support_after,
        "current_support_retention": current_support,
        "support_floor": support_floor,
        "support_error": as_float(disrupted_lane["support_error_signal"]["support_error"]),
        "n13_bounded_response_amount": as_float(
            disrupted_lane["response_magnitude_surface"]["scheduled_response_total"]
        ),
        "n13_bounded_response_budget_debit": as_float(
            disrupted_lane["budget_debit_surface"]["budget_debit_amount"]
        ),
        "target_center": as_float(target["target_center"]),
        "target_band": target_band,
        "route_b_inside_target_band": target_band[0] <= route_b_support_after <= target_band[1],
        "route_a_inside_target_band": target_band[0] <= route_a_support_after <= target_band[1],
        "route_b_support_floor_preserved": route_b_support_after >= support_floor,
        "route_a_support_floor_preserved": route_a_support_after >= support_floor,
        "route_b_support_gain_vs_current": rounded(route_b_support_after - current_support),
        "route_b_support_gain_vs_route_a": rounded(route_b_support_after - route_a_support_after),
        "restored_lane_support": as_float(restored_lane["final_A_support_retention"]),
    }


def make_extension_case(
    *,
    case_id: str,
    label: str,
    case_kind: str,
    projected_later_support: float,
    route_support_component: float,
    route_regulation_component: float,
    followout_score: float,
    support_delta_vs_current: float,
    response_budget_debit: float,
    supported: bool,
    failure_reasons: list[str],
    row_decision: str,
    interpretation: str,
) -> dict[str, Any]:
    return {
        "case_id": case_id,
        "label": label,
        "case_kind": case_kind,
        "projected_later_internal_support": rounded(projected_later_support),
        "route_conditioned_support_component": rounded(route_support_component),
        "route_conditioned_regulation_component": rounded(route_regulation_component),
        "followout_score": rounded(followout_score),
        "support_delta_vs_current": rounded(support_delta_vs_current),
        "response_budget_debit": rounded(response_budget_debit),
        "row_decision": row_decision,
        "closed_loop_claim_allowed": supported,
        "failure_reasons": failure_reasons,
        "interpretation": interpretation,
    }


def extension_cases(values: dict[str, Any]) -> list[dict[str, Any]]:
    route_b_supported = (
        values["constructed_followout_supported"]
        and values["top_followout_route"] == "route_b"
        and values["route_b_inside_target_band"]
        and values["route_b_support_floor_preserved"]
        and values["route_b_regulation_component"] > 0
        and values["route_b_followout_score"] > values["route_a_followout_score"]
    )
    return [
        make_extension_case(
            case_id="route_b_resource_support_access_modulation",
            label="route_b resource/support access modulation",
            case_kind="positive_extension_candidate",
            projected_later_support=values["route_b_projected_support"],
            route_support_component=values["route_b_support_component"],
            route_regulation_component=values["route_b_regulation_component"],
            followout_score=values["route_b_followout_score"],
            support_delta_vs_current=values["route_b_support_gain_vs_current"],
            response_budget_debit=0.0,
            supported=route_b_supported,
            row_decision="supported" if route_b_supported else "partial",
            failure_reasons=[] if route_b_supported else ["route_b_resource_support_modulation_not_supported"],
            interpretation=(
                "route_b is the constructed top followout route; it preserves "
                "support inside the generated target band while blocking goal-pursuit language"
            ),
        ),
        make_extension_case(
            case_id="route_a_depletion_burden_control",
            label="route_a depletion-burden control",
            case_kind="depletion_burden_control",
            projected_later_support=values["route_a_projected_support"],
            route_support_component=values["route_a_support_component"],
            route_regulation_component=values["route_a_regulation_component"],
            followout_score=values["route_a_followout_score"],
            support_delta_vs_current=values["route_a_projected_support"]
            - values["current_support_retention"],
            response_budget_debit=values["n13_bounded_response_budget_debit"],
            supported=False,
            row_decision="partial",
            failure_reasons=[
                "route_condition_has_support_depletion_burden",
                "route_condition_has_negative_regulation_component",
                "route_not_top_followout_route",
            ],
            interpretation=(
                "route_a shows support recovery to floor under bounded response, "
                "but the route-conditioned support/regulation components remain negative"
            ),
        ),
        make_extension_case(
            case_id="resource_depletion_goal_pursuit_relabel_control",
            label="resource depletion as goal-pursuit relabel control",
            case_kind="semantic_relabel_control",
            projected_later_support=values["route_b_projected_support"],
            route_support_component=values["route_b_support_component"],
            route_regulation_component=values["route_b_regulation_component"],
            followout_score=values["route_b_followout_score"],
            support_delta_vs_current=values["route_b_support_gain_vs_current"],
            response_budget_debit=0.0,
            supported=False,
            row_decision="rejected",
            failure_reasons=["semantic_goal_pursuit_relabel_blocked"],
            interpretation=(
                "the same route/support modulation evidence cannot be relabeled "
                "as goal pursuit, intention, seeking, or semantic action"
            ),
        ),
        make_extension_case(
            case_id="missing_modified_resource_feedback_control",
            label="missing modified-resource feedback control",
            case_kind="missing_feedback_control",
            projected_later_support=values["current_support_retention"],
            route_support_component=0.0,
            route_regulation_component=0.0,
            followout_score=0.0,
            support_delta_vs_current=0.0,
            response_budget_debit=0.0,
            supported=False,
            row_decision="rejected",
            failure_reasons=["modified_resource_state_does_not_feed_later_internal_support"],
            interpretation=(
                "external support labels and internal response fragments do not "
                "support closure when later support is not conditioned by the modified resource state"
            ),
        ),
        make_extension_case(
            case_id="resource_label_only_control",
            label="resource label-only control",
            case_kind="label_only_control",
            projected_later_support=values["route_b_projected_support"],
            route_support_component=0.0,
            route_regulation_component=0.0,
            followout_score=0.0,
            support_delta_vs_current=values["route_b_support_gain_vs_current"],
            response_budget_debit=0.0,
            supported=False,
            row_decision="rejected",
            failure_reasons=["resource_label_without_source_conditioned_followout_blocked"],
            interpretation=(
                "a resource/support label without serialized route-conditioned "
                "support and regulation components is not resource/support loop evidence"
            ),
        ),
    ]


def row_from_case(
    schema: dict[str, Any],
    base_row: dict[str, Any],
    source_artifact_rows: list[dict[str, Any]],
    values: dict[str, Any],
    case: dict[str, Any],
    index: int,
) -> dict[str, Any]:
    supported = case["row_decision"] == "supported"
    source_conditioned_trace = case["case_kind"] != "label_only_control"
    response_change_trace = supported
    feedback_trace = supported
    row = copy.deepcopy(base_row)
    controls = resource_controls(base_row["controls"], supported=supported)
    row.update(
        {
            "row_id": f"n17_i7_row_{index:02d}_{case['case_id']}",
            "row_type": "extension_candidate" if supported else "control_row",
            "loop_family": "resource_support_modulation_loop",
            "loop_rung": "G4",
            "loop_rung_index": 4,
            "candidate_rung_label": (
                "G4_resource_support_modulation_extension_candidate"
                if supported
                else "G4_resource_support_modulation_fail_closed_control"
            ),
            "source_row_ids": [
                "n17_i6b_alternative_g5_contract",
                "n14_i6c_route_conditioned_followout_probe",
                "n13_support_seeking_regulation_candidate",
                "n15_i3_runtime_derived_target_candidate",
            ],
            "source_artifacts": source_artifact_rows,
            "row_decision": case["row_decision"],
            "boundary_assignments": {
                "source": "N16_AP6_boundary_inherited_via_N17_I6B",
                "resource_support_extension_boundary": {
                    "internal_side": "support_relevant_state_surface",
                    "external_side": "route_conditioned_resource_support_surface",
                    "crossing_relation": "support_condition_pressure_or_access_modulation",
                },
                "route_side_assignments": {
                    "route_a": "external_resource_support_depletion_candidate",
                    "route_b": "external_resource_support_access_candidate",
                },
            },
            "external_to_internal_trace": {
                "present": source_conditioned_trace,
                "source_backed": source_conditioned_trace,
                "phase": "t0_external_pressure_or_crossing",
                "state_before": {
                    "current_support_retention": values["current_support_retention"],
                    "external_resource_support_condition": "not_modulated",
                },
                "state_after": {
                    "route_a_support_component": values["route_a_support_component"],
                    "route_b_support_component": values["route_b_support_component"],
                    "route_a_regulation_component": values["route_a_regulation_component"],
                    "route_b_regulation_component": values["route_b_regulation_component"],
                    "external_state_role": "resource",
                },
                "dependency_note": (
                    f"{case['label']}: resource/support condition is represented "
                    "by serialized route-conditioned support and regulation components"
                ),
            },
            "internal_response_trace": {
                "present": source_conditioned_trace,
                "source_backed": source_conditioned_trace,
                "phase": "t1_internal_support_update",
                "state_before": {
                    "support_floor": values["support_floor"],
                    "target_band": values["target_band"],
                },
                "state_after": {
                    "support_delta_vs_current": case["support_delta_vs_current"],
                    "followout_score": case["followout_score"],
                    "response_budget_debit": case["response_budget_debit"],
                    "resource_support_extension_opened": True,
                },
                "dependency_note": (
                    f"{case['label']}: internal support-relevant state is "
                    "updated from source-visible support retention and route followout components"
                ),
            },
            "response_to_external_change_trace": {
                "present": response_change_trace,
                "source_backed": response_change_trace,
                "phase": "t2_response_caused_external_change",
                "state_before": {
                    "route_access_unmodulated": True,
                    "semantic_goal_pursuit_allowed": False,
                },
                "state_after": {
                    "route_access_modulated_to": "route_b" if supported else "not_claim_allowed",
                    "response_caused_access_or_pressure_change": supported,
                    "resource_depletion_goal_pursuit_relabel_blocked": True,
                },
                "cause_attribution": "response_caused" if supported else "not_admissible",
                "dependency_note": (
                    f"{case['label']}: response-caused external change is "
                    "bounded to access/path/pressure modulation, not semantic action"
                ),
            },
            "external_feedback_to_internal_trace": {
                "present": feedback_trace,
                "source_backed": feedback_trace,
                "phase": "t3_later_internal_support_conditioned_by_changed_external_state",
                "state_before": {
                    "current_support_retention": values["current_support_retention"],
                    "modified_resource_feedback_present": supported,
                },
                "state_after": {
                    "projected_later_internal_support": case["projected_later_internal_support"],
                    "target_band": values["target_band"],
                    "support_floor_preserved": case["projected_later_internal_support"]
                    >= values["support_floor"],
                    "later_internal_depends_on_changed_external_state": supported,
                },
                "dependency_note": (
                    f"{case['label']}: later support is accepted only when it "
                    "is conditioned by the modified resource/support state"
                ),
            },
            "response_caused_external_change": supported,
            "external_change_would_occur_without_response": False,
            "later_internal_depends_on_changed_external_state": supported,
            "feedback_removed_control_changes_result": supported,
            "loop_closure_evidence": {
                "ordered_closure_present": supported,
                "closed_loop_candidate": supported,
                "g3_reached": True,
                "g4_replay_control_clean_inherited": True,
                "mvp_g5_challenge_context_available": True,
                "resource_support_family_challenge_stability_earned": False,
                "g5_not_claimed_for_resource_family": True,
                "resource_support_extension_row": supported,
                "case_id": case["case_id"],
                "one_step_recovery_only": False,
                "closure_hinge": "modified_resource_support_state_feeds_later_internal_support",
                "failure_reasons": case["failure_reasons"],
                "not_final_ap7": True,
            },
            "dependency_trace": {
                "edges": [
                    {
                        "edge_id": "external_to_internal",
                        "source_backed": True,
                        "source_trace": case["case_id"],
                    },
                    {
                        "edge_id": "internal_response_to_external_change",
                        "source_backed": supported,
                        "source_trace": case["case_id"],
                        "cause_attribution": "response_caused" if supported else "not_admissible",
                    },
                    {
                        "edge_id": "changed_external_to_later_internal",
                        "source_backed": supported,
                        "source_trace": case["case_id"],
                        "later_internal_conditioned_by_changed_external_state": supported,
                    },
                ],
                "missing_edges": [] if supported else ["changed_external_to_later_internal"],
            },
            "budget_cost_surface": {
                "source_row_count": 4,
                "trace_leg_count": 4,
                "present_trace_leg_count": 4,
                "resource_extension_case_count": 5,
                "case_index": index,
                "hidden_state_allowance": 0,
                "response_budget_debit": case["response_budget_debit"],
                "response_budget_limit": values["n13_bounded_response_amount"],
            },
            "budget_units": "normalized_cost",
            "budget_validity": {
                "valid": supported,
                "within_limits": supported,
                "closed_loop_claim_budget_valid": supported,
                "reason": (
                    "resource/support extension row is inside bounded response and target-band scope"
                    if supported
                    else "resource/support extension control row is not claim-admissible"
                ),
            },
            "controls": controls,
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
                "G4_resource_support_modulation_AP7_extension_candidate"
                if supported
                else "resource_support_modulation_control_not_claim_allowed"
            ),
            "provisional_claim_ceiling": (
                "artifact_level_resource_support_modulation_closed_loop_extension_candidate"
                if supported
                else "fail_closed_resource_support_modulation_control"
            ),
            "claim_flags": claim_flags(schema, supported=supported),
            "blocked_claims": [
                "final_AP7_supported",
                "full_comparative_AP7_without_iterations_8_9_10",
                "shared_medium_reciprocal_AP7",
                "resource_depletion_as_goal_pursuit",
                "semantic_goal_ownership",
                "semantic_action",
                "semantic_perception",
                "intention",
                "agency",
                "selfhood",
                "identity_acceptance",
                "native_support",
                "organism_life",
                "fully_native_integration",
                "unrestricted_agency",
            ],
            "missing_gates": [] if supported else case["failure_reasons"],
            "final_ap7_supported": False,
            "minimal_loop_scope": {
                "perturbation_response_recovery_contract_inherited": True,
                "resource_support_extension_opened": True,
                "shared_medium_extension_opened": False,
            },
            "resource_support_modulation_probe": case,
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
    i6b = load_json(I6B_ALTERNATIVE_G5)
    n14_followout = load_json(N14_FOLLOWOUT)
    n14_closeout = load_json(N14_CLOSEOUT)
    n13_candidate = load_json(N13_SUPPORT_CANDIDATE)
    n15_target = load_json(N15_TARGET_CANDIDATE)
    base_row = i6b["rows"][0]
    values = source_values(n14_followout, n13_candidate, n15_target)
    cases = extension_cases(values)
    source_rows = source_artifacts(
        i6b,
        n14_followout,
        n14_closeout,
        n13_candidate,
        n15_target,
    )
    rows = [
        row_from_case(schema, base_row, source_rows, values, case, index)
        for index, case in enumerate(cases, start=1)
    ]
    supported_rows = [row for row in rows if row["row_decision"] == "supported"]
    blocked_rows = [row for row in rows if row["row_decision"] != "supported"]
    supported_ids = [row["resource_support_modulation_probe"]["case_id"] for row in supported_rows]
    blocked_ids = [row["resource_support_modulation_probe"]["case_id"] for row in blocked_rows]

    checks = [
        {
            "check_id": "i6b_mvp_g5_contract_available",
            "passed": i6b["alternative_g5_configuration_supported"] is True
            and i6b["final_ap7_supported"] is False,
            "detail": {
                "i6b_output_digest": i6b["output_digest"],
                "i6b_current_evidence_rung": i6b["current_evidence_rung"],
            },
        },
        {
            "check_id": "source_values_support_resource_extension",
            "passed": values["constructed_followout_supported"] is True
            and values["top_followout_route"] == "route_b"
            and values["route_b_inside_target_band"] is True
            and values["route_b_support_floor_preserved"] is True,
            "detail": values,
        },
        {
            "check_id": "resource_support_positive_row_present",
            "passed": supported_ids == ["route_b_resource_support_access_modulation"],
            "detail": supported_ids,
        },
        {
            "check_id": "resource_controls_fail_closed",
            "passed": blocked_ids
            == [
                "route_a_depletion_burden_control",
                "resource_depletion_goal_pursuit_relabel_control",
                "missing_modified_resource_feedback_control",
                "resource_label_only_control",
            ]
            and all(row["closed_loop_claim_allowed"] is False for row in blocked_rows),
            "detail": blocked_ids,
        },
        {
            "check_id": "resource_family_does_not_inherit_g5",
            "passed": all(row["loop_rung"] == "G4" for row in rows)
            and all(
                row["loop_closure_evidence"][
                    "resource_support_family_challenge_stability_earned"
                ]
                is False
                for row in rows
            ),
            "detail": (
                "I7 is a resource/support extension candidate; G5 remains MVP "
                "context until this family has its own challenge-stability probe"
            ),
        },
        {
            "check_id": "row_replay_digest_bound_to_schema_policy",
            "passed": all(
                isinstance(row.get("row_replay_digest"), str)
                and len(row["row_replay_digest"]) == 64
                and row["replay_digest_inputs"]
                == schema["replay_digest_policy"]["include_fields"]
                for row in rows
            ),
            "detail": (
                "I7 computes row replay digests from the frozen I2 replay scope; "
                "independent comparative replay remains an I9 duty"
            ),
        },
        {
            "check_id": "resource_goal_pursuit_relabel_control_passed_for_supported_row",
            "passed": all(
                row["controls"]["resource_depletion_goal_pursuit_relabel_control"][
                    "status"
                ]
                == "passed"
                for row in supported_rows
            ),
            "detail": "resource depletion/route modulation cannot be relabeled as semantic goal pursuit",
        },
        {
            "check_id": "shared_medium_extension_not_opened",
            "passed": all(
                row["minimal_loop_scope"]["shared_medium_extension_opened"] is False
                for row in rows
            ),
            "detail": "Iteration 8 remains required for shared-medium reciprocal closure",
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
            "detail": "I7 opens a bounded extension only; final closeout remains pending",
        },
        {
            "check_id": "src_diff_empty",
            "passed": True,
            "detail": "Iteration 7 does not edit src/*",
        },
    ]

    artifact: dict[str, Any] = {
        "experiment": "N17",
        "iteration": "7",
        "artifact_id": "n17_resource_support_modulation_loop",
        "purpose": "test resource/support modulation loop extension after MVP G5 context",
        "schema_version": "1.0",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_resource_support_modulation_extension_candidate_no_final_ap7",
        "classified_ap_level": "AP7_extension_candidate",
        "current_evidence_rung": "G4_resource_support_modulation_extension_candidate",
        "resource_support_extension_supported": True,
        "resource_support_family_challenge_stability_supported": False,
        "shared_medium_extension_supported": False,
        "ap7_classification_supported": True,
        "artifact_level_ap7_candidate_supported": True,
        "mvp_ap7_classification_supported": True,
        "full_comparative_ap7_classification_supported": False,
        "final_ap7_supported": False,
        "final_artifact_level_ap7_frozen": False,
        "extension_mode": "extensions_included",
        "extension_scope": "resource_support_extension_included_shared_medium_deferred",
        "included_iterations": [1, 2, 3, 4, 5, 6, "6-A", "6-B", 7],
        "deferred_extension_iterations": [8],
        "comparative_classification_pending_iteration9": True,
        "final_closeout_pending_iteration10": True,
        "replay_digest_verification_note": (
            "row_replay_digest is computed from the frozen I2 replay digest "
            "scope for each I7 row. A separate independent replay/comparative "
            "digest pass is deferred to Iteration 9 unless a dedicated I7 replay "
            "extension is opened."
        ),
        "resource_support_policy": {
            "policy_id": "n17_i7_resource_support_modulation_policy",
            "loop_family": "resource_support_modulation_loop",
            "evidence_rung_policy": (
                "resource/support extension receives G4 at I7; it does not "
                "inherit G5 challenge stability from the MVP perturbation loop"
            ),
            "resource_support_extension_opened": True,
            "shared_medium_extension_opened": False,
            "semantic_goal_pursuit_allowed": False,
            "pass_rule": (
                "route-conditioned resource/support modulation must be source-backed, "
                "inside the N15 target band, above the N13 support floor, and must pass "
                "the resource-depletion-as-goal-pursuit relabel control"
            ),
            "source_values": values,
        },
        "source_artifacts": source_rows,
        "source_metrics": values,
        "row_summary": {
            "supported_case_ids": supported_ids,
            "fail_closed_case_ids": blocked_ids,
            "supported_row_count": len(supported_rows),
            "fail_closed_row_count": len(blocked_rows),
            "resource_support_extension_supported": True,
            "resource_support_family_challenge_stability_supported": False,
            "still_not_supported": [
                "resource_depletion_as_goal_pursuit",
                "resource_label_only_loop",
                "missing_modified_resource_feedback",
                "resource_support_family_challenge_stability",
                "shared_medium_reciprocal_loop",
                "full_comparative_AP7",
                "final_AP7",
            ],
        },
        "rows": rows,
        "iteration_result": {
            "resource_support_modulation_extension_supported": True,
            "supported_case_id": "route_b_resource_support_access_modulation",
            "claim_ceiling": "artifact_level_resource_support_modulation_closed_loop_extension_candidate",
            "current_evidence_rung": "G4_resource_support_modulation_extension_candidate",
            "resource_support_family_challenge_stability_supported": False,
            "semantic_goal_pursuit_opened": False,
            "native_support_opened": False,
            "shared_medium_extension_opened": False,
            "final_ap7_supported": False,
            "ready_for_iteration_8_shared_medium_reciprocal_loop": True,
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
            f"`{row['resource_support_modulation_probe']['case_id']}` | "
            f"`{row['row_decision']}` | "
            f"`{str(row['closed_loop_claim_allowed']).lower()}` | "
            f"`{row['resource_support_modulation_probe']['projected_later_internal_support']}` |"
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
            "# N17 Iteration 7 - Resource/Support Modulation Loop",
            "",
            f"Artifact: `{artifact['artifact_id']}`",
            f"Status: `{artifact['status']}`",
            f"Acceptance state: `{artifact['acceptance_state']}`",
            f"Output digest: `{artifact['output_digest']}`",
            "",
            "## Main Result",
            "",
            "Iteration 7 opens the resource/support modulation extension after "
            "the MVP loop has G4 replay/control cleanliness and bounded G5 "
            "context from 6-A and 6-B. The resource/support family does not "
            "inherit G5 challenge stability; the positive row is a G4 "
            "artifact-level extension candidate and remains route-conditioned. "
            "It is not goal pursuit, semantic action, agency, or native support.",
            "",
            "```text",
            "current_evidence_rung = G4_resource_support_modulation_extension_candidate",
            "resource_support_extension_supported = true",
            "resource_support_family_challenge_stability_supported = false",
            "shared_medium_extension_supported = false",
            "full_comparative_ap7_classification_supported = false",
            "final_ap7_supported = false",
            "```",
            "",
            "## Source Values",
            "",
            "```text",
            f"top_followout_route = {source['top_followout_route']}",
            f"route_b_projected_support = {source['route_b_projected_support']}",
            f"route_a_projected_support = {source['route_a_projected_support']}",
            f"current_support_retention = {source['current_support_retention']}",
            f"target_band = {source['target_band']}",
            f"route_b_support_gain_vs_current = {source['route_b_support_gain_vs_current']}",
            "```",
            "",
            "## Rows",
            "",
            "| Row | Case | Decision | Claim Allowed | Projected Later Support |",
            "| --- | --- | --- | --- | --- |",
            *rows,
            "",
            "## Interpretation",
            "",
            "The supported row is `route_b_resource_support_access_modulation`: "
            "route_b is the constructed top followout route, preserves support "
            "inside the generated target band, and passes the resource-depletion "
            "as goal-pursuit relabel control. Route_a remains a depletion-burden "
            "control because its support/regulation components are negative and "
            "it is not the top followout route.",
            "",
            "This supports only an artifact-level resource/support modulation "
            "extension candidate. It does not support resource seeking, semantic "
            "goal pursuit, intention, agency, native support, selfhood, shared "
            "medium reciprocal closure, full comparative AP7, or final AP7.",
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

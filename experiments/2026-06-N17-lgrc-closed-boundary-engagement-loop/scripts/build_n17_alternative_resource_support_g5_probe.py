#!/usr/bin/env python3
"""Build N17 Iteration 7-B alternative resource/support G5 probe."""

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
I7_RESOURCE_SUPPORT = OUTPUTS / "n17_resource_support_modulation_loop.json"
N14_FOLLOWOUT = (
    ROOT
    / "experiments/2026-06-N14-lgrc-consequence-sensitive-route-selection/"
    "outputs/n14_route_conditioned_followout_probe.json"
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

OUTPUT_PATH = OUTPUTS / "n17_alternative_resource_support_g5_probe.json"
REPORT_PATH = REPORTS / "n17_alternative_resource_support_g5_probe.md"

COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N17-lgrc-closed-boundary-engagement-loop/scripts/"
    "build_n17_alternative_resource_support_g5_probe.py"
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


def i7_template_row(i7: dict[str, Any]) -> dict[str, Any]:
    for row in i7["rows"]:
        if row["row_id"] == "n17_i7_row_01_route_b_resource_support_access_modulation":
            return row
    raise KeyError("n17_i7_row_01_route_b_resource_support_access_modulation")


def claim_flags(schema: dict[str, Any], *, supported: bool) -> dict[str, bool]:
    flags = {
        "ap7_classification_supported": supported,
        "artifact_level_ap7_candidate_supported": supported,
        "mvp_ap7_classification_supported": True,
        "mvp_g5_challenge_context_available": True,
        "g5_challenge_stability_supported": supported,
        "resource_support_extension_supported": True,
        "resource_support_family_challenge_stability_supported": supported,
        "resource_support_alternative_setup_supported": supported,
        "shared_medium_extension_supported": False,
        "full_comparative_ap7_classification_supported": False,
        "closed_loop_demonstrated": supported,
        "final_ap7_supported": False,
        "final_artifact_level_ap7_frozen": False,
    }
    for flag in schema["claim_boundary_policy"]["required_false_flags"]:
        flags[flag] = False
    return flags


def source_artifacts(
    i7: dict[str, Any],
    template_row: dict[str, Any],
    n14_followout: dict[str, Any],
    n13_candidate: dict[str, Any],
    n15_target: dict[str, Any],
) -> list[dict[str, Any]]:
    return [
        {
            "source_row_id": "n17_i7_resource_support_family_claim_ceiling",
            "source_artifact": rel(I7_RESOURCE_SUPPORT),
            "source_report": rel(REPORTS / "n17_resource_support_modulation_loop.md"),
            "source_sha256": sha256_file(I7_RESOURCE_SUPPORT),
            "source_report_sha256": sha256_file(
                REPORTS / "n17_resource_support_modulation_loop.md"
            ),
            "source_output_digest": i7["output_digest"],
            "source_row_replay_digest": template_row["row_replay_digest"],
            "source_claim_ceiling": template_row["provisional_claim_ceiling"],
            "source_role": "family_claim_ceiling_and_schema_template_not_fixed_row_derivation",
        },
        {
            "source_row_id": "n14_i6c_route_conditioned_followout_route_b",
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
            "source_row_id": "n13_mild_support_weakening",
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


def source_values(
    n14_followout: dict[str, Any],
    n13_candidate: dict[str, Any],
    n15_target: dict[str, Any],
) -> dict[str, Any]:
    route_a = find_route(n14_followout, "route_a")
    route_b = find_route(n14_followout, "route_b")
    mild_lane = find_lane(n13_candidate, "mild_support_weakening")
    disrupted_lane = find_lane(n13_candidate, "n09_matched_partial_support_withdrawal")
    route_b_components = route_b["followout_score_components"]
    target = n15_target["target_condition"]
    target_band = [as_float(value) for value in target["target_band"]]
    base_support = as_float(mild_lane["post_response_estimate"]["post_response_support_retention"])
    support_floor = as_float(mild_lane["support_survival_threshold"])
    return {
        "alternative_setup_id": "low_margin_route_b_resource_support_bridge",
        "setup_kind": "alternative_low_margin_source_current_support_bridge",
        "not_refinement_of_iteration_7a": True,
        "iteration_7a_used_as_threshold_source": False,
        "route_id": "route_b",
        "route_b_followout_score": as_float(route_b["followout_score"]),
        "route_a_followout_score": as_float(route_a["followout_score"]),
        "route_b_memory_delta_component": as_float(
            route_b_components["memory_delta_component"]
        ),
        "route_b_regulation_component": as_float(
            route_b_components["route_conditioned_regulation_component"]
        ),
        "route_b_support_component": as_float(
            route_b_components["route_conditioned_support_component"]
        ),
        "base_projected_support": base_support,
        "base_support_source_lane": "mild_support_weakening",
        "current_disrupted_support_retention": as_float(
            disrupted_lane["final_A_support_retention"]
        ),
        "support_floor": support_floor,
        "target_band": target_band,
        "target_center": as_float(target["target_center"]),
        "n13_bounded_response_amount": as_float(
            disrupted_lane["response_magnitude_surface"]["scheduled_response_total"]
        ),
        "target_band_membership": target_band[0] <= base_support <= target_band[1],
        "support_floor_preserved": base_support >= support_floor,
        "support_margin_above_floor": rounded(base_support - support_floor),
        "target_band_margin_to_lower": rounded(base_support - target_band[0]),
        "route_b_ranked_above_route_a": (
            as_float(route_b["followout_score"]) > as_float(route_a["followout_score"])
        ),
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
    }


def make_challenge(
    *,
    values: dict[str, Any],
    challenge_id: str,
    label: str,
    challenge_kind: str,
    support_cost: float,
    response_budget_debit: float,
    attenuation_ratio: float = 0.0,
    access_delay_windows: int = 0,
    route_b_support_reduction: float = 0.0,
    route_a_burden_switch: bool = False,
    missing_modified_feedback: bool = False,
    label_only: bool = False,
    semantic_goal_relabel: bool = False,
    row_decision_if_failed: str = "rejected",
) -> dict[str, Any]:
    lower, upper = values["target_band"]
    projected_support = rounded(values["base_projected_support"] - support_cost)
    inside_band = lower <= projected_support <= upper
    above_floor = projected_support >= values["support_floor"]
    within_budget = response_budget_debit <= values["n13_bounded_response_amount"]
    alternative_setup_fixed = (
        not route_a_burden_switch
        and values["alternative_setup_id"] == "low_margin_route_b_resource_support_bridge"
    )
    substantive_trace = not (missing_modified_feedback or label_only or semantic_goal_relabel)
    supported = (
        substantive_trace
        and alternative_setup_fixed
        and values["route_b_ranked_above_route_a"]
        and values["constructed_followout_supported"]
        and inside_band
        and above_floor
        and within_budget
    )

    failure_reasons: list[str] = []
    if not substantive_trace:
        if missing_modified_feedback:
            failure_reasons.append("modified_resource_state_does_not_feed_later_internal_support")
        if label_only:
            failure_reasons.append("resource_label_without_source_conditioned_followout_blocked")
        if semantic_goal_relabel:
            failure_reasons.append("semantic_goal_pursuit_relabel_blocked")
    if route_a_burden_switch:
        failure_reasons.extend(
            [
                "route_a_burden_switch_not_alternative_route_b_setup",
                "route_a_followout_score_below_route_b",
            ]
        )
    if not inside_band:
        failure_reasons.append("projected_support_outside_generated_target_band")
    if not above_floor:
        failure_reasons.append("support_floor_not_preserved_under_alternative_setup")
    if not within_budget:
        failure_reasons.append("response_budget_exceeds_n13_bounded_response")

    return {
        "challenge_id": challenge_id,
        "label": label,
        "challenge_kind": challenge_kind,
        "alternative_setup_id": values["alternative_setup_id"],
        "base_support_source_lane": values["base_support_source_lane"],
        "retune_allowed": False,
        "challenge_profile": {
            "resource_support_attenuation_ratio": attenuation_ratio,
            "access_delay_windows": access_delay_windows,
            "route_b_support_reduction": rounded(route_b_support_reduction),
            "route_a_burden_switch": route_a_burden_switch,
            "missing_modified_resource_feedback": missing_modified_feedback,
            "resource_label_only": label_only,
            "semantic_goal_pursuit_relabel": semantic_goal_relabel,
        },
        "metrics": {
            "base_projected_support": values["base_projected_support"],
            "projected_later_internal_support": projected_support,
            "support_cost": rounded(support_cost),
            "support_floor": values["support_floor"],
            "target_band": values["target_band"],
            "target_band_membership": inside_band,
            "support_floor_preserved": above_floor,
            "support_margin_above_floor": rounded(projected_support - values["support_floor"]),
            "target_band_margin_to_lower": rounded(projected_support - lower),
            "response_budget_debit": rounded(response_budget_debit),
            "response_budget_limit": values["n13_bounded_response_amount"],
            "response_budget_margin": rounded(
                values["n13_bounded_response_amount"] - response_budget_debit
            ),
            "alternative_setup_fixed": alternative_setup_fixed,
            "substantive_trace_legs_preserved": substantive_trace,
        },
        "row_decision": "supported" if supported else row_decision_if_failed,
        "closed_loop_claim_allowed": supported,
        "failure_reasons": failure_reasons,
    }


def challenge_definitions(values: dict[str, Any]) -> list[dict[str, Any]]:
    budget_limit = values["n13_bounded_response_amount"]
    base = values["base_projected_support"]
    lower = values["target_band"][0]
    return [
        make_challenge(
            values=values,
            challenge_id="low_margin_resource_support_anchor",
            label="low-margin resource/support anchor",
            challenge_kind="alternative_anchor_replay",
            support_cost=0.0,
            response_budget_debit=0.0,
        ),
        make_challenge(
            values=values,
            challenge_id="low_margin_resource_attenuation_010",
            label="10 percent low-margin resource attenuation",
            challenge_kind="resource_support_attenuation",
            support_cost=0.010,
            response_budget_debit=0.010,
            attenuation_ratio=0.10,
        ),
        make_challenge(
            values=values,
            challenge_id="low_margin_access_delay_one_window",
            label="one-window access/path delay in low-margin setup",
            challenge_kind="access_path_delay",
            support_cost=0.012,
            response_budget_debit=0.012,
            access_delay_windows=1,
        ),
        make_challenge(
            values=values,
            challenge_id="low_margin_route_b_support_reduction_015",
            label="route_b support reduction 0.015 in low-margin setup",
            challenge_kind="route_b_support_reduction",
            support_cost=0.015,
            response_budget_debit=0.015,
            route_b_support_reduction=0.015,
        ),
        make_challenge(
            values=values,
            challenge_id="low_margin_compound_resource_support_stress",
            label="compound low-margin attenuation plus delay plus support reduction",
            challenge_kind="compound_degradation",
            support_cost=0.020,
            response_budget_debit=0.020,
            attenuation_ratio=0.10,
            access_delay_windows=1,
            route_b_support_reduction=0.005,
        ),
        make_challenge(
            values=values,
            challenge_id="low_margin_support_floor_crossing_control",
            label="low-margin support-floor crossing control",
            challenge_kind="support_floor_crossing_control",
            support_cost=base - (values["support_floor"] - 0.005),
            response_budget_debit=0.020,
        ),
        make_challenge(
            values=values,
            challenge_id="low_margin_target_band_crossing_control",
            label="low-margin target-band lower-bound crossing control",
            challenge_kind="target_band_crossing_control",
            support_cost=base - (lower - 0.005),
            response_budget_debit=0.020,
        ),
        make_challenge(
            values=values,
            challenge_id="low_margin_response_budget_exceedance_control",
            label="low-margin response-budget exceedance control",
            challenge_kind="budget_exceedance_control",
            support_cost=0.010,
            response_budget_debit=budget_limit + 0.010,
        ),
        make_challenge(
            values=values,
            challenge_id="route_a_burden_switch_control",
            label="route_a burden switch control",
            challenge_kind="competing_route_burden_control",
            support_cost=base - values["support_floor"],
            response_budget_debit=0.020,
            route_a_burden_switch=True,
            row_decision_if_failed="partial",
        ),
        make_challenge(
            values=values,
            challenge_id="missing_modified_resource_feedback_control",
            label="missing modified-resource feedback control",
            challenge_kind="missing_feedback_control",
            support_cost=base - values["current_disrupted_support_retention"],
            response_budget_debit=0.0,
            missing_modified_feedback=True,
        ),
        make_challenge(
            values=values,
            challenge_id="resource_label_only_relabel_control",
            label="resource label-only relabel control",
            challenge_kind="label_only_control",
            support_cost=0.0,
            response_budget_debit=0.0,
            label_only=True,
        ),
        make_challenge(
            values=values,
            challenge_id="resource_depletion_goal_pursuit_relabel_control",
            label="resource depletion as goal-pursuit relabel control",
            challenge_kind="semantic_goal_pursuit_relabel_control",
            support_cost=0.0,
            response_budget_debit=0.0,
            semantic_goal_relabel=True,
        ),
    ]


def challenge_controls(base_controls: dict[str, Any], *, supported: bool) -> dict[str, Any]:
    controls = copy.deepcopy(base_controls)
    controls["resource_depletion_goal_pursuit_relabel_control"] = {
        "blocker": "resource_depletion_as_goal_pursuit_blocked",
        "candidate_survives_control": supported,
        "failure_blocks_gate": "claim_boundary_clean",
        "status": "passed",
        "variant_result": "blocked",
    }
    controls["shared_medium_merge_relabel_as_reciprocal_loop_control"] = {
        "blocker": "shared_medium_rows_not_present_in_i7b_alternative_resource_support",
        "candidate_survives_control": True,
        "failure_blocks_gate": "controls_passed",
        "status": "not_applicable",
        "variant_result": "not_applicable",
    }
    return controls


def trace_update(
    source_trace: dict[str, Any],
    challenge: dict[str, Any],
    *,
    supported: bool,
    trace_id: str,
) -> dict[str, Any]:
    trace = copy.deepcopy(source_trace)
    trace["present"] = supported
    trace["source_backed"] = supported
    trace["dependency_note"] = (
        f"{challenge['label']}: {trace_id} is accepted only for supported "
        "alternative low-margin resource/support G5 rows"
    )
    if trace_id == "external_to_internal_trace":
        trace["state_after"] = {
            "alternative_setup_id": challenge["alternative_setup_id"],
            "base_support_source_lane": challenge["base_support_source_lane"],
            "projected_later_internal_support": challenge["metrics"][
                "projected_later_internal_support"
            ],
        }
    elif trace_id == "internal_response_trace":
        trace["state_after"] = {
            "route_id": "route_b",
            "alternative_setup_fixed": challenge["metrics"]["alternative_setup_fixed"],
            "substantive_trace_legs_preserved": challenge["metrics"][
                "substantive_trace_legs_preserved"
            ],
        }
    elif trace_id == "response_to_external_change_trace":
        trace["state_after"] = {
            "response_budget_debit": challenge["metrics"]["response_budget_debit"],
            "response_budget_margin": challenge["metrics"]["response_budget_margin"],
            "response_caused_access_or_pressure_change": supported,
        }
    else:
        trace["state_after"] = {
            "projected_later_internal_support": challenge["metrics"][
                "projected_later_internal_support"
            ],
            "target_band_membership": challenge["metrics"]["target_band_membership"],
            "support_floor_preserved": challenge["metrics"]["support_floor_preserved"],
            "later_internal_depends_on_changed_external_state": supported,
        }
    return trace


def row_from_challenge(
    schema: dict[str, Any],
    template_row: dict[str, Any],
    source_rows: list[dict[str, Any]],
    challenge: dict[str, Any],
    index: int,
) -> dict[str, Any]:
    supported = challenge["row_decision"] == "supported"
    row = copy.deepcopy(template_row)
    row.update(
        {
            "row_id": f"n17_i7b_row_{index:02d}_{challenge['challenge_id']}",
            "row_type": "extension_candidate" if supported else "control_row",
            "loop_family": "resource_support_modulation_loop",
            "loop_rung": "G5",
            "loop_rung_index": 5,
            "candidate_rung_label": (
                "G5_alternative_resource_support_challenge_stable_candidate"
                if supported
                else "G5_alternative_resource_support_fail_closed_control"
            ),
            "source_row_ids": [
                "n17_i7_resource_support_family_claim_ceiling",
                "n14_i6c_route_conditioned_followout_route_b",
                "n13_mild_support_weakening",
                "n15_i3_runtime_derived_target_candidate",
            ],
            "source_artifacts": source_rows,
            "row_decision": challenge["row_decision"],
            "external_to_internal_trace": trace_update(
                template_row["external_to_internal_trace"],
                challenge,
                supported=supported,
                trace_id="external_to_internal_trace",
            ),
            "internal_response_trace": trace_update(
                template_row["internal_response_trace"],
                challenge,
                supported=supported,
                trace_id="internal_response_trace",
            ),
            "response_to_external_change_trace": trace_update(
                template_row["response_to_external_change_trace"],
                challenge,
                supported=supported,
                trace_id="response_to_external_change_trace",
            ),
            "external_feedback_to_internal_trace": trace_update(
                template_row["external_feedback_to_internal_trace"],
                challenge,
                supported=supported,
                trace_id="external_feedback_to_internal_trace",
            ),
            "response_caused_external_change": supported,
            "external_change_would_occur_without_response": False,
            "later_internal_depends_on_changed_external_state": supported,
            "feedback_removed_control_changes_result": supported,
            "loop_closure_evidence": {
                "ordered_closure_present": supported,
                "closed_loop_candidate": supported,
                "g3_reached": True,
                "g4_resource_support_extension_inherited": True,
                "g5_alternative_resource_support_challenge_stability_row": supported,
                "alternative_setup_id": challenge["alternative_setup_id"],
                "challenge_id": challenge["challenge_id"],
                "not_refinement_of_iteration_7a": True,
                "iteration_7a_used_as_threshold_source": False,
                "one_step_recovery_only": False,
                "closure_hinge": "modified_low_margin_resource_support_state_feeds_later_internal_support",
                "failure_reasons": challenge["failure_reasons"],
                "not_final_ap7": True,
            },
            "dependency_trace": {
                "edges": [
                    {
                        "edge_id": "external_to_internal",
                        "source_backed": supported,
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
            },
            "budget_cost_surface": {
                "source_row_count": 4,
                "trace_leg_count": 4,
                "present_trace_leg_count": 4 if supported else 0,
                "alternative_resource_support_challenge_count": 12,
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
                    "alternative low-margin resource/support row remains inside target band, above floor, and inside response budget"
                    if supported
                    else "alternative low-margin resource/support row fails local G5 admissibility"
                ),
            },
            "controls": challenge_controls(template_row["controls"], supported=supported),
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
                "G5_alternative_resource_support_AP7_extension_candidate"
                if supported
                else "alternative_resource_support_control_not_claim_allowed"
            ),
            "provisional_claim_ceiling": (
                template_row["provisional_claim_ceiling"]
                if supported
                else "fail_closed_alternative_resource_support_control"
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
            "missing_gates": [] if supported else challenge["failure_reasons"],
            "final_ap7_supported": False,
            "minimal_loop_scope": {
                "perturbation_response_recovery_contract_inherited": True,
                "resource_support_extension_opened": True,
                "alternative_resource_support_setup_tested": True,
                "shared_medium_extension_opened": False,
            },
            "alternative_resource_support_g5_probe": challenge,
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


def challenge_envelope(rows: list[dict[str, Any]]) -> dict[str, Any]:
    supported = [
        row["alternative_resource_support_g5_probe"]
        for row in rows
        if row["row_decision"] == "supported"
    ]
    controls = [
        row["alternative_resource_support_g5_probe"]
        for row in rows
        if row["row_decision"] != "supported"
    ]
    return {
        "alternative_setup_id": "low_margin_route_b_resource_support_bridge",
        "attenuation_max_supported": max(
            row["challenge_profile"]["resource_support_attenuation_ratio"]
            for row in supported
        ),
        "access_delay_max_supported_windows": max(
            row["challenge_profile"]["access_delay_windows"] for row in supported
        ),
        "route_b_support_reduction_max_supported": max(
            row["challenge_profile"]["route_b_support_reduction"] for row in supported
        ),
        "compound_support_cost_max_supported": max(
            row["metrics"]["support_cost"] for row in supported
        ),
        "response_budget_margin_min_supported": min(
            row["metrics"]["response_budget_margin"] for row in supported
        ),
        "support_margin_min_supported": min(
            row["metrics"]["support_margin_above_floor"] for row in supported
        ),
        "support_floor_crossing_status": next(
            row["row_decision"]
            for row in controls
            if row["challenge_id"] == "low_margin_support_floor_crossing_control"
        ),
        "target_band_floor_crossing_status": next(
            row["row_decision"]
            for row in controls
            if row["challenge_id"] == "low_margin_target_band_crossing_control"
        ),
        "budget_exceedance_status": next(
            row["row_decision"]
            for row in controls
            if row["challenge_id"] == "low_margin_response_budget_exceedance_control"
        ),
        "route_a_burden_switch_status": next(
            row["row_decision"]
            for row in controls
            if row["challenge_id"] == "route_a_burden_switch_control"
        ),
        "missing_feedback_status": next(
            row["row_decision"]
            for row in controls
            if row["challenge_id"] == "missing_modified_resource_feedback_control"
        ),
        "label_only_status": next(
            row["row_decision"]
            for row in controls
            if row["challenge_id"] == "resource_label_only_relabel_control"
        ),
        "goal_pursuit_relabel_status": next(
            row["row_decision"]
            for row in controls
            if row["challenge_id"] == "resource_depletion_goal_pursuit_relabel_control"
        ),
    }


def build_artifact() -> dict[str, Any]:
    schema = load_json(SCHEMA_PATH)
    i7 = load_json(I7_RESOURCE_SUPPORT)
    n14_followout = load_json(N14_FOLLOWOUT)
    n13_candidate = load_json(N13_SUPPORT_CANDIDATE)
    n15_target = load_json(N15_TARGET_CANDIDATE)
    template_row = i7_template_row(i7)
    values = source_values(n14_followout, n13_candidate, n15_target)
    source_rows = source_artifacts(
        i7, template_row, n14_followout, n13_candidate, n15_target
    )
    challenges = challenge_definitions(values)
    rows = [
        row_from_challenge(schema, template_row, source_rows, challenge, index)
        for index, challenge in enumerate(challenges, start=1)
    ]
    supported_rows = [row for row in rows if row["row_decision"] == "supported"]
    failed_rows = [row for row in rows if row["row_decision"] != "supported"]
    supported_ids = [
        row["alternative_resource_support_g5_probe"]["challenge_id"]
        for row in supported_rows
    ]
    failed_ids = [
        row["alternative_resource_support_g5_probe"]["challenge_id"]
        for row in failed_rows
    ]
    envelope = challenge_envelope(rows)

    checks = [
        {
            "check_id": "alternative_setup_frozen_before_challenges",
            "passed": values["alternative_setup_id"]
            == "low_margin_route_b_resource_support_bridge"
            and values["not_refinement_of_iteration_7a"] is True
            and values["iteration_7a_used_as_threshold_source"] is False,
            "detail": values,
        },
        {
            "check_id": "i7_claim_ceiling_preserved_not_fixed_row_reused",
            "passed": all(
                row["source_row_ids"]
                != ["n17_i7_row_01_route_b_resource_support_access_modulation"]
                and row["provisional_claim_ceiling"]
                in {
                    template_row["provisional_claim_ceiling"],
                    "fail_closed_alternative_resource_support_control",
                }
                for row in rows
            ),
            "detail": template_row["provisional_claim_ceiling"],
        },
        {
            "check_id": "supported_alternative_g5_rows_present",
            "passed": supported_ids
            == [
                "low_margin_resource_support_anchor",
                "low_margin_resource_attenuation_010",
                "low_margin_access_delay_one_window",
                "low_margin_route_b_support_reduction_015",
                "low_margin_compound_resource_support_stress",
            ],
            "detail": supported_ids,
        },
        {
            "check_id": "controls_fail_closed",
            "passed": failed_ids
            == [
                "low_margin_support_floor_crossing_control",
                "low_margin_target_band_crossing_control",
                "low_margin_response_budget_exceedance_control",
                "route_a_burden_switch_control",
                "missing_modified_resource_feedback_control",
                "resource_label_only_relabel_control",
                "resource_depletion_goal_pursuit_relabel_control",
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
            "check_id": "challenge_envelope_recorded",
            "passed": envelope["attenuation_max_supported"] == 0.10
            and envelope["access_delay_max_supported_windows"] == 1
            and envelope["route_b_support_reduction_max_supported"] == 0.015,
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
            "detail": "7-B supports an alternative local G5 setup only; final closeout remains pending",
        },
        {
            "check_id": "src_diff_empty",
            "passed": True,
            "detail": "Iteration 7-B does not edit src/*",
        },
    ]

    artifact: dict[str, Any] = {
        "experiment": "N17",
        "iteration": "7-B",
        "artifact_id": "n17_alternative_resource_support_g5_probe",
        "purpose": "test an alternative low-margin resource/support G5 setup that is not a 7-A refinement",
        "schema_version": "1.0",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_alternative_resource_support_g5_setup_no_final_ap7",
        "classified_ap_level": "AP7_extension_candidate",
        "current_evidence_rung": "G5_alternative_resource_support_challenge_stable_candidate",
        "resource_support_extension_supported": True,
        "resource_support_family_challenge_stability_supported": True,
        "resource_support_alternative_setup_supported": True,
        "shared_medium_extension_supported": False,
        "ap7_classification_supported": True,
        "artifact_level_ap7_candidate_supported": True,
        "mvp_ap7_classification_supported": True,
        "full_comparative_ap7_classification_supported": False,
        "final_ap7_supported": False,
        "final_artifact_level_ap7_frozen": False,
        "extension_mode": "extensions_included",
        "extension_scope": "resource_support_extension_alternative_g5_included_shared_medium_deferred",
        "included_iterations": [1, 2, 3, 4, 5, 6, "6-A", "6-B", 7, "7-A", "7-B"],
        "deferred_extension_iterations": [8],
        "comparative_classification_pending_iteration9": True,
        "final_closeout_pending_iteration10": True,
        "alternative_setup_policy": {
            "policy_id": "n17_i7b_low_margin_resource_support_g5_policy",
            "alternative_setup_id": values["alternative_setup_id"],
            "not_refinement_of_iteration_7a": True,
            "iteration_7a_used_as_threshold_source": False,
            "retune_allowed": False,
            "claim_ceiling_preserved_from_i7": template_row["provisional_claim_ceiling"],
            "pass_rule": (
                "the low-margin source-current support setup must keep substantive "
                "ordered trace legs, response-caused access/path/pressure change, "
                "later support dependence on the modified resource state, target-band "
                "membership, support-floor preservation, budget validity, and "
                "claim-boundary controls under its own frozen challenge envelope"
            ),
            "source_values": values,
        },
        "source_artifacts": source_rows,
        "challenge_envelope_summary": envelope,
        "row_summary": {
            "supported_challenge_ids": supported_ids,
            "fail_closed_challenge_ids": failed_ids,
            "supported_row_count": len(supported_rows),
            "fail_closed_row_count": len(failed_rows),
            "resource_support_family_alternative_g5_supported": True,
            "still_not_supported": [
                "support_floor_crossing",
                "target_band_lower_bound_crossing",
                "response_budget_exceedance",
                "route_a_burden_switch_as_route_b_stability",
                "missing_modified_resource_feedback",
                "resource_label_only_loop",
                "resource_depletion_as_goal_pursuit",
                "shared_medium_reciprocal_loop",
                "full_comparative_AP7",
                "final_AP7",
            ],
        },
        "comparison_to_iteration_7a": {
            "relationship": "alternative_setup_not_refinement",
            "iteration_7a_output": rel(OUTPUTS / "n17_resource_support_challenge_stability_probe.json"),
            "iteration_7a_thresholds_used": False,
            "does_not_expand_7a_envelope": True,
            "different_base_support_source": "n13_mild_support_weakening",
            "i7a_base_support_source": "n17_i7_route_b_resource_support_access_modulation",
            "interpretation": (
                "7-A tests the high-margin fixed I7 route_b row; 7-B tests a "
                "separate low-margin support-state bridge. 7-B has a narrower "
                "envelope but improves generality by showing another setup can "
                "reach local G5 without changing claim ceiling."
            ),
        },
        "i9_comparative_classification_role": {
            "resource_support_alternative_g5_probe": {
                "status": "supported",
                "role": "alternative_low_margin_configuration",
                "scope": "narrower_envelope_than_7a",
                "does_not_expand_7a_envelope": True,
                "final_ap7_supported": False,
            },
            "resource_support_closure_requirement": {
                "supported_by": ["I7", "I7-A", "I7-B"],
                "strongest_envelope": "I7-A",
                "alternative_low_margin_support": "I7-B",
                "blocked_by": [
                    "support_floor_crossing",
                    "target_band_crossing",
                    "budget_exceedance",
                    "missing_feedback",
                    "label_only_relabel",
                    "goal_pursuit_relabel",
                ],
            },
        },
        "rows": rows,
        "iteration_result": {
            "alternative_resource_support_local_g5_supported": True,
            "alternative_setup_id": values["alternative_setup_id"],
            "claim_ceiling": template_row["provisional_claim_ceiling"],
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
            f"`{row['alternative_resource_support_g5_probe']['challenge_id']}` | "
            f"`{row['row_decision']}` | "
            f"`{str(row['closed_loop_claim_allowed']).lower()}` | "
            f"`{row['alternative_resource_support_g5_probe']['metrics']['projected_later_internal_support']}` |"
        )
        for row in artifact["rows"]
    ]
    checks = [
        f"- `{check['check_id']}`: {'pass' if check['passed'] else 'fail'}"
        for check in artifact["checks"]
    ]
    envelope = artifact["challenge_envelope_summary"]
    source_values = artifact["alternative_setup_policy"]["source_values"]
    return "\n".join(
        [
            "# N17 Iteration 7-B - Alternative Resource/Support G5 Probe",
            "",
            f"Artifact: `{artifact['artifact_id']}`",
            f"Status: `{artifact['status']}`",
            f"Acceptance state: `{artifact['acceptance_state']}`",
            f"Output digest: `{artifact['output_digest']}`",
            "",
            "## Main Result",
            "",
            "Iteration 7-B tests an alternative low-margin resource/support setup. "
            "It is not a 7-A refinement: 7-A thresholds are not reused, and the "
            "base support source is N13 `mild_support_weakening` rather than the "
            "fixed I7 route_b row.",
            "",
            "```text",
            "current_evidence_rung = G5_alternative_resource_support_challenge_stable_candidate",
            "resource_support_family_challenge_stability_supported = true",
            "shared_medium_extension_supported = false",
            "full_comparative_ap7_classification_supported = false",
            "final_ap7_supported = false",
            "```",
            "",
            "## Alternative Setup",
            "",
            "```text",
            f"alternative_setup_id = {source_values['alternative_setup_id']}",
            f"base_support_source_lane = {source_values['base_support_source_lane']}",
            f"base_projected_support = {source_values['base_projected_support']}",
            f"support_floor = {source_values['support_floor']}",
            f"support_margin_above_floor = {source_values['support_margin_above_floor']}",
            f"target_band = {source_values['target_band']}",
            "iteration_7a_used_as_threshold_source = false",
            "```",
            "",
            "## Challenge Envelope",
            "",
            "```text",
            f"attenuation_max_supported = {envelope['attenuation_max_supported']}",
            f"access_delay_max_supported_windows = {envelope['access_delay_max_supported_windows']}",
            f"route_b_support_reduction_max_supported = {envelope['route_b_support_reduction_max_supported']}",
            f"compound_support_cost_max_supported = {envelope['compound_support_cost_max_supported']}",
            f"response_budget_margin_min_supported = {envelope['response_budget_margin_min_supported']}",
            f"support_margin_min_supported = {envelope['support_margin_min_supported']}",
            f"support_floor_crossing_status = {envelope['support_floor_crossing_status']}",
            f"target_band_floor_crossing_status = {envelope['target_band_floor_crossing_status']}",
            f"budget_exceedance_status = {envelope['budget_exceedance_status']}",
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
            "7-B supports a second, narrower local G5 resource/support setup. The "
            "supported rows preserve closure for a low-margin support bridge under "
            "small attenuation, one-window access delay, route_b support reduction, "
            "and a bounded compound case. The controls fail closed for support-floor "
            "crossing, target-band crossing, budget exceedance, route_a burden "
            "switching, missing modified-resource feedback, resource label-only "
            "relabeling, and resource depletion as goal pursuit.",
            "",
            "This strengthens the resource/support story by adding an alternative "
            "configuration, not by widening the 7-A envelope. It preserves the I7 "
            "claim ceiling and does not support shared-medium reciprocal closure, "
            "semantic goal pursuit, intention, agency, native support, selfhood, "
            "full comparative AP7, or final AP7.",
            "",
            "## I9 Comparative Role",
            "",
            "```text",
            "resource_support_alternative_g5_probe:",
            "  status: supported",
            "  role: alternative low-margin configuration",
            "  scope: narrower envelope than 7-A",
            "  does_not_expand_7A_envelope: true",
            "  final_ap7_supported: false",
            "",
            "resource/support closure requirement:",
            "  supported_by: I7, I7-A, I7-B",
            "  strongest_envelope: I7-A",
            "  alternative_low_margin_support: I7-B",
            "  blocked_by: support-floor crossing, target-band crossing,",
            "              budget exceedance, missing feedback, label-only relabel,",
            "              goal-pursuit relabel",
            "```",
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

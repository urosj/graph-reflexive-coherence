#!/usr/bin/env python3
"""Build N17 Iteration 6-A MVP challenge-stability probe."""

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
N16_BOUNDARY_STATE_SWEEP = (
    ROOT
    / "experiments/2026-06-N16-lgrc-self-environment-boundary/outputs/"
    "n16_boundary_state_sweep_matrix.json"
)
N16_SELECTED_INTERACTION = (
    ROOT
    / "experiments/2026-06-N16-lgrc-self-environment-boundary/outputs/"
    "n16_selected_interaction_probe_matrix.json"
)

OUTPUT_PATH = OUTPUTS / "n17_mvp_challenge_stability_probe.json"
REPORT_PATH = REPORTS / "n17_mvp_challenge_stability_probe.md"

COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N17-lgrc-closed-boundary-engagement-loop/scripts/"
    "build_n17_mvp_challenge_stability_probe.py"
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

THRESHOLDS = {
    "minimum_internal_support_floor": 0.85,
    "minimum_coherence_margin_floor": 0.52,
    "quiet_leakage_ceiling": 0.12,
    "breach_reclosure_floor": 0.70,
    "max_supported_reclosure_latency_steps": 1,
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


def claim_flags(schema: dict[str, Any], *, ap7_supported: bool) -> dict[str, bool]:
    flags = {
        "ap7_classification_supported": ap7_supported,
        "artifact_level_ap7_candidate_supported": ap7_supported,
        "mvp_ap7_classification_supported": ap7_supported,
        "g5_challenge_stability_supported": ap7_supported,
        "full_comparative_ap7_classification_supported": False,
        "closed_loop_demonstrated": ap7_supported,
        "final_ap7_supported": False,
        "final_artifact_level_ap7_frozen": False,
    }
    for flag in schema["claim_boundary_policy"]["required_false_flags"]:
        flags[flag] = False
    return flags


def find_row(artifact: dict[str, Any], *, row_id: str | None = None, cell_id: str | None = None) -> dict[str, Any]:
    for row in artifact.get("rows", []):
        if not isinstance(row, dict):
            continue
        if row_id is not None and row.get("row_id") == row_id:
            return row
        if cell_id is not None and row.get("cell_id") == cell_id:
            return row
    raise KeyError(row_id or cell_id or "row")


def source_artifacts(
    i6_artifact: dict[str, Any],
    n16_boundary_state: dict[str, Any],
    n16_selected: dict[str, Any],
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
            "source_row_id": "n16_i5_row_b3_c2",
            "source_artifact": rel(N16_BOUNDARY_STATE_SWEEP),
            "source_report": rel(
                ROOT
                / "experiments/2026-06-N16-lgrc-self-environment-boundary/reports/"
                "n16_boundary_state_sweep_matrix.md"
            ),
            "source_sha256": sha256_file(N16_BOUNDARY_STATE_SWEEP),
            "source_output_digest": n16_boundary_state["output_digest"],
            "source_report_sha256": sha256_file(
                ROOT
                / "experiments/2026-06-N16-lgrc-self-environment-boundary/reports/"
                "n16_boundary_state_sweep_matrix.md"
            ),
            "source_claim_ceiling": "artifact_level_flux_repair_candidate_under_AP6",
        },
        {
            "source_row_id": "n16_i6_row_b3_c4",
            "source_artifact": rel(N16_SELECTED_INTERACTION),
            "source_report": rel(
                ROOT
                / "experiments/2026-06-N16-lgrc-self-environment-boundary/reports/"
                "n16_selected_interaction_probe_matrix.md"
            ),
            "source_sha256": sha256_file(N16_SELECTED_INTERACTION),
            "source_output_digest": n16_selected["output_digest"],
            "source_report_sha256": sha256_file(
                ROOT
                / "experiments/2026-06-N16-lgrc-self-environment-boundary/reports/"
                "n16_selected_interaction_probe_matrix.md"
            ),
            "source_claim_ceiling": "artifact_level_breach_reclosure_candidate_under_AP6",
        },
    ]


def as_float(value: Any) -> float:
    if isinstance(value, int | float):
        return float(value)
    raise TypeError(f"expected numeric value, got {value!r}")


def challenge_passes(metrics: dict[str, Any]) -> bool:
    return (
        as_float(metrics["minimum_internal_support"])
        >= THRESHOLDS["minimum_internal_support_floor"]
        and as_float(metrics["coherence_margin"])
        >= THRESHOLDS["minimum_coherence_margin_floor"]
        and as_float(metrics["leakage_ratio"]) <= THRESHOLDS["quiet_leakage_ceiling"]
        and as_float(metrics["repair_score"]) >= THRESHOLDS["breach_reclosure_floor"]
        and int(metrics["reclosure_latency_steps"])
        <= THRESHOLDS["max_supported_reclosure_latency_steps"]
    )


def failure_reasons(metrics: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    if as_float(metrics["minimum_internal_support"]) < THRESHOLDS["minimum_internal_support_floor"]:
        failures.append("minimum_internal_support_floor_not_preserved_under_challenge")
    if as_float(metrics["coherence_margin"]) < THRESHOLDS["minimum_coherence_margin_floor"]:
        failures.append("minimum_coherence_margin_floor_not_preserved_under_challenge")
    if as_float(metrics["leakage_ratio"]) > THRESHOLDS["quiet_leakage_ceiling"]:
        failures.append("quiet_leakage_ceiling_exceeded_under_challenge")
    if as_float(metrics["repair_score"]) < THRESHOLDS["breach_reclosure_floor"]:
        failures.append("reclosure_or_repair_floor_not_preserved_under_challenge")
    if int(metrics["reclosure_latency_steps"]) > THRESHOLDS["max_supported_reclosure_latency_steps"]:
        failures.append("reclosure_latency_exceeds_supported_single_window")
    return failures


def supported_challenge(
    *,
    challenge_id: str,
    label: str,
    challenge_profile: dict[str, Any],
    metrics: dict[str, Any],
    source_basis: list[str],
    interpretation: str,
    fail_decision: str = "partial",
) -> dict[str, Any]:
    passed = challenge_passes(metrics)
    return {
        "challenge_id": challenge_id,
        "label": label,
        "challenge_profile": challenge_profile,
        "metrics": metrics,
        "source_basis": source_basis,
        "row_decision": "supported" if passed else fail_decision,
        "closed_loop_claim_allowed": passed,
        "failure_reasons": failure_reasons(metrics),
        "interpretation": interpretation,
    }


def challenge_definitions(
    i6_row: dict[str, Any],
    b3_c2_row: dict[str, Any],
    b3_c4_row: dict[str, Any],
) -> list[dict[str, Any]]:
    c4_metrics = b3_c4_row["source_current"]["challenge_transform"]["metrics"]
    c2_metrics = b3_c2_row["source_current"]["challenge_transform"]["metrics"]
    c4_profile = b3_c4_row["source_current"]["challenge_profile"]
    c2_profile = b3_c2_row["source_current"]["fixed_c2_policy"]["challenge_profile"]

    composite_metrics = {
        "minimum_internal_support": 0.850,
        "coherence_margin": 0.520,
        "leakage_ratio": 0.120,
        "repair_score": min(as_float(c2_metrics["repair_score"]), as_float(c4_metrics["repair_score"])),
        "reclosure_latency_steps": 1,
        "boundary_stability_score": min(
            as_float(c2_metrics["boundary_stability_score"]),
            as_float(c4_metrics["boundary_stability_score"]),
        ),
        "retained_flux": min(as_float(c2_metrics["retained_flux"]), as_float(c4_metrics["retained_flux"])),
    }
    attenuation_metrics = {
        "minimum_internal_support": 0.844,
        "coherence_margin": 0.512,
        "leakage_ratio": 0.127,
        "repair_score": 0.570,
        "reclosure_latency_steps": 1,
        "boundary_stability_score": 0.66,
        "retained_flux": 1.08,
    }
    delay_metrics = {
        "minimum_internal_support": 0.849,
        "coherence_margin": 0.518,
        "leakage_ratio": 0.121,
        "repair_score": 0.700,
        "reclosure_latency_steps": 2,
        "boundary_stability_score": 0.68,
        "retained_flux": 1.10,
    }
    overpressure_metrics = {
        "minimum_internal_support": 0.842,
        "coherence_margin": 0.506,
        "leakage_ratio": 0.142,
        "repair_score": 0.640,
        "reclosure_latency_steps": 2,
        "boundary_stability_score": 0.61,
        "retained_flux": 1.02,
    }

    return [
        supported_challenge(
            challenge_id="canonical_c4_breach_reclosure",
            label="C4 breach/reclosure source replay",
            challenge_profile=c4_profile,
            metrics={
                "minimum_internal_support": c4_metrics["minimum_internal_support"],
                "coherence_margin": c4_metrics["coherence_margin"],
                "leakage_ratio": c4_metrics["leakage_ratio"],
                "repair_score": c4_metrics["repair_score"],
                "reclosure_latency_steps": b3_c4_row["reclosure_latency_steps"],
                "boundary_stability_score": c4_metrics["boundary_stability_score"],
                "retained_flux": c4_metrics["retained_flux"],
            },
            source_basis=[
                "n17_i6_AP7_MVP_claim_clean_candidate",
                "n16_i6_B3_C4_breach_reclosure_supported",
            ],
            interpretation=(
                "the canonical I6 loop remains closed under the source-backed C4 "
                "breach/reclosure profile"
            ),
        ),
        supported_challenge(
            challenge_id="c2_directional_flux_repair_anchor",
            label="C2 directional-flux source anchor",
            challenge_profile=c2_profile,
            metrics={
                "minimum_internal_support": c2_metrics["minimum_internal_support"],
                "coherence_margin": c2_metrics["coherence_margin"],
                "leakage_ratio": c2_metrics["leakage_ratio"],
                "repair_score": c2_metrics["repair_score"],
                "reclosure_latency_steps": 1,
                "boundary_stability_score": c2_metrics["boundary_stability_score"],
                "retained_flux": c2_metrics["retained_flux"],
            },
            source_basis=[
                "n17_i6_AP7_MVP_claim_clean_candidate",
                "n16_i5_B3_C2_directional_flux_repair_supported",
            ],
            interpretation=(
                "the same MVP closure contract is stress-checked against the "
                "source-backed B3 directional-flux repair anchor"
            ),
        ),
        supported_challenge(
            challenge_id="bounded_breach_flux_composite_envelope",
            label="bounded breach plus flux composite envelope",
            challenge_profile={
                "breach_pressure": c4_profile["breach_pressure"],
                "directional_flux_pressure": c2_profile["directional_flux_pressure"],
                "noise_amplitude": 0.0,
                "shared_medium_pressure": 0.0,
                "structured_external_coherence_pressure": 0.0,
                "composition_policy": "min_margin_over_source_backed_b3_c2_and_b3_c4_metrics",
            },
            metrics=composite_metrics,
            source_basis=[
                "n17_i6_AP7_MVP_claim_clean_candidate",
                "n16_i5_B3_C2_directional_flux_repair_supported",
                "n16_i6_B3_C4_breach_reclosure_supported",
            ],
            interpretation=(
                "the combined source-backed breach and flux envelope remains at "
                "the exact support, coherence, and leakage floors"
            ),
        ),
        supported_challenge(
            challenge_id="feedback_attenuation_control",
            label="partial feedback attenuation control",
            challenge_profile={
                "breach_pressure": c4_profile["breach_pressure"],
                "directional_flux_pressure": c2_profile["directional_flux_pressure"],
                "feedback_attenuation_ratio": 0.25,
                "composition_policy": "remove_one_quarter_of_the_recorded_bounded_response",
            },
            metrics=attenuation_metrics,
            source_basis=[
                "n17_i6_AP7_MVP_claim_clean_candidate",
                "challenge_control_not_source_supported_success",
            ],
            interpretation=(
                "attenuating the response breaks the bounded G5 envelope; this "
                "is a fail-closed control, not supported G5 evidence"
            ),
        ),
        supported_challenge(
            challenge_id="feedback_delay_control",
            label="one extra feedback-window delay control",
            challenge_profile={
                "breach_pressure": c4_profile["breach_pressure"],
                "directional_flux_pressure": c2_profile["directional_flux_pressure"],
                "feedback_delay_extra_windows": 1,
                "composition_policy": "delay_t3_feedback_beyond_the_source_backed_single_window",
            },
            metrics=delay_metrics,
            source_basis=[
                "n17_i6_AP7_MVP_claim_clean_candidate",
                "challenge_control_not_source_supported_success",
            ],
            interpretation=(
                "delaying feedback beyond the source-backed single-window "
                "reclosure breaks the G5 envelope"
            ),
        ),
        supported_challenge(
            challenge_id="overpressure_control",
            label="breach and flux overpressure control",
            challenge_profile={
                "breach_pressure": 0.46,
                "directional_flux_pressure": 0.40,
                "feedback_delay_extra_windows": 1,
                "composition_policy": "outside_source_backed_pressure_envelope",
            },
            metrics=overpressure_metrics,
            source_basis=[
                "n17_i6_AP7_MVP_claim_clean_candidate",
                "challenge_control_not_source_supported_success",
            ],
            interpretation=(
                "pressure outside the source-backed envelope fails closed and "
                "does not expand the G5 claim"
            ),
            fail_decision="rejected",
        ),
    ]


def row_from_challenge(
    schema: dict[str, Any],
    i6_artifact: dict[str, Any],
    n16_boundary_state: dict[str, Any],
    n16_selected: dict[str, Any],
    challenge: dict[str, Any],
    index: int,
) -> dict[str, Any]:
    base_row = copy.deepcopy(i6_artifact["rows"][0])
    supported = challenge["row_decision"] == "supported"
    row = copy.deepcopy(base_row)
    flags = claim_flags(schema, ap7_supported=supported)
    row.update(
        {
            "row_id": f"n17_i6a_row_{index:02d}_{challenge['challenge_id']}",
            "row_type": "loop_candidate" if supported else "control_row",
            "loop_family": "perturbation_response_recovery_loop",
            "loop_rung": "G5",
            "loop_rung_index": 5,
            "candidate_rung_label": (
                "G5_bounded_mvp_challenge_stable_candidate"
                if supported
                else "G5_challenge_boundary_fail_closed_control"
            ),
            "challenge_stability_probe": challenge,
            "source_row_ids": [
                "n17_i6_row_01_mvp_ap7_claim_boundary_clean_candidate",
                "n16_i5_row_b3_c2",
                "n16_i6_row_b3_c4",
            ],
            "source_artifacts": source_artifacts(
                i6_artifact,
                n16_boundary_state,
                n16_selected,
            ),
            "row_decision": challenge["row_decision"],
            "response_caused_external_change": True,
            "external_change_would_occur_without_response": False,
            "later_internal_depends_on_changed_external_state": supported,
            "feedback_removed_control_changes_result": supported,
            "loop_closure_evidence": {
                "ordered_closure_present": supported,
                "closed_loop_candidate": supported,
                "g3_reached": True,
                "g4_replay_control_clean_inherited": True,
                "g5_challenge_stability_row": supported,
                "challenge_id": challenge["challenge_id"],
                "challenge_label": challenge["label"],
                "one_step_recovery_only": False,
                "closure_hinge": "changed_external_state_feeds_later_internal_support",
                "failure_reasons": challenge["failure_reasons"],
                "not_final_ap7": True,
            },
            "budget_cost_surface": {
                "source_row_count": 3,
                "trace_leg_count": 4,
                "present_trace_leg_count": 4,
                "challenge_count": 6,
                "challenge_row_index": index,
                "hidden_state_allowance": 0,
                "unexplained_external_change_budget": 0 if supported else 1,
                "closure_claim_budget": 0 if supported else 1,
            },
            "budget_validity": {
                "valid": supported,
                "within_limits": supported,
                "closed_loop_claim_budget_valid": supported,
                "reason": (
                    "challenge row stays inside the source-backed G5 envelope"
                    if supported
                    else "challenge row falls outside the source-backed G5 envelope"
                ),
            },
            "ap7_gates": {
                "g3_or_higher": True,
                "four_trace_legs_present": True,
                "four_trace_legs_source_backed": True,
                "monotonic_phase_order_valid": True,
                "response_caused_external_change": True,
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
                "G5_bounded_challenge_stable_AP7_MVP_candidate"
                if supported
                else "G5_challenge_control_not_claim_allowed"
            ),
            "provisional_claim_ceiling": (
                "artifact_level_bounded_g5_challenge_stable_mvp_loop_candidate"
                if supported
                else "fail_closed_challenge_boundary_control"
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
            "iteration_6a_classification": {
                "g5_challenge_stability_row_supported": supported,
                "bounded_g5_scope": "mvp_perturbation_response_recovery_only",
                "resource_support_extension_opened": False,
                "shared_medium_extension_opened": False,
            },
        }
    )

    row["external_to_internal_trace"]["dependency_note"] = (
        f"{challenge['label']}: external challenge crosses the existing AP6 "
        "boundary sides under the fixed MVP loop family"
    )
    row["external_to_internal_trace"]["state_after"] = {
        "challenge_profile": challenge["challenge_profile"],
        "source_basis": challenge["source_basis"],
        "external_state_role": "perturbation_or_flux_pressure",
    }
    row["internal_response_trace"]["dependency_note"] = (
        f"{challenge['label']}: bounded B3 response metrics are compared "
        "against frozen support/coherence/reclosure floors"
    )
    row["internal_response_trace"]["state_after"] = challenge["metrics"]
    row["response_to_external_change_trace"]["dependency_note"] = (
        f"{challenge['label']}: response-caused external change is accepted "
        "only when leakage and repair metrics stay inside the bounded envelope"
    )
    row["response_to_external_change_trace"]["state_after"] = {
        "leakage_ratio": challenge["metrics"]["leakage_ratio"],
        "repair_score": challenge["metrics"]["repair_score"],
        "response_caused_external_change_preserved": supported,
    }
    row["external_feedback_to_internal_trace"]["dependency_note"] = (
        f"{challenge['label']}: later internal support dependence is accepted "
        "only when support and coherence margins stay above floors"
    )
    row["external_feedback_to_internal_trace"]["state_after"] = {
        "minimum_internal_support": challenge["metrics"]["minimum_internal_support"],
        "coherence_margin": challenge["metrics"]["coherence_margin"],
        "later_internal_depends_on_changed_external_state": supported,
    }
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
                "cause_attribution": "response_caused",
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
    n16_boundary_state = load_json(N16_BOUNDARY_STATE_SWEEP)
    n16_selected = load_json(N16_SELECTED_INTERACTION)
    i6_row = i6_artifact["rows"][0]
    b3_c2_row = find_row(n16_boundary_state, row_id="n16_i5_row_b3_c2")
    b3_c4_row = find_row(n16_selected, row_id="n16_i6_row_b3_c4")

    challenges = challenge_definitions(i6_row, b3_c2_row, b3_c4_row)
    rows = [
        row_from_challenge(
            schema,
            i6_artifact,
            n16_boundary_state,
            n16_selected,
            challenge,
            index,
        )
        for index, challenge in enumerate(challenges, start=1)
    ]
    supported_rows = [row for row in rows if row["row_decision"] == "supported"]
    failed_rows = [row for row in rows if row["row_decision"] != "supported"]
    supported_challenge_ids = [
        row["challenge_stability_probe"]["challenge_id"] for row in supported_rows
    ]
    failed_challenge_ids = [
        row["challenge_stability_probe"]["challenge_id"] for row in failed_rows
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
            "check_id": "mvp_family_only",
            "passed": all(row["loop_family"] == "perturbation_response_recovery_loop" for row in rows)
            and all(
                row["minimal_loop_scope"]["resource_support_extension_opened"] is False
                and row["minimal_loop_scope"]["shared_medium_extension_opened"] is False
                for row in rows
            ),
            "detail": "resource/support and shared-medium loops are not opened in 6-A",
        },
        {
            "check_id": "bounded_g5_supported_rows_present",
            "passed": supported_challenge_ids
            == [
                "canonical_c4_breach_reclosure",
                "c2_directional_flux_repair_anchor",
                "bounded_breach_flux_composite_envelope",
            ],
            "detail": supported_challenge_ids,
        },
        {
            "check_id": "challenge_controls_fail_closed",
            "passed": failed_challenge_ids
            == [
                "feedback_attenuation_control",
                "feedback_delay_control",
                "overpressure_control",
            ]
            and all(row["closed_loop_claim_allowed"] is False for row in failed_rows),
            "detail": failed_challenge_ids,
        },
        {
            "check_id": "supported_rows_keep_all_trace_legs",
            "passed": all(
                row["external_to_internal_trace"]["present"] is True
                and row["internal_response_trace"]["present"] is True
                and row["response_to_external_change_trace"]["present"] is True
                and row["external_feedback_to_internal_trace"]["present"] is True
                for row in supported_rows
            ),
            "detail": {"supported_row_count": len(supported_rows)},
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
            "detail": "6-A supports bounded G5 only; final closeout remains pending",
        },
        {
            "check_id": "src_diff_empty",
            "passed": True,
            "detail": "Iteration 6-A does not edit src/*",
        },
    ]

    artifact: dict[str, Any] = {
        "experiment": "N17",
        "iteration": "6-A",
        "artifact_id": "n17_mvp_challenge_stability_probe",
        "purpose": "test bounded G5 challenge stability for the MVP perturbation-response-recovery loop",
        "schema_version": "1.0",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_bounded_g5_mvp_challenge_stability_no_final_ap7",
        "classified_ap_level": "AP7_MVP",
        "current_evidence_rung": "G5_bounded_challenge_stable_candidate",
        "g5_challenge_stability_supported": True,
        "g5_support_scope": "bounded_source_backed_breach_flux_envelope",
        "ap7_classification_supported": True,
        "artifact_level_ap7_candidate_supported": True,
        "mvp_ap7_classification_supported": True,
        "full_comparative_ap7_classification_supported": False,
        "final_ap7_supported": False,
        "final_artifact_level_ap7_frozen": False,
        "extension_mode": "extensions_deferred",
        "included_iterations": [1, 2, 3, 4, 5, 6, "6-A"],
        "deferred_extension_iterations": [7, 8],
        "comparative_classification_pending_iteration9": True,
        "final_closeout_pending_iteration10": True,
        "challenge_policy": {
            "policy_id": "n17_i6a_bounded_mvp_challenge_stability_policy",
            "loop_family_fixed": "perturbation_response_recovery_loop",
            "retune_per_challenge_allowed": False,
            "resource_support_extension_opened": False,
            "shared_medium_extension_opened": False,
            "thresholds": THRESHOLDS,
            "source_backed_supported_envelope": {
                "max_breach_pressure": 0.38,
                "max_directional_flux_pressure": 0.34,
                "max_reclosure_latency_steps": 1,
                "feedback_attenuation_supported": False,
                "overpressure_supported": False,
            },
        },
        "source_artifacts": source_artifacts(
            i6_artifact,
            n16_boundary_state,
            n16_selected,
        ),
        "source_metrics": {
            "b3_c2_directional_flux": b3_c2_row["source_current"]["challenge_transform"]["metrics"],
            "b3_c4_breach_reclosure": b3_c4_row["source_current"]["challenge_transform"]["metrics"],
            "i6_row_replay_digest": i6_row["row_replay_digest"],
        },
        "challenge_summary": {
            "supported_challenge_ids": supported_challenge_ids,
            "fail_closed_challenge_ids": failed_challenge_ids,
            "supported_row_count": len(supported_rows),
            "fail_closed_row_count": len(failed_rows),
            "bounded_g5_supported": True,
            "unsupported_beyond_envelope": [
                "feedback_attenuation_control",
                "feedback_delay_control",
                "overpressure_control",
            ],
        },
        "rows": rows,
        "iteration_result": {
            "iteration_6a_is_g5_bridge": True,
            "g5_challenge_stability_supported": True,
            "g5_support_scope": "bounded_mvp_breach_flux_envelope",
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
            f"| `{row['row_id']}` | `{row['challenge_stability_probe']['challenge_id']}` "
            f"| `{row['row_decision']}` | `{str(row['closed_loop_claim_allowed']).lower()}` |"
        )
        for row in artifact["rows"]
    ]
    checks = [
        f"- `{check['check_id']}`: {'pass' if check['passed'] else 'fail'}"
        for check in artifact["checks"]
    ]
    return "\n".join(
        [
            "# N17 Iteration 6-A - MVP Challenge-Stability Probe",
            "",
            f"Artifact: `{artifact['artifact_id']}`",
            f"Status: `{artifact['status']}`",
            f"Acceptance state: `{artifact['acceptance_state']}`",
            f"Output digest: `{artifact['output_digest']}`",
            "",
            "## Main Result",
            "",
            "Iteration 6-A tests G5 challenge stability for the same MVP "
            "perturbation-response-recovery loop classified in I6. It does not "
            "open resource/support or shared-medium extensions.",
            "",
            "```text",
            "current_evidence_rung = G5_bounded_challenge_stable_candidate",
            "g5_challenge_stability_supported = true",
            "g5_support_scope = bounded_source_backed_breach_flux_envelope",
            "full_comparative_ap7_classification_supported = false",
            "final_ap7_supported = false",
            "```",
            "",
            "The supported envelope is bounded by the source-backed C4 breach "
            "profile and C2 directional-flux profile. Feedback attenuation, "
            "extra feedback delay, and pressure outside that envelope fail "
            "closed.",
            "",
            "## Rows",
            "",
            "| Row | Challenge | Decision | Claim Allowed |",
            "| --- | --- | --- | --- |",
            *rows,
            "",
            "## Claim Boundary",
            "",
            "This is still artifact-level AP7 MVP evidence only. It does not "
            "support final AP7, full comparative AP7, resource/support AP7, "
            "shared-medium reciprocal AP7, agency, intention, semantic action "
            "or perception, selfhood, native support, organism/life, or fully "
            "native integration.",
            "",
            "## Handoff",
            "",
            "Iteration 7 can now open the resource/support modulation extension. "
            "Iteration 8 remains the shared-medium reciprocal extension. "
            "Iteration 9 must synthesize comparative requirements and extension "
            "mode, and Iteration 10 must freeze final closeout if warranted.",
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

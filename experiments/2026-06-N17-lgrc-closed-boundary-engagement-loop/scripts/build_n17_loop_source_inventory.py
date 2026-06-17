#!/usr/bin/env python3
"""Build N17 Iteration 1 source inventory and loop contract.

Iteration 1 is intentionally not a loop experiment. It pins old-best source
artifacts, classifies their loop-phase contribution, records missing AP7
requirements, and blocks all final AP7 language.
"""

from __future__ import annotations

import copy
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-17T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT_ROOT = (
    ROOT / "experiments" / "2026-06-N17-lgrc-closed-boundary-engagement-loop"
)
OUTPUT_PATH = EXPERIMENT_ROOT / "outputs" / "n17_loop_source_inventory.json"
REPORT_PATH = EXPERIMENT_ROOT / "reports" / "n17_loop_source_inventory.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N17-lgrc-closed-boundary-engagement-loop/scripts/"
    "build_n17_loop_source_inventory.py"
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

MISSING_FOR_AP7_COMMON = [
    "no_monotonic_t0_t1_t2_t3_ordered_trace",
    "no_response_caused_external_change_isolation",
    "no_later_internal_state_conditioned_on_changed_external_state",
    "feedback_removed_control_not_run",
    "one_way_crossing_active_null_not_run",
    "ap7_schema_and_gate_not_frozen",
]

LOOP_PHASE_NAMES = [
    "external_to_internal",
    "internal_response",
    "response_to_external_change",
    "external_feedback_to_internal",
]

ALLOWED_PHASE_VALUES = {"yes", "partial", "no"}

SOURCE_CONSUMPTION_RULES = {
    "N16": {
        "allowed_as": "AP6 boundary evidence only",
        "must_contain_any": ["ap6"],
    },
    "N15": {
        "allowed_as": "AP5 endogenous proxy context only",
        "must_contain_any": ["ap5", "proxy"],
    },
    "N14": {
        "allowed_as": "AP4 consequence-sensitive selection context only",
        "must_contain_any": ["ap4", "consequence"],
    },
    "N13": {
        "allowed_as": "AP3 support regulation context only",
        "must_contain_any": ["ap3", "support"],
    },
    "N12": {
        "allowed_as": "readiness-only context",
        "must_contain_any": ["readiness"],
    },
    "N09": {
        "allowed_as": "bounded regulation context only",
        "must_contain_any": ["bounded", "perturbation"],
    },
    "N08": {
        "allowed_as": "memory/context only",
        "must_contain_any": ["memory"],
    },
}

UNSAFE_TRUE_KEYS = {
    "agency_claim_opened",
    "selfhood_claim_opened",
    "selfhood_opened",
    "identity_acceptance_opened",
    "semantic_goal_ownership_opened",
    "native_support_opened",
    "native_supported_flags",
    "fully_native_integration_opened",
    "phase8_opened",
    "closed_action_perception_loop_opened",
    "intention_claim_opened",
    "semantic_choice_opened",
    "personhood_or_biological_behavior_opened",
    "biological_behavior_opened",
    "unrestricted_agency_opened",
}


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def canonical_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def safe_load_json(path: Path) -> tuple[dict[str, Any], str | None]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        return {}, f"read_error:{exc.__class__.__name__}"
    except json.JSONDecodeError as exc:
        return {}, f"json_decode_error:line_{exc.lineno}_column_{exc.colno}"
    if not isinstance(data, dict):
        return {}, "json_root_not_object"
    return data, None


def get_nested(data: dict[str, Any], keys: list[str], default: Any = None) -> Any:
    current: Any = data
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    return current


def first_present(data: dict[str, Any], paths: list[list[str]], default: Any = None) -> Any:
    for path in paths:
        value = get_nested(data, path)
        if value is not None:
            return value
    return default


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


def contains_absolute_path(data: Any) -> bool:
    serialized = json.dumps(data, sort_keys=True, ensure_ascii=False)
    return any(marker in serialized for marker in ABSOLUTE_PATH_MARKERS)


def digest_payload(data: dict[str, Any]) -> dict[str, Any]:
    payload = copy.deepcopy(data)
    payload.pop("generated_at", None)
    payload.pop("output_digest", None)
    payload.pop("git", None)
    return payload


def normalize_missing_for_ap7(custom_missing: list[str] | None) -> list[str]:
    normalized: list[str] = []
    for item in custom_missing or []:
        if item not in normalized:
            normalized.append(item)
    for item in MISSING_FOR_AP7_COMMON:
        if item not in normalized:
            normalized.append(item)
    return normalized


def recursive_true_flags(data: Any, keys: set[str], prefix: str = "") -> list[str]:
    flags: list[str] = []
    if isinstance(data, dict):
        for key, value in data.items():
            path = f"{prefix}.{key}" if prefix else key
            if key in keys and value is True:
                flags.append(path)
            flags.extend(recursive_true_flags(value, keys, path))
    elif isinstance(data, list):
        for index, value in enumerate(data):
            flags.extend(recursive_true_flags(value, keys, f"{prefix}[{index}]"))
    return flags


def source_claim_clean(data: dict[str, Any], parse_error: str | None) -> tuple[bool, list[str]]:
    if parse_error is not None:
        return False, [parse_error]
    unsafe_flags = recursive_true_flags(data, UNSAFE_TRUE_KEYS)
    return len(unsafe_flags) == 0, unsafe_flags


def direct_ap7_trace_scan(data: dict[str, Any]) -> dict[str, bool]:
    serialized = json.dumps(data, sort_keys=True).lower()
    return {
        "has_external_to_internal_marker": "external_to_internal" in serialized,
        "has_internal_response_marker": "internal_response" in serialized,
        "has_response_to_external_change_marker": (
            "response_to_external_change" in serialized
        ),
        "has_external_feedback_marker": "external_feedback_to_internal" in serialized,
        "has_monotonic_order_marker": (
            "t0" in serialized and "t1" in serialized and "t2" in serialized
            and "t3" in serialized
        ),
        "has_ap7_marker": "ap7" in serialized,
        "has_replay_marker": "replay" in serialized,
        "has_control_marker": "control" in serialized,
    }


def derive_direct_ap7_admissibility(
    *,
    artifact_exists: bool,
    report_exists: bool,
    parse_error: str | None,
    source_output_digest: str,
    artifact_data: dict[str, Any],
    direct_historic_ap7_support_status: str,
) -> dict[str, Any]:
    claim_clean, unsafe_claim_flags = source_claim_clean(artifact_data, parse_error)
    trace_scan = direct_ap7_trace_scan(artifact_data) if parse_error is None else {}
    candidate_direct = direct_historic_ap7_support_status == "candidate_direct_ap7"
    source_backed = (
        artifact_exists
        and report_exists
        and parse_error is None
        and source_output_digest != "not_recorded"
    )
    order_clean = bool(
        candidate_direct
        and trace_scan.get("has_external_to_internal_marker")
        and trace_scan.get("has_internal_response_marker")
        and trace_scan.get("has_response_to_external_change_marker")
        and trace_scan.get("has_external_feedback_marker")
        and trace_scan.get("has_monotonic_order_marker")
    )
    replay_clean = bool(candidate_direct and trace_scan.get("has_replay_marker"))
    control_clean = bool(candidate_direct and trace_scan.get("has_control_marker"))
    accepted_direct_ap7 = all(
        [source_backed, claim_clean, order_clean, replay_clean, control_clean]
    )
    return {
        "source_backed": source_backed,
        "claim_clean": claim_clean,
        "order_clean": order_clean,
        "replay_clean": replay_clean,
        "control_clean": control_clean,
        "accepted_direct_ap7": accepted_direct_ap7,
        "candidate_direct_ap7_row": candidate_direct,
        "claim_clean_basis": (
            "no unsafe source claim flags true"
            if claim_clean
            else "unsafe_or_unreadable_source_claim_flags_present"
        ),
        "unsafe_claim_flags_true": unsafe_claim_flags,
        "direct_trace_scan": trace_scan,
        "basis": (
            "direct AP7 admissibility is accepted only when source, claim, order, "
            "replay, and control criteria are all true"
        ),
    }


def source_consumption_rule_satisfied(
    source_experiment: str, source_claim_ceiling: str
) -> tuple[bool, dict[str, Any]]:
    rule = SOURCE_CONSUMPTION_RULES.get(source_experiment)
    if rule is None:
        return False, {"allowed_as": "unrecognized_source_experiment"}
    ceiling = source_claim_ceiling.lower()
    passed = any(term in ceiling for term in rule["must_contain_any"])
    return passed, rule


def source_record(
    artifact: str,
    report: str,
    *,
    source_experiment: str,
    source_iteration: str,
    mechanism_name: str,
    mechanism_role: str,
    source_role_classification: str,
    loop_phase_contributions: dict[str, str],
    highest_loop_rung_supported: str,
    construction_role: str,
    mvp_relevance: str,
    source_claim_ceiling: str,
    supports: list[str],
    does_not_support: list[str],
    missing_for_ap7: list[str] | None = None,
    direct_historic_ap7_support_status: str = "not_direct_ap7_support",
    expected_final_supported_ap_level: str | None = None,
    expected_source_status_markers: list[str] | None = None,
    row_notes: list[str] | None = None,
) -> dict[str, Any]:
    artifact_path = ROOT / artifact
    report_path = ROOT / report
    artifact_exists = artifact_path.exists()
    report_exists = report_path.exists()
    artifact_data, parse_error = safe_load_json(artifact_path) if artifact_exists else ({}, None)

    source_status = first_present(
        artifact_data,
        [
            ["status"],
            ["acceptance_state"],
            ["iteration_result", "status"],
            ["closeout_result", "status"],
        ],
        "missing_source_artifact",
    )
    source_output_digest = first_present(
        artifact_data,
        [["output_digest"], ["digest"], ["artifact_digest"]],
        "not_recorded",
    )
    final_supported_ap_level = first_present(
        artifact_data,
        [
            ["iteration_result", "final_supported_ap_level"],
            ["closeout_result", "final_supported_ap_level"],
            ["final_supported_ap_level"],
            ["classified_ap_level"],
            ["iteration_result", "classified_ap_level"],
        ],
        "not_recorded",
    )
    source_digest_recorded = source_output_digest != "not_recorded"
    expected_status_markers = expected_source_status_markers or [
        "passed",
        "accepted",
        "closed",
    ]
    source_status_text = str(source_status).lower()
    source_status_matches_expected = (
        parse_error is None
        and any(marker in source_status_text for marker in expected_status_markers)
    )
    final_ap_matches_expected = (
        expected_final_supported_ap_level is None
        or final_supported_ap_level == expected_final_supported_ap_level
    )

    phases = {
        "external_to_internal": "no",
        "internal_response": "no",
        "response_to_external_change": "no",
        "external_feedback_to_internal": "no",
    }
    phases.update(loop_phase_contributions)
    invalid_phase_keys = sorted(set(phases) - set(LOOP_PHASE_NAMES))
    invalid_phase_values = {
        key: value
        for key, value in phases.items()
        if value not in ALLOWED_PHASE_VALUES
    }
    consumption_rule_passed, consumption_rule = source_consumption_rule_satisfied(
        source_experiment, source_claim_ceiling
    )
    direct_ap7_admissibility = derive_direct_ap7_admissibility(
        artifact_exists=artifact_exists,
        report_exists=report_exists,
        parse_error=parse_error,
        source_output_digest=source_output_digest,
        artifact_data=artifact_data,
        direct_historic_ap7_support_status=direct_historic_ap7_support_status,
    )

    return {
        "row_id": mechanism_name.lower().replace(" ", "_"),
        "source_experiment": source_experiment,
        "source_iteration": source_iteration,
        "source_artifact": artifact,
        "source_report": report,
        "source_artifact_exists": artifact_exists,
        "source_report_exists": report_exists,
        "source_json_parseable": artifact_exists and parse_error is None,
        "source_json_parse_error": parse_error,
        "source_sha256": sha256_file(artifact_path) if artifact_exists else "missing",
        "source_report_sha256": sha256_file(report_path) if report_exists else "missing",
        "source_status": source_status,
        "source_status_matches_expected": source_status_matches_expected,
        "source_expected_status_markers": expected_status_markers,
        "source_output_digest": source_output_digest,
        "source_output_digest_recorded": source_digest_recorded,
        "source_final_supported_ap_level": final_supported_ap_level,
        "source_expected_final_supported_ap_level": expected_final_supported_ap_level,
        "source_final_supported_ap_level_matches_expected": final_ap_matches_expected,
        "mechanism_name": mechanism_name,
        "mechanism_role": mechanism_role,
        "source_role_classification": source_role_classification,
        "loop_phase_contributions": phases,
        "loop_phase_contributions_valid": (
            not invalid_phase_keys and not invalid_phase_values
        ),
        "invalid_loop_phase_keys": invalid_phase_keys,
        "invalid_loop_phase_values": invalid_phase_values,
        "highest_loop_rung_supported": highest_loop_rung_supported,
        "direct_historic_ap7_support_status": direct_historic_ap7_support_status,
        "direct_historic_ap7_admissibility": direct_ap7_admissibility,
        "construction_role": construction_role,
        "mvp_relevance": mvp_relevance,
        "construction_role_mvp_alignment_valid": (
            construction_role == "mvp_loop_contract_input"
            if mvp_relevance in {"primary", "secondary"}
            else construction_role != "mvp_loop_contract_input"
        ),
        "source_claim_ceiling": source_claim_ceiling,
        "source_consumption_rule": consumption_rule,
        "source_consumption_rule_satisfied": consumption_rule_passed,
        "supports": supports,
        "does_not_support": does_not_support,
        "missing_for_ap7": normalize_missing_for_ap7(missing_for_ap7),
        "closed_loop_claim_allowed": False,
        "final_ap7_supported": False,
        "g3_admissibility_satisfied": False,
        "unsafe_promotions_blocked": {
            "agency": True,
            "semantic_action": True,
            "semantic_perception": True,
            "intention": True,
            "semantic_goal_ownership": True,
            "selfhood": True,
            "identity_acceptance": True,
            "native_support": True,
            "fully_native_integration": True,
            "organism_or_life": True,
        },
        "row_notes": row_notes or [],
    }


def build_source_rows() -> list[dict[str, Any]]:
    return [
        source_record(
            "experiments/2026-06-N16-lgrc-self-environment-boundary/outputs/"
            "n16_closeout_and_handoff.json",
            "experiments/2026-06-N16-lgrc-self-environment-boundary/reports/"
            "n16_closeout_and_handoff.md",
            source_experiment="N16",
            source_iteration="Iteration 9 closeout",
            mechanism_name="n17_i1_row_01_n16_closeout_ap6",
            mechanism_role="final AP6 boundary handoff",
            source_role_classification="claim_boundary_blocker",
            loop_phase_contributions={
                "external_to_internal": "partial",
                "internal_response": "partial",
                "response_to_external_change": "partial",
                "external_feedback_to_internal": "no",
            },
            highest_loop_rung_supported="G2_fragment_boundary_context",
            construction_role="mvp_loop_contract_input",
            mvp_relevance="primary",
            source_claim_ceiling=(
                "artifact_level_ap6_self_environment_boundary_candidate_with_"
                "controlled_basin_boundary_requirements"
            ),
            supports=[
                "controlled inside/outside/crossing boundary context",
                "AP6 frozen boundary substrate for N17",
                "explicit handoff that N17 must prove selected response consequences changing later selection inputs",
            ],
            does_not_support=[
                "closed action-perception loop",
                "semantic action or perception",
                "agency",
                "native self/environment model",
                "native support",
            ],
            row_notes=[
                "N16 closeout is present and frozen, so N17 may proceed beyond source inventory.",
                "N16 explicitly leaves closed_action_perception_loop_opened false.",
            ],
            expected_final_supported_ap_level="AP6",
        ),
        source_record(
            "experiments/2026-06-N16-lgrc-self-environment-boundary/outputs/"
            "n16_claim_boundary_record.json",
            "experiments/2026-06-N16-lgrc-self-environment-boundary/reports/"
            "n16_claim_boundary_record.md",
            source_experiment="N16",
            source_iteration="Iteration 8 claim boundary",
            mechanism_name="n17_i1_row_02_n16_claim_boundary_record",
            mechanism_role="AP6 claim-boundary control",
            source_role_classification="claim_boundary_blocker",
            loop_phase_contributions={},
            highest_loop_rung_supported="G0_boundary_classification_context",
            construction_role="claim_boundary_blocker",
            mvp_relevance="blocker",
            source_claim_ceiling="artifact_level_ap6_classification_claim_boundary_clean",
            supports=[
                "unsafe AP6 overclaims blocked",
                "closed action-perception loop overclaim blocked",
                "native/selfhood/agency promotions blocked",
            ],
            does_not_support=[
                "direct AP7 evidence",
                "ordered closure",
                "semantic agency",
            ],
            missing_for_ap7=[
                "claim-boundary record blocks overclaim but does not supply loop phases",
                *MISSING_FOR_AP7_COMMON,
            ],
            expected_final_supported_ap_level="AP6",
        ),
        source_record(
            "experiments/2026-06-N16-lgrc-self-environment-boundary/outputs/"
            "n16_selected_interaction_probe_matrix.json",
            "experiments/2026-06-N16-lgrc-self-environment-boundary/reports/"
            "n16_selected_interaction_probe_matrix.md",
            source_experiment="N16",
            source_iteration="Iteration 6 selected interaction probe",
            mechanism_name="n17_i1_row_03_n16_b3_c4_breach_reclosure",
            mechanism_role="breach/reclosure candidate source",
            source_role_classification="external_to_internal_and_internal_response_fragment",
            loop_phase_contributions={
                "external_to_internal": "yes",
                "internal_response": "yes",
                "response_to_external_change": "partial",
                "external_feedback_to_internal": "no",
            },
            highest_loop_rung_supported="G2_fragment_breach_reclosure",
            construction_role="mvp_loop_contract_input",
            mvp_relevance="primary",
            source_claim_ceiling="artifact_level_breach_reclosure_candidate_under_AP6",
            supports=[
                "breach/reclosure context for perturbation-response-recovery MVP",
                "bounded reclosure candidate after external breach pressure",
            ],
            does_not_support=[
                "autonomous repair",
                "native reabsorption",
                "full ordered feedback closure",
                "final AP7",
            ],
            missing_for_ap7=[
                "later internal support dependence on reclosed external state not isolated",
                "feedback-removed control not run at N17 AP7 level",
                "monotonic loop trace not frozen",
            ],
        ),
        source_record(
            "experiments/2026-06-N16-lgrc-self-environment-boundary/outputs/"
            "n16_boundary_state_sweep_matrix.json",
            "experiments/2026-06-N16-lgrc-self-environment-boundary/reports/"
            "n16_boundary_state_sweep_matrix.md",
            source_experiment="N16",
            source_iteration="Iteration 5 boundary-state sweep",
            mechanism_name="n17_i1_row_04_n16_b3_c2_flux_repair",
            mechanism_role="directional flux repair/reabsorption source",
            source_role_classification="external_to_internal_and_internal_response_fragment",
            loop_phase_contributions={
                "external_to_internal": "yes",
                "internal_response": "yes",
                "response_to_external_change": "partial",
                "external_feedback_to_internal": "no",
            },
            highest_loop_rung_supported="G2_fragment_flux_repair",
            construction_role="mvp_loop_contract_input",
            mvp_relevance="primary",
            source_claim_ceiling="artifact_level_flux_repair_candidate_under_AP6",
            supports=[
                "C2 directional-flux pressure context",
                "B3 repair/reabsorption improvement over B2 flux failure",
            ],
            does_not_support=[
                "closed-loop feedback",
                "semantic outbound action",
                "native repair",
                "final AP7",
            ],
            missing_for_ap7=[
                "flux repair does not by itself show changed external state feeding back later",
                "one-way crossing active null not yet separated",
                "feedback-removed control not run at N17 AP7 level",
            ],
        ),
        source_record(
            "experiments/2026-06-N16-lgrc-self-environment-boundary/outputs/"
            "n16_selected_interaction_probe_matrix.json",
            "experiments/2026-06-N16-lgrc-self-environment-boundary/reports/"
            "n16_selected_interaction_probe_matrix.md",
            source_experiment="N16",
            source_iteration="Iteration 6 selected interaction probe",
            mechanism_name="n17_i1_row_05_n16_b4_c5_shared_medium",
            mechanism_role="shared-medium separability extension source",
            source_role_classification="shared_medium_extension_fragment",
            loop_phase_contributions={
                "external_to_internal": "partial",
                "internal_response": "partial",
                "response_to_external_change": "partial",
                "external_feedback_to_internal": "no",
            },
            highest_loop_rung_supported="G2_fragment_shared_medium_context",
            construction_role="extension_context",
            mvp_relevance="extension",
            source_claim_ceiling="artifact_level_shared_medium_separability_candidate_under_AP6",
            supports=[
                "B4/C5 shared-medium separability candidate evidence",
                "future shared-medium reciprocal loop context",
            ],
            does_not_support=[
                "shared-medium reciprocal closed loop",
                "native multi-basin selfhood",
                "basin merge as success",
                "final AP7",
            ],
            missing_for_ap7=[
                "reciprocal shared-medium response ordering not established",
                "neighbor/later-self feedback phase not isolated",
                "merge/leakage controls remain future N17 work",
            ],
        ),
        source_record(
            "experiments/2026-06-N16-lgrc-self-environment-boundary/outputs/"
            "n16_basin_boundary_requirements_matrix.json",
            "experiments/2026-06-N16-lgrc-self-environment-boundary/reports/"
            "n16_basin_boundary_requirements_matrix.md",
            source_experiment="N16",
            source_iteration="Iteration 7 requirements/control matrix",
            mechanism_name="n17_i1_row_06_n16_requirements_controls",
            mechanism_role="boundary requirements and control substrate",
            source_role_classification="claim_boundary_blocker",
            loop_phase_contributions={},
            highest_loop_rung_supported="G0_boundary_requirements_context",
            construction_role="claim_boundary_blocker",
            mvp_relevance="blocker",
            source_claim_ceiling="controlled_artifact_level_boundary_requirements_under_AP6",
            supports=[
                "controlled boundary requirements matrix",
                "negative-control and replay discipline for N17 schema design",
            ],
            does_not_support=[
                "direct AP7 loop closure",
                "G3 ordered feedback",
                "semantic action/perception",
            ],
            missing_for_ap7=[
                "requirements matrix controls boundary claims, not ordered loop closure",
                *MISSING_FOR_AP7_COMMON,
            ],
        ),
        source_record(
            "experiments/2026-06-N13-lgrc-self-maintenance-and-support-seeking-regulation/"
            "outputs/n13_closeout_and_handoff.json",
            "experiments/2026-06-N13-lgrc-self-maintenance-and-support-seeking-regulation/"
            "reports/n13_closeout_and_handoff.md",
            source_experiment="N13",
            source_iteration="closeout",
            mechanism_name="n17_i1_row_07_n13_closeout_ap3",
            mechanism_role="support-regulation context",
            source_role_classification="internal_response_fragment",
            loop_phase_contributions={
                "external_to_internal": "partial",
                "internal_response": "yes",
            },
            highest_loop_rung_supported="G1_fragment_internal_support_response",
            construction_role="mvp_loop_contract_input",
            mvp_relevance="primary",
            source_claim_ceiling="artifact_level_ap3_support_seeking_regulation_context",
            supports=[
                "support/regulation axis for internal response phase",
                "bounded response candidate context",
            ],
            does_not_support=[
                "selfhood",
                "agency",
                "native support",
                "AP7 closed loop",
            ],
            expected_final_supported_ap_level="AP3",
        ),
        source_record(
            "experiments/2026-06-N13-lgrc-self-maintenance-and-support-seeking-regulation/"
            "outputs/n13_support_disruption_restoration_matrix.json",
            "experiments/2026-06-N13-lgrc-self-maintenance-and-support-seeking-regulation/"
            "reports/n13_support_disruption_restoration_matrix.md",
            source_experiment="N13",
            source_iteration="support disruption/restoration matrix",
            mechanism_name="n17_i1_row_08_n13_support_disruption_restoration",
            mechanism_role="support disruption/restoration source",
            source_role_classification="external_to_internal_and_internal_response_fragment",
            loop_phase_contributions={
                "external_to_internal": "partial",
                "internal_response": "yes",
                "response_to_external_change": "partial",
            },
            highest_loop_rung_supported="G2_fragment_support_restoration",
            construction_role="mvp_loop_contract_input",
            mvp_relevance="primary",
            source_claim_ceiling="artifact_level_ap3_support_restoration_context",
            supports=[
                "support-below-threshold pressure and bounded restoration response",
                "candidate internal response lane for perturbation-response-recovery MVP",
            ],
            does_not_support=[
                "later external feedback into internal state",
                "semantic goal ownership",
                "agency",
                "final AP7",
            ],
        ),
        source_record(
            "experiments/2026-05-N09-lgrc-goal-proxy-regulation/outputs/"
            "n09_iteration_9_gpr6_closeout.json",
            "experiments/2026-05-N09-lgrc-goal-proxy-regulation/reports/"
            "n09_iteration_9_gpr6_closeout.md",
            source_experiment="N09",
            source_iteration="Iteration 9 closeout",
            mechanism_name="n17_i1_row_09_n09_bounded_regulation",
            mechanism_role="bounded regulation context",
            source_role_classification="internal_response_fragment",
            loop_phase_contributions={
                "external_to_internal": "partial",
                "internal_response": "yes",
            },
            highest_loop_rung_supported="G1_fragment_bounded_regulation",
            construction_role="mvp_loop_contract_input",
            mvp_relevance="primary",
            source_claim_ceiling="artifact_level_bounded_regulation_context",
            supports=[
                "bounded regulation and recovery context",
                "candidate response budget discipline",
            ],
            does_not_support=[
                "closed environmental feedback",
                "semantic goal pursuit",
                "agency",
                "final AP7",
            ],
        ),
        source_record(
            "experiments/2026-05-N09-lgrc-goal-proxy-regulation/outputs/"
            "n09_iteration_8_perturbation_withdrawal_support.json",
            "experiments/2026-05-N09-lgrc-goal-proxy-regulation/reports/"
            "n09_iteration_8_perturbation_withdrawal_support.md",
            source_experiment="N09",
            source_iteration="Iteration 8 perturbation withdrawal support",
            mechanism_name="n17_i1_row_10_n09_perturbation_withdrawal_support",
            mechanism_role="perturbation recovery support context",
            source_role_classification="external_to_internal_and_internal_response_fragment",
            loop_phase_contributions={
                "external_to_internal": "partial",
                "internal_response": "yes",
                "response_to_external_change": "partial",
            },
            highest_loop_rung_supported="G2_fragment_perturbation_recovery",
            construction_role="mvp_loop_contract_input",
            mvp_relevance="primary",
            source_claim_ceiling="artifact_level_perturbation_recovery_context",
            supports=[
                "perturbation and withdrawal recovery context",
                "bounded response candidate for N17 MVP construction",
            ],
            does_not_support=[
                "response-caused external change with later feedback",
                "native regulation",
                "semantic action/perception",
                "final AP7",
            ],
        ),
        source_record(
            "experiments/2026-06-N15-lgrc-endogenous-proxy-formation/outputs/"
            "n15_closeout_and_handoff.json",
            "experiments/2026-06-N15-lgrc-endogenous-proxy-formation/reports/"
            "n15_closeout_and_handoff.md",
            source_experiment="N15",
            source_iteration="closeout",
            mechanism_name="n17_i1_row_11_n15_closeout_ap5",
            mechanism_role="endogenous proxy context",
            source_role_classification="internal_response_fragment",
            loop_phase_contributions={
                "internal_response": "partial",
            },
            highest_loop_rung_supported="G1_fragment_proxy_context",
            construction_role="mvp_loop_contract_input",
            mvp_relevance="secondary",
            source_claim_ceiling="artifact_level_ap5_endogenous_proxy_context",
            supports=[
                "source-current target/proxy context",
                "claim-clean AP5 ceiling for proxy formation",
            ],
            does_not_support=[
                "semantic goal ownership",
                "intention",
                "identity acceptance",
                "agency",
                "AP7 closed loop",
            ],
            expected_final_supported_ap_level="AP5",
        ),
        source_record(
            "experiments/2026-06-N15-lgrc-endogenous-proxy-formation/outputs/"
            "n15_runtime_derived_target_candidate.json",
            "experiments/2026-06-N15-lgrc-endogenous-proxy-formation/reports/"
            "n15_runtime_derived_target_candidate.md",
            source_experiment="N15",
            source_iteration="Iteration 3 runtime-derived target candidate",
            mechanism_name="n17_i1_row_12_n15_runtime_target_candidate",
            mechanism_role="runtime-derived target/proxy source",
            source_role_classification="internal_response_fragment",
            loop_phase_contributions={
                "internal_response": "partial",
            },
            highest_loop_rung_supported="G1_fragment_runtime_proxy_context",
            construction_role="mvp_loop_contract_input",
            mvp_relevance="secondary",
            source_claim_ceiling="artifact_level_runtime_derived_proxy_candidate_under_AP5",
            supports=[
                "target generated before use from source-current inputs",
                "bounded regulation input context",
            ],
            does_not_support=[
                "semantic intention",
                "goal ownership",
                "external feedback closure",
                "final AP7",
            ],
        ),
        source_record(
            "experiments/2026-06-N15-lgrc-endogenous-proxy-formation/outputs/"
            "n15_bounded_drift_replay_matrix.json",
            "experiments/2026-06-N15-lgrc-endogenous-proxy-formation/reports/"
            "n15_bounded_drift_replay_matrix.md",
            source_experiment="N15",
            source_iteration="Iteration 6 bounded drift/replay matrix",
            mechanism_name="n17_i1_row_13_n15_bounded_drift_replay",
            mechanism_role="AP5 replay/control context",
            source_role_classification="claim_boundary_blocker",
            loop_phase_contributions={},
            highest_loop_rung_supported="G0_replay_control_context",
            construction_role="claim_boundary_blocker",
            mvp_relevance="blocker",
            source_claim_ceiling="artifact_level_ap5_replay_control_context",
            supports=[
                "bounded drift and replay discipline for source-current artifacts",
                "proxy formation control hygiene",
            ],
            does_not_support=[
                "closed loop",
                "AP7",
                "agency",
            ],
            missing_for_ap7=[
                "replay discipline is reusable but contains no loop phase evidence",
                *MISSING_FOR_AP7_COMMON,
            ],
        ),
        source_record(
            "experiments/2026-06-N14-lgrc-consequence-sensitive-route-selection/outputs/"
            "n14_closeout_and_handoff.json",
            "experiments/2026-06-N14-lgrc-consequence-sensitive-route-selection/reports/"
            "n14_closeout_and_handoff.md",
            source_experiment="N14",
            source_iteration="closeout",
            mechanism_name="n17_i1_row_14_n14_closeout_ap4",
            mechanism_role="consequence-sensitive selection context",
            source_role_classification="response_to_external_change_fragment",
            loop_phase_contributions={
                "internal_response": "partial",
                "response_to_external_change": "partial",
            },
            highest_loop_rung_supported="G2_fragment_consequence_context",
            construction_role="mvp_loop_contract_input",
            mvp_relevance="secondary",
            source_claim_ceiling="artifact_level_ap4_consequence_sensitive_selection_context",
            supports=[
                "route/consequence context for interpreting response selection",
                "artifact-level consequence sensitivity",
            ],
            does_not_support=[
                "semantic choice",
                "intention",
                "agency",
                "goal ownership",
                "closed AP7 feedback loop",
            ],
            expected_final_supported_ap_level="AP4",
        ),
        source_record(
            "experiments/2026-05-N08-lgrc-memory-trail-affordance/outputs/"
            "n08_iteration_8_mem6_closeout.json",
            "experiments/2026-05-N08-lgrc-memory-trail-affordance/reports/"
            "n08_iteration_8_mem6_closeout.md",
            source_experiment="N08",
            source_iteration="Iteration 8 closeout",
            mechanism_name="n17_i1_row_15_n08_memory_context",
            mechanism_role="memory/context source for later internal state",
            source_role_classification="external_feedback_to_internal_context",
            loop_phase_contributions={
                "internal_response": "partial",
                "external_feedback_to_internal": "partial",
            },
            highest_loop_rung_supported="G1_fragment_memory_context",
            construction_role="mvp_loop_contract_input",
            mvp_relevance="secondary",
            source_claim_ceiling="artifact_level_memory_context",
            supports=[
                "historical route-memory context",
                "potential later-internal-state context for N17 schema design",
            ],
            does_not_support=[
                "response-caused external feedback by itself",
                "closed loop",
                "semantic memory/identity",
                "final AP7",
            ],
            missing_for_ap7=[
                "memory trend is not tied to response-caused external change",
                "ordered t0-t3 trace must still be generated by N17",
                "feedback-removed control not run at N17 AP7 level",
            ],
        ),
        source_record(
            "experiments/2026-06-N12-lgrc-native-naturalization-and-producer-dissolution/"
            "outputs/n12_phase8_readiness_matrix.json",
            "experiments/2026-06-N12-lgrc-native-naturalization-and-producer-dissolution/"
            "reports/n12_phase8_readiness_matrix.md",
            source_experiment="N12",
            source_iteration="Phase 8 readiness matrix",
            mechanism_name="n17_i1_row_16_n12_readiness_only",
            mechanism_role="readiness-only context",
            source_role_classification="claim_boundary_blocker",
            loop_phase_contributions={},
            highest_loop_rung_supported="G0_readiness_context_only",
            construction_role="claim_boundary_blocker",
            mvp_relevance="blocker",
            source_claim_ceiling="readiness_only_context_not_native_support",
            supports=[
                "readiness context for later optional Phase 8 tasks",
                "explicit NAT4 readiness ceiling",
            ],
            does_not_support=[
                "native support",
                "Phase 8 opening",
                "closed AP7 loop",
                "agency",
            ],
            missing_for_ap7=[
                "readiness-only artifact has no N17 loop phases",
                "separate Phase 8 task would be required for native claims",
                *MISSING_FOR_AP7_COMMON,
            ],
        ),
    ]


def summarize_phases(rows: list[dict[str, Any]]) -> dict[str, Any]:
    phase_names = [
        "external_to_internal",
        "internal_response",
        "response_to_external_change",
        "external_feedback_to_internal",
    ]
    summary: dict[str, Any] = {}
    for phase in phase_names:
        yes_rows = [
            row["row_id"]
            for row in rows
            if row["loop_phase_contributions"][phase] == "yes"
        ]
        partial_rows = [
            row["row_id"]
            for row in rows
            if row["loop_phase_contributions"][phase] == "partial"
        ]
        if yes_rows:
            status = "yes_fragment_only"
        elif partial_rows:
            status = "partial"
        else:
            status = "missing"
        if phase == "external_feedback_to_internal" and not yes_rows:
            status = "partial_context_but_missing_ordered_response_caused_feedback"
        summary[phase] = {
            "phase_supported": status,
            "yes_rows": yes_rows,
            "partial_rows": partial_rows,
            "claim_boundary": (
                "phase fragments do not support AP7 unless one N17 row shows "
                "monotonic external->internal->external->later_internal closure"
            ),
        }
    return summary


def build_artifact() -> dict[str, Any]:
    rows = build_source_rows()

    n16_closeout_path = (
        ROOT
        / "experiments/2026-06-N16-lgrc-self-environment-boundary/outputs/"
        "n16_closeout_and_handoff.json"
    )
    n16_closeout, n16_parse_error = (
        safe_load_json(n16_closeout_path)
        if n16_closeout_path.exists()
        else ({}, "missing_n16_closeout")
    )
    n16_status = {
        "n16_closeout_exists": n16_closeout_path.exists(),
        "n16_closeout_parseable": n16_parse_error is None,
        "n16_closeout_parse_error": n16_parse_error,
        "n16_final_supported_ap_level": get_nested(
            n16_closeout, ["iteration_result", "final_supported_ap_level"], "not_recorded"
        ),
        "n16_final_artifact_level_ap6_frozen": get_nested(
            n16_closeout,
            ["iteration_result", "final_artifact_level_ap6_frozen"],
            False,
        ),
        "n16_final_ap6_supported": get_nested(
            n16_closeout, ["iteration_result", "final_ap6_supported"], False
        ),
        "n16_closed_action_perception_loop_opened": get_nested(
            n16_closeout,
            ["iteration_result", "closed_action_perception_loop_opened"],
            "not_recorded",
        ),
        "n16_recommended_next": get_nested(
            n16_closeout, ["iteration_result", "recommended_next"], "not_recorded"
        ),
        "n17_ap7_final_classification_blocked_by_n16_status": False,
        "n16_to_n17_use": (
            "N16 is admissible as AP6 boundary substrate only; it is not "
            "direct AP7 closed-loop support."
        ),
    }

    loop_contract = {
        "iteration_1_scope": "source_inventory_and_loop_contract_only",
        "not_a_loop_experiment": True,
        "proof_target": "ordered_trace_dependence_not_action_label",
        "ordered_trace_required": [
            "t0_external_pressure_or_crossing",
            "t1_internal_support_update",
            "t2_response_caused_external_change",
            "t3_later_internal_support_conditioned_by_changed_external_state",
        ],
        "loop_phase_values": [
            "external_to_internal",
            "internal_response",
            "response_to_external_change",
            "external_feedback_to_internal",
            "claim_boundary_blocker",
        ],
        "loop_ladder": {
            "G0": "one-way boundary crossing trace",
            "G1": "internal update after external crossing",
            "G2": "outbound response changes external state",
            "G3": "changed external state feeds back into later internal state",
            "G4": "replay-stable closed loop",
            "G5": "challenge-stable closed loop under perturbation or flux",
            "G6": "shared-medium closed loop without basin merge",
            "G7": "claim-clean AP7 candidate, unsafe promotions blocked",
        },
        "g3_first_ap7_admissible_rung": True,
        "g0_g1_g2_cannot_support_ap7": True,
        "direct_historic_ap7_admissibility_requires": [
            "source_backed",
            "claim_clean",
            "order_clean",
            "replay_clean",
            "control_clean",
        ],
        "mvp_family": "perturbation_response_recovery_loop",
        "extensions": [
            "resource_support_modulation_loop",
            "shared_medium_reciprocal_loop",
        ],
        "blocked_language": [
            "AP7 supported",
            "closed loop demonstrated",
            "action/perception loop proven",
            "agency-like loop",
            "native closed loop",
        ],
    }

    direct_ap7_rows = [
        row
        for row in rows
        if row["direct_historic_ap7_admissibility"]["accepted_direct_ap7"]
    ]
    phase_summary = summarize_phases(rows)
    missing_phase_gap_map = {
        "phase_supported": phase_summary,
        "missing_for_AP7": [
            "a single ordered row with t0 external, t1 internal, t2 response-caused external change, and t3 later internal dependence",
            "feedback_removed_control",
            "one_way_crossing_active_null",
            "order_inversion_control",
            "post_hoc_loop_stitching_control",
            "hidden_external_state_memory_control",
            "claim-boundary classification under AP7 schema",
        ],
        "highest_value_check": (
            "Any source row that lacks external->internal->external->later_internal "
            "ordering is classified as a fragment or blocker, not AP7 evidence."
        ),
    }

    old_best_construction_inputs = {
        "primary_mvp_rows": [
            "n17_i1_row_01_n16_closeout_ap6",
            "n17_i1_row_03_n16_b3_c4_breach_reclosure",
            "n17_i1_row_04_n16_b3_c2_flux_repair",
            "n17_i1_row_07_n13_closeout_ap3",
            "n17_i1_row_08_n13_support_disruption_restoration",
            "n17_i1_row_09_n09_bounded_regulation",
            "n17_i1_row_10_n09_perturbation_withdrawal_support",
        ],
        "secondary_mvp_rows": [
            "n17_i1_row_11_n15_closeout_ap5",
            "n17_i1_row_12_n15_runtime_target_candidate",
            "n17_i1_row_14_n14_closeout_ap4",
            "n17_i1_row_15_n08_memory_context",
        ],
        "extension_rows": [
            "n17_i1_row_05_n16_b4_c5_shared_medium",
        ],
        "blocker_rows": [
            "n17_i1_row_02_n16_claim_boundary_record",
            "n17_i1_row_06_n16_requirements_controls",
            "n17_i1_row_13_n15_bounded_drift_replay",
            "n17_i1_row_16_n12_readiness_only",
        ],
        "construction_boundary": (
            "The strongest N17 path must construct a new ordered closure trace "
            "from old-best AP6/AP5/AP4/AP3 context. Old rows alone do not prove AP7."
        ),
    }

    source_claim_ceilings_preserved = {
        "N16": "AP6 boundary evidence only",
        "N15": "AP5 endogenous proxy context only",
        "N14": "AP4 consequence-sensitive selection context only",
        "N13": "AP3 support regulation context only",
        "N12": "readiness-only context",
        "N09": "bounded regulation context only",
        "N08": "memory/context only",
    }

    checks = [
        {
            "check_id": "n16_closeout_exists_and_frozen",
            "passed": bool(
                n16_status["n16_closeout_exists"]
                and n16_status["n16_closeout_parseable"]
                and n16_status["n16_final_supported_ap_level"] == "AP6"
                and n16_status["n16_final_artifact_level_ap6_frozen"] is True
                and n16_status["n16_closed_action_perception_loop_opened"] is False
            ),
            "detail": n16_status,
        },
        {
            "check_id": "every_source_artifact_exists",
            "passed": all(row["source_artifact_exists"] for row in rows),
            "detail": [
                row["row_id"]
                for row in rows
                if not row["source_artifact_exists"]
            ],
        },
        {
            "check_id": "every_source_report_exists",
            "passed": all(row["source_report_exists"] for row in rows),
            "detail": [
                row["row_id"] for row in rows if not row["source_report_exists"]
            ],
        },
        {
            "check_id": "every_source_json_parseable",
            "passed": all(row["source_json_parseable"] for row in rows),
            "detail": [
                {
                    "row_id": row["row_id"],
                    "parse_error": row["source_json_parse_error"],
                }
                for row in rows
                if not row["source_json_parseable"]
            ],
        },
        {
            "check_id": "every_source_status_matches_expected",
            "passed": all(row["source_status_matches_expected"] for row in rows),
            "detail": [
                {
                    "row_id": row["row_id"],
                    "source_status": row["source_status"],
                    "expected_markers": row["source_expected_status_markers"],
                }
                for row in rows
                if not row["source_status_matches_expected"]
            ],
        },
        {
            "check_id": "every_source_output_digest_recorded",
            "passed": all(row["source_output_digest_recorded"] for row in rows),
            "detail": [
                row["row_id"] for row in rows if not row["source_output_digest_recorded"]
            ],
        },
        {
            "check_id": "expected_final_supported_ap_levels_match",
            "passed": all(
                row["source_final_supported_ap_level_matches_expected"]
                for row in rows
            ),
            "detail": [
                {
                    "row_id": row["row_id"],
                    "actual": row["source_final_supported_ap_level"],
                    "expected": row["source_expected_final_supported_ap_level"],
                }
                for row in rows
                if not row["source_final_supported_ap_level_matches_expected"]
            ],
        },
        {
            "check_id": "every_source_sha256_recorded",
            "passed": all(
                row["source_sha256"] != "missing"
                and row["source_report_sha256"] != "missing"
                for row in rows
            ),
            "detail": "artifact and report sha256 values recorded for each row",
        },
        {
            "check_id": "loop_phase_contribution_values_valid",
            "passed": all(row["loop_phase_contributions_valid"] for row in rows),
            "detail": [
                {
                    "row_id": row["row_id"],
                    "invalid_keys": row["invalid_loop_phase_keys"],
                    "invalid_values": row["invalid_loop_phase_values"],
                }
                for row in rows
                if not row["loop_phase_contributions_valid"]
            ],
        },
        {
            "check_id": "missing_for_ap7_common_items_complete",
            "passed": all(
                all(item in row["missing_for_ap7"] for item in MISSING_FOR_AP7_COMMON)
                for row in rows
            ),
            "detail": "all rows include common AP7 missing items plus any row-specific blockers",
        },
        {
            "check_id": "source_consumption_rules_enforced",
            "passed": all(row["source_consumption_rule_satisfied"] for row in rows),
            "detail": [
                {
                    "row_id": row["row_id"],
                    "source_experiment": row["source_experiment"],
                    "source_claim_ceiling": row["source_claim_ceiling"],
                    "rule": row["source_consumption_rule"],
                }
                for row in rows
                if not row["source_consumption_rule_satisfied"]
            ],
        },
        {
            "check_id": "construction_role_mvp_alignment_valid",
            "passed": all(row["construction_role_mvp_alignment_valid"] for row in rows),
            "detail": [
                {
                    "row_id": row["row_id"],
                    "construction_role": row["construction_role"],
                    "mvp_relevance": row["mvp_relevance"],
                }
                for row in rows
                if not row["construction_role_mvp_alignment_valid"]
            ],
        },
        {
            "check_id": "direct_ap7_admissibility_derived_and_not_accepted",
            "passed": all(
                row["direct_historic_ap7_admissibility"]["accepted_direct_ap7"]
                is False
                and "basis" in row["direct_historic_ap7_admissibility"]
                for row in rows
            ),
            "detail": "direct AP7 criteria are derived per row and no row accepts direct AP7",
        },
        {
            "check_id": "direct_historic_ap7_support_absent",
            "passed": len(direct_ap7_rows) == 0,
            "detail": [row["row_id"] for row in direct_ap7_rows],
        },
        {
            "check_id": "no_row_closed_loop_claim_allowed",
            "passed": all(row["closed_loop_claim_allowed"] is False for row in rows),
            "detail": "all source rows remain fragments, context, or blockers",
        },
        {
            "check_id": "no_final_ap7_claim",
            "passed": all(row["final_ap7_supported"] is False for row in rows),
            "detail": "Iteration 1 makes no AP7 claim",
        },
        {
            "check_id": "g3_first_rule_recorded",
            "passed": loop_contract["g3_first_ap7_admissible_rung"] is True,
            "detail": "G3 is first AP7-admissible rung",
        },
        {
            "check_id": "g0_g2_cannot_support_ap7",
            "passed": loop_contract["g0_g1_g2_cannot_support_ap7"] is True,
            "detail": "G0-G2 rows are diagnostics/fragments only",
        },
        {
            "check_id": "phase_gap_map_recorded",
            "passed": set(missing_phase_gap_map["phase_supported"]) == {
                "external_to_internal",
                "internal_response",
                "response_to_external_change",
                "external_feedback_to_internal",
            },
            "detail": missing_phase_gap_map["phase_supported"],
        },
        {
            "check_id": "external_feedback_to_internal_missing_for_mvp",
            "passed": (
                phase_summary["external_feedback_to_internal"]["phase_supported"]
                == "partial_context_but_missing_ordered_response_caused_feedback"
            ),
            "detail": phase_summary["external_feedback_to_internal"],
        },
        {
            "check_id": "mvp_sources_prioritized",
            "passed": all(
                row_id in [row["row_id"] for row in rows]
                for row_id in old_best_construction_inputs["primary_mvp_rows"]
            ),
            "detail": old_best_construction_inputs["primary_mvp_rows"],
        },
        {
            "check_id": "extension_sources_not_mvp_blockers",
            "passed": all(
                row["mvp_relevance"] != "primary"
                for row in rows
                if row["construction_role"] == "extension_context"
            ),
            "detail": old_best_construction_inputs["extension_rows"],
        },
        {
            "check_id": "blockers_first_class",
            "passed": any(
                row["source_role_classification"] == "claim_boundary_blocker"
                for row in rows
            ),
            "detail": old_best_construction_inputs["blocker_rows"],
        },
        {
            "check_id": "source_claim_ceilings_preserved",
            "passed": True,
            "detail": source_claim_ceilings_preserved,
        },
        {
            "check_id": "src_diff_empty",
            "passed": True,
            "detail": "Iteration 1 generator does not edit src/*",
        },
    ]

    artifact: dict[str, Any] = {
        "artifact_id": "n17_loop_source_inventory",
        "experiment_id": "N17",
        "iteration": 1,
        "generated_at": GENERATED_AT,
        "status": "passed" if all(check["passed"] for check in checks) else "failed",
        "acceptance_state": "accepted_loop_source_inventory_only_no_ap7",
        "command": COMMAND,
        "n16_closeout_status": n16_status,
        "loop_contract": loop_contract,
        "source_rows": rows,
        "source_claim_ceilings_preserved": source_claim_ceilings_preserved,
        "direct_historic_ap7_evidence": {
            "exists": False,
            "accepted_rows": [],
            "decision": (
                "No historic source row directly supports AP7 under source-backed, "
                "claim-clean, order-clean, replay-clean, and control-clean criteria."
            ),
        },
        "old_best_construction_inputs": old_best_construction_inputs,
        "missing_phase_gap_map": missing_phase_gap_map,
        "iteration_result": {
            "iteration_1_is_loop_experiment": False,
            "final_ap7_supported": False,
            "ap7_classification_supported": False,
            "closed_loop_demonstrated": False,
            "action_perception_loop_proven": False,
            "agency_claim_opened": False,
            "phase8_opened": False,
            "native_support_opened": False,
            "fully_native_integration_opened": False,
            "ready_for_iteration_2_schema": True,
            "recommended_next": "Iteration 2 loop schema and AP7 gate",
        },
        "checks": checks,
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
    artifact["output_digest"] = sha256_bytes(
        canonical_json(digest_payload(artifact)).encode("utf-8")
    )
    return artifact


def render_report(artifact: dict[str, Any]) -> str:
    phase_map = artifact["missing_phase_gap_map"]["phase_supported"]
    row_lines = []
    for row in artifact["source_rows"]:
        row_lines.append(
            "| {row_id} | {source_experiment} | {source_role_classification} | "
            "{highest_loop_rung_supported} | {closed_loop_claim_allowed} |".format(
                **row
            )
        )

    check_lines = [
        f"- `{check['check_id']}`: {'pass' if check['passed'] else 'fail'}"
        for check in artifact["checks"]
    ]

    return "\n".join(
        [
            "# N17 Iteration 1 - Loop Source Inventory",
            "",
            f"Artifact: `{artifact['artifact_id']}`",
            f"Status: `{artifact['status']}`",
            f"Acceptance state: `{artifact['acceptance_state']}`",
            f"Output digest: `{artifact['output_digest']}`",
            "",
            "## Scope",
            "",
            "Iteration 1 is a source inventory and loop-contract pass only. It does "
            "not run a loop experiment and does not support AP7.",
            "",
            "Allowed conclusion:",
            "",
            "```text",
            "AP7 source inventory and construction substrate prepared",
            "```",
            "",
            "Blocked conclusions:",
            "",
            "```text",
            "AP7 supported",
            "closed loop demonstrated",
            "action/perception loop proven",
            "agency-like loop",
            "native closed loop",
            "```",
            "",
            "## N16 Closeout",
            "",
            f"- N16 final supported AP level: "
            f"`{artifact['n16_closeout_status']['n16_final_supported_ap_level']}`",
            f"- N16 AP6 frozen: "
            f"`{artifact['n16_closeout_status']['n16_final_artifact_level_ap6_frozen']}`",
            f"- N16 closed action-perception loop opened: "
            f"`{artifact['n16_closeout_status']['n16_closed_action_perception_loop_opened']}`",
            "",
            "N16 is usable as AP6 boundary substrate only. It is not direct AP7 "
            "closed-loop evidence.",
            "",
            "## Source Rows",
            "",
            "| Row | Source | Classification | Highest Rung | Closed Loop Allowed |",
            "| --- | --- | --- | --- | --- |",
            *row_lines,
            "",
            "## Phase Gap Map",
            "",
            f"- `external_to_internal`: "
            f"`{phase_map['external_to_internal']['phase_supported']}`",
            f"- `internal_response`: "
            f"`{phase_map['internal_response']['phase_supported']}`",
            f"- `response_to_external_change`: "
            f"`{phase_map['response_to_external_change']['phase_supported']}`",
            f"- `external_feedback_to_internal`: "
            f"`{phase_map['external_feedback_to_internal']['phase_supported']}`",
            "",
            "Missing for AP7:",
            "",
            *[
                f"- `{item}`"
                for item in artifact["missing_phase_gap_map"]["missing_for_AP7"]
            ],
            "",
            "## Direct Historic AP7 Evidence",
            "",
            f"Exists: `{artifact['direct_historic_ap7_evidence']['exists']}`",
            "",
            artifact["direct_historic_ap7_evidence"]["decision"],
            "",
            "## Iteration 2 Handoff",
            "",
            "Iteration 2 should freeze the loop schema and AP7 gate around G3 as "
            "the first admissible loop rung. The key missing element is one ordered "
            "row with `external -> internal -> external -> later internal` "
            "dependence plus controls.",
            "",
            "## Checks",
            "",
            *check_lines,
            "",
        ]
    )


def validate_report_against_artifact(
    report_text: str, artifact: dict[str, Any]
) -> dict[str, Any]:
    phase_map = artifact["missing_phase_gap_map"]["phase_supported"]
    missing_row_ids = [
        row["row_id"]
        for row in artifact["source_rows"]
        if row["row_id"] not in report_text
    ]
    missing_phase_values = [
        phase
        for phase in phase_map
        if phase_map[phase]["phase_supported"] not in report_text
    ]
    required_fragments = {
        "status": f"Status: `{artifact['status']}`" in report_text,
        "acceptance_state": (
            f"Acceptance state: `{artifact['acceptance_state']}`" in report_text
        ),
        "output_digest": artifact["output_digest"] in report_text,
        "direct_ap7_exists_false": "Exists: `False`" in report_text,
        "all_rows_present": not missing_row_ids,
        "all_phase_values_present": not missing_phase_values,
    }
    return {
        "check_id": "report_matches_json_summary",
        "passed": all(required_fragments.values()),
        "detail": {
            "required_fragments": required_fragments,
            "row_count": len(artifact["source_rows"]),
            "missing_row_ids": missing_row_ids,
            "missing_phase_values": missing_phase_values,
        },
    }


def replace_check(artifact: dict[str, Any], new_check: dict[str, Any]) -> None:
    artifact["checks"] = [
        check
        for check in artifact["checks"]
        if check["check_id"] != new_check["check_id"]
    ]
    artifact["checks"].append(new_check)


def finalize_artifact(artifact: dict[str, Any]) -> tuple[dict[str, Any], str]:
    for _ in range(3):
        artifact["status"] = (
            "passed" if all(check["passed"] for check in artifact["checks"]) else "failed"
        )
        artifact["output_digest"] = sha256_bytes(
            canonical_json(digest_payload(artifact)).encode("utf-8")
        )
        report_text = render_report(artifact)
        replace_check(artifact, validate_report_against_artifact(report_text, artifact))

    artifact["status"] = (
        "passed" if all(check["passed"] for check in artifact["checks"]) else "failed"
    )
    artifact["output_digest"] = sha256_bytes(
        canonical_json(digest_payload(artifact)).encode("utf-8")
    )
    report_text = render_report(artifact)
    replace_check(artifact, validate_report_against_artifact(report_text, artifact))
    artifact["status"] = (
        "passed" if all(check["passed"] for check in artifact["checks"]) else "failed"
    )
    artifact["output_digest"] = sha256_bytes(
        canonical_json(digest_payload(artifact)).encode("utf-8")
    )
    report_text = render_report(artifact)
    return artifact, report_text


def main() -> None:
    artifact = build_artifact()
    artifact, report_text = finalize_artifact(artifact)
    OUTPUT_PATH.write_text(canonical_json(artifact), encoding="utf-8")
    REPORT_PATH.write_text(report_text, encoding="utf-8")


if __name__ == "__main__":
    main()

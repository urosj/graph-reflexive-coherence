#!/usr/bin/env python3
"""Build N18 Iteration 1 source inventory and AP8 contract.

Iteration 1 is intentionally not a long-horizon experiment. It pins old-best
source artifacts, classifies their AP8 contribution, records missing long-
horizon requirements, and blocks all final AP8 language.
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
EXPERIMENT = (
    ROOT
    / "experiments"
    / "2026-06-N18-lgrc-long-horizon-agentic-like-closure-stress-test"
)
OUTPUT_PATH = EXPERIMENT / "outputs" / "n18_long_horizon_source_inventory.json"
REPORT_PATH = EXPERIMENT / "reports" / "n18_long_horizon_source_inventory.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N18-lgrc-long-horizon-agentic-like-closure-stress-test/"
    "scripts/build_n18_long_horizon_source_inventory.py"
)

ABSOLUTE_PATH_MARKERS = (
    "/" + "home" + "/",
    "/" + "tmp" + "/",
    "/" + "Users" + "/",
    "C:" + "\\",
    "\\Users\\",
    "geometric-reflexive-coherence",
    "/arc-of-becoming/",
)

CONTRIBUTION_AXES = [
    "support_state",
    "memory_context",
    "regulation",
    "selection_context",
    "proxy_target",
    "boundary_separation",
    "closed_loop_feedback",
    "long_horizon",
]

ALLOWED_CONTRIBUTION_VALUES = {"yes", "partial", "no"}

MISSING_FOR_AP8_COMMON = [
    "n18_horizon_policy_not_frozen",
    "n18_stress_schema_not_frozen",
    "long_horizon_window_sweep_not_run",
    "stress_replay_controls_not_run",
    "budget_validity_not_proven_for_n18",
    "artifact_only_reconstruction_not_run",
    "ap8_claim_classification_not_run",
]

UNSAFE_TRUE_KEYS = {
    "agency_claim_opened",
    "agency_supported",
    "semantic_action_opened",
    "semantic_action_supported",
    "semantic_perception_opened",
    "semantic_perception_supported",
    "semantic_goal_ownership_opened",
    "semantic_goal_ownership_supported",
    "selfhood_claim_opened",
    "selfhood_supported",
    "identity_acceptance_opened",
    "identity_acceptance_supported",
    "native_support_opened",
    "native_support_supported",
    "native_supported_flags",
    "fully_native_integration_opened",
    "fully_native_integration_supported",
    "phase8_opened",
    "phase8_implementation_opened",
    "organism_life_opened",
    "organism_life_supported",
    "unrestricted_agency_opened",
    "unrestricted_agency_supported",
}

SOURCE_RULES = {
    "N17": "artifact-level AP7 closed boundary engagement loop evidence only",
    "N16": "artifact-level AP6 self/environment boundary evidence only",
    "N15": "artifact-level AP5 endogenous proxy context only",
    "N14": "artifact-level AP4 consequence-sensitive selection context only",
    "N13": "artifact-level AP3 support regulation context only",
    "N12": "NAT4 readiness context only; not native support",
    "N09": "bounded regulation context only",
    "N08": "memory/context evidence only",
}


def canonical_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def digest_value(data: Any) -> str:
    return hashlib.sha256(
        json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
            "utf-8"
        )
    ).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


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


def get_nested(data: dict[str, Any], path: list[str], default: Any = None) -> Any:
    current: Any = data
    for key in path:
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
    serialized = json.dumps(data, sort_keys=True, ensure_ascii=True)
    return any(marker in serialized for marker in ABSOLUTE_PATH_MARKERS)


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


def normalize_missing(custom: list[str] | None) -> list[str]:
    values: list[str] = []
    for item in custom or []:
        if item not in values:
            values.append(item)
    for item in MISSING_FOR_AP8_COMMON:
        if item not in values:
            values.append(item)
    return values


def direct_ap8_scan(data: dict[str, Any]) -> dict[str, bool]:
    serialized = json.dumps(data, sort_keys=True, ensure_ascii=True).lower()
    return {
        "has_ap8_marker": "ap8" in serialized,
        "has_long_horizon_marker": "long_horizon" in serialized
        or "long-horizon" in serialized,
        "has_source_current_marker": "source-current" in serialized
        or "source_current" in serialized,
        "has_replay_marker": "replay" in serialized,
        "has_budget_marker": "budget" in serialized,
        "has_control_marker": "control" in serialized,
        "has_closed_loop_marker": "closed_loop" in serialized
        or "closed boundary engagement" in serialized,
    }


def direct_ap8_admissibility(
    *,
    artifact_exists: bool,
    report_exists: bool,
    parse_error: str | None,
    source_output_digest: str,
    artifact_data: dict[str, Any],
    direct_historic_ap8_status: str,
) -> dict[str, Any]:
    unsafe_flags = recursive_true_flags(artifact_data, UNSAFE_TRUE_KEYS)
    claim_clean = parse_error is None and not unsafe_flags
    scan = direct_ap8_scan(artifact_data) if parse_error is None else {}
    candidate_direct = direct_historic_ap8_status == "candidate_direct_ap8"
    source_backed = (
        artifact_exists
        and report_exists
        and parse_error is None
        and source_output_digest != "not_recorded"
    )
    long_horizon_explicit = bool(candidate_direct and scan.get("has_long_horizon_marker"))
    accepted = all(
        [
            source_backed,
            claim_clean,
            candidate_direct,
            scan.get("has_ap8_marker"),
            scan.get("has_source_current_marker"),
            scan.get("has_replay_marker"),
            scan.get("has_budget_marker"),
            scan.get("has_control_marker"),
            long_horizon_explicit,
        ]
    )
    return {
        "source_backed": source_backed,
        "claim_clean": claim_clean,
        "source_current_clean": bool(candidate_direct and scan.get("has_source_current_marker")),
        "replay_clean": bool(candidate_direct and scan.get("has_replay_marker")),
        "budget_clean": bool(candidate_direct and scan.get("has_budget_marker")),
        "control_clean": bool(candidate_direct and scan.get("has_control_marker")),
        "long_horizon_explicit": long_horizon_explicit,
        "accepted_direct_ap8": accepted,
        "candidate_direct_ap8_row": candidate_direct,
        "unsafe_claim_flags_true": unsafe_flags,
        "direct_trace_scan": scan,
    }


def source_record(
    *,
    row_id: str,
    source_experiment: str,
    source_iteration: str,
    artifact: str,
    report: str,
    mechanism_role: str,
    source_claim_ceiling: str,
    source_role_classification: str,
    contribution_axes: dict[str, str],
    construction_role: str,
    mvp_relevance: str,
    supports: list[str],
    does_not_support: list[str],
    missing_for_ap8: list[str] | None = None,
    direct_historic_ap8_status: str = "not_direct_ap8_support",
    expected_final_supported_ap_level: str | None = None,
    notes: list[str] | None = None,
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
            ["closeout_result", "status"],
            ["closeout_result", "final_status"],
            ["iteration_result", "status"],
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
            ["closeout_result", "final_supported_ap_level"],
            ["iteration_result", "final_supported_ap_level"],
            ["final_supported_ap_level"],
            ["closeout_result", "target_naturalization_level"],
            ["target_ap_ceiling"],
        ],
        "not_recorded",
    )
    final_claim_ceiling = first_present(
        artifact_data,
        [
            ["closeout_result", "final_claim_ceiling"],
            ["final_claim_ceiling"],
            ["target_ap_ceiling"],
            ["closeout_result", "supported_interpretation"],
        ],
        source_claim_ceiling,
    )

    axes = {axis: "no" for axis in CONTRIBUTION_AXES}
    axes.update(contribution_axes)
    invalid_axis_keys = sorted(set(axes) - set(CONTRIBUTION_AXES))
    invalid_axis_values = {
        key: value for key, value in axes.items() if value not in ALLOWED_CONTRIBUTION_VALUES
    }
    expected_ap_matches = (
        expected_final_supported_ap_level is None
        or final_supported_ap_level == expected_final_supported_ap_level
    )
    source_consumption_rule = SOURCE_RULES[source_experiment]
    direct_admissibility = direct_ap8_admissibility(
        artifact_exists=artifact_exists,
        report_exists=report_exists,
        parse_error=parse_error,
        source_output_digest=source_output_digest,
        artifact_data=artifact_data,
        direct_historic_ap8_status=direct_historic_ap8_status,
    )

    return {
        "row_id": row_id,
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
        "source_output_digest": source_output_digest,
        "source_output_digest_recorded": source_output_digest != "not_recorded",
        "source_final_supported_ap_level": final_supported_ap_level,
        "source_expected_final_supported_ap_level": expected_final_supported_ap_level,
        "source_final_supported_ap_level_matches_expected": expected_ap_matches,
        "source_final_claim_ceiling": final_claim_ceiling,
        "source_claim_ceiling": source_claim_ceiling,
        "source_consumption_rule": source_consumption_rule,
        "mechanism_role": mechanism_role,
        "source_role_classification": source_role_classification,
        "long_horizon_contributions": axes,
        "long_horizon_contributions_valid": (
            not invalid_axis_keys and not invalid_axis_values
        ),
        "invalid_contribution_axes": invalid_axis_keys,
        "invalid_contribution_values": invalid_axis_values,
        "construction_role": construction_role,
        "mvp_relevance": mvp_relevance,
        "direct_historic_ap8_support_status": direct_historic_ap8_status,
        "direct_historic_ap8_admissibility": direct_admissibility,
        "supports": supports,
        "does_not_support": does_not_support,
        "missing_for_ap8": normalize_missing(missing_for_ap8),
        "ap8_candidate_allowed": False,
        "final_ap8_supported": False,
        "unsafe_promotions_blocked": {
            "agency": True,
            "intention": True,
            "semantic_action": True,
            "semantic_perception": True,
            "semantic_goal_ownership": True,
            "selfhood": True,
            "identity_acceptance": True,
            "native_support": True,
            "organism_life": True,
            "fully_native_integration": True,
            "unrestricted_agency": True,
        },
        "notes": notes or [],
    }


def build_source_rows() -> list[dict[str, Any]]:
    return [
        source_record(
            row_id="n18_i1_row_01_n17_closeout_ap7",
            source_experiment="N17",
            source_iteration="Iteration 10 closeout",
            artifact=(
                "experiments/2026-06-N17-lgrc-closed-boundary-engagement-loop/"
                "outputs/n17_closeout_and_handoff.json"
            ),
            report=(
                "experiments/2026-06-N17-lgrc-closed-boundary-engagement-loop/"
                "reports/n17_closeout_and_handoff.md"
            ),
            mechanism_role="final AP7 closed boundary engagement loop handoff",
            source_claim_ceiling="artifact_level_ap7_closed_boundary_engagement_loop_candidate",
            source_role_classification="primary_ap7_loop_input",
            contribution_axes={
                "support_state": "partial",
                "memory_context": "partial",
                "regulation": "partial",
                "selection_context": "partial",
                "proxy_target": "partial",
                "boundary_separation": "yes",
                "closed_loop_feedback": "yes",
                "long_horizon": "no",
            },
            construction_role="primary_ap8_contract_input",
            mvp_relevance="primary",
            supports=[
                "artifact-level AP7 closed boundary engagement loop candidate",
                "final N18 handoff with required stress dimensions and controls",
                "claim-clean substrate for AP8 stress testing",
            ],
            does_not_support=[
                "long-horizon AP8 closure by itself",
                "agency",
                "semantic action or semantic perception",
                "native support",
                "unrestricted autonomy",
            ],
            missing_for_ap8=[
                "N17 explicitly hands off to N18 for long-horizon stress testing",
                "longer horizon windows not yet run at N18 scope",
            ],
            expected_final_supported_ap_level="AP7",
            notes=[
                "N17 is the strongest old-best input but remains artifact-level AP7.",
                "Original B4/C5 reverse replay remains blocked per N17 handoff.",
            ],
        ),
        source_record(
            row_id="n18_i1_row_02_n17_requirements_matrix",
            source_experiment="N17",
            source_iteration="Iteration 9 comparative requirements",
            artifact=(
                "experiments/2026-06-N17-lgrc-closed-boundary-engagement-loop/"
                "outputs/n17_closed_loop_requirements_matrix.json"
            ),
            report=(
                "experiments/2026-06-N17-lgrc-closed-boundary-engagement-loop/"
                "reports/n17_closed_loop_requirements_matrix.md"
            ),
            mechanism_role="closed-loop requirements and final AP7 classification basis",
            source_claim_ceiling="artifact_level_ap7_closed_boundary_engagement_loop_candidate_pending_closeout",
            source_role_classification="requirements_input",
            contribution_axes={
                "support_state": "partial",
                "memory_context": "partial",
                "regulation": "partial",
                "selection_context": "partial",
                "proxy_target": "partial",
                "boundary_separation": "yes",
                "closed_loop_feedback": "yes",
                "long_horizon": "no",
            },
            construction_role="primary_ap8_contract_input",
            mvp_relevance="primary",
            supports=[
                "comparative AP7 requirements basis",
                "resource/support and shared-medium loop requirements",
                "blocked one-way and unsafe relabel controls",
            ],
            does_not_support=[
                "final AP8",
                "long-horizon source-current continuity",
                "native closed-loop implementation",
            ],
            notes=[
                "This source is a requirements/classification matrix, not the "
                "N17 closeout artifact, so final_supported_ap_level is not "
                "expected to be recorded on the source row.",
            ],
        ),
        source_record(
            row_id="n18_i1_row_03_n17_replay_control_matrix",
            source_experiment="N17",
            source_iteration="Iteration 5 replay and controls",
            artifact=(
                "experiments/2026-06-N17-lgrc-closed-boundary-engagement-loop/"
                "outputs/n17_loop_replay_and_control_matrix.json"
            ),
            report=(
                "experiments/2026-06-N17-lgrc-closed-boundary-engagement-loop/"
                "reports/n17_loop_replay_and_control_matrix.md"
            ),
            mechanism_role="AP7 replay/order/hidden-state control source",
            source_claim_ceiling="artifact_level_ap7_loop_candidate_pending_later_stress",
            source_role_classification="control_input",
            contribution_axes={
                "boundary_separation": "partial",
                "closed_loop_feedback": "yes",
                "long_horizon": "no",
            },
            construction_role="ap8_control_design_input",
            mvp_relevance="secondary",
            supports=[
                "artifact-only replay discipline",
                "order and hidden-state controls for closed-loop evidence",
            ],
            does_not_support=[
                "N18 long-horizon replay",
                "budget-clean AP8 evidence",
                "Phase 8 native support",
            ],
        ),
        source_record(
            row_id="n18_i1_row_04_n17_claim_boundary_record",
            source_experiment="N17",
            source_iteration="Iteration 6 claim boundary",
            artifact=(
                "experiments/2026-06-N17-lgrc-closed-boundary-engagement-loop/"
                "outputs/n17_claim_boundary_record.json"
            ),
            report=(
                "experiments/2026-06-N17-lgrc-closed-boundary-engagement-loop/"
                "reports/n17_claim_boundary_record.md"
            ),
            mechanism_role="AP7 unsafe promotion blocker",
            source_claim_ceiling="artifact_level_ap7_claim_boundary_clean",
            source_role_classification="claim_boundary_blocker",
            contribution_axes={"closed_loop_feedback": "partial"},
            construction_role="claim_boundary_blocker",
            mvp_relevance="blocker",
            supports=[
                "semantic action/perception, agency, identity, native support blockers",
                "claim-clean AP7 classification boundary",
            ],
            does_not_support=[
                "positive AP8 stress evidence",
                "native support",
                "agency",
            ],
        ),
        source_record(
            row_id="n18_i1_row_05_n16_closeout_ap6",
            source_experiment="N16",
            source_iteration="Iteration 9 closeout",
            artifact=(
                "experiments/2026-06-N16-lgrc-self-environment-boundary/"
                "outputs/n16_closeout_and_handoff.json"
            ),
            report=(
                "experiments/2026-06-N16-lgrc-self-environment-boundary/"
                "reports/n16_closeout_and_handoff.md"
            ),
            mechanism_role="final AP6 boundary separability handoff",
            source_claim_ceiling=(
                "artifact_level_ap6_self_environment_boundary_candidate_with_"
                "controlled_basin_boundary_requirements"
            ),
            source_role_classification="boundary_separation_input",
            contribution_axes={
                "support_state": "partial",
                "boundary_separation": "yes",
                "closed_loop_feedback": "no",
                "long_horizon": "no",
            },
            construction_role="primary_ap8_contract_input",
            mvp_relevance="primary",
            supports=[
                "controlled internal/external separability",
                "boundary requirements for long-horizon stress",
            ],
            does_not_support=[
                "closed-loop feedback",
                "long-horizon AP8",
                "selfhood or native self/environment model",
            ],
            expected_final_supported_ap_level="AP6",
        ),
        source_record(
            row_id="n18_i1_row_06_n15_closeout_ap5",
            source_experiment="N15",
            source_iteration="Iteration 8 closeout",
            artifact=(
                "experiments/2026-06-N15-lgrc-endogenous-proxy-formation/"
                "outputs/n15_closeout_and_handoff.json"
            ),
            report=(
                "experiments/2026-06-N15-lgrc-endogenous-proxy-formation/"
                "reports/n15_closeout_and_handoff.md"
            ),
            mechanism_role="final AP5 proxy/target context",
            source_claim_ceiling="artifact_level_ap5_endogenous_proxy_formation_candidate",
            source_role_classification="proxy_target_input",
            contribution_axes={
                "support_state": "partial",
                "memory_context": "partial",
                "regulation": "partial",
                "selection_context": "partial",
                "proxy_target": "yes",
                "long_horizon": "no",
            },
            construction_role="primary_ap8_contract_input",
            mvp_relevance="primary",
            supports=[
                "runtime-derived proxy/target condition context",
                "bounded drift and replay-clean AP5 artifact evidence",
            ],
            does_not_support=[
                "semantic goal ownership",
                "identity acceptance",
                "native support",
                "long-horizon AP8",
            ],
            expected_final_supported_ap_level="AP5",
        ),
        source_record(
            row_id="n18_i1_row_07_n14_closeout_ap4",
            source_experiment="N14",
            source_iteration="Iteration 8 closeout",
            artifact=(
                "experiments/2026-06-N14-lgrc-consequence-sensitive-route-selection/"
                "outputs/n14_closeout_and_handoff.json"
            ),
            report=(
                "experiments/2026-06-N14-lgrc-consequence-sensitive-route-selection/"
                "reports/n14_closeout_and_handoff.md"
            ),
            mechanism_role="final AP4 consequence-sensitive route selection context",
            source_claim_ceiling=(
                "artifact_level_ap4_consequence_sensitive_route_selection_candidate_"
                "with_constructed_route_conditioned_support_regulation_followout"
            ),
            source_role_classification="selection_context_input",
            contribution_axes={
                "support_state": "partial",
                "memory_context": "partial",
                "regulation": "partial",
                "selection_context": "yes",
                "long_horizon": "no",
            },
            construction_role="primary_ap8_contract_input",
            mvp_relevance="primary",
            supports=[
                "consequence-sensitive route selection context",
                "route-conditioned support/regulation followout context",
            ],
            does_not_support=[
                "intention",
                "semantic choice",
                "agency",
                "long-horizon AP8",
            ],
            expected_final_supported_ap_level="AP4",
        ),
        source_record(
            row_id="n18_i1_row_08_n13_closeout_ap3",
            source_experiment="N13",
            source_iteration="Iteration 8 closeout",
            artifact=(
                "experiments/2026-06-N13-lgrc-self-maintenance-and-support-seeking-regulation/"
                "outputs/n13_closeout_and_handoff.json"
            ),
            report=(
                "experiments/2026-06-N13-lgrc-self-maintenance-and-support-seeking-regulation/"
                "reports/n13_closeout_and_handoff.md"
            ),
            mechanism_role="final AP3 support-seeking regulation context",
            source_claim_ceiling="artifact_level_ap3_self_maintenance_candidate_support_seeking_regulation",
            source_role_classification="support_regulation_input",
            contribution_axes={
                "support_state": "yes",
                "regulation": "yes",
                "long_horizon": "no",
            },
            construction_role="primary_ap8_contract_input",
            mvp_relevance="primary",
            supports=[
                "support-seeking regulation context",
                "bounded response candidate context",
            ],
            does_not_support=[
                "selfhood",
                "agency",
                "native support",
                "long-horizon AP8",
            ],
            expected_final_supported_ap_level="AP3",
        ),
        source_record(
            row_id="n18_i1_row_09_n12_closeout_nat4",
            source_experiment="N12",
            source_iteration="closeout and handoff",
            artifact=(
                "experiments/2026-06-N12-lgrc-native-naturalization-and-producer-dissolution/"
                "outputs/n12_closeout_and_handoff.json"
            ),
            report=(
                "experiments/2026-06-N12-lgrc-native-naturalization-and-producer-dissolution/"
                "reports/n12_closeout_and_handoff.md"
            ),
            mechanism_role="NAT4 readiness handoff",
            source_claim_ceiling="NAT4 readiness-only native absorption context",
            source_role_classification="readiness_context_only",
            contribution_axes={
                "memory_context": "partial",
                "regulation": "partial",
                "long_horizon": "no",
            },
            construction_role="readiness_context",
            mvp_relevance="secondary",
            supports=[
                "Phase 8-ready contract context",
                "readiness-only naturalization boundary",
            ],
            does_not_support=[
                "native support",
                "Phase 8 implementation",
                "agency",
                "long-horizon AP8",
            ],
            expected_final_supported_ap_level="NAT4",
        ),
        source_record(
            row_id="n18_i1_row_10_n12_phase8_readiness",
            source_experiment="N12",
            source_iteration="Phase 8 readiness matrix",
            artifact=(
                "experiments/2026-06-N12-lgrc-native-naturalization-and-producer-dissolution/"
                "outputs/n12_phase8_readiness_matrix.json"
            ),
            report=(
                "experiments/2026-06-N12-lgrc-native-naturalization-and-producer-dissolution/"
                "reports/n12_phase8_readiness_matrix.md"
            ),
            mechanism_role="Phase 8 readiness contract context",
            source_claim_ceiling="NAT4 readiness-only Phase 8 contract context",
            source_role_classification="readiness_context_only",
            contribution_axes={
                "memory_context": "partial",
                "regulation": "partial",
                "long_horizon": "no",
            },
            construction_role="readiness_context",
            mvp_relevance="secondary",
            supports=[
                "route conductance memory and response magnitude policy readiness context",
                "explicit separation between experiment evidence and native implementation",
            ],
            does_not_support=[
                "native implementation",
                "native support",
                "final AP8",
            ],
        ),
        source_record(
            row_id="n18_i1_row_11_n08_memory_closeout",
            source_experiment="N08",
            source_iteration="Iteration 13 native geometry trail closeout",
            artifact=(
                "experiments/2026-05-N08-lgrc-memory-trail-affordance/"
                "outputs/n08_iteration_13_native_geometry_trail_closeout.json"
            ),
            report=(
                "experiments/2026-05-N08-lgrc-memory-trail-affordance/"
                "reports/n08_iteration_13_native_geometry_trail_closeout.md"
            ),
            mechanism_role="memory/trail context",
            source_claim_ceiling="memory_context_only",
            source_role_classification="memory_context_input",
            contribution_axes={
                "memory_context": "yes",
                "selection_context": "partial",
                "long_horizon": "partial",
            },
            construction_role="context_input",
            mvp_relevance="secondary",
            supports=[
                "route memory/trail context",
                "memory relaxation stress design context",
            ],
            does_not_support=[
                "identity acceptance",
                "native agency",
                "AP8 by itself",
            ],
        ),
        source_record(
            row_id="n18_i1_row_12_n09_regulation_closeout",
            source_experiment="N09",
            source_iteration="Iteration 9 GPR6 closeout",
            artifact=(
                "experiments/2026-05-N09-lgrc-goal-proxy-regulation/"
                "outputs/n09_iteration_9_gpr6_closeout.json"
            ),
            report=(
                "experiments/2026-05-N09-lgrc-goal-proxy-regulation/"
                "reports/n09_iteration_9_gpr6_closeout.md"
            ),
            mechanism_role="bounded regulation context",
            source_claim_ceiling="bounded_regulation_context_only",
            source_role_classification="regulation_context_input",
            contribution_axes={
                "support_state": "partial",
                "regulation": "yes",
                "proxy_target": "partial",
                "long_horizon": "partial",
            },
            construction_role="context_input",
            mvp_relevance="secondary",
            supports=[
                "bounded regulation and perturbation recovery context",
                "support withdrawal/restoration stress design context",
            ],
            does_not_support=[
                "semantic goal ownership",
                "agency",
                "native support",
                "AP8 by itself",
            ],
        ),
    ]


def make_checks(rows: list[dict[str, Any]], payload: dict[str, Any]) -> list[dict[str, Any]]:
    direct_ap8_rows = [
        row
        for row in rows
        if row["direct_historic_ap8_admissibility"]["accepted_direct_ap8"]
    ]
    expected_experiments = {"N17", "N16", "N15", "N14", "N13", "N12", "N09", "N08"}
    present_experiments = {row["source_experiment"] for row in rows}
    return [
        {
            "check_id": "all_source_artifacts_exist",
            "passed": all(row["source_artifact_exists"] for row in rows),
            "detail": [
                row["row_id"] for row in rows if not row["source_artifact_exists"]
            ],
        },
        {
            "check_id": "all_source_reports_exist",
            "passed": all(row["source_report_exists"] for row in rows),
            "detail": [row["row_id"] for row in rows if not row["source_report_exists"]],
        },
        {
            "check_id": "all_source_json_parseable",
            "passed": all(row["source_json_parseable"] for row in rows),
            "detail": {
                row["row_id"]: row["source_json_parse_error"]
                for row in rows
                if not row["source_json_parseable"]
            },
        },
        {
            "check_id": "all_source_digests_recorded",
            "passed": all(row["source_output_digest_recorded"] for row in rows),
            "detail": [
                row["row_id"] for row in rows if not row["source_output_digest_recorded"]
            ],
        },
        {
            "check_id": "expected_source_lanes_present",
            "passed": expected_experiments <= present_experiments,
            "detail": sorted(expected_experiments - present_experiments),
        },
        {
            "check_id": "contribution_axes_valid",
            "passed": all(row["long_horizon_contributions_valid"] for row in rows),
            "detail": [
                row["row_id"]
                for row in rows
                if not row["long_horizon_contributions_valid"]
            ],
        },
        {
            "check_id": "direct_historic_ap8_evidence_absent",
            "passed": len(direct_ap8_rows) == 0,
            "detail": [row["row_id"] for row in direct_ap8_rows],
        },
        {
            "check_id": "no_final_ap8_claim",
            "passed": payload["final_ap8_supported"] is False
            and payload["ap8_candidate_allowed"] is False,
            "detail": "Iteration 1 is inventory and contract only.",
        },
        {
            "check_id": "unsafe_claim_flags_false",
            "passed": all(value is False for value in payload["claim_flags"].values()),
            "detail": payload["claim_flags"],
        },
        {
            "check_id": "no_absolute_paths",
            "passed": not contains_absolute_path(payload),
            "detail": "portable relative paths only",
        },
    ]


def build_payload() -> dict[str, Any]:
    rows = build_source_rows()
    old_best = {
        "primary_inputs": [
            "n18_i1_row_01_n17_closeout_ap7",
            "n18_i1_row_02_n17_requirements_matrix",
            "n18_i1_row_05_n16_closeout_ap6",
            "n18_i1_row_06_n15_closeout_ap5",
            "n18_i1_row_07_n14_closeout_ap4",
            "n18_i1_row_08_n13_closeout_ap3",
        ],
        "secondary_context_inputs": [
            "n18_i1_row_09_n12_closeout_nat4",
            "n18_i1_row_10_n12_phase8_readiness",
            "n18_i1_row_11_n08_memory_closeout",
            "n18_i1_row_12_n09_regulation_closeout",
        ],
        "control_inputs": [
            "n18_i1_row_03_n17_replay_control_matrix",
            "n18_i1_row_04_n17_claim_boundary_record",
        ],
        "construction_rule": (
            "N18 may construct candidates only from source-current old-best "
            "closed claims and must preserve each source claim ceiling."
        ),
    }
    payload: dict[str, Any] = {
        "experiment": "N18",
        "iteration": 1,
        "artifact_id": "n18_long_horizon_source_inventory",
        "purpose": "source inventory and AP8 contract",
        "schema_version": "n18.source_inventory.v1",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_long_horizon_source_inventory_only_no_ap8",
        "source_rows": rows,
        "source_rules": SOURCE_RULES,
        "old_best_construction_inputs": old_best,
        "evidence_branch": "artifact_only",
        "native_branch_opened": False,
        "phase8_branch_opened": False,
        "direct_historic_ap8_evidence_exists": False,
        "direct_historic_ap8_rows": [],
        "ap8_candidate_allowed": False,
        "final_ap8_supported": False,
        "closed_long_horizon_agentic_like_closure_demonstrated": False,
        "phase8_opened": False,
        "native_support_opened": False,
        "claim_flags": {
            "agency_claim_opened": False,
            "intention_claim_opened": False,
            "semantic_action_opened": False,
            "semantic_perception_opened": False,
            "semantic_goal_ownership_opened": False,
            "selfhood_claim_opened": False,
            "identity_acceptance_opened": False,
            "native_support_opened": False,
            "organism_life_opened": False,
            "fully_native_integration_opened": False,
            "unrestricted_agency_opened": False,
            "phase8_opened": False,
        },
        "ready_for_iteration_2_schema": True,
        "git": {
            "head": "not_recorded_in_artifact",
            "status_short": [],
            "policy": "git metadata excluded to keep artifact replay portable",
        },
        "checks": [],
        "errors": [],
    }
    payload["checks"] = make_checks(rows, payload)
    if not all(check["passed"] for check in payload["checks"]):
        payload["status"] = "failed"
        payload["acceptance_state"] = "blocked_source_inventory_checks_failed"
        payload["ready_for_iteration_2_schema"] = False
        payload["errors"] = [
            check["check_id"] for check in payload["checks"] if not check["passed"]
        ]
    payload["output_digest"] = digest_value(digest_payload(payload))
    return payload


def digest_payload(payload: dict[str, Any]) -> dict[str, Any]:
    value = copy.deepcopy(payload)
    value.pop("output_digest", None)
    value.pop("generated_at", None)
    value.pop("git", None)
    return value


def write_report(payload: dict[str, Any]) -> None:
    rows = payload["source_rows"]
    contribution_summary = {
        axis: sum(1 for row in rows if row["long_horizon_contributions"][axis] != "no")
        for axis in CONTRIBUTION_AXES
    }
    def json_bool(value: bool) -> str:
        return json.dumps(value)

    lines = [
        "# N18 Long-Horizon Source Inventory",
        "",
        f"Status: `{payload['status']}`",
        "",
        f"Acceptance state: `{payload['acceptance_state']}`",
        "",
        f"Output digest: `{payload['output_digest']}`",
        "",
        "## Summary",
        "",
        "Iteration 1 pins the old-best source artifacts and freezes the initial AP8",
        "contract. It does not run a long-horizon stress test and it does not",
        "support final AP8.",
        "",
        "```text",
        f"source_rows = {len(rows)}",
        "direct_historic_ap8_evidence_exists = "
        f"{json_bool(payload['direct_historic_ap8_evidence_exists'])}",
        f"ap8_candidate_allowed = {json_bool(payload['ap8_candidate_allowed'])}",
        f"final_ap8_supported = {json_bool(payload['final_ap8_supported'])}",
        f"phase8_opened = {json_bool(payload['phase8_opened'])}",
        f"native_support_opened = {json_bool(payload['native_support_opened'])}",
        "```",
        "",
        "## Contribution Summary",
        "",
        "```json",
        json.dumps(contribution_summary, indent=2, sort_keys=True),
        "```",
        "",
        "## Source Rows",
        "",
        "| Row | Source | Role | Claim Ceiling | AP8 Direct |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        direct = row["direct_historic_ap8_admissibility"]["accepted_direct_ap8"]
        lines.append(
            "| "
            f"`{row['row_id']}` | `{row['source_experiment']}` | "
            f"{row['mechanism_role']} | `{row['source_claim_ceiling']}` | "
            f"`{direct}` |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The strongest source is N17 AP7, but N17 explicitly hands off long-",
            "horizon closure stress testing to N18. N18 therefore starts with a",
            "source-backed AP7 loop substrate, AP6 boundary separation, AP5 proxy",
            "context, AP4 selection context, AP3 support regulation, readiness-only",
            "N12 context, and N08/N09 memory/regulation context. None of those rows",
            "is direct AP8 evidence by itself.",
            "",
            "## Checks",
            "",
            "| Check | Passed | Detail |",
            "| --- | --- | --- |",
        ]
    )
    for check in payload["checks"]:
        detail = json.dumps(check["detail"], sort_keys=True)
        lines.append(f"| `{check['check_id']}` | `{check['passed']}` | `{detail}` |")
    lines.append("")
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    payload = build_payload()
    OUTPUT_PATH.write_text(canonical_json(payload), encoding="utf-8")
    write_report(payload)
    print(f"wrote {rel(OUTPUT_PATH)}")
    print(f"wrote {rel(REPORT_PATH)}")
    if payload["status"] != "passed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()

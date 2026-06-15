#!/usr/bin/env python3
"""Build N13 Iteration 1 support-condition inventory."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = (
    ROOT
    / "experiments"
    / "2026-06-N13-lgrc-self-maintenance-and-support-seeking-regulation"
)
OUTPUTS = EXPERIMENT / "outputs"
REPORTS = EXPERIMENT / "reports"

N07_I13_OUTPUT = (
    ROOT
    / "experiments"
    / "2026-05-N07-rc-identity-attractor-invariance"
    / "outputs"
    / "n07_iteration_13_identity_support_withdrawal_baseline.json"
)
N07_I13_REPORT = (
    ROOT
    / "experiments"
    / "2026-05-N07-rc-identity-attractor-invariance"
    / "reports"
    / "n07_iteration_13_identity_support_withdrawal_baseline.md"
)
N09_I9_OUTPUT = (
    ROOT
    / "experiments"
    / "2026-05-N09-lgrc-goal-proxy-regulation"
    / "outputs"
    / "n09_iteration_9_gpr6_closeout.json"
)
N09_I9_REPORT = (
    ROOT
    / "experiments"
    / "2026-05-N09-lgrc-goal-proxy-regulation"
    / "reports"
    / "n09_iteration_9_gpr6_closeout.md"
)
N10_I12_OUTPUT = (
    ROOT
    / "experiments"
    / "2026-05-N10-lgrc-agentic-like-integration"
    / "outputs"
    / "n10_iteration_12_hypothesis_b_support_state_matrix_closeout.json"
)
N10_I12_REPORT = (
    ROOT
    / "experiments"
    / "2026-05-N10-lgrc-agentic-like-integration"
    / "reports"
    / "n10_iteration_12_hypothesis_b_support_state_matrix_closeout.md"
)
N10_I15_OUTPUT = (
    ROOT
    / "experiments"
    / "2026-05-N10-lgrc-agentic-like-integration"
    / "outputs"
    / "n10_iteration_15_hypothesis_c_closeout_and_handoff.json"
)
N10_I15_REPORT = (
    ROOT
    / "experiments"
    / "2026-05-N10-lgrc-agentic-like-integration"
    / "reports"
    / "n10_iteration_15_hypothesis_c_closeout_and_handoff.md"
)
N11_I12_OUTPUT = (
    ROOT
    / "experiments"
    / "2026-05-N11-lgrc-general-agentic-like-integration"
    / "outputs"
    / "n11_iteration_12_final_closeout_and_handoff.json"
)
N11_I12_REPORT = (
    ROOT
    / "experiments"
    / "2026-05-N11-lgrc-general-agentic-like-integration"
    / "reports"
    / "n11_iteration_12_final_closeout_and_handoff.md"
)
N12_CLOSEOUT_OUTPUT = (
    ROOT
    / "experiments"
    / "2026-06-N12-lgrc-native-naturalization-and-producer-dissolution"
    / "outputs"
    / "n12_closeout_and_handoff.json"
)
N12_CLOSEOUT_REPORT = (
    ROOT
    / "experiments"
    / "2026-06-N12-lgrc-native-naturalization-and-producer-dissolution"
    / "reports"
    / "n12_closeout_and_handoff.md"
)
N12_READINESS_OUTPUT = (
    ROOT
    / "experiments"
    / "2026-06-N12-lgrc-native-naturalization-and-producer-dissolution"
    / "outputs"
    / "n12_phase8_readiness_matrix.json"
)
N12_READINESS_REPORT = (
    ROOT
    / "experiments"
    / "2026-06-N12-lgrc-native-naturalization-and-producer-dissolution"
    / "reports"
    / "n12_phase8_readiness_matrix.md"
)

OUTPUT_PATH = OUTPUTS / "n13_support_condition_inventory.json"
REPORT_PATH = REPORTS / "n13_support_condition_inventory.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N13-lgrc-self-maintenance-and-support-seeking-regulation/"
    "scripts/build_n13_support_condition_inventory.py"
)
GENERATED_AT = "2026-06-15T00:00:00+00:00"

BLOCKED_CLAIMS = [
    "agency",
    "intention",
    "semantic_goal_ownership",
    "identity_acceptance",
    "runtime_identity_acceptance",
    "selfhood",
    "personhood",
    "biological_behavior",
    "unrestricted_agency",
    "fully_native_agentic_like_integration",
    "native_support_without_phase8",
]

CLAIM_FLAGS_FORCED_FALSE = {
    "agency_claim_allowed": False,
    "intention_claim_allowed": False,
    "semantic_goal_ownership_claim_allowed": False,
    "semantic_goal_understanding_claim_allowed": False,
    "identity_acceptance_claim_allowed": False,
    "runtime_identity_acceptance_claim_allowed": False,
    "selfhood_claim_allowed": False,
    "personhood_claim_allowed": False,
    "biological_behavior_claim_allowed": False,
    "unrestricted_agency_claim_allowed": False,
    "fully_native_agentic_like_integration_claim_allowed": False,
    "native_support_opened": False,
}


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def digest_value(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def digest_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise TypeError(f"{rel(path)} must contain a JSON object")
    return data


def git_head() -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def git_status_short(pathspec: str) -> str:
    completed = subprocess.run(
        ["git", "status", "--short", pathspec],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def output_digest(output: dict[str, Any]) -> str:
    excluded = {"generated_at", "output_digest", "git"}
    return digest_value(
        {key: value for key, value in output.items() if key not in excluded}
    )


def source_artifact(path: Path, artifact: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "path": rel(path),
        "sha256": digest_file(path),
        "status": None if artifact is None else artifact.get("status"),
        "output_digest": None if artifact is None else artifact.get("output_digest"),
    }


def source_report(path: Path) -> dict[str, str]:
    return {"path": rel(path), "sha256": digest_file(path)}


def source_pair(artifact: Path, report: Path) -> dict[str, str]:
    return {
        "source_artifact": rel(artifact),
        "source_report": rel(report),
        "source_sha256": digest_file(artifact),
        "source_report_sha256": digest_file(report),
    }


def support_lane_summary(n07: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "lane_id": lane["lane_id"],
            "withdrawal_depth": lane["withdrawal_depth"],
            "restoration_fraction": lane["restoration_fraction"],
            "final_A_support_retention": lane["final_A_support_retention"],
            "support_survival_threshold": lane["support_survival_threshold"],
            "support_survival_passed": lane["support_survival_passed"],
            "identity_support_outcome_tag": lane["identity_support_outcome_tag"],
            "lane_digest": lane["lane_digest"],
        }
        for lane in n07["withdrawal_lanes"]
    ]


def build_rows(
    n07: dict[str, Any],
    n09: dict[str, Any],
    n10_i12: dict[str, Any],
    n10_i15: dict[str, Any],
    n11: dict[str, Any],
    n12_closeout: dict[str, Any],
    n12_readiness: dict[str, Any],
) -> list[dict[str, Any]]:
    n07_pair = source_pair(N07_I13_OUTPUT, N07_I13_REPORT)
    n09_pair = source_pair(N09_I9_OUTPUT, N09_I9_REPORT)
    n10_i12_pair = source_pair(N10_I12_OUTPUT, N10_I12_REPORT)
    n10_i15_pair = source_pair(N10_I15_OUTPUT, N10_I15_REPORT)
    n11_pair = source_pair(N11_I12_OUTPUT, N11_I12_REPORT)
    n12_closeout_pair = source_pair(N12_CLOSEOUT_OUTPUT, N12_CLOSEOUT_REPORT)
    n12_readiness_pair = source_pair(N12_READINESS_OUTPUT, N12_READINESS_REPORT)
    support_matrix = n10_i12["support_state_matrix"]
    readiness_contracts = n12_readiness["matrix_result"]["phase8_ready_contracts"]
    deferred_blockers = n12_readiness["matrix_result"]["deferred_blockers"]

    return [
        {
            "row_id": "n13_i1_row_01_n07_support_withdrawal_baseline",
            "source_experiment": "N07",
            "source_iteration": 13,
            **n07_pair,
            "mechanism_name": "n07_support_survival_disruption_restoration_baseline",
            "mechanism_role": "support_state_baseline",
            "support_state_fields": {
                "support_area_id": n07["n10_handoff"]["support_area_id"],
                "support_area_digest": n07["n10_handoff"]["support_area_digest"],
                "source_n07_ceiling": n07["n10_handoff"]["source_n07_ceiling"],
                "source_c3_class": n07["n10_handoff"]["source_c3_class"],
                "lanes": support_lane_summary(n07),
            },
            "external_proxy_fields": [],
            "producer_decision_fields": [
                "withdrawal_depth",
                "restoration_fraction",
            ],
            "bookkeeping_fields": [
                "lane_digest",
                "n09_withdrawal_digest",
                "n10_consumption_role",
            ],
            "runtime_visible_surfaces": [
                "final_A_support_retention",
                "support_survival_threshold",
                "support_survival_passed",
                "withdrawal_depth",
                "restoration_fraction",
            ],
            "budget_surfaces": ["final_budget_error"],
            "response_surfaces": [],
            "support_condition_name": "support_retention_above_threshold",
            "target_derivation": (
                "candidate source rule: final_A_support_retention >= "
                "support_survival_threshold"
            ),
            "provisional_ap_level": "AP2",
            "provisional_self_maintenance_candidate": False,
            "claim_ceiling": "support_condition_inventory_only",
            "blocked_claims": BLOCKED_CLAIMS,
            "missing_gates": [
                "n13_support_schema_not_frozen",
                "support_derived_target_not_evaluated",
                "support_seeking_regulation_not_evaluated",
                "external_proxy_controls_not_run",
            ],
            "control_requirements": [
                "support_survival_relabel_as_identity_acceptance_blocked",
                "hidden_restoration_blocked",
                "budget_exact_required",
                "source_current_replay_required",
            ],
        },
        {
            "row_id": "n13_i1_row_02_n09_bounded_external_proxy_regulation",
            "source_experiment": "N09",
            "source_iteration": 9,
            **n09_pair,
            "mechanism_name": "n09_bounded_goal_proxy_regulation",
            "mechanism_role": "external_proxy_regulation_baseline",
            "support_state_fields": {
                "identity_support_digest": n09["identity_support_boundary"][
                    "identity_support_digest"
                ],
                "identity_support_outcome_tag": n09["identity_support_boundary"][
                    "identity_support_outcome_tag"
                ],
                "support_baseline_available": n09["identity_support_boundary"][
                    "baseline_available"
                ],
                "primary_blocker": n09["identity_support_boundary"][
                    "primary_blocker"
                ],
            },
            "external_proxy_fields": {
                "proxy_surface_digest": n09["n10_handoff_fields"][
                    "proxy_surface_digest"
                ],
                "error_policy_digest": n09["n10_handoff_fields"][
                    "error_policy_digest"
                ],
                "regulation_policy_digest": n09["n10_handoff_fields"][
                    "goal_proxy_regulation_policy_digest"
                ],
                "regulation_response_digest": n09["n10_handoff_fields"][
                    "regulation_response_digest"
                ],
            },
            "producer_decision_fields": [
                "goal_proxy_target_band",
                "response_thresholds",
                "producer_authorized_policy",
            ],
            "bookkeeping_fields": [
                "proxy_surface_digest_chain",
                "repeated_regulation_response_digests",
                "source_candidate_set_digest",
            ],
            "runtime_visible_surfaces": [
                "proxy_measurement",
                "proxy_error",
                "bounded_response",
                "perturbation_recovery_to_band",
            ],
            "budget_surfaces": ["node_plus_packet_budget_error"],
            "response_surfaces": [
                "gpr5_cycle_count",
                "bounded_repeated_regulation",
                "perturbation_recovered_to_band",
            ],
            "support_condition_name": "none_external_proxy_only",
            "target_derivation": "external proxy target declared by N09 fixtures",
            "provisional_ap_level": "AP1",
            "provisional_self_maintenance_candidate": False,
            "claim_ceiling": n09["claim_ceiling"],
            "blocked_claims": BLOCKED_CLAIMS,
            "missing_gates": [
                "support_condition_not_derived_from_source_current_support_state",
                "identity_support_baseline_missing_in_original_n09_closeout",
                "external_proxy_control_required",
            ],
            "control_requirements": [
                "external_proxy_relabel_blocked",
                "semantic_goal_ownership_relabel_blocked",
                "agency_relabel_blocked",
                "budget_ambiguity_blocked",
            ],
        },
        {
            "row_id": "n13_i1_row_03_n10_support_sensitive_matrix",
            "source_experiment": "N10",
            "source_iteration": 12,
            **n10_i12_pair,
            "mechanism_name": "n10_support_sensitive_full_composition_matrix",
            "mechanism_role": "support_sensitive_integration_baseline",
            "support_state_fields": {
                "matrix_states": n10_i12["hypothesis_b_closeout"]["matrix_states"],
                "support_sensitive_rule": n10_i12["hypothesis_b_closeout"][
                    "support_sensitive_rule"
                ],
                "support_state_matrix": support_matrix,
            },
            "external_proxy_fields": [
                "N09 bounded proxy regulation consumed as source artifact"
            ],
            "producer_decision_fields": [
                "support-state matrix row selection",
                "integration allowance by support state",
            ],
            "bookkeeping_fields": [
                "matrix_row_digest",
                "source_row_digest",
                "hypothesis_b_closeout_digest",
            ],
            "runtime_visible_surfaces": [
                "support_state_tag",
                "integration_allowed",
                "integration_outcome_tag",
                "primary_blocker",
            ],
            "budget_surfaces": ["budget_error_zero"],
            "response_surfaces": [
                "composition_preserved",
                "composition_blocked_or_downgraded",
                "composition_restoration_gated_resume",
            ],
            "support_condition_name": "support_state_valid_for_composition",
            "target_derivation": (
                "support-sensitive rule from N10 matrix: intact, mild, and "
                "explicit-restoration states may compose; disrupted support "
                "blocks or downgrades"
            ),
            "provisional_ap_level": "AP2",
            "provisional_self_maintenance_candidate": False,
            "claim_ceiling": n10_i12["hypothesis_b_closeout"]["positive_scope"],
            "blocked_claims": BLOCKED_CLAIMS,
            "missing_gates": [
                "n13_support_derived_target_not_isolated",
                "external_proxy_and_hidden_target_controls_not_run",
                "support_seeking_response_not_evaluated",
            ],
            "control_requirements": [
                "disrupted_support_blocks",
                "explicit_restoration_required",
                "artifact_only_replay",
                "claim_promotion_blocked",
            ],
        },
        {
            "row_id": "n13_i1_row_04_n10_final_handoff",
            "source_experiment": "N10",
            "source_iteration": 15,
            **n10_i15_pair,
            "mechanism_name": "n10_bounded_artifact_only_support_sensitive_handoff",
            "mechanism_role": "bounded_artifact_only_integration_handoff",
            "support_state_fields": {
                "support_sensitive_integration_supported": n10_i15[
                    "n10_final_closeout"
                ]["support_sensitive_integration_supported"],
                "bounded_artifact_only_agentic_like_integration_supported": n10_i15[
                    "n10_final_closeout"
                ]["bounded_artifact_only_agentic_like_integration_supported"],
            },
            "external_proxy_fields": [
                "N09 goal-proxy regulation remains producer/artifact mediated"
            ],
            "producer_decision_fields": [
                "N10 artifact-only integration handoff",
                "native contract handoff ordering",
            ],
            "bookkeeping_fields": ["n11_consumption_handoff", "phase8_native_absorption_handoff"],
            "runtime_visible_surfaces": [
                "support-sensitive integration supported",
                "native support flags false",
            ],
            "budget_surfaces": ["cross-cutting budget and replay contract"],
            "response_surfaces": ["bounded artifact-only composition"],
            "support_condition_name": "support_sensitive_integration_handoff",
            "target_derivation": "handoff record only; no N13 target derived yet",
            "provisional_ap_level": "AP2",
            "provisional_self_maintenance_candidate": False,
            "claim_ceiling": n10_i15["n10_final_closeout"]["final_n10_ceiling"],
            "blocked_claims": BLOCKED_CLAIMS,
            "missing_gates": [
                "n13_schema_not_frozen",
                "support_derived_target_not_evaluated",
                "native_support_not_opened",
            ],
            "control_requirements": [
                "artifact_only_replay",
                "native_support_relabel_blocked",
                "agency_relabel_blocked",
            ],
        },
        {
            "row_id": "n13_i1_row_05_n11_gali7_artifact_envelope",
            "source_experiment": "N11",
            "source_iteration": 12,
            **n11_pair,
            "mechanism_name": "n11_gali7_artifact_only_generalization_envelope",
            "mechanism_role": "generalization_envelope",
            "support_state_fields": {
                "final_supported_gali_ceiling": n11["final_supported_gali_ceiling"],
                "final_claim_ceiling": n11["final_claim_ceiling"],
                "artifact_only": n11["result_mediation"]["artifact_only"],
                "fully_native": n11["result_mediation"]["fully_native"],
            },
            "external_proxy_fields": [],
            "producer_decision_fields": ["artifact-only GALI7 closeout"],
            "bookkeeping_fields": ["output_digest", "source_artifacts"],
            "runtime_visible_surfaces": ["artifact replay envelope"],
            "budget_surfaces": ["artifact replay budget gates"],
            "response_surfaces": ["generalization envelope only"],
            "support_condition_name": "none_generalization_envelope_only",
            "target_derivation": "no support target; envelope source boundary",
            "provisional_ap_level": "AP0",
            "provisional_self_maintenance_candidate": False,
            "claim_ceiling": n11["final_claim_ceiling"],
            "blocked_claims": BLOCKED_CLAIMS,
            "missing_gates": [
                "support_condition_not_defined",
                "support_seeking_regulation_not_evaluated",
            ],
            "control_requirements": [
                "artifact_only_replay_not_native_support",
                "agentic_like_integration_not_agency",
            ],
        },
        {
            "row_id": "n13_i1_row_06_n12_phase8_readiness_inputs",
            "source_experiment": "N12",
            "source_iteration": 7,
            **n12_readiness_pair,
            "mechanism_name": "n12_route_memory_and_response_magnitude_readiness_inputs",
            "mechanism_role": "phase8_ready_input_records",
            "support_state_fields": {
                "phase8_ready_contracts": readiness_contracts,
                "deferred_blockers": deferred_blockers,
            },
            "external_proxy_fields": [
                "response magnitude is bounded/envelope-gated, not goal ownership"
            ],
            "producer_decision_fields": [
                "N12 readiness matrix contract selection",
                "default-off native policy planning",
            ],
            "bookkeeping_fields": [
                "controls_summary",
                "telemetry_summary",
                "test_gate_summary",
            ],
            "runtime_visible_surfaces": [
                "route conductance memory contract",
                "response magnitude policy contract",
            ],
            "budget_surfaces": [
                "route conductance memory budget surface",
                "node-plus-packet response budget surface",
            ],
            "response_surfaces": ["bounded response magnitude policy readiness"],
            "support_condition_name": "none_phase8_readiness_input_only",
            "target_derivation": (
                "N12 readiness input only; no N13 support target derived yet"
            ),
            "provisional_ap_level": "AP1",
            "provisional_self_maintenance_candidate": False,
            "claim_ceiling": "phase8_ready_contract_input_only",
            "blocked_claims": BLOCKED_CLAIMS,
            "missing_gates": [
                "phase8_not_opened",
                "support_condition_not_derived",
                "support_seeking_controls_not_run",
            ],
            "control_requirements": [
                "phase8_readiness_not_phase8_implementation",
                "native_support_relabel_blocked",
                "intention_relabel_blocked",
                "goal_ownership_relabel_blocked",
            ],
        },
        {
            "row_id": "n13_i1_row_07_n12_closeout_boundary",
            "source_experiment": "N12",
            "source_iteration": 8,
            **n12_closeout_pair,
            "mechanism_name": "n12_closeout_n13_boundary",
            "mechanism_role": "handoff_and_claim_boundary",
            "support_state_fields": {
                "n13_allowed_inputs": n12_closeout["n13_handoff"][
                    "allowed_inputs"
                ],
                "n13_blocked_inputs": n12_closeout["n13_handoff"][
                    "blocked_inputs"
                ],
                "final_nat_levels": n12_closeout["final_nat_levels"],
            },
            "external_proxy_fields": [],
            "producer_decision_fields": ["N13 starts support-seeking, not identity-seeking"],
            "bookkeeping_fields": ["final_claim_boundary", "checks"],
            "runtime_visible_surfaces": ["handoff boundary"],
            "budget_surfaces": ["no implementation checks"],
            "response_surfaces": [],
            "support_condition_name": "n13_handoff_boundary",
            "target_derivation": (
                "N13 may consume support-survival evidence but not identity acceptance"
            ),
            "provisional_ap_level": "AP0",
            "provisional_self_maintenance_candidate": False,
            "claim_ceiling": "handoff_boundary_only",
            "blocked_claims": BLOCKED_CLAIMS,
            "missing_gates": [
                "n13_inventory_not_closed",
                "support_derived_target_not_evaluated",
            ],
            "control_requirements": [
                "identity_acceptance_input_blocked",
                "agency_input_blocked",
                "fully_native_integration_input_blocked",
            ],
        },
    ]


def build_output() -> dict[str, Any]:
    n07 = load_json(N07_I13_OUTPUT)
    n09 = load_json(N09_I9_OUTPUT)
    n10_i12 = load_json(N10_I12_OUTPUT)
    n10_i15 = load_json(N10_I15_OUTPUT)
    n11 = load_json(N11_I12_OUTPUT)
    n12_closeout = load_json(N12_CLOSEOUT_OUTPUT)
    n12_readiness = load_json(N12_READINESS_OUTPUT)

    rows = build_rows(n07, n09, n10_i12, n10_i15, n11, n12_closeout, n12_readiness)
    source_artifacts = {
        rel(N07_I13_OUTPUT): source_artifact(N07_I13_OUTPUT, n07),
        rel(N09_I9_OUTPUT): source_artifact(N09_I9_OUTPUT, n09),
        rel(N10_I12_OUTPUT): source_artifact(N10_I12_OUTPUT, n10_i12),
        rel(N10_I15_OUTPUT): source_artifact(N10_I15_OUTPUT, n10_i15),
        rel(N11_I12_OUTPUT): source_artifact(N11_I12_OUTPUT, n11),
        rel(N12_CLOSEOUT_OUTPUT): source_artifact(N12_CLOSEOUT_OUTPUT, n12_closeout),
        rel(N12_READINESS_OUTPUT): source_artifact(N12_READINESS_OUTPUT, n12_readiness),
    }
    source_reports = {
        rel(N07_I13_REPORT): source_report(N07_I13_REPORT),
        rel(N09_I9_REPORT): source_report(N09_I9_REPORT),
        rel(N10_I12_REPORT): source_report(N10_I12_REPORT),
        rel(N10_I15_REPORT): source_report(N10_I15_REPORT),
        rel(N11_I12_REPORT): source_report(N11_I12_REPORT),
        rel(N12_CLOSEOUT_REPORT): source_report(N12_CLOSEOUT_REPORT),
        rel(N12_READINESS_REPORT): source_report(N12_READINESS_REPORT),
    }
    ap_counts = {
        level: sum(1 for row in rows if row["provisional_ap_level"] == level)
        for level in ["AP0", "AP1", "AP2", "AP3"]
    }
    support_rows = [
        row["row_id"]
        for row in rows
        if row["support_condition_name"] not in {
            "none_external_proxy_only",
            "none_generalization_envelope_only",
            "none_phase8_readiness_input_only",
            "n13_handoff_boundary",
        }
    ]
    boundary_rows = [
        row["row_id"]
        for row in rows
        if row["mechanism_role"]
        in {"generalization_envelope", "handoff_and_claim_boundary"}
    ]
    external_proxy_rows = [
        row["row_id"]
        for row in rows
        if row["support_condition_name"] == "none_external_proxy_only"
    ]
    checks = {
        "source_artifacts_all_present": all(
            artifact["sha256"] for artifact in source_artifacts.values()
        ),
        "source_reports_all_present": all(
            report["sha256"] for report in source_reports.values()
        ),
        "every_row_has_source_sha256": all(row["source_sha256"] for row in rows),
        "every_row_has_source_report_sha256": all(
            row["source_report_sha256"] for row in rows
        ),
        "every_row_has_support_state_fields": all(
            row["support_state_fields"] is not None for row in rows
        ),
        "support_condition_rows_present": bool(support_rows),
        "boundary_rows_present": bool(boundary_rows),
        "external_proxy_rows_present": bool(external_proxy_rows),
        "n10_support_matrix_present": any(
            row["mechanism_name"] == "n10_support_sensitive_full_composition_matrix"
            for row in rows
        ),
        "n12_handoff_boundary_present": any(
            row["mechanism_name"] == "n12_closeout_n13_boundary" for row in rows
        ),
        "identity_acceptance_not_consumed": "identity acceptance"
        in n12_closeout["n13_handoff"]["blocked_inputs"],
        "no_ap3_claimed_in_iteration_1": ap_counts.get("AP3", 0) == 0,
        "native_support_not_opened": CLAIM_FLAGS_FORCED_FALSE[
            "native_support_opened"
        ]
        is False,
        "phase8_not_opened": n12_closeout["closeout_result"]["phase8_opened"]
        is False,
        "claim_flags_all_false": all(
            value is False for value in CLAIM_FLAGS_FORCED_FALSE.values()
        ),
        "src_diff_empty": git_status_short("src") == "",
    }
    output = {
        "experiment": "N13",
        "iteration": 1,
        "purpose": "support_condition_inventory",
        "schema": "n13_support_condition_inventory_v1",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "passed" if all(checks.values()) else "failed",
        "target_ap_ceiling": "AP3",
        "iteration_ceiling": "AP2_inventory_only",
        "n13_inventory_rows": rows,
        "inventory_summary": {
            "row_count": len(rows),
            "provisional_ap_counts": ap_counts,
            "support_condition_rows": support_rows,
            "boundary_rows": boundary_rows,
            "external_proxy_rows": external_proxy_rows,
            "phase8_ready_contract_inputs": n12_readiness["matrix_result"][
                "phase8_ready_contracts"
            ],
            "theory_sensitive_blockers": n12_readiness["matrix_result"][
                "deferred_blockers"
            ],
        },
        "claim_flags_forced_false": CLAIM_FLAGS_FORCED_FALSE,
        "blocked_inputs": n12_closeout["n13_handoff"]["blocked_inputs"],
        "checks": checks,
        "source_artifacts": source_artifacts,
        "source_reports": source_reports,
        "artifact_reproducibility": {
            "generated_at_fixed": GENERATED_AT,
            "wall_clock_timestamp_in_file": False,
            "output_digest_excludes_generated_at_and_git": True,
        },
        "git": {
            "head": git_head(),
            "src_status_short": git_status_short("src"),
        },
    }
    output["output_digest"] = output_digest(output)
    return output


def write_report(output: dict[str, Any]) -> None:
    lines = [
        "# N13 Support-Condition Inventory",
        "",
        "## Status",
        "",
        f"Status: `{output['status']}`.",
        "",
        "```text",
        f"target_ap_ceiling = {output['target_ap_ceiling']}",
        f"iteration_ceiling = {output['iteration_ceiling']}",
        "phase8_opened = false",
        "native_support_opened = false",
        "identity_acceptance_opened = false",
        "agency_claim_opened = false",
        "```",
        "",
        "Iteration 1 is an inventory only. It records support-state, external",
        "proxy, producer-decision, budget, replay, and claim-boundary fields",
        "without assigning AP3 self-maintenance support.",
        "",
        "## Inventory Rows",
        "",
        "| Row | Mechanism | Role | AP | Self-maintenance candidate | Source |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in output["n13_inventory_rows"]:
        lines.append(
            "| "
            f"`{row['row_id']}` | "
            f"`{row['mechanism_name']}` | "
            f"`{row['mechanism_role']}` | "
            f"`{row['provisional_ap_level']}` | "
            f"`{str(row['provisional_self_maintenance_candidate']).lower()}` | "
            f"`{row['source_artifact']}` |"
        )
    lines.extend(
        [
            "",
            "## Summary",
            "",
            "```json",
            json.dumps(output["inventory_summary"], indent=2, sort_keys=True),
            "```",
            "",
            "## Blocked Inputs",
            "",
            "```json",
            json.dumps(output["blocked_inputs"], indent=2, sort_keys=True),
            "```",
            "",
            "## Checks",
            "",
            "```json",
            json.dumps(output["checks"], indent=2, sort_keys=True),
            "```",
            "",
            "## Claim Boundary",
            "",
            "```text",
            "support-seeking regulation != agency",
            "self-maintenance candidate != selfhood",
            "support survival != identity acceptance",
            "support-derived target != semantic goal ownership",
            "bounded response != intention",
            "artifact replay != native support",
            "N12 NAT4 readiness != Phase 8 implementation",
            "```",
            "",
            "## Output Digest",
            "",
            "```text",
            output["output_digest"],
            "```",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    output = build_output()
    OUTPUT_PATH.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    write_report(output)
    if output["status"] != "passed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()

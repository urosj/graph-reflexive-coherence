#!/usr/bin/env python3
"""Build N15 Iteration 1 proxy source inventory."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N15-lgrc-endogenous-proxy-formation"
OUTPUTS = EXPERIMENT / "outputs"
REPORTS = EXPERIMENT / "reports"

ROADMAP = ROOT / "experiments" / "N12-N18-LGRC-AgencyPrerequisitesRoadmap.md"
HANDOFF = ROOT / "experiments" / "N12-N18-LGRC-AgencyPrerequisitesHandoff.md"

N08_MEM6_OUTPUT = (
    ROOT
    / "experiments"
    / "2026-05-N08-lgrc-memory-trail-affordance"
    / "outputs"
    / "n08_iteration_8_mem6_closeout.json"
)
N08_MEM6_REPORT = (
    ROOT
    / "experiments"
    / "2026-05-N08-lgrc-memory-trail-affordance"
    / "reports"
    / "n08_iteration_8_mem6_closeout.md"
)
N09_GPR6_OUTPUT = (
    ROOT
    / "experiments"
    / "2026-05-N09-lgrc-goal-proxy-regulation"
    / "outputs"
    / "n09_iteration_9_gpr6_closeout.json"
)
N09_GPR6_REPORT = (
    ROOT
    / "experiments"
    / "2026-05-N09-lgrc-goal-proxy-regulation"
    / "reports"
    / "n09_iteration_9_gpr6_closeout.md"
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
N13_TARGET_OUTPUT = (
    ROOT
    / "experiments"
    / "2026-06-N13-lgrc-self-maintenance-and-support-seeking-regulation"
    / "outputs"
    / "n13_support_derived_target_candidate.json"
)
N13_TARGET_REPORT = (
    ROOT
    / "experiments"
    / "2026-06-N13-lgrc-self-maintenance-and-support-seeking-regulation"
    / "reports"
    / "n13_support_derived_target_candidate.md"
)
N13_REGULATION_OUTPUT = (
    ROOT
    / "experiments"
    / "2026-06-N13-lgrc-self-maintenance-and-support-seeking-regulation"
    / "outputs"
    / "n13_support_seeking_regulation_candidate.json"
)
N13_REGULATION_REPORT = (
    ROOT
    / "experiments"
    / "2026-06-N13-lgrc-self-maintenance-and-support-seeking-regulation"
    / "reports"
    / "n13_support_seeking_regulation_candidate.md"
)
N13_CLOSEOUT_OUTPUT = (
    ROOT
    / "experiments"
    / "2026-06-N13-lgrc-self-maintenance-and-support-seeking-regulation"
    / "outputs"
    / "n13_closeout_and_handoff.json"
)
N13_CLOSEOUT_REPORT = (
    ROOT
    / "experiments"
    / "2026-06-N13-lgrc-self-maintenance-and-support-seeking-regulation"
    / "reports"
    / "n13_closeout_and_handoff.md"
)
N14_FOLLOWOUT_OUTPUT = (
    ROOT
    / "experiments"
    / "2026-06-N14-lgrc-consequence-sensitive-route-selection"
    / "outputs"
    / "n14_route_conditioned_followout_probe.json"
)
N14_FOLLOWOUT_REPORT = (
    ROOT
    / "experiments"
    / "2026-06-N14-lgrc-consequence-sensitive-route-selection"
    / "reports"
    / "n14_route_conditioned_followout_probe.md"
)
N14_BOUNDARY_OUTPUT = (
    ROOT
    / "experiments"
    / "2026-06-N14-lgrc-consequence-sensitive-route-selection"
    / "outputs"
    / "n14_claim_boundary_record.json"
)
N14_BOUNDARY_REPORT = (
    ROOT
    / "experiments"
    / "2026-06-N14-lgrc-consequence-sensitive-route-selection"
    / "reports"
    / "n14_claim_boundary_record.md"
)
N14_CLOSEOUT_OUTPUT = (
    ROOT
    / "experiments"
    / "2026-06-N14-lgrc-consequence-sensitive-route-selection"
    / "outputs"
    / "n14_closeout_and_handoff.json"
)
N14_CLOSEOUT_REPORT = (
    ROOT
    / "experiments"
    / "2026-06-N14-lgrc-consequence-sensitive-route-selection"
    / "reports"
    / "n14_closeout_and_handoff.md"
)

OUTPUT_PATH = OUTPUTS / "n15_proxy_source_inventory.json"
REPORT_PATH = REPORTS / "n15_proxy_source_inventory.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N15-lgrc-endogenous-proxy-formation/"
    "scripts/build_n15_proxy_source_inventory.py"
)
GENERATED_AT = "2026-06-16T00:00:00+00:00"

BLOCKED_CLAIMS = [
    "agency",
    "intention",
    "semantic_choice",
    "semantic_goal_ownership",
    "semantic_goal_understanding",
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
    "semantic_choice_claim_allowed": False,
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

ARC_METHOD_MAPPING = {
    "classification_of_becoming": (
        "classify source rows at the lowest supported rung; separate local "
        "observation tags, reusable construction inputs, AP5 candidates, and "
        "blocked relabels"
    ),
    "interrogation_of_becoming": (
        "treat later target derivation and controls as bounded questions, not "
        "proof of semantic goal ownership"
    ),
    "naturalization_of_becoming": (
        "keep direct historic, constructed, readiness-only, and native-support "
        "evidence separate"
    ),
    "cultivation_of_becoming": (
        "cultivate the missing target-formation function rather than optimizing "
        "a local proxy"
    ),
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


def contains_absolute_path(value: Any) -> bool:
    if isinstance(value, str):
        return value.startswith(("/", "\\")) or (
            len(value) > 2 and value[1] == ":" and value[2] in {"/", "\\"}
        )
    if isinstance(value, dict):
        return any(contains_absolute_path(item) for item in value.values())
    if isinstance(value, list):
        return any(contains_absolute_path(item) for item in value)
    return False


def row(
    *,
    row_id: str,
    source_experiment: str,
    source_iteration: str,
    source_artifact: Path,
    source_report: Path,
    mechanism_name: str,
    mechanism_role: str,
    evidence_strategy: str,
    old_best_claim_inputs: list[str],
    direct_historic_support_status: str,
    runtime_state_surface_id: str,
    support_state_descriptor: str,
    identity_condition_descriptor: str,
    memory_state_descriptor: str,
    regulation_state_descriptor: str,
    provisional_ap_level: str,
    provisional_claim_ceiling: str,
    source_role_classification: str,
    missing_gates: list[str],
) -> dict[str, Any]:
    return {
        "row_id": row_id,
        "source_experiment": source_experiment,
        "source_iteration": source_iteration,
        "source_artifact": rel(source_artifact),
        "source_report": rel(source_report),
        "source_sha256": digest_file(source_artifact),
        "source_report_sha256": digest_file(source_report),
        "mechanism_name": mechanism_name,
        "mechanism_role": mechanism_role,
        "evidence_strategy": evidence_strategy,
        "old_best_claim_inputs": old_best_claim_inputs,
        "direct_historic_support_status": direct_historic_support_status,
        "runtime_state_surface_id": runtime_state_surface_id,
        "state_source_window": source_iteration,
        "source_current": "not_validated_until_iteration_2_schema",
        "support_state_descriptor": support_state_descriptor,
        "identity_condition_descriptor": identity_condition_descriptor,
        "memory_state_descriptor": memory_state_descriptor,
        "regulation_state_descriptor": regulation_state_descriptor,
        "declared_proxy_absent": "not_validated_until_iteration_2_schema",
        "external_target_input_absent": "not_validated_until_iteration_2_schema",
        "endogenous_derivation_policy": "not_frozen_until_iteration_2_schema",
        "target_condition_generated_at": "not_generated_until_iteration_3",
        "target_condition_surface": "not_generated_until_iteration_3",
        "target_center": "not_generated_until_iteration_3",
        "target_band": "not_generated_until_iteration_3",
        "target_tolerance": "not_generated_until_iteration_3",
        "drift_bound": "not_frozen_until_iteration_2_schema",
        "drift_update_rule": "not_frozen_until_iteration_2_schema",
        "drift_clamp_policy": "not_frozen_until_iteration_2_schema",
        "dependency_trace": "not_constructed_until_iteration_3",
        "budget_cost_surface": "source_inventory_digest_and_row_count_only",
        "budget_units": "not_frozen_until_iteration_2_schema",
        "budget_validity": "not_validated_until_iteration_2_schema",
        "replay_digest_inputs": "not_constructed_until_iteration_3",
        "replay_digest_algorithm": "sha256_canonical_json_pending_iteration_2",
        "idempotency_digest_plan": "not_frozen_until_iteration_2_schema",
        "fully_native_integration_opened": False,
        "artifact_only_replay_status": "not_run_until_iteration_6",
        "snapshot_load_status": "not_run_until_iteration_6",
        "order_inversion_replay_status": "not_run_until_iteration_6",
        "externally_injected_target_control": "required_before_ap5",
        "hidden_target_derivation_control": "required_before_ap5",
        "post_hoc_proxy_formation_control": "required_before_ap5",
        "unbounded_target_drift_control": "required_before_ap5",
        "budget_surface_ambiguity_control": "required_before_ap5",
        "semantic_goal_ownership_relabel_control": "required_before_ap5",
        "identity_acceptance_relabel_control": "required_before_ap5",
        "native_support_relabel_control": "required_before_ap5",
        "source_role_classification": source_role_classification,
        "arc_method_mapping": ARC_METHOD_MAPPING,
        "provisional_ap_level": provisional_ap_level,
        "provisional_claim_ceiling": provisional_claim_ceiling,
        "blocked_claims": BLOCKED_CLAIMS,
        "missing_gates": missing_gates,
    }


def build_rows() -> list[dict[str, Any]]:
    return [
        row(
            row_id="n15_i1_row_01_n13_support_derived_target_candidate",
            source_experiment="N13",
            source_iteration="iteration_3_support_derived_target_candidate",
            source_artifact=N13_TARGET_OUTPUT,
            source_report=N13_TARGET_REPORT,
            mechanism_name="source_current_support_derived_target_rule",
            mechanism_role="direct_historic_target_formation_support",
            evidence_strategy="direct_historic_evidence_allowed_but_not_ap5",
            old_best_claim_inputs=[],
            direct_historic_support_status=(
                "direct_support_for_support_derived_target_candidate_at_ap2_scope"
            ),
            runtime_state_surface_id="n13_support_target_runtime_state_surface",
            support_state_descriptor=(
                "support retention threshold rule from source-current lanes"
            ),
            identity_condition_descriptor=(
                "support/identity-condition descriptor only; no identity acceptance"
            ),
            memory_state_descriptor="not_present",
            regulation_state_descriptor=(
                "pending support-error response in later N13 iterations"
            ),
            provisional_ap_level="AP2",
            provisional_claim_ceiling="support_derived_target_candidate_only",
            source_role_classification="direct_historic_support",
            missing_gates=[
                "final_ap5_not_assigned",
                "n15_derivation_policy_not_frozen",
                "n15_replay_controls_not_run",
                "semantic_goal_ownership_blocked",
            ],
        ),
        row(
            row_id="n15_i1_row_02_n13_support_seeking_regulation_candidate",
            source_experiment="N13",
            source_iteration="iteration_4_support_seeking_regulation_candidate",
            source_artifact=N13_REGULATION_OUTPUT,
            source_report=N13_REGULATION_REPORT,
            mechanism_name="support_error_bounded_response_candidate",
            mechanism_role="support_regulation_axis_source",
            evidence_strategy="old_best_claims_construction_input",
            old_best_claim_inputs=["N13_AP3_candidate_support_regulation_axis"],
            direct_historic_support_status=(
                "indirect_support_for_proxy_formation_via_support_error_response"
            ),
            runtime_state_surface_id="n13_support_error_response_surface",
            support_state_descriptor="support error and support trend surface",
            identity_condition_descriptor=(
                "support condition only; identity acceptance blocked"
            ),
            memory_state_descriptor="not_present",
            regulation_state_descriptor="bounded response magnitude candidate",
            provisional_ap_level="AP3_candidate",
            provisional_claim_ceiling=(
                "artifact_level_ap3_candidate_pending_controls"
            ),
            source_role_classification="old_best_claim_input",
            missing_gates=[
                "n15_target_generation_not_built",
                "n15_dependency_trace_not_built",
                "native_support_not_opened",
            ],
        ),
        row(
            row_id="n15_i1_row_03_n13_closeout_ap3",
            source_experiment="N13",
            source_iteration="iteration_8_closeout_and_handoff",
            source_artifact=N13_CLOSEOUT_OUTPUT,
            source_report=N13_CLOSEOUT_REPORT,
            mechanism_name="n13_ap3_support_seeking_regulation_closeout",
            mechanism_role="old_best_ap3_support_axis",
            evidence_strategy="old_best_claims_construction_input",
            old_best_claim_inputs=["N13_AP3_final_support_seeking_regulation"],
            direct_historic_support_status="no_direct_ap5_support_claimed",
            runtime_state_surface_id="n13_final_ap3_support_axis",
            support_state_descriptor="final AP3 support-seeking regulation",
            identity_condition_descriptor=(
                "self-maintenance candidate only; selfhood and identity acceptance blocked"
            ),
            memory_state_descriptor="not_present",
            regulation_state_descriptor="support-error bounded response candidate",
            provisional_ap_level="AP3",
            provisional_claim_ceiling=(
                "artifact_level_ap3_self_maintenance_candidate_support_seeking_regulation"
            ),
            source_role_classification="old_best_claim_input",
            missing_gates=[
                "ap5_target_generation_not_present_in_n13_closeout",
                "semantic_goal_ownership_blocked",
                "native_support_not_opened",
            ],
        ),
        row(
            row_id="n15_i1_row_04_n14_closeout_ap4",
            source_experiment="N14",
            source_iteration="iteration_8_closeout_and_handoff",
            source_artifact=N14_CLOSEOUT_OUTPUT,
            source_report=N14_CLOSEOUT_REPORT,
            mechanism_name="n14_ap4_consequence_sensitive_selection_closeout",
            mechanism_role="old_best_ap4_selection_axis",
            evidence_strategy="old_best_claims_construction_input",
            old_best_claim_inputs=["N14_AP4_consequence_sensitive_selection"],
            direct_historic_support_status="no_direct_ap5_support_claimed",
            runtime_state_surface_id="n14_final_ap4_selection_axis",
            support_state_descriptor=(
                "constructed route-conditioned support followout caveated"
            ),
            identity_condition_descriptor=(
                "memory-sensitive route choice only; identity acceptance blocked"
            ),
            memory_state_descriptor="observed route-specific memory consequence",
            regulation_state_descriptor=(
                "constructed route-conditioned regulation followout"
            ),
            provisional_ap_level="AP4",
            provisional_claim_ceiling=(
                "artifact_level_ap4_consequence_sensitive_route_selection_candidate_with_constructed_route_conditioned_support_regulation_followout"
            ),
            source_role_classification="old_best_claim_input",
            missing_gates=[
                "target_condition_generation_not_present_in_n14",
                "ap5_derivation_trace_not_built",
                "semantic_goal_ownership_blocked",
            ],
        ),
        row(
            row_id="n15_i1_row_05_n14_constructed_followout",
            source_experiment="N14",
            source_iteration="iteration_6c_route_conditioned_followout_probe",
            source_artifact=N14_FOLLOWOUT_OUTPUT,
            source_report=N14_FOLLOWOUT_REPORT,
            mechanism_name="constructed_route_conditioned_support_regulation_followout",
            mechanism_role="constructed_followout_context_source",
            evidence_strategy="old_best_claims_construction_context",
            old_best_claim_inputs=["N14_constructed_followout_context"],
            direct_historic_support_status=(
                "constructed_followout_support_not_upstream_observed_support"
            ),
            runtime_state_surface_id="n14_constructed_followout_surface",
            support_state_descriptor="constructed support followout by route",
            identity_condition_descriptor="not_identity_acceptance",
            memory_state_descriptor="route id context only",
            regulation_state_descriptor="constructed regulation followout by route",
            provisional_ap_level="AP4_context",
            provisional_claim_ceiling=(
                "constructed_followout_context_not_upstream_observed_evidence"
            ),
            source_role_classification="constructed_context",
            missing_gates=[
                "upstream_observed_route_conditioned_support_missing",
                "upstream_observed_route_conditioned_regulation_missing",
                "native_support_not_opened",
            ],
        ),
        row(
            row_id="n15_i1_row_06_n14_claim_boundary",
            source_experiment="N14",
            source_iteration="iteration_7_claim_boundary_ap4_classification",
            source_artifact=N14_BOUNDARY_OUTPUT,
            source_report=N14_BOUNDARY_REPORT,
            mechanism_name="n14_claim_boundary_and_blocked_input_record",
            mechanism_role="claim_boundary_source",
            evidence_strategy="boundary_and_blocked_input_audit",
            old_best_claim_inputs=[],
            direct_historic_support_status="not_target_formation_evidence",
            runtime_state_surface_id="n14_claim_boundary_surface",
            support_state_descriptor="boundary only",
            identity_condition_descriptor="identity acceptance blocked",
            memory_state_descriptor="boundary only",
            regulation_state_descriptor="boundary only",
            provisional_ap_level="AP0_boundary",
            provisional_claim_ceiling="claim_boundary_record_only",
            source_role_classification="boundary_source",
            missing_gates=[
                "not_ap5_evidence",
                "blocked_input_audit_required_for_n15",
            ],
        ),
        row(
            row_id="n15_i1_row_07_n08_memory_context",
            source_experiment="N08",
            source_iteration="iteration_8_mem6_closeout",
            source_artifact=N08_MEM6_OUTPUT,
            source_report=N08_MEM6_REPORT,
            mechanism_name="serialized_route_memory_trail_affordance",
            mechanism_role="memory_context_axis_source",
            evidence_strategy="old_best_claims_construction_input",
            old_best_claim_inputs=["N08_route_memory_context"],
            direct_historic_support_status="not_direct_target_formation_evidence",
            runtime_state_surface_id="n08_route_memory_context_surface",
            support_state_descriptor="not_present",
            identity_condition_descriptor="not_identity_acceptance",
            memory_state_descriptor="route memory/trail affordance context",
            regulation_state_descriptor="not_present",
            provisional_ap_level="AP2",
            provisional_claim_ceiling=(
                "artifact_only_route_memory_or_trail_affordance_candidate"
            ),
            source_role_classification="old_best_claim_input",
            missing_gates=[
                "memory_context_not_target_generation",
                "native_memory_support_not_opened",
            ],
        ),
        row(
            row_id="n15_i1_row_08_n09_bounded_regulation_context",
            source_experiment="N09",
            source_iteration="iteration_9_gpr6_closeout",
            source_artifact=N09_GPR6_OUTPUT,
            source_report=N09_GPR6_REPORT,
            mechanism_name="bounded_goal_proxy_regulation",
            mechanism_role="bounded_regulation_context_source",
            evidence_strategy="old_best_claims_construction_input",
            old_best_claim_inputs=["N09_bounded_regulation_context"],
            direct_historic_support_status=(
                "external_proxy_baseline_not_endogenous_proxy_support"
            ),
            runtime_state_surface_id="n09_bounded_regulation_context_surface",
            support_state_descriptor="support boundary recorded but externally proxied",
            identity_condition_descriptor="not_identity_acceptance",
            memory_state_descriptor="memory handoff digest context",
            regulation_state_descriptor="bounded repeated regulation context",
            provisional_ap_level="AP2",
            provisional_claim_ceiling="artifact_only_goal_proxy_regulation_candidate",
            source_role_classification="old_best_claim_input",
            missing_gates=[
                "external_proxy_baseline_must_not_be_relabelled",
                "endogenous_target_generation_not_present",
                "semantic_goal_ownership_blocked",
            ],
        ),
        row(
            row_id="n15_i1_row_09_n12_phase8_readiness",
            source_experiment="N12",
            source_iteration="iteration_7_phase8_readiness_matrix",
            source_artifact=N12_READINESS_OUTPUT,
            source_report=N12_READINESS_REPORT,
            mechanism_name="phase8_ready_route_memory_and_response_magnitude_contracts",
            mechanism_role="phase8_readiness_input_only",
            evidence_strategy="readiness_only_context",
            old_best_claim_inputs=["N12_NAT4_readiness_only_context"],
            direct_historic_support_status="readiness_only_not_ap5_support",
            runtime_state_surface_id="n12_phase8_readiness_surface",
            support_state_descriptor="not_runtime_support",
            identity_condition_descriptor="identity acceptance blocker remains",
            memory_state_descriptor="route conductance memory policy readiness",
            regulation_state_descriptor="response magnitude policy readiness",
            provisional_ap_level="AP0_readiness",
            provisional_claim_ceiling="phase8_ready_contracts_not_native_support",
            source_role_classification="readiness_only",
            missing_gates=[
                "phase8_implementation_not_opened",
                "native_supported_flags_false",
                "ap5_runtime_derivation_not_built",
            ],
        ),
    ]


def build_output() -> dict[str, Any]:
    n08_mem6 = load_json(N08_MEM6_OUTPUT)
    n09_gpr6 = load_json(N09_GPR6_OUTPUT)
    n12_readiness = load_json(N12_READINESS_OUTPUT)
    n13_target = load_json(N13_TARGET_OUTPUT)
    n13_regulation = load_json(N13_REGULATION_OUTPUT)
    n13_closeout = load_json(N13_CLOSEOUT_OUTPUT)
    n14_followout = load_json(N14_FOLLOWOUT_OUTPUT)
    n14_boundary = load_json(N14_BOUNDARY_OUTPUT)
    n14_closeout = load_json(N14_CLOSEOUT_OUTPUT)
    rows = build_rows()
    required_roles = {
        "direct_historic_target_formation_support",
        "support_regulation_axis_source",
        "old_best_ap3_support_axis",
        "old_best_ap4_selection_axis",
        "constructed_followout_context_source",
        "claim_boundary_source",
        "memory_context_axis_source",
        "bounded_regulation_context_source",
        "phase8_readiness_input_only",
    }
    observed_roles = {source_row["mechanism_role"] for source_row in rows}
    old_best_roles = {
        "old_best_ap3_support_axis",
        "old_best_ap4_selection_axis",
        "memory_context_axis_source",
        "bounded_regulation_context_source",
        "phase8_readiness_input_only",
    }
    checks = {
        "required_source_paths_exist": all(
            path.exists()
            for path in [
                N08_MEM6_OUTPUT,
                N08_MEM6_REPORT,
                N09_GPR6_OUTPUT,
                N09_GPR6_REPORT,
                N12_READINESS_OUTPUT,
                N12_READINESS_REPORT,
                N13_TARGET_OUTPUT,
                N13_TARGET_REPORT,
                N13_REGULATION_OUTPUT,
                N13_REGULATION_REPORT,
                N13_CLOSEOUT_OUTPUT,
                N13_CLOSEOUT_REPORT,
                N14_FOLLOWOUT_OUTPUT,
                N14_FOLLOWOUT_REPORT,
                N14_BOUNDARY_OUTPUT,
                N14_BOUNDARY_REPORT,
                N14_CLOSEOUT_OUTPUT,
                N14_CLOSEOUT_REPORT,
            ]
        ),
        "source_statuses_passed": all(
            source.get("status") == "passed"
            for source in [
                n12_readiness,
                n13_target,
                n13_regulation,
                n13_closeout,
                n14_followout,
                n14_boundary,
                n14_closeout,
            ]
        ),
        "legacy_sources_loaded": isinstance(n08_mem6, dict)
        and isinstance(n09_gpr6, dict),
        "every_row_has_source_sha256": all(
            source_row["source_sha256"] for source_row in rows
        ),
        "every_row_has_source_report_sha256": all(
            source_row["source_report_sha256"] for source_row in rows
        ),
        "required_roles_present": required_roles.issubset(observed_roles),
        "direct_historic_support_recorded": any(
            source_row["mechanism_role"] == "direct_historic_target_formation_support"
            and source_row["direct_historic_support_status"]
            == "direct_support_for_support_derived_target_candidate_at_ap2_scope"
            for source_row in rows
        ),
        "direct_historic_support_not_promoted_to_ap5": all(
            source_row["provisional_ap_level"] != "AP5"
            for source_row in rows
            if source_row["mechanism_role"]
            == "direct_historic_target_formation_support"
        ),
        "old_best_claim_inputs_recorded": old_best_roles.issubset(observed_roles),
        "n13_ap3_old_best_claim_present": n13_closeout["closeout_result"][
            "final_supported_ap_level"
        ]
        == "AP3"
        and n13_closeout["closeout_result"]["native_support_opened"] is False,
        "n14_ap4_old_best_claim_present": n14_closeout["closeout_result"][
            "final_supported_ap_level"
        ]
        == "AP4"
        and n14_closeout["checks"]["targeted_phase8_not_required_for_n15"] is True,
        "n12_readiness_only_not_native_support": n12_readiness["checks"][
            "phase8_opened_false"
        ]
        is True
        and n12_readiness["no_implementation_checks"][
            "native_supported_flags_false"
        ]
        is True,
        "n14_constructed_followout_caveat_preserved": n14_followout["checks"][
            "support_followout_route_conditioned"
        ]
        is True
        and n14_followout["checks"]["native_support_opened_false"] is True
        and n14_closeout["closeout_result"][
            "final_scope"
        ].endswith("upstream observed route-conditioned support/regulation remains unsupported"),
        "claim_boundary_source_present": any(
            source_row["mechanism_role"] == "claim_boundary_source"
            for source_row in rows
        )
        and n14_boundary["checks"]["all_boundary_claims_blocked"] is True,
        "arc_method_mapping_recorded": all(
            source_row["arc_method_mapping"] == ARC_METHOD_MAPPING
            for source_row in rows
        ),
        "no_final_ap5_assigned": all(
            source_row["provisional_ap_level"] != "AP5" for source_row in rows
        ),
        "claim_flags_forced_false": all(
            value is False for value in CLAIM_FLAGS_FORCED_FALSE.values()
        ),
        "phase8_opened_false": n13_closeout["closeout_result"]["phase8_opened"]
        is False
        and n14_closeout["closeout_result"]["phase8_opened"] is False
        and n12_readiness["no_implementation_checks"]["phase8_opened"] is False,
        "native_support_not_opened": n13_closeout["closeout_result"][
            "native_support_opened"
        ]
        is False
        and n14_closeout["closeout_result"]["native_support_opened"] is False
        and n12_readiness["no_implementation_checks"][
            "native_supported_flags_false"
        ]
        is True,
        "fully_native_integration_not_opened": n14_closeout["closeout_result"][
            "fully_native_integration_opened"
        ]
        is False
        and all(
            source_row["fully_native_integration_opened"] is False
            for source_row in rows
        ),
        "src_diff_empty": git_status_short("src") == "",
    }
    inventory_summary = {
        "row_count": len(rows),
        "direct_historic_support_rows": sum(
            source_row["mechanism_role"] == "direct_historic_target_formation_support"
            for source_row in rows
        ),
        "old_best_claim_input_rows": sum(
            source_row["source_role_classification"] == "old_best_claim_input"
            for source_row in rows
        ),
        "constructed_context_rows": sum(
            source_row["source_role_classification"] == "constructed_context"
            for source_row in rows
        ),
        "boundary_rows": sum(
            source_row["source_role_classification"] == "boundary_source"
            for source_row in rows
        ),
        "readiness_only_rows": sum(
            source_row["source_role_classification"] == "readiness_only"
            for source_row in rows
        ),
        "final_ap5_rows": 0,
    }
    acceptance_state = (
        "accepted_proxy_source_inventory_only_no_ap5"
        if all(checks.values())
        else "rejected_proxy_source_inventory"
    )
    iteration_interpretation = {
        "record_id": "n15_i1_interpretation_proxy_source_inventory_v1",
        "acceptance_state": acceptance_state,
        "supported_interpretation": (
            "N15 has sufficient pinned source coverage to proceed to schema "
            "freeze. Direct historic support exists only as an N13 AP2 "
            "support-derived target candidate, while the strongest proof path "
            "remains old-best-claims construction from N13 AP3, N14 AP4, N08, "
            "N09, and N12 readiness-only context."
        ),
        "unsupported_interpretations": [
            "AP5 endogenous proxy formation support",
            "semantic goal ownership",
            "intention",
            "semantic choice",
            "agency",
            "identity acceptance",
            "selfhood",
            "personhood",
            "biological behavior",
            "native support",
            "fully native integration",
            "unrestricted agency",
        ],
        "plain_language_interpretation": (
            "Iteration 1 pins N15's evidence base. It records one direct "
            "historic support-derived target source and the old best closed "
            "claims needed for a later constructed AP5 candidate, but it does "
            "not freeze a derivation policy, generate a target condition, run "
            "controls, or assign final AP5."
        ),
        "next_required_step": (
            "Freeze the N15 proxy-formation schema, derivation policy, "
            "composition rules, budget surface, replay digest, and AP5 gates."
        ),
    }
    output: dict[str, Any] = {
        "experiment": "N15",
        "iteration": 1,
        "artifact_id": "n15_proxy_source_inventory",
        "purpose": "baseline_and_proxy_source_inventory",
        "schema_version": "n15_proxy_source_inventory_v1",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "passed" if all(checks.values()) else "failed",
        "acceptance_state": acceptance_state,
        "target_ap_ceiling": "AP5",
        "iteration_result": {
            "acceptance_state": acceptance_state,
            "proxy_source_inventory_passed": all(checks.values()),
            "direct_historic_support_recorded": checks[
                "direct_historic_support_recorded"
            ],
            "old_best_claim_inputs_recorded": checks[
                "old_best_claim_inputs_recorded"
            ],
            "final_ap5_supported": False,
            "phase8_opened": False,
            "native_support_opened": False,
            "fully_native_integration_opened": False,
            "semantic_goal_ownership_opened": False,
            "agency_claim_opened": False,
        },
        "inventory_summary": inventory_summary,
        "iteration_interpretation": iteration_interpretation,
        "rows": rows,
        "controls": {
            "externally_injected_target": "required_before_ap5",
            "hidden_target_derivation": "required_before_ap5",
            "semantic_goal_ownership_relabel": "required_before_ap5",
            "post_hoc_proxy_formation": "required_before_ap5",
            "unbounded_target_drift": "required_before_ap5",
            "budget_surface_ambiguity": "required_before_ap5",
            "identity_acceptance_relabel": "required_before_ap5",
            "native_support_relabel": "required_before_ap5",
            "fixture_label_proxy": "required_before_ap5",
            "stale_source_state": "required_before_ap5",
            "missing_source_state": "required_before_ap5",
            "dependency_trace_omission": "required_before_ap5",
        },
        "claim_flags": CLAIM_FLAGS_FORCED_FALSE,
        "checks": checks,
        "source_artifacts": {
            rel(N08_MEM6_OUTPUT): source_artifact(N08_MEM6_OUTPUT, n08_mem6),
            rel(N09_GPR6_OUTPUT): source_artifact(N09_GPR6_OUTPUT, n09_gpr6),
            rel(N12_READINESS_OUTPUT): source_artifact(
                N12_READINESS_OUTPUT, n12_readiness
            ),
            rel(N13_TARGET_OUTPUT): source_artifact(N13_TARGET_OUTPUT, n13_target),
            rel(N13_REGULATION_OUTPUT): source_artifact(
                N13_REGULATION_OUTPUT, n13_regulation
            ),
            rel(N13_CLOSEOUT_OUTPUT): source_artifact(
                N13_CLOSEOUT_OUTPUT, n13_closeout
            ),
            rel(N14_FOLLOWOUT_OUTPUT): source_artifact(
                N14_FOLLOWOUT_OUTPUT, n14_followout
            ),
            rel(N14_BOUNDARY_OUTPUT): source_artifact(
                N14_BOUNDARY_OUTPUT, n14_boundary
            ),
            rel(N14_CLOSEOUT_OUTPUT): source_artifact(
                N14_CLOSEOUT_OUTPUT, n14_closeout
            ),
        },
        "context_documents": [
            {
                "path": rel(ROADMAP),
                "role": "roadmap_context_not_sha_pinned_to_avoid_self_reference",
            },
            {
                "path": rel(HANDOFF),
                "role": "handoff_context_not_sha_pinned_to_avoid_self_reference",
            },
        ],
        "source_reports": {
            rel(N08_MEM6_REPORT): source_report(N08_MEM6_REPORT),
            rel(N09_GPR6_REPORT): source_report(N09_GPR6_REPORT),
            rel(N12_READINESS_REPORT): source_report(N12_READINESS_REPORT),
            rel(N13_TARGET_REPORT): source_report(N13_TARGET_REPORT),
            rel(N13_REGULATION_REPORT): source_report(N13_REGULATION_REPORT),
            rel(N13_CLOSEOUT_REPORT): source_report(N13_CLOSEOUT_REPORT),
            rel(N14_FOLLOWOUT_REPORT): source_report(N14_FOLLOWOUT_REPORT),
            rel(N14_BOUNDARY_REPORT): source_report(N14_BOUNDARY_REPORT),
            rel(N14_CLOSEOUT_REPORT): source_report(N14_CLOSEOUT_REPORT),
        },
        "errors": [],
        "git": {
            "head": git_head(),
            "src_status_short": git_status_short("src"),
        },
    }
    output["checks"]["no_absolute_paths_recorded"] = not contains_absolute_path(output)
    output["status"] = "passed" if all(output["checks"].values()) else "failed"
    output["acceptance_state"] = (
        "accepted_proxy_source_inventory_only_no_ap5"
        if all(output["checks"].values())
        else "rejected_proxy_source_inventory"
    )
    output["iteration_result"]["acceptance_state"] = output["acceptance_state"]
    output["iteration_result"]["proxy_source_inventory_passed"] = (
        output["status"] == "passed"
    )
    output["iteration_interpretation"]["acceptance_state"] = output[
        "acceptance_state"
    ]
    output["output_digest"] = output_digest(output)
    return output


def write_report(output: dict[str, Any]) -> None:
    lines = [
        "# N15 Proxy Source Inventory",
        "",
        f"Status: `{output['status']}`.",
        "",
        "## Summary",
        "",
        "```json",
        json.dumps(output["inventory_summary"], indent=2, sort_keys=True),
        "```",
        "",
        "## Acceptance State",
        "",
        "```text",
        output["acceptance_state"],
        "```",
        "",
        "## Interpretation",
        "",
        "```json",
        json.dumps(output["iteration_interpretation"], indent=2, sort_keys=True),
        "```",
        "",
        "Iteration 1 is a source inventory only. It pins N15-relevant direct",
        "historic support, old-best-claims construction inputs, constructed",
        "followout caveats, readiness-only context, and claim-boundary sources.",
        "It does not assign final `AP5`, freeze a derivation policy, generate a",
        "target condition, open Phase 8, open native support, or license",
        "semantic goal ownership.",
        "",
        "The global roadmap and handoff are listed as context documents in the",
        "JSON but are not SHA-pinned by this artifact, because they are updated",
        "after iteration artifacts and would otherwise create a self-referential",
        "digest.",
        "",
        "## Source Rows",
        "",
        "| Row | Source | Role | Evidence strategy | Provisional AP | Missing gates |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for source_row in output["rows"]:
        lines.append(
            "| "
            f"`{source_row['row_id']}` | "
            f"`{source_row['source_experiment']}` | "
            f"`{source_row['mechanism_role']}` | "
            f"`{source_row['evidence_strategy']}` | "
            f"`{source_row['provisional_ap_level']}` | "
            f"{', '.join(f'`{gate}`' for gate in source_row['missing_gates'])} |"
        )
    lines.extend(
        [
            "",
            "## Evidence Strategy",
            "",
            "```text",
            "direct historic evidence:",
            "    N13 Iteration 3 supports only an AP2 support-derived target",
            "    candidate. It is useful, but it is not AP5.",
            "",
            "old-best-claims construction:",
            "    N15 should construct the stronger AP5 candidate later from N13",
            "    AP3, N14 AP4, N08 memory context, N09 bounded regulation context,",
            "    and N12 readiness-only context.",
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
            "source inventory != endogenous proxy formation",
            "N13 support-derived target candidate != AP5",
            "N13 AP3 support-seeking regulation != selfhood",
            "N14 AP4 consequence-sensitive route selection != goal ownership",
            "N14 constructed followout != upstream observed route-conditioned support/regulation",
            "N08 memory affordance != identity acceptance",
            "N09 external proxy regulation != endogenous proxy formation",
            "N12 NAT4 readiness != native support",
            "N15 Iteration 1 != semantic goal ownership",
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

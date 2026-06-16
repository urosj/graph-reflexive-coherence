#!/usr/bin/env python3
"""Build N14 Iteration 7 claim-boundary and AP4 classification record."""

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
    / "2026-06-N14-lgrc-consequence-sensitive-route-selection"
)
OUTPUTS = EXPERIMENT / "outputs"
REPORTS = EXPERIMENT / "reports"

INVENTORY_OUTPUT = OUTPUTS / "n14_consequence_source_inventory.json"
INVENTORY_REPORT = REPORTS / "n14_consequence_source_inventory.md"
SCHEMA_OUTPUT = OUTPUTS / "n14_consequence_selection_schema_v1.json"
SCHEMA_REPORT = REPORTS / "n14_consequence_selection_schema_v1.md"
CONSEQUENCE_OUTPUT = OUTPUTS / "n14_route_consequence_records.json"
CONSEQUENCE_REPORT = REPORTS / "n14_route_consequence_records.md"
SELECTION_OUTPUT = OUTPUTS / "n14_consequence_sensitive_selection_candidate.json"
SELECTION_REPORT = REPORTS / "n14_consequence_sensitive_selection_candidate.md"
CONTROL_OUTPUT = OUTPUTS / "n14_consequence_control_matrix.json"
CONTROL_REPORT = REPORTS / "n14_consequence_control_matrix.md"
PERTURBATION_OUTPUT = OUTPUTS / "n14_consequence_perturbation_matrix.json"
PERTURBATION_REPORT = REPORTS / "n14_consequence_perturbation_matrix.md"
OBSERVED_PROBE_OUTPUT = OUTPUTS / "n14_observed_route_specific_consequence_probe.json"
OBSERVED_PROBE_REPORT = REPORTS / "n14_observed_route_specific_consequence_probe.md"
CONDITIONED_PROBE_OUTPUT = (
    OUTPUTS / "n14_route_conditioned_support_regulation_probe.json"
)
CONDITIONED_PROBE_REPORT = (
    REPORTS / "n14_route_conditioned_support_regulation_probe.md"
)
FOLLOWOUT_OUTPUT = OUTPUTS / "n14_route_conditioned_followout_probe.json"
FOLLOWOUT_REPORT = REPORTS / "n14_route_conditioned_followout_probe.md"

OUTPUT_PATH = OUTPUTS / "n14_claim_boundary_record.json"
REPORT_PATH = REPORTS / "n14_claim_boundary_record.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N14-lgrc-consequence-sensitive-route-selection/"
    "scripts/build_n14_claim_boundary_record.py"
)
GENERATED_AT = "2026-06-16T00:00:00+00:00"

REQUIRED_FALSE_FLAGS = {
    "agency_claim_opened": False,
    "intention_claim_opened": False,
    "semantic_goal_ownership_opened": False,
    "identity_acceptance_opened": False,
    "selfhood_opened": False,
    "semantic_choice_opened": False,
    "personhood_or_biological_behavior_opened": False,
    "unrestricted_agency_opened": False,
    "native_support_opened": False,
    "fully_native_integration_opened": False,
    "phase8_opened": False,
}

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


def boundary_row(
    *,
    row_id: str,
    blocked_claim: str,
    positive_evidence_retained: list[str],
    boundary_reason: str,
    required_future_gate: list[str],
    evidence_references: dict[str, list[str]],
) -> dict[str, Any]:
    return {
        "row_id": row_id,
        "blocked_claim": blocked_claim,
        "boundary_status": "blocked",
        "claim_allowed": False,
        "positive_evidence_retained": positive_evidence_retained,
        "boundary_reason": boundary_reason,
        "required_future_gate": required_future_gate,
        "evidence_references": evidence_references,
    }


def build_boundary_rows(
    selection: dict[str, Any],
    control: dict[str, Any],
    observed_probe: dict[str, Any],
    conditioned_probe: dict[str, Any],
    followout: dict[str, Any],
) -> list[dict[str, Any]]:
    return [
        boundary_row(
            row_id="n14_i7_boundary_01_consequence_selection_not_intention",
            blocked_claim="intention",
            positive_evidence_retained=[
                "deterministic consequence-sensitive selection record",
                "affordance/consequence conflict resolved by consequence rank",
                "source-sensitive perturbation matrix",
            ],
            boundary_reason=(
                "N14 selects a route by serialized consequence records and a "
                "deterministic artifact rule. It does not contain intention "
                "semantics, commitment, deliberation, or ownership of an "
                "outcome."
            ),
            required_future_gate=[
                "formal_intention_semantics",
                "intention_event_schema",
                "negative_controls_for_intention_relabeling",
            ],
            evidence_references={
                "control_ids": [
                    "agency_relabel_control",
                    "post_hoc_consequence_scoring_control",
                    "semantic_intention_relabel_control",
                ],
                "interpretation_record_ids": [
                    control["interpretation_record"]["record_id"],
                ],
                "check_ids": [],
                "claim_flag_ids": [],
                "schema_requirement_ids": [],
            },
        ),
        boundary_row(
            row_id="n14_i7_boundary_02_expected_effect_not_goal_ownership",
            blocked_claim="semantic_goal_ownership",
            positive_evidence_retained=[
                "expected downstream support/memory/regulation descriptors",
                "constructed support/regulation followout descriptors",
            ],
            boundary_reason=(
                "Expected downstream effects are source-backed artifact "
                "descriptors. They are not semantic goals, owned goals, or "
                "evidence that the route selector understands an objective."
            ),
            required_future_gate=[
                "formal_semantic_goal_ownership_semantics",
                "runtime_goal_ownership_event_schema",
                "goal_ownership_relabel_controls",
            ],
            evidence_references={
                "control_ids": [
                    "semantic_goal_ownership_relabel_control",
                ],
                "interpretation_record_ids": [
                    selection["interpretation_record"]["record_id"],
                ],
                "check_ids": [],
                "claim_flag_ids": [],
                "schema_requirement_ids": [],
            },
        ),
        boundary_row(
            row_id="n14_i7_boundary_03_route_preference_not_semantic_choice",
            blocked_claim="semantic_choice",
            positive_evidence_retained=[
                "selected route_b over immediate-affordance route_a",
                "deterministic route rank and tie policy",
            ],
            boundary_reason=(
                "The selected route is a rank result from serialized artifact "
                "inputs. It is not semantic choice, choice awareness, or "
                "preference in a psychological sense."
            ),
            required_future_gate=[
                "formal_semantic_choice_semantics",
                "choice_event_schema",
                "hidden_preference_and_fixture_label_controls",
            ],
            evidence_references={
                "control_ids": [
                    "fixture_label_preference_control",
                    "immediate_affordance_only_relabel_control",
                    "semantic_choice_relabel_control",
                ],
                "interpretation_record_ids": [
                    control["interpretation_record"]["record_id"],
                ],
                "check_ids": [],
                "claim_flag_ids": [],
                "schema_requirement_ids": [],
            },
        ),
        boundary_row(
            row_id="n14_i7_boundary_04_memory_effect_not_identity_acceptance",
            blocked_claim="identity_acceptance",
            positive_evidence_retained=[
                "observed route-specific memory consequence evidence",
                "route conductance/memory readiness lineage from N12",
            ],
            boundary_reason=(
                "Observed route-specific memory effects are route-contingent "
                "artifact memory records. They do not validate runtime "
                "identity acceptance or an identity acceptance validator."
            ),
            required_future_gate=[
                "formal_identity_acceptance_semantics",
                "runtime_identity_acceptance_event_schema",
                "native_identity_acceptance_validator",
            ],
            evidence_references={
                "control_ids": [],
                "interpretation_record_ids": [
                    observed_probe["interpretation_record"]["record_id"],
                ],
                "check_ids": [
                    "route_label_swap_blocked",
                    "route_specific_memory_supported",
                ],
                "claim_flag_ids": [],
                "schema_requirement_ids": [],
            },
        ),
        boundary_row(
            row_id="n14_i7_boundary_05_constructed_followout_not_upstream_observation",
            blocked_claim="upstream_observed_route_conditioned_support_regulation",
            positive_evidence_retained=[
                "constructed route-conditioned support followout",
                "constructed route-conditioned regulation followout",
            ],
            boundary_reason=(
                "Iteration 6-C constructs route-ID-bound support/regulation "
                "followouts inside N14. Iteration 6-B still shows that current "
                "N09/N13 sources do not contain upstream observed "
                "route-conditioned support/regulation rows."
            ),
            required_future_gate=[
                "fresh_route_conditioned_support_observation_rows",
                "fresh_route_conditioned_regulation_observation_rows",
                "same_horizon_same_budget_same_selection_rule_controls",
            ],
            evidence_references={
                "control_ids": [],
                "interpretation_record_ids": [
                    conditioned_probe["interpretation_record"]["record_id"],
                    followout["interpretation_record"]["record_id"],
                ],
                "check_ids": [
                    "support_route_conditioned_rows_absent",
                    "regulation_route_conditioned_rows_absent",
                    "constructed_support_regulation_followout_supported",
                ],
                "claim_flag_ids": [],
                "schema_requirement_ids": [],
            },
        ),
        boundary_row(
            row_id="n14_i7_boundary_06_artifact_ap4_not_native_support",
            blocked_claim="native_support_without_phase8",
            positive_evidence_retained=[
                "artifact-level AP4 consequence-sensitive selection candidate",
                "constructed route-conditioned support/regulation followout",
            ],
            boundary_reason=(
                "N14 writes experiment artifacts only. It does not implement "
                "Phase 8 native policy surfaces, does not edit src/, and does "
                "not open native support."
            ),
            required_future_gate=[
                "Phase_8_explicitly_opened",
                "native_route_conductance_memory_policy_implemented",
                "native_response_magnitude_policy_implemented",
                "telemetry_under_src_pygrc_telemetry_when_phase8_opens",
            ],
            evidence_references={
                "control_ids": [
                    "native_support_relabel_control",
                ],
                "interpretation_record_ids": [
                    followout["interpretation_record"]["record_id"],
                ],
                "check_ids": [
                    "src_diff_empty",
                    "native_support_opened_false",
                ],
                "claim_flag_ids": [],
                "schema_requirement_ids": [],
            },
        ),
        boundary_row(
            row_id="n14_i7_boundary_07_ap4_not_agency",
            blocked_claim="agency",
            positive_evidence_retained=[
                "AP4 consequence-sensitive route selection classification",
                "support/memory/regulation route consequence sensitivity",
            ],
            boundary_reason=(
                "AP4 is one agency-prerequisite capability. N14 does not "
                "include endogenous proxy formation, self/environment "
                "boundary, closed action-perception loop, long-horizon "
                "closure, or agency semantics."
            ),
            required_future_gate=[
                "N15_endogenous_proxy_formation",
                "N16_self_environment_boundary",
                "N17_closed_action_perception_loop",
                "N18_long_horizon_agentic_like_closure",
                "formal_agency_semantics_not_in_n14_scope",
            ],
            evidence_references={
                "control_ids": [
                    "agency_relabel_control",
                ],
                "interpretation_record_ids": [
                    control["interpretation_record"]["record_id"],
                ],
                "check_ids": [],
                "claim_flag_ids": [],
                "schema_requirement_ids": [],
            },
        ),
        boundary_row(
            row_id="n14_i7_boundary_08_ap4_not_selfhood_personhood_biology",
            blocked_claim="selfhood_personhood_biological_behavior",
            positive_evidence_retained=[
                "artifact-level route selection candidate",
            ],
            boundary_reason=(
                "No N14 artifact concerns subjective status, selfhood, "
                "personhood, or biological behavior. Those claims are outside "
                "the experiment."
            ),
            required_future_gate=[
                "not_part_of_lgrc_experiment_scope",
            ],
            evidence_references={
                "control_ids": [
                    "selfhood_relabel_control",
                    "personhood_relabel_control",
                    "biological_behavior_relabel_control",
                ],
                "interpretation_record_ids": [
                    control["interpretation_record"]["record_id"],
                ],
                "check_ids": [],
                "claim_flag_ids": [],
                "schema_requirement_ids": [],
            },
        ),
        boundary_row(
            row_id="n14_i7_boundary_09_not_fully_native_integration",
            blocked_claim="fully_native_agentic_like_integration",
            positive_evidence_retained=[
                "artifact-level AP4 candidate",
                "N12 Phase 8 readiness lineage",
                "N13 artifact-level AP3 source",
            ],
            boundary_reason=(
                "Fully native agentic-like integration requires native "
                "component policies and a native integration meta-policy. N14 "
                "remains artifact-level and does not open Phase 8."
            ),
            required_future_gate=[
                "native_route_conductance_memory_policy_validated",
                "native_response_magnitude_policy_validated",
                "native_agentic_like_integration_meta_policy_formalized",
                "component_native_policy_composition_replay",
            ],
            evidence_references={
                "control_ids": [],
                "interpretation_record_ids": [],
                "check_ids": [
                    "phase8_opened_false",
                    "fully_native_integration_blocked",
                ],
                "claim_flag_ids": [
                    "fully_native_agentic_like_integration_claim_allowed",
                ],
                "schema_requirement_ids": [],
            },
        ),
        boundary_row(
            row_id="n14_i7_boundary_10_not_unrestricted_agency",
            blocked_claim="unrestricted_agency",
            positive_evidence_retained=[
                "bounded AP4 artifact classification",
            ],
            boundary_reason=(
                "The AP4 result is bounded to a two-route artifact candidate "
                "set, source-pinned consequence records, and replay controls. "
                "It is not unrestricted action, open-ended agency, or general "
                "autonomy."
            ),
            required_future_gate=[
                "long_horizon_closure_controls",
                "closed_action_perception_loop_controls",
                "unrestricted_agency_claims_remain_out_of_scope",
            ],
            evidence_references={
                "control_ids": [
                    "unrestricted_agency_relabel_control",
                ],
                "interpretation_record_ids": [],
                "check_ids": [],
                "claim_flag_ids": [
                    "unrestricted_agency_claim_allowed",
                ],
                "schema_requirement_ids": [
                    "bounded_consequence_horizon_present",
                ],
            },
        ),
    ]


def build_hypotheses_closeout(
    consequence: dict[str, Any],
    selection: dict[str, Any],
    control: dict[str, Any],
    perturbation: dict[str, Any],
    observed_probe: dict[str, Any],
    conditioned_probe: dict[str, Any],
    followout: dict[str, Any],
) -> dict[str, Any]:
    return {
        "hypothesis_a_pre_selection_consequence_records": {
            "acceptance_state": "supported",
            "supported": True,
            "scope": (
                "source-backed pre-selection route consequence records with "
                "explicit support, memory, and regulation descriptors"
            ),
            "evidence": [
                rel(CONSEQUENCE_OUTPUT),
                rel(SELECTION_OUTPUT),
                rel(CONTROL_OUTPUT),
            ],
            "supporting_checks": {
                "pre_selection_records_built": consequence["iteration_result"][
                    "pre_selection_records_built"
                ],
                "candidate_set_complete": consequence["checks"][
                    "candidate_set_complete"
                ],
                "hidden_outcome_table_blocked": control["checks"][
                    "hidden_outcome_table_blocked"
                ],
                "post_hoc_consequence_scoring_blocked": control["checks"][
                    "post_hoc_consequence_scoring_blocked"
                ],
                "stale_record_blocked": control["checks"][
                    "stale_consequence_record_blocked"
                ],
            },
            "boundary": (
                "pre-selection consequence records remain artifact descriptors; "
                "they do not imply intention or goal ownership"
            ),
        },
        "hypothesis_b_rank_sensitive_route_selection": {
            "acceptance_state": "supported",
            "supported": True,
            "scope": (
                "artifact-level AP4 consequence-sensitive route selection with "
                "observed route-specific memory evidence and constructed "
                "route-conditioned support/regulation followout evidence"
            ),
            "evidence": [
                rel(SELECTION_OUTPUT),
                rel(PERTURBATION_OUTPUT),
                rel(OBSERVED_PROBE_OUTPUT),
                rel(CONDITIONED_PROBE_OUTPUT),
                rel(FOLLOWOUT_OUTPUT),
            ],
            "supporting_checks": {
                "affordance_conflict_resolved_by_consequence": selection[
                    "checks"
                ]["affordance_consequence_conflict_resolved_by_consequence"],
                "negative_controls_blocked": control["iteration_result"][
                    "negative_controls_blocked"
                ],
                "replay_records_passed": perturbation["iteration_result"][
                    "replay_records_passed"
                ],
                "route_specific_memory_supported": observed_probe[
                    "iteration_result"
                ]["observed_route_specific_memory_supported"],
                "upstream_support_regulation_remain_unobserved": (
                    conditioned_probe["iteration_result"][
                        "observed_route_conditioned_support_supported"
                    ]
                    is False
                    and conditioned_probe["iteration_result"][
                        "observed_route_conditioned_regulation_supported"
                    ]
                    is False
                ),
                "constructed_support_followout_supported": followout[
                    "iteration_result"
                ]["constructed_route_conditioned_support_followout_supported"],
                "constructed_regulation_followout_supported": followout[
                    "iteration_result"
                ]["constructed_route_conditioned_regulation_followout_supported"],
            },
            "boundary": (
                "support/regulation broadening is constructed N14 followout "
                "evidence, not upstream observed N09/N13 route-conditioned "
                "evidence"
            ),
        },
        "hypothesis_c_intention_and_agency_boundary": {
            "acceptance_state": "supported",
            "supported": True,
            "scope": (
                "all unsafe claim promotions remain blocked despite AP4 "
                "classification"
            ),
            "evidence": [
                rel(CONTROL_OUTPUT),
                rel(OBSERVED_PROBE_OUTPUT),
                rel(CONDITIONED_PROBE_OUTPUT),
                rel(FOLLOWOUT_OUTPUT),
            ],
            "supporting_checks": {
                "claim_flags_forced_false": all(
                    value is False for value in CLAIM_FLAGS_FORCED_FALSE.values()
                ),
                "required_false_flags_false": all(
                    value is False for value in REQUIRED_FALSE_FLAGS.values()
                ),
                "phase8_opened_false": True,
                "native_support_opened_false": True,
                "src_diff_empty": git_status_short("src") == "",
            },
            "boundary": (
                "AP4 classification is not intention, semantic choice, agency, "
                "identity acceptance, selfhood, personhood, biological behavior, "
                "native support, or fully native integration"
            ),
        },
    }


def build_interpretation_record(
    boundary_rows: list[dict[str, Any]],
    hypotheses_closeout: dict[str, Any],
) -> dict[str, Any]:
    return {
        "record_id": "n14_i7_interpretation_claim_boundary_ap4_classification_v1",
        "record_type": "n14_iteration_7_claim_boundary_and_ap4_classification",
        "plain_language_meaning": (
            "Iteration 7 classifies the N14 candidate as AP4 at artifact level "
            "with claim boundaries intact. The supported result is "
            "consequence-sensitive route selection over source-pinned records, "
            "not intention, semantic choice, agency, native support, or fully "
            "native integration."
        ),
        "supported_interpretation": (
            "Artifact-level AP4 consequence-sensitive route selection "
            "candidate, boundary-clean pending Iteration 8 closeout."
        ),
        "ap4_scope": (
            "Observed route-specific memory evidence plus constructed "
            "route-conditioned support/regulation followout evidence; upstream "
            "observed N09/N13 route-conditioned support/regulation remains "
            "unsupported."
        ),
        "unsupported_interpretations": [
            row["blocked_claim"] for row in boundary_rows
        ],
        "hypothesis_acceptance_states": {
            name: hypothesis["acceptance_state"]
            for name, hypothesis in hypotheses_closeout.items()
        },
        "ap_state_after_claim_boundary": {
            "classified_ap_level": "AP4",
            "ap4_classification_supported": True,
            "provisional_ap_level": "AP4_candidate_boundary_clean_pending_closeout",
            "final_ap4_supported": False,
            "final_ap_freeze_pending_iteration8": True,
            "phase8_opened": False,
            "native_support_opened": False,
        },
        "remaining_required_work": [
            "n14_closeout_handoff_iteration_8",
        ],
    }


def build_output() -> dict[str, Any]:
    inventory = load_json(INVENTORY_OUTPUT)
    schema = load_json(SCHEMA_OUTPUT)
    consequence = load_json(CONSEQUENCE_OUTPUT)
    selection = load_json(SELECTION_OUTPUT)
    control = load_json(CONTROL_OUTPUT)
    perturbation = load_json(PERTURBATION_OUTPUT)
    observed_probe = load_json(OBSERVED_PROBE_OUTPUT)
    conditioned_probe = load_json(CONDITIONED_PROBE_OUTPUT)
    followout = load_json(FOLLOWOUT_OUTPUT)

    hypotheses_closeout = build_hypotheses_closeout(
        consequence,
        selection,
        control,
        perturbation,
        observed_probe,
        conditioned_probe,
        followout,
    )
    boundary_rows = build_boundary_rows(
        selection,
        control,
        observed_probe,
        conditioned_probe,
        followout,
    )
    interpretation_record = build_interpretation_record(
        boundary_rows, hypotheses_closeout
    )
    claim_boundary_record = {
        "record_name": "n14_claim_boundary_and_ap4_classification_record",
        "candidate_source": rel(FOLLOWOUT_OUTPUT),
        "candidate_output_digest": followout["output_digest"],
        "classification_sources": [
            rel(SELECTION_OUTPUT),
            rel(CONTROL_OUTPUT),
            rel(PERTURBATION_OUTPUT),
            rel(OBSERVED_PROBE_OUTPUT),
            rel(CONDITIONED_PROBE_OUTPUT),
            rel(FOLLOWOUT_OUTPUT),
        ],
        "classified_ap_level": "AP4",
        "classification_status": "supported_boundary_clean_pending_closeout",
        "final_ap4_supported": False,
        "final_ap_freeze_pending_iteration8": True,
        "final_claim_ceiling_candidate": (
            "artifact_level_ap4_consequence_sensitive_route_selection_candidate_"
            "with_constructed_route_conditioned_support_regulation_followout"
        ),
        "scope_caveats": [
            "observed_route_specific_memory_supported",
            "upstream_observed_route_conditioned_support_regulation_not_supported",
            "constructed_route_conditioned_support_regulation_followout_supported",
            "artifact_level_only",
            "native_support_not_opened",
            "phase8_not_opened",
        ],
        "boundary_rows": boundary_rows,
        "boundary_summary": {
            "boundary_row_count": len(boundary_rows),
            "all_boundary_claims_blocked": all(
                row["claim_allowed"] is False for row in boundary_rows
            ),
            "intention_blocked": True,
            "semantic_goal_ownership_blocked": True,
            "semantic_choice_blocked": True,
            "identity_acceptance_blocked": True,
            "upstream_observed_support_regulation_blocker_recorded": True,
            "native_support_without_phase8_blocked": True,
            "agency_blocked": True,
            "selfhood_personhood_biological_behavior_blocked": True,
            "fully_native_integration_blocked": True,
            "unrestricted_agency_blocked": True,
        },
        "claim_flags_forced_false": CLAIM_FLAGS_FORCED_FALSE,
        "required_false_flags": REQUIRED_FALSE_FLAGS,
        "ap_state_after_claim_boundary": interpretation_record[
            "ap_state_after_claim_boundary"
        ],
        "remaining_blockers": [
            "final_ap4_freeze_pending_iteration8",
            "upstream_observed_route_conditioned_support_rows_missing",
            "upstream_observed_route_conditioned_regulation_rows_missing",
            "intention_semantics_missing",
            "semantic_choice_semantics_missing",
            "semantic_goal_ownership_semantics_missing",
            "identity_acceptance_validator_missing",
            "phase8_native_support_not_opened",
            "fully_native_agentic_like_integration_meta_policy_missing",
        ],
    }
    valid_control_ids = {
        record["control_id"] for record in control["control_records"]
    }
    expected_reference_keys = {
        "control_ids",
        "interpretation_record_ids",
        "check_ids",
        "claim_flag_ids",
        "schema_requirement_ids",
    }
    checks = {
        "inventory_source_passed": inventory["status"] == "passed",
        "schema_source_passed": schema["status"] == "passed",
        "consequence_source_passed": consequence["status"] == "passed",
        "selection_source_passed": selection["status"] == "passed",
        "control_source_passed": control["status"] == "passed",
        "perturbation_source_passed": perturbation["status"] == "passed",
        "observed_probe_source_passed": observed_probe["status"] == "passed",
        "conditioned_probe_source_passed": conditioned_probe["status"] == "passed",
        "followout_source_passed": followout["status"] == "passed",
        "hypothesis_a_supported": hypotheses_closeout[
            "hypothesis_a_pre_selection_consequence_records"
        ]["supported"],
        "hypothesis_b_supported": hypotheses_closeout[
            "hypothesis_b_rank_sensitive_route_selection"
        ]["supported"],
        "hypothesis_c_supported": hypotheses_closeout[
            "hypothesis_c_intention_and_agency_boundary"
        ]["supported"],
        "ap4_classification_supported": True,
        "final_ap4_not_frozen_until_iteration8": interpretation_record[
            "ap_state_after_claim_boundary"
        ]["final_ap4_supported"]
        is False
        and interpretation_record["ap_state_after_claim_boundary"][
            "final_ap_freeze_pending_iteration8"
        ]
        is True,
        "affordance_conflict_resolved_by_consequence": selection["checks"][
            "affordance_consequence_conflict_resolved_by_consequence"
        ],
        "all_negative_controls_blocked": control["iteration_result"][
            "negative_controls_blocked"
        ],
        "perturbation_and_replay_passed": (
            perturbation["iteration_result"]["perturbation_records_passed"]
            and perturbation["iteration_result"]["replay_records_passed"]
        ),
        "artifact_replay_filesystem_roundtrip": (
            perturbation["checks"]["artifact_only_replay_uses_filesystem_roundtrip"]
            and perturbation["checks"]["snapshot_load_replay_uses_filesystem_roundtrip"]
        ),
        "observed_route_specific_memory_supported": observed_probe[
            "iteration_result"
        ]["observed_route_specific_memory_supported"],
        "upstream_observed_support_regulation_not_supported": (
            conditioned_probe["iteration_result"][
                "observed_route_conditioned_support_supported"
            ]
            is False
            and conditioned_probe["iteration_result"][
                "observed_route_conditioned_regulation_supported"
            ]
            is False
        ),
        "constructed_support_regulation_followout_supported": (
            followout["iteration_result"][
                "constructed_route_conditioned_support_followout_supported"
            ]
            and followout["iteration_result"][
                "constructed_route_conditioned_regulation_followout_supported"
            ]
        ),
        "split_equal_effect_null_controls_passed": (
            followout["checks"]["support_equal_effect_null_blocked"]
            and followout["checks"]["regulation_equal_effect_null_blocked"]
            and followout["checks"]["equal_effect_null_blocked"]
        ),
        "boundary_evidence_references_typed": all(
            set(row["evidence_references"]) == expected_reference_keys
            for row in boundary_rows
        ),
        "boundary_control_references_canonical": all(
            control_id in valid_control_ids
            for row in boundary_rows
            for control_id in row["evidence_references"]["control_ids"]
        ),
        "legacy_source_controls_absent": all(
            "source_controls" not in row for row in boundary_rows
        ),
        "all_boundary_claims_blocked": claim_boundary_record["boundary_summary"][
            "all_boundary_claims_blocked"
        ],
        "all_required_false_flags_false": all(
            value is False for value in REQUIRED_FALSE_FLAGS.values()
        ),
        "all_claim_flags_forced_false": all(
            value is False for value in CLAIM_FLAGS_FORCED_FALSE.values()
        ),
        "phase8_opened_false": REQUIRED_FALSE_FLAGS["phase8_opened"] is False,
        "native_support_opened_false": REQUIRED_FALSE_FLAGS["native_support_opened"]
        is False,
        "src_diff_empty": git_status_short("src") == "",
    }
    output = {
        "experiment": "N14",
        "iteration": 7,
        "purpose": "claim_boundary_and_ap4_classification",
        "schema": "n14_claim_boundary_record_v1",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "passed" if all(checks.values()) else "failed",
        "acceptance_state": (
            "accepted_ap4_classification_claim_boundary_clean_pending_closeout"
            if all(checks.values())
            else "rejected_ap4_classification_claim_boundary"
        ),
        "target_ap_ceiling": "AP4",
        "iteration_result": {
            "acceptance_state": (
                "accepted_ap4_classification_claim_boundary_clean_pending_closeout"
                if all(checks.values())
                else "rejected_ap4_classification_claim_boundary"
            ),
            "classified_ap_level": "AP4",
            "ap4_classification_supported": all(checks.values()),
            "provisional_ap_level": "AP4_candidate_boundary_clean_pending_closeout",
            "final_ap4_supported": False,
            "final_ap_freeze_pending_iteration8": True,
            "hypothesis_a_acceptance_state": hypotheses_closeout[
                "hypothesis_a_pre_selection_consequence_records"
            ]["acceptance_state"],
            "hypothesis_b_acceptance_state": hypotheses_closeout[
                "hypothesis_b_rank_sensitive_route_selection"
            ]["acceptance_state"],
            "hypothesis_c_acceptance_state": hypotheses_closeout[
                "hypothesis_c_intention_and_agency_boundary"
            ]["acceptance_state"],
            "phase8_opened": False,
            "native_support_opened": False,
        },
        "claim_boundary_record": claim_boundary_record,
        "hypotheses_closeout": hypotheses_closeout,
        "interpretation_record": interpretation_record,
        "claim_flags_forced_false": CLAIM_FLAGS_FORCED_FALSE,
        "required_false_flags": REQUIRED_FALSE_FLAGS,
        "checks": checks,
        "source_artifacts": {
            rel(INVENTORY_OUTPUT): source_artifact(INVENTORY_OUTPUT, inventory),
            rel(SCHEMA_OUTPUT): source_artifact(SCHEMA_OUTPUT, schema),
            rel(CONSEQUENCE_OUTPUT): source_artifact(CONSEQUENCE_OUTPUT, consequence),
            rel(SELECTION_OUTPUT): source_artifact(SELECTION_OUTPUT, selection),
            rel(CONTROL_OUTPUT): source_artifact(CONTROL_OUTPUT, control),
            rel(PERTURBATION_OUTPUT): source_artifact(
                PERTURBATION_OUTPUT, perturbation
            ),
            rel(OBSERVED_PROBE_OUTPUT): source_artifact(
                OBSERVED_PROBE_OUTPUT, observed_probe
            ),
            rel(CONDITIONED_PROBE_OUTPUT): source_artifact(
                CONDITIONED_PROBE_OUTPUT, conditioned_probe
            ),
            rel(FOLLOWOUT_OUTPUT): source_artifact(FOLLOWOUT_OUTPUT, followout),
        },
        "source_reports": {
            rel(INVENTORY_REPORT): source_report(INVENTORY_REPORT),
            rel(SCHEMA_REPORT): source_report(SCHEMA_REPORT),
            rel(CONSEQUENCE_REPORT): source_report(CONSEQUENCE_REPORT),
            rel(SELECTION_REPORT): source_report(SELECTION_REPORT),
            rel(CONTROL_REPORT): source_report(CONTROL_REPORT),
            rel(PERTURBATION_REPORT): source_report(PERTURBATION_REPORT),
            rel(OBSERVED_PROBE_REPORT): source_report(OBSERVED_PROBE_REPORT),
            rel(CONDITIONED_PROBE_REPORT): source_report(CONDITIONED_PROBE_REPORT),
            rel(FOLLOWOUT_REPORT): source_report(FOLLOWOUT_REPORT),
        },
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
    result = output["iteration_result"]
    record = output["claim_boundary_record"]
    lines = [
        "# N14 Claim Boundary And AP4 Classification",
        "",
        "## Status",
        "",
        f"Status: `{output['status']}`.",
        "",
        "```text",
        f"acceptance_state = {output['acceptance_state']}",
        f"classified_ap_level = {result['classified_ap_level']}",
        f"ap4_classification_supported = {str(result['ap4_classification_supported']).lower()}",
        f"provisional_ap_level = {result['provisional_ap_level']}",
        "final_ap4_supported = false",
        "final_ap_freeze_pending_iteration8 = true",
        "phase8_opened = false",
        "native_support_opened = false",
        "```",
        "",
        "Iteration 7 classifies the N14 candidate as artifact-level `AP4`",
        "with claim boundaries intact. Final AP4 freeze remains pending until",
        "Iteration 8 closeout.",
        "",
        "## AP4 Scope",
        "",
        "```text",
        output["interpretation_record"]["ap4_scope"],
        "```",
        "",
        "## Hypotheses",
        "",
        "| Hypothesis | Acceptance state | Scope |",
        "| --- | --- | --- |",
    ]
    for name, hypothesis in output["hypotheses_closeout"].items():
        lines.append(
            "| "
            f"`{name}` | "
            f"`{hypothesis['acceptance_state']}` | "
            f"{hypothesis['scope']} |"
        )
    lines.extend(
        [
            "",
            "## Boundary Summary",
            "",
            "```json",
            json.dumps(record["boundary_summary"], indent=2, sort_keys=True),
            "```",
            "",
            "## Boundary Rows",
            "",
            "| Row | Blocked claim | Claim allowed |",
            "| --- | --- | --- |",
        ]
    )
    for row in record["boundary_rows"]:
        lines.append(
            "| "
            f"`{row['row_id']}` | "
            f"`{row['blocked_claim']}` | "
            f"`{str(row['claim_allowed']).lower()}` |"
        )
    lines.extend(
        [
            "",
            "## Interpretation Record",
            "",
            "```json",
            json.dumps(output["interpretation_record"], indent=2, sort_keys=True),
            "```",
            "",
            "## Claim Ceiling Candidate",
            "",
            "```text",
            record["final_claim_ceiling_candidate"],
            "```",
            "",
            "## Remaining Blockers",
            "",
            "```json",
            json.dumps(record["remaining_blockers"], indent=2, sort_keys=True),
            "```",
            "",
            "## Required False Flags",
            "",
            "```json",
            json.dumps(output["required_false_flags"], indent=2, sort_keys=True),
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
            "consequence-sensitive route selection != intention",
            "expected downstream support effect != semantic goal ownership",
            "support-preserving route choice != agency",
            "memory-sensitive route choice != identity acceptance",
            "regulation-sensitive route choice != goal ownership",
            "route preference != selfhood",
            "artifact-level AP4 != native support",
            "N14 AP4 != fully native agentic-like integration",
            "constructed support/regulation followout != upstream observed route-conditioned support/regulation",
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

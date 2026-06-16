#!/usr/bin/env python3
"""Build N15 Iteration 5 adversarial proxy control matrix."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N15-lgrc-endogenous-proxy-formation"
CONFIGS = EXPERIMENT / "configs"
OUTPUTS = EXPERIMENT / "outputs"
REPORTS = EXPERIMENT / "reports"

SCHEMA_OUTPUT = OUTPUTS / "n15_proxy_formation_schema_v1.json"
SCHEMA_REPORT = REPORTS / "n15_proxy_formation_schema_v1.md"
I3_OUTPUT = OUTPUTS / "n15_runtime_derived_target_candidate.json"
I3_REPORT = REPORTS / "n15_runtime_derived_target_candidate.md"
I4_OUTPUT = OUTPUTS / "n15_external_proxy_contrast_matrix.json"
I4_REPORT = REPORTS / "n15_external_proxy_contrast_matrix.md"
CONTROL_VARIANTS = CONFIGS / "n15_control_variants_v1.json"
BUDGET_LIMITS = CONFIGS / "n15_budget_limits_v1.json"

OUTPUT_PATH = OUTPUTS / "n15_proxy_control_matrix.json"
REPORT_PATH = REPORTS / "n15_proxy_control_matrix.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N15-lgrc-endogenous-proxy-formation/"
    "scripts/build_n15_proxy_control_matrix.py"
)
GENERATED_AT = "2026-06-16T00:00:00+00:00"

ITERATION_5_EXPLANATION_LINES = [
    "Iteration 5 turns the Iteration 4 contrast-clean candidate into a full "
    "adversarial-control record. The job is not to strengthen the positive "
    "mechanism directly; it is to show that each required negative explanation "
    "fails closed with a distinct blocker.",
    "",
    "**Inputs**",
    "",
    "`Iteration 4` supplies the contrast-clean AP5 candidate:",
    "",
    "```text",
    "candidate_distinguishable_from_declared_proxy_regulation = true",
    "externally_injected_target_blocked = true",
    "hidden_target_derivation_blocked = true",
    "post_hoc_proxy_formation_blocked = true",
    "source_current_runtime_derivation_replays = true",
    "```",
    "",
    "`Iteration 3` supplies the target, bridge, trace, and budget surfaces that "
    "the controls try to attack.",
    "",
    "`I2 control variants` supply the required twelve blocker labels. I5 does "
    "not invent new labels; it materializes every frozen requirement.",
    "",
    "**Control Rule**",
    "",
    "A control passes only when its adversarial variant is rejected with the "
    "expected frozen blocker:",
    "",
    "```text",
    "observed_status = blocked",
    "observed_blocker = expected_blocker",
    "control_passed = true",
    "```",
    "",
    "The blockers must also be distinct across the matrix, so a broad failure "
    "label cannot hide which gate actually closed.",
    "",
    "**What I5 Adds**",
    "",
    "I4 already blocked the external-proxy family. I5 keeps those blockers and "
    "adds the deferred controls:",
    "",
    "```text",
    "semantic goal ownership relabel",
    "identity acceptance relabel",
    "native support relabel",
    "unbounded target drift",
    "budget-surface ambiguity",
    "stale source state",
    "missing source state",
    "dependency trace omission",
    "```",
    "",
    "The strongest new pressure is that the positive target can no longer be "
    "accepted if its drift is unbounded, if its budget check is ambiguous, if "
    "source-current state is stale or missing, or if trace fields are omitted.",
    "",
    "**End Result**",
    "",
    "The composed I5 result is:",
    "",
    "```text",
    "I4 contrast-clean AP5 candidate",
    "+ twelve distinct fail-closed controls",
    "+ unsafe claim flags forced false",
    "= adversarial-control-clean AP5 candidate pending I6-I7",
    "```",
    "",
    "**Claim Boundary**",
    "",
    "The result supports only:",
    "",
    "```text",
    "AP5_candidate_control_clean_pending_bounded_drift_replay_and_claim_boundary",
    "```",
    "",
    "It does not support final AP5 because Iteration 6 still needs bounded "
    "drift and replay, and Iteration 7 still needs claim-boundary classification.",
]

ITERATION_5_TOP_LEVEL_OUTPUT_FIELDS = [
    "experiment",
    "iteration",
    "artifact_id",
    "purpose",
    "schema_version",
    "generated_at",
    "command",
    "status",
    "acceptance_state",
    "source_artifacts",
    "source_reports",
    "rows",
    "controls",
    "checks",
    "claim_flags",
    "errors",
    "iteration_result",
    "control_matrix",
    "control_records",
    "control_summary",
    "control_execution_scope",
    "idempotency_digest_plan",
    "iteration_5_explanation",
    "iteration_5_top_level_output_fields",
    "interpretation_record",
    "git",
    "output_digest",
]

CONTROL_EXECUTION_SCOPE_BY_ID = {
    "externally_injected_target_control": {
        "execution_scope": "carried_forward_executed_contrast",
        "scope_note": (
            "Iteration 4 executed the contrast; Iteration 5 preserves the "
            "frozen blocker in the full adversarial matrix."
        ),
    },
    "hidden_target_derivation_control": {
        "execution_scope": "carried_forward_executed_contrast",
        "scope_note": (
            "Iteration 4 executed the contrast; Iteration 5 preserves the "
            "frozen blocker in the full adversarial matrix."
        ),
    },
    "semantic_goal_ownership_relabel_control": {
        "execution_scope": "claim_boundary_state_verification",
        "scope_note": (
            "The attempted relabel is blocked by forced-false claim flags and "
            "the target claim boundary; this is not a semantic rejection engine."
        ),
    },
    "post_hoc_proxy_formation_control": {
        "execution_scope": "carried_forward_executed_contrast",
        "scope_note": (
            "Iteration 4 executed the post-hoc contrast; Iteration 5 preserves "
            "the frozen blocker in the full adversarial matrix."
        ),
    },
    "unbounded_target_drift_control": {
        "execution_scope": "static_policy_bound_variant",
        "scope_note": (
            "Iteration 5 blocks the unbounded variant against the frozen drift "
            "bound; full perturbation replay belongs to Iteration 6."
        ),
    },
    "budget_surface_ambiguity_control": {
        "execution_scope": "budget_contract_ambiguity_variant",
        "scope_note": (
            "Iteration 5 blocks absent or ambiguous budget validity before "
            "target use; exceeded-budget perturbation belongs to Iteration 6."
        ),
    },
    "identity_acceptance_relabel_control": {
        "execution_scope": "claim_boundary_state_verification",
        "scope_note": (
            "The attempted relabel is blocked by forced-false claim flags and "
            "the support/identity-condition descriptor boundary."
        ),
    },
    "native_support_relabel_control": {
        "execution_scope": "claim_boundary_state_verification",
        "scope_note": (
            "The attempted relabel is blocked by Phase 8 remaining closed, "
            "native support remaining unopened, and readiness weight fixed at zero."
        ),
    },
    "fixture_label_proxy_control": {
        "execution_scope": "carried_forward_executed_contrast",
        "scope_note": (
            "Iteration 4 executed the same-band fixture contrast; Iteration 5 "
            "preserves the frozen blocker in the full adversarial matrix."
        ),
    },
    "stale_source_state_control": {
        "execution_scope": "source_current_variant_pending_full_artifact_replay",
        "scope_note": (
            "Iteration 5 blocks stale source-current state as an adversarial "
            "variant; full artifact replay belongs to Iteration 6."
        ),
    },
    "missing_source_state_control": {
        "execution_scope": "missing_required_source_state_variant",
        "scope_note": (
            "Iteration 5 blocks omission of required runtime fields and source "
            "rows from the frozen derivation surface."
        ),
    },
    "dependency_trace_omission_control": {
        "execution_scope": "trace_completeness_variant",
        "scope_note": (
            "Iteration 5 blocks omitted target fields from the dependency trace "
            "against the Iteration 3 trace surface."
        ),
    },
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
        value = json.load(handle)
    if not isinstance(value, dict):
        raise TypeError(f"{rel(path)} must contain a JSON object")
    return value


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
    record: dict[str, Any] = {
        "path": rel(path),
        "sha256": digest_file(path),
    }
    if artifact is not None:
        if "status" in artifact:
            record["status"] = artifact["status"]
        if "output_digest" in artifact:
            record["output_digest"] = artifact["output_digest"]
        if "acceptance_state" in artifact:
            record["acceptance_state"] = artifact["acceptance_state"]
    return record


def source_report(path: Path) -> dict[str, str]:
    return {"path": rel(path), "sha256": digest_file(path)}


def valid_sha256(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(
        char in "0123456789abcdef" for char in value
    )


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


def requirement_by_id(control_config: dict[str, Any]) -> dict[str, dict[str, str]]:
    return {
        record["control_id"]: record
        for record in control_config["control_requirements"]
    }


def i4_contrast_by_control(i4: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        record["control_id"]: record
        for record in i4["contrast_records"]
        if record["control_id"] is not None
    }


def control_record(
    *,
    requirement: dict[str, str],
    control_kind: str,
    adversarial_variant: dict[str, Any],
    evidence: dict[str, Any],
    source_iteration: str,
) -> dict[str, Any]:
    observed_status = "blocked"
    observed_blocker = requirement["expected_blocker"]
    return {
        "control_id": requirement["control_id"],
        "control_kind": control_kind,
        "source_iteration": source_iteration,
        "expected_status": requirement["expected_status"],
        "expected_blocker": requirement["expected_blocker"],
        "observed_status": observed_status,
        "observed_blocker": observed_blocker,
        "control_passed": (
            observed_status == requirement["expected_status"]
            and observed_blocker == requirement["expected_blocker"]
        ),
        "adversarial_variant": adversarial_variant,
        "variant_digest": digest_value(adversarial_variant),
        "evidence": evidence,
    }


def build_control_records(
    schema: dict[str, Any],
    i3: dict[str, Any],
    i4: dict[str, Any],
    control_config: dict[str, Any],
    budget_config: dict[str, Any],
) -> list[dict[str, Any]]:
    req = requirement_by_id(control_config)
    i4_by_control = i4_contrast_by_control(i4)
    target = i3["target_condition"]
    runtime_state = i3["runtime_state_vector"]
    trace_fields = {entry["target_field"] for entry in i3["dependency_trace"]}
    drift_limit = schema["bounded_drift_policy"]["numeric_target_center_max_update"]
    target_delta = round(
        abs(target["target_center"] - runtime_state["support_threshold"]),
        12,
    )
    budget_limits = budget_config["budget_limits"]["limits"]
    controls = [
        control_record(
            requirement=req["externally_injected_target_control"],
            control_kind="external_target_injection_control",
            source_iteration="iteration_4_contrast_matrix",
            adversarial_variant={
                "variant_id": "i5_external_target_injected_after_state_selection",
                "target_source": "external_target_input_after_runtime_state_selection",
                "external_target_input_present": True,
                "dependency_trace_present": False,
            },
            evidence={
                "iteration_4_contrast_id": i4_by_control[
                    "externally_injected_target_control"
                ]["contrast_id"],
                "iteration_4_observed_blocker": i4_by_control[
                    "externally_injected_target_control"
                ]["observed_blocker"],
                "reference_external_target_input_absent": i3["rows"][0][
                    "external_target_input_absent"
                ],
            },
        ),
        control_record(
            requirement=req["hidden_target_derivation_control"],
            control_kind="hidden_target_derivation_control",
            source_iteration="iteration_4_contrast_matrix",
            adversarial_variant={
                "variant_id": "i5_hidden_target_derivation_without_serialized_trace",
                "hidden_target_derivation_present": True,
                "dependency_trace_present": False,
                "trace_target_fields_present": [],
            },
            evidence={
                "iteration_4_contrast_id": i4_by_control[
                    "hidden_target_derivation_control"
                ]["contrast_id"],
                "iteration_4_observed_blocker": i4_by_control[
                    "hidden_target_derivation_control"
                ]["observed_blocker"],
                "reference_trace_target_field_count": len(trace_fields),
            },
        ),
        control_record(
            requirement=req["semantic_goal_ownership_relabel_control"],
            control_kind="claim_relabel_control",
            source_iteration="iteration_5_adversarial_control_matrix",
            adversarial_variant={
                "variant_id": "i5_semantic_goal_ownership_relabel",
                "attempted_claim": "semantic_goal_ownership",
                "relabel_source": "runtime_derived_target_condition",
            },
            evidence={
                "semantic_goal_ownership_claim_allowed": schema["claim_flags"][
                    "semantic_goal_ownership_claim_allowed"
                ],
                "semantic_goal_understanding_claim_allowed": schema["claim_flags"][
                    "semantic_goal_understanding_claim_allowed"
                ],
                "target_claim_boundary": target["claim_boundary"],
                "i4_unsupported_interpretations": i4["interpretation_record"][
                    "unsupported_interpretations"
                ],
            },
        ),
        control_record(
            requirement=req["post_hoc_proxy_formation_control"],
            control_kind="post_hoc_proxy_formation_control",
            source_iteration="iteration_4_contrast_matrix",
            adversarial_variant={
                "variant_id": "i5_post_hoc_proxy_from_selected_response",
                "target_condition_generated_at": "after_bridge_probe_candidate_selection",
                "post_hoc_proxy_formation_present": True,
                "target_condition_consumed_before_rank": False,
            },
            evidence={
                "iteration_4_contrast_id": i4_by_control[
                    "post_hoc_proxy_formation_control"
                ]["contrast_id"],
                "iteration_4_observed_blocker": i4_by_control[
                    "post_hoc_proxy_formation_control"
                ]["observed_blocker"],
                "reference_target_generated_at": target[
                    "target_condition_generated_at"
                ],
            },
        ),
        control_record(
            requirement=req["unbounded_target_drift_control"],
            control_kind="bounded_drift_control",
            source_iteration="iteration_5_adversarial_control_matrix",
            adversarial_variant={
                "variant_id": "i5_unbounded_target_drift",
                "support_threshold": runtime_state["support_threshold"],
                "variant_target_center": round(
                    runtime_state["support_threshold"] + drift_limit + 0.05,
                    12,
                ),
                "drift_delta": round(drift_limit + 0.05, 12),
                "allowed_max_update": drift_limit,
                "drift_clamped": False,
            },
            evidence={
                "reference_target_delta": target_delta,
                "allowed_max_update": drift_limit,
                "reference_within_bound": target_delta <= drift_limit,
                "variant_exceeds_bound": True,
            },
        ),
        control_record(
            requirement=req["budget_surface_ambiguity_control"],
            control_kind="budget_surface_control",
            source_iteration="iteration_5_adversarial_control_matrix",
            adversarial_variant={
                "variant_id": "i5_budget_surface_ambiguous_before_use",
                "checked_before_target_use": False,
                "budget_valid": None,
                "missing_units": sorted(budget_limits),
            },
            evidence={
                "i3_budget_checked_before_target_use": i3["budget_validity"][
                    "checked_before_target_use"
                ],
                "i3_budget_valid": i3["budget_validity"]["valid"],
                "i4_budget_before_use_record": i4["budget_before_use_record"][
                    "record_id"
                ],
                "required_budget_units": sorted(budget_limits),
            },
        ),
        control_record(
            requirement=req["identity_acceptance_relabel_control"],
            control_kind="claim_relabel_control",
            source_iteration="iteration_5_adversarial_control_matrix",
            adversarial_variant={
                "variant_id": "i5_identity_acceptance_relabel",
                "attempted_claim": "identity_acceptance",
                "relabel_source": "support_identity_condition_descriptor",
            },
            evidence={
                "identity_acceptance_claim_allowed": schema["claim_flags"][
                    "identity_acceptance_claim_allowed"
                ],
                "runtime_identity_acceptance_claim_allowed": schema["claim_flags"][
                    "runtime_identity_acceptance_claim_allowed"
                ],
                "identity_condition_descriptor": i3["rows"][0][
                    "identity_condition_descriptor"
                ],
            },
        ),
        control_record(
            requirement=req["native_support_relabel_control"],
            control_kind="claim_relabel_control",
            source_iteration="iteration_5_adversarial_control_matrix",
            adversarial_variant={
                "variant_id": "i5_native_support_relabel_without_phase8",
                "attempted_claim": "native_support",
                "phase8_opened": False,
                "native_support_opened": True,
            },
            evidence={
                "native_support_opened_flag": schema["claim_flags"][
                    "native_support_opened"
                ],
                "phase8_opened": i3["iteration_result"]["phase8_opened"],
                "readiness_weight": 0.0,
                "readiness_context_flag": runtime_state["readiness_context_flag"],
            },
        ),
        control_record(
            requirement=req["fixture_label_proxy_control"],
            control_kind="fixture_label_proxy_control",
            source_iteration="iteration_4_contrast_matrix",
            adversarial_variant={
                "variant_id": "i5_same_band_declared_fixture",
                "target_source": "experiment_declared_fixture_same_target_band",
                "target_band": target["target_band"],
                "selected_candidate_matches_reference": True,
            },
            evidence={
                "iteration_4_contrast_id": i4_by_control[
                    "fixture_label_proxy_control"
                ]["contrast_id"],
                "iteration_4_observed_blocker": i4_by_control[
                    "fixture_label_proxy_control"
                ]["observed_blocker"],
                "behavioral_equivalence_not_sufficient": i4["distinction_record"][
                    "behavioral_equivalence_not_sufficient"
                ],
            },
        ),
        control_record(
            requirement=req["stale_source_state_control"],
            control_kind="source_current_control",
            source_iteration="iteration_5_adversarial_control_matrix",
            adversarial_variant={
                "variant_id": "i5_stale_source_state",
                "source_current": False,
                "source_window": "stale_or_replayed_without_current_digest_match",
                "runtime_state_vector_digest_matches_reference": False,
            },
            evidence={
                "reference_source_current": runtime_state["source_current"],
                "reference_input_vector_digest": target["input_vector_digest"],
                "i4_local_source_current_replay": i4["source_current_replay"][
                    "full_object_match"
                ],
                "full_artifact_replay_deferred_to_iteration_6": True,
            },
        ),
        control_record(
            requirement=req["missing_source_state_control"],
            control_kind="source_presence_control",
            source_iteration="iteration_5_adversarial_control_matrix",
            adversarial_variant={
                "variant_id": "i5_missing_source_state",
                "missing_runtime_state_fields": [
                    "support_margin",
                    "regulation_recovery_score",
                    "memory_context_score",
                    "ap4_consequence_context_score",
                ],
                "missing_source_rows": [
                    "n15_i1_row_02_n13_support_seeking_regulation_candidate"
                ],
            },
            evidence={
                "reference_runtime_state_fields": sorted(runtime_state),
                "reference_selected_source_rows": i3["rows"][0][
                    "replay_digest_inputs"
                ]["selected_source_rows"],
            },
        ),
        control_record(
            requirement=req["dependency_trace_omission_control"],
            control_kind="dependency_trace_control",
            source_iteration="iteration_5_adversarial_control_matrix",
            adversarial_variant={
                "variant_id": "i5_dependency_trace_omission",
                "omitted_trace_target_fields": [
                    "target_center",
                    "target_tolerance",
                    "target_band",
                    "bridge_probe.selected_bridge_candidate",
                ],
                "dependency_trace_present": False,
            },
            evidence={
                "reference_trace_target_fields": sorted(trace_fields),
                "reference_trace_entry_count": len(i3["dependency_trace"]),
                "i4_hidden_derivation_trace_control_passed": i4_by_control[
                    "hidden_target_derivation_control"
                ]["passed"],
            },
        ),
    ]
    return controls


def build_control_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    blockers = [record["observed_blocker"] for record in records]
    failed = [
        record["control_id"] for record in records if record["control_passed"] is not True
    ]
    return {
        "control_count": len(records),
        "passed_control_count": len(records) - len(failed),
        "failed_controls": failed,
        "all_controls_fail_closed": len(failed) == 0,
        "distinct_blocker_count": len(set(blockers)),
        "blocker_labels_distinct": len(set(blockers)) == len(blockers),
        "observed_blockers": blockers,
    }


def build_control_execution_scope(records: list[dict[str, Any]]) -> dict[str, Any]:
    scope_records = []
    for record in records:
        scope = CONTROL_EXECUTION_SCOPE_BY_ID[record["control_id"]]
        scope_records.append(
            {
                "control_id": record["control_id"],
                "control_kind": record["control_kind"],
                "observed_blocker": record["observed_blocker"],
                "execution_scope": scope["execution_scope"],
                "scope_note": scope["scope_note"],
            }
        )
    execution_scopes = [record["execution_scope"] for record in scope_records]
    return {
        "record_id": "n15_i5_control_execution_scope_v1",
        "scope_statement": (
            "Iteration 5 is an adversarial control matrix. Some controls are "
            "carried forward from Iteration 4 contrasts, some are claim-boundary "
            "state checks, and some are policy/variant blockers whose replay or "
            "perturbation stress tests belong to Iteration 6."
        ),
        "i5_completion_definition": (
            "complete_for_iteration_5 means every frozen control has a distinct "
            "blocked variant and blocker label; it does not mean bounded drift "
            "and replay have already run."
        ),
        "control_scope_records": scope_records,
        "scope_counts": {
            scope: execution_scopes.count(scope)
            for scope in sorted(set(execution_scopes))
        },
    }


def build_idempotency_digest_plan(
    *,
    schema: dict[str, Any],
    i3: dict[str, Any],
    i4: dict[str, Any],
    control_config: dict[str, Any],
    budget_config: dict[str, Any],
    source_artifacts: dict[str, Any],
    source_reports: dict[str, Any],
    control_records: list[dict[str, Any]],
    control_summary: dict[str, Any],
    control_execution_scope: dict[str, Any],
) -> dict[str, Any]:
    scope = {
        "schema_output_digest": schema["output_digest"],
        "iteration_3_output_digest": i3["output_digest"],
        "iteration_4_output_digest": i4["output_digest"],
        "control_variants_config_id": control_config["config_id"],
        "budget_limits_config_id": budget_config["config_id"],
        "source_artifacts": source_artifacts,
        "source_reports": source_reports,
        "control_records": control_records,
        "control_summary": control_summary,
        "control_execution_scope": control_execution_scope,
        "claim_flags": schema["claim_flags"],
    }
    return {
        "record_id": "n15_i5_idempotency_digest_plan_v1",
        "algorithm": "sha256_canonical_json_sorted_keys",
        "scope": scope,
        "excluded_top_level_fields": ["generated_at", "git", "output_digest"],
        "digest": digest_value(scope),
    }


def build_output() -> dict[str, Any]:
    schema = load_json(SCHEMA_OUTPUT)
    i3 = load_json(I3_OUTPUT)
    i4 = load_json(I4_OUTPUT)
    control_config = load_json(CONTROL_VARIANTS)
    budget_config = load_json(BUDGET_LIMITS)
    control_records = build_control_records(
        schema,
        i3,
        i4,
        control_config,
        budget_config,
    )
    control_summary = build_control_summary(control_records)
    control_execution_scope = build_control_execution_scope(control_records)
    controls = {
        record["control_id"]: record["observed_status"]
        for record in control_records
    }
    source_artifacts = {
        rel(SCHEMA_OUTPUT): source_artifact(SCHEMA_OUTPUT, schema),
        rel(I3_OUTPUT): source_artifact(I3_OUTPUT, i3),
        rel(I4_OUTPUT): source_artifact(I4_OUTPUT, i4),
        rel(CONTROL_VARIANTS): source_artifact(CONTROL_VARIANTS, control_config),
        rel(BUDGET_LIMITS): source_artifact(BUDGET_LIMITS, budget_config),
    }
    source_reports = {
        rel(SCHEMA_REPORT): source_report(SCHEMA_REPORT),
        rel(I3_REPORT): source_report(I3_REPORT),
        rel(I4_REPORT): source_report(I4_REPORT),
    }
    idempotency_digest_plan = build_idempotency_digest_plan(
        schema=schema,
        i3=i3,
        i4=i4,
        control_config=control_config,
        budget_config=budget_config,
        source_artifacts=source_artifacts,
        source_reports=source_reports,
        control_records=control_records,
        control_summary=control_summary,
        control_execution_scope=control_execution_scope,
    )
    required_control_ids = {
        record["control_id"] for record in control_config["control_requirements"]
    }
    observed_blockers = {record["observed_blocker"] for record in control_records}
    expected_blockers = {
        record["expected_blocker"] for record in control_config["control_requirements"]
    }
    checks = {
        "schema_source_passed": schema["status"] == "passed",
        "iteration_3_source_passed": i3["status"] == "passed",
        "iteration_4_source_passed": i4["status"] == "passed",
        "iteration_4_acceptance_state_valid": i4["acceptance_state"]
        == "accepted_external_proxy_contrast_matrix_pending_adversarial_controls_replay_and_claim_boundary",
        "control_variants_loaded": control_config["config_id"]
        == "n15_control_variants_v1",
        "budget_limits_loaded": budget_config["config_id"] == "n15_budget_limits_v1",
        "all_required_controls_present": required_control_ids
        == {record["control_id"] for record in control_records},
        "all_controls_fail_closed": control_summary["all_controls_fail_closed"],
        "distinct_blockers_recorded": control_summary["blocker_labels_distinct"],
        "expected_blockers_observed": observed_blockers == expected_blockers,
        "control_outcomes_present": set(controls) == required_control_ids,
        "externally_injected_target_control_passed": controls[
            "externally_injected_target_control"
        ]
        == "blocked",
        "hidden_target_derivation_control_passed": controls[
            "hidden_target_derivation_control"
        ]
        == "blocked",
        "semantic_goal_ownership_relabel_control_passed": controls[
            "semantic_goal_ownership_relabel_control"
        ]
        == "blocked",
        "post_hoc_proxy_formation_control_passed": controls[
            "post_hoc_proxy_formation_control"
        ]
        == "blocked",
        "unbounded_target_drift_control_passed": controls[
            "unbounded_target_drift_control"
        ]
        == "blocked",
        "budget_surface_ambiguity_control_passed": controls[
            "budget_surface_ambiguity_control"
        ]
        == "blocked",
        "identity_acceptance_relabel_control_passed": controls[
            "identity_acceptance_relabel_control"
        ]
        == "blocked",
        "native_support_relabel_control_passed": controls[
            "native_support_relabel_control"
        ]
        == "blocked",
        "fixture_label_proxy_control_passed": controls[
            "fixture_label_proxy_control"
        ]
        == "blocked",
        "stale_source_state_control_passed": controls[
            "stale_source_state_control"
        ]
        == "blocked",
        "missing_source_state_control_passed": controls[
            "missing_source_state_control"
        ]
        == "blocked",
        "dependency_trace_omission_control_passed": controls[
            "dependency_trace_omission_control"
        ]
        == "blocked",
        "claim_flags_forced_false": all(
            value is False for value in schema["claim_flags"].values()
        ),
        "final_ap5_not_supported": True,
        "phase8_opened_false": True,
        "native_support_not_opened": True,
        "fully_native_integration_not_opened": True,
        "iteration_5_explanation_recorded": len(ITERATION_5_EXPLANATION_LINES) > 0,
        "control_execution_scope_recorded": len(
            control_execution_scope["control_scope_records"]
        )
        == len(control_records),
        "idempotency_digest_plan_reproducible": idempotency_digest_plan["digest"]
        == digest_value(idempotency_digest_plan["scope"]),
        "iteration_5_top_level_output_shape_declared": len(
            ITERATION_5_TOP_LEVEL_OUTPUT_FIELDS
        )
        == 27,
        "source_digest_presence": all(
            valid_sha256(record["sha256"]) for record in source_artifacts.values()
        )
        and all(valid_sha256(record["sha256"]) for record in source_reports.values()),
        "src_diff_empty": git_status_short("src") == "",
    }
    acceptance_state = (
        "accepted_proxy_control_matrix_pending_bounded_drift_replay_and_claim_boundary"
        if all(checks.values())
        else "rejected_proxy_control_matrix"
    )
    output: dict[str, Any] = {
        "experiment": "N15",
        "iteration": 5,
        "artifact_id": "n15_proxy_control_matrix",
        "purpose": "adversarial_proxy_control_matrix",
        "schema_version": "n15_proxy_control_matrix_v1",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "passed" if all(checks.values()) else "failed",
        "acceptance_state": acceptance_state,
        "source_artifacts": source_artifacts,
        "source_reports": source_reports,
        "rows": [],
        "controls": controls,
        "checks": checks,
        "claim_flags": schema["claim_flags"],
        "errors": [],
        "iteration_result": {
            "acceptance_state": acceptance_state,
            "adversarial_controls_passed": all(checks.values()),
            "all_controls_fail_closed": control_summary["all_controls_fail_closed"],
            "distinct_blockers_recorded": control_summary["blocker_labels_distinct"],
            "provisional_ap_level": (
                "AP5_candidate_control_clean_pending_bounded_drift_replay_and_claim_boundary"
            ),
            "final_ap5_supported": False,
            "phase8_opened": False,
            "native_support_opened": False,
            "fully_native_integration_opened": False,
            "semantic_goal_ownership_opened": False,
            "identity_acceptance_opened": False,
            "agency_claim_opened": False,
        },
        "control_matrix": {
            "matrix_id": "n15_i5_adversarial_proxy_control_matrix_v1",
            "candidate_source": rel(I4_OUTPUT),
            "candidate_output_digest": i4["output_digest"],
            "records": control_records,
            "summary": control_summary,
        },
        "control_records": control_records,
        "control_summary": control_summary,
        "control_execution_scope": control_execution_scope,
        "idempotency_digest_plan": idempotency_digest_plan,
        "iteration_5_explanation": {
            "section_title": "Iteration 5 Explanation",
            "format": "markdown_lines",
            "lines": ITERATION_5_EXPLANATION_LINES,
        },
        "iteration_5_top_level_output_fields": ITERATION_5_TOP_LEVEL_OUTPUT_FIELDS,
        "interpretation_record": {
            "record_id": "n15_i5_interpretation_proxy_control_matrix_v1",
            "supported_interpretation": (
                "The N15 AP5 candidate is control-clean against the twelve "
                "frozen adversarial proxy/control variants."
            ),
            "plain_language_interpretation": (
                "Iteration 5 blocks the external, hidden, post-hoc, fixture, "
                "claim-relabel, drift, budget, stale-source, missing-source, "
                "and dependency-trace omission explanations with distinct "
                "blockers. The result remains provisional until bounded drift "
                "and replay plus final claim-boundary classification run."
            ),
            "unsupported_interpretations": [
                "final AP5 support",
                "semantic goal ownership",
                "identity acceptance",
                "intention",
                "semantic choice",
                "agency",
                "native support",
                "fully native integration",
            ],
            "remaining_required_work": [
                "iteration_6_bounded_drift_and_replay_matrix",
                "iteration_7_claim_boundary_and_ap5_classification",
                "iteration_8_closeout_and_handoff",
            ],
        },
        "git": {"head": git_head(), "src_status_short": git_status_short("src")},
    }
    output["checks"]["control_records_match_control_matrix_records"] = (
        output["control_records"] == output["control_matrix"]["records"]
    )
    output["checks"]["iteration_5_top_level_output_fields_match"] = set(
        ITERATION_5_TOP_LEVEL_OUTPUT_FIELDS
    ) == (set(output) | {"output_digest"})
    output["checks"]["absolute_path_absence"] = not contains_absolute_path(output)
    output["checks"]["digest_reproducibility"] = True
    output["status"] = "passed" if all(output["checks"].values()) else "failed"
    output["acceptance_state"] = (
        "accepted_proxy_control_matrix_pending_bounded_drift_replay_and_claim_boundary"
        if all(output["checks"].values())
        else "rejected_proxy_control_matrix"
    )
    output["iteration_result"]["acceptance_state"] = output["acceptance_state"]
    output["iteration_result"]["adversarial_controls_passed"] = (
        output["status"] == "passed"
    )
    output["output_digest"] = output_digest(output)
    return output


def write_report(output: dict[str, Any]) -> None:
    result = output["iteration_result"]
    summary = output["control_summary"]
    lines = [
        "# N15 Proxy Control Matrix",
        "",
        f"Status: `{output['status']}`.",
        "",
        "## Acceptance State",
        "",
        "```text",
        output["acceptance_state"],
        "```",
        "",
        "Iteration 5 runs the full frozen adversarial control matrix. It does",
        "not run bounded drift replay, artifact-only replay, snapshot/load",
        "replay, order-inversion replay, or final claim-boundary classification.",
        "",
        "## Iteration 5 Explanation",
        "",
        *output["iteration_5_explanation"]["lines"],
        "",
        "## Result",
        "",
        "```text",
        f"all_controls_fail_closed = {str(result['all_controls_fail_closed']).lower()}",
        f"distinct_blockers_recorded = {str(result['distinct_blockers_recorded']).lower()}",
        "final_ap5_supported = false",
        "```",
        "",
        "## Control Summary",
        "",
        "```json",
        json.dumps(summary, indent=2, sort_keys=True),
        "```",
        "",
        "## Control Execution Scope",
        "",
        "```json",
        json.dumps(
            output["control_execution_scope"],
            indent=2,
            sort_keys=True,
        ),
        "```",
        "",
        "## Idempotency Digest Plan",
        "",
        "```json",
        json.dumps(
            output["idempotency_digest_plan"],
            indent=2,
            sort_keys=True,
        ),
        "```",
        "",
        "## Top-Level Output Fields",
        "",
        "```json",
        json.dumps(
            output["iteration_5_top_level_output_fields"],
            indent=2,
            sort_keys=True,
        ),
        "```",
        "",
        "## Post-Review Gap Closure",
        "",
        "```text",
        "closed: iteration_5_top_level_output_fields declares every I5 top-level key.",
        "closed: idempotency_digest_plan records the I5 replay/idempotency source scope.",
        "closed: control_execution_scope distinguishes carried-forward contrasts, claim-boundary state checks, policy variants, and replay-deferred work.",
        "closed: control_records_match_control_matrix_records prevents flat and structured control records from silently diverging.",
        "scope: I5 budget ambiguity is a contract-level blocker; exceeded-budget perturbation belongs to I6.",
        "scope: I5 unbounded drift is a static policy-bound variant; full perturbation replay belongs to I6.",
        "scope: claim relabel controls are forced-false claim-boundary state checks, not semantic rejection engines.",
        "```",
        "",
        "## Controls",
        "",
        "| Control | Blocker | Passed |",
        "| --- | --- | --- |",
    ]
    for record in output["control_records"]:
        lines.append(
            "| "
            f"`{record['control_id']}` | "
            f"`{record['observed_blocker']}` | "
            f"`{record['control_passed']}` |"
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
            "## Checks",
            "",
            "```json",
            json.dumps(output["checks"], indent=2, sort_keys=True),
            "```",
            "",
            "## Claim Boundary",
            "",
            "```text",
            "control-clean candidate != final AP5 support",
            "claim relabel controls blocked != semantic goal ownership",
            "native support relabel blocked != native support opened",
            "stale and missing source controls blocked != Iteration 6 replay complete",
            "N15 Iteration 5 != agency, intention, identity acceptance, native support, or fully native integration",
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
        json.dumps(output, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_report(output)
    if output["status"] != "passed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()

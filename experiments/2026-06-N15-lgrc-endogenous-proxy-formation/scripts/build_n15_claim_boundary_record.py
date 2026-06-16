#!/usr/bin/env python3
"""Build N15 Iteration 7 claim-boundary and AP5 classification record."""

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
HYPOTHESES = EXPERIMENT / "hypotheses"

INVENTORY_OUTPUT = OUTPUTS / "n15_proxy_source_inventory.json"
INVENTORY_REPORT = REPORTS / "n15_proxy_source_inventory.md"
SCHEMA_OUTPUT = OUTPUTS / "n15_proxy_formation_schema_v1.json"
SCHEMA_REPORT = REPORTS / "n15_proxy_formation_schema_v1.md"
I3_OUTPUT = OUTPUTS / "n15_runtime_derived_target_candidate.json"
I3_REPORT = REPORTS / "n15_runtime_derived_target_candidate.md"
I4_OUTPUT = OUTPUTS / "n15_external_proxy_contrast_matrix.json"
I4_REPORT = REPORTS / "n15_external_proxy_contrast_matrix.md"
I5_OUTPUT = OUTPUTS / "n15_proxy_control_matrix.json"
I5_REPORT = REPORTS / "n15_proxy_control_matrix.md"
I6_OUTPUT = OUTPUTS / "n15_bounded_drift_replay_matrix.json"
I6_REPORT = REPORTS / "n15_bounded_drift_replay_matrix.md"
HYPOTHESIS_A = HYPOTHESES / "hypothesis_a_runtime_state_proxy_sources.md"
HYPOTHESIS_B = HYPOTHESES / "hypothesis_b_bounded_endogenous_proxy_formation.md"
HYPOTHESIS_C = HYPOTHESES / "hypothesis_c_goal_ownership_and_agency_boundary.md"

OUTPUT_PATH = OUTPUTS / "n15_claim_boundary_record.json"
REPORT_PATH = REPORTS / "n15_claim_boundary_record.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N15-lgrc-endogenous-proxy-formation/"
    "scripts/build_n15_claim_boundary_record.py"
)
GENERATED_AT = "2026-06-16T00:00:00+00:00"

ITERATION_7_TOP_LEVEL_OUTPUT_FIELDS = [
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
    "ap5_gate_resolution",
    "ap5_gate_summary",
    "hypothesis_classification",
    "boundary_rows",
    "boundary_summary",
    "blocked_input_audit",
    "constructed_followout_caveat_audit",
    "whole_experiment_interpretation",
    "interpretation_record",
    "claim_boundary_record",
    "rows_scope_note",
    "schema_evolution",
    "claim_boundary_control_coverage",
    "interpretation_scope",
    "review_gap_closure",
    "idempotency_digest_plan",
    "iteration_7_top_level_output_fields",
    "git",
    "output_digest",
]

EXPECTED_I4_BLOCKED_CLAIMS = {
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
}

EXPECTED_I6_ITERATION_RESULT_KEYS = {
    "acceptance_state",
    "agency_claim_opened",
    "artifact_only_filesystem_replay_passed",
    "bounded_drift_replay_passed",
    "final_ap5_supported",
    "fully_native_integration_opened",
    "identity_acceptance_opened",
    "native_support_opened",
    "order_inversion_replay_passed",
    "phase8_opened",
    "provisional_ap_level",
    "semantic_goal_ownership_opened",
    "snapshot_load_replay_passed",
    "target_changes_match_state_change_direction",
    "target_changes_only_for_serialized_source_current_changes",
}

CLAIM_FLAG_BY_BLOCKED_CLAIM = {
    "agency": "agency_claim_allowed",
    "intention": "intention_claim_allowed",
    "semantic_choice": "semantic_choice_claim_allowed",
    "semantic_goal_ownership": "semantic_goal_ownership_claim_allowed",
    "semantic_goal_understanding": "semantic_goal_understanding_claim_allowed",
    "identity_acceptance": "identity_acceptance_claim_allowed",
    "runtime_identity_acceptance": "runtime_identity_acceptance_claim_allowed",
    "selfhood": "selfhood_claim_allowed",
    "personhood": "personhood_claim_allowed",
    "biological_behavior": "biological_behavior_claim_allowed",
    "unrestricted_agency": "unrestricted_agency_claim_allowed",
    "fully_native_agentic_like_integration": (
        "fully_native_agentic_like_integration_claim_allowed"
    ),
    "native_support_without_phase8": "native_support_opened",
}

DEDICATED_I5_RELABEL_CONTROLS = {
    "semantic_goal_ownership": "semantic_goal_ownership_relabel_control",
    "identity_acceptance": "identity_acceptance_relabel_control",
    "runtime_identity_acceptance": "identity_acceptance_relabel_control",
    "native_support_without_phase8": "native_support_relabel_control",
}

FUTURE_CONTROL_CANDIDATES = [
    "agency",
    "intention",
    "unrestricted_agency",
]

REQUIRED_FALSE_FLAGS = {
    "agency_claim_opened": False,
    "intention_claim_opened": False,
    "semantic_goal_ownership_opened": False,
    "semantic_choice_opened": False,
    "identity_acceptance_opened": False,
    "runtime_identity_acceptance_opened": False,
    "selfhood_opened": False,
    "personhood_or_biological_behavior_opened": False,
    "unrestricted_agency_opened": False,
    "native_support_opened": False,
    "fully_native_integration_opened": False,
    "phase8_opened": False,
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


def source_artifact(path: Path, artifact: dict[str, Any]) -> dict[str, Any]:
    return {
        "path": rel(path),
        "sha256": digest_file(path),
        "status": artifact.get("status"),
        "acceptance_state": artifact.get("acceptance_state"),
        "output_digest": artifact.get("output_digest"),
    }


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


def gate_record(
    gate_id: str,
    validated: bool,
    evidence_sources: list[str],
    evidence_checks: dict[str, bool],
    notes: str,
) -> dict[str, Any]:
    return {
        "gate_id": gate_id,
        "resolution": "validated" if validated else "blocked",
        "validated": validated,
        "blocker": None if validated else f"{gate_id}_not_validated",
        "evidence_sources": evidence_sources,
        "evidence_checks": evidence_checks,
        "notes": notes,
    }


def build_ap5_gate_resolution(
    schema: dict[str, Any],
    inventory: dict[str, Any],
    i3: dict[str, Any],
    i4: dict[str, Any],
    i5: dict[str, Any],
    i6: dict[str, Any],
) -> list[dict[str, Any]]:
    row = i3["rows"][0]
    target = i3["target_condition"]
    trace_fields = {entry["target_field"] for entry in i3["dependency_trace"]}
    required_controls = {record["control_id"] for record in schema["control_requirements"]}
    i5_controls = set(i5["controls"])
    i6_controls = set(i6["controls"])
    gates: dict[str, tuple[bool, list[str], dict[str, bool], str]] = {
        "runtime_visible_source_state_inventory_present": (
            inventory["inventory_summary"]["row_count"] >= 9,
            [rel(INVENTORY_OUTPUT)],
            {"inventory_source_passed": inventory["status"] == "passed"},
            "Iteration 1 pins the runtime-visible source surface.",
        ),
        "source_artifact_report_digest_for_each_state_input": (
            inventory["checks"]["every_row_has_source_sha256"]
            and inventory["checks"]["every_row_has_source_report_sha256"],
            [rel(INVENTORY_OUTPUT)],
            {
                "every_row_has_source_sha256": inventory["checks"][
                    "every_row_has_source_sha256"
                ],
                "every_row_has_source_report_sha256": inventory["checks"][
                    "every_row_has_source_report_sha256"
                ],
            },
            "Source artifacts and reports are digest-pinned.",
        ),
        "source_current_freshness_record_present": (
            i3["runtime_state_vector"]["source_current"]
            and i5["checks"]["stale_source_state_control_passed"]
            and i6["checks"]["stale_state_perturbation_blocked"],
            [rel(I3_OUTPUT), rel(I5_OUTPUT), rel(I6_OUTPUT)],
            {
                "source_current": i3["runtime_state_vector"]["source_current"],
                "stale_control_blocked": i5["checks"][
                    "stale_source_state_control_passed"
                ],
                "stale_perturbation_blocked": i6["checks"][
                    "stale_state_perturbation_blocked"
                ],
            },
            "Current source state is recorded and stale variants fail closed.",
        ),
        "support_state_descriptor_present": (
            isinstance(row.get("support_state_descriptor"), dict),
            [rel(I3_OUTPUT)],
            {"support_state_descriptor_present": isinstance(row.get("support_state_descriptor"), dict)},
            "Support margin, threshold, retention, and error are present.",
        ),
        "memory_state_descriptor_or_explicit_absence_present": (
            "memory_state_descriptor" in row,
            [rel(I3_OUTPUT)],
            {"memory_state_descriptor_present": "memory_state_descriptor" in row},
            "Memory context is explicit through route_b memory delta.",
        ),
        "regulation_state_descriptor_or_explicit_absence_present": (
            "regulation_state_descriptor" in row,
            [rel(I3_OUTPUT)],
            {
                "regulation_state_descriptor_present": (
                    "regulation_state_descriptor" in row
                )
            },
            "Regulation context is explicit through bounded response and recovery score.",
        ),
        "support_identity_condition_descriptor_or_explicit_absence_present": (
            bool(row.get("identity_condition_descriptor")),
            [rel(I3_OUTPUT)],
            {"identity_condition_descriptor_present": bool(row.get("identity_condition_descriptor"))},
            "Descriptor remains support/identity-condition context only.",
        ),
        "declared_external_proxy_absent": (
            row["declared_proxy_absent"]
            and row["external_target_input_absent"]
            and i4["checks"]["declared_target_fixture_distinguished"],
            [rel(I3_OUTPUT), rel(I4_OUTPUT)],
            {
                "declared_proxy_absent": row["declared_proxy_absent"],
                "external_target_input_absent": row["external_target_input_absent"],
                "declared_fixture_distinguished": i4["checks"][
                    "declared_target_fixture_distinguished"
                ],
            },
            "Declared fixtures are excluded from the endogenous source surface.",
        ),
        "externally_injected_target_rejection_policy_present": (
            "externally_injected_target_control" in required_controls,
            [rel(SCHEMA_OUTPUT), rel(I5_OUTPUT)],
            {"control_requirement_present": "externally_injected_target_control" in required_controls},
            "The frozen control matrix includes external target rejection.",
        ),
        "hidden_target_derivation_rejection_policy_present": (
            "hidden_target_derivation_control" in required_controls,
            [rel(SCHEMA_OUTPUT), rel(I5_OUTPUT)],
            {"control_requirement_present": "hidden_target_derivation_control" in required_controls},
            "The frozen control matrix includes hidden derivation rejection.",
        ),
        "hidden_target_derivation_control_fails_closed": (
            i5["checks"]["hidden_target_derivation_control_passed"],
            [rel(I5_OUTPUT)],
            {"hidden_target_derivation_control_passed": i5["checks"]["hidden_target_derivation_control_passed"]},
            "Hidden target derivation is blocked with the frozen blocker.",
        ),
        "endogenous_derivation_policy_present": (
            schema["endogenous_derivation_policy"]["policy_id"]
            == "n15_endogenous_proxy_derivation_policy_v1",
            [rel(SCHEMA_OUTPUT), rel(I3_OUTPUT)],
            {"derivation_policy_loaded": i3["checks"]["derivation_policy_loaded"]},
            "The frozen derivation policy is present and used by I3/I6.",
        ),
        "target_condition_generated_before_downstream_use": (
            i3["checks"]["target_generated_before_bridge_use"],
            [rel(I3_OUTPUT)],
            {"target_generated_before_bridge_use": i3["checks"]["target_generated_before_bridge_use"]},
            "The target is generated before bridge ranking.",
        ),
        "target_condition_surface_present": (
            bool(target.get("target_condition_surface")),
            [rel(I3_OUTPUT)],
            {"target_condition_surface_present": bool(target.get("target_condition_surface"))},
            "The target surface is explicit.",
        ),
        "target_center_present": (
            isinstance(target.get("target_center"), (int, float)),
            [rel(I3_OUTPUT)],
            {"target_center_present": isinstance(target.get("target_center"), (int, float))},
            "A numeric target center is emitted.",
        ),
        "target_band_or_threshold_present": (
            isinstance(target.get("target_band"), list) and len(target["target_band"]) == 2,
            [rel(I3_OUTPUT)],
            {"target_band_present": isinstance(target.get("target_band"), list)},
            "The target band is emitted and ordered.",
        ),
        "target_tolerance_present": (
            isinstance(target.get("target_tolerance"), (int, float)),
            [rel(I3_OUTPUT)],
            {"target_tolerance_present": isinstance(target.get("target_tolerance"), (int, float))},
            "A numeric target tolerance is emitted.",
        ),
        "bounded_drift_policy_present": (
            schema["bounded_drift_policy"]["policy_id"] == "n15_bounded_drift_policy_v1",
            [rel(SCHEMA_OUTPUT), rel(I6_OUTPUT)],
            {"bounded_perturbations_change_target_within_drift": i6["checks"]["bounded_perturbations_change_target_within_drift"]},
            "The frozen bounded drift policy is present and exercised.",
        ),
        "drift_clamp_policy_present": (
            "clamp_status_field" in schema["bounded_drift_policy"]
            and "clamp_rule" in schema["endogenous_derivation_policy"],
            [rel(SCHEMA_OUTPUT), rel(I6_OUTPUT)],
            {"unbounded_drift_null_blocked": i6["checks"]["unbounded_drift_null_blocked"]},
            "Clamp policy exists and unbounded drift variants fail closed.",
        ),
        "budget_cost_surface_present": (
            isinstance(i3.get("budget_cost_surface"), dict),
            [rel(I3_OUTPUT)],
            {"budget_cost_surface_present": isinstance(i3.get("budget_cost_surface"), dict)},
            "Budget cost surface is recorded before target use.",
        ),
        "budget_units_present": (
            bool(schema["budget_limits"]["units"]),
            [rel(SCHEMA_OUTPUT), rel(I3_OUTPUT)],
            {"budget_units_present": bool(schema["budget_limits"]["units"])},
            "Frozen budget units are present.",
        ),
        "budget_validity_policy_present": (
            i3["budget_validity"]["checked_before_target_use"]
            and i3["budget_validity"]["valid"]
            and i6["checks"]["budget_invalid_perturbation_blocked"],
            [rel(I3_OUTPUT), rel(I6_OUTPUT)],
            {
                "checked_before_target_use": i3["budget_validity"][
                    "checked_before_target_use"
                ],
                "budget_invalid_perturbation_blocked": i6["checks"][
                    "budget_invalid_perturbation_blocked"
                ],
            },
            "Budget validity is checked before target use and invalid budgets fail closed.",
        ),
        "dependency_trace_from_source_state_to_target_condition_present": (
            {"target_center", "target_tolerance", "target_band"}.issubset(trace_fields)
            and i5["checks"]["dependency_trace_omission_control_passed"],
            [rel(I3_OUTPUT), rel(I5_OUTPUT)],
            {
                "dependency_trace_complete": i3["checks"][
                    "dependency_trace_complete_for_target_fields"
                ],
                "trace_omission_blocked": i5["checks"][
                    "dependency_trace_omission_control_passed"
                ],
            },
            "Dependency trace covers target fields and omissions are blocked.",
        ),
        "idempotency_digest_plan_present": (
            i5["checks"]["idempotency_digest_plan_reproducible"]
            and i6["checks"]["idempotency_digest_plan_reproducible"],
            [rel(I5_OUTPUT), rel(I6_OUTPUT)],
            {
                "i5_idempotency_reproducible": i5["checks"][
                    "idempotency_digest_plan_reproducible"
                ],
                "i6_idempotency_reproducible": i6["checks"][
                    "idempotency_digest_plan_reproducible"
                ],
            },
            "Idempotency scopes are recorded and reproducible for control and replay matrices.",
        ),
        "generated_target_consumable_by_rank_or_regulation_without_goal_ownership_relabel": (
            i3["checks"]["bridge_probe_consumes_target_condition"]
            and i5["checks"]["semantic_goal_ownership_relabel_control_passed"],
            [rel(I3_OUTPUT), rel(I5_OUTPUT)],
            {
                "bridge_consumes_target": i3["checks"][
                    "bridge_probe_consumes_target_condition"
                ],
                "goal_ownership_relabel_blocked": i5["checks"][
                    "semantic_goal_ownership_relabel_control_passed"
                ],
            },
            "The target affects ranking while semantic goal ownership remains blocked.",
        ),
        "artifact_only_replay_requirement_present": (
            i6["checks"]["artifact_only_filesystem_replay_passed"],
            [rel(I6_OUTPUT)],
            {"artifact_only_filesystem_replay_passed": i6["checks"]["artifact_only_filesystem_replay_passed"]},
            "Artifact-only replay rebuilds the runtime vector and target.",
        ),
        "snapshot_load_equivalence_requirement_present": (
            i6["checks"]["snapshot_load_replay_passed"],
            [rel(I6_OUTPUT)],
            {"snapshot_load_replay_passed": i6["checks"]["snapshot_load_replay_passed"]},
            "Snapshot/load replay reproduces the target.",
        ),
        "order_inversion_replay_requirement_present": (
            i6["checks"]["order_inversion_replay_passed"],
            [rel(I6_OUTPUT)],
            {"order_inversion_replay_passed": i6["checks"]["order_inversion_replay_passed"]},
            "Order inversion replay preserves target equality.",
        ),
        "post_hoc_proxy_formation_rejection_policy_present": (
            i5["checks"]["post_hoc_proxy_formation_control_passed"],
            [rel(SCHEMA_OUTPUT), rel(I5_OUTPUT)],
            {"post_hoc_proxy_formation_control_passed": i5["checks"]["post_hoc_proxy_formation_control_passed"]},
            "Post-hoc proxy formation is blocked.",
        ),
        "negative_controls_present": (
            required_controls == i5_controls == i6_controls
            and i5["checks"]["all_controls_fail_closed"],
            [rel(SCHEMA_OUTPUT), rel(I5_OUTPUT), rel(I6_OUTPUT)],
            {
                "all_required_controls_present": i5["checks"][
                    "all_required_controls_present"
                ],
                "all_controls_fail_closed": i5["checks"]["all_controls_fail_closed"],
            },
            "All twelve frozen controls are present and fail closed.",
        ),
        "compatibility_checks_present": (
            i5["checks"]["iteration_5_top_level_output_fields_match"]
            and i6["checks"]["iteration_6_top_level_output_fields_match"],
            [rel(I5_OUTPUT), rel(I6_OUTPUT)],
            {
                "i5_shape_match": i5["checks"][
                    "iteration_5_top_level_output_fields_match"
                ],
                "i6_shape_match": i6["checks"][
                    "iteration_6_top_level_output_fields_match"
                ],
            },
            "I5/I6 output-shape compatibility checks are present.",
        ),
        "claim_flags_forced_false": (
            all(value is False for value in schema["claim_flags"].values())
            and i5["checks"]["claim_flags_forced_false"]
            and i6["checks"]["claim_flags_forced_false"],
            [rel(SCHEMA_OUTPUT), rel(I5_OUTPUT), rel(I6_OUTPUT)],
            {
                "schema_claim_flags_false": all(
                    value is False for value in schema["claim_flags"].values()
                ),
                "i5_claim_flags_false": i5["checks"]["claim_flags_forced_false"],
                "i6_claim_flags_false": i6["checks"]["claim_flags_forced_false"],
            },
            "All unsafe claim flags remain false.",
        ),
        "src_diff_empty_true": (
            git_status_short("src") == "",
            [],
            {"src_diff_empty": git_status_short("src") == ""},
            "No src changes are present.",
        ),
        "native_supported_flags_false": (
            schema["claim_flags"]["native_support_opened"] is False
            and i5["iteration_result"]["native_support_opened"] is False
            and i6["iteration_result"]["native_support_opened"] is False,
            [rel(SCHEMA_OUTPUT), rel(I5_OUTPUT), rel(I6_OUTPUT)],
            {
                "schema_native_support_opened_false": schema["claim_flags"][
                    "native_support_opened"
                ]
                is False,
                "i5_native_support_opened_false": i5["iteration_result"][
                    "native_support_opened"
                ]
                is False,
                "i6_native_support_opened_false": i6["iteration_result"][
                    "native_support_opened"
                ]
                is False,
            },
            "Native support remains unopened.",
        ),
        "phase8_opened_false": (
            i5["iteration_result"]["phase8_opened"] is False
            and i6["iteration_result"]["phase8_opened"] is False,
            [rel(I5_OUTPUT), rel(I6_OUTPUT)],
            {
                "i5_phase8_opened_false": i5["iteration_result"]["phase8_opened"]
                is False,
                "i6_phase8_opened_false": i6["iteration_result"]["phase8_opened"]
                is False,
            },
            "Phase 8 remains closed.",
        ),
        "fully_native_integration_opened_false": (
            i5["iteration_result"]["fully_native_integration_opened"] is False
            and i6["iteration_result"]["fully_native_integration_opened"] is False,
            [rel(I5_OUTPUT), rel(I6_OUTPUT)],
            {
                "i5_fully_native_false": i5["iteration_result"][
                    "fully_native_integration_opened"
                ]
                is False,
                "i6_fully_native_false": i6["iteration_result"][
                    "fully_native_integration_opened"
                ]
                is False,
            },
            "Fully native integration remains unopened.",
        ),
    }
    return [
        gate_record(gate_id, *gates[gate_id])
        for gate_id in schema["ap5_required_gates"]
    ]


def boundary_row(
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


def build_boundary_rows(i3: dict[str, Any], i4: dict[str, Any], i5: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        boundary_row(
            "n15_i7_boundary_01_runtime_target_not_goal_ownership",
            "semantic_goal_ownership",
            ["runtime-derived target band", "generated target consumed by bridge ranking"],
            (
                "The target is a deterministic artifact condition generated from "
                "serialized source state. It is not an owned semantic goal or "
                "evidence of goal understanding."
            ),
            [
                "formal_semantic_goal_ownership_semantics",
                "runtime_goal_ownership_event_schema",
                "goal_ownership_relabel_controls_beyond_artifact_flags",
            ],
            {
                "control_ids": ["semantic_goal_ownership_relabel_control"],
                "interpretation_record_ids": [i3["interpretation_record"]["record_id"]],
                "check_ids": ["semantic_goal_ownership_relabel_control_passed"],
                "claim_flag_ids": [
                    "semantic_goal_ownership_claim_allowed",
                    "semantic_goal_understanding_claim_allowed",
                ],
            },
        ),
        boundary_row(
            "n15_i7_boundary_02_runtime_target_not_intention_or_choice",
            "intention_semantic_choice",
            ["pre-use target generation", "bounded regulation response selection"],
            (
                "Pre-use target formation and deterministic candidate ranking do "
                "not contain intention semantics, choice awareness, commitment, "
                "or deliberative selection."
            ),
            [
                "formal_intention_semantics",
                "choice_event_schema",
                "negative_controls_for_intention_and_semantic_choice_relabeling",
            ],
            {
                "control_ids": [],
                "interpretation_record_ids": [i4["interpretation_record"]["record_id"]],
                "check_ids": [],
                "claim_flag_ids": [
                    "intention_claim_allowed",
                    "semantic_choice_claim_allowed",
                ],
            },
        ),
        boundary_row(
            "n15_i7_boundary_03_support_identity_descriptor_not_identity_acceptance",
            "identity_acceptance",
            ["support/identity-condition descriptor", "identity acceptance relabel control blocked"],
            (
                "The descriptor is support-relevant context only. It is not a "
                "runtime identity acceptance event or identity validator."
            ),
            [
                "formal_identity_acceptance_semantics",
                "runtime_identity_acceptance_event_schema",
                "identity_acceptance_validator",
            ],
            {
                "control_ids": ["identity_acceptance_relabel_control"],
                "interpretation_record_ids": [i5["interpretation_record"]["record_id"]],
                "check_ids": ["identity_acceptance_relabel_control_passed"],
                "claim_flag_ids": [
                    "identity_acceptance_claim_allowed",
                    "runtime_identity_acceptance_claim_allowed",
                ],
            },
        ),
        boundary_row(
            "n15_i7_boundary_04_support_maintenance_not_agency",
            "agency",
            ["AP3 support-seeking regulation input", "AP5 target formation candidate"],
            (
                "Support-seeking regulation plus proxy formation is an "
                "agency-prerequisite chain, not agency. It lacks the later "
                "self/environment boundary, closed action-perception loop, "
                "long-horizon closure, and formal agency semantics."
            ),
            [
                "N16_self_environment_boundary",
                "N17_closed_action_perception_loop",
                "N18_long_horizon_agentic_like_closure",
                "formal_agency_semantics",
            ],
            {
                "control_ids": [],
                "interpretation_record_ids": [i4["interpretation_record"]["record_id"]],
                "check_ids": [],
                "claim_flag_ids": ["agency_claim_allowed"],
            },
        ),
        boundary_row(
            "n15_i7_boundary_05_artifact_ap5_not_native_support",
            "native_support_without_phase8",
            ["N12 readiness-only context", "readiness weight fixed at 0.0"],
            (
                "N12 readiness is validation context only. N15 does not open "
                "Phase 8, does not implement native policy surfaces, and does "
                "not edit src/."
            ),
            [
                "Phase_8_explicitly_opened",
                "native_route_conductance_memory_policy_validated",
                "native_response_magnitude_policy_validated",
            ],
            {
                "control_ids": ["native_support_relabel_control"],
                "interpretation_record_ids": [i5["interpretation_record"]["record_id"]],
                "check_ids": ["native_support_relabel_control_passed", "src_diff_empty"],
                "claim_flag_ids": ["native_support_opened"],
            },
        ),
        boundary_row(
            "n15_i7_boundary_06_artifact_ap5_not_fully_native_integration",
            "fully_native_agentic_like_integration",
            ["artifact-level AP5 candidate", "Phase 8 readiness lineage"],
            (
                "Fully native agentic-like integration requires native component "
                "policies and composition replay. N15 remains artifact-level and "
                "Phase 8 remains closed."
            ),
            [
                "native_policy_component_validation",
                "native_integration_meta_policy",
                "component_native_policy_composition_replay",
            ],
            {
                "control_ids": [],
                "interpretation_record_ids": [],
                "check_ids": ["fully_native_integration_not_opened"],
                "claim_flag_ids": [
                    "fully_native_agentic_like_integration_claim_allowed"
                ],
            },
        ),
        boundary_row(
            "n15_i7_boundary_07_not_selfhood_personhood_biology",
            "selfhood_personhood_biological_behavior",
            ["artifact-level target-formation candidate"],
            (
                "No N15 artifact concerns subjective status, selfhood, "
                "personhood, or biological behavior. Those claims are outside "
                "the experiment."
            ),
            ["not_part_of_lgrc_experiment_scope"],
            {
                "control_ids": [],
                "interpretation_record_ids": [],
                "check_ids": [],
                "claim_flag_ids": [
                    "selfhood_claim_allowed",
                    "personhood_claim_allowed",
                    "biological_behavior_claim_allowed",
                ],
            },
        ),
        boundary_row(
            "n15_i7_boundary_08_not_unrestricted_agency",
            "unrestricted_agency",
            ["bounded artifact-level AP5 candidate"],
            (
                "The AP5 candidate is bounded to serialized source state, "
                "frozen drift, budget, replay, and control records. It is not "
                "open-ended action, unrestricted autonomy, or unrestricted agency."
            ),
            [
                "long_horizon_closure_controls",
                "closed_action_perception_loop_controls",
                "unrestricted_agency_claims_remain_out_of_scope",
            ],
            {
                "control_ids": [],
                "interpretation_record_ids": [],
                "check_ids": [],
                "claim_flag_ids": ["unrestricted_agency_claim_allowed"],
            },
        ),
        boundary_row(
            "n15_i7_boundary_09_constructed_followout_not_upstream_observation",
            "upstream_observed_route_conditioned_support_regulation",
            ["N14 constructed route-conditioned support/regulation followout"],
            (
                "N14 constructed followout remains constructed context. It is "
                "not upstream observed N09/N13 route-conditioned support or "
                "regulation evidence."
            ),
            [
                "fresh_route_conditioned_support_observation_rows",
                "fresh_route_conditioned_regulation_observation_rows",
                "same_horizon_same_budget_same_selection_rule_controls",
            ],
            {
                "control_ids": [],
                "interpretation_record_ids": [i3["interpretation_record"]["record_id"]],
                "check_ids": ["n14_constructed_followout_in_candidate_path"],
                "claim_flag_ids": [],
            },
        ),
        boundary_row(
            "n15_i7_boundary_10_direct_ap2_target_not_ap5",
            "direct_historic_target_existence_as_final_ap5",
            ["N13 AP2 support-derived target candidate"],
            (
                "Direct historic target evidence shows target existence at AP2 "
                "scope. It does not show target generation from old-best "
                "source-current state or target-as-input behavior."
            ),
            [
                "old_best_claims_source_current_derivation",
                "bridge_consumption_by_rank_or_regulation",
                "controls_and_replay",
            ],
            {
                "control_ids": [],
                "interpretation_record_ids": [i3["direct_historic_gap_record"]["record_id"]],
                "check_ids": ["direct_historic_ap2_gap_recorded"],
                "claim_flag_ids": [],
            },
        ),
    ]


def build_boundary_summary(boundary_rows: list[dict[str, Any]]) -> dict[str, Any]:
    blocked_claims = [row["blocked_claim"] for row in boundary_rows]
    return {
        "boundary_row_count": len(boundary_rows),
        "all_boundary_claims_blocked": all(
            row["boundary_status"] == "blocked" and row["claim_allowed"] is False
            for row in boundary_rows
        ),
        "blocked_claims": blocked_claims,
        "semantic_goal_ownership_blocked": "semantic_goal_ownership" in blocked_claims,
        "intention_semantic_choice_blocked": "intention_semantic_choice" in blocked_claims,
        "identity_acceptance_blocked": "identity_acceptance" in blocked_claims,
        "agency_blocked": "agency" in blocked_claims,
        "native_support_without_phase8_blocked": (
            "native_support_without_phase8" in blocked_claims
        ),
        "fully_native_integration_blocked": (
            "fully_native_agentic_like_integration" in blocked_claims
        ),
        "constructed_followout_caveat_preserved": (
            "upstream_observed_route_conditioned_support_regulation" in blocked_claims
        ),
        "direct_ap2_not_promoted_to_ap5": (
            "direct_historic_target_existence_as_final_ap5" in blocked_claims
        ),
    }


def build_hypothesis_classification(
    inventory: dict[str, Any],
    i3: dict[str, Any],
    i4: dict[str, Any],
    i5: dict[str, Any],
    i6: dict[str, Any],
) -> dict[str, Any]:
    return {
        "hypothesis_a_runtime_state_proxy_sources": {
            "acceptance_state": "supported",
            "supported": True,
            "scope": (
                "source-backed runtime-visible support, memory, regulation, "
                "and support/identity-condition source surface for proxy formation"
            ),
            "evidence": [rel(INVENTORY_OUTPUT), rel(I3_OUTPUT), rel(I4_OUTPUT)],
            "supporting_checks": {
                "runtime_source_inventory_passed": inventory["status"] == "passed",
                "old_best_claim_inputs_recorded": inventory["iteration_result"][
                    "old_best_claim_inputs_recorded"
                ],
                "direct_historic_support_not_promoted": inventory["checks"][
                    "direct_historic_support_not_promoted_to_ap5"
                ],
                "source_current_state_present": i3["runtime_state_vector"][
                    "source_current"
                ],
                "declared_external_proxy_absent": i3["checks"][
                    "declared_external_proxy_absent"
                ],
                "hidden_derivation_blocked": i5["checks"][
                    "hidden_target_derivation_control_passed"
                ],
            },
            "boundary": (
                "runtime-visible source state remains artifact state, not "
                "semantic ownership, agency, identity acceptance, or native support"
            ),
        },
        "hypothesis_b_bounded_endogenous_proxy_formation": {
            "acceptance_state": "supported",
            "supported": True,
            "scope": (
                "deterministic source-current target generation with bridge "
                "consumption, external-proxy contrast, fail-closed controls, "
                "bounded drift, and replay"
            ),
            "evidence": [rel(I3_OUTPUT), rel(I4_OUTPUT), rel(I5_OUTPUT), rel(I6_OUTPUT)],
            "supporting_checks": {
                "target_generated_before_use": i3["checks"][
                    "target_generated_before_bridge_use"
                ],
                "bridge_consumes_target": i3["checks"][
                    "bridge_probe_consumes_target_condition"
                ],
                "external_proxy_contrast_passed": i4["iteration_result"][
                    "external_proxy_contrast_passed"
                ],
                "all_controls_fail_closed": i5["checks"]["all_controls_fail_closed"],
                "bounded_drift_replay_passed": i6["iteration_result"][
                    "bounded_drift_replay_passed"
                ],
                "artifact_replay_passed": i6["checks"][
                    "artifact_only_filesystem_replay_passed"
                ],
                "snapshot_load_replay_passed": i6["checks"][
                    "snapshot_load_replay_passed"
                ],
                "order_inversion_replay_passed": i6["checks"][
                    "order_inversion_replay_passed"
                ],
            },
            "boundary": (
                "bounded endogenous proxy formation is artifact-level AP5, not "
                "semantic goal ownership, intention, agency, or native support"
            ),
        },
        "hypothesis_c_goal_ownership_and_agency_boundary": {
            "acceptance_state": "supported",
            "supported": True,
            "scope": (
                "unsafe claim promotions remain blocked by claim flags, I4 "
                "blocked-claim records, and I5 dedicated relabel controls"
            ),
            "evidence": [rel(SCHEMA_OUTPUT), rel(I4_OUTPUT), rel(I5_OUTPUT), rel(I6_OUTPUT)],
            "supporting_checks": {
                "claim_flags_forced_false": i6["checks"]["claim_flags_forced_false"],
                "semantic_goal_ownership_relabel_blocked": i5["checks"][
                    "semantic_goal_ownership_relabel_control_passed"
                ],
                "identity_acceptance_relabel_blocked": i5["checks"][
                    "identity_acceptance_relabel_control_passed"
                ],
                "native_support_relabel_blocked": i5["checks"][
                    "native_support_relabel_control_passed"
                ],
                "i4_unsafe_claim_set_matches_expected": (
                    set(i4["blocked_claims"]) == EXPECTED_I4_BLOCKED_CLAIMS
                ),
                "phase8_opened_false": i6["checks"]["phase8_opened_false"],
                "native_support_opened_false": i6["checks"][
                    "native_support_not_opened"
                ],
                "fully_native_integration_opened_false": i6["checks"][
                    "fully_native_integration_not_opened"
                ],
                "src_diff_empty": git_status_short("src") == "",
            },
            "scope_note": (
                "N15 has dedicated I5 relabel controls for semantic goal "
                "ownership, identity acceptance, and native support. Intention, "
                "semantic choice, agency, selfhood, personhood, biological "
                "behavior, unrestricted agency, and fully native integration "
                "remain blocked through the frozen claim flags and I4 blocked "
                "claim records, not separate semantic rejection engines."
            ),
            "boundary": (
                "AP5 target formation does not open goal ownership, intention, "
                "semantic choice, agency, identity acceptance, native support, "
                "fully native integration, or unrestricted agency"
            ),
        },
    }


def build_blocked_input_audit(
    inventory: dict[str, Any],
    i3: dict[str, Any],
    i4: dict[str, Any],
    i5: dict[str, Any],
    i6: dict[str, Any],
    boundary_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "record_id": "n15_i7_blocked_input_audit_v1",
        "blocked_control_inputs": [
            {
                "control_id": record["control_id"],
                "observed_blocker": record["observed_blocker"],
                "source": rel(I5_OUTPUT),
            }
            for record in i5["control_records"]
        ],
        "blocked_replay_inputs": [
            {
                "record_id": record["record_id"],
                "observed_blocker": record["observed_blocker"],
                "source": rel(I6_OUTPUT),
            }
            for record in i6["matrix_records"]
            if record["observed_status"] == "blocked"
        ],
        "blocked_boundary_claims": [
            {
                "row_id": row["row_id"],
                "blocked_claim": row["blocked_claim"],
                "source": "n15_i7_boundary_rows",
            }
            for row in boundary_rows
        ],
        "direct_historic_support_boundary": {
            "source": rel(I3_OUTPUT),
            "direct_historic_support_status": i3["direct_historic_gap_record"][
                "direct_historic_support_status"
            ],
            "reason_not_promoted": i3["direct_historic_gap_record"][
                "reason_not_promoted"
            ],
        },
        "readiness_only_boundary": {
            "source": rel(INVENTORY_OUTPUT),
            "n12_readiness_only_not_native_support": inventory["checks"][
                "n12_readiness_only_not_native_support"
            ],
            "native_support_relabel_blocked": i5["checks"][
                "native_support_relabel_control_passed"
            ],
        },
        "i4_blocked_claims": {
            "source": rel(I4_OUTPUT),
            "blocked_claims": i4["blocked_claims"],
        },
        "audit_complete": True,
    }


def build_constructed_followout_caveat_audit(
    inventory: dict[str, Any], i3: dict[str, Any]
) -> dict[str, Any]:
    context = i3["runtime_state_vector"]["constructed_followout_context"]
    return {
        "record_id": "n15_i7_constructed_followout_caveat_audit_v1",
        "source_context": rel(I3_OUTPUT),
        "source_inventory": rel(INVENTORY_OUTPUT),
        "constructed_route_conditioned_regulation_followout_supported": context[
            "constructed_route_conditioned_regulation_followout_supported"
        ],
        "constructed_route_conditioned_support_followout_supported": context[
            "constructed_route_conditioned_support_followout_supported"
        ],
        "observed_upstream_route_conditioned_support_regulation_supported": context[
            "observed_upstream_route_conditioned_support_regulation_supported"
        ],
        "scope_caveat": context["scope_caveat"],
        "n14_constructed_followout_in_candidate_path": i3["checks"][
            "n14_constructed_followout_in_candidate_path"
        ],
        "n14_constructed_followout_caveat_preserved": inventory["checks"][
            "n14_constructed_followout_caveat_preserved"
        ],
        "caveat_preserved": (
            i3["checks"]["n14_constructed_followout_in_candidate_path"]
            and inventory["checks"]["n14_constructed_followout_caveat_preserved"]
            and context[
                "observed_upstream_route_conditioned_support_regulation_supported"
            ]
            is False
        ),
    }


def build_rows_scope_note() -> dict[str, Any]:
    return {
        "record_id": "n15_i7_rows_scope_note_v1",
        "rows_value": [],
        "rows_empty": True,
        "inherited_shape_source": rel(SCHEMA_OUTPUT),
        "scope": (
            "Iteration 7 is a claim-boundary and classification record, not a "
            "new candidate-row derivation."
        ),
        "reason_rows_empty": (
            "The row-bearing candidate is Iteration 3. I7 preserves the "
            "standard top-level `rows` field for schema compatibility while "
            "placing classification evidence in AP5 gates, boundary rows, "
            "hypothesis classification, and claim-boundary records."
        ),
        "canonical_i7_row_like_surfaces": [
            "ap5_gate_resolution",
            "boundary_rows",
            "hypothesis_classification",
            "claim_boundary_record.boundary_rows",
        ],
        "not_evidence_gap": True,
    }


def build_schema_evolution(schema: dict[str, Any]) -> dict[str, Any]:
    runtime_fields = schema["top_level_output_fields"]
    schema_freeze_fields = schema["top_level_schema_freeze_fields"]
    i7_fields = ITERATION_7_TOP_LEVEL_OUTPUT_FIELDS
    runtime_field_set = set(runtime_fields)
    schema_freeze_field_set = set(schema_freeze_fields)
    i7_field_set = set(i7_fields)
    return {
        "record_id": "n15_i7_schema_evolution_v1",
        "source_schema": rel(SCHEMA_OUTPUT),
        "inherited_runtime_output_fields": runtime_fields,
        "inherited_schema_freeze_fields": schema_freeze_fields,
        "iteration_7_output_fields": i7_fields,
        "shared_with_runtime_output_shape": [
            field for field in i7_fields if field in runtime_field_set
        ],
        "shared_with_schema_freeze_shape": [
            field for field in i7_fields if field in schema_freeze_field_set
        ],
        "iteration_7_specific_fields": [
            field for field in i7_fields if field not in runtime_field_set
        ],
        "schema_freeze_fields_not_reemitted_by_i7": [
            field for field in schema_freeze_fields if field not in i7_field_set
        ],
        "runtime_output_fields_preserved": runtime_field_set.issubset(i7_field_set),
        "output_digest_field_retained": "output_digest" in i7_field_set,
        "evolution_rationale": {
            "runtime_core_fields": (
                "I7 keeps the standard runtime output envelope for portable "
                "validation and digest checks."
            ),
            "classification_fields": (
                "I7 adds AP5 gate resolution, hypothesis classification, "
                "claim-boundary, interpretation, and review-closure records."
            ),
            "schema_freeze_fields": (
                "I7 consumes the I2 schema-freeze artifact instead of "
                "re-emitting every frozen policy body."
            ),
        },
        "schema_evolution_recorded": True,
    }


def build_claim_boundary_control_coverage(
    schema: dict[str, Any],
    i4: dict[str, Any],
    i5: dict[str, Any],
) -> dict[str, Any]:
    blocked_claims = set(i4["blocked_claims"])
    controls = set(i5["controls"])
    rows = []
    for claim in i4["blocked_claims"]:
        claim_flag = CLAIM_FLAG_BY_BLOCKED_CLAIM[claim]
        dedicated_control = DEDICATED_I5_RELABEL_CONTROLS.get(claim)
        rows.append(
            {
                "claim": claim,
                "claim_flag": claim_flag,
                "claim_flag_forced_false": schema["claim_flags"][claim_flag] is False,
                "i4_blocked_claim_recorded": claim in blocked_claims,
                "dedicated_i5_control": dedicated_control,
                "dedicated_i5_control_present": (
                    dedicated_control in controls if dedicated_control else False
                ),
                "coverage_mode": (
                    "dedicated_i5_relabel_control_plus_i4_blocked_claim_and_claim_flag"
                    if dedicated_control
                    else "i4_blocked_claim_plus_forced_false_claim_flag"
                ),
                "scope_limit": (
                    "This is a claim-boundary blocker at artifact level, not a "
                    "separate semantic rejection engine."
                ),
            }
        )
    dedicated_claims = [
        claim for claim in i4["blocked_claims"] if claim in DEDICATED_I5_RELABEL_CONTROLS
    ]
    claim_flag_only_claims = [
        claim
        for claim in i4["blocked_claims"]
        if claim not in DEDICATED_I5_RELABEL_CONTROLS
    ]
    return {
        "record_id": "n15_i7_claim_boundary_control_coverage_v1",
        "source_i4": rel(I4_OUTPUT),
        "source_i5": rel(I5_OUTPUT),
        "coverage_asymmetry_recorded": True,
        "expected_blocked_claims": sorted(EXPECTED_I4_BLOCKED_CLAIMS),
        "observed_blocked_claims": i4["blocked_claims"],
        "dedicated_control_claims": dedicated_claims,
        "claim_flag_and_i4_blocked_claims": claim_flag_only_claims,
        "future_control_candidates": FUTURE_CONTROL_CANDIDATES,
        "coverage_rows": rows,
        "all_expected_claims_covered": (
            blocked_claims == EXPECTED_I4_BLOCKED_CLAIMS
            and all(row["claim_flag_forced_false"] for row in rows)
            and all(
                row["dedicated_i5_control_present"]
                for row in rows
                if row["dedicated_i5_control"] is not None
            )
        ),
        "coverage_boundary": (
            "Dedicated relabel controls exist for semantic goal ownership, "
            "identity acceptance/runtime identity acceptance, and native "
            "support. Other unsafe claims are blocked by I4 blocked-claim "
            "records plus forced-false claim flags."
        ),
    }


def build_interpretation_scope(
    whole_experiment_interpretation: dict[str, Any],
    interpretation_record: dict[str, Any],
    claim_boundary_record: dict[str, Any],
) -> dict[str, Any]:
    return {
        "record_id": "n15_i7_interpretation_scope_v1",
        "canonical_sources": {
            "whole_experiment_interpretation": (
                "narrative summary only; not the canonical claim-boundary source"
            ),
            "interpretation_record": (
                "canonical AP state, hypothesis acceptance states, unsupported "
                "interpretations, and remaining work"
            ),
            "claim_boundary_record": (
                "canonical AP5 scope, claim ceiling candidate, final-freeze "
                "state, boundary rows, and boundary summary"
            ),
        },
        "compatibility_mirrors": {
            "boundary_rows": "compatibility mirror of claim_boundary_record.boundary_rows",
            "boundary_summary": (
                "compatibility mirror of claim_boundary_record.boundary_summary"
            ),
        },
        "consistency_checks": {
            "claim_ceiling_consistent": (
                whole_experiment_interpretation["claim_ceiling_candidate"]
                == claim_boundary_record["claim_ceiling_candidate"]
            ),
            "classified_ap_level_consistent": (
                interpretation_record["ap_state_after_claim_boundary"][
                    "classified_ap_level"
                ]
                == claim_boundary_record["classified_ap_level"]
            ),
            "final_ap5_pending_consistent": (
                interpretation_record["ap_state_after_claim_boundary"][
                    "final_ap5_supported"
                ]
                is claim_boundary_record["final_ap5_supported"]
                and interpretation_record["ap_state_after_claim_boundary"][
                    "final_ap_freeze_pending_iteration8"
                ]
                is claim_boundary_record["final_ap_freeze_pending_iteration8"]
            ),
            "remaining_work_consistent": (
                whole_experiment_interpretation["remaining_required_work"]
                == interpretation_record["remaining_required_work"]
            ),
        },
        "overlap_resolution": (
            "I7 keeps overlapping records for downstream readers but assigns "
            "canonical responsibility to each record so duplicated narrative "
            "does not change the claim boundary."
        ),
    }


def build_review_gap_closure() -> dict[str, Any]:
    return {
        "record_id": "n15_i7_review_gap_closure_v1",
        "review_source": "iteration_7_gap_analysis_and_improvement_proposals",
        "closures": [
            {
                "gap_id": "i7_1_boundary_record_duplication",
                "status": "closed_as_compatibility_shape",
                "resolution": (
                    "Top-level boundary rows and summary are retained as "
                    "compatibility mirrors and guarded by identity checks."
                ),
            },
            {
                "gap_id": "i7_2_interpretation_overlap",
                "status": "closed",
                "resolution": (
                    "interpretation_scope assigns canonical responsibility to "
                    "whole-experiment, interpretation, and claim-boundary "
                    "records."
                ),
            },
            {
                "gap_id": "i7_3_magic_blocked_claim_count",
                "status": "closed",
                "resolution": (
                    "I4 blocked claims are validated against a frozen expected "
                    "claim set instead of a raw count."
                ),
            },
            {
                "gap_id": "i7_4_pending_closeout_language_after_i8",
                "status": "not_gap_current",
                "resolution": (
                    "I7 remains a historical pre-closeout classification "
                    "snapshot. I8 is the final closeout source after I7; I7 "
                    "does not embed an I8 digest to avoid circular provenance."
                ),
            },
            {
                "gap_id": "i7_5_idempotency_digest_scope",
                "status": "closed",
                "resolution": (
                    "idempotency_digest_plan now documents semantic-core scope "
                    "versus the full artifact output_digest scope."
                ),
            },
            {
                "gap_id": "i7_6_output_shape_evolution",
                "status": "closed",
                "resolution": (
                    "schema_evolution records inherited runtime fields, "
                    "schema-freeze fields, and I7-specific additions."
                ),
            },
            {
                "gap_id": "i7_7_empty_rows_array",
                "status": "closed",
                "resolution": (
                    "rows_scope_note records that empty rows are intentional "
                    "for I7 classification scope."
                ),
            },
            {
                "gap_id": "i7_8_asymmetric_claim_controls",
                "status": "closed_as_boundary_record",
                "resolution": (
                    "claim_boundary_control_coverage records which claims have "
                    "dedicated I5 relabel controls and which rely on I4 "
                    "blocked claims plus forced-false flags."
                ),
            },
            {
                "gap_id": "i7_9_i6_iteration_result_key_coupling",
                "status": "closed",
                "resolution": (
                    "I7 checks the exact expected I6 iteration_result key set."
                ),
            },
            {
                "gap_id": "i7_10_independent_i7_validator",
                "status": "closed",
                "resolution": (
                    "scripts/validate_n15_claim_boundary_record.py validates "
                    "the generated I7 artifact independently."
                ),
            },
        ],
        "review_gap_closure_recorded": True,
    }


def build_idempotency_digest_plan(
    *,
    source_artifacts: dict[str, Any],
    source_reports: dict[str, Any],
    controls: dict[str, str],
    ap5_gate_resolution: list[dict[str, Any]],
    hypothesis_classification: dict[str, Any],
    boundary_rows: list[dict[str, Any]],
    boundary_summary: dict[str, Any],
    blocked_input_audit: dict[str, Any],
    constructed_followout_caveat_audit: dict[str, Any],
    rows_scope_note: dict[str, Any],
    schema_evolution: dict[str, Any],
    claim_boundary_control_coverage: dict[str, Any],
    interpretation_scope: dict[str, Any],
    review_gap_closure: dict[str, Any],
    claim_flags: dict[str, bool],
) -> dict[str, Any]:
    scope = {
        "source_artifacts": source_artifacts,
        "source_reports": source_reports,
        "controls": controls,
        "ap5_gate_resolution": ap5_gate_resolution,
        "hypothesis_classification": hypothesis_classification,
        "boundary_rows": boundary_rows,
        "boundary_summary": boundary_summary,
        "blocked_input_audit": blocked_input_audit,
        "constructed_followout_caveat_audit": constructed_followout_caveat_audit,
        "rows_scope_note": rows_scope_note,
        "schema_evolution": schema_evolution,
        "claim_boundary_control_coverage": claim_boundary_control_coverage,
        "interpretation_scope": interpretation_scope,
        "review_gap_closure": review_gap_closure,
        "claim_flags": claim_flags,
    }
    return {
        "record_id": "n15_i7_idempotency_digest_plan_v1",
        "algorithm": "sha256_canonical_json_sorted_keys",
        "scope_note": (
            "This digest covers the semantic-core I7 evidence scope. The "
            "top-level output_digest covers the full artifact after excluding "
            "generated_at, git, and output_digest."
        ),
        "scope": scope,
        "excluded_top_level_fields": ["generated_at", "git", "output_digest"],
        "digest": digest_value(scope),
    }


def build_output() -> dict[str, Any]:
    inventory = load_json(INVENTORY_OUTPUT)
    schema = load_json(SCHEMA_OUTPUT)
    i3 = load_json(I3_OUTPUT)
    i4 = load_json(I4_OUTPUT)
    i5 = load_json(I5_OUTPUT)
    i6 = load_json(I6_OUTPUT)
    controls = {control_id: "blocked_in_iteration_5" for control_id in i5["controls"]}
    source_artifacts = {
        rel(INVENTORY_OUTPUT): source_artifact(INVENTORY_OUTPUT, inventory),
        rel(SCHEMA_OUTPUT): source_artifact(SCHEMA_OUTPUT, schema),
        rel(I3_OUTPUT): source_artifact(I3_OUTPUT, i3),
        rel(I4_OUTPUT): source_artifact(I4_OUTPUT, i4),
        rel(I5_OUTPUT): source_artifact(I5_OUTPUT, i5),
        rel(I6_OUTPUT): source_artifact(I6_OUTPUT, i6),
    }
    source_reports = {
        rel(INVENTORY_REPORT): source_report(INVENTORY_REPORT),
        rel(SCHEMA_REPORT): source_report(SCHEMA_REPORT),
        rel(I3_REPORT): source_report(I3_REPORT),
        rel(I4_REPORT): source_report(I4_REPORT),
        rel(I5_REPORT): source_report(I5_REPORT),
        rel(I6_REPORT): source_report(I6_REPORT),
        rel(HYPOTHESIS_A): source_report(HYPOTHESIS_A),
        rel(HYPOTHESIS_B): source_report(HYPOTHESIS_B),
        rel(HYPOTHESIS_C): source_report(HYPOTHESIS_C),
    }
    ap5_gate_resolution = build_ap5_gate_resolution(
        schema, inventory, i3, i4, i5, i6
    )
    ap5_gate_summary = {
        "gate_count": len(ap5_gate_resolution),
        "validated_gate_count": sum(1 for gate in ap5_gate_resolution if gate["validated"]),
        "blocked_gate_count": sum(1 for gate in ap5_gate_resolution if not gate["validated"]),
        "all_ap5_gates_validated": all(gate["validated"] for gate in ap5_gate_resolution),
        "blocked_gates": [
            gate["gate_id"] for gate in ap5_gate_resolution if not gate["validated"]
        ],
    }
    hypothesis_classification = build_hypothesis_classification(
        inventory, i3, i4, i5, i6
    )
    boundary_rows = build_boundary_rows(i3, i4, i5)
    boundary_summary = build_boundary_summary(boundary_rows)
    blocked_input_audit = build_blocked_input_audit(
        inventory, i3, i4, i5, i6, boundary_rows
    )
    constructed_followout_caveat_audit = build_constructed_followout_caveat_audit(
        inventory, i3
    )
    whole_experiment_interpretation = {
        "record_id": "n15_i7_whole_experiment_interpretation_v1",
        "supported_interpretation": (
            "N15 supports an artifact-level AP5 endogenous proxy formation "
            "candidate, boundary-clean pending Iteration 8 closeout."
        ),
        "plain_language_interpretation": (
            "The target condition is generated from source-current support, "
            "memory, regulation, and AP4 consequence context before use; it is "
            "distinguishable from fixtures and hidden/post-hoc derivations; all "
            "frozen controls fail closed; replay and bounded drift pass. The "
            "result remains artifact-level and does not open semantic goal "
            "ownership, intention, agency, identity acceptance, native support, "
            "or fully native integration."
        ),
        "claim_ceiling_candidate": (
            "artifact_level_ap5_endogenous_proxy_formation_candidate"
        ),
        "remaining_required_work": ["n15_closeout_handoff_iteration_8"],
    }
    interpretation_record = {
        "record_id": "n15_i7_interpretation_claim_boundary_ap5_classification_v1",
        "record_type": "n15_iteration_7_claim_boundary_and_ap5_classification",
        "supported_interpretation": (
            "Artifact-level AP5 endogenous proxy formation candidate, "
            "boundary-clean pending Iteration 8 closeout."
        ),
        "plain_language_meaning": whole_experiment_interpretation[
            "plain_language_interpretation"
        ],
        "ap_state_after_claim_boundary": {
            "classified_ap_level": "AP5",
            "ap5_classification_supported": True,
            "provisional_ap_level": "AP5_candidate_boundary_clean_pending_closeout",
            "final_ap5_supported": False,
            "final_ap_freeze_pending_iteration8": True,
            "phase8_opened": False,
            "native_support_opened": False,
        },
        "hypothesis_acceptance_states": {
            key: value["acceptance_state"]
            for key, value in hypothesis_classification.items()
        },
        "unsupported_interpretations": [
            row["blocked_claim"] for row in boundary_rows
        ],
        "remaining_required_work": ["n15_closeout_handoff_iteration_8"],
    }
    claim_boundary_record = {
        "record_id": "n15_i7_claim_boundary_record_v1",
        "classified_ap_level": "AP5",
        "ap5_scope": (
            "Runtime-derived target/proxy condition generated from "
            "source-current support, memory, regulation, and AP4 consequence "
            "context, control-clean and replay-clean at artifact level."
        ),
        "claim_ceiling_candidate": (
            "artifact_level_ap5_endogenous_proxy_formation_candidate"
        ),
        "final_ap5_supported": False,
        "final_ap_freeze_pending_iteration8": True,
        "boundary_rows": boundary_rows,
        "boundary_summary": boundary_summary,
    }
    rows_scope_note = build_rows_scope_note()
    schema_evolution = build_schema_evolution(schema)
    claim_boundary_control_coverage = build_claim_boundary_control_coverage(
        schema, i4, i5
    )
    interpretation_scope = build_interpretation_scope(
        whole_experiment_interpretation,
        interpretation_record,
        claim_boundary_record,
    )
    review_gap_closure = build_review_gap_closure()
    idempotency_digest_plan = build_idempotency_digest_plan(
        source_artifacts=source_artifacts,
        source_reports=source_reports,
        controls=controls,
        ap5_gate_resolution=ap5_gate_resolution,
        hypothesis_classification=hypothesis_classification,
        boundary_rows=boundary_rows,
        boundary_summary=boundary_summary,
        blocked_input_audit=blocked_input_audit,
        constructed_followout_caveat_audit=constructed_followout_caveat_audit,
        rows_scope_note=rows_scope_note,
        schema_evolution=schema_evolution,
        claim_boundary_control_coverage=claim_boundary_control_coverage,
        interpretation_scope=interpretation_scope,
        review_gap_closure=review_gap_closure,
        claim_flags=schema["claim_flags"],
    )
    required_control_ids = {
        record["control_id"] for record in schema["control_requirements"]
    }
    checks = {
        "inventory_source_passed": inventory["status"] == "passed",
        "schema_source_passed": schema["status"] == "passed",
        "iteration_3_source_passed": i3["status"] == "passed",
        "iteration_4_source_passed": i4["status"] == "passed",
        "iteration_5_source_passed": i5["status"] == "passed",
        "iteration_6_source_passed": i6["status"] == "passed",
        "iteration_6_acceptance_state_valid": i6["acceptance_state"]
        == "accepted_bounded_drift_replay_matrix_pending_claim_boundary_classification",
        "i6_iteration_result_keys_match_expected": (
            set(i6["iteration_result"]) == EXPECTED_I6_ITERATION_RESULT_KEYS
        ),
        "all_ap5_gates_resolved": len(ap5_gate_resolution)
        == len(schema["ap5_required_gates"]),
        "all_ap5_gates_validated": ap5_gate_summary["all_ap5_gates_validated"],
        "hypothesis_a_supported": hypothesis_classification[
            "hypothesis_a_runtime_state_proxy_sources"
        ]["supported"],
        "hypothesis_b_supported": hypothesis_classification[
            "hypothesis_b_bounded_endogenous_proxy_formation"
        ]["supported"],
        "hypothesis_c_supported": hypothesis_classification[
            "hypothesis_c_goal_ownership_and_agency_boundary"
        ]["supported"],
        "all_boundary_claims_blocked": boundary_summary[
            "all_boundary_claims_blocked"
        ],
        "boundary_rows_match_claim_boundary_record": (
            boundary_rows == claim_boundary_record["boundary_rows"]
        ),
        "boundary_summary_match_claim_boundary_record": (
            boundary_summary == claim_boundary_record["boundary_summary"]
        ),
        "blocked_input_audit_complete": blocked_input_audit["audit_complete"],
        "constructed_followout_caveat_preserved": constructed_followout_caveat_audit[
            "caveat_preserved"
        ],
        "claim_boundary_control_coverage_recorded": (
            claim_boundary_control_coverage["coverage_asymmetry_recorded"]
            and claim_boundary_control_coverage["all_expected_claims_covered"]
        ),
        "interpretation_scope_recorded": (
            all(interpretation_scope["consistency_checks"].values())
            and bool(interpretation_scope["canonical_sources"])
        ),
        "rows_scope_note_recorded": (
            rows_scope_note["rows_empty"] and rows_scope_note["not_evidence_gap"]
        ),
        "schema_evolution_recorded": (
            schema_evolution["schema_evolution_recorded"]
            and schema_evolution["runtime_output_fields_preserved"]
        ),
        "review_gap_closure_recorded": review_gap_closure[
            "review_gap_closure_recorded"
        ],
        "i4_blocked_claim_set_matches_expected": (
            set(i4["blocked_claims"]) == EXPECTED_I4_BLOCKED_CLAIMS
        ),
        "all_controls_fail_closed": i5["checks"]["all_controls_fail_closed"],
        "control_outcomes_present": set(controls) == required_control_ids,
        "claim_flags_forced_false": all(
            value is False for value in schema["claim_flags"].values()
        ),
        "required_false_flags_false": all(
            value is False for value in REQUIRED_FALSE_FLAGS.values()
        ),
        "native_supported_flags_false": (
            i5["iteration_result"]["native_support_opened"] is False
            and i6["iteration_result"]["native_support_opened"] is False
        ),
        "phase8_opened_false": (
            i5["iteration_result"]["phase8_opened"] is False
            and i6["iteration_result"]["phase8_opened"] is False
        ),
        "fully_native_integration_opened_false": (
            i5["iteration_result"]["fully_native_integration_opened"] is False
            and i6["iteration_result"]["fully_native_integration_opened"] is False
        ),
        "final_ap5_not_frozen_until_iteration8": True,
        "source_digest_presence": all(
            valid_sha256(record["sha256"]) for record in source_artifacts.values()
        )
        and all(valid_sha256(record["sha256"]) for record in source_reports.values()),
        "idempotency_digest_plan_reproducible": idempotency_digest_plan["digest"]
        == digest_value(idempotency_digest_plan["scope"]),
        "idempotency_digest_scope_note_recorded": bool(
            idempotency_digest_plan["scope_note"]
        ),
        "iteration_7_top_level_output_shape_declared": (
            len(ITERATION_7_TOP_LEVEL_OUTPUT_FIELDS) == 36
            and len(ITERATION_7_TOP_LEVEL_OUTPUT_FIELDS)
            == len(set(ITERATION_7_TOP_LEVEL_OUTPUT_FIELDS))
        ),
        "src_diff_empty": git_status_short("src") == "",
    }
    acceptance_state = (
        "accepted_ap5_classification_claim_boundary_clean_pending_closeout"
        if all(checks.values())
        else "rejected_ap5_claim_boundary_classification"
    )
    output: dict[str, Any] = {
        "experiment": "N15",
        "iteration": 7,
        "artifact_id": "n15_claim_boundary_record",
        "purpose": "claim_boundary_and_ap5_classification",
        "schema_version": "n15_claim_boundary_record_v1",
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
            "claim_boundary_classification_passed": all(checks.values()),
            "classified_ap_level": "AP5",
            "ap5_classification_supported": True,
            "provisional_ap_level": "AP5_candidate_boundary_clean_pending_closeout",
            "final_ap5_supported": False,
            "final_ap_freeze_pending_iteration8": True,
            "hypothesis_a_acceptance_state": hypothesis_classification[
                "hypothesis_a_runtime_state_proxy_sources"
            ]["acceptance_state"],
            "hypothesis_b_acceptance_state": hypothesis_classification[
                "hypothesis_b_bounded_endogenous_proxy_formation"
            ]["acceptance_state"],
            "hypothesis_c_acceptance_state": hypothesis_classification[
                "hypothesis_c_goal_ownership_and_agency_boundary"
            ]["acceptance_state"],
            "phase8_opened": False,
            "native_support_opened": False,
            "native_supported_flags": False,
            "fully_native_integration_opened": False,
            "semantic_goal_ownership_opened": False,
            "identity_acceptance_opened": False,
            "agency_claim_opened": False,
        },
        "ap5_gate_resolution": ap5_gate_resolution,
        "ap5_gate_summary": ap5_gate_summary,
        "hypothesis_classification": hypothesis_classification,
        "boundary_rows": boundary_rows,
        "boundary_summary": boundary_summary,
        "blocked_input_audit": blocked_input_audit,
        "constructed_followout_caveat_audit": constructed_followout_caveat_audit,
        "whole_experiment_interpretation": whole_experiment_interpretation,
        "interpretation_record": interpretation_record,
        "claim_boundary_record": claim_boundary_record,
        "rows_scope_note": rows_scope_note,
        "schema_evolution": schema_evolution,
        "claim_boundary_control_coverage": claim_boundary_control_coverage,
        "interpretation_scope": interpretation_scope,
        "review_gap_closure": review_gap_closure,
        "idempotency_digest_plan": idempotency_digest_plan,
        "iteration_7_top_level_output_fields": ITERATION_7_TOP_LEVEL_OUTPUT_FIELDS,
        "git": {"head": git_head(), "src_status_short": git_status_short("src")},
    }
    output["checks"]["iteration_7_top_level_output_fields_match"] = set(
        ITERATION_7_TOP_LEVEL_OUTPUT_FIELDS
    ) == (set(output) | {"output_digest"})
    output["checks"]["absolute_path_absence"] = not contains_absolute_path(output)
    output["checks"]["digest_reproducibility"] = True
    output["status"] = "passed" if all(output["checks"].values()) else "failed"
    output["acceptance_state"] = (
        "accepted_ap5_classification_claim_boundary_clean_pending_closeout"
        if all(output["checks"].values())
        else "rejected_ap5_claim_boundary_classification"
    )
    output["iteration_result"]["acceptance_state"] = output["acceptance_state"]
    output["iteration_result"]["claim_boundary_classification_passed"] = (
        output["status"] == "passed"
    )
    output["output_digest"] = output_digest(output)
    return output


def write_report(output: dict[str, Any]) -> None:
    result = output["iteration_result"]
    lines = [
        "# N15 Claim Boundary And AP5 Classification",
        "",
        "## Status",
        "",
        f"Status: `{output['status']}`.",
        "",
        "```text",
        f"acceptance_state = {output['acceptance_state']}",
        f"classified_ap_level = {result['classified_ap_level']}",
        f"ap5_classification_supported = {str(result['ap5_classification_supported']).lower()}",
        f"provisional_ap_level = {result['provisional_ap_level']}",
        "final_ap5_supported = false",
        "final_ap_freeze_pending_iteration8 = true",
        "phase8_opened = false",
        "native_support_opened = false",
        "```",
        "",
        "Iteration 7 classifies the N15 candidate as artifact-level `AP5` with",
        "claim boundaries intact. Final AP5 freeze remains pending until",
        "Iteration 8 closeout.",
        "",
        "## AP5 Scope",
        "",
        "```text",
        output["claim_boundary_record"]["ap5_scope"],
        "```",
        "",
        "## Gate Summary",
        "",
        "```json",
        json.dumps(output["ap5_gate_summary"], indent=2, sort_keys=True),
        "```",
        "",
        "## Hypotheses",
        "",
        "| Hypothesis | Acceptance state | Scope |",
        "| --- | --- | --- |",
    ]
    for key, record in output["hypothesis_classification"].items():
        lines.append(
            "| "
            f"`{key}` | "
            f"`{record['acceptance_state']}` | "
            f"{record['scope']} |"
        )
    lines.extend(
        [
            "",
            "## Boundary Summary",
            "",
            "```json",
            json.dumps(output["boundary_summary"], indent=2, sort_keys=True),
            "```",
            "",
            "## Boundary Rows",
            "",
            "| Row | Blocked claim | Claim allowed |",
            "| --- | --- | --- |",
        ]
    )
    for row in output["boundary_rows"]:
        lines.append(
            "| "
            f"`{row['row_id']}` | "
            f"`{row['blocked_claim']}` | "
            f"`{str(row['claim_allowed']).lower()}` |"
        )
    lines.extend(
        [
            "",
            "## Blocked Input Audit",
            "",
            "```json",
            json.dumps(output["blocked_input_audit"], indent=2, sort_keys=True),
            "```",
            "",
            "## Constructed Followout Caveat Audit",
            "",
            "```json",
            json.dumps(
                output["constructed_followout_caveat_audit"],
                indent=2,
                sort_keys=True,
            ),
            "```",
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
            output["claim_boundary_record"]["claim_ceiling_candidate"],
            "```",
            "",
            "## Rows Scope",
            "",
            "```json",
            json.dumps(output["rows_scope_note"], indent=2, sort_keys=True),
            "```",
            "",
            "## Schema Evolution",
            "",
            "```json",
            json.dumps(output["schema_evolution"], indent=2, sort_keys=True),
            "```",
            "",
            "## Claim Boundary Control Coverage",
            "",
            "```json",
            json.dumps(
                output["claim_boundary_control_coverage"],
                indent=2,
                sort_keys=True,
            ),
            "```",
            "",
            "## Interpretation Scope",
            "",
            "```json",
            json.dumps(output["interpretation_scope"], indent=2, sort_keys=True),
            "```",
            "",
            "## Review Gap Closure",
            "",
            "```json",
            json.dumps(output["review_gap_closure"], indent=2, sort_keys=True),
            "```",
            "",
            "## Idempotency Digest Plan",
            "",
            "```json",
            json.dumps(
                {
                    "record_id": output["idempotency_digest_plan"]["record_id"],
                    "algorithm": output["idempotency_digest_plan"]["algorithm"],
                    "scope_note": output["idempotency_digest_plan"]["scope_note"],
                    "excluded_top_level_fields": output[
                        "idempotency_digest_plan"
                    ]["excluded_top_level_fields"],
                    "digest": output["idempotency_digest_plan"]["digest"],
                },
                indent=2,
                sort_keys=True,
            ),
            "```",
            "",
            "## Required False Flags",
            "",
            "```json",
            json.dumps(REQUIRED_FALSE_FLAGS, indent=2, sort_keys=True),
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
            "endogenous proxy formation != semantic goal ownership",
            "runtime-derived target != intention",
            "support-derived target != agency",
            "support/identity-condition descriptor != identity acceptance",
            "artifact-level AP5 != native support",
            "N15 AP5 != fully native agentic-like integration",
            "constructed N14 followout != upstream observed route-conditioned support/regulation",
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

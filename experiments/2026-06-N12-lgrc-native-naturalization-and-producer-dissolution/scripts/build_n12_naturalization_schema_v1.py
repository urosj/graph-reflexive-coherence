#!/usr/bin/env python3
"""Build N12 Iteration 2 naturalization schema."""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = (
    ROOT
    / "experiments"
    / "2026-06-N12-lgrc-native-naturalization-and-producer-dissolution"
)
OUTPUTS = EXPERIMENT / "outputs"
REPORTS = EXPERIMENT / "reports"

ITERATION_1_OUTPUT = OUTPUTS / "n12_native_naturalization_inventory.json"
ITERATION_1_REPORT = REPORTS / "n12_native_naturalization_inventory.md"

OUTPUT_PATH = OUTPUTS / "n12_naturalization_schema_v1.json"
REPORT_PATH = REPORTS / "n12_naturalization_schema_v1.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N12-lgrc-native-naturalization-and-producer-dissolution/"
    "scripts/build_n12_naturalization_schema_v1.py"
)

CLAIM_FLAGS_FORCED_FALSE = {
    "agency_claim_allowed": False,
    "intention_claim_allowed": False,
    "semantic_goal_ownership_claim_allowed": False,
    "semantic_goal_understanding_claim_allowed": False,
    "identity_acceptance_claim_allowed": False,
    "runtime_identity_acceptance_claim_allowed": False,
    "rc_identity_collapse_claim_allowed": False,
    "aco_like_claim_allowed": False,
    "ant_colony_claim_allowed": False,
    "biological_claim_allowed": False,
    "personhood_claim_allowed": False,
    "unrestricted_agency_claim_allowed": False,
    "fully_native_agentic_like_integration_claim_allowed": False,
    "native_support_opened": False,
}

FINAL_ROW_FIELDS = [
    "row_id",
    "source_experiment",
    "source_iteration",
    "source_artifact",
    "source_report",
    "source_sha256",
    "source_report_sha256",
    "source_gap_rows",
    "source_contract_rows",
    "source_gap_row_summaries",
    "source_row_digest",
    "mechanism_name",
    "mechanism_role",
    "secondary_tags",
    "producer_decision_fields",
    "bookkeeping_fields",
    "runtime_visible_surfaces",
    "runtime_visible_inputs",
    "contract_runtime_visible_inputs",
    "budget_surfaces",
    "thresholds_to_serialize",
    "native_gap",
    "native_policy_name",
    "record_schema_sketch",
    "covered_policy_records",
    "primary_disposition",
    "nat_level",
    "phase8_ready",
    "phase8_readiness_source",
    "phase8_decision_source",
    "phase8_order_source",
    "claim_ceiling",
    "blocked_claims",
    "missing_gates",
    "non_rc_quantity_audit",
    "artifact_replay_requirements",
    "claim_boundary_controls",
    "ordering_requirements",
    "stale_context_blockers",
    "n11_native_supported",
    "n11_native_support_scope",
    "mutation_boundary",
    "producer_or_policy_may_schedule_only",
    "step_or_topology_event_owns_state_mutation",
    "default_off_flags",
    "enabled_validated_supported_separation",
    "idempotency_digest_plan",
    "telemetry_requirements",
    "snapshot_replay_requirements",
    "negative_controls",
    "compatibility_tests",
    "claim_flags_forced_false",
    "src_diff_empty",
    "native_supported_flags_false",
    "phase8_opened_false",
    "row_digest",
]


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


def nat_ladder() -> dict[str, dict[str, Any]]:
    return {
        "NAT0": {
            "name": "producer_only_artifact_scaffold",
            "definition": "producer-only artifact scaffold",
            "phase8_ready": False,
            "native_support": False,
        },
        "NAT1": {
            "name": "source_backed_producer_pattern",
            "definition": "source-backed producer pattern",
            "phase8_ready": False,
            "native_support": False,
        },
        "NAT2": {
            "name": "replayable_producer_pattern_with_controls",
            "definition": "replayable producer pattern with controls",
            "phase8_ready": False,
            "native_support": False,
        },
        "NAT3": {
            "name": "native_contract_candidate",
            "definition": (
                "native contract candidate; policy surface is named and "
                "plausible but one or more readiness gates remain missing"
            ),
            "phase8_ready": False,
            "native_support": False,
        },
        "NAT4": {
            "name": "phase8_ready_native_policy_candidate",
            "definition": (
                "Phase 8-ready native policy candidate with all readiness "
                "gates explicit, no implementation, and no native support claim"
            ),
            "phase8_ready": True,
            "native_support": False,
        },
        "NAT5": {
            "name": "native_implementation_not_integrated",
            "definition": (
                "native implementation exists but is not integrated into "
                "agentic-like composition"
            ),
            "phase8_ready": None,
            "native_support": "requires_separate_phase8_source",
        },
        "NAT6": {
            "name": "native_implementation_validates_in_composition",
            "definition": "native implementation validates within composition replay",
            "phase8_ready": None,
            "native_support": "requires_separate_phase8_source",
        },
    }


def field_schema() -> dict[str, dict[str, str]]:
    return {
        "row_id": {"type": "string", "required": "true"},
        "source_experiment": {"type": "string", "required": "true"},
        "source_iteration": {"type": "integer|string", "required": "true"},
        "source_artifact": {"type": "path", "required": "true"},
        "source_report": {"type": "path", "required": "true"},
        "source_sha256": {"type": "sha256", "required": "true"},
        "source_report_sha256": {"type": "sha256", "required": "true"},
        "source_gap_rows": {"type": "list[string]", "required": "true"},
        "source_contract_rows": {"type": "list[string]", "required": "true"},
        "source_gap_row_summaries": {"type": "list[object]", "required": "true"},
        "source_row_digest": {"type": "sha256|null", "required": "true"},
        "mechanism_name": {"type": "string", "required": "true"},
        "mechanism_role": {"type": "string", "required": "true"},
        "secondary_tags": {"type": "list[string]", "required": "true"},
        "producer_decision_fields": {"type": "list[string]", "required": "true"},
        "bookkeeping_fields": {"type": "list[string]", "required": "true"},
        "runtime_visible_surfaces": {"type": "list[string]", "required": "true"},
        "runtime_visible_inputs": {"type": "list[string]", "required": "for_NAT4"},
        "contract_runtime_visible_inputs": {
            "type": "list[string]",
            "required": "true",
        },
        "budget_surfaces": {"type": "list[string]", "required": "true"},
        "thresholds_to_serialize": {"type": "list[string]", "required": "true"},
        "native_gap": {"type": "string|null", "required": "true"},
        "native_policy_name": {"type": "string|null", "required": "for_NAT4"},
        "record_schema_sketch": {"type": "object|null", "required": "for_NAT4"},
        "covered_policy_records": {"type": "list[string]", "required": "true"},
        "primary_disposition": {"type": "enum", "required": "true"},
        "nat_level": {"type": "NAT0..NAT6", "required": "true"},
        "phase8_ready": {"type": "boolean", "required": "true"},
        "phase8_readiness_source": {"type": "string|null", "required": "true"},
        "phase8_decision_source": {"type": "string|null", "required": "true"},
        "phase8_order_source": {"type": "object|null", "required": "true"},
        "claim_ceiling": {"type": "string", "required": "true"},
        "blocked_claims": {"type": "list[string]", "required": "true"},
        "missing_gates": {"type": "list[string]", "required": "true"},
        "non_rc_quantity_audit": {"type": "object", "required": "true"},
        "artifact_replay_requirements": {"type": "list[string]", "required": "true"},
        "claim_boundary_controls": {"type": "list[string]", "required": "true"},
        "ordering_requirements": {"type": "list[string]", "required": "true"},
        "stale_context_blockers": {"type": "list[string]", "required": "true"},
        "n11_native_supported": {"type": "boolean|null", "required": "true"},
        "n11_native_support_scope": {"type": "string|null", "required": "true"},
        "mutation_boundary": {"type": "object", "required": "for_NAT4"},
        "producer_or_policy_may_schedule_only": {
            "type": "boolean|null",
            "required": "for_NAT4",
        },
        "step_or_topology_event_owns_state_mutation": {
            "type": "boolean|null",
            "required": "for_NAT4",
        },
        "default_off_flags": {"type": "object", "required": "for_NAT4"},
        "enabled_validated_supported_separation": {
            "type": "object",
            "required": "for_NAT4",
        },
        "idempotency_digest_plan": {"type": "object", "required": "for_NAT4"},
        "telemetry_requirements": {"type": "list[string]", "required": "for_NAT4"},
        "snapshot_replay_requirements": {
            "type": "list[string]",
            "required": "for_NAT4",
        },
        "negative_controls": {"type": "list[string]", "required": "true"},
        "compatibility_tests": {"type": "list[string]", "required": "for_NAT4"},
        "claim_flags_forced_false": {"type": "object", "required": "true"},
        "src_diff_empty": {"type": "boolean", "required": "for_NAT4"},
        "native_supported_flags_false": {"type": "boolean", "required": "for_NAT4"},
        "phase8_opened_false": {"type": "boolean", "required": "for_NAT4"},
        "row_digest": {"type": "sha256", "required": "true"},
    }


def build_output() -> dict[str, Any]:
    iteration1 = load_json(ITERATION_1_OUTPUT)
    ladder = nat_ladder()
    primary_dispositions = [
        "scaffold",
        "native_absorption_candidate",
        "theory_sensitive_blocker",
        "blocked_missing_source_or_gate",
    ]
    nat4_required_gates = [
        "native_policy_name",
        "record_schema_sketch",
        "default_off_flags",
        "enabled_validated_supported_separation",
        "idempotency_digest_plan",
        "runtime_visible_inputs",
        "budget_surfaces",
        "telemetry_requirements",
        "snapshot_replay_requirements",
        "negative_controls",
        "compatibility_tests",
        "claim_flags_forced_false",
        "non_rc_quantity_audit",
        "mutation_boundary",
        "producer_or_policy_may_schedule_only",
        "step_or_topology_event_owns_state_mutation",
        "src_diff_empty",
        "native_supported_flags_false",
        "phase8_opened_false",
    ]
    checks = {
        "iteration_1_passed": iteration1["status"] == "passed",
        "final_row_fields_declared": set(FINAL_ROW_FIELDS).issuperset(
            set(field_schema().keys())
        ),
        "primary_disposition_non_overlapping": "phase8_ready_contract"
        not in primary_dispositions,
        "phase8_ready_is_derived_from_nat4": all(
            (info["phase8_ready"] is True) == (level == "NAT4")
            for level, info in ladder.items()
            if level not in {"NAT5", "NAT6"}
        )
        and all(
            ladder[level]["phase8_ready"] is None for level in {"NAT5", "NAT6"}
        ),
        "nat4_has_no_implementation_flags": all(
            gate in nat4_required_gates
            for gate in [
                "src_diff_empty",
                "native_supported_flags_false",
                "phase8_opened_false",
            ]
        ),
        "nat4_has_mutation_boundary": all(
            gate in nat4_required_gates
            for gate in [
                "mutation_boundary",
                "producer_or_policy_may_schedule_only",
                "step_or_topology_event_owns_state_mutation",
            ]
        ),
        "nat4_gates_represented_in_field_schema": all(
            gate in field_schema()
            for gate in [
                "native_policy_name",
                "record_schema_sketch",
                "runtime_visible_inputs",
                "src_diff_empty",
                "native_supported_flags_false",
                "phase8_opened_false",
            ]
        ),
        "iteration_1_traceability_fields_preserved": all(
            field in field_schema()
            for field in [
                "secondary_tags",
                "thresholds_to_serialize",
                "source_gap_rows",
                "source_contract_rows",
                "source_gap_row_summaries",
                "source_row_digest",
                "n11_native_supported",
                "n11_native_support_scope",
                "phase8_decision_source",
                "phase8_order_source",
                "phase8_readiness_source",
                "artifact_replay_requirements",
                "claim_boundary_controls",
                "contract_runtime_visible_inputs",
                "covered_policy_records",
                "ordering_requirements",
                "stale_context_blockers",
            ]
        ),
        "non_rc_quantity_audit_required": "non_rc_quantity_audit"
        in FINAL_ROW_FIELDS,
        "claim_flags_forced_false": all(
            value is False for value in CLAIM_FLAGS_FORCED_FALSE.values()
        ),
        "src_clean": git_status_short("src") == "",
    }
    output: dict[str, Any] = {
        "schema": "n12_naturalization_schema_v1",
        "experiment": "2026-06-N12-lgrc-native-naturalization-and-producer-dissolution",
        "iteration": 2,
        "purpose": "naturalization_schema_and_ladder",
        "status": "passed" if all(checks.values()) else "failed",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "command": COMMAND,
        "git": {
            "head": git_head(),
            "src_status_short": git_status_short("src"),
            "src_clean": git_status_short("src") == "",
        },
        "source_artifacts": {
            "iteration_1_inventory": {
                "path": rel(ITERATION_1_OUTPUT),
                "sha256": digest_file(ITERATION_1_OUTPUT),
                "status": iteration1["status"],
                "output_digest": iteration1["output_digest"],
            },
            "iteration_1_report": {
                "path": rel(ITERATION_1_REPORT),
                "sha256": digest_file(ITERATION_1_REPORT),
                "status": None,
                "output_digest": None,
            },
        },
        "nat_ladder": ladder,
        "primary_dispositions": primary_dispositions,
        "secondary_tags": [
            "producer_mediated",
            "validator_local",
            "bookkeeping_only",
            "native_supported_selection_only",
            "native_policy_gap",
            "cross_cutting_contract",
        ],
        "phase8_ready_derivation": {
            "rule": "phase8_ready is true only when nat_level = NAT4",
            "not_primary_disposition": True,
        },
        "provisional_to_final_field_mapping": {
            "provisional_primary_disposition": "primary_disposition",
            "provisional_nat_level": "nat_level",
            "provisional_phase8_ready": "phase8_ready",
        },
        "iteration_1_fields_preserved_in_final_schema": [
            "secondary_tags",
            "thresholds_to_serialize",
            "source_gap_rows",
            "source_contract_rows",
            "source_gap_row_summaries",
            "source_row_digest",
            "n11_native_supported",
            "n11_native_support_scope",
            "phase8_decision_source",
            "phase8_order_source",
            "phase8_readiness_source",
            "artifact_replay_requirements",
            "claim_boundary_controls",
            "contract_runtime_visible_inputs",
            "covered_policy_records",
            "ordering_requirements",
            "stale_context_blockers",
        ],
        "final_row_fields": FINAL_ROW_FIELDS,
        "field_schema": field_schema(),
        "nat3_gates": {
            "meaning": (
                "Plausible native contract target, but not Phase 8-ready "
                "until all NAT4 gates are explicit."
            ),
            "required": [
                "source_backed_mechanism",
                "native_policy_name_or_candidate_name",
                "native_gap_named",
                "missing_gates_recorded",
                "claim_flags_forced_false",
            ],
        },
        "nat4_gates": {
            "meaning": "Phase 8-ready native policy candidate, no implementation.",
            "required": nat4_required_gates,
        },
        "non_rc_quantity_audit_schema": {
            "required": True,
            "questions": [
                "is mechanism expressible as RC causality/coherence/geometry/flux/scheduling/lineage/budget?",
                "is mechanism only producer bookkeeping?",
                "does decay, relaxation, or response sizing conserve or debit an accounted quantity?",
                "does candidate require a new scalar state outside RC accounting?",
                "if extra quantity is required, what NAT4 blocker prevents readiness?",
            ],
            "candidate_specific_questions": {
                "route_conductance_memory": [
                    "is memory a coherence, geometry, or flux effect?",
                    "is it only producer bookkeeping?",
                    "does decay or relaxation conserve an accounted quantity?",
                    "does it require a new scalar state outside RC accounting?",
                ],
                "response_magnitude": [
                    "is proxy measurement a derived observable or new state?",
                    "is target band exogenous or runtime-visible policy?",
                    "is response gain serialized and replayable?",
                    "does correction debit node-plus-packet budget?",
                    "does response sizing require hidden optimization or external controller state?",
                ],
            },
            "nat4_rejection_rule": "unaccounted_non_rc_quantity_required",
        },
        "mutation_boundary_schema": {
            "required_for_nat4": True,
            "fields": [
                "mutation_boundary",
                "producer_or_policy_may_schedule_only",
                "step_or_topology_event_owns_state_mutation",
            ],
            "rule": (
                "Native policy may schedule or record only unless the committed "
                "step/topology event boundary owns the state mutation."
            ),
        },
        "claim_flags_forced_false": CLAIM_FLAGS_FORCED_FALSE,
        "rejection_rules": {
            "producer_scaffold_relabelled_native": "blocked",
            "artifact_only_replay_relabelled_native": "blocked",
            "native_absorption_candidate_relabelled_native_support": "blocked",
            "non_rc_quantity_required": "blocked",
            "hidden_producer_mutation": "blocked",
            "budget_surface_ambiguity": "blocked",
            "claim_promotion": "blocked",
            "phase8_opened_inside_n12": "blocked",
        },
        "planned_iteration_artifacts": {
            "iteration_3_route_memory": [
                "outputs/n12_route_conductance_memory_candidate.json",
                "reports/n12_route_conductance_memory_candidate.md",
                "scripts/build_n12_route_conductance_memory_candidate.py",
            ],
            "iteration_4_response_magnitude": [
                "outputs/n12_response_magnitude_candidate.json",
                "reports/n12_response_magnitude_candidate.md",
                "scripts/build_n12_response_magnitude_candidate.py",
            ],
            "iteration_5_identity_boundary": [
                "outputs/n12_identity_acceptance_boundary.json",
                "reports/n12_identity_acceptance_boundary.md",
                "scripts/build_n12_identity_acceptance_boundary.py",
            ],
            "iteration_6_integration_boundary": [
                "outputs/n12_agentic_like_integration_boundary.json",
                "reports/n12_agentic_like_integration_boundary.md",
                "scripts/build_n12_agentic_like_integration_boundary.py",
            ],
            "iteration_7_readiness": [
                "outputs/n12_phase8_readiness_matrix.json",
                "reports/n12_phase8_readiness_matrix.md",
                "scripts/build_n12_phase8_readiness_matrix.py",
            ],
        },
        "schema_validation_scope": {
            "iteration_2_freezes_schema_only": True,
            "candidate_row_validation_starts_in_iterations_3_to_7": True,
            "note": (
                "Iteration 2 validates that schema fields, gates, and rejection "
                "rules are declared. It does not yet validate candidate rows "
                "against the final schema."
            ),
        },
        "checks": checks,
        "acceptance": {
            "status": "passed" if all(checks.values()) else "failed",
            "achieved": all(checks.values()),
            "acceptance_statement": (
                "Iteration 2 passes if the N12 schema and ladder are frozen "
                "before candidate evaluation or Phase 8 implementation work."
            ),
        },
    }
    output["output_digest"] = output_digest(output)
    return output


def write_json(output: dict[str, Any]) -> None:
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(output, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )


def write_report(output: dict[str, Any]) -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)
    lines = [
        "# N12 Naturalization Schema V1",
        "",
        f"Status: `{output['status']}`.",
        "",
        "## Summary",
        "",
        "Iteration 2 freezes the N12 NAT ladder, row schema, dispositions,",
        "NAT3/NAT4 gates, non-RC audit fields, mutation boundary fields,",
        "and rejection rules before candidate evaluation or Phase 8 work.",
        "",
        "## NAT Ladder",
        "",
        "```json",
        json.dumps(output["nat_ladder"], indent=2, sort_keys=True),
        "```",
        "",
        "## Primary Dispositions",
        "",
        "```json",
        json.dumps(output["primary_dispositions"], indent=2, sort_keys=True),
        "```",
        "",
        "## NAT4 Gates",
        "",
        "```json",
        json.dumps(output["nat4_gates"], indent=2, sort_keys=True),
        "```",
        "",
        "## Preserved Traceability Fields",
        "",
        "```json",
        json.dumps(
            output["iteration_1_fields_preserved_in_final_schema"],
            indent=2,
            sort_keys=True,
        ),
        "```",
        "",
        "## Non-RC Quantity Audit",
        "",
        "```json",
        json.dumps(output["non_rc_quantity_audit_schema"], indent=2, sort_keys=True),
        "```",
        "",
        "## Mutation Boundary",
        "",
        "```json",
        json.dumps(output["mutation_boundary_schema"], indent=2, sort_keys=True),
        "```",
        "",
        "## Rejection Rules",
        "",
        "```json",
        json.dumps(output["rejection_rules"], indent=2, sort_keys=True),
        "```",
        "",
        "## Validation Scope",
        "",
        "```json",
        json.dumps(output["schema_validation_scope"], indent=2, sort_keys=True),
        "```",
        "",
        "## Checks",
        "",
        "```json",
        json.dumps(output["checks"], indent=2, sort_keys=True),
        "```",
        "",
        "## Output Digest",
        "",
        "```text",
        output["output_digest"],
        "```",
        "",
    ]
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    output = build_output()
    write_json(output)
    write_report(output)


if __name__ == "__main__":
    main()

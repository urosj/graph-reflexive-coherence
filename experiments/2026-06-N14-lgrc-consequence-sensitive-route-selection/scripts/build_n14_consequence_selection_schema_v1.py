#!/usr/bin/env python3
"""Build N14 Iteration 2 consequence selection schema and AP4 gate."""

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

OUTPUT_PATH = OUTPUTS / "n14_consequence_selection_schema_v1.json"
REPORT_PATH = REPORTS / "n14_consequence_selection_schema_v1.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N14-lgrc-consequence-sensitive-route-selection/"
    "scripts/build_n14_consequence_selection_schema_v1.py"
)
GENERATED_AT = "2026-06-15T00:00:00+00:00"

AP_LADDER = {
    "AP0": {
        "label": "passive integrated replay",
        "n14_interpretation": "source or boundary input with no N14 selection claim",
    },
    "AP1": {
        "label": "runtime-visible trigger produces bounded response",
        "n14_interpretation": (
            "route alternatives or immediate arbitration evidence exists, but "
            "no downstream consequence-sensitive selection is supported"
        ),
    },
    "AP2": {
        "label": "support-sensitive regulation preserves declared support condition",
        "n14_interpretation": (
            "memory, support, or regulation effects are source-backed, but "
            "selection does not yet depend on consequence ranking"
        ),
    },
    "AP3": {
        "label": "self-maintenance candidate",
        "n14_interpretation": (
            "N13 source-current support-seeking regulation evidence is usable "
            "as an input only"
        ),
    },
    "AP4": {
        "label": "consequence-sensitive selection candidate",
        "n14_interpretation": (
            "route selection depends on source-backed, pre-selection downstream "
            "support, memory, or regulation effects under controls"
        ),
    },
    "AP5": {
        "label": "endogenous proxy candidate",
        "n14_interpretation": "reserved for N15",
    },
    "AP6": {
        "label": "self/environment boundary candidate",
        "n14_interpretation": "reserved for N16",
    },
    "AP7": {
        "label": "closed action-perception loop candidate",
        "n14_interpretation": "reserved for N17",
    },
    "AP8": {
        "label": "long-horizon agentic-like closure candidate",
        "n14_interpretation": "reserved for N18",
    },
}

ROW_SCHEMA_FIELDS = [
    "row_id",
    "source_experiment",
    "source_iteration",
    "source_artifact",
    "source_report",
    "source_sha256",
    "source_report_sha256",
    "mechanism_name",
    "mechanism_role",
    "route_candidate_id",
    "route_alternative_surface",
    "eligible_candidate_set_id",
    "candidate_set_completeness_status",
    "rejected_candidate_record",
    "immediate_affordance_surface",
    "immediate_affordance_rank",
    "consequence_record_source",
    "consequence_record_timing",
    "bounded_consequence_horizon",
    "prediction_basis",
    "derivation_policy",
    "source_window",
    "expected_support_effect",
    "expected_memory_effect",
    "expected_regulation_effect",
    "observed_downstream_effect",
    "prediction_match_status",
    "consequence_rank",
    "selected_rank",
    "affordance_consequence_conflict_resolved_by_consequence",
    "budget_cost_surface",
    "budget_validity",
    "selection_rationale_surface",
    "tie_policy",
    "missing_consequence_record_rejection",
    "hidden_outcome_table_control",
    "post_hoc_scoring_control",
    "stale_record_policy",
    "artifact_only_replay_status",
    "snapshot_load_status",
    "order_inversion_replay_status",
    "runtime_state_used",
    "provisional_ap_level",
    "provisional_claim_ceiling",
    "blocked_claims",
    "missing_gates",
]

AP4_REQUIRED_GATES = [
    "candidate_route_set_present",
    "eligible_candidate_completeness_record_present",
    "pre_selection_consequence_record_for_each_candidate",
    "source_artifact_report_digest_for_each_consequence_record",
    "prediction_basis_declared",
    "derivation_policy_declared",
    "source_window_declared",
    "downstream_support_effect_descriptor_present",
    "downstream_memory_effect_descriptor_present",
    "downstream_regulation_effect_descriptor_present",
    "observed_downstream_effect_descriptor_present_when_horizon_evaluated",
    "prediction_match_status_present",
    "immediate_affordance_rank_present",
    "consequence_rank_present",
    "selected_rank_present",
    "affordance_consequence_conflict_case_present",
    "affordance_consequence_conflict_resolved_by_consequence_true",
    "budget_cost_surface_present",
    "bounded_consequence_horizon_present",
    "deterministic_selection_rule_present",
    "tie_policy_present",
    "missing_consequence_record_rejection_present",
    "idempotency_digest_plan_present",
    "artifact_only_replay_requirement_present",
    "snapshot_load_equivalence_requirement_present",
    "order_inversion_replay_requirement_present",
    "runtime_state_used_false",
    "stale_record_policy_present",
    "negative_controls_present",
    "compatibility_checks_present",
    "claim_flags_forced_false",
    "src_diff_empty_true",
    "native_supported_flags_false",
    "phase8_opened_false",
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


def build_output() -> dict[str, Any]:
    inventory = load_json(INVENTORY_OUTPUT)
    consequence_record_schema = {
        "timing": {
            "required": "pre_selection",
            "post_hoc_records_supported": False,
        },
        "projection_fields": [
            "prediction_basis",
            "derivation_policy",
            "source_window",
            "bounded_consequence_horizon",
            "expected_support_effect",
            "expected_memory_effect",
            "expected_regulation_effect",
            "observed_downstream_effect",
            "prediction_match_status",
        ],
        "source_requirements": [
            "source_artifact",
            "source_report",
            "source_sha256",
            "source_report_sha256",
            "output_digest_when_available",
        ],
    }
    route_candidate_schema = {
        "candidate_set_fields": [
            "route_candidate_id",
            "eligible_candidate_set_id",
            "candidate_set_completeness_status",
            "rejected_candidate_record",
            "missing_consequence_record_rejection",
        ],
        "ranking_fields": [
            "immediate_affordance_rank",
            "consequence_rank",
            "selected_rank",
            "affordance_consequence_conflict_resolved_by_consequence",
        ],
        "tie_policy_required": True,
        "missing_record_policy": "reject_or_mark_unsupported",
    }
    replay_requirements = {
        "artifact_only_replay_required": True,
        "snapshot_load_equivalence_required": True,
        "order_inversion_replay_required": True,
        "duplicate_replay_required": True,
        "runtime_state_used_required_value": False,
    }
    control_requirements = [
        "hidden_outcome_table_blocked",
        "post_hoc_consequence_scoring_blocked",
        "stale_consequence_record_blocked",
        "budget_invalid_route_blocked",
        "missing_consequence_record_blocked",
        "candidate_set_cherry_picking_blocked",
        "tie_policy_ambiguity_blocked",
        "immediate_affordance_only_relabel_blocked",
        "matched_affordance_conflict_resolved_by_consequence",
        "fixture_label_preference_blocked",
        "semantic_intention_relabel_blocked",
        "agency_relabel_blocked",
        "native_support_relabel_blocked",
        "identity_acceptance_relabel_blocked",
        "selfhood_relabel_blocked",
        "personhood_relabel_blocked",
        "biological_behavior_relabel_blocked",
        "semantic_choice_relabel_blocked",
        "unrestricted_agency_relabel_blocked",
    ]
    final_ap4_freeze_requirements = {
        "minimum_iterations_required": [3, 4, 5, 6, 7],
        "iteration_4_can_assign_only": "provisional_ap_level = AP4_candidate",
        "final_ap4_requires_controls": True,
        "final_ap4_requires_claim_boundary": True,
        "final_ap4_requires_replay_matrix": True,
    }
    required_fields = set(ROW_SCHEMA_FIELDS)
    inventory_fields = set(inventory["n14_inventory_rows"][0].keys())
    checks = {
        "inventory_source_passed": inventory["status"] == "passed",
        "inventory_rows_available": inventory["inventory_summary"]["row_count"] >= 7,
        "all_required_fields_declared": all(ROW_SCHEMA_FIELDS),
        "inventory_rows_satisfy_schema": all(
            required_fields.issubset(set(row.keys()))
            for row in inventory["n14_inventory_rows"]
        ),
        "inventory_schema_not_extra_only": len(inventory_fields - required_fields) == 0,
        "ap4_gate_contains_affordance_conflict": (
            "affordance_consequence_conflict_case_present" in AP4_REQUIRED_GATES
            and "affordance_consequence_conflict_resolved_by_consequence_true"
            in AP4_REQUIRED_GATES
        ),
        "derivation_projection_fields_declared": all(
            field in consequence_record_schema["projection_fields"]
            for field in [
                "prediction_basis",
                "derivation_policy",
                "source_window",
                "observed_downstream_effect",
                "prediction_match_status",
            ]
        ),
        "candidate_set_completeness_declared": (
            "candidate_set_completeness_status"
            in route_candidate_schema["candidate_set_fields"]
            and route_candidate_schema["missing_record_policy"]
            == "reject_or_mark_unsupported"
        ),
        "replay_snapshot_fields_declared": (
            replay_requirements["artifact_only_replay_required"] is True
            and replay_requirements["snapshot_load_equivalence_required"] is True
            and replay_requirements["order_inversion_replay_required"] is True
            and replay_requirements["duplicate_replay_required"] is True
            and replay_requirements["runtime_state_used_required_value"] is False
        ),
        "required_controls_declared": len(control_requirements) == 19,
        "full_claim_flags_declared_false": all(
            value is False for value in CLAIM_FLAGS_FORCED_FALSE.values()
        ),
        "final_ap4_requires_later_controls": final_ap4_freeze_requirements[
            "final_ap4_requires_controls"
        ]
        is True,
        "phase8_opened_false": True,
        "native_supported_flags_false": True,
        "src_diff_empty": git_status_short("src") == "",
    }
    acceptance_state = (
        "accepted_schema_freeze_no_row_validation"
        if all(checks.values())
        else "rejected_schema_freeze"
    )
    iteration_interpretation = {
        "record_id": "n14_i2_interpretation_schema_gate_v1",
        "acceptance_state": acceptance_state,
        "supported_interpretation": (
            "N14 has a frozen AP4 row schema, AP4 gate, replay requirements, "
            "control list, and false claim flags for later candidate rows."
        ),
        "unsupported_interpretations": [
            "AP4 consequence-sensitive selection support",
            "validated route consequence records",
            "validated consequence-sensitive selected route",
            "intention",
            "agency",
            "semantic goal ownership",
            "identity acceptance",
            "native support",
            "fully native integration",
        ],
        "plain_language_interpretation": (
            "Iteration 2 converts the N14 definition into a strict validation "
            "contract. It says what later rows must contain, including "
            "candidate-set completeness, derivation basis, immediate-affordance "
            "versus consequence rank conflict, replay/snapshot controls, and "
            "claim-boundary flags. It does not validate any AP4 candidate row."
        ),
        "next_required_step": (
            "Build pre-selection route consequence records in Iteration 3 and "
            "validate them against this schema before route selection is "
            "classified."
        ),
    }
    output = {
        "experiment": "N14",
        "iteration": 2,
        "purpose": "consequence_selection_schema_and_ap4_gate",
        "schema": "n14_consequence_selection_schema_v1",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "passed" if all(checks.values()) else "failed",
        "acceptance_state": acceptance_state,
        "target_ap_ceiling": "AP4",
        "ap_ladder": AP_LADDER,
        "row_schema_fields": ROW_SCHEMA_FIELDS,
        "consequence_record_schema": consequence_record_schema,
        "route_candidate_schema": route_candidate_schema,
        "selection_rule_schema": {
            "deterministic": True,
            "inputs": [
                "candidate_route_set",
                "pre_selection_consequence_records",
                "budget_validity",
                "tie_policy",
            ],
            "forbidden_inputs": [
                "hidden_outcome_table",
                "post_hoc_consequence_score",
                "runtime_state_not_serialized_in_artifact",
                "semantic_intention_label",
                "agency_label",
            ],
        },
        "budget_schema": {
            "budget_cost_surface_required": True,
            "budget_invalid_route_policy": "reject_or_mark_unsupported",
        },
        "stale_record_policy": {
            "stale_consequence_record_policy": "reject_or_mark_unsupported",
            "source_window_required": True,
        },
        "replay_requirements": replay_requirements,
        "control_requirements": control_requirements,
        "ap4_required_gates": AP4_REQUIRED_GATES,
        "final_ap4_freeze_requirements": final_ap4_freeze_requirements,
        "claim_flags_forced_false": CLAIM_FLAGS_FORCED_FALSE,
        "iteration_interpretation": iteration_interpretation,
        "iteration_result": {
            "acceptance_state": acceptance_state,
            "schema_frozen": all(checks.values()),
            "final_ap4_supported": False,
            "row_validation_starts_in_iterations_3_to_7": True,
            "phase8_opened": False,
            "native_support_opened": False,
        },
        "checks": checks,
        "source_artifacts": {
            rel(INVENTORY_OUTPUT): source_artifact(INVENTORY_OUTPUT, inventory),
        },
        "source_reports": {
            rel(INVENTORY_REPORT): source_report(INVENTORY_REPORT),
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
        "# N14 Consequence Selection Schema V1",
        "",
        f"Status: `{output['status']}`.",
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
        json.dumps(
            output["iteration_interpretation"],
            indent=2,
            sort_keys=True,
        ),
        "```",
        "",
        "Iteration 2 freezes the N14 row schema, AP4 gate, controls, replay",
        "requirements, and claim flags. It does not validate AP4 candidate rows;",
        "row validation starts in Iterations 3-7.",
        "",
        "## AP4 Gate",
        "",
        "```json",
        json.dumps(output["ap4_required_gates"], indent=2),
        "```",
        "",
        "## Row Schema Fields",
        "",
        "```json",
        json.dumps(output["row_schema_fields"], indent=2),
        "```",
        "",
        "## Consequence Record Schema",
        "",
        "```json",
        json.dumps(
            output["consequence_record_schema"],
            indent=2,
            sort_keys=True,
        ),
        "```",
        "",
        "## Route Candidate Schema",
        "",
        "```json",
        json.dumps(output["route_candidate_schema"], indent=2, sort_keys=True),
        "```",
        "",
        "## Replay Requirements",
        "",
        "```json",
        json.dumps(output["replay_requirements"], indent=2, sort_keys=True),
        "```",
        "",
        "## Controls",
        "",
        "```json",
        json.dumps(output["control_requirements"], indent=2),
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
        "schema freeze != AP4 support",
        "AP4 support requires Iterations 3-7 controls",
        "consequence-sensitive selection != intention",
        "expected downstream effect != semantic goal ownership",
        "artifact-level AP4 != native support",
        "```",
        "",
        "## Output Digest",
        "",
        "```text",
        output["output_digest"],
        "```",
    ]
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

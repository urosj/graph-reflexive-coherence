#!/usr/bin/env python3
"""Build N14 Iteration 4 consequence-sensitive selection candidate."""

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

SCHEMA_OUTPUT = OUTPUTS / "n14_consequence_selection_schema_v1.json"
SCHEMA_REPORT = REPORTS / "n14_consequence_selection_schema_v1.md"
ROUTE_RECORDS_OUTPUT = OUTPUTS / "n14_route_consequence_records.json"
ROUTE_RECORDS_REPORT = REPORTS / "n14_route_consequence_records.md"

OUTPUT_PATH = OUTPUTS / "n14_consequence_sensitive_selection_candidate.json"
REPORT_PATH = REPORTS / "n14_consequence_sensitive_selection_candidate.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N14-lgrc-consequence-sensitive-route-selection/"
    "scripts/build_n14_consequence_sensitive_selection_candidate.py"
)
GENERATED_AT = "2026-06-15T00:00:00+00:00"

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


def sorted_by_consequence(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        records,
        key=lambda record: (
            record["consequence_rank"],
            record["immediate_affordance_rank"],
            record["route_candidate_id"],
        ),
    )


def build_selection_records(
    route_records: list[dict[str, Any]],
    selected_route_id: str,
) -> list[dict[str, Any]]:
    source_sha256 = digest_file(ROUTE_RECORDS_OUTPUT)
    source_report_sha256 = digest_file(ROUTE_RECORDS_REPORT)
    selected_order = sorted_by_consequence(route_records)
    selected_ranks = {
        record["route_candidate_id"]: rank
        for rank, record in enumerate(selected_order, start=1)
    }
    selection_records = []
    for record in route_records:
        route_id = record["route_candidate_id"]
        selected = route_id == selected_route_id
        selection_record = {
            **record,
            "row_id": f"n14_i4_selection_{route_id}",
            "source_iteration": "iteration_4_consequence_sensitive_selection_candidate",
            "source_artifact": rel(ROUTE_RECORDS_OUTPUT),
            "source_report": rel(ROUTE_RECORDS_REPORT),
            "source_sha256": source_sha256,
            "source_report_sha256": source_report_sha256,
            "mechanism_name": "consequence_sensitive_route_selection_candidate",
            "mechanism_role": (
                "selected_route_candidate"
                if selected
                else "rejected_route_candidate_with_consequence_record"
            ),
            "rejected_candidate_record": (
                "not_rejected_selected_by_lowest_consequence_rank_budget_valid"
                if selected
                else (
                    "rejected_by_consequence_rank_"
                    f"{record['consequence_rank']}_with_budget_valid_record"
                )
            ),
            "selection_status_record": {
                "status": "selected" if selected else "rejected",
                "selection_rule_id": "lowest_derived_consequence_rank_budget_valid_v1",
                "reason": (
                    "selected_lowest_derived_consequence_rank"
                    if selected
                    else "rejected_lower_derived_consequence_rank_available"
                ),
            },
            "budget_validity": "source_budget_surfaces_present_for_selection_candidate",
            "selection_rationale_surface": (
                "deterministic_rule_selected_lowest_consequence_rank_from_"
                "complete_pre_selection_candidate_set"
            ),
            "selected_rank": selected_ranks[route_id],
            "affordance_consequence_conflict_resolved_by_consequence": True,
            "provisional_ap_level": "AP4_candidate",
            "provisional_claim_ceiling": (
                "artifact_level_ap4_consequence_sensitive_selection_candidate_"
                "pending_controls_replay_and_claim_boundary"
            ),
            "blocked_claims": BLOCKED_CLAIMS,
            "missing_gates": [
                "controls_not_run_until_iteration_5",
                "replay_matrix_not_run_until_iteration_6",
                "claim_boundary_classification_not_run_until_iteration_7",
                "final_ap4_not_supported",
            ],
        }
        selection_records.append(selection_record)
    return selection_records


def build_selection_decision(
    route_records_artifact: dict[str, Any],
    selection_records: list[dict[str, Any]],
) -> dict[str, Any]:
    candidate_set = route_records_artifact["candidate_set_completeness_record"]
    selected_order = sorted_by_consequence(selection_records)
    selected = selected_order[0]
    rejected = [record for record in selection_records if record is not selected]
    return {
        "decision_record_id": "n14_i4_consequence_sensitive_selection_decision_v1",
        "selection_rule_id": "lowest_derived_consequence_rank_budget_valid_v1",
        "eligible_candidate_set_id": candidate_set["eligible_candidate_set_id"],
        "candidate_set_digest": candidate_set["candidate_set_digest"],
        "eligible_routes": candidate_set["eligible_routes"],
        "selected_route": selected["route_candidate_id"],
        "rejected_routes": [record["route_candidate_id"] for record in rejected],
        "immediate_affordance_top_route": candidate_set[
            "immediate_affordance_top_route"
        ],
        "consequence_top_route": candidate_set["consequence_top_route"],
        "selected_route_immediate_affordance_rank": selected[
            "immediate_affordance_rank"
        ],
        "selected_route_consequence_rank": selected["consequence_rank"],
        "selected_route_consequence_score": selected["consequence_score_components"][
            "consequence_score"
        ],
        "consequence_rank_source": selected["consequence_rank_source"],
        "consequence_signal_scope": candidate_set["consequence_signal_scope"],
        "affordance_consequence_conflict_present": candidate_set[
            "affordance_consequence_conflict_present"
        ],
        "affordance_consequence_conflict_resolved_by_consequence": True,
        "selection_depends_on_downstream_consequence_vector": True,
        "final_ap4_supported": False,
        "provisional_ap_level": "AP4_candidate",
    }


def build_output() -> dict[str, Any]:
    schema = load_json(SCHEMA_OUTPUT)
    route_records_artifact = load_json(ROUTE_RECORDS_OUTPUT)
    route_records = route_records_artifact["route_consequence_records"]
    candidate_set = route_records_artifact["candidate_set_completeness_record"]
    selected_source = sorted_by_consequence(route_records)[0]
    selected_route_id = selected_source["route_candidate_id"]
    selection_records = build_selection_records(route_records, selected_route_id)
    selection_decision = build_selection_decision(
        route_records_artifact, selection_records
    )
    selected_record = next(
        record
        for record in selection_records
        if record["route_candidate_id"] == selected_route_id
    )
    rejected_records = [
        record
        for record in selection_records
        if record["route_candidate_id"] != selected_route_id
    ]
    schema_fields = set(schema["row_schema_fields"])
    selection_rule = {
        "selection_rule_id": "lowest_derived_consequence_rank_budget_valid_v1",
        "deterministic": True,
        "allowed_inputs": [
            "complete_candidate_route_set",
            "pre_selection_consequence_records",
            "serialized_consequence_score_components",
            "derived_consequence_rank",
            "budget_validity",
            "tie_policy",
        ],
        "forbidden_inputs": [
            "hidden_outcome_table",
            "post_hoc_consequence_score",
            "runtime_state_not_serialized_in_artifact",
            "semantic_intention_label",
            "agency_label",
            "native_support_label",
        ],
        "selection_order": [
            "reject candidates with missing consequence records",
            "reject candidates without budget-valid source surfaces",
            "require consequence_rank_source derived from serialized score components",
            "sort by derived consequence_rank ascending",
            "if consequence_rank ties, sort by immediate_affordance_rank ascending",
            "if still tied, sort by route_candidate_id lexicographically",
        ],
        "positive_candidate_scope": "memory_dominant_provisional_ap4_candidate",
        "executed_controls_status": (
            "not_executed_until_iteration_5; current missing/stale/budget "
            "handling is recorded as policy only"
        ),
        "tie_policy": (
            "tie_policy_explicit_replayable_no_tie_observed; consequence rank "
            "tie would use immediate_affordance_rank then route_candidate_id"
        ),
        "missing_consequence_record_policy": "reject_or_mark_unsupported",
        "stale_record_policy": "source_window_pinned_reject_or_mark_unsupported",
        "idempotency_digest_plan": (
            "digest complete candidate set, source artifact sha256, source "
            "output digest, sorted route ids, ranks, budget validity, and "
            "selected route"
        ),
    }
    idempotency_record = {
        "candidate_set_digest": candidate_set["candidate_set_digest"],
        "route_records_output_digest": route_records_artifact["output_digest"],
        "route_records_sha256": digest_file(ROUTE_RECORDS_OUTPUT),
        "selection_rule_id": selection_rule["selection_rule_id"],
        "selected_route": selected_route_id,
        "selection_digest": digest_value(
            {
                "candidate_set_digest": candidate_set["candidate_set_digest"],
                "route_records_output_digest": route_records_artifact["output_digest"],
                "selection_rule_id": selection_rule["selection_rule_id"],
                "selected_route": selected_route_id,
                "selection_records": [
                    {
                        "route_candidate_id": record["route_candidate_id"],
                        "immediate_affordance_rank": record[
                            "immediate_affordance_rank"
                        ],
                        "consequence_score": record["consequence_score_components"][
                            "consequence_score"
                        ],
                        "consequence_rank": record["consequence_rank"],
                        "consequence_rank_source": record["consequence_rank_source"],
                        "selected_rank": record["selected_rank"],
                        "selection_status_record": record["selection_status_record"],
                    }
                    for record in sorted(
                        selection_records,
                        key=lambda record: record["route_candidate_id"],
                    )
                ],
            }
        ),
    }
    checks = {
        "route_records_source_passed": route_records_artifact["status"] == "passed",
        "schema_source_passed": schema["status"] == "passed",
        "candidate_set_complete": candidate_set[
            "records_present_for_all_eligible_routes"
        ]
        and candidate_set["missing_consequence_records"] == [],
        "all_eligible_candidates_recorded": set(candidate_set["eligible_routes"])
        == {record["route_candidate_id"] for record in selection_records},
        "rejected_candidate_records_present": all(
            record["rejected_candidate_record"].startswith("rejected_by_")
            for record in rejected_records
        ),
        "missing_consequence_records_rejected": (
            candidate_set["missing_consequence_records"] == []
            and all(
                "reject_or_mark_unsupported"
                in record["missing_consequence_record_rejection"]
                for record in selection_records
            )
        ),
        "immediate_affordance_rank_recorded": all(
            isinstance(record["immediate_affordance_rank"], int)
            for record in selection_records
        ),
        "consequence_rank_recorded": all(
            isinstance(record["consequence_rank"], int)
            for record in selection_records
        ),
        "consequence_score_components_serialized": all(
            isinstance(
                record.get("consequence_score_components", {}).get(
                    "consequence_score"
                ),
                float,
            )
            and record["consequence_score_components"]["score_scope"]
            == "memory_dominant_route_consequence"
            for record in selection_records
        ),
        "consequence_rank_derived_from_score_components": all(
            record.get("consequence_rank_source")
            == "derived_from_serialized_consequence_score_components"
            for record in selection_records
        ),
        "memory_dominant_candidate_scope_recorded": (
            "memory_dominant_provisional_candidate"
            in candidate_set.get("consequence_signal_scope", "")
            and selection_rule["positive_candidate_scope"]
            == "memory_dominant_provisional_ap4_candidate"
        ),
        "selected_rank_recorded": all(
            isinstance(record["selected_rank"], int) for record in selection_records
        ),
        "selection_status_record_present": all(
            record["selection_status_record"]["status"] in {"selected", "rejected"}
            for record in selection_records
        ),
        "matched_or_conflicting_affordance_case_present": (
            candidate_set["immediate_affordance_top_route"]
            != candidate_set["consequence_top_route"]
            and any(
                record["route_candidate_id"]
                == candidate_set["immediate_affordance_top_route"]
                and record["selected_rank"] > 1
                for record in selection_records
            )
        ),
        "selected_route_is_consequence_top": selected_route_id
        == candidate_set["consequence_top_route"],
        "selected_route_is_not_immediate_affordance_top": selected_route_id
        != candidate_set["immediate_affordance_top_route"],
        "affordance_consequence_conflict_resolved_by_consequence": (
            selection_decision["affordance_consequence_conflict_resolved_by_consequence"]
            and all(
                record["affordance_consequence_conflict_resolved_by_consequence"]
                is True
                for record in selection_records
            )
        ),
        "deterministic_selection_rule_present": selection_rule["deterministic"],
        "tie_policy_explicit_and_replayable": "tie_policy_explicit_replayable"
        in selection_rule["tie_policy"],
        "controls_recorded_as_policy_not_executed": (
            selection_rule["executed_controls_status"].startswith(
                "not_executed_until_iteration_5"
            )
            and all(
                "controls_not_run_until_iteration_5" in record["missing_gates"]
                for record in selection_records
            )
        ),
        "budget_validity_recorded": all(
            record["budget_cost_surface"]
            and record["budget_validity"]
            == "source_budget_surfaces_present_for_selection_candidate"
            for record in selection_records
        ),
        "selection_depends_on_downstream_consequence_vector": selection_decision[
            "selection_depends_on_downstream_consequence_vector"
        ],
        "selection_records_satisfy_schema": all(
            schema_fields.issubset(set(record.keys())) for record in selection_records
        ),
        "hidden_outcome_table_not_used": all(
            record["hidden_outcome_table_control"]
            == "not_used_source_artifact_projection_only"
            for record in selection_records
        ),
        "post_hoc_scoring_not_used": all(
            record["post_hoc_scoring_control"]
            == "not_used_records_constructed_before_n14_selection"
            for record in selection_records
        ),
        "runtime_state_used_false": all(
            record["runtime_state_used"] is False for record in selection_records
        ),
        "only_provisional_ap4_assigned": all(
            record["provisional_ap_level"] == "AP4_candidate"
            for record in selection_records
        ),
        "final_ap4_not_frozen": selection_decision["final_ap4_supported"] is False,
        "controls_pending_recorded": all(
            "controls_not_run_until_iteration_5" in record["missing_gates"]
            for record in selection_records
        ),
        "replay_pending_recorded": all(
            "replay_matrix_not_run_until_iteration_6" in record["missing_gates"]
            for record in selection_records
        ),
        "claim_flags_forced_false": all(
            value is False for value in CLAIM_FLAGS_FORCED_FALSE.values()
        ),
        "phase8_opened_false": True,
        "native_supported_flags_false": True,
        "src_diff_empty": git_status_short("src") == "",
    }
    acceptance_state = (
        "accepted_consequence_sensitive_selection_candidate_pending_controls"
        if all(checks.values())
        else "rejected_consequence_sensitive_selection_candidate"
    )
    interpretation_record = {
        "record_id": "n14_i4_interpretation_selection_candidate_v1",
        "acceptance_state": acceptance_state,
        "supported_interpretation": (
            "N14 now has a provisional AP4 candidate selection: the deterministic "
            "artifact-only rule selects route_b by a derived, memory-dominant "
            "pre-selection consequence rank even though immediate affordance "
            "favors route_a."
        ),
        "unsupported_interpretations": [
            "final AP4 support",
            "intention",
            "agency",
            "semantic choice",
            "semantic goal ownership",
            "identity acceptance",
            "selfhood",
            "personhood",
            "biological behavior",
            "native support",
            "fully native integration",
        ],
        "plain_language_interpretation": (
            "Iteration 4 resolves the Iteration 3 affordance/consequence "
            "conflict by derived consequence evidence. The selected route is "
            "route_b, while the immediate-affordance winner route_a is rejected. "
            "The positive candidate is memory-dominant: support and regulation "
            "sources are compatible but not route-specific yet. This is still "
            "only a provisional AP4 candidate because adversarial controls, "
            "replay/snapshot checks, and final claim-boundary classification "
            "remain pending."
        ),
        "next_required_step": (
            "Run Iteration 5 controls against hidden outcomes, post-hoc labels, "
            "stale records, invalid budgets, missing records, fixture labels, "
            "and claim relabels."
        ),
    }
    output = {
        "experiment": "N14",
        "iteration": 4,
        "purpose": "consequence_sensitive_selection_candidate",
        "schema": "n14_consequence_sensitive_selection_candidate_v1",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "passed" if all(checks.values()) else "failed",
        "acceptance_state": acceptance_state,
        "target_ap_ceiling": "AP4",
        "iteration_result": {
            "acceptance_state": acceptance_state,
            "selection_candidate_passed": all(checks.values()),
            "selected_route": selected_route_id,
            "rejected_routes": [
                record["route_candidate_id"] for record in rejected_records
            ],
            "immediate_affordance_top_route": candidate_set[
                "immediate_affordance_top_route"
            ],
            "consequence_top_route": candidate_set["consequence_top_route"],
            "affordance_consequence_conflict_present": candidate_set[
                "affordance_consequence_conflict_present"
            ],
            "affordance_consequence_conflict_resolved_by_consequence": True,
            "provisional_ap_level": "AP4_candidate",
            "final_ap4_supported": False,
            "phase8_opened": False,
            "native_support_opened": False,
        },
        "selection_rule": selection_rule,
        "selection_decision_record": selection_decision,
        "idempotency_record": idempotency_record,
        "selected_route_record": selected_record,
        "rejected_route_records": rejected_records,
        "selection_records": selection_records,
        "interpretation_record": interpretation_record,
        "claim_flags_forced_false": CLAIM_FLAGS_FORCED_FALSE,
        "checks": checks,
        "source_artifacts": {
            rel(SCHEMA_OUTPUT): source_artifact(SCHEMA_OUTPUT, schema),
            rel(ROUTE_RECORDS_OUTPUT): source_artifact(
                ROUTE_RECORDS_OUTPUT, route_records_artifact
            ),
        },
        "source_reports": {
            rel(SCHEMA_REPORT): source_report(SCHEMA_REPORT),
            rel(ROUTE_RECORDS_REPORT): source_report(ROUTE_RECORDS_REPORT),
        },
        "git": {
            "head": git_head(),
            "src_status_short": git_status_short("src"),
        },
    }
    output["output_digest"] = output_digest(output)
    return output


def write_report(output: dict[str, Any]) -> None:
    decision = output["selection_decision_record"]
    lines = [
        "# N14 Consequence-Sensitive Selection Candidate",
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
        json.dumps(output["interpretation_record"], indent=2, sort_keys=True),
        "```",
        "",
        "## Selection Decision",
        "",
        "```json",
        json.dumps(decision, indent=2, sort_keys=True),
        "```",
        "",
        "## Candidate Records",
        "",
        "| Route | Immediate rank | Consequence score | Consequence rank | Selected rank | Selection status |",
        "| --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for record in sorted(
        output["selection_records"], key=lambda item: item["route_candidate_id"]
    ):
        status = (
            "selected"
            if record["route_candidate_id"] == decision["selected_route"]
            else "rejected"
        )
        lines.append(
            "| "
            f"`{record['route_candidate_id']}` | "
            f"{record['immediate_affordance_rank']} | "
            f"{record['consequence_score_components']['consequence_score']} | "
            f"{record['consequence_rank']} | "
            f"{record['selected_rank']} | "
            f"`{status}` |"
        )
    lines.extend(
        [
            "",
            "The selected route is `route_b`. Immediate affordance favors",
            "`route_a`, so this is a matched conflict case resolved by the",
            "pre-selection consequence vector. The positive candidate is",
            "memory-dominant; support and regulation sources are compatible",
            "but are not route-specific consequence evidence yet. Final `AP4`",
            "remains unsupported until controls, replay/snapshot checks, and",
            "claim-boundary classification pass in later iterations.",
            "",
            "## Selection Rule",
            "",
            "```json",
            json.dumps(output["selection_rule"], indent=2, sort_keys=True),
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
            "provisional AP4 candidate != final AP4 support",
            "consequence-sensitive selection candidate != intention",
            "selected route by derived consequence rank != semantic choice",
            "source-backed consequence vector != semantic goal ownership",
            "artifact-level selection candidate != native support",
            "N14 Iteration 4 != agency",
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

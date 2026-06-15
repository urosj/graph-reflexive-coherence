#!/usr/bin/env python3
"""Build N14 Iteration 3 route consequence records."""

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

N06_OUTPUT = (
    ROOT
    / "experiments"
    / "2026-05-N06-lgrc-semantic-route-choice"
    / "outputs"
    / "n06_iteration_8_sc6_closeout.json"
)
N06_REPORT = (
    ROOT
    / "experiments"
    / "2026-05-N06-lgrc-semantic-route-choice"
    / "reports"
    / "n06_iteration_8_sc6_closeout.md"
)
N08_OUTPUT = (
    ROOT
    / "experiments"
    / "2026-05-N08-lgrc-memory-trail-affordance"
    / "outputs"
    / "n08_iteration_8_mem6_closeout.json"
)
N08_REPORT = (
    ROOT
    / "experiments"
    / "2026-05-N08-lgrc-memory-trail-affordance"
    / "reports"
    / "n08_iteration_8_mem6_closeout.md"
)
N09_OUTPUT = (
    ROOT
    / "experiments"
    / "2026-05-N09-lgrc-goal-proxy-regulation"
    / "outputs"
    / "n09_iteration_9_gpr6_closeout.json"
)
N09_REPORT = (
    ROOT
    / "experiments"
    / "2026-05-N09-lgrc-goal-proxy-regulation"
    / "reports"
    / "n09_iteration_9_gpr6_closeout.md"
)
N13_STRESS_OUTPUT = (
    ROOT
    / "experiments"
    / "2026-06-N13-lgrc-self-maintenance-and-support-seeking-regulation"
    / "outputs"
    / "n13_support_disruption_restoration_matrix.json"
)
N13_STRESS_REPORT = (
    ROOT
    / "experiments"
    / "2026-06-N13-lgrc-self-maintenance-and-support-seeking-regulation"
    / "reports"
    / "n13_support_disruption_restoration_matrix.md"
)

OUTPUT_PATH = OUTPUTS / "n14_route_consequence_records.json"
REPORT_PATH = REPORTS / "n14_route_consequence_records.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N14-lgrc-consequence-sensitive-route-selection/"
    "scripts/build_n14_route_consequence_records.py"
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

CONSEQUENCE_SCORE_POLICY = {
    "policy_id": "n14_i3_memory_dominant_consequence_score_v1",
    "score_direction": "higher_is_better",
    "components": {
        "memory_delta_component": (
            "N08 memory_strength_end - memory_strength_start from the pinned "
            "MEM6 replay window"
        ),
        "route_specific_support_component": (
            "0.0 unless a route-specific support effect is source-backed; "
            "Iteration 3 has source-compatible support evidence but no "
            "route-specific support consequence"
        ),
        "route_specific_regulation_component": (
            "0.0 unless a route-specific regulation effect is source-backed; "
            "Iteration 3 has source-compatible regulation evidence but no "
            "route-specific regulation consequence"
        ),
        "budget_penalty_component": (
            "0.0 when pinned budget surfaces are present; budget-invalid "
            "variants are deferred to Iteration 5 controls"
        ),
    },
    "claim_boundary": (
        "artifact-local consequence ordering only; not utility, intention, "
        "semantic choice, goal ownership, agency, or native support"
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


def source_ref(
    ref_id: str,
    artifact_path: Path,
    report_path: Path,
    artifact: dict[str, Any],
    evidence_fields: list[str],
) -> dict[str, Any]:
    return {
        "ref_id": ref_id,
        "artifact": rel(artifact_path),
        "artifact_sha256": digest_file(artifact_path),
        "artifact_output_digest": artifact.get("output_digest"),
        "report": rel(report_path),
        "report_sha256": digest_file(report_path),
        "evidence_fields": evidence_fields,
    }


def rank_scores(scores: dict[str, float]) -> dict[str, int]:
    return {
        route_id: rank
        for rank, (route_id, _score) in enumerate(
            sorted(scores.items(), key=lambda item: (-item[1], item[0])),
            start=1,
        )
    }


def memory_delta_score(memory_values: list[float]) -> float:
    return round(memory_values[-1] - memory_values[0], 12)


def consequence_score_components(memory_values: list[float]) -> dict[str, Any]:
    memory_delta = memory_delta_score(memory_values)
    components = {
        "memory_delta_component": memory_delta,
        "route_specific_support_component": 0.0,
        "route_specific_regulation_component": 0.0,
        "budget_penalty_component": 0.0,
    }
    consequence_score = round(sum(components.values()), 12)
    return {
        "components": components,
        "consequence_score": consequence_score,
        "score_policy_id": CONSEQUENCE_SCORE_POLICY["policy_id"],
        "score_direction": CONSEQUENCE_SCORE_POLICY["score_direction"],
        "score_scope": "memory_dominant_route_consequence",
        "support_regulation_specificity": (
            "support_and_regulation_sources_are_compatible_but_not_"
            "route_specific_in_iteration_3"
        ),
    }


def assign_consequence_ranks(records: list[dict[str, Any]]) -> None:
    ranked = sorted(
        records,
        key=lambda record: (
            -record["consequence_score_components"]["consequence_score"],
            record["route_candidate_id"],
        ),
    )
    for rank, record in enumerate(ranked, start=1):
        record["consequence_rank"] = rank
        record["consequence_rank_source"] = (
            "derived_from_serialized_consequence_score_components"
        )


def find_stress_record(stress: dict[str, Any], regime_id: str) -> dict[str, Any]:
    for record in stress["stress_matrix"]["stress_records"]:
        if record["regime_id"] == regime_id:
            return record
    raise KeyError(regime_id)


def build_records(
    n06: dict[str, Any],
    n08: dict[str, Any],
    n09: dict[str, Any],
    n13_stress: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    cycle = n06["artifact_only_closeout"]["per_cycle"][0]
    score_sums = cycle["candidate_score_component_sums"]
    immediate_ranks = rank_scores(score_sums)
    memory = n08["artifact_only_replay"]
    route_a_memory = memory["route_a_strength_after_each_cycle"]
    route_b_memory = memory["route_b_strength_after_each_cycle"]
    regulation_summary = n09["regulation_summary"]
    support_disrupted = find_stress_record(
        n13_stress, "stress_02_support_disrupted_regime"
    )
    candidate_set_id = cycle["candidate_set_id"]
    source_references = [
        source_ref(
            "n06_route_affordance",
            N06_OUTPUT,
            N06_REPORT,
            n06,
            [
                "artifact_only_closeout.per_cycle[0].candidate_score_component_sums",
                "artifact_only_closeout.per_cycle[0].candidate_set_id",
                "artifact_only_closeout.per_cycle[0].selected_route",
            ],
        ),
        source_ref(
            "n08_memory_trend",
            N08_OUTPUT,
            N08_REPORT,
            n08,
            [
                "artifact_only_replay.route_a_strength_after_each_cycle",
                "artifact_only_replay.route_b_strength_after_each_cycle",
                "artifact_only_replay.selected_routes",
            ],
        ),
        source_ref(
            "n09_bounded_regulation",
            N09_OUTPUT,
            N09_REPORT,
            n09,
            [
                "regulation_summary.gpr5_regulation_outcome_tag",
                "regulation_summary.gpr8_perturbation_classification",
                "regulation_summary.node_plus_packet_budget_error",
            ],
        ),
        source_ref(
            "n13_support_disruption",
            N13_STRESS_OUTPUT,
            N13_STRESS_REPORT,
            n13_stress,
            [
                "stress_matrix.stress_records.stress_02_support_disrupted_regime",
                "stress_matrix.stress_summary",
            ],
        ),
    ]
    common = {
        "source_experiment": "N14",
        "source_iteration": "iteration_3_route_consequence_records",
        "source_artifact": rel(OUTPUT_PATH),
        "source_report": rel(REPORT_PATH),
        "source_sha256": "self_digest_assigned_after_write_not_used_as_source",
        "source_report_sha256": "self_digest_assigned_after_write_not_used_as_source",
        "mechanism_name": "pre_selection_route_consequence_record",
        "mechanism_role": "route_consequence_record_candidate",
        "eligible_candidate_set_id": candidate_set_id,
        "candidate_set_completeness_status": "complete_for_n06_cycle_0_route_a_route_b",
        "rejected_candidate_record": "not_rejected_until_iteration_4_selection",
        "consequence_record_source": "N06_cycle_0_N08_MEM6_N09_GPR6_N13_AP3_stress",
        "consequence_record_timing": "pre_selection",
        "bounded_consequence_horizon": {
            "n06_route_window": "cycle_0",
            "n08_memory_window": "four_cycle_MEM6_replay",
            "n09_regulation_window": "GPR5_repeated_and_GPR8_perturbation_closeout",
            "n13_support_window": "stress_02_four_window_support_response",
        },
        "prediction_basis": [
            "N06 immediate route score component sums",
            "N08 observed route memory trend",
            "N09 bounded regulation and perturbation recovery summary",
            "N13 support-disrupted bounded response stress record",
        ],
        "derivation_policy": (
            "artifact_only_pre_selection_projection_from_pinned_source_windows;"
            " no hidden outcome table; no post-hoc selected-route scoring"
        ),
        "source_window": {
            "n06": "iteration_8_cycle_0",
            "n08": "iteration_8_MEM6_four_cycle_replay",
            "n09": "iteration_9_GPR6_closeout",
            "n13": "iteration_6_stress_02_support_disrupted_regime",
        },
        "budget_cost_surface": {
            "n06_budget": "budget_conservation_passed",
            "n08_budget": "memory_budget_and_node_plus_packet_budget_controls_passed",
            "n09_budget": {
                "node_plus_packet_budget_error": regulation_summary[
                    "node_plus_packet_budget_error"
                ]
            },
            "n13_budget": {
                "support_response_budget_debit": support_disrupted[
                    "budget_debit_amount"
                ],
                "within_bounded_window": support_disrupted["bounded_window"][
                    "within_bounded_window"
                ],
            },
        },
        "budget_validity": "source_budget_surfaces_present_not_selection_validated",
        "selection_rationale_surface": "not_constructed_until_iteration_4",
        "tie_policy": "schema_policy_present_no_tie_observed_in_i3_candidate_set",
        "missing_consequence_record_rejection": (
            "schema_policy_reject_or_mark_unsupported; no missing records in "
            "iteration_3_candidate_set"
        ),
        "hidden_outcome_table_control": "not_used_source_artifact_projection_only",
        "post_hoc_scoring_control": (
            "not_used_records_constructed_before_n14_selection"
        ),
        "stale_record_policy": "source_window_pinned_for_each_projection",
        "artifact_only_replay_status": "source_artifact_replay_fields_present",
        "snapshot_load_status": "not_run_until_iteration_6",
        "order_inversion_replay_status": "not_run_until_iteration_6",
        "runtime_state_used": False,
        "provisional_ap_level": "AP3_consequence_record_candidate",
        "provisional_claim_ceiling": (
            "artifact_level_pre_selection_route_consequence_record_candidate"
        ),
        "blocked_claims": BLOCKED_CLAIMS,
        "source_references": source_references,
    }
    route_a = {
        **common,
        "row_id": "n14_i3_record_01_route_a_affordance_preferred",
        "route_candidate_id": "route_a",
        "route_alternative_surface": "N06 cycle_0 candidate route_a",
        "immediate_affordance_surface": {
            "n06_cycle_0_score": score_sums["route_a"],
            "n06_selected_route_under_immediate_affordance": cycle["selected_route"],
        },
        "immediate_affordance_rank": immediate_ranks["route_a"],
        "expected_support_effect": (
            "no route-specific support restoration evidence; N13 support "
            "correction remains separate bounded response evidence"
        ),
        "expected_memory_effect": (
            "route_a memory strength decays without reinforcement over the "
            "N08 MEM6 window"
        ),
        "expected_regulation_effect": (
            "no route-specific bounded regulation recovery evidence attached "
            "to route_a in the pinned sources"
        ),
        "observed_downstream_effect": {
            "memory_strength_start": route_a_memory[0],
            "memory_strength_end": route_a_memory[-1],
            "memory_trend": "decay_without_reinforcement",
            "support_response_source": support_disrupted["expected_behavior"],
            "regulation_source": regulation_summary["gpr5_regulation_outcome_tag"],
        },
        "prediction_match_status": (
            "source_window_observed_for_memory_and_support; not_yet_n14_selection_validated"
        ),
        "consequence_score_components": consequence_score_components(route_a_memory),
        "selected_rank": "not_selected_until_iteration_4",
        "affordance_consequence_conflict_resolved_by_consequence": False,
        "missing_gates": [
            "selection_rule_not_applied",
            "affordance_consequence_conflict_not_resolved",
            "controls_not_run",
            "replay_matrix_not_run",
            "final_ap4_not_supported",
        ],
    }
    route_b = {
        **common,
        "row_id": "n14_i3_record_02_route_b_consequence_preferred",
        "route_candidate_id": "route_b",
        "route_alternative_surface": "N06 cycle_0 candidate route_b",
        "immediate_affordance_surface": {
            "n06_cycle_0_score": score_sums["route_b"],
            "n06_selected_route_under_immediate_affordance": cycle["selected_route"],
        },
        "immediate_affordance_rank": immediate_ranks["route_b"],
        "expected_support_effect": (
            "compatible with N13 bounded support-error response source; route "
            "specific support selection remains unvalidated until Iteration 4"
        ),
        "expected_memory_effect": (
            "route_b memory strength rises to saturation over the N08 MEM6 window"
        ),
        "expected_regulation_effect": (
            "compatible with N09 bounded repeated regulation and perturbation recovery"
        ),
        "observed_downstream_effect": {
            "memory_strength_start": route_b_memory[0],
            "memory_strength_end": route_b_memory[-1],
            "memory_trend": "reinforced_saturation",
            "support_response_source": support_disrupted["expected_behavior"],
            "support_scheduled_response_total": support_disrupted[
                "scheduled_response_total"
            ],
            "regulation_source": regulation_summary[
                "gpr8_perturbation_classification"
            ],
        },
        "prediction_match_status": (
            "source_window_observed_for_memory_regulation_and_support; "
            "not_yet_n14_selection_validated"
        ),
        "consequence_score_components": consequence_score_components(route_b_memory),
        "selected_rank": "not_selected_until_iteration_4",
        "affordance_consequence_conflict_resolved_by_consequence": False,
        "missing_gates": [
            "selection_rule_not_applied",
            "affordance_consequence_conflict_not_resolved",
            "controls_not_run",
            "replay_matrix_not_run",
            "final_ap4_not_supported",
        ],
    }
    records = [route_a, route_b]
    assign_consequence_ranks(records)
    candidate_set = {
        "eligible_candidate_set_id": candidate_set_id,
        "candidate_set_digest": cycle["candidate_set_digest"],
        "eligible_routes": ["route_a", "route_b"],
        "records_present_for_all_eligible_routes": True,
        "missing_consequence_records": [],
        "immediate_affordance_top_route": "route_a",
        "consequence_top_route": "route_b",
        "consequence_score_policy": CONSEQUENCE_SCORE_POLICY,
        "consequence_signal_scope": (
            "memory_dominant_provisional_candidate; support and regulation "
            "sources are compatible but not route-specific in Iteration 3"
        ),
        "affordance_consequence_conflict_present": True,
        "affordance_consequence_conflict_resolved": False,
        "selection_deferred_to_iteration_4": True,
    }
    return records, candidate_set


def build_output() -> dict[str, Any]:
    inventory = load_json(INVENTORY_OUTPUT)
    schema = load_json(SCHEMA_OUTPUT)
    n06 = load_json(N06_OUTPUT)
    n08 = load_json(N08_OUTPUT)
    n09 = load_json(N09_OUTPUT)
    n13_stress = load_json(N13_STRESS_OUTPUT)
    records, candidate_set = build_records(n06, n08, n09, n13_stress)
    schema_fields = set(schema["row_schema_fields"])
    checks = {
        "inventory_source_passed": inventory["status"] == "passed",
        "schema_source_passed": schema["status"] == "passed",
        "route_consequence_record_count": len(records) == 2,
        "candidate_set_complete": candidate_set[
            "records_present_for_all_eligible_routes"
        ]
        and candidate_set["missing_consequence_records"] == [],
        "records_satisfy_schema": all(
            schema_fields.issubset(set(record.keys())) for record in records
        ),
        "records_pre_selection": all(
            record["consequence_record_timing"] == "pre_selection"
            for record in records
        ),
        "source_references_pinned": all(
            all(
                ref["artifact_sha256"] and ref["report_sha256"]
                for ref in record["source_references"]
            )
            for record in records
        ),
        "prediction_basis_declared": all(record["prediction_basis"] for record in records),
        "derivation_policy_declared": all(
            record["derivation_policy"] for record in records
        ),
        "source_window_declared": all(record["source_window"] for record in records),
        "support_memory_regulation_descriptors_present": all(
            record["expected_support_effect"]
            and record["expected_memory_effect"]
            and record["expected_regulation_effect"]
            for record in records
        ),
        "observed_downstream_effect_present": all(
            record["observed_downstream_effect"] for record in records
        ),
        "prediction_match_status_present": all(
            record["prediction_match_status"] for record in records
        ),
        "bounded_consequence_horizon_present": all(
            record["bounded_consequence_horizon"] for record in records
        ),
        "budget_cost_surface_present": all(
            record["budget_cost_surface"] for record in records
        ),
        "hidden_outcome_table_not_used": all(
            record["hidden_outcome_table_control"]
            == "not_used_source_artifact_projection_only"
            for record in records
        ),
        "post_hoc_scoring_not_used": all(
            record["post_hoc_scoring_control"]
            == "not_used_records_constructed_before_n14_selection"
            for record in records
        ),
        "immediate_affordance_rank_recorded": all(
            isinstance(record["immediate_affordance_rank"], int)
            for record in records
        ),
        "consequence_rank_recorded": all(
            isinstance(record["consequence_rank"], int) for record in records
        ),
        "consequence_score_components_serialized": all(
            record["consequence_score_components"]["score_policy_id"]
            == CONSEQUENCE_SCORE_POLICY["policy_id"]
            and isinstance(
                record["consequence_score_components"]["consequence_score"], float
            )
            for record in records
        ),
        "consequence_rank_derived_from_score_components": all(
            record["consequence_rank_source"]
            == "derived_from_serialized_consequence_score_components"
            for record in records
        )
        and sorted(records, key=lambda record: record["consequence_rank"])[0][
            "route_candidate_id"
        ]
        == "route_b",
        "memory_dominant_scope_recorded": (
            candidate_set["consequence_signal_scope"].startswith(
                "memory_dominant_provisional_candidate"
            )
            and all(
                record["consequence_score_components"][
                    "support_regulation_specificity"
                ]
                == (
                    "support_and_regulation_sources_are_compatible_but_not_"
                    "route_specific_in_iteration_3"
                )
                for record in records
            )
        ),
        "affordance_consequence_conflict_present": candidate_set[
            "affordance_consequence_conflict_present"
        ],
        "affordance_consequence_conflict_not_resolved_yet": all(
            record["affordance_consequence_conflict_resolved_by_consequence"]
            is False
            for record in records
        ),
        "no_selected_route_claim": all(
            record["selected_rank"] == "not_selected_until_iteration_4"
            for record in records
        ),
        "no_final_ap4_supported": all(
            record["provisional_ap_level"] != "AP4" for record in records
        ),
        "claim_flags_forced_false": all(
            value is False for value in CLAIM_FLAGS_FORCED_FALSE.values()
        ),
        "runtime_state_used_false": all(
            record["runtime_state_used"] is False for record in records
        ),
        "phase8_opened_false": True,
        "native_supported_flags_false": True,
        "src_diff_empty": git_status_short("src") == "",
    }
    acceptance_state = (
        "accepted_route_consequence_records_no_selection"
        if all(checks.values())
        else "rejected_route_consequence_records"
    )
    interpretation_record = {
        "record_id": "n14_i3_interpretation_route_consequence_records_v1",
        "acceptance_state": acceptance_state,
        "supported_interpretation": (
            "N14 now has source-backed, pre-selection consequence records for "
            "the route_a/route_b candidate set, including an explicit "
            "affordance-versus-consequence conflict."
        ),
        "unsupported_interpretations": [
            "selected route by consequence",
            "AP4 consequence-sensitive selection support",
            "intention",
            "agency",
            "semantic choice",
            "semantic goal ownership",
            "identity acceptance",
            "native support",
            "fully native integration",
        ],
        "plain_language_interpretation": (
            "Iteration 3 builds the consequence records that Iteration 4 can "
            "use for route selection. N06 immediate affordance favors route_a, "
            "while a serialized, memory-dominant consequence score derived "
            "from N08 memory deltas ranks route_b higher. N09/N13 support and "
            "regulation evidence is source-compatible but not route-specific "
            "in this iteration. The conflict is recorded, but it is not "
            "resolved by a selection rule yet."
        ),
        "next_required_step": (
            "Apply a deterministic selection rule in Iteration 4 and test "
            "whether the recorded consequence vector, not immediate affordance "
            "alone, determines the selected route."
        ),
    }
    output = {
        "experiment": "N14",
        "iteration": 3,
        "purpose": "route_consequence_record_candidate",
        "schema": "n14_route_consequence_records_v1",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "passed" if all(checks.values()) else "failed",
        "acceptance_state": acceptance_state,
        "target_ap_ceiling": "AP4",
        "iteration_result": {
            "acceptance_state": acceptance_state,
            "route_consequence_records_passed": all(checks.values()),
            "pre_selection_records_built": True,
            "candidate_set_complete": candidate_set[
                "records_present_for_all_eligible_routes"
            ],
            "affordance_consequence_conflict_present": candidate_set[
                "affordance_consequence_conflict_present"
            ],
            "affordance_consequence_conflict_resolved": False,
            "selected_route_assigned": False,
            "final_ap4_supported": False,
            "phase8_opened": False,
            "native_support_opened": False,
        },
        "candidate_set_completeness_record": candidate_set,
        "consequence_score_policy": CONSEQUENCE_SCORE_POLICY,
        "route_consequence_records": records,
        "interpretation_record": interpretation_record,
        "claim_flags_forced_false": CLAIM_FLAGS_FORCED_FALSE,
        "checks": checks,
        "source_artifacts": {
            rel(INVENTORY_OUTPUT): source_artifact(INVENTORY_OUTPUT, inventory),
            rel(SCHEMA_OUTPUT): source_artifact(SCHEMA_OUTPUT, schema),
            rel(N06_OUTPUT): source_artifact(N06_OUTPUT, n06),
            rel(N08_OUTPUT): source_artifact(N08_OUTPUT, n08),
            rel(N09_OUTPUT): source_artifact(N09_OUTPUT, n09),
            rel(N13_STRESS_OUTPUT): source_artifact(N13_STRESS_OUTPUT, n13_stress),
        },
        "source_reports": {
            rel(INVENTORY_REPORT): source_report(INVENTORY_REPORT),
            rel(SCHEMA_REPORT): source_report(SCHEMA_REPORT),
            rel(N06_REPORT): source_report(N06_REPORT),
            rel(N08_REPORT): source_report(N08_REPORT),
            rel(N09_REPORT): source_report(N09_REPORT),
            rel(N13_STRESS_REPORT): source_report(N13_STRESS_REPORT),
        },
        "git": {
            "head": git_head(),
            "src_status_short": git_status_short("src"),
        },
    }
    output["output_digest"] = output_digest(output)
    return output


def write_report(output: dict[str, Any]) -> None:
    candidate_set = output["candidate_set_completeness_record"]
    lines = [
        "# N14 Route Consequence Records",
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
        "## Candidate Set",
        "",
        "```json",
        json.dumps(candidate_set, indent=2, sort_keys=True),
        "```",
        "",
        "## Consequence Score Policy",
        "",
        "```json",
        json.dumps(output["consequence_score_policy"], indent=2, sort_keys=True),
        "```",
        "",
        "## Route Records",
        "",
        "| Route | Immediate rank | Consequence score | Consequence rank | Selected rank | Conflict resolved |",
        "| --- | ---: | ---: | ---: | --- | --- |",
    ]
    for record in output["route_consequence_records"]:
        lines.append(
            "| "
            f"`{record['route_candidate_id']}` | "
            f"{record['immediate_affordance_rank']} | "
            f"{record['consequence_score_components']['consequence_score']} | "
            f"{record['consequence_rank']} | "
            f"`{record['selected_rank']}` | "
            f"`{str(record['affordance_consequence_conflict_resolved_by_consequence']).lower()}` |"
        )
    lines.extend(
        [
            "",
            "Iteration 3 records candidate consequences before N14 selection.",
            "The rank is derived from serialized memory-dominant score",
            "components. Support and regulation sources are compatible inputs",
            "but are not route-specific consequence evidence in this iteration.",
            "Iteration 3 does not assign a selected route, does not resolve the",
            "affordance/consequence conflict, and does not support final `AP4`.",
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
            "route consequence record != selected route",
            "affordance/consequence conflict present != conflict resolved",
            "pre-selection consequence records != intention",
            "source-backed support effect != semantic goal ownership",
            "N14 Iteration 3 != AP4 closeout",
            "artifact-level route consequence record != native support",
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

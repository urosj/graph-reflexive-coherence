#!/usr/bin/env python3
"""Build N14 Iteration 1 consequence source inventory."""

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

ROADMAP = ROOT / "experiments" / "N12-N18-LGRC-AgencyPrerequisitesRoadmap.md"
HANDOFF = ROOT / "experiments" / "N12-N18-LGRC-AgencyPrerequisitesHandoff.md"

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
N08_GEOMETRY_OUTPUT = (
    ROOT
    / "experiments"
    / "2026-05-N08-lgrc-memory-trail-affordance"
    / "outputs"
    / "n08_iteration_13_native_geometry_trail_closeout.json"
)
N08_GEOMETRY_REPORT = (
    ROOT
    / "experiments"
    / "2026-05-N08-lgrc-memory-trail-affordance"
    / "reports"
    / "n08_iteration_13_native_geometry_trail_closeout.md"
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

OUTPUT_PATH = OUTPUTS / "n14_consequence_source_inventory.json"
REPORT_PATH = REPORTS / "n14_consequence_source_inventory.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N14-lgrc-consequence-sensitive-route-selection/"
    "scripts/build_n14_consequence_source_inventory.py"
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


def row(
    *,
    row_id: str,
    source_experiment: str,
    source_iteration: str,
    source_artifact: Path,
    source_report: Path,
    mechanism_name: str,
    mechanism_role: str,
    route_alternative_surface: str,
    immediate_affordance_surface: str,
    consequence_record_source: str,
    expected_support_effect: str,
    expected_memory_effect: str,
    expected_regulation_effect: str,
    budget_cost_surface: str,
    provisional_ap_level: str,
    provisional_claim_ceiling: str,
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
        "route_candidate_id": "not_assigned_until_iteration_3",
        "route_alternative_surface": route_alternative_surface,
        "eligible_candidate_set_id": "not_assigned_until_iteration_3",
        "candidate_set_completeness_status": "not_validated_until_iteration_3",
        "rejected_candidate_record": "not_constructed_until_iteration_4",
        "immediate_affordance_surface": immediate_affordance_surface,
        "immediate_affordance_rank": "not_ranked_until_iteration_4",
        "consequence_record_source": consequence_record_source,
        "consequence_record_timing": "source_inventory_only_not_selection_input",
        "bounded_consequence_horizon": "not_frozen_until_iteration_2_schema",
        "prediction_basis": "source_artifact_inventory",
        "derivation_policy": "not_frozen_until_iteration_2_schema",
        "source_window": source_iteration,
        "expected_support_effect": expected_support_effect,
        "expected_memory_effect": expected_memory_effect,
        "expected_regulation_effect": expected_regulation_effect,
        "observed_downstream_effect": "not_evaluated_until_iteration_3_or_later",
        "prediction_match_status": "not_evaluated_until_iteration_3_or_later",
        "consequence_rank": "not_ranked_until_iteration_4",
        "selected_rank": "not_ranked_until_iteration_4",
        "affordance_consequence_conflict_resolved_by_consequence": False,
        "budget_cost_surface": budget_cost_surface,
        "budget_validity": "not_validated_until_iteration_3_or_later",
        "selection_rationale_surface": "not_constructed_until_iteration_4",
        "tie_policy": "not_frozen_until_iteration_2_schema",
        "missing_consequence_record_rejection": "not_frozen_until_iteration_2_schema",
        "hidden_outcome_table_control": "required_before_ap4",
        "post_hoc_scoring_control": "required_before_ap4",
        "stale_record_policy": "not_frozen_until_iteration_2_schema",
        "artifact_only_replay_status": "not_run_for_n14_yet",
        "snapshot_load_status": "not_run_for_n14_yet",
        "order_inversion_replay_status": "not_run_for_n14_yet",
        "runtime_state_used": False,
        "provisional_ap_level": provisional_ap_level,
        "provisional_claim_ceiling": provisional_claim_ceiling,
        "blocked_claims": BLOCKED_CLAIMS,
        "missing_gates": missing_gates,
    }


def build_rows() -> list[dict[str, Any]]:
    return [
        row(
            row_id="n14_i1_row_01_n06_route_arbitration_baseline",
            source_experiment="N06",
            source_iteration="iteration_8_sc6_closeout",
            source_artifact=N06_OUTPUT,
            source_report=N06_REPORT,
            mechanism_name="selection_only_route_arbitration",
            mechanism_role="route_alternative_and_immediate_affordance_source",
            route_alternative_surface=(
                "candidate route sets and selected/rejected route digests"
            ),
            immediate_affordance_surface=(
                "context-conditioned route score components from N06"
            ),
            consequence_record_source="not_present_in_n06_selection_only_scope",
            expected_support_effect="not_present",
            expected_memory_effect="not_present",
            expected_regulation_effect="not_present",
            budget_cost_surface="N06 budget conservation closeout surface",
            provisional_ap_level="AP1",
            provisional_claim_ceiling="artifact_only_semantic_route_choice_candidate",
            missing_gates=[
                "pre_selection_consequence_records_missing",
                "affordance_consequence_conflict_case_missing",
                "support_memory_regulation_projection_missing",
            ],
        ),
        row(
            row_id="n14_i1_row_02_n08_serialized_memory_affordance",
            source_experiment="N08",
            source_iteration="iteration_8_mem6_closeout",
            source_artifact=N08_OUTPUT,
            source_report=N08_REPORT,
            mechanism_name="serialized_route_memory_trail_affordance",
            mechanism_role="memory_effect_source",
            route_alternative_surface="memory-shaped route arbitration records",
            immediate_affordance_surface="route memory strength score components",
            consequence_record_source="serialized producer-policy memory trail",
            expected_support_effect="not_present",
            expected_memory_effect=(
                "route strengths change through decay/reinforcement across cycles"
            ),
            expected_regulation_effect="not_present",
            budget_cost_surface=(
                "memory budget and node-plus-packet budget controls from N08"
            ),
            provisional_ap_level="AP2",
            provisional_claim_ceiling=(
                "artifact_only_route_memory_or_trail_affordance_candidate"
            ),
            missing_gates=[
                "native_memory_support_not_opened",
                "pre_selection_n14_projection_not_built",
                "consequence_rank_not_assigned",
            ],
        ),
        row(
            row_id="n14_i1_row_03_n08_geometry_memory_boundary",
            source_experiment="N08",
            source_iteration="iteration_13_native_geometry_trail_closeout",
            source_artifact=N08_GEOMETRY_OUTPUT,
            source_report=N08_GEOMETRY_REPORT,
            mechanism_name="geometry_mediated_route_memory_boundary",
            mechanism_role="memory_geometry_boundary_source",
            route_alternative_surface="geometry-mediated route trail records",
            immediate_affordance_surface="route conductance/geometry evidence",
            consequence_record_source="native-geometry evidence source only",
            expected_support_effect="not_present",
            expected_memory_effect=(
                "geometry-mediated trail evidence may inform memory projection"
            ),
            expected_regulation_effect="not_present",
            budget_cost_surface="geometry/conductance accounting boundary",
            provisional_ap_level="AP2",
            provisional_claim_ceiling=(
                "memory_geometry_source_for_later_projection_only"
            ),
            missing_gates=[
                "phase8_native_route_conductance_memory_not_opened",
                "n14_consequence_projection_not_built",
                "native_support_not_opened",
            ],
        ),
        row(
            row_id="n14_i1_row_04_n09_bounded_regulation",
            source_experiment="N09",
            source_iteration="iteration_9_gpr6_closeout",
            source_artifact=N09_OUTPUT,
            source_report=N09_REPORT,
            mechanism_name="bounded_goal_proxy_regulation",
            mechanism_role="regulation_effect_source",
            route_alternative_surface="route/producer evidence for regulation",
            immediate_affordance_surface="proxy-conditioned eligibility surface",
            consequence_record_source="bounded regulation response chain",
            expected_support_effect="support boundary recorded but not target-owned",
            expected_memory_effect="memory surface handoff digest recorded",
            expected_regulation_effect=(
                "bounded repeated regulation and perturbation recovery"
            ),
            budget_cost_surface="scheduled/processed packet and budget controls",
            provisional_ap_level="AP2",
            provisional_claim_ceiling="artifact_only_goal_proxy_regulation_candidate",
            missing_gates=[
                "source_current_support_target_not_n09_native",
                "n14_consequence_rank_not_assigned",
                "semantic_goal_ownership_blocked",
            ],
        ),
        row(
            row_id="n14_i1_row_05_n12_phase8_readiness",
            source_experiment="N12",
            source_iteration="iteration_7_phase8_readiness_matrix",
            source_artifact=N12_READINESS_OUTPUT,
            source_report=N12_READINESS_REPORT,
            mechanism_name="phase8_ready_route_memory_and_response_magnitude_contracts",
            mechanism_role="phase8_readiness_input_only",
            route_alternative_surface="route conductance memory contract source",
            immediate_affordance_surface="native policy readiness record only",
            consequence_record_source="readiness contract not runtime support",
            expected_support_effect="not_present",
            expected_memory_effect="route conductance memory policy candidate",
            expected_regulation_effect="response magnitude policy candidate",
            budget_cost_surface="N12 contract budget and telemetry requirements",
            provisional_ap_level="AP0",
            provisional_claim_ceiling="phase8_ready_contracts_not_native_support",
            missing_gates=[
                "phase8_implementation_not_opened",
                "native_supported_flags_false",
                "n14_route_consequence_records_not_built",
            ],
        ),
        row(
            row_id="n14_i1_row_06_n13_support_stress_matrix",
            source_experiment="N13",
            source_iteration="iteration_6_support_disruption_restoration_matrix",
            source_artifact=N13_STRESS_OUTPUT,
            source_report=N13_STRESS_REPORT,
            mechanism_name="support_disruption_restoration_stress",
            mechanism_role="support_effect_and_control_source",
            route_alternative_surface="not_route_selection_source",
            immediate_affordance_surface="not_route_affordance_source",
            consequence_record_source="support stress regimes and response gating",
            expected_support_effect=(
                "support target presence and support error gate response"
            ),
            expected_memory_effect="not_present",
            expected_regulation_effect="support-seeking response survives controls",
            budget_cost_surface="N13 bounded response and budget controls",
            provisional_ap_level="AP3",
            provisional_claim_ceiling=(
                "artifact_level_ap3_self_maintenance_candidate_support_seeking_regulation"
            ),
            missing_gates=[
                "route_selection_not_present",
                "consequence_sensitive_ranking_not_present",
                "intention_and_agency_blocked",
            ],
        ),
        row(
            row_id="n14_i1_row_07_n13_closeout_and_handoff",
            source_experiment="N13",
            source_iteration="iteration_8_closeout_and_handoff",
            source_artifact=N13_CLOSEOUT_OUTPUT,
            source_report=N13_CLOSEOUT_REPORT,
            mechanism_name="n13_ap3_support_seeking_regulation_closeout",
            mechanism_role="ap3_support_regulation_and_n14_handoff_source",
            route_alternative_surface="N14 handoff allowed inputs only",
            immediate_affordance_surface="not_route_affordance_source",
            consequence_record_source="N14 handoff consequence question",
            expected_support_effect="artifact-level AP3 support-seeking evidence",
            expected_memory_effect="allowed input through N08/N12 records",
            expected_regulation_effect="support-error bounded response candidate",
            budget_cost_surface="N13 final controls and stress summary",
            provisional_ap_level="AP3",
            provisional_claim_ceiling=(
                "artifact_level_ap3_self_maintenance_candidate_support_seeking_regulation"
            ),
            missing_gates=[
                "n14_source_inventory_only",
                "ap4_selection_candidate_not_built",
                "native_support_not_opened",
            ],
        ),
    ]


def build_output() -> dict[str, Any]:
    n06 = load_json(N06_OUTPUT)
    n08 = load_json(N08_OUTPUT)
    n08_geometry = load_json(N08_GEOMETRY_OUTPUT)
    n09 = load_json(N09_OUTPUT)
    n12_readiness = load_json(N12_READINESS_OUTPUT)
    n13_stress = load_json(N13_STRESS_OUTPUT)
    n13_closeout = load_json(N13_CLOSEOUT_OUTPUT)
    rows = build_rows()
    required_roles = {
        "route_alternative_and_immediate_affordance_source",
        "memory_effect_source",
        "memory_geometry_boundary_source",
        "regulation_effect_source",
        "phase8_readiness_input_only",
        "support_effect_and_control_source",
        "ap3_support_regulation_and_n14_handoff_source",
    }
    observed_roles = {row["mechanism_role"] for row in rows}
    checks = {
        "required_source_paths_exist": all(
            path.exists()
            for path in [
                N06_OUTPUT,
                N06_REPORT,
                N08_OUTPUT,
                N08_REPORT,
                N08_GEOMETRY_OUTPUT,
                N08_GEOMETRY_REPORT,
                N09_OUTPUT,
                N09_REPORT,
                N12_READINESS_OUTPUT,
                N12_READINESS_REPORT,
                N13_STRESS_OUTPUT,
                N13_STRESS_REPORT,
                N13_CLOSEOUT_OUTPUT,
                N13_CLOSEOUT_REPORT,
            ]
        ),
        "source_statuses_passed_or_document_sources": all(
            status in {"passed", None}
            for status in [
                n06.get("status"),
                n08.get("status"),
                n08_geometry.get("status"),
                n09.get("status"),
                n12_readiness.get("status"),
                n13_stress.get("status"),
                n13_closeout.get("status"),
            ]
        ),
        "every_row_has_source_sha256": all(row["source_sha256"] for row in rows),
        "every_row_has_source_report_sha256": all(
            row["source_report_sha256"] for row in rows
        ),
        "required_roles_present": required_roles.issubset(observed_roles),
        "no_final_ap4_assigned": all(
            row["provisional_ap_level"] != "AP4" for row in rows
        ),
        "route_source_present": any(
            row["mechanism_role"] == "route_alternative_and_immediate_affordance_source"
            for row in rows
        ),
        "memory_source_present": any(
            row["mechanism_role"] in {
                "memory_effect_source",
                "memory_geometry_boundary_source",
            }
            for row in rows
        ),
        "regulation_source_present": any(
            row["mechanism_role"] == "regulation_effect_source" for row in rows
        ),
        "support_source_present": any(
            row["mechanism_role"] == "support_effect_and_control_source"
            for row in rows
        ),
        "n12_nat4_input_only": any(
            row["mechanism_role"] == "phase8_readiness_input_only" for row in rows
        )
        and n12_readiness["checks"]["phase8_opened_false"] is True,
        "n13_ap3_input_only": n13_closeout["closeout_result"][
            "final_supported_ap_level"
        ]
        == "AP3"
        and n13_closeout["closeout_result"]["native_support_opened"] is False,
        "claim_flags_forced_false": all(
            value is False for value in CLAIM_FLAGS_FORCED_FALSE.values()
        ),
        "native_support_not_opened": n13_closeout["closeout_result"][
            "native_support_opened"
        ]
        is False
        and n12_readiness["no_implementation_checks"][
            "native_supported_flags_false"
        ]
        is True,
        "phase8_opened_false": n13_closeout["closeout_result"]["phase8_opened"]
        is False
        and n12_readiness["no_implementation_checks"]["phase8_opened"] is False,
        "src_diff_empty": git_status_short("src") == "",
    }
    inventory_summary = {
        "row_count": len(rows),
        "route_source_rows": sum(
            row["mechanism_role"] == "route_alternative_and_immediate_affordance_source"
            for row in rows
        ),
        "memory_source_rows": sum(
            row["mechanism_role"]
            in {"memory_effect_source", "memory_geometry_boundary_source"}
            for row in rows
        ),
        "regulation_source_rows": sum(
            row["mechanism_role"] == "regulation_effect_source" for row in rows
        ),
        "support_source_rows": sum(
            row["mechanism_role"] == "support_effect_and_control_source"
            for row in rows
        ),
        "phase8_readiness_rows": sum(
            row["mechanism_role"] == "phase8_readiness_input_only" for row in rows
        ),
        "final_ap4_rows": 0,
    }
    acceptance_state = (
        "accepted_source_inventory_only_no_ap4"
        if all(checks.values())
        else "rejected_source_inventory"
    )
    iteration_interpretation = {
        "record_id": "n14_i1_interpretation_source_inventory_v1",
        "acceptance_state": acceptance_state,
        "supported_interpretation": (
            "N14 has sufficient pinned source coverage to proceed to schema "
            "and later route consequence record construction."
        ),
        "unsupported_interpretations": [
            "AP4 consequence-sensitive selection support",
            "intention",
            "agency",
            "semantic choice",
            "semantic goal ownership",
            "identity acceptance",
            "selfhood",
            "native support",
            "fully native integration",
        ],
        "plain_language_interpretation": (
            "Iteration 1 establishes the N14 evidence base. It identifies "
            "where route alternatives, memory effects, regulation effects, "
            "support effects, and Phase 8 readiness records will come from, "
            "but it does not yet build pre-selection consequence records or "
            "show route selection by consequences."
        ),
        "next_required_step": (
            "Freeze the N14 consequence-selection schema and AP4 gates before "
            "building candidate route consequence records."
        ),
    }
    output = {
        "experiment": "N14",
        "iteration": 1,
        "purpose": "baseline_and_consequence_source_inventory",
        "schema": "n14_consequence_source_inventory_v1",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "passed" if all(checks.values()) else "failed",
        "acceptance_state": acceptance_state,
        "target_ap_ceiling": "AP4",
        "iteration_result": {
            "acceptance_state": acceptance_state,
            "consequence_source_inventory_passed": all(checks.values()),
            "final_ap4_supported": False,
            "phase8_opened": False,
            "native_support_opened": False,
            "agency_claim_opened": False,
            "intention_claim_opened": False,
            "semantic_goal_ownership_opened": False,
        },
        "inventory_summary": inventory_summary,
        "iteration_interpretation": iteration_interpretation,
        "n14_inventory_rows": rows,
        "claim_flags_forced_false": CLAIM_FLAGS_FORCED_FALSE,
        "checks": checks,
        "source_artifacts": {
            rel(N06_OUTPUT): source_artifact(N06_OUTPUT, n06),
            rel(N08_OUTPUT): source_artifact(N08_OUTPUT, n08),
            rel(N08_GEOMETRY_OUTPUT): source_artifact(
                N08_GEOMETRY_OUTPUT, n08_geometry
            ),
            rel(N09_OUTPUT): source_artifact(N09_OUTPUT, n09),
            rel(N12_READINESS_OUTPUT): source_artifact(
                N12_READINESS_OUTPUT, n12_readiness
            ),
            rel(N13_STRESS_OUTPUT): source_artifact(N13_STRESS_OUTPUT, n13_stress),
            rel(N13_CLOSEOUT_OUTPUT): source_artifact(
                N13_CLOSEOUT_OUTPUT, n13_closeout
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
            rel(N06_REPORT): source_report(N06_REPORT),
            rel(N08_REPORT): source_report(N08_REPORT),
            rel(N08_GEOMETRY_REPORT): source_report(N08_GEOMETRY_REPORT),
            rel(N09_REPORT): source_report(N09_REPORT),
            rel(N12_READINESS_REPORT): source_report(N12_READINESS_REPORT),
            rel(N13_STRESS_REPORT): source_report(N13_STRESS_REPORT),
            rel(N13_CLOSEOUT_REPORT): source_report(N13_CLOSEOUT_REPORT),
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
        "# N14 Consequence Source Inventory",
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
        json.dumps(
            output["iteration_interpretation"],
            indent=2,
            sort_keys=True,
        ),
        "```",
        "",
        "Iteration 1 is a source inventory only. It pins consequence-relevant",
        "route, memory, regulation, support, Phase 8 readiness, and boundary",
        "sources for later N14 work. It does not assign final `AP4`, open Phase",
        "8, open native support, or license intention/agency claims.",
        "",
        "The global roadmap and handoff are listed as context documents in the",
        "JSON but are not SHA-pinned by this artifact, because they are updated",
        "after Iteration 1 and would otherwise create a self-referential digest.",
        "",
        "## Source Rows",
        "",
        "| Row | Source | Role | Provisional AP | Missing gates |",
        "| --- | --- | --- | --- | --- |",
    ]
    for source_row in output["n14_inventory_rows"]:
        lines.append(
            "| "
            f"`{source_row['row_id']}` | "
            f"`{source_row['source_experiment']}` | "
            f"`{source_row['mechanism_role']}` | "
            f"`{source_row['provisional_ap_level']}` | "
            f"{', '.join(f'`{gate}`' for gate in source_row['missing_gates'])} |"
        )
    lines.extend(
        [
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
            "source inventory != consequence-sensitive selection",
            "N06 route arbitration != N14 intention",
            "N08 memory affordance != identity acceptance",
            "N09 regulation != semantic goal ownership",
            "N12 NAT4 readiness != native support",
            "N13 AP3 support-seeking regulation != selfhood",
            "N14 Iteration 1 != AP4 closeout",
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

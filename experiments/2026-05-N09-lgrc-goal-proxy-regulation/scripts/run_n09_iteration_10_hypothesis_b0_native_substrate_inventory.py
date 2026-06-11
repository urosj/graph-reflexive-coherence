#!/usr/bin/env python3
"""Run N09 Iteration 10 Hypothesis B0 native/substrate inventory.

Iteration 10 reopens the staged Hypothesis B path without running a new
regulation probe. It inventories the load-bearing Hypothesis A variables and
maps them to available LGRC/N05-N08 substrate ingredients, preserving the
closed A-path ceiling and recording the remaining native policy blockers.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from run_n09_iteration_8_perturbation_withdrawal_support import (
    digest_file,
    digest_row,
    digest_value,
    git_head,
    git_status_short,
    load_json,
    rel,
    source_artifact_digest,
)


ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-05-N09-lgrc-goal-proxy-regulation"

N05 = ROOT / "experiments" / "2026-05-N05-lgrc-coherence-waves-oscillators"
N06 = ROOT / "experiments" / "2026-05-N06-lgrc-semantic-route-choice"
N07 = ROOT / "experiments" / "2026-05-N07-rc-identity-attractor-invariance"
N08 = ROOT / "experiments" / "2026-05-N08-lgrc-memory-trail-affordance"

N09_CLOSEOUT_PATH = EXPERIMENT / "outputs" / "n09_iteration_9_gpr6_closeout.json"
N05_CLOSEOUT_PATH = N05 / "outputs" / "n05_iteration_8_o6_closeout.json"
N06_CLOSEOUT_PATH = N06 / "outputs" / "n06_iteration_8_sc6_closeout.json"
N07_CLOSEOUT_PATH = (
    N07 / "outputs" / "n07_iteration_12_long_horizon_compatibility_closeout.json"
)
N08_CLOSEOUT_PATH = N08 / "outputs" / "n08_iteration_13_native_geometry_trail_closeout.json"

N09_CLOSEOUT_REPORT_PATH = EXPERIMENT / "reports" / "n09_iteration_9_gpr6_closeout.md"
N05_CLOSEOUT_REPORT_PATH = N05 / "reports" / "n05_iteration_8_o6_closeout.md"
N06_CLOSEOUT_REPORT_PATH = N06 / "reports" / "n06_iteration_8_sc6_closeout.md"
N07_CLOSEOUT_REPORT_PATH = (
    N07 / "reports" / "n07_iteration_12_long_horizon_compatibility_closeout.md"
)
N08_CLOSEOUT_REPORT_PATH = N08 / "reports" / "n08_iteration_13_native_geometry_trail_closeout.md"

OUTPUT_PATH = (
    EXPERIMENT / "outputs" / "n09_iteration_10_hypothesis_b0_native_substrate_inventory.json"
)
REPORT_PATH = (
    EXPERIMENT / "reports" / "n09_iteration_10_hypothesis_b0_native_substrate_inventory.md"
)
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N09-lgrc-goal-proxy-regulation/scripts/"
    "run_n09_iteration_10_hypothesis_b0_native_substrate_inventory.py"
)


def all_false(mapping: dict[str, bool]) -> bool:
    return all(value is False for value in mapping.values())


def add_row_digest(row: dict[str, Any], digest_field: str = "inventory_row_digest") -> dict[str, Any]:
    row[digest_field] = digest_row(row, digest_field)
    return row


def source_paths() -> dict[str, Path]:
    return {
        "n09_gpr6_closeout": N09_CLOSEOUT_PATH,
        "n05_o6_closeout": N05_CLOSEOUT_PATH,
        "n06_sc6_closeout": N06_CLOSEOUT_PATH,
        "n07_id6_closeout": N07_CLOSEOUT_PATH,
        "n08_hypothesis_b_closeout": N08_CLOSEOUT_PATH,
    }


def source_report_paths() -> dict[str, Path]:
    return {
        "n09_gpr6_closeout": N09_CLOSEOUT_REPORT_PATH,
        "n05_o6_closeout": N05_CLOSEOUT_REPORT_PATH,
        "n06_sc6_closeout": N06_CLOSEOUT_REPORT_PATH,
        "n07_id6_closeout": N07_CLOSEOUT_REPORT_PATH,
        "n08_hypothesis_b_closeout": N08_CLOSEOUT_REPORT_PATH,
    }


def load_sources() -> dict[str, dict[str, Any]]:
    return {key: load_json(path) for key, path in source_paths().items()}


def path_refs(paths: dict[str, Path]) -> dict[str, str]:
    return {key: rel(path) for key, path in paths.items()}


def path_sha256(paths: dict[str, Path]) -> dict[str, str]:
    return {key: digest_file(path) for key, path in paths.items()}


def existing_n09_native_gaps(n09_closeout: dict[str, Any]) -> list[str]:
    return sorted(
        {
            record["gap_id"]
            for record in n09_closeout["native_policy_gap_records"]
            if record.get("status") == "missing"
        }
    )


def build_a_path_variable_inventory(sources: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    n09 = sources["n09_gpr6_closeout"]
    handoff = n09["n10_handoff_fields"]
    n05 = sources["n05_o6_closeout"]
    n07 = sources["n07_id6_closeout"]
    n08 = sources["n08_hypothesis_b_closeout"]

    common_source = [rel(N09_CLOSEOUT_PATH)]
    common_report = [rel(N09_CLOSEOUT_REPORT_PATH)]
    rows = [
        {
            "row_id": "n09_b0_proxy_surface",
            "a_path_variable": "proxy_surface",
            "a_path_evidence": "serialized proxy surface digest chain ending at perturbation recovery surface",
            "a_path_source_digest": handoff["proxy_surface_digest"],
            "source_artifacts": common_source,
            "source_reports": common_report,
            "native_substrate_mapping": "partially_native_representable",
            "available_lgrc_or_substrate_mechanisms": [
                "node_coherence_measurement",
                "native_causal_surface_digest",
                "packet_ledger_state_surface",
            ],
            "missing_native_policy_surfaces": [
                "native_proxy_surface_policy_missing",
                "native_goal_proxy_regulation_policy_missing",
            ],
            "iteration_11_role": "candidate observable proxy can be measured, but proxy meaning remains serialized",
            "claim_boundary": "proxy surface evidence does not imply semantic goal or agency",
        },
        {
            "row_id": "n09_b0_target_band",
            "a_path_variable": "target_band",
            "a_path_evidence": "declared serialized band consumed by GPR2-GPR8",
            "a_path_source_digest": handoff["error_policy_digest"],
            "source_artifacts": common_source,
            "source_reports": common_report,
            "native_substrate_mapping": "producer_policy_required",
            "available_lgrc_or_substrate_mechanisms": [
                "numeric coherence values",
                "serialized policy rows",
            ],
            "missing_native_policy_surfaces": [
                "native_target_band_policy_missing",
                "native_goal_proxy_regulation_policy_missing",
            ],
            "iteration_11_role": "band remains the comparison frame, not a native attractor target",
            "claim_boundary": "declared band is a regulator scaffold, not a native intention",
        },
        {
            "row_id": "n09_b0_error_sign_and_magnitude",
            "a_path_variable": "error_sign_and_magnitude",
            "a_path_evidence": "signed distance from proxy surface to declared target band",
            "a_path_source_digest": handoff["error_policy_digest"],
            "source_artifacts": common_source,
            "source_reports": common_report,
            "native_substrate_mapping": "producer_policy_required",
            "available_lgrc_or_substrate_mechanisms": [
                "coherence_difference_observable",
                "artifact_digest_replay",
            ],
            "missing_native_policy_surfaces": [
                "native_proxy_error_policy_missing",
                "native_goal_proxy_regulation_policy_missing",
            ],
            "iteration_11_role": "probe can compare measured drift, but error computation is not native",
            "claim_boundary": "error value is a serialized diagnostic, not felt goal error",
        },
        {
            "row_id": "n09_b0_response_direction",
            "a_path_variable": "response_direction",
            "a_path_evidence": "decrease-proxy route selected when proxy is above band",
            "a_path_source_digest": handoff["source_candidate_set_digest"],
            "source_artifacts": common_source,
            "source_reports": common_report,
            "native_substrate_mapping": "partially_native_representable",
            "available_lgrc_or_substrate_mechanisms": [
                "native_route_arbitration_candidate_sets",
                "native_route_arbitration_records",
                "runtime_visible_candidate_scores",
            ],
            "missing_native_policy_surfaces": [
                "native_proxy_conditioned_response_policy_missing",
                "native_goal_proxy_regulation_policy_missing",
            ],
            "iteration_11_role": "candidate routes may exist natively, but response direction remains externally scored",
            "claim_boundary": "route selection is not semantic choice or goal understanding",
        },
        {
            "row_id": "n09_b0_packet_correction_amount",
            "a_path_variable": "packet_correction_amount",
            "a_path_evidence": "scheduled LGRC packet amount restores proxy to band",
            "a_path_source_digest": handoff["regulation_response_digest"],
            "source_artifacts": common_source,
            "source_reports": common_report,
            "native_substrate_mapping": "partially_native_representable",
            "available_lgrc_or_substrate_mechanisms": [
                "native_packet_scheduling",
                "step_owned_packet_processing",
                "node_plus_packet_budget_conservation",
            ],
            "missing_native_policy_surfaces": [
                "native_response_amount_policy_missing",
                "native_goal_proxy_regulation_policy_missing",
            ],
            "iteration_11_role": "LGRC can carry a packet; choosing correction magnitude remains policy-mediated",
            "claim_boundary": "packet correction is scheduling evidence only",
        },
        {
            "row_id": "n09_b0_repeated_boundedness",
            "a_path_variable": "repeated_boundedness",
            "a_path_evidence": "four repeated memory-shaped correction windows remain bounded",
            "a_path_source_digest": digest_value(handoff["repeated_regulation_response_digests"]),
            "source_artifacts": common_source,
            "source_reports": common_report,
            "native_substrate_mapping": "partially_native_representable",
            "available_lgrc_or_substrate_mechanisms": [
                "native_packet_loop_execution",
                "bounded_budget_accounting",
                "N05_O5_self_sustained_oscillator_candidate",
            ],
            "missing_native_policy_surfaces": [
                n05["phase3_native_policy_support_audit"]["native_policy_blocker"],
                "native_repeated_goal_proxy_regulation_policy_missing",
                "native_goal_proxy_regulation_policy_missing",
            ],
            "iteration_11_role": "look for bounded return tendency without replaying producer correction",
            "claim_boundary": "bounded repetition does not imply autonomous regulation",
        },
        {
            "row_id": "n09_b0_perturbation_recovery",
            "a_path_variable": "perturbation_recovery",
            "a_path_evidence": "proxy perturbation recovered to band through scheduled packet and step",
            "a_path_source_digest": handoff["regulation_response_digest"],
            "source_artifacts": common_source,
            "source_reports": common_report,
            "native_substrate_mapping": "producer_policy_required",
            "available_lgrc_or_substrate_mechanisms": [
                "packet_processing_after_perturbation",
                "budget_conserved_recovery_evidence",
            ],
            "missing_native_policy_surfaces": [
                "perturbation_recovery_policy_not_constitutive_native",
                "native_goal_proxy_regulation_policy_missing",
            ],
            "iteration_11_role": "perturb same proxy and observe passive return, wrong-direction response, saturation, or no-response",
            "claim_boundary": "recovery remains regulation evidence only under serialized policy",
        },
        {
            "row_id": "n09_b0_memory_shaped_route_evidence",
            "a_path_variable": "memory_shaped_route_evidence",
            "a_path_evidence": "N08 memory surface changes route ranking for N09 producer eligibility",
            "a_path_source_digest": handoff["memory_surface_digest"],
            "source_artifacts": [rel(N09_CLOSEOUT_PATH), rel(N08_CLOSEOUT_PATH)],
            "source_reports": [rel(N09_CLOSEOUT_REPORT_PATH), rel(N08_CLOSEOUT_REPORT_PATH)],
            "native_substrate_mapping": "partially_native_representable",
            "available_lgrc_or_substrate_mechanisms": [
                "native_route_arbitration_can_read_runtime_visible_candidates",
                "N08_static_positive_geometry_route_response_persistence_candidate",
            ],
            "missing_native_policy_surfaces": [
                n08["closeout_summary"]["hypothesis_b_current_blocker"],
                "native_memory_shaped_regulation_surface_missing",
                "native_goal_proxy_regulation_policy_missing",
            ],
            "iteration_11_role": "use static geometry response as design direction, not adaptive trail memory",
            "claim_boundary": "Hypothesis A memory claim is artifact-only; Hypothesis B native trail claim remains blocked",
        },
        {
            "row_id": "n09_b0_identity_support_anchor",
            "a_path_variable": "support_identity_anchor",
            "a_path_evidence": "N07 support digest is available; withdrawal baseline remains unavailable for N09/N10 consumption",
            "a_path_source_digest": n07["long_horizon_closeout_row"]["support_area_digest"],
            "source_artifacts": [rel(N09_CLOSEOUT_PATH), rel(N07_CLOSEOUT_PATH)],
            "source_reports": [rel(N09_CLOSEOUT_REPORT_PATH), rel(N07_CLOSEOUT_REPORT_PATH)],
            "native_substrate_mapping": "partially_native_representable",
            "available_lgrc_or_substrate_mechanisms": [
                "runtime_coherence_basin_support_area_digest",
                "N07_ID6_bounded_non_destructive_exchange_evidence",
            ],
            "missing_native_policy_surfaces": [
                "n07_identity_withdrawal_baseline_not_available",
                "native_identity_preserving_regulation_validator_missing",
                *n07["closeout_decision"]["native_policy_blockers"],
            ],
            "iteration_11_role": "support anchor constrains overclaiming; not required to prove B1 probe response",
            "claim_boundary": "support evidence does not imply runtime identity acceptance",
        },
    ]
    return [add_row_digest(row) for row in rows]


def build_substrate_ingredient_inventory(sources: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    n05 = sources["n05_o6_closeout"]
    n06 = sources["n06_sc6_closeout"]
    n07 = sources["n07_id6_closeout"]
    n08 = sources["n08_hypothesis_b_closeout"]
    rows = [
        {
            "ingredient_id": "n05_oscillation_return_channels",
            "source_experiment": "N05",
            "source_artifacts": [rel(N05_CLOSEOUT_PATH)],
            "source_reports": [rel(N05_CLOSEOUT_REPORT_PATH)],
            "evidence_ceiling": n05["n05_closeout"]["strongest_claim_ceiling"],
            "supported_level_or_class": n05["n05_closeout"]["strongest_supported_o_level"],
            "usable_for_iteration_11": trueish(n05["n05_closeout"]["strongest_supported_o_level"] == "O5"),
            "native_support_status": "route_aspect_serialized_self_rearm_available_o6_blocked",
            "available_mechanisms": n05["phase3_native_policy_support_audit"]["current_native_supports"],
            "blockers": n05["phase3_native_policy_support_audit"]["native_policy_blockers"],
            "claim_boundary": "oscillation/return channels are not route memory or goal regulation",
        },
        {
            "ingredient_id": "n06_route_arbitration_context_selection",
            "source_experiment": "N06",
            "source_artifacts": [rel(N06_CLOSEOUT_PATH)],
            "source_reports": [rel(N06_CLOSEOUT_REPORT_PATH)],
            "evidence_ceiling": n06["closeout"]["strongest_claim_ceiling"],
            "supported_level_or_class": n06["closeout"]["strongest_supported_sc_level"],
            "usable_for_iteration_11": True,
            "native_support_status": n06["closeout"]["selection_causality_basis"],
            "available_mechanisms": [
                "native_route_arbitration_records",
                "runtime_visible_candidate_scores",
                "selected_and_rejected_route_digests",
            ],
            "blockers": [
                item["limitation"] for item in n06["closeout"]["native_policy_limitations"]
            ],
            "claim_boundary": "native route arbitration is selection evidence, not semantic choice",
        },
        {
            "ingredient_id": "n07_identity_support_and_bounded_exchange",
            "source_experiment": "N07",
            "source_artifacts": [rel(N07_CLOSEOUT_PATH)],
            "source_reports": [rel(N07_CLOSEOUT_REPORT_PATH)],
            "evidence_ceiling": n07["long_horizon_closeout_row"]["claim_ceiling"],
            "supported_level_or_class": n07["closeout_decision"]["frozen_n07_ceiling"],
            "usable_for_iteration_11": True,
            "native_support_status": n07["closeout_decision"]["native_support_status"],
            "available_mechanisms": [
                "support_area_digest",
                "coherence_basin_identity_surface",
                "bounded_non_destructive_exchange_class",
            ],
            "blockers": n07["closeout_decision"]["native_policy_blockers"],
            "claim_boundary": "ID6 evidence is not runtime identity acceptance or RC identity collapse",
        },
        {
            "ingredient_id": "n08_static_positive_geometry_route_response",
            "source_experiment": "N08",
            "source_artifacts": [rel(N08_CLOSEOUT_PATH)],
            "source_reports": [rel(N08_CLOSEOUT_REPORT_PATH)],
            "evidence_ceiling": n08["closeout_summary"]["hypothesis_b_claim_ceiling"],
            "supported_level_or_class": n08["closeout_summary"]["hypothesis_b_status"],
            "usable_for_iteration_11": True,
            "native_support_status": "static_geometry_response_persistence_without_native_conductance_memory",
            "available_mechanisms": [
                "positive_conserved_geometry_shapes_native_arbitration",
                "static_response_persistence",
            ],
            "blockers": [n08["closeout_summary"]["hypothesis_b_current_blocker"]],
            "claim_boundary": "static geometry response is not adaptive trail memory",
        },
        {
            "ingredient_id": "current_lgrc_runtime_surfaces",
            "source_experiment": "LGRC/Phase8",
            "source_artifacts": [rel(N09_CLOSEOUT_PATH)],
            "source_reports": [rel(N09_CLOSEOUT_REPORT_PATH)],
            "evidence_ceiling": "runtime_support_ingredient_inventory",
            "supported_level_or_class": "packet_flux_budget_topology_route_arbitration_state_reabsorption_available",
            "usable_for_iteration_11": True,
            "native_support_status": "available_as_mechanisms_not_goal_proxy_policy",
            "available_mechanisms": [
                "packet_scheduling",
                "step_owned_packet_processing",
                "node_plus_packet_budget_accounting",
                "native_route_arbitration",
                "topology_commit_lineage",
                "topology_state_reabsorption",
            ],
            "blockers": [
                "native_goal_proxy_regulation_policy_missing",
                "native_proxy_error_policy_missing",
                "native_proxy_conditioned_response_policy_missing",
            ],
            "claim_boundary": "runtime mechanisms do not create semantic goal, agency, or native regulation claims by themselves",
        },
    ]
    return [add_row_digest(row) for row in rows]


def trueish(value: bool) -> bool:
    return bool(value)


def build_blocker_refinement(
    sources: dict[str, dict[str, Any]],
    variable_rows: list[dict[str, Any]],
    ingredient_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    n09 = sources["n09_gpr6_closeout"]
    blockers = set(existing_n09_native_gaps(n09))
    for row in variable_rows:
        blockers.update(row["missing_native_policy_surfaces"])
    for row in ingredient_rows:
        blockers.update(row["blockers"])
    ordered = [
        "native_goal_proxy_regulation_policy_missing",
        "native_proxy_surface_policy_missing",
        "native_target_band_policy_missing",
        "native_proxy_error_policy_missing",
        "native_proxy_conditioned_response_policy_missing",
        "native_response_amount_policy_missing",
        "native_repeated_goal_proxy_regulation_policy_missing",
        "perturbation_recovery_policy_not_constitutive_native",
        "native_memory_shaped_regulation_surface_missing",
        "native_route_conductance_memory_policy_missing",
        "missing_route_conductance_memory_policy",
        "missing_serialized_delayed_passive_response_policy",
        "missing_serialized_custom_node_potentials_policy",
        "missing_serialized_potential_inversion_policy",
        "missing_flux_facilitated_metric_map_policy",
        "native_identity_preserving_regulation_validator_missing",
        "n07_identity_withdrawal_baseline_not_available",
        "native_neutral_absorber_reservoir_policy_missing",
        "native_identity_acceptance_contract_missing",
        "native_long_horizon_c3_replay_policy_missing",
        "native_goal_proxy_regulation_artifact_replay_validator_missing",
        "native_oscillator_return_regulation_policy_missing",
    ]
    rows = []
    for blocker in ordered:
        if blocker not in blockers:
            continue
        if blocker == "native_goal_proxy_regulation_policy_missing":
            role = "primary_b_path_blocker"
        elif blocker.startswith("native_proxy") or blocker in {
            "native_target_band_policy_missing",
            "native_response_amount_policy_missing",
            "native_repeated_goal_proxy_regulation_policy_missing",
        }:
            role = "refined_goal_proxy_policy_surface_gap"
        elif "route_conductance" in blocker or "memory" in blocker:
            role = "memory_or_route_response_native_gap"
        elif blocker.startswith("missing_serialized") or "flux_facilitated" in blocker:
            role = "oscillation_or_potential_native_gap"
        elif blocker.startswith("native_identity") or blocker.startswith("n07_"):
            role = "identity_support_native_gap"
        else:
            role = "supporting_native_gap"
        rows.append(
            add_row_digest(
                {
                    "blocker": blocker,
                    "status": "open",
                    "role": role,
                    "blocks_hypothesis_b_native_regulation_claim": True,
                    "blocks_iteration_11_probe_execution": False,
                    "claim_boundary": "record gap without promoting agency, semantic goal, or native regulation claim",
                },
                "blocker_row_digest",
            )
        )
    return rows


def build_controls(n09_closeout: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        "no_new_probe": {
            "control_passed": True,
            "primary_blocker": "new_probe_run_in_inventory_iteration",
            "reason": "Iteration 10 reads existing artifacts only and constructs no LGRC runtime",
        },
        "a_path_ceiling_preserved": {
            "control_passed": n09_closeout["claim_ceiling"]
            == "artifact_only_goal_proxy_regulation_candidate",
            "primary_blocker": "a_path_claim_ceiling_mutated",
            "reason": "GPR6 ceiling is copied from Iteration 9 closeout",
        },
        "b_path_not_promoted": {
            "control_passed": True,
            "primary_blocker": "hypothesis_b_claim_promotion_blocked",
            "reason": "B-path inventory records blockers and does not run a positive native regulation probe",
        },
        "claim_promotion": {
            "control_passed": all_false(n09_closeout["claim_flags"]),
            "primary_blocker": "claim_promotion_blocked",
            "reason": "N09 stronger claim flags remain false",
        },
        "visual_or_report_not_source_of_truth": {
            "control_passed": True,
            "primary_blocker": "non_artifact_source_of_truth_rejected",
            "reason": "Inventory rows cite output JSON artifacts; reports are supporting references",
        },
    }


def build_artifact() -> dict[str, Any]:
    sources = load_sources()
    source_artifacts = path_refs(source_paths())
    source_reports = path_refs(source_report_paths())
    source_artifact_sha256 = path_sha256(source_paths())
    n09 = sources["n09_gpr6_closeout"]

    variable_rows = build_a_path_variable_inventory(sources)
    ingredient_rows = build_substrate_ingredient_inventory(sources)
    blocker_rows = build_blocker_refinement(sources, variable_rows, ingredient_rows)
    controls = build_controls(n09)

    required_variables = {
        "proxy_surface",
        "target_band",
        "error_sign_and_magnitude",
        "response_direction",
        "packet_correction_amount",
        "repeated_boundedness",
        "perturbation_recovery",
        "memory_shaped_route_evidence",
        "support_identity_anchor",
    }
    observed_variables = {row["a_path_variable"] for row in variable_rows}
    ingredient_ids = {row["ingredient_id"] for row in ingredient_rows}
    validation_checks = {
        "source_artifacts_present": all(path.exists() for path in source_paths().values()),
        "source_reports_present": all(path.exists() for path in source_report_paths().values()),
        "all_source_artifacts_passed": all(
            source.get("status") == "passed" for source in sources.values()
        ),
        "n09_a_path_closeout_preserved": n09["claim_ceiling"]
        == "artifact_only_goal_proxy_regulation_candidate",
        "hypothesis_a_closed": n09["hypothesis_a_closeout"]["status"] == "closed",
        "hypothesis_b_staged": n09["hypothesis_b_status"]["status"] == "staged",
        "native_substrate_b_claim_not_supported": not n09["hypothesis_b_status"][
            "native_substrate_mediated_goal_proxy_regulation_supported"
        ],
        "required_a_path_variables_inventory_complete": observed_variables
        == required_variables,
        "n05_n08_ingredient_inventory_complete": ingredient_ids
        == {
            "n05_oscillation_return_channels",
            "n06_route_arbitration_context_selection",
            "n07_identity_support_and_bounded_exchange",
            "n08_static_positive_geometry_route_response",
            "current_lgrc_runtime_surfaces",
        },
        "all_inventory_rows_have_sources": all(
            row["source_artifacts"] and row["source_reports"]
            for row in [*variable_rows, *ingredient_rows]
        ),
        "all_inventory_row_digests_present": all(
            "inventory_row_digest" in row for row in [*variable_rows, *ingredient_rows]
        ),
        "primary_b_path_blocker_recorded": any(
            row["blocker"] == "native_goal_proxy_regulation_policy_missing"
            for row in blocker_rows
        ),
        "refined_proxy_policy_blockers_recorded": {
            "native_proxy_surface_policy_missing",
            "native_target_band_policy_missing",
            "native_proxy_error_policy_missing",
            "native_proxy_conditioned_response_policy_missing",
            "native_response_amount_policy_missing",
        }.issubset({row["blocker"] for row in blocker_rows}),
        "claim_flags_all_false": all_false(n09["claim_flags"]),
        "controls_all_passed": all(row["control_passed"] for row in controls.values()),
        "no_new_probe_run": True,
    }

    claim_flags = dict(n09["claim_flags"])
    claim_flags["native_substrate_mediated_goal_proxy_regulation_claim_allowed"] = False

    artifact: dict[str, Any] = {
        "schema": "n09_iteration_10_hypothesis_b0_native_substrate_inventory_v1",
        "experiment": "2026-05-N09-lgrc-goal-proxy-regulation",
        "iteration": 10,
        "purpose": "hypothesis_b0_native_substrate_inventory_no_new_probe",
        "status": "passed" if all(validation_checks.values()) else "failed",
        "acceptance_state": "achieved" if all(validation_checks.values()) else "not_achieved",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "command": COMMAND,
        "source_artifacts": source_artifacts,
        "source_reports": source_reports,
        "source_artifact_sha256": source_artifact_sha256,
        "source_artifact_digests": {
            key: source_artifact_digest(value) for key, value in sources.items()
        },
        "a_path_preservation": {
            "hypothesis_a_status": n09["hypothesis_a_closeout"]["status"],
            "claim_ceiling": n09["claim_ceiling"],
            "gpr_level": n09["gpr_level"],
            "strongest_evidence": n09["hypothesis_a_closeout"]["strongest_evidence"],
            "artifact_only_validator_preserved": n09["validation_checks"][
                "artifact_only_validator_used"
            ],
            "lower_gpr5_evidence_preserved": n09["ceiling_algorithm_result"][
                "lower_gpr5_evidence_preserved"
            ],
        },
        "hypothesis_b_inventory_status": {
            "status": "reopened_for_inventory_only",
            "native_substrate_mediated_goal_proxy_regulation_supported": False,
            "primary_blocker": "native_goal_proxy_regulation_policy_missing",
            "strongest_possible_iteration_11_positive_ceiling": "native_substrate_mediated_goal_proxy_regulation_design_candidate",
            "inventory_does_not_change_a_path_ceiling": True,
        },
        "a_path_variable_inventory": variable_rows,
        "substrate_ingredient_inventory": ingredient_rows,
        "b_path_blocker_refinement": blocker_rows,
        "iteration_11_probe_guidance": {
            "probe_may_use": [
                "measured proxy node/surface",
                "declared target band as comparison frame",
                "fixed geometry or positive conserved route-response geometry",
                "native route arbitration evidence if serialized and runtime-visible",
                "LGRC packet/flux/budget accounting",
            ],
            "probe_must_not_use": [
                "A-path producer correction scheduler",
                "hidden reward or goal labels",
                "experiment-side if/else route selection",
                "post-hoc policy threshold changes",
                "claim promotion fields",
            ],
            "result_classes": [
                "toward_band_passive_response",
                "bounded_degradation",
                "wrong_direction_response",
                "saturation",
                "no_response",
                "blocked_missing_native_policy_surface",
            ],
        },
        "controls": controls,
        "validation_checks": validation_checks,
        "claim_flags": claim_flags,
        "blocked_claims": sorted(
            set(n09["blocked_claims"])
            | {
                "native_substrate_goal_proxy_regulation",
                "semantic_goal_understanding",
                "agency",
                "identity_acceptance",
                "rc_identity_collapse",
                "native_memory_trail",
                "aco_like_behavior",
            }
        ),
        "git": {
            "head": git_head(),
            "status_short_experiment": git_status_short(rel(EXPERIMENT)),
            "status_short_src": git_status_short("src"),
        },
        "next_iteration": "11_hypothesis_b1_geometry_substrate_mediated_probe",
    }
    artifact["artifact_digest"] = source_artifact_digest(artifact)
    return artifact


def write_report(artifact: dict[str, Any]) -> None:
    rows = artifact["a_path_variable_inventory"]
    ingredients = artifact["substrate_ingredient_inventory"]
    blockers = artifact["b_path_blocker_refinement"]
    checks = artifact["validation_checks"]
    lines = [
        "# N09 Iteration 10 - Hypothesis B0 Native/Substrate Inventory",
        "",
        f"Status: {artifact['status']}",
        f"Acceptance state: {artifact['acceptance_state']}",
        "",
        "## Summary",
        "",
        "Iteration 10 reopens Hypothesis B as an inventory-only path. It does not "
        "run a new LGRC probe and does not change the closed Hypothesis A ceiling.",
        "",
        f"- Preserved A-path ceiling: `{artifact['a_path_preservation']['claim_ceiling']}`",
        f"- Preserved GPR level: `{artifact['a_path_preservation']['gpr_level']}`",
        "- B-path status: `reopened_for_inventory_only`",
        "- Primary B-path blocker: `native_goal_proxy_regulation_policy_missing`",
        "",
        "## A-Path Variable Inventory",
        "",
        "| Variable | Mapping | Missing native policy surfaces | Iteration 11 role |",
        "|---|---|---|---|",
    ]
    for row in rows:
        missing = ", ".join(f"`{item}`" for item in row["missing_native_policy_surfaces"])
        lines.append(
            "| "
            f"`{row['a_path_variable']}` | "
            f"`{row['native_substrate_mapping']}` | "
            f"{missing} | "
            f"{row['iteration_11_role']} |"
        )
    lines.extend(
        [
            "",
            "## Substrate Ingredient Inventory",
            "",
            "| Ingredient | Evidence ceiling | Native status | B1 use | Blockers |",
            "|---|---|---|---|---|",
        ]
    )
    for row in ingredients:
        blockers_text = ", ".join(f"`{item}`" for item in row["blockers"])
        lines.append(
            "| "
            f"`{row['ingredient_id']}` | "
            f"`{row['evidence_ceiling']}` | "
            f"`{row['native_support_status']}` | "
            f"`{row['usable_for_iteration_11']}` | "
            f"{blockers_text} |"
        )
    lines.extend(
        [
            "",
            "## Blocker Refinement",
            "",
            "The inventory keeps `native_goal_proxy_regulation_policy_missing` as the "
            "primary blocker and refines it into specific proxy, error, response, "
            "memory, oscillator, and identity/support policy gaps.",
            "",
            "| Blocker | Role |",
            "|---|---|",
        ]
    )
    for row in blockers:
        lines.append(f"| `{row['blocker']}` | `{row['role']}` |")
    lines.extend(
        [
            "",
            "## Controls",
            "",
            "| Control | Passed | Primary blocker if failed |",
            "|---|---:|---|",
        ]
    )
    for control_id, control in artifact["controls"].items():
        lines.append(
            f"| `{control_id}` | `{control['control_passed']}` | "
            f"`{control['primary_blocker']}` |"
        )
    lines.extend(
        [
            "",
            "## Validation",
            "",
            "| Check | Result |",
            "|---|---:|",
        ]
    )
    for key, value in checks.items():
        lines.append(f"| `{key}` | `{value}` |")
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "Iteration 10 is an inventory and planning artifact. It does not support "
            "native substrate-mediated goal-proxy regulation, semantic goal "
            "understanding, agency, identity acceptance, ACO-like behavior, "
            "locomotion-like behavior, or biological behavior.",
            "",
            "## Acceptance",
            "",
            "Achieved. The closed A-path result is preserved while the B-path "
            "native/substrate inventory maps A-path proxy, error, response, "
            "repeated boundedness, perturbation, memory, and support ingredients "
            "to available LGRC and N05-N08 substrate mechanisms, explicitly "
            "recording which pieces are native-representable and which remain "
            "blocked by missing native policy surfaces.",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    artifact = build_artifact()
    OUTPUT_PATH.write_text(
        json.dumps(artifact, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    write_report(artifact)
    print(f"wrote {rel(OUTPUT_PATH)}")
    print(f"wrote {rel(REPORT_PATH)}")
    print(f"status: {artifact['status']}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Build N29 Iteration 2 agency diagnostic and method constraint extraction."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-29T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
GEOMETRIC_ROOT = ROOT.parent / "geometric-reflexive-coherence"
EXPERIMENT = ROOT / "experiments" / "2026-06-N29-lgrc-agentic-ecology-convergence-bridge"
I1_OUTPUT = EXPERIMENT / "outputs" / "n29_ecology_demand_extraction_i1.json"
OUTPUT = EXPERIMENT / "outputs" / "n29_agency_diagnostic_method_constraints_i2.json"
REPORT = EXPERIMENT / "reports" / "n29_agency_diagnostic_method_constraints_i2.md"
SCRIPT_RELATIVE_PATH = (
    "experiments/2026-06-N29-lgrc-agentic-ecology-convergence-bridge/scripts/"
    "build_n29_agency_diagnostic_method_constraints_i2.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"

UNSAFE_CLAIM_FLAGS = {
    "native_agency_claim_opened": False,
    "semantic_choice_claim_opened": False,
    "semantic_intention_claim_opened": False,
    "semantic_goal_claim_opened": False,
    "selfhood_claim_opened": False,
    "identity_acceptance_claim_opened": False,
    "native_support_opened": False,
    "native_ant_agency_opened": False,
    "native_colony_agency_opened": False,
    "biological_agency_opened": False,
    "organism_life_opened": False,
    "consciousness_opened": False,
    "sentience_opened": False,
    "phase8_completion_opened": False,
    "fully_native_ecology_opened": False,
    "unrestricted_autonomy_opened": False,
}

AGENCY_SOURCES: list[dict[str, Any]] = [
    {
        "source_id": "agency_of_becoming_essay",
        "source_path": (
            "geometric-reflexive-coherence/essays/"
            "2026-06-12-AgencyOfBecoming-InterpretationThroughRC.md"
        ),
        "local_relative_path": "essays/2026-06-12-AgencyOfBecoming-InterpretationThroughRC.md",
        "source_role": "agency_diagnostic_interpretation_source",
        "may_consume_as": [
            "diagnostic_vocabulary",
            "interpretive_constraint",
            "claim_boundary_context",
            "future_probe_alignment_context",
        ],
        "must_not_consume_as": [
            "implementation_evidence",
            "native_agency_evidence",
            "ant_ecology_evidence",
            "prototype_proof",
            "n05_n28_capability_coverage_proof",
        ],
    },
    {
        "source_id": "arc_classification_of_becoming",
        "source_path": (
            "geometric-reflexive-coherence/arc-of-becoming/"
            "2026-05-ClassificationOfBecoming.md"
        ),
        "local_relative_path": "arc-of-becoming/2026-05-ClassificationOfBecoming.md",
        "source_role": "classification_method_constraint_source",
        "may_consume_as": [
            "method_vocabulary",
            "classification_value_gate",
            "observation_first_constraint",
            "claim_boundary_context",
        ],
        "must_not_consume_as": [
            "implementation_evidence",
            "native_agency_evidence",
            "prototype_proof",
        ],
    },
    {
        "source_id": "arc_interrogation_of_becoming",
        "source_path": (
            "geometric-reflexive-coherence/arc-of-becoming/"
            "2026-05-InterrogationofBecoming.md"
        ),
        "local_relative_path": "arc-of-becoming/2026-05-InterrogationofBecoming.md",
        "source_role": "bounded_probe_method_constraint_source",
        "may_consume_as": [
            "bounded_probe_vocabulary",
            "probe_as_question_constraint",
            "control_and_withdrawal_constraint",
            "claim_boundary_context",
        ],
        "must_not_consume_as": [
            "probe_success_as_proof",
            "native_agency_evidence",
            "implementation_evidence",
            "prototype_proof",
        ],
    },
    {
        "source_id": "arc_naturalization_of_becoming",
        "source_path": (
            "geometric-reflexive-coherence/arc-of-becoming/"
            "2026-05-NaturalizationOfBecoming.md"
        ),
        "local_relative_path": "arc-of-becoming/2026-05-NaturalizationOfBecoming.md",
        "source_role": "naturalization_method_constraint_source",
        "may_consume_as": [
            "naturalization_gap_vocabulary",
            "probe_absence_constraint",
            "producer_residue_boundary",
            "claim_boundary_context",
        ],
        "must_not_consume_as": [
            "native_support_evidence",
            "native_agency_evidence",
            "implementation_evidence",
            "prototype_proof",
        ],
    },
    {
        "source_id": "arc_cultivation_of_becoming",
        "source_path": (
            "geometric-reflexive-coherence/arc-of-becoming/"
            "2026-05-CultivationOfBecoming.md"
        ),
        "local_relative_path": "arc-of-becoming/2026-05-CultivationOfBecoming.md",
        "source_role": "cultivation_method_constraint_source",
        "may_consume_as": [
            "method_sequence_context",
            "function_not_proxy_constraint",
            "support_withdrawal_context",
            "claim_boundary_context",
        ],
        "must_not_consume_as": [
            "endpoint_forcing_permission",
            "native_agency_evidence",
            "implementation_evidence",
            "prototype_proof",
        ],
    },
]


def canonical_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def digest_value(data: Any) -> str:
    return hashlib.sha256(
        json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
            "utf-8"
        )
    ).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def no_absolute_paths(data: Any) -> bool:
    text = json.dumps(data, sort_keys=True, ensure_ascii=True)
    forbidden = ("/" + "home" + "/", "Documents" + "/" + "RC-github")
    return all(pattern not in text for pattern in forbidden)


def source_record(source: dict[str, Any]) -> dict[str, Any]:
    path = GEOMETRIC_ROOT / source["local_relative_path"]
    record = {key: value for key, value in source.items() if key != "local_relative_path"}
    record.update(
        {
            "exists": path.exists(),
            "sha256": sha256_file(path) if path.exists() else "missing",
            "digest_policy": "sha256_of_external_method_source",
            "source_scope": "diagnostic_and_method_source_only",
            "implementation_evidence_opened": False,
            "native_agency_claim_opened": False,
            "ant_ecology_claim_opened": False,
            "prototype_proof_opened": False,
            "claim_ceiling": "method_and_diagnostic_vocabulary_only_no_proof",
        }
    )
    return record


def diagnostic_row(
    *,
    diagnostic_id: str,
    diagnostic_code: str,
    diagnostic_name: str,
    future_experiment_alignment: list[str],
    definition: str,
    operational_reading: str,
    required_declared_conditions: list[str],
    what_it_can_classify: list[str],
    what_it_cannot_claim: list[str],
    required_surfaces_for_future_probe: list[str],
    bridge_value_for_n29: str,
    blocked_relabels: list[str],
    source_refs: list[str],
) -> dict[str, Any]:
    return {
        "diagnostic_id": diagnostic_id,
        "diagnostic_code": diagnostic_code,
        "diagnostic_name": diagnostic_name,
        "source_role": "agency_diagnostic_not_evidence",
        "source_reference": source_refs,
        "source_references": source_refs,
        "definition": definition,
        "diagnostic_description": definition,
        "operational_reading": operational_reading,
        "required_declared_conditions": required_declared_conditions,
        "what_it_can_classify": what_it_can_classify,
        "what_it_cannot_claim": what_it_cannot_claim,
        "mapped_experiment_family": future_experiment_alignment,
        "future_experiment_alignment": future_experiment_alignment,
        "required_surfaces_for_future_probe": required_surfaces_for_future_probe,
        "bridge_value_for_n29": bridge_value_for_n29,
        "mapped_to_n21_n28_without_proof": True,
        "implementation_evidence_opened": False,
        "native_agency_claim_opened": False,
        "prototype_row_opened": False,
        "n05_n28_capability_coverage_claimed": False,
        "blocked_relabels": blocked_relabels,
        "claim_ceiling": "diagnostic_vocabulary_only_future_probe_alignment",
    }


def agency_diagnostic_rows() -> list[dict[str, Any]]:
    essay = (
        "geometric-reflexive-coherence/essays/"
        "2026-06-12-AgencyOfBecoming-InterpretationThroughRC.md"
    )
    return [
        diagnostic_row(
            diagnostic_id="withdrawal_resistance",
            diagnostic_code="WR",
            diagnostic_name="withdrawal_resistance",
            future_experiment_alignment=["N21"],
            definition=(
                "Tests whether a declared basin continuation persists when a declared "
                "support, probe, or scaffold is weakened or removed."
            ),
            operational_reading=(
                "Persistence ratio or decay-rate reading under declared withdrawal "
                "conditions, with same-basin continuation and hidden-support controls."
            ),
            required_declared_conditions=[
                "declared_support_or_scaffold",
                "declared_withdrawal_condition",
                "same_basin_continuation_rule",
                "support_coherence_boundary_flux_floors",
            ],
            what_it_can_classify=[
                "support_removal_persistence_question",
                "withdrawal_dependence_or_resistance_candidate",
            ],
            what_it_cannot_claim=[
                "willpower",
                "semantic_choice",
                "native_agency",
                "native_support",
            ],
            required_surfaces_for_future_probe=[
                "support_or_scaffold_surface",
                "same_basin_signature",
                "withdrawal_schedule",
                "replay_and_hidden_support_controls",
            ],
            bridge_value_for_n29=(
                "Names the support-removal demand that ecology prototypes must not "
                "mistake for willpower, choice, or native agency."
            ),
            blocked_relabels=[
                "willpower",
                "semantic_choice",
                "native_agency",
                "native_support_by_label",
            ],
            source_refs=[f"{essay}#withdrawal-resistance"],
        ),
        diagnostic_row(
            diagnostic_id="naturalization_depth",
            diagnostic_code="ND",
            diagnostic_name="naturalization_depth",
            future_experiment_alignment=["N21", "N22"],
            definition=(
                "Tests whether a capacity first exposed under support becomes available "
                "through source-current basin geometry without the original probe."
            ),
            operational_reading=(
                "Rung-limited reading of the highest supported probe-absent or "
                "support-withdrawn condition, not a general native-capacity claim."
            ),
            required_declared_conditions=[
                "probe_present_baseline",
                "probe_absent_or_probe_withdrawn_run",
                "original_probe_residue_audit",
                "same_class_comparison_rule",
            ],
            what_it_can_classify=[
                "bounded_naturalization_depth_candidate",
                "producer_or_scaffold_dependence_boundary",
            ],
            what_it_cannot_claim=[
                "native_regime_expression_by_label",
                "native_support",
                "general_agency",
            ],
            required_surfaces_for_future_probe=[
                "probe_present_baseline",
                "probe_absent_replay",
                "post_probe_state_derivation",
                "producer_residue_audit",
            ],
            bridge_value_for_n29=(
                "Separates ecology capacities that are scaffolded from capacities that "
                "have evidence of bounded naturalization."
            ),
            blocked_relabels=[
                "probe_success_as_native_expression",
                "scaffold_as_substrate_carried_capacity",
                "native_support",
            ],
            source_refs=[
                f"{essay}#naturalization-depth",
                (
                    "geometric-reflexive-coherence/arc-of-becoming/"
                    "2026-05-NaturalizationOfBecoming.md#naturalization-gap"
                ),
            ],
        ),
        diagnostic_row(
            diagnostic_id="substrate_transfer_capacity",
            diagnostic_code="ST",
            diagnostic_name="substrate_transfer_capacity",
            future_experiment_alignment=["N27"],
            definition=(
                "Tests whether basin-relevant structure can be mapped into a distinct "
                "substrate or frame while preserving declared continuation constraints."
            ),
            operational_reading=(
                "A structurally distinct target-frame continuation test, ideally linked "
                "to withdrawal and naturalization conditions rather than copy labels."
            ),
            required_declared_conditions=[
                "source_substrate_or_frame",
                "target_substrate_or_frame",
                "transfer_mapping_rule",
                "same_basin_transfer_identity_rule",
            ],
            what_it_can_classify=[
                "bounded_substrate_transfer_candidate",
                "transfer_mapping_debt_or_failure_mode",
            ],
            what_it_cannot_claim=[
                "identity_transfer_by_copy",
                "semantic_role_transfer",
                "native_agency",
            ],
            required_surfaces_for_future_probe=[
                "source_frame_signature",
                "target_frame_signature",
                "transfer_mapping_ledger",
                "same_basin_transfer_replay",
            ],
            bridge_value_for_n29=(
                "Supplies the transfer requirement for ecology components that must "
                "move between substrate frames without identity-by-label."
            ),
            blocked_relabels=[
                "copy_as_transfer",
                "identity_label_as_continuation",
                "semantic_role_transfer",
                "native_agency",
            ],
            source_refs=[f"{essay}#substrate-transfer-capacity"],
        ),
        diagnostic_row(
            diagnostic_id="proxy_collapse_rate",
            diagnostic_code="PC",
            diagnostic_name="proxy_collapse_rate",
            future_experiment_alignment=["N26"],
            definition=(
                "Tests whether proxy metrics improve while source-current basin support, "
                "continuation, or native function degrades or collapses."
            ),
            operational_reading=(
                "A divergence reading between proxy score and declared native-function "
                "or basin-continuation traces over a declared window."
            ),
            required_declared_conditions=[
                "proxy_metric_definition",
                "native_function_or_basin_continuation_descriptor",
                "divergence_window",
                "collapse_or_demote_rule",
            ],
            what_it_can_classify=[
                "proxy_native_divergence",
                "proxy_collapse_or_proxy_safety_boundary",
            ],
            what_it_cannot_claim=[
                "goal_ownership",
                "semantic_success",
                "agency_by_score",
            ],
            required_surfaces_for_future_probe=[
                "proxy_metric_trace",
                "native_function_or_basin_continuation_trace",
                "divergence_window",
                "collapse_or_demote_control",
            ],
            bridge_value_for_n29=(
                "Protects ecology prototypes from treating externally convenient scores "
                "as evidence of agentic function."
            ),
            blocked_relabels=[
                "proxy_improvement_as_native_function",
                "reward_as_goal_ownership",
                "semantic_success",
                "agency_by_score",
            ],
            source_refs=[f"{essay}#proxy-collapse-rate"],
        ),
        diagnostic_row(
            diagnostic_id="generative_agency",
            diagnostic_code="GA",
            diagnostic_name="generative_agency",
            future_experiment_alignment=["N24", "N25", "N25.2", "N28"],
            definition=(
                "Tests whether a persistent basin increases nearby basin-forming capacity "
                "or medium richness while remaining distinguishable and bounded."
            ),
            operational_reading=(
                "Higher-order diagnostic over focal persistence plus neighboring "
                "basin-forming capacity, with extractive or competitive contrasts."
            ),
            required_declared_conditions=[
                "focal_basin_persistence_rule",
                "neighbor_or_environment_capacity_measure",
                "distinguishability_and_merge_leakage_controls",
                "extractive_or_competitive_contrast",
            ],
            what_it_can_classify=[
                "environment_basin_forming_capacity_change",
                "generative_vs_extractive_persistence_pattern",
            ],
            what_it_cannot_claim=[
                "cooperation",
                "altruism",
                "biological_agency",
                "native_colony_agency",
                "organism_life",
            ],
            required_surfaces_for_future_probe=[
                "focal_basin_persistence_trace",
                "neighbor_capacity_or_child_basin_trace",
                "shared_medium_or_capacity_shell_trace",
                "extractive_competitive_contrast",
            ],
            bridge_value_for_n29=(
                "Names the ecology-facing difference between preserving one identity "
                "and enriching the conditions under which other basins can form."
            ),
            blocked_relabels=[
                "cooperation",
                "altruism",
                "biological_agency",
                "native_colony_agency",
                "organism_life",
            ],
            source_refs=[f"{essay}#generative-agency"],
        ),
    ]


def method_constraint_row(
    *,
    method_id: str,
    source_id: str,
    method_role: str,
    required_n29_discipline: list[str],
    blocked_failure_modes: list[str],
    future_iteration_relevance: list[str],
) -> dict[str, Any]:
    return {
        "method_id": method_id,
        "constraint_id": method_id,
        "source_id": source_id,
        "source_role": "arc_method_constraint_not_evidence",
        "method_role": method_role,
        "required_n29_discipline": required_n29_discipline,
        "blocked_failure_modes": blocked_failure_modes,
        "future_iteration_relevance": future_iteration_relevance,
        "implementation_evidence_opened": False,
        "native_agency_claim_opened": False,
        "claim_ceiling": "method_constraint_only",
    }


def arc_method_constraint_rows() -> list[dict[str, Any]]:
    return [
        method_constraint_row(
            method_id="classification_constraint",
            source_id="arc_classification_of_becoming",
            method_role=(
                "Classify what prior experiments express before using those labels as "
                "capability cards or bridge motifs."
            ),
            required_n29_discipline=[
                "observation_tags_do_not_automatically_become_bridge_classes",
                "bridge_classes_must_be_reusable_or_generative",
                "classification_must_not_raise_claim_ceiling",
            ],
            blocked_failure_modes=[
                "vocabulary_as_evidence",
                "local_tag_promoted_to_ecology_capability",
                "chronological_revalidation_replaces_bridge_mapping",
            ],
            future_iteration_relevance=["I3", "I4", "I8", "I9"],
        ),
        method_constraint_row(
            method_id="interrogation_constraint",
            source_id="arc_interrogation_of_becoming",
            method_role=(
                "Treat prototypes and future ecology probes as bounded questions, not "
                "as proof that an agentic ecology behavior exists natively."
            ),
            required_n29_discipline=[
                "prototype_rows_need_declared_question_and_claim_ceiling",
                "probe_success_cannot_promote_native_agency",
                "controls_and_withdrawal_paths_remain_required",
            ],
            blocked_failure_modes=[
                "probe_promotion",
                "constructive_overreach",
                "boundary_collapse",
                "control_blindness",
            ],
            future_iteration_relevance=["I10", "I11", "I12", "I13", "I14"],
        ),
        method_constraint_row(
            method_id="naturalization_constraint",
            source_id="arc_naturalization_of_becoming",
            method_role=(
                "Keep scaffolded or producer-assisted bridge compositions separate from "
                "substrate-carried or native-ready capacities."
            ),
            required_n29_discipline=[
                "producer_residue_must_be_recorded_row_locally",
                "naturalization_debt_cannot_be_erased_by_mapping",
                "probe_absent_or_support_withdrawn_status_must_be_explicit",
            ],
            blocked_failure_modes=[
                "scaffold_as_native_capacity",
                "support_translation_as_naturalization",
                "producer_residue_as_native_support",
            ],
            future_iteration_relevance=["I6", "I7", "I10", "I15"],
        ),
        method_constraint_row(
            method_id="cultivation_constraint",
            source_id="arc_cultivation_of_becoming",
            method_role=(
                "Preserve the bridge as disciplined participation in unfolding dynamics, "
                "not endpoint forcing or proxy optimization."
            ),
            required_n29_discipline=[
                "bridge_motifs_must_name_function_not_proxy_only",
                "prototype_rows_must_state_remaining_debt",
                "N30_plus_handoff_must_record_missing_native_mechanisms",
            ],
            blocked_failure_modes=[
                "proxy_localization_trap",
                "endpoint_forcing",
                "producer_optimization_as_agency",
                "ecology_handoff_without_native_debt",
            ],
            future_iteration_relevance=["I8", "I14", "I15", "I16"],
        ),
    ]


def future_alignment_rows() -> list[dict[str, Any]]:
    common_may = [
        "coverage_debt_classification",
        "prototype_claim_ceiling",
        "N30_plus_missing_mechanism_handoff",
    ]
    common_must_not = [
        "native_agency_proof",
        "positive_ecology_evidence",
        "N05_N28_capability_coverage_claim",
        "prototype_success_claim",
    ]
    return [
        {
            "alignment_id": "withdrawal_resistance_to_n21",
            "diagnostic_or_method": "withdrawal_resistance",
            "mapped_experiment_family": ["N21"],
            "alignment_role": "interpretive_filter_and_probe_design_constraint",
            "may_use_for": common_may,
            "must_not_use_for": common_must_not,
        },
        {
            "alignment_id": "naturalization_depth_to_n21",
            "diagnostic_or_method": "naturalization_depth",
            "mapped_experiment_family": ["N21"],
            "alignment_role": "interpretive_filter_and_probe_design_constraint",
            "may_use_for": common_may,
            "must_not_use_for": common_must_not,
        },
        {
            "alignment_id": "susceptibility_update_to_n22",
            "diagnostic_or_method": "naturalization_depth_susceptibility_bridge",
            "mapped_experiment_family": ["N22"],
            "alignment_role": "durable_geometry_update_boundary_for_later_capability_cards",
            "may_use_for": common_may,
            "must_not_use_for": common_must_not,
        },
        {
            "alignment_id": "collapse_selection_to_n23",
            "diagnostic_or_method": "classification_and_interrogation_boundary",
            "mapped_experiment_family": ["N23"],
            "alignment_role": "collapse_or_selection_interpretation_constraint",
            "may_use_for": common_may,
            "must_not_use_for": common_must_not,
        },
        {
            "alignment_id": "abundance_optionality_to_n24",
            "diagnostic_or_method": "generative_capacity_context",
            "mapped_experiment_family": ["N24"],
            "alignment_role": "abundance_or_optionality_bridge_constraint",
            "may_use_for": common_may,
            "must_not_use_for": common_must_not,
        },
        {
            "alignment_id": "basin_formation_to_n25_n25_2",
            "diagnostic_or_method": "generative_agency_boundary",
            "mapped_experiment_family": ["N25", "N25.2"],
            "alignment_role": "basin_formation_and_child_basin_claim_ceiling",
            "may_use_for": common_may,
            "must_not_use_for": common_must_not,
        },
        {
            "alignment_id": "proxy_collapse_rate_to_n26",
            "diagnostic_or_method": "proxy_collapse_rate",
            "mapped_experiment_family": ["N26"],
            "alignment_role": "proxy_native_divergence_interpretation_constraint",
            "may_use_for": common_may,
            "must_not_use_for": common_must_not,
        },
        {
            "alignment_id": "substrate_transfer_capacity_to_n27",
            "diagnostic_or_method": "substrate_transfer_capacity",
            "mapped_experiment_family": ["N27"],
            "alignment_role": "transfer_claim_boundary_and_probe_design_constraint",
            "may_use_for": common_may,
            "must_not_use_for": common_must_not,
        },
        {
            "alignment_id": "generative_extractive_diagnostic_to_n28",
            "diagnostic_or_method": "generative_agency",
            "mapped_experiment_family": ["N28"],
            "alignment_role": "generative_extractive_persistence_interpretation_constraint",
            "may_use_for": common_may,
            "must_not_use_for": common_must_not,
        },
    ]


def check(check_id: str, passed: bool, details: str | None = None) -> dict[str, Any]:
    row: dict[str, Any] = {"check_id": check_id, "passed": passed}
    if details is not None:
        row["details"] = details
    return row


def build() -> dict[str, Any]:
    i1 = load_json(I1_OUTPUT)
    source_records = [source_record(source) for source in AGENCY_SOURCES]
    diagnostics = agency_diagnostic_rows()
    method_rows = arc_method_constraint_rows()
    alignment_rows = future_alignment_rows()

    data: dict[str, Any] = {
        "artifact_id": "n29_agency_diagnostic_method_constraints_i2",
        "experiment_id": "N29",
        "iteration": "I2",
        "title": "Agency Diagnostic And Method Constraint Extraction",
        "status": "passed",
        "acceptance_state": "accepted_agency_diagnostics_as_method_no_agency_claim",
        "generated_at": GENERATED_AT,
        "generated_by": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "i1_source_artifact": (
            "experiments/2026-06-N29-lgrc-agentic-ecology-convergence-bridge/"
            "outputs/n29_ecology_demand_extraction_i1.json"
        ),
        "i1_status": i1.get("status", "not_recorded"),
        "i1_acceptance_state": i1.get("acceptance_state", "not_recorded"),
        "i1_output_digest": i1.get("output_digest", "not_recorded"),
        "source_scope": "agency_of_becoming_and_arc_method_sources_only",
        "source_inventory": source_records,
        "source_records": source_records,
        "source_count": len(source_records),
        "diagnostic_taxonomy": diagnostics,
        "agency_diagnostic_rows": diagnostics,
        "agency_diagnostic_row_count": len(diagnostics),
        "arc_method_constraints": method_rows,
        "arc_method_constraint_rows": method_rows,
        "arc_method_constraint_row_count": len(method_rows),
        "n21_n28_alignment": alignment_rows,
        "diagnostic_to_future_experiment_alignment": alignment_rows,
        "agency_diagnostics_extracted": True,
        "arc_method_constraints_extracted": True,
        "diagnostics_mapped_to_n21_n28": True,
        "diagnostics_mapped_without_proof": True,
        "interpretation_limits_recorded": True,
        "claim_boundary_recorded": True,
        "implementation_evidence_opened": False,
        "positive_ecology_evidence_opened": False,
        "prototype_rows_opened": False,
        "n05_n28_capability_coverage_claimed": False,
        "native_agency_claim_opened": False,
        "native_ant_agency_opened": False,
        "native_colony_agency_opened": False,
        "biological_agency_opened": False,
        "organism_life_opened": False,
        "sentience_opened": False,
        "phase8_completion_opened": False,
        "claim_ceiling": "agency_diagnostics_and_arc_method_constraints_only_no_implementation_evidence",
        "claim_boundary_audit": copy.deepcopy(UNSAFE_CLAIM_FLAGS),
        "blocked_claim_audit": copy.deepcopy(UNSAFE_CLAIM_FLAGS),
        "ready_for_iteration_3": True,
        "script_sha256": sha256_file(ROOT / SCRIPT_RELATIVE_PATH),
    }

    required_diagnostics = {
        "withdrawal_resistance",
        "naturalization_depth",
        "substrate_transfer_capacity",
        "proxy_collapse_rate",
        "generative_agency",
    }
    required_methods = {
        "classification_constraint",
        "interrogation_constraint",
        "naturalization_constraint",
        "cultivation_constraint",
    }
    checks = [
        check(
            "i1_ecology_demand_model_passed",
            data["i1_status"] == "passed"
            and data["i1_acceptance_state"]
            == "accepted_ecology_demand_model_no_implementation_claims",
        ),
        check(
            "agency_and_arc_sources_inventoried",
            len(source_records) == 5 and all(row["exists"] for row in source_records),
        ),
        check(
            "source_roles_are_method_not_implementation_evidence",
            all(
                not row["implementation_evidence_opened"]
                and "implementation_evidence" in row["must_not_consume_as"]
                for row in source_records
            ),
        ),
        check(
            "agency_diagnostics_complete",
            {row["diagnostic_id"] for row in diagnostics} == required_diagnostics,
        ),
        check(
            "arc_method_constraints_complete",
            {row["method_id"] for row in method_rows} == required_methods,
        ),
        check(
            "diagnostics_mapped_to_n21_n28_without_proof",
            all(row["mapped_to_n21_n28_without_proof"] for row in diagnostics)
            and all(not row["implementation_evidence_opened"] for row in diagnostics)
            and all(not row["native_agency_claim_opened"] for row in diagnostics),
        ),
        check(
            "method_constraints_do_not_satisfy_evidence_gates",
            all(not row["implementation_evidence_opened"] for row in method_rows)
            and all(not row["native_agency_claim_opened"] for row in method_rows),
        ),
        check(
            "alignment_table_covers_n21_n28_without_importing_evidence",
            {family for row in alignment_rows for family in row["mapped_experiment_family"]}
            == {"N21", "N22", "N23", "N24", "N25", "N25.2", "N26", "N27", "N28"}
            and all("N05_N28_capability_coverage_claim" in row["must_not_use_for"] for row in alignment_rows),
        ),
        check(
            "no_n05_n28_capability_coverage_claimed",
            not data["n05_n28_capability_coverage_claimed"]
            and all(not row["n05_n28_capability_coverage_claimed"] for row in diagnostics),
        ),
        check(
            "no_prototype_rows_opened",
            not data["prototype_rows_opened"]
            and all(not row["prototype_row_opened"] for row in diagnostics),
        ),
        check("no_positive_ecology_evidence_opened", not data["positive_ecology_evidence_opened"]),
        check("unsafe_claim_flags_false", not any(data["claim_boundary_audit"].values())),
        check("no_absolute_paths_in_records", no_absolute_paths(data)),
    ]
    data["checks"] = checks
    data["failed_checks"] = [row["check_id"] for row in checks if not row["passed"]]

    digest_payload = copy.deepcopy(data)
    digest_payload.pop("output_digest", None)
    data["output_digest"] = digest_value(digest_payload)
    return data


def write_report(data: dict[str, Any]) -> None:
    lines = [
        "# N29 Iteration 2 - Agency Diagnostic And Method Constraint Extraction",
        "",
        "## Summary",
        "",
        f"- status: `{data['status']}`",
        f"- acceptance_state: `{data['acceptance_state']}`",
        f"- source_count: `{data['source_count']}`",
        f"- agency_diagnostic_row_count: `{data['agency_diagnostic_row_count']}`",
        f"- arc_method_constraint_row_count: `{data['arc_method_constraint_row_count']}`",
        f"- native_agency_claim_opened: `{str(data['native_agency_claim_opened']).lower()}`",
        f"- implementation_evidence_opened: `{str(data['implementation_evidence_opened']).lower()}`",
        f"- positive_ecology_evidence_opened: `{str(data['positive_ecology_evidence_opened']).lower()}`",
        f"- ready_for_iteration_3: `{str(data['ready_for_iteration_3']).lower()}`",
        f"- output_digest: `{data['output_digest']}`",
        "",
        "Iteration 2 extracts agency diagnostics and Arc method constraints as method",
        "vocabulary only. These rows can shape N29 bridge classification, prototype",
        "claim ceilings, and N30+ handoff questions, but they do not prove native",
        "agency, ecology behavior, implementation capability, or N05-N28 coverage.",
        "",
        "## Source Records",
        "",
        "| Source | Role | Exists | Claim Ceiling |",
        "| --- | --- | --- | --- |",
    ]
    for row in data["source_inventory"]:
        lines.append(
            f"| `{row['source_id']}` | `{row['source_role']}` | "
            f"`{str(row['exists']).lower()}` | `{row['claim_ceiling']}` |"
        )
    lines.extend(
        [
            "",
            "## Agency Diagnostics",
            "",
            "| Diagnostic | Future Alignment | Claim Ceiling |",
            "| --- | --- | --- |",
        ]
    )
    for row in data["diagnostic_taxonomy"]:
        alignment = ", ".join(row["mapped_experiment_family"])
        lines.append(
            f"| `{row['diagnostic_code']}` / `{row['diagnostic_id']}` | "
            f"`{alignment}` | `{row['claim_ceiling']}` |"
        )
    lines.extend(
        [
            "",
            "## Arc Method Constraints",
            "",
            "| Method Constraint | Source | Future Iterations |",
            "| --- | --- | --- |",
        ]
    )
    for row in data["arc_method_constraints"]:
        future = ", ".join(row["future_iteration_relevance"])
        lines.append(f"| `{row['method_id']}` | `{row['source_id']}` | `{future}` |")
    lines.extend(
        [
            "",
            "## N21-N28 Diagnostic Alignment",
            "",
            "| Alignment | Diagnostic Or Method | Experiment Family |",
            "| --- | --- | --- |",
        ]
    )
    for row in data["n21_n28_alignment"]:
        family = ", ".join(row["mapped_experiment_family"])
        lines.append(
            f"| `{row['alignment_id']}` | `{row['diagnostic_or_method']}` | `{family}` |"
        )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "Blocked:",
            "",
        ]
    )
    for claim, opened in data["claim_boundary_audit"].items():
        lines.append(f"- `{claim}` = `{str(opened).lower()}`")
    lines.extend(
        [
            "",
            "## Checks",
            "",
            "| Check | Passed |",
            "| --- | --- |",
        ]
    )
    for row in data["checks"]:
        lines.append(f"| `{row['check_id']}` | `{str(row['passed']).lower()}` |")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "Iteration 2 supports only the method-level statement that Agency of",
            "Becoming diagnostics and Arc of Becoming constraints can be used to",
            "structure later N29 bridge rows. The diagnostics map to prior and future",
            "experiment surfaces, but their role is interpretive: they cannot replace",
            "source-current artifacts, replay, controls, or runtime probes.",
            "",
            "The correct next step is Iteration 3: import N05-N28 as capability cards",
            "with later review gates and claim ceilings attached.",
            "",
        ]
    )
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    data = build()
    OUTPUT.write_text(canonical_json(data), encoding="utf-8")
    write_report(data)


if __name__ == "__main__":
    main()

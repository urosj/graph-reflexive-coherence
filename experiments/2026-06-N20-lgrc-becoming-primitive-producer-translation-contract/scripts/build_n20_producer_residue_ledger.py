#!/usr/bin/env python3
"""Build N20 Iteration 3 producer-residue and naturalization-debt ledger."""

from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-22T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = (
    ROOT
    / "experiments"
    / "2026-06-N20-lgrc-becoming-primitive-producer-translation-contract"
)
SCHEMA = EXPERIMENT / "outputs" / "n20_translation_schema_v1.json"
OUTPUT = EXPERIMENT / "outputs" / "n20_producer_residue_ledger.json"
REPORT = EXPERIMENT / "reports" / "n20_producer_residue_ledger.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N20-lgrc-becoming-primitive-producer-translation-contract/"
    "scripts/build_n20_producer_residue_ledger.py"
)

INVARIANTS = {
    "primitive_evidence_opened": False,
    "agency_claim_opened": False,
    "phase8_opened": False,
    "native_support_opened": False,
    "sentience_opened": False,
    "ant_ecology_spec_opened": False,
    "src_diff_empty_required": True,
}

COMMON_BLOCKED_RELABELS = [
    "agency",
    "semantic_choice",
    "semantic_intention",
    "semantic_goal",
    "semantic_goal_ownership",
    "semantic_action",
    "semantic_perception",
    "selfhood",
    "identity_acceptance",
    "sentience",
    "consciousness",
    "native_support",
    "phase8_implementation",
    "organism_life",
    "native_ant_agency",
    "native_colony_agency",
    "unrestricted_autonomy",
]

PRIMITIVE_DEFINITIONS: list[dict[str, Any]] = [
    {
        "primitive_id": "withdrawal_resistance",
        "primitive_name": "Withdrawal Resistance",
        "roadmap_target": "N21",
        "expected_first_positive_experiment": "N21",
        "diagnostic_source_titles": [
            "Agency of Becoming: An Interpretation Through Reflexive Coherence",
            "Interrogation of Becoming",
            "Naturalization of Becoming",
        ],
        "source_inventory_row_ids": [
            "n20_i1_row_01_n19_implementation_boundary",
            "n20_i1_row_02_n20_n29_roadmap",
            "n20_i1_row_04_interrogation_of_becoming_method",
            "n20_i1_row_05_naturalization_of_becoming_method",
            "n20_i1_row_07_agency_of_becoming_diagnostics",
        ],
        "substrate": [
            ("basin_signature_trace", "committed basin signature fields under replay"),
            ("support_coherence_floor_trace", "source-visible support and coherence floors"),
            ("boundary_integrity_trace", "boundary condition during support reduction"),
            ("withdrawal_window_trace", "ordered support-reduction window state"),
        ],
        "producer": [
            ("declared_withdrawal_schedule", "producer chooses when support is weakened"),
            ("withdrawal_amount_policy", "producer declares support reduction amplitude"),
            ("pass_fail_threshold_label", "producer labels resistance threshold until I4/I5 freeze it"),
        ],
        "debt": [
            (
                "source_current_support_withdrawal_surface",
                "policy_debt",
                "support withdrawal must become a replay-visible producer surface before N21 support",
            ),
            (
                "producer_independent_withdrawal_replay",
                "replay_debt",
                "withdrawal result must replay without hidden runtime support",
            ),
            (
                "native_support_decay_owner",
                "state_mutation_debt",
                "state mutation owner for support decay is not yet substrate-carried",
            ),
        ],
        "additional_blocked": ["willpower", "resilience_as_identity"],
        "ap_gap_dependencies": [],
        "conditional_gap_dependencies": [],
    },
    {
        "primitive_id": "naturalization_depth",
        "primitive_name": "Naturalization Depth",
        "roadmap_target": "N21",
        "expected_first_positive_experiment": "N21",
        "diagnostic_source_titles": [
            "Naturalization of Becoming",
            "Agency of Becoming: An Interpretation Through Reflexive Coherence",
        ],
        "source_inventory_row_ids": [
            "n20_i1_row_01_n19_implementation_boundary",
            "n20_i1_row_02_n20_n29_roadmap",
            "n20_i1_row_05_naturalization_of_becoming_method",
            "n20_i1_row_07_agency_of_becoming_diagnostics",
        ],
        "substrate": [
            ("post_probe_basin_signature_trace", "basin signature after original probe is absent"),
            ("post_probe_support_floor_trace", "support floor after declared scaffold withdrawal"),
            ("post_probe_coherence_floor_trace", "coherence floor after declared scaffold withdrawal"),
            ("multi_window_replay_trace", "replay-visible persistence across multiple windows"),
        ],
        "producer": [
            ("naturalization_depth_score_formula", "producer-defined depth score"),
            ("support_source_annotation", "producer labels original and residual support source"),
            ("depth_rank_label", "producer ranks naturalization depth before contract freeze"),
        ],
        "debt": [
            (
                "source_current_producer_removal_observation",
                "source_currentness_debt",
                "producer removal must be source-current, not inferred from labels",
            ),
            (
                "multi_window_without_probe_replay",
                "replay_debt",
                "naturalization depth must replay without the original probe",
            ),
            (
                "naturalization_depth_budget_surface",
                "budget_debt",
                "residual support budget must be visible and bounded",
            ),
        ],
        "additional_blocked": ["native_absorption_by_label", "support_memory_as_selfhood"],
        "ap_gap_dependencies": [],
        "conditional_gap_dependencies": [],
    },
    {
        "primitive_id": "susceptibility_update",
        "primitive_name": "Susceptibility Update",
        "roadmap_target": "N22",
        "expected_first_positive_experiment": "N22",
        "diagnostic_source_titles": [
            "Agency After Choice",
            "N20-N29 LGRC Becoming-Agency Ecology Roadmap",
        ],
        "source_inventory_row_ids": [
            "n20_i1_row_01_n19_implementation_boundary",
            "n20_i1_row_02_n20_n29_roadmap",
            "n20_i1_row_08_agency_after_choice_vocabulary",
        ],
        "substrate": [
            ("pre_interaction_geometry_trace", "pre-interaction basin geometry"),
            ("post_interaction_geometry_trace", "post-interaction basin geometry"),
            ("susceptibility_delta_trace", "durable geometry delta visible in replay"),
            ("route_or_region_reentry_trace", "later re-entry trace through altered geometry"),
        ],
        "producer": [
            ("route_update_rule", "producer declares how prior interaction alters route susceptibility"),
            ("reinforcement_schedule", "producer schedules reinforcement or inhibition pressure"),
            ("learning_label", "learning remains interpretation, not implementation state"),
        ],
        "debt": [
            (
                "source_current_route_conditioned_state_mutation",
                "state_mutation_debt",
                "durable route-conditioned mutation is not yet source-current native policy",
            ),
            (
                "peer_route_same_budget_comparison",
                "telemetry_debt",
                "same-budget peer-route comparison is required to avoid route-label success",
            ),
            (
                "proxy_free_susceptibility_policy",
                "policy_debt",
                "susceptibility update must not inherit unresolved AP5 proxy policy",
            ),
        ],
        "additional_blocked": ["semantic_learning", "free_will"],
        "ap_gap_dependencies": [
            {
                "ap_level": "AP4",
                "source": "N19/N14",
                "status": "required_local_gap_dependency",
                "reason": "susceptibility update may depend on route-conditioned selection evidence",
            }
        ],
        "conditional_gap_dependencies": [
            {
                "ap_level": "AP5",
                "source": "N19/N15",
                "condition": "proxy or target formation participates in susceptibility update",
                "status": "conditional_local_gap_dependency",
            }
        ],
    },
    {
        "primitive_id": "live_continuation_collapse",
        "primitive_name": "Live-Continuation Collapse",
        "roadmap_target": "N23",
        "expected_first_positive_experiment": "N23",
        "diagnostic_source_titles": [
            "Agency After Choice",
            "N20-N29 LGRC Becoming-Agency Ecology Roadmap",
        ],
        "source_inventory_row_ids": [
            "n20_i1_row_01_n19_implementation_boundary",
            "n20_i1_row_02_n20_n29_roadmap",
            "n20_i1_row_08_agency_after_choice_vocabulary",
        ],
        "substrate": [
            ("live_branch_set_trace", "source-visible competing continuation branches"),
            ("branch_support_coherence_traces", "support and coherence for each branch"),
            ("collapsed_continuation_trace", "selected continuation as geometric collapse result"),
            ("counterfactual_branch_retention_trace", "non-selected branches remain auditable"),
        ],
        "producer": [
            ("branch_enumeration_policy", "producer defines which branches are counted live"),
            ("selected_branch_label", "producer label before geometry-conditioned collapse exists"),
            ("tie_breaker_schedule", "producer tie-breaking must not masquerade as choice"),
        ],
        "debt": [
            (
                "source_current_counterfactual_branch_records",
                "telemetry_debt",
                "counterfactual branches must be real source-visible alternatives",
            ),
            (
                "route_conditioned_selection_policy",
                "policy_debt",
                "AP4 route-conditioned selection remains NAT4 gap debt",
            ),
            (
                "proxy_independent_branch_valuation",
                "source_currentness_debt",
                "branch valuation must not depend on hidden AP5 proxy/target formation",
            ),
        ],
        "additional_blocked": ["semantic_choice", "intention", "preference_injection"],
        "ap_gap_dependencies": [
            {
                "ap_level": "AP4",
                "source": "N19/N14",
                "status": "required_local_gap_dependency",
                "reason": "live continuation collapse depends on route or branch consequence selection",
            }
        ],
        "conditional_gap_dependencies": [
            {
                "ap_level": "AP5",
                "source": "N19/N15",
                "condition": "proxy or target formation participates in branch valuation",
                "status": "conditional_local_gap_dependency",
            }
        ],
    },
    {
        "primitive_id": "surplus_supported_optionality",
        "primitive_name": "Surplus-Supported Optionality",
        "roadmap_target": "N24",
        "expected_first_positive_experiment": "N24",
        "diagnostic_source_titles": [
            "From Structural Abundance to Agency",
            "N20-N29 LGRC Becoming-Agency Ecology Roadmap",
        ],
        "source_inventory_row_ids": [
            "n20_i1_row_01_n19_implementation_boundary",
            "n20_i1_row_02_n20_n29_roadmap",
            "n20_i1_row_09_structural_abundance_boundary",
        ],
        "substrate": [
            ("support_surplus_margin_trace", "support above maintenance floor"),
            ("optional_continuation_set_trace", "optional branches opened by surplus"),
            ("maintenance_floor_trace", "basin remains above maintenance floor"),
            ("boundary_integrity_under_optionality_trace", "boundary stays coherent while optionality exists"),
        ],
        "producer": [
            ("optionality_enumerator", "producer lists optional continuations before N24 tests them"),
            ("exploration_schedule", "producer schedules exploration pressure"),
            ("reward_or_proxy_label", "reward/proxy label cannot replace surplus-supported geometry"),
        ],
        "debt": [
            (
                "source_current_optional_branch_telemetry",
                "telemetry_debt",
                "optional branches must be visible as geometry, not labels",
            ),
            (
                "surplus_budget_owner",
                "budget_debt",
                "surplus budget must be source-visible and bounded",
            ),
            (
                "hidden_budget_relief_control",
                "claim_boundary_debt",
                "hidden relief must be blocked before abundance can be supported",
            ),
        ],
        "additional_blocked": ["reward_maximization", "abundance_as_goal"],
        "ap_gap_dependencies": [],
        "conditional_gap_dependencies": [],
    },
    {
        "primitive_id": "spark_sub_basin_new_basin_formation",
        "primitive_name": "Spark / Sub-Basin / New-Basin Formation",
        "roadmap_target": "N25",
        "expected_first_positive_experiment": "N25",
        "diagnostic_source_titles": [
            "Agency of Becoming: An Interpretation Through Reflexive Coherence",
            "N20-N29 LGRC Becoming-Agency Ecology Roadmap",
        ],
        "source_inventory_row_ids": [
            "n20_i1_row_01_n19_implementation_boundary",
            "n20_i1_row_02_n20_n29_roadmap",
            "n20_i1_row_07_agency_of_becoming_diagnostics",
        ],
        "substrate": [
            ("bifurcation_trace", "source-visible split or basin-creation candidate"),
            ("new_boundary_candidate_trace", "distinguishable boundary for new/sub-basin"),
            ("new_basin_support_coherence_trace", "support and coherence for new/sub-basin"),
            ("replayable_distinction_trace", "distinction persists under replay"),
        ],
        "producer": [
            ("new_basin_label", "producer labels a basin before source-backed formation exists"),
            ("seed_insertion_policy", "producer may insert a seed that is not native formation"),
            ("split_threshold_schedule", "producer schedules split threshold"),
        ],
        "debt": [
            (
                "source_current_basin_birth_state_mutation",
                "state_mutation_debt",
                "basin birth must be carried as source-current geometry",
            ),
            (
                "distinguishability_replay",
                "replay_debt",
                "new/sub-basin distinction must replay without label support",
            ),
            (
                "surplus_precondition_from_n24",
                "source_currentness_debt",
                "N25 should consume N24 surplus conditions or record blocker",
            ),
        ],
        "additional_blocked": ["label_only_new_basin", "transient_as_basin"],
        "ap_gap_dependencies": [],
        "conditional_gap_dependencies": [],
    },
    {
        "primitive_id": "proxy_divergence_proxy_collapse",
        "primitive_name": "Proxy Divergence / Proxy Collapse",
        "roadmap_target": "N26",
        "expected_first_positive_experiment": "N26",
        "diagnostic_source_titles": [
            "Agency of Becoming: An Interpretation Through Reflexive Coherence",
            "Agency After Choice",
        ],
        "source_inventory_row_ids": [
            "n20_i1_row_01_n19_implementation_boundary",
            "n20_i1_row_02_n20_n29_roadmap",
            "n20_i1_row_07_agency_of_becoming_diagnostics",
            "n20_i1_row_08_agency_after_choice_vocabulary",
        ],
        "substrate": [
            ("basin_persistence_capacity_trace", "basin persistence capacity under perturbation"),
            ("support_coherence_floor_trace", "support/coherence floors independent of proxy gain"),
            ("proxy_failure_under_perturbation_trace", "collapse of proxy-only success under stress"),
            ("basin_deepening_comparison_trace", "comparison between proxy gain and basin deepening"),
        ],
        "producer": [
            ("target_derivation_policy", "producer derives target/proxy until AP5 naturalizes"),
            ("proxy_metric_formula", "producer defines the proxy metric before I4 freeze"),
            ("ranking_policy", "producer ranks proxy and basin outcomes"),
        ],
        "debt": [
            (
                "native_lower_stack_input_vector",
                "source_currentness_debt",
                "AP5 lower-stack input vector is not yet NAT4 source-current",
            ),
            (
                "source_current_proxy_derivation_policy",
                "policy_debt",
                "proxy derivation policy must be default-off and replay-visible",
            ),
            (
                "target_condition_digest_before_use",
                "replay_debt",
                "target condition digest must exist before proxy use",
            ),
        ],
        "additional_blocked": ["goal_ownership", "hidden_proxy_policy"],
        "ap_gap_dependencies": [
            {
                "ap_level": "AP5",
                "source": "N19/N15",
                "status": "required_local_gap_dependency",
                "reason": "proxy divergence/collapse depends directly on AP5 proxy derivation",
            }
        ],
        "conditional_gap_dependencies": [],
    },
    {
        "primitive_id": "configuration_substrate_transfer",
        "primitive_name": "Configuration / Substrate Transfer",
        "roadmap_target": "N27",
        "expected_first_positive_experiment": "N27",
        "diagnostic_source_titles": [
            "Agency of Becoming: An Interpretation Through Reflexive Coherence",
            "N20-N29 LGRC Becoming-Agency Ecology Roadmap",
        ],
        "source_inventory_row_ids": [
            "n20_i1_row_01_n19_implementation_boundary",
            "n20_i1_row_02_n20_n29_roadmap",
            "n20_i1_row_07_agency_of_becoming_diagnostics",
        ],
        "substrate": [
            ("pre_transfer_basin_signature_trace", "basin signature before configuration change"),
            ("post_transfer_basin_signature_trace", "basin signature after configuration change"),
            ("boundary_mapping_trace", "boundary mapping across fixture/topology change"),
            ("support_preservation_trace", "support preservation without reconstructing original support"),
        ],
        "producer": [
            ("configuration_mapping_policy", "producer defines fixture or topology mapping"),
            ("fixture_equivalence_label", "producer labels configurations as equivalent"),
            ("support_reconstruction_schedule", "producer may reconstruct original support"),
        ],
        "debt": [
            (
                "source_current_mapping_telemetry",
                "telemetry_debt",
                "mapping must be source-backed, not asserted",
            ),
            (
                "independent_substrate_replay",
                "replay_debt",
                "transfer must replay under structurally distinct fixture",
            ),
            (
                "route_conditioned_transfer_selection",
                "policy_debt",
                "transfer that uses route-conditioned selection inherits AP4 gap",
            ),
        ],
        "additional_blocked": ["same_label_different_basin", "identity_acceptance"],
        "ap_gap_dependencies": [],
        "conditional_gap_dependencies": [
            {
                "ap_level": "AP4",
                "source": "N19/N14",
                "condition": "route-conditioned selection is part of transfer",
                "status": "conditional_local_gap_dependency",
            }
        ],
    },
    {
        "primitive_id": "generative_extractive_persistence",
        "primitive_name": "Generative Vs Extractive Persistence",
        "roadmap_target": "N28",
        "expected_first_positive_experiment": "N28",
        "diagnostic_source_titles": [
            "Agency After Choice",
            "N20-N29 LGRC Becoming-Agency Ecology Roadmap",
        ],
        "source_inventory_row_ids": [
            "n20_i1_row_01_n19_implementation_boundary",
            "n20_i1_row_02_n20_n29_roadmap",
            "n20_i1_row_08_agency_after_choice_vocabulary",
            "n20_i1_row_11_agentic_ecology_future_context",
        ],
        "substrate": [
            ("focal_basin_stability_trace", "focal basin remains stable"),
            ("neighbor_basin_distinguishability_trace", "neighbor or sub-basin distinguishability"),
            ("neighbor_support_floor_trace", "neighbor support floor"),
            ("extraction_cost_trace", "cost imposed on surrounding basin-forming capacity"),
        ],
        "producer": [
            ("generativity_label", "producer labels generative outcome"),
            ("neighbor_attribution_policy", "producer attributes neighbor effect to focal basin"),
            ("medium_segmentation_policy", "producer declares shared-medium segmentation"),
        ],
        "debt": [
            (
                "source_current_neighbor_basin_birth_telemetry",
                "telemetry_debt",
                "neighbor basin-forming capacity must be source-current",
            ),
            (
                "medium_debt_deferred_to_n28_n29",
                "source_currentness_debt",
                "shared medium remains deferred context until N28/N29",
            ),
            (
                "environment_capacity_budget_replay",
                "budget_debt",
                "environment-side capacity must replay under bounded budget",
            ),
        ],
        "additional_blocked": ["native_colony_agency", "organism_life"],
        "ap_gap_dependencies": [],
        "conditional_gap_dependencies": [],
    },
]

PRIMITIVE_SPECIFIC_CONSUMPTION_INPUTS = {
    "withdrawal_resistance": [
        "withdrawal_condition",
        "support_scaffold_declaration",
        "support_floor",
        "coherence_floor",
        "same_basin_continuation_rule",
        "hidden_producer_support_control",
        "proxy_only_success_control",
    ],
    "naturalization_depth": [
        "withdrawal_condition",
        "support_scaffold_declaration",
        "support_floor",
        "coherence_floor",
        "same_basin_continuation_rule",
        "hidden_producer_support_control",
        "proxy_only_success_control",
    ],
    "susceptibility_update": [
        "susceptibility_fields",
        "replay_requirement",
        "durable_geometry_modification_controls",
        "AP4_gap_dependency_if_route_conditioned",
    ],
    "live_continuation_collapse": [
        "live_continuation_set",
        "fake_alternative_controls",
        "producer_preference_injection_blockers",
        "AP4_gap_dependency",
    ],
    "surplus_supported_optionality": [
        "surplus_support_condition",
        "optional_continuation_space",
        "floor_crossing_controls",
        "hidden_budget_relief_control",
    ],
    "spark_sub_basin_new_basin_formation": [
        "basin_signature",
        "sub_basin_distinguishability_rule",
        "new_basin_replay_requirement",
        "hidden_producer_insertion_control",
    ],
    "proxy_divergence_proxy_collapse": [
        "proxy_metric_definition",
        "continuation_function_descriptor",
        "proxy_divergence_condition",
        "proxy_collapse_condition",
        "AP5_gap_dependency",
    ],
    "configuration_substrate_transfer": [
        "basin_signature",
        "transfer_mapping_declaration",
        "reconstructed_support_ledger",
        "producer_residue_ledger",
    ],
    "generative_extractive_persistence": [
        "generative_persistence_fields",
        "extractive_persistence_fields",
        "environment_basin_forming_capacity_fields",
        "medium_debt_placeholder",
    ],
}


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
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"{path.name} must contain a JSON object")
    return data


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def unsafe_claim_flags(schema: dict[str, Any]) -> dict[str, bool]:
    return {flag: False for flag in schema["enums"]["unsafe_claim_flags"]}


def variable_record(
    primitive_id: str,
    short_name: str,
    classification: str,
    description: str,
    *,
    debt_type: str | None = None,
    producer_surface: str = "not_applicable",
    source_current_visibility: str,
    claim_boundary: str,
    future_action_hint: str = "not_applicable",
    owning_later_experiment: str = "not_applicable",
) -> dict[str, Any]:
    return {
        "variable_id": f"{primitive_id}.{short_name}",
        "short_name": short_name,
        "classification": classification,
        "description": description,
        "source_current_visibility": source_current_visibility,
        "producer_surface": producer_surface,
        "naturalization_debt_type": debt_type,
        "claim_boundary": claim_boundary,
        "future_action_hint": future_action_hint,
        "owning_later_experiment": owning_later_experiment,
    }


def classification_records(definition: dict[str, Any]) -> list[dict[str, Any]]:
    primitive_id = definition["primitive_id"]
    owning_later_experiment = definition["expected_first_positive_experiment"]
    records: list[dict[str, Any]] = []
    for short_name, description in definition["substrate"]:
        records.append(
            variable_record(
                primitive_id,
                short_name,
                "substrate_carried",
                description,
                source_current_visibility=(
                    "source-visible LGRC geometry or committed artifact replay state"
                ),
                claim_boundary="substrate-carried field only; not primitive evidence in N20",
            )
        )
    for short_name, description in definition["producer"]:
        records.append(
            variable_record(
                primitive_id,
                short_name,
                "producer_mediated",
                description,
                producer_surface="explicit_N21_N28_producer_surface_required",
                source_current_visibility=(
                    "visible as producer residue, not as substrate-carried geometry"
                ),
                claim_boundary=(
                    "producer-mediated success cannot be treated as native support"
                ),
            )
        )
    for short_name, debt_type, description in definition["debt"]:
        records.append(
            variable_record(
                primitive_id,
                short_name,
                "naturalization_debt",
                description,
                debt_type=debt_type,
                producer_surface="future_source_backed_naturalization_surface_required",
                source_current_visibility="required but not source-current in the required way",
                claim_boundary=(
                    "naturalization debt must be resolved by source-backed result before "
                    "conversion to substrate_carried"
                ),
                future_action_hint=(
                    f"{owning_later_experiment} must record a source-backed "
                    "naturalization result that makes this variable replay-visible, "
                    "source-current, and no longer producer-mediated before it can "
                    "be converted to substrate_carried."
                ),
                owning_later_experiment=owning_later_experiment,
            )
        )
    blocked_labels = sorted(set(COMMON_BLOCKED_RELABELS + definition["additional_blocked"]))
    for label in blocked_labels:
        records.append(
            variable_record(
                primitive_id,
                f"blocked.{label}",
                "blocked_relabel",
                f"{label} is a blocked semantic or claim-inflating relabel",
                source_current_visibility="not an implementation variable",
                claim_boundary="must fail closed; cannot be producer-mediated evidence",
            )
        )
    return records


def bucket(records: list[dict[str, Any]], classification: str) -> list[str]:
    return [
        record["variable_id"]
        for record in records
        if record["classification"] == classification
    ]


def contract_placeholders(primitive_id: str) -> dict[str, Any]:
    return {
        "continuation_function_descriptor": {
            "descriptor_id": f"pending_n20_i4_{primitive_id}_continuation_function",
            "status": "deferred_to_iteration_4",
            "not_evidence": True,
        },
        "native_function_descriptor_alias": {
            "alias_for": "continuation_function_descriptor",
            "status": "deferred_to_iteration_4",
            "semantic_function_claim_allowed": False,
        },
        "proxy_metric_definition": {
            "proxy_id": f"pending_n20_i4_{primitive_id}_proxy_metric",
            "status": "deferred_to_iteration_4",
            "proxy_only_success_allowed": False,
        },
        "support_scaffold_declaration": {
            "support_id": f"pending_n20_i4_{primitive_id}_support_scaffold",
            "status": "deferred_to_iteration_4",
            "hidden_support_allowed": False,
        },
        "same_basin_continuation_rule": {
            "rule_id": f"pending_n20_i5_{primitive_id}_same_basin_rule",
            "status": "deferred_to_iteration_5",
            "label_only_continuation_allowed": False,
        },
        "minimum_controls": {
            "status": "deferred_to_iteration_5",
            "required_control_templates": [
                "label_only_success_control",
                "proxy_only_success_control",
                "hidden_producer_support_control",
                "post_hoc_trace_construction_control",
                "semantic_relabel_control",
                "native_support_relabel_control",
                "phase8_relabel_control",
            ],
        },
    }


def source_role_dependencies(row_ids: list[str]) -> list[dict[str, str]]:
    role_map = {
        "n20_i1_row_01_n19_implementation_boundary": "implementation_boundary_source",
        "n20_i1_row_02_n20_n29_roadmap": "roadmap_source",
        "n20_i1_row_04_interrogation_of_becoming_method": "method_source",
        "n20_i1_row_05_naturalization_of_becoming_method": "method_source",
        "n20_i1_row_07_agency_of_becoming_diagnostics": "diagnostic_vocabulary_source",
        "n20_i1_row_08_agency_after_choice_vocabulary": "diagnostic_vocabulary_source",
        "n20_i1_row_09_structural_abundance_boundary": "diagnostic_vocabulary_source",
        "n20_i1_row_11_agentic_ecology_future_context": "future_application_context",
    }
    return [
        {
            "source_inventory_row_id": row_id,
            "source_role": role_map[row_id],
            "consumption_status": "vocabulary_method_boundary_or_context_only_not_evidence",
        }
        for row_id in row_ids
    ]


def build_rows(schema: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, definition in enumerate(PRIMITIVE_DEFINITIONS, start=1):
        primitive_id = definition["primitive_id"]
        records = classification_records(definition)
        placeholders = contract_placeholders(primitive_id)
        row = {
            "row_id": f"n20_i3_row_{index:02d}_{primitive_id}",
            "primitive_id": primitive_id,
            "primitive_name": definition["primitive_name"],
            "roadmap_target": definition["roadmap_target"],
            "diagnostic_source_titles": definition["diagnostic_source_titles"],
            "source_inventory_row_ids": definition["source_inventory_row_ids"],
            "source_role_dependencies": source_role_dependencies(
                definition["source_inventory_row_ids"]
            ),
            "LGRC_visible_fields": bucket(records, "substrate_carried"),
            "producer_mediated_fields": bucket(records, "producer_mediated"),
            "naturalization_debt_fields": bucket(records, "naturalization_debt"),
            "blocked_relabel_fields": bucket(records, "blocked_relabel"),
            "variable_classification_records": records,
            "producer_residue_classification": {
                "status": "complete_for_iteration3_ledger_only",
                "exactly_one_classification_per_variable": True,
                "producer_mediated_success_native_support_rule": (
                    "producer_mediated and naturalization_debt variables cannot be "
                    "treated as substrate_carried evidence without a source-backed "
                    "naturalization result"
                ),
            },
            **placeholders,
            "contract_status": "incomplete_missing_continuation_function",
            "contract_complete_allowed": False,
            "missing_contract_objects": [
                "continuation_function_descriptor",
                "proxy_metric_definition",
                "support_scaffold_declaration",
                "same_basin_continuation_rule",
                "minimum_controls",
            ],
            "row_decision": "supported",
            "ledger_row_supported_as": "producer_residue_and_naturalization_debt_accounting",
            "primitive_supported": False,
            "primitive_evidence_opened": False,
            "ap_gap_dependencies": definition["ap_gap_dependencies"],
            "conditional_gap_dependencies": definition["conditional_gap_dependencies"],
            "expected_first_positive_experiment": definition[
                "expected_first_positive_experiment"
            ],
            "primitive_specific_consumption_inputs": (
                PRIMITIVE_SPECIFIC_CONSUMPTION_INPUTS[primitive_id]
            ),
            "must_consume_from_N20": [
                "continuation_function_descriptor",
                "proxy_metric_definition",
                "support_scaffold_declaration",
                "same_basin_continuation_rule",
                "producer_residue_ledger",
                "naturalization_debt_ledger",
                "minimum_controls",
                "claim_ceiling",
            ],
            "downstream_consumption_status": "not_consumable_until_contract_status_complete",
            "downstream_immutability_rule": (
                "N21-N28 may not redefine basin signature, continuation condition, "
                "proxy-only success blocker, or producer-residue classification in "
                "order to pass."
            ),
            "claim_ceiling": (
                "producer-residue ledger row only; no primitive evidence, agency, "
                "Phase 8, native support, sentience, or ant-ecology implementation"
            ),
            "unsafe_claim_flags": unsafe_claim_flags(schema),
            "artifact_invariants": INVARIANTS,
            "source_consumption_rules": {
                "diagnostic_vocabulary_can_define_fields": True,
                "diagnostic_vocabulary_can_satisfy_evidence_gates": False,
                "N12_N18_status": "historical_prerequisite_context_only",
                "N19_status": "current_implementation_classification_boundary",
            },
        }
        rows.append(row)
    return rows


def no_absolute_paths(data: Any) -> bool:
    return not absolute_path_strings(data)


def absolute_path_strings(data: Any) -> list[str]:
    found: list[str] = []
    if isinstance(data, str):
        if data.startswith("/") or data.startswith("file://"):
            found.append(data)
        elif len(data) >= 3 and data[1] == ":" and data[2] in {"\\", "/"}:
            found.append(data)
        return found
    if isinstance(data, dict):
        for value in data.values():
            found.extend(absolute_path_strings(value))
    elif isinstance(data, list):
        for value in data:
            found.extend(absolute_path_strings(value))
    return found


def source_schema_reference(schema: dict[str, Any]) -> dict[str, Any]:
    return {
        "path": rel(SCHEMA),
        "sha256": sha256_file(SCHEMA),
        "output_digest": schema["output_digest"],
        "status": schema["status"],
        "acceptance_state": schema["acceptance_state"],
    }


def classification_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for row in rows:
        for record in row["variable_classification_records"]:
            counts[record["classification"]] += 1
    return dict(sorted(counts.items()))


def row_variables_partitioned(row: dict[str, Any]) -> bool:
    buckets = [
        row["LGRC_visible_fields"],
        row["producer_mediated_fields"],
        row["naturalization_debt_fields"],
        row["blocked_relabel_fields"],
    ]
    bucket_variables = [variable for bucket_values in buckets for variable in bucket_values]
    record_variables = [
        record["variable_id"] for record in row["variable_classification_records"]
    ]
    return (
        len(bucket_variables) == len(set(bucket_variables))
        and sorted(bucket_variables) == sorted(record_variables)
        and len(record_variables) == len(set(record_variables))
    )


def debt_fields_have_subtypes(row: dict[str, Any], allowed_debt_types: set[str]) -> bool:
    for record in row["variable_classification_records"]:
        if record["classification"] == "naturalization_debt":
            if record["naturalization_debt_type"] not in allowed_debt_types:
                return False
        elif record["naturalization_debt_type"] is not None:
            return False
    return True


def blocked_relabels_not_producer_variables(row: dict[str, Any]) -> bool:
    blocked_short_names = {
        record["short_name"].removeprefix("blocked.")
        for record in row["variable_classification_records"]
        if record["classification"] == "blocked_relabel"
    }
    producer_short_names = {
        record["short_name"]
        for record in row["variable_classification_records"]
        if record["classification"] == "producer_mediated"
    }
    common_present = set(COMMON_BLOCKED_RELABELS).issubset(blocked_short_names)
    return common_present and not (set(COMMON_BLOCKED_RELABELS) & producer_short_names)


def naturalization_debt_is_actionable(row: dict[str, Any]) -> bool:
    for record in row["variable_classification_records"]:
        if record["classification"] != "naturalization_debt":
            continue
        if record["owning_later_experiment"] != row["expected_first_positive_experiment"]:
            return False
        if "source-backed naturalization result" not in record["future_action_hint"]:
            return False
        if "converted to substrate_carried" not in record["future_action_hint"]:
            return False
    return True


def primitive_specific_core_fields(rows: list[dict[str, Any]]) -> bool:
    core_sets: list[tuple[str, ...]] = []
    for row in rows:
        core_sets.append(
            tuple(
                record["short_name"]
                for record in row["variable_classification_records"]
                if record["classification"] != "blocked_relabel"
            )
        )
    return len(core_sets) == len(set(core_sets))


def local_gap_dependency_check(rows: list[dict[str, Any]]) -> dict[str, bool]:
    by_primitive = {row["primitive_id"]: row for row in rows}
    return {
        "susceptibility_update_has_ap4": any(
            gap["ap_level"] == "AP4"
            for gap in by_primitive["susceptibility_update"]["ap_gap_dependencies"]
        ),
        "susceptibility_update_has_conditional_ap5": any(
            gap["ap_level"] == "AP5"
            for gap in by_primitive["susceptibility_update"][
                "conditional_gap_dependencies"
            ]
        ),
        "live_continuation_collapse_has_ap4": any(
            gap["ap_level"] == "AP4"
            for gap in by_primitive["live_continuation_collapse"]["ap_gap_dependencies"]
        ),
        "live_continuation_collapse_has_conditional_ap5": any(
            gap["ap_level"] == "AP5"
            for gap in by_primitive["live_continuation_collapse"][
                "conditional_gap_dependencies"
            ]
        ),
        "proxy_divergence_proxy_collapse_has_ap5": any(
            gap["ap_level"] == "AP5"
            for gap in by_primitive["proxy_divergence_proxy_collapse"][
                "ap_gap_dependencies"
            ]
        ),
        "configuration_substrate_transfer_has_conditional_ap4": any(
            gap["ap_level"] == "AP4"
            for gap in by_primitive["configuration_substrate_transfer"][
                "conditional_gap_dependencies"
            ]
        ),
    }


def build_checks(artifact: dict[str, Any], schema: dict[str, Any]) -> list[dict[str, Any]]:
    rows = artifact["producer_residue_rows"]
    allowed_primitive_ids = schema["enums"]["expected_primitive_ids"]
    allowed_classifications = set(schema["enums"]["variable_classification"])
    allowed_debt_types = set(schema["enums"]["naturalization_debt_type"])
    local_gap_checks = local_gap_dependency_check(rows)
    checks = [
        {
            "check_id": "source_schema_passed",
            "passed": schema["status"] == "passed" and not schema["failed_checks"],
            "detail": schema["acceptance_state"],
        },
        {
            "check_id": "all_expected_primitives_have_one_row",
            "passed": sorted(row["primitive_id"] for row in rows)
            == sorted(allowed_primitive_ids)
            and len(rows) == len(allowed_primitive_ids),
            "detail": [row["primitive_id"] for row in rows],
        },
        {
            "check_id": "all_variables_exactly_one_classification",
            "passed": all(row_variables_partitioned(row) for row in rows)
            and all(
                record["classification"] in allowed_classifications
                for row in rows
                for record in row["variable_classification_records"]
            ),
            "detail": artifact["classification_counts"],
        },
        {
            "check_id": "naturalization_debt_fields_have_debt_subtypes",
            "passed": all(debt_fields_have_subtypes(row, allowed_debt_types) for row in rows),
            "detail": sorted(allowed_debt_types),
        },
        {
            "check_id": "blocked_relabels_are_not_producer_variables",
            "passed": all(blocked_relabels_not_producer_variables(row) for row in rows),
            "detail": COMMON_BLOCKED_RELABELS,
        },
        {
            "check_id": "full_unsafe_claim_family_blocked_as_variables",
            "passed": all(
                set(COMMON_BLOCKED_RELABELS).issubset(
                    {
                        record["short_name"].removeprefix("blocked.")
                        for record in row["variable_classification_records"]
                        if record["classification"] == "blocked_relabel"
                    }
                )
                for row in rows
            ),
            "detail": COMMON_BLOCKED_RELABELS,
        },
        {
            "check_id": "primitive_specific_field_sets_not_generic_template",
            "passed": primitive_specific_core_fields(rows),
            "detail": "substrate, producer, and debt field short-name sets differ per primitive",
        },
        {
            "check_id": "naturalization_debt_fields_are_actionable",
            "passed": all(naturalization_debt_is_actionable(row) for row in rows),
            "detail": "each naturalization debt record names owner and source-backed conversion condition",
        },
        {
            "check_id": "ap4_ap5_gap_dependencies_are_row_local",
            "passed": all(local_gap_checks.values()),
            "detail": local_gap_checks,
        },
        {
            "check_id": "contract_rows_not_marked_complete_in_i3",
            "passed": all(row["contract_status"] != "complete" for row in rows)
            and all(row["contract_complete_allowed"] is False for row in rows)
            and all(row["downstream_consumption_status"] != "consumable" for row in rows),
            "detail": {
                row["primitive_id"]: row["contract_status"] for row in rows
            },
        },
        {
            "check_id": "producer_mediated_success_cannot_be_native_support",
            "passed": all(
                "cannot be treated as substrate_carried evidence"
                in row["producer_residue_classification"][
                    "producer_mediated_success_native_support_rule"
                ]
                for row in rows
            ),
            "detail": "source-backed naturalization result required before conversion",
        },
        {
            "check_id": "n21_n28_consumption_rules_present",
            "passed": all(row["must_consume_from_N20"] for row in rows)
            and all(row["primitive_specific_consumption_inputs"] for row in rows)
            and all(
                row["expected_first_positive_experiment"]
                in {"N21", "N22", "N23", "N24", "N25", "N26", "N27", "N28"}
                for row in rows
            ),
            "detail": {
                row["primitive_id"]: row["expected_first_positive_experiment"]
                for row in rows
            },
        },
        {
            "check_id": "primitive_specific_n21_n28_consumption_map_present",
            "passed": all(
                row["primitive_specific_consumption_inputs"]
                == PRIMITIVE_SPECIFIC_CONSUMPTION_INPUTS[row["primitive_id"]]
                for row in rows
            ),
            "detail": PRIMITIVE_SPECIFIC_CONSUMPTION_INPUTS,
        },
        {
            "check_id": "diagnostic_vocabulary_not_evidence",
            "passed": all(
                row["source_consumption_rules"][
                    "diagnostic_vocabulary_can_satisfy_evidence_gates"
                ]
                is False
                for row in rows
            ),
            "detail": "method and essay rows define vocabulary/contracts only",
        },
        {
            "check_id": "unsafe_claim_flags_false_per_row",
            "passed": all(
                all(value is False for value in row["unsafe_claim_flags"].values())
                for row in rows
            ),
            "detail": len(schema["enums"]["unsafe_claim_flags"]),
        },
        {
            "check_id": "no_primitive_evidence_opened",
            "passed": artifact["primitive_evidence_opened"] is False
            and all(row["primitive_supported"] is False for row in rows)
            and all(row["primitive_evidence_opened"] is False for row in rows),
            "detail": {
                "primitive_evidence_opened": artifact["primitive_evidence_opened"],
                "producer_residue_rows_classified": artifact[
                    "producer_residue_rows_classified"
                ],
            },
        },
        {
            "check_id": "artifact_invariants_preserved",
            "passed": artifact["artifact_invariants"] == INVARIANTS
            and all(row["artifact_invariants"] == INVARIANTS for row in rows),
            "detail": artifact["artifact_invariants"],
        },
        {
            "check_id": "no_absolute_paths",
            "passed": no_absolute_paths(artifact),
            "detail": "ledger paths are relative",
        },
    ]
    return checks


def render_report(artifact: dict[str, Any]) -> None:
    lines = [
        "# N20 Iteration 3 - Producer Residue And Naturalization Debt Ledger",
        "",
        "Status:",
        "",
        "```text",
        f"status = {artifact['status']}",
        f"acceptance_state = {artifact['acceptance_state']}",
        f"row_count = {artifact['row_count']}",
        f"variable_record_count = {artifact['variable_record_count']}",
        f"primitive_evidence_opened = {str(artifact['primitive_evidence_opened']).lower()}",
        f"producer_residue_rows_classified = {str(artifact['producer_residue_rows_classified']).lower()}",
        f"agency_claim_opened = {str(artifact['agency_claim_opened']).lower()}",
        f"phase8_opened = {str(artifact['phase8_opened']).lower()}",
        f"native_support_opened = {str(artifact['native_support_opened']).lower()}",
        "```",
        "",
        "Classification counts:",
        "",
        "```json",
        json.dumps(artifact["classification_counts"], indent=2, sort_keys=True),
        "```",
        "",
        "Interpretation:",
        "",
        "Iteration 3 supports the ledger rows as accounting records only. It does "
        "not support withdrawal resistance, naturalization depth, learning, "
        "choice, abundance, spark, proxy collapse, transfer, generative "
        "persistence, agency, Phase 8, native support, or sentience.",
        "",
        "Primitive rows:",
        "",
        "| Primitive | Target | Decision | Contract Status | Substrate | Producer | Debt | Blocked | AP gaps |",
        "| --- | --- | --- | --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in artifact["producer_residue_rows"]:
        gap_labels = [
            gap["ap_level"] for gap in row["ap_gap_dependencies"]
        ] + [
            f"{gap['ap_level']} conditional"
            for gap in row["conditional_gap_dependencies"]
        ]
        lines.append(
            "| "
            f"{row['primitive_id']} | "
            f"{row['expected_first_positive_experiment']} | "
            f"{row['row_decision']} | "
            f"{row['contract_status']} | "
            f"{len(row['LGRC_visible_fields'])} | "
            f"{len(row['producer_mediated_fields'])} | "
            f"{len(row['naturalization_debt_fields'])} | "
            f"{len(row['blocked_relabel_fields'])} | "
            f"{', '.join(gap_labels) if gap_labels else 'none'} |"
        )
    lines.extend(
        [
            "",
            "Downstream consumption rule:",
            "",
            "```text",
            artifact["downstream_consumption_rule"],
            "```",
            "",
            "Primitive-specific downstream consumption inputs:",
            "",
            "| Primitive | Specific Inputs |",
            "| --- | --- |",
        ]
    )
    for row in artifact["producer_residue_rows"]:
        lines.append(
            f"| {row['primitive_id']} | "
            f"{', '.join(row['primitive_specific_consumption_inputs'])} |"
        )
    lines.extend(
        [
            "",
            "AP4/AP5 local dependencies:",
            "",
            "```json",
            json.dumps(
                artifact["ap4_ap5_local_dependency_summary"],
                indent=2,
                sort_keys=True,
            ),
            "```",
            "",
            "Iteration 4 carry-forward guards:",
            "",
            "```json",
            json.dumps(
                artifact["iteration4_carry_forward_requirements"],
                indent=2,
                sort_keys=True,
            ),
            "```",
            "",
            "Checks:",
            "",
            "| Check | Passed |",
            "| --- | --- |",
        ]
    )
    for check in artifact["checks"]:
        lines.append(f"| {check['check_id']} | {str(check['passed']).lower()} |")
    lines.extend(
        [
            "",
            "Claim boundary:",
            "",
            "```text",
            artifact["claim_boundary"],
            "```",
            "",
        ]
    )
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    schema = load_json(SCHEMA)
    rows = build_rows(schema)
    artifact: dict[str, Any] = {
        "artifact_id": "n20_producer_residue_ledger",
        "schema_version": "n20_producer_residue_ledger_v1",
        "experiment": "2026-06-N20-lgrc-becoming-primitive-producer-translation-contract",
        "iteration": 3,
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "purpose": (
            "Classify producer residue and naturalization debt for each N20 "
            "becoming primitive without testing or supporting primitive evidence."
        ),
        "source_schema": source_schema_reference(schema),
        "artifact_invariants": INVARIANTS,
        "producer_residue_rows_classified": True,
        "naturalization_debt_ledger_defined": True,
        "primitive_rows_evidence_classified": False,
        "primitive_evidence_opened": False,
        "agency_claim_opened": False,
        "phase8_opened": False,
        "native_support_opened": False,
        "sentience_opened": False,
        "ant_ecology_spec_opened": False,
        "producer_residue_rows": rows,
        "row_count": len(rows),
        "variable_record_count": sum(
            len(row["variable_classification_records"]) for row in rows
        ),
        "classification_counts": classification_counts(rows),
        "ap4_ap5_local_dependency_summary": local_gap_dependency_check(rows),
        "downstream_consumption_rule": (
            "N21-N28 may consume I3 only as producer-residue and naturalization-"
            "debt ledger input. A primitive row cannot be consumable as a "
            "complete contract until N20 Iterations 4 and 5 define the "
            "continuation, proxy, support/scaffold, same-basin, and control "
            "contracts."
        ),
        "producer_mediated_conversion_rule": (
            "producer_mediated and naturalization_debt variables may convert to "
            "substrate_carried only through a later source-backed naturalization "
            "result; blocked_relabel variables never convert."
        ),
        "iteration4_carry_forward_requirements": {
            "ap4_ap5_dependencies_must_be_carried_forward": True,
            "i4_must_not_mark_all_rows_complete": True,
            "suggested_post_i4_status": (
                "incomplete_missing_same_basin_rule or incomplete_missing_controls "
                "unless I4 also supplies the I5 same-basin and control criteria"
            ),
            "producer_mediated_success_native_support_allowed": False,
            "blocked_relabels_may_be_proxy_metrics": False,
            "blocked_proxy_metric_examples": [
                "semantic_goal_score",
                "choice_score",
                "agency_score",
                "sentience_score",
                "identity_score",
            ],
        },
        "review_double_check_summary": {
            "supported_means_ledger_row_supported_not_primitive_supported": True,
            "core_variable_lists_are_primitive_specific": primitive_specific_core_fields(
                rows
            ),
            "full_unsafe_claim_family_blocked_per_row": True,
            "naturalization_debt_records_are_actionable": True,
            "contract_rows_complete_after_i3": False,
        },
        "claim_boundary": (
            "N20 Iteration 3 supports producer-residue and naturalization-debt "
            "accounting only. It does not test, support, or classify primitive "
            "evidence and does not open agency, Phase 8, native support, "
            "sentience, ant ecology specifications, or AP4/AP5 gap resolution."
        ),
        "output_digest": "pending",
    }
    checks = build_checks(artifact, schema)
    failed_checks = [check["check_id"] for check in checks if not check["passed"]]
    artifact["checks"] = checks
    artifact["failed_checks"] = failed_checks
    artifact["status"] = "passed" if not failed_checks else "failed"
    artifact["acceptance_state"] = (
        "accepted_producer_residue_naturalization_debt_ledger_no_primitive_evidence"
        if not failed_checks
        else "failed_producer_residue_naturalization_debt_ledger"
    )
    digest_input = dict(artifact)
    digest_input.pop("output_digest", None)
    artifact["output_digest"] = digest_value(digest_input)
    OUTPUT.write_text(canonical_json(artifact), encoding="utf-8")
    render_report(artifact)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Build N29 Iteration 1 ecology demand extraction."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-29T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
ECOLOGY_ROOT = ROOT.parent / "reflexive-coherence-agentic-ecology"
EXPERIMENT = ROOT / "experiments" / "2026-06-N29-lgrc-agentic-ecology-convergence-bridge"
OUTPUT = EXPERIMENT / "outputs" / "n29_ecology_demand_extraction_i1.json"
REPORT = EXPERIMENT / "reports" / "n29_ecology_demand_extraction_i1.md"
SCRIPT_RELATIVE_PATH = (
    "experiments/2026-06-N29-lgrc-agentic-ecology-convergence-bridge/scripts/"
    "build_n29_ecology_demand_extraction_i1.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"

TARGET_SOURCES: list[dict[str, Any]] = [
    {
        "source_id": "rc_agentic_ecology_readme",
        "source_path": "reflexive-coherence-agentic-ecology/README.md",
        "local_relative_path": "README.md",
        "source_role": "target_orientation_and_claim_boundary_source",
        "may_consume_as": [
            "ecology_target_vocabulary",
            "translation_rule_source",
            "producer_residue_and_medium_debt_boundary",
            "claim_boundary_source",
        ],
        "must_not_consume_as": [
            "implementation_evidence",
            "native_ecology_evidence",
            "ant_agency_evidence",
            "shared_medium_coordination_evidence",
        ],
    },
    {
        "source_id": "from_state_to_becoming",
        "source_path": (
            "reflexive-coherence-agentic-ecology/papers/"
            "2026-06-FromStateToBecoming.md"
        ),
        "local_relative_path": "papers/2026-06-FromStateToBecoming.md",
        "source_role": "state_to_geometry_transition_method_source",
        "may_consume_as": [
            "demand_vocabulary_context",
            "producer_residue_discipline_context",
            "claim_boundary_context",
        ],
        "must_not_consume_as": [
            "implementation_evidence",
            "native_agency_evidence",
            "prototype_proof",
        ],
    },
    {
        "source_id": "rc_agentic_ecology_spec",
        "source_path": (
            "reflexive-coherence-agentic-ecology/papers/"
            "2026-06-RC-AgenticEcology.md"
        ),
        "local_relative_path": "papers/2026-06-RC-AgenticEcology.md",
        "source_role": "rc_ant_worked_domain_target_source",
        "may_consume_as": [
            "rc_ant_component_demand_source",
            "hierarchical_basin_target_source",
            "producer_residue_boundary",
        ],
        "must_not_consume_as": [
            "native_ant_colony_evidence",
            "native_agency_evidence",
            "biological_life_evidence",
            "implementation_evidence",
        ],
    },
    {
        "source_id": "the_shared_medium",
        "source_path": (
            "reflexive-coherence-agentic-ecology/papers/"
            "2026-06-TheSharedMedium.md"
        ),
        "local_relative_path": "papers/2026-06-TheSharedMedium.md",
        "source_role": "shared_medium_transition_method_source",
        "may_consume_as": [
            "shared_medium_demand_vocabulary",
            "medium_debt_boundary",
            "co_response_and_resonance_context",
        ],
        "must_not_consume_as": [
            "native_shared_medium_coordination_evidence",
            "implementation_evidence",
            "ant_communication_evidence",
        ],
    },
    {
        "source_id": "shared_medium_coordination_spec",
        "source_path": (
            "reflexive-coherence-agentic-ecology/papers/"
            "2026-06-SharedMediumCoordination-EngineeringSpec.md"
        ),
        "local_relative_path": "papers/2026-06-SharedMediumCoordination-EngineeringSpec.md",
        "source_role": "shared_medium_engineering_vocabulary_source",
        "may_consume_as": [
            "medium_surface_schema_source",
            "perturbation_trace_pressure_susceptibility_source",
            "medium_debt_schema_source",
            "control_vocabulary_source",
        ],
        "must_not_consume_as": [
            "runnable_api_evidence",
            "native_shared_medium_coordination_evidence",
            "implementation_evidence",
        ],
    },
]

GENERAL_DEMAND_IDS = [
    "parent_basin",
    "shared_medium",
    "medium_surface",
    "perturbation",
    "trace",
    "pressure",
    "susceptibility",
    "co_response",
    "resonance",
    "parent_basin_modulation",
    "message_scaffold",
    "medium_debt",
    "producer_residue",
    "naturalization_condition",
]

RC_ANT_DEMAND_IDS = [
    "colony_parent_basin",
    "mobile_boundary_expression",
    "nest_home_basin",
    "food_resource_coupling",
    "route_support_trace",
    "foodward_affordance_surface",
    "homeward_affordance_surface",
    "cargo_shaped_susceptibility",
    "reserve_hunger_pressure",
    "alarm_threat_pressure",
    "nursery_demand",
    "waste_isolation",
    "construction_tension",
    "crowding_congestion_cost",
    "role_susceptibility_division_of_labor",
    "surplus_supported_split_reproduction",
]

UNSAFE_CLAIM_FLAGS = {
    "native_ant_agency_opened": False,
    "native_colony_agency_opened": False,
    "biological_agency_opened": False,
    "organism_life_opened": False,
    "consciousness_opened": False,
    "sentience_opened": False,
    "semantic_goal_claim_opened": False,
    "semantic_cooperation_claim_opened": False,
    "native_shared_medium_coordination_opened": False,
    "fully_native_ecology_opened": False,
    "phase8_completion_opened": False,
    "unrestricted_autonomy_opened": False,
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


def no_absolute_paths(data: Any) -> bool:
    text = json.dumps(data, sort_keys=True, ensure_ascii=True)
    forbidden = ("/" + "home" + "/", "Documents" + "/" + "RC-github")
    return all(pattern not in text for pattern in forbidden)


def source_record(source: dict[str, Any]) -> dict[str, Any]:
    path = ECOLOGY_ROOT / source["local_relative_path"]
    record = {key: value for key, value in source.items() if key != "local_relative_path"}
    record.update(
        {
            "exists": path.exists(),
            "sha256": sha256_file(path) if path.exists() else "missing",
            "digest_policy": "sha256_of_external_target_source",
            "source_scope": "conceptual_specification_source",
            "implementation_evidence_opened": False,
            "positive_ecology_evidence_opened": False,
            "claim_ceiling": "target_requirement_and_vocabulary_source_only",
        }
    )
    return record


def demand_row(
    *,
    demand_id: str,
    component: str,
    family: str,
    source_refs: list[str],
    required_dynamics: list[str],
    state_surfaces: list[str],
    trace_surfaces: list[str],
    controls: list[str],
    producer_residue_risk: str,
    medium_debt_risk: str,
    blocked_relabels: list[str],
    first_probe_relevance: str,
) -> dict[str, Any]:
    return {
        "demand_id": demand_id,
        "ecology_component": component,
        "demand_family": family,
        "source_spec_reference": source_refs,
        "source_role": "target_requirement_not_evidence",
        "required_dynamics": required_dynamics,
        "required_state_surfaces": state_surfaces,
        "required_trace_surfaces": trace_surfaces,
        "required_controls": controls,
        "producer_residue_risk": producer_residue_risk,
        "medium_debt_risk": medium_debt_risk,
        "blocked_relabels": blocked_relabels,
        "first_probe_relevance": first_probe_relevance,
        "implementation_evidence_opened": False,
        "n05_n28_capability_coverage_claimed": False,
        "prototype_row_opened": False,
        "positive_ecology_evidence_opened": False,
        "claim_ceiling": "ecology_target_requirement_only_no_implementation_evidence",
    }


def general_demand_rows() -> list[dict[str, Any]]:
    readme_core = "reflexive-coherence-agentic-ecology/README.md#core-translation"
    shared_spec = (
        "reflexive-coherence-agentic-ecology/papers/"
        "2026-06-SharedMediumCoordination-EngineeringSpec.md#core-definitions"
    )
    shared_essay = (
        "reflexive-coherence-agentic-ecology/papers/"
        "2026-06-TheSharedMedium.md#shared-medium"
    )
    becoming = (
        "reflexive-coherence-agentic-ecology/papers/"
        "2026-06-FromStateToBecoming.md#rc-inversion"
    )
    return [
        demand_row(
            demand_id="general_parent_basin",
            component="parent_basin",
            family="general",
            source_refs=[shared_spec, shared_essay],
            required_dynamics=[
                "higher_order_context_modulates_local_continuation",
                "local_elements_remain_differentiated_inside_parent_geometry",
            ],
            state_surfaces=["parent_identity_boundary", "reserve_condition", "local_subbasin_state"],
            trace_surfaces=["event_history", "parent_pressure_trace"],
            controls=["parent_label_only_relabel_control", "central_controller_as_parent_basin_control"],
            producer_residue_risk="parent pressure may be maintained by explicit producer state",
            medium_debt_risk="parent modulation may be simulated as direct broadcast",
            blocked_relabels=["native_colony_agency", "central_manager_as_parent_basin"],
            first_probe_relevance="required for any colony-level or shared-medium probe",
        ),
        demand_row(
            demand_id="general_shared_medium",
            component="shared_medium",
            family="general",
            source_refs=[readme_core, shared_spec],
            required_dynamics=[
                "multiple_local_geometries_respond_to_common_medium_condition",
                "relation_carried_by_medium_change_not_pairwise_message_only",
            ],
            state_surfaces=["support_distribution", "cost_surface", "reserve_condition"],
            trace_surfaces=["trace_field", "pressure_field", "signature_field"],
            controls=["direct_message_scaffold_control", "hidden_global_variable_control"],
            producer_residue_risk="medium may be maintained by producer-visible ledger",
            medium_debt_risk="message bus may stand in for shared medium",
            blocked_relabels=["native_shared_medium_coordination", "message_bus_as_medium"],
            first_probe_relevance="central surface for relation and coordination probes",
        ),
        demand_row(
            demand_id="general_medium_surface",
            component="medium_surface",
            family="general",
            source_refs=[shared_spec],
            required_dynamics=[
                "specific_medium_aspect_can_be_perturbed",
                "later_local_response_depends_on_surface_change",
            ],
            state_surfaces=["route_support_surface", "reserve_pressure_surface", "cost_surface"],
            trace_surfaces=["surface_update_trace", "surface_decay_trace"],
            controls=["surface_label_only_control", "unperturbed_surface_response_control"],
            producer_residue_risk="surface may be an annotation rather than substrate geometry",
            medium_debt_risk="surface may be represented as explicit message channel",
            blocked_relabels=["surface_annotation_as_native_medium", "visual_surface_as_evidence"],
            first_probe_relevance="needed before medium participation can be probed",
        ),
        demand_row(
            demand_id="general_perturbation",
            component="perturbation",
            family="general",
            source_refs=[shared_spec, shared_essay],
            required_dynamics=[
                "activity_changes_shared_medium",
                "change_has_auditable_cause_and_later_effect",
            ],
            state_surfaces=["changed_medium_state", "boundary_or_cost_change"],
            trace_surfaces=["perturbation_event_trace", "cause_attribution_trace"],
            controls=["post_hoc_perturbation_control", "independent_change_control"],
            producer_residue_risk="producer may inject perturbation after outcome inspection",
            medium_debt_risk="perturbation may be encoded as message payload",
            blocked_relabels=["message_payload_as_medium_change", "post_hoc_causality"],
            first_probe_relevance="required for any shared-medium cause/effect probe",
        ),
        demand_row(
            demand_id="general_trace",
            component="trace",
            family="general",
            source_refs=[readme_core, shared_spec, shared_essay],
            required_dynamics=[
                "prior_activity_leaves_persistent_medium_alteration",
                "later_affordance_or_cost_changes_due_to_trace",
            ],
            state_surfaces=["persistent_aftereffect_state", "route_cost_state"],
            trace_surfaces=["trace_deposition", "trace_decay", "trace_reentry"],
            controls=["trace_label_only_control", "stale_trace_control"],
            producer_residue_risk="trace may be kept in explicit memory table",
            medium_debt_risk="trace may be replaced by direct notification",
            blocked_relabels=["pheromone_label_as_native_trace", "memory_variable_as_trace"],
            first_probe_relevance="basis for route-support and aftereffect prototypes",
        ),
        demand_row(
            demand_id="general_pressure",
            component="pressure",
            family="general",
            source_refs=[readme_core, shared_spec],
            required_dynamics=[
                "medium_condition_changes_likelihood_or_cost_of_continuation",
                "pressure_can_bias_multiple_local_elements_without_command",
            ],
            state_surfaces=["reserve_deficit", "cost_gradient", "support_pressure"],
            trace_surfaces=["pressure_change_trace", "response_bias_trace"],
            controls=["broadcast_as_pressure_control", "pressure_label_only_control"],
            producer_residue_risk="pressure may be a scheduler priority variable",
            medium_debt_risk="pressure may be sent as a broadcast instruction",
            blocked_relabels=["semantic_goal_as_pressure", "central_command_as_pressure"],
            first_probe_relevance="basis for reserve/hunger and threat-pressure probes",
        ),
        demand_row(
            demand_id="general_susceptibility",
            component="susceptibility",
            family="general",
            source_refs=[shared_spec, shared_essay],
            required_dynamics=[
                "local_geometry_can_be_captured_by_medium_condition",
                "different_local_states_respond_differently_to_same_condition",
            ],
            state_surfaces=["local_basin_capture_state", "role_bias_state"],
            trace_surfaces=["susceptibility_update_trace", "capture_response_trace"],
            controls=["role_label_only_control", "hidden_assignment_control"],
            producer_residue_risk="susceptibility may be task assignment state",
            medium_debt_risk="susceptibility may be emulated by message subscription",
            blocked_relabels=["semantic_role_as_susceptibility", "assignment_as_native_capture"],
            first_probe_relevance="required for role and differentiated-response probes",
        ),
        demand_row(
            demand_id="general_co_response",
            component="co_response",
            family="general",
            source_refs=[readme_core, shared_spec, shared_essay],
            required_dynamics=[
                "multiple_elements_shift_due_to_same_medium_condition",
                "coordination_occurs_without_direct_pairwise_instruction",
            ],
            state_surfaces=["common_pressure_state", "local_response_state"],
            trace_surfaces=["co_response_event_trace", "shared_cause_trace"],
            controls=["hidden_coordinator_control", "message_passing_as_co_response_control"],
            producer_residue_risk="producer may coordinate elements directly",
            medium_debt_risk="co-response may be simulated by broadcast",
            blocked_relabels=["native_coordination_without_medium", "semantic_cooperation"],
            first_probe_relevance="needed for shared-medium coordination probes",
        ),
        demand_row(
            demand_id="general_resonance",
            component="resonance",
            family="general",
            source_refs=[shared_spec, shared_essay],
            required_dynamics=[
                "perturbation_integrates_in_compatible_geometry",
                "incompatible_geometry_rejects_or_dissipates_perturbation",
            ],
            state_surfaces=["compatibility_state", "integration_or_dissipation_state"],
            trace_surfaces=["resonance_response_trace", "failed_integration_trace"],
            controls=["compatibility_label_only_control", "same_response_for_incompatible_state_control"],
            producer_residue_risk="compatibility may be precomputed by producer",
            medium_debt_risk="resonance may be replaced by protocol agreement",
            blocked_relabels=["semantic_understanding", "symbolic_decoding_as_resonance"],
            first_probe_relevance="useful for distinguishing shared perturbation from arbitrary signal",
        ),
        demand_row(
            demand_id="general_parent_basin_modulation",
            component="parent_basin_modulation",
            family="general",
            source_refs=[readme_core, shared_spec, shared_essay],
            required_dynamics=[
                "parent_condition_changes_affordance_landscape",
                "local_susceptibilities_shift_without_individual_commands",
            ],
            state_surfaces=["parent_reserve_state", "parent_demand_state", "local_capture_state"],
            trace_surfaces=["modulation_event_trace", "local_shift_trace"],
            controls=["central_scheduler_as_modulation_control", "broadcast_as_modulation_control"],
            producer_residue_risk="parent modulation may be explicit scheduler policy",
            medium_debt_risk="modulation may be implemented as global broadcast",
            blocked_relabels=["colony_intention", "central_manager_as_parent_modulation"],
            first_probe_relevance="needed for colony-demand and reserve-pressure probes",
        ),
        demand_row(
            demand_id="general_message_scaffold",
            component="message_scaffold",
            family="general",
            source_refs=[readme_core, shared_spec, shared_essay],
            required_dynamics=[
                "explicit_message_is_allowed_only_as_scaffold",
                "message_target_rc_meaning_is_declared",
            ],
            state_surfaces=["message_state", "target_medium_surface"],
            trace_surfaces=["message_to_medium_mapping_trace"],
            controls=["message_as_native_medium_control", "undeclared_message_scaffold_control"],
            producer_residue_risk="message scaffold may become hidden producer state",
            medium_debt_risk="message scaffold is medium debt until naturalized",
            blocked_relabels=["direct_message_as_native_coordination", "protocol_as_shared_medium"],
            first_probe_relevance="needed when early ecology probes require explicit relation scaffolds",
        ),
        demand_row(
            demand_id="general_medium_debt",
            component="medium_debt",
            family="general",
            source_refs=[readme_core, shared_spec, shared_essay],
            required_dynamics=[
                "message_or_coordination_scaffold_is_recorded_as_debt",
                "debt_has_naturalization_condition",
            ],
            state_surfaces=["debt_ledger_state", "target_medium_surface"],
            trace_surfaces=["debt_resolution_trace"],
            controls=["debt_hidden_as_native_control", "missing_medium_debt_control"],
            producer_residue_risk="debt may be omitted from producer ledger",
            medium_debt_risk="this row is the explicit medium debt requirement",
            blocked_relabels=["scaffold_as_native_relation", "medium_debt_erased_by_success"],
            first_probe_relevance="required for all message-mediated ecology prototypes",
        ),
        demand_row(
            demand_id="general_producer_residue",
            component="producer_residue",
            family="general",
            source_refs=[readme_core, becoming, shared_spec],
            required_dynamics=[
                "explicit_producer_state_is_declared",
                "target_rc_meaning_and_naturalization_debt_are_recorded",
            ],
            state_surfaces=["producer_state_surface", "target_geometry_surface"],
            trace_surfaces=["producer_to_target_mapping_trace"],
            controls=["producer_state_as_native_control", "undeclared_producer_variable_control"],
            producer_residue_risk="this row tracks producer residue risk directly",
            medium_debt_risk="producer may also carry relation/message scaffolds",
            blocked_relabels=["producer_scaffold_as_native_behavior", "native_agency_by_producer"],
            first_probe_relevance="required for any ecology probe using scaffolding",
        ),
        demand_row(
            demand_id="general_naturalization_condition",
            component="naturalization_condition",
            family="general",
            source_refs=[readme_core, becoming],
            required_dynamics=[
                "scaffolded_behavior_has_declared_native_target",
                "withdrawal_or_substrate_carriage_condition_is_defined",
            ],
            state_surfaces=["substrate_carried_geometry", "scaffold_removed_state"],
            trace_surfaces=["naturalization_replay_trace", "scaffold_withdrawal_trace"],
            controls=["scaffold_not_removed_control", "label_only_naturalization_control"],
            producer_residue_risk="naturalization may be asserted without scaffold withdrawal",
            medium_debt_risk="message scaffold may be left unresolved",
            blocked_relabels=["partial_scaffold_as_native", "implementation_success_as_naturalization"],
            first_probe_relevance="defines when future ecology behavior can become native claim",
        ),
    ]


def rc_ant_demand_rows() -> list[dict[str, Any]]:
    rc_ant = (
        "reflexive-coherence-agentic-ecology/papers/"
        "2026-06-RC-AgenticEcology.md#rc-ant-colony"
    )
    shared = (
        "reflexive-coherence-agentic-ecology/papers/"
        "2026-06-SharedMediumCoordination-EngineeringSpec.md#ant-colony-examples"
    )
    return [
        demand_row(
            demand_id="rc_ant_colony_parent_basin",
            component="colony_parent_basin",
            family="rc_ant_worked_domain",
            source_refs=[rc_ant],
            required_dynamics=["colony_persists_as_parent_basin", "subbasins_gain_meaning_inside_parent"],
            state_surfaces=["colony_boundary", "nest_reserve", "subbasin_membership"],
            trace_surfaces=["colony_event_history", "reserve_change_trace"],
            controls=["colony_label_only_control", "sum_of_ants_as_colony_control"],
            producer_residue_risk="colony identity may be maintained by top-level producer object",
            medium_debt_risk="colony pressure may be broadcast to ants",
            blocked_relabels=["native_colony_agency", "biological_colony_life"],
            first_probe_relevance="root demand for RC-Ant-style probe",
        ),
        demand_row(
            demand_id="rc_ant_mobile_boundary_expression",
            component="mobile_boundary_expression",
            family="rc_ant_worked_domain",
            source_refs=[rc_ant],
            required_dynamics=["mobile_local_geometry_couples_parent_to_external_support", "movement_has_cost"],
            state_surfaces=["mobile_boundary_state", "local_reserve", "coupling_surface"],
            trace_surfaces=["movement_trace", "support_transfer_trace"],
            controls=["ant_object_as_native_agent_control", "free_motion_control"],
            producer_residue_risk="ant mode may be explicit state-machine variable",
            medium_debt_risk="movement coordination may be message-mediated",
            blocked_relabels=["native_ant_agency", "semantic_action"],
            first_probe_relevance="needed for any mobile ecology element",
        ),
        demand_row(
            demand_id="rc_ant_nest_home_basin",
            component="nest_home_basin",
            family="rc_ant_worked_domain",
            source_refs=[rc_ant],
            required_dynamics=["nest_provides_internal_support_architecture", "home_coupling_shapes_return"],
            state_surfaces=["nest_support_state", "home_affordance_state", "internal_subbasins"],
            trace_surfaces=["return_trace", "storage_update_trace"],
            controls=["home_label_only_control", "storage_without_support_control"],
            producer_residue_risk="home may be hard-coded coordinate or state variable",
            medium_debt_risk="homeward pressure may be direct instruction",
            blocked_relabels=["semantic_home_goal", "native_colony_home_identity"],
            first_probe_relevance="needed for food-return and reserve probes",
        ),
        demand_row(
            demand_id="rc_ant_food_resource_coupling",
            component="food_resource_coupling",
            family="rc_ant_worked_domain",
            source_refs=[rc_ant],
            required_dynamics=["external_support_basin_can_couple_to_mobile_expression", "support_can_be_bound_or_depleted"],
            state_surfaces=["food_support_basin", "external_affordance", "depletion_state"],
            trace_surfaces=["food_contact_trace", "support_binding_trace"],
            controls=["food_label_without_support_control", "resource_counter_as_native_food_control"],
            producer_residue_risk="food may be producer-managed resource counter",
            medium_debt_risk="food discovery may be direct message",
            blocked_relabels=["semantic_food_goal", "resource_counter_as_basin"],
            first_probe_relevance="basis for resource-coupling probe",
        ),
        demand_row(
            demand_id="rc_ant_route_support_trace",
            component="route_support_trace",
            family="rc_ant_worked_domain",
            source_refs=[rc_ant, shared],
            required_dynamics=["prior_passage_changes_future_route_affordance", "trace_has_cost_and_decay"],
            state_surfaces=["route_cost_surface", "trace_strength_state"],
            trace_surfaces=["deposition_trace", "decay_trace", "reentry_trace"],
            controls=["pheromone_label_only_control", "global_path_memory_control"],
            producer_residue_risk="route trace may be stored in global path table",
            medium_debt_risk="route support may be communicated directly",
            blocked_relabels=["native_pheromone_without_trace", "ant_message_as_route_support"],
            first_probe_relevance="central trace/aftereffect prototype demand",
        ),
        demand_row(
            demand_id="rc_ant_foodward_affordance_surface",
            component="foodward_affordance_surface",
            family="rc_ant_worked_domain",
            source_refs=[rc_ant, shared],
            required_dynamics=["empty_or_food_susceptible_mobile_geometry_moves_toward_food_affordance", "foodward_coupling_depends_on_reserve_or_role"],
            state_surfaces=["food_affordance_surface", "empty_cargo_state", "food_susceptibility_state"],
            trace_surfaces=["foodward_route_trace", "food_signature_contact_trace"],
            controls=["foodward_goal_label_control", "hidden_food_assignment_control"],
            producer_residue_risk="foodward route may be scheduled by producer",
            medium_debt_risk="food location may be sent as message",
            blocked_relabels=["semantic_food_seeking", "foodward_message_as_affordance"],
            first_probe_relevance="needed for foraging-like probe without goal labels",
        ),
        demand_row(
            demand_id="rc_ant_homeward_affordance_surface",
            component="homeward_affordance_surface",
            family="rc_ant_worked_domain",
            source_refs=[rc_ant, shared],
            required_dynamics=["cargo_or_home_susceptible_mobile_geometry_moves_toward_nest_affordance", "homeward_coupling_depends_on_bound_support"],
            state_surfaces=["home_affordance_surface", "cargo_state", "nest_coupling_state"],
            trace_surfaces=["homeward_route_trace", "cargo_return_trace"],
            controls=["homeward_goal_label_control", "hidden_return_assignment_control"],
            producer_residue_risk="return may be controlled by mode variable",
            medium_debt_risk="home location may be direct message",
            blocked_relabels=["semantic_return_goal", "home_message_as_affordance"],
            first_probe_relevance="needed for food-return/cargo probe",
        ),
        demand_row(
            demand_id="rc_ant_cargo_shaped_susceptibility",
            component="cargo_shaped_susceptibility",
            family="rc_ant_worked_domain",
            source_refs=[rc_ant],
            required_dynamics=["bound_cargo_changes_cost_and_future_coupling", "cargo_type_modulates_nest_subbasin_relevance"],
            state_surfaces=["bound_cargo_state", "movement_cost_state", "target_subbasin_susceptibility"],
            trace_surfaces=["cargo_binding_trace", "cargo_delivery_trace"],
            controls=["cargo_flag_as_bound_support_control", "cargo_without_cost_control"],
            producer_residue_risk="cargo may be boolean variable without support binding",
            medium_debt_risk="cargo routing may be direct task message",
            blocked_relabels=["semantic_carrying_intention", "cargo_flag_as_coherence_binding"],
            first_probe_relevance="needed for support transport and role-capture probes",
        ),
        demand_row(
            demand_id="rc_ant_reserve_hunger_pressure",
            component="reserve_hunger_pressure",
            family="rc_ant_worked_domain",
            source_refs=[rc_ant, shared],
            required_dynamics=["reserve_deficit_modulates_food_coupling_pressure", "many_local_elements_can_shift_due_to_common_deficit"],
            state_surfaces=["nest_reserve", "reserve_deficit", "foraging_susceptibility"],
            trace_surfaces=["reserve_pressure_trace", "local_shift_trace"],
            controls=["hunger_broadcast_control", "semantic_hunger_goal_control"],
            producer_residue_risk="hunger may be a global scheduler priority",
            medium_debt_risk="reserve deficit may be broadcast as command",
            blocked_relabels=["colony_hunger_as_semantic_goal", "broadcast_as_pressure"],
            first_probe_relevance="pressure/reserve prototype demand",
        ),
        demand_row(
            demand_id="rc_ant_alarm_threat_pressure",
            component="alarm_threat_pressure",
            family="rc_ant_worked_domain",
            source_refs=[rc_ant, shared],
            required_dynamics=["boundary_threat_alters_local_affordance", "compatible_mobile_geometries_shift_to_defense"],
            state_surfaces=["boundary_threat_state", "alarm_pressure_surface", "defense_susceptibility"],
            trace_surfaces=["alarm_trace", "defense_response_trace"],
            controls=["alarm_message_control", "semantic_fear_or_intention_control"],
            producer_residue_risk="defense response may be task assignment",
            medium_debt_risk="alarm may be direct broadcast",
            blocked_relabels=["semantic_alarm_understanding", "native_defense_agency"],
            first_probe_relevance="tests pressure/co-response under boundary perturbation",
        ),
        demand_row(
            demand_id="rc_ant_nursery_demand",
            component="nursery_demand",
            family="rc_ant_worked_domain",
            source_refs=[rc_ant, shared],
            required_dynamics=["brood_or_nursery_support_need_captures_compatible_roles", "care_coupling_remains_basin_demand_not_task_label"],
            state_surfaces=["nursery_support_basin", "brood_demand", "care_susceptibility"],
            trace_surfaces=["nursery_demand_trace", "care_response_trace"],
            controls=["task_assignment_as_nursery_control", "semantic_care_goal_control"],
            producer_residue_risk="nursery role may be explicit task assignment",
            medium_debt_risk="nursery demand may be message broadcast",
            blocked_relabels=["semantic_nursing_intention", "task_label_as_role_basin"],
            first_probe_relevance="role susceptibility and demand-field probe",
        ),
        demand_row(
            demand_id="rc_ant_waste_isolation",
            component="waste_isolation",
            family="rc_ant_worked_domain",
            source_refs=[rc_ant],
            required_dynamics=["harmful_or_spent_support_routes_to_isolation_basin", "persistence_requires_removal_or_boundary_repair"],
            state_surfaces=["waste_basin", "isolation_boundary", "leakage_state"],
            trace_surfaces=["waste_contact_trace", "isolation_route_trace"],
            controls=["waste_task_label_control", "waste_removal_without_isolation_control"],
            producer_residue_risk="waste removal may be hard-coded cleanup policy",
            medium_debt_risk="waste route may be direct task message",
            blocked_relabels=["semantic_cleaning_goal", "cleanup_policy_as_native_waste_basin"],
            first_probe_relevance="negative-basin and leakage-control probe",
        ),
        demand_row(
            demand_id="rc_ant_construction_tension",
            component="construction_tension",
            family="rc_ant_worked_domain",
            source_refs=[rc_ant],
            required_dynamics=["material_or_boundary_tension_changes_future_affordance", "construction_spends_support_to_modify_geometry"],
            state_surfaces=["construction_site_basin", "material_support", "boundary_strength"],
            trace_surfaces=["construction_action_trace", "geometry_change_trace"],
            controls=["construction_label_only_control", "free_geometry_change_control"],
            producer_residue_risk="construction may be external topology edit",
            medium_debt_risk="builders may receive direct construction commands",
            blocked_relabels=["semantic_building_intention", "producer_topology_edit_as_native_construction"],
            first_probe_relevance="tests geometry modification as ecology demand",
        ),
        demand_row(
            demand_id="rc_ant_crowding_congestion_cost",
            component="crowding_congestion_cost",
            family="rc_ant_worked_domain",
            source_refs=[rc_ant, shared],
            required_dynamics=["density_or_route_use_changes_movement_cost", "local_elements_redistribute_due_to_cost_surface"],
            state_surfaces=["congestion_cost_surface", "route_capacity_state", "local_density"],
            trace_surfaces=["crowding_trace", "route_shift_trace"],
            controls=["scheduler_collision_control", "crowding_label_only_control"],
            producer_residue_risk="congestion may be a pathfinding penalty inserted by producer",
            medium_debt_risk="route redirection may be direct message",
            blocked_relabels=["semantic_avoidance_choice", "scheduler_as_congestion_medium"],
            first_probe_relevance="shared cost surface and co-response probe",
        ),
        demand_row(
            demand_id="rc_ant_role_susceptibility_division_of_labor",
            component="role_susceptibility_division_of_labor",
            family="rc_ant_worked_domain",
            source_refs=[rc_ant, shared],
            required_dynamics=["repeated_coupling_deepens_role_basin_susceptibility", "different_mobile_geometries_respond_differently_to_same_demand"],
            state_surfaces=["role_basin_state", "local_history", "susceptibility_profile"],
            trace_surfaces=["role_reentry_trace", "demand_capture_trace"],
            controls=["task_table_as_division_control", "semantic_job_choice_control"],
            producer_residue_risk="division of labor may be explicit role table",
            medium_debt_risk="roles may be assigned through messages",
            blocked_relabels=["semantic_job_identity", "task_assignment_as_native_role"],
            first_probe_relevance="role differentiation and susceptibility probe",
        ),
        demand_row(
            demand_id="rc_ant_surplus_supported_split_reproduction",
            component="surplus_supported_split_reproduction",
            family="rc_ant_worked_domain",
            source_refs=[rc_ant],
            required_dynamics=["surplus_support_enables_new_identity_or_subidentity", "parent_closure_survives_split"],
            state_surfaces=["surplus_support", "new_boundary_candidate", "parent_closure_state"],
            trace_surfaces=["split_event_trace", "post_split_persistence_trace"],
            controls=["spawn_label_control", "parent_destroyed_by_split_control"],
            producer_residue_risk="spawn may be producer insertion",
            medium_debt_risk="split coordination may rely on central schedule",
            blocked_relabels=["biological_reproduction_claim", "producer_spawn_as_native_split"],
            first_probe_relevance="future reproduction/split probe target, not I1 evidence",
        ),
    ]


def all_demands() -> list[dict[str, Any]]:
    return general_demand_rows() + rc_ant_demand_rows()


def build_output() -> dict[str, Any]:
    sources = [source_record(source) for source in TARGET_SOURCES]
    rows = all_demands()
    general_rows = [row for row in rows if row["demand_family"] == "general"]
    rc_ant_rows = [row for row in rows if row["demand_family"] == "rc_ant_worked_domain"]
    check_inputs = {
        "sources": sources,
        "rows": rows,
        "general_rows": general_rows,
        "rc_ant_rows": rc_ant_rows,
    }
    output: dict[str, Any] = {
        "artifact_id": "n29_ecology_demand_extraction_i1",
        "experiment_id": "N29",
        "iteration": "I1",
        "generated_at": GENERATED_AT,
        "generated_by": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "status": "pending",
        "acceptance_state": "pending_checks",
        "source_scope": "rc_agentic_ecology_target_sources_only",
        "n05_n28_capability_coverage_claimed": False,
        "positive_ecology_evidence_opened": False,
        "prototype_rows_opened": False,
        "implementation_evidence_opened": False,
        "source_role_audit": sources,
        "ecology_demand_rows": general_rows,
        "rc_ant_component_demand_rows": rc_ant_rows,
        "blocked_claim_audit": UNSAFE_CLAIM_FLAGS,
        "claim_ceiling": (
            "ecology_demand_model_extracted_as_target_requirements_only_no_"
            "implementation_evidence"
        ),
        "iteration_1_interpretation": (
            "Iteration 1 supports an ecology demand model extracted from "
            "RC-agentic-ecology sources as target requirements only. It opens "
            "no implementation evidence, no positive ecology evidence, no "
            "prototype rows, and no native ant, colony, biological, sentience, "
            "or Phase 8 claim."
        ),
    }
    expected_source_paths = {source["source_path"] for source in TARGET_SOURCES}
    seen_source_paths = {source["source_path"] for source in sources}
    expected_general = {f"general_{demand_id}" for demand_id in GENERAL_DEMAND_IDS}
    expected_rc_ant = {f"rc_ant_{demand_id}" for demand_id in RC_ANT_DEMAND_IDS}
    seen_general = {row["demand_id"] for row in general_rows}
    seen_rc_ant = {row["demand_id"] for row in rc_ant_rows}
    checks = [
        {
            "check_id": "all_five_target_ecology_sources_inventoried",
            "passed": seen_source_paths == expected_source_paths
            and len(sources) == 5
            and all(source["exists"] for source in sources),
        },
        {
            "check_id": "source_roles_are_target_not_implementation_evidence",
            "passed": all(
                not source["implementation_evidence_opened"]
                and "implementation_evidence" in source["must_not_consume_as"]
                for source in sources
            ),
        },
        {
            "check_id": "general_demand_families_complete",
            "passed": seen_general == expected_general and len(general_rows) == 14,
        },
        {
            "check_id": "rc_ant_component_demand_families_complete",
            "passed": seen_rc_ant == expected_rc_ant and len(rc_ant_rows) == 16,
        },
        {
            "check_id": "every_demand_row_has_source_role_and_reference",
            "passed": all(
                row["source_role"] == "target_requirement_not_evidence"
                and row["source_spec_reference"]
                for row in rows
            ),
        },
        {
            "check_id": "implementation_evidence_closed_per_row",
            "passed": all(not row["implementation_evidence_opened"] for row in rows),
        },
        {
            "check_id": "no_n05_n28_capability_coverage_claimed",
            "passed": not output["n05_n28_capability_coverage_claimed"]
            and all(not row["n05_n28_capability_coverage_claimed"] for row in rows),
        },
        {
            "check_id": "no_prototype_rows_opened",
            "passed": not output["prototype_rows_opened"]
            and all(not row["prototype_row_opened"] for row in rows),
        },
        {
            "check_id": "no_positive_ecology_evidence_opened",
            "passed": not output["positive_ecology_evidence_opened"]
            and all(not row["positive_ecology_evidence_opened"] for row in rows),
        },
        {
            "check_id": "producer_residue_and_naturalization_debt_visible",
            "passed": any(row["ecology_component"] == "producer_residue" for row in rows)
            and any(row["ecology_component"] == "naturalization_condition" for row in rows),
        },
        {
            "check_id": "medium_debt_visible",
            "passed": any(row["ecology_component"] == "medium_debt" for row in rows)
            and any(row["medium_debt_risk"] for row in rows),
        },
        {
            "check_id": "unsafe_claim_flags_false",
            "passed": all(value is False for value in output["blocked_claim_audit"].values()),
        },
        {
            "check_id": "no_absolute_paths_in_records",
            "passed": no_absolute_paths({**output, "checks": []}),
        },
    ]
    output["checks"] = checks
    output["failed_checks"] = [
        check["check_id"] for check in checks if not bool(check["passed"])
    ]
    output["status"] = "passed" if not output["failed_checks"] else "failed"
    output["acceptance_state"] = (
        "accepted_ecology_demand_model_no_implementation_claims"
        if output["status"] == "passed"
        else "rejected_ecology_demand_model_failed_checks"
    )
    output["ready_for_iteration_2"] = output["status"] == "passed"
    output["source_count"] = len(sources)
    output["ecology_demand_row_count"] = len(general_rows)
    output["rc_ant_component_demand_row_count"] = len(rc_ant_rows)
    output["total_demand_row_count"] = len(rows)
    output["script_sha256"] = sha256_file(ROOT / SCRIPT_RELATIVE_PATH)
    output["output_digest"] = digest_value(
        {key: value for key, value in output.items() if key != "output_digest"}
    )
    # Preserve the local variable to make linting of check_inputs impossible to
    # accidentally remove before the row-count checks above.
    if not check_inputs["rows"]:
        raise RuntimeError("demand rows unexpectedly empty")
    return output


def write_report(output: dict[str, Any]) -> None:
    lines: list[str] = [
        "# N29 Iteration 1 - Ecology Demand Extraction",
        "",
        "## Summary",
        "",
        f"- Status: `{output['status']}`",
        f"- Acceptance state: `{output['acceptance_state']}`",
        f"- Source count: `{output['source_count']}`",
        f"- General demand rows: `{output['ecology_demand_row_count']}`",
        f"- RC-Ant demand rows: `{output['rc_ant_component_demand_row_count']}`",
        f"- Output digest: `{output['output_digest']}`",
        f"- Ready for Iteration 2: `{str(output['ready_for_iteration_2']).lower()}`",
        "",
        "Iteration 1 extracts ecology demands as target requirements only. It does not match",
        "those demands to N05-N28 capability evidence, does not open prototype rows, and",
        "does not claim implementation evidence from the ecology repository.",
        "",
        "## Source Role Audit",
        "",
        "| Source | Role | Exists | Digest policy | Claim ceiling |",
        "| --- | --- | --- | --- | --- |",
    ]
    for source in output["source_role_audit"]:
        lines.append(
            "| "
            f"`{source['source_path']}` | "
            f"`{source['source_role']}` | "
            f"`{str(source['exists']).lower()}` | "
            f"`{source['digest_policy']}` | "
            f"`{source['claim_ceiling']}` |"
        )
    lines.extend(
        [
            "",
            "## Demand Row Counts",
            "",
            "| Family | Count |",
            "| --- | ---: |",
            f"| General ecology demands | {output['ecology_demand_row_count']} |",
            f"| RC-Ant worked-domain demands | {output['rc_ant_component_demand_row_count']} |",
            f"| Total | {output['total_demand_row_count']} |",
            "",
            "## General Demand Rows",
            "",
            "| Demand | Component | First probe relevance |",
            "| --- | --- | --- |",
        ]
    )
    for row in output["ecology_demand_rows"]:
        lines.append(
            f"| `{row['demand_id']}` | `{row['ecology_component']}` | "
            f"{row['first_probe_relevance']} |"
        )
    lines.extend(
        [
            "",
            "## RC-Ant Demand Rows",
            "",
            "| Demand | Component | First probe relevance |",
            "| --- | --- | --- |",
        ]
    )
    for row in output["rc_ant_component_demand_rows"]:
        lines.append(
            f"| `{row['demand_id']}` | `{row['ecology_component']}` | "
            f"{row['first_probe_relevance']} |"
        )
    lines.extend(
        [
            "",
            "## Checks",
            "",
            "| Check | Passed |",
            "| --- | --- |",
        ]
    )
    for check in output["checks"]:
        lines.append(f"| `{check['check_id']}` | `{str(check['passed']).lower()}` |")
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "All blocked claim flags remain `false`. The ecology repository sources are",
            "consumed as demand, vocabulary, target ontology, and claim-boundary sources",
            "only.",
            "",
            "Closeout interpretation:",
            "",
            "```text",
            output["iteration_1_interpretation"],
            "```",
            "",
        ]
    )
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    output = build_output()
    OUTPUT.write_text(canonical_json(output), encoding="utf-8")
    write_report(output)


if __name__ == "__main__":
    main()

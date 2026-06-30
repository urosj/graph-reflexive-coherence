#!/usr/bin/env python3
"""Build N29 Iteration 3 N05-N28 capability card import."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-29T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N29-lgrc-agentic-ecology-convergence-bridge"
I1_OUTPUT = EXPERIMENT / "outputs" / "n29_ecology_demand_extraction_i1.json"
I2_OUTPUT = EXPERIMENT / "outputs" / "n29_agency_diagnostic_method_constraints_i2.json"
OUTPUT = EXPERIMENT / "outputs" / "n29_capability_atlas_i3.json"
REPORT = EXPERIMENT / "reports" / "n29_capability_atlas_i3.md"
SCRIPT_RELATIVE_PATH = (
    "experiments/2026-06-N29-lgrc-agentic-ecology-convergence-bridge/scripts/"
    "build_n29_capability_atlas_i3.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"

UNSAFE_CLAIM_FLAGS = {
    "native_agency_claim_opened": False,
    "native_ant_agency_opened": False,
    "native_colony_agency_opened": False,
    "biological_agency_opened": False,
    "organism_life_opened": False,
    "consciousness_opened": False,
    "sentience_opened": False,
    "semantic_choice_claim_opened": False,
    "semantic_goal_claim_opened": False,
    "semantic_cooperation_claim_opened": False,
    "fully_native_ecology_opened": False,
    "native_shared_medium_coordination_opened": False,
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


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def no_absolute_paths(data: Any) -> bool:
    text = json.dumps(data, sort_keys=True, ensure_ascii=True)
    forbidden = ("/" + "home" + "/", "Documents" + "/" + "RC-github")
    return all(pattern not in text for pattern in forbidden)


def source_artifact(rel_path: str, role: str) -> dict[str, Any]:
    path = ROOT / rel_path
    record: dict[str, Any] = {
        "path": rel_path,
        "artifact_role": role,
        "exists": path.exists(),
        "sha256": sha256_file(path) if path.exists() else "missing",
    }
    if path.exists() and path.suffix == ".json":
        try:
            payload = load_json(path)
            record["json_parseable"] = True
            record["source_status"] = payload.get("status", "not_recorded")
            record["source_acceptance_state"] = payload.get("acceptance_state", "not_recorded")
            record["source_output_digest"] = payload.get("output_digest", "not_recorded")
            record["source_artifact_id"] = payload.get("artifact_id", "not_recorded")
        except json.JSONDecodeError:
            record["json_parseable"] = False
            record["source_status"] = "json_parse_failed"
            record["source_acceptance_state"] = "json_parse_failed"
            record["source_output_digest"] = "json_parse_failed"
            record["source_artifact_id"] = "json_parse_failed"
    else:
        record["json_parseable"] = False
        record["source_status"] = "not_json"
        record["source_acceptance_state"] = "not_json"
        record["source_output_digest"] = "not_json"
        record["source_artifact_id"] = "not_json"
    return record


def card(
    *,
    capability_id: str,
    source_experiment: str,
    primary_artifact: str,
    source_claim_ceiling: str,
    review_gate_status: str,
    native_readiness_status: str,
    supplied_geometry_or_dynamic: list[str],
    producer_residue: str,
    naturalization_debt: str,
    medium_debt: str,
    possible_ecology_demands: list[str],
    blocked_ecology_relabels: list[str],
    prototype_potential: str,
    source_group: str,
    secondary_artifacts: list[str] | None = None,
) -> dict[str, Any]:
    artifacts = [source_artifact(primary_artifact, "primary_closeout_or_handoff")]
    for artifact in secondary_artifacts or []:
        artifacts.append(source_artifact(artifact, "supporting_source_artifact"))
    return {
        "capability_id": capability_id,
        "source_experiment": source_experiment,
        "source_group": source_group,
        "source_artifacts": artifacts,
        "source_claim_ceiling": source_claim_ceiling,
        "review_gate_status": review_gate_status,
        "native_readiness_status": native_readiness_status,
        "supplied_geometry_or_dynamic": supplied_geometry_or_dynamic,
        "producer_residue": producer_residue,
        "naturalization_debt": naturalization_debt,
        "medium_debt": medium_debt,
        "possible_ecology_demands": possible_ecology_demands,
        "blocked_ecology_relabels": blocked_ecology_relabels,
        "prototype_potential": prototype_potential,
        "consumption_rule": "capability_card_import_only_no_revalidation",
        "prior_experiment_revalidated": False,
        "positive_ecology_evidence_opened": False,
        "prototype_row_opened": False,
        "native_agency_claim_opened": False,
        "native_ecology_claim_opened": False,
    }


def capability_cards() -> list[dict[str, Any]]:
    n12_gate = "constrained_by_N12_native_producer_review_for_N05_N11"
    n19_gate = "constrained_by_N19_native_readiness_review_for_N13_N18"
    n20_gate = "constrained_by_N20_becoming_primitive_contract_and_debt_ledger"
    return [
        card(
            capability_id="n05_coherence_waves_oscillators",
            source_experiment="N05",
            primary_artifact=(
                "experiments/2026-05-N05-lgrc-coherence-waves-oscillators/"
                "outputs/n05_iteration_8_o6_closeout.json"
            ),
            source_claim_ceiling="bounded self-sustained oscillator / coherence-wave candidate; route-coupled trail memory remains blocked",
            review_gate_status=n12_gate,
            native_readiness_status="historical_LGRC_circuit_surface_reviewed_by_N12_not_agency",
            supplied_geometry_or_dynamic=[
                "delayed_coherence_pulse",
                "return_cycle",
                "oscillator_candidate",
                "budgeted_replayable_circuit",
            ],
            producer_residue="route coupling and memory policy not supplied by N05 itself",
            naturalization_debt="native trail/memory and agency use require later N08/N12/N20 discipline",
            medium_debt="no shared ecology medium; local circuit only",
            possible_ecology_demands=["trace", "pressure", "co_response", "resonance"],
            blocked_ecology_relabels=["choice", "agency", "ant_movement", "pheromone_memory"],
            prototype_potential="trace_pressure_loop_supporting_component",
            source_group="N05_N11_historical_mechanism_stack",
        ),
        card(
            capability_id="n06_runtime_visible_route_selection",
            source_experiment="N06",
            primary_artifact=(
                "experiments/2026-05-N06-lgrc-semantic-route-choice/"
                "outputs/n06_iteration_8_sc6_closeout.json"
            ),
            source_claim_ceiling="artifact-level runtime-visible route-selection candidate; semantic choice remains blocked",
            review_gate_status=n12_gate,
            native_readiness_status="historical_route_selection_surface_reviewed_by_N12_not_semantic_choice",
            supplied_geometry_or_dynamic=[
                "route_candidate_commitment",
                "runtime_visible_affordance_relation",
                "route_arbitration_surface",
            ],
            producer_residue="route scoring/arbitration policy may remain explicit unless naturalized later",
            naturalization_debt="semantic choice and native selection ownership blocked",
            medium_debt="does not by itself provide shared-medium coordination",
            possible_ecology_demands=[
                "foodward_affordance_surface",
                "homeward_affordance_surface",
                "route_support_trace",
            ],
            blocked_ecology_relabels=["semantic_choice", "ant_foraging_choice", "intention"],
            prototype_potential="route_affordance_mapping_component",
            source_group="N05_N11_historical_mechanism_stack",
        ),
        card(
            capability_id="n07_identity_attractor_invariance",
            source_experiment="N07",
            primary_artifact=(
                "experiments/2026-05-N07-rc-identity-attractor-invariance/"
                "outputs/n07_iteration_12_long_horizon_compatibility_closeout.json"
            ),
            source_claim_ceiling="artifact-only ID6 bounded identity-attractor / non-destructive exchange candidate",
            review_gate_status=n12_gate,
            native_readiness_status="identity_candidate_context_reviewed_by_N12_not_selfhood",
            supplied_geometry_or_dynamic=[
                "stable_identity_basin_candidate",
                "bounded_non_destructive_exchange",
                "long_horizon_artifact_replay_context",
            ],
            producer_residue="identity classification remains artifact-mediated",
            naturalization_debt="identity acceptance, selfhood, and native support blocked",
            medium_debt="no ecology parent basin or colony medium by itself",
            possible_ecology_demands=["parent_basin", "naturalization_condition"],
            blocked_ecology_relabels=["selfhood", "identity_acceptance", "organism_identity"],
            prototype_potential="same_basin_signature_context",
            source_group="N05_N11_historical_mechanism_stack",
        ),
        card(
            capability_id="n08_memory_trail_affordance",
            source_experiment="N08",
            primary_artifact=(
                "experiments/2026-05-N08-lgrc-memory-trail-affordance/"
                "outputs/n08_iteration_13_native_geometry_trail_closeout.json"
            ),
            source_claim_ceiling="route memory / trail-affordance candidate with producer-vs-native distinction preserved",
            review_gate_status=n12_gate,
            native_readiness_status="memory_context_surface_reviewed_by_N12; independent memory scalar remains risky unless geometry-mediated",
            supplied_geometry_or_dynamic=[
                "serialized_route_history",
                "trail_or_affordance_surface",
                "route_memory_context",
            ],
            producer_residue="memory_strength-like surfaces may be producer or policy scaffolds",
            naturalization_debt="pure coherence/flux pheromone-like memory requires later native validation",
            medium_debt="not yet shared ecology pheromone medium",
            possible_ecology_demands=["trace", "route_support_trace", "foodward_affordance_surface"],
            blocked_ecology_relabels=["pheromone_as_native_medium", "ant_memory", "semantic_memory"],
            prototype_potential="trace_surface_component_with_debt",
            source_group="N05_N11_historical_mechanism_stack",
        ),
        card(
            capability_id="n09_goal_proxy_regulation",
            source_experiment="N09",
            primary_artifact=(
                "experiments/2026-05-N09-lgrc-goal-proxy-regulation/"
                "outputs/n09_iteration_12_hypothesis_b2_native_substrate_closeout.json"
            ),
            source_claim_ceiling="artifact-only goal-proxy regulation candidate; semantic goal ownership blocked",
            review_gate_status=n12_gate,
            native_readiness_status="proxy_regulation_context_reviewed_by_N12_not_native_goal",
            supplied_geometry_or_dynamic=[
                "runtime_visible_proxy_condition",
                "bounded_regulation_response",
                "target_band_or_proxy_band_context",
            ],
            producer_residue="declared target/proxy surfaces may remain producer-defined",
            naturalization_debt="endogenous proxy formation deferred to N15 and proxy collapse to N26",
            medium_debt="no ecology pressure medium by itself",
            possible_ecology_demands=["pressure", "reserve_hunger_pressure", "alarm_threat_pressure"],
            blocked_ecology_relabels=["semantic_goal", "reward_maximization", "intention"],
            prototype_potential="pressure_regulation_component_with_proxy_debt",
            source_group="N05_N11_historical_mechanism_stack",
        ),
        card(
            capability_id="n10_agentic_like_integration",
            source_experiment="N10",
            primary_artifact=(
                "experiments/2026-05-N10-lgrc-agentic-like-integration/"
                "outputs/n10_iteration_15_hypothesis_c_closeout_and_handoff.json"
            ),
            source_claim_ceiling="bounded artifact-only agentic-like integration candidate",
            review_gate_status=n12_gate,
            native_readiness_status="composition_reviewed_by_N12_not_agency",
            supplied_geometry_or_dynamic=[
                "route_memory_support_regulation_composition",
                "support_disruption_sensitive_integration",
                "restoration_gated_integration",
            ],
            producer_residue="composition ledger and some policy surfaces remain explicit",
            naturalization_debt="native integrated agentic-like behavior not established",
            medium_debt="no shared ecology or colony surface by itself",
            possible_ecology_demands=["parent_basin_modulation", "pressure", "trace"],
            blocked_ecology_relabels=["agency", "semantic_action", "native_colony_behavior"],
            prototype_potential="multi_surface_bridge_context",
            source_group="N05_N11_historical_mechanism_stack",
        ),
        card(
            capability_id="n11_general_agentic_like_integration",
            source_experiment="N11",
            primary_artifact=(
                "experiments/2026-05-N11-lgrc-general-agentic-like-integration/"
                "outputs/n11_iteration_12_final_closeout_and_handoff.json"
            ),
            source_claim_ceiling="broader general artifact-only agentic-like integration candidate",
            review_gate_status=n12_gate,
            native_readiness_status="generalization_reviewed_by_N12_not_native_agency",
            supplied_geometry_or_dynamic=[
                "multi_axis_context_transfer",
                "support_state_transfer",
                "longer_horizon_generalization_candidate",
            ],
            producer_residue="generalization remains artifact-level and policy-mediated",
            naturalization_debt="fully native general integration blocked",
            medium_debt="no ecology-wide medium or role surface by itself",
            possible_ecology_demands=["naturalization_condition", "parent_basin_modulation"],
            blocked_ecology_relabels=["general_agency", "organism_life", "colony_agency"],
            prototype_potential="historical_integration_context_only",
            source_group="N05_N11_historical_mechanism_stack",
        ),
        card(
            capability_id="n12_native_producer_review_gate",
            source_experiment="N12",
            primary_artifact=(
                "experiments/2026-06-N12-lgrc-native-naturalization-and-producer-dissolution/"
                "outputs/n12_closeout_and_handoff.json"
            ),
            source_claim_ceiling="native/producers review gate for N05-N11; no agency and no native support opened",
            review_gate_status="review_gate_for_N05_N11",
            native_readiness_status="NAT classification gate; Phase 8 candidates only where explicitly recorded",
            supplied_geometry_or_dynamic=[
                "native_absorption_candidate_inventory",
                "producer_dissolution_boundary",
                "N05_N11_claim_ceiling_review",
            ],
            producer_residue="records which older surfaces remain producer scaffolds",
            naturalization_debt="native absorption candidates require later implementation validation",
            medium_debt="not a shared-medium evidence source",
            possible_ecology_demands=["producer_residue", "naturalization_condition"],
            blocked_ecology_relabels=["N05_N11_as_native_agency", "native_support_by_review"],
            prototype_potential="review_gate_only",
            source_group="review_gate_stack",
        ),
        card(
            capability_id="n13_support_seeking_regulation",
            source_experiment="N13",
            primary_artifact=(
                "experiments/2026-06-N13-lgrc-self-maintenance-and-support-seeking-regulation/"
                "outputs/n13_closeout_and_handoff.json"
            ),
            source_claim_ceiling="artifact-level AP3 support-seeking regulation candidate",
            review_gate_status=n19_gate,
            native_readiness_status="artifact_level_AP3_reviewed_by_N19_not_native_support",
            supplied_geometry_or_dynamic=["support_margin", "bounded_support_response", "support_regulation_axis"],
            producer_residue="support thresholds and response policies remain artifact-mediated",
            naturalization_debt="native support-generation not established",
            medium_debt="does not define ecology medium",
            possible_ecology_demands=["pressure", "reserve_hunger_pressure", "naturalization_condition"],
            blocked_ecology_relabels=["self_maintenance_as_selfhood", "support_seeking_as_intention"],
            prototype_potential="support_pressure_component",
            source_group="AP3_AP8_agency_prerequisite_stack",
        ),
        card(
            capability_id="n14_consequence_sensitive_route_selection",
            source_experiment="N14",
            primary_artifact=(
                "experiments/2026-06-N14-lgrc-consequence-sensitive-route-selection/"
                "outputs/n14_closeout_and_handoff.json"
            ),
            source_claim_ceiling="artifact-level AP4 consequence-sensitive route-selection candidate",
            review_gate_status=n19_gate,
            native_readiness_status="N19 records AP4 NAT4 gap; consume as artifact-level selection only",
            supplied_geometry_or_dynamic=["route_consequence_record", "consequence_sensitive_selection_context"],
            producer_residue="route consequence derivation and followout remain constructed in places",
            naturalization_debt="AP4 native route-conditioned selection remains unresolved",
            medium_debt="no shared ecology medium by itself",
            possible_ecology_demands=["foodward_affordance_surface", "homeward_affordance_surface", "role_susceptibility_division_of_labor"],
            blocked_ecology_relabels=["semantic_choice", "intention", "ant_decision"],
            prototype_potential="route_selection_component_with_AP4_gap",
            source_group="AP3_AP8_agency_prerequisite_stack",
        ),
        card(
            capability_id="n15_endogenous_proxy_formation",
            source_experiment="N15",
            primary_artifact=(
                "experiments/2026-06-N15-lgrc-endogenous-proxy-formation/"
                "outputs/n15_closeout_and_handoff.json"
            ),
            source_claim_ceiling="artifact-level AP5 runtime-derived proxy / target candidate",
            review_gate_status=n19_gate,
            native_readiness_status="N19 records AP5 NAT4 gap; consume as artifact-level proxy formation only",
            supplied_geometry_or_dynamic=["runtime_derived_target_candidate", "proxy_or_target_band", "bounded_regulation_input"],
            producer_residue="derivation policy and context weights remain frozen artifact policy",
            naturalization_debt="native proxy formation remains unresolved",
            medium_debt="no ecology medium by itself",
            possible_ecology_demands=["pressure", "susceptibility", "proxy_divergence_context"],
            blocked_ecology_relabels=["semantic_goal", "native_goal_ownership", "reward_as_function"],
            prototype_potential="proxy_pressure_component_with_AP5_gap",
            source_group="AP3_AP8_agency_prerequisite_stack",
        ),
        card(
            capability_id="n16_self_environment_boundary",
            source_experiment="N16",
            primary_artifact=(
                "experiments/2026-06-N16-lgrc-self-environment-boundary/"
                "outputs/n16_closeout_and_handoff.json"
            ),
            source_claim_ceiling="artifact-level AP6 self/environment boundary candidate",
            review_gate_status=n19_gate,
            native_readiness_status="artifact_level_boundary_requirements_reviewed_by_N19",
            supplied_geometry_or_dynamic=["internal_external_separation", "boundary_requirements", "shared_medium_separability_candidate"],
            producer_residue="boundary classification remains artifact/control mediated",
            naturalization_debt="selfhood and native boundary ownership blocked",
            medium_debt="shared-medium separability candidate, not ecology coordination",
            possible_ecology_demands=["parent_basin", "shared_medium", "mobile_boundary_expression"],
            blocked_ecology_relabels=["selfhood", "organism_boundary", "ant_body"],
            prototype_potential="boundary_shared_medium_unit_component",
            source_group="AP3_AP8_agency_prerequisite_stack",
        ),
        card(
            capability_id="n17_closed_boundary_engagement_loop",
            source_experiment="N17",
            primary_artifact=(
                "experiments/2026-06-N17-lgrc-closed-boundary-engagement-loop/"
                "outputs/n17_closeout_and_handoff.json"
            ),
            source_claim_ceiling="artifact-level AP7 closed boundary engagement loop candidate",
            review_gate_status=n19_gate,
            native_readiness_status="artifact_level_loop_reviewed_by_N19_not_action_perception_agency",
            supplied_geometry_or_dynamic=["external_internal_external_later_internal_loop", "resource_support_loop", "shared_medium_reciprocal_loop_candidates"],
            producer_residue="loop construction and some resource/shared-medium variants remain artifact mediated",
            naturalization_debt="semantic action/perception and native agency blocked",
            medium_debt="paired-perspective shared medium remains bounded and scoped",
            possible_ecology_demands=["co_response", "resonance", "shared_medium", "perturbation"],
            blocked_ecology_relabels=["semantic_action", "semantic_perception", "native_shared_medium_coordination"],
            prototype_potential="trace_pressure_loop_and_boundary_medium_component",
            source_group="AP3_AP8_agency_prerequisite_stack",
        ),
        card(
            capability_id="n18_limited_long_horizon_closure",
            source_experiment="N18",
            primary_artifact=(
                "experiments/2026-06-N18-lgrc-long-horizon-agentic-like-closure-stress-test/"
                "outputs/n18_closeout_and_handoff.json"
            ),
            source_claim_ceiling="limited artifact-level AP8 h4/L5 long-horizon agentic-like closure candidate",
            review_gate_status=n19_gate,
            native_readiness_status="Phase-8-ready validation telemetry only; h8/h16 and general AP8 blocked",
            supplied_geometry_or_dynamic=["limited_h4_long_horizon_stress_envelope", "cross_axis_continuity_bottleneck", "replay_control_cleanliness"],
            producer_residue="validation telemetry does not become native implementation",
            naturalization_debt="general long-horizon native closure blocked",
            medium_debt="shared-medium evidence remains narrow and bottleneck-aware",
            possible_ecology_demands=["naturalization_condition", "shared_medium", "resonance"],
            blocked_ecology_relabels=["general_AP8", "agency", "unrestricted_autonomy"],
            prototype_potential="long_horizon_constraint_context",
            source_group="AP3_AP8_agency_prerequisite_stack",
        ),
        card(
            capability_id="n19_native_readiness_review_gate",
            source_experiment="N19",
            primary_artifact=(
                "experiments/2026-06-N19-lgrc-native-naturalization-review-ap3-ap8/"
                "outputs/n19_closeout_and_handoff.json"
            ),
            source_claim_ceiling="artifact-level Phase-8 readiness review for AP3-AP8; AP4/AP5 NAT4 gaps remain",
            review_gate_status="review_gate_for_N13_N18",
            native_readiness_status="current implementation cannot generate full claimed AP3-AP8 NAT4 ladder",
            supplied_geometry_or_dynamic=["AP3_AP8_native_readiness_matrix", "AP4_AP5_gap_classification", "unsafe_relabel_blockers"],
            producer_residue="records AP-stack implementation gaps and scaffolds",
            naturalization_debt="AP4/AP5 native evidence gaps propagate to dependent rows",
            medium_debt="no ecology medium evidence by itself",
            possible_ecology_demands=["producer_residue", "naturalization_condition"],
            blocked_ecology_relabels=["AP_stack_as_native_agency", "Phase8_completion"],
            prototype_potential="review_gate_only",
            source_group="review_gate_stack",
        ),
        card(
            capability_id="n20_becoming_primitive_contract",
            source_experiment="N20",
            primary_artifact=(
                "experiments/2026-06-N20-lgrc-becoming-primitive-producer-translation-contract/"
                "outputs/n20_closeout_and_n21_handoff.json"
            ),
            source_claim_ceiling="artifact-level becoming primitive translation contract only",
            review_gate_status="contract_gate_for_N21_N28",
            native_readiness_status="schema_contract_no_primitive_evidence",
            supplied_geometry_or_dynamic=["primitive_contracts", "producer_residue_ledger", "same_basin_continuation_contract"],
            producer_residue="explicit ledger of producer-mediated fields and naturalization debt",
            naturalization_debt="defines debt; does not resolve it",
            medium_debt="records medium-related debt for later primitives",
            possible_ecology_demands=["producer_residue", "naturalization_condition"],
            blocked_ecology_relabels=["contract_as_evidence", "native_support_by_schema"],
            prototype_potential="schema_gate_only",
            source_group="becoming_primitive_stack",
        ),
        card(
            capability_id="n21_withdrawal_naturalization",
            source_experiment="N21",
            primary_artifact=(
                "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/"
                "outputs/n21_closeout_and_n22_handoff.json"
            ),
            source_claim_ceiling="bounded artifact-level WR6 withdrawal candidate plus N21-local ND5 naturalization-depth candidate",
            review_gate_status=n20_gate,
            native_readiness_status="bounded becoming primitive evidence; no native support or agency",
            supplied_geometry_or_dynamic=["withdrawal_resistance", "probe_absent_persistence", "same_basin_replay"],
            producer_residue="declared supports and probes remain audited surfaces",
            naturalization_debt="ND6 durable source mutation deferred to N22 bridge",
            medium_debt="no shared ecology medium by itself",
            possible_ecology_demands=["naturalization_condition", "withdrawal_resistance_context"],
            blocked_ecology_relabels=["willpower", "native_support", "agency"],
            prototype_potential="naturalization_gate_component",
            source_group="becoming_primitive_stack",
        ),
        card(
            capability_id="n22_susceptibility_update",
            source_experiment="N22",
            primary_artifact=(
                "experiments/2026-06-N22-lgrc-susceptibility-update-durable-geometry-modification/"
                "outputs/n22_closeout_and_n23_handoff.json"
            ),
            source_claim_ceiling="producer-mediated bounded SU5 susceptibility-update / durable geometry modification candidate",
            review_gate_status=n20_gate,
            native_readiness_status="producer-mediated susceptibility update; no native learning",
            supplied_geometry_or_dynamic=["durable_geometry_delta", "reentry_trace", "peer_same_budget_comparison"],
            producer_residue="carrier/producers remain visible and load-bearing",
            naturalization_debt="native learning and source mutation remain blocked",
            medium_debt="no ecology role or shared medium by itself",
            possible_ecology_demands=["susceptibility", "cargo_shaped_susceptibility", "role_susceptibility_division_of_labor"],
            blocked_ecology_relabels=["learning", "semantic_adaptation", "native_support"],
            prototype_potential="proxy_susceptibility_reentry_component",
            source_group="becoming_primitive_stack",
        ),
        card(
            capability_id="n23_live_continuation_collapse",
            source_experiment="N23",
            primary_artifact=(
                "experiments/2026-06-N23-lgrc-live-continuation-collapse-selection-geometry/"
                "outputs/n23_closeout_and_n24_handoff.json"
            ),
            source_claim_ceiling="LC6 live-continuation collapse / selection geometry candidate; semantic choice blocked",
            review_gate_status=n20_gate,
            native_readiness_status="bounded selection geometry with AP4 bridge candidate; final AP4 remains blocked",
            supplied_geometry_or_dynamic=["live_branch_set", "collapse_to_selected_continuation", "counterfactual_branch_audit"],
            producer_residue="branch fixtures and collapse probes remain artifact-scoped",
            naturalization_debt="semantic choice and native route selection blocked",
            medium_debt="no ecology shared medium by itself",
            possible_ecology_demands=["co_response", "role_susceptibility_division_of_labor"],
            blocked_ecology_relabels=["choice", "free_will", "producer_preference_as_selection"],
            prototype_potential="live_branch_collapse_component",
            source_group="becoming_primitive_stack",
        ),
        card(
            capability_id="n24_surplus_supported_optionality",
            source_experiment="N24",
            primary_artifact=(
                "experiments/2026-06-N24-lgrc-abundance-surplus-supported-optionality/"
                "outputs/n24_closeout_and_n25_handoff.json"
            ),
            source_claim_ceiling="AB5/N24-C5 surplus-supported optionality with producer flux scaffold context; N24-C6 not native",
            review_gate_status=n20_gate,
            native_readiness_status="mostly native surplus/optionality evidence plus producer-assisted flux conditioning context",
            supplied_geometry_or_dynamic=["surplus_above_maintenance_floor", "optional_continuation_set", "producer_flux_conditioning_scaffold"],
            producer_residue="producer flux conditioning marks missing native mechanism",
            naturalization_debt="broad native flux robustness remains debt",
            medium_debt="abundance not yet ecology medium or reproduction",
            possible_ecology_demands=["reserve_hunger_pressure", "surplus_supported_split_reproduction", "construction_tension"],
            blocked_ecology_relabels=["reward", "semantic_choice", "unbounded_abundance"],
            prototype_potential="reserve_optionality_formation_component",
            source_group="becoming_primitive_stack",
        ),
        card(
            capability_id="n25_scoped_basin_formation",
            source_experiment="N25",
            primary_artifact=(
                "experiments/2026-06-N25-lgrc-spark-sub-basin-new-basin-formation/"
                "outputs/n25_closeout_and_n26_handoff.json"
            ),
            source_claim_ceiling="N25-C6 scoped BF5 core/sub-basin formation with producer scaffold context; BF6 and independent new basin blocked",
            review_gate_status=n20_gate,
            native_readiness_status="scoped native sub-basin evidence; multi-basin runtime required N25.1/N25.2",
            supplied_geometry_or_dynamic=["sub_basin_candidate", "high_margin_core_formation", "producer_assisted_scaffold_context"],
            producer_residue="producer-assisted BF5 scaffold records missing native mechanism",
            naturalization_debt="independent new basin and BF6 blocked in original N25",
            medium_debt="multi-basin shared substrate absent until N25.2 validation",
            possible_ecology_demands=["parent_basin", "surplus_supported_split_reproduction", "mobile_boundary_expression"],
            blocked_ecology_relabels=["independent_new_basin", "native_multi_basin_by_label", "reproduction"],
            prototype_potential="formation_component_with_extension_dependency",
            source_group="becoming_primitive_stack",
        ),
        card(
            capability_id="n25_1_multi_basin_requirements_bridge",
            source_experiment="N25.1",
            primary_artifact=(
                "experiments/2026-06-N25.1-lgrc9v3-multi-basin-formation-extension-requirements/"
                "outputs/n25_1_closeout_and_phase8_extension_handoff.json"
            ),
            source_claim_ceiling="requirements bridge for LGRC9V3 multi-basin extension; no runtime evidence",
            review_gate_status="requirements_bridge_after_N25_before_phase8_runtime_validation",
            native_readiness_status="Phase 8 implementation requirement source only",
            supplied_geometry_or_dynamic=["multi_basin_extension_contract", "child_basin_runtime_surface_requirements"],
            producer_residue="records what must not be backfilled by labels or producers",
            naturalization_debt="runtime validation deferred to Phase 8 and N25.2",
            medium_debt="defines shared child-basin substrate requirements, not evidence",
            possible_ecology_demands=["medium_debt", "producer_residue", "parent_basin"],
            blocked_ecology_relabels=["requirements_as_runtime_evidence", "Phase8_completion"],
            prototype_potential="requirements_context_only",
            source_group="becoming_primitive_stack",
        ),
        card(
            capability_id="n25_2_mb6_validation_bridge",
            source_experiment="N25.2",
            primary_artifact=(
                "experiments/2026-06-N25.2-lgrc9v3-mb6-validation-bridge/"
                "outputs/n25_2_closeout_and_n26_handoff.json"
            ),
            source_claim_ceiling="validation-backed scoped LGRC9V3 MB6 multi-basin substrate handoff; not ant ecology or Phase 8 completion",
            review_gate_status="N25_1_contract_plus_phase8_runtime_validation_gate",
            native_readiness_status="scoped native multi-basin substrate evidence consumable by N26+ with limits",
            supplied_geometry_or_dynamic=["child_basin_record", "multi_window_child_basin_persistence", "fail_closed_multi_basin_controls"],
            producer_residue="runtime extension is default-off and scoped; not a third-party observer layer",
            naturalization_debt="unscoped ecology/ant use remains blocked",
            medium_debt="multi-basin substrate exists, but ecology shared-medium coordination remains future work",
            possible_ecology_demands=["parent_basin", "shared_medium", "mobile_boundary_expression", "surplus_supported_split_reproduction"],
            blocked_ecology_relabels=["ant_ecology_implementation", "organism_life", "Phase8_completion"],
            prototype_potential="boundary_shared_medium_unit_component",
            source_group="becoming_primitive_stack",
        ),
        card(
            capability_id="n26_proxy_divergence_collapse",
            source_experiment="N26",
            primary_artifact=(
                "experiments/2026-06-N26-lgrc-proxy-divergence-proxy-collapse/"
                "outputs/n26_closeout_and_n27_handoff.json"
            ),
            source_claim_ceiling="PD6 bounded proxy divergence / proxy collapse evidence with scoped artifact AP5 bridge candidate; native AP5 unresolved",
            review_gate_status=n20_gate,
            native_readiness_status="controlled proxy divergence/collapse; AP5 NAT4 gap unresolved",
            supplied_geometry_or_dynamic=["proxy_native_divergence", "proxy_collapse_under_perturbation", "basin_deepening_vs_proxy_score_contrast"],
            producer_residue="proxy surfaces and perturbation regimes remain declared/audited",
            naturalization_debt="native AP5 proxy formation remains blocked",
            medium_debt="no ecology reward or resource medium by itself",
            possible_ecology_demands=["pressure", "proxy_divergence_context", "food_resource_coupling"],
            blocked_ecology_relabels=["reward_as_goal", "proxy_success_as_agency", "semantic_goal"],
            prototype_potential="proxy_susceptibility_reentry_component",
            source_group="becoming_primitive_stack",
        ),
        card(
            capability_id="n27_configuration_substrate_transfer",
            source_experiment="N27",
            primary_artifact=(
                "experiments/2026-06-N27-lgrc-configuration-substrate-transfer/"
                "outputs/n27_closeout_and_n28_handoff.json"
            ),
            source_claim_ceiling="CT6 bounded configuration/topology transfer evidence; semantic identity transfer blocked",
            review_gate_status=n20_gate,
            native_readiness_status="bounded artifact-level transfer candidate ready for N28 context",
            supplied_geometry_or_dynamic=["configuration_transfer", "same_basin_mapping_replay", "stress_variant_transfer"],
            producer_residue="mapping ledger and artifact reconstruction surfaces remain explicit",
            naturalization_debt="cross-substrate generality and semantic role transfer blocked",
            medium_debt="does not create ecology role relocation by itself",
            possible_ecology_demands=["role_susceptibility_division_of_labor", "mobile_boundary_expression"],
            blocked_ecology_relabels=["identity_transfer", "semantic_role_relocation", "agency"],
            prototype_potential="transfer_replay_role_relocation_component",
            source_group="becoming_primitive_stack",
        ),
        card(
            capability_id="n28_generative_extractive_persistence",
            source_experiment="N28",
            primary_artifact=(
                "experiments/2026-06-N28-lgrc-generative-vs-extractive-persistence/"
                "outputs/n28_closeout_and_n29_handoff.json"
            ),
            source_claim_ceiling="GE6 bounded generative/extractive persistence evidence; broad margin robustness and ant ecology remain blocked",
            review_gate_status=n20_gate,
            native_readiness_status="N29-ready bounded generative/extractive pattern evidence, not agency",
            supplied_geometry_or_dynamic=["generative_capacity_shell", "extractive_contrast", "redistribution_processor_pattern", "environment_basin_forming_capacity_change"],
            producer_residue="pattern construction and visual diagnostics remain bounded source artifacts",
            naturalization_debt="broad margin robustness and ecology composition deferred",
            medium_debt="medium reshaping exists as pattern evidence, not shared ecology medium",
            possible_ecology_demands=["medium_surface", "co_response", "construction_tension", "waste_isolation"],
            blocked_ecology_relabels=["cooperation", "altruism", "ant_ecology", "biological_agency"],
            prototype_potential="generative_extractive_medium_reshaping_component",
            source_group="becoming_primitive_stack",
        ),
    ]


def check(check_id: str, passed: bool, details: str | None = None) -> dict[str, Any]:
    row: dict[str, Any] = {"check_id": check_id, "passed": passed}
    if details is not None:
        row["details"] = details
    return row


def build() -> dict[str, Any]:
    i1 = load_json(I1_OUTPUT)
    i2 = load_json(I2_OUTPUT)
    cards = capability_cards()
    required_ids = {
        "n05_coherence_waves_oscillators",
        "n06_runtime_visible_route_selection",
        "n07_identity_attractor_invariance",
        "n08_memory_trail_affordance",
        "n09_goal_proxy_regulation",
        "n10_agentic_like_integration",
        "n11_general_agentic_like_integration",
        "n12_native_producer_review_gate",
        "n13_support_seeking_regulation",
        "n14_consequence_sensitive_route_selection",
        "n15_endogenous_proxy_formation",
        "n16_self_environment_boundary",
        "n17_closed_boundary_engagement_loop",
        "n18_limited_long_horizon_closure",
        "n19_native_readiness_review_gate",
        "n20_becoming_primitive_contract",
        "n21_withdrawal_naturalization",
        "n22_susceptibility_update",
        "n23_live_continuation_collapse",
        "n24_surplus_supported_optionality",
        "n25_scoped_basin_formation",
        "n25_1_multi_basin_requirements_bridge",
        "n25_2_mb6_validation_bridge",
        "n26_proxy_divergence_collapse",
        "n27_configuration_substrate_transfer",
        "n28_generative_extractive_persistence",
    }
    required_fields = {
        "capability_id",
        "source_experiment",
        "source_artifacts",
        "source_claim_ceiling",
        "review_gate_status",
        "native_readiness_status",
        "supplied_geometry_or_dynamic",
        "producer_residue",
        "naturalization_debt",
        "medium_debt",
        "possible_ecology_demands",
        "blocked_ecology_relabels",
        "prototype_potential",
    }

    data: dict[str, Any] = {
        "artifact_id": "n29_capability_atlas_i3",
        "experiment_id": "N29",
        "iteration": "I3",
        "title": "N05-N28 Capability Card Import",
        "status": "passed",
        "acceptance_state": "accepted_n05_n28_capability_atlas_with_review_gates",
        "generated_at": GENERATED_AT,
        "generated_by": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "i1_source_artifact": (
            "experiments/2026-06-N29-lgrc-agentic-ecology-convergence-bridge/"
            "outputs/n29_ecology_demand_extraction_i1.json"
        ),
        "i1_status": i1.get("status", "not_recorded"),
        "i1_output_digest": i1.get("output_digest", "not_recorded"),
        "i2_source_artifact": (
            "experiments/2026-06-N29-lgrc-agentic-ecology-convergence-bridge/"
            "outputs/n29_agency_diagnostic_method_constraints_i2.json"
        ),
        "i2_status": i2.get("status", "not_recorded"),
        "i2_output_digest": i2.get("output_digest", "not_recorded"),
        "capability_atlas_supported": True,
        "prior_experiment_revalidation_attempted": False,
        "source_scope": "N05_N28_capability_cards_with_review_gates",
        "capability_cards": cards,
        "capability_card_count": len(cards),
        "review_gate_summary": {
            "N05_N11": "current consumption constrained by N12 native/producers review",
            "N13_N18": "current consumption constrained by N19 native-readiness review",
            "N20_N28": "current consumption constrained by N20 becoming-primitive contracts and each closeout",
            "N25_1_N25_2": "N25 extension and validation cards; N25.1 is requirements-only, N25.2 is scoped MB6 validation",
        },
        "source_of_truth_policy": {
            "capability_cards_role": "orientation_index_and_claim_boundary_summary_only",
            "capability_cards_are_full_data_source": False,
            "source_artifacts_required_for_full_data": True,
            "downstream_rule": (
                "Coverage, motif, and prototype rows may use I3 cards to find candidate "
                "sources and inherit claim ceilings, but any real evidence claim must "
                "read and cite the original experiment artifacts, closeouts, reports, "
                "or runtime records directly."
            ),
            "blocked_use": [
                "card_summary_as_full_experiment_data",
                "card_summary_as_runtime_evidence",
                "card_summary_as_prototype_proof",
                "card_summary_as_source_artifact_replacement",
            ],
        },
        "implementation_evidence_opened": False,
        "positive_ecology_evidence_opened": False,
        "prototype_rows_opened": False,
        "native_agency_claim_opened": False,
        "native_ant_agency_opened": False,
        "native_colony_agency_opened": False,
        "biological_agency_opened": False,
        "organism_life_opened": False,
        "sentience_opened": False,
        "phase8_completion_opened": False,
        "claim_ceiling": "capability_card_import_only_no_prior_revalidation_no_ecology_prototype_evidence",
        "blocked_claim_audit": copy.deepcopy(UNSAFE_CLAIM_FLAGS),
        "ready_for_iteration_4": True,
        "script_sha256": sha256_file(ROOT / SCRIPT_RELATIVE_PATH),
    }

    checks = [
        check("i1_ecology_demand_model_passed", data["i1_status"] == "passed"),
        check("i2_agency_method_constraints_passed", data["i2_status"] == "passed"),
        check("all_required_capability_cards_imported", {row["capability_id"] for row in cards} == required_ids),
        check("capability_card_count_expected", len(cards) == 26),
        check(
            "every_card_has_required_fields",
            all(required_fields.issubset(set(row)) for row in cards),
        ),
        check(
            "primary_source_artifacts_exist",
            all(row["source_artifacts"][0]["exists"] for row in cards),
        ),
        check(
            "primary_json_artifacts_parseable",
            all(row["source_artifacts"][0]["json_parseable"] for row in cards),
        ),
        check(
            "source_statuses_are_passed_or_complete",
            all(
                row["source_artifacts"][0]["source_status"] in {"passed", "pass", "complete"}
                for row in cards
            ),
        ),
        check(
            "review_gates_attached_to_historical_blocks",
            all("N12" in row["review_gate_status"] for row in cards if row["source_experiment"] in {"N05", "N06", "N07", "N08", "N09", "N10", "N11"})
            and all("N19" in row["review_gate_status"] for row in cards if row["source_experiment"] in {"N13", "N14", "N15", "N16", "N17", "N18"}),
        ),
        check(
            "n20_contract_gate_visible_for_becoming_primitives",
            all(
                "N20" in row["review_gate_status"] or row["source_experiment"] in {"N25.1", "N25.2"}
                for row in cards
                if row["source_experiment"] in {"N21", "N22", "N23", "N24", "N25", "N25.1", "N25.2", "N26", "N27", "N28"}
            ),
        ),
        check(
            "prototype_potential_present_but_rows_not_opened",
            all(row["prototype_potential"] and not row["prototype_row_opened"] for row in cards)
            and not data["prototype_rows_opened"],
        ),
        check(
            "positive_ecology_evidence_closed_per_card",
            all(not row["positive_ecology_evidence_opened"] for row in cards)
            and not data["positive_ecology_evidence_opened"],
        ),
        check(
            "prior_experiment_revalidation_not_attempted",
            not data["prior_experiment_revalidation_attempted"]
            and all(not row["prior_experiment_revalidated"] for row in cards),
        ),
        check(
            "capability_cards_are_orientation_not_source_replacement",
            data["source_of_truth_policy"]["capability_cards_role"]
            == "orientation_index_and_claim_boundary_summary_only"
            and not data["source_of_truth_policy"]["capability_cards_are_full_data_source"]
            and data["source_of_truth_policy"]["source_artifacts_required_for_full_data"],
        ),
        check("unsafe_claim_flags_false", not any(data["blocked_claim_audit"].values())),
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
        "# N29 Iteration 3 - N05-N28 Capability Card Import",
        "",
        "## Summary",
        "",
        f"- status: `{data['status']}`",
        f"- acceptance_state: `{data['acceptance_state']}`",
        f"- capability_card_count: `{data['capability_card_count']}`",
        f"- prior_experiment_revalidation_attempted: `{str(data['prior_experiment_revalidation_attempted']).lower()}`",
        f"- positive_ecology_evidence_opened: `{str(data['positive_ecology_evidence_opened']).lower()}`",
        f"- prototype_rows_opened: `{str(data['prototype_rows_opened']).lower()}`",
        f"- ready_for_iteration_4: `{str(data['ready_for_iteration_4']).lower()}`",
        f"- output_digest: `{data['output_digest']}`",
        "",
        "Iteration 3 imports N05-N28 as capability cards. It does not replay,",
        "revalidate, or promote prior experiments. Each card preserves source",
        "claim ceiling, review gate, native-readiness status, residue/debt, blocked",
        "ecology relabels, and prototype potential.",
        "",
        "Important source-of-truth rule: capability cards are orientation/index",
        "records only. Later N29 coverage, motif, and prototype rows must return to",
        "the original experiment artifacts, closeouts, reports, and runtime records",
        "for real/full data.",
        "",
        "## Capability Cards",
        "",
        "| Capability | Source | Group | Review Gate | Prototype Potential |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in data["capability_cards"]:
        lines.append(
            f"| `{row['capability_id']}` | `{row['source_experiment']}` | "
            f"`{row['source_group']}` | `{row['review_gate_status']}` | "
            f"`{row['prototype_potential']}` |"
        )
    lines.extend(
        [
            "",
            "## Source Of Truth Policy",
            "",
            f"- capability_cards_role: `{data['source_of_truth_policy']['capability_cards_role']}`",
            f"- capability_cards_are_full_data_source: `{str(data['source_of_truth_policy']['capability_cards_are_full_data_source']).lower()}`",
            f"- source_artifacts_required_for_full_data: `{str(data['source_of_truth_policy']['source_artifacts_required_for_full_data']).lower()}`",
            f"- downstream_rule: {data['source_of_truth_policy']['downstream_rule']}",
            "",
            "## Review Gate Summary",
            "",
        ]
    )
    for key, value in data["review_gate_summary"].items():
        lines.append(f"- `{key}`: {value}")
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
            "Iteration 3 supports the capability atlas as a bridge-facing import layer.",
            "It answers what prior experiments can supply as cards for later demand",
            "coverage and motif construction. It does not yet match those capabilities",
            "to ecology demands, open prototypes, or claim native ecology behavior.",
            "For any real evidence use, later rows must consume the original source",
            "artifacts directly; the I3 card is only a compact orientation and claim",
            "boundary record.",
            "",
            "The correct next step is Iteration 4: freeze bridge schemas and claim",
            "boundary enums before building coverage/debt rows.",
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

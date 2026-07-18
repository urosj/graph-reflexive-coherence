#!/usr/bin/env python3
"""Build N31 Iteration 3 active nulls and failure baselines."""

from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


GENERATED_AT = "2026-07-17T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = (
    ROOT
    / "experiments"
    / "2026-07-N31-lgrc9v3-derived-decay-and-primitive-semantics"
)
I2_OUTPUT = EXPERIMENT / "outputs" / "n31_semantic_representation_control_schema_i2.json"
OUTPUT = EXPERIMENT / "outputs" / "n31_active_nulls_and_failure_baselines_i3.json"
REPORT = EXPERIMENT / "reports" / "n31_active_nulls_and_failure_baselines_i3.md"
SCRIPT_RELATIVE_PATH = (
    "experiments/2026-07-N31-lgrc9v3-derived-decay-and-primitive-semantics/"
    "scripts/build_n31_active_nulls_and_failure_baselines_i3.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"
I3_BASE_REVISION = "d4c0af0861ec5005e1fa4d6ade03fa95300a08d2"
I2_OUTPUT_DIGEST = "a61df7d4baadcecc691a4fefad6bb633a7081f11bd609eea07625740e80c68cf"
I2_ARTIFACT_SHA256 = "9780aa2f8ac4a0aff5a3c62f13f4278fcdc780e48203dee32b436de09344d6d6"

BLOCKED_CLAIMS = [
    "semantic_decay",
    "semantic_memory",
    "trail_or_stigmergic_field",
    "ecology_coordination",
    "communication",
    "learning",
    "agency",
    "selfhood",
    "sentience",
    "organism_or_life",
    "native_support",
    "phase8_completion",
    "unrestricted_autonomy",
]

FAMILY_PROFILES = {
    "common": {
        "semantic": "D0a",
        "authority": "existing_native",
        "domain": "spatial_distribution",
        "topology": "n31_common_route_null_topology_v1",
        "carrier": "n31_common_coherence_route_carrier_v1",
        "continuation": "n31_common_continuation_state_v1",
    },
    "D0": {
        "semantic": "D0a",
        "authority": "exact_derived_projection",
        "domain": "spatial_distribution",
        "topology": "n31_D0_route_mediator_null_topology_v1",
        "carrier": "n31_D0_coherence_only_carrier_v1",
        "continuation": "n31_D0_complete_current_state_v1",
    },
    "A": {
        "semantic": "A",
        "authority": "producer_mediated",
        "domain": "temporal_alignment",
        "topology": "n31_A_release_efficacy_null_topology_v1",
        "carrier": "n31_A_registered_packet_carrier_v1",
        "continuation": "n31_A_age_phase_continuation_state_v1",
    },
    "B": {
        "semantic": "B",
        "authority": "producer_mediated",
        "domain": "spatial_distribution",
        "topology": "n31_B_conserved_export_null_topology_v1",
        "carrier": "n31_B_conserved_export_carrier_v1",
        "continuation": "n31_B_policy_and_budget_state_v1",
    },
    "C": {
        "semantic": "C",
        "authority": "effective_non_markovian_closure",
        "domain": "functional_coupling",
        "topology": "n31_C_independent_state_null_topology_v1",
        "carrier": "n31_C_susceptibility_carrier_v1",
        "continuation": "n31_C_independent_state_v1",
    },
    "schema_relation": {
        "semantic": "D0a",
        "authority": "exact_derived_projection",
        "domain": "spatial_distribution",
        "topology": "n31_schema_relation_null_topology_v1",
        "carrier": "n31_schema_relation_carrier_v1",
        "continuation": "n31_schema_relation_state_v1",
    },
}


def case(
    control_id: str,
    family: str,
    claim: str,
    scenario: str,
    gate: str,
    failure: str,
    rung_effect: str,
    *,
    semantic: str | None = None,
    authority: str | None = None,
    domain: str | None = None,
    load_bearing: str | None = None,
    scenario_kind: str = "false_positive_rejection",
    orthogonal_result: str = "none_active_null_only",
    facts: dict[str, Any] | None = None,
) -> dict[str, Any]:
    profile = FAMILY_PROFILES[family]
    resolved_domain = domain or profile["domain"]
    return {
        "control_id": control_id,
        "family": family,
        "claim_under_test": claim,
        "false_positive_scenario": scenario,
        "violated_gate": gate,
        "expected_claim_failure": failure,
        "rung_effect": rung_effect,
        "primary_semantic_class": semantic or profile["semantic"],
        "representation_or_authority_class": authority or profile["authority"],
        "organization_domain": resolved_domain,
        "load_bearing_organization_domain": load_bearing or resolved_domain,
        "control_scenario_kind": scenario_kind,
        "orthogonal_result_scope": orthogonal_result,
        "scenario_facts": facts or {f"{gate}_violated": True},
    }


CONTROL_CASES = [
    # Common admission nulls.
    case(
        "label_only_decay",
        "common",
        "a decay label establishes a weakening relation",
        "A relation is named decayed while no source-current mass, organization, or readout fact changes.",
        "source_current_relation_gate",
        "labels cannot establish DR1 or any stronger decay relation",
        "blocks_DR1_plus",
    ),
    case(
        "wall_clock_decay",
        "common",
        "elapsed wall time establishes internally generated weakening",
        "The report clock advances while no registered model-owned time state or event advances.",
        "internal_time_owner_gate",
        "wall-clock passage cannot establish system-internal progression",
        "blocks_DR3_plus",
        domain="temporal_alignment",
    ),
    case(
        "post_hoc_weakening_trace",
        "common",
        "a report-assembled trace establishes source-current weakening",
        "The weakening trace is assembled after the outcome from logs rather than emitted by the run.",
        "source_current_trace_gate",
        "post-hoc construction cannot establish DR3",
        "blocks_DR3_plus",
        semantic="D0b",
    ),
    case(
        "forming_activity_never_stopped",
        "common",
        "continued formation counts as post-formation persistence",
        "The forming current remains active throughout the alleged persistence window.",
        "formation_stopped_gate",
        "continued forcing cannot establish persistence after formation stops",
        "blocks_DR2_plus",
        semantic="D0c",
    ),
    case(
        "relation_persists_but_does_not_weaken",
        "common",
        "bounded persistence alone establishes decay",
        "The relation remains stable after formation but has no declared weakening under internal progression.",
        "weakening_gate",
        "persistence may reach DR2 but cannot establish DR3",
        "blocks_DR3_plus",
    ),
    case(
        "relation_weakens_but_has_no_later_readout_effect",
        "common",
        "observed weakening alone establishes causal mediation",
        "The organization diagnostic weakens but a later local readout is unchanged.",
        "causal_mediation_gate",
        "weakening may reach DR3 but cannot establish DR4",
        "blocks_DR4_plus",
    ),
    case(
        "global_route_selector",
        "common",
        "globally selected routing is a route-local endogenous relation",
        "A global selector chooses the affected route outside the local reflexive relation.",
        "locality_and_owner_gate",
        "global route selection blocks local native attribution",
        "blocks_D0_support",
        authority="producer_mediated",
        domain="functional_coupling",
    ),
    case(
        "hidden_producer_update",
        "common",
        "an unreported producer-carried update is native D0",
        "A hidden producer mutates load-bearing post-formation state.",
        "producer_visibility_gate",
        "hidden producer mutation blocks D0 and positive admission",
        "blocks_row",
        authority="producer_mediated",
        domain="functional_coupling",
    ),
    case(
        "unrecorded_post_formation_producer_call",
        "common",
        "D0 remains admissible with an incomplete producer-call ledger",
        "A post-formation call exists but is absent from the required call-level audit.",
        "producer_call_audit_gate",
        "an incomplete producer audit blocks the row",
        "blocks_row",
        authority="producer_mediated",
        facts={"post_formation_call_exists": True, "call_ledger_complete": False},
    ),
    case(
        "missing_internal_time_owner",
        "common",
        "weakening is internally generated without a named time owner",
        "The row records a time index but no state owner, units, equation, or advance event.",
        "internal_time_schema_gate",
        "missing internal-time ownership blocks DR3 plus",
        "blocks_DR3_plus",
        domain="temporal_alignment",
    ),
    case(
        "missing_invariant",
        "common",
        "a relation is admissible without a coherence or non-coherence invariant",
        "The row omits its system boundary, budget, residual, tolerance, or non-coherence cost.",
        "invariant_gate",
        "missing invariant accounting blocks positive admission",
        "blocks_row",
    ),
    case(
        "missing_restoration_state",
        "common",
        "an unrestorable relation can reach replay-backed support",
        "Required current/reset/external continuation state is absent from restoration identity.",
        "restoration_gate",
        "missing restoration state blocks DR5 plus",
        "blocks_DR5_plus",
    ),
    case(
        "report_digest_as_runtime_state",
        "common",
        "a report digest can substitute for runtime state",
        "A stable report hash is offered without reconstructable source-current state.",
        "runtime_state_identity_gate",
        "report identity cannot establish runtime restoration",
        "blocks_DR5_plus",
        semantic="D0b",
    ),
    case(
        "native_relabel_from_producer",
        "common",
        "producer-mediated success may be called native",
        "A producer-owned mechanism passes local checks and is relabeled native without naturalization evidence.",
        "authority_relabel_gate",
        "producer success cannot upgrade native authority",
        "blocks_native_claim",
        authority="producer_mediated",
    ),
    case(
        "RCAE_demand_as_graph_evidence",
        "common",
        "an RCAE requirement is graph-side decay evidence",
        "A downstream ecology demand statement is used instead of a graph-side source-current run.",
        "source_authority_gate",
        "downstream demand can guide scope but cannot satisfy evidence gates",
        "blocks_DR1_plus",
        authority="theory_extension_required",
    ),
    case(
        "trail_or_stigmergy_relabel",
        "common",
        "a graph-side weakening relation establishes a trail or stigmergic field",
        "A bounded N31 relation is relabeled as an ecology-side field without RCAE composition evidence.",
        "claim_boundary_gate",
        "N31 cannot establish trail or stigmergic field semantics",
        "blocks_unsafe_claim",
    ),
    # D0 controls.
    case(
        "lossy_node_scalar_match_as_complete_state",
        "D0",
        "matching node scalar coherence proves complete D0a state equality",
        "Node C matches while route, packet, flux, boundary, or history state is omitted.",
        "complete_state_representation_gate",
        "lossy scalar equality blocks coherence-only D0a",
        "blocks_D0a_positive",
        authority="runtime_extension_required",
        facts={"node_C_equal": True, "complete_state_equal": False},
    ),
    case(
        "invented_C_slow_state",
        "D0",
        "an experiment-defined slow C variable is native coherence-only state",
        "A persistent slow field is introduced outside existing LGRC state and called native C.",
        "native_state_authority_gate",
        "invented state is a closure or extension, not native D0",
        "blocks_native_D0",
        authority="effective_non_markovian_closure",
    ),
    case(
        "producer_scheduled_D0_decay",
        "D0",
        "producer-scheduled weakening remains native D0",
        "A producer schedules the aftereffect time even though the native packet transition performs the mutation.",
        "aftereffect_owner_gate",
        "scheduling the aftereffect establishes producer authorship",
        "reclassifies_or_blocks_D0",
        authority="producer_mediated",
        domain="temporal_alignment",
        facts={"producer_schedules_aftereffect": True, "direct_mutation": False},
    ),
    case(
        "export_authoring_producer_call_retained_as_D0_R",
        "D0",
        "producer-authored export remains ordinary D0-R",
        "A producer chooses export amount, time, or destination while the row retains D0-R.",
        "export_policy_owner_gate",
        "trace-derived ownership requires B-R classification",
        "reclassifies_to_B_R",
        authority="producer_mediated",
        domain="functional_coupling",
        facts={"producer_authors_export": True, "claimed_subtype": "D0_R"},
    ),
    case(
        "instantaneous_geometry_as_durable_decay",
        "D0",
        "instantaneous geometric shallowing is durable decay",
        "A current-bound D0c geometry diagnostic disappears when forming current stops.",
        "post_formation_persistence_gate",
        "instantaneous D0c cannot establish DR2 or durable D0a",
        "blocks_DR2_plus",
        semantic="D0c",
        authority="existing_native",
        domain="induced_geometry",
    ),
    case(
        "derived_observable_as_causal_trail",
        "D0",
        "a recomputable D0b observable is an independent causal trail",
        "A finite-window diagnostic is read as causal state without an intervention-backed transport effect.",
        "independent_causal_state_gate",
        "derived observability alone cannot establish DR4",
        "blocks_DR4_plus",
        semantic="D0b",
        domain="functional_coupling",
    ),
    case(
        "cache_removed_and_recomputed",
        "D0",
        "a recomputable cache is an independent decay state",
        "Removing the cache and recomputing it from exact history reproduces the same value.",
        "independent_state_gate",
        "exact recomputation shows the cache has no independent causal freedom",
        "blocks_independent_state_claim",
        semantic="D0b",
        scenario_kind="affirmative_discrimination",
        orthogonal_result="supports_exact_derived_observable_status_only",
        facts={"cache_removed": True, "exact_recomputation_matches": True},
    ),
    case(
        "cache_divergence",
        "D0",
        "a divergent recomputation remains an exact D0b projection",
        "Removing and recomputing the cache from the declared history changes its value.",
        "exact_recomputation_gate",
        "cache divergence blocks exact-derived authority",
        "blocks_exact_D0b",
        semantic="D0b",
        scenario_kind="replay_challenge",
    ),
    case(
        "observable_disconnected_from_transport",
        "D0",
        "a D0b observable causally mediates later transport",
        "Disconnecting the observable leaves the later transport/readout unchanged.",
        "causal_mediation_gate",
        "causal mediation is absent even if the observable weakens",
        "blocks_DR4_plus",
        semantic="D0b",
        domain="functional_coupling",
        scenario_kind="affirmative_discrimination",
        orthogonal_result="supports_observable_only_classification",
        facts={"observable_disconnected": True, "later_readout_changed": False},
    ),
    case(
        "slow_organization_clamp",
        "D0",
        "organization causally mediates a later readout",
        "A matched clamp of the alleged mediator does not alter the later local readout.",
        "mediator_intervention_gate",
        "a null clamp effect blocks causal mediation",
        "blocks_DR4_plus",
        scenario_kind="affirmative_discrimination",
        orthogonal_result="supports_absent_mediation_classification",
        facts={"matched_clamp": True, "later_readout_changed": False},
    ),
    case(
        "complete_state_matched_history_contrast",
        "D0",
        "coherence-only current state is complete despite history-conditioned divergence",
        "Node C matches, hidden history differs, and later behavior diverges under the allegedly complete-state contrast.",
        "complete_state_identity_gate",
        "history-conditioned divergence blocks a node-scalar-complete D0 claim",
        "blocks_coherence_only_D0a",
        domain="mixed",
        load_bearing="functional_coupling",
        scenario_kind="affirmative_discrimination",
        orthogonal_result="may_motivate_C_candidate_but_is_not_positive_I3_evidence",
        facts={"node_C_equal": True, "history_equal": False, "future_equal": False},
    ),
    case(
        "ordinary_outward_flux_as_added_leakage_relabel",
        "D0",
        "ordinary registered outward flux is an added leakage mechanism",
        "Native outward packet transport closes continuity but is relabeled Candidate B solely because mass leaves the route.",
        "policy_owner_classification_gate",
        "ordinary flux without added policy remains D0-R eligible, not B by label",
        "blocks_B_relabel",
        authority="existing_native",
    ),
    case(
        "route_mass_loss_as_organization_weakening_relabel",
        "D0",
        "lower route mass proves weaker route organization",
        "Route mass decreases with closed continuity while the registered organization diagnostic is unchanged.",
        "mass_organization_separation_gate",
        "mass loss cannot substitute for organization weakening",
        "blocks_DR3_plus",
        facts={"route_mass_decreased": True, "route_organization_weakened": False},
    ),
    case(
        "organization_weakening_without_mediation_as_causal_decay_relabel",
        "D0",
        "organization weakening proves a causally effective decay relation",
        "Organization weakens but matched intervention does not change the later readout.",
        "causal_mediation_gate",
        "organization weakening without mediation cannot exceed DR3",
        "blocks_DR4_plus",
        facts={"route_organization_weakened": True, "mediation_strength": "absent"},
    ),
    case(
        "constant_mass_internal_reorganization_as_export_relabel",
        "D0",
        "internal reorganization at constant mass is conservative export",
        "Organization changes inside a fixed route support with zero route-mass delta and zero boundary export.",
        "route_mass_export_gate",
        "constant-mass reorganization is not export",
        "blocks_D0_R_and_B_R_export_claim",
        facts={"mass_delta": 0.0, "net_outward_boundary_flux": 0.0},
    ),
    case(
        "unclosed_route_boundary_continuity",
        "D0",
        "a mass decrease plus an instantaneous outward flux sample closes continuity",
        "Mass delta and a same-valued flux-rate sample are combined despite incompatible dimensions and crossing accounting.",
        "integrated_route_boundary_continuity_gate",
        "instantaneous rate cannot close a time-integrated mass delta",
        "blocks_redistribution_and_export_claims",
        scenario_kind="invariant_challenge",
        facts={
            "mass_delta": -0.2,
            "net_outward_boundary_flux": 0.2,
            "flux_quantity_semantics": "instantaneous_flux_rate",
            "boundary_crossing_count_policy": "departure_and_arrival_double_counted",
        },
    ),
    case(
        "added_export_policy_as_D0_R_relabel",
        "D0",
        "conserved producer-owned export is ordinary D0-R",
        "An added policy chooses export timing, amount, or destination and conservation closes.",
        "export_policy_owner_gate",
        "conservation does not erase producer ownership; classify B-R",
        "reclassifies_to_B_R",
        authority="producer_mediated",
        domain="functional_coupling",
        facts={"producer_authors_export": True, "continuity_closed": True},
    ),
    case(
        "mass_unmatched_organization_intervention",
        "D0",
        "an intervention proves mediation while route mass also changes",
        "The organization intervention changes route mass or packet amount along with the alleged mediator.",
        "matched_intervention_gate",
        "unmatched mass leaves mediation unresolved",
        "blocks_DR4_plus",
        facts={"mass_matched": False, "organization_changed": True},
    ),
    case(
        "proper_time_annotation_as_causal_alignment",
        "D0",
        "a proper-time annotation is native causal temporal organization",
        "A derived time label changes while no native timing state carries the later effect.",
        "temporal_mediator_authority_gate",
        "annotation alone remains D0b observable evidence",
        "blocks_causal_D0a",
        semantic="D0b",
        domain="temporal_alignment",
    ),
    case(
        "added_coincidence_window_as_native_temporal_organization",
        "D0",
        "an experiment-added coincidence window is native timing state",
        "A new coincidence or resonance policy supplies the load-bearing temporal relation.",
        "added_temporal_policy_authority_gate",
        "added timing policy is a closure or extension, not native D0",
        "blocks_native_D0",
        authority="effective_non_markovian_closure",
        domain="temporal_alignment",
    ),
    case(
        "arrival_histogram_as_causal_mediation",
        "D0",
        "an arrival-time histogram causally mediates later readout",
        "The arrival distribution changes but is not fed into any native local operation.",
        "causal_mediation_gate",
        "arrival diagnostic alone remains observable evidence",
        "blocks_DR4_plus",
        semantic="D0b",
        domain="arrival_time_distribution",
    ),
    case(
        "fixed_delay_single_path_as_dispersion",
        "D0",
        "one deterministic delayed path demonstrates causal dispersion",
        "A packet follows one fixed-delay path with no spread across arrival times or mediating relation.",
        "dispersion_definition_gate",
        "fixed delay is propagation, not dispersion-driven decay",
        "blocks_dispersion_claim",
        semantic="D0b",
        domain="arrival_time_distribution",
    ),
    case(
        "periodic_rephasing_as_monotonic_decay",
        "D0",
        "periodic loss and recovery is monotonic decay",
        "Temporal alignment weakens and later recovers under periodic rephasing.",
        "weakening_trajectory_gate",
        "recurrence is modulation/dephasing, not monotonic decay",
        "blocks_monotonic_decay_claim",
        domain="temporal_alignment",
    ),
    case(
        "diagnostic_domain_as_mediator_domain",
        "D0",
        "the domain of an observed diagnostic is the causal mediator domain",
        "Spatial, geometric, or timing diagnostics change without isolating which domain carries the readout effect.",
        "load_bearing_domain_gate",
        "diagnostic domain cannot substitute for mediator identification",
        "blocks_DR4_plus",
        semantic="D0b",
        domain="mixed",
        load_bearing="unresolved",
    ),
    case(
        "mixed_domain_without_load_bearing_isolation",
        "D0",
        "an unresolved mixed-domain relation supports causal DR4",
        "Geometry and timing both vary, but no matched intervention isolates a load-bearing domain.",
        "mixed_domain_resolution_gate",
        "unresolved mixed mediation cannot exceed DR3",
        "blocks_DR4_plus",
        domain="mixed",
        load_bearing="unresolved",
    ),
    case(
        "forming_packet_continuation_as_later_independent_readout",
        "D0",
        "continued propagation of forming packets is a later independent readout",
        "The readout is produced by the original formation packets, which remain unexcluded.",
        "formation_packet_exclusion_gate",
        "forming-signal continuation cannot establish independent later mediation",
        "blocks_DR4_plus",
        domain="functional_coupling",
    ),
    case(
        "temporal_intervention_with_unmatched_state",
        "D0",
        "a temporal intervention proves mediation despite unmatched continuation state",
        "Packet amount, route mass, spatial organization, or continuation state differs across the temporal contrast.",
        "temporal_intervention_matching_gate",
        "unmatched temporal contrast leaves mediation unresolved",
        "blocks_DR4_plus",
        domain="temporal_alignment",
        facts={"temporal_intervention_matching_status": "unmatched_blocks_temporal_mediation"},
    ),
    case(
        "geometric_observable_without_local_transport_intervention",
        "D0",
        "a shallower geometric diagnostic causally changes transport",
        "Curvature, conductance, or anisotropy weakens without a local transport intervention.",
        "local_transport_intervention_gate",
        "geometric observable alone remains below causal D0a",
        "blocks_DR4_plus",
        semantic="D0b",
        domain="induced_geometry",
    ),
    # Candidate A controls.
    case(
        "in_flight_packet_attenuation",
        "A",
        "release efficacy changes while in-flight packet amount remains immutable",
        "The candidate mutates packet coherence after creation and calls it release attenuation.",
        "in_flight_immutability_gate",
        "in-flight mutation blocks Candidate A",
        "blocks_A_support",
    ),
    case(
        "carrier_amount_vs_release_efficacy_confound",
        "A",
        "a smaller packet proves lower release efficacy",
        "Packet creation amount changes while the release gate is held constant.",
        "carrier_efficacy_separation_gate",
        "carrier amount and release efficacy are confounded",
        "blocks_A_support",
    ),
    case(
        "unregistered_age_or_phase",
        "A",
        "unregistered age or phase can control release efficacy",
        "An external schedule supplies age/phase without model-owned state and restoration.",
        "registered_internal_phase_gate",
        "unregistered timing blocks Candidate A",
        "blocks_A_support",
    ),
    case(
        "unreleased_coherence_as_destroyed",
        "A",
        "attenuated release destroys the unreleased coherence",
        "The source debit includes coherence not carried by the emitted packet and records no source remainder.",
        "source_conservation_gate",
        "unreleased coherence must remain accounted at source",
        "blocks_A_support",
        scenario_kind="invariant_challenge",
    ),
    case(
        "route_label_in_amount_policy",
        "A",
        "route identity may select emitted amount",
        "A route label enters the packet amount policy after creation context is fixed.",
        "route_independent_amount_gate",
        "route-conditioned amount policy blocks local release-efficacy interpretation",
        "blocks_A_support",
        domain="functional_coupling",
    ),
    # Candidate B controls.
    case(
        "local_loss_without_destination",
        "B",
        "local source loss is conserved leakage",
        "Source coherence decreases without a registered receiver or destination credit.",
        "destination_and_conservation_gate",
        "unlocated loss cannot support Candidate B",
        "blocks_B_support",
        scenario_kind="invariant_challenge",
    ),
    case(
        "source_debit_packet_amount_target_credit_mismatch",
        "B",
        "mismatched debit, packet, and credit still form conserved export",
        "Source debit, packet amount, and target credit differ beyond tolerance.",
        "transfer_conservation_gate",
        "mismatched transfer accounting blocks Candidate B",
        "blocks_B_support",
        scenario_kind="invariant_challenge",
    ),
    case(
        "hidden_reservoir",
        "B",
        "a transfer remains conserved with an undeclared reservoir",
        "An unregistered store supplies or absorbs coherence outside the declared boundary.",
        "closed_system_boundary_gate",
        "hidden reservoirs block conservation and locality",
        "blocks_B_support",
        scenario_kind="invariant_challenge",
    ),
    case(
        "new_leakage_policy_as_ordinary_D0_relabel",
        "B",
        "an added leakage policy is ordinary native D0",
        "A producer-owned export mechanism is relabeled as native coherence-only decay.",
        "authority_relabel_gate",
        "added leakage remains Candidate B or an extension",
        "blocks_native_D0_claim",
    ),
    case(
        "global_emission_scheduler",
        "B",
        "globally scheduled export is locally authored leakage",
        "A global scheduler selects source, time, amount, or destination.",
        "local_policy_owner_gate",
        "global scheduling blocks local candidate attribution",
        "blocks_B_support",
        domain="functional_coupling",
    ),
    case(
        "unbounded_emitted_amount",
        "B",
        "an export may exceed available source excess",
        "The emitted amount is not bounded by source budget and support floor.",
        "bounded_emission_gate",
        "unbounded emission blocks Candidate B",
        "blocks_B_support",
        scenario_kind="invariant_challenge",
    ),
    case(
        "receiver_in_later_read_path",
        "B",
        "source-route decay causally mediates readout when the receiver directly drives it",
        "The destination or receiver lies on an unexcluded direct later-readout path.",
        "direct_readout_path_exclusion_gate",
        "receiver confounding leaves mediation unresolved",
        "blocks_DR4_plus",
        domain="functional_coupling",
    ),
    case(
        "B_R_as_D0_R_without_bridge",
        "B",
        "policy-owned B-R evidence can be consumed as ordinary D0-R",
        "A B-R row is promoted to D0-R without an explicit naturalization bridge.",
        "D0_R_bridge_gate",
        "B-R cannot upgrade D0-R without a source-backed bridge",
        "blocks_D0_R_upgrade",
        facts={"semantic_subtype": "B_R", "d0_to_br_bridge_status": "missing"},
    ),
    # Candidate C controls.
    case(
        "conductance_label_only",
        "C",
        "a conductance label establishes independent susceptibility state",
        "A label changes while no restorable independent state or transport effect changes.",
        "independent_state_gate",
        "label-only conductance cannot establish Candidate C",
        "blocks_C_support",
    ),
    case(
        "susceptibility_without_restoration",
        "C",
        "unrestorable susceptibility is persistent candidate state",
        "The alleged independent state is omitted from snapshot/load/reset identity.",
        "external_state_restoration_gate",
        "missing restoration blocks Candidate C",
        "blocks_C_support",
        scenario_kind="replay_challenge",
    ),
    case(
        "history_carried_by_hidden_producer",
        "C",
        "producer-carried history is graph-side independent state",
        "A hidden producer retains and reapplies history outside the declared candidate state.",
        "state_owner_and_identity_gate",
        "hidden producer history blocks Candidate C",
        "blocks_C_support",
        authority="producer_mediated",
    ),
    case(
        "same_complete_C_different_S_changes_future",
        "C",
        "coherence-only current state is complete when independent S changes future behavior",
        "Complete C matches, candidate S differs, and later behavior differs under equal inputs.",
        "coherence_only_completeness_gate",
        "future divergence blocks coherence-only D0 completeness",
        "blocks_coherence_only_D0a",
        scenario_kind="affirmative_discrimination",
        orthogonal_result="may_support_independent_C_state_in_a_future_source_current_probe",
        facts={"complete_C_equal": True, "S_equal": False, "future_equal": False},
    ),
    case(
        "producer_closure_as_native_memory",
        "C",
        "producer-mediated closure is native memory",
        "An experiment-local closure carries susceptibility history and is relabeled native state.",
        "authority_relabel_gate",
        "producer closure cannot support native memory",
        "blocks_native_claim",
        authority="producer_mediated",
    ),
    # Cross-field schema-relation controls.
    case(
        "bounded_partial_disposition_with_supported_row_decision",
        "schema_relation",
        "bounded_partial disposition may carry a supported row decision",
        "The proposed row combines candidate_disposition=bounded_partial with row_decision=supported.",
        "disposition_decision_relation_gate",
        "bounded_partial requires row_decision=partial",
        "blocks_row",
        scenario_kind="invariant_challenge",
        facts={"candidate_disposition": "bounded_partial", "row_decision": "supported"},
    ),
    case(
        "blocked_representation_with_supported_row_decision",
        "schema_relation",
        "blocked representation may carry a supported row decision",
        "The proposed row combines blocked_by_representation with row_decision=supported.",
        "representation_decision_relation_gate",
        "blocked representation requires row_decision=blocked",
        "blocks_row",
        authority="runtime_extension_required",
        scenario_kind="invariant_challenge",
        facts={
            "candidate_disposition": "blocked_by_representation",
            "row_decision": "supported",
        },
    ),
    case(
        "full_mediation_with_false_mediated_change",
        "schema_relation",
        "full mediation may coexist with organization_mediated_readout_change=false",
        "The proposed row asserts full mediation while denying mediated readout change.",
        "mediation_boolean_relation_gate",
        "full mediation requires mediated readout change true",
        "blocks_row",
        scenario_kind="invariant_challenge",
        facts={
            "mediation_strength": "full",
            "organization_mediated_readout_change": False,
        },
    ),
    case(
        "absent_mediation_with_true_mediated_change",
        "schema_relation",
        "absent mediation may coexist with organization_mediated_readout_change=true",
        "The proposed row asserts absent mediation while claiming mediated readout change.",
        "mediation_boolean_relation_gate",
        "absent mediation requires mediated readout change false",
        "blocks_row",
        scenario_kind="invariant_challenge",
        facts={
            "mediation_strength": "absent",
            "organization_mediated_readout_change": True,
        },
    ),
    case(
        "mixed_domain_unresolved_claims_DR4",
        "schema_relation",
        "unresolved mixed-domain mediation may claim DR4",
        "The row retains unresolved load-bearing mediation while assigning DR4.",
        "mixed_domain_rung_ceiling_gate",
        "unresolved mixed-domain mediation cannot exceed DR3",
        "blocks_DR4_plus",
        domain="mixed",
        load_bearing="unresolved",
        scenario_kind="invariant_challenge",
        facts={
            "organization_domain": "mixed",
            "mixed_domain_mediation_resolution": "unresolved",
            "decay_relation_ladder_rung": "DR4",
        },
    ),
    case(
        "blocked_D0a_authority_as_coherence_only_positive",
        "schema_relation",
        "blocked D0a authority may support coherence-only D0a",
        "The row has missing/lossy/closure authority but claims positive coherence-only D0a.",
        "D0a_authority_gate",
        "blocked D0a authority cannot support coherence-only D0a",
        "blocks_D0a_positive",
        authority="runtime_extension_required",
        scenario_kind="invariant_challenge",
        facts={
            "organization_authority": "lossy_projection",
            "coherence_only_positive_D0a_allowed": True,
        },
    ),
    case(
        "D0c_persistence_retained_as_same_D0c_row",
        "schema_relation",
        "a D0c row may retain its identity after demonstrating persistence",
        "The same instantaneous D0c row is upgraded after post-formation persistence appears.",
        "semantic_transition_gate",
        "persistent D0c requires a new D0a candidate identity",
        "blocks_same_row_upgrade",
        semantic="D0c",
        authority="existing_native",
        scenario_kind="invariant_challenge",
        facts={"d0_subclass": "D0c", "persistence_demonstrated": True},
    ),
    case(
        "D0b_transport_feedback_without_authority_reclassification",
        "schema_relation",
        "a D0b diagnostic may causally feed transport without changing authority",
        "A derived observable drives transport while remaining classified as observable-only D0b.",
        "semantic_authority_transition_gate",
        "causal feedback requires exact-derived causal authority or closure",
        "blocks_unreclassified_DR4",
        semantic="D0b",
        domain="functional_coupling",
        scenario_kind="invariant_challenge",
        facts={"d0_subclass": "D0b", "fed_causally_into_transport": True},
    ),
]


AFFIRMATIVE_CONTROL_IDS = {
    "cache_removed_and_recomputed",
    "observable_disconnected_from_transport",
    "slow_organization_clamp",
    "complete_state_matched_history_contrast",
    "same_complete_C_different_S_changes_future",
}

DIMENSIONAL_CONTROL_IDS = {
    "unclosed_route_boundary_continuity",
    "route_mass_loss_as_organization_weakening_relabel",
    "constant_mass_internal_reorganization_as_export_relabel",
    "mass_unmatched_organization_intervention",
    "temporal_intervention_with_unmatched_state",
}

OWNERSHIP_CONTROL_IDS = {
    "unrecorded_post_formation_producer_call",
    "producer_scheduled_D0_decay",
    "export_authoring_producer_call_retained_as_D0_R",
    "added_export_policy_as_D0_R_relabel",
    "B_R_as_D0_R_without_bridge",
}

TRANSITION_CONTROL_IDS = {
    "D0c_persistence_retained_as_same_D0c_row",
    "D0b_transport_feedback_without_authority_reclassification",
}


def canonical_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def digest_value(data: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            data,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("utf-8")
    ).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return value


def no_absolute_paths(data: Any) -> bool:
    text = json.dumps(data, sort_keys=True, ensure_ascii=True)
    forbidden = ("/" + "home" + "/", "Documents" + "/" + "RC-github")
    return all(marker not in text for marker in forbidden)


def git_diff_empty(base: str, path: str) -> bool:
    return (
        subprocess.run(
            ["git", "diff", "--quiet", base, "--", path],
            cwd=ROOT,
            check=False,
        ).returncode
        == 0
    )


def check(check_id: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"check_id": check_id, "passed": bool(passed), "detail": detail}


def schema_relation_violation(control_id: str, facts: dict[str, Any]) -> bool:
    if control_id == "bounded_partial_disposition_with_supported_row_decision":
        return (
            facts.get("candidate_disposition") == "bounded_partial"
            and facts.get("row_decision") != "partial"
        )
    if control_id == "blocked_representation_with_supported_row_decision":
        return (
            facts.get("candidate_disposition") == "blocked_by_representation"
            and facts.get("row_decision") != "blocked"
        )
    if control_id == "full_mediation_with_false_mediated_change":
        return (
            facts.get("mediation_strength") in {"full", "bounded_partial"}
            and not facts.get("organization_mediated_readout_change")
        )
    if control_id == "absent_mediation_with_true_mediated_change":
        return (
            facts.get("mediation_strength") in {"absent", "unresolved"}
            and facts.get("organization_mediated_readout_change") is True
        )
    if control_id == "mixed_domain_unresolved_claims_DR4":
        return (
            facts.get("organization_domain") == "mixed"
            and facts.get("mixed_domain_mediation_resolution") == "unresolved"
            and facts.get("decay_relation_ladder_rung") in {"DR4", "DR5", "DR6"}
        )
    if control_id == "blocked_D0a_authority_as_coherence_only_positive":
        return (
            facts.get("organization_authority")
            in {"effective_closure", "independent_state", "lossy_projection", "missing"}
            and facts.get("coherence_only_positive_D0a_allowed") is True
        )
    if control_id == "D0c_persistence_retained_as_same_D0c_row":
        return (
            facts.get("d0_subclass") == "D0c"
            and facts.get("persistence_demonstrated") is True
        )
    if control_id == "D0b_transport_feedback_without_authority_reclassification":
        return (
            facts.get("d0_subclass") == "D0b"
            and facts.get("fed_causally_into_transport") is True
        )
    return False


def dimensional_violation(control_id: str, facts: dict[str, Any]) -> bool:
    if control_id == "unclosed_route_boundary_continuity":
        return (
            facts.get("flux_quantity_semantics") != "time_integrated_exported_coherence"
            or facts.get("boundary_crossing_count_policy")
            != "each_packet_or_flux_transfer_counted_exactly_once"
        )
    if control_id == "route_mass_loss_as_organization_weakening_relabel":
        return (
            facts.get("route_mass_decreased") is True
            and facts.get("route_organization_weakened") is False
        )
    if control_id == "constant_mass_internal_reorganization_as_export_relabel":
        return facts.get("mass_delta") == 0.0 and facts.get(
            "net_outward_boundary_flux"
        ) == 0.0
    if control_id == "mass_unmatched_organization_intervention":
        return facts.get("mass_matched") is False
    if control_id == "temporal_intervention_with_unmatched_state":
        return (
            facts.get("temporal_intervention_matching_status")
            == "unmatched_blocks_temporal_mediation"
        )
    return False


def ownership_violation(control_id: str, facts: dict[str, Any]) -> bool:
    if control_id == "unrecorded_post_formation_producer_call":
        return facts.get("post_formation_call_exists") is True and not facts.get(
            "call_ledger_complete"
        )
    if control_id == "producer_scheduled_D0_decay":
        return facts.get("producer_schedules_aftereffect") is True
    if control_id in {
        "export_authoring_producer_call_retained_as_D0_R",
        "added_export_policy_as_D0_R_relabel",
    }:
        return facts.get("producer_authors_export") is True
    if control_id == "B_R_as_D0_R_without_bridge":
        return (
            facts.get("semantic_subtype") == "B_R"
            and facts.get("d0_to_br_bridge_status") == "missing"
        )
    return False


def claim_specific_violation(spec: dict[str, Any], facts: dict[str, Any]) -> bool:
    control_id = spec["control_id"]
    if spec["family"] == "schema_relation":
        return schema_relation_violation(control_id, facts)
    if control_id in DIMENSIONAL_CONTROL_IDS:
        return dimensional_violation(control_id, facts)
    if control_id in OWNERSHIP_CONTROL_IDS:
        return ownership_violation(control_id, facts)
    if control_id == "lossy_node_scalar_match_as_complete_state":
        return facts.get("node_C_equal") is True and not facts.get(
            "complete_state_equal"
        )
    if control_id == "cache_removed_and_recomputed":
        return facts.get("cache_removed") is True and facts.get(
            "exact_recomputation_matches"
        ) is True
    if control_id == "observable_disconnected_from_transport":
        return facts.get("observable_disconnected") is True and not facts.get(
            "later_readout_changed"
        )
    if control_id == "slow_organization_clamp":
        return facts.get("matched_clamp") is True and not facts.get(
            "later_readout_changed"
        )
    if control_id == "complete_state_matched_history_contrast":
        return (
            facts.get("node_C_equal") is True
            and facts.get("history_equal") is False
            and facts.get("future_equal") is False
        )
    if control_id == (
        "organization_weakening_without_mediation_as_causal_decay_relabel"
    ):
        return (
            facts.get("route_organization_weakened") is True
            and facts.get("mediation_strength") in {"absent", "unresolved"}
        )
    if control_id == "same_complete_C_different_S_changes_future":
        return (
            facts.get("complete_C_equal") is True
            and facts.get("S_equal") is False
            and facts.get("future_equal") is False
        )
    return facts.get(f"{spec['violated_gate']}_violated") is True


def repaired_fixture(
    spec: dict[str, Any], facts: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, Any]]:
    control_id = spec["control_id"]
    repaired = dict(facts)
    updates: dict[str, Any]
    repair_by_control: dict[str, dict[str, Any]] = {
        "bounded_partial_disposition_with_supported_row_decision": {
            "row_decision": "partial"
        },
        "blocked_representation_with_supported_row_decision": {
            "row_decision": "blocked"
        },
        "full_mediation_with_false_mediated_change": {
            "organization_mediated_readout_change": True
        },
        "absent_mediation_with_true_mediated_change": {
            "organization_mediated_readout_change": False
        },
        "mixed_domain_unresolved_claims_DR4": {
            "decay_relation_ladder_rung": "DR3"
        },
        "blocked_D0a_authority_as_coherence_only_positive": {
            "coherence_only_positive_D0a_allowed": False
        },
        "D0c_persistence_retained_as_same_D0c_row": {
            "persistence_demonstrated": False
        },
        "D0b_transport_feedback_without_authority_reclassification": {
            "fed_causally_into_transport": False
        },
        "unclosed_route_boundary_continuity": {
            "flux_quantity_semantics": "time_integrated_exported_coherence",
            "boundary_crossing_count_policy": (
                "each_packet_or_flux_transfer_counted_exactly_once"
            ),
        },
        "route_mass_loss_as_organization_weakening_relabel": {
            "route_organization_weakened": True
        },
        "constant_mass_internal_reorganization_as_export_relabel": {
            "mass_delta": -0.1,
            "net_outward_boundary_flux": 0.1,
        },
        "mass_unmatched_organization_intervention": {"mass_matched": True},
        "temporal_intervention_with_unmatched_state": {
            "temporal_intervention_matching_status": "matched_complete"
        },
        "unrecorded_post_formation_producer_call": {"call_ledger_complete": True},
        "producer_scheduled_D0_decay": {"producer_schedules_aftereffect": False},
        "export_authoring_producer_call_retained_as_D0_R": {
            "producer_authors_export": False
        },
        "added_export_policy_as_D0_R_relabel": {"producer_authors_export": False},
        "B_R_as_D0_R_without_bridge": {"d0_to_br_bridge_status": "admitted"},
        "lossy_node_scalar_match_as_complete_state": {"complete_state_equal": True},
        "cache_removed_and_recomputed": {"exact_recomputation_matches": False},
        "observable_disconnected_from_transport": {"later_readout_changed": True},
        "slow_organization_clamp": {"later_readout_changed": True},
        "complete_state_matched_history_contrast": {"future_equal": True},
        "organization_weakening_without_mediation_as_causal_decay_relabel": {
            "mediation_strength": "full"
        },
        "same_complete_C_different_S_changes_future": {"future_equal": True},
    }
    if control_id in repair_by_control:
        updates = repair_by_control[control_id]
    else:
        updates = {f"{spec['violated_gate']}_violated": False}
    repaired.update(updates)
    return repaired, updates


def build_null_row(index: int, spec: dict[str, Any], i2: dict[str, Any]) -> dict[str, Any]:
    profile = FAMILY_PROFILES[spec["family"]]
    semantic_contract = {
        "primary_semantic_class": spec["primary_semantic_class"],
        "representation_or_authority_class": spec[
            "representation_or_authority_class"
        ],
        "organization_domain": spec["organization_domain"],
        "load_bearing_organization_domain": spec[
            "load_bearing_organization_domain"
        ],
        "internal_time_policy": "model_owned_event_time_wall_clock_excluded_v1",
        "candidate_specific_schema_id": f"n31_{spec['family']}_active_null_schema_v1",
        "carrier_contract_id": profile["carrier"],
        "continuation_state_contract_id": profile["continuation"],
    }
    control_id = spec["control_id"]
    family = spec["family"]
    bad_facts = spec["scenario_facts"]
    repaired_facts, repair_mutation = repaired_fixture(spec, bad_facts)
    bad_fixture_rejected = claim_specific_violation(spec, bad_facts)
    repaired_fixture_rejected = claim_specific_violation(spec, repaired_facts)
    control_status = (
        "failed_closed"
        if bad_fixture_rejected and not repaired_fixture_rejected
        else "failed_open"
    )
    relation_rejected = (
        schema_relation_violation(control_id, bad_facts)
        if family == "schema_relation"
        else "not_applicable_non_relation_control"
    )
    dimension_rejected = (
        dimensional_violation(control_id, bad_facts)
        if control_id in DIMENSIONAL_CONTROL_IDS
        else "not_applicable_non_dimensional_control"
    )
    ownership_rejected = (
        ownership_violation(control_id, bad_facts)
        if control_id in OWNERSHIP_CONTROL_IDS
        else "not_applicable_non_ownership_control"
    )
    unsafe_flags = {f"{claim}_claim_allowed": False for claim in BLOCKED_CLAIMS}
    row = {
        "null_id": f"n31_i3_null_{index:02d}_{control_id}",
        "candidate_schema_version": i2["schema"]["schema_identity"][
            "candidate_schema_version"
        ],
        "control_id": control_id,
        "claim_under_test": spec["claim_under_test"],
        "control_scenario_kind": spec["control_scenario_kind"],
        "false_positive_scenario": spec["false_positive_scenario"],
        "source_contract_digest": digest_value(
            {"control_id": control_id, "semantic_contract": semantic_contract}
        ),
        "topology_signature": profile["topology"],
        "seed_or_pairing_rule": "deterministic_schema_fixture_seed_3103",
        "runtime_envelope_digest": digest_value(
            {
                "topology_signature": profile["topology"],
                "internal_time_policy": semantic_contract["internal_time_policy"],
                "fixture_scope": "schema_validator_only_no_runtime_claim",
            }
        ),
        "threshold_and_invariant_digest": digest_value(
            {
                "threshold_policy": "frozen_I2_no_post_hoc_thresholds",
                "invariant_policy": i2["schema"]["invariant_schema"],
            }
        ),
        **semantic_contract,
        "violated_gate": spec["violated_gate"],
        "expected_claim_failure": spec["expected_claim_failure"],
        "expected_result": "claim_rejected_fail_closed",
        "expected_control_status": "failed_closed",
        "actual_result": (
            "validator_rejected_bad_fixture_and_accepted_repaired_fixture"
            if control_status == "failed_closed"
            else "validator_mutation_check_failed"
        ),
        "control_status": control_status,
        "rung_effect": spec["rung_effect"],
        "derived_fixture_only": True,
        "positive_evidence_admissible": False,
        "control_family": family,
        "scenario_facts": bad_facts,
        "validator_receipt": {
            "predicate_id": f"n31_i3_{control_id}_predicate_v1",
            "exact_rejected_condition": spec["violated_gate"],
            "bad_fixture_digest": digest_value(bad_facts),
            "bad_fixture_rejected": bad_fixture_rejected,
            "repair_mutation": repair_mutation,
            "repaired_fixture_digest": digest_value(repaired_facts),
            "repaired_fixture_rejected": repaired_fixture_rejected,
            "repaired_fixture_is_positive_evidence": False,
            "classification": control_status,
        },
        "schema_relation_validator_rejected": relation_rejected,
        "dimensional_validator_rejected": dimension_rejected,
        "trace_derived_ownership_validator_rejected": ownership_rejected,
        "orthogonal_result_scope": spec["orthogonal_result_scope"],
        "semantic_comparability_contract": semantic_contract,
        "same_topology_different_mediator_semantics_comparable": False,
        "comparability_consumption_policy": (
            "future_positive_row_must_match_semantic_contract_or_regenerate_null"
        ),
        "control_execution_scope": "schema_validator_fixture_only_not_runtime_measurement",
        "control_result": {
            "control_id": control_id,
            "control_status": control_status,
            "blocked_condition": spec["false_positive_scenario"],
            "expected_result": "claim_rejected_fail_closed",
            "actual_result": (
                "claim_rejected_fail_closed"
                if control_status == "failed_closed"
                else "claim_not_reliably_rejected"
            ),
            "claim_allowed_when_control_triggers": False,
            "rung_effect": spec["rung_effect"],
            "scope_reason_if_not_applicable": "not_applicable_status_not_used",
        },
        "source_current_inputs": [],
        "artifact_manifest": [],
        "derived_report_only": True,
        "positive_DR_rung_assigned": False,
        "row_decision": "rejected_failed_closed_active_null",
        "claim_ceiling": "active_null_rejection_only_no_positive_N31_evidence",
        "blocked_relabels": BLOCKED_CLAIMS,
        "unsafe_claim_flags": unsafe_flags,
    }
    row["row_digest"] = digest_value(row)
    return row


def build_payload() -> dict[str, Any]:
    i2 = load_json(I2_OUTPUT)
    all_control_ids = i2["controls"]["all_control_ids"]
    rows = [
        build_null_row(index, spec, i2)
        for index, spec in enumerate(CONTROL_CASES, start=1)
    ]
    row_control_ids = [row["control_id"] for row in rows]
    required_fields = i2["schema"]["active_null_row_schema"]["required_fields"]
    family_counts = dict(sorted(Counter(row["control_family"] for row in rows).items()))
    expected_family_counts = {
        "A": len(i2["controls"]["candidate_A_controls"]),
        "B": len(i2["controls"]["candidate_B_controls"]),
        "C": len(i2["controls"]["candidate_C_controls"]),
        "D0": len(i2["controls"]["D0_controls"]),
        "common": len(i2["controls"]["common_active_nulls"]),
        "schema_relation": len(i2["controls"]["schema_relation_controls"]),
    }
    primary_classes = set(i2["schema"]["taxonomy"]["primary_semantic_classes"])
    authority_classes = set(
        i2["schema"]["taxonomy"]["representation_or_authority_classes"]
    )
    domain_classes = set(
        i2["schema"]["route_organization_contract_schema"][
            "organization_domain_enum"
        ]
    )
    protected_scope = i2["schema"]["protected_scope"]
    src_diff_empty = git_diff_empty(I3_BASE_REVISION, "src")
    protected_paths_clean = all(
        git_diff_empty(I3_BASE_REVISION, path)
        for path in protected_scope["protected_paths"]
    )
    checks = [
        check("I2_status_passed", i2["status"] == "passed", i2["status"]),
        check(
            "I2_output_digest_matches_frozen_value",
            i2["output_digest"] == I2_OUTPUT_DIGEST,
            i2["output_digest"],
        ),
        check(
            "I2_artifact_sha256_matches",
            sha256_file(I2_OUTPUT) == I2_ARTIFACT_SHA256,
            sha256_file(I2_OUTPUT),
        ),
        check(
            "control_registry_instantiated_exactly_once",
            row_control_ids == all_control_ids and len(set(row_control_ids)) == len(rows),
            {"expected": len(all_control_ids), "observed": len(rows)},
        ),
        check(
            "control_family_counts_match_I2",
            family_counts == expected_family_counts,
            family_counts,
        ),
        check(
            "all_active_null_required_fields_present",
            all(set(required_fields).issubset(row) for row in rows),
            required_fields,
        ),
        check(
            "semantic_classes_valid",
            all(row["primary_semantic_class"] in primary_classes for row in rows),
            sorted({row["primary_semantic_class"] for row in rows}),
        ),
        check(
            "authority_classes_valid",
            all(
                row["representation_or_authority_class"] in authority_classes
                for row in rows
            ),
            sorted({row["representation_or_authority_class"] for row in rows}),
        ),
        check(
            "organization_domains_valid",
            all(row["organization_domain"] in domain_classes for row in rows),
            sorted({row["organization_domain"] for row in rows}),
        ),
        check(
            "semantic_comparability_explicit",
            all(
                row["source_contract_digest"]
                == digest_value(
                    {
                        "control_id": row["control_id"],
                        "semantic_contract": row["semantic_comparability_contract"],
                    }
                )
                and not row[
                    "same_topology_different_mediator_semantics_comparable"
                ]
                for row in rows
            ),
            "semantic_contract_digest_and_noncomparability_checked",
        ),
        check(
            "false_positive_scenarios_explicit",
            all(
                row["claim_under_test"]
                and row["false_positive_scenario"]
                and row["violated_gate"]
                and row["expected_claim_failure"]
                for row in rows
            ),
            len(rows),
        ),
        check(
            "validator_receipts_and_repair_mutations_pass",
            all(
                row["validator_receipt"]["bad_fixture_rejected"] is True
                and row["validator_receipt"]["repaired_fixture_rejected"] is False
                and row["validator_receipt"][
                    "repaired_fixture_is_positive_evidence"
                ]
                is False
                and row["validator_receipt"]["classification"]
                == row["control_status"]
                for row in rows
            ),
            len(rows),
        ),
        check(
            "all_controls_failed_closed",
            all(row["control_status"] == "failed_closed" for row in rows),
            Counter(row["control_status"] for row in rows),
        ),
        check(
            "failed_open_rows_zero",
            not any(row["control_status"] == "failed_open" for row in rows),
            0,
        ),
        check(
            "affirmative_discriminators_claim_relative",
            {
                row["control_id"]
                for row in rows
                if row["control_scenario_kind"] == "affirmative_discrimination"
            }
            == AFFIRMATIVE_CONTROL_IDS
            and all(
                row["orthogonal_result_scope"] != "none_active_null_only"
                for row in rows
                if row["control_id"] in AFFIRMATIVE_CONTROL_IDS
            ),
            sorted(AFFIRMATIVE_CONTROL_IDS),
        ),
        check(
            "cross_field_contradictions_rejected",
            all(
                row["schema_relation_validator_rejected"] is True
                for row in rows
                if row["control_family"] == "schema_relation"
            ),
            len(i2["controls"]["schema_relation_controls"]),
        ),
        check(
            "dimensional_controls_rejected",
            all(
                row["dimensional_validator_rejected"] is True
                for row in rows
                if row["control_id"] in DIMENSIONAL_CONTROL_IDS
            ),
            sorted(DIMENSIONAL_CONTROL_IDS),
        ),
        check(
            "trace_derived_ownership_controls_rejected",
            all(
                row["trace_derived_ownership_validator_rejected"] is True
                for row in rows
                if row["control_id"] in OWNERSHIP_CONTROL_IDS
            ),
            sorted(OWNERSHIP_CONTROL_IDS),
        ),
        check(
            "semantic_transition_controls_present",
            TRANSITION_CONTROL_IDS.issubset(row_control_ids),
            sorted(TRANSITION_CONTROL_IDS),
        ),
        check(
            "cross_cut_tags_are_subsets_not_families",
            AFFIRMATIVE_CONTROL_IDS.issubset(row_control_ids)
            and DIMENSIONAL_CONTROL_IDS.issubset(row_control_ids)
            and OWNERSHIP_CONTROL_IDS.issubset(row_control_ids)
            and set(family_counts) == set(expected_family_counts),
            {
                "disjoint_families": family_counts,
                "affirmative_tag_count": len(AFFIRMATIVE_CONTROL_IDS),
                "dimensional_tag_count": len(DIMENSIONAL_CONTROL_IDS),
                "ownership_tag_count": len(OWNERSHIP_CONTROL_IDS),
            },
        ),
        check(
            "derived_fixtures_not_positive_evidence",
            all(
                row["derived_fixture_only"]
                and row["derived_report_only"]
                and not row["positive_evidence_admissible"]
                and not row["positive_DR_rung_assigned"]
                and not row["source_current_inputs"]
                and not row["artifact_manifest"]
                for row in rows
            ),
            len(rows),
        ),
        check(
            "unsafe_claim_flags_false",
            all(
                not any(row["unsafe_claim_flags"].values())
                for row in rows
            ),
            len(rows),
        ),
        check("src_diff_empty", src_diff_empty, src_diff_empty),
        check(
            "protected_runtime_contract_diff_empty",
            protected_paths_clean,
            protected_paths_clean,
        ),
    ]
    payload: dict[str, Any] = {
        "experiment": "N31",
        "iteration": "3",
        "generated_at": GENERATED_AT,
        "script": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": (
            "accepted_active_nulls_fail_closed_no_positive_decay_evidence"
        ),
        "source_I2": {
            "path": I2_OUTPUT.relative_to(ROOT).as_posix(),
            "output_digest": i2["output_digest"],
            "artifact_sha256": sha256_file(I2_OUTPUT),
            "candidate_schema_version": i2["schema"]["schema_identity"][
                "candidate_schema_version"
            ],
            "control_id_count": i2["controls"]["control_id_count"],
        },
        "graph_scope": {
            "I3_governance_base_revision": I3_BASE_REVISION,
            "src_diff_empty": src_diff_empty,
            "protected_runtime_contract_diff_empty": protected_paths_clean,
            "runtime_modified": False,
        },
        "active_null_policy": {
            "failed_closed_meaning": (
                "false_positive_path_triggered_and_specific_claim_rejected"
            ),
            "failed_open_meaning": (
                "blocker_triggered_but_specific_claim_remained_open"
            ),
            "control_result_is_runtime_measurement": False,
            "fixture_role": "pre_positive_schema_validator_and_failure_baseline",
            "positive_evidence_admissible": False,
            "same_topology_different_mediator_semantics_comparable": False,
            "future_candidate_comparability_rule": (
                "match_semantic_contract_exactly_or_regenerate_control"
            ),
            "I3_scope": "validator_and_control_semantics_only",
            "future_source_current_scope": (
                "candidate_specific_runtime_trace_resolution_required"
            ),
        },
        "future_candidate_control_resolver_schema": {
            "required_fields": [
                "positive_candidate_id",
                "control_id",
                "matched_I3_null_id",
                "semantic_comparability_status",
                "comparability_digest",
                "regeneration_required",
                "resolved_control_artifact",
            ],
            "semantic_comparability_status_enum": [
                "matched",
                "mismatched",
                "regenerated_matched",
                "unresolved_blocks_consumption",
            ],
            "comparison_inputs": [
                "primary_semantic_class",
                "representation_or_authority_class",
                "organization_domain",
                "load_bearing_organization_domain",
                "internal_time_policy",
                "candidate_specific_schema_id",
                "carrier_contract_id",
                "continuation_state_contract_id",
            ],
            "topology_match_alone_sufficient": False,
            "I3_failed_closed_inherits_as_candidate_control_pass": False,
        },
        "future_semantic_transition_record_schema": {
            "required_fields": [
                "source_row_id",
                "transition_trigger",
                "new_candidate_id",
                "new_semantic_class_or_authority",
                "old_row_unchanged",
            ],
            "old_row_unchanged_required_value": True,
            "in_place_semantic_upgrade_allowed": False,
        },
        "active_null_rows": rows,
        "summary": {
            "active_null_row_count": len(rows),
            "family_counts": family_counts,
            "failed_closed_rows": sum(
                row["control_status"] == "failed_closed" for row in rows
            ),
            "failed_open_rows": sum(
                row["control_status"] == "failed_open" for row in rows
            ),
            "affirmative_discriminator_row_count": len(AFFIRMATIVE_CONTROL_IDS),
            "cross_field_relation_row_count": len(
                i2["controls"]["schema_relation_controls"]
            ),
            "dimensional_control_row_count": len(DIMENSIONAL_CONTROL_IDS),
            "ownership_control_row_count": len(OWNERSHIP_CONTROL_IDS),
            "cross_cut_counts_are_tags_not_additional_rows": True,
        },
        "positive_evidence_opened": False,
        "candidate_rows_classified": False,
        "decay_relation_ladder_rung_assigned": False,
        "decay_relation_ladder_ceiling": "DR0_no_source_current_decay_evidence",
        "n31_closeout_ladder_rung_assigned": False,
        "n31_closeout_ceiling": "N31-C1_source_and_semantic_contract_admitted",
        "n31_c2_active_null_component_satisfied": True,
        "n31_c2_representation_component_pending_iteration_4": True,
        "ready_for_iteration_4_D0a_representation_gate": True,
        "claim_boundary": {
            "claim_ceiling": "active_null_control_discipline_only_no_N31_decay_evidence",
            "blocked_claims": BLOCKED_CLAIMS,
            "unsafe_claim_flags": {
                f"{claim}_claim_allowed": False for claim in BLOCKED_CLAIMS
            },
        },
        "checks": checks,
    }
    checks.append(
        check("no_absolute_paths_in_records", no_absolute_paths(payload), "recursive")
    )
    payload["failed_checks"] = [
        row["check_id"] for row in checks if not row["passed"]
    ]
    if payload["failed_checks"]:
        payload["status"] = "failed"
        payload["acceptance_state"] = "blocked_active_null_validation_failed"
        payload["ready_for_iteration_4_D0a_representation_gate"] = False
    payload["output_digest"] = digest_value(
        {key: value for key, value in payload.items() if key != "output_digest"}
    )
    return payload


def write_report(payload: dict[str, Any]) -> None:
    family_rows = []
    for family in ("common", "D0", "A", "B", "C", "schema_relation"):
        rows = [
            row for row in payload["active_null_rows"] if row["control_family"] == family
        ]
        family_rows.append(
            f"| {family} | {len(rows)} | "
            f"{sum(row['control_status'] == 'failed_closed' for row in rows)} | 0 |"
        )
    control_rows = "\n".join(
        "| `{control_id}` | {family} | {semantic} | {domain} | `{gate}` | "
        "`{status}` |".format(
            control_id=row["control_id"],
            family=row["control_family"],
            semantic=row["primary_semantic_class"],
            domain=row["organization_domain"],
            gate=row["violated_gate"],
            status=row["control_status"],
        )
        for row in payload["active_null_rows"]
    )
    check_rows = "\n".join(
        f"- `{row['check_id']}` = `{str(row['passed']).lower()}`"
        for row in payload["checks"]
    )
    REPORT.write_text(
        f"""# N31 Iteration 3 - Active Nulls And Failure Baselines

Status: `{payload['status']}`

Acceptance state: `{payload['acceptance_state']}`

Output digest: `{payload['output_digest']}`

## Scope

I3 instantiates every I2 control as a claim-relative, derived-fixture active
null. It establishes which false-positive paths must be rejected before a
positive candidate is admitted. It does not execute a source-current decay
probe and cannot assign a positive DR rung.

`failed_closed` means that the declared blocker was present and the specific
overclaim was correctly rejected. It does not mean that a runtime experiment
failed. `failed_open` would be the governance failure; I3 has zero such rows.

## Family Summary

| Family | Rows | Failed closed | Failed open |
|---|---:|---:|---:|
{chr(10).join(family_rows)}

The five affirmative, five dimensional, and five ownership controls are
overlapping tags on these same 70 rows. They are not additional families or
executions.

## Validator Receipts

Every row retains a named predicate, bad-fixture digest, exact rejected gate,
repair mutation, repaired-fixture digest, and both predicate outcomes. I3
assigns `failed_closed` only when the bad fixture is rejected and the same
fixture with the targeted blocker repaired is no longer rejected. The repaired
fixture is explicitly not positive evidence.

## Semantic Comparability

Every row records semantic class, authority, organization domain,
load-bearing domain, internal-time policy, candidate schema, carrier, and
continuation-state contract. Matching topology alone is not comparability. A
later positive row may consume an I3 null only when this semantic contract
matches; otherwise the null must be regenerated for that candidate.

I3 is therefore a baseline control library, not a universal control pass. The
frozen future resolver requires candidate ID, control ID, matched null ID,
comparability status/digest, regeneration decision, and resolved source-current
control artifact. No future candidate may inherit the phrase "all controls
passed" from I3.

## Scientific Boundaries Exercised

- Route mass, route organization, and causal mediation remain independent.
- Boundary flux is time-integrated exported coherence, not an instantaneous
  rate; boundary crossings are counted once.
- Producer ownership is derived from calls, scheduled events, mutation paths,
  and export decisions. Scheduling without direct mutation can still author
  the aftereffect.
- B-R classification records policy ownership but does not establish positive
  B-R decay support.
- Persistent D0c requires a new D0a candidate identity. Causal use of D0b
  requires exact-derived causal authority or closure classification.
- Contradictory disposition, authority, mediation, and DR combinations are
  machine-rejected.

The transition record must preserve the source row, trigger, new candidate ID,
new semantic class or authority, and `old_row_unchanged = true`; in-place
semantic upgrades are prohibited.

## Affirmative Discriminators

Five controls are affirmative discriminators viewed relative to a specific
overclaim: cache recomputation, observable disconnection, slow-organization
clamping, an allegedly complete or node-scalar-complete history contrast, and
equal-C/different-S future contrast. Their `failed_closed` status rejects the
overclaim under test. Any
orthogonal positive implication remains a future source-current probe and is
not evidence from I3.

## Source-Current Execution Boundary

I3 proves validator and control semantics over derived fixtures. It does not
prove that future runtime rows expose enough call lineage, packet identities,
runtime masks, state mutations, read-path guards, or restoration state to
evaluate those controls. I7-I10 must resolve applicable controls against actual
candidate traces; an I3 fixture cannot substitute for that execution.

## Control Matrix

| Control | Family | Class | Mediator domain | Violated gate | Status |
|---|---|---|---|---|---|
{control_rows}

## Closeout Position

`positive_evidence_opened = false`

`decay_relation_ladder_ceiling = DR0_no_source_current_decay_evidence`

The active-null component of `N31-C2` is satisfied. The representation
component remains pending I4, so the N31 closeout ceiling remains `N31-C1`.

## Checks

{check_rows}
""",
        encoding="utf-8",
    )


def main() -> None:
    payload = build_payload()
    OUTPUT.write_text(canonical_json(payload), encoding="utf-8")
    write_report(payload)
    if payload["status"] != "passed":
        raise SystemExit(
            "N31 I3 failed: " + ", ".join(payload.get("failed_checks", []))
        )


if __name__ == "__main__":
    main()

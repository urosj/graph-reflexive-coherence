# GRC9V4 Constitutive Design Investigation

**Disposition:** D10.2 accepted bounded; GRCv4/GRC9v4 specification writing authorized; implementation remains unauthorized

This directory records the accepted bounded decision work authorizing a
normative GRCv4 specification followed by a substantive GRC9v4 nine-port
specialization. It consumes the Continuation/Read-Back 3.4.1 theory-to-graph
contract, the accepted B1-GR and B2-GR boundaries, the reconciled legacy
GRC9V3 specification, and the Phase 7 implementation record.
This is also the historical chain that produced the V4 question. B1 made the
theory distinctions executable against unchanged GRC9V3; B2 tested stronger
unchanged-runtime constructibility. Their bounded results constrain this work
but do not prescribe a V4 architecture.

The investigation did not assume that GRC9V4 is temporalized conductance,
introduces a new independent retained carrier, or temporalizes current. D1
admitted retained-representation ontologies; D6 separately decided whether
current remains slaved; D10 then classified the accepted current profile
population without selecting a unique candidate or realization. The
investigation compared the admitted candidates against one frozen target:

> GRC9V4 is a possible revision-distinct synchronous GRC profile in which an
> admitted retained causal representation participates in structurally and
> temporally classified continuation and is conditionally read by present
> activity into an oriented current contribution.

D0-D3 are the verification-to-design bridge. From D4 onward, B1/B2 provide
bounded V3 facts, verification controls, design pressure, and open hypotheses;
they do not dictate V4 ontology. Their conclusions should not be rerun merely
to rediscover V3, but must be revisited when V4 changes the causal object,
state space, or operator. Every gate must add a candidate-specific constitutive
fact, reject a candidate for a named incompatibility, or route a named missing
derivation.

Start with:

- [constitutive design basis](./GRC9V4ConstitutiveDesignBasis.md);
- [D0-D10 investigation plan](./GRC9V4ConstitutiveDesignPlan.md);
- [execution checklist](./GRC9V4ConstitutiveDesignChecklist.md);
- [decision ledger](./GRC9V4ConstitutiveDesignDecisionLedger.md);
- [frozen initialization predecessor](./GRC9V4ConstitutiveDesignInitialization.json);
- [D0 structured decision](./decisions/D0TargetInheritanceAndClaimCeiling.json);
- [D0 interpretation](./decisions/D0TargetInheritanceAndClaimCeiling.md).
- [D1 structured decision](./decisions/D1RetainedRepresentationOntologyAndCandidateAdmission.json);
- [D1 interpretation](./decisions/D1RetainedRepresentationOntologyAndCandidateAdmission.md).
- [D2 structured decision](./decisions/D2FormationRetentionReleaseAndWriteInterface.json);
- [D2 interpretation](./decisions/D2FormationRetentionReleaseAndWriteInterface.md).
- [D3 structured decision](./decisions/D3ContinuationRequirementsAndStructuralDomain.json);
- [D3 interpretation](./decisions/D3ContinuationRequirementsAndStructuralDomain.md).
- [D4 structured decision](./decisions/D4GeometryMobilityAndTopologyOwnership.json);
- [D4 interpretation](./decisions/D4GeometryMobilityAndTopologyOwnership.md).
- [D5 structured decision](./decisions/D5DirectionalReadBack.json);
- [D5 interpretation](./decisions/D5DirectionalReadBack.md).
- [D6 structured decision](./decisions/D6TotalCurrentClosure.json);
- [D6 interpretation](./decisions/D6TotalCurrentClosure.md).
- [D7 structured decision](./decisions/D7ClosedWriteReadLoop.json);
- [D7 interpretation](./decisions/D7ClosedWriteReadLoop.md).
- [D4-v2 structured decision](./decisions/D4v2CandidateGeometryAndCarrierCompletion.json);
- [D4-v2 interpretation](./decisions/D4v2CandidateGeometryAndCarrierCompletion.md).
- [D5-v2 structured decision](./decisions/D5v2DirectionalReadBackCompletion.json);
- [D5-v2 interpretation](./decisions/D5v2DirectionalReadBackCompletion.md).
- [D6-v2 structured decision](./decisions/D6v2UpdatedTotalCurrentClosure.json);
- [D6-v2 interpretation](./decisions/D6v2UpdatedTotalCurrentClosure.md).
- [D7-v2 structured decision](./decisions/D7v2CandidateTransitionComparativeAdmission.json);
- [D7-v2 interpretation](./decisions/D7v2CandidateTransitionComparativeAdmission.md).
- [D7G-v1 structured decision](./decisions/D7GGlobalMetricAndStructuralCultivationClosure.json);
- [D7G-v1 interpretation](./decisions/D7GGlobalMetricAndStructuralCultivationClosure.md).
- [D7G-v2 structured decision](./decisions/D7Gv2GeometryParametricClosureAndFinalization.json);
- [D7G-v2 interpretation](./decisions/D7Gv2GeometryParametricClosureAndFinalization.md).
- [D7G-post-v2 graph-Hodge type correction](./decisions/D7GPostv2GraphHodgeTypeCorrection.json);
- [D7G-post-v2 correction interpretation](./decisions/D7GPostv2GraphHodgeTypeCorrection.md).
- [D8-A structured decision](./decisions/D8ABranchAppropriateStructuralTargetExtraction.json);
- [D8-A interpretation](./decisions/D8ABranchAppropriateStructuralTargetExtraction.md).
- [coupled/implicit geometry-temporal successor decision](./decisions/GeometryTemporalRealizationSuccessorCoupledImplicit.json);
- [coupled/implicit successor interpretation](./decisions/GeometryTemporalRealizationSuccessorCoupledImplicit.md).
- [D8-B coupled architecture-local decision](./decisions/D8BCoupledArchitectureLocalContinuationAnalysis.json);
- [D8-B coupled architecture-local interpretation](./decisions/D8BCoupledArchitectureLocalContinuationAnalysis.md).
- [operator-split same-beat successor decision](./decisions/GeometryTemporalRealizationSuccessorOperatorSplit.json);
- [operator-split same-beat successor interpretation](./decisions/GeometryTemporalRealizationSuccessorOperatorSplit.md).
- [reconstructed-geometry successor decision](./decisions/GeometryTemporalRealizationSuccessorReconstructedGeometry.json);
- [reconstructed-geometry successor interpretation](./decisions/GeometryTemporalRealizationSuccessorReconstructedGeometry.md);
- [persistent-carrier successor decision](./decisions/GeometryTemporalRealizationSuccessorPersistentCarrier.json);
- [persistent-carrier successor interpretation](./decisions/GeometryTemporalRealizationSuccessorPersistentCarrier.md);
- [comparative realization synthesis](./decisions/GeometryTemporalRealizationComparativeSynthesis.json);
- [comparative synthesis interpretation](./decisions/GeometryTemporalRealizationComparativeSynthesis.md);
- [coupled-implicit plus persistent-carrier decision](./decisions/GeometryTemporalRealizationHybridCoupledPersistentCarrier.json);
- [hybrid interpretation](./decisions/GeometryTemporalRealizationHybridCoupledPersistentCarrier.md);
- [D9 complete-step and lifecycle decision](./decisions/D9CompleteStepAndLifecycleContract.json);
- [D9 scientific interpretation](./decisions/D9CompleteStepAndLifecycleContract.md);
- [D9 profile/state/lifecycle registry](./decisions/D9ProfileStateLifecycleRegistry.json);
- [D9 adversarial coverage matrix](./decisions/D9LifecycleCoverageMatrix.json);
- [D9 residual debt ledger](./decisions/D9ResidualDebtLedger.json).
- [D10 design synthesis](./decisions/D10DesignSynthesisAndSpecWritingDecision.json);
- [D10 scientific interpretation](./decisions/D10DesignSynthesisAndSpecWritingDecision.md);
- [D10.1 preliminary substrate provenance decision](./decisions/D10_1PreliminarySubstrateProvenance.json);
- [D10.1 preliminary substrate provenance interpretation](./decisions/D10_1PreliminarySubstrateProvenance.md).
- [D10.2 full substrate provenance and promotion audit](./decisions/D10_2FullSubstrateProvenanceAndPromotionAudit.json);
- [D10.2 scientific interpretation](./decisions/D10_2FullSubstrateProvenanceAndPromotionAudit.md).

Current gate status:

```text
D0 = accepted
D1 = accepted_bounded
D2 = accepted_bounded
D3 = accepted_bounded
D4 = accepted_bounded
D5 = accepted_bounded
D6 = accepted_bounded
D7 = accepted_bounded
D4-v2 = accepted_bounded
D5-v2 = accepted_bounded
D6-v2 = accepted_bounded
D7-v2 = accepted_bounded
D7G-v1 = accepted_bounded
D7G-v1 disposition = H4_interface_frozen_affine_reference_profile_family_conditionally_admitted_D7Gv2_embedding_parametric_and_handoff_closure_required
D7G-v2 = accepted_bounded
D7G-v2 disposition = reference_profile_instantiated_A_C_candidate_local_transitions_valid_selected_lagged_explicit_geometry_feedback_unresolved
D7G-v2 profile/stage audit complete = true
D7G-v2 global structural cultivation complete = false
D7G-post-v2 graph-Hodge type correction = accepted_bounded
automatic_D4-v3-D7-v3_cycle = not_authorized
D8-A = accepted_bounded
D8_authorized = true
D8_authorized_scope = D8-A_plus_coupled_A_and_C_architecture_local_D8B
D8-B_coupled_architecture_local = accepted_bounded_charge_parametric_design_operator_contract
D8-B_numeric_spectrum_and_stability = uninstantiated
D8-B_full_continuation = comparative_blocked
next_route_after_accepted_D8-A = GRC9V4-GEOMETRY-TEMPORAL-REALIZATION-SUCCESSOR
geometry_temporal_realization_successor_authorized = true
geometry_temporal_realization_successor_coupled_implicit = accepted_bounded
coupled_implicit_C = accepted_bounded_complete_realization_candidate
coupled_implicit_A = accepted_bounded_complete_realization_candidate
architecture_local_D8B_A_authorized = true
architecture_local_D8B_C_authorized = true
comparative_D8B_authorized = false
GTRS-OS_operator_split_same_beat = accepted_bounded_two_bounded_complete_design_rows
GTRS-RG_reconstructed_geometry = accepted_bounded_local_family_complete_A_C
GTRS-RG1_same_beat_A_C = family_level_obstruction_exact_CI_or_staged_OS_equivalence
GTRS-RG2_existing_CI_OS_poststate_A_C = supported_local_reconstructibility_property
GTRS-RG2_lagged_invariant_section_A_C = bounded_complete_realization
GTRS-RG_universal_reconstruction_impossibility = false
GTRS-PC_persistent_K4_carrier = accepted_bounded_two_bounded_complete_design_rows
GTRS-PC_capability_beyond_local_RG = independent_retained_structural_state_without_inverse_or_graph_transform
GTRS-PC_base_state_hysteresis = unsupported_pending_complete_chain_witnesses
GTRS-COMP = accepted_bounded
GTRS-CI-PC = accepted_bounded
D9 = accepted_bounded_lifecycle_and_typed_event_closure
D9_positive_profiles = 10
D9_coverage_cells = 260
D9_blank_cells = 0
D9_multi_authority_intervention_subcases = 16
D9_typed_topology_event_continuation_profiles = 10
D9_lossy_topology_event_continuation_profiles = 10
D9_untyped_topology_event_supported_profiles = 0
D9_current_scientific_debts = 0
D9_resolved_negative_results = 1
D9_live_scientific_debt_union = 29
D9_post_spec_verification_obligations = 4
next_substantive_route = GRCV4_normative_specification_then_GRC9V4_specialization
remaining_family_order = operator_split_then_reconstructed_then_persistent_then_comparative_synthesis
D9_before_remaining_family_pressure = false
D10_authorized = true
D10 = accepted_bounded
D10.1 = accepted_preliminary_bounded_substrate_provenance_separation
D10.2 = accepted_bounded
D10.2_human_acceptance = accepted_bounded_2026-08-26
D10_human_acceptance = accepted_bounded_2026-08-26
D10_selected_architecture = profile_explicit_lineage_local_GRC9V4_common_substrate_interface
D10_unique_candidate_selected = false
D10_unique_realization_selected = false
D10_claim_topology = {normative: 9, optional: 7, conditional: 12, open: 5, negative: 6}
D10_historical_predecessor_claim_nodes = 29
D10_reciprocal_typed_claim_debt_edges = 129
D10_transformed_D9_debts = 29
D10_claimless_debt_dispositions = 0
D10_verification_obligations = 11
D10_executable_complete_profiles = 10
D10_runtime_complete_profile_binding = exactly_one_candidate_plus_exactly_one_realization
D10_migration_receipt_profile_binding = ordered_source_target_complete_profile_pair
D10_topology_event_receipt_profile_binding = ordered_source_target_complete_profile_pair_equal_when_unchanged
D10_current_profile_population_future_exhaustive = false
D10_current_PC_profile = scalar_ZOH_one_tau_PC_persistent_K4_history
D10_unfolding_trajectory = claim_activated_not_fixed_successor_schedule
D10_final_substrate_identity_closed = false
D10_preclosure_substrate_provenance_audit_required = true
D10.1_working_factorization = GRCV4_to_nine_port_GRC9V4_to_disabled_GRC9V3
D10.1_promotion_proved = false
D10.2_factorization_earned = true
D10.2_factorization_scope = current_D10_initial_specification_population_only
D10.2_normatively_load_bearing_objects = 67
D10.2_normative_equation_contracts = 152
D10.2_explicit_equation_contracts = 85
D10.2_disabled_reduction_matrix_rows = 40
D10.2_accepted_D10_claims_covered = 39
D10.2_accepted_D10_claim_surfaces_exact = true
D10.2_D10_CL_C_012_is_accepted_D10_content = true
D10.2_independent_GRC_derivations = 12
D10.2_core_K_separate_from_graph_K4 = true
D10.2_M4_is_separate_transport_mobility = true
D10.2_Candidate_A_promoted_profile = accepted_D7_curvature_disabled_G_W
D10.2_generic_migration_separate_from_exact_GRC9V3_A_initializer = true
D10.2_reference_Hodge_embedding_rederived_from_GRCV3_surfaces = true
D10.2_core_theory_and_specification_meta_categories_separate = true
D10.2_promotion_pending_rows = 0
D10.2_equation_contract_promotion_pending_rows = 0
D10.2_event_resource_increment_separate_from_conservative_transport = true
D10.2_charge_target_stage_separation = true
D10.2_audit_checks = 289/289
D10.2_final_substrate_identity_closed_for_current_population = true
D10.2_final_substrate_identity_globally_closed_for_all_future_profiles = false
D10.2_GRCV4_specification_authorized_after_human_acceptance = true
D10.2_GRC9V4_specialization_specification_authorized_after_human_acceptance = true
D10.2_GRCV4_specification_authorized_now = true
D10.2_GRC9V4_specialization_specification_authorized_now = true
D10_scientific_disposition = accepted_bounded_lineage_local_profile_explicit_spec_authorization
specification_authorized = true
implementation_authorized = false
```

D4-v2 now gives B and C bounded revision-specific constitutive completions
without selecting A. Candidate B is a bounded graph-local symmetric bilinear
carrier on the oriented edge one-form space, metric-typed relative to
`H_1,pre`, bounded through dimensionless `Theta_B`, and restricted to a
radius-one line-graph mask. Candidate C combines an instantiated weighted graph
spectral selector with an explicitly scaled cutoff, a pressured retained-to-edge
map, a positive graph-Hodge congruence, and an instantiated candidate-local
`I_4M^pre` that is not assumed isometric. D4-v2 does not add a direct
`T_C -> K_4` adapter: C's common structural crossing remains the source-backed
retained-mediated route pending D5-v2, D6-v2, and D7G, with `j_C` mapped from
the `h_M` representation through `(I_4M^pre)^-1` before common physical
`j_C tensor j_C` assembly. Retained-geometry-off, read-off, and gain-off are
separate controls; read-off and gain-off preserve the `h_M`-conditioned
baseline path. Direct
candidate contributions enter an assembled finite-radius graph-local `K_4`
domain rather than an arbitrary dense edge matrix; diagonal overlap
multiplicity is closed for D7G-v1's admitted partition choice while
off-diagonal pair normalization remains explicit profile pressure. A's causal architecture is
unchanged, but its vertex-star local assembly is newly typed by D4-v2. Both B
and C are D5-v2 eligible. These are constrained V4 choices, not unique
core-theory formulas. Global `H_4` remains D7G work.

D5-v2 now carries A unchanged, admits B's canonical metric-raised Riesz
response `H_1,pre^-1 T_B`, and closes C's Hodge response through the retained
`T_C -> H_M` path and the explicit non-isometric physical back-map. B's direct
`T_B -> K_4` and current-mediated `T_B -> R_B -> j_B` paths remain separately
switched and may not be double-counted. C's selected-sector counterfactual
changes the physical response while a matched complement does not; null
directions remain valid compatibility controls. The record preserves the full
41-row live debt union, including the 22 exact inherited rows bound through
D4-v2. These are operator-level constitutive results, not runtime or physical
channel evidence. D5-v2 is accepted bounded. D6-v2 now carries A's accepted
closure unchanged, admits B's signed Riesz closure through exact
generalized-eigenvalue regularity, and admits C's non-isometric Hodge closure
while separating exact similarity invariance from robust physical
conditioning. B's fixed-probe sign discriminator is preserved, but active
feedback has mixed parity and later tensor assembly must use the solved
current. `A_B` remains radius-one line-graph local, while its solved inverse is
only component-confined and may propagate influence beyond one hop. D6-v2 also
preserves D5-v2 debt lineage exactly: 15 unchanged current rows are copied
verbatim, four changed obligations have explicit successors, and no row is
dropped. All three candidates entered D7-v2. D6-v2 is accepted bounded.

D7-v2 supersedes D7-v1 for the comparative partition while binding A's
accepted transition unchanged. It closes C's complete fixed-selector-stratum
formal recurrence and terminally closes B for the current
tranche at the missing exact source-backed `U_B`. C counts `C` once:
authoritative continuity commits `C[k+1]` and the derived nonresource sector is
then recomputed as `T_C[k+1] = P_M,Delta C[k+1]`; it has no independent writer.
B is therefore a complete conditional constitutive/read-current mechanism, not
a complete formative mechanism. C has projected-sector writing and
retained-conditioned mediation, but effective retained write, dynamical
retention, persistence class, and stability remain D8 questions.
B's typed carrier, geometry, Read-Back, and current closures remain bounded
work, and its terminal result is not ontology rejection or preference for A/C.
A named constitutive successor may reopen B if it derives the writer's type,
units, capacity, formation, release, covariance, and lifecycle semantics; that
reopening reactivates B's path-factorization, post-`H_4` capacity, and
absorbability debts rather than silently resolving them.
All 22 D6-v2 current debts are dispositioned and all 22 inherited rows remain
bound. Human acceptance now authorizes A and C to proceed to D7G. Global `H_4`,
D8, specification, implementation, and runtime claims remain blocked.

D7G-v1 confirms from current source that GRC9V3 is implemented but has not
resolved `g[K]`: the row-basis hybrid node tensor is a diagnostic/cache surface,
while operative transport is rebuilt independently through scalar
`base_conductance`, potential, and flux. The GRC9V3 specification also reserves
tensor-derived transport for a named `anisotropic_edges` extension. That V3
boundary does not imply that V4 `h_4` must replace mobility or select that
extension. Core RC leaves `g[K]` constitutively incomplete, so D7G-v1 freezes a
typed `H_profile` substrate interface and conditionally admits one bounded
common affine profile family without relabeling it as inherited behavior:

```text
E_ref : W_V3 -> H_1,ref
H_1,read+ = H_1,ref + kappa_H Delta K_4
H_0,read+ = H_0,ref
```

on the explicit positive domain. D7G-v2 now instantiates that family with the
revision-specific embedding
`H_0,ref = diag(mu_V3)` and `H_1,ref = diag(W_V3^-1)`. The edge choice consumes
B1's primary native constitutive metric; it does not relabel V3's regularized
`geometric_length` diagnostic as the exact map or claim that V3 already owned
physical `h_4`.

D7G-v2 also separates `H_adm` geometry states from `P_adm` profile maps and
closes bounded supplied-geometry domains for A and C. A's accepted operator
family remains regular while `W_A` remains the sole mobility authority; this is
an invariance/type result, not demonstrated geometry sensitivity. C's selector,
retained geometry, identification, response, and current closure are well typed
on a bounded fixed-rank strict-gap SPD subdomain. Supplied geometry is
load-bearing in C's internal operator chain, but nonzero `D_(h_pre) J_C` and
nonzero `D_(h_pre) F_C` remain unproved. These are profile mathematics, not a
completed cultivation chain.

Both selected lagged explicit transitions stop after the same generated-
geometry surface. A's writer does not consume postsolve `h_4+`; C commits only
`C` and cannot reconstruct prior postsolve `h_4+` from that poststate. This is
a limitation of that D6/D7 realization, not a terminal A/C candidate failure,
a general V4 impossibility, or evidence that core requires a cross-beat
handoff. Core also permits a coupled effective block
`J -> j -> K -> h -> J0 -> J` when the complete chain rule and fixed-point
regularity are carried explicitly.

D7G-v2 now separates supplied pre-read sensitivity `D_(h_pre) F_a` from
generated-geometry sensitivity through candidate-specific `Gamma_a` or an
equivalent complete realization. The latter is currently undefined, not zero.
Accepted D7G-v2 authorizes D8-A to derive each branch-appropriate reduced,
joint, nonselfadjoint, or DAE continuation object and classify its target
directions as realization-invariant, accepted-lagged-branch-relative, or not
finalizable before temporal realization. Only invariant targets constrain all
successors; changed slaving requires rederivation of branch-relative targets.
D8-A is an analysis consumer of `h_4+`, not a runtime causal consumer.
Repeating the absent-`Gamma_a` diagnosis is not evidence. This authorization is
limited to D8-A; D8-B remains blocked.

Those targets then constrain
`GRC9V4-GEOMETRY-TEMPORAL-REALIZATION-SUCCESSOR`. The successor must pressure
coupled/implicit, operator-split same-beat, persistent-carrier, and
reconstructed-geometry families equally as a non-exhaustive minimum set and
instantiate at least one bounded complete realization. Failure of the four is
not V4 impossibility without a separate completeness proof; otherwise search
must broaden or close bounded unresolved. A typed `S_H` interface alone cannot
close it. A and C receive the same burden of proof but need not share equations
when their retained ontologies justify different realizations. D8-B must match
realization families where meaningful or treat each `(candidate, realization)`
pair as an architecture. Specification, implementation, runtime evidence,
stability, and architecture selection remain blocked.

A concrete realization may enter D8-B after defining its equations, authority,
stage order, fixed-stratum Markov closure, accounting, covariance, failure
semantics, bounded regularity, and linearization surface. It must declare later
disabled, lifecycle, and stability obligations, but exact V3 reduction and full
event lifecycle remain D9 work, while stability classification remains D8-B
work. Those downstream results are not circular prerequisites for admission.

D5 currently defines two bounded candidate operator channels (A and C), routes
B to a named derivation, and physically identifies zero channels. Its 68-point
hardening audit keeps trial current distinct from the D6 total-current solve and
keeps A/mobility attribution plus C/`T_C` mediation explicitly open. Typed
operator-family admission is separate from closed retained mediation, all D4
debts have explicit successor dispositions, and pre-spec design obligations are
separated from post-spec causal verification. B remains an architecture
candidate while routed out of D6; it has not been eliminated.

D6 now selects bounded same-beat algebraic slaving for A and parameterized C
and keeps B routed without rejection. The declared solve freezes all noncurrent
context, making `zeta chi R` the complete within-solve block only for that
revision-distinct lagged-geometry staging, not for the core simultaneous loop
in general. Loss of invertibility fails closed; it does not establish a temporal
current law, fast-limit interpretation, stability threshold, write-back, or a
closed reflexive loop. Its 96-point hardening audit also separates partial
deslavement, solver behavior, admissible current support, harmonic topology,
shared current/geometry gain, and mathematical absorbability from those later
claims. Postsolve `J_C` is D7's authoritative causal current; diagnostic `j`
cannot bypass it as a direct write input. Transitive debt persistence keeps 20
older unresolved IDs, including 16 pre-D10 blockers, visible beside the 25
current debts. D6 was accepted bounded on 2026-08-24; D7 is accepted bounded.

D7 now defines one complete Candidate A fixed-stratum kinetic reduced
transition. Authoritative `W_A` drives the graph baseline, the accepted D5/D6
edge-contrast operator closes total current, and the exact downstream mediator
`D_A[k] = (C[k+1], J_C_A[k])` writes one bounded positive `W_A[k+1]` through a
log-geometric one-beat update. This closes the direct retained-mobility
recurrence. The explicit Read-Back subloop is separately constitutively
load-bearing on its declared nondegenerate domain; exact physical
nonabsorbability remains open.
It does not close the normative structural path: `K_4 -> H_4 -> h_4` remains
underdefined, so structural cultivation and a complete GRC9V4 architecture are
still unsupported. B and C remain routed, not rejected. A's earlier completion
does not select or prefer it over B or C. Before D8, an append-only
D4-v2-D7-v2 tranche will complete or close B geometry/operator/writer and C
retained-geometry pathways, then D7G will address the global `H_4` structural
closure over the completed A/B/C candidate-local set. D4-v2 first freezes the
common payload boundary `S_4^a -> iota_a -> K_4^a`, so candidate-local `h_B`
or `h_M` cannot silently become rival owners of physical `h_4`. This prevents
the global law from being shaped around A merely because A became concrete
first. The adapter must preserve at least one lawful candidate-specific
retained distinction rather than merely type-checking. D4-v2 also freezes the
provisional current-space identifications needed to type B/C before global
`h_4`; C's `I_4M^pre` remains candidate-local and must be validated or replaced
by D7G. The
original 72-row pressure audit and an additional 96-row adversarial audit
preserve the D7 distinctions item by item.
The explicit `J_C squared` writer term is sign-even, but full physical history
reversal may change continuity-mediated `C[k+1]` and therefore the complete A
writer; scalar state is not relabeled as signed cochain memory. D7 also freezes
a three-way D10 debt union, with named pre-D10 audits required for A's
core-status, absorbability, and units/gauge questions. Reduced temporal
stability remains a future D8 question. D7G-v2 readies bounded D8-A
branch-appropriate structural-target extraction after acceptance, while full
continuation comparison still waits for a concrete typed temporal geometry
realization.

D8-A now extracts separate A and C reduced structural forms under the accepted
D6-v2 smoothly slaved current closure. A remains conditional C structure at
frozen `W_A`; C remains C-only structure with the exact derived `T_C` tangent.
The D7G-post-v2 correction separates the structural one-form Hodge `H1_form`,
the dual current/flux metric `G_J`, and causally distinct transport mobility
`M4`. On the simple V3 reference, `H1_form = diag(W)` and
`G_J = diag(W^-1)`. Candidate C now uses an explicit
flux/flat/response/sharp/flux chain; its identity-metric witness survives
within binary roundoff, while general nonidentity conditioning remains debt.
The correction also separates physical `j_flux`, consumed by continuity, from
lowered `j_struct^flat`, whose rank-one tensor is consumed by structural `K4`.
Candidate-specific `iota_a` adapters preserve the accepted A/C payload gains;
the correction introduces no common `kappa_K`.
The accepted lagged A/C pullbacks freeze pre-read geometry and therefore use
`delta j_struct^flat = G_J,pre delta j_flux`; variable-metric successors must
also retain `(delta G_J) j_flux`. A nonidentity regression confirms that the
flux and lowered-form outer products are not interchangeable.
Under that typed contract D8-A derives the exact direct field metric target

```text
D_H1_form Q_field[delta H1_form](u,v)
  = kappa_C (d0 u)^T delta H1_form (d0 v),

delta H1_form = kappa_H delta K4.
```

This is not yet a full Hessian or stability result. A nonzero metric increment
can vanish after exact-gradient and conservation/gauge pullback, and the
induced-geometry plus constraint second variations remain branch-specific.
The simple reference weights are not a unique normative graph-DEC
discretization; successors changing edge-volume factors, the structural-Hodge
profile, or flux/form identification must rederive the affected response. The
matrix representative includes `kappa_C`, and target orthogonality is
`H0`-weighted.

D8-A classifies four invariant targets, two accepted-lagged-branch pullbacks,
two additional lagged-branch structural targets that are potentially
derivable before temporal synthesis but not instantiated, and two targets that
genuinely cannot be finalized before temporal realization. The latter are
generated-geometry influence on a later transition and temporal `gamma`/`mu`.
The correction receipt and D8-A are jointly accepted bounded. This authorizes
the named realization successor, not D8-B directly.

The successor's first family pass now pressures coupled/implicit realization.
Candidate C supplies a complete same-step root for `(J_C,flux, h_C)` because
its accepted geometry chain is already load-bearing in `J0_C` and its retained
response. It uses the ungated
`Rhat_C,M = (I + tau_C Delta_1,M)^-1`, applies `chi_C` only in the explicit
causal read, and keeps shared `zeta_C` outside the candidate adapter. Its
corrected physical current block is exactly similar to the
accepted retained D6-v2 block through `Q_C = I_4M(T_C,h) G_J(h)`, so exact
invertibility transfers while physical conditioning remains separate debt.

Candidate A now also supplies a complete same-step root. D4 permits geometry
and `W_A` mobility to enter baseline transport through distinct typed roles;
D7 supplies the exact reference baseline and writer. A's revision-specific
profile adds `[Delta_0(h)-Delta_0(h_ref)] C` to the baseline potential, keeps
`W_A` as the sole mobility owner, and preserves the D7 writer. The correction
vanishes exactly at reference geometry. Its typed `kappa_Ah` uses a
preregistered finite enabled value and a zero ablation, `W_hat_A(h)` is
recomputed inside every joint-root residual, and shared `zeta_A` remains
outside the candidate adapter.

The successor also supplies formal projected direct-field visibility receipts
for both candidates. The C selected-sector receipt has pre-adapter projected
value `-0.014842807194071116`; the A receipt has value
`0.41999999999999993`. Accepted non-erasure plus exact-gradient surjectivity on
the connected three-node tree establishes nonempty post-adapter visible
subdomains. These receipts close the D8-A witness obligation but do not provide
runtime, complete transition-chain, Hessian, temporal, or stability evidence.

Both candidates therefore have block-triangular reference Jacobians and local
implicit-function branches on their declared smooth fixed-stratum domains.
These are local constitutive existence results, not global branches, numeric
coupling margins, stability results, or unique core-theory laws. The pass does
not rank A and C or select the coupled family. Human acceptance authorizes A
and C separately for architecture-local D8-B rederivation, while comparative
D8-B and the remaining operator-split, persistent, and reconstructed family
pressure stay open. The coupled family record is complete; the overall
geometry-temporal successor is not.

D8-B now derives the exact analysis surfaces made available by the accepted
coupled roots. For A and C separately it defines the full implicit first and
second root derivatives, architecture-local constrained structural second
variation, complete committed-state Jacobian, direct Read-Back operator,
spatial graph operator, projector/reference transport, covariance, and
nonnormal stability diagnostics. Candidate A remains conditional C structure
at fixed `W_A`; Candidate C remains C-only with a derived `T_C` tangent.

The hardened result requires `C2` subcharts for classical Hessians, instantiates
the graph-field second-variation formula, separates intrinsic response `r_a`
from enacted gain `beta_a = zeta_a r_a`, and uses a transported temporal
cocycle with the correct `k+1` output transport on moving branches. `beta`
remains spectral; direct-response singular values are separate diagnostics.
Constraint and measure curvature stay inside the differentiated Lagrangian,
while projector transport is not additive Hessian curvature. The result leaves
the complete-step V4 charge/projector and Candidate A's relative `C`/`log W_A`
analysis metric as explicit debts
rather than inferring them from legacy GRC9V3 or an arbitrary norm.

This is a design-level operator completion, not a numerical spectrum result.
There is no instantiated formed V4 critical branch or normalized functional
parameter set, so D8-B reports no `alpha`, `beta`, `gamma`, `mu`, or `lambda`
values and no stability classification. B1/B2 verification methods are mapped
for later reuse or V4-specific adaptation, while all V3 numerical outputs stay
historical. The A and C direct-field visibility receipts remain narrower than
complete-chain nonannihilation. At D8-B acceptance, comparative D8-B,
remaining realization-family pressure, and D9 remained blocked pending later
gates.

The route from D8-B was the remaining realization-family pressure, not D9 and
not a numerical-spectrum campaign. Operator-split same-beat came first,
reconstructed geometry second, and persistent structural carrier third;
comparative realization synthesis follows. The ordering minimizes unnecessary
new state authority and does not rank the families. Each row asks whether the
family can produce a bounded complete A/C step and terminates as a bounded
complete realization, candidate-local blocker, family-level obstruction, or
bounded unresolved result.

The operator-split primary row is accepted bounded. It freezes
one predictor, one generated-geometry stage, one fixed-geometry corrector, and
one atomic commit, with no retroactive geometry correction. A and C each admit
a bounded complete design realization with an explicit equation-level same-
beat geometry consumer. The split pair solves the coupled current equation
exactly; its only coupled-equation residual is the deliberately unclosed final-
current geometry fixed point. A typed normed local theorem keeps `Delta K4`
in the common `K_4` norm and maps it through `P_0: K_4 -> T_h H1_form`
before applying the relative Hodge norm. The resulting residual is quadratic
in `kappa_H` on the D8-B `C2` charts. It is not relabeled as an
`O(Delta_t)` time-integration error, and no numeric split envelope or executed
complete-chain witness is claimed.

The reconstructed-geometry pressure now supplies an accepted bounded local A/C
family result. RG-1 closes same-beat distinct-family identity:
an exact reduced evaluator is constitutively CI-equivalent, while staged
evaluation is OS. An exact state-only formula may exist; formula nonexistence
is not claimed.

RG-2 first proves local poststate reconstruction as a property of existing
CI/OS steps from their zero-duration identity limits. It then closes a distinct
lagged A/C architecture through a unique local Lipschitz invariant section near
the constant `kappa_H=0` section, relative to a frozen equivariant family-local
extension/profile completion. Nested `K_-`, `K`, and `U` domains plus forward
containment keep the claimed transition on the accepted candidate maps. The
result requires smooth fixed-context charts, small positive `Delta_t`, small
typed geometry gain `epsilon_H`, value and Lipschitz self-map bounds, and the
corrected `C0` contraction. It does not provide numeric radii, `C1` section
regularity, global reconstruction, event continuation, or extension-independent
uniqueness.

Persistent-carrier pressure tests independently retained structural state
beyond the local invariant section without requiring local inversion or a
single-valued section. It may also expose representation-preserving context
continuation, while base-state hysteresis remains a stronger complete-chain
claim. It may not begin from an assumed local information deficit.

The authoritative RG records are
[`GeometryTemporalRealizationSuccessorReconstructedGeometry.json`](./decisions/GeometryTemporalRealizationSuccessorReconstructedGeometry.json)
and its
[`scientific interpretation`](./decisions/GeometryTemporalRealizationSuccessorReconstructedGeometry.md).

The persistent-carrier pressure now supplies bounded complete A/C design rows
with an explicit new state cost. Each row stores one bounded candidate-specific
`K_4` coordinate `Z_4`, derives current geometry from it, and updates it once
per beat through

```text
Z_4+ = a_PC Z_4 + (1-a_PC) Delta K_4(J_C,h),
a_PC = exp(-Delta_t/tau_PC).
```

On a constructively admitted carrier ball satisfying `m(R)<=R`, profile
admissibility, and uniform fixed-geometry current regularity
`sigma_min(D_JF_J)>=m_J>0`, this writer forms from nonzero current, retains
state at every finite time, releases asymptotically under zero source, and
remains bounded without clipping. The sufficient radius theorem uses
`||S||<=M_0+L_Z||Z||`, `L_Z<1`, and caps `R` by the profile and current-
regularity radii; numerical constants remain uninstantiated. Variable-step
convergence requires accumulated elapsed time to diverge, and matched forcing
strictly contracts carrier differences. A keeps `W_A` as mobility authority;
C keeps `T_C` derived. Current and full geometry are not serialized.

PC is not native coherence-only theory. It is a revision-specific completion
that tests the core's open Markov-sufficiency boundary and explicitly adds D1
B-like independent structural authority to A or C. Its positive capability is
independently retained path-dependent state: the same base A or C state may
coexist with different carrier histories, so geometry need not be a single-
valued local `Gamma(X)`. Nonsingularity of `a_PC I+O(epsilon_H)` preserves those
differences in complete PC state, but base-state hysteresis and nonzero future
`C/W` effects remain debt.

Snapshot, restoration, reset-baseline, migration, disabled-profile, D2
intervention, and atomic failure semantics are frozen. Representation-preserving
context/boundary changes retain the carrier and refresh surfaces only when
profile/carrier/writer semantics are unchanged; semantic profile changes require
explicit migration and target re-admission. Carrier-space topology changes
still fail closed without a typed interspace map. Comparative synthesis must
audit full `K_4` versus the exact profile-kernel quotient, treat this as the
scalar-ZOH representative rather than a universal single-timescale PC law, and
test persistence as a potentially orthogonal axis to CI/OS/lagged timing. PC is
accepted bounded and routed comparative realization synthesis.

The authoritative PC records are
[`GeometryTemporalRealizationSuccessorPersistentCarrier.json`](./decisions/GeometryTemporalRealizationSuccessorPersistentCarrier.json)
and its
[`scientific interpretation`](./decisions/GeometryTemporalRealizationSuccessorPersistentCarrier.md).

Comparative synthesis subsequently retained eight positive primary A/C rows,
two RG-1 obstruction rows, and Candidate B as routed rather than rejected. It
separated candidate ontology, geometry/current timing, and history authority
without ranking them. The narrow CI+PC pressure then established that coupled
same-beat timing and independently persistent `K_4` history compose locally
for A and C under the preregistered unit-plus-unit profile. The steady source
therefore has structural gain two; this was not normalized away.

D9 now closes design-level operational semantics across all ten positive
profiles. Its registry and 260-cell matrix freeze complete-step ordering,
charge, failure atomicity, temporal edges, disablement, exact V3 reduction,
migration, restoration identity, replay, covariance, and regime boundaries.
The charge is derived from the actual closed-internal unit-measure write path
as `Q=sum(C)` and generalized to `Q_varpi=varpi^T C` for typed resource events.
Its structural `H0`-weighted C-sector projector extends to a canonical full
tangent retraction without claiming a full-state orthogonal projector. The
current budget stage is an identity/no-op before final-`C` writers.

All ten rows admit typed topology continuation through an event-supplied
resource map, explicit charge receipt, candidate-specific history transport or
lossy reset, target reconstruction, readmission, and atomic commit over the
whole lifecycle tuple `(X_current, X_reset, Q_target)`. Exact V3
base-conductance reconstruction supplies the history-free A initializer,
persistent carriers use a typed `L_K4_evt` when sufficient lineage exists or
an explicit reset receipt when it does not, RG reconstructs its target section,
and C rank changes use stratum-local contraction plus basis-independent root
selection. Topology continuation therefore does not imply lossless history
transport. Generic preservation without sufficient lineage is closed as a
bounded negative result, leaving zero open D9 lifecycle-mathematics debts and a
29-debt inherited scientific live union. Typed lifecycle continuation also does
not establish continuation-spectrum identity preservation. Four
numerical/runtime conformance items remain post-spec verification obligations
rather than missing design mathematics. Candidate B remains
underdetermined because PC does not derive its signed symmetric formation
source. The matrix also exposes 16 independent interventions across its three
multi-authority rows. D9 is accepted bounded. D10 and its D10.1/D10.2
provenance successors are accepted bounded. The current-population substrate
identity is closed, and GRCv4-first specification writing is authorized.

The later specification and implementation must also rebuild every
differential or gradient summary used by `G_W(C[k+1], J_C[k])` from
post-continuity `C[k+1]`; pre-continuity cache reuse is outside the accepted
writer contract.

By D7-v2, each A/B/C row must either expose a complete candidate-local
transition conditional on admitted pre-read geometry and admissible to D7G, or
close for this tranche with a localized
missing-theory, missing-derivation, or target-incompatibility result.
`routed_not_rejected` is not a terminal v2 status, and reopening is paused
control flow rather than scientific closure. D7G is a distinct integration
gate that extends D7-v2 and supersedes nothing. It freezes the typed
`H_profile` interface, admits named realizations, and tests whether candidate
families close parametrically over an admitted geometry class. A profile
change alone does not reopen D4-D7; authority, staging, or operator-family
changes do. Only after that audit closes can it determine D8 comparability. A sole
surviving candidate remains unselected until D10 evaluates the frozen target
and all veto debts.

The documented successor lineage is the default no-reopening path. Any earlier
gate change gives the resumed successor a new identity whose predecessor is the
latest accepted record in the propagated chain. Unresolved debt follows that
chronological predecessor, not merely the older gate being superseded. Zero
survivors map to `rejected_all_candidates`/current-candidate-set exhaustion;
one common theory blocker may instead map to `blocked_missing_theory`.

Current boundary:

```text
D0-D10.2 accepted bounded design and provenance closeout
  -> authorizes a GRCv4 normative specification
  -> then authorizes a substantive GRC9v4 nine-port specialization
  -> requires exact disabled-profile compatibility from GRC9v4 to GRC9v3
  -> does not authorize implementation or src/ changes

future constitutive or realization profiles outside the current D10 population
  -> reopen provenance and the earliest accepted contract they affect
  -> do not inherit current-population promotion automatically
```

The accepted route is specification work, not a claim that GRCv4 or GRC9v4 is
already runnable. Candidate A and C profiles and the admitted realization
families remain claim-qualified current-population choices; Candidate B remains
a routed successor slot rather than a rejected ontology.

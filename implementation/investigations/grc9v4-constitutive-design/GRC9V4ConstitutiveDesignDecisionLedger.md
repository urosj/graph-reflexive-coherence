# GRC9V4 Constitutive Design Decision Ledger

**Status:** D0-D7, D4-v2-D7-v2, D7G-v1, D7G-v2, the D7G-post-v2 correction, D8-A, and coupled/implicit A+C accepted bounded; architecture-local D8-B for coupled A and C is authorized, while comparative D8-B and successor-family closeout remain blocked

This ledger is the additive decision record for D0-D10. The design basis and
plan define questions and constraints; this file records accepted answers.
Rejected alternatives remain visible rather than being rewritten after a later
selection.

## Ledger Rules

Every gate record must contain:

```text
gate_id
status
predecessor_decision_digest
decision_record_digest
supersedes
source_identities
assumptions
candidates_considered
decision
rejected_alternatives
evidence_or_argument
open_debt
blocked_relabels
authorization_effect
human_acceptance
```

An unresolved field is written as `pending` or `not_identifiable`, never filled
from anticipated later results. Design arguments, analytical prototypes, and
runtime evidence keep distinct provenance labels.

Accepted records are immutable and append-only. Reopening a gate creates a new
record with `predecessor_decision_digest` and `supersedes`; it does not edit the
accepted payload. The canonical decision payload is the complete gate record
with `decision_record_digest` omitted, serialized as UTF-8 JSON with object keys
sorted lexicographically, compact `,` and `:` separators, ASCII escaping
enabled, finite-number formatting supplied by Python
`json.dumps(..., sort_keys=True, separators=(",", ":"), ensure_ascii=True,
allow_nan=False)`, and array order preserved. `decision_record_digest` is the
SHA-256 of those canonical bytes. A prose-only record cannot receive an
accepted digest unless an equivalent structured decision object is frozen
with it.

`predecessor_decision_digest` names the accepted serial predecessor gate.
`supersedes` names an earlier record of the same gate when that gate is reopened.
For example, `D3-v2` consumes the accepted D2 digest as predecessor and names
the D3-v1 digest under `supersedes`.

Every debt carried by `accepted_bounded` must contain:

```text
debt_id
blocking_scope
candidate_scope
assumption_forbidden_downstream
resolution_gate
must_close_before_D10
```

`rejected_all_candidates`, `blocked_missing_theory`, or
`blocked_missing_discriminator` may open only a bounded D10 closeout route or a
named revised gate. They do not authorize later constitutive gates.
`rejected_all_candidates` is recorded as `current_candidate_set_exhausted`; it
does not reject the GRC9V4 target and must identify a named next derivation,
candidate-admission revision, or discriminator requirement.

## Initialization Record

Authoritative structured record:
[`GRC9V4ConstitutiveDesignInitialization.json`](./GRC9V4ConstitutiveDesignInitialization.json)

The following is a non-authoritative reading summary; the JSON record and its
verified semantic digest define the predecessor identity.

```text
record_id = GRC9V4-CD-INIT
status = initialized_pre_D0
decision_record_digest = 7daf0693e2603b8e0c7062c77789a4ae71b6372b5605e31024be304a282e2654
branch = investigation-GRC9V4-constitutive-design
target = continuation_capable_retained_representation_with_directional_readback
architecture_selected = false
candidate_families =
  V4-A-temporalized-W
  V4-B-independent-derived-carrier
  V4-C-constitutive-C-sector
  V4-D-source-admitted-structural
current_closure_axis = deferred_to_D6_slaved_or_explicitly_deslaved
specification_authorized = false
runtime_implementation_authorized = false
normative_GRC9V4_spec_exists = false
next_gate = D0
```

## D0. Target, Inheritance, And Claim Ceiling

Status: accepted.

Required predecessor decision digest:
`7daf0693e2603b8e0c7062c77789a4ae71b6372b5605e31024be304a282e2654`.

Structured decision:
[`decisions/D0TargetInheritanceAndClaimCeiling.json`](./decisions/D0TargetInheritanceAndClaimCeiling.json)

Human interpretation:
[`decisions/D0TargetInheritanceAndClaimCeiling.md`](./decisions/D0TargetInheritanceAndClaimCeiling.md)

```text
record_id = GRC9V4-CD-D0-v1
status = accepted
decision_record_digest = b38b07311afc24bfe1016d75e985f886718e5a9d104c69c59e29318801f457c0
theory_source_identity_match = exact
B1_statement_drift = 33 unchanged; 0 narrowed/broadened/superseded/conflicted
claim_level_theory_anchors = 33
current_GRC9V3_runtime_source_match = exact_5_of_5
runtime_drift = false
spec_runtime_mismatch = false
candidate_set_frozen = true
candidate_universe_status = exhaustive_named_pre_D1_only_not_all_possible_V4
candidate_family_labels = investigation_classifications_not_mutually_exclusive_truths
design_verification_envelope = fixed_topology_event_free_smooth_strata
normative_runtime_scope = full_GRC9V3_capability_successor
disabled_legacy_subspace_invariance_required = true
disabled_hidden_history_accumulation_allowed = false
typed_debt_count = 7
claim_ceiling = GRC9V4-CD-D0-contract-only
human_acceptance = accepted_2026-08-24
D1_authorized = true
specification_authorized = false
runtime_implementation_authorized = false
```

## D1. Retained-Representation Ontology And Candidate Admission

```text
record_id = GRC9V4-CD-D1-v1
status = accepted_bounded
predecessor_decision_digest = b38b07311afc24bfe1016d75e985f886718e5a9d104c69c59e29318801f457c0
decision_record_digest = f8ae101beb9fa6e9827555eba64452087c1d19b6933325966f10c4c4ec64c507
admitted_candidate_set = [V4-A-temporalized-W, V4-B-independent-derived-carrier, V4-C-constitutive-C-sector]
rejected_on_ontology = [V4-D-source-admitted-structural]
rejection_reason = uninstantiated_admission_slot_not_materially_distinct
sole_surviving_candidate = none
current_candidate_set_exhausted = false
architecture_selected = false
current_temporalization = deferred_to_D6
transport_role_status = provisional_candidate_signatures_pending_D4
verification_envelope = fixed_topology_event_free_smooth_strata
normative_target = full_topology_capable_GRC9V4_successor
claim_ceiling = GRC9V4-CD-D1-bounded-ontology-admission
open_debt_rows = 9
must_close_before_D10_debt_rows = 8
D2_authorized = true
specification_authorized = false
runtime_implementation_authorized = false
```

D1 admits A, B, and C as bounded ontology families without ranking them. D is
closed because the frozen source search produced no materially distinct fourth
causal object; all concrete forms classify under A, B, C, or analysis-only.
Candidate-specific embeddings and projections are constructed at the state-space
level only. D7/D9 still own transition commutation and invariant disabled-profile
parity. Fixed topology remains a local verification envelope, not the final V4
capability scope.

## D2. Formation, Retention, Release, And Write Interface

```text
record_id = GRC9V4-CD-D2-v1
status = accepted_bounded
predecessor_decision_digest = f8ae101beb9fa6e9827555eba64452087c1d19b6933325966f10c4c4ec64c507
decision_record_digest = ea2b953685bb23dfe979b2f5d2ae0f22f364a51484d6536c1721f144c9cad740
candidate_set_after_D2 = [V4-A-temporalized-W, V4-B-independent-derived-carrier, V4-C-constitutive-C-sector]
rejected_on_D2_interface = []
same_beat_new_state_read_allowed = false
control_contract_rows = 33
D2_pressure_audit_rows = 30
open_debt_rows = 15
must_close_before_D10_debt_rows = 14
claim_ceiling = GRC9V4-CD-D2-bounded-write-interface
D3_authorized = true
human_acceptance = accepted_bounded_2026-08-24
specification_authorized = false
runtime_implementation_authorized = false
```

D2 freezes one-beat-delayed candidate write interfaces; distinct initialization,
no-forming-input, write-off, frozen-state, and reset controls; bounded native
release/reconfiguration; and resource/capacity/lifetime boundaries. The
33-control contract and 30-row pressure audit cover A double-write and
normalization, B cache/Markov/resource-regeneration, C projector/rank/sector
identity, and cross-candidate multiwrite/covariance/RNG risks. A writes
authoritative enabled `W`; B writes independent `T`; C writes only through
authoritative `C` and derives its sector. Exact operators, D4 transport
ownership, runtime effects, and reduction remain open.

## D3. Continuation Requirements And Structural Domain

```text
record_id = GRC9V4-CD-D3-v1
status = accepted_bounded
predecessor_decision_digest = ea2b953685bb23dfe979b2f5d2ae0f22f364a51484d6536c1721f144c9cad740
decision_record_digest = 8e7db364cc4402b9794d825629962d1851fc15a2f0b71fa015cfaeb01f42643d
candidate_set_after_D3 = [V4-A-temporalized-W, V4-B-independent-derived-carrier, V4-C-constitutive-C-sector]
candidate_domain_status = [A: conditionally_supported, B: conditionally_supported, C: supported_bounded]
support_matrix_rows = 12
support_matrix_cell_detail_rows = 12
support_matrix_status_counts = [supported: 2, conditionally_supported: 7, theory_open: 3, blocked: 0]
control_contract_rows = 39
D3_pressure_audit_rows = 42
predecessor_debt_rows_classified = 15
open_debt_rows = 24
must_close_before_D10_debt_rows = 20
conditional_nonblocking_debt_rows = 3
all_non_D10_blocking_debt_rows = 4
joint_structural_candidate_supported = false
current_regime_selected = false
architecture_selected = false
claim_ceiling = GRC9V4-CD-D3-bounded-structural-domain
D4_authorized = true
specification_authorized = false
runtime_implementation_authorized = false
```

D3 admits C-only structure for Candidate C on smooth fixed-rank reduced
branches and conditional C structure for A/B with their retained coordinates
frozen. It separates structural reference states from the stronger
D2-retained structural intersection and separates candidate viability from
continuation-claim viability. It does not admit
independent `delta_W` or `delta_T` into a structural Hessian. Functional
normalization, gauge/null treatment, geometry chain rules, tangent-cone and
nonsmooth-selector boundaries, and every matrix-cell claim are explicit.
Independently active-current rows remain theory-open for all candidates; D6
still owns current-regime selection. Analysis-only and retrospective temporal
projectors cannot become constitutive by relabel, while a future runtime-owned
dynamic projector remains conditionally admissible under the full temporal,
isolation, causal-consumption, and fixed-point contract. No Hessian, spectrum,
formed branch, complete transition, or architecture is claimed.

Joint A/B structure and independently active-current structure remain
conditional, nonblocking debts. They become D10-blocking only if D6/D8 selects
a claim that requires the corresponding independent structural coordinate.

Forward execution boundary:

```text
D0-D3 = accepted verification-to-design bridge
D4-D9 = candidate-specific constitutive design
bounded V3 conclusion rerun without a changed question = not a completed gate
reconfirmed unchanged-GRC9V3 absence = not a completed gate
changed V4 causal object/state/operator = inherited result must be reclassified
```

B1/B2 now supply four explicitly different inputs: `legacy_fact`,
`verification_control`, `design_pressure`, and `open_hypothesis`. Only a legacy
fact is a hard premise, and only about its frozen V3 revision and envelope.
D4 onward may depart from inherited assumptions when the change is explicit,
source-backed, and tied to the new V4 causal object. It must add concrete
ownership maps, operators, closure equations, complete-transition equations,
or named candidate rejection/routing outcomes.

## D4. Geometry, Mobility, And Topology Ownership

```text
record_id = GRC9V4-CD-D4-v1
status = accepted_bounded
predecessor_decision_digest = 8e7db364cc4402b9794d825629962d1851fc15a2f0b71fa015cfaeb01f42643d
decision_record_digest = c3c4507d4623ee526e636c4434bc13b4af23bdd3f6051cf1db99a2ce5736215c
candidate_dispositions = [A: coherent_bounded_ownership, B: routed_named_missing_derivation, C: routed_named_missing_derivation]
architecture_selected = false
D5_authorized = true
```

D4 assigns geometry to `K_4 -> h_4`, keeps mobility as a causally distinct
`A_4/M_4` role, and binds legacy scalar `W` to the discrete mobility role rather
than to the metric. Candidate A uses retained `W_A` as the single enabled
transport authority; `R_W` remains the D2 relation to `W_hat`, not mobility
authority.
Baseline geometry follows declared source inputs through `K_4 -> h_4 -> J0`;
present `J_C` enters geometry only after a D5 `J_C -> j` map. Candidate C's
direct `H_M` map excludes present `J_C`. B is routed to an independent-carrier
geometry closure; C is routed to the exact retained-geometry closure that the
core paper explicitly leaves open. Neither route is a rejection or a completed
constitutive equation.

An analysis projector does not gain runtime authority by analysis alone.
Candidate C may consume a dynamic sector only when it is deterministically
reconstructable under D1/D3 or separately admitted as runtime causal state;
analysis-only sectors remain unavailable to `H_M`.

The hardened D4 record contains 12 object rows, 15 typed causal arrows, three
candidate event-transport rows, three D3-feedback rows, 39 controls, 50 pressure
rows, 15 localized failure codes, and 23 open debts. It distinguishes roles
from stored fields, runtime mobility from the D8 analytical operator, structural
from kinetic effects, baseline `J0` from Read-Back `j`, and zero mobility from
metric degeneracy or topology deletion. A's direct retained-`W` structural
claim is demoted without rejecting its retained-mobility architecture.

## D5. Directional Read-Back

```text
record_id = GRC9V4-CD-D5-v1
status = accepted_bounded
predecessor_decision_digest = c3c4507d4623ee526e636c4434bc13b4af23bdd3f6051cf1db99a2ce5736215c
decision_record_digest = 453416f42beefa1c9e725b675a0af7d4fd49c3e83691ee16e3e3bcfb6d37f213
operator_family_count = 2
operator_channel_definition_count = 2
physically_identified_Read_Back_channel_count = 0
D6_eligible_candidates = [V4-A-temporalized-W, V4-C-constitutive-C-sector]
candidate_set_after_D5 = [V4-A-temporalized-W, V4-B-independent-derived-carrier, V4-C-constitutive-C-sector]
D6_eligible_candidate_set = [V4-A-temporalized-W, V4-C-constitutive-C-sector]
routed_candidate_set = [V4-B-independent-derived-carrier]
routed_not_rejected = [V4-B-independent-derived-carrier]
control_contract_rows = 57
D5_pressure_audit_rows = 68
open_debt_rows = 27
predecessor_debt_disposition_rows = 23
candidate_ranking_performed = false
architecture_selected = false
D6_authorized = true
human_acceptance = accepted_bounded_2026-08-24
```

D5 assigns Candidate A the bounded explicit V4 edge-contrast family
`j_A = Diag((W_A-W_hat)/(W_A+W_hat)) J_trial`. It is not inherited core
retained-geometry Read-Back and does not redefine D2 `R_W`. Candidate C receives
an explicit isotropic graph-resolvent specialization of the core Hodge-response
candidate class,
`j_C^M = (I + tau_C Delta1_M)^-1 J_trial^M`, parameterized by regular `h_M`; the
exact `H_M` closure remains open. Candidate B remains unrejected but is routed
to `GRC9V4-D5-B-TYPED-READBACK-DERIVATION` because its carrier and geometry map
cannot yet type a one-cochain operator.

Both admitted families obey the operator passive null, graph-isomorphism and
orientation covariance, candidate-specific reversal rules, support/accounting
contracts, and read-off that preserves direct retained-conditioned `J0`. They
define candidate channels but physically identify none: A may remain absorbable
into mobility, while C has no direct `T_C` consumer until `H_M` is derived. D6
owns total-current closure, gain, support, regularity, and the full direct/read
overlap and identifiability audit. No operator has been implemented or run.
The generic signature includes declared nonretained `X_read` context, and typed
operator-family admission is separate from closed retained mediation. All 23 D4
debts have explicit D5 dispositions. Pre-D10 factorization and rival-control
availability are separated from post-spec physical identification and empirical
attribution; the excluded C dynamic sector is dormant unless later admitted.
B remains in the post-D5 architecture candidate set while routed out of D6.
The C selector/geometry fixed-point debt remains independently open, and Hodge
construction closure at D8 is separated from post-D10 normative encoding.

## D6. Total-Current Closure

```text
record_id = GRC9V4-CD-D6-v1
status = accepted_bounded
predecessor_decision_digest = 453416f42beefa1c9e725b675a0af7d4fd49c3e83691ee16e3e3bcfb6d37f213
decision_record_digest = 0c78ede1551ece13c4b4fc916f60531bdc30219791bf90be574e5b0f80aa3f16
candidate_set_after_D6 = [V4-A-temporalized-W, V4-B-independent-derived-carrier, V4-C-constitutive-C-sector]
D7_eligible_candidate_set = [V4-A-temporalized-W, V4-C-constitutive-C-sector]
routed_candidate_set = [V4-B-independent-derived-carrier]
algebraically_slaved_candidate_count = 2
current_temporalized_candidate_count = 0
routed_candidate_count = 1
candidate_rejected_count = 0
control_contract_rows = 72
D6_pressure_audit_rows = 96
predecessor_debt_disposition_rows = 27
transitive_predecessor_debt_disposition_rows = 20
transitive_predecessor_must_close_before_D10_rows = 16
open_debt_rows = 25
candidate_ranking_performed = false
architecture_selected = false
D7_authorized = true
human_acceptance = accepted_bounded_2026-08-24
```

D6 assigns A and parameterized C exact bounded same-beat algebraic current
closures. It freezes all noncurrent constitutive context before the solve, so
the declared full within-solve block is `B_eff,D6 = zeta chi R`; any later
same-beat re-entry requires a D6 successor and a full chain-rule derivation. A's
diagonal inverse preserves baseline support and closes the initial exact-zero-
mobility edge case. C's Hodge inverse is a bounded positive modal response on a
regular retained-geometry metric space, but remains parameterized by `h_M` and
does not close `T_C` mediation.

B remains in the candidate set and is routed through its D4/D5 missing
derivations. No current is independently temporalized. Loss of invertibility
fails closed and does not select a temporal completion or identify structural
marginality, spark, basin birth, or topology change. D6 supplies neither a
demonstrated fast temporal limit nor write-back, a closed loop, stability,
runtime evidence, physical channel identification, architecture selection, or
specification authority.

The 96-point hardening pass further freezes the admissible current space,
potential-gauge boundary, exact solver-independent branch rule, robust
singular-value conditioning, and partial critical-subspace successor. A's
subunit profile is uniformly regular without a future `W_A` cap. C is regular
on trees and cycle graphs below unit gain, while its harmonic sector is singular
at unit gain and cannot be repaired by `tau_C` or projection. The initial
profile uses one shared `zeta_a` for current and staged `j tensor j` geometry.
Exact A/C mathematical absorbability remains typed pre-D10 debt; it is not
collapsed into later empirical identifiability.

The lagged-geometry closure is a revision-distinct GRC9V4 discrete-beat
realization, not a general reduction of the core simultaneous
`J -> j -> K -> h -> J0` loop. Postsolve `J_C` is the authoritative causal
current handed to D7. `j` is restricted to the declared shared-gain geometry
path and telemetry/analysis; it is not an authorized direct retained-state
write input, and gain-off diagnostic `j` has no causal consumer. The shared
gain is dimensionless only in the initial normalized current profile pending
the inherited D4 physical-units audit.

D6 also incorporates by reference all 20 still-open older debt IDs carried
through D5. Sixteen remain pre-D10 blockers. D10 must consume the union of that
transitive ledger and the 25 current-generation open debts.

## D7. Closed Write/Read Loop

```text
record_id = GRC9V4-CD-D7-v1
status = accepted_bounded
predecessor_decision_digest = 0c78ede1551ece13c4b4fc916f60531bdc30219791bf90be574e5b0f80aa3f16
decision_record_digest = 7ffaf92b1672aa4fb116539ca5da36aef8bc7f3caf088827fd71f3ec7b483fea
candidate_set_after_D7 = [V4-A-temporalized-W, V4-B-independent-derived-carrier, V4-C-constitutive-C-sector]
D8_eligible_candidate_set = [V4-A-temporalized-W]
routed_candidate_set = [V4-B-independent-derived-carrier, V4-C-constitutive-C-sector]
complete_reduced_transition_count = 1
complete_normative_transition_count = 0
closed_write_read_loop_count = 1
closed_retained_mobility_recurrence_count = 1
constitutively_load_bearing_explicit_Read_Back_subloop_count = 1
empirically_attributed_explicit_Read_Back_loop_count = 0
closed_structural_cultivation_loop_count = 0
candidate_rejected_count = 0
control_contract_rows = 70
D7_pressure_audit_rows = 72
D7_adversarial_audit_rows = 96
predecessor_debt_disposition_rows = 25
immediate_predecessor_superseded_or_resolved_rows = 23
immediate_predecessor_independently_carried_rows = 2
immediate_predecessor_independently_carried_pre_D10_blockers = 0
transitive_predecessor_debt_disposition_rows = 20
transitive_predecessor_must_close_before_D10_rows = 16
open_debt_rows = 16
candidate_ranking_performed = false
architecture_selected = false
D8_authorized = false
D8_authorization_status = deferred_pending_separate_human_direction
D8_authorized_after_human_acceptance = false
D8_authorization_requires_separate_human_direction = true
```

D7 defines one exact Candidate A fixed-topology, fixed-geometry kinetic reduced
transition. Its graph-coupled baseline uses authoritative `W_A`; its
instantaneous reference is staged from `C` and pre-read `J0`; its D5/D6
edge-contrast current closure remains unchanged; and postsolve `J_C` plus
postcontinuity `C` construct one positive bounded log-geometric write to
`W_A[k+1]`. The result closes the direct retained-mobility recurrence and makes
the explicit cross-beat Read-Back subloop constitutively load-bearing on a
declared nondegenerate domain, without introducing independent current state,
direct `j` write authority, RNG, clipping, or hidden helper history. Exact
physical nonabsorbability remains open.

The result is deliberately reduced. The exact global `H_4` map remains open,
so the staged `j tensor j` contribution cannot yet establish structural
cultivation or a complete normative GRC9V4 transition. B remains routed through
its geometry and typed-operator derivations. C retains the core-derived sector
write equation but remains routed because the `T_C -> H_M -> h_M` mediation,
selector regularity, and event-space transport are missing. No candidate is
rejected or selected.

D7 dispositions all 25 D6 current-generation debts and all 20 transitive
inherited rows. Its 72-row pressure audit and additional 96-row adversarial
closure audit separate current/write authority,
formation/retention/release, orientation, rivals, failure atomicity,
moving-neutral attribution, arrow-specific loop sensitivity, absorbability,
reduced-versus-normative scope, and routing. D7 is accepted bounded; D8 remains
unauthorized pending a separate human direction, with eligible scope limited to
the concrete A reduced transition.

The immediate ledger is explicit: 23 rows are resolved or superseded into
named D7 debts and two nonblocking rows remain independently carried. D10 uses
a three-way union of current D7 debt plus unresolved immediate and transitive
predecessor dispositions. A's core-status, absorbability, and units/gauge
technical results require named pre-D10 audits. D8 may close only reduced A
temporal-transition stability and floor nonsmoothness; normative structural
stability remains blocked on the missing `H_4` map.

The later specification and implementation must rebuild every differential or
gradient summary consumed by `G_W(C[k+1], J_C[k])` from post-continuity
`C[k+1]`. Reusing pre-continuity `C[k]` summaries would violate the accepted
writer temporal side.

## D4-v2-D7G. Candidate Completion And Structural-Closure Successor Tranche

Status: D4-v2 through D7-v2, D7G-v1, and D7G-v2 accepted bounded; bounded
D8-A structural-target extraction is authorized while full continuation is
blocked.

This append-only tranche does not modify or supersede accepted D4-D7 until a
specific successor record is accepted. It prevents A's earlier completeness
from becoming an implicit selection criterion and gives B, C, and the global
structural map their named derivation attempts before comparative D8.

```text
D4-v2 = GRC9V4-CD-D4V2-v1, accepted_bounded
D5-v2 = GRC9V4-CD-D5V2-v1, accepted_bounded
D6-v2 = GRC9V4-CD-D6V2-v1, accepted_bounded
D7-v2 = GRC9V4-CD-D7V2-v1, accepted_bounded
D7G = GRC9V4-CD-D7G-v1, accepted_bounded_requires_D7G-v2_parametric_closure_and_finalization
D7G-v2 = GRC9V4-CD-D7G-v2, accepted_bounded_with_A_C_D8A_structural_target_authorization_and_no_full_D8_survivor

default_successor_lineage_when_no_earlier_gate_reopens =
  D4-v2:
    predecessor = 7ffaf92b1672aa4fb116539ca5da36aef8bc7f3caf088827fd71f3ec7b483fea
    supersedes = c3c4507d4623ee526e636c4434bc13b4af23bdd3f6051cf1db99a2ce5736215c
  D5-v2:
    predecessor = accepted_D4-v2_digest
    supersedes = 453416f42beefa1c9e725b675a0af7d4fd49c3e83691ee16e3e3bcfb6d37f213
  D6-v2:
    predecessor = accepted_D5-v2_digest
    supersedes = 0c78ede1551ece13c4b4fc916f60531bdc30219791bf90be574e5b0f80aa3f16
  D7-v2:
    predecessor = accepted_D6-v2_digest
    supersedes = 7ffaf92b1672aa4fb116539ca5da36aef8bc7f3caf088827fd71f3ec7b483fea
  D7G:
    predecessor = accepted_D7-v2_digest
    supersedes = null
    relation_to_D7-v2 = extends_with_global_structural_integration

reopening_lineage_rule =
  paused gate does not retain the obsolete default predecessor
  resumed successor receives a new record/version identity
  predecessor = latest accepted record in propagated serial chain
  supersedes = latest accepted record for same logical gate when one exists

successor_debt_input = complete unresolved debt union of predecessor record
superseded_gate_debt_role = provenance_and_disposition_source_only

required_D7-v2_lane_terminal_status =
  D7G_eligible_complete_candidate_transition
  | current_tranche_closed_missing_theory
  | current_tranche_closed_missing_constitutive_derivation
  | current_tranche_rejected_target_incompatibility

D7-v2_control_flow_disposition = reopen_at_named_earlier_gate

required_D7G_survivor_terminal_status =
  D8_comparable_complete_transition
  | current_tranche_closed_missing_theory
  | current_tranche_closed_missing_constitutive_derivation
  | current_tranche_rejected_target_incompatibility

D7G_control_flow_disposition = reopen_at_named_earlier_gate

zero_survivor_gate_status =
  rejected_all_candidates
  current_candidate_set_exhausted = true
  preserve_candidate_local_close_reasons = true

common_theory_gap_gate_status =
  blocked_missing_theory
  current_candidate_set_exhausted = false unless no candidate remains admitted

D8 = blocked_on_accepted_D7G_comparative_admission_or_terminal_route
```

D4-v2 execution record:

```text
decision_digest = 5862cbab0d36e1137dc647d7d21d48f77666a77bf9e7b178c830d323e4ed6309
chronological_predecessor = accepted_D7_v1
superseded_scope = accepted_D4_v1_B_C_completion_and_common_interface

B:
  selected constitutive type = bounded graph-local symmetric bilinear form
  minimal subprofile = diagonal unoriented-edge scalar
  units = H_1,pre bilinear-form units
  normalized carrier = Theta_B = H_1,pre^-1/2 T_B H_1,pre^-1/2
  locality = radius-one line-graph mask, graph-covariant and array-order independent
  signed spectrum = direction of K_4 bilinear contribution only;
                    no pre-H_4/D8 hardening or softening claim
  D7G capacity lifecycle = recompute Theta_B under accepted h_4/H_1,
                           readmit without clipping or renormalization
  authority = independent serialized nonresource
  G_B = T_B
  adapter = finite preregistered nonzero kappa_B-scaled injection into common K_4
  future current space = Omega^1(h_4^pre)
  disposition = admitted_bounded_candidate_geometry_and_carrier_completion

C:
  T_C spatial sector = source-backed
  selector = H_0,pre-weighted graph scalar spectral projector at
             Lambda_C = bar_Lambda_C sigma_L,pre with explicit units/gauge
  sigma_L,pre authority = fixed profile-owned dimensional reference,
                          not outcome-adaptive
  selector staging = pre-read fixed-rank strict-gap no-flux smooth stratum
  selector lifecycle = D7G recomputation/readmission after h_4 scale change
  inner map = pressured smooth bounded odd family with selected tanh representative
              and symmetric endpoint lift; not uniquely theory-selected
  H_M = positive graph-Hodge congruence specialized by retained T_C
  I_4M^pre = instantiated canonical metric-lowering map, not assumed isometric
  read-geometry gain = kappa_M,C
  H_M load bearing = same-state kappa_M,C on/off with nonzero r_C
  direct T_C -> K_4 adapter = not admitted
  future common structural route = T_C -> H_M -> R_C -> j_C^(M,flat)
                                   -> inverse I_4M^pre -> j_C^(phys,flat)
                                   -> graph-local j_C^phys tensor j_C^phys -> K_4
  retained geometry off = kappa_M,C zero removes H_M-conditioned J_0,C path
  read_off = chi_C zero removes explicit j_C/tensor route but preserves
             H_M-conditioned J_0,C
  gain_off = zeta_C zero blocks current/K_4 gain while preserving diagnostic
             j_C and H_M-conditioned J_0,C
  disposition = admitted_bounded_candidate_retained_geometry_completion

A = causal architecture carried unchanged; vertex-star current-tensor assembly
    is a new D4-v2 common-interface discretization result
common K_4 = assembled finite-radius graph-local symmetric bilinear forms;
             local weights live in K_4,s and exact normalization is D7G debt
inherited D7 debt binding = exact 2 immediate + 20 transitive row identities,
                            statuses, blocker flags, source SHA, and D7 digest
candidate_rejected_count = 0
architecture_selected = false
H_4 = deferred_to_D7G
D5-v2_eligible_candidate_set = [B, C]
D5-v2 = accepted_bounded
```

D5-v2 execution record:

```text
decision_digest = 212c7db173fbe286816965070a4beebd1e5ba8e39ccc3ffb73bbecde8410cf1c
chronological_predecessor = accepted_D4-v2
superseded_scope = accepted_D5-v1_B_C_and_common_comparison_only

A:
  accepted D5 operator carried unchanged
  changed causal object = false
  D6-v2 reuse requires explicit unchanged-object proof

B:
  A_B = H_1,pre^-1 T_B
  R_B = chi_B A_B
  j_B = R_B J_trial
  derivation = Riesz endomorphism of admitted symmetric bilinear carrier
  units = dimensionless operator on physical one-form current
  norm_H1(A_B) = norm_2(Theta_B) <= t_B_max
  positivity = not required; signed response allowed
  retained mediation = closed at operator level
  direct path = T_B -> kappa_B T_B -> K_4
  current path = T_B -> R_B -> j_B -> future local j_B tensor j_B -> K_4
  direct/current double counting = forbidden

C:
  R_C,M = chi_C (I + tau_C Delta_1,M)^-1
  Rbar_C = inverse(I_4M^pre) R_C,M I_4M^pre
  j_C,phys = Rbar_C J_trial,phys
  selected-content witness = nonzero physical output change
  matched-complement witness = zero output change
  kappa_M,C zero = removes retained-conditioned difference
  tau_C zero = removes retained selectivity
  retained mediation = closed at operator level on fixed-rank smooth stratum
  retained-space contraction != physical-space contraction
  direct T_C -> K_4 = not admitted

candidate_set_after_D5-v2 = [A, B, C]
D6-v2_eligible_candidate_set = [A, B, C]
physical_channel_identification_count = 0
control_rows = 60, all fail closed
chronological_predecessor_debt_dispositions = 16
superseded_D5_debt_dispositions = 27
current_typed_debts = 19
inherited_immediate_debt_rows = 2, exact identity/status/blocker binding
inherited_transitive_debt_rows = 20, exact identity/status/blocker binding
complete_live_debt_union_rows = 41
C mediation gate = at least one compatible selected-content probe changes;
                   null-direction probes may remain unchanged
D6-v2_at_D5-v2_closeout = authorized_not_started
```

D6-v2 handoff obligations:

```text
B exact regularity = classify 1 - zeta_B lambda_i(A_B)
B sufficient region = |zeta_B| t_B,max < 1
B fixed-probe path parity = T_B sign reversal flips direct K_4 and j_B,
                            but preserves fixed-probe j_B tensor j_B
B active-loop parity obligation = audit changed inverse; do not assume the
                                  solved tensor remains even

C exact regularity = similarity invariant between
                     I - zeta_C Rbar_C and I - zeta_C R_C,M
C robust conditioning = separately bounded through cond(I_4M^pre)

common staging = retained-conditioned J_0, explicit j, and future current
                 tensor remain separate with no same-beat geometry re-entry
```

D6-v2 execution record:

```text
record_id = GRC9V4-CD-D6V2-v1
status = accepted_bounded
decision_digest = ad02150010c4759d1c0ac4ba079c81cff99bad1f35b715f52b980aaf404eac0a
chronological_predecessor = accepted_D5-v2
supersedes = accepted_D6-v1

A:
  accepted D6 closure reused after exact unchanged-causal-object proof
  source candidate row canonical SHA =
    82bea78821e721c52f9d54addb21a78dcff823e82d2b9a3cf695479c4825fa6f
  no ornamental A-v2 formula

B:
  L_B = I - zeta_B chi_B H_1,pre^-1 T_B
  exact regularity = 1 - zeta_B chi_B lambda_i != 0 for every
                     generalized eigenvalue of (T_B,H_1,pre)
  sufficient uniform region = |zeta_B| t_B,max < 1
  singular locus = zeta_B chi_B = 1 / lambda_i
  operator support = radius-one line-graph locality
  solved inverse support = may propagate through the connected live-edge component
  claimed support boundary = component confinement, not one-hop preservation
  fixed-probe T_B sign reversal = sign-odd j_B, sign-even tensor
  active closed-loop sign reversal = mixed odd/even response because the
                                     inverse changes
  active closed-loop displayed formulas = chi_B = 1
  future tensor = assembled from actual solved j_B, no parity shortcut

C:
  Lbar_C = inverse(I_4M^pre) L_C,M I_4M^pre
  exact invertibility = similarity invariant
  robust physical inverse bound = kappa_bar_C / (1 - zeta_bar_C)
  robust physical margin = (1 - zeta_bar_C) / kappa_bar_C
  harmonic singular locus = zeta_C chi_C = 1
  retained-space contraction != unqualified physical-space contraction
  fixed selector, H_M, I_4M^pre, and J0_C remain pre-read

candidate_set_after_D6-v2 = [A, B, C]
D7-v2_eligible_candidate_set = [A, B, C]
current temporalization = not selected
candidate ranking = not performed

active controls = 107
active pressure rows = 130
current typed debts = 22
exact unchanged D5-v2 current debt rows = 15
explicitly superseded or narrowed D5-v2 current debt rows = 4
dropped D5-v2 current debt rows = 0
exact inherited live debt rows = 22
complete live debt union = 44

D7-v2 = accepted_bounded
D7G-v1 = accepted_bounded
D7G-v2 = accepted_bounded
D7G-post-v2_Hodge_type_correction = accepted_bounded
D7G-post-v2_Hodge_type_correction_digest = 2e2f4d53e0abf3134f586cc60467bf5881cc60414af82df35bf6ac7772400984
D8-A = accepted_bounded
D8-A_decision_digest = 5e3af8a6b8b327b3d98b5c5f6ac934ff528f048c3927a085c59194262afba021
D8_authorized = true
D8_authorized_scope = D8-A_branch_appropriate_scope_classified_structural_target_extraction_only
D8_full_continuation = blocked_on_typed_temporal_geometry_realization
named_next_route_after_accepted_D8-A = GRC9V4-GEOMETRY-TEMPORAL-REALIZATION-SUCCESSOR
geometry_temporal_realization_successor_authorized = true
```

Human acceptance: `accepted_bounded_2026-08-24`.

The candidate-local tranche has two separately attributable starting rows in
one combined D4-v2 execution:

```text
B = typed T_B plus G_B(C,T_B,...) -> S_4^B
C = T_C,C,selector context -> H_M -> h_M

common future-H_4 interface =
  S_4^a -> iota_a -> K_4^a in common K_4 domain

adapter_load_bearing_gate =
  applies to candidate claiming direct retained structural crossing
  matched lawful retained-state intervention changes K_4^a after iota_a
  structurally inert adapter does not close candidate crossing
  C direct crossing is not admitted; its source-backed current route is deferred

C provisional current-space identification =
  I_4M^pre : Omega^1(h_4^pre) -> Omega^1(h_M)
  status = candidate_local_typing_only
  final_h_4_h_M_compatibility = deferred_to_D7G

B current-space requirement =
  freeze R_B one-form/current geometry and physical-current identification
  separate h_B is optional, implicit current space is forbidden

D5-v2 B path pressure =
  if j_B tensor j_B -> K_4 is admitted, separate it from direct T_B -> K_4
  freeze read-off, gain-off, overlap, and double-count controls

D5-v2 C representation pressure =
  map j_C^(M,flat) through inverse I_4M^pre before common K_4 assembly
  equal edge-array dimension is not physical-one-form identity
```

Successful derivations propagate only through affected D5-v2, D6-v2, and
D7-v2 contracts. A lane that cannot close without arbitrary invention receives
a bounded current-tranche closure and a named future route. `routed_not_rejected`
is not a permitted D7-v2 terminal state. A sole survivor is not selected by
survival alone. Reopening is paused control flow, not scientific closure.

Only after D7-v2 closes every A/B/C candidate-local lane does D7G address
the common `K_4^a -> H_4 -> h_4` structural crossing. This ordering prevents a
global metric law from being shaped around A merely because A became concrete
first. D7G decides which candidate-local survivors become D8-comparable and
which close on a localized structural gap. D7G must emit a per-candidate
`H4_upstream_effect`; any changed upstream causal object reopens the earliest
affected gate and must propagate back to D7G before D8 admission. D7G must also
validate or replace C's `I_4M^pre` and establish a non-erasing
`delta T_a -> delta K_4^a -> delta h_4 -> later consequence` direction for
every candidate claiming structural cultivation.

For B, D7G must distinguish graph-local assembly of `j_B tensor j_B` from the
causal support of `j_B`: the D6-v2 inverse may already propagate baseline
influence throughout a connected live-edge component.

D7-v2 is accepted bounded under
`GRC9V4-CD-D7V2-v1`, digest
`f0d355c3e769b43fe48f0eb8ab6e986ce80838dd55e884ad33c66e988b65106e`.
Its terminal candidate-local partition is:

```text
A = D7G_eligible_complete_candidate_transition
B = current_tranche_closed_missing_constitutive_derivation
C = D7G_eligible_complete_candidate_transition
```

A is bound unchanged to the accepted D7 candidate row by immutable source-row
reference and canonical hash; no condensed duplicate becomes authoritative. D7-v2
supersedes D7-v1 for the comparative A/B/C partition while retaining unchanged
D7 contracts. C closes one fixed-selector-stratum formal recurrence with `C` as the sole resource and
authoritative write: continuity commits `C[k+1]`, then
`T_C[k+1] = P_M,Delta C[k+1]` is recomputed as a derived decomposition. No
independent `T_C` state or writer is admitted. Selector motion, rank change,
and event transport remain D8/D9 debt, and `h_4 <-> h_M` remains D7G debt.
Projected-sector writing and retained-conditioned mediation are closed at the
formal/operator level; effective retained write, dynamical retention,
persistence class, and stability remain open to D8.

B retains its typed independent carrier, direct candidate geometry payload,
Riesz Read-Back, and regular current closure. It closes only because no frozen
source derives the exact recursive `U_B`. A copied A writer, EMA, untyped
current tensor target, or zero-relaxation law does not close that missing
formation/retention/release arrow. This is neither B ontology rejection nor
candidate ranking. B is a complete conditional constitutive/read-current
mechanism, not a complete formative mechanism. A named source-backed writer
successor may reopen B.

The resulting ontology comparison is:

```text
A = independent retained mobility plus explicit writer
B = independent structural carrier plus conditional effects, missing formation
C = selected content of C, with no independent carrier state
```

All 22 D6-v2 current debts are dispositioned and all 22 exact inherited rows
remain bound. The 18 current D7-v2 debts preserve A/C blockers and archive B's
missing-writer obligations under an explicit nonblocking future reopening
record. A valid future `U_B` reactivates four distinct predecessor obligations
rather than superseding them: writer/lifecycle, path factorization, post-`H_4`
capacity, and absorbability. The count is 40 current-live plus exact-inherited
bound rows, four archived predecessor rows, and 44 complete lineage evidence
identities. D7G-v1 is accepted bounded and authorizes the D7G-v2
geometry-parametric closure and finalization route. D8 and all specification, implementation,
runtime, and `src/` work remain blocked.

Human acceptance: `accepted_bounded_2026-08-24`.

## D7G. Global Metric And Structural-Cultivation Closure

Authoritative structured record:
[`D7GGlobalMetricAndStructuralCultivationClosure.json`](./decisions/D7GGlobalMetricAndStructuralCultivationClosure.json)

Scientific report:
[`D7GGlobalMetricAndStructuralCultivationClosure.md`](./decisions/D7GGlobalMetricAndStructuralCultivationClosure.md)

```text
record_id = GRC9V4-CD-D7G-v1
status = accepted_bounded
predecessor_decision_digest = f0d355c3e769b43fe48f0eb8ab6e986ce80838dd55e884ad33c66e988b65106e
decision_record_digest = b173c03f7dbe55aa53b22960da2be55e42e86dda769cac1356e36499f658d071
supersedes = null

source_GRC9V3_implemented = true
source_GRC9V3_K_tensor_operational_geometry = false
source_GRC9V3_transport = scalar_base_conductance

H4_interface = H_profile(Delta_K_4,h_4_ref,context_with_K_4_base)->h_4_plus
H4_interface_status = frozen_substrate_contract_not_universal_profile
admitted_H4_reference_profile_family = reference_relative_affine_graph_Hodge_update
H4_reference_profile_status = bounded_revision_specific_family_conditional_on_E_ref
E_ref_status = pending_D7G-v2_not_defined_by_current_V3_source
H4_common_to_A_and_C = true
H4_non_erasing = true
H4_unique_core_theory_formula = false
H4_continuum_metric_claim = false

A_H4_upstream_effect = requires_geometry_parametric_closure_audit
C_H4_upstream_effect = requires_geometry_parametric_closure_audit
global_structural_disposition = H4_interface_frozen_affine_reference_profile_family_conditionally_admitted_D7Gv2_embedding_parametric_and_handoff_closure_required
D7G_complete = false
D8_authorized = false
human_acceptance = accepted_bounded_2026-08-24
```

The GRC9V3 source audit is load-bearing. `compute_hybrid_node_tensors()`
materializes the GRC9 Eq. (1) row-basis tensor into cached diagnostics, while
`compute_base_conductance()` independently rebuilds the operative scalar edge
weights from coherence, gradient mismatch, and incoming current squared. No
source consumer maps the cached tensor into conductance, potential, or flux.
The V3 spec also requires an explicit `anisotropic_edges` capability for
tensor-derived transport. D7G therefore does not relabel implemented V3 as
missing, but it also does not treat V3 as having already resolved `g[K]`.

D7G-v1 freezes a typed graph-substrate `H_profile` interface and conditionally
admits one bounded reference-relative affine graph-Hodge profile family.
`E_ref` would be an explicit V4 embedding of scalar V3 conductance into
`H_1,ref`, not a claim that V3 already possessed physical `h_4`. Current V3
source and specification do not define a unique `E_ref`, so D7G-v2 must admit
the exact embedding or close this family without instantiation:

```text
Theta_4 = kappa_H H_1,ref^(-1/2) Delta K_4 H_1,ref^(-1/2)
H_1,read+ = H_1,ref^(1/2) (I + Theta_4) H_1,ref^(1/2)
            = H_1,ref + kappa_H Delta K_4
H_0,read+ = H_0,ref
```

The domain requires `I + Theta_4` positive definite. The family is common,
graph-covariant, local in assembly, reference-neutral, and non-erasing. Exact
reference neutrality does not prove the complete disabled V4 transition
reduces to V3; that remains separate debt. This is one revision-specific
family rather than a unique core-theory, canonical V4, or continuum-metric
result. The partition identity closes
diagonal overlap multiplicity for the admitted vertex-star choice but does not
uniquely determine off-diagonal pair normalization. Local `H_1` also does not
imply local inverse or solver support.

D4-D7 are now explicitly interpreted as candidate-local results conditional on
an admitted pre-read geometry. `H_adm` contains geometry states; `P_adm`
contains profile maps landing in that class. The conditional affine family
supplies an algebraic witness for a supplied reference, not an instantiated
embedding or closure over all admitted profiles. Physical `h_4` remains distinct from
transport mobility unless an explicit factorization states otherwise. Both A
and C therefore pause for D7G-v2 geometry-parametric closure; neither receives
a terminal scientific disposition or D8 admission.

D7G-v1 acceptance authorizes the append-only next gate:

```text
D7G-v2 = A/C geometry-parametric closure under H_profile
```

D7G-v2 must freeze quantitative `H_1` lower/upper bounds, C selector gap,
`I_4M` conditioning, and D6 regularity margins before evaluation. It must also
close how postsolve `h_4+[k]` reaches a later transition: deterministic
reconstruction from committed Markov state, precommit consumption into an
admitted committed effect, or a named D1 successor. Cache history is forbidden.

Pre-acceptance is governed by `D7G-v2-PREACCEPT-v1`. Its 12 passes cover
definitions, quantifiers/bounds, geometry/profile class separation,
reference/base closure, causal-state graph, A proof, C proof, causal
non-erasure, authority mutation, neutral/full reduction separation, claim
audit, and machine integrity/lineage. Every load-bearing statement must resolve
to a definition, derivation/reproducible witness, bounded restriction, or named
debt outside the consumed claim ceiling.
The protocol permits asymmetric candidate receipts and forbids broadening the
admissible class merely to place both A and C into D8.

D7G-v2 owns the remaining D7G chain closure, final A/C dispositions, and any
triggered zero-survivor/hard-blocker route. Those tasks are not written back
into D7G-v1. Work discovered after accepted D7G-v2 must be named
`D7G-post-v2` or reopen the earliest affected gate explicitly.

An earlier D4-D7 gate reopens only if a profile leaves the admitted class,
changes state/write authority or same-beat staging, or invalidates a declared
operator family. Profile change alone does not trigger a restart.

The 18 D7-v2 current debts are explicitly dispositioned. The D5-v2 reference
continues to bind all 22 exact inherited rows, and B's four archived
obligations remain attached to its named future writer reopening. The current
ledger contains 26 typed D7G debts plus the 22 exact inherited rows, with four
additional archived B predecessor identities retained as evidence. No debt is
silently dropped.

D7G-v1 supports `delta T_a -> delta K_4^a -> delta h_4` for A and C under the
bounded affine family conditional on a supplied admissible reference surface.
It does not support an admitted exact `E_ref`, complete disabled-transition
reduction, a lawful cross-beat geometry handoff, or the later transition
consequence, complete structural cultivation, stability, runtime evidence,
architecture selection, specification, or implementation.

### D7G-v2. Geometry-Parametric Closure And Finalization

Authoritative structured record:
[`D7Gv2GeometryParametricClosureAndFinalization.json`](./decisions/D7Gv2GeometryParametricClosureAndFinalization.json)

Scientific report:
[`D7Gv2GeometryParametricClosureAndFinalization.md`](./decisions/D7Gv2GeometryParametricClosureAndFinalization.md)

```text
record_id = GRC9V4-CD-D7G-v2
status = accepted_bounded
predecessor_decision_digest = b173c03f7dbe55aa53b22960da2be55e42e86dda769cac1356e36499f658d071
decision_record_digest = c52912d83797ee294799709b3e770574043df37f80073b51eebfaf8b2fd27efb

E_ref_status = admitted_revision_specific
affine_profile_status = instantiated_bounded
A_receipt = bounded_candidate_local_transition_and_profile_receipt_selected_lagged_explicit_geometry_feedback_unresolved
C_receipt = bounded_candidate_local_transition_and_profile_receipt_selected_lagged_explicit_geometry_feedback_unresolved
D8-A_structural_target_candidate_set = [A, C]
D8_full_continuation_comparable_candidate_set = []
global_blocker = selected_lagged_explicit_realization_missing_geometry_feedback_completion
C_internal_D_h_pre = load_bearing_and_conditionally_nonzero_on_named_strict_gap_directions
D_h_pre_J_C = nonzero_sensitivity_not_established
D_h_pre_F_C = load_bearing_not_identically_excluded_nonzero_full_transition_sensitivity_unproved
D_h_generated_F_A_C = undefined_absent_Gamma_or_equivalent_complete_realization
D7G_profile_stage_audit_complete = true
D7G_global_structural_cultivation_complete = false
named_successor = GRC9V4-GEOMETRY-TEMPORAL-REALIZATION-SUCCESSOR
D8-A_ready_after_human_acceptance = true
D8-A_authorized = true
D8_authorized = true
D8_authorized_scope = D8-A_branch_appropriate_scope_classified_structural_target_extraction_only
control_rows = 39
human_acceptance = accepted_bounded_2026-08-24
```

D7G-v2 admits
`H_0,ref = diag(mu_V3)` and `H_1,ref = diag(W_V3^-1)` as an explicit
revision-specific V4 reference embedding. The edge convention consumes B1's
primary native constitutive metric; the runtime's regularized inverse-
conductance label is not substituted for that exact map. This instantiates the
bounded affine graph-Hodge profile while preserving the distinction between
physical geometry, transport mobility, and A's authoritative `W_A`.

The gate freezes separate `H_adm` geometry-state and `P_adm` profile-map
classes, an 18-row load-bearing symbol registry including the future typed
`S_H` interface, candidate-specific `Gamma_a`, and branch-appropriate
`C_struct,a`, a 13-row quantifier ledger, and
explicit lower/upper geometry, selector-gap, identification-condition, and D6
regularness bounds. Candidate A remains regular over supplied admitted
geometry without making that geometry load-bearing; this is an invariance/type
receipt, not demonstrated geometry sensitivity. Candidate C has a bounded
strict-gap SPD supplied-geometry domain in which `P_M`, `H_M`, `I_4M`, `R_C`,
`J0_C`, and its current closure are well defined. Geometry is load-bearing in
that internal chain, but nonzero `D_(h_pre) J_C` and `D_(h_pre) F_C` remain
unproved because downstream cancellation, annihilation, and divergence-free
response have not been excluded.

Neither result closes structural cultivation. A's accepted writer does not
consume postsolve `h_4+`; C commits only `C` and cannot reconstruct prior
postsolve `h_4+` from that poststate. Thus both explicit runtime chains stop
after nonzero `delta h_4` under the selected lagged D6/D7 realization. This is
a realization-relative feedback gap, not a terminal candidate-local A/C
failure, a general V4 impossibility, or evidence that core requires a
cross-beat handoff.

D7G-v2 separates:

```text
delta h_4 -> delta branch-appropriate structural continuation object
D_(h_pre) F_a
D_(h_generated) F_a,later through Gamma_a or an equivalent realization
```

A and C are ready, only after D7G-v2 acceptance, for bounded D8-A extraction
of branch-appropriate structural objects and target directions classified as
realization-invariant, accepted-lagged-branch-relative, or not finalizable
before realization. The generated-geometry derivative is currently undefined
rather than zero. D8-A is an analysis consumer of `h_4+`, not a runtime causal
consumer. Full continuation comparison remains blocked. Neither candidate is
rejected, ranked, or selected.

The gate does not reopen D1-D7 by procedure. D8-A must first derive the
branch-appropriate reduced, joint, nonselfadjoint, or DAE continuation object
and scope its target directions; only invariant targets constrain every
successor, while lagged-branch targets require D8-B rederivation after changed
slaving. Repeating the already known absent-`Gamma_a` diagnosis is not
evidence. The named successor then pressures coupled/implicit, operator-split
same-beat, persistent-carrier, and reconstructed-geometry families as a
non-exhaustive minimum set under the same burden of proof. Its typed `S_H`
interface cannot close the successor by itself: at least one bounded complete
realization must be instantiated and pressured. Failure of all four is not V4
impossibility without a separate completeness proof; otherwise the search
broadens or closes bounded unresolved. A and C need not use identical equations
when their retained ontologies independently justify different realizations.
D8-B must match realization families where meaningful or treat each
`(candidate, realization)` pair as an architecture and isolate realization
effects. Only an admitted realization reopens the earliest affected owner or
stage. Cache-only history, least-incomplete selection, and promotion of the
lagged realization into a core requirement are fail-closed.

All 26 D7G-v1 debts have one explicit disposition. The live D7G-v2 ledger has
24 typed debts, continues to bind the 22 exact inherited rows, and preserves
the four archived B obligations. No runtime, normative specification,
implementation, or `src/` authority is opened.

### D7G-post-v2 Graph-Hodge Type Correction

Status: accepted bounded. The narrow correction receipt separates
`H1_form`, the structural one-form Hodge/Dirichlet weight, from `G_J`, the
dual current/flux resistance metric and flat map, and from causally distinct
transport mobility `M4`. The simple V3 reference is
`H1_form = diag(W)` and `G_J = diag(W^-1)`. Candidate C's physical response is
retagged as an explicit flux/flat/response/sharp/flux composite. The accepted
identity-metric witness survives within binary roundoff, but general
nonidentity conditioning remains pre-D10 debt. Physical `j_flux` remains the
continuity current, while structural `K4` consumes lowered
`j_struct^flat tensor j_struct^flat`. The correction freezes the variable-
metric tangent and a nonidentity tensor-separation regression. Candidate-
specific `iota_a` adapters preserve accepted payload gains; no common
`kappa_K` is introduced. Accepted historical records and candidate
dispositions are unchanged. D8-A consumes this correction under their joint
accepted-bounded status.

## D8. Continuation Realization And Analysis Contract

Status: D8-A is accepted bounded. It derives branch-appropriate continuation
objects and classifies
targets as realization-invariant, accepted-lagged-branch-relative,
accepted-lagged-branch work not yet instantiated, or genuinely not finalizable
before realization. It does not classify stability or compare completed
temporal architectures.

```text
D8-A = GRC9V4-CD-D8A-v1
status = accepted_bounded
human_acceptance = accepted_bounded_2026-08-24
predecessor_decision_digest = c52912d83797ee294799709b3e770574043df37f80073b51eebfaf8b2fd27efb
decision_record_digest = 5e3af8a6b8b327b3d98b5c5f6ac934ff528f048c3927a085c59194262afba021

A_object = conditional_C_given_W_A_reduced_form_on_smoothly_slaved_branch
C_object = C_only_exact_derived_sector_reduced_form_on_smoothly_slaved_branch
graph_Hodge_type_correction = D7G-post-v2_H1_form_G_J_M4_separation
H1_form_ref = diag(W_V3)
G_J_ref = diag(W_V3^-1)
M4_authority = causally_distinct_transport_mobility
C_physical_pipeline = flux_to_flat_to_Hodge_response_to_sharp_to_flux
C_structural_rank_one_input = j_struct_flat_tensor_j_struct_flat_before_sharp
A_structural_rank_one_input = G_J_pre_j_A_flux_tensor_G_J_pre_j_A_flux
structural_gain_authority = candidate_specific_iota_a_no_common_kappa_K
lagged_delta_G_J_pre = 0
variable_metric_successor_rule = retain_(delta_G_J)_j_flux
common_direct_field_target = exact_kappa_C_(d0_u)^T_delta_H1_form_(d0_v)
delta_H1_form = kappa_H_delta_K4
complete_Hessian_response = not_finalized

target_scope_rows = 10
realization_invariant = 4
accepted_lagged_branch_relative = 2
accepted_lagged_branch_not_instantiated = 2
not_finalizable_before_temporal_realization = 2

full_lagged_branch_Hessian = potentially_derivable_before_temporal_synthesis_not_instantiated
lagged_alpha = potentially_computable_before_temporal_synthesis_not_instantiated
generated_geometry_later_transition_and_gamma_mu = genuinely_temporal_realization_dependent

nonzero_delta_K4_implies_nonzero_complete_structural_target = false
alpha_or_gamma_assigned = false
stability_classified = false
candidate_ranking = false
architecture_selected = false

predecessor_debt_dispositions = 24
correction_debt_dispositions = 5
current_typed_debts = 28
controls = 40
runtime_or_src_changed = false

joint_acceptance_of_Hodge_type_correction_required = true
successor_ready_if_accepted = GRC9V4-GEOMETRY-TEMPORAL-REALIZATION-SUCCESSOR
successor_authorized = true
D8-B_authorized = false
```

The exact positive result is the direct field metric-response target under the
typed D7G-post-v2 correction. D5's structural one-form Hodge uses the
conductance-like `H1_form`; B1-GR's inverse-conductance object survives as the
dual current metric and flat map `G_J`; `M4` remains causally distinct
transport mobility. Candidate C now has an explicit
flux/flat/response/sharp/flux chain. Its identity-metric witness survives
within binary roundoff, while nonidentity conditioning remains pre-D10 debt.
The structural route branches before sharp: physical `j_flux` goes to
continuity, while lowered `j_struct^flat` enters the rank-one `K4` map. The
accepted lagged rows set `delta G_J,pre = 0` because pre-read geometry is
frozen; successors with variable `G_J` inside the chain must retain the
additional metric-variation term.
The result remains bounded because the constrained pullback can vanish and
because the full induced-geometry and constraint second variations are not
instantiated. The `H0`-weighted matrix representative
includes `kappa_C`, and target orthogonality uses the declared `H0`-weighted
candidate structural inner product. A's candidate-generated
pullback and C's exact-selector pullback use the accepted D6-v2 lagged slaving
and therefore must be rederived when a successor changes that relation. The
candidate authority boundaries and direct metric-response map are the
realization-invariant constraints.

The full accepted-lagged-branch Hessian and its `alpha` spectrum are
potentially derivable before temporal synthesis, but D8-A does not instantiate
them. Generated-geometry influence on a later transition and temporal
`gamma`/`mu` remain genuinely blocked on a complete temporal realization. The
accepted predecessor digest `c52912d...` and file SHA `364b1b05...`, plus the
correction digest `2e2f4d5...` and file SHA `bbef6c3...`, were independently
recomputed exactly during the revision.

The authoritative records are
[`D7GPostv2GraphHodgeTypeCorrection.json`](./decisions/D7GPostv2GraphHodgeTypeCorrection.json),
its
[`interpretation`](./decisions/D7GPostv2GraphHodgeTypeCorrection.md),
[`D8ABranchAppropriateStructuralTargetExtraction.json`](./decisions/D8ABranchAppropriateStructuralTargetExtraction.json)
and
[`D8ABranchAppropriateStructuralTargetExtraction.md`](./decisions/D8ABranchAppropriateStructuralTargetExtraction.md).

D8-B remains blocked on a concrete typed temporal geometry realization. A
realization may enter D8-B after freezing complete equations, state authority,
stage order, fixed-stratum Markov closure, conservation/accounting, design
covariance, failure semantics, bounded local well-posedness/regularity, and a
linearization surface. It must declare disabled behavior, lifecycle
requirements, and stability-analysis surfaces, but exact V3 reduction and full
topology/event lifecycle remain D9 debt while stability classification remains
D8-B work. Requiring those later results before admission is fail-closed as
circular governance.

## Geometry-Temporal Realization Successor: Coupled/Implicit

Status: accepted bounded.

```text
record = GRC9V4-GTRS-CI-v1
status = accepted_bounded
decision_record_digest = a0292d35d3dfc18e6386a78c26ae9bc2a4b6de9f31e505cf67edf7c094aea3a3
human_acceptance = accepted_bounded_2026-08-25

family = coupled_implicit
unknown_A = (J_A_flux, h_A)
unknown_C = (J_C_flux, h_C)
C_reference = accepted_D6v2_C_root_transferred_through_Q_C_similarity_at_kappa_H_zero_and_h4_ref
C_reference_full_block = [[L_C_flux_ref, B_C], [0, I]]
C_reference_full_block_invertible = true
C_old_physical_singular_margin_reused = false
C_Q_C_conditioning_required = true
C_local_IFT_branch = accepted_bounded_candidate
A_reference = accepted_D6_D7_A_root_with_reference_relative_geometry_correction_zero
A_reference_full_block = [[L_A, B_A], [0, I]]
A_reference_full_block_invertible = true
A_local_IFT_branch = accepted_bounded_candidate
C_global_branch = unsupported
A_global_branch = unsupported
A_C_numeric_uniform_epsilon = unsupported
A_C_temporal_stability = unsupported

C_structural_path = J_flux_to_G_J_flat_to_retained_intrinsic_response_to_chi_C_causal_j_flat_to_zeta_C_iota_C_K4_to_H_profile
C_physical_path = chi_C_causal_j_flat_to_G_J_sharp_to_j_flux_to_zeta_C_current_closure_and_continuity
C_ungated_resolvent = Rhat_C_M=(I+tau_C_Delta_1_M)^-1
C_historical_D5v2_gated_R_C_M_notation_reused = false
C_zeta_squared = false
C_zeta_external_to_iota_C = true
C_I_4M_signature = I_4M(T_C,h)
C_full_regularness_object = joint_J_h_block
C_lagged_L_C_is_full_regularness_object = false
C_delta_G_J_J_retained = true
C_projected_visibility_test_frozen = true
C_projected_visibility_witness = passed_formal_constitutive_direct_field_visibility_not_runtime_evidence
C_projected_visibility_pre_adapter_value = -0.014842807194071116
C_nonempty_visible_subdomain_proven = true

A_equal_burden = applied
A_result = accepted_bounded_complete_reference_relative_coupled_realization_candidate
A_geometry_consumer = Phi_A_D7_plus_kappa_Ah_times_Delta0_h_minus_Delta0_href_applied_to_C
A_kappa_Ah_units = Phi_A_per_Delta0_times_C
A_kappa_Ah_enabled_profile = +1.0_in_declared_unit_basis_preregistered_before_D8B
A_kappa_Ah_ablation = 0
A_kappa_Ah_sign = revision_specific_not_theory_fixed
A_W_hat_stage = recomputed_inside_every_joint_root_residual_after_J0_A_CI_and_before_q_A
A_zeta_external_to_iota_A = true
A_mobility_owner = W_A_only
A_writer = accepted_D7_postcontinuity_writer_unchanged
A_direct_h_to_W_A_writer = false
A_full_regularness_object = joint_J_h_block
A_projected_visibility_witness = passed_formal_constitutive_direct_field_visibility_not_runtime_evidence
A_projected_visibility_pre_adapter_value = 0.41999999999999993
A_nonempty_visible_subdomain_proven = true
A_rejected = false
A_or_C_selected_or_ranked = false
B_reopened = false

predecessor_debt_dispositions = 28
carried_predecessor_debts = 23
resolved_predecessor_projected_visibility_debt = 1
current_successor_debts = 10
live_debt_union = 33
controls = 55
remaining_family_pressure_complete = false

architecture_local_D8B_A_authorized = true
architecture_local_D8B_C_authorized = true
comparative_D8B_authorized = false
runtime_or_src_changed = false
```

Candidate C supplies a complete same-step root because its accepted geometry
chain is already load-bearing in `J0_C` and the retained response. This
successor names the ungated resolvent
`Rhat_C,M = (I + tau_C Delta_1,M)^-1`; historical D5-v2 notation that included
`chi_C` inside `R_C,M` is not reused. The causal read is
`j_C^flat = chi_C r_C^flat`. The shared `zeta_C` gain appears once in the
current use and as an external multiplier of `iota_C(A_star(j_C^flat))`, so no
adapter homogeneity or hidden squared gain is assumed. `I_4M(T_C,h)` exposes
the full selector/retained-metric dependency.

At `kappa_H = 0`, the physical current block is exactly similar to the
accepted retained D6-v2 block through `Q_C = I_4M G_J`. Exact invertibility
therefore transfers, while robust physical conditioning separately requires a
finite `cond(Q_C)` and a new inverse bound. With the identity geometry block,
the implicit function theorem admits a unique local smooth C branch on the
declared fixed-rank, fixed-topology, smooth SPD domain.

The root uses independent symmetric `H1_form` coordinates in the fixed
oriented-edge basis; all other geometry/current metric objects are derived or
candidate-owned, so the residual is square. This is a revision-distinct C
successor to D6 staging. Accepted D6-v2 bytes remain unchanged, C retains its
D7 state authority, and the changed joint solve stage is propagated into the
D8-B rederivation burden.

Away from the reference point, the full joint block includes all active
selector, retained-Hodge, identification, flat/sharp, profile, baseline, and
structural derivatives. It explicitly retains `(delta G_J) J`. A Schur
complement is subordinate to separate geometry-pivot regularity.

The declared D8-B surface is `D_X Y_C = -B_full,C^-1 D_X F_C`, followed by
continuity and the C commit map. `kappa_H = 0` reduces to the accepted D6-v2 C
root only; complete V3 reduction and topology/event lifecycle remain D9 debt.

Candidate A uses D4's accepted geometry/mobility separation and D7's exact
baseline and writer. The reference-relative profile
`Phi_A^CI = Phi_A^D7 + kappa_Ah [Delta_0(h)-Delta_0(h_ref)] C` makes generated
geometry load-bearing in `J0_A` while `W_A` remains the sole mobility owner.
At `h = h_ref`, the correction vanishes and the accepted A baseline returns
exactly. The accepted D7 writer remains unchanged and has no direct `h` input.
`kappa_Ah` has units `[Phi_A]/([Delta_0][C])`, uses the preregistered enabled
value `+1.0` in that unit basis, and uses zero only as the explicit geometry
consumer ablation; its sign is revision-specific and may not be tuned after
D8-B results. `W_hat_A(h)` is recomputed inside every joint-root residual after
`J0_A^CI(h)` and before `q_A`. The structural gain `zeta_A` remains external to
`iota_A`. The accepted A current margin and identity geometry block provide a
local IFT branch on the smooth `G_W` floor-inactive chart.

The successor closes D8-A's projected-target witness burden for both branches.
The D5-v2 C selected-sector receipt gives pre-adapter projected value
`-0.014842807194071116`; an admissible A three-node star receipt gives
`0.41999999999999993`. For the accepted non-erasing adapters, a connected
three-node tree maps the zero-sum node tangent isomorphically onto the two-edge
form space, so each nonzero post-adapter symmetric metric variation has some
lawful projected pair. These are formal constitutive direct-field visibility
receipts only, not runtime, complete transition-chain, Hessian, temporal, or
stability evidence.

This accepted record authorizes Candidates A and C separately for
architecture-local D8-B rederivation. Cross-candidate and cross-family
comparison remains blocked. The
operator-split, persistent-carrier, and reconstructed families remain open for
successor-family completeness and architecture selection.

The authoritative records are
[`GeometryTemporalRealizationSuccessorCoupledImplicit.json`](./decisions/GeometryTemporalRealizationSuccessorCoupledImplicit.json)
and its
[`scientific interpretation`](./decisions/GeometryTemporalRealizationSuccessorCoupledImplicit.md).

## D9. Complete Step And Lifecycle Contract

Status: blocked on architecture-local D8-B completion plus the remaining
realization-family pressure and comparative/selection boundary.

## D10. Design Synthesis And Spec-Writing Decision

Status: blocked on D9 or explicit early terminal route.

Permitted final dispositions:

```text
authorize_GRC9V4_specification
reopen_named_design_gate
route_to_named_theory_or_constitutive_derivation
close_current_design_tranche_unresolved
```

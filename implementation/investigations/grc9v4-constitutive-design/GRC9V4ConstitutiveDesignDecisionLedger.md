# GRC9V4 Constitutive Design Decision Ledger

**Status:** D0-D7 and D4-v2-D6-v2 accepted bounded; D7-v2 authorized; D7G-D8 blocked

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

Status: D4-v2 through D6-v2 accepted bounded; D7-v2 authorized but not
started; later gates blocked.

This append-only tranche does not modify or supersede accepted D4-D7 until a
specific successor record is accepted. It prevents A's earlier completeness
from becoming an implicit selection criterion and gives B, C, and the global
structural map their named derivation attempts before comparative D8.

```text
D4-v2 = GRC9V4-CD-D4V2-v1, accepted_bounded
D5-v2 = GRC9V4-CD-D5V2-v1, accepted_bounded
D6-v2 = GRC9V4-CD-D6V2-v1, accepted_bounded
D7-v2 = GRC9V4-CD-D7V2-v1, authorized_not_started
D7G = GRC9V4-CD-D7G-v1, blocked_on_D7-v2

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

D7-v2 = authorized_not_started
D7G = blocked_on_D7-v2
D8 = blocked_on_D7G_or_terminal_route
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

## D8. Continuation Realization And Analysis Contract

Status: blocked pending accepted D7G comparative admission or an explicit
terminal closeout route.

## D9. Complete Step And Lifecycle Contract

Status: blocked on D8.

## D10. Design Synthesis And Spec-Writing Decision

Status: blocked on D9 or explicit early terminal route.

Permitted final dispositions:

```text
authorize_GRC9V4_specification
reopen_named_design_gate
route_to_named_theory_or_constitutive_derivation
close_current_design_tranche_unresolved
```

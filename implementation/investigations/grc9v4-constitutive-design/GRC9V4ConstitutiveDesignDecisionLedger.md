# GRC9V4 Constitutive Design Decision Ledger

**Status:** D0-D10.2 accepted bounded; GRCv4/GRC9v4 specification writing authorized; implementation remains unauthorized

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

## D8-B. Coupled Architecture-Local Continuation Analysis

Status: accepted bounded.

```text
record = GRC9V4-CD-D8B-CI-v1
status = accepted_bounded
decision_record_digest = 53ed6d6ee616ab42c59ce6dabb6bc106a595f5c70ad1acaedc445c7fa73a5b7f
predecessor = GRC9V4-GTRS-CI-v1
predecessor_decision_digest = a0292d35d3dfc18e6386a78c26ae9bc2a4b6de9f31e505cf67edf7c094aea3a3

family = coupled_implicit
architecture_local_rows = [A, C]
cross_candidate_comparison = blocked
cross_family_comparison = blocked

implicit_first_derivative = D_X_Y_a=-B_a^-1_D_X_F_a
implicit_second_derivative = full_XX_XY_YX_YY_chain
classical_second_variation_chart = C2_required
A_structural_domain = conditional_C_given_fixed_W_A
C_structural_domain = C_only_exact_derived_T_C_tangent
A_complete_step_domain = (C,W_A)
C_complete_step_domain = C

structural_alpha_surface = charge_parametric_defined_not_numerically_instantiated
temporal_mu_gamma_surface = defined_not_numerically_instantiated
direct_beta_surface = defined_not_numerically_instantiated
direct_response_singular_value_surface = defined_separately_from_beta
intrinsic_response_gain_rule = beta_a=zeta_a*r_a
spatial_lambda_surface = defined_not_numerically_instantiated
moving_branch_temporal_object = U_kplus1_to_ref*M_k*U_ref_to_k_transported_Jacobian_cocycle
projector_transport = defined
covariance = defined_at_design_level
nonnormality_tests = defined

formed_V4_branch_instantiated = false
numeric_spectrum_rows = 0
full_chain_nonannihilation_witnesses = 0
structural_or_temporal_stability = unsupported
candidate_ranking = false

B1_B2_discriminator_rows = 8
immediate_predecessor_debt_dispositions = 10
transitive_predecessor_debt_dispositions = 23
current_successor_debts = 7
live_debt_union = 34
controls = 54

D9_authorized = false
runtime_or_src_changed = false
```

The result derives each operator from the accepted coupled root instead of
reusing D8-A's lagged pullback. The structural object uses the full implicit
second derivative of the candidate-local geometry branch on a declared `C2`
subchart. The graph-field Hessian includes first- and second-order geometry
slaving. Constraint curvature and measure dependence remain inside the
differentiated Lagrangian, while projector transport is a comparison operation,
not additive Hessian curvature. The complete-step conserved charge/projector
remains typed D9/pre-D10 debt rather than being inferred from `H0`. Candidate A remains
conditional C structure with `delta W_A = 0`; Candidate C remains C-only and
retains the exact derived selector tangent. The temporal object is the complete
committed-state Jacobian, not the root block and not a relabeled structural
Hessian. Intrinsic response `r_a`, spectral enacted
`beta_a = zeta_a r_a`, separately reported response singular values, temporal
`mu`/`gamma`, structural `alpha`, retained-sector `lambda_M`, and spatial
`lambda` remain different analytical objects. Moving branches transport each
Jacobian output from `k+1` or transport only the native cocycle endpoints.

The accepted design sources do not instantiate a formed V4 critical branch,
functional normalization values, or numerical root derivatives. D8-B
therefore records exact operator and falsification surfaces but emits no
numeric spectrum and no stability result. The A and C direct-field visibility
receipts remain insufficient for a complete-chain nonannihilation claim.
B1/B2 contribute discriminator and control methods only; V3 numeric outputs
are not promoted to V4 evidence.

The authoritative records are
[`D8BCoupledArchitectureLocalContinuationAnalysis.json`](./decisions/D8BCoupledArchitectureLocalContinuationAnalysis.json)
and its
[`scientific interpretation`](./decisions/D8BCoupledArchitectureLocalContinuationAnalysis.md).

## Remaining Realization-Family Pressure

Status: `GTRS-OS`, `GTRS-RG`, `GTRS-PC`, and `GTRS-COMP` accepted bounded;
`GTRS-CI-PC` is authorized.

```text
execution_order = operator_split_same_beat -> reconstructed_geometry -> persistent_structural_carrier -> comparative_realization_synthesis
ordering_is_architecture_ranking = false
common_question = can_this_family_produce_a_bounded_complete_step_from_existing_A_C_constitutive_content
row_dispositions = [bounded_complete_realization, candidate_local_blocker, family_level_obstruction, bounded_unresolved]
D8A_rerun_required_for_admission = false
numeric_alpha_mu_gamma_required_for_admission = false
D9_before_family_pressure = false
```

Operator-split receives first pressure because it is the closest causal
alternative to the coupled root and tests explicit versus implicit same-beat
feedback with minimal new ontology. Reconstructed geometry follows to test
whether authoritative state already suffices. Persistent carrier is last
because it introduces state and lifecycle authority. Comparative synthesis
then enumerates the actual architecture population and separates candidate
effects from realization effects before D9.

### GTRS-OS: Operator-Split Same-Beat

The preregistered primary realization uses exactly one predictor, one geometry
update, one fixed-geometry corrector, and one atomic commit. A second geometry
update from the corrector current is forbidden in this row. Both A and C admit
bounded local equation-level complete realizations without new persistent
state:

```text
A = bounded_complete_realization
C = bounded_complete_realization
```

The family exposes rather than hides its closure defect:

```text
r_h^OS = h^(1) - H_profile(K4_base + Delta K4(J^(1),h^(1))).
```

Because the corrector solves the fixed-geometry current equation exactly, the
authoritative residual identity is

```text
F_a^CI(J_a^(1),h_a^(1)) = (0,r_h,a^OS).
```

The pair is current-consistent with the coupled equations and leaves only the
geometry fixed point unclosed. The structural map remains `K_4`-valued and
enters the relative `H1_form` operator norm only through the typed affine
profile adapter `P_0: K_4 -> T_h H1_form`. With
`g_0=||P_0||_(K->H)`, the D8-B `C2` subcharts and named current/structural
Lipschitz constants give

```text
||r_h^OS||
  <= |kappa_H|^2 g_0^2 L_S M_S (1+L_C).
```

The corresponding first-Picard-iterate comparison has the bound
`|kappa_H|^2 L_T M_G / (1-|kappa_H| L_T)` when
`|kappa_H| L_T < 1`. No `O(Delta_t)` order, nonsmooth-boundary extension, or
numeric bound is claimed.

The result establishes explicit equation-level geometry consumers in A and C,
not executed nonzero complete-state effects. The latter remain tied to
`D_h J_a^(1) = -(D_J F_J,a)^(-1) D_h F_J,a` and the two current OS witness
debts. A's mobility/writer authority, C's derived `T_C`, exact switch
semantics, final-current accounting, and failure atomicity remain unchanged.
The result adds no runtime state and makes no source change.

The authoritative records are
[`GeometryTemporalRealizationSuccessorOperatorSplit.json`](./decisions/GeometryTemporalRealizationSuccessorOperatorSplit.json)
and its
[`scientific interpretation`](./decisions/GeometryTemporalRealizationSuccessorOperatorSplit.md).

### GTRS-RG: Reconstructed Geometry

GTRS-RG-v1 separates same-beat family identity, reconstruction as a property of
an already complete transition, and a distinct lagged invariant-section
architecture.

```text
RG-1 exact same-beat reconstruction = coupled/implicit equivalence
RG-1 staged same-beat reconstruction = operator-split equivalence

RG-2a existing CI/OS local reconstruction = G_a o local_inverse(Phi_a)
RG-2b lagged invariant section = Gamma_a o Phi_a,lag = G_a
```

An exact closed-form, symbolically eliminated, generated, or otherwise reduced
same-beat evaluator may exist. When it reproduces the fixed point exactly it is
constitutively CI-equivalent, not a third family. RG-1 therefore closes both A
and C as `family_level_obstruction` for distinct family identity.

RG-2a closes locally because A and C complete commit maps extend to identity at
`Delta_t=0`; derivative continuity and the inverse function theorem provide
local poststate reconstruction for small step size. This remains a CI/OS
property, not a distinct family.

RG-2b closes the original lagged step. At `kappa_H=0`, `Gamma_a=h_ref` is an
exact constant invariant section and the section derivative of the graph
transform vanishes. A frozen, equivariant family-local extension/profile
completion supplies one fixed base domain and a global inverse for the
extended near-identity base map. Nested domains
`K_- compactly contained in K compactly contained in U` and
`Psi_(a,Gamma)(K_-) subset K` ensure that every claimed transition on `K_-`
uses only the accepted candidate maps on `K`. Typed `epsilon_H`, value and
Lipschitz self-map bounds, and the corrected `C0` contraction give a unique
local Lipschitz invariant section for A and C relative to that frozen
completion. Extension-independent uniqueness is not claimed. The completion
is profile configuration, not serialized geometry, runtime state, history, or
trajectory-dependent tuning. `C1` regularity remains separate analysis debt.

```text
record = GRC9V4-GTRS-RG-v1
status = accepted_bounded
top_level_disposition = bounded_local_reconstructed_geometry_family_complete_A_C
decision_record_digest = dce24993ac0dd39a5fa5bcd35e46d9166fa28628d3811e9b33724c210ada4c0b

RG1_A = family_level_obstruction
RG1_C = family_level_obstruction
RG2_A = bounded_complete_realization
RG2_C = bounded_complete_realization
existing_CI_OS_local_poststate_reconstructibility = supported
exact_state_only_formula_nonexistence = not_claimed
universal_impossibility = false

predecessor_live_debts = 37
predecessor_debt_dispositions = 37
current_successor_debts = 3
live_debt_union = 39
controls = 62

GTRS_RG2_authorized = false
GTRS_PC_authorized_after_acceptance = true
GTRS_PC_authorized = true
D9_authorized = false
runtime_or_src_changed = false
```

The zero-duration limit is a smooth-extension reference, not an executed step.
The result does not provide numeric theorem radii, global reconstruction,
event continuation, `C1` section regularity, or extension-independent
uniqueness. Context is fixed. `Gamma_a` is the unique section relative to the
frozen equivariant family-local completion, not an independently authored
runtime law; fitting or updating it from trajectory history would be hidden
authority.

GTRS-PC tests independently retained structural state beyond the local RG
domain without requiring local inversion or a single-valued invariant section.
Representation-preserving context continuation is admissible, while base-state
hysteresis remains a complete-chain claim. It cannot start from an assumed
local information deficit or default to storing full `h`.

The authoritative records are
[`GeometryTemporalRealizationSuccessorReconstructedGeometry.json`](./decisions/GeometryTemporalRealizationSuccessorReconstructedGeometry.json)
and its
[`scientific interpretation`](./decisions/GeometryTemporalRealizationSuccessorReconstructedGeometry.md).

### GTRS-PC: Persistent Structural Carrier

GTRS-PC-v1 pressures one preregistered carrier architecture for A and C. Add
one authoritative bounded structural coordinate

```text
Z_4,a,k in B_R,a subset K_4,a
h_a,k = H_profile(K_4,base + Z_4,a,k).
```

After the accepted fixed-geometry current solve, the existing typed structural
path produces `S_a,k=Delta K_4,a(J_C,a,k,h_a,k)`. The sole carrier writer is

```text
a_PC,k = exp(-Delta_t,k/tau_PC,a)
Z_4,a,k+1 = a_PC,k Z_4,a,k + (1-a_PC,k) S_a,k.
```

Carrier admission is constructive rather than assumed. In a declared `K_4`
norm, the exact criterion is `m_a(R)<=R` for the source supremum over compact
`K_X,a x B_R,a`, together with profile admissibility. The sufficient theorem
uses `||S||<=M_0+L_Z||Z||`, `L_Z<1`, and
`M_0/(1-L_Z)<=R<=min(R_profile_adm,R_reg)`. Every `(X,h(Z))` must remain in the
candidate's fixed-geometry regular domain with uniform
`sigma_min(D_J F_J)>=m_J>0`; A includes floor-inactive positive-domain
conditions and C includes fixed rank and strict gap. Convexity then preserves
the admitted ball without clipping. The theorem is parametric; no numerical
constants or unconditional domain are claimed. For positive duration,
`0<a_PC<1` provides formation, retention at every finite time, asymptotic
no-source release, bounded maintenance, and reconfiguration. The zero-duration
`a_PC=1` case is an identity reference only.

For variable steps, zero-source and constant-source convergence require
accumulated elapsed time `sum Delta_t -> infinity`. On the sufficient chart,
matched future forcing contracts carrier differences by the strict factor
`a_PC+(1-a_PC)L_Z<1`.

The theory status is deliberately bounded. Mature coherence-only RC does not
authorize an independent memory field. PC is a revision-specific constitutive
completion motivated by the historical slow-field form and by the core's open
Markov-sufficiency boundary. PC success neither promotes `Z_4` to a core
primitive nor proves coherence-only closure failure.

PC is not ontology-neutral relative to CI, OS, or RG. It adds the independent
D1 B-like nonresource structural authority `Z_4` to A's mobility semantics or
C's sector semantics. The scalar-ZOH writer is one preregistered PC
representative, not the universal persistent-carrier family law.

Candidate A has state `(C,W_A,Z_4,A)`; `W_A` remains the sole mobility authority
and its writer is unchanged. Candidate C has state `(C,Z_4,C)`; `T_C` remains a
derived, uncommitted coherence sector. In both rows, committed `Z_4,k` produces
same-beat geometry, the current and continuity execute once, and new
`Z_4,k+1` is read only on the next beat. All updates commit atomically.

The family contributes a real capability beyond RG. RG requires a locally
single-valued `h=Gamma_a(X_a)`. PC admits distinct complete states with the same
base `X_a` and different carrier histories. Along the accepted D8-A visibility
directions, that difference changes geometry entering a named current-equation
term. Moreover, `D_Z U_PC=a_PC I` at vanishing geometry sensitivity remains
nonsingular for sufficiently small coupling, so independent retained complete-
state capacity is established. PC therefore supports equation-level path
dependence without a base-map inverse, graph-transform contraction, or section
uniqueness. Base-state hysteresis and nonzero future `C/W` effects remain debt.

State lifecycle is explicit: snapshots and restoration identity include the
current and reset-baseline carrier; reset returns to the construction baseline;
`set_state` does not silently rebase; migration from non-PC initializes
canonical zero without inventing history; disabled PC keeps zero carrier and
reference geometry. None of these administrative operations counts as native
release.

D2 interventions remain distinct. Natural no-input and explicit `write_off`
both produce `Z_4+=a_PC Z_4` in the scalar profile but have separate receipts;
retained-state freeze gives `Z_4+=Z_4`; reset restores the baseline; full PC
disable enforces zero carrier and reference geometry. With PC enabled,
`chi=0` or `zeta=0` stops new inscription but does not erase existing state.

Profile semantics are lifecycle authority. Changing `H_profile`, `K_4,base`,
the representation, carrier norm/domain, or writer semantics requires explicit
migration and target re-admission even if array shapes match.

The positive result is fixed-topology and fixed `K_4` representation.
Representation-preserving context or boundary changes retain `Z_4` and refresh
all declared surfaces. Same-space nonsmooth changes require a deterministic
runtime map and block classical analysis. Without typed `L_event^K4`, carrier-
space-changing topology/reindex/split/merge/birth/death changes abort before
mutation. Ordinary context retention requires unchanged profile/carrier/writer
semantics. Event termination is not carrier transport.

GTRS-COMP must audit full `K_4` against the exact profile-kernel quotient before
assigning PC state cost. A zero profile kernel establishes irreducibility under
that equivalence, not absolute minimal reachable-state representation. COMP
must also avoid universalizing the scalar single-timescale writer; a
multi-timescale operator-semigroup profile remains a nonprimary later
alternative.

COMP must also separate history authority analytically from CI/OS/lagged timing
without assuming composability. No hybrid campaign is opened, but the first
hybrid that could materially change the population must be identified and
routed before lifecycle freeze.

```text
record = GRC9V4-GTRS-PC-v1
status = accepted_bounded
top_level_disposition = accepted_bounded_persistent_K4_carrier_family_complete_A_C
decision_record_digest = d1e38d6aa36b03154715c1e26c0b4a1b181dab19ed4bbfbd1575c94c9962e49a

A_PC = bounded_complete_realization
C_PC = bounded_complete_realization
capability_beyond_local_RG = supported_at_equation_level
complete_state_nonannihilation_witnesses = 0
topology_event_transport_instantiated = false
numeric_spectrum_or_stability = uninstantiated

predecessor_live_debts = 39
predecessor_debt_dispositions = 39
current_successor_debts = 5
live_debt_union = 43
controls = 82

GTRS_COMP_authorized_after_acceptance = true
GTRS_COMP_authorized = true
D9_authorized = false
runtime_or_src_changed = false
```

The five current debts preserve comparative synthesis including the quotient
audit, numerical carrier-domain/current-regularity/writer/parameter
instantiation, carrier-space
event interspace semantics, and A/C base-state complete-chain witnesses. No
candidate or realization is selected.

The authoritative records are
[`GeometryTemporalRealizationSuccessorPersistentCarrier.json`](./decisions/GeometryTemporalRealizationSuccessorPersistentCarrier.json)
and its
[`scientific interpretation`](./decisions/GeometryTemporalRealizationSuccessorPersistentCarrier.md).

## Comparative Realization Synthesis

Status: `accepted_bounded`.

GTRS-COMP enumerates eight positive primary A/C rows, preserves two RG-1
same-beat family obstructions, and keeps Candidate B visible as routed rather
than rejected. It does not rank a candidate or architecture.

The architecture population has three analytically separable dimensions:

```text
candidate ontology
geometry/current timing
history authority
```

CI and OS share committed candidate-state coordinates and are lawfully related
through derived `(J,h)` analysis lifts and the exact split residual. RG-2b is
comparable only through its invariant-section analysis lift. Neither lift adds
state authority. PC projects many-to-one onto the base candidate state and
loses `Z_4` history, so it supports capability/state-cost comparison but not
transition equivalence. A and C have no lawful common state isomorphism for
numeric ranking.

The PC quotient audit closes for the accepted enabled affine profile:

```text
D_K H_profile = kappa_H I
kappa_H != 0
kernel(D_K H_profile) = {0}
no nontrivial profile-kernel quotient = true
absolute minimal reachable-state representation = unproved
```

This result is profile-local. Future noninjective profiles must repeat the
quotient and writer well-definedness audit. The scalar-ZOH one-`tau_PC` writer
remains a representative, not the family law.

Timing and history authority are analytically separable, but their composition
is not automatic. The first materially missing pair is coupled-implicit plus
persistent `K_4` for A and C. No hybrid matrix is opened; that narrow pair must
be pressured before D9. OS+PC and RG+PC remain unpressured and not currently
required, with reactivation if selection later uses solver cost, failure
surface, latency, or state-conditioned lagged geometry.

Numerical stability is not activated as an unconditional pre-D10 gate. It
becomes mandatory with matched branches, D9 charge/projector semantics, and
lawful metrics if D10 attempts exclusive preference, numeric ranking, or a
stability claim.

```text
record = GRC9V4-GTRS-COMP-v1
status = accepted_bounded
decision_record_digest = 67a9c97a79525dc70c2233fb2b6706c47d2e31388c9160520f6842d7dc63a84b

positive_primary_rows = 8
family_level_obstruction_rows = 2
routed_not_rejected_candidates = 1

predecessor_live_debts = 43
predecessor_debt_dispositions = 43
current_successor_debts = 3
live_debt_union = 43
controls = 68

remaining_family_pressure_complete = true
GTRS_CI_PC_authorized = true
D9_ready_after_human_acceptance = false
D9_authorized = false
D10_authorized = false
runtime_or_src_changed = false
```

The authoritative records are
[`GeometryTemporalRealizationComparativeSynthesis.json`](./decisions/GeometryTemporalRealizationComparativeSynthesis.json)
and its
[`scientific interpretation`](./decisions/GeometryTemporalRealizationComparativeSynthesis.md).

## Narrow Coupled-Implicit Plus Persistent-Carrier Pressure

Status: accepted bounded.

GTRS-CI-PC is the only hybrid pressure currently routed. It must determine
whether retained `Z_4,k` and source-current `Delta_K_4(J,h)` can share one typed
same-beat profile without hidden gain duplication:

```text
(X_k, Z_4,k)
  -> joint root candidate using K_4,base + Z_4,k + Delta_K_4(J,h)
  -> atomic X_k+1 commit
  -> Z_4,k+1 = a_PC Z_4,k + (1-a_PC) Delta_K_4(J,h)
```

The displayed composition is a pressure target, not an accepted equation. The
gate owns composite-domain regularity, disabled/read-off behavior, failure
atomicity, no same-beat read of new carrier state, and full hybrid
serialization/restoration/reset/migration/event boundaries for both A and C.
OS+PC and RG+PC remain visible as unpressured, conditionally reactivatable
compositions.

The executed primary profile composes retained prior structure with a
source-current structural increment without assigning them duplicate same-beat
authority:

```text
h = H_profile(K_4,base + Z_4,k + rho_inst Delta_K_4(J,h))
F_J,a(J,h; X_a,k) = 0

after valid root and authoritative continuity:
  Z_4,k+1 = a_PC,a Z_4,k + (1-a_PC,a) Delta_K_4,a(J,h)
```

`rho_inst = 1` is fixed for the primary profile and `rho_inst = 0` is the exact
PC timing ablation. Both A and C admit bounded complete hybrid realizations on
the declared `B_2R` composite profile/current domain. Joint-root regularity is
local and parametric: at `kappa_H = 0` the derivative is block triangular with
the accepted candidate current block and identity geometry block. The result
does not claim a numerical envelope, global root, topology-event continuation,
stability, or universal timing-history composability.

Strict reference source slack plus uniform root/source continuity closes the
same-root source ball for a nonzero local coupling envelope; the convex writer
then preserves the carrier ball. Exact derivatives prove retained-path
nonannihilation for nonzero admissible `delta Z` and immediate-path
nonannihilation where the same-root source is nonzero. Committed endpoint
nonannihilation remains debt.

For constant source, the unit-plus-unit primary profile has `Z -> S` and hence
steady structural argument `K_4,base + 2S`. This is not amplitude-equivalent to
CI or PC. A normalized two-gain profile remains a possible D10 comparison and
does not replace the current pressure row.

```text
record = GRC9V4-GTRS-CI-PC-v1
status = accepted_bounded
decision_record_digest = 5f003ff5f4dbbb60788ac50827b5a3ccff7ff7e194173721f15503bc6024682a

A_CI_PC = bounded_complete_hybrid_realization
C_CI_PC = bounded_complete_hybrid_realization
predecessor_live_debts = 43
predecessor_debt_dispositions = 43
carried_predecessor_debts = 42
resolved_predecessor_debts = 1
current_successor_debts = 5
live_debt_union = 47
controls = 93

human_acceptance_recorded = true
D9_ready_after_human_acceptance = true
D9_authorized = true
D10_authorized = false
runtime_or_src_changed = false
```

The authoritative records are
[`GeometryTemporalRealizationHybridCoupledPersistentCarrier.json`](./decisions/GeometryTemporalRealizationHybridCoupledPersistentCarrier.json)
and its
[`scientific interpretation`](./decisions/GeometryTemporalRealizationHybridCoupledPersistentCarrier.md).

## D9. Complete Step And Lifecycle Contract

Status: `accepted_bounded`.

D9 freezes operational semantics for ten independent positive profiles:

```text
A/C x CI, OS, RG2b, PC
A/C x CI+PC
```

Candidate B remains `routed_not_rejected_no_lifecycle_profile`. D9 does not
rank candidates or realizations and does not infer B failure from the absence
of an admitted `U_B` transition. PC establishes viable independent structural
state but does not derive B's signed symmetric formation source, so B remains
underdetermined rather than rejected or solved by relabel.

The complete-step charge is derived from the current closed-internal,
unit-measure write path:

```text
Q(X) = sum_i C_i
Q(X_k+1) - Q(X_k) = B_ext + S_ext
current admitted profile: B_ext = S_ext = 0
V_Q = kernel(DQ)
Pi_Q_C_H0 = H0-weighted zero-sum projector on C
full tangent retraction = identity extension on nonresource coordinates

general event profile:
  Q_varpi(C) = varpi^T C
  T_C_evt = event resource transport, not Candidate C derived T_C
  C+ = T_C_evt C- + Delta_C_event
  varpi+^T T_C_evt = varpi-^T
  receipt = varpi+^T C+ - varpi-^T C-
  Q_target+ = Q_target- + receipt = varpi+^T C+
```

The only authoritative nonresource state is `W_A` where present and `Z_4`
where present. Candidate C's `T_C`, geometry, current, substages, RG section,
solver work, and analysis projectors remain derived or transient. The structural projector and its
canonical full-tangent retraction do not claim a full-state orthogonal
projector before the product metric is frozen. Post-continuity `C` must already
be finite, nonnegative, and on serialized `Q_target`; the current budget stage
is an identity/no-op, and a nontrivial correction fails before any final-`C`
writer.

The complete-step transaction validates profile and state, derives or solves
all uncommitted geometry/current stages, validates the authoritative solver
disposition, applies antisymmetric continuity once, validates the simplex and
budget no-op, refreshes final-`C` surfaces, runs the A/C poststate writer,
writes persistent carriers once without same-beat readback, refreshes derived
surfaces, and commits atomically. Failure at any solver or writer stage changes
nothing authoritative.

Disablement, migration/drop, causal switch-off, and native release remain
distinct. All ten disabled profiles have separately scoped GRC9V3 transition,
state-projection, observable, and lifecycle/event reduction surfaces.
Migration maps are direction-specific: A-to-C is admitted as lossy, while
C-to-A uses exact V3 base-conductance reconstruction as its history-free A
initializer. Context-contract identity is separate from mutable current
context input.

The ten-profile by 26-operation matrix contains all 260 cells, with 16
additional independent intervention subcases in three multi-authority rows. A
floor activation is runtime-valid but nonsmooth under the frozen total policy.
All C selector-rank changes use basis-independent strata. Each regular stratum
has its own self-map and contraction domain; coupled profiles accept exactly
one regular self-consistent root across the stratum union and otherwise return
no or multiple admitted roots. Threshold-boundary roots fail closed. All ten
rows admit typed topology continuation through `T_C_evt` resource accounting,
whole-lifecycle migration of current state, reset baseline, and `Q_target`,
typed `L_K4_evt` history transport or explicit reset, target reconstruction,
readmission, and atomic commit. Generic lossless history preservation without
sufficient lineage is resolved negative, not an optional open debt, and typed
lifecycle continuation does not establish continuation-spectrum identity.

```text
record = GRC9V4-CD-D9-v1
decision_record_digest = 33c8fe75ae7fda716e97bb9714d5f297911bc4d606f5d382d77f9c3092aa4586

positive_profile_rows = 10
coverage_cells = 260
blank_cells = 0
exact_V3_reduction_witnesses = 10
controls = 130

predecessor_live_debts = 47
carried = 29
resolved = 18
superseded = 0
current_D9_debts = 0
D9_resolved_negative_results = 1
live_debt_union = 29
post_spec_verification_obligations = 4
silent_drop_count = 0

human_acceptance_recorded = true
D10_ready_after_human_acceptance = true
human_acceptance = accepted_bounded_2026-08-25
D10_authorized = true
specification_authorized = false
implementation_authorized = false
runtime_or_src_changed = false
```

The authoritative records are
[`D9CompleteStepAndLifecycleContract.json`](./decisions/D9CompleteStepAndLifecycleContract.json),
its [scientific interpretation](./decisions/D9CompleteStepAndLifecycleContract.md),
the [profile registry](./decisions/D9ProfileStateLifecycleRegistry.json),
the [coverage matrix](./decisions/D9LifecycleCoverageMatrix.json), and the
[residual debt ledger](./decisions/D9ResidualDebtLedger.json).

## D10. Design Synthesis And Spec-Writing Decision

Status: `accepted_bounded`.

D10 selects a lineage-local, profile-explicit GRC9V4 architecture without
ranking candidate or realization profiles. The decision is claim-ledger first:

```text
claim -> debt -> pressure/evidence -> claim transformation
```

All 29 debts carried by D9 have explicit historical predecessor nodes, typed
supported/blocked/conditioned/routed/negative/successor relations, and full
accepted-record lineage. Their transformations are 1 confirmed, 7 narrowed, 2
split, 1 resolved negative, and 18 routed. The 129 claim/debt edges are
reciprocal. No debt is closed by scope exclusion, and no normative claim is
admitted without its bearing-debt set. A `blocked_by` edge may target only a
historical predecessor claim or a still-unearned current conditional/open
claim; supported and negative successor claims remain successors rather than
being represented as temporally blocked.

The common normative layer is a resource/state-authority/current/geometry/
lifecycle interface and invariant contract. Constitutive laws remain
profile-owned. A and C remain optional revision-specific families, with the
present A law admitted only as normalized and nondimensional. CI, OS, RG2b, the
current scalar-ZOH one-`tau_PC` PC profile, and the exact CI+PC gain-two profile
remain optional realizations. An executable state binds exactly one candidate
and one realization from the ten currently admitted complete profiles. This is
the complete initial specification population, not a completeness theorem over
future lawful V4 profiles. B remains routed, unrejected, and nonexecutable
pending a source-backed writer. D9's stronger bounded-domain A and stratum-local,
uniquely self-consistent C root results remain part of CI and CI+PC.
Current/reset states and snapshots each bind one complete-profile identity.
Migration and topology-event receipts instead bind the ordered pair
`(p_source, p_target)`, with equality allowed when the profile is unchanged.

The unfolding trajectory is claim-activated rather than scheduled. Normative
claims may proceed into specification after acceptance; conditional/open claims
and verification obligations activate only for the stronger claims they name.
New candidate, realization, hybrid, or geometry profiles require explicit
successor admission, a new complete identity, and reopening of the earliest
affected authority/staging/state/geometry/accounting/lifecycle contract.
Negative claims remain boundaries until new evidence transforms them.

The authorization is lineage-local. A pre-closure substrate-provenance audit
must classify every selected equation and contract before final substrate
identity is closed or any promotion from the GRC9 lineage to GRCv4 is attempted.

```text
record = GRC9V4-CD-D10-v1
decision_record_digest = 3e673b335ad428d01006f231765d060a9bdd5f134332b143048f774de94bad00
human_acceptance = accepted_bounded_2026-08-26

claim_topology = {normative: 9, optional: 7, conditional: 12, open: 5, negative: 6}
historical_predecessor_claim_nodes = 29
reciprocal_typed_claim_debt_edges = 129
D9_carried_debts = 29
D10_transformed_debts = 29
claimless_debt_dispositions = 0
verification_obligations = 11
controls = 73
executable_complete_profiles = 10
runtime_complete_profile_binding = exactly_one_candidate_plus_exactly_one_realization
migration_receipt_profile_binding = ordered_source_target_complete_profile_pair
topology_event_receipt_profile_binding = ordered_source_target_complete_profile_pair_equal_when_unchanged
current_profile_population_future_exhaustive = false
current_PC_profile = scalar_ZOH_one_tau_PC_persistent_K4_history
unfolding_trajectory = claim_activated_not_fixed_successor_schedule

scientific_disposition = accepted_bounded_lineage_local_profile_explicit_spec_authorization
final_substrate_identity_closed = false
preclosure_substrate_provenance_audit_required = true
specification_authorized_after_human_acceptance = true
specification_authorized = true
implementation_plan_authorized = false
implementation_authorized = false
runtime_or_src_changed = false
```

The authoritative records are
[`D10DesignSynthesisAndSpecWritingDecision.json`](./decisions/D10DesignSynthesisAndSpecWritingDecision.json),
its [scientific interpretation](./decisions/D10DesignSynthesisAndSpecWritingDecision.md),
the [claim topology](./decisions/D10NormativeClaimTopology.json), the
[debt/claim transformation ledger](./decisions/D10DebtClaimTransformationLedger.json),
and the [specification authorization profile](./decisions/D10SpecificationAuthorizationProfile.json).

## D10.1. Preliminary Substrate Provenance And Nine-Port Necessity

Status: `accepted_preliminary_bounded_substrate_provenance_separation`.

D10.1 preserves accepted D10 and records the first bounded result on its open
substrate-identity question. GRC9V3 provenance is load-bearing through exact
formula reuse, disabled reduction, and lifecycle compatibility, but current
evidence does not establish that the new Read-Back, retained-state,
`K_4`/Hodge, or realization machinery intrinsically requires nine ports.

Candidate A is provisionally classified as GRC9V3-derived with independent
derivation over GRCv3 contracts required before promotion. Candidate C and the
common structural/realization surfaces are stronger GRC-level candidates,
still without promotion to GRCv4. Ordered port mechanics, mechanical expansion,
hybrid spark/stabilization, and column coarse-graining are GRC9-intrinsic.
Exact GRC9V3 disabled reduction and lifecycle targeting are instead
GRC9-specialization-specific compatibility content.

The naming taxonomy is `GRCv3` for general graph GRC and `GRC9v3` for its
nine-port specialization/profile. The prospective general successor is
therefore `GRCv4`, with `GRC9v4` as its nine-port specialization. The older D10
phrase `generic Graph GRC V4` refers to `GRCv4`, not a separate naming family.

```text
record_id = GRC9V4-CD-D10.1-v1
status = accepted_preliminary_bounded_substrate_provenance_separation
human_acceptance = accepted_preliminary_bounded_substrate_provenance_separation_2026-08-26
predecessor_decision_digest = 3e673b335ad428d01006f231765d060a9bdd5f134332b143048f774de94bad00
decision_record_digest = 51572056af21abd3c4c623e72bf7a20ba34c54dafae8b23086979d2c761c939f

findings = [D10.1-P1, D10.1-P2, D10.1-P3, D10.1-P4, D10.1-P5]
representative_provenance_rows = 12
working_factorization = GRCV4 ->[nine-port specialization] GRC9V4 ->[disabled V4 profile] GRC9V3
working_factorization_status = hypothesis_supported_by_preliminary_provenance_separation
promotion_proved = false
final_substrate_identity_closed = false
D10_claim_topology_unchanged = true
preclosure_substrate_provenance_audit_still_required = true
GRCV4_specification_authorized = false
implementation_authorized = false
runtime_or_src_changed = false
```

Authoritative records:

- [`D10_1PreliminarySubstrateProvenance.json`](./decisions/D10_1PreliminarySubstrateProvenance.json)
- [`D10_1PreliminarySubstrateProvenance.md`](./decisions/D10_1PreliminarySubstrateProvenance.md)

## D10.2. Full Substrate Provenance And GRCV4 Promotion Audit

Status: `accepted_bounded`.

D10.2 consumes accepted D10.1 and performs the complete pre-closure audit for
the current D10 initial specification population. It binds all 39 accepted D10
claim nodes to 67 normatively load-bearing parent objects and 152 subordinate
normative equation/contract rows. Every row records premises, lineage,
substrate disposition, promotion status, independent derivation,
specification destination, and blocked overread.

The accepted D10 decision, normative claim topology, and specification
authorization surfaces contain exactly the same 39 claim IDs. This includes
`D10-CL-C-012`; the 38-claim count in the external pressure review was stale.
The subordinate registry distinguishes family-level provenance from the
candidate-specific equations and contracts that instantiate it.

Twelve source-bound derivations show that the general resource, scalar
transport, GRCv3 differential, Candidate A, Candidate C, graph-Hodge geometry,
candidate-specific transport mobility, Candidate-A initialization,
realization, complete-step/lifecycle, and specification-grammar contracts do
not require the nine-port substrate. Candidate A promotion is restricted to
the accepted curvature-disabled D7 `G_W`; a curvature-conditioned successor
must reopen profile identity and provenance.

The hardening separates core `K -> g[K]` from graph `K_4`, restores `M_4` as
transport mobility rather than overlap assembly, derives the reference Hodge
embedding from GRCv3 measure/base-conductance surfaces, and splits generic
migration plus the GRCv4 Candidate-A initializer from the exact GRC9v3
initializer binding. It also distinguishes core-theory physics from
substrate-independent specification metadata.

The final classification is:

```text
GRC_derived = 45
core_theory_substrate_independent = 1
substrate_independent_specification_meta = 8
GRC9_intrinsic = 8
GRC9_specialization_specific = 5
GRC9V3_derived_GRC_rederivation_required = 0
```

This earns the bounded current-population factorization:

```text
GRCV4 ->[nine-port specialization] GRC9V4 ->[disabled V4 profile] GRC9V3
```

The GRC9 specialization remains substantive: it owns the fixed row-basis
backend, ordered ports, 3x3 chart, saturation, mechanical expansion, hybrid
spark/child-basin stabilization, and column coarse-graining. Exact disabled
transition, state, observable, and lifecycle reductions are separately
specialization-specific because they deliberately target GRC9v3. The ten
current profiles expose all four as independent contracts, producing an exact
40-row compatibility matrix.

The 85 expanded subordinate rows also make the charge tangent/projector,
candidate-specific CI and CI+PC roots, PC retention/release, OS staging and
split residual, RG invariant section, Candidate C chain, structural crossing,
and typed topology-event maps individually provenance-auditable.

The event resource row preserves the full accepted D9 map
`C_plus = T_C_evt C_minus + Delta_C_event`. The conservative transport map,
resource-coordinate increment, resulting `Delta_Q_event` receipt, and
`Q_target_plus` update remain distinct. Ordinary complete-step validation uses
`Q_target_next`; it cannot double-count an event delta against a target that
has already been updated.

D10.2 accepts the named successor `D10.2-CL-N-001` to accepted claim
`D10-CL-C-011` without mutating accepted D10 bytes. The pre-closure provenance
obligation is closed for the current population, and specification ownership
is now GRCv4 first plus GRC9v4 specialization. Future profiles must reopen
provenance and the earliest affected design contract.

```text
record_id = GRC9V4-CD-D10.2-v1
status = accepted_bounded
predecessor_decision_digest = 51572056af21abd3c4c623e72bf7a20ba34c54dafae8b23086979d2c761c939f
decision_record_digest = 28343064e85065b7f18227cf429e8cd8f33b414d7a19d5f3e9090a318adcb32c
human_acceptance = accepted_bounded_2026-08-26

accepted_D10_claims_covered = 39
normatively_load_bearing_objects = 67
normative_equation_contracts = 152
explicit_equation_contracts = 85
disabled_reduction_matrix_rows = 40
independent_GRC_derivations = 12
controls = 48
audit_checks = 289/289
promotion_pending_rows = 0
factorization_earned = true
factorization_scope = current_D10_initial_specification_population_only
final_substrate_identity_closed_for_current_population = true
final_substrate_identity_globally_closed_for_all_future_profiles = false
GRCV4_specification_authorized_now = true
GRC9V4_specialization_specification_authorized_now = true
normative_spec_files_written_by_D10_2 = false
implementation_authorized = false
runtime_or_src_changed = false
```

Authoritative records:

- [`D10_2FullSubstrateProvenanceAndPromotionAudit.json`](./decisions/D10_2FullSubstrateProvenanceAndPromotionAudit.json)
- [`D10_2FullSubstrateProvenanceAndPromotionAudit.md`](./decisions/D10_2FullSubstrateProvenanceAndPromotionAudit.md)

Permitted final dispositions:

```text
authorize_GRC9V4_specification
reopen_named_design_gate
route_to_named_theory_or_constitutive_derivation
close_current_design_tranche_unresolved
```

## D11. Specification-Audit Successor Opening and Preregistration

The accepted D10.2 record remains immutable. The bounded procedural opening
created two exact successor investigations after the specification audit found
missing accepted authority. The opening itself accepted no proposed solution;
the later D11-C resolution below is an append-only scientific successor.

The companion routing record carries all accumulated authority rather than
only the terminal D10.2 digest:

```text
routing_record_id = GRC9V4-CD-D11-CLAIM-DEBT-ROUTING-v1
routing_record_digest = 63cc407bffefef85602c28ead6c3da6b846778d3be9f78952db11cb10275c78d
current_D10_claims_carried = 39
historical_D10_claim_nodes_carried = 29
D10_debt_transformations_carried = 29
D10_verification_obligations_carried = 11
pending_forward_verification_obligations = 10
D10_preclose_provenance_disposition = satisfied_for_current_population_only
D10.2_objects_carried = 67
D10.2_equation_contracts_carried = 152
new_D11_successor_debts = 2
claim_reclassifications_at_opening = 0
prior_debt_disposition_changes_at_opening = 0
```

```text
record_id = GRC9V4-CD-D11-OPEN-v1
status = accepted_bounded_successor_opening
predecessor_decision_digest = 28343064e85065b7f18227cf429e8cd8f33b414d7a19d5f3e9090a318adcb32c
decision_record_digest = 51ba66d5404dee29f7b2a7dcd9501b43711fce0d47d466118945b5a0f71ac23a
scientific_result_accepted = false

D11-C_opening_state = open_preregistered
D11-C_preregistration_digest = c1c22c88fa676705370d01256a34801a364e310c93e4ef85cc5a3208e6e06a78
D11-G9_opening_state = queued_preregistered_requires_accepted_D11-C
D11-G9_preregistration_digest = 856e3db9ffa6a09080f7af0b9753be222ab986599855168a4fe9d218490c1635

paper_correction_authorized = false
D11_dependent_specification_authority = false
implementation_authorized = false
runtime_or_src_tests_change_authorized = false
GRC9_or_GRC9V3_change_authorized = false
```

D11-C reopened Candidate C direct transport at the D4/D4-v2 boundary and its
bounded D6-v2/D7-v2 consumers. Its resolution is recorded below. The current
spec law remains the unselected D11-C-T1 candidate until ordered propagation.

D11-G9 was queued at opening. After D11-C acceptance it may reopen only
`D10.2-EC-PARENT-GRC9-MECHANICAL-EXPANSION` and bounded GRC9V4 consequences.
The current collision-free mapping is the unselected D11-G9-P1 candidate. No
older GRC9 or GRC9V3 artifact is changed.

### D11-C Accepted-Bounded Successor

```text
record_id = GRC9V4-CD-D11-C-RESOLUTION-v1
status = accepted_bounded
decision_record_digest = 82e8008e8edade39db7b5327a31a807031b712dcc86b3fe3e8c0977bda51e797
selected_candidate = D11-C-T3a
selected_profile = C-HM-STIFFNESS-BASELINE-v1
D11-C = closed_accepted_bounded
D11-G9 = active_preregistered_after_accepted_D11-C
```

The accepted law gives mobility and retained Hodge geometry separate typed
authority:

$$
M_{4,C}=\eta_C\operatorname{Diag}(W_{C,\mathrm{tr}}),
\qquad
H_{1,\mathrm{form},M}=\mathsf D_C H_{1,\mathrm{form}}\mathsf D_C,
$$

$$
\Phi_{0,C}=\kappa_{\Phi,C}BH_{1,\mathrm{form},M}d_0C-V'_{C,U}(C),
\qquad
J_{0,C}=-M_{4,C}d_0\Phi_{0,C}.
$$

`W_C,tr` is an exact positive stable-edge reference map in the complete
profile, has no ordinary-beat writer, and must be supplied in full by the
target profile before topology-event readmission. D11-C-T1 is not selected;
D11-C-T2 remains an admissible successor family; D11-C-T3 is refined into the
selected T3a; and D11-C-T0 remains a future bounded fallback.

The append-only provenance supplement adds `D11-C-CL-O-001`, three objects,
and eleven equation contracts. No D10 claim, historical node, debt
transformation, object, contract, or digest changes. The local D11-C debt is
resolved boundedly; all ten inherited forward verification obligations remain
pending. GRC9V4 must delegate the disabled branch exactly to unchanged GRC9V3
rather than substitute T3a.

### D11-G9 Accepted-Bounded Axis-Preserving Expansion

```text
record_id = GRC9V4-CD-D11-G9-RESOLUTION-v1
status = accepted_bounded
decision_record_digest = a0813ceead2c992ec197790abd8a0ceea167ae2d952f853cf48f1db4d8001615
selected_candidate = D11-G9-P4a
selected_policy = grc9v4_axis_preserving_chiral_same_port_expansion_v1
scientific_result_accepted = true
```

The accepted primary law is

$$
\beta_\epsilon(b)=b\oplus_3\epsilon,
\qquad
r_b^\epsilon=\beta_\epsilon(b)+3(b-1),
$$

$$
(c,r_b^\epsilon)\leftrightarrow(s_b,r_b^\epsilon),
\qquad
\epsilon\in\{-1,+1\}.
$$

The two mirror spines are $(2,6,7)$ and $(3,4,8)$. Every internal edge uses the
same port type at both endpoints, all old boundaries retain their exact ports,
and creation-order branch-row BFS trees extend the construction to arbitrary
capacity-selected size. Chirality is always explicit; growth phase is `none`
exactly when the extra-node remainder is zero and otherwise is an explicit
member of $\{1,2,3\}$. The witness passes 23,256 admitted plans over
$D_{\mathrm{eff}}=9,\ldots,5000$, 1,000 input shuffles, unique local endpoint
occupancy, nonstalling, $7n+2$ capacity, row/column imbalance at most one, and
dihedral covariance.

D11-G9-P4a supersedes the provisional P1/P1a center-row repair while retaining
P1a's exact stable-ID grammar and its corrected Candidate C and whole-carrier
$K_4$ lifecycle boundaries. GRC9 and GRC9V3 remain unchanged. Exact disabled
compatibility is limited to the legacy target-defined domain; the saturated
port-5 conflict fails closed as `legacy_expansion_target_undefined`.

The append-only supplement adds `D11-G9-CL-N-001`, nine reciprocal claim
edges, ten specialization objects, and twenty contracts. The accumulated
population is 80 objects and 183 contracts, with 39 D10 current claims, 29
historical nodes, two D11 successor claims, and all 29 D10 debt transformations
preserved. Seventeen forward verification obligations remain pending. Paper
propagation is now the next gate; specification and implementation authority
remain closed until their ordered gates.

Authoritative opening and preregistration records:

- [`D11SuccessorInvestigationOpening.json`](./decisions/D11SuccessorInvestigationOpening.json)
- [`D11SuccessorInvestigationOpening.md`](./decisions/D11SuccessorInvestigationOpening.md)
- [`D11ClaimDebtAndAuthorityRouting.json`](./decisions/D11ClaimDebtAndAuthorityRouting.json)
- [`D11ClaimDebtAndAuthorityRouting.md`](./decisions/D11ClaimDebtAndAuthorityRouting.md)
- [`D11CCandidateCBaselineTransportAndMobilityClosure.json`](./decisions/D11CCandidateCBaselineTransportAndMobilityClosure.json)
- [`D11CCandidateCBaselineTransportAndMobilityClosure.md`](./decisions/D11CCandidateCBaselineTransportAndMobilityClosure.md)
- [`D11CCandidateBaselineTransportAndMobilityResolution.json`](./decisions/D11CCandidateBaselineTransportAndMobilityResolution.json)
- [`D11CCandidateBaselineTransportAndMobilityResolution.md`](./decisions/D11CCandidateBaselineTransportAndMobilityResolution.md)
- [`D11CCandidateBaselineTransportProvenanceSupplement.json`](./decisions/D11CCandidateBaselineTransportProvenanceSupplement.json)
- [`D11G9CanonicalExpansionPortAllocationClosure.json`](./decisions/D11G9CanonicalExpansionPortAllocationClosure.json)
- [`D11G9CanonicalExpansionPortAllocationClosure.md`](./decisions/D11G9CanonicalExpansionPortAllocationClosure.md)
- [`D11G9CanonicalExpansionPortAllocationResolution.json`](./decisions/D11G9CanonicalExpansionPortAllocationResolution.json)
- [`D11G9CanonicalExpansionPortAllocationResolution.md`](./decisions/D11G9CanonicalExpansionPortAllocationResolution.md)
- [`D11G9AxisPreservingExpansionProvenanceSupplement.json`](./decisions/D11G9AxisPreservingExpansionProvenanceSupplement.json)

## GRCV4 Specification Release Acceptance and Freeze

The final narrow audit accepts the exact release below as the normative
preimplementation GRCV4/GRC9V4 specification contract:

```text
record_id = GRCV4-SPECIFICATION-RELEASE-ACCEPTANCE-v1
status = accepted_frozen
predecessor_decision_digest = 57f2e8e634ae362933e94e72f634141e989dc357858940a4e5a4342dfc530f73
decision_record_digest = 914761881649b34bd7d0e80ef006551696c30190308544587d267800634faa11
accepted_release_id = grcv4-spec-release-sha256:9f4c8fe5b57b1c477d834a3e4dae3f98a2b18c70e6e7f598e3c9652170c8645f
accepted_release_sha256 = bba0bb649bc2e80c5bfa99f96bd5824bbdda3b3fbc87fb68c3e3a59da1cee46b
final_narrow_acceptance_audit_sha256 = f136c8552e1c7ef59570c11b26d592430e42058a9d9994e75a09560fda84242e
specification_release_state = frozen_normative_preimplementation_contract
specification_correction_gate_closed = true
specification_branch_ready_for_closure = true
specification_branch_closed = false
implementation_review_ready = true
implementation_review_activated = false
implementation_authorized = false
runtime_conformance_established = false
```

This acceptance changes governance state, not scientific or specification
content. The accepted release is not regenerated to contain its own downstream
acceptance record. The release-bound `PostD10SpecificationBoundary.json`
therefore remains unchanged, while
`PostGRCV4SpecificationAcceptanceBoundary.json` records the live successor
state and freezes every accepted release byte. The next eligible gate is
`GRCV4_GRC9V4_implementation_review`; opening it requires separate explicit
authorization.

Authoritative acceptance records:

- [`GRCV4SpecificationReleaseAcceptanceGate.json`](./specification/GRCV4SpecificationReleaseAcceptanceGate.json)
- [`PostGRCV4SpecificationAcceptanceBoundary.json`](./specification/PostGRCV4SpecificationAcceptanceBoundary.json)

## ATC-OPEN — autonomous-topology successor research

On 2026-09-20 the user instructed committing the retained proposal inputs and
continuing with the first bounded research step. Reference-intake commit
`0386568` retains Draft 8, Draft 7 and the stable local claim/debt index.
The [opening](./decisions/ATCSuccessorInvestigationOpening.md) and
[source intake](./evidence/autonomous-topology-change/ATCSourceIntake.json)
pin the accepted Tranche 7 baseline, current primary-source subjects, full
inherited forensic node/edge identities and eight typed boundary queries.

Status: research authorized; opening artifacts prepared for review. Scientific
results accepted: none. The 35 proposed claims and 28 debts remain unadmitted
and unresolved; all accumulated accepted history and runtime support remain.
Primary-source clause reconciliation and explicit proposed-source
adapter/readmission are pending, not inferred from source hashes.

ATC-1 is next: source/contract reconciliation and causal-input, stage, identity,
memory and transaction-composition proposal. Reserve Phase 9 7T after the
reviewed proposal/paper/specification route and before dependent specialization.
No production implementation, paper/spec correction, new G2/G3, legacy change
or scientific candidate selection is authorized by this opening.

## ATC-1 — causal-boundary proposal prepared

On 2026-09-20 the user authorized ATC-1. The
[proposal](./decisions/ATC1CausalBoundaryProposal.md) and
[machine companion](./evidence/autonomous-topology-change/ATC1CausalBoundaryProposal.json)
reconcile the relevant source clauses and propose `ATC-K0`: present-state,
time-homogeneous, no-new-memory reads with one autonomous attempt after each
successful positive ordinary beat. Physical selection excludes reset and
administration; binding and target admission still consume the full publication.

After-commit composition is explicitly distinct from joint rollback: event
failure preserves s1, including the ordinary receipt. Positive duration need
not advance the rounded clock. The same lifecycle owner must eventually
serialize both transactions without recursively acquiring its existing lock.
Crash-durable completion, implicit retries and non-Zeno behavior are not claimed.

Status: proposed, not admitted; review pending. The
[pressure result](./evidence/autonomous-topology-change/ATC1PressureResults.json)
separates protocol countermodels, exact arithmetic and bounded existing A_OS
and reference-geometry calculations. It is not native ATC conformance or an
all-product result. The receiving claim/debt mapping is specified, not installed;
no proposed or inherited debt is closed, and no accepted node/edge changes.
After review, continue to ATC-2's concrete law/construction pressure. Existing
paper/specifications, runtime, releases and G2/G3 acceptance remain unchanged.

Validation: ten focused checks passed, including ten reproduced typed queries
and exact inherited node/edge identities. A development-only substring check
initially confused `MATCHED` in inherited IDs with the ATC namespace; it was
corrected to test the identifier prefix. No authority or numerical assertion
was relaxed, and no production source was changed.

## ATC-1 — user acceptance of the bounded research envelope

On 2026-09-20 the user confirmed having checked the full opening and
reconstruction and instructed a new branch, acceptance and commit. The
[acceptance addendum](./decisions/ATC1Acceptance.md) and
[record](./evidence/autonomous-topology-change/ATC1Acceptance.json) close ATC-1
in its research-design scope on `investigation/grcv4-atc`.

The independent review's scoped PASS and eleven reproduced groups are retained
as readable files with their exact inputs. The addendum records the explicit
diagonal-reference CAN-R+ limitation, unrecorded-history and beat-sampling
limits, and s2 retention after an event has committed. The user's separate
opening/reconstruction review is not represented as independent native evidence.

The preceding preparation entries and all reviewed source/evidence bytes remain
historical snapshots. No accepted graph node/edge, proposal-debt status,
Tranche 7/G2/G3 support, paper/specification or runtime changes. The receiving
mapping is accepted as design only; adapter/readmission remains pending.
ATC-2 is next eligible, not started by this acceptance/commit request.

## ATC-2 — concrete candidate proposal and bounded native pressure

On 2026-09-20 the user authorized ATC-2. The
[candidate proposal](./decisions/ATC2CandidateClosureProposal.md) and
[machine companion](./evidence/autonomous-topology-change/ATC2CandidateClosureProposal.json)
specify separate represented-value CAN-A birth and CAN-C coarsening policies,
complete target references/resources/history recipes, and a CAN-B builder
conditional on a supplied half-edge partition. CAN-B's qualified structural
functional/branch/mode-to-partition law is held, not fabricated from K4.

The [retained pressure](./evidence/autonomous-topology-change/ATC2PressureResults.json)
covers ten native current reads, exact arithmetic/symmetry controls, three
generated requests executed by the supplied-event owner, independent role
transport/initialization, matched identity-topology history controls, replay,
continuation and postordinary rollback. The fixed A_PC source-envelope
rejection is retained. Read applicability, constructed targets and executed
events remain distinct. No chart enlargement or production change was made.

This is prepared research, pending independent review and user acceptance.
All 35 origin claims, 28 open debts and 165 reciprocal links remain unchanged;
there is no accepted descendant, graph/source-adapter admission, G2/G3 change
or native autonomous dispatcher. ATC-3 adjudication and the topology-only
proposal/paper/spec sequence still precede 7T implementation. The accepted
ATC-1 subjects and historical records remain byte-identical.

## ATC — corrected capability objective and first V4-native information probe

On 2026-09-20 the independent ATC-2 review supported its bounded research
results. Its subsequent correction kept generic capability closure open;
the user endorsed capability-gap-driven V4-native scientific design, using
V2/V3 as hints about functional needs rather than mechanisms to transplant.

The [continuation](./decisions/ATCCapabilityClosureContinuation.md) introduces
open program requirement ATC-CAP-REQ-01: relation growth, endogenous vertex
refinement and simplification in each of ten families, constitutive composition,
and continuing native autonomy. It does not add an accepted graph claim or
rewrite the 35 origin claims, 28 debts or 165 associations. Bounded ATC-3
adjudication remains possible; final scientific synthesis cannot silently
adopt the currently passing subset as the complete extension. Runtime closure
belongs to 7T before topology-dependent Tranche 8, with independent preparation
and all accepted historical gates preserved.

The [first probe](./evidence/autonomous-topology-change/ATCCapabilityInformationProbe.json)
performs fifteen native reads/admissions at two retained sources and a separate
homogeneous A_OS zero-current control, including twelve exact-charge finite
resource redistributions. Current responses are nonzero while the Hodge-only
birth decision stays unchanged. The homogeneous control also responds, so
finite response alone is not a refinement-necessity certificate. No derivative,
partition, law, onset or all-product result is inferred. Zero ordinary steps or
events occur, and original publications are unchanged.

The [review retention](./evidence/autonomous-topology-change/review/ATC2-IndependentReview/README.md)
reproduces thirteen non-native groups; unused production-file copies are omitted
and the fresh source-availability count is explicitly one rather than eight.
The checker uses portable explicit paths and cannot overwrite an output
directory. Reviewed scientific inputs and original results are unchanged.
All 169 original execution bindings and three current typed provenance queries
were checked without rerunning the ATC-2 native campaign or broader tooling.

Status: research continuation in progress, no scientific acceptance or commit.
Next: justify and discriminate the response/representation distinction alongside
the structural-functional route; derive refinement/OS-growth mechanisms and
their composition. No existing paper, specification or production source changed.

## ATC — core-informed refinement discrimination

The user asked to revisit the original *Identity, Choice, and Abundance* paper,
then authorized continuation. Its already pinned S02 subject supplies direction
about sustained organization, not a graph-edit law or imported V4 proof.

The [discrimination study](./decisions/ATCRefinementDiscrimination.md) and
[focused result](./evidence/autonomous-topology-change/ATCRefinementDiscriminationProbe.json)
separate sensitivity, finite amplification, partition selection, graph growth
and stronger spark claims. Exact secants on the earlier samples are positive
even at the uniform source. Five explicitly declared A_OS trajectories each
execute two ordinary steps with literal independent current/resource oracles.
Temporal amplification alone does not supply a half-edge partition. Exact
abstract symmetry checks retain the unresolved three-/four-arm boundary.

The matched identity/history-reset event stays at zero current; the supplied
equal split creates contrast and nonzero current from the same uniform source,
but no relative child tendency. Both events and subsequent ordinary steps pass.
A separately admitted uniform target has zero current. This distinguishes
fixed-unit-measure constitutive growth from neutral field subdivision without
silently adding nonunit measures or global resource redistribution.

Focused run: eight fresh source admissions, twenty-two explicit reads, twelve
ordinary commits, two supplied-event commits, all assertions passing. Two
harness construction errors and their corrections are described in the note;
no runtime/admission criteria changed. No broad campaign was rerun.

Next investigate a source-side fission criterion and covariant partition under
the existing unit-measure contract, with constructor/history discrimination.
Keep the structural-functional alternative open. This is a working research
direction, not selection or acceptance of a law. All origin claims/debts,
capability cells, accepted history, papers/specifications and production sources
retain their previous status. No commit or scientific acceptance is recorded.

## ATC — independent-review correction and fixed modal split follow-up

The supplied independent review identified a prose error: the zero-exponent
modal control's current W remains all-one; its ordinary writer does not change
it. The note is corrected, with original script/result bytes preserved. The
degree-two unique unordered partition, unit-measure dimension argument and
restricted fixed-W amplification identity are now explicit as well.

The [follow-up](./decisions/ATCModalSplitDiscrimination.md) independently checks
the review's child-fiber coefficient matrix and executes only three new native
supplied splits, reusing the old uniform control. The higher-growth source mode
gives zero child difference; the lower-growth mode and its reversal produce
-1/4096 and +1/4096 after one step. Actual activity allocation yields the same
equal shares, so the construction is unchanged across the comparison. Both
roles map/readmit, current W remains one, and actual reset persists through
ordinary continuation. All assertions pass: three fresh source admissions,
nine explicit reads, three event commits and three ordinary commits.

The [new record](./evidence/autonomous-topology-change/ATCModalSplitProbe.json)
binds its sources and the unchanged predecessor. Review-reported arithmetic
checks remain distinct from this native run; the linked external check archive
was not attached and is not claimed reproduced. No broader campaign was run.

The result distinguishes source modal growth from child-resource response under
a fixed event. It does not justify a source guard, stable child organization,
all-product fission, the structural-functional route or a native dispatcher.
Those obligations, origin claims/debts and all accepted gates remain unchanged.
No user acceptance, paper/spec propagation or commit is inferred from the review.

## ATC — source-only accumulation/funding hypothesis CAN-F2

The next independent review found no inconsistency in the modal split result
and called for an explicit source-only fission proposal. It also related the
retained child response to signed source half-edge contributions, while warning
that balanced through-flow alone does not warrant another coordinate.

[CAN-F2](./decisions/ATCSourceFissionProposal.md) proposes a new constitutive
postulate: two inward participations may seed two activity-allocated sites once
each allocation exceeds its continuing exterior neighbor's resource. This is
not an inherited capacity, a theorem of necessity, or a claim that the existing
mediator cannot function. The first domain is unit-measure simple graphs with
maximum degree two. Singleton active loci resolve; multiple loci do not rank;
out-of-domain sources remain uncertified. The adjacent-resource benchmark needs
scientific review. CAN-B's structural route is not renamed or discharged.

The [focused run](./evidence/autonomous-topology-change/ATCSourceFissionProbe.json)
checks the additional source identity and retained controls, exact funding
equality, an equal-activity through-flow negative, synthetic positive and
multiple-active cases, and 96 algebraic order/orientation comparisons. One
fresh A_OS source admits two explicit reads and one ordinary commit: its
funding margin crosses from -1/256 to 631/131072 and the proposed source rule
selects b with its unique unordered partition. Current W/reset are unchanged;
reads and prescriptions do not publish. Zero topology events or target searches
occur, and no earlier native campaign is rerun.

Next assess the physical postulate, then pressure its selected target and
profile domains if it is retained. Executable source discrimination is progress,
not scientific acceptance, all-product closure or native ATC implementation.
All origin claims/debts and accepted records remain unchanged. No paper/spec
propagation, user acceptance or commit is inferred from the review.

## ATC — CAN-F2 endowment and target-support discrimination

The [benchmark review and native follow-up](./decisions/ATCFissionTargetDiscrimination.md)
sharpen the hypothesis without changing F2-v1 or its reviewed evidence. Its
rounded guard implies a locally resource-dominant parent, not a vertex capacity
or sustained inflow. The symmetric construction has initial child accumulation
exactly when its funding margin is positive. Two fixed asymmetric sources pass
the same rule while one child loses resource; in the second, even its exterior
current reverses outward. This refutes a stronger general support interpretation,
not the proposal's explicitly limited initial-endowment condition.

The focused native comparison uses the onset, both counterexamples and a
nonuniform-history split versus identity/history-reset control, each followed
by three ordinary steps. Original selection, allocation, references and
admission domains are preserved. Current/reset transport, W reinitialization,
edge currents and continuation are checked against literal equations; no
successful target is substituted for an adverse outcome. Target registration
remains caller-controlled, not native automatic ATC.

All fixed native predictions pass. The retained run has four splits, one
history-only event and sixteen ordinary commits. Unlike the symmetric and two
asymmetric review targets, the nonuniform-history target remains F2-active at
its larger child. No second event is executed; successful admission does not
establish stopping, repeated-event composition or continuing organization.

Next select the intended scientific meaning: deliberate initial-endowment
growth, or a separately reviewed stronger domain/law. Further passing predicate
or admission checks cannot establish the refuted support implication. Stable
organization, all thirty capability/family cells, structural CAN-B, composition
and sustained autonomy remain open; accepted claims, paper, specs and code are
unchanged. This review is not user acceptance and does not authorize a commit.

## ATC — next eligible F2 event and a proposed support-bearing fixture

The user agreed to two separate research questions while retaining F2-v1:
execute the next eligible descendant attempt and define an operational-support
assessment. Agreement to that work is not acceptance of a new scientific law.

The [follow-up](./decisions/ATCFissionContinuationAndSupport.md) replays the
weighted split and its first ordinary step with exact predecessor receipts.
On the same native owner, a fresh source read selects the larger child with
shares (16791/32768,15977/32768). Its sole target commits; current and reset
independently conserve charge, W reinitializes, and the five-node target reads
`no_event`. There is no second event in the first invocation or future-target
search. Caller target registration remains explicit. The new attempt is
bounded source-law-to-event evidence, not installed autonomous ATC.

All sixteen old split frames satisfy the review's exact collective-gain
identity. Resource gain, individual support and organization are still different
claims. Support is now assessed through a fixed balanced-load operation,
background-subtracted response, formation-neutral control and return horizon,
without requiring unequal child responses or autonomous isolation.

ATC-SUP-MW-AOS-v1 proposes one identical three-well site potential at every
vertex. Its exact rational certificate establishes a local charge-5 return
component and positive per-child load response; the same-charge uniform
barrier preparation has negative response. The old counterexamples are not
revised, and the new potential's pre-existing wells are not called a spark.
This is a new mathematical binding requiring review. No production evaluator
exists for it, no native support campaign ran, and no G2 or graph authority is
inferred. Review the binding and explicit evaluator bridge next; all thirty
capability/family cells and the unchanged broader scientific debts remain open.

## ATC — support review, native bridge boundary and causal controls

The [independent-review integration](./decisions/ATCSupportFixtureReviewAndBridge.md)
records favorable bounded repeated-use evidence and PASS for the proposed
multiwell mathematical existence fixture. It narrows formation-dependent
support to resource-organization dependence: the neutral preparation is not
a same-source no-fission counterfactual. Fission-caused durable acquisition,
parent nonviability, H5-style non-factorizability and child identities remain
unestablished. Neither original positive record is replaced or promoted.

Read-only native pressure confirms that source/target zero-potential controls
pass while a properly reidentified new potential is rejected at current,
crossing and initializer boundaries, including both roles. Twelve expected
rejections demonstrate the missing bridge, not native support. No steps or
events run. Gate N requires a new potential-plus-initializer contract and
off-root potential/flux checks; unchanged all-one W would conceal an omitted
site term. Existing accepted declarations and production code are untouched.

Gate C separately compares fission, direct preparation of the same scientific
target state and a common-source no-fission counterfactual, with projected
loads/budget observations. Equal futures after direct preparation would be
consistent with state-mediated causation, not establish fission irrelevance.
That experiment is specified, not executed. No automatic acceptance, commit,
claim/debt promotion, paper/spec propagation or capability closure follows.

## ATC — content-bound support recipe and exact causal preregistration

The subsequent [bridge review](./decisions/ATCSupportFixtureReviewAndBridge.md)
reports PASS as a research design and PASS for the native-boundary probe, with
Gate N and Gate C both OPEN. The proposed machine binding now fixes the site
polynomial, units, domain, exact rational evaluation/rounding, finite work and
public role-qualified initializer intermediates. A locally pinned SHA-256
identity rejects fourteen content mutations, including recomputed incoming
hashes. This is not accepted evaluator registration or production implementation.

Independent factored/incidence and expanded/Laplacian arithmetic verifies the
review's exact pre-execution predictions: P C+ = C-, P f+ = f-/6, both source
projected-load responses positive, both target pair-total responses positive
but smaller, and both addressed-child Q positive. Full delta vectors and
stage-rounded oracle values/comparison bounds are retained. These predict a
state-mediated reorganization of existing response, not acquisition from
absence, incidence-only causation or a source stability theorem.

Direct preparation must be independently admitted as a fresh publication,
not produced by stripping event receipts. Its scientific equality prediction
is distinct from complete-publication equality. No native experiment ran in
this pressure step. Original evidence, F2, accepted authority, paper/specs,
production code and all capability/gate dispositions remain unchanged.

## ATC — final design/preregistration review complete; native scope decision

The final independent review reports PASS for bounded research admission review
of the potential binding and PASS for Gate-C preregistration. It independently
confirms binding/record identities, exact vectors and conservative numerical
bounds, and requests no mathematical redesign before Gate N. Both native gates
remain OPEN; this is review completion, not user acceptance or runtime admission.

The [bridge note](./decisions/ATCSupportFixtureReviewAndBridge.md) now preserves
scientific F/D mismatch as a falsification condition and keeps three prospective
native claim subjects separate: changed baseline projected dynamics, changed
shared response, and separately addressable positive child channels. The
interpretation candidate is differentiation of participation, not increased
aggregate capacity, independent identities or a general fission theorem.

The review recommends native research implementation next. This intersects the
existing prohibition on production-owner changes before proposal/paper/spec
propagation. Explicit direction is required for a bounded research-only
exception, otherwise the existing route applies. No runtime change, new
acceptance, numerical rerun or commit is inferred from the review.

## ATC — placement clarification and local support-law execution

The user clarified that the freeze is about the substrate `src/*`, not code
creation in this investigation. Research implementations should provide the
mathematical foundations for the paper. This supersedes the preceding
unnecessary request for a production exception; no exception is taken.

The [local realization](./decisions/ATCSupportLocalResearch.md) implements the
fixed reduced A_OS equations, both-role reference-pass evidence and local
resource/reset operations, with no production backend/schema registration or
receipt machinery. Eight focused checks pass against an independent expanded
polynomial/dense-incidence oracle. The fixed unchanged F2 prescription supplies
one local split, followed by matched fission/direct-preparation/no-fission
histories and independent encounters at ages 0, 8 and 15.

All preregistered initial causal differences reproduce exactly. F/D scientific
trajectories agree; the source already responds positively and the target pair
response is smaller. Individual child channels remain positive at all three
checkpoints. All eighteen loaded continuations remain in the box and decrease
energy over sixteen updates; equilibrium distance decreases but complete
relaxation is not asserted. Maximum represented charge drift is about 1.89e-15,
reported without repair. Infinite rounded return is not inferred from the
separate exact-arithmetic certificate.

This is local scientific evidence awaiting review, not substrate-native
conformance or accepted law/claim closure. Existing binding, predictions,
certificate, F2, accepted claims and substrate files are unchanged. Native
integration remains later work and is not a prerequisite for local research.

## ATC — bounded research closure and outward sufficient-condition proposal

Independent review reran all eight local SupportTests, verified the retained
execution/source identities and confirmed the fields and causal comparisons.
Record N-R PASS/CLOSED and C-R PASS/CLOSED for the fixed bounded research claim.
Production integration/reproduction is explicitly N-P/C-P and deferred. This
does not mint accepted claim nodes, close generic capability cells or infer a
user acceptance/commit. Keep projected baseline change, shared response change
and persistent observed child addressability as separate scientific subjects.

The nonblocking redundant-allocation issue is hardened by an append-only
checked constructor interface. Seven invalid/missing forms reject; the valid
construction and current/reset initializer evidence match exactly. Original
model, tests, driver and evidence remain byte-identical. No F/D/N campaign is
rerun to re-close the already reviewed questions.

The new [sufficient-condition proposal](./decisions/ATCAddressabilitySufficientConditions.md)
separates source convergence/endowment, the conservative degree-two map,
target energy curvature, equilibrium clearance and encounter response. It
does not require particular polynomial roots. Exact interval inequalities
hold uniformly for p_lambda = p_0 + lambda C, |lambda| <= 1/8192, with positive
source current, trapping and both child responses. Nonzero lambda removes
the exact-root coincidence at all three old operating levels. The fixed
binding and preregistered predictions are not changed.

This extends an existence witness to a proposed conditional criterion and a
locally robust mathematical family, not a universal formation theorem or
all-ten-family result. Review of the proof, claim/debt successor mapping,
nonzero feedback and higher-degree applicability remain open. No substrate
changes or production gate promotion occur.

## ATC — conditional theorem review PASS and slope-softening corollary

The supplied independent review reports separate rederivation of the proof,
Bernstein coefficients from the monomial polynomial, all theorem-relevant exact
rationals and the retained certificate digest. Record PASS for the conditional
theorem, uniform non-root family certificate and affine exclusion, with no
mathematical blocker. Apply the proof precision amendments in the
[derivation](./decisions/ATCAddressabilitySufficientConditions.md): compact closed
positive intervals and explicit Euclidean clearance; projected charge-tangent
gradient; charge-preserving cancellation at equilibrium; integral/secant
definition of the finite-difference slopes. Also state j_t = -eta g(0) and
clarify that response positivity follows from convexity plus the chosen loads,
not an independent physical discriminator or general controllability.

The new corollary is necessary for this sufficient route: source participation
requires the secant slope from r to 2x to be below 3 kappa, hence p' is below
3 kappa somewhere outside the target neighborhoods where it exceeds 4 kappa.
At kappa = 0 that contrast requires a negative derivative somewhere despite
positive target slopes. The affine exclusion survives the exact target
spectral bound 2+sqrt(2), not merely the conservative bound 4. Softening alone
is not sufficient and no specific well count or root placement is required.

The certificate/checker, reviewed fixture, binding and execution records stay
unchanged. Mathematical review PASS does not mint accepted claim authority.
N-R/C-R remain closed; N-P/C-P remain deferred. Next work is bounded claim/debt
mapping and the transformation of this constraint under geometry/history
feedback or higher-degree partitions, not another fixed-polynomial campaign.

## ATC — graph/partition dependence before feedback

The user endorsed deriving the graph-dependent participation-versus-stability
criterion before restoring feedback. The
[new analysis](./decisions/ATCPartitionDependentStability.md) keeps the reduced
law fixed and supplies binary partitions of a symmetric unit-weight star,
with activity-proportional exact shares and one child bridge. It does not
select a partition or extend the installed degree-at-most-two F2 rule.

For d=m+n, source participation demands a secant below (d+1) kappa; affine
target stability demands a > kappa lambda_max(L_target). A Schur-complement
proof gives a nonempty affine window iff kappa>0 and m,n>=2. Thus singleton
blocks retain the original type of obstruction, but larger blocks can remove
the need for slope softening. The all-integer statement is analytical; 16
exact finite partition-size/isomorphism class checks pressure its algebra,
not substitute for proof.

For the smallest 2+2 case, p(c)=19c/4, kappa=eta=1 and h=1/8 give source
inflow 1/2, strict child endowment, Q_child=7/24 and exact geometric return
after one signed joint encounter at any unencountered age. The certified
positive-resource ball has lower coordinate bound 5/12. Initial child tendency
is negative, separating restorative response from accumulation. A funded/inward
1+3 control still has indefinite target curvature. These are exact mathematical
results, not native experiments, independent identities or an autonomous law.

The note maps bounded research implications to existing debt fronts without
discharging them or minting accepted claim nodes. Independent review and
formal successor adjudication remain open. Next analyze one genuine coupled
V4 feedback channel on the degree-two map; combining feedback and higher
degree follows separately. Reviewed evidence, native N-P/C-P, the thirty
capability cells, papers/specs and production sources remain unchanged.

## ATC — partition review PASS, exact pressure and scope corrections

The supplied independent review passes the partition restorative-curvature
window, nonlinear continuation, 2+2 funded/return witness and 1+3 funded
instability control. The finite roster is sixteen unordered block-size/
isomorphism classes, representing 247 labeled maps by symmetry, not an
enumeration of them. The iff guarantees a slope window and existence of a
stable positive Euler step; fixed h still requires every mode multiplier to
have magnitude below one. A large-step counterexample makes that limit explicit.

The [corrected successor certificate](./evidence/autonomous-topology-change/ATCPartitionStabilityReviewCertificate.json)
uses the corrected metadata, reproduces and binds the original checker/record,
and checks four exact Euler images. The actual s=3 source/target modes switch
from multiplier 37/32 to 11/32 at the same affine slope. For the same source
s=5, 2+2 contracts by squared-distance ratio 121/1024, while 1+3 expands by
66211/50176; the latter's three-edge child has Q=-3/16. These compare declared
maps and their allocations, not an autonomous choice or long-run s=5 encounter
certificate. The original s=3 positive-ball return certificate remains intact.

Bridge weight tau is recorded only as scope pressure: the Schur determinant
is (d+1)/d^2 times [mn(d+1)-tau*d^2], so the unit-bridge cardinality boundary
is not universal. Source symmetry still leaves three labeled 2+2 choices;
IDs cannot pick one. The proof also now makes the nonlinear q>=0 bound explicit.

There is no trajectory campaign, native step, new weighted runtime contract
or graph admission. The graph-only mathematical review is complete. Stop
extending the zero-feedback star family for now and move to one genuine
coupled V4 feedback channel on the degree-two map. Formal bounded claim/debt
admission and all broader capability obligations remain open.

## ATC — genuine retained-history feedback on the degree-two map

The user authorized the next feedback step after the partition mathematical
review. The [coupled analysis](./decisions/ATCHistoryFeedbackContinuation.md)
restores Candidate A's selected-current-squared retained-mobility writer,
with W evolving in both the direct mobility and potential stiffness. Geometry
source/read-back remain off. This is a separately named research law, not a
silent change to the reviewed gamma=0 binding or native potential admission.

For gamma in [0,256], rho=1/2 and the original multiwell/degree-two parameters,
an invariant rectangle in edge-charge displacement and log W admits a full
weighted-norm return proof. One signed joint child encounter at any
unencountered age remains in its domain; individual response stays positive.
The current-zero equilibrium has W=1, so the memory is transient rather than
a persistent resting identity. Its local eigenvalues are gamma-independent
because the writer forcing is quadratic at zero current; the finite nonlinear
bound, not that observation alone, establishes the stated basin. Failure of
the same sufficient bound at gamma=512 is not a proven instability.

Four finite mathematical step evaluations compare gamma-on/off from identical
incoming state. They confirm formation from neutral history and attributable
retention during prepared-history release, with changed next current. Wrong
same-beat W reuse, next-current writing and frozen-stiffness substitutions are
discriminated. The exact certificate retains rational inequalities and typed
forensic provenance without promoting the parent contracts' indeterminate
support dispositions. No trajectory campaign, native step or event ran.

At submission independent review was pending; the review disposition follows
below. Its bounded evidence concerns history/constitutive feedback and DB-07/27
support/discrimination, not CAN-B's DB-05/06/08 functional/mode/partition debts.
No debt is discharged or accepted node minted. Geometry/read-back channels,
higher-degree combination, native nonzero-gamma potential/initializer admission
and all-family capability remain
open. The old N-R/C-R, N-P/C-P dispositions, CAN-F2 guard, reviewed evidence,
paper/specifications and production sources are unchanged.

## ATC — coupled-history mathematical review PASS and scope corrections

Independent review finds no mathematical blocker and passes the coupled
return theorem, finite gamma interval [0,256], one bounded encounter, positive
child response and writer-to-next-current activation. It verifies the exact
certificate digest and checker hash now recorded in the
[derivation's review disposition](./decisions/ATCHistoryFeedbackContinuation.md#independent-review-disposition).
Both artifacts remain unchanged, including their preparation-time status.

The theorem is explicitly one-sided: exp(-1/128)<=W<=1, with nonpositive
log history. Both mobility bounds rely on that depression; W>1 is not
silently included. Operations remain fixed-reference -L_0 e_i, not adaptive
-L_w e_i. Gamma=256 is a sufficient interior choice, not a physical threshold;
gamma=512 only defeats the stated majorant. Gamma changes the finite nonlinear
estimates and a causal next read without changing local eigenvalues; no actual
basin-boundary movement is thereby proved.

The tree is essential to the unique edge-coordinate return proof. A narrower
point in the review is qualified: for the purely gradient current with
positive weights, g^T BJ=eta (B^T g)^T D_w(B^T g) also forces J=0 at resource
equilibrium on cyclic closed graphs. Thus cycles alone do not yield resting
history for this reduced law. This integration clarification supplies no
cyclic return theorem and does not widen the independently reviewed scope.

The earlier loose DB-05/06/08 attribution is withdrawn. No topology-changing
structural functional, critical branch, selected mode or mode-to-half-edge
partition lift is derived; CAN-B and especially DB-08 are unchanged. This is
retained-history/constitutive-feedback and support/discrimination evidence,
with no accepted claim/debt transformation. The next scientific task is another
genuine geometry/read-back channel; higher-degree combination and all broader
capability/native obligations stay separate. No research campaign is rerun.

## ATC — consumed OS geometry with the retained-history writer

The user authorized the next substantive feedback step. The
[new investigation-local theorem](./decisions/ATCOSGeometryFeedbackContinuation.md)
restores A's explicit Read-Back, normalized star assembly, affine Hodge update
and fresh corrector potential while retaining the reviewed gamma writer. W
remains mobility authority; generated geometry is neither retained state nor
an alternative mobility. Predictor baseline current owns its instantaneous
reference; selected corrector current owns continuity and the later writer.

On the same fixed-tree depressed-history rectangle, exact bounds cover
gamma in [0,256], chi_A in [0,1/2] and kappa_H/kappa_Ah in [0,1], with
zeta_A=1. H1>=I, both current denominators exceed 399/400, all three conductance
floors are inactive, and the nonzero OS split defect is below the declared
2^-30 operator-norm tolerance. A weighted-norm factor below one proves full
C/W return and derived geometry's return to reference. One signed joint
encounter remains inside the domain; the fixed-epsilon individual response
lower bound is 180242767/858993459200. It is not a uniform derivative theorem.

Ten finite mathematical steps check two symmetric preparations, asymmetric
state/dense geometry, three matched switch-off controls, signed coordinate
action, a next beat and two child loads. An extra corrector is observed only
as a forbidden-stage discriminator. Removing kappa_Ah leaves nonzero geometry
but removes its current effect, separating production from consumption. The
prepared geometry-current effect is approximately 5.048e-29; an inherited
depressed state gives approximately 1.384e-14. Exact activation is not a
claim of material native/binary64 resolution, especially for the former.

The source pipeline has the reviewed history tangent at equilibrium because
the new read/structural terms enter at higher order. Finite feedback remains
causal. These results concern constitutive feedback and support, not CAN-B
functional, branch, mode or partition-lift closure. The new certificate keeps
six forensic support dispositions indeterminate and binds the unchanged
reviewed predecessor. At submission independent review was pending; the
review disposition follows below. No native step/event,
trajectory campaign, accepted-node transformation or paper/spec/src change
occurs; higher-degree composition and broader capability obligations stay open.

## ATC — three-path OS mathematical review PASS and interpretation limits

The supplied independent review passes the coupled A_OS return theorem,
uniform exact-real parameter box, declared split admission, bounded encounter
and child response, and generated geometry's consumption by the corrector.
It verifies the exact certificate digest, checker hash and rational margins;
the [current review disposition](./decisions/ATCOSGeometryFeedbackContinuation.md#independent-review-disposition)
records those identities. The reviewed bytes are unchanged, including their
historical preparation-time status. No accepted claim or native gate is promoted.

Four boundaries now govern synthesis. First, the already established return
domain survives the added channels: geometry is not shown to cause stability,
enlarge a basin or improve a rate. Second, return holds throughout the gain box,
including zero-gain faces, while strict activation has selected witnesses at
the fully enabled corner. Third, robust native resource-endpoint nonannihilation
remains open. The inherited current gap produces a resource difference of
approximately 2.163e-16: 0.974 ulp at the actual child endpoints near 1.5,
but 1.948 ulps at the outer endpoints just below 1. These are scale comparisons
from retained high-precision diagnostics, not staged binary64 validation.
Fourth, 2^-30 is the research OS residual tolerance, not inherited native
profile authority; its norm, tolerance and arithmetic require later N-P binding.

The bounded three-path mathematical review is complete. Higher-degree,
all-family, autonomous-topology and native obligations remain open. The source
trace dispositions and CAN-B functional/mode/partition debts are unchanged.
Only retained-value arithmetic and documentation/integrity checks accompany
this review; no new numerical campaign, substrate change or handoff archive.

## ATC — supplied partition discrimination with one-pass A_OS history/read/geometry feedback

The user authorized combining the reviewed graph/partition and OS-feedback
results. The [new derivation](./decisions/ATCPartitionOSFeedback.md) keeps the
affine partition law p(c)=19c/4, eta=kappa_c=1 and h=1/8, rather than importing
the multiwell potential. A common new box gamma<=2^-16, chi_A<=1/2 and
kappa_H/kappa_Ah<=1 with exp(-1/256)<=W<=1 gives stage/floor/current/residual
admission for the declared source/targets. The 2^-9 residual tolerance is
research-only. The complete law includes retained W in mobility and stiffness,
fresh predictor/corrector reads, overlap-normalized dense geometry, actual
geometry consumption and the selected-current writer.

For the same s=5 funded source, the supplied 2+2 target enters a positive
radius-one domain in one step and has exact full-state contraction factor
below 0.936002, including one signed fixed-reference encounter. A complete
staged derivative bound retains both positive child responses. The 1+3 map
retains an expanding homogeneous tangent and, separately, a positive-resource
first-step distance increase above 2.726 from an initial distance below 2.5.
Its large-child response remains negative throughout the same declared box.
No infinite positive divergence, stability caused by geometry or differentiated
resting identities are inferred.

Twenty-one finite mathematical steps check both maps and matched channel
controls, rational zero-feedback images, scalar source/target oracles, loaded
responses, nonuniform history, signed coordinate action and one continuation.
Two unselected stage probes pressure premature new-history reuse and forbidden
OS iteration. The fully enabled 2+2 geometry effect changes resource endpoints
at about 10^-6 in Decimal96; an exact positive lower bound proves activation.
This is neither a repair to the old tiny witness nor native conformance.

Both reviewed records and their source identities are checked unchanged. Six
typed current forensic queries equal the previously retained complete traces;
the new certificate references those exact rows instead of duplicating an
archive. At submission independent review was pending; its PASS and scope
clarifications follow below. Claim/debt graph,
CAN-F2, CAN-B functional/mode/partition obligations, native scope and all-family
capability cells remain unchanged. After review, investigate the missing
source-side distinction/equivariant partition choice: the symmetric source's
three equivalent labeled 2+2 maps remain unresolved.

## ATC — partition/OS mathematical review PASS with explicit channel and evidence scope

The supplied independent review finds no blocking mathematical defect in the
combined supplied-partition/history/read/geometry result. It passes common
stage admission, 2+2 entry and positive full-state encounter-return, 1+3's
expanding tangent and positive-resource first-step expansion, retained child
response signs, symmetric source participation and consumed geometry.
The [review disposition](./decisions/ATCPartitionOSFeedback.md#independent-review-disposition-and-evidence-boundary)
records the verified certificate digest and checker SHA-256. Those reviewed
bytes and both predecessor records remain unchanged, including historical
pre-review status in the machine record.

The reviewed scope is explicitly one-pass A_OS history/read/geometry feedback,
not every Candidate-A channel: alpha=beta=0 and there is no carrier. The
identity adapter in common overlap-normalized star-tensor coordinates is
load-bearing; another typed adapter needs new positivity/norm/derivative
bounds. The 2^-9 residual tolerance belongs to this research declaration,
not native authority. Return and response-sign bounds cover the gain box;
strict activation is demonstrated at selected fully enabled prestates.

The reviewer read and compiled the checker, verified identities and
independently reconstructed central exact bounds and margins. Its environment
lacked the complete predecessor/forensic context for an end-to-end run.
The Decimal96 observations remain the original retained execution evidence,
not an independent numerical rerun or a finding of missing repository inputs.
This review integration requires no campaign rerun or evidence replacement.

Source participation, supplied partition and post-partition support remain
separate scientific subjects. Equal symmetric source activity is compatible
with different consequences for 2+2 and 1+3; those consequences cannot supply
a retrospective source-side chooser. The next scientific question is lawful
source information and equivariant selection, with an invariant set-valued
alternative or unresolved symmetry legitimate for the perfectly symmetric
source. CAN-F2, accepted claims/debts, native gates and all-family capability
obligations are unchanged; no new selection mechanism is implemented here.

## ATC — source symmetry obstruction and a bounded activity-grouping proposal

The user authorized the next source-side investigation after the partition/OS
mathematical review. The [new derivation](./decisions/ATCSourcePartitionSymmetry.md)
proves that a fully S4-symmetric four-edge source has no deterministic
equivariant singleton binary partition. The seven possibilities form orbits
of sizes three and four; a favorable target size class cannot select one.
Its normalized symmetric geometry has a three-dimensional degenerate contrast
space and therefore supplies no hidden frame. Equivariant fixed-graph evolution
preserves exact source symmetry. Equal projected activities alone, however,
need not imply symmetry of every physical source field.

The proposed source-only consumer minimizes within-block inward-activity
variance over all seven partitions, returning every tied minimizer rather
than ordering by IDs or filtering through target outcomes. This is an explicit
new grouping hypothesis, not a derived fission trigger or physical necessity.
Exact score gaps and perturbation bounds preserve unique two-level groupings
away from symmetry; no uniform error margin survives at symmetry. A physically
asymmetric source may also leave this particular score tied.

For the affine A_OS source star with parent C=5, zero-sum leaf deviations
bounded by 1/64 and uniform depressed W, new stage/derivative bounds hold on
the declared gain box. They prove that selected inward activities preserve
strict leaf-resource order with separation coefficient above 3.7242. The
same proposed rule then returns either 2+2 or 1+3 on the corresponding
two-level source families. Seven finite Decimal96 present reads, an independent
reduced-star oracle, signed/reordered actions and 1,920 small exact rule checks
support these bounded statements. No target is evaluated, no retained writer
or ordinary step runs, and no event/campaign/native execution is claimed.

At submission, independent review was pending; its disposition follows below.
The reviewed partition/OS evidence and all
accepted authority remain unchanged. Source-law/resolution and covariance
fronts gain partial research evidence; CAN-B's functional/branch/mode debts,
physical refinement justification and all capability cells remain open. After
review, decide whether/when this grouping should have constitutive refinement
force and justify its source-only trigger/funding/allocation, or identify a
better source invariant. A unique grouping is not proof of a viable target,
spontaneous asymmetry formation or an obligation to split.

## ATC — source-partition mathematical PASS; constitutive choice remains open

The supplied independent review passes the exact S4 singleton obstruction,
degenerate generated contrast geometry, selector covariance/exact ties,
conditional robustness, coupled A_OS ordering/separation and both two-level
source-resolution families. It independently reruns the exact routines and
all seven finite source reads, matching `exact_checks` and `decimal_diagnostics`
including signed/reordered representations. This does not assert an independent
end-to-end rerun of the forensic wrapper. The
[review disposition](./decisions/ATCSourcePartitionSymmetry.md#independent-review-disposition-and-evidence-boundary)
pins the verified checker SHA-256 and certificate digest. Reviewed bytes and
the machine record's historical pre-review status are preserved.

Four distinctions are now explicit. Equivariance permits either complete
partition orbit or their union; returning all seven at equality belongs to
the variance rule. Its objective maximizes mn times squared block-mean
separation, exposing cardinality weighting rather than deriving it from
covariance. The uniform-W two-level examples do not distinguish current-based
grouping from resource grouping. Finally, neither new asymmetric 2+2 nor 1+3
source inherits the old target-support result; a future activity-share
allocator would generally change the old equal 2+2 resource split.
One precision correction to the review itself is retained: score gaps shrink
quadratically near symmetry, while the sufficient D/10 error radius shrinks
linearly. No checked mathematical result changes.

The next bounded research question is competing resource/current information
under lawful W/context/geometry variation, with new domain checks and a
principled physical interpretation rather than mere numerical disagreement.
Grouping authority and, separately, the trigger and child funding/allocation
must be justified before testing selected targets; target consequences cannot
retrospectively choose source partitions. The variance rule remains a
constitutive hypothesis, not a derived fission law. No accepted claim/debt,
CAN-F2 rule, native gate or capability cell is changed, and no new campaign
or production work accompanies this review integration.

## ATC — competing resource/history source information and a conditional rate interpretation

The user authorized the bounded source-information continuation. The
[new derivation](./decisions/ATCCompetingSourceInformation.md) keeps the same
affine A_OS source law but rederives its bounds for crossed nonuniform retained
W. On theta in [1/1024,1/512] and delta/theta in [1/128,1/64], resources uniquely
favor {{0,1},{2,3}}, whereas the complete fresh selected current uniquely favors
{{0,2},{1,3}} throughout the declared gain box. All seven partitions participate.
Uniform positivity, floor, geometry, residual and score-gap estimates establish
the result; an additional activity error of norm theta/64 still preserves it.

History reassignment preserves resources and the history multiset but changes
the selected partition. Equalizing history restores resource grouping;
equalizing both fields restores unresolved full symmetry. Thus resources alone
cannot reproduce the current-based partition across these lawful prestates.
The source is supplied, not formed by an executed history trajectory.

Continuity gives a precise conditional interpretation: current variance is
the two-block least-squares approximation error of instantaneous leaf resource
rates, whereas resource variance approximates inventory. This does not select
that objective as a constitutive law. History-only grouping also agrees in
this history-dominated family, and disagreement survives switching Read-Back
off. Enabled geometry is consumed but is not necessary for the partition
difference. No fission need, allocator, target support or general source
optimality is inferred.

Exact rational estimates, three scalar baseline anchors and twelve Decimal96
complete source reads pass. Independent reduced-star predictor/corrector
oracles, gain/symmetry/history controls, signed reordering, rate-projection
identities and three domain rejections are retained. Six typed equation traces
match predecessor references; the additional continuity trace is retained in
full with `indeterminate_requires_review`. These are research reads, not
ordinary updates, retained writes, targets, native steps or a campaign.
At submission, independent review was pending; its disposition follows below.
All reviewed predecessor artifacts, accepted
claims/debts, CAN-F2 and capability cells are unchanged. Next establish what
source-side physical requirement warrants refinement, comparing rate coherence
with competing interpretations, and justify trigger/funding/allocation
separately before target testing.

## ATC — competing-source mathematical review PASS with instantaneous scope

The supplied independent review passes the conditional source-information
theorem, resource-only insufficiency, uniform robustness through the fresh
A_OS read and the continuity-rate least-squares interpretation. It independently
checks the certificate digest and checker hash, exact history/perturbation
bounds and both rational score-gap margins, the upper-anchor continuity
identity and retained diagnostic values. It does not report a fresh execution
of all twelve source reads and explicitly does not rerun the repository-only
forensic stage. Those original executions and traces remain retained evidence.
The [review disposition](./decisions/ATCCompetingSourceInformation.md#independent-review-disposition-and-evidence-boundary)
records the verified identities; checker/certificate bytes and historical
pre-review machine status are preserved.

The main ceiling is now a headline: current and history grouping agree
throughout this deliberately history-dominated family. The result separates
resources from current/history, not current from raw W grouping. Read-off and
geometry controls confirm compatibility with those channels rather than their
necessity for the partition difference. The resource grouping's upper-anchor
gap is exactly 1/402653184 in resource-squared units; it is unique but weak,
not an equal-strength contest with history.

The rate interpretation is explicitly instantaneous approximation on an isolated
star with degree-one neighbors. It does not establish an invariant subspace
under complete C/W evolution, a commuting autonomous quotient, persistence of
the chosen partition, or evolution of children as block means. The identity
between a contact activity and a full neighbor rate does not extend to neighbors
with other incident edges. None of these qualifications changes the proved
inequalities or requires replacing the reviewed numerical evidence.

The next proposed pressure is current versus retained history. Prefer a lawful
newly bounded source family with resource, history and selected-current variance
partitions all distinct; a separately declared source-only persistence study
is an alternative, not a second required campaign. Either strengthens the
scientific comparison without itself deriving a refinement principle. The
bridge from instantaneous exchange-rate coherence to fission structure and
the separate trigger/funding/allocation obligations remain open. No new research
execution, accepted claim/debt change, native work or target campaign accompanies
this review integration; CAN-F2 and all capability cells remain unchanged.

## ATC — prioritize physical continuation obstruction over grouping refinement

The user agreed that the next investigation should concern when an unsplit
topology ceases to sustain a required continuation, rather than simply improve
evidence for a grouping observable. The supplied comment sharpens four distinct
scientific tests: endogenous development of a condition, genuine obstruction
to remaining unsplit, a mechanically connected partition, and admissible
invariant-preserving resolution by refinement. Neither an arbitrary score
threshold nor a solver failure establishes such a mechanism. Repeated bounded
negative examples cannot prove absence of refinement need in all V4 profiles.
The previously proposed three-way grouping/persistence studies are now optional
mechanism discriminators, not independent milestones.

The [new investigation](./decisions/ATCUnsplitViabilityAndMechanicalBoundary.md)
uses the existing affine research A_OS declaration on the symmetric four-leaf
source at charge 9. New bounds cover the whole positive concentration range
0<x=s-r<9 and uniform log history in [-1/256,0], including actual writer
evolution and fresh predictor/geometry/corrector reconstruction. The selected
inflow obeys j >= (5015/21888)x, forcing eventual positive-domain exit for every
fixed positive step. At h=1/8 it occurs by the seventh attempted update.
This is a conditional failure of indefinite closed positive continuation,
not an empty instantaneous root set, a newly crossed instability onset or a
universal native resource requirement. The zero-channel continuous-time
control reaches the positivity boundary too, separating the phenomenon from
mere Euler overshoot.

All activities remain equal, and the unstable mode contrasts parent against
all leaves; neither supplies a binary partition. The reviewed supplied 2+2
target is restorative at the same initial prestate, but this does not establish
a mechanically selected or correctly timed event, a remedy at later depleted
states, or fission as the only possible resolution. K0 cannot invoke an event
after an ordinary rejection; no witness or scheduling rule is changed.

An additional exact diagnostic exposes the missing energetic choice. Adding
mu per vertex leaves the declared fixed-graph derivatives/read/writer unchanged
but shifts a split's energy difference by mu. The two historical supplied maps
have zero-offset differences -35/16 (2+2) and -305/64 (1+3): the known unstable
control drops more energy. No target ranking is installed, and no full-feedback
Lyapunov claim follows. An energetic refinement principle must independently
justify its creation-energy reference/barrier rather than tune it for birth.

Exact inequalities, mode identities and 51 energy-gradient checks pass. Two
Decimal96 continuations each make five positive mathematical resource/writer
updates and reject their sixth proposal without a write. Fourteen full source
reads include those failed-update prestates, homogeneous and coordinate
controls, with scalar/dense agreement. No native step, topology event or new
target dynamics is executed. Six inherited typed traces match; continuity and
writer-target traces retain their `indeterminate_requires_review` dispositions.
The new checker/certificate are investigation-local and repository-relative;
reviewed predecessors, accepted claims/debts, CAN-F2, capabilities and runtime
remain unchanged. Independent mathematical review is pending. Next seek an
obstruction-linked refinement principle and covariant partition, with the
missing timing/creation/funding/history/target authority explicit.

## ATC unsplit audit and critical-mode/operation-compatibility continuation

The user supplied an independent mathematical PASS of the unsplit-viability
result and authorized continuation to the next question. The review reproduced
exact bounds, energy/mode identities, certificate/checker identities and the
enabled scalar trajectory. It did not execute the repository checker and
forensic dependencies end-to-end. The old checker and certificate remain
unchanged; the decision note records the review without upgrading accepted
scientific authority or historical machine status.

The [successor derivation](./decisions/ATCCriticalModeAndRefinementTest.md) first
closes the adaptive-step question: summing the old lower current bound gives
total duration below 5472/5015 for any accepted positive prefix. Hence no
non-Zeno positive adaptive schedule restores that declared continuation. This
does not forbid finite-time Zeno accumulation or authorize native adaptation.
The energy qualification also matters: reference H0 already has positive
vertex-measure notation, but the inspected charge/Hodge/event contracts do not
supply an extensive conserved-measure fission law. A density-energy convention
with conserved measure cancels an extensive additive constant and changes the
target mathematics. The unit-site identifiability result is not a theorem that
every future subdivision requires a per-site birth constant.

The next source fixture has five vertices and twelve unit-reference edges:
four parent spokes and two parallel edges for each cross-pair between two
two-leaf classes. Its Laplacian spectrum is 0,5,5,5,9, with simple top mode
(1,1,-1,-1,0). Under a newly declared p(c)=15c/2 law, ordinary uniform history
recovery from W=3/4 crosses W*=5/6. The old potential and source graph are not
silently reinterpreted. The full homogeneous A_OS step Jacobian has that simple
resource multiplier crossing and stable history/other resource modes. Geometry
gains can be enabled, but their derivative at zero current vanishes; this is
not a nonlinear full-feedback obstruction theorem.

In the exact zero-read control, a nonzero critical-mode perturbation has actual
resource/history evolution and eventually exits positivity. Parent-incidence
rectification makes contact signs independent of edge orientation. Only the
parent has both signs, so the source determines one unordered 2+2 partition
without IDs or target lookahead. The homogeneous zero-perturbation trajectory
stays positive: instability onset is not universal mandatory firing.

Only after deriving the lift, one conservative unit-site map is tested at the
first successful source successor. It halves the parent resource, retains old
edges/history and initializes one bridge at W=1. Its odd-sector Laplacian has
a largest eigenvalue greater than the source's 9W. A positive-cone growth
argument proves eventual positive-domain exit with actual evolving histories,
not merely a frozen spectral warning. Thus the critical mode gives a partition
but not a restorative operation: retained cross-contact connectivity sustains
the obstruction. No other maps are searched or ruled out.

Exact identities and one focused run pass: 29 background/derivative reads,
23 continuation reads, 21 positive mathematical resource/writer updates and
two rejected proposals. The source rejects attempt 13 after twelve positive
updates; the mapped target rejects attempt 10 after nine, starting from its
later source prestate. No writer executes on either rejection. Eight inherited
typed traces match, and four additional measure/Hodge/charge traces retain
`indeterminate_requires_review`; they supply lineage, not new admission.

This successor awaits independent mathematical review. The next productive
question is operation compatibility and coarse/fine state/tangent plus measure/
energy semantics: which obstruction does a physically meaningful refinement
actually remove? K0's success-only timing and reference witness stay unchanged.
No native event, accepted claim/debt transformation, CAN-F2/capability closure,
paper/specification edit or production change follows from this local research.

## ATC critical-mode audit: stop the mechanism branch, keep ATC-2 open

The user supplied the critical-mode review after reiterating that autonomous
splitting and ATC-2 closure, not refinement sophistication, govern the work.
The review gives the bounded mathematics PASS and independently reconstructs
the source spectrum/crossing, rectified signatures, adaptive bound, target
odd-sector equations and both source/target zero-read continuations. It checks
certificate digest `6e3a7831bd7ae9ec3f5fa45925d3776837d1e996a6d6dec88e602ca3cf09e647`
and checker SHA-256 `9a10e97c87a521ac9614565a84d1a5729fc8db5527df147d02f3074179e995fc`,
but does not report running the complete repository forensic checker.
Those original artifacts and their historical machine status stay unchanged.

Record the scientific disposition as **mechanism implication refuted in this
family; stop this branch**. This is not aggregate ATC-2 closure or formal
accepted-graph claim/debt adjudication. The review identifies why no further
bridge/allocation tuning is warranted: the mode's squared norm is 4, its star
contribution is 4 and its unaffected cross-edge contribution is 32. A zero
extension to the new children gives target lambda_max>=8w on the unit-measure
charge-zero tangent, irrespective of additional positive-mobility parent/bridge
terms. The same affine zero-read generator retains an unstable eigenvalue once
w>15/16, and the unchanged cross-edge history recovers toward one.

This bound excludes removing the spectral instability within that operation
class. It does not prove every specially prepared target trajectory exits or
exclude new measure, history, nonlinear-feedback or nonincident-edge laws. The
particular tested map retains its separate finite-amplitude exit proof. A lean
read-only check confirmed 4,32,4, the threshold and all twenty retained source
bindings; no numerical campaign, new target or forensic suite was rerun.

The [decision note](./decisions/ATCCriticalModeAndRefinementTest.md) and current
plan/checklist/handoff now prioritize the complete autonomous-split chain. The
next candidate must show that its allowed primitive can modify a component
responsible for the obstruction before target construction. Sufficient untouched
obstruction is a reason to abandon the candidate, not elaborate its measure or
allocator. This is a scientific screen, not another governance/tooling gate.
Measure/coarse-fine/history semantics are subordinate to a compatible mechanism.
Any additional constitutive physics must be explicit through claims/debts;
bounded failed branches do not establish universal impossibility. ATC-2,
autonomous splitting, capability cells and accepted authority remain open or
unchanged at their existing dispositions. No commit or production edit is made.

## ATC localized-sector candidate: positive bounded source-to-target evidence

The user authorized the next operation-compatible investigation, asking whether
the unfolding could yield positive evidence. The failed cross-edge mechanism
was not reopened. The [new candidate](./decisions/ATCLocalizedSectorFission.md)
uses an isolated four-star whose obstructing support is actually changed by
splitting its parent. Two exact retained-mobility sectors, with equal resources
inside each pair, remain invariant under the reduced ordinary dynamics. They
also equal the two exact contact-amplitude classes of the simple top Laplacian
mode. All contact signs agree; this is not the stopped sign-split rule.

The affine p(c)=19c/4 research law has zero alpha/beta/gamma/chi_A, no carrier,
unit reference geometry and actual square-root W recovery. The prepared source
W=((19/20)^2,(19/20)^2,(77/80)^2,(77/80)^2) is not formed by its canonical
zero-channel initializer, which would yield one. Initially all source resource
modes are damped. After one positive ordinary commit, a source-only Rayleigh
certificate becomes positive. An exact two-sector cone recurrence proves
eventual positive-resource exit if the source remains unsplit, with multiplier
at least 8345/8192 for its concentration coordinate after that boundary.

The new constitutive postulate promotes the two exact response sectors to
sites when that certificate, strict inflow and dyadic child-funding conditions
hold. No target outcome selects the partition. The retained current yields
k=30876, shares 7719/16384 and 8665/16384. Only then does the checker construct
one target using proposed ATC-2 reference/resource conventions and explicit
all-W loss/reinitialization. The same conservative map acts separately on
current and the actual initial reset. Both-role mathematical read and first
continuity checks pass; no native initializer/owner admission is inferred from
the abstract producer formula.

The resulting unit-weight double star has maximum Laplacian eigenvalue below
19/4. At h=1/8 its charge-tangent contraction factor is
(53+sqrt(17))/64<457/512. Both roles enter a radius-2/3 ball about (3/2)1
after their first positive target step and remain above resource 5/6 thereafter.
The reset entry is independently checked; it was outside the simpler initial
positive-ball bound. Thus restoration is proved at the actual selected source
boundary, not imported from an unrelated original prestate.

No split rejects attempt 10; resetting history without splitting rejects
attempt 7 from that same poststate. Homogeneous input does not fire; ambiguous
history/resource sectors and multiple active loci are unresolved. Twelve exact
coordinate actions preserve the prescription. Target policy reevaluation is
defined and returns no event for the double star. Exact rational entry checks,
41 Decimal96 reduced reads, 39 positive resource/history writes and two rejected
proposals pass; no rejected state writes history. The represented-input companion
retains the same allocation bin and exposes exact stored charge, without claiming
native charge admission. No target search, native run or old campaign occurs.

Typed continuity/writer traces preserve `indeterminate_requires_review`;
the selected initializer contract retains required support for an optional
producer claim, not authority for this new potential or topology consumer.
The new certificate is
`66e7faa8899da3ab0aa636a5f943fcc97cd1451adeb2ff0a93cc09cd96cab0af`.
The complete bounded mechanism is positive evidence, but the sector-to-site
physical postulate, prepared-history origin, exact-symmetry restriction and
explicit history loss need review. There is no universal guard-positive return,
formation, nonzero-feedback or all-family theorem. Review this candidate and
its source-domain ceiling next; if accepted, establish its admitted restoration
domain and authority before extending it. ATC-2, CAN-B, formal claims/debts and
capability cells are not closed. No production, paper/specification or commit
change is made.

## ATC localized-sector review: preserve history, separate pressure and funding

The supplied review passes the original bounded causal-chain mathematics. Its
independent execution covers `exact_stage()` and `finite_runs()` in isolation,
not the full repository/forensic runner. The reported original checker SHA and
certificate digest match. That evidence remains byte-identical; its embedded
pending-review label is historical, not the current review disposition.

Two corrections are integrated in the
[same scientific note, Section 8](./decisions/ATCLocalizedSectorFission.md#8-review-integration-retain-history-and-keep-pressure-distinct-from-funding),
with a [focused successor checker](./scripts/certify_atc_sector_lineage.py) and
[certificate](./evidence/autonomous-topology-change/ATCSectorLineageCertificate.json):

- The selected research transfer now preserves old-edge histories by lineage,
  independently in actual current and reset. Only the new child bridge is seeded
  to one. The source prescription, graph and resource map are unchanged.
- The review's retained-reset comparator used current W1. Actual reset history
  is W0; exact calculation gives first-step norm squared 0.3246804772, not
  0.3504555063. Current gives 0.2512835384. Both steps are positive and enter the
  radius-2/3 ball. Uniform mobility bounds and a common 1829/2048 contraction
  prove indefinite continuation with changing histories; the constant HRESET
  bound is not reused. History erasure is unnecessary for this restoration.
- Certified source obstruction/decomposition precedes transfer funding.
  Unfunded selected transfer is `blocked_transfer`, not `no_event`. Mixed
  funded/unfunded pressure loci remain unresolved; funding cannot supply an
  implicit ranking or runner-up. Size rejection also preserves pressure.

Focused exact checks, twelve coordinate actions and six Decimal continuation
steps pass. Original no-split/reset-only failures are retained, not rerun. All
26 predecessor/current source bindings match; the successor digest is
`787c4a1cf33b3152a228751db98363389a268158614ad7279af79c398adc2521`.
This is local validation of review corrections, not independent review of the
successor or native execution. The lineage/new-coordinate producer remains a
research transfer proposal; the old ATC-2 CAN-HRESET and accepted initializer
contracts have not been silently changed.

The next scientific decision concerns the remaining sector-to-site postulate:
why exact persistent response sectors should become sites when their common
parent is obstructed. Removing gratuitous history loss sharpens that question;
it does not derive the postulate from V4 or make creation measure-neutral.
Prepared-history origin, exact symmetry, zero Read-Back, general feedback and
all-family coverage remain ceilings. No prettier target, partition optimization
or renewed failed-branch campaign is proposed. ATC-2, formal claims/debts and
capability cells remain open/unchanged; source, paper/specification and production
authority are not promoted. No commit is made.

## ATC lineage review PASS: distinguish semantic causes before propagation

The supplied successor review independently executed `exact_checks()` and
`finite_checks()` with generic helper substitutions, confirming both actual
history roles, charge, uniform contraction and all six positive updates. It
recomputed certificate `787c4a1cf33b3152a228751db98363389a268158614ad7279af79c398adc2521`
and checker SHA `207fece35ac40284ea0481d2b69a2d639d12ea8a4f06c24fa7308f242fe5aa07`.
This is independent mathematical PASS, not a reported repository wrapper or
native execution. Reviewed artifacts remain unchanged; the later disposition
supersedes their historical pending-review wording without editing evidence.

The [status correction](./decisions/ATCLocalizedSectorFission.md#9-lineage-review-pass-and-status-typing-corrections)
addresses both review pressures: multiple resolved decompositions remain
`resolved_per_locus` while locus arbitration is `multiple_unresolved`; funding
and construction-domain admission are separate fields. Size rejection cannot
erase successful funding, and combined failures remain visible. Ambiguous
partitions, mixed funded/unfunded loci and order reversal are covered without a
hidden chooser. Lineage wording now explicitly states that a parent's endpoint
changes; the scalar W is transported to a successor edge, not retained on a
literally identical edge.

The focused source-status checker passes 13 cases, preserves all physical
outcomes/prescriptions and verifies 28 source bindings. It constructs no target
and runs no trajectory. Its record digest is
`e5e97877d2bfcc16607bfbc2c9469b6948be4fed9eb1f6f0e550544332c3793e`.
These are local semantic corrections, not a new physical campaign or additional
scientific gate. The checklist now marks independent successor mathematics,
typing corrections and the bounded obstruction/required-postulate derivation
complete, separately from still-open scientific adoption and generic coverage.

Keep the lineage-preserving candidate. The next substantive decision is the
scientific status/domain of exact persistent response-sector to site promotion,
followed by its activation/authority/debt proposal if selected. No generic
perturbation tolerance is introduced: this is a symmetry-sector candidate,
not a generic self-fission law. A future invariant quotient/equivalence requires
its own justification and is not a prerequisite for the bounded mathematical
PASS. ATC-2, native authority and formal claim/debt/capability dispositions remain
open or unchanged. No production, paper/specification or commit change is made.

## ATC CAN-LSF: bounded constitutive recommendation and proposed authority

The user authorized the next scientific step after the lineage/status review.
The [CAN-LSF proposal](./decisions/ATCSectorConstitutiveProposal.md) recommends
selecting the localized exact response-sector-to-site principle as a bounded
new law. Its justification combines persistent source distinction, occupied
unsplit obstruction, operation-compatible surgery, prior source resolution and
the reviewed causal contrast. These support a defensible explicit extension,
not uniqueness, derivation from ordinary V4 or empirical universality.

This is not another target/refinement test. The proposal identifies the physical
choice, distinguishes pressure from restored-target scope, retains both-role
edge-lineage transport, and states h0=1/8 as a fixed ordinary-scheme restriction.
That restriction must be bound before future ordinary execution, not introduced
as an event-time dependence on requested duration. The exact zero-channel map
also yields an algebraic positive-resource-scaling corollary: the source ratio,
partition, W and contraction factor stay fixed while resources, target center
and positive return radius scale together. This is newly derived for review,
not relabeled as independently executed evidence or generic perturbation scope.

The staged companion contains six proposed claim handles, reciprocal local
links to all 28 origin-debt assessments, an unchanged 35-claim/165-link origin
projection and ten explicit family dispositions. Native CAN-LSF is unsupported
in every family; only the reduced research A_OS slice has the reviewed positive
mathematical witness. Classical CAN-B obligations are retained as a different
route; response-to-surgery DB-08 and actual-restoration DB-19 are not evaded.
No original debt is discharged, and the 30-cell capability/composition program
is not weakened by this bounded recommendation.

Current source observation is `current_bundle_exact`. Six fresh typed contract
queries retain five historical `indeterminate_requires_review` dispositions and
the bounded initializer's `required` support. The new claim handle fails closed
as absent from the admitted graph. Source/edge references and trace digests are
retained; no graph, adapter, accepted source or profile registry is changed.
Reviewed numerical/status certificates and their source bindings are verified
without rerunning a physical campaign. No new target or trajectory is produced.

The current review subject is the principle plus its proposed domain/authority
surface, not another prettier target. Scientific acceptance, scoped ATC-3
adjudication/readmission, remaining ATC-2 capabilities and downstream propagation
remain separate. No acceptance, commit, implementation permission or ATC-2
closure is implied by preparing this proposal.

## CAN-LSF scoped scientific acceptance; first Read-Back lift results

The supplied constitutive review accepts CAN-LSF as a bounded new research law
and passes positive scaling analytically. The user requests scoped claim/debt
adjudication followed by the first two Read-Back lifts, with a second
adjudication only after review of that new work. The
[acceptance addendum](./decisions/ATCSectorConstitutiveAcceptance.md) and
[machine adjudication](./evidence/autonomous-topology-change/ATCSectorConstitutiveAdjudication.json)
record six accepted local research decisions and partial treatment of all 28
origin debts. Original 35 claims/165 links and reviewed proposal/certificate
bytes remain unchanged. No original debt is blanket-discharged; no forensic
node or production authority is added. Source readmission remains open.

The acceptance defines persistence by the exact invariant sector manifold,
not a temporal operand, and makes deterministic prospective generation
explicitly conditional on subsequent target admission. It retains the
zero-feedback fixed-step anchor/scaling ceiling, prepared histories and exact
symmetry. The reviewer did not independently execute the status adapter;
its thirteen checks retain their prior local attribution.

The [Read-Back proposal](./decisions/ATCSectorReadBackLiftProposal.md) specifies
the fixed enabled point and compact positive box before its focused check.
The [results](./decisions/ATCSectorReadBackLiftResults.md) distinguish exact
rational inequalities from 96-digit Decimal observations. Actual Read-Back,
generated geometry consumption and gamma-dependent writing are nonzero;
the original reference-stage selector gives k=30779. Both independently mapped
target roles enter the return region. Enabled no-split/reset-only controls
fail through resources at attempts 10/7, not OS tolerance. No target search or
physical parameter/allocator changes occur. A development exact-Decimal-charge
assertion was corrected to the declared diagnostic arithmetic scope.

The analytic target estimate gives q<=9209/10240<0.9 uniformly across the
proposed box, conditional on charge/history/resource-domain entry. This is
substantive nonzero-feedback progress, not complete-box causal closure: source
obstruction and actual both-role entry still need certified uniform treatment,
including possible dyadic-boundary crossings. The finite point is not a
rounding-certified proof. New work is pending review; no second adjudication
or enlargement of the first acceptance has occurred. Next close those causal
implications, not another partition or target. Native/other-family/formation,
ATC-2 capability/composition and final propagation remain separate/open.
## CAN-LSF qualified lift review and point-first outward certificate

The supplied [review](./evidence/autonomous-topology-change/review/CAN-LSF-ReadBack-Qualified-Pass.md)
independently reruns the predecessor's mathematical core with neutral helpers,
verifies its identities and passes the uniform conditional target theorem.
It explicitly keeps the finite source/entry evidence diagnostic and holds
nonzero scope acceptance and the second claim/debt adjudication. Preserve
the reviewed checker, proposal, record and zero-channel acceptance unchanged.
The old/source spectral guard margin is not a full-feedback eigenvalue;
distance from a tie needs enclosure before it supplies pointwise certainty.

The review's point-first continuation is implemented in the
[new certification note](./decisions/ATCSectorReadBackPointCertification.md).
Exact outward dyadic intervals, rational alternating-series exponential bounds,
integer square-root bounds and positive-pivot interval elimination certify
the fixed enabled point. No Decimal/libm transcendental result selects a sign
or rounding bin. The initial beat passes; source conditions, funding and the
unique k=30779 are enclosed. All preceding no-split/reset-only beats pass and
the first negative resource proposals occur at attempts 10/7 with OS residuals
still admitted. Failed proposals are not advanced or history-written.

Both actual roles' first target states enter the reviewed positive-return
domain. Its analytic q=9209/10240 theorem therefore supplies their infinite
continuation, without a long trajectory campaign. Exact source-sector
equalities use structural equivariance, not interval overlap or a tolerance.
This certifies the prepared point's chain, not every guard-positive source,
the complete parameter box or native execution. The certificate itself is
new and pending independent review; no second adjudication is performed.

Next review this point proof, then attempt the original box's source/entry
implications over all reachable dyadic bins. Do not narrow the box to keep one
k, tune the target or replace the reference-stage source consumer. Source
readmission, formation, native authority, other families and aggregate ATC-2
remain unchanged/open. No production, paper/specification or commit changes.
## CAN-LSF point PASS, second scoped adjudication and original-box successor

The supplied [point review](./evidence/autonomous-topology-change/review/CAN-LSF-ReadBack-Point-Pass.md)
independently executes kernel/symmetry/evidence, verifies reviewed identities
and pressure-tests nonzero exponential arguments. It does not execute the
repository wrapper. The fixed enabled point's source, unique bin, obstruction,
both-role entry and infinite restoration now pass as mathematics, not merely
Decimal observations. The old spectral guard remains an old/source guard;
no general full-feedback instability implication is inferred.

Under the user's review-then-adjudicate instruction, the
[second decision](./decisions/ATCSectorReadBackPointAdjudication.md) accepts
six local mathematical/scope claims, with all 28 origin debts carried forward
beyond earned portions. It accepts the enabled point plus the already-reviewed
conditional target theorem, not the whole parameter-box source/entry chain.
The first decision, 35 origin claims/165 links and all reviewed evidence remain
unchanged. Graph/source readmission and native authority are not promoted.

The next pressure addresses the original box directly. The
[new box certificate](./decisions/ATCSectorReadBackBoxCertification.md) uses
exact paired-source coordinates with outward enclosures, not sampled corners.
All source conditions, funding and both enabled counterfactuals are certified
across the unchanged box; resource rejections remain at attempts 10/7.
The initial single-hull target estimate was too wide to decide entry, not a
physical counterexample. Eight universal share-proof cells cover every integer
in the conservative 30378–31236 output hull. All cells pass both actual roles;
the maximal target squared-distance upper bound is below 0.377<4/9.
Every actual source still prescribes one target. No parameter shrinking,
target scoring/selection, partition or stage change occurred.

The reviewed infinite-tail theorem therefore completes the proposed whole-box
causal chain. Uniform nonvacuity is bounded analytically, not inferred merely
from positive parameter declarations. Five deterministic nonzero exponential
probes compare the unchanged kernel with independent rational positive-series
reciprocal brackets and all pass. This hardens evidence, not scientific debt.

This new box result requires independent review before further scientific
scope or claim/debt enlargement. It is not retroactively included in the point
review/second adjudication. Formation, other families, generic guard sufficiency,
native/source admission and aggregate ATC-2 remain open. No production,
paper/specification or commit changes are made.

## CAN-LSF original-box acceptance and G1–G4 state/environment results

The user's supplied box PASS independently reproduced the mathematical box,
kernel-hardening and reduced-algebra components, not the repository wrapper.
The [third scoped adjudication](./decisions/ATCSectorReadBackBoxAdjudication.md)
accepts the whole original feedback box for the fixed prepared source family.
Six local successor claims and all 28 retained debts distinguish that scope
from arbitrary states, resets, native admission and other families. Prior
certificates/adjudications and their historical pending fields remain unchanged.

The requested [G1–G4 successor](./decisions/ATCSectorStateDomain.md) provides
new research mathematics, separately pending review. G1 gives a full-dimensional
sufficient event-state region and independent reset region. G2 proves uniform
full-feedback growth x+>=(51/50)x on a source cone, excluding indefinite
unsplit nonnegative continuation without a prepared trajectory. G3 defines
exact decorated-automorphism sectors and proves staged covariance; bare
equitable pooling is not promoted to nonlinear closure.

G4 supplies a positive genuinely coupled environmental class: two external
pendants on one sector, with external reference current uniformly above 1.18.
All declared source states/feedback tuples reject unsplit and history-reset-only
resource proposals at attempt six. Independently transported actual roles
enter the whole eight-vertex target's return domain. Exact rational spectral
pivots cover all mean-zero modes, with full-feedback contraction below 49/50.
A shared-parent environment retains a Rayleigh obstruction 26/5>19/4 and is
explicitly excluded. This is not arbitrary-environment closure or repeated
autonomous operation.

The new exact checker verifies the analytic inequalities, quotient matrix
identities, spectrum and finite source enclosures. A hand-expansion sign error
was caught by matrix comparison; interval wrapping was resolved by an exact
polynomial quotient, not domain/target selection. No old numerical campaign
or production tests were rerun. G5 remains a substantive next problem:
positive alpha changes the history equilibrium and beta needs a descriptor
binding. G6 requires a consistent changed-step writer; G7 requires the
reviewed claims → proposal → paper → specification authority chain. Plans,
checklists, indexes and handoff retain these limits. No src, tests, specs,
paper, forensic graph, commit or aggregate ATC-2 changes.

## CAN-LSF G1–G4 PASS and fourth scoped adjudication

The supplied [G1–G4 review](./evidence/autonomous-topology-change/review/CAN-LSF-G1-G4-Pass.md)
independently reproduces the whole certificate evidence payload, checks the
reviewed identities and analytically passes G3's equivariance argument.
It does not report executing the repository wrapper or native ATC code.

The [fourth adjudication](./decisions/ATCSectorStateDomainAdjudication.md)
accepts six local bounded mathematical/scope claims, with reciprocal links
and all 28 wider debts retained. The gain is substantive: G2 establishes
predictive full-feedback source obstruction on its cone, and G4 supplies
active environmental coupling with whole-target restoration. Nevertheless
G1's four-dimensional interior is inside the exact paired quotient manifold;
G3 is a definition/equivariance theorem, not arbitrary-orbit fission authority;
G4 supports one declared environmental class. The second-parent exclusion,
independent reset conditions and all other limitations remain intact.

This successor leaves the narrower prepared-family adjudication and every
reviewed checker/note/certificate byte unchanged, including historical pending
fields. Validation checks identities, reciprocal claim/debt references and
portable paths/links without repeating the reviewed mathematical campaign.
Plans, checklists, indexes and the current handoff now record acceptance and
G5 as next: descriptor/reference binding, shifted alpha equilibrium and the
potential class. G6 and G7 remain separate; no new G5–G7 result, native or
forensic graph admission, other-family support, formation claim, aggregate
ATC-2/ATC-3 closure, paper/specification change or commit is made here.

## CAN-LSF G5–G6 mathematical successor and G7 readiness

The requested [G5–G6 investigation](./decisions/ATCSectorChannelsAndRequests.md)
now supplies bounded positive results without changing any reviewed predecessor.
G5 binds one-dimensional unit-reference-weight WLS descriptors with positive
regularization and explicit child-position inheritance. Both alpha/beta are
genuinely active at the source; their full read/writer operands are consumed.
The potential class is C¹ with |p'-19/4|<=1/2048 on [0,9], including a strictly
nonlinear quadratic subclass. Source-only event balance uses the actual
potential, not the old affine surrogate. The target history limit becomes
exp(-alpha c), while the resource return factors remain below 9/10 and 49/50.

G6 then admits every requested h in [3/25,1/8] with tau fixed at 1/(8 log 2),
including varying request sequences without a subdivision-invariance claim.
Paired-source growth is bounded below by 61/60. Embedded unsplit/history-reset-only
controls fail by attempt ten (G5: seven); these are upper horizons, not common
exact failure times. The finite enclosure conditions on nonnegative survivors
when interval wrapping loses a sign: rejected trajectories are not advanced
or written, and interval intersections are not a physical resource clamp.
The final G6 rejection is an empty intersection of exact resource descriptions.
The shared-parent environmental counterexample remains excluded.

One new mathematical certificate checks analytic bounds, descriptor identities,
full mean-zero rational spectral pivots, true h-dependent writer decay and
the finite embedded enclosures. Focused native readiness checks additionally
compare four differential references and two log-writer requests with
independent exact-input oracles. Together, the checks distinguish stale writer
descriptors / a wrongly retained half-decay writer. The near-lower-endpoint
native request is the next binary64 value above 3/25, not the slightly
out-of-domain binary64 spelling 0.12. Represented tau is recorded separately
from the theorem's exact transcendental parameter.

G7 is not completed: source inspection still finds only the zero-derivative
site-potential declaration in the production current. Primitive agreement
does not supply native ATC, a profile/owner, numerical error closure or a
lifecycle test. Independent G5–G6 review and bounded claim/debt adjudication
are next, then the topology proposal → extension paper → specification route
before native implementation. All 28 wider debts, intake claims, earlier
adjudications, formation/other-family obligations and ATC-2/ATC-3 status stay
unchanged. Plans, checklist, indexes and handoff now state that boundary.
No src/runtime tests/specification/paper/gates or commits are changed.

## CAN-LSF G5–G6 acceptance and investigation-local G7-R

The supplied [G5–G6 PASS](./evidence/autonomous-topology-change/review/CAN-LSF-G5-G6-Pass.md)
independently reproduces the mathematical evidence and reconstructs the
captured native primitive outputs, but does not execute pygrc or repository
wrappers. The [fifth adjudication](./decisions/ATCSectorChannelsAdjudication.md)
accepts exactly the bounded G5–G6 mathematics, with six local claims/all 28
wider debts retained. Earlier scopes and every reviewed byte stay unchanged.

The user explicitly authorized G7 research without src changes. The
[G7-R package](./decisions/ATCSectorReferenceConformance.md) therefore builds
the full nonlinear A_OS law inside the investigation. It uses full incidence
equations and an independent edge-local Decimal oracle, not merely another
trajectory of the accepted paired reduction. Eight point cases compare
1,116 scalar stage values, with explicit stale-descriptor and wrong-stage
writer discrimination. The paired/embedded inputs select source dyadic bins
32775/31897; both roles preserve old-edge history and seed only the bridge.

The small local owner checks independent reset readmission before publication,
invalid lineage/profile/history even with recomputed digests, injected late
failure, invalid requests, ambiguous quantization, retained-state mutation,
and full split/step/reset replay. Ordinary unsplit/reset-history controls reject
through resources at 9/8 attempts (paired) and 6/6 (embedded), with complete
publication rollback and no writer or event fallback on a failed proposal.

Four sixteen-step runs compare exact enclosures with a declared publication-only
binary64 recipe, represented h and fixed represented tau. Maximum resource/
history errors stay below 4.1e-16/8.3e-17. Independent publication rounding
produces charge drift up to about 2e-15; the record preserves it rather than
silently balancing resources. These are finite represented-error bounds, not
the production staged-arithmetic recipe, exact native conservation or an
infinite binary64 theorem. A native numerical/conservation policy remains
substantive work, not an administrative check.

G7-R now awaits independent review and a separate scoped adjudication. G7-N
still needs native potential/profile/owner and public lifecycle admission
after reviewed claims → topology proposal → extension paper → specification.
The local owner is not K0, and formation/repeated autonomous operation,
other families, arbitrary environments and aggregate ATC-2/ATC-3 stay open.
No production code, runtime tests, paper, specs, gates or commit changed.

## CAN-LSF G7 acceptance and completion of bounded A_OS G1–G7

The [G7 review](./evidence/autonomous-topology-change/review/CAN-LSF-G7-Pass.md)
passes the full-graph executable law, independent stages, source-only
selection, both-role transfer/readmission, lineage/reset, atomicity, replay,
negative pressure, variable requests and finite represented-error bridge.
The reviewer reruns eight point rows (1,116 scalars), four source controls,
both graph lifecycle suites, extra h=3/25 request pressure and both
current-role continuations. The two reset-role continuations remain retained
author-run evidence; no main-wrapper or native rerun is attributed to the review.

The user explicitly corrects the review's proposed G7-R/G7-N split.
For this investigation **G7 is the research reference/conformance task**:
**G7: PASS; bounded A_OS G1–G7 research program: PASS**. The
[sixth scoped adjudication](./decisions/ATCSectorReferenceAdjudication.md)
and [record](./evidence/autonomous-topology-change/ATCSectorReferenceAdjudication.json)
accept six bounded local claims and retain all 28 wider debts without
turning them into unmet criteria on the completed research program.
All reviewed artifacts and prior dispositions remain byte-identical; this
entry and the successor adjudication supersede the earlier current-status
recommendation above, not the evidence itself.

The accepted charge-drift finding identifies a later production numerical
policy requirement, not a G7 defect. Starting at admitted event-state
preimages rather than implementing K0 scheduling is within the bounded
task. Native implementation follows reviewed results → topology proposal →
extension paper → specification → Phase 9; it is not an open G7-N half.
The acceptance addendum also clarifies that PROFILE_ID binds evaluator
operands, while source/checker hashes and the outer conformance record
additionally bind event/lifecycle semantics.

The next scientific decision is to use completed A_OS as the reference
template for other Candidate-A realizations, starting with an A_CI-specific
implicit-closure study. No such lift starts in this adjudication. Other
realizations, wider formation/composition and aggregate ATC-2/ATC-3 remain
open. No production code, runtime tests, paper/specifications, native gates
or commits are changed.

## Pre-commit relocation of the ATC research evidence

The user authorized relocating the uncommitted chain before its separate
claim/debt ledger reconciliation. Forty-two top-level JSON records and
nineteen review/input files moved from `drafts/autonomous-topology-change/`
to [evidence/autonomous-topology-change/](./evidence/autonomous-topology-change/README.md).
The current research/review navigation moved with them. Committed ATC-1,
source-intake, origin-index, location-map and manuscript subjects remain at
their existing paths with unchanged bytes; their READMEs link to the new index.

Repository-relative references, quoted source identities, canonical record
digests and predecessor pins were rebuilt in dependency order. Sorted source
rosters retain their generator ordering. This maintenance does not change
scientific payloads, numerical outputs, accepted scopes, claim/debt
dispositions or review verdicts. Migrated reviews disclose the identity update;
it is not attributed to a new independent execution. No new forensic admission,
native implementation authority, aggregate closure or commit follows.

Validation compared the pre-move scientific payloads and Python syntax with
the relocated subjects, checked every migrated record digest/source binding
and local link, and confirmed committed subjects unchanged. G1–G4, G5–G6 and
G7 wrappers reconstructed their records using retained evidence only (not new
numerical runs). The thirteen-case source-status checker and thirteen-group
compact ATC-2 review reproducer passed; the admitted forensic context still
rebuilds unchanged. Full numerical campaigns were not repeated.

## A_OS research checkpoint — relocation and ledger admission

The user authorized the remaining relocation, scoped ledger reconciliation
and checkpoint commit. All ATC evidence, including the complete review tree,
now resides in `evidence/autonomous-topology-change`; drafts contains only
the two unchanged manuscripts and navigation. Remaining ATC-1 subjects were
relocated with dependent paths/hashes rebuilt; their original committed bytes
remain in Git. No scientific payload or historical verdict was rewritten.

The [successor reconciliation](./decisions/ATCAOSClaimDebtReconciliation.md)
and machine ledger admit 36 bounded A_OS research claims, preserve 35 proposed
origins, and adjudicate all 28 debts locally: 13 closed, 6 partial, 9 not
activated. Global origin debts remain open. DB-11 batch equivalence and
DB-22 repeated-event/non-Zeno obligations are not discharged by single-event
replay. DB-24 closes locally through the actual pinned research admission.
A_OS G1–G7 remains accepted; aggregate ATC-2 remains open. Native ATC, other
families and paper/spec propagation are not authorized by this checkpoint.

The explicit ATC API/CLI admits an append-only graph while preserving every
pre-ATC node, edge and annotation. Ten focused tests pass, including all
claim/debt queries, lineage, proposal ceilings, source drift, manifest pins
and command dispatch. The admission checks 78 evidence subjects and 325
support bindings. All 60 pre-existing JSON subjects match their pre-move
scientific payloads after path/identity substitution. Manuscripts remain
byte-identical; relocated Python parses; local document links and portable
paths were checked. ATC-1's eleven review groups and bundle manifest pass;
ATC-2's thirteen compact review groups pass (one locally byte-matched
execution source, not a new native rerun). The thirteen-case status checker
reproduces its retained record. G1–G4, G5–G6 and G7 wrappers reconstruct
their exact records using retained numerical evidence, not new numerical
campaigns. No `src/`, production tests, paper or specification was changed.

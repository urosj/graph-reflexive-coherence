# GRC9V4 Constitutive Design Decision Ledger

**Status:** D0-D4 accepted bounded; D5 authorized and not started

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
enabled, and array order preserved. `decision_record_digest` is the SHA-256 of
those canonical bytes. A prose-only record cannot receive an accepted digest
unless an equivalent structured decision object is frozen with it.

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

Status: authorized by accepted D4; not started.

## D6. Total-Current Closure

Status: blocked on D5.

## D7. Closed Write/Read Loop

Status: blocked on D6.

## D8. Continuation Realization And Analysis Contract

Status: blocked on D7.

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

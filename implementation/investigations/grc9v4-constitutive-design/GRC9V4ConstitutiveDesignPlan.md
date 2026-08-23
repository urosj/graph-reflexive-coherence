# GRC9V4 Constitutive Design Investigation Plan

**Date:** 2026-08-23  
**Status:** Initialized; D0 not yet executed  
**Design basis:** [`GRC9V4ConstitutiveDesignBasis.md`](./GRC9V4ConstitutiveDesignBasis.md)  
**Checklist:** [`GRC9V4ConstitutiveDesignChecklist.md`](./GRC9V4ConstitutiveDesignChecklist.md)  
**Decision ledger:** [`GRC9V4ConstitutiveDesignDecisionLedger.md`](./GRC9V4ConstitutiveDesignDecisionLedger.md)
**Initialization:** [`GRC9V4ConstitutiveDesignInitialization.json`](./GRC9V4ConstitutiveDesignInitialization.json)

## Purpose

Resolve the constitutive decisions required before a revision-distinct GRC9V4
specification can be written. The plan is an investigation, not a runtime
implementation tranche and not a normative specification.

## Execution Rules

- Execute D0-D10 serially; a later gate consumes accepted earlier decisions,
  except for the explicit early terminal route to bounded D10 closeout.
- Keep theory inheritance, graph derivation, candidate completion, runtime
  evidence, and design preference separately labeled.
- Treat the B1 contract and B1/B2 experiments as historical decision lineage
  and bounded evidence, never as a literal V4 architecture template.
- Compare all admitted architectures under the same gate criteria.
- Preserve `current_candidate_set_exhausted` as a valid route to named theory,
  constitutive, candidate-admission, or discriminator work.
- Do not modify `src/`, existing runtime tests, or normative GRC specifications.
- Analysis prototypes may be used only if they are clearly non-constitutive and
  cannot mutate source-current runtime state.
- A convenient field layout or numerical result cannot decide ontology.
- Frozen response, replay, or persistence cannot substitute for dynamic joint
  continuation.
- Endpoint evidence does not establish the retained/read/write crossing.
- Every gate records assumptions, alternatives, rejected mappings, debt, and
  exact authorization effect in the decision ledger.
- Accepted records are immutable. Reopening a gate appends a successor record
  with predecessor and supersession digests rather than editing accepted text.
- D1 admits or rejects candidate ontologies; it does not select the final V4
  architecture.
- Independent current temporalization is an orthogonal D6 decision, not a D1
  retained-representation candidate.
- Human acceptance is required before advancing each design gate.

## Gate Outcomes

Each gate closes as one of:

```text
accepted
accepted_bounded
blocked_missing_theory
blocked_missing_discriminator
rejected_all_candidates
superseded_by_revised_gate
```

`accepted` opens the next gate. `accepted_bounded` opens only the scope not
blocked by its typed debts. `rejected_all_candidates`,
`blocked_missing_theory`, and `blocked_missing_discriminator` may route directly
to bounded D10 closeout instead of forcing irrelevant gates to execute. A
blocked gate may also be superseded by a named revised gate. D10 alone may set
`specification_authorized = true`.

`rejected_all_candidates` means `current_candidate_set_exhausted`: none of the
presently admitted candidates closes the frozen target. It does not reject
GRC9V4 and cannot authorize a no-V4 conclusion.

Every `accepted_bounded` debt must record:

```text
debt_id
blocking_scope
candidate_scope
assumption_forbidden_downstream
resolution_gate
must_close_before_D10
```

## D0. Target, Inheritance, And Claim Ceiling

Consume the frozen initialization record with predecessor digest
`7daf0693e2603b8e0c7062c77789a4ae71b6372b5605e31024be304a282e2654`.

Freeze the exact source identities and classify every inherited statement as:

```text
core_inherited
core_derived
candidate_constitutive_completion
substrate_requirement
legacy_substrate_exact
bounded_evidence
open
```

Record the target, non-targets, architecture-neutral vocabulary, and claim
ceiling. Confirm that 3.4.1 is a design constraint and verification source, not
the V4 implementation specification.

Build a historical-consumption matrix for the B1 verification specification,
B1 accepted gate/closeout artifacts, B2 constructibility protocol, and B2
accepted classification/handoff. For each source, freeze:

```text
historical_role
exact_or_bounded_claims_consumed
source_envelope
may_consume_as
must_not_consume_as
open_debt_carried_forward
```

The matrix must preserve B2's bounded-empty-search semantics: it may motivate a
revision-distinct investigation but cannot select a retained representation or
establish global unchanged-runtime impossibility.

Audit every B1-derived theory statement against the current core revision and
classify it as unchanged, narrowed, broadened, superseded, historical-only, or
requiring rederivation. Current core controls theory; B1 retains measurement
and historical authority only within its accepted envelope.

Before D1, also freeze:

- the complete candidate-admission set, source rule, and admission deadline;
- the design/verification topology envelope separately from the normative
  runtime capability scope;
- topology-event transport/accounting, explicit capability disablement, or
  event-boundary behavior, with any deferred full-runtime duty recorded as
  `must_close_before_D10`;
- the candidate-neutral disabled-retention/read GRC9V3 reference transition,
  required equivalence surfaces, allowed exact/projected/tolerance semantics,
  added-state initialization requirements, serialization rules, and lifecycle
  comparison requirements;
- the requirement that every D1 candidate construct `i_a`, `pi_a`, disabled
  added-state initialization, and reduction obligations without claiming a
  completed-transition witness before D7/D9; and
- the hard-veto requirements separately from selection preferences.

## D1. Retained-Representation Ontology And Candidate Admission

Compare temporalized `W`, a separate independent retained carrier with an
RC-derived update law, a constitutively retained sector of `C`, and any
additional D0-admitted structural representation. Determine what object may
satisfy the retention contract without becoming a new core primitive or an
analysis-only relabel.

Required outputs:

- causal type and ownership;
- state authority: independent state, derived constitutive representation,
  reconstructed view, or observer only;
- resource accounting: independent resource, projected existing resource,
  nonresource structural information, or no resource role;
- transport roles: a set containing `conditions_geometry`,
  `conditions_mobility`, and/or `direct_transport_parameter`, with the empty set
  meaning none;
- formation inputs;
- complete-step causal authority, whether derived or independently serialized;
- relation to `C`, `W`, `J`, topology, and lifecycle state;
- elimination/reconstruction test;
- candidate reduction embedding and projection;
- added-state disabled initialization;
- `candidate_reduction_construction_status`, reduction obligations, and
  structural blockers;
- representation selector, inputs, constitutive authority, statefulness,
  sector identity/transport, and hidden-history/future-information audit for
  every derived constitutive representation;
- hidden-state audit;
- `admitted_candidate_set` and `rejected_on_ontology`; and
- `sole_surviving_candidate`, if applicable, without final selection.

If the admitted set is empty, record `current_candidate_set_exhausted`, the
localized missing role, required derivation or revised admission work, and the
gate at which investigation can resume.

Current slaving/deslavement is out of scope until D6.
An observer-selected sector discovered from later trajectory behavior is
rejected as a runtime retained representation.
Any selector state that depends on its own history is explicit serialized
causal state; otherwise the selector must be deterministic from current
declared causal state.

## D2. Formation, Retention, Release, And Write Interface

Define candidate formation, retention, release/reconfiguration, transfer, and
write-interface semantics. Reject a recomputed proxy with no historical causal
content, an indefinite accumulator, or an arbitrary slow cache without
constitutive authority. Do not reject a `C`-derived representation merely
because it is derived if it is historically formed and later load-bearing.

Freeze conservation/budget treatment, update ownership,
`no_forming_or_write_input` behavior,
the distinction between driver persistence and retained-state persistence, and
the admissible inputs to the future write law. For every candidate, decide
how its authority, accounting, and transport classifications interact.

Name this control `no_forming_or_write_input`; it tests retention/release after
the forming or write driver is absent and is not the Read-Back passive null.

For `V4-C-constitutive-C-sector`, require a recoverable factorization between
ordinary `C` update, activity-induced retained-sector occupation/change, and
the later retained-conditioned read effect. Generic `C` continuity is not
retained write-back.

## D3. Continuation Requirements And Structural Domain

Define formed structural state, formed branch, reference transport, admitted
perturbation state, clock, and the requirements a later complete transition
must satisfy. Specify how ordinary branch displacement, fast temporal
relaxation, and retained structural continuation are distinguished.

For each admitted candidate, decide where structural continuation lives while
reserving `F` for the runtime transition, `F_struct` for a structural
functional, `P_M`/`P_slow` for projectors, and `pi_a` for reduction projections:

```text
C-only: H_C is derived from F_struct(C)
conditional C structure: H_C_given_T is derived from F_struct(C; T_*) while delta_T
  is not a continuation coordinate
joint structure: H_(C,T) is derived from a source-backed F_struct(C,T)
candidate blocked pending new theory
```

Do not derive a joint continuation Hessian from runtime `DF(C,T)`. Freeze the
distinct roles of structural `alpha`, temporal `gamma` or map multipliers,
Read-Back `beta`, and spatial `lambda`. Explicitly block:

```text
slow_temporal_mode == low_continuation_stiffness
```

Build a support matrix over no-current, frozen-current, smoothly slaved-current,
and independently active-current references. For each row, record supported,
conditionally supported, theory-open, or blocked status; conditions; the
elimination/freezing rule; whether current would be a structural coordinate;
and active-joint-continuation theory status. D3 does not choose the runtime
regime. D6 selects closure and D8 consumes the corresponding row. Do not inherit
a self-adjoint Hessian for active `(C,T,J)` without a source-backed derivation.

For every derived representation, freeze the tangent constraint relating
`delta_T_M` to perturbations of its declared causal inputs. Independent
`delta_T_M` is blocked unless D1 admitted independent state authority.

Keep topology/event strata explicit. D3 freezes requirements, not the final
operator of a loop that has not yet been closed.

## D4. Geometry, Mobility, And Topology Ownership

Decide whether each retained representation is geometry, conditions geometry,
or remains a separate structural carrier. Define its relation to scalar `W`,
analytic edge labels, node tensors, constitutive/induced geometry `h`, the
geometry-inducing or constitutive object `K`, any separately realized mobility
operator `M` or `A`, topology, and basin hierarchy.

Prevent one field from silently serving as retained structure, mobility,
directional current, and analysis projector. Do not preassign `K` as transport
mobility. Apply both topology scopes and the event transport/accounting boundary
frozen in D0.

## D5. Directional Read-Back

Define the graph-native retained-conditioned current map, passive null,
edge-coordinate orientation covariance, physical present-current reversal
response, retained-representation orientation/chirality content,
present-current convention, retained-state counterfactual, rival-carrier
controls, and output cochain space.

Name the passive-null control `zero_present_current`. Separately record the
direct `T_M -> h/W/mobility -> J0` path, the `(T_M,J_C) -> j` Read-Back path,
and any overlap/double-count risk. Where structurally possible, read-off must
disable `j` while preserving the direct retained-conditioned `J0` path.

Separate `J0`, `j`, and total `J_C`. Reject scalar/label/proxy relabels.

## D6. Total-Current Closure

Define regular algebraic slaving, the full effective loop block, solve order,
uniqueness/invertibility, failure semantics, and deslavement trigger.

For every surviving representation candidate, decide the orthogonal axis:

```text
J slaved within the beat
J independently temporalized under an explicit trigger
candidate blocked because neither closure is admissible
```

Current temporalization is admitted only if regular closure fails under that
candidate or a separately declared target requires independent current
dynamics.

The closure record must preserve the direct-retained-to-`J0` and Read-Back-to-
`j` decomposition through total-current formation and reject double counting.

## D7. Closed Write/Read Loop

Close and attribute the architecture-neutral dependency:

```text
T_M,k
  -> j_k
  -> J_C,k
  -> declared downstream state consequence
  -> T_M,k+1
```

Define passive, frozen-carrier, write-off, read-off, rival-carrier, reversed
orientation, and loop-open controls. Select the exact write inputs from the D2
admissible set and define the complete effective transition. Specify formation,
retention, reconfiguration, and the later stability questions without promoting
a one-way path to a closed loop or requiring `C_(k+1)` as the sole mediator
without evidence.

For a constitutive `C` sector, preserve the D2 factorization and prove that the
write/read arrows are not ordinary `C` evolution under new names.

At D7, freeze formed-loop conditions, admissibility and singular/invalid
boundaries, reconfiguration triggers, and the questions D8 must answer. Defer
structural and temporal stability classification to D8.

## D8. Continuation Realization And Analysis Contract

Analyze the completed D7 transition while keeping four objects separate:

```text
structural functional/Hessian H_*       -> alpha_n
temporal generator or effective DF_*    -> gamma_n or multipliers mu_n
Read-Back derivative D_J R_*            -> beta_n
spatial graph operator -Delta_h         -> lambda_n
```

Define spectrum, cluster/subspace, projector transport, basis and symmetry
covariance, non-normality, and static-versus-dynamic comparison contracts. Keep
analysis projectors out of runtime state unless an earlier gate independently
admitted the same representation for constitutive reasons.

For every operator/projector, record its domain, admissible tangent space,
inner product or weight, physical and reduced/self-adjoint representations,
representation map, projector pullback/pushforward, moving-space
identification, and cluster conditioning. An analysis-coordinate projector
cannot be consumed on physical runtime coordinates without the declared
conjugation and transport.

For a derived retained representation, the admitted tangent space must enforce
the D3 derivative constraint. A joint analysis may not manufacture an
independent retained direction absent D1 independent-state authority.

No temporal slow mode, spatial Hessian, graph Laplacian eigenvalue,
Read-Back response, or frozen-carrier response may be relabeled as low
structural continuation stiffness. Compare them only under declared mappings
and assumptions.

## D9. Complete Step And Lifecycle Contract

Freeze candidate complete-step ordering, causal state, serialization,
restoration identity, reset baseline, RNG use, deterministic replay,
capabilities, profile identity, migration from GRC9V3, disabled behavior, and
test/telemetry/analysis ownership.

After D7 closes the candidate transition, verify the selected candidate's D1
embedding/projection construction on every declared equivalence surface. Freeze
the actual `pi_a o F_V4_a_disabled o i_a = F_V3` witness and its exact,
projected, or tolerance-bounded classifications as the lifecycle/migration
contract.
Enforce the normative topology capability decision: freeze
parent-to-child retained-representation transport, resource accounting, reset,
and replay semantics; explicitly disable topology-changing capabilities in a
fixed-topology subprofile; or freeze deterministic event-boundary termination
or reset. A fixed early verification envelope cannot discharge a full-runtime
topology debt.

No legacy GRC9V3 snapshot may be silently interpreted as containing retained
state it never serialized.

## D10. Design Synthesis And Spec-Writing Decision

Integrate all executed gates into one internally consistent architecture and
adjudicate every D10-blocking debt. D10 may be reached after D9 or by the early
terminal route from `rejected_all_candidates`, `blocked_missing_theory`, or
`blocked_missing_discriminator`.
Produce a source-backed closeout and one disposition:

```text
authorize_GRC9V4_specification
reopen_named_design_gate
route_to_named_theory_or_constitutive_derivation
close_current_design_tranche_unresolved
```

`authorize_GRC9V4_specification` requires a selected architecture, complete
causal loop, continuation contract, lifecycle contract, verification outline,
claim ceiling, and human acceptance. D10 does not itself write the normative
specification or authorize runtime implementation.

`close_current_design_tranche_unresolved` closes only this investigation
tranche. It must preserve the GRC9V4 target and identify the missing role,
reopening condition, and resume gate. Candidate exhaustion never supports a
conclusion that GRC9V4 should not be built.

## Expected Records

Each gate should add a separate decision record or a clearly delimited ledger
entry containing:

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

Accepted records are append-only. A revised gate creates a new record and names
the record it supersedes; accepted decision payloads are never rewritten. The
decision digest hashes the canonical gate record with
`decision_record_digest` omitted, using sorted-key compact ASCII-escaped UTF-8
JSON with array order preserved. The predecessor digest names the accepted
serial predecessor; `supersedes` names an earlier record of the same gate.

Numerical or prototype artifacts are optional and subordinate to the decision
record. They become load-bearing only when explicitly admitted and frozen.

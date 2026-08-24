# GRC9V4 Constitutive Design Investigation Plan

**Date:** 2026-08-23  
**Status:** D0-D2 accepted; D3 complete and awaiting human review
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
- From D4 onward, do not rerun B1/B2 merely to rediscover their bounded V3
  conclusions. Revisit an inherited distinction, control, or negative result
  when a V4 choice changes the causal object, state space, or operator to which
  it applied.
- Classify each B1/B2 item consumed by D4+ as `legacy_fact`,
  `verification_control`, `design_pressure`, or `open_hypothesis`. Only a
  `legacy_fact` is a hard historical premise, and only about frozen GRC9V3; no
  category dictates V4 ontology or equations.
- Every D4-D9 gate must add a candidate-specific constitutive fact, reject a
  candidate for a named incompatibility, or route a named missing derivation.
  Requirement-only prose is not a completed design gate.
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

D0 also freezes closure guardrails. The named candidate universe is exhaustive
only over the preregistered D1 families, not all possible V4 architectures.
Candidate families are investigation classifications and may be reclassified
without new admission only when their causal architecture is unchanged.
Source absence is classified as contradiction, undefined relation,
underdetermined completion, or new-theory requirement rather than treated as a
blanket prohibition.

The V3 reduction target must be audited against current runtime source, the
reconciled normative specification, and the historical B1/B2 evidence
revisions. Disabled-profile reduction requires an invariant legacy subspace
over repeated steps, external complete-step clock parity, and no hidden history
accumulation. It does not require identical internal solver staging.

Every later result must declare whether it belongs to the fixed verification
envelope, a fixed-topology normative subprofile, or a full-topology-capable V4.
Vetoes must be typed as claim-scope or architecture/gate blocking, and evidence
provenance must remain separate from constitutive design arguments.

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
  meaning none; D1 records provisional candidate signatures and D4 owns final
  confirmation, narrowing, or reclassification;
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
- five-way elimination/reconstruction classification, including finite-history
  reconstruction and independent variation under constraints;
- a candidate-specific historical-content rationale and native-consumer
  rationale;
- hidden producer/helper, administrative, scheduler, registry, and RNG
  dependence;
- state dimension, value-domain, information-capacity growth, and release or
  pruning obligations;
- candidate equivalence classes and pairwise causal-conjugacy audit;
- disabled-embedding multiplicity and obvious disabled-mode causal activity;
- candidate-local `established_in_D1`, `unresolved_but_permitted`,
  `must_be_proved_by_gate`, and `would_reject_if_failed` fields;
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

D1 rejects only ontological contradictions. Missing exact D2-D9 laws become
named obligations rather than premature D1 failures. Independent state requires
a possible counterfactual future difference, not serialization alone. A
derived update law does not imply that the current value is algebraically
derived from current state. Candidate equivalence requires a bijective causal
state transform preserving transition, outputs, accounting, transport, and
lifecycle; equal state dimension is insufficient.

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

Freeze initialization, `no_forming_or_write_input`, `write_off`,
`retained_state_frozen`, and administrative reset as distinct interventions.
Formation and post-input retention are separate causal arrows. Permit multiple
explicit retention mechanisms, but reject small rates and hidden external
maintenance as sufficient retention. Require some constitutive native release
or reconfiguration route distinct from administrative reset. Require smooth
fixed-topology release only when claimed; admit event-mediated release only
after D4/D9 define its causal, accounting, interspace, and lifecycle contract.

Classify every write input as `pre_solve`, `post_solve`, or
`post_state_update`. Flag any prospective same-beat algebraic cycle for D6/D7.
Freeze multiwrite composition, information-content, orientation-covariance, and
serialized-RNG obligations without selecting the eventual numerical law. For
order-sensitive composition, require deterministic recovery from declared
current causal state, input batch, and constitutive ordering, or serialize any
persistent order state.

Candidate-specific pressure requirements are load-bearing:

- A must separate instantaneous and retained write attribution, distinguish
  retained `W` from its persistent effect on `C`, and classify clipping,
  saturation, and normalization scope constitutively;
- B must be Markov-closed on declared state, bound information capacity, reject
  an EMA rate as sufficient structural justification, and prevent nonresource
  `T` from restoring depleted physical `C`;
- C must separate content change, projector motion, rank change, basis
  transport, and sector exit/re-entry before formation, release, or transfer
  labels are allowed.

Record capacity and lifetime as independent axes. Transfer may remain out of
scope for the initial profile, but copying, replication, resource transfer, and
topology interspace transport may not be conflated.

## D3. Continuation Requirements And Structural Domain

Define structural reference state, retained structural state, formed branch,
reference transport, admitted
perturbation state, clock, and the requirements a later complete transition
must satisfy. Specify how ordinary branch displacement, fast temporal
relaxation, and retained structural continuation are distinguished.

For each admitted candidate, decide where structural continuation lives while
reserving `F` for the runtime transition, `F_struct` for a structural
functional, `P_M`/`P_slow_analysis`/`P_slow_runtime` for projectors, and `pi_a`
for reduction projections:

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
Missing joint A/B or independently active-current structural theory remains a
claim-local, conditional debt while a valid conditional or reduced lane stays
open. If D6/D8 later selects a claim that needs the missing independent
structural coordinate, that gate must create a named D10-blocking successor
debt before the claim can proceed.

For every derived representation, freeze the tangent constraint relating
`delta_T_M` to perturbations of its declared causal inputs. Independent
`delta_T_M` is blocked unless D1 admitted independent state authority.

Keep topology/event strata explicit. D3 freezes requirements, not the final
operator of a loop that has not yet been closed.

Distinguish D2 `retained_formed` from D3 `structurally_formed`; neither implies
the other. A structural reference state need not have been produced by D2;
only the stronger retained-structural claim requires both contracts. Classify
candidate runtime viability separately from C-only, conditional, and joint
structural-claim viability. A retained carrier may condition a C-only spectrum
without owning an alpha spectrum of its own.

Freeze the functional normalization, perturbation metric, constraint scope,
symmetry/gauge null treatment, and fixed-geometry versus total induced-geometry
derivative convention before any alpha magnitude or zero mode is interpreted.
If retained state conditions the measure, include that response in the
conservation tangent without reclassifying nonresource state as resource.

Require the A `R_W` coupled tangent and the exact C selector tangent. Block
continuation-derived, analysis-only, or retrospectively selected temporal-slow
projectors from becoming constitutive by relabel. Preserve the conditional
route for a runtime-owned dynamic slow projector only under an executed
temporal law, declared clock/branch, isolation, causal runtime consumption,
and any required self-consistent projector fixed point. At active
inequality bounds, clipping, hard cutoffs, rank/mode crossings, and topology
events, use the appropriate tangent-cone, stratified, or event object rather
than reporting an undefined Hessian as `alpha = 0`.

Freeze branch gauge prospectively and block retrospective fitting to the
observed trajectory. Structural marginality must remain distinct from spark,
collapse, topology change, current deslavement, temporal lifetime, nonnormal
survival, and any specific finite basin.

## D4-D10. Verification-To-Design Inflection

D0-D3 establish the bridge from unchanged-runtime verification to a bounded V4
candidate set; D3 human acceptance still governs D4 authorization. These gates
do not need to rediscover the accepted B1/B2 boundary. Nor may that boundary
become a timeless V4 template. From D4 onward the governing question is no
longer only what a valid V4 would have to respect, but what constitutive
architecture each surviving candidate actually supplies.

The no-redo rule is:

```text
rerun whose only purpose is rediscovering a bounded V3 conclusion
  != new V4 constitutive fact

reconfirmed absence in unchanged GRC9V3
  != V4 design decision

inherited result applied to a changed V4 causal object/state/operator
  -> rederive, adapt, or retest under the new constitutive semantics

candidate-specific map, equation, ownership, solve order, or named rejection
  = admissible D4-D9 design output
```

B1/B2 provide bounded V3 facts, controls, design pressure, and hypotheses. Their
distinctions remain valuable until the selected V4 architecture changes the
object under test; then D4+ must state what is retained, revised, or replaced
and why. After a V4 specification and implementation are separately authorized,
applicable B1/B2 discriminators should be reused or adapted against the selected
V4 profile. They are not substitutes for selecting its constitutive equations.

## D4. Geometry, Mobility, And Topology Ownership

Produce a candidate-specific constitutive ownership record. For every surviving
candidate, identify the exact retained object, the owner of induced geometry
`h`, the owner of transport mobility `M` or `A`, the role of `K`, the role of
legacy scalar `W`, and the topology/basin relation. Supply the constitutive maps
between those objects rather than only listing possible roles.

At minimum, resolve these candidate-local questions:

```text
A:
  what is authoritative retained W?
  what induces h?
  what realizes mobility?
  how are retained W, instantaneous W, K, h, and mobility related?

B:
  what exact map carries T into h or another structural object?
  what role remains for W and K?
  what realizes mobility without turning T into undeclared resource?

C:
  how does the constitutive C-sector condition h or another structural object?
  what role remains for W and K?
  how are selector motion, topology, and mobility kept distinct?
```

Each candidate must receive one D4 disposition: coherent bounded ownership,
blocked pending a named constitutive/theory derivation, rejected for incompatible
roles, or routed to a named successor investigation. Repeating that geometry
and mobility may be conflated is not a D4 result; B1 already established that
as a V3 design debt. D4 may revise the inherited distinction when a new V4
object or map makes the revision explicit and source-backed.

Prevent one field from silently serving as retained structure, mobility,
directional current, and analysis projector. Do not preassign `K` as transport
mobility. Apply both topology scopes and the event transport/accounting boundary
frozen in D0.

## D5. Directional Read-Back

Produce the actual candidate-specific graph-native retained-conditioned
operator family, or route the candidate to a named missing derivation. Record
its equation/signature, domain, codomain, typed inputs, output cochain, and
composition with present current. The operator must expose the passive null,
edge-coordinate orientation covariance, physical present-current reversal
response, retained-representation orientation/chirality content,
present-current convention, retained-state counterfactual, rival-carrier
controls, and output cochain space.

D5 consumes the B1 typed-cochain bridge as a strong starting derivation and
verification control, not as immutable V4 semantics. It may refine or replace
that bridge when current core theory and the selected V4 geometry justify the
change. Restating the inherited requirements without an operator family or
named derivation does not close D5.

Name the passive-null control `zero_present_current`. Separately record the
direct `T_M -> h/W/mobility -> J0` path, the `(T_M,J_C) -> j` Read-Back path,
and any overlap/double-count risk. Where structurally possible, read-off must
disable `j` while preserving the direct retained-conditioned `J0` path.

Separate `J0`, `j`, and total `J_C`. Reject scalar/label/proxy relabels.

## D6. Total-Current Closure

Choose and write the candidate-specific total-current closure. A surviving row
must provide either an actual regular algebraic relation such as
`J_C = Psi(C,T,...)` with the full effective loop block, or an explicit temporal
current state law with its trigger and clock. Record solve order,
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

D6 consumes B1's algebraic-slaving and singular-boundary results as bounded V3
facts, controls, and design pressure. A changed V4 current operator requires a
fresh closure derivation rather than mechanical inheritance. Listing slaved and
temporalized current as generic possibilities is not a D6 decision; the gate
must select or reject one for each surviving architecture.

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

By D7, write the complete candidate transition `X_(k+1) = F_V4(X_k)` with
constitutive equations, stage order, state ownership, write inputs, release or
reconfiguration law, Read-Back law, and all accounting surfaces. A candidate
that cannot supply such a transition must be rejected or routed to a named
derivation rather than carried by requirement prose.

For a constitutive `C` sector, preserve the D2 factorization and prove that the
write/read arrows are not ordinary `C` evolution under new names.

At D7, freeze formed-loop conditions, admissibility and singular/invalid
boundaries, reconfiguration triggers, and the questions D8 must answer. Defer
structural and temporal stability classification to D8.

## D8. Continuation Realization And Analysis Contract

Analyze the concrete completed D7 transition while keeping four objects
separate:

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

D8 must map the selected V4 operators to applicable B1/B2 discriminators and
identify which tests can be reused after implementation, which require a
V4-specific adaptation or rederivation because the causal object changed, and
which are inapplicable. Recreating GRV3/GRV4/GRV7 unchanged as design prose is
not new evidence and does not close D8.

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

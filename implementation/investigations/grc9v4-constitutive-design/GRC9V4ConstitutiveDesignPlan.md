# GRC9V4 Constitutive Design Investigation Plan

**Date:** 2026-08-23  
**Status:** D0-D7, D4-v2-D7-v2, D7G-v1/v2, the D7G-post-v2 correction, D8-A, coupled/implicit A+C, coupled A+C architecture-local D8-B, GTRS-OS, GTRS-RG, GTRS-PC, and GTRS-COMP accepted bounded; narrow GTRS-CI-PC is authorized; D9 and D10 remain blocked
**Design basis:** [`GRC9V4ConstitutiveDesignBasis.md`](./GRC9V4ConstitutiveDesignBasis.md)  
**Checklist:** [`GRC9V4ConstitutiveDesignChecklist.md`](./GRC9V4ConstitutiveDesignChecklist.md)  
**Decision ledger:** [`GRC9V4ConstitutiveDesignDecisionLedger.md`](./GRC9V4ConstitutiveDesignDecisionLedger.md)
**Initialization:** [`GRC9V4ConstitutiveDesignInitialization.json`](./GRC9V4ConstitutiveDesignInitialization.json)

## Purpose

Resolve the constitutive decisions required before a revision-distinct GRC9V4
specification can be written. The plan is an investigation, not a runtime
implementation tranche and not a normative specification.

## Execution Rules

- Execute D0-D10 serially, with the D4-v2-D7G append-only successor tranche
  inserted after accepted D7 and before D8; a later gate consumes accepted
  earlier decisions except for the explicit early terminal route to bounded
  D10 closeout.
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
- Reopen from the earliest accepted gate whose actual decision changes. Do not
  mechanically restart at D1 or D6, and do not use later completeness to
  retroactively promote an earlier incomplete candidate.
- A candidate's earlier completion, implementation convenience, or fit with
  current GRC9V3 surfaces is not selection evidence. Before comparative D8,
  each still-admitted candidate receives its named derivation attempt under
  the same veto and claim rules.
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

Current D4 execution resolves ownership without selecting an architecture:

```text
A = coherent bounded retained-mobility ownership
B = routed to GRC9V4-D4-B-INDEPENDENT-CARRIER-GEOMETRY-CLOSURE
C = source-backed retained-geometry role routed to
    GRC9V4-D4-C-RETAINED-GEOMETRY-CLOSURE for its exact map
```

For A, enabled `W_A` replaces legacy reconstructed `W_hat` as the single
transport authority; it does not become `h`. Here `W_A` is D2's authoritative
positive `W[k]`, while `R_W` remains the declared relation between `W_A` and
`W_hat` and is not itself mobility authority. For B, an intended geometry role
without a selected `T -> K/h` map is insufficient. For C, the core supports a
retained-geometry role but explicitly leaves `h_M` underdetermined. D5 may
derive candidate-specific operator families only within these ownership and
missing-closure boundaries.

Preserve the source-stage ordering rather than treating stored current as a
generic geometry input. Baseline `K_4` consumes `C`, gradient-`C`, and other
declared source-typed terms; D5 may later map present `J_C` to directional `j`,
which may then enter `K_4`, induce `h_4`, and condition a later `J0`. Candidate
C's `H_M` consumes the retained sector, an optional D1-admitted or
deterministically reconstructable dynamic sector, `C`, and base/reference
geometry, not present `J_C`; present current belongs to the subsequent
Read-Back map. Analysis alone does not grant a projector runtime authority. A
dynamic sector that needs its own persistent history requires D1
reclassification or successor admission, while an analysis-only sector cannot
be consumed by `H_M` at runtime.

D4 pressure records should make the ownership graph inspectable rather than
count fields. For every load-bearing object, record causal-state status,
derivation and serialization, writer, native consumers, units/gauge,
orientation, positivity/domain, cache status, and topology transport. For every
arrow, record whether it is constitutive, derived, analytical, or theory-open;
its temporal side, locality, invertibility, resource/measure effect,
smooth-stratum domain, and event obligation. One object may parameterize
multiple roles only through explicit factorized maps. Runtime mobility is not
the D8 analytical relaxation operator without a derived push-forward.

Feed D4 conclusions back into D3 consumption without rewriting the accepted D3
record. In particular, mobility-only Candidate A retains runtime viability but
does not retain a direct `W_A`-conditioned structural claim. Candidate C must
resolve its selector/geometry fixed point and show sector-specific causal
consumption; ordinary full-`C` geometry is not enough. Keep baseline-current
paths through retained-conditioned geometry or mobility distinct from the D5
Read-Back path.

Treat persistent topology mutation as a possible rival historical carrier even
when topology is not the candidate's claimed retained representation. Candidate
credit requires that topology-mediated history be isolated and included in
write/read and event accounting.

## D5. Directional Read-Back

Produce the actual candidate-specific graph-native retained-conditioned
operator family, or route the candidate to a named missing derivation. Use the
widened signature `R_a(T_a,h_a,X_read_a,k;J_trial)`, where `X_read` is declared
nonretained current-step context and may not hide prior history. Record its
equation/signature, domain, codomain, typed inputs, output cochain, and
composition with an unsolved present trial current in the later total-current
space. D5 must not silently solve D6 by treating the trial argument as an
already self-consistent `J_C`. The operator must expose the passive null,
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
direct `T_M -> h/W/mobility -> J0` path, the `(T_M,J_trial) -> j` D5 path,
and any overlap/double-count risk. Where structurally possible, read-off must
disable `j` while preserving the direct retained-conditioned `J0` path.

Separate `J0`, `j`, and total `J_C`. Reject scalar/label/proxy relabels.

The hardening audit further requires graph-isomorphism covariance, arbitrary
edge-subset reorientation, four distinct reversal cases, candidate-specific
directionality class, decomposition and gain gauges, and separate read-off,
carrier-neutral, and frozen-carrier controls. Every counterfactual must be
labelled algebraic/off-manifold or runtime-reachable. Freeze live-edge support,
exact-zero mobility debt, locality, disconnected-component behavior,
divergence/boundary accounting, and cut/cycle/harmonic scope. Passive null is
not energetic passivity or full-loop stability. A typed operator family is
distinct from closed retained mediation. The former requires a lawful typed map
and controls; the latter additionally requires an admitted retained-state-to-
conditioning path and counterfactual. Neither is yet a physically identified
channel when its effect may be absorbed into the retained-conditioned baseline
path.

Current D5 execution produces two bounded operator families and one named
derivation route:

```text
A:
  q_A = (W_A - W_hat) / (W_A + W_hat)
  j_A = chi_A Diag(q_A) J_trial
  status = explicit V4 extension family; not inherited core Read-Back

B:
  status = routed to GRC9V4-D5-B-TYPED-READBACK-DERIVATION
  reason = T_B and G_B do not yet type a one-cochain response

C:
  Delta1_M = B^T H0^-1 B H1
  j_C^M = chi_C (I + tau_C Delta1_M)^-1 J_trial^M
  status = explicit isotropic resolvent specialization of the core candidate
           Hodge-response class, parameterized by h_M
```

The A contrast is dimensionless, bounded, invariant under stored-edge
orientation reversal, and distinct from D2's `R_W`. It does not make `W_A`
retained geometry or historical chirality. C's graph Hodge resolvent is a
positive contraction on a regular fixed-topology, fixed-rank retained-geometry
one-form space. Its larger response on low or harmonic Hodge modes is a read
gain, not temporal persistence.

For both admitted families, `zero_present_current` enforces the passive null.
Physical current reversal is separate from edge-coordinate reorientation.
Read-off sets only the candidate read gate `chi_a = 0`, preserving A's direct
`W_A -> J0` path or C's conditional direct `h_M -> J0` path. D6 must include
both direct and explicit read paths in the full effective loop and reject
unattributed double counting.

Candidate C remains blocked from final architecture status by the named `H_M`
derivation, metric-identification, and lawful `T_C`-mediation debts. The current
C operator consumes `h_M`; it has no direct `T_C` consumer, and a fixed-`h_M`
`T_C` swap must be a negative control. Candidate B remains routed rather than
rejected. A's explicit channel remains physically unidentifiable from mobility
until D6 and later interventions close the decomposition debt. D5 therefore
defines two operator channels but identifies zero physical Read-Back channels.
The equations are constitutive design outputs, not runtime implementation or
positive runtime evidence. During D6, `X_read_a,k` remains frozen at its
D5-declared pre-read stage while solving the total-current recurrence; it may
not be silently recomputed from the unknown `J_C`. D5 must also classify every
predecessor debt and
separate pre-D10 factorization/control-availability obligations from post-spec
physical-identification and empirical rival-attribution work. Optional sectors
excluded from an initial profile remain dormant rather than blocking that
profile unconditionally. D8 must freeze C's Hodge-star construction, boundary
convention, and discretization semantics before D10; later normative encoding
is not itself a D10 blocker. A routed candidate remains in the architecture
candidate set unless explicitly rejected.

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
Postsolve `J_C` is the authoritative causal current available to D7. D6 does
not authorize a direct `j -> retained state` write; `j` is available only to
the declared shared-gain `j tensor j` geometry path and telemetry/analysis
unless D7 derives a lawful non-bypassing successor. Under `zeta = 0`, diagnostic
`j` has no causal downstream consumer in the initial profile.

Current D6 execution selects regular same-beat algebraic slaving for A and C
and routes B without rejection:

```text
A:
  J_C,e = J0,A,e / (1 - zeta_A chi_A q_A,e)
  q_A,e = (W_A,e - W_hat,e) / (W_A,e + W_hat,e)

C:
  J_C^M = (I - zeta_C chi_C R_C)^-1 J0,C^M
  R_C = (I + tau_C Delta1,M)^-1

B:
  routed to the existing D4 geometry and D5 typed-operator derivations
```

Both admitted profiles use `0 < zeta_a <= zeta_bar,a < 1`, freeze `J0`,
geometry, retained state, and `X_read` before the solve, and therefore have
`B_eff,D6 = zeta_a chi_a R_a`. This effective block is complete only for that
declared solve staging. Moving a `J_C`-dependent geometry, mobility, retained-
state, or baseline path inside the solve requires D6 rederivation with the full
chain rule.

This lagged-geometry order is an explicit revision-distinct GRC9V4
discrete-beat constitutive realization. It does not assert that the core
simultaneous active-current loop generally reduces to `(I - zeta R)`. A profile
that places `J -> j -> K -> h -> J0` inside one solve must reopen D6 and include
the complete chain-rule effective block.

Loss of bounded invertibility fails closed. It does not select temporalized
current, a pseudoinverse, a critical-mode deletion, spark, basin birth, or
topology change. Algebraic slaving is not claimed as a demonstrated fast
temporal limit. D6 resolves same-beat total-current closure only; D7 still owns
the cross-beat write/read loop and complete transition.

The hardened D6 execution distinguishes regular algebraic slaving, partial
critical-subspace deslavement, full current temporalization, and blocked/routed
closure. A/C remain in the first class on the selected subunit-gain profiles;
partial deslavement is the first successor question if only a proper subspace
later loses regular elimination. A critical runtime subspace cannot be named by
an analysis mode index without constitutive authority and event transport.

Solve on the declared transport-current space with closed-channel and boundary
conditions inside the equation. Potential gauge nulls are removed upstream and
do not count as current singularity. Numerical solver path, damping, seed,
regularization, or iteration count cannot select a physical branch or become a
clock. Robust closure uses a singular-value or inverse-norm margin; `+1` in the
full effective-block spectrum is the finite-dimensional singularity condition,
not spectral radius one in general.

For C, tree and cycle topology are separated: harmonic response remains unit
for every `tau_C`, but subunit gain retains a uniform margin. Unit gain on a
cycle is a singular boundary and harmonics may not be projected away to rescue
the solve. For A, the exact `(zeta_A,q_A)` domain is recorded and the selected
subunit gain supplies a uniform margin without requiring a D7 `W_A` cap.

D6 also freezes a single shared `zeta_a` for the linear `j` current contribution
and the later staged `j tensor j` geometry contribution in an initial
normalized profile. Separate gains require a successor. Physical unit and
tensor compatibility remain under the inherited D4 gauge/units audit. Exact
A/C absorbability relative to their complete baseline model
classes remains a pre-D10 mathematical debt, distinct from post-spec empirical
identification. Explicit `J0 + zeta j` notation alone cannot establish a
nonredundant Read-Back mechanism.

Debt persistence is transitive. D6 must preserve both its 25 current-generation
open debts and the 20 still-open older IDs incorporated through D5; all 16
transitive pre-D10 blockers remain adjudicable even when they do not receive a
new D5 or D6 identifier.

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

By D7, write the complete candidate-local transition
`X_(k+1) = F_V4(X_k; h_pre)` conditional on an admitted pre-read geometry with
constitutive equations, stage order, state ownership, write inputs, release or
reconfiguration law, Read-Back law, and all accounting surfaces. A candidate
that cannot supply such a transition must be rejected or routed to a named
derivation rather than carried by requirement prose.

For a constitutive `C` sector, preserve the D2 factorization and prove that the
write/read arrows are not ordinary `C` evolution under new names.

At D7, freeze formed-loop conditions, admissibility and singular/invalid
boundaries, reconfiguration triggers, and the questions D8 must answer. Defer
the concrete reduced transition's temporal stability and floor-nonsmoothness
classification to D8. Normative structural continuation and stability remain
blocked on the missing `H_4` map and require later reanalysis after that map
exists.

### D7 implementation result

D7 closes one bounded reduced transition without treating that result as a
complete normative architecture. Candidate A receives an exact fixed-topology,
fixed-geometry kinetic profile:

```text
C[k], W_A[k]
  -> graph-coupled Phi_A and J0_A
  -> W_hat_A = G_W(C[k], J0_A)
  -> q_A, j_A, regular postsolve J_C_A
  -> incidence continuity C[k+1]
  -> rebuild writer differential/gradient summaries from C[k+1]
  -> W_drv_A = G_W(C[k+1], J_C_A[k])
  -> log-geometric retained write W_A[k+1]
```

The retained write is one-beat delayed, consumes authoritative postsolve
`J_C`, has one deterministic writer, preserves a positive bounded interval,
and provides native release toward the zero-forming-current target. It is an
explicit V4 candidate completion based on the existing graph conductance
functional, not a unique law inherited from core theory.

The exact downstream mediator is `D_A[k] = (C[k+1], J_C_A[k])`. The result
separates two loops: the direct retained-mobility recurrence remains available
when `chi_A = 0`, while the explicit Read-Back subloop is constitutively
load-bearing only on admissible states with nonzero `chi_A`, `zeta_A`, `q_A`,
`J0_A`, and writer sensitivity. Exact mathematical absorbability on the
selected model class remains open to a named post-D8, pre-D10 classification;
D10 consumes that classification rather than deriving it. Post-spec physical
channel attribution remains separate. Changes in `W_A`, `W_hat_A`, and their
moving neutral relation are attributed separately.

Stored-edge coordinate reorientation, local current parity, and full physical
history reversal are distinct. Scalar `W_A`, `W_hat_A`, `W_drv_A`, and `q_A`
are invariant under arbitrary stored-edge coordinate reversal, and the
explicit `J_C squared` contribution in `G_W` is sign-even. Reversing the
physical current generally changes `C[k+1]`, however, so the complete
`W_drv_A` and `W_A[k+1]` need not be invariant. A therefore stores no
intrinsically signed cochain coordinate while its scalar spatial pattern may
still distinguish reversed physical histories through continuity-mediated
`C`.

This closes A's kinetic recurrence only. The exact
`K_4 -> H_4 -> h_4` map remains open, so a recorded `j tensor j` contribution
does not establish structural cultivation or a complete normative GRC9V4
transition. Candidate B remains routed through its typed carrier/geometry and
Read-Back derivations. Candidate C retains the core-derived sector write
equation but remains routed because `T_C -> H_M -> h_M` is not closed on
manifold. D8 may analyze only the concrete reduced A transition and its
explicit structural limitation after a separate human direction.

The initial 72-row pressure matrix is supplemented by a 96-row adversarial
closure audit. That audit binds every concern to a satisfied contract, a
bounded open debt, or a named B/C/D8/D9/D10 route; it does not convert routed
or deferred questions into positive evidence.

D7 carries 16 current debts. It explicitly dispositions all 25 immediate D6
generation rows: 23 are resolved or superseded into named D7 debts and two
nonblocking rows remain independently carried. D10 consumes the three-way
union of current D7 debts, unresolved immediate predecessor dispositions, and
unresolved transitive predecessor dispositions. A technical debt marked
`must_close_before_D10` requires a named earlier result; D10 may consume but
may not generate that missing result.

D7 is accepted bounded, but D8 authorization is separately deferred. The later
specification and implementation must recompute every differential or gradient
summary consumed by `G_W(C[k+1], J_C[k])` from post-continuity `C[k+1]`.
Reusing the pre-continuity `C[k]` summaries would violate the accepted writer
temporal side and stale-derived-surface prohibition.

## D4-v2-D7G. Candidate Completion And Structural-Closure Successor Tranche

Accepted D4-D7 established one bounded A recurrence and localized the earliest
missing causal objects for B, C, and the normative structural path. They did
not select A. This successor tranche gives those missing objects a
theory-grounded completion attempt before comparative continuation analysis.
It is not an optimization pass and does not require B or C to survive.

The accepted D4-D7 records remain immutable. Every v2 record must bind its
predecessor decision digest, identify exactly which earlier conclusion changes,
and carry every unaffected accepted contract forward unchanged.

The default successor lineage is frozen before execution for the path on which
no earlier accepted gate must reopen:

```text
D4-v2:
  predecessor = accepted D7-v1 digest
  supersedes = accepted D4-v1 digest

D5-v2:
  predecessor = accepted D4-v2 digest
  supersedes = accepted D5-v1 digest

D6-v2:
  predecessor = accepted D5-v2 digest
  supersedes = accepted D6-v1 digest

D7-v2:
  predecessor = accepted D6-v2 digest
  supersedes = accepted D7-v1 digest

D7G:
  predecessor = accepted D7-v2 digest
  supersedes = null
  relation_to_D7-v2 = extends_with_global_structural_integration
```

The exact accepted v1 digests are recorded in the decision ledger. D7G is a
new integration gate, not another correction of D7-v2.

If a gate pauses and changes an earlier accepted decision, this default chain
no longer applies beyond the pause. The resumed successor receives a new
record/version identity, consumes the latest accepted record in the fully
propagated serial chain, and supersedes the latest accepted record for the same
logical gate when one exists. In particular, a resumed D7G after a required
D4-D7 successor cycle must consume the newly accepted D7 successor, never the
obsolete original D7-v2 digest.

Debt follows chronological predecessor identity:

```text
successor_debt_input =
  complete unresolved debt union of predecessor record

superseded_gate_debt =
  provenance/disposition source only,
  not a replacement for chronological predecessor debt
```

D4-v2 therefore begins from the complete accepted D7 three-way debt union even
though it supersedes D4-v1. Every later successor applies the same rule.

The controlling source set is the current core Continuation Spectrum and
Read-Back theory, the constitutive design basis, and the accepted D0-D7
decision chain. B1/B2 and GRC9V3 remain historical evidence and compatibility
boundaries. No v2 lane may infer a constitutive map from implementation
convenience, requirement prose, or the desire to preserve a candidate.

Every candidate row must end D7-v2 in one of these scientific dispositions:

```text
D7G_eligible_complete_candidate_transition
current_tranche_closed_missing_theory
current_tranche_closed_missing_constitutive_derivation
current_tranche_rejected_target_incompatibility
```

`routed_not_rejected` remains valid during D4-v2-D6-v2 but is not a D7-v2
terminal disposition. A closed current-tranche lane retains its named future
route and does not become a claim that the candidate family is impossible.

Reopening is control flow, not a terminal scientific disposition:

```text
control_flow_disposition = reopen_at_named_earlier_gate
```

The current gate pauses, a named successor propagates the changed decision
forward, and the paused gate resumes. A candidate cannot enter D7G merely by
carrying a reopening label.

Gate-level exhaustion is machine-decidable:

```text
zero candidate survivors after candidate-local terminal dispositions:
  gate_status = rejected_all_candidates
  current_candidate_set_exhausted = true
  preserve every candidate-local close reason

all remaining paths blocked by one common theory gap:
  gate_status = blocked_missing_theory
  current_candidate_set_exhausted = false unless no candidate remains admitted
```

Neither status rejects GRC9V4. Each opens only the existing bounded D10 or
named successor route authorized by the general gate rules.

The reopening rule is causal rather than procedural:

```text
independent nonresource T_B retained as admitted
  -> no D1 successor required

T_B reclassified as a projection or sector of C
  -> reopen D1 through a named successor

U_B introduces a resource reservoir or changes admitted formation/write inputs
  -> reopen D2 through a named successor

B requires independent delta-T_B structural directions
  -> reopen D3 through a named successor

new geometry/current dependencies alter an accepted D4-D6 operator
  -> append the corresponding earliest successor and propagate forward
```

### D4-v2. Candidate Geometry And Carrier Completion

Planned record: `GRC9V4-CD-D4V2-v1`, with structured and interpretive outputs
`decisions/D4v2CandidateGeometryAndCarrierCompletion.json` and
`decisions/D4v2CandidateGeometryAndCarrierCompletion.md`.

Run two separately attributable candidate rows in one combined D4-v2
execution:

```text
B row:
  type T_B, including graph domain, rank, orientation, units, covariance,
  state authority, resource status, and exact G_B(C,T_B,...) -> S_4^B

C row:
  derive or close T_C,C,selector context -> H_M -> h_M,
  including Hodge-star/metric construction, selector timing, lagged versus
  staged versus uniquely regular fixed-point semantics, and fixed-stratum
  rank/boundary admissibility
```

D4-v2 also freezes a common input interface to the future global structural
map without deriving that map:

```text
candidate-local structural payload S_4^a
  -> typed adapter iota_a
  -> K_4^a in the common K_4 domain
  -> deferred H_4
  -> deferred h_4
```

The initial common `K_4` domain is graph-local and assembled, not the full
dense matrix algebra on all live edges. Candidate contributions take the form
`sum_s R_s^T K_4,s R_s` over declared finite-radius stalks. Candidate A uses
vertex-star current-tensor assembly, B uses radius-one line-graph support, and C
may enter only through a retained-mediated candidate-local current followed by
the same graph-local current-tensor assembly. Any graph-global nonlocal `K_4`
requires a named successor and cannot enter accidentally through a global
`j j^T` array.

Any local quadrature or partition weight must be preregistered as part of its
`K_4,s`. D4-v2 freezes the exact locality/covariance class only; D7G must freeze
assembly normalization and show that overlapping stalk multiplicity does not
silently rescale the global contribution.

For every candidate row, freeze the payload and adapter domain/codomain,
authority, units, gauge, covariance, orientation, boundary/topology behavior,
information loss, and whether the adapter is identity, derived, or absent.
Candidate A carries its accepted structural input into this interface. Candidate
B must expose `K_4^B` in the common domain or a typed `iota_B`; direct `h_B` may
remain candidate-local read geometry but cannot become a rival owner of
physical `h_4`. Candidate C may retain `h_M` as retained/read geometry, but any
claimed physical/global effect must expose a typed crossing into the same common
domain. For C, D4-v2 may defer that crossing to the source-backed
`T_C -> H_M -> R_C -> j_C^(M,flat) -> (I_4M^pre)^-1 -> j_C^(phys,flat) ->
graph-local (j_C^phys tensor j_C^phys) -> K_4` route rather than inventing a
direct `T_C -> K_4` adapter. An absent lawful direct adapter
closes that direct route; it cannot be filled later by relabeling `h_B` or
`h_M` as `h_4`.

Any claimed direct adapter must also be load-bearing rather than merely
type-correct. For any candidate claiming a direct retained structural crossing,
preregister at least one
lawful retained-state intervention with matched nonretained inputs for which
`K_4^a` changes after `iota_a`. An adapter that maps every candidate-specific
retained distinction to the same baseline `K_4` does not close the structural
crossing. A candidate that defers the crossing to a retained-mediated current
route must record that route as deferred and may not receive direct-crossing
credit at D4-v2.

D4-v2 must also type the candidate-local current spaces needed before global
`h_4` exists. Candidate C freezes a provisional fixed-profile identification:

```text
I_4M^pre : Omega^1(h_4^pre) -> Omega^1(h_M)
status = candidate_local_typing_only
final_h_4_h_M_compatibility = deferred_to_D7G
```

Record its source and target geometry, orientation, units, basis covariance,
invertibility or information loss, stage validity, and fixed-profile scope.
It is sufficient to type D5-v2/D6-v2 but must be validated or replaced by D7G.
Candidate B must likewise freeze the one-form/current geometry on which `R_B`
acts, whether `Omega^1(h_B)`, `Omega^1(h_4^pre)`, or another explicitly typed
space, plus its lawful identification with authoritative physical current.
D4-v2 does not require a separate `h_B`; it requires that this choice stop being
implicit before D5-v2.

Carry accepted A D4 ownership unchanged. Defer the common
`K_4 -> H_4 -> h_4` construction until D7G, after A/B/C candidate-local
transitions have either closed or received terminal current-tranche
dispositions. Neither B nor C may borrow A's retained ontology or the other
candidate's equations.

D4-v2 must either produce exact typed maps with admissibility and authority
contracts or close the affected lane with a localized theory/constitutive
reason. Symbols, interface requirements, or a convenient numerical closure do
not count as derivations.

#### D4-v2 implementation result

D4-v2 is accepted bounded under record
`GRC9V4-CD-D4V2-v1`, decision digest
`5862cbab0d36e1137dc647d7d21d48f77666a77bf9e7b178c830d323e4ed6309`.
It consumed accepted D7-v1 as its chronological predecessor and supersedes only
the D4-v1 B/C completion and common-interface scope.

The corrected constitutive standard does not require a uniquely theory-selected
representation. D4-v2 first pressures the admissible representation family and
then permits a bounded revision-specific choice, as earlier gates did for A and
the C Hodge response. A selected broader family is not called minimal when a
strictly smaller admissible subprofile already has the required consumer.

The two candidate rows remain separately attributable:

```text
B:
  T_B = bounded graph-local symmetric bilinear form on Omega^1_G
  minimal subprofile = diagonal unoriented-edge scalar
  [T_B] = [H_1,pre]
  Theta_B = H_1,pre^-1/2 T_B H_1,pre^-1/2 is dimensionless and bounded
  locality = d_L(G)(e,f) <= 1, covariant and independent of array order
  authority = independent serialized nonresource
  G_B = T_B
  iota_B(S) = kappa_B S into common K_4 graph domain
  kappa_B = finite preregistered nonzero conversion coefficient
  signed spectrum = direction of K_4 bilinear contribution only,
                    not continuation hardening or softening before H_4/D8
  D7G capacity rule = recompute Theta_B under accepted h_4/H_1 and readmit;
                      no silent clipping or renormalization
  future R_B space = Omega^1(h_4^pre)
  disposition = admitted_bounded_candidate_geometry_and_carrier_completion

C:
  L_0,sym,pre = H_0,pre^-1/2 B_pre H_1,pre B_pre^T H_0,pre^-1/2
  Lambda_C = bar_Lambda_C sigma_L,pre with explicit operator units/gauge
  sigma_L,pre = fixed profile-owned dimensional reference declared before
                evaluation, not selected from observed spectrum or outcomes
  P_M^Delta = H_0,pre^-1/2 1_[0,Lambda_C](L_0,sym,pre) H_0,pre^1/2
  T_C = P_M^Delta C on a fixed-rank strict-gap no-flux stratum
  dynamic sector = analysis-only outside the initial runtime profile
  selector stage = h_4^pre -> P_M^Delta -> T_C
  H_1,M = D_C H_1,pre D_C with D_C = diag(exp(kappa_M,C r_C / 2))
  inner map = pressured smooth bounded odd family with tanh representative
              and symmetric endpoint lift; not uniquely theory-selected
  I_4M^pre = H_1,M H_1,pre^-1, instantiated but not assumed isometric
  local log scaling = kappa_M,C diag(r_C), not global H_4 relative log
  H_M load-bearing = same-state kappa_M,C on/off with nonzero r_C
  direct T_C -> K_4 adapter = not admitted
  future common route = T_C -> H_M -> R_C -> j_C^(M,flat)
                        -> (I_4M^pre)^-1 -> j_C^(phys,flat)
                        -> graph-local (j_C^phys tensor j_C^phys) -> K_4
  retained_geometry_off = kappa_M,C = 0 removes H_M-conditioned J_0,C path
  read_off = chi_C = 0 removes explicit j_C/tensor route but preserves
             H_M-conditioned J_0,C
  gain_off = zeta_C = 0 allows diagnostic j_C but blocks its total-current and
             K_4 effect while preserving H_M-conditioned J_0,C
  disposition = admitted_bounded_candidate_retained_geometry_completion
```

The gate freezes the common graph `K_4` domain as assembled finite-radius
symmetric bilinear forms on the oriented live-edge one-form space and applies
the load-bearing adapter test to candidates claiming direct crossings.
Candidate A's causal architecture is unchanged, while its vertex-star local
assembly is a new D4-v2 common-interface discretization result rather than an
accepted D7 result. C receives no direct-crossing credit at this gate.
The record binds the 2 immediate and 20 transitive live D7 debt rows by exact
machine-readable identity, status, blocker flag, source SHA, and D7 digest;
counts alone are not an admissible debt handoff.
The local fixed-topology stratum remains an analysis profile, not a
fixed-topology V4 target. Neither candidate is rejected or ranked, and `H_4`
remains D7G work.

D5-v2 was authorized by D4-v2 acceptance and is now implemented awaiting human
review. Both B and C remain eligible for candidate-specific directional
Read-Back completion under bounded V4 choices, not unique core-theory
deductions. D6-v2 and all later gates remain blocked.

### D5-v2. Candidate-Specific Directional Read-Back Completion

Planned record: `GRC9V4-CD-D5V2-v1`, with outputs
`decisions/D5v2DirectionalReadBackCompletion.json` and
`decisions/D5v2DirectionalReadBackCompletion.md`.

Propagate only lanes whose D4-v2 objects exist. Preserve accepted D5 results
that are unaffected.

For B, derive the actual typed one-cochain `R_B`, its domain/codomain,
orientation and basis covariance, passive/read-off behavior, resource boundary,
lawful dependence on retained `T_B`, and exact consumption of the D4-v2-frozen
current-space identification. For C, determine whether the accepted
Hodge response becomes genuinely conditioned by retained `T_C` through the
new `H_M`, rather than remaining only an externally parameterized `h_M`
family. Consume `I_4M^pre` explicitly and require lawful on-manifold
selected-content and matched-complement counterfactuals.

If B's derived `R_B` supports a source-patterned
`j_B tensor j_B -> K_4` route, keep it distinct from the already admitted
direct `T_B -> K_4` route. Freeze read-off, gain-off, path-overlap, and
double-count controls before either route is credited as evidence for the
other. For C, map any `h_M`-represented Read-Back current back through
`(I_4M^pre)^-1` before common physical-one-form tensor assembly; matching edge
array dimension is not sufficient typing.

Carry accepted A D5 unchanged unless a named earlier reopening changes its
causal object. Do not manufacture an A-v2 operator merely to keep all lanes
visually symmetric.

#### D5-v2 implementation result

D5-v2 is accepted bounded under record
`GRC9V4-CD-D5V2-v1`. It consumes accepted D4-v2 as its chronological
predecessor, supersedes only the B/C and common-comparison scope of D5-v1, and
carries A's accepted D5 operator unchanged.

Candidate B now has the canonical Riesz endomorphism of the admitted D4-v2
bilinear carrier:

```text
A_B = H_1,pre^-1 T_B
R_B = chi_B A_B
j_B = R_B J_trial
```

The defining relation is `<u,A_B v>_H1pre = T_B(u,v)`. It preserves B's full
bounded graph-local directional content without the unit error of applying a
bilinear form directly or the representation error of applying `Theta_B` in
physical coordinates. The operator is `H_1,pre`-self-adjoint and bounded by
the accepted `Theta_B` capacity, but it need not be positive. Signed response
is not continuation hardening or softening.

B's direct and current-mediated structural paths remain distinct:

```text
direct:           T_B -> kappa_B T_B -> K_4
current-mediated: T_B -> R_B -> j_B -> future local j_B tensor j_B -> K_4
```

`chi_B`, `kappa_B`, and future `zeta_B` controls isolate those paths. The
current-tensor route receives no load-bearing credit before D6-v2 and D7G.

Candidate C retains the accepted Hodge resolvent but now consumes the D4-v2
retained geometry and non-isometric metric identification exactly:

```text
R_C,M = chi_C (I + tau_C Delta_1,M)^-1
Rbar_C = (I_4M^pre)^-1 R_C,M I_4M^pre
j_C,phys = Rbar_C J_trial,phys
```

An equal-resource selected-sector perturbation changes `H_1,M`, `Rbar_C`, and
one compatible probe output; a matched complement perturbation leaves `T_C`
and the complete response unchanged. This closes C retained mediation at the
constitutive-operator level on the fixed-rank smooth selector stratum. It does
not establish runtime mediation. Because `I_4M^pre` is not assumed isometric,
retained-space positivity and contraction are not promoted into physical
`H_1,pre` norm claims.

The implementation records 60 fail-closed controls, dispositions for all 16
current chronological D4-v2 debts and all 27 superseded D5-v1 debts, and 19
current typed debts. It also rebinds the exact 2 immediate plus 20 transitive
debt rows inherited through accepted D4-v2, producing a 41-row complete live
debt union. C mediation uses an existential compatible-probe gate: one
null-direction probe may remain unchanged, while the claim requires at least
one preregistered lawful selected-content probe with nonzero response.

All A/B/C rows are D6-v2 eligible after human acceptance, but A may be reused
only with an explicit unchanged-causal-object proof. Total-current closure,
complete transitions, common `H_4`, runtime evidence, physical channel
identification, candidate ranking, specification, and implementation remain
blocked.

### D6-v2. Updated Total-Current Closure

Status: accepted bounded.

Planned record: `GRC9V4-CD-D6V2-v1`, with outputs
`decisions/D6v2UpdatedTotalCurrentClosure.json` and
`decisions/D6v2UpdatedTotalCurrentClosure.md`.

For every lane changed by D4-v2 or D5-v2, rebuild the complete within-solve
dependency graph and effective current block. Determine whether retained
geometry introduces new same-beat current dependence, whether the accepted
lagged/staged semantics remain valid, and whether regularity, support,
singular-boundary, orientation, and conservation contracts still close.

Reusing accepted D6 is allowed only with an explicit unchanged-causal-object
proof. Endpoint compatibility is not evidence that the crossing or effective
operator is unchanged. A candidate that lacks a regular total-current closure
cannot proceed to D7-v2.

D6-v2 must use the exact operator structure now available. For B, classify
`I - zeta_B A_B` by the generalized eigenvalues of the `H_1,pre`-self-adjoint
`A_B`; `|zeta_B| t_B,max < 1` is a sufficient uniform regularity region rather
than a generic untyped small-gain assertion. Use `T_B -> -T_B` as a
fixed-probe path discriminator: the direct linear `kappa_B T_B` contribution
and fixed-probe `j_B` change sign, while that fixed-probe `j_B tensor j_B`
contribution is even. Audit active solved-loop parity separately because the
feedback inverse also changes under carrier sign reversal. Any displayed
closed-loop parity formulas that omit `chi_B` are explicitly scoped to active
read `chi_B = 1`. Keep the D4-v2 radius-one locality claim on `A_B` separate
from the solved inverse: repeated couplings may propagate influence throughout
one connected live-edge component, so D6-v2 claims component confinement and
not one-hop support of `J_C,B`. Preserve `chi` in singular loci:
`zeta_B chi_B = 1 / lambda_i` for B and `zeta_C chi_C = 1` on C harmonic
modes; the familiar `zeta`-only forms are active-read special cases.

For C, exploit the exact similarity:

```text
I - zeta_C Rbar_C
  = inverse(I_4M^pre) (I - zeta_C R_C,M) I_4M^pre
```

Exact invertibility is therefore similarity-invariant on the regular
identification domain, while physical singular-value conditioning may degrade
with `cond(I_4M^pre)`. Report exact branch regularity and robust physical
conditioning separately. For both candidates, keep retained-conditioned `J_0`,
explicit `j`, and later `j tensor j` geometry stages factorized without
same-beat geometry re-entry.

#### D6-v2 implementation result

D6-v2 is accepted bounded under record
`GRC9V4-CD-D6V2-v1`, decision digest
`ad02150010c4759d1c0ac4ba079c81cff99bad1f35b715f52b980aaf404eac0a`.
Candidate A is reused only after an exact unchanged
causal-object proof against accepted D6. Candidate B now has the regular
algebraic closure

```text
L_B = I - zeta_B chi_B H_1,pre^-1 T_B.
```

Its exact regularity is classified by the generalized eigenvalues of
`(T_B,H_1,pre)`, while `|zeta_B| t_B,max < 1` supplies a sufficient uniform
margin. The `T_B -> -T_B` discriminator is now explicitly stage-scoped: it is
sign-odd for the fixed-probe operator response, but the active solved feedback
has a generally nonzero even component because its inverse changes too. D7G
must therefore assemble the future tensor from the actual solved `j_B` rather
than assuming full-loop tensor parity.

Candidate C now uses

```text
Lbar_C = inverse(I_4M^pre) L_C,M I_4M^pre.
```

Exact invertibility is similarity-invariant. Robust physical conditioning is
separate and requires a finite declared cross-metric condition bound for
`I_4M^pre`; retained-space contraction is not promoted into an unqualified
physical-space claim.

The implementation consumes 67 unchanged D6 controls, replaces five changed
B/C controls, and adds 40 D6-v2 controls, producing 107 active controls. It
preserves 90 unchanged D6 pressure rows and adds 40 after superseding six
changed-premise rows, producing 130 active pressure rows. All 19 D5-v2 current
debts are dispositioned: 15 unchanged rows are copied exactly, while four
changed obligations are explicitly narrowed or superseded into seven D6-v2
debts. No predecessor debt is dropped. The exact 22 inherited debt rows remain
bound. The resulting live union contains 22 current plus 22 inherited rows.

All A/B/C closures are D7-v2 eligible, and D7-v2 is authorized but not started.
No current temporalization, complete transition,
global `H_4`, candidate ranking, specification, implementation, or runtime
claim is opened.

### D7-v2. Candidate Transition Completion And Comparative Admission

Planned record: `GRC9V4-CD-D7V2-v1`, with outputs
`decisions/D7v2CandidateTransitionComparativeAdmission.json` and
`decisions/D7v2CandidateTransitionComparativeAdmission.md`.

Write the complete candidate-local transition for every surviving lane without
yet claiming the common global structural closure:

```text
A:
  preserve the accepted kinetic recurrence and its open H_4 boundary

B:
  T_B[k] -> G_B/h_B -> R_B -> J_C[k]
  -> declared downstream consequence -> exact U_B -> T_B[k+1]

C:
  T_C[k] -> H_M/h_M -> R_C -> J_C[k]
  -> C[k+1] and selector staging -> T_C[k+1]
```

Each completed candidate-local transition must be Markov-closed on declared
state, stage ordered, atomic, resource-accounted, and equipped with passive,
read-off, write-off, frozen-carrier, rival-carrier, reversal/covariance, and
event-boundary control roles. Use a literal runtime intervention where it is
ontologically lawful; otherwise use a preregistered on-manifold matched
counterfactual or an explicitly labelled algebraic probe. An impossible or
off-manifold intervention may not be manufactured merely to make B or C look
control-symmetric with A. Missing lifecycle details may remain typed D9 debt,
but no load-bearing constitutive arrow may remain requirement prose.

D7-v2 produces a candidate-local completion table with one terminal disposition
per A/B/C lane. Every complete lane is marked
`D7G_eligible_complete_candidate_transition`; it is not yet D8-comparable
because the common structural closure remains open. If no candidate survives,
skip D7G and route to bounded D10 closeout or a named theory successor.

D7-v2 is accepted bounded under record
`GRC9V4-CD-D7V2-v1`, decision digest
`f0d355c3e769b43fe48f0eb8ab6e986ce80838dd55e884ad33c66e988b65106e`.
The candidate-local partition is:

```text
A = D7G_eligible_complete_candidate_transition
B = current_tranche_closed_missing_constitutive_derivation
C = D7G_eligible_complete_candidate_transition
```

A is bound without causal change to the accepted D7 transition by immutable
source-row reference and canonical candidate-row hash; D7-v2 does not maintain
a condensed duplicate of that authoritative row. D7-v2 supersedes D7-v1 only for the comparative A/B/C
partition; unchanged D7 contracts remain in force. C closes on the initial fixed-topology, fixed-boundary,
fixed-rank, strict-selector-gap stratum: authoritative continuity writes `C`
once and the derived nonresource sector is recomputed as
`T_C[k+1] = P_M,Delta C[k+1]`. Selector motion, rank change, and event transport
remain D8/D9 debt. This establishes a formal projected-sector recurrence and
retained-conditioned mediation, not effective retained write, dynamical
retention, a persistence class, or stability. Those remain D8 questions.

B's independent carrier, direct geometry payload, metric-raised Read-Back, and
regular D6-v2 current closure remain valid bounded work. The current tranche
closes B because no frozen source derives the exact recursive `U_B`. Copying
A's positive-mobility writer, calling an EMA a carrier, or inventing a
current-tensor target would add a load-bearing constitutive law after the
admission boundary. This is not ontology rejection, candidate ranking, or a
claim that A/C is more faithful to RC theory. A named theory or constitutive
successor may reopen B by deriving `U_B` with its type, units, capacity,
formation, release, covariance, and lifecycle semantics.

The comparative interpretation is:

```text
A = independent retained mobility with an explicit writer
B = independent structural carrier with complete conditional effects but no
    endogenous formative writer
C = no independent carrier; selected content is a sector of authoritative C
```

B therefore separates constitutive structure from formative law: given an
admissible `T_B`, its accepted equations state what the structure does, not how
it becomes. C instead separates formal recurrence from dynamical retention:
there is no missing independent `U_C`, but D8 must still determine whether the
selected content is slow, persistent, neutral, growing, or transient.

All 22 D6-v2 current debts are dispositioned and all 22 exact inherited debt
rows remain bound. Candidate-B obligations are terminally archived with a
named reopening debt rather than dropped or allowed to block A/C. A future
`U_B` reactivates four separate B obligations: writer/lifecycle,
direct/read/tensor factorization, post-`H_4` capacity, and absorbability. The
record distinguishes 40 current-live plus exact-inherited-bound rows from four
terminally archived predecessor rows, preserving 44 lineage evidence
identities. D7G-v1 is accepted bounded and authorizes the D7G-v2
geometry-parametric closure and finalization tranche. D8,
specification, implementation, runtime, and `src/` changes remain unauthorized.

### D7G. Global Metric And Structural-Cultivation Closure

Status: accepted bounded. D7G-v1 freezes a typed `H_4`
constitutive interface and admits one bounded affine profile family conditional
on an exact `E_ref` that current V3 source does not define. D7G-v2 must admit
that embedding, establish geometry-parametric or bounded profile-specific A/C
closure, and classify generated-geometry feedback relative to the selected
temporal realization before the profile/stage audit can complete.

Planned record: `GRC9V4-CD-D7G-v1`, with outputs
`decisions/D7GGlobalMetricAndStructuralCultivationClosure.json` and
`decisions/D7GGlobalMetricAndStructuralCultivationClosure.md`.

D7G begins only after D7-v2 has completed or closed every A/B/C lane. It
derives or formally closes the common:

```text
candidate-local admitted structural input K_4^a
  -> H_4
  -> h_4

then distinguish:
  h_4 -> branch-appropriate structural continuation consequence
  h_4+[k] -> discrete runtime geometry context for F[k+1]
```

Core RC leaves `g[K]` constitutively incomplete. D7G therefore freezes a typed
substrate interface rather than a universal metric law:

```text
H_profile : (Delta K_4, h_4,ref, context[K_4,base]) -> h_4+
```

Named profiles must declare positivity/nondegeneracy, covariance,
locality/support and inverse/solver support, units/gauge/capacity,
boundary/topology behavior, neutral reduction, temporal staging, geometry /
mobility factorization, and derivative access when consumed by analysis.

For B, graph-local assembly of `j_B tensor j_B` does not imply one-hop causal
dependence of the assembled values. The D6-v2 inverse may already make `j_B`
depend on baseline current throughout its connected live-edge component. D7G
must keep assembly locality separate from causal-support attribution.

Freeze the interface contract and every admitted profile's domain, codomain,
state/derived authority, measure, units, gauge, covariance, boundary and
topology/event behavior, stage order, fixed-point or lagged semantics, and
relation to every surviving candidate's local geometry map. A
candidate-indexed profile requires an explicit theory/constitutive basis and
may not be introduced merely to keep a candidate alive.

For Candidate C, D4-v2 may close the retained `h_M` construction and its typed
structural interface, but the physical `h_4 <-> h_M` compatibility remains open
until this gate. Candidate-local closure cannot pre-accept that identification;
D7G-v2 must replace witness-only `I_4M^pre` with `I_4M(h)` on the admitted
geometry class or emit a bounded profile-specific/terminal receipt.

For each D7-v2 survivor, prove that its admitted `K_4^a` reaches the global map
lawfully and that the resulting `h_4` re-enters a later transition without
same-beat circularity, hidden state, duplicate geometry authority, or broken
resource/accounting semantics. Preserve a candidate-local transition unchanged
only when the new structural crossing causes no upstream causal change. For
each survivor emit this structural-propagation receipt:

```text
H4_upstream_effect =
  no_upstream_causal_change
  | requires_geometry_parametric_closure_audit
  | requires_D4_successor
  | requires_D5_successor
  | requires_D6_successor
  | requires_D7_successor
  | candidate_incompatible
```

The D7G-v1 architectural correction treats `H_4` as a constitutive profile
parameter rather than a late universal completion. D4-D7 results are therefore
conditional candidate-local results over supplied pre-read geometry. D7G-v2
must lift those witnesses to a declared admissible geometry class or label them
as bounded profile-specific results. Changing between admitted profiles does
not itself reopen D4-D7. Reopen the earliest owning gate only when a profile
leaves the admitted class, changes state/write authority, changes same-beat
staging, or invalidates a candidate's declared operator family.

For every candidate claiming structural cultivation, D7G must establish at
least one admissible nondegenerate direction with matched nonretained inputs:

```text
delta T_a != 0
  -> delta K_4^a != 0
  -> delta h_4 != 0
  -> declared later transition consequence
```

A common `H_4` that exists but erases the candidate-specific structural payload
does not close that candidate's cultivation crossing.

D7G emits one of these per-candidate scientific dispositions:

```text
D8_comparable_complete_transition
candidate_local_transition_valid_selected_lagged_explicit_geometry_feedback_unresolved
current_tranche_closed_missing_theory
current_tranche_closed_missing_constitutive_derivation
current_tranche_rejected_target_incompatibility
```

`reopen_at_named_earlier_gate` is a control-flow disposition that pauses D7G;
it is not scientific closure and is not D8 admission.

It also emits one global structural disposition. If one candidate reaches D8,
it is a sole survivor, not a selected architecture. If no candidate reaches
D8 or the global structural map remains a hard target blocker, route to bounded
D10 closeout or a named theory successor rather than selecting the least
incomplete candidate.

#### D7G-v1 Implementation Result

D7G-v1 audited the implemented GRC9V3 source before freezing the V4
constitutive interface and conditionally admitting an affine profile family.
The source already provides an executable scalar geometry/transport law and a
separate row-basis hybrid node tensor, but the tensor is cached for diagnostics
and telemetry and is not consumed by scalar `base_conductance`, potential, or
flux. The current GRC9V3 specification explicitly reserves tensor-derived or
channel-specific transport for an `anisotropic_edges` extension. Thus current
GRC9V3 does not already close `K -> g[K]`. This source result does not imply
that V4 `h_4` must replace transport mobility or select `anisotropic_edges`.

D7G-v1 freezes
`H_profile : (Delta K_4, h_4,ref, context[K_4,base]) -> h_4+` and admits one
common affine profile family conditional on an exact V4 reference embedding
`E_ref : W_V3 -> H_1,ref`. Source and specification inspection found no unique
repository-owned convention for that embedding. D7G-v2 must define and admit
it, or close the affine family without instantiation. This prevents scalar V3
conductance from being relabeled as already-existing physical `h_4`:

```text
Delta K_4^a = K_4^a - K_4,base
Theta_4^a = kappa_H H_1,ref^(-1/2) Delta K_4^a H_1,ref^(-1/2)

H_1,read+^a
  = H_1,ref^(1/2) (I + Theta_4^a) H_1,ref^(1/2)
  = H_1,ref + kappa_H Delta K_4^a

H_0,read+^a = H_0,ref
```

The admitted domain requires `I + Theta_4^a` positive definite. The family is
a bounded revision-specific construction, not a unique core-theory formula,
canonical V4 completion, or continuum metric theorem. It is common to A and C,
preserves graph locality, is signed-edge/graph covariant, and is non-erasing because
`delta H_1 = kappa_H delta K_4` for nonzero `kappa_H`.

Exact affine neutrality is closed only relative to a supplied `h_4,ref`:

```text
Delta K_4 = 0 -> h_4+ = h_4,ref
```

The complete disabled-transition reduction `F_V4,disabled = F_V3` remains a
separate D7G-v2/full-factorization obligation.

The admitted vertex-star partition closes diagonal edge multiplicity, not a
unique off-diagonal pair normalization. Sparse/local assembly also does not
imply sparse/local inverse, identification, or solver support; both remain
typed profile pressure.

D4-D7 are now explicitly interpreted as candidate-local transitions
conditional on supplied pre-read geometry. The affine profile demonstrates a
non-erasing `delta K_4 -> delta h_4` direction, but a fixed witness does not
establish closure over an admissible geometry class:

B's missing source-backed `U_B` result remains independent of this correction;
its metric-raised response is constitutively valid while its formative writer
remains absent. A/C operator and transition results remain conditional
mathematics rather than discarded work.

```text
A.H4_upstream_effect = requires_geometry_parametric_closure_audit
C.H4_upstream_effect = requires_geometry_parametric_closure_audit

global_structural_disposition =
  H4_interface_frozen_affine_reference_profile_family_conditionally_admitted_
  D7Gv2_embedding_parametric_and_handoff_closure_required
```

D7G-v1 acceptance authorizes the append-only next gate:

```text
D7G-v2 = A/C geometry-parametric closure under H_profile
```

It must preserve geometry/mobility factorization and the lagged
`J_C[k] -> j[k] -> K_4[k] -> h_4+[k] -> later transition` stage. A profile
change reopens an earlier gate only if it leaves the admitted class, changes
state/write authority or same-beat staging, or invalidates the declared
operator family.

D7G-v1 establishes the bounded `delta T_a -> delta K_4^a -> delta h_4`
direction for both survivors, but it does not claim the later transition
consequence before that parametric audit. D7G is incomplete, no candidate is yet
D8-comparable, and specification, implementation, runtime, stability, and
architecture-selection claims remain blocked. The authoritative records are
[`D7GGlobalMetricAndStructuralCultivationClosure.json`](./decisions/D7GGlobalMetricAndStructuralCultivationClosure.json)
and its
[`scientific report`](./decisions/D7GGlobalMetricAndStructuralCultivationClosure.md).

#### D7G-v2 Planned Geometry-Parametric Closure And Finalization

D7G-v2 must declare two different objects:

```text
H_adm = admissible geometry-state class
P_adm = admissible H_profile map class landing in H_adm
```

It must separate candidate closure over `H_adm`, profile-map sensitivity under
`D_K H_profile` or a declared nonsmooth replacement, and conclusions specific
to the conditional affine family. It must:

- define and admit exact `E_ref`, or close the affine family without
  instantiation;
- keep exact affine reference neutrality separate from complete disabled
  V4-to-V3 transition reduction;
- freeze `Delta K_4` as the primary profile input and declare `K_4,base` in the
  named profile context;
- preserve the distinction among `K_4`, physical `h_4`, transport mobility
  `M_4`, and A's `W_A` authority through an explicit current factorization;
- preregister quantitative uniform bounds for `lambda_min(H_1)`,
  `lambda_max(H_1)`, C's selector gap, `cond(I_4M)`, and each D6 current-closure
  regularity margin;
- show whether A's D5 operator, D6 regularity argument, and D7 writer/state law
  remain well typed and regular over `H_adm`;
- for C, define `P_M(h)`, `H_M(T_C,h)`, `I_4M(h)`, and `R_C(h_M)` on a declared
  SPD subdomain with explicit spectral-gap, conditioning, and regularity bounds;
- preserve the accepted `J_C[k] -> j[k] -> K_4[k] -> h_4+[k]` order only as
  the selected lagged explicit realization under audit, not as a general V4
  temporal requirement;
- distinguish supplied pre-read sensitivity `D_(h_pre) F_a` from generated
  geometry sensitivity through `Gamma_a` or another complete realization;
  absent `Gamma_a` makes the latter undefined, not zero;
- for C, distinguish nonzero internal-map derivatives, nonzero current
  sensitivity, and nonzero full-transition sensitivity; do not promote one
  level to the next without the complete downstream chain or a matched witness;
- ready a non-exhaustive minimum pressure set covering coupled/implicit,
  operator-split same-beat, persistent carrier, and reconstructed geometry;
  cache history is forbidden, and failure of those four does not establish V4
  impossibility without a separate completeness proof;
- distinguish graph-local assembly from inverse, identification, solver, and
  causal support;
- emit a geometry-parametric equivalence receipt, bounded profile-specific
  receipt, named earlier-gate reopening, or terminal disposition for A and C;
  and
- admit a candidate to full D8 continuation comparison only after `delta h_4`
  has a declared later transition consequence under the corresponding receipt;
  bounded D8-A structural-target extraction may proceed earlier when it derives
  a branch-appropriate continuation object and does not repeat the known absent
  `Gamma_a` diagnosis.

D7G-v2 also owns D7G profile/stage finalization. It classifies the
per-candidate `delta T_a -> delta K_4^a -> delta h_4` chain, separates its
branch-appropriate structural consequence from complete temporal realization,
and emits the current D7G disposition for A and C. Missing generated-geometry
feedback in the selected lagged explicit realization does not terminally close
candidate-local A/C theory, impose a cross-beat handoff on V4, or prove a hard
global blocker. These results are not written back as unfinished D7G-v1 tasks.

##### D7G-v2 Formal Pre-Acceptance Protocol (`D7G-v2-PREACCEPT-v1`)

D7G-v2 is audited as a formal closure gate, not by another undifferentiated
pressure list. The audit order is fixed:

```text
1. definitions and load-bearing symbol/noun registry
2. quantifiers, domains, norms, constants, and uniform bounds
3. H_adm geometry-state / P_adm profile-map separation
4. exact reference and K_4,base definition closure
5. causal beat/state graph and selected temporal realization
6. Candidate A proof or bounded receipt
7. Candidate C proof or bounded receipt
8. per-candidate causal non-erasure / structural-target-versus-realization consequence
9. authority mutation and earlier-gate reopening audit
10. reference neutrality / complete reduction separation
11. claim-word audit
12. debt lineage, machine integrity, and canonical digest
```

The symbol registry must state type, space, units/gauge, owner, independent or
derived status, evaluation stage, serialization or deterministic
reconstruction rule, runtime causal consumers, and analysis consumers where
applicable for every load-bearing object. Analysis access must not be relabeled
as runtime causal consumption. At a minimum it covers `H_adm`, `P_adm`, profile
`context`, `E_ref`, `K_4,base`,
`Delta K_4`, `M_4`, `H_1(h)`, `P_M(h)`, `I_4M(h)`, `Gamma_a`, `S_H`, and the
branch-appropriate structural continuation object.

Every use of `all`, `any`, `uniform`, `bounded`, `admissible`, `equivalent`,
`regular`, `stable`, `preserves`, `same`, `exact`, `later`, or
`profile-invariant` must bind a set, norm, constant, and independence scope as
applicable. If a uniform result is unavailable, D7G-v2 emits a bounded
profile-specific receipt rather than enlarging `H_adm` until both candidates
pass.

The acceptance rule is fail-closed:

> Every load-bearing statement must trace to an exact definition, a derivation
> or reproducible witness, an explicitly bounded assumption/profile
> restriction, or a named open debt that the claim ceiling does not consume.

D7G-v2 does not optimize for placing both A and C into full D8 continuation
comparison. An asymmetric result such as geometry-parametric A closure and
profile-specific C closure is valid when that is what the evidence supports.

After D7G-v2 acceptance, newly discovered work must be named either
`D7G-post-v2` or an earlier-gate reopening. The plan does not reopen an accepted
barrier merely to complete a task that belonged to a later tranche.

Profile variation within `H_adm` is reevaluation of the same constitutive
family. It is not an automatic D4-D7 restart. Earlier reopening is reserved for
changed authority, changed same-beat staging, or invalidated operator families.

#### D7G-v2 Implementation Result

D7G-v2 executed the complete 12-pass pre-acceptance protocol and was accepted
bounded on 2026-08-24 under record `GRC9V4-CD-D7G-v2`, decision digest
`c52912d83797ee294799709b3e770574043df37f80073b51eebfaf8b2fd27efb`.

The gate admits a revision-specific reference embedding:

```text
H_0,ref = diag(V3 positive quadrature weights)
H_1,ref = diag(W_V3^-1)
B_ref   = oriented live-edge incidence
```

The edge convention consumes B1-GR's primary native constitutive metric and
does not relabel the regularized runtime `geometric_length` diagnostic as the
exact embedding. The affine graph-Hodge family is therefore instantiated as a
bounded V4 profile, not inherited as baseline V3 physical `h_4` and not
promoted to a unique core `g[K]`.

Candidate A retains bounded D5-D7 regularness over supplied admitted geometry
while `W_A` remains the sole transport-mobility authority. Candidate C closes a
bounded theorem-shaped supplied-geometry domain with positive `H_1`, positive
`H_1,M`, strict selector gap, finite `I_4M` condition, retained-response bound,
and positive D6 margin. These results close profile mathematics, not the full
causal chain.

The accepted A transition writes `C[k+1]` and `W_A[k+1]` without consuming
postsolve `h_4+[k]`. The accepted C transition commits only `C[k+1]` and cannot
reconstruct prior postsolve `h_4+[k]` from that poststate. Consequently the
selected lagged explicit realization has no `Gamma_A` or `Gamma_C`:

```text
delta T_a -> delta K_4^a -> delta h_4 -?-> delta F_a,later
```

The generated-geometry derivative is undefined under that factorization, not
zero. It is distinct from supplied pre-read sensitivity. C has load-bearing
supplied geometry and conditionally nonzero dependence in named internal maps,
but nonzero `D_(h_pre) J_C` and nonzero `D_(h_pre) F_C` remain unproved because
downstream annihilation, cancellation, or divergence-free response have not
been excluded. A's receipt is an invariance/type-regularness result and has not
made supplied geometry load-bearing. This does not terminally close either
candidate.
A and C both receive:

```text
candidate-local transition valid
geometry-parametric regularness valid
selected lagged explicit geometry feedback unresolved
```

Human acceptance authorizes D8-A to
derive each branch-appropriate continuation object and classify each target as
realization-invariant, accepted-lagged-branch-relative, or not finalizable
before temporal realization. Only invariant targets constrain every successor;
lagged-branch targets require D8-B rederivation if the slaving relation changes.
D8-A may not assume one common self-adjoint Hessian, promote C internal-map
sensitivity into full-transition sensitivity, count the known absent `Gamma_a`
as new evidence, or count its analysis access as runtime causal consumption.

The scope-classified targets then constrain
`GRC9V4-GEOMETRY-TEMPORAL-REALIZATION-SUCCESSOR`. Its `S_H` interface is only a
start: the successor must instantiate and pressure at least one bounded
complete step while treating coupled/implicit, operator-split, persistent, and
reconstructed forms as a minimum, non-exhaustive pressure set. Failure of all
four requires broader search or bounded unresolved closeout unless the family
classification is independently proven complete. A and C receive the same
burden of proof but need not share an equation. Core theory need not uniquely
select one, and convenience cannot select one. Cache-only history and
least-incomplete candidate selection remain blocked. The authoritative records are
[`D7Gv2GeometryParametricClosureAndFinalization.json`](./decisions/D7Gv2GeometryParametricClosureAndFinalization.json)
and its
[`scientific report`](./decisions/D7Gv2GeometryParametricClosureAndFinalization.md).

### D7G-post-v2 Graph-Hodge Type Correction (Accepted Bounded)

The jointly accepted narrow correction receipt
separates the structural one-form Hodge `H1_form`, the current/flux flat metric
`G_J`, and transport mobility `M4`. The correction preserves accepted
historical bytes and dispositions, retags Candidate C's physical response as
an explicit flux/flat/response/sharp/flux chain, and requires exact source
identity, energy-duality, rank-one tensor-separation, and witness-recalculation
checks. It also freezes physical `j_flux` as the continuity current and lowered
`j_struct^flat` as the structural input to
`j_struct^flat tensor j_struct^flat -> K4`. General nonidentity conditioning,
richer graph-DEC edge-volume factors, topology transport, and normative
encoding remain typed debt. The correction is authoritative for D8-A and
future consumers but does not authorize runtime work.

## D8. Continuation Realization And Analysis Contract

Status: D8-A is accepted bounded and the named geometry-temporal-realization
successor is authorized. D8-B full continuation comparison remains blocked on
an instantiated complete geometry-temporal realization.

### D8-A. Branch-Appropriate Structural-Target Extraction

For A and C, first derive the branch-appropriate structural continuation object
under the accepted D6 closure. Do not assume one common self-adjoint Hessian:

```text
smoothly slaved branch -> reduced self-adjoint Hessian may be admissible
active/joint branch    -> joint, nonselfadjoint, or DAE object may be required
```

Then extract admissible directions `v` for which the derived structural object
responds to `delta h_4` and classify each as realization-invariant,
accepted-lagged-branch-relative, accepted-lagged-branch work not yet
instantiated, or genuinely not finalizable before temporal realization. Only
invariant directions become universal non-erasure
requirements. If the successor changes the slaving relation, lagged-branch
directions must be rederived in D8-B before they constrain that realization.

D8-A must keep these derivatives separate:

```text
D_(h_pre) F_a
D_(h_generated) F_a,later through Gamma_a or an equivalent realization
```

The second is currently undefined, not zero. Recomputing the already known
absence of `Gamma_a` is not a D8-A result. For C, nonzero derivatives of
internal maps do not establish nonzero `D_(h_pre) J_C` or `D_(h_pre) F_C`
without a complete chain derivation or matched witness. D8-A is an analysis
consumer of `h_4+`, not a runtime causal consumer.

#### D8-A Accepted-Bounded Result

D8-A binds Candidate A to D3's conditional-C-given-`W_A` smoothly slaved row
and Candidate C to D3's C-only exact-derived-sector smoothly slaved row. It
derives separate reduced constrained second-variation forms; it does not assign
either candidate a joint retained-state or independent-current structural
coordinate.

The D7G-post-v2 correction resolves a source-level type conflation. D5's
`H1` is the structural one-form Hodge/Gram weight used by the scalar
Dirichlet form, while B1-GR's inverse-conductance object is the dual metric and
flat map on physical edge currents. Transport mobility remains a third,
causally distinct object:

```text
H1_form,ref = diag(W_V3)
G_J,ref     = diag(W_V3^-1)
M4          = candidate/realization-owned transport mobility.
```

Numerical coincidence between `H1_form,ref` and legacy mobility does not merge
their authority. Candidate C therefore uses an explicit
`flux -> flat -> Hodge response -> sharp -> flux` pipeline. Its existing
identity-metric D5-v2/D6-v2 witness survives within binary roundoff, while
general nonidentity conditioning remains pre-D10 debt.

The corrected path branches before sharp. Continuity consumes `j_flux`, while
structural assembly consumes the lowered Read-Back one-form:

```text
A: j_A,flux -> G_J,pre -> j_A,struct^flat -> K4_A
C: retained response -> j_C,struct^flat -> K4_C
                             |
                             +-> G_J,pre^-1 -> j_C,flux for continuity.
```

The candidate-generated tangent is generally

```text
delta j_struct^flat
  = (delta G_J) j_flux + G_J delta j_flux.
```

The accepted lagged rows freeze pre-read geometry, so their
`delta G_J,pre` term is zero. Coupled or implicit successors must retain that
term when `G_J` varies inside the reflexive chain.

Candidate-specific structural scaling is unchanged:

```text
Delta K4^a = iota_a(A_star(j_a,struct^flat)).
```

`iota_a` is each candidate's already accepted typed structural adapter and
gain, not a new common `kappa_K`. The same type rule applies to B only if B is
later reopened with a separately admitted current-mediated path and `iota_B`.

Under that typed correction, the direct field response to the affine
structural profile is exact. With `d0 = B_ref^T`:

```text
Q_field,h[u,v]
  = kappa_C (d0 u)^T H1_form (d0 v)
  + u^T H0 diag(W_pot''(C_star)) v

delta H1_form = kappa_H delta K4

D_H1_form Q_field[delta H1_form](u,v)
  = kappa_C (d0 u)^T delta H1_form (d0 v).
```

Here `W_pot` is the core local structural potential, not Candidate A's `W_A`.
The `H0`-weighted matrix representative includes the same `kappa_C` factor,
and target orthogonality is taken in the declared `H0`-weighted candidate
structural inner product. A successor that changes the structural-Hodge
profile, graph-DEC edge-volume factors, or flux/form identification must
rederive the affected response. It may not substitute `G_J` for `H1_form` by
symbol or array shape.

This is a structural target, not a complete Hessian or runtime feedback result.
`delta K4 != 0` does not ensure a nonzero constrained target: the pullback may
lie in an exact-gradient, constraint, gauge, or branch-specific kernel. The
full induced-geometry and constraint second variations also remain open.

D8-A classifies ten target rows:

```text
realization-invariant structural targets = 4
accepted-lagged-branch targets = 2
accepted-lagged-branch structural targets not instantiated = 2
not finalizable before temporal realization = 2
```

The invariant rows preserve the conditional direct field metric response,
metric-aware
conservation tangent, A conditional-coordinate boundary, and C exact derived
sector tangent. The candidate-generated A/C pullbacks through accepted D6-v2
slaving and the typed `delta j_flux -> delta j_struct^flat -> delta K4`
crossing are lagged-branch-relative and require D8-B rederivation if the
successor changes slaving, metric timing, or stage. The full
accepted-lagged-branch Hessian and
its `alpha` spectrum are potentially derivable before temporal synthesis, but
D8-A does not instantiate them; they become architecture-final only when the
successor preserves that slaving and typed structural-Hodge/current-metric
dictionary. Generated-
geometry runtime sensitivity and temporal generators remain genuinely not
finalizable before a complete temporal realization.

The authoritative records are the
[`D7G-post-v2 graph-Hodge type correction`](./decisions/D7GPostv2GraphHodgeTypeCorrection.json),
its
[`interpretation`](./decisions/D7GPostv2GraphHodgeTypeCorrection.md),
[`D8ABranchAppropriateStructuralTargetExtraction.json`](./decisions/D8ABranchAppropriateStructuralTargetExtraction.json)
and its
[`scientific interpretation`](./decisions/D8ABranchAppropriateStructuralTargetExtraction.md).
Joint accepted-bounded status authorizes only the named geometry-temporal
realization successor. It does not authorize D8-B or any runtime work.

### Geometry-Temporal Realization Successor

After accepted D8-A, freeze `S_H` as a common interface and common burden of
proof, then pressure at least these four concrete realization families equally:

```text
coupled/implicit:
  existence, uniqueness, complete B_eff chain rule, fixed-point regularity

operator-split same beat:
  ordering, conservation, splitting error, atomicity

persistent structural carrier:
  D1 authority, writer, lifecycle, reset, serialization

reconstructed geometry:
  exact reconstructibility, no lost J-dependent information, Markov closure
```

Admission of a concrete realization to D8-B requires its complete equations,
state authority, stage order, fixed-stratum Markov closure,
conservation/accounting, design covariance, failure semantics, bounded local
well-posedness/regularity, and a declared linearization surface. It must also
declare disabled behavior, lifecycle requirements, and the later stability
analysis surface. Exact disabled V4-to-V3 reduction remains D9 debt, full
topology/event lifecycle remains D9 debt, and stability classification remains
D8-B work. Requiring those later results before admission would be circular.

The implicit family must receive serious treatment because the core effective
loop already admits algebraic `J -> j -> K -> h -> J0 -> J` dependence. It may
require a D6 successor; that is a new constitutive solution, not a correction
of accepted D6.

The four families are a non-exhaustive minimum pressure set. The successor
cannot close with an interface-only result and must instantiate and pressure at
least one bounded complete realization. Failure of all four is not a V4
impossibility without a separate completeness proof; otherwise the search must
broaden or return a bounded unresolved result. The common `H_profile` does not
force A and C to use identical temporal equations. Candidate neutrality means
the same acceptance criteria and burden of proof.

#### First Family Pass: Coupled/Implicit

The successor begins with the coupled/implicit family because D6 already
supplies an accepted regular current reference and the core effective loop
admits same-solve `J -> j -> K4 -> h -> J0 -> J` dependence. This ordering is
not an architecture preference.

For Candidate C, freeze the algebraic unknown `Y_C = (J_C,flux, h_C)`. The
intrinsic retained response, causal read, physical current, and structural use
are distinct:

```text
r_C^flat
  = I_4M(T_C,h)^-1 Rhat_C,M(T_C,h) I_4M(T_C,h) G_J(h) J_C,flux

j_C^flat = chi_C r_C^flat
j_C,flux = G_J(h)^-1 j_C^flat

Delta K4_C = zeta_C iota_C(A_star(j_C^flat)).
```

`Rhat_C,M = (I + tau_C Delta_1,M)^-1` is explicitly ungated. Historical D5-v2
notation with `chi_C` inside `R_C,M` is not used by this successor.
`chi_C` therefore gates the explicit read and its structural branch. `zeta_C`
gates both causal uses exactly once as an external multiplier and is not
inserted inside `j_C^flat` or `iota_C`. No adapter homogeneity is assumed.
`I_4M(T_C,h)` exposes the complete
`h -> P_M -> T_C -> H_M -> I_4M` derivative chain. Solve

```text
F_J,C
  = J_C,flux
    - J0_C(C_k,T_C,h_C,context)
    - zeta_C j_C,flux(J_C,flux,h_C)
  = 0

F_h,C
  = h_C
    - H_profile(
        K4_base + Delta K4_C(J_C,flux,h_C),
        h4_ref,
        context)
  = 0.
```

Only physical flux enters continuity. Candidate-specific `iota_C` remains the
typed structural adapter and excludes the shared `zeta_C`. The same-step `J`
and `h` variables do not become persistent state.

At `kappa_H = 0`, define

```text
Q_C,ref = I_4M(T_C,ref,h4_ref) G_J(h4_ref)

L_C,flux,ref
  = Q_C,ref^-1
    (I - zeta_C chi_C Rhat_C,M,ref)
    Q_C,ref.
```

The physical block is exactly similar to the accepted retained D6-v2 block,
so invertibility transfers. The old physical singular-value margin does not.
Robust physical conditioning additionally requires finite `cond(Q_C,ref)` and
a new inverse bound. The reference root derivative is

```text
[ L_C,flux,ref  B_C ]
[       0        I  ].
```

On the fixed stratum, `h` is represented by the independent symmetric
coordinates of `H1_form` in the declared oriented-edge basis. `H0`, incidence,
boundary, and live order are fixed; `G_J` and candidate operators are derived
rather than independent root coordinates. The residual is therefore square in
a local SPD chart.

The implicit function theorem therefore admits a unique local smooth coupled
branch for sufficiently small `|kappa_H|`. This is a local existence and
uniqueness result, not a numeric radius, global branch, or stability result.
This is a revision-distinct C successor to D6 staging, not a correction of
accepted D6-v2. C keeps its D7 state authority but jointly solves current and
geometry before continuity, so D8-A's lagged targets require D8-B rederivation.

Away from the reference point, the authoritative regularity object is the full
`(J,h)` block. It must retain every active derivative through `P_M`, `T_C`,
`H_M`, `I_4M`, `Rhat_C,M`, `G_J`, flat/sharp, `K4`, and `H_profile`. In particular,
`(delta G_J) J` cannot be dropped. A current-only Schur complement is valid
only after its geometry pivot is separately proved regular.

The later architecture-local D8-B linearization surface is

```text
D_X Y_C = -B_full,C^-1 D_X F_C,
```

composed with continuity and the C commit map. `kappa_H = 0` returns the
accepted D6-v2 C root, not the complete V3 transition; full disabled reduction
and topology/event lifecycle remain D9 debt.

Candidate A receives the same family burden. D4 already separates structural
geometry from retained mobility while admitting both as typed inputs to
baseline transport, and D7 freezes the reference baseline and writer. The
successor therefore defines a reference-relative geometry consumer:

```text
Delta_0(h) = H0,ref^-1 B H1_form(h) B^T

Phi_A^CI
  = Phi_A^D7
    + kappa_Ah [Delta_0(h) - Delta_0(h_ref)] C

M4_A = eta Diag(W_A)
J0_A^CI = -M4_A d0 Phi_A^CI.
```

`W_A` remains the sole mobility owner. At `h = h_ref`, the correction vanishes
and the accepted D7 baseline returns exactly. The existing `G_W`, `q_A`,
directional read, structural adapter, continuity, and postsolve D7 writer are
preserved. Generated geometry has no direct writer authority; it acts through
the baseline current, authoritative total current, and continuity.

Freeze

```text
[kappa_Ah] = [Phi_A] / ([Delta_0] [C])
enabled kappa_Ah = +1.0 in that declared unit basis
ablation kappa_Ah = 0.
```

The enabled value is preregistered before D8-B, not selected to optimize
visibility or stability; its sign is a profile convention rather than a
theory-fixed sign. `W_hat_A(h) = G_W(C,J0_A^CI(h))` is recomputed inside every
joint-root residual evaluation after `J0_A^CI(h)` and before `q_A`. “Pre-read”
describes this internal order, not evaluation outside the root. A's structural
increment is `Delta K4_A = zeta_A iota_A(A_star(j_A^flat))`.

The A root uses `Y_A = (J_A,flux,h_A)` and the same current/geometry residual
shape as C with A-specific maps. At `kappa_H = 0`, its reference block is
`[[L_A,B_A],[0,I]]`; the accepted
`sigma_min(L_A) >= 1-zeta_bar_A > 0` bound supplies a local IFT branch on the
smooth chart where the `G_W` floor is inactive. Away from the reference, the
complete derivative must retain
`h -> Delta_0 -> Phi_A^CI -> J0_A^CI -> W_hat_A -> q_A -> j_A -> K4 -> h`.
The reference-relative profile is a minimal revision-specific completion, not
a unique core-theory or normative V4 law.

Every admitted branch point is classified by the D8-A projected visibility
test. A point may be a lawful complete root while lying in the direct
structural target kernel. Nonzero `Delta K4` alone does not establish a
nonzero constrained continuation target. This pass closes the instantiated
branch obligation with two formal constitutive receipts:

```text
C D5-v2 selected-minus-base star receipt:
  (d0 u)^T delta A_star (d0 u) = -0.014842807194071116

A admitted q/J star receipt:
  (d0 u)^T delta A_star (d0 u) = 0.41999999999999993
```

Both use the connected three-node path. Accepted non-erasing adapters and
nonzero profile gains preserve a nonzero metric variation; exact-gradient
tangents span the full two-edge form space, so an admissible post-adapter
projected pair exists. These are direct-field visibility receipts, not runtime,
full-chain, Hessian, or stability evidence.

The provisional result is recorded in
[`GeometryTemporalRealizationSuccessorCoupledImplicit.json`](./decisions/GeometryTemporalRealizationSuccessorCoupledImplicit.json)
and its
[`scientific interpretation`](./decisions/GeometryTemporalRealizationSuccessorCoupledImplicit.md).
It is accepted bounded. Candidates A and C are separately authorized for
architecture-local D8-B rederivation. Comparative D8-B and successor-family
closeout remain blocked on the other realization families or an explicit
contract revision.

### D8-B. Full Continuation Analysis And Comparison

Architecture-local D8-B is authorized for coupled/implicit A and C. Comparative
D8-B remains blocked until the minimum realization-family pressure is complete
or an explicit contract revision closes that obligation. Local analysis must
not be relabeled as cross-candidate or cross-family comparison.

Where meaningful, compare A and C under a matched realization family. If their
ontologies justify different realizations, treat each `(candidate,
realization)` pair as an architecture and identify realization effects
separately from candidate effects.

Within the later authorized scope, keep four objects separate:

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

D8 must map every D7G-admitted candidate's V4 operators to applicable B1/B2
discriminators and identify which tests can be reused after implementation,
which require a
V4-specific adaptation or rederivation because the causal object changed, and
which are inapplicable. Recreating GRV3/GRV4/GRV7 unchanged as design prose is
not new evidence and does not close D8.

#### D8-B Coupled Architecture-Local Result

The coupled/implicit A and C pass is recorded in
[`D8BCoupledArchitectureLocalContinuationAnalysis.json`](./decisions/D8BCoupledArchitectureLocalContinuationAnalysis.json)
and its
[`scientific interpretation`](./decisions/D8BCoupledArchitectureLocalContinuationAnalysis.md).
It is accepted bounded.

The pass derives the complete architecture-local implicit first and second
derivative surfaces for each accepted coupled root. It uses those surfaces to
define the charge-parametric architecture-local structural second variation,
complete once D9 freezes the conserved charge and tangent, plus the committed
state Jacobian, direct Read-Back response operator, spatial graph operator,
cluster/projector transport, covariance, nonnormality, and stability tests.
Candidate A remains conditional C structure at fixed `W_A`; Candidate C
remains C-only with an exact derived selector tangent. Neither `W_A`, `T_C`,
`J`, nor `h` receives a new structural or persistent-state authority.

Classical second variation is admitted only on declared `C2` subcharts; the
accepted `C1` implicit-function result is not overpromoted into a Hessian. The
field contribution is instantiated from the graph functional, including first
and second geometry-slaving terms. The structural tangent must be bound to the
actual conserved charge of the complete V4 transition, which remains explicit
D9/pre-D10 debt rather than being inferred from `H0` or legacy GRC9V3.

The primary temporal object is the complete discrete multiplier map
`M_a = D_X Phi_a`; moving branches require a transported cocycle rather than
one permanent spectrum, with the output transported from `k+1`, not `k`. A
continuous `gamma` requires a declared clock and logarithm branch or a
separately derived generator. Intrinsic response `r_a`
is separated from enacted Read-Back gain `beta_a = zeta_a r_a`; `beta` remains
spectral while direct-response singular values are reported separately.
Structural `alpha`, temporal `mu`/`gamma`, direct `beta`, retained-sector
`lambda_M`, and formed-geometry spatial `lambda` remain separate. The B1/B2 methods are
classified for reuse or V4 adaptation; their V3 numerical results are not
consumed as V4 evidence.

No formed V4 constrained critical branch, normalized functional parameter set,
or numerical root derivative is instantiated by the accepted design sources.
The pass therefore emits no numeric spectrum and makes no temporal or
structural stability claim. The existing A and C direct-field receipts do not
close complete-chain nonannihilation. Those are bounded results, not missing
rows to be filled with V3 values or partial graph-Hodge proxies.

The complete predecessor live-debt union is dispositioned: 10 immediate
coupled-successor debts plus 23 transitive D8-A debts. Equation-level
architecture-local rederivation is closed; seven successor debts preserve
formed-branch alpha, temporal stability, comparative reference-space work,
complete-step charge/projector selection, and Candidate A analysis-metric
selection.
Comparative D8-B remains blocked.

#### Remaining Realization-Family Pressure

D8-B acceptance does not route directly to D9. The next substantive work is
the minimum pressure on the three realization families still open in the
accepted coupled-successor contract, followed by comparative realization
synthesis:

```text
GTRS-OS  operator-split same-beat
GTRS-RG  reconstructed geometry
GTRS-PC  persistent structural carrier
GTRS-COMP comparative realization synthesis
```

This order minimizes unnecessary new state authority; it is not an
architecture ranking. Operator-split is the closest causal alternative to the
accepted coupled root. Reconstructed geometry then tests whether existing
authoritative state suffices without a new carrier. Persistent carrier is last
because it adds lifecycle, serialization, reset, and migration obligations.

For each family and Candidate A/C row, ask only whether the family can produce
a bounded complete step from the already derived candidate-local constitutive
content. Freeze one disposition:

```text
bounded_complete_realization
candidate_local_blocker
family_level_obstruction
bounded_unresolved
```

A successful row must provide exact equations, state authority, stage order,
accounting/conservation, atomic failure behavior, covariance, disabled
behavior, and a declared architecture-local linearization surface. It must
show at minimum that the geometry-producing substage is an explicit
equation-level input to a later complete-step substage. A nonzero complete-
state effect is a separate witness obligation. Endpoint coverage, interface
compatibility, or a nonzero intermediate geometry value is insufficient.

Family pressure does not rerun D8-A and does not require numerical `alpha`,
`mu`, or `gamma` before admission. Once a family yields a bounded complete
realization, derive only enough architecture-local operator and representation
semantics to make later comparison lawful. Numerical spectra and stability
remain a separate evidence decision. D8-B's still-open charge, complete-chain,
conditioning, global-root, and event debts do not block this family pressure.

##### GTRS-OS: Operator-Split Same-Beat

Pressure an ordered within-beat realization of the accepted A/C maps against
the coupled root. The preregistered primary realization is one predictor,
one geometry update, one fixed-geometry corrector, and one atomic commit:

```text
X_k
  -> J^(0)
  -> j_flat^(0)
  -> Delta K4^(0)
  -> h^(1)
  -> J^(1)
  -> X_(k+1)
```

`J^(1)` may not feed a second geometry update in this primary row. Any second
predictor/corrector pass or alternative stage order is a separately named
successor realization, not a repair made after observing this row.

For C, `J_C^(0)` is the accepted fixed-geometry C current at `h_ref`. It
produces `j_C^flat,(0)`, `Delta K4_C^(0)`, and `h_C^(1)`. At fixed
`h_C^(1)`, recompute the entire C geometry-dependent selector,
identification, response, baseline-current, and current-closure construction
and solve `J_C^(1)`. Only `J_C^(1)` enters continuity.

For A, `J_A^(0)` is the accepted A reference current at `h_ref`. It produces
`h_A^(1)`. At fixed `h_A^(1)`, use the admitted reference-relative consumer

```text
Phi_A^OS
  = Phi_A^D7
    + kappa_Ah [Delta_0(h_A^(1)) - Delta_0(h_ref)] C,
```

then recompute `J0_A^OS -> W_hat_A -> q_A`, solve `J_A^(1)`, and run the
unchanged continuity and D7 writer stages.

Freeze the split-consistency diagnostic

```text
h_hat^(1)
  = H_profile(K4_base + Delta K4(J^(1), h^(1)))

r_h^OS = h^(1) - h_hat^(1).
```

Because the corrector solves the accepted fixed-`h^(1)` current equation
exactly, freeze the stronger coupled-equation identity

```text
F_a^CI(J_a^(1),h_a^(1)) = (0,r_h,a^OS).
```

The operator split is therefore exactly current-consistent with the coupled
constitutive equations; its sole coupled-equation residual is the deliberately
unclosed final-current geometry fixed point.

The coupled root has zero residual by construction. A nonzero one-pass
residual is not automatically a failed realization; it must remain explicit,
bounded on the admitted chart, and compatible with the complete step's causal,
accounting, and atomicity contracts. Do not assume `r_h^OS = O(Delta_t)`.
Pressure `r_h^OS(Delta_t, kappa_H)` and `Psi^OS - Psi^CI` independently. Any
small-coupling order must be derived from the declared maps and regularity
bounds, not imported from time-integrator terminology.

Use the relative Hodge operator norm

```text
||delta h||_(H1,ref)
  = ||H1_form,ref^(-1/2)
       delta H1_form
       H1_form,ref^(-1/2)||_2.
```

Keep the common structural and Hodge spaces dimensionally distinct:

```text
S_a(J,h) = Delta K4_a(J,h) in K_4
P_0 = (1/kappa_H) D_K H_profile : K_4 -> T_h H1_form
G_a,kappa(J,h) = kappa_H P_0[S_a(J,h)] in T_h H1_form
g_0 = ||P_0||_(K->H)
g_H = |kappa_H| g_0.
```

Use a reference-scaled operator norm `||.||_K` on the accepted common `K_4`
coordinate/unit basis. Never apply the relative `H1_form` norm directly to
`S_a`; only its typed profile push-forward is geometry-valued.

On A's D8-B floor-inactive `C2` chart and C's fixed-rank, strict-gap `C2`
chart, write `J=C_a(h)`, `S_a(J,h)=Delta K4_a(J,h)`, and
`M_S=||S_a(J^(0),h_ref)||_K`. If `C_a` and `S_a` have local Lipschitz
constants `L_C` and `L_S` in the declared current and geometry norms, require
the exact bound

```text
||r_h^OS||_(H1,ref)
  <= |kappa_H|^2 g_0^2 L_S M_S (1+L_C)
   = g_H^2 L_S M_S (1+L_C).
```

For `T_a(h)=P_0[S_a(C_a(h),h)]`, let
`M_G=||P_0[S_a(J^(0),h_ref)]||_(H1,ref) <= g_0 M_S`. If
`|kappa_H| L_T < 1`, also freeze

```text
||h_star-h^(1)||_(H1,ref)
  <= |kappa_H|^2 L_T M_G
     / (1-|kappa_H| L_T).
```

These statements establish a conditional local quadratic coupling defect and
matched coupled/split order. They do not cross nonsmooth stratum boundaries
and are not numeric or uniform envelopes.

Freeze this substage order before seeing outcomes and test:

```text
explicit same-beat feedback versus implicit feedback
substage authority and atomic commit
conservation/accounting at every substage and complete beat
splitting error and step-size dependence
whether generated geometry is consumed by a later substage in the same beat
whether ordering changes the candidate ontology or only its realization
```

No producer-authored correction may hide the splitting error or restore a
failed conservation result after the fact. `chi_a = 0` and `zeta_a = 0` retain
their accepted switch semantics; generated geometry must be an explicit input
to the `J^(1)` equation rather than merely be emitted. This equation-level
consumer does not establish a nonzero complete-state effect. The future exact
witness surface is

```text
D_h J_a^(1) = -(D_J F_J,a)^(-1) D_h F_J,a.
```

A retains `W_A` as mobility authority and its D7
writer, C retains derived `T_C`, cache or solver-history authority is
forbidden, and failure in any substage commits nothing. Comparison with the
coupled root is a realization-effect comparison, not candidate ranking.

##### GTRS-RG: Reconstructed Geometry

Test whether the needed structural surface is exactly and deterministically
reconstructible from already-authoritative candidate state and declared
same-step inputs. Require:

```text
no independent geometry authority
no hidden cache, solver-history, RNG, or prior-step receipt
no loss of load-bearing J-dependent information
same complete authoritative state, inputs, and admitted local branch imply the
same reconstruction; global root uniqueness is not assumed
reconstruction remains Markovian and covariant
```

Freeze reconstructed geometry as a *distinct realization family* before
pressure. For candidate `a`, let

```text
X_a,k = authoritative committed state
U_k   = declared same-step boundary/context and fixed constitutive
        chart/equivariant root-selection profile configuration
C_a(h;X_a,k,U_k) = accepted fixed-h current solution
S_a(J,h) = accepted K_4-valued structural map.
```

A direct reconstructed family would require a deterministic map

```text
R_a : (X_a,k,U_k) -> h_a
```

that preserves the accepted `J`-dependent structural information without new
persistent geometry authority. Classify rather than hide these cases:

```text
R_a solves h = H_profile(K4_base + S_a(C_a(h),h))
  -> coupled/implicit semantics, regardless of closed-form or solver algorithm

R_a evaluates one or more frozen-current predictors before a corrector
  -> operator-split semantics; each new stage order is a named OS successor

R_a uses prior-step current, cache, receipt, RNG, or solver history
  -> invalid hidden authority

R_a omits current information or substitutes a report/diagnostic proxy
  -> loses the accepted J-dependent structural path
```

Reconstruction after `X_(k+1)` commits cannot establish same-beat geometry
consumption, but it is a lawful candidate for next-beat use. Freeze that case
separately. For admissible execution `E`, let

```text
Phi_a(E) = X_a,k+1
G_a(E)   = h_a,k+.
```

Exact no-new-state next-beat reconstruction exists only when

```text
G_a = R_a+ o Phi_a,
```

equivalently when `G_a` is constant on every fiber of `Phi_a` with next-beat
inputs fixed. A positive local result may instead prove `D Phi_a` invertible
on a named chart and construct `R_a+ = G_a o local_inverse(Phi_a)`. A negative
differential result may exhibit `v in ker(D Phi_a)` with `D G_a[v] != 0`.
Apparent noninvertibility, dimension counting, or a cycle-space direction not
shown reachable by the constitutive map is pressure, not evidence.

A fixed constitutive chart or equivariant root-selection rule may be profile
configuration. Previous root, previous geometry, solver continuation state, or
a per-step dynamic branch token may not enter `U`. Any lawful `R_a+` and any
selected inverse branch must be graph-relabeling and reorientation covariant.

The pressure may therefore find that deterministic reconstructibility is a
state-ownership property already satisfied by an admitted CI or OS map rather
than a third temporal realization family. Such a result is a family-level
classification, not a rejection of reconstruction or of future candidates
whose geometry is source-backed as a direct function of committed state.

The earlier failure to reconstruct old postsolve `h+` from lagged committed
state is historical pressure, not an impossibility result for these new
architecture-specific maps.

GTRS-RG-v1 applies the same-beat partition to A and C. For both candidates,
exact information-preserving reconstruction is constitutively equivalent to
the coupled fixed point; staged reconstruction is operator-split. A closed-form
state-only evaluator may exist and remains CI-equivalent when exact. The RG-1
row dispositions are:

```text
A distinct reconstructed-geometry family = family_level_obstruction
C distinct reconstructed-geometry family = family_level_obstruction
```

Same-beat reconstruction is therefore a state-ownership property of CI/OS,
not a third temporal relation.

RG-2 first establishes a local property of already-complete CI/OS steps. On
the smooth zero-duration extension, both A and C commit maps are identity: C
because continuity has no finite impulse, and A because continuity is identity
and `a_A=exp(-Delta_t/tau_A)` becomes one, leaving `W_A+ = W_A`. The inverse
function theorem therefore supplies local poststate reconstruction for small
`abs(Delta_t)`. This is not a distinct temporal family.

The distinct RG-2 architecture instead closes the original lagged step with a
fixed invariant section:

```text
h_k = Gamma_a(X_k)
J_k uses h_k
h_k+ = G_a(X_k,h_k)
X_k+1 = Phi_a,lag(X_k,h_k)

Gamma_a(Phi_a,lag(X,Gamma_a(X))) = G_a(X,Gamma_a(X)).
```

At `kappa_H=0`, `Gamma_a,0=h_ref` is an exact constant section and the section
derivative of the graph transform is zero. A merely common local image is not
a fixed Banach domain. Choose `K_minus` compactly contained in `K`, with `K`
compactly contained in the admitted chart. Freeze one equivariant family-local
extension profile completion whose maps agree exactly with the real candidate
maps on `K`, return outside a compact neighborhood to `X+=X`, `h+=h_ref`, and
require

```text
Psi_a,Gamma = identity + f_a,Gamma
Lip(f_a,Gamma) < 1
M_inverse <= 1 / (1 - Lip(f_a,Gamma)).
```

Work on one fixed complete class of bounded Lipschitz sections with value
radius `r` and Lipschitz ceiling `L_Gamma`. Use the typed profile gain

```text
epsilon_H = norm(D_K H_profile)_(K4 -> geometry)
```

and require

```text
epsilon_H M_G <= r
epsilon_H (L_G_X + L_G_h L_Gamma) M_inverse <= L_Gamma

q_a,0 <= epsilon_H [
           L_G_h
           + (L_G_X + L_G_h L_Gamma) M_inverse L_Phi_h
         ] < 1.
```

The graph transform then has a unique local Lipschitz fixed section for
sufficiently small positive `Delta_t` and `epsilon_H`; restrict it back to
`K_minus`.
`C1` regularity requires a separate derivative-graph or `C1,1` bunching result.
Apply the admission theorem only on fixed-context charts: A is floor-inactive
with positive `W_A`; C has fixed selector rank and strict gap. Time-varying
context requires explicit state augmentation. A boundary/source impulse or
unavailable exogenous input blocks the identity/factorization argument.

Also require `Psi_a,Gamma(K_minus)` to be a subset of `K`, and restrict the real
architecture claim to `K_minus`. Section uniqueness is relative to the frozen
extension completion; independence from other admissible extensions is not
claimed. The completion is profile configuration, not causal state or runtime
tuning.

This produces no simultaneous root, no same-beat corrector, and no serialized
geometry, current, cache, or branch token. Relative to the frozen extension
completion, `Gamma_a` is the uniquely derived family-local constitutive section,
not an independently authored, fitted, learned, or trajectory-updated carrier.
Therefore:

```text
A lagged invariant-section reconstruction = bounded_complete_realization
C lagged invariant-section reconstruction = bounded_complete_realization
```

Status: `accepted_bounded` with disposition
`bounded_local_reconstructed_geometry_family_complete_A_C`. GTRS-PC is next.
D9 remains blocked on PC and comparative synthesis.

##### GTRS-PC: Persistent Structural Carrier

Pressure a declared persistent structural carrier only after the less stateful
families. A bounded row must freeze D1-compatible authority, formation and
writer semantics, no-input persistence/release, serialization, restoration
identity, reset baseline, migration, topology/event lifecycle, and exact
disabled behavior. Persistence is not credited merely for adding another state
variable; the row must identify what causal capability it supplies beyond
local invariant-section RG, such as noninvertible or multivalued regions,
independently retained structural state, representation-preserving context
changes, or a larger coupling/step-size domain. Base-state hysteresis requires
a complete-chain witness rather than serialization alone.

GTRS-PC-v1 freezes one primary realization before disposition. For candidate
`a` in `{A,C}`, add a bounded authoritative structural coordinate

```text
Z_4,a,k in B_R,a subset K_4,a

K_4,a,k = K_4,base + Z_4,a,k
h_a,k   = H_profile(K_4,a,k).
```

`Z_4` has the same candidate-local structural type as the accepted
`Delta K_4` source. It is not coherence resource, `W_A`, `T_C`, full geometry,
current, or solver state. The mature coherence-only theory does not authorize
an independent memory field; PC is therefore an explicit revision-specific
constitutive completion, not a core primitive. Its success also does not prove
that coherence-only Markov sufficiency fails.

After the accepted fixed-geometry current solve, derive

```text
S_a,k = Delta K_4,a(J_C,a,k,h_a,k)
a_PC,k = exp(-Delta_t,k / tau_PC,a),  tau_PC,a > 0

Z_4,a,k+1 = a_PC,k Z_4,a,k + (1-a_PC,k) S_a,k.
```

This is the exact held-source step of
`tau_PC,a dot Z_4,a = -Z_4,a + S_a`. It is the scalar-ZOH primary
representative, not the universal persistent-carrier law. It is a family-local
completion motivated by, but not normatively inherited from, the historical
slow-field form. Declare a `K_4` norm and compact base chart, then admit a ball
`B_R,a` only when

```text
m_a(R) = sup_{X in K_X,a, Z in B_R,a} ||S_a(X,Z)||_K <= R
H_profile(K_4,base+B_R,a) subset H_adm.

(X,H_profile(K_4,base+Z)) in D_reg,a for all X,Z
inf_{X,Z} sigma_min(D_J F_J,a) >= m_J,a > 0.
```

The constructive sufficient condition is

```text
||S_a(X,Z)||_K <= M_0,a + L_Z,a ||Z||_K
0 <= L_Z,a < 1
M_0,a/(1-L_Z,a) <= R <= min(R_profile_adm,a,R_reg,a).
```

Here `D_reg,A` includes floor-inactive positive-domain A conditions, while
`D_reg,C` includes fixed rank, strict gap, positive domain, and the accepted C
current conditions. Compact reference charts and continuity provide positive
`R_reg,a`. This proves parametric local carrier and current-substep admission
without clipping; numerical constants and an unconditional runtime envelope
remain open. For positive duration require `0<a_PC<1`; `a_PC=1` is allowed only
at the zero-duration identity reference.

The writer supplies the D2 lifecycle directly:

```text
nonzero S from neutral -> formation
zero S with nonzero Z  -> retention at every finite time
sustained zero S       -> asymptotic gradual release to neutral
constant S             -> bounded maintenance toward S
changed S              -> reconfiguration
```

Administrative reset, profile disable, migration, and threshold labels do not
count as native release.

Freeze D2 interventions separately. Natural no-input and explicit `write_off`
both use `S=0, Z+=a_PC Z` in this scalar profile but emit distinct receipts.
`retained_state_frozen` uses `Z+=Z`; administrative reset restores the baseline;
full PC disable enforces `Z=Z+=0` and `h=h_ref`. With PC enabled, `chi=0` or
`zeta=0` stops new inscription but does not erase existing carrier state; the
retained geometry remains load-bearing while `Z` decays.

For variable steps, zero-source and constant-source convergence use
`T_n=sum_{k<n}Delta_t,k` and require `T_n -> infinity`. On the sufficient chart,
matched future forcing contracts carrier differences by
`a_PC+(1-a_PC)L_Z<1`, giving explicit finite-capacity forgetting.

Freeze the complete PC order:

```text
validate Z/profile/context
-> derive h_k from Z_k
-> solve accepted fixed-h candidate current
-> derive j_k and S_k
-> continuity C_k+1
-> unchanged A writer or C poststate sector derivation
-> carrier writer Z_k+1
-> atomic commit.
```

`Z_k+1` is not read in the same beat. Candidate A has state `(C,W_A,Z_4,A)`;
`W_A` remains the sole mobility authority and its writer is unchanged.
Candidate C has state `(C,Z_4,C)`; `T_C` remains derived and uncommitted. In
both rows, `Z_4` is bounded nonresource structural information and `C` is
counted exactly once.

PC adds a real capability beyond local RG. RG requires one locally
single-valued `h=Gamma_a(X_a)`. PC admits distinct complete states
`(X_a,Z_4,a^(1))` and `(X_a,Z_4,a^(2))` with the same base `X_a`. This adds a
D1 B-like independent structural coordinate to A or C and is not
ontology-neutral relative to CI, OS, or RG. At vanishing geometry sensitivity,
`D_Z U_PC=a_PC I` is nonsingular and remains so for sufficiently small geometry
coupling, establishing independent retained complete-state capacity. Along an
accepted D8-A direct-field visibility direction, the carrier difference changes
the geometry entering a named current-equation term. This supports
equation-level path dependence without a base-map inverse, graph-transform
contraction, or section uniqueness. It does not yet prove base-state hysteresis,
a nonzero future `C/W` effect, or a larger numeric operating envelope.

Snapshots serialize the current carrier, profile identity, graph identity,
`tau_PC`, and reset-baseline carrier. Save/load restores both current and
baseline state; reset returns to the construction baseline; `set_state` does
not silently rebase. Non-PC migration initializes canonical zero without
inventing history. Disabled PC keeps `Z_4=0`, `Z_4+=0`, and `h=h_ref`; this
removes PC but does not by itself close full V3 reduction.

Changing `H_profile`, `K_4,base`, the representation, carrier norm/domain, or
writer semantics requires explicit migration and target re-admission even when
array shapes match. Such a change is not ordinary context continuation.

The positive profile remains fixed-topology and fixed-`K_4`-representation,
with a fixed-rank strict-gap smooth chart for C. Representation-preserving
context or boundary changes retain `Z_4` and recompute all declared surfaces.
That permission applies only while profile, base, representation, carrier
domain, and writer semantics are unchanged.
Same-space nonsmooth changes require a deterministic runtime map and block
classical analysis. Carrier-space-changing topology/reindex/split/merge/birth/
death events require typed `L_event^K4` or abort before mutation. Event
termination is not carrier transport.

GTRS-COMP must audit whether the exact profile quotient
`K_4/kernel(D_K H_profile)` removes any current profile-equivalent carrier
directions. Profile-kernel irreducibility must not be promoted into absolute
minimal reachable-state representation without a separate reachability,
writer-invariant-subspace, runtime-equivalence, and lossless-coordinate audit.
It must also call this profile the scalar-ZOH representative; a future typed
contractive operator semigroup may carry multiple timescales but is not opened
as another PC gate here.

COMP must additionally test whether timing and history authority are
analytically separable dimensions. Separation is not automatic composability.
No hybrid campaign is required, but COMP must name the first exact missing
hybrid row that could materially change the architecture population and route
it before the gate whose lifecycle contract depends on that population.

The architecture-local derivative surface is the block transition

```text
M_PC,a = [[D_X Phi_a, D_Z Phi_a],
          [D_X U_PC,a, D_Z U_PC,a]],

D_Z U_PC,a
  = a_PC I + (1-a_PC)(D_J S_a D_Z J_a + D_h S_a D_Z h_a).
```

No numeric spectrum or stability classification is implied.

The executed dispositions are:

```text
A persistent K_4 carrier = bounded_complete_realization
C persistent K_4 carrier = bounded_complete_realization
```

Status: `accepted_bounded` with top-level disposition
`accepted_bounded_persistent_K4_carrier_family_complete_A_C`. GTRS-COMP is now
authorized. D9 remains blocked on comparative synthesis.

##### GTRS-COMP: Comparative Realization Synthesis

After all three families receive minimum pressure, enumerate the actual
architecture population. Compare matched `(candidate, realization)` rows where
lawful and declare noncomparability otherwise. Separate candidate-ontology
effects from temporal-realization effects. Determine whether reconstruction
loses information, whether persistence adds capability beyond lifecycle cost,
and whether coupled/implicit differs materially from operator-split. For PC,
compare full `K_4` with its exact profile-kernel quotient before assigning
state/lifecycle cost, and distinguish the scalar-ZOH representative from a
possible multi-timescale contractive operator-semigroup profile. Only this
synthesis may close the remaining-family debt or route a named unresolved
family obstruction into D9/D10.

Do not assume `{CI,OS,RG,PC}` are mutually exclusive columns. Separate
geometry/current timing from history authority analytically without assuming
that arbitrary compositions are lawful. Pressure no combinatorial hybrid
matrix by default; identify and route the first precise missing hybrid row when
it could materially change the architecture population.

Executed result:

```text
record = GRC9V4-GTRS-COMP-v1
status = accepted_bounded
decision_record_digest = 67a9c97a79525dc70c2233fb2b6706c47d2e31388c9160520f6842d7dc63a84b

positive_primary_rows = 8
family_level_obstruction_rows = 2
routed_not_rejected_candidates = 1

architecture_dimensions = candidate_ontology x geometry_current_timing x history_authority
timing_history_composability_proved = false
PC_enabled_affine_profile_kernel = {0}
PC_full_K4_profile_kernel_irreducible = true
PC_absolute_minimal_reachable_state_representation_proved = false
scalar_ZOH_is_universal_PC_law = false
first_materially_missing_hybrid_pair = [A_CI_PC, C_CI_PC]

unconditional_pre_D10_numeric_stability_gate = false
conditional_selection_or_stability_gate = true
remaining_family_pressure_complete = true
candidate_or_architecture_selected = false
GTRS_CI_PC_authorized = true
D9_ready_after_human_acceptance = false
D9_authorized = false
D10_authorized = false
```

The result shows that timing and history authority are analytically separable,
but does not assume their composition. It closes minimum family pressure
without ranking the population. The named CI+PC pair is the first materially
missing hybrid and receives narrow pressure before D9. OS+PC and RG+PC remain
unpressured, not currently required, and may reactivate if solver cost, failure
surface, latency, or state-conditioned lagged geometry becomes a selection
axis. Numerical evidence becomes pre-D10 only if D10 attempts exclusive
preference, numeric ranking, or a stability claim.

##### GTRS-CI-PC: Narrow Coupled-Implicit Plus Persistent-Carrier Pressure

Status: authorized by accepted GTRS-COMP.

Pressure only the A and C pair identified by COMP. This is not a general hybrid
campaign. The primary constitutive question is whether retained past structure
and source-current same-beat geometry can compose lawfully in one atomic step:

```text
committed state = (X_a,k, Z_4,a,k)

joint root candidate:
  h_a = H_profile(K_4,base + Z_4,a,k + Delta_K_4,a(J_a,h_a))
  F_J,a(J_a,h_a; X_a,k) = 0

after a valid root only:
  X_a,k+1 = candidate commit from authoritative J_a
  Z_4,a,k+1 = a_PC,a Z_4,a,k + (1-a_PC,a) Delta_K_4,a(J_a,h_a)
```

The displayed sum is a pressure target, not an accepted equation. The gate must
determine whether retained and source-current structural increments share one
typed `K_4` authority, whether gains are applied exactly once, and whether the
current source's same-beat geometry effect plus later retained effect is the
declared temporal contract rather than accidental double counting.

The gate must also freeze:

- the invariant source/root domain for
  `Z_4 + Delta_K_4`, not only the carrier ball for `Z_4`;
- uniform joint-root regularity on that composite domain;
- `chi`, `zeta`, `kappa_H`, CI-off, PC-off, read-off, and retained-`Z_4`
  semantics without deleting lawful past state accidentally;
- failure atomicity: a failed root commits neither candidate state nor carrier;
- writer timing: new `Z_4,k+1` is not read back in the same beat;
- serialization, restoration identity, reset baseline, `set_state`, duplicate,
  migration, replay, and profile-mismatch behavior for the hybrid state;
- representation-preserving context change and carrier-space-changing event
  boundaries;
- exact A/C row dispositions without ranking either candidate.

OS+PC and RG+PC remain recorded as unpressured compositions. Reopen them only
if a later selection uses solver cost, failure surface, latency, or
state-conditioned lagged geometry in a way that could make either material.

## D9. Complete Step And Lifecycle Contract

Status: blocked on completion of the narrow GTRS-CI-PC pressure. D10 remains
subject to conditional numerical-discrimination obligations.

Freeze candidate complete-step ordering, causal state, serialization,
restoration identity, reset baseline, RNG use, deterministic replay,
capabilities, profile identity, migration from GRC9V3, disabled behavior, and
test/telemetry/analysis ownership.

For Candidate A, freeze the post-continuity writer refresh explicitly: after
`C[k+1]` is accepted, rebuild all differential and gradient summaries consumed
by `G_W(C[k+1], J_C[k])` before constructing `W_drv_A`. Pre-continuity
summaries from `C[k]` are not admissible writer inputs.

After D7G closes the candidate and structural partition, verify every
surviving candidate's D1 embedding/projection construction on every declared
equivalence surface.
Freeze each actual `pi_a o F_V4_a_disabled o i_a = F_V3` witness and its exact,
projected, or tolerance-bounded classifications as the lifecycle/migration
contract. Do not use singular "selected candidate" language before D10.
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
`decision_record_digest` omitted, using Python
`json.dumps(..., sort_keys=True, separators=(",", ":"), ensure_ascii=True,
allow_nan=False)` encoded as UTF-8, with array order preserved. The predecessor
digest names the accepted serial predecessor; `supersedes` names an earlier
record of the same gate.

Numerical or prototype artifacts are optional and subordinate to the decision
record. They become load-bearing only when explicitly admitted and frozen.

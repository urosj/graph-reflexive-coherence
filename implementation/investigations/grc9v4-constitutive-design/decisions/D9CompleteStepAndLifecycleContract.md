# GRC9V4 Complete Step And Lifecycle Contract

**Gate:** `D9`  
**Record:** `GRC9V4-CD-D9-v1`  
**Status:** `accepted_bounded`  
**Decision digest:** `33c8fe75ae7fda716e97bb9714d5f297911bc4d606f5d382d77f9c3092aa4586`

## Purpose

D9 closes the design-level operational semantics of the current GRC9V4
population. It does not ask whether one nominal beat can run; the preceding
candidate and realization gates already established that. It asks whether each
profile remains scientifically coherent under interruption, restoration,
disablement, migration, failure, representation change, nonsmooth regime
change, typed topology events, and fail-closed untyped events.

The inherited positive population is:

```text
A/C x CI, OS, RG2b, PC
+
A/C x CI+PC
=
10 independently registered lifecycle profiles
```

Candidate B remains visible as
`routed_not_rejected_no_lifecycle_profile`. Without an admitted `U_B` writer
and complete transition, D9 has no B lifecycle row to pressure. This is not a
negative result for B and does not remove it from D10's architecture record.
The persistent-carrier family proves that independent structural state is
viable, but it does not derive B's required signed symmetric formation source.
B therefore remains underdetermined rather than rejected or silently solved by
PC.

No runtime, `src/`, test, or normative specification file changes in D9.

## Required Outputs

D9 produces four mutually checked records:

- [profile/state/lifecycle registry](./D9ProfileStateLifecycleRegistry.json);
- [10 x 26 adversarial coverage matrix](./D9LifecycleCoverageMatrix.json);
- [residual debt ledger](./D9ResidualDebtLedger.json); and
- [complete-step and lifecycle decision](./D9CompleteStepAndLifecycleContract.json).

The matrix contains 260 explicit cells and no blank inheritance. Three
multi-authority rows additionally expose 16 independent write-off, freeze, and
immediate-path subcases without multiplying the top-level columns.
Unsupported operations fail closed or name migration, while controls and
analysis-only operations are labeled separately from native runtime
transitions.

## Charge From The Complete Step

The current bounded V4 profiles use the existing closed-internal,
unit-measure resource model. Their authoritative resource coordinate is `C` on
live nodes. The authoritative nonresource state is `W_A` where present and
`Z_4` where present. Candidate C's `T_C`, `h`, solved current, OS substages,
the RG section, solver work state, and analysis projectors are derived or
transient nonresource coordinates, not authorities.

The continuity write is:

```text
C[k+1] = C[k] - Delta_t div(J_C) + B_ext + S_ext
```

Antisymmetry of every live internal edge contribution gives:

```text
sum_i div(J_C)_i = 0
```

Therefore the complete-step charge is derived, rather than inherited by name:

```text
Q(X) = sum_i C_i

Q(X[k+1]) - Q(X[k])
  = sum_i B_ext_i + sum_i S_ext_i
```

The ordinary admitted beat is closed internal, with `B_ext = S_ext = 0`.
Before any writer consumes final `C`, the
post-continuity state must be finite, nonnegative, and on the serialized
`Q_target` simplex. The current unit-measure budget projection must therefore
be the identity. A nontrivial correction fails the beat rather than repairing
it after a writer has consumed a different `C`.

A future profile may deliberately admit a nontrivial projection, but it must
apply and receipt that projection before every final-`C` consumer and include
the projection in the complete derivative.

D9 also freezes the general charge and event-accounting form:

To avoid collision with Candidate C's derived nonresource coordinate `T_C`,
this D9 report writes the event resource transport map as `T_C_evt`. It is the
same map denoted `T_C` in the review equations; the two `T_C` roles are not the
same object.

```text
Q_varpi(C) = varpi^T C

C+ = T_C_evt C- + Delta_C_event

conservative part:
  varpi+^T T_C_evt = varpi-^T

event receipt:
  Delta_Q_event = varpi+^T C+ - varpi-^T C-

Q_target+ = Q_target- + Delta_Q_event
          = varpi+^T C+
```

For positivity-preserving unit-measure events, `T_C_evt >= 0` and
`1+^T T_C_evt = 1-^T`. Split weights, merge aggregation, and node lineage are event
data. Birth, death, and external exchange use `Delta_C_event` and its explicit
charge receipt. The corresponding tangent and structural projector replace
`1` by `varpi`:

```text
V_Q_varpi = {delta X : varpi^T delta C = 0}

Pi_varpi_H0(delta C)
  = delta C
    - H0^-1 varpi (varpi^T delta C)
      / (varpi^T H0^-1 varpi)
```

The resulting tangent and analysis projector are:

```text
DQ = (1^T on C, 0 on nonresource coordinates)

V_Q = ker(DQ)

Pi_Q_C_H0(delta C)
  = delta C
    - H0^-1 1 (sum_i delta C_i) / (1^T H0^-1 1)
```

`Pi_Q_C_H0` is the `H0`-orthogonal projector on the structural `C` sector. Its
identity extension on nonresource coordinates is a canonical retraction onto
the full tangent `V_Q`, not yet the full-state orthogonal projector. That
stronger object remains open until a product analysis metric, including
Candidate A's state metric, is frozen. Neither object is runtime state or
resource authority. D9 therefore resolves D8-B's charge, tangent, and
structural projector debt while carrying the A analysis-metric debt.

## Complete-Step Order

Every profile follows one atomic transaction:

```text
validate state, profile, context, time, input, and capability identity
-> derive or solve profile-specific geometry/current stages without commit
-> validate disposition, chart, residual, conditioning, and finiteness
-> apply authoritative antisymmetric continuity once
-> validate final C is finite, nonnegative, and on the serialized Q target
-> require the current budget projection to be an identity/no-op, or fail
-> refresh every final-C-derived surface
-> apply the A post-continuity W writer or rederive the C poststate
-> apply the PC/CI+PC carrier writer once when present
-> refresh derived surfaces and verify postconditions
-> commit every authoritative coordinate, or commit nothing
```

For Candidate A, every differential or gradient quantity consumed by
`G_W(C[k+1], J_C[k])` is recomputed from `C[k+1]`. A pre-continuity cache built
from `C[k]` is not an admissible writer input.

CI and CI+PC admit only a finite, checked solver disposition:

```text
valid_root
domain_failure
singular
conditioning_failure
nonfinite
no_admitted_root
multiple_admitted_roots
```

A solver return is not enough. Root selection must follow from authoritative
state, profile, input, and the admitted local or bounded domain. Previous roots, caches,
continuation tokens, retry history, and hidden RNG cannot become causal state.
OS preserves its one-pass split residual instead of repairing it. RG2b binds
the frozen extension completion as profile identity, not state. PC and CI+PC
write new `Z_4` only after a valid current/geometry result and never read the
new carrier in the same beat.

Candidate A CI and CI+PC are no longer limited conceptually to pointwise IFT
branches. Let `C_A(h;X)` be the admitted fixed-`h` current solution and define:

```text
G_A(h) = H_profile(K_base + Z + rho S_A(C_A(h;X), h))
```

On a closed convex geometry domain `H_A`, require
`G_A(H_A) subset H_A` and:

```text
abs(rho) epsilon_H (L_S,h + L_S,J L_C) < 1
```

Banach then gives a unique A root on the declared bounded domain.

Candidate C requires the theorem separately on each regular selector stratum
`sigma`. For every `H_sigma`, freeze:

```text
G_C,sigma(H_sigma) subset H_sigma

abs(rho) epsilon_H
  (L_S,h,sigma + L_S,J,sigma L_C,sigma) < 1
```

This gives at most one root per admitted smooth stratum. D9 only then compares
the selector-consistent regular roots across strata. It does not treat a rank
jump as one smooth contraction domain. A root exactly on a selector threshold
or other nonregular boundary fails closed until a separate boundary-root
contract is admitted. These are bounded-domain theorems, not claims of
arbitrary-large-coupling globality; numerical constants remain verification
inputs rather than missing constitutive mathematics.

## Temporal Boundaries

`Delta_t = 0` is an identity on authoritative state only for an already
admitted state, profile, and context whose preconditions remain valid and for
which no external impulse exists. It does not bypass an invalid root, domain,
profile, or context. Negative duration is invalid. A failed attempt commits
nothing; a smaller-duration retry by an external controller is a new attempt.
An instantaneous external exchange is represented by the typed event jump and
`Delta_Q_event` receipt, not by weakening ordinary zero-duration identity.

The primary persistent profile keeps:

```text
a_PC = exp(-Delta_t / tau_PC)
tau_PC > 0 and finite
```

With zero source:

```text
Z_n = exp(-sum_k Delta_t_k / tau_PC) Z_0
```

Release therefore requires divergent accumulated elapsed time, not merely an
infinite beat count. `tau_PC = infinity` or `a_PC = 1` at positive duration is
outside the primary release-capable profile unless admitted separately.

D9 preserves the CI+PC unit-plus-unit composition. Under constant source,
`K_eff` approaches `K_base + 2S`; lifecycle handling does not normalize that
profile. Its normative classification belongs to D10.

## Disablement And V3 Reduction

D9 keeps four operations distinct:

```text
causal switch-off
state disablement
state migration or drop
native release
```

For persistent profiles, `chi = 0` or `zeta = 0` stops new inscription or
enactment but does not erase existing `Z_4`. `kappa_H = 0` makes the structural
channel inert without deleting its state. Disabling PC with nonzero `Z_4`
requires migration. `rho_inst = 0` is the CI+PC-to-PC timing ablation and
preserves history.

All ten disabled-profile rows have an exact candidate-specific GRC9V3
transition commuting witness:

```text
pi_a o F_V4,a,disabled o i_a = F_V3
```

For A, the disabled branch restores exact V3 `W` reconstruction and step
authority. For C, retained-sector Read-Back is disabled and `T_C` is diagnostic
only. The contract separately freezes transition equivalence, snapshot/state
projection, equivalence on the V3 observable set, and lifecycle/event
equivalence. V4-only diagnostics, receipts, and profile metadata are projected
out rather than called equal, and enabled V4 lifecycle is not relabeled as V3
event lifecycle. V3 snapshots never acquire fabricated retained history.

`Q_target` is serialized lifecycle identity and equals `sum(C)` on admission.
`set_state()` cannot silently change it or accept a mismatching `C` sum.

## Migration And Identity

Every permitted profile transition is a typed map with admission
preconditions, information-loss semantics, and a receipt. The registry freezes
seven classes:

```text
same-candidate nonhistory -> nonhistory
same-candidate nonhistory -> history with Z_4 = 0
same-candidate history -> nonhistory with explicit archive/drop
PC -> CI+PC under exact profile identity and B_2R readmission
CI+PC -> PC while preserving Z_4 and removing immediate timing
A -> C: preserve C, archive/drop W_A and A history, initialize target C history
        to zero when required, rederive T_C, and re-admit with a loss receipt
C -> A: preserve C, initialize target history to zero, and require a frozen
        I_A(C,U,G) = exact GRC9V3 base-conductance reconstruction for W_A
```

Migration need not be an isomorphism. A-to-C is admitted as explicitly lossy.
C-to-A is also admitted as a history-free migration: all declared V3
reconstruction inputs must be available, target `W_A` must satisfy its positive
domain, optional target `Z_A` starts at zero, and the target profile re-admits.
No A history is fabricated.

Events and profile migrations act on the lifecycle tuple, not only current
state:

```text
mathfrak X = (X_current, X_reset, Q_target)

M_tilde_p->q(X_current, X_reset)
  = (M_p->q(X_current), M_p->q(X_reset))
```

The same declared history-preservation or reset policy applies to current and
reset state, and the target charge is migrated explicitly. Consequently,
`reset()` after an admitted event returns to the construction baseline as
transformed through all admitted lifecycle events. It cannot resurrect an
obsolete source graph, profile, carrier, or charge target.

Changing `H_profile`, `K4_base`, `tau_PC`, `rho_inst`, carrier norm/domain,
writer identity, RG extension completion, selector/`W` policy, solver/root
selection, `Q_target`, or the context contract changes the meaning of state. It
requires migration and readmission, not an in-place configuration edit.

The context contract and current context value are distinct. Schema, units,
representation, semantics, and admissibility rules belong to profile identity.
An ordinary value change under that unchanged contract is declared transition
input and requires refresh/readmission, not migration. RG remains stricter: a
new value may require a new extension-relative section admission.

Serialization contains authoritative state plus the graph, profile, context
contract, `Q_target`, and reset baseline needed to reconstruct the transition.
Restoration identity includes semantic profile fields and excludes
representation-only caches. Reset returns to the lifecycle-transformed
construction baseline;
`set_state` does not silently rebase it or change `Q_target`; duplicates share
no mutable state. Scientific replay equivalence is required, while
cross-platform bitwise equality is not claimed.

## Representation, Regime, And Events

Node relabeling and edge reorientation are covariance transformations under
the declared permutation, signed-cochain, and `K_4` representations. They do
not create new scientific states.

Same-contract context value changes may retain state after derived-surface
refresh and target readmission. Candidate A's floor activation is runtime-valid
under the frozen total policy but analytically nonsmooth.

Candidate C uses a basis-independent functional-calculus selector at every
rank. Fixed-`h` and OS-stage changes remain runtime-valid but nonsmooth after
target `P_M`, `H_M`, `I_4M`, and current-stage readmission. Coupled C-CI and
C-CI+PC now solve the root stratum by stratum:

```text
R(X) = union over selector strata sigma of
       regular roots of F_C,sigma(J,h)=0
       that satisfy their own selector consistency conditions

abs(R(X)) = 1  -> accept the unique self-consistent root
abs(R(X)) = 0  -> no_admitted_root
abs(R(X)) > 1  -> multiple_admitted_roots
```

Previous rank, previous root, continuation token, and eigenbasis ordering have
no selection authority. Rank crossings are runtime-valid nonsmooth when one
regular root survives across the stratum-local result union; classical
derivatives stop at the crossing.

All ten profiles admit typed topology-event continuation:

```text
event declaration
-> T_C_evt resource map and charge receipt on current and reset resource state
-> candidate-specific nonresource transport or explicit history reset on both
   current and reset history
-> Q_target update
-> target derived-state reconstruction
-> target profile readmission
-> atomic lifecycle-tuple commit
```

Candidate A may use an admitted history-preserving `W_A` event map. Otherwise
it archives temporal `W_A` history and applies the exact V3 reconstruction on
the target graph. Persistent profiles require a typed event map
`L_K4_evt : K4(G-) -> K4(G+)` that is bounded, symmetry preserving,
PSD-cone preserving for the current A/C profiles, representation covariant,
target-profile compatible, deterministic, and replay-identifiable. An
event-supplied one-form lineage may factorize it as
`L_K4_evt(Z) = L_1 Z L_1_star` only when the source/target pairing and adjoint
are explicit; orthonormal edge coordinates recover `L_1_star = L_1^T`.
Without an admitted `L_K4_evt`, the event archives the old carrier, sets
`Z_4+ = 0`, and emits `structural_history_lost_at_event`. RG maps
the authoritative candidate state, builds the frozen completion on the target
graph, solves its invariant section, and re-admits.

Thus topology continuation does not imply lossless history transport.
Generic lossless history preservation without sufficient event lineage is a
resolved negative boundary, not an open debt: dimension reduction prevents an
injective map, while absent correspondence leaves symmetry-related target
embeddings without a canonical choice. Untyped events, failed target roots,
irregular target objects, or failed receipts still abort before mutation. Array resizing or
stable IDs alone are not an event map, and fail-closed termination is not
typed topology support.

Typed substrate lifecycle continuation also does not by itself establish
continuation-spectrum identity preservation across the event. That core-level
identity question remains separate from the lawfulness of the state transition.

## Debt And Claim Boundary

All 47 CI+PC predecessor debts receive exactly one disposition:

```text
carried       = 29
resolved      = 18
superseded    = 0
current D9    = 0
D9 resolved negative results = 1
live union    = 29
verification obligations = 4
silent drops = 0
```

D9 has no open lifecycle-mathematics debt. Its one tranche-local question is
closed negatively: generic lossless history preservation is not canonically
defined without sufficient event lineage. Explicit archive/reset plus target
reconstruction is the lawful generic fallback; stronger preservation requires
an admitted typed event map.

Numerical parameter instantiation, lifecycle runtime conformance, executable
migration/event conformance, and charge-receipt conformance are recorded
separately as post-spec verification obligations. They block implemented or
numerically ranked claims, but they are not unresolved D9 mathematics.
Every resolved quantitative predecessor row names
`D9-VERIFY-QUANTITATIVE-PARAMETER-ENVELOPES` as its successor obligation.

D9 supports a population-wide design contract for ten bounded profiles,
including typed topology-event continuation for all ten through conservative or
receipted resource transport, history transport or explicit reset, target
reconstruction, and readmission. It freezes the complete-step unit-measure and
general charge-covector contracts, full tangent, structural C-sector projector,
canonical tangent retraction, whole-lifecycle event and profile migration,
both directional A/C migrations, bounded-domain A CI contraction,
stratum-local C contraction and stratified C roots, typed `K_4` event maps,
scoped exact disabled GRC9V3 reduction
surfaces, and typed lifecycle, identity, replay, failure, and regime boundaries.

It does not support generic history preservation when an event supplies no
sufficient lineage map, continuation-spectrum identity preservation from typed
lifecycle continuation alone, untyped or failed-readmission events, a
full-state orthogonal projector,
arbitrary-large-coupling globality or numerical operating envelopes, formed-
branch endpoint hysteresis or stability, runtime implementation, architecture
selection, or a normative GRC9V4 specification.

## Disposition

```text
status = accepted_bounded
scientific_disposition = accepted_bounded_lifecycle_and_typed_event_closure
D9_complete_after_human_acceptance = true
D9_complete = true
D10_ready_after_human_acceptance = true
D10_authorized = true
specification_authorized = false
implementation_authorized = false
runtime_or_src_changed = false
```

D9 closes operational semantics without erasing architectural differences.
Human acceptance is recorded. D10 is authorized to begin, while specification
and implementation authorization remain closed.

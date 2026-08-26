# D2 Formation, Retention, Release, And Write Interface

**Record:** `GRC9V4-CD-D2-v1`  
**Status:** accepted bounded  
**Decision digest:** `ea2b953685bb23dfe979b2f5d2ae0f22f364a51484d6536c1721f144c9cad740`

## Purpose

D2 defines what it would mean for each D1 survivor to form, retain,
reconfigure, release, transfer, and receive a lawful write. It freezes causal
interfaces and invariants. It does not invent final numerical equations,
select parameters, execute runtime probes, or choose the GRC9V4 architecture.

All three D1 survivors remain in the comparison:

```text
V4-A-temporalized-W
V4-B-independent-derived-carrier
V4-C-constitutive-C-sector
```

No candidate is rejected or reclassified at D2.

## Causal Beat Order

The default write order is explicit and one-beat delayed:

```text
read retained representation at k
  -> form baseline/direct current J0[k]
  -> apply future D5 read contribution if enabled
  -> close future D6 total current J_C[k]
  -> apply declared downstream C/runtime consequence
  -> compute forming or write driver
  -> write retained representation at k+1 exactly once
  -> apply bounds, release, and lifecycle recording
  -> serialize complete post-state
```

The newly written value at `k+1` cannot feed `J_C[k]`. Such a same-beat loop
would be an implicit closure and requires a D6 decision, regular solve, and
causal-state audit. D2 therefore permits reflexive write-back without silently
introducing an algebraic self-loop.

## Formation And Retention

Formation requires an attributable transition away from a neutral or baseline
relation under a qualifying source-current input. Labels, serialization, slow
parameters, or persistence alone do not form a retained representation.

The D2 no-input control is:

```text
no_forming_or_write_input
```

It begins from a formed state and removes only the declared forming/write
driver. Other lawful ordinary dynamics may continue. The candidate may then:

```text
retain within declared bounds
relax lawfully
release to neutral
reconfigure through ordinary declared dynamics
```

It may not be secretly refreshed by the forming driver or a hidden producer.
This control is distinct from the D5 passive null:

```text
no_forming_or_write_input != zero_present_current
```

The first tests post-input retention/release. The second tests whether a future
Read-Back operator emits zero read current when present current is zero.

Initialization, driver removal, write disabling, and state freezing are four
different operations:

```text
initialization
  declares a starting or reset state; it is not formation

no_forming_or_write_input
  removes the external or activity-forming driver while ordinary dynamics and
  the constitutive write law remain active

write_off
  disables the constitutive write coupling

retained_state_frozen
  holds the retained coordinate fixed while other state advances
```

Post-input retention may be passive, decaying, metastable, internally
maintained, regenerated from another declared retained coordinate, or
transferred between declared representations. A small rate does not establish
retention. Any internal maintenance must close on declared causal state;
lingering input, schedules, queues, stale caches, mutable registries, repeated
driver events, and undeclared RNG injections count as external forcing.

Native release need not invert formation. It may use a distinct smooth decay,
opposing activity, inactivity threshold, constitutive saturation response,
sector transfer, event-mediated release, or declared reconfiguration. Every
candidate needs some constitutive native release or reconfiguration route, but
D2 does not require that route to remain on a smooth fixed-topology stratum.
Smooth release is required only when claimed. Event-mediated release remains
admissible only if D4/D9 later provide its causal, accounting, interspace, and
lifecycle contract. Administrative reset never counts as native release.

## Temporal Write And Composition Boundary

Every future write input belongs to one of three temporal classes:

```text
pre_solve       = state and declared preclosure surfaces at k
post_solve      = J_C[k] only after D6 defines and solves total-current closure
post_state_update = C[k+1] or another declared downstream consequence
```

The generic word `J` is not an admissible temporal specification. If a future
law makes `J_C[k]` depend on the newly written candidate state at `k+1`, it has
created an implicit same-beat cycle. D6/D7 must admit and solve that cycle; D2
does not conceal it as an ordinary update.

Simultaneous writes arrive as one declared batch. A candidate must later choose
commutative bounded addition, serialized ordered composition, declared
competition/normalization, or deterministic priority. Undefined iteration
order and external sequence memory are forbidden. If composition is
order-sensitive, its order must be deterministically recoverable from the
declared current causal state, input batch, and constitutive ordering rule; any
persistent order state must be serialized.

## Candidate A: Temporalized W

D2 gives Candidate A one authoritative enabled state, `W[k]`. The legacy
GRC9V3 reconstruction is an instantaneous reference proposal:

```text
W_hat[k] = legacy reconstruction from current permitted surfaces
R_W[k]   = declared difference/relation between W[k] and W_hat[k]
```

`W_hat` is not a second retained state. The candidate writer has the abstract
shape:

```text
W[k+1] = U_A(W[k], W_hat[k], C[k], J_C[k], downstream state, clock, lifecycle)
```

Formation moves `R_W` away from neutral by a preregistered attributable margin.
Post-input retention means `R_W` remains causally available after the forming
driver ends. Numerical inertia alone is not structural retention.

Release returns `R_W` to neutral so that authoritative `W` rejoins its declared
instantaneous-baseline relation. Release must be explicit; silent overwrite is
not release.

The eventual relation between instantaneous and retained contributions remains
open:

```text
additive composition
declared nonlinear composition
replacement of the legacy relation
```

D4 owns the effective geometry/mobility/transport interpretation. If one `W`
cannot own the two contributions coherently, A must be split or reclassified.

Resource status remains:

```text
nonresource structural information
```

`W` can condition current but cannot source, sink, or duplicate coherence.

Candidate A also carries four explicit hardening obligations. The
instantaneous reconstruction `W_hat` and retained writer `U_A` may not count the
same current history twice without a nonduplicative constitutive derivation.
Floors, ceilings, clipping, and normalization are constitutive if they alter
future history; they cannot be hidden as numerical hygiene. Persistence of a
`C` branch previously reached through `W` is not persistence of `W` itself.
Finally, capacity control must declare whether normalization is local,
basin-local, or graph-wide, because a global normalization writes every edge.

## Candidate B: Independent Derived Carrier

Candidate B writes an independent serialized `T` recursively:

```text
T[k+1] = U_B(T[k], C[k], J_C[k], downstream state,
             geometry/topology context, clock, lifecycle)
```

The update must be derived from permitted RC quantities. The present value is
not required to satisfy `T[k] = f(C[k], J[k])`; if it does, B becomes a
reconstructed representation rather than independent state.

Formation moves `T` away from canonical `T_neutral`. Retention requires that it
remain nonneutral or causally available after the forming driver ends. If `T`
can be rebuilt from a finite history, later work must determine whether that
history is already part of complete declared state. Otherwise `T` may be a
legitimate Markov completion, but not an unsaved history cache.

Release returns `T` to canonical neutral or removes a declared component under
a nonresource ledger. Append-only history and unbounded dimensional growth are
blocked.

Candidate B also remains:

```text
nonresource structural information
```

An independent resource variant would change the theory-level conservation
story and is outside the current B family.

An EMA is therefore only an admissible candidate equation shape, not evidence
that B has earned retained RC structure. A small `eta` creates a D3/D7
obligation. `T[k+1]` must be Markov-closed on `T[k]` and declared inputs rather
than requiring an undeclared trajectory. Its dimension/value capacity and
release must be bounded independently of its lifetime. Most importantly,
physical `C` depleted from the system cannot be restored solely from
nonresource `T`; such behavior would force a resource reclassification and a
theory-level conservation reopening.

## Candidate C: Constitutive C Sector

Candidate C has no independent write to its retained representation:

```text
T_C[k] = S[k] C[k]
```

Only the authoritative `C` update writes physical state. The sector is then
recomputed by its D1-admitted constitutive selector.

D2 freezes the exact discrete bookkeeping identity:

```text
T_C[k+1] - T_C[k]
  = S[k](C[k+1] - C[k])
  + (S[k+1] - S[k])C[k+1]
```

The first term contains `C` change under the old selector. The second records
selector/basis drift. This identity does not by itself prove retained
formation. Activity-induced sector change is attributed through a matched
control:

```text
Delta_T_write
  = T_C[k+1, forming]
  - T_C[k+1, matched no-forming-input]
```

The complete factorization remains:

```text
ordinary C update
  != attributable retained-sector occupation/change
  != later retained-conditioned read effect
```

The third arrow belongs to D5/D7. Generic continuity of `C` cannot be relabeled
as retained write-back.

Under no forming input, ordinary `C` dynamics may continue while selected
sector content persists, relaxes, or leaves the sector. Rank changes are
changes of decomposition, not automatic resource creation/destruction. D2/D4
must account for content entering/leaving the sector and selector drift.

Candidate C projects existing `C` resource. The budget counts `C` once; a
serialized derived view would duplicate representation only.

For C, projector motion and content change remain separate:

```text
content change   = S[k] (C[k+1] - C[k])
projector motion = (S[k+1] - S[k]) C[k+1]
```

Rank increase is not automatically formation, and rank decrease is not
automatically release. Sector exit and later re-entry remain an explicit
D4/D8 ambiguity: they could represent release/reformation, selector motion,
transfer, or continuous identity under basis transport. D2 blocks every one of
those labels until the corresponding transport and identity rule is supplied.

## Write Inputs And Hidden Authority

All candidates may consume only declared current or downstream state:

```text
candidate state at k
C[k]
J_C[k] after declared current closure
C[k+1] or another declared downstream consequence
declared geometry/topology/lifecycle context
declared clock
serialized RNG state if stochastic writing is explicitly admitted
```

Blocked inputs include future outcomes, later basin classifications,
analysis-only labels, report success, unsaved optimizers/accumulators, and
undeclared scheduler, registry, or RNG state.

Each candidate has one authoritative write or an explicit no-write per beat.
Hidden pre-step/post-step writers are forbidden.

The future write record must also declare what information it preserves:

```text
signed orientation | axis only | magnitude/activity | temporal order | none
```

Net-zero activity may still be historically nontrivial; a squared-current law
cannot claim signed orientation. Scalar or axis carriers must be invariant to
storage-edge reversal, while a directional carrier needs an explicit oriented
type. Stochastic writing is permitted only with serialized RNG state, declared
consumption order, replay equivalence, and site-specific attribution.

## Resource And Capacity Boundary

D2 admits no independent physical resource:

| Candidate | Accounting | Capacity boundary |
| --- | --- | --- |
| A | nonresource structural information | bounded/coercive edge state; no hidden history growth |
| B | nonresource structural information | bounded/coercive `T`; no append-only history |
| C | projection of existing `C` | rank/decomposition accounted; `C` counted once |

Every candidate requires explicit release/reconfiguration, serialization, and
reset ownership. A transport role cannot create a resource role.

Capacity and lifetime are independent. Finite dimension does not prove release,
and finite lifetime does not prove bounded information capacity. Saturation is
part of the constitutive mechanism whenever it selects or irreversibly changes
a future branch.

## Transfer Boundary

D2 does not manufacture topology transport:

```text
fixed-stratum reconfiguration
  -> D2 interface

peer/source-destination transfer
  -> requires explicit accounting

topology-event interspace transport
  -> D4 and D9
```

Lineage, node IDs, copied state, or a shared label are not transfer.

## Control And Pressure Contract

Thirty-three controls are frozen for later candidate transitions. They include
the original lifecycle/accounting controls plus explicit initialization,
write-off, frozen-state, hidden-maintenance, A double-write, B cache/resource,
C projector/rank/re-entry, multiwrite, covariance, RNG, saturation, and
capacity/lifetime controls.

```text
no_forming_or_write_input
nonneutral_initialization_as_formation
formation_source_omission
write_off
retained_state_frozen
writer_ownership_swap
multiwrite_order_and_composition
indefinite_accumulator
arbitrary_slow_cache
B_EMA_substitute
hidden_resource_duplication
B_resource_regeneration
hidden_helper_state
hidden_external_maintenance
same_beat_new_state_read
silent_release_reset
administrative_reset_as_native_release
uncontracted_event_release
driver_vs_state_persistence
formation_retention_arrow_collapse
A_instantaneous_retained_double_write
A_clipping_or_normalization_as_hidden_memory
A_W_state_vs_C_effect_persistence
C_generic_continuity_relabel
C_projector_motion_relabel
C_rank_change_relabel
C_sector_exit_reentry_relabel
net_zero_or_squared_history_collapse
write_orientation_covariance
stochastic_write_replay
capacity_as_lifetime
saturation_as_numerical_hygiene
topology_lineage_transfer
```

These controls are specified, not executed. Runtime conformance belongs to D7
and reduction/lifecycle parity to D9.

The structured record also carries a 30-row pressure audit. Every supplied
pressure point is bound either to a frozen D2 rule or to a typed later-gate
obligation. None is left as an unspecified implementation detail. The most
important deferred obligations are:

```text
A normalization/composition/saturation              -> D4/D7
B structural justification and resource boundary    -> D3/D4/D7
C selector/rank/sector identity                      -> D3/D4/D7/D8
multiwrite information/covariance/RNG                -> D5/D7
native release route and topology lifecycle          -> D4/D7/D9
```

## Candidate Status

```text
candidate_set_after_D2 = [A, B, C]
rejected_on_D2_interface = []
reclassified_or_revision_needed = []
architecture_selected = false
candidate_equivalence_resolved = false
```

D2 narrows the D1 authority, selector, capacity, and hidden-state debts but does
not close them empirically. It adds six explicit debts: exact update operators;
A double-write/saturation/normalization; B cache/Markov/resource regeneration;
C sector entry/exit/rank/basis; multiwrite information/covariance/RNG; and
release-route ownership separated from capacity and lifetime. These cannot be dismissed
as implementation details or populated with convenient rates before their named
gates.

## Claim Ceiling

D2 supports only:

> Bounded candidate-specific formation, retention, release, reconfiguration,
> transfer, resource, capacity, and write-interface contracts for A, B, and C.

It does not support exact update equations, observed retention, a formed
structural branch, final transport ownership, directional Read-Back, current
closure, a complete transition, topology interspace transport, V3 reduction,
architecture selection, specification, or implementation.

## Acceptance And Authorization

```text
D2_acceptance = accepted_bounded_2026-08-24
D3_authorized = true
specification_authorized = false
runtime_implementation_authorized = false
src_change_authorized = false
```

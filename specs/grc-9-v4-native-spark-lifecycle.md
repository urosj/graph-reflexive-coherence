# Native C_OS spark lifecycle boundary — P9-9.1a.3

Status: implemented, bounded verification pending review. This implements the
optional [scientific completion contract](grc-9-v4-spark-completion.md) and its
[earlier-endpoint successor](grc-9-v4-spark-completion-earlier.md). It does not
establish that the native source trajectory reaches the domain near beat 374.
That acceptance remains P9-9.1a.5, after the P9-9.1a.4 runtime estimate.

## Explicit declarations and mathematical admission

`GRC9V4SparkConfiguration` selects configuration v3, exact rational C and clock,
resolved specialization v3 with explicit completion policy or null, identity v3,
and `spark_cos_exact_flint_flux128_v1`. The unchanged public `GRC9V4` facade
delegates to its existing public transaction owner. Existing v1/v2 decoders and
binary64 execution remain separate. The optional JSON schema is packaged as a
separate byte-pinned asset; the frozen generic asset index is unchanged.

The normative site unit ID `resource_potential_site_units_v1` denotes the
resource/potential units within `grcv4_nondimensional_reference_v1`. The .2
numerical declaration's older spelling remains readable at that boundary,
with its original identity. V3 requires the normative optional-site spelling;
changing it changes the profile preimage. No old execution record is rewritten.

An immutable `CompletionCertificate` contains exact center, full n×(n−1) S and
(n−1)×n U, and complete graph/profile/context/reference/charge/duration/role/policy
bindings. Construction recomputes US=I, charge tangency, positive resource domain,
the whole-domain all-route geometric roster, and the analytic full C_OS map and
Jacobian with Arb512. Every predictor/geometry/corrector derivative contributes.
The correlated resolvent split bound must pass the unchanged OS tolerance;
conditioning bounds must pass the declared solver limits. Strict contraction
and center defect yield a positive image margin. The native conservative flux
error `32 ||UB||∞ 2^-129` must lie strictly below that margin.

Proofs are cached only by complete immutable operand bytes, with bounded cache
size. Actual state membership, rows and terminal reachability are recomputed.
Failed proof admission is unresolved certification, not scientific impossibility.
No saved research success flag, trajectory checkpoint or accepted endpoint is an
input to the production validator. Geometric children are independent of the
represented-current `basin_identity` diagnostic.

## Event and positive window

The selected event reuses the canonical native port allocator and event identity
grammar. It requires an actual fresh committed source beat, saturated source,
exact hybrid trigger, a unique geometric parent, unit internal references and
the declared shares (1/64,31/32,1/64). The actual event identity names the new
module. Both resource roles transfer through the same exact stochastic map and
receive fresh predictor/corrector OS readmission without continuity or clock
advancement. Target profile maps are rebuilt from this actual graph.

Certificate installation validates the ordered current/reset pair and adds no
window time. Every positive ordinary commit checks actual membership and complete
children inside the lifted parent footprint. Entry is observation zero; two
further committed duration-32 beats supply elapsed time 64. Leaving the domain,
changing the roster or replacing the certificate restarts the window. Inspection
and rejected/zero-duration calls change nothing. Reset/rebase and admitted static
migration invalidate the event candidate. A migration cannot replace resources,
topology, reset state or clock. Unimplemented exact-to-legacy branch conversion
fails closed and preserves the existing state/window.

Completed evidence follows `grc9v4-child-completion-evidence-v2`. Its hash
references resolve to immutable objects embedded in the checkpoint, using the
virtual `implementation/native-spark/objects/<sha256>.json` namespace. They are
not arbitrary filesystem reads. `completion_evidence_object(reference)` resolves
these values, including completed evidence retained in the occurrence record
after reset or in another live fork. The completed record binds the actual source
capture, event receipt, full certificate, reads and committed observations.

## Atomic accounting and persistence

The public owner's `_publish` owns the native extension. One immutable accounting
root contains each fork's publication, consumed event occurrences and canonical
new-child records. A completion receipt, occurrence claim and new-child insertion
are validated before one root assignment. The surviving parent is excluded.
A late failure changes none of these. There is no independently advancing mutable
completion tracker or UI-side accounting authority.

An occurrence binds the actual successful event receipt, ancestry and accounting
origin. It does not bind certificate IDs or window numbers. Duplicates before
completion share the same lock/root, so even concurrent completion credits only
one occurrence. Reset, policy/certificate replacement and stale checkpoint import
cannot remove an already published consumption record.

An explicit typed request `operation_id` identifies a delivery within the
branch's successful ancestry, across ordinary and expansion requests. Repeating
that ID is rejected before numerical preparation and changes no publication,
clock, window or accounting. Forks/restores inherit IDs in that ancestry; this
does not claim global delivery deduplication across disconnected histories.
Failed attempts consume no ID and can be retried. Untyped `step()` has no delivery
ID and each successful call is a new physical beat.

Checkpoint v3 carries exact configuration, receipts, action journal, certificates,
window, retrievable evidence and accounting records. Previously admitted immutable
publications can be reused within the live authority; otherwise exact scientific
replay must reproduce the publication. Replay runs detached and earns no live
credit. Restore reconciles with the live authority before publishing a fork.
Stale checkpoint accounting can be a subset of current accounting, never an
instruction to erase it. A cold checkpoint carrying another fork's claims without
that shared authority is rejected.

This accounting scope is explicitly **one process-local shared publication**.
Cold restore reconstructs the checkpoint's own validated accounting history.
Two disconnected processes restoring separate pre-completion copies require an
external reconciliation authority for global uniqueness; this implementation
does not claim it. Broader hierarchy evolution remains deferred.

## Public use and verification scope

Construct `GRC9V4(configuration_v3)`, execute the source `step()`, then `expand()`
with the typed canonical event request. Install both actual-graph certificates
with `install_completion_certificates(current, reset)`. Ordinary `step()` drives
the window. `compute_observables()` exposes exact resources, fresh both-role
membership, window/evidence, consumed occurrences and children; inspection earns
no gain. Save/load/duplicate use the explicit checkpoint successor.

The retained .3 checks execute the actual source beat and event. Positive-window
unit controls use an explicitly synthetic target-center fixture with actual event
provenance and the real native map. They prove lifecycle behavior, not a lawful
source-to-center trajectory. The public support report keeps optional completion
and native endpoint acceptance false until the full campaign is reviewed.

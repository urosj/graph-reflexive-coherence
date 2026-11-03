# Native C_PC numerical policy

Policy `spark_cpc_arb256_flux128_carrier192_v1` is an explicit successor for
quartic C_PC, with exact charge 21 and duration 32 on the declared actual graph.
It does not upgrade legacy binary64 states. The native preflight is
[P9-9.1a.6-CPC-Contract](../implementation/phase-9-grcv4/tranche-9/P9-9.1a.6-CPC-Contract.md).
The mathematical law and adopted domain remain those of the
[PC contract](grc-9-v4-spark-completion-pc.md) and
[earlier closure successor](grc-9-v4-spark-completion-earlier.md).

## Complete physical state and ordinary beat

`grcv4-exact-carrier-state-v1` stores canonical reduced rational strings for C
and the complete dense Z_4 matrix. FLINT performs exact operations. Admission
requires symmetry, exact symmetric-star support and Frobenius norm at most
1/64. Signed carrier coordinates are admitted. A resource-only state is not a
C_PC state and cannot silently enter this branch.

With B outward incidence, L=BᵀB, O=|B|ᵀ|B| and old H=I+Z/2, a fresh Arb256 read
computes

    j0 = -Bᵀ[B H Bᵀ C/64 - ((C-2)^3-(C-2))]/1024
    y  = (3I/4 + H L)^(-1) j0
    J  = j0 + y/4
    f  = H^(-1)y/2
    S_ij = O_ij f_i f_j/4.

Both uses of H consume the same old carrier. The one physical write is
C'=C-32 B J and Z'=exp(-1)Z+(1-exp(-1))S. The writer consumes that same fresh
read; no sequential substitution of the new carrier is permitted. A fresh
read admits the represented poststate. A separate final diagnostic holds the
consumed H fixed; the reference diagnostic uses H=I. Neither diagnostic writes
state. No changing-state read, writer result or saved trajectory is a cache.

## Representation and complete rounding bound

Each current interval must lie within 2^-192 of its midpoint. Midpoints round
nearest/even to a 2^-128 flux lattice; the incidence update is exact, so charge
is exactly conserved without repair. Each independent symmetric-star carrier
coordinate rounds nearest/even to 2^-192. The whole ideal writer interval must
lie within 2^-224 of its midpoint. Mirrored entries are written identically;
nonstar entries remain exactly zero. Failed admission aborts the entire beat.

Let εJ=2^-129+2^-192, εZ=2^-193+2^-224, U the exact resource chart, m the number
of edges and z the positive carrier radius. The uniform error in
max(||U δC||∞, ||δZ||F/z) is bounded by

    δ = max(32 ||U B||∞ εJ, m εZ/z).

The dense Frobenius bound is conservative for the star support. Both errors
are included in certificate admission and independent sampled-step checks.
Strict δ < 1-q-defect is required. Arb256 is fixed; there is no fallback or
tolerance relaxation. Independent verification uses Arb768; the bounded
256/512 comparison is an experiment, not a second execution policy.

## Full domain certificate and membership

On the declared 15-vertex/16-edge target, the certificate has 14 charge-plane
resource directions and all 46 independent signed symmetric-star directions.
It uses the exact S/U resource parallelotope times a zero-centered Frobenius
carrier ball of radius 1/100000000. Full CC, CZ, SC and SZ derivative blocks
include both H consumers and the same-read writer. Orthonormal symmetric
coordinates use off-diagonal factor sqrt(2). Decay weights are applied to the
source derivative blocks when bounding the complete map. This is a whole-domain
inclusion proof, with geometric row predicates independent of Z.

Exact membership returns the **squared** max-product norm, to avoid irrational
serialization. Its threshold is still 1. Contraction and error estimates use
the unsquared norm; they must never be compared to the serialized squared
value as though it were an unsquared distance.

## Event, history and execution scope

The declared expansion archives both complete current/reset C/Z states and
fresh reads. `grcv4-exact-carrier-history-v1` wraps those exact objects, and its
canonical bytes are hashed with the `grcv4-history-content-sha256:` prefix.
The existing request envelope `whole_carrier_reset_with_loss_receipt_v1` and
`zero_carrier_v1` binds that explicit loss. The scientific disposition is
`event_loss_and_zero_target_carrier_v1` / `canonical_zero_carrier_v1`: the whole
target carrier is zero. This event loss is distinct from an ordinary beat's
exponential release. Legacy history schema validation remains unchanged.

Steps 1–4 cover bounded source/event execution, full-map checks, lifecycle and
runtime estimates. Synthetic near-center completion tests prove lifecycle
behavior, not source-to-entry success. Expected 374→376 current and 375→377
reset remain unverified until .5. Aggregate native completion support is false.

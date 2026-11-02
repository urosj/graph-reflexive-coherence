# Native A_PC numerical policy

Policy `spark_apc_arb256_flux128_conductance192_carrier192_v1` implements the
bounded [A_PC law](grc-9-v4-spark-completion-a-pc.md) under the
[native contract](../implementation/phase-9-grcv4/tranche-9/P9-9.1a.6-APC-Contract.md).
The full endpoint campaign remains separate from steps 1–4.

## State and actual ordinary map

`grcv4-exact-adaptive-carrier-state-v1` stores canonical rational C, every
positive W_A and the complete signed symmetric star-supported Z_4. It rejects
missing channels, noncanonical or floating values, wrong coverage, asymmetry,
off-star entries and carrier Frobenius norm above 1/64. Partial resource,
conductance or carrier publication is unavailable. Exact FLINT incidence
preserves charge 21. The explicit quartic A_PC profile uses the exact weighted
fixed-row descriptor and graph-bound unit reference; physical W remains separate.

At fixed Arb256, the one selected incoming-state read uses H=I+Z/2 and incoming
W in both the transport and weighted rows. The A_PC equations compute Phi, j0,
G(C,W,j0), q, J and f; the source is O_ij f_i f_j/4. There is no OS predictor,
CI iteration, automatic precision escalation or history substitution. The
fresh residual and flat conditioning satisfy the unchanged declared tolerances.
All reads are bound to the complete C/W/Z subject.

Nearest/even flux128 rounding of the certified current midpoint provides exact
C+=C−32BJ. Two separate writers consume the same selected read:

    log W_ideal = exp(-1) log W + (1-exp(-1)) log G(C_final,W,J_selected)
    Z_ideal = exp(-1) Z + (1-exp(-1)) S_selected.

The W writer uses final represented C and incoming W; the Z writer uses the
incoming-state source. Each rounds nearest/even to the 2^-192 lattice, with
canonical zero off-star entries and identical paired off-diagonal values.
One atomic C/W/Z write follows both writers. A fresh returned-state read uses
both newly written histories. Held-geometry/old-W and reference-H/new-W
diagnostics remain separate from the physical returned read.

The conditional read domain is C in [0,4], W in [.99,1.01] and signed
||Z||_F≤1/64. Exact rational source, closure, drive and eigenvalue bounds are
recomputed for each graph. The weighted selector includes the 127/128 carrier
factor. The selected drive is strictly floor-inactive; both ideal and represented
resource endpoints are checked. No global resource-box invariance is claimed.
Immutable graph, row, history-domain, decay and certificate facts are cached;
changing-state reads and both writers remain fresh.

## Complete represented-map error

Current midpoint enclosure error is at most 2^-192, so flux error is bounded by
epsilon_J=2^-129+2^-192 and epsilon_C[i]=32 sum_j |B[i,j]| epsilon_J.
Both writer midpoint enclosures have radius at most 2^-224. Carrier component
error is epsilon_Z=2^-193+2^-224. The complete log-conductance error is

    epsilon_L = (194/65536) max_i epsilon_C[i] + (100/99) epsilon_Z.

The first term propagates represented final-resource error into the W writer;
the second covers positive-W rounding through log. The selected current is
never replaced by the rounded edge flux inside either writer.

For the complete C/logW chart U and carrier radius rho=2^-30, the product error is

    max(max_i sum_j |U[i,j]| (epsilon_C,epsilon_L,...)[j],
        m epsilon_Z/rho).

The conservative m bound encloses the dense carrier Frobenius error and is
strictly below the recomputed image margin. Independent Arb768 audits compare
represented samples against the entire ideal map, including all three channels.
These are local transition guarantees, not an outside-domain orbit-shadow bound.

## Product domain, event and lifecycle

Exact rational S/U operands span fourteen charge directions and sixteen logW
directions. The product adds all 46 Frobenius-orthonormal symmetric-star carrier
directions, with unrestricted signs. The full derivative includes both uses of
H, W-dependent row ratios, inverse-flat differentiation, final-C W writing and
the independent Z source/writer. One multiple-right-hand-side solve computes
the flat derivative. Product block norms, center defect and strict image margin
are recomputed at Arb256; no research verdict or trajectory is imported.

Membership combines an outward logarithmic chart enclosure with exact squared
carrier norm/rho², returning the squared product-norm upper bound. Boundary
uncertainty fails closed. Exact W-weighted classification includes every
descending route; whole-domain predicates are certified separately.

Current starts with W=4097/4096 and diagonal Z=1/65536; reset starts with
W=8191/8192 and diagonal Z=−1/131072. The event archives both actual complete
histories with fresh reads. Exact A shares 1/128,63/64,1/128 allocate resources,
with zero core and copied exterior. Every old edge retains its W and three new
edges receive one. Both complete target carriers are canonically zeroed under
explicit carrier_history_loss; conductance has exact_transport and no loss.

The existing atomic owner controls invalidation, positive windows, occurrence
identity, once-only gain, rollback and cold journal replay. Near-domain unit
fixtures do not claim an actual approach prefix. Expected current 375→377 and
reset 372→374 remain unverified until .5; aggregate native support stays false.

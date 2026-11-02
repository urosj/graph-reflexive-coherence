# Native A_CI_PC numerical policy

Policy `spark_acipc_arb256_flux128_conductance192_carrier192_v1` implements the
bounded [A_CI_PC law](grc-9-v4-spark-completion-a-ci-pc.md) under the
[native contract](../implementation/phase-9-grcv4/tranche-9/P9-9.1a.6-ACIPC-Contract.md).
Steps 1–4 leave actual source-to-completion execution to a separate .5 campaign.

## Complete state and selected composite root

The existing `grcv4-exact-adaptive-carrier-state-v1` codec stores canonical exact
rational C, positive W_A and the entire signed symmetric star-supported Z_4.
It rejects missing histories, floating/noncanonical values, wrong coverage,
asymmetry, off-star entries and Frobenius norm above 1/64. No partial publication
is available. The explicit quartic A_CI_PC profile binds the exact weighted
fixed rows and graph-bound unit reference separately from physical conductance.

At fixed Arb256, hold incoming C/W/Z during the equation

    S(f)_ij = O_ij f_i f_j/4
    H = I + (Z + S(f))/2
    f = F(C,W,Z,f).

Both potential construction and inverse lowering use that H. Incoming W drives
transport and the weighted rows. Exact rational graph-specific constants prove
a unique root in ||f||_infinity < 1/32 on the conditional C in [0,4],
W in [.99,1.01], ||Z||_F <= 1/64 domain. They include both geometry consumers,
signed-carrier eigenvalue and selector separation, a floor-inactive drive and
an invariant carrier-source envelope. No global resource-box invariance follows.

The numerical proposal starts at zero and uses at most the declared 60 fixed
point iterations at the same precision. Midpoint input/proposal arithmetic has
no physical authority. Re-evaluate F at the actual full input intervals; the
outward residual divided by 1-root_q encloses the unique selected root, and the
entire enclosure must remain strictly inside the flat ball. The same enclosed
f supplies instantaneous S(f), H and the carrier-writer source. Root evidence
retains proposal, residual, error radius, domain, geometry, source, selected
current, joint residual and conditioning. There is no automatic precision
escalation or fallback. Changing-state roots are fresh; only immutable graph,
row, domain, decay and certificate facts are cached.

## Exact continuity and the two writers

The current enclosure must admit a midpoint error <= 2^-192. Nearest/even
flux128 rounding gives exact FLINT C+ = C - 32 B J_rounded and preserves charge.
The unrounded selected current drives both history updates:

    log W_ideal = exp(-1) log W + (1-exp(-1)) log G(C_final,W,J_selected)
    Z_ideal = exp(-1) Z + (1-exp(-1)) S_selected.

The W writer uses final represented C and incoming W. The Z writer uses incoming
Z and the source from the same root that supplied instantaneous geometry.
Writer midpoint errors are <= 2^-224; both outputs round nearest/even to the
2^-192 lattice. Paired off-diagonal carrier entries are identical, with exact
zero off-star entries. One atomic C/W/Z write precedes a fresh full-state root.
Held-H/old-W and reference-H/new-W diagnostics do not replace the returned read.

Let eJ=2^-129+2^-192, eC_i=32 sum_j |B_ij| eJ, eZ=2^-193+2^-224. The full
log-conductance error includes the propagated final-resource displacement:

    eL = (194/65536) max_i eC_i + (100/99) eZ.
    full_error = max(max_i sum_j |U_ij| (eC,eL,...eL)_j, m eZ/rho).

The product radius is rho=2^-30. All components and the conservative Frobenius
bound are checked against the freshly computed strict image margin. Independent
Arb768 checks reconstruct the complete ideal map. These are local represented
transition bounds, not a global outside-domain ideal-orbit shadow estimate.

## Full implicit trapping proof and lifecycle

Authenticated exact rational C/logW chart operands provide 14 charge and
16 conductance coordinates. All 46 symmetric-star carrier coordinates use the
Frobenius-orthonormal basis (diagonal 1, paired off-diagonal 1/sqrt(2)).
The whole outer box contains the product domain. At fixed f, direct C/W/Z
partials include dH=dZ/2. Flat-root partials include dS/2 in both H consumers.
A single multiple-right-hand-side implicit solve computes

    df = (I-F_f)^(-1) F_x,
    dJ = J_x + J_f df.

Propagate through exact continuity, the final-C/incoming-W conductance writer
and dZ+ = exp(-1)dZ + (1-exp(-1))dS. The full 76-dimensional product block
bound, center defect, positive image margin, weighted predicates and represented
map error are recomputed. Neither a fixed-geometry derivative nor a prior-family
proof verdict is imported. Both chiral graphs receive actual graph bindings.

Membership compares an outward logarithmic chart enclosure and exact squared
carrier norm/rho², returning the squared full product-norm bound. Unresolved
boundary cases reject. Exact W-weighted classification checks every route.

Current starts at W=4097/4096 and diagonal Z=1/65536; unadvanced reset starts at
W=8191/8192 and diagonal Z=-1/131072. A fresh source beat precedes the lawful A
event. Both complete histories are archived with fresh selected roots. Old W
is preserved, three new edges receive one, and the entire target Z is explicitly
reset under carrier_history_loss. Resource shares are 1/128,63/64,1/128, with
zero core and copied exterior; W transport and Z loss remain separate channels.

Atomic owner semantics cover positive elapsed windows, occurrence identity,
at-most-once gain, invalidation, failure/retry, reset, replay and checkpoint
recovery. Near-domain tests establish lifecycle behavior only. Native current
375→377 and reset 372→374 are unverified expectations until .5. Aggregate native
completion support remains false.

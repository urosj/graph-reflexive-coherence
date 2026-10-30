# GRC-v4 connected Candidate-A RG2b completion addendum

This bounded successor selects the connected Candidate-A completion for native
conformance. Its conditional authority is
`P9-EC-A-RG2B-CONNECTED-COMPLETION`. It preserves the accepted tree17 result
and does not close the C1 section-regularity debt.

The [connected completion derivation](../../../phase-9-grcv4/tranche-8/P9-ARG2b-ConnectedCompletion.md)
extends the original argument to simple connected nine-port graphs using
incidence, Gram and overlap-mask infinity norms bounded by 9, 18 and 9.
No tree, spectral gap, Candidate-C selector or ATC result is assumed.
The authoritative coordinates are resources C and edge history W; the
auxiliary joint chart uses Y = 512 log W. Its complete equations are

$$
z=B^TC,\quad
J_0=-\operatorname{diag}(W)B^TB
       [\operatorname{diag}(W)z+\tfrac12(H-I)z].
$$

Let each named port-row value be its normalized W-weighted neighbor-resource
difference (zero for an empty row), and let

$$
E_e(C,W,j)=2^{-25}\left[C_u+C_v+
 \sum_{a=1}^3(r_a(u)-r_a(v))^2+j_e^2\right].
$$

The read, feedback, continuity and fresh-resource writer are

$$
g=e^{-E(C,W,J_0)},\quad q=(W-g)/(W+g),\quad
J=J_0/(1-q/32),\quad v=H^{-1}(qJ/16),
$$

$$
S=\tfrac12 A_\star\odot vv^T,\quad C^+=C-2^{-12}BJ,
\quad Y^+=Y+(1-e^{-2^{-12}})[-512E(C^+,W,J)-Y].
$$

All products/divisions in the current equations are componentwise. The fixed
W floor is inactive throughout the proved signed chart; its lower drive
bound is checked, not presumed. Auxiliary C and Y arguments retract to
[-1,5] and [-1,1]. The outer state and physical state are never clipped.
The section satisfies the original inverse graph transform with generated
geometry I+S/2. The unchanged chart nesting, radius 2^-12 and Lipschitz limit
2^-10 satisfy the exact inequalities in the linked derivation for the whole
9/18/9 class. Four terminal-I levels leave a tail below 2^-48.

The numerical successor uses binary64 proposals and fixed 192-bit Arb
certificates of all resource, history and geometry residuals. Computing the
writer via its log drive and expm1 avoids an unnecessary exp/log round trip;
this is an explicit new numerical identity, not a claim of old bit identity.
Native certification may factor B^TB through B; the independent research
checker retains the full edge-space equations. Both use the same mathematics.
Every physical state reconstructs fresh inverse chains; only immutable graph
algebra may be cached. No automatic precision/backend fallback is allowed.

The original prepared large target's reset role has a certified negative first
resource step. A separately declared source-history companion assigns
W=1025/1024 on old edges and transports it unchanged; new bonds retain W=1.
Its exact reference-H zero-extra increment is 3 dt (W-1), and its scaled-log
history is below 1/2, strictly inside the 5/8 ordinary-history chart. The full
joint section certificates establish positive first steps for both roles.
That is a bounded feasibility witness, not a trajectory or event certificate.
Native event staging, both-role continuation, covariance, rollback/replay and
public compatibility remain separate obligations. A Lipschitz completion
grants neither differentiability nor a classical spectrum.

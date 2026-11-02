# Native quartic C_CI numerical bridge

Status: implemented for review in P9-9.1a.6-C_CI steps 1–4. This explicit
successor supplements the scientific CI/earlier-domain contracts. It grants no
aggregate native completion support and makes no source-to-entry claim.
The C_OS policy remains unchanged.

## Declared map and root

Physical state consists only of exact rational resources C. Duration is 32;
charge is 21 on the declared connected 12/13 source and 15/16 target.
With B the incidence matrix, L=BᵀB, O=|B|ᵀ|B| and V'(C)=(C−2)³−(C−2),

    H(f) = I + diag(f) O diag(f)/8
    j₀ = −Bᵀ(BHBᵀC/64 − V'(C))/1024
    y = (3I/4 + HL)⁻¹ j₀
    J = j₀ + y/4
    F(C,f) = H⁻¹y/2
    f = F(C,f),   T(C) = C − 32BJ.

The selected root is unique in ||f||∞≤1/32 for C∈[0,4]^V. There is no
assertion of global uniqueness outside this domain. Exact FLINT rational
Neumann bounds establish a strict self-map and contraction q<1 on the entire
box. Inverse, selector-gap and conditioning predicates remain mandatory.
Generated geometry and continuity current consume the same joint root.

## Represented execution and error

`spark_cci_arb256_certified_root_flux128_v1` uses Arb256 for outward enclosures,
FLINT rationals for state and incidence, and nearest/even rounding on edge
fluxes to the 2^-128 lattice. No vertex-charge repair or binary64 state write
is permitted. Each root proposal starts at zero; the fixed-point iteration
limit is 60. Proposal convergence at 2^-224 is a stopping aid only.
A fresh residual r at the actual input yields the Banach enclosure
||f−f_proposal||∞≤r/(1−q). Whole intervals, not floating residuals, certify it.
The joint geometry residual and declared 1e-11 root admission remain checked.
Each exact selected current must be enclosed within 2^-192 of its midpoint.
Thus each represented flux differs from the ideal current by at most

    εJ = 2^-129 + 2^-192.

The sole physical write is C⁺=C−32B J_represented; its charge is exactly
preserved because 1ᵀB=0. In the full charge chart U, the whole-step error is
bounded by 32||UB||∞ εJ. Completion admission requires this bound to be
strictly smaller than the actual full-domain image margin. It is not an
accumulated trajectory-shadowing estimate. Actual entry must be executed.
A fresh joint root at C⁺ certifies restart admission. The diagnostic read at
C⁺ using consumed H is distinct and never supplies the next step's root.

## Complete invariant-domain certificate

For independent variables C,f, differentiate all occurrences of H. Then

    df/dC = (I−F_f)⁻¹ F_C
    DT = I − 32B (J_C + J_f df/dC).

Arb256 encloses this derivative on the complete 14-dimensional charge chart,
not a symmetry slice. The certificate checks q_map=||U DT S||∞<1 and
1−q_map−||U(T(center)−center)||∞>ε_map, along with robust complete basin
rows, edge order, role, actual graph/ports, charge, policy and profile binding.
A frozen-H derivative or OS corrector is not a CI certificate.

## Precision, caching and failure

The bounded 256/512 comparison retains independent Arb768 Newton checks and
represented-state equality. Higher precision is a verification control, not
an automatic production fallback. Fixed-point proposal stalls, unresolved
root/derivative/inverse bounds, current error over budget, changed graph or
profile, or inconclusive spatial predicates reject without publication.
Only immutable exact graph/reference facts, graph-bound root-domain proofs,
and fully bound domain certificates are cached. Current, root, geometry and
poststate reads are recomputed for each changing state. The same finite
provenance mechanism preserves historical C_OS execution source bytes.

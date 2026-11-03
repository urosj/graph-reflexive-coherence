# Native C_OS spark numerical policy

Implementation supplement for P9-9.1a.2; review pending. This supplements
[the optional scientific contract](grc-9-v4-spark-completion.md) and its
[earlier-domain successor](grc-9-v4-spark-completion-earlier.md). It grants no
public completion capability. The frozen generic schema, binary64 profiles,
release assets and completion-off behavior retain their existing meanings.

## Explicit representation and scope

`spark_cos_exact_flint_flux128_v1` selects FLINT exact rational evaluation and
a fixed final edge-flux lattice of spacing 2^-128. It is bound to C_OS,
c0=2, a=mu=1, eta=1/1024, h=32, kappa_Phi=Lambda=1/64,
tau=1, chi=zeta=kappa_H=1/2, kappa_M=0, unit transport/reference weights,
zero K4 base and zero context. Its implementation checks the complete typed
profile, actual graph coverage, reference digests and supported recipe IDs.
The bounded kernel accepts connected loop-free graphs with 2–32 vertices,
1–64 edges and the proved selector separation below. This is an execution
limit, not certificate or release support for all such graphs.

The explicit site/candidate/resolved successors are
`grcv4-homogeneous-quartic-site-v1`, `grcv4-candidate-c-params-v2`, and
`grcv4-resolved-params-v2`. Exact reduced rational strings encode the site
coefficients, with the selected nondimensional units. V, V' and V'' are
evaluated exactly. The complete resolved successor participates in the
existing generic profile identity hash. Its separate decoder validates all
unchanged sections through the existing typed decoder; it never executes
that predecessor as a substitute for the quartic law.

`grcv4-charge-policy-v2` / `exact_rational_incidence_charge_v1` specifies
`canonical_rational_strings_v1`, `exact_rational_sum` and
`never_mutate_resource`. `grcv4-exact-resource-state-v1` carries exactly
`schema_version`, `graph`, `C`, and `charge`; C follows the graph's live-node
order and its exact sum must equal charge. Negative resources, floats,
noncanonical fractions, missing coordinates and unknown fields reject.
Input, allocation and wire round trips have zero conversion error.
This is a resource capsule, not an owner checkpoint: configuration v3,
completion policy/evidence v2 and lifecycle checkpoint admission belong to .3.

The numerical policy owns an explicit FLINT scope and restores the caller's
scope. Rational construction uses `grc_v4_exact`; inverses use
`grc_v4_numerics` and its operation-owned reuse. No ambient Arb precision,
binary64 intermediate, automatic precision escalation or solver fallback is
used. The old declared binary64 split tolerance is interpreted as its exact
binary64 rational value, without a decimal reinterpretation or widening.

## Exact read and whole represented step

Let B be tail-positive incidence, L=B^T B, O=|B|^T|B| and I the unit edge
Hodge. For input C and selected geometry H, compute exactly

```
s(C) = (C-2)^3 - (C-2)
Phi  = B H B^T C/64 - s(C)
j0   = -B^T Phi/1024
A    = 3I/4 + H L
y    = A^-1 j0
J    = j0 + y/4
f    = H^-1 y/2
```

The predictor uses H=I. Assemble
`Hstar = I + diag(f_predictor) O diag(f_predictor)/8`, then perform one
corrector on the **same C** with Hstar in both the potential and physical
Read-Back. This is the full physical resolvent/similarity equation after exact
algebraic elimination, not an approximation to it. Check the squared
Frobenius norm of `Hstar-H(f_corrector)` against the squared unchanged OS
tolerance; this is a sufficient operator-norm admission test. Failure of a
sufficient numerical bound is `CertificationInconclusive`, not a theorem
that no scientific solution exists.

Round each corrector J once, with signed nearest/even integer arithmetic, to
the 2^-128 edge lattice. Call the resulting vector Jhat and compute
`Chat = C - 32 B Jhat` **exactly**. Preserve J and Jhat as distinct result
fields. Check nonnegative Chat and perform fresh exact final and restart
reads at Chat using Hstar and I. Inverses for those unchanged operators may
be reused within the step; their right-hand sides are always fresh.

Since every column of B sums to zero,
`sum(Chat)=sum(C)` exactly. There is no balancing-vertex correction. If
`epsilon=Jhat-J`, then each `|epsilon_e| <= 2^-129` and

```
Chat - T(C) = -32 B epsilon
|Chat_i - T(C)_i| <= 32 degree(i) 2^-129
||U (Chat - T(C))||inf <= 32 ||U B||inf 2^-129.
```

These are **uniform** bounds, not sampled residuals. All earlier arithmetic
is exact, so they include site evaluation, generated geometry, current solve,
continuity, and all representation conversions. Given a separately validated
trap/chart, exact-charge membership and successful stage admission, a bound
strictly smaller than the image margin proves the represented self-map.
The numeric helper alone does not validate an arbitrary caller-supplied chart
or admit a completion certificate; .3 owns that boundary.

For the accepted 14-dimensional C_OS parallelotope, the retained check
reconstructs S and U, verifies US=I and zero column sums of S, and obtains
an error bound about **4.39102e-31**, below the strict margin **0.00457383**.
No subsequent trajectory is an operand of this calculation.

## Stage domains, conditioning and diagnostics

O is a Gram matrix, so every generated H is I plus a positive semidefinite
matrix. H>=I implies that the nonconstant vertex spectrum is bounded below
by the graph Laplacian spectrum. The connected graph estimate
`2/((n-1)*diameter)>1/64` certifies the constant selector and strict gap.
A is similar to `3I/4 + sqrt(H) L sqrt(H)`, which is positive definite.
Exact inverse/residual identities are checked for each consumed operator.

The runtime uses the sufficient condition bound
`m ||A||inf ||A^-1||inf` and the H bound `m ||H||inf`, compared to the
declared conditioning limit. These also dominate the physical feedback
block's bound `(4/3) cond_2(H)` for m>=2; for a single edge that block is a
scalar with condition one. On the accepted whole domain, exact scalar norm
bounds on the predictor imply Hinf<=Hmax. Consequently

`m ||A||inf ||A^-1||inf <= (4/3) m^2 (3/4 + Hmax ||L||inf) Hmax`.

The retained check verifies this is below the declared 10^12 limit, checks
positive resources on the domain, and compares the accepted whole-domain
OS split upper bound with the exact native tolerance. Thus the new numerical
admission guards introduce no unresolved stage on that domain. The scientific
trap proof itself remains independently bound; a positive numerical budget
does not replace its derivative or geometry proof.

Fixed-row gradients use exact unit-weight means on the sole typed port
graph. Gradient norms are compared squared; signed Hessian diagonals,
resource thresholds, edge order and contrast use exact comparisons. The
spatial evaluator's arithmetic error is **zero for every exact C**, so its
strict seed/anchor flags agree with the scientific predicates throughout the
accepted domain. Equality never becomes a strict predicate. All-route basin
membership and event ancestry remain .3 work, separate from these arithmetic
primitives and from represented-current `basin_identity`.

## Finite source prefix and entry

Read the exact accepted source prestate; do not round it to binary64 or
substitute the saved research poststate. Advance only current through one
actual native source beat. Reset stays unchanged and receives a fresh read.
An explicitly supplied nonnegative column-stochastic allocation matrix M
preserves charge exactly; its error propagation is
`||M deltaC||inf <= ||M||inf ||deltaC||inf`. The checked accepted allocation
has norm one. The native topology allocator reconstructs both chiral target
graphs; resource transfer follows the actual native source output.

The represented trajectory is the authoritative native trajectory. Each
step has the local error bound above. These local bounds do not by themselves
bound its accumulated deviation from the old unrounded research trajectory:
such a comparison would additionally require a certified prefix recurrence
`e_(k+1) <= L_k e_k + delta_k`. This implementation makes no such orbit-shadow
claim and does not import a saved research state to obtain entry. Its entry
contract is to check the **actual exact native state** in the independently
admitted domain, which avoids assuming that a small local error implies the
same entry beat. The short check separately verifies source and event prefix
errors, compares changing-state steps with independent exact/Arb equations,
and preserves the exact inputs for the later public execution.

The full source-to-entry execution and observed 374/375 entry targets remain
.5, after .3 lifecycle integration and .4 measured runtime preflight. No
public endpoint or approximately 400-beat completion claim follows from .2.

## Reuse and retained scope

Only immutable graph-bound reference facts are cached across calls, with a
16-entry limit. Keys include the complete graph payload, including port chart,
ordering and orientation. No state, current, split result or admission decision
is cached. The selected geometry's verified operators are reused only within
their own step. Cold/warm equality, changing-state currents, backend restoration
and orientation/chiral covariance are checked.

The side-tool exposes the retained numerical evidence through a separate
native API/browser/notebook panel. It neither computes a completion decision
nor promotes the scientific witness to public native support. The broad
research native obligations remain pending until their full family review.

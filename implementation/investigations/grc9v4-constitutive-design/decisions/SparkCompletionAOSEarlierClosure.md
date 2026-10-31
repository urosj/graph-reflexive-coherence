# A_OS earlier closure through an anisotropic full-state domain

2026-10-31. Research successor on `investigation/grc9v4-spark-completion`,
pending review. The user prioritizes a substantial reduction through an
anisotropic domain. The accepted A_OS result at `fc723f2c` remains the baseline.
This work changes the certificate, with no change to the equations, physical
duration, allocation, SC-1 predicates, tolerances or retained trajectories.

| Same retained event | Accepted entry → window end | Enlarged ball | Anisotropic domain |
| --- | --- | --- | --- |
| Current | 1039 → 1041 | 627 → 629 | **375 → 377** |
| Reset | 1022 → 1024 | 613 → 615 | **372 → 374** |

The current completion endpoint uses 36.22% of the accepted proof's beats:
664 fewer, a 63.78% reduction. Reset uses 36.52%: 650 fewer, a 63.48% reduction.
Both preserve the two-beat positive window (elapsed physical time 64). These
are stronger witnesses for the same event; they create **zero additional gain**.
The current event retains its one child and reset earns no live gain.

## Domain and full-map proof

The original rational center is unchanged. Write the full physical state in
the smooth coordinates x=(C,log W), with sum C=21. There are 14 independent
resource directions and all 16 conductance directions. R selects the first
14 resource coordinates and all conductance coordinates; E restores the last
resource coordinate by charge conservation. Thus RE=I and every resource
column of E sums to zero.

`AOSAnisotropicDomain.json` declares an invertible exact rational 30×30 matrix
T and strictly positive rational radii r. Define

```
S = E T diag(r)             U = diag(r)^(-1) T^(-1) R
K = { x0 + S z : ||z||∞ ≤ 1 },       U S = I30 exactly.
```

K is a closed, convex parallelotope in the physical charge hyperplane,
complete in its induced norm. The exact inverse and a positive coordinate
neighborhood bound prove full relative interior; no W direction is frozen.
Exponentiation gives a positive, full-dimensional W domain. The physical map
preserves charge algebraically because its resource update is C−32BJ and
the columns of B sum to zero.

FLINT/Arb at 512 bits evaluates the original analytic Jacobian on a coordinate
box enclosing **all of K**, including every resource and writer cross block.
With F the unchanged full C/logW map, the induced infinity-norm bound is

```
q = max_i sum_j sup_K |(U DF(x) S)_ij| < 0.995934130
d = ||U(F(x0)−x0)||∞
1 − q − d > 0.00406586.
```

The mean-value theorem proves contraction; q+d<1 proves strict self-mapping.
Banach therefore supplies the full-map attracting fixed point. Original
positive closure, smooth floor-inactive writer and OS split checks are run
on the whole enclosing box. This is a domain-wide proof, not a spectral-radius
claim at the center or a finite sequence of predicted states.

Floating-point eigenvectors of the coupled center Jacobian proposed T only.
Complex pairs were represented by real/imaginary columns, and all entries and
radii were converted to exact rationals. Neither eigenvalues nor approximate
eigenvector identities are assumptions of the proof. The disclosed discovery
includes unsuccessful shapes and is not described as preregistered.

## Fixed ordering, predicates and entry

For each edge i–j the exact support of its resource contrast over K is
sum_k |S_ik−S_jk|. Bounding the two endpoint coordinates separately would
lose their correlation and fail an edge-order test. Using the actual domain
instead gives a strict minimum edge-order margin above 1.11×10^-5. Weighted
fixed-row predicates are enclosed on the larger coordinate box; every seed,
anchor, barrier and complete basin is resolved for both chiral charts. The
basins remain p:{p,private} and satellite/2:{n2,n8,satellite/2}.

All 2065 retained interval states are authenticated against the accepted
execution/source identities. Their original 8192-bit integration is reused;
the verifier recomputes membership from every retained C and logW interval,
never from stored scalar distances or floating-point state estimates. It
checks both charts and every subsequent retained state. Every earlier state
is strictly outside this particular anisotropic K; the entry and two positive
window states are strictly inside. The compressed check record contains all
membership bounds and full original-state checkpoints around entry and the
last ordering reversal. No physical trajectory is rerun or shortened in place.

The last edge reversal is `positive-2` (satellite/3–n3): current 364→365,
reset 352→353, proved from disjoint interval endpoint differences. A forward
invariant SC-1 domain with uniform edge order cannot contain a pre-reversal
state from the same orbit: it would also contain the later opposite ordering.
This is an obstruction to earlier **entry**, not a proof that a qualifying
domain exists immediately after reversal. Current entry 375 is ten beats
later; the earliest possible window under this obstruction is 367. We do not
claim global optimality. Spatial basin gain at current beat 92 alone cannot
satisfy the fixed-order trapping requirement.

## Enlarged-ball comparison and review limits

The attached proposal is retained as `UserEarlierClosureProposal.txt`.
The same Arb implementation reproduces its max(||dC||P,256||dlogW||2)≤1/5000
comparison and the 627/613 entries. Exact rational LDL elimination on the
charge tangent proves (2/5)P ≺ D0 ≺ 14P. Hence the P-self-adjoint reference
return has norm at most 79/80. Actual ellipsoidal edge support is
r sqrt((ei−ej)^T A0 (ei−ej)); row predicates still use a valid outer box.
The conservative Arb bound is q<0.999768493, with strict image margin above
4.6301×10^-8. This slightly differs from the attachment's external-backend
bound; the retained Arb result is the one asserted here.

The certificate reuses the accepted analytic Jacobian and trajectories. It
is not an independently derived Jacobian or an independent trajectory replay.
Tests exercise positive and negative secants in all 30 oblique directions,
rank/history/radius/source controls, exact support and spectral inequalities,
and a complete deterministic interval recheck. Review/adjudication is still
required to adopt the earlier endpoints. Native completion, hierarchy, other
families and G4 receive no new support. The next family remains A_CI after
this requested investigation; no A_CI campaign has started.

## Reproduction and side-tool

```
.venv/bin/python implementation/investigations/grc9v4-constitutive-design/scripts/check_spark_completion_a_os_earlier.py --check
.venv/bin/python implementation/investigations/grc9v4-constitutive-design/scripts/test_spark_completion_a_os_earlier.py
.venv/bin/python implementation/investigations/grc9v4-constitutive-design/scripts/test_spark_completion_a_os_earlier_surfaces.py
```

The new read-only API `/api/spark-completion/applicability/a-os/earlier`,
browser panel and notebook cell `spark-completion-a-os-earlier` show the
comparison and source evidence. They verify retained bindings without running
numerical proofs. The accepted and historical research projections remain
unchanged through a finite metadata successor. Large check evidence is XZ
compressed. `AOSEarlierValidation.json` records the actual checks and the
previously documented repository audit failure separately.

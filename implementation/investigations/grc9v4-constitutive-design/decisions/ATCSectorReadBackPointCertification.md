> Relocation-only maintenance: repository paths and dependent identities were
> rebuilt before first commit. Scientific statements, numerical results and
> review verdicts are unchanged; the new identities are not an independent
> reviewer rerun. Earlier byte-preservation statements describe the pre-move stage.

# CAN-LSF — certifying the fixed enabled point

**Status:** successor mathematical certificate for review, not acceptance of
nonzero-feedback scope or a second claim/debt adjudication. The
[qualified review](../evidence/autonomous-topology-change/review/CAN-LSF-ReadBack-Qualified-Pass.md)
independently reran the predecessor's mathematical core using neutral helpers,
checked its exact target inequalities and verified its identities. This was
not a reported native or complete repository-wrapper execution. The reviewed
[proposal](./ATCSectorReadBackLiftProposal.md),
[diagnostic results](./ATCSectorReadBackLiftResults.md), checker and record stay
unchanged. Their historical pending-review labels are superseded only to the
extent stated by the review: finite evidence and the conditional target
theorem pass; nonzero scientific acceptance and second adjudication remain held.

## 1. What this successor certifies

Follow the review's point-first order. Keep the same a=19/4, h0=1/8,
chi_A=1/16, gamma=1/1024, kappa_H=kappa_Ah=1, alpha=beta=0 and tau_A=h0/log(2).
Keep the prepared four-star C0=(1,1,1,1,5), paired W0 values 361/400 and
5929/6400, unit references and the same source-only sector-to-site prescription.
The role-local edge lineage and bridge seed one do not change. Neither do
the allocator, source stage, fixed OS tolerance 1/512 or failed-beat semantics.

The [exact-enclosure checker](../scripts/certify_atc_sector_readback_point.py)
and its [certificate](../evidence/autonomous-topology-change/ATCSectorReadBackPointCertificate.json)
address precisely the missing finite premises:

1. The initial guard is inactive; the first ordinary beat is positive and
   OS-admissible. Read-Back, generated geometry, its consumption and the
   gamma-dependent writer are provably nonzero at this point.
2. At the committed poststate, strict separation, inflow, x/y cone and
   **old/source spectral guard** margins hold. The last quantity is not a
   full-feedback instability eigenvalue. The event current is freshly
   recomputed selected reference-stage current, never the previous consumed
   current or a target-derived quantity.
3. The source activity ratio lies strictly inside one round-even dyadic bin,
   fixing k=30779 with positive child funding. No target search is involved.
4. Every preceding unsplit beat is OS/resource/writer admissible and the
   tenth proposed resource state has a certified negative coordinate.
   At the event boundary, resetting W to one without splitting also fails
   through a certified negative resource proposal on its seventh attempt.
   Both rejecting attempts pass the OS residual bound; no failed output is
   advanced and no writer is run after its resource rejection.
5. The separately transported live and actual reset first target beats pass
   and enter the already-proved return domain. Only one target beat per role
   is needed: the reviewed theorem supplies the infinite tail.

This proves obstruction along this fixed prepared source trajectory; it does
**not** prove that the old source guard implies obstruction for every source
passing that guard under nonzero feedback. The no-event counterfactual is a
proof consumer, never an event-time lookahead operand.

The enclosure run passes. The following deliberately widened rational bounds
are readable consequences of the full dyadic endpoints in the certificate:

| Certified quantity | Outward rational range |
| --- | --- |
| Source sector separation | (0.01251, 0.01253) |
| Old/source spectral guard margin | (0.03075, 0.03077) |
| Smallest reference inflow | (0.09933, 0.09935) |
| Distance of grid coordinate from nearest rounding tie | (0.2665, 0.2666) |
| First current-target squared deviation | (0.25545, 0.25546) |
| First reset-target squared deviation | (0.33111, 0.33112) |
| No-split rejected minimum resource, attempt 10 | (-0.23693, -0.23691) |
| History-reset-only rejected minimum resource, attempt 7 | (-0.16399, -0.16397) |

Each displayed terminating decimal denotes an exact rational endpoint, not
a rounded equality. The certificate retains full integer endpoints; inspection
of these larger margins does not require a trajectory rerun.

## 2. Exact outward arithmetic

An interval is encoded as integer endpoints [l/2^256,u/2^256]. Addition and
negation are exact on this grid; products, quotients and rational input
conversion use integer floor/ceiling bounds. A divisor containing zero fails
closed. Squaring uses zero as its lower bound when the interval crosses zero;
it never treats dependent x*x as an independent-sign product for norm bounds.

For exp(x), x<=0, enclose each endpoint separately by monotonicity. Write
x=-2^s t with 0<=t<=1/8. The alternating Taylor sums satisfy

$$
\sum_{j=0}^{49}\frac{(-t)^j}{j!}
\le e^{-t}\le
\sum_{j=0}^{48}\frac{(-t)^j}{j!}.
$$

All terms and sums are exact fractions; the decreasing-term alternating
remainder proves the bounds, independent of a transcendental library.
Round outwards once, then square outwards s times. Exact zero gives [1,1].
For sqrt, integer `isqrt` supplies l^2<=2^256*input_lower and
u^2>=2^256*input_upper. No floating approximation determines any certificate
sign or threshold. Scalar kernel checks cover signed arithmetic, zero-crossing
squares, rational square roots and rejection of uncertain division/rounding.

The retained writer is evaluated in the algebraically equivalent form

$$
W^+=\sqrt{W\,\max(1/2,e^{-\gamma J_{\rm fresh}^2/2})}.
$$

The computed enclosures prove the floor is inactive on every consumed stage
and successful writer. Log evaluation is unnecessary: the return condition
y>=-1/8 is proved by lower(W)>upper(exp(-1/8)), together with W<=1.
Interval Gaussian elimination encloses the regenerated form H^-1 r; every
pivot interval must be positive. This is not a second OS corrector.

Every stage encloses the full map in the reviewed proposal. In particular,
pre-read W_hat uses the stage baseline, while the retained writer uses the
fresh selected current. The corrector structural form uses the inverse of
the generated edge Hodge. Frobenius residual bounds imply the required
operator-norm admission. The resource proposal is tested before its writer.

## 3. Structural premises and discrete decisions

Paired equality is supplied by the reviewed exact-real symmetry argument,
not inferred from overlapping numerical intervals. The two independent leaf
swaps fix the graph, prepared C/W, unit references and scalar parameters.
Each staged operation is equivariant, hence their fixed subspace is invariant.
The checker verifies the relevant source/target graph automorphisms. Strict
inter-sector separation is then enclosed at the actual event boundary; no
near-equality tolerance is introduced and no perpetual separation claim made.

For enclosed grid coordinate z=65536*A_u/(A_u+A_v), the checker requires

$$
k-1/2<\underline z\le\overline z<k+1/2.
$$

An interval touching a tie is rejected as unresolved. This proves the unique
bin at this point; it does not discharge generic/native DB-10. Conservation is
an exact algebraic invariant: initial charge is nine, incidence columns sum
to zero, and the dyadic transfer columns sum to one. Summing dependent interval
coordinates need not give an interval of zero width and is not the proof of
exact charge. Old histories are transported separately for current and reset.

## 4. Composition with the passed infinite-time theorem

For each actual role the certified first target state satisfies

$$
\sum C=9,\qquad
\|C-(3/2)\mathbf1\|_2^2<4/9,\qquad
-1/8\le\log W_e\le0.
$$

The reviewed conditional theorem applies at this fixed enabled parameter
point (which lies in its proved box). From that first admitted target state,

$$
X_n\le(9209/10240)^n X_0,
$$

all later resource coordinates stay above 5/6, the OS residual and history
domain remain admitted, and log W tends to zero. This combines a finite
enclosure proof of entry with an analytic infinite tail. It does not
extrapolate a finite sampled trajectory into indefinite continuation.

The resulting bounded statement is: at this prepared nonzero-feedback point,
the unchanged reference-source prescription yields a target restoring both
roles, whereas enabled no-split and history-reset-only continuation reject
through resource positivity. It is a mathematical result pending review,
not a universal fission law, production event, native rounding proof or a
newly accepted profile.

## 5. Review disposition and next boundary

The supplied review independently verifies predecessor digest
`4f12d56fd3cccf87925613b021eaed34ecc3087a3403c06b3e7c6023e23fa4a3`, checker SHA
`49b39bee5d6aa98577d98dbf3f046db02fc0b58ea528bc0d06920da07d924680`, proposal SHA
`bc633922044f222e595d71f37c6807870bf5b31d0adfe4015fbea8edc74375f4` and scoped
zero-channel adjudication digest
`8e25258e9b728f034c008fb71d7efa1cf9455dbdea8059c66835a5a54de2105a`.
It does not independently review this new certifier or its certificate.

Next review the point certificate, then attempt the original compact box's
source and entry implications. Cover all reachable prescribed dyadic bins;
do not shrink the box merely to keep k=30779. Retain failure, and require a
justified successor proposal for any changed region. The uniform target
theorem is already available; no target or grouping redesign is indicated.

Nonzero-feedback scientific scope acceptance and the second adjudication
remain held pending review of the new source/entry certificate. Original
claims/debts, zero-channel acceptance, source readmission, formation, native
lifecycle, other families and aggregate ATC-2 retain their prior dispositions.

Reproduce from the repository root without overwriting evidence:

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python implementation/investigations/grc9v4-constitutive-design/scripts/certify_atc_sector_readback_point.py
```

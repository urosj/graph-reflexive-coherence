# GRCV4 performance evidence

## Production numerical-policy integration — 2026-10-14

The opt-in policy now lives in `src/`, with no research callback dependency.
See the [integration record](../../corrections/GRCV4-CertifiedNumericalPolicy.md)
and [exact replacement formulas and conditions](../../../specs/grc-v4-numerical-policy.md).
The [production source-pass record](certified_native_os_pass.json) completes
in 140.517 s worker wall time (133.606 s OS pass), clean child exit 0, and matches
both retained research point summaries and the exact split operands. The runner
does not change the fixture or tolerances. It records zero whole steps/events;
P9-8.4g remains open. This 96,201-byte record is below the compression threshold.

The sections below describe **historical research attempts**, including their
then-accurate statements that `src/` was unchanged. They are not claims about
the successor production tree. Their measured scripts/records remain intact;
source bindings are authenticated against pre-integration Git commit
`5b9836358af2873e524e6ceae7256639e8a6bbce`. A clone must include that object;
missing history fails explicitly. Non-source bindings remain current-byte
checks. The new production run has independent current-source bindings; retained
verification is not a rerun of either large numerical trajectory.

## Exact weighted split certificate — 2026-10-14

The [explicit successor](../../../scripts/benchmark_grcv4_split_certificate.py)
replaces only the research harness's OS split decision with
`flint_exact_weighted_row_sum_os_split_v1`. The native driver, predictor/corrector,
geometry assembly, selector-path check, fixed 256-bit Arb solves, exact rounded
residual requirements and Hodge positivity policy are unchanged. No production
`src/` changes or new admission authority.

### Proof domain and exact arithmetic

Let R be the **exact difference of the two staged Hodge matrices**, and let the
declared reference pairing be D=diag(w), with every w strictly positive. The
certificate checks dimensions, exact symmetry of R, positive diagonal D,
nonnegative tolerance and exact dyadic inputs. It computes with FLINT rationals:

$$
b=\max_i\frac{\sum_j |R_{ij}|}{w_i}.
$$

The symmetric matrix S=D^(-1/2) R D^(-1/2) is similar to D^(-1) R. Consequently

$$
\|S\|_2=\rho(D^{-1}R)\le\|D^{-1}R\|_\infty=b.
$$

Thus b<=t proves the **unchanged reference-normalized OS split condition**,
including equality. Neither inverse, square root, eigenvalue estimate nor
inertia is computed. Zero tolerance admits the zero residual; an exact subnormal
defect cannot be rounded away. The native residual display is preserved, including
`values=None` when an exact entry cannot round to finite binary64; display never
decides admission. The complete exact-defect digest and a named proof are retained.

If b>t, the outcome is **certificate inconclusive**, not scientific rejection:
the bound can overestimate the true norm. There is no inertia fallback, second
OS correction, changed tolerance or precision retry. The implementation uses a
research-only split-result subclass; it does not spoof global inertia counts.
Native typed-operand, common-reference and OS norm-policy guards remain present.

The split proof applies to any topology and positive diagonal reference weights.
Dense work is quadratic in the number of **edges**, not vertices. This does not
broaden the enclosing experimental current policy, which still requires its
identity reference pairings and constant-selector witnesses. Nor does it imply
that every graph/state satisfies the bound. General non-diagonal reference
pairings are explicitly outside this certificate's domain.

### Completed bounded source OS pass

The [retained successor](weighted_split_os_pass_probe.json) **completes** its
single 300 s capped attempt in **139.353 s worker wall time**. Materialization
takes 4.584 s; the instrumented native OS pass takes 132.904 s (remaining time
is process startup, retained comparisons, communication and cleanup).
Predictor/corrector take 24.255 s / 69.740 s, and the unchanged native selector
path takes 18.108 s with one certified segment. All fourteen solves retain their
rounded-residual passes. All eight Arb rounded-output digests match the previous
run; the full predictor summary matches the earlier exact-materialization result.

The weighted split check, including exact defect construction, proof, digest and
display serialization, takes **1.291 s**, versus at least 162.589 s unfinished
under native exact inertia. Its actual exact weighted-row bound is
approximately **1.0585306884e-24**, below the unchanged binary64-declared **1e-8**
tolerance. This is the bound on the **difference** of the staged matrices;
the earlier 1.656e-12 bound summed their separate deviations from identity and
was much looser. No tolerance or arithmetic staging was changed to obtain this.

This completes one **source/current instrumented C_OS pass**, not a complete
ordinary step. Resource continuity, charge, final-C readmission, target/reset
roles, other profiles and production policy integration are not established by
this result. `native_steps=0`, `native_events=0`, and `production_admission=false`
remain explicit. P9-8.4g remains open. The previous timed-out records remain
unchanged rather than being overwritten by this successful successor.

Process detail: the inherited supervisor receives the complete result, allows
0.1 s for child teardown, then terminates a still-live child. This record therefore
has `outcome=completed` **and `worker_exitcode=-15`**. The command exits 0 because
the pass and retained comparisons returned successfully; this is not a claim of
clean child-process exit. No numerical result is inferred merely from termination.
The focused tests distinguish a returned result from process teardown explicitly.

Retained verification checks source and record bindings, exact predictor
agreement and the two runs' Arb-output digests, then independently reconstructs
the staged comparison Hodges from retained causal-flat outputs and recomputes
the actual split certificate/digest. It does not rerun currents or replace the
original execution. The complete new record is 149,972 bytes, below the 1 MB
compression threshold.

### Pressure and reproduction

The [focused tests](../../../tests/models/test_grc_v4_split_certificate.py)
compare against exact native inertia for weighted equality and adjacent limits,
zero/subnormal/extreme-scale cases, and thirty seeded small symmetric matrices.
They cover signed edge permutation invariance, normalization that materially
changes admission, invalid/nonsymmetric/non-diagonal inputs, exact display
overflow, and an admitted weighted case that this sufficient bound leaves
inconclusive. Small complete native passes agree in currents, Read-Back,
intermediate matrices, selector paths and split results; failure restores hooks
without inertia fallback. No broad trajectory campaign is implied.
The final focused suite passes **10 tests in 9.577 s**, including retained split
reconstruction. Only one large native pass was run for this successor.

Reproduce with an unused repository-relative output path:

```sh
PYTHONPATH=src:.:tests OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  .venv/bin/python scripts/benchmark_grcv4_split_certificate.py \
  --policy source_os_arb_256_exact_weighted_split_v1 --seconds 300 \
  --output implementation/evidence/grcv4-performance/weighted_split_os_pass_rerun.json
```

## Explicit Arb LU with certified binary64 rounding — 2026-10-14

The [successor policy](../../../scripts/benchmark_grcv4_arb_policy.py) selects
**Arb LU at exactly 256 bits** for all declared non-diagonal predictor/corrector
solve roles. Previously declared diagonal roles retain exact diagonal solving;
this is a fixed role map, not algorithm selection after a failed attempt.
It uses the already installed python-flint 0.9.0. No production `src/` changes.

Inputs must be represented exactly by Arb at this precision. The LU result
encloses the exact solution; each outward-rounded interval endpoint is extracted
as an exact rational. Both endpoints must propose the same finite binary64 value,
and the entire closed interval must fit **exactly** inside that value's
round-to-nearest/even cell. Midpoint ties use significand parity; signed underflow
maps to native canonical positive zero; overflow never becomes an admitted entry.
The exact rounding-cell check is independent of the floating conversion proposal.
The result is the uniquely certified rounded matrix, not its unchecked midpoint.

Arb does not materialize the exact rational solution or claim an explicit AX=B
rational identity. Its enclosure plus rounding proof replaces that intermediate
representation. Existing exact conditioning proofs run first; **all unchanged
native rounded residual checks still run afterwards**. The earlier explicit Hodge
positivity policy remains selected, including both unrounded and represented
affine matrices. Native selector-path and split admission are unchanged.

There is no precision escalation, approximate mode, exact inverse fallback or
silent retry. Unresolved input representation, nonfinite/unresolved intervals
or failed Arb certification stop as `certificate_inconclusive`; this is not
proof of scientific singularity or inadmissibility. Worker timeout remains a
separate `resource_limit`. Old scripts and execution records are unchanged.

The [focused tests](../../../tests/models/test_grc_v4_arb_policy.py) cover pivoting,
nonsymmetric and nearly singular systems, multiple RHS, exact ties, intervals
straddling ties, signed zero/subnormal/overflow boundaries, a deliberately wrong
floating conversion proposal, precision exhaustion, native small-pass matrix and
Read-Back equivalence, conditioning/residual/split rejection, context restoration,
and bounded worker failure/termination without fallback. This is still research
instrumentation, not production integration or new runtime admission authority.

### Measured solver progress on the retained large source

The 100-node/400-edge predictor finishes in **24.172 s**, compared with 79.676 s
in the exact-materialization predecessor. The generated-geometry corrector
finishes in **69.625 s**. All 14 solve calls across the two stages pass their
unchanged exact rounded-residual checks; eight use Arb and six use their
explicitly declared diagonal method. Every Arb output entry has unique-rounding
certification at the fixed 256-bit precision. No precision retry occurs.

The corrector structural-flat solve that previously exceeded 188 s now takes
**6.958 s** for solving, certification and exact residual checking: LU itself
0.964 s, exact rounding-cell checks 3.986 s, residual checks 1.341 s, plus input
conversion and digest overhead. The stronger per-entry rounding-cell checks
explain the overhead relative to the earlier informal endpoint-only diagnostic;
this is not an unexplained change of solver precision or tolerance.

Both native physical-current closure residuals pass. The native selector-path
certificate then completes in **18.108 s**; the regenerated comparison Hodge
completes in 3.046 s. This distinguishes completed solver/stage evidence from
the separate final split-admission gate. Neither a complete step nor resource,
charge, final-C, event, target/reset or all-realization admission follows from
these successful stages.

The [retained run](arb_policy_os_pass_probe.json) reaches its **300 s cap in
native split admission**, which starts at elapsed 137.411 s and remains unfinished
after at least **162.589 s**. Worker wall time including termination is 300.184 s;
the command exits 2 with `outcome: resource_limit`. This is neither a completed
OS pass nor a numerical rejection. No retry or fallback follows. The remaining
cost is the native exact-inertia gate, not an unfinished Arb solve.

Retained checking authenticates the record and sources, checks the fourteen-call
roster and predictor-current digest against the prior exact result, then
reconstructs the actual 400-RHS structural-flat matrix from retained predictor
data and reproduces its certified rounded output and exact residuals. This does
not rerun the trajectory or claim the unfinished split gate passed. Small native
pass comparisons separately cover all intermediate matrices and final admission.

Reproduce the capped attempt with an unused repository-relative output path:

```sh
PYTHONPATH=src:.:tests OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  .venv/bin/python scripts/benchmark_grcv4_arb_policy.py \
  --policy source_os_arb_lu_256_unique_binary64_v1 --seconds 300 \
  --output implementation/evidence/grcv4-performance/arb_policy_os_pass_rerun.json
```

The remaining question at this predecessor was to certify the **same normalized OS split condition** with an
explicit bounded method, preserving its tolerance and arithmetic stages, or stop
as inconclusive. The weighted split successor above now addresses that question.
Production integration and full-step admission remain separate work.
This record is below the 1 MB compression threshold.

## Explicit FLINT Hodge positivity — 2026-10-14

The [successor harness](../../../scripts/benchmark_grcv4_hodge_positive.py) adds
an explicitly selected **exact FLINT rational positivity certificate** to the
preceding predictor/corrector policy. Earlier measurements already used FLINT for
exact scalar/matrix work, but the native Hodge positivity routine converted
dyadics to Python integers and used Python-loop fraction-free elimination.
Selecting the FLINT backend did not replace that routine.

### Exact proof and unchanged arithmetic boundaries

For actual symmetric H and a fixed positive s, define

$$
E=H/s-I,\qquad d=\max(\|E\|_1,\|E\|_\infty).
$$

If d<1, symmetry and the induced norm inequality imply

$$
0<s(1-d)\le\lambda_{\min}(H)\le\lambda_{\max}(H)\le s(1+d).
$$

The run fixes **s=1 before execution**. Symmetry, exact dyadic entries, the
norms and the strict inequality are all checked with FLINT rationals. There is
no floating eigensolver, tolerance, inverse, elimination or scale search. Outside
this sufficient domain the run stops as **certificate inconclusive**, never
silently switching to the old checker or declaring the geometry inadmissible.
This is not a complete positive-definiteness decision for every SPD matrix.

The native affine Hodge construction is unchanged. Instrumentation requires its
two positivity sites in order: the unrounded exact affine matrix and the staged
binary64 represented matrix. Each receives its own certificate, exact matrix
digest and timer. Other reconstructed/retained Hodge checks use the same declared
method and have distinct labels. Native selector-path and normalized OS split
admission still use their original algorithms. This remains research
instrumentation, not production integration or a change of scientific identity.

### Larger-graph measurement

On the unchanged 100-node/400-edge source, the instrumented predictor completes
in **79.676 s**. The formerly unfinished source-geometry construction now
completes in **2.974 s**, including **0.472 s** for the unrounded affine Hodge
certificate and **0.545 s** for its represented counterpart. Their exact matrix
digests differ: the second check does not reuse the first one's result.
Both lower eigenvalue bounds exceed 1-8.3e-13. The previous attempt spent over
209 s in this geometry stage without completing; this is a bounded witness
comparison, not a general full-pass speedup claim.

The corrector policy setup, including its selector/Hodge witness, completes in
6.358 s. Its non-diagonal structural-flat conditioning certificate passes;
the subsequent fixed Dixon solve computes H X=I for 400 right-hand sides.
That matrix is genuinely consumed by the existing implementation, unlike the
earlier discarded regularity inverse. Avoiding it by directly solving H x=j
would change the existing matrix-rounding/application stages unless equivalence
were separately established.

The [retained successor](exact_policy_hodge_positive_probe.json) reaches its
**300 s cap in that structural-flat solve**, after at least **188.120 s** in the
solve. It exits 2 with `outcome: resource_limit`, no completed-pass result, no
fallback, and no numerical rejection. The complete corrector, selector-path and
split checks have not run to completion. Worker wall time is 300.293 s including
termination. All computations use the explicitly selected single-thread FLINT
exact backend; no tolerance or production source changes are involved.

The next performance question is now **full-matrix exact materialization**, not
Hodge positivity or the discarded inverse guards. A useful successor would
explicitly select a certified-enclosure/unique-binary64-rounding method for the
matrix solve, preserving every existing represented entry and residual check.
It must have a declared precision/work budget and stop as inconclusive if it
cannot prove a unique rounding, including zero/subnormal/tie cases; it must not
fall back to unbounded exact elimination. This method was **not implemented in
this predecessor**; the Arb successor above now supplies it.
Another whole pass with unchanged exact matrix materialization would not answer
that question efficiently; first test the isolated corrector structural-flat
matrix, then return to the pass. Any genuinely different arithmetic/output
contract requires an explicit reviewed policy rather than a silent optimization.

Reproduce this bounded attempt with an unused repository-relative output path:

```sh
PYTHONPATH=src:.:tests OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  .venv/bin/python scripts/benchmark_grcv4_hodge_positive.py \
  --policy source_os_exact_hodge_positive_v1 --seconds 300 \
  --output implementation/evidence/grcv4-performance/exact_policy_hodge_positive_rerun.json
```

Retained checking authenticates sources and the preceding attempt, then
reconstructs both affine matrices from the earlier retained predictor's
causal-flat output to recheck their exact certificates. It does **not** rerun
currents or turn this incomplete pass into success. The source-bound report
is below 1 MB; old scripts and measurements are preserved unchanged.

### Scientific and numerical pressure

The [focused tests](../../../tests/models/test_grc_v4_hodge_positive_probe.py)
check spectral endpoints against independent exact inertia and the original
elimination; positive, singular, indefinite and nonsymmetric matrices; the strict
d=1 boundary and adjacent binary64 values; invalid shapes/nonfinite/non-dyadic
inputs; empty spaces; and extreme exact scales, including subnormal and
above-binary64-range values. A positive exact matrix that rounds to a singular
matrix demonstrates why **both** arithmetic-stage checks are necessary.

An SPD matrix outside the fixed-scale proof domain is an explicit inconclusive
control, with no elimination retry. Small complete OS passes agree exactly with
the unchanged implementation at tau=0 and tau=1, including current, Read-Back,
intermediate matrices, selector paths and split admission. A native split failure
remains a failure, and callbacks are restored after exceptions.

## Generated-geometry corrector policy — 2026-10-14

The [successor harness](../../../scripts/benchmark_grcv4_os_pass.py) extends the
explicit research policy to the generated-geometry C_OS corrector and runs the
actual `CandidateCOSPass` driver. It does **not** change production `src/`.
The predictor keeps its previously measured policy; the corrector has a fixed
Dixon solve for every non-vertex matrix role, including the structural flat map,
identifications, resolvent and physical current. The vertex pairing is explicitly
restricted to identity. No algorithm search or fallback occurs.

### Larger-graph attempt: resource limit, not a completed pass

The [retained attempt](exact_policy_os_pass_probe.json) has outcome
`resource_limit`, exit status 2 and no completed-pass result. Its fixed deadline
is 300 seconds. The actual 100-node/400-edge predictor completes in **78.716 s**;
all seven solves pass exact identity and unchanged rounded residual checks, and
its native physical closure residual passes. Source-geometry construction starts
at elapsed 90.766 s and has not finished at the deadline: **at least 209.234 s**
in that stage. Neither the corrector nor selector-path/split admission is reached.
The 300.241 s worker wall time includes termination overhead. Single-thread FLINT
and the numerical environment are recorded.

This is a new bottleneck before the corrector, not evidence that the corrector's
solves have failed. `H_profile` includes exact positivity of the unrounded affine
Hodge and of the retained represented Hodge; its non-diagonal positivity checker
uses Python-level, fraction-free integer elimination with growing integer sizes.
The timer covers the whole source-geometry construction, **not an isolated
profile of those positivity calls**, so it does not assign all 209 seconds to
that checker. The earlier predictor speedup alone does not establish usable
full-pass performance.

The next bounded task is an explicitly selected exact sufficient positivity
certificate for **both** actual Hodge matrices, timed separately from assembly.
For symmetric H and positive scale s, an exact bound
`max(||H/s-I||_1, ||H/s-I||_infinity) < 1` proves H positive definite.
It must check actual symmetry/entries, retain the original two arithmetic stages,
and return inconclusive outside its proof domain, with no silent elimination
fallback. This is a proposed extension, **not installed in this attempt**.
After small native-equivalence pressure, resume the full-pass measurement;
the generated-geometry direct-solve cost and the native path/split costs remain
unmeasured. No step, resource/charge admission, event or P9-8.4g closure follows.

Reproduce the bounded attempt with an unused repository-relative output name:

```sh
PYTHONPATH=src:.:tests OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  .venv/bin/python scripts/benchmark_grcv4_os_pass.py \
  --policy source_os_exact_generated_geometry_v1 --seconds 300 \
  --output implementation/evidence/grcv4-performance/exact_policy_os_pass_rerun.json
```

An exit status of 2 signals an incomplete/failed attempt, not scientific
rejection. Inspect `outcome` and the last stage. The retained-integrity test
authenticates this original capped attempt; it neither reruns nor completes it.
The report is below 1 MB and duplicates no dense matrices.

### What the extension proves

The corrector checks a constant selector but does **not** assume a scalar actual
Hodge. It reconstructs the actual rounded retained Hodge H and proves symmetry
and positivity with an exact positive-scalar-centred norm bound. With beta=zeta*chi
below one and nonnegative tau, the exact pre-rounding regularity block

$$
(1-\beta)I+\tau B^T B H
$$

is similar to a positive definite symmetric matrix, so the discarded regularity
inverse is unnecessary. This is a nonsingularity proof, not a claim about that
block's Euclidean condition number. The actual represented resolvent is checked
against the scalar Gram comparison centre used by the preceding probe; its exact
perturbation now includes **all non-diagonal geometry and assembly-rounding
effects**. Other matrix roles use the explicit scaled-identity condition bound.
All solved equations satisfy exact AX=B before rounding, and every rounded RHS
passes the unchanged native residual criterion. Native Read-Back and physical
closure are still evaluated.

Native source-geometry positivity, selector-path certification and normalized OS
split admission are deliberately left unchanged and timed separately. In
particular, this is not a blanket replacement of inverses outside the declared
current-solver roles: the existing nonmonotone selector-path method can still
construct a centre inverse. That is an unchanged admission algorithm, not a
fallback from this research solver policy.

### Focused pressure and limits

The [focused tests](../../../tests/models/test_grc_v4_os_pass_probe.py) compare
both full small-graph OS passes and materially non-diagonal correctors with the
unchanged exact implementation, for tau=0 and tau=1. Currents, Read-Back, baseline,
potential, retained Hodge, all intermediate matrices, split residual and selector
path agree exactly where the policy certifies. Tests also preserve native
split rejection, forbid hidden inverse/conditioning fallback inside current
solves, inject solver/certificate failures, reject unknown roles, and check
callback restoration.

A stronger non-diagonal small-graph control passes native admission but exceeds
the sufficient resolvent certificate's domain. The experimental policy reports
**certificate inconclusive**. This control is retained as a limitation, not
reclassified as a scientifically inadmissible geometry. These tests establish
bounded stage fidelity, not a general replacement for native admission.

## Resolvent certificate and complete predictor — 2026-10-14

The successor [research harness](../../../scripts/benchmark_grcv4_resolvent_predictor.py)
finishes the unchanged 100-vertex/400-edge C_OS source/current predictor using
an **explicitly injected experimental numerical policy**. Production `src/`
is unchanged. This runs the actual `CandidateCCurrent` assembly, selector,
Read-Back and closure-residual code, not merely the isolated physical solve.
It is neither a complete predictor/corrector OS pass nor lifecycle admission.

| Work in this run | Observed time |
| --- | --- |
| Complete instrumented predictor | **78.611 s** |
| Native input materialization (outside predictor timer) | 4.615 s |
| Policy witness setup, including an extra selector check | 0.876 s |
| Complete worker, including imports and retained-result comparisons | 86.358 s |
| Retained-resolvent conditioning | **0.153 s** |
| Retained-resolvent exact 400-RHS solve | 43.888 s |
| Resolvent exact identity, rounding and residual verification | 10.398 s |
| Physical-current exact solve in this run | 6.590 s |
| All conditioning calls inside predictor | 1.357 s |

The earlier production probe did not complete this predictor in 900 seconds.
That comparison demonstrates a substantial improvement on the measured witness,
not a controlled full-step speedup or a guarantee for all geometries. The
resolvent solve plus verification now accounts for about 69% of predictor time.
All seven named solves pass exact equation and unchanged rounded-residual checks.
Native physical Read-Back closure also passes. The physical block, baseline and
rounded current exactly match the previous retained direct-solve probe.

### Certificate, including represented assembly error

For the declared scalar retained Hodge h I, set

$$
R_0=I+\tau h B^T B,\qquad E=R_{\mathrm{represented}}-R_0,
\qquad \epsilon=\max(\|E\|_1,\|E\|_\infty).
$$

With h>0 and tau>=0, positivity of the Gram matrix and the norm inequality
give singular-value bounds for the **actual represented matrix**, even when
E is nonsymmetric:

$$
\sigma_{\min}(R_{\mathrm{represented}})\ge 1-\epsilon,
\qquad
\sigma_{\max}(R_{\mathrm{represented}})
\le 1+\tau h\|B\|_1\|B\|_\infty+\epsilon.
$$

The ratio certifies conditioning only if the lower bound is positive and the
ratio meets the existing limit. All coefficients, perturbations and comparisons
are exact rationals; no inverse, numerical eigenvalue estimate or omitted
rounding error is used. On this source predictor epsilon is exactly zero, and
the condition upper bound is about 19.00000104 against the unchanged 1e8 limit.
The standalone certificate took 0.155 s. Pressure tests include nonzero rounding
error and nonsymmetric perturbations, independently checking the resulting
singular-value endpoints with exact Gram inertia.

### Explicit experimental policy and limits

The worker installs a fixed numerical callback map only for its lifetime:
diagonal solves for roles proved diagonal, Dixon for the resolvent and physical
current, the Gram/perturbation certificate for the resolvent, and the earlier
identity-norm certificate for the physical block. Every role and timing is in
the report. Unknown roles, invalid structures, unresolved certificates and direct
solver errors stop the run, without trying another method. The worker has an
enforced deadline; unsuccessful CLI execution exits nonzero.

The two inverse calls used only as guards are explicitly replaced with proofs:
positive-Gram regularity for the exact pre-rounding block, and certified
nonsingularity for the represented physical block. Their returned value is
unused by the native caller. This instrumentation returns no fictitious inverse
and **must not become a generic inverse API**. The value-producing vertex-Hodge
inverse is the checked identity. No original admission predicate is skipped.
Certificate bounds change, not the condition limit, staged arithmetic or output.

This policy is restricted to a reference-geometry predictor with identity
pairings and a constant selector. Nonuniform/generated geometry, the OS
corrector, target/reset predictors and other realizations have not been run.
The mathematical perturbation bound can cover more matrices, but the callback
map cannot be applied to those stages without extending and testing its contract.
No general topology law, P9-8.4g closure or new runtime support follows.

Artifacts: [standalone certificate](resolvent_condition_probe.json),
[complete predictor](exact_policy_predictor_probe.json), and
[focused pressure tests](../../../tests/models/test_grc_v4_resolvent_predictor_probe.py).
The records are small (about 44 KB for the complete predictor); shared inputs
remain in the already compressed block and unchanged source declaration. No
dense matrices are duplicated. Retained tests authenticate inputs and sources,
compare the prior block/current and re-evaluate closure residuals; they do not
reexecute the complete predictor. Failure-injection tests check that numerical
callbacks are restored and no hidden inverse/legacy conditioning is called.

Reproduce with fresh output names, from the repository root:

```bash
PYTHONPATH=src:. OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python scripts/benchmark_grcv4_resolvent_predictor.py certificate --policy source_predictor_exact_gram_perturbation_v1 --seconds 30 --output implementation/evidence/grcv4-performance/runs/resolvent-condition.json
PYTHONPATH=src:. OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python scripts/benchmark_grcv4_resolvent_predictor.py predictor --policy source_predictor_exact_gram_perturbation_v1 --seconds 180 --output implementation/evidence/grcv4-performance/runs/exact-predictor.json
PYTHONPATH=src:.:tests OPENBLAS_NUM_THREADS=1 .venv/bin/python -m unittest tests.models.test_grc_v4_resolvent_predictor_probe -v
```

The next engineering work is a real, explicitly selected numerical component,
not publication of these callback patches. Preserve the different regularity,
conditioning and residual obligations. Broader stage support still needs its
own applicable certificate/solver choices; unavailable proof is inconclusive,
not a license to switch methods silently.

## Exact direct-solve feasibility probe — 2026-10-14

Research/benchmark only: **no production implementation or new native admission**.
This tests the unchanged P9-8.4g C_OS source/current predictor (100 vertices,
400 edges). The earlier inverse diagnostic did not retain its matrix; this
probe reconstructs the represented block from the retained declaration, with
literal stage rounding. It does not substitute the fused exact-real equation.
Small triangle fixtures at tau=0 and tau=1 match the native block, baseline
and rounded current exactly. The restricted reconstruction requires connected,
simple, unit-weight topology, identity reference Hodge and a kernel-only selector;
the direct linear solver itself does not impose those restrictions.

| Explicitly selected work | Measured result |
| --- | --- |
| Prepare retained resolvent (Dixon, 400 RHS columns) | 43.761 s solve; 58.569 s complete preparation worker |
| Physical-current exact direct solve (Dixon, one RHS) | 3.893 s |
| Exact verification of L J = J0 | 0.131 s; passed |
| Existing rounded-current residual test | 0.033 s; passed |
| Existing exact Gram/PSD conditioning method | 120 s resource limit; incomplete, not rejection |
| Separately selected exact identity-norm certificate | 0.459 s; certified condition number below 1.00000000086 |

These are single local measurements, not a general speed guarantee. The
previous profiled inverse remained unfinished after at least 390.6 seconds,
but that is not a controlled end-to-end speedup comparison. The direct
solution has rational denominators up to 41,913 bits: it is not an approximate
floating-point proposal. Rounding still occurs at the original binary64 stage.

The alternative conditioning proof is explicit and sufficient, not universal.
For nonzero declared scale s, put E=A/s-I and
d=max(||E||_1, ||E||_infinity). Then ||E||_2<=d. If d<1,
the singular values lie between |s|(1-d) and |s|(1+d), so
kappa_2(A)^2 <= ((1+d)/(1-d))^2. All quantities in the checker are rational.
Here s=1 and d is about 4.256e-10; the declared condition limit remains 1e8.
When the bound is unavailable or insufficient, the method reports
**inconclusive**, not mathematical rejection, and does not call another method.
The report contains the exact rational endpoints; displayed decimals are summaries.

Artifacts and consumers:

- [Compressed matrix/RHS and declaration binding](direct_source_predictor_block.json.xz):
  3,715,925 original bytes, 880,568 stored bytes; registered in the root storage
  manifest. The two probe scripts consume this shared block directly from XZ.
- [Preparation](direct_source_predictor_prepare.json),
  [direct solve](direct_source_predictor_dixon.json),
  [bounded old conditioning attempt](direct_source_predictor_condition.json), and
  [explicit norm certificate](direct_source_predictor_identity_condition.json)
  retain source hashes, selected methods, deadlines, outcomes and timings.
- [Focused tests](../../../tests/models/test_grc_v4_exact_direct_probe.py) cover
  exact/inverse equivalence on small matrices, pivoting, nonsymmetry, near
  singularity, multiple RHS, scale extremes, rounding ties/underflow/overflow,
  singular and invalid inputs, admission-boundary equality, exact solve versus
  rounded residual failure, small native reconstruction and deadline/failure
  handling. The norm certificate is checked against independent exact Gram
  inertia on small examples, including inconclusive but well-conditioned inputs.
  Retained checking authenticates sources, recomputes the inexpensive certificate
  and rounded residual, but does not rerun the large exact solve or conditioning.

The recorded exact-solution identity is an execution observation, not a
self-contained rational solution certificate: exact fractions are represented
by their digest, while the rounded current is retained. Reproduce the rational
solution with the explicit solve command below when needed. Neither successful
linear solving nor this one condition certificate establishes the nonlinear
Read-Back residual, final-resource/charge admission, OS corrector, event or step.

From the repository root, use fresh ignored output paths (existing outputs are
never overwritten). Commands do not silently chain into alternative methods:

```bash
PYTHONPATH=src:. OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python scripts/benchmark_grcv4_exact_direct.py prepare --algorithm dixon --seconds 180 --block implementation/evidence/grcv4-performance/runs/direct-block.json.xz --output implementation/evidence/grcv4-performance/runs/direct-prepare.json
PYTHONPATH=src:. OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python scripts/benchmark_grcv4_exact_direct.py solve --algorithm dixon --seconds 120 --block implementation/evidence/grcv4-performance/runs/direct-block.json.xz --output implementation/evidence/grcv4-performance/runs/direct-solve.json
PYTHONPATH=src:. OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python scripts/benchmark_grcv4_identity_condition.py --seconds 10 --block implementation/evidence/grcv4-performance/runs/direct-block.json.xz --output implementation/evidence/grcv4-performance/runs/direct-condition.json
PYTHONPATH=src:.:tests OPENBLAS_NUM_THREADS=1 .venv/bin/python -m unittest tests.models.test_grc_v4_exact_direct_probe -v
```

The legacy conditioning comparison is optional: invoke the first script with
`condition --algorithm dixon --seconds 120` and the same `--block`, plus a new
`--output`. For that job the report explicitly names `existing_exact_gram_psd`;
the required solve-algorithm option is unused, and no solve occurs.

Conclusion: exact direct solving is promising enough for a production design,
without approximate/exact fallback. It does not yet remove the expensive
multi-RHS resolvent construction or supply cheap certificates for every block.
Production integration must make solve/certificate choices explicit, preserve
stage rounding and residual guards, and distinguish certificate inconclusiveness
and resource limits from scientific rejection. A's scalar physical current stays
unchanged. No all-family speedup or P9-8.4g closure follows.

## Earlier grid measurements

This directory retains measured V4 grid runs, numerical-work counts, profiles,
source hashes, and paired strict-public comparisons. The [implementation
closeout](../../corrections/GRCV4-MatrixPerformanceCloseout.md) explains the
changes and their contract boundaries. The runnable public grid declarations
remain in [examples/grcv4](../../../examples/grcv4/README.md).

For the larger original grid, see the [6×6 A_OS FLINT comparison](grid_transport_6x6_flint_comparison.md),
which pairs the pre-optimization five-step run with the current exact CPU backend.

Start with the [A realization comparison](grid_transport_a_realizations_comparison.md),
[primitive reuse comparison](grid_transport_a_primitive_reuse_comparison.md), and
[shared matrix API validation](shared_matrix_api_validation.md). The
[Candidate C comparison](grid_transport_c_realizations_comparison.md) covers
all five C realizations, and the [exact PSD comparison](grid_transport_c_exact_psd_comparison.md)
shows the later shared conditioning improvement. Linked JSON files contain the
raw per-step measurements and complete declarations/results; timing samples
are local observations, not statistical estimates.

The `grid_transport_*` files were relocated from `examples/grcv4/results/`
after the measurements. Historical source-hash keys and runtime commit IDs
still name the files and revisions that were actually measured. Those hashes
were not recalculated to describe the new layout. Navigational links between
reports now point here; the relocation itself did not rerun or alter the
numerical experiments.

From the repository root, the benchmark-only harnesses now live under `scripts/`:

```bash
PYTHONPATH=src:.:tests .venv/bin/python scripts/benchmark_grcv4_grid_a.py --realization CI --rows 4 --cols 5 --steps 5 --reuse
PYTHONPATH=src:.:tests .venv/bin/python scripts/benchmark_grcv4_grid_c.py --realization CI --rows 3 --cols 4 --steps 5 --reuse
PYTHONPATH=src:.:tests .venv/bin/python scripts/benchmark_grcv4_grid_continuation.py --candidate C --realization PC --rows 3 --cols 4 --steps 5
```

The harnesses write new reports to the ignored `runs/` folder here by
default, so a repeat cannot overwrite curated evidence. `--output` selects
another location for an explicitly retained run. Ordinary grid runners in `examples/grcv4` remain usage examples and
keep their own optional output behavior. A benchmark control changes only the
observer's fact lookup/continuation return, not the production solver policy.

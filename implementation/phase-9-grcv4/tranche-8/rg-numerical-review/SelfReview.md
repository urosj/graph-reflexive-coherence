# P9-8.0 actual RG implementation: local adversarial review

2026-10-02. **Four implementation-verification defects reproduced and corrected;
bounded corrected implementation passes this local review.** This is the agent's
own review requested by the user, including a separately written 90-digit oracle.
It is not an externally independent audit, and it does not retroactively extend
the earlier reviewers' verdicts. The user explicitly accepts this own review
and RG-NR1–4 corrections through the 2026-10-02 acceptance/commit instruction.
This resolves the bounded actual-implementation review checkpoint under the
user-requested review method; aggregate P9-8.0 disposition remains open.

## Subject and method

The baseline is the actual `test_p980_rg2b_numerical.py` at
`42976ed60da397a95de95b0361454e39ffbf9643`, with its real repository dependencies.
The corrected subject is that file plus the retained
[numerical-correction.patch](./numerical-correction.patch). The
[pressure owner](../../verification/test_p980_rg_implementation_review.py) exercises
the numerical consumer directly, including failures the RG event guard already
prevented. No dependency reconstruction supplies the implementation under test.

The review covers complete residual accounting, every chain depth, frozen
completion, finite/shape/domain boundaries, input ownership, represented versus
intended-exact inputs, actual output fields, field semantics, legal equilibria
and very large finite queries. Mutation tests reuse a valid returned chain only
to isolate the subsequent physical read/write boundary: the actual section
consumer still recertifies that chain. They do not replace the interval oracle.

## Reproduced findings and corrections

| Finding | Baseline failure | Correction and regression |
| --- | --- | --- |
| RG-NR1: incomplete physical read certification | `ordinary()` checked resource/history errors only. Corrupted baseline/source fields, even a nonfinite or incomplete source, could be returned. A current-coordinate perturbation of `2^-35` passed because its resource effect is scaled by the short duration. | Validate complete binary64 shapes/finiteness and certify J/baseline against saved point references at `<2^-40`, source at `<2^-64`. All twelve A/C substitutions reject. These are the existing event-consumer budgets, not relaxed thresholds. |
| RG-NR2: producer-owned mutable operands | A writer could overwrite caller W and returned J after computing a correct W result; the original function accepted it. A read using its inputs/H as scratch could destroy caller state or certified H and fail for the wrong reason. | Snapshot entry C/W; build independent references before producers; provide private C/W/H and writer C/W/J arrays; own returned arrays. Three lawful scratch controls now pass while preserving entry state and published geometry/current. |
| RG-NR3: returned depth did not bind the requested recipe | `section()` requested A4/C6 but accepted a substituted A5/C7 chain. Its error estimate was valid for the returned depth, but it silently changed the declared evaluator recipe. | Validate requested depth and require returned chain length to match it. Both substitutions reject. Explicitly requested valid alternative depths remain available for auxiliary research. |
| RG-NR4: intended-exact input bypassed point-domain admission | A represented target core of `-2^-45` was accepted when the separately supplied intended-exact core was zero. Only the intended input's physical domain was checked. | Validate both point and intended domains before solving. Certify point evaluation errors separately from composed intended truth. Both invalid point cases reject; two valid intended-exact intervals excluding rounded operands still pass. |

The first five regression methods against the baseline produced **17 failing
assertions and two erroring scratch controls**, retained in
[pressure-before.txt](./pressure-before.txt). Repository-absolute prefixes in that
historical traceback were removed for portability; failures and messages are
unchanged. After the corrections those five methods passed, recorded in
[pressure-corrections.txt](./pressure-corrections.txt). The expanded ten-method
campaign is recorded separately below.

Related input hardening validates interval-vector shape/finite endpoints and
positive exact W before logarithms, and binds consumed parameters/index/B/D/I/
star mask to the graph reconstructed for the certificate. These changes align
the original numerical boundary with its mathematical assumptions. They do not
register another native profile or claim arbitrary graph support.

For `ordinary(..., exact_c=..., exact_w=...)`, `exact_*` and `certificate` retain
the intended-input interpretation; `point_certificate` and the full output error
fields explicitly certify the saved represented point. When no intended inputs
are supplied, both certificates coincide. A represented point need not belong
to a separate intended-exact interval, but each must satisfy its own admission
conditions. This separation is necessary for next-history counterfactuals.

## Mathematical and field-accounting review

No defect was found in the finite-chain residual inequalities, coupled error
solution, or output-section truncation bound. The implementation evaluates all
state and geometry residual coordinates at every returned depth. The graph
hypotheses, terminal identity, symmetry/support and global geometry ball remain
checked; poisoned values cannot gain acceptance merely by carrying small
producer-reported error scalars.

The actual field is precisely

`input_error = SECTION_LIP * full_error(chain.x[0], exact_query)`.

It is the weighted section contribution. Dividing it by `SECTION_LIP` before
applying inverse sensitivity is therefore correct. The output tail uses
`q^N V`; the first-inverse allowance correctly uses `q^(N-1) V`. Centering the
section enclosure on the first independently evaluated source image retains
propagation, truncation and input errors, with returned-H publication error
still bounded separately. No numerical sweep convergence assumption replaces
the residual test.

The completion acts on arguments at every depth; backward states themselves
are not clipped. Its signed-C conductance extension permits negative exponents
and drives above one while retaining the proved inactive floor. A negative
auxiliary predecessor is not a negative physical published state. The original
positive-chart completion remains incompatible with prescribed target zeros.

The original source/target physical continuation and effect tests pass after
the corrections, and **all original numerical JSON report fields are exactly
unchanged**: 50 read stages, 44 named effects, minimum full-gate ratio
`1.371312206257596`. This does not prove a global error bound over every
completion input. The current construction's exact-real theorem supplies
section existence/invariance; an interval defect containing zero is only
numerical consistency.

## Edge, outlier and independent-equation pressure

The expanded campaign passes **ten methods**. In addition to the finding
regressions, the [report](./pressure-report.json) retains:

- **34 chain rejections:** perturb each state/geometry depth and exercise empty,
  oversized, nonfinite, wrong-shaped and unsupported-geometry chains. A smallest
  positive subnormal on a required zero support coordinate also rejects.
- **33 input/model rejections:** invalid point shapes/dtypes, NaN/infinity,
  negative resource and excluded upper face, incomplete/nonfinite exact inputs,
  changed model arrays/index/parameters and invalid A histories.
- **Eight equilibria:** both candidates, both graphs, constant resources zero
  and three, with unit A history. Identity geometry and zero current remain
  legal; no artificial universal nonzero-effect requirement is introduced.
- **Four clamp-face controls:** each candidate at exact auxiliary resource
  faces -1 and 5, with alternating A history-coordinate faces -1/+1.
- **Six finite outliers:** mixed signs at `1e16`, `1e100` and maximum binary64.
  All fail the numerical certificate. This is a precision/budget limitation,
  not proof that the exact globally completed section is undefined there.
- **Two intended-exact controls:** valid intended resources deliberately exclude
  a rounded point coordinate; weighted query error and point certification stay
  separate.

`DecimalEquations` independently assembles incidence, edge Gram, vertex-star
mask and port rows from graph endpoints. It uses a private 90-digit mpmath
context and literal A read/conductance/writer formulas. C evaluates the full
physical/retained similarity `Q^-1 R_hat Q` with `Q=H^-1` on this constant sector,
rather than calling the reduced NumPy or interval response implementation.
It calls none of the represented or interval constitutive methods to produce
expected increments, sources or currents.

At the two actual reset target queries and two mixed exterior queries, it
checks every original-chain increment/source entry against the interval
formula, independently computes original residuals and verifies they are below
the reported bounds. It then refines the actual returned chains for sixteen
sweeps against the intended query and checks refined H and physical read fields.

| Query | Entries enclosed, no misses | Refined maximum residual |
| --- | ---: | ---: |
| A physical target | 1,700 | `<9.089e-46` |
| A exterior | 1,412 | `<1.990e-47` |
| C physical target | 2,182 | `<1.074e-44` |
| C exterior | 1,894 | `<1.360e-46` |
| Total | **7,188** | All `<1e-28` diagnostic threshold |

The 90-digit results are numerical cross-checks, not a substitute for outward
interval certification. They cover those four named queries, not all possible
inputs or a uniform floating-point theorem. Existing event tests retain both
roles; this separate expensive refinement campaign specifically uses reset and
exterior probes.

## Reproduce and remaining disposition

From the repository root, with dependencies in the linked package requirements:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python implementation/phase-9-grcv4/verification/test_p980_rg_implementation_review.py --report
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python implementation/phase-9-grcv4/verification/test_p980_rg2b_numerical.py --report
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python implementation/phase-9-grcv4/verification/test_p980_rg_event_companion.py --report
```

The baseline snapshot results retain their original filenames. Corrected-owner
results are [numerical-corrected-report.json](./numerical-corrected-report.json)
and [numerical-corrected-run.txt](./numerical-corrected-run.txt); corrected-dependency
event results are [event-corrected-report.json](./event-corrected-report.json) and
[event-corrected-run.txt](./event-corrected-run.txt). The ten-method pressure
summary is [pressure-run.txt](./pressure-run.txt). These runs use Python 3.12.3,
NumPy 2.4.6 and mpmath 1.3.0 with one OpenBLAS/OMP thread, as in the baseline
[environment record](./environment.json); corrections ran from the working tree.

The portable export distinguishes pinned baseline source, corrected working-tree
source and local review evidence in its manifest. It includes the original
numerical owner under the review directory's exported `baseline/` subtree so
another reviewer can reproduce the findings without reconstructing that owner.

The requested own review is complete: all ten pressure methods, four original
numerical methods and seven event methods pass. Every nominal numerical and
event report field is unchanged.
Its authorship is explicit; it is not a second-party independent verdict.
The user explicitly accepts the findings/corrections and this bounded review
disposition on 2026-10-02. All-ten disposition/restriction review and aggregate
acceptance remain separate. No production hold is released by this checkpoint,
and no mathematical witness retuning was needed.

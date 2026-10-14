# GRCV4 certified numerical policy — production integration

**2026-10-14; accepted by the user for commit.** This is the shared numerical
component requested during P9-8.4g, not acceptance of that checkpoint or a new
scientific support declaration. Older versions and the default execution policy
are unchanged.

## Contract and exact replacements

The [specification supplement](../../specs/grc-v4-numerical-policy.md) is the
formula-level reference: previous computation, replacement, assumptions, proof,
arithmetic staging, limits and explicit failure for every changed role. It
covers rounded solves, general and C-resolvent conditioning, Hodge positivity,
both C regularity guards and OS split admission. The existing accepted
specification release/package is not rewritten as a numerical-policy release.

The implementation is [grc_v4_certification.py](../../src/pygrc/models/grc_v4_certification.py),
reached through the existing [numerics API](../../src/pygrc/models/grc_v4_numerics.py).
`certified_arb_256_weighted_v1` requires explicit FLINT selection.
`legacy_exact_v1` remains the default. This is a numerical execution choice,
not a new constitutive equation or profile identity.

| Production consumer | Integration | Unchanged obligation |
| --- | --- | --- |
| Shared rounded solve | Exact diagonal division or fixed 256-bit Arb LU; exact whole-interval binary64 rounding-cell proof | Actual coefficient/RHS stages, conditioning limit and exact rounded residual |
| Generated geometry | Exact positive strict diagonal dominance, separately on unrounded and represented operands | Symmetry, typed construction and actual represented Hodge |
| Candidate C | Gram/perturbation resolvent bound; positive-similarity regularity; actual physical-block bound and solve | Selector and baseline/potential/Read-Back equations; all materialization stages |
| A_OS and C_OS | Exact weighted split bound on the actual staged Hodge difference | Declared reference normalization and tolerance; no extra correction |
| Candidate A | Reuses shared flat solve, geometry and OS split | Direct diagonal physical-current law and its existing checks |
| Generic lifecycle / nine-port event owner | Captured policy, restored with backend at numerical entry points | Atomic publication, receipts, reset semantics and scientific wire bytes |
| Private matrix facts | Policy-tagged reuse, rejection of cross-policy continuation | No rounded matrix stored as an exact inverse |

The shared proofs are not silently restricted to the measured identity-reference
fixture. The production scalar-center condition proof fixes `s=A[0,0]` before
attempting certification; the Hodge proof accepts positive strict row dominance;
the C Gram comparison allows positive nonunit vertex weights and non-scalar
retained Hodge. These generalizations are stated and justified in the supplement
and tested separately. They remain **sufficient** domains, not complete decisions
for all invertible/SPD matrices.

An unresolved proof raises `CertificationInconclusive` before publication. It
does not fabricate a scientific rejection receipt. There is no hidden inverse
fallback, precision escalation, tolerance change or clipping. Exact `inverse()`
and `solve_positive()` callers retain their exact contracts and can still be
expensive. Arb input enclosure alone is insufficient: this policy requires exact
inputs and a uniquely certified rounded output.

Owners expose their policy. Duplication preserves it; loading a scientific
snapshot/checkpoint selects the active policy explicitly. Reproduction therefore
records/reselects policy, FLINT version and thread settings outside scientific
state. Existing serialized scientific bytes do not imply an execution choice.

## Evidence and focused verification

The [production run](../evidence/grcv4-performance/certified_native_os_pass.json)
uses [the capped native runner](../../scripts/benchmark_grcv4_certified_native.py)
without research callbacks. On the unchanged 100-vertex/400-edge C_OS source:

- Worker wall time **140.517 s**, setup **4.758 s**, native OS pass **133.606 s**.
- Predictor, corrector, native selector-path and split admission complete.
- Both complete retained point summaries and the exact split-operand digest
  match the preceding research result. The weighted split bound is
  `21469553/20282409603651670423947251286016` (about `1.05853e-24`), below the
  unchanged declared `1e-8` tolerance.
- Child exit **0**, no teardown termination, no fallback. This separately closes
  the earlier research supervisor's process-exit caveat without rewriting it.
- `native_steps=0`, `native_events=0`, `aggregate_closed=false`. A constitutive
  OS pass is not a whole ordinary step or a larger-graph lifecycle campaign.

The [production tests](../../tests/models/test_grc_v4_certified_policy.py) cover
rounding ties/subnormals/overflow and exact-input limits; singular/ill-conditioned
and valid-but-inconclusive cases; unchanged residual rejection; weighted split
limits against exact inertia; nonunit weights and nonconstant selector; C
predictor/corrector parity; full small A_OS/C_OS public step, receipt, observation,
snapshot, duplicate/load/reset parity; policy ownership and atomic rollback.
Nine-port event/checkpoint parity and retained production-record integrity are
also checked. These are bounded conformance cases, not all-ten certification.

The first **37 tests passed** across production policy, existing numerics/matrix
facts and legacy backend checks. The **48 historical research regression tests
passed**, retaining earlier timed-out attempts and the successful research pass.
The final production-policy suite passes **11 tests in 7.158 s**, including the
added nine-port event/checkpoint and retained-record checks. Their first test-only
errors used a nonexistent lifecycle-result serializer and a research proof field
that was not stored; checks now compare emitted receipts/checkpoints and derive
the exact margin from the recorded bound/tolerance. No numerical criteria or
production behavior changed. No second large pass or full historical campaign
was run.

Portability: all seven FLINT-specific production/research test modules explicitly
skip when the optional package is absent, before importing their FLINT helpers;
the missing-dependency paths were checked separately. Production imports still
do not require FLINT unless its backend/policy is selected. Existing runtime and
maintenance hash rosters are refreshed; the two new runtime paths belong to the
existing generic numerics owner, not an invented specialization acceptance.
Metadata-only binding checks do not claim that the full Phase 9 audit was rerun.

```sh
PYTHONPATH=src:.:tests OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  .venv/bin/python -m unittest tests.models.test_grc_v4_certified_policy -v

# A new execution gets a new output path; never replace the retained run.
PYTHONPATH=src:.:tests OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  .venv/bin/python scripts/benchmark_grcv4_certified_native.py \
  --policy certified_arb_256_weighted_v1 --seconds 300 \
  --output implementation/evidence/grcv4-performance/certified_native_os_pass_rerun.json
```

The native record is 96,201 bytes; compression is not required. Retained integrity
checking hashes current production sources and compares retained results; it
does **not** rerun the large numerical trajectory.

## Historical evidence and remaining Phase 9 scope

The research records and measured scripts are unchanged. Their source bindings
resolve against pre-integration commit
`5b9836358af2873e524e6ceae7256639e8a6bbce` using the
[historical-source helper](../../tests/models/_grc_v4_research_sources.py).
Non-source research inputs/scripts must still match their recorded local bytes.
A clone needs that Git object; a shallow clone without it cannot authenticate
the historical source and fails explicitly. These checks establish what ran
then, not conformance of today's implementation. The production successor has
its own current-tree source bindings and result identity.

P9-8.4g remains open. Next is the native large-source **complete ordinary step**,
including continuity, represented charge and final-C readmission, followed by
the still-required target/reset and family-specific admission evidence. Retain
the original pointwise sign bounds and fixtures; do not infer full-step success
from this pass or small-case parity. Other profiles' nonlinear/domain obligations
and `.h` readiness remain separate. No claim/debt status or accepted G2/G3 support
is promoted by this execution optimization.

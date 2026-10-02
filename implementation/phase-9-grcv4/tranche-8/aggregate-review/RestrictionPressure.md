# R1–R10 focused pressure check

2026-10-02. **PASS: no restriction changed and no new blocking defect found.**
This follow-up answers the user's request to pressure the restrictions before
acceptance. It adds boundary checks to the aggregate review; it does not record
acceptance, widen the admitted domain or repeat the full continuation campaign.

The [new boundary owner](../../verification/test_p980_restriction_boundaries.py)
and selected existing methods pass **ten methods** in the retained
[execution log](./restrictions-run.txt). The original aggregate report already
covers twenty paths, 200 target beats, 103 injected event defects and 2,048
linear-transfer corners. Those counts are reused, not credited as new runs.

| Restriction | Evidence and edge pressure | Result and limit |
| --- | --- | --- |
| R1: pinned graph/layout | Fresh scope tests check exact endpoint ports, capacity 58, reordered fixture lists and ambiguous selections. New checks reject requested capacities 0/51/53/58, alternate chirality and adjacent phases in the pinned recipe. | Pass. Rejecting a different research recipe says nothing about general allocator feasibility at those capacities. |
| R2: fixed parameters/stages/horizon | New checks reject target horizons 0/9/11, current source counts 0/2, a reset source beat, altered duration and relaxed split tolerance. Existing recipe mutations reject gain and detection-stage changes. | Pass. The actual ten-beat trajectories remain the aggregate evidence; eleven-beat admission is not inferred. |
| R3: numerical/proof coverage | Fresh realization-budget tests reject equality at the strict source/image/contraction bounds. New RG physical checks admit zero and the last binary64 value below four; negative subnormal resources, four itself and exterior values reject. | Pass. These are actual guard tests, not a uniform event-neighborhood floating-point theorem. CI and RG retain their own distinct domain contracts. |
| R4: supplied A history | Earlier aggregate mutations reject changed old-edge W and invented C W. Fresh CI/PC/CI+PC and RG tests admit lawful W=1 zero-current equilibria; RG history checks reject zero, negative and positive values outside its log-history agreement chart. | Pass. Legal equilibria do not need a nonzero effect; other realizations' W charts are not replaced by the RG chart. |
| R5: carrier type/reset/loss | New checks admit the exact closed radius and its inner neighbor, reject one ULP outside either signed radius, and reject subnormal asymmetry/disjoint support even when naive squared norms could underflow. Symmetric supported subnormal entries remain legal. Fresh carrier tests reject malformed arrays; prior aggregate controls bind complete archives, order, stage, zero reset and separate loss channels. | Pass. Radius admission cannot replace tensor type; archived history still incurs the selected carrier loss. |
| R6: completion-relative RG | Fresh RG tests admit eight lawful equilibria and four auxiliary clamp-face cases; six extreme finite queries fail numerical certification. New physical-face checks keep auxiliary values -1 and 5 outside physical admission. | Pass. The completion remains mathematically global; finite arithmetic is allowed to fail its certificate on extreme queries. |
| R7: charge | Independently recounted all twenty retained scalar budgets from physical operation counts: 197 times `2^-40` for current and 187 times `2^-40` for reset. Every exact recorded discrepancy satisfies its bound. Initial encoding remains separate. | Pass for the research bound. No native pairwise-sum tolerance, resource repair or runtime charge gate is tested. |
| R8: legacy-defined domain | Rechecked the specification's saturated port-5 obstruction and no-mutation requirement against the freshly checked source ports. | Contract remains explicit. No legacy runtime rejection/rollback or forty-cell acceptance is claimed here. |
| R9: later native work | Checked the acceptance checklist still leaves aggregate acceptance, native implementation and Tranche 9 execution open. | Scope boundary remains intact; research rejection tests cannot establish transaction rollback. |
| R10: provenance | Verified all 248 prior manifest hashes before adding this follow-up. Own-review attribution and unavailable external CI/RG script limits remain recorded. | Integrity check passes; hashes do not authenticate an external reviewer or create independent authorship. |

The one-ULP/subnormal cases supplement the earlier coarse cancellation,
malformed-output and extreme-query tests. Negative zero is treated as numerical
zero, not incorrectly rejected as a negative resource or carrier. The resource
and carrier tests explicitly distinguish open from closed boundaries.

## Reproduce the focused run

From the repository root with the existing project environment:

```bash
PYTHONPATH=implementation/phase-9-grcv4/verification OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python -m unittest -v \
  test_p980_restriction_boundaries \
  test_p980_scope_binding \
  test_p980_event_companion.EventCompanionTests.test_binding_rejects_incomplete_or_different_recipes \
  test_p980_revised_realization_bounds.RevisedRealizationBoundTests.test_realization_budget_boundaries \
  test_p980_realization_numerical.RealizationNumericalTests.test_carrier_domains_and_legitimate_zero_equilibrium \
  test_p980_rg_implementation_review.RGImplementationReviewTests.test_equilibria_clamp_faces_and_outliers
```

[restrictions-integrity.txt](./restrictions-integrity.txt) retains the integrity
and scalar-budget check result. Recompute those checks with:

```python
import hashlib, json
from fractions import Fraction
from pathlib import Path

root = Path('implementation/phase-9-grcv4/tranche-8/aggregate-review')
manifest = json.loads((root / 'manifest.json').read_text())
assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest() == digest
           for p, digest in manifest['files'].items())
report = json.loads((root / 'report.json').read_text())
assert len(report) == 20
for name, path in report.items():
    role = name.rsplit('_', 1)[1]
    assert path['physical_source_steps'] == (role == 'current')
    assert path['physical_target_steps'] == 10
    limit = (10 * path['physical_source_steps'] + 17
             + 17 * path['physical_target_steps']) * Fraction(1, 2**40)
    assert limit == Fraction(path['charge_limit'])
    assert Fraction(path['charge_error']) <= limit
```

The updated manifest includes this addendum and the new checker; its file count
therefore differs from the historical pre-addendum integrity result.

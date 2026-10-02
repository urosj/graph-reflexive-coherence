# P9-8.0 aggregate own-review evidence

Repository baseline: `d508fa0`. Disposition and restrictions:
[aggregate review](../P9-8.0-AggregateReview.md). All files and commands are
repository-relative; no external temporary audit directory is required.

The new [checker](../../verification/test_p980_aggregate_review.py) consumes
the existing five event companions and their actual numerical dependencies.
It adds independent rational transfer/charge assertions and adversarial event
outputs, while reusing the existing interval dynamics oracles. No external
authorship, native API, full runtime transaction or uniform floating-point
proof is claimed.

## Retained runs

| Files | Execution |
| --- | --- |
| [report.json](./report.json), [run.txt](./run.txt) | Main method: all twenty profile/role paths, 200 target beats, 63 event defects rejected |
| [outlier-run.txt](./outlier-run.txt) | Forty further event-output defects rejected across all ten profiles |
| [algebra-run.txt](./algebra-run.txt) | 2,048 initial-resource transfer corners and five signed coarse/Split cases |
| [focused-run.txt](./focused-run.txt) | Outlier/algebra methods repeated after final import/format/explicit closure-binding cleanup |
| [environment.json](./environment.json) | Local Python/package versions and thread settings |
| [manifest.json](./manifest.json) | SHA-256 of the final checker, research dependencies, construction inputs and retained evidence; paths relative to repository root |

The main method was run before the two focused methods were added; formatting
and explicit binding of the synchronously used mutation label subsequently
changed no tested formulas, cases or thresholds. The individual logs therefore
show one method each. The final checker contains all three methods. These are
fresh local results; historical effect campaigns were not rerun or relabeled.

## Focused restriction follow-up

The [R1–R10 pressure check](./RestrictionPressure.md) adds a reproducible
restriction/evidence map, three new boundary methods and seven selected
existing methods. All ten pass; [restrictions-run.txt](./restrictions-run.txt)
and [restrictions-integrity.txt](./restrictions-integrity.txt) retain the results.
No restriction or acceptance disposition changes.

## Reproduce

From the repository root, use the project environment with NumPy, mpmath and
the repository's normal Python dependencies installed. Local runs used `.venv`.
Set `OPENBLAS_NUM_THREADS=1` and `OMP_NUM_THREADS=1` as below. New output names
avoid overwriting retained evidence.

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python implementation/phase-9-grcv4/verification/test_p980_aggregate_review.py --report > aggregate-local.json 2> aggregate-local.txt
```

Or run the three methods individually with the same environment variables:

```bash
.venv/bin/python implementation/phase-9-grcv4/verification/test_p980_aggregate_review.py AggregateReviewTests.test_all_ten_both_roles_charge_history_and_continuation --report
.venv/bin/python implementation/phase-9-grcv4/verification/test_p980_aggregate_review.py AggregateReviewTests.test_all_ten_nonfinite_extreme_and_incomplete_event_outputs
.venv/bin/python implementation/phase-9-grcv4/verification/test_p980_aggregate_review.py AggregateReviewTests.test_resource_box_corners_and_signed_coarse_boundary
```

Rational strings in `report.json` are exact differences of exact sums of
represented resources. Per-step `resource_lower` and `resource_error` are
summaries of the actual interval consumers. Physical source counts are one
for current, zero for reset; the final/reference probes are not physical
beats. The report explicitly marks C_OS's absent complete old-reference-vector
check rather than inventing that common interface.

The large-scale coarse examples test exact rational contract identities only.
Malformed maximum-finite/NaN/infinite values are injected event outputs,
not a successful physical-domain outlier campaign. Neither set expands the
admitted research domain.

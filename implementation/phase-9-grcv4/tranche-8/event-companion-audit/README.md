# Retained C_OS event-companion audit evidence

These five JSON files are the supplied 2026-10-02 audit's unchanged historical
results. Read the [retained review](../P9-8.0-EventIndependentReview.md) for its
execution boundary and the [local correction record](../P9-8.0-EventConstruction.md#review-corrections-and-local-verification)
for subsequent verification against current repository dependencies.

- [original_results.json](./original_results.json): the original four test bodies,
  both-role continuation and six effects in the isolated reconstruction.
- [model_binding_pressure.json](./model_binding_pressure.json): accepted port and
  parameter substitutions, including errors against the intended C law.
- [final_read_pressure.json](./final_read_pressure.json): the accepted final-only
  input mutation and its entry-referenced error lower bound.
- [additional_results.json](./additional_results.json): exact matrix/graph checks,
  2,048 transfer-only corner probes, nonuniform exterior-swap rejection, six
  full-Q-similarity cross-checks covering 2,542 entries and fresh-trigger values.
- [review_controls_results.json](./review_controls_results.json): the reviewer's
  proposed model-binding and read-isolation controls, under isolated dependencies.

Accepted counterexamples in these files describe the uncorrected consumer; they
are not expected behavior of the corrected checker. The original loader,
duplicate kernels and temporary package layout are not required by repository
checks. Reusable binding and ownership controls are integrated in the current
owner; run from the repository root:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python implementation/phase-9-grcv4/verification/test_p980_event_companion.py --report
```

The independent corner/full-Q pressure remains historical audit evidence; the
local correction run is not represented as a repeat of that separate campaign.
No native event, complete-profile, RG implementation-review or aggregate
P9-8.0 acceptance follows from these files.

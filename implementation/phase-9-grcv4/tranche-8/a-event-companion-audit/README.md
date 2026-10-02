# Retained A_OS event-companion audit evidence

These four JSON files are the supplied 2026-10-02 audit's unchanged historical
results. Read the [retained review](../P9-8.0-AEventIndependentReview.md) for its
isolated execution boundary and the [local correction record](../P9-8.0-AEventConstruction.md#review-correction-and-local-verification)
for subsequent verification against current repository dependencies.

- [original_results.json](./original_results.json): the original four test bodies,
  both-role continuation and eight effects in the isolated reconstruction.
- [writer_alias_results.json](./writer_alias_results.json): the accepted incoming-W
  mutation, two writer calls and the resulting misattributed effect comparisons.
- [review_controls_results.json](./review_controls_results.json): four original
  controls, twelve C/W/J mutation rejections, four allowed scratch overwrites,
  and the proposed guard's integration into the original effect consumer.
- [additional_results.json](./additional_results.json): exact resource/history
  algebra, six insertion-order permutations, three wrong reference-stage
  rejections, 4,652 independent 90-digit equation checks and exact counterexample
  error lower bounds.

Accepted counterexamples describe the uncorrected consumer; they are not
expected behavior of the corrected checker. Reusable ownership controls and
the mutation reproducer are integrated in the current research owner. The
original isolated loader and duplicate predecessor tree are not repository
inputs. Run from the repository root:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python implementation/phase-9-grcv4/verification/test_p980_a_event_companion.py --report
```

The additional independent equation/algebra pressure remains historical audit
evidence. The local correction run is not a repeat of that separate campaign.
No native event, complete-profile, RG implementation-review or aggregate
P9-8.0 acceptance follows from these files.

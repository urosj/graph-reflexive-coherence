# GRC9V3 Hessian / Hybrid Spark Handoff

Date: 2026-05-05

Updated: 2026-05-06 for Lane B v1 and Lane C comparison completion.

Purpose: resume future GRC9V3 Hessian / spark-lane work without losing the
current experimental baseline.

This handoff closes the current readiness pass and records how to continue
with later Hessian/spark lanes, including canonical column-H, without blurring
Lane A with future implementation work.

## 1. Read First

Read these in order before resuming implementation:

1. [GRC9V3-Hessian-ImplementationPlan.md](./GRC9V3-Hessian-ImplementationPlan.md)
2. [GRC9V3-Hessian-ImplementationChecklist.md](./GRC9V3-Hessian-ImplementationChecklist.md)
3. [GRC9V3-CanonicalColumnH-LaneDecision.md](./GRC9V3-CanonicalColumnH-LaneDecision.md)
4. [GRC9V3-LaneA-SparkGateTraceSchema.md](./GRC9V3-LaneA-SparkGateTraceSchema.md)
5. [GRC9V3-ArtifactSurfaceHardening.md](./GRC9V3-ArtifactSurfaceHardening.md)
6. `outputs/grc9v3/hessian_readiness/readiness_gate.md`
7. `outputs/grc9v3/hessian_readiness/theory_runtime_gap_ledger.md`
8. `outputs/grc9v3/hessian_readiness/current_hybrid_baseline.md`

For experiment context, also read:

1. `experiments/2026-05-N01-grc9v3-properties/implementation/ExperimentSpecification.md`
2. `experiments/2026-05-N01-grc9v3-properties/implementation/ExperimentSpecificationChecklist.md`
3. `experiments/2026-05-N01-grc9v3-properties/implementation/DiscriminatorExperimentSpecification.md`
4. `experiments/2026-05-N01-grc9v3-properties/implementation/DiscriminatorExperimentSpecificationChecklist.md`
5. `experiments/2026-05-N01-grc9v3-properties/reports/artifact_surface_inventory.md`

## 2. Current Baseline

The current object under test is:

```text
baseline_id = GRC9V3-current-hybrid
spark_lane = current_hybrid_signed_hessian
default_hessian_backend = row_basis_diagonal
```

Lane A candidate semantics:

```text
active_degree == 9
gradient_norm < eps_gradient
min_signed_hessian < eps_spark
optional signed crossing only when spark_signed_crossing is true
```

Current direct candidate evidence comes from:

```text
StepResult.events[kind=hybrid_spark_candidate].payload
GRC9V3State.event_log
snapshot.events
telemetry.event_rows.family_extensions.grc9v3.spark_evidence
```

Column-H / cancellation evidence is not a direct Lane A spark gate.

## 3. Completed Work

Completed readiness items:

| Iteration | Status | Output |
|---|---|---|
| 0. Documentation bootstrap | complete | readiness plan/checklist and spec alignment |
| 1. Baseline freeze | complete | `outputs/grc9v3/hessian_readiness/current_hybrid_baseline.md` |
| 2. Current-lane conformance tests | complete | `tests/models/test_grc_9_v3_hessian_readiness.py` |
| 3. Lane A spark-gate trace | complete | `implementation/GRC9V3-LaneA-SparkGateTraceSchema.md` |
| 4. Artifact surface hardening | complete | `implementation/GRC9V3-ArtifactSurfaceHardening.md` |
| 5. Theory/runtime gap ledger | complete | `outputs/grc9v3/hessian_readiness/theory_runtime_gap_ledger.*` |
| 6. Canonical column-H lane decision | complete | Lane B deferred during readiness, later opened separately |
| 7. Comparison lane contract | complete | Lane C setup and experiment-side comparison artifacts produced |
| 8. Downstream experiment-spec impact | complete | gap ledger and specs/checklists aligned |
| Lane B v1. Column-H-assisted spark | complete through Iteration 8 | `grc9v3_column_h_assisted` opt-in lane implemented; Lane A remains default |

Readiness gate:

```text
outputs/grc9v3/hessian_readiness/readiness_gate.md
outputs/grc9v3/hessian_readiness/readiness_gate.json
decision = GO for Experiment Iteration 2
```

## 4. Current Surface Classification

| Surface | Lane A Status |
|---|---|
| row differential state | direct |
| signed-Hessian hybrid spark candidate | direct |
| active-degree saturation | direct |
| mechanical expansion mapping | direct |
| edge labels | direct |
| coarse-graining/Split | direct |
| sink/basin hierarchy | direct |
| column-H / cancellation diagnostic | derived |
| full port-history motion observer | partial |

Primary overclaim risks:

- Do not claim direct column-H spark gating under Lane A.
- Do not claim identity fission from mechanical expansion alone.
- Do not infer signed flux orientation from absolute flux alone.
- Do not treat current motion loader output as full port-history support.

## 5. Validation Commands

Run these from repo root:

```bash
.venv/bin/python -m json.tool outputs/grc9v3/hessian_readiness/readiness_gate.json
```

```bash
.venv/bin/python -m json.tool outputs/grc9v3/hessian_readiness/theory_runtime_gap_ledger.json
```

```bash
PYTHONPATH=src .venv/bin/python -m unittest tests.models.test_grc_9_v3_hessian_readiness
```

```bash
PYTHONPATH=src .venv/bin/python -m unittest tests.models.test_grc_9_v3_state tests.models.test_grc_9_v3_differential tests.models.test_grc_9_v3_transport tests.models.test_grc_9_v3_sparks tests.models.test_grc_9_v3_choice_budget tests.models.test_grc_9_v3_coarse tests.models.test_grc_9_v3_step tests.models.test_grc_9_v3_representative_runtime tests.models.test_grc_9_v3_hessian_readiness tests.telemetry.test_grc9v3_contract tests.telemetry.test_grc9v3_extensions
```

```bash
.venv/bin/python -m ruff check tests/models/test_grc_9_v3_hessian_readiness.py
```

Latest recorded status:

```text
focused readiness tests: 12 OK
broader GRC9V3 suite: 75 OK
ruff: OK
json.tool readiness gate: OK
json.tool gap ledger: OK
```

## 6. Future Lane Vocabulary

Use these lane labels consistently:

| Lane | Status | Meaning |
|---|---|---|
| Lane A: `current_hybrid_signed_hessian` | current baseline | Saturation plus basin-interior and signed-Hessian degeneracy evidence. |
| Lane B: `grc9v3_column_h_assisted` | implemented as opt-in v1 | GRC9V3 spark lane using the v3 saturation/gradient envelope plus direct runtime-computed column-H proxy threshold/sign-crossing evidence. |
| Lane C: `comparison` | complete as analysis pass | Analysis lane comparing Lane A and Lane B on selected fixtures. |

Potential future Hessian/backend comparison work should use explicit names such
as:

```text
hessian_backend_row_basis_diagonal
hessian_backend_weighted_least_squares
```

Do not call a Hessian backend comparison a new spark lane unless it actually
changes the spark predicate.

## 7. Lane B V1 Status

Lane B v1 is now implemented as a bounded repo-level runtime lane. The plan and
checklist are:

- [GRC9V3-CanonicalColumnH-ImplementationPlan.md](./GRC9V3-CanonicalColumnH-ImplementationPlan.md)
- [GRC9V3-CanonicalColumnH-ImplementationChecklist.md](./GRC9V3-CanonicalColumnH-ImplementationChecklist.md)
- [GRC9V3-LaneC-ComparisonSetup.md](./GRC9V3-LaneC-ComparisonSetup.md)

```text
spark_lane = grc9v3_column_h_assisted
```

Lane B v1 implements direct runtime-computed column-H proxy evidence inside the
GRC9V3 saturation / small-gradient envelope. It is not a plain column-H-only
trigger and it does not change mechanical expansion or identity acceptance.

Direct column-H proxy-branch gate evidence is valid only when the candidate
payload records:

```text
spark_lane = grc9v3_column_h_assisted
column_h_branch_hit = true
gate_reasons includes column_h_threshold_hit or column_h_sign_crossing_hit
```

Lane A remains the default baseline and does not consume or update column-H
history under default configuration.

Naming note:

```text
canonical_column_h:
    conceptual core GRC9 column-H diagnostic source

grc9v3_column_h_assisted:
    preferred GRC9V3 Lane B runtime lane id
```

Minimum negative tests:

```text
saturated with small gradient but no signed-Hessian hit and no column-H hit -> no spark
column-H crossing but unsaturated under Lane B v1 -> no spark
degree 8 near-saturation remains blocked in Lane B v1
derived column-H proxy alone does not trigger Lane A
```

Minimum positive tests:

```text
saturated small-gradient direct column-H threshold case -> Lane B candidate
saturated small-gradient direct column-H sign-crossing case -> Lane B candidate, if enabled
Lane A unchanged under default config
same fixture emits lane-tagged event evidence under Lane B only when configured
```

These tests are now represented in
`tests/models/test_grc_9_v3_column_h_assisted.py` and
`tests/models/test_grc_9_v3_sparks.py`.

## 8. How To Resume Hessian Backend Work

The current default Hessian backend is:

```text
row_basis_diagonal
```

The implementation already recognizes:

```text
weighted_least_squares
```

Future backend work should be handled as backend comparison or conformance work
unless it changes the spark predicate.

Recommended first backend task:

```text
GRC9V3 Hessian Backend Comparison Readiness
```

Scope:

- verify `row_basis_diagonal` and `weighted_least_squares` populate expected
  caches,
- assert backend selection is explicit in params and artifacts,
- compare candidate traces under both backends on the same fixtures,
- report differences as backend sensitivity, not as column-H evidence.

Do not silently make `weighted_least_squares` the default.

## 9. Lane C Comparison Contract

Lane C setup and experiment-side execution are complete.

Lane C compared a small first subset:

1. Experiment B: derived column-interface cancellation versus direct Lane B
   column-H evidence.
2. Experiment C / D4: saturation and spark gating.
3. Experiment D / D5: refinement mapping and interface memory.
4. D1: factorization near spark events.
5. D8: identity emergence only if enough post-event basin artifacts exist.

Keep O1 row-mode stress out of the first Lane A/B comparison unless the new
predicate unexpectedly affects row-local response.

Generated Lane C artifacts:

```text
experiments/2026-05-N01-grc9v3-properties/scripts/run_lane_c_comparison.py
experiments/2026-05-N01-grc9v3-properties/outputs/lane_c_comparison_manifest.json
experiments/2026-05-N01-grc9v3-properties/outputs/lane_c_candidate_comparison.csv
experiments/2026-05-N01-grc9v3-properties/outputs/lane_c_refinement_comparison.csv
experiments/2026-05-N01-grc9v3-properties/outputs/lane_c_identity_comparison.csv
experiments/2026-05-N01-grc9v3-properties/outputs/lane_c_branch_attribution.csv
experiments/2026-05-N01-grc9v3-properties/outputs/lane_c_summary.json
experiments/2026-05-N01-grc9v3-properties/reports/lane_c_comparison_report.md
experiments/2026-05-N01-grc9v3-properties/reports/lane_c_blocked_observations.md
```

Result:

```text
comparison rows: 60
Lane A candidates/refinements: 25 / 25
Lane B candidates/refinements: 40 / 40
direct Lane B column-H proxy-branch rows: 15
candidate/refinement delta rows: 15 / 15
degree-8 near-saturation blocked: true
```

Classification:

```text
lane_c_comparison_complete_direct_column_h_branch_delta_observed_with_boundaries
```

## 10. Source Files To Protect

Do not change these casually when resuming:

```text
src/pygrc/models/grc_9_v3.py
src/pygrc/models/grc_9_v3_runtime.py
src/pygrc/models/grc_9_v3_sparks.py
src/pygrc/models/grc_9_v3_state.py
src/pygrc/telemetry/grc9v3_contract.py
```

If a future lane changes `src/pygrc`, classify the change before editing:

```text
documentation-only
test-only
artifact extraction / observability-only
non-semantic bug fix
semantic runtime change
```

Semantic runtime changes require their own implementation plan/checklist and
must not be hidden inside experiment code.

## 11. Experiment Baseline Boundary

The property experiments should proceed from:

```text
experiments/2026-05-N01-grc9v3-properties/implementation/ExperimentSpecificationChecklist.md
Iteration 2. Shared Fixture And Transform Harness
```

Those experiments assume Lane A only.

Do not retroactively reinterpret old Lane A experiment outputs after Lane B v1.
Instead, run Lane C comparison with shared fixture ids, seeds, params, artifact
schema, and lane ids.

## 12. Handoff Decision

Current handoff state:

```text
Readiness pass: complete
Experiment readiness gate: GO
Lane A: frozen baseline
Lane B: implemented as opt-in grc9v3_column_h_assisted v1
Lane C: completed comparison artifacts
Next experiment step: Shared Fixture And Transform Harness
Next implementation step, if chosen instead: docs/spec closeout or a separately scoped future lane
```

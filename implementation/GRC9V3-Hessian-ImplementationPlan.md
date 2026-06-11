# GRC9V3 Hessian / Hybrid Spark Implementation Readiness Plan

This document defines a bounded readiness pass for the current `GRC9V3`
runtime before the GRC9V3 property experiments continue.

It is an implementation-alignment plan, not an instruction to change runtime
semantics during the experiment track.

Companion checklist:

- [GRC9V3-Hessian-ImplementationChecklist.md](./GRC9V3-Hessian-ImplementationChecklist.md)

Handoff:

- [GRC9V3-Hessian-Handoff.md](./GRC9V3-Hessian-Handoff.md)

## Purpose

The immediate goal is to make the existing `GRC9V3` Hessian and hybrid spark
surface auditable enough for experiments.

Although the title names Hessian and hybrid spark explicitly, the readiness
scope also covers the artifact surfaces needed to audit those semantics:
checkpoint/event extraction, expansion reassignment evidence, port-history
reconstruction, coarse-graining/Split checks, and identity hierarchy evidence.

The pass should answer:

```text
What does the current signed-Hessian hybrid spark runtime actually expose?
Which theory-facing spark and column-H surfaces are direct, derived, partial,
or absent?
What tests and artifact contracts are needed before experiments rely on them?
```

## Non-Goals

This pass must not silently replace the current runtime object under test.

Out of scope unless explicitly split into a later canonical lane:

- changing the default spark predicate,
- adding direct column-H gating as an incidental fix,
- adding new identity-fission rules,
- altering mechanical expansion to satisfy an experiment,
- treating source-authored theory claims as runtime evidence.

## Runtime Lanes

Use three labels consistently.

| Lane | Purpose | Runtime Semantics |
|---|---|---|
| Lane A: `current_hybrid_signed_hessian` | Freeze and audit the implemented baseline | GRC9 saturation plus basin-interior and signed-Hessian degeneracy evidence |
| Lane B: `grc9v3_column_h_assisted` | Opt-in direct column-H-assisted implementation lane opened after this readiness pass | GRC9V3 saturation / small-gradient envelope plus signed-Hessian or direct runtime-computed column-H proxy threshold/sign-crossing evidence |
| Lane C: `comparison` | Rerun selected fixtures across A and B | Analysis lane; does not define a new runtime predicate |

Lane A is the only lane assumed by the current experiment baseline.

Lane B must be a separate repo-level `implementation/` task if pursued. It
requires explicit configuration, tests, telemetry/checkpoint evidence, and
before/after reporting.

Readiness decision:

- Lane B was deferred, not rejected, during this Lane A readiness pass.
- It is not in scope for this readiness pass.
- This pass remains Lane A only: `current_hybrid_signed_hessian`.
- Lane C comparison was completed as a separate experiment-side analysis task
  after Lane B v1 was implemented.
- Decision note:
  [GRC9V3-CanonicalColumnH-LaneDecision.md](./GRC9V3-CanonicalColumnH-LaneDecision.md)

Post-readiness update:

- Lane B v1 has now been opened as the separate repo-level task
  [GRC9V3-CanonicalColumnH-ImplementationPlan.md](./GRC9V3-CanonicalColumnH-ImplementationPlan.md).
- The implementation lane id is `grc9v3_column_h_assisted`.
- `canonical_column_h` names the conceptual core GRC9 column-H diagnostic
  source, not the GRC9V3 runtime lane id.
- Lane A remains default and must not be retroactively reinterpreted.

## Semantic-Change Firewall

Every change made during this readiness pass must be classified as one of:

| Category | Allowed In Lane A Readiness | Meaning |
|---|---|---|
| documentation-only | yes | prose/spec/checklist/report updates only |
| test-only | yes | tests that assert existing behavior |
| artifact extraction / observability-only | yes | exposing, reading, or reporting existing state without changing runtime outcomes |
| non-semantic bug fix | yes, with evidence | correction that preserves intended Lane A state/event behavior |
| semantic runtime change | no | changes spark predicates, event timing, expansion behavior, identity rules, transport equations, or default runtime outputs |

Category 5 requires a Lane B decision record or a separate accepted
implementation plan. Artifact hardening must be checked against golden-run
state/event outputs so it does not accidentally become semantic drift.

## Inputs

- [../specs/grc-9-v3-spec.md](../specs/grc-9-v3-spec.md)
- [../specs/grc-9-spec.md](../specs/grc-9-spec.md)
- [Phase-7-ImplementationPlan.md](./Phase-7-ImplementationPlan.md)
- [Phase-7-StepLoop.md](./Phase-7-StepLoop.md)
- [Phase-T-GRC9V3-TelemetryContract.md](./Phase-T-GRC9V3-TelemetryContract.md)
- [../experiments/2026-05-N01-grc9v3-properties/reports/artifact_surface_inventory.md](../experiments/2026-05-N01-grc9v3-properties/reports/artifact_surface_inventory.md)

## Scope

### 1. Baseline Freeze

Record the current implementation as:

```text
GRC9V3-current-hybrid
spark lane = current_hybrid_signed_hessian
```

The freeze should include the relevant params, capability list, step-loop
ordering, event kinds, checkpoint surfaces, and test command inventory.

The freeze should also record exact reproducibility fields:

- git commit SHA and branch,
- Python/package environment or lockfile reference,
- default `GRC9V3` params as serialized JSON,
- spark-lane id,
- fixture ids and random seeds used for baseline smoke tests,
- artifact schema / telemetry contract version.

### 2. Conformance Tests

Add or verify tests for what the current runtime already claims:

- port id to row/column mapping,
- active degree calculation,
- endpoint port recording,
- row differential state availability,
- signed Hessian backend behavior,
- signed flux orientation,
- zero-active-port and partially active node behavior where relevant,
- active-degree 8 versus 9 distinction under current lane semantics,
- inactive-port handling,
- signed flux antisymmetry under endpoint orientation reversal,
- edge label availability,
- hybrid spark candidate event payload shape,
- mechanical expansion reassignment map,
- budget preservation around expansion,
- coarse-graining/Split round trip,
- zero-column coarse-graining/Split behavior,
- signed-flux `J+` / `J-` reconstruction where signed flux is available,
- sink/basin hierarchy availability.

These tests should not add theory. They make the baseline observable.

### 3. Lane A Spark-Gate Trace

Trace schema:

- [GRC9V3-LaneA-SparkGateTraceSchema.md](./GRC9V3-LaneA-SparkGateTraceSchema.md)

For every Lane A spark candidate, artifact extraction should expose or
reconstruct:

- node id,
- timestep,
- active degree,
- sink status,
- gradient or row-differential evidence,
- signed-Hessian degeneracy evidence,
- candidate event kind,
- whether mechanical expansion followed,
- expansion event id, if any,
- completed identity-event / child-basin status, if any.

The same report may compute a derived column-H / cancellation proxy, but it
must record:

- whether a proxy formula is defined,
- proxy formula version,
- source fields used,
- whether the proxy is direct, derived, partial, or blocked.

This readiness pass does not define a column-H proxy formula. Until a separate
formula specification exists, Lane A trace records should mark the proxy section
as blocked rather than inventing a `H` diagnostic.

Reports may say:

```text
derived column-H proxy was near zero at the candidate event
```

Reports may not say:

```text
column-H triggered the spark
```

unless Lane B or a direct runtime field proves that gate.

### 4. Artifact Surface Hardening

Artifact hardening note:

- [GRC9V3-ArtifactSurfaceHardening.md](./GRC9V3-ArtifactSurfaceHardening.md)

Stabilize observability where needed:

- checkpoint readers,
- event payload extraction,
- expansion mapping evidence from `StepResult.events`,
- full port-history reconstruction from checkpoint overlays,
- deterministic artifact reports.

Reusable observability changes in `src/pygrc` are allowed only as their own
implementation work with tests. Experiment-local code must not mutate the
runtime.

Expansion reassignment evidence should use this priority order:

1. `StepResult.events[kind=hybrid_mechanical_expansion].payload.reassignment_map`
2. `cached_quantities.last_hybrid_expansion`
3. `GRC9V3State.expansion_registry`
4. snapshot `basin_attributes.expansion_registry`

Snapshot `basin_attributes.expansion_registry` is corroborating expansion
registry evidence, not primary reassignment-map evidence.

### 5. Theory / Runtime Gap Ledger

Maintain a short map:

Each row should include:

- surface,
- theory-facing meaning,
- Lane A status: direct / derived / partial / absent,
- artifact source,
- experiment impact,
- blocked claims, if any,
- required change for Lane B, if any.

Initial rows:

| Surface | Lane A Status | Experiment Impact |
|---|---|---|
| row differential state | direct | Experiment A and D1/D3/D6 may use direct row evidence |
| signed-Hessian hybrid spark candidate | direct | Experiment C/D4 and D8 may audit Lane A candidate conditions |
| active-degree saturation | direct | Experiment C/D4 may test degree-9 capacity |
| mechanical expansion mapping | direct if event payload exists | Experiment D/D5 may audit reassignment by column |
| edge labels | direct | Experiment F may compare metric/delay/flux paths |
| coarse-graining/Split | direct | Experiment E/D7 may test reconstruction |
| sink/basin hierarchy | direct | Experiment D/D8 may test persistence |
| column-H / cancellation diagnostic | derived under Lane A; direct runtime-computed proxy evidence only when `spark_lane == "grc9v3_column_h_assisted"` | Experiment B/D4 may test Lane A correlation or prediction; Lane B runs may audit direct proxy-branch gate evidence |
| full port-history motion observer | partial unless hardened | Experiment G remains partial until overlay reconstruction is stable |

### 6. Canonical Column-H Decision Gate

Do not implement direct column-H gating until the project explicitly chooses
Lane B.

Readiness decision for this pass:

```text
Lane B is not in scope for the current GRC9V3 Hessian / Hybrid Spark
Implementation Readiness pass.

Lane B is deferred, not rejected.
```

Subsequent implementation work has opened Lane B v1 separately as
`grc9v3_column_h_assisted`. That later work does not change the meaning of this
readiness pass: Lane A remains the signed-Hessian baseline, and old Lane A
artifacts remain Lane A artifacts.

The decision record must state:

- whether Lane B is being implemented,
- whether it changes the default or is opt-in only,
- which config value selects it,
- which tests prove the gate,
- which telemetry/checkpoint fields expose direct evidence,
- how Lane A and Lane B experiments will be compared.

It must also answer:

- whether Lane B uses `min_b |H_s^(b)|`, sign crossing, or both,
- whether Lane B still requires signed-Hessian evidence,
- whether Lane B still requires sink status,
- whether Lane B requires active degree 9 or allows near-saturation,
- how virtual zero-conductance stubs are handled if near-saturation exists,
- which positive and negative tests prove the predicate.

Required negative cases before Lane B can be accepted:

- saturated but no instability and no column-H crossing -> no spark,
- column-H crossing but unsaturated under canonical mode -> no spark,
- degree 8 near-saturation triggers only when the explicit extension is enabled,
- derived column-H proxy alone does not trigger Lane A.

### 7. Comparison Lane Contract

Lane C was executed after an explicit comparison setup was opened. The first
comparison subset was:

- Experiment B: column-interface cancellation,
- Experiment C / D4: saturation and spark gating,
- Experiment D / D5: refinement mapping and interface memory,
- D1: factorization near spark events,
- D8: identity emergence only if post-event basin artifacts are sufficient.

O1 row-mode stress was not prioritized for the first Lane A/B comparison.
Lane C produced:

```text
comparison rows: 60
Lane A candidates/refinements: 25 / 25
Lane B candidates/refinements: 40 / 40
direct Lane B column-H proxy-branch rows: 15
degree-8 near-saturation blocked: true
```

Classification:

```text
lane_c_comparison_complete_direct_column_h_branch_delta_observed_with_boundaries
```

### 8. Downstream Experiment-Spec Impact

The readiness pass changes the interpretation of these experiment specs:

| Experiment | Lane A Interpretation |
|---|---|
| Experiment B | column cancellation is a derived proxy, not a direct gate |
| Experiment C / D4 | degree-9 saturation is direct; column-H gating is not direct |
| Experiment D / D5 | reassignment mapping is direct when event payload exists; interface memory is post-event analysis |
| Experiment G | full port history remains partial unless checkpoint overlay reconstruction is hardened |
| D8 | identity emergence requires sink/basin persistence, not expansion alone |

All reports should use strict report-level terminology:

| Term | Meaning |
|---|---|
| `spark_candidate` | local runtime event or condition indicating possible chart failure |
| `mechanical_expansion` | graph/module refinement event |
| `completed_identity_event` | post-event attractor/basin structure gains a persistent child identity |

The runtime event name `hybrid_spark_completed` may still be cited as an
artifact. Reports should avoid using it as proof of identity unless the
persistence criteria pass.

## Acceptance Criteria

This readiness pass is complete when:

- the baseline lane is documented and reproducible,
- conformance tests cover the current signed-Hessian hybrid spark surface,
- artifact extraction rules identify direct versus derived evidence,
- semantic-change classification exists for any implementation change in this
  pass,
- golden-run state/event comparisons guard Lane A against semantic drift,
- theory/runtime gaps are explicit,
- the experiment specs no longer conflate baseline signed-Hessian spark with a
  direct column-H gate,
- and any decision to add a canonical column-H lane is recorded separately.

# GRC9V3 Hessian / Hybrid Spark Implementation Readiness Checklist

This checklist tracks the bounded readiness pass defined in:

- [GRC9V3-Hessian-ImplementationPlan.md](./GRC9V3-Hessian-ImplementationPlan.md)
- [GRC9V3-Hessian-Handoff.md](./GRC9V3-Hessian-Handoff.md)

## Usage Rules

- Treat the current `GRC9V3` runtime as the `current_hybrid_signed_hessian`
  baseline until a separate canonical-column-H lane is explicitly implemented.
- Do not change the default spark predicate as part of observability hardening.
- Keep tests and artifact extraction focused on what the runtime already claims
  unless a new lane is declared.
- Mark column-H/cancellation evidence as derived unless direct runtime gating
  evidence exists.
- Keep experiment-local code under `experiments/`; reusable runtime or telemetry
  changes are tracked by repo-level `implementation/` tasks, belong in
  `src/pygrc`, and require tests.
- Preserve the distinction between spark candidate, mechanical expansion, and
  completed identity event.
- Classify every change made during this pass as documentation-only,
  test-only, artifact extraction / observability-only, non-semantic bug fix, or
  semantic runtime change.
- Allow only documentation-only, test-only, artifact extraction /
  observability-only, and justified non-semantic bug fixes in Lane A readiness.
- Require a Lane B decision record for semantic runtime changes.

## Iteration Template

```markdown
## Iteration N. <Short Name>

Status: pending | in progress | complete | blocked.

### Goal

<What this iteration is intended to complete>

### Checks

- [ ] <Concrete task 1>
- [ ] <Concrete task 2>

### Implementation Notes

- <Important implementation detail, decision, or constraint>

### Verification

- [ ] <Import / run / report / review check>

### Summary

<Short outcome summary once iteration is complete>
```

## Iteration 0. Documentation Bootstrap

Status: complete.

### Goal

Create the readiness plan/checklist and align the specs so the current
signed-Hessian hybrid spark baseline is not confused with any separate direct
column-H lane.

### Checks

- [x] Create `GRC9V3-Hessian-ImplementationPlan.md`
- [x] Create `GRC9V3-Hessian-ImplementationChecklist.md`
- [x] Update `specs/grc-9-v3-spec.md` with explicit spark-lane language
- [x] Update `specs/README.md` with signed-Hessian / column-H distinction
- [x] Update experiment specifications to mark column-H as derived unless a
      canonical-column-H lane exists
- [x] Link the readiness pass from `ImplementationPhases.md`

### Verification

- [x] Documentation changes only; no runtime code edits
- [x] Plan names Lane A, Lane B, and Lane C explicitly
- [x] Checklist records that Lane A remains the experiment baseline
- [x] Checklist includes the semantic-change firewall

### Summary

The documentation bootstrap is complete. The project now has a bounded
readiness track for auditing GRC9V3 Hessian and hybrid spark semantics before
continuing the property experiments.

## Iteration 1. Baseline Freeze

Status: complete.

### Goal

Record the current runtime as `GRC9V3-current-hybrid` with spark lane
`current_hybrid_signed_hessian`.

### Checks

- [x] Record current `GRC9V3` params relevant to Hessian and spark behavior
- [x] Record git commit SHA and branch
- [x] Record Python/package environment or lockfile reference
- [x] Record default `GRC9V3` params as serialized JSON
- [x] Record spark-lane id
- [x] Record current capability list
- [x] Record current step-loop ordering around Hessian, spark candidate,
      expansion, stabilization, and completion
- [x] Record current event kinds and payload surfaces
- [x] Record current checkpoint/telemetry surfaces for Hessian and spark claims
- [x] Record fixture ids and random seeds used for baseline smoke tests
- [x] Record artifact schema / telemetry contract version
- [x] Record current test command inventory
- [x] Produce a baseline freeze report

### Verification

- [x] Produce `outputs/grc9v3/hessian_readiness/current_hybrid_baseline.md`
- [x] Baseline report distinguishes direct, derived, partial, and absent
      surfaces
- [x] Golden-run state/event comparison is captured for later observability
      hardening checks
- [x] No runtime behavior changed

### Summary

Iteration 1 froze the current `GRC9V3` runtime as
`GRC9V3-current-hybrid` with spark lane `current_hybrid_signed_hessian`.

The freeze report records git/environment metadata, default params, capability
claims, step-loop order, direct Lane A event payloads, checkpoint/telemetry
surfaces, a replay-matched golden run, and focused test status.

## Iteration 2. Current-Lane Conformance Tests

Status: complete.

### Goal

Add or verify tests for the current signed-Hessian hybrid spark runtime claims.

### Checks

- [x] Test port id to row/column mapping
- [x] Test row/column mapping for all port ids 1 through 9
- [x] Test active degree calculation
- [x] Test zero-active-port and partially active node behavior where relevant
- [x] Test active-degree 8 versus 9 distinction under current lane semantics
- [x] Test inactive-port handling does not accidentally act like a real edge
- [x] Test endpoint port recording
- [x] Test row differential state availability
- [x] Test signed Hessian backend behavior
- [x] Test signed flux orientation
- [x] Test signed flux antisymmetry under endpoint orientation reversal
- [x] Test edge label availability
- [x] Test hybrid spark candidate event payload shape
- [x] Test mechanical expansion reassignment map
- [x] Test expansion event payload exposes primary reassignment evidence
- [x] Test budget preservation around expansion
- [x] Test coarse-graining/Split round trip
- [x] Test coarse G/Split zero-column behavior
- [x] Test signed-flux `J+` / `J-` reconstruction where signed flux is
      available
- [x] Test sink/basin hierarchy availability

### Verification

- [x] Focused test command passes
- [x] Tests do not require new theoretical behavior
- [x] Any missing conformance surface is recorded as blocked or deferred

### Implementation Notes

- Added `tests/models/test_grc_9_v3_hessian_readiness.py`.
- The new tests are Lane A conformance checks only. They do not add Lane B
  semantics and do not change runtime code.
- Expansion reassignment evidence is asserted from the direct
  `hybrid_mechanical_expansion` event payload and cross-checked against
  `cached_quantities.last_hybrid_expansion`.
- Full extractor priority over checkpoint/module overlays is deferred to
  Iteration 4 artifact surface hardening.
- The expansion/hierarchy test uses the deterministic Appendix E
  representative fixture. Natural evolved-state spark coverage is not claimed
  by this iteration.

### Verification Command

```bash
PYTHONPATH=src .venv/bin/python -m unittest tests.models.test_grc_9_v3_state tests.models.test_grc_9_v3_differential tests.models.test_grc_9_v3_transport tests.models.test_grc_9_v3_sparks tests.models.test_grc_9_v3_choice_budget tests.models.test_grc_9_v3_coarse tests.models.test_grc_9_v3_step tests.models.test_grc_9_v3_representative_runtime tests.models.test_grc_9_v3_hessian_readiness tests.telemetry.test_grc9v3_contract tests.telemetry.test_grc9v3_extensions
```

Result:

```text
Ran 72 tests in 0.612s
OK
```

### Summary

Iteration 2 is complete. The current signed-Hessian Lane A surface now has a
focused readiness test file covering port mapping, active-degree gates,
positive spark-threshold degeneracy, inactive-port non-participation, endpoint
orientation and antisymmetry, differential/transport values, spark payloads,
expansion reassignment, budget preservation, coarse/Split reconstruction,
zero-column reconstruction, signed-flux J+/J- decomposition, and hierarchy
evidence.

## Iteration 3. Lane A Spark-Gate Trace

Status: complete.

### Goal

Define and verify the artifact trace required to audit every Lane A spark
candidate without implying direct column-H gating.

### Checks

- [x] Extract or reconstruct spark candidate node id
- [x] Extract or reconstruct timestep
- [x] Extract or reconstruct active degree
- [x] Extract or reconstruct sink status
- [x] Extract or reconstruct gradient / row differential evidence
- [x] Extract or reconstruct signed-Hessian degeneracy evidence
- [x] Extract candidate event kind
- [x] Record whether mechanical expansion followed
- [x] Record expansion event id when present
- [x] Record completed identity-event / child-basin status when present
- [x] Represent derived column-H / cancellation proxy only as a derived or
      blocked analysis artifact
- [x] Record column-H proxy formula status and formula version
- [x] Record candidate source fields for any later direct column-H proxy
- [x] Add report wording rule:
      `derived column-H proxy was near zero at the candidate event`
- [x] Add forbidden Lane A wording rule:
      `column-H triggered the spark`

### Verification

- [x] Produce a Lane A spark-gate trace schema
- [x] Trace schema separates direct signed-Hessian evidence from derived
      column-H proxy evidence
- [x] Trace schema preserves candidate / expansion / completed identity-event
      terminology

### Implementation Notes

- Added `GRC9V3-LaneA-SparkGateTraceSchema.md`.
- The schema is documentation-only. It defines artifact records and reporting
  rules but does not add extraction code or change runtime semantics.
- The schema includes a telemetry contract mapping to
  `GRC9V3SparkEvidence`, `GRC9V3ExpansionEvidence`, and
  `GRC9V3CompletionEvidence`.
- Candidate evidence is sourced first from
  `StepResult.events[kind=hybrid_spark_candidate].payload`, then telemetry
  event extensions, then checkpoint/state replay.
- Expansion and identity follow-up sections are matched from same-step
  `hybrid_mechanical_expansion` and `hybrid_spark_completed` events.
- Column-H / cancellation remains an optional analysis proxy with
  `predicate_role: analysis_proxy_only`. No column-H proxy formula is defined
  in Iteration 3, so the valid default is `status: "blocked"` with
  `formula_status: "undefined_in_iteration_3"`.
- The schema records `candidate_event.time`, run-level `dt`, and a boolean
  `candidate_condition`; the textual conjunction remains a reporting rule.
- Full event/cache/registry/checkpoint extractor priority is deferred to
  Iteration 4 artifact surface hardening.

### Summary

Iteration 3 is complete. The readiness track now has a Lane A spark-gate trace
schema that records candidate, row differential, signed-Hessian, mechanical
expansion, identity-event, and derived column-H proxy sections while preserving
the rule that column-H is not a direct Lane A spark gate. The column-H proxy is
blocked by default until a future formula specification exists.

## Iteration 4. Artifact Surface Hardening

Status: complete.

### Goal

Make existing Hessian, spark, expansion, and port-history evidence easier to
extract without changing semantics.

### Checks

- [x] Audit checkpoint reader robustness for GRC9V3 Hessian/spark claims
- [x] Add schema validation for
      `GRC9V3-LaneA-SparkGateTraceSchema.md` minimal required fields before
      implementing extraction
- [x] Audit event payload extraction for spark and expansion evidence
- [x] Formalize expansion reassignment evidence priority:
      `StepResult.events[kind=hybrid_mechanical_expansion].payload.reassignment_map`
      before `cached_quantities.last_hybrid_expansion`
      before `GRC9V3State.expansion_registry`
      before snapshot `basin_attributes.expansion_registry`
- [x] Treat snapshot `basin_attributes.expansion_registry` as corroborating
      expansion evidence, not primary reassignment-map evidence
- [x] Define full port-history reconstruction from snapshot/checkpoint
      sequences
- [x] Define deterministic artifact report generation
- [x] Keep derived column-H proxy blocked unless a separate formula
      specification is added

### Verification

- [x] Produce an artifact extraction note
- [x] Extraction preserves direct versus derived evidence labels
- [x] Golden-run state/event comparison confirms observability hardening does
      not change Lane A runtime outputs except explicitly added non-semantic
      artifact fields
- [x] No default spark predicate changes

### Implementation Notes

- Added `GRC9V3-ArtifactSurfaceHardening.md`.
- Added structural schema-document validation tests to
  `tests/models/test_grc_9_v3_hessian_readiness.py`.
- Added a runtime snapshot structure test confirming that `GRC9V3.snapshot()`
  exposes `metadata`, `topology`, `basin_attributes`, `edge_labels`,
  `dynamics`, `observables`, `events`, and `caches`.
- The runtime snapshot test also round-trips through `GRC9V3.save()` /
  `GRC9V3.load()`.
- The artifact hardening note defines candidate, expansion, completion,
  snapshot/checkpoint, port-history, and deterministic report extraction rules.
- Expansion reassignment priority is explicit: event payload first, cache
  second, expansion registry third, snapshot expansion registry fourth.
- Snapshot expansion registry is corroborating evidence only for expansion
  identity/module metadata; it does not store per-edge reassignment maps.
- Full port history is reconstructed only from ordered snapshot/checkpoint
  sequences; missing checkpoint windows remain partial.
- Column-H / cancellation proxy remains blocked by default because no formula
  specification exists.
- No runtime or telemetry implementation code changed. The Iteration 1
  golden-run state/event digest remains the Lane A baseline.

### Verification Command

```bash
PYTHONPATH=src .venv/bin/python -m unittest tests.models.test_grc_9_v3_state tests.models.test_grc_9_v3_differential tests.models.test_grc_9_v3_transport tests.models.test_grc_9_v3_sparks tests.models.test_grc_9_v3_choice_budget tests.models.test_grc_9_v3_coarse tests.models.test_grc_9_v3_step tests.models.test_grc_9_v3_representative_runtime tests.models.test_grc_9_v3_hessian_readiness tests.telemetry.test_grc9v3_contract tests.telemetry.test_grc9v3_extensions
```

Result:

```text
Ran 74 tests in 0.608s
OK
```

Ruff:

```text
All checks passed!
```

### Summary

Iteration 4 is complete. Artifact extraction rules are now documented with
explicit source priorities, checkpoint robustness guidance, port-history
reconstruction rules, deterministic reporting rules, structural schema
validation, and runtime snapshot structure validation. The work is
observability-only and preserves the current Lane A spark predicate.

## Iteration 5. Theory / Runtime Gap Ledger

Status: complete.

### Goal

Record which theory-facing Hessian and spark surfaces are direct, derived,
partial, or absent in the current runtime.

### Checks

- [x] Mark row differential state
- [x] Mark signed-Hessian hybrid spark candidate evidence
- [x] Mark active-degree saturation
- [x] Mark mechanical expansion mapping
- [x] Mark edge labels
- [x] Mark coarse-graining/Split
- [x] Mark sink/basin hierarchy
- [x] Mark column-H/cancellation diagnostic
- [x] Mark full port-history motion observer
- [x] For each surface, record theory-facing meaning
- [x] For each surface, record Lane A status:
      direct / derived / partial / absent
- [x] For each surface, record artifact source
- [x] For each surface, record experiment impact
- [x] For each surface, record blocked claims, if any
- [x] For each surface, record required change for Lane B, if any

### Verification

- [x] Produce `outputs/grc9v3/hessian_readiness/theory_runtime_gap_ledger.json`
- [x] Produce a human-readable gap ledger report
- [x] Gap ledger is referenced before property experiment fixture coding

### Implementation Notes

- Added `outputs/grc9v3/hessian_readiness/theory_runtime_gap_ledger.json`.
- Added `outputs/grc9v3/hessian_readiness/theory_runtime_gap_ledger.md`.
- Added a structural ledger validation test to
  `tests/models/test_grc_9_v3_hessian_readiness.py`.
- Updated the property-experiment checklist to reference the ledger before
  fixture coding.
- Ledger classification:
  - direct: 7 surfaces
  - derived: 1 surface
  - partial: 1 surface
  - absent: 0 surfaces
- Column-H / cancellation is derived and blocked for direct Lane A spark-gate
  claims.
- Full port-history motion observation remains partial until an analyzer reads
  ordered snapshots/checkpoints.

### Verification Command

```bash
PYTHONPATH=src .venv/bin/python -m unittest tests.models.test_grc_9_v3_state tests.models.test_grc_9_v3_differential tests.models.test_grc_9_v3_transport tests.models.test_grc_9_v3_sparks tests.models.test_grc_9_v3_choice_budget tests.models.test_grc_9_v3_coarse tests.models.test_grc_9_v3_step tests.models.test_grc_9_v3_representative_runtime tests.models.test_grc_9_v3_hessian_readiness tests.telemetry.test_grc9v3_contract tests.telemetry.test_grc9v3_extensions
```

Result:

```text
Ran 75 tests in 0.618s
OK
```

Additional checks:

```text
python -m json.tool theory_runtime_gap_ledger.json: OK
ruff: OK
```

### Summary

Iteration 5 is complete. The theory/runtime gap ledger now records each
Hessian, spark, expansion, edge-label, coarse-graining, identity, column-H, and
motion surface with a Lane A status, artifact sources, experiment impact,
blocked claims, and Lane B requirements. The ledger is linked before property
fixture coding so experiments do not overclaim derived or partial evidence.

## Iteration 6. Canonical Column-H Lane Decision

Status: complete; deferred Lane B decision items resolved by the later
canonical Lane B v1 implementation task.

### Goal

Decide whether to implement a separate direct column-H spark lane.

### Decision

Lane B was not in scope for this readiness pass.

Lane B is deferred, not rejected.

This pass remains focused on Lane A:

```text
current_hybrid_signed_hessian
```

Column-H / cancellation evidence remains derived in Lane A. Reports must not
claim direct column-H spark gating under Lane A. Subsequent Lane B v1 work uses
`spark_lane = "grc9v3_column_h_assisted"`; direct column-H proxy-branch gate
evidence is valid only for runs that explicitly use that lane.

### Checks

- [x] Decide whether Lane B is in scope
- [x] Record that Lane B is not in scope for this readiness pass
- [x] Record that Lane B is deferred, not rejected
- [x] Record that this pass remains Lane A only
- [x] Record that Column-H / cancellation evidence remains derived in Lane A
- [x] Record that reports must not claim direct column-H spark gating under
      Lane A
- [x] Record that Lane B may be opened later as a separate repo-level
      implementation task

### Post-Readiness Lane B Resolution

Lane B was later opened in the canonical implementation task:
[GRC9V3-CanonicalColumnH-ImplementationPlan.md](./GRC9V3-CanonicalColumnH-ImplementationPlan.md).

The deferred readiness questions are resolved there and accepted in:
[GRC9V3-CanonicalColumnH-ImplementationChecklist.md](./GRC9V3-CanonicalColumnH-ImplementationChecklist.md).

- [x] Explicit config/mode name defined:
      `spark_lane = "grc9v3_column_h_assisted"`.
- [x] Lane B v1 is opt-in; Lane A remains the default.
- [x] Lane B v1 uses direct runtime-computed `min_b |H_s[b]| <
      eps_column_h` and optional sign crossing.
- [x] Lane B v1 keeps signed-Hessian as a branch inside the GRC9V3
      saturation / small-gradient envelope, not as an always-required
      corroboration.
- [x] Lane B v1 remains sink-only.
- [x] Lane B v1 requires active degree 9.
- [x] Degree-8 near-saturation and virtual zero-conductance stubs remain out of
      scope.
- [x] Direct column-H proxy-branch artifact fields are defined in candidate
      events, telemetry extensions, and checkpoint overlays.
- [x] Lane B v1 positive and negative pass/fail tests are implemented.
- [x] Negative test covered:
      saturated/small-gradient with no signed-Hessian branch and no column-H
      branch emits no candidate.
- [x] Negative test covered:
      column-H branch hit with missing saturation/envelope requirements emits
      no candidate.
- [x] Negative test covered:
      degree 8 near-saturation remains blocked in v1.
- [x] Negative test covered:
      derived column-H-like evidence alone does not trigger Lane A.

### Verification

- [x] Produce a decision note:
      [GRC9V3-CanonicalColumnH-LaneDecision.md](./GRC9V3-CanonicalColumnH-LaneDecision.md)
- [x] No default runtime semantic change occurs without an accepted decision
- [x] Current readiness pass remains Lane A only

### Post-Readiness Update

- Lane B v1 was later opened as the separate implementation task
  [GRC9V3-CanonicalColumnH-ImplementationPlan.md](./GRC9V3-CanonicalColumnH-ImplementationPlan.md).
- The implemented lane id is `grc9v3_column_h_assisted`.
- `canonical_column_h` remains the conceptual core GRC9 diagnostic source, not
  the GRC9V3 runtime lane id.
- Lane A artifacts from this readiness pass remain `current_hybrid_signed_hessian`
  artifacts and must not be reinterpreted as Lane B results.
- Final Lane B v1 implementation acceptance classification:
  `grc9v3_column_h_assisted_lane_b_implemented_with_lane_a_default_preserved`.

## Iteration 7. Comparison Lane Contract

Status: complete as post-readiness setup and experiment-side execution.

### Goal

Define how selected experiments will compare Lane A and Lane B if Lane B is
implemented.

### Decision

Lane B was not in scope for the current readiness pass, so no Lane C comparison
contract was required then. After Lane B v1 exists, Lane C remains separate
from both the Lane A readiness pass and the Lane B runtime predicate.

Post-readiness clarification:

- Lane C setup is prepared in
  [GRC9V3-LaneC-ComparisonSetup.md](./GRC9V3-LaneC-ComparisonSetup.md).
- Lane C execution was later run from the experiment family under
  `experiments/2026-05-N01-grc9v3-properties/`.
- Lane C remains an analysis pass, not a runtime predicate.

### Deferred Checks

- [x] Select experiment subset for comparison setup
- [x] Include Experiment B column-interface cancellation in setup
- [x] Include Experiment C / D4 saturation and spark gating in setup
- [x] Include Experiment D / D5 refinement mapping and interface memory in setup
- [x] Include D1 factorization near spark events in setup
- [x] Include D8 identity emergence only if enough post-event basin artifacts
      exist
- [x] Exclude O1 row-mode stress from the first comparison unless spark
      predicate changes unexpectedly affect row-local response
- [x] Define shared fixture ids and seeds
- [x] Define lane-specific runtime params
- [x] Define output naming convention
- [x] Define direct versus introduced-semantics interpretation rule
- [x] Execute the Lane C experiment comparison
- [x] Produce Lane C comparison outputs and reports

### Verification

- [x] Lane B decision note exists
- [x] Current readiness pass remains Lane A only
- [x] Column-H remains marked as derived under Lane A
- [x] Comparison contract exists before any Lane C experiment run
- [x] Lane C reports can say which effects existed in Lane A and which appeared only
      after Lane B

### Post-Readiness Execution

Lane C comparison artifacts were generated by:

```bash
PYTHONPATH=src:experiments/2026-05-N01-grc9v3-properties/scripts .venv/bin/python experiments/2026-05-N01-grc9v3-properties/scripts/run_lane_c_comparison.py --write-defaults --seed 0
```

Generated:

- `experiments/2026-05-N01-grc9v3-properties/scripts/run_lane_c_comparison.py`
- `experiments/2026-05-N01-grc9v3-properties/outputs/lane_c_comparison_manifest.json`
- `experiments/2026-05-N01-grc9v3-properties/outputs/lane_c_candidate_comparison.csv`
- `experiments/2026-05-N01-grc9v3-properties/outputs/lane_c_refinement_comparison.csv`
- `experiments/2026-05-N01-grc9v3-properties/outputs/lane_c_identity_comparison.csv`
- `experiments/2026-05-N01-grc9v3-properties/outputs/lane_c_branch_attribution.csv`
- `experiments/2026-05-N01-grc9v3-properties/outputs/lane_c_summary.json`
- `experiments/2026-05-N01-grc9v3-properties/reports/lane_c_comparison_report.md`
- `experiments/2026-05-N01-grc9v3-properties/reports/lane_c_blocked_observations.md`

Result:

- comparison rows: `60`;
- Lane A candidates/refinements: `25 / 25`;
- Lane B candidates/refinements: `40 / 40`;
- direct Lane B column-H proxy-branch rows: `15`;
- candidate/refinement delta rows: `15 / 15`;
- degree-8 near-saturation remains blocked.

Classification:
    `lane_c_comparison_complete_direct_column_h_branch_delta_observed_with_boundaries`

## Iteration 8. Downstream Experiment-Spec Impact

Status: complete.

### Goal

Record exactly how the readiness pass changes interpretation of the property
experiment specs.

### Checks

- [x] Record Experiment B impact:
      column cancellation is a derived proxy under Lane A
- [x] Record Experiment C / D4 impact:
      degree-9 saturation is direct; column-H gate is not direct under Lane A
- [x] Record Experiment D / D5 impact:
      reassignment mapping is direct if event payload exists; interface memory
      is post-event analysis
- [x] Record Experiment G impact:
      full port history remains partial unless ordered snapshot/checkpoint
      analysis is used
- [x] Record D8 impact:
      identity emergence requires sink/basin persistence, not expansion alone
- [x] Enforce report terminology:
      `spark_candidate`, `mechanical_expansion`, `completed_identity_event`

### Verification

- [x] Experiment specs and checklists refer to Lane A/Lane B consistently
- [x] Reports do not use completed spark wording as identity proof unless
      persistence criteria pass

### Implementation Notes

- Downstream interpretation is now captured in:
  - `outputs/grc9v3/hessian_readiness/theory_runtime_gap_ledger.md`
  - `outputs/grc9v3/hessian_readiness/theory_runtime_gap_ledger.json`
  - `implementation/GRC9V3-ArtifactSurfaceHardening.md`
  - `experiments/2026-05-N01-grc9v3-properties/reports/artifact_surface_inventory.md`
  - `experiments/2026-05-N01-grc9v3-properties/implementation/ExperimentSpecificationChecklist.md`
- The property-experiment checklist references the gap ledger before fixture
  coding.
- D2 schema/scoring split is already reflected in
  `DiscriminatorExperimentSpecificationChecklist.md`: Iteration 3 is D2 schema,
  Iteration 10 is D2 scoring, and synthesis follows in Iteration 11.

### Summary

Iteration 8 is complete. Downstream experiment interpretation is aligned with
Lane A: column-H is derived, degree-9 saturation and signed-Hessian spark
evidence are direct, refinement is mechanical until post-event evidence says
otherwise, full port-history motion is partial, and identity claims require
persistent sink/basin support.

# D1-D8 Discriminator Experiment Specification Checklist

This checklist tracks execution of the discriminator experiment program defined
in:

- [`DiscriminatorExperimentSpecification.md`](./DiscriminatorExperimentSpecification.md)

Related local documents:

- [`../hypotheses/Index.md`](../hypotheses/Index.md)
- [`../hypotheses/Experiment-DiscriminatorHypotheses.md`](../hypotheses/Experiment-DiscriminatorHypotheses.md)
- [`../hypotheses/Predictions.md`](../hypotheses/Predictions.md)
- [`ExperimentSpecification.md`](./ExperimentSpecification.md)
- [`ExperimentSpecificationChecklist.md`](./ExperimentSpecificationChecklist.md)

The discriminator specification defines the D-style falsification tests:

- D1: factorization discriminator
- D2: predictive role separation discriminator
- D3: row/column transpose discriminator
- D4: saturation discriminator
- D5: interface-memory discriminator
- D6: port-interaction discriminator
- D7: multiscale discriminator
- D8: identity-emergence discriminator

## Ground Rules

- Keep discriminator code under
  `experiments/2026-05-N01-grc9v3-properties/`.
- Import reusable behavior from `src/pygrc`; do not mutate runtime behavior
  from this discriminator track.
- Treat `current_hybrid_signed_hessian` as the Lane A baseline for D-style
  experiments; direct column-H spark gating belongs only to a separate
  canonical-column-H lane if one is implemented later.
- Do not add new runtime behavior to make D1-D8 pass.
- Every claimed discriminator result must identify the existing artifacts,
  checkpoints, telemetry records, observer records, edge labels, or event logs
  that support it.
- If an observation cannot be reconstructed from existing artifacts, mark the
  relevant discriminator blocked or inconclusive.
- Preserve controls against the anonymous-port null:
  - row-preserving transforms,
  - column-preserving transforms,
  - row/column transpose,
  - arbitrary S9 port relabeling,
  - random triple regrouping,
  - degree/adjacency-only baselines,
  - shuffled target controls where applicable.
- Reuse O-style outputs as D-style inputs where possible.
- Record shared fixture ids, run ids, random seeds, port mappings, and artifact
  maps so discriminator reports can trace their source evidence.
- Every D report must preserve evidence labels:
  - direct
  - derived
  - partial
  - blocked
  - inconclusive
- Every D run manifest must record:
  - lane id
  - git commit
  - fixture id
  - transform id
  - seed
  - runtime params
  - artifact schema version
  - artifact source map
- Separate core-loop factorization evidence from canonical spark-wiring
  convention effects.
- Keep mechanical refinement evidence separate from identity-emergence
  evidence.
- Do not promote visual-only or source-intent-only interpretations.

## Pre-D1 Go/No-Go Readiness

Status: complete.

These checks gate the start of D1. They require no runtime behavior changes.

- [x] `../reports/family_level_synthesis.md` is recorded as complete
- [x] O-style checklist statuses reflect A-G completion
- [x] Readiness notes reflect Lane A complete and Lane B deferred
- [x] D2 schema/scoring split is reflected in this checklist:
  - Iteration 3 defines schema only
  - Iteration 10 runs scoring only after enough O-style and D-style data exist
- [x] D6 checklist explicitly requires all nine port perturbations
- [x] D7 checklist includes true-column vs row/random-triple semantic
      comparison
- [x] D5 checklist includes row-label and random-triple controls
- [x] D8 checklist includes explicit outcome classes and threshold sensitivity
- [x] All D reports preserve direct/derived/partial/blocked/inconclusive
      evidence labels
- [x] All D run manifests record lane, commit, fixture id, transform id, seed,
      params, and artifact schema

### Lane Readiness

- Lane A `current_hybrid_signed_hessian`: ready for D-style discriminator
  experiments using existing artifacts.
- Lane B `canonical_column_h`: deferred to a separate implementation lane and
  must not be inferred from Lane A derived column-H/cancellation proxies.

## Directory Contract

- Discriminator fixtures and run configs:
  - `../configs/`
- Discriminator scripts:
  - `../scripts/`
- Raw discriminator outputs:
  - `../outputs/`
- Human-readable discriminator reports:
  - `../reports/`
- Local implementation trace:
  - `./`

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

## Iteration 0. Discriminator Specification Bootstrap

Status: complete.

### Goal

Create the discriminator hypothesis and specification documents and lock D1-D8
as falsification tests against the anonymous-port null.

### Checks

- [x] Create `hypotheses/Index.md`
- [x] Create `hypotheses/Experiment-DiscriminatorHypotheses.md`
- [x] Create `hypotheses/Predictions.md`
- [x] Create `implementation/DiscriminatorExperimentSpecification.md`
- [x] Create `implementation/DiscriminatorExperimentSpecificationChecklist.md`
- [x] Record D1 factorization discriminator
- [x] Record D2 predictive role separation discriminator
- [x] Record D3 row/column transpose discriminator
- [x] Record D4 saturation discriminator
- [x] Record D5 interface-memory discriminator
- [x] Record D6 port-interaction discriminator
- [x] Record D7 multiscale discriminator
- [x] Record D8 identity-emergence discriminator
- [x] Record blocked/inconclusive handling for missing artifact surfaces

### Verification

- [x] Discriminator documents exist under the experiment directory
- [x] The discriminator specification requires artifact-backed claims
- [x] The discriminator specification defines expected outputs for D1-D8
- [x] The discriminator specification preserves the no-`src/`-mutation rule

### Summary

Iteration 0 is complete. D1-D8 have a local specification and execution
checklist.

## Iteration 1. Shared Discriminator Harness

Status: complete.

### Goal

Build experiment-local helpers shared by D1-D8 for transforms, feature
extraction, artifact comparison, blocked-observation reporting, and pass/fail
classification.

### Checks

- [x] Define common discriminator run-record schema
- [x] Define fixture description schema
- [x] Define port mapping representation
- [x] Define transform metadata representation
- [x] Define artifact extraction method registry
- [x] Define pass/fail/inconclusive classification schema
- [x] Define blocked-observation report schema
- [x] Define output naming conventions for D1-D8
- [x] Define deterministic random seed handling

### Verification

- [x] Produce shared harness notes in `../reports/discriminator_harness.md`
- [x] Produce a machine-readable harness schema under `../outputs/`
- [x] Confirm all D1-D8 expected outputs can be represented
- [x] Confirm harness imports from `src/pygrc` without modifying runtime code

### Summary

Completed the shared discriminator harness.

Generated:

- `../scripts/discriminator_harness.py`
- `../outputs/discriminator_harness_schema.json`
- `../reports/discriminator_harness.md`

The harness records shared D1-D8 run-record, fixture, transform metadata,
artifact extraction registry, classification, blocked-observation, manifest,
and expected-output schemas. It also records the required evidence labels
`direct`, `derived`, `partial`, `blocked`, and `inconclusive`, and the D2
schema/scoring split. No `src/pygrc` behavior was changed.

D1 was rerun after this harness was generated, and its summary/manifest now
record `outputs/discriminator_harness_schema.json` as an input.

## Iteration 2. D1 Factorization Discriminator

Status: complete.

### Goal

Test whether behavior respects the 3x3 row/column factorization more than
arbitrary anonymous nine-port relabeling.

### Checks

- [x] Build or select D1a non-sparking core-loop fixture
- [x] Build or select D1b spark-eligible fixture
- [x] Build or select D1c post-refinement fixture
- [x] Run original port assignment
- [x] Run row-preserving transforms
- [x] Run column-preserving transforms
- [x] Run combined row+column transforms
- [x] Run arbitrary S9 relabel transforms
- [x] Run random triple regrouping controls
- [x] Store inverse transform metadata for every transform
- [x] Define distance metric per artifact class before computing equivariance
      error
- [x] Compute normalized equivariance errors by artifact class
- [x] Split core-loop factorization effects from canonical-wiring effects

### Verification

- [x] Produce `../outputs/d1_equivariance_matrix.csv`
- [x] Produce `../reports/d1_artifact_distance_report.md`
- [x] Produce `../outputs/d1_transform_pair_records.jsonl`
- [x] Produce `../reports/d1_blocked_observations.md`
- [x] Report whether S9 relabeling has higher semantic error than structured
      row/column transforms

### Summary

Completed D1 by reusing completed O-style artifacts without adding runtime
behavior.

Inputs:

- Experiment A row-mode rows for non-sparking core-loop row signatures
- Experiment B column-interface rows for derived column proxy signatures
- Experiment C saturation rows for Lane A spark/capacity behavior
- Experiment D refinement reassignment rows for post-refinement mechanical
  column mapping

Result:

- structured row/column transforms have mean semantic error `0.0` on
  factorization-sensitive row and derived-column artifacts
- the non-factorized S9 relabel / random-triple proxy has mean semantic error
  `1.0` on those same factorization-sensitive artifacts
- Lane A saturation gate evidence is direct but invariant under S9 relabeling,
  so it is reported separately and not counted as factorization evidence
- post-refinement current-port column preservation is direct mechanical
  evidence, but S9 semantic equivalence is marked partial/inconclusive rather
  than inferred from the mapping alone

Classification: `supported_with_lane_a_boundaries`.

## Iteration 3. D2 Predictive Role Separation Schema

Status: complete.

### Goal

Define the D2 feature families, target classes, controls, scoring contract,
blocked-observation rules, and output schemas. Do not run final predictive
scoring in this iteration.

### Checks

- [x] Define degree/adjacency baseline features
- [x] Define row feature family
- [x] Define column feature family
- [x] Define port feature family
- [x] Define random grouping controls
- [x] Define shuffled target controls
- [x] Define geometric/differential targets
- [x] Define interface/routing/refinement targets
- [x] Define edge-local targets
- [x] Define identity-level targets
- [x] Define cross-validation-by-fixture protocol
- [x] Define scoring outputs and blocked-observation report format
- [x] Define schema-only status separately from later scoring status
- [x] Define D2 scoring readiness criteria based on completed O-style and
      D-style run count

### Implementation Notes

- D2 is a synthesis discriminator. This iteration defines the schema early, but
  final scoring should execute only after enough O-style and D-style run data
  exist.

### Verification

- [x] Produce `../reports/d2_target_definitions.md`
- [x] Produce `../reports/d2_blocked_observations.md`
- [x] Confirm D2 scoring is blocked until enough completed run data exist

### Summary

Completed the D2 schema-only pass. Final predictive scoring remains blocked by
design until enough O-style and D-style rows exist.

Generated:

- `../scripts/run_discriminator_d2_schema.py`
- `../outputs/d2_predictive_role_schema.json`
- `../reports/d2_target_definitions.md`
- `../reports/d2_blocked_observations.md`

Defined feature families:

- degree/adjacency baseline
- row
- column
- port
- random grouping controls

Defined target classes:

- geometric/differential
- interface/routing/refinement
- edge-local
- generic activity
- identity-level persistence

The scoring contract uses cross-validation by fixture and compares feature
families against degree/adjacency and random grouping controls. Identity-level
targets remain partial until D8 provides stricter outcome windows.

## Iteration 4. D3 Row/Column Transpose

Status: complete.

### Goal

Test whether transposing a 3x3 port-attached pattern changes behavior in a way
consistent with row and column role separation.

### Checks

- [x] Build base port-matrix fixtures
- [x] Build transposed fixture pairs
- [x] Include single-row-high pattern
- [x] Include single-column-high pattern
- [x] Include diagonal and anti-diagonal controls
- [x] Include rank-1 row x column pattern
- [x] Include symmetric and isotropic controls
- [x] Run pre-event dynamics phase
- [x] Run event-capable dynamics phase
- [x] Run row permutation controls
- [x] Run column permutation controls
- [x] Run arbitrary S9 relabel controls
- [x] Run random triple regrouping controls
- [x] Compute geometry response score
- [x] Compute interface response score
- [x] Compute role separation index

### Verification

- [x] Produce `../outputs/d3_transpose_pair_scores.csv`
- [x] Produce `../reports/d3_role_separation_report.md`
- [x] Produce `../outputs/d3_control_patterns.csv`
- [x] Produce `../reports/d3_blocked_observations.md`
- [x] Report whether transpose moves effects between artifact classes

### Summary

Completed D3 by reusing completed O-style artifacts without adding runtime
behavior.

Generated:

- `../scripts/run_discriminator_d3_transpose.py`
- `../outputs/d3_transpose_pair_scores.csv`
- `../outputs/d3_control_patterns.csv`
- `../outputs/d3_transpose_summary.json`
- `../outputs/d3_transpose_manifest.json`
- `../reports/d3_role_separation_report.md`
- `../reports/d3_blocked_observations.md`

Result:

- row-local geometry response mean: `0.627051`
- transposed row-local geometry response mean: `0.333333`
- column-local interface-proxy response mean: `0.988678`
- transposed column-local interface-proxy response mean: `0.000000`
- role separation index: `1.282396`

Classification: `supported_with_available_controls`.

D3 supports row/column role separation for the available pre-event artifact
classes. Geometry response is reconstructed from Experiment A row-response
dominance; interface response is reconstructed from Experiment B's Lane A
derived column-cancellation proxy.

Boundaries:

- direct column-H transpose behavior remains blocked under Lane A
- event-capable M/M^T transpose refinement behavior is inconclusive because no
  transpose-specific event fixture exists
- anti-diagonal and rank-1 row x column controls are blocked in the completed
  artifact set
- S9/random-triple coverage is a sampled non-factorized proxy, not exhaustive

## Iteration 5. D4 Saturation Discriminator

Status: complete.

### Goal

Test whether nine-port fullness functions as representational bottleneck or
chart exhaustion under canonical spark rules.

### Checks

- [x] Build matched active-degree 7 fixture
- [x] Build matched active-degree 8 fixture
- [x] Build matched active-degree 9 fixture
- [x] Build stress-without-fullness control
- [x] Build fullness-without-stress control
- [x] Run canonical saturation policy
- [x] Run optional near-saturation policy only if already available
- [x] Extract active degree and inactive ports
- [x] Extract sink status
- [x] Extract local instability evidence
- [x] Extract column diagnostic / cancellation evidence
- [x] Extract spark eligibility
- [x] Extract refinement event evidence
- [x] Extract budget before/after event

### Verification

- [x] Produce `../outputs/d4_saturation_gate_table.csv`
- [x] Produce `../reports/d4_saturation_report.md`
- [x] Produce `../reports/d4_blocked_observations.md`
- [x] Report canonical and optional near-saturation results separately
- [x] Report whether fullness alone is insufficient without instability or
      cancellation

### Summary

Completed D4 by reusing completed Experiment C saturation artifacts without
adding runtime behavior.

Generated:

- `../scripts/run_discriminator_d4_saturation.py`
- `../outputs/d4_saturation_gate_table.csv`
- `../outputs/d4_saturation_summary.json`
- `../outputs/d4_saturation_manifest.json`
- `../reports/d4_saturation_report.md`
- `../reports/d4_blocked_observations.md`

Result:

- canonical Lane A gate:
  `active_degree == 9 AND gradient_norm < eps_gradient AND min_signed_hessian < eps_spark`
- degree 7 stressed: no candidate, no refinement
- degree 8 stressed: no candidate, no refinement
- degree 9 stressed: one candidate and one mechanical expansion
- degree 9 stable-Hessian fullness control: no candidate, no refinement
- canonical positive budget error: `0.0` under tolerance `1e-12`
- candidate/refinement counts are invariant across structured transforms and
  the sampled non-factorized relabel control

Classification: `supported_with_lane_a_boundaries`.

D4 supports the Lane A saturation bottleneck discriminator. Fullness alone is
insufficient, and signed-Hessian stress alone is insufficient without
saturation. The positive event requires the combination of active-degree 9
saturation and signed-Hessian degeneracy under the current Lane A gate.

Boundaries:

- direct column-H saturation gating remains blocked under Lane A
- active-degree-8 near-saturation policy is blocked because it is not
  implemented in Lane A
- derived column diagnostics are reported separately and are not gate evidence
- identity-level consequences are inconclusive and deferred to D8

## Iteration 6. D5 Interface-Memory Discriminator

Status: complete.

### Goal

Test whether parent column labels remain predictive after refinement rather
than only during the mechanical rewiring event.

### Checks

- [x] Select refinement runs with auditable old boundary ports
- [x] Extract parent column for each old boundary edge
- [x] Extract post-refinement endpoint or module location
- [x] Extract post-refinement flux over a configured window
- [x] Extract post-refinement basin assignment
- [x] Extract child/satellite relation if available
- [x] Compute immediate column-preservation score
- [x] Compute post-window predictive score
- [x] Compare against random column labels
- [x] Compare against row-label prediction
- [x] Compare against random triple grouping
- [x] Report row-label and random-triple controls separately
- [x] Compare against degree/adjacency baseline
- [x] Run column permutation replay
- [x] Track budget preservation across refinement
- [x] Record post-event persistence window explicitly

### Verification

- [x] Produce `../outputs/d5_interface_memory_edges.csv`
- [x] Produce `../reports/d5_interface_memory_report.md`
- [x] Produce `../outputs/d5_random_column_controls.csv`
- [x] Produce `../reports/d5_blocked_observations.md`
- [x] Report immediate mechanical column memory separately from dynamic
      post-event interface memory

### Summary

Completed D5 by reusing completed Experiment D refinement artifacts without
adding runtime behavior.

Generated:

- `../scripts/run_discriminator_d5_interface_memory.py`
- `../outputs/d5_interface_memory_edges.csv`
- `../outputs/d5_random_column_controls.csv`
- `../outputs/d5_interface_memory_summary.json`
- `../outputs/d5_interface_memory_manifest.json`
- `../reports/d5_interface_memory_report.md`
- `../reports/d5_blocked_observations.md`

Result:

- immediate old-column preservation score: `1.0`
- post-window old-column memory score: `0.888889`
- post-window row-label score: `0.222222`
- post-window random-column score: `0.222222`
- post-window random-triple score: `0.222222`
- persistent endpoint edge count: `32 / 36`
- persistence window: `3` steps
- minimum basin mass threshold: `1.0`
- budget preserved for all refinement rows

Classification: `mechanical_supported_post_window_partial`.

D5 supports immediate mechanical column memory directly from the expansion
payload. It also supports a narrower runtime-state post-window memory result:
old parent column remains more predictive than row labels and sampled random
grouping controls for reassignment endpoints that participate in persistent
child sink/basin rows.

Boundaries:

- post-refinement per-edge flux windows are blocked in the current D artifacts
- persisted checkpoint-window interface memory remains inconclusive
- the module-center reassignment endpoint is not a persistent child-sink row,
  so post-window memory is partial rather than complete
- landscape-general interface memory remains inconclusive

## Iteration 7. D6 Port-Interaction Discriminator

Status: complete.

### Goal

Test whether some responses require row x column interaction terms and cannot
be explained by additive row-only plus column-only summaries.

### Checks

- [x] Build additive row+column fixture controls
- [x] Build interaction-specific port fixtures
- [x] Run matched perturbations for all nine ports `(1,1)` through `(3,3)`
- [x] Record the canonical port ids for all nine perturbations `1..9`
- [x] Match perturbation magnitude across all nine port treatments
- [x] Audit neighbor-shell equality before interpreting interaction residuals
- [x] Define additive row model features
- [x] Define additive column model features
- [x] Define row+column additive model
- [x] Define row x column interaction model
- [x] Define port-level model
- [x] Compare models on edge-local response targets
- [x] Run row permutation controls
- [x] Run column permutation controls
- [x] Include random S9 relabel controls
- [x] Include random triple controls

### Verification

- [x] Produce `../outputs/d6_interaction_model_scores.csv`
- [x] Produce `../reports/d6_port_interaction_report.md`
- [x] Produce `../reports/d6_blocked_observations.md`
- [x] Report whether interaction or port-level features improve over additive
      row+column summaries

### Summary

Completed D6 with matched single-port perturbations for all nine canonical
ports without adding runtime behavior.

Generated:

- `../scripts/run_discriminator_d6_port_interaction.py`
- `../outputs/d6_port_perturbation_treatments.csv`
- `../outputs/d6_interaction_model_scores.csv`
- `../outputs/d6_port_interaction_summary.json`
- `../outputs/d6_port_interaction_manifest.json`
- `../reports/d6_port_interaction_report.md`
- `../reports/d6_blocked_observations.md`

Result:

- canonical ports tested: `1..9`
- matched perturbation magnitude: `true`
- matched neighbor shell: `true`
- primary signed edge-local target additive row+column `R2`: `0.200000`
- primary signed edge-local target row x column interaction `R2`: `1.000000`
- primary signed edge-local target port-level `R2`: `1.000000`
- runtime absolute-flux control additive row+column `R2`: `1.000000`
- runtime absolute-flux interaction required: `false`

Classification: `supported_for_signed_edge_local_target_with_runtime_abs_control`.

D6 supports the claim that at least one edge-local port surface requires row x
column interaction or port-level features: the signed edge-local target is not
fit by additive row+column summaries, while the interaction and port-level
models fit exactly.

Boundaries:

- the positive witness is the configured signed edge-local flux target
- the rebuilt runtime absolute-flux control does not require interaction in
  this matched fixture
- landscape-general port interaction remains inconclusive
- S9 coverage is a sampled non-factorized relabel control, not exhaustive

## Iteration 8. D7 Multiscale Discriminator

Status: complete.

### Goal

Test whether column G/Split reconstructs eligible nonnegative port fields and
whether exact signed flux reconstruction requires J+/J- decomposition.

### Checks

- [x] Identify nonnegative eligible port fields
- [x] Reconstruct conductance/base-weight fields
- [x] Reconstruct absolute-flux or coupling fields
- [x] Reconstruct geometric-length or delay fields if valid as port-attached
      nonnegative fields
- [x] Reconstruct signed flux through J+/J-
- [x] Run compressed signed-flux lossy control
- [x] Include before/after refinement checkpoints
- [x] Include sparse, dense, and zero-column controls
- [x] Compare true-column grouping against true-row grouping
- [x] Compare true-column grouping against random triple grouping
- [x] Report true-column vs true-row vs random-triple semantic comparison
      separately from exact reconstruction error
- [x] Compare grouping usefulness for interface/refinement targets
- [x] Compute reconstruction error by field and checkpoint

### Verification

- [x] Produce `../outputs/d7_reconstruction_errors.csv`
- [x] Produce `../reports/d7_multiscale_report.md`
- [x] Produce `../outputs/d7_signed_flux_controls.csv`
- [x] Produce `../outputs/d7_grouping_semantic_comparison.csv`
- [x] Produce `../reports/d7_blocked_observations.md`
- [x] Report lossy signed compression only as diagnostic, not exact
      reconstruction

### Summary

Completed D7 by reusing Experiment E reconstruction artifacts and D5
interface-memory grouping rows without adding runtime behavior.

Generated:

- `../scripts/run_discriminator_d7_multiscale.py`
- `../outputs/d7_reconstruction_errors.csv`
- `../outputs/d7_signed_flux_controls.csv`
- `../outputs/d7_grouping_semantic_comparison.csv`
- `../outputs/d7_multiscale_summary.json`
- `../outputs/d7_multiscale_manifest.json`
- `../reports/d7_multiscale_report.md`
- `../reports/d7_blocked_observations.md`

Result:

- eligible nonnegative Experiment E fields reconstruct through true-column
  G/Split with max exact error `1.1102230246251565e-16`
- signed flux reconstructs exactly through `J+ / J-` with error `0.0`
- compressed signed-column-total reconstruction is lossy with error
  `2.0833333333333335`
- immediate interface/refinement target scores:
  - true column: `1.0`
  - true row: `0.333333`
  - random triple: `0.222222`
  - single nine-port total: `0.333333`
- post-window persistent endpoint target scores:
  - true column: `0.888889`
  - true row: `0.222222`
  - random triple: `0.222222`
  - single nine-port total: `0.333333`

Classification:
`reconstruction_supported_semantic_columns_supported_with_boundaries`.

D7 supports exact true-column G/Split reconstruction for eligible Experiment E
fields and signed flux through `J+ / J-`. It also supports true-column semantic
usefulness for interface/refinement targets: true columns outperform true rows,
sampled random triples, and a single-total baseline on D5 immediate and
post-window targets.

Boundaries:

- before/after refinement E-style G/Split checkpoints remain blocked because
  persisted refinement checkpoints with E-style port fields are not available
- semantic grouping comparison is clean-fixture evidence only
- D7 does not claim rows or random triples cannot be made mathematically
  invertible with their own profiles

## Iteration 9. D8 Identity-Emergence Discriminator

Status: complete.

### Goal

Test whether mechanical refinement is kept distinct from identity fission and
whether identity-emergence claims require persistent child sink/basin evidence.

### Checks

- [x] Select refinement-only candidate runs
- [x] Select refinement plus persistent child-basin candidate runs
- [x] Extract event and module creation evidence
- [x] Extract post-event sink sets
- [x] Extract post-event basin assignments
- [x] Extract basin mass persistence over configured window
- [x] Extract lineage or parent/child evidence where available
- [x] Define identity-emergence acceptance thresholds
- [x] Record threshold sensitivity grid before classifying accepted identity
      emergence
- [x] Classify every event as:
  - blocked
  - mechanical refinement only
  - transient child candidate
  - persistent child identity
  - multi-child fission
  - collapse/reabsorption
- [x] Run persistence-window sensitivity
- [x] Run minimum-basin-mass sensitivity
- [x] Define negative controls where refinement occurs without child identity
- [x] Classify mechanical refinement, candidate identity fission, and accepted
      identity emergence separately

### Verification

- [x] Produce `../outputs/d8_identity_emergence_windows.csv`
- [x] Produce `../reports/d8_identity_emergence_report.md`
- [x] Produce `../outputs/d8_negative_controls.csv`
- [x] Produce `../reports/d8_blocked_observations.md`
- [x] Produce budget audit for every accepted identity-emergence claim
- [x] Report no identity emergence without persistent sink/basin support

### Summary

Completed D8 by reusing Experiment D refinement and runtime-state persistence
artifacts without adding runtime behavior.

Generated:

- `../scripts/run_discriminator_d8_identity_emergence.py`
- `../outputs/d8_identity_emergence_windows.csv`
- `../outputs/d8_negative_controls.csv`
- `../outputs/d8_identity_emergence_summary.json`
- `../outputs/d8_identity_emergence_manifest.json`
- `../reports/d8_identity_emergence_report.md`
- `../reports/d8_blocked_observations.md`

Result:

- configured persistence window: `3` steps
- configured minimum basin mass: `1.0`
- accepted identity window rows: `60`
- accepted identity events: `20`
- classified refinement events: `20`
- multi-child persistence events: `20`
- accepted budget audit pass: `true`
- strict threshold failure rows: `30`
- no-refinement negative controls: `5`

Classification:
`configured_window_persistent_child_identity_supported_with_boundaries`.

D8 supports configured-window child-basin identity persistence in clean
Experiment D refinement fixtures. Accepted identity requires mechanical
refinement, persistent post-event child sink/basin rows, lineage evidence, and
budget preservation. Mechanical refinement alone is not identity fission.

Boundaries:

- checkpoint-window identity persistence remains inconclusive
- no mechanical-refinement-only positive control is available in the completed
  clean fixture set
- collapse/reabsorption is not observed in the current artifacts
- landscape-general identity emergence remains inconclusive

## Iteration 10. D2 Predictive Role Separation Scoring

Status: complete.

### Goal

Execute D2 after enough O-style and D-style run data exist, testing whether
rows, columns, ports, and ordinary graph baselines predict different artifact
classes with different explanatory strength.

### Checks

- [x] Build D2 dataset from completed O-style and D-style runs
- [x] Preserve fixture ids, run ids, seeds, port mappings, and artifact maps
- [x] Extract degree/adjacency baseline features
- [x] Extract row feature family
- [x] Extract column feature family
- [x] Extract port feature family
- [x] Extract random grouping controls
- [x] Extract shuffled target controls
- [x] Run cross-validation by fixture
- [x] Compare feature-family performance by target class
- [x] Identify target classes where H0 remains competitive

### Verification

- [x] Produce `../outputs/d2_feature_family_scores.csv`
- [x] Produce `../reports/d2_cross_validation_report.md`
- [x] Produce `../outputs/d2_random_grouping_controls.csv`
- [x] Produce `../reports/d2_blocked_observations.md`
- [x] Report whether degree/adjacency explains all targets as well as
      row/column/port features
- [x] Mark D2 inconclusive if the completed run dataset is too small

### Summary

Completed D2 scoring by aggregating completed A-G and D1/D3/D4/D5/D6/D7/D8
artifact scores into a feature-family scorecard. No runtime behavior was
added.

Generated:

- `../scripts/run_discriminator_d2_scoring.py`
- `../outputs/d2_feature_family_scores.csv`
- `../outputs/d2_random_grouping_controls.csv`
- `../outputs/d2_scoring_summary.json`
- `../outputs/d2_scoring_manifest.json`
- `../reports/d2_cross_validation_report.md`
- `../reports/d2_blocked_observations.md`

Result:

- row features are strongest for geometric/differential targets:
  - Experiment A row dominance: `1.0`
  - D3 row-geometry response: `0.627051` versus transpose baseline `0.333333`
- column features are strongest for interface/refinement/multiscale targets:
  - Experiment B derived column proxy dominance: `1.0`
  - D5 immediate column memory: `1.0`
  - D5 post-window column memory: `0.888889`
  - D7 immediate true-column semantic grouping: `1.0`
- port features are strongest for edge-local targets:
  - D6 signed edge-local port model: `R2 = 1.0`
  - Experiment G observer-local motion controls: `1.0`
- identity-level persistence requires a composite
  port-plus-column-plus-global-basin context:
  - D8 configured-window accepted identity criteria: `1.0`
- random grouping controls do not explain all targets:
  - D1 sampled non-factorized preservation score: `0.0`
  - D5/D7 random-triple interface scores: `0.222222`
  - D6 random-triple `R2`: `0.1`
- degree/adjacency does not explain all targets, but remains competitive for:
  - D4 Lane A saturation gate
  - Experiment F edge-label path disagreement
  - D5 post-window endpoint persistence in the clean fixture

Classification:
`role_separation_supported_with_scorecard_cv_limitations`.

D2 supports predictive role separation at the artifact-scorecard level. Rows,
columns, ports, and ordinary graph/edge-label baselines predict different
target classes with different strength. H0 remains competitive for generic
capacity/path-label targets and for endpoint persistence availability in one
clean fixture.

Boundaries:

- full fitted held-out-landscape cross-validation remains inconclusive because
  the completed artifact set is a small deterministic clean fixture set
- shuffled-target predictive controls are recorded but not scored
- D2 is not a landscape-general predictive robustness suite

## Iteration 11. Discriminator Synthesis

Status: complete.

### Goal

Synthesize D1-D8 into a family-level discriminator result against the
anonymous-port null.

### Checks

- [x] Summarize D1 factorization result
- [x] Summarize D2 predictive separation result
- [x] Summarize D3 transpose result
- [x] Summarize D4 saturation result
- [x] Summarize D5 interface-memory result
- [x] Summarize D6 port-interaction result
- [x] Summarize D7 multiscale result
- [x] Summarize D8 identity-emergence result
- [x] Classify each D hypothesis as supported, weakened, refuted, blocked, or
      inconclusive
- [x] Compare results to `hypotheses/Predictions.md`
- [x] Record which parts of H0 remain competitive
- [x] Record missing reusable surfaces as future implementation candidates

### Verification

- [x] Produce `../reports/discriminator_synthesis.md`
- [x] Produce `../outputs/discriminator_hypothesis_status.csv`
- [x] Ensure every supported discriminator cites artifact-backed evidence
- [x] Ensure source-intent-only claims are not promoted
- [x] Ensure any suggested `src/` changes are follow-up candidates, not hidden
      experiment changes

### Summary

Completed the D1-D8 discriminator synthesis without adding runtime behavior.

Generated:

- `../scripts/run_discriminator_synthesis.py`
- `../outputs/discriminator_hypothesis_status.csv`
- `../outputs/discriminator_prediction_comparison.csv`
- `../outputs/discriminator_followup_surfaces.csv`
- `../outputs/discriminator_synthesis_summary.json`
- `../outputs/discriminator_synthesis_manifest.json`
- `../reports/discriminator_synthesis.md`

Classification:
`anonymous_port_null_partially_rejected_with_lane_a_boundaries`.

Conclusion:

D1-D8 partially reject the anonymous-port null for controlled Lane A artifact
classes. Rows, columns, ports, composite basin context, and ordinary
graph/edge-label baselines explain different artifact classes. H0 is no longer
competitive for all artifacts.

H0 remains competitive for:

- D4 Lane A saturation gate
- Experiment F edge-label path disagreement
- D5 post-window endpoint persistence availability in the clean fixture

Supported discriminator results:

- D1 factorization:
  `structured_error = 0.0`, sampled non-factorized `s9_error = 1.0`
- D2 scorecard:
  row, column, port, composite, and graph/edge-label features explain different
  target classes
- D3 transpose:
  role separation index `1.282396`
- D4 saturation:
  Lane A active-degree-9 signed-Hessian gate supported with budget error `0.0`
- D5 interface memory:
  immediate column memory `1.0`, post-window column memory `0.888889`
- D6 port interaction:
  signed edge-local additive `R2 = 0.2`, port/intersection `R2 = 1.0`
- D7 multiscale:
  true-column G/Split max error `1.11e-16`, true columns beat random triples
- D8 identity emergence:
  configured-window accepted events `20`, strict-threshold failures `30`

Boundaries:

- direct column-H proxy-branch gate evidence remains blocked under Lane A and
  available only in explicit Lane B/Lane C artifacts
- degree-8 near-saturation remains blocked under Lane A
- checkpoint-window identity persistence remains inconclusive
- landscape-general identity emergence remains inconclusive
- full fitted held-out-landscape predictive CV remains inconclusive
- reusable motion-loader full port histories remain partial
- S9/random controls are sampled, not exhaustive

# GRC9V3 Properties Experiment Specification Checklist

This checklist tracks execution of the observational experiment program defined
in:

- [`ExperimentSpecification.md`](./ExperimentSpecification.md)

Related local documents:

- [`../hypotheses/Index.md`](../hypotheses/Index.md)
- [`../hypotheses/Experiment-DiscriminatorHypotheses.md`](../hypotheses/Experiment-DiscriminatorHypotheses.md)
- [`../hypotheses/Predictions.md`](../hypotheses/Predictions.md)
- [`DiscriminatorExperimentSpecification.md`](./DiscriminatorExperimentSpecification.md)

The specification defines the O-style experiment classes:

- Experiment A: row-mode stress
- Experiment B: column-interface cancellation
- Experiment C: port saturation and near-saturation
- Experiment D: column-preserving refinement and child identity inheritance
- Experiment E: coarse-graining and Split reconstruction
- Experiment F: metric path, temporal-delay path, and strongest-flux path
  disagreement
- Experiment G: row-preserving, column-changing motion observer

## Ground Rules

- Keep experiment code under `experiments/2026-05-N01-grc9v3-properties/`.
- Import reusable behavior from `src/pygrc`; do not mutate runtime behavior
  from this experiment track.
- Treat `current_hybrid_signed_hessian` as the Lane A baseline for these
  experiments; direct column-H spark gating belongs only to a separate
  canonical-column-H lane if one is implemented later.
- Do not add new spark mechanics, identity logic, routing rules, or telemetry
  producers inside `src/pygrc` to make an experiment pass.
- Treat telemetry as an observability surface. If an observation cannot be
  reconstructed from existing artifacts, mark the claim blocked or
  inconclusive.
- Do not treat source-authored intent as evidence.
- Preserve paired/counterfactual controls: row permutation, column permutation,
  row/column transpose, degree-preserving random port relabeling,
  energy-matched perturbations, and seed replay.
- Reuse O-style outputs as D-style inputs where possible.
- Record shared fixture ids, run ids, random seeds, port mappings, and artifact
  maps so O-style and D-style reports do not diverge.
- Keep mechanical refinement claims separate from identity fission claims.
- Require persistent sink/basin artifacts before making child identity claims.
- Keep outputs and generated reports under this experiment family.

## Directory Contract

- Fixtures, run configs, and manifest-like experiment inputs:
  - `../configs/`
- Experiment-local scripts:
  - `../scripts/`
- Generated artifacts and raw outputs:
  - `../outputs/`
- Human-readable reports and summary tables:
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

## Iteration 0. Specification Bootstrap

Status: complete.

### Goal

Create the experiment-local hypothesis and specification documents and lock the
scope as observational research over the existing `GRC9V3` runtime.

### Checks

- [x] Create `README.md`
- [x] Create `hypotheses/Index.md`
- [x] Create `hypotheses/Experiment-DiscriminatorHypotheses.md`
- [x] Create `hypotheses/Predictions.md`
- [x] Create `implementation/ExperimentSpecification.md`
- [x] Create `implementation/DiscriminatorExperimentSpecification.md`
- [x] Create `implementation/ExperimentSpecificationChecklist.md`
- [x] Record the anonymous-port null hypothesis
- [x] Record O-style semantic hypotheses
- [x] Record D1-D8 discriminator hypotheses
- [x] Record that experiments must not mutate `src/pygrc`
- [x] Record that unsupported observations are blocked or inconclusive, not
      inferred

### Verification

- [x] Local documents exist under the experiment directory
- [x] The top-level experiment README links the hypothesis and specification
      entry points
- [x] The specification distinguishes source intent from runtime evidence
- [x] The specification distinguishes mechanical refinement from identity
      fission

### Summary

Iteration 0 is complete. The experiment family has a hypothesis map,
observational specification, discriminator specification, predictions document,
and execution checklist.

## Iteration 1. Artifact Surface Inventory

Status: complete.

### Goal

Map each observation required by `ExperimentSpecification.md` to existing
runtime artifacts, checkpoints, telemetry records, edge labels, event logs, or
derived analysis values.

### Checks

- [x] Inventory existing `GRC9V3` state fields needed for node-level evidence
- [x] Inventory existing checkpoint fields needed for edge/port evidence
- [x] Inventory existing event records needed for spark/refinement evidence
- [x] Inventory existing edge-label concepts and their actual runtime field
      names:
  - geometric separation / metric length
  - temporal delay
  - functional coupling or flux strength
  - conductance/base weight
  - signed flux or flux proxy
- [x] Inventory existing coarse-graining/Split surfaces
- [x] Inventory existing motion observer surfaces that can support Experiment G
- [x] Record blocked observations by experiment class
- [x] Record derived reconstruction formulas for row, column, and port
      features
- [x] Record artifact source path, artifact type, and reconstruction method for
      every available or derived observation
- [x] Treat named edge labels as candidate concepts; do not require exact field
      names unless the runtime already exposes them

### Verification

- [x] Produce `../reports/artifact_surface_inventory.md`
- [x] Produce a machine-readable artifact map under `../outputs/`
- [x] Every Experiment A-G observation is classified as available, derived,
      partial, or blocked
- [x] No inventory item requires adding runtime behavior to `src/pygrc`

### Summary

Iteration 1 is complete. Existing `GRC9V3` state, checkpoint, telemetry,
coarse-graining, event, and motion surfaces are sufficient to begin the shared
fixture and transform harness. No surface is fully blocked, but column
cancellation is currently a derived GRC9V3 proxy and full port-history motion
classification requires experiment-local checkpoint overlay analysis.

Before coding property-experiment fixtures, also consult the repo-level
theory/runtime gap ledger:

- `outputs/grc9v3/hessian_readiness/theory_runtime_gap_ledger.md`
- `outputs/grc9v3/hessian_readiness/theory_runtime_gap_ledger.json`

## Iteration 2. Shared Fixture And Transform Harness

Status: complete.

### Goal

Create experiment-local fixture builders and transform utilities for paired
counterfactual runs.

### Checks

- [x] Define a fixture schema for central-node port matrices
- [x] Define row permutation transforms
- [x] Define column permutation transforms
- [x] Define row/column transpose transforms
- [x] Define degree-preserving random port relabeling transforms
- [x] Define energy-matching checks for perturbations
- [x] Define seed replay conventions
- [x] Define artifact extraction entry points
- [x] Define comparison report schema

### Verification

- [x] Transform utilities preserve graph degree and edge count where required
- [x] Row and column transforms preserve the 3x3 factorization
- [x] Random port relabeling breaks the 3x3 factorization
- [x] Fixture generation is deterministic under a declared seed
- [x] Fixture scripts import from `src/pygrc` without modifying library files

### Summary

Iteration 2 is complete. Added experiment-local fixture and transform harness:

- `../scripts/grc9v3_fixture_harness.py`
- `../configs/shared_fixture_transform_manifest.json`
- `../outputs/iter2_fixture_transform_verification.json`
- `../reports/iter2_shared_fixture_transform_harness.md`

The harness defines a deterministic central-node 3x3 port-matrix fixture,
row/column/transpose/random relabel transforms, partial-activity and row-stress
helper fixtures, perturbation-energy matching for balanced and non-uniform
fixtures, seed replay conventions, deterministic run-id convention, artifact
extraction entry points, blocked-observation CSV schema, runtime binding
requirements, fixture-to-state mapping convention, and comparison report schema.
It imports canonical port helpers from `src/pygrc` but does not modify runtime
behavior. The generated manifest records Lane A as
`current_hybrid_signed_hessian` and keeps the signed Hessian backend as a
runtime assumption rather than a fixture property.

## Iteration 3. Experiment A Row-Mode Stress

Status: complete.

### Goal

Test whether row-local perturbations produce row-local differential or
geometric signatures.

### Checks

- [x] Build row-1, row-2, row-3, and balanced perturbation fixtures
- [x] Match total perturbation magnitude and squared perturbation magnitude
- [x] Run row permutation controls
- [x] Run column permutation controls
- [x] Run row/column transpose controls
- [x] Run degree-preserving random port relabel controls
- [x] Extract row-local response artifacts
- [x] Compute row-local response scores
- [x] Record whether isotropic `K` terms dominate or mute the row-local signal

### Verification

- [x] Produce `../reports/experiment_a_row_mode_stress.md`
- [x] Produce row-local perturbation tables under `../outputs/`
- [x] Report whether row signatures move under row permutation
- [x] Report whether random relabeling weakens row interpretability
- [x] Mark unavailable row observations as blocked, not failed

### Summary

Iteration 3 is complete. Added a raw GRC9V3 central-node Experiment A runner:

- `../scripts/run_experiment_a_row_mode_stress.py`
- `../outputs/experiment_a_row_mode_stress_rows.csv`
- `../outputs/experiment_a_row_mode_stress_summary.json`
- `../outputs/experiment_a_row_mode_stress_manifest.json`
- `../reports/experiment_a_row_mode_stress.md`

The run uses raw experiment-local GRC9V3 fixtures rather than landscape seeds:
one central node with all nine ports active and one neighbor per port. Row-1,
row-2, row-3, and balanced fixtures match total absolute coherence delta,
total squared coherence delta, affected-port count, and perturbation energy.

Observed Lane A result: identity row-local fixtures produce the expected
dominant row, row-permutation controls move the dominant row as expected,
column permutation preserves the stressed row, transpose controls remove the
clean row-local expectation, and random relabeling is treated as a
non-factorized scramble control. The report also records that isotropic `K`
terms are large relative to the anisotropic span, so the row signal is visible
but potentially muted by isotropic terms.

The run manifest records the script path, git commit, branch, Lane A runtime
params, fixture ids, seed, transform mappings, artifact schema version, output
paths, validation commands, and reuse notes for later D1/D2/D3 analysis.

## Iteration 4. Experiment B Column-Interface Cancellation

Status: complete.

### Goal

Test whether column-local cancellation or pressure affects interface,
routing, spark risk, or refinement behavior.

### Checks

- [x] Build column-1, column-2, and column-3 near-cancellation fixtures
- [x] Build sign-crossing fixtures if existing runtime artifacts can support
      them
- [x] Preserve row energy across matched column treatments where possible
- [x] Run column permutation controls
- [x] Run row permutation controls
- [x] Run row/column transpose controls
- [x] Run random port relabel controls
- [x] Extract column-local cancellation, pressure, and event evidence

### Verification

- [x] Produce `../reports/experiment_b_column_interface_cancellation.md`
- [x] Produce column cancellation tables under `../outputs/`
- [x] Separate spark candidate, refinement event, and completed identity-level
      event terminology
- [x] Mark routing/refinement claims blocked if artifacts do not expose them

### Summary

Iteration 4 is complete. Added a raw GRC9V3 central-node Experiment B runner:

- `../scripts/run_experiment_b_column_interface_cancellation.py`
- `../outputs/experiment_b_column_interface_cancellation_rows.csv`
- `../outputs/experiment_b_column_interface_cancellation_sign_crossings.csv`
- `../outputs/experiment_b_column_interface_cancellation_summary.json`
- `../outputs/experiment_b_column_interface_cancellation_manifest.json`
- `../reports/experiment_b_column_interface_cancellation.md`
- `../reports/experiment_b_column_interface_cancellation_blocked_observations.csv`

The run uses clean saturated central-node fixtures and treats column-H as a
derived Lane A analysis proxy, not a direct spark gate. Column-local
plus/minus coherence patterns produce the expected target-column derived
cancellation/pressure proxy, column permutation moves that proxy, row
permutation preserves the proxy column, transpose controls remove the
predefined clean column claim, random relabel controls remove the clean
predefined column interpretation, and sign-crossing proxy pairs are available
as paired derived observations. No spark candidate, refinement, or completed
identity-level event occurred in this fixture, so direct column-H gating,
routing, refinement, and identity-event claims are blocked or inconclusive as
recorded in the blocked-observations CSV.

Validation passed: `py_compile`, `ruff`, JSON validation for summary/manifest,
and scoped `git diff --check`.

## Iteration 5. Experiment E Coarse-Graining And Split Reconstruction

Status: complete.

### Goal

Test the clearest multiscale column claim: lossless G/Split reconstruction for
eligible nonnegative port-attached fields and signed-flux exactness through
positive/negative decomposition.

### Checks

- [x] Identify eligible nonnegative port-attached fields
- [x] Run G/Split reconstruction for conductance or base weight
- [x] Run G/Split reconstruction for absolute flux or functional coupling
- [x] Run J+/J- reconstruction for signed flux where available
- [x] Run compressed signed-flux lossy control where applicable
- [x] Include zero-column and single-active-port-column controls
- [x] Include mixed-sign flux-column controls where available
- [x] Include before/after topology-change checkpoints if available

### Verification

- [x] Produce `../reports/experiment_e_coarse_graining_split.md`
- [x] Produce field-by-field reconstruction error tables under `../outputs/`
- [x] Report exact or near-exact reconstruction for eligible nonnegative fields
- [x] Report signed-flux exactness only when J+/J- evidence is available
- [x] Mark unavailable fields as blocked for that field

### Summary

Iteration 5 is complete. Added a raw GRC9V3 coarse-graining/Split runner:

- `../scripts/run_experiment_e_coarse_graining_split.py`
- `../outputs/experiment_e_coarse_graining_split_errors.csv`
- `../outputs/experiment_e_coarse_graining_split_summary.json`
- `../outputs/experiment_e_coarse_graining_split_manifest.json`
- `../reports/experiment_e_coarse_graining_split.md`
- `../reports/experiment_e_coarse_graining_split_blocked_observations.csv`

Eligible nonnegative port-attached fields reconstruct exactly or near-exactly:
conductance, geometric length, temporal delay, flux coupling, and absolute
flux. Signed flux reconstructs exactly through the public `signed_flux_split`
J+/J- path using the local oriented-flux convention. The compressed
signed-column-total control is explicitly lossy in the mixed-sign column
fixture. Zero-column and single-active-port-in-column controls pass. A
curvature proxy field is blocked because no nonnegative curvature coarse field
is exposed, and before/after topology-change reconstruction is inconclusive
until refinement fixtures exist. Semantic usefulness of true columns versus
rows/random triples remains deferred to D7.

Validation passed: `py_compile`, `ruff`, JSON validation for summary/manifest,
and scoped `git diff --check`.

## Iteration 6. Experiment C Saturation And Near-Saturation

Status: complete.

### Goal

Test whether finite port capacity acts as a meaningful canonical refinement
gate.

### Checks

- [x] Build active-degree 7, 8, and 9 sink-candidate fixtures
- [x] Match local stress, coherence, flux pressure, and neighborhood structure
      where possible
- [x] Separate canonical saturation from optional near-saturation policy
- [x] Extract sink status before spark eligibility
- [x] Extract instability evidence separately from active degree
- [x] Extract column diagnostic / cancellation evidence separately from active
      degree
- [x] Run same-instability-without-saturation controls
- [x] Run same-saturation-without-instability controls
- [x] Extract spark eligibility and refinement evidence
- [x] Extract budget before/after event where available

### Verification

- [x] Produce `../reports/experiment_c_saturation.md`
- [x] Report canonical degree-9 behavior separately from near-saturation
      behavior
- [x] Report non-events explicitly when stressed unsaturated fixtures do not
      refine
- [x] Mark missing event surfaces as blocked or inconclusive

### Summary

Iteration 6 is complete. Added a raw GRC9V3 saturation runner:

- `../scripts/run_experiment_c_saturation.py`
- `../outputs/experiment_c_saturation_rows.csv`
- `../outputs/experiment_c_saturation_summary.json`
- `../outputs/experiment_c_saturation_manifest.json`
- `../reports/experiment_c_saturation.md`
- `../reports/experiment_c_saturation_blocked_observations.csv`

The run uses matched central-node fixtures for active degree 7, 8, and 9
under the Lane A gate formula:

```text
active_degree == 9 AND gradient_norm < eps_gradient AND min_signed_hessian < eps_spark
```

The result strongly supports the Lane A representational-bottleneck claim.
Degree 7 and degree 8 stressed fixtures share the same central signed-Hessian
stress as the degree 9 positive fixture but produce no candidates or
refinement events. The degree 9 stressed fixture produces one candidate and
one mechanical expansion with budget evidence. The degree 9 stable-Hessian
control does not trigger merely because all ports are occupied.

Therefore, under Lane A, fullness alone is insufficient, signed-Hessian stress
alone is insufficient when unsaturated, and the positive event requires the
combination of full nine-port occupancy and signed-Hessian degeneracy.

Candidate and refinement counts are invariant across row permutation, column
permutation, row/column transpose, and degree-preserving random relabel
controls. This is expected for the Lane A gate and is interpreted as capacity
plus signed-Hessian bottleneck behavior, not direct row/column semantic
evidence.

The positive run records candidate payload availability, mechanical expansion
payload availability, reassignment map availability, event sequencing/step
indices, and budget provenance from `hybrid_mechanical_expansion.payload`.
The canonical positive budget error is `0.0` under tolerance `1e-12`.

Near-saturation is blocked under Lane A because no active-degree-8 policy is
implemented. Direct column-H gate evidence remains blocked under Lane A. The
completed event emitted by the canonical positive run is recorded as event-level
mechanical evidence only; persistent child identity claims remain deferred to
Experiment D.

Validation passed: `py_compile`, `ruff`, JSON validation for summary/manifest.

## Iteration 7. Experiment D Refinement And Child Identity

Status: complete.

### Goal

Test whether refinement preserves column interface structure and whether any
post-refinement child identity claims are backed by persistent sink/basin
artifacts.

### Checks

- [x] Select or induce refinement runs with auditable parent ports
- [x] Extract old boundary edge mapping
- [x] Extract new module endpoint mapping
- [x] Compare old column to post-refinement module location
- [x] Check budget preservation around refinement
- [x] Extract post-event sink set
- [x] Extract post-event basin assignments
- [x] Check child basin persistence over a configured window
- [x] Define persistence thresholds before classifying child identity
- [x] Run threshold sensitivity over persistence window and minimum basin mass
- [x] Separate mechanical refinement from identity fission

### Verification

- [x] Produce `../reports/experiment_d_refinement_identity.md`
- [x] Produce boundary-edge reassignment tables under `../outputs/`
- [x] Report column-preserving refinement support separately from child
      identity support
- [x] Reject visual-only or source-only child identity claims

### Summary

Iteration 7 is complete. Added a raw GRC9V3 refinement and child-persistence
runner:

- `../scripts/run_experiment_d_refinement_identity.py`
- `../outputs/experiment_d_refinement_identity_reassignments.csv`
- `../outputs/experiment_d_refinement_identity_persistence.csv`
- `../outputs/experiment_d_refinement_identity_thresholds.csv`
- `../outputs/experiment_d_refinement_identity_conditions.csv`
- `../outputs/experiment_d_refinement_identity_summary.json`
- `../outputs/experiment_d_refinement_identity_manifest.json`
- `../reports/experiment_d_refinement_identity.md`
- `../reports/experiment_d_refinement_identity_blocked_observations.csv`

The run reuses the Iteration 6 saturated stressed positive fixture shape and
tests uniform expansion transfer plus runtime-supported custom column-skewed
expansion weights. A degree-8 stressed condition is retained as the
no-refinement control.

Mechanical refinement support is clean in the raw fixtures: every observed
mechanical expansion exposes a `hybrid_mechanical_expansion.payload.
reassignment_map`, all nine old boundary edges are reassigned, old boundary
columns match the new module endpoint column, and unit-measure budget is
preserved within tolerance.

Child-basin support is narrower and thresholded. Post-event child sink/basin
artifacts persist over the configured three-step runtime-state window with
minimum basin mass `1.0`, and threshold-sensitivity rows are recorded through
a five-step trace. Snapshot source is experiment-local runtime state; lineage
source is expansion payload plus post-event basin assignment. This supports
configured-window child-basin persistence in the clean raw fixtures, not
identity fission from expansion alone and not landscape-general identity
behavior.

Blocked or inconclusive items:

- inflow-weighted transfer is blocked because GRC9V3 exposes equal/custom
  expansion distribution weights, not an inflow-weighted transfer lane
- checkpoint-window identity persistence is inconclusive because Iteration 7
  uses experiment-local runtime state snapshots rather than persisted
  checkpoint observer windows
- landscape-general child identity remains inconclusive

Validation passed: `py_compile`, `ruff`, JSON validation for summary/manifest,
and scoped `git diff --check`.

### Iteration 7.1 Deferred Unblocking Decisions

Status: complete.

No new runtime behavior or broad landscape study is added in this pass.

Keep blocked:

- inflow-weighted transfer remains blocked because GRC9V3 exposes equal/custom
  expansion distribution weights, not an inflow-weighted transfer lane
- direct column-H proxy-branch gate evidence remains blocked under Lane A and
  available only in explicit Lane B/Lane C artifacts
- near-saturation degree-8 policy remains blocked under Lane A

Keep deferred:

- landscape-general child identity remains inconclusive until a later
  landscape/seed robustness suite

Candidate addenda, but not required before Experiment F:

- persisted checkpoint-window identity persistence
- before/after topology-change G/Split reconstruction using the Experiment D
  refinement fixture

Default next step remains Experiment F.

## Iteration 8. Experiment F Path Disagreement

Status: complete.

### Goal

Test whether metric, temporal-delay, and strongest-flux path notions can
disagree while remaining auditable edge by edge.

### Checks

- [x] Build or select a fixture with at least three corridors between endpoints
- [x] Compute metric path from available geometric labels
- [x] Compute delay path from available temporal-delay labels
- [x] Compute flux path from available flux or coupling labels
- [x] Define strongest-flux path scoring convention:
  - bottleneck flux
  - cumulative flux
  - functional-coupling route
- [x] Run equalized-label controls
- [x] Run equalized-flux controls
- [x] Run port relabel controls
- [x] Produce edge-by-edge path explanations

### Verification

- [x] Produce `../reports/experiment_f_path_disagreement.md`
- [x] Produce path tables under `../outputs/`
- [x] Report whether `P_metric`, `P_delay`, and `P_flux` differ
- [x] Mark path criteria blocked when labels are unavailable

### Summary

Completed Experiment F path disagreement under the Lane A baseline using a
three-corridor fixture with explicit edge-label surfaces.

Scoring conventions are recorded in the report header:

- metric path minimizes `sum geometric_length(e)`
- delay path minimizes `sum temporal_delay(e)`
- primary flux path maximizes `min_e abs(signed_flux(e))`
- primary coupling path maximizes `min_e flux_coupling(e)`
- cumulative absolute flux and cumulative coupling are recorded as secondary
  diagnostics
- ties prefer fewer edges, then lexicographic edge-id order

The base fixture produces the intended auditable disagreement:

- `P_metric` selects corridor A (`path_0_A_metric_short`)
- `P_delay` selects corridor B (`path_1_B_delay_fast`)
- `P_flux_bottleneck` and `P_coupling_bottleneck` select corridor C
  (`path_2_C_flux_strong`)

Equalized geometric, temporal, flux/coupling, and all-label controls show that
path choices change or collapse for the intended label reason. The
degree-preserving random port relabel preserves path choices. The result
supports multi-label edge-surface path disagreement, not direct row/column
semantic separation.

## Iteration 9. Experiment G Mixed Row/Column Motion

Status: complete.

### Goal

Test whether existing artifacts and observers can classify behavior as
row-preserving/column-changing or column-preserving/row-changing.

### Checks

- [x] Build or select runs with dominant local behavior moving across ports
- [x] Extract dominant flux edge by timestep where available
- [x] Extract dominant boundary edge by timestep where available
- [x] Extract basin or successor changes where available
- [x] Classify transitions by row and column
- [x] Define transition classes:
  - row-preserving/column-changing
  - column-preserving/row-changing
  - both-changing
  - neither-changing
- [x] Run row permutation controls
- [x] Run column permutation controls
- [x] Run random port relabel controls
- [x] Run static no-motion baseline

### Verification

- [x] Produce `../reports/experiment_g_mixed_motion.md`
- [x] Produce port-history tables under `../outputs/`
- [x] Report row-preserving/column-changing classifications only when backed by
      edge/port artifacts
- [x] Mark observer-local claims blocked when artifact windows are insufficient

### Summary

Completed Experiment G under the Lane A `current_hybrid_signed_hessian`
baseline using an experiment-local checkpoint-overlay observer over
`GRC9V3State.port_edges` and topology endpoint metadata.

The observer selects the dominant central-node incident edge by maximum
`abs(PortEdge.flux_uv)`, records the selected central port and successor node,
derives row/column coordinates with `port_to_rc`, and classifies adjacent
timestep transitions as:

- row-preserving/column-changing
- column-preserving/row-changing
- both-changing
- neither-changing

Canonical controls match the expected classes:

- row-2 sweep `4 -> 5 -> 6` classifies as row-preserving/column-changing
- column-3 sweep `3 -> 6 -> 9` classifies as column-preserving/row-changing
- static port `5 -> 5 -> 5` classifies as neither-changing
- row and column permutations preserve the expected transition class while
  moving the concrete row or column labels

The degree-preserving random port relabel is non-factorized and weakens
semantic interpretability rather than serving as a canonical row/column test.

The result supports observer-local mixed row/column motion classification in
clean checkpoint-overlay fixtures. Full reusable motion-loader port histories,
basin-assignment motion, and landscape-general motion semantics remain
inconclusive.

## Iteration 10. Cross-Experiment Synthesis

Status: complete.

### Goal

Synthesize A-G results into a family-level assessment against the
anonymous-port null and the O-style semantic hypotheses.

### Checks

- [x] Summarize row evidence
- [x] Summarize column evidence
- [x] Summarize port intersection evidence
- [x] Summarize refinement evidence
- [x] Summarize multiscale evidence
- [x] Summarize path-label evidence
- [x] Summarize motion-observer evidence
- [x] Classify each hypothesis as supported, weakened, refuted, blocked, or
      inconclusive
- [x] Compare observed results to `hypotheses/Predictions.md`
- [x] Record missing reusable surfaces as future implementation candidates

### Verification

- [x] Produce `../reports/family_level_synthesis.md`
- [x] Produce a hypothesis status table under `../outputs/`
- [x] Ensure every supported claim cites runtime artifacts or derived reports
- [x] Ensure no source-intent-only claim is promoted
- [x] Ensure proposed `src/` changes are listed as follow-up candidates, not
      made inside the experiment track

### Summary

Completed the O-style A-G family-level synthesis under the Lane A
`current_hybrid_signed_hessian` baseline.

The synthesis concludes that the O-style pass partially weakens the
anonymous-port null across controlled artifact classes while preserving Lane A
and clean-fixture boundaries.

Strong supported themes:

- row-local stress signatures
- derived column-local proxy observability
- G/Split reconstruction and signed flux `J+ / J-` exactness
- Lane A degree-9 saturation bottleneck
- column-preserving mechanical refinement
- multi-label edge path disagreement
- observer-local mixed row/column motion classification

Bounded or inconclusive themes:

- direct column-H spark gating
- near-saturation degree-8 policy
- inflow-weighted transfer
- identity fission or landscape-general identity
- full reusable motion-loader port histories
- landscape/seed generality
- formal D-style discriminator baselines

Generated the family-level hypothesis table, experiment-status table,
prediction check, follow-up surface list, summary JSON, manifest, and report.
No `src/pygrc` behavior was changed. The next layer is the D-style
discriminator pass.

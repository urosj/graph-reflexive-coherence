# Polarized Basin Loops Implementation Checklist

This checklist tracks execution of:

- [`PolarizedBasinLoopsImplementationPlan.md`](./PolarizedBasinLoopsImplementationPlan.md)
- [`../README.md`](../README.md)

It is the replay log for what was done, why it was done, how it was done, and
what evidence was produced.

## Ground Rules

- Keep experiment code under
  `experiments/2026-05-N03-grc9v3-polarized-basin-loops/`.
- Use existing `src/pygrc` runtime behavior; do not mutate runtime semantics
  from this experiment track.
- Treat any required `src/*` change as a stop condition. Pause, record the
  missing capability, and request explicit approval for a separate core-library
  task.
- Treat this as a fixed-topology polarity-loop experiment first.
- Treat fixed topology as an execution-surface requirement, not only a theory
  scope statement.
- Prefer `runner_mode = "fixed_topology_continuity_runner"` for the first
  implementation pass.
- Do not enable topology growth, pruning, spark refinement, or adaptive
  movement in the first implementation pass.
- Do not use full `GRC9V3.step()` unless the runner proves topology-changing
  stages are disabled or no-op at every step.
- Do not claim movement, locomotion, identity fission, agency, intention, or
  biological behavior.
- Do not use external source/sink terms.
- Defer Appendix A multi-pole basin-loop surfaces until the two-aspect L4
  result is stable and reproducible.
- Every positive claim must be reconstructable from outputs, reports, and run
  manifests.
- If an observation cannot be reconstructed, mark it blocked or inconclusive.
- Preserve null controls, reversed source/sink controls, and zero-sum
  perturbation controls.
- Preserve README controls:
  shuffled conductance,
  zero-flux reset,
  budget-projection-disabled diagnostic dry run,
  randomized labels post-hoc,
  and topology disabled.
- Treat source/sink masks as candidate regions. Source-like and sink-like
  roles must be measured from net flux before they can support a claim.
- Do not infer experiment source/sink roles from `GRC9V3State.sink_set` unless
  a run explicitly declares that evidence mode.
- Compute region export/import from edge-level `PortEdge.flux_uv` orientation
  evidence, not from node summaries alone.
- Record measurement phases, budget correction magnitude, and runner
  provenance in every report.
- Record raw or referenced time series for every classifier result.
- Preserve expanded generated evidence during active experiment work. Do not
  delete or collapse outputs until the final packaging task validates a bundle
  and manifest.
- Record deterministic metric configuration, including `n_cycles_min`, in
  every report.
- Separate path closure from measured flux closure and repeated cycle closure.
- Treat pairwise phase-lock as a submetric. L4 needs ordered phase-cascade
  evidence unless explicitly blocked.
- Use washout windows so a K-lane injected kick is not counted as a loop.
- Record fixed-topology evidence in every report.

## Directory Contract

- `../configs/`: run configs, fixture manifests, masks, and lane parameters.
- `../scripts/`: experiment-local runners and report builders.
- `../outputs/`: generated machine-readable artifacts.
- `../reports/`: human-readable reports and blocked-observation notes.
- `./`: implementation plan, checklist, and local trace notes.

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

## Iteration 0. Scope And Replay Contract

Status: complete.

### Goal

Create the experiment-local implementation plan and checklist, using the
existing `implementation/` directory rather than adding a new `specs/` area.

### Checks

- [x] Add `PolarizedBasinLoopsImplementationPlan.md`.
- [x] Add `PolarizedBasinLoopsImplementationChecklist.md`.
- [x] Record that this experiment is fixed-topology first.
- [x] Record that external source/sink terms are out of scope.
- [x] Record that topology adaptation and movement claims are out of scope.
- [x] Record that `src/*` changes are a stop condition requiring separate
      approval.
- [x] Record required evidence surfaces.
- [x] Record report schema target:
      `grc9v3_polarized_basin_loop_report_v1`.
- [x] Record candidate-region versus measured-role rule.
- [x] Record same-parent-basin evidence modes.
- [x] Record closure gate separation:
      path closure, flux closure, cycle closure.
- [x] Record phase-lock and washout requirements.
- [x] Record fixed-topology audit fields.
- [x] Record null tiers and source/sink reversal outcomes.
- [x] Record deterministic claim-ceiling downgrades.
- [x] Record first implementation iterations.

### Implementation Notes

- The imported paper already defines the experiment theory and report schema
  direction.
- The plan turns that paper into a bounded executable program with replayable
  iteration records.
- The local `implementation/` directory is the correct place for this track;
  no separate `specs/` directory is needed.

### Verification

- [x] Plan file exists.
- [x] Checklist file exists.
- [x] Plan/checklist live under the experiment-local implementation directory.
- [x] Plan/checklist record the core-library stop rule.

### Summary

Iteration 0 is complete. The experiment now has a local implementation plan and
replay checklist.

## Iteration 0-A. Runtime Execution Surface Tightening

Status: complete.

### Goal

Tighten the plan against the actual `GRC9V3` implementation so a
fixed-topology experiment cannot accidentally execute topology-changing runtime
phases.

### Checks

- [x] Record `runner_mode = "fixed_topology_continuity_runner"` as the default
      first execution surface.
- [x] Record allowed fixed-topology runtime calls:
      `rebuild_differential_state`,
      `rebuild_transport_state`,
      `apply_continuity`,
      `enforce_quadrature_budget`,
      `rebuild_identity_state`,
      `compute_observables`.
- [x] Record disallowed first-pass topology-changing surfaces:
      `apply_hybrid_sparks`,
      `apply_growth`,
      `apply_boundary_behavior`,
      mechanical expansion,
      node birth,
      node pruning.
- [x] Add full-step escape-hatch requirements:
      topology-changing features disabled or no-op,
      per-step topology audit,
      empty topology event logs,
      budget correction magnitude reported.
- [x] Record that source/sink aspect masks are not runtime `sink_set` labels.
- [x] Record `PortEdge.flux_uv` orientation convention for export/import
      evidence.
- [x] Record measurement phase ordering:
      `C_pre`,
      transport/flux,
      continuity delta,
      `C_post_continuity`,
      budget correction,
      `C_post_budget`,
      diagnostics.
- [x] Record mass-change consistency gates before budget correction.
- [x] Extend report schema with runtime provenance, topology event counts,
      budget correction fields, and edge-level evidence fields.

### Implementation Notes

- This iteration does not implement a runner. It updates the plan/checklist so
  Iteration 1 inventories actual implementation surfaces before code is added.
- The main risk closed here is treating full `GRC9V3.step()` as equivalent to a
  fixed-topology continuity pass.

### Verification

- [x] Plan documents execution-surface contract.
- [x] Checklist ground rules include implementation-backed constraints.

### Summary

Iteration 0-A is complete. The experiment now distinguishes theoretical fixed
topology from the concrete runtime surface that must enforce or prove it.

## Iteration 0-B. Review-Facing Controls And Artifact Contract

Status: complete.

### Goal

Align the implementation plan/checklist with the README controls, time-series
evidence requirements, phase-cascade signal, deterministic thresholds, and
README tranche naming.

### Checks

- [x] Add explicit control matrix:
      `uniform_ring`,
      `symmetric_bump`,
      `symmetric_closed_substrate`,
      `reversed_source_sink`,
      `shuffled_conductance`,
      `zero_flux_reset`,
      `budget_projection_disabled_dry_run`,
      `randomized_labels_posthoc`,
      `topology_disabled`.
- [x] Record shuffled-conductance surface choices:
      `initial_fixture_base_conductance`,
      `per_tick_rebuilt_base_conductance`,
      `channel_mask_assignment`,
      `posthoc_flux_series_assignment`.
- [x] Record that budget-projection-disabled dry runs are diagnostic only and
      cannot support positive conservation claims.
- [x] Add time-series artifact contract with paths/digests.
- [x] Add `simplex_projection_count`, correction counts, and correction
      magnitudes to the report schema.
- [x] Add explicit `topology_events_enabled` runtime/config flag.
- [x] Add `n_cycles_min = 3` as the first deterministic L4 default.
- [x] Record metric configuration block for all threshold values.
- [x] Add ordered phase-cascade evidence:
      `C_source` drop,
      `J_forward` rise,
      `C_sink` rise,
      `J_return` rise,
      `C_source` refill.
- [x] Add runner-step mapping from README sequence to actual runtime phases.
- [x] Record canonical fixture choice:
      `grc9v3_ported_ring_v1`,
      with `simple_unported_ring_v1` as an analysis/control fixture.
- [x] Cross-reference README `L1.0`-`L1.8` tranche names from the plan
      iterations.

### Implementation Notes

- This iteration is documentation and contract alignment only.
- The new controls should not all block initial smoke runs, but no strong L4
  claim should be promoted without the required controls or explicit blocked
  statuses.

### Verification

- [x] Plan includes review-facing controls.
- [x] Plan includes raw/referenced time-series contract.
- [x] Plan includes phase-cascade fields.
- [x] Plan includes deterministic metric configuration.

### Summary

Iteration 0-B is complete. The implementation docs now preserve the README's
review controls and evidence surfaces before runner implementation begins.

## Iteration 1. Artifact Surface Inventory

Status: complete.

### Goal

Map the loop paper's required observables to available runtime artifacts,
checkpoint fields, event logs, or experiment-local derived values.

### Checks

- [x] Inventory node coherence history sources.
- [x] Inventory edge flux/conductance history sources:
      `flux_uv`,
      `base_conductance`,
      `flux_coupling`,
      `geometric_length`,
      `temporal_delay`.
- [x] Inventory edge endpoint and port-orientation sources:
      `edge.u`,
      `edge.v`,
      `u_port`,
      `v_port`.
- [x] Inventory basin/sink/parent-basin evidence sources.
- [x] Record whether `GRC9V3State.sink_set` / `basins` are used as identity
      evidence, and confirm they are not used as source/sink aspect labels.
- [x] Decide first `same_parent_basin_mode`:
      `flux_successor_basin`,
      `configured_parent_region_only`,
      or `unavailable_blocked`.
- [x] Inventory budget audit sources.
- [x] Inventory budget correction method and correction magnitude sources.
- [x] Inventory fixed-topology audit sources.
- [x] Inventory topology-event audit sources:
      mechanical expansion,
      growth,
      pruning,
      boundary birth,
      spark events.
- [x] Inventory explicit topology config flags:
      `topology_events_enabled`,
      spark enabled,
      growth enabled,
      boundary behavior enabled,
      pruning enabled,
      birth enabled.
- [x] Inventory net region export/import evidence sources.
- [x] Inventory time-series artifact storage options:
      JSONL,
      CSV,
      NPZ,
      canonical JSON.
- [x] Inventory digest/hash mechanism for time-series artifacts.
- [x] Decide whether the first runner uses:
      `fixed_topology_continuity_runner`,
      `full_step_runner`,
      `LGRC9V3`,
      or another experiment-local fixed-topology harness.
- [x] If `full_step_runner` is selected, record how topology-changing phases
      are disabled or proven no-op at every step.
- [x] Record runner measurement phases used for evidence:
      `C_pre`,
      transport/flux,
      continuity delta,
      `C_post_continuity`,
      budget correction,
      `C_post_budget`,
      diagnostics.
- [x] Map README runner sequence to concrete runtime methods or blocked
      surfaces.
- [x] Record whether the first serious GRC9V3 fixture is
      `grc9v3_ported_ring_v1`.
- [x] Record whether `simple_unported_ring_v1` is used only for analysis or
      synthetic control checks.
- [x] Inventory feasibility for README controls:
      shuffled conductance,
      zero-flux reset,
      budget-projection-disabled dry run,
      randomized labels post-hoc.
- [x] Record which observables are available, derived, partial, or blocked.
- [x] Produce `../reports/artifact_surface_inventory.md`.
- [x] Produce `../outputs/artifact_surface_inventory.json`.

### Verification

- [x] Every required observable has a source or blocked status.
- [x] No inventory item requires changing `src/pygrc`.
- [x] No `src/*` files changed.
- [x] If a required surface appears to need `src/*`, the experiment is paused
      and a separate core-library task is requested.
- [x] Inventory distinguishes source/sink aspect masks from runtime
      `sink_set` / basin evidence.
- [x] Inventory identifies the concrete flux orientation convention used for
      export/import.
- [x] Inventory identifies where raw time-series evidence will be stored and
      how report digests reference it.

### Summary

Iteration 1 is complete. The selected first execution surface is
`fixed_topology_continuity_runner` over existing `GRC9V3` state/model APIs.
Full `GRC9V3.step()` remains blocked by default because it includes spark,
growth, boundary, and semantic stages beyond the fixed-topology loop scope.
The first parent-basin evidence mode is `configured_parent_region_only`;
stronger `flux_successor_basin` evidence remains partial until fixtures and
runner path evidence exist. The inventory artifacts are:

```text
../reports/artifact_surface_inventory.md
../outputs/artifact_surface_inventory.json
```

The JSON inventory was validated with `python -m json.tool`. No `src/*` files
were changed.

## Iteration 2. Fixed-Topology Fixture Design

Status: complete.

### Goal

Define the first fixed-topology fixtures, masks, and initialization lanes.

### Checks

- [x] Add ring/chain fixture manifest under `../configs/`.
- [x] Add canonical GRC9V3 fixture id:
      `grc9v3_ported_ring_v1`.
- [x] Add analysis/control fixture id, if used:
      `simple_unported_ring_v1`.
- [x] Define source-aspect candidate mask.
- [x] Define sink-aspect candidate mask.
- [x] Define forward-channel edge/path mask.
- [x] Define return-channel edge/path mask.
- [x] Define U lane: uniform/null.
- [x] Define U0 null: uniform field.
- [x] Define U1 null: symmetric bump.
- [x] Define U2 null: symmetric closed substrate/masks.
- [x] Define S lane: structured initialization.
- [x] Define K lane: one-time zero-sum kick.
- [x] Add reversed source/sink control configuration.
- [x] Add budget-conserving projection or normalization rule.
- [x] Add canonical ring initialization:
      `C_i = C_0 + A exp(kappa cos(theta_i - theta_0))`.
- [x] Add small local source/sink modulation masks:
      `C_i <- C_i + epsilon_s m_s(i) - epsilon_k m_k(i)`.
- [x] Add nonnegative conserved projection:
      `C_i >= 0`, `sum_i C_i = B`.
- [x] Add K-lane `washout_steps` and `min_eval_steps`.
- [x] Add metric config defaults:
      `n_cycles_min = 3`,
      `washout_steps`,
      `min_eval_steps`,
      `theta_export`,
      `theta_import`,
      `theta_mass`,
      `theta_null_margin`,
      `phase_lock_min`,
      `phase_cascade_score_min`.
- [x] Add control configs for:
      shuffled conductance,
      zero-flux reset,
      budget-projection-disabled dry run,
      randomized labels post-hoc.

### Verification

- [x] Fixture manifest is deterministic and JSON-serializable.
- [x] All masks reference valid node/edge ids.
- [x] Initial conditions preserve nonnegative coherence and total budget.
- [x] No `src/*` files changed.
- [x] If fixture construction exposes a missing core API, the experiment is
      paused rather than patching `src/*`.

### Summary

Iteration 2 is complete. Added the deterministic fixture and lane manifest:

```text
../configs/fixture_manifest_v1.json
```

The canonical fixture is `grc9v3_ported_ring_v1`, a 12-node ring using row-2
ports `6` and `4` as the clockwise boundary pair. The analysis/control fixture
is `simple_unported_ring_v1`. The manifest defines source/sink aspect masks,
forward/return channels, U/U0/U1/U2/S/K lanes, reversed controls, metric
defaults, budget projection rules, and README control configs.

Validation:

```text
python -m json.tool experiments/2026-05-N03-grc9v3-polarized-basin-loops/configs/fixture_manifest_v1.json
python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/validate_fixture_manifest.py
python -m json.tool experiments/2026-05-N03-grc9v3-polarized-basin-loops/outputs/fixture_manifest_validation.json
git diff -- src
```

Observed validator output:

```text
{"status": "pass", "errors": []}
```

`git diff -- src` produced no output.

The manifest is valid JSON, all masks reference live node/edge ids, and no
`src/*` files were changed.

Post-review validation artifacts:

```text
../scripts/validate_fixture_manifest.py
../reports/fixture_manifest_validation.md
../outputs/fixture_manifest_validation.json
```

Additional checks passed for port orientation, active degree, mask
disjointness, forward/return route consistency, reversed-control coherence,
metric defaults, control config presence, and synthetic `flux_uv=+1`
orientation behavior. No `src/*` files were changed.

Post-review manifest tightening also records:

- `two_equal_canonical_ring_bumps` as a resolvable initialization formula;
- `canonical_ring_bump_plus_small_local_source_sink_modulation` as an explicit
  S-lane composition:
  bump -> modulation -> one conserved projection;
- K lane as `base_lane = U2`, `initialization = uniform`, followed by
  `zero_sum_kick` at `kick_step`;
- `runner_config.dt = 0.01` and `runner_config.total_steps = 140`;
- default edge properties for `flux_coupling_initial` and
  `temporal_delay_initial`;
- `simple_unported_ring_v1.reversed_masks_available = false` with a note that
  reversal controls should use the canonical ported ring unless added there;
- a pre-run hypothesis record under
  `../hypotheses/polarized_basin_loop_hypothesis_v1.md`;
- `pruning_enabled = false` in scope and topology-disabled controls;
- return flux as positive clockwise channel flux, not counterclockwise flux;
- `J_forward` / `J_return` as channel sums, distinct from source/sink boundary
  export/import;
- edge field aliases for `u/v` versus `node_u/node_v`;
- zero-sum modulation/kick projection-audit expectations;
- uniform-conductance shuffled-control caveat.

The replayable validator enforces these fields and reports:

```text
{"status": "pass", "errors": []}
```

## Iteration 3. Loop Observable Library

Status: complete.

### Goal

Implement experiment-local observable computation without changing runtime
behavior.

### Checks

- [x] Compute source-aspect mass history.
- [x] Compute sink-aspect mass history.
- [x] Compute source-region net export:
      `export(R, t) = sum_{i in R, j not in R} J_ij(t)`,
      reconstructed from boundary-edge `flux_uv` orientation.
- [x] Compute sink-region net import:
      `import(R, t) = -export(R, t)`.
- [x] Classify source/sink roles from measured export/import means.
- [x] Classify source/sink roles with pre-budget mass-change consistency:
      source export with negative source `Delta C`,
      sink import with positive sink `Delta C`.
- [x] Report post-budget mass changes separately from pre-budget role
      consistency.
- [x] Compute forward flux summary.
- [x] Compute return flux summary.
- [x] Compute path-closure evidence from masks.
- [x] Compute flux-closure evidence from measured return flux.
- [x] Compute polarity score.
- [x] Compute closure score.
- [x] Compute phase-lock / phase relation metric.
- [x] Serialize the phase-lock formula used by the runner.
- [x] Compute ordered phase-cascade evidence:
      source drop -> forward flux -> sink rise -> return flux -> source refill.
- [x] Serialize phase-cascade formula and thresholds used by the runner.
- [x] Compute cycle count.
- [x] Require cycle count to satisfy configured `n_cycles_min` for L4.
- [x] Compute budget audit.
- [x] Compute budget correction audit:
      before continuity,
      after continuity,
      pre-correction error,
      after correction,
      post-correction error,
      correction method,
      correction magnitude.
- [x] Count budget correction applications:
      `simplex_projection_count`,
      `uniform_shift_count`.
- [x] Emit or reference raw time series:
      `C_source`,
      `C_sink`,
      `J_forward`,
      `J_return`,
      `source_export`,
      `sink_import`,
      pre-budget deltas,
      loop scores,
      budget errors.
- [x] Compute topology audit:
      initial/final node count,
      initial/final edge count,
      changed,
      passed fixed-topology gate,
      topology event count,
      blocked topology event kinds.
- [x] Emit runtime provenance:
      model family,
      runner mode,
      called methods,
      disabled/enabled spark/growth/boundary/birth flags,
      runtime semantics changed flag.
- [x] Emit controls status block.
- [x] Emit schema-compatible run report objects.

### Verification

- [x] Unit or smoke checks cover null, structured, and kick-shaped synthetic
      traces.
- [x] Budget audit fails clearly on budget drift.
- [x] Report object contains all required schema fields.
- [x] No `src/*` files changed.
- [x] Missing observable/library capability is recorded as blocked or raised as
      a separate approved core task.

### Summary

Iteration 3 complete.

Added an experiment-local observable library and replayable smoke validator:

- `../scripts/loop_observables.py`;
- `../scripts/validate_loop_observables.py`;
- `../outputs/loop_observables_smoke_report.json`;
- `../outputs/loop_observables_timeseries/*.jsonl`;
- `../reports/loop_observables_smoke_report.md`.

Replay command:

```bash
python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/validate_loop_observables.py
```

Result:

```json
{"errors": [], "status": "pass"}
```

Smoke coverage:

- `U0_synthetic`: budget passes, no measured source/sink role, no cycles;
- `S_synthetic`: budget passes, measured source/sink roles, three ordered
  phase cascades, L4 cycle gate satisfied;
- `K_synthetic`: budget passes, measured source/sink roles, three ordered
  phase cascades, L4 cycle gate satisfied;
- `partial_cascade_synthetic`: source/sink role shape present, but no return
  / refill closure; cascade count `0`, L4 cycle gate false;
- `phase_scrambled_synthetic`: matching amplitudes with wrong event order;
  cascade count `0`, L4 cycle gate false;
- `budget_drift_synthetic`: budget audit fails clearly.
- `budget_drift_with_cascade_synthetic`: cascade shape present but budget gate
  false, so positive claim remains blocked.

The observable library reconstructs source export and sink import from
edge-level `flux_uv` orientation, keeps `J_forward`/`J_return` separate from
region boundary export/import, serializes raw time-series artifacts with
digests, records phase-lock and ordered cascade formulas, emits topology and
runtime provenance blocks, and reports controls status.

Preflight hardening records:

- synthetic reports use `runner_mode = synthetic_trace_validator` and never
  promote runtime loop claims;
- report schema is aligned to
  `grc9v3_polarized_basin_loop_report_v1`;
- `ladder` and `blocked_claims` are emitted alongside `claim_gate` and
  `claim_ceiling` until Iteration 6 freezes the fail-closed negative/blocked
  report shape;
- `blocked_reasons` is a list, and `primary_scientific_blocker` exposes
  scientific blockers such as `budget_gate_failed` even when the synthetic
  runner gate also blocks claims;
- `claim_ceiling.fixture_allows_candidate_claims` separates fixture-level claim
  ceiling from `claim_gate.positive_candidate_loop_claim_allowed`;
- `roles.reversal_outcome = not_run_iteration_3` is emitted until reversal
  controls run in Iteration 5;
- `phase_lock_max_lag` and `phase_cascade_max_stage_lag` are manifest metric
  defaults, not hidden constants;
- phase-lock serialization includes lag window, sign convention, smoothing
  rule, and evaluation-window fields;
- phase-cascade serialization includes event detection rules, stage lag,
  thresholds, sign convention, and `n_cycles_min`;
- boundary export/import and channel flux are kept as separate fields;
- deterministic reruns produced stable time-series digests, including:
  `ca62df87cfcf6441acbe7be50e40229adcbe9f1ce8d09a37cf94b82a1e4f4096`
  for the positive synthetic S/K trace;
- the smoke JSON report digest after hardening is
  `e0b7bcbd797bae30caa25af1ef5c8c58f91b9adaafa90065541731d3402eb175`.

Note: `S_synthetic` and `K_synthetic` intentionally share the same synthetic
positive trace in Iteration 3. This validates the observable library only; real
S/K initialization differences begin in Iterations 4 and 5.

No `src/*` files were changed. The current implementation remains
experiment-local and synthetic-trace only; real U/S/K runner execution begins
in Iterations 4 and 5.

## Iteration 4. Null And Structured Lanes

Status: complete.

### Goal

Run U and S lanes and verify that null separation can be measured.

### Checks

- [x] Add U-lane runner.
- [x] Add S-lane runner.
- [x] Run uniform/null control.
- [x] Run U0 uniform null.
- [x] Run symmetric structured control.
- [x] Run U1 symmetric bump null.
- [x] Run U2 symmetric closed-substrate/mask null.
- [x] Run source/sink structured lane.
- [x] Run randomized-label post-hoc classifier check or mark blocked.
- [x] Run zero-flux reset control where inherited transport state exists, or
      mark not applicable for fresh rebuild-only lanes.
- [x] Compare polarity, closure, and phase-lock against nulls.
- [x] Compare phase-cascade score against nulls.
- [x] Record blocked observations.

### Verification

- [x] Machine-readable outputs written under `../outputs/`.
- [x] Human-readable reports written under `../reports/`.
- [x] Null lanes do not produce false L4 positives.
- [x] No `src/*` files changed.

### Summary

Iteration 4 complete.

Added a real GRC9V3 fixed-topology runner:

- `../scripts/run_null_structured_lanes.py`;
- `../outputs/null_structured_lanes_report.json`;
- `../outputs/null_structured_raw_records/*.jsonl`;
- `../outputs/null_structured_timeseries/*.jsonl`;
- `../reports/null_structured_lanes_report.md`.

Replay command:

```bash
.venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/run_null_structured_lanes.py
```

Validation commands:

```bash
.venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/validate_fixture_manifest.py
.venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/validate_loop_observables.py
.venv/bin/python -m py_compile experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/loop_observables.py experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/validate_loop_observables.py experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/run_null_structured_lanes.py
git status --short src
```

Result:

```json
{"errors": [], "status": "pass"}
```

Runtime boundary:

- uses real `GRC9V3` construction and methods;
- does not call `step()`;
- calls only fixed-topology continuity phases:
  `rebuild_differential_state`, `rebuild_transport_state`,
  `apply_continuity`, `enforce_quadrature_budget`,
  `rebuild_identity_state`, and experiment-local observables;
- does not call spark expansion, growth, boundary behavior, birth, or pruning.

Lane results:

| Lane | Budget | Source role | Sink role | Cascades | Claim allowed |
| --- | --- | --- | --- | ---: | --- |
| `U0` | pass | false | false | 0 | false |
| `U1` | pass | true | false | 21 raw / 0 role-gated | false |
| `U2` | pass | false | false | 0 | false |
| `S` | pass | false | false | 0 | false |

Blocked observations:

- `U1` produced shape-only phase-cascade evidence under a symmetric null, but
  measured source/sink role evidence failed, so no candidate loop claim was
  allowed. This is recorded as
  `null_lane_shape_cascade_without_role_gate`. The report now distinguishes
  raw cascades from role-gated cascades; U1 has `21` raw cascades and `0`
  role-gated cascades.
- `S` did not produce candidate loop evidence above the null controls. This is
  recorded as `structured_lane_no_candidate_loop_claim`.

Iteration 4 diagnostics:

- budget correction magnitudes were negligible:
  U0 `0.0`, U1 `4.44e-16`, U2 `0.0`, S `5.55e-16`;
- U1 initial source/sink coherence and potential means are symmetric, so its
  raw cascade count is a null shape-dynamics artifact rather than configured
  role polarity;
- S initial diagnostics show the structured modulation is visible to the
  runtime (`source_C_mean > sink_C_mean`), but the rebuilt transport surface is
  forward/return asymmetric in the wrong direction for a loop claim:
  forward flux mean `0.0450`, return flux mean `-0.0522`, source/sink role gate
  false.

This is a conservative null/structured-lane result, not positive loop evidence.
The first structured fixed-topology lane did not validate the hypothesis. It
did validate the runtime bridge: real GRC9V3 traces can be captured and scored
through the Iteration 3 observable library without changing `src/*`.

## Iteration 5. One-Time Kick Lane

Status: complete.

### Goal

Run K lanes with budget-preserving perturbations and reversed controls.

### Checks

- [x] Add zero-sum kick API or experiment-local perturbation helper.
- [x] Run forward kick.
- [x] Run reversed kick.
- [x] Run shuffled-conductance control or mark blocked with surface reason.
- [x] Run budget-projection-disabled diagnostic dry run or mark blocked.
- [x] Confirm perturbation preserves total budget.
- [x] Enforce `eval_window_start = kick_step + washout_steps`.
- [x] Count cycles only inside the post-washout evaluation window.
- [x] Compare loop metrics between directions.
- [x] Classify reversal outcome:
      `antisymmetric_pass`,
      `substrate_biased_pass`,
      or `failure`.
- [x] Record whether the loop persists after the kick.

### Verification

- [x] Budget conservation passes.
- [x] Reversed direction behaves consistently or is reported as asymmetry.
- [x] No external source/sink term is introduced.
- [x] No `src/*` files changed.

### Summary

Iteration 5 complete.

Added a real GRC9V3 one-time kick runner:

- `../scripts/run_kick_lanes.py`;
- `../outputs/kick_lanes_report.json`;
- `../outputs/kick_raw_records/*.jsonl`;
- `../outputs/kick_timeseries/*.jsonl`;
- `../reports/kick_lanes_report.md`.

Replay command:

```bash
.venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/run_kick_lanes.py
```

Validation commands:

```bash
.venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/validate_fixture_manifest.py
.venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/validate_loop_observables.py
.venv/bin/python -m py_compile experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/loop_observables.py experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/validate_loop_observables.py experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/run_null_structured_lanes.py experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/run_kick_lanes.py
git status --short src
```

Result:

```json
{"errors": [], "status": "pass"}
```

Runtime boundary:

- uses real `GRC9V3` construction and fixed-topology continuity methods;
- applies one experiment-local zero-sum kick before the first transport rebuild;
- does not call `step()`, spark expansion, growth, boundary behavior, birth, or
  pruning;
- does not add external source/sink terms.

Kick audit:

- `K`: source nodes `[0, 1]`, sink nodes `[6, 7]`, `kick_delta = 0.02`;
- `K_reversed`: source nodes `[6, 7]`, sink nodes `[0, 1]`,
  `kick_delta = 0.02`;
- both kicks are zero-sum before projection;
- both preserve budget after projection;
- projection L1 delta is `0.0`.

Lane results:

| Lane | Budget | Source role | Sink role | Raw cascades | Role-gated cascades | Claim allowed |
| --- | --- | --- | --- | ---: | ---: | --- |
| `K` | pass | false | false | 0 | 0 | false |
| `K_reversed` | pass | false | false | 0 | 0 | false |

Reversal outcome:

```text
failure
```

Reason:

```text
neither kick direction produced paired role-gated loop evidence
```

Blocked controls:

- shuffled conductance is blocked/non-informative for the current uniform
  conductance surface;
- budget-projection-disabled dry run is blocked until a separate approved
  diagnostic runner exists.

This is another conservative negative result for the loop hypothesis. A
one-time zero-sum kick did not induce measured paired source/sink polarity,
return closure, or role-gated cascades on the first fixed-topology ported-ring
fixture.

## Iteration 6. Fail-Closed Classifier And Negative Tranche Closeout

Status: complete.

### Goal

Freeze the report schema and classifier behavior for negative, blocked, and
candidate outcomes. Do not promote L4 claims from this first canonical
fixed-topology fixture.

### Checks

- [x] Record first tranche classification:
      `negative_fixed_topology_first_tranche`.
- [x] Record first tranche result:
      no polarized basin loop observed on the first 12-node fixed-topology
      ported-ring fixture under S/K lanes.
- [x] Preserve L0 no-loop classification.
- [x] Preserve L1/L2/L3/L4 shape classification as report evidence only.
- [x] Keep positive claim promotion blocked unless all gates pass.
- [x] Require conservation gate for any positive/candidate claim.
- [x] Require single-parent-basin gate for full positive claims.
- [x] Require measured source/sink roles for polarity claims.
- [x] Require flux-closure evidence for loop claims.
- [x] Require cycle count for L4-shaped evidence.
- [x] Require `n_cycles_min` for L4-shaped evidence.
- [x] Require ordered phase-cascade evidence for L4-shaped evidence, or
      downgrade/block if unavailable.
- [x] Require role-gated cascades for candidate loop claims.
- [x] Keep raw cascade counts separate from role-gated cascade counts.
- [x] Require null separation before any future L4 promotion.
- [x] Require randomized-label post-hoc sanity check before any future strong
      L4 claim.
- [x] Apply deterministic claim-ceiling downgrades:
      no budget audit -> blocked;
      no source/sink role measurement -> no polarity claim;
      no return-channel measurement -> no loop claim;
      no cycle count -> at most L3-shaped evidence;
      no `n_cycles_min` -> blocked for L4-shaped evidence;
      no phase-cascade evidence -> at most L3/candidate L4-shaped evidence;
      no null separation -> candidate only;
      no same-parent-basin evidence -> candidate loop only;
      no fixed-topology audit -> blocked.
- [x] Serialize gates passed/failed in every report.
- [x] Serialize blocked claims and primary scientific blocker.
- [x] State explicitly that S/K failure is a valid negative result, not an
      implementation failure.
- [x] State explicitly that no classifier/threshold tuning was performed to
      rescue the first tranche.
- [x] Record validated surfaces:
      fixed-topology runtime bridge,
      observable library on real traces,
      budget/topology/provenance reporting,
      null rejection,
      role-gated blocking of shape-only cascades.
- [x] Record non-validated surfaces:
      L4 conserved internal loop,
      L5 self-regulating pulse generator,
      L6 boundary-couplable loop,
      movement/locomotion precursor evidence.

### Diagnostic Branch Notes

- [x] Add Branch B diagnostic sweep placeholders:
      amplitude,
      mask width,
      ring size,
      conductance asymmetry,
      source/sink spacing,
      forward/return asymmetry,
      budget correction magnitude,
      transport rebuild behavior.
- [x] Mark Branch B claim ceiling as diagnostic sensitivity map, not positive
      loop claim.
- [x] Add Branch C fixture/theory redesign placeholder.
- [x] Keep L5/L6 unopened because L4 was not established.
- [x] Keep Appendix A multi-pole surfaces deferred.

### Verification

- [x] Classifier/report behavior is deterministic on repeated runs.
- [x] Budget-violating traces remain blocked.
- [x] Topology-changing traces remain rejected for this experiment.
- [x] First tranche closeout report links to U/S/K outputs.
- [x] No `src/*` files changed.

### Summary

Iteration 6 complete.

Added a deterministic negative-tranche closeout:

- `../scripts/close_negative_tranche.py`;
- `../outputs/negative_tranche_closeout.json`;
- `../reports/negative_tranche_closeout.md`.

Replay command:

```bash
.venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/close_negative_tranche.py
```

Result:

```json
{"errors": [], "status": "pass"}
```

Classification:

```text
negative_fixed_topology_first_tranche
```

Conclusion:

```text
No polarized basin loop was observed on the first 12-node fixed-topology
GRC9V3 ported-ring fixture under S/K lanes.
```

Closeout digest:

```text
e5a051b7b37e762141333ee954e79116c841064f0ab87a002c56ab5240e41be3
```

The closeout validates that:

- all input reports are passing;
- budget-drift synthetic traces remain blocked;
- runtime U/S/K lanes do not promote candidate claims;
- topology remained fixed;
- U1's raw shape cascade remains blocked by role-gated evidence;
- no positive claim was promoted;
- no classifier or threshold tuning was performed to rescue the first tranche.

Future state:

- Branch B diagnostic sweeps are recorded but unopened, with claim ceiling
  `diagnostic_sensitivity_map_not_positive_loop_claim`;
- Branch C fixture/theory redesign is recorded but unopened;
- L5, L6, multi-pole Appendix A, and movement-ladders handoff remain blocked
  or deferred because L4 was not established.

Retrospective note:

- This was the correct state at the close of Iteration 6. Later packetized
  branches reopened the loop question on a different execution surface. D2.3
  established an experiment-local L5-like self-rearming packet pulse candidate,
  and E3 later reproduced that mechanism natively in LGRC9V3. This does not
  change the negative result for native fixed-topology GRC9V3 proposal flux.

## Iteration 7. Reports And Handoff

Status: pending.

### Goal

Close the first implementation pass with readable reports and clear claim
ceilings.

### Checks

- [ ] Produce family summary report.
- [ ] Produce blocked-observations report.
- [ ] Produce report schema notes.
- [ ] Record first tranche negative result.
- [ ] Record which lanes reached L0-L4-shaped evidence.
- [ ] Record whether L5/L6 should be opened later.
- [ ] Record relationship to movement-ladders experiment.

### Verification

- [ ] Reports link to generated outputs.
- [ ] Claims stay inside loop/polarity scope.
- [ ] Movement claims remain blocked.
- [ ] No repo-level runtime changes were made for the experiment.
- [ ] No `src/*` files changed.

### Summary

Pending.

## Branch B. Diagnostic Sweeps

Status: closed for current plain two-pole ring line.

Open only as a new diagnostic branch. Do not treat sweeps as a continuation of
the first positive claim path.

### Branch Claim Ceiling

```text
diagnostic sensitivity map, not positive loop claim
```

Branch B may identify promising conditions, but it must not promote loop
success directly. Any apparently positive diagnostic row must be promoted into
a new named fixture/tranche with fresh nulls and controls.

### Branch B Closeout

Status: complete.

Conclusion:

```text
No tested amplitude, mask, scale, spacing, attenuation, or fixed
conductance-corridor diagnostic produced role-gated cascades.
```

Evidence:

```text
B1:
    rows = 26
    promising diagnostic rows = 0
    max role-gated cascades = 0

B2:
    rows = 10
    static S export attenuates/redistributes across intermediate nodes before
    paired sink-role evidence forms.

B3:
    rows = 24
    promising diagnostic rows = 0
    max raw cascades = 0
    max role-gated cascades = 0
```

Interpretation:

```text
The first two-aspect homogeneous/plain ported ring behaves like a local
relaxation/redistribution substrate, not a directed conserved loop substrate
under the current fixed-topology continuity dynamics.
```

Next action:

```text
Open Branch C fixture/theory redesign.
```

### B1. Amplitude/Mask/Scale/Spacing Diagnostics

Status: complete.

Ground rules:

- [x] No positive loop claim allowed.
- [x] No classifier/threshold tuning.
- [x] No `src/*` changes.
- [x] Record every row as diagnostic only.
- [x] Preserve current fail-closed gates.

Implementation:

- [x] Add replayable B1 diagnostic sweep script:
      `scripts/run_b1_diagnostic_sweeps.py`.
- [x] Generate in-memory fixture variants without modifying the canonical
      fixture manifest.
- [x] Use real `GRC9V3` fixed-topology continuity execution.
- [x] Apply a diagnostic Branch B claim ceiling after scoring:
      `diagnostic_sensitivity_map_not_positive_loop_claim`.
- [x] Write machine-readable output:
      `outputs/b1_diagnostic_sweeps_report.json`.
- [x] Write human-readable report:
      `reports/b1_diagnostic_sweeps_report.md`.

Command run:

```bash
.venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/run_b1_diagnostic_sweeps.py
```

Result:

```text
status: pass
rows: 26
promising diagnostic rows: 0
max raw cascades: 13
max role-gated cascades: 0
positive loop claims allowed: false
topology changed: false
budget failures: 0
interpretation:
    no_role_gated_cascades_detected_fixture_mechanism_mismatch_likely
```

#### B1.1 Amplitude Sweep

- [x] Sweep S modulation:
      `0.005`, `0.01`, `0.02`, `0.04`.
- [x] Sweep K kick:
      `0.005`, `0.01`, `0.02`, `0.04`.
- [x] Record source/sink role gates.
- [x] Record raw cascade counts.
- [x] Record role-gated cascade counts.
- [x] Record forward/return flux signs.
- [x] Record budget correction magnitude.
- [x] Record topology audit.
- [x] Record transport erase/preserve metrics.

#### B1.2 Mask Width Sweep

- [x] Sweep source/sink aspect width:
      `1`, `2`, `3` nodes.
- [x] Keep diagnostic-only claim ceiling.
- [x] Compare against B1.1 baseline rows.

#### B1.3 Ring Size Sweep

- [x] Sweep ring sizes:
      `12`, `24`, `48` nodes.
- [x] Keep diagnostic-only claim ceiling.
- [x] Compare whether longer rings create phase-delayed role-gated cascades.

#### B1.4 Source/Sink Spacing Sweep

- [x] Test half-ring separation.
- [x] Test third-ring separation.
- [x] Test quarter-ring separation.
- [x] Keep diagnostic-only claim ceiling.

#### B1.5 Transport Rebuild Audit

- [x] Compare initialized source/sink polarity against post-transport rebuild
      conductance surfaces.
- [x] Compare initialized source/sink polarity against post-transport rebuild
      potential surfaces.
- [x] Compare initialized source/sink polarity against post-transport rebuild
      flux surfaces.
- [x] Record whether runtime transport erases or preserves initialized polarity.

B1 outcome:

```text
No sweep produced role-gated cascades.
The diagnostic interpretation is fixture/mechanism mismatch likely.
No positive loop claim was promoted.
```

### B1 Interpretation Rule

```text
If no sweep produces role-gated cascades:
    likely fixture/mechanism mismatch; move to Branch C.

If some sweep produces role-gated cascades:
    do not claim success.
    promote that condition into a new named fixture/tranche with fresh
    U/S/K/null/reversal controls.
```

### Candidate Axes

- [x] S modulation amplitude sweep.
- [x] K kick strength sweep.
- [x] Source/sink mask width sweep.
- [x] Ring size sweep.
- [ ] Conductance asymmetry / channel-structure sweep.
- [x] Source/sink spacing sweep.
- [ ] Forward/return asymmetry sweep.
- [x] Budget correction magnitude audit.
- [x] Transport rebuild behavior audit.

### Claim Ceiling

```text
diagnostic sensitivity map, not positive loop claim
```

Any apparent positive diagnostic result must be promoted into a new named
fixture/tranche with fresh nulls and controls before supporting a loop claim.

### B2. Channel Attenuation / Intermediate-Node Dissipation Audit

Status: complete.

Goal:

```text
Test whether source-region export survives across intermediate channel nodes
as directed flux toward the sink, or whether it is redistributed by the
ordinary fixed-topology continuity substrate before sink-role evidence forms.
```

Ground rules:

- [x] No positive loop claim allowed.
- [x] No classifier/threshold tuning.
- [x] No `src/*` changes.
- [x] Use real `GRC9V3` fixed-topology continuity execution.
- [x] Preserve diagnostic-only claim ceiling.

Implementation:

- [x] Add replayable B2 attenuation script:
      `scripts/run_b2_channel_attenuation.py`.
- [x] Use a 16-node ported ring with two-node source/sink masks.
- [x] Sweep source-to-sink forward gap lengths:
      `0`, `1`, `2`, `4`, `6` intermediate nodes.
- [x] Run S and K lanes for each gap.
- [x] Record first-vs-last forward-edge flux ratios.
- [x] Record sink-import/source-export boundary ratios.
- [x] Record channel mass deviation across intermediate nodes.
- [x] Record topology and budget audits.
- [x] Write machine-readable output:
      `outputs/b2_channel_attenuation_report.json`.
- [x] Write human-readable report:
      `reports/b2_channel_attenuation_report.md`.

Command run:

```bash
.venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/run_b2_channel_attenuation.py
```

Result:

```text
status: pass
rows: 10
positive loop claims allowed: false
topology changed: false
budget failures: 0
```

Observed:

```text
Static S lane:
    gap 4 early last/first forward-edge ratio ~= 0.063
    gap 4 early sink/source boundary ratio ~= 0.046
    gap 6 early last/first forward-edge ratio ~= 0.047
    gap 6 early sink/source boundary ratio ~= 0.049

K lane:
    one-time kick produces broader relaxation and does not show the same early
    last-edge attenuation, but this remains diagnostic only and does not
    support loop evidence.
```

B2 outcome:

```text
B2 supports the concern that intermediate nodes in the plain ring can
attenuate or redistribute static source export before paired sink-role
evidence forms. The plain ring continues to look more like a local relaxation
substrate than a directed loop substrate for the first S initialization.
```

### B3. Fixed-Topology Conductance Corridor Diagnostic

Status: complete.

Goal:

```text
Test whether fixed-topology channel structure alone helps preserve source
export as directed source-to-sink transport under the existing S/K
initialization surfaces.
```

Ground rules:

- [x] No positive loop claim allowed.
- [x] No classifier/threshold tuning.
- [x] No `src/*` changes.
- [x] Use real `GRC9V3` fixed-topology continuity execution.
- [x] Modify only in-memory fixture conductance values.
- [x] Preserve diagnostic-only claim ceiling.

Implementation:

- [x] Add replayable B3 conductance-corridor script:
      `scripts/run_b3_conductance_corridor.py`.
- [x] Sweep forward-channel conductance boosts:
      `1.5`, `2.0`, `4.0`.
- [x] Sweep return-channel conductance boosts:
      `1.5`, `2.0`, `4.0`.
- [x] Sweep balanced forward/return boosts:
      `1.5`, `2.0`, `4.0`.
- [x] Sweep asymmetric corridors:
      forward `4.0` / return `1.5`,
      forward `1.5` / return `4.0`.
- [x] Sweep source-exit/sink-entry boundary gate boost:
      `4.0`.
- [x] Run S and K lanes for each variant.
- [x] Record role gates, raw cascades, role-gated cascades, attenuation ratios,
      budget correction magnitude, and topology audit.
- [x] Write machine-readable output:
      `outputs/b3_conductance_corridor_report.json`.
- [x] Write human-readable report:
      `reports/b3_conductance_corridor_report.md`.

Command run:

```bash
.venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/run_b3_conductance_corridor.py
```

Result:

```text
status: pass
rows: 24
promising diagnostic rows: 0
max raw cascades: 0
max role-gated cascades: 0
positive loop claims allowed: false
topology changed: false
budget failures: 0
interpretation:
    conductance_corridor_did_not_create_role_gated_loop_evidence
```

B3 outcome:

```text
Fixed-topology conductance corridors alone did not produce paired source/sink
roles, raw loop cascades, or role-gated loop evidence under the current S/K
initialization surfaces. The first-tranche failure is therefore not explained
only by uniform channel conductance.
```

## Branch C. Fixture/Theory Redesign

Status: opened, not implemented.

Open only if diagnostic sweeps show that the first two-aspect plain ring is
understructured. This branch requires a new fixture manifest and claim ceiling.

Potential redesign surfaces:

- [ ] larger ring;
- [ ] buffered source/sink masks;
- [ ] persistent channel conductance structure;
- [ ] delayed transport / memory-like channels;
- [ ] three-pole or multi-pole phase cycling.

### C1. Delayed/Accumulator Channel Substrate

Status: complete, first accumulator policy negative for cycles.

Question:

```text
Can a conserved fixed-topology basin sustain source/sink cycling if forward
and return channels include explicit delay/accumulator states, rather than
instantaneous homogeneous ring continuity?
```

Ground rules:

- [x] No external source/sink terms.
- [x] Budget conserved over node coherence plus any explicit accumulator or
      channel storage.
- [x] Fixed topology unless a later branch explicitly opens topology
      adaptation.
- [x] Source/sink roles measured from runtime evidence, not masks.
- [x] Raw cascades remain separate from role-gated cascades.
- [x] Fresh U/S/K/null/reversal controls required.
- [x] No movement claim.
- [x] No `src/*` changes without explicit separate approval.

Implementation:

- [x] Add replayable C1 delayed accumulator runner:
      `scripts/run_c1_delayed_accumulator.py`.
- [x] Add execution surface:
      `c1_delayed_accumulator_runner`.
- [x] Use GRC9V3 differential/transport rebuilds as flux proposal sources.
- [x] Move coherence through experiment-local forward/return delay queues.
- [x] Audit budget as:
      node coherence + forward in-flight queue + return in-flight queue.
- [x] Run U0, U2, S, K, and K-reversed lanes.
- [x] Sweep delay steps:
      `3`, `6`, `10`.
- [x] Write machine-readable output:
      `outputs/c1_delayed_accumulator_report.json`.
- [x] Write human-readable report:
      `reports/c1_delayed_accumulator_report.md`.

Command run:

```bash
.venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/run_c1_delayed_accumulator.py
```

Result:

```text
status: pass
rows: 15
candidate rows: 0
classification: c1_no_candidate_loop_rows_observed
topology changed: false
max nodes+in-flight budget error <= 2.23e-16
full L-positive claims allowed: false
```

Observed:

```text
U0/U2:
    clean null controls; no source/sink roles and no cycles.

S/K/K-reversed:
    paired source/sink roles are measured under delayed accumulator transport.
    raw cascades = 0.
    role-gated cascades = 0.
```

C1 outcome:

```text
Delayed accumulator transport fixes the role-formation failure but does not
yet produce ordered repeated loop cycles. C1 therefore does not support a
candidate loop claim in its first policy. The next redesign question is which
accumulator/release policy can turn paired delayed transport into
phase-ordered cycling, if any.
```

### C1-B. Accumulator Release Policy Diagnostics

Status: complete; C1 closed.

Question:

```text
Given a conserved delayed accumulator substrate that can produce paired
source/sink transport, what release policy produces ordered recurrent cycling
rather than one-shot delayed transfer or monotone relaxation?
```

Claim ceiling:

```text
diagnostic release-policy sensitivity map, not positive loop claim
```

State distinction:

- [x] C1 reached paired delayed transport.
- [x] C1 did not reach phase-ordered cycling.
- [x] Next question is release dynamics, not source/sink existence.

Implementation:

- [x] Add replayable C1-B release-policy runner:
      `scripts/run_c1b_release_policy_diagnostics.py`.
- [x] Add execution surface:
      `c1b_release_policy_runner`.
- [x] Use GRC9V3 differential/transport rebuilds as flux proposal sources.
- [x] Audit budget as:
      node coherence + forward accumulator + return accumulator.
- [x] Preserve diagnostic release-policy claim ceiling.
- [x] Keep `src/*` unchanged.

Command run:

```bash
.venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/run_c1b_release_policy_diagnostics.py
```

Result:

```text
status: pass
rows: 51
promising rows: 0
classification: release_policy_no_role_gated_cycles_observed
max raw cascades: 0
max role-gated cascades: 0
topology changed: false
accumulator budget failures: 0
positive loop claims allowed: false
```

Observed:

```text
Most S/K release-policy rows form paired source/sink roles.
No tested release policy produces raw cascades or role-gated cascades.
U0/U2 controls remain clean under the coupled serious policy.
```

Interpretation:

```text
Release timing alone, when driven by current GRC9V3 flux proposals and local
accumulator state, does not produce recurrent phase-ordered loop cycling.
The missing mechanism is likely not simply delay plus thresholded release.
```

#### C1-B.1 Passive Leaky Accumulator

- [x] Implement passive leak policy:
      `A_next = (1 - leak) A + input`,
      `release = leak * A`.
- [x] Sweep leak:
      `0.05`, `0.1`, `0.2`, `0.4`.
- [x] Treat as smoothing/control surface unless it unexpectedly produces
      role-gated cycles.

#### C1-B.2 Threshold Release

- [x] Implement threshold release:
      release only when `A > theta_release`.
- [x] Sweep `theta_release`.
- [x] Sweep `release_fraction`.

#### C1-B.3 Hysteretic Release

- [x] Implement open/close thresholds:
      open when `A > theta_high`;
      close when `A < theta_low`.
- [x] Sweep `theta_low/theta_high`.
- [x] Sweep release fraction.

#### C1-B.4 Hysteresis Plus Refractory

- [x] Add refractory period after release.
- [x] Sweep `refractory_steps`:
      `5`, `10`, `20`.
- [x] Check whether refractory policy reduces chatter and creates stable phase
      ordering.

#### C1-B.5 Coupled Forward/Return Gate

- [x] Implement coupled forward/return gating only after single-channel
      release policies are audited.
- [x] Ensure forward and return channels do not fire independently.
- [x] Record reset/enable conditions from sink intake and source refill.

#### Required Controls

- [x] No-delay accumulator.
- [x] Passive leak only.
- [ ] Threshold shuffled.
- [x] Forward-only accumulator.
- [x] Return-only accumulator.
- [ ] Randomized release phase.
- [x] Accumulator budget audit:
      `B = sum_i C_i + sum_a A_a`.

Note:

```text
Threshold-shuffled and randomized-release-phase controls remain available for
a promoted tranche. They were not needed to interpret this first C1-B result,
because no release policy produced raw or role-gated cascades.
```

### C1 Closeout

Status: complete.

Classification:

```text
c1_closed_no_recurrent_role_gated_phase_cycle
```

Result:

```text
Delayed accumulator transport and local release policies resolved neither the
phase-order nor recurrence problem. Across leak, threshold, hysteresis,
refractory, and coupled-release variants, no recurrent role-gated phase cycle
was observed under the current GRC9V3 flux proposal surface.
```

Remaining failure mode:

```text
absence of endogenous loop-phase organization,
not merely lack of delay, storage, or paired source/sink transport
```

Next surface:

```text
C3: three-pole phase substrate
```

#### Promotion Rule

- [ ] If a release policy produces role-gated repeated cycles, do not promote
      from the diagnostic sweep directly.
- [ ] Create a new named tranche, e.g.
      `N03-C1R1-delayed-accumulator-loop-v1`.
- [ ] Require fresh U/S/K/null/reversal controls.
- [ ] Require role-gated cascades >= `n_cycles_min`.
- [ ] Require budget including accumulator state to be conserved.
- [ ] Require nulls to fail the same cycle claim.
- [ ] Require forward-only and return-only controls to fail.
- [ ] Require phase order to survive small perturbation.

### Secondary Branch C Surfaces

- [ ] C2: two-compartment/reservoir-conduit fixture:
      source reservoir, forward conduit, sink reservoir, return conduit.
- [x] C3: theory-justified three-pole phase substrate, opened because two-pole
      cycling appears underdetermined under C1/C1-B.
- [ ] C4: full `GRC9V3.step()` execution surface, only as a separate named
      surface with adaptive topology/spark/boundary stages explicitly audited.

### C3. Three-Pole Phase Substrate

Status: opened, not implemented.

Question:

```text
Is the two-pole source/sink loop underdetermined because it lacks an explicit
intermediate phase state, and can a conserved three-pole substrate produce
ordered recurrent phase cycling under fixed topology?
```

Ground rules:

- [ ] New named surface; does not inherit positive evidence from C1.
- [ ] Fresh nulls and controls required.
- [ ] Three candidate pole regions:
      `R1`, `R2`, `R3`.
- [ ] Directed pole-interaction matrix:
      `P_mn(t)`.
- [ ] Phase-pattern target:
      `R1 -> R2 -> R3 -> R1`.
- [ ] Budget conservation over node coherence and any explicit accumulator
      state.
- [ ] Fixed topology.
- [ ] No external source/sink terms.
- [ ] No movement claim.
- [ ] No `src/*` changes without explicit separate approval.

Claim ceiling:

```text
three-pole diagnostic surface, not positive loop claim
```

### C3.1 Three-Pole Fixture And Masks

Status: complete.

- [x] Define fixed topology for three-pole surface.
- [x] Define candidate pole masks:
      `R1`, `R2`, `R3`.
- [x] Define channel arcs:
      `R1 -> R2`,
      `R2 -> R3`,
      `R3 -> R1`.
- [x] Define null controls.
- [x] Define reversal controls.
- [x] Define phase target:
      `R1 -> R2 -> R3 -> R1`.
- [x] Ensure source/pole labels are masks, not positive evidence.
- [x] Preserve fixed-topology and no-external-source/sink constraints.

### C3.2 Three-Pole Observables

Status: complete.

- [x] Compute pole masses:
      `C_1(t)`, `C_2(t)`, `C_3(t)`.
- [x] Compute pole export/import roles from edge-level flux evidence.
- [x] Compute pole-interaction matrix:
      `P_mn(t)`.
- [x] Compute network closure score.
- [x] Compute phase-pattern score.
- [x] Compute ordered three-stage cascade count.
- [x] Keep raw cascades separate from role-gated cascades.
- [x] Serialize formulas and thresholds used by the classifier.

### C3.3 Synthetic Validator

Status: complete.

- [x] Accept ordered synthetic cycle:
      `R1 -> R2 -> R3 -> R1`.
- [x] Reject scrambled phase order.
- [x] Reject two-pole-only traces.
- [x] Reject budget-drift traces.
- [ ] Reject randomized-label traces.
- [x] Verify report schema and deterministic digests.

Note:

```text
Randomized-label rejection remains required before promotion into a named
positive tranche. It was not required for the first C3 runtime interpretation
because no runtime candidate rows were observed.
```

### C3.4 Runtime Fixed-Topology Runner

Status: complete; negative for runtime three-pole cycling.

- [x] Run real GRC9V3 fixed-topology continuity on the three-pole fixture.
- [x] Do not call full `step()`.
- [x] Do not call spark expansion, growth, boundary behavior, birth, pruning,
      or adaptive topology stages.
- [x] Keep `src/*` untouched.
- [x] Audit topology.
- [x] Audit budget.
- [x] Record result as diagnostic only.

Implementation:

- [x] Add replayable C3 diagnostic script:
      `scripts/run_c3_three_pole_diagnostic.py`.
- [x] Write machine-readable output:
      `outputs/c3_three_pole_diagnostic_report.json`.
- [x] Write human-readable report:
      `reports/c3_three_pole_diagnostic_report.md`.

Command run:

```bash
.venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/run_c3_three_pole_diagnostic.py
```

Result:

```text
status: pass
classification: c3_fixed_topology_no_three_pole_candidate_rows
runtime candidate lanes: []
topology changed: false
budget failures: 0
```

Synthetic validator:

```text
ordered R1 -> R2 -> R3 -> R1:
    raw cascades = 4
    role-gated cascades = 4
    budget passed = true

scrambled phase order:
    role-gated cascades = 0

two-pole-only trace:
    role-gated cascades = 0

budget-drift trace:
    budget passed = false
```

Runtime fixed-topology result:

```text
U0, U3, P, P_reversed:
    network closure = 0
    raw three-pole cascades = 0
    role-gated three-pole cascades = 0
    candidate = false
```

Interpretation:

```text
The C3 observable/classifier can detect ordered three-pole cycles in controlled
traces, but the real fixed-topology GRC9V3 continuity surface does not generate
three-pole network closure or phase cycling from the first three-pole fixture.
```

### C3.5 Accumulator / Phase-Channel Runner

Status: complete; negative for three-pole closure.

- [x] Open only if C3.4 is negative or insufficient.
- [x] Add three-channel accumulator/phase-channel runner.
- [x] Audit budget as node coherence plus accumulator state.
- [x] Preserve fixed topology.
- [x] Keep raw phase-pattern evidence separate from role-gated evidence.
- [x] Record result as diagnostic only.

Implementation:

- [x] Add replayable C3.5 runner:
      `scripts/run_c3_5_three_channel_accumulator.py`.
- [x] Run parallel three-channel delay policies:
      `3`, `6`.
- [x] Run cyclic phase-delay policies:
      `3`, `6`, `10`.
- [x] Run cyclic phase-delay with refractory:
      delay `6`, refractory `10`.
- [x] Run P and P-reversed lanes for all policies.
- [x] Run U0/U3 controls for the serious cyclic phase-delay policy.
- [x] Write machine-readable output:
      `outputs/c3_5_three_channel_accumulator_report.json`.
- [x] Write human-readable report:
      `reports/c3_5_three_channel_accumulator_report.md`.

Command run:

```bash
.venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/run_c3_5_three_channel_accumulator.py
```

Result:

```text
status: pass
classification: c3_5_no_three_pole_candidate_conditions
rows: 14
promising rows: 0
max network closure: 0
max raw three-pole cascades: 0
max role-gated three-pole cascades: 0
topology changed: false
accumulator budget failures: 0
```

Interpretation:

```text
Three-channel accumulator storage produces small in-flight amounts, but under
the current GRC9V3 flux proposal surface it does not generate three-pole
network closure. The failure remains generative: the runtime does not produce
the channel sequence R1 -> R2 -> R3 -> R1 without a more explicit phase drive,
compartmental mechanism, or different theory surface.
```

### C3.6 Controls And Closeout

Status: partial for negative C3 result.

- [x] Run null controls.
- [ ] Run shuffled pole-label control.
- [ ] Run disabled-channel control.
- [x] Run reversed phase-order/control lane:
      `P_reversed`.
- [x] Run budget audit.
- [x] Run topology audit.
- [x] Produce current closeout classification:
      `c3_5_no_three_pole_candidate_conditions`.

Note:

```text
Shuffled pole labels and disabled-channel controls remain required before any
future promotion into a named positive tranche. They were not required to
interpret the current C3.5 result because no network closure, raw cascades, or
role-gated cascades were observed.
```

### C3 Closeout

Status: complete.

Classification:

```text
c3_closed_no_directed_cyclic_channel_sequence
```

Result:

```text
The three-pole fixed-topology accumulator fixture validated the multi-pole
fixture path, classifier, and accumulator budget accounting, but did not
produce the ordered channel sequence R1 -> R2 -> R3 -> R1.
```

Narrowed failure mode:

```text
The issue is not only two-pole underdetermination, missing delay, or lack of
accumulator storage. Under the current GRC9V3 proposal surface, the system does
not generate directed cyclic channel sequencing on the tested fixed-topology
substrates.
```

Negative-evidence ladder:

```text
N03 first tranche:
    plain two-aspect ported ring does not produce polarized loop.

Branch B:
    amplitude, mask, scale, spacing, attenuation, and conductance corridor
    sweeps do not rescue it.

C1:
    delayed accumulators create paired delayed transport but not repeated
    phase-ordered cycling.

C1-B:
    leak / threshold / hysteresis / refractory / coupled release policies do
    not produce recurrent cycles.

C3:
    three-pole fixture and three-channel accumulator budget preservation still
    do not produce ordered channel sequence R1 -> R2 -> R3 -> R1.
```

Next action:

```text
Open Branch D1 circulatory proposal audit before adding new proposal terms or
phase controllers.
```

## Branch D. Proposal-Surface Diagnosis

Status: opened, not implemented.

### D1. Circulatory Proposal Audit

Status: complete.

Question:

```text
Can the current GRC9V3 proposal surface produce any nonzero loop circulation
around a closed channel, independent of source/sink masks?
```

Target metric:

```text
loop_circulation(t) = signed sum of flux_uv around a declared closed cycle
```

Checks:

- [x] Define closed-cycle fixtures independent of source/sink masks.
- [x] Compute signed loop circulation from edge-level `flux_uv`.
- [x] Compare ring and three-pole cycle surfaces.
- [x] Test whether circulation persists, decays, or reverses.
- [x] Keep topology fixed.
- [x] Do not add circulatory proposal terms.
- [x] Do not add phase controllers.
- [x] Keep `src/*` unchanged unless separately approved.

Implementation:

- [x] Add replayable D1 audit script:
      `scripts/run_d1_circulatory_proposal_audit.py`.
- [x] Run original ring scenarios:
      U0, U1, S, K.
- [x] Run deterministic ring profile scenarios:
      sinusoid, traveling_phase_seed, sawtooth.
- [x] Run three-pole scenarios:
      U0, U3, P, P_reversed.
- [x] Write machine-readable output:
      `outputs/d1_circulatory_proposal_audit.json`.
- [x] Write human-readable report:
      `reports/d1_circulatory_proposal_audit.md`.

Command run:

```bash
.venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/run_d1_circulatory_proposal_audit.py
```

Result:

```text
status: pass
classification: d1_weak_residual_loop_circulation_observed
max_abs_loop_circulation: 0.0070727893817062425
max_abs_normalized_circulation: 0.006041388204739038
topology changed: false
budget failures: 0
```

Observed:

```text
U0 and several symmetric/null cases have zero or numerical-near-zero
circulation.

Structured S and three-pole P/P_reversed show nonzero signed loop circulation,
but the normalized circulation is weak: at most about 0.006 of total absolute
edge flux.
```

Interpretation:

```text
The current GRC9V3 proposal surface can produce weak residual signed loop
imbalance on asymmetric fixtures, but D1 does not show material self-sustaining
circulatory proposal dynamics. This supports the broader conclusion that
fixed-topology GRC9V3 continuity remains primarily a conservative relaxation
substrate under the tested surfaces.
```

Bounded interpretation:

```text
D1 did not show absence of circulation.
D1 showed weak residual circulation only.
```

Key normalized metric:

```text
abs(sum_cycle J_e) / sum_cycle abs(J_e) ~= 0.006
```

Updated failure mode:

```text
GRC9V3 fixed-topology continuity can produce small asymmetric circulation
residue, but not a sufficiently strong, persistent, phase-organizing
circulatory mode under the tested fixtures.
```

### D1b. Persistence And Coherence Of Residual Circulation

Status: complete.

Question:

```text
Is the weak residual circulation persistent, sign-stable, and correlated with
loop-role evidence, or is it transient/noisy relaxation residue?
```

Metrics:

- [x] Mean signed circulation.
- [x] Max absolute signed circulation.
- [x] Mean normalized circulation.
- [x] Max normalized circulation.
- [x] Sign persistence fraction.
- [x] Lag-1 autocorrelation.
- [x] Circulation decay rate.
- [x] Correlation with mean absolute flux as the available D1 proxy.

Run record:

```bash
.venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/run_d1b_circulation_persistence.py
```

Generated artifacts:

```text
outputs/d1b_circulation_persistence_report.json
reports/d1b_circulation_persistence_report.md
```

Result:

```text
status: pass
classification: d1b_stable_weak_residual_circulation
material_rows: none
stable_weak_rows: d1_ring_s
```

Key metrics:

```text
d1_ring_s:
    mean signed circulation: -0.0024265037154406937
    max absolute signed circulation: 0.0070727893817062425
    mean absolute normalized circulation: 0.0021872230291446163
    max absolute normalized circulation: 0.006041388204739038
    sign persistence fraction: 1.0
    lag-1 autocorrelation: 0.9984405959734713
    late/early absolute-circulation ratio: 2.9245508068298265

d1_three_pole_p:
    max absolute normalized circulation: 0.003058654627651635
    sign persistence fraction: 0.55

d1_three_pole_p_reversed:
    max absolute normalized circulation: 0.003058654627651635
    sign persistence fraction: 0.55
```

Interpretation rule:

```text
If residual circulation is transient, sign-unstable, or uncorrelated with loop
evidence, close the native fixed-topology proposal branch and open D2 as an
explicitly labeled conservative circulatory proposal prototype.

If residual circulation is stable but weak, D2 can target amplification or
preservation of the native residual component.
```

D1b conclusion:

```text
The native fixed-topology GRC9V3 proposal surface is not strictly
circulation-free. It can produce weak, partly coherent residual circulation on
structured fixtures. However, the observed residual remains below the material
circulation threshold and has not organized source/sink roles, closure, or
recurrent phase cycles. Treat it as a possible target for explicit prototype
amplification/preservation, not as native loop evidence.
```

### D1c. Native Port-Rotation Circulation Audit

Status: complete.

Question:

```text
Do native GRC9V3 port-rotation fixtures expose stronger loop circulation than
the direct source/sink channel fixtures tested in D1?
```

Boundary:

```text
D1c changes only the fixture and measurement surface. It does not add a
circulatory proposal term, phase controller, topology change, or src/* change.
```

Checks:

- [x] Define clockwise port-cycle fixture:
      `1 -> 2 -> 3 -> 6 -> 9 -> 8 -> 7 -> 4 -> 1`.
- [x] Define counter-clockwise/reversed port-cycle fixtures.
- [x] Run native fixed-topology GRC9V3 continuity surface.
- [x] Compute signed loop circulation from edge-level `flux_uv`.
- [x] Compare against prior D1 direct/channel baseline.
- [x] Preserve topology.
- [x] Preserve budget.
- [x] Keep material threshold at normalized circulation `>= 0.01`.
- [x] Do not modify `src/*`.

Run record:

```bash
.venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/run_d1c_port_rotation_audit.py
```

Generated artifacts:

```text
outputs/d1c_port_rotation_audit.json
reports/d1c_port_rotation_audit.md
```

Result:

```text
status: pass
classification: d1c_weak_residual_port_rotation_circulation_observed
material_rows: none
max_abs_loop_circulation: 0.0036735167365173904
max_abs_normalized_circulation: 0.005365511110850774
```

Baseline comparison:

```text
D1 direct/channel max_abs_normalized_circulation:
    0.006041388204739038

D1c port-rotation max_abs_normalized_circulation:
    0.005365511110850774
```

Key rows:

```text
d1c_rotation_cw_uniform:
    max_abs_normalized_circulation: 0.0

d1c_rotation_ccw_traveling_phase_seed:
    max_abs_normalized_circulation: 0.005365511110850693

d1c_rotation_cw_traveling_phase_seed_reversed:
    max_abs_normalized_circulation: 0.005365511110850774
```

D1c conclusion:

```text
Native fixed-topology GRC9V3 can produce weak residual circulation on both
direct channel fixtures and port-rotation fixtures. Port rotation does not
unlock a material loop-generating mode under the tested surfaces. The
remaining failure is not only direct-flow fixture bias; it is absence of a
strong endogenous circulatory proposal mode.
```

### D1d. Initial Circulating-Flux Retention Audit

Status: complete.

Question:

```text
If every edge in the closed ring starts with clockwise/counter-clockwise
`flux_uv`, does native GRC9V3 preserve that initialized corridor flow, or does
`rebuild_transport_state()` overwrite it with potential-driven proposal flux?
```

Boundary:

```text
D1d initializes edge flux only. It does not add edge storage, momentum,
packets, accumulators, a circulatory proposal term, topology changes, or
src/* changes.
```

Checks:

- [x] Initialize closed ring with nonzero clockwise `flux_uv` on every edge.
- [x] Test uniform coherence with multiple initial flux magnitudes.
- [x] Test asymmetric coherence profiles with initialized flux.
- [x] Test counter-clockwise initialized flux control.
- [x] Measure first-rebuild signed circulation retention.
- [x] Measure first-rebuild absolute-flux retention.
- [x] Measure max normalized circulation after rebuild.
- [x] Preserve topology.
- [x] Preserve budget.
- [x] Do not modify `src/*`.

Run record:

```bash
.venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/run_d1d_initial_flux_retention.py
```

Generated artifacts:

```text
outputs/d1d_initial_flux_retention.json
reports/d1d_initial_flux_retention.md
```

Result:

```text
status: pass
classification: d1d_initial_flux_erased_by_transport_rebuild
retained_rows: none
material_rows: none
```

Representative rows:

```text
d1d_uniform_clockwise_flux_0p05:
    initial loop circulation: 0.6000000000000001
    first rebuild loop circulation: 0.0
    first signed retention ratio: 0.0
    max normalized circulation after rebuild: 0.0

d1d_source_sink_clockwise_flux_0p05:
    initial loop circulation: 0.6000000000000001
    first rebuild loop circulation: 0.0
    first signed retention ratio: 0.0
    first absolute-flux retention ratio: 0.09933619270504468
    max normalized circulation after rebuild: 0.0

d1d_traveling_phase_seed_clockwise_flux_0p05:
    initial loop circulation: 0.6000000000000001
    first rebuild loop circulation: 6.954434341799928e-07
    first signed retention ratio: 1.1590723902999878e-06
    first absolute-flux retention ratio: 0.2933865757187918
    max normalized circulation after rebuild: 9.582625842412871e-05
```

D1d conclusion:

```text
Initialized edge `flux_uv` does not behave as persistent closed corridor flow
in native GRC9V3. The first transport rebuild effectively erases the imposed
signed loop circulation. Some asymmetric profiles retain or regenerate
absolute edge activity, but not the original signed circulation. Therefore
plain native GRC9V3 `flux_uv` is a recomputed proposal surface, not a
blood/vein-like edge-flow or momentum state.
```

Updated native-audit conclusion:

```text
The tested native fixed-topology GRC9V3 surfaces do not contain a material
closed-flow state. Direct channels, port rotations, and initialized full-ring
flux all reduce to weak residual or recomputed relaxation behavior. A
blood/vein-like conserved loop would need explicit edge/corridor coherence,
packets, accumulators, momentum, a circulatory proposal term, an adaptive
runtime stage, or a different causal execution layer.
```

### D1e. Alternating Source/Sink Pole Ring Audit

Status: complete.

Question:

```text
If the passive intermediate-node corridor is the failure point, does
distributing active source/sink-aspect regions around the whole ring create
stronger native cyclic circulation?
```

Fixture:

```text
S1 -> K2 -> S2 -> K1 -> S1

S1 = nodes [0, 1]
K2 = nodes [3, 4]
S2 = nodes [6, 7]
K1 = nodes [9, 10]
```

Boundary:

```text
D1e changes only the fixture/initialization surface. It does not add role
switching, propulsion, edge storage, a phase controller, a circulatory proposal
term, topology changes, or src/* changes.
```

Checks:

- [x] Define alternating source/sink pole masks.
- [x] Define channel arcs between alternating poles.
- [x] Run uniform null.
- [x] Run alternating polarity rows.
- [x] Run reversed/control rows.
- [x] Measure source/sink role pattern from export/import and pre-budget mass
      change.
- [x] Measure signed loop circulation.
- [x] Measure repeated channel-activity proxy.
- [x] Preserve topology.
- [x] Preserve budget.
- [x] Do not modify `src/*`.

Run record:

```bash
.venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/run_d1e_alternating_pole_ring.py
```

Generated artifacts:

```text
outputs/d1e_alternating_pole_ring.json
reports/d1e_alternating_pole_ring.md
```

Result:

```text
status: pass
classification: d1e_partial_alternating_pole_evidence_only
candidate_rows: none
role_pattern_rows: d1e_alternating, d1e_alternating_strong
material_rows: none
max_abs_normalized_circulation: 0.0014352682367625483
```

Representative rows:

```text
d1e_alternating:
    role pattern passed: true
    max normalized circulation: 0.0
    cycle proxy count: 0

d1e_alternating_strong:
    role pattern passed: true
    max normalized circulation: 0.0
    cycle proxy count: 0

d1e_traveling_four_pole:
    role pattern passed: false
    max normalized circulation: 0.0014352682367625483
    cycle proxy count: 0
```

D1e conclusion:

```text
Distributed active polarity can create the intended static measured
source/sink role pattern, but it does not create cyclic propagation. In the
balanced alternating rows, opposing channel pairs cancel signed loop
circulation. In the traveling/four-pole rows, weak residual circulation appears
but the intended role pattern fails and no repeated cycle appears.
```

Updated native-audit conclusion:

```text
The failure is not only that passive intermediate corridor nodes drop flux.
Native fixed-topology GRC9V3 can form static distributed source/sink roles,
but those roles do not hand off or propel a closed loop without an additional
phase, storage, momentum, handoff, adaptive, or causal transport mechanism.
```

### D1f. Minimal Handoff Mechanism Probes

Status: complete.

Question:

```text
Which single added mechanism is sufficient to convert the D1e static
source/sink role pattern into closed-loop propagation?
```

Boundary:

```text
D1f is experiment-local mechanism isolation. It is not native GRC9V3 evidence
and not a positive N03 loop claim.
```

Lanes:

- [x] `D1f1`: D1e + explicit phase handoff.
- [x] `D1f2`: D1e + edge/corridor storage.
- [x] `D1f3`: D1e + momentum retention.
- [x] `D1f4`: D1e + causal packet delay.
- [x] `D1f5`: D1e + adaptive role handoff.

Run record:

```bash
.venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/run_d1f_minimal_handoff_mechanisms.py
```

Generated artifacts:

```text
outputs/d1f_minimal_handoff_mechanisms.json
reports/d1f_minimal_handoff_mechanisms.md
outputs/d1f_minimal_handoff_timeseries/*.jsonl
```

Result:

```text
status: pass
classification: d1f_phase_and_closed_flow_positive_lanes_observed
phase_positive_lanes: D1f1, D1f4, D1f5
closed_flow_positive_lanes: D1f3
positive_lanes: D1f1, D1f3, D1f4, D1f5
```

Lane outcomes:

```text
D1f1 explicit phase handoff:
    phase cycles: 8
    positive surface: phase

D1f2 edge/corridor storage:
    phase cycles: 0
    positive surface: none
    note: storage alone creates one-way channel activity but not a closed loop

D1f3 momentum retention:
    phase cycles: 0
    simultaneous closed-flow steps: 140
    positive surface: closed-flow

D1f4 causal packet delay:
    phase cycles: 11
    positive surface: phase

D1f5 adaptive role handoff:
    phase cycles: 11
    positive surface: phase
```

D1f conclusion:

```text
D1f confirms that the missing ingredient is not another static fixture alone.
Explicit phase handoff, causal packet delay, and adaptive role handoff are
sufficient to produce ordered closed-loop event cycles under conserved
experiment-local dynamics. Momentum retention is sufficient to produce
continuous closed-flow behavior, but not phase-ordered handoff. Edge/corridor
storage alone is insufficient: it can produce material channel activity, but
without handoff it does not close the loop.
```

Claim boundary:

```text
D1f is sufficiency evidence for future prototype design, not native GRC9V3
loop evidence. Any promising D1f surface must be promoted into a named tranche
or D2 prototype with fresh controls before stronger claims are made.
```

### D2. Conserved Causal Packet Loop Prototype

Status: unblocked as prototype only after D1b, D1c, D1d, D1e, and D1f.

Boundary:

```text
D2 replaces the earlier broad conservative-circulatory-prototype placeholder.
It promotes D1f4 causal packet delay only.

D2 is a new experiment-local packetized prototype, not native GRC9V3 evidence.
```

- [x] Do not open D2 until D1b is complete.
- [x] Run D1c native port-rotation audit before D2.
- [x] Run D1d initialized closed-flow retention audit before D2.
- [x] Run D1e alternating active-pole audit before D2.
- [x] Run D1f minimal handoff mechanism probes before D2.
- [x] Select D1f4 causal packet delay as D2.
- [x] Record that old generic D2 is replaced.
- [x] Keep D2 experiment-local unless separately approved as a
      core/theory task.
- [x] Label D2 reports as packetized closed-flow prototype evidence.
- [x] Preserve budget as node coherence plus in-flight packet coherence.
- [x] Add fresh null and reversal controls.
- [ ] Keep D1f1, D1f3, and D1f5 as deferred alternatives.
- [x] Do not hide D2 behavior in `src/*`.

Selected D2 rationale:

```text
D1f4 was mechanism-positive, budget-conserving, and closest to LGRC-style
in-flight coherence. It directly addresses the D1d result that native
`flux_uv` is recomputed proposal flux rather than persistent corridor flow.
```

Scope:

```text
Promote D1f4 only.
Do not combine D1f1, D1f3, or D1f5 into D2.
```

Deferred alternatives:

- [ ] `D2-alt-phase-handoff`: D1f1 explicit phase handoff, deferred because it
      is more controller-like.
- [ ] `D2-alt-momentum`: D1f3 momentum retention, deferred because it produces
      continuous closed flow rather than phase handoff.
- [ ] `D2-alt-adaptive-handoff`: D1f5 adaptive role handoff, deferred because
      it opens adaptive policy semantics.

Promotion rule:

- [x] Positive D2 results support packetized prototype evidence only.
- [x] Do not promote D2 results as native GRC9V3 evidence.
- [x] Keep movement claims blocked.

Run record:

```bash
.venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/run_d2_conserved_causal_packet_loop.py
```

Generated artifacts:

```text
outputs/d2_conserved_causal_packet_loop.json
reports/d2_conserved_causal_packet_loop.md
outputs/d2_conserved_causal_packet_loop_timeseries/*.jsonl
```

Result:

```text
status: pass
classification: d2_packetized_closed_flow_positive_with_controls
positive_rows: D2-P-cw-packet-loop, D2-R-ccw-packet-loop
errors: none
```

Lane outcomes:

```text
D2-U0-no-seed:
    cycles: 0
    expected: negative
    result: negative

D2-P-cw-packet-loop:
    direction: clockwise
    cycles: 11
    opposite cycles: 0
    expected: positive
    result: positive

D2-R-ccw-packet-loop:
    direction: counter-clockwise
    cycles: 11
    opposite cycles: 0
    expected: positive
    result: positive

D2-C-forward-only:
    cycles: 0
    expected: negative
    result: negative

D2-C-broken-return:
    cycles: 0
    expected: negative
    result: negative

D2-C-scrambled-order:
    cycles: 0
    expected: negative
    result: negative
```

D2 conclusion:

```text
Packetized in-flight coherence is sufficient, in this experiment-local
prototype, to turn the D1e static role surface into ordered closed-loop
propagation under exact node-plus-packet budget accounting. The null, one-way,
broken-return, and scrambled-order controls stay negative. Material
per-channel circulation alone is not enough: the controls can move packets,
but they fail the ordered cycle gate.
```

### D2.1. Packet Loop Robustness And Conservation Audit

Status: complete.

Boundary:

```text
D2.1 hardens D2 only. It is experiment-local packetized prototype evidence,
not native GRC9V3 evidence, not a `src/*` change, and not movement evidence.
```

Checklist:

- [x] Add a D2.1 robustness script.
- [x] Keep the script under the experiment-local `scripts/` directory.
- [x] Reuse D2 channel definitions without changing D2 or `src/*`.
- [x] Preserve the node-plus-packet budget invariant.
- [x] Assign deterministic packet ids.
- [x] Record packet creation, absorption, and in-flight totals.
- [x] Audit duplicate packet ids.
- [x] Audit orphan parent ids.
- [x] Audit unknown channel ids.
- [x] Audit packet balance:
      `created - absorbed - in_flight = 0`.
- [x] Check canonical channel causality for positive rows.
- [x] Keep scrambled/wrong-direction controls negative.
- [x] Check direction reversal symmetry.
- [x] Include no-seed and wrong-seed controls.
- [x] Include weak-seed and over-seed rows.
- [x] Include a packet-delay sweep.
- [x] Include deterministic delay jitter.
- [x] Include deterministic small node-coherence perturbation.
- [x] Record the command and generated artifacts.
- [x] Keep positive rows labeled as packetized prototype evidence only.
- [x] Keep native GRC9V3 and movement claims blocked.

Run record:

```bash
.venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/run_d2_1_packet_loop_robustness.py
```

Generated artifacts:

```text
outputs/d2_1_packet_loop_robustness.json
reports/d2_1_packet_loop_robustness.md
outputs/d2_1_packet_loop_robustness_timeseries/*.jsonl
```

Result:

```text
status: pass
classification: d2_1_packet_loop_robustness_passed
direction reversal symmetry: passed
max node-plus-packet budget error: 1.11022e-16
duplicate packet ids: 0
orphan parent ids: 0
unknown channel ids: 0
errors: none
```

Positive prototype rows:

```text
D2.1-P-cw-delay-1:
    cycles: 34

D2.1-P-cw-delay-3:
    cycles: 11

D2.1-P-cw-delay-6:
    cycles: 5

D2.1-R-ccw-delay-3:
    cycles: 11

D2.1-S-weak-seed:
    cycles: 11

D2.1-S-over-seed:
    cycles: 11

D2.1-N-jittered-delay:
    cycles: 11

D2.1-N-node-perturbation:
    cycles: 11
```

Negative controls:

```text
D2.1-U0-no-seed:
    cycles: 0
    result: negative

D2.1-C-wrong-direction-seed:
    declared clockwise cycles: 0
    opposite cycles: 11
    result: negative for the declared clockwise expectation

D2.1-C-forward-only:
    cycles: 0
    result: negative

D2.1-C-broken-return:
    cycles: 0
    result: negative

D2.1-C-scrambled-order:
    cycles: 0
    result: negative
```

D2.1 conclusion:

```text
The D2 packetized prototype survives the first robustness and conservation
audit. Ordered closed-flow propagation remains stable across delay sweep,
direction reversal, seed-strength changes, deterministic delay jitter, and a
small node perturbation. Packet ids are conserved without duplication or
orphaning, and the node-plus-packet budget remains exact to floating-point
tolerance. This strengthens the bounded packetized prototype result only; it
does not convert the result into native GRC9V3 loop evidence.
```

### D2.2. State-Triggered Packet Departure

Status: complete.

Boundary:

```text
D2.2 is the last N03-local autonomy bridge before LGRC9V3 alignment. It asks
whether packet departure can be triggered by measured state rather than a
hand-authored packet seed schedule. It remains experiment-local packetized
prototype evidence, not native GRC9V3 evidence.
```

Trigger policy:

```text
source_pole_mass - reference_pole_mass >= trigger_threshold
```

Checklist:

- [x] Add a D2.2 state-triggered packet script.
- [x] Keep the script under the experiment-local `scripts/` directory.
- [x] Do not change `src/*`.
- [x] Use a serialized trigger threshold.
- [x] Launch initial packet departure from measured pole surplus rather than
      an explicit packet seed schedule.
- [x] Trigger later departures from packet arrivals and measured target-pole
      surplus.
- [x] Preserve exact node-plus-packet budget accounting.
- [x] Preserve packet id, duplicate, orphan, and unknown-channel audits.
- [x] Preserve direction reversal symmetry.
- [x] Include no-surplus and subthreshold controls.
- [x] Include wrong-direction, forward-only, and broken-return controls.
- [x] Include delay sweep rows.
- [x] Include weak-trigger and over-trigger rows.
- [x] Include deterministic delay jitter.
- [x] Include deterministic small node-coherence perturbation.
- [x] Record initial failed run cause and correction.
- [x] Record the final command and generated artifacts.
- [x] Keep native GRC9V3 and movement claims blocked.

Initial failed run:

```text
The first D2.2 run failed with:
    D2.2-C-forward-only failed expectation
    D2.2-C-broken-return failed expectation

Cause:
    the state-trigger scanner ignored the forward-only and broken-return
    control modes, allowing those controls to trigger all channels.

Correction:
    restrict trigger-eligible channels by mode:
        forward_only -> first channel only
        broken_return -> sequence without final return channel
```

Final run record:

```bash
.venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/run_d2_2_state_triggered_packets.py
```

Generated artifacts:

```text
outputs/d2_2_state_triggered_packets.json
reports/d2_2_state_triggered_packets.md
outputs/d2_2_state_triggered_packets_timeseries/*.jsonl
```

Result:

```text
status: pass
classification: d2_2_state_triggered_packet_departure_positive_with_controls
direction reversal symmetry: passed
max node-plus-packet budget error: 1.11022e-16
duplicate packet ids: 0
orphan parent ids: 0
unknown channel ids: 0
errors: none
```

Positive prototype rows:

```text
D2.2-P-cw-state-triggered:
    triggers: 47
    events: 46
    cycles: 11

D2.2-R-ccw-state-triggered:
    triggers: 47
    events: 46
    cycles: 11

D2.2-P-cw-delay-1:
    triggers: 140
    events: 139
    cycles: 34

D2.2-P-cw-delay-6:
    triggers: 24
    events: 23
    cycles: 5

D2.2-S-weak-trigger:
    cycles: 11

D2.2-S-over-trigger:
    cycles: 11

D2.2-N-jittered-delay:
    cycles: 11

D2.2-N-node-perturbation:
    cycles: 11
```

Negative controls:

```text
D2.2-U0-no-surplus:
    triggers: 0
    cycles: 0
    result: negative

D2.2-C-subthreshold-surface:
    triggers: 0
    cycles: 0
    result: negative

D2.2-C-wrong-direction-trigger:
    declared clockwise cycles: 0
    opposite cycles: 11
    result: negative for the declared clockwise expectation

D2.2-C-forward-only:
    triggers: 1
    cycles: 0
    result: negative

D2.2-C-broken-return:
    triggers: 3
    cycles: 0
    result: negative
```

D2.2 conclusion:

```text
D2.2 shows that the packetized loop can be launched from measured
state-triggered departure rather than from an explicit packet seed schedule.
The loop remains conserved and robust under the same audit discipline used by
D2.1. This is a meaningful autonomy bridge for the packetized prototype, but
it is still not native GRC9V3 loop evidence and does not open movement claims.
```

### D2.3. Self-Rearming Packet Pulse Probe

Status: complete.

Boundary:

```text
D2.3 is the final N03-local bridge before LGRC9V3 alignment. It tests whether
the state-triggered packet loop can re-arm itself after a completed cycle. It
is a bounded L5-like packetized pulse candidate only, not native GRC9V3
evidence and not movement evidence.
```

Self-rearm rule:

```text
completed cycle returns packet to source pole
-> source_pole_mass - reference_pole_mass >= trigger_threshold
-> next packet departs
```

Checklist:

- [x] Add a D2.3 self-rearming packet script.
- [x] Keep the script under the experiment-local `scripts/` directory.
- [x] Do not change `src/*`.
- [x] Measure rearming from returned-packet source surplus.
- [x] Do not use a hand-authored packet seed schedule after initial state.
- [x] Remove the first attempted explicit reserve-recharge surface.
- [x] Restrict eligible next channel by declared lane order after parent
      arrivals.
- [x] Keep scrambled-order control meaningful.
- [x] Preserve exact node-plus-packet budget accounting.
- [x] Preserve packet id, duplicate, orphan, and unknown-channel audits.
- [x] Preserve direction reversal symmetry.
- [x] Include no-surplus, subthreshold, and threshold-too-high controls.
- [x] Include wrong-direction, forward-only, broken-return, and scrambled-order
      controls.
- [x] Include a low-threshold robustness row.
- [x] Include deterministic delay jitter.
- [x] Record failed probe setup and final correction.
- [x] Record the final command and generated artifacts.
- [x] Keep native GRC9V3, movement, locomotion, agency, and biological motility
      claims blocked.

Probe correction notes:

```text
First attempt:
    used an explicit reserve-recharge policy after completed cycles.

Issue:
    the extra recharge surface interfered with canonical packet causality.

Correction:
    remove explicit recharge and measure natural self-rearm only.

Second issue:
    scrambled-order control was inert because unrestricted state scanning still
    selected the canonical surplus pole.

Correction:
    after a parent packet arrival, restrict trigger-eligible channels to the
    lane's declared next channel.
```

Final run record:

```bash
.venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/run_d2_3_self_rearming_packets.py
```

Generated artifacts:

```text
outputs/d2_3_self_rearming_packets.json
reports/d2_3_self_rearming_packets.md
outputs/d2_3_self_rearming_packets_timeseries/*.jsonl
```

Result:

```text
status: pass
classification: d2_3_self_rearming_packet_pulse_candidate_with_controls
direction reversal symmetry: passed
max node-plus-packet budget error: 0
duplicate packet ids: 0
orphan parent ids: 0
unknown channel ids: 0
errors: none
```

Positive prototype rows:

```text
D2.3-P-self-rearming-cw:
    triggers: 47
    rearms: 11
    events: 46
    cycles: 11

D2.3-R-self-rearming-ccw:
    triggers: 47
    rearms: 11
    events: 46
    cycles: 11

D2.3-S-low-threshold:
    triggers: 47
    rearms: 11
    events: 46
    cycles: 11

D2.3-N-jittered-delay:
    triggers: 47
    rearms: 11
    events: 46
    cycles: 11
```

Negative controls:

```text
D2.3-U0-no-surplus:
    cycles: 0
    result: negative

D2.3-C-subthreshold:
    cycles: 0
    result: negative

D2.3-C-threshold-too-high:
    cycles: 0
    result: negative

D2.3-C-wrong-direction:
    declared clockwise cycles: 0
    opposite cycles: 11
    result: negative for the declared clockwise expectation

D2.3-C-forward-only:
    cycles: 0
    result: negative

D2.3-C-broken-return:
    cycles: 0
    result: negative

D2.3-C-scrambled-order:
    cycles: 0
    result: negative
```

D2.3 conclusion:

```text
D2.3 provides the first bounded L5-like packetized pulse-generator candidate.
The returned packet recreates measured source surplus, which fires the next
state-triggered departure without a hand-authored schedule. This strengthens
the packetized mechanism path but does not convert it into native GRC9V3 loop
evidence or movement evidence.
```

## E1. LGRC Adapter Alignment

Status: complete.

Boundary:

```text
E1 asks whether the D2.3 packetized pulse mechanism has LGRC-shaped causal
semantics. It does not claim native LGRC9V3 execution.
```

Checklist:

- [x] Translate D2.3 packet activity into an LGRC-style event ledger.
- [x] Preserve packet departure, packet arrival, event-time key, route order,
      and node-plus-packet budget evidence.
- [x] Validate the ledger from artifacts rather than hidden runner state.
- [x] Keep native GRC9V3, movement, locomotion, agency, and biological claims
      blocked.
- [x] Record that native LGRC9V3 execution was not yet established.

Result:

```text
classification: adapter_compatible
d2_3_lgrc_aligned: true
native_lgrc9v3_execution: false
core_task_requested: false
```

Conclusion:

```text
D2.3 has LGRC-shaped semantics, but E1 is an adapter/ledger result. It shows
that the packetized pulse mechanism is naturally expressible as LGRC causal
history, not that native LGRC9V3 produced it.
```

## E2. Native LGRC9V3 Runtime Alignment

Status: complete.

Boundary:

```text
E2 moves from adapter compatibility toward actual native LGRC9V3 execution.
It verifies native packet execution, static route autonomy, and the missing
surplus-trigger/self-rearm surfaces before the core Phase 8 continuation.
```

Checklist:

- [x] Replay scheduled packet routes through native LGRC9V3 packet execution.
- [x] Extract native packet events into the E1 ledger schema.
- [x] Validate packet identity, route order, event-time/proper-time surfaces,
      and node-plus-packet budget from native artifacts.
- [x] Verify static route autonomy is available.
- [x] Verify static route autonomy alone is not D2.3-equivalent.
- [x] Record missing native D2.3 primitive:
      measured surplus-trigger production.
- [x] Record missing native D2.3 evidence:
      completed self-rearm chain.
- [x] Preserve negative controls and claim boundaries.

Result:

```text
native_packet_execution_compatible
adapter_triggered_runtime_compatible
native_static_route_autonomy_available
missing_native_surplus_trigger_primitive
native_d2_3_equivalent = false
native_self_rearm_evidence = false
```

Conclusion:

```text
E2 shows that native LGRC9V3 can run the packet geometry and preserve the
ledger evidence surfaces, but D2.3 equivalence still required native route
aspects, surplus-trigger production, and completed self-rearm evidence.
```

## E3. Native LGRC9V3 D2.3-Equivalent Packet Loop

Status: complete.

Boundary:

```text
E3 is the Phase 8 native LGRC9V3 reproduction of D2.3. It is the first surface
where route-aspect semantics, surplus-trigger production, and completed
self-rearm evidence are all native LGRC9V3 runtime artifacts rather than
experiment-local adapter behavior.
```

Checklist:

- [x] Use native route-aspect semantics for pole/channel route identity.
- [x] Use native surplus-trigger production.
- [x] Require post-arrival trigger ordering:
      parent arrival -> measured surplus -> child scheduled -> child departure.
- [x] Require completed self-rearm evidence linked by packet ids, event ids,
      producer ids, route-aspect digest, channel order, and timing evidence.
- [x] Validate from native artifacts/ledger only.
- [x] Preserve node-plus-packet budget conservation.
- [x] Preserve fixed topology.
- [x] Pass clockwise and counter-clockwise direction symmetry.
- [x] Keep no-surplus, subthreshold, threshold-too-high, wrong-direction,
      forward-only, broken-return, and scrambled-order controls negative.
- [x] Preserve snapshot/telemetry replayability.
- [x] Keep native GRC9V3 proposal-flux, movement, locomotion, agency, and
      biological claims blocked.

Result:

```text
classification: n03_native_lgrc9v3_packet_loop_reproduced
native_lgrc9v3_execution = true
native_packet_execution = true
native_surplus_trigger = true
native_self_rearm_evidence = true
native_d2_3_equivalent = true
native_d2_3_equivalent_packet_loop_supported
adapter_required_for_d2_3_semantics = false
native_static_route_only = false
snapshot_telemetry_replayable = true
```

Positive rows:

```text
clockwise cycles = 3
counter-clockwise cycles = 3
clockwise completed self-rearms = 12
counter-clockwise completed self-rearms = 12
clockwise trigger count = 12
counter-clockwise trigger count = 12
max event budget error = 0.0
topology changed = false
direction symmetry = passed
```

Conclusion:

```text
E3 resolves the L5-like self-rearming pulse requirement for the native
LGRC9V3 packetized execution surface. Returned packet coherence recreates the
measured surplus condition that triggers later departures, and this is
validated under controls from native runtime artifacts.

This does not resolve L5 for native synchronous GRC9V3 proposal flux, and it
does not open L6 movement or boundary-coupling claims.
```

## Later Surface. Self-Regulation L5

Status: resolved for native LGRC9V3 packetized execution; blocked for native
GRC9V3 proposal-flux execution.

Resolution:

```text
D2.3 first established an experiment-local L5-like self-rearming packet pulse
candidate. E3 reproduced the same D2.3-equivalent mechanism as a native
LGRC9V3 packet-loop runtime surface.
```

Claim boundary:

```text
Supported:
    L5-like self-rearming packet pulse on native LGRC9V3 packetized causal
    execution.

Not supported:
    native fixed-topology GRC9V3 proposal-flux L5;
    movement or locomotion;
    agency, intention, or biological behavior.
```

## Later Surface. Boundary-Couplable Loop L6

Status: not started.

Open only after a separate boundary-coupling plan is accepted. E3 supplies a
native packetized L5-like pulse substrate, but L6 is still a movement precursor
and must hand off to the movement-ladders experiment rather than making
movement claims inside this experiment.

## Later Surface. Multi-Pole Basin Loops

Status: deferred.

Appendix A of the paper records multi-pole basin loops as a later
generalization. They are not part of the first implementation pass.

### Deferred Items

- [ ] Multi-pole candidate region sets `R_1 ... R_N`.
- [ ] Pole-interaction matrix `P_mn(t)`.
- [ ] Network closure score `Lambda_net`.
- [ ] Phase-pattern scores:
      `in_phase`,
      `anti_phase`,
      `traveling_wave_3`,
      `traveling_wave_9`,
      `custom`.
- [ ] Fragmentation gate for multi-pole claims.
- [ ] MP0-MP6 classifier.
- [ ] Three-pole fixed-topology fixtures.
- [ ] Column-mapped and row-mapped GRC9V3 fixtures.
- [ ] Nine-pole full-bundle fixture.
- [ ] Multi-pole boundary-coupling handoff to movement ladders.

### Reopen Condition

Open only after the minimal two-aspect L4 result is stable, reproducible, and
reviewed. Until then, multi-pole Appendix A surfaces must remain blocked or
deferred in reports.

## Final Packaging. Output Cleanup And Artifact Bundling

Status: pending.

Purpose:

Keep Branch B through E3 outputs reviewable during active work, then collapse
the generated-file footprint near the end without losing replay evidence.

This task is intentionally deferred. Do not perform cleanup while the current
priority is active review or actual LGRC code work.

Decision record:

```text
The number of output files is not itself an issue. Expanded outputs should stay
available while the N03 evidence trail is still being reviewed, because they
make the path from negative GRC9V3 evidence through D2.3/E3 easier to audit.

Cleanup becomes useful only for final sharing, repository operations, or review
ergonomics if the generated-file footprint starts obscuring the canonical
reports and summaries.
```

### Checklist

- [ ] Inventory generated outputs from Branch B through E3.
- [ ] Classify artifacts that should stay directly visible:
      reports,
      closeout summaries,
      compact summary JSON files,
      configs,
      scripts,
      implementation docs,
      and validation records.
- [ ] Classify bulky artifacts that may be bundled:
      time-series directories,
      packet-ledger JSONL files,
      per-lane trace dumps,
      row-level sweep outputs,
      animation checkpoint sequences,
      graph snapshots,
      and repeated validator intermediate outputs.
- [ ] Create `outputs/bundles/`.
- [ ] Create one or more JSONL bundles for bulky artifacts.
- [ ] Create `outputs/bundles/n03_generated_artifacts_manifest.json`.
- [ ] In the manifest, map each original logical artifact path to:
      bundled path,
      artifact kind,
      lane or run id,
      source command when known,
      SHA-256 digest,
      and validation status.
- [ ] Preserve report and summary references by either updating paths or
      recording explicit manifest mappings.
- [ ] Validate that every bundled artifact can be recovered or checked from the
      manifest.
- [ ] Re-run the relevant closeout/validation commands after bundling, or
      record why the manifest-level validation is sufficient.
- [ ] Record cleanup command(s), validation command(s), and before/after file
      counts.
- [ ] Confirm no scientific interpretation changes as a result of cleanup.
- [ ] Confirm no `src/*` files changed during cleanup.

### Completion Rule

Cleanup is complete only when the bundle manifest is enough to reconstruct the
evidence trail for Branch B through E3. Until then, expanded outputs should
remain available even if they are noisy in `git status`.

# Polarized Basin Loops Implementation Plan

## Purpose

This plan turns the polarized basin loop paper into a replayable experiment
program under:

```text
experiments/2026-05-N03-grc9v3-polarized-basin-loops/
```

The central question is:

```text
Can a single GRC9V3 basin sustain an internal conservative source-aspect /
sink-aspect loop without external source terms, topology adaptation, or
movement claims?
```

The experiment target is a **polarized basin loop**, not locomotion. Movement
belongs to the separate movement-ladders experiment.

## Scope

In scope:

- fixed-topology substrates;
- ring and small GRC9V3-backed fixtures;
- source-aspect and sink-aspect candidate regions inside one parent basin;
- forward-channel and return-channel masks;
- budget-conserving initialization and perturbation lanes;
- loop observables, gates, and reports;
- null controls and reversed source/sink controls;
- report schema `grc9v3_polarized_basin_loop_report_v1`.

Out of scope for this experiment:

- external source or sink terms;
- topology growth, pruning, spark refinement, or adaptive graph movement;
- identity fission claims;
- locomotion, movement, agency, or goal-seeking claims;
- reusable runtime changes in `src/pygrc` unless promoted through a separate
  repo-level implementation task.

## Core-Library Stop Rule

This experiment track may consume existing library APIs, but it must not modify
`src/*` or change `src/pygrc` runtime semantics.

If an implementation step appears to require a core-library change, stop the
experiment, record the missing capability, and request explicit approval for a
separate core-library task. Do not hide core runtime changes inside the
experiment track.

## Runtime Execution Contract

Fixed topology is an execution-surface requirement, not only a theoretical
scope statement. The first implementation must either use an explicit
experiment-local fixed-topology runner or prove that a full `GRC9V3.step()` run
behaved as fixed topology at every step.

The default runner contract is:

```text
runner_mode = "fixed_topology_continuity_runner"
```

Allowed runtime surfaces:

```text
rebuild_differential_state()
rebuild_transport_state()
apply_continuity()
enforce_quadrature_budget()
rebuild_identity_state()
compute_observables()
```

Disallowed in the first implementation pass:

```text
apply_hybrid_sparks()
apply_growth()
apply_boundary_behavior()
mechanical_expansion
node_birth
node_pruning
```

The non-default full-step escape hatch is allowed only when the report proves:

```text
all topology-changing features are disabled or no-op;
node and edge counts are unchanged at every step;
topology event logs are empty;
budget correction magnitude is reported;
runner provenance records the exact methods or phases used.
```

The first pass should prefer the fixed-topology continuity runner. A full
`GRC9V3.step()` run can be used only as a separately named execution surface.

## Evidence Contract

Every positive claim must be reconstructable from experiment artifacts.

Required evidence surfaces:

- node coherence histories;
- region mass histories for source-aspect and sink-aspect;
- measured source-like export and sink-like import roles;
- forward and return flux summaries;
- fixed-topology audit;
- polarity score;
- closure score;
- phase relation / phase-lock evidence;
- budget before/after and maximum budget error;
- parent-basin continuity evidence;
- null-lane comparison evidence.

The experiment may use existing `GRC9V3` and `LGRC9V3` library surfaces, but it
must not change runtime semantics to make a lane pass.

Every report must include runner provenance:

```json
{
  "model_family": "GRC9V3",
  "runner_mode": "fixed_topology_continuity_runner",
  "called_methods": [],
  "spark_enabled": false,
  "growth_enabled": false,
  "boundary_behavior_enabled": false,
  "birth_enabled": false,
  "runtime_semantics_changed": false
}
```

## Control Matrix

The first implementation must preserve the README controls as explicit run
variants or post-hoc checks. A run cannot support a strong L4 claim unless the
required controls for that claim are present or explicitly blocked.

| Control | Type | Purpose | Claim impact |
|---|---|---|---|
| `uniform_ring` / `U0` | runtime null | ensures no loop appears from numerical drift | required before any positive claim |
| `symmetric_bump` / `U1` | runtime null | checks basin structure without polarity | required before L4 |
| `symmetric_closed_substrate` / `U2` | runtime null | checks closed path without measured polarity | required before L4 |
| `reversed_source_sink` | runtime control | tests directionality | required before L4 |
| `shuffled_conductance` | runtime or classifier control | tests dependence on intended channel structure | required before strong L4 |
| `zero_flux_reset` | runtime initialization control | checks whether inherited transport state seeds the loop | required for snapshot/replay lanes; optional for fresh rebuild-only lanes |
| `budget_projection_disabled_dry_run` | diagnostic dry run | checks whether projection hides drift | diagnostic only; cannot support positive conservation claims |
| `randomized_labels_posthoc` | post-hoc classifier control | verifies classification is state-derived, not label-derived | required classifier sanity check before L4 |
| `topology_disabled` | runtime config/audit | keeps loop evidence separate from topology adaptation | required for every first-pass run |

The shuffled-conductance control must declare the controlled surface:

```text
shuffled_conductance_surface =
    "initial_fixture_base_conductance"
  | "per_tick_rebuilt_base_conductance"
  | "channel_mask_assignment"
  | "posthoc_flux_series_assignment"
```

Only `initial_fixture_base_conductance` and
`per_tick_rebuilt_base_conductance` are runtime controls. The channel-mask and
post-hoc flux-series forms are classifier controls and must be labeled as
analysis controls, not altered dynamics.

## Metric Configuration

All thresholds are run configuration, not hidden classifier constants. The
first deterministic classifier should record:

```json
{
  "n_cycles_min": 3,
  "washout_steps": 10,
  "min_eval_steps": 100,
  "theta_export": 0.0,
  "theta_import": 0.0,
  "theta_mass": 0.0,
  "theta_null_margin": 0.0,
  "phase_lock_min": 0.0,
  "phase_cascade_score_min": 0.0
}
```

The zero values above are placeholders for explicit calibration, not final
scientific thresholds. Every run report must serialize the actual configured
values. L4 is blocked if `n_cycles_min`, evaluation window, or positive
thresholds are unavailable.

## Loop Ladder

The implementation classifies runs by the paper's L0-L6 ladder:

| Level | Meaning | Experiment claim |
|---|---|---|
| L0 | no persistent source/sink polarity | no loop evidence |
| L1 | transient polarity | polarity candidate |
| L2 | paired source/sink aspects | internal polarity observed |
| L3 | return-path refill | closed redistributive path candidate |
| L4 | repeated conserved cycle | conserved internal loop |
| L5 | self-regulating cycle | pulse-generator candidate |
| L6 | boundary-couplable loop | locomotion precursor only |

The first implementation target is L0-L4. L5/L6 remain follow-up surfaces
unless L4 is stable and reproducible.

Later branches changed the execution-surface boundary. The native
fixed-topology GRC9V3 proposal-flux surface remained negative, but the
packetized LGRC path established an L5-like self-rearming packet pulse:
D2.3 first as an experiment-local prototype, and E3 later as a native LGRC9V3
D2.3-equivalent runtime surface. This resolves L5 only for native LGRC9V3
packetized causal execution. It does not resolve L5 for synchronous GRC9V3
proposal flux, and it does not open L6 movement or boundary-coupling claims.

## Experiment Lanes

Initial lanes:

| Lane | Meaning | Required role |
|---|---|---|
| U | uniform/null | no loop should appear except numerical artifacts |
| S | structured initialization | tests whether source/sink-like asymmetry can form a loop |
| K | one-time kick | tests whether a conserved perturbation can initiate a loop |
| R | repeated scheduled zero-sum pulses | steerability control, not intrinsic loop evidence |
| T | state-triggered redistribution | feedback/self-regulation candidate |
| F | free-after-trigger | persistence after one trigger |

The first tranche focuses on U/S/K. R/T/F are only promoted after the core
L0-L4 classifier is stable.

## Candidate Regions Versus Measured Roles

Source/sink masks are candidate regions, not results. A run only earns
source/sink evidence when measured net flux confirms export/import roles over
the evaluation window.

The experiment's `source_aspect_nodes` and `sink_aspect_nodes` are polarity-role
candidate masks. They are not automatically the same as `GRC9V3State.sink_set`
or identity-basin sinks. The report must state whether any runtime
`sink_set`/`basins` evidence was used, and it must not infer source/sink
polarity from mask labels alone.

Use the signed region export:

```text
export(R, t) = sum_{i in R, j not in R} J_ij(t)
```

and:

```text
import(R, t) = -export(R, t)
```

Then:

```text
R_s is source-like if mean_W export(R_s, t) > theta_export
R_k is sink-like if mean_W import(R_k, t) > theta_import
```

If source/sink roles cannot be measured, the claim ceiling is no polarity
claim, even if the fixture contains source/sink candidate masks.

For implementation-backed runs, region export must be reconstructable from
edge-level `PortEdge.flux_uv` evidence, not only from node summaries. Use the
runtime orientation convention:

```text
oriented_flux(edge, node) =
    +flux_uv if node == edge.u
    -flux_uv if node == edge.v
```

Then compute export over boundary edges incident to the region. The artifact
should retain the edge endpoint orientation, port ids, and `flux_uv` values
used for the calculation.

Role evidence should include mass-change consistency before budget correction:

```text
source-like:
    mean_W export(source_aspect) > theta_export
    and mean_W Delta C_source_pre_budget < -theta_mass

sink-like:
    mean_W import(sink_aspect) > theta_import
    and mean_W Delta C_sink_pre_budget > theta_mass
```

Post-budget mass changes should be reported separately so projection or budget
correction cannot silently create the apparent role.

## Measurement Phase Contract

Each step or runner tick must declare the measurement phases used for evidence.
The default fixed-topology runner should expose:

```text
C_pre
transport_state / flux_uv
continuity_delta
C_post_continuity
budget_correction
C_post_budget
diagnostics
```

Flux-role evidence is measured from the transport/flux surface. Mass-change
role consistency is measured from `C_pre` to `C_post_continuity`; corrected
mass evidence is reported separately after budget enforcement.

## Canonical Gates

### Conservation Gate

```text
max_k |B(k) - B(0)| < eps_budget
```

where:

```text
B(k) = sum_i C_i(k)
```

for unit-measure runs, or the configured node-measure variant when active.

### Single-Parent-Basin Gate

Source-aspect and sink-aspect regions must remain inside the same tracked
parent basin over the evaluated window. If a split/refinement occurs, the run
is not loop-positive for this experiment.

Allowed evidence modes:

```text
same_parent_basin_mode = "flux_successor_basin"
same_parent_basin_mode = "configured_parent_region_only"
same_parent_basin_mode = "unavailable_blocked"
```

`flux_successor_basin` supports full L-positive claims. The configured-parent
mode supports only candidate loop claims. If neither is available, the
same-parent-basin gate is blocked.

### Polarity Gate

Persistent source/sink polarity requires export bias from the source-aspect
and import bias into the sink-aspect over a declared window.

### Return Gate

The sink-aspect intake must be followed by detectable return flux that refills
the source-aspect through the declared return channel.

Separate three closure notions:

| Gate | Meaning |
|---|---|
| path-closure gate | forward and return masks form a connected closed route |
| flux-closure gate | measured return flux follows sink intake |
| cycle gate | source/sink masses and fluxes repeat with phase relation |

A ring or closed path only satisfies the path-closure gate. L3/L4 require
measured flux closure and cycle evidence.

### Repetition Gate

L4 requires at least `n_cycles` repeated conserved cycles under the budget
gate.

The default first-pass value is:

```text
n_cycles_min = 3
```

This is a minimum deterministic classifier parameter. It may be changed only
through run configuration and must be serialized in the report.

### Phase-Lock Gate

The first phase-lock metric may be simple but must be explicit. A minimum
acceptable definition uses lagged correlations:

```text
Delta_t_S_to_K =
    argmax_tau corr(-Delta C_source(t), Delta C_sink(t + tau))

Delta_t_K_to_S =
    argmax_tau corr(-Delta C_sink(t), Delta C_source(t + tau))
```

`phase_lock` should combine correlation magnitude, stable lag sign, and repeat
cycle count. The exact formula can be experiment-local, but it must be written
to the report metadata.

Pairwise source/sink lag correlation is a submetric, not the full loop signal.
L4 should also compute an ordered phase-cascade metric for the sequence:

```text
C_source drop
-> J_forward rise
-> C_sink rise
-> J_return rise
-> C_source refill
```

The report should include:

```json
{
  "phase_cascade": {
    "score": 0.0,
    "n_detected_cascades": 0,
    "mean_lag_source_drop_to_forward_flux": 0,
    "mean_lag_forward_flux_to_sink_rise": 0,
    "mean_lag_sink_rise_to_return_flux": 0,
    "mean_lag_return_flux_to_source_refill": 0,
    "passed": false
  }
}
```

This distinguishes an ordered redistributive loop from a generic oscillation.

### Washout Gate

K-lane evaluation must not count the injected kick transient itself as a loop.

```text
eval_window_start = kick_step + washout_steps
eval_window_len >= min_eval_steps
```

L4 cycles are counted only inside the evaluation window.

### Null Separation Gate

Positive lanes must exceed uniform/symmetric null lanes by a predefined margin
on polarity, closure, and phase-lock metrics.

Required null tiers:

| Null | Purpose |
|---|---|
| U0 uniform | no structure, no loop |
| U1 symmetric bump | basin exists, no polarity |
| U2 symmetric closed substrate/masks | closed path exists, no source/sink polarity |

U2 prevents a closed ring or corridor from being mistaken for a measured
conservative loop.

### Source/Sink Reversal Gate

Reversed source/sink controls must be classified as one of:

| Outcome | Meaning |
|---|---|
| antisymmetric pass | reversed lane reverses polarity/phase as expected |
| substrate-biased pass | reversed lane weakens/fails with a declared fixture asymmetry reason |
| failure | reversed lane reports the same source/sink direction without a fixture reason |

## Report Schema

Each run should produce one machine-readable report under `outputs/` and one
human-readable report under `reports/`.

Schema name:

```text
grc9v3_polarized_basin_loop_report_v1
```

Minimum required fields:

```json
{
  "schema": "grc9v3_polarized_basin_loop_report_v1",
  "run_id": "",
  "fixture_id": "",
  "lane": "U|S|K|R|T|F",
  "metric_config": {
    "n_cycles_min": 3,
    "washout_steps": 10,
    "min_eval_steps": 100,
    "theta_export": 0.0,
    "theta_import": 0.0,
    "theta_mass": 0.0,
    "theta_null_margin": 0.0,
    "phase_lock_min": 0.0,
    "phase_cascade_score_min": 0.0
  },
  "runtime": {
    "model_family": "GRC9V3",
    "runner_mode": "fixed_topology_continuity_runner|full_step_runner",
    "called_methods": [],
    "topology_events_enabled": false,
    "spark_enabled": false,
    "growth_enabled": false,
    "boundary_behavior_enabled": false,
    "birth_enabled": false,
    "runtime_semantics_changed": false,
    "measurement_phases": [
      "C_pre",
      "transport_state_flux_uv",
      "continuity_delta",
      "C_post_continuity",
      "budget_correction",
      "C_post_budget",
      "diagnostics"
    ]
  },
  "budget": {
    "initial": 0.0,
    "final": 0.0,
    "before_continuity": 0.0,
    "after_continuity": 0.0,
    "after_correction": 0.0,
    "error_pre_correction": 0.0,
    "error_post_correction": 0.0,
    "correction_method": "",
    "correction_magnitude": 0.0,
    "simplex_projection_count": 0,
    "uniform_shift_count": 0,
    "max_correction_magnitude": 0.0,
    "mean_correction_magnitude": 0.0,
    "max_abs_error": 0.0,
    "passed": false
  },
  "topology": {
    "initial_node_count": 0,
    "final_node_count": 0,
    "initial_edge_count": 0,
    "final_edge_count": 0,
    "changed": false,
    "passed_fixed_topology_gate": false,
    "topology_event_count": 0,
    "blocked_topology_event_kinds": [],
    "mechanical_expansion_count": 0,
    "growth_count": 0,
    "pruning_count": 0,
    "boundary_birth_count": 0,
    "spark_event_count": 0
  },
  "regions": {
    "parent_basin_id": "",
    "same_parent_basin_mode": "flux_successor_basin|configured_parent_region_only|unavailable_blocked",
    "source_aspect_nodes": [],
    "sink_aspect_nodes": [],
    "forward_channel_edges": [],
    "return_channel_edges": []
  },
  "role_evidence": {
    "source_export_mean": 0.0,
    "sink_import_mean": 0.0,
    "source_delta_c_pre_budget_mean": 0.0,
    "sink_delta_c_pre_budget_mean": 0.0,
    "source_delta_c_post_budget_mean": 0.0,
    "sink_delta_c_post_budget_mean": 0.0,
    "source_like_measured": false,
    "sink_like_measured": false,
    "reversal_outcome": "antisymmetric_pass|substrate_biased_pass|failure|not_run"
  },
  "timeseries": {
    "artifact_path": "",
    "artifact_digest": "",
    "C_source": "",
    "C_sink": "",
    "J_forward": "",
    "J_return": "",
    "source_export": "",
    "sink_import": "",
    "source_delta_C_pre_budget": "",
    "sink_delta_C_pre_budget": "",
    "polarity_score": "",
    "closure_score": "",
    "phase_lock": "",
    "phase_cascade_score": "",
    "budget_error_pre_correction": "",
    "budget_error_post_correction": ""
  },
  "controls": {
    "uniform_ring": "pass|fail|not_run",
    "symmetric_bump": "pass|fail|not_run",
    "symmetric_closed_substrate": "pass|fail|not_run",
    "reversed_source_sink": "pass|fail|not_run",
    "shuffled_conductance": "pass|fail|not_run",
    "shuffled_conductance_surface": "",
    "zero_flux_reset": "pass|fail|not_run|not_applicable",
    "budget_projection_disabled_dry_run": "pass|fail|not_run",
    "randomized_labels_posthoc": "pass|fail|not_run",
    "topology_disabled": "pass|fail"
  },
  "phase_cascade": {
    "score": 0.0,
    "n_detected_cascades": 0,
    "mean_lag_source_drop_to_forward_flux": 0,
    "mean_lag_forward_flux_to_sink_rise": 0,
    "mean_lag_sink_rise_to_return_flux": 0,
    "mean_lag_return_flux_to_source_refill": 0,
    "passed": false
  },
  "edge_evidence": {
    "orientation_convention": "flux_uv_positive_from_u_to_v",
    "fields": [
      "edge_id",
      "u",
      "v",
      "u_port",
      "v_port",
      "flux_uv",
      "base_conductance",
      "flux_coupling",
      "geometric_length",
      "temporal_delay"
    ]
  },
  "loop_metrics": {
    "polarity_score": 0.0,
    "closure_score": 0.0,
    "phase_lock": 0.0,
    "phase_lock_formula": "",
    "washout_steps": 0,
    "eval_window_start": 0,
    "eval_window_len": 0,
    "cycle_count": 0,
    "source_mass_amplitude": 0.0,
    "sink_mass_amplitude": 0.0
  },
  "ladder": {
    "level": "L0|L1|L2|L3|L4|L5|L6",
    "gates_passed": [],
    "gates_failed": []
  },
  "claim_ceiling": "",
  "blocked_claims": []
}
```

Large time-series arrays should live in separate JSONL, CSV, NPZ, or canonical
JSON artifacts. The run report should include paths and digests so the scalar
classification is reproducible from raw evidence.

## Runner Step Mapping

The README runner sequence maps to the default fixed-topology runner as:

| Paper/README step | Default runtime phase | Artifact surface |
|---|---|---|
| compute basin attributes | `rebuild_differential_state()` and `rebuild_identity_state()` | node summaries, basin evidence |
| compute local geometry / `K`-like state | `rebuild_differential_state()` | gradients, signed Hessian, node diagnostics |
| update conductances | `rebuild_transport_state()` | `base_conductance`, `flux_coupling` |
| compute potentials | `rebuild_transport_state()` | `potential` |
| compute antisymmetric flux | `rebuild_transport_state()` | `PortEdge.flux_uv` |
| update `C_i` by continuity | `apply_continuity()` | `C_post_continuity`, continuity delta |
| enforce budget | `enforce_quadrature_budget()` | correction audit |
| verify parent basin | `rebuild_identity_state()` plus experiment evidence mode | basin/parent evidence |
| compute source/sink summaries | experiment-local postprocessor | region export/import |
| compute loop scores | experiment-local postprocessor | metrics and time series |
| assign L-level | experiment-local classifier | report ladder fields |

The first implementation should use:

```text
canonical_fixture = "grc9v3_ported_ring_v1"
analysis_control_fixture = "simple_unported_ring_v1"
```

The simple ring is acceptable for synthetic metric tests. GRC9V3 evidence
should use the ported ring unless the run explicitly declares itself an
analysis/control fixture.

## Claim-Ceiling Downgrades

Reports should downgrade deterministically when evidence is missing.

| Evidence missing | Claim ceiling |
|---|---|
| budget audit | blocked |
| source/sink role measurement | no polarity claim |
| return-channel measurement | no loop claim |
| cycle count | at most L3 |
| null separation | candidate only |
| same-parent-basin evidence | candidate loop only |
| fixed-topology audit | blocked for this first experiment pass |

## Implementation Iterations

### Iteration 0: Scope And Replay Contract

Create the local plan/checklist, lock fixed-topology scope, and record that
movement/topology claims are out of scope.

### Iteration 1: Artifact Surface Inventory

Map required observables to available runtime artifacts or derived values.
Record blocked surfaces explicitly.

This corresponds to README tranche `L1.2`/`L1.3` inventory preparation.

### Iteration 2: Fixed-Topology Fixture Design

Define ring/chain fixture conventions, region masks, source/sink candidates,
forward/return channel masks, and budget-conserving initialization.

This corresponds to README tranche `L1.0` and `L1.1`.

Canonical ring initialization should be explicit. For ring node coordinate:

```text
theta_i = 2*pi*i/N
```

use a localized bump:

```text
C_i = C_0 + A exp(kappa cos(theta_i - theta_0))
```

and optional small local source/sink polarity modulation:

```text
C_i <- C_i + epsilon_s m_s(i) - epsilon_k m_k(i)
```

Then project/renormalize to:

```text
C_i >= 0
sum_i C_i = B
```

This separates structured static asymmetry from a one-time zero-sum kick and
from repeated pulse forcing.

### Iteration 3: Loop Observable Library

Implement experiment-local post-processing for region masses, forward/return
flux, polarity score, closure score, phase relation, cycle count, and budget
audit.

This corresponds to README tranche `L1.2`, `L1.3`, and the report-schema
preparation in `L1.8`.

### Iteration 4: Null And Structured Lanes

Run U and S lanes. Confirm uniform/symmetric nulls do not produce false loop
positives and structured lanes produce interpretable evidence or fail cleanly.

This corresponds to README tranche `L1.4` and `L1.5`.

### Iteration 5: One-Time Kick Lane

Run K lanes with zero-sum perturbations and reversed-direction controls.

This corresponds to README tranche `L1.6`.

### Iteration 6: Fail-Closed Classifier And Negative Tranche Closeout

Freeze report/schema behavior for negative, blocked, and candidate outcomes.
Do not promote L4 claims from the first canonical fixture. The first tranche is
closed as a negative fixed-topology result unless later diagnostic branches are
opened explicitly.

This corresponds to README tranche `L1.7` and `L1.8`.

### Iteration 7: Reports And Handoff

Generate human-readable reports, blocked-observation notes, and a handoff that
records what can and cannot be claimed from the negative first tranche.

### Branch B: Diagnostic Sweeps

Diagnostic sweeps are a new branch, not a continuation of the first positive
claim path. Their purpose is to determine which condition failed, not to tune
the first tranche into a pass.

Possible axes:

- amplitude sweep for S modulation and K kick strength;
- source/sink mask width sweep;
- ring size sweep;
- conductance asymmetry or channel-structure sweep;
- source/sink spacing sweep;
- channel attenuation / intermediate-node dissipation audit;
- forward/return asymmetry sweep;
- budget correction magnitude audit;
- transport rebuild behavior audit.

Claim ceiling:

```text
diagnostic sensitivity map, not positive loop claim
```

Any diagnostic result that appears positive must be promoted into a new named
fixture/tranche with fresh nulls and controls before it can support a loop
claim.

Recommended first diagnostic tranche:

```text
B1: amplitude/mask/scale/spacing diagnostics
Claim ceiling: diagnostic sensitivity map only
No positive loop claim allowed
No classifier/threshold tuning
No src/* changes
```

Execution order:

1. `B1.1` amplitude sweep
   - S modulation: `0.005`, `0.01`, `0.02`, `0.04`;
   - K kick: `0.005`, `0.01`, `0.02`, `0.04`.
2. `B1.2` mask width sweep
   - source/sink aspect width: `1`, `2`, `3` nodes.
3. `B1.3` ring size sweep
   - ring sizes: `12`, `24`, `48` nodes.
4. `B1.4` source/sink spacing sweep
   - half-ring, third-ring, quarter-ring separation.
5. `B1.5` transport rebuild audit
   - compare initialized polarity against post-`rebuild_transport_state`
     conductance, potential, flux, and role-gate surfaces.

Per-row diagnostics:

- source/sink role gates;
- raw cascade count;
- role-gated cascade count;
- forward/return flux signs;
- budget correction magnitude;
- topology audit;
- transport erase/preserve metrics.

Interpretation rule:

```text
If no sweep produces role-gated cascades:
    likely fixture/mechanism mismatch; move to Branch C.

If some sweep produces role-gated cascades:
    do not claim success.
    promote that condition into a new named fixture/tranche with fresh
    U/S/K/null/reversal controls.
```

B1 execution record:

```text
Command:
    .venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/run_b1_diagnostic_sweeps.py

Result:
    status = pass
    diagnostic rows = 26
    promising diagnostic rows = 0
    max raw cascades = 13
    max role-gated cascades = 0
    topology changed = false
    budget failures = 0
    positive loop claims allowed = false

Interpretation:
    B1 did not identify a role-gated loop-producing condition across
    amplitude, mask-width, ring-size, or spacing sweeps. This supports the
    diagnostic interpretation `no_role_gated_cascades_detected_fixture_
    mechanism_mismatch_likely`, not a loop claim.
```

Follow-up diagnostic:

```text
B2: channel attenuation / intermediate-node dissipation audit
Claim ceiling: channel attenuation diagnostic only
No positive loop claim allowed
No classifier/threshold tuning
No src/* changes
```

B2 asks whether coherence exported from the source survives across intermediate
channel nodes as directed channel flux toward the sink. It uses a 16-node
ported ring with two-node source/sink masks and explicit source-to-sink gap
lengths:

```text
forward_gap_nodes = 0, 1, 2, 4, 6
lanes = S, K
```

B2 execution record:

```text
Command:
    .venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/run_b2_channel_attenuation.py

Result:
    status = pass
    diagnostic rows = 10
    topology changed = false
    budget failures = 0
    positive loop claims allowed = false

Observed:
    In the static S lane, longer source-to-sink gaps strongly attenuate early
    forward-channel flux before it reaches the sink. For gap 4 and gap 6,
    early last/first forward-edge mean-absolute flux ratios are approximately
    0.063 and 0.047, with early sink/source boundary ratios approximately
    0.046 and 0.049.

    In the K lane, the one-time kick produces broader relaxation and does not
    show the same early last-edge attenuation, but this still does not
    constitute loop evidence.

Interpretation:
    B2 supports the diagnostic concern that the plain ring behaves more like a
    local relaxation substrate than a directed loop substrate for static S
    initialization. Intermediate nodes can absorb/redistribute source export
    before paired sink-role evidence forms.
```

Follow-up diagnostic:

```text
B3: fixed-topology conductance corridor diagnostic
Claim ceiling: conductance corridor diagnostic only
No positive loop claim allowed
No classifier/threshold tuning
No src/* changes
```

B3 tests whether channel structure alone helps the same fixed-topology runner
preserve directed transport. It changes only in-memory fixture conductance:

```text
forward-channel boost:        1.5, 2.0, 4.0
return-channel boost:         1.5, 2.0, 4.0
balanced corridor boost:      1.5, 2.0, 4.0
asymmetric corridor boosts:   forward 4 / return 1.5, forward 1.5 / return 4
boundary gate boost:          source-exit and sink-entry edges x4
lanes:                        S, K
```

B3 execution record:

```text
Command:
    .venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/run_b3_conductance_corridor.py

Result:
    status = pass
    diagnostic rows = 24
    promising diagnostic rows = 0
    max raw cascades = 0
    max role-gated cascades = 0
    topology changed = false
    budget failures = 0
    positive loop claims allowed = false

Interpretation:
    B3 did not show that fixed-topology conductance corridors alone create
    measured paired roles or ordered loop evidence under the current S/K
    initialization surfaces. The failure is therefore not explained only by
    uniform channel conductance.
```

### Branch C: Fixture/Theory Redesign

If diagnostic sweeps show that the two-aspect plain ring is understructured,
open a separate redesign branch. Possible redesign surfaces include larger
rings, buffered source/sink masks, persistent channel conductance structure,
delayed transport/memory-like channels, or multi-pole phase cycling.

This branch must not silently replace the first tranche. It starts a new
experiment surface with its own fixture manifest and claim ceiling.

Branch B closeout:

```text
Branch B current diagnostic conclusion:
    No tested amplitude, mask, scale, spacing, attenuation, or fixed
    conductance-corridor diagnostic produced role-gated cascades.

    B1: 26 rows, 0 promising rows, max role-gated cascades = 0.
    B2: static S source export attenuates/redistributes across intermediate
        nodes before paired sink-role evidence forms.
    B3: 24 rows, 0 promising rows, max raw cascades = 0, max role-gated
        cascades = 0.

Interpretation:
    The first two-aspect homogeneous/plain ported ring behaves like a local
    relaxation/redistribution substrate, not a directed conserved loop
    substrate under current fixed-topology continuity dynamics.
```

Recommended Branch C opening:

```text
C1: delayed/accumulator channel substrate
```

C1 question:

```text
Can a conserved fixed-topology basin sustain source/sink cycling if forward
and return channels include explicit delay/accumulator states, rather than
instantaneous homogeneous ring continuity?
```

C1 remains fail-closed:

- no external source/sink terms;
- budget conserved over node coherence plus any explicit accumulator/channel
  storage;
- topology fixed unless a later branch explicitly opens topology adaptation;
- roles measured from runtime evidence, not masks;
- raw cascades remain separate from role-gated cascades;
- fresh U/S/K/null/reversal controls are required;
- no movement claim;
- no `src/*` changes without explicit separate approval.

Secondary Branch C surfaces:

- `C2`: two-compartment/reservoir-conduit fixture:
  source reservoir, forward conduit, sink reservoir, return conduit;
- `C3`: theory-justified three-pole phase substrate, only if two-pole cycling
  is judged underdetermined;
- `C4`: full `GRC9V3.step()` execution surface, only as a separate named
  surface with adaptive topology/spark/boundary stages explicitly audited.

C1 execution record:

```text
Command:
    .venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/run_c1_delayed_accumulator.py

Result:
    status = pass
    rows = 15
    candidate rows = 0
    topology changed = false
    max nodes+in-flight budget error <= 2.23e-16
    full L-positive claims allowed = false

Observed:
    U0/U2 remain clean.
    S/K/K_reversed rows produce measured paired source/sink roles under
    delayed accumulator transport.
    No row produces raw cascades or role-gated cascades.

Classification:
    c1_no_candidate_loop_rows_observed

Interpretation:
    C1 resolves part of the B-branch failure by allowing conserved delayed
    source/sink transport with explicit in-flight storage. However, the first
    accumulator policy does not yet produce ordered repeated cycles. The next
    redesign question is no longer only "can roles form?", but "what policy
    turns paired delayed transport into phase-ordered cycling?"
```

### C1-B: Accumulator Release Policy Diagnostics

C1-B opens a narrower question after the first delayed-accumulator result:

```text
Given a conserved delayed accumulator substrate that can produce paired
source/sink transport, what release policy produces ordered recurrent cycling
rather than one-shot delayed transfer or monotone relaxation?
```

The distinction is:

| Level | Meaning |
| --- | --- |
| paired delayed transport | source exports, sink imports after delay |
| return-enabled transport | sink/return path can refill source |
| phase-ordered cycle | repeated source drop -> forward release -> sink rise -> return release -> source refill |

C1 reached paired delayed transport, but not phase-ordered cycling.

Release policy surfaces:

1. `C1-B.1` passive leaky accumulator
   - `A_next = (1 - leak) A + input`;
   - `release = leak * A`;
   - sweep `leak = 0.05, 0.1, 0.2, 0.4`;
   - expected role: smoothing/control surface.
2. `C1-B.2` threshold release
   - release only when accumulator exceeds `theta_release`;
   - sweep `theta_release` and `release_fraction`.
3. `C1-B.3` hysteretic release
   - open when `A > theta_high`;
   - close when `A < theta_low`;
   - sweep `theta_low/theta_high` and release fraction.
4. `C1-B.4` hysteresis plus refractory period
   - after release, channel cannot release again for `r` steps;
   - sweep `refractory_steps = 5, 10, 20`.
5. `C1-B.5` coupled forward/return gate
   - forward and return channels do not fire independently;
   - sink intake and source refill participate in reset/enable conditions.

Required controls:

- no-delay accumulator;
- passive leak only;
- threshold shuffled;
- forward-only accumulator;
- return-only accumulator;
- randomized release phase;
- accumulator budget audit.

Claim ceiling:

```text
diagnostic release-policy sensitivity map, not positive loop claim
```

If one release policy produces role-gated repeated cycles, it must be promoted
into a new named tranche with fresh controls, for example:

```text
N03-C1R1-delayed-accumulator-loop-v1
```

Success target for a future promoted tranche:

```text
source accumulator fills
source/source-aspect exports
forward accumulator releases
sink-aspect imports
sink accumulator fills
return accumulator releases
source-aspect refills
source-side reset condition restored
```

Promotion requirements:

- role-gated cascades >= `n_cycles_min`;
- budget including accumulator state conserved;
- nulls do not show the same cycle;
- forward-only and return-only controls fail;
- phase order survives small perturbation.

C1-B execution record:

```text
Command:
    .venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/run_c1b_release_policy_diagnostics.py

Result:
    status = pass
    rows = 51
    promising rows = 0
    max raw cascades = 0
    max role-gated cascades = 0
    topology changed = false
    accumulator budget failures = 0
    positive loop claims allowed = false

Policies tested:
    no-delay control;
    passive leak: 0.05, 0.1, 0.2, 0.4;
    threshold release;
    hysteretic release;
    hysteretic release with refractory periods 5, 10, 20;
    coupled forward/return hysteretic-refractory gate;
    forward-only and return-only controls.

Observed:
    Most S/K release-policy rows form paired source/sink roles.
    No tested release policy produces raw cascades or role-gated cascades.
    U0/U2 controls remain clean under the coupled serious policy.

Classification:
    release_policy_no_role_gated_cycles_observed

Interpretation:
    C1-B confirms that release timing alone, when driven by current GRC9V3 flux
    proposals and local accumulator state, does not produce recurrent
    phase-ordered loop cycling. The missing mechanism is likely not simply
    "delay plus thresholded release"; it may require an explicit cyclic
    reset/drive condition, a compartmental reservoir-conduit substrate, or a
    theory-level decision that two-pole cycling is underdetermined without an
    additional phase state.
```

C1 closeout:

```text
C1 result:
    Delayed accumulator transport and local release policies resolved neither
    the phase-order nor recurrence problem. Across leak, threshold, hysteresis,
    refractory, and coupled-release variants, no recurrent role-gated phase
    cycle was observed under the current GRC9V3 flux proposal surface.

Remaining failure mode:
    absence of endogenous loop-phase organization, not merely lack of delay,
    storage, or paired source/sink transport.
```

Next redesign surface:

```text
C3: three-pole phase substrate
```

C3 question:

```text
Is the two-pole source/sink loop underdetermined because it lacks an explicit
intermediate phase state, and can a conserved three-pole substrate produce
ordered recurrent phase cycling under fixed topology?
```

C3 opens as a new named surface. It must not inherit positive evidence from C1.
It should start with fresh nulls and controls:

- three candidate pole regions `R1`, `R2`, `R3`;
- directed pole-interaction matrix `P_mn(t)`;
- phase-pattern target:
  `R1 -> R2 -> R3 -> R1`;
- budget conservation over node coherence and any explicit accumulator state;
- fixed topology;
- no external source/sink terms;
- no movement claim;
- no `src/*` changes without explicit separate approval.

C3 execution split:

```text
C3.1 Three-pole fixture and masks
C3.2 Three-pole observables
C3.3 Synthetic validator
C3.4 Runtime fixed-topology runner
C3.5 Accumulator/phase-channel runner
C3.6 Controls and closeout
```

`C3.1` defines the fixture surface:

- fixed topology;
- candidate pole masks `R1`, `R2`, `R3`;
- channel arcs `R1 -> R2`, `R2 -> R3`, `R3 -> R1`;
- null/reversal controls;
- phase target `R1 -> R2 -> R3 -> R1`.

`C3.2` defines observables:

- pole masses `C_1(t)`, `C_2(t)`, `C_3(t)`;
- pole export/import roles;
- pole-interaction matrix `P_mn(t)`;
- network closure score;
- phase-pattern score;
- three-stage cascade count.

`C3.3` validates the classifier on synthetic traces:

- accepts ordered `R1 -> R2 -> R3 -> R1` cycles;
- rejects scrambled phase order;
- rejects two-pole-only traces;
- rejects budget drift;
- rejects randomized labels.

`C3.4` runs the real fixed-topology GRC9V3 continuity surface on the
three-pole fixture. It keeps `src/*` untouched and does not call adaptive
topology stages.

`C3.5` opens a three-channel accumulator/phase-channel runner only if C3.4 is
negative or insufficient. Budget must include node coherence plus accumulator
state.

`C3.6` produces controls and closeout:

- nulls;
- shuffled pole labels;
- disabled channel;
- reversed phase order;
- budget audit;
- topology audit;
- closeout classification.

Claim ceiling through C3.1-C3.6:

```text
three-pole diagnostic surface, not positive loop claim
```

Promotion rule:

```text
If a C3 diagnostic produces recurrent role-gated three-pole cycles, promote it
into a new named tranche with fresh controls. Do not promote directly from the
diagnostic sweep.
```

C3.1-C3.4 execution record:

```text
Command:
    .venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/run_c3_three_pole_diagnostic.py

Result:
    status = pass
    classification = c3_fixed_topology_no_three_pole_candidate_rows
    runtime candidate lanes = []
    topology changed = false
    budget failures = 0

Synthetic validator:
    ordered R1 -> R2 -> R3 -> R1 cycles:
        raw cascades = 4
        role-gated cascades = 4
        budget passed = true
    scrambled phase order:
        role-gated cascades = 0
    two-pole-only trace:
        role-gated cascades = 0
    budget-drift trace:
        budget passed = false

Runtime fixed-topology result:
    U0, U3, P, P_reversed:
        network closure = 0
        raw three-pole cascades = 0
        role-gated three-pole cascades = 0
        candidate = false

Interpretation:
    The C3 observable/classifier can detect ordered three-pole cycles in
    controlled traces, but the real fixed-topology GRC9V3 continuity surface
    does not generate three-pole network closure or phase cycling from the
    first three-pole fixture. C3.5 is now justified as a separate
    three-channel accumulator/phase-channel surface.
```

C3.5 execution record:

```text
Command:
    .venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/run_c3_5_three_channel_accumulator.py

Result:
    status = pass
    classification = c3_5_no_three_pole_candidate_conditions
    rows = 14
    promising rows = 0
    max network closure = 0
    max raw three-pole cascades = 0
    max role-gated three-pole cascades = 0
    topology changed = false
    accumulator budget failures = 0

Policies tested:
    parallel three-channel delay: 3, 6;
    cyclic phase delay: 3, 6, 10;
    cyclic phase delay with refractory: delay 6, refractory 10.

Controls:
    P_reversed;
    U0;
    U3.

Interpretation:
    Three-channel accumulator storage produces small in-flight amounts, but
    under the current GRC9V3 flux proposal surface it does not generate
    three-pole network closure. The failure remains generative: the runtime
    does not produce the channel sequence R1 -> R2 -> R3 -> R1 without a more
    explicit phase drive, compartmental mechanism, or different theory surface.
```

C3 closeout:

```text
C3 result:
    The three-pole fixed-topology accumulator fixture validated the multi-pole
    fixture path, classifier, and accumulator budget accounting, but did not
    produce the ordered channel sequence R1 -> R2 -> R3 -> R1.

Narrowed failure mode:
    The issue is not only two-pole underdetermination, missing delay, or lack
    of accumulator storage. Under the current GRC9V3 proposal surface, the
    system does not generate directed cyclic channel sequencing on the tested
    fixed-topology substrates.
```

Updated negative-evidence ladder:

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

Next branch:

```text
D1: circulatory proposal audit
```

D1 question:

```text
Can the current GRC9V3 proposal surface produce any nonzero loop circulation
around a closed channel, independent of source/sink masks?
```

D1 target metric:

```text
loop_circulation(t) = signed sum of flux_uv around a declared closed cycle
```

D1 interpretation:

```text
If signed loop circulation is absent or always decays in fixed-topology cases,
then fixed-topology GRC9V3 continuity is best understood as a conservative
relaxation substrate, not an oscillator/circulator, unless a new proposal term,
phase controller, adaptive runtime stage, or causal execution layer is opened.
```

D1 execution record:

```text
Command:
    .venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/run_d1_circulatory_proposal_audit.py

Result:
    status = pass
    classification = d1_weak_residual_loop_circulation_observed
    max_abs_loop_circulation = 0.0070727893817062425
    max_abs_normalized_circulation = 0.006041388204739038
    topology changed = false
    budget failures = 0

Scenarios:
    original ring: U0, U1, S, K;
    deterministic ring profiles: sinusoid, traveling_phase_seed, sawtooth;
    three-pole fixture: U0, U3, P, P_reversed.

Observed:
    U0 and several symmetric/null cases have zero or numerical-near-zero
    circulation.

    Structured S and three-pole P/P_reversed show nonzero signed loop
    circulation, but the normalized circulation is weak: at most about 0.006
    of total absolute edge flux.

Interpretation:
    The current GRC9V3 proposal surface can produce weak residual signed loop
    imbalance on asymmetric fixtures, but D1 does not show material
    self-sustaining circulatory proposal dynamics. This supports the broader
    conclusion that fixed-topology GRC9V3 continuity remains primarily a
    conservative relaxation substrate under the tested surfaces.
```

D1 bounded interpretation:

```text
D1 did not show absence of circulation.
D1 showed weak residual circulation only.
```

The key normalized metric is:

```text
abs(sum_cycle J_e) / sum_cycle abs(J_e) ~= 0.006
```

This means the signed loop imbalance is about 0.6% of total absolute edge-flux
activity in the strongest observed case. The current proposal surface is not
perfectly circulation-free, but its observed circulation component is too weak
or residual to organize the missing phase cycle.

Updated failure mode:

```text
GRC9V3 fixed-topology continuity can produce small asymmetric circulation
residue, but not a sufficiently strong, persistent, phase-organizing
circulatory mode under the tested fixtures.
```

D1b follow-up:

```text
D1b: persistence and coherence of residual circulation
```

D1b question:

```text
Is the weak residual circulation persistent, sign-stable, and correlated with
loop-role evidence, or is it transient/noisy relaxation residue?
```

D1b metrics:

- mean signed circulation;
- max absolute signed circulation;
- mean and max normalized circulation;
- sign persistence fraction;
- lag-1 autocorrelation;
- circulation decay rate;
- correlation with role/cascade evidence where available.

D1b interpretation:

```text
If residual circulation is transient, sign-unstable, or uncorrelated with loop
evidence, close the native fixed-topology proposal branch and open D2 as an
explicitly labeled conservative circulatory proposal prototype.

If residual circulation is stable but weak, D2 can target amplification or
preservation of the native residual component.
```

D1b result:

```text
Command:
    .venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/run_d1b_circulation_persistence.py

Output:
    outputs/d1b_circulation_persistence_report.json
    reports/d1b_circulation_persistence_report.md

Status:
    pass

Classification:
    d1b_stable_weak_residual_circulation

Material rows:
    none

Stable weak rows:
    d1_ring_s
```

D1b did not promote native GRC9V3 loop evidence. It shows that the strongest
D1 residual circulation is persistent and sign-stable in the structured
two-aspect S row, but remains below the material normalized threshold:

```text
d1_ring_s:
    mean signed circulation = -0.0024265037154406937
    max absolute signed circulation = 0.0070727893817062425
    mean absolute normalized circulation = 0.0021872230291446163
    max absolute normalized circulation = 0.006041388204739038
    sign persistence fraction = 1.0
    lag-1 autocorrelation = 0.9984405959734713
    late/early absolute-circulation ratio = 2.9245508068298265
```

The three-pole P/P_reversed rows show weak residual circulation below the
material threshold as well, but they are not sign-stable enough under this D1b
criterion:

```text
d1_three_pole_p:
    max absolute normalized circulation = 0.003058654627651635
    sign persistence fraction = 0.55

d1_three_pole_p_reversed:
    max absolute normalized circulation = 0.003058654627651635
    sign persistence fraction = 0.55
```

Updated D1/D1b conclusion:

```text
The native fixed-topology GRC9V3 proposal surface is not strictly
circulation-free. It can produce weak, partly coherent residual circulation on
structured fixtures. However, the observed residual remains below the material
circulation threshold and has not organized source/sink roles, closure, or
recurrent phase cycles. Treat it as a possible target for explicit prototype
amplification/preservation, not as native loop evidence.
```

D1c rotation follow-up:

```text
D1c: native port-rotation circulation audit
```

D1c question:

```text
Do native GRC9V3 port-rotation fixtures expose stronger loop circulation than
the direct source/sink channel fixtures tested in D1?
```

D1c is still a native fixed-topology audit. It changes the fixture and
measurement surface, not the proposal law:

```text
clockwise port cycle:
    1 -> 2 -> 3 -> 6 -> 9 -> 8 -> 7 -> 4 -> 1

counter-clockwise port cycle:
    reverse(clockwise)
```

D1c result:

```text
Command:
    .venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/run_d1c_port_rotation_audit.py

Output:
    outputs/d1c_port_rotation_audit.json
    reports/d1c_port_rotation_audit.md

Status:
    pass

Classification:
    d1c_weak_residual_port_rotation_circulation_observed

Material rows:
    none

Max absolute loop circulation:
    0.0036735167365173904

Max absolute normalized circulation:
    0.005365511110850774
```

D1c compared against the prior D1 direct/channel baseline:

```text
D1 direct/channel max absolute normalized circulation:
    0.006041388204739038

D1c port-rotation max absolute normalized circulation:
    0.005365511110850774
```

Observed:

```text
Uniform port-rotation control remains zero.
Port-rotation traveling-phase and reversed-phase rows produce weak residual
circulation.
No row reaches the material normalized threshold of 0.01.
The strongest port-rotation residual is slightly weaker than the strongest
prior direct/channel D1 residual.
```

Updated D1/D1b/D1c conclusion:

```text
Native fixed-topology GRC9V3 can produce weak residual circulation on both
direct channel fixtures and port-rotation fixtures. Port rotation does not
unlock a material loop-generating mode under the tested surfaces. The
remaining failure is not only direct-flow fixture bias; it is absence of a
strong endogenous circulatory proposal mode.
```

D1d initialized-flow follow-up:

```text
D1d: initial circulating-flux retention audit
```

D1d question:

```text
If every edge in the closed ring starts with clockwise/counter-clockwise
`flux_uv`, does native GRC9V3 preserve that initialized corridor flow, or does
`rebuild_transport_state()` overwrite it with potential-driven proposal flux?
```

D1d is still native fixed-topology GRC9V3. It initializes edge flux but does
not add edge storage, momentum, packets, accumulators, a circulatory proposal
term, or any `src/*` change.

D1d result:

```text
Command:
    .venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/run_d1d_initial_flux_retention.py

Output:
    outputs/d1d_initial_flux_retention.json
    reports/d1d_initial_flux_retention.md

Status:
    pass

Classification:
    d1d_initial_flux_erased_by_transport_rebuild

Retained rows:
    none

Material rows:
    none
```

Representative retention rows:

```text
d1d_uniform_clockwise_flux_0p05:
    initial loop circulation = 0.6000000000000001
    first rebuild loop circulation = 0.0
    first signed retention ratio = 0.0
    max normalized circulation after rebuild = 0.0

d1d_source_sink_clockwise_flux_0p05:
    initial loop circulation = 0.6000000000000001
    first rebuild loop circulation = 0.0
    first signed retention ratio = 0.0
    first absolute-flux retention ratio = 0.09933619270504468
    max normalized circulation after rebuild = 0.0

d1d_traveling_phase_seed_clockwise_flux_0p05:
    initial loop circulation = 0.6000000000000001
    first rebuild loop circulation = 6.954434341799928e-07
    first signed retention ratio = 1.1590723902999878e-06
    first absolute-flux retention ratio = 0.2933865757187918
    max normalized circulation after rebuild = 9.582625842412871e-05
```

Interpretation:

```text
Initialized edge `flux_uv` does not behave as persistent closed corridor flow
in native GRC9V3. The first transport rebuild effectively erases the imposed
signed loop circulation. Some asymmetric profiles retain or regenerate
absolute edge activity, but not the original signed circulation. Therefore
plain native GRC9V3 `flux_uv` is a recomputed proposal surface, not a
blood/vein-like edge-flow or momentum state.
```

Updated D1/D1b/D1c/D1d conclusion:

```text
The tested native fixed-topology GRC9V3 surfaces do not contain a material
closed-flow state. Direct channels, port rotations, and initialized full-ring
flux all reduce to weak residual or recomputed relaxation behavior. A
blood/vein-like conserved loop would need explicit edge/corridor coherence,
packets, accumulators, momentum, a circulatory proposal term, an adaptive
runtime stage, or a different causal execution layer.
```

D1e alternating-pole follow-up:

```text
D1e: alternating source/sink pole ring audit
```

D1e question:

```text
If the passive intermediate-node corridor is the failure point, does
distributing active source/sink-aspect regions around the whole ring create
stronger native cyclic circulation?
```

D1e fixture:

```text
S1 -> K2 -> S2 -> K1 -> S1

S1 = nodes [0, 1]
K2 = nodes [3, 4]
S2 = nodes [6, 7]
K1 = nodes [9, 10]
```

D1e still changes only the fixture/initialization surface. It does not add
role switching, propulsion, edge storage, a phase controller, a circulatory
proposal term, or any `src/*` change.

D1e result:

```text
Command:
    .venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/run_d1e_alternating_pole_ring.py

Output:
    outputs/d1e_alternating_pole_ring.json
    reports/d1e_alternating_pole_ring.md

Status:
    pass

Classification:
    d1e_partial_alternating_pole_evidence_only

Candidate rows:
    none

Role-pattern rows:
    d1e_alternating
    d1e_alternating_strong

Material rows:
    none

Max absolute normalized circulation:
    0.0014352682367625483
```

Representative observations:

```text
d1e_alternating:
    role pattern passed = true
    max normalized circulation = 0.0
    cycle proxy count = 0

d1e_alternating_strong:
    role pattern passed = true
    max normalized circulation = 0.0
    cycle proxy count = 0

d1e_traveling_four_pole:
    role pattern passed = false
    max normalized circulation = 0.0014352682367625483
    cycle proxy count = 0
```

Interpretation:

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

D1f mechanism-isolation follow-up:

```text
D1f: minimal handoff mechanism probes
```

D1f starts from the D1e result and adds one missing ingredient at a time. D1f
is explicitly experiment-local mechanism isolation, not native GRC9V3 evidence
and not a positive N03 loop claim.

D1f lanes:

```text
D1f1: D1e + explicit phase handoff
D1f2: D1e + edge/corridor storage
D1f3: D1e + momentum retention
D1f4: D1e + causal packet delay
D1f5: D1e + adaptive role handoff
```

D1f result:

```text
Command:
    .venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/run_d1f_minimal_handoff_mechanisms.py

Output:
    outputs/d1f_minimal_handoff_mechanisms.json
    reports/d1f_minimal_handoff_mechanisms.md

Status:
    pass

Classification:
    d1f_phase_and_closed_flow_positive_lanes_observed
```

Lane outcomes:

```text
D1f1 explicit phase handoff:
    phase cycles = 8
    positive surface = phase

D1f2 edge/corridor storage:
    phase cycles = 0
    positive surface = none
    note = storage alone creates one-way channel activity but not a closed loop

D1f3 momentum retention:
    phase cycles = 0
    simultaneous closed-flow steps = 140
    positive surface = closed-flow

D1f4 causal packet delay:
    phase cycles = 11
    positive surface = phase

D1f5 adaptive role handoff:
    phase cycles = 11
    positive surface = phase
```

D1f interpretation:

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

D2 selected framing:

```text
D2: conserved causal packet loop prototype
```

This replaces the earlier broad placeholder:

```text
old D2: conservative circulatory proposal prototype
```

The replacement is evidence-driven. D1f4 showed that causal packet delay is a
minimal sufficient mechanism for ordered phase cycles under conserved
experiment-local dynamics, and it is the closest tested surface to LGRC-style
in-flight coherence.

D2 selected scope:

```text
Promote D1f4 only.
Do not combine D1f1, D1f3, or D1f5 into D2.
```

D2 boundaries:

```text
D2 is not native GRC9V3 evidence.
D2 is not a core `src/*` change.
D2 is experiment-local first.
D2 budget is node coherence plus in-flight packet coherence.
D2 requires fresh nulls, reversal controls, and budget audits.
D2 positive results support packetized prototype evidence only.
```

Deferred D1f alternatives:

```text
D2-alt-phase-handoff:
    from D1f1 explicit phase handoff;
    deferred because it is more controller-like.

D2-alt-momentum:
    from D1f3 momentum retention;
    deferred because it produces continuous closed flow, not phase handoff.

D2-alt-adaptive-handoff:
    from D1f5 adaptive role handoff;
    deferred because it opens adaptive policy semantics.
```

D2 result:

```text
Command:
    .venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/run_d2_conserved_causal_packet_loop.py

Output:
    outputs/d2_conserved_causal_packet_loop.json
    reports/d2_conserved_causal_packet_loop.md
    outputs/d2_conserved_causal_packet_loop_timeseries/*.jsonl

Status:
    pass

Classification:
    d2_packetized_closed_flow_positive_with_controls

Positive rows:
    D2-P-cw-packet-loop
    D2-R-ccw-packet-loop
```

D2 lanes:

```text
D2-U0-no-seed:
    cycles = 0
    expected = negative
    result = negative

D2-P-cw-packet-loop:
    direction = clockwise
    cycles = 11
    opposite cycles = 0
    expected = positive
    result = positive

D2-R-ccw-packet-loop:
    direction = counter-clockwise
    cycles = 11
    opposite cycles = 0
    expected = positive
    result = positive

D2-C-forward-only:
    cycles = 0
    expected = negative
    result = negative

D2-C-broken-return:
    cycles = 0
    expected = negative
    result = negative

D2-C-scrambled-order:
    cycles = 0
    expected = negative
    result = negative
```

D2 interpretation:

```text
Packetized in-flight coherence is sufficient, in this experiment-local
prototype, to turn the D1e static role surface into ordered closed-loop
propagation under exact node-plus-packet budget accounting. The null, one-way,
broken-return, and scrambled-order controls stay negative. Material
per-channel circulation alone is not enough: the controls can move packets,
but they fail the ordered cycle gate.
```

D2 claim boundary:

```text
D2 is packetized prototype evidence only. It is not native GRC9V3 evidence,
does not imply that N03 passed in native fixed-topology GRC9V3, and does not
open movement claims.
```

D2.1 robustness audit:

```text
D2.1: packet loop robustness and conservation audit
```

Purpose:

```text
Harden the D2 packetized closed-flow prototype before any later interpretation.
The audit tests exact node-plus-packet conservation, packet loss/duplication,
declared channel causality, direction-reversal symmetry, seed dependence,
delay sensitivity, and deterministic small perturbations.
```

Run record:

```text
Command:
    .venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/run_d2_1_packet_loop_robustness.py

Output:
    outputs/d2_1_packet_loop_robustness.json
    reports/d2_1_packet_loop_robustness.md
    outputs/d2_1_packet_loop_robustness_timeseries/*.jsonl

Status:
    pass

Classification:
    d2_1_packet_loop_robustness_passed

Positive rows:
    D2.1-P-cw-delay-1
    D2.1-P-cw-delay-3
    D2.1-P-cw-delay-6
    D2.1-R-ccw-delay-3
    D2.1-S-weak-seed
    D2.1-S-over-seed
    D2.1-N-jittered-delay
    D2.1-N-node-perturbation
```

D2.1 audit result:

```text
max node-plus-packet budget error: 1.11022e-16
duplicate packet ids: 0
orphan parent ids: 0
unknown channel ids: 0
direction reversal symmetry: passed
errors: none
```

D2.1 controls:

```text
D2.1-U0-no-seed:
    negative; no packet activity

D2.1-C-wrong-direction-seed:
    negative for the declared clockwise expectation;
    opposite-direction cycles are detected as the control condition

D2.1-C-forward-only:
    negative; one-channel movement does not close the ordered cycle

D2.1-C-broken-return:
    negative; missing return closure blocks cycle formation

D2.1-C-scrambled-order:
    negative; packet activity without canonical order is not promoted
```

D2.1 interpretation:

```text
The D2 packetized prototype survives the first robustness audit. The positive
closed-loop rows remain stable across packet-delay sweep, direction reversal,
weak/over seed amounts, deterministic delay jitter, and small node-coherence
perturbation. The negative controls remain negative. This strengthens the
bounded prototype result only: packetized in-flight coherence can support
ordered closed-flow propagation under explicit packet accounting. It still is
not native GRC9V3 evidence and does not open movement claims.
```

D2.2 state-triggered departure bridge:

```text
D2.2: state-triggered packet departure
```

Purpose:

```text
Test whether the D2 packetized loop can be launched from measured state
conditions rather than a hand-authored packet seed schedule. Departure is
triggered when a source pole's measured mass exceeds its reference mass by a
serialized threshold.
```

Trigger policy:

```text
source_pole_mass - reference_pole_mass >= trigger_threshold
```

Initial run note:

```text
The first D2.2 run failed because the state-trigger scanner ignored the
forward-only and broken-return control modes. This was a control-implementation
bug, not a positive result. The trigger eligibility was tightened so those
controls remove the intended channel surfaces, then the script was rerun.
```

Run record:

```text
Command:
    .venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/run_d2_2_state_triggered_packets.py

Output:
    outputs/d2_2_state_triggered_packets.json
    reports/d2_2_state_triggered_packets.md
    outputs/d2_2_state_triggered_packets_timeseries/*.jsonl

Status:
    pass

Classification:
    d2_2_state_triggered_packet_departure_positive_with_controls

Positive rows:
    D2.2-P-cw-state-triggered
    D2.2-R-ccw-state-triggered
    D2.2-P-cw-delay-1
    D2.2-P-cw-delay-6
    D2.2-S-weak-trigger
    D2.2-S-over-trigger
    D2.2-N-jittered-delay
    D2.2-N-node-perturbation
```

D2.2 audit result:

```text
max node-plus-packet budget error: 1.11022e-16
duplicate packet ids: 0
orphan parent ids: 0
unknown channel ids: 0
direction reversal symmetry: passed
errors: none
```

D2.2 controls:

```text
D2.2-U0-no-surplus:
    negative; no measured surplus and no packet activity

D2.2-C-subthreshold-surface:
    negative; surplus below trigger threshold

D2.2-C-wrong-direction-trigger:
    negative for the declared clockwise expectation;
    opposite-direction cycles are detected as the control condition

D2.2-C-forward-only:
    negative; one channel fires but does not close the ordered cycle

D2.2-C-broken-return:
    negative; partial propagation stops before return closure
```

D2.2 interpretation:

```text
D2.2 shows that the packetized prototype can be launched from a measured
state-triggered departure rule rather than an explicit packet seed schedule.
The result is a stronger autonomy bridge for the packet mechanism, but remains
packetized prototype evidence only. It does not establish native GRC9V3 loop
formation and does not open movement claims.
```

D2.3 self-rearming packet pulse probe:

```text
D2.3: self-rearming packetized pulse candidate
```

Purpose:

```text
Test whether a state-triggered packet loop can regenerate the next trigger
condition after a completed cycle. The self-rearm condition is natural: the
returned packet recreates source-pole surplus, crosses the serialized trigger
threshold, and launches the next packet without a hand-authored schedule.
```

Probe correction notes:

```text
The first D2.3 probe used an explicit reserve-recharge surface. That surface
interfered with canonical packet causality and was removed. D2.3 now measures
natural self-rearming only: returned packet -> source surplus -> threshold
crossing -> next packet departure.

The scrambled-order control initially remained inert because state scanning
could still select the canonical surplus pole. The final script restricts the
eligible next channel after a parent arrival according to the lane's declared
order, so scrambled order genuinely tests the wrong handoff.
```

Run record:

```text
Command:
    .venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/run_d2_3_self_rearming_packets.py

Output:
    outputs/d2_3_self_rearming_packets.json
    reports/d2_3_self_rearming_packets.md
    outputs/d2_3_self_rearming_packets_timeseries/*.jsonl

Status:
    pass

Classification:
    d2_3_self_rearming_packet_pulse_candidate_with_controls

Positive rows:
    D2.3-P-self-rearming-cw
    D2.3-R-self-rearming-ccw
    D2.3-S-low-threshold
    D2.3-N-jittered-delay
```

D2.3 audit result:

```text
max node-plus-packet budget error: 0
duplicate packet ids: 0
orphan parent ids: 0
unknown channel ids: 0
direction reversal symmetry: passed
errors: none
```

D2.3 main positive rows:

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

D2.3-N-jittered-delay:
    triggers: 47
    rearms: 11
    events: 46
    cycles: 11
```

D2.3 controls:

```text
D2.3-U0-no-surplus:
    negative

D2.3-C-subthreshold:
    negative

D2.3-C-threshold-too-high:
    negative

D2.3-C-wrong-direction:
    negative for the declared clockwise expectation;
    opposite cycles are detected as the control condition

D2.3-C-forward-only:
    negative

D2.3-C-broken-return:
    negative

D2.3-C-scrambled-order:
    negative
```

D2.3 interpretation:

```text
D2.3 provides the first bounded L5-like packetized pulse-generator candidate.
The loop does not merely launch from measured state; after completing a cycle,
the returned packet recreates the measured source surplus that fires the next
departure. This is still experiment-local packetized prototype evidence only.
It does not establish native GRC9V3 loop formation, movement, locomotion,
agency, or biological motility.
```

E1 LGRC adapter alignment:

```text
E1: LGRC adapter alignment
```

Purpose:

```text
Translate D2.3 into an LGRC-style causal event ledger before making native
LGRC9V3 runtime claims.
```

Result:

```text
classification: adapter_compatible
d2_3_lgrc_aligned: true
native_lgrc9v3_execution: false
core_task_requested: false
```

Interpretation:

```text
D2.3 has LGRC-shaped semantics: packet departure, packet arrival, route order,
event-time key, and node-plus-packet budget can be validated from an LGRC-style
ledger. E1 is not native execution evidence; it only proves adapter
compatibility.
```

E2 native LGRC9V3 runtime alignment:

```text
E2: native LGRC9V3 runtime alignment
```

Purpose:

```text
Move from adapter compatibility to actual LGRC9V3 packet execution while
identifying the missing native D2.3 surfaces.
```

Result:

```text
native_packet_execution_compatible
adapter_triggered_runtime_compatible
native_static_route_autonomy_available
missing_native_surplus_trigger_primitive
native_d2_3_equivalent = false
native_self_rearm_evidence = false
```

Interpretation:

```text
Native LGRC9V3 can execute the packet geometry and preserve ledger evidence,
but static route autonomy is not D2.3 equivalence. D2.3 requires the returned
packet to change runtime pole mass, the producer to observe post-arrival
surplus, and the child departure to be scheduled from that evidence.
```

E3 native LGRC9V3 D2.3-equivalent reproduction:

```text
E3: native LGRC9V3 D2.3-equivalent packet loop
```

Purpose:

```text
Promote the missing D2.3 surfaces into native LGRC9V3 runtime semantics:
route-aspects, surplus-trigger production, and completed self-rearm evidence.
```

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

Interpretation:

```text
E3 resolves the L5-like self-rearming pulse requirement for native LGRC9V3
packetized causal execution. Returned packet coherence recreates the measured
surplus condition that triggers later departures, and the positive and
negative classifications are validated from native runtime artifacts.

This remains false for native fixed-topology GRC9V3 proposal flux. It does not
support movement, locomotion, agency, biology, or native GRC9V3 proposal-flux
loop claims.
```

### Later Surface: Self-Regulation L5

Status:

```text
resolved for native LGRC9V3 packetized execution;
blocked for native GRC9V3 proposal-flux execution.
```

### Later Surface: Boundary Coupling

E3 supplies a native packetized L5-like pulse substrate. L6 remains unopened
until a separate boundary-coupling plan is accepted. Any L6 evidence must hand
off to the movement-ladders experiment rather than making movement claims
inside this experiment.

### Later Surface: Multi-Pole Basin Loops

Appendix A of the paper records multi-pole basin loops as a future
generalization. They are deferred for the first implementation pass.

The current scope remains the minimal two-aspect loop:

```text
source-aspect -> forward channel -> sink-aspect -> return channel -> source-aspect
```

Do not implement multi-pole interaction matrices, multi-pole closure scores,
phase-pattern ladders, MP0-MP6 classifiers, or 3-/9-pole fixtures until the
two-aspect L4 result is stable and reproducible.

## Deferred Final Output Cleanup

Generated outputs are intentionally left expanded during active experiment
work. The current priority is preserving reviewability while the execution
model is still being developed.

The number of generated files is not, by itself, a correctness problem. During
active review, expanded outputs are useful because they preserve the full audit
trail from negative GRC9V3 runs through D2.3 and native E3. Cleanup should stay
deferred unless the file count starts harming review, repository operations,
or final sharing.

Before final sharing, repository cleanup, or another concrete file-count
pressure, add a packaging pass that reduces the generated-file footprint
without losing replay evidence.

Cleanup scope:

- inventory generated outputs from Branch B through E3;
- keep human-readable reports, summary JSON files, configs, scripts, and
  implementation docs directly visible;
- consolidate bulky time-series, packet-ledger, per-lane trace, and row-level
  artifacts, including animation checkpoint sequences if needed, into one or
  more machine-readable bundles;
- write a bundle manifest that maps every original logical artifact path to
  its bundled location, digest, artifact kind, lane/run id, and generating
  command when known;
- preserve enough information to replay or validate every result from the
  bundle and manifest;
- update reports or add manifest mappings so stale expanded-output paths remain
  resolvable;
- do not delete expanded evidence until the bundle and manifest have been
  validated;
- record the final cleanup command, validation command, and before/after file
  counts.

Preferred packaging target:

```text
outputs/bundles/
    n03_generated_artifacts_bundle.jsonl
    n03_generated_artifacts_manifest.json
```

This is a final packaging task, not part of the active Branch B/C/D/E
scientific interpretation.

## Completion Criteria

The first implementation pass is complete when:

- U/S/K lanes are runnable from `scripts/`;
- every run emits schema-valid output under `outputs/`;
- reports under `reports/` state the claim ceiling;
- budget and single-parent-basin gates are audited;
- null separation is reported;
- negative/blocked/candidate classification is deterministic and replayable;
- the first fixed-topology tranche conclusion is recorded as positive,
  negative, or blocked;
- multi-pole Appendix A surfaces remain explicitly deferred;
- output cleanup remains recorded as a final packaging task, or has been
  completed with a validated bundle manifest;
- no `src/pygrc` runtime behavior was changed by the experiment.

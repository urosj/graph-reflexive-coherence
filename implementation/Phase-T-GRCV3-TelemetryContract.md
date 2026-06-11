# Phase T GRCV3 Telemetry Contract

## Purpose

This note records the explicit `GRCV3` telemetry extension contract introduced
in Phase T Iteration 16 and widened in the later rich-`GRCV3` observability
lift. It was later extended by the pressure-boundary track to expose
default-off `GRCV3` frontier-birth telemetry.

The shared telemetry core remains unchanged:

- step rows
- event rows
- run summaries
- experiment reports
- comparison reports

`GRCV3` adds family-specific payloads only through:

- `family_extensions["grcv3"]` on step rows
- `family_extensions["grcv3"]` on event rows
- `family_extensions["grcv3"]` on run summaries

The canonical contract version for this first slice is:

- `phase_t_iter26_v1`

## Family Key

- family key: `grcv3`
- contract version: `phase_t_iter26_v1`

These values are exported from:

- [src/pygrc/telemetry/grcv3_contract.py](../src/pygrc/telemetry/grcv3_contract.py)

## Step-Row Extension Payload

Each `GRCV3` step row should carry:

- `contract_version`
- `backend_summary`
- `signed_hessian`
- `basin_summary`
- `spark_state`
- `hierarchy_state`
- `choice_state`
- `frontier_birth_state`

The landscape-capable step surface may also carry:

- `transient_landscape`

### Step-Extension Builder Precondition

The current representative `GRCV3` builders assume `hessian_sign` has already
been calibrated and stored in `state.cached_quantities`.

That means:

- step and run-summary extension builders are valid after at least one
  differential rebuild that establishes `hessian_sign`
- the representative lane satisfies this because telemetry assembly happens
  after stepping
- a fresh unstepped model is not a supported input for the current
  representative builders

This is a representative-lane precondition, not a recorder requirement.

### Required Step Fields

`backend_summary`:

- `geometry_backend`
- `differential_backend`
- `metric_backend`
- `spark_backend`
- `hierarchy_backend`
- `choice_backend`

`signed_hessian`:

- `hessian_sign`

`basin_summary`:

- `attributed_node_count`
- `active_basin_count`
- `geometric_seed_count`
- `geometric_validated_basin_count`
- `max_hierarchy_depth`

`spark_state`:

- `split_registry_size`
- `active_split_count`
- `confirmed_split_count`
- `pending_spark_count`

`hierarchy_state`:

- `hierarchy_root_count`
- `hierarchy_node_count`
- `child_basin_link_count`

`choice_state`:

- `choice_regime_count`
- `collapse_registry_count`
- `evaluated_node_count`

`frontier_birth_state`:

- `frontier_birth_mode`
- `frontier_birth_rule`
- `frontier_candidate_count`
- `pressure_boundary_candidate_count`
- `frontier_birth_count`
- `pressure_boundary_birth_count`
- `frontier_sources_observed`
- `outward_flux_pressure_min` when birth events are observed
- `outward_flux_pressure_max` when birth events are observed
- `outward_flux_pressure_mean` when birth events are observed
- `birth_probability_min` when birth events are observed
- `birth_probability_max` when birth events are observed
- `birth_probability_mean` when birth events are observed

Frontier-birth interpretation:

- missing `frontier_birth_mode` in runtime configuration means disabled
- explicit `frontier_birth_mode = disabled` means current no-birth behavior
- `frontier_birth_mode = active_frontier_pressure` is the only opt-in birth
  mode in this contract slice
- pressure-boundary provenance is reported as `frontier_source =
  pressure_boundary`, not as GRC9/GRC9V3 `front_capacity_source`

`transient_landscape` when present:

- `monitoring_surface_kind`
- `observed_sites`

Each `observed_site` records:

- `primitive_id`
- `node_id`
- `gradient_norm`
- `min_signed_eigenvalue` when available
- `max_signed_eigenvalue` when available
- `weak_mode_signed_curvature` when available
- `gradient_gate_pass`
- `geometric_validation_pass`
- `spark_candidate_regime`

Interpretation rule:

- the reported weak-mode signed curvature is the runtime minimum signed-Hessian
  eigenvalue
- it is the operational weak mode used by spark detection
- it is not a claim that source role labels are identical to the runtime
  eigenbasis

## Event-Row Extension Payload

Each `GRCV3` event row should carry:

- `contract_version`
- `event_domain`
- `lifecycle_stage`
- `topology_mutation`
- `hierarchy_mutation`

### Optional Event Fields

The event payload may also carry:

- `primary_node_id`
- `primary_basin_id`
- `registry_key`

These are optional because some event kinds do not have one stable subject in
the raw event payload.

### Event Classification Rule

The event-row extension does not replace the raw `event_kind`. It gives a
stable classification layer for downstream report and visualization code.

The first classification table is:

- `spark_candidate` -> domain `spark`, stage `candidate`
- `spark_pending` -> domain `spark`, stage `pending`
- `spark` -> domain `spark`, stage `confirmed`
- `split_init` -> domain `split`, stage `init`
- `split_progress` -> domain `split`, stage `progress`
- `split_complete` -> domain `split`, stage `complete`
- `choice_detected` -> domain `choice`, stage `detected`
- `choice_resolved` -> domain `choice`, stage `resolved`
- `collapse` -> domain `choice`, stage `collapse`
- `frontier_birth` -> domain `birth`, stage `created`
- unknown kinds -> domain `other`, stage `other`

## Run-Summary Extension Payload

Each `GRCV3` run summary should carry:

- `contract_version`
- `backend_summary`
- `signed_hessian`
- `final_basin_summary`
- `final_spark_state`
- `final_hierarchy_state`
- `final_choice_state`
- `frontier_birth_summary`
- `lifecycle_event_counts`

The landscape-capable run-summary surface may also carry:

- `transient_landscape`

### Required Run-Summary Fields

`lifecycle_event_counts` uses a fixed surface:

- `spark_candidate_count`
- `spark_pending_count`
- `spark_confirmed_count`
- `split_init_count`
- `split_progress_count`
- `split_complete_count`
- `choice_detected_count`
- `choice_resolved_count`
- `collapse_count`
- `frontier_birth_count`

The summary contract is fixed-width on purpose so later report code can compare
or display lifecycle totals without parsing arbitrary free-form maps.

`frontier_birth_summary` uses the same field surface as step-row
`frontier_birth_state`, but aggregates over the run's `frontier_birth` events.

`transient_landscape` when present carries:

- `monitoring_surface_kind`
- `monitored_node_ids_by_primitive_id`
- `surface_realization_summary`
- `primitive_summaries`
- `event_aligned_observations`

This addition is intentionally still compressed:

- it gives event-aligned and trajectory-facing observability
- without dumping full per-node state into step rows or run summaries

## Recorder Boundary

The shared recorder does **not** validate family-extension payload structure for
known families. In this first slice it validates:

- step-extension sequence length against `step_results`
- event-extension sequence lengths against per-step event counts

The internal payload shape remains the responsibility of:

- the family contract dataclasses
- the family-specific extension builders
- and their direct tests

This is an intentional boundary for Iterations 16 through 19, not an accidental
omission.

## Representative Identity Notes

The first `GRCV3` representative lane uses a synthetic runtime identity rather
than a landscape-seed identity.

So the saved telemetry currently records:

- synthetic `seed_path` values of the form
  - `synthetic/grcv3/<lane_name>/<role>`
- `param_family = None`
- `rng_seed = None`

This is deliberate for the Phase 5 reference lane and should not be confused
with the landscape-seed-driven `GRCV2` representative experiments.

## Compression Rules

Iteration 16 is intentionally summary-oriented. The contract records compressed
diagnostics, not full `GRCV3` internal state.

The following are deliberate compression rules:

- no per-node gradient vectors
- no per-node Hessian matrices
- no per-node net-flux vectors
- no full `choice_registry` payloads in step rows
- no full `collapse_registry` payloads in step rows
- no full `split_registry` payloads in step rows
- no hierarchy tree dump in step rows or run summaries

Instead, the contract uses:

- counts
- backend identities
- `hessian_sign`
- small lifecycle summaries
- optional event-local identifiers already present in raw events
- optional monitored-site transient summaries for landscape-facing rich runs

## Why This Shape

This first `GRCV3` telemetry slice is meant to be:

- explicit enough for later runtime wiring
- light enough to keep telemetry cheap and deterministic
- honest about what it is summarizing versus omitting

Richer per-node or graph-visible `GRCV3` telemetry may come later, but it
should be added as:

- new checkpoint payload groups
- or explicitly versioned family-extension additions

not by silently mutating this contract.

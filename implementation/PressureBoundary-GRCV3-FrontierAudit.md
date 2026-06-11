# Pressure Boundary GRCV3 Frontier Audit

This note records Pressure Boundary Iteration 5.1.

## Result

GRCV3 / GRCL-V3 pressure-boundary support is currently not replay-backed in
the default runtime, because default `GRCV3.step()` has no birth/frontier
stage. The implementation decision is to preserve that no-birth default while
allowing a future explicit opt-in birth mode for new pressure-boundary lanes.

The GRCV3 paper describes front propagation / birth as a theory mechanism, but
the current `GRCV3.step()` implementation does not include an `apply_growth`,
`apply_birth`, or active-frontier-birth step. Its canonical step order is:

```text
compute_differential_summary_pre_flux
compute_node_tensors
compute_metric
compute_edge_labels_pre_flux
compute_potential
compute_flux
compute_edge_labels_post_flux
refresh_differential_summary_post_flux
detect_identities
detect_sparks
advance_splits
update_choice_state
apply_continuity
enforce_budget
refresh_runtime_state
compute_observables
```

Therefore existing GRCV3 seeds cannot yet produce artifact-backed
pressure-boundary birth evidence equivalent to the GRC9/GRC9V3
`front_capacity_source = pressure_boundary` runs. New evidence may be added
only through an explicit mode such as:

```text
frontier_birth_mode = active_frontier_pressure
frontier_birth_strict = error
```

When `frontier_birth_mode` is absent, the runtime must behave exactly as it
does today. Authored pressure-boundary/frontier seeds should set
`frontier_birth_mode = active_frontier_pressure`; missing or disabled mode is
for legacy compatibility and explicit no-birth controls.

## Runtime Findings

- `GRCV3.step()` has spark, split, choice/collapse, continuity, budget, and
  refresh stages.
- There is no growth/birth/frontier stage in the default implemented step
  loop.
- There is no `growth` event kind emitted by GRCV3.
- There is no GRC9-style port capacity, inactive-port, lowest-port, or
  `front_capacity_source` mechanism in GRCV3.
- Boundary mode exists as `prune`, `barrier`, or `ghost`, but that is boundary
  handling / traversal-cost capability, not birth-front provenance.
- The accepted extension path is default-off:
  - missing `frontier_birth_mode` means `disabled`,
  - explicit `frontier_birth_mode = disabled` means current no-birth behavior,
  - explicit `frontier_birth_mode = active_frontier_pressure` may activate the
    new birth/frontier implementation,
  - `frontier_birth_strict = warn` warns once when frontier candidates exist
    but birth is disabled,
  - `frontier_birth_strict = error` stops source/evidence runs that declare
    frontier candidates while leaving birth disabled,
  - `frontier_birth_strict = allow` is reserved for explicit no-birth controls
    and legacy compatibility lanes,
  - unknown mode or strictness values must fail validation.

## Telemetry Findings

The Phase T GRCV3 contract exposes:

- backend identity,
- basin summaries,
- signed Hessian metadata,
- spark/split state,
- hierarchy state,
- choice/collapse state,
- lifecycle event counts for spark, split, choice, and collapse,
- transient landscape monitoring surfaces.

It does not expose:

- growth count,
- birth probability,
- active-frontier birth parent,
- pressure-boundary growth count,
- front-capacity provenance,
- GRC9/GRC9V3 port-capacity fields.

Any GRCV3 pressure-boundary selector added before the opt-in runtime and
telemetry surface exists would either have to be source-only or would report
missing runtime surfaces for replay evidence.

## GRCL-V3 Source / Lowering Findings

GRCL-V3 rich seeds already have useful boundary/interface language:

- `boundary_roles`,
- `channel_roles`,
- `preferred_attachment_sites`,
- `boundary_geometry`,
- `channel_geometry`,
- `settlement_regime`.

The family-native lowering path preserves attachment semantics through:

1. preferred attachment sites,
2. family-local role labels,
3. geometric fallback.

This is the right place to align pressure-boundary vocabulary in Iteration 5.2,
but it should be described as active-frontier / boundary-interface intent, not
as GRC9-style port capacity.

## Status Decision

For default GRCV3 / GRCL-V3, pressure boundary is:

- `source_vocabulary_candidate`: yes,
- `lowering_alignment_candidate`: yes,
- `runtime_growth_backed`: no,
- `telemetry_growth_backed`: no,
- `replayable_pressure_boundary_evidence`: reserved unless an explicit opt-in
  GRCV3 birth/frontier mode is declared by seed/config and supported by
  telemetry.

For the future opt-in path, the compatibility decision is:

- no existing seed/config gains birth behavior by omission,
- vocabulary alone does not activate birth,
- lowering must write the explicit runtime mode before birth can occur,
- the only planned runtime-enabling value is
  `frontier_birth_mode = active_frontier_pressure`,
- missing `frontier_birth_mode` and explicit `frontier_birth_mode = disabled`
  are both no-birth modes,
- pressure-boundary provenance should use family-native GRCV3 names such as
  `frontier_source = pressure_boundary`, not GRC9/GRC9V3
  `front_capacity_source`,
- existing GRCV3 results remain valid because their runtime mode is
  effectively `disabled`,
- compatibility must be validated by rerunning representative old outputs and
  confirming that no-birth runs reproduce the same observed telemetry and event
  results under the new `.step()` implementation.

## Consequences For Iterations 5.2-5.5

- Iteration 5.2 should add vocabulary notes mapping pressure boundary to
  active-frontier / boundary-interface intent and define the opt-in mode
  contract.
- Iteration 5.2 must explicitly avoid `front_capacity_source` and nine-port
  eligibility in GRCL-V3.
- Iteration 5.3 should implement the default-off GRCV3 runtime mode.
- Iteration 5.4 should add telemetry/selectors only for artifact-backed opt-in
  surfaces.
- Iteration 5.5 should compare representative old output sessions against
  reruns before adding opt-in evidence.
- Iteration 5.5 should run new evidence only for seeds/configs that explicitly
  set `frontier_birth_mode = active_frontier_pressure`.

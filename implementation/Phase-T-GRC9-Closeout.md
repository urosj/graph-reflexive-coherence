# Phase T-GRC9 Closeout

Status: completed

Contract family: `grc9`

Contract version: `phase_t_grc9_iter1_v1`

Post-closeout note: GRC9 growth telemetry has completed the correction follow-up
that distinguishes legacy broad inactive-port growth from paper-facing
front-capacity growth. The current contract remains the historical Revision 1
telemetry surface; the completed migration is tracked in
[GRC9-GRCL9-GrowthCorrection-Plan.md](./GRC9-GRCL9-GrowthCorrection-Plan.md)
and
[GRC9-GRCL9-GrowthCorrection-Checklist.md](./GRC9-GRCL9-GrowthCorrection-Checklist.md).
The accepted corrected catalogs are `S0035` for pure GRC9 and `S0036` for
GRCL-9 lowered evidence. Historical broad-growth outputs are replay-only
diagnostics and require explicit force flags on guarded tools.

Primary implementation files:

- `src/pygrc/telemetry/grc9_contract.py`
- `src/pygrc/telemetry/_grc9_extensions.py`
- `src/pygrc/models/grc_9_checkpoints.py`

The Phase 6 contract `phase6_iter10_v1` remains historical. This phase adds a
paper-facing GRC9 telemetry layer without changing the interpretation of
existing Phase 6 artifacts.

## Artifact Identities

Representative mechanical lane:

- lane: `phase_t_grc9_iter6_representative`
- default artifact roots:
  - `outputs/representative/grc9/phase_t_grc9_iter6_representative/primary/`
  - `outputs/representative/grc9/phase_t_grc9_iter6_representative/replay/`
- emits typed step, event, and run-summary `grc9` extensions.
- preserves primary/replay digest equality.

Seed-driven structural bridge lane:

- profile: `phase_t_grc9_iter7_seed`
- default artifact roots:
  - `outputs/representative/grc9_landscape/phase_t_grc9_iter7_seed/cell-1/`
  - `outputs/representative/grc9_landscape/phase_t_grc9_iter7_seed/cell-4/`
- keeps `source_lowering_mode = structural_graph_graft_v1`.
- does not claim `GRCL-9` or `GRC9V3` semantics.

Theory-facing diagnostic probe:

- probe: `phase_t_grc9_iter9_diagnostic_probe`
- entrypoint: `telemetry.build_grc9_diagnostic_probe()`
- returns a JSON-safe diagnostic payload rather than writing artifact files.
- records exercised fields and runtime gaps explicitly.

Optional graph checkpoint surface:

- exporter: `pygrc.models.grc_9_checkpoints.export_grc9_graph_checkpoint`
- checkpoint `graph_kind`: `port_graph`
- family-extension payload: `port_chart_module_overlay_v1`
- checkpoint capture is opt-in through the representative and seed-driven lane
  entrypoints; behavior-only Phase T-GRC9 runs do not write checkpoint artifacts
  by default.

## Theory-To-Telemetry Status

| Paper-facing phenomenon | Closeout status | Evidence surface |
| --- | --- | --- |
| Nine ordered ports and active degree | artifact-backed | step `port_chart`, checkpoint port overlays |
| Rows as local directional basis | artifact-backed | step `row_tensor`, checkpoint row occupancy |
| Columns as interface families | artifact-backed | step `column_diagnostic`, expansion reassignment counts, coarse summaries |
| Tensor from density, mismatch, flux feedback | artifact-backed | step `row_tensor` term summaries and hotspots |
| Conductance map and analytic labels | artifact-backed | step `transport`, checkpoint edge label availability |
| Potential and flux | artifact-backed | step `transport`, checkpoint signed flux overlays |
| Sinks and identity basins | artifact-backed | step/run `identity_abundance` |
| Scale-weighted abundance | artifact-backed when gamma configured | `scale_weighted_abundance`, diagnostic probe |
| Spark under saturation | artifact-backed | spark event taxonomy and evidence |
| Optional near-saturation rule | reserved_future | named as deferred; not applied by Phase 6 |
| Optional sign-crossing spark | artifact-backed when configured | sign-crossing event evidence, diagnostic probe |
| Expansion module | artifact-backed | expansion events, run summary, checkpoint modules |
| Expansion distribution | artifact-backed | backend config, transfer ratios |
| Expansion bond initialization | artifact-backed | expansion bond mode/weight/stats |
| Effective degree policy | artifact-backed | spark prediction and expansion evidence |
| Adiabatic expansion schedule | diagnostic-only | configured schedule/substeps are recorded; phased loop remains deferred |
| Identity fission after expansion | artifact-backed when evaluator observations are supplied | candidate and confirmed run-summary counts; Appendix E persistence evaluator |
| Growth on inactive ports | artifact-backed with provenance split | growth events, run growth summary, `growth_parent_eligibility_mode`, front-capacity and legacy broad-growth counts |
| Invertible column coarse-graining | artifact-backed | coarse summaries and diagnostic reconstruction checks |
| Signed flux exact encoding | artifact-backed | signed flux split and reconstruction probe |
| Profile sparsity compression | diagnostic-only | `profile_compression_mode = full`; compressed storage remains future-facing |
| Successor-map tie handling | artifact-backed | successor tie count and tie-break policy |
| Budget preservation policy | artifact-backed | budget policy/path and correction count split |
| Ternary identity tree extraction | reserved_future | not implemented in Phase 6 GRC9 |
| Calibration magnitudes | diagnostic-only | threshold mode and optional burn-in fields; no automatic burn-in lane |
| Boundary-horizon analogue | reserved_future | barrier/ghost modes reserved; prune is current runtime behavior |
| Temporal/causal layer | temporal-delay label artifact-backed; causal layer out_of_scope | transport labels only |
| Scale-indexed FRC field | reserved_future | no sigma-field runtime |
| Observer-local unpredictability | reserved_future | no restricted observer-view runtime |

## Deferred Boundaries

The following remain explicitly outside the completed Phase T-GRC9 telemetry
claim:

- `GRC9V3`: no lifted hierarchy, collapse, or choice semantics are claimed.
- `GRCL-9`: seed-driven structural bridge telemetry is not a lowering proof.
- boundary `barrier` / `ghost`: reserved until runtime modes exist.
- Lorentzian causal layer: only `temporal_delay` labels are surfaced.
- FRC sigma field: no scale-indexed field is implemented.
- observer-local views: no restricted observer telemetry is implemented.
Confirmed identity fission has been closed as a bounded diagnostic follow-up.
The Appendix E evaluator observes completed trajectories, checks stable
same-pair two-sink persistence inside expansion modules, applies a minimum basin-mass
threshold, and updates confirmed fission run-summary fields without mutating
GRC9 dynamics.

This follow-up does not reopen the other deferred semantic layers. Observer
views, `GRC9V3`, `GRCL-9`, Lorentzian causal structure, FRC sigma fields, and
boundary barrier/ghost runtime remain reserved or out of scope.

## Verification

Focused verification covers:

- contract dataclasses and validators,
- step/event/run-summary builders,
- representative Phase T lane,
- seed-driven Phase T profile,
- diagnostic probe,
- opt-in graph checkpoint export,
- opt-in graph checkpoint capture in representative and seed-driven lanes,
- legacy Phase 6 GRC9 representative and seed profiles.

The representative and seed-driven Phase T lanes can be reconstructed through
their public experiment entrypoints:

- `telemetry.run_grc9_representative_experiment(lane_name="phase_t_grc9_iter6_representative")`
- `telemetry.run_grc9_landscape_experiment(profile_name="phase_t_grc9_iter7_seed")`

Closeout does not collapse future paper-facing constructs into current runtime
behavior. It records what is artifact-backed now, what is diagnostic-only, and
what remains reserved or out of scope.

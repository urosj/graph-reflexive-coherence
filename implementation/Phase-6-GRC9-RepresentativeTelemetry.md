# Phase 6 GRC9 Representative Telemetry

## Purpose

This note records the two closeout-facing `GRC9` artifact lanes introduced by
Phase 6:

- the representative eventful mechanical lane
- the seed-driven structural lane

The purpose of these lanes is deliberately narrow:

- prove that the shared telemetry framework can capture `GRC9`
- keep `GRC9.step()` telemetry-agnostic
- produce saved reports that can be inspected without live runtime access
- separate mechanical event validation from seed-driven structural validation

## Lane 1. Representative Eventful Mechanical Lane

### Selected Lane

The representative lane is the deliberately eventful synthetic substrate used
to make core Phase 6 mechanics visible in saved artifacts.

The lane is intentionally designed so that over the default run:

- spark is visible
- expansion is visible
- later growth is visible
- replay stability is visible through `primary` vs `replay`

Post growth-semantics correction note: this historical representative lane
uses the default `legacy_any_inactive_port` growth eligibility unless a rerun
explicitly selects corrected `grc9_front_capacity` mode. Its growth events
remain useful replay diagnostics, but paper-facing front-growth claims should
use the corrected fields introduced in the Phase T-GRC9 contract:
`growth_parent_eligibility_mode`, `parent_capacity_source`,
`front_growth_provenance_present`, and `legacy_broad_growth`.

This is the right representative lane for Phase 6 because it exercises the
family’s characteristic mechanical topology events directly rather than
suppressing them.

### Comparison Surface

The representative comparison surface is:

- `primary`
- versus `replay`

where both runs start from the same deterministic initial state.

This comparison is narrow but honest:

- it checks artifact-backed replay stability
- it does not pretend to be a seed-driven comparison
- it does not make any `GRC9V3` source-semantic claim

The saved run identity is therefore intentionally synthetic:

- `seed_path = synthetic/grc9/<lane_name>/<role>`
- `param_family = None`
- `rng_seed` comes from the resolved mechanical config

### Artifact Layout

The representative artifacts live under:

- `outputs/representative/grc9/<lane_name>/primary/`
- `outputs/representative/grc9/<lane_name>/replay/`

using the standard telemetry subdirectory layout:

- `telemetry/steps.jsonl`
- `telemetry/events.jsonl`
- `telemetry/run_summary.json`
- `telemetry/experiment_report.json`
- `telemetry/comparison_report.json`

The first concrete closeout lane is:

- `lane_name = phase6_mechanical_baseline`

and the recorded closeout artifacts now exist at:

- `outputs/representative/grc9/phase6_mechanical_baseline/primary/.../telemetry/`
- `outputs/representative/grc9/phase6_mechanical_baseline/replay/.../telemetry/`

### Contract Surface Used

Each representative step row, event row, and run summary carries the compact
`grc9` family extension with:

- `contract_version`
- `lane_name`
- `role`
- `abundance_contract`
- `source_reference`

The run summary also carries:

- `final_expansion_count`

The field-level contract remains in:

- [Phase-6-GRC9-TelemetryContract.md](./Phase-6-GRC9-TelemetryContract.md)

## Lane 2. Seed-Driven Structural Lane

### Selected Lane

The seed-driven lane uses the real in-house seed pair:

- `configs/landscapes/seed/cell-1.seed.yaml`
- `configs/landscapes/seed/cell-4.seed.yaml`

This lane is not meant to prove `GRC9V3` semantics. It is meant to prove that
Phase 6 `GRC9` can ingest nontrivial seed inputs through an honest structural
bridge and still produce reproducible artifact-backed runs.

The key interpretation rule is:

- this lane is a structural graph graft onto the nine-slot substrate
- it currently reuses the existing `GRCV2` landscape blueprint boundary
- it is not a rich semantic projector
- it is not a full `GRCL-9` implementation

### Comparison Surface

The first truthful seed-driven `GRC9` comparison surface is:

- `cell-1`
- versus `cell-4`

This comparison is different from the representative replay lane:

- it checks structural seed-lowering plus saved artifact capture
- it does not check same-state replay equality
- it does not claim the two seeds should end in the same final digest

The saved run identity is correspondingly real rather than synthetic:

- `seed_path` is the concrete seed file path
- `param_family = phase6_seed_baseline`
- `seed_source_reference` is inherited from the source seed metadata

### Artifact Layout

The seed-driven artifacts live under:

- `outputs/representative/grc9_landscape/<profile_name>/cell-1/`
- `outputs/representative/grc9_landscape/<profile_name>/cell-4/`

using the same standard telemetry subdirectory layout:

- `telemetry/steps.jsonl`
- `telemetry/events.jsonl`
- `telemetry/run_summary.json`
- `telemetry/experiment_report.json`
- `telemetry/comparison_report.json`

The first concrete closeout lane is:

- `profile_name = phase6_seed_baseline`

and the recorded closeout artifacts now exist at:

- `outputs/representative/grc9_landscape/phase6_seed_baseline/cell-1/.../telemetry/`
- `outputs/representative/grc9_landscape/phase6_seed_baseline/cell-4/.../telemetry/`

### Contract Surface Used

Each seed-driven step row, event row, and run summary carries the compact
`grc9` family extension with:

- `contract_version`
- `profile_name`
- `abundance_contract`
- `seed_source_reference`
- `source_reference`
- `source_lowering_mode`

The run summary also carries:

- `final_expansion_count`

The critical interpretation field is:

- `source_lowering_mode = structural_graph_graft_v1`

That field exists so later readers do not silently reinterpret the Phase 6
seed lane as if it were already a `GRC9V3` semantic source lift.
It should also prevent the lane from being misread as a completed `GRCL-9`
family-native source path.

## Why There Are Two Lanes

These two lanes answer different questions:

- the representative lane checks whether the characteristic mechanical events
  are visible and replay-stable in saved artifacts
- the seed-driven lane checks whether real in-house seed inputs can be lowered
  honestly onto the mechanical substrate without smuggling in later semantics
  or overstating the current bridge as if it were already `GRCL-9`

Phase 6 closeout needs both:

- a purely mechanical event lane
- and one real-seed lane

but it does not yet need a dense rich-source lane, because Phase 6 still does
not open a family-local semantic source surface beyond structural graph
lowering.

## Current Limits

These representative notes do not yet cover:

- `grc9` graph checkpoint extensions
- graph-visible visualization contracts comparable to Phase V `GRCV3`
- richer event taxonomy layered on top of raw `GRC9` event kinds
- dense rich-source semantic lanes

Those are later concerns. The current Phase 6 telemetry surface is narrower by
design.

# Landscape Language Reference Guide

This guide describes the normalized landscape seed language used by PyGRC.
The language is implemented by the `LandscapeSeed` schema and stored in
`configs/landscapes/seed/`.

Landscape seeds are source-side descriptions. They preserve authored landscape
meaning, but they are not solved runtime states and they are not proof that a
runtime event or observed structure occurred.

## Scope

Use this guide when you want to:

- read or author `LandscapeSeed` YAML/JSON files,
- understand neutral primitive types such as `basin`, `ridge`, `valley`, and
  `junction`,
- add family-specific source annotations without contaminating the neutral
  seed layer,
- validate and serialize seed documents,
- distinguish normal, legacy, inferred, and motion seed documents.

This guide does not cover family lowering in detail. Lowering from source
seeds into GRC runtime states belongs in the Landscape Compiler reference.

## Authority Model

A `LandscapeSeed` can describe source intent, translated PDE structure,
manual research preconditions, or observed inference results.

It must not smuggle runtime facts into source documents. In particular, an
authored seed should not claim:

- a spark happened,
- growth happened,
- an identity moved,
- a collapse happened,
- a runtime selector passed,
- a checkpoint was solved,
- a telemetry event was emitted.

Runtime claims must come from telemetry, checkpoints, selector validation,
landscape inference, or motion inference.

## Canonical Locations

| Path | Purpose |
|---|---|
| `implementation/LandscapeSeedSchema.md` | Engineering schema definition and design notes. |
| `src/pygrc/landscapes/seed.py` | Dataclass model for normalized seeds. |
| `src/pygrc/landscapes/io.py` | YAML/JSON load/save API. |
| `src/pygrc/landscapes/validation.py` | Validation boundary. |
| `configs/landscapes/seed/` | Canonical reusable seed library. |
| `configs/landscapes/seed/legacy/` | Quarantined historical seeds. |
| `configs/landscapes/seed/motion/` | Motion source-precondition seeds. |

## Top-Level Shape

Every normal seed has this shape:

```yaml
seed_schema: "pygrc.landscape_seed"
seed_version: "0.1"

meta: {}
constitutive_profile: {}
primitives: []
transport_intent: []
geometry_hints: {}
extensions: {}
```

Required top-level fields:

- `seed_schema`
- `seed_version`
- `meta`
- `constitutive_profile`
- `primitives`

Optional top-level fields:

- `transport_intent`
- `geometry_hints`
- `extensions`

The validator permits empty `primitives` only for observed inferred landscape
shells using `meta.source_kind: inferred_observed_landscape` and
`extensions.landscape_inference`.

## Metadata

The `meta` block identifies the document and its source authority.

Common fields:

```yaml
meta:
  name: GRCL9V3 Corrected Hybrid Full Composition
  source_kind: manual_seed
  source_reference: implementation/GRCL-9V3-ImplementationChecklist.md
  source_schema_version: "0.1"
  source_domain: grcl9v3
  description: Corrected composition with spark, front growth, choice, and transport.
  tags: [grcl9v3, corrected_growth, hybrid]
  translator_name: manual_seed_authoring
  translator_version: "0.1"
  translation_mode: semantic_enrichment
  translation_notes: []
```

Common `source_kind` values used in the repository:

- `pde_landscape_dsl`
- `manual_seed`
- `translated_seed`
- `authored_motion_seed`
- `inferred_observed_landscape`

Common `translation_mode` values:

- `lossless_source_normalization`
- `semantic_enrichment`

## Constitutive Profile

The `constitutive_profile` carries neutral dynamical coefficients attached to
the source.

```yaml
constitutive_profile:
  lambda_c: 1.0
  xi_c: 1.5
  zeta_c: 0.8
  kappa_c: 1.0
  dt: 0.001
  potential:
    type: double_well
    params:
      a: 1.0
      b: 1.2
  budget_b: 4.0
  notes: Optional explanation.
  source_params: {}
```

Validation requirements:

- coefficients must be finite real numbers,
- `dt` must be greater than zero,
- `potential.type` must be a non-empty string,
- `potential.params` must be a mapping,
- `budget_b`, when present, must be greater than zero.

`budget_b` is a source-side target or hint. Runtime budget correctness still
comes from runtime initialization and telemetry.

## Primitive Vocabulary

The neutral primitive types are:

- `basin`
- `plateau`
- `ridge`
- `valley`
- `junction`
- `saddle`

Every primitive has:

```yaml
- id: primitive_id
  type: basin
  label: Optional label
  role: Optional role
  tags: []
  hints: {}
  extensions: {}
```

Primitive IDs must be unique. Cross-reference fields such as `parent_id`,
`owner_id`, `from_id`, `to_id`, `host_id`, and `branch_target_ids` must point
to existing primitive IDs.

`hints` is the generic catch-all container for source-side annotations that do
not have a typed field yet. Prefer typed fields such as `chart_center_hint`,
`depth_hint`, `thickness_hint`, or `waypoints` when the schema already provides
one; reserve `hints` for non-standard, non-runtime metadata.

Most primitive variants also provide a `notes` field. Notes are descriptive
source metadata, not runtime evidence.

### Primitive Field Summary

| Type | Core References | Geometry / Shape Fields | Validation Notes |
|---|---|---|---|
| `basin` | `parent_id`, `boundary_ids` | `depth_hint`, `coherence_prior`, `chart_center_hint`, `chart_scale_hint`, `shape_hint`, `stability_class` | `depth_hint` is a non-negative int; root depth is `0` or omitted; references must resolve. |
| `plateau` | `parent_id`, `hosted_primitive_ids` | `depth_hint`, `coherence_prior`, `chart_center_hint`, `chart_scale_hint`, `stability_class` | Same hierarchy rules as `basin`; hosted IDs must resolve. |
| `ridge` | `owner_id`, `adjacent_ids` | `interior_coherence_hint`, `exterior_coherence_hint`, `thickness_hint`, `chart_principal_axis_hint`, `anisotropy_hint`, `permeability_hint` | `thickness_hint`, when present, must be greater than zero; adjacent/owner IDs must resolve. |
| `valley` | `from_id`, `to_id` | `path_hint`, `width_hint`, `coherence_prior`, `channel_role`, `waypoints` | `from_id` and `to_id` are required; `width_hint`, when present, must be greater than zero. |
| `junction` | `host_id`, `branch_target_ids` | `junction_role`, `coherence_prior`, `chart_center_hint` | Authored junctions need a host or branch targets; observed inference junctions may be looser. |
| `saddle` | `host_id`, `branch_target_ids` | `junction_role`, `coherence_prior`, `chart_center_hint` | Same runtime dataclass shape as `junction`, with `type: saddle`. |

### Basin

Basins represent support regions or identity-like source regions.

```yaml
- id: parent_basin
  type: basin
  parent_id: null
  depth_hint: 0
  coherence_prior: 1.0
  chart_center_hint: [0.0, 0.0]
  chart_scale_hint:
    radius: 1.0
  shape_hint: {}
  stability_class: stable
  boundary_ids: [membrane]
  notes: Optional source note.
```

Important validation rules:

- root basins have `parent_id: null` and `depth_hint` omitted or `0`,
- `depth_hint`, when present, must be a non-negative integer,
- non-root basin depth must match parent-implied depth when specified,
- `boundary_ids` must reference known primitives.

### Plateau

Plateaus represent stable hosting regions or broad support domains.

```yaml
- id: cell_plateau
  type: plateau
  depth_hint: 0
  coherence_prior: 2.0
  hosted_primitive_ids: [nucleus, cytoplasm]
  stability_class: persistent
  notes: Optional source note.
```

`hosted_primitive_ids` must reference known primitives. `depth_hint`, when
present, must be a non-negative integer.

### Ridge

Ridges represent boundaries, membranes, or separating structures.

```yaml
- id: membrane
  type: ridge
  ridge_kind: membrane
  owner_id: parent_basin
  adjacent_ids: [outside]
  interior_coherence_hint: 1.0
  exterior_coherence_hint: 0.2
  thickness_hint: 0.1
  chart_principal_axis_hint: [1.0, 0.0]
  anisotropy_hint:
    ratio: 2.0
  permeability_hint:
    mode: low_leakage
  notes: Optional source note.
```

A ridge is a source boundary claim, not automatically an observed runtime
ridge. Observed ridge classification requires checkpoint-local gradient or
tensor evidence.

`thickness_hint`, when present, must be greater than zero. `owner_id` and every
`adjacent_ids` entry must reference known primitives.

### Valley

Valleys represent transport channels or preferred corridors.

```yaml
- id: pressure_channel
  type: valley
  from_id: basin_a
  to_id: basin_b
  path_hint: directed_channel
  width_hint: 0.2
  coherence_prior: 0.5
  channel_role: transport
  waypoints:
    - [0.0, 0.0]
    - [1.0, 0.0]
  notes: Optional source note.
```

`from_id` and `to_id` are required and must reference known primitives.
`width_hint`, when present, must be greater than zero.

### Junction And Saddle

Junctions and saddles represent routing, branching, gates, choice loci, or
critical regions. They share the same dataclass shape; `type` may be
`junction` or `saddle`.

```yaml
- id: choice_locus
  type: saddle
  host_id: parent_basin
  branch_target_ids: [basin_a, basin_b]
  junction_role: choice
  coherence_prior: 1.0
  chart_center_hint: [0.5, 0.0]
  notes: Optional source note.
```

For authored primitives, a junction/saddle must provide `host_id` or at least
one `branch_target_ids` entry. Observed inference primitives may omit these
when they carry `extensions.landscape_inference.authority: observed`.

## Transport Intent

`transport_intent` records source-declared transport preference without
prescribing runtime flux directly.

```yaml
transport_intent:
  - id: walking_then_refinement_intent
    mode: ordered_precondition_sequence
    sources: [walking_origin]
    targets: [walking_successor]
    magnitude_hint: 1.0
    priority: 1.0
    carrier_id: walking_channel
    direction_hint: forward
    notes: Source intent only.
```

Validation rules:

- `id` and `mode` are required strings,
- `sources`, `targets`, and `carrier_id` must reference known primitives,
- `magnitude_hint` and `priority`, when present, must be finite numbers.

## Geometry Hints

`geometry_hints` preserve source-chart metadata. They are hints, not proof of
realized runtime coordinates.

```yaml
geometry_hints:
  source_chart: source_chart_2d
  periodicity: {}
  scale_units: normalized
  separation_hints: {}
  coordinate_convention: source_chart_xy
```

Per-primitive geometry hints include fields such as:

- `chart_center_hint`
- `chart_scale_hint`
- `chart_principal_axis_hint`
- `waypoints`

The validator currently expects 2D point lists for chart points.

## Extensions

Extensions are namespaced mappings. They let family-specific layers attach
source-side detail without changing the neutral schema.

Common namespaces:

- `source_pde`
- `grcl9`
- `grcl9v3`
- `landscape_inference`
- `motion_seed`

Example GRCL-9V3 primitive extension:

```yaml
extensions:
  grcl9v3:
    term_kind: growth_locus
    term_id: corrected_hybrid_full_composition_growth
    region_id: front_parent
    source_role: composition_control
    profile:
      outward_pressure_profile:
        pressure: corrected_front_high_outward_pressure
      lambda_birth: 100.0
      growth_semantics: front_capacity
```

Rules:

- unsupported extension namespaces should be ignored, not reinterpreted,
- extensions are not neutral truth unless a consumer explicitly supports them,
- source extensions must not contain solved runtime evidence unless the
  document is an observed inference artifact with explicit observed authority.

## Seed Families In The Repository

Current seed directories:

| Directory | Meaning |
|---|---|
| `configs/landscapes/seed/` | Active normalized and manual research seeds. |
| `configs/landscapes/seed/motion/` | Motion source-precondition seeds. |
| `configs/landscapes/seed/legacy/grcl9-overaggressive-growth/` | Historical GRCL-9 standalone-growth diagnostics. |
| `configs/landscapes/seed/legacy/grcl9v3-overaggressive-growth/` | Historical GRCL-9V3 standalone-growth diagnostics. |

Legacy growth seeds are retained for historical reproducibility. They are not
paper-facing front-growth evidence and should not be used as current examples
unless a diagnostic tool explicitly opts into legacy behavior.

## Minimal YAML Example

```yaml
seed_schema: "pygrc.landscape_seed"
seed_version: "0.1"

meta:
  name: minimal_two_basin_channel
  source_kind: manual_seed
  source_domain: example
  description: Two source basins connected by a preferred valley.
  tags: [example]

constitutive_profile:
  lambda_c: 1.0
  xi_c: 1.0
  zeta_c: 1.0
  kappa_c: 1.0
  dt: 0.1
  potential:
    type: double_well
    params: {}

primitives:
  - id: basin_a
    type: basin
    coherence_prior: 1.0
    chart_center_hint: [0.0, 0.0]
  - id: basin_b
    type: basin
    coherence_prior: 1.0
    chart_center_hint: [1.0, 0.0]
  - id: channel_ab
    type: valley
    from_id: basin_a
    to_id: basin_b
    channel_role: transport

transport_intent:
  - id: intent_ab
    mode: preferred_transport
    sources: [basin_a]
    targets: [basin_b]
    carrier_id: channel_ab
    magnitude_hint: 1.0
```

## API Examples

### Load And Validate A Seed

```python
from pygrc.landscapes.io import load_landscape_seed

seed = load_landscape_seed(
    "configs/landscapes/seed/grcl9v3-corrected-hybrid-full-composition.seed.yaml"
)

print(seed.meta.name)
print(len(seed.primitives))
```

### Inspect Primitive Types

```python
from collections import Counter
from pygrc.landscapes.io import load_landscape_seed

seed = load_landscape_seed("configs/landscapes/seed/motion/motion_seed_identity_walking.seed.yaml")
counts = Counter(primitive.type for primitive in seed.primitives)

print(dict(counts))
```

### Save A Seed

```python
from pygrc.landscapes.io import load_landscape_seed, save_landscape_seed

seed = load_landscape_seed("configs/landscapes/seed/cell-1.seed.yaml")
save_landscape_seed(seed, "outputs/examples/cell-1-copy.seed.yaml")
```

### Produce Canonical JSON

```python
from pygrc.landscapes.io import (
    landscape_seed_to_canonical_json,
    load_landscape_seed,
)

seed = load_landscape_seed("configs/landscapes/seed/cell-1.seed.yaml")
print(landscape_seed_to_canonical_json(seed))
```

### Handle Validation Errors

```python
from pygrc.core import InvalidLandscapeSeedError
from pygrc.landscapes.io import load_landscape_seed

try:
    seed = load_landscape_seed("configs/landscapes/seed/cell-1.seed.yaml")
except InvalidLandscapeSeedError as exc:
    raise SystemExit(f"invalid seed: {exc}") from exc
```

## Script Examples

### Validate One Seed

```bash
PYTHONPATH=src ./.venv/bin/python - <<'PY'
from pygrc.landscapes.io import load_landscape_seed

path = "configs/landscapes/seed/grcl9v3-corrected-hybrid-full-composition.seed.yaml"
seed = load_landscape_seed(path)
print(f"{path}: ok ({len(seed.primitives)} primitives)")
PY
```

### Validate All Active Seeds

```bash
PYTHONPATH=src ./.venv/bin/python - <<'PY'
from pathlib import Path
from pygrc.landscapes.io import load_landscape_seed

root = Path("configs/landscapes/seed")
paths = sorted(
    path for path in root.rglob("*.seed.yaml")
    if "legacy" not in path.parts
)

for path in paths:
    load_landscape_seed(path)

print(f"validated {len(paths)} active seed files")
PY
```

### List Motion Seeds

```bash
find configs/landscapes/seed/motion -maxdepth 1 -type f | sort
```

### Count Primitive Types For One Seed

```bash
PYTHONPATH=src ./.venv/bin/python - <<'PY'
from collections import Counter
from pygrc.landscapes.io import load_landscape_seed

seed = load_landscape_seed(
    "configs/landscapes/seed/grcl9v3-corrected-hybrid-full-composition.seed.yaml"
)
print(Counter(primitive.type for primitive in seed.primitives))
PY
```

## Validation Errors To Expect

Typical validation failures:

- missing required top-level fields,
- empty `primitives` on a normal authored seed,
- duplicate primitive IDs,
- unknown primitive references in `parent_id`, `from_id`, `to_id`, `host_id`,
  `owner_id`, `branch_target_ids`, `boundary_ids`, or `hosted_primitive_ids`,
- cyclic containment hierarchy,
- contradictory `depth_hint`,
- non-finite coefficient values,
- `dt <= 0`,
- `budget_b <= 0`,
- negative or non-integer `depth_hint`,
- `thickness_hint <= 0`,
- `width_hint <= 0`,
- invalid point shape; chart points must be `[x, y]`.

Validation errors are raised as `pygrc.core.InvalidLandscapeSeedError`.

## Seed Authoring Checklist

Before committing a new seed:

- [ ] Use quoted schema/version strings for readability.
- [ ] Keep source intent separate from runtime evidence.
- [ ] Use typed primitive fields before generic `hints`.
- [ ] Give every primitive a unique `id`.
- [ ] Verify every cross-reference resolves to an existing primitive.
- [ ] Keep containment acyclic and align `depth_hint` with parents.
- [ ] Keep `dt > 0`, `budget_b > 0` when present, `thickness_hint > 0`, and
  `width_hint > 0`.
- [ ] Put family-specific source details under a namespaced extension.
- [ ] Put historical broad-growth seeds under `configs/landscapes/seed/legacy/`.
- [ ] Run `load_landscape_seed(path)` before using the seed in lowering or
  replay.

## Relationship To Other Guides

- [Landscape Inference Reference Guide](LandscapeInference-ReferenceGuide.md)
  explains how observed runtime geometry is mapped back into this same seed
  language.
- [Motion Reference Guide](Motion-ReferenceGuide.md) explains how temporal
  motion records can be represented without creating a separate source
  ontology.
- [Landscape Compiler And Lowering Reference Guide](LandscapeCompiler-ReferenceGuide.md)
  covers family-specific compilation and lowering.

## Current Limitations

- The language is intentionally neutral; family-specific runtime semantics are
  consumed by compiler/lowering layers.
- Geometry hints are source-chart hints, not guaranteed runtime embeddings.
- Transport intent is not raw flux.
- Legacy growth seeds remain quarantined and diagnostic-only.
- Source preconditions do not count as runtime evidence.

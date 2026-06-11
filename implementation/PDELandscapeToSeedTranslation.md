# PDE Landscape To Seed Translation

This document defines how the current PDE landscape DSL should be translated
into the normalized `PyGRC` landscape seed schema.

It sits after:

- [`GRCL-Landscape-DSL-TranslationGuide.md`](./GRCL-Landscape-DSL-TranslationGuide.md)
- [`LandscapeSeedSchema.md`](./LandscapeSeedSchema.md)

and before:

- family-specific seed projectors,
- and PDE-derived parameter-family definitions.

Primary source inputs are the current PDE-side landscape materials:

- `rc-sim/papers/2026-02-ComposingCells.md`
- `rc-sim/experiments/scripts/landscape_schema.py`
- `rc-sim/configs/landscapes/*.json`

## 1. Role

The current PDE landscape JSON is a source DSL and compiler contract. It is not
yet the neutral seed format used by `PyGRC`.

This document defines the translation layer between them.

Its job is to answer:

- what maps directly,
- what becomes a neutral hint,
- what remains source/compiler metadata,
- what may be inferred in an optional enrichment pass,
- and what should not be translated into the neutral layer at all.

## 2. Main Translation Principle

The translator should preserve source meaning conservatively.

That means:

- explicit source structures translate directly,
- source compiler controls are preserved as source-side metadata or extensions,
- source-specific geometry conventions become hints rather than hard backend
  commitments,
- and semantically richer neutral primitives such as `plateau` and `saddle`
  should only be synthesized by an explicit enrichment pass.

The translation therefore has two modes.

### 2.1 Mode A: Lossless Source Normalization

This is the default and recommended first translator mode.

It performs:

- one-to-one mapping of explicit source primitives,
- parameter normalization,
- neutral hint extraction,
- transport-intent extraction,
- and preservation of source-only compile metadata under extensions.

It does not invent new structural primitives unless they are explicitly present
in the source.

### 2.2 Mode B: Semantic Enrichment

This is an optional second pass.

It may:

- synthesize `saddle` from routing-hub configurations,
- synthesize `plateau` from broader composed support structures,
- lift source naming or topology patterns into explicit neutral roles,
- and attach explanatory metadata documenting the inference.

This pass must be explicit because enrichment is interpretation, not direct
source transcription.

## 3. Source Contract Summary

The current PDE validator defines:

- top-level `schema_version`
- `meta`
- `params`
- `potential`
- `compile`
- `initial_flux`
- optional `geometry`
- `primitives`

Current source primitive types are only:

- `basin`
- `ridge`
- `valley`

The neutral seed vocabulary is intentionally richer:

- `basin`
- `plateau`
- `ridge`
- `valley`
- `junction`
- `saddle`

This means the translator must support both:

- direct primitive mapping,
- and explicit non-default enrichment rules for source-implied semantics.

## 4. Top-Level Mapping

The following table defines the baseline top-level mapping.

| PDE source field | Seed target | Rule |
| --- | --- | --- |
| `schema_version` | `meta.source_schema_version` | Preserve as source metadata |
| `meta.name` | `meta.name` | Direct |
| `meta.description` | `meta.description` | Direct |
| `meta.domain` | `meta.source_domain` | Preserve as source metadata |
| source spec path | `meta.source_reference` | Translator should attach if known |
| `params` | `constitutive_profile` | Normalize names and preserve values |
| `potential.type` | `constitutive_profile.potential.type` | Direct |
| `potential.params` | `constitutive_profile.potential.params` | Direct |
| `initial_flux` | `transport_intent` | Translate when enabled or channelized |
| `geometry` | `geometry_hints` plus source extension | Translate as source-chart hints |
| `compile` | `extensions.source_pde.compile` | Preserve, not elevate to neutral core |
| `potential.compile_policy` | `extensions.source_pde.potential_compile_policy` | Preserve as source/compiler metadata |

## 5. Constitutive Profile Translation

The current source `params` block uses PDE-style names.

Map it as follows:

| Source | Seed |
| --- | --- |
| `lambda_C` | `lambda_c` |
| `xi_C` | `xi_c` |
| `zeta_C` | `zeta_c` |
| `kappa_C` | `kappa_c` |
| `dt` | `dt` |

Potential maps directly:

- `potential.type` -> `constitutive_profile.potential.type`
- `potential.params` -> `constitutive_profile.potential.params`

### 5.1 Budget Mapping Rule

The current PDE DSL does not carry an explicit `GRC` budget field by default.

Use the following rule:

- if `compile.mass_normalization.mode == "target_mass"`, map
  `compile.mass_normalization.target` to `constitutive_profile.budget_b`
  as a source-derived initialization target,
- otherwise do not synthesize `budget_b` from compile controls alone.

Reason:

- `target_mass` is the closest source-side statement of intended total mass,
- while `target_mean` and `none` are compiler-side controls that do not
  directly define a portable cross-family coherence budget.

The original compile block should still be preserved under
`extensions.source_pde.compile`.

## 6. Primitive Mapping Rules

The translator should preserve source primitive identity by using:

- source `name` -> seed `id`

unless a caller explicitly requests a different ID-normalization policy.

## 6.1 Basin

Source fields:

- `type`
- `name`
- `parent`
- `center`
- `radius`
- `coherence`

Seed mapping:

| Source basin field | Seed field |
| --- | --- |
| `name` | `id` |
| `type=basin` | `type=basin` |
| `parent` | `parent_id` |
| `coherence` | `coherence_prior` |
| `center` | `chart_center_hint` |
| `radius` | `chart_scale_hint.radius` |

Additional rules:

- source `parent: null` becomes omitted `parent_id`
- if hierarchy depth is useful, the translator may compute `depth_hint` from
  the parent chain in the normalized output
- if the source name or context strongly implies a role such as `nucleus` or
  `cytoplasm`, the translator may attach `role`, but this should be treated as
  enrichment unless the source already labels it explicitly

## 6.2 Ridge

Source fields:

- `type`
- `name`
- `parent`
- `ridge_type`
- `inner_radius`
- `outer_radius`
- `interior_coherence`
- `exterior_coherence`
- optional v2 fields:
  - `shape_mode`
  - `anisotropy_ratio`
  - `orientation_deg`
  - `angular_modulation_amplitude`
  - `angular_modulation_phase_deg`
  - `distance_mode_override`

Seed mapping:

| Source ridge field | Seed field |
| --- | --- |
| `name` | `id` |
| `type=ridge` | `type=ridge` |
| `parent` | `owner_id` |
| `ridge_type` | `ridge_kind` |
| `inner_radius`, `outer_radius` | `thickness_hint` and chart-scale-related hints |
| `interior_coherence` | `interior_coherence_hint` |
| `exterior_coherence` | `exterior_coherence_hint` |

Recommended translation rules:

- set `thickness_hint = outer_radius - inner_radius` when both are present
- preserve `inner_radius` and `outer_radius` under primitive `hints` if exact
  radial source values are worth keeping
- map `orientation_deg` into `chart_principal_axis_hint` when possible
- map `anisotropy_ratio` and related modulation settings into
  `anisotropy_hint`
- preserve any unconsumed source ridge-shape fields under
  `primitive.extensions.source_pde`

### 6.2.1 Ridge Orientation Conversion

If the translator converts `orientation_deg` into
`chart_principal_axis_hint`, use:

- `chart_principal_axis_hint = [cos(theta), sin(theta)]`
- with `theta` in radians converted from degrees

This remains a neutral orientation hint, not a commitment to one later
discrete frame backend.

## 6.3 Valley

Source fields:

- `type`
- `name`
- `from`
- `to`
- `path_type`
- `width`
- `coherence`
- optional `control_points`

Seed mapping:

| Source valley field | Seed field |
| --- | --- |
| `name` | `id` |
| `type=valley` | `type=valley` |
| `from` | `from_id` |
| `to` | `to_id` |
| `path_type` | `path_hint` |
| `width` | `width_hint` |
| `coherence` | `coherence_prior` |
| `control_points` | `waypoints` or `hints.control_points` |

Recommended rule:

- use `waypoints` when the control points are intended as transport-path shape
  guidance,
- and preserve raw source control points under `hints.control_points` if a more
  source-authentic record is desired.

## 7. Source-Implied Structures

The current PDE DSL often encodes semantically richer structures by
composition. The translator must decide whether to:

- preserve the source composition only,
- or also synthesize an explicit neutral primitive.

The default should be conservative.

## 7.1 Saddle / Junction Inference

The source paper defines saddle points explicitly, but the current JSON schema
does not. Instead, some source landscapes encode routing structure as:

- a small hub basin,
- often with its own ridge,
- and multiple outgoing valleys.

Default translation rule:

- preserve the hub as a `basin`,
- preserve attached valleys as `valley`,
- and add a source-side annotation under `extensions.source_pde` such as
  `implied_role: saddle_like_hub` when the translator recognizes the pattern.

Optional enrichment rule:

- synthesize an additional neutral primitive with `type: saddle`
- with `host_id` equal to the hub basin,
- and `branch_target_ids` taken from the outgoing valleys.

This should be opt-in because it is an interpretation of composition, not a
direct source primitive.

## 7.2 Plateau Inference

The current source DSL does not define `plateau` as a first-class JSON
primitive even though the theory does.

Default translation rule:

- do not synthesize `plateau` automatically.

Optional enrichment rule:

- create `plateau` when a source family or translator profile explicitly marks a
  broad support region as weakly differentiated and multi-basin-hosting,
- and record the inference basis in metadata or extension notes.

This keeps the first translator stable and reproducible.

## 8. Geometry Translation

The current source `geometry` block is still PDE/compiler-oriented.

Source fields include:

- `distance_mode`
- `period_x`
- `period_y`

### 8.1 Geometry Mapping Rule

Map these into neutral hints, not hard backend commitments.

Recommended mapping:

| Source geometry field | Seed target |
| --- | --- |
| `distance_mode=euclidean` | `geometry_hints.source_chart: planar_hint` |
| `distance_mode=periodic_torus` | `geometry_hints.source_chart: planar_periodic_hint` |
| `period_x`, `period_y` | `geometry_hints.periodicity.{x,y}` or wrap-length hints |

Preserve the full original geometry block under:

- `extensions.source_pde.geometry`

Reason:

- the source is describing compilation geometry,
- while the seed should preserve only the portable geometric intent.

## 9. Compile Block Handling

The source `compile` block is primarily a compiler/runtime concern.

It may include:

- `composition_mode`
- `value_range`
- `mass_normalization`

Translation rule:

- preserve the full block under `extensions.source_pde.compile`
- do not elevate it into required neutral fields

Possible exception:

- `mass_normalization.mode == target_mass` may additionally inform
  `constitutive_profile.budget_b` as described earlier.

## 10. Initial Flux To Transport Intent

The current source `initial_flux` block is the bridge point for seed transport
intent.

Source fields:

- `enabled`
- `direction`
- `magnitude`
- `channels`

### 10.1 Baseline Translation Rule

If:

- `enabled == false`
- and `channels` is empty,

then omit `transport_intent` or emit an empty list.

If transport is declared:

- convert the source declaration into one or more `transport_intent` items,
- without translating directly into runtime flux values.

### 10.2 Direction Mapping

Recommended mapping:

| Source direction | Seed `mode` |
| --- | --- |
| `source_to_sink` | `directed_bias` |
| `custom` | `channel_preference` or `directed_bias`, depending on channels |
| `none` | omit transport intent |

### 10.3 Channel Mapping

For each source `initial_flux.channels[*]` item:

- `name` -> `id`
- `from` -> `sources`
- `to` -> `targets`
- `weight` -> `magnitude_hint`

If channel `type == valley`:

- try to bind the transport intent to the matching translated valley via
  `carrier_id`

If channel `type == basin_pair`:

- preserve it as a direct region-to-region transport preference without a
  carrier

The translator should also preserve the full original `initial_flux` block
under `extensions.source_pde.initial_flux`.

## 11. Metadata And Provenance

The translator should attach provenance so the seed can always be traced back
to the source spec.

Recommended metadata fields:

- `meta.source_kind: pde_landscape_dsl`
- `meta.source_reference`
- `meta.source_schema_version`
- `meta.translator_name`
- `meta.translator_version`
- `meta.translation_mode`

Allowed translation-mode values:

- `lossless_source_normalization`
- `semantic_enrichment`

## 12. Normalized Example Rules

## 12.1 Cell-4 Routing Example

For a source like `cell-4.json`:

- `routing_junction` remains a translated `basin` in default mode
- attached branch valleys remain ordinary `valley` primitives
- translator may annotate `routing_junction` with
  `extensions.source_pde.implied_role: saddle_like_hub`

Only the enrichment mode should additionally synthesize:

- `type: saddle`
- with `host_id: routing_junction`
- and `branch_target_ids` derived from outgoing valleys

## 12.2 S6 Periodic Seam Example

For a source like `s6-periodic-seam-ring.json`:

- the two seam basins map directly to `basin`
- the seam channel maps directly to `valley`
- `geometry.distance_mode: periodic_torus` becomes geometry hints plus preserved
  source geometry extension

The translator should not collapse periodic seam structure into ordinary planar
distance assumptions.

## 13. Loss Recording Rules

Any translator should record when the normalized seed does not preserve some
source distinction exactly.

Typical examples:

- a source ridge shape field preserved only under extensions
- a source routing hub not lifted into explicit `saddle`
- a source compile policy intentionally excluded from the neutral core

These records may live in:

- `meta.translation_notes`
- or `extensions.source_pde.translation_notes`

## 14. Immediate Next Step

After this document, the next implementation-facing artifact should be a
translator execution note or plan that defines:

- whether the first translator is documentation-only or code-generating,
- the exact normalization output shape for one or two canonical fixtures,
- and the enrichment rules that remain disabled by default in the first pass.

Canonical normalization targets now recorded in:

- [`../configs/landscapes/seed/cell-1.seed.yaml`](../configs/landscapes/seed/cell-1.seed.yaml)
- [`../configs/landscapes/seed/cell-4.seed.yaml`](../configs/landscapes/seed/cell-4.seed.yaml)
- [`../configs/landscapes/seed/s6-periodic-seam-ring.seed.yaml`](../configs/landscapes/seed/s6-periodic-seam-ring.seed.yaml)

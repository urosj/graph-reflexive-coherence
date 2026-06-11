# Landscape Seed Schema

This document defines the first family-neutral carrier for translating the
landscape DSL into `PyGRC`.

It comes after:

- [`GRCL-Landscape-DSL-TranslationGuide.md`](./GRCL-Landscape-DSL-TranslationGuide.md)

and before:

- family-specific projection rules,
- and PDE-derived parameter-family definitions.

Its purpose is to define:

- what the normalized seed document must contain,
- which parts are required across all families,
- which parts are optional neutral hints,
- and how family-specific enrichments can be attached without contaminating the
  neutral layer.

## 1. Role

The landscape seed schema is not:

- the original PDE DSL,
- a family-specific initialization format,
- or a serialized runtime state.

It is a normalized translation layer that preserves the source meaning in a
form that every `PyGRC` family can read.

This means the schema must do two things at once:

1. preserve the source ontology from the `GRCL` guide,
2. avoid forcing `GRCV2`, `GRCV3`, `GRC9`, and `GRC9V3` to share one internal
   storage model.

## 2. Design Principles

The schema follows these rules.

### 2.1 Preserve Meaning Before Mechanism

The schema should encode:

- support regions,
- interfaces,
- channels,
- routing sites,
- containment,
- constitutive profile,
- and transport intent.

It should not encode:

- runtime caches,
- solved gradients/Hessians,
- mutable flux state,
- or one family's internal graph or port layout.

### 2.2 Common Kernel Plus Extension Surface

Every valid seed must contain a portable common kernel.

On top of that, the schema may carry:

- optional neutral hints,
- and namespaced family-specific extension blocks.

This avoids the two bad extremes:

- a seed that is too weak to preserve landscape meaning,
- and a seed that bakes `GRCV3` or `GRC9` internals into the neutral layer.

### 2.3 Transport Intent Is Separate From Raw Flux

If the source declares preferred transport, the schema should store that as
transport intent, not as directly prescribed `J`.

Families remain free to realize that intent by:

- potential bias,
- conductance bias,
- coherence-gradient bias,
- initialization events,
- or other constitutively valid mechanisms.

### 2.4 Geometry Hints Are Allowed, Geometry Backends Are Not Required

The seed may carry geometry hints such as:

- source-chart anchors,
- source-chart scales,
- source-chart principal axes,
- and separation relations.

But it should not require all families to adopt one PDE metric backend or one
ambient coordinate dependence.

These hints are inherited from the source chart and are not ontological
coordinates of the realized `GRC` object.

### 2.5 Unsupported Extensions Must Be Ignored, Not Reinterpreted

If a seed contains an extension block for one family, other families should
ignore it unless they explicitly know how to consume it.

They must not silently reinterpret another family's extension as neutral truth.

## 3. Top-Level Shape

The normalized seed document should have the following top-level structure.

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

Only `transport_intent`, `geometry_hints`, and `extensions` may be omitted.

The required top-level fields are:

- `seed_schema`
- `seed_version`
- `meta`
- `constitutive_profile`
- `primitives`

## 4. Required Common Kernel

Every valid seed must preserve the following information.

### 4.1 Document Identity

The `meta` block should include:

- `name`
- `source_kind`
- `source_reference` if known
- `description` optional
- `tags` optional

Recommended `source_kind` values:

- `pde_landscape_dsl`
- `manual_seed`
- `translated_seed`

### 4.2 Constitutive Profile

The `constitutive_profile` block carries the neutral dynamical regime attached
to the seed.

It should include:

- `lambda_c`
- `xi_c`
- `zeta_c`
- `kappa_c`
- `dt`
- `potential`

The `potential` object should include:

- `type`
- `params`

Optional fields may include:

- `budget_b`
- `notes`
- `source_params`

This block is required because the landscape DSL does not just describe shape.
It also describes how the resulting support should evolve.

`budget_b` is optional but recommended when the translated seed is intended to
initialize a family with an explicit global coherence-budget invariant.

If present:

- it defines the target total coherence budget for initialization,
- and loaders may normalize coherence priors to this total exactly.

If absent:

- loaders may use family defaults,
- or treat the sum of realized priors as the implied initial budget.

### 4.3 Structural Primitives

The `primitives` array is the main body of the seed.

Each primitive must have:

- `id`
- `type`
- `label` optional
- `role` optional
- `tags` optional
- `hints` optional
- `extensions` optional

Supported neutral primitive types are:

- `basin`
- `plateau`
- `ridge`
- `valley`
- `junction`
- `saddle`

Each primitive type has additional required or recommended fields defined below.

## 5. Primitive Definitions

The schema keeps the primitive vocabulary close to the source ontology rather
than prematurely converting everything into one graph object model.

## 5.1 Basin

A `basin` represents a stable coherence-support region.

Required fields:

- `id`
- `type: basin`

Recommended fields:

- `role`
- `parent_id`
- `depth_hint`
- `coherence_prior`
- `chart_center_hint`
- `chart_scale_hint`
- `shape_hint`

Optional fields:

- `stability_class`
- `boundary_ids`
- `notes`

Example:

```yaml
- id: cytoplasm
  type: basin
  role: cytoplasm
  depth_hint: 0
  coherence_prior: 0.82
  chart_center_hint: [0.0, 0.0]
  chart_scale_hint:
    radius: 12.0
```

## 5.2 Plateau

A `plateau` represents a broad, weakly differentiated support region that may
host multiple later identity resolutions.

Required fields:

- `id`
- `type: plateau`

Recommended fields:

- `parent_id`
- `depth_hint`
- `coherence_prior`
- `chart_center_hint`
- `chart_scale_hint`

Optional fields:

- `stability_class`
- `hosted_primitive_ids`
- `notes`

The schema treats plateau as first-class because the semantic distinction is
real even when the source DSL currently encodes some plateaus compositionally.

`depth_hint` is optional and advisory. `parent_id` remains the authoritative
hierarchy relation.

## 5.3 Ridge

A `ridge` represents an interface or membrane-like barrier.

Required fields:

- `id`
- `type: ridge`

Recommended fields:

- `ridge_kind`
- `owner_id`
- `adjacent_ids`
- `interior_coherence_hint`
- `exterior_coherence_hint`
- `thickness_hint`

Optional fields:

- `chart_principal_axis_hint`
- `anisotropy_hint`
- `permeability_hint`
- `notes`

Recommended `ridge_kind` values:

- `boundary`
- `internal`
- `membrane`
- `separator`

`chart_principal_axis_hint` and `anisotropy_hint` are source-chart hints. They
are not direct commitments to a tensor representation or a port-row encoding.

## 5.4 Valley

A `valley` represents a transport corridor between support regions.

Required fields:

- `id`
- `type: valley`
- `from_id`
- `to_id`

Recommended fields:

- `path_hint`
- `width_hint`
- `coherence_prior`

Optional fields:

- `channel_role`
- `waypoints`
- `notes`

The valley primitive preserves corridor semantics even if a later family
realizes it as:

- one edge,
- many edges,
- or a more elaborate channel structure.

## 5.5 Junction / Saddle

A `junction` represents a routing or branch-selection site.

The schema also accepts `type: saddle` as a source-authentic alias when the
author wants to preserve the continuous-theory emphasis on curvature
degeneracy.

The normalization rule is:

- `junction` is the neutral routing term,
- `saddle` is an allowed source-facing alias,
- and projectors may preserve which spelling was used for documentation, but
  should treat them as the same primitive class unless they explicitly support
  a stronger distinction.

Required fields:

- `id`
- `type: junction` or `type: saddle`

Recommended fields:

- `host_id`
- `branch_target_ids`
- `junction_role`

Structural rule:

- a junction/saddle may omit `host_id`, but it must not be truly floating
- if `host_id` is omitted, `branch_target_ids` must contain at least one target
- family projectors may impose stronger realization requirements for hostless
  junctions, such as requiring a locational hint or an incident channel

Optional fields:

- `coherence_prior`
- `chart_center_hint`
- `notes`

This primitive exists so routing semantics do not disappear when the source DSL
currently encodes a junction indirectly via basin-plus-channel composition.

It should be read as the neutral bridge for:

- saddle-like decision structure in the continuous theory,
- and routing/junction structure in the graph-facing realization.

## 6. Neutral Hint Surface

Hints are allowed when they preserve source meaning without forcing one backend
implementation.

The allowed neutral hints are grouped here for clarity.

### 6.1 Geometry Hints

`geometry_hints` is an optional top-level block for document-wide hints.

It may include:

- `source_chart`
- `periodicity`
- `scale_units`
- `separation_hints`
- `coordinate_convention`

Examples:

- `source_chart: planar_hint`
- `periodicity: {x: false, y: false}`
- `scale_units: arbitrary`

Important boundary:

- these are hints,
- not obligations to use one Euclidean or PDE-native metric construction.

### 6.2 Primitive-Level Hints

The `hints` field on primitives may include information such as:

- approximate geometric placement,
- support scale,
- relative orientation,
- interface anisotropy,
- and intended relation to neighboring structures.

These hints should remain descriptive rather than backend-specific.

### 6.3 Separation Intent

If the source needs to preserve explicit separation semantics, that should be
represented as relation or hint data rather than as a hardcoded metric backend.

Examples of neutral separation intent:

- two regions are distinct but adjacent,
- one region encloses another,
- a ridge separates two basins,
- a valley is transport-preferred between two sites.

## 7. Transport Intent

`transport_intent` is an optional top-level array of source-declared transport
preferences.

Each transport-intent item should include:

- `id`
- `mode`
- `sources`
- `targets`

Recommended optional fields:

- `magnitude_hint`
- `priority`
- `carrier_id`
- `direction_hint`
- `notes`

Recommended `mode` values:

- `directed_bias`
- `channel_preference`
- `exchange`
- `broadcast`

Example:

```yaml
transport_intent:
  - id: nucleus_export
    mode: directed_bias
    sources: [nucleus]
    targets: [cytoplasm]
    carrier_id: er_valley_1
    magnitude_hint: 0.4
```

This block is intentionally separate from:

- constitutive coefficients,
- and runtime flux values.

## 8. Extension Policy

The schema explicitly allows family-specific extensions.

This is necessary because:

- some source seeds may want to carry `GRCV3`-specific initialization hints,
- some may want `GRC9`-specific mechanical or port hints,
- and those should not be forced into the neutral core.

For the theory-facing `GRCV3` rich-seed boundary, see:

- [GRCL-V3-Vocabulary.md](./GRCL-V3-Vocabulary.md)

### 8.1 Top-Level Extensions

The `extensions` object may contain namespaced sub-objects such as:

- `grcv2`
- `grcv3`
- `grc9`
- `grc9v3`
- `host`

Example:

```yaml
extensions:
  grc9:
    default_port_policy: balanced_open
  grcv3:
    initialize_signed_hessian: true
```

### 8.2 Primitive-Level Extensions

Each primitive may also contain an `extensions` block with the same namespaced
pattern.

Example:

```yaml
- id: membrane
  type: ridge
  extensions:
    grc9:
      preferred_row_family: 1
    grcv3:
      local_frame_hint: normal_aligned
```

### 8.3 Validation Rule

The neutral loader should:

- validate the common kernel,
- preserve extension blocks,
- and ignore unsupported extension namespaces.

It should not:

- fail just because an unknown family namespace is present,
- unless a strict-validation mode is explicitly requested.

## 9. Validation Rules

The seed schema should enforce these baseline rules.

### 9.1 Required Structural Rules

- `seed_schema` and `seed_version` must be present.
- `meta`, `constitutive_profile`, and `primitives` must be present.
- primitive `id` values must be unique.
- all cross-references such as `parent_id`, `owner_id`, `from_id`, `to_id`,
  `host_id`, and `branch_target_ids` must resolve to existing primitive IDs.
- containment via `parent_id` must be acyclic.

### 9.2 Required Constitutive Rules

- `lambda_c`, `xi_c`, `zeta_c`, `kappa_c`, and `dt` must be present in
  `constitutive_profile`.
- `potential.type` must be present.
- `potential.params` must exist, even if empty.
- if `budget_b` is present, it must be positive.

### 9.3 Neutrality Rules

- no required field may depend on one family's runtime data structures.
- no neutral field may directly encode solved flux values or cached
  differential summaries as if they were source truth.
- family-specific details must live under `extensions`, not under neutral
  fields with overloaded meaning.
- if both `parent_id` and `depth_hint` are present, `depth_hint` must not
  contradict the implied containment depth.

## 10. Normalized Example

```yaml
seed_schema: pygrc.landscape_seed
seed_version: "0.1"

meta:
  name: eukaryotic_cell_seed
  source_kind: pde_landscape_dsl
  source_reference: papers/2026-02-ComposingCells.md

constitutive_profile:
  lambda_c: 1.0
  xi_c: 1.5
  zeta_c: 0.8
  kappa_c: 0.6
  dt: 0.05
  budget_b: 1000.0
  potential:
    type: double_well
    params:
      a: 1.0
      b: 0.15

primitives:
  - id: cytoplasm
    type: basin
    role: cytoplasm
    depth_hint: 0
    coherence_prior: 0.85
    chart_center_hint: [0.0, 0.0]
    chart_scale_hint:
      radius: 12.0

  - id: membrane
    type: ridge
    ridge_kind: membrane
    owner_id: cytoplasm
    adjacent_ids: [cytoplasm]
    thickness_hint: 1.2
    chart_principal_axis_hint: [0.0, 1.0]
    anisotropy_hint:
      mode: normal_barrier

  - id: nucleus
    type: basin
    parent_id: cytoplasm
    role: nucleus
    depth_hint: 1
    coherence_prior: 0.92
    chart_center_hint: [0.0, 0.0]
    chart_scale_hint:
      radius: 4.0

  - id: routing_plateau
    type: plateau
    parent_id: cytoplasm
    depth_hint: 1
    coherence_prior: 0.55

  - id: er_valley_1
    type: valley
    from_id: nucleus
    to_id: cytoplasm
    width_hint: 0.8
    path_hint: curved

  - id: export_junction
    type: saddle
    host_id: routing_plateau
    branch_target_ids: [cytoplasm, nucleus]

transport_intent:
  - id: nucleus_export
    mode: directed_bias
    sources: [nucleus]
    targets: [cytoplasm]
    carrier_id: er_valley_1
    magnitude_hint: 0.3

geometry_hints:
  source_chart: planar_hint
  periodicity:
    x: false
    y: false

extensions:
  grc9:
    default_port_policy: balanced_open
```

## 11. Loader Obligations

Any family-specific projector that reads this schema should:

1. validate the common kernel,
2. preserve unknown extension blocks,
3. consume only the namespaces it understands,
4. record any semantic losses or approximations it introduces,
5. and avoid silently collapsing one primitive type into another without
   documentation.

Examples:

- if `GRCV2` approximates a plateau as a region ensemble, that should be
  documented at the projector level,
- if `GRC9` interprets ridge orientation using row families, that mapping
  belongs in the `GRC9` projector note rather than in this schema.

## 12. Immediate Follow-On Work

This schema enables the next artifacts:

1. a source-landscape translator from PDE DSL to normalized seed,
2. family-specific seed projectors,
3. and parameter-family definitions built on top of normalized seeds or their
   projections.

The immediate next implementation-facing document should define:

- translation rules from PDE landscape JSON into this schema,
- including how current source primitives map into normalized primitive
  objects,
- and how source compiler artifacts are filtered or preserved as hints.

That follow-on document is:

- [`PDELandscapeToSeedTranslation.md`](./PDELandscapeToSeedTranslation.md)

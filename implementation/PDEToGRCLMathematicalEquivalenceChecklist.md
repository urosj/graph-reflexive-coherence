# PDE To GRCL Mathematical Equivalence Checklist

This document records what **can** and **cannot** currently be defended as
mathematical equivalence between the PDE landscape DSL and the neutral `GRCL`
seed layer.

Its purpose is to prevent the project from making a stronger claim than the
implementation supports.

At Phase L, the correct target is:

- **seed-layer mathematical invariance**

not:

- full PDE-field reconstruction equivalence,
- full compiled-landscape numerical equivalence,
- or later family-realization equivalence.

## 1. Scope

This checklist applies to:

- PDE landscape source documents,
- translation into normalized `LandscapeSeed` / `GRCL` objects,
- and validation of the resulting seed against source-side invariants.

It does **not** yet certify:

- equality of the compiled scalar field `C(x)`,
- equality of PDE gradients, Hessians, or curvature fields,
- equality of later `GRCV2`, `GRCV3`, or `GRC9` realizations,
- or equality of dynamics after reflexive stepping begins.

## 2. Defensible Equivalence Claim

At the current implementation boundary, the strongest defensible claim is:

> The translated `GRCL` seed preserves the source PDE landscape's declared
> constitutive regime, explicit primitive geometry, containment, periodicity
> intent, transport intent, and compile/provenance metadata in a normalized
> cross-family carrier.

That claim is stronger than "topological mapping only", but weaker than
"numerically identical PDE field".

## 3. Required Seed-Layer Invariants

The following invariants must hold for a translation to count as mathematically
faithful at the `GRCL` seed layer.

### 3.1 Constitutive Profile Invariants

- `lambda_C -> lambda_c`
- `xi_C -> xi_c`
- `zeta_C -> zeta_c`
- `kappa_C -> kappa_c`
- `dt -> dt`
- `potential.type` is preserved exactly
- `potential.params` is preserved exactly

### 3.2 Budget Intent Invariant

If:

- `compile.mass_normalization.mode == target_mass`

then:

- `compile.mass_normalization.target -> constitutive_profile.budget_b`

Otherwise:

- `budget_b` must remain unset rather than being synthesized from weaker
  compile controls.

### 3.3 Basin Invariants

For each explicit PDE `basin`:

- source `name -> seed.id`
- source primitive remains `type: basin`
- `parent -> parent_id`
- `coherence -> coherence_prior`
- `center -> chart_center_hint`
- `radius -> chart_scale_hint.radius`
- `depth_hint` matches the source parent chain

### 3.4 Ridge Invariants

For each explicit PDE `ridge`:

- source `name -> seed.id`
- source primitive remains `type: ridge`
- `parent -> owner_id`
- `ridge_type -> ridge_kind`
- `interior_coherence -> interior_coherence_hint`
- `exterior_coherence -> exterior_coherence_hint`
- `thickness_hint == outer_radius - inner_radius`
- `inner_radius` and `outer_radius` remain recoverable under `hints`
- `orientation_deg` maps to `chart_principal_axis_hint`
- anisotropy-related fields remain recoverable under `anisotropy_hint`

### 3.5 Valley Invariants

For each explicit PDE `valley`:

- source `name -> seed.id`
- source primitive remains `type: valley`
- `from -> from_id`
- `to -> to_id`
- `path_type -> path_hint`
- `width -> width_hint`
- `coherence -> coherence_prior`
- `control_points -> waypoints`

### 3.6 Geometry Intent Invariants

If PDE `geometry.distance_mode == euclidean`:

- `geometry_hints.source_chart == planar_hint`

If PDE `geometry.distance_mode == periodic_torus`:

- `geometry_hints.source_chart == planar_periodic_hint`
- `period_x` / `period_y` induce periodicity flags under
  `geometry_hints.periodicity`

The original PDE geometry block must also remain preserved under:

- `extensions.source_pde.geometry`

### 3.7 Transport Intent Invariants

The translator must not inject direct runtime flux values.

Instead:

- disabled + channel-free `initial_flux` becomes no `transport_intent`
- channelized source transport becomes `SeedTransportIntent`
- valley-like transport channels bind to a translated valley via `carrier_id`
  when possible

### 3.8 Provenance And Compile Invariants

The following must remain traceable:

- source schema version
- source description/domain/tags
- translator identity and translation mode
- source compile block
- source potential compile policy
- source initial flux block
- source metadata not elevated into neutral core

These belong under:

- `meta.*`
- `extensions.source_pde.*`

according to the neutral-seed boundary.

### 3.9 Lossless-Mode Non-Enrichment Invariant

When translation mode is:

- `lossless_source_normalization`

the translator must **not** synthesize:

- `plateau`
- `junction`
- `saddle`

unless the source DSL declared an explicit primitive of that kind.

## 4. What This Checklist Does Not Yet Prove

The following still remain open:

### 4.1 PDE Field Equivalence

We do not yet prove that the seed reconstructs the same compiled scalar field
`C(x)` as the PDE compiler.

### 4.2 Differential Equivalence

We do not yet prove equivalence of:

- gradients,
- Hessians,
- curvature,
- or decision/saddle structure as a field property.

### 4.3 Compile Policy Numerical Equivalence

Preserving:

- `compile`,
- `value_range`,
- and `potential_compile_policy`

under `extensions.source_pde` means the information is retained.

It does **not** yet mean the translated neutral seed reproduces the exact
numerical effect of those compiler policies.

### 4.4 Later Family Realization Equivalence

We do not yet prove that:

- `GRCV2`,
- `GRCV3`,
- `GRC9`,
- or `GRC9V3`

realize the seed in a way that reproduces the original PDE landscape
quantitatively.

That will require projector- and family-level validation later.

## 5. Executable Enforcement

Phase L now includes an executable validator:

- `src/pygrc/landscapes/equivalence.py`
- `validate_pde_seed_translation_equivalence(...)`

This validator enforces the seed-layer invariants listed above and is covered by
tests under:

- `tests/landscapes/test_pde_equivalence.py`

## 6. Consequence For Claims

When discussing current Phase L status, the correct statement is:

- the PDE-to-`GRCL` bridge is now tested for seed-layer mathematical
  invariants

and the incorrect statement would be:

- the PDE landscape is already proven numerically equivalent to later graph
  realizations

The latter remains future work.

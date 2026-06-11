# Landscape To GRC Plan

This document defines the recommended translation path from the PDE landscape
language into the `PyGRC` family implementations.

Primary source inputs:

- `rc-sim/papers/2026-02-ComposingCells.md`
- `rc-sim/configs/landscapes/README.md`
- representative landscape specs under:
  - `rc-sim/configs/landscapes/*.json`

This note exists because the landscape layer is more fundamental than the PDE
runtime-regime layer for initializing meaningful discrete-family states.

Theory-first prerequisite:
[`GRCL-Landscape-DSL-TranslationGuide.md`](./GRCL-Landscape-DSL-TranslationGuide.md)

Neutral carrier schema:
[`LandscapeSeedSchema.md`](./LandscapeSeedSchema.md)

PDE-to-seed translation rules:
[`PDELandscapeToSeedTranslation.md`](./PDELandscapeToSeedTranslation.md)

## 1. Main Conclusion

Before defining cross-model parameter families, `PyGRC` should define how the
landscape language translates into `GRC`.

The correct order is:

1. theory-facing landscape DSL translation guide
2. family-neutral landscape seed schema
3. PDE landscape to normalized seed translation rules
4. landscape language to family-neutral structural seed plan
5. family-specific realization
6. regime / parameter families on top of that realization

This avoids conflating:

- structural composition of the organism/substrate,

with:

- dynamic regime selection.

Those are not the same thing.

## 2. Why Landscape Translation Comes First

The PDE landscape specs are not just field snapshots or arbitrary initializer
files. They already encode a compositional ontology:

- basins
- ridges
- valleys
- routing-junction / saddle-like structures
- parent / containment relations
- potential family
- initial flux intent
- constitutive coefficients such as:
  - `lambda_C`
  - `xi_C`
  - `zeta_C`
  - `kappa_C`
  - `dt`

That means the landscape layer is already much closer to the theoretical RC
object model than later PDE runtime knobs like:

- `nx`
- `ny`
- `dx`
- `metric_blend`
- determinant regularization settings
- rendering/storage controls

So if `PyGRC` wants to inherit something principled from the PDE program, the
landscape language is the better starting point.

## 3. Three-Layer Translation Architecture

The cleanest architecture is a three-layer bridge.

## 3.1 Layer 1: Landscape Language

This is the source DSL used in the PDE program.

Examples from the specs:

- `type = basin`
- `type = ridge`
- `type = valley`
- `ridge_type = boundary | internal`
- `parent`
- `from`
- `to`
- `center`
- `radius`
- `inner_radius`
- `outer_radius`
- `width`
- `control_points`
- `coherence`

This layer should remain source-authentic and not be modified to fit one
particular discrete family.

## 3.2 Layer 2: Family-Neutral Structural Seed

This is the new layer `PyGRC` should define explicitly.

Its job is to represent:

- structural regions,
- interfaces,
- transport channels,
- routing/decision junctions,
- containment relations,
- constitutive coefficients,
- and initial priors for coherence / flux,

in a way that is independent of whether the target family is:

- `GRCV2`
- `GRCV3`
- `GRC9`
- `GRC9V3`

This is the key abstraction that is currently missing.

## 3.3 Layer 3: Family-Specific Projection

Each family then translates the structural seed into its own native substrate:

- `GRCV2` weighted graph
- `GRCV3` weighted graph + semantic lift
- `GRC9` mechanical nine-slot substrate
- `GRC9V3` hybrid substrate/semantic realization

This is where family differences belong.

## 4. Proposed Family-Neutral Structural Vocabulary

The structural seed should likely contain a vocabulary like this.

### 4.1 Regions

Represents basin-like coherent support units.

Suggested fields:

- `id`
- `role`
- `parent_region_id`
- `chart_center_hint`
- `chart_scale_hint`
- `coherence_prior`
- `tags`

Examples of `role`:

- `cytoplasm`
- `nucleus`
- `organelle`
- `junction`
- `anchor`

### 4.2 Interfaces

Represents ridge-like membrane / boundary structures.

Suggested fields:

- `id`
- `interface_type`
- `owner_region_id`
- `adjacent_region_ids`
- `inner_scale_hint`
- `outer_scale_hint`
- `interior_coherence`
- `exterior_coherence`
- `tags`

Examples of `interface_type`:

- `boundary`
- `internal`

### 4.3 Channels

Represents valley-like transport pathways.

Suggested fields:

- `id`
- `from_region_id`
- `to_region_id`
- `path_hint`
- `width_hint`
- `coherence_prior`
- `tags`

Examples of `path_hint`:

- `bezier`
- `straight`
- `periodic_wrap`

### 4.4 Junctions

Represents routing/saddle-like branching sites.

Suggested fields:

- `id`
- `region_id`
- `junction_type`
- `branch_targets`
- `tags`

In many cases, the source landscape already encodes this as a small basin plus
channel structure. The neutral seed should preserve that role even if it is
implemented through ordinary regions plus channels.

### 4.5 Constitutive Profile

Represents transferable constitutive coefficients and potential family.

Suggested fields:

- `lambda_c`
- `xi_c`
- `zeta_c`
- `kappa_c`
- `dt`
- `potential_type`
- `potential_params`

### 4.6 Initial Flux Profile

Represents initial transport intent if present in the landscape.

Suggested fields:

- `enabled`
- `direction_mode`
- `magnitude`
- `channel_hints`

## 5. Primitive Mapping Recommendations

The following mappings are recommended.

## 5.1 Basin -> Region

Source meaning from `2026-02-ComposingCells.md`:

- stable coherence accumulation
- identity-support unit

Recommended neutral mapping:

- basin becomes a `Region`

What to preserve:

- name
- parent relation
- center
- radius / scale
- coherence
- semantic role

## 5.2 Ridge -> Interface

Source meaning:

- membrane-like steep gradient boundary
- internal or external separation structure

Recommended neutral mapping:

- ridge becomes an `Interface`

Important caution:

- a ridge should not usually become an ordinary identity-support node by
  default,
- because its semantics are boundary/interface, not accumulation basin.

What to preserve:

- owner / parent relation
- `ridge_type`
- thickness hint (`inner_radius`, `outer_radius`)
- interior / exterior coherence contrast

## 5.3 Valley -> Channel

Source meaning:

- transport pathway
- flux-supporting connector between basins

Recommended neutral mapping:

- valley becomes a `Channel`

What to preserve:

- endpoints
- width
- path type
- control points
- coherence prior

This is the cleanest primitive mapping.

## 5.4 Saddle / Routing Junction -> Junction Role

The paper describes saddles as decision points, but the actual landscape specs
often encode them as:

- a small hub basin,
- plus outgoing valleys.

Recommended neutral mapping:

- preserve the junction role explicitly,
- but do not force a special substrate object unless the target family needs it

So the neutral seed should allow:

- a region with role `junction`
- plus outgoing channels
- plus optional explicit `Junction` metadata

## 5.5 Parent -> Containment Relation

The `parent` field in the landscape language is highly important and should not
be dropped.

Recommended neutral mapping:

- `parent` becomes `parent_region_id` or equivalent containment metadata

This matters especially for:

- `GRCV3` hierarchy semantics,
- compartment interpretation,
- and later mechanical layout priors in `GRC9`.

## 6. What Transfers Directly From Landscape Specs

The following fields are structurally transferable:

- primitive types and names
- containment relations
- local coherence priors
- characteristic scales
- channel widths / path hints
- constitutive coefficients:
  - `lambda_C`
  - `xi_C`
  - `zeta_C`
  - `kappa_C`
  - `dt`
- potential family and potential parameters
- initial flux intent

These should be treated as the first bridge surface.

## 7. What Does Not Transfer Directly

The following are not direct discrete-family semantics:

- PDE grid size:
  - `nx`
  - `ny`
  - `dx`
- compile-time field composition details
- field-range clamp policies
- profile remap policies
- visualization/export settings
- numerical regularization controls

These belong either to:

- PDE implementation,
- or to a later family-specific compiler/projector,

not to the family-neutral structural seed.

## 8. Family-Specific Projection Guidance

## 8.1 `GRCV2`

Recommended projection:

- region -> node
- channel -> edge
- interface -> metadata on adjacent nodes/edges or explicit edge weighting hints
- junction -> node with routing role
- containment -> metadata only

This keeps `GRCV2` simple while still inheriting landscape structure.

Likely outputs:

- initial weighted graph
- node coherence priors
- edge/channel priors
- boundary/interface metadata

## 8.2 `GRCV3`

Recommended projection:

- same structural substrate as `GRCV2`
- plus richer semantic state derived from:
  - roles
  - containment
  - interface/channel semantics
  - junction annotations

`GRCV3` is where the landscape language becomes especially valuable because it
can inform:

- basin attributes,
- hierarchy tracking,
- precursor/spark interpretation,
- and semantic routing structure.

## 8.3 `GRC9`

Recommended projection:

- do not force a literal `region -> node`, `channel -> edge` reading only
- use the structural seed as a mechanical layout prior

In particular:

- interfaces may map more directly into mechanical constraints
- channels may map into preferred port-to-port routing
- junction roles may map into valence/refinement hotspots

So the same seed is still useful, but the projection should be substrate-aware.

## 8.4 `GRC9V3`

Recommended projection:

- combine the semantic use of the `GRCV3` projection
- with the mechanical use of the `GRC9` projection

This is one reason the family-neutral seed is worth defining now.

## 9. Relation To Parameter Families

Parameter families should be defined **after** this translation layer.

Reason:

- `cell-1`, `cell-4`, `s5`, and `s6` are not just “parameter settings”
- they are structural compositions

So parameter families should sit on top of:

- a translated structural seed,
- not in place of it.

The correct later order is:

1. choose a structural landscape seed
2. project it into a family substrate
3. choose a dynamic regime family

This will keep:

- structure
- and dynamics

from being mixed together too early.

## 10. Recommended Planning Follow-Ups

After this plan, the next recommended planning documents are:

1. `implementation/GRCL-Landscape-DSL-TranslationGuide.md`
2. `implementation/LandscapeSeedSchema.md`
3. `implementation/ParameterFamiliesPlan.md`
4. later, possibly:
   - `implementation/LandscapeProjectionTestPlan.md`

## 11. Immediate Next Step

Before creating code, we should define:

- the theory-facing primitive translation guide,
- the exact neutral seed schema,
- field classification:
  - structural
  - constitutive
  - compiler-only
- and the first `GRCV2` projection rule set.

That should happen in the eventual implementation plan for the landscape bridge
or as a dedicated schema note.

## 12. Final Recommendation

Yes: the landscape language should be translated first.

It is the correct bridge between:

- PDE composition,
- and discrete-family initialization.

Only after that theory-facing translation exists should `PyGRC` lock seed
schema, projection rules, and example parameter families, because those later
artifacts must act on already-defined structural meanings rather than trying to
substitute for them.

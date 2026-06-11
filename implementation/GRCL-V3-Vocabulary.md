# GRCL-v3 Vocabulary

## Purpose

This document defines the **theory-facing vocabulary** for `GRCL-v3`, the
`GRCV3`-specific extension surface that sits on top of the neutral/common
landscape seed schema.

It answers one question precisely:

- what may a `GRCV3`-rich seed express that neutral/common `GRCL`
  intentionally cannot?

This note is the Stage 0 artifact referenced in:

- [GRCL-V3-ImplementationPlan.md](./GRCL-V3-ImplementationPlan.md)

It is not yet a complete implementation checklist.
It is the semantic boundary that later schema, validation, and projector work
must obey.

It also answers the deeper language question behind this arc:

- how do we give raw geometric and constitutive structure a truthful
  high-level language?

`GRCL-v3` is not just a list of names for things that already happened at
runtime.
It is a set of source-side structural distinctions that let us author,
constrain, and reason about raw geometry in behavioral terms.
In that sense, the project is not merely “running a simulation.”
It is building a language for specifying the conditions under which particular
phenomenology can or cannot emerge.

## 1. Role

`GRCL-v3` exists because the neutral/common seed layer is intentionally
portable across families, while `GRCV3` needs some source-side geometry-bearing
information that cannot always be reconstructed from:

- primitive identity,
- containment,
- coherence priors,
- transport intent,
- and generic chart hints alone.

So `GRCL-v3` is a **constructive geometry extension**.

It is not:

- a runtime cache format,
- a shortcut for directly storing `GRCV3` basin attributes,
- a way to prescribe solved gradients, Hessians, or fluxes,
- or a replacement for the neutral/common seed schema.

## 2. The Core Distinction

The correct distinction is:

- neutral/common `GRCL` expresses **semantic landscape ontology**
- `GRCL-v3` expresses **family-specific geometry realization intent**

That means `GRCL-v3` may say:

- how a semantic center should be surrounded by support structure,
- how branch interfaces are distinguished locally,
- which local direction is intended to be weak or nearly degenerate,
- how a ridge should realize as a support arc or boundary stencil,
- and how a valley/channel should preserve interior geometry rather than
  collapsing to one abstract edge

But it may not say:

- “the gradient is exactly this vector”
- “the Hessian is exactly this matrix”
- “this node is already a spark candidate”
- “this primitive has already collapsed into this basin identity”

In short:

- `GRCL-v3` may define the **construction** from which geometry should emerge
- it may not define the **solved geometry** itself as source truth

## 3. Placement In The Seed Schema

`GRCL-v3` lives under the extension policy already allowed by
[LandscapeSeedSchema.md](./LandscapeSeedSchema.md).

The only correct placement is:

- top-level `extensions.grcv3`
- primitive-level `extensions.grcv3`

No `GRCL-v3` field should be introduced into the neutral/common kernel unless
it is later proven to be cross-family rather than `GRCV3`-specific.

## 4. Ontological Rule

Every `GRCL-v3` field must satisfy this test:

1. it is part of the **source-side construction** of local geometry
2. it can be known before the `GRCV3` reflexive loop runs
3. it is not merely a hidden encoding of solved runtime state

If a proposed field fails any of those three conditions, it does not belong in
`GRCL-v3`.

## 5. What `GRCL-v3` Is Allowed To Express

The allowed vocabulary is grouped by semantic role.

## 5.1 Realization Vocabulary

This group defines how a primitive should lower into a local `GRCV3` motif.

Suggested location:

- `primitive.extensions.grcv3.realization`

Allowed meanings:

- `kind`
  - the intended motif family
  - examples:
    - `support_patch`
    - `junction_motif`
    - `boundary_arc`
    - `channel_chain`

- `support_count`
  - how many support nodes should participate in the first lowering
  - this is constructive motif size, not a runtime node count guarantee across
    all later refinements

- `radius_scale`
  - the intended local support radius relative to the primitive chart scale
  - this is a source-side geometric proportion, not a solved metric distance

- `support_angles`
  - explicit angular ordering of support sites around a semantic center
  - valid only as source-side layout intent

- `branch_order`
  - canonical ordering of branch interfaces around a junction/saddle-like site

- `attachment_mode`
  - how valleys/ridges/channels attach to the realized motif
  - examples:
    - `center_only`
    - `support_nearest`
    - `branch_interface`

What this vocabulary means:

- the source is no longer saying only “this thing is a junction”
- it is saying “this junction should realize as this local stencil”

## 5.2 Local Geometry Vocabulary

This group defines local geometry **intent**, not solved differential values.

Suggested location:

- `primitive.extensions.grcv3.local_geometry`

Allowed meanings:

- `frame_mode`
  - how the local chart should be interpreted when lowering the motif
  - examples:
    - `chart_aligned`
    - `radial_tangent`
    - `branch_ordered`

- `axis_roles`
  - names for the local axes or support directions
  - examples:
    - `radial`
    - `tangent`
    - `branch_0`
    - `branch_1`

- `weak_axis_role`
  - which axis is intended to be the locally weak or near-degenerate direction
  - this is allowed because it is a **construction target**, not a solved
    Hessian value

- `symmetry_class`
  - qualitative intended symmetry of the local motif
  - examples:
    - `radial`
    - `bilateral`
    - `cross`
    - `branch_biased`

- `center_role`
  - whether the semantic center is intended as:
    - `anchor`
    - `interior_probe`
    - `routing_core`

What this vocabulary means:

- `GRCL-v3` may tell the projector which local directions matter
- but it still may not prescribe the gradient/Hessian numbers that later arise
  from the lowered structure

## 5.3 Curvature-Intent Vocabulary

This group allows **qualitative curvature intent**.
It must remain qualitative or ordinal.

Suggested location:

- `primitive.extensions.grcv3.curvature_intent`

Allowed meanings:

- `class`
  - qualitative local regime
  - examples:
    - `stable_interior`
    - `near_degenerate`
    - `boundary_barrier`
    - `channel_axis`

- `stable_axis_roles`
  - which axis roles are intended to remain strongly stabilizing

- `weak_axis_role`
  - repeated here if the curvature intent needs to name the weak direction

- `ordering`
  - relative ordering only, not magnitudes
  - example:
    - `weak << stable`

Forbidden meanings:

- explicit eigenvalues
- explicit Hessian matrix entries
- explicit signed-Hessian snapshots
- explicit `hessian_sign`

Rationale:

- the source may declare that one axis is intended to be weak
- it may not declare the solved curvature tensor that the runtime should have

## 5.4 Interface Vocabulary

This group expresses how local interfaces correspond to semantic neighbors.

Suggested location:

- `primitive.extensions.grcv3.interfaces`

Allowed meanings:

- `branch_targets`
  - a stable mapping from local branch roles to neighboring primitives
  - for the current executable language, these neighbors are specifically the
    primitives connected by incident **valley/channel** carriers
  - this is a transport-incidence contract, not a generic adjacency contract

- `boundary_roles`
  - labels for local boundary sectors or support arcs

- `channel_roles`
  - labels for channels that must attach to distinct local interfaces

- `preferred_attachment_sites`
  - which support/branch roles a ridge or valley should attach to

This matters because `GRCV3` often needs more than one edge incident on a
semantic primitive. The source may need to preserve **which local side** of the
primitive an interface belongs to.

Important boundary:

- `branch_targets` should name the neighbors reached through junction/saddle
  branch transport
- ridge-adjacent shells or clamp-like boundary shells do **not** belong in
  `branch_targets`
- those should instead be expressed through:
  - `boundary_roles`
  - `preferred_attachment_sites`
  - and, where needed, `boundary_geometry`

So if a source needs to say:

- “this side of the junction faces an upper shell through a boundary clamp”

that is boundary/interface semantics, not branch-target semantics.

### 5.4.1 Pressure-Boundary / Active-Frontier Intent

Pressure-boundary language belongs to the interface vocabulary when it is used
for `GRCV3`.

In `GRCL-v3`, a pressure boundary means:

- a source-authored boundary/interface region that may serve as active-frontier
  birth provenance in an opt-in `GRCV3` runtime,
- a place where outward flux pressure may later be measured by the runtime,
- and a family-local attachment intent that can be preserved by lowering.

It does not mean:

- GRC9/GRC9V3 nine-port capacity,
- GRC9/GRC9V3 inactive-port eligibility,
- GRC9/GRC9V3 `front_capacity_source`,
- a solved birth event,
- or automatic runtime growth.

Source-side representation should use existing `GRCL-v3` interface geometry
where possible:

- `boundary_roles`
  - may include a role such as `pressure_boundary`
  - this marks the intended boundary/interface sector
- `preferred_attachment_sites`
  - may map that role to the local support site where the frontier should be
    preserved
- `boundary_geometry`
  - may describe the structural boundary support around that role
- `channel_geometry`
  - may describe the transport channel that creates outward flux pressure
    across or toward that role

The runtime activation contract is deliberately separate from the vocabulary.
For compatibility with existing `GRCV3` seeds and results:

```text
frontier_birth_mode = disabled | active_frontier_pressure
frontier_birth_strict = warn | error | allow
```

The default is strict:

- missing `frontier_birth_mode` means `disabled`,
- explicit `frontier_birth_mode = disabled` means current no-birth behavior,
- authored pressure-boundary/frontier seeds should prefer
  `frontier_birth_mode = active_frontier_pressure`,
- only explicit `frontier_birth_mode = active_frontier_pressure` may enable
  frontier birth logic,
- `frontier_birth_strict = warn` warns once when frontier candidates exist but
  node birth is disabled,
- `frontier_birth_strict = error` is preferred for source/evidence runs that
  declare frontier candidates and should not silently become no-birth,
- `frontier_birth_strict = allow` is reserved for explicit no-birth controls
  and legacy compatibility lanes,
- vocabulary/lowering intent alone does not activate birth,
- unknown mode or strictness values must fail validation.

If a future lowering path needs to preserve pressure-boundary provenance for
runtime telemetry, it should use family-native `GRCV3` names such as:

```text
frontier_source = pressure_boundary
```

It must not write the GRC9/GRC9V3 field:

```text
front_capacity_source = pressure_boundary
```

This preserves the semantic distinction:

- ridge / membrane boundary: internal separator geometry,
- valley / channel: transport connector geometry,
- active frontier / pressure boundary: possible birth-front provenance,
- system boundary: open-system exchange boundary.

## 5.5 Ridge/Boundary Vocabulary

This group is specific to support boundaries and membrane-like structures.

Suggested location:

- `primitive.extensions.grcv3.boundary_geometry`

Allowed meanings:

- `realization_kind`
  - examples:
    - `support_arc`
    - `double_support_arc`
    - `barrier_stencil`

- `normal_role`
  - which local role acts as outward normal

- `tangent_role`
  - which local role acts as tangent direction

- `arc_span`
  - qualitative or geometric span of the boundary support structure

- `support_distribution`
  - how explicit boundary support nodes are distributed across the arc

What this means:

- a ridge can preserve how a boundary should be constructed locally
- without claiming that the realized metric has already been solved

## 5.6 Channel Vocabulary

This group is specific to valleys or transport corridors.

Suggested location:

- `primitive.extensions.grcv3.channel_geometry`

Allowed meanings:

- `realization_kind`
  - examples:
    - `single_channel`
    - `double_channel`
    - `curved_chain`

- `interior_count`
  - intended count of interior channel support nodes

- `waypoint_policy`
  - how source waypoints should be preserved
  - examples:
    - `preserve_all`
    - `midpoint_only`
    - `fit_curvature`

- `entry_role`
- `exit_role`
  - which local roles on the adjacent motifs the channel should attach to

This is allowed because it defines source-side transport geometry, not solved
transport flux.

## 5.7 Top-Level Lowering Contract Vocabulary

Some `GRCL-v3` content belongs at the top level because it constrains the whole
seed, not one primitive.

Suggested location:

- `extensions.grcv3`

Allowed meanings:

- `contract_version`
  - identifies the expected rich-seed contract revision

- `lowering_policy`
  - examples:
    - `preserve_if_possible`
    - `require_rich_lowering`

- `rich_required`
  - boolean
  - if `true`, the `GRCV3` projector must not silently downgrade the seed to a
    neutral/common-only realization path

- `projection_goal`
  - examples:
    - `geometry_preservation`
    - `spark_probe`
    - `interface_preservation`

This group is important because one of the main failure modes to avoid is
silent fallback to a weaker projector path that erases the rich seed’s meaning.

## 6. What `GRCL-v3` Must Not Express

These are forbidden categories, even if they would be convenient.

## 6.1 Solved Differential State

Forbidden:

- explicit gradient vectors
- explicit Hessian matrices
- explicit Hessian eigenvalues
- explicit signed-Hessian summaries
- explicit `hessian_sign`

Reason:

- those belong to solved or derived runtime state, not source construction

## 6.2 Solved Transport State

Forbidden:

- explicit per-edge `J_ij`
- explicit net flux values
- explicit `flux_coupling`
- explicit `temporal_delay`
- explicit `geometric_length` as a runtime result

Reason:

- these are outputs of the constitutive loop, not source ontology

## 6.3 Runtime Identity State

Forbidden:

- basin-attribute payloads as source truth
- `spark_candidate: true`
- `choice_state: ...`
- `collapse_target: ...`
- split registry state
- live hierarchy state that depends on runtime evolution rather than source
  containment

Reason:

- the source may describe intended initial structure
- it may not describe runtime conclusions as already achieved

## 6.4 Hidden Projector Blobs

Forbidden:

- opaque projector-private payloads with undocumented meaning
- blobs that can only be interpreted by one code path and have no documentable
  semantics

If a field cannot be explained in this vocabulary note, it should not be part
of the seed contract.

## 7. Lowering Obligations

This section is critical.

If `GRCV3` consumes `GRCL-v3`, it must obey these rules.

### 7.1 Consume Or Fail Explicitly

If:

- `extensions.grcv3.rich_required = true`

then the `GRCV3` projector must either:

- lower the supported rich-seed vocabulary faithfully,
- or fail explicitly

It must not silently ignore the rich extension and fall back to neutral/common
projection.

### 7.2 Preserve Meaning, Not Just Data

Lowering is successful only if the realized motif preserves the intended local
roles:

- center versus support
- weak-axis versus stable-axis roles
- branch-interface separation
- ridge normal/tangent interpretation
- channel entry/exit correspondence

Copying fields into metadata while erasing their geometric effect is not enough.

### 7.3 Deterministic Realization

The same rich seed must realize identically under:

- primitive order
- repeated runs
- save/load replay
- representative diagnostics

### 7.4 Record Approximation When Needed

If the projector approximates a rich instruction rather than matching it
exactly, that approximation should be recorded in projector notes or emitted
diagnostics.

`GRCL-v3` should reduce heuristic guesswork, not hide it.

## 8. Minimum Viable Schema Shape

The first practical schema surface can stay small.

A minimal first rich primitive could look like:

```yaml
- id: decision_core
  type: saddle
  chart_center_hint: [0.0, 0.0]
  chart_scale_hint:
    radius: 0.2
  extensions:
    grcv3:
      realization:
        kind: junction_motif
        support_count: 4
        radius_scale: 0.45
        branch_order: [north, east, south, west]
        attachment_mode: branch_interface
      local_geometry:
        frame_mode: branch_ordered
        axis_roles: [north, east, south, west]
        weak_axis_role: east
        symmetry_class: cross
        center_role: routing_core
      curvature_intent:
        class: near_degenerate
        weak_axis_role: east
        stable_axis_roles: [north, south]
        ordering: weak << stable
      interfaces:
        branch_targets:
          north: nucleus
          east: mito_a
          south: mito_b
          west: mito_c
```

This example is allowed because it says:

- how the routing site should be constructed
- which local branches correspond to which semantic neighbors
- which role is intended to be weak

It is not saying:

- the solved Hessian is this matrix
- or the spark has already happened

This abstract shape is now also recorded as a concrete manual fixture:

- `configs/landscapes/seed/grcv3-rich-collapse-example.seed.yaml`

That fixture remains source-side and geometry-facing. The observed
choice-to-collapse transition comes from the runtime envelope recorded next to
the seed, not from any solved collapse state encoded into the seed itself.

## 9. First Minimal Vocabulary For Implementation

The first implementation slice should stay narrower than the full possible
surface.

The recommended initial executable subset is:

1. `extensions.grcv3.contract_version`
2. `extensions.grcv3.rich_required`
3. `primitive.extensions.grcv3.realization.kind`
4. `primitive.extensions.grcv3.realization.support_count`
5. `primitive.extensions.grcv3.realization.radius_scale`
6. `primitive.extensions.grcv3.realization.branch_order`
7. `primitive.extensions.grcv3.local_geometry.frame_mode`
8. `primitive.extensions.grcv3.local_geometry.weak_axis_role`
9. `primitive.extensions.grcv3.interfaces.branch_targets`

That subset is enough to test the central hypothesis:

- whether explicit geometry-bearing source intent can preserve a manual
  sparkable motif through the seed-driven path

## 10. Relation To Later Full `GRCL-v3`

If the first small rich-seed probe succeeds, this vocabulary becomes the seed
of full `GRCL-v3` capability.

That expansion should still follow one rule:

- extend by adding more **constructive geometry semantics**
- not by gradually allowing solved runtime state to leak into the source seed

## 11. Recommended Follow-On

The next document after this vocabulary note should be:

- a small `GRCL-v3` implementation checklist:
  [GRCL-V3-ImplementationChecklist.md](./GRCL-V3-ImplementationChecklist.md)

That checklist should define:

1. the first accepted field subset
2. validation rules for those fields
3. one minimal rich seed fixture
4. one projector lowering path
5. one diagnostic gate against the manual spark probe

## 12. Second Capability Slice

After the first gate split, the next executable slice should remain explicit and
versioned rather than expanding `grcv3.rich.v1` invisibly.

Recommended next contract:

- `grcv3.rich.v2`

Recommended newly executable groups:

1. `primitive.extensions.grcv3.local_geometry`
   - `axis_roles`
   - `symmetry_class`
   - `center_role`
2. `primitive.extensions.grcv3.curvature_intent`
   - `class`
   - `stable_axis_roles`
   - `weak_axis_role`
   - `ordering`
3. `primitive.extensions.grcv3.interfaces`
   - `boundary_roles`
   - `channel_roles`
   - `preferred_attachment_sites`
4. `primitive.extensions.grcv3.channel_geometry`
   - `realization_kind`
   - `interior_count`
   - `waypoint_policy`
   - `entry_role`
   - `exit_role`
5. `primitive.extensions.grcv3.boundary_geometry`
   - `realization_kind`
   - `normal_role`
   - `tangent_role`
   - `arc_span`
   - `support_distribution`

Primitive scope for the second slice:

- `basin`
- `plateau`
- `junction`
- `saddle`
- `ridge`
- `valley`

Still out of scope after this second slice:

- top-level:
  - `lowering_policy`
  - `projection_goal`
- realization:
  - `attachment_mode`
  - `support_angles`
- any source field that attempts to inject solved Hessian, solved flux,
  runtime identity state, or projector-private blobs

The point of `grcv3.rich.v2` is not to solve the runtime at the seed layer. It
is to give the seed enough constructive local geometry to express why a basin,
channel, or boundary should lower into a spark-relevant local stencil more
faithfully than the neutral/common language can.

## 13. Third Capability Slice

The next capability slice should now be made explicit rather than left as an
informal follow-on.

Recommended next contract:

- `grcv3.rich.v3`

Role of this slice:

- move beyond “richer family-native lowering”
- toward direct constructive specification of interior-shaping motifs
- while still forbidding solved runtime-state injection

This is the point where the preferred architecture begins to shift from:

- projector-style semantic interpretation

toward:

- direct family-native assembly of explicitly declared local motifs

### 13.1 What `grcv3.rich.v3` Should Add

The central new executable group should be:

- `primitive.extensions.grcv3.interior_geometry`

Suggested allowed meanings:

- `probe_mode`
  - examples:
    - `interior_candidate`
    - `routing_core`
    - `stable_anchor`

- `support_profile`
  - ordinal support-spacing / confinement by role
  - examples:
    - weak-axis supports are `loose`
    - stable-axis supports are `tight`

- `attachment_isolation`
  - whether channels/boundaries may attach:
    - to the center directly
    - only through named support roles
    - or only through boundary-interface roles

- `interior_clearance_class`
  - whether the center should remain:
    - `shielded`
    - `semi_open`
    - `through_loaded`

- `support_connectivity`
  - how support members should be connected locally
  - examples:
    - `ring`
    - `paired_clamps`
    - `spindle`
    - `branch_only`

- `support_role_groups`
  - named support-role partitions such as:
    - `stable = [north, south]`
    - `weak = [east, west]`
    - `boundary = [north, south]`
    - `transport = [west, east]`

These remain constructive source semantics.
They are still not solved differential state.

### 13.2 Why `grcv3.rich.v3` Is Needed

`grcv3.rich.v2` is now sufficient to:

- express richer local role structure
- preserve explicit interface attachment intent
- build a real interior geometric seed in the basin-centered probe path

But the current evidence also shows that `grcv3.rich.v2` is still not
sufficient to express:

- role-indexed support-spacing asymmetry
- role-indexed confinement asymmetry
- enough direct attachment isolation to keep the center in the intended
  weak-axis regime

So `grcv3.rich.v3` is not a generic “more features” release.
It is the first slice aimed specifically at:

- making an interior seed not merely valid
- but weak-axis sparkable

### 13.3 Primitive Scope For `grcv3.rich.v3`

The initial `grcv3.rich.v3` scope should stay narrow.

Recommended first primitive scope:

- `basin`
- `saddle`
- `junction`
- `ridge`
- `valley`

The practical target is:

- one direct interior-probe family
- one clamp/boundary family
- one transport/channel family

That is enough to test whether direct constructive assembly can move the
basin-centered weak-axis probe from:

- validated geometric seed

to:

- actual `spark_candidate`

### 13.4 What Remains Forbidden In `grcv3.rich.v3`

Even at this stronger slice, the following remain forbidden:

- explicit gradient vectors
- explicit Hessian matrices
- explicit Hessian eigenvalues
- explicit signed-curvature summaries
- explicit `hessian_sign`
- explicit per-edge fluxes
- explicit runtime edge labels as solved values
- `spark_candidate: true`
- collapse targets or choice-state conclusions
- any runtime registry state

So `grcv3.rich.v3` may become more direct in local geometry construction, but
it still must not become a disguised snapshot or solved-state carrier.

### 13.5 Direction For `grcv3.rich.v4`

If a later `grcv3.rich.v4` slice is introduced, it should not be framed as
“more projector power.”

It should be framed as:

- a source contract strong enough for direct translation into `GRCV3`
  family-native assembly

That means `grcv3.rich.v4` should **not** exist merely to support:

- another layer of heuristic lowering
- additional projector-side semantic recovery
- or wider refinement search over underspecified seeds

It should exist only if the new fields are explicit enough that the assembly
step becomes:

- deterministic construction from declared source structure

rather than:

- projection from an incomplete source into a guessed motif

So the intended boundary is:

- `rich.v1` / `rich.v2`: weaker, projector-tolerant
- `rich.v3`: first direct-assembly-capable interior-geometry lane
- `rich.v4`: direct-translation-only contract

## 14. Sufficient Interior-Shaping Semantics For A Weak-Axis Spark Probe

One unresolved design question is now precise:

- what source-side information would be sufficient to construct a sparkable
  weak-axis interior candidate
- without injecting solved gradients, solved Hessians, or solved fluxes?

The answer is not “name the weak axis” by itself.

That is necessary, but not sufficient.

What a sparkable weak-axis candidate needs from the source is a constructive
combination of three things:

1. a genuine interior probe site
2. anisotropic support geometry around that site
3. controlled external attachment so the center stays low-gradient while one
   axis remains weak

In other words, the source does not need to say:

- “the Hessian at the center is this matrix”

but it likely does need to say enough to construct:

- a center with multiple neighbors,
- a stable branch/interface ordering,
- an intentionally weaker support direction,
- and a non-accidental loading pattern from channels/boundaries.

### 14.1 The Three Constructive Requirements

### A. Interior Probe Existence

The source must be able to say that a semantic center should lower into a real
interior stencil rather than a pure routing hub or boundary-adjacent anchor.

That requires constructive semantics such as:

- `center_role = interior_probe` or `routing_core`
- `realization.kind = support_patch` or `junction_motif`
- `support_count >= 4`
- stable `branch_order` or `support_angles`

This is the minimum needed so the projector can create a center with enough
local neighborhood structure for WLS differential reconstruction at all.

### B. Weak-Versus-Stable Axis Shaping

The source must be able to shape the local stencil so one direction is
intentionally near-degenerate while the orthogonal directions remain
stabilizing.

That requires more than just naming roles.
It requires constructive asymmetry such as:

- `weak_axis_role`
- `stable_axis_roles`
- `symmetry_class`
- and a source-side profile for how support geometry differs by role

The important point is that this profile should remain constructive and
ordinal, not solved.

Examples of acceptable source intent:

- weak-axis supports are farther from the center than stable-axis supports
- weak-axis supports are fewer, looser, or less confining than stable-axis
  supports
- stable-axis supports form a tighter bracket around the interior probe

Examples of unacceptable source intent:

- explicit Hessian entries
- explicit eigenvalues
- explicit signed-curvature values

So the missing capability is not “inject Hessians.”
It is “let the seed describe enough local spacing and confinement asymmetry that
the Hessian can emerge.”

### C. Interface And Load Isolation

The source must also be able to keep the center from becoming a high-gradient
through-node as soon as valleys or boundaries attach.

That means the seed likely needs explicit control over:

- which branch/interface roles channels attach to
- which support roles ridges/boundaries load
- whether attachments hit the center directly or only the support structure
- and how opposite branches are paired or separated

Without that, a projector may build a geometrically richer motif and still
destroy the intended weak-axis regime by loading the center in the wrong place.

### 14.2 The Likely Minimal Sufficient Surface

The current evidence suggests that a minimal sufficient source surface for this
problem would likely include:

1. interior-stencil realization:
   - `kind`
   - `support_count`
   - `branch_order` or `support_angles`
2. center semantics:
   - `center_role`
3. axis semantics:
   - `axis_roles`
   - `weak_axis_role`
   - `stable_axis_roles`
4. constructive asymmetry:
   - a role-indexed support-spacing or support-confinement profile
5. interface isolation:
   - `branch_targets`
   - `preferred_attachment_sites`
   - channel `entry_role` / `exit_role`
   - boundary `normal_role` / `tangent_role`

That list is deliberately about construction, not solved state.

### 14.3 What New Field Family This Suggests

If later work needs a new `GRCL-v3` extension group specifically for this
problem, the right direction is not a differential-state group.

The right direction is something like:

- `primitive.extensions.grcv3.interior_geometry`

with meanings such as:

- `probe_mode`
  - `interior_candidate`
  - `routing_core`
  - `stable_anchor`
- `support_profile`
  - ordinal support-spacing / confinement by role
- `attachment_isolation`
  - whether channels/boundaries may attach to the center directly or only
    through named support roles
- `interior_clearance_class`
  - whether the center should remain shielded from immediate boundary loading

These would still be source-side constructive semantics.
They would not be solved geometry.

### 14.4 Practical Design Rule

For `GRCV3`, the correct target is:

- enough source semantics to build a low-gradient interior probe with one weak
  axis and one or more stable axes
- but not enough source semantics to pre-solve the differential state

That is the boundary future `GRCL-v3` work should aim for.

## 15. Next Constructive Group: Interior Partition

The first executable `interior_geometry` slice and its direct-assembly gate
produced a narrower result than before:

- the weak-axis structure improved
- but the center still became too gradient-loaded

So the next source-side problem is no longer just spacing or support grouping.
It is the missing distinction between:

- the inner probe that should remain low-gradient
- and the outer support surface that is allowed to carry boundary/transport
  load

The next justified group should therefore be:

- `primitive.extensions.grcv3.interior_partition`

This would still be constructive source semantics.
It would still not be solved runtime state.

### 15.1 Why This Should Be A Separate Group

This should not be folded silently into `support_profile`.

Reason:

- `support_profile` changes local spacing / confinement / relative support
  strength
- the next missing requirement changes which layer of the motif is allowed to
  take load before that load reaches the probe

That is a different semantic problem.

So if the language hides it inside the existing profile fields, the source will
lose the distinction between:

- geometry of the support surface
- load-routing structure between support surface and probe

### 15.2 Suggested Allowed Meanings

Suggested location:

- `primitive.extensions.grcv3.interior_partition`

Suggested constructive fields:

- `partition_mode`
  - examples:
    - `two_tier_probe_shell`
    - `probe_plus_clamp_shell`
    - `single_surface`

- `probe_role_groups`
  - which declared local roles belong to the inner probe tier

- `load_role_groups`
  - which roles belong to the outer load-bearing tier

- `probe_shell_count`
  - how many outer-shell members participate in the first lowering

- `load_transfer_mode`
  - how load may pass from the outer tier to the inner tier
  - examples:
    - `support_mediated`
    - `clamp_mediated`
    - `transport_mediated`
    - `direct_open`

- `probe_protection_class`
  - qualitative shielding class for the inner probe
  - examples:
    - `shielded`
    - `semi_open`
    - `open`

- `attachment_transfer_roles`
  - which local roles may receive external channel/boundary load before it is
    allowed to influence the probe tier

### 15.2.1 First Executable Slice

The first executable `interior_partition` slice should stay narrower than the
full suggested family above.

Recommended first executable field set:

- `partition_mode`
- `load_role_groups`
- `load_transfer_mode`
- `probe_protection_class`
- `attachment_transfer_roles`

Recommended first scope:

- basin-centered interior probes that already use `interior_geometry`
- channel and ridge load routing into that basin-centered structure

Explicitly out of scope for the first executable slice:

- `probe_shell_count`
- arbitrary multi-shell constructions
- free-form probe/load role hierarchies beyond one inner probe tier and one
  outer load-bearing tier
- junction-specific partition semantics

Reason:

- the next gate is trying to solve one precise near-miss
- keep the center low-gradient while the outer surface takes load
- so the first slice should focus on load-bearing layer declaration, not on
  generalized motif multiplication

### 15.3 What Remains Forbidden

Even with this stronger slice, the following remain forbidden:

- solved inner/outer coherence values as source truth
- solved gradient values on either tier
- solved Hessian values on either tier
- explicit flux-routing tables as runtime truth
- explicit spark/collapse labels

So `interior_partition` may define:

- which tier exists
- which roles belong to which tier
- how external load must pass through those tiers

But it still may not define:

- the solved differential state that the runtime should have

### 15.4 Practical Design Rule

The language should now evolve in this order:

1. `interior_geometry`
   - spacing, grouping, connectivity, immediate attachment policy
2. `interior_partition`
   - inner probe versus outer load-bearing layer semantics
3. only after that:
   - richer assembly rules that consume both groups together

That keeps the language honest:

- geometry construction first
- load partition second
- solved state never

## 16. The Next Missing Source Group: `interior_load_carriers`

The first `interior_partition` gate narrowed the next source-side gap further.

What failed was not merely:

- “the source lacks an outer load tier”

because that tier now exists.

What still failed was closer to:

- “the outer load tier is still too role-aligned and too coincident with the
  probe stencil, so external load projects back onto the same weak-axis support
  geometry too directly”

That is a different semantic problem again.

It is no longer about:

- whether there is one shell or two

It is about:

- where the load-bearing carriers actually sit
- how those carriers are offset relative to the probe shell
- how transfer from those carriers back into the probe shell is mediated

So the next strengthening should not be folded silently into:

- `support_profile`
- `interior_partition`

because that would collapse three distinct ideas into one field family:

- probe-shell geometry
- probe versus load tier membership
- actual placement and mediation of the load-bearing carriers

### 16.1 Suggested Location

Suggested location:

- `primitive.extensions.grcv3.interior_load_carriers`

Reason:

- `interior_partition` should keep meaning:
  - which tier exists
  - which roles belong to which tier
  - which roles are allowed to receive load
- `interior_load_carriers` should add meaning:
  - how the load-bearing carrier layer is spatially and topologically realized

### 16.2 Suggested Allowed Meanings

Suggested constructive fields:

- `carrier_layout_mode`
  - how load carriers are arranged relative to the probe shell
  - examples:
    - `offset_ring`
    - `paired_tracks`
    - `staggered_arc`
    - `group_midpoints`

- `carrier_anchor_policy`
  - whether load carriers sit on declared roles directly or between them
  - examples:
    - `role_aligned`
    - `between_roles`
    - `group_centroid`

- `carrier_offset_profile`
  - qualitative or role-indexed declaration of how far carriers sit from the
    probe shell
  - examples:
    - role/group-indexed `tight | neutral | far`

- `transfer_topology_mode`
  - how carriers couple back into the probe shell
  - examples:
    - `nearest_probe_role`
    - `group_bridge`
    - `cross_axis_bridge`
    - `paired_role_bridge`

- `transfer_role_pairs`
  - explicit permitted carrier-to-probe role pairings when the transfer mode is
    not symmetric
  - examples:
    - `[ [north_load, north_probe], [south_load, south_probe] ]`
    - `[ [east_load, north_probe], [west_load, south_probe] ]`

- `carrier_attachment_roles`
  - which carrier roles are allowed to receive external channel/boundary
    attachments before the transfer stage

### 16.2.1 First Executable Slice

The first executable `interior_load_carriers` slice should again stay narrow.

Recommended first executable field set:

- `carrier_layout_mode`
- `carrier_anchor_policy`
- `transfer_topology_mode`
- `transfer_role_pairs`
- `carrier_attachment_roles`

Recommended first scope:

- basin-centered interior probes that already use:
  - `interior_geometry`
  - `interior_partition`
- family-native `GRCV3` assembly only

Explicitly out of scope for the first executable slice:

- arbitrary free-positioned carrier coordinates
- solved transfer weights
- more than one outer carrier layer
- junction/saddle-specific carrier fabrics
- direct import of a fully realized runtime graph

Reason:

- the next gate is not trying to generalize everything
- it is trying to answer one precise question:
  - can non-coincident load-carrier placement plus explicit transfer topology
    keep the center low-gradient while preserving a usable weak axis?

### 16.3 What Remains Forbidden

Even with this stronger slice, the following remain forbidden:

- solved carrier node coordinates as immutable runtime truth
- solved edge weights between carrier and probe layers
- solved gradient/Hessian values on either layer
- explicit spark labels or collapse labels as source truth
- direct “this node must spark” declarations

So `interior_load_carriers` may define:

- where the load-bearing layer is constructively placed relative to the probe
- which carriers may receive external load
- how carrier-to-probe transfer is mediated

But it still may not define:

- the solved discrete state that the runtime should have after assembly

### 16.4 Practical Design Rule

The source-side evolution order should now be:

1. `interior_geometry`
   - spacing, grouping, connectivity, immediate attachment policy
2. `interior_partition`
   - inner probe versus outer load-bearing layer semantics
3. `interior_load_carriers`
   - where the outer carrier layer sits and how it couples back
4. only after that:
   - richer assembly rules consuming all three together

That keeps the language honest:

- probe geometry first
- load partition second
- carrier placement and mediation third
- solved state never

## 17. Next Constructive Group: Transfer Mediation (`grcv3.rich.v4`)

The `rich.v3` line narrowed the remaining source problem further than earlier
lanes:

- geometry shaping helped
- partitioning helped clarify the probe-versus-load distinction
- non-identity carrier remaps improved the Hessian materially
- but the center gradient still plateaued far above the validation threshold

So the next justified source-side need is no longer:

- more projector refinement
- more transfer-pair permutations
- or another generic geometry-profile expansion

It is:

- explicit transfer mediation semantics

The missing degree of freedom is how already-declared carrier-to-probe transfer
paths are allowed to influence the intended low-gradient interior site.

### 17.1 Why This Belongs To `grcv3.rich.v4`

This should be the first `rich.v4` field family because it satisfies the new
boundary recorded for `rich.v4`:

- it can be translated directly into native assembly
- it targets the precise remaining near-miss
- and it does not require projector-style semantic interpretation

It should therefore be introduced only as a direct-translation contract, not
as another “smarter lowering” surface.

### 17.2 Suggested Location

Suggested location:

- `primitive.extensions.grcv3.transfer_mediation`

Reason:

- `interior_geometry` answers:
  - what the probe stencil is
- `interior_partition` answers:
  - which tier takes load first
- `interior_load_carriers` answers:
  - where the outer carriers sit and which transfer pairs exist
- `transfer_mediation` should answer:
  - how those already-explicit transfer pairs are allowed to pass load toward
    the probe

So this group should not redefine geometry, partition, or carrier placement.
It should operate only on the already-declared transfer surface.

### 17.3 Suggested Allowed Meanings

Suggested constructive fields:

- `mediation_mode`
  - the direct transfer recipe used for declared carrier-to-probe pair links
  - examples:
    - `attenuated_pairs`
    - `guarded_pairs`
    - `confined_pairs`

- `pair_mediation_classes`
  - explicit class assignment for every declared `transfer_role_pair`
  - examples of class values:
    - `blocked`
    - `weak`
    - `medium`
    - `strong`

- `probe_guard_class`
  - whether transfer may remain on the probe shell or may influence the center
    more directly
  - examples:
    - `shell_only`
    - `guarded_center`
    - `open_center`

- `lateral_spill_policy`
  - whether transferred load may spread laterally across neighboring probe roles
    before center influence
  - examples:
    - `role_locked`
    - `axis_locked`
    - `open`
  - current language result from Iteration 39:
    - this field is behavior-bearing
    - but in the current spindle lane it does not introduce a third productive
      settlement regime
    - instead, `role_locked` acts as a closure boundary, while the productive
      regime split still depends on `axis_locked` together with other
      `transfer_mediation` structure

- `spill_branch_mode`
  - where that allowed lateral spill branches from relative to the declared
    mediation path
  - examples:
    - `carrier_branch`
    - `mediated_branch`
  - intended meaning:
    - distinguish whether spill branches directly from the carrier site or from
      the realized intermediated path node without prescribing the solved
      transport outcome
  - important interpretation rule:
    - this field does not promise that the same operative candidate site will
      survive across direct and path-mediated lanes
    - it may instead change where the spark-capable settlement locus appears
      while still leaving the previously tracked carrier site non-settled

These are still constructive source semantics.
They are not solved transport values.

- `center_coupling_classes`
  - optional per-probe-role refinement of whether already-mediated ingress may
    still couple through the semantic center spoke for that role
  - examples:
    - `[north, blocked]`
    - `[south, weak]`
  - intended meaning:
    - refine center-spoke participation for declared probe roles without
      redefining carrier placement, pair coverage, or runtime transport laws

### 17.3.1 How `direct` And `mediated` Should Be Read

This distinction must be read carefully.

At the implementation level, `direct` versus `mediated` does look like a graph
assembly difference:

- `direct`
  - realized as immediate carrier-to-probe adjacency
- `mediated`
  - realized through an explicit intermediate
    `basin_transfer_path_node`

But the theory-facing meaning is stronger than “put a helper node on an edge.”

The right source-language reading is:

- `direct`
  - the declared carrier-to-probe ingress is assembled as one immediate local
    adjacency
- `mediated`
  - that ingress is assembled as passing through an intermediate local
    structural site before it reaches the probe shell

In `GRCV3`, that intermediate site is represented as a real node because a
`GRCV3` node is a basin chart carrying local differential summaries, not just a
scalar placeholder. So if settlement, spark, or split localizes there, that is
not merely an implementation accident. It is the discrete realization of the
claim that the operative basin-like site along ingress is intermediate rather
than immediately carrier-local or probe-local.

Relative to the 2025-11 RC papers, this should still be read as a discrete
realization choice, not as a literal new continuum primitive. RC itself speaks
in terms of coherence flow, curvature, and attractor regions, not graph edges
or path nodes. So the closest RC reading is:

- `mediated` says there exists an intermediate region along ingress where
  coherence can organize enough to become the operative settlement locus

That is why `transfer_mediation` belongs to `GRCL-v3`:

- it is a constructive statement about how ingress is assembled in the discrete
  realization
- it is not a declaration of solved transport values
- and it is not a claim that RC contains a literal node-on-an-edge ontology

### 17.3.2 GRCV3 Theory-Facing Correctness Boundary

The point of `transfer_mediation` is to describe source-side structure that is
still faithful to `GRCV3` theory, not to add an ad hoc control layer.

So the intended meaning must remain:

- constructive constraints on how exterior load reaches the interior probe
- constructive shielding / guarding / spill structure around declared
  carrier-to-probe links
- deterministic assembly policy for those declared links

It must **not** become:

- a source-side override of the constitutive transport law
- a direct prescription of `w_ij`, `Phi_i`, or `J_ij` as solved values
- a hidden substitute for explicit Hessian injection

The theory-facing rule is:

- `transfer_mediation` may change the assembled discrete structure through
  which transport is later computed
- but the runtime must still obtain geometry and transport through the normal
  `GRCV3` loop:
  - coherence/support state
  - local differential reconstruction
  - basin tensor / metric construction
  - edge conductance
  - potential
  - flux

In other words:

- the source may describe how ingress is structurally mediated
- the runtime must still solve what transport that structure produces

That keeps the new slice theory-correct:

- source semantics shape the conditions for transport
- they do not replace transport constitutively

### 17.3.1 First Executable Slice

The first executable `transfer_mediation` slice should stay narrow.

Recommended first executable field set:

- `mediation_mode`
- `pair_mediation_classes`
- `probe_guard_class`
- `lateral_spill_policy`
- optional controlled broadening, only if transient evidence still localizes
  the residual gap inside transfer mediation:
  - `center_coupling_classes`

Recommended first scope:

- basin-centered interior probes already using:
  - `interior_geometry`
  - `interior_partition`
  - `interior_load_carriers`
- family-native `GRCV3` assembly only

Direct-translation rule for the first slice:

- every declared `transfer_role_pair` must receive an explicit mediation class
- no undeclared pair may be synthesized by projector logic
- no mediation class may be inferred from geometry alone
- native assembly may only realize the declared pair structure using the
  declared mediation classes and guard/spill policy
- if `center_coupling_classes` is present:
  - it may only refine center-spoke participation for already-declared probe
    roles
  - it may not introduce new roles, new transfer pairs, or new nonlocal
    transfer structure

If one more post-28 `rich.v4` cycle is later justified, the next accepted
surface should still stay narrow.

Recommended first Iteration 29 path-structure surface:

- `primitive.extensions.grcv3.transfer_mediation.path_topology`

Recommended encoding:

- an explicit list of `[carrier_role, probe_role, topology_class]` triples
- the list should cover exactly the already-declared `transfer_role_pairs`
  whenever it is present

Recommended first executable topology classes:

- `direct`
  - realize the current carrier-to-probe route directly
- `single_intermediate`
  - realize one dedicated intermediate node on the declared pair before the
    probe role
- `fan_in`
  - realize one shared intermediate node for multiple declared pairs that
    target the same probe role

Recommended first deferred candidates:

- `path_roles`
- `path_mode`
- `double_intermediate`
- `buffered_chain`

Reason:

- `transfer_role_pairs` already declare role coverage
- so the first path-structure slice should change only assembled route shape,
  not reopen the role surface or introduce a second coordination layer

Validation rule for the first path-structure slice:

- `fan_in` should be accepted only when at least two declared pairs share the
  same probe role inside the same primitive
- omitted or partial path-topology coverage should fail explicitly rather than
  falling back to projector interpretation

Explicitly out of scope for the first executable slice:

- solved numeric per-edge transfer weights in the seed
- free-form arbitrary transfer matrices
- runtime-learned or adaptive mediation rules
- projector-inferred fallback classes for omitted pairs
- family-neutral backporting of mediation semantics
- source-side constitutive overrides of the `GRCV3` conductance / potential /
  flux law

Reason:

- the next gate is trying to solve one precise problem:
  - how to reduce center load ingress without injecting solved Hessians
- so the first `rich.v4` slice should constrain transfer semantics directly,
  not reopen the whole source geometry surface

### 17.4 What Remains Forbidden

Even with this stronger slice, the following remain forbidden:

- explicit solved transfer weights as source truth
- explicit per-step transport schedules
- solved gradient/Hessian/flux values on the mediated links
- direct declarations that a center must validate, spark, or collapse
- omitted transfer semantics that rely on projector recovery
- source fields that directly prescribe constitutive transport outcomes while
  pretending to be geometry

So `transfer_mediation` may define:

- how declared transfer pairs are mediated
- how strongly each declared pair class participates
- how much probe shielding or spill is allowed structurally
- where spill branches from along an already-declared mediated ingress path

But it still may not define:

- the solved runtime transport state after assembly
- or any per-step/solved decision that a probe role must or must not spark

### 17.5 Practical Design Rule

If `grcv3.rich.v4` is opened, the first accepted semantic family should be
`transfer_mediation` and it should be judged by one strict rule:

- if a proposed field only gives the projector more room to guess, it does not
  belong in `rich.v4`

The point of `rich.v4` is not richer interpretation.
It is direct translation of the still-missing source semantics.

### 17.6 Why Failed Semantic Probes Still Matter

The `GRCL-v3` arc should not evaluate a semantic probe only by asking whether
it immediately restores a preferred behavior lane.

The stricter question is:

- does the probe make the landscape language more behavior-truthful?

That means a failed probe can still be valuable if it clarifies one of these
boundaries:

- a distinction that really does belong in source language
- a distinction that is only constructive/runtime realization and should not be
  promoted as source semantics
- or a landscape phrase that sounds plausible but does not actually correspond
  to the dynamical mechanism seen in the trace

Iterations 29 to 32 make this concrete for `transfer_mediation.path_topology`:

- path intermediacy is a real source-side structural distinction
- but the current `single_intermediate` realization does not fail because
  ingress is absent
- it fails because the added intermediacy does not form the weak-axis geometry

Iteration 40 sharpens that same field further:

- `path_topology` is not only a distinction between productive and
  non-productive ingress
- it also constrains whether an already-productive path-node settlement regime
  is portable across mediated-path realizations
- in the current spindle lane:
  - `single_intermediate` supports the productive path-node regime
  - `fan_in` does not

So `path_topology` is now known to be behavior-bearing at two levels:

- whether mediated ingress can recover a productive regime at all
- and whether a recovered path-node regime survives under another path
  realization class

### 17.7 Current Closure Boundary For `transfer_mediation`

The present `transfer_mediation` side-quest is now close to exhausted for the
current spindle spark lane.

That should be read as a success of the language exercise, not as a failure of
the family.

The family has already established the main behavior-truthful distinctions it
needed to establish:

- mediated ingress can change the operative settlement locus
- that locus can live on a carrier site or on a path node
- later migration onto split children is itself part of the regime description
- permitted lateral spill is required for productive settlement in this lane
- and path topology constrains whether a productive path-node regime is even
  portable

So the current boundary is:

- do not keep broadening `transfer_mediation` merely because more variants are
  imaginable
- only reopen it if a new proposal names a missing source distinction more
  directly than a new semantic family would
- otherwise the next `GRCL-v3` step should intentionally identify the next
  direct semantic family rather than stretching this one further

Iterations 37 to 38 sharpen the positive side of that same rule:

- a successful probe is not fully understood just because a saved visual looks
  rich or convincing
- the important closure is the regime description that the trace supports in
  source-language terms
- in this case, the right statement is:
  - the direct lane stays on the carrier-site regime
  - the mediated path lane first anchors on a path node
  - and only later migrates onto split children

That is a stronger language result than “the path animation looks complex.”
It says what kind of settlement regime the source language now needs to
describe.

So the lesson is not only “this probe did not recover spark.”
The deeper lesson is:

- the source language may describe intermediated ingress truthfully
- but it must not pretend that such intermediacy already means productive
  geometry formation

That is exactly the kind of negative result the `GRCL-v3` vocabulary should
keep, because it sharpens the source/runtime boundary instead of obscuring it.

### 17.8 Strongest Candidate For The Next Direct Semantic Family

The next family should not be named casually.
It should be chosen by asking which remaining question is still genuinely
source-side after `transfer_mediation` is treated as close to exhausted.

The strongest current candidate is:

- `primitive.extensions.grcv3.settlement_regime`

or, if a narrower name is preferred:

- `primitive.extensions.grcv3.settlement_locus`

Reason:

- the remaining unexplained behavior is no longer mainly:
  - how ingress reaches the probe
  - how strongly declared pairs are guarded
  - or how spill is routed along already-declared mediation structure
- it is now:
  - where productive settlement lives
  - whether that settlement remains anchored or migrates
  - and whether later migration onto split children is itself part of the
    source-language claim

This follows directly from Iterations 37 to 40:

- direct lanes can realize a `carrier_site_regime`
- mediated lanes can realize a `path_node_regime`
- only the path-node regime currently shows later migration onto split children
- and those distinctions survive as regime descriptions even after the present
  `transfer_mediation` family is treated as close to exhausted

So the candidate family should answer questions like:

- what kind of site may become the operative settlement locus:
  - carrier-local
  - path-local
  - probe-local
- whether settlement is expected to stay anchored at its first operative site
  or later migrate during spark/split
- whether split children may inherit the operative settlement locus
- whether that migration belongs to source semantics rather than being treated
  only as an incidental runtime trace

Preferred current naming decision:

- `settlement_regime` should be preferred as the next family name
- `settlement_locus` should be retained only as a possible narrower sub-surface
  name later

Reason:

- the present evidence is not only about where first settlement anchors
- it is also about whether that settlement remains anchored or later migrates
- and whether migration onto split children is itself part of the
  source-language description

What this family should **not** do:

- prescribe solved thresholds
- prescribe spark outcomes directly
- replace transport, candidate gating, or split progression numerically

### 17.8.1 Why The Other Existing Families Are Weaker Next Choices

The already-named families still have legitimate meanings, but they are weaker
choices for the next post-`transfer_mediation` side-quest.

- `interior_geometry`
  - expected to answer probe stencil, spacing, grouping, connectivity, and
    immediate attachment structure
  - weaker next choice because the current question is no longer mainly about
    shape or support layout

- `interior_partition`
  - expected to answer which tier exists and which tier is allowed to take load
    first
  - weaker next choice because the current question is no longer mainly about
    tier membership

- `interior_load_carriers`
  - expected to answer where load-bearing carriers sit and which explicit
    carrier-to-probe transfer surfaces exist
  - weaker next choice because the current question is no longer mainly about
    carrier placement or declared transfer coverage

- `boundary_geometry`
  - expected to answer local boundary/clamp support realization such as arcs,
    normals, tangents, and support distribution
  - weaker next choice because the present spindle-side result does not yet
    implicate boundary-support layout as the main reason the operative
    settlement locus differs or migrates

- `transfer_mediation`
  - expected to answer how already-declared transfer pairs are mediated,
    guarded, and allowed to spill
  - weaker next choice because the present side-quest has already extracted the
    main behavior-truthful distinctions this family could justify here

So the present recommendation is:

- record `settlement_regime` / `settlement_locus` as the strongest current
  candidate for the next direct semantic family
- keep that as a recorded proposal first
- and only then decide whether to open a concrete next iteration around it

### 17.8.2 First Executable Settlement-Regime Slice

The first executable slice should stay narrower than the full family.

Recommended first executable field:

- `primitive.extensions.grcv3.settlement_regime.regime_class`

Recommended first executable classes:

- `carrier_site_regime`
- `path_node_regime`

Reason:

- these are the two productive regimes already evidenced directly by
  Iterations 37 to 40
- they already differ in both:
  - first operative settlement locus
  - and later split-child inheritance behavior
- so they are narrow enough to execute without pretending to generalize every
  possible settlement phenomenology at once

Theory-facing execution rule:

- this slice may constrain which realized site classes are eligible to enter
  the spark-candidate gate
- and whether split-child inheritance belongs to the declared regime
- but it must still **not** prescribe solved thresholds, solved candidate
  scores, or guaranteed spark outcomes

Current implementation result from Iteration 42:

- matched `carrier_site_regime` preserves the productive direct lane
- matched `path_node_regime` preserves the productive single-intermediate path
  lane
- the path-node regime still shows later migration onto split children
- forcing `carrier_site_regime` onto that productive path lane suppresses the
  lane

So the first executable slice is already behavior-bearing, not merely a
post-hoc label for traces.

### 17.8.3 Settlement-Regime Decomposition Result

Iteration 43 shows that the first executable `settlement_regime` slice can
already be decomposed one step further without collapsing back into runtime
tuning.

The key split is:

- `initial_locus_class`
- `split_inheritance_mode`

Current narrow allowed values:

- `initial_locus_class`
  - `carrier_site`
  - `path_node`
- `split_inheritance_mode`
  - `anchored`
  - `split_child_inheriting`

Current language result:

- `path_node + split_child_inheriting` preserves the productive repeated
  path-node lane
- `path_node + anchored` still preserves first productive settlement on the
  same path node
- but it suppresses later split-child candidate migration

So the right source-language reading is now sharper:

- first productive settlement locus is one semantic fact
- later split-child inheritance is another semantic fact
- the earlier coarse `path_node_regime` name bundled both of them together

This matters because it tells us the current productive path lane is not
described most truthfully by “path-node regime” alone.
It is described more truthfully by:

- `initial_locus_class=path_node`
- `split_inheritance_mode=split_child_inheriting`

That is a cleaner language result than merely saying the path lane “shows later
migration.”
It says that migration can already be promoted as a separate source-side
distinction without prescribing solved outcomes.

### 17.8.4 First Matrix-Completion Result

Iteration 44 completes the first small `settlement_regime` matrix by testing:

- `carrier_site + split_child_inheriting`

The result is negative in a useful way:

- the lane still sparks
- first settlement still anchors on a carrier site
- but later split-child candidate migration still does not occur
- and no new repeated inherited carrier-side regime appears

So the current language result sharpens again:

- `split_inheritance_mode` is not a fully independent semantic axis across all
  initial settlement loci in this lane
- it is behavior-bearing on the `path_node` side
- but not symmetrically regime-opening on the `carrier_site` side

That means the current regime space is not best described as a full Cartesian
product of:

- `initial_locus_class`
- `split_inheritance_mode`

Instead, the presently productive repeating combinations are narrower:

- `path_node + split_child_inheriting`

while the other three current corners remain productive but non-repeating:

- `carrier_site + anchored`
- `path_node + anchored`
- `carrier_site + split_child_inheriting`

### 17.8.5 Post-Split Reentry Boundary

Iteration 45 asks the next question more directly:

- why does only `path_node + split_child_inheriting` repeat through later
  split-child candidacy?

The observability result is now explicit:

- the repeating lane does not merely “allow inheritance” in the abstract
- its derived split children later settle enough to pass the spark-candidate
  gate and re-enter the lifecycle
- the one-shot `carrier_site + split_child_inheriting` lane still produces
  derived split children
- but those children never settle enough to pass the same gate

So the more truthful language statement is:

- current non-repetition on the carrier side is not a failure of inheritance
  existence
- it is a failure of post-split reentry readiness at the derived child sites

That matters because it tightens the remaining open question inside
`settlement_regime`.
If the family continues, the next missing distinction is no longer “can split
children inherit candidacy?”
It is closer to:

- when inherited child sites are expected to settle back into candidate-ready
  states after the first split

### 17.8.6 Reentry Neighborhood Boundary

Iteration 46 sharpens that remaining question one step further.

The current strongest explanatory signature is now:

- repeating inherited child sites do not differ only by eventual gate success
- they also retain a different neighbor-role mix at the matched descendant step
  where the repeating lane first becomes gate-ready again

Current trace-backed result:

- repeating `path_node + split_child_inheriting` descendants share:
  - `basin_support`
  - `basin_load_carrier`
  neighbors
- one-shot `carrier_site + split_child_inheriting` descendants instead share:
  - `basin_support`
  - `ridge_support`
  neighbors

So the remaining open language boundary is now narrower again:

- not only whether child sites inherit candidacy
- not only whether those child sites eventually cross the gate
- but whether inherited child-site reentry support / neighborhood class is
  itself a truthful source distinction

That is still not enough by itself to justify a new field immediately.
But it does identify the most direct next candidate if `settlement_regime`
continues to grow.

### 17.8.7 Descendant Support Isolation

Iteration 47 narrows the remaining boundary further by factoring out what the
two inherited-child lanes still share.

Current trace-backed result:

- both lanes keep the same descendant degree at the matched step
- both lanes keep nearly the same common `basin_support` weight
- the isolated surviving difference is the secondary non-support role:
  - repeating lane: `basin_load_carrier`
  - one-shot lane: `ridge_support`

So the strongest current language statement is now:

- post-split reentry readiness is not best described by total support burden
- it is more tightly correlated with the secondary inherited support class that
  remains attached to the derived child sites

That makes the remaining candidate distinction narrower than a full
“neighborhood class” field.
If the family continues, the next direct proposal should be framed closer to:

- inherited secondary support class for descendant reentry

rather than reopening settlement-regime structure more broadly.

### 17.8.8 Secondary Support Counterfactual

Iteration 48 runs the decisive next check on that narrowed candidate.

Current trace-backed result:

- removing descendant secondary `basin_load_carrier` support from the repeating
  path-derived lane removes reentry
- removing descendant secondary `ridge_support` from the one-shot carrier-derived
  lane does not rescue reentry

So the strongest current language statement is now:

- inherited secondary support class is not merely a correlated trace signature
- retained secondary `basin_load_carrier` support is necessary for the current
  repeating reentry regime
- and secondary `ridge_support` removal alone is not sufficient to create the
  same regime

That is strong enough to treat as a real closure boundary for this semantic
slice.
If the family continues from here, the next move should be an explicit naming
decision rather than one more diagnostic refinement.

### 17.8.9 Why The Next Step Is Not Immediate Promotion

The current recommendation is to **stop and record Iteration 48 as the closure
boundary for the present `settlement_regime` slice**, rather than immediately
promoting inherited secondary support class into a new field.

Why:

- Iteration 48 proves a runtime-behavior necessity
- but not yet a clean direct-translation source contract
- promoting it immediately would risk turning a traced runtime dependency into
  source truth before the authoring gap is shown explicitly

So the next justified question is not:

- “what should the new `settlement_regime` field be called?”

It is:

- “can existing structural families already author the required descendant
  secondary `basin_load_carrier` support condition?”

If yes:

- no new `settlement_regime` field is needed
- the traced secondary support class is a downstream consequence of already
  authorable structure

If no:

- then the new field becomes justified by a genuine translation gap rather than
  by post-hoc behavioral interpretation

### 17.8.10 Secondary Support Structural Authorability

Iteration 49 closes that translation-gap question for the current spindle lane.

Current trace-backed result:

- the pre-`settlement_regime` structural path lane already produces:
  - repeating descendant reentry
  - secondary `basin_load_carrier` support
- the later explicit path lane produces the same condition
- between those two path seeds, the only added family is `settlement_regime`

And across the decisive existing-family comparison:

- `transfer_mediation` differs between the productive path lane and the
  non-productive direct control
- `interior_load_carriers` does not
- `channel_geometry` does not
- `boundary_geometry` does not

So the strongest current language statement becomes:

- inherited secondary `basin_load_carrier` support is already a downstream
  consequence of existing authorable `transfer_mediation` structure in this
  lane
- there is no present translation gap here
- therefore no new `settlement_regime` field is justified on this basis

This also gives the family a clean current closure:

- `settlement_regime` remains the right executable language for:
  - first productive settlement locus
  - split-child inheritance behavior
- but it does not presently need another field for descendant secondary support
  class
- because that condition is already authored downstream by existing
  `transfer_mediation` structure in this lane

### 17.8.11 Collapse Closure Record

The collapse-side investigation is also now closed at the current vocabulary
boundary.

What the Iteration 50 to 55 trace bundle supports is:

- collapse-capable lanes are real and plural
- those lanes are heterogeneous across pre-spark and post-spark regimes
- but the traced differences still close inside already-authored structure
- including the stricter post-collapse question of why flow stops preferring an
  initially chosen sink

The right vocabulary statement is therefore:

- `GRCL-v3` may describe source-side structure that later yields collapse
  behavior
- it may also describe source-side geometry that later reroutes preference away
  from an initially chosen sink
- but it still may not encode solved collapse outcomes, explicit anti-reentry
  commands, or a declaration that a node must never be chosen again

In the current evidence bundle, the post-collapse shift is best described as
geometry-mediated rerouting of preference inside existing
`transfer_mediation.center_coupling_classes`, not as a missing collapse family
or a missing persistence rule.

So the present vocabulary closure is:

- no new collapse-side source family is justified
- no explicit anti-reentry field belongs in source language
- and collapse does not remain the default next discovery lane under the
  current `GRCL-v3` record

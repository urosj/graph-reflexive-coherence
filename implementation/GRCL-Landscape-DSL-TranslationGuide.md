# GRCL Landscape DSL Translation Guide

This document defines the meaning of the PDE-side landscape DSL when it is
translated into the `PyGRC` world.

For this project, `GRCL` means:

- a theory-facing `GRC` landscape language,
- derived from the PDE landscape DSL,
- but interpreted in a way that remains valid across all discrete `GRC`
  families.

This guide exists so that later work does not confuse:

- source meaning,
- family-specific realization,
- and compiler/runtime convenience.

It should be read before:

- `LandscapeToGRCPlan.md`,
- any landscape-seed schema,
- any family-specific projection rules,
- and any PDE-to-discrete parameter-family mapping.

## 1. Role

The purpose of this guide is to define a stable semantic bridge between:

- the compositional landscape language used in the PDE program,
- and the family-neutral concepts that later discrete implementations must
  preserve.

This guide is intentionally earlier than implementation shape. Its job is to
answer:

- what the landscape primitives mean,
- which parts of that meaning are structural,
- which parts are constitutive,
- which parts are only compiler/projection artifacts,
- and which obligations every later `PyGRC` projection must satisfy.

## 1.1 From Field To Graph-Reflexive Structure

The source landscape DSL was introduced in a PDE setting where coherence is
described as a field over a Euclidean domain. `PyGRC` does not inherit that
domain literally. Instead, it must translate the same reflexive-coherence
intent into discrete substrates.

The core translation is therefore:

| Source idea | Continuous RC / landscape view | `GRCL` family-neutral view |
| --- | --- | --- |
| Domain | support over a spatial field | support over a discrete substrate |
| State | coherence field `C(x)` | coherence carried by discrete support units |
| Geometry | induced by the coherence-dependent constitutive object | induced by local discrete constitutive summaries and adjacency |
| Identity | stable basin/attractor structure | stable support region that may later realize as sink, basin, or module |
| Boundary | steep barrier/interface region | interface constraint or transport-resistant separator |
| Transport | flux over the field | directed transfer over discrete adjacency relations |

This table should be read carefully:

- it is a conceptual translation,
- not a claim that one discrete family exactly reproduces the PDE substrate,
- and not a commitment that all families use the same numerical objects.

For example:

- `GRCV2` may realize support using weighted graph nodes and edges,
- `GRCV3` may add basin-attribute and differential summaries,
- `GRC9` may realize the same source intent through port-structured mechanics.

Those are realizations of the source meaning, not the meaning itself.

## 2. Non-Goals

This guide does not:

- define final Python dataclasses,
- define the final seed schema,
- define final defaults for all parameters,
- choose one discrete backend,
- or declare that one family's realization is the true meaning of the source
  language.

In particular, this guide must not let:

- `GRCV2` weighted-graph convenience,
- `GRCV3` semantic summaries,
- or `GRC9` mechanical port structure

become the semantic definition of the source DSL.

## 3. Main Claim

The PDE landscape DSL is not merely an initializer format.

It is a compositional source language for declaring reflexive-coherence
structure before that structure is projected into any one numerical substrate.

Its primitives describe things such as:

- identity-support regions,
- interfaces and membranes,
- transport corridors,
- routing and branching sites,
- containment and compartment nesting,
- constitutive coefficients,
- and potential-family intent.

That means the correct translation order is:

1. recover the source meaning,
2. define a family-neutral `GRCL` interpretation,
3. only then project into `GRCV2`, `GRCV3`, `GRC9`, or `GRC9V3`.

Another way to state this:

- the landscape DSL declares reflexive-coherence architecture,
- `GRCL` preserves that architecture in family-neutral terms,
- and each family then supplies one admissible discrete realization.

## 4. Semantic Strata

The source DSL contains three different kinds of information. They should not
be mixed.

### 4.1 Structural Semantics

These describe what kind of reflexive-coherence object is being declared.

Examples:

- basin,
- ridge,
- valley,
- routing junction,
- containment,
- relative inside/outside relationships,
- path connectivity,
- and support-scale hints.

This is the most important layer and must survive every later projection.

### 4.2 Constitutive Semantics

These describe how the declared structure should behave dynamically once
realized.

Examples:

- `lambda_C`,
- `xi_C`,
- `zeta_C`,
- `kappa_C`,
- `dt`,
- potential family,
- potential parameters,
- and initial transport intent.

These are not merely rendering or compilation knobs. They help determine how
geometry, flow, and identity evolve.

In continuous RC language, these are the coefficients and constitutive choices
that shape the induced geometry rather than merely decorating a finished
structure. The same principle must hold in the discrete bridge: they are part
of the dynamical meaning of the seed.

### 4.3 Compiler / Projection Semantics

These describe how a particular runtime or compiler turns source intent into a
concrete numerical object.

Examples:

- composition mode,
- normalization mode,
- clamping/value-range policies,
- profile transforms,
- grid-spacing assumptions,
- periodic-wrap settings,
- and implementation-specific distance conventions.

These are important, but they are not the primary meaning of the source DSL.
They must not be promoted into the family-neutral semantic core unless there is
a strong theoretical reason to do so.

## 5. Primitive Meanings

The landscape paper and source examples imply the following neutral meanings.

## 5.1 Basin

A basin is a stable coherence-support region.

Its meaning is:

- a region that tends to accumulate or sustain coherence,
- an identity-support unit,
- a candidate compartment or sub-compartment,
- and a structural site around which later discrete identities may organize.

In continuous language, this corresponds to basin-like or attractor-like
support. In discrete language, it should be treated as a prior for identity
support, not as a guarantee that one particular runtime detector will produce
exactly one sink or exactly one node.

A basin is not automatically:

- a final discrete sink,
- a final node count,
- or proof that one node in a target graph must correspond to one basin.

What must survive projection:

- basin identity,
- basin role,
- containment relation,
- coherence prior,
- and approximate scale/location hints when the target family can use them.

## 5.2 Ridge

A ridge is an interface or membrane-like barrier structure.

Its meaning is:

- an interface separating regimes of coherence support,
- a steep transition zone,
- a transport-resisting or transport-shaping boundary,
- and a structural delimiter between compartments or between interior and
  exterior support.

In constitutive terms, a ridge usually marks a regime where interface effects
dominate over unrestricted mixing. In later discrete realizations, that may be
expressed by barrier conductances, delayed transport, restricted ports,
forbidden adjacencies, or other family-specific mechanisms.

A ridge is not primarily an identity-bearing object. In most later projections
it should appear as:

- a constraint on adjacency,
- a barrier modifier,
- a boundary primitive,
- or an interface annotation.

What must survive projection:

- which regions it separates,
- whether it is external or internal,
- its relative thickness/scale intent,
- and its role as a barrier rather than a basin.

## 5.3 Valley

A valley is a transport corridor.

Its meaning is:

- a preferred pathway for directed or facilitated flow,
- a structural channel between support regions,
- and a route along which coherence transfer is easier than across the
  surrounding substrate.

In continuous language, valleys are not merely low-valued places but shaped
transport routes. In discrete language, they should remain identifiable as
preferred transfer structure rather than dissolving into generic connectivity.

A valley is not merely a low-valued patch. In `GRCL`, it should be interpreted
functionally as a transport-supporting path.

What must survive projection:

- source and destination relation,
- path intent,
- approximate width/scale,
- and its routing function.

## 5.4 Saddle / Routing Junction

The source language may not always expose "saddle" as a first-class primitive,
but the theory clearly requires routing/choice sites.

Its meaning is:

- a branch-selection site,
- a mixed-stability region,
- a location where transport can be redistributed,
- and a structural precursor to later identity branching or decision dynamics.

In source examples, this may be encoded indirectly as:

- a small basin used as a hub,
- together with multiple outgoing valleys.

That encoding is acceptable, but the semantics should still be preserved as
"routing junction" rather than silently collapsed into "just another basin".

What must survive projection:

- junction role,
- branch targets,
- and its distinction from a generic storage basin.

This matters especially for later `GRCV3` and `GRC9` work, where branching,
spark, and refinement events can otherwise be over-read as purely mechanical or
purely graph-theoretic operations. The source-side meaning is routing and
choice structure.

## 5.5 Plateau

The paper-level ontology includes plateau-like regions even when the current
JSON schema does not expose them as a first-class primitive.

Its meaning is:

- a broad support region with weak internal differentiation,
- often hosting multiple sub-basins,
- and a federating support layer rather than a sharply isolated compartment.

This matters because later schema work should not assume the current primitive
set is semantically complete. `GRCL` must remain open to plateau-like support
structures even if the first discrete bridge expresses them by composition.

## 5.6 Parent / Containment

`parent` is not just a drawing convenience.

Its meaning is:

- compartment nesting,
- support inclusion,
- structural ownership,
- or containment of one coherent unit within another.

Containment must survive every later projection. It may be realized as:

- region nesting metadata,
- hierarchy edges,
- ownership annotations,
- or coarse-to-fine placement constraints,

but it must not be dropped merely because a target backend is flat.

For biological cell-like landscapes, containment is often the difference
between:

- one organelle inside a host region,

and:

- two peer regions connected in a flat graph.

Those are not semantically equivalent and should not be treated as
interchangeable.

## 6. Field Classification

The source DSL mixes fields with different semantic status. The bridge layer
must classify them explicitly.

### 6.1 Structural Fields

These fields describe structural intent and should generally survive into the
family-neutral seed.

Examples:

- `type`,
- `name`,
- `parent`,
- `from`,
- `to`,
- `center`,
- `radius`,
- `inner_radius`,
- `outer_radius`,
- `width`,
- `control_points`,
- primitive-local `coherence`,
- external/internal ridge kind,
- and geometric relation hints.

These should be interpreted as declarations of structure, not as already-final
numerical discretization.

### 6.2 Constitutive Fields

These fields define the dynamical regime associated with the declared
landscape.

Examples:

- `lambda_C`,
- `xi_C`,
- `zeta_C`,
- `kappa_C`,
- `dt`,
- potential family,
- potential parameters,
- and initial-flux settings.

These fields should usually survive into the translated seed as a constitutive
profile or regime attachment.

They are the most plausible bridge surface for later PDE-derived parameter
families, but only after structural translation is complete.

### 6.3 Projection / Compiler Fields

These fields may be necessary for PDE compilation or numerical realization but
should not be mistaken for source ontology.

Examples:

- `compile`,
- `composition_mode`,
- `mass_normalization`,
- `value_range`,
- `profile_transform`,
- `distance_mode`,
- periodic-wrap flags,
- grid-resolution assumptions,
- and other compiler-specific output controls.

These may later influence one realization path, but they should be explicitly
labeled as projection-side instructions rather than structural meaning.

That distinction is important because the PDE program necessarily contains
grid-specific and compiler-specific controls that a graph-native realization may
not share.

## 7. Family-Neutral Translation Axioms

The following axioms should govern later bridge work.

### 7.1 Basin Is a Support Primitive, Not a Guaranteed Final Sink

A source basin declares support intent. A target family may realize that basin
with:

- one node,
- many nodes,
- one basin plus surrounding interface structure,
- or a multi-scale arrangement.

The source meaning is therefore upstream of any one sink-detection result.

### 7.2 Ridge Is an Interface Primitive, Not a Basin with Different Numbers

Ridges should retain their barrier/interface role. They should not be converted
into ordinary support regions unless a family makes that transformation explicit
and records it.

### 7.3 Valley Is a Transport Primitive, Not Just Geometry

Valleys are functional corridors. A projection that preserves only their shape
but loses their transport meaning is incomplete.

The inverse error is also possible: preserving only a high-flux edge and losing
the fact that it was intended as a structured corridor between specific support
regions is also incomplete.

### 7.4 Routing Semantics Must Survive Encoding Tricks

If the source DSL encodes a junction by using a small basin plus branch valleys,
the translated meaning should still record:

- this is a routing site,
- not just an arbitrary local basin.

### 7.5 Containment Must Survive Flat Backends

Even if a target family uses a flat graph, the fact that one structure is
inside or owned by another must remain available as metadata or hierarchy.

### 7.6 Constitutive Profile Is Attached to Structure, Not Substituted for It

Parameter families do not replace structural translation. They act on already
translated structural seeds.

This is why parameter-family work must come after the `GRCL` meaning is fixed.

### 7.7 PDE Compilation Choices Must Not Be Mistaken for Universal Truth

If the PDE program uses one grid resolution, one normalization method, or one
distance convention, that does not automatically make those settings part of
the cross-family semantic core.

This is exactly why `GRCL` has to exist as an explicit layer. Without it, the
project would silently inherit PDE compiler decisions as if they were theory.

## 8. Concept-To-Realization Examples

To help later implementers, it is useful to state a few examples without
turning them into hard commitments.

### 8.1 Basin

A basin may later realize as:

- one weighted-graph node with a coherence prior,
- a cluster of nodes whose aggregate acts as one support region,
- one semantic basin record layered over several substrate nodes,
- or one mechanically distinguished module in a port graph.

All of those can be faithful if they preserve basin role and relations.

### 8.2 Ridge

A ridge may later realize as:

- weakened or penalized conductances,
- inflated geometric-length labels,
- explicit boundary annotations,
- ghost/barrier structures,
- restricted port exposure,
- or delayed transport.

No one of these is the universal meaning of ridge. They are candidate
realization strategies.

### 8.3 Valley

A valley may later realize as:

- a preferred weighted path,
- a channel annotation over several edges,
- a set of low-delay / high-coupling adjacencies,
- or a persistent port-family wiring rule.

Again, the meaning is the transport corridor, not the chosen mechanism.

### 8.4 Routing Junction

A routing junction may later realize as:

- a special basin-like support node,
- a branching semantic region,
- a spark-prone refinement site,
- or a mechanically saturated module that opens new branch structure.

Those realizations differ, but they should all remain legible as
routing/choice structure inherited from the source landscape.

## 9. Translation Obligations For Later Documents

Any later landscape bridge or seed schema should preserve, at minimum:

- primitive identity,
- primitive role,
- region-to-region adjacency intent,
- containment,
- routing/junction semantics,
- constitutive profile,
- potential-family selection,
- initial transport intent if present,
- and enough geometry hints to support later realization choices.

Any later document should explicitly say when it is:

- preserving source semantics,
- approximating them,
- or replacing them with a family-specific construction.

## 10. What Belongs To Family Projection Rather Than GRCL Meaning

The following questions belong downstream of this guide:

- how many nodes to allocate for one basin,
- whether a ridge becomes edge penalties, ghost boundary nodes, or port-level
  constraints,
- whether a valley becomes a weighted path, a directional channel annotation,
  or a port bundle,
- whether a routing junction becomes one node, a refinement scaffold, or a
  basin-plus-split mechanic,
- how ambient coordinates are synthesized when the source provided only hints,
- and how curvature, Hessians, or semantic summaries are numerically estimated.

These are family-specific realization choices. They are not the meaning of the
source DSL itself.

## 11. Consequences For Upcoming Work

This guide implies the following sequence.

### 11.1 Landscape Seed Schema Must Come Next

The seed schema should be designed as the first family-neutral carrier of:

- structural primitives,
- constitutive profile,
- routing semantics,
- containment,
- and geometry hints.

It should not directly mirror:

- PDE compiler internals,
- raw grid arrays,
- or one model family's native storage.

### 11.2 Parameter Families Come After Structural Translation

Parameter families should be defined over translated structural seeds or over
family-specific projections derived from them.

They should not be defined directly over raw PDE landscape files, because that
would blur:

- structural composition,
- constitutive regime,
- and runtime/compiler baggage.

### 11.3 Family-Specific Projection Documents Must Declare Losses

When `GRCV2`, `GRCV3`, or `GRC9` cannot preserve some source distinction
exactly, the projection document should name that loss explicitly rather than
silently collapsing meanings.

## 12. Resolved Positions For Seed Translation

The following questions were open during the first draft of this guide. Their
semantic positions are now resolved here so they do not get answered
accidentally by the seed schema.

### 12.1 Plateau Becomes A First-Class Neutral Primitive

Decision:

- `plateau` should be treated as a first-class neutral primitive.

Meaning:

- a broad, weakly differentiated support region,
- capable of hosting multiple sub-basins or later identity resolution,
- and not equivalent to a single basin or a generic low-gradient filler area.

Reason:

- the paper-level ontology already distinguishes plateau-like support from
  sharply localized basins,
- and collapsing plateau into mere composition would erase a meaningful source
  distinction before projection begins.

Boundary:

- this guide does not require one universal runtime policy such as "suppress
  spark for N warmup steps",
- because warmup, stabilization, or delayed-event handling are family/projector
  decisions rather than the semantic definition of plateau.

Implication for later work:

- the seed schema should allow `plateau` as a declared primitive even if some
  source files still encode it compositionally.

### 12.2 Separation Intent Is Semantic; Concrete Distance Is A Projection Choice

Decision:

- the neutral layer must preserve separation intent,
- but the exact metric implementation remains family-specific.

Meaning:

- the source may declare that some regions are distinct, adjacent, nested,
  transport-near, barrier-separated, or otherwise geometrically related,
- and those relations are semantic commitments,
- while the later computation of distance may be topological, induced,
  transport-weighted, or otherwise family-native.

Reason:

- RC geometry is induced rather than assumed as a fixed background,
- so a graph-native realization should not be forced to inherit PDE Euclidean
  distance as universal truth.

Boundary:

- if the later seed schema keeps a field named `distance_mode`, it should be
  interpreted as a geometry/separation hint rather than an obligation to use a
  particular PDE metric backend.
- schema naming can still be decided later. The semantic point is that
  separation intent is part of the source meaning, while metric construction is
  part of projection.

### 12.3 Initial Flux Intent Belongs In A Separate Transport-Intent Block

Decision:

- initial flux intent should be represented as its own transport-intent layer,
- not as raw constitutive coefficients alone,
- and not as directly prescribed edge/node flux values.

Meaning:

- the source may express that transport should preferentially run from one
  region to another, along a channel, or with a certain directional bias,
- but that intent should be translated into family-specific initialization of
  potential, geometry, mobility, or seed-time perturbation,
- rather than bypassing the reflexive closure by setting `J` directly.

Reason:

- in the RC loop, flux is a response to the constitutive and potential state,
  not an independent primitive to hardcode as the neutral seed truth.

Boundary:

- this guide does not force one single mechanism for realizing transport
  intent.
- one family may bias potentials,
- another may bias conductances or initial coherence gradients,
- and another may stage an explicit initialization event.

What is fixed here is the semantic boundary:

- transport intent is first-class,
- direct raw-flux assignment is not the neutral meaning.

### 12.4 Ridge Orientation And Anisotropy Must Be Preserved As Hints

Decision:

- ridge anisotropy and orientation should be preserved when present,
- but as optional neutral hints rather than as family-specific tensor or
  port-row data.

Meaning:

- the source may indicate a principal interface axis, preferred normal/tangent
  direction, or anisotropic permeability/barrier behavior,
- and that information should survive translation whenever available.

Reason:

- interface directionality is part of structural meaning,
- especially for membranes, channels, and selective transport boundaries,
- and losing it too early would force later families to invent incompatible
  replacement semantics.

Boundary:

- this guide does not define the representation as "gradient vector" or "row
  basis" at the neutral level.
- those are later projection choices.

Projection examples:

- `GRCV3` may map the hint into local directional differential summaries,
- `GRC9` may map it into row/column or port-constraint orientation,
- other families may reduce it to annotated edge/interface asymmetry.

### 12.5 The Common Kernel Is A Portable Floor, Not The Full Ceiling

Decision:

- the neutral seed needs a common portable kernel,
- but it must also allow family-specific extension data.

The portable floor should include at least:

- support/coherence priors,
- structural primitives and their identities,
- adjacency or connectivity intent,
- containment relations,
- routing/transport intent,
- constitutive profile,
- and geometry/interface hints that are not tied to one backend.

Optional additions may include:

- edge priors,
- relative separation hints,
- barrier strength hints,
- or other cross-family structural annotations.

Reason:

- a seed limited to only node coherence plus bare adjacency is too weak to
  carry many of the distinctions that the landscape DSL actually encodes,
- especially containment, routing semantics, ridges, and plateau support.

At the same time:

- the seed should not require all families to accept another family's native
  differential summaries, port bundles, or internal caches as part of the
  neutral core.

Therefore the correct rule is:

- define a required common kernel,
- then allow namespaced family-specific extension blocks.

Extension policy:

- family-specific attributes may be present,
- they must be explicitly scoped to the target family or projection layer,
- and unsupported families should ignore them rather than reinterpret them as
  neutral semantics.

## 13. Remaining Questions For Schema Design

The semantic questions above are now closed. What remains open is primarily
schema design rather than theory.

Questions still to decide later:

1. What exact field names should the seed schema use for:
   - transport intent,
   - separation/geometry hints,
   - anisotropy/orientation hints,
   - and family-specific extension namespaces?
2. Which neutral hints are required versus optional for a valid seed document?
3. How should validation distinguish:
   - missing neutral data,
   - optional projection hints,
   - and unsupported family-specific extensions?
4. Should plateau be represented as its own top-level primitive type, or as a
   region primitive with an explicit role/stability class?
5. How should projector-specific realization policies such as warmup,
   stabilization, or initialization events be documented without polluting the
   neutral semantic layer?

## 14. Recommended Follow-On Documents

Once this guide is accepted, the intended dependency order is:

1. `LandscapeToGRCPlan.md`
2. `LandscapeSeedSchema.md`
3. family-specific projection notes
4. parameter-family definitions built on top of translated seeds

That is the order that keeps source meaning stable while allowing later
implementation freedom.

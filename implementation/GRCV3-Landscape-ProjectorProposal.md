# GRCV3 Landscape Projector Proposal

## Purpose

This note defines the next corrective step for seed-driven `GRCV3` work after
the failed `cell-4` comparison against the saved `GRCV2` fulltest lane.

The goal is precise:

- do **not** change the `GRCV3` runtime equations first,
- do **not** hand-author special `cell-4-grcv3` source seeds,
- do **not** treat threshold loosening as the primary fix,
- but instead redesign the **family-local `LandscapeSeed -> GRCV3State`
  projector** so that existing `GRCL` seeds realize into a geometry-supporting
  `GRCV3` substrate.

## 1. Diagnosis

The current `cell-4` seed-driven `GRCV3` lane fails before spark/split
refinement can even begin.

Observed runtime outcome:

- `cell-4` reaches no events
- `spark_event_count = 0`
- `active_split_count = 0`
- `geometric_seed_count = 0`
- `active_basin_count = 3` remains flat through 100 steps

This contrasts sharply with the saved `GRCV2` fulltest lane, where `cell-4`
enters a growth regime:

- `birth_count = 58`
- `num_nodes = 64`
- `num_edges = 67`
- `sink_count = 18`

### 1.1 Immediate Cause

The current `GRCV3` projector realizes `cell-4` into a sparse 6-node graph:

- `cytoplasm`
- `nucleus`
- `mitochondrion_1`
- `mitochondrion_2`
- `mitochondrion_3`
- `routing_junction`

with 9 edges:

- 5 ridge/support edges
- 4 valley/channel edges

Degree profile:

- `cytoplasm`: degree 5
- `routing_junction`: degree 5
- `nucleus`: degree 2
- each mitochondrion: degree 2

This graph is semantically meaningful, but too coarse for the current
`GRCV3` differential summary stack.

### 1.2 Why The Spark Layer Never Activates

The current `GRCV3` runtime requires:

1. differential summaries from local neighborhoods,
2. geometric seed validation,
3. spark candidate detection,
4. split initialization and continuation.

In `cell-4`, that chain breaks at geometric seed validation.

What we observed:

- the only nodes with nontrivial Hessians are the two hubs
  - `cytoplasm`
  - `routing_junction`
- those hubs have gradient norms far above `eps_gradient`
- the degree-2 leaf nodes have nearly flat Hessians
- so:
  - hubs fail the gradient gate
  - leaves fail the curvature gate

Therefore:

- `geometric_identity.seed_nodes = []`
- spark detection falls back to basin representatives/sinks
- those are exactly the flat leaf nodes
- no spark candidates are ever emitted

The spark layer is not “wrong”; it is starved of the kind of local geometry it
expects.

## 2. Key Conclusion

The problem is **not yet** that `GRCL` lacks semantic meaning.

The problem is that the current `GRCL -> GRCV3` realization is too coarse.

That distinction must remain explicit:

- `GRCL` may already be semantically rich enough,
- while the current family-local projector is operationally too thin.

So the first corrective move should be:

- enrich the **realized initial substrate**
- while keeping the **source seed** unchanged

rather than immediately expanding the source language.

## 3. Boundary Conditions

This proposal intentionally preserves the following boundaries.

### 3.1 What Stays Unchanged

- `GRCV3` step order
- differential summary backend semantics
- spark detection semantics
- split lifecycle semantics
- hierarchy semantics
- shared `GRCL` source fixtures such as:
  - `cell-1.seed.yaml`
  - `cell-4.seed.yaml`

### 3.2 What Changes

- only the family-local projector in:
  - `src/pygrc/models/grc_v3_landscape.py`

### 3.3 What Is Explicitly Deferred

- adding new `GRCL` schema fields
- changing common seed ontology
- changing spark thresholds just to force activity
- changing `GRCV3` runtime equations to compensate for a weak projector

## 4. Projector Principle

The `GRCV3` projector should no longer realize every source primitive as a
single node or single edge.

Instead, it should realize each primitive as a **small local motif** whenever
that is necessary to give `GRCV3`:

- meaningful neighborhood geometry,
- nontrivial local Hessians,
- candidate interior points,
- and channel/boundary structure that can actually participate in the reflexive
  loop.

The source seed remains the same. The richer structure is a family-local
realization policy.

## 5. Proposed Primitive Realization Rules

The first implementation should use deterministic, documented motifs derived
from the current seed information only.

## 5.1 Basin -> Core Patch

Current projector:

- basin-like primitive -> one node

Proposed `GRCV3` projector:

- basin-like primitive -> one **core patch**

Minimal first patch:

- 1 center node
- 3 or 4 support ring nodes around the center

The center node should carry:

- the canonical basin identity
- parent/depth semantics
- most of the coherence prior

Support ring nodes should carry:

- the same basin identity initially
- small distributed coherence mass
- local chart-derived offsets around the center

Purpose:

- create an interior point with multiple neighbors
- allow meaningful WLS differential reconstruction
- avoid degree-1/degree-2 stagnation at every semantically important region

Deterministic placement source:

- `chart_center_hint`
- `chart_scale_hint.radius` when present
- otherwise a small projector default radius

## 5.2 Ridge -> Boundary Support Arc

Current projector:

- ridge -> one support edge or metadata-only marker

Proposed `GRCV3` projector:

- ridge -> one or more **boundary support nodes** connected to the owning basin
  patch

Minimal first realization:

- for each explicit ridge, create 2 or 3 boundary support nodes placed on the
  principal normal or on a small arc around the owner center

These support nodes should:

- carry lower coherence than the owner interior
- connect to the owner patch
- optionally connect to explicit adjacent structure if the ridge is not
  metadata-only

Implementation guard:

- if the ridge is listed in `blueprint.metadata_only_ridge_ids`, do **not**
  synthesize explicit ridge support nodes for it in Revision 1
- preserve it as metadata-only until a later projector revision explicitly
  chooses to materialize metadata-only boundaries

Purpose:

- give the basin boundary an explicit local stencil
- let local geometry see a real interior/boundary transition
- avoid representing membrane/boundary semantics as just one abstract edge

## 5.3 Valley -> Channel Chain

Current projector:

- valley -> one edge

Proposed `GRCV3` projector:

- valley -> a short **channel chain**

Minimal first realization:

- 1 interior channel node between source and target patches
- or 2 channel nodes if waypoints imply curvature

Deterministic layout source:

- if waypoints exist, use them
- otherwise use the midpoint between source and target basin centers

Coherence initialization:

- distribute valley `coherence_prior` across the channel nodes
- attach channel nodes to the source/target basin patches, not only to the
  semantic basin centers

Purpose:

- create an actual transport corridor instead of a single graph edge
- give local differential structure along the channel
- support interior curvature and transport asymmetry in later runtime states

## 5.4 Junction -> Routing Motif

Current projector:

- junction-like or routing primitive -> one node

Proposed `GRCV3` projector:

- routing hub -> one **junction motif**

Minimal first realization:

- 1 junction center
- 3 branch interface nodes, one per outgoing channel family

In `cell-4`, that means the routing hub should not be a single node with degree
5. It should be a small local stencil whose branch points connect to:

- nucleus channel,
- mitochondrion 1 channel,
- mitochondrion 2 channel,
- mitochondrion 3 channel.

Purpose:

- prevent the routing region from being the only nontrivial Hessian carrier
- create enough local anisotropy for the differential layer to identify a
  meaningful interior structure rather than a flat star center

## 5.5 Plateau -> Support Patch

Plateau support is not the immediate blocker for `cell-4`, but the same rule
should apply if/when plateaus are projected into `GRCV3`:

- plateau -> low-curvature support patch
- not one node

That preserves the meaning of meta-stable support regions without reducing them
to degree-poor placeholders.

## 6. Initialization Policy

The projector should distribute coherence and conductance deterministically
within each motif.

Recommended baseline rules:

- preserve total seed budget exactly
- keep semantic owner IDs stable
- assign one canonical center node per primitive as the semantic anchor
- distribute remaining primitive mass over support nodes using fixed ratios
- initialize support-node gradients and Hessians implicitly through geometry and
  topology, not by hand-authoring differential summaries

### 6.1 Exact Budget Rule

This must be explicit before implementation.

When one source primitive is expanded into a motif with multiple runtime nodes,
the primitive coherence prior must be partitioned **inside the motif first**
rather than copied to each realized node.

Required rule:

- for a primitive with raw coherence prior `m_p`
- and a realized motif with node-local mass fractions
  `r_1, ..., r_n` such that:
  - each `r_k >= 0`
  - and `sum_k r_k = 1`
- define node-local raw masses as:
  - `m_{p,k} = m_p * r_k`

Then compute the global budget scale factor from the **expanded** raw mass sum:

- `total_raw_mass_expanded = sum_{all realized nodes} m_{p,k}`
- since each motif partition sums back to its source primitive mass,
  `total_raw_mass_expanded` must equal the original primitive-level raw total

And finally initialize coherence per realized node as:

- `C_{p,k} = m_{p,k} * mass_scale`
- with `mass_scale = budget_target / total_raw_mass_expanded`

This preserves:

- exact total seed budget
- exact primitive-level mass contribution
- deterministic internal motif allocation

It also avoids the incorrect alternative where each realized motif node would
inherit the full primitive mass, which would inflate total coherence by the
motif expansion factor.

Revision 1 should use fixed deterministic motif ratios, for example:

- basin patch:
  - center gets the dominant fraction
  - ring/support nodes share the remainder equally
- ridge support arc:
  - support nodes share the ridge-local allocation equally
- valley channel chain:
  - channel nodes share the valley-local allocation equally unless waypoint
    weighting is added later
- junction motif:
  - center gets a dominant fraction
  - branch interface nodes share the remainder equally

The exact ratios must be documented once chosen and tested as part of the
projector contract.

Revision 1 chosen baseline:

- basin patch:
  - 1 center node
  - 3 support nodes
  - center mass fraction = `0.7`
  - each support node mass fraction = `0.1`
- junction motif:
  - 1 junction center node
  - 1 branch-interface node per incident valley
  - center mass fraction = `0.6`
  - branch-interface nodes share the remaining `0.4` equally
- ridge support arc:
  - 2 explicit ridge support nodes per realizable ridge
  - metadata-only ridges remain metadata-only in Revision 1
- valley channel chain:
  - `1` channel node when no waypoints are present
  - `2` channel nodes when waypoints are present
  - valley mass split equally across channel nodes

These values are now part of the executable projector contract and should only
change through an explicit projector-revision note plus test updates.

### 6.2 Deterministic Geometry Fallbacks

The first projector revision should define fallback geometry values explicitly.

Required baseline:

- if `chart_scale_hint.radius` is missing, use a family-local deterministic
  default radius
- if richer scale hints are unavailable, use the same default consistently for
  all motifs of the same projector revision

Revision 1 chosen baseline:

- default projector radius = `0.05`
- basin support radius = `0.45 * primitive_radius`
- junction branch radius = `0.45 * primitive_radius`
- support-ring angles =
  - `0`
  - `2π/3`
  - `4π/3`
- ridge support points =
  - the two interior quarter-points on the owner-to-target chart segment

This keeps motif layout reproducible even when the source seed does not provide
full geometric sizing information.

Important:

- the projector should still initialize `BasinAttributes`
- but it should **not** fake differential geometry by writing arbitrary
  Hessians/gradients just to trigger spark behavior

The local geometry should emerge from the realized motif and the existing
runtime differential pass.

## 7. Acceptance Criteria

The first successful projector revision should satisfy all of the following.

### 7.1 Structural Acceptance

- `cell-4` realizes to a graph denser than the current 6-node/9-edge graph
- basin interiors are no longer represented only by single semantic nodes
- valley/channel structure contains explicit intermediate nodes
- routing hubs are realized as local motifs rather than single stars
- exact initialized coherence sum matches `budget_target`

### 7.2 Geometric Acceptance

Within the first few runtime steps:

- `geometric_identity.seed_nodes` should become non-empty for `cell-4`
- at least one interior candidate should have:
  - `gradient_norm < eps_gradient`
  - and `min_signed_eigenvalue > eps_hessian`
- spark candidate detection should emit at least one candidate on `cell-4`

### 7.3 Runtime Acceptance

Over a representative run horizon:

- `cell-1` should remain comparatively quiet
- `cell-4` should no longer be event-empty
- `cell-4` should produce at least one topology-changing event path:
  - spark candidate
  - spark confirmation
  - split init/progress/complete

### 7.4 Comparison Acceptance

Only after the above holds should a new `GRCV3` 100-step candidate be compared
again against the saved `GRCV2` fulltest lane.

The first comparison target is not exact equality of outcomes.
The first comparison target is:

- `cell-1` quiet, `cell-4` structurally richer
- rather than both staying in a quiescent no-event regime

### 7.5 Determinism Acceptance

- the same source seed and parameter envelope always produce the same:
  - realized node count
  - realized edge count
  - motif-local connectivity
  - initial coherence allocation
  - chart-hint-derived placement metadata

These need explicit unit tests so the projector does not drift while `GRCV3`
runtime work continues.

## 8. Why This Is Preferable To Source Expansion First

This approach is preferred because it:

- preserves a single shared source seed,
- keeps family differences where they belong,
- does not hide the problem behind per-example seeds,
- and tests whether the current `GRCL` meaning is already sufficient.

Only if this richer projector still fails should we conclude that `GRCL`
requires new family-specific hint fields or a dedicated family-rich seed layer.

## 9. If GRCV3-Rich Seed Extensions Become Necessary Later

Those should be introduced only after the projector-only attempt is exhausted.

That condition is now met. See:

- [GRCV3-RichSeed-Rationale.md](./GRCV3-RichSeed-Rationale.md)
- [GRCL-V3-ImplementationPlan.md](./GRCL-V3-ImplementationPlan.md)

The projector-only attempt established three facts:

- manual `GRCV3` spark states are executable
- richer neutral/common projector realization improves geometry but does not
  unlock sparks for `cell-4`
- a richer neutral/common cross-probe seed still does not produce a sparkable
  projected geometry

So the remaining gap is not just “more nodes.” It is geometry-bearing source
expressivity.

Likely later extension candidates would be:

- preferred basin patch density
- preferred channel subdivision count
- junction branch-arity realization hints
- ridge discretization density hints
- explicit geometry-bearing local motif definitions
- local differential intent relevant to weak-axis formation

But these should be treated as optional later refinements, not as the first
response.

## 10. Recommended Next Step

Implement **Projector Revision 1** with the following constrained scope:

1. Basin core patch motif
2. Valley channel chain motif
3. Routing junction motif
4. No runtime-equation changes
5. No seed-schema changes
6. Re-run `cell-4` short diagnostics first
7. Only then re-run the 100-step candidate lane, but only if the diagnostic gate
   actually passes

That is the cleanest way to determine whether the failure is really due to
coarse realization rather than to deeper `GRCV3` constitutive issues.

Post-Iteration-8 status:

- the diagnostic gate did **not** pass honestly
- therefore the representative rerun is intentionally deferred
- the next justified move is a `GRCV3`-rich seed layer, not Iteration 9 under
  the current neutral/common seed contract
- if the first small rich-seed gate passes, the correct escalation is full
  `GRCL-v3` capability rather than further neutral/common projector patching
  alone

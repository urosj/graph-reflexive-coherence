# Phase 5 Landscape Projector Checklist

This document tracks the implementation of the **GRCV3 landscape-projector
revision** described in
[GRCV3-Landscape-ProjectorProposal.md](./GRCV3-Landscape-ProjectorProposal.md).

It exists because Phase 5 baseline runtime closeout was correct for intrinsic
`GRCV3`, but the current `GRCL -> GRCV3` projector remains too coarse for
seed-driven `cell-4` behavior.

Use this checklist as the execution tracker.
Use the proposal as the scope, boundary, and acceptance document.

## Usage Rules

- Do not change `GRCV3` runtime equations as part of this checklist unless the
  projector-only attempt proves insufficient.
- Do not add new `GRCL` schema fields in Revision 1.
- Do not loosen spark thresholds merely to force events.
- Keep mass allocation, motif topology, and chart-hint realization
  deterministic and documented.
- Record every constitutive projector choice here when it becomes executable.

## Iteration Template

Copy this section for each new iteration.

```markdown
## Iteration N. <Short Name>

### Goal

<What this iteration is intended to complete>

### Checks

- [ ] <Concrete task 1>
- [ ] <Concrete task 2>
- [ ] <Concrete task 3>

### Implementation Notes

- <Important implementation detail, decision, or constraint>

### Verification

- [ ] <Import / test / review check>
- [ ] <Boundary / acceptance check>

### Summary

<Short outcome summary once iteration is complete>
```

## Iteration 0. Checklist Bootstrap

### Goal

Turn the projector proposal into an explicit tracked follow-on before any
family-local projector code changes begin.

### Checks

- [x] Link this checklist from:
  - `ImplementationPhases.md`
  - `Phase-5-ImplementationPlan.md`
  - `Phase-5-ImplementationChecklist.md`
- [x] State explicitly that `GRCV3-Landscape-ProjectorProposal.md` is the scope
  and boundary document for this follow-on
- [x] Record that this work is a Phase 5 follow-on rather than a Phase 6 task

### Implementation Notes

- The proposal already contains the theory-facing diagnosis and the initial
  acceptance ladder.
- This checklist should focus on executable sequencing and verification gates.

### Verification

- [x] The top-level phase registry points to this checklist
- [x] Phase 5 docs mention the follow-on explicitly rather than leaving it as
  conversation-only context

### Summary

Completed. The projector proposal is now promoted into an explicit tracked
Phase 5 follow-on with links from the top-level phase registry and the Phase 5
plan/checklist surfaces.

## Iteration 1. Motif Contract And Exact Budget Rule

### Goal

Lock the deterministic motif vocabulary and exact mass-allocation rule before
any topology expansion logic lands.

### Checks

- [x] Define the Revision 1 motif vocabulary:
  - basin core patch
  - valley channel chain
  - routing junction motif
  - explicit ridge support arc
- [x] Define the exact per-motif mass partition rule
- [x] Define deterministic default motif sizes for Revision 1
- [x] Define the default chart-scale fallback radius when source hints are absent
- [x] Define deterministic node-role names and metadata keys for motif members

### Implementation Notes

- The critical invariant is:
  - sum of initialized motif-node coherence equals the original seed budget
- Primitive mass must be partitioned inside the motif before global budget
  scaling is applied.
- Metadata-only ridges remain metadata-only in Revision 1.
- Ridge support arcs are part of the locked Revision 1 vocabulary, but their
  actual realization remains deferred to Iteration 5.
- Revision 1 chosen contract:
  - basin patch = `1` center + `3` support nodes
  - basin center mass fraction = `0.7`
  - each basin support mass fraction = `0.1`
  - valley chain = `1` node without waypoints, `2` with waypoints
  - valley channel mass is split equally across realized channel nodes
  - default projector radius = `0.05`
  - basin support radius = `0.45 * primitive_radius`
  - node payloads now record:
    - `realized_key`
    - `motif_role`
    - `semantic_anchor`

### Verification

- [x] The chosen mass rule is written in code-facing terms, not only prose
- [x] Determinism and budget invariants are explicit and reviewable before code
  changes start

### Summary

Completed. The first executable projector contract is now explicit in both the
proposal and code: deterministic basin patches, deterministic valley channel
counts, exact motif-level mass partition, and deterministic fallback geometry.

## Iteration 2. Basin Core Patch Realization

### Goal

Replace one-node basin projection with deterministic basin patches.

### Checks

- [x] Implement basin center + support-ring motif realization
- [x] Keep one canonical semantic anchor node per basin primitive
- [x] Assign support-node placement from chart hints or the deterministic
  fallback radius
- [x] Partition primitive coherence across basin motif nodes according to the
  Iteration 1 contract
- [x] Preserve basin identity, parent, and depth semantics across motif members

### Implementation Notes

- The basin center should remain the canonical semantic owner.
- Support nodes should help local differential reconstruction without hand-made
  gradient/Hessian values.
- Implemented in:
  - `src/pygrc/models/grc_v3_landscape.py`
- Basin primitives now realize as:
  - one semantic anchor center node
  - three support-ring nodes
  - six internal structural edges:
    - three center-to-support spokes
    - three support-ring edges
- Initial patch conductance is intentionally asymmetric:
  - spoke weight = `primitive_mass`
  - ring weight = `0.5 * primitive_mass`
  - rationale:
    - keep the semantic center more strongly coupled to the support ring than
      support nodes are to each other
    - bias the initial patch toward a coherent interior with local boundary
      support rather than a free ring
- Canonical per-primitive metadata now includes:
  - anchor node id
  - all realized node ids
  - support node ids
  - realization mode and motif contract summary

### Verification

- [x] `cell-1` and `cell-4` both realize to denser basin interiors than the
  current one-node-per-basin surface
- [x] Initial total coherence still matches `budget_target`

Focused verification:

- `./.venv/bin/python -m unittest tests.models.test_grc_v3_landscape_runtime`
  - result: `Ran 5 tests ... OK`

### Summary

Completed. Basin-like seed primitives now realize as deterministic core patches
with exact budget partitioning and preserved semantic anchor identities.

## Iteration 3. Valley Channel Chain Realization

### Goal

Replace one-edge valley realization with explicit transport corridors.

### Checks

- [x] Implement one- or two-node channel chains for valleys
- [x] Use waypoints when present; otherwise use deterministic midpoint layout
- [x] Attach channels to basin patches rather than only semantic center nodes
- [x] Partition valley coherence across channel nodes deterministically
- [x] Preserve valley identity and transport-intent metadata through the expanded
  realization

### Implementation Notes

- The point is not visual richness. The point is to create local interior
  structure that the differential backend can actually read.
- Implemented in:
  - `src/pygrc/models/grc_v3_landscape.py`
- Valley primitives now realize as:
  - one channel node if no waypoints exist
  - two channel nodes if waypoints exist
  - one runtime edge per chain segment
- Channel chains now attach to the nearest basin support node rather than always
  to the semantic basin center.
- Ridge primitives remain on the pre-existing anchor-to-anchor realization path
  in this batch. Explicit ridge support arcs are still deferred to Iteration 5.
- Transport-intent multipliers were widened from:
  - one primitive -> one edge
  to:
  - one primitive -> all realized carrier edges

### Verification

- [x] Realized channel topology is deterministic for the same seed
- [x] Channel nodes participate in the initial runtime topology without breaking
  budget or identity metadata

Focused verification:

- `./.venv/bin/python -m unittest tests.models.test_grc_v3_landscape_runtime tests.telemetry.test_experiments tests.visualization.test_visualization`
  - result:
    - `Ran 5 tests ... OK`
    - `Ran 7 tests ... OK`
    - `Ran 22 tests ... OK`

### Summary

Completed. Valleys now realize as deterministic channel chains attached to
basin patches, with preserved transport metadata and exact coherence
partitioning across realized channel nodes.

## Iteration 4. Routing Junction Motif Realization

### Goal

Replace star-like routing hubs with local branch motifs that expose usable
anisotropy.

### Checks

- [x] Implement junction center + branch-interface motif realization
- [x] Define deterministic branch-node ordering
- [x] Connect branch interfaces to the corresponding channel families
- [x] Preserve host/parent semantics and explicit hostless-junction metadata if
  applicable
- [x] Ensure the routing hub is no longer represented as one degree-heavy star
  center

### Implementation Notes

- `cell-4` is the immediate target: the routing region must stop being a single
  degree-5 differential bottleneck.
- Revision 1 now realizes both:
  - explicit `junction` / `saddle` seed primitives
  - basin primitives tagged with `source_pde.implied_role = saddle_like_hub`
- Junction branch ordering is deterministic:
  - sort incident valley blueprints by `primitive_id`
  - create one branch-interface node per incident valley in that order
- Channel families now attach to the nearest available interface node before
  falling back to basin support nodes or semantic anchors.
- Hostless explicit junctions preserve:
  - `is_hostless`
  - `junction_anchor_mode`
  in realized node payloads.

### Verification

- [x] `cell-4` routing topology becomes motif-based rather than single-node
- [x] Junction realization remains deterministic and snapshot-safe

Focused verification:

- `./.venv/bin/python -m unittest tests.models.test_grc_v3_landscape_runtime`
  - result: `Ran 10 tests ... OK`

### Summary

Completed. Routing hubs now realize as deterministic junction motifs with one
semantic center plus one branch interface per incident valley. `cell-4`
`routing_junction` is no longer a single star node; it now realizes to `5`
nodes and `4` local junction edges, and explicit hostless junction seeds retain
their standalone anchor metadata.

## Iteration 5. Ridge Boundary Handling

### Goal

Materialize explicit ridge support only where Revision 1 intends it, while
keeping metadata-only boundaries stable.

### Checks

- [x] Implement explicit ridge support arcs for realizable ridges
- [x] Add the explicit guard that skips `blueprint.metadata_only_ridge_ids`
- [x] Preserve metadata-only ridges as metadata-only in Revision 1
- [x] Define how ridge support nodes attach to the owning basin patch
- [x] Preserve ridge-local metadata for later telemetry and visualization

### Implementation Notes

- `cell-1` currently relies on a metadata-only `plasma_membrane` ridge.
- Revision 1 should not silently materialize it unless a later projector
  revision explicitly chooses to do so.
- Realizable ridges now realize as:
  - two ridge support nodes
  - three support-arc segments
  between the selected source-side attachment node and the selected target-side
  attachment node.
- Metadata-only ridges are skipped explicitly and remain present only through
  cached metadata surfaces such as `landscape_metadata_only_ridge_ids`.

### Verification

- [x] Metadata-only ridges remain stable and non-ambiguous
- [x] Explicit ridges no longer collapse to a single abstract support edge

Focused verification:

- `./.venv/bin/python -m unittest tests.models.test_grc_v3_landscape_runtime`
  - result: `Ran 10 tests ... OK`

### Summary

Completed. Explicit ridges now realize as local support arcs, while
metadata-only ridges remain metadata-only. This moves `cell-1` from `8/13` to
`10/15` realized nodes/edges via the explicit `nuclear_envelope`, while
`plasma_membrane` remains unmaterialized by design.

## Iteration 6. State Initialization, Snapshot, And Replay Surface

### Goal

Make the richer projector surface fully reproducible and inspectable.

### Checks

- [x] Record motif-member roles and owner mappings in node payload metadata
- [x] Record motif-derived edge roles and transport-bias participation in edge
  payload metadata
- [x] Preserve enough projector metadata to explain the realized topology later
- [x] Ensure snapshot/save/load roundtrip preserves the expanded initial state
- [x] Ensure replay from a saved projector-expanded state is deterministic

### Implementation Notes

- The runtime should still derive differential summaries fresh.
- The projector should serialize realization structure, not fake downstream
  geometry.
- Cached projector surfaces now include:
  - `landscape_interface_node_ids_by_primitive_id`
  - `landscape_ridge_support_node_ids_by_primitive_id`
  - `landscape_mass_scale`
  - `landscape_realized_raw_mass_total`
  - `landscape_motif_contract`
- Edge payloads now preserve:
  - `landscape_base_conductance`
  - `transport_intent_multiplier`
  - `transport_biased_initial_conductance`
  so later telemetry and visualization can separate source conductance from
  transport-intent bias.

### Verification

- [x] Expanded states survive snapshot/save/load without topology drift
- [x] Replayed runs start from the same motif-expanded topology and mass layout

Focused verification:

- `./.venv/bin/python -m unittest tests.models.test_grc_v3_landscape_runtime`
  - result: `Ran 10 tests ... OK`

### Summary

Completed. The richer projector surface is now snapshot-safe and replay-stable:
the expanded topology, motif roles, conductance attribution, and cached
realization metadata survive save/load and reproduce identical short replay
digests.

## Iteration 7. Determinism And Projector Unit Tests

### Goal

Lock the projector revision down with direct structural tests before relying on
runtime behavior.

### Checks

- [x] Add tests for deterministic realized node count
- [x] Add tests for deterministic realized edge count
- [x] Add tests for deterministic motif-local connectivity
- [x] Add tests for exact initialized coherence sum against `budget_target`
- [x] Add tests for metadata-only ridge skip behavior
- [x] Add tests for default-radius fallback behavior

### Implementation Notes

- These tests should validate projector structure directly, not only downstream
  observables after stepping.
- Added direct projector/runtime tests for:
  - `cell-1` structural counts and metadata-only ridge skip
  - `cell-4` junction and ridge-support counts
  - hostless explicit junction anchor metadata
  - default-radius fallback placement
  - snapshot determinism and short replay stability

### Verification

- [x] The same seed and parameter envelope always realize identically
- [x] Projector tests fail if motif counts/connectivity/mass allocation drift

Focused verification:

- `./.venv/bin/python -m unittest tests.models.test_grc_v3_landscape_runtime tests.telemetry.test_experiments tests.visualization.test_visualization`
  - result: `Ran 39 tests ... OK`

### Summary

Completed. The projector revision now has direct structural coverage for motif
counts, connectivity, exact initialized mass, metadata-only ridge handling,
default-radius fallback, and save/load replay determinism.

## Iteration 8. Short `cell-4` Diagnostic Gate

### Goal

Check whether the richer projector actually unlocks the geometric path needed
for spark detection before spending time on long runs.

### Checks

- [x] Re-run short `cell-4` diagnostics with the revised projector
- [x] Inspect geometric seed nodes
- [x] Inspect representative candidate gradient norms and signed Hessian
  eigenvalues
- [x] Verify whether spark candidate detection becomes non-empty

### Implementation Notes

- This is the first real go/no-go gate.
- If `cell-4` still has no geometric seeds or spark candidates, pause and
  document why before moving to long runs.
- Boundary note:
  - this iteration now terminates in
    [GRCV3-RichSeed-Rationale.md](./GRCV3-RichSeed-Rationale.md)
  - the rationale explains why the next honest step is no longer Iteration 9
    under the current neutral/common seed contract
- Added reproducible developer diagnostic script:
  - `scripts/diagnose_grcv3_landscape_seed.py`
- Observed result under the unchanged `seed_baseline` parameter envelope:
  - initial projected surface: `43` nodes / `61` edges
  - exact pre-spark build produces one geometric seed:
    - node `20`
    - primitive `routing_junction`
    - motif role `junction_center`
    - gradient norm `~2.0e-05 < eps_gradient`
    - signed Hessian eigenvalues `[1.154996556..., 1.155003427...]`
  - spark candidate count remains `0`
- Reason the gate still fails:
  - the new junction center is now geometrically stable enough to pass the seed
    criterion
  - but it is too stable to pass spark degeneracy
  - `min_signed_eigenvalue ~= 1.155`, while `eps_spark = 0.001`
  - so the weakest curvature is not near the spark threshold
- Short runtime probe (`3` to `5` steps) shows:
  - `geometric_seed_count` falls back to `0`
  - `spark_event_count` remains `0`
  - `detect_spark_candidates()` remains empty
- Extended runtime probe (`100` steps) shows the same outcome:
  - steps `1..100`: `geometric_seed_count = 0`
  - steps `1..100`: `geometric_validated_basin_count = 0`
  - steps `1..100`: `spark_event_count = 0`
  - steps `1..100`: `candidate_count = 0`
  - so this is not just a short transient issue
- Manual direct-state probes and a richer neutral/common cross-probe seed were
  then used to disambiguate the failure mode:
  - manual `GRCV3` spark probes confirm the runtime spark/split path is
    reachable
  - richer neutral/common projection still fails to produce sparkable geometry
  - therefore the missing ingredient is geometry-bearing seed expressivity, not
    only graph richness

### Verification

- [ ] `geometric_identity.seed_nodes` is no longer empty for `cell-4`
- [ ] At least one spark candidate exists under the same parameter envelope

Focused verification:

- `./.venv/bin/python scripts/diagnose_grcv3_landscape_seed.py --steps 3 --limit 5`
  - result:
    - pre-spark `seed_nodes=[20]`
    - pre-spark `spark_candidates=0`
    - step `1..3` `geometric_seed_count=0`
    - step `1..3` `candidate_count=0`
- `./.venv/bin/python scripts/diagnose_grcv3_landscape_seed.py --steps 100 --limit 5`
  - result:
    - pre-spark `seed_nodes=[20]`
    - pre-spark `spark_candidates=0`
    - step `1..100` `geometric_seed_count=0`
    - step `1..100` `candidate_count=0`

### Summary

Executed, but the acceptance gate does not yet pass. The richer projector now
creates one genuine pre-spark geometric seed at the `routing_junction` center,
which is a real improvement over the old empty geometric layer. But spark
detection remains empty under the same parameter envelope because the new seed
is strongly positive-curvature and not near degeneracy. This means Iteration 8
served its purpose: it shows the projector revision alone improved local
geometry, but not enough to unlock spark/split behavior. Do not treat Iteration
9 as cleared on this basis alone. The follow-on conclusion is recorded in
[GRCV3-RichSeed-Rationale.md](./GRCV3-RichSeed-Rationale.md).

## Iteration 9. Representative Candidate Rerun

### Goal

Repeat the seed-driven candidate run only after the short diagnostic gate
passes.

### Checks

- [ ] Re-run the 100-step GRCV3 candidate lane for `cell-1` and `cell-4`
- [ ] Verify that `cell-1` remains comparatively quiet
- [ ] Verify that `cell-4` is no longer event-empty
- [ ] Record the resulting run IDs and artifact paths
- [ ] Compare the new candidate against the saved GRCV2 fulltest lane

### Implementation Notes

- The first comparison target is not exact equality with GRCV2.
- The first success criterion is escaping the quiescent no-event regime.
- Status:
  - intentionally deferred
  - see [GRCV3-RichSeed-Rationale.md](./GRCV3-RichSeed-Rationale.md)
  - current evidence does not justify rerunning the representative candidate
    lane under the same neutral/common seed contract

### Verification

- [ ] `cell-4` produces at least one topology-changing event path
- [ ] The revised projector makes `cell-4` qualitatively richer than `cell-1`

### Summary

Intentionally deferred. Iteration 8 did not satisfy the gate honestly, and the
rich-seed rationale now records why the next justified move is a `GRCV3`-rich
seed extension rather than a representative rerun under the same neutral/common
projection boundary.

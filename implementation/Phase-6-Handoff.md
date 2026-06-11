# Phase 6 Handoff

This document was the entry handoff from the completed `GRCV3` cycle into
Phase 6 (`GRC9`).

Phase 6 has now been implemented and closed as the mechanical `GRC9`
substrate.

Its retained purpose is now to keep explicit:

- what now exists and should be reused,
- what `GRC9` was allowed to inherit,
- what it had to keep separate,
- which mistakes from `GRCV2` / `GRCV3` it was not supposed to repeat,
- and what the current post-Phase-6 boundary now is.

Treat this as a historical entry-handoff plus current boundary note for
`GRC9`, not as the Phase 6 implementation plan itself.

For the implemented Phase 6 state, read:

1. [`Phase-6-ImplementationPlan.md`](./Phase-6-ImplementationPlan.md)
2. [`Phase-6-ImplementationChecklist.md`](./Phase-6-ImplementationChecklist.md)
3. [`Phase-6-StepLoop.md`](./Phase-6-StepLoop.md)
4. [`Phase-6-EquationMap.md`](./Phase-6-EquationMap.md)
5. [`Phase-6-MidGate-Review.md`](./Phase-6-MidGate-Review.md)
6. [`Phase-6-Closeout.md`](./Phase-6-Closeout.md)
7. [`Phase-6-GRC9-TelemetryContract.md`](./Phase-6-GRC9-TelemetryContract.md)
8. [`Phase-6-GRC9-RepresentativeTelemetry.md`](./Phase-6-GRC9-RepresentativeTelemetry.md)

## 0. Current Status

Phase 6 is now complete in the following sense:

- `GRC9` is implemented as an executable mechanical nine-slot family
- the representative eventful artifact lane exists
- one real-seed structural bridge lane exists
- closeout is based on saved evidence rather than tests alone

The current Phase 6 boundary must also be read honestly:

- the seed-driven `GRC9` lane is a structural bridge via the existing
  `GRCV2` landscape blueprint boundary
- it is valid and useful for Phase 6 mechanical evidence
- it is not a full family-native `GRCL-9` implementation
- it is not `GRC9V3`

## 1. Read First

Before writing follow-on `GRC9` family work, read these documents in this
order:

1. [`../specs/grc-9-spec.md`](../specs/grc-9-spec.md)
2. [`ImplementationPhases.md`](./ImplementationPhases.md)
3. [`Phase-0-BoundaryDecisions.md`](./Phase-0-BoundaryDecisions.md)
4. [`Phase-0-DeterminismConventions.md`](./Phase-0-DeterminismConventions.md)
5. [`Common-BackendStrategyPlan.md`](./Common-BackendStrategyPlan.md)
6. [`Phase-2-BackendMatrix.md`](./Phase-2-BackendMatrix.md)
7. [`Phase-2-ImplementationPlan.md`](./Phase-2-ImplementationPlan.md)
8. [`Phase-2-ImplementationChecklist.md`](./Phase-2-ImplementationChecklist.md)
9. [`Phase-4-Retrospective.md`](./Phase-4-Retrospective.md)
10. [`GRCV3-Retrospective.md`](./GRCV3-Retrospective.md)
11. [`GRCV3-Closeout.md`](./GRCV3-Closeout.md)
12. [`Phase-T-GRCV3-Closeout.md`](./Phase-T-GRCV3-Closeout.md)
13. [`Phase-T-ExperimentsRefactorChecklist.md`](./Phase-T-ExperimentsRefactorChecklist.md)
14. [`GRCL-V3-Handoff.md`](./GRCL-V3-Handoff.md)
15. [`GRCL-Landscape-DSL-TranslationGuide.md`](./GRCL-Landscape-DSL-TranslationGuide.md)
16. [`LandscapeSeedSchema.md`](./LandscapeSeedSchema.md)
17. [`LandscapeToGRCPlan.md`](./LandscapeToGRCPlan.md)
18. [`PDE-ParameterFamilyBridge.md`](./PDE-ParameterFamilyBridge.md)
19. [`GRCV3-RichSeed-Rationale.md`](./GRCV3-RichSeed-Rationale.md)

These together provide:

- the `GRC9` spec target,
- the already-fixed port-substrate and determinism commitments,
- the shared backend-selection pattern,
- the process failures already seen in `GRCV2` / `GRCV3`,
- the runtime/source/artifact separation that later families must preserve,
- the now-stabilized telemetry experiment surface that later family work should
  reuse rather than rebuild ad hoc,
- the current `GRCL-v3` closure boundary, including which late-cycle source
  questions are materially done and not the default next work,
- the current seed/landscape boundary that `GRC9` should reuse rather than
  reinterpret silently,
- and the strongest current evidence that a family-local rich seed can carry a
  nontrivial reflexive trajectory end to end once the source semantics are
  explicit enough.

## 2. What Already Exists And Must Be Reused

Phase 6 does not start from an empty codebase.

What already exists and should be reused directly:

- shared core contracts from `src/pygrc/core/`
- canonical params hashing and snapshot infrastructure from Phases 1 and 3
- the backend-selection contract from `src/pygrc/core/backends.py`
- the first-party deterministic `PortGraphBackend`
- shared telemetry and visualization infrastructure
- the refactored telemetry experiment surface and split test coverage from the
  completed Phase T experiment-structure lane
- the existing landscape seed layer and projector boundary documents
- the evidence pattern of a saved dense rich-source lane with telemetry and
  graph-visible artifacts

What already exists conceptually and should be reused as process structure:

- equation-map style paper-to-code traceability
- explicit step-loop documentation
- artifact-backed validation lanes
- closeout through real saved outputs rather than tests alone
- promotion of major family claims only after artifact-backed dense lanes exist

Phase 6 should not re-solve:

- first persistence story
- first determinism story
- first backend-selection story
- or first telemetry/visualization architecture
- or first proof that a rich family-local source lane can become stronger than
  a representative smoke once the right semantics are expressed

Those are already established.

It is also important to read the current closure boundary honestly:

- the latest `GRCL-v3` collapse-side search is materially closed for the
  current planning window
- the current `GRCL-v3` continuation is paused unless a genuinely new
  source-side distinction needs to be opened
- so Phase 6 does not need to wait for another default `GRCL-v3` cleanup pass
  before beginning

## 3. What GRC9 Must Keep Distinct

`GRC9` must be treated as a distinct substrate, not as `GRCV2` with extra
fields and not as `GRCV3` with ports added afterward.

The mechanical chart is constitutive.

That means Phase 6 must keep explicit:

- exactly nine ordered slots per node
- row/column semantics as part of the family substrate
- occupancy and rewiring as first-class state
- mechanical expansion/refinement semantics
- and any row-based constitutive updates that depend on the port chart itself

Do not flatten these into:

- a weighted graph plus metadata,
- or a semantic family with an optional port adapter,
- or a visualization-level convention only

If a concept is constitutive in `GRC9`, it belongs in the family runtime and
state model directly.

## 4. What GRC9 Must Not Silently Inherit

`GRC9` may reuse infrastructure, but it must not silently inherit semantic
assumptions that belong to other families.

In particular, do not silently inherit:

- `GRCV2` weighted-edge mental models as if ports were just decorated edges
- `GRCV3` basin-attribute semantics as if Phase 6 were already hybrid work
- `GRCV3` differential-summary defaults as if `GRC9` had the same constitutive
  geometry object
- landscape/projector assumptions that were only justified for weighted-graph
  families

If Phase 6 borrows a concept from another family, it must state:

- what is shared,
- what is renamed,
- and what differs mechanically.

## 5. Main Risks To Avoid

## 5.1 Runtime / Source / Artifact Confusion

The main lesson from `GRCV3` applies immediately.

Phase 6 must keep separate:

1. runtime constitutive correctness
2. source/lowering correctness
3. artifact/observability correctness

Do not let “the model runs” stand in for all three.

## 5.2 Treating The Port Substrate As Just Storage

The `PortGraphBackend` already exists, but that does not mean Phase 6 is mostly
done.

The backend is only the substrate.
The family still has to define:

- mechanical update semantics
- expansion/refinement rules
- row-based conductance/tensor laws
- and truthful event/telemetry meaning

Do not confuse substrate readiness with family readiness.

## 5.3 Smuggling Hybrid Semantics Into Phase 6

Phase 6 is `GRC9`, not `GRC9V3`.

That means Phase 6 should not quietly add:

- basin attributes,
- signed-Hessian semantics,
- hierarchy borrowed from `GRCV3`,
- or choice/collapse semantics that only make sense once the hybrid layer is
  explicit

If a feature really belongs to the hybrid family, leave it for Phase 7.

## 5.4 Late Experiment Evidence

`GRCV3` showed that the right questions often appear only after real runs and
saved artifacts exist.

Phase 6 should therefore plan at least:

- a pure-runtime control probe
- a representative artifact-backed lane
- and one real-seed or real-experiment lane

earlier than feels comfortable.

The stronger late-cycle lesson is now even more concrete:

- once `GRCV3` gained a saved rich-v4 direct-translation run with spark, split,
  and collapse all visible in artifacts, the family’s status changed
  materially

So for `GRC9`, do not stop at:

- “the runtime can do the event”

Push until at least one saved family-local lane shows:

- the event sequence
- the artifact trail
- and the visual legibility of the sequence

## 6. What Phase 6 Did Early

Before the implementation became large, Phase 6 needed to create:

1. a Phase 6 implementation plan
2. a Phase 6 implementation checklist
3. a `GRC9` equation map
4. a canonical `GRC9` step-loop document

Those now exist and answer:

- where the row-based constitutive update lives
- how mechanical spark/instability is detected
- how expansion modules are represented and applied
- how inactive-port growth is handled
- what counts as coarse-grain / Split state
- what the required deterministic event order is
- and which parts are strictly Phase 6 versus deferred to `GRC9V3`

## 7. Recommended Validation Ladder

Phase 6 adopted the same three-lane evidence ladder that `GRCV3`
clarified:

1. pure-runtime control probes
2. representative artifact-backed lane
3. real-seed / real-experiment lane

These lanes answer different questions and are now named explicitly in the
Phase 6 checklist/closeout rather than left implicit.

`GRCV3` now adds one more practical refinement to that ladder:

4. rich-source dense artifact lane

Meaning:

- once a family introduces family-local source semantics, it should aim for at
  least one dense saved run where those semantics produce the family’s
  characteristic nontrivial behavior under real artifact capture

For `GRCV3`, that lane now exists in the saved rich-v4 spark/collapse run.
`GRC9` should still assume it will need an equivalent lane before claiming
later rich-source family closure, but that lane was correctly deferred beyond
the Phase 6 mechanical closeout boundary.

## 8. Landscape Boundary For Phase 6

Phase 6 should reuse the current landscape/seed boundary carefully.

What it may inherit:

- neutral/common seed parsing
- the existing landscape validation model
- the documented projector-boundary discipline

What it must decide explicitly:

- whether `GRC9` needs family-local source semantics beyond the neutral/common
  layer
- whether row/column or mechanical interface hints need a family-specific seed
  extension
- and whether projector enrichment is sufficient for early `GRC9` evidence or
  only as a temporary compatibility path

The implemented Phase 6 answer is now explicit:

- projector-style structural grafting was accepted as a temporary
  compatibility/evidence path
- it was enough for mechanical Phase 6 closeout
- it was not promoted into a claim that `GRCL-9` already exists

Do not assume in advance that the current common seed surface is already rich
enough for mechanical families.

Also do not over-read the current `GRCV3` source state as a blocker:

- `GRCL-v3` remains available if Phase 6 later needs a sharper family-local
  source-language comparison
- but the current `GRCL-v3` lane is not the active default next project step
- and Phase 6 should start from its own constitutive mechanical questions
  rather than inheriting `GRCV3` source-side follow-ons by momentum

## 9. Final Handoff Rule

The implemented Phase 6 record should now be read through this sequence:

1. [Phase-6-Handoff.md](./Phase-6-Handoff.md)
2. [Phase-6-ImplementationPlan.md](./Phase-6-ImplementationPlan.md)
3. [Phase-6-ImplementationChecklist.md](./Phase-6-ImplementationChecklist.md)
4. [Phase-6-EquationMap.md](./Phase-6-EquationMap.md)
5. [Phase-6-StepLoop.md](./Phase-6-StepLoop.md)

Throughout implementation and closeout, one governing rule had to stay visible:

- reuse infrastructure aggressively
- but keep family semantics explicit

That is the main condition under which `GRC9` can move faster than `GRCV3`
without inheriting its avoidable confusion.

## 10. Post-Phase-6 Follow-On

After the completed mechanical Phase 6 closeout, the most likely next
`GRC9`-specific arc is:

1. `Phase-T-GRC9`
2. `GRCL-9`
3. `Phase-V-GRC9`

Meaning:

- `Phase-T-GRC9` should extend the current compact `GRC9` telemetry surface
  toward fuller family-specific telemetry/checkpoint parity
- `GRCL-9` should introduce the real family-native source/lowering layer that
  Phase 6 explicitly does not claim to have completed
- `Phase-V-GRC9` should then build graph/behavior visualization on top of that
  proper `GRCL-9`-driven lane rather than over-reading the current bridge lane

Only after that source-facing family work is explicit should later hybrid
`GRC9V3` work be read as standing on a complete `GRC9` mechanical-plus-source
base rather than only the Phase 6 mechanical substrate.

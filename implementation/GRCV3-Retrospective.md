# GRCV3 Retrospective

This document records the retrospective on the first full `GRCV3` cycle:

- Phase 5 semantic/runtime implementation
- later `GRCL-v3` source/lowering work
- Phase T telemetry closure
- and Phase V visualization closure

It exists for the same reason as
[Phase-4-Retrospective.md](./Phase-4-Retrospective.md):

- to record what worked,
- to record where time and clarity were lost,
- to make the next family implementation smoother,
- and to keep later work from rediscovering the same failure modes.

This is not a blame document. It is a precision document.

## 1. What GRCV3 Achieved Well

`GRCV3` did close on the things that matter most for a semantic reference
family.

At the end of the cycle, the project now has:

- a deterministic executable `GRCV3` step loop
- explicit basin attributes and hierarchy semantics
- explicit signed-Hessian handling
- deterministic save/load replay
- explicit choice / collapse state and events
- representative runtime evidence
- seed-driven telemetry and visualization on real `cell-1` / `cell-4` runs
- checkpoint-backed graph rendering
- and a richer `GRCL-v3` seed path that can express family-native geometry
- and a saved rich-v4 direct-translation artifact lane where spark, split, and
  collapse all occur in one inspectable run

That means the family is no longer a speculative design surface. It has:

- real runtime semantics,
- real artifact semantics,
- and real evidence lanes.

The architecture also held up under correction:

- the shared graph substrate remained usable
- the shared serializer remained usable
- the shared telemetry layer absorbed family-specific extensions cleanly
- the shared visualization stack could be extended rather than forked

That is important because `GRCV3` is not just another model. It is the first
family where semantic richness, geometry reconstruction, hierarchy, sparks, and
collapse all need to coexist without becoming opaque.

## 2. What Took Longer Than Expected

The biggest surprise was not inside the core `GRCV3` runtime.

The biggest surprise was that a family can be mathematically sound at runtime
and still fail to show the intended phenomena when the source seed and lowering
path are too weak.

That happened here.

Pure-runtime `GRCV3` probes could produce spark-capable behavior.
But the first seed-driven `cell-1` / `cell-4` runs, lowered from the weaker
neutral/common landscape surface, did not expose the same geometric conditions.

That was not a runtime bug in the usual sense.
It was a source-semantics and lowering-boundary problem.

In practice, the time sink came from three coupled facts:

1. the runtime was already good enough to invite confidence
2. the shared `GRCL` seed surface looked rich enough to seem reusable
3. the projector could produce runnable graphs, which made the mismatch easy to
   misread as “the family is behaving differently” rather than
   “the family was not given enough geometry-bearing structure”

That distinction mattered a lot.

## 3. The Main GRCV3 Lessons

## 3.1 The Core Lesson: Three Layers Of Correctness

One of the most important lessons from `GRCV3` is that there are at least three
different correctness layers:

1. runtime constitutive correctness
2. source/lowering correctness
3. artifact/observability correctness

All three matter.

The family can be correct at one layer and still fail at another.

This is the most important corrective to the easy but misleading sentence:

- “the model runs”

That is not a single closure criterion.

For `GRCV3`, this showed up clearly:

- the runtime spark logic could be made correct
- but shared weak seeds could still fail to generate sparkable local geometry
- and later, visualization could hide real collapse events if overlays were too
  weak or event emission was duplicated

That means future family work must not treat “the model runs” as a single
closure criterion.

Instead, each family should be validated through three separate questions:

1. Does the pure runtime realize the paper-facing semantics?
2. Does the seed/lowering path preserve enough structure to reach those
   semantics?
3. Do telemetry and visualization make the resulting behavior honestly visible?

Those three questions should stay explicit in future family plans rather than
being folded into one generic “implementation status” label.

## 3.2 Family-Native Lowering Matters Earlier Than It Looks

The first `GRCV3` landscape path reused too much of the `GRCV2` projector
intuition.

That was a useful bridge, but it created a hidden trap:

- it made `GRCV3` seed lowering appear “done enough”
- while still depending on a weaker semantic carrier than the family actually
  needed

The later `GRCL-v3` work clarified the right boundary:

- neutral/common seeds should remain available
- weak schemas should still lower through compatibility and enrichment paths
- but once a seed claims `grcv3.rich.v2+`, `GRCV3` should prefer
  family-native lowering rather than semantic interpretation through a
  `GRCV2`-shaped intermediate meaning layer

This is one of the clearest architectural outcomes of the whole cycle.

Future families should take the same lesson seriously:

- reuse common parsing and common validation
- but do not force family-specific semantics through a weaker family's mental
  model longer than necessary

Once a richer family-local schema exists, family-native lowering should be
treated as a design rule rather than postponed as cleanup.

## 3.3 Artifact-Backed Validation Is Not Optional

Another lesson from `GRCV3` is that code-level closure was not enough.

Several important corrections happened only because the artifact lanes were
actually run and inspected:

- the mismatch between `GRCV2` and early `GRCV3` `cell-4` outcomes
- the need for richer collapse visuals
- the late but real collapse in the rich fulltest lane
- and the duplicate choice/collapse event emission bug
- and, finally, the fact that the rich-v4 direct-translation lane was not just
  spark-capable but collapse-capable under a saved dense artifact run

The duplicate event bug is especially instructive.

The runtime itself looked plausible.
Tests were already present.
But once saved event artifacts were inspected carefully, it became clear that
`rebuild_choice_state()` was already appending emitted events and `step()` was
appending them again.

That is exactly the kind of defect that a purely local unit-level reading can
miss and a real artifact lane can reveal.

Future family work should therefore assume:

- if a semantic event exists,
- and if that event matters for interpretation,
- then at least one artifact-backed check must inspect the saved rows directly

## 3.4 Representative Lanes Are Necessary But Not Sufficient

The representative `GRCV3` runtime lane was useful.
It closed the baseline runtime and replay surface cleanly.

But it would have been a mistake to treat that lane as proof that the
family-level landscape path was also truthful.

That mistake was avoided only because the work later moved onto:

- real `cell-1` / `cell-4` telemetry
- real `cell-1` / `cell-4` visualization
- checkpoint-backed graph rendering
- and then richer `GRCL-v3` source work

The general lesson is:

- representative lanes prove that a family runtime exists
- real-seed evidence proves whether the family can be used honestly on the
  intended source material
- dense artifact-backed rich-seed runs prove whether the richer family-local
  semantics can carry the full reflexive trajectory rather than only isolated
  event fragments

Both are necessary, and they answer different questions.

## 3.5 Visualization Is Part Of Semantic Honesty

The `GRCV3` cycle made something else very clear:

visualization is not only presentation.
It is part of semantic verification.

That became obvious around collapse.

At first, collapse events existed but were barely legible visually.
The solution was not to invent fake activity.
The solution was to make the real state transition readable:

- fade the collapsed-from node
- highlight the sink it collapsed into
- draw explicit collapse linkage
- restore normal appearance if the node later re-enters choice

That is the right general rule:

- do not make the visualization louder than the model
- but do make the actual semantic transition unmissable

The later rich-v4 saved lane is the clearest example of why this matters.
Once the run under:

- `outputs/grcv3-rich-v4-spark-visual/grcv3-rich/seed_baseline/...`

showed not only sparks and splits but also real collapse events, the collapse
rendering stopped being a “nice-to-have polish” issue and became part of the
evidence chain itself. If the saved artifacts cannot make that transition
legible, the family is under-explained even when the runtime is correct.

## 3.6 One Good Rich-Seed Lane Can Change The Status Of A Family

Another lesson that became clear only late in the cycle:

- one honest, saved, dense rich-seed lane can materially change what can be
  claimed about a family

The rich-v4 transfer-mediation lane now provides:

- direct source semantics rather than compatibility-path interpretation
- seed-driven spark lifecycle events
- split progression
- collapse events
- saved telemetry
- saved graph checkpoints
- saved behavior and graph visualization artifacts

That means the family is no longer limited to:

- a correct baseline runtime
- representative runtime smoke
- and weaker-seed cautionary examples

It also has:

- a concrete end-to-end rich-source evidence lane

That should affect future families directly.

For later phases, the rule should be:

- once a family has one artifact-backed rich-source lane that reaches its
  characteristic nontrivial behavior honestly, record it as a milestone
  immediately
- do not leave that kind of evidence floating as an informal experiment

`GRCV3` crossed that line when the saved rich-v4 spark/collapse run landed.

## 3.7 `GRCL-v3` Became A Real Translation Program, Not Just A Probe Surface

One of the clearest late-cycle outcomes is that the `GRCL-v3` arc stopped
being only a seed-enrichment experiment.

By the time the later `transfer_mediation` and `settlement_regime` work was
done, the project had a much sharper answer to a deeper question:

- how do we give raw `GRCV3` geometry and phenomenology a truthful
  high-level language?

That work mattered because it clarified a boundary that future family source
work should keep explicit:

- a rich source language is not just a list of names for runtime outcomes
- and it is not a place to smuggle solved-state requirements back into the
  seed
- it is a source-side set of structural distinctions that can be translated
  into geometry-bearing assembly and then judged by the phenomenology that
  becomes available

The later `GRCL-v3` side-quest produced several durable language results:

- `transfer_mediation` was shown to be a real source-side family, not just a
  projector implementation detail
- `settlement_regime` became a real executable family for:
  - first productive settlement locus
  - split-child inheritance behavior
- and the last surviving descendant secondary-support condition was shown to be
  already authorable by existing `transfer_mediation` structure rather than a
  justified new `settlement_regime` field

That is important for later work because it shows the right standard for new
source semantics:

- first trace the behavior carefully
- then ask whether the distinction is already authorable by existing structure
- only after that promote a new source-side field or family

So one of the most useful `GRCV3` outcomes is not only that the runtime works.
It is that the project now has a more disciplined answer to what a
family-specific high-level language is allowed to say honestly.

## 4. Where The GRCV3 Cycle Lost Time

The lost time was not random. It came from specific boundary mistakes.

## 4.1 We Trusted The Shared Seed Surface Too Early

The project had already invested heavily in the neutral/common landscape layer.
That created a natural pressure to keep reusing it.

But `GRCV3` is exactly the kind of family where source geometry is not just
topology-plus-mass.
It also needs:

- local patch structure
- attachment intent
- branch ordering
- curvature intent
- and geometry-bearing hints that are not faithfully recoverable from a weaker
  seed once they were never expressed

The result was extra time spent proving that projector enrichment alone would
not recover what had never been specified.

That was a valuable result, but it should be remembered as a lesson:

- common source schemas are not automatically rich enough for all families

## 4.2 Compatibility Paths Can Become Too Comfortable

The compatibility/enrichment path was useful and should remain for weaker
schemas.

But once richer `grcv3.rich.v2+` semantics existed, staying on the same mental
path for too long would only have hidden drift:

- “projection” starts sounding like “realization”
- “enrichment” starts sounding like “preservation”
- and eventually the family is doing semantic invention instead of semantic
  lowering

The refactor toward family-native lowering was the correct correction.

That should be treated as a real design rule, not as cleanup.

## 4.3 We Needed Real Experiments Earlier

The right questions only appeared sharply once the project started running:

- 100-step and 150-step lanes
- checkpoint-backed graph outputs
- dense versus sparse cadence
- collapse-focused probe seeds
- and late-event inspection on saved artifacts

In other words:

- experiments were not just “nice to have after implementation”
- they were how implementation quality became visible

Future families should plan at least one real experiment lane earlier, even if
it is small.

## 5. The Landscape/Projector Lesson In One Sentence

If a family requires geometry-bearing source semantics, the project should
encode those semantics explicitly rather than hoping projector enrichment can
reconstruct them from a weaker common seed.

That is the single most important `GRCV3` lesson for later source-facing work.

## 6. What Worked Especially Well

Several decisions were clearly good and should be reused.

## 6.1 Equation Map Before Full Expansion

The explicit equation map and step-loop documentation paid off.

They gave the runtime implementation:

- a target
- a review surface
- and a way to discuss disagreement without hand-waving

Future families should again create:

- an equation map
- a canonical step-loop document
- and an early constitutive review point

## 6.2 Shared Telemetry With Family Extensions

The telemetry architecture scaled well:

- shared core rows remained shared
- family-specific information stayed explicit
- recorder logic did not need to invade the model

That is the right pattern for later families.

Do not build a second family-local telemetry stack unless the shared one is
truly impossible to extend.

The same lesson held beyond telemetry:

- the shared graph substrate remained shared
- the shared serializer remained shared
- the shared visualization stack remained shared
- while family-specific meaning stayed explicit in extension payloads and
  family-local overlays

That is the scalable pattern:

- shared infrastructure remains shared
- family-specific semantics remain explicit

## 6.3 Checkpoint-Backed Visualization

The split between:

- telemetry artifacts,
- checkpoint artifacts,
- and visualization outputs

was worth keeping, but only after the artifact roots were made run-centric and
stable.

The later shift to experiment/run-id rooted outputs was the right move because
it preserved:

- reconstruction,
- comparison,
- and visualization traceability

without depending on ad hoc file discovery.

## 6.4 Control Probes

The manual / focused probes were extremely valuable:

- pure runtime spark-capable structures
- collapse-specific seeds
- representative replay lanes
- projected-vs-native lane comparison

These should not be treated as temporary debugging scraps.
They are part of the evidence ladder.

## 7. What Future Family Work Should Copy

For `GRC9` and later families, the recommended order is now much clearer.

## 7.1 Separate The Questions Early

For each new family, explicitly split work into:

1. runtime semantics
2. source/lowering semantics
3. telemetry semantics
4. visualization semantics

Do not let those collapse into one broad “implementation” label.

## 7.2 Use A Three-Lane Evidence Ladder

The `GRCV3` cycle suggests a reusable validation ladder:

1. pure-runtime control probes
2. representative artifact-backed lane
3. real-seed / real-experiment lane

Each lane should exist explicitly and answer a different question.

Those probes should not be treated as disposable debugging scraps.
They are evidence surfaces:

- pure-runtime control probes prove the constitutive semantics exist
- representative artifact-backed lanes prove the runnable graph plus telemetry
  stack works end to end
- real-seed / real-experiment lanes prove the family is honest on the intended
  source material

## 7.3 Add Family-Native Source Semantics Earlier When Needed

If `GRC9` or later families need family-specific source geometry or mechanical
semantics, add them early and explicitly.

Do not force them through:

- `GRCV2`-shaped topology,
- or a weak neutral seed,
- just because the common layer already exists

## 7.4 Make Artifact Review Part Of Closeout

Closeout should require:

- tests
- and at least one artifact review pass

That artifact review should check:

- event rows
- summary interpretation
- graph-visible overlays if present
- and whether the saved outputs actually show the claimed phenomenon

## 7.5 Treat Visualization As A Truth Surface

If a behavior matters enough to claim in docs, it matters enough to make
legible in visualization.

This applies especially to:

- spark
- split progression
- basin formation
- choice
- collapse
- and mechanical refinement later in `GRC9`

## 8. Open Boundaries After The Retrospective

This retrospective does not claim `GRCV3` has no open work.

The remaining open work is just narrower and better identified now.

What remains open is not:

- the baseline runtime
- the telemetry surface
- or the visualization surface

What remains open is mainly:

- projector-side semantic refinement
- richer `GRCL-v3` source authoring
- deeper phenomenology search
- backend comparison work
- and later comparison against other families

What does **not** remain open in the same way is:

- another broad `transfer_mediation` sweep for the current spindle lane
- or another automatic `settlement_regime` expansion for descendant secondary
  support
- or another default collapse-family hunt for the already-audited collapse arc

Those two later `GRCL-v3` slices now have a clean current closure boundary:

- `transfer_mediation` already produced the main behavior-bearing distinctions
  it could justify for this lane
- `settlement_regime` remains useful for
  - `initial_locus_class`
  - `split_inheritance_mode`
  but does not presently justify another field for descendant secondary support
  class because that condition is already authored downstream by existing
  `transfer_mediation` structure

The same is now true for the later collapse-side search:

- Iterations 50 through 55 established plural collapse-capable lanes
- but the investigated collapse differences still closed inside existing
  authored structure
- including the stricter phenomenology question of post-collapse rerouting away
  from an initially chosen sink
- so no new collapse-side source family is presently justified
- and collapse is no longer the default next `GRCL-v3` discovery lane

So if `GRCL-v3` continues from here, the next step should be treated as an
intentional choice of a new structural family or follow-on authoring question,
not as “one more tweak” to the two slices that are now cleanly characterized.

That is a healthier kind of open work.
It means the fundamentals are no longer where the uncertainty lives.

## 9. Recommended Read Order For The Next Family

Anyone starting the next family should read these in order:

1. [Phase-4-Retrospective.md](./Phase-4-Retrospective.md)
2. [GRCV3-Retrospective.md](./GRCV3-Retrospective.md)
3. [GRCV3-Closeout.md](./GRCV3-Closeout.md)
4. [Phase-T-GRCV3-Closeout.md](./Phase-T-GRCV3-Closeout.md)
5. [Phase-V-GRCV3-RepresentativeVisualization.md](./Phase-V-GRCV3-RepresentativeVisualization.md)
6. [GRCL-V3-LoweringArchitectureDecision.md](./GRCL-V3-LoweringArchitectureDecision.md)
7. [GRCL-V3-FamilyNativeLoweringRefactorPlan.md](./GRCL-V3-FamilyNativeLoweringRefactorPlan.md)
8. [GRCL-V3-ImplementationChecklist.md](./GRCL-V3-ImplementationChecklist.md)
9. [GRCL-V3-Handoff.md](./GRCL-V3-Handoff.md)

That set captures:

- the runtime lessons
- the source/lowering lessons
- the telemetry/visualization lessons
- and the family-native seed/lowering boundary lessons
- and the clean current closure plus restart boundary for the continuing
  `GRCL-v3` arc

## 10. Final Retrospective Statement

`GRCV3` proved that the difficult part of a richer family is not only the
runtime math.

It is the full chain:

- theory
- runtime
- source semantics
- lowering
- telemetry
- visualization
- and honest experiment evidence

The good outcome is that this chain now exists and has been exercised.

That is why experiment work should not be treated as a post-implementation
extra.
For `GRCV3`, experiment quality became visible only through actual experiment
lanes:

- longer runs
- checkpoint-backed outputs
- dense versus sparse cadence
- collapse-focused probes
- and direct inspection of saved event rows

The main thing to preserve from this work is not a single algorithm.
It is the discipline of keeping those layers separate enough that each one can
be corrected without confusing the others.

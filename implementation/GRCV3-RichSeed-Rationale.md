# GRCV3 Rich Seed Rationale

## Purpose

This note explains why the Phase 5 landscape-projector follow-on stops after
the Iteration 8 diagnostic gate and does **not** proceed directly to the
Iteration 9 representative rerun.

The short version is:

- `GRCV3` spark machinery is executable,
- richer neutral/common `GRCL` projection improves geometry somewhat,
- but richer neutral/common projection still does **not** preserve or generate
  the geometry required for spark formation reliably,
- therefore the next justified step is a **GRCV3-rich seed extension surface**
  rather than further neutral projector patching alone.

## 1. What We Needed To Distinguish

There were two competing hypotheses:

1. the current `GRCL -> GRCV3` projector is simply too coarse
2. `GRCV3` requires geometry-bearing source information that the current
   family-neutral `GRCL` cannot express

The projector follow-on was designed to test hypothesis 1 first, because that
is the cleaner explanation and preserves the shared seed layer if successful.

## 2. What Was Confirmed

### 2.1 Manual GRCV3 Spark States Work

Using direct `GRCV3.from_state(...)` probes, we confirmed that the runtime
spark/split path itself is functional.

Evidence:

- a single-node manual state with:
  - zero gradient
  - weak signed curvature on one axis
  - strong positive curvature on the orthogonal axis
  produces:
  - `spark_candidate`
  - `split_init`
  - `spark`
  - deterministic split progression

- a three-node manual state with stricter confirmation requirements produces:
  - `spark_candidate`
  - `split_init`
  - `spark_pending`

Implication:

- the failure of seed-driven `cell-4` is **not** because the `GRCV3` spark path
  is broken or unreachable in principle

## 3. What The Revised Projector Achieved

The projector revision added:

- basin core patches
- valley channel chains
- routing junction motifs
- explicit ridge support arcs

This materially enriched the realized runtime surface.

For `cell-4`, the projector now creates:

- a larger realized graph
- a real junction-center stencil
- one genuine pre-spark geometric seed at the routing center

That is important:

- the old projector produced an empty geometric seed layer
- the revised projector produced a non-empty pre-spark seed layer

So the projector work was not wasted. It identified the actual remaining gap.

## 4. What Still Failed

### 4.1 `cell-4` Still Does Not Reach Spark

Under both:

- `seed_baseline`
- `balanced_baseline`

the revised projected `cell-4` still yields:

- pre-spark geometric seed count: non-empty only in the explicit pre-spark
  diagnostic
- pre-spark spark candidate count: `0`
- runtime steps `1..100`:
  - `geometric_seed_count = 0`
  - `spark_event_count = 0`
  - `candidate_count = 0`

Reason:

- the new routing-center seed is geometrically **stable**, not near-degenerate
- its weakest signed curvature remains far above `eps_spark`
- so the projector creates a usable interior point, but not a sparkable one

### 4.2 A Richer Neutral/Common Probe Also Fails

We then constructed a richer but still family-neutral/common seed:

- `configs/landscapes/seed/spark-probe-cross.seed.yaml`

Intent:

- create a low-gradient central routing site
- create explicit four-branch anisotropy
- keep the seed within the current neutral/common `GRCL` surface

Result under projected `GRCV3`:

- no geometric seeds
- no spark candidates
- no spark events over `100` steps

Most revealingly:

- the projected `decision_core` center had `grad = 0`
- but `eig = []`

That means the richer neutral topology still did not preserve or induce the
local differential structure that `GRCV3` spark detection actually requires.

## 5. Why This Matters

This gives a stronger conclusion than “the projector still needs tuning.”

What the evidence now says is:

- manual `GRCV3` spark states can be built
- current neutral/common seeds can be made richer
- but richer neutral/common seeds still do not map cleanly onto those sparkable
  `GRCV3` local states

So the limiting factor is no longer just graph richness.
The limiting factor is **geometry-bearing source expressivity**.

## 6. Exact Conclusion

Current family-neutral/common `GRCL` is sufficient for:

- shared semantic landscape description
- cross-family structural initialization
- `GRCV2`-class execution
- basic `GRCV3` landscape realization

Current family-neutral/common `GRCL` is **not sufficient** for:

- expressing the local geometry required by `GRCV3` spark formation
- or guaranteeing that projector synthesis will reconstruct that geometry from
  neutral primitives alone

Therefore:

- the next correct move is **not** Iteration 9 representative rerun
- the next correct move is a **GRCV3-rich seed extension**

## 7. What A GRCV3-Rich Seed Must Do

The extension should be minimal and explicit.
It should not replace the common seed layer.

Its job is to preserve the information that neutral/common projection currently
loses, especially:

- local geometry-bearing motif structure
- branch-interface semantics that are not only topological
- local differential intent relevant to weak-axis formation
- interior-probe versus through-routing intent
- support-spacing / confinement asymmetry that can make one axis weak without
  prescribing the solved Hessian
- attachment-isolation intent so channels and boundaries do not destroy the
  intended low-gradient interior site during lowering
- any constitutive hints needed so the projector acts as a preserver/lowerer
  rather than a heuristic synthesizer

In other words:

- common `GRCL` remains the semantic substrate
- `GRCV3`-rich seed content becomes the geometry-sensitive refinement layer

## 8. Consequence For Phase 5

Phase 5 landscape-projector follow-on should be considered complete through the
diagnostic boundary established by Iteration 8.

Iteration 9 is intentionally not executed yet because the gate condition did not
pass honestly.

That is not an implementation failure.
It is a successful falsification result:

- “richer neutral/common projector realization alone is enough” is not supported
  by the evidence

## 9. Recommended Next Step

Create a small `GRCV3`-rich seed design note and one minimal spark-probe seed
that uses it.

That next step should answer the real remaining question:

- whether explicit geometry-bearing seed structure can preserve the manual spark
  topology in a shareable, documentable seed format

That implementation lane is now planned in:

- [GRCL-V3-ImplementationPlan.md](./GRCL-V3-ImplementationPlan.md)

## 10. Later Basin-Centered Weak-Axis Probe Result

A later follow-on probe refined this diagnosis further using:

- `configs/landscapes/seed/grcv3-rich-weak-axis-basin-spark-probe.seed.yaml`

This probe changed one important thing:

- the intended weak-axis site was lowered as a basin-centered interior patch
  rather than as a two-branch junction center

Observed outcome under both:

- `seed_baseline`
- `hot_exploratory`

The result was:

- a real interior geometric seed at the `spindle_core` basin center
- `geometric_seed_count = 1`
- `validated_basin_ids = [spindle_core_center_node]`
- but still:
  - `spark_candidates = 0`
  - `spark_event_count = 0`

Why this matters:

- the source/lowering path can now construct a truthful low-gradient interior
  seed
- but the resulting signed-Hessian spectrum at that center is still strongly
  stable on both axes rather than weak on one axis

So the diagnosis is now narrower than before.

The remaining missing source-side ingredient is no longer merely:

- “how do we create an interior seed at all?”

It is now closer to:

- “how do we express enough constructive support-spacing / confinement
  asymmetry that one axis can emerge near-degenerate while the orthogonal axis
  remains stabilizing?”

## 11. `grcv3.rich.v3` Direct-Assembly Gate Result

The next follow-on tested exactly that question using:

- `configs/landscapes/seed/grcv3-rich-v3-interior-spindle-probe.seed.yaml`

This was the first probe to use:

- typed `interior_geometry`
- family-native direct assembly
- role-indexed support spacing
- support-only attachment
- spindle-style support connectivity

The result under the baseline gate envelope:

- `profile_name = seed_baseline`
- default `GRCV3` thresholds
- `num_steps = 50`

was still:

- `spark_candidate_events = 0`
- `spark_events = 0`

But the failure mode changed in an important way.

Compared with the earlier basin-centered `rich.v2` probe:

- `rich.v2` kept a truthful low-gradient interior seed
- but its signed Hessian stayed strongly stable on both axes

The `rich.v3` direct-assembly probe instead produced:

- a center Hessian very close to degeneracy
- but no validated geometric seed

In other words:

- `rich.v2` solved the low-gradient part but not the weak-axis part
- `rich.v3` began to solve the weak-axis part but lost the low-gradient center

That is a better result than “nothing changed,” because it narrows the missing
constructive ingredient further.

The next missing source-side requirement is now closer to:

- explicit separation between interior probe shielding and support-surface load
  routing

Practically, that suggests a future `GRCL-v3` slice stronger than the current
first `interior_geometry` implementation, likely something like:

- a two-tier interior construction
- inner probe versus outer load-bearing support layers
- or equivalent load-partition semantics that can keep the center
  low-gradient while still preserving a usable weak-axis stencil

So the direct-assembly result is an honest near-miss, not a regression:

- the richer source semantics changed the realized geometry materially
- but the current first `rich.v3` slice is still not sufficient to generate a
  sparkable weak-axis seed by itself

## 12. First `interior_partition` Gate Result

The next follow-on tested whether an explicit inner-probe / outer-load split
was already enough to close that remaining gap. The probe used:

- `configs/landscapes/seed/grcv3-rich-v3-partitioned-spindle-probe.seed.yaml`

This kept the same broad spindle-core intent as the first `rich.v3` direct
assembly probe, but added:

- `interior_partition.partition_mode = two_tier_probe_shell`
- an explicit outer load shell covering the declared role universe
- explicit probe-to-load transfer edges
- attachment resolution through the outer shell rather than through the inner
  probe shell

The first runtime meaning of that field was intentionally narrow:

- inner support nodes remain the probe shell and weak-axis stencil
- outer load nodes become the attachment-facing shell
- transfer edges mediate load from outer shell back to the probe shell

Under the same gate envelope:

- `profile_name = seed_baseline`
- default `GRCV3` thresholds
- `num_steps = 50`

the outcome was still:

- `geometric_seed_count = 0`
- `geometric_validated_basin_count = 0`
- `spark_candidate_events = 0`
- `spark_events = 0`

Compared with the earlier probes:

- `rich.v2` weak-axis basin probe still remains the only one of the three that
  produces a validated geometric seed
- first `rich.v3` direct assembly preserved near-degenerate center Hessian
  behavior but left the center gradient-loaded
- partitioned `rich.v3` also leaves the center gradient-loaded

The important lesson is that “two shells” alone is still not enough when the
outer shell remains role-aligned with the probe stencil.

The next missing constructive requirement is therefore narrower than “more
detail in general.” It is closer to:

- explicit non-coincident load-carrier placement
- or explicit transfer-topology semantics that let attachment load enter the
  outer shell without projecting straight back onto the same role-aligned
  probe nodes

That means the next justified source-side move is not runtime compensation. It
is a richer constructive field that controls how load-bearing carriers sit
relative to the interior probe stencil.

## 13. First `interior_load_carriers` Gate Result

The next follow-on tested whether explicit non-coincident carrier placement was
already enough to break that remaining coupling. The probe used:

- `configs/landscapes/seed/grcv3-rich-v3-load-carrier-spindle-probe.seed.yaml`

This extended the partitioned spindle probe with:

- explicit load-carrier realization semantics
- non-coincident attachment-facing carrier nodes
- explicit `transfer_role_pairs`
- explicit carrier attachment roles

The first runtime meaning of that field was intentionally narrow:

- the probe shell remains the local weak-axis stencil
- the outer attachment-facing nodes become carrier nodes rather than
  role-aligned load-shell nodes
- carrier-to-probe influence is mediated through explicit role pairs

Under the same gate envelope:

- `profile_name = seed_baseline`
- default `GRCV3` thresholds
- `num_steps = 50`

the outcome was still:

- `geometric_seed_count = 0`
- `geometric_validated_basin_count = 0`
- `spark_candidate_events = 0`
- `spark_events = 0`

Compared with the earlier probes:

- `rich.v2` weak-axis basin probe still remains the only source-side probe in
  this line that produces a validated geometric seed
- first `rich.v3` direct assembly moved the Hessian close to degeneracy but
  lost the low-gradient center
- partitioned `rich.v3` still left the center gradient-loaded
- load-carrier `rich.v3` remained effectively the same near-miss as the
  partitioned probe under the first executable semantics

This is useful because it rules out one more overly optimistic diagnosis.

The remaining blockage is no longer merely:

- “we need non-coincident attachment-facing nodes”

because those nodes now exist.

It is now closer to:

- “the transfer path from carrier layer back to probe shell is still too
  identity-preserving, so the effective load pattern collapses back onto the
  same role-indexed probe coupling”

That points to the next source-side need more precisely:

- stronger expressive control over carrier-to-probe remapping
- or stronger expressive control over transfer weighting/topology

So the first `interior_load_carriers` slice is another honest near-miss:

- it improved source/runtime honesty
- it changed the realized outer attachment layer materially
- but it still did not cross the spark gate

## 14. Exploratory Softness Sweep Around The Load-Carrier Probe

After the first `interior_load_carriers` near-miss, the next natural question
was:

- is the source geometry simply too strict?

To test that, a small diagnostic sweep was added:

- `scripts/sweep_grcv3_load_carrier_softness.py`

The sweep kept the same seed family:

- `grcv3-rich-v3-load-carrier-spindle-probe.seed.yaml`

and varied only a few local “softness” knobs:

- support-profile sharpness
- interior-clearance class
- carrier layout mode
- carrier-to-probe transfer topology

The key outcome was:

- geometry softening by itself changed little
- carrier layout mode also changed little under the current first executable
  assembly meaning
- but transfer remapping mattered much more than the other tested knobs

Most importantly, the `weak_to_stable_bridge` transfer preset produced:

- center gradient norm around `5.40e-01`
- signed eigenvalues around:
  - weak axis: `-1.22e-04`
  - stable axis: `6.07e-04`

compared with the baseline load-carrier identity bridge:

- center gradient norm around `5.72e-01`
- signed eigenvalues around:
  - weak axis: `-3.59e-07`
  - stable axis: `1.78e-06`

So the exploratory sweep taught something precise:

- the stable signed-Hessian axis can be moved much closer to the required
  `1e-3` threshold by changing transfer semantics
- but the center gradient barely improves and remains hundreds of times above
  the `1e-3` gradient threshold

That shifts the diagnosis again.

The problem is no longer simply:

- “make the stable Hessian axis larger”

because one family of source-side tweaks already moves in that direction.

It is now more clearly:

- “how do we preserve that Hessian improvement while collapsing the center
  gradient by orders of magnitude?”

So the current evidence suggests:

- source geometry may indeed be somewhat too strict
- but the dominant remaining blocker is still the center gradient regime, not
  the signed-Hessian weak-axis pattern alone

## 15. Narrow Transfer-Remap Sweep Around The Best Current Near-Miss

The exploratory softness sweep showed that transfer semantics mattered much more
than either geometry softening or carrier-layout variation. That raised the
next sharper question:

- is there still useful room to search inside the current transfer-remap
  surface, or has the current `rich.v3` slice already reached a local ceiling?

To answer that, a narrower follow-on sweep was added:

- `scripts/sweep_grcv3_transfer_gradient.py`

anchored on a dedicated best-current probe fixture:

- `configs/landscapes/seed/grcv3-rich-v3-load-carrier-weak-to-stable-probe.seed.yaml`

This second sweep intentionally held the geometry fixed and varied only the
carrier-to-probe transfer remap around the same load-carrier construction.

The tested transfer families were:

- identity-group bridge
- weak-to-stable bridge
- stable-to-weak bridge
- cross-swap bridge

Under the same gate envelope:

- `profile_name = seed_baseline`
- default `GRCV3` thresholds
- `num_steps = 50`

the result was clearer than the broader softness sweep.

The identity bridge remained distinctly worse:

- center gradient norm around `5.72e-01`
- signed eigenvalues around:
  - weak axis: `-3.59e-07`
  - stable axis: `1.78e-06`

But every tested non-identity remap converged to almost the same improved
regime:

- center gradient norm around `5.40e-01`
- signed eigenvalues around:
  - weak axis: `-1.22e-04`
  - stable axis: `6.07e-04`

and still:

- `geometric_seed_count = 0`
- `geometric_validated_basin_count = 0`
- `spark_candidate_events = 0`
- `spark_events = 0`

This matters because it separates two questions cleanly.

The first question was:

- does transfer remapping matter at all?

The answer is now clearly yes.

The second question was:

- is the current `rich.v3` transfer surface still wide enough that a better
  remap alone is likely to cross the spark gate?

The current evidence says probably not.

Within the present runtime meaning, different non-identity remaps all fall into
nearly the same center-gradient regime. That suggests the current source-side
surface is approaching an expressive ceiling:

- transfer remapping can improve the Hessian materially
- but it does not yet collapse the center gradient by the orders of magnitude
  still required for geometric validation

So the best current interpretation is not:

- “keep searching transfer permutations until one happens to spark”

It is closer to:

- “the current `rich.v3` transfer language already captures the first real
  degree of freedom, and the next missing degree of freedom is something
  stronger than simple remapping”

That points directly toward the next justified rich-source need:

- richer transfer mediation semantics
- explicit transfer weighting / attenuation / confinement
- or another equally direct source-side way to reduce center load ingress
  without injecting solved Hessians

So this second sweep does not close the spark gate either, but it improves the
diagnosis materially.

It shows that:

- the current `rich.v3` surface is no longer failing only because of obviously
  bad topology
- the remaining blockage is now concentrated in how load transfer reaches and
  perturbs the intended low-gradient interior site

## 16. First `rich.v4` Transfer-Mediation Gate Result

The first `rich.v4` lane tested whether that remaining blockage could be
addressed honestly without reopening projector-style interpretation.

The probe used:

- `configs/landscapes/seed/grcv3-rich-v4-transfer-mediation-probe.seed.yaml`

and the first executable semantics were intentionally narrow:

- explicit mediation classes over already-declared `transfer_role_pairs`
- guarded center ingress through reduced probe-to-center coupling on impacted
  probe roles
- explicit lateral spill structure derived directly from the declared
  `lateral_spill_policy`

This remained theory-facing and source-side:

- no solved `w_ij`
- no solved `Phi_i`
- no solved `J_ij`
- no runtime-state injection

Under the same baseline gate envelope:

- `profile_name = seed_baseline`
- default `GRCV3` thresholds
- `num_steps = 50`

the comparison against the best current `rich.v3` near-miss changed the
outcome qualitatively.

Baseline `rich.v3` weak-to-stable near-miss:

- `configs/landscapes/seed/grcv3-rich-v3-load-carrier-weak-to-stable-probe.seed.yaml`
- final observables:
  - `geometric_seed_count = 0`
  - `geometric_validated_basin_count = 0`
  - `spark_event_count = 0`
- event counts:
  - none

First `rich.v4` transfer-mediation probe:

- `configs/landscapes/seed/grcv3-rich-v4-transfer-mediation-probe.seed.yaml`
- final observables:
  - `geometric_seed_count = 0`
  - `geometric_validated_basin_count = 0`
  - `spark_event_count = 0`
- but lifecycle events now include:
  - `spark_candidate = 2`
  - `spark = 2`
  - `split_init = 2`
  - `split_progress = 4`
  - `split_complete = 2`

This is important because it shows the first `rich.v4` slice did not merely
change the same near-miss numerically. It crossed the behavioral boundary:

- the same source family now produces real seed-driven spark lifecycle events
  under the baseline gate

That means the current diagnosis has shifted again.

The remaining problem is no longer:

- “can direct source semantics break the `rich.v3` plateau at all?”

The answer to that is now yes.

The next question becomes narrower:

- whether later `rich.v4` work is needed to stabilize geometric validation
  earlier in the trajectory
- or whether the runtime/observability side simply needs a better lens on the
  transient seed-to-spark path already being realized

So the first `rich.v4` gate should be treated as a real pass, with one
important caution:

- it is a pass at the spark-lifecycle boundary
- not yet a claim that the entire geometric-validation surface is fully solved

## 17. First `rich.v4` Pass Closure Boundary

The correct closure after the first `rich.v4` gate is now narrower and more
useful than either of the two easy misreadings:

- it is **not** “`GRCV3` rich seeds are fully solved”
- and it is **not** “this is still only a theoretical probe”

What is now closed:

- `grcv3.rich.v4` is a real direct-translation lane, not merely a vocabulary
  proposal
- direct source semantics are sufficient to reach real spark lifecycle events
  under the normal `GRCV3` runtime loop
- the project no longer needs to justify `rich.v4` at the behavioral
  reachability level

What is still open:

- how the interior regime moves along the transient path before
  `spark_candidate` / `spark` onset
- why explicit geometric validation remains weak or late relative to the
  observed spark lifecycle
- whether any later source-side broadening is still needed inside
  `transfer_mediation` once that transient path is made observable enough

This means the next justified step is **not**:

- “add full `rich.v4` content”
- or “open another semantic family because sparks now exist”

The next justified step is:

- observability first
- then, only if the evidence still points there, controlled broadening inside
  `primitive.extensions.grcv3.transfer_mediation`

So the first `rich.v4` pass should be treated as a real closure boundary:

- behavioral reachability is proven
- semantic growth is no longer justified by lack of sparks
- any further growth must now be justified by residual evidence about the
  transient seed-to-spark path

## 18. First Seed-To-Spark Observability Lift

After that closure boundary, the next justified question was no longer:

- “can the direct rich-v4 lane spark at all?”

It became:

- “what interior regime is actually being traversed before those spark events?”

That required an observability lift, not another source-language expansion.

The recorded contract decision is:

- graph checkpoints should keep exporting raw node state
  (`gradient`, `gradient_norm`, `hessian`, `net_flux`)
- but they also need a deterministic pointer to the monitored interior site
- step telemetry should carry a compressed transient summary for that monitored
  site
- run summaries should carry the first event-aligned snapshots plus a compact
  trajectory rollup

So the observability split is now:

1. runtime artifact metadata:
   - monitoring surface kind
   - monitored node ids by primitive id
2. telemetry summaries:
   - per-step observed interior metrics
   - run-level event-aligned and trajectory summaries
3. later visualization:
   - should render from those summaries first
   - and use graph checkpoints only when graph-visible detail is required

One important interpretation rule had to be made explicit:

- the runtime “weak axis” should be reported as the **minimum signed-Hessian
  eigenvalue**, because that is the operational weak mode actually used by
  spark detection
- it should **not** pretend that a source role label is automatically the same
  thing as the runtime eigenbasis

The first real readout on:

- `configs/landscapes/seed/grcv3-rich-v4-transfer-mediation-probe.seed.yaml`
- `profile_name = seed_baseline`
- `num_steps = 50`

now gives a much clearer picture.

The monitored surface is:

- `transfer_mediation`

The monitored interior site is:

- `spindle_core -> node 16`

The first event-aligned observations occur at:

- `spark_candidate` step `6`
- `spark` step `6`
- `split_init` step `6`
- `split_complete` step `7`

And the monitored-center trajectory summary is currently:

- initial gradient norm: about `4.63e-01`
- minimum gradient norm over the run: about `4.63e-01`
- final gradient norm: about `5.42e-01`

This is exactly why Iteration 26 matters.

Before this lift, the project could only say:

- “the seed sparks”

Now it can say something much more precise:

- the first `rich.v4` spark lane is real
- but it is not presently a story where the monitored center first settles into
  a low-gradient regime and then sparks

That does **not** invalidate the spark pass.
It sharpens the next design question.

The remaining issue is now closer to:

- whether later direct source semantics should reduce the monitored-center load
  regime itself
- or whether sparkability here is already being mediated through another
  transient structural route that the new observability surface now makes
  inspectable

## 19. Controlled `transfer_mediation` Broadening

The first justified broadening after that observability lift stayed strictly
inside:

- `primitive.extensions.grcv3.transfer_mediation`

The added field was:

- `center_coupling_classes`

Its meaning is intentionally narrow:

- refine whether already-mediated ingress may still couple through the semantic
  center spoke for a declared probe role
- without moving carrier placement
- without inventing new transfer pairs
- and without prescribing solved conductance, potential, flux, or Hessian data

That broadening was justified by the Iteration 26 readout itself:

- the monitored center stayed gradient-loaded
- the residual looked ingress-specific rather than like a new geometry-family
  gap

The follow-on probe result is useful precisely because it is mixed rather than
universally “better”.

Baseline `rich.v4` transfer mediation probe:

- spark lifecycle events were present under the baseline gate
- monitored center gradient stayed around `4.63e-01` initially and at its
  minimum

Blocked stable-axis center coupling probe:

- reduced the monitored center gradient to about:
  - `4.26e-01` initially
  - `4.22e-01` at its minimum over the same run horizon
- but it also suppressed spark candidates and sparks entirely

Weaker stable-axis center coupling:

- did not improve the center regime meaningfully
- and also suppressed the spark path

So the conclusion is not “less center coupling is the answer.”
The conclusion is:

- the remaining gap really is sensitive to ingress mediation
- `center_coupling_classes` is a valid direct semantic degree of freedom
- but the field is explanatory, not yet a new default recipe

## 20. `rich.v4` Breadth Decision

At this point the right classification is no longer ambiguous.

`grcv3.rich.v4` should now be treated as:

- a **real** direct-translation lane
- a **stable narrow** family-level authoring surface
- and **not yet** a fully general-purpose `GRCV3` rich authoring language

Why it is no longer only a probe family:

- it already crossed the behavioral reachability bar:
  - seed-driven spark lifecycle events exist under the normal baseline gate
- it crossed the architecture bar:
  - direct source semantics, not compatibility-path interpretation, are the
    authority
- it crossed the observability bar:
  - the transient path is inspectable through telemetry/checkpoint summaries
- it crossed the controlled-broadening bar:
  - one additional field inside `transfer_mediation`
    (`center_coupling_classes`) was added without reopening unrelated semantic
    families or leaking solved-state semantics

Why it is still not “full rich GRCV3”:

- the successful lane is still concentrated around a specific interior
  mediation problem
- geometric validation remains weaker or later than ideal relative to spark
  onset
- the new broadening proved that more control can just as easily over-guard the
  lane as improve it

So the correct planning posture is:

- do **not** demote `rich.v4` back to “just a temporary probe”
- do **not** promote it to “general-purpose family-complete language”
- do treat it as a stable narrow authoring family whose next growth, if any,
  must still be justified by evidence from the already-visible transient path

That gives the project a much cleaner next-step rule:

- later work may stay inside `transfer_mediation` for one more cycle if the
  evidence continues to localize the remaining issue there
- otherwise the next semantic family should be opened only intentionally and
  with the same direct-translation discipline

## 21. What The Next `rich.v4` Step Should Actually Be

The next step should not be:

- “add more rich.v4 fields because the lane now works”

The right next step is stricter:

1. treat the saved rich-v4 spark/split/collapse run as the baseline evidence
   lane
2. use that lane as the comparison target for any later candidate
3. only then decide whether another direct semantic move is justified

In practice that means:

- the current saved lane under:
  - `outputs/grcv3-rich-v4-spark-visual/grcv3-rich/seed_baseline/...`
  should now be treated as the stable reference artifact for rich-v4
- future candidate changes should be asked to improve something specific
  against that lane, not against an abstract desire for “more expressivity”

If `rich.v4` grows again, the preferred order should be:

- first, only one more `transfer_mediation` cycle if the observed residual is
  still clearly ingress-structure-localized
- otherwise, open the next direct semantic family intentionally and name the
  new missing source-side meaning explicitly before coding

What should be rejected at this point:

- projector-style reinterpretation of already-explicit rich-v4 seeds
- generic geometry-profile widening without a new evidence-backed semantic gap
- constitutive/runtime tuning offered as a substitute for source-side meaning

So the family is no longer waiting for “more ideas”.
It is waiting for the next evidence-backed semantic claim.

## 22. Likely Next Candidate, But Not A New Family Yet

One concrete post-28 proposal that deserves to be recorded is:

- the remaining gap may involve not only which mediated ingress routes exist,
  and not only whether center spokes participate,
  but also the **assembled path structure** between carrier layer and probe
  shell

That diagnosis is plausible because the current `rich.v4` surface already
controls:

- transfer pair coverage
- guard/spill structure
- center-spoke participation

but does **not** yet explicitly describe the path shape of those mediated
routes.

The important boundary decision is:

- this should **not** be recorded yet as a separate semantic family with an
  effect-oriented name such as `interior_spoke_compliance`

Why not:

- names like `compliance`, `flexible`, or `damping` are too
  phenomenological/effect-facing
- they describe hoped-for behavior rather than direct source structure
- and the currently observed residual still looks like one more
  `transfer_mediation` problem, not yet a clearly distinct semantic family

So the cleaner next candidate, if the evidence later justifies another cycle,
is:

- stay inside `primitive.extensions.grcv3.transfer_mediation`
- open a structural slice around **carrier-to-probe path structure**

The preferred vocabulary should therefore stay structural:

- `path_roles`
- `path_mode`
- `path_topology`

with direct assembly-facing values such as:

- `direct`
- `single_intermediate`
- `double_intermediate`
- `fan_in`
- `buffered_chain`

The rule should be:

- if this slice remains small and clearly ingress-local, keep it under
  `transfer_mediation`
- only if it grows into something semantically broader should it later be
  promoted into its own direct semantic family

That keeps the next step from getting lost in memory while preserving the
post-28 discipline:

- evidence first
- structure before effect-language
- and no premature family splitting

# Phase 4 Retrospective

This document records the retrospective on Phase 4 development of `GRCV2`.

It focuses on:

- where the implementation went smoothly,
- where mathematical fidelity drifted,
- why some paper details were temporarily lost,
- what process gaps allowed that drift,
- and what should change before or during `GRCV3` so Phase 5 runs more cleanly.

This is not a blame document. It is a process and architecture correction note.

## 1. What Phase 4 Achieved Well

Phase 4 succeeded on several important fronts:

- `GRCV2` became the first full executable family.
- The shared contracts, graph substrate, and persistence path held up under a
  real model implementation.
- Determinism was treated as a first-class concern:
  - stable IDs,
  - canonical snapshots,
  - replayable RNG state,
  - repeatable smoke tests.
- The explicit 14-step loop gave the implementation a structure that could be
  tested and reasoned about.
- The later paper-alignment remediation succeeded in closing the major
  constitutive gaps without breaking the rest of the system.

That means the underlying architecture was strong enough to support correction.

## 2. What Went Wrong

The main issue was not that the code became non-functional. The main issue was
that the implementation temporarily drifted from the paper in several central
mathematical places while still appearing “done” from a purely engineering
perspective.

The drift showed up in:

- the tensor path,
- the conductance law,
- abundance semantics,
- birth semantics,
- curvature backend fidelity,
- and earlier, sink semantics.

In other words:

- the loop existed,
- the tests passed,
- the model ran,
- but the constitutive interpretation was not yet trustworthy enough.

That is exactly the kind of problem a later family lift would inherit if not
caught.

## 3. Why The Math Details Were Temporarily Lost

Several causes contributed.

## 3.1 Execution-First Momentum

Once the executable step skeleton existed, development naturally optimized for:

- getting the next stage running,
- preserving determinism,
- keeping tests green,
- and closing checklist iterations.

That made it easy to substitute:

- a mathematically plausible local surrogate,

for:

- the exact paper-facing constitutive object.

This happened most clearly in:

- `_compute_geometry(...)`
- `_compute_metric(...)`
- `_apply_front_birth(...)`

The implementation pressure favored:

- “make the loop real first”

before:

- “make the realized law exactly match the paper”.

That is an understandable development pattern, but it is dangerous when the
first executable family becomes the inherited baseline for later work.

## 3.2 The Paper Was Present, But Not Mapped Into Code Early Enough

We had:

- the paper,
- the spec,
- and the implementation plan.

But early Phase 4 did not yet have an explicit per-equation implementation map
that forced the team to answer questions like:

- where is Eq. (1) in code?
- where is Eq. (2) in code?
- where does `lambda_c` enter?
- where does `xi_c` enter?
- where does `zeta_c` enter?
- where is the Bernoulli birth law represented?

Without that map, it was too easy for:

- a heuristic to look “close enough”,
- or a parameter to exist in validation but not in its true constitutive role.

The code had structure, but it did not yet have equation traceability.

## 3.3 Tests Initially Followed Implementation More Than Theory

The early tests were strong on:

- executability,
- deterministic behavior,
- serialization,
- API correctness,
- and local invariants.

They were weaker on:

- direct paper-to-code equivalence checks.

This created the classic risk:

- tests verified the implemented behavior,
- not necessarily the intended mathematical behavior.

That is why a stale implementation could still have a passing suite.

Only when stronger paper-facing smokes and validation-gate review were added did
the remaining constitutive gaps become impossible to ignore.

## 3.4 Placeholder Semantics Were Temporarily Too Comfortable

Some temporary simplifications were reasonable during the first executable pass:

- surrogate curvature,
- deterministic birth threshold,
- simplified local tensor summaries.

The problem was not their temporary existence.

The problem was that they were close enough to the intended math to create
false confidence unless they were kept aggressively labeled as placeholders.

In practice, placeholder logic is dangerous when:

- the public backend name sounds final,
- the config surface looks complete,
- and the code is already executable and tested.

At that point, “temporary” can start acting like “canonical”.

## 3.5 Too Much Variation Logic Stayed Inline In One Model Class

`GRCV2` now works, but much of the variation logic still lives inside one large
model class.

That made it easy to:

- add branches,
- add surrogate logic,
- and keep moving.

But it made it harder to see:

- which pieces were foundational,
- which were family baselines,
- which were backend variants,
- and which were temporary stand-ins.

This matters because backend and constitutive drift are easier to hide inside
large inline methods than inside explicit backend modules or equation-mapped
subsystems.

## 4. Where The Implementation Gaps Were

The Phase 4 validation gate identified the most important gaps explicitly.

## 4.1 Eq. (1) Tensor Gap

The node tensor was not initially treated as the real constitutive geometry
object.

Instead, the implementation first stored local summaries that were useful for
running the loop but not faithful enough to the paper's tensor story.

### Lesson

If the paper names a constitutive object directly, the implementation should not
replace it with an unlabeled summary object unless that summary is explicitly
documented as a reduction of the same object.

## 4.2 Eq. (2) Conductance Gap

The conductance law initially drifted into a hybrid heuristic rather than the
paper's exponential law.

That was especially risky because conductance sits at the center of:

- geometry,
- flux,
- basin behavior,
- and event timing.

### Lesson

Any formula that drives the full loop should be treated as a high-risk fidelity
surface and tested directly against the paper as soon as it is implemented.

## 4.3 Parameter-Semantics Drift

`lambda_c`, `xi_c`, and `zeta_c` existed in the parameter contract before they
existed in their correct mathematical roles.

This is one of the most dangerous implementation smells in theory-driven code:

- a parameter is present,
- tests pass,
- but the semantic role is wrong.

### Lesson

Parameter presence is not enough. Each named parameter must have a traceable
equation role.

## 4.4 Observable-Naming Drift

`abundance` temporarily meant total coherence mass instead of sink/basin count.

This is not just a cosmetic problem. It changes the semantics of the published
observable surface.

### Lesson

When a paper gives a quantity a canonical name, the implementation should either:

- preserve that meaning,
- or rename the implementation quantity explicitly.

Never silently overload the paper's term.

## 4.5 Stochastic-Semantics Drift

Birth was simplified into a threshold rule before the Bernoulli law and RNG
replay were restored.

This was understandable as a first-pass simplification, but it shows an
important process issue:

- stochastic semantics should not be “made deterministic” by changing the law,
- they should be made reproducible by controlling the RNG.

### Lesson

Use seeded/stored randomness, not deterministic substitutes, when the paper's
law is genuinely probabilistic.

## 4.6 Backend-Naming Drift

Backend names like:

- `forman`
- `ollivier`

were exposed before their implementations were fully paper-worthy.

That created a mismatch between:

- what the public interface suggested,
- and what the code actually did.

### Lesson

Do not publish final-looking backend names for placeholder implementations unless
the placeholder status remains explicit in:

- code,
- specs,
- plan,
- and tests.

Better yet, avoid placeholder publication when the named backend can be closed in
the current phase.

## 5. What Helped Recover The Correct Baseline

Several decisions were especially useful in getting Phase 4 back onto the right
track.

## 5.1 The Validation Gate

The dedicated validation gate was the turning point.

It forced the project to answer:

- what is structurally done,
- what is mathematically done,
- what is still a blocker,
- and whether the family is actually ready to become the inherited baseline.

Without that gate, the project could easily have declared success too early.

## 5.2 Paper-Facing Smoke Tests

The stronger smokes were not redundant with the unit suite.

They did two crucial things:

- exposed a real stability bug,
- and forced the implementation to justify itself at the loop-and-paper level.

### Lesson

Model-family development needs:

- unit tests,
- deterministic scenario tests,
- and paper-facing smoke tests.

All three are necessary.

## 5.3 Explicit Remediation Iteration

Turning the remediation into its own iteration was the right process move.

It prevented:

- paper corrections from becoming vague future work,
- and it made closeout conditional on actual constitutive repair.

### Lesson

When a baseline family is intended to seed later families, constitutive
misalignment should get its own remediation stage, not a footnote.

## 6. What `GRCV3` Should Do Differently

Phase 5 should not repeat the same process shape blindly.

## 6.1 Start With A Paper-To-Code Equation Map

Before substantial `GRCV3` coding starts, create a document that maps:

- each important paper equation or semantic object,
- to the intended code location,
- to the parameters it depends on,
- to the tests that will verify it.

Representative questions:

- where is the gradient backend defined?
- where is the Hessian backend defined?
- where is the Hessian sign fixed?
- where are basin attributes materialized?
- where is attractor-count change represented?
- where is hierarchy tracking updated?

This should exist before the implementation becomes large.

## 6.2 Separate Backend Categories Early

`GRCV3` should adopt the backend-selection architecture early rather than keeping
all alternatives inline inside `grc_v3.py`.

Likely categories:

- `geometry`
- `differential_summary`
- `spark`
- `metric`
- possibly `hierarchy_update`

The common strategy plan already records this direction:

- [`Common-BackendStrategyPlan.md`](./Common-BackendStrategyPlan.md)

### Lesson

Do not wait until the model is large to extract backend variation points.

## 6.3 Add Theory Tests Earlier

For `GRCV3`, theory-facing tests should land earlier than they did in Phase 4.

That means:

- direct gradient/Hessian shape tests,
- direct basin-attribute serialization tests,
- direct hierarchy update tests,
- explicit sign-calibration tests,
- and paper-facing scenario tests before closeout.

### Lesson

Theory-facing tests should be first-class from the middle of the phase, not only
at the end.

## 6.4 Treat Public Names As Commitments

If `GRCV3` exposes names such as:

- `weighted_least_squares`
- `canonical_induced_frame`
- `degeneracy_spark`

then those names should correspond to real implementations, not placeholders that
merely resemble them.

### Lesson

Public names are commitments. Use them carefully.

## 6.5 Keep Observables And Semantics Aligned

`GRCV3` will introduce richer semantic surfaces than `GRCV2`, which makes naming
discipline even more important.

If the paper distinguishes:

- basin identity,
- abundance,
- choice/collapse state,
- hierarchy level,

then implementation names should preserve those distinctions explicitly.

### Lesson

Semantic richness increases the risk of naming drift, not decreases it.

## 6.6 Add An Earlier Mid-Phase Review

Phase 4's big validation gate was extremely useful, but it came after a lot of
implementation momentum had already accumulated.

For `GRCV3`, add:

- an earlier mid-phase paper review,
- before the family feels “mostly done”.

### Lesson

A single late gate is good. An earlier constitutive review would be better.

## 7. Concrete Process Changes Recommended Before Phase 5

Before or at the start of Phase 5:

1. create a `Phase-5-EquationMap.md`
2. create the detailed `Phase-5-ImplementationPlan.md`
3. embed the common backend strategy plan directly into the Phase 5 plan
4. define theory-facing test categories at plan time
5. define an explicit mid-phase validation gate for `GRCV3`

## 8. Final Judgment

Phase 4 should be judged as:

- successful,
- but educational in exactly the right way.

The project now has:

- a working executable baseline,
- a validated remediation pattern,
- and a clearer understanding of where theory-driven implementations tend to
  drift under engineering pressure.

If the lessons in this retrospective are applied, `GRCV3` should build faster,
with less semantic drift, and with fewer late-stage constitutive corrections.

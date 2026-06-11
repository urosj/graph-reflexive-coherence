# GRC9V3 Ports Conceptual And Design Guide

**Audience:** project contributors, experiment authors, synthesis writers, and anyone onboarding to the GRC9V3 nine-port substrate.

**Status:** conceptual/design guide. This document is not the ports reference, not an experiment report, and not a proof document.

---

## 1. Why This Guide Exists

The ports reference should answer questions like:

- What is port 6?
- Which row and column does it belong to?
- Which experiment reported which score?
- Which artifacts are direct, derived, partial, blocked, or inconclusive?

This guide answers a different set of questions:

- Why does the 3x3 structure exist?
- How should I think about rows, columns, and ports when designing new work?
- When is a claim row-semantic, column-semantic, port-semantic,
  graph-semantic, or identity-semantic?
- What kind of evidence is appropriate for each claim?
- How do I avoid turning a fixture witness into an overclaim?

The reference guide is a map. This guide is the interpretation manual.

The core lesson of the completed Lane A experiment family is not simply:

> The ports are semantic.

That is too blunt.

The better lesson is:

> The nine ports support several different readings of the same local graph
> state. Those readings explain different classes of runtime artifacts.

A GRC9V3 node is an ordinary graph node, a 3x3 local chart, and, when
refinement and basins enter, a possible basin chart in a larger identity
process.

The design task is to know which reading is appropriate for the artifact in
front of you.

---

## 2. The Central Design Claim

GRC9V3 should not be understood as “a graph with maximum degree nine.”

It should be understood as a bounded-degree graph substrate whose local degree
is organized as a 3x3 chart, so that the same incident edge can be read
geometrically, as an interface, and as a row-column intersection.

That gives three kinds of explanatory structure:

- **Rows:** local differential / geometric directions
- **Columns:** interface, refinement, and multiscale families
- **Ports:** exact row-column intersections where edge-local behavior lives

The completed experiments partially reject the anonymous-port null because
these views do not all explain the same things. Rows explain row/geometric
artifacts. Columns explain interface/refinement/multiscale artifacts. Ports
explain edge-local and observer-local artifacts. Ordinary graph and edge-label
baselines still explain generic capacity and path-label targets.

This is the important architectural conclusion:

> The system is not purely semantic. It is not purely anonymous graph degree.
> It has a division of explanatory labor.

That distinction should guide every future experiment and synthesis report.

---

## 3. Three Readings Of A Node

A GRC9V3 node can be read in three layers.

### 3.1 Graph Reading

In the graph reading, a node has degree, neighbors, edge weights,
conductance, flux, edge labels, and sink/basin status.

This reading is appropriate when the question is about active degree,
saturation, capacity, metric paths, temporal-delay paths, flux/coupling paths,
ordinary graph connectivity, or generic endpoint persistence.

The graph reading is not a failure of the 3x3 design. It is part of the design.
Some artifacts really are graph-level or edge-label-level artifacts.

For example, the Lane A saturation gate is a capacity-plus-signed-Hessian gate.
The path-disagreement fixture is an edge-label result. These are meaningful,
but they should not be forced into row/column semantic language.

### 3.2 Chart Reading

In the chart reading, the nine ports are arranged as:

| | Column 1 | Column 2 | Column 3 |
| --- | ---: | ---: | ---: |
| Row 1 | 1 | 2 | 3 |
| Row 2 | 4 | 5 | 6 |
| Row 3 | 7 | 8 | 9 |

Now an incident edge is not just “an edge.” It is an edge occupying a position
in a local chart: `port r = (row a, column b)`.

This reading is appropriate when the question is about row-local differential
response, column-local interface pressure, column-preserving refinement,
row/column transpose, port interaction, observer-local motion through ports, or
column G/Split.

The chart reading is where the nine-port structure becomes meaningful.

### 3.3 Basin Reading

In the basin reading, the node and its local module participate in a larger
identity process involving sinks, basins, lineage, budget, post-event
persistence, child basins, and possible collapse or reabsorption.

This reading is appropriate when asking whether refinement created a
persistent child identity, whether a post-event basin persisted, whether the
child basin had enough mass, whether lineage to the parent can be audited, and
whether budget was preserved.

This reading is stricter than the chart reading. A mechanical expansion can be
fully column-preserving and still not, by itself, be identity fission.

---

## 4. The Design Reason For Rows

Rows exist because geometry needs a local direction basis.

Without rows, a nine-port node can say, “I have nine incident edges,” but it
cannot stably say, “this local differential stress is concentrated in one chart
direction.”

The row grouping gives the node three local mode directions. These are not
literal continuum axes. They are a discrete chart convention for anisotropic
response.

### 4.1 What Rows Let You Ask

Rows let you ask:

- Which local direction is stressed?
- Does a row-local perturbation produce a row-local response?
- Does row permutation move the response?
- Does column permutation leave the row claim alone?
- Does transposition change the artifact class?

These are geometric or differential questions.

### 4.2 Why Row Evidence Matters

If rows were just labels, a row-local perturbation would not produce a stable
row-local artifact. It might produce activity, but that activity would not move
correctly under row permutation or vanish under balanced/random controls.

A good row experiment therefore does not only show that something changed. It
shows that the change is localized by row, transforms correctly under row
permutations, is not explained by column permutation, and is weakened by
non-factorized relabeling.

### 4.3 What Rows Do Not Prove

Rows do not prove that every geometric artifact is row-dominated.

In the completed row experiment, isotropic K terms were large relative to the
anisotropic row span. That is an important design lesson. The row signal can be
visible and correctly transforming even when isotropic terms dominate total
magnitude.

The safe conceptual claim is:

> Rows provide an observable local basis for anisotropic differential response.

The unsafe claim is:

> Total geometry is always row-dominated.

---

## 5. The Design Reason For Columns

Columns exist because interfaces need stable handles.

A row tells you how stress is distributed across local differential directions.
A column tells you how the node's boundary is partitioned into families that
can survive refinement, regrouping, and multiscale analysis.

Columns are therefore not “the other set of rows.”

They solve a different problem: how does the local boundary remain organized
when the graph changes?

### 5.1 What Columns Let You Ask

Columns let you ask:

- Which interface family is under pressure?
- Which old boundary edges belong together?
- Did refinement preserve the boundary organization?
- Which grouping aligns with post-event endpoint or basin behavior?
- Can a port-attached field be pooled and split by interface family?

These are interface, refinement, and multiscale questions.

### 5.2 Why Column Evidence Matters

The strongest column evidence is not just a column-local proxy.

The stronger column story is that the column-local proxy is observable, old
boundary edges are reassigned by column, old columns remain predictive after
refinement, true columns beat rows/random triples on interface/refinement
targets, and true columns support the intended multiscale view.

This makes columns the continuity mechanism across topology change.

### 5.3 Lane A Column Boundary

Under Lane A, column-H/cancellation is a derived analysis proxy. It is useful,
but it is not a direct spark gate.

That means a report may say:

- A derived column-local cancellation proxy was observed.
- The proxy transformed correctly under column controls.
- The proxy was compared against Lane A events.

A report may not say:

> Column-H directly triggered the Lane A spark.

unless an explicit Lane B implementation provides direct column-H proxy-branch
gate evidence. For GRC9V3, that implementation lane is
`spark_lane = "grc9v3_column_h_assisted"`; `canonical_column_h` names the
conceptual core GRC9 diagnostic rather than the preferred GRC9V3 runtime lane.
Lane B makes column-H a direct runtime-computed proxy branch, not a
primary geometric Hessian.

This is not a defect in the experiment family. It is a boundary that keeps the
object under test stable.

---

## 6. The Design Reason For Ports

A port is where a row and a column meet.

If rows and columns were the whole story, then a port would be mostly
bookkeeping: `port effect = row effect + column effect`.

D6 asks whether that is always enough. For the signed edge-local D6 target, it
is not.

At least one signed edge-local target required the specific row-column
intersection. The additive row+column model was insufficient, while the
port/intersection model fit.

### 6.1 What Ports Let You Ask

Ports let you ask:

- Which exact edge slot is special?
- Does the response require row x column interaction?
- Which port dominated the local observer?
- Which old boundary port was moved during refinement?
- Does grouping by row lose important column information?
- Does grouping by column lose important row information?

These are edge-local and intersection questions.

### 6.2 Why Port Evidence Matters

The port is the place where two meanings meet:

- **Row meaning:** local differential direction
- **Column meaning:** interface family
- **Port meaning:** exact edge-local realization of both

A non-additive port result means that knowing the row and knowing the column
separately is not enough. You need the exact intersection.

### 6.3 What Port Evidence Does Not Prove

D6 is an existence witness, not a universal law.

The runtime absolute-flux control in the matched fixture was additive. That is
valuable. It tells us that port interaction is not a magical property of every
port surface. It appears where the artifact class needs it.

The safe conceptual claim is:

> Some edge-local port surfaces require row-column interaction.

The unsafe claim is:

> All port-level behavior is non-additive.

---

## 7. Saturation Is Capacity, Not Automatically Semantics

Saturation is the moment when the local chart has no unused port capacity.

Under Lane A, refinement requires more than fullness. The observed gate is:

```text
active_degree == 9
AND gradient_norm < eps_gradient
AND min_signed_hessian < eps_spark
```

This means fullness alone is insufficient, signed-Hessian stress alone is
insufficient without saturation, and fullness plus signed-Hessian degeneracy
produces the positive event.

This is a representational bottleneck claim.

It should not be confused with a row/column factorization claim. The saturation
gate is allowed to be invariant under row/column transforms and non-factorized
relabels because it is about capacity and Hessian degeneracy, not about row or
column semantics.

### 7.1 How To Use Saturation Correctly

Use saturation evidence when you are asking:

- Did the local chart exhaust its interface capacity?
- Was the active degree exactly nine?
- Did the signed-Hessian gate hold?
- Did a candidate or expansion event occur?
- Was budget preserved?

Do not use saturation evidence by itself to claim:

- Rows caused the event.
- Columns caused the event.
- Column-H directly gated the event.
- Identity fission occurred.

Those are different claims requiring different evidence.

---

## 8. Refinement Is Mechanical; Identity Is Basin-Level

This is one of the most important distinctions in the system.

A spark candidate is not a refinement.

A refinement is not an identity.

A child basin is not landscape-general identity unless persistence is shown at
the appropriate scope.

The lifecycle is:

```text
candidate condition
    -> mechanical expansion
    -> post-event flow
    -> possible persistent child basins
    -> possible identity emergence claim
```

### 8.1 Mechanical Refinement

Mechanical refinement is a topology event.

A mechanical refinement claim needs:

- expansion event payload
- old boundary edge mapping
- old port and column
- new module endpoint
- budget before and after

If old boundary columns match new module endpoint columns, then mechanical
column preservation is supported.

### 8.2 Identity Emergence

Identity emergence is a stricter claim.

It needs:

- mechanical refinement
- persistent post-event sink/basin rows
- minimum basin mass
- lineage to the refined parent/module
- budget preservation
- threshold sensitivity
- negative controls where possible

Mechanical refinement alone is not identity fission.

### 8.3 Why This Matters Philosophically

This distinction preserves the RC idea that identity is not a label or a graph
rewrite. Identity is a stable, self-maintaining attractor basin.

GRC9V3 can create new mechanical degrees of freedom. The reflexive dynamics
then decide whether those degrees of freedom stabilize into child identities.

This is a central design principle:

> The event creates room. The persistent basin supports the identity claim.

---

## 9. G/Split: Reconstruction Versus Semantic Usefulness

Column G/Split has two different meanings.

- Mathematical: can eligible nonnegative port-attached fields be reconstructed
  exactly?
- Semantic: is the true column grouping the useful grouping for
  interface/refinement targets?

Experiment E answers the first. D7 answers the second.

### 9.1 Reconstruction

For eligible nonnegative port fields, column G/Split reconstructs exactly or
near-exactly. Signed flux reconstructs exactly through J+ / J-. Compressed
signed totals are lossy when signs mix within a column.

This supports the operator behavior for the tested eligible fields.

### 9.2 Semantic Grouping

Exact reconstruction alone does not prove that columns are semantically special.
Any grouping can reconstruct if it stores its own total and profile.

The semantic evidence is that true columns outperform rows, random triples, and
a single-total baseline on interface/refinement targets.

That is the design lesson: G/Split is exact as an operator, and true columns
are useful because they align with interface/refinement behavior.

---

## 10. Edge-Label Paths Are A Different Kind Of Evidence

Experiment F shows that metric, delay, and strongest-flux/coupling paths can
disagree while remaining auditable.

This is important, but it is not row/column evidence.

It supports the idea that the v3 edge surface can carry multiple analytic
labels:

- geometric length
- temporal delay
- flux or coupling strength

A path disagreement claim should be written as an edge-label claim.

Safe claim:

> Different edge-label path criteria can select different corridors and remain
> auditable edge by edge.

Unsafe claim:

> Path disagreement proves row/column semantics.

---

## 11. Motion Observer: Semantics Over Time

Experiment G shows that row/column classifications can be reconstructed over a
time window when the observer has port-level history.

The useful transition classes are row-preserving / column-changing,
column-preserving / row-changing, both-changing, and neither-changing.

This is the temporal version of the chart reading.

A static port says that an edge occupies row `a` and column `b`.

A motion observer asks how the dominant port moved through row/column space.

The completed support uses experiment-local checkpoint overlays. Reusable
motion-loader full port histories remain partial.

The safe claim is:

> Observer-local mixed row/column motion classification is supported in clean
> checkpoint-overlay fixtures.

The unsafe claim is:

> Reusable motion-loader histories already support all port-motion semantics.

---

## 12. Experiment Design Philosophy

The completed work used two layers.

### 12.1 O-Style Witnesses

A-G answer: can the phenomenon be observed at all?

These are controlled fixtures. They are intentionally close to unit or
integration tests.

They show row, derived-column, G/Split, saturation,
refinement/identity-boundary, path-label, and motion witnesses.

They do not, by themselves, prove the global semantics of GRC9V3.

### 12.2 D-Style Discriminators

D1-D8 answer: does the phenomenon survive alternative explanations?

They compare against structured row/column transforms, row/column transpose,
sampled non-factorized relabeling, random triples, degree/adjacency baselines,
additive row+column models, and identity persistence thresholds.

This is where the anonymous-port null is partially rejected.

### 12.3 Why This Layering Matters

A clean fixture is not a philosophical proof.

A discriminator is not a landscape robustness suite.

A landscape robustness suite is not a direct runtime implementation.

Each layer has its job. Mixing them causes overclaims.

---

## 13. How To Choose The Right Evidence

Before writing a claim, identify the claim type.

### 13.1 Row Claim

Use when the artifact is geometric or differential.

Evidence should include:

- row-local response
- row permutation
- column permutation
- balanced or isotropic control
- transpose or non-factorized control where available

Claim shape:

> Rows are observable for this differential/geometric artifact class in this
> fixture family.

### 13.2 Column Claim

Use when the artifact is interface, refinement, or multiscale.

Evidence should include:

- column-local proxy or grouping
- column permutation
- row control
- refinement mapping or G/Split where relevant
- random grouping comparison where relevant

Claim shape:

> Columns are observable as interface/refinement/multiscale families for this
> artifact class.

### 13.3 Port Claim

Use when the exact edge slot matters.

Evidence should include:

- port-level target
- row+column additive baseline
- row x column interaction or port-level model
- matched perturbation
- neighbor-shell control

Claim shape:

> This edge-local target requires port/intersection information beyond additive
> row and column summaries.

### 13.4 Saturation Claim

Use when the artifact is capacity or spark gating.

Evidence should include:

- active degree
- gradient norm
- signed-Hessian minimum
- candidate count
- refinement count
- budget evidence
- degree 7/8/9 controls
- fullness-without-stress control
- stress-without-fullness control

Claim shape:

> Under Lane A, active-degree 9 plus signed-Hessian degeneracy gates refinement
> in this fixture.

### 13.5 Identity Claim

Use only when persistence evidence exists.

Evidence should include:

- mechanical refinement
- sink/basin persistence
- minimum basin mass
- lineage
- budget
- threshold sensitivity
- negative controls

Claim shape:

> Configured-window persistent child-basin identity emergence is supported in
> this fixture family.

---

## 14. Claim Grammar

Use precise verbs.

### 14.1 Good Verbs

Use precise verbs such as `observed`, `reconstructed`, `supported`,
`partially supported`, `blocked`, `inconclusive`, `derived`, `direct`,
`thresholded`, `fixture-level`, and `Lane A bounded`.

### 14.2 Dangerous Verbs

Be careful with verbs and phrases such as `proves`, `causes`, `is`, `always`,
`globally`, `universally`, `directly gates`, and `identity fission`.

These can be used only when the evidence really supports them.

### 14.3 Examples

Good:

> The derived column-local cancellation proxy is observable and transforms
> correctly under Lane A.

Bad:

> Column-H triggers sparks.

Good:

> Mechanical refinement preserves old boundary columns.

Bad:

> Refinement is identity fission.

Good:

> D1-D8 partially reject the anonymous-port null for controlled Lane A artifact
> classes.

Bad:

> The anonymous-port null is dead everywhere.

---

## 15. The Anonymous-Port Null After The Experiments

The anonymous-port null says that rows, columns, and ports add no explanatory
power beyond ordinary graph degree, adjacency, conductance, coherence, and edge
labels.

The completed D1-D8 pass partially rejects this.

It is no longer plausible that all tested artifacts are explained by anonymous
nine-port degree alone.

But H0 remains competitive for some targets:

- Lane A saturation gate
- edge-label path disagreement
- some endpoint persistence availability in clean fixtures

This is not a contradiction. It is the final design lesson: the system has
multiple explanatory views, and the right view depends on the artifact class.

---

## 16. Teaching The System Philosophy

When teaching GRC9V3, avoid starting with the scores.

Start with the problem: how can a finite graph node carry enough local
structure to support geometry, interface continuity, refinement, multiscale
views, and identity claims without adding arbitrary labels at every event?

Then introduce the answer: use a fixed 3x3 local chart.

Then explain the division:

- **Rows** let the graph talk about local differential direction.
- **Columns** let the graph preserve boundary/interface organization across
  refinement and scale.
- **Ports** let the graph retain edge-local row-column intersections.
- **Saturation** makes local chart exhaustion explicit.
- **Refinement** creates more substrate without declaring identity by fiat.
- **Basins** decide whether identity actually persists.

This is the philosophy in one sentence:

> GRC9V3 makes local graph mechanics interpretable without pretending that
> every interpretation is already an identity claim.

---

## 17. Designing New Experiments

A new experiment should begin with one sentence:

> This experiment tests whether `<feature family>` explains `<artifact class>`
> better than `<alternative explanation>`.

Examples:

- This experiment tests whether true columns explain post-refinement routing
  better than random triples.
- This experiment tests whether port-level interaction explains flux reversal
  better than additive row+column summaries.
- This experiment tests whether checkpoint-window basin persistence agrees
  with runtime-state persistence after refinement.

Then define the primary artifact, feature family, alternative baseline,
controls, evidence type, blocked rule, and claim boundary.

### 17.1 Minimal Design Checklist

Before running, answer:

- What is the artifact class?
- Is the evidence direct, derived, partial, blocked, or inconclusive?
- Which baseline could explain the result without row/column/port semantics?
- Which transform should preserve the result?
- Which transform should break or weaken it?
- What would count as failure?
- What claim will remain blocked even if the fixture passes?

If those questions are not answered, the experiment is probably not ready.

---

## 18. Designing Synthesis Reports

A synthesis report should not merely list pass/fail outcomes.

It should classify explanatory roles.

A good synthesis asks:

- Which parts of H0 are weakened?
- Which parts remain competitive?
- Which claims are Lane A bounded?
- Which claims are fixture-level only?
- Which claims require future runtime implementation?
- Which claims require landscape robustness?

Use a structure like:

1. Scope
2. Object under test
3. Supported claims
4. H0-competitive targets
5. Blocked / inconclusive surfaces
6. Claim guardrails
7. Follow-up work

Always separate mechanical support from identity support, and operator
reconstruction from semantic usefulness.

---

## 19. Follow-Up Work: What Kind Of Work Is It?

Not every future item is the same type of work.

Completed comparison work:

- Lane C comparison of Lane A against implemented Lane B
  `grc9v3_column_h_assisted` proxy-branch gate evidence:
  `lane_c_comparison_complete_direct_column_h_branch_delta_observed_with_boundaries`

### 19.1 Runtime Implementation Work

These require `src/pygrc` implementation and tests:

- degree-8 near-saturation policy
- inflow-weighted expansion transfer lane
- reusable motion-loader full port histories

These are not experiment-local fixes.

### 19.2 Artifact/Observer Work

These improve evidence without necessarily changing semantics:

- checkpoint-window identity persistence
- persisted refinement checkpoints with E-style port fields
- better motion overlay readers
- more complete basin/lineage checkpoint surfaces

### 19.3 Experiment Robustness Work

These test generality:

- landscape/seed robustness suite
- larger fitted held-out predictive CV
- broader S9 sampling
- more refinement outcome classes
- collapse/reabsorption fixtures

Keeping these categories separate prevents the experiment track from becoming
an implementation track by accident.

---

## 20. Closing Orientation

The nine-port substrate is useful because it lets one local graph object carry
several kinds of meaning without collapsing them into one another.

A row claim is not a column claim.

A column claim is not a port-interaction claim.

A refinement claim is not an identity claim.

A path-label claim is not row/column evidence.

A clean fixture is not landscape generality.

The completed Lane A experiments show that these distinctions are not only
source-authored intent. They are visible in controlled runtime artifacts.

The right final attitude is:

> GRC9V3 is not merely a bounded-degree graph convention. It is also not a
> universal semantic explanation for every artifact. It is a compact 3x3
> mechanical chart whose rows, columns, ports, capacity, and basin context each
> become meaningful for the artifact classes they are designed to explain.

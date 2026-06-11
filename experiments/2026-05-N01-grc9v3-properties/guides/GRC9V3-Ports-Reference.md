# GRC9V3 Ports, Rows, and Columns

Reference and interpretation guide.

## Purpose

This guide is for reading GRC9V3 runtime artifacts.

A nine-port node can be analyzed in two complementary ways. As a graph node, it
has degree, edges, weights, fluxes, labels, and state. As a 3x3 port chart, it
has rows, columns, and row-column intersections. The completed experiments show
that neither view alone is enough: ordinary graph features explain some target
classes, while row, column, port, and basin-context features explain others.

The practical question is not "are ports semantic or not?"

The useful question is: which grouping explains this artifact class, and what
evidence is allowed under Lane A?

This guide is not a new experiment report and it is not a proof document. The
reports record evidence. This guide provides the operational bridge from
theory to implementation to experiments to practical use.

Primary evidence sources:

- `reports/family_level_synthesis.md`
- `reports/discriminator_synthesis.md`
- `outputs/discriminator_hypothesis_status.csv`

## How To Use This Guide

Read:

- `What Rows Are For` if you are testing geometric or differential response.
- `What Columns Are For` if you are testing interface pressure, refinement, or
  multiscale structure.
- `What Ports Are For` if you are testing edge-local behavior or row x column
  interaction.
- `Saturation And Chart Exhaustion` if you are testing spark eligibility under
  Lane A.
- `Spark, Refinement, And Identity` before making any identity claim.
- `Claim Decision Tree` before writing a report or synthesis claim.
- `Minimal Fixture Recipes` before designing the next fixture.

## One-Page Mental Model

Think of a GRC9V3 node as a small local chart.

The nine ports are not just nine sockets. They are arranged so the same
incident edge can be interpreted in several useful ways:

- by row: which local differential direction does this edge belong to?
- by column: which interface family does this edge belong to?
- by port: which exact row-column intersection carries this edge?
- by graph state: what degree, conductance, flux, label, and basin context does
  the edge participate in?

This is why the same edge can matter to multiple analyses. A row analysis asks
whether geometry is stressed in a local direction. A column analysis asks
whether boundary/interface organization is stable or under pressure. A port
analysis asks whether the exact edge slot matters beyond row and column
membership. A graph analysis asks whether the behavior is ordinary degree,
capacity, conductance, or edge-label behavior.

Port map:

| | Column 1 | Column 2 | Column 3 |
| --- | ---: | ---: | ---: |
| Row 1 | `1` | `2` | `3` |
| Row 2 | `4` | `5` | `6` |
| Row 3 | `7` | `8` | `9` |

The row/column coordinates are derived from `port_id`:

- `row = ((port_id - 1) // 3) + 1`
- `column = ((port_id - 1) % 3) + 1`

Interpretation:

- rows are local geometric / differential mode directions
- columns are interface / refinement / multiscale families
- ports are row-column intersections

The final discriminator classification is
`anonymous_port_null_partially_rejected_with_lane_a_boundaries`.

Plain language:

> The nine ports are not anonymous for everything. They are also not semantic
> for everything. The evidence supports a division of labor.

## Evidence Types Used In This Guide

The experiment family uses these evidence labels.

| Evidence label | Meaning |
| --- | --- |
| `direct` | Present in runtime state, event payload, checkpoint, public operator, or generated output. |
| `derived` | Reconstructed from existing artifacts without changing runtime behavior. |
| `partial` | Available only through special capture, overlay reconstruction, thresholded analysis, or incomplete surface. |
| `blocked` | Not reconstructable under the current runtime surface. |
| `inconclusive` | Some relevant surface exists, but the current fixture set cannot support the claim. |

A supported claim must be backed by direct, derived, or carefully bounded
partial artifacts. A blocked claim is not a failed hypothesis. It means the
current runtime does not expose the evidence needed to test it.

Derived means useful, but it is not causal gate evidence. For example, Lane A
column cancellation proxies are valid derived analysis surfaces, but they are
not direct column-H spark gates.

## Lane A Boundary

All completed results use `lane_id = current_hybrid_signed_hessian`. This is
Lane A: the current implemented runtime object under test.

That distinction matters. The experiment family asks what the existing Lane A
runtime exposed. Direct runtime column-H proxy-branch gating is now available
only in the separate opt-in Lane B runtime and should be compared against Lane
A rather than silently replacing it.

Under Lane A:

- hybrid spark candidates are signed-Hessian hybrid runtime events
- direct column-H spark gating is not implemented or claimed
- column-H / cancellation evidence is derived/non-gating
- degree-8 near-saturation is not implemented
- mechanical refinement is not identity fission
- child identity claims require persistent post-event sink/basin artifacts

Lane B for GRC9V3 uses
`spark_lane = "grc9v3_column_h_assisted"`. The phrase `canonical_column_h`
refers to the conceptual core GRC9 column-H diagnostic, not the preferred
GRC9V3 runtime lane id. Lane B makes the column-H proxy a direct
runtime-computed predicate branch; it would not make column-H a primary
geometric Hessian. Do not infer direct column-H proxy-branch gating from Lane A
column proxy or saturation evidence.

## The Division Of Labor

The final discriminator result is not that rows, columns, and ports explain
everything. It is that they explain different things.

| Artifact class | Most useful view |
| --- | --- |
| Geometric / differential response | Rows |
| Interface pressure / refinement / multiscale | Columns |
| Edge-local signed behavior / observer port motion | Ports |
| Lane A saturation and current spark gate | Active degree plus signed-Hessian gate |
| Path disagreement | Edge labels |
| Identity emergence | Composite basin context |
| Generic activity | Degree / adjacency / conductance / edge state |

This is why the anonymous-port null is only partially rejected. It remains
competitive for generic graph and edge-label targets, but not for the
row/column/port-sensitive targets.

## The Port Lifecycle

A port can participate in several roles over a run:

- As an ordinary edge slot, it contributes to graph dynamics, conductance, flux,
  degree, and labels.
- Through row membership, it contributes to row-resolved differential or
  geometric response.
- Through column membership, it contributes to interface grouping, cancellation
  proxies, refinement mapping, and multiscale views.
- As a specific port, it may carry edge-local behavior that is not reducible to
  row plus column.
- At full saturation, active degree 9 marks local chart exhaustion under Lane A
  only when the signed-Hessian gate also holds.
- During mechanical refinement, old boundary edges are reassigned by column.
- In post-event basin dynamics, persistent sink/basin artifacts determine
  whether any child identity claim is supported.

Lifecycle sketch:

- Row stress leads to row-resolved geometry / differential response.
- Column pressure leads to interface proxy / refinement mapping / multiscale
  grouping.
- A port-level edge can expose row x column interaction or an observer
  transition.
- Saturation plus signed-Hessian degeneracy can lead to mechanical expansion;
  post-event basins support an identity claim only if they persist.

## What Rows Are For

### Intuition

Rows are the part of the 3x3 chart that lets a node say that stress is stronger
in one local direction than another.

Without rows, a saturated nine-port node could still have nine incident edges,
but there would be no stable way to ask whether a perturbation is geometrically
directional or merely high-degree.

Rows are a discrete chart convention for anisotropic response. They do not
claim that the continuum theory literally has three primitive spatial
directions.

### Use Rows When

Use row grouping when asking:

- Which local geometric direction is stressed?
- Which row-resolved mismatch, gradient, flux stress, or tensor signature moved?
- Did a structured row transform move the signature as expected?

### Supported Under Lane A

- Experiment A row-local stress produces the expected dominant row signature.
- Row permutation moves the signature.
- Column permutation preserves the stressed row.
- Balanced controls have no dominant row.
- Transpose and random relabel controls remove the clean predefined row claim.
- D3 shows row-local geometry response exceeds its transpose baseline:
  `0.627051` versus `0.333333`.

Safe claim:

> Rows are observable in clean row-stress fixtures as differential/geometric
> artifact families.

### Boundary

The isotropic contribution to `K` can dominate magnitude. The supported claim
is not that total `K` is always row-dominated. It is that row-resolved
anisotropic signatures are detectable and transform correctly in the tested
fixtures.

### Artifact Extraction

| Needed observation | Artifact surface |
| --- | --- |
| Port row | Derived from `port_id` with `port_to_rc` / row formula |
| Row-local response | Experiment A rows and cached row mismatch/tensor fields |
| Edge flux by row | `GRC9V3State.port_edges` plus endpoint ports |
| Isotropic caveat | Compare isotropic and anisotropic response terms |

### Example: Reading A Row-Stress Fixture

Suppose ports `4`, `5`, and `6` are perturbed. These are row 2.

Expected row interpretation: row 2 should dominate the row-resolved response.

What supports the claim:

- the dominant row is row 2
- a row permutation moves the dominant row
- a column permutation preserves the stressed row
- a balanced control has no dominant row
- a random relabel removes the clean predefined row meaning

What does not follow: total `K` is always row-dominated.

## What Columns Are For

### Intuition

Columns are the part of the chart that lets a node preserve boundary
organization when the graph changes. Rows help describe local differential
stress. Columns help keep interface identity stable across refinement and
scale.

This is why column evidence is not only about a cancellation proxy. The
stronger column evidence is that old boundary columns are preserved during
mechanical expansion and remain predictive in tested post-window
interface-memory targets.

### Use Columns When

Use column grouping when asking:

- Which interface family is under cancellation or pressure?
- Did refinement preserve old boundary-column structure?
- Which grouping aligns with interface/refinement targets?
- Can a port-attached field be reconstructed through G/Split?

### Supported Under Lane A

- Experiment B observes a derived column-local cancellation/pressure proxy.
- D5 shows immediate old-column preservation score `1.0`.
- D5 shows post-window old-column memory score `0.888889`, while row/random
  semantic controls score `0.222222`.
- D7 shows true columns outperform rows, random triples, and a single-total
  baseline on immediate and post-window interface/refinement targets.
- D7 confirms true-column G/Split reconstruction for eligible fields.

Safe claim:

> Columns are observable as interface/refinement/multiscale families under
> Lane A.

Unsafe overclaim:

> Lane A has direct column-H spark gating.

### Boundary

Under Lane A, column-H/cancellation is a derived analysis proxy. Lane B
`grc9v3_column_h_assisted` provides direct runtime column-H proxy-branch
evidence only for runs explicitly configured with that spark lane. Derived
column evidence can be analyzed, scored, and compared, but it did not directly
trigger the spark under Lane A.

### Artifact Extraction

| Needed observation | Artifact surface |
| --- | --- |
| Port column | Derived from `port_id` with `port_to_rc` / column formula |
| Column proxy | Endpoint ports, coherence, conductance, signed flux |
| Refinement mapping | `hybrid_mechanical_expansion.payload.reassignment_map` |
| Interface memory | Post-event endpoint, sink, basin, and child rows |
| Multiscale profile | Column G/Split output fields |

### Example: Reading A Refinement Event

An old boundary edge occupies parent port `6`.

Port `6` is row 2, column 3.

During mechanical expansion, the old edge should be reassigned to the
column-3 satellite/module endpoint.

A successful mechanical column-memory claim requires:

- old column is `3`
- new module endpoint column is `3`
- reassignment evidence comes from the expansion payload
- budget is preserved

A child identity claim requires more:

- post-event child sink/basin persistence
- lineage evidence
- basin mass threshold
- budget audit

Mechanical column preservation is not identity fission.

## What Ports Are For

### Intuition

A port is where a row direction and a column family meet.

If all behavior were explainable by row effects plus column effects, the
individual port would be mostly bookkeeping. D6 matters because it shows at
least one signed edge-local surface where the specific row-column intersection
is needed.

### Use Ports When

Use port-level features when asking:

- Which exact edge or port is special?
- Does the artifact need row x column interaction?
- Which port dominated an observer-local transition?
- Which old boundary port was reassigned during refinement?

### Supported Under Lane A

- D6 tested all nine canonical ports with matched perturbations.
- The signed edge-local target had additive row+column `R2 = 0.2`.
- The interaction and port-level models fit that target with `R2 = 1.0`.
- Experiment G classifies observer-local transitions from port histories:
  row-preserving/column-changing, column-preserving/row-changing,
  both-changing, and neither-changing.

Safe claim:

> At least one signed edge-local port surface requires row x column interaction
> or port-level features.

### Boundary

D6 is an existence witness, not a universal claim. The runtime absolute-flux
control in the same matched fixture was additive and did not require an
interaction term.

### Artifact Extraction

| Needed observation | Artifact surface |
| --- | --- |
| Exact port | Port id from endpoint metadata or `PortEdge` records |
| Port row/column | Derived from `port_id` |
| Signed port flux | `GRC9V3State.port_edges[*].flux_uv` or cached oriented flux |
| Dominant observer port | Experiment-local checkpoint overlay over port state |
| Port interaction target | D6 configured signed edge-local target rows |

### Example: Additive Versus Port Interaction

Suppose a signed edge-local target at port `(2,3)` is much larger than expected.

A useful additive shorthand is
`response(2,3) ~= row_effect(2) + column_effect(3)`.

A port-interaction explanation says the response at `(2,3)` requires that
specific row-column intersection.

D6 supports the second interpretation for one signed edge-local target:

- additive row+column `R2 = 0.2`
- port / interaction `R2 = 1.0`

But the runtime absolute-flux control did not require interaction in that
fixture, so the correct claim is narrow.

## Saturation And Chart Exhaustion

### Intuition

Saturation is finite local chart exhaustion.

The nine-port chart gives a node finite local representational capacity. Under
Lane A, refinement is not triggered merely by high stress or merely by being
full. It requires the conjunction of full occupancy and signed-Hessian
degeneracy.

### Lane A Gate

The observed canonical gate is:

```text
active_degree == 9
AND gradient_norm < eps_gradient
AND min_signed_hessian < eps_spark
```

D4 supports this as a capacity plus signed-Hessian bottleneck:

- degree-7 stressed: no candidate, no refinement
- degree-8 stressed: no candidate, no refinement
- degree-9 stressed: candidate plus mechanical expansion
- degree-9 stable-Hessian fullness control: no trigger
- positive budget error: `0.0` under tolerance `1e-12`

Safe claims:

- Fullness alone is insufficient.
- Signed-Hessian stress alone is insufficient without saturation.
- The positive Lane A event requires active-degree 9 plus signed-Hessian
  degeneracy.

### Boundary

This is not row/column factorization evidence by itself. It is a Lane A
capacity/Hessian gate. D2 records D4 saturation as an H0-competitive generic
capacity target.

Degree-8 near-saturation remains blocked under Lane A.

## Spark, Refinement, And Identity

### Intuition

Spark and refinement create representational room. Identity requires persistent
post-event basin structure.

Keep these layers separate:

| Layer | Meaning |
| --- | --- |
| Spark candidate | Local gate/candidate evidence |
| Mechanical expansion | Topology refinement event |
| Identity emergence | Persistent post-event child sink/basin structure |

Mechanical refinement is not identity fission.

### Supported Under Lane A

- Experiment D and D5 support column-preserving mechanical refinement.
- D8 supports configured-window child-basin identity persistence in clean
  Experiment D refinement fixtures.
- Accepted D8 identity requires refinement, persistent child sink/basin rows,
  lineage evidence, and budget preservation.
- D8 records `20` accepted configured-window identity events and `30`
  strict-threshold failure rows.

Safe claim:

> D8 supports configured-window persistent child-basin identity emergence in
> clean runtime-state refinement fixtures.

Unsafe overclaims:

- Every refinement is identity fission.
- Checkpoint-window identity persistence is established.
- Landscape-general identity emergence is established.

### Artifact Extraction

| Needed observation | Artifact surface |
| --- | --- |
| Refinement event | `hybrid_mechanical_expansion` event |
| Reassignment lineage | Expansion payload and module records |
| Sink set | `GRC9V3State.sink_set` or persisted equivalent |
| Basin assignments | `GRC9V3State.basins` or persisted equivalent |
| Basin mass | Post-event basin mass rows |
| Budget | Pre/post coherence sum and event payload budget evidence |

## Multiscale G/Split

### Intuition

Column G/Split is the multiscale view for eligible port-attached fields.

Exact reconstruction proves that the operator works. Semantic usefulness
requires a second question: does the true-column grouping align with
interface/refinement targets better than rows or random triples?

D7 answers yes for the tested clean fixtures.

### Supported Under Lane A

Experiment E and D7 support:

- eligible nonnegative fields reconstruct through true-column G/Split
- max exact reconstruction error is `1.11e-16`
- signed flux reconstructs exactly through `J+ / J-`
- compressed signed-column-total reconstruction is lossy when signs mix inside
  a column

D7 adds the semantic discriminator:

- true columns score `1.0` on immediate interface/refinement target
- true rows score `0.333333`
- sampled random triples score `0.222222`
- single total scores `0.333333`

Safe claim:

> True columns reconstruct eligible fields and align better than tested
> row/random/single-total alternatives with interface/refinement targets.

### Boundary

Exact reconstruction alone does not prove semantic column superiority. Any
grouping can reconstruct if it stores its own totals and profiles.

Before/after refinement E-style G/Split checkpoints remain blocked.

## Edge-Label Paths

Experiment F tests multi-label edge semantics:

| Path criterion | Scoring rule |
| --- | --- |
| Metric path | Minimize `sum geometric_length(e)` |
| Delay path | Minimize `sum temporal_delay(e)` |
| Primary flux path | Maximize `min_e abs(signed_flux(e))` |
| Primary coupling path | Maximize `min_e flux_coupling(e)` |

Supported evidence:

- metric path selects corridor A
- delay path selects corridor B
- strongest flux/coupling path selects corridor C
- equalized-label controls collapse or change choices for the intended reason

Why this matters:

GRC-v3 can separate base graph dynamics from analytic edge labels such as
metric length, temporal delay, and coupling/flux strength.

Boundary:

Path disagreement supports the multi-label edge surface. It is not direct
row/column semantic evidence. D2 records it as an H0-competitive edge-label
target.

## Motion Observer

Experiment G classifies observer-local motion transitions:

- row-preserving / column-changing
- column-preserving / row-changing
- both-changing
- neither-changing

Supported evidence:

- row-2 sweep `4 -> 5 -> 6` classifies as row-preserving/column-changing
- column-3 sweep `3 -> 6 -> 9` classifies as column-preserving/row-changing
- static port `5 -> 5 -> 5` classifies as neither-changing
- structured row/column permutations preserve expected transition class
- non-factorized random relabel weakens semantic interpretability

Why this matters:

Motion classification shows how row/column meaning can be reconstructed from
port-level state over time, not only from static perturbation fixtures.

Boundary:

This support uses experiment-local checkpoint overlays over port-level state.
Reusable motion-loader full port histories remain partial.

## Choosing The Right Grouping

| Question | Use |
| --- | --- |
| What local geometric direction is stressed? | Rows |
| Which interface family is under pressure? | Columns |
| Which exact edge or port is special? | Ports |
| Will a full node refine under Lane A? | Active degree plus signed-Hessian gate |
| Did refinement preserve interface structure? | Old column -> new endpoint column |
| Did identity emerge? | Persistent sink/basin plus lineage plus budget |
| Can I reconstruct port fields at scale? | Column G/Split |
| Do different path notions disagree? | Edge labels, not row/column grouping |
| Is this generic activity? | Degree/adjacency or edge-label baselines |

## Claim Decision Tree

Use this before writing a report claim.

1. Classify the artifact surface.
   - `blocked`: make no positive claim.
   - `inconclusive`: report the surface and why the fixture cannot decide.
   - `partial`: make only a local, qualified claim.
   - `derived`: claim the derived proxy, not direct runtime causality.
   - `direct`: claim the runtime artifact, with scope.

2. Decide whether the claim is mechanical or identity-level.
   - Mechanical claims can be supported by event payload, mapping, and budget
     evidence.
   - Identity claims require persistent sink/basin evidence, lineage, mass
     threshold, and budget.

3. For row/column/port semantic claims, require structured transform controls,
   compare against non-factorized or random grouping controls where possible,
   and check a degree/adjacency baseline where relevant.

4. For landscape-general claims, require landscape/seed robustness. Otherwise,
   say clean-fixture support.

## Hypothesis Map

The hypotheses are layered.

H0 is the skeptical baseline. O1-O4 say what phenomena should exist. D1-D8 ask
whether those phenomena survive alternative explanations.

For example, O1 can show that a row effect exists, but D1 and D3 ask whether
that row effect is really part of a 3x3 factorization rather than an artifact
of labels. O2 can show that columns are useful, but D5 and D7 ask whether true
columns remain better than rows or random triples for interface/refinement
targets. O3 can show port-level behavior, but D6 asks whether the specific port
matters beyond row plus column.

### H0: Anonymous-Port Null

Plain meaning:

Maybe the nine ports are only anonymous degree slots.

Why it matters:

If H0 explained every artifact, row/column/port semantics would add no
predictive value beyond ordinary graph features.

Evidence:

D1-D8 partially reject H0 for controlled Lane A artifact classes. D2 shows
rows, columns, ports, composite basin context, and graph/edge-label baselines
explain different target classes.

Boundary:

H0 remains competitive for D4 Lane A saturation, Experiment F edge-label path
disagreement, and D5 endpoint persistence availability in the clean fixture.

### O1: Rows As Differential Modes

Plain meaning:

Rows should be visible in geometric or differential response.

Why it matters:

If row-local perturbations did not produce row-local signatures, rows would be
only labels.

Evidence:

Experiment A and D3 support row-local signatures and transpose
non-equivalence.

Boundary:

Clean fixtures only; isotropic terms can dominate total magnitude.

### O2: Columns As Interface Families

Plain meaning:

Columns should organize interface, refinement, and multiscale behavior.

Why it matters:

Columns must survive refinement and multiscale tests, not merely appear in
notation.

Evidence:

Experiment B derived proxy, D5 interface memory, and D7 multiscale semantic
grouping support column usefulness.

Boundary:

Direct column-H proxy-branch spark evidence is blocked under Lane A and
available only in explicit Lane B runs.

### O3: Ports As Row-Column Intersections

Plain meaning:

The exact row-column intersection should sometimes matter.

Why it matters:

If all port behavior were row main effect plus column main effect, the port
would mostly be bookkeeping.

Evidence:

D6 supports one signed edge-local port-interaction witness. Experiment G
supports observer-local port transition classes.

Boundary:

Runtime absolute flux was additive in the D6 matched fixture.

### O4: Multi-Label Edge Paths

Plain meaning:

Metric, delay, and strongest-flux paths can be different.

Why it matters:

This tests edge-label semantics, not row/column factorization.

Evidence:

Experiment F supports auditable path disagreement with equalized controls.

Boundary:

Not direct row/column semantic evidence.

### D1-D8 In One Line

| Discriminator | Plain meaning | Boundary |
| --- | --- | --- |
| D1 | Structured row/column transforms should beat sampled non-factorized regrouping. | Sampled, not exhaustive S9. |
| D2 | Different feature families should predict different artifact classes. | Scorecard, not full held-out landscape CV. |
| D3 | Rows and columns should not be interchangeable. | Direct column-H transpose remains blocked. |
| D4 | Nine occupied ports can act as local capacity under Lane A. | Capacity/Hessian evidence, not factorization evidence. |
| D5 | Parent columns should preserve interface memory across refinement. | Post-window support is partial. |
| D6 | Some port targets should require row x column interaction. | Existence witness only. |
| D7 | Columns should reconstruct and align with interface/refinement semantics. | Other groupings can reconstruct with their own profiles. |
| D8 | Refinement is identity only if child basins persist. | Checkpoint and landscape identity remain inconclusive. |

## Claim Discipline

| Safe claim | Unsafe overclaim |
| --- | --- |
| Rows are observable in clean row-stress fixtures. | Rows prove full continuum geometry. |
| Derived column proxies are observable under Lane A. | Lane A has direct column-H spark gating. |
| Mechanical refinement preserves old boundary columns. | Every refinement is identity fission. |
| D8 supports configured-window child-basin persistence. | Landscape-general identity emergence is proven. |
| D7 supports true-column semantic usefulness in clean fixtures. | Rows/random triples can never reconstruct. |
| Experiment F supports edge-label path disagreement. | Path disagreement proves row/column semantics. |
| D1-D8 partially reject H0. | H0 is globally dead for every artifact. |

## Common Mistakes

### Mistake 1: Treating Column Proxy As Column-H Gating

Under Lane A, column cancellation is derived. It can be analyzed, scored, and
compared, but it did not directly trigger a spark unless the run explicitly
uses Lane B and records direct column-H proxy-branch gate evidence.

### Mistake 2: Treating Refinement As Identity Fission

Expansion creates mechanical degrees of freedom. Identity requires persistent
post-event basin structure.

### Mistake 3: Treating Path Disagreement As Row/Column Evidence

Experiment F supports multi-label edge semantics. It is not direct evidence
that rows or columns matter.

### Mistake 4: Treating Exact G/Split As Semantic Superiority

Exact reconstruction proves the operator works. D7's grouping comparison is
what supports true-column semantic usefulness.

### Mistake 5: Treating Clean Fixtures As Landscape-General Results

The completed artifacts are controlled fixtures. Landscape/seed robustness is
future work.

## Minimal Fixture Recipes

### To Test Row Behavior

- Use a central node with controlled port occupancy.
- Perturb one full row with energy-matched deltas.
- Compare balanced, row-permuted, column-permuted, transpose, and random-relabel
  controls.
- Claim row-resolved response, not total `K` dominance.

### To Test Column Behavior

- Build column-local cancellation or pressure.
- Preserve row energy where possible.
- Compare column permutation, row permutation, transpose, and random grouping.
- Under Lane A, call this a derived proxy. Direct column-H evidence requires
  an explicit `grc9v3_column_h_assisted` Lane B run.

### To Test Saturation

- Match degree-7, degree-8, degree-9 stressed, and degree-9 stable controls.
- Record active degree, gradient norm, signed Hessian minimum, candidate count,
  refinement count, and budget.
- Keep direct column-H and near-saturation claims blocked under Lane A.

### To Test Refinement Memory

- Start from a refinement event with an expansion payload.
- Extract old boundary edge, old parent port, old column, new module endpoint,
  new endpoint port, and budget.
- Compare true old column against row labels, random columns, random triples,
  and degree/adjacency where meaningful.

### To Test Port Interaction

- Perturb all nine canonical ports with matched magnitude and neighbor shell.
- Fit additive row+column and port/intersection models.
- Report whether interaction is required for each target separately.
- Include a runtime control where interaction is not required if available.

### To Test Identity Emergence

- Require a refinement event.
- Track post-event sink/basin rows.
- Apply persistence-window and minimum-basin-mass thresholds.
- Require lineage and budget preservation.
- Do not count expansion alone.

## Designing Future Fixtures

Before adding a new fixture, decide which artifact class you are testing:

- row/differential
- column/interface/refinement
- port/edge-local
- saturation/capacity
- multiscale reconstruction
- identity/basin persistence
- edge-label path behavior
- motion-observer behavior

Then choose controls that can actually falsify the claim:

- structured row permutations
- structured column permutations
- row/column transpose
- sampled non-factorized relabels
- random triples
- degree/adjacency baseline
- shuffled target controls, when a reusable dataset exists
- persistence-window and basin-mass sensitivity, for identity claims

If the artifact surface is unavailable, record it as blocked or inconclusive.
Do not add runtime behavior inside an observational experiment track to make a
claim pass.

## Follow-Up Surfaces

Completed post-pass comparison:

- Lane C comparison of Lane A against direct `grc9v3_column_h_assisted`
  proxy-branch gating:
  `lane_c_comparison_complete_direct_column_h_branch_delta_observed_with_boundaries`

These require explicit future work:

- degree-8 near-saturation policy
- inflow-weighted transfer lane
- persisted checkpoint-window identity persistence
- reusable motion-loader full port histories
- landscape/seed robustness suite
- broader or exhaustive S9 relabel sampling

Treat these as future implementation or robustness candidates, not as hidden
claims from the completed Lane A artifact family.

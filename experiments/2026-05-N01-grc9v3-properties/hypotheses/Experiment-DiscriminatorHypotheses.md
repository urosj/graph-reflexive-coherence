# Experiment Hypotheses

The following are **stronger, more falsifiable hypotheses** that test not only whether rows/columns/ports have effects, but whether the **specific 3×3 factorization is necessary, predictive, and better than plausible alternatives**.

The strongest additions are these.

## 1. Factorization hypothesis

### Hypothesis

```text
GRC9V3 behavior is equivariant under row permutations and column permutations,
but not under arbitrary nine-port relabeling.
```

In other words, the relevant symmetry group should look like:

```text
S3_rows × S3_columns
```

not:

```text
S9_ports
```

### Why this is better than the original hypothesis

The original question asks whether rows, columns, and ports have meaning. This hypothesis makes that sharper:

```text
If the 3×3 structure is real, then preserving the 3×3 factorization should
preserve behavior up to relabeling.

If ports are merely nine bounded-degree slots, then arbitrary relabeling should
behave just as well.
```

This directly tests whether GRC9V3 is a **factorized substrate** rather than a nine-port graph with labels.

The GRC-9 document explicitly says the ports are organized as a 3×3 bundle with mode rows and polarity columns, not merely as nine unordered edge slots .

### Test method

Run matched fixtures under:

```text
original port assignment
row-permuted assignment
column-permuted assignment
row+column permuted assignment
arbitrary S9 port relabeling
```

Then compare runtime artifacts after undoing the corresponding permutation.

### Expected result

If the factorization matters:

```text
row/column-preserving relabels should preserve the semantic response
arbitrary S9 relabels should degrade or scramble it
```

### Observation directive

Telemetry must support reconstruction of:

```text
port id
row id
column id
edge endpoint ports
node/edge response artifacts
event artifacts, if events occur
```

The experiment should report an **equivariance error**:

```text
equivariance_error =
    distance(original_artifact,
             inverse_permuted_artifact)
```

This is one of the cleanest family-level tests.

## 2. Row/column transpose non-equivalence hypothesis

### Hypothesis

```text
Swapping rows and columns changes behavior.
```

More specifically:

```text
row-local perturbations should affect geometry/differential response
column-local perturbations should affect interface/routing/refinement response
```

A transposed version of the same fixture should not behave equivalently.

### Why this is better

This tests whether rows and columns are **roles**, not merely two ways of grouping the same nine ports.

If the row/column distinction is only cosmetic, then transposing the 3×3 bundle should produce equivalent results. If the distinction is real, transposition should move the system into the wrong semantic regime.

The GRC-9 text assigns rows to the local geometric/directional basis used in the coherence tensor, while columns are assigned to interface handling, deterministic refinement, and coarse-graining .

### Test method

Create fixtures where the same numerical pattern is applied in two forms:

```text
row-local pattern:
    concentrated across one row

column-local pattern:
    same values transposed into one column
```

Then run both.

### Expected result

A row-local fixture should produce stronger evidence in:

```text
K anisotropy
row-resolved gradient
row-resolved flux stress
row Hessian proxy
```

A column-local fixture should produce stronger evidence in:

```text
column cancellation
boundary pressure
spark eligibility
routing/refinement consequences
coarse-graining profile shifts
```

### Observation directive

Telemetry must support separating:

```text
row-resolved response
column-resolved response
event/routing/refinement response
```

If the artifacts do not expose these distinctions, the result is inconclusive rather than failed.

## 3. Nine-port minimality hypothesis

### Hypothesis

```text
The 3×3 nine-port structure is the minimal substrate that simultaneously supports:

1. row-resolved anisotropic geometry,
2. column-preserving interface/refinement,
3. deterministic central spark wiring,
4. invertible column coarse-graining,
5. finite local saturation before refinement.
```

### Why this is important

This goes beyond asking:

```text
Do nine ports work?
```

It asks:

```text
Why nine?
```

The GRC-9 document gives a theoretical reason: 3×3 is presented as the smallest square that preserves the row/column semantics, provides a unique center port, supports deterministic spark wiring, and yields a three-branch multiscale ladder .

The experiment should test whether those advantages are visible in artifacts.

### Test method

Since the runtime already implements GRC9V3, we should not add new 4×4 or 2×2 runtimes. Instead, use **ablation views** over the existing runtime:

```text
nine ordered ports, but ignore rows/columns
nine ordered ports, but randomize row/column grouping
nine ordered ports, but use row-only grouping
nine ordered ports, but use column-only grouping
true 3×3 grouping
```

These are analysis-layer ablations, not runtime changes.

### Expected result

The true 3×3 grouping should outperform the ablations on combined explanatory power:

```text
predicts row geometry better than unordered ports
predicts refinement/routing better than unordered ports
supports exact G/Split reconstruction better than random triples
preserves lineage better than random grouping
```

### Observation directive

Telemetry must support enough port-level data to compare semantic groupings after the run.

This hypothesis is especially useful because it turns “nine is canonical” into a measurable claim.

## 4. Interface memory hypothesis

### Hypothesis

```text
Columns preserve boundary identity across time and refinement.
```

More concretely:

```text
The parent column of an edge should remain predictive of that edge’s
post-refinement location, child basin participation, or routing role.
```

### Why this is stronger

Column-preserving reassignment can be checked mechanically from the source, but that alone is not enough. The better question is whether column identity remains meaningful **after dynamics continue**.

If columns are true interface families, then a boundary edge’s column should not just determine where it is rewired during a spark. It should continue to predict something about post-spark flow, basin membership, or child identity.

### Test method

Select spark/refinement runs.

For each old boundary edge, record:

```text
parent node
old port
old column
new endpoint after refinement
post-refinement flux
post-refinement basin assignment
post-refinement child/satellite relation
persistence over a window
```

Then measure whether:

```text
old column → post-refinement role
```

has predictive power.

A simple analysis could compute:

```text
mutual_information(old_column, post_refinement_basin)
mutual_information(old_column, dominant_route)
mutual_information(old_column, child_satellite)
```

Compare against randomized column labels.

### Expected result

If columns are interface memory carriers:

```text
real columns should predict post-refinement interface behavior
random columns should not
```

### Observation directive

Telemetry must support reconstructing old boundary edges, their ports, their reassigned endpoints, and post-refinement basin/flux behavior.

This is one of the best hypotheses for testing whether columns are more than deterministic wiring labels.

## 5. Representational bottleneck hypothesis

### Hypothesis

```text
Nine-port saturation marks chart exhaustion, not merely high graph degree.
```

A saturated unstable node should behave qualitatively differently from an unsaturated unstable node.

### Why this matters

The GRC-9 spark rule intentionally ties refinement to finite representational capacity. A spark is not merely “large stress”; it is stress at a locally exhausted chart. The core rule uses active degree 9 as canonical spark eligibility, with near-saturation described as an optional extension .

This is a stronger hypothesis because it tests the **use of nine as capacity**, not just the use of nine as a convenient maximum degree.

### Test method

Construct matched nodes with:

```text
degree 7 stressed
degree 8 stressed
degree 9 stressed
degree 9 unstressed
```

Try to match:

```text
local C
net flux
row stress
column cancellation
sink status
neighborhood size
```

### Expected result

The degree-9 stressed case should become refinement-eligible under canonical rules, while degree-7 and degree-8 cases should not, unless an explicitly configured near-saturation policy exists.

The degree-9 unstressed case should not refine merely because it is full.

### Observation directive

Telemetry must support:

```text
active degree
inactive ports
sink status
spark eligibility
spark event
refinement event
budget before/after
post-event basin structure
```

This tests whether nine ports act as a **finite local chart capacity**.

## 6. Port interaction hypothesis

### Hypothesis

```text
Some behaviors are not explainable by row effect + column effect alone.
The individual port, as a row-column intersection, carries interaction behavior.
```

Formally:

```text
response(a,b) ≠ row_effect(a) + column_effect(b)
```

for some runtime artifacts.

### Why this is useful

The original hypotheses say:

```text
rows matter
columns matter
ports are intersections
```

This hypothesis makes the third claim testable.

If a port is only a bookkeeping intersection, then row and column effects should explain most behavior additively. If ports are true interaction sites, then some edge or flux behavior should require a row×column interaction term.

### Test method

Run a 3×3 factorial perturbation experiment.

For each port `(a,b)`, apply a matched perturbation:

```text
stress port (1,1)
stress port (1,2)
...
stress port (3,3)
```

Fit an analysis model:

```text
artifact_response[a,b]
    = global_mean
    + row_effect[a]
    + column_effect[b]
    + interaction_effect[a,b]
```

### Expected result

A strong port-level result would show:

```text
interaction_effect[a,b] is significant for some artifacts
```

Especially interesting artifacts:

```text
edge flux reversal
dominant route selection
spark-column diagnostic
basin boundary movement
post-refinement edge role
```

### Observation directive

Telemetry must expose enough port-specific runtime data to compare individual `(row,column)` intersections.

This is probably the best way to test whether “port” has its own observable role, beyond row and column grouping.

## 7. Predictive separation hypothesis

### Hypothesis

```text
Rows predict geometric response better than columns.
Columns predict interface/refinement response better than rows.
Ports predict edge-local response better than either alone.
```

### Why this is better

This reframes the experiment as a prediction problem.

Instead of asking:

```text
Do rows and columns matter?
```

ask:

```text
Which grouping best predicts which class of artifact?
```

That gives a clearer success criterion.

### Test method

For a set of runs, build simple post-processing predictors:

```text
row-only features
column-only features
port-level features
degree/adjacency-only features
random grouping features
```

Then compare their ability to predict:

```text
K anisotropy
row gradient signatures
flux stress
boundary pressure
spark eligibility
refinement event
post-refinement child basin
dominant path class
```

### Expected result

The expected pattern is:

| Artifact class                        | Best predictor            |
| ------------------------------------- | ------------------------- |
| Geometric/differential response       | Row features              |
| Interface/routing/refinement response | Column features           |
| Edge-local behavior                   | Port features             |
| Generic activity level                | Degree/adjacency features |

### Observation directive

Telemetry must support deriving artifact-level target variables from existing runtime outputs.

This hypothesis is valuable because it allows negative results to be informative. For example:

```text
If degree-only features predict everything, GRC9V3 semantics are weak.
If row/column/port features predict different artifact classes, semantics are strong.
```

## 8. Column coarse-graining sufficiency hypothesis

### Hypothesis

```text
Column coarse-graining is the correct lossless multiscale view for
nonnegative port-attached interface fields, while row coarse-graining is not
equally suited for refinement/interface reconstruction.
```

### Why this extends the current hypotheses

The original plan already includes G/Split reconstruction. The stronger hypothesis is comparative:

```text
column grouping should outperform row grouping and random triple grouping
for interface/refinement fields.
```

The GRC-9 document defines invertible column coarse-graining and Split for nonnegative port-attached scalar fields, and explicitly separates exact signed-flux reconstruction through positive/negative decomposition from lossy compressed signed diagnostics .

### Test method

At checkpoints, collect eligible nonnegative port fields:

```text
conductance
absolute flux
positive flux
negative flux
curvature/cancellation magnitude if exposed
functional coupling magnitude if exposed
```

Compare reconstruction using:

```text
true columns
true rows
random triples
unordered nine-port total only
```

### Expected result

For nonnegative fields:

```text
true column G/Split should reconstruct exactly
```

For compressed representations:

```text
signed flux should fail when signs mix inside a column
J+ / J- decomposition should reconstruct exactly
```

For semantic usefulness:

```text
column grouping should be more useful for post-refinement interface analysis
than row grouping or random grouping
```

### Observation directive

Telemetry must expose port-attached scalar fields and port-to-column mapping.

## 9. Spark-outcome emergence hypothesis

### Hypothesis

```text
A GRC9V3 spark creates mechanical degrees of freedom, but child identities
emerge only if post-event attractor basins persist.
```

### Why this is important

This is a guardrail hypothesis. It prevents the experiments from overclaiming.

The RC identity text defines identity as a stable attractor basin, not a node label or a graph rewrite . The GRC-9 text also distinguishes mechanical expansion from post-event child identity emergence; the expansion creates a module, while the reflexive dynamics may later produce stable child sinks .

So the better hypothesis is not:

```text
spark creates children
```

but:

```text
spark creates representational room, and only persistent post-event basins
count as child identities
```

### Test method

For each spark/refinement event, classify outcomes:

```text
mechanical refinement only
transient extra sink
persistent child identity
multi-child fission
collapse back to one identity
```

### Expected result

A mature GRC9V3 result would show that some sparks produce persistent child basins, while others merely refine the substrate.

That would support the distinction between:

```text
mechanical event
identity event
```

### Observation directive

Telemetry must support:

```text
pre-event sink/basin
refined parent
created module nodes
post-event sinks
post-event basins
basin mass
persistence window
lineage relation
```

This should be part of the spec even if the first tranche does not emphasize identity claims.

## 10. Observer-sufficiency hypothesis

### Hypothesis

```text
A row-restricted observer can predict geometric response better than
interface/refinement response.

A column-restricted observer can predict interface/refinement response better
than geometric response.

Neither restricted observer can reliably predict full collapse/spark outcomes
when global basin structure matters.
```

### Why this is useful

This connects the nine-port experiment to the broader RC claim that global dynamics can be deterministic while local observers remain unable to predict outcomes from partial information .

It also gives rows and columns an observer-theoretic interpretation:

```text
rows = local differential visibility
columns = interface/refinement visibility
full port graph = stronger but still not omniscient visibility
```

### Test method

Define analysis-only observers:

```text
row observer:
    sees row-grouped local artifacts only

column observer:
    sees column-grouped local artifacts only

port observer:
    sees full local port artifacts

global observer:
    sees full graph artifacts
```

Ask each observer to predict:

```text
next-step K anisotropy
next-step dominant flux
spark eligibility
refinement event
post-event child basin outcome
collapse winner, if applicable
```

### Expected result

The expected pattern:

```text
row observer best for geometry
column observer best for interface/refinement
port observer best for local routing
global observer required for reliable basin/collapse outcome
```

### Observation directive

Telemetry must support creating restricted observation views from existing artifacts.

This is not necessary for the first experiment tranche, but it could become a very good second-stage experiment.

## Recommended additions to the spec

I would add the following as the core “better hypotheses” section.

```text
H0: Anonymous-port null
    GRC9V3 behavior is explainable by degree, adjacency, conductance, and
    scalar coherence alone. Rows, columns, and ports add no predictive power.

H1: Factorization
    Runtime artifacts are equivariant under S3 row and S3 column permutations,
    but not under arbitrary S9 port relabeling.

H2: Role separation
    Rows predict geometric/differential artifacts better than columns.
    Columns predict interface/routing/refinement artifacts better than rows.
    Ports predict edge-local artifacts better than either grouping alone.

H3: Transpose non-equivalence
    Swapping rows and columns changes the artifact class affected by the same
    numerical perturbation.

H4: Representational bottleneck
    Full nine-port saturation acts as chart exhaustion and gates refinement
    under canonical rules.

H5: Interface memory
    Parent column labels remain predictive of post-refinement boundary,
    routing, and child-basin behavior.

H6: Port interaction
    Some artifacts require row×column interaction terms and cannot be explained
    additively by row effect plus column effect.

H7: Multiscale sufficiency
    Column G/Split is the correct lossless coarse-graining for eligible
    nonnegative interface fields, while signed flux requires J+/J- channels.

H8: Emergent identity
    Refinement is not itself identity fission. A child identity is present only
    when post-event sink/basin artifacts persist.
```

The three I would prioritize beyond the original plan are:

```text
1. Factorization / S3×S3 versus S9.
2. Predictive separation: rows predict geometry, columns predict interface.
3. Interface memory across refinement.
```

Those are stronger than the initial hypotheses because they can clearly fail. They also avoid relying on source-authored intent: the claim has to show up as permutation behavior, predictive power, or post-refinement lineage in runtime artifacts.

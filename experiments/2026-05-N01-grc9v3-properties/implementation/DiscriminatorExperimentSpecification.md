# D1–D8 Discriminator Experiment Specification

## Common directive for all D experiments

Each discriminator should use this shared rule:

```text
Telemetry is an observability directive, not a fixed field list.

For every claimed observation, the implementation must identify which existing
runtime artifacts, checkpoints, telemetry records, observer records, edge labels,
or event logs support the claim.

If the observation cannot be reconstructed from existing artifacts, the result
is blocked or inconclusive for that claim.

Experiment code must not add new runtime behavior to src/pygrc.
```

For the May 2026 GRC9V3 property experiments, the baseline runtime lane is
`current_hybrid_signed_hessian`: saturation plus basin-interior and
signed-Hessian degeneracy evidence. A direct per-column `H_s^(b)` spark gate is
a separate canonical-column-H lane if it is later implemented and tested. D
experiments must not treat a derived column-H/cancellation proxy as direct
runtime gating evidence.

Each experiment should produce:

```text
1. fixture description
2. run parameters
3. random seed, if applicable
4. port mapping used in the run
5. perturbation or transform applied
6. artifact extraction method
7. comparison/control method
8. pass/fail/inconclusive classification
9. explanation of what the result supports or does not support
```

A recurring rule:

```text
No claim should be supported by source intent alone.
The claim must be visible in runtime artifacts or derived from runtime artifacts.
```

---

# D1 — Factorization discriminator

## Hypothesis

```text
GRC9V3 behavior respects the 3×3 factorization.

Behavior should transform predictably under row-preserving and column-preserving
relabelings, but should not remain equally interpretable under arbitrary S9
nine-port relabeling.
```

More compactly:

```text
Expected symmetry:
    structured row/column transforms preserve the semantic response.

Rejected symmetry:
    arbitrary nine-port relabeling preserves the same semantic response.
```

## Purpose

D1 tests whether the substrate is actually a **3×3 factored substrate** rather than merely a node with nine anonymous incident slots.

This is stronger than saying:

```text
Rows matter.
Columns matter.
```

It asks:

```text
Does the runtime response depend on the row/column factorization in a way that
survives structured relabeling but fails under arbitrary relabeling?
```

## Why this method is chosen

Permutation tests are one of the cleanest ways to distinguish semantic structure from label coincidence.

If rows and columns are real semantic axes, then a row permutation should move row-sensitive artifacts in the corresponding way, and a column permutation should move column-sensitive artifacts in the corresponding way. If ports are merely arbitrary labels, then random relabeling should perform just as well.

The GRC-9 text explicitly treats the nine ports as a 3×3 bundle, not as an unordered set of nine slots. Rows provide the mode basis for row-wise geometry, while columns provide the stable interface families. 

## Experiment design

Run a base fixture and transformed fixtures.

### Required fixtures

Use at least one fixture with:

```text
a saturated or near-saturated central node
all nine ports auditable
nontrivial row variation
nontrivial column variation
nonzero edge flux or reconstructable flux proxy
```

Preferably use more than one fixture:

```text
D1a: non-sparking core-loop fixture
D1b: spark-eligible fixture
D1c: post-refinement fixture
```

This matters because pure row/column dynamics and spark expansion may have different symmetry expectations.

### Transform classes

Run the same fixture under:

```text
T0: original port assignment

T_row:
    permute rows 1,2,3 while preserving columns

T_col:
    permute columns 1,2,3 while preserving rows

T_row_col:
    apply both a row and column permutation

T_s9:
    arbitrary degree-preserving nine-port relabeling that does not preserve
    row/column factorization

T_random_triples:
    regroup ports into random triples and analyze as if they were rows or columns
```

The arbitrary `S9` transform should preserve ordinary graph degree and edge count. It should only break the semantic 3×3 organization.

### Artifact comparison

For each artifact class, compute a normalized equivariance error.

```text
equivariance_error(T, artifact_class)
    =
distance(
    artifact_base,
    inverse_transform(artifact_transformed)
)
/
scale(artifact_base)
```

Different artifact classes need different distances:

```text
scalar/vector artifacts:
    normalized L2 error, cosine distance, rank correlation

event artifacts:
    event match/mismatch, timing difference, Jaccard overlap

path artifacts:
    edge-overlap distance, path-cost difference, route-class difference

basin artifacts:
    adjusted mutual information, Jaccard overlap, basin-mass error

refinement artifacts:
    boundary-edge mapping agreement, lineage agreement, budget error
```

### Important scope split

D1 should report two symmetry regimes separately:

```text
core-loop factorization:
    row/column permutations before topology events

mechanical-refinement convention:
    behavior after spark expansion
```

The reason is that the canonical spark module uses a fixed center convention around port 5 and the column-2 spine. That deterministic wiring convention may intentionally break some naive full-row/full-column symmetry at the mechanical event layer. Therefore, post-refinement non-equivariance should not automatically be interpreted as failure. It should be classified as:

```text
semantic non-equivariance
```

or:

```text
canonical-wiring convention effect
```

depending on which artifact differs.

## Observation directive

The implementation must identify existing artifacts sufficient to reconstruct:

```text
port id r
row a
column b
edge endpoint ports
node states
edge weights/conductances
fluxes or flux proxies
row-resolved artifacts, if available or reconstructable
column-resolved artifacts, if available or reconstructable
spark/refinement events, if present
boundary reassignment records, if present
basin/sink records, if present
```

## Supporting result

D1 supports the factorization claim if:

```text
row transforms preserve row-sensitive artifacts after inverse relabeling
column transforms preserve column-sensitive artifacts after inverse relabeling
combined row/column transforms preserve the appropriate transformed artifacts
arbitrary S9 relabeling produces larger semantic error
random triple groupings perform worse than true rows/columns
```

## Weakening or refuting result

D1 weakens the factorization claim if:

```text
arbitrary S9 relabeling preserves behavior as well as structured relabeling
row/column transforms do not transform artifacts predictably
degree-only or adjacency-only summaries explain the results equally well
random triples predict row/column artifacts as well as true groupings
```

## Expected output

```text
d1_equivariance_matrix.csv
d1_artifact_distance_report.md
d1_transform_pair_records.jsonl
d1_blocked_observations.md
```

The report should include a matrix like:

| Transform              |   Row geometry error | Column interface error | Port flux error | Event mapping error |
| ---------------------- | -------------------: | ---------------------: | --------------: | ------------------: |
| Row permutation        |         low expected |   neutral/low expected |    low expected |         conditional |
| Column permutation     | neutral/low expected |           low expected |    low expected |         conditional |
| Row+column permutation |         low expected |           low expected |    low expected |         conditional |
| S9 random relabel      |        high expected |          high expected |   high expected |       high expected |

---

# D2 — Predictive role separation discriminator

## Hypothesis

```text
Rows, columns, and ports predict different classes of runtime artifact.

Rows should predict geometric/differential artifacts better than columns.
Columns should predict interface/routing/refinement artifacts better than rows.
Ports should predict edge-local artifacts better than either row-only or
column-only summaries.
Degree/adjacency-only features should not explain everything.
```

## Purpose

D2 turns the semantic hypothesis into a prediction problem.

Instead of asking:

```text
Did a row effect occur?
```

it asks:

```text
Which grouping best predicts each kind of runtime behavior?
```

This gives a stronger discriminator against H0.

## Why this method is chosen

A single successful row or column fixture can be accidental. A predictive separation test is stronger because it asks whether rows, columns, and ports have **different explanatory power across many runs**.

This is especially useful if the runtime is nonlinear. Nonlinear systems can produce surprising local effects. D2 checks whether those effects sort into the expected artifact classes.

## Experiment design

Build a dataset from the completed O1–O4 and D experiments.

Each sample should correspond to a local node/time/window observation, for example:

```text
node i at timestep k
node i over window [k, k + T]
edge e over window [k, k + T]
spark candidate s before/after event
refined parent s and its post-event module
```

### Feature families

Construct analysis-only feature groups from existing artifacts.

```text
degree/adjacency baseline features:
    active degree
    total incident weight
    total flux magnitude
    mean neighbor coherence
    variance of neighbor coherence
    ordinary graph neighborhood summaries

row features:
    per-row coherence mismatch
    per-row conductance sum
    per-row flux stress
    per-row gradient proxy
    per-row K contribution, if available or reconstructable

column features:
    per-column conductance sum
    per-column flux balance
    per-column cancellation proxy
    per-column H proxy
    per-column boundary pressure
    per-column occupancy

port features:
    individual (row, column) edge values
    port-level flux
    port-level conductance
    port-level neighbor coherence
    port-level route or path participation
```

Also include controls:

```text
random row triples
random column triples
arbitrary S9 port relabeling
degree-only features
shuffled target labels
```

### Target artifact classes

Use targets that are already visible or reconstructable.

```text
geometric/differential targets:
    K anisotropy
    row-resolved gradient response
    row-resolved flux stress
    Hessian-like row signature

interface/routing/refinement targets:
    column cancellation
    boundary pressure
    spark eligibility
    spark/refinement event
    boundary edge reassignment
    post-refinement routing role

edge-local targets:
    dominant port
    flux reversal
    strongest edge
    path membership
    route class

identity-level targets:
    sink status
    basin assignment
    child-basin persistence
    attractor-count change
```

### Predictive comparison

Use transparent analysis methods. The goal is explanation, not model sophistication.

Acceptable methods:

```text
linear or ridge regression for scalar targets
logistic regression for binary targets
multinomial logistic regression for categorical targets
decision stumps or shallow trees for interpretability
mutual information for small datasets
rank correlation for monotonic relationships
```

Use cross-validation by fixture, not just random sample splitting, so the test does not merely memorize one graph.

```text
train on some fixtures
test on held-out fixtures
compare feature-family performance
```

## Observation directive

The implementation must identify existing artifacts sufficient to derive:

```text
row features
column features
port features
degree/adjacency baseline features
target artifact values
run labels
fixture labels
seed labels
time/window labels
```

If any feature family cannot be derived from existing artifacts, report that family as blocked for the relevant target.

## Supporting result

D2 supports predictive role separation if the score ordering looks like:

| Target class                 | Expected strongest feature family    |
| ---------------------------- | ------------------------------------ |
| Geometric/differential       | Rows                                 |
| Interface/routing/refinement | Columns                              |
| Edge-local                   | Ports                                |
| Generic activity             | Degree/adjacency                     |
| Identity-level persistence   | Port + column + global basin context |

A strong result would be:

```text
row features outperform column and degree features on geometry targets
column features outperform row and degree features on interface/refinement targets
port features outperform row-only and column-only features on edge-local targets
random groupings underperform true row/column groupings
degree-only features do not dominate all targets
```

## Weakening or refuting result

D2 weakens the semantic claim if:

```text
degree/adjacency features predict all artifact classes as well as rows/columns
random triples perform as well as true rows/columns
rows and columns have indistinguishable predictive value for all targets
port-level features add no explanatory value beyond degree/adjacency
```

## Expected output

```text
d2_feature_family_scores.csv
d2_target_definitions.md
d2_cross_validation_report.md
d2_random_grouping_controls.csv
d2_blocked_observations.md
```

---

# D3 — Row/column transpose discriminator

## Hypothesis

```text
Row/column transpose is not behaviorally equivalent.

A numerical pattern placed row-wise should affect geometric/differential
artifacts differently from the same numerical pattern placed column-wise.
```

## Purpose

D3 tests whether rows and columns are **different roles**, not merely two interchangeable ways to group nine ports.

If rows and columns are cosmetic, then transposing a 3×3 port pattern should produce equivalent behavior. If rows and columns have distinct runtime meaning, the transposed pattern should move the effect into a different artifact class.

## Why this method is chosen

Transpose is a sharper test than ordinary row or column permutation.

A row permutation preserves the fact that a pattern is row-local. A column permutation preserves the fact that a pattern is column-local. A transpose changes the kind of localization:

```text
row-local pattern → column-local pattern
column-local pattern → row-local pattern
```

That makes it a direct test of role separation.

## Experiment design

Construct paired fixtures from a 3×3 port matrix `M`.

```text
D3_base:
    apply M to the central node’s port-attached field

D3_transpose:
    apply Mᵀ to the same field
```

The field may be:

```text
neighbor coherence C_neighbor
conductance/weight
initial flux proxy
edge-label magnitude
controlled perturbation ΔC
```

Use several patterns:

```text
single row high
single column high
diagonal pattern
anti-diagonal pattern
rank-1 row × column pattern
mixed sign/cancellation pattern, if applicable
```

The paired fixtures should be matched for:

```text
total perturbation magnitude
squared perturbation magnitude
number of affected ports
degree
neighbor shell structure
initial budget
seed
```

### Two phases

Run D3 in two phases.

```text
D3a: pre-event dynamics
    Run for a short window where no spark/refinement should occur.
    Goal: isolate row/column effects in ordinary dynamics.

D3b: event-capable dynamics
    Run longer or under stress so that spark/refinement may occur.
    Goal: test whether transpose changes interface/refinement behavior.
```

## Artifact comparison

Define two response scores.

```text
geometry_response_score:
    magnitude of row-resolved K/gradient/Hessian/flux-stress response

interface_response_score:
    magnitude of column-resolved cancellation/routing/boundary/refinement response
```

Then compare:

```text
base row-local pattern:
    expected geometry_response_score high

transposed column-local pattern:
    expected interface_response_score high
```

A useful derived quantity:

```text
role_separation_index =
    geometry_response_score(row_local)
    +
    interface_response_score(column_local)
    -
    geometry_response_score(column_local)
    -
    interface_response_score(row_local)
```

Positive values support role separation.

## Controls

```text
symmetric pattern M = Mᵀ:
    transpose should not change much

isotropic pattern:
    neither row nor column response should dominate

random S9 relabel:
    should weaken interpretability

row permutation of M:
    should preserve row-local interpretation

column permutation of M:
    should preserve column-local interpretation
```

## Observation directive

The implementation must identify existing artifacts sufficient to reconstruct:

```text
port-attached input pattern
row-local response
column-local response
geometry/differential artifact class
interface/routing/refinement artifact class
event occurrence and timing, if any
```

## Supporting result

D3 supports row/column role separation if:

```text
M and Mᵀ produce different dominant artifact classes
row-local M affects geometry/differential artifacts more strongly
column-local Mᵀ affects interface/routing/refinement artifacts more strongly
symmetric or isotropic controls do not falsely show role separation
random relabeling weakens the pattern
```

## Weakening or refuting result

D3 weakens role separation if:

```text
M and Mᵀ are behaviorally equivalent across artifact classes
row-local and column-local patterns produce the same response distribution
random relabeling produces the same result as true transpose
degree/adjacency baselines explain the difference
```

## Expected output

```text
d3_transpose_pair_table.csv
d3_role_separation_scores.csv
d3_pre_event_report.md
d3_event_capable_report.md
d3_blocked_observations.md
```

---

# D4 — Saturation / representational bottleneck discriminator

## Hypothesis

```text
Nine-port saturation acts as local chart exhaustion.

A saturated signed-Hessian-unstable node should become refinement-eligible in
the baseline GRC9V3 lane. An unsaturated unstable node should not behave the
same way under baseline GRC9V3 spark rules.
```

## Purpose

D4 tests whether the nine-port limit functions as **finite local representational capacity**, not merely as graph degree.

The baseline GRC9V3 spark trigger ties refinement eligibility to active degree
9 plus basin-interior and signed-Hessian degeneracy evidence. The GRC9
column-H diagnostic is important, but in this experiment family it is direct
gating evidence only for a separately implemented canonical-column-H lane.

## Why this method is chosen

This test separates two conditions that are easy to conflate:

```text
local stress
```

versus:

```text
local stress at exhausted port capacity
```

If nine ports are a real chart capacity, then stress alone should not be sufficient under canonical rules. Full local saturation should matter.

## Experiment design

Construct matched sink-candidate fixtures.

```text
D4_7_stressed:
    active degree 7
    local stress/instability present

D4_8_stressed:
    active degree 8
    local stress/instability present

D4_9_stressed:
    active degree 9
    comparable local stress/instability present

D4_9_stable:
    active degree 9
    no qualifying instability/cancellation

D4_7_or_8_stable:
    active degree 7 or 8
    no qualifying instability/cancellation
```

If the runtime already supports near-saturation policy, keep it separate:

```text
D4_8_near_saturation_policy:
    active degree 8
    near-saturation extension enabled or configured
```

Do not mix canonical and near-saturation results.

## Matching requirements

Try to match:

```text
central node coherence
neighbor coherence distribution
total incident conductance
total flux magnitude
row stress profile
column cancellation profile
sink status
seed
```

Exact matching may be impossible because active degree differs. In that case, report the mismatch explicitly.

Useful normalizations:

```text
per-port stress
total stress
mean incident stress
max column stress
min |H_column|
```

## Controls

```text
same stress without saturation
same saturation without stress
same degree but not a sink
same degree and stress under random port relabeling
same fixture with spark/refinement disabled only if runtime already supports it
```

The last control should not require adding new runtime behavior. Use it only if already available.

## Observation directive

The implementation must identify existing artifacts sufficient to reconstruct:

```text
active degree
inactive ports
sink status
local instability proxy
signed-Hessian degeneracy evidence
column diagnostic or reconstructable H proxy, marked as derived unless a
canonical-column-H lane exists
spark eligibility
spark trigger
refinement event
event timestep
budget before and after event
created module, if any
post-event sink/basin structure
```

## Supporting result

D4 supports the bottleneck hypothesis if:

```text
degree 7 stressed does not trigger canonical refinement
degree 8 stressed does not trigger canonical refinement
degree 9 signed-Hessian-stressed becomes eligible and may trigger refinement
degree 9 Hessian-stable does not trigger merely because it is full
column-H effects are reported as derived proxies unless a canonical-column-H
lane exists
near-saturation behavior, if present, is reported as an extension
budget remains preserved across any refinement event
```

## Weakening or refuting result

D4 weakens the bottleneck hypothesis if:

```text
degree 7 or 8 stressed nodes refine under canonical rules
degree 9 stressed nodes do not become distinguishable from degree 7/8
degree 9 stable nodes refine simply because full
spark eligibility cannot be audited from artifacts
```

## Expected output

```text
d4_saturation_gate_table.csv
d4_spark_eligibility_report.md
d4_budget_audit.csv
d4_near_saturation_extension_report.md
d4_blocked_observations.md
```

---

# D5 — Interface-memory discriminator

## Hypothesis

```text
Parent column labels remain predictive after refinement.

A boundary edge’s parent column should help explain its post-refinement
location, routing role, flux behavior, or child-basin participation.
```

## Purpose

D5 tests whether columns are not just mechanical rewrite labels.

The basic refinement rule already says old boundary edges are reassigned by column. That is necessary, but not enough. D5 asks whether column identity continues to matter **after the system resumes dynamics**.

## Why this method is chosen

A deterministic rewire can be audited mechanically. But a stronger semantic claim is:

```text
column identity carries interface memory across topology change
```

This requires post-event evidence.

If a column label predicts only where the edge is attached immediately after refinement, then columns are mechanical handles. If it also predicts later routing, basin participation, or child identity, then columns are behaving as persistent interface families.

GRC-9 explicitly uses columns for deterministic boundary reassignment during spark expansion. 

## Experiment design

Run or select fixtures where a spark/refinement event occurs.

For each refined parent node `s`, collect the old incident boundary edges before refinement.

For each old boundary edge record:

```text
edge id
outside neighbor
old parent node s
old parent port r
old row a
old column b
old conductance
old flux
old neighbor coherence
old basin assignment
old route/path role, if available
```

Immediately after refinement, record:

```text
new endpoint
new module node
new module port
whether it attached to the expected column satellite
new conductance
new flux
new basin assignment
```

Then continue for a persistence window:

```text
post-refinement window [k_event, k_event + T]
```

Track:

```text
edge flux over time
dominant routing role
basin assignment over time
whether edge participates in a child basin
whether edge remains near the same column-family module region
```

## Analysis

D5 has two levels.

### Level 1: mechanical interface preservation

Audit whether the immediate rewire is column-preserving.

```text
old column b → corresponding satellite/module column b
```

This is a conformance check.

### Level 2: dynamic interface memory

Measure whether old column predicts later post-refinement behavior.

Possible targets:

```text
post_refinement_basin
dominant_route_class
edge_flux_sign_after_T
edge_flux_magnitude_after_T
child_identity_membership
satellite/module region after T
```

Use simple measures:

```text
mutual_information(old_column, target)
classification_accuracy(old_column → target)
conditional_flux_difference_by_column
Jaccard overlap of old-column groups and post-basin groups
```

Compare against:

```text
randomized old column labels
row labels
degree/flux-only controls
random triple groupings
```

## Controls

```text
same parent fixture with no refinement event, if available
random column labels
row labels instead of column labels
random triples
column permutation
seed replay
```

## Observation directive

The implementation must identify existing artifacts sufficient to reconstruct:

```text
refined parent node
old boundary edges
old endpoint ports
old row/column assignment
new module nodes
new endpoint ports
boundary reassignment
post-event edge fluxes
post-event routing/path role, if available
post-event sink/basin assignments
child lineage, if available or reconstructable
```

If post-event basin structure is not visible, D5 can still report mechanical preservation, but dynamic interface memory is blocked.

## Supporting result

D5 supports interface memory if:

```text
old boundary edges are reassigned by column
old column labels predict post-refinement routing or basin behavior
true columns outperform random columns and random triples
column permutation moves the prediction accordingly
row labels do not explain the same interface behavior as well
```

## Weak result

A weak but still useful result is:

```text
The run supports mechanical column-preserving refinement,
but does not support dynamic interface memory.
```

That means the event was auditable, but post-event dynamics did not preserve enough column-specific structure to support the stronger claim.

## Weakening or refuting result

D5 weakens the interface-memory claim if:

```text
old columns do not predict anything beyond immediate deterministic rewiring
random column labels predict post-event behavior equally well
post-event routing/basin behavior is independent of old column
boundary reassignment cannot be audited
```

## Expected output

```text
d5_boundary_lineage_table.csv
d5_column_reassignment_audit.md
d5_interface_memory_scores.csv
d5_random_label_controls.csv
d5_blocked_observations.md
```

---

# D6 — Port-interaction discriminator

## Hypothesis

```text
Some artifacts require row × column interaction terms.

The behavior of port (a,b) is not always reducible to:

    row_effect(a) + column_effect(b)
```

## Purpose

D6 tests whether individual ports matter as intersections.

O1 and O2 test rows and columns separately. D6 tests the third claim:

```text
ports are where row semantics and column semantics meet
```

If a port is only bookkeeping, row and column main effects should explain most port-local behavior. If ports are true intersections, some artifacts should show non-additive row×column interaction.

## Why this method is chosen

A 3×3 factorial perturbation design is the natural test for row/column interaction.

It allows the experiment to decompose response into:

```text
global mean
row main effect
column main effect
row × column interaction effect
residual
```

This avoids over-interpreting one interesting port as special.

## Experiment design

Use a highly symmetric baseline fixture where all nine neighbor shells are as similar as possible.

Baseline requirements:

```text
central node has all nine ports active
neighbor nodes are structurally comparable
initial conductances are comparable
initial coherence differences are controlled
no single neighbor has unrelated special status
```

For each port `(a,b)`, run a matched perturbation:

```text
D6_ab:
    apply the same perturbation to port (a,b)
```

Examples:

```text
increase neighbor coherence at port (a,b)
decrease neighbor coherence at port (a,b)
increase conductance at port (a,b)
initialize a flux imbalance at port (a,b), if supported
```

Use the same perturbation magnitude for all nine ports.

Run multiple seeds or repeated deterministic variants if the runtime has stochastic components.

## Analysis model

For each artifact target `Y`, fit or compute:

```text
Y[a,b] = μ + R[a] + C[b] + ε[a,b]
```

Then compare against:

```text
Y[a,b] = μ + R[a] + C[b] + I[a,b] + ε[a,b]
```

where:

```text
R[a] = row effect
C[b] = column effect
I[a,b] = row × column interaction
```

The interaction signal is:

```text
interaction_residual[a,b]
    =
Y[a,b] - predicted_additive_Y[a,b]
```

For binary or categorical targets, use logistic or categorical equivalents.

### Artifact targets

Good D6 targets include:

```text
port-level flux magnitude
flux sign reversal
dominant outgoing port
dominant path membership
column H sign crossing
spark eligibility contribution
basin boundary movement
post-refinement edge role
```

D6 can also inspect row and column targets, but the primary value is edge-local and port-local behavior.

## Controls

```text
row-only perturbations
column-only perturbations
isotropic all-port perturbation
random S9 relabeling
random triple grouping
neighbor-shell equality audit
perturbation magnitude sweep
```

The neighbor-shell equality audit is important. Without it, a port interaction result may simply reflect that one neighbor was topologically special.

## Observation directive

The implementation must identify existing artifacts sufficient to reconstruct:

```text
which port was perturbed
port-level edge state
row/column assignment
artifact target Y
neighbor shell descriptors
run seed
time window
```

If target artifacts cannot be resolved at port level, D6 is blocked for those targets.

## Supporting result

D6 supports port-intersection semantics if:

```text
interaction terms are non-negligible for some artifacts
interaction terms are stable across seeds or repeated fixtures
interaction pattern transforms predictably under row/column permutations
interaction pattern is degraded by arbitrary S9 relabeling
interaction is not explained by neighbor-shell asymmetry
```

## Weakening or refuting result

D6 weakens port-intersection semantics if:

```text
row + column additive effects explain all port-level artifacts
interaction terms are indistinguishable from noise
random port groupings produce the same interaction structure
interaction is explained by one special neighbor or degree artifact
```

## Expected output

```text
d6_factorial_response_table.csv
d6_additive_vs_interaction_scores.csv
d6_interaction_heatmaps.md
d6_neighbor_shell_audit.csv
d6_blocked_observations.md
```

---

# D7 — Multiscale discriminator

## Hypothesis

```text
Column G/Split is the correct auditable multiscale interface for eligible
nonnegative port-attached fields.

Signed flux requires positive/negative decomposition for exact reconstruction.

Column grouping should align with refinement/interface behavior better than
row grouping or random triple grouping.
```

## Purpose

D7 tests the multiscale part of the 3×3 claim.

The GRC-9 text defines an invertible column coarse-graining operator `G` and `Split` for nonnegative port-attached fields, and separately explains why signed flux requires either positive/negative channels for exact reconstruction or a lossy compressed representation. 

## Important interpretation rule

Exact reconstruction alone is **necessary but not sufficient** to prove semantic column meaning.

Why?

```text
Any partition into triples can reconstruct exactly if it stores both:
    total
    intra-group profile
```

So D7 has two parts:

```text
D7a: mathematical conformance
    Does the implemented analysis reconstruct eligible fields correctly?

D7b: semantic discrimination
    Do true columns align with interface/refinement behavior better than
    rows or random triples?
```

## Experiment design

At selected checkpoints, collect port-attached fields.

Candidate nonnegative fields:

```text
conductance / base weight
absolute flux magnitude
positive flux J+
negative flux J-
functional coupling magnitude, if exposed
curvature/cancellation magnitude, if exposed
edge-label-derived nonnegative quantities
```

For each field `X ≥ 0`, compute:

```text
G(X) = (column_total, intra_column_profile)
X_reconstructed = Split(G(X))
reconstruction_error = ||X - X_reconstructed||
```

For signed flux `J`, test two routes:

```text
lossless:
    J+ = max(J, 0)
    J- = max(-J, 0)
    reconstruct J = Split(G(J+)) - Split(G(J-))

compressed:
    store signed column total and absolute profile
    reconstruct approximately
```

## Required checkpoint classes

Use diverse checkpoints:

```text
ordinary pre-event checkpoint
near-spark checkpoint
immediate post-refinement checkpoint
later post-refinement checkpoint
zero-column case
single-active-port column case
mixed-sign flux column case
dense all-port case
```

## Semantic grouping comparison

Compare true columns against:

```text
true rows
random triples
S9-random grouping
single nine-port total
```

For exact total+profile reconstruction, rows and random triples may also reconstruct. That is not the semantic test.

The semantic test asks which grouping better supports:

```text
boundary reassignment audit
post-refinement edge lineage
interface-memory prediction
column cancellation diagnostics
routing/refinement targets
```

Expected:

```text
true columns should align better with interface/refinement artifacts
than rows or random triples
```

## Controls

```text
nonnegative fields with zero totals
signed fields with all same sign in each column
signed fields with mixed signs inside a column
pre/post topology event
randomized port labels
randomized field values preserving totals
```

## Observation directive

The implementation must identify existing artifacts sufficient to reconstruct:

```text
port-attached field X
port row and column
edge endpoint port
field sign, if signed
checkpoint timestep
topology event context
boundary reassignment context, if used
```

If no eligible port-attached field is visible, D7 is blocked for that field.

## Supporting result

D7 supports the multiscale discriminator if:

```text
eligible nonnegative fields reconstruct with near-zero numerical error
J+/J- signed flux reconstruction is near-exact
compressed signed flux reconstruction fails exactly when signs mix within a column
true columns align with refinement/interface behavior better than rows/random triples
post-refinement column grouping remains auditable
```

## Weakening or refuting result

D7 weakens the multiscale claim if:

```text
eligible nonnegative fields cannot be reconstructed
signed flux exactness fails even with J+/J-
column grouping cannot be audited from artifacts
random triples align with interface/refinement behavior as well as true columns
post-refinement mappings lose column traceability
```

## Expected output

```text
d7_reconstruction_errors.csv
d7_signed_flux_exact_vs_compressed.csv
d7_grouping_semantic_comparison.csv
d7_post_refinement_multiscale_audit.md
d7_blocked_observations.md
```

---

# D8 — Identity-emergence discriminator

## Hypothesis

```text
Mechanical refinement is not automatically identity fission.

A child identity exists only when post-event sink/basin artifacts persist.
```

## Purpose

D8 is a guardrail against overclaiming.

A spark/refinement event creates more mechanical degrees of freedom. It does not, by itself, prove that a new identity emerged.

The RC identity text defines identity as a stable attractor basin, not as a graph node, label, or rewrite event.  The GRC-9/v3 lift similarly separates mechanical expansion from completed identity emergence: refinement creates the substrate, while post-event attractor structure determines whether child identities actually persist. 

## Why this method is chosen

This discriminator preserves the distinction between:

```text
event mechanics
```

and:

```text
identity-level consequence
```

Without D8, experiments may incorrectly count every spark as a new identity. D8 forces identity claims to be supported by sink/basin persistence.

## Experiment design

For every spark/refinement event observed in the experiment family, classify the outcome.

### Event record

For each event, record:

```text
parent node
event timestep
spark trigger artifacts
active degree
instability/cancellation evidence
created module nodes
boundary reassignment
budget before event
budget immediately after event
```

### Post-event window

Track a window:

```text
[k_event, k_event + T_persist]
```

Within that window record:

```text
sink set at each timestep
basin assignment at each timestep
basin mass at each timestep
module-local sinks
former-parent-basin descendants
flux routing into/out of the module
whether child candidates persist
```

## Outcome classes

Each refinement event should be classified into exactly one primary class.

```text
Class 0 — blocked
    artifacts are insufficient to determine post-event basin outcome

Class 1 — mechanical refinement only
    refinement occurred, but no additional persistent sink/basin appeared

Class 2 — transient child candidate
    an additional sink/basin appeared briefly but failed persistence criteria

Class 3 — persistent child identity
    one additional child sink/basin persisted over the configured window

Class 4 — multi-child fission
    two or more child sinks/basins persisted over the configured window

Class 5 — collapse/reabsorption
    temporary differentiation occurred but collapsed back into one parent-like basin
```

## Persistence criteria

Use configurable but explicit thresholds.

A child identity candidate should require:

```text
sink persistence:
    the candidate sink or a lineage-equivalent sink persists for Δ steps

basin mass:
    basin mass remains above m_min

basin continuity:
    basin membership remains sufficiently stable by Jaccard or mass overlap

lineage:
    the basin is traceable to the refined parent or its created module

budget:
    total budget remains conserved within tolerance
```

Example criterion:

```text
child_identity = true if:

    sink persists for at least Δ timesteps
    basin_mass >= m_min for at least Δ timesteps
    lineage_to_parent = true
    budget_error <= tolerance
```

Use threshold sensitivity analysis:

```text
Δ ∈ {small, medium, large}
m_min ∈ {low, medium, high}
```

This prevents a single arbitrary threshold from deciding the conclusion.

## Controls

```text
matched non-refinement run
transient sink run
randomized lineage labels
randomized basin labels
post-event window sensitivity
degree-only abundance baseline
seed replay
```

## Observation directive

The implementation must identify existing artifacts sufficient to reconstruct:

```text
spark/refinement event
parent node
created module nodes
budget before/after
sink set over time
basin assignment over time
basin mass over time
module lineage
edge/flux continuity into child candidates
```

If sink/basin persistence is not visible, D8 must mark identity outcome as blocked.

## Supporting result

D8 supports the identity-emergence discriminator if:

```text
the experiment distinguishes mechanical refinement from identity fission
only persistent sink/basin artifacts are counted as child identities
transient sinks are classified separately
budget conservation is audited
lineage to the refined parent is auditable
some events may refine without identity fission
some events may produce persistent child identities
```

A strong D8 result does **not** require every spark to produce a child identity. In fact, a mature result may show several outcome classes.

## Weakening or refuting result

D8 weakens identity-level claims if:

```text
identity fission is declared without persistent sink/basin evidence
post-event basins cannot be reconstructed
lineage cannot be audited
budget is not preserved
all refinement events are automatically counted as new identities
```

## Expected output

```text
d8_event_outcome_classification.csv
d8_persistence_windows.csv
d8_basin_lineage_report.md
d8_budget_audit.csv
d8_identity_claims_audit.md
d8_blocked_observations.md
```

---

# Cross-discriminator integration

The D experiments should not be interpreted independently only. They should feed into a family-level evidence table.

## D1 + D3

Together these test:

```text
Rows and columns are structured axes.
Rows and columns are not interchangeable.
```

Strong evidence:

```text
row/column-preserving transforms behave predictably
transpose changes artifact class
S9 random relabeling degrades semantic interpretation
```

## D2 + D6

Together these test:

```text
Rows, columns, and ports have separable predictive roles.
Ports carry interaction behavior beyond row-only and column-only effects.
```

Strong evidence:

```text
rows predict geometry
columns predict interface/refinement
ports predict edge-local behavior
row × column interaction terms are needed for some artifacts
```

## D4 + D5 + D8

Together these test:

```text
Saturation gates refinement.
Columns preserve interface structure across refinement.
Identity claims require persistent attractor/basin evidence.
```

Strong evidence:

```text
degree 9 matters under canonical spark rules
old columns determine boundary reassignment
old columns retain post-event predictive value
some refinements produce persistent child basins
some refinements do not, and are not overclaimed
```

## D7

D7 supports the multiscale/interface side:

```text
eligible nonnegative fields reconstruct through G/Split
signed flux exactness requires J+/J-
true columns align with interface/refinement better than random groupings
```

---

# Suggested implementation order

I would implement D1–D8 in this order:

```text
1. D1 — Factorization
2. D3 — Transpose non-equivalence
3. D4 — Saturation bottleneck
4. D7 — Multiscale reconstruction
5. D6 — Port interaction
6. D5 — Interface memory
7. D8 — Identity emergence
8. D2 — Predictive role separation
```

The reason D2 comes last is that it benefits from the dataset generated by the other discriminators. D2 is the family-level statistical synthesis.

# Final D1–D8 success criteria

The discriminator layer supports the GRC9V3 row/column/port semantics if the reports show:

```text
D1:
    structured row/column transforms preserve semantic artifacts better than
    arbitrary S9 relabeling

D2:
    rows, columns, and ports predict different artifact classes

D3:
    row/column transpose changes behavior in the expected direction

D4:
    nine-port saturation acts as canonical refinement capacity

D5:
    parent column labels preserve and predict interface behavior across refinement

D6:
    some artifacts require row × column port interaction terms

D7:
    column G/Split is auditable for eligible fields, and signed flux exactness
    requires J+/J- decomposition

D8:
    identity fission is reported only when persistent post-event sink/basin
    artifacts support it
```

The strongest possible family-level conclusion would be:

```text
GRC9V3 is not merely a bounded-degree graph convention.

Its 3×3 factorization is visible in runtime artifacts:
    rows carry differential/geometric signatures,
    columns carry interface/refinement/multiscale signatures,
    ports carry intersection-level edge behavior,
    and identity-level claims can be separated from mechanical refinement.
```

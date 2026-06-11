# GRC9V3 Properties Experiment Specification

## 1. Purpose

This experiment family tests whether `GRC9V3` behaves as a meaningful nine-port substrate, rather than merely as a bounded-degree graph convention.

The central question is:

```text
Do rows, columns, and ports separate differential, interface, routing,
refinement, and identity behavior in ways that are visible in runtime artifacts?
```

The experiment should not prove the row/column/port semantics by reading the source or by assuming the intended interpretation. It should test whether those semantics produce **observable runtime differences**.

The relevant theoretical distinction is:

```text
Rows = local differential / mode directions.
Columns = interface / boundary / refinement families.
Ports = intersections where row and column semantics meet.
```

The GRC-9 text defines rows as the triplet directions used in the row-wise contribution to the coherence tensor, while columns are the polarity/interface families used for deterministic routing, refinement, and invertible column coarse-graining/Split . The broader RC framing treats identities as stable attractor basins and sparks as degeneracy events that can change the attractor structure, so identity-level claims must be backed by sink/basin persistence rather than by source-authored labels alone .

## 2. Experimental stance

The experiments should be **observational and counterfactual**.

They may:

```text
construct fixtures
choose initial states
choose perturbations
choose runtime parameters
run the existing implementation
collect existing runtime artifacts
post-process artifacts
generate reports
```

They should not:

```text
change runtime behavior
add new spark mechanics
add new identity logic
add new routing rules
add new telemetry producers inside src/pygrc
treat source intent as experimental evidence
```

If an experiment reveals that the existing runtime lacks a reusable surface needed to make a claim, the experiment should record that as a missing capability. That capability can later graduate into `src/` through a separate repo-level `implementation/` task with tests.

Before experiment implementation resumes, the current `GRC9V3` runtime should
be treated as the **current-hybrid signed-Hessian baseline**. In that baseline,
spark candidates are audited through saturation, basin-interior evidence, and
signed-Hessian degeneracy. Direct per-column `H_s^(b)` cancellation is a
derived analysis proxy unless a separate canonical-column-H runtime lane is
explicitly implemented, configured, tested, and reported.

## 3. Telemetry directive

Telemetry in this spec means **required observability**, not specific implementation fields.

Each experiment should declare:

```text
Observation requirement:
    What must be visible in artifacts to support or reject the hypothesis.

Acceptable artifact sources:
    Existing checkpoints, telemetry, observer records, edge labels,
    event logs, runtime summaries, or reportable derived values.

Evidence rule:
    The claim is supported only if the observation can be reconstructed from
    existing runtime artifacts.

Blocked rule:
    If no existing artifact can support the observation, the experiment result
    should be marked blocked or inconclusive, not silently inferred.
```

For example, instead of saying:

```text
Read telemetry field row_gradient_i_a.
```

the spec should say:

```text
The run must expose enough existing artifact data to reconstruct or approximate
row-local differential response at the tested node.
```

Then implementation can decide whether that comes from existing `K`, edge fluxes, edge weights, node state, observer output, or checkpoint reconstruction.

This keeps the experiment independent of the current telemetry naming scheme.

## 4. Claim standard

The experiments should distinguish several levels of evidence.

### Level 0: source intent

```text
The implementation or paper says rows mean differential modes.
```

This is not experimental evidence.

### Level 1: artifact presence

```text
Runtime artifacts expose ports, rows, columns, edges, sinks, or events.
```

Useful, but not enough.

### Level 2: localized response

```text
A row-local or column-local perturbation produces a localized runtime response.
```

Better, but still possibly confounded.

### Level 3: controlled equivariance

```text
The response moves correctly under row or column permutation.
```

This is strong evidence that the label family matters.

### Level 4: semantic separation

```text
Rows and columns behave differently under matched controls.
Rows affect differential/geometric signatures.
Columns affect interface/routing/refinement/coarse-graining signatures.
```

This is the main target.

### Level 5: identity-level consequence

```text
The effect changes persistent sink/basin structure, child identity inheritance,
or path/observer classification.
```

This requires persistence evidence, not just an event trigger.

## 5. Core method: paired counterfactual runs

Every experiment should use paired or grouped runs where most conditions are identical and only the port interpretation or perturbation location changes.

The main controls are:

| Control                                      | Purpose                                                                   |
| -------------------------------------------- | ------------------------------------------------------------------------- |
| **Row permutation**                          | Tests whether row effects move with row labels.                           |
| **Column permutation**                       | Tests whether column effects move with column labels.                     |
| **Row/column transpose**                     | Tests whether rows and columns are semantically different.                |
| **Degree-preserving random port relabeling** | Tests whether results are only graph-degree effects.                      |
| **Energy-matched perturbations**             | Prevents larger perturbations from being mistaken for row/column meaning. |
| **Seed replay**                              | Separates structural effects from stochastic or parameter noise.          |

The null hypothesis for the whole family is:

```text
The 3×3 port structure is only a bounded-degree graph convention.
Rows, columns, and ports do not produce separable runtime signatures beyond
ordinary adjacency, conductance, degree, and initial coherence values.
```

The alternative hypothesis is:

```text
Rows, columns, and ports produce distinct, reproducible, auditable runtime
signatures under controlled perturbations.
```

This method is chosen because it tests semantics through behavior. A source statement such as “columns are interface families” is weak. A controlled result such as “column-2 cancellation affects column-2 routing and refinement, and the effect moves under column permutation but not row permutation” is stronger.

## 6. Common observability requirements

Each run should make it possible, using existing artifacts, to inspect the following categories where relevant.

### Node-level observability

The experiment should be able to inspect or reconstruct:

```text
coherence density C
active degree
sink status
basin assignment
local geometry or row-resolved geometric proxy
net flux or local flux balance
spark eligibility
spark/refinement event participation
parent/child identity relation, if already exposed
```

### Edge-level observability

The experiment should be able to inspect or reconstruct:

```text
edge endpoints
endpoint ports
row and column of endpoint ports
conductance / base weight
oriented flux or absolute flux
edge labels such as distance, delay, or functional coupling, if already exposed
path membership, if computed during analysis
```

### Event-level observability

The experiment should be able to inspect or reconstruct:

```text
spark candidate conditions
spark trigger event
refinement event
old boundary edge mapping
new boundary edge mapping
budget before event
budget after event
sink/basin structure before and after event
```

### Coarse-graining observability

The experiment should be able to inspect or reconstruct:

```text
port-attached scalar field X
column totals
intra-column row profiles
Split reconstruction
reconstruction error
```

For signed flux, exact reconstruction should use positive and negative parts separately, because the GRC-9 text distinguishes lossless signed-flux encoding from compressed diagnostic encoding .

## 7. Experiment A: row-mode stress

### Question

Do rows behave as local differential modes?

### Hypothesis

A perturbation localized to one row should produce a localized response in row-sensitive geometric or differential artifacts.

For example:

```text
stress row 1 → row 1 geometric/differential signature dominates
stress row 2 → row 2 geometric/differential signature dominates
stress row 3 → row 3 geometric/differential signature dominates
```

### Why this test is diagnostic

Rows are the part of the 3×3 bundle that directly correspond to local mode directions. If rows have runtime meaning, then row-local coherence differences should affect row-resolved geometry or differential response. If rows are only arbitrary labels, then moving the same perturbation between rows should not produce structured row-local effects.

### Method

Use a symmetric saturated or near-saturated node with all nine ports active.

Apply matched perturbations:

```text
A1: row-1-localized coherence gradient
A2: row-2-localized coherence gradient
A3: row-3-localized coherence gradient
A4: balanced gradient across all rows
```

Perturbations should be energy-matched:

```text
same total |ΔC|
same total (ΔC)^2
same number of affected ports
same conductance initialization, where controllable
```

### Controls

```text
row permutation
column permutation
row/column transpose
degree-preserving random port relabeling
seed replay
```

### Observation requirement

The run must expose enough existing artifact data to determine whether the stressed row produced a row-local runtime response.

Acceptable evidence may include any existing combination of:

```text
row-resolved K or geometry summaries
row-resolved gradient proxies
row-resolved edge mismatch
row-resolved flux stress
row-resolved Hessian-like signatures
checkpoint-derived reconstruction from C, ports, edges, and weights
```

### Supporting result

The hypothesis is supported if:

```text
row-a stress produces dominant response in row a
row permutation moves the dominant response accordingly
column permutation does not explain the response
random port relabeling weakens or destroys the clean row signature
```

### Refuting or weakening result

The hypothesis is weakened if:

```text
all row stresses produce indistinguishable responses
the response is explained only by degree or total perturbation magnitude
row/column transpose behaves equivalently
random port relabeling preserves the same effect
```

## 8. Experiment B: column-interface cancellation

### Question

Do columns behave as interface and cancellation families?

### Hypothesis

A perturbation localized to one column should affect column-sensitive interface behavior: cancellation proxy, boundary pressure, routing, spark risk, or refinement behavior.

### Why this test is diagnostic

Columns are not primarily differential directions. They are supposed to be stable interface families. Therefore the diagnostic should not ask whether columns behave like rows. It should ask whether column-local conditions affect boundary and refinement behavior.

The GRC-9 construction uses column families for curvature/cancellation diagnostics, deterministic boundary reassignment during expansion, and column coarse-graining/Split .

### Method

Use a saturated sink candidate with all nine ports active.

Construct matched states where one column is near cancellation or sign crossing:

```text
B1: column 1 near cancellation
B2: column 2 near cancellation
B3: column 3 near cancellation
B4: column 1 sign crossing over time
B5: column 2 sign crossing over time
B6: column 3 sign crossing over time
```

The treatments should preserve row energy as much as possible, so that the result is not secretly a row-mode effect.

### Controls

```text
column permutation
row permutation
row/column transpose
degree-preserving random port relabeling
seed replay
```

### Observation requirement

The run must expose enough existing artifact data to determine whether column-local cancellation or pressure changed interface behavior.

Acceptable evidence may include:

```text
column-local cancellation proxy
column-local flux balance
column-local boundary pressure
signed-Hessian hybrid spark candidate conditions
direct column-H spark trigger conditions only if a canonical-column-H lane exists
spark trigger event
routing changes by column
refinement reassignment by column
checkpoint-derived reconstruction from C, ports, edges, fluxes, and weights
```

### Supporting result

The hypothesis is supported if:

```text
column-b cancellation produces a column-b-local effect
column permutation moves the effect
row permutation does not reproduce the same explanation
degree-preserving random relabeling weakens or destroys the clean column effect
```

### Important interpretation rule

Use three separate terms:

```text
spark candidate:
    runtime state approaches or satisfies local trigger conditions

refinement event:
    runtime executes mechanical expansion

completed identity spark:
    post-event sink/basin structure gains at least one persistent child basin
```

Do not call an event a completed identity spark unless the post-event attractor structure supports it.

## 9. Experiment C: port saturation and near-saturation

### Question

Does finite port capacity matter?

### Hypothesis

Saturation should act as a meaningful gate for refinement. A stressed but unsaturated node should not behave the same as a saturated stressed node under canonical rules.

### Why this test is diagnostic

The nine-port substrate is not just a graph with labels; it imposes finite local interface capacity. The current `GRC9V3` baseline uses active degree 9 together with basin-interior and signed-Hessian degeneracy evidence. The core `GRC9` column-H diagnostic is a separate canonical-column-H lane if implemented. Near-saturation remains an optional extension. This experiment tests whether the runtime distinguishes:

```text
geometric stress
```

from:

```text
geometric stress plus exhausted local port capacity
```

### Method

Create matched sink candidates with active degree:

```text
C1: active degree 7
C2: active degree 8
C3: active degree 9
```

Try to keep local coherence, instability proxy, flux pressure, and neighborhood structure as similar as possible.

If near-saturation behavior is already implemented, run it as a separate labeled condition:

```text
C4: active degree 8 under near-saturation policy
```

### Controls

```text
same instability without saturation
same saturation without instability
row/column relabeling
seed replay
```

### Observation requirement

The run must expose enough existing artifact data to determine:

```text
active degree
inactive ports
spark eligibility
spark trigger or non-trigger
refinement event or non-event
budget before/after event
sink/basin structure before/after event
```

### Supporting result

Canonical saturation behavior is supported if:

```text
degree 7 or 8 with stress does not trigger canonical refinement
degree 9 with comparable signed-Hessian hybrid stress becomes eligible
degree 9 without signed-Hessian degeneracy does not trigger merely because full
direct column-H effects are reported separately if a canonical-column-H lane exists
```

Near-saturation behavior should be reported separately as an optional policy, not as canonical GRC9V3 evidence.

## 10. Experiment D: column-preserving refinement and child identity inheritance

### Question

When refinement occurs, does it preserve column interface structure, and can post-refinement child identities be audited?

### Hypothesis

A refinement event should preserve the parent’s external boundary organization by column. If child identities emerge later, their relation to the parent should be visible through runtime artifacts.

### Why this test is diagnostic

Column semantics become most concrete during refinement. In GRC-9, expansion is mechanical: old boundary edges are reassigned by column family, and the module creates additional local representational capacity . This is the strongest test of whether columns are interface families rather than merely labels.

The RC/v3 interpretation also requires care: expansion does not itself prove identity fission. Identity fission requires post-event stable sink/basin structure .

### Method

Start from a saturated sink whose incident edges occupy known ports.

Induce or select a run where refinement occurs.

Compare:

```text
D1: uniform state transfer, if runtime uses it
D2: inflow-weighted state transfer, if already supported
D3: column-1-skewed inflow
D4: column-2-skewed inflow
D5: column-3-skewed inflow
```

### Controls

```text
column permutation
row permutation
same node without refinement
seed replay
```

### Observation requirement

The run must expose enough existing artifact data to determine:

```text
which parent node refined
which module nodes were created
which old boundary edges were reassigned
old endpoint port
new endpoint port
old column
new module attachment location
budget before refinement
budget after refinement
post-event sink set
post-event basin assignments
persistence of any child basin
```

### Supporting result for refinement

Column-preserving refinement is supported if:

```text
old boundary edges from column b are reassigned to the corresponding
column-b part of the refinement module
budget is preserved across the event
the event is visible in checkpoints and event logs
```

### Supporting result for child identity inheritance

Child identity inheritance is supported only if:

```text
post-refinement child sink or sinks persist for a configured window
child basin mass exceeds a configured threshold
child structure can be traced back to the refined parent
observer or checkpoint artifacts support the lineage claim
```

### Weak result

If refinement is visible but no persistent child basin emerges, the correct conclusion is:

```text
The run supports mechanical column-preserving refinement,
but not identity fission.
```

## 11. Experiment E: coarse-graining and Split reconstruction

### Question

Is column coarse-graining lossless for eligible port-attached fields, and where is it lossy for compressed signed fields?

### Hypothesis

For nonnegative port-attached scalar fields, applying column coarse-graining followed by Split should reconstruct the original field up to numerical error. For signed flux, exact reconstruction should require separate positive and negative channels.

### Why this test is diagnostic

The GRC-9 multiscale claim is unusually concrete: column coarse-graining and Split are defined as an invertible local transformation for nonnegative port fields. This is directly testable from runtime artifacts. It also tests the distinction between exact multiscale representation and diagnostic compression.

### Method

At selected checkpoints, identify existing port-attached scalar fields.

Candidate fields:

```text
conductance / base weight
absolute flux
positive flux
negative flux
functional coupling magnitude, if exposed
curvature proxy, if nonnegative and exposed
edge-label-derived nonnegative quantities
```

For each eligible field:

```text
X → G(X) → Split(G(X)) → reconstruction error
```

For signed flux:

```text
J+ = max(J, 0)
J- = max(-J, 0)
G/Split J+ and J- separately
reconstruct J = J+ - J-
```

If a compressed signed representation is also tested, report it explicitly as lossy.

### Controls

```text
zero columns
single-active-port columns
mixed-sign flux columns
dense columns
after-refinement checkpoints
before/after topology change checkpoints
```

### Observation requirement

The run must expose enough existing artifact data to reconstruct port-attached fields and their column grouping.

### Supporting result

The hypothesis is supported if:

```text
nonnegative fields reconstruct with near-zero numerical error
J+/J- signed flux reconstruction is near-exact
compressed signed flux reconstruction fails or loses information exactly
when signs vary within a column
```

### Negative result

The hypothesis is weakened if:

```text
eligible nonnegative fields cannot be reconstructed
column grouping is not auditable from artifacts
post-refinement port mappings cannot support Split checks
```

If the field is unavailable in existing artifacts, the result should be marked blocked for that field, not failed.

## 12. Experiment F: metric path, temporal-delay path, and strongest-flux path disagreement

### Question

Can different edge-label path notions disagree while remaining auditable?

### Hypothesis

The same graph can contain cases where:

```text
metric shortest path
temporal-delay shortest path
strongest-flux path
```

select different routes.

### Why this test is diagnostic

The GRC-v3 lift distinguishes base conductance used by dynamics from additional analytic edge labels such as geometric separation, temporal delay, and functional coupling strength . This experiment tests whether the runtime artifacts can support multiple path interpretations without collapsing them into a single “best path.”

### Method

Use a fixture with at least three corridors between the same endpoints.

Design or search for a run where:

```text
corridor A has lowest metric cost
corridor B has lowest temporal delay
corridor C has strongest flux / functional coupling
```

Compute paths using existing edge labels where available:

```text
metric path:
    minimize total geometric length or metric cost

delay path:
    minimize total temporal delay

flux path:
    maximize bottleneck flux or maximize cumulative flux score
```

### Controls

```text
same graph with labels equalized
same graph with flux equalized
same graph with port relabeling
seed replay
```

### Observation requirement

The run must expose enough existing artifact data to compute or reconstruct the relevant path criteria.

If temporal delay or geometric length labels are not available in existing artifacts, the experiment should either:

```text
use whatever existing labels correspond to those concepts
```

or mark that path comparison as blocked.

### Supporting result

The hypothesis is supported if:

```text
the selected metric path differs from the delay path or flux path
the winning criterion for each path is auditable edge by edge
the disagreement is not caused by missing labels or analysis artifacts
```

A strong result is:

```text
P_metric ≠ P_delay ≠ P_flux
```

with an edge-level explanation for each selected route.

## 13. Experiment G: row-preserving, column-changing motion observer

### Question

Can the runtime distinguish motion that preserves row semantics while changing column/interface semantics?

### Hypothesis

Some dynamics should be classifiable as:

```text
row-preserving but column-changing
```

or the reverse:

```text
column-preserving but row-changing
```

### Why this test is diagnostic

This experiment targets the port intersection layer. A port belongs to exactly one row and one column. If rows and columns separate differential and interface roles, then a route or dominant flow can remain stable in one semantic dimension while changing in the other.

This is a more subtle test than row stress or column cancellation because it asks whether the runtime can observe **mixed semantic behavior**.

### Method

Create or identify a run where dominant flux, basin boundary, or local continuation moves across ports.

Target patterns:

```text
same row, changing column:
    (row 2, column 1) → (row 2, column 2) → (row 2, column 3)

same column, changing row:
    (row 1, column 3) → (row 2, column 3) → (row 3, column 3)
```

### Controls

```text
row permutation
column permutation
random port relabeling
static no-motion baseline
seed replay
```

### Observation requirement

The run must expose enough existing artifact data to classify dominant local behavior by row and column over time.

Acceptable evidence may include:

```text
dominant flux edge by timestep
dominant boundary edge by timestep
basin assignment changes
sink-directed successor changes
port-level route changes
checkpoint-derived edge/port histories
```

### Supporting result

The hypothesis is supported if:

```text
the observer can classify transitions as row-preserving/column-changing
or column-preserving/row-changing
the classification is backed by edge/port artifacts
row and column permutations transform the classification as expected
random port relabeling weakens semantic interpretability
```

## 14. Cross-experiment analysis

Each experiment should produce local conclusions, but the family-level result should be based on convergence across experiments.

### Row evidence is strong if

```text
row-local stress produces row-local geometric/differential signatures
row permutations move those signatures
column permutations do not explain them
row/column transpose is not equivalent
```

### Column evidence is strong if

```text
column-local cancellation affects interface/routing/refinement signatures
column permutations move those signatures
row permutations do not explain them
row/column transpose is not equivalent
```

### Port evidence is strong if

```text
some edge or route classifications differ under row grouping and column grouping
the difference is visible in runtime edge/port artifacts
the behavior cannot be reduced to degree or adjacency alone
```

### Refinement evidence is strong if

```text
saturation/refinement events are auditable
boundary reassignment preserves column structure
budget is preserved
child identity claims are supported by persistent sink/basin artifacts
```

### Multiscale evidence is strong if

```text
G/Split reconstructs eligible nonnegative port fields
signed flux exactness requires J+/J-
compressed signed representations visibly lose information in mixed-sign columns
```

## 15. Suggested first tranche

The first implementation tranche should avoid the most ambiguous identity-level claims and focus on the clearest semantics.

### First: row-mode stress

This gives the cleanest test of row differential meaning.

Expected output:

```text
row-local perturbation table
row permutation comparison
row/column transpose comparison
row-local response report
```

### Second: column-interface cancellation

This gives the cleanest test of column interface meaning.

Expected output:

```text
column cancellation table
column permutation comparison
spark/refinement candidate evidence
routing/refinement report if event occurs
```

### Third: coarse-graining/Split reconstruction

This gives the cleanest test of the multiscale column claim.

Expected output:

```text
field-by-field reconstruction error
signed flux exact/lossy comparison
before/after topology event reconstruction check, if possible
```

Only after those pass should the experiment family emphasize child identity inheritance, path disagreement, and motion observer classification.

## 16. Family-level success criteria

The experiment family supports the intended GRC9V3 semantics if the completed reports show:

```text
1. Rows produce reproducible differential/geometric signatures.

2. Columns produce reproducible interface/routing/refinement signatures.

3. Row and column permutations behave equivariantly.

4. Row/column transpose is not behaviorally equivalent.

5. Degree-preserving random port relabeling weakens or destroys clean semantic signatures.

6. Saturation gates refinement under canonical rules.

7. Column-preserving refinement is visible in boundary edge reassignment.

8. Budget preservation is maintained across topology events.

9. Child identity claims are made only when persistent sink/basin artifacts support them.

10. G/Split reconstructs eligible nonnegative port fields.

11. Signed flux is exactly reconstructable through positive/negative decomposition,
    while compressed signed representations are correctly reported as lossy.

12. Distinct path notions can disagree when supported by existing edge labels.

13. Port-level observer records can classify mixed row/column behavior when artifacts expose it.
```

A negative or inconclusive result is still useful. The goal is not to force confirmation; it is to determine which parts of the nine-port interpretation are actually observable through the implemented runtime.

---
title: "Polarized Basin Loops in GRC9V3"
subtitle: "Source–Sink Aspects, Conserved Pulse Cycles, and Internal Loop Formation"
version: "draft v0.1"
date: "2026-05-15"
status: "research scaffold / implementation-ready draft"
license: "CC BY-SA 4.0"
---

# Polarized Basin Loops in GRC9V3

## Abstract

This paper defines a first experimental program for studying **polarized basin loops** in a Graph Reflexive Coherence execution layer, here called **GRC9V3**. The core hypothesis is that a single identity basin can internally differentiate into two complementary aspects: an **emitter/source-aspect** that exports coherence and a **collector/sink-aspect** that imports coherence, while a return channel restores the source-aspect under exact global budget conservation. The result is not an external source or an external sink. It is a **closed redistributive loop** inside one basin.

The paper deliberately stops short of claiming movement or locomotion. Its claim surface is narrower: internal polarity, source/sink-aspect roles, return-path closure, cyclic redistribution, self-regulation of pulse amplitude, and conservation. This experiment is intended to precede or run in parallel with movement experiments. If successful, it provides the pulse-generating substrate from which movement and locomotion-like behavior may later be explored.

---

## Methodological Note: Mechanism Before Execution Surface

This experiment separates a proposed discrete-geometric mechanism from any one
runtime surface that might later execute it.

The first question is not:

```text
Can the current GRC9V3 step surface produce the loop?
```

but:

```text
What conserved causal mechanism would count as a loop, and what evidence would
distinguish it from relaxation, label artifacts, or hidden source/sink terms?
```

Only after that mechanism is specified and audited should it be mapped onto a
specific execution model such as fixed-topology GRC9V3 continuity, LGRC9V3
packet/event execution, or a later fractal/hierarchical runtime.

This distinction matters because a negative result on one execution surface is
not automatically a negative result for the mechanism. In this experiment,
native fixed-topology GRC9V3 proposal flux is tested first and remains a valid
execution-surface result. If that surface cannot carry the needed causal
handoff, the correct conclusion is not that the loop idea is false, but that
this particular execution surface is insufficient for that mechanism.

The packetized branch follows this discipline. It records a conserved causal
in-flight coherence mechanism:

```text
state trigger
    -> packet departure
    -> in-flight coherence
    -> packet arrival
    -> returned coherence recreates trigger condition
    -> next departure
```

That mechanism is then translated into an LGRC-style ledger before any stronger
claim is made about native LGRC9V3 execution. The ledger records the expected
events, packets, route, trigger, budget, self-rearm evidence, and blocked
controls. This makes the later runtime question precise:

```text
Can a concrete runtime reproduce this ledger-level causal structure?
```

The claim discipline is therefore:

| Claim | Required evidence |
|---|---|
| Mechanism-positive | Conserved event/packet/route evidence passes controls. |
| Execution-surface-positive | A named runtime reproduces the mechanism without hidden adapters. |
| Native-runtime-positive | The runtime produces the mechanism through its own declared primitives. |

This prevents two mistakes: treating an implementation failure as a theory
failure, and treating an experiment-local adapter as native runtime evidence.

---

## 1. Motivation

Movement in Reflexive Coherence should not be introduced as a repeatedly forced external input. A one-time perturbation can demonstrate transient basin drift, but locomotion-like behavior requires something stronger: a mechanism that can **regenerate the conditions required for further movement**.

The missing mechanism proposed here is an internal loop.

A basin that contains an emitter region and a collector region may be able to sustain a cycle:

```text
source-aspect exports coherence
    -> forward channel carries coherence
    -> sink-aspect collects coherence
    -> return channel refills source-aspect
    -> source-aspect exports again
```

If this cycle is conservative, recurrent, and state-regulated, it becomes a candidate **internal pulse generator**. Later, if that pulse generator couples asymmetrically to a basin boundary, it may become a movement mechanism. This paper isolates the first question:

> Can a single basin sustain an internal source–sink coherence loop under the closed GRC9V3 reflexive dynamics?

---

## 2. Background: closed coherence dynamics

The relevant RC/GRC commitment is that coherence is redistributed, not externally created or destroyed. In the continuum theory, the primitive state contains coherence density and coherence flux:

$$
\mathcal S_{\mathrm{coh}} = (C, J_C),
\qquad
J_C = C v_C .
$$

The closed continuity law is:

$$
\partial_t C + \nabla \cdot J_C = 0 .
$$

The core loop is:

$$
C
\rightarrow
K[C]
\rightarrow
g[K]
\rightarrow
J_C
\rightarrow
\partial_t C
\rightarrow
C .
$$

In a graph execution layer, the corresponding discrete loop is:

$$
C
\rightarrow
K[C]
\rightarrow
w
\rightarrow
\Phi
\rightarrow
J
\rightarrow
C .
$$

For GRC9V3, we use the G-RC-9 mechanical substrate read through the GRC-v3 basin-attribute interpretation. A node is not only a scalar carrier. It can be read as a basin chart with attributes:

$$
\mathcal B_i =
(C_i,\mathbf g_i,\widetilde H_i,\mathbf J_i^{net},M_i,id_i,parent_i,depth_i).
$$

The nine-slot layer supplies the mechanical interface: finite ports, row-based local directional structure, column-based interface families, deterministic local rewiring, and exact budget preservation.

---

## 3. Terminology: avoid external source/sink confusion

This paper does **not** introduce external sources or external sinks.

An external source term would change the continuity equation into:

$$
\partial_t C + \nabla \cdot J_C = S_{\mathrm{ext}},
$$

which would open the loop and break the intended closed-system interpretation unless explicitly modeled as an environment exchange. That is out of scope here.

Instead, we define **source** and **sink** as internal basin roles.

### 3.1 Source-aspect

A region \(R_S \subset B\) is a **source-aspect** over a window \(W=[k_0,k_1]\) when it persistently exports coherence into the rest of the basin:

$$
F_{\mathrm{out}}(R_S,k)
=
\sum_{i\in R_S}\sum_{j\notin R_S} J_{ij}^{(k)}
> \theta_S
$$

for enough steps in \(W\), under a fixed orientation convention where \(J_{ij}>0\) means flux leaves \(i\) toward \(j\).

The source-aspect is not a creator of coherence. It is an export-biased subregion.

### 3.2 Sink-aspect

A region \(R_K \subset B\) is a **sink-aspect** over a window \(W\) when it persistently imports coherence:

$$
F_{\mathrm{in}}(R_K,k)
=
\sum_{i\notin R_K}\sum_{j\in R_K} J_{ij}^{(k)}
> \theta_K .
$$

The sink-aspect is not an annihilator of coherence. It is an import-biased subregion.

### 3.3 Return channel

A **return channel** is a path or subgraph \(P_{K\to S}\subset B\) through which coherence that has accumulated near the sink-aspect later contributes to refilling the source-aspect.

A return channel is detected by a delayed relation:

$$
F_{\mathrm{in}}(R_K,k)
\leadsto
F_{\mathrm{return}}(P_{K\to S},k+\Delta)
\leadsto
C_S(k+\Delta') \uparrow .
$$

### 3.4 Polarized basin loop

A **polarized basin loop** exists when the same parent basin \(B\) contains a source-aspect, sink-aspect, forward channel, and return channel that together form a recurrent conservative cycle:

$$
R_S
\rightarrow
P_{S\to K}
\rightarrow
R_K
\rightarrow
P_{K\to S}
\rightarrow
R_S .
$$

The loop is not an imposed semantic label. It should be detected from flux, coherence, and basin-attribute traces.

---

## 4. Relationship to graph-theoretic sinks

GRC-style graphs already define **sinks** as attractor nodes under directed flux routing. That usage must be separated from the present sink-aspect concept.

| Term | Meaning | Scale |
|---|---|---|
| Attractor sink | A graph node or basin seed receiving directed flux and defining an attraction basin | identity/basin layer |
| Sink-aspect | An import-biased subregion inside one parent basin | internal organization layer |
| Source-aspect | An export-biased subregion inside one parent basin | internal organization layer |
| Loop | A conservative circulation connecting source-aspect and sink-aspect through forward and return channels | intra-basin dynamics |

The preferred wording is therefore:

- emitter pole,
- collector pole,
- source-aspect,
- sink-aspect,
- return channel,
- polarized basin loop.

Use "sink" alone only when the graph-theoretic attractor sink is meant.

---

## 5. Loop taxonomy L0–L6

The first experiment family uses a loop ladder.

| Level | Name | Meaning | Claim ceiling |
|---|---|---|---|
| L0 | no-loop | No persistent source/sink polarity. Flux relaxes, dissipates, or settles. | No loop evidence. |
| L1 | transient polarity | Source-like and sink-like regions appear briefly but do not close a cycle. | Polarity candidate only. |
| L2 | paired source/sink aspects | One region exports while another imports within the same basin. | Internal polarity observed. |
| L3 | return-path refill | Sink intake is followed by detectable return flux that refills the source-aspect. | Closed redistributive path candidate. |
| L4 | repeated conserved cycle | The source/sink/return relation repeats for multiple periods under exact budget conservation. | Conserved internal loop. |
| L5 | self-regulating cycle | Cycle amplitude/frequency recovers after small perturbation or damping. | Pulse-generator candidate. |
| L6 | boundary-couplable loop | The loop can be phase-coupled to a boundary/front-rear asymmetry without losing identity. | Locomotion precursor only; movement claim belongs to the second paper. |

L6 is intentionally a bridge level, not a movement claim.

---

## 6. Experimental design

### 6.1 Minimal substrate

The recommended first substrate is a **1D ring**:

$$
0-1-2-\cdots-(N-1)-0 .
$$

A line has endpoints and can make export/import look like boundary leakage. A ring makes closure explicit.

For GRC9V3, the ring can be represented either as:

1. a simple graph adapter using the GRC-v3 loop equations, or
2. a nine-slot port graph where each node uses two occupied boundary ports and the remaining ports are inactive.

The initial study should disable topology events:

```text
growth = off
pruning = off
spark expansion = off
merge-back = off
```

This keeps the experiment about loop formation, not substrate adaptation.

### 6.2 Initial basin

Initialize a single basin distributed around the ring. The simplest nonuniform profile has:

- one higher-gradient/export-biased region \(R_S\),
- one lower-potential/import-biased region \(R_K\),
- two arcs connecting them.

A generic initialization may be:

$$
C_i^{(0)}
=
C_0
+
A_S \exp\left(-d(i,i_S)^2/2\sigma_S^2\right)
+
A_K \exp\left(-d(i,i_K)^2/2\sigma_K^2\right)
+
\epsilon h_i ,
$$

followed by projection to the conserved budget simplex:

$$
C^{(0)} \leftarrow \operatorname{Proj}_{\Delta_B}(C^{(0)}),
\qquad
\Delta_B=\{x_i\ge 0,\sum_i x_i=B\}.
$$

The profile should be varied across controlled lanes. Some lanes may initialize only \(C\); later lanes may initialize conductance asymmetry \(w\), local mobility, or port-column asymmetry.

### 6.3 No external source terms

All pulses must be either:

- produced by initial structure,
- produced by a one-time budget-preserving perturbation,
- or produced by state-triggered redistribution inside the conserved graph.

Do not add coherence from outside.

---

## 7. Pulse-lane taxonomy

The loop paper uses pulse lanes, but the target is not movement.

| Lane | Name | How asymmetry enters | What it tests |
|---|---|---|---|
| U | unperturbed/null | Uniform ring, no source/sink structure | No loop should appear except numerical artifacts. |
| S | structured initialization | Source/sink-like asymmetry present only at \(k=0\) | Can structure alone produce a loop? |
| K | one-time kick | One budget-preserving impulse at \(k=0\) | Can a local conserved perturbation initiate a loop? |
| R | repeated scheduled redistribution | Small zero-sum pulses at fixed cadence | Can the substrate carry a driven cycle? |
| T | state-triggered redistribution | Pulse occurs only when source/sink state crosses a threshold | Can feedback regulate the cycle? |
| F | free-after-trigger | One state-triggered event, then no further intervention | Does the loop persist without continuous control? |

For this paper, lanes U/S/K are the most important. Lanes R/T/F are useful later for L5/L6.

---

## 8. Observables

### 8.1 Region masses

For source-aspect and sink-aspect regions:

$$
C_S(k)=\sum_{i\in R_S} C_i^{(k)},
\qquad
C_K(k)=\sum_{i\in R_K} C_i^{(k)}.
$$

For parent basin:

$$
M_B(k)=\sum_{i\in B(k)} C_i^{(k)}.
$$

Global budget:

$$
B_{\mathrm{total}}(k)=\sum_i C_i^{(k)}.
$$

### 8.2 Forward and return flux

Let \(P_{S\to K}\) be the forward arc and \(P_{K\to S}\) the return arc.

$$
J_{\mathrm{fwd}}(k)
=
\sum_{(i,j)\in P_{S\to K}} J_{ij}^{(k)}
$$

$$
J_{\mathrm{return}}(k)
=
\sum_{(i,j)\in P_{K\to S}} J_{ij}^{(k)} .
$$

### 8.3 Polarity score

A simple polarity score:

$$
\Pi(k)
=
\frac{
|F_{\mathrm{out}}(R_S,k)|+
|F_{\mathrm{in}}(R_K,k)|
}{
\epsilon+
\sum_{(i,j)\in E}|J_{ij}^{(k)}|
}.
$$

A direction-consistent version should also check signs.

### 8.4 Closure score

A loop closure score should require both forward and return activity:

$$
\Lambda(k)
=
\min\left(
\frac{|J_{\mathrm{fwd}}(k)|}{\epsilon+J_0},
\frac{|J_{\mathrm{return}}(k+\Delta)|}{\epsilon+J_0}
\right).
$$

### 8.5 Phase relation

The expected loop signature is not simply "flux is high." It is a phase relation:

$$
C_S \downarrow
\Rightarrow
J_{\mathrm{fwd}} \uparrow
\Rightarrow
C_K \uparrow
\Rightarrow
J_{\mathrm{return}} \uparrow
\Rightarrow
C_S \uparrow .
$$

Use lagged cross-correlation or event-order rules to detect this.

### 8.6 Self-regulation

For L5, measure recovery after perturbing cycle amplitude:

$$
A_{\mathrm{cycle}}(k)
=
\max_{w} C_S - \min_{w} C_S
$$

over a rolling window \(w\). A self-regulating cycle should return toward a stable amplitude band after small perturbations.

---

## 9. Acceptance gates

### 9.1 Conservation gate

For every run:

$$
|B_{\mathrm{total}}(k)-B_{\mathrm{total}}(0)| < \epsilon_B
$$

for all sampled \(k\).

### 9.2 Single-parent-basin gate

The source-aspect and sink-aspect must remain within the same tracked parent basin:

$$
R_S(k)\subset B(k),
\qquad
R_K(k)\subset B(k).
$$

If a split occurs, the run is not a loop-positive result for this paper. It may be retained as a refinement byproduct.

### 9.3 Polarity gate

Persistent source/sink polarity requires:

$$
F_{\mathrm{out}}(R_S,k)>\theta_S
$$

and

$$
F_{\mathrm{in}}(R_K,k)>\theta_K
$$

for a minimum fraction of the window.

### 9.4 Return gate

There must be delayed return activity:

$$
J_{\mathrm{return}}(k+\Delta)>\theta_R
$$

after forward emission events.

### 9.5 Repetition gate

For L4+, the loop must complete at least \(n_{\mathrm{cycles}}\) cycles under budget conservation.

### 9.6 Null separation gate

The loop-positive lanes must exceed null lanes by a predefined margin:

$$
\Lambda_{\mathrm{positive}}-\Lambda_{\mathrm{null}}>\Delta_\Lambda .
$$

---

## 10. Controls

| Control | Purpose |
|---|---|
| uniform ring | ensures no loop appears from numerical drift |
| symmetric two-pole ring | checks that polarity requires directed asymmetry |
| shuffled conductance control | tests dependence on intended channel structure |
| reversed source/sink initialization | tests directionality |
| zero-flux reset | checks whether loop depends on inherited flux state |
| budget projection disabled only in diagnostic dry run | confirms conservation enforcement is not hiding drift |
| topology disabled | keeps loop experiment separate from refinement/movement |
| source/sink labels randomized after run | ensures classification is state-derived, not label-derived |

---

## Appendix A. Multi-Pole Basin Loops as a Later Generalization

The main experiment studies the minimal case of a polarized basin loop: one
source-like aspect, one sink-like aspect, one forward channel, and one return
channel. This two-aspect construction is intentionally conservative. It is the
smallest configuration in which the experiment can ask whether a single basin
can sustain an internal redistributive loop without external source/sink terms,
topology adaptation, or movement claims.

However, the two-aspect model is not a structural limit. It should be
understood as the minimal member of a broader family of **multi-pole basin
loops**.

### A.1. Generalization from two aspects to \(N\) aspects

Let a parent basin \(B\) contain \(N\) candidate pole regions:

$$
R_1, R_2, \ldots, R_N \subset B
$$

where each \(R_m\) is an experiment-defined candidate aspect region. As in the
two-aspect case, these are not ontological sources or sinks. They are candidate
masks whose functional role must be measured from coherence flux and mass
change.

A pole may be:

- export-biased over a window;
- import-biased over a window;
- phase-shifted relative to other poles;
- transiently neutral;
- part of a return channel;
- or part of a larger closed redistribution network.

The core conservation rule is unchanged:

$$
\sum_i C_i(t) = B
$$

for the whole graph or configured quadrature measure. Multi-pole loops
therefore do not introduce external creation or destruction of coherence. They
are richer internal redistributions inside one tracked basin.

### A.2. Relationship to GRC9V3 row/column structure

The GRC9V3 / G-RC-9 substrate makes multi-pole organization especially natural
because each node has a structured local interface. The two-aspect loop can be
interpreted as a minimal front/rear or emitter/collector polarity. A
three-aspect loop can be mapped to the three columns or the three rows of the
\(3 \times 3\) port bundle. A nine-aspect loop can, in principle, use the full
row-column structure.

A conservative interpretation is:

| Pole count | Possible mapping | Interpretation |
|---:|---|---|
| 2 | opposite columns, opposite arcs, or front/rear masks | minimal source/sink loop |
| 3 | columns \(C_1,C_2,C_3\) or rows \(a=1,2,3\) | triangular loop, phase-shifted redistribution, steering precursor |
| 4 | \(2 \times 2\) subset | cross-channel switching or interference |
| 9 | full \(3 \times 3\) bundle | distributed actuation / full local interface network |

This appendix does not require the first experiment to use these mappings. It
records the extension path: once the two-aspect loop is stable and
reproducible, the same measurement principles can be lifted to multiple pole
regions.

### A.3. Multi-pole interaction matrix

For \(N\) pole regions, define a directed pole-interaction matrix:

$$
P_{mn}(t)
=
\sum_{i\in R_m}
\sum_{j\in R_n}
J_{ij}(t)
$$

where \(P_{mn}(t)\) measures flux from pole \(m\) toward pole \(n\). In
implementation, this must be reconstructed from edge-level oriented flux
evidence, not from labels alone. For GRC9V3 this means using the recorded edge
orientation and `flux_uv` convention, as in the two-aspect experiment.

A stable multi-pole loop is not merely a graph with many candidate regions. It
requires persistent, ordered, measured redistribution among pole regions.

Example loop patterns include:

$$
R_1 \rightarrow R_2 \rightarrow R_3 \rightarrow R_1
$$

for a triangular cycle, or:

$$
R_1 \rightarrow R_2 \rightarrow \cdots \rightarrow R_N \rightarrow R_1
$$

for an \(N\)-pole traveling wave.

### A.4. Network closure score

The two-aspect experiment distinguishes path closure, flux closure, and
repeated cycle closure. The same distinction applies to multi-pole loops.

A candidate network closure score can be defined as:

$$
\Lambda_{\mathrm{net}}
=
\frac{1}{N}
\sum_{m=1}^{N}
\mathbf{1}
\left[
\exists n\neq m:
\langle |P_{mn}(t)| \rangle_W > \theta_{\mathrm{pole}}
\right]
$$

This measures whether every pole participates in nontrivial measured
redistribution over the evaluation window \(W\).

A stricter version requires that the directed graph induced by \(P_{mn}\)
contains at least one closed cycle involving all or most pole regions.

### A.5. Phase pattern score

For each pole \(R_m\), define a mass time series:

$$
C_m(t) = \sum_{i\in R_m} C_i(t)
$$

or the configured quadrature-weighted equivalent.

Extract a phase \(\theta_m\) from the oscillatory component of \(C_m(t)\), using
the declared experiment-local phase method. A simple synchronization index is:

$$
\Phi_{\mathrm{sync}}
=
\left|
\frac{1}{N}
\sum_{m=1}^{N}
e^{i\theta_m}
\right|
$$

However, multi-pole loops need not be in-phase. Some of the most important
cases are phase-shifted. For example, a three-pole traveling wave may have
target phases:

$$
0,\quad \frac{2\pi}{3},\quad \frac{4\pi}{3}
$$

Therefore, the more general metric should be a **phase pattern score**, not
only an in-phase synchronization score.

Possible target patterns:

| Pattern | Meaning |
|---|---|
| `in_phase` | all poles rise/fall together |
| `anti_phase` | two dominant groups alternate |
| `traveling_wave_3` | three poles activate in ordered phase offsets |
| `traveling_wave_9` | nine poles activate around the full port bundle |
| `custom` | experiment-defined phase offsets |

This distinction matters because locomotion-like or steering-like behavior may
require stable phase offsets rather than full synchronization.

### A.6. Fragmentation gate

Multi-pole organization introduces a major failure mode: the parent basin may
split into multiple identity basins. That can be scientifically interesting,
but it is not evidence for a multi-pole loop inside one basin.

Therefore, strong multi-pole claims require a single-parent-basin gate:

$$
R_1,\ldots,R_N \subset B_{\mathrm{parent}}(t)
$$

throughout the evaluation window.

If the pole regions become separate runtime identity basins, the run should be
downgraded or reclassified as a fragmentation/refinement event, not promoted as
a multi-pole loop.

A strict gate may require:

```text
same_parent_basin_mode = "flux_successor_basin"
```

for strong claims. Configured-parent evidence alone should support only
candidate claims.

### A.7. Multi-pole ladder

The two-aspect L0-L6 ladder should remain intact for the first experiment.
Multi-pole loops can later use a separate extension ladder:

| Level | Meaning | Claim ceiling |
|---|---|---|
| MP0 | no coherent multi-pole organization | no multi-pole evidence |
| MP1 | more than two candidate regions show transient role differentiation | multi-pole polarity candidate |
| MP2 | measured directed flux exists between multiple pole regions | multi-pole interaction observed |
| MP3 | a closed multi-pole redistribution path is measured | multi-pole loop candidate |
| MP4 | repeated ordered multi-pole cycle under budget conservation | conserved multi-pole loop |
| MP5 | stable phase-patterned multi-pole cycle | phase-locked or wave-like multi-pole loop |
| MP6 | multi-pole cycle couples to boundary or movement experiment | movement/locomotion precursor only |

MP6 should not itself claim movement inside the polarity-loop paper. It should
hand off to the movement-ladders experiment.

### A.8. Suggested future experiments

The first multi-pole extension should be three-pole, not nine-pole. Three poles
are the smallest nontrivial extension beyond source/sink polarity and map
naturally onto the three rows or three columns of GRC9V3.

Possible extension sequence:

| Surface | Focus | Purpose |
|---|---|---|
| MP-E1 | 3-pole triangular loop on fixed topology | verify \(P_{mn}\), network closure, phase pattern, and single-parent continuity |
| MP-E2 | 3-pole column-mapped GRC9V3 loop | test column/interface specialization |
| MP-E3 | 3-pole row-mapped GRC9V3 loop | test row/directional-mode specialization |
| MP-E4 | 9-pole full-bundle loop | test distributed port-bundle cycling |
| MP-E5 | multi-pole boundary coupling | handoff to movement-ladders experiment |

Controls should include:

- randomized pole labels;
- randomized pole connectivity;
- shuffled conductance or channel assignment;
- single-pole disabled;
- desynchronized phase initialization;
- fragmentation audit.

### A.9. Claim discipline

The first polarity-loop experiment should not depend on multi-pole evidence.
Two-aspect source/sink looping is the minimal proof target. Multi-pole loops
should only be opened after the two-aspect L4 result is stable and
reproducible.

The correct dependency is:

$$
\text{two-aspect loop}
\rightarrow
\text{stable conserved cycle}
\rightarrow
\text{multi-pole internal loop}
\rightarrow
\text{phase-patterned loop}
\rightarrow
\text{boundary-coupled movement precursor}
$$

The guiding claim for this appendix is:

> Two-aspect polarization is the minimal case of a broader \(N\)-pole
> basin-loop family. Multi-pole polarization is structurally compatible with
> GRC9V3 and may later support phase-patterned internal redistribution,
> steering precursors, and movement-coupled dynamics, but it is not part of
> the first fixed-topology loop claim.

---

## 11. Implementation direction

### 11.1 Required runtime surfaces

A GRC9V3 loop runner should emit:

```json
{
  "run_id": "...",
  "substrate_id": "ring_N64_v1",
  "topology_events_enabled": false,
  "budget_initial": 1.0,
  "budget_error_max": 0.0,
  "source_region": [ ... ],
  "sink_region": [ ... ],
  "forward_path": [ ... ],
  "return_path": [ ... ],
  "loop_ladder_status": "L0|L1|L2|L3|L4|L5|L6",
  "claim_ceiling": "...",
  "blocked_claims": [ ... ],
  "timeseries": {
    "C_source": "...",
    "C_sink": "...",
    "J_forward": "...",
    "J_return": "...",
    "polarity_score": "...",
    "closure_score": "..."
  }
}
```

### 11.2 Runner steps

```text
INPUT:
  graph G=(V,E)
  coherence C_i >= 0
  budget B=sum_i C_i
  source/sink candidate regions R_S,R_K
  forward/return paths
  GRC9V3 parameters

FOR k = 0..T:
  1. compute basin attributes:
       g_i, H_i, J_i^net, M_i
  2. compute K_i from C_i, g_i, J_i^net
  3. update conductances w_ij
  4. compute potentials Phi_i
  5. compute antisymmetric flux J_ij
  6. update C_i by continuity
  7. enforce exact budget / simplex projection
  8. identify basins and verify R_S,R_K remain in one parent basin
  9. compute source/sink flux summaries
 10. compute forward/return flux and loop scores
 11. assign L-level by gates
END
```

### 11.3 First implementation tranche

Recommended initial tranche:

```text
L1.0  Build ring substrate generator.
L1.1  Implement region/path masks.
L1.2  Add loop observables.
L1.3  Add conservation/null gates.
L1.4  Run uniform and symmetric nulls.
L1.5  Run structured initialization lanes.
L1.6  Run one-time kick lanes.
L1.7  Add loop ladder classifier L0-L4.
L1.8  Freeze report schema.
```

Do not enable topology events until the loop classifier is stable.

---

## 12. Report schema

Suggested schema name:

```text
grc9v3_polarized_basin_loop_report_v1
```

Required fields:

```json
{
  "schema": "grc9v3_polarized_basin_loop_report_v1",
  "run_id": "",
  "substrate": {
    "type": "ring|ported_ring|custom",
    "node_count": 0,
    "edge_count": 0,
    "topology_events_enabled": false
  },
  "regions": {
    "source_aspect_nodes": [],
    "sink_aspect_nodes": [],
    "forward_path_edges": [],
    "return_path_edges": []
  },
  "conservation": {
    "budget_initial": 0.0,
    "budget_final": 0.0,
    "budget_abs_error_max": 0.0,
    "simplex_projection_count": 0
  },
  "loop_metrics": {
    "polarity_score_max": 0.0,
    "closure_score_max": 0.0,
    "cycles_detected": 0,
    "phase_relation_status": "pass|fail|na",
    "self_regulation_status": "pass|fail|na"
  },
  "ladder": {
    "L0_no_loop": "pass|fail",
    "L1_transient_polarity": "pass|fail",
    "L2_paired_source_sink": "pass|fail",
    "L3_return_refill": "pass|fail",
    "L4_repeated_conserved_cycle": "pass|fail",
    "L5_self_regulating_cycle": "pass|fail|not_tested",
    "L6_boundary_couplable_loop": "pass|fail|not_tested"
  },
  "claim_ceiling": "",
  "blocked_claims": []
}
```

---

## 13. Claim language

Allowed:

- polarized basin loop
- source-aspect / sink-aspect
- emitter pole / collector pole
- closed redistributive cycle
- conserved internal pulse
- internal loop candidate
- self-regulating pulse candidate
- locomotion precursor

Blocked in this paper:

- locomotion
- movement proof
- agency
- choice
- intention
- biological motility
- autonomous organism
- external energy source
- non-conserved source/sink
- stable learned memory

Preferred positive claim if L4 passes:

> A single GRC9V3 basin can sustain a conserved internal source–sink loop in which an emitter aspect exports coherence, a collector aspect imports it, and a return channel refills the emitter over repeated cycles.

Preferred positive claim if L5 passes:

> The polarized basin loop behaves as a self-regulating conserved pulse generator under bounded perturbation.

Current D2.3/native-LGRC branch claim after native LGRC9V3 reproduction:

> Native LGRC9V3 packetized causal execution reproduces a conserved
> self-rearming polarized packet loop under controls.

This is not a native GRC9V3 proposal-flux loop claim. It is a causal-history
packet-loop claim.

---

## 14. Relationship to the movement paper

This paper supplies the pulse mechanism. It does not test movement.

The dependency is:

$$
\text{polarity}
\rightarrow
\text{source–sink loop}
\rightarrow
\text{conserved pulse cycle}
\rightarrow
\text{boundary-coupled movement}
$$

The final arrow belongs to the second paper.

---

## 15. Current two-layer result

The completed D2.3/native-LGRC packet-loop branch gives a two-layer result.
This does not close every possible N03 follow-up. It closes the branch that
starts with the negative fixed-topology GRC9V3 result, discovers the packetized
causal handoff mechanism, and reproduces that mechanism with native LGRC9V3
packet-loop surfaces.

### 15.1 Negative synchronous result

Native fixed-topology GRC9V3 proposal flux did **not** produce polarized loops
on the tested fixtures.

This negative result covers the tested synchronous/fixed-topology proposal
surface:

```text
fixed-topology GRC9V3 continuity
native proposal flux
plain two-aspect rings
amplitude, mask, scale, spacing, and conductance-corridor diagnostics
delayed accumulator and release-policy variants
three-pole accumulator variants
circulation, rotation, and initial-flux audits
```

The interpretation is:

```text
GRC9V3 proposal flux behaves primarily as a conservative relaxation surface,
not as an endogenous phase-organizing loop generator on these fixtures.
```

### 15.2 Positive causal-history result

Native LGRC9V3 packetized causal execution **does** reproduce the
self-rearming polarized packet loop under controls.

The native packet-loop branch classification is:

```text
native_d2_3_equivalent_packet_loop_supported
adapter_required_for_d2_3_semantics = false
native_static_route_only = false
```

The N03 E3 native reproduction verifies:

```text
native_lgrc9v3_execution = true
native_packet_execution = true
native_surplus_trigger = true
native_self_rearm_evidence = true
native_d2_3_equivalent = true
controls_passed = true
snapshot_telemetry_replayable = true
```

Both directions pass:

```text
clockwise:         S1 -> K2 -> S2 -> K1 -> S1
counter-clockwise: S1 -> K1 -> S2 -> K2 -> S1
```

and the required controls remain negative:

```text
no_surplus
subthreshold
threshold_too_high
wrong_direction
forward_only
broken_return
scrambled_order
```

### 15.3 Claim boundary

The supported result is:

```text
native LGRC9V3 causal packet-loop support
```

The following remain blocked:

```text
native GRC9V3 proposal-flux loop evidence
movement or locomotion
agency, intention, or biological behavior
identity acceptance
multi-pole generalization
```

### 15.4 Remaining N03 scope

The broader N03 experiment family remains open for work that was explicitly
deferred or not exercised by the D2.3/native-LGRC branch, including:

```text
movement-ladder handoff
boundary-coupled pulse experiments
multi-pole basin loops
larger fixture families
output bundling / artifact cleanup
paper polish against the full implementation record
```

Those should be opened as separate branches with their own controls and claim
boundaries. They should not be inferred from the D2.3/native-LGRC closeout.

## 16. Summary

The source–sink idea is best treated as an internal **polarity loop** experiment, not as a movement experiment. The goal is to verify whether the GRC9V3 execution layer can support a conservative, recurrent intra-basin redistribution cycle. If it can, it becomes the natural source of pulses for later movement studies. If it cannot, movement experiments should not assume an internal drive and should remain limited to one-time perturbation or externally scheduled zero-sum steering.

The current D2.3/native-LGRC branch resolves its central question by separating
execution surfaces. Native fixed-topology GRC9V3 proposal flux did not produce
the loop, while native LGRC9V3 packetized causal execution did reproduce the
self-rearming loop under controls. This establishes the pulse prerequisite only
for the packetized causal-history execution surface:

> Before a basin can move itself, it must be able to pulse itself.

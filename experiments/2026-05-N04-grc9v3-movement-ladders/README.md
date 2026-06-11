---
title: "Movement Ladders from Polarized Basin Loops in GRC9V3"
subtitle: "Identity-Preserving Displacement, Boundary Coupling, and Locomotion-Like Cycles"
version: "draft v0.1"
date: "2026-05-15"
status: "research scaffold / implementation-ready draft"
license: "CC BY-SA 4.0"
---

# Movement Ladders from Polarized Basin Loops in GRC9V3

## Abstract

This paper defines the second experiment family in the GRC9V3 movement program. The first experiment family studies **polarized basin loops**: conserved source–sink cycles inside a single basin. This paper treats movement as an extension of that loop mechanism. The core hypothesis is that a loop-polarized basin can convert internal pulses into measurable displacement when the loop couples asymmetrically to basin boundary, substrate geometry, or front/rear polarity.

Movement is not defined as Euclidean translation of a rigid object. In Reflexive Coherence and GRC, an identity is a basin-like attractor structure. Movement therefore means identity-preserving change in representative location, support assignment, boundary shape, internal geometry, and possibly substrate representation. Locomotion-like behavior is a stricter condition: repeated displacement that preserves identity, regenerates polarity, manages boundary, maintains shape envelope, and remains globally budget-conserving.

This paper provides the movement taxonomy, substrate taxonomy, pulse taxonomy, persistence and identity-continuity gates, front/rear polarity gates, boundary-management gates, shape-preservation gates, aftereffect/highway gates, implementation direction, and claim ceilings.

---

## 1. Motivation

A localized basin can be displaced by a one-time conserved perturbation, but that is not yet locomotion. Locomotion-like dynamics require a closed cycle:

```text
internal loop creates pulse
    -> pulse couples to front/rear polarity
    -> basin boundary shifts
    -> identity remains continuous
    -> geometry/loop regenerates the next pulse
```

The movement program should therefore not begin with repeated external forcing. It should inherit the loop mechanism from the polarized basin loop experiment and then ask:

> Which forms of movement become possible when conserved internal pulses couple to basin geometry and boundary?

This paper organizes that question into a staged ladder.

---

## 2. Background: movement as basin kinematics

An identity is not a point moving through a container. It is a basin-like coherent region whose current representation may change over time.

Movement has at least three components:

1. **Drift** — the basin representative shifts.
2. **Deformation** — the boundary expands, contracts, or reshapes.
3. **Reorganization** — internal coherence, flux, curvature, conductance, and basin attributes change.

On a graph, a basin at time \(k\) may be represented by an induced subgraph:

$$
G_b(k)=G[B_b(k)].
$$

But the identity is not the subgraph itself. The identity is the tracked attractor/basin continuity:

$$
I_b \quad \text{with current support} \quad B_b(k).
$$

Thus a better statement is:

> The identity persists while its current graph support, routing domain, representative location, and internal geometry change.

This distinction prevents the misleading image of a rigid subgraph sliding through a fixed background.

---

## 3. Execution-layer assumptions

The execution layer is GRC9V3: the G-RC-9 mechanical substrate read through GRC-v3 basin attributes.

Core state:

$$
C_i,\quad w_{ij},\quad \Phi_i,\quad J_{ij},\quad \mathcal B_i .
$$

Basin-attribute state:

$$
\mathcal B_i =
(C_i,\mathbf g_i,\widetilde H_i,\mathbf J_i^{net},M_i,id_i,parent_i,depth_i).
$$

Core loop:

$$
C \rightarrow K[C] \rightarrow w \rightarrow \Phi \rightarrow J \rightarrow C.
$$

Budget:

$$
B=\sum_i C_i
$$

under unit-measure convention, or:

$$
B=\sum_i \mu_i C_i
$$

when node measures are active.

Topology events should be disabled in the first movement tranche. They are enabled only after fixed-substrate movement has been demonstrated.

Adaptive topology is not allowed to promote movement class. It may only be
evaluated after fixed-substrate loop-driven movement has already achieved the
declared fixed-substrate entry gate. This prevents front birth, rear pruning,
or spark refinement from being misread as movement before the non-topological
movement mechanism has been established.

---

## 4. Relationship to polarized basin loops

This paper assumes or imports the loop ladder from the first paper:

| Loop level | Meaning |
|---|---|
| L0 | no internal loop |
| L1 | transient source/sink polarity |
| L2 | paired source/sink aspects |
| L3 | return path refills source-aspect |
| L4 | repeated conserved cycle |
| L5 | self-regulating cycle |
| L6 | loop can couple to boundary/front-rear asymmetry |

Movement experiments should state which loop level is available. The strongest movement claims require at least L4. Locomotion-like claims likely require L5 or L6.

---

## 5. Movement taxonomy M0–M6

| Level | Name | Meaning | Claim ceiling |
|---|---|---|---|
| M0 | no movement | No meaningful centroid, boundary, or routing shift. | no movement |
| M1 | centroid drift | Basin representative shifts, but boundary/support change is weak or absent. | drift response |
| M2 | boundary reassignment | Basin support changes by node flips or threshold crossing on fixed topology. | boundary movement |
| M3 | shape-preserving displacement | Representative and support shift while mass/width/profile remain within tolerance. | identity-basin movement |
| M4 | front/rear coordinated movement | Leading edge advances and trailing edge retracts in coordinated phase. | organized movement |
| M5 | repeated loop-driven displacement | A polarized loop produces repeated movement pulses over a finite window. | locomotion precursor |
| M6 | locomotion-like cycle | Movement regenerates the polarity/geometry required for continued movement. | locomotion-like basin dynamics |

M6 is still not a claim of agency, intention, or biological locomotion. It is a bounded dynamical claim.

---

## 6. Substrate taxonomy

| Level | Substrate | Purpose |
|---|---|---|
| S0 | 1D chain | Cleanest proof of left/right drift and conservation. |
| S1 | 1D ring | Closed-loop pulse testing; movement only if symmetry is broken. |
| S2 | 1D chain with loop-internal actuator abstraction | Tests loop-driven displacement without 2D ambiguity. |
| S3 | 2D grid | Shows deformation, lateral spread, corridor following. |
| S4 | 2D corridor / track | Tests sustained directional movement under constrained geometry. |
| S5 | two-route substrate | Tests shortest-vs-fastest/operational route effects. |
| S6 | adaptive graph | Enables growth, pruning, refinement. |
| S7 | full GRC9V3 port graph | Tests nine-slot mechanical interface, row/column effects, and local refinement. |

Recommended order:

$$
S0 \rightarrow S1 \rightarrow S3 \rightarrow S4 \rightarrow S7 .
$$

Do not begin with S7 unless the goal is specifically port mechanics. The movement phenomenon itself should first be isolated in S0/S1.

---

## 7. Pulse/drive taxonomy

| Lane | Name | Description | Interpretation |
|---|---|---|---|
| P0 | no pulse | No intentional asymmetry after initialization. | intrinsic/free movement test |
| P1 | one-time conserved kick | A single zero-sum perturbation at \(k=0\). | movement response |
| P2 | scheduled repeated pulses | Fixed-cadence zero-sum pulses. | steerability, not intrinsic locomotion |
| P3 | loop-generated pulses | Pulses arise from L4/L5 polarized loop. | internal drive candidate |
| P4 | state-triggered pulses | Pulses triggered by basin state thresholds. | feedback drive |
| P5 | self-renewing pulses | Movement restores the conditions for the next pulse. | locomotion-like drive |

The preferred movement paper begins with P0/P1 controls and then uses P3/P4 once Experiment 1 provides loop evidence.

---

## 8. Persistence taxonomy

| Level | Meaning |
|---|---|
| T0 | no displacement |
| T1 | transient displacement |
| T2 | displacement followed by settling |
| T3 | sustained drift over a finite window |
| T4 | repeatable displacement under same protocol |
| T5 | cyclic or renewable displacement |
| T6 | displacement cycle recovers after perturbation |

Movement can be M1 but only T1. Locomotion-like behavior requires at least T5.

---

## 9. Identity-continuity taxonomy

A movement claim is invalid unless identity continuity is tracked.

| Level | Meaning |
|---|---|
| I0 | no stable basin identity |
| I1 | representative moves but identity unclear |
| I2 | same basin by maximum overlap |
| I3 | same basin by overlap plus mass preservation |
| I4 | same basin by overlap plus flux-routing continuity |
| I5 | same basin by overlap plus internal geometry continuity |
| I6 | identity survives split/merge through parent/child tracking |

Recommended identity continuity score:

$$
S_{bb'}(k,k+1)
=
\frac{
\sum_{i\in B_b(k)\cap B_{b'}(k+1)} C_i^{(k)}
}{
\sum_{i\in B_b(k)} C_i^{(k)}
}.
$$

Require mutual best match for I2+, and add mass/geometric constraints for I3+.

---

## 10. Front/rear polarity taxonomy

Locomotion-like movement requires front/rear organization.

| Level | Meaning |
|---|---|
| R0 | no front/rear distinction |
| R1 | transient flux imbalance |
| R2 | persistent leading-edge gain and trailing-edge loss |
| R3 | front/rear geometry differentiates |
| R4 | front advances while rear retracts |
| R5 | polarity survives displacement |
| R6 | polarity resets/re-establishes after perturbation |

Define front/rear relative to intended displacement direction or discovered centroid velocity:

$$
v_b(k)=x_{\mathrm{cen}}(k+1)-x_{\mathrm{cen}}(k).
$$

Then leading boundary nodes are those with positive projection along \(v_b\); trailing boundary nodes have negative projection.

---

## 11. Boundary-management taxonomy

| Level | Meaning |
|---|---|
| B0 | centroid moves, boundary unchanged |
| B1 | boundary nodes flip assignment |
| B2 | leading boundary advances |
| B3 | trailing boundary retracts |
| B4 | front/rear boundary changes are coordinated |
| B5 | boundary motion preserves mass/shape envelope |
| B6 | boundary management works with growth/pruning enabled |

Boundary node flips:

$$
N_{\mathrm{flip}}(k)=|\{i: b_i(k)\ne b_i(k+1)\}|.
$$

Leading edge advance:

$$
A_{\mathrm{front}}(k)=
\sum_{i\in B(k+1)\setminus B(k)}
C_i^{(k+1)}\mathbf 1[\langle x_i-x_{\mathrm{cen}},v_b\rangle>0].
$$

Trailing retraction:

$$
R_{\mathrm{rear}}(k)=
\sum_{i\in B(k)\setminus B(k+1)}
C_i^{(k)}\mathbf 1[\langle x_i-x_{\mathrm{cen}},v_b\rangle<0].
$$

---

## 12. Shape-preservation taxonomy

| Level | Meaning |
|---|---|
| G0 | basin disperses |
| G1 | centroid moves but shape degrades |
| G2 | mass/width roughly preserved |
| G3 | profile class preserved after displacement |
| G4 | profile deforms but recovers |
| G5 | shape preserved under repeated movement cycles |
| G6 | shape adapts to environment while identity remains coherent |

Use mass, width, profile similarity, and Hessian/gradient summaries:

$$
M_b(k)=\sum_{i\in B(k)} C_i^{(k)}
$$

$$
\sigma_b^2(k)=
\frac{\sum_{i\in B(k)} C_i^{(k)}\|x_i-x_{\mathrm{cen}}\|^2}
{\sum_{i\in B(k)} C_i^{(k)}} .
$$

A simple profile similarity after aligning centroids:

$$
P_{\mathrm{sim}}(k,k+\Delta)
=
\operatorname{corr}
\left(
C_{B(k)}^{aligned},
C_{B(k+\Delta)}^{aligned}
\right).
$$

The minimum quantitative shape gates are:

$$
G2_{\mathrm{width}}:
\frac{|\sigma_b(k)-\sigma_b(0)|}{\sigma_b(0)} < 0.15 .
$$

$$
G3_{\mathrm{profile}}:
P_{\mathrm{sim}}(k) > 0.8
$$

after centroid alignment.

These gates distinguish coherent basin movement from spreading, smearing, or
dissolution. Hessian summaries should preserve legitimate front/rear polarity
while blocking runaway deformation. The gate is therefore bounded imbalance,
not front/rear equality:

$$
G3_H:
|\operatorname{Tr}(H_{\mathrm{front}})
-\operatorname{Tr}(H_{\mathrm{rear}})|
< H_{\Delta,\max}.
$$

Optionally also require:

$$
\max(
|\operatorname{Tr}(H_{\mathrm{front}})|,
|\operatorname{Tr}(H_{\mathrm{rear}})|
)
< H_{\max}.
$$

---

## 13. Environment / affordance taxonomy

| Level | Meaning |
|---|---|
| E0 | uniform substrate |
| E1 | gradient substrate |
| E2 | corridor substrate |
| E3 | two-route substrate |
| E4 | obstacle/barrier substrate |
| E5 | resource-pocket substrate |
| E6 | changing substrate |

The two-route substrate is especially useful later because it can distinguish geometric shortest path from operational fastest path. A loop-driven basin may prefer a longer high-coupling path over a shorter low-coherence path if the operational travel-time labels favor it.

---

## 14. Geometry-memory / highway taxonomy

Movement may leave an aftereffect. This is where movement connects to geometric learning.

| Level | Meaning |
|---|---|
| H0 | no persistent path effect |
| H1 | temporary flux trace |
| H2 | conductance changes along traversed path |
| H3 | later movement is faster/easier along the same path |
| H4 | path survives after perturbation stops |
| H5 | path biases future route choice |
| H6 | path becomes reusable locomotion channel |

Path aftereffect should be tested with replay:

1. run movement over path \(P\),
2. reset or preserve selected state layers,
3. rerun same perturbation,
4. compare return time, conductance, flux coupling, centroid displacement, and route selection.

---

## 15. Energy/budget economy taxonomy

| Level | Meaning |
|---|---|
| Q0 | budget violation |
| Q1 | budget conserved but identity mass leaks heavily |
| Q2 | identity mass mostly preserved |
| Q3 | movement cost measurable as redistribution load |
| Q4 | repeated movement has bounded cost |
| Q5 | movement becomes cheaper along a reused path |
| Q6 | locomotion cycle maintains budget, identity, polarity, and bounded cost |

Movement cost can be measured as total redistribution load:

$$
\mathcal C_{\mathrm{move}}(k)
=
\sum_{(i,j)\in E}|J_{ij}^{(k)}|
$$

or normalized by displacement:

$$
\mathcal E_{\mathrm{per\_step}}
=
\frac{\sum_{k}\sum_{(i,j)}|J_{ij}^{(k)}|}
{\epsilon+\|x_{\mathrm{cen}}(T)-x_{\mathrm{cen}}(0)\|}.
$$

---

## 16. Control/feedback taxonomy

| Level | Meaning |
|---|---|
| F0 | open-loop external pulses |
| F1 | scheduled pulses independent of state |
| F2 | pulses triggered by basin state |
| F3 | internal front/rear imbalance triggers redistribution |
| F4 | basin geometry modulates its own mobility |
| F5 | closed locomotion cycle: state creates drive, drive moves basin, movement restores state |
| F6 | adaptive locomotion across changing substrates |

The critical transition is:

$$
F2/F3 \rightarrow F5.
$$

That is where movement becomes self-renewing rather than externally scheduled.

---

## 17. Experimental phases

### Phase 1: Movement exists

Substrate: 1D chain.  
Loop: optional; not required.  
Drive: P0/P1.  
Topology: fixed.

Required gates:

$$
M\ge 1,\quad I\ge 2,\quad T\ge 1,\quad Q\ge 2.
$$

Claim ceiling:

> A conserved perturbation produces transient identity-basin movement.

### Phase 2: Movement is organized

Substrate: 1D chain or ring.  
Drive: initialized asymmetry or one-time kick.  
Topology: fixed.

Required gates:

$$
R\ge 2,\quad B\ge 2,\quad G\ge 2.
$$

Claim ceiling:

> Basin movement has front/rear polarity and preserves a coherent profile.

### Phase 3: Loop-driven movement

Substrate: 1D ring with broken symmetry or 2D narrow corridor.  
Loop: L4+.  
Drive: P3/P4.

Required gates:

$$
M\ge 3,\quad L\ge 4,\quad T\ge 3,\quad I\ge 3.
$$

Claim ceiling:

> A conserved internal loop can drive repeated basin displacement over a finite window.

### Phase 4: Movement leaves a path

Substrate: 2D corridor or two-route environment.  
Loop: L4/L5.  
Drive: P3/P4.

Required gates:

$$
H\ge 3,\quad Q\ge 3.
$$

Claim ceiling:

> Prior movement creates a reusable geometric or operational aftereffect.

### Phase 5: Locomotion-like cycle

Substrate: 2D grid, corridor, or GRC9V3 port graph.  
Loop: L5/L6.  
Drive: P5.  
Topology: fixed first; adaptive later.

Required gates:

$$
M\ge 6,\quad
L\ge 5,\quad
T\ge 5,\quad
I\ge 4,\quad
R\ge 5,\quad
B\ge 5,\quad
G\ge 4,\quad
Q\ge 4,\quad
F\ge 5.
$$

Claim ceiling:

> A loop-polarized basin shows locomotion-like dynamics: repeated identity-preserving displacement that regenerates front/rear polarity and remains globally budget-conserving.

### Phase 6: Adaptive locomotion-like movement

Substrate: full GRC9V3 port graph.  
Topology: growth/pruning/spark refinement enabled.  
Loop: L5/L6.  
Drive: P5.

Entry condition:

$$
fixed\_substrate\_movement\_passed = true.
$$

At minimum this requires fixed-substrate loop-driven movement to have already
passed:

$$
M\ge 5,\quad I\ge 4,\quad R\ge 4,\quad S\ge 3,\quad Q\ge 4.
$$

Additional gates:

$$
B\ge 6,\quad H\ge 5,\quad E\ge 4.
$$

The \(B\ge 6\) adaptive boundary-management claim is valid only after the
fixed-substrate movement gate has passed. Adaptive topology may explain how
movement couples to substrate change; it may not be used as a shortcut to
claim movement that was not already present on fixed topology.

Claim ceiling:

> Movement couples to substrate refinement, producing adaptive locomotion-like basin dynamics.

---

## 18. Minimal first movement experiment

Use a 1D chain:

$$
0-1-2-\cdots-N .
$$

Run four cases:

| Case | Initialization | Perturbation | Expected |
|---|---|---|---|
| U0 | uniform \(C_i=C_0\) | none | no movement |
| B0 | symmetric basin bump | none | no directed movement |
| B1 | asymmetric basin bump | none after init | drift/settling possible |
| K1 | symmetric basin + one-time zero-sum kick | one at \(k=0\) | induced drift |

Canonical asymmetric-basin initialization in 1D:

$$
C_i =
C_0
+
A\exp\left(-\frac{(i-i_0)^2}{2\sigma^2}\right)
+
\epsilon(i-i_0)
\exp\left(-\frac{(i-i_0)^2}{2\sigma_{\mathrm{tilt}}^2}\right).
$$

The tilt term is locally tapered so the experiment tests movement from basin
asymmetry rather than drift down a global background gradient.

After initialization, project/renormalize to the conserved nonnegative
simplex:

$$
\sum_i C_i = B,
\qquad
C_i\ge 0 .
$$

Centroid:

$$
x_{\mathrm{cen}}(k)
=
\frac{\sum_{i\in B(k)} x_i C_i^{(k)}}{\sum_{i\in B(k)} C_i^{(k)}}.
$$

Movement response:

$$
\Delta x_{\mathrm{cen}}
=
x_{\mathrm{cen}}(T)-x_{\mathrm{cen}}(0).
$$

Conservation:

$$
\left|\sum_i C_i^{(k)}-\sum_i C_i^{(0)}\right|<\epsilon_B .
$$

---

## 19. Loop-driven movement experiment

After the loop paper establishes L4+, use a ring or narrow 2D corridor with source/sink-aspect regions embedded asymmetrically relative to a boundary.

Possible 1D ring-to-chain bridge:

1. source-aspect near rear,
2. sink-aspect near front,
3. forward channel loads front boundary,
4. return channel refills source-aspect,
5. basin support shifts forward if leading boundary gain exceeds trailing loss.

Detection pattern:

$$
C_S\downarrow
\Rightarrow
J_{\mathrm{fwd}}\uparrow
\Rightarrow
C_{\mathrm{front}}\uparrow
\Rightarrow
B_{\mathrm{front}}\text{ advances}
\Rightarrow
J_{\mathrm{return}}\uparrow
\Rightarrow
C_S\uparrow .
$$

This is the first place movement should be claimed as loop-driven.

---

## 20. Report schema

Suggested schema name:

```text
grc9v3_movement_ladder_report_v1
```

Required fields:

```json
{
  "schema": "grc9v3_movement_ladder_report_v1",
  "run_id": "",
  "substrate": {
    "type": "chain|ring|grid|corridor|two_route|grc9v3_port_graph",
    "node_count": 0,
    "edge_count": 0,
    "topology_events_enabled": false
  },
  "loop_dependency": {
    "loop_report_id": "",
    "loop_ladder_level": "L0|L1|L2|L3|L4|L5|L6|not_used",
    "loop_phase_lock": 0.0
  },
  "drive": {
    "pulse_lane": "P0|P1|P2|P3|P4|P5",
    "external_source_terms": false,
    "budget_preserving": true
  },
  "identity_tracking": {
    "method": "overlap|overlap_mass|overlap_flux|overlap_geometry|parent_child",
    "min_similarity": 0.0,
    "identity_continuity_level": "I0|I1|I2|I3|I4|I5|I6"
  },
  "movement_metrics": {
    "centroid_displacement": 0.0,
    "boundary_flip_count": 0,
    "front_advance_mass": 0.0,
    "rear_retraction_mass": 0.0,
    "boundary_coupling_score": 0.0,
    "shape_similarity": 0.0,
    "width_relative_change": 0.0,
    "front_rear_hessian_trace_delta": 0.0,
    "movement_cost": 0.0,
    "highway_replay_improvement": 0.0
  },
  "taxonomies": {
    "movement_level": "M0|M1|M2|M3|M4|M5|M6",
    "substrate_level": "S0|S1|S2|S3|S4|S5|S6|S7",
    "persistence_level": "T0|T1|T2|T3|T4|T5|T6",
    "front_rear_level": "R0|R1|R2|R3|R4|R5|R6",
    "boundary_level": "B0|B1|B2|B3|B4|B5|B6",
    "shape_level": "G0|G1|G2|G3|G4|G5|G6",
    "environment_level": "E0|E1|E2|E3|E4|E5|E6",
    "highway_level": "H0|H1|H2|H3|H4|H5|H6",
    "budget_economy_level": "Q0|Q1|Q2|Q3|Q4|Q5|Q6",
    "feedback_level": "F0|F1|F2|F3|F4|F5|F6"
  },
  "conservation": {
    "budget_initial": 0.0,
    "budget_final": 0.0,
    "budget_abs_error_max": 0.0,
    "identity_mass_ratio_min": 0.0
  },
  "gates": {
    "fixed_substrate_gate_passed": false,
    "adaptive_topology_entry_allowed": false
  },
  "claim_ceiling": "",
  "blocked_claims": []
}
```

`loop_phase_lock` measures whether source/sink oscillation and return flow keep
a stable phase relation. It supports L4/L5 loop claims.

`boundary_coupling_score` measures whether internal loop pulses couple to
front/rear boundary change. It supports the L6 to M4/M5 bridge.

`highway_replay_improvement` measures whether a previously traversed path
improves later movement efficiency. It supports H3/H4/H5 claims.

`fixed_substrate_gate_passed` records whether adaptive topology is allowed to
be interpreted as an extension of movement rather than as the movement source
itself.

---

## 21. Implementation direction

### 21.1 Runner tranche A: fixed-substrate movement

```text
M-A1  Add chain/ring/grid substrate generators.
M-A2  Add basin initializer: symmetric bump, locally tapered asymmetric bump,
      loop-polarized profile, and conserved nonnegative projection.
M-A3  Add zero-sum perturbation API.
M-A4  Add centroid, mass, width, profile similarity metrics.
M-A5  Add basin extraction / tracking.
M-A6  Add movement ladder classifier M0-M3.
M-A7  Run nulls and one-time-kick lanes.
M-A8  Freeze fixed-substrate report schema.
```

### 21.2 Runner tranche B: loop-driven movement

```text
M-B1  Import loop report / loop level.
M-B2  Add source/sink phase observables to movement runner.
M-B3  Add front/rear boundary masks.
M-B4  Add loop-to-boundary coupling metrics.
M-B5  Classify M4-M5.
M-B6  Run symmetric-coupling null and asymmetric-coupling positive lanes.
```

### 21.3 Runner tranche C: locomotion-like cycle

```text
M-C1  Add self-renewing pulse detection.
M-C2  Add polarity regeneration metrics.
M-C3  Add repeated-cycle persistence windows.
M-C4  Add movement cost / economy metrics.
M-C5  Classify M6 only if all required gates pass.
```

### 21.4 Runner tranche D: adaptive substrate

```text
M-D1  Enable growth/pruning under explicit policy only after
      fixed_substrate_movement_passed=true.
M-D2  Enable GRC9V3 spark refinement under strict gates only after
      fixed_substrate_movement_passed=true.
M-D3  Add parent/child identity tracking.
M-D4  Re-run loop-driven movement with topology enabled.
M-D5  Classify adaptive movement only if fixed-substrate controls remain valid.
```

---

## 22. Controls

| Control | Purpose |
|---|---|
| uniform field | should not move |
| symmetric basin | should not have directed drift |
| one-time kick with reversed sign | drift should reverse |
| loop enabled but symmetric boundary coupling | cycle without net movement |
| loop disabled but same boundary geometry | movement should weaken/disappear |
| shuffled source/sink regions | tests whether phase relation is real |
| topology disabled vs enabled | separates movement from representation adaptation |
| budget projection audit | ensures conservation is not concealing numerical errors |
| identity tracking null | rejects apparent movement caused by basin replacement |

---

## 23. Blocked claims

Unless explicitly gated, do not claim:

- biological locomotion,
- agency,
- intention,
- decision-making,
- semantic goal-seeking,
- autonomous organism,
- cognitive learning,
- stable memory,
- external energy harvesting,
- movement through absolute Euclidean space,
- graph topology change as movement itself.

Allowed language:

- movement response,
- basin drift,
- identity-preserving displacement,
- boundary-coupled movement,
- loop-driven movement,
- locomotion-like basin dynamics,
- conserved pulse-driven displacement,
- movement aftereffect,
- reusable path/highway candidate.

Preferred strong claim if Phase 5 passes:

> A loop-polarized GRC9V3 basin can exhibit locomotion-like dynamics: repeated identity-preserving displacement driven by an internal conserved pulse cycle that regenerates front/rear polarity under exact global budget conservation.

---

## 24. Summary

This paper turns movement into a gated research program rather than a single demonstration. The first paper asks whether a basin can generate conserved internal pulses. This paper asks whether those pulses can be coupled to boundary and geometry to produce identity-preserving movement.

The conceptual dependency is:

$$
\text{source/sink polarity}
\rightarrow
\text{closed internal loop}
\rightarrow
\text{conserved pulse cycle}
\rightarrow
\text{front/rear coupling}
\rightarrow
\text{boundary displacement}
\rightarrow
\text{locomotion-like cycle}.
$$

The core test for locomotion-like behavior is not whether a basin moves once. It is whether movement regenerates the condition for further movement:

> Does the basin move, preserve identity, maintain shape, manage its boundary, and restore the polarity needed to move again?

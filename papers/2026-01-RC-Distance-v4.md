---
title: "RC Geometry: Induced Distance and Support-Derived Space"
version: v4 (narrative + rigor, Riemannian core)
author: Uros Jovanovic
license: CC BY-SA 4.0
date: 2026-01-19
---
# RC Geometry: Induced Distance and Support-Derived Space

Copyright © 2026 Uroš Jovanovič, CC BY-SA 4.0.

**Thesis:** In Reflexive Coherence, space is not a background container: **space is the support of coherence**, and "spacetime growth" is **refinement of that support and its induced metric**, not extension of coordinates.

## Roadmap (what we will show and why)

We make one nonstandard claim and support it with explicit constructions and proofs:

1. **Space is derived.** We define the instantaneous spatial domain as
   $\Omega_t := \mathrm{supp}\,C(\cdot,t)$, so "where the system exists" is determined by coherence itself.

2. **Geometry is derived.** From $C$ we construct a tensor $K[C]$ and an induced metric $g[C]$, and we show that the induced metric is **positive-definite** wherever $C>0$, hence Riemannian.

3. **Distance is derived.** Once $g$ exists, geodesic distance is canonical. We emphasize what is RC-specific: the metric (and even the domain) is state-dependent, so distances can change as coherence reorganizes.

4. **Growth is refinement, not coordinate extension.** We make precise how discrete topology changes of $\Omega_t$ can occur under smooth evolution of $C$, and we identify the critical degeneracy ("spark") at which basin split/merge events can occur.

5. **Flux induces anisotropy.** We show how the flux term in $K$ produces directional deformation of $g$, yielding intrinsic "highways" aligned with coherent currents.

6. **Continuum-to-discrete bridge.** We show how the continuum construction induces a discrete weighted graph distance, making refinement events explicit as split/merge operations on the topological skeleton.

## Notation and conventions (kept minimal)


- $x\in\mathbb{R}^d$: chart coordinates (a reference frame, not "space itself").
- $t\in[0,T]$: time parameter.
- $C(x,t)\ge 0$: coherence density (the only primitive).
- $\Omega_t := \mathrm{supp}\,C(\cdot,t)$: emergent spatial domain at time $t$.
- $B_i(t)$: connected components ("identity basins") of $\Omega_t$.
- $\nabla$: covariant derivative associated with the induced metric (when defined).
- Indices $\mu,\nu$ run over spatial coordinates $1,\dots,d$.
- $g^{(\mathrm{aux})}_{\mu\nu}$: an auxiliary chart metric used only for index bookkeeping (typically Euclidean).
- **Covariant derivative convention.** Before the induced metric $g$ is constructed, $\nabla$ denotes differentiation with respect to the auxiliary chart structure (equivalently, ordinary derivatives in the chosen chart). After $g$ is defined, $\nabla$ denotes the Levi-Civita covariant derivative of $g$ unless stated otherwise. In computations, we keep this explicit by writing $\nabla^{(\mathrm{aux})}$ and $\nabla^{(g)}$ when ambiguity matters.


## Standing assumptions and well-posedness (for the constructions used here)

To avoid implicit circularity, we make the following standing assumptions explicit. They are mild, standard in geometric PDE settings, and match typical computational practice.

1. **Regularity.** $C(x,t)$ is at least $C^2$ in $x$ and $C^1$ in $t$ on regions of interest; the transport quantities (e.g., $v_C$, hence $j=Cv_C$) are sufficiently regular as functionals of $C$ to make $K[C]$ and $g[C]$ well-defined and continuous in $x$ and $t$.
2. **Coefficient signs (Riemannian core).** We take $\lambda_C>0$ and (for the positivity argument as stated) $\xi_C,\zeta_C\ge 0$, with $g^{(\mathrm{aux})}$ positive-definite.
3. **Domain of definition.** Geometric objects are defined on the interior where coherence is positive, and (for boundary control) on the regularized domains $\Omega_t^\varepsilon$ introduced in Section 3.5.
4. **Operator convention.** Gradient and divergence in transport equations are understood with respect to the same explicit choice (auxiliary vs induced) stated in the notation above; where the distinction is immaterial we suppress it.
5. **Scope near sparks.** Differential-geometric statements are made on regions away from spark events; topology-changing transitions are treated as controlled limits from either side.

These assumptions are not additional postulates of RC; they are the minimal technical hypotheses under which the constructions in this paper are mathematically well-posed.


# 1. Why distance needs an explicit construction in RC

Many geometric and physical frameworks treat the ambient point set (and often a metric) as prior structure. In RC, this would obscure the central commitment: coherence is primitive, while the domain of existence and the geometry are derived. Accordingly, we proceed by constructing (i) the instantaneous spatial domain from the support of coherence and (ii) a metric as a functional of coherence, from which distance follows canonically.

Consequently, the primary questions are:

1. **Which points exist at time $t$?**
2. **Once they exist, how do we measure length among them?**

RC adopts the minimal construction compatible with these requirements:

- existence is defined by **support** of the coherence field, and
- length is defined by a metric that is **constructed from the coherence field**.

We treat the coordinate chart as a reference frame for description; no ontological status is assigned to its background point set. The organism's *actual* spatial substrate is wherever coherence is nonzero.

# 2. Foundations: coherence, support, and identity basins

## 2.1 The primitive scalar: coherence density

**Assumption A1 (primitive).**
RC starts with a smooth scalar coherence density
$$
C: \mathbb{R}^d \times [0,T] \to \mathbb{R}_{\ge 0},\qquad C(x,t)\ge 0.
$$

**Motivation.**
A scalar is the minimal object that can be:

- present/absent ($C>0$ vs $C=0$),
- shaped (gradients),
- transported (flux),
- and used to derive geometry without choosing preferred directions a priori.

RC will *derive* preferred directions from coherent activity (flux), not postulate them.

## 2.2 Emergent spatial support

**Definition D1 (emergent space).**
The spatial domain at time $t$ is the support
$$
\Omega_t := \mathrm{supp}\,C(\cdot,t)
= \overline{\{x\in\mathbb{R}^d\mid C(x,t)>0\}}.
\tag{Eq. S}
$$

**Why support instead of $\{C>0\}$ directly?**
Support is the closed set that "contains" the region of nonzero coherence. This matters because:

- it is stable under small perturbations (a physically desirable property),
- and it avoids pathological boundary issues when we build geometric operators.

We interpret $\Omega_t$ as the realized spatial domain at time $t$.

## 2.3 Identity basins: the topology RC cares about

**Definition D2 (identity basins).**
Let $\{B_i(t)\}_{i=1}^{N(t)}$ be the connected components of $\Omega_t$. Then
$$
\Omega_t = \bigcup_{i=1}^{N(t)} B_i(t).
\tag{Eq. B}
$$

**Interpretation.**

- Each basin is a coherent "island" of existence.
- A split of a basin corresponds to *refinement*: one identity becomes two differentiated identities.
- A merge corresponds to integration or collapse of separation.

This is already the first place where RC differs from "space as container": topology is now an evolving property of $\Omega_t$, not a fixed stage.

# 3. From coherence to geometry: why we build a tensor and then a metric

To measure distance, we need a metric. But why should a metric come from a scalar field? Because a metric is a rule that assigns a squared length to an infinitesimal displacement:
$$
ds^2 = g_{\mu\nu}(x,t)\,dx^\mu dx^\nu.
$$

So we need a positive-definite symmetric tensor $g_{\mu\nu}$. The only raw materials available are:

- $C$,
- its gradient $\nabla C$,
- and its flux/current.

This motivates building a **coherence tensor** $K_{\mu\nu}[C]$ first.

## 3.1 Coherence flux and current

We assume coherence has a transport description:

$$
\partial_t C + \nabla_\mu J_C^\mu = 0,
\tag{Eq. F1}
$$
with
$$
J_C^\mu = C\,v_C^\mu,\qquad j_\mu := C\,v_{C,\mu}.
\tag{Eq. F2}
$$

Here $v_C$ is the coherence velocity and $j_\mu$ is the "stress-bearing" current that will enter geometry.

**Remark.** The moment we allow $g$ to depend on $j$, we are saying: *repeated coherent activity can reshape geometry.* This is the mathematical version of "paths get carved into highways."

## 3.2 Definition and motivation of the coherence tensor

**Definition D3 (coherence tensor).**
We define a symmetric tensor
$$
K_{\mu\nu}[C]
:= \lambda_C\,C\,g^{(\mathrm{aux})}_{\mu\nu}

+ \xi_C\,\nabla_\mu C\,\nabla_\nu C
+ \zeta_C\,j_\mu j_\nu.
\tag{Eq. K}
$$

### Motivation for the tensor form.

- **Density term:** $\lambda_C C g^{(\mathrm{aux})}$.
  This provides a baseline geometry proportional to "how much coherence exists."
  Without it, regions of uniform coherence (zero gradient, zero flux) would have no defined geometry.

- **Gradient term:** $\xi_C\,\nabla C\otimes \nabla C$.
  Gradients encode "tension" or "stiffness." Intuitively, sharp spatial transitions create barriers and boundaries.

- **Flux term:** $\zeta_C\,j\otimes j$.
  Flux is directional and should therefore induce anisotropy. The outer product $j_\mu j_\nu$ is the simplest directional symmetric contribution.

### Why is $g^{(\mathrm{aux})}$ allowed?

Because we still need a way to contract indices on the chart; but we treat that as bookkeeping. The emergent geometry is the $g$ we define next, not the auxiliary metric.

## 3.3 The induced metric (and why we normalize)

**Definition D4 (induced metric).**
Wherever $C(x,t)>0$, define
$$
g_{\mu\nu}(x,t) := \frac{1}{\lambda_C\,C(x,t)}\,K_{\mu\nu}[C](x,t).
\tag{Eq. g}
$$

### Motivation for density normalization.

Two reasons:

1. **Dimensional / scaling control.**
   If coherence doubles everywhere, distances should not necessarily double. Normalization makes geometry sensitive to *relative structure* (gradients and flux per unit coherence).

2. **Interpretation as "shape over amount."**
   Geometry should reflect organization, not only magnitude. The ratios $\nabla C / C$ and $j / C$ are exactly the natural "organization per unit coherence" objects.

## 3.4 Proof: the induced metric is Riemannian on $\{C>0\}$

**Proposition P1 (positive-definiteness).**
Assume $\lambda_C>0$ and the auxiliary chart metric $g^{(\mathrm{aux})}$ is positive-definite. Then, for any nonzero tangent vector $u$ at a point with $C>0$,
$$
g_{\mu\nu}u^\mu u^\nu > 0.
$$

**Proof.**
Insert (Eq. K) into (Eq. g) and contract with $u$:
$$
g_{\mu\nu}u^\mu u^\nu
=
u^\mu u^{(\mathrm{aux})}_\mu

+ \frac{\xi_C}{\lambda_C C}\,(\nabla_\mu C\,u^\mu)^2
+ \frac{\zeta_C}{\lambda_C C}\,(j_\mu u^\mu)^2.
$$

- The first term is strictly positive for $u\neq 0$ because $g^{(\mathrm{aux})}$ is positive-definite.
- The remaining terms are nonnegative because they are squares multiplied by real coefficients divided by $C>0$.

Therefore the sum is strictly positive. $\square$

## 3.5. Boundary regularization and the working domain $\Omega_t^\varepsilon$

Because the induced metric is normalized by $C$ (Eq. g), it can become ill-conditioned as $C\to 0^+$ near the support boundary. Rather than treating this as a pathology, we adopt an explicit and standard regularization protocol that also matches numerical practice.

For $\varepsilon>0$, define the regularized domain
$$
\Omega_t^\varepsilon := \{x\in\mathbb R^d \mid C(x,t)\ge \varepsilon\},
$$
and the $\varepsilon$-regularized metric
$$
g^{(\varepsilon)}_{\mu\nu}(x,t)
:= \frac{1}{\lambda_C\,(C(x,t)+\varepsilon)}\,K_{\mu\nu}[C](x,t).
$$

We then define regularized distances $d_t^\varepsilon$ and $\tau_t^\varepsilon$ exactly as in Chapters 4-5, but with $g^{(\varepsilon)}$ and admissible paths constrained to $\Omega_t^\varepsilon$. The physical (unregularized) distances are interpreted as the controlled limit
$$
d_t(x_1,x_2) := \lim_{\varepsilon\downarrow 0} d_t^\varepsilon(x_1,x_2),
\qquad
\tau_t(x_1,x_2) := \lim_{\varepsilon\downarrow 0} \tau_t^\varepsilon(x_1,x_2),
$$
whenever these limits exist (and in computations, $\varepsilon$ is retained as a coherence floor set by resolution or by a minimal meaningful coherence scale).

This protocol makes boundary behavior explicit:

- it avoids relying on uncontrolled cancellations at $C\approx 0$,
- it keeps the geometry well-conditioned on the working domain,
- and it cleanly separates interior geometry from boundary formation dynamics.

## 3.6. Coefficient semantics and pointers to the core theory

The metric construction depends on three coefficient families $\lambda_C,\xi_C,\zeta_C$, which weight baseline density geometry, gradient stiffness, and flux-induced anisotropy, respectively. In this paper we use only their qualitative roles and the sign constraints needed for the Riemannian core.

A full treatment-dimensional analysis, invariances under rescalings of $C$, calibration principles, and how these coefficients emerge from the RC coherence functional-belongs to the core theory documents (Reflexive Coherence; Identity/Choice/Abundance; Fractal Reflexive Coherence). Here we require only:

- $\lambda_C>0$ to set the baseline metric scale,
- $\xi_C\ge 0$ so gradients contribute nonnegatively to stiffness,
- $\zeta_C\ge 0$ so flux contributes nonnegatively and directionally.

When applying the distance construction to a specific RC model, one should import the coefficient definitions and scaling conventions from the core theory unchanged; the distance theory in this paper is designed to be compatible with that upstream structure.


**Consequence.**
Each snapshot $M_t := (\Omega_t, g(t))$ is a (possibly time-varying) **Riemannian manifold** wherever $C>0$. This is the structural foundation needed for geodesic distance, Laplace-Beltrami operators, and spectral coarse-graining.

# 4. Distance as geodesic length (and what becomes RC-specific)

Once a Riemannian metric exists, distance is not an additional hypothesis: it is the canonical object associated with the metric. What is *specific to RC* is that the metric is **induced from the coherence state** via (Eq. K)-(Eq. g), and the underlying domain of existence is **support-derived** via (Eq. S). Consequently, distance is state-dependent for two distinct reasons:

1. **Metric dependence:** even on a fixed set, changing $C$ changes $g$, hence changes lengths and geodesics.
2. **Domain dependence:** the set of admissible paths changes when $\Omega_t$ splits/merges, even if the local metric were unchanged.

We make these statements precise below, and we keep the discussion constructive: given a snapshot $C(\cdot,t)$, one can compute $g(t)$ and then distances.

## 4.1. From the induced metric to the line element

Given $g_{\mu\nu}(x,t)$ on $\Omega_t$, we define the infinitesimal length of a displacement $dx$ by the usual line element
$$
ds^2 = g_{\mu\nu}(x,t)\,dx^\mu dx^\nu.
$$
This is where the positivity proof matters: because $g$ is positive-definite wherever $C>0$, the expression above defines a genuine norm on tangent vectors, and $ds$ is real and nonzero for nonzero displacements.

Two immediate consequences follow:

- **Local comparison is intrinsic.** In any coordinate chart, the numerical components of $dx$ are chart-dependent, but the scalar $ds$ is invariant.
- **Lengths encode coherence structure.** Since $g$ depends on $C$, gradients, and flux, the local "cost" of moving through a region depends on the coherence organization at that point.

## 4.2. Length of curves and why we use the standard functional

Let $\gamma:[0,1]\to\Omega_t$ be a piecewise-smooth curve. We define its length at fixed time $t$ by
$$
L_t[\gamma] := \int_0^1 \sqrt{g_{\mu\nu}(\gamma(s),t)\,\dot\gamma^\mu(s)\dot\gamma^\nu(s)}\,ds.
\tag{Eq. L}
$$

This functional is not chosen for convenience; it is the unique natural length functional induced by the metric tensor. In particular, it satisfies:

- **Reparameterization invariance:** the geometric length does not depend on how the curve is parameterized.
- **Additivity:** if a curve is concatenated from segments, the length is the sum of segment lengths.

These properties are important in RC because admissible paths may be piecewise (e.g., when crossing basin boundaries), and we require a distance notion that composes consistently.

## 4.3. Geodesic distance and what it measures in RC

**Definition (Geodesic distance).** For $x_1,x_2\in\Omega_t$,
$$
d_t(x_1,x_2) := \inf_{\gamma:x_1\to x_2} L_t[\gamma].
\tag{Eq. d}
$$

We emphasize two RC-relevant interpretations:

1. **Intrinsic proximity:** $d_t$ measures proximity in the geometry induced by the coherence state at time $t$. Two points may be close in chart coordinates and far in $d_t$, or vice versa, depending on coherence gradients and flux.
2. **Path admissibility depends on support:** If $x_1$ and $x_2$ lie in different connected components of $\Omega_t$, then no curve exists and $d_t$ is effectively infinite (or undefined). Thus basin connectivity is not an ornament; it determines whether distance is defined at all.

## 4.4. From variational principle to geodesic equation (brief derivation)

To avoid treating the geodesic equation as a black box, we recall the standard variational route. Instead of minimizing $L_t$ directly, it is often convenient to minimize the energy functional
$$
E_t[\gamma] := \frac12\int_0^1 g_{\mu\nu}(\gamma(s),t)\,\dot\gamma^\mu(s)\dot\gamma^\nu(s)\,ds.
\tag{Eq. E}
$$
On sufficiently regular paths, minimizers of $L_t$ are reparameterizations of minimizers of $E_t$. Applying the Euler-Lagrange equations to (Eq. E) yields
$$
\ddot x^\mu + \Gamma^\mu_{\alpha\beta}(g)\,\dot x^\alpha\dot x^\beta = 0,
\tag{Eq. geo}
$$
where $\Gamma(g)$ is constructed from the induced metric.

In RC, the content of this equation is that "shortest paths" are shaped by coherence-induced geometry: the Christoffel symbols inherit the spatial structure of $C$ and the directionality of $j=Cv_C$ through (Eq. K)-(Eq. g). This is the precise sense in which coherent organization bends geodesics.

## 4.5. Existence and well-posedness (what assumptions we need)

A minimal practical statement is:

- On compact regions where $g$ is smooth, minimizing geodesics exist between any two points in the same connected component.

This is standard Riemannian theory. For RC, it matters because computations are typically performed on finite-resolution domains (effectively compact) and within basins. Where completeness fails globally (e.g., near moving boundaries of $\Omega_t$), one still has well-posed distances on compact subsets away from degeneracies.

## 4.6. Computational recipe (snapshot distance)

Given $C(\cdot,t)$:

1. Determine $\Omega_t=\mathrm{supp}\,C(\cdot,t)$ and its basins $B_i(t)$.
2. Construct $j_\mu=C v_{C,\mu}$ from the chosen transport law.
3. Assemble $K[C]$ and $g[C]$ via (Eq. K) and (Eq. g).
4. Solve the boundary-value problem (Eq. geo) (or compute shortest paths numerically) to obtain $d_t(x_1,x_2)$.

This recipe is essential for the interpretation of "distance is state-relative": it is not an analogy but a computable functional of $C$.

# 5. Operational distance: propagation time of coherence perturbations

Geodesic distance is the canonical intrinsic notion of length once a metric is defined.
However, in a reflexive system the physically relevant notion of separation is often *causal/operational*: how long it takes for a perturbation, signal, or boundary change to propagate from one region to another. RC provides a natural operational distance because transport of coherence is part of the same closed description that induces the geometry.

The key point is not merely that we can define a time functional, but that the time functional is **intrinsic**: it uses the same induced line element $ds$ and a velocity field $v_C$ that is itself a functional of $C$.

## 5.1. Transport structure and why a closure matters

We assume coherence obeys a continuity equation
$$
\partial_t C + \nabla_\mu J_C^\mu = 0,
\tag{Eq. F1}
$$
and we write the flux as
$$
J_C^\mu = C\,v_C^\mu,\qquad j_\mu := C\,v_{C,\mu}.
\tag{Eq. F2}
$$

At this point, the theory is kinematic: $v_C$ is unspecified. A purely "fixed-operator" choice-e.g., constant diffusion in a fixed background-would undermine the central RC claim that geometry and dynamics are mutually determining. Therefore, we use a reflexive closure in which transport depends on the coherence state.

## 5.2. State-dependent closure (gradient-flow form)

A structurally minimal and widely interpretable closure is a generalized gradient flow:
$$
v_C^\mu = -D^{\mu\nu}[C]\;\nabla_\nu \Phi_C,
\qquad
\Phi_C := \frac{\delta \mathcal P}{\delta C}.
\tag{Eq. v}
$$

Here:

- $\mathcal P[C]$ is an RC potential/functional; its variational derivative $\Phi_C$ plays the role of a generalized "coherence pressure."
- $D^{\mu\nu}[C]$ is a mobility tensor, allowed to be anisotropic and state-dependent.

We emphasize the structural reason for this form: it guarantees that coherence flow is driven by a functional of the state and can thus support self-stabilizing or self-refining dynamics depending on $\mathcal P$ and $D$. The particular $\mathcal P$ is not needed for defining distance; what matters is that $v_C$ is intrinsic and coherence-dependent.

## 5.3. Travel-time functional and operational distance

Given a path $\gamma$ in $\Omega_t$, we define the travel time along $\gamma$ as
$$
\tau_t[\gamma] := \int_{\gamma}\frac{ds}{|v_C|},
\tag{Eq. tau}
$$
where $ds$ is the induced line element from Chapter 4 and $|v_C|$ is the speed in the induced geometry.

We then define operational distance between points as the minimal travel time:
$$
\tau_t(x_1,x_2) := \inf_{\gamma:x_1\to x_2}\tau_t[\gamma].
\tag{Eq. Tau}
$$

This definition parallels geodesic distance (Eq. d), but the object being minimized is time rather than length. It is therefore sensitive not only to geometry but also to how the system can move coherence through that geometry.

## 5.4. When $\tau_t$ differs from $d_t$ (and why this is expected)

Even in classical settings, "shortest path" and "fastest path" differ if speed depends on location or direction. RC has both effects:

- **Location dependence:** because $v_C$ depends on $C$, regions of high coherence may support faster or slower propagation depending on the mobility.
- **Directional dependence:** if $D[C]$ is anisotropic (or if flux channels exist), then propagation is faster along preferred directions.

Thus $\tau_t$ captures *effective causal adjacency* as perceived by the coherence dynamics, whereas $d_t$ captures intrinsic geometric adjacency.

A useful way to summarize:

- $d_t$ is "spatial proximity" in the induced geometry.
- $\tau_t$ is "response proximity" in the induced dynamics.

In systems where coordination and adaptation matter, $\tau_t$ is often the operationally relevant notion.

## 5.5. Domain effects: operational distance inherits basin topology

Because both $ds$ and $v_C$ are defined only on $\Omega_t$, operational distance inherits the same domain restriction as geodesic distance:

- If $x_1$ and $x_2$ lie in different connected components of $\Omega_t$, there is no admissible path, and $\tau_t$ is undefined/infinite.

This observation is one reason topology refinement is not a side story: it changes *which operational interactions are possible at all*.

## 5.6. Practical use: an operational notion of "shortcut"

When we say a flux channel creates a shortcut, we mean precisely that it can decrease $\tau_t$ substantially even if $d_t$ changes only modestly. Conversely, a geometric contraction can decrease $d_t$ while leaving $\tau_t$ large if the mobility is low. Distinguishing these effects is often essential when interpreting "distance" in a reflexive system.

# 6. Growth as refinement, not coordinate extension (the central conceptual result)

This section is the "relativity of space" core: **space itself** is a derived object and can change.

## 6.1 Coordinate extension is the wrong mental model

Coordinate extension means enlarging the underlying point set. That presumes the point set is primary.

RC says: the point set that exists is $\Omega_t$ derived from $C$. Therefore:

- the chart can stay fixed,
- and "more space" can appear as new connected regions of $\{C>0\}$.

## 6.2 Topology change without surgery: level-set bifurcations

Because $\Omega_t$ is determined by $\{C>0\}$, changes in the number of basins are changes in connectivity of a superlevel set of a smooth function.

A standard result in differential topology (Morse/regular value intuition) is:

- Away from critical degeneracies, level-set topology is stable.
- Topology can change only when the level hits a degenerate critical point.

RC packages that as a "spark."

## 6.3 Spark condition (and why it is necessary)

**Definition D6 (spark).**
A point $(x_s,t_s)$ is a spark if
$$
\nabla_x C(x_s,t_s)=0
\quad\text{and}\quad
\det(\mathrm{Hess}_x\,C)(x_s,t_s)=0.
\tag{Eq. spark}
$$

### Why these conditions?

- $\nabla C=0$ means we are at a critical point; only critical points can create or annihilate components.
- Hessian degeneracy is the "non-Morse" condition that allows the local structure of $\{C=0\}$ to change. Without degeneracy, the boundary moves smoothly and connectivity does not jump.

**Proposition P3 (refinement events require sparks).**

**Scope note.** The spark criterion is used here as a necessary degeneracy condition for topology change of the positive-coherence region. A full classification of refinement transitions (genericity conditions, local normal forms, and stability under dynamics) is substantial and is deferred to a dedicated treatment.

If the number of connected components $N(t)$ of $\Omega_t$ changes at time $t_s$, then there exists a spark $(x_s,t_s)$ satisfying (Eq. spark).

**Explanation.**
This is the precise mathematical version of "a smooth field can induce discrete basin splits."
The field evolves smoothly, but the topology of its positive region can change at a bifurcation.

## 6.4 What changes at a refinement event?

Two things change-neither requires coordinate extension:

1. The set $\Omega_t$ changes connectivity: basins split/merge.
2. The induced geometry $g(t)$ changes continuously with $C$, reshaping distances inside and between basins.

This is why RC calls it "spacetime growth": the **space of existence** and its **metric** evolve.

# 7. Anisotropic distance from flux: why activity creates "highways"

Now we connect the flux term in (Eq. K) to the intuitive claim that coherent activity creates shortcuts.

## 7.1 Flux term as a rank-1 deformation

Combine (Eq. K) and (Eq. g) to write
$$
g_{\mu\nu}
= g^{(0)}_{\mu\nu} + \frac{\zeta_C}{\lambda_C C}\,j_\mu j_\nu,
\tag{Eq. aniso}
$$
where $g^{(0)}$ collects density + gradient contributions.

This is a rank-1 update aligned with $j$. In a local basis aligned with $j$, only the "parallel" direction is modified strongly.

## 7.2 Why this produces shortcuts (not just metaphor)

A clean way to make this rigorous is through the kinetic-energy perspective.

Consider the kinetic Lagrangian
$$
\mathcal L = \tfrac12 g_{\mu\nu}\dot x^\mu\dot x^\nu.
\tag{Eq. kin}
$$

For fixed energy (or fixed action budget), the inverse metric $g^{\mu\nu}$ determines which velocity components are "cheaper."
Increasing the parallel component $g_{\parallel\parallel}$ decreases $g^{\parallel\parallel}$, making displacement along the current direction more efficient under the same budget.

**Conclusion.**
Regions of sustained coherent transport become intrinsic "highways": both geodesic minimizers and travel-time minimizers tend to align with flux channels.

# 8. Basin-local clocks and hierarchical structure

We keep the construction of basin-clock fully Riemannian while preserving (and clarifying) the intent:

- Basins can have different *intrinsic progression scales* because their induced geometries differ.
- Spectral properties of basin geometry provide a principled hierarchy (coarse to fine).
- These notions are needed if we want a distance theory that remains meaningful across refinement events, where the identity partition itself changes.

We do **not** claim that RC requires a spacetime signature at this stage. The point is subtler: even in a purely Riemannian setting, different coherent regions can have different natural internal scales.

## 8.1. Basin-wise metrics and restriction

Given $\Omega_t$ and its basin decomposition $\Omega_t=\bigcup_i B_i(t)$, we restrict the induced metric $g(t)$ to a basin:
$$
g^{(i)}_{\mu\nu}(x,t) := g_{\mu\nu}(x,t)\big|_{x\in B_i(t)}.
$$

This restriction is mathematically straightforward but conceptually important: it is the precise way to say that each basin is a coherent sub-geometry. All standard Riemannian constructions (geodesics, Laplacian, volume form) can now be applied basin-wise.

## 8.2. Basin intrinsic clock element

We define a basin-local intrinsic progression element by the basin line element
$$
d\tau_i := \sqrt{g^{(i)}_{\mu\nu}\,dx^\mu dx^\nu}.
\tag{Eq. clock}
$$

A few clarifications:

- $d\tau_i$ is **not** relativistic proper time. It is a Riemannian arc-length parameter measuring progression internal to the basin geometry.
- The meaning is operational: if dynamics within a basin relax or propagate according to the basin geometry, then $d\tau_i$ is the natural parameter in which "unit changes" are measured.

This is the minimal way to capture the idea that "time scales are basin-relative" without introducing a Lorentzian structure prematurely.

## 8.3. Spectral hierarchy: why basin scales are not arbitrary

To turn "basin time scales" into a rigorous statement, we use the Laplace-Beltrami spectrum. On $(B_i, g^{(i)})$, consider eigenmodes
$$
-\Delta_{g^{(i)}}\phi_{i,k} = \lambda_{i,k}\phi_{i,k},
\qquad
C|_{B_i}(x,t) = \sum_k c_{i,k}(t)\phi_{i,k}(x).
\tag{Eq. spec}
$$

Interpretation:

- Small $\lambda_{i,k}$ correspond to smooth, long-wavelength modes that encode basin-scale structure.
- Large $\lambda_{i,k}$ correspond to fine, rapidly varying modes that encode microstructure.

In many diffusive or gradient-flow dynamics, eigenvalues relate directly to relaxation rates. Thus the spectrum provides a principled hierarchy of intrinsic basin scales, which is essential if refinement is to be treated as more than a purely topological event.

## 8.4. Boundary effects and refinement: why clocks matter at basin splits/merges

When a basin splits, two new basins inherit geometry from the parent but can rapidly diverge in spectral structure. In practice this means:

- a single "parent" internal scale can bifurcate into two distinct scales,
- and distances measured within each child basin should be interpreted in each basin's own intrinsic parameterization.

This perspective helps separate two mechanisms that can both look like "growth" in coordinates:

1. **Geometry deformation:** $g(t)$ changes continuously with $C$.
2. **Topology refinement:** $\Omega_t$ changes connectivity (basin split/merge).

Basin-local clocks and spectral hierarchies provide the language needed to describe these mechanisms coherently across refinement events.

## 8.5. Relation to operational distance

Operational distance $\tau_t$ (Chapter 5) uses $|v_C|$ and $ds$. If $v_C$ is strongly basin-dependent (through $C$ and $D[C]$), then $\tau_t$ naturally decomposes into basin-wise contributions. This is one reason we emphasize basin-local structures: they supply the correct "units" in which operational propagation should be interpreted.

# 9. Hierarchical distances (micro / meso / macro)

The basin decomposition is not merely a topological ornament: it supplies a natural hierarchy of distance notions corresponding to the scale at which we coarse-grain the coherence field. If we do not distinguish these scales, we risk conflating two different phenomena:

- **Metric deformation** (continuous changes in $g$ for fixed connectivity), and
- **Refinement events** (discrete changes in connectivity and basin partition).

We therefore describe distance at three nested levels. The key point is not to invent three unrelated distances, but to understand how the canonical metric distance behaves under restrictions and coarse-graining.

## 9.1. Microscopic distance: within a single basin

Fix a basin $B_i(t)$. The most fine-grained notion of distance is simply the geodesic distance induced by $g^{(i)}$ on $B_i$, i.e., (Eq. d) with admissible curves constrained to lie in $B_i.$

Conceptually, this is the distance relevant for internal differentiation within an identity basin. It is the correct distance notion to use when we discuss the basin's internal structure, internal communication (short paths), and internal spectral hierarchy.

Operationally, if one computes distances via numerical geodesics, constraining to a basin typically improves well-posedness because boundaries are fixed within a snapshot and the region is effectively compact.

## 9.2. Mesoscopic distance: between adjacent basins

Between basins, two issues arise:

1. Curves must pass through boundary regions, which may be thin (low coherence) or dynamically active (high flux).
2. Distances may be better understood as **compositions** of within-basin segments plus a boundary-crossing segment.

A useful representation is therefore *piecewise-geodesic*:

- within each basin, segments are geodesics for $g^{(i)}$,
- at transitions, segments are stitched across boundary neighborhoods where the metric and flux may change rapidly.

At this level, reporting only a single scalar $d_t(x_1,x_2)$ may discard structure. It is often informative to report:

- the sequence of basins visited, and
- the basin-wise length/time contributions (using basin line elements $d\tau_i$ and operational travel-time contributions).

This is the level at which "refinement as growth" becomes geometrically salient: the boundary structure and inter-basin couplings determine how macro distances reorganize when basins split/merge.

## 9.3. Macroscopic distance: across the full support $\Omega_t$

At the coarsest level, we treat $(\Omega_t,g(t))$ as the manifold and compute geodesic distances globally (Eq. d). This captures the organism's overall geometry at time $t$ and is the correct notion for "global proximity" questions.

However, we emphasize two caveats:

- Macroscopic distance is undefined across disconnected components; thus refinement events that create or remove components can abruptly change which global distances exist at all.
- Macroscopic distances can change substantially even without topology change, simply because $g(t)$ changes with $C$.

## 9.4. Coarse-graining as a map between distance notions

One can view the micro/meso/macro hierarchy as a sequence of coarse-graining operations:

- micro: points within a basin,
- meso: boundary-mediated coupling between basins,
- macro: global geometry of the full support.

On the discrete side (Chapter 10), this hierarchy corresponds naturally to:

- landmark graphs within basins (micro),
- adjacency/flux graphs between basins (meso),
- shortest paths on the basin graph (macro).

This alignment is not accidental: it is an expression of the same refinement principle in two representations (continuum and combinatorial).

## 9.5. Why we insist on hierarchy (interpretive necessity)

Without an explicit hierarchy, one can mistakenly interpret a refinement event as "space expansion" in coordinates. The hierarchy clarifies that what changes is:

- the admissible path set (via topology), and
- the intrinsic cost of motion (via the induced metric and flux).

In other words: refinement is not a coordinate story; it is a *geometric and topological* story, and the hierarchy provides the correct descriptive resolution.

# 10. Discrete induced distance: continuum $\rightarrow$ graph (RC/GRC bridge)

Refinement events are combinatorial (splits/merges), while the induced metric is differential.
To analyze *both* in one framework-especially across spark-driven topology changes-it is useful to extract a **topological skeleton**: a time-dependent weighted graph derived from $C(\cdot,t)$. This is not merely a numerical discretization; it is the natural compression of the continuum geometry to the level where refinement is explicit.

We proceed in three steps:

1. Define the node set as identity basins $B_i(t)$ (or, at higher resolution, sub-basin landmarks).
2. Define edge existence as adjacency and/or coherent coupling (via flux).
3. Define edge weights in a way that preserves either intrinsic geometry ($d_t$) or operational causality ($\tau_t$), depending on the question.

The result is a discrete distance that can be compared across time even when $\Omega_t$ changes topology.

## 10.1. Induced basin graph: objects and intent

Let $V(t)=\{B_i(t)\}$ be the set of basins at time $t$. We define a graph
$$
\mathcal G(t) = (V(t),E(t),w(t)).
$$

### Node semantics

A node is not "a point in space"; it is an *identity basin*, i.e., a connected component of $\Omega_t$. This choice has two advantages:

- **Topological events are explicit:** a refinement event is literally a node split/merge.
- **Coarse-graining is built-in:** basins are already a natural partition induced by $C$.

In applications that require more resolution, one can refine each basin into landmarks (e.g., local maxima of $C$, spectral centroids, or a covering by patches). The basin graph is then the coarse layer of a multilevel graph.

## 10.2. Edge existence: adjacency vs coherent coupling

There are two conceptually distinct notions of "connection" between basins.

### (a) Geometric adjacency

Declare an undirected edge $i\leftrightarrow j$ when the basin boundaries touch (in the chart topology), i.e.,
$$
\overline{B_i(t)}\cap \overline{B_j(t)} \neq \varnothing.
$$
Adjacency captures the idea that the basins are "neighbors" in the support geometry.

### (b) Coherent coupling (flux-mediated)

Declare an edge when there is sustained coherence transport between basins, e.g., when the time-integrated boundary flux exceeds a threshold. A representative functional is
$$
\mathcal F_{ij}(t;\Delta t)
:= \int_{t-\Delta t}^{t}\int_{\partial B_i \cap \partial B_j} \bigl|J_C\cdot n_{ij}\bigr|\,dS\,d\tau,
$$
where $n_{ij}$ is a choice of normal convention. One may then set
$$
(i,j)\in E(t)\quad \Longleftrightarrow \quad \mathcal F_{ij}(t;\Delta t)>\theta.
$$

Adjacency is structural; flux coupling is functional/causal. In practice, one often uses adjacency to generate candidate edges and flux to select which candidates are active.

## 10.3. Edge weights: intrinsic length vs operational time

Once edges exist, we choose weights that encode the notion of distance of interest.

### (a) Intrinsic geometric weight

Choose representatives $p_i(t)\in B_i(t)$ (e.g., the basin maximizer of $C$, a centroid, or a spectral landmark). Define
$$
w^{(d)}_{ij}(t) := d_t\bigl(p_i(t),p_j(t)\bigr),
$$
or, for adjacent basins where boundary neighborhoods dominate,
$$
w^{(d)}_{ij}(t) := \inf_{x\in B_i,\;y\in B_j} d_t(x,y).
$$
This choice makes the graph distance a coarse approximation to geodesic distance on $(\Omega_t,g(t))$.

### (b) Operational weight (travel time)

Define analogously
$$
w^{(\tau)}_{ij}(t) := \tau_t\bigl(p_i(t),p_j(t)\bigr),
$$
or boundary-based variants. This yields a discrete approximation to operational (causal) distance.

### (c) Flux-based inverse coupling (effective-resistance style)

If high flux is interpreted as strong coupling, a distance-like weight is inverse coupling:
$$
w^{(F)}_{ij}(t) := \frac{1}{\varepsilon + \mathcal F_{ij}(t;\Delta t)},
$$
with $\varepsilon>0$ for stability.

The important point is methodological: the graph is induced by the same RC primitives; the choice of weight makes explicit which notion of "distance" is being represented.

## 10.4. Graph distance

Given weights $w_{ab}(t)$, define the discrete shortest-path distance
$$
d_{\mathcal G}(i,j;t) = \min_{\text{paths }i\to j} \sum_{(a,b)\in \text{path}} w_{ab}(t).
$$

With $w^{(d)}$, $d_{\mathcal G}$ is a coarse intrinsic distance; with $w^{(\tau)}$, it is a coarse operational distance; with $w^{(F)}$, it measures effective separation in a coupling network.

## 10.5. Refinement events as graph operations

When a spark event causes a basin $B_i$ to split into $B_{i_1},B_{i_2},\dots$, the graph update is explicit:

- Replace node $i$ by nodes $i_1,i_2,\dots$.
- Recompute local adjacency/coupling edges.
- Reassign weights using the same rules.

A merge is a node contraction. This gives a discrete representation of "growth by refinement": the object that changes is the partition/graph resolution, not the coordinate chart.

## 10.6. Multi-level graphs and consistency with Chapters 4-9

The micro/meso/macro hierarchy (Chapter 9) aligns with multilevel graphs:

- **Micro:** landmark graphs within each basin (within-basin geodesics/travel times).
- **Meso:** basin adjacency/flux graph (this chapter).
- **Macro:** shortest paths across the basin graph.

This provides a practical and conceptual consistency check: distance remains interpretable across resolution changes, and refinement events have a coherent meaning in both continuum and discrete representations.

# 11. Fractal extension (FRC): scale-expanding hierarchies (optional)

The core construction in this paper is scale-agnostic: it treats $C(x,t)$ as the coherence field and derives $\Omega_t$, $g(t)$, and distances.
In many RC settings, coherence is naturally multi-scale (nested identities, coarse-graining, hierarchical structure). The Fractal Reflexive Coherence (FRC) extension makes this explicit by introducing a scale coordinate $\sigma$ and allowing coherence to appear as a family $C(x,t;\sigma)$.

The point here is a compatibility statement: the distance theory constructed above remains well-defined and structurally stable under a multi-scale lift.

## 11.1. Scale-indexed coherence and scale-dependent supports

Assume a scale-indexed coherence density
$$
C(x,t;\sigma)\ge 0,\qquad \sigma\in(0,\infty).
$$
At each $\sigma$, define the support
$$
\Omega_t(\sigma) := \mathrm{supp}\,C(\cdot,t;\sigma),
$$
and its basin decomposition into components $B_i(t;\sigma)$.

This captures a key phenomenon: connectivity can be scale-dependent. A region that is disconnected at fine scale may become connected at coarse scale, depending on how coherence distributes across $\sigma$.

## 11.2. Scale-wise coherence tensors and integrated geometry

At each $\sigma$, build a coherence tensor of the same form as (Eq. K):
$$
K_{\mu\nu}(x,t;\sigma)
:= \lambda_C\,C(x,t;\sigma)\,g^{(\mathrm{aux})}_{\mu\nu}

+ \xi_C\,\nabla_\mu C(x,t;\sigma)\,\nabla_\nu C(x,t;\sigma)
+ \zeta_C\,j_\mu(x,t;\sigma)\,j_\nu(x,t;\sigma).
$$

Define integrated coherence and integrated tensor:
$$
C^{(\mathrm{int})}(x,t) := \int_0^\infty C(x,t;\sigma)\,d\sigma,\qquad
K^{(\mathrm{int})}_{\mu\nu}(x,t) := \int_0^\infty K_{\mu\nu}(x,t;\sigma)\,d\sigma.
$$

Induce the metric by the same normalization logic:
$$
g_{\mu\nu}(x,t) := \frac{1}{\lambda_C\,C^{(\mathrm{int})}(x,t)}\,K^{(\mathrm{int})}_{\mu\nu}(x,t),
$$
where defined.

Positivity is preserved: $K^{(\mathrm{int})}$ remains a sum/integral of positive semidefinite contributions, and the same argument as Proposition P1 applies wherever $C^{(\mathrm{int})}>0$.

## 11.3. Distance and refinement in the multi-scale setting

With $g(t)$ defined as above:

- Geodesic distance $d_t$ is defined exactly as in Chapter 4.
- Operational distance $\tau_t$ is defined exactly as in Chapter 5.

What changes is interpretation and resolution:

- Geometry now reflects contributions from multiple scales.
- Refinement events can occur at specific scales, producing a hierarchy of basin graphs $\mathcal G(t;\sigma)$.
- One may also define an "integrated" basin graph $\mathcal G^{(\mathrm{int})}(t)$ from $C^{(\mathrm{int})}$.

This allows scale-sensitive questions (e.g., connectivity and causal coupling at one scale vs another) while preserving the core RC commitments.

## 11.4. Relation to the distance hierarchy (Chapter 9) and to graphs (Chapter 10)

The micro/meso/macro hierarchy can be viewed as an implicit scale hierarchy. FRC makes this explicit and provides a unified language for:

- geometric coarse-graining (via integrated metrics),
- topological coarse-graining (via scale-dependent supports/graphs),
- dynamical coarse-graining (via scale-dependent mobilities $D[C(\cdot;\sigma)]$).

In this sense, the FRC lift is not an add-on but a stability statement: the distance theory above is compatible with explicit multi-scale generalization.

# 12. Summary (what you should now be convinced of)

1. **Space is derived**: $\Omega_t = \mathrm{supp}\,C(\cdot,t)$ (Eq. S).
2. **Basins encode identity** as connected components (Eq. B).
3. **Geometry is derived** from density, gradient, and flux via $K[C]$ (Eq. K) and normalization (Eq. g).
4. The induced metric is **Riemannian** wherever $C>0$ (Proposition P1).
5. **Distance is state-dependent**: geodesic distance (Eq. d) changes because $g$ changes with $C$.
6. **Operational distance** (Eq. Tau) measures propagation time and is intrinsic to the same loop.
7. **Growth is refinement**: topology changes of $\Omega_t$ require sparks (Eq. spark) and occur without coordinate extension.
8. **Flux induces anisotropic highways** through a rank-1 metric deformation (Eq. aniso) and an energy argument (Eq. kin).
9. The continuum picture induces a **graph distance** that mirrors refinement combinatorics.

## Note on Lorentzian extension

The main text deliberately remains Riemannian: the induced spatial metric $g_{ij}(x,t)$ is positive-definite wherever $C>0$, and all distance notions (geodesic length and operational travel time) are defined on the support-derived domain $\Omega_t$. When a spacetime (Lorentzian) structure is required-e.g., to discuss causal cones, proper time, or relativistic-style invariants-we can layer a Lorentzian metric on top of the present spatial geometry **without altering any of the main-text constructions**. A detailed construction is provided in Appendix A.

---

# Appendix A. Lorentzian construction consistent with the Riemannian core


## A.0. Compatibility contract (what is fixed, what is chosen)

To keep the Lorentzian layer purely additive (and to avoid reintroducing a fixed background spacetime), we make the contract explicit.

**Fixed by the main text**

- The derived spatial supports $\Omega_t=\mathrm{supp}\,C(\cdot,t)$ and the spacetime set $\mathcal M=\{(t,x)\mid x\in\Omega_t\}$.
- The induced spatial Riemannian metric $g_{ij}(x,t)$ on each slice $\Omega_t$, constructed from coherence via (Eq. K)-(Eq. g) (or its $\varepsilon$-regularized form on $\Omega_t^\varepsilon$).

**Chosen in Appendix A**

- A lapse $N(x,t)>0$ and (optionally) a shift $\beta^i(x,t)$, specified as functionals of coherence-derived quantities (e.g., spectral scales or operational speed scales).

**Consistency condition (recommended)**

- When the Lorentzian layer is intended to bound operational propagation, we impose a cone-compatibility condition of the form
  $$
  N(x,t)\ \ge\ |v_C(x,t)|_{g}\quad\text{(in compatible units, optionally with margin)},
  $$
  so that coherence transport respects the causal cones of $G$. Alternative choices (e.g., spectral lapse emphasizing basin timescales) remain admissible but should be interpreted as defining a causal structure not necessarily saturated by operational transport.

This appendix provides a controlled extension from the induced spatial (Riemannian) metric $g_{ij}(x,t)$ to a spacetime (Lorentzian) metric $G_{ab}(t,x)$ with signature $(- + + +)$ (or $(- +\cdots +)$ in $d$ spatial dimensions). The intent is modular:

1. Preserve the RC commitments: **support-derived space** and **state-induced geometry**.
2. Introduce a causality structure (null cones), a notion of proper time, and a clean interface with operational propagation and basin scales.

We do not require the resulting spacetime to be a globally smooth manifold across refinement events. Instead, we define the Lorentzian layer on the derived spacetime set and restrict differential-geometric statements to regions away from sparks where smoothness holds.

## A.1. The derived spacetime set ("world-tube")

Given the time-indexed supports $\Omega_t=\mathrm{supp}\,C(\cdot,t)$, define
$$
\mathcal M := \{(t,x)\in[0,T]\times\mathbb R^d \mid x\in\Omega_t\}.
$$
A spacetime point exists exactly when its spatial point exists at that time. This is the minimal spacetime substrate consistent with RC.

- If $\Omega_t$ changes topology (spark events), $\mathcal M$ remains a well-defined subset of $[0,T]\times\mathbb R^d$.
- Global smooth-manifold structure can fail at sparks; this is an expected feature of refinement-as-growth, not a pathology.

For local constructions (connections, curvature), we restrict to open regions $U\subset\mathcal M$ away from sparks and away from moving boundaries where $C$, the induced $g$, and auxiliary choices are smooth.

## A.2. Lorentzian metric via 3+1 decomposition

Let $g_{ij}(x,t)$ be the induced spatial metric from the main text. We define a Lorentzian spacetime metric $G_{ab}$ on $\mathcal M$ using a standard 3+1 (ADM-style) form:
$$
dS^2 = G_{ab}\,dX^a dX^b
= -N(x,t)^2\,dt^2 + g_{ij}(x,t)\,(dx^i+\beta^i(x,t)\,dt)(dx^j+\beta^j(x,t)\,dt).
$$
Here:

- $N(x,t)>0$ is the **lapse**: it converts coordinate time $t$ into proper time along observers orthogonal to the spatial slices.
- $\beta^i(x,t)$ is the **shift**: it describes how spatial coordinates move relative to the foliation.
- The spatial slices carry exactly the induced $g_{ij}(x,t)$ already constructed from coherence.

**Signature condition.** If $N>0$ and $g_{ij}$ is positive-definite, then $G_{ab}$ is Lorentzian with signature $(- +\cdots +)$.

### A.2.1. Minimal choice: zero shift

The simplest choice is $\beta^i\equiv 0$, giving
$$
dS^2 = -N(x,t)^2\,dt^2 + g_{ij}(x,t)\,dx^i dx^j.
$$
This already provides causal cones and proper time while leaving the spatial metric unchanged.

### A.2.2. Coherence-adapted shift (optional)

If one wishes the foliation to be adapted to coherence transport, a natural shift is to align with the coherence velocity:
$$
\beta^i(x,t) := \alpha\,v_C^i(x,t),
$$
with $\alpha$ a scaling/conversion factor. This makes the coordinates partially comoving with coherence flow (useful when one wants to compare with transport-based notions like $\tau_t$).

## A.3. Proper time and its relation to spatial arc-length

Consider a timelike worldline $\Gamma:t\mapsto (t,x(t))$. The proper time increment satisfies
$$
d\tau^2 = N^2\,dt^2 - g_{ij}(x,t)\,(\dot x^i+\beta^i)(\dot x^j+\beta^j)\,dt^2.
$$
In the zero-shift case, this becomes
$$
d\tau = N\,\sqrt{1 - \frac{g_{ij}\dot x^i\dot x^j}{N^2}}\;dt.
$$

The spatial arc-length element on a slice is still
$$
ds^2 = g_{ij}\,dx^i dx^j,
$$
so the Lorentzian layer introduces temporal structure through $N$ (and $\beta$) while preserving the spatial geometry exactly.

## A.4. Choosing the lapse $N$ from RC data

The lapse is the natural place to encode an intrinsic temporal scale without modifying the spatial metric. Two coherence-consistent choices are particularly useful.

### A.4.1. Spectral lapse (basin timescale)

On each basin $(B_i,g^{(i)})$, the Laplace-Beltrami spectrum provides characteristic scales. For example, one may define a basin timescale from the first nonzero eigenvalue $\lambda_{i,1}$ as
$$
T_i \propto \frac{1}{\sqrt{\lambda_{i,1}}}\quad\text{or}\quad T_i\propto \frac{1}{\lambda_{i,1}},
$$
depending on the underlying dynamics. One can then choose $N(x,t)$ to be piecewise-smooth with $N\approx N_i$ on basin interiors, where $N_i$ encodes the basin scale $T_i$. Smoothing near boundaries avoids discontinuities.

This choice ties proper time to basin-intrinsic geometry while keeping the core construction unchanged.

### A.4.2. Operational lapse (propagation-limited cones)

Operational distance $\tau_t$ depends on $|v_C|$. If one wishes the causal cones of the Lorentzian layer to reflect operational propagation constraints, a natural requirement is that the null speed bound dominates the actual transport speed. In the zero-shift case, the null condition gives
$$
0=-N^2 dt^2 + ds^2 \quad\Rightarrow\quad \frac{ds}{dt} = N.
$$
Thus choosing $N(x,t)$ to satisfy $N(x,t)\ge |v_C(x,t)|$ (in compatible units) ensures that coherence transport is causal with respect to the Lorentzian cones. One may interpret $N$ as a local "maximum propagation speed" induced by coherence organization.

## A.5. Causal cones and relation to $d_t$ and $\tau_t$

The Lorentzian layer separates three notions:

- **Geometric distance $d_t$:** determined by the slice metric $g(t)$.
- **Operational travel time $\tau_t$:** determined by $ds$ and the transport speed $|v_C|$.
- **Causal structure:** determined by the null cones of $G$, governed (in the simplest case) by the lapse $N$.

In the zero-shift case, null curves satisfy $ds/dt=N$. If $N$ is chosen to bound $|v_C|$, then operational propagation respects the causal cones. Conversely, one can set $N$ to encode basin scales (spectral lapse) even when $|v_C|$ varies; then $\tau_t$ and causal reachability differ in interpretable ways.

## A.6. Compatibility with refinement (spark) events

At a spark, $\Omega_t$ changes topology. The Lorentzian construction remains consistent because it is defined on the derived spacetime set $\mathcal M$. What fails at a spark is global smoothness; one therefore treats refinement as a controlled transition:

- Analyze on $(t_s-\epsilon,t_s)$ and $(t_s,t_s+\epsilon)$ where geometry is smooth.
- Track conserved/integrated quantities (e.g., total coherence, flux balance) across the transition via the governing dynamics.
- Update basin decomposition and any basin-local lapse assignments accordingly.

This viewpoint is consistent with the main thesis: refinement is not coordinate extension, and the Lorentzian layer must not reintroduce a fixed global manifold assumption.

## A.7. Summary of the Lorentzian layer

By specifying $N(x,t)$ (and optionally $\beta^i(x,t)$) as functionals of coherence-derived quantities, we obtain:

- a spacetime set $\mathcal M$ consistent with $\Omega_t$,
- a Lorentzian metric whose spatial slices are exactly the induced $g(t)$,
- proper time and causal cones that can be tied either to basin spectral scales or operational propagation bounds,
- and a construction that remains compatible with topology refinement events by treating sparks as transitions in the derived spacetime set.


# Appendix B. Worked example (analytic 1D + illustrative 2D)

This appendix gives a minimal worked example that exercises the main pipeline:

- a coherence field with a tunable *neck* parameter that produces a basin split/merge (refinement transition),
- explicit induced (regularized) metric in 1D and the associated geodesic distance,
- a simple operational travel-time model (to distinguish shortest vs fastest propagation),
- and the induced basin graph construction.

The intent is not to propose a canonical "RC toy model," but to provide a reproducible demonstration of the definitions and how the objects behave near boundaries and refinement transitions.

## B.1. A smooth compactly supported "bump" function

Let $b_r:\mathbb R\to\mathbb R_{\ge 0}$ be the standard $C^\infty$ bump of radius $r>0$,
$$
b_r(x) :=
\begin{cases}
\exp\!\left(-\dfrac{1}{1-(x/r)^2}\right), & |x|<r,\\
0, & |x|\ge r.
\end{cases}
$$
This function is smooth everywhere and vanishes identically outside $(-r,r)$. It is therefore well suited for support-based constructions.

We will use three bumps:

- a left bump centered at $-1$,
- a right bump centered at $+1$,
- a bridge bump centered at $0$ whose amplitude controls connectivity.

## B.2. Coherence field with a controllable neck (refinement parameter)

Fix radii $r_{\text{main}}=0.7$ and $r_{\text{bridge}}=0.35$. Define a one-parameter family
$$
C_a(x) := b_{r_{\text{main}}}(x+1) \;+\; b_{r_{\text{main}}}(x-1) \;+\; a\,b_{r_{\text{bridge}}}(x),
\qquad a\ge 0.
$$

### Basin structure

- If $a=0$, the support $\Omega(a)=\mathrm{supp}\,C_a$ is the disjoint union of two intervals:
  $$
  \Omega(0)=(-1-r_{\text{main}},-1+r_{\text{main}})\;\sqcup\;(1-r_{\text{main}},1+r_{\text{main}}),
  $$
  so there are two basins.

- If $a>0$, the bridge bump contributes support on $(-r_{\text{bridge}},r_{\text{bridge}})$, which connects the left and right regions through a nonzero-coherence corridor; $\Omega(a)$ becomes connected for sufficiently large overlap. With the radii chosen above, the bridge closes the gap already for any $a>0$, hence there is one basin.

This provides a concrete refinement transition as $a\downarrow 0$: connectivity changes (two basins $\to$ one basin) without any coordinate extension.

> **Remark (spark idealization).**
> In this toy family, the transition at $a=0$ is "non-generic" in the sense that a whole interval of points has $C=0$ between the two bumps. This is adequate for demonstrating the support/topology mechanism. A generic point-spark normal form can be constructed by using analytic (non-compact-support) profiles or by tuning bumps so the neck pinch occurs at an isolated critical degeneracy; that classification is beyond the present scope.

## B.3. Induced (regularized) metric in 1D

In 1D, the induced metric is a scalar $g(x)$ multiplying $dx^2$. For clarity, we begin with the no-flux case $j=0$ (so we isolate the density + gradient geometry).

Take the auxiliary metric $g^{(\mathrm{aux})}=1$. Then (Eq. K)-(Eq. g) imply, on $\{C>0\}$,
$$
g(x) = 1 \;+\; \frac{\xi_C}{\lambda_C\,C(x)}\,(C'(x))^2.
$$

### Regularization (main text Section 3.5)

Define the $\varepsilon$-regularized metric
$$
g^{(\varepsilon)}(x) := 1 \;+\; \frac{\xi_C}{\lambda_C\,(C(x)+\varepsilon)}\,(C'(x))^2,
\qquad \varepsilon>0,
$$
and work on the domain $\Omega^\varepsilon(a)=\{x: C_a(x)\ge \varepsilon\}$.

Two immediate observations:

1. On plateaus where $C'\approx 0$, $g^{(\varepsilon)}\approx 1$: distances are approximately Euclidean.
2. Near steep boundary layers where $|C'|$ is large while $C$ is small, the ratio $(C')^2/(C+\varepsilon)$ becomes large, and the metric inflates. This expresses a basic RC geometric effect: *sharp coherence transitions create distance-stretching barriers.*

## B.4. Geodesic distance in 1D (explicit integral)

For two points $x_1<x_2$ in the same connected component of $\Omega^\varepsilon(a)$, the geodesic distance is simply the integral of the line element:
$$
d^\varepsilon(x_1,x_2;a)=\int_{x_1}^{x_2} \sqrt{g^{(\varepsilon)}_a(x)}\,dx
=\int_{x_1}^{x_2}\sqrt{1+\frac{\xi_C}{\lambda_C\,(C_a(x)+\varepsilon)}(C_a'(x))^2}\;dx.
$$

### What this example demonstrates

- **Distance is state-dependent:** changing $a$ changes $C_a$ and its gradient structure, hence changes $g^{(\varepsilon)}$ and the integral above.
- **Support-derived admissibility:** if $a=0$, points chosen one on the left bump and one on the right bump are in different components; no admissible path exists inside $\Omega^\varepsilon(0)$, so the distance is undefined/infinite in the RC sense.
- **Refinement-as-growth:** when $a>0$, a connecting corridor appears, and the same pair of points becomes connected by admissible paths; the distance becomes finite and computable.

A transparent comparison is to choose representative points near the centers of the two main bumps (e.g., $x_1=-1$, $x_2=+1$). For $a=0$, they are disconnected; for $a>0$, the distance exists and is dominated by the bridge region where coherence is low and gradients may be steep, producing a large contribution to the integral. This makes the "neck" not only topologically important but geometrically significant.

## B.5. Operational travel time in 1D (distinguishing shortest vs fastest)

In 1D there is only one path between two points (up to reparameterization), so "shortest" vs "fastest" cannot differ by route choice. Nevertheless, operational time still differs from geometric length because speed can depend on the coherence state.

To keep the example minimal while remaining intrinsic, take an illustrative speed law
$$
|v_C(x)| := v_0\,\frac{C_a(x)}{C_a(x)+\kappa},
\qquad v_0>0,\ \kappa>0,
$$
which captures a common qualitative behavior: propagation is slower in low-coherence regions and saturates in high-coherence regions.

Then the operational travel time is
$$
\tau^\varepsilon(x_1,x_2;a)
=\int_{x_1}^{x_2}\frac{\sqrt{g^{(\varepsilon)}_a(x)}}{|v_C(x)|}\,dx,
$$
where in computations one uses $C_a(x)+\varepsilon$ in the denominator to avoid singularity at the boundary.

This illustrates an RC point: a corridor that makes $d^\varepsilon$ finite may still yield a very large $\tau^\varepsilon$ if coherence in the corridor is low (small $C\Rightarrow$ slow propagation). Thus geometric connectivity and effective causal adjacency can differ sharply near refinement transitions.

## B.6. Induced basin graph for the toy family

For each $a$, define basins $B_i(a)$ as connected components of $\Omega(a)$ (or $\Omega^\varepsilon(a)$ if boundary regularization is retained).

- If $a=0$, there are two nodes $i=L,R$ and **no edge** between them (disconnected support).
- If $a>0$, there is one node (single basin); the basin graph collapses to a single vertex.

To obtain a nontrivial multi-edge example, one can extend the construction to three bumps (left-middle-right) and tune two bridges independently; then adjacency and flux coupling can be illustrated with a genuine multi-node graph. Even in the present two-to-one transition, the basin graph makes the refinement thesis explicit: the topological skeleton changes discretely while the continuum metric remains defined basin-wise.

## B.7. Illustrative 2D extension (route choice and "fastest path")

To demonstrate "shortest vs fastest" by different *routes*, we move to 2D where alternative paths exist.

Let $(x,y)\in\mathbb R^2$. Construct a coherence field with two high-coherence "islands" connected by two possible corridors:

- a short corridor with low coherence (slow),
- a longer corridor with high coherence (fast).

For instance, define
$$
C(x,y) = C_{\text{islands}}(x,y) + a\,C_{\text{corr,short}}(x,y) + b\,C_{\text{corr,long}}(x,y),
$$
with smooth compactly supported bumps for each component. The induced metric $g^{(\varepsilon)}$ is computed from $C$ and $\nabla C$ as in the main text, and operational speed is set by a coherence-sensitive law as in SectionB.5 (now with $C(x,y)$).

Then:

- **Shortest path (geodesic)** tends to prefer the geometrically shorter corridor, unless boundary gradients inflate the metric strongly.
- **Fastest path (minimizing travel time)** can prefer the longer corridor if it has higher coherence, hence higher $|v_C|$, yielding lower $\tau$.

This 2D example is best accompanied by a coherence heatmap and two overlaid paths (geodesic vs time-minimizer), computed numerically on a grid with $\varepsilon$-regularization. The purpose is interpretive: it makes concrete how RC separates geometric proximity from operational proximity.

## B.8. Summary

This appendix exhibits:

1. a support-defined domain and basin decomposition,
2. a refinement transition controlled by a neck parameter,
3. a regularized induced metric and explicit geodesic distance in 1D,
4. an operational travel-time functional that can blow up near low-coherence corridors even when geometric distance is finite,
5. the basin-graph representation of topology changes, and
6. (in 2D) the distinction between shortest and fastest paths via route choice.

The same pipeline extends directly to more realistic RC models once $C$, $v_C$, and coefficient conventions are imported from the core theory.

# Appendix C. Motion of identities (basin kinematics without Euclidean primitives)

The main text defines *what exists* at time $t$ as the support-derived domain $\Omega_t=\mathrm{supp}\,C(\cdot,t)$ and defines identities as its connected components $B_i(t)$. This appendix addresses a complementary question:

> Given a time-dependent coherence field $C(x,t)$, how do we define and track the **motion** of identities $B_i(t)$ intrinsically-without introducing Euclidean primitives?

We emphasize scope: this appendix is **kinematic**. It provides intrinsic definitions of basin position, velocity, deformation, and correspondence across time. Topology-changing refinement events (sparks) are treated as transitions where tracking must be re-initialized or branched; their classification is outside this paper.

## C.1. What "motion" means for an identity in RC

An identity is a *region* $B_i(t)\subset\Omega_t$, not a point. Accordingly, "motion" has at least three distinct aspects:

1. **Drift:** the identity's representative location changes (a trajectory).
2. **Deformation:** the shape/extent of $B_i(t)$ changes (boundary motion).
3. **Reorganization:** the internal distribution of $C$ within $B_i(t)$ changes (spectral/content dynamics).

The first two are geometric/kinematic; the third is dynamical and is already partially captured in the basin spectral hierarchy (Chapter 8). Here we focus on drift and deformation in a way that is compatible with the induced geometry.

## C.2. Choosing an intrinsic basin representative ("position")

To speak about a basin's drift, we select a representative point $x_i(t)$ defined purely from coherence and the induced geometry. Two standard, intrinsic choices are:

### (a) Peak representative

Assuming a unique maximizer exists in the basin interior, define
$$
x_i^{\max}(t) := \arg\max_{x\in B_i(t)} C(x,t).
$$

### (b) Coherence-weighted centroid (Riemannian)

Let $dV_g$ be the volume form of the induced metric $g(t)$ (or the regularized metric $g^{(\varepsilon)}(t)$ on $\Omega_t^\varepsilon$). Define the basin mass and centroid:
$$
M_i(t) := \int_{B_i(t)} C(x,t)\,dV_g,
\qquad
x_i^{\mathrm{cen}}(t) := \frac{1}{M_i(t)}\int_{B_i(t)} x\,C(x,t)\,dV_g.
$$
This definition depends on the chart for the coordinate embedding of $x$, but its weighting is intrinsic to the induced geometry and coherence distribution. In practice, the centroid is best interpreted as a coordinate representation of an intrinsic weighted average.

### Remarks on uniqueness and stability

If $C$ has multiple maxima or if a basin is highly multimodal, one can adopt a *set* of representatives (e.g., local maxima) and treat the basin as a small landmark graph internally. This aligns with the multilevel graph viewpoint of Chapter 10.

## C.3. Basin drift velocity from coherence transport

Given a coherence velocity field $v_C(x,t)$ (Chapter 5), a natural basin-level drift velocity is the coherence-weighted mean transport:
$$
\bar v_i(t) := \frac{\int_{B_i(t)} v_C(x,t)\,C(x,t)\,dV_g}{\int_{B_i(t)} C(x,t)\,dV_g}.
$$

This definition is intrinsic to the RC state: it uses $C$, $v_C$, and the induced volume form. It is also compatible with the Lorentzian layer (Appendix A): choosing a coherence-adapted shift $\beta^i\propto v_C^i$ corresponds to describing motion in a partially comoving frame.

When the centroid representative $x_i^{\mathrm{cen}}(t)$ is used, $\bar v_i(t)$ provides a natural candidate for $\dot x_i(t)$ in regimes where basin boundaries do not move too rapidly relative to interior transport.

## C.4. Deformation and boundary motion via level-set kinematics

Beyond drift, basins deform. A clean intrinsic handle on deformation is obtained by tracking a regularized boundary defined by a coherence level set.

Fix $\varepsilon>0$ and consider the $\varepsilon$-boundary of a basin component:
$$
\partial B_i^\varepsilon(t) \subset \{x \mid C(x,t)=\varepsilon\}.
$$
Assuming $\nabla C\neq 0$ on this level set (regular value), level-set kinematics gives the normal velocity of the boundary:
$$
V_n = -\frac{\partial_t C}{\|\nabla C\|},
\qquad \text{on } C=\varepsilon,
$$
where $\|\nabla C\|$ is computed with the chosen derivative convention (auxiliary or induced). This expresses the fact that the boundary moves so that the value $C=\varepsilon$ is maintained along the moving interface.

Interpretively:

- if $\partial_t C>0$ at the boundary, the $\varepsilon$-region expands,
- if $\partial_t C<0$, it contracts.

## C.5. Basin correspondence across time (identity tracking)

To speak about identity motion, we need to match basins across nearby times $t$ and $t+\Delta t$. Away from refinement events, the matching can be defined by maximizing overlap or minimizing an intrinsic discrepancy.

A minimal overlap-based correspondence is:
$$
j^\ast(i) := \arg\max_j \ \mu\!\left(B_i(t)\cap B_j(t+\Delta t)\right),
$$
where $\mu(\cdot)$ is an intrinsic measure (e.g., induced volume, or coherence-weighted volume $\int C\,dV_g$).

A coherence-weighted similarity is:
$$
S_{ij} := \frac{\int_{B_i(t)\cap B_j(t+\Delta t)} C(x,t)\,dV_g}{\int_{B_i(t)} C(x,t)\,dV_g},
$$
and correspondences can be chosen by maximizing $S_{ij}$ with mutual-consistency constraints.

## C.6. Handling refinement events (scope-limited protocol)

At a split or merge, basin correspondence is not one-to-one. For kinematic tracking it suffices to adopt a branching protocol:

- **Split:** if $B_i(t)$ corresponds to multiple $B_{j_k}(t+\Delta t)$, treat the identity as branching into child identities and distribute mass $M_i$ by overlap fractions.
- **Merge:** if multiple $B_{i_k}(t)$ correspond to one $B_j(t+\Delta t)$, treat the identity as merging, with $M_j$ obtained as the sum (or coherence-consistent recombination) of the parents.

This matches the discrete graph update picture in Chapter 10: split/merge are node operations. The kinematic definitions above supply continuous descriptors (representatives, drift) for each node before and after the event.

## C.7. Relation to distance notions in the main text

These kinematic constructions complement (rather than replace) the distance notions:

- Geodesic distance $d_t$ measures intrinsic proximity on each slice $(\Omega_t,g(t))$.
- Operational distance $\tau_t$ measures minimal travel time under coherence transport.
- Basin motion supplies a way to interpret time evolution of separation between identities, e.g.,
  $$
  t\mapsto d_t\!\left(x_i(t),x_j(t)\right),
  \qquad
  t\mapsto \tau_t\!\left(x_i(t),x_j(t)\right),
  $$
  with $x_i(t)$ defined by an intrinsic representative.

One can distinguish distance changes due to metric deformation (changing $g(t)$), identity drift/deformation (changing $B_i(t)$ and representatives), and refinement (changing connectivity/identity graph). This separation is often essential for interpreting "spatial change" in RC.

# Appendix D. Limiting regimes and sanity checks (interpretive anchors)

This appendix records several limiting regimes in which the induced-geometry construction reduces to familiar forms. These checks serve two purposes:

1. They provide interpretive anchors for readers coming from standard geometry/physics.
2. They expose which features of the distance theory are carried by which RC terms (density, gradient, flux, regularization).

Throughout we assume we are working on $\Omega_t^\varepsilon$ with the regularized metric $g^{(\varepsilon)}$ (main text Section 3.5), and we suppress explicit $(x,t)$ dependence where not needed.

## D.1. Uniform coherence (no gradients, no flux)

Assume $C(x,t)=C_0>0$ is spatially uniform on a region and $j=0$. Then $\nabla C=0$ and the coherence tensor reduces to the density term
$$
K_{\mu\nu} = \lambda_C C_0\,g^{(\mathrm{aux})}_{\mu\nu}.
$$
The induced metric (Eq. g) becomes
$$
g_{\mu\nu} = g^{(\mathrm{aux})}_{\mu\nu}.
$$
Thus distances reduce to the baseline auxiliary geometry on that region. This is the most basic sanity check: when coherence is homogeneous and inactive, RC does not invent spurious curvature.

## D.2. Gradient-only regime ($j=0$, nonuniform $C$)

Assume $j=0$ but $C$ varies spatially. With regularization,
$$
g^{(\varepsilon)}_{\mu\nu}
= g^{(\mathrm{aux})}_{\mu\nu}

+ \frac{\xi_C}{\lambda_C\,(C+\varepsilon)}\,(\nabla_\mu C)(\nabla_\nu C).
$$
Consequences:

- The second term is positive semidefinite (rank $\le 1$ if $\nabla C\neq 0$ but otherwise low-rank in special cases).
- Regions with sharp coherence transitions ($\|\nabla C\|$ large while $C$ is small) inflate the metric along gradient directions, creating distance-stretching barriers.

Interpretively: the gradient term encodes "tension" or "stiffness" against rapid coherence variation.

## D.3. Flux-only anisotropy ($\xi_C=0$, $j\neq 0$)

Assume $\xi_C=0$ while $j\neq 0$. Then
$$
g^{(\varepsilon)}_{\mu\nu}
= g^{(\mathrm{aux})}_{\mu\nu}

+ \frac{\zeta_C}{\lambda_C\,(C+\varepsilon)}\,j_\mu j_\nu.
$$
This is a rank-1 deformation aligned with $j$. If $u$ is a direction orthogonal to $j$ in the auxiliary metric, the second term does not contribute to $g^{(\varepsilon)}(u,u)$; if $u$ aligns with $j$, the metric is inflated along that direction.

Two interpretive notes:

- This term is often best thought of as encoding *directional structure* rather than "curvature" in the classical sense: the geometry becomes anisotropic along coherent currents.
- Whether this produces "highways" (lower effective operational distance) depends on how transport speed $|v_C|$ and lapse $N$ are chosen; the metric alone defines length, not propagation speed.

## D.4. Turning off RC structure: $\xi_C=\zeta_C=0$

If $\xi_C=\zeta_C=0$, then $K_{\mu\nu}=\lambda_C C\,g^{(\mathrm{aux})}_{\mu\nu}$ and the induced metric is exactly $g^{(\mathrm{aux})}$, independent of the magnitude of $C$. In this sense, the distance theory reduces to the baseline chart geometry unless one includes gradient and/or flux structure.

This clarifies a core design point: RC does not equate "more coherence" with "more distance"; instead, coherence shapes distance through *structure* (gradients and flux), with the density term providing normalization and baseline.

## D.5. Behavior as $\varepsilon\downarrow 0$

On interior regions where $C$ is bounded below by a positive constant, $g^{(\varepsilon)}\to g$ smoothly as $\varepsilon\to 0$. Near the support boundary $C\to 0$, regularization controls conditioning by replacing $1/C$ with $1/(C+\varepsilon)$.

Interpretively:

- $\varepsilon$ sets a coherence floor, consistent with finite resolution or minimal meaningful coherence.
- Distances computed on $\Omega_t^\varepsilon$ are therefore distances within the "realized" region above that floor.
- The $\varepsilon\downarrow 0$ limit is a mathematical idealization that should be interpreted as a controlled refinement of resolution.

## D.6. Micro vs macro stability under these limits

The micro/meso/macro hierarchy (Chapter 9) remains stable under the limiting regimes above:

- Within basins of approximately uniform $C$, distances become close to the baseline geometry.
- Near boundaries and corridors, gradients/flux dominate and produce the primary geometric and operational effects.
- The basin graph abstraction (Chapter 10) becomes particularly informative precisely in regimes where the continuum geometry is dominated by boundary/corridor structure.

# Appendix E. Conventions and non-circularity (explicit dependency diagram)

This appendix consolidates conventions that are otherwise distributed across the main text and clarifies the dependency structure so the construction is visibly non-circular.

## E.1. Derivative and operator conventions

We use two distinct notions of differentiation, depending on which geometric structure is already available.

1. **Auxiliary derivatives $\nabla^{(\mathrm{aux})}$.**
   Before the induced metric $g$ is constructed, gradients/divergences are understood with respect to the auxiliary chart structure. In coordinates this is typically ordinary differentiation, and we write $\nabla^{(\mathrm{aux})}$ when the distinction matters.

2. **Induced (Levi-Civita) derivatives $\nabla^{(g)}$.**
   After $g$ is defined, geometric objects such as geodesics, Laplace-Beltrami operators, and curvature use the Levi-Civita connection of $g$. We write $\nabla^{(g)}$ when needed.

**Practical rule.**

- $K[C]$ is built using $\nabla^{(\mathrm{aux})}$ acting on $C$ (and transport fields defined from $C$).
- Distances/geodesics/spectral objects are computed using $g$ and $\nabla^{(g)}$.

## E.2. Domain convention and regularization

Geometric objects are computed on the regularized domain $\Omega_t^\varepsilon=\{C(\cdot,t)\ge\varepsilon\}$ with the regularized metric $g^{(\varepsilon)}$. Limits as $\varepsilon\downarrow 0$ are interpreted as controlled resolution refinement, not as a requirement for practical use.

## E.3. Non-circular dependency diagram

The construction in this paper has the following dependency structure:

1. **Primitive:** $C(x,t)\ge 0$.
2. **Derived domain:** $\Omega_t^\varepsilon = \{x: C(x,t)\ge\varepsilon\}$ and basins $B_i(t)$.
3. **Transport (model choice):** $v_C[C]$ and $j=Cv_C$ (e.g., via continuity + closure).
4. **Coherence tensor:** $K[C]$ built from $C$, $\nabla^{(\mathrm{aux})}C$, and $j$.
5. **Induced metric:** $g^{(\varepsilon)}[C]\propto K[C]/(C+\varepsilon)$.
6. **Geometric distance:** $d_t^\varepsilon$ from $g^{(\varepsilon)}$ via geodesic length.
7. **Operational distance:** $\tau_t^\varepsilon$ from $ds^{(\varepsilon)}$ and $|v_C|$.
8. **Discrete skeleton:** basin graph $\mathcal G(t)$ with weights derived from $d_t^\varepsilon$ or $\tau_t^\varepsilon$.
9. **Lorentzian layer (optional):** choose lapse $N$ (and shift $\beta$) as functionals of $C$ and derived quantities.

At no stage is $g$ assumed prior to its construction; when $g$-covariant operations are used, they occur only after $g$ has been induced.

## E.4. Coordinate status

Coordinates are used as a descriptive reference frame. RC assigns ontological status to $\Omega_t$ (support-derived existence) and to the induced geometry $g(t)$, not to the ambient coordinate chart. This is essential for the "refinement rather than extension" interpretation: the point set that matters is $\Omega_t$, which can change topology without any coordinate enlargement.

# Appendix G. Design space and robustness (alternative choices)

The constructions in the main text are deliberately minimal. This appendix records nearby alternatives and clarifies which conclusions are robust to such choices.

## G.1. Alternative normalizations

We used
$$
g_{\mu\nu} \propto \frac{1}{C}\,K_{\mu\nu}
\quad\text{(regularized as }1/(C+\varepsilon)\text{)}.
$$
One can consider $1/C^\alpha$ for $\alpha\neq 1$. The qualitative effects are:

- $\alpha>1$ emphasizes low-coherence regions (stronger boundary stretching).
- $\alpha<1$ reduces boundary sensitivity (more uniform geometry).

The choice $\alpha=1$ is distinguished by the "relative-structure" motivation in the main text: it prevents absolute scaling of $C$ from trivially inflating all distances while preserving structural sensitivity through gradients and flux.

## G.2. Alternative gradient terms

Instead of $(\nabla C)\otimes(\nabla C)$, one may use second-derivative information (e.g., Hessian-based stiffness) or isotropized gradient energy (e.g., $\|\nabla C\|^2 g^{(\mathrm{aux})}$). The main tradeoff is:

- outer-product gradients produce directionally selective stiffness,
- isotropic gradient energy produces uniform stiffening proportional to gradient magnitude.

The positivity arguments remain straightforward so long as the added terms are positive semidefinite.

## G.3. Alternative flux contributions

We used $j\otimes j$ as the minimal positive semidefinite flux deformation. Alternatives include symmetrized derivatives of flux (capturing shear-like structure) or time-averaged flux covariances. These can encode richer anisotropies but come with higher regularity demands and potentially more modeling choices.

The robust conclusion is: any positive semidefinite flux-derived term introduces directional structure aligned with persistent transport patterns, which is the geometric basis for "highway-like" effects.

## G.4. Representative choices for identity motion

Appendix C described peak and coherence-weighted centroid representatives. Alternatives include:

- spectral landmarks (mode centers of low eigenmodes),
- medoids with respect to geodesic distance within a basin,
- multi-representative landmark sets for multimodal basins.

The robust conclusion is: the *existence* of basin kinematics does not depend on a unique representative; when uniqueness fails, one naturally transitions to a landmark graph within the basin, consistent with Chapter 10's multilevel picture.

## G.5. Robust claims under these variations

The following claims are stable under the design variations above (modulo technical regularity conditions):

1. Space as support $\Omega_t$ and identity basins $B_i(t)$ are derived from $C$.
2. A positive-definite Riemannian metric can be induced from nonnegative quadratic forms in $C$, $\nabla C$, and transport variables.
3. Geodesic distance and operational travel-time distance are canonical once $g$ and $v_C$ are specified.
4. Topology refinement changes the admissible path set and therefore changes which distances exist.
5. Flux-derived anisotropy provides a mechanism for directional structure in distances and propagation.

This separation-robust structural claims vs model-dependent choices-is important for interpreting RC distance as a family of compatible constructions rather than a single frozen formula.

# Appendix H. Glossary of key terms (RC distance and refinement)

This glossary provides a compact reference for the central objects used in the paper.

- **Coherence density $C(x,t)$:** the primitive nonnegative scalar field from which all geometry is derived.

- **Support-derived domain $\Omega_t$:** $\Omega_t=\mathrm{supp}\,C(\cdot,t)$. The set of spatial points that "exist" at time $t$ in RC.

- **Regularized domain $\Omega_t^\varepsilon$:** $\Omega_t^\varepsilon=\{x: C(x,t)\ge\varepsilon\}$, used to control boundary conditioning.

- **Identity basin $B_i(t)$:** a connected component of $\Omega_t$ (or $\Omega_t^\varepsilon$). Basins are the RC notion of discrete identities at time $t$.

- **Refinement:** discrete change in the basin decomposition (split/merge), i.e., topology change of the positive-coherence region. Interpreted as "growth by refinement," not coordinate extension.

- **Spark (scope-limited here):** the critical degeneracy condition associated with topology change of $\{C>0\}$. Used as a necessary condition; full classification is deferred.

- **Coherence flux $J_C$:** transport flux satisfying a continuity equation $\partial_t C+\nabla\cdot J_C=0$.

- **Coherence velocity $v_C$:** defined by $J_C=Cv_C$, typically closed by a state-dependent law.

- **Current $j$:** $j_\mu=Cv_{C,\mu}$; used in flux-derived contributions to geometry.

- **Coherence tensor $K[C]$:** symmetric tensor built from density, gradient, and flux contributions; the precursor to the metric.

- **Induced metric $g[C]$:** Riemannian metric obtained by normalizing $K[C]$ by $\lambda_C C$ (regularized by $C+\varepsilon$). Defines intrinsic line elements and lengths.

- **Geodesic distance $d_t$:** canonical intrinsic length distance on $(\Omega_t,g(t))$ (or regularized $d_t^\varepsilon$ on $\Omega_t^\varepsilon$).

- **Operational distance $\tau_t$:** minimal travel time functional using the induced line element and the coherence transport speed $|v_C|$.

- **Basin graph $\mathcal G(t)$:** discrete topological skeleton whose nodes are basins and whose edges encode adjacency or coupling (optionally weighted by geometric or operational distances).

- **Lapse $N$, shift $\beta$:** Lorentzian-layer fields (Appendix A) specifying a spacetime metric with spatial slices given by the induced $g(t)$.

- **Basin kinematics:** intrinsic motion/deformation/tracking of basins (Appendix C), defined without Euclidean primitives.

---

## Bibliography

- **Lee, J. M.** (1997). _Riemannian Manifolds: An Introduction to Curvature_. Springer. **ISBN:** 978-0387983226
- **do Carmo, M. P.** (1992). _Riemannian Geometry_. Birkhäuser. **ISBN:** 978-0817634902
- **O'Neill, B.** (1983). _Semi-Riemannian Geometry: With Applications to Relativity_. Academic Press. **ISBN:** 978-0125267403
- **Sethian, J. A.** (1999). _Level Set Methods and Fast Marching Methods: Evolving Interfaces in Computational Geometry, Fluid Mechanics, Computer Vision, and Materials Science_ (2nd ed.). Cambridge University Press. **ISBN:** 978-0521645577
- **Chavel, I.** (1984). _Eigenvalues in Riemannian Geometry_ (2nd ed.). Academic Press. **ISBN:** 978-0121706401
- **Rosenberg, S.** (1997). _The Laplacian on a Riemannian Manifold: An Introduction to Analysis on Manifolds_. Cambridge University Press. **ISBN:** 978-0521463003
- **Chung, F. R. K.** (1997). _Spectral Graph Theory_. American Mathematical Society. **ISBN:** 978-0821803158

- **Jovanovic, U.** (2025). *Reflexive Organism Model*.
- **Jovanovic, U.** (2025). *Seeds of life*
- **Jovanovic, U.** (2025). *Coherence in Reflexive Organism Model*
- **Jovanovic, U.** (2025). *Reflexive Coherence*
- **Jovanovic, U.** (2025). *Reflexive Coherence: A Geometric Theory of Identity, Choice, and Abundance*
- **Jovanovic, U.** (2025). *Fractal Reflexive Coherence*

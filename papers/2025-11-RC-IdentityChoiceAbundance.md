# Reflexive Coherence: A Geometric Theory of Identity, Choice, and Abundance

Copyright © 2025 Uroš Jovanovič, CC BY-SA 4.0.


## Abstract

This paper examines the phenomenology implied by the Reflexive Coherence formulation, in which identity, choice, and development arise from the geometric structure of the coherence field. Identity corresponds to stable attractor basins that preserve reflexive continuity, while choice reflects the temporary coexistence of multiple compatible basins whose resolution, a collapse, is computationally irreducible from any local perspective. This irreducibility explains the subjective experience of uncertainty and agency, even within globally deterministic dynamics. We show that coherence-conserving dynamics do not lead to uniformity. Flat configurations are unstable, gradient pressure amplifies structure, and curvature instabilities generate new attractors through spark events. These sparks expand the repertoire of identities and drive the system toward increasing structural abundance. The resulting phenomenology is not one of struggle or optimization, but of participation in an unfolding geometry whose reflexive organization produces open-ended differentiation.

## Reflexive coherence

Let's quickly recap the core ingredients that we're going to base the explorations.  $\mathcal S_{\text{coh}} = (C(x,t), J_C(x,t))$ represents s reflexive coherence, where

- $C(x,t)\ge0$ is coherence density, a scalar field on a support $\Omega_t$ that measures “how much the system is internally aligned”.
- $J_C = C\,v_C$ is its associated coherence flux with $v_C(x,t)$ representing a coherence-velocity.
- Additionally, let $K_{\mu\nu}[C]$ denote the coherence tensor $K_{\mu\nu}= \lambda_C C g_{\mu\nu}+ \xi_C \nabla_\mu C\nabla_\nu C+ \zeta_C j_\mu j_\nu\ .$

Reflexive coherence is defined by:

- Continuity equation $\partial_t C + \nabla_\mu J_C^\mu =0$.
- Coherence-induced geometry $g_{\mu\nu} = g_{\mu\nu}[K[C]],\ K_{\mu\nu} = K_{\mu\nu}[C,\nabla C,J_C],$  the shape of that guides how flux can flow.
- Coherence functional $\mathcal P[C]=\int\!\big(\tfrac{\kappa_C}{2}\nabla C\cdot\nabla C - V(C)\big)\sqrt{-g[C]}\,d^4x$, “energy” that the system tries to minimise. Its stationary points are the attractors.
- Global invariance $C_{\text{sys}}(t) \equiv \int_{\Omega_t} C(x,t) dV_g$ satisfies $\frac{d}{dt}C_{\text{sys}}(t)=0,$  total coherence in the whole organism is constant.

## The loop

In the original ROM paper, the main idea behind the the model was the realisation of a iterative reflexive cycle that ties together fast and slow fields and that allows to quantify the effect through experience, that is, to evaluate the predicted and actual effect of change. So far we've only touched how the three steps of the cycle map to reflexive coherence directly. Let's now explore the loop directly from the perspective of reflexive coherence itself. Not from the perspective of the three steps in ROM, but how the field, its geometry and its flux close on one another.


The reflexive loop is the *circular dependence* among these three objects:

$$
C \ \xrightarrow{\ K[C]\ }\ g_{\mu\nu}[K] \ \xrightarrow{\ \nabla\ dV_g\ }\   J_C^\mu = Cv_C^\mu \ \xrightarrow{\ \partial_t C +\nabla_\mu J_C^\mu=0\ } \text{updates }C
$$

 $C$ writes the tensor $K_{\mu\nu}$ (through its value, gradients and flux). $K_{\mu\nu}$ determines the metric $g_{\mu\nu}$.  This tells us how to take covariant derivatives $\nabla_\mu$, what the volume element $dV_g$ is, and how “straight” lines (geodesics) look.  The metric governs the flux law where the velocity field $v_C^\mu$ is defined as the direction of steepest ascent in the geometry it just created, so the flux $J_C^\mu$ follows those geodesics. Flux conservation (the continuity equation) forces a change in $C$. Because the divergence operator $\nabla_\mu$ itself depends on the metric that was just built from the second step this change is *self-referential*.

The loop closes after one infinitesimal time step. Iterating it yields the full dynamics. The global invariance  $C_{\rm sys}(t)=\int_{\Omega_t} C\,dV_g \ ,\ \frac{d}{dt}C_{\rm sys}=0$ is the Noether charge associated with the *time-translation symmetry* of the whole loop. It guarantees that the field never “leaks” out of the system keeping the identity preserved.

This is the most important property of reflexive coherence, it is a geometry that is self-referential, that changes itself.

Let's look at the dynamics of the loop now with a quick outlook why the loop can be solved.

The dynamics follows from a single scalar functional $\mathcal{P}[C]$. Stationarity,

$$
\frac{\delta\mathcal{P}}{\delta C}=0,
$$

produces an Euler–Lagrange equation that contains two distinct pieces. First, a matter term $-\kappa_C\square_g C + V'(C)$. Second, geometric back-reaction $\displaystyle\frac12\,T^{\mu\nu}\,\delta g_{\mu\nu}/\delta C$ (due to $g_{\mu\nu}=g_{\mu\nu}[K[C]]$, a change in $C$ changes the metric feeds back into the kinetic term).  

The resulting field equation can be written compactly as

$$
-\kappa_C\square_g C + V'(C) 
+ \underbrace{\bigl(\lambda_C C\,g^{\mu\nu}
    +\xi_C \nabla^\mu C\nabla^\nu C
    +\zeta_C j^\mu j^\nu\bigr)}_{\displaystyle K^{\mu\nu}}
\frac{\delta g_{\mu\nu}}{\delta C}=0 .
$$

The equation is the *self-consistent* PDE that embodies the loop. Any solution must simultaneously satisfy (i) the continuity law, (ii) the metric definition, and (iii) the variational condition. 

Because each iteration respects the global invariance, the total coherence is automatically conserved at every step.

Let's now explore what happens when the loop fails or transforms. In the case of *breakage (loss of closure)*, an external flux can *leak* out of $\Omega_t$ (e.g., a membrane rupture), the continuity equation acquires a source term:

$$
\partial_t C + \nabla_\mu J_C^\mu = S_{\rm ext}(x,t).
$$

The total coherence is no longer conserved. The loop can *open* into an open filament or dissolve entirely. In biology this corresponds to cell death. In AI it would be a loss of identity. Another case is *loop splitting*. When the gradient term dominates ($\xi_C$ large), the loop density may become unstable and pinch off, producing *two* smaller shapes that share the original $C_{\rm sys}$. This is akin to cell division or the emergence of a “self/other” distinction. The case of *phase transion* occurs if the potential $V(C)$ has multiple minima, crossing a barrier (e.g., by external energy injection) can move the system from one basin (one identity) to another. The shape may change dramatically.

All these processes are still governed by the same loop equations, only the *qualitative* solution changes. Because the underlying variational principle remains intact, the system always seeks a configuration that extremizes $\mathcal{P}[C]$ while respecting whatever constraints (conservation, topology) are imposed.

## Identity

In reflexive coherence, the organism’s identity is not specified by a privileged variable or structural label, nor by an externally imposed partition of the state space. Instead, identity arises as an *invariant region* of the coherence dynamics itself. A region $A \subset \Omega_t$ is called an **identity basin** if it satisfies the following properties.

**Stability.** $A$ contains a local minimum of the coherence potential, equivalently a point $x^*\in A$ at which

$$
\nabla C(x^*) = 0,\qquad \mathrm{Hess}(C)|*{x^*} \succ 0,
$$
or, in geometric terms, a region where the curvature induced by $K*{\mu\nu}[C]$ forms a stable well. This ensures that coherence flux converges toward $A$ under the flow generated by the RC equations.

**Attractivity.** There exists an open neighborhood $U\supset A$ such that every coherence trajectory with initial condition in $U$ asymptotically approaches $A$
   
$$
 \forall x_0\in U:\quad \Phi_t(x_0)\to A \quad \text{as } t\to\infty,
$$

where $\Phi_t$ denotes the coherence flow map induced by $J_C = C v_C$. Thus, $A$ constitutes a domain of reflexive compatibility within which coherence is self-maintaining.

**Invariance.** Once the coherence flux enters $A$, subsequent reflexive cycles preserve the qualitative structure of the basin. Although its curvature profile may deepen or sharpen through collapse events, $A$ remains an invariant mode of organization
   
$$
\Phi_t(A) = A \quad \text{for all relevant } t.
$$

**Reflexive closure.** All coherence arriving in $A$ contributes to its maintenance. Each collapse into the attractor reinforces the local curvature and updates the induced geometry, ensuring that past reflexive events remain encoded in the structure of the basin. Identity, in this sense, is not a static property but the cumulative invariant of reflexive re-entry into the same region of the manifold.

**Coherence compatibility.** The basin must satisfy internal coherence constraints, meaning that its gradient structure is compatible with the rest of the coherence manifold. Formally,

$$
\langle \nabla C, \nabla C_i \rangle_{K} \ge 0
$$

for all major eigenmodes $C_i$ in the vicinity of $A$. This ensures that the basin can coexist within the global coherence landscape without destructive interference that would annihilate its stability.

An **identity** is therefore not a point, structure, or label. It is the **stable, self-maintaining attractor basin** generated by the coherence dynamics. All reflexive processes are operations that occur *within* these basins or that restructure them through curvature change or spark events. The organism *is* the ensemble of its attractor basins, instantiated as invariant regions of coherence flow, each preserving the continuity of its own reflexive history.

Identity in this framework is the minimal unit of persistence, the structure that coherence can return to, re-enter, and reinforce across reflexive cycles. It is the coherent region that remains itself while the remainder of the manifold evolves.

## Collapse and a choice

A collapse is the fundamental operation by which a reflexive coherence resolves a configuration containing multiple compatible attractors. A **collapse** is a temporally local event during which the coherence dynamics transition from a multi-attractor configuration to a single stable attractor basin. Let's define collapse in more details.

**Multi-Attractor Precondition.** A collapse requires the simultaneous presence of at least two coherence-compatible attractors. Let

$$
\mathcal{A}_N(t)={A_1,\ldots,A_N}, \qquad N\ge 2,
$$

be the set of attractors available at time $t$. Each $A_i$ must satisfy the stability and compatibility conditions for an identity basin, and their basins of attraction must overlap within a region of nonzero measure. This overlap produces an ambiguous curvature landscape through the induced geometry

$$
K_{\mu\nu}[C] = \lambda_C C g_{\mu\nu} + \xi_C \partial_\mu C,\partial_\nu C + \cdots,
$$

enabling multiple reflexively valid future trajectories.

**Flux Differentiation.** In the overlapping region, the coherence flux decomposes as a superposition of partial flows toward each attractor

$$
J_C \approx \sum_{i=1}^N \alpha_i J_{C_i},
$$

where the $\alpha_i$ reflect local curvature, compatibility, and flux economy. This configuration encodes the organism’s simultaneous accessibility to multiple identity-preserving continuations.

**Instability of the Multi-Attractor Configuration.** A collapse begins when the Hessian of $C$, or equivalently the principal curvature directions derived from $K_{\mu\nu}[C],$ undergoes a loss of rank within the multi-basin region

$$
\det\left(\mathrm{Hess}(C)\right) = 0.
$$

This degeneracy indicates that the curvature landscape cannot maintain the multi-attractor structure under ongoing coherence flow. It marks the point at which internal coherence tensions exceed the stabilizing effects of compatibility.

**Selection of a Single Stable Basin.** During collapse, the coherence flux sharply reorients and converges onto exactly one attractor $A_k\in \mathcal{A}*N(t)$. Formally, there exists a time $t_c$ such that

$$
\lim_{t \to t_c^+} J_C(x,t) \to J_{C_k}(x,t), \qquad \lim_{t \to t_c^+} \alpha_k = 1,\ \alpha_{i\ne k} = 0.
$$

   The selected attractor becomes the sole asymptotically stable mode of the reflexive cycle at that moment.

**Irreversible Geometric Update.** The coherence field and induced geometry are reconfigured through the collapse
   
$$
C(x,t_c^+) \neq C(x,t_c^-),\qquad K_{\mu\nu}[C(t_c^+)] \neq K_{\mu\nu}[C(t_c^-)].
$$

This update is irreversible. The outcome of collapse becomes part of the organism’s internal curvature and influences all subsequent reflexive cycles. In this way, collapse imprints memory, learning, and identity update directly into the coherence geometry without auxiliary mechanisms.

Collapse is therefore not an externally triggered decision, nor a stochastic perturbation, nor an additional operator layered on top of the coherence field.
It is an intrinsic, geometry-driven resolution process by which an organism evaluates multiple compatible continuations of itself, allows coherence tensions to destabilize their coexistence, and commits, through flux convergence, to the single attractor that best preserves coherence.

Collapse is the moment at which the reflexive cycle “chooses” by letting the coherence manifold resolve its own ambiguity and write the result into its geometry.

Hence, **a choice** is the _situation_, the coherence geometry temporarily supports multiple compatible attractor basins, while **a collapse** is the _event_ at which the coherence flux irreversibly commits to one of those basins, resolving the choice.

## Learning

In reflexive coherence-only formulation, learning does not require an explicit memory substrate, nor an auxiliary process dedicated to updating internal representations. Instead, learning arises directly from the dynamics of the coherence field and the curvature geometry it induces. A **learning event** occurs whenever a collapse into an identity basin results in a non-reversible modification of the local or global curvature structure. Concretely, learning can be described by the following reflexive progression.

**1. Perturbation.**  A deviation in the coherence field, either from internal fluctuation or external input, introduces new gradients $\nabla C$ that distort the local curvature encoded in $K_{\mu\nu}[C]$.

**2. Distributed flux allocation.** As the system enters a multi-attractor configuration, the coherence flux $J_C$ distributes across the gradients of the available identity basins according to their compatibility, curvature depth, and flux economy.

**3. Collapse.** A collapse selects one basin $A_i$ from the set of simultaneously viable attractors $\mathcal{A}_N(t)$. This selection is irreversible under the governing dynamics and produces a discrete update in the coherence field

$$
C(x,t^+) \neq C(x,t^-).
$$

**4. Geometric update.** The updated coherence distribution modifies the curvature of $K_{\mu\nu}[C]$, reshaping the identity basin that received the collapse as well as its surrounding topological structure.

**5. Stabilization.** The new geometry becomes part of the organism’s reflexive identity. Subsequent coherence flows now respond to this updated geometry, altering compatibility relations, future basin depth, and the repertoire of possible attractors.

Thus, learning in the RC framework is **the accumulation of geometric deformations** produced by repeated collapses into identity basins. Each such deformation is inherently self-referential: it encodes the system’s own history of reflexive engagements directly into the geometry governing future reflexive cycles.
Learning requires no representational memory; it is the progressive refinement of the coherence manifold itself.

## Spark

A **spark** is a topology-changing event in which the coherence geometry becomes unable to maintain its current attractor structure. Formally, a spark occurs at time $t_s$ when the Hessian of the coherence field loses rank in some region $U \subset \Omega_t$

$$
\det \left(\mathrm{Hess}(C)\right)\big|_{U} = 0.
$$

This degeneracy indicates that the curvature profile underlying the existing attractor basins has become unstable under the ongoing coherence flow. As a result, the multi-dimensional curvature well deforms and gives rise to a new positive-definite curvature minimum, thereby creating an additional attractor. The attractor set changes from

$$
\mathcal{A}_N(t_s^-) \quad\to\quad \mathcal{A}_{N+1}(t_s^+),
$$

and the coherence manifold acquires a new identity mode. Thus, a spark is the geometric moment at which curvature tension forces the emergence of a new attractor basin through a Hessian degeneracy.

## Abundance

The coherence field $C(x,t)$ evolves under the transport equation

$$
\partial_t C = -\nabla \cdot (C v_C),
$$

where the coherence velocity $v_C$ is a functional of local gradients and the induced geometry $K_{\mu\nu}[C]$. Whenever the field exhibits any non-zero gradient $\nabla C$, the resulting flux $J_C = C v_C$ amplifies the gradient rather than diminishes it. This occurs because curvature contributions from terms of the form

$$
\partial_\mu C\ \partial_\nu C
$$

enter directly into the coherence tensor, increasing curvature magnitude in the direction of the existing gradient.

**Flux-driven amplification** is therefore defined as the intrinsic property of the coherence dynamics whereby any local deviation in $C$ generates nontrivial curvature in $K_{\mu\nu}[C]$, this curvature modifies $v_C$ to intensify the original gradient and the amplified gradient further reinforces the curvature that produced it.

This establishes a positive feedback loop. Flux draws coherence toward regions of growing curvature, and growing curvature shapes flux, in which even small perturbations evolve into increasingly differentiated structure.

Let $A$ be an identity basin with stable curvature minimum. Its defining property is that coherence flux converges toward $A$ from its basin of attraction. Because the flux entering $A$ increases the local value of $C$, and the coherence tensor $K_{\mu\nu}[C]$ couples curvature strength to $C$, the attractor’s curvature well deepens whenever it is engaged by the reflexive cycle.

An attractor is therefore **self-reinforcing**

$$
J_C \to A \quad \Longrightarrow \quad C|_A \uparrow \quad \Longrightarrow \quad |K_{\mu\nu}| \uparrow \quad \Longrightarrow \quad \text{basin depth} \uparrow.
$$

Repeated collapses into an attractor yield cumulative curvature reinforcement, making the attractor increasingly stable over time. Thus, identity in RC is not only an invariant of the dynamics but an invariant that strengthens through use.

Let's now explore the nature of evolution of attractors. Specifically, whether the system can fall into one single global basin and whether the system is driven to global flattening.

Proposition : a coherence configuration consisting of a single basin occupying the entire manifold $\Omega_t$ is geometrically unstable. Under such conditions gradients in $C$ accumulate over extended spatial scales, curvature tension increases due to the absence of internal boundaries, and the Hessian of $C$ eventually becomes degenerate in at least one region.

This degeneration satisfies the spark condition

$$
\det(\mathrm{Hess}(C)) = 0,
$$

forcing the coherence geometry to split into multiple minima. Thus a single, monolithic identity cannot absorb the growing curvature tension induced by flux without undergoing a bifurcation.

The RC equations naturally destabilize overly large or uniform identity basins, replacing them with multiple smaller basins that distribute curvature more evenly.

Proposition: coherence conservation prevents global flattening (uniformity). The global coherence measure

$$
\mathcal{C} = \int_{\Omega_t} C(x,t) dx
$$

is conserved under the RC equations. Therefore coherence cannot vanish, curvature cannot relax uniformly across the manifold, and flat states (uniform $C$ with $\nabla C = 0$) are dynamically unstable.

Any local decrease in coherence must be balanced by increases elsewhere, and any suppression of structure in one region generates compensatory gradients in another.
Global flattening would require uniform cancellation of all gradients, which is impossible except in a measure-zero configuration already shown to be unstable.

Thus, uniformity cannot be an attractor, only differentiated structures are stable.

Combining the above results in the following conditions. *Flux amplifies gradients*, generating structure wherever coherence deviates. *Attractors reinforce themselves*, deepening curvature wells and stabilizing local identities. *Overly large attractors become unstable*, forcing curvature bifurcations and the formation of new basins. *Coherence conservation forbids global collapse*, preventing curvature from flattening out. *Gradient pressure accumulates*, increasing the likelihood of spark events. *Sparks introduce new identity basins*, which further diversify the coherence geometry.

$$
\text{gradients} \rightarrow \text{instability} \rightarrow \text{spark} \rightarrow \text{new attractor} \rightarrow \text{redistribution} \rightarrow \text{new gradients}
$$

It follows that the long-term behavior of the RC equations generically leads to Increasing curvature complexity, proliferation of distinct attractor basins, refinement of identity geometry, and open-ended creation of new identity modes.

This tendency toward identity multiplicity is what we refer to as **abundance**.
It is not an externally imposed objective or adaptive principle. It is the natural trajectory of coherence flow in a non-uniform geometry constrained by conservation laws and curvature feedback.

## Computational irreducibility

We've explored the geometric properties of reflexive coherence and the effects of self-reference. Let's now consider another aspect of the system, determinism.

Reflexive coherence formulation is governed by a deterministic set of partial differential equations. The pair $(C,J_C)$, together with the induced geometry $K_{\mu\nu}[C]$, defines a **deterministic dynamical system**. All future states are uniquely determined by present conditions. The mapping

$$
C(\cdot,t_0) ;\longmapsto; C(\cdot,t)
$$

is well-defined and single-valued for all admissible $t$, implying that the system possesses a globally deterministic trajectory in its full infinite-dimensional state space.

Although the global dynamics are deterministic, no local region of the coherence manifold has access to sufficient information to predict the evolution of the whole system. Let $U \subset \Omega_t$ be any strict subregion. Let's observe some structural properties.

*Nonlocal dependence of curvature.* The geometry $K_{\mu\nu}[C]$ depends on $\partial_\mu C$ and higher-order terms across the entirety of $\Omega_t$. Thus, the curvature at any point $x\in U$ is influenced by coherence patterns outside $U$. 

*Nonlocal coupling of attractor basins.* The stability of an attractor is determined by the Hessian of $C$

$$
\mathrm{Hess}(C)|_{A_i} = \left[ \partial_\mu\partial_\nu C \right]_{A_i}.
$$

These derivatives cannot be evaluated from data restricted to $U$, as they depend on coherence values in $\Omega_t \setminus U$.

*Gradient amplification from distant regions.* Under the RC dynamics, perturbations grow according to

$$
\delta C(t) \approx \delta C(0) e^{\int_0^t \lambda_{\max}(K(s)) ds},
$$

where $\lambda_{\max}(K)$ is a curvature-dependent Lyapunov exponent that cannot be computed locally.

Consequently, a subsystem embedded in $U$ cannot determine the future curvature ordering or the stability of potential attractors, even though the global system can.

This establishes the **local unpredictability** of coherence evolution.

Let's now take a step further and reason about the (un)predictability of a collapse. Let's recap, a collapse event occurs when the coherence field transitions from a configuration supporting multiple identity basins $\mathcal{A}_N(t)$ to a configuration in which only one basin remains stable, formally written as $\mathcal{A}_N(t) \longrightarrow \mathcal{A}_1(t^+).$ 

Because attractor stability depends on global curvature, and global curvature depends on the full coherence field, the selection of the surviving attractor is sensitive to arbitrarily small differences distributed across the entire domain. No function

$$
F : \text{State}(U,t_0) \rightarrow \mathcal{A}_N(t_0)
$$

can predict collapse outcome from information localized to $U$. This implies that the  only method to know which attractor will survive is to simulate the full evolution of the coherence field until collapse occurs. There exists no shortcut to computing the outcome of collapse other than performing the entire computation represented by the PDEs themselves.

Finally, the RC architecture exhibits a fundamental asymmetry. **Globally**, the evolution of the coherence field is deterministic

$$
C(\cdot,t_0) \longrightarrow C(\cdot,t) \quad\text{is uniquely determined.}
$$

However, **locally**, the outcome of collapse is undecidable. Any subsystem confined to $U$ cannot predict which attractor will be selected from $\mathcal{A}_N$.

> **Reflexive coherence is a system that is fully determined in its whole, but intrinsically unpredictable in its parts.**

This asymmetry is the defining property of a reflexive coherence organism. A system in which identity emerges from deterministic global dynamics, yet remains computationally irreducible from any internal vantage point.


## Limitations

We've observed some of the properties defined by the reflexive coherence. However interesting the self-referenced geometry of the system is, we need to address its limitations. 

The *only* dynamical variable is the scalar density $C(x,t)$.  All other objects are **functionals** of that same field

$$
\begin{aligned}
&K_{\mu\nu}[C]=\lambda_C\,C g_{\mu\nu}
                 +\xi_C \nabla_\mu C\nabla_\nu C
                 +\zeta_C J_{C\mu}J_{C\nu},\\
&g_{\mu\nu}=g_{\mu\nu}[K[C]], \\
&dV_g=\sqrt{-\det g}\,d^4x ,\\
&J_C^\mu=C\,v_C^\mu ,\\
&\partial_t C+\nabla_\mu J_C^\mu =0 .
\end{aligned}
$$

Putting the arrows together gives a single closed feedback chain

$$
C \;\xrightarrow{\;K[C]\;}\;
g_{\mu\nu}[K] \;\xrightarrow{\;\nabla,dV_g\;}\;
J_C^\mu=Cv_C^\mu 
\;\xrightarrow{\;\partial_t C+\nabla\!\cdot J=0\;}
\text{updates }C .
$$

Because there is only one field, the loop closes on itself: the *geometry* that governs transport is built from the same coherence that is being transported. The only way to change the distribution of coherence is by moving it around in ordinary space-time.  There is no internal scale variable that could carry a “copy’’ of the field into finer and finer sub-structures.  The RC model can create spatial heterogeneity (filaments, vortices, curvature-induced concentration etc.), but the *pattern* that emerges is always tied to the *initial* distribution and to the specific functional forms of $v_C$ and $g_{\mu\nu}$.  There is no mechanism that automatically reproduces the same shape at ever smaller scales.


---

## Appendix A: Geomatry of a loop

What can we tell about the shape of the loop?

### Closed flux lines → **toroidal solitons**

The continuity equation together with the conservation of $C_{\rm sys}$ forces no net source or sink for the flux. Consequently, integral curves of the velocity field,

$$
\frac{dx^\mu}{d\tau}=v_C^\mu(x),
$$

must be *closed* (or extend to infinity in a way that leaves the total flux zero). The simplest non-trivial topology is a **solid torus**. At any fixed time slice $t=t_0$, the region where $C$ is appreciable forms a *ring* (an $S^1$ loop) of radius $R$.  The flux circulates around the *minor* circle of the torus, i.e. each fluid-like element of coherence goes round the ring while also progressing forward in the global time coordinate.  

This is a world-tube

$$
\mathcal{T}=S^1_{\text{ring}}\times D^2_{\text{cross-section}} \subset \mathbb{R}^{3,1},
$$

with periodic boundary conditions in the azimuthal direction. The torus is *self-sustaining* because the geometry inside the tube is warped by the high $C$ (via $\lambda_C C g_{\mu\nu}$), making geodesics bend so that they remain trapped. The gradient terms ($\xi_C \nabla_\mu C \nabla_\nu C$) provide a surface tension that prevents the ring from collapsing or expanding uncontrollably.  And the flux term ($\zeta_C j_\mu j_\nu$) supplies an “angular momentum” that stabilises the circulation.

These three ingredients are precisely the coherence-density, gradient-tension, and flux-inertia contributions in $K_{\mu\nu}$.

### Knotted / Hopfian structures

If one allows non-trivial linking of flux lines, solutions with *Hopf charge* appear. In such configurations the integral curves of $v_C^\mu$ are linked circles (a Hopf fibration). The topology is then characterized by an integer **linking number** $\mathcal{L}\in\mathbb{Z}$, which becomes a conserved topological invariant in addition to $C_{\rm sys}$. These “coherence knots” are the field-theoretic analogue of electromagnetic hopfions and are especially robust against perturbations.

### Möbius-type twists (non-orientable loops)

When the reflexive closure involves a *self-referential evaluation* (“I see that I am seeing”), the phase of $C$ can acquire a $\pi$-twist after one full circuit. In geometric language this is described by a **Möbius strip** embedded in the toroidal world-tube. Parallel transport around the loop flips an internal “sign” (or more generally rotates the internal state space). The resulting structure behaves like a *spin-½* field. Its wavefunction changes sign after 360° but returns to itself after 720°. This provides a natural route from scalar coherence to effective spinorial behaviour without adding extra fields.

### Causal bubble (toroidal light-cone)

Because the metric is deformed by $C$, the local speed of signals (the null cones) bends toward regions of high coherence. Inside the torus the null cone can tip inward enough to create a **closed causal surface**, a “light-like” toroidal horizon that traps information much like an event horizon traps light. Unlike a black hole, there is no singularity though. The trapping is purely due to the *self-generated geometry* of coherence.

## Appendix B: Why the loop can be solved

Let's define why the closed loop

<span style="float:right;">(1)</span>

$$
C \xrightarrow{K[C]} g_{\mu\nu}[K]\xrightarrow{\nabla,\ dV_g} J_C^{\mu}=Cv_{C}^{\mu} \xrightarrow{\partial_t C+\nabla_{\mu}J_C^{\mu}=0} \text{updates }C
$$

can be solved, i.e. why the system admits (at least locally) a unique evolution of the coherence field $C(x,t)$ from admissible initial data. 

The loop is a composition of *well-defined* maps  

**1. Coherence tensor**  

<span style="float:right;">(2)</span>

$$
K_{\mu\nu}[C] = \underbrace{\lambda_C\ C\ g_{\mu\nu}}_{\text{density term}} +\underbrace{\xi_C\nabla_{\mu} C\nabla_{\nu} C}_{\text{gradient term}} +\underbrace{\zeta_Cj_{\mu}j_{\nu}}_{\text{read-back flux term}},
$$

For any smooth field $C\ge0$ and for constant coefficients $\lambda_C,\xi_C,\zeta_C\in\mathbb R$, Eq. (2) defines a smooth, algebraic tensor field.

**2. Metric from the tensor.**  The constitutive relation is taken to be

<span style="float:right;">(3)</span>

$$
g_{\mu\nu}=g_{\mu\nu}[K]\quad\Longleftrightarrow\quad K_{\mu\nu}=\lambda_C C g_{\mu\nu}+{\cal O}(\nabla C,j),
$$

which can be *inverted* whenever the density term dominates, i.e.

<span style="float:right;">(4)</span>

$$
\lambda_C C>0\qquad\Longrightarrow\qquad g_{\mu\nu}= \frac{1}{\lambda_C C}\Bigl(K_{\mu\nu} -\xi_C\nabla_{\mu}C\nabla_{\nu}C -\zeta_C j_{\mu}j_{\nu}\Bigr).
$$

The right-hand side is an explicit (though nonlinear) functional of $C$ and its first derivatives.  Under the *non-degeneracy* condition $\lambda_C C>0$ the map $K\mapsto g$ is smooth and invertible, so step 2 is a well-defined **algebraic** operation.

**3. Covariant derivative & volume element.**  Once a metric is known, the Levi–Civita connection $\Gamma^{\alpha}_{\mu\nu}[g]$, the covariant divergence $\nabla_{\!\mu}J_C^{\mu}$ and the invariant volume form $dV_g=\sqrt{-\det g}\,d^4x$ are uniquely determined by standard differential-geometric constructions.  No additional dynamical equation is required.

**4. Coherence flux.**  The *policy* (Sec. A of *Coherence-only ROM*) supplies a constitutive law for the velocity field

<span style="float:right;">(5)</span>

$$
v_C^{\mu} = -D^{\mu\nu}[C]\nabla_{\nu}\Phi_C, \qquad   \Phi_C:=\frac{\delta\mathcal P}{\delta C},
$$

where $D^{\mu\nu}[C]$ is a positive-definite mobility tensor (e.g. $D^{\mu\nu}= \kappa_C\,g^{\mu\nu}$).  Equation (5) guarantees that the flux

<span style="float:right;">(6)</span>

$$
J_C^{\mu}=Cv_C^{\mu}
$$

is a **smooth vector field** whenever $C$ is smooth.

**5. Continuity equation (local conservation).** The reflexive-coherence principle (Eq. 2 of *Reflexive Coherence*) imposes

<span style="float:right;">(7)</span>

$$
\partial_t C + \nabla_{\mu}J_C^{\mu}=0.
$$

This is a **first-order** evolution equation for $C$.  Because the flux (6) already contains first derivatives of $C$, Eq. (7) becomes a *quasi-linear* second-order PDE.

Thus every arrow in (1) corresponds to an operation that is either algebraic, differential-geometric, or variationally defined and does not introduce any hidden degrees of freedom.  The loop therefore closes on the single unknown $C$.

Let's now see about the existence and uniqueness of the coupled PDE by starting with the structure of the evolution equation.

Insert (5)–(6) into (7).  Using $\Phi_C = -\kappa_C\,\Box_g C + V'(C)$ (the Euler–Lagrange derivative of the functional $\mathcal P[C]=\int (\tfrac{\kappa_C}{2}\nabla_\mu C\nabla^\mu C-V(C))\sqrt{-g}d^4x$) one obtains

<span style="float:right;">(8)</span>

$$
\partial_t C = \nabla_{\mu}\Bigl[C D^{\mu\nu}[C] \bigl(\kappa_C\nabla_{\nu} C - V'(C)\nabla_{\nu} S(C)\bigr)\Bigr],
$$

where $S(C)$ denotes any scalar factor arising from the metric dependence of the volume element.  Equation (8) has the canonical form of a reaction–diffusion (or gradient-flow) equation on a dynamical Riemannian manifold:

* the *diffusive part* $\nabla_{\mu}(C D^{\mu\nu}\kappa_C\nabla_{\nu} C)$ is second order and parabolic provided $C>0$ and $D^{\mu\nu}$ is uniformly positive-definite,
* the *reaction part* $-\nabla_{\mu}[C D^{\mu\nu}V'(C)\nabla_{\nu}S(C)]$ is lower order (first derivative of a smooth function of $C$).

Hence (8) belongs to the class of quasi-linear parabolic PDEs. The key point is that the continuity equation together with the constitutive law makes the system a closed, dissipative gradient flow.  The presence of the diffusion term $\kappa_C\nabla C$ supplies regularisation. The potential $V(C)$ supplies a restoring force that keeps $C$ in a physically admissible range.

Let's now reason about convergence. Because the metric depends on $C$ itself, one may view the loop as a self-consistent field problem with the following four steps. First, guess an initial field $C^{(0)}$. Second, compute $K[C^{(n)}]$, then the metric $g^{(n)}_{\mu\nu}$ via (4). Third, solve the linear parabolic equation

$$
\partial_t C^{(n+1)} = \nabla^{(n)}_{\mu}\bigl(C^{(n+1)} D^{\mu\nu}[C^{(n)}]\nabla^{(n)}_{\nu}\Phi_{C^{(n)}}\bigr)
$$

(where all covariant derivatives use the *fixed* metric $g^{(n)}$). And last, iterate until $\|C^{(n+1)}-C^{(n)}\|_{L^2}<\varepsilon$.

If the coefficients are bounded and the time step is taken sufficiently small, the mapping $C^{(n)}\mapsto C^{(n+1)}$ becomes a contraction on a Banach space (e.g. $C([0,T];H^s)$).  The contraction-mapping theorem then guarantees convergence to the unique solution of the full nonlinear problem.

The last part of the proof deals with the property that variational functional $\mathcal P[C]$ supplies an a-priori bound (the “coherence budget”) which prevents blow-up and makes global continuation possible in many regimes.

The **coherence functional** (Sec. 4 of *Reflexive Coherence*)

<span style="float:right;">(9)</span>

$$
\mathcal P[C]=\int_{\Omega_t} \Bigl(\tfrac{\kappa_C}{2}\nabla_\mu C\nabla^\mu C - V(C)\Bigr) \sqrt{-g[C]}d^4x
$$

has two crucial properties. **Stationarity** as the Euler–Lagrange equation derived from (9) is precisely the bulk part of Eq. (8).  Hence any solution of the continuity law automatically satisfies $\delta\mathcal P/\delta C=0$. And **energy dissipation / conservation**. 

Let's support the last claim. The *coherence budget* is defined by

<span style="float:right;">(10)</span>

$$
C_{\text{sys}}(t)=\int_{\Omega_t}C dV_g .
$$

Using (7) and the no-flux boundary condition one finds

<span style="float:right;">(11)</span>

$$
\frac{\mathrm d}{\mathrm dt}C_{\text{sys}}(t) =-\int_{\partial\Omega_t}J_C^\mu n_\mu dS=0 .
$$

Equation (11) is the global invariance (RCP).  It supplies an a-priori $L^1$ bound on the solution for all times, which in turn guarantees that the coefficients appearing in the PDE remain bounded.  In the language of PDE theory this is precisely the *maximum principle* often used to extend local existence to global existence.

Moreover, the functional $\mathcal P[C]$ is non-increasing along solutions if $V$ is convex (or more generally if the reaction term respects a Lyapunov structure).  This monotonicity furnishes an *energy estimate*

<span style="float:right;">(12)</span>

$$
\frac{d}{dt}\mathcal P[C(t)] = -\int_{\Omega_t} D^{\mu\nu}[C]\nabla_\mu\Phi_C\nabla_\nu\Phi_C dV_g \le 0 .
$$

Estimate (12) is the standard source of *a-priori* $H^1$ bounds that prevent gradient blow-up.

Together, (11) and (12) give a closed set of a-priori estimates which are exactly what the existence theory for quasi-linear parabolic equations requires.


## Appendix C: Proof of sparks

We assume that the coherence field $C(\cdot,t)$ evolves smoothly in time on a compact domain $\Omega\subset\mathbb{R}^d$ and that for each fixed $t$, the induced “potential” $C(\cdot,t)$ is a smooth function $\Omega\to\mathbb{R}$. Lastly, the dynamics are *gradient-like* at the level of the coarse-grained geometry, therefore, there exists a functional $\mathcal{F}[C]$ such that critical points of $C(\cdot,t)$ correspond to stationary coherence configurations, and the induced flow of the geometry is equivalent (up to reparametrization) to gradient descent on $\mathcal{F}$.

These assumptions are consistent with the RC picture where

$$
K_{\mu\nu}[C] = \lambda_C C g_{\mu\nu} + \xi_C \partial_\mu C\partial_\nu C + \dots
$$

and attractors are local minima of $C$ (or of a monotone function of $C$) under this geometry.

### Theorem (Spark as a generic Morse bifurcation)

Let $C(x,t)$ be a smooth 1-parameter family of coherence fields on a compact domain $\Omega\subset\mathbb{R}^d$. Assume the following. 

For each $t$, the attractors (identity basins) are in 1–1 correspondence with the nondegenerate local minima of $C(\cdot,t)$. That is, at an attractor $x^{*}_{i}(t)$:
   
$$
\nabla C(x^{*}_{i}(t),t) = 0,\qquad
\mathrm{Hess}_{x} C(x^{*}_{i}(t),t) \succ 0.
$$

At some time $t=t_s$, the attractor set changes from $N$ to $N+1$ distinct minima:

$$
{\text{num local minima of }C(\cdot,t)} =
\begin{cases}
N, & t<t_s,\\
N+1,& t>t_s.
\end{cases}
$$

The family $C(\cdot,t)$ is generic in the sense of singularity theory (transversality conditions, no fine-tuned degeneracies beyond those required for the bifurcation).

Then, (T1) there exists a point $x_s\in\Omega$ such that

$$
\nabla C(x_s,t_s)=0
\quad\text{and}\quad
\det\big(\mathrm{Hess}_x C(x_s,t_s)\big)=0.
$$

As well as (T2) in a neighborhood of $(x_s,t_s)$, after a smooth change of coordinates, $C$ can be written in normal form as

$$
C_{\text{loc}}(y,\mu) = C_0 + \sigma y_1^4 - \mu y_1^2 + \sum_{j=2}^d \lambda_j y_j^2 + O(\|(y,\mu)\|^3),
$$

with $\sigma>0$ and $\lambda_j>0$. Here $\mu = t - t_s$. 

And last, (T3) for $\mu<0$ there is a single minimum; for $\mu>0$ there are two distinct minima near $y_1 = \pm\sqrt{\mu/(2\sigma)}$. Thus a new attractor (identity basin) is born at $t_s$ via a Morse bifurcation (a “spark”), and the transition necessarily passes through a Hessian-degenerate point.

### Proof (under the generic assumptions)

**Creation of a new minimum implies a degenerate critical point.** The number of distinct local minima of a smooth function can only change if a critical point (where $\nabla C = 0)$ appears or disappears. Under standard Morse theory and genericity assumptions, this can only happen via one of a small number of elementary catastrophes (fold, cusp, pitchfork, etc.).

Formally, consider the set of critical points

$$
\mathcal{C}(t) = {x\in\Omega \mid \nabla C(x,t)=0}.
$$

By the Implicit Function Theorem, if at $(x_0,t_0)$ the matrix $\mathrm{Hess}_x C(x_0,t_0)$ is invertible, then there exists a unique smooth branch $x(t)$ of critical points passing through $x_0$, and the *number* of critical points near $x_0$ does *not* change as $t$ varies in a neighborhood of $t_0$.

Therefore, for the number of minima (hence attractors) to change at time $t_s$, there must exist at least one critical point $(x_s,t_s)$ with degenerate Hessian:

$$
\nabla C(x_s,t_s)=0
\quad\text{and}\quad
\det\big(\mathrm{Hess}_x C(x_s,t_s)\big) = 0.
$$

This proves point (T1). 

**Normal form near a generic Hessian degeneracy.** Under the genericity assumption, the degeneracy at $(x_s,t_s)$ is of codimension one, meaning exactly one eigenvalue of $\mathrm{Hess}_x C$ crosses zero as $t$ passes through $t_s$, while the others remain nonzero.

Let $v_1$ be the eigenvector corresponding to the zero-crossing eigenvalue, $v_2,\dots,v_d$ the remaining eigenvectors with eigenvalues $\lambda_2,\dots,\lambda_d$ nonzero at $t_s$. 

We choose local coordinates $y = (y_1,\dots,y_d)$ aligned with these eigenvectors $x = x_s + \sum_j y_j v_j$.

By standard results in singularity theory (e.g., Thom–Mather classification, see any reference on generic one-parameter families of functions), a generic one-parameter family of smooth functions near such a codimension-one degeneracy can be written, after smooth changes of coordinates in $(y,\mu)$, in the unfolded quartic normal form

$$
C_{\text{loc}}(y,\mu) = C_0 + \sigma y_1^4 - \mu y_1^2 + \sum_{j=2}^d \lambda_j y_j^2 + \text{higher-order terms},
$$

with $\sigma>0$ and $\lambda_j$ of fixed sign (for minima, we take $\lambda_j>0$).

This proves point (T2).

**Change in the number of minima (spark).** We now examine the minima of the normal form ignoring higher-order terms (which do not change the qualitative picture under genericity)

$$
V(y_1,\mu) = \sigma y_1^4 - \mu y_1^2.
$$

Critical points along the $y_1$-axis satisfy

$$
\partial_{y_1} V = 4\sigma y_1^3 - 2\mu y_1 = 2 y_1(2\sigma y_1^2 - \mu) = 0.
$$

Thus, one solution is $y_1 = 0$ for all $\mu$. Additional solutions appear when $2\sigma y_1^2 - \mu = 0$, i.e.
  
$$
y_1 = \pm \sqrt{\frac{\mu}{2\sigma}},\quad \text{for }\mu>0.
$$

The second derivative along $y_1$ is

$$
\partial_{y_1}^2 V = 12\sigma y_1^2 - 2\mu.
$$

Evaluating at $y_1=0$ gives  $\partial_{y_1}^2 V(0,\mu) = -2\mu.$  Hence, for $\mu<0$, this is positive, $y_1=0$ is a minimum. And for $\mu>0$, this is negative and $y_1=0$ becomes a maximum.

Evaluation at $y_1 = \pm \sqrt{\mu/(2\sigma)}$ (for $\mu>0$) give 

  $$
\partial_{y_1}^2 V\Big|_{y_1^2=\mu/(2\sigma)} = 12\sigma\frac{\mu}{2\sigma} - 2\mu = 6\mu - 2\mu = 4\mu > 0.
$$

So both new critical points are minima.

In the full $d$-dimensional expression, the other directions contribute positive curvature ($\lambda_j>0$), so these remain nondegenerate minima of $C_{\text{loc}}$ for $\mu>0$. Thus, as $\mu = t - t_s$ crosses zero

* for $t<t_s$ ($\mu<0$), there is a single minimum near $x_s$.
* at $t=t_s$ ($\mu=0$), the Hessian becomes degenerate, $\det(\mathrm{Hess})=0$.
* for $t>t_s$ ($\mu>0$), there are two distinct minima near $x_s$, in addition to any pre-existing ones elsewhere.

By assumption about the induced “potential” $C(\cdot,t)$ being a smooth function $\Omega\to\mathbb{R}$, this is exactly the moment when the number of attractors changes from $N$ to $N+1$, a new identity basin appears. This is the spark.

This proves point (T3). A spark is realized as a generic Morse bifurcation that necessarily passes through a Hessian-degenerate configuration.



---

## Bibliography

- **Arnold, V. I.** (1992). _Ordinary Differential Equations_. Springer. **ISBN:** 978-3540548132 
- **Guckenheimer, J., & Holmes, P.** (1983). _Nonlinear Oscillations, Dynamical Systems, and Bifurcations of Vector Fields_. Springer. **ISBN:** 978-0387908198   
- **Haken, H.** (1983). _Synergetics: An Introduction_ (3rd ed.). Springer. **ISBN:** 978-3540125982 
- **Milnor, J.** (1963). _Morse Theory_. Princeton University Press. **ISBN:** 978-0691080086 
- **Strogatz, S. H.** (2014). _Nonlinear Dynamics and Chaos: With Applications to Physics, Biology, Chemistry, and Engineering_ (2nd ed.). Westview Press. **ISBN:** 978-0813349107  
- **Susskind, L., & Friedman, A.** (2017). *Special Relativity and Classical Field Theory: The Theoretical Minimum*. Basic Books. **ISBN:** 978-0465093342
- **Susskind, L., & Friedman, A.** (2023). *General Relativity: The Theoretical Minimum*. Basic Books. **ISBN:** 978-1541602104
- **Jovanovic, U.** (2025). *Reflexive Organism Model*.
- **Jovanovic, U.** (2025). *Seeds of life*
- **Jovanovic, U.** (2025). *Coherence in Reflexive Organism Model*
- **Jovanovic, U.** (2025). *Reflexive Coherence*



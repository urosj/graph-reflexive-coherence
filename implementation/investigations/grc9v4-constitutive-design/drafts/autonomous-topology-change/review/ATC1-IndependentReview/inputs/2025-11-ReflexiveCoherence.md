# Reflexive Coherence

Copyright © 2025 Uroš Jovanovič, CC BY-SA 4.0.

## Abstract

We propose a reduced formulation of the Reflexive Organism Model in which **coherence** is the only primitive dynamical field. All structures—organs, networks, memory, policies, assembly pathways, and experience—arise as _derived functionals_ of this field and of the geometry it induces. The coherence potential defines stable identity basins, while coherence flux governs reconfiguration, learning, and environmental coupling. Reproduction and pruning appear as topology-changing events in the coherence landscape. This coherence-only ROM shows that the entire organismal identity and behavior can be derived from the conservation, redistribution, and curvature of a single scalar field.

## Reflexive coherence

Let

$$
\mathcal S_{\text{coh}} = (C(x,t), J_C(x,t))
$$

represent **reflexive coherence**, where:

- $C(x,t)\ge 0$ be a **coherence density field** on a support $\Omega_t$,
- $J_C(x,t)$ its associated **coherence flux**, with

$$
J_C = C v_C,
$$

where $v_C(x,t)$ is a coherence-velocity.
  
Let $K_{\mu\nu}[C]$ denote the **coherence tensor**, i.e. the effective geometry induced by $C$ and its gradients,

$$  
K_{\mu\nu} \equiv \underbrace{\lambda_C C g_{\mu\nu}}_{\text{coherence density term}} + \underbrace{\xi_C \nabla_\mu C \nabla_\nu C}_{\text{coherence gradient term}} +   \underbrace{\zeta_C j_\mu j_\nu}_{\text{read-back flux term}}.  
$$

The **coherence-only ROM** is defined by:

1. A **global invariance** (conservation of total coherence)

$$
C_{\text{sys}}(t) \equiv \int_{\Omega_t} C(x,t) dV_g \quad\text{satisfies}\quad \frac{d}{dt}C_{\text{sys}}(t)=0,
$$

   where $dV_g$ is the volume element of the induced metric $g_{\mu\nu}[C]$.

2. A **local continuity equation**

$$
\partial_t C + \nabla_\mu J_C^\mu = 0 .
$$

3. A **coherence geometry** given by a constitutive relation

$$
g_{\mu\nu} = g_{\mu\nu}[K[C]],\qquad K_{\mu\nu} = K_{\mu\nu}[C,\nabla C,J_C],
$$

which plays the role previously carried by the metric, assembly and active tensors.

4. A **coherence functional**

$$
\mathcal P[C] = \int \Big(\frac{\kappa_C}{2}\nabla_\mu C \nabla^\mu C - V(C)\Big)\sqrt{-g[C]}d^4x
$$

whose stationarity $\delta \mathcal P/\delta C = 0$ and constitutive closure for $v_C$ together generate the dynamics of $C$ and $J_C$.

Thus, **coherence is the scalar field whose geometry, dynamics, and invariants encode the organism’s structural complexity, experiential groundedness, and reflexive closure. It is the conserved quantity that defines identity and the generative field from which all internal geometry and functionality of the organism emerge.**

---

## Appendix Zero: Mapping of the classical ROM state into coherence

The original ROM state was defined as a tuple

$$
\mathcal{S} = \big(\Omega, \mathcal{A}, \mathcal{G}, X(t), F(t), M(t), \Sigma, \Pi, \Upsilon, \mathcal{R}, \mathcal{P}(t), AI(t), \mathcal{E}(t)\big).
$$

In the coherence-only formulation, each component is realized as a functional of the coherence field and its geometry.

**Domain $\Omega$ as emergent support of coherence.** The spatial domain is no longer primitive. We define

$$
\Omega_t \equiv \text{supp}\ C(\cdot,t) = \overline{{x \mid C(x,t) > 0}},
$$

with topology and metric inherited from $g_{\mu\nu}[C]$. In this sense, *“space” is where coherence is non-zero and geometrically stable*.

**Action alphabet $\mathcal{A}$ as admissible coherence deformations.** Actions are no longer organs. Each “organ class” in the old ROM defined a *pattern of allowed flows* and f*eedback channels*. In the coherence-only ROM, these become simply *patterns of how coherence may locally move*. They become admissible local deformations of the coherence field

$$
\mathcal{A} \subset \left\lbrace \mathcal{O}: C \mapsto C' \big| \partial_t C' + \nabla \cdot J_C'[C'] = 0, C' \ge 0 \right\rbrace.
$$

That is, an “action” is any operator that redistributes coherence while respecting conservation and non-negativity.

**Internal network $\mathcal{G}$ as coherence-induced graph.** The explicit internal graph is replaced by an **emergent network** extracted from coherence basins and flux channels. Let

- $\lbrace B_i(t)\rbrace_i$ be a partition of $\Omega_t$ into coherence basins (e.g. connected components of super-level sets of $C$),
- and define edge weights by time-integrated flux

$$
w_{ij}(t) \equiv \int_{t-\Delta t}^{t} \int_{\partial B_i\cap\partial B_j} J_C \cdot n_{ij} dS d\tau .
$$

Then the **induced graph** is

$$
\mathcal{G}(t) \equiv \big(V(t),E(t),w(t)\big),\quad V(t)={B_i(t)}_i,\quad E(t)={(i,j)\mid w_{ij}(t)>0}.
$$

This $\mathcal{G}(t)$ is now a *derived* object, $\mathcal{G}(t)=\mathcal{G}[C,J_C]$.

**Organ states $X(t)$ as coarse-grained coherence patterns.** Each “organ” is identified with a coherence basin $B_i(t)$. Its state is the restriction (or low-dimensional projection) of the field

$$
x_i(t) \equiv \Phi_i[C(\cdot,t)] \in \mathbb{R}^{k_i},
$$

for some coarse-graining functional $\Phi_i$ (e.g. averages of $C$ and its gradients over $B_i$). The collection $X(t)={x_i(t)}_i$ is thus a **summary of the field**, not an independent degree of freedom.

**Fast fields $F(t)$ and memory $M(t)$ as spectral components of coherence**. Given the induced metric $g_{\mu\nu}[C]$, let ${\phi_k}$ be eigenfunctions of the Laplace–Beltrami operator $-\Delta_{g[C]}.$ We may expand

$$
C(x,t) = \sum_{k} c_k(t) \phi_k(x).
$$

Define a cutoff $\Lambda>0$. Then

$$
F(t) \equiv {c_k(t)\mid \lambda_k>\Lambda},\qquad
M(t) \equiv {c_k(t)\mid \lambda_k\le \Lambda},
$$

so that “fast” and “memory” modes are separated by their spectral scale. Again, both are **decompositions of $C$**, not new fields.

**Sensing $\Sigma$ as boundary and source functionals of coherence.** Let $I$ denote external inputs. In the coherence-only ROM, sensing is how inputs modulate boundary conditions or sources of $C$. Formally,

$$
\Sigma: I \mapsto \big(\mathcal{B}[I],\mathcal{S}[I]\big),
$$

where $\mathcal{B}[I]$ prescribes boundary data for $C$ (Dirichlet/Neumann/Robin), and $\mathcal{S}[I]$ prescribes any admissible source/sink terms (subject to global conservation). The “sensed state” is the induced perturbation of $C$ under $(\mathcal{B},\mathcal{S})$.

**Policy $\Pi$ as constitutive law for coherence flux.** The policy no longer maps a symbolic state to a symbolic action. It is encoded in the **constitutive relation** that turns coherence geometry into coherence flow

$$
J_C(x,t) = C(x,t) v_C(x,t),\qquad
v_C(x,t) = \Pi_{\text{coh}}\big(\nabla C,K_{\mu\nu}[C],x,t\big).
$$

Here $\Pi_{\text{coh}}$ is a response functional specifying how flux aligns with gradients and curvature. It plays precisely the role that the policy + actuators played previously, but as a **local law of motion** rather than a separate object.

**Actuation $\Upsilon$ as redistribution of coherence.** Actuation becomes the explicit divergence term in the continuity equation. For any effective policy $\Pi_{\text{coh}}$ and sensing map $\Sigma$, we can write

$$
\partial_t C = -\nabla \cdot \big(C \Pi_{\text{coh}}[\cdot]\big)
\equiv \Upsilon_{\text{coh}}[C;I],
$$

so $\Upsilon$ is no longer a separate operator on $(X,F,M)$. It is the **vector field** driving $C$.

**Reproduction/senescence $\mathcal{R}$ as topology changes of coherence support.** Reproduction and pruning are represented as topology-changing events of the coherence field. Let $\lbrace\Omega_t\rbrace_t$ be the (possibly disconnected) support of $C$. When a viability functional $V[C]$ crosses thresholds, we allow **surgical updates**

$$
\mathcal{R}_{coh}:\ C(\cdot,t^-)\mapsto C(\cdot,t^+),
$$

such that $C_{\text{sys}}$ is redistributed between connected components of $\Omega_t$ (spawning/merging basins, extinguishing low-coherence regions). Thus $\mathcal{R}$ becomes a rule for **splitting/merging coherence basins** under viability constraints.

**Assembly pathway $\mathcal{P}(t)$ as trajectory in coherence configuration space.** Let $\mathcal{C}$ be the space of admissible coherence fields. The assembly pathway is the **history curve**

$$
\mathcal{P}(t) \equiv { C(\cdot,\tau)\mid 0\le \tau\le t} \subset \mathcal{C},
$$

optionally summarized as a geodesic or minimum-action path between a reference configuration $C_{\text{init}}$ and $C(\cdot,t)$ with respect to some metric on $\mathcal{C}$. The discrete assembly narrative is thus a coarse-grained description of the continuous trajectory of coherence.

**Assembly index $AI(t)$ as coherence functional via induced graph.** The assembly index becomes a **coherence functional** defined via the induced graph $\mathcal G[C]$. Concretely,

$$
AI(t) = \mathcal{I}\big[\mathcal{G}(t)\big] = \mathcal{I}\big[\mathcal{G}[C(\cdot,t)]\big],
$$

where $\mathcal{I}$ is the usual Assembly Theory functional (e.g. shortest directed path length). In the continuum limit, this can be recast directly in terms of coherence flow lines $\gamma$:

$$
AI(t) = \min_{\gamma\ \text{coherence-admissible}} \int_\gamma \ell\big(C,J_C\big) ds,
$$

for an appropriate local cost density $\ell$. Either way, $AI$ is no longer an independent coordinate, but a **scalar extracted from $C$** and its induced connectivity.

**Experience index $\mathcal{E}(t)$ (EI, $EI^\star$) as flux–curvature alignment.** Finally, the experience index becomes a scalar functional of coherence and its flux

$$
EI^{\star}(t) = \mathcal{E} [C, J_C] (t),
$$

for example of the general form

$$
\mathcal{E}[C,J_C] = \int_{\Omega_t} \Phi\big(C,\nabla C,J_C\big) dV_g,
$$

where $\Phi$ measures alignment between flux and coherence gradients (closed-loop, “felt” use of structure). The specific choice recovers the previous $EI^\star$ (world-coupled, prediction-calibrated) but is now explicitly realized as a *curvature-flux invariant* of the coherence field.

The classical scalar invariants of ROM, assembly and (grounded) experience, are retained only as *coherence-derived quantities*

$$
C_{\text{sys}}(t) = \big(AI(t)\big)^{\alpha[C]} \big(EI^\star(t)\big)^{\beta[C]},
$$

with $\alpha[C],\beta[C]$ state-dependent exponents determined by the coherence geometry (they are constitutive response functions, not independent coordinates) defined as

$$
\begin{aligned}
\alpha[C] &= f_\alpha\left( |\nabla C|_{g[C]}, \mathrm{Tr}(K_{\mu\nu}[C]), C_{\text{slow}} \right), \\
\beta[C] &= f_\beta \left( \frac{J_C^\mu \nabla_\mu C}{|J_C| |\nabla C|},
|j_\mu|, C_{\text{fast}} \right).
\end{aligned}
$$

A canonical pair for example $\alpha[C] = 1 + k_\alpha\frac{\mathrm{Tr}(K_{\mu\nu}[C])}{\max_x C(x,t)}$ and $\beta[C] = 1 + k_\beta \left|\frac{J_C^\mu \nabla_\mu C}{\|J_C\| \|\nabla C\|}\right|.$

Let's close this section now with the iterative reflexive cycle. The cycle's definition

$$
\begin{aligned}
\mathcal{E}_P^{(k)} &= W_P(\Phi_P^{(k)}) \quad\text{(perceptual error)},\\
\Psi_{O_i}^{(k)} &= G_i(F_i(\mathcal{E}_P^{(k)})) \quad\text{(organ reaction)}, \\
\Phi_P^{(k+1)} &= \mathcal{Q}_\ell^{(P)}\big({\Psi_{O_i}^{(k)}}\big)
\quad\text{(memory / internal geometry update)}
\end{aligned}
$$

needs to be must be expressed in terms of coherence geometry and coherence flow

$$
\begin{aligned}
\text{Perception:} && &\delta C^{(k)} = \mathcal B\big[C^{(k)}\big] \\
\text{Reaction / Action:} && &J_C^{(k)} = J_C[C^{(k)}] \\
\text{Identity update:} && &C^{(k+1)} = C^{(k)} - \Delta t \nabla_\mu J_C^{\mu (k)},
\end{aligned}
$$

where $\mathcal B[\cdot]$ encodes boundary perturbations (sensing), and the update

$$
C^{(k+1)} = C^{(k)} + \Delta t \partial_t C = C^{(k)} - \Delta t \nabla_\mu J_C^\mu
$$

is the identity/memory/geometry update. 

In summary, the entire original state

$$
\mathcal{S} = \big(\Omega, \mathcal{A}, \mathcal{G}, X, F, M, \Sigma, \Pi, \Upsilon, \mathcal{R}, \mathcal{P}, AI, \mathcal{E}\big)
$$

is mapped into the pair $(C,J_C)$ and its induced geometry $K_{\mu\nu}[C]$, with all other quantities appearing as **functionals or emergent structures** of this coherence field.

---

## Appendix A: Coherence velocity

We define the coherence velocity as the *unique vector field* that satisfies

$$
J_C^\mu = C v_C^\mu
$$

and

$$
J_C^\mu = g^{\mu\nu}[C] \left(\lambda_C \nabla_\nu C + \xi_C \nabla^\alpha C K_{\nu\alpha} + \zeta_C j_\nu \right).
$$

Therefore

$$
v_C^\mu(x,t) = \frac{1}{C(x,t)} g^{\mu\nu}[C] \left( \lambda_C \nabla_\nu C + \xi_C \nabla^\alpha C K_{\nu\alpha}[C] + \zeta_C j_\nu \right).
$$

In the coherence-only ROM, the coherence velocity $v_C$ is the constitutive relation that maps coherence geometry into coherence flow. It is determined entirely by the gradients, curvature, and read-back currents of the coherence field. An **alternative formulation for coherence velocity** is derived through the use of coherence potential $\Phi_C$

$$
v_C^\mu = - D^{\mu\nu}[C] \nabla_\nu \Phi_C,
$$

with

$$
\Phi_C \equiv \frac{\delta \mathcal{P}[C]}{\delta C},
$$

where $\mathcal{P}[C]$ is the coherence functional already introduced in the coherence-only ROM description.

Then the full dynamics are

$$
\partial_t C + \nabla_\mu \left[C,D^{\mu\nu}[C],\nabla_\nu \Phi_C \right] = 0.
$$

## Appendix B: Coherence functional

Let's explore a bit more about the dynamics defined by **coherence functional $\mathcal P[C]$**. The coherence functional

$$
\mathcal P[C] = \int \Big(\frac{\kappa_C}{2} \nabla_\mu C \nabla^\mu C - V(C)\Big)\sqrt{-g[C]} d^4x
$$

is the analogue of a *free-energy functional* or *action functional* for the coherence field. It assigns a single scalar to any admissible configuration of coherence density $C(x,t)$.

The functional defines the geometry via $g_{\mu\nu}[C]$, the dynamics via stationarity $\delta \mathcal P / \delta C = 0$ and stability / viability via the value of the functional itself. It replaces **all** of the following from the old ROM: free energy, memory stability constraints, assembly/active stress tensors, compatibility consistency constraint, intent functional and viability functional. Everything collapses into this one object.

The funcitonal is composed of three terms: gradient term $(\displaystyle \frac{\kappa_C}{2}\nabla_\mu C \nabla^\mu C)$, potential term $V(C)$ and metric term $\sqrt{-g[C]}d^4x$. 

Gradient term encodes spatial coherence. It is large if coherence varies sharply, or the field is fragmented or basins have sharp walls. It pushes the field toward smooth and integrated configurations. This term replaces the role of the compatibility tensor in ROM.

Potential term encodes intrinsic preference for certain coherence densities. For example, double-well representing two stable coherence phases, or soft plateau representing multi-basin organism, or steep well of tightly integrated identity.  This term replaces AI, EI, reserve dynamics and spark thresholding in a single scalar potential.

The metric $g_{\mu\nu}[C]$ is induced by the coherence field itself (via the coherence tensor $K_{\mu\nu}[C]$). Which implies that the *geometry* of the organism is created by coherence,
curvature wells are the seeds, geodesics represents the eigenmodes, and metric deformations show area of learning / growth.

We get the **equations of motion** by extremizing $\mathcal P[C]$

$$
\frac{\delta \mathcal P}{\delta C} = 0.
$$

This gives the coherence-field PDE

$$
\nabla_\mu\big(\kappa_C \nabla^\mu C\big) - V'(C) + \text{metric-coupling terms}(g[C],\partial g[C]) = 0.
$$

This replaces all old ROM dynamical pieces: $\partial_t X = f(X,F,M,\Pi)$, flux $\leftrightarrow$ memory consistency, curvature update rules, compatibility conservation, policy dynamics, reserve updates and reproduction/pruning triggers.

Everything now follows from:

- **a conservation law** $\partial_t C + \nabla_\mu(C v_C^\mu)=0,$
- **a constitutive law for flux:** $v_C^\mu = -D^{\mu\nu}[C]\nabla_\nu \left(\frac{\delta \mathcal{P}}{\delta C}\right),$
- **and the variational equation** $\delta \mathcal P/\delta C = 0$.

This is exactly analogous to a gradient-flow dynamics in the space of coherence fields.

## Appendix C: Coherence basin $B_i(t)$

Let $C(x,t)\ge 0$ be the coherence density field on its induced manifold $(\Omega_t, g_{\mu\nu}[C])$. A coherence basin at time (t) is a maximal connected region of $\Omega_t$ in which coherence is locally self-stabilizing. Formally

$$
B_i(t) \equiv \text{a connected component of the stable sublevel/critical set of }C(\cdot,t)
$$

where stability is defined by the following conditions.

**1. Local extremum condition (critical point).** A point $x^\ast \in B_i(t)$ satisfies $\nabla_\mu C(x^\ast,t) = 0,$ and the Hessian of $C$ with respect to the induced metric $g[C]$ is positive definite $\nabla_\mu\nabla_\nu C(x^\ast,t)$ is positive definite. This makes the point a *local maximum* of coherence density, the “center” of the basin.

**2. Attraction condition (basin of flow).** Let the coherence flux be $J_C = Cv_C$, and let $\Phi_{J_C}^\tau(x)$ denote the flow generated by this vector field. Then the basin consists of all points whose integral curves converge to the same local maximum

$$
B_i(t) = \lbrace x\in\Omega_t | \lim_{\tau\to +\infty} \Phi_{J_C}^\tau(x) = x_i^\ast \rbrace,
$$

where $x_i^\ast$ is a coherence maximum as above. This makes $B_i(t)$ exactly analogous to an attractor basin in dynamical systems, but defined on the coherence field.

**3. Geometric stability condition.** The region $B_i(t)$ must satisfy $K_{\mu\nu}[C] u^\mu u^\nu > 0$ for all nonzero tangent vectors $u^\mu$ in $B_i(t),$ i.e. the coherence tensor is locally positive along all directions. This ensures the basin is a *coherence well* (a region where curvature reinforces coherence).

**4. Connectivity condition.** $B_i(t)$ is a maximal connected open set. So once the three above conditions hold, you take the connected component, that is the basin.

Each basin is therefore a curvature well of the coherence field and acts as an emergent “organ” or functional subunit of the organism.

Let's make a quick observation, a geometric interpretation of the basin. Coherence basins are the *natural partitions* of the coherence field. They correspond to the *stable attractor regions* of the coherence geometry. They serve as the coherence-only analog of organs in the old ROM. Their boundaries are coherence saddles where $\nabla C = 0$ and $\nabla^2 C$ has mixed eigenvalues.

## Appendix D: Topology-changing update $\mathcal{R}_{coh}$

$\mathcal{R}_{\text{coh}}$ is the **topology‐changing update** of the coherence field. It is the coherence-only replacement for the ROM reproduction/pruning operator $\mathcal{R}$ (which used viability and organ states to decide when to split or collapse parts of the organism).

Let $C(x,t^-)$ and $C(x,t^+)$ be the coherence fields immediately *before* and *after* a topology-changing event. Then $\mathcal{R}_{\text{coh}}:\ C(\cdot,t^-)\ \longrightarrow\ C(\cdot,t^+)$ is a non-continuous update map satisfying

1. **Global coherence conservation** $\int_{\Omega_{t^-}} C(x,t^-)dV_{g[C^-]} = \int_{\Omega_{t^+}} C(x,t^+)dV_{g[C^+]}.$
2. **Topology change** $\Omega_{t^-} \not\cong \Omega_{t^+}$ or number of coherence basins changes $|{B_i(t^-)}|\neq |{B_i(t^+)}|.$
3. **Viability thresholding** $V[C(\cdot,t^-)] \lessgtr \theta_{\text{coh}} \quad\Longrightarrow\quad \mathcal{R}_{\text{coh}} \text{event}.$
4. **Local stability restoration** $C(\cdot,t^+)$ must lie in a basin of $\mathcal{P}[C]$ (a local minimum of the coherence potential).

We can interpret three canonical cases for the operator.

**Basin splitting (reproduction / spawning).** If a coherence basin becomes unstable at its midpoint (e.g. due to flux bifurcation), then

$$
\Omega_{t^-} = B \quad\longrightarrow\quad \Omega_{t^+} = B_1 \cup B_2,
$$

with

$$
C(x,t^+) = C(x,t^-)\big|_{B_1} + C(x,t^-)\big|_{B_2}.
$$

This is the coherence-only version of making a *new organism*.

**Basin merging (pruning / senescence).**  If a basin’s viability dips below threshold $B_i(t^-)$ then the operator collapses it and redistributes its coherence

$$
C(x,t^+) =
\begin{cases}
C(x,t^-)+ C_{B_i}, & x\in \text{neighbor basin(s)} \\
0, & x\in B_i(t^-)
\end{cases}
$$

This is the coherence-only analogue of pruning an organ or collapsing an unviable subunit.

**Basin extinction (collapse)** occurs if a basin is completely dissipated (e.g. eaten, starved, or outcompeted) noted as $C(x,t^+)=0$ on that basin. This corresponds directly to ROM’s senescence/death operator.

Let's now relate this all to the dynamics. Between events, coherence evolves continuously by the PDE

$$
\partial_t C + \nabla_\mu(Cv_C^\mu)=0.
$$

But at discrete times $t_1,t_2,\dots$, when viability conditions trigger it, $\mathcal{R}_{\text{coh}}$ produces a **jump:**

$$
C(\cdot,t_i^+) = \mathcal{R}_{\text{coh}}[C(\cdot,t_i^-)].
$$

So the full dynamics are **continuous flow** of coherence, interrupted by **event-driven topology updates**.

## Appendix E: Potential $V(C)$

In the coherence functional, the potential term $V(C)$ specifies the *internal thermodynamic landscape* of the organism in the space of coherence densities.
It encodes which coherence configurations are energetically favored, stable, self-maintaining, viable, or unstable.

Just as in physical field theories (e.g., double-well potentials in phase transitions), the shape of $V(C)$ determines how many stable states exist, whether basin creation occurs, when basins split or merge, and how identity persists or changes.

In ROM all of these functions were previously spread over separate objects (compatibility, memory, reserves, reflexive operator, assembly tensors). In the coherence-only world they are *all absorbed by the shape of the potential*.

We've mentioned the three canonical forms, so let's explore them.

**Double-well potential**. A double-well means there are *two distinct stable coherence phases*, high-coherence state $C=C_{\text{high}}$ and low-coherence state $C=C_{\text{low}}$. This represents an organism that has two preferred modes of being. For example dormant vs active colony phases, sparse vs dense mycelial states, or exploratory vs exploitative ecological modes. We can define it as

$$
V(C) = -\tfrac{a}{2}C^2 + \tfrac{b}{4}C^4,\qquad a,b>0.
$$

This is the minimal polynomial capable of producing two stable coherence phases separated by an unstable barrier. The negative quadratic term destabilizes the low-coherence state, while the positive quartic term restores global boundedness and creates two energetic minima.

It implies that a perturbation can push the field from one minimum to the other (phase change), which corresponds to metamorphosis-like transitions, or reorganization of the organism, colony switching between foraging architectures, or ant colony switching from weakly to strongly trail-driven behavior.

Double wells are also where sparks naturally arise as the system can be pushed from one “identity” to another by surpassing the barrier.

**Soft plateau potential (multi-well)**. A soft plateau means that the field tolerates **multiple basins** of coherence at once, several distinct coherence densities are almost equally stable and the system can sustain multi-organism or multi-module configurations. This corresponds to multi-basin superorganisms (polycentric colonies), forests with multiple stable guild cores, brain-like systems with several specialized modules, and multi-node “identity clusters” that coexist.

We can define them as

$$
V(C)\ \text{has a broad flat region}.
$$

For example

$$
V(C) = \alpha C^2 - \beta C^4 + \gamma C^6,\quad \beta^2 > 4\alpha\gamma.
$$

A plateau allows multiple coherence basins (organs) to remain stable, dynamic restructuring without loss of overall identity, and “federated” organism architecture.

**Steep single-well potential** state that the system has one very strongly preferred coherence density. These represents strongly integrated organism, or high coherence-pressure to remain unified. We can define it something like

$$
V(C)=\tfrac{k}{2}(C-C_0)^2,\qquad k\gg 1.
$$

The steep well potentials correspond to eusocial colonies with rigid caste structure, or tightly coordinated tissues, also strongly canalized development, or organismal identities that resist splitting (reproduction is costly).

In such areas we can expect that basin splitting is rare, pruning tends to collapse small basins quickly and that the entire coherence remains locked in a narrow state. This is the limit where ROM behaves like a classical organism with a single persistent body plan.

Because in the coherence functional $\mathcal P[C]=\int \left( \frac{\kappa_C}{2}|\nabla C|^2 - V(C) \right)dV,$ the extrema of $\mathcal P[C]$ are the equilibria, and the *minima of $-V(C)$* determine which coherence densities the organism wants to maintain, how many identities it supports, how easy it is to split or merge, how stable memory and structure are, the depth of coherence basins (organs). 

$VC$ is immensely expressive. The potential shape defines the identity architecture, the gradient stiffness defines structural coupling, minima defines attractor basins, barrier height corresponds to the spark threshold and number of minima is the number of stable coherence phases. 

In ROM, this is spread through $\mathcal G$, $M$, AI, EI, $\rho_{\text{compat}}$, $\Pi$, actuation rules, reserve budged and spark criteria.

## Appendix F: Continuity equation

The central invariant of the coherence-only ROM is 

$$
C_{\text{sys}} = \int_{\Omega_t} C(x,t) dV_{g[K[C]]} \qquad\text{and}\qquad \frac{d}{dt} C_{\text{sys}} = 0.
$$

If the *total coherence* is conserved, then coherence can only move within the organism, but never be created or destroyed. Conservation of total coherence implies a local conservation law for the coherence density. As the coherence flux $J_C^\mu = Cv_C^\mu$ is derived from the induced coherence geometry, coherence evolves according to the continuity equation

$$
\partial_t C + \nabla_\mu J_C^\mu = 0,
$$

which states that coherence changes at a point only through the divergence of flux. No local source or sink of coherence exists. All increase in one region corresponds to an equal decrease elsewhere. This continuity equation is the local expression of the global invariant $\frac{d}{dt}C_{\text{sys}}=0$, and replaces all explicit growth, depletion, compatibility, and reserve terms of the original ROM.

Putting it all together, the coherence flux $J_C^\mu$ is defined by the constitutive relation

$$
J_C^\mu = g^{\mu\nu}[K[C]]\left(\lambda_C \nabla_\nu C + \xi_C \nabla^\alpha C K_{\nu\alpha}[C] + \zeta_C j_\nu\right)]
$$

and total coherence is conserved. Therefore, $C$ satisfies

$$
\partial_t C = -\nabla_\mu J_C^\mu,
$$

which governs all redistribution, reconfiguration, and basin formation in the coherence landscape.

Note that coherence is conserved only internally, not absolutely. Internal coherence $C_{\text{sys}} = \int_{\Omega_t} C dV_{g[K]}$ is conserved only in the absence of boundary inflows/outflows. The general form is

$$
\partial_t C + \nabla_\mu J_C^\mu = S_{\text{coh}},
$$

where

- $S_{\text{coh}}>0$ defines external coherence influx,
- $S_{\text{coh}}<0$ defines external coherence loss.

In the first chapter, we initially present the *closed-system* version $S_{\text{coh}} = 0$ because it defines the internal dynamics. But the full organism must include the possibility of coherence injection. External inputs enter through the boundary as flux, not as internal creation

$$
S_{\text{coh}}(x,t) = J_C^\mu n_\mu \Big|_{\partial\Omega_t}.
$$

Thus, we still have the generalized second law from original ROM paper. The continuity equation expresses internal coherence conservation, while the experience-driven entropy pump persists as boundary-driven coherence influx that, through flux–curvature alignment, locally increases order without violating the global invariant.

## Appendix G: Boundary perturbation operator

External inputs act on the coherence field only through its boundary. The boundary perturbation operator

$$
\mathcal{B}\lbrack C\rbrack(x,t)
$$

is defined as a functional that modifies $C$ on $\partial\Omega_t$ such that

$$
\delta C(x,t) = \mathcal{B}\lbrack C\rbrack(x,t)\quad\text{for }x\in\partial\Omega_t,
$$

and $\delta C=0$ in the interior. This operator captures all forms of sensing, environmental coupling, and external energy/matter inflow, without introducing internal sources.  Mathematically,

$$
\mathcal{B}[C] = \bigl( C_{\rm ext} - C\bigr) \big|_{\partial\Omega_t} ,
$$

where $C_{\rm ext}$ encodes the environmental boundary condition (e.g. nutrient availability, stimuli, neighbor interaction). This makes sensing a boundary condition, not an internal variable.

## Appendix H: Proper time

In the original ROM, each hierarchical level (organ, organism, colony, guild) carried its own induced metric and therefore its own proper time. Proper time was tied to the level’s internal memory dynamics and structural curvature. Slow memory modes generated slow metrics, fast modes generated fast ones, and a hierarchy of memory timescales produced a hierarchy of proper times.

In the coherence-only formulation this structure remains, but in a greatly simplified and unified form. Since coherence $C(x,t)$ is the sole primitive field, the organism’s geometry is now encoded entirely in the coherence tensor $K_{\mu\nu}[C]$ from which the induced metric at any coarse level $\ell$ is obtained by appropriate averaging

$$
g^{(\ell)}_{\mu\nu} = g_{\mu\nu}[K[C]]_{\text{coarse over level }\ell}.
$$

Each coherence basin $B_i(t)$ (a stable region of the coherence landscape) has its own local geometry $g^{(i)}*{\mu\nu}$ and its own characteristic coherence relaxation time. Let

$$
C|_{B_i}(x,t) = \sum_k c_{i,k}(t)\phi_{i,k}(x)
$$

be the spectral decomposition of coherence restricted to the basin. The **slowest non-trivial mode** determines the basin’s **integration timescale** $\tau_i$. This leads directly to a proper time for that level

$$
d\tau_i = \frac{1}{c}\sqrt{-g^{(i)}_{\mu\nu}[K[C]]dx^\mu dx^\nu}.
$$

Thus, the hierarchy of proper times in ROM survives unchanged in meaning, but emerges without separate memory fields, update rules, or graph structures. It is now a direct consequence of coherence geometry.

**Each coherence basin evolves according to its own induced metric, and therefore experiences its own proper time, set by the slow modes of its coherence field.**

Graphs were useful scaffolding for expressing connectivity and timescale coupling in early ROM formulations. In the coherence-only picture they are no longer needed. The basin structure, induced metric and coherence flow together generate the same hierarchy of internal clocks in a continuous, geometric form.

## Appendix I: Coarse-graining

In the coherence-only ROM, coarse-graining still exists, but its *meaning* and *location* have changed dramatically. It is no longer an explicit operator $\mathcal Q_\ell$ acting on organ states, memory states, or graph levels to produce higher-level summaries. Instead, **coarse-graining becomes a geometric and spectral property** of the coherence field itself.

Let the coherence field be expanded in eigenmodes of the induced Laplace–Beltrami operator

$$
C(x,t) = \sum_{k=0}^{\infty} c_k(t) \phi_k(x), \qquad -\Delta_{g[K]} \phi_k = \lambda_k \phi_k.
$$

Low-frequency (small $\lambda_k$) modes then represent slow, large-scale patterns, interpreted as _**coarse**-grained structure_. High-frequency (large $\lambda_k$) modes represent fast fluctuations, interpreted as fine details / rapid reactions.

The coarse-grained coherence field is

$$
C_{\text{coarse}}(x,t) = \sum_{\lambda_k \le \Lambda} c_k(t) \phi_k(x),
$$

where $\Lambda$ is a cutoff separating “macro” and “micro” scales. Coarse graining happens automatically in two places. First, **within each basin (intra-level coarse-graining)**. A basin $B_i$ has its own internal geometry $g^{(i)}$. Its slowest eigenmode defines its identity, its next few modes define substructure, and its high modes define momentary microstates. Thus, the basin inherently coarse-grains itself

$$
C|_{B_i} \longmapsto C_{\text{coarse}}^{(i)}.
$$

No operator is needed. Coarse structure is *the geometry of slow modes*.

The second place when coarse graining automatically happens is **across levels (inter-level coarse-graining)**. When considering a collection of basins $B_1,\dots,B_n$ their combined low-mode spectrum defines the next-level geometry. This produces a hierarchy automatically.  Formally

$$
C_{\text{coarse}}^{(\ell+1)} = \text{projection of } C \text{ onto low modes of union of basins at level } \ell.
$$

Thus, coarse-graining in the coherence-only ROM is the extraction of persistent, large-scale structure from the coherence field by projecting onto its slow geometric modes. Hierarchical levels correspond to nested sets of these slow modes, and proper times correspond to their relaxation timescales.

## Appendix J: Additional definitions

**Viability functional.** In the coherence-only ROM, the viability of an organism is defined as the negative coherence functional

$$
V[C] = -\mathcal P[C],
$$

Stable organisms correspond to local minima of $\mathcal P[C]$ (maxima of $V[C]$). Reproduction or pruning events occur when $V[C]$ crosses threshold values, replacing the original ROM condition $V(X,F,M;I)>\theta$.

---

## Reflection: Coherence

So what is coherence? Is it a number? A product? Density?

Coherence looks like a scalar value $C(x,t)$, but that is only the *representation* not the meaning. **Coherence is the *total self-consistency* of an organism’s structure, experience, and dynamics, compressed into a single invariant scalar field.**

Everything else (organs, policy, memory, graph, flow, identity) becomes an *emergent structure of this field*. So coherence is a field, not a number. But it is also the **only field**.

The global coherence invariant is $C_{\text{sys}} = (AI)^{\alpha[C]} (EI^\star)^{\beta[C]}.$ This is not a definition but a constraint. Thus **coherence is the conserved “joint contribution” of structure and experience.**  But coherence is *more than the product*. The product is the global budget. The local field $C(x,t)$ is the way this budget is distributed across space, time, and internal geometry.

However, the most important interpretation is that coherence is density of reflexive closure. **Coherence measures how well the feedback loop closes at each location.**

High coherence means that signals complete the loop without distortion, structure and experience reinforce each other, and the organism “knows how to be itself”. Low coherence on the other hand means reflexive loops leak or break, sensory signals don’t match memory, action–consequence mappings fail, and identity destabilizes.

**Coherence induces the organism’s internal geometry.** The metric is no longer stored separately and **space is where coherence lives**, and geometry is the shape coherence imposes.

Coherence moves through the organism. Its **flow** determines behavior, morphology changes, learning, planning, resource allocation, organ differentiation. The velocity $v_C$ is the **policy** in the coherence-only world. In other words, **coherence redistribution is emergent behavior**.

Coherence is also viability measure. **The organism is viable precisely when coherence lies in a local minimum of the coherence potential.** This replaces reserves, risk, latency, compatibility, memory deficits, etc.

$\partial_t C_{\text{sys}} = 0$ is the sole identity condition. Hence, **identity is the conservation of coherence budget combined with the persistence of coherence geometry.**

Finally, coherence is not something the organism “has.” **The organism *is* the coherence field.** All of its parts, functions, memories, organs, and actions are geometric features of that field.

Organs are coherence basins. Graph is flux-induced adjacency. Memory is low-frequency coherence modes. Fast fields are high-frequency coherence modes. Policy is flux response law. Spark is the crossing an unstable point of the coherence potential. Reproduction is splitting of a coherence basin. Pruning is the collapse of a basin. Space is support of $C$. Time is evolution of coherence. Dynamics is variational flow of coherence. Geometry is curvature induced by $C$.

Coherence is not a quantity evolving *within* space and time. It is the generative substance *from which* space and time arise.

**Life is the dynamics of a conserved coherence field whose geometry generates its own space, structure, behavior, and identity.**

---

## Bibliography

- **Batchelor, G. K.** (2000). _An Introduction to Fluid Dynamics_. Cambridge University Press.
- **Evans, L. C.** (2010). _Partial Differential Equations_ (2nd ed.). American Mathematical Society.
- **Guckenheimer, J., & Holmes, P.** (1983). _Nonlinear Oscillations, Dynamical Systems, and Bifurcations of Vector Fields_. Springer.
- **Hirsch, M. W., Smale, S., & Devaney, R. L.** (2013). _Differential Equations, Dynamical Systems, and an Introduction to Chaos_ (3rd ed.). Academic Press.
- **Newman, M. E. J.** (2018). _Networks_ (2nd ed.). Oxford University Press.
- **Strogatz, S. H.** (2015). _Nonlinear Dynamics and Chaos_ (2nd ed.). CRC Press.
- **Susskind, L., & Friedman, A.** (2017). *Special Relativity and Classical Field Theory: The Theoretical Minimum*. Basic Books. **ISBN:** 978-0465093342
- **Susskind, L., & Friedman, A.** (2023). *General Relativity: The Theoretical Minimum*. Basic Books. **ISBN:** 978-1541602104
- **Jovanovic, U.** (2025). *Reflexive Organism Model*.
- **Jovanovic, U.** (2025). *Seeds of life*
- **Jovanovic, U.** (2025). *Coherence in Reflexive Organism Model*

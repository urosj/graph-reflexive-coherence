# Fractal Reflexive Coherence

Copyright © 2025 Uroš Jovanovič, CC BY-SA 4.0.

## Abstract

We present Fractal Reflexive Coherence (FRC), an extension of the Reflexive Coherence (RC) framework that resolves a central limitation shared by single-field and two-field RC, the inability to propagate identity across scales. While classical RC describes a single reflexive loop whose geometry is shaped by a coherence field $C(x,t),$ this structure cannot reproduce the hierarchical, self-similar patterns seen in biological, cognitive, and collective systems. We introduce a generation coordinate $\sigma\in[0,\infty)$ and promote coherence to a scale-resolved density $C(x,t;\sigma)$ on the product manifold $\Omega_t\times[0,\infty)$. The resulting position-scale continuity equation couples spatial transport to a scale-flux $J^\sigma$ that governs branching in a mass-preserving cascade. Coherence from all scales contributes to the effective geometry through an integrated coherence tensor $K_{\mu\nu}(x,t)=\int_0^\infty K_{\mu\nu}(x,t;\sigma) d\sigma,$ allowing fine-grained sub-identities to curve and constrain the large-scale dynamics. We show that this system admits stable, invariant multiscale identity basins, attractor tubes in $(x,\sigma)$ that persist under perturbations and encode hierarchical, fractal self-organization. The FRC formulation thus provides a mathematically coherent mechanism for the emergence of nested identities, scale-free geometry, and fractal patterns, completing the progression from single-loop reflexivity to an infinitely cascading hierarchy of reflexive loops.

## Separation

What happens if we "separate" an identity? Let's define a second scalar that lives on the same spacetime manifold but is associated with the environment

$$
C_{\text{tot}}(x,t)=C(x,t)+C_{E}(x,t) .
$$

The total coherence functional then becomes

$$
\begin{aligned}
\mathcal P_{\text{tot}}[C,C_E]=\int \Big[\frac{\kappa_C}{2}\nabla_\mu C\nabla^\mu C +\frac{\kappa_E}{2}\nabla_\mu C_E\nabla^\mu C_E - V(C) \\
-V_E(C_E) - \underbrace{U_{\text{int}}(C,C_E)}_{\text{mutual coupling}}\Big]\sqrt{-g[C,C_E]}d^4x .
\end{aligned}
$$

Here, interaction potential $U_{\text{int}}(C,C_E)$ directly couples the organism’s coherence to that of its surroundings. The variation $\delta U/\delta C$ is a *force* exerted by the whole on the self, while $\delta U/\delta C_E$ is the reciprocal back-reaction. The geometry, defined by joint metric $g_{\mu\nu}[K[C,C_E]]$ now depends on both fields, the space is shaped not only by its own gradients but also by the environmental gradients.

We still require, that the global invariance $\frac{d}{dt}\!\int_{\Omega}C_{\text{tot}}\,dV_g=0$ holds, hence increase of agent's coherence must be compensated elsewhere in the environment.

Let's now apply the change to the coherence tensor. The current definition

$$
K_{\mu\nu}= \lambda_C C\,g_{\mu\nu} + \xi_C \nabla_\mu C \nabla_\nu C + \zeta_C j_\mu j_\nu, \qquad j_\mu = C v_{C,\mu},
$$

already mixes a *density term*, a *gradient term* and a *flux term*. To let the environment speak directly to the geometry, we need to add cross-terms that involve both $C$ and $C_E$

$$
K_{\mu\nu}\to K_{\mu\nu}^{\text{(ext)}}=
\underbrace{\lambda_{CE} C C_E g_{\mu\nu}}_{\text{mixed density}}
+\underbrace{\xi_{CE}\nabla_\mu C\nabla_\nu C_E}_{\text{mixed gradient}}
+\underbrace{\zeta_{CE}(j_\mu j_{E,\nu}+j_{E,\mu}j_\nu)}_{\text{mixed flux}} .
$$

The mixed density term makes the *local curvature* proportional to the product of agent's and environmental coherence. Where both are high, space “tightens” and where one is low, it “loosens”.  The mixed gradient couples directional changes. A steep personal gradient in a region of strong environmental coherence will produce an anisotropic stretching that feels like the environment *guiding* the organism’s attention. The mixed flux term encodes *co-movement*. If the environment carries a coherent flow (e.g., a cultural wave), the organism can hitch onto it, and vice-versa.

These additions preserve the tensorial nature of $K_{\mu\nu}$ and therefore keep the whole formalism covariant. They also make the metric explicitly *environment-dependent*

$$
g_{\mu\nu}=g_{\mu\nu}[K^{\text{(ext)}}] .
$$

Thus, *the geometry that determines agent's shape is now a joint product of the agent and the whole*.

Let's now make one more change that is more in line with the separation.  For a relational system we may want to allow *exchange* with an external reservoir while still enforcing an overall **balance**

$$
\frac{d}{dt}\int_{\Omega} C dV_g = \Phi_{\text{in}} - \Phi_{\text{out}} .
$$

Here $\Phi_{\text{in}}$ and $\Phi_{\text{out}}$ are *coherence fluxes* through the boundary of $\Omega$, possibly expressed as surface integrals of a coherence current that includes contributions from $C_E$. The balance law captures two crucial ideas. The whole can give coherence (e.g., learning, nourishment) - $\Phi_{\text{in}}>0$, and the agent can return coherence to the whole (e.g., creative work, ecological impact) - $\Phi_{\text{out}}>0$.

When $\Phi_{\text{in}}=\Phi_{\text{out}}$ we recover strict conservation, otherwise we have a *net growth* or *decay* that reflects genuine co-evolution.

With these additions, the geometry is no longer a function of a single field alone. Instead it becomes a joint functional $g_{\mu\nu}[C,C_E]$ whose values are determined by the *entire coherence landscape*.

Let us write the two fields explicitly. We have agent (part) coherence$C_A(x,t)$ with flux $J_A^\mu=C_A v_A^\mu$.  And we have environment (whole) coherence $C_E(x,t)$ with flux $J_E^\mu=C_E v_E^\mu .$

The original reflexive coherence (RC) model imposes a *single* global invariant

$$
\frac{d}{dt} C_{\text{sys}}(t)=0,\qquad 
C_{\text{sys}}(t):=\int_{\Omega_t}\bigl[C_A(x,t)+C_E(x,t)\bigr] dV_g .
$$

If we write a local continuity equation for each field *without* any cross-terms,

$$
\partial_t C_A+\nabla_\mu J_A^\mu =0, \qquad
\partial_t C_E+\nabla_\mu J_E^\mu =0,
$$

then adding these two gives exactly the global invariant.  Consequently the two equations are *decoupled* except for the trivial statement that their sum is conserved.   

In this situation the “part” and the “whole’’ live in parallel worlds. Each obeys its own reflexive loop, but there is no *information exchange* between them.  The only coupling left is the global constraint, which merely tells us that whatever coherence disappears from one field must appear somewhere else in the same total integral.  

This is equivalent to a single-field theory with an internal label

$$
C(x,t)=\bigl(C_A(x,t),\,C_E(x,t)\bigr) .
$$

However, we can show that the proposed strict conservation law blocks genuine cooperation. Let's assume that the dynamics of each field is generated by an action functional that depends only on the field itself and its first derivatives (no mixed terms)  

$$
S[C_A,C_E]=\int{\cal L}_A(C_A,\nabla C_A)d^4x +\int{\cal L}_E(C_E,\nabla C_E)d^4x .
$$

The second assumption is that time-translation invariance holds for the *total* action (the usual Noether hypothesis). 

Noether’s theorem then yields a conserved current

$$
\partial_t \bigl( {\cal H}_A+{\cal H}_E\bigr)+\nabla_\mu\bigl({\cal S}^\mu_A+{\cal S}^\mu_E\bigr)=0,
$$

where ${\cal H}$ are the Hamiltonian densities (the “energy-like” quantities).  If we identify the conserved quantity with the *coherence* integral, then the only way for conserved currents to reduce exactly to local continuity for the two fields, is that each field’s contribution to the Noether current be separately divergence-free

$$
\partial_t {\cal H}_A+\nabla_\mu{\cal S}^\mu_A=0,\qquad
\partial_t {\cal H}_E+\nabla_\mu{\cal S}^\mu_E=0 .
$$

This equation is precisely the statement that each sector possesses its own conserved charge.  Hence, under the two assumptions a *global* conservation law inevitably collapses into two independent local conservations.  The “whole” never exerts any dynamical influence on the “part”, and vice-versa. Hence, this extension can still be reduced to one field with one loop.

## Participation

In order to address this limitation, let's look at a minimal extension that restores genuine cooperation.

Let's introduce a **mutual exchange density** $S(x,t)$ (units of coherence per unit time).  The local balances become

$$
\begin{aligned}
\partial_t C_A+\nabla_\mu J_A^\mu &= S ,\\
\partial_t C_E+\nabla_\mu J_E^\mu &= -S .
\end{aligned}
$$

A positive $S$ means the environment donates coherence to the agent, while a negative $S$ means the opposite.  The two equations are now *coupled*. They cannot be solved independently.

Adding the two yields

$$
\partial_t(C_A+C_E)+\nabla_\mu(J_A^\mu+J_E^\mu)=0,
$$

so total coherence is still conserved, but the *distribution* between part and whole can change dynamically, information flows through $S$.

We can now add a bilinear contribution to the action functional $S[C_A,C_E]$ (the mixed Lagrangian)

$$
\Delta S = \int \Bigl[\xi_{AE}\nabla_\mu C_A\nabla^\mu C_E +\zeta_{AE} J_A^\mu J_{E,\mu} +\lambda_{AE} C_A C_E\Bigr] \sqrt{-g}d^4x .
$$

Varying with respect to $C_A$ (and similarly for $C_E$) produces precisely the exchange term $S$.  Thus the exchange it follows from a well-defined variational principle and the two sectors cannot be reduced to one effective field without loss of information.

**Lemma:** If $\xi_{AE}\neq0$ or $\zeta_{AE}\neq0$ or $\lambda_{AE}\neq0$, then the Euler-Lagrange equations for $C_A$ and $C_E$ are *linearly independent* functional differential equations.

**Proof:** The variation of $\Delta S$ with respect to $C_A$ yields

$$
\delta_{C_A}\Delta S = \int \Bigl[\xi_{AE}\nabla_\mu C_E\nabla^\mu(\delta C_A) + \zeta_{AE} J_E^\mu v_{A,\mu} \delta C_A + \lambda_{AE} C_E \delta C_A \Bigr]\sqrt{-g} d^4x .
$$

Integrating the first term by parts gives a contribution proportional to $\Box C_E$.  The resulting Euler-Lagrange equation for $C_A$ contains terms that involve only $C_E$** (and its derivatives) multiplied by non-zero constants $\xi_{AE},\zeta_{AE},\lambda_{AE}$.  

If we attempted to write a single field equation $F(C_{\rm eff})=0$ with $C_{\rm eff}=f(C_A,C_E)$, the dependence on $\Box C_E$ would have to be expressible solely in terms of $C_{\rm eff}$ and its derivatives.  Because the coefficients $\xi_{AE},\zeta_{AE},\lambda_{AE}$ are independent parameters, no universal function $f$ can eliminate **all** cross-terms simultaneously unless those coefficients vanish.

Hence, when at least one mixed coupling constant is non-zero, the system possesses *two* dynamical degrees of freedom that cannot be collapsed into a single effective reflexive loop without discarding part of the dynamics (i.e., the information carried by the exchange terms). Thus the extended model genuinely captures cooperation rather than mere relabelling.

The following is a summary, a compact representation of the extension that deals with the separation of agent and the environment

$$
\begin{aligned}
S[C_A,C_E] &= \int{\cal L}_A(C_A,\nabla C_A) + {\cal L}_E(C_E,\nabla C_E) + \Delta{\cal L}(C_A,C_E,\nabla C_A,\nabla C_E,J_A,J_E) d^4x,\\
\mathcal{L}_{A} &= \frac{\kappa_A}{2}\nabla_\mu C_A\nabla^\mu C_A - V_A(C_A),\\
\mathcal{L}_{E} &= \frac{\kappa_E}{2}\nabla_\mu C_E\nabla^\mu C_E - V_E(C_E),\\
\Delta{\cal L} &= \xi_{AE}\nabla_\mu C_A\nabla^\mu C_E +\zeta_{AE} J_A^\mu J_{E,\mu} + \lambda_{AE} C_A C_E ,\\
\partial_t C_A+\nabla_\mu J_A^\mu &= S(C_A,C_E),\\
\partial_t C_E+\nabla_\mu J_E^\mu &= -S(C_A,C_E),\\
S(C_A,C_E) &= \alpha(C_E-C_A)
            -\beta\bigl(v_E^\mu-v_A^\mu\bigr)\nabla_\mu C_A .
\end{aligned}
$$

The original reflexive coherence model already hinted at a deep symmetry between an agent and the environment. Both are encoded in the same scalar field that also builds its own geometry.  By splitting the field but re-coupling them through exchange terms derived from a shared action, we obtain a mathematically consistent picture where the *whole* defines the *shape* of experience (through the metric $g_{\mu\nu}[K(C_A,C_E)]$), the *part* contributes to the evolution of that shape by donating and receiving coherence and global conservation is retained, but local autonomy is relinquished.

In this sense the theory becomes truly “unified” rather than merely “two copies of the same reflexive loop”.  The resulting dynamics are computationally irreducible, but we gain a principled, variational framework for studying how *participation* can be mathematically expressed and empirically tested.

## Cascading

So far, we've shown how to generate more than one loop yet still preserve the invariants and the dynamics of the original one-field system. However, the method is more exploratory and experimental than practical. First, we've only dealt with one agent. Extending to arbitrary number of agents would become unpractical. However, it is not just finding a more elegant solution to describe more complex behavior of arbitrary number of agents as well as relations between the agents themselves. It's something much more intrinsic.

What we can observe around us is not only the repetition of the same types of agents, organisms, but the repetition of principles, patterns across scales, hierarchies of structures that share same patterns of behavior. And our simple approach of splitting and participation does not provide the answer. 

In other words, coherence is not merely redistributed within one field or exchanged between two fields. It propagates across scales in a cascading hierarchy of reflexive loops.

And proposed two-field model cannot produce an infinite cascade, because in the coupled system

$$
\partial_t C_A+\nabla_\mu J_A^\mu = S(C_A,C_E),\qquad
\partial_t C_E+\nabla_\mu J_E^\mu =-S(C_A,C_E),
$$

the source term $S$ merely transfers coherence between *two* subsystems. Even if we let the interaction be nonlinear, there are only two dynamical degrees of freedom. After each “splitting” event one can at most label the daughters as “A’’ and “E’’.  No further subdivision is possible without introducing a new field.

Consequently the model can describe one identity that exchanges coherence with an environment, but it cannot generate a *fractal* family $\{C_i\}_{i=1}^{\infty}$ where each member may in turn split into two (or many) children ad infinitum.  To capture that, we need something else, for example a continuous index that keeps track of the *generation/scale* of every sub-identity.

Let's propose a more expressive model that addressed these limitations. We'll start with an introduction of a **scale (or generation) label** $\sigma\in[0,\infty)$.  The full state is now a *measure-valued field*

$$
C(x,t;\sigma)\ge0 ,\qquad (x\in\Omega_t\subset\mathbb R^{3}), 
$$

where $\sigma=0$ denotes the **root identity** (the “whole’’ you start with) and increasing $\sigma$ corresponds to finer-grained sub-identities.

The *total coherence* of the whole hierarchy is defined as a double integral

$$
C_{\text{tot}}(t) := \int_{0}^{\infty} d\sigma \int_{\Omega_t} C(x,t;\sigma) dV_g .
$$

The global invariance we require is  

$$
\frac{d}{dt}C_{\text{tot}}(t)=0 .
$$

Let's now define the continuity equation on the product space $\Omega\times[0,\infty).$ We postulate a *local* conservation law that includes a **scale-flux** $J_\sigma^\mu$ (the analogue of the spatial flux $J_x^\mu=C v_C^\mu$).  In covariant notation ($\mu=0,1,2,3,\ 5$ with the extra index "$5$" for $\sigma$) we write

$$
\partial_t C +\nabla_i J^i +\partial_\sigma J^\sigma = 0, \qquad i=1,2,3 .
$$

where $J^i(x,t;\sigma)=C\,v_C^{\,i}$ is the usual spatial coherence flux and $J^\sigma(x,t;\sigma)$ governs **branching** (movement in scale).

This equation is a *continuity equation on the 4-dimensional space $(x,\sigma)$*; it guarantees that any loss of coherence at one scale must appear either as spatial transport or as transfer to another scale.

Assume no flux through the outer boundaries

$$
J^i n_i\Big|_{\partial\Omega}=0, \qquad 
J^\sigma\Big|_{\sigma=0}=J^\sigma\Big|_{\sigma\to\infty}=0 .
$$

Integrating covariant notation over all $x$ and $\sigma$ and using these boundaries gives

$$
\frac{d}{dt}C_{\text{tot}}(t)= -\int d\sigma\int_{\partial\Omega} J^i n_i dS -\Big[ J^\sigma\Big]_{0}^{\infty}=0 .
$$

Thus global invariance $\frac{d}{dt}C_{\text{tot}}(t)=0$ follows automatically, the total coherence is a strict constant of motion, no matter how many times the cascade splits.

Let's make things a bit more grounded and look at a concrete branching rule, the multiplicative cascade. To make $\partial_t C +\nabla_i J^i +\partial_\sigma J^\sigma = 0$ operative we need an explicit expression for $J^\sigma$. A simple deterministic choice that reproduces the classic *binary multiplicative cascade* is

$$
J^\sigma(x,t;\sigma)= -\,\kappa_\sigma \,
\partial_\sigma C(x,t;\sigma)
+ B\bigl[C(x,t;\sigma)\bigr],
$$

where  $\kappa_\sigma>0$ is a **scale-diffusion** coefficient (smoothes the distribution over generations) and $B[\cdot]$ is a **branching source** that pushes coherence from scale $\sigma$ to the next finer scale $\sigma+\Delta\sigma$.

A convenient discrete version (binary splitting with random weights) reads

$$
C(x,t;\sigma+\Delta\sigma)= w_1(\sigma) C(x,t;\sigma) + w_2(\sigma) C(x,t;\sigma), \qquad w_1+w_2=1 .
$$

In the continuum limit $\Delta\sigma\to0$ this becomes

$$
\partial_\sigma C = - \frac{1}{\Delta\sigma} \bigl[ C(x,t;\sigma)- (w_1+w_2)C(x,t;\sigma)\bigr] = 0 ,
$$

i.e. **no net loss of mass** because the weights sum to one.  Hence the *local* branching operator satisfies

$$
\int_{0}^{\infty} d\sigma\partial_\sigma J^\sigma =0 .
$$

We now have an example for a **mass-conserving cascade**. Each parent identity hands down *all* of its coherence to its children, possibly redistributed unevenly.

Let's look at **fractal statistics** now. We define the *$q$-th moment* of the coarse-grained field at scale $\ell=2^{-\sigma}$

$$
M_q(\ell)=\int_{\Omega} \bigl\langle C(x,t;\sigma)^q\bigr\rangle dV_g .
$$

For a binary multiplicative cascade with i.i.d. weights $w$ the classic result is

$$
M_q(\ell) \propto \ell^{\tau(q)}, \qquad \tau(q)= -\log_2\bigl\langle w^q+(1-w)^q\bigr\rangle .
$$

The **multifractal spectrum** $f(\alpha)$ follows from the Legendre transform of $\tau(q)$.  The existence of a non-linear $\tau(q)$ is precisely what makes the hierarchy *fractal*, different moments scale with different exponents.

Thus, by embedding the cascade in the RC continuity equation, **fractality becomes an intrinsic dynamical property** rather than an ad-hoc statistical description.

What about geometry that is generated by a fractal hierarchy? Recall that in the original RC model the *effective metric* is built from the **coherence tensor**

$$
K_{\mu\nu}(x,t)= \lambda_C C g_{\mu\nu} +\xi_C \nabla_\mu C \nabla_\nu C
+\zeta_C J_\mu J_\nu .
$$

When we have a whole hierarchy, the natural generalisation is to **superpose** the contributions of every scale

$$
K_{\mu\nu}(x,t)= \int_{0}^{\infty} d\sigma\, \Bigl[\,\lambda(\sigma) C(x,t;\sigma) g_{\mu\nu} + \xi(\sigma) \nabla_\mu C \nabla_\nu C
+\zeta(\sigma) J_\mu J_\nu\Bigr] .
$$

The metric is then defined as before

$$
g_{\mu\nu}=g_{\mu\nu}[K] , \qquad  dV_g=\sqrt{-\det g} d^4x .
$$

Because the integral contains *all* generations, **large-scale geometry** feels a weighted average of fine-grained sub-identities.  In particular if the weight functions $\lambda(\sigma),\xi(\sigma),\zeta(\sigma)$ decay as power laws, $\lambda(\sigma)\sim e^{-\alpha\sigma},\quad \xi(\sigma)\sim e^{-\beta\sigma},\dots ,$ the metric acquires *scale-free* contributions, which is precisely what a fractal object does to its surrounding geometry. The **self-similarity** of the cascade $M_q(\ell)$ translates into an invariance of $g_{\mu\nu}$ under the combined rescaling

$$
x\to \ell x,\qquad t\to \ell^{z}t,\qquad \sigma\to\sigma-\log_2\ell,
$$

provided the coupling constants transform accordingly (e.g. $\lambda(\sigma)\to \ell^{d}\lambda(\sigma-\log_2\ell)$).  This is a *renormalisation-group* symmetry of the whole RC system.

Hence, **the fractal hierarchy directly sculpts the organism’s internal geometry**, fulfilling the aim that “identities are spawned and divide into infinity while still preserving the global coherence invariant”.

### Proof of global conservation for an infinite cascade  

We now give a compact proof that $\partial_t C +\nabla_i J^i +\partial_\sigma J^\sigma = 0$ together with the *mass-preserving* branching rule guarantees the global invariance **for any number of generations**, even an uncountable continuum.

**Lemma 1 (local scale balance):** For every $(x,t)$ let the branching operator satisfy

$$
\int_{0}^{\infty} d\sigma \partial_\sigma J^\sigma(x,t;\sigma)=0 .
$$

*Proof.* By definition $J^\sigma$ is a flux in scale space.  The only way coherence can disappear from the hierarchy is if it leaves through the *boundaries* $\sigma=0$ or $\sigma\to\infty$.  Imposing the no-flux conditions gives exactly the integral above.

**Lemma 2 (spatial flux balance):** Assuming the usual no-through-boundary condition on $\partial\Omega$,

$$
\int_{\Omega} \nabla_i J^i dV_g =0 .
$$

*Proof.* Straightforward application of Gauss’ theorem with $J^i n_i|_{\partial\Omega}=0$.

**Theorem (global coherence invariance):** If the field $C(x,t;\sigma)$ obeys the continuity equation together with Lemmas 1-2, then

$$
\frac{d}{dt} C_{\text{tot}}(t)=0 .
$$

*Proof.* We first integrate $\partial_t C +\nabla_i J^i +\partial_\sigma J^\sigma = 0$  over $\Omega\times[0,\infty)$

$$
\int_0^\infty d\sigma \int_\Omega \bigl[\partial_t C + \nabla_i J^i + \partial_\sigma J^\sigma\bigr] dV_g =0 .
$$

Let's now swap integration and time derivative

$$
\frac{d}{dt}\underbrace{\int_0^\infty d\sigma \int_\Omega C}_{C_{\text{tot}}} + \underbrace{\int_0^\infty d\sigma \int_\Omega \nabla_i J^i}_{=0\ \text{by Lemma 2}} + \underbrace{\int_\Omega\Bigl[J^\sigma\Bigr]_{0}^{\infty}}_{=0\ \text{by Lemma 1}} =0 .
$$

Thus $\dot C_{\text{tot}}=0$.

The theorem holds independently of how many splitting events actually occur, because the balance is built into the *local* equation $\partial_t C +\nabla_i J^i +\partial_\sigma J^\sigma = 0,$ $i=1,2,3 .$  Hence an *infinite* binary tree of identities can be generated without ever violating global coherence.

## Fractal reflexive coherence

**Fractal Reflexive Coherence (FRC)** is a reflexive coherence system defined on the product space $\mathcal M = \Omega_t\times[0,\infty)_\sigma$, represented by a non-negative density $C(x,t;\sigma)$ satisfying the position-scale continuity equation

$$
\partial_t C + \nabla_i J^i + \partial_\sigma J^\sigma = 0 , \quad i=1,2,3,
$$

with spatial flux $J^i=C v_C^{i}$ and boundary conditions $J^i n_i|_{\partial\Omega}=0$, $J^\sigma|_{\sigma=0}=J^\sigma|_{\sigma\to\infty}=0$, ensuring conservation of the global invariant

$$
C_{\rm tot}(t) = \int_0^\infty d\sigma \int_{\Omega_t} C(x,t;\sigma) dV_g.
$$

The scale flux

$$
J^\sigma = -\kappa_\sigma\partial_\sigma C + B[C]
$$
 
 implements branching, transferring coherence between generations while preserving total coherence. Each scale $\sigma$ contributes a coherence tensor

$$
K_{\mu\nu}(x,t;\sigma) = \lambda(\sigma) C g_{\mu\nu} + \xi(\sigma)\nabla_\mu C\nabla_\nu C + \zeta(\sigma) J_\mu J_\nu,
$$

and the full tensor of the organism is the scale-integral

$$
K_{\mu\nu}(x,t) = \int_0^\infty K_{\mu\nu}(x,t;\sigma) d\sigma,
$$

which defines the induced metric $g_{\mu\nu}[K]$.

Note that the full coherence functional on the position-scale manifold is

$$
\mathcal P[C]=\int_0^\infty d\sigma \int_\Omega\Big(\tfrac{\kappa_C}{2}\nabla_\mu C\nabla^\mu C -V(C)\Big) \sqrt{-g[K]} d^4x .
$$

Varying with respect to $C(x,t;\sigma)$ yields the functional derivative $\Phi_C = \delta\mathcal P/\delta C$, which plays the role of a coherence “potential”. Together with the constitutive laws for the spatial and scale fluxes $J^i[C,\Phi_C]$ and $J^\sigma[C,\Phi_C]$, this potential enters the continuity equation

$$
\partial_t C + \nabla_i J^i + \partial_\sigma J^\sigma = 0,
$$

so that the FRC dynamics can be viewed as a generalized gradient flow generated by $\mathcal P[C]$.

An FRC system therefore consists of an infinite cascade of reflexive loops coupled across scales, each contributing to a unified geometry, while the total coherence of the hierarchy remains strictly conserved.

A more detailed form of $\mathcal P$, including explicit scale-gradient and branching terms, is given in Appendix C. Appendix E proposes a fully deterministic branching operator $B[C]$ based on reflexivity alone.

## The loop

In the ordinary reflexive coherence theory the *only* dynamical variable is the scalar density $C(x,t)$. There is a single closed feedback chain

$$
C \xrightarrow{K[C]} g_{\mu\nu}[K] \xrightarrow{\nabla,dV_g} 
J_C^\mu=Cv_C^\mu \xrightarrow{\partial_t C+\nabla\cdot J=0}
\text{updates }C .
$$

Because there is only one field, the loop closes on itself. The *geometry* that governs transport is built from the same coherence that is being transported. 

How about in the fractal definition? If we *freeze* a particular value of $\sigma$ and look only at that slice, the equations reduce to exactly the same pattern

$$
C_\sigma \xrightarrow{K[C_\sigma]} g_{\mu\nu}[K] \xrightarrow{\nabla,dV_g} J_C^\mu(\sigma) \xrightarrow{\partial_t C_\sigma+\nabla\cdot J_C(\sigma)= -\partial_\sigma J^\sigma}
\text{updates }C_\sigma .
$$

Thus each $\sigma$-slice possesses its own reflexive loop. The right-hand side of the continuity equation contains $-\partial_\sigma J^\sigma$, which is *exactly* the term that couples slice $\sigma$ to its neighbours $(\sigma\pm\Delta\sigma)$.  Consequently the scale-flux $J^\sigma$ (or its divergence $-\partial_\sigma J^\sigma$) injects coherence *into* slice $\sigma$ from the coarser slice and extracts it *toward* finer slices. It also follows, that while in most implementations we define the metric as an integral over all scales, e.g. $K_{\mu\nu}(x,t)=\int_0^\infty d\sigma\bigl[\lambda(\sigma)C_\sigma g_{\mu\nu}+ \dots\bigr]$, all slices see the same geometry, which itself is a *collective* of all loops. One important distinction is that only the sum over $\sigma$ is conserved with $C_{\rm tot}(t)=\int_0^\infty d\sigma\!\int_\Omega C(x,t;\sigma)\,dV_g=\text{const.}$  Individual slices can gain or lose coherence, but the total never changes.

## Identity basins across scales

In the standard RC formulation, an identity is defined as a stable, self-maintaining attractor basin of the coherence dynamics in physical space. In the fractal extension, identities persist not only in spatial regions $A \subset \Omega_t$ but across **bands of the scale coordinate**. 

Let $C_\sigma(x,t) := C(x,t;\sigma)$ denote the slice at scale $\sigma$. For each such slice, the reflexive cycle

$$
C_\sigma \to K[C_\sigma] \to g_{\mu\nu} \to J_C^\mu(\sigma)
\to \partial_t C_\sigma + \nabla_i J^i(\sigma)
= -\partial_\sigma J^\sigma
$$

defines a dynamical flow in $(x,t)$ whose fixed structures depend on the inter-scale coupling term $-\partial_\sigma J^\sigma$.

Given this extension, let's make a generlized definition, a scale-resolved identity basin. A subset

$$
A_{\Sigma} \subset \Omega_t \times \Sigma, \qquad \Sigma \subset [0,\infty)
$$

is called a **scale-resolved identity basin** if it satisfies the following requirements.

**1. Spatial-scale stability.** There exists $(x^{*}, \sigma^{*}) \in A_\Sigma$ such that 

$$
\nabla_{x} C(x^{*},t;\sigma^{*}) = 0, \qquad
\partial_{\sigma} C(x^{*},t;\sigma^{*}) = 0,
$$

and the combined Hessian in $(x,\sigma)$ $\mathrm{Hess}_{(x,\sigma)} C$ is positive definite on $A_\Sigma$. This ensures a joint curvature minimum in both space and scale.

**2. Spatial-scale attractivity.** There exists a neighborhood $U \subset \Omega_t\times\Sigma$ such that trajectories of the position-scale flow $\Phi_t(x,\sigma)$ obey $\Phi_t(x_0,\sigma_0) \to A_\Sigma\ (t\to\infty)$ 
for all $(x_0,\sigma_0)\in U$. Thus the basin attracts coherence both horizontally (in space) and vertically (in scale).

**3. Invariance under the FRC dynamics.** Once coherence enters $A_\Sigma$ it holds $\Phi_t(A_\Sigma) = A_\Sigma$ for all future times, even though individual slices $\sigma$ may gain or lose coherence due to $-\partial_\sigma J^\sigma$. The identity persists as a scale-extended invariant mode.

**4. Reflexive closure across scales.** Coherence arriving at scale $\sigma$ within $A_\Sigma$ contributes to the geometry that subsequently governs all neighbor slices $\sigma\pm \Delta\sigma$. Thus the curvature reinforcement property of RC now applies along the $\sigma$ direction as well

$$
J^\sigma \to A_\Sigma
\quad \Longrightarrow \quad
\partial_\sigma C|*{A*\Sigma} \to 0
\quad\text{and the basin deepens in scale}.
$$

Repeated collapses into any slice of the basin stabilize not just a spatial identity but an entire hierarchical lineage across multiple generations.

With this definition , a scale-resolved identity is no longer just a point attractor in space but a tube-like attractor that threads through the $\sigma$-dimension, a “fractal line of descent”. Identity becomes a multiscale invariant, preserved not only under spatial reflexive cycles but also under branching and inter-generation transfer.

This matches the observed phenomenology. Real organisms preserve identity through nested structures (molecules → organelles → cells → tissues → organisms), each stabilized by reflexive coherence at its own scale and coupled to its neighbors.

---

## Appendix A: Binary cascade on a line  

Let's take a one-dimensional domain $[0,1]$ and start with uniform coherence $C_0(x)=1$ at $\sigma$=0. At each generation, we split every interval into two equal halves and then assign random weights $w\sim\text{Beta}(\alpha,\beta)$. The left half receives weight $w$, the right half $1-w$.  

After $n$ generations $(\sigma=n\Delta\sigma)$ the coherence on a sub-interval of length $\ell=2^{-n}$ is

$$
C_n(x)=\prod_{k=1}^{n} w_k^{\epsilon_k} (1-w_k)^{1-\epsilon_k},
\qquad \epsilon_k\in\{0,1\}\ \text{depending on left/right choice}.
$$

The moments are

$$
\langle C_n^q\rangle = \bigl\langle w^q+(1-w)^q\bigr\rangle^{n} = \ell^{-\tau(q)}, \quad \tau(q)=-\log_2\bigl\langle w^q+(1-w)^q\bigr\rangle .
$$

For $\alpha=\beta=0.5$ (the classic “uniform” cascade) one finds a concave $\tau(q)$, i.e. a multifractal spectrum with Hausdorff dimension $D_H\approx 0.63$.  

If we now compute the metric contribution $K_{\mu\nu}(x,t)$ using this $C_n$, the effective distance between two points will depend on how many cascade levels separate them, a hallmark of *fractal geometry*.

## Appendix B: Arity of branching

Although we've used binary branching, the branching operator $B[C]$ can split a parent identity into any number $N\ge2$ of children (triplets, nine-fold, etc.).  The only hard requirement is mass conservation. The weights that distribute coherence among the children must sum to unity.  All the formal machinery such as the extra scale coordinate $\sigma$, the continuity equation with a scale-flux term $\partial_\sigma J^\sigma$, and the resulting multifractal statistics, works for arbitrary arity. Binary splitting is merely the simplest illustrative example.

Hence, for an $N$-ary cascade we may write

$$
J^\sigma(x,t;\sigma) = - \kappa_\sigma\partial_\sigma C + B[C] (x,t;\sigma) ,
$$

with  

$$
B[C] = \sum_{a=1}^{N} w_a(\sigma) C\bigl(x,t;\sigma+\Delta\sigma\bigr)  - C(x,t;\sigma) .
$$

Here the weights $w_a(\sigma)\ge0$ describe how much of the parent’s coherence is handed to child  $a$. The *mass-conserving* condition is

$$
\sum_{a=1}^{N} w_a(\sigma)=1 .
$$

We can see that the structure of the equations does not change, only the explicit form of the branching operator (the sum over children) does.

Another property that changes with arbitrary arity is multifractal scaling. For a *deterministic* equal-split cascade ($w_a=1/N$ for all $a$) every moment scales linearly with the resolution and the hierarchy is not multifractal (the spectrum collapses to a single exponent). The interesting case is when the weights are random variables drawn independently at each branching event. 

Let's define the coarse-graining scale $\ell = L_0 N^{-\sigma}$ (so that one step in $\sigma$ reduces the physical length by a factor $1/N$).  The $q$-th moment of the field at that scale is

$$
M_q(\ell)=\int_{\Omega}\bigl\langle C(x,t;\sigma)^q\bigr\rangle dV_g .
$$

Repeating the derivation that leads to equation for binary splitting, one obtains the **generalised scaling exponent**

$$
M_q(\ell)\propto \ell^{\tau_N(q)}, \qquad \tau_N(q)= -\log_{N}\Bigl\langle\sum_{a=1}^{N} w_a^q\Bigr\rangle .
$$

For $N=2$ this reduces exactly to the binary formula. For $N=3,9,\dots$ the base of the logarithm changes accordingly, but the *shape* of $\tau_N(q)$ is still dictated by the statistics of the weight distribution.

The multifractal spectrum $f(\alpha)$ follows from the Legendre transform of $\tau_N(q)$ exactly as in the binary case. Non-linear $\tau_N(q)$ signals genuine fractality regardless of the arity.

The metric in FRC is built from the *integrated* coherence tensor,

$$
g_{\mu\nu}=g_{\mu\nu}\Bigl[\int_0^{\infty}K_{\mu\nu}[C(x,t;\sigma)]d\sigma\Bigr],
$$

so whatever cascade is choosen (binary, ternary, nine-fold) the resulting geometry inherits the scale-free power laws of the underlying measure.

## Appendix C: Variational Origin of Scale Flux

In the ordinary RC model, the spatial flux $J^i=C,v_C^{,i}$ follows from a constitutive relation for the velocity $v_C^{,i}$, itself determined by the Euler-Lagrange equation $\delta\mathcal{P}/\delta C=0$ of the coherence functional. For the fractal hierarchy, we require an analogous derivation for the **scale-flux** $J^\sigma$.

To this end, we extend the coherence functional to the product space $\Omega_t\times[0,\infty)$ by introducing a **scale-gradient term** and a **branching potential**

$$
\mathcal{P}[C] = \int_0^\infty d\sigma \int_{\Omega_t} \Big[\tfrac{\kappa_C}{2} \nabla_\mu C \nabla^\mu C + \tfrac{\kappa_\sigma}{2} (\partial_\sigma C)^2 - V(C) - U_{\mathrm{branch}}(C,\sigma) \Big] \sqrt{-g[K]} d^4 x .
$$

The term $\tfrac{\kappa_\sigma}{2}(\partial_\sigma C)^2$ penalizes rapid changes of coherence across scale. The potential $U_{\mathrm{branch}}(C,\sigma)$ encodes preferred branching rules or multiplicative structure. As in standard RC, the metric $g_{\mu\nu}$ depends on the integrated tensor $K_{\mu\nu}$, coupling all scales geometrically.

We now compute the variation of $\mathcal{P}$ with respect to $C(x,t;\sigma)$. The relevant terms are

$$
\delta\mathcal{P} = \int d\sigma \int_{\Omega_t} \Big[-\kappa_C \Box_g C - \kappa_\sigma\partial_\sigma^2 C + V'(C) + \partial_C U_{\mathrm{branch}} + K^{\mu\nu} \frac{\delta g_{\mu\nu}}{\delta C}
  \Big]\delta C dV_g .
$$

Stationarity $\delta\mathcal{P}/\delta C = 0$ yields the **Euler-Lagrange equation**

$$
-\kappa_C \Box_g C - \kappa_\sigma \partial_\sigma^2 C + V'(C) + \partial_C U_{\mathrm{branch}} + K^{\mu\nu} \frac{\delta g_{\mu\nu}}{\delta C}
  = 0 .
$$

Rewriting the $\sigma$-term as a divergence gives

$$
\kappa_\sigma \partial_\sigma^2 C = \partial_\sigma J^\sigma_{\mathrm{grad}}, \qquad J^\sigma_{\mathrm{grad}} := -\kappa_\sigma\partial_\sigma C .
$$

The remaining branching contribution $\partial_C U_{\mathrm{branch}}$ defines a complementary flux component

$$
\partial_\sigma J^\sigma_{\mathrm{branch}} := \partial_C U_{\mathrm{branch}} .
$$

Thus the **total scale-flux** is

$$
J^\sigma = J^\sigma_{\mathrm{grad}} + J^\sigma_{\mathrm{branch}}
= -\kappa_\sigma\partial_\sigma C + B[C] ,
$$

exactly the expression introduced earlier.

Hence the scale flux used in the FRC continuity equation is derived from the variational principle governing the extended coherence functional. This guarantees that the cascade respects the same action-based structure as ordinary RC and that branching is not an ad-hoc prescription but part of the reflexive loop itself.


## Appendix D: Existence of Multiscale Identity Basins in Fractal Reflexive Coherence

We now establish the existence of scale-resolved invariant structures (“multiscale identity basins”) in the FRC dynamics. The theorem shows that the addition of the scale coordinate $\sigma$ and the scale flux $J^\sigma$ does not destroy the attractor structure of reflexive coherence, but lifts it to the product manifold $\Omega_t\times[0,\infty)$.

**Theorem (Existence and Persistence of Multiscale Identity Basins):** Let $C(x,t;\sigma)$ be a solution of the FRC continuity equation 

$$
\partial_t C + \nabla_i J^i + \partial_\sigma J^\sigma = 0,
\qquad
J^i = C v_C^{,i},
\qquad
J^\sigma = -\kappa_\sigma \partial_\sigma C + B[C],
$$

on the product manifold $\mathcal M = \Omega_t \times [0,\infty)_\sigma$, with no-flux boundary conditions

$$
J^i n_i|*{\partial\Omega}=0,\qquad
J^\sigma|*{\sigma=0}=J^\sigma|_{\sigma\to\infty}=0.
$$

We assume the following properties.

**1. Local spatial stability.** For some $\sigma^*\in[0,\infty)$ the slice $C(\cdot,t;\sigma^*)$ possesses a nondegenerate local minimum $x^*\in\Omega_t$ with $\nabla_x C(x^*,t;\sigma^*)=0,$ $\mathrm{Hess}_x C(x^*,t;\sigma^*) \succ 0.$

**2. Local scale stability.** The scale-gradient term satisfies $\partial_\sigma C(x^*,t;\sigma^*) =0,$ $\partial_\sigma J^\sigma(x^*,t;\sigma^*) = +\lambda_\sigma,C(x^*,t;\sigma^*),$ with $\lambda_\sigma>0$. (Flux from neighboring scales reinforces the coherence minimum.)

**3. Uniform geometric bounds.** The induced metric $g_{\mu\nu}[K]$ and its inverse remain uniformly bounded on $\mathcal M$, and the curvature induced by $K_{\mu\nu}(x,t) = \int_0^\infty K_{\mu\nu}(x,t;\sigma) d\sigma$ varies smoothly with $\sigma$.

**4. Mass preservation in scale.** The branching operator obeys $\int_0^\infty \partial_\sigma J^\sigma d\sigma = 0,$ and the global invariant $C_{\rm tot}(t) = \int_0^\infty\int_{\Omega_t}C dV_g d\sigma$ is finite and conserved.

Then there exists a neighborhood $U \subset \Omega_t \times \Sigma,$ $\Sigma\equiv[\sigma^*-\varepsilon,\sigma^*+\varepsilon],$ and a compact set $A_\Sigma \subset U,$ such that:

**(i) Spatial-scale attractor.**  For all initial conditions $(x_0,\sigma_0)\in U$, $\Phi_t(x_0,\sigma_0)\longrightarrow A_\Sigma \quad (t\to+\infty),$ where $\Phi_t$ is the flow induced by the vector field $V = (v_C^{i} \dot{\sigma}),\quad \dot{\sigma} = J^\sigma/C.$

**(ii) Invariance.** Once reached, the basin is preserved $\Phi_t(A_\Sigma) = A_\Sigma,\quad \forall t\ge0.$

**(iii) Stability under perturbations.** For any sufficiently small perturbation $\delta C$ of the coherence field, respecting the global invariant and the no-flux boundaries, there exists a perturbed basin $A_\Sigma'$ with $d_{\mathrm{Haus}}(A_\Sigma,A_\Sigma') = \mathcal O(\|\delta C\|),$ i.e. the structure persists under small spatial and scale perturbations.

**(iv) Reflexive reinforcement.** Coherence flux into $A_\Sigma$ deepens the spatial-scale minimum $J^i \to A_\Sigma$ and $J^\sigma \to A_\Sigma \ \Longrightarrow\  \mathrm{Hess}_{(x,\sigma)} C|_{A_\Sigma}$ increases.

**(v) Existence of multiscale identity.** The set $A_\Sigma$ constitutes a scale-resolved identity basin, it is a stable, invariant, self-reinforcing attractor tube threading through the $\sigma$-dimension.

Let's consider a sketch of a proof.

**1. Local minimum in $(x,\sigma)$ .** Assumptions (1) and (2) imply that $(x^*,\sigma^*)$ is a nondegenerate minimum of $C$ on $\mathcal M$, since 

$$
\mathrm{Hess}_{(x,\sigma)}C =
\begin{pmatrix}
\mathrm{Hess}_x C & \ast \\
\ast & \partial_\sigma J^\sigma/C
\end{pmatrix}
\succ 0.
$$

**2. Invariant manifold.** Smoothness of the geometry and the flux fields implies that the flow $\Phi_t$ is $C^1$. Standard invariant manifold theorems (Hadamard-Perron type) guarantee the existence of a compact attracting neighborhood $A_\Sigma$ around the minimum.

**3. Attraction.** Dissipativity in $\sigma$ (from $-\kappa_\sigma\partial_\sigma C$) and gradient-flow structure in $x$ imply that trajectories converge to the minimum along both dimensions.

**4. Invariance.** No-flux boundary conditions and mass preservation ensure that the coherence cannot escape the neighborhood along $x$ or $\sigma$, so the basin remains invariant under the flow.

**5. Stability.** Small perturbations induce small changes in $C$ and hence in the minimum and its basin, yielding stability in the Hausdorff metric.

This completes the proof. 

The theorem guarantees that identity is not lost when the system is extended to infinite scale depth; and the cascade does not produce noise or unstructured diffusion; and coherent, self-maintaining identity modes appear as tubes in $(x,\sigma)$, not points; as well as these multiscale identities are stable under perturbations and collectively sculpt the geometry through the integrated tensor $K_{\mu\nu}$.

Thus the FRC model supports hierarchical, fractal identity structures in a mathematically rigorous sense.

## Appendix E: Determinism (no randomness)

In the text above, we used randomization to achieve fractal structures. However, RC and ROM never use randomness. Their dynamics are deterministic, variational, reflexive, and geometry-driven. But the multiplicative cascades we borrowed from classical multifractal theory *usually* rely on randomness in the branching weights $w_1,w_2$ to avoid trivial uniformity.

However, there are fully deterministic mechanisms for non-uniform fractal branching and RC already contains these mechanisms implicitly.

**1. Geometry-Induced Deterministic Asymmetry.** In classical multiplicative cascades, randomness is only used to break symmetry between children $C \to (w_1 C, w_2 C),$ and $w_1+w_2=1.$ But in **FRC**, geometry is never uniform. Every scale slice $\sigma$ lives in a metric $g_{\mu\nu}[K(\cdot,\sigma)]$ that varies across $x$. This means the branching operator can deterministically depend on local geometry $w_1(x,\sigma) = f\big(K_{\mu\nu}(x,t;\sigma)\big),$ $w_2(x,\sigma) = 1 - w_1(x,\sigma).$

Examples of deterministic asymmetries are 

- gradient-based branching: $w_1 = \frac{1}{1 + e^{-a,|\nabla C|}}, \quad w_2 = 1-w_1 ,$
- curvature-based branching: $w_1 = \frac{R(x,\sigma)}{R(x,\sigma)+1},\quad w_2=1-w_1,$ where (R) is scalar curvature of the induced metric,
- flux-driven branching: $w_i \propto |J^i|,\quad J^i = C v_C^{,i}.$

**2. Deterministic nonlinear branching operator (B[C])** (no randomness, nonlinearity creates multifractality). Instead of $B[C] = w_1 C + w_2 C,$ we can use a nonlinear local operator $B[C] = C^\alpha \quad (\alpha \neq 1).$ Or in differential form $J^\sigma = -\kappa_\sigma\partial_\sigma C + \gamma C^\alpha, \quad \alpha>1.$

This creates multiplicative distortions deterministically. Large values get amplified, small values shrink, and cascades become multifractal automatically. This mechanism is identical to how deterministic chaotic maps generate fractality (e.g., the logistic map).

**3. Deterministic transfer across $(x,\sigma)$** (fractals from transport, not local splitting). The fractal structure doesn’t need to originate at each splitting event. It can instead come from the combined effect of spatial flux $J^i$, scale flux $J^\sigma$, geometry $g_{\mu\nu}$, and  nonlinearities in $v_C^\mu$. FRC’s full continuity equation $\partial_t C + \nabla_i (C v_C^{i}) +  \partial_\sigma J^\sigma = 0$ is nonlinear, coupled, and anisotropic. 

Hence, slight differences lead to strong distortions (sensitive dependence),  geometry couples across scales enabling iterative folding, and fluxes amplify anisotropies generating “deterministic chaos” in $(x,\sigma)$. This is how Navier-Stokes, reaction-diffusion, or Vlasov dynamics produce deterministic multifractals with *no randomness*.

Thus, a deterministic PDE with nonlinear flux almost always produces fractal invariants without randomness. 

**4. The RC-consistent replacement for randomness: reflexivity.** In RC (and hence FRC) geometry produced by coherence, feeds back into dynamics, which updates coherence, which reshapes geometry… This feedback loop is *intrinsically symmetry-breaking*. Even if we start from a uniform initial condition, any tiny perturbation in  coherence density, geometry, gradients, or flux fields gets amplified through reflexive curvature coupling. This is the deterministic analogue of “random weights” in a traditional cascade, random weights are discretized approximation of reflexive curvature feedback.


## Appendix F: Reflexivity (no randomness)

Let's dive into the last example from previous chapter and explore reflexivity based deterministic symmetry breaking in place of random branching.

Used for simplicity in the beginning of the paper, the classical multiplicative cascades often introduce randomness in the branching weights $(w_1,w_2),\quad w_1+w_2=1,$ to avoid a trivial uniform split. In the fractal RC setting, however, **no stochasticity is required**. The reflexive coupling between coherence and geometry already induces deterministic anisotropy, each scale-slice contributes to the coherence tensor

$$
K_{\mu\nu}(x,t;\sigma),
$$

which then shapes the metric $g_{\mu\nu}[K]$ entering the fluxes $J^i$ and $J^\sigma$.
Because $g_{\mu\nu}$ varies across space and scale, the effective branching ratios become deterministic, geometry-dependent functions, e.g.

$$
w_i(x,\sigma) = F_i\big(K_{\mu\nu}(x,t;\sigma),\ \nabla C(x,t;\sigma),\  J_\mu(x,t;\sigma)\big),
\quad i=1,2.
$$

Thus the “weights” that drive the cascade are fully reflexive. The geometry created by coherence determines how coherence subsequently divides. Random branching may be viewed as a coarse discrete surrogate for this deterministic curvature feedback, but it is not part of the RC or FRC framework.

Let's make the "discretized reflexivity equals random weights" claim more formal.

**Lemma: deterministic origin of non-uniform branching.**  Let $C(x,t;\sigma)$ evolve under the FRC continuity equation and let $K_{\mu\nu}(x,t;\sigma)$ be the scale-resolved coherence tensor. Let's define the local branching weights by any smooth functional

$$
w_i(x,\sigma) = \frac{G_i\big(K_{\mu\nu}(x,t;\sigma),\ \nabla C(x,t;\sigma),\ J_\mu(x,t;\sigma)\big)} {G_1(\cdot)+G_2(\cdot)},\quad i=1,2,
$$

with $G_i>0$. 

Then the resulting branching operator $B[C] (x,\sigma)=w_1(x,\sigma)C(x,\sigma)+w_2(x,\sigma)C(x,\sigma)$ 
generates a non-uniform multiplicative cascade without the introduction of stochasticity.

**Proof (sketch).** Non-uniformity follows from the fact that either $K_{\mu\nu}$, $\nabla C$, or $J_\mu$ is non-constant on $\Omega\times[0,\infty)$. Since geometry and flux depend reflexively on $C$, any perturbation in coherence induces a perturbation in the weights. Thus all symmetry breaking is supplied deterministically by coherence-geometry coupling.

Let's conclude the section with the definition of **deterministic branching operator**. A natural geometry-driven branching operator is

$$
B[C] (x,t;\sigma) = \gamma C(x,t;\sigma) \frac{|\nabla C(x,t;\sigma)|^\alpha} {\int_{\Omega} |\nabla C(x,t;\sigma)|^\alpha dV_g}, \quad \alpha>0,
$$

or equivalently,

$$
w_i(x,\sigma)= \frac{|\nabla C|^\alpha}{\sum_j |\nabla C_j|^\alpha},
$$

where the denominator normalizes the mass flux. This operator is **deterministic**, **nonlinear**, and **reflexive**, producing multifractal scaling through geometric anisotropy rather than stochasticity.

---

## Bibiliography

- **Dafermos, C. M.** (2016). *Hyperbolic Conservation Laws in Continuum Physics* (4th ed.). Springer. **ISBN:** 978-3662518208
- **Evans, L. C.** (2010). *Partial Differential Equations* (2nd ed.). American Mathematical Society. **ISBN:** 978-0821849743
- **Falconer, K.** (2014). *Fractal Geometry: Mathematical Foundations and Applications* (3rd ed.). Wiley. **ISBN:** 978-1119942399
- **Guckenheimer, J., & Holmes, P.** (1983). *Nonlinear Oscillations, Dynamical Systems, and Bifurcations of Vector Fields*. Springer. **ISBN:** 978-0387908199
- **Mandelbrot, B. B.** (1982). *The Fractal Geometry of Nature*. W. H. Freeman. **ISBN:** 978-0716711865
- **Strogatz, S. H.** (2014). *Nonlinear Dynamics and Chaos: With Applications to Physics, Biology, Chemistry, and Engineering* (2nd ed.). Westview Press. **ISBN:** 978-0813349107
- **Susskind, L., & Friedman, A.** (2014). *Quantum Mechanics: The Theoretical Minimum*. Basic Books. **ISBN:** 978-0465062904
- **Susskind, L., & Friedman, A.** (2017). *Special Relativity and Classical Field Theory: The Theoretical Minimum*. Basic Books. **ISBN:** 978-0465093342
- **Jovanovic, U.** (2025). *Reflexive Organism Model*.
- **Jovanovic, U.** (2025). *Seeds of life*
- **Jovanovic, U.** (2025). *Coherence in Reflexive Organism Model*
- **Jovanovic, U.** (2025). *Reflexive Coherence*
- **Jovanovic, U.** (2025). *Reflexive Coherence: A Geometric Theory of Identity, Choice, and Abundance*


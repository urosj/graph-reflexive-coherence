Yes. I think the right framing has shifted from

$$
A_{\mathrm{CI+PC}}\stackrel{?}{=}A_{\mathrm{CI}}+A_{\mathrm{PC}}
$$

to

$$
\boxed{
A_{\mathrm{CI+PC}}
=
\text{a coupled realization whose two mechanisms are individually understood}
}
$$

That is a much better situation than starting a third realization from scratch, but it still needs its **own causal and mathematical closure**.

The reason is that CI and PC are not merely two independent decorations.

For \(A_{\rm CI}\), the difficult object was the **instantaneous implicit joint root**

$$
(J^*,H^*)
$$

and we proved its branch, regularity, source obstruction and return domain.

For \(A_{\rm PC}\), the difficult object was **persistent structural history**

$$
Z
$$

including its old-carrier staging, writer recurrence and cross-topology transport.

Once both are active, those two structures can affect each other. So the central question becomes not “do CI and PC individually work?” but:

$$
\boxed{
\text{does the coupled CI root + persistent carrier admit one coherent event/continuation law?}
}
$$

## What should *not* be redone

A large amount is already settled and should be treated as imported lemmas unless the coupling invalidates their hypotheses.

We should not rediscover:

* the binary \(2+2\) fission operation;
* source-only topology selection as a principle;
* exact decorated-sector machinery;
* charge-conservative resource transfer;
* old-edge \(W\) lineage and bridge \(W=1\);
* Candidate-A WLS/current/writer staging;
* the target double-star spectral algebra;
* dyadic allocator mechanics;
* reset/current role separation;
* transaction/replay/rollback architecture;
* finite represented-number methodology;
* the PC lossless relational \(Z\)-transport law \(c_t=c_s\);
* the CI Banach/root proof technique.

Those are now infrastructure.

So CI+PC should indeed be **narrower than either original investigation**.

---

# But the coupled mathematics has to be redone

There are several places where simply intersecting the CI and PC certificates would be unjustified.

### 1. The actual CI+PC ordinary step has to be fixed first

Before doing any theorem, we need the exact implementation/spec semantics for `A_CI+PC`.

In particular:

* what carrier enters the implicit CI root;
* whether the CI source is added on top of the persistent \(Z\) geometry;
* which \(S\) is held by the PC writer;
* whether that \(S\) comes from the selected coupled root;
* what geometry the restart root sees after \(Z^+\);
* whether there is any same-beat \(Z^+\to J\) feedback.

We must derive this from the actual step, just as we did for CI-0 and PC-0.

I would not assume the formula yet.

That gives a first small gate:

$$
\boxed{\mathrm{CIP\!-\!0}:\text{ exact realization-native step/event boundary}}
$$

This should be mostly forensic, not a research campaign.

---

# 2. The combined geometry budget is the main new theorem

This is probably the heart of CI+PC.

CI currently proved a root on

$$
\|H-I\|_F\le \frac1{4096}.
$$

PC currently admits persistent \(Z\) with

$$
\|Z\|_F\le\frac1{3072},
$$

with its induced geometry kept positive.

But we cannot simply say both bounds hold simultaneously.

If the combined realization has schematically

$$
H
=
I+\mathcal G(Z)+\kappa_H\operatorname{Star}(f(H)),
$$

then the CI instantaneous contribution and the PC persistent contribution consume the **same geometry budget**.

That means the first real coupled question is something like:

$$
\|\mathcal G(Z)\|
+
\|\kappa_H\operatorname{Star}(f(H))\|
\le \rho_{\rm CIP}.
$$

The separate CI and PC radii may be too generous when superposed.

So we likely need to derive a new joint domain:

$$
\boxed{
\|Z\|\le R_{\rm CIP},
\qquad
\|H-I\|\le\rho_{\rm CIP}
}
$$

with possibly

$$
R_{\rm CIP}<R_{\rm PC}
$$

and/or a slightly smaller parameter box.

That is not a problem. A smaller coupled domain is scientifically natural.

The important point is not to force the full union of both individual parameter boxes.

---

# 3. CI root uniqueness must be reproved *uniformly in Z*

This is the biggest thing we cannot inherit directly.

CI proves

$$
H=T(H)
$$

with a uniform contraction.

CI+PC will instead have a \(Z\)-parameterized map

$$
H=T_Z(H).
$$

We need:

$$
T_Z:\mathcal B_H\to\mathcal B_H
$$

and

$$
\sup_{Z\in\mathcal B_Z}
\operatorname{Lip}_H(T_Z)<1.
$$

Ideally also a useful dependence estimate

$$
\|H^*(Z_1)-H^*(Z_2)\|
\le L_Z\|Z_1-Z_2\|.
$$

That latter inequality would be extremely valuable, because then PC's carrier recurrence can be coupled cleanly to the CI root without treating every beat as a new independent proof problem.

This is the genuinely new CI+PC theorem.

---

# 4. The source obstruction must be checked with both mechanisms active

Again, likely much of the algebra transfers, but the error term changes.

For CI we had roughly

$$
x^+\ge (1+g_{\rm CI})x.
$$

For PC:

$$
x^+\ge (1+g_{\rm PC})x.
$$

CI+PC needs

$$
x^+\ge (1+g_{\rm CIP})x
$$

with \(Z\) evolving and the implicit root active simultaneously.

The useful outcome may simply be

$$
g_{\rm CIP}>0
$$

over a smaller joint box.

We do **not** need the same \(65/64\), \(61/60\), 71-step, or 89-step constants.

This is exactly where trying to “combine the certificates” would become artificial.

---

# 5. Event selection is likely reusable structurally, but not numerically

The allocator principle can stay:

$$
\text{fresh committed-state realization-native current}
\longrightarrow k.
$$

But CI and PC already produced slightly different values:

$$
k_{\rm CI}=33616,
\qquad
k_{\rm PC}=33615.
$$

So CI+PC should be allowed to produce its **own**

$$
k_{\rm CIP}.
$$

We should not expect it to equal either one.

The topology operation and transfer interval

$$
\frac{31}{64}\le \frac{k}{65536}\le\frac{33}{64}
$$

can probably remain, provided the new root/current theorem keeps the allocator inside it.

---

# 6. The PC relational transport probably survives, but its input has changed

This is an interesting distinction.

The topological meaning of

$$
c_t=c_s
$$

does not depend on whether the current that caused the fission came from PC or CI+PC.

So I think the **event transport law for persistent \(Z\)** is a strong candidate for direct reuse.

But its domain must be re-established:

* exact decorated sectors must remain invariant under the combined ordinary map;
* the pre-event \(Z\) must remain in the lossless-lift domain;
* the transported signed \(Z_t\) must be admissible to the **combined target root**, not merely PC's fixed-H read.

So:

$$
\boxed{\text{reuse the map, reprove its compatibility}}
$$

rather than derive a third \(Z\)-transport law.

That could save a lot of work.

---

# 7. Target continuation is now a coupled recurrence

This is probably the second major mathematical novelty after the \(Z\)-uniform root theorem.

PC had:

$$
X_{n+1}\le qX_n,
$$

$$
z_{n+1}
\le
b z_n+sX_n^2.
$$

CI had:

$$
X_{n+1}\le q_{\rm CI}X_n
$$

and instantaneous geometry satisfying roughly

$$
\|H-I\|\lesssim X^2.
$$

CI+PC should lead to a coupled system of the general shape

$$
X_{n+1}
\le
qX_n+A z_n,
$$

$$
z_{n+1}
\le
b z_n+sX_n^2,
$$

or perhaps the \(z_n\) effect can already be absorbed into the uniform root/current error and we retain

$$
X_{n+1}\le qX_n.
$$

Which case is true should be derived rather than assumed.

If the genuinely coupled recurrence is needed, we can analyze the comparison system

$$
\begin{pmatrix}
X_{n+1}\\
z_{n+1}
\end{pmatrix}
\lesssim
\begin{pmatrix}
q&A\\
0&b
\end{pmatrix}
\begin{pmatrix}
X_n\\
z_n
\end{pmatrix}
+
\begin{pmatrix}
0\\
sX_n^2
\end{pmatrix}.
$$

If

$$
q<1,\qquad b<1
$$

with sufficiently small coupling \(A\), closure should be straightforward.

And then the natural asymptotic target remains

$$
C\to\frac32\mathbf1,
\qquad
Z\to0,
\qquad
H\to I,
\qquad
J\to0,
\qquad
W\to e^{-3\alpha/2}.
$$

But this time \(H\to I\) would result from **both** disappearing persistent history and vanishing instantaneous CI source.

---

# A compact investigation program

I would not do another CI-0/1/2/3 + PC-0/1/2/3/4 sized campaign.

I think we can compress CI+PC to **three substantive stages**.

### CIP-0 — semantics and coupled-domain derivation

One package containing:

* exact native `A_CI+PC` step staging;
* authoritative state and old/new carrier timing;
* fresh event operand;
* combined \(H(Z,\text{CI root})\) equation;
* uniform \(Z\)-parameterized root theorem;
* exact-sector invariance;
* candidate joint parameter/request domain.

Gate:

$$
\boxed{\text{unique regular coupled root over a nonempty joint domain}}
$$

If that fails, stop and adjust the domain—not topology.

### CIP-1 — complete causal chain

Use one preregistered interior witness to prove:

$$
\text{ordinary combined onset}
\to
\text{combined obstruction}
\to
\text{fresh combined current}
\to
k_{\rm CIP}
\to
\text{binary fission}
$$

then:

* same resource/W transfer;
* existing lossless \(Z\) relational lift;
* both-role combined target roots;
* coupled \(X,z\) return theorem;
* no-split controls;
* \(W\)-reset, \(Z\)-reset, both-reset controls where relevant.

This is the real scientific gate.

### CIP-2 — consolidation/reference

Only after CIP-1 passes:

* widen to the proved parameter/request box;
* full executable research reference;
* independent Decimal oracle;
* root + carrier stage discrimination;
* covariance;
* lifecycle/replay/rollback;
* finite represented-number bridge;
* explicit scope/debt routing.

Then adjudicate.

So:

$$
\boxed{
\mathrm{CIP\!-\!0}
\rightarrow
\mathrm{CIP\!-\!1}
\rightarrow
\mathrm{CIP\!-\!2}
}
$$

rather than another 4–5-stage discovery sequence.

---

## What I would reuse immediately

The clean dependency picture is approximately:

$$
\begin{array}{c}
\text{Candidate-A fixed-H equations}\\
\text{WLS + writer staging}\\
\text{paired graph algebra}\\
\text{source/target transfer coordinates}\\
\text{transaction mechanics}
\end{array}
$$

feed all realizations.

Then:

$$
\boxed{\text{CI-2}}
$$

supplies the implicit-root machinery,

while

$$
\boxed{\text{PC-2/PC-4}}
$$

supplies persistent-carrier domain, relational event transport, and carrier recurrence machinery.

CI+PC's actual contribution is the **compatibility theorem between those two already-understood mechanisms**.

That is much narrower than solving either realization independently.

---

### One thing I would explicitly resist

I would not define the CI+PC admissible parameters as mechanically

$$
\mathcal P_{\rm CI}\cap\mathcal P_{\rm PC}.
$$

The right object is

$$
\boxed{
\mathcal P_{\rm CIP}
=
\{p:\text{the coupled root, obstruction, transfer and return inequalities all close}\}.
}
$$

It may happen to equal the intersection.

It may be strictly smaller.

And in some dimensions it might even tolerate values outside an individual conservative bound because the combined proof uses a different estimate.

So the domain should be **derived**, not inherited by set intersection.

---

I think this is actually a good point in the investigation. We have now reduced CI+PC to a much sharper scientific question:

$$
\boxed{
\textbf{Can persistent structural history }Z
\textbf{ and instantaneous implicit coherence geometry coexist through fission}
}
$$

without reopening the topology mechanism itself.

That is a substantially narrower problem than either A_CI or A_PC was at the start.

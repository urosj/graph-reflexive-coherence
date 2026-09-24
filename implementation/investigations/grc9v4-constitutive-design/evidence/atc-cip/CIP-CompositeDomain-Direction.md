Yes. A quick pass says the earlier idea holds **more strongly than I expected**: CI+PC is not “just combine the certificates,” but most of the hard machinery really does collapse to a small coupled-core problem.

The biggest simplification is that **CI-2 and PC-4 already use the same scalar parameter box and request interval**: the same \(\alpha,\beta,\gamma,\chi,\kappa_H,\kappa_{Ah},a,\nu\) ranges and \(h\in[3/25,1/8]\). What differs is the structural domain: CI controls a joint-root geometry ball, while PC controls a persistent-\(Z\) ball. 

And V4 already fixes the actual hybrid semantics. For A-CI+PC,

$$
K_{\rm eff}
=
K_{4,\rm base}+Z_k+\rho_{\rm inst}S(J,H),
$$

with old \(Z_k\) a committed input—not a root unknown—and the same root source later written into \(Z_{k+1}\). The primary profile has \(\rho_{\rm inst}=1\), and new \(Z_{k+1}\) never re-enters the same beat.

So I would now make **CIP-0 and CIP-1 much tighter**.

## CIP-0 — coupled semantics and nonempty composite domain

### CIP-0A — freeze the actual step

The realization-native ordinary step should be audited against:

$$
(C_k,W_k,Z_k)
\rightarrow
(J_k^\*,H_k^\*,S_k^\*)
\rightarrow
C_{k+1}
\rightarrow
W_{k+1}
\rightarrow
Z_{k+1}
\rightarrow
\text{fresh combined restart root}.
$$

The joint root reads:

$$
Z_k
$$

and simultaneously solves the instantaneous CI source. Then the **same**

$$
S_k^\*
$$

is used by

$$
Z_{k+1}
=
a_{\rm PC}Z_k+(1-a_{\rm PC})S_k^\*.
$$

No \(Z_{k+1}\) same-beat feedback. That is already specified by V4 rather than something we need to invent.

One specific audit obligation here is gain identity:

$$
\chi\text{ once},\quad
\zeta\text{ once},\quad
\rho_{\rm inst}\text{ once},\quad
\kappa_H\text{ once}.
$$

We should verify that the \(S\) closed by the CI root and the \(S\) consumed by the PC writer are literally the same registered source, not two almost-equivalent research constructions.

### CIP-0B — parameterized CI root

For the affine A specialization, the composite fixed-point map should reduce schematically to

$$
\boxed{
T_Z(H)
=
I+\kappa_H
\left[
Z+\operatorname{Star}(f(H))
\right]
}
$$

for \(\rho_{\rm inst}=1\).

This is very favorable mathematically.

Since \(Z\) is fixed during a root solve,

$$
T_{Z_1}(H)-T_{Z_2}(H)
=
\kappa_H(Z_1-Z_2),
$$

and, crucially,

$$
D_HT_Z
=
D_HT_{\rm CI}.
$$

Therefore **old \(Z\) does not worsen the CI contraction constant**. It only consumes self-map/displacement radius.

So the CI-2 contraction/regularity work almost imports directly. The new inequality is basically

$$
\boxed{
\kappa_H
\left(
R_Z+S_{\max}
\right)
<
\rho_H.
}
$$

CI-2 has

$$
\rho_H=\frac1{4096}\approx2.4414\times10^{-4}
$$

and its source instantaneous-geometry bound is about

$$
S_{\max}\approx1.9904\times10^{-4}.
$$

PC-4's independently derived whole-box held-source bound is extremely similar,

$$
S_{\max,\rm PC}\approx1.9960\times10^{-4}.
$$



This immediately tells us something important:

### The full PC carrier ball does *not* simply compose

PC has

$$
R_{\rm PC}=\frac1{3072}\approx3.2552\times10^{-4}.
$$

Even at

$$
\kappa_H=\frac12,
$$

a naive worst-case superposition gives roughly

$$
\frac12
\left(
3.2552\times10^{-4}
+
1.9960\times10^{-4}
\right)
\approx2.6256\times10^{-4},
$$

which is larger than \(1/4096\).

So:

$$
\boxed{
\text{full PC domain}+\text{full CI geometry ball does not compose naively}.
}
$$

That confirms your concern.

But there is already a clear nonempty combined domain.

For example, take provisionally

$$
\boxed{
R_{\rm CIP}=\frac1{5000}=2\times10^{-4}
}
$$

and

$$
\boxed{
\frac12\le\kappa_H\le\frac35.
}
$$

Then even using the slightly larger PC held-source bound,

$$
\frac35
\left(
\frac1{5000}
+
1.9960\times10^{-4}
\right)
\approx2.3976\times10^{-4}
<
\frac1{4096}.
$$

At the same time,

$$
S_{\max}<\frac1{5000},
$$

so the PC writer preserves the \(Z\)-ball simply because it is a convex update:

$$
\|Z^+\|
\le
a\|Z\|+(1-a)\|S\|
\le R_{\rm CIP}.
$$

That is already a plausible **first composite domain**, without deriving any new physics.

I would treat \(R=1/5000,\ \kappa_H\in[1/2,3/5]\) only as a first proof box—not as the final maximal one.

### CIP-0C — root dependence on persistent history

We can probably get essentially for free:

$$
\boxed{
\|H^\*(Z_1)-H^\*(Z_2)\|
\le
\frac{\kappa_H}{1-L_{\rm CI}}
\|Z_1-Z_2\|.
}
$$

This follows from the parameterized contraction theorem.

That gives a clean mathematical statement of how persistent geometry perturbs the instantaneous root, which neither standalone realization needed.

### CIP-0D — symmetry and event operand

If \(Z\) begins in the exact decorated \(2+2\) carrier subspace:

* the combined root is equivariant;
* its \(S^\*\) is decorated;
* the PC writer preserves that decoration;
* therefore the next \(Z\) remains decorated.

So the PC-2 relational fission map remains type-compatible.

The K0 operand should then be the **fresh committed-state combined root**

$$
R_{\rm CIP}
(C_{k+1},W_{k+1},Z_{k+1}),
$$

not the root that drove the preceding beat.

That combines the CI fresh-root lesson and PC old/new-carrier lesson without conflict.

### CIP-0 gate

I would call CIP-0 closed if we have:

$$
\boxed{
\begin{array}{l}
\text{exact ordinary-step staging}\\
+\text{ same-source identity}\\
+\text{ nonempty }(Z,H)\text{ composite domain}\\
+\text{ unique regular }Z\text{-parameterized root}\\
+\text{ carrier-ball invariance}\\
+\text{ decorated-sector invariance}\\
+\text{ fresh poststate event root}.
\end{array}}
$$

This looks very achievable.

---

# CIP-1 — one complete combined causal chain

Here it gets even more reusable.

## CIP-1A — use the existing common source witness

CI and PC already happen to use the same useful current-role \(C/W\) source:

$$
C=
\left(
\frac{61}{50},
\frac{61}{50},
\frac65,
\frac65,
\frac{104}{25}
\right),
$$

$$
W=
\left(
\frac{97}{100},
\frac{97}{100},
\frac{99}{100},
\frac{99}{100}
\right).
$$

PC adds

$$
Z=\frac1{16384}I_4.
$$

This is almost ideal for the combined witness.

Its initial carrier norm is

$$
\|Z\|_F=\frac1{8192}
\approx1.22\times10^{-4},
$$

well inside the candidate \(1/5000\) ball.

So the first CIP-1 calculation could simply be:

$$
\text{same CI/PC C,W fixture}
+
\text{PC's existing nonzero }Z
$$

with \(h=1/8\) and, initially, \(\kappa_H=1/2\).

That exercises both mechanisms from the start rather than using the degenerate \(Z=0\) ablation.

## CIP-1B — source obstruction probably needs almost no new algebra

This is an important consequence of keeping the **total combined \(H\)** inside the old CI geometry ball.

CI-2's source-current error estimate only cares that

$$
\|H-I\|\le\rho_H
$$

and that the read/current channel stays within its existing bounds.

It does not care whether

$$
H-I
$$

came from instantaneous CI source alone or from

$$
Z+S^\*.
$$

So if CIP-0 closes the composite root inside the same ball, I think the existing CI obstruction

$$
\boxed{
x^+\ge\frac{65}{64}x
}
$$

can probably be imported **unchanged**.

That would mean we do not need a new source-instability campaign.

The combined no-split trajectory fails by the same 71-proposal resource argument.

## CIP-1C — only the allocator is really new

After one ordinary combined beat, recompute

$$
R_{\rm CIP}(C',W',Z').
$$

Then require:

* fresh combined-root sector inflows positive;
* exact decorated sectors;
* source-only dyadic selection;
* result within

$$
\frac{31}{64}
\le
\frac{k_{\rm CIP}}{65536}
\le
\frac{33}{64}.
$$

We should **not** require

$$
k_{\rm CIP}=33616
$$

or

$$
33615.
$$

It gets its own value.

This may be one of the very few genuinely new numerical facts in CIP-1.

## CIP-1D — topology transfer can mostly be imported

Once \(k_{\rm CIP}\) lies in the admitted transfer interval:

### \(C\)

Use exactly the established conservative dyadic resource map.

### \(W\)

Use exact old-edge lineage plus bridge seed \(W_b=1\).

### \(Z\)

Use the already-selected PC lossless relational transport:

$$
L_{\rm rel},
\qquad
c_t=c_s.
$$

The CI-2 funding lemma is realization-independent over this share box, and now explicitly has

$$
\boxed{
\Delta_{\rm fund}\ge\frac{1303}{1600}>0.
}
$$



And the PC \(Z\) lift is Frobenius-isometric, so if

$$
\|Z_s\|\le R_{\rm CIP},
$$

then automatically

$$
\|Z_t\|\le R_{\rm CIP}.
$$

So the transfer itself needs very little new work.

## CIP-1E — target return may be simpler than I thought

My previous sketch suggested a genuinely coupled resource recurrence such as

$$
X_{n+1}\le qX_n+A z_n.
$$

I now suspect we **do not need that**.

If CIP-0 guarantees

$$
\|H_n-I\|\le\rho_H
$$

for every combined root, then CI-2 already uniformly absorbs *all* permitted geometry error into its return theorem.

So we may retain directly:

$$
\boxed{
X_{n+1}\le q_{\rm CI}X_n,
\qquad
q_{\rm CI}\approx0.900516.
}
$$

The persistent carrier then obeys the separate PC-style recurrence

$$
z_{n+1}
\le
b z_n+(1-b)sX_n^2,
$$

with

$$
b\le\frac{25}{37}<1.
$$

Since

$$
q_{\rm CI}^2
\approx0.811
>
\frac{25}{37}
\approx0.676,
$$

the usual convolution closes:

$$
z_n\to0.
$$

Then the instantaneous source also vanishes:

$$
S_n\to0,
$$

and hence

$$
H_n-I
=
\kappa_H(Z_n+S_n)
\to0.
$$

So the combined asymptotic is again

$$
\boxed{
C\to\frac32\mathbf1,\quad
J\to0,\quad
Z\to0,\quad
H\to I,\quad
W\to e^{-3\alpha/2}.
}
$$

The key difference is that now \(H\to I\) requires **both temporal structural paths** to disappear.

That looks much easier than deriving a new coupled stability theory.

---

# CIP-1 controls are almost already done

The counterfactual side is also unusually clean.

### No split

Full CI+PC remains in the source obstruction cone:

$$
x^+\ge65x/64.
$$

### Reset \(W\) only

Still inside the same uniform source theorem.

### Reset \(Z\) only

The profile reduces exactly to CI because V4 declares

$$
Z=0,\quad \rho_{\rm inst}=1,\quad\text{PC disabled}
\;\Rightarrow\;
\text{CI}.
$$

The CI obstruction is already closed.

### Reset both \(W\) and \(Z\)

Reduces to the already-failing CI \(W\)-reset control.

So fission remains causally necessary in the bounded family without inventing another control campaign.

---

# What I think the quick outline says

The remaining new science is probably only four things:

1. **Composite root-domain budget**

   $$
   \kappa_H(R_Z+S_{\max})<\rho_H.
   $$

2. **Exact source identity**
   — the instantaneous root source must be exactly the source written into \(Z\).

3. **One new combined selector result**

   $$
   k_{\rm CIP}.
   $$

4. **Both-role target composite readmission**
   with signed transported \(Z\).

Everything else looks likely to be imported or slightly generalized from CI-2/3 and PC-2/4.

So I would revise the program to something like:

$$
\boxed{
\mathrm{CIP\!-\!0}
=
\text{step semantics}
+
\text{composite-root/domain theorem}
}
$$

then

$$
\boxed{
\mathrm{CIP\!-\!1}
=
\text{one complete combined fission/return witness}
}
$$

and **only if both work**, a short CIP-2 conformance/adjudication package.

My provisional expectation after this pass is that **CIP-0 is substantially mathematical but small, and CIP-1 could be surprisingly short**. The big discovery campaigns—finding the operation, finding the carrier law, finding the CI root branch—are already behind us.

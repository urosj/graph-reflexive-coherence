Yes. The pressure **breaks the current PC-2 selection rationale**.

The submitted partial-loss map is mathematically valid as one admissible carrier transport, but I do **not** think it should be selected as the PC-2 law. In the actual PC-1 exact decorated domain, I can construct a **lossless, covariant, Frobenius-isometric carrier transport** using the new bridge.

So my disposition is:

$$
\boxed{\textbf{PC-2 partial-loss map as a valid option: PASS}}
$$

but

$$
\boxed{\textbf{PC-2 partial-loss map as the preferred/best law: REFUTED}}
$$

and

$$
\boxed{\textbf{“loss is unavoidable” on the accepted PC-1 domain: REFUTED}.}
$$

## Where the current argument over-constrains the problem

The proposed law first injects the four old edge coordinates into the target, then orthogonally projects away entries that cease to be target-star-supported:

$$
\widetilde Z=EZE^\top,\qquad
Z_t=\Pi_t\widetilde Z.
$$

It additionally requires **zero memory on the new bridge**. The note is explicit that this “no invented bridge memory” condition is an additional constitutive choice, not something already forced by V4. 

Under that assumption, the projection is indeed uniquely Frobenius-nearest to the naive old-edge embedding. It has source dimension \(10\), retained rank \(6\), and kernel dimension \(4\); on the decorated paired subspace it maps dimension \(5\) to rank \(4\), losing one degree. 

But those are the dimensions of **that projection**, not of the admissible target carrier space.

The target double-star carrier has five edge coordinates:

$$
u_0,u_1,v_0,v_1,b,
$$

where \(b\) is the new bridge. A symmetric star-supported target carrier may contain:

* two \(U\)-block degrees;
* two \(V\)-block degrees;
* one bridge–\(U\) coupling;
* one bridge–\(V\) coupling;
* one bridge diagonal.

So its decorated target space has dimension

$$
\boxed{7}.
$$

The accepted decorated source carrier has dimension

$$
\boxed{5}.
$$

There is therefore ample target capacity. And the hardened carrier admission code does **not** require bridge entries to vanish—it requires symmetry, target-star support, decorated-sector symmetry, and the carrier norm bound. 

So the rank-\(4\) result is self-imposed by:

$$
\boxed{\text{“new bridge has no inherited memory.”}}
$$

That is exactly the axiom we should pressure.

---

# The lost source mode has an obvious new physical locus

On the exact paired source domain, write the carrier in sector form:

$$
Z_s=
\begin{pmatrix}
A&C\\
C^\top&B
\end{pmatrix},
$$

where decorated symmetry forces

$$
A=
\begin{pmatrix}a&b\\b&a\end{pmatrix},
\qquad
B=
\begin{pmatrix}d&e\\e&d\end{pmatrix},
$$

and, in canonical orientation,

$$
C=
c
\begin{pmatrix}
1&1\\
1&1
\end{pmatrix}.
$$

Thus the entire part discarded by the current PC-2 projection is **one scalar**

$$
\boxed{c}.
$$

For the actual current-role PC-1 carrier,

$$
c\approx6.71072581\times10^{-9},
$$

which is why the submitted certificate finds genuinely nonzero loss. 

Before fission, \(c\) describes memory coupling the two sectors **through their shared parent**.

After fission, the sectors no longer share a parent.

But they now have exactly one new physical relation:

$$
\boxed{\text{the child--child bridge}.}
$$

That strongly suggests that discarding \(c\) is not the natural continuation. The bridge is precisely the new topological realization of what used to be a parent-mediated inter-sector relation.

---

# A lossless carrier lift

Let \(p\) be the source parent, with sectors \(U,V\). Let \(b\) denote the new target bridge connecting children \(p_U,p_V\).

Use oriented incidence signs. For source old edge \(i\),

$$
\sigma_i=B^s_{p i}\in\{\pm1\}.
$$

On the decorated source domain the cross-sector carrier has the coordinate-free form

$$
Z^s_{ij}
=
c\,\sigma_i\sigma_j,
\qquad
i\in U,\;j\in V.
$$

Equivalently,

$$
\boxed{
c=
\frac1{|U||V|}
\sum_{i\in U,j\in V}
\sigma_i\sigma_j Z^s_{ij}.
}
$$

That scalar is invariant under arbitrary edge-orientation changes.

Now let old edge \(i\) survive as target edge \(\bar i\), with signed lineage \(\ell_i\). Preserve all within-child memory exactly:

$$
Z^t_{\bar i\bar j}
=
\ell_i\ell_j Z^s_{ij},
\qquad
i,j\in U
\quad\text{or}\quad
i,j\in V.
$$

As target star support requires,

$$
Z^t_{\bar i\bar j}=0,
\qquad
i\in U,\ j\in V.
$$

But instead of deleting that relational memory, put it on the bridge.

If \(\bar i\) belongs to child \(p_X\), define

$$
\tau_{\bar i}=B^t_{p_X,\bar i},
\qquad
\tau_b^{(X)}=B^t_{p_X,b}.
$$

Then set

$$
\boxed{
Z^t_{\bar i b}
=
Z^t_{b\bar i}
=
c\,\tau_{\bar i}\tau_b^{(X)}.
}
$$

Finally,

$$
\boxed{Z^t_{bb}=0}.
$$

So no independent bridge **self-memory** is invented. Only source relational memory is moved onto the new relation that replaces the old common parent.

Call this, provisionally,

$$
\boxed{
L_{K4,\mathrm{evt}}^{\rm rel}
:
Z_s\mapsto Z_t
}
$$

or something like `pc_star_fission_relational_lift_lossless_v1`.

---

## In the canonical fixture

With the usual source/target edge orientations, it has the form

$$
\boxed{
Z_t=
\begin{pmatrix}
a&b&0&0&-c\\
b&a&0&0&-c\\
0&0&d&e&+c\\
0&0&e&d&+c\\
-c&-c&+c&+c&0
\end{pmatrix}.
}
$$

The signs are not arbitrary decorations. They are generated from target incidence, so changing edge orientations transforms them covariantly.

Compare that with the present projection:

$$
\begin{pmatrix}
a&b&0&0&0\\
b&a&0&0&0\\
0&0&d&e&0\\
0&0&e&d&0\\
0&0&0&0&0
\end{pmatrix}.
$$

The latter is literally obtained by dropping the \(c\)-mode.

---

# It is exactly lossless

The source cross-sector block contains eight matrix entries of magnitude \(|c|\): four \(U\times V\), plus their four transposes.

Its Frobenius contribution is therefore

$$
8c^2.
$$

The lossless target has four old-edge/bridge couplings, again present symmetrically, hence also eight entries of magnitude \(|c|\):

$$
8c^2.
$$

Everything else is transported sign-isometrically.

Therefore

$$
\boxed{\|Z_t\|_F=\|Z_s\|_F}.
$$

Not merely bounded:

$$
\boxed{\textbf{exact Frobenius isometry}.}
$$

Consequently the already-declared PC carrier ball immediately survives:

$$
\|Z_s\|_F\le\frac1{3072}
\Longrightarrow
\|Z_t\|_F\le\frac1{3072}.
$$

Hence

$$
\|H_t-I\|_F
\le
\frac34\frac1{3072}
=
\frac1{4096},
$$

and

$$
\lambda_{\min}(H_t)
\ge
\frac{4095}{4096}>0.
$$

So it gets the same carrier/geometry admission that the lossy map had, without deleting information. The current proposal's carrier admission result was based on precisely this radius. 

---

# There is an explicit inverse

The source cross scalar is recovered from target bridge couplings:

$$
\boxed{
c=
\frac14
\sum_{\bar i\in U'\cup V'}
\tau_{\bar i}\tau_b^{(X(\bar i))}
Z^t_{\bar i b}.
}
$$

Then reconstruct

$$
Z^s_{ij}
=
c\,\sigma_i\sigma_j
$$

for every source cross-sector pair, and invert signed lineage on the two surviving blocks.

Therefore

$$
\boxed{
R\circ L_{K4,\mathrm{evt}}^{\rm rel}
=
I
}
$$

on the accepted decorated PC source domain.

This is information-lossless in the literal sense, not merely “loss recorded in a receipt.”

---

# Covariance pressure passes

I pressure-tested this construction independently with exact rational arithmetic.

I randomly changed:

* all source-edge orderings;
* all target-edge orderings, including moving the bridge index;
* independent source edge orientations;
* independent target edge orientations;
* signed surviving-edge lineage;
* vertex labels.

Across **1,000 exact signed edge-coordinate cases**, the directly recomputed map equaled the corresponding signed/permuted transform of the canonical result, and the explicit inverse reconstructed the exact source carrier every time.

I also separately exercised 100 vertex relabelings with exact arithmetic.

That numerical pressure is not needed for the algebraic proof, but it is useful confirmation that the incidence-sign formula is doing what it is supposed to do rather than relying on canonical array positions.

The proposed lossy checker already establishes that graph/coordinate covariance is an important obligation. 

The lossless rule satisfies the same kind of obligation, but without imposing zero bridge couplings.

---

# Why the existing “nearest carrier” argument doesn't beat this

The current proposal says its projection is the unique target-star matrix minimizing

$$
\|Y-EZE^\top\|_F.
$$

That statement is mathematically correct. 

But it answers the wrong optimization problem for persistent structural memory.

The embedding \(EZE^\top\) already says:

> old edge coordinates survive, and **the new bridge begins with no relation to source memory**.

Then the closest target-star matrix naturally deletes unsupported cross-sector entries.

So the conclusion

$$
\text{“projection is minimally destructive”}
$$

really means

$$
\boxed{
\text{“minimally changes a representation in which bridge inheritance was prohibited in advance.”}
}
$$

It is not a proof that information loss is physically unavoidable.

The lossless lift uses a different continuity principle:

> Preserve a structural relation when its **support changes representation** under the topology event.

That seems more appropriate for persistent \(Z_4\) history.

---

# It is also almost uniquely determined by natural requirements

On the decorated source domain, suppose we require:

1. linear transport;
2. exact preservation of both within-sector blocks;
3. no direct target \(U\)-\(V\) old-edge entries, because they are not star-supported;
4. exact sector covariance;
5. child-exchange covariance;
6. zero bridge **diagonal**—no invented bridge self-history;
7. exact Frobenius norm preservation.

The only available place for \(c\) is then the bridge–old-edge couplings.

Sector symmetry gives one coupling value on each side:

$$
g_U,\qquad g_V.
$$

Child exchange reverses bridge orientation, forcing

$$
g_V=-g_U
$$

in canonical coordinates.

Frobenius isometry gives

$$
8g_U^2=8c^2.
$$

Hence

$$
|g_U|=|c|.
$$

Incidence covariance fixes the remaining sign.

So, up to coordinate convention, the rule above is essentially the unique solution under those conditions.

That is a much stronger selection principle than “nearest after requiring zero bridge memory.”

---

## Actual current-role consequence

The PC-2 certificate currently proves nonzero discarded memory for the live role. 

That loss is

$$
\|D\|_F^2
\approx
3.60270727\times10^{-16},
$$

or

$$
\|D\|_F\approx1.89808\times10^{-8}.
$$

It is small compared with the whole carrier norm, but it is **genuinely nonzero**.

The lossless map moves exactly that Frobenius contribution onto the four bridge couplings.

For the reset role, the source carrier is diagonal, hence

$$
c=0.
$$

So the lossless map reduces exactly to the current support restriction and still reports no cross-memory movement. The existing certificate already observes that restriction loses exactly zero information for reset. 

That is a nice consistency check.

---

# There is, however, a real no-go beyond the present PC-1 domain

This is important because the lossy proposal was not completely misguided.

For a **generic symmetry-breaking source carrier**, the cross block

$$
C\in\mathbb R^{2\times2}
$$

contains four independent modes under

$$
G=S_2^U\times S_2^V:
$$

$$
(++),\quad (+-),\quad (-+),\quad (--).
$$

The mixed mode is represented by

$$
C_{--}
=
\begin{pmatrix}
1&-1\\
-1&1
\end{pmatrix}.
$$

It changes sign under either individual sector swap but is fixed by performing both swaps.

The target double-star star-supported carrier has:

* \(U\)-block modes;
* \(V\)-block modes;
* bridge–\(U\) modes;
* bridge–\(V\) modes;
* bridge diagonal.

It has no \((--)\) representation.

That gives a genuine equivariance obstruction.

Let \(g_U,g_V\) denote the two swaps. For the source mixed mode \(z\),

$$
g_Uz=-z,
\qquad
g_Vz=-z,
\qquad
g_Ug_Vz=z.
$$

If \(F\) were an injective equivariant target-carrier map, then

$$
F(z)=g_Ug_VF(z).
$$

But the target subspace fixed by \(g_Ug_V\) has no mixed-sign component, so \(g_U\) acts trivially there. Hence

$$
F(-z)
=
F(g_Uz)
=
g_UF(z)
=
F(z),
$$

contradicting injectivity.

Thus:

$$
\boxed{
\textbf{a lossless equivariant transport is impossible on the full symmetry-breaking carrier space}
}
$$

without enlarging the target state representation or relaxing some structural condition.

But—and this is the decisive distinction—

$$
\boxed{
\textbf{the accepted PC-1 carrier domain does not contain that mode.}
}
$$

Its exact decorated symmetry removes the \((+-),(-+),(--)\) modes, leaving just the one cross-sector scalar \(c\).

That scalar **can** be transported losslessly.

---

# Therefore I would change PC-2

The submitted document currently says:

> preserve supported memory, discard unsupported memory, invent no history on the bridge. 

I would replace that principle for the bounded decorated domain with:

> **Preserve all structural memory whose causal relation survives the fission, allowing its carrier coordinates to change with the topology. Within-sector memory follows surviving old-edge support; the exact parent-mediated cross-sector memory is transported onto the new child–child bridge incidence. No independent bridge self-memory is introduced.**

Then use the lossless map above.

My revised status table would be:

| PC-2 question                                                          | Verdict                                   |
| ---------------------------------------------------------------------- | ----------------------------------------- |
| Existing support projection is mathematically well-defined             | **PASS**                                  |
| Projection is Frobenius-nearest with bridge memory forced to zero      | **PASS**                                  |
| Zero bridge memory is forced by V4 / topology                          | **REFUTED**                               |
| Partial information loss is unavoidable on PC-1 domain                 | **REFUTED**                               |
| Lossless target-star carrier exists on PC-1 decorated domain           | **YES**                                   |
| Lossless map can be bounded by same carrier radius                     | **YES — isometry**                        |
| Exact inverse exists                                                   | **YES**                                   |
| Signed-coordinate / relabel covariance                                 | **PASS in independent pressure**          |
| Bridge self-memory must be invented                                    | **NO — diagonal can remain zero**         |
| Generic symmetry-breaking carrier can always be transported losslessly | **NO — genuine equivariance obstruction** |
| Current selected PC-2 policy                                           | **HOLD / supersede**                      |
| Lossless relational-bridge policy                                      | **Strong candidate for revised PC-2**     |

So the pressure did exactly what you wanted:

$$
\boxed{
\textbf{controlled partial memory loss is not the best PC-2 solution at the scope we have actually proved.}
}
$$

The more interesting result is that topology change does **not** necessarily destroy the old relational memory. It can change the *support on which that memory is represented*:

$$
\boxed{
\text{shared-parent cross-sector memory}
\quad\longrightarrow\quad
\text{bridge-mediated child relation}.
}
$$

That feels much more like the PC realization we were trying to preserve in the first place.

The next PC-2 evidence should therefore try to **falsify this lossless relational lift**, rather than proceeding to PC-3 with the lossy projection.

Yes. I tried to falsify the **lossless relational lift** rather than defend it, and so far the pressure goes the other way:

$$
\boxed{\textbf{the lossless lift survives PC-2 pressure}}
$$

and

$$
\boxed{\textbf{the present partial-loss law should not be selected as PC-2}.}
$$

The current partial-loss proposal is valid only after adding the constitutive axiom that the newly created bridge must carry **zero inherited carrier memory**. The document is explicit about that extra assumption: it preserves old memory only where old support survives, zeros unsupported cross-child terms, and initializes bridge diagonal and bridge couplings to zero.  Once that extra axiom is removed, loss is not forced.

## 1. Exact lossless map on the actual PC-1 domain

On the exact decorated \(2+2\) source sector manifold, every admitted source carrier has the form

$$
Z_s=
\begin{pmatrix}
a&b&c&c\\
b&a&c&c\\
c&c&d&e\\
c&c&e&d
\end{pmatrix}
$$

in canonical orientation.

So the entire cross-sector history that the current projection deletes is only **one independent scalar**, \(c\). This agrees with the submitted dimension count: decorated source dimension \(5\), projected retained dimension \(4\). 

The target, however, has five edges:

$$
(u_0,u_1,v_0,v_1,b),
$$

where \(b\) is the new child-child bridge. Its star-supported decorated carrier space has **seven** degrees of freedom, because bridge-to-old-edge couplings are perfectly lawful target coordinates. The current `Carrier` admission requires symmetry, target star support, decorated-sector symmetry, and the Frobenius ball; it does not require bridge couplings to vanish. 

So there is enough target state space to carry \(c\).

In canonical orientation, the map I get is

$$
\boxed{
L_{\rm rel}(Z_s)=
\begin{pmatrix}
a&b&0&0&-c\\
b&a&0&0&-c\\
0&0&d&e&+c\\
0&0&e&d&+c\\
-c&-c&+c&+c&0
\end{pmatrix}.
}
$$

Interpretation:

* \(a,b\): old \(U\)-sector structural history stays with the \(U\) child;
* \(d,e\): old \(V\)-sector history stays with the \(V\) child;
* old \(U\)-\(V\) direct coupling disappears because those old edges no longer share a vertex;
* that same relational memory \(c\) becomes coupling of the surviving old edges to the **new bridge**;
* bridge diagonal remains zero.

So this does **not** claim the new bridge itself existed historically. It says the pre-existing *relation between the two sectors* now has a new support.

That distinction is important.

---

## 2. The map is exactly invertible

The source scalar can be recovered from the target bridge incidences.

Coordinate-free, let

$$
\epsilon_i^s=B^s_{p i}
$$

be the source-parent incidence sign. Define

$$
c(Z)=
\frac1{|U||V|}
\sum_{i\in U,j\in V}
\epsilon_i^s\epsilon_j^s Z_{ij}.
$$

For a target old edge \(\bar i\) attached to child \(p_X\), with new bridge \(b\), set

$$
(L_{\rm rel}Z)_{\bar i b}
=
\epsilon_{\bar i,p_X}^t\,
\epsilon_{b,p_X}^t\,
c(Z).
$$

The old within-sector blocks follow signed edge lineage exactly.

Then

$$
c=
\frac1{4}
\sum_{\bar i}
\epsilon_{\bar i,p_X}^t
\epsilon_{b,p_X}^t
(L_{\rm rel}Z)_{\bar i b},
$$

and the complete old cross block follows from

$$
Z_{ij}
=
\epsilon_i^s\epsilon_j^s c.
$$

Hence there is an explicit left inverse:

$$
\boxed{
R_{\rm rel}L_{\rm rel}=I
}
$$

on the declared PC-1 decorated carrier domain.

So there is literally no carrier information loss there.

---

## 3. It is an exact Frobenius isometry

This was the nicest surprise.

In the \(2+2\) source, \(c\) occurs in eight matrix positions when symmetry is counted:

$$
4\quad U\!\times V
$$

plus their four transposes, giving

$$
8c^2
$$

of Frobenius norm squared.

After fission, there are four bridge-old-edge couplings, each appearing symmetrically:

$$
2\times4c^2=8c^2.
$$

Everything else is transported sign-isometrically.

Therefore

$$
\boxed{
\|L_{\rm rel}Z\|_F=\|Z\|_F.
}
$$

So its operator norm is exactly one, and the existing PC carrier ball transports unchanged:

$$
\|Z\|_F\le\frac1{3072}
\quad\Longrightarrow\quad
\|L_{\rm rel}Z\|_F\le\frac1{3072}.
$$

Consequently,

$$
\|H_t-I\|_F
=
\frac34\|Z_t\|_F
\le\frac1{4096},
$$

and therefore

$$
\lambda_{\min}(H_t)
\ge
1-\frac1{4096}
=
\frac{4095}{4096}>0.
$$

That gives the same carrier/geometry admission margin claimed by the partial-loss proposal. The latter's target admission relies on exactly this carrier radius. 

---

## 4. Signed-coordinate covariance survives strong pressure

I implemented the coordinate-free version independently with exact rational arithmetic and tried to break it through:

* arbitrary permutations of the four source edge coordinates;
* arbitrary permutations of all five target coordinates, including moving the bridge;
* independent orientation reversal of every source edge;
* independent orientation reversal of every target edge;
* corresponding signed old-edge lineage;
* reconstruction through the explicit inverse.

Across **5,000 randomized exact signed/permuted cases**:

$$
L(Q_sZQ_s^\top)
=
Q_tL(Z)Q_t^\top
$$

held exactly, the inverse recovered the exact transformed source each time, and

$$
\|LZ\|_F^2=\|Z\|_F^2
$$

held exactly.

This directly targets the same covariance concern exercised by the existing PC-2 checker, which currently tests signed coordinate generators, vertex relabelings, Pythagorean decomposition, and malformed lineage. 

I found no canonical-edge-order dependency.

---

## 5. It works on the actual PC-1 carriers

For the actual current-role postbeat carrier, the cross-sector scalar is approximately

$$
c=6.7107258103\times10^{-9}.
$$

This is exactly the component the submitted partial-loss certificate identifies as genuinely discarded—the current-role loss is explicitly `proved_nonzero`. 

Applying the lossless map to the actual interval carrier:

* satisfies the existing target `Carrier` star-support checks;
* preserves the **same exact carrier norm upper bound** as the source;
* therefore stays inside the same \(1/3072\) domain.

For the independent reset carrier,

$$
c=0.
$$

So the lossless map naturally reduces to the current support-restriction result: no bridge coupling is created because there is no cross-sector history to carry. The existing certificate already observes exactly zero discarded history for this reset under restriction. 

That is a particularly good negative control.

---

# 6. The hardest pressure: PSD/reachable-history semantics

There is one real objection to the simple linear isometry.

The PC structural source

$$
S=\operatorname{Star}(f)
$$

is PSD, and starting from a PSD carrier the ordinary PC writer preserves PSD. The actual current source carrier is indeed PSD.

The simple linear lift above can make the target \(Z\) slightly indefinite.

For the actual current witness I obtain roughly

$$
\lambda_{\min}(Z_t)
\approx-5.90\times10^{-12}.
$$

But the actual geometry remains extremely safely SPD:

$$
\lambda_{\min}
\left(I+\frac34Z_t\right)
\approx
0.9999999999956.
$$

And importantly, **PSD of \(Z\) is not part of the present V4 PC carrier admission**. The PC-2 note itself says PSD preservation is a property of its projection but that general V4 structural increments need not be PSD. 

So this does not falsify the lossless lift.

Still, I pushed further: suppose we voluntarily strengthen the law and demand that a PSD source carrier remain PSD.

Even then, information loss is unnecessary.

---

# 7. A lossless PSD-preserving variant also exists

Let

$$
A=a+b,\qquad D=d+e.
$$

For a PSD source carrier,

$$
A\ge0,\qquad D\ge0,\qquad AD\ge4c^2.
$$

Keep the two within-sector blocks unchanged, but define target bridge couplings

$$
f
=
c\sqrt{\frac{A}{A+D}},
$$

$$
g
=
-c\sqrt{\frac{D}{A+D}},
$$

and bridge diagonal

$$
h
=
\frac{4c^2}{A+D},
$$

with the obvious zero definition when \(A+D=0\).

Then the nontrivial symmetric target sector is

$$
\begin{pmatrix}
A&0&\sqrt2 f\\
0&D&\sqrt2 g\\
\sqrt2 f&\sqrt2 g&h
\end{pmatrix}.
$$

Its Schur complement is exactly

$$
h-\frac{2f^2}{A}-\frac{2g^2}{D}=0.
$$

Therefore

$$
\boxed{Z_t\succeq0}.
$$

It is still injective because \(A,D\) are retained and the sign/magnitude of \(c\) are recoverable from \(f\) or \(g\).

And it does not enlarge the Frobenius norm. The newly introduced target contribution is

$$
4f^2+4g^2+h^2
=
4c^2+\frac{16c^4}{(A+D)^2}.
$$

Since

$$
AD\ge4c^2
$$

and

$$
(A+D)^2\ge4AD\ge16c^2,
$$

we obtain

$$
4f^2+4g^2+h^2
\le5c^2
<
8c^2,
$$

where \(8c^2\) was the source cross-sector contribution being replaced.

Thus

$$
\boxed{
\|Z_t\|_F\le\|Z_s\|_F.
}
$$

I pressure-tested this construction on **10,000 randomly generated decorated PSD source carriers** spanning strongly unequal sector magnitudes and correlations up to the PSD boundary. I found no PSD violation or Frobenius expansion.

For the actual current witness it gives approximately

$$
f=4.74759\times10^{-9},
$$

$$
g=-4.74281\times10^{-9},
$$

$$
h=2.94778\times10^{-12}.
$$

The target \(Z\) is PSD to numerical precision and its Frobenius norm is actually slightly *smaller* than the source's.

So even the strongest natural attempted rescue of the loss hypothesis fails:

$$
\boxed{
\textbf{requiring reachable/PSD carrier semantics still does not force memory loss.}
}
$$

The cost is that the PSD-preserving rule is nonlinear and gives the bridge a derived diagonal history as well as relational couplings.

---

# 8. Where a real no-go does appear

There **is** a genuine boundary, but it lies outside PC-1's exact decorated-sector domain.

If we allow a completely general source \(4\times4\) symmetric carrier, its \(U\)-\(V\) cross block contains four independent symmetry modes under the two within-sector swaps:

$$
(++),\quad(-+),\quad(+-),\quad(--).
$$

The target star-supported carrier has no \((--)\) representation: bridge-\(U\) couplings can carry the \(U\)-odd mode, bridge-\(V\) the \(V\)-odd mode, but there is no lawful star-supported coordinate transforming oddly under **both** sector swaps.

Therefore an equivariant injective transport of the entire unrestricted source carrier space into the target star-supported carrier space is impossible.

So:

$$
\boxed{
\textbf{generic lossless PC fission is not available without enlarging the target state.}
}
$$

But PC-1 explicitly assumes exact decorated sectors. On that invariant manifold all three nontrivial symmetry modes vanish, including the obstructed \((--)\) component. What remains is precisely the single trivial relational scalar \(c\), and that scalar can be carried losslessly.

This gives us a very clean scope boundary:

$$
\boxed{
\begin{array}{ll}
\text{exact decorated 2+2 PC domain} & \Rightarrow \text{lossless transport exists},\\[2mm]
\text{generic symmetry-breaking carrier} & \Rightarrow \text{loss may become unavoidable}.
\end{array}}
$$

---

# Revised PC-2 direction

I would now **HOLD/supersede** `pc_star_restriction_partial_loss_v1`.

The partial projection is still useful as:

* a legitimate explicit-loss control;
* the correct result when \(c=0\);
* potentially the necessary fallback outside the lossless domain.

But it should not be the selected law for the current PC-1 domain.

The next PC-2 certificate should pressure the lossless rule against these exact obligations:

1. prove the five-dimensional decorated source form and seven-dimensional target form;
2. implement the incidence-normalized \(c(Z)\);
3. transport same-sector blocks by signed lineage;
4. map \(c\) to bridge incidences;
5. prove exact target star support;
6. prove \(R_{\rm rel}L_{\rm rel}=I\);
7. prove exact Frobenius isometry;
8. exhaust signed edge permutations/orientations and child exchange;
9. apply to both actual current/reset carriers;
10. retain partial projection and whole reset as **negative/control alternatives**, not selected competitors by target performance;
11. include the generic \((--)\)-mode counterexample as the precise ceiling of lossless authority;
12. optionally retain the PSD-preserving nonlinear lift as a pressure control showing that PSD does not restore the loss necessity.

The most defensible constitutive principle now looks like:

> **Persistent structural history follows the surviving physical relation, not necessarily its old coordinates. A binary parent fission transports within-sector history along surviving edges and transfers the exact parent-mediated inter-sector history onto the new child-child bridge relation. Information is discarded only when no covariant target carrier exists for it.**

That gives PC a much more interesting meaning than “topology change causes a little memory erasure.”

For the domain we have actually established, it looks like:

$$
\boxed{
\textbf{topology changes the representation of memory without requiring its loss.}
}
$$

I would make that the candidate to falsify in the revised PC-2 evidence package before moving to PC-3.

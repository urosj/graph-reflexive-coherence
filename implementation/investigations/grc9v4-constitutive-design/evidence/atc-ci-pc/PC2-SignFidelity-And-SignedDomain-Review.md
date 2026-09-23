Yes—but in two different senses.

The **polarity should be resolved before PC-2 is accepted**. The **indefinite \(Z\)** should be resolved as a domain/semantics question, not automatically “fixed” into PSD.

For the polarity, the current package is correct that covariance alone leaves two maps: the checker explicitly finds the opposite polarity to be a distinct equally covariant isometry, and the certificate records that covariance does not fix it.   But I think we can do better than merely saying “choose \(+1\) constitutively.”

We already have an orientation-invariant physical scalar on the source,

$$
c_s=
\frac14
\sum_{i\in U,j\in V}
\sigma_i\sigma_jZ^s_{ij},
$$

and an equally orientation-invariant target relational readout,

$$
c_t=
\frac14
\sum_{i\in U\cup V}
\tau_i\tau_b^{X(i)}
Z^t_{\bar i b}.
$$

The current positive-polarity lift gives

$$
c_t=c_s,
$$

whereas the negative-polarity lift gives

$$
c_t=-c_s.
$$

So I would add an explicit **relational sign-fidelity condition**

$$
\boxed{c_t=c_s}
$$

to the PC carrier-continuation law.

That is stronger than covariance. It says that a retained signed historical relation is **continued**, rather than inverted, when its support changes from shared-parent coupling to bridge coupling. It is still a new cross-topology constitutive principle—ordinary V4 cannot force it—but it is no longer an arbitrary binary sign choice.

Then the statement in the note can change from:

> positive normalized polarity is selected as an extra choice

to essentially:

> the event preserves the incidence-normalized signed relational observable; this fixes the relational polarity.

That seems scientifically clean. The present note already comes very close to this by describing the \(+\) branch as `c_target=c_source`; it just stops one step short of making that equality the actual continuity obligation. 

---

The indefinite-\(Z\) issue is subtler.

The linear lossless lift provably makes the live target carrier indefinite whenever the transported bridge coupling is nonzero and the bridge diagonal is zero. The certificate retains this as an exact negative principal minor, not a numerical artifact.  The working note also correctly observes that nevertheless

$$
H=I+\frac34Z
$$

remains safely positive definite under the existing carrier-radius bound, and that the V4 structural space admits signed increments; \(Z\succeq0\) is not currently an admission requirement. 

So there is **no mathematical defect** in the present lift.

The real question is:

$$
\boxed{
\text{Must an event-transported PC carrier remain in the ordinary target-native PSD history cone?}
}
$$

I currently think the answer should be **no**, unless we adopt a stronger principle saying otherwise.

Why? Under ordinary PC evolution, starting from PSD \(Z\), the writer remains PSD because it averages PSD `Star(f)` sources. But after fission the target graph did not exist during that old history. The event is precisely translating history from one structural representation into another. There is no obvious requirement that the translated effective history be reproducible by having run the **target graph** ordinarily in the past.

What should remain lawful is:

$$
Z_t\ \text{symmetric and target-star supported},
$$

$$
\|Z_t\|_F\le1/3072,
$$

and, most importantly,

$$
H_t=I+\frac34Z_t\succ0.
$$

The present lossless lift satisfies all three, is invertible, and exactly preserves the declared Frobenius norm. 

So I would resolve this qualification by explicitly distinguishing two domains:

$$
\mathcal Z_{\rm ordinary,PSD}
\subset
\mathcal Z_{\rm PC,event},
$$

where ordinary evolution from the present initialization lies in the PSD subset, while lawful cross-topology event transport may land anywhere in the signed star-supported carrier ball for which \(H\) remains admitted.

Then PC-3 has a genuine obligation:

$$
\boxed{
\text{prove target PC continuation from this signed event-carrier domain.}
}
$$

The current note already states essentially that obligation: PC-3 must prove post-event dynamics in the signed ball and must not silently infer target historical realizability from the source. 

### Why I would not switch to the PSD lift yet

Your package already includes the important pressure result that PSD preservation does **not** force information loss: a nonlinear injective PSD-preserving map exists and is norm-nonexpansive. 

That is useful because it eliminates a false dilemma:

$$
\text{lossless}\not\Rightarrow\text{indefinite necessarily}.
$$

But choosing that map adds new physics:

* nonlinear dependence on \(A,D,c\);
* a nonzero derived bridge diagonal;
* a different distribution of the historical relational magnitude;
* loss of the simple linear/isometric relation-transport rule.

At present we have no independent reason to prefer those additions.

So I would retain the PSD-preserving version as a **predeclared pressure alternative**, not make it the main law merely because PSD feels nicer.

The selection hierarchy I would use is:

| Issue                                  | Resolution before PC-3                                                                                                              |
| -------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| Global relational polarity             | **Resolve now:** require \(c_t=c_s\)                                                                                                |
| Signed/indefinite \(Z_t\)              | **Resolve semantically:** explicitly admit signed event carriers when \(H_t\succ0\)                                                 |
| PSD preservation                       | **Not required by current PC law**; retain PSD-preserving lossless lift as a falsification/control alternative                      |
| PC target dynamics from signed \(Z_t\) | **Must be proved in PC-3**                                                                                                          |
| If signed event carrier fails PC-3     | Linear lift is falsified for this continuation problem; then test the already-preregistered PSD lift rather than tuning it post hoc |

So I would tighten PC-2 before adjudication, but **not by changing the main map yet**.

The revised PC-2 claim would be approximately:

$$
\boxed{
\begin{array}{l}
\text{On the exact decorated 2+2 PC domain, preserve the incidence-normalized}\\
\text{signed relational memory }c_t=c_s\text{ by transporting it onto bridge incidence.}\\
\text{The transport is linear, injective and Frobenius-isometric. Its event image}\\
\text{is the signed target-star carrier ball; PSD of }Z\text{ is not required, while}\\
H=I+\frac34Z\text{ must remain positive definite.}
\end{array}}
$$

That resolves the first qualification physically and turns the second from a lingering caveat into an **explicit domain statement with a PC-3 proof obligation**.

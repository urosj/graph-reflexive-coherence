> Relocation-only maintenance: repository paths and dependent identities were
> rebuilt before first commit. Scientific statements, numerical results and
> review verdicts are unchanged; the new identities are not an independent
> reviewer rerun. Earlier byte-preservation statements describe the pre-move stage.

This one is a **PASS for the fixed enabled Read-Back point**. It closes the two finite premises that were still open in my last review: rigorous source-side certification and rigorous entry of both actual target roles into the already-proved infinite-time return domain.

It does **not** close the proposed compact parameter box. That distinction is clean and should remain. 

## Verdict

The causal chain at

$$
\chi_A=\frac1{16},\qquad
\gamma=\frac1{1024},\qquad
\kappa_H=\kappa_{Ah}=1
$$

is now mathematically certified:

$$
\boxed{
\begin{aligned}
&\text{initial CAN-LSF guard inactive}\\
&\rightarrow\text{ordinary full-feedback beat admitted}\\
&\rightarrow\text{nonzero Read-Back + geometry consumed}\\
&\rightarrow\text{source guard/decomposition certified}\\
&\rightarrow k=30779\text{ uniquely certified}\\
&\rightarrow\text{funded source-selected fission}\\
&\rightarrow\text{current/reset target entries certified}\\
&\rightarrow\text{uniform infinite target theorem}.
\end{aligned}}
$$

The two relevant counterfactuals are also now mathematical rather than Decimal observations:

$$
\boxed{\text{no split}\rightarrow\text{negative resource proposal at attempt 10}}
$$

and

$$
\boxed{\text{history reset without split}\rightarrow
\text{negative resource proposal at attempt 7}.}
$$

Both rejecting attempts remain OS-residual admissible, so the observed obstruction is resource positivity rather than solver/admission failure. 

That is the point-level full causal chain we were missing.

---

## I independently reran the certifier's mathematical path

I executed the uploaded certifier's `kernel_checks()`, `symmetry_checks()` and complete `evidence()` path independently of its repository wrapper.

It reproduces:

$$
k=30779,
$$

no-split failure:

$$
n=10,
$$

history-reset-only failure:

$$
n=7,
$$

and certified first-entry for both current and reset.

The critical source margins reproduce as enclosed strictly positive quantities:

$$
W_v-W_u\approx0.01251979433,
$$

$$
\frac52(W_u+W_v)-\frac{19}{4}
\approx0.03075944195,
$$

$$
J_{\rm ref,min}\approx0.09934134680,
$$

$$
x\approx3.595265846,\qquad
y\approx0.004357297712.
$$

The dyadic grid coordinate lies approximately

$$
0.2665146771
$$

away from its nearest half-integer tie, so the integer enclosure really fixes one rounding outcome rather than merely reproducing a Decimal decision. 

Thus DB-10's **generic/native** issue remains, but the fixed-point decision itself is no longer numerically uncertain.

## The full-feedback nonvacuity is now certified too

The four quantities that previously existed only as high-precision diagnostics now all have strictly positive lower interval endpoints:

$$
\|J_{\rm ref}-b_0\|^2>0,
$$

$$
\|J_{\rm fresh}-J_{\rm ref}\|^2>0,
$$

$$
\|H^{[1]}-I\|_F^2>0,
$$

$$
\|\Delta\Phi_{\rm geom}\|^2>0.
$$

Their enclosed values agree with the preceding evidence:

$$
1.37797\times10^{-5},
\quad
9.28003\times10^{-8},
\quad
8.82516\times10^{-11},
\quad
2.25698\times10^{-8}.
$$

So this result can no longer be described as a zero-Read-Back or merely parameter-enabled witness. The reflexive correction is mathematically demonstrated to be present and consumed. 

---

## The interval machinery passes pressure

I reviewed the interval arithmetic rather than treating the resulting JSON as an oracle.

The representation

$$
[l/2^{256},u/2^{256}]
$$

uses outward integer operations. Division fails if zero lies in the denominator interval. Squaring correctly gives zero as the lower bound on intervals crossing zero. Square roots use integer `isqrt` with explicit outward endpoint tests. 

The exponential construction is also sound. For nonpositive \(x\), it range-reduces until \(t\le1/8\), brackets \(e^{-t}\) between the odd/even alternating Taylor sums, rounds outward once, and then squares outward back to the original exponent.

I additionally pressure-tested that helper at several nonzero negative arguments against high-precision transcendental evaluation, including

$$
-\frac1{2048},\quad-\frac18,\quad-\frac32,\quad-10,\quad-100,
$$

and every high-precision value lay inside its generated dyadic enclosure.

So:

$$
\boxed{\textbf{Outward arithmetic mechanism: PASS}}
$$

One minor evidence-hardening suggestion: the retained `kernel_checks()` only directly exercises `exp_nonpositive()` at zero. The proof and my independent checks support it, so this is not a scientific debt, but adding a few deterministic nonzero exponential kernel probes would make future regression evidence stronger.

---

## The symmetry treatment is correct

An especially good choice is that pair equality is **not inferred from overlapping intervals**.

Instead, the certificate relies on the exact automorphisms

$$
(0\ 1),\qquad(2\ 3)
$$

and equivariance of every staged operation. The interval execution then only needs to prove that the two invariant sectors remain **strictly distinct** at the event boundary. 

That avoids an otherwise serious trap: using numerical overlap as a surrogate for the exact response-sector relation on which CAN-LSF depends.

I accept:

$$
\boxed{\textbf{Exact sector invariance at this point: PASS}}
$$

without introducing any approximate-sector tolerance.

---

# The counterfactual obstruction is now a theorem for this trajectory

This is a meaningful upgrade over the preceding evidence.

For the enabled no-split trajectory, attempts 1–9 are positively admitted. On attempt 10 the enclosure of the minimum proposed resource is entirely negative:

$$
-0.23693
<
\min C_{\rm proposal}
<
-0.23691.
$$

There is no overlap with zero.

Likewise, starting from the live event state but resetting \(W=1\) without changing topology, attempts 1–6 are positive and attempt 7 has

$$
-0.16399
<
\min C_{\rm proposal}
<
-0.16397.
$$

The writer is not executed after either rejected resource proposal. 

This establishes the exact point-specific causal contrast:

$$
\boxed{
\text{changing history alone is insufficient; changing topology resolves the demonstrated obstruction.}
}
$$

It still does **not** prove that fission is the only physically possible remedy. CAN-LSF never needed that stronger claim.

---

# Both target roles now rigorously enter the infinite theorem

This was the other decisive missing piece.

For the actual current target, the first admitted full-feedback target beat gives

$$
\|C^+-\tfrac32\mathbf1\|^2
\approx0.25545282494<\frac49
$$

and

$$
\min C^+\approx1.356625422.
$$

For the independently retained reset,

$$
\|C^+-\tfrac32\mathbf1\|^2
\approx0.33111490363<\frac49
$$

and

$$
\min C^+\approx1.341005081.
$$

The interval certificate also proves every target \(W^+\) lies above

$$
e^{-1/8}
$$

and at most \(1\), hence

$$
-\frac18<\log W_e^+\le0.
$$



Therefore all hypotheses of the previously reviewed uniform return theorem now hold **mathematically**, not diagnostically.

Composition gives

$$
X_{n+1}\le
\frac{9209}{10240}X_n
$$

from that certified entry state onward, with

$$
\frac{9209}{10240}<0.9,
$$

all resources remaining above

$$
\frac56,
$$

history remaining admitted and tending toward \(W=1\), and the OS residual staying inside its proved bound. 

So I now accept:

$$
\boxed{\textbf{Indefinite full-feedback restoration at the fixed enabled point: PASS}}
$$

for **both** actual roles.

---

## One subtle distinction should remain explicit

The quantity

$$
\frac52(W_u+W_v)-a
$$

is still only the **old/source spectral guard**.

The point theorem does not magically make that guard a general full-feedback instability theorem.

What has now been proved is more specific and actually stronger for the point:

1. the source-selected guard is satisfied at this committed state;
2. ignoring the event and following the actual complete full-feedback OS map leads to certified resource rejection;
3. executing the uniquely prescribed CAN-LSF event leads both actual target roles into an indefinitely restorative domain.

That establishes **causal discrimination at this point** without claiming

$$
\text{guard}>0
\Longrightarrow
\text{full-feedback obstruction}
$$

for arbitrary states.

The documentation already states this correctly. 

---

# What this earns scientifically

I would now change the status from the previous review.

Before this certificate:

$$
\text{nonzero-feedback CAN-LSF point}
=
\text{strong finite evidence}.
$$

After this certificate:

$$
\boxed{
\text{nonzero-feedback CAN-LSF fixed point}
=
\textbf{certified mathematical causal-chain witness}.
}
$$

So a **second scoped adjudication is now justified**, provided it is explicitly restricted to this enabled point and the already-reviewed conditional target theorem.

What may now be carried forward includes:

* reference-stage source consumption remains valid at this nonzero point;
* genuine Read-Back and generated geometry are consumed;
* current-dependent \(W\) writing is active;
* exact response-sector symmetry survives the complete map;
* the source prescription is unique and source-only;
* the fixed point's no-split obstruction is certified;
* role-local target entry is certified;
* indefinite full-feedback restoration follows.

What must **not** yet be carried forward is:

$$
\boxed{\text{the whole Lift-2 parameter box}.}
$$

The certificate explicitly leaves

$$
\texttt{full\_parameter\_box\_source\_or\_entry\_certified=false}.
$$



---

## Evidence integrity

I independently recomputed the certificate canonical digest:

$$
\texttt{28a93f62eab7c99164708b87b15ee6569e60ad1be6119d564366139afe79fcc0}.
$$

The uploaded certifier SHA-256 is

$$
\texttt{920eabaf709bd6dca2600a011f1cbba41594b88ce9c6cdacd44c76dca86d584f},
$$

and the certification Markdown SHA-256 is

$$
\texttt{ee0fa83328e3b2352664af2836203abff9bb30cd0928e922537da63a7e74cb90},
$$

matching their retained bindings.  

I did not execute the repository-dependent `main()` wrapper because its predecessor/review paths are not mounted as a repository here. I did execute the complete new mathematical `evidence()` computation from the uploaded certifier itself.

## Final disposition

| Item                                                  | Verdict                      |
| ----------------------------------------------------- | ---------------------------- |
| 256-bit outward enclosure arithmetic                  | **PASS**                     |
| Nonzero Read-Back/geometry/history consumption        | **PASS, certified**          |
| Initial inactive → post-beat active source transition | **PASS**                     |
| Exact two-sector symmetry and strict separation       | **PASS**                     |
| Reference-stage source operand                        | **PASS at fixed point**      |
| Unique \(k=30779\) bin                                | **PASS, certified**          |
| Child funding                                         | **PASS**                     |
| Enabled no-split obstruction                          | **PASS at fixed trajectory** |
| Reset-without-split failure                           | **PASS at fixed trajectory** |
| Current target entry                                  | **PASS**                     |
| Independent reset target entry                        | **PASS**                     |
| Infinite full-feedback target continuation            | **PASS by composition**      |
| Full compact-box causal chain                         | **OPEN**                     |
| Generic guard ⇒ full-feedback obstruction             | **NOT CLAIMED / OPEN**       |
| Native execution / graph admission                    | **OPEN**                     |
| ATC-2                                                 | **OPEN**                     |

This is the result I was looking for after the previous review. **The fixed genuinely reflexive A_OS witness is now mathematically closed.**

The next scientific pressure should therefore move to the original Lift-2 compact box—specifically its **source and entry implications across all reachable dyadic bins**. There is no reason from this result to change CAN-LSF, its target, its source stage, or its partition rule.

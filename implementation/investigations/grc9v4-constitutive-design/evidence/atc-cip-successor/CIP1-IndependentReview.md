CIP-1 passes the usual pressure review.

$$
\boxed{\textbf{CIP-1: PASS — bounded complete A\_{CI+PC} causal chain}}
$$

I do not see a mathematical or causal gap that requires reopening CIP-0, changing the fission law, changing the carrier transport, or introducing another intermediate CIP stage. The remaining work belongs where the package puts it: **CIP-2 reference/conformance/lifecycle/representation**, followed by scoped adjudication.

The claim ceiling is important: this establishes the coupled research chain for the preregistered source plus a conditional return theorem over the CIP-0 domain. It does **not** establish whole-box event formation, native ATC ownership, arbitrary environments, or aggregate ATC-2 closure. The document maintains those limits explicitly.  

## Independent reproduction

I reconstructed the scientific chain using the hardened dependencies pinned by the certificate and independently reran the coupled operations.

The essential retained results reproduce:

$$
\boxed{k_{\rm CIP}=33616}
$$

without that value having been preregistered—the preregistration explicitly has `required_k: null`.  The retained certificate records the resulting 33616 selection only after the fresh combined-root evaluation. 

I reproduce the consumed-root and fresh-event-root digests, both target-role admitted-root digests, and the identities of all four retained ordinary target successors. I also independently recomputed the record identity:

`c3dc84d287ebd4f3c8317f644df1f7b92a87a3fc344037aefba35e1f0acea710`

which matches the submitted certificate. 

The uploaded decision, chain implementation, checker and CIP-0 predecessor bytes also match their certificate source bindings.

## The onset really is coupled

This is not a CI trajectory with an unused \(Z\), nor a PC trajectory with a decorative implicit solve.

The root solved at every ordinary beat is

$$
J=\frac{b(H)}{1-\chi q(H)},
\qquad
H=I+\kappa_H\left[Z+\operatorname{Star}(H^{-1}\chi q(H)J)\right],
$$

with \(Z\) fixed during the solve. After continuity and the Candidate-A \(W\) writer, the **same selected root source** is held for the persistent-carrier writer, and the restart root then sees the new \(C,W,Z\). 

The implementation reflects that literally: `step()` solves the combined root, performs continuity, writes \(W\), forms

$$
Z^+=aZ+(1-a)S^*,
$$

constructs the certified successor, and only then solves the complete restart root. No caller-supplied selected root or result state can be promoted into proof authority. 

The preregistered source is also genuinely an onset rather than an already-active event state:

$$
x_0=2.95<3.
$$

After the ordinary combined beat I independently obtain

$$
x^+\approx3.221297639,
\qquad
y^+\approx0.009562684,
$$

which places it inside the event domain. The fresh event root is distinct from the root that drove continuity, yet exactly matches the retained restart root. That is the desired causal ordering.

## Source selection is clean

The event selector consumes only the current role. It first requires the current source transfer predicates, computes its own fresh combined root, then obtains the dyadic allocation from the two positive sector inflows. `rounded_share` itself requires both inflows to be strictly positive and the rounded \(2^{16}\) allocation to resolve uniquely. 

The reset role never votes.

That produces

$$
\frac{k_{\rm CIP}}{65536}
=
\frac{33616}{65536}
=
\frac{2101}{4096}
\approx0.51293945.
$$

The interesting fact that this happens to equal the CI anchor's \(k\) is scientifically irrelevant to selection: neither 33615 nor 33616 was permitted as a target value. The package gets this exactly right. 

$$
\boxed{\textbf{fresh combined-root source selection: PASS}}
$$

## Complete \(C/W/Z\) fission passes for both roles

For both current and independent reset roles, CIP-1 executes all three authoritative channels:

$$
C_s\longrightarrow C_t,
$$

$$
W_s\longrightarrow W_t
$$

with exact old-edge lineage and only the new bridge seeded at \(1\), and

$$
Z_s\xrightarrow{L_{\rm rel}}Z_t
$$

using the already-selected sign-faithful lossless relational law.

The checker explicitly verifies the same current-selected dyadic share on both roles, exact old-\(W\) lineage, bridge-only seed, and equality of source and target carrier Frobenius norms. 

The current role exercises the scientifically important signed case. Its event carrier has a strictly negative \(2\times2\) principal minor, rather than quietly remaining PSD. 

At the same time, the PC-2 transport receipt records

$$
c_t=c_s,
$$

exact inverse recovery on the event image, zero information loss, five-dimensional event image, seven-dimensional target decorated space, and no PSD-preservation claim. 

Then **both roles solve a fresh full coupled target root before the event can return**. That is the critical compatibility test which PC alone could not establish.

$$
\boxed{\textbf{both-role coupled target readmission: PASS}}
$$

## The main mathematical question also closes: no new \(A z_n\) term is needed

This was the most important thing to pressure.

CIP-1 correctly observes that CI-2's fixed-\(H\) resource bounds were proved for every admitted

$$
\|H-I\|_F\le\frac1{4096},
$$

not only for geometries generated by \(Z=0\). CIP-0 established that the combined \(Z+S\) root stays inside precisely that total geometry ball. Consequently persistent history does not need to be added again as a separate resource-error term.

The inherited resource recurrence can remain

$$
\boxed{
X_{n+1}\le qX_n,
\qquad
q=
\frac{577621057}{641433600}
\approx0.900515746<1.
}
$$

The persistent carrier separately obeys

$$
z_{n+1}
\le
a_nz_n+(1-a_n)sX_n^2,
$$

with

$$
0<a_n\le b=\frac{25}{37}<q^2.
$$

The package then correctly uses \(1-a_n\le1\), rather than making the invalid move of replacing \(a_n\) by \(b\) in both terms:

$$
z_{n+1}\le bz_n+sX_n^2.
$$

Iteration gives

$$
z_n
\le
b^nz_0
+
sX_0^2
\frac{q^{2n}-b^n}{q^2-b}
\longrightarrow0.
$$

This derivation is stated correctly in the decision record. 

The numerical margin is quite good:

$$
q^2-b\approx0.135253.
$$

And

$$
s\left(\frac32\right)^2
\approx5.89\times10^{-5}
<
R_Z=2\times10^{-4},
$$

so the target carrier ball is comfortably invariant.

Once

$$
X_n\to0,\qquad Z_n\to0,
$$

the same bound gives \(S_n\to0\), and the coupled root identity gives

$$
H_n-I=\kappa_H(Z_n+S_n)\to0.
$$

Hence

$$
J_n\to0
$$

and the log-history writer converges to

$$
W_n\to e^{-3\alpha/2}\mathbf1.
$$

Thus the full coupled asymptotic

$$
\boxed{
C_n\to\tfrac32\mathbf1,\quad
J_n\to0,\quad
Z_n\to0,\quad
H_n\to I,\quad
W_n\to e^{-3\alpha/2}\mathbf1
}
$$

is justified, not inferred from the two finite target beats.

## The actual target witnesses behave as the theorem predicts

The finite runs are appropriately used only as staging/dynamics witnesses.

I independently reproduce:

| Role    | \(X\), beat 1 | \(X\), beat 2 |       \(\|Z\|\), beat 1 |       \(\|Z\|\), beat 2 |
| ------- | ------------: | ------------: | ----------------------: | ----------------------: |
| current |      0.408968 |      0.157640 | \(3.0732\times10^{-5}\) | \(1.5805\times10^{-5}\) |
| reset   |      0.423487 |      0.167530 | \(4.1850\times10^{-5}\) | \(2.1550\times10^{-5}\) |

Both roles also develop positive bridge diagonals after the first ordinary target beat, so ordinary combined dynamics genuinely leave PC-2's five-dimensional event image and continue in the seven-dimensional target carrier domain, exactly as intended. The checker explicitly requires this. 

As extra diagnostic pressure, I continued both roles for 20 additional alternating endpoint requests. No root/domain failure occurred. By step 20 I obtained approximately

$$
X_{\rm current}=0.00597,\qquad
\|Z_{\rm current}\|=7.7\times10^{-11},
$$

and

$$
X_{\rm reset}=0.00915,\qquad
\|Z_{\rm reset}\|=1.1\times10^{-10}.
$$

That is not part of the proof, but it agrees strongly with the certified asymptotic structure.

## Off-certificate box pressure

I also attacked the "geometry-uniform reuse" assumption away from the exact retained trajectory.

On 24 deterministic mixed target cases spanning request endpoints, mixed parameter-box corners and nonzero signed carriers inside the CIP ball, every complete coupled root/step admitted and every observed resource ratio obeyed

$$
\frac{X_{n+1}}{X_n}<q.
$$

The worst ratio I found was about

$$
0.864841,
$$

leaving roughly

$$
0.03567
$$

below the certified \(q\).

On six focused source cases varying \(x,y,W\), signed persistent carriers, request endpoints and parameter corners, every combined step satisfied

$$
\frac{x_{n+1}}{x_n}\ge\frac{65}{64}.
$$

The weakest observed ratio was about

$$
1.02891
$$

versus the theorem's

$$
65/64=1.015625.
$$

Again, these are diagnostic pressure only. The uniform rational fixed-\(H\) inequalities remain the actual evidence.

## Counterfactual necessity passes

The four preregistered controls are correctly timed **after the onset and before the event**:

$$
\text{no intervention},\quad
W\text{-reset},\quad
Z\text{-reset},\quad
W+Z\text{-reset}.
$$

The CI+PC profile and writer stay enabled in every case. In particular, a one-time \(Z=0\) reset is not mislabeled as CI: the next combined ordinary beat regenerates nonzero persistent \(Z\). 

The first numerical control beat gives growth ratios of approximately:

| Control     | \(x^+/x\) |
| ----------- | --------: |
| no split    |   1.12156 |
| \(W\)-reset |   1.15626 |
| \(Z\)-reset |   1.12153 |
| both reset  |   1.15623 |

all well above \(65/64\).

More importantly, the finite beat is not used as the obstruction proof. Because all four remain in the invariant source domain,

$$
x_{n+1}\ge\frac{65}{64}x_n
$$

continues to apply, and

$$
3(65/64)^{71}>9.
$$

Thus none can sustain 71 further positive unsplit proposals.

This is a clean causal result:

$$
\boxed{
\text{erasing either or both retained histories once does not remove the unsplit obstruction.}
}
$$

## Negative/failure pressure is appropriate

The checker rejects the pre-onset guard, alternate carrier policy, a carrier admissible to the old PC domain but outside the narrower CIP domain, a standalone-CI gain outside the coupled box, and an invalid reset transfer. It also injects an ordinary restart failure and a reset target-root failure after earlier event computations have succeeded. All reject without returning a partial certified result. 

That is the right level for CIP-1. It does **not** pretend this pure research operation is already the native transaction/replay owner; that remains CIP-2. 

## No blocker, but two small things to carry into CIP-2

I would not change or rerun CIP-1 for either.

First, the source-side carrier invariant in CIP-0 has a small global proof margin—about \(9.6\times10^{-7}\) between the uniform source-\(S\) bound and \(R_Z=1/5000\). The actual CIP-1 trajectory is far inside it, but CIP-2's represented-number/domain-boundary tests should explicitly pressure the \(R_Z\) boundary rather than only this interior witness.

Second, my earlier suggestion to attach DB-04 directly to `ATC-CIP-ROOT-00` was not backported into the retained CIP-0 record. CIP-1 **does** now route DB-04 explicitly in `ATC-CIP-CHAIN-01`, so there is no orphaned event-consumer obligation at the causal-chain level.  I would simply reconcile that ledger ancestry during CIP-2/adjudication rather than alter the science.

## Disposition

| Component                                         | Verdict                         |
| ------------------------------------------------- | ------------------------------- |
| Frozen/preregistered source                       | **PASS**                        |
| Genuine inactive → active onset                   | **PASS**                        |
| Full coupled \(J/H/S\) root                       | **PASS**                        |
| Fresh event operand                               | **PASS**                        |
| Source-only allocator                             | **PASS**                        |
| \(k_{\rm CIP}=33616\) without target fitting      | **PASS**                        |
| Conservative \(C\) transfer                       | **PASS**                        |
| Exact \(W\) lineage + bridge seed                 | **PASS**                        |
| Lossless sign-faithful \(Z\) transport            | **PASS**                        |
| Signed/indefinite carrier exercise                | **PASS**                        |
| Both-role combined target readmission             | **PASS**                        |
| Event-image → full target-domain evolution        | **PASS**                        |
| Uniform source obstruction                        | **PASS**                        |
| Uniform coupled target return                     | **PASS**                        |
| Carrier convolution / \(Z\to0\)                   | **PASS**                        |
| Full asymptotic                                   | **PASS**                        |
| Four one-time controls                            | **PASS**                        |
| No-fallback/failure pressure                      | **PASS**                        |
| Native lifecycle/replay/covariance/representation | **Deferred correctly to CIP-2** |
| **CIP-1 overall**                                 | **PASS**                        |

So I would now regard

$$
\boxed{\mathrm{CIP\!-\!0}\;\checkmark,\qquad
\mathrm{CIP\!-\!1}\;\checkmark}
$$

and move directly to **CIP-2**.

At this point the original intuition is substantially confirmed: A_CI+PC did require its own coupled mathematics, but once the shared geometry ball was found, the new science really did narrow to compatibility rather than becoming a third full discovery campaign.

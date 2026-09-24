The scientific result is strong.

$$
\boxed{\textbf{CI-1: PASS — bounded complete causal anchor}}
$$

$$
\boxed{\textbf{PC-1: PASS — bounded evolving-carrier obstruction + support screen}}
$$

I would, however, separate that from one **provenance HOLD before formal adjudication**: several source hashes in the new anchor certificate no longer match the frozen A_OS proof-script hashes retained through G7. That does not undermine the mathematics—I can reproduce the new payload using the earlier accepted kernels—but the dependency lineage should be reconciled before this becomes an accepted record.

## Independent reproduction

I executed the new research module in an isolated repository-shaped environment using the uploaded A_OS kernels. The generated `uniform_bounds`, inherited algebra block, complete `CI_1`, and complete `PC_1` objects are exactly equal to the corresponding retained certificate payloads.

The certificate canonical digest independently recomputes to

$$
\texttt{70386c47cc86d29f14fe69b2e6c80ebafb0cb1bd00dc4b2a7c28bff3ecbf2ac1},
$$

and the profile digest to

$$
\texttt{88620d22a0a3663f76d51ecfb79249cedde397dd94a6a058cd3a06ad7f27c97b}.
$$

Those match the retained record. 

I also independently reconstructed the initial CI fixed point with a separate dense numerical implementation of the full fixed-geometry A equations and the CI \(H\mapsto T(H)\) map. Its selected \(H\) agrees with the interval certificate midpoint to below \(4\times10^{-22}\) componentwise and its \(J\) to roughly \(2\times10^{-15}\). That is only an independent numerical cross-check—the Banach bounds remain the proof—but it gives no indication that the interval root is enclosing the wrong branch.

The previous CI-0 review issue has also been fixed properly: the revised checker now compares the entire fresh `CandidateCIRoot`, selected geometry and certificate, and retains a canonical joint-root digest; it no longer treats current equality alone as sufficient. The PC injected failure is also now realization-specific.  

---

# CI-1

This is substantially more than a compatibility result. It is already a complete bounded ATC causal witness for CI.

### The CI root theorem passes

The declared source and target geometry neighborhoods use

$$
\rho=\frac1{4096}.
$$

The proof bounds the fixed-geometry baseline response and then proves that

$$
T(H)=I+\frac34\operatorname{Star}(f(H))
$$

is both a strict self-map and contraction.

For the source:

$$
\|T(H)-I\|_F
\le
8.37489\times10^{-5}
<
2.44141\times10^{-4}=\rho,
$$

with contraction factor bounded by

$$
L_{\rm src}<0.001753.
$$

For the target:

$$
\|T(H)-I\|_F
\le
2.48190\times10^{-5},
$$

with

$$
L_{\rm tgt}<0.000290.
$$

The underlying exact rational values are retained in the certificate. 

That is an excellent margin. It does not rely on “the iteration converged,” because the iteration is only used to localize the root after the a priori contraction theorem has already established existence and uniqueness. The final enclosure uses the residual bound

$$
\frac{\|T(H_n)-H_n\|}{1-L}.
$$

The note also correctly addresses branch regularity: the fixed-\(H\) current block is regular, the reduced \(H\) block has inverse bounded by \(1/(1-L)\), and the reference-connected branch persists as the coupling is reduced to zero. 

So DB-05, which was inactive for A_OS, is genuinely exercised here rather than silently inherited.

$$
\boxed{\textbf{CI root existence / uniqueness / regularity: PASS}}
$$

### Exact sector symmetry is earned, not numerically assumed

The CI root domain is invariant under the decorated pair swaps. Because the root inside that domain is unique, the exact root must be equivariant under those swaps. Only after that theorem does the interval implementation intersect paired enclosures.

That is the correct logical order:

$$
\text{equivariance + unique root}
\Longrightarrow
\text{exact root symmetry},
$$

not

$$
\text{overlapping numerical intervals}
\Longrightarrow
\text{physical symmetry}.
$$

The note is explicit about this distinction. 

---

## The CI unsplit obstruction passes

The source theorem is now genuinely CI-native because it bounds the actual selected CI root current, not an OS reference current or OS corrector.

The retained bound is

$$
x^+
\ge
\left(1+\delta_{\rm CI}\right)x
$$

with

$$
\delta_{\rm CI}
=
\frac{23484949}{1283276800}
\approx0.01830077
>
\frac1{60}.
$$

Therefore every successful positive proposal satisfies the simpler certified inequality

$$
\boxed{x^+\ge\frac{61}{60}x}.
$$

And

$$
3\left(\frac{61}{60}\right)^{67}>9,
$$

so positive unsplit continuation cannot survive all 67 subsequent proposals. The writer remains in \(W\in[24/25,1]\), the CI root remains admitted, and failure is therefore a **resource-continuation obstruction rather than root-solver failure**. 

The same theorem includes \(W=1\), so history reset alone cannot solve the obstruction.

I also put finite pressure around the lower cone boundary rather than only rerunning the supplied anchor. For twelve CI states near

$$
x=3.001
$$

with \(y\in\{-1,0,1\}\) and sector weights near both ends of the admitted interval, all admitted one-step contrast multipliers were above approximately

$$
1.03298,
$$

comfortably stronger than \(61/60\approx1.01667\). That is diagnostic only, but agrees with the uniform theorem.

$$
\boxed{\textbf{CI evolving-history unsplit obstruction: PASS}}
$$

---

# The CI event law is actually realization-native

This is one of the best features of the result.

The prestate starts below the event threshold:

$$
x=\frac{59}{20}=2.95<3.
$$

One complete CI ordinary beat reaches

$$
x\approx3.221091,
$$

and the **fresh poststate joint root** supplies event activity. 

More importantly, the old A_OS baseline-balance test fails:

$$
\frac{|b_u-b_v|}{b_u+b_v}
\approx0.025997
>
\frac1{64}.
$$

The result keeps this failure instead of modifying the fixture to preserve the OS rule. The CI law instead uses positive inward **joint-root currents**, whose ratio directly resolves the dyadic allocation. 

That is strong evidence we are actually deriving CI physics rather than relabeling CAN-LSF/OS.

The source-selected result is

$$
\boxed{k=33616},
$$

hence

$$
\lambda
=
\frac{33616}{65536}
=
\frac{2101}{4096}
\approx0.51293945.
$$



No target data enter this selection.

I independently checked the two-role funding margins at that exact selected share. Their lower bounds are approximately:

$$
\begin{array}{c|cc}
&u\text{-child}&v\text{-child}\\
\hline
\text{current}&1.07973&0.98558\\
\text{reset}&1.15245&1.00755
\end{array}
$$

so funding is nowhere near marginal.

$$
\boxed{\textbf{CI source-only prescription and funding: PASS}}
$$

---

## Operation support passes

The causal obstruction is still carried by the high-stiffness four-contact parent organization. The source has the familiar lower support condition

$$
5m>\frac{19}{4}
$$

while the split double-star has the certified upper spectral bound

$$
\lambda_{\max}\le\frac{73}{16}
<
\frac{19}{4}.
$$

The CI root/Read-Back/geometry terms have already been enclosed as perturbations around this constitutive support.

So this is not the failed critical-mode situation in which the operation left the actual unstable support untouched.

$$
\boxed{\textbf{CI operation-support screen: PASS}}
$$

---

# CI target restoration passes strongly

Both actual roles are transferred with the same source-selected \(k\), old \(W\) follows lineage, and only the bridge is initialized at \(W=1\). Each transferred target has its own certified CI root before the first target beat and another certified root after that beat. 

The actual first-step return radii are:

$$
X_{\rm current}<0.408905,
$$

$$
X_{\rm reset}<0.423467,
$$

both comfortably inside

$$
\frac23.
$$

The uniform theorem is stronger than these two fixture values. It gives first-entry upper bound

$$
X^+
<
\frac{47675553}{78970880}
\approx0.603711
<
\frac23,
$$

and repeated CI steps satisfy

$$
X_{n+1}
\le
q_{\rm CI}X_n,
$$

with

$$
q_{\rm CI}
=
\frac{7072159}{7897088}
\approx0.8955401
<
0.9.
$$

The margin to \(0.9\) is about \(0.00446\), substantially healthier than the narrowest A_OS G6 margin. 

Resources remain above

$$
\frac56,
$$

\(W\) stays in the admitted interval, every subsequent CI root remains unique, and the history limit is correctly shifted to

$$
W\to e^{-3\alpha/2}.
$$



Therefore the complete bounded chain now exists:

$$
\boxed{
\begin{array}{c}
\text{ordinary CI onset}\\
\downarrow\\
\text{fresh unique poststate root}\\
\downarrow\\
\text{CI-native source allocation}\\
\downarrow\\
\text{supported binary fission}\\
\downarrow\\
\text{both-role target CI roots}\\
\downarrow\\
\text{indefinite CI continuation}
\end{array}}
$$

with no-split and \(W\)-reset-only controls.

That meets the declared CI-1 milestone. 

$$
\boxed{\textbf{CI-1 scientific disposition: PASS}}
$$

The ceiling is exactly what the note says: this is a fixed-profile, paired-star, \(h=1/8\) anchor—not yet CI-2's consolidated domain/request/generalization theorem or CI-3's independent executable conformance. 

---

# PC-1

PC-1 also passes, but its milestone is deliberately different.

It does **not** claim a complete PC topology rule yet.

Its job was:

$$
\text{evolving }W,Z
\rightarrow
\text{unsplit obstruction}
\rightarrow
\text{exact decorated sectors}
\rightarrow
\text{operation-support screen}.
$$

That is what the evidence establishes.

## The evolving carrier proof passes

The carrier domain is

$$
\|Z\|_F\le\frac1{3072}.
$$

Because

$$
H=I+\frac34Z,
$$

this places every PC fixed-geometry read inside the same geometry neighborhood

$$
\|H-I\|_F\le\frac1{4096}.
$$

The selected fixed-\(H\) source produces a structural source satisfying

$$
\|S\|_F
<
1.11666\times10^{-4}
<
\frac1{3072}.
$$

At the preregistered PC relaxation time,

$$
\tau_{\rm PC}
=
\frac1{8\log2},
$$

and \(h=1/8\), the actual held-source writer is

$$
Z^+
=
\frac12Z+\frac12S.
$$

So the carrier ball is convexly invariant. This is actual PC carrier evolution—not a frozen-\(Z\) approximation. 

The same resource-growth theorem then applies at every successful PC beat:

$$
x^+\ge\frac{61}{60}x,
$$

while \(W\) and \(Z\) both remain in their invariant domains.

Thus no-split PC continuation fails, and so do all three history controls:

$$
W\text{-reset only},
$$

$$
Z\text{-reset only},
$$

$$
W+Z\text{-reset}.
$$

The certificate explicitly retains all four source reads in the invariant cone. 

I also pressured several symmetric carrier states near the declared carrier radius. Their actual one-step contrast multipliers were about \(1.088\)–\(1.096\), again comfortably above the uniform \(61/60\) lower theorem. This is diagnostic support, not the proof.

$$
\boxed{\textbf{PC full evolving-}W/Z\textbf{ source obstruction: PASS}}
$$

---

## Exact PC sectors survive carrier evolution

This matters because in PC, \(Z\) itself is decoration.

The supplied initial carrier is symmetric, the full fixed-geometry A read is equivariant under the two within-sector swaps, `Star(f)` preserves those actions, and

$$
Z^+=\frac12(Z+S)
$$

therefore preserves them as well.

I independently checked the retained \(Z_{\rm postbeat}\) interval matrix under both edge permutations

$$
(0\,1),\qquad(2\,3),
$$

and every corresponding interval endpoint is identical.

So the poststate really does still have two exact decorated edge sectors.

However, I would harden the **research function interface** here: `pc_read()` currently checks the carrier norm but does not itself reject an asymmetric/non-star-supported \(Z\), while downstream `paired_enclosures()` relies on proved symmetry. For the supplied anchor this is sound because every carrier is generated from the symmetric construction, but before PC-2/PC-3 accepts broader inputs I would make the symmetry/star-support premise executable rather than comment-level. 

That is not a PC-1 failure.

---

# PC operation support passes

This is the right place to apply the lesson from the failed A_OS critical-mode branch.

The obstruction persists throughout the small carrier ball, including \(Z=0\). Therefore it is not generated solely by the persistent carrier.

The resource/stiffness source is the four-contact parent structure itself. Binary sector fission modifies exactly that incidence support. The target's base double-star spectrum has

$$
\lambda_{\max}\le\frac{73}{16}<\frac{19}{4}.
$$

Thus the allowed operation acts on the support that produces the obstruction. 

That is enough for the **support screen**.

It is intentionally **not yet a target-restoration theorem**, because we still do not know the lawful disposition of \(Z\) across the topology event.

$$
\boxed{\textbf{PC operation-support screen: PASS}}
$$

---

# And PC-1 discovers exactly why PC-2 is real science

The postbeat carrier contains a strictly positive cross-sector component

$$
Z_{02}\approx6.71073\times10^{-9}.
$$

Before fission, edges \(e_0\) and \(e_2\) share the original parent, so such a star-supported coupling is lawful.

After fission, those two old edges terminate on different children and no longer share a target vertex.

Therefore “copy the old \(4\times4\) carrier into the target and append a bridge row/column” would preserve a structural coupling that is **not in the target's star-supported carrier space**. 

This is an excellent negative result because it rules out the easiest but physically unjustified PC implementation.

It means PC-2 really must decide between something like

$$
Z_{\rm target}
=
L_{K4,\rm evt}(Z_{\rm source})
$$

with a derived covariant structural map, or

$$
Z_{\rm target}=0
$$

with explicit carrier loss.

And the result has not biased that decision by testing which target behaves better. The certificate keeps:

* `carrier_event_law_selected=false`;
* `target_restoration_claimed=false`.



That is exactly correct.

$$
\boxed{\textbf{PC-1 scientific disposition: PASS}}
$$

---

# Two hardening items

Neither overturns the mathematics, but I would address both before scoped adjudication.

### 1. Explicit domain enforcement

`source_check()` currently relies on the fact that its callers originate from an exactly paired construction; it checks \(x\) and \(W\), but does not itself verify exact charge/pairing. Likewise `pc_read()` checks the \(Z\) radius but not decorated symmetry/star support.  

That is fine for these **fixed anchors**, because their ancestry proves those properties.

For CI-2 and especially PC-2, I would make those premises explicit executable admissions:

$$
C_0=C_1,\quad C_2=C_3,
$$

$$
W_0=W_1,\quad W_2=W_3,
$$

exact \(Q=9\), and for PC

$$
QZQ^\top=Z
$$

for the decorated-sector generators plus target/source star support.

Otherwise a future arbitrary caller could enter the helper with an asymmetric state and then reach `paired_enclosures()`, which is only valid after the symmetry theorem.

This is a **domain-interface hardening**, not a theorem defect.

### 2. Source-binding provenance needs reconciliation

This one should be fixed before acceptance.

The new anchor certificate binds several inherited A_OS scripts to hashes different from the hashes retained in the reviewed G7 reference.

For example, G7 bound:

* `certify_atc_sector_channels.py` →
  `034fe630...`
* `certify_atc_sector_state_domain.py` →
  `629d3295...`
* `certify_atc_sector_readback_point.py` →
  `86373eb2...`



The new anchor certificate instead binds those same paths as:

* channels → `8d0aa701...`
* state-domain → `19b88f77...`
* point → `920eabaf...`

while the readback-box hash remains unchanged. 

This conflicts with the working note's statement that the accepted A_OS scientific artifacts remain unchanged. 

Importantly, I reproduced the entire CI-1/PC-1 mathematical payload using the **earlier retained A_OS versions**, and it matches the new certificate exactly. So I see no evidence of a mathematical regression.

But the provenance needs one of two resolutions:

* restore/bind the frozen accepted versions; or
* explicitly declare successor versions and provide a bounded diff showing that changes do not alter the imported mathematics used here.

Until then I would call the **scientific result PASS but the final evidence package not yet cleanly adjudicable**.

---

## Claim/debt pressure

For CI, I think the result now supplies bounded research evidence for essentially every scientific item attached to CI-1:

* DB-02: realization-native guard;
* DB-05: branch uniqueness/regularity;
* DB-06: declared norms;
* DB-07: genuine unsplit obstruction;
* DB-08: operation acts on obstruction support;
* DB-14/16: explicit target and both-role admission;
* DB-19: indefinite return;
* DB-26: actual A_CI family support.

The record conservatively keeps `local_debt_discharge=false`, which is appropriate until adjudication. 

For PC, the source-side items now have strong evidence:

* DB-02/07: evolving-carrier obstruction;
* DB-08: support screen;
* part of DB-15: persistent carrier meaning and explicit evidence that naive transfer is invalid.

But DB-15's **event map**, DB-14/16 target construction/readmission, and DB-19 restoration correctly remain the PC-2/PC-3 frontier. The record already represents that accurately. 

## Final disposition

| Gate                             | Verdict                 | Remaining issue                                  |
| -------------------------------- | ----------------------- | ------------------------------------------------ |
| CI-0 hardening                   | **PASS**                | none scientific                                  |
| CI root theorem                  | **PASS**                | fixed profile/domain only                        |
| CI exact sectors                 | **PASS**                | make domain admission explicit for CI-2          |
| CI unsplit obstruction           | **PASS**                | fixed \(h=1/8\)                                  |
| CI-native source prescription    | **PASS**                | fixed anchor/general guard consolidation in CI-2 |
| CI operation support             | **PASS**                | —                                                |
| CI both-role transfer/root entry | **PASS**                | —                                                |
| CI indefinite return             | **PASS**                | —                                                |
| **CI-1**                         | **PASS**                | proceed to CI-2                                  |
| PC evolving \(W,Z\) cone         | **PASS**                | fixed profile/carrier ball                       |
| PC no-split/reset controls       | **PASS**                | —                                                |
| PC exact decorated sectors       | **PASS**                | add explicit \(Z\)-symmetry admission            |
| PC operation-support screen      | **PASS**                | —                                                |
| Naive \(Z\) copy                 | **REFUTED**             | productive negative result                       |
| PC carrier event law             | **OPEN by design**      | PC-2                                             |
| PC target restoration            | **OPEN by design**      | PC-3                                             |
| **PC-1**                         | **PASS**                | proceed to PC-2                                  |
| Package provenance               | **HOLD for correction** | inherited A_OS hash mismatch                     |

So scientifically:

$$
\boxed{\textbf{CI-1 PASS}}
\qquad
\boxed{\textbf{PC-1 PASS}}
$$

and the path has compressed exactly as hoped. CI already has a complete bounded realization-native ATC anchor after essentially one major derivation step. PC has reached the one genuinely new constitutive question that OS and CI could not answer for it:

$$
\boxed{\textbf{what does persistent structural memory }Z_4\textbf{ mean across fission?}}
$$

That is now the right PC-2 problem; I would not spend another step searching for a different PC obstruction or partition mechanism.

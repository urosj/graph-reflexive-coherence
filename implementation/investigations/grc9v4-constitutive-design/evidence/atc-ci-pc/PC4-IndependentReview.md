PC-4 passes.

$$
\boxed{\textbf{PC-4: PASS — bounded paired-domain / reference / representation closure}}
$$

I do not see a scientific reason to hold it or rerun it before scoped adjudication. The important qualifier is that this closes the **declared paired A_PC research scope**, not active-environment transport, formal source admission, repeated-event/non-Zeno behavior, or native implementation.

### Independent reproduction

I rebuilt the PC-4 execution chain and reran the submitted reference checker. The reproduced **contract, profile identity, and complete evidence payload are exactly equal** to `ATCPC4ReferenceCertificate.json`: the whole-box bounds, all 1,645 Decimal-oracle scalar comparisons, lifecycle sequence and negative pressure, eight represented continuation steps, and environmental scope all match.

I also independently recomputed the certificate's canonical record digest:

`0a1369d4bdfa1edbf44f757c0ef0fcc25b5af5398c14d119075170407975cc91`

and it matches the retained record.

The contract itself is disciplined: it freezes the relational lossless carrier law with \(c_t=c_s\), request interval \([3/25,1/8]\), fixed \(\tau_A=\tau_{\rm PC}=1/(8\log2)\), a fixed profile chosen from the declared box, paired graphs only, a four-step represented schedule, and explicitly no native authority or active-environment transport claim. 

One reproduction detail remains the already-known provenance issue rather than a new PC-4 issue: the older raw copies of three G7 proof scripts available in the conversation have the pre-relocation hashes, whereas the current retained chain uses the accepted relocated hashes. The CI-1/PC-1 resolution already pins those accepted versions at commit `5e1a63a`.  The new PC-4 files themselves—checker, reference, working note, and PC-3 certificate—match the hashes declared by the PC-4 record.

## 1. The whole-box theorem survives pressure

This is the main scientific gain over PC-3.

PC-4 proves one simultaneous envelope over

$$
\alpha,\beta\in[1/4096,1/2048],
$$

$$
\gamma\in[1/2048,1/1024],\qquad
\chi\in[1/32,1/16],
$$

$$
\kappa_H,\kappa_{Ah}\in[1/2,1],
$$

with the declared potential class and every request

$$
h\in[3/25,1/8].
$$

The certificate retains the complete rational bounds rather than deriving the conclusion from parameter samples. 

The margins are healthy.

For the source,

$$
g=
\frac{14682197}{1002240000}
\approx0.01464938
>
\frac1{80}=0.0125,
$$

so the uniform claimed multiplier

$$
\boxed{x^+\ge\frac{81}{80}x}
$$

has a nontrivial margin of about \(2.15\times10^{-3}\). Since

$$
3(81/80)^{89}>9,
$$

unsplit positive continuation cannot survive all 89 further proposals. This is now uniform over the enlarged request and parameter domain rather than the PC-3 point profile. 

The carrier bounds are also comfortably inside

$$
R=\frac1{3072}.
$$

Numerically, from the retained exact fractions:

$$
\|S_{\rm source}\|_F
<1.9960\times10^{-4},
$$

leaving roughly \(1.26\times10^{-4}\) before the carrier radius, while the target entry bound is only

$$
5.8943\times10^{-5}.
$$

The read/W-writer exponent budgets likewise remain well below \(1-M=1/25\). 

So there is no "barely positive inequality" problem here.

## 2. Variable-request target return closes

The widened first-entry theorem is

$$
X_{\rm first}
<
\frac{8086615}{12828672}
\approx0.6303548
<
\frac23.
$$

That leaves about \(0.03631\) of radius margin.

The repeated target factor is

$$
q=
\frac{433407199}{481075200}
\approx0.9009136
<
0.91.
$$

So PC-4 is slightly weaker than the fixed-profile PC-3 \(q<0.9\), as expected from enlarging both the parameter and request domains, but still has about \(9.09\times10^{-3}\) margin below its declared \(0.91\) ceiling. 

I also checked the carrier/resource coupling rather than treating the two bounds independently. With

$$
d(h)=2^{-8h},
$$

the proof uses the uniform

$$
d(h)<b=\frac{25}{37}.
$$

And

$$
q^2-b\approx0.13597>0.
$$

Hence

$$
z_n
\le
b^n z_0+
sX_0^2\frac{q^{2n}-b^n}{q^2-b}
\longrightarrow0.
$$

This is enough for the complete asymptotic statement

$$
C\to\frac32\mathbf1,\qquad
J\to0,\qquad
Z\to0,\qquad
H\to I,\qquad
W\to e^{-3\alpha/2}.
$$

The working note explicitly derives this from the uniform recurrence, not from a finite continuation. 

$$
\boxed{\textbf{PC-4 variable-request indefinite-return theorem: PASS}}
$$

## 3. The reference evaluator has the right staging

The PC-4 reference is not using the PC-3 half-step shortcut for arbitrary \(h\).

Its actual step is:

$$
(C,W,Z)
\stackrel{\text{old }Z}{\longrightarrow}
J,S
\longrightarrow
C^+
\longrightarrow
D(C^+)
\longrightarrow
W^+
\longrightarrow
Z^+=d(h)Z+[1-d(h)]S
\longrightarrow
\text{fresh read}(C^+,W^+,Z^+).
$$

The implementation uses the selected pre-continuity current for the W writer, rebuilds the descriptor at post-resource \(C\), and uses the **held pre-continuity \(S\)** for the PC writer. 

The checker directly discriminates all three common staging errors:

* stale descriptor;
* poststate/restart \(J\) substituted into the W writer;
* newly recomputed poststate \(S\) substituted into the carrier writer.

All are numerically distinguished from the correct stage on both roles and both request endpoints. 

That is particularly important because PC's science depends on the old-carrier / held-source ordering.

## 4. Independent oracle pressure is strong

The second evaluator is meaningfully independent.

It uses 110-digit `Decimal`, assembles:

* WLS descriptors edge-locally;
* conductance directly;
* the Hodge/current system through its own dense elimination;
* structural source explicitly;
* continuity;
* log-space W writing;
* held-source \(Z\) writing;
* fresh restart read.

It does not call the research evaluator's scientific stages. 

The retained result contains

$$
\boxed{1645}
$$

scalar enclosure comparisons, including:

* the source beat;
* current/reset targets at both \(h=3/25\) and \(1/8\);
* low and high full-parameter-box corners on a signed carrier.

Every independent Decimal value lies inside the outward interval result.  

I added off-certificate pressure as well. I tested 18 deterministic **mixed** parameter corners—not just the all-low/all-high corners—at both request endpoints on the signed target stress state: 36 additional target cases.

Results:

* 0 resource-domain failures;
* 0 carrier-domain failures;
* 0 W-history failures;
* worst observed one-step \(X\) ratio \(\approx0.78650\), comfortably below the analytic uniform \(q\).

I separately ran the same 18 mixed corners at both request endpoints through the source onset. All 36 entered the event region and all 36 produced a resolved source-only share, with

$$
33597\le k\le33623.
$$

That latter result is **diagnostic only**—the theorem does not claim that every possible event state/profile automatically resolves a share—but it gives useful off-certificate pressure against the chosen box.

## 5. Lifecycle/replay is substantive, not digest-only

The bounded owner executes:

$$
\text{ordinary source}
\to
\text{split}
\to
\text{ordinary target}
\to
\text{reset}.
$$

Reset remains independent during ordinary steps; after reset, current is the independently transported target reset \(C/W/Z\).

Replay reconstructs the operations rather than accepting a digest chain. The retained negative pressure has 15 cases, including:

* missing source lineage;
* changed request;
* forged reset \(Z\);
* invalid edge lineage;
* wrong profile;
* reset outside transfer domain;
* injected failure after current-role target readmission but before reset-role completion;
* late event and ordinary publication failure;
* requests outside the declared interval;
* second/descendant fission;
* fabricated raw exact-state witness;
* unresolved allocator.

All are rejected, with rollback where publication had not completed. 

I particularly like the injected reset-readmission failure: it prevents a current-role success from partially publishing an event before the independent reset role has passed.

$$
\boxed{\textbf{PC-4 bounded transaction/replay/rollback: PASS}}
$$

## 6. The represented-number bridge is correctly modest

The representation result is appropriately scoped.

It rounds \(C,W,Z\) only at publication, propagates the rounded state into the next step, uses represented \(h\) and the separately pinned binary64 \(\tau\), and does **not** manufacture an exact-charge witness for a rounded state. The record explicitly says intermediate arithmetic is not being claimed as binary64 and there is no infinite numerical-conformance theorem. 

Across the eight retained continuation steps, I independently obtain maximum errors of approximately:

| role    |                    \(C\) |                    \(W\) |                    \(Z\) |
| ------- | -----------------------: | -----------------------: | -----------------------: |
| current | \(2.7132\times10^{-16}\) | \(4.4349\times10^{-17}\) | \(9.6851\times10^{-22}\) |
| reset   | \(1.8549\times10^{-16}\) | \(5.2806\times10^{-17}\) | \(1.2392\times10^{-21}\) |

against the preregistered

$$
10^{-10}
$$

budget.

The maximum observed charge discrepancy is

$$
\frac1{2251799813685248}
\approx4.44\times10^{-16},
$$

and, correctly, it is **retained rather than repaired**.

$$
\boxed{\textbf{finite represented-error bridge: PASS}}
$$

## Two scope points I would make explicit in adjudication

I don't see either as a correction requiring a new PC-4 run.

First, `whole_box_theorem=true` should continue to mean:

> uniform source obstruction, carrier invariance, transfer-entry/return and asymptotic bounds for the declared box **conditional on an admitted event state with a resolved source-only share**.

It must not be shortened to “every source state/profile in the box autonomously forms an event.” The assumption inventory already says unresolved/out-of-range allocation rejects, and calls the event region a sufficient admitted domain. 

My mixed-corner pressure finding that the fixed witness resolves in all 36 extra cases should not be promoted into such a theorem.

Second, keep the distinction:

$$
\boxed{\text{C}^{1}\text{ potential class = analytic theorem}}
$$

versus

$$
\boxed{\text{quadratic subclass = executable PC-4 reference/oracle}}.
$$

The contract already makes that distinction correctly. 

---

## Environmental pressure

I agree with the current ceiling.

PC-4 does **not** pretend that the paired carrier lift already extends to active external edges. The record says explicitly that active external-edge transport is outside the contract and no numerical environment campaign is claimed. It retains only the unaffected-support result: a disjoint block-diagonal unsplit component remains autonomous and its obstruction cannot be repaired by fission elsewhere. 

That is the correct outcome. Trying to "complete" PC-4 by naively resizing \(Z\) into the earlier A_OS embedded graph would undo the discipline we just established in PC-2.

So active environmental PC transport remains a **future extension**, not a PC-4 defect.

## Debt/claim disposition

Scientifically, PC-4 now adds bounded support for the pieces that PC-3 deliberately left open:

* **DB-10** — finite represented-number bridge;
* **DB-21** — bounded atomic research transaction / rollback / replay;
* **DB-23** — executable research-reference evidence;
* **DB-28** — finite deterministic resolution/work surface;

while broadening the previously established A_PC source/transfer/target/return evidence across the positive parameter and request box.

The record correctly keeps `local_debt_discharge=false` and routes formal admission, active-environment carrier extension, other families, repeated-event/non-Zeno, and native implementation forward. 

I would also continue to keep **DB-24/source admission** explicitly open. PC-4 gives us the scientific/reference evidence needed for adjudication; it is not itself source/forensic admission.

### Final disposition

| PC-4 component                           | Verdict                    |
| ---------------------------------------- | -------------------------- |
| Parameter-box theorem                    | **PASS**                   |
| Request interval \([3/25,1/8]\)          | **PASS**                   |
| Source obstruction with evolving \(W,Z\) | **PASS**                   |
| Signed carrier invariance                | **PASS**                   |
| Variable-request first target entry      | **PASS**                   |
| Uniform indefinite target return         | **PASS**                   |
| \(Z\to0,\ H\to I\) asymptotic            | **PASS**                   |
| \(W\to e^{-3\alpha/2}\)                  | **PASS**                   |
| PC-3 carrier policy preserved            | **PASS**                   |
| Independent full-step Decimal oracle     | **PASS**                   |
| Stage mutation discrimination            | **PASS**                   |
| Research owner / replay / rollback       | **PASS**                   |
| Finite represented-error bridge          | **PASS**                   |
| Active coupled environment               | **Open by explicit scope** |
| Native ATC                               | **Open by explicit scope** |
| Formal scoped admission                  | **Open**                   |

Therefore:

$$
\boxed{\textbf{PC-4 PASS}}
$$

and I would consider the **A_PC paired research derivation complete enough for formal scoped claim/debt adjudication**. I would not add another PC-5 discovery stage before that.

That leaves the parallel A-side scientific work exactly where we expected: **CI-2 and CI-3** remain the unfinished realization-native pieces; A_PC has now reached its consolidation/reference endpoint.

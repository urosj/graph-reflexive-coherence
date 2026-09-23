I found one real conformance gap, but no corresponding failure in the CI-2 mathematics.

My disposition is:

$$
\boxed{\textbf{CI-2: PASS}}
$$

$$
\boxed{\textbf{CI-3 mathematical/reference core: PASS}}
$$

but

$$
\boxed{\textbf{CI-3 full domain-conformance closure: HOLD for one boundary-admission fix}}
$$

The hold is narrow: **CI-2 declares closed exact domains, while CI-3's interval implementation excludes some exact states lying exactly on those boundaries.** Everything exercised by the retained CI-1 witness and the CI-3 numerical/reference campaign lies comfortably inside the domain, so I do not see a need to redo the physics or the root derivation.

## Independent reproduction

I independently reran the CI-2 certificate. Its complete mathematical `evidence` payload and claim routing reproduced exactly. The retained self-digest also recomputes correctly:

`a25873b7792acc09d8446226562857de5548ca6e357bcbd1fbc178320822d4e6`.

For CI-3, the full monolithic checker exceeds the execution window here, so I split it into its substantive components. The complete stage campaign reproduced **exactly**, including all

$$
\boxed{2153}
$$

independent scalar comparisons and \(k=33616\); the covariance result reproduced exactly; all eight finite-representation steps reproduced their retained C/W/J/H errors exactly; and the ordinary → split → ordinary → reset lifecycle plus physical replay reproduced the retained final identity

`9599c459bd2977d69fb5232d7b1d0a801be5c6c4653c8c3e4c863bf16dc76cfb`.

I also independently executed the two most consequential atomicity injections: failure of the reset target root after the current target had passed, and failure of the final root during an ordinary beat. Both leave the previous publication unchanged, as intended. The retained CI-3 record itself has a valid self-digest:

`3ee8192cd1c951f51eff85ce42d8bb6d8cf00ac537ff00a353e00ec3d9d44c5b`.

The certificate explicitly remains non-native and non-admitted. 

---

# CI-2 mathematics

I do not find a gap in the joint-root construction.

The widened parameter box is genuinely handled before iteration: the source and target root certificates use the worst \(\chi,\gamma,\kappa_H,\kappa_{Ah}\), the conductance/history invariant is proved first, and only then is Banach invoked. The certificate retains both the self-map displacement and contraction constants, plus the current-block and reduced-block inverse bounds. 

The useful margins are:

$$
\rho=\frac1{4096}\approx2.4414\times10^{-4}.
$$

Source:

$$
\|T(H)-I\|<1.9904\times10^{-4},
$$

$$
\operatorname{Lip}(T)<0.006012.
$$

Target:

$$
\|T(H)-I\|<5.8896\times10^{-5},
$$

$$
\operatorname{Lip}(T)<0.000975.
$$

So neither root theorem is marginal.

The regularity argument also looks legitimate. Since the fixed-current block has inverse bound \(1/d\), and the reduced \(H\) residual has derivative inverse bounded by

$$
\frac1{1-L},
$$

the Schur-complement argument gives local regularity of the **joint** \((J,H)\) root rather than merely convergence of one Picard sequence. The document correctly declines to classify roots outside the certified ball. 

I also agree with the reference-connected-branch argument. Extending the mathematical homotopy in \(\kappa_H\) down to zero does not silently add a zero-coupling runtime profile; the uniform contraction simply identifies which branch is being continued. 

## Source obstruction is sound

The widened bound is

$$
x^+\ge (1+g)x,
\qquad
g=
\frac{16152197}{1002240000}
\approx0.01611610.
$$

That is genuinely above

$$
\frac1{64}=0.015625
$$

by about \(4.91\times10^{-4}\).

Thus the simpler certified recurrence

$$
x^+\ge\frac{65}{64}x
$$

holds, and

$$
3\left(\frac{65}{64}\right)^{71}
\approx9.01969>9.
$$

So the 71-proposal contradiction is sound and is a resource-positivity obstruction, not a solver failure. 

As additional diagnostic pressure, I independently sampled 3,000 interior source states over random admissible parameters and \(h\in[3/25,1/8]\). The weakest actual one-step contrast multiplier I encountered was about

$$
1.03083,
$$

well above \(65/64\approx1.015625\).

That is not proof—the rational theorem is—but it did not expose a hidden bad corner.

## Transfer/return theorem also survives

The CI-2 transfer derivation correctly turns the source event box and dyadic interval into

$$
|t|\le\frac25,\qquad
|y|\le\frac1{50},\qquad
|\epsilon|\le\frac{23}{320}.
$$

Its first-entry theorem yields

$$
X_{\rm first}
<
\frac{10771945}{17104896}
\approx0.629758
<
\frac23,
$$

leaving roughly \(0.03691\) radius margin. 

The recurrent factor is

$$
q=
\frac{577621057}{641433600}
\approx0.90051575
<
0.91,
$$

leaving about \(9.48\times10^{-3}\) to the declared ceiling. 

I independently sampled 5,000 paired target states in the return ball over random admissible profiles and requests. The largest actual one-step ratio I encountered was about

$$
0.8840.
$$

I also sampled 3,000 transfer states over the event box/share range; the largest first-step target radius was about \(0.5073\), versus the certified \(0.6298\).

Again: diagnostics only, but useful pressure.

The asymptotic reasoning is also complete: \(X_n\to0\), the root equation gives \(H-I=O(X^2)\), therefore \(H\to I\), then \(J\to0\), while the uniformly contractive log-history writer has target \(e^{-3\alpha/2}\). 

### CI-2 scope is disciplined

Crucially, it does **not** pretend to prove event formation over the whole box. The certificate explicitly says `whole_box_event_formation=false` and conditions the theorem on an admitted event with a resolved source-only share.  

So:

$$
\boxed{\textbf{CI-2 mathematical disposition: PASS}}
$$

---

# CI-3 scientific staging

This part is quite strong.

The numerical root is not being substituted for the Banach proof. `raw_root()` first imports the CI-2 certificate, iterates only inside the certified neighborhood, obtains

$$
\epsilon_{\rm root}
=
\frac{\|T(H_c)-H_c\|}{1-L},
$$

and then constructs an outward root enclosure. It separately verifies that the literal current and geometry residuals enclose zero. 

The stop criterion is computational only:

$$
\max(10^{-35},1000\times\text{input width}),
$$

not a convergence-derived existence criterion. That distinction is correct.

The complete root identity includes state/profile/certificate identity, \(H\), generated \(H\), current/read data and residual information. The checker explicitly corrupts \(H\) while leaving \(J\) unchanged and requires the comparison to fail.  

That closes the concern we had at CI-0 about accidentally treating “joint root” as merely “current.”

## The independent oracle is meaningfully independent

It does not import the reference evaluator. It independently assembles WLS descriptors, incidence action, conductance, the dense solve, readback, Star source, fixed-point root, continuity and log writer at 110-digit Decimal precision. It even starts its root iteration from a nonidentity geometry. 

Its convergence is correctly described only as an independent numerical diagnostic; existence and uniqueness continue to come from CI-2. 

The retained campaign includes source onset, both actual target roles at both request endpoints, two preregistered parameter corners, and stage-mutation discrimination. 

## Covariance pressure passes

The transformed full target changes:

* vertex labels,
* edge ordering,
* edge orientations,

and compares both \(J\) and \(H\), not merely a scalar outcome. The certificate retains 30 transformed joint-\(J/H\) comparisons with independent-oracle residual around \(5.27\times10^{-104}\). 

That is correctly scoped as one full-graph representation pressure, not arbitrary-template admission.

## Lifecycle/replay logic is sound

The bounded owner executes:

$$
\text{ordinary source}
\to
\text{zero-time event}
\to
\text{ordinary target}
\to
\text{reset}.
$$

Both target roots are admitted before event publication. Ordinary steps preserve the independent reset. Replay reexecutes the physics rather than trusting digests. 

The retained negative roster has 21 cases, including stale state/profile root use, forged joint-root identity, wrong W lineage, reset-root failure after current-role success, ordinary final-root failure, out-of-domain requests and unresolved allocation. 

I independently reran the two most important atomicity cases and both passed.

## Finite representation also looks correct

The represented experiment does not store geometry; it reconstructs the joint root from rounded \(C/W\). It propagates the previous rounded publication rather than restarting from exact state every beat, keeps exact and represented \(h/\tau\) distinct, and never grants an exact-charge witness to the rounded state. 

My independent split rerun reproduced every retained error exactly. Across the eight steps the maxima are approximately

$$
\begin{array}{c|c}
C & 2.07\times10^{-16}\\
W & 8.03\times10^{-17}\\
J & 3.42\times10^{-16}\\
H & 7.45\times10^{-23}
\end{array}
$$

against the declared \(10^{-10}\) budget.

Maximum observed charge drift is

$$
\frac1{2251799813685248}
\approx4.44\times10^{-16},
$$

and it is retained rather than repaired.

So none of that is where I would hold CI-3.

---

# The real gap: closed mathematical domain vs executable interval admission

CI-2 explicitly declares:

$$
x\ge\frac{29}{10},
\qquad
W\in\left[\frac{24}{25},1\right]
$$

for the source root, and

$$
3\le x\le\frac72,
\qquad
0\le y\le\frac1{50}
$$

for the current event. The target likewise allows \(W=24/25\). 

These are **closed exact mathematical domains**.

But CI-3 delegates source and target admission to the interval-backed domain machinery. `root()` calls `source_check()`/`target_check()`, while `select()` derives \(x,y\) from outward intervals and tests their interval endpoints.  

The inherited exact constructor does verify exact rational charge and pairing **before** interval conversion, but the later inequality checks use the outward intervals rather than the exact input witness.

That creates a reproducible boundary mismatch.

I constructed exact rational states satisfying the stated CI-2 contract and obtained:

* exact \(x=29/10\), interior \(W\): `root()` rejects with **`source contrast domain`**;
* exact \(W=24/25\), otherwise interior source: rejects with **`source history interval`**;
* exact event \(x=3,\ y=0\): event selection rejects because the outward \(x\) interval dips below \(3\) and the outward \(y\) interval straddles zero;
* exact \(y=1/50\): upper interval endpoint exceeds \(1/50\), so the event is rejected;
* exact \(x=7/2\): upper interval endpoint exceeds \(7/2\), so the event is rejected;
* target \(W=24/25\): target root admission rejects with **`target history interval`**.

The reason is deterministic. For a non-dyadic exact rational such as

$$
\frac{24}{25},
$$

the outward \(2^{-256}\)-grid interval has

$$
W_{\rm lo}<\frac{24}{25}<W_{\rm hi}.
$$

The code then asks

$$
W_{\rm lo}\ge\frac{24}{25},
$$

which is false even though the **exact input value** equals the allowed boundary.

Likewise, subtracting outward intervals representing equal exact quantities gives something like

$$
y\in[-2^{-256},2^{-256}]
$$

rather than the exact witnessed fact \(y=0\).

This is not floating-point noise. It is a mismatch between:

$$
\boxed{\text{exact closed theorem domain}}
$$

and

$$
\boxed{\text{interval-certified executable interior}}.
$$

### Why this matters

The actual CI-1 witness is comfortably interior, as are all retained CI-3 runs. Therefore:

$$
\boxed{\text{none of the positive CI evidence is invalidated}.}
$$

But CI-3 currently embeds the CI-2 domain contract unchanged, so it appears to claim executable coverage of those closed boundaries. 

That exact claim is presently false.

I would correct it before calling CI-3 closed.

---

# How I would fix it

I would **not shrink the mathematics** merely to accommodate interval bookkeeping.

The clean solution is to distinguish:

$$
\mathcal D_{\rm CI2}^{\rm exact}
$$

from

$$
\mathcal D_{\rm CI3}^{\rm certified}.
$$

Ideally the constructive domain witness should retain/prove the exact scalar predicates that matter:

$$
x,\quad y,\quad W_{\min},\quad Q,\quad\text{pairing},
$$

rather than deriving all of them later from outward boxes.

For exact rational input, use the exact values already available before interval conversion. For states produced by certified operations, propagate the relevant domain facts as proof/witness metadata when the operation theorem establishes them.

Then the interval arrays remain numerical enclosures while the **domain predicate** remains an exact/certified mathematical fact.

That is consistent with the architecture already used for exact charge and exact pairing.

The weaker but acceptable alternative is to explicitly declare:

> The CI-3 executable reference is a conservative certified subset of the closed CI-2 mathematical domain. Boundary cases whose outward enclosures straddle a predicate boundary fail closed.

If you choose that route, CI-3 should stop implying complete executable coverage of the closed CI-2 domain.

I prefer the first solution because the project already distinguishes physical exact facts from numerical enclosure overlap.

---

# One smaller interface hardening

`raw_root()` intentionally permits non-exact-charge target states for the represented diagnostic. That is good. 

But `advance_raw()` subsequently applies the inherited paired-enclosure intersection when updating \(C\) and \(W\). 

For the actual representation experiment this is sound: rounded states originate from exactly paired roles and binary64 projection preserves equality of the paired coordinates.

Still, I would make that ancestry explicit at the represented interface:

$$
C_0=C_1,\quad C_2=C_3,
\qquad
W_0=W_1,\quad W_2=W_3
$$

before invoking a symmetry-based enclosure intersection.

That prevents a future caller from supplying arbitrary overlapping interval pairs and having intersection look like a proof of symmetry.

I classify this as **hardening**, not a current evidence defect.

---

# Things I specifically do *not* think are gaps

Several apparent concerns are already handled correctly:

* CI-2 does not prove whole-box event formation.
* The two executable parameter corners do not masquerade as proof of the continuous box.
* The C1 potential envelope and executable quadratic subclass are kept distinct.
* The numerical root is not used as the existence theorem.
* Roots outside the declared ball are not ruled out.
* The zero-\(\kappa_H\) homotopy is branch identification, not a runtime profile claim.
* The represented target root is allowed without exact charge, while the exact-charge return theorem is explicitly not transferred to it.
* Active external environments remain outside scope.
* Native ATC and DB-24/source admission remain open.  

## Verdict

| Item                                            | Verdict                                               |
| ----------------------------------------------- | ----------------------------------------------------- |
| CI-2 uniform root theorem                       | **PASS**                                              |
| CI-2 joint-root regularity                      | **PASS**                                              |
| CI-2 source obstruction                         | **PASS**                                              |
| CI-2 transfer/first entry                       | **PASS**                                              |
| CI-2 variable-request return                    | **PASS**                                              |
| CI-2 asymptotics                                | **PASS**                                              |
| CI-2 claim ceiling                              | **PASS**                                              |
| CI-3 complete joint-root semantics              | **PASS**                                              |
| Independent Decimal oracle                      | **PASS**                                              |
| Stage/order discrimination                      | **PASS**                                              |
| J/H covariance pressure                         | **PASS**                                              |
| Both-role target roots                          | **PASS**                                              |
| Lifecycle/replay/atomicity                      | **PASS**                                              |
| Finite C/W/J/H representation bridge            | **PASS**                                              |
| CI-2 closed-domain ↔ CI-3 admission equivalence | **FAIL / fix required**                               |
| Represented symmetry precondition               | **Harden**                                            |
| **CI-2 overall**                                | **PASS**                                              |
| **CI-3 overall**                                | **HOLD narrowly for domain-admission reconciliation** |

So I would **close CI-2 scientifically now**.

For CI-3 I would make one small successor correction rather than another scientific stage: fix or explicitly narrow the exact-boundary admission semantics, add boundary-pressure cases for \(x=29/10\), \(x=3\), \(x=7/2\), \(y=0\), \(y=1/50\), and \(W=24/25\), rerun the same reference certificate, and then adjudicate CI-3. There is no evidence here that the CI topology law, root theorem, or return physics need reopening.

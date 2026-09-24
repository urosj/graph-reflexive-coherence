> Relocation-only maintenance: repository paths and dependent identities were
> rebuilt before first commit. Scientific statements, numerical results and
> review verdicts are unchanged; the new identities are not an independent
> reviewer rerun. Earlier byte-preservation statements describe the pre-move stage.

The right disposition is:

$$
\boxed{\textbf{G7-R: PASS}}
$$

but

$$
\boxed{\textbf{G7-N / original native G7: still OPEN}}
$$

So this is a successful executable-reference and conformance milestone, not yet native autonomous topology change.

The package keeps that distinction correctly. G7-R is explicitly investigation-local, does not import or modify `src/`, and does not claim native profile/event ownership or K0 integration. 

## Independent execution

I reconstructed the uploaded reference/checker in an isolated repository-shaped environment and executed the substantive new paths directly.

The eight full-stage point checks reproduce exactly:

$$
97+97+124+124+153+153+184+184
=
1116
$$

independent scalar comparisons.

They cover both source and target graph classes at

$$
h=\frac18,\qquad h=\frac3{25},
$$

and every retained point-check row matches the supplied record exactly. Both deliberately wrong writer-stage substitutions are rejected in all eight cases.  

The local lifecycle tests also reproduce:

$$
k_{\rm paired}=32775,
\qquad
k_{\rm embedded}=31897.
$$

For each graph I reproduced all twelve negative-control outcomes, old-history lineage, bridge-only seeding, split→step→reset behavior, event replay, and whole-publication rollback. The source controls independently reproduce rejection at:

$$
\begin{array}{c|cc}
&\text{no split}&\text{history reset only}\\
\hline
\text{paired}&9&8\\
\text{embedded}&6&6
\end{array}
$$

with the rejecting resource proposal occurring before the writer. 

I also added one pressure not retained in the submitted campaign: I executed the entire split and event-replay path at the **lower G6 endpoint**

$$
h=\frac3{25}.
$$

Both graph classes retain the same source-selected \(k\) and replay to exactly the same research publication identity. So the event wrapper itself is not accidentally tied to \(h=1/8\).

---

# Full-graph evaluator: PASS

The most important implementation fact is that `atc_sector_reference.py` really does implement the full staged graph equations. It does not take the G1/G2 paired quotient formulas and dress them as an executable model.

For each graph it independently constructs:

$$
B,\quad L_W,\quad D(C),\quad p(C),
$$

then the reference baseline/current,

$$
b_0,\qquad J_{\rm ref},
$$

the generated geometry

$$
H=I+\kappa_H S,
$$

the fresh stage

$$
J_{\rm fresh},
$$

continuity,

$$
C^+=C-hBJ_{\rm fresh},
$$

and finally rebuilds

$$
D(C^+)
$$

before forming the writer drive and applying the \(h\)-dependent log interpolation. 

The sequencing is correct.

In particular, the writer does **not** reuse either:

* the source descriptor instead of \(D(C^+)\), or
* \(J_{\rm ref}\) instead of \(J_{\rm fresh}\).

The independent Decimal evaluator assembles the graph edge-by-edge rather than calling the reference `read()` or `evaluate()` path, and all 1,116 compared scalar quantities fall inside the outward intervals. 

So:

$$
\boxed{\textbf{Full staged A\_OS executable reference: PASS}}
$$

for the selected concrete G5/G6 research profile.

A useful scope point: the executable chooses one concrete nonlinear potential

$$
p(c)=\frac{19}{4}c+\frac{c^2}{131072}
$$

and one interior parameter tuple. That is completely appropriate for conformance testing; it does **not** replace the broader accepted \(C^1\) theorem. The package says this correctly. 

---

# Source selection and event construction: PASS

The event path remains cleanly source-only.

The exact source preimage is required; interval overlap is not allowed to masquerade as exact charge or exact sector symmetry. The allocator consumes the recomputed **reference selected current**, not a previous current, fresh current, or target outcome. 

The dyadic resolver also fails closed. It only admits \(k\) if the complete current enclosure resolves to one round-even cell. An unresolved interval produces no target.

The transfer then uses exactly one \(k\) for both actual roles, while independently transporting their own resources and histories. For the embedded graph, the edge-lineage reindexing is explicitly verified:

$$
0\to0,\quad1\to1,\quad2\to2,\quad3\to3,\quad4\to5,\quad5\to6,
$$

while target edge \(4\) is solely the newly seeded bridge. 

That is the correct interpretation of lineage preservation; it is not pretending endpoint identity is unchanged.

Both children inherit the parent host coordinate through the bound target graph profile.

So:

$$
\boxed{\textbf{Source prescription / transfer / lineage conformance: PASS}}.
$$

---

# Both-role transaction behavior: PASS

The local owner has the right atomicity shape.

It computes:

$$
\text{source selection}
\rightarrow
\text{current transfer}
\rightarrow
\text{reset transfer}
\rightarrow
\text{current readmission}
\rightarrow
\text{reset readmission}
$$

before assigning the new publication pointer.

The injected reset-readmission failure proves that current admission alone is insufficient. The injected late failure proves that even failure after both readmissions does not publish the candidate. 

Reset semantics are also right: after

$$
\text{split}\rightarrow\text{ordinary step}\rightarrow\text{reset},
$$

the current becomes the actual transported reset from the topology event, rather than source reset, event current, or a regenerated default.

Replay reconstructs the physical event rather than trusting a digest. Forged profile, parent lineage, edge mapping, reset history, or request provenance are rejected when replayed. 

This earns:

$$
\boxed{\textbf{Bounded research lifecycle/replay conformance: PASS}}.
$$

It is still not a production receipt/security system, which the note explicitly avoids claiming.

---

# Represented-error bridge: PASS for exactly its stated meaning

I pressure this part separately because numerical evidence is very easy to overstate.

The scheme being tested is precisely:

$$
\boxed{
\text{exact-input enclosed stage}
\rightarrow
\text{uniquely rounded binary64 }C,W\text{ publication}
}
$$

at every beat.

It is **not** pretending to model binary64 rounding after every multiplication, solve, exponential, geometry construction, etc. That distinction is explicit and correct. 

I independently reran the complete sixteen-step **paired-current** and **embedded-current** continuation comparisons. Every retained step row matches the supplied record exactly, including:

* exact/represented state images,
* represented \(h\),
* represented \(\tau\),
* exact and represented stage digests,
* error envelopes,
* and charge discrepancy.

The largest errors reported over all four retained runs are approximately

$$
\max\|C_{\rm exact}-C_{64}\|_\infty
=
4.064\times10^{-16},
$$

$$
\max\|W_{\rm exact}-W_{64}\|_\infty
=
8.278\times10^{-17}.
$$

Both are far below the declared finite comparison ceiling \(10^{-10}\). 

But the more scientifically valuable observation is the negative one:

$$
\boxed{\text{independent binary64 publication does not conserve charge exactly}.}
$$

The largest retained discrepancy is

$$
\frac{11}{5629499534213120}
\approx1.95\times10^{-15}.
$$

That is not normalized away. 

This is exactly the correct conclusion:

$$
\boxed{\textbf{finite represented-error bridge: PASS}}
$$

but

$$
\boxed{\textbf{exact represented conservation: NOT ESTABLISHED}}.
$$

And therefore:

$$
\boxed{\textbf{infinite binary64 continuation theorem: NOT ESTABLISHED}}.
$$

That boundary is handled correctly.

---

## One wording/identity issue I would tighten before G7-R adjudication

I do see one small but important semantic precision point.

The note says the research profile preimage binds “all physical and computational operands.” The profile hash does indeed bind the graphs, host coordinates, potential and constitutive parameters, \(\tau\), and numerical recipe labels. 

But `PROFILE_ID` by itself does **not** bind the complete event semantics:

* reference-stage source consumption,
* dyadic allocator definition,
* source-domain predicates,
* sector-to-site transfer law,
* history-lineage recipe,
* target readmission semantics,
* transaction/replay contract.

Those are currently bound by the **source code hashes and outer conformance record**, not by `PROFILE_ID` alone.

That is perfectly adequate for G7-R.

I would only change the prose to something like:

> “The profile preimage binds all evaluator/profile operands; the G7-R event and lifecycle contract is additionally bound by the implementation/checker source identities and conformance record.”

For G7-N, the normative profile/contract identity should either contain or explicitly reference those event semantics.

I would classify this as:

$$
\boxed{\textbf{wording/authority hardening, not a review blocker}}.
$$

---

# Why this still does not close native G7

The package is disciplined about this, and I agree with its boundary.

Three major things remain genuinely different from G7-R.

First, **event formation and K0 scheduling are absent**. The wrapper begins from retained exact-rational states that are already admitted as event-boundary sources. An ordinary source step does not manufacture a new exact `source_exact` object and there is no autonomous successful-boundary dispatcher. 

So this proves:

$$
\text{event-boundary conformance}
$$

not

$$
\text{ordinary evolution}\rightarrow\text{native autonomous dispatch}.
$$

Second, **production numerical semantics remain undefined**. The current publication-only scheme is an excellent oracle, but native code either needs to adopt an explicitly authorized representation policy or prove its own staged-rounding error theorem.

The charge-drift result makes that unavoidable.

Third, the production model still lacks the revision-distinct potential/profile/event ownership already identified in the G5–G6 boundary. G7-R deliberately does not solve that by importing research code into `src/`. 

Thus:

$$
\boxed{\textbf{G7-R success does not imply G7-N success}}.
$$

---

## Evidence integrity

The supplied conformance record's canonical digest independently recomputes to

$$
\texttt{9a8624ff777911ad90ff68c88df2c3f8a886e9c61a876175e880a09adb33ad37}.
$$

The uploaded reference implementation hash is

$$
\texttt{202fd964df2ea52415957c5cf1adccfc3c25f034e15b0166088fd47faa4954c5},
$$

the independent checker hash is

$$
\texttt{7651e34126ce76cfcae0afd600da6d609d6149b06575c979f6f7c1f741ba07d5},
$$

and the conformance note hash is

$$
\texttt{d842ad5e289b5309bb6c241218e4589ef1c0b574879e475a5182623ef4422c7d}.
$$

These match the retained bindings. 

I did not run the repository-binding `main()` wrapper because the companion G5–G6 adjudication JSON/source tree was not supplied as a complete executable repository in this turn. I did execute the substantive new evaluator, point-check, source-control, lifecycle and replay paths directly.

## Final disposition

| Component                                       | Verdict                                   |
| ----------------------------------------------- | ----------------------------------------- |
| Full-graph nonlinear A_OS evaluator             | **PASS**                                  |
| Independent staged oracle comparison            | **PASS**                                  |
| 1,116 scalar point comparisons                  | **PASS**                                  |
| Wrong descriptor/current staging discrimination | **PASS**                                  |
| Source-only dyadic prescription                 | **PASS**                                  |
| Both-role resource/history transfer             | **PASS**                                  |
| Old-edge lineage + bridge-only seed             | **PASS**                                  |
| Detached both-role target admission             | **PASS**                                  |
| Atomic local publication behavior               | **PASS**                                  |
| Split/step/reset replay                         | **PASS**                                  |
| Negative lifecycle pressure                     | **PASS**                                  |
| Lower-endpoint \(h=3/25\) split/replay pressure | **PASS**                                  |
| Finite publication-only binary64 bridge         | **PASS**                                  |
| Exact binary64 charge conservation              | **FAILS, correctly retained as boundary** |
| Infinite binary64 theorem                       | **Open**                                  |
| Automatic source formation / K0 dispatcher      | **Open**                                  |
| Native potential/profile/owner admission        | **Open**                                  |
| G7-R                                            | **PASS**                                  |
| G7-N                                            | **OPEN**                                  |
| Aggregate ATC-2                                 | **OPEN**                                  |

So I would support the next scoped adjudication of **G7-R exactly as stated**.

At that point the A_OS research stack is in a strong place: mathematics through G1–G6 plus an executable full-graph oracle, transaction model, replay model, and finite representation bridge. The remaining A_OS work is qualitatively different now—it is **native authority and numerical-policy engineering**, not another search for the scientific topology mechanism.

> Relocation-only maintenance: repository paths and dependent identities were
> rebuilt before first commit. Scientific statements, numerical results and
> review verdicts are unchanged; the new identities are not an independent
> reviewer rerun. Earlier byte-preservation statements describe the pre-move stage.

This is a **PASS for both G5 and G6**. The package does what those stages were supposed to do rather than merely adding parameter knobs.

G5 genuinely activates the remaining Candidate-A conductance channels and broadens the site law from one affine choice to a \(C^1\) potential class. G6 then changes the request duration while preserving the same physical relaxation timescale instead of accidentally changing the writer law. The coupled G4 environment survives both extensions as well. 

## G5 — PASS

### The \(\alpha,\beta\) channels are genuinely consumed

The descriptor binding is explicit:

$$
D_i(C)=
\frac{\sum_{j\sim i}(r_j-r_i)(C_j-C_i)}
{1+\sum_{j\sim i}(r_j-r_i)^2},
$$

with fixed physical host positions transported through fission. The exact WLS matrices annihilate constants, respect the decorated pair symmetries, and give the required bound

$$
|D_u-D_v|\le2\|C-c\mathbf1\|_2.
$$

The checker verifies those identities on the paired and embedded source/target graphs, including the corresponding environmental swaps. 

More importantly, neither new channel is vacuous on the active source domain. The paired event region has uniform positive lower bounds

$$
\alpha\bar C_e
\ge
\frac{269}{409600}>0,
$$

and

$$
\frac{\beta}{2}(D_u-D_v)^2
\ge
\frac{7921}{81920000}>0.
$$

The embedded source also has positive lower interval endpoints for all retained \(\alpha\)- and \(\beta\)-contributions, including the genuinely active external edge. 

The writer also correctly rebuilds \(D\) from **post-resource \(C^+\)** instead of silently reusing the source descriptor. The exact pressure example

$$
\frac{196}{625}\ne\frac{1849}{5625}
$$

shows that this staging matters physically. 

So:

$$
\boxed{\textbf{Active }\alpha/\beta\textbf{ channel lift: PASS}}
$$

### The potential generalization is real

The theorem assumes only

$$
p\in C^1([0,9]),
\qquad
|p'(c)-19/4|\le\frac1{2048}.
$$

Writing

$$
p(c)=\frac{19}{4}c+g(c),
$$

the proof uses only

$$
|g(c_i)-g(c_j)|
\le
\frac1{2048}|c_i-c_j|.
$$

That is sufficient because additive constants disappear under the edge difference.

It is therefore not merely another affine parameter interval. The included family

$$
p(c)=ac+\frac{\nu}{2}c^2
$$

with

$$
|a-19/4|\le\frac1{4096},
\qquad
\nu\in
\left[\frac1{131072},\frac1{65536}\right]
$$

is genuinely nonlinear and lies strictly inside the declared slope class. 

I accept:

$$
\boxed{\textbf{Bounded nonlinear potential-class lift: PASS}}
$$

with the important ceiling that it is a **common fixed law** at all vertices—not independent per-edge or per-step potential choices.

---

## The G2 obstruction theorem survives G5

This was essential.

On the paired source cone, the new potential contributes at most \(18K\) to the summed bare-current loss. Since \(x\ge3\), that becomes a relative loss bounded by \(6Kx\).

Together with the already-reviewed Read-Back/geometry error,

$$
x^+
\ge
\left[
1+\frac52h
\left(
\frac{19}{250}
-6K-\frac{2\epsilon}{3}
\right)
\right]x.
$$

At \(h=1/8\), the exact coefficient still exceeds \(1/50\):

$$
\text{growth}
=
\frac{1324826221837}{65542647398400}
\approx0.0202132
>
0.02.
$$

Thus

$$
x^+\ge\frac{51}{50}x,
$$

and the existing 56-step impossibility bound survives. 

This is not a perturbative “probably still unstable” statement. It is the same kind of predictive full-feedback obstruction theorem G2 earned, now including:

* nonlinear \(p\),
* \(\alpha\),
* \(\beta\),
* \(\gamma\),
* Read-Back,
* generated geometry,
* and the actual post-resource writer.

$$
\boxed{\textbf{G5 source obstruction: PASS}}
$$

---

# The event and reset domains also survive

The event law is correctly updated to require balance of the **actual \(p\)-baselines**, not the affine surrogate.

The previous strict interior point remains interior uniformly for every \(p\) in the class, even after the conservative \(9K\) per-baseline uncertainty.

The resulting source-selected dyadic share remains inside

$$
\frac{31}{64}
<
\lambda
<
\frac{33}{64},
$$

and both-role funding retains

$$
\text{margin}\ge\frac{1303}{1600}.
$$

Reset remains a separate independent role and does not have to satisfy the current's ordering or balance condition. 

So the potential/channel extension does not smuggle reset into source selection.

---

## The changed history equilibrium is handled correctly

This is another place where the new proof is materially better than simply reusing G1–G4.

When \(\alpha>0\), uniform resources no longer drive \(W\to1\). Instead,

$$
G_e(c\mathbf1)=e^{-\alpha c},
$$

because descriptor contrasts and currents vanish.

The proof therefore correctly introduces

$$
e_n=\log W_n+\alpha c
$$

and obtains

$$
e_{n+1}
=
\rho_n e_n
-
(1-\rho_n)
\left[
\alpha(\bar C_{e,n+1}-c)
+\frac{\beta}{2}\Delta D_{e,n+1}^2
+\frac{\gamma}{2}J_{e,n}^2
\right].
$$

As \(C_n\to c\mathbf1\), the forcing tends to zero. Uniform \(\rho_n<1\) therefore gives

$$
e_n\to0,
$$

hence

$$
\boxed{W_n\to e^{-\alpha c}}.
$$

That is the correct constitutive equilibrium, not the old \(W\to1\). 

This resolves exactly the G5 issue we anticipated after G1–G4.

---

# Target restoration survives G5

For the paired target,

$$
q
\le
\frac{178001006444257}{198861247217664}
\approx0.895102
<
\frac9{10}.
$$

For the full embedded target,

$$
q
\le
\frac{34384837005624313}{35353110616473600}
\approx0.972612
<
\frac{49}{50}.
$$

The potential remainder, descriptor term, Read-Back correction, generated geometry, and current-dependent writer are all included in those bounds. 

So:

$$
\boxed{\textbf{G5 paired and embedded indefinite return: PASS}}
$$

for the stated balls and histories.

---

# G6 — PASS

G6 correctly changes the request domain without changing the constitutive relaxation law.

The physical constant remains

$$
\tau_A=\frac{1}{8\log2}.
$$

For each request,

$$
h_n\in
\left[\frac3{25},\frac18\right],
$$

the writer uses

$$
\rho_n=e^{-h_n/\tau_A},
$$

rather than retaining an artificial square-root update. 

That distinction is essential.

At \(h=1/8\),

$$
\rho=\frac12,
$$

so the old square-root case is recovered.

For smaller requested \(h\),

$$
\rho>\frac12,
$$

and the retained proof establishes a uniform bound

$$
0<\rho_n<\frac{25}{37}<1.
$$

The logarithm kernel and \(h\)-dependent decay were pressure-tested with outward rational arithmetic rather than a floating transcendental assumption. 

### Variable request sequences are actually covered

This is stronger than proving two endpoint values.

The mathematical enclosure uses the entire \(h\)-interval at every source step. Thus it safely contains **arbitrary sequences**

$$
h_1,h_2,\ldots
\in[3/25,1/8]
$$

while the constitutive parameters and potential law stay fixed.

Dependency is intentionally forgotten, so the proof is if anything more permissive than one fixed schedule.

This means G6 is legitimately a request-domain result rather than an endpoint experiment.

It is **not**:

* subdivision invariance,
* continuous-time equivalence,
* \(h\to0\) closure,
* or permission to change the constitutive parameters with each request.

The note correctly avoids all four claims. 

---

## Source obstruction survives arbitrary G6 requests

At

$$
h_{\min}=\frac3{25},
$$

the source growth lower bound becomes

$$
\frac{1324826221837}{68273591040000}
\approx0.0194047
>
\frac1{60}.
$$

Thus every successful nonnegative unsplit update satisfies

$$
x^+\ge\frac{61}{60}x,
$$

and

$$
3\left(\frac{61}{60}\right)^{67}>9.
$$

Therefore nonnegative unsplit continuation cannot survive all 67 subsequent proposals, even under varying allowed request lengths.

History reset remains inside the same obstruction domain, so it does not solve the problem. 

$$
\boxed{\textbf{G6 variable-request source obstruction: PASS}}
$$

---

# G6 target return also passes

For the paired target, the worst resource contraction becomes

$$
q
=
\frac{4471290108929017}{4971531180441600}
\approx0.899378873
<
0.9.
$$

For the embedded target,

$$
q
=
\frac{860659422764966737}{883827765411840000}
\approx0.97378636
<
0.98.
$$



The paired bound is fairly close to the declared \(9/10\) ceiling—there is only about

$$
6.21\times10^{-4}
$$

of margin.

That is not a defect in G6, but it is a useful warning: future widening of \(h\), \(K\), \(\alpha/\beta\), or the feedback box must recompute this exact inequality rather than treating “\(q<0.9\)” as inherited folklore.

For the present scope:

$$
\boxed{\textbf{G6 indefinite return: PASS}}
$$

---

# The embedded-environment proof survives G5–G6

This is important because otherwise G5/G6 could have quietly fallen back to the isolated star.

The active seven-vertex environment remains genuinely coupled. The external reference current is still strictly positive, and all three edge classes have positive \(\alpha\) and \(\beta\) contributions. The source-selected share remains within the conservative interval

$$
\left[\frac{15}{32},\frac{17}{32}\right],
$$

with positive funding and direct both-role entry

$$
X^2
<
\frac1{16}.
$$



For G5, every unsplit and reset-only trajectory is proved to reject by attempt 7.

For G6, every such trajectory rejects by attempt 10.

The G6 enclosure becomes wide enough that some intermediate interval rows contain both negative and positive resource possibilities. The checker does **not** clamp those physically. It restricts subsequent proof propagation to possible nonnegative survivors and then intersects two exact descriptions of the same difference coordinates.

That narrowing is legitimate:

$$
\text{actual surviving state}
\subseteq
\text{raw }d\text{ enclosure}
\cap
\text{difference enclosure from nonnegative }C.
$$

If those sets become disjoint, no physically nonnegative survivor exists.

The writer is only evaluated for the surviving subset, and terminal empty intersection means all trajectories have already rejected. 

I therefore accept this as an interval-proof operation, **not resource clamping or repair**.

$$
\boxed{\textbf{G5/G6 embedded obstruction and return: PASS}}
$$

---

## The arbitrary-environment counterexample also survives

The second-parent exclusion remains valid.

Its untouched mode has weighted Rayleigh lower bound

$$
\frac{24}{25}\frac{26}{5}
=
\frac{624}{125}
=
4.992,
$$

while the largest allowed potential slope is

$$
\frac{19}{4}+\frac1{2048}
\approx4.75049.
$$

Therefore the resource linear block remains unstable.

At the shifted uniform equilibrium, \(\alpha\) adds resource-to-history forcing, but the resource derivative with respect to \(W\) vanishes on uniform \(C\). Read-Back, geometry and the \(\beta,\gamma\) pieces are higher order there. Thus they cannot remove that unstable resource diagonal block.

So G5 does **not** accidentally invalidate the G4 operation-support counterexample. 

That is a good pressure result.

---

# Native-readiness result: useful, but correctly not G7

The separate readiness record is appropriately conservative.

It reports successful primitive comparisons for:

* all four WLS descriptor graphs;
* the existing log-interpolation writer at \(h=1/8\);
* a non-\(1/8\) request inside the G6 domain.

It also records that the production `CandidateACurrent` still accepts only

`quadratic_site_potential_zero_derivative_v1`

and therefore does **not** provide native authority for the new potential class. 

I could not execute the `pygrc` native probe itself from the uploaded sandbox because the production package is not present there. I did, however, independently reconstruct the captured binary64 descriptor outputs from the pinned inputs and the stated WLS formula, and independently reconstruct both retained log-writer outputs; they agree with the recorded values.

So I would disposition the native material as:

$$
\boxed{\textbf{Primitive/native-readiness evidence: consistent PASS}}
$$

but

$$
\boxed{\textbf{G7: emphatically OPEN}}.
$$

The record gets that boundary right.

---

## Evidence integrity

I independently executed the complete new mathematical `evidence()` calculation from the uploaded certifier against the uploaded G1–G4 predecessor scripts. Its encoded evidence matches the certificate exactly.

The G5/G6 certificate canonical digest recomputes to

$$
\texttt{d404e45a76bafad90a1a563b298ae01b1cc4866c125627cb6163bc417bd1afb1}.
$$

The mathematical checker SHA-256 is

$$
\texttt{8d0aa7016710d5e64935a3496fb9160689eda87e6c999b3336924b4f99c0828f},
$$

and the decision-note hash is

$$
\texttt{34974e4489f9e62a805bf5d105be78b37b06e6597084a73b9a3db1ef59104840}.
$$

The native-readiness record's canonical digest also recomputes to

$$
\texttt{87a2085de7c0ec11fa1aa89ec10b40f1ecdcd908d1bef9ccfa640df165918ec6}.
$$

 

I did not execute either repository-dependent `main()` wrapper because the full accepted repository/adjudication tree is not mounted in this environment.

## Final disposition

| Stage                                              | Verdict               |
| -------------------------------------------------- | --------------------- |
| Explicit host/WLS descriptor binding               | **PASS**              |
| \(\alpha\) genuinely active                        | **PASS**              |
| \(\beta\) genuinely active                         | **PASS**              |
| Post-resource descriptor rebuilding                | **PASS**              |
| \(C^1\) potential class                            | **PASS**              |
| Genuine nonlinear potential subclass               | **PASS**              |
| G2 full-feedback obstruction with all A channels   | **PASS**              |
| Event/reset target entry                           | **PASS**              |
| Shifted history equilibrium \(W\to e^{-\alpha c}\) | **PASS**              |
| Paired full-channel target return                  | **PASS**              |
| Embedded full-channel target return                | **PASS**              |
| Variable \(h\in[3/25,1/8]\)                        | **PASS**              |
| Fixed-\(\tau_A\) writer under variable requests    | **PASS**              |
| Arbitrary request sequence inside interval         | **PASS**              |
| Subdivision/continuous-time invariance             | **Not claimed**       |
| Native primitive readiness                         | **Positive evidence** |
| Native potential/event authority                   | **Open**              |
| G7                                                 | **Open**              |

So:

$$
\boxed{\textbf{G5–G6 mathematical package: PASS}}
$$

This is a substantial A_OS generalization. At this point, within the bounded exact-sector/state/environment classes, the law is no longer dependent on zero \(\alpha/\beta\), one affine potential, or one fixed request duration.

I would support a scoped G5–G6 adjudication now. After that, **G7 really is the next distinct problem**: not more A_OS mathematical widening by another fixture, but authority, represented-error closure, native potential/profile ownership, event lifecycle, lineage/rollback/replay, and actual substrate conformance.

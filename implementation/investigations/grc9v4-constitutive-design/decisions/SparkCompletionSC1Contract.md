# SC-1 — A proposed geometric child-basin completion contract

Date: 2026-10-31. **Conditional mathematics passes scientific pressure; precision
corrections applied. Geometric policy admission remains open.** Predecessor: initial feasibility checkpoint
0d27440b. [Opening](./SparkCompletionDefinitionAndFeasibility.md),
[successor ledger](../evidence/spark-completion/SC1ClaimDebtLedger.json),
[focused evidence](../evidence/spark-completion/SC1Checks.json).

**Applicability:** the [audit resolution and equilibrium exclusion](./SparkCompletionSC1EquilibriumExclusion.md)
show that the retained C_OS/C_CI/A_CI/A_PC zero-site closed-tree bindings
cannot supply this stationary completion certificate. This is a bounded
mathematical exclusion, not just an unsuccessful witness search. Earlier
finite-horizon continuation remains valid.

## 1. Scientific choice and authority boundary

Propose the named branch **grc9v4-certified-geometric-child-basins-v1**:
a child is a qualified geometric seed with a nontrivial, all-route spatial
attraction domain, preserved by a full-state trapping/contraction certificate.
Completion requires a certified gain of these basins relative to the same
classifier on the pre-event parent. A peak, a finite-lived flow sink, or a
mechanical expansion alone does not meet this definition.

This supplies the previously missing bridge from geometric cores to actual
basins. It is an **explicit new geometric identity policy**, not a claim that
the accepted physical-flow diagnostic already implements it. Nor is the
routing operator below a new constitutive transport law.

The [V3 paper](../../../../papers/2026-02-GRC-V3.md), identity discussion and
Appendix B, distinguishes geometric seeds from flux-topological identity and
defines spatial attraction domains on vertices. This motivates distinguishing
spatial basins from alternative attractors of the entire field. Its particular
physical-flux routing is not inherited here. The new signed-resource descent
rule requires its own scientific acceptance. The
[V4 paper](../drafts/2026-09-GRC-V4.md), A.5/A.7, and
[current specification](../../../../specs/grc-9-v4-spec.md) require stable
child-organization gain but do not select this evaluator. The
[basin interface](../../../../specs/grc-9-v4-basin-interface.md) remains an
instantaneous physical-flow diagnostic, with its existing claim ceiling.

This bounded choice is conservative: it does not cover oscillatory, moving,
plateau or noncontractive organizations. Excluding them from this certificate
does not prove that they are not organizations. No accepted authority, paper,
specification, production code or old evidence is changed here.

## 2. A spatial basin with no external chooser

Fix a graph, its port/row chart, positive edge weights and a declared signed
Hessian convention $s_H\in\{-1,+1\}$. Define the diagnostic landscape

$$
\Psi_x(i)=s_H C_i.
$$

It is derived from state, not an additional authoritative variable, Candidate
A/C constitutive potential, mobility, or physical current. The global sign is
part of policy identity; it cannot be chosen per node or after seeing a result.
For every vertex use **all** strict neighbor descents:

$$
D_x(i)=\{j\sim i:\Psi_x(j)<\Psi_x(i)\}.
$$

If this set is empty, stop at $i$. Equal levels create no descent; self loops
create none. Parallel edges do not create extra choices of destination.
No strongest-edge choice, random successor, label order or redirection of an
unqualified terminal is allowed.

Let $\mathcal T_x(i)$ contain every terminal reachable by strict descent.
A qualified anchor $s$ must satisfy all of the following:

1. The declared fixed-row seed predicate, with strict margins:
   $\sum_a g_a(s)^2<\epsilon_g^2$ and
   $\min_a(s_H g_a(s))>\epsilon_H>0$.
2. $C_s>c_{\min}>0$.
3. At least one distinct neighbor, and
   $\Psi_x(j)-\Psi_x(s)>\Delta_\Psi>0$ for **every** neighbor $j$.
4. Its guaranteed attraction domain
   $B_s(x)=\{i:\mathcal T_x(i)=\{s\}\}$ contains at least two vertices.

Scientific anchors use **exact row functions** at the state being certified,
with the declared row convention and units. A native completion observation
additionally needs certified agreement with the represented row predicate,
as specified in §5. The existing represented-only diagnostic remains unchanged.
All thresholds are fixed before witness selection. The row summary is not
promoted to a newly proved continuum Hessian. In particular, the strict
neighbor condition is additional: it does not follow from an average row
predicate. Since $\min_a s_Hg_a>\epsilon_H$, the necessary seed condition
$\epsilon_g>\sqrt{3}\epsilon_H$ still applies. On a loop-free positive-weight
chart every occupied signed row is a weighted mean of neighbor differences
greater than $\Delta_\Psi$. All three rows must be occupied, giving the stronger
necessary condition

$$
\epsilon_g^2>3\max(\epsilon_H,\Delta_\Psi)^2.
$$

This is a pre-search exclusion, not a sufficient predicate; the contrast
strengthening is not asserted for rows diluted by self-loop contributions.

**Spatial-basin lemma.** Strict descent on a finite graph is a DAG, so every
maximal route from $B_s$ reaches $s$ in at most $|V|-1$ routing moves.
If $i\in B_s$, every descent successor also belongs to $B_s$; otherwise its
other terminal would belong to $\mathcal T_x(i)$. Distinct $B_s$ are
disjoint. Ambiguous vertices are unassigned.

These are attraction domains of a declared set-valued routing system, not just
collections of peaks. For any undirected path between distinct qualified
anchors, the neighbor of the higher-$\Psi$ endpoint has landscape value
greater than that endpoint by $\Delta_\Psi$. Hence every such path has

$$
\max_{\text{path}}\Psi>\max(\Psi(s),\Psi(t))+\Delta_\Psi.
$$

Disconnected anchors are already separated by topology. This is an explicit
landscape barrier; it is not a physical energy barrier or an estimate of
transport work. Routing moves are not ordinary physical timesteps.

## 3. Parent correspondence and genuine gain

Apply **this same geometric classifier** to the admitted pre-event source.
Require a unique qualified parent basin $P=B_{s_P}$ containing the expanded
vertex $v$. The anchor $s_P$ need not equal $v$: a degenerating interior
vertex can belong to a basin anchored elsewhere. If no such parent exists,
there is no certificate under this branch; never substitute parent count zero.
This is instantaneous qualification of the parent, not proof that the whole
pre-event field was already attracting. In the old nine-leaf source, leaves
have empty rows and the center cannot be both a spark candidate and a seed
when $\epsilon_{\rm spark}\leq\epsilon_H$. That source has no qualified parent;
a larger source can fix this local issue but not the equilibrium obstruction.

Let $M$ be the exact new module of the admitted D11-G9 event. Its comparison
map is

$$
\pi(x)=
\begin{cases}
v,&x\in M,\\
x,&x\text{ is an unchanged old vertex},
\end{cases}
\qquad F=\pi^{-1}(P).
$$

This map compares source and target organization. It is not an inverse
constitutive/history map. Actual event resource accounting, explicit W/Z
transport or loss, and both-role target readmission remain independently
required. This is the proposed D4/D9 comparison bridge, not an implicit
promotion of an older lineage contract.

A descendant is a qualified target basin with **its whole domain inside**
$F$, anchored either in $M$ or at surviving $s_P$. Count every such basin.
Completion requires

$$
N_{\mathrm{desc}}\geq2,\qquad
\#\{s\in M:B_s\text{ is a descendant}\}\geq1,\qquad
\Delta N=N_{\mathrm{desc}}-1\geq1.
$$

This gain is **local to eligible descendants in the lifted parent footprint**.
It is not a theorem of increased total basin count across the whole graph:
exterior organizations can disappear. Event lineage establishes comparison and
ancestry, not a counterfactual claim that expansion caused the organization.
A surviving parent plus one new child can constitute gain; replacement by one
basin cannot. Unrelated exterior basins, extra unanchored vertices or relabelled
old nodes cannot count. If the source anchor is replaced, two new descendant
basins are needed.

Children entirely inside the event module are allowed if they have the
distinct attraction domains and barriers just proved. Their collapsed source
footprints can coincide at $v$; demanding distinct collapsed footprints
would incorrectly forbid internal differentiation. Thus the earlier finite
physical-flow screen is a control, **not a prerequisite** for this branch.

## 4. Full-state stability and the completion theorem

Let $T_h$ be the actual exact-real ordinary-step map at fixed positive step
$h$, graph, profile, autonomous context and references. Its scientific state
is $x=(C,W_A,Z_4)$, omitting genuinely absent channels. The clock, audit log
and fixed reset snapshot are not evolving scientific coordinates. Every
selected root/section, generated geometry, continuity and history/carrier write
must be defined and admitted. A time-dependent forcing law needs a separate
extended-state argument and is outside this certificate.

Choose a declared scaled norm and a nonempty closed complete domain $K$.
It must contain a positive-radius relative neighborhood in **all independent
physical coordinates**, subject only to genuine constraints such as fixed
total charge. A point, one successful orbit or an unjustified symmetry slice
is insufficient. Require:

1. $T_h(K)\subset\operatorname{relint}K$, with a strict image margin.
2. $\|T_h(x)-T_h(y)\|\leq q\|x-y\|$ for all $x,y\in K$, $q<1$.
3. Uniformly on $K$, every descent edge has the same direction or a proved
   exact identity tie; the qualified-anchor roster and all basin domains are
   fixed, with strict seed, resource and neighbor-barrier margins.
4. The parent reference and descendant gain of §3 hold for that fixed roster.

Uniform comparisons must be proved over $K$, not sampled. Interval boxes
intersected with the fixed-charge manifold are one sufficient representation.
A tie that might change under admissible perturbation is unresolved, not
silently fixed. Full-map contraction is distinct from CI inner-root
contraction, a fixed-geometry current solve or an RG2b section certificate.

**Conditional completion theorem.** Suppose an admitted event is followed by
at least one positive ordinary step, whose resulting state enters $K$.
By invariance all later exact states remain in $K$; completeness and
contraction give a unique $x^*\in K$ and
$\|T_h^n(x)-x^*\|\leq q^n\|x-x^*\|$. Uniform certification preserves each
spatial basin, its qualified anchor and its barrier throughout this return and
at the limit. Their domains attract under the all-route routing operator by
§2. Even if a routing walk observes successive physical states in $K$, its
arrows belong to the same finite DAG. The certified descendant gain therefore
constitutes a completed spark **under this proposed geometric identity branch**.

This proves stable spatial child basins within an attracting full-field
organization. It does **not** assert multiple alternative full-state
attractors, independent subsystem dynamics, causal autonomy, or universal
completion. This distinction is the substantive bridge that the earlier
“several stable cores” proposal lacked. Whether this is the intended bounded
interpretation of A.7 is a scientific selection for review, not a coding choice.

## 5. Represented arithmetic and lifecycle observation

A native numerical claim requires an independent full-step error bound
$\|\widehat T_h(x)-T_h(x)\|\leq\varepsilon$, including selected-root/section
and geometry errors, with error smaller than the image margin. In the
fixed-charge version, the represented output must also belong to the **same
exact charge slice**, independently of any tolerant runtime charge gate.
Then, while these hypotheses hold,

$$
\|\widehat x_n-x^*\|
\leq q^n\|\widehat x_0-x^*\|
+\frac{\varepsilon(1-q^n)}{1-q}.
$$

An error normal to the charge slice can leave $K$ even below both the relative
image margin and the runtime charge tolerance. The present numerical lift
requires a proof of exact constraint preservation; it does not infer it from a
small charge residual. A family of invariant charge slices with fixed points
$x^*(Q)$ and an explicit charge-drift analysis is a possible separate extension,
not supplied by this theorem. Thickening $K$ to a charge slab does not permit
one global contraction for an exactly charge-conserving map: distinct conserved
charges cannot converge to one fixed point.

This bound alone does not enforce exact charge, nonnegative resources, allowed
history domains or target admission. Those gates must also pass on the actual
represented states. Fixed-H bounds cannot substitute for a joint-root bound.
No clipping, tolerance relaxation or unbounded numerical guarantee is inferred
from a finite native run.

**Diagnostic agreement is a separate enclosure.** Scientific basins use exact
row functions. For each represented observation certify the row-evaluation
errors $|\widehat g_a-g_a|\leq\delta_a$ on the relevant domain and thresholds
with the same declared real values. For a positive seed, if $|g_a|\leq G_a$,
it suffices to prove

$$
\sum_a(2G_a\delta_a+\delta_a^2)<m_g,
\qquad \max_a\delta_a<m_H,
$$

where $m_g=\epsilon_g^2-\sup_K\sum_ag_a^2>0$ and
$m_H=\inf_{K,a}s_Hg_a-\epsilon_H>0$. Also certify excluded anchors so rounding
cannot enlarge the roster; interval predicate evaluation is one sufficient
method. Resource/contrast and descent predicates retain their own margins.
If an interval cannot decide the same predicate, report unresolved agreement.
A complete-step error bound does not automatically enclose separately
reconstructed rows. If comparing different exact/represented states, include
both state-propagation and row-evaluation errors. Exact squaring of rounded
rows alone is insufficient: $(1/3,2/3,2/3)$ lies on the exact gradient boundary,
while its binary64 rounding passes the represented strict test. This does not
change the accepted represented diagnostic's flag.

A declared positive observation window additionally checks arrival in $K$
and repeated admitted states there. Fix its duration, minimum positive beats,
comparison norm/scales, thresholds, $h$ and numerical policy before the
witness. It corroborates the actual implementation and lineage; the window
alone is not the stability proof.

- A zero-duration step, read, replay or duplicate does not advance time/beats.
- Failed attempts do not advance the window. It resumes only after verified
  restoration of the entire prior scientific/lifecycle state.
- Reset, graph/profile/context/reference change, rebase or disabled crossing
  terminates the active window. A different context needs a new proof.
- Current and reset are admitted independently. A reset-only observation cannot
  substitute for the evolving current; restarting cannot mint another birth.
- Record **at most one completion gain per event lineage**. A second window,
  policy identity, load/replay or duplicate supplies evidence for the same
  event, not another gain. Distinct child anchors and parent lineage are bound;
  surviving $s_P$ is not entered as its own new child.

The static policy identity is separate from event/parent evidence identity:
configuration selects the rule; event evidence binds the actual source,
parent, target, proof and window. A hash cycle between target profile identity
and its own parent observation is not allowed. The frozen v1 schema's
parent-digest envelope does not express this complete certificate. Any future
implementation needs an explicit successor schema after review, not a silent
reinterpretation of v1 or an edit to the old acceptance record.

## 6. Why the earlier substitutes do not settle completion

For actual consumed continuity current on a closed unit-measure graph,

$$
C^{k+1}=C^k-h_kBJ_k^{\mathrm{use}}+e_k,\qquad
C^k\geq0,\quad \sum_i C_i^k\leq Q_{\max}.
$$

If a fixed vertex has consumed inflow at least $\iota>0$ and accumulated
coordinate error at least $-E_n$, summation gives

$$
\iota\sum_{k<n}h_k\leq Q_{\max}-C_s^0+E_n.
$$

At finite charge this excludes indefinite uniformly positive inflow if
$T_n\to\infty$ and $\limsup_{n\to\infty}E_n/T_n<\iota$.
More generally, it suffices that $\iota T_n-E_n$ eventually exceed
$Q_{\max}-C_s^0$. Pointwise $E_n/T_n<\iota$ at every finite $n$ is insufficient:
$E_n=(n-1)\iota$ with $T_n=n$ approaches the rate $\iota$ and can cancel
all but the first resource increment. It does not exclude decaying inflow, circulation,
external exchange, or a stable geometric basin at zero flux. A fresh diagnostic
current only inherits this bound through a separately proved stage comparison.

At an exact fixed point, **the consumed** current has $BJ^{\mathrm{use}}=0$.
It need not equal the fresh poststate read. The earlier unconditional sentence
that the fresh basin API must therefore return no basins was too strong:
it requires that additional stage equality or bound. No fixed-point condition
is being substituted into a different read stage.

The finite physical-flow reference remains useful negative pressure on
observational persistence, lineage and replay. It is neither a proof of
attraction nor the chosen geometry-basin evaluator. Adding a stable peak to a
flow label would still not supply the spatial-domain or full-state theorems.

## 7. Exact executable definition check

[The research reference](../research/spark_completion_basins.py) checks the
definitions and an **abstract affine** return example using exact rationals.
It is not a GRCV4 constitutive operator or a saturated D11-G9 expansion.

The port-valid source has eight vertices, parent anchor $p$, expanded interior
vertex $v$, and six leaves. Resources are $C_p=3,C_v=2,C_{\rm leaf}=1$.
A declared abstract replacement introduces $x,m,y$, preserving other resources
and splitting $2=3/4+1/2+3/4$. Immediately afterward only the parent basin
exists. No child is declared by the mechanical replacement alone.

On the ten-vertex target choose the center
$C_p^*=C_x^*=C_y^*=2$, all other seven values $5/7$, total charge 11, and

$$
T(C)=C^*+\tfrac12(C-C^*),\qquad
K=\{\|C-C^*\|_\infty\leq1/14,\ \sum_iC_i=11\}.
$$

This map is deliberately abstract: its chosen center encodes the desired
pattern. It does not show V4 selecting or forming that pattern. $K$ has relative dimension nine, positive
resources at least $9/14$, image margin $1/28$, and contraction $1/2$.
With sign $-1$, gradient threshold 4, Hessian threshold $1/4$, contrast
$1/2$, and core-resource threshold $1/2$, exact interval inequalities prove
the same three basins everywhere in $K$:

| Anchor | Guaranteed domain |
| --- | --- |
| p | p, a, b |
| x | x, d, f |
| y | y, e, g |

The saddle $m$ can descend to all three and stays unassigned. The uniform
edge/anchor contrast lower bound is $8/7$. The event state first enters $K$
after five abstract steps; two further positive observations retain gain two.
One full-field fixed point contains three genuine spatial attraction domains.

Fifteen geometric result groups include missing parent, replacement alone,
zero-radius domain, $q=1$, contraction to an unorganized uniform state,
strict seed/barrier boundaries, insufficient numerical image margin, incorrect
lineage, plateaus, ambiguous routing, sign and label/orientation controls,
and omission of unstable history coordinates. The 25 earlier finite-window
groups and affine error/nonnormal controls remain separately labelled.
The [audit pressure](../research/spark_completion_pressure.py) also reproduces
5,422 graph/landscape cases, 252 charge-box corners and explicit capacity,
charge-normal error and row-rounding countermodels, with regression checks of
the corrected interfaces. Forensic queries preserve their own provenance/support
boundaries; the equilibrium audit also checks the 112 retained declarations.
These checks establish internal consistency and conditional mathematics,
**not actual V4 feasibility, native charge preservation or completed sparks**.

## 8. SC-1 disposition and finite next step

The independent audit passes the conditional spatial/temporal mathematics.
Its precision corrections are applied, and the bounded equilibrium exclusion
is recorded in [the resolution](./SparkCompletionSC1EquilibriumExclusion.md).
SC-1 remains a conditional research proposal, not an achievable completion
policy for the retained zero-site tree bindings. Formal scientific policy
admission and positive V4 feasibility remain open.

The next question is which admitted constitutive mechanism, if any, can sustain
an admissible nonconstant equilibrium. SC-2 must derive that mechanism and its
domain before selecting a witness. Longer runs, new positive thresholds, and
for A even adding cycles within the positive-denominator domain cannot remove
the recorded obstruction. A richer source could fix the missing parent issue
without fixing stationarity. A changed constitutive binding or nonstationary
completion criterion must be justified explicitly, not silently selected to
make the affine example achievable.

SC-3 adjudication and authority → proposal/paper → specification precede
P9-9.1a native implementation. This note grants no completion/hierarchy support,
aggregate Tranche 10 closure or G4.

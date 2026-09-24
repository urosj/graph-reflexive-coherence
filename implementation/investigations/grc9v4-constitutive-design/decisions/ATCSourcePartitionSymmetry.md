> Relocation-only maintenance: repository paths and dependent identities were
> rebuilt before first commit. Scientific statements, numerical results and
> review verdicts are unchanged; the new identities are not an independent
> reviewer rerun. Earlier byte-preservation statements describe the pre-move stage.

# Source symmetry, physical asymmetry and a proposed activity partition

Status: independent mathematical review PASS for the symmetry obstruction,
conditional robustness and A_OS source-asymmetry transmission. The reviewer
independently reproduced the exact checks and seven finite source reads.
The activity-variance rule remains a constitutive grouping hypothesis, not a
derived fission law. No accepted claim, refinement trigger, native topology
policy or capability cell is promoted.
The reviewed [partition/OS result](./ATCPartitionOSFeedback.md) is unchanged.

That predecessor separated source participation, supplied partition and target
support. This continuation goes upstream. It establishes an exact symmetry
obstruction and tests one explicit source-only partition proposal on a bounded
asymmetric A_OS family. It does not consult any target or feed the earlier
2+2/1+3 consequences back into a source chooser.

## 1. What symmetry actually forbids

Let s denote the complete physical source data used by a proposed rule, and
let F(s) be one unordered partition of the four parent half-edges into two
nonempty blocks. Relabeling equivariance requires

$$
F(g s)=g F(s).
$$

If g fixes s, it must therefore fix F(s). In other words, any deterministic
single-valued partition must be fixed by the source's stabilizer. This is a
necessary condition, not a physical principle choosing between several allowed
fixed outputs when the stabilizer is smaller.

For the fully symmetric four-leaf source, all leaf resources, old histories,
reference weights and external context are equal, and all profile operations
respect that symmetry. Its stabilizer contains S4 acting on the four
half-edges. There are seven unordered nonempty binary partitions:

| Size class | Number of labeled partitions | S4 orbit size |
| --- | --- | --- |
| 1+3 | 4 | 4 |
| 2+2 | 3 | 3 |

Neither orbit contains a fixed partition. A transposition across blocks moves
any proposed partition to another. Thus **no deterministic equivariant rule
can select a single nontrivial binary partition from this source**.

This is stronger than a tie in one particular score. It also explains the
degree-two exception: the unordered pair of singleton blocks is unique and
is fixed when its two half-edges are exchanged.

The invariant possibilities here are an explicitly unresolved outcome or a
set of alternatives closed under the source symmetry. A nonempty set-valued
output may be either complete orbit (the three 2+2 alternatives or the four
1+3 alternatives), or their union. **Equivariance does not force all seven.**
The variance rule below returns all seven because its seven scores are zero
at equality; that is rule-specific. A separately justified size-class
restriction could select an orbit, but target-support results alone do not
justify that restriction or choose one member of the orbit.

A distribution-valued law would be another possible mathematical object, but sampling one outcome
requires separately declared stochastic authority; no random seed, hidden
chooser or additional physical memory is introduced here. A set of possible
partitions is not permission to execute all their conflicting graph edits.

### Generated geometry does not secretly provide a direction

On the symmetric source the four predictor structural components equal f.
The declared identity-adapter star source is

$$
S_\star=\tfrac12 f^2(I+\mathbf1\mathbf1^\top).
$$

Its uniform eigenvalue is (5/2)f squared, while its three-dimensional contrast
subspace has eigenvalue f squared/2. It therefore supplies no preferred
contrast vector or 2+2 split. If f=0, the degeneracy is greater, not resolved.
Choosing one numerical eigenbasis vector would insert information absent
from the source. The same issue applies to any equivariantly derived response
operator: a basis choice inside a degenerate subspace is not a physical
source distinction. This does not derive CAN-B's missing functional or mode.

Moreover, deterministic equivariant fixed-graph evolution preserves the
stabilizer: g T(s)=T(g s)=T(s). A trajectory starting in exact full symmetry
does not acquire a preferred labeled partition merely by waiting or reading
its own symmetric geometry. Numerical order effects are not a scientific
symmetry-breaking law.

**Equal currents alone are not this theorem's hypothesis.** A physically
asymmetric source might have equal projected activities but unequal W, context,
geometry or other lawful data. The proposed scalar rule below discards such
distinctions; its unresolved result would not prove that every source-side
rule must be unresolved there.

## 2. One deliberately explicit source-only proposal

At a degree-four simple-star parent v, obtain the selected profile-correct
present current J, keeping incoming W fixed throughout the read. Define the
orientation-independent inward activity

$$
a_e=-B_{ve}J_e.
$$

Reversing an edge changes both factors' signs and leaves a_e unchanged.
For this proposal require all four activities strictly positive. Mixed signs,
zero activity or other degrees are outside its proposed domain, **not** a
certificate of `no_event`. This is a partition consumer, not a growth guard.

For every unordered binary partition P={A,B}, define

$$
V(P;a)=\sum_{D\in P}\sum_{e\in D}(a_e-\bar a_D)^2,
\qquad \bar a_D=\frac1{|D|}\sum_{e\in D}a_e.
$$

Interpretation: put similar present inward exchanges in the same prospective
block, minimizing their within-block disparity. Equal weighting is an explicit
choice for this unit-reference, four-contact research domain. The score has
current-squared units; it is neither energy, a reduced Hessian, geometry nor
an established measure of a site's inability to continue as one vertex.

This is a **new constitutive grouping hypothesis**, not a consequence of
equivariance or the accepted V4 equations. Other source-only functionals may
be lawful and choose differently. What is tested here is whether this one
can consume genuine source distinctions coherently and robustly. Its physical
meaning as part of a fission law still needs justification.

### The score includes cardinality weighting

Let m=|A|, n=|B|, m+n=4, and define the overall mean and centered variance by

$$
\bar a=\frac14\sum_e a_e,\qquad T=\sum_e(a_e-\bar a)^2.
$$

Within each block, expanding around its block mean cancels the cross term.
Therefore

$$
T=V(P;a)+m(\bar a_A-\bar a)^2+n(\bar a_B-\bar a)^2,
\qquad
V(P;a)=T-\frac{mn}{4}(\bar a_A-\bar a_B)^2.
$$

Since T is independent of P, minimizing V is exactly equivalent to maximizing
mn times the squared block-mean separation. For the same separation, the
weight mn is 4 for 2+2 and 3 for 1+3. This favors balanced blocks at equal
separation without excluding singleton isolation. It is physical content of
the proposed functional, **not a consequence of equivariance** or a hard
size-class filter. Similarity grouping with this weighting still needs a
constitutive rationale; complementary-flux balancing, history grouping or
other lawful structural observables could yield different hypotheses.

### Selection and covariance

Resolve to the unique minimizer if it exists; otherwise return `unresolved`
with the whole minimizer set. Enumerate all seven partitions. In particular:

- Do not restrict the search to the three 2+2 maps because those targets passed.
- Do not choose the first minimizer, break a tie by edge IDs, or order children.
- Do not use target resources, target admission, future currents or return rates.
- Do not mix reset, receipts, elapsed time, requested duration or failed attempts
  into the physical score or its computation budget.

The first restriction matters: an independent scientific reason could someday
justify a cardinality restriction, but target-support evidence alone does not
supply one. The score is evaluated on source activities, not on candidate
target graphs. It introduces no target catalogue.

For any permutation g, V(gP;ga)=V(P;a), so the whole argmin set is equivariant.
If the minimizer is unique, its single partition is equivariant too. Adding a
common activity offset or multiplying all activities by a positive constant
preserves the ranking whenever the strict-inflow domain is preserved. These
algebraic properties do not justify changing physical source data.

## 3. Exact symmetric, asymmetric and tie cases

At a_e=a_* for all four edges, every score is zero. This proposed rule returns
**all seven alternatives**, not just the favorable size class. No target read
is needed to obtain that honest outcome.

If there are exactly two distinct activity levels and each occurs, the unique
zero-variance partition is into those level classes. Every other partition
mixes levels in at least one block and has positive variance. This covers
both 2+2 and 1+3 patterns. For level separation D>0, the exact gap to the next
best partition is 2D squared/3 for 2+2 and D squared/2 for 1+3.

Asymmetry alone need not resolve the proposed score. For example, activities
(1,2,2,3) have two equal minima: isolate the first or the last edge, each with
score 2/3. Both remain in the output. In contrast, (1,2,3,4) has a unique
minimum grouping the adjacent low and high pairs. These rational examples
pressure the rule; they are not claims of native source reachability.

The implementation's use of array positions to enumerate/serialize all
partitions removes duplicate representations only. It does not select among
equal candidates. The unordered physical result transforms with the input.

## 4. Robustness without a hidden tie epsilon

Let R=||a-mean(a)1||_2, and suppose a perturbation e obeys ||e||_2<=epsilon.
The score is a squared orthogonal within-block projection. Therefore

$$
|V(P;a+e)-V(P;a)|\le2R\epsilon+\epsilon^2.
$$

If the unique minimizer has gap Delta to all competitors, it remains unique
with the same partition whenever

$$
\Delta>4R\epsilon+2\epsilon^2.
$$

The perturbed input must also remain in the strict-inflow domain; for example,
epsilon<min(a_e) suffices. Score separation alone cannot certify that guard.

For either two-level pattern above, R<=D. Thus epsilon<=D/10 suffices:
the comparison error is at most 21D squared/50, strictly below both exact gaps.
This is a conditional error certificate, not a hardcoded equality tolerance.
The exact rational evaluator treats actual ties exactly; it does not convert
small differences into ties or physical asymmetries by a hidden threshold.

As D tends to zero the score gap is O(D squared), while the sufficient error
radius epsilon=D/10 shrinks **linearly**, O(D), not quadratically. The comparison
score error at that radius is O(D squared). There is no uniform numerical
margin at symmetry.
Three distinct two-level source families approach the same symmetric source
while favoring the three different 2+2 maps. No single-valued continuous
extension to that symmetric point can preserve those choices and equivariance.
A later native consumer would need a bound on its source-read error and a
declared insufficient-margin disposition; these Decimal diagnostics do not
provide that native error bound.

## 5. Are the distinguishing activities actually available in A_OS?

Yes, on a bounded family, without manufacturing a source-current vector.
Use the reviewed affine law p(c)=19c/4, eta=kappa_c=1, alpha=beta=0, zeta_A=1,
no carrier, identity reference Hodge and identity common star adapter. Keep
the same gain box gamma<=2^-16, chi_A<=1/2, kappa_H/kappa_Ah<=1 and research
split tolerance 2^-9. All gains are nonnegative. This enables the declared
one-pass history/read/geometry path, not every Candidate-A descriptor channel.

Let the actual source resources be

$$
C=(1+u_0,1+u_1,1+u_2,1+u_3,5),\qquad
\sum_i u_i=0,\qquad |u_i|\le1/64.
$$

Charge is 9 and every resource is positive. Old W is uniformly w=exp(y), with
-1/256<=y<=0. This history symmetry is part of this theorem, not arbitrary W.
Physical source asymmetry enters through the leaf resources; it is not an ID,
frame, reset-state choice or random perturbation applied by the selector.

For canonical leaf-to-parent orientations, the predictor baseline is exactly

$$
v_{0,i}=4w(5w-19/4)+k u_i,\qquad k=w(19/4-w),\qquad
3825/1024\le k<4.
$$

The actual one-pass source read is the reviewed fresh predictor, normalized
star assembly, Hodge pushforward and fresh corrector, all at the same C,W.
Only its final selected current is consumed. No continuity step or retained
writer is run; gamma still enters the fresh pre-read functional. Incoming W
is retained history, not a new write performed by this investigation.

### Common source-read and derivative bounds

Here ||v0||<=17/8, ||B-transpose C||<9 and ||B-transpose B||=5. Each baseline
component is at least 14021/16384. With Q=1/256 and d_min=511/512, the same
read bound gives ||f0||<=||v0||/511. Hence

$$
\|v_1-v_0\|\le5\cdot9\,(17/(8\cdot511))^2
=13005/16711744<0.000779.
$$

This is much smaller than the positive baseline lower bound, so every
corrector baseline and selected inward activity remains positive. Also
||v1||<3. Both fresh contrasts obey |q|<Q and both conductance floors remain
inactive. With H1>=I the source residual is bounded by

$$
\|R_h\|\le(17/(8\cdot511))^2+(\tfrac12 Q\,3/d_{\min})^2
=865/16711744<0.000052<2^{-9}.
$$

The selected activity lower bound is
(14021/16384-13005/16711744)/(1+1/512)>0.85, whereas the activity norm is
less than 3/d_min. Consequently the D/10 error budget of the two-level
families below also preserves strict inflow; it is not just a score guarantee.

For the fresh read map F_y, the derivative deviation on both stages is at most
520/261121<1/500=:t. Work on the zero-sum leaf-u subspace, holding w fixed.
Its baseline derivative is kI, the derivative of B-transpose C is identity,
and the star derivative norm is bounded by 2||f||. Thus the geometry correction
has derivative bound

$$
G=5[2(17/(8\cdot511))t\,4\cdot9+(17/(8\cdot511))^2]
=1287053/417793600.
$$

The selected current can be written a(u)=k u+g(u), with

$$
\|Dg\|\le L_g=G+t(4+G)
=2315987953/208896800000<0.011087.
$$

This includes the fresh corrector and generated geometry; it is not a frozen
reference-current assertion. The source cube is convex and invariant under
leaf permutations, and g is equivariant. Apply the bound between u and the
state with components i,j exchanged. Since the output exchange has the same
two-component form,

$$
|g_i(u)-g_j(u)|\le L_g|u_i-u_j|.
$$

It follows that resource ordering survives the complete selected read:

$$
u_i>u_j\quad\Longrightarrow\quad
a_i-a_j\ge(k-L_g)(u_i-u_j)
\ge\frac{3111948001313}{835587200000}(u_i-u_j)
>3.7242(u_i-u_j)>0.
$$

Equal leaf resources give equal activities by equivariance. These uniform
statements hold throughout the declared gain/history box, not just at the
finite diagnostic corner.

### Two-level families and the non-vacuous negative control

For any declared pair of leaves take u=+delta on that pair and -delta on its
complement, where 0<delta<=1/64. The resulting exact activities have two
distinct levels, and the proposed source rule uniquely recovers that unordered
pair partition. All three pairings occur on such physical source families.
The minimum activity separation is 2 delta times the bound above, so the
conditional noise certificate is nonzero for every fixed positive delta.

For a distinguished leaf instead take u=(3delta,-delta,-delta,-delta), with
0<delta<=1/192. The source read now has a unique 1+3 activity grouping, which
the **same** rule returns. This is not filtered out using the old target result.
That old result concerned a different, symmetric source and its supplied
allocations; its exact target bounds are not transplanted to this new source.
The example shows what the rule chooses, not whether its new target would
return, admit, or be funded by any future allocator.

**The same non-inheritance applies to the new 2+2 case.** Neither class gains
the predecessor's target-support conclusion: the new source resources and
selected activities differ. For example, if a future allocator used

$$
\lambda_A=\frac{\sum_{e\in A}a_e}{\sum_e a_e},
\qquad \lambda_B=1-\lambda_A,
$$

the high/high versus low/low 2+2 blocks would receive unequal shares, not the
old symmetric 1/2,1/2 allocation. This is an illustration, not an adopted
allocator. Funding/allocation must be specified independently and the resulting
targets newly tested for admission/support. Those outcomes must not feed back
into the source selector or supply a retrospective size-class restriction.

At the fully enabled gain corner and y=-1/512, seven complete Decimal96 source
reads cover the symmetric source, all three pair families at delta=1/64, the
1+3 family at delta=1/256, and two signed/reordered representations. Independent
reduced-star scalar calculations check each canonical corrector baseline.

| Source | Selected activity levels, approximately | Proposed result |
| --- | --- | --- |
| Fully symmetric | 0.958645 on all four edges | Unresolved; seven minimizers |
| Two resource levels, 2+2 | 1.017127 and 0.900163 | Unique corresponding 2+2 |
| Two resource levels, 1+3 | 1.002506 and 0.944025 | Unique corresponding 1+3 |

The 2+2 activity gap is about 0.116964; the 1+3 gap is about 0.058482. Numerical
values are diagnostics of this declared law, not certified rounding enclosures
or native reads. The analytic result establishes that resource distinctions
are transmitted through feedback here; feedback does not create those
distinctions.

### Principal scientific limit: current has not beaten resource grouping

Direct resource grouping identifies the same two-level classes in this
special domain. Thus the result proves faithful transmission of physical
source asymmetry, **not a scientifically preferable partition signal in
current rather than resource**. Ordering preservation alone also does not
prove equality of variance-minimizing partitions for general multilevel
inputs. No new information or spontaneous formation is inferred from the
current projection.

Before granting refinement authority, the next bounded investigation should
make lawful source variables compete: resource grouping favors P1 while
nonuniform retained W, context or geometry makes the complete selected
current favor a distinct P2. The question is then which grouping has a
principled RC interpretation, not merely whether either rule is equivariant.
Such a family requires new source-read/domain checks; it is outside this
uniform-W theorem. Disagreement alone would not justify either choice.

## 6. Evidence, claim/debt boundary and the next scientific choice

The [checker](../scripts/certify_atc_source_partition.py) emits the
[certificate](../evidence/autonomous-topology-change/ATCSourcePartitionCertificate.json).
Exact checks enumerate all seven partitions and the S4 orbits, pressure the
degenerate symmetric geometry, and verify five synthetic activity cases under
24 permutations times 16 orientation actions: 1,920 rule checks. Thirty-two
bounded activity-error corners, six malformed-input rejections and two
out-of-domain cases accompany the seven complete finite source reads. These
small algebraic checks are not 1,920 native simulations or event trials.

The current forensic context still matches the admitted bundle. Six fresh
typed contract queries equal the retained bound traces and keep their
`indeterminate_requires_review` disposition. They supply source equation/stage
lineage, not authority for the new variance consumer. The reviewed predecessor,
accepted claims/debts and original source-law records remain unchanged.

From the repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python implementation/investigations/grc9v4-constitutive-design/scripts/certify_atc_source_partition.py
```

This prints a new deterministic record without overwriting retained evidence.
No target is built/read, no writer or ordinary step executes, and no event,
campaign, source admission extension or production edit occurs.

### Independent review disposition and evidence boundary

The supplied independent review reports no blocking mathematical defect. It
passes the S4 singleton obstruction, absence of a preferred generated contrast
direction, selector equivariance/exact ties, conditional robustness, uniform
A_OS ordering/separation and both two-level source-resolution witnesses.
It independently reran the checker's exact routines and all seven finite
source reads, reproducing the retained `exact_checks` and `decimal_diagnostics`
exactly, including coordinate/reorientation diagnostics. It also verified:

- Checker SHA-256:
  `10efc8860209aa78b74c13626a364fcb718d059cf5f2f4db133b35f57f64c180`.
- Certificate canonical digest:
  `787fd13f12f446dfd5313bec7fbe528bb3e88ac8bd8ec99c103817a0c63e6c5b`.

This is independent reproduction of those routines, not a claimed independent
end-to-end rerun of the repository forensic wrapper. The reviewed checker and
certificate remain unchanged, including the certificate's historical
pre-review status. This note records the current review disposition.

The review clarifications are explicit above: orbit-union freedom versus the
rule-specific seven-way tie; cardinality weighting; current-versus-resource
underdetermination; and non-inheritance of target support for **both** size
classes. One precision correction to the review itself is necessary: score
gaps shrink quadratically, but the sufficient error radius D/10 shrinks
linearly. These distinctions do not alter the checked mathematics or promote
`ATC-PARTITION-SOURCE-ACTIVITY-VARIANCE-v1` to a refinement law.

### Open scientific continuation and authority boundary

The symmetry obstruction and conditional source-information result bear on
DB-02/09's source-law/resolution front and DB-10's covariance obligation. The
grouping proposal gives partial research evidence relevant to DB-08's lift
question; it neither derives nor discharges CAN-B's functional/branch/mode
debts. It does not close DB-07/27's physical-refinement discrimination, resource/
history/target-integration obligations, or any of the thirty capability cells.
Formal claim/debt admission still needs the existing successor route.

The next step is the **competing resource/current source-information study**
above, not another target campaign or promotion of the variance rule. Establish
what physical information warrants a grouping, or choose a better source
invariant. Separately justify whether/when refinement should occur and its
source-only trigger plus child funding/allocation. Only after those choices
have independent justification should their selected targets be tested,
retaining the existing counterexamples and excluding target-outcome lookahead
from the selector. Coherent blocks do not prove that one vertex cannot
continue or that two vertices are supported.

If the source is perfectly symmetric, unresolved or invariant set-valued
output remains legitimate; it is not a failure to repair with labels or
numerical noise. CAN-F2 is unchanged. The claims/debts → topology proposal →
paper → specification → native 7T dependency remains unchanged.

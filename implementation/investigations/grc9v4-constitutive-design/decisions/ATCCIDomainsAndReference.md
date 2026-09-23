# A_CI — CI-2 combined domains and CI-3 research reference

2026-09-23. Status: CI-2 independently reviewed PASS and scientifically closed;
CI-3 core and closed-boundary correction independently reviewed PASS.
The later derived-witness provenance HOLD is corrected and locally checked.
Scoped claim/debt admission remains separate; no independent review of this
latest correction is claimed.
The user authorizes CI-2 then CI-3 after the paired
[A_PC adjudication](ATCPCClaimDebtAdjudication.md). No accepted A_OS/PC source
is changed. This successor continues the reviewed
[CI-1 anchor](ATCCIPCRealizationNativeProgram.md#4-ci-1--pc-1-a-shared-bound-two-different-dynamical-arguments),
not its discovery process. It does not add native code, paper/spec authority,
active-environment support or aggregate ATC-2 closure.

## CI-2: one assumption inventory

| Item | Declared sufficient scope |
| --- | --- |
| Scientific state | Candidate A, realization CI, authoritative C/W; no persistent carrier Z. |
| Graphs | Full five-vertex/four-edge paired source and six-vertex/five-edge double-star target; original WLS host positions, unit reference weights and ridge one. |
| Source root domain | Positive paired C of exact charge nine, contrast x>=29/10, paired W in [24/25,1]. The positivity-obstruction cone starts at x>=3. |
| Event current | 3<=x<=7/2, 0<=y<=1/50, strictly ordered decorated W sectors, positive selected-root inflows and a uniquely certified round-even dyadic share in [31/64,33/64]. |
| Event reset | Independent C/W; 3<=x<=7/2, abs(y)<=1/50 and W in [24/25,1], with no sector-order requirement and no vote in selection. |
| Transfer | Same current-selected share for both roles; independent exact-charge C maps; preserve every old W by lineage and initialize only bridge W=1. |
| Joint root | J=b(H)/(1-chi q(H)) and H=I+kappa_H Star(H^-1 chi q(H)J), in the symmetric star-supported ball of radius 1/4096 around I. |
| Target | Exact charge nine, X=norm(C-(3/2)1)<=3/2 and W in [24/25,1]; first step enters X<2/3 and subsequent steps contract. |
| Potential | Common C1 function on [0,9], with abs(p'-19/4)<=1/2048. Executable checks cover the quadratic subclass below. |
| Parameters | One fixed profile in the positive box below, not parameter switching during a run. |
| Requests | Any sequence h in [3/25,1/8], fixed physical tau_A=1/(8 log 2). Events take zero time and are not zero-duration ordinary steps. |

The parameter box is

$$
\alpha,\beta\in[1/4096,1/2048],\quad
\gamma\in[1/2048,1/1024],\quad
\chi\in[1/32,1/16],\quad
\kappa_H,\kappa_{Ah}\in[1/2,1].
$$

The executed subclass is p(c)=ac+nu c²/2, with
abs(a-19/4)<=1/4096 and nu in [1/131072,1/65536]. Its slope remainder is
at most 1/4096+9/65536<1/2048. All channels remain active. Shared
incidence/WLS/spectral and transfer-coordinate lemmas concern these same
graphs and operators, not the OS pass or PC carrier evolution. They are
rechecked algebraically; no realization-specific dynamics is inherited.

## 1. Uniform joint-root theorem before numerical iteration

Write m=24/25, K=1/2048, rho=1/4096, r=1/783, and
d=1-(1/16)/49. The fixed-H baseline is b. The post-C writer uses the
selected J, whereas the read conductance uses b. The following uniform
bounds account for both stages, separately from the fixed-point iteration.

| Domain | B0 | Lb for baseline response to H | Component-to-vector factor n |
| --- | --- | --- | --- |
| Source | 11/2 | 90 | 2 |
| Target entry | (4+(5/2)K)(3/2) | (125/8)(3/2) | 1 |

Here B=B0+Lb rho. Source Lb follows from kappa_Ah<=1,
norm(B_incidence)²=5 and norm(B_incidenceᵀ C)<=18. The target bound uses
norm(B_incidence)<=5/2 and X<=3/2. The source bare baseline estimate also
holds on the small x>=2.9 onset enlargement; this is not a theorem that every
such state enters the event region.

Source and target read/post-C writer exponent budgets are respectively

$$
E_s=\frac{9/2+(27/10)^2/2}{2048}
    +\frac{(B_s/d)^2}{2048},\qquad
E_t=\frac{3+2(3/2)^2}{2048}
    +\frac{(B_t/d)^2}{2048}.
$$

They are below 0.018904 and 0.021330, both less than 1-m. Thus the
conductance targets remain in [m,1], the floor is inactive, abs(q)<=1/49,
and abs(J-b)<=r abs(b). This is a bound from the declared H neighborhood,
not an assumption that an iteration happened to behave well.

For f(H)=H^-1 chi q J and T(H)=I+kappa_H Star(f(H)), define

$$
F=\frac{nrB}{1-\rho},\quad
L_R=\left(r+\frac{\chi_{max}\gamma_{max}B^2}{2d^2}\right)L_b,
\quad L_f=\frac{L_R}{1-\rho}+\frac{nrB}{(1-\rho)^2}.
$$

The derivative estimate uses abs(dq/db)<=gamma abs(b)/2. The normalized
star obeys norm(Star(f))<=norm(f)² and difference bound
(norm(f)+norm(g))norm(f-g). Consequently

$$
\|T(H)-I\|_F\le F^2<\rho,\qquad
\operatorname{Lip}(T)\le2F L_f<1.
$$

The [rational checker](../scripts/check_atc_ci_domains.py) obtains:

| Domain | Displacement upper bound | Contraction upper bound |
| --- | --- | --- |
| Source | <0.000199039 | <0.006012 |
| Target entry | <0.000058896 | <0.000975 |

The closed symmetric star ball is convex, complete and wholly SPD with
H>=(4095/4096)I. It therefore has one root, also throughout decreasing
kappa_H to zero, which identifies the reference-connected branch. This
mathematical homotopy does not admit a new zero-channel runtime profile.
The current block inverse is bounded by 1/d; the reduced H residual inverse
is bounded by 1/(1-L). The Schur complement gives regularity of the joint
root, not merely convergence of one numerical solver. Other roots outside
the admitted ball are not classified.

Decorated symmetries preserve the equations and this domain. Uniqueness
therefore implies exact root covariance and paired-state preservation.
Intersecting paired enclosures applies that theorem; interval overlap alone
does not establish exact pairing or charge.

## 2. Source obstruction, transfer, return and history limit

The actual CI source-current error is bounded by

$$
E=90\rho+r(11/2+90\rho).
$$

The paired incidence identity gives, while resources remain positive,

$$
x^+\ge(1+g)x,\qquad
g=\tfrac52h_{min}(19/250-6K-2E/3)
=\frac{16152197}{1002240000}>\frac1{64}.
$$

Since 3(65/64)^71>9, an unsplit positive continuation cannot survive all
71 further proposals. This is a resource-positivity obstruction, not a
root-solver failure. Evolving W remains in [m,1]; resetting W to one does
not remove the obstruction. CI-1's sharper fixed-profile result remains
unchanged; this bound covers the enlarged parameter/request box.

For either transferred role, deviations are
(-t+y,-t+y,-t-y,-t-y,2t+epsilon,2t-epsilon), with
abs(t)<=2/5, abs(y)<=1/50 and abs(epsilon)<=23/320. Thus initial X<3/2.
Each child also strictly funds its attached leaves. The least possible share
is 31/64, the largest leaf is (9-x)/5+1/50, and the parent is (9+4x)/5.
Their difference is increasing in x, so the minimum occurs at x=3:

$$
\min(C_{child}-C_{attached\ leaf})\ge
\frac{31}{64}\frac{21}{5}-\left(\frac65+\frac1{50}\right)
=\frac{1303}{1600}>0.
$$

`domain_bounds()` retains and checks this same bound for both independently
transported roles. It makes an existing transfer fact explicit; it does not
change the law or CI-2's scientifically closed disposition.
The reviewed bare polynomial expansions, bounded over the new request
interval, give leaf and parent envelopes

$$
L=(1-3h_{min}a_{min})\frac25
 +(1-h_{min}a_{min})\frac1{50}+\frac{h_{max}}4\frac{23}{320},
$$

$$
P=[2-6h_{min}(a_{min}-1/25)]\frac25
 +\frac{h_{max}}2\frac1{50}+(1-h_{min})\frac{23}{320},
\qquad a_{min}=7/4.
$$

Exact arithmetic verifies 4L²+2P²<(5/8)². This a_min is a bound on
the transfer polynomial coefficient, not the potential-slope parameter a.
Put B*=4+(5/2)K+(125/8)rho and

$$
e=h_{max}\tfrac52[(5/2)K+(125/8)\rho+rB_*].
$$

Then

$$
X_{first}<5/8+(3/2)e
=\frac{10771945}{17104896}<0.629758<2/3.
$$

On the full target mean-zero space the weighted spectrum is in
[m(7/16),73/16]. The multiplier 1+h lambda(lambda-19/4) is positive;
its largest value occurs at a spectral endpoint and h_min. Therefore

$$
X^+\le qX,\qquad
q=\max_{\lambda\in\{m(7/16),73/16\}}
 [1+h_{min}\lambda(\lambda-19/4)]+e
=\frac{577621057}{641433600}<0.900516<1.
$$

Resources stay above 5/6, W stays in [m,1], and every next root is admitted
by the same theorem. Moreover norm(H-I)<=sX² with
s=[rB*/(1-rho)]², hence C→(3/2)1, J→0 and H→I. The actual log writer
uses decay 2^(-8h), bounded above by 25/37<1; its drive tends to
exp(-3alpha/2), so W has that same limit. No persistent Z or PC recurrence
appears in this CI argument.

The theorem is conditional on a resolved admitted event and both roles in
their declared transfer domains. It is not a whole-box formation theorem,
a maximum domain, a repeated-event/non-Zeno result or a universal topology law.
Active external-edge environments are not investigated here. The accepted
A_OS environmental results are not CI evidence by analogy.

## CI-3: executable research conformance

The [new full-graph reference](../research/atc_ci_reference.py) consumes the
CI-2 constants before solving. It iterates the full H map and bounds the root
error by the outward residual divided by 1-L. It retains J, H, generated H,
both literal joint residuals, certificate/domain/profile/state identities and
a canonical digest of the complete selected root. A small iterate difference
is not used as the existence/uniqueness proof. Unresolved root enclosures
fail closed under a finite iteration budget.

One beat selects this root, performs one continuity update, rebuilds the
post-C descriptor, writes W from the same selected J and fixed physical tau,
and reconstructs the complete final-state root. The event recomputes that
fresh root, not the old current, OS reference pass or PC read. Both target
roles are separately reconstructed before the one publication assignment.

The [independent Decimal oracle](../research/atc_ci_oracle.py) imports no
reference scientific stages. It assembles incidence actions edge by edge,
WLS, dense solves, current closure and the H fixed-point map independently,
starting from a nonidentity geometry. Its numerical convergence is an
independent diagnostic, not a replacement Banach proof. The
[CI-3 checker](../scripts/check_atc_ci_reference.py) compares complete J/H
roots and all scientific stages for the source onset, both target roles at
both request endpoints, and two predetermined parameter corners. Corners
do not prove the continuous box. It also challenges vertex/edge reorder and
orientation changes, H-only corruption with unchanged J, stale descriptors
and substitution of poststate J into the writer.

The research owner/replay checks ordinary source onset → zero-time event →
ordinary target step → reset. Reset restores independently transported C/W;
ordinary steps do not rewrite it. Replay reexecutes selection, transfer and
both-role root admission, not just digest validation. Missing lineage, altered
profiles/requests/edge maps/root identities, actual reset-only domain failure,
injected final/reset-root failure and unexpected late exceptions challenge
full-publication atomicity. An event failure retains the committed postbeat
source, whereas an ordinary-step failure retains the prebeat publication.

The finite representation experiment starts independently from each actual
transported role and runs four declared requests (1/8,3/25,31/250,121/1000).
It rounds C/W to binary64 at publication and reconstructs both J and H;
geometry is not a stored coordinate. Requests and tau have separately stated
binary64 images. The lower request endpoint uses the next float above 0.12
to remain inside the exact interval. Internal calculations remain enclosed,
not all-binary64 arithmetic. Errors in C/W and reconstructed J/H are bounded
against the continued exact-real trajectory, not restarted from it each beat,
under a declared 1e-10 finite budget. Actual charge drift is retained, never
repaired or treated as exact charge nine. The target root neighborhood also
applies to these non-exact-charge diagnostic states; the exact-charge return
theorem is not thereby applied to them.

## Evidence, claims and continuation

### Closed-domain admission correction

The [independent review](../evidence/atc-ci-successor/CI2CI3-IndependentReview.md)
reproduced the mathematical certificate and the substantive CI-3 numerical
campaign. It identified a conformance defect, not a failure of the CI law:
outward intervals for exact rational endpoints can straddle a closed-domain
boundary. Testing their endpoints against that boundary rejects lawful input.

The CI-only [predicate witness](../research/atc_ci_state.py) now retains exact
rational C/W preimages and their exact x, y, history floor, charge, pairing and
target-radius predicates. Numerical arrays remain outward enclosures. Derived
states carry only operation-proved facts: incidence/uniqueness preserves
charge/pairing, the log writer preserves W>=24/25, the source obstruction gives
its contrast lower bound, and the transfer/entry/return lemmas bound target
radius. Other derived predicates remain conservatively interval-certified.
The selected root binds this witness as well as the numerical state, profile
and root certificate. No epsilon, domain shrinkage, changed root theorem or
change to the frozen A_OS/PC constructors is introduced.

This distinguishes the closed exact CI-2 domain from CI-3's computably
certified representation. All exact rational predicates at the reported
boundaries are supported. Arbitrary derived transcendental boundary facts
without an exact or operation witness, unresolved shares and finite-budget
root enclosures still fail closed; this is not a claim that every mathematical
domain input is algorithmically decidable on the fixed interval grid.

The [boundary regression checker](../scripts/check_atc_ci_boundaries.py), also
executed by the main CI-3 checker, covers x=29/10, event x=3 and 7/2, y=0
and ±1/50, source/target W=24/25 and exact target radius 3/2. It exercises
selection, transfer, first-step readmission and propagated invariant facts,
and rejects values outside by 2^-300, smaller than the enclosure grid.

Represented advance now requires point-valued dyadic inputs and exact C/W
pair equality **before** any symmetry-based enclosure intersection. Unequal
point pairs and merely overlapping boxes are rejected by both public and
direct advance interfaces. A paired represented state with measured nonzero
charge drift still runs as a diagnostic, never as an exact-charge witness.

The CI-2 proof bounds and claim routing remain unchanged, apart from adding
the explicit positive funding bound to the retained mathematical evidence.
CI-3's equations, numerical arrays, independent comparisons and finite error
observations likewise remain unchanged; the root/publication/replay identities
change intentionally because they now bind predicate provenance. The retained
review names the pre-correction identities, not the refreshed ones. Only the
unadmitted CI successor certificates are rebound; accepted PC/A_OS files are
not rewritten. The review's extra random samples remain reviewer-reported
diagnostics, not part of this local proof or an additional execution campaign.

### Derived-witness provenance correction

The [follow-up independent review](../evidence/atc-ci-successor/CI3-DerivedWitness-IndependentReview.md)
passes the boundary fix and reproduces the substantive scientific results.
It also demonstrates a real interface defect: the former `after_step(before,
data)` could label arbitrary paired numerical data as a charge-nine,
history-invariant successor without executing the operation. Both the Q=8.4
and W=0.8 counterexamples were reproduced locally. The actual retained
trajectory was correctly executed; the invalid permission to mint a witness
was the defect.

That promotion entry point is removed, not merely renamed private. Public
`step(before,h,profile)` delegates to `certified_step(before,h,profile)`, which
itself selects the root, executes continuity and the log writer, constructs
the successor facts, and admits the full restart root before returning.
Neither API accepts caller-supplied output, selected roots or proof receipts.
`advance_raw` returns numerical data only, with no path to promote that data
into a certified state. Transfer similarly computes its own affine result.

The derived witness retains the exact before-witness, selected full-root,
request, profile, numerical result and theorem digests. These are execution
provenance, not externally redeemable proof tokens. The constructor checks
that the result binding matches its arrays. Its private token remains an
internal research boundary, not security against Python monkeypatching or
deliberate private-token access.

Defense-in-depth construction checks require the numerical boxes to be
compatible with charge nine, the asserted history interval, source x/y and
target radius. These checks reject contradictions; they **do not** establish
operation provenance or turn overlapping enclosures into a proof.

The boundary checker adds the three requested wrong-charge, below-floor and
unrelated-target forgery controls, requiring rejection before certified-state
construction. An otherwise lawful unrelated target is still rejected, so
this is not just extra endpoint checking. Serialized execution metadata also
cannot mint authority. Six white-box contradiction tests separately pressure
the constructor guards; a real step verifies every retained execution binding
and the full restart-root binding. The existing boundary and representation
checks remain in force. Only the CI successor chain is rebound.

- [CI-2 certificate](../evidence/atc-ci-successor/ATCCI2DomainCertificate.json)
- [CI-3 certificate](../evidence/atc-ci-successor/ATCCI3ReferenceCertificate.json)
- [Evidence/reproduction notes](../evidence/atc-ci-successor/README.md)

`ATC-CI-DOMAIN-02` is a pending conditional successor of `ATC-CI-CHAIN-01`,
especially activating DB-05 joint-root branch/regularity and DB-19 actual
return. `ATC-CI-REFERENCE-03` follows that domain result and CI-0/CI-1, routing
bounded representation, charge, lifecycle and executable evidence to
DB-10/13/16/21/23/28. The certificates contain explicit reciprocal-routing
inputs for later adjudication, not new accepted graph nodes. DB-24 admission
and all global debts remain open. CI-2 is scientifically closed by its PASS;
CI-3's core/boundary PASS and locally validated provenance correction are recorded separately
from full closure/admission. The next action is scoped CI closure/adjudication,
not another discovery stage or CI+PC by inference.

From repository root, use `.venv/bin/python` with
`implementation/investigations/grc9v4-constitutive-design/scripts/check_atc_ci_domains.py`
and then `implementation/investigations/grc9v4-constitutive-design/scripts/check_atc_ci_reference.py`.
Each prints a fresh certificate to stdout and writes no evidence. Retained
records include exact source hashes and self-digests. The accepted PC checkpoint
and A_OS inventory are unchanged; no migration of their hashes is required.

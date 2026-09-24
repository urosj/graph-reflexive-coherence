# A_CI / A_PC — realization-native ATC closure

**2026-09-23. Status: CI-0/CI-1/PC-1 independently reviewed PASS within their
bounded scope; review hardening and committed-source reconciliation complete.
PC-2's partial-loss selection is superseded; a lossless relational-bridge
candidate has survived bounded pressure. The follow-up freezes it as the sole
PC-3 law, without a PSD fallback. PC-3 has independent scientific PASS for
its bounded complete chain and signed-domain return. PC-4 has independent
PASS for bounded paired-domain/reference/representation closure. The declared
A_PC paired research scope is ready for formal adjudication; CI-2/CI-3 remain
unfinished. Scoped claim/debt admission, including DB-24, remains pending.** No
CI/PC topology law has yet been formally source-admitted. The user replaces the earlier
“lift CAN-LSF from OS” framing. Start from each actual realization and reuse
proved lemmas only within their domains or through explicit error bounds.
No `src/` changes, native ATC, paper/spec propagation or aggregate ATC-2 closure.

This is one shared working note, one executable boundary audit and one
[retained record](../evidence/atc-ci-pc/ATCCIPCStepBoundaryAudit.json), rather
than a new document ladder for each successful calculation. The accepted
[A_OS ledger](../evidence/autonomous-topology-change/ATCAOSClaimDebtLedger.json)
and its scientific artifacts remain unchanged **from accepted commit
`5e1a63a`**, which already contains the user-approved relocation and rebuilt
uncommitted evidence chain. Pending CI/PC evidence is
separate from that frozen inventory; an A_OS query passing does **not** admit
or validate the new CI/PC physics.

## 0. Step-to-event causal contracts

The normative bases are the [CI/PC laws and complete-step transaction](../../../../specs/grc-v4-spec.md),
and the accepted [K0 research envelope](ATC1Acceptance.md). K0 already
distinguishes realization-specific reads. It attempts a source-selected event
only after a successfully committed positive ordinary beat, with no extra
physical time. The current/reset publication is available for transfer, but
reset state, receipt IDs and administrative history do not choose the event.
The scheduler is proposed research authority, not implemented native ATC.

### CI-0: the poststate joint root already exists

Authoritative state is `(C,W_A)`, with `Z_4=None`.
[ProvisionalCandidateCIStep](../../../../src/pygrc/models/grc_v4_ci.py)
independently admits the reset root, then the live root. The live selected
trial has stage `ci_trial`; continuity consumes its current exactly once.
[CandidateAWriter](../../../../src/pygrc/models/grc_v4_candidate_a.py)
then rebuilds the descriptor at final C and uses that **same selected current**
in the unchanged conductance/writer law. New W never supplies this beat's solve.

```text
(C_k,W_k) → R_CI(C_k,W_k)=(J_k*,h_k*)
          → one continuity → C' → W writer(C',D(C'),J_k*) → W'
          → restart=R_CI(C',W'; dt=0) → successful publication
          → event operand (C',W',J_evt*,h_evt*) → optional zero-time event
```

`step.restart` is a fresh `CandidateCIRoot` with `current=next_inputs.current`
and `dt=0`. It redoes bounded-domain admission and the literal joint residual;
the previous beat's root is not its seed. The proposed event consumes this
poststate root, or an equivalent read-only reconstruction bound to the same
complete state/profile/context. It must not consume the preceding root, an
OS corrector, or a fixed-reference current.

This is a **bounded numerical root with a contraction certificate and a
declared residual tolerance**, not exact arithmetic evidence that an arbitrary
research profile has a unique root. The forthcoming research theorem must
establish that root on its own domain, including final states and both targets.
Equivariance plus uniqueness implies root symmetry only if the decorated
action also preserves the admitted branch/domain. Matching tolerances alone
does not prove symmetry of represented roots.

Following review, the checker now compares the entire fresh and restart
`CandidateCIRoot`, including the selected point/geometry and certificate.
It retains a canonical selected-root digest covering recipe, J, h, generated
h, structural source, literal/analytic residuals, certificate bounds and
iteration count, plus the recipe/domain/certificate identities. Equality of
current alone is no longer the evidence criterion. Injected final-read errors
are realization-specific (`CIStageError` / `PCStageError`).

### PC-0: old history is relative to each read

Authoritative state is `(C,W_A,Z_4)`.
[ProvisionalCandidatePCStep](../../../../src/pygrc/models/grc_v4_pc.py)
first admits the reset read using **reset Z**, then reads the live old carrier.
The selected point has stage `pc_old_history`. It supplies both continuity
and the W writer. The W writer retains old Z; the carrier writer follows it.

```text
(C_k,W_k,Z_k) → h_k=H(K_base+Z_k) → fixed-h J_k and held S_k
             → one continuity → C' → W writer(C',D(C'),J_k) → W'
             → Z'=a Z_k+(1-a)S_k, a=exp(-dt/tau_PC)
             → restart=R_PC(C',W',Z'; dt=0) → successful publication
             → event operand (C',W',Z',h(Z'),J_evt) → optional event
```

`S_k` comes from the pre-continuity read, not from new C/W, not from the
poststate read, and not from the updated carrier. The restart rebuilds
geometry from **Z'**, revalidates the declared base chart/carrier envelope
and computes a new fixed-geometry current. Its stage is still
`pc_old_history`: Z' is the old committed history for the next prospective
beat, though it was written by the beat just completed. There is no CI-like
instantaneous structural-source addition to this geometry.

The proposed event therefore reads the committed `(C',W',Z')`, not the
previously consumed J or Z. Both roles retain their own carriers when their
targets are constructed. A uniform carrier-envelope certificate does not
establish invariance of the evolving base state `(C,W)` or target restoration.

### Publication boundary and failure discipline

[The lifecycle owner](../../../../src/pygrc/models/grc_v4_lifecycle.py)
consumes the provisional result, validates target/receipts/serialization, and
publishes once at the end. For non-OS products it exposes the poststate current
as `reconstructed_current`, not `reference_current`. That observation is not
an authoritative cached event operand: any later consumer must bind it to the
actual committed state or recompute it. Final read failure rejects the
ordinary step; there is then **no** K0 opportunity. Event target rejection
after an ordinary commit preserves that poststate, not the earlier pre-beat
state. The event is not a zero-duration ordinary step.

The [boundary checker](../scripts/audit_atc_ci_pc_boundary.py) executes both
provisional native numerical owners on a five-node/four-edge fixture with
distinct live/reset states and nonzero distinct PC carriers. It checks
selected versus reconstructed current, independent role reads, exactly one
continuity/W write, PC held-source ordering, fresh poststate reconstruction,
zero-duration identity, and injected final-read rejection. It does **not**
execute a live owner's ATC transaction or claim nonlinear CAN-LSF behavior.
Its shipped zero-site-derivative fixture is only a stage discriminator.

The generic PC test helper initially supplied a wider W chart whose uniform
source envelope rejected this four-edge fixture. The audit uses the explicit
W chart [1/2,1], which contains its actual live/reset histories and writes;
the full envelope check still executes. This fixture correction supplies no
claim about the nonlinear research profile or its future PC domain.

## 1. What is reused, and what earns a new proof

Default shell: exact decorated sectors, source-only prescription, operation
support, binary sector-to-site surgery, charge-conservative funding/transfer,
old-edge W lineage and bridge seeding, independent roles and atomic event
semantics. These are candidate reusable structures, not proofs of CI/PC
restoration. In PC the decoration includes the tensor Z and its induced
action; resource/W symmetry alone is insufficient. A proposed carrier map
must land in the target's star-supported carrier space, not merely have the
right matrix dimensions.

Re-derive event activity, obstruction and restorative domains from the
actual realization. In particular **do not insert the OS reference-stage
allocator operand into CI or PC**. Inward event-sector flux is a candidate;
its positivity, meaning and allocation bounds must follow from the new law.

Use the accepted active-channel research binding from
[G5–G6](ATCSectorChannelsAndRequests.md) and the
[G7 reference](../research/atc_sector_reference.py) as the initial physical
profile: alpha=beta=3/8192, gamma=3/4096, chi=3/64,
kappa_H=kappa_Ah=3/4, p(c)=(19/4)c+c²/131072,
tau_A=1/(8 log 2), initially dt=1/8, with the declared WLS descriptor.
These values specify the **first candidate**, not an admitted CI/PC domain.
Keep all these feedback channels active. PC additionally needs a declared
tau_PC, carrier ball and initial Z; preregister them before comparing outcomes.
The missing native nonzero-site-derivative evaluator is downstream Phase 9
work, not permission to substitute zero-potential physics here.

An explicit comparison bound may reuse strict A_OS margins, but vanishing CI
geometry coupling reduces to the matching fixed-geometry law, **not generally
to the finite-coupling OS corrector**. Establish the common limit, admitted
branch and uniform error first. Similarly a frozen-Z single PC read supplies
no theorem about repeated PC beats with changing Z.

## 2. Compressed closure sequence

| Stage | Single scientific deliverable | Stop condition |
| --- | --- | --- |
| CI-0 | Exact step/event boundary above, with bounded stage pressure. | Wrong stage, omitted writer or poststate admission. |
| CI-1 | One full-feedback paired-star causal chain: unique root, symmetry, evolving unsplit obstruction, source-only operation, independent both-role target roots and return; no-split/W-reset controls. | Report the first failed arrow; do not tune a target after selection. |
| CI-2 | One assumption inventory and combined source/root/target/request domain proof. | No transfer of OS bounds without a bound or same-law lemma. |
| CI-3 | Full-graph research reference, independent oracle, transaction/replay and finite represented-error bridge. | Numerical convergence is not root/domain certification. |
| PC-0 | Exact old-carrier/write/poststate-read boundary above. | Same-beat use of newly written Z or recomputed S. |
| PC-1 | Obstruction and exact sectors while both W and Z evolve; identify its constitutive support. | If fission cannot affect that support, stop this mechanism/domain. |
| PC-2 | Derive and discriminate a bounded covariant carrier map versus explicit carrier loss. | No reshape, map fitting or silent erasure. |
| PC-3 | Complete source-selected chain and both-role target PC continuation, with discriminating W/Z/both-reset controls. | If reset alone restores, do not claim fission is necessary. |
| PC-4 | One combined domain/envelope/asymptotic proof and executable-reference/representation check. | A finite trajectory is not indefinite return or carrier invariance. |

PC-2 treats transport and loss as **scientific alternatives**, not a choice
made because production already supports one. Preserve W separately from Z.
For transport prove the space/norm/covariance/lineage and target-admission
properties; for loss record both roles' complete discarded carriers and
zero initialization honestly. Section 6 retains the valid partial-loss control
whose selection was superseded. Section 7 now proposes a lossless relational
lift on the exact decorated domain; neither is previously accepted authority.

For each chain, check in order: actual-step fidelity; source obstruction;
operation support; source-only prescription; complete C/W(/Z) transfer;
realization-native target restoration. Put the support screen before expensive
allocation/history/return proofs. Failure stops that mechanism **in that
domain**, not the whole family. Generalize only after a complete anchor;
later use the coupled-environment class and retain the unaffected-support
negative control. CI+PC is a composition question after CI and PC, not a third
independent discovery campaign. None of this claims general source formation,
repeated-event/non-Zeno behavior, or all-ten-family completion.

## 3. Claim/debt routing from the start

These identifiers are pending research handles, not accepted graph nodes.
The inherited claims are queryable via the [ATC API](../tools/exploratory-side-tool/docs/ATCQueryGuide.md);
the boundary record preserves trace identities and authority classes. A_OS
claim ancestry supplies context, **not CI/PC support**.

| Handle | Present status | Obligation routing |
| --- | --- | --- |
| ATC-CI-STEP-01 | Staging reviewed PASS; full-root evidence hardened; not graph-admitted. | DB-03 stage, DB-04 consumer, DB-16 final admission. |
| ATC-PC-STEP-01 | Observed ordering with realization-specific failure pressure; not graph-admitted. | DB-03 stage, DB-04 consumer, DB-15 history, DB-16 final admission. |
| ATC-CI-CHAIN-01 | Independent review PASS for the bounded fixed-profile causal anchor; formal scoped admission pending. | DB-02 guard, DB-05 branch/regularity, DB-06 norm, DB-07 obstruction, DB-08 operation, DB-14/16 target, DB-19 return, DB-26 family scope. |
| ATC-PC-CHAIN-01 | Independent review PASS for evolving-carrier source obstruction/support; later event/return evidence is separate in ATC-PC-CHAIN-02. | DB-02/07/08 source/support, DB-13 charge, DB-15 carrier, DB-14/16 target, DB-19 return, DB-26 family scope. |
| ATC-PC-CARRIER-02 | Projection remains valid as an explicit-loss control; selection superseded after relational-lift pressure. | DB-15 conditional loss alternative; no unavoidable-loss or preferred-law claim. |
| ATC-PC-CARRIER-03 | Lossless relational lift on the exact decorated 2+2 domain; inverse, isometry, covariance, sign-fidelity continuity and both-role signed-carrier admission checked; integrated into reviewed PC-3, pending formal admission. | DB-15 scoped transport; DB-06 norm; carrier part of DB-16; DB-26 bounded A_PC only. Full readmission/return evidence is separate in ATC-PC-CHAIN-02, not retroactively part of PC-2. |
| ATC-PC-CHAIN-02 | Independent review PASS for PC-3's complete bounded causal chain; formal scoped admission pending. | DB-02/03/04/06/07/08/13/14/15/16/19/26; no automatic debt discharge. |
| ATC-PC-DOMAIN-04 | Independent review PASS for PC-4's combined paired-domain, positive parameter/request envelope and executable reference/representation result; ready for scoped adjudication. | Extends the PC-3 scope; DB-10 finite numerical bridge, DB-21 research transactions, DB-23 executable evidence, DB-28 finite resolution. DB-24 source admission remains open; no arbitrary-environment or native authority. |

All IDs above use the origin prefix `ATC7-DB-`. Existing A_OS dispositions
stay unchanged: DB-05 being inactive for OS does not exempt an implicit-branch
proof; DB-15's W result does not transport Z. DB-10 represented arithmetic,
DB-21 transaction, DB-23 executable evidence, DB-24 source admission and
DB-28 finite resolution remain explicit downstream obligations for each
proposed chain. Local results must be reviewed and source-admitted before
they become accepted CI/PC claims; no global debt is discharged here.

## 4. CI-1 / PC-1: a shared bound, two different dynamical arguments

The [local evaluator](../research/atc_ci_pc_anchor.py) and
[checker](../scripts/check_atc_ci_pc_anchor.py) produce the
[anchor certificate](../evidence/atc-ci-pc/ATCCIPCAnchorCertificate.json).
They import the accepted **fixed-geometry** A equations and outward interval
kernel, not its OS pass, event selector, target admission or research owner.
All active parameters and the nonlinear potential remain as declared above;
eta=kappa_c=zeta_A=1 and W_floor=1/2. Reference Hodge is identity and K_base=0.
Requests here are fixed at h=1/8. These results do not claim parameter-box,
environmental, native or represented-number conformance closure.

### 4.1 One declared geometry neighborhood

Put m=24/25, rho=1/4096 and r=3/3133. On the paired source with Q=9,
x>=29/10 and nonnegative resources, assume W in [m,1] and a symmetric
star-supported Hodge with `||H-I||_F <= rho`. The x>=29/10 enlargement only
admits the one ordinary pre-event step; the obstruction cone starts at x>=3.
The existing paired incidence algebra bounds each reference baseline by
B0=11/2, including the nonlinear site-law remainder. For fixed C/W,

$$
\|b(H)-b(\widetilde H)\|_2
\le L_b\|H-\widetilde H\|_F,
\qquad L_b=(3/4)\,5\,18=135/2.
$$

Here ||B||²=5 and ||BᵀC||<=18; the descriptor depends on C and fixed host
references, not H. Thus each baseline has magnitude at most
B=B0+L_b rho. The checker verifies that the read **and post-resource writer**
exponent budgets are below 1-m. Consequently G and W stay in [m,1], the
floor is inactive, |q|<=1/49, and

$$
d=1-\chi/49>0,\qquad |J-b|\le r|b|,
\qquad r=\frac{\chi}{49-\chi}=\frac3{3133}.
$$

For the target entry ball `||C-(3/2)1||<=3/2`, the same calculation uses
B0=(4+(5/2)K)(3/2), L_b=(375/32)(3/2), K=1/2048, and a vector rather
than per-component baseline bound. The inherited fixed-graph spectral,
descriptor and bare-polynomial identities are valid for this same potential
remainder and history interval; their use does not assume an OS step.

### 4.2 CI: certify the actual root before consuming it

Write f(H)=H⁻¹(chi q J) and T(H)=I+(3/4)Star(f(H)). Let n_b=2 on the
four-edge source (converting the component bound to a vector bound), and
n_b=1 for the target vector bound. The following rational estimates are
checked before numerical iteration:

$$
F=\frac{n_b rB}{1-\rho},\quad
L_R=\left(r+\frac{\chi\gamma B^2}{2d^2}\right)L_b,
\quad L_f=\frac{L_R}{1-\rho}+\frac{n_b rB}{(1-\rho)^2}.
$$

The derivative bound uses `|dq/db| <= gamma |b|/2` and the exact
fixed-geometry current denominator. The normalized star obeys
`||Star(f)||_F <= ||f||²` and has difference bound
`(||f||+||g||)||f-g||`. Therefore

$$
\|T(H)-I\|_F\le(3/4)F^2<\rho,
\qquad \operatorname{Lip}(T)\le(3/2)F L_f<1.
$$

Source displacement is below 0.00008375 and contraction below 0.001753;
target entry displacement is below 0.00002482 and contraction below 0.000290.
These are rounded-out summaries of exact rational checks. The symmetric,
star-supported closed ball is convex, complete and wholly SPD. It is a
self-map with a unique root; the same bounds hold when geometry coupling
is decreased to zero, identifying the reference-connected branch. No claim
is made about other roots outside this declared branch.
The fixed-h current block is invertible because d>0; the reduced H block
has inverse bounded by 1/(1-L). Their Schur complement therefore also gives
regularity of the joint root, not just uniqueness of an iteration limit.

The interval evaluator encloses that root using the **a priori** contraction
constant and `||T(H_n)-H_n||/(1-L)`, not an empirical convergence test.
It retains J **and H**, the domain/certificate digest, root error and the
digest of the full joint read. Decorated pair swaps preserve this ball and
residual. Uniqueness makes the exact root equivariant, so exact paired source
and target states stay paired. Intersecting paired interval enclosures uses
that theorem; equality of boxes is not asserted to prove physical symmetry.

### 4.3 Both realizations: evolving-history source obstruction

For x>=3, reuse only the exact bare source identity
`b_u+b_v >= (19/250)x` at p(c)=(19/4)c, with its nonlinear-potential bound
6Kx. Geometry and Read-Back now have the realization-independent error bound

$$
\varepsilon=(135/2)\rho+r\left(11/2+(135/2)\rho\right).
$$

Thus the **actual selected current** gives

$$
x^+\ge\left[1+\frac5{16}
 \left(\frac{19}{250}-6K-\frac{2\varepsilon}{3}\right)\right]x
>\frac{61}{60}x.
$$

The bracketed excess is greater than 0.01830. If resources remain positive,
the post-resource writer preserves [m,1], exact charge and symmetry preserve
the cone, and the next realization read is admitted. But
`3(61/60)^67 > 9`; hence positive unsplit continuation cannot survive all
67 further proposals. The conclusion is a positivity obstruction, not a
root-solver failure. W-reset-to-one remains in this cone and cannot remedy it.

For PC this requires a separate invariant-carrier argument. Preregister
`||Z||_F <= 1/3072`, tau_PC=1/(8 log 2), with symmetric star support.
Then H=I+(3/4)Z has exactly the declared geometry radius. The same fixed-h
read bound gives `||S||_F <= F² < 1/3072`. The held-source half-step
`Z^+=(Z+S)/2` preserves that ball while W evolves. This proves the PC source
bound through **actual carrier evolution**, not by freezing Z. Z-reset-only
and both-reset controls also stay in the invariant cone and fail to restore
positive unsplit continuation. No carrier map or target has been chosen.

### 4.4 CI: ordinary onset, native activity, transfer and return

The fixed prestate is `(x,y,u,v)=(59/20,1/100,97/100,99/100)`. Its guard
x>=3 is inactive. One full CI beat gives x about 3.221091, with the fresh
post-C/W root supplying the event activity. The independently held reset is
`(33/10,-3/200,49/50,97/100)` and is separately root-admitted.

An initially attempted OS-style auxiliary condition
`|b_u-b_v|/(b_u+b_v)<=1/64` fails here: the CI poststate ratio is about
0.025997. **That failed comparison is retained.** It is not a required CI
law: the old sufficient balance test was used to bound allocation, whereas
the joint-root inflows now supply that bound directly. No input, potential,
target or transfer interval was changed after this observation.

The proposed **CI-native source guard** uses x in [3,7/2], y in [0,1/50],
two exact decorated sectors with m<=u<v<=1, positive inward joint-root
currents, and a uniquely resolved round-even dyadic share in [31/64,33/64].
This is an explicit guard difference, not a claim that the old OS guard passed.
The resulting share is 33616/65536. It is computed once from the current
source and applied to both roles; there is no target search. The target
interval was justified by the inherited transfer algebra before inspecting
this point's target. Old W follows edge lineage; the new bridge alone gets W=1.

For any target supplied by that transfer domain, the bare first-step bound
is X^+<3/5 with initial X<3/2. The new uniform-geometry/current estimate gives

$$
e=\frac5{16}\left[\frac52K+\frac{375}{32}\rho
   +r\left(4+\frac52K+\frac{375}{32}\rho\right)\right],
\qquad X^+<\frac35+\frac32e<\frac23.
$$

On the return ball, the weighted target spectrum lies within
`[m(7/16),73/16]`; the bare polynomial `1+h lambda(lambda-19/4)` is positive.
Adding e bounds the true CI resource factor below 0.895541<9/10.
Resource remains above 5/6, histories stay in [m,1], and CI roots remain
unique on the declared ball indefinitely. As C approaches (3/2)1, J and the
descriptor vanish; the same log writer gives W→exp(-3 alpha/2).

For the two actual roles the interval first-step radii are below 0.408905
and 0.423467. Both target roots and their first post-write roots are explicitly
enclosed. Indefinite continuation rests on the bound above, **not** a long
finite trajectory. This closes the bounded CI-1 causal anchor subject to
review, not CI-2 parameter/environment generalization or CI-3 conformance.

### 4.5 PC: the support screen passes, but shape-preserving copying does not

The same fixed ordinary prestate uses Z=I/16384; reset independently uses
Z_reset=I/24576. One complete PC beat enters x>=3 while both W and Z change;
the event read uses the resulting carrier. The obstructing weighted star
stiffness has its high mode above the potential slope (`5m>19/4`), whereas
the split target's unweighted upper bound is below it (`73/16<19/4`). Fission
therefore changes the responsible constitutive support. Carrier erasure alone
does not remove the proved source obstruction.

The postbeat carrier has a strictly positive cross-sector entry Z[0,2], about
6.71073e-9. Those edges share the source parent but no target vertex after
fission. Naively embedding the old matrix and appending a bridge coordinate
would violate target star support. This is a concrete reason PC-2 must derive
a typed map or adopt explicit loss; neither choice follows from PC-1.
PC target restoration and any preference between transport/loss remain open.

### Limits and next work

These are fixed-profile, bounded exact-real results. Full-graph interval
evaluation retains deterministic enclosures, not a production numerical
policy or an independent second CI solver. CI-3 still owns independent oracle,
representation and lifecycle conformance. No new environmental class,
parameter sweep, repeated-event/non-Zeno or all-family claim is made.
The independent CI-1/PC-1 review and its corrections are recorded below.
After review of the proposed PC-2 law, PC-3 is the next PC causal obligation;
CI-2 should consolidate only changed domain/request assumptions, not restart
an A_OS-style ladder. Review PASS is not source admission or global closure.

## 5. CI-1/PC-1 review resolution

The [retained independent review](../evidence/atc-ci-pc/CI1PC1-IndependentReview.md)
passes both bounded scientific milestones, including full CI joint-root
evidence and realization-specific failure injection. Its independent dense
CI solver check and finite near-boundary pressure are **reviewer-reported**;
they are not represented as new locally retained execution certificates.
The [resolution record](../evidence/atc-ci-pc/CI1PC1ReviewResolution.json)
separates those observations from the locally executed corrections.

### 5.1 Exact domain premises are executable

Public research input admission accepts exact rational C/W and verifies
Q=9 and both pair equalities **before** interval conversion. The carrier
admission similarly checks exact symmetry, decorated pair permutations,
source/target star support, coverage and the Frobenius ball. Sub-grid
differences must not disappear into matching interval endpoints.

Non-point state enclosures are admitted only through an immutable internal
domain witness built by those exact constructors or the proved operations:
equivariant continuity/writer, charge-preserving split, or W-only reset.
Carrier witnesses propagate only through the equivariant held-source writer
or the proved event map. Raw interval arrays and hand-labelled witnesses are
rejected. Selected reads bind the actual source state and graph; a stale
read cannot advance another state. Equality of boxes is checked for internal
consistency, **never used to infer exact physical equality or charge**.
These are local typed mathematical interfaces, not a hostile-code sandbox
or a serialized/native admission system; CI-3/PC-4 retain those conformance
obligations. The algebraically certified transformations establish the
invariants, rather than a digest establishing a mathematical fact.

### 5.2 The provenance HOLD is stale against the accepted repository chain

The committed G7 reference record at `5e1a63a` and the current anchor bind
the **same current files**, which are byte-identical to that commit:

| Kernel | Accepted G7 and current SHA-256 |
| --- | --- |
| `certify_atc_sector_channels.py` | `8d0aa7016710d5e64935a3496fb9160689eda87e6c999b3336924b4f99c0828f` |
| `certify_atc_sector_state_domain.py` | `19b88f776b0084c9dd9f5220304080f685d25c98aeca0a30d7b572ae42f5ee2d` |
| `certify_atc_sector_readback_point.py` | `920eabaf709bd6dca2600a011f1cbba41594b88ce9c6cdacd44c76dca86d584f` |

That acceptance followed the explicitly requested relocation out of drafts
and reconstruction of the then-uncommitted hash chain. The review's quoted
older prefixes are not the frozen repository's G7 bindings. Reversing the
two evidence-path substitutions in the state-domain script reproduces its
quoted old `629d3295...` hash exactly. Reversing the single path substitution
alone does **not** reproduce the other two quoted prefixes; without their
exact historical bytes, no complete old-to-new diff is claimed for those
external versions. The decisive check is against the actual accepted commit
and G7 record, not an invented explanation of unavailable versions.

No accepted proof script or scientific certificate is restored or rewritten.
The resolution pins all inherited Python dependencies against the committed
G7 bindings and retains the review's original certificate/profile identities.
The hardened successor's numerical CI-1/PC-1 payload is compared with the
reviewed payload separately from newly added domain metadata and digests.
Formal scoped claim/debt adjudication remains distinct from this review PASS.

## 6. PC-2: surviving-star restriction with explicit partial loss

**Historical candidate, retained as a valid explicit-loss control. Its
selection is superseded by §7.** Nearest to the zero-bridge embedding is
not a proof of least information loss among all lawful transports. This
section's conditional projection mathematics is retained, not erased.

### 6.1 A new constitutive choice, not automatic authority

The reviewed PC-1 obstruction/support result is unchanged. The first proposal
used the following bounded event principle: **preserve the old structural memory
where the selected operation leaves its support meaningful; discard only
the unsupported component; invent no history on a newly created bridge.**
Use the already declared symmetric-star Frobenius norm, not a norm chosen
to make a target trajectory succeed. This additional minimal-change axiom
selects a unique map. V4's requirement of typed bounded covariant transport
alone does not select it: whole-carrier reset and other covariant maps remain
mathematically possible. No target current or target trajectory is used in
this choice. Proposed identity: `pc_star_restriction_partial_loss_v1`.

Let E be the signed isometric old-edge injection into the selected target
(old edge identities survive, and the new bridge has no source ancestor).
Let Pi_t zero matrix entries whose two target edges have no common vertex.
On the declared symmetric carrier space define

$$
\widetilde Z=EZE^\top,\qquad
L_{K4,\mathrm{evt}}Z=\Pi_t\widetilde Z,\qquad
D=(I-\Pi_t)\widetilde Z.
$$

For this four-contact star split, with edges ordered by the two sectors,

$$
Z=\begin{pmatrix}Z_{uu}&Z_{uv}\\Z_{uv}^\top&Z_{vv}\end{pmatrix}
\quad\longmapsto\quad
Z_t=\begin{pmatrix}Z_{uu}&0&0\\0&Z_{vv}&0\\0&0&0\end{pmatrix}.
$$

This transports history **partially**, not losslessly: D contains the removed
cross-child couplings. Bridge diagonal and couplings start at zero, not at a
copy or interpolation of old cross-sector memory. W is a separate channel:
all old W follows edge lineage; only bridge W is seeded at one.

### 6.2 Space, boundedness, covariance and admission

Pi_t is the orthogonal coordinate projection onto symmetric target-star
matrices. Therefore Z_t uniquely minimizes `||Y-EZE^T||_F` over that space.
The bridge coordinates of the embedded matrix are already zero, so the
minimizer invents none. The exact-real decomposition gives

$$
\|Z\|_F^2=\|Z_t\|_F^2+\|D\|_F^2,
\qquad \|L_{K4,\mathrm{evt}}\|_{F\to F}=1.
$$

The map preserves symmetry and target star support; its norm is exactly one
because nonzero surviving diagonal matrices attain equality. On the full
source symmetric space it has rank six and kernel dimension four. On the
paired decorated subspace those dimensions are four and one. In particular
no inverse reconstructs general cross-sector history from Z_t alone.
For this split, positive semidefinite input also stays positive semidefinite
because the retained blocks are principal blocks; PSD is not required of
general V4 signed structural increments.

For signed source/target edge-coordinate changes Q_s,Q_t, use
`E'=Q_t E Q_s^T` and the correspondingly relabelled target support. Then

$$
L'(Q_sZQ_s^\top)=Q_tL(Z)Q_t^\top,
\qquad D'=Q_tDQ_t^\top.
$$

This follows because signed permutations commute with the appropriately
relabelled support mask; orientation signs change entries but not incidence
support. Vertex relabeling and exchange of the two children also commute.
Source within-sector symmetries restrict to target within-sector symmetries.
The research map is typed by both graphs, signed injective lineage, carrier
norm and the explicit policy. Fixed-graph covariance alone was not used to
infer this topology-changing law.

If `||Z||_F<=1/3072`, then `||Z_t||_F<=1/3072` and

$$
\|H_t-I\|_F\le\frac1{4096},\qquad
\lambda_{\min}(H_t)\ge1-\frac1{4096}>0.
$$

Thus the carrier and its induced geometry are admitted on the target.
This is **carrier/geometry admission only**: complete target C/W/Z readmission,
the actual PC event-current allocation, and indefinite PC restoration remain
PC-3. PC-2 does not infer them from CI return or the spectral support screen.

### 6.3 Explicit loss and the reset alternative

The research event evidence keeps each role's complete source carrier,
transported carrier and discarded matrix with content digests and the loss
norm. Map non-injectivity and actual loss are separate facts: a particular
input can lie in the preserved subspace even though the policy is lossy.
The loss evidence concerns information absent from future constitutive
state; retaining D in an explanatory receipt does not restore that memory
to the dynamics. Interval uncertainty is reported as `not_excluded`, never
silently rounded to zero loss.

Whole-carrier reset is the second, typed candidate
`pc_whole_carrier_loss_zero_v1`. It is covariant, norm-bounded and admissible,
but discards all memory rather than only unsupported memory. It agrees with
the proposed restriction exactly when the preserved component is zero.
Its squared distortion exceeds that of restriction by `||Z_t||_F^2`.
This discriminates the alternatives using source history and topology,
not observed restoration. Neither reset nor projection is obtained by
untyped array resizing; production's existing reset policy does not settle
this new scientific choice.

The [PC-2 certificate](../evidence/atc-ci-pc/ATCPCCarrierEventCertificate.json)
uses the original live postbeat carrier and the independently supplied reset
carrier. Restriction proves nonzero discarded live history but exactly zero
discarded reset history; it preserves nonzero history in both. Full reset
discards nonzero history in both. This asymmetry is retained, not flattened
into one event-wide loss flag. Both role targets have fresh zero bridge memory.

### 6.4 Evidence and scope

The [map kernel](../research/atc_pc_carrier_event.py) and
[focused checker](../scripts/check_atc_pc_carrier_event.py) retain exact
rational pressure on every symmetric source basis, a dense signed matrix,
signed permutation generators on both graphs, vertex relabeling,
Pythagorean decomposition, idempotence and malformed lineage rejection.
They also exercise the review's exact-input domain rejections and the
two-role carrier witnesses. These are finite checks of the separately proved
linear statements; they do not replace the general proof.

The projection is a **valid control, no longer the preferred PC-2 candidate**.
The new pressure shows why this nearest-embedding criterion does not justify
losing the relational mode on the domain already proved in PC-1. Do not
proceed to PC-3 with this selection by default. No runtime authority or
automatic DB-15 discharge follows from either candidate.

## 7. Revised PC-2: lossless relational-bridge lift

The [pressure review](../evidence/atc-ci-pc/PC2-RelationalLift-PressureReview.md)
refutes selection of the partial-loss map on the actual PC-1 decorated
domain, not its conditional projection theorem. Its reported randomized
campaigns are retained as reviewer reports, not relabelled as local runs.
The [new certificate](../evidence/atc-ci-pc/ATCPCRelationalLiftCertificate.json)
retains our exact local pressure and the qualifications below.

### 7.1 Domain, meaning and the missing target coordinates

In parent-incidence-normalized coordinates the exact two-sector source is

$$
Z_s=\begin{pmatrix}
a&b&c&c\\b&a&c&c\\c&c&d&e\\c&c&e&d
\end{pmatrix}.
$$

Its invariant carrier space has five independent real coordinates.
The symmetric target-star space has eleven coordinates before decoration;
its decorated subspace has seven: two coordinates in each old sector block,
one bridge coupling per sector, and the bridge diagonal. Therefore the
source's relational scalar c is not excluded by target capacity or support.
The earlier restriction lost it because of the extra zero-bridge-memory
condition, not a no-go theorem.

New proposed continuity principle: **persistent structural history follows
the surviving relation as its support changes.** Within-child memory follows
old-edge lineage; the former shared-parent inter-sector relation moves to
bridge incidence. This is an explicit constitutive proposal, not a theorem
that all conceivable histories or representations admit such transport.
There is no independent new bridge self-history, so its diagonal stays zero.

### 7.2 Incidence-normalized map and explicit inverse

Let `U,V` each contain two source edges at parent p. With source incidence
`sigma_i=B_s[p,i]`, define the exact scalar

$$
c=\frac14\sum_{i\in U,j\in V}\sigma_i\sigma_j Z^s_{ij}.
$$

Admission requires all four normalized cross entries to be **exactly this
same scalar**. Averaging a symmetry-breaking block must not grant admission.
For each surviving edge use signed lineage `(i -> bar(i), ell_i)`, and write
`tau_i=B_t[p_X,bar(i)]`, `tau_b^X=B_t[p_X,b]` at its target child. Preserve
the within-sector blocks as `ell_i ell_j Z^s_ij`. Set the forbidden old-edge
cross-child entries to zero, and define

$$
(L_{\rm rel}Z)_{\bar i b}=(L_{\rm rel}Z)_{b\bar i}
  =\tau_i\tau_b^X c,\qquad (L_{\rm rel}Z)_{bb}=0.
$$

All new nonzero entries share a target child with the bridge. In the retained
canonical orientations this is

$$
L_{\rm rel}Z_s=\begin{pmatrix}
a&b&0&0&-c\\b&a&0&0&-c\\
0&0&d&e&c\\0&0&e&d&c\\-c&-c&c&c&0
\end{pmatrix}.
$$

The inverse on the image recovers

$$
c=\frac14\sum_{i\in U\cup V}\tau_i\tau_b^{X(i)} Z^t_{\bar i b},
\qquad Z^s_{ij}=\sigma_i\sigma_j c\quad(i\in U,j\in V),
$$

and reverses signed lineage on the old blocks. Hence `R_rel L_rel=I`.
The executable inverse verifies image membership, including zero bridge
diagonal and consistent bridge couplings; it does not interpret arbitrary
target carriers as fission preimages. Later PC evolution need not stay in
this event image, so this inverse is **not** a general time-reversal claim.

### 7.3 Isometry, covariance and the sign qualification

The source cross block and transpose contribute `8c^2` to the squared
Frobenius norm. The four target bridge couplings and transposes contribute
the same `8c^2`; the within-sector contribution is unchanged. Thus

$$
\|L_{\rm rel}Z\|_F=\|Z\|_F,\qquad
\|Z\|_F\le\frac1{3072}\Longrightarrow
\lambda_{\min}(I+\tfrac34L_{\rm rel}Z)\ge\frac{4095}{4096}>0.
$$

For independently changed signed source/target edge coordinates, incidence
signs and signed lineage transform together. The normalized c is invariant;
each target bridge coupling gains precisely its two target orientation
signs. Therefore `L'(Q_s Z Q_s^T)=Q_t L(Z) Q_t^T`. Vertex relabeling and
exchanging the two child/sector names commute as well. The inverse has the
same covariance. This proof changes coordinates, not the physical event.

**Qualification to the review's near-uniqueness statement:** incidence
covariance does not fix the remaining global relational polarity. Negating
all four bridge couplings also gives an equivariant isometry with an explicit
inverse and zero bridge diagonal. The two maps are distinct on the **same**
oriented event; reversing a coordinate also transforms its incidence, and
does not remove this constitutive freedom. The kernel and tests retain both.
The [follow-up review](../evidence/atc-ci-pc/PC2-SignFidelity-And-SignedDomain-Review.md)
now resolves this freedom by making **relational sign fidelity an actual
continuity obligation**, not just choosing a binary implementation setting.
Define the target observable independently of the selected polarity:

$$
c_s=\frac14\sum_{i\in U,j\in V}\sigma_i\sigma_j Z^s_{ij},\qquad
c_t=\frac14\sum_{i\in U\cup V}\tau_i\tau_b^{X(i)} Z^t_{\bar i b},
\qquad \boxed{c_t=c_s}.
$$

Both observables are orientation-invariant. For the two previously
admissible linear isometries, `c_t=+c_s` and `c_t=-c_s`, respectively.
For nonzero c the negative branch inverts the signed historical relation
and is rejected by continuity; for c=0 the two maps coincide, so the zero
case does not determine a sign. With the retained linearity, block
preservation, child exchange, zero bridge diagonal and isometry conditions,
this continuity law fixes the displayed map on the whole declared domain.
`pc_star_fission_relational_lift_lossless_v1` enforces it in both role
receipts. It remains **new cross-topology constitutive content**, not a
consequence of covariance or ordinary V4 alone. No target performance is
used to select polarity. The algebra proves equality of the exact observables;
equal retained interval endpoints are a consistency check, not its proof.

### 7.4 Both actual roles and PSD pressure

For the original live postbeat carrier, c is about `6.7107258103e-9`.
The lossless map moves its nonzero contribution onto the bridge; it does not
discard it. The target is admitted by the existing carrier constructor,
the inverse reproduces every retained source enclosure, and the source and
target interval norm upper bounds are equal. The independent reset has c=0,
so the relational lift equals the restriction control there. Projection and
whole reset remain separately executed explicit-loss controls: projection
loses nonzero live history, while whole reset loses history in both roles.
W history and bridge W=1 remain a separate channel throughout.

The linear lift need not preserve positive semidefiniteness of Z. In fact
any nonzero bridge coupling together with zero bridge diagonal gives a
negative two-by-two principal minor `-c^2`. This is certified for the actual
live role, not hidden by a floating eigenvalue tolerance. Its geometry H
remains safely SPD by the uniform norm bound above. The existing V4
[structural space](../../../../src/pygrc/models/grc_v4_geometry.py) permits
signed/indefinite increments; it does not require Z itself to be PSD.
The domain distinction is now explicit. For this fixed target and decorated
action, write

$$
\mathcal Z_{\rm event}^{\rm dec}
=\{Z=Z^\top:\ Z\text{ is target-star-supported and exactly decorated},
\ \|Z\|_F\le1/3072,\ I+\tfrac34 Z\succ0\}.
$$

The SPD condition is retained semantically and follows quantitatively from
the radius bound here. No additional requirement $Z\succeq0$ is imposed. The PSD
part is $\mathcal Z_{\rm event}^{\rm dec}\cap\{Z\succeq0\}$. Ordinary
evolution from the present PSD initialization stays in that cone while
admitted, since its writer averages PSD structural sources. Its **reachable
subset** is not asserted to equal the entire PSD intersection. An event
translates old history to a graph that did not previously exist; it need not
manufacture a fictitious ordinary target-graph past.

**Correction to the follow-up review's concluding claim:** the lift's image
is contained in this ball; it is not the whole ball. The carrier image has
dimension five inside the seven-dimensional decorated target space, subject
to zero bridge diagonal and equal incidence-normalized bridge couplings.
Both signs of a sufficiently small nonzero bridge diagonal give admitted
target carriers outside this image. The checker admits them as carriers and
rejects them as inverse preimages. Full undecorated target-star space has
dimension eleven and is not silently added to this scientific scope.

PC-3 must prove postevent continuation from the signed event image inside a
justified invariant signed target domain containing it. Ordinary writing may
leave the five-dimensional image, so PC-3 cannot repeatedly assume inverse-
image constraints or PSD. It must establish complete C/W/Z and both-role
readmission and restoration, not assume target historical realizability.
Information recovery and isometry do not assert identical currents, energy,
or a commuting source/target writer.

The review's optional nonlinear PSD control also has sound bounded algebra.
For a PSD decorated input let `A=a+b`, `D=d+e`; then `A,D>=0`,
`AD>=4c^2`, and the antisector eigenvalues are nonnegative. In the canonical
orientation set

$$
f=-c\sqrt{\frac A{A+D}},\qquad
g=c\sqrt{\frac D{A+D}},\qquad h_b=\frac{4c^2}{A+D}.
$$

These are the U/V bridge couplings and bridge diagonal. When `A+D=0`, use
zero; if only A or D vanishes, PSD forces c=0 and again all three are zero.
For positive A,D the reduced three-by-three block has Schur complement
`h_b-2f^2/A-2g^2/D=0`, so it is PSD. The old blocks recover A,D, and any
nonzero scale in f or g recovers c, proving injectivity on this PSD domain.
Its new norm contribution satisfies

$$
4f^2+4g^2+h_b^2
=4c^2+\frac{16c^4}{(A+D)^2}\le5c^2\le8c^2.
$$

This control shows that adding PSD preservation would not force loss either.
It is **predeclared but not selected or implemented as the event policy** here; the local
checker pressures its exact squared Schur/norm algebra and degeneracies,
not a new nonlinear numerical transport campaign. PSD preservation would
require a separate explicit domain/policy decision, not a silent change.

There is an additional consequence of sign fidelity: this nonlinear control
is not interchangeable with the main law under the same target observable.
For nonzero c it gives

$$
c_t=\frac c2\left(\sqrt{\frac A{A+D}}+\sqrt{\frac D{A+D}}\right)\ne c.
$$

The scale lies at most at `1/sqrt(2)`, while c is still recoverable through
the control's nonlinear decoder. An exact retained example with
`A=9q,D=16q,c=q,q=2^-18` gives `c_t=7c_s/10`, and the same sign-fidelity
check rejects it. Thus injective information preservation is not identical
to preservation of this particular signed relational readout.

The [PC-3 scope review](../evidence/atc-ci-pc/PC3-SolePolicy-ScopeReview.md)
now freezes `pc_star_fission_relational_lift_lossless_v1` with `c_t=c_s` as
**the sole PC-3 carrier policy**. The PSD construction remains a mathematical
pressure control: its relational-continuity contract is undeclared, and it
is not an admissible fallback inside PC-3. A genuine failure of the signed
lift is retained as failure. Any PSD-preserving successor requires its own
preregistered cross-topology contract and new bounded investigation (PC-2b),
not a rescue selected after examining PC-3 outcomes. Do not silently relax
`c_t=c_s` or tune coefficients. Failure to obtain a proof alone is not
evidence that the continuation law is false.

### 7.5 Genuine generic obstruction, not a universal loss claim

Outside the decorated domain the source cross block has a double-odd mode
`[[1,-1],[-1,1]]`. Under the within-U and within-V swaps, the associated
symmetric source tensor z satisfies `g_U z=-z`, `g_V z=-z`, and
`g_U g_V z=z`. The full target-star carrier space has no double-odd component:

$$
P_{--}=\tfrac14(I-g_U-g_V+g_Ug_V)=0.
$$

If F is any equivariant map on the unrestricted source domain, then F(z)
is fixed by `g_Ug_V`. On this target space that implies it is also fixed by
g_U. Consequently `F(-z)=g_UF(z)=F(z)`: F cannot be injective. This argument
does not assume F is linear or continuous. It is restricted to this fixed
target, carrier-only output and symmetry action; changing the target state
representation or event problem can change the conclusion.

The exact PC-1 domain excludes this double-odd mode, as well as the other
nontrivial cross-sector modes. The proposed lift explicitly rejects them
rather than averaging them away. The no-go does not prove projection is
the only, or automatically best, fallback on a wider domain.

### 7.6 Falsification evidence and next boundary

The [new kernel](../research/atc_pc_relational_lift.py) validates the fission
incidence diagram and signed surviving-edge lineage. The
[checker](../scripts/check_atc_pc_relational_lift.py) verifies dimensions,
the complete five-basis Gram matrix, an independent canonical matrix formula,
the inverse, isometry, image rejection and the generic mixed-mode ceiling.
It checks both polarities on the signed group generators and all five source
bases. It exhausts all 384 signed source frames and all 3,840 signed target
frames separately on a dense signed input. Their independent commuting
actions and the algebraic covariance proof cover combined changes; **this
is not reported as 1,474,560 Cartesian executions**. Child exchange, arbitrary
vertex labels and the actual role enclosures are checked separately.

The sign-fidelity follow-up checks the invariant readout in every signed
frame, rejects the opposite branch for both signs of nonzero c, and accepts
the coincident zero case. Both actual role receipts retain c_s and c_t.
Additional exact cases distinguish carrier admission from inverse-image
admission and reject the PSD alternative under the same linear observable.

The revised result survives this bounded pressure and is ready for review.
`ATC-PC-CARRIER-02` is a valid but superseded selection; conditional
`ATC-PC-CARRIER-03` records this lossless candidate and its narrower domain.
Neither is admitted graph authority or a global debt closure. The subsequent
scope review authorizes direct PC-3 work under this sole carrier choice;
§8 supplies actual PC source allocation, complete both-role target readmission
and evolving-W/Z restoration, subsequently reviewed PASS. No new
obstruction search, CI/PC-1 rerun campaign, native ATC, or paper/spec change.

## 8. PC-3 — fixed causal experiment

Before target evaluation, freeze the selected map
`pc_star_fission_relational_lift_lossless_v1`, continuity `c_t=c_s`, and
**no policy switching or PSD fallback within PC-3**. Retain the original PC-1
profile, graph, both roles, nonzero carriers and `h=1/8`; do not search a
new source or target. Event allocation must come from the fresh postbeat PC
fixed-geometry read, not the CI root or the OS reference pass. Prove target
continuation in the seven-dimensional signed decorated carrier domain,
starting from the five-dimensional event image, not invariance of that image.

The [research kernel](../research/atc_pc_causal_chain.py) implements that
fixed experiment; the [checker](../scripts/check_atc_pc_causal_chain.py) and
[certificate](../evidence/atc-ci-pc/ATCPC3CausalChainCertificate.json) retain
the results. The PC-3 contract is explicit in the kernel and digest-bound in
the record. No CI solve or OS pass is called: the checker replaces both with
raising sentinels throughout execution. The shared fixed-geometry A read is
legitimate common mathematics, not an OS realization substituted for PC.

### 8.1 Source-selected event and independent role readmission

The original live fixture starts with contrast `x=59/20<3`,
`y=1/100`, `u=97/100`, `v=99/100`, and `Z=I/16384`. One positive PC beat
reads from old Z, writes C and W once, writes `Z'=(Z+S)/2` using the held
old-state structural source, and reconstructs the fresh committed-state read.
That read, not the consumed prebeat current, activates the source event and
selects

$$
\lambda_{\rm PC}=\frac{33615}{65536}.
$$

This differs from CI-1's `33616/65536`; no CI allocation is imported. The
source-only selector has no reset state or target in its arguments. It uses
the positive U/V inward PC currents and their unique dyadic share within
the already proved interval `[31/64,33/64]`. Both roles separately satisfy
`3<=x<=7/2`, `|y|<=1/50`, `24/25<=u,v<=1`. The independent reset fixture
remains `x=33/10`, `y=-3/200`, `u=49/50`, `v=97/100`, `Z=I/24576`.

Each role's own parent resource is divided by the same current-selected
share. Its own four old W entries follow exact surviving-edge lineage;
only the new bridge gets W=1. Its own Z is transported by the sole lossless
law, preserving its norm and relational scalar. Exact charge is still 9
by the linear split identity. Each complete target C/W/Z receives its own
full fixed-H PC read before any ordinary target beat. The event has zero
duration and executes no additional ordinary W or Z writer. These are
research preparation/readmission checks, not a native atomic-owner claim.

### 8.2 Uniform signed-carrier continuation, not an image constraint

Let `M=24/25`, `R=1/3072`, `rho=1/4096`, `K=1/2048`, and
`r=3/3133`, as in the fixed PC-1 profile. On the decorated target set
write `X=||C-(3/2)1||_2`, `z=||Z||_F`. For every signed, symmetric,
star-supported decorated Z with `z<=R`,

$$
H=I+\tfrac34Z,\qquad \|H-I\|_F\le\rho,
\qquad \lambda_{\min}(H)\ge1-\rho=4095/4096.
$$

The shared pointwise read estimates hold for **every** H in this ball,
not just a CI root. On `X<=3/2`, `M<=W<=1`, set

$$
B=4+\tfrac52K+\tfrac{375}{32}\rho,
\qquad s=\left(\frac{rB}{1-\rho}\right)^2.
$$

The baseline obeys `||b||<=BX`, the Read-Back correction obeys
`||J-b||<=r||b||`, and the target-star source therefore obeys

$$
\|S\|_F\le sX^2,\qquad
s(3/2)^2<0.000033092<R.
$$

The PC writer, with the unchanged `h=1/8` and
`tau_PC=1/(8 log 2)`, gives

$$
z^+\le\tfrac12z+\tfrac12sX^2<R
\quad\text{when }z\le R,\ X\le3/2.
$$

It preserves symmetry, decorated equivariance and star support, so the
**seven-dimensional signed carrier ball**, not the five-dimensional event
image, is invariant. Neither Z PSD nor an event inverse is needed for an
ordinary step. The actual live event Z has a negative principal minor;
the proof covers it directly.

For resource continuation, the bare paired-target Laplacian has nonconstant
spectrum in `[M*7/16,73/16]`. Put `a=19/4`, `h=1/8`,

$$
q_0=\max_{\ell\in\{M(7/16),73/16\}}
       \{1+h\ell(\ell-a)\},
$$

$$
e=\frac5{16}\left[\frac52K+\frac{375}{32}\rho+
r\left(4+\frac52K+\frac{375}{32}\rho\right)\right],
\qquad q=q_0+e<0.895541<0.9.
$$

The multiplier is positive throughout that interval
(`1-ha^2/4>0`); convexity puts its maximum at the endpoints. The error e
bounds nonlinear-potential, geometry and Read-Back contributions uniformly
in the changing W and signed Z. Thus `X^+<=qX`; no fixed eigenbasis or
commuting history evolution is assumed.

For first entry from the transferred roles, the earlier **bare algebraic**
transfer lemma is rechecked exactly, not imported as an OS trajectory:
with `t<=2/5`, `|y|<=1/50`, split imbalance `|epsilon|<=23/320`, and
`a_min=7/4`, its coordinate envelopes are

$$
L=\tfrac{11}{32}t+\tfrac{25}{32}|y|+\tfrac1{32}|\epsilon|,
$$

$$
P=\left[2-\tfrac34(a_{\min}-1/25)\right]t
 +\tfrac14(2-a_{\min})|y|+\tfrac78|\epsilon|.
$$

They give `4L^2+2P^2<(3/5)^2` and initial
`X^2<=12t^2+4y^2+2epsilon^2<(3/2)^2`. Adding the full PC error gives

$$
X_{\rm first}<\frac35+\frac32e<0.603711<\frac23.
$$

Inside this return ball every resource is greater than `3/2-2/3=5/6`.
The read denominator stays at least `1-chi/49>0`. The read and post-C
conductance-writer exponent budgets are less than `1-M`, so their targets
are in `[M,1]`; `W^+=sqrt(W G)` preserves that interval. The writer uses
the same selected J with the post-continuity descriptor, as required.
These bounds close the joint induction on resources, W, carrier, geometry
and fresh readmission. This is indefinite **exact-real** continuation,
not a claim that outward interval widths or floating-point implementations
remain controlled for infinitely many executions.

The fixed-domain asymptotics follow as well. Index n from entry into the
return ball. Then `X_n<=q^n X_0` and, since `q^2>1/2`,

$$
z_n\le2^{-n}z_0+
\frac{sX_0^2}{2}\frac{q^{2n}-2^{-n}}{q^2-1/2}\longrightarrow0.
$$

Consequently H tends to I and the currents and descriptor tend to zero.
The log-half W writer has limiting target `exp(-3 alpha/2)`, so each W
tends to this positive value while C tends to `(3/2)1`. No finite-time
return to Z PSD is asserted.

### 8.3 Retained witnesses, controls and honest boundary

The checker executes one source beat and **two target beats per actual
role**, retaining complete C/W/Z, H, potential, baseline, current, Read-Back,
held structural source and fresh poststate reads. Rounded-up summary bounds
are below; the certificate retains outward rational enclosures.

| Role | Target beat | Resource radius X, upper | Carrier norm, upper |
| --- | --- | ---: | ---: |
| Current | 1 | 0.408988 | 0.000030732 |
| Current | 2 | 0.147500 | 0.000015374 |
| Reset | 1 | 0.423482 | 0.000041850 |
| Reset | 2 | 0.157441 | 0.000020964 |

Both roles acquire a strictly positive bridge diagonal after their first
ordinary target beat. This proves they leave the event image; the inverse
rejects them while complete ordinary PC readmission succeeds. H, W and Z
all evolve, and selected old-Z geometry differs from final new-Z geometry.
The second-step contraction is checked against a lower enclosure of the
preceding norm, not by comparing two unrelated upper bounds.

No-split, W-only reset, Z-only reset and both-reset controls are admitted
in the same source growth cone. With W and Z subsequently evolving, the
uniform PC-1 argument still gives `x^+>=(61/60)x`. Since
`3(61/60)^67>9` and positive charge-9 resources imply `x<9`, none can
continue positively through all 67 further proposals. This is a uniform
obstruction proof, **not 67 executed steps** and not a fitted failure time.

Negative checks reject an inactive prebeat guard, projection, whole-carrier
reset and the PSD alternative as PC-3 policy substitutions, and a reset
outside the transfer domain. Captured source/reset inputs remain unchanged.
No alternate policy is attempted after a target failure.

Conditional pending `ATC-PC-CHAIN-02` records this complete bounded result
after `ATC-PC-CHAIN-01` and `ATC-PC-CARRIER-03`. It contributes evidence for
DB-02/03/04/06/07/08/13/14/15/16/19/26 without silently discharging any
ledger debt or admitting a graph node. **PC-3 has independent scientific
PASS**, recorded below. PC-4 owns combined domain/request/environment scope and
executable reference/representation conformance. There is no repeated-event,
no-Zeno, native K0, native transaction/replay, all-family or aggregate ATC-2
claim. Native implementation is downstream Phase 9 work, not a new research
acceptance condition.

### 8.4 Independent PC-3 review: PASS, no corrective rerun

The [retained independent review](../evidence/atc-ci-pc/PC3-IndependentReview.md)
reproduced the mathematical payload and checked the original canonical record
digest `f5269098cdc8ac88c21dd2eb5f1d45b76140316b816d4f68db44a635aff681f6`.
It passes source causality, all three transferred state channels, signed
carrier invariance, both-role return/asymptotics, off-image evolution and
counterfactual controls. Its extra finite signed-carrier/high-mode pressure
is retained as reviewer-reported evidence, not claimed as a new local run.

The older raw-matrix dependency encountered by the reviewer is not the
currently bound typed `Carrier` successor. The supplied review resolved that
reconstruction mismatch using the pinned dependencies; it is not a new
scientific defect. No corrective numerical rerun is required.

The current certificate incorporates review status and refreshed documentary
bindings. Its scientific payload is unchanged, checked against canonical
digest `3809b7fb77887e8598c03bf040df9ea2e561c3f2cfb4e01fac559d5158f73688`
over profile/contract identities, evidence and the CI/OS exclusion flag.
The original reviewed record identity remains explicit rather than being
silently replaced by a new reviewer claim. Formal scoped adjudication remains
separate; PC-3's PASS authorizes no native or aggregate closure.

## 9. PC-4 — combined paired-domain and research reference

The user authorizes PC-4 after PC-3 review. This is one combined extension,
not a fresh obstruction search. The
[reference](../research/atc_pc_reference.py),
[checker](../scripts/check_atc_pc_reference.py), and
[record](../evidence/atc-ci-pc/ATCPC4ReferenceCertificate.json)
keep the sole lossless relational law and exact decorated 2+2 topology fixed.
Their contract declares the domains, numerical recipe and finite schedule
before outcome evaluation. **Status: independent scientific PASS for bounded
paired-domain/reference/representation closure; ready for scoped adjudication,
with DB-24/source admission still open.**

### 9.1 One assumption inventory

| Assumption | PC-4 treatment and boundary |
| --- | --- |
| Realization and event operand | Full fixed-H read from old committed Z; one C/W/Z update; fresh poststate PC read selects the event. No CI/OS pass. |
| Exact source domain | Charge 9; exact paired C/W; decorated signed symmetric carrier of norm at most 1/3072. Ordinary source bounds use x>=29/10, obstruction x>=3. |
| Current event domain | 3<=x<=7/2, 0<=y<=1/50, M<=u<v<=1, positive sector currents, resolved source-only dyadic share in [31/64,33/64]. An unresolved or outside share rejects; no target search. |
| Independent reset | Own C/W/Z, 3<=x<=7/2, abs(y)<=1/50, M<=u,v<=1; no ordering or allocator vote. |
| Transfer | Same current-selected share conserves each role's charge; old W survives, bridge W=1; the exact signed relational lift acts on each role's own Z. |
| Target | Initial X<=3/2; first beat enters X<2/3; thereafter resources exceed 5/6, W in [M,1], and Z remains in the full decorated signed carrier ball. |
| Parameters/potential | Fixed profile selected in the positive box below; common C1 potential slope envelope for the theorem, quadratic subclass for execution. No profile switching between beats. |
| Requests | Any sequence h in [3/25,1/8] at fixed physical tau_A=tau_PC=1/(8 log 2); the writer coefficient varies with h. |
| Environment | Paired component only. Active external-edge history is outside the selected PC-2 map; no coupled-environment admission is inferred from A_OS. Unaffected-support negative control remains. |
| Representation | Finite publication-only rounding comparison, separate from the exact-charge theorem and from production arithmetic. |

The source event region is a **sufficient admitted domain**, not a theorem
that every positive state forms a resolved event. It has the reviewed PC-3
strict witness. Exact rational constructors and certified equivariant
operations preserve charge/pairing witnesses; overlapping intervals do not
invent equality or admit a rounded source as exact charge nine.

The positive parameter box is inherited from the earlier channel work,
then **reproved for PC**:

$$
\alpha,\beta\in[1/4096,1/2048],\quad
\gamma\in[1/2048,1/1024],\quad
\chi\in[1/32,1/16],\quad
\kappa_H,\kappa_{Ah}\in[1/2,1].
$$

The common potential theorem uses `|p'(c)-19/4|<=K=1/2048` on `[0,9]`.
The executable quadratic subclass is

$$
p(c)=ac+\tfrac12\nu c^2,\qquad
|a-19/4|\le1/4096,\quad
\nu\in[1/131072,1/65536].
$$

Indeed `1/4096+9/65536<K`. Nonzero alpha/beta/gamma/chi and both geometry
couplings are retained throughout the box; this is not a zero-channel lift.

### 9.2 Simultaneous uniform bounds with evolving W and signed Z

Put `M=24/25`, `R=1/3072`, now `rho=R` because `kappa_H<=1`, and
`r_max=1/783`. Thus `H>= (3071/3072)I` for every admitted signed carrier.
The uniform denominator bound is `d_min=1-(1/16)/49`. The paired-source
baseline bound is `B_s=11/2+90rho`, and the source error is
`E_s=90rho+r_max B_s`. The same exact source-support algebra gives

$$
x^+\ge(1+g)x,\qquad
g=\tfrac52h_{\min}
\left[\tfrac{19}{250}-6K-\tfrac23E_s\right]
=\frac{14682197}{1002240000}>\frac1{80}.
$$

Since `3(81/80)^89>9`, a positive unsplit continuation cannot contain all
89 further proposals. This holds with both W and Z evolving, including
after a one-time W-only, Z-only or both reset. It replaces PC-3's sharper
fixed-point 67-proposal bound only for the enlarged box, not retroactively.
The source held-S norm bound is below `0.000199600<R`.

On the target let

$$
B_t=4+\tfrac52K+\tfrac{125}{8}\rho,\qquad
s=\left(\frac{r_{\max}B_t}{1-\rho}\right)^2,
$$

$$
e=h_{\max}\tfrac52\left[\tfrac52K+\tfrac{125}{8}\rho+r_{\max}B_t\right].
$$

The bare spectral multiplier is positive and its worst request is h_min;
its spectral maximum remains at the two endpoints of
`[M*7/16,73/16]`. With `q=q_0(h_min)+e`,

$$
q=\frac{433407199}{481075200}<0.900914<0.91<1.
$$

For variable-request entry, the bare coordinate envelopes from §8.2 become

$$
L=(1-3h_{\min}a_{\min})t+(1-h_{\min}a_{\min})|y|
  +\tfrac14h_{\max}|\epsilon|,
$$

$$
P=[2-6h_{\min}(a_{\min}-1/25)]t
  +\tfrac12h_{\max}|y|+(1-h_{\min})|\epsilon|.
$$

The same t/y/epsilon bounds give `4L^2+2P^2<(5/8)^2`, whence

$$
X_{\rm first}<5/8+(3/2)e
=\frac{8086615}{12828672}<0.630355<2/3.
$$

The enlarged target bound is `||S||<=sX^2`, with
`s(3/2)^2<0.000058943<R`. Source/target read and post-C writer exponent
budgets remain below `1-M`. Therefore W remains in `[M,1]`. For every
allowed request the carrier writer is genuinely

$$
Z^+=d(h)Z+[1-d(h)]S,\qquad d(h)=2^{-8h},
\qquad 1/2\le d(h)<25/37<1,
$$

so the signed carrier ball remains invariant by convexity. The upper decay
bound follows from `log(2)>1/2` and `exp(t)>=1+t`; no floating estimate of
the transcendental writer coefficient is used to prove invariance.

On the return ball, `X_n<=q^nX_0`. With `b=25/37<q^2`,

$$
z_n\le b^nz_0+sX_0^2\frac{q^{2n}-b^n}{q^2-b}\longrightarrow0.
$$

This proves the same C/J/Z/H limits as PC-3 for any admitted request
sequence. Since the fixed profile's log-writer contracts by at most b and
its drive tends to `exp(-3alpha/2)`, W tends to that value as well. These
are whole-domain exact-real theorems, not conclusions drawn from corner
samples or finite numerical trajectories.

### 9.3 Full-graph reference and bounded lifecycle conformance

The executor independently assembles the full fixed-H PC read with explicit
profile parameters. It performs one continuity update, recomputes the post-C
descriptor, writes W using the **same selected J**, writes Z using the
**held selected S**, and performs a fresh read from final C/W/Z. Variable h
uses the exponential/log writer, not the PC-3 half-step shortcut.

An independent 110-digit Decimal oracle uses edge-local accumulation, its
own WLS and dense solve, and an explicit canonical carrier-transfer formula.
It calls neither the reference's scientific stages nor the CI/OS solver.
The retained 1,645 scalar comparisons check the original source beat, both
transported roles at both request endpoints, and two predetermined parameter
box corners on a signed target carrier. Every oracle value is enclosed by
the outward reference intervals. These corners are diagnostic examples;
the rational inequalities above certify the box. Stale descriptors,
poststate-J writer substitution and newly recomputed S substitution are
numerically separated from the correct stages.

The exact-domain research owner executes ordinary source onset → source-only
event → ordinary target step → reset, with one publication assignment per
successful operation. Each event role is independently admitted, including
its carrier; reset restores the actual transported reset C/W/Z, and ordinary
steps do not rewrite it. Replay reconstructs the physical sequence from its
pinned source, not merely a chain of matching hashes. Missing lineage,
changed requests, wrong profile, forged reset Z and wrong edge lineage are
rejected even when the supplied final digest is recomputed. Actual reset-only
domain rejection and injected reset-readmission/late-publication failures
leave the complete old publication untouched. Request boundaries, unresolved
allocation, exact tie parity and out-of-scope descendant events are explicit.
This is bounded research lifecycle conformance, not a production wire API,
native K0 scheduler or repeated-event theorem.

### 9.4 Finite representation and environmental ceilings

The predeclared four-step schedule is `(1/8,3/25,31/250,121/1000)` for
each actual transported role. Exact-real enclosures propagate separately
from a diagnostic that rounds **C, W and every Z entry** to binary64 at
publication. Its internal stages are enclosed, not rounded at every
arithmetic operation. Physical exact tau and the separately pinned binary64
tau are not conflated. At the lower request endpoint the diagnostic uses
the next float above `0.12`, because the usual binary64 value lies below
the exact closed interval. The profile parameters in this run are exact
dyadics; requests, tau and state projections supply the represented errors.

The record retains per-step C/W/Z error enclosures, binary64 state images,
exact/represented stage identities and measured charge discrepancy against
the predeclared `1e-10` finite error budget. Errors are propagated from the
prior rounded state, not reset to an exact trajectory at each step. A rounded
state never acquires an exact-charge `DomainState` witness. Observed carrier,
resource and read admission are checked separately; no infinite binary64
invariant-domain or exact represented conservation theorem is claimed.

All eight retained steps meet the finite budget. Maximum enclosed errors
are below `2.72e-16` for C, `5.29e-17` for W, and `1.24e-21` for Z.
The maximum observed absolute charge discrepancy is exactly
`1/2251799813685248` (about `4.44e-16`). It is retained as a numerical-policy
finding, not corrected by an unauthorized balancing adjustment.

The selected PC-2 transport accepts exactly the four-edge decorated source.
Adding active external edges introduces additional old-edge/cross-history
components; neither that map nor A_OS environmental success authorizes an
array extension. Accordingly **active coupled-environment PC transport is
outside this bounded PC-4 result**, not silently marked solved. The negative
operation-support statement does generalize: a disjoint unsplit source
component with block-diagonal carrier has its own incidence/descriptor/H
block and retains its obstruction after fission elsewhere. It is an algebraic
locality control, not a claimed new environmental campaign.

`ATC-PC-DOMAIN-04` routes these conditional paired-domain and research
reference results to the existing debts; its numerical/transaction scope is
explicit. Independent review is PASS; formal scoped admission remains pending. No new native
implementation gate is added to research acceptance, and no coupled-environment,
other-family, repeated-event, non-Zeno or aggregate ATC-2 result is inferred.

### 9.5 Independent PC-4 review: PASS, ready for scoped adjudication

The [retained independent review](../evidence/atc-ci-pc/PC4-IndependentReview.md)
reproduces the contract, profile identity and complete evidence payload,
including all 1,645 scalar comparisons, the 15 negative cases and eight
represented continuation steps. It independently verifies the original
record digest `0a1369d4bdfa1edbf44f757c0ef0fcc25b5af5398c14d119075170407975cc91`.
**No corrective rerun is required.** The earlier pre-relocation proof-script
copies do not supersede the accepted relocated bindings already reconciled
against commit `5e1a63a`.

The review additionally reports 18 deterministic mixed parameter corners
at both request endpoints: 36 admitted target cases and 36 source-onset
cases with resolved shares in `33597<=k<=33623`. These are retained as
**reviewer-reported diagnostics**, not new local runs, a parameter sweep
proving the theorem, or a whole-box autonomous-formation result.

Two scope conditions remain explicit in the certificate's review metadata
and must survive subsequent adjudication:

- `whole_box_theorem=true` means uniform obstruction and carrier invariance,
  and transfer-entry/return/asymptotic bounds **conditional on an admitted
  event state with a resolved source-only share**. It does not mean that
  every source state/profile autonomously forms a resolved event.
- The C¹ potential class belongs to the analytic theorem; the quadratic
  subclass belongs to the executable reference/oracle. Finite reference
  checks do not execute every C¹ law.

The reviewed contract/profile/evidence remain unchanged, checked against
canonical mathematical-payload digest
`d78a0c362250b9b371e080105bf18ba26c13724a1aeb0c9fc85aae224b22362f`.
The updated record preserves the original reviewed identity separately from
new review-status/documentary bindings. It does not claim a new independent
review of those metadata changes.

This completes the declared paired A_PC scientific/reference scope enough
for **formal scoped claim/debt adjudication**, not source admission itself.
DB-10/21/23/28 now have reviewed bounded evidence; DB-24 remains explicitly
open and `local_debt_discharge=false` is unchanged. Active coupled-environment
transport is a future extension, **not an unmet PC-4 criterion**. Native,
repeated-event/non-Zeno, other-family and aggregate ATC-2 claims remain open.
Do not add a PC-5 discovery stage before adjudication. The parallel A-side
scientific continuation is CI-2 and CI-3, not another A_PC anchor refinement.

## Reproduction

From repository root, use `.venv/bin/python` with
`implementation/investigations/grc9v4-constitutive-design/scripts/audit_atc_ci_pc_boundary.py`.
Default prints a fresh bounded stage audit; `--check` checks retained identities
without rerunning numerical owners. Neither writes files or publishes results.

For the full-feedback research certificate, run
`implementation/investigations/grc9v4-constitutive-design/scripts/check_atc_ci_pc_anchor.py`
with the same repository Python. It prints a fresh fixed-anchor record and
performs no filesystem writes. Its source-bound reference inputs and rational
inequalities are separate from the boundary checker's native zero-potential
stage fixtures.

For PC-2 and the new domain-negative pressure, run
`implementation/investigations/grc9v4-constitutive-design/scripts/check_atc_pc_carrier_event.py`
with the same Python. It prints the retained projection/control certificate
without writing files or simulating target continuation.

For revised PC-2, run
`implementation/investigations/grc9v4-constitutive-design/scripts/check_atc_pc_relational_lift.py`.
It prints the proposed lossless-lift certificate with exact coordinate,
inverse, domain and PSD/no-go pressure, without executing PC-3.

For PC-3, run
`implementation/investigations/grc9v4-constitutive-design/scripts/check_atc_pc_causal_chain.py`
with the same Python. It prints the source/both-role fixed causal certificate
and exact uniform continuation bounds. It does not write files, run CI/OS
solvers, search parameters or execute a long trajectory.

For PC-4, run
`implementation/investigations/grc9v4-constitutive-design/scripts/check_atc_pc_reference.py`
with the same Python. It prints the combined domain/reference certificate,
independent stage comparisons, bounded lifecycle pressure and four-step-per-role
representation comparison. No generated output directory is required.

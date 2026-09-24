# A_CI+PC — coupled root and persistent-history compatibility

2026-09-23. **CIP-0 prepared for review; CIP-1 and CIP-2 not executed.**
Research only. No new accepted claim, local/global debt discharge, native
ATC, proposal/paper/spec authority or aggregate ATC-2 closure is inferred.

The user's [program direction](../evidence/atc-cip/CIP-CoupledProgram-Direction.md)
and [sharper domain direction](../evidence/atc-cip/CIP-CompositeDomain-Direction.md)
motivate this successor. They are proposals, not accepted certificates.
Accepted CI/PC notes, source files, evidence and graph identities stay unchanged.
This is a compatibility problem between an instantaneous joint root and a
persistent carrier, not a third discovery of the topology operation.

## 1. Three stages and their stopping points

| Stage | Required new result | Current disposition |
| --- | --- | --- |
| CIP-0 | Actual step/source identity; nonempty composite domain; Z-uniform unique regular root; decoration and carrier-ball preservation; fresh event operand | Prepared below, pending independent review |
| CIP-1 | One preregistered complete onset → obstruction → source selection → split → both-role readmission → actual combined return chain, with lawful controls | Not executed |
| CIP-2 | Consolidated domain, executable research reference, independent oracle, covariance, lifecycle/replay/rollback and finite representation; then separate scoped adjudication | Not executed |

Stop on a failed arrow. Do not adjust the topology law or retune the witness
after seeing target success. A changed sufficient domain is a named successor,
not silent promotion of failed evidence. Production integration remains later:
reviewed research → topology proposal → paper → specification → Phase 9.

## 2. CIP-0A: exact ordinary step and gains

The [specification](../../../../specs/grc-v4-spec.md#coupled-implicit-plus-persistent-carrier-cipc)
and `src/pygrc/models/grc_v4_ci.py` agree. The authoritative state is C/W/Z;
old Z is a fixed root input, not another unknown:

$$
(C_k,W_k,Z_k)\longrightarrow(J_k^*,H_k^*,S_k^*)
\longrightarrow C_{k+1}\longrightarrow W_{k+1}
\longrightarrow Z_{k+1}\longrightarrow R_{\rm CIP}(C_{k+1},W_{k+1},Z_{k+1}).
$$

$$
K_{\rm eff}=K_{4,\rm base}+Z_k+\rho_{\rm inst}S_k^*,\qquad
Z_{k+1}=a_kZ_k+(1-a_k)S_k^*,\quad a_k=e^{-h_k/\tau_{PC}}.
$$

The writer uses the **literal selected root's registered S**, not a second
post-continuity source. W writing preserves old Z until the single carrier
write. New Z enters the fresh restart root only; it cannot change the current
that drove the preceding continuity update. Current/reset admission uses their
separate C/W/Z. A K0 event must consume the fresh committed-state full joint
root and its certificate, not just the consumed current.

Gain accounting: chi occurs once in Read-Back; zeta multiplies that flux in
the current equation and separately occurs once outside its quadratic star
in the registered structural source. Rho_inst multiplies the instantaneous
source in geometry, not the held-source writer; primary rho_inst is exactly
one. Kappa_H multiplies the combined structural input once. The bound below
fixes zeta_A=1 and rho_inst=1, as in the accepted paired research. The native
stage check deliberately uses non-unit zeta to discriminate duplicate gains;
its shipped zero-site-derivative fixture is **not** this nonlinear research box.

The checker compares J/H/S with the existing independent literal native
fixed-point oracle, checks the writer argument tuple, full fresh/restart root
equality and canonical root digest, distinct reset, zero-duration identity,
and final-reconstruction rejection with captured-state preservation. It does
not claim live-owner topology transactions from this provisional-step test.

## 3. CIP-0B: derive the domain, do not intersect certificates

Use exactly CI-2's paired source/target graphs, WLS host positions, reference
weights, reference identity Hodge, potential and C/W hypotheses in
[CI-2 §§1–2](ATCCIDomainsAndReference.md). Source: positive charge nine,
x>=29/10; target: positive charge nine, X=norm(C-(3/2)1)<=3/2.
W is paired and lies in [24/25,1]. The common C1 potential satisfies
abs(p'-19/4)<=1/2048 on [0,9]; the executable subclass is quadratic.

Keep CI-2's positive scalar box except for kappa_H:

$$
\alpha,\beta\in[1/4096,1/2048],\quad
\gamma\in[1/2048,1/1024],\quad\chi\in[1/32,1/16],
$$
$$
\kappa_{Ah}\in[1/2,1],\quad\kappa_H\in[1/2,3/5],\quad
|a-19/4|\le1/4096,\quad\nu\in[1/131072,1/65536].
$$

Choose one fixed profile. Requests may vary in [3/25,1/8];
tau_A=tau_PC=1/(8 log 2). Z is signed symmetric, star-supported and exactly
decorated, with no PSD requirement. Define the closed balls by

$$
\|Z\|_F\le R_Z=1/5000,\qquad \|H-I\|_F\le\rho=1/4096.
$$

At fixed C/W, let f(H) be the accepted Candidate-A causal-flat read. Then

$$
T_Z(H)=I+\kappa_H[Z+\operatorname{Star}(f(H))].
$$

The imported CI bounds concern **every H in this ball**, before a root is
selected: baseline, read/writer budget, current inverse, F bounding norm(f),
and L_f bounding its H-Lipschitz constant. They do not require Z=0 or H to
already be a CI root. Those hypotheses are the reason reuse is valid.

For every admitted fixed Z,

$$
\|T_Z(H)-I\|_F\le\kappa_{H,max}(R_Z+F^2)<\rho,\qquad
\operatorname{Lip}_H(T_Z)\le L=2\kappa_{H,max}FL_f<1.
$$

The [exact rational checker](../research/atc_cip_domains.py) establishes:

| Domain | Bound on norm(S) | Total H displacement | L | Bound on Z-to-H root response |
| --- | --- | --- | --- | --- |
| Source | <0.000199039 | <0.000239424 | <0.003608 | <0.602173 |
| Target entry | <0.000058896 | <0.000155338 | <0.000585 | <0.600352 |

The smallest geometry slack is greater than 0.0000047175; source carrier
slack is greater than 0.0000009615. Exact fractions, not these rounded display
values, decide the inequalities. The closed H ball is complete, convex and
uniformly SPD with eigenvalues at least 4095/4096. The star map and Z preserve
its linear support/symmetry subspace. Banach therefore gives a unique root
inside it, uniformly over the Z ball. The current inverse bound and reduced
H inverse bound 1/(1-L) give joint-root regularity via the Schur complement.
Roots outside the admitted ball are not classified.

For the same C/W/profile and two admitted carriers,

$$
\|H^*(Z_1)-H^*(Z_2)\|_F
\le\frac{\kappa_H}{1-L}\|Z_1-Z_2\|_F.
$$

This does not assert matched-trajectory contraction of the whole nonlinear
writer/state system. Scaling kappa_H down continuously to zero preserves
the self-map and contraction, identifying the reference-connected branch;
the mathematical homotopy does not widen the positive runtime profile box.

The old PC radius 1/3072 fails this *sufficient source budget* even with
kappa_H=1/2. The old CI gain endpoint one likewise fails with R_Z=1/5000.
These failures reject naive certificate composition, **not** prove that no
coupled root exists in a larger or differently estimated domain. A carrier
radius below the source bound fails the convex-writer certificate as well.

## 4. CIP-0C: writer and exact-sector compatibility

Both root domains have norm(S)<R_Z. For a positive request/tau, 0<a_k<1,
so the actual selected-source writer obeys

$$
\|Z^+\|_F\le a_k\|Z\|_F+(1-a_k)\|S^*\|_F\le R_Z.
$$

This is a conditional carrier invariant while the C/W hypotheses hold;
resource positivity/onset and indefinite target continuation belong to CIP-1.
It is not a claim that every source state has a successful next ordinary beat.

The decorated within-sector swaps preserve C/W/Z, the incidence/WLS equations,
and the H domain. Equivariance plus uniqueness fixes the selected J/H under
these symmetries; its S has the same decoration. Continuity, the edgewise W
writer and the linear Z writer preserve these exact symmetries on successful
steps. Approximate matrix equality or interval overlap does not certify them.

Use the accepted PC-2 sign-faithful relational lift unchanged. On its exact
2+2 decorated source domain it preserves c_target=c_source and is a Frobenius
isometry, so transported Z fits the new target carrier ball. Its signed
five-dimensional image lies inside the seven-dimensional decorated target
ball. The target root theorem above then applies **provided the independent
C/W transfer premises also hold**. CIP-1 must execute both-role transfer and
combined readmission; this algebra is not their execution evidence.

## 5. CIP-1 preregistration and controls

Start with the shared interior source, in leaf/leaf/leaf/leaf/parent order:
C=(61/50,61/50,6/5,6/5,104/25), W=(97/100,97/100,99/100,99/100),
Z=I4/16384 (norm=1/8192<R_Z), h=1/8, kappa_H=1/2. Use the accepted shared
anchor's remaining positive parameters, independently declared reset role,
and existing source-only sector/dyadic selection rule. Freeze the exact full
input before executing CIP-1. The result gets its own k_CIP; neither 33615
nor 33616 is a target. Require its certified share in [31/64,33/64].

Reuse only the conditional graph/transfer lemmas: resource conservation,
old W lineage/bridge seed one, child funding 1303/1600, relational carrier
isometry. Prove the geometry-uniform source obstruction and return estimates
still apply to this actual coupled root. Test the proposed simplification
X_next<=q_CI X with q_CI=577621057/641433600 before introducing an additive
carrier error. Establish the selected-source bound S<=s X² and actual
variable-request recurrence z_next<=a_k z+(1-a_k)sX²; do not replace a_k by
its upper bound in both terms without a valid inequality. Derive the
asymptotic C/J/W/Z/H limits, not just a finite numerical approach.

Controls are no split, W-reset only, Z-reset only and both reset, with exact
intervention timing stated. **A one-time Z reset is not a CI trajectory:**
its next coupled writer normally creates nonzero Z. A zero-Z instantaneous
root equals the CI root; disabling or repeatedly clamping the carrier is a
different declared control. Do not conflate these in the causal conclusion.

## 6. Claims/debts and evidence route

The checker uses typed reconstruction of accepted conditional
ATC-CI-DOMAIN-02, ATC-CI-REFERENCE-03, ATC-PC-CARRIER-03 and ATC-PC-DOMAIN-04,
retaining authority boundaries, source references, edges and trace digests.
The accepted carrier claim is CARRIER-03, not the superseded projection
control CARRIER-02. Neither CI nor PC local debt closure transfers to CIP.

Proposed `ATC-CIP-ROOT-00` concerns only this root/staging result; its pending
debt links are DB-03/05/06/07/15/16/24. No local discharge occurs at CIP-0.
CIP-1 must supply the actual causal/transfer/return evidence; CIP-2 adds
reference, numerical/lifecycle and scope routing. Separate review and scoped
adjudication must then reconcile **all 28** realization-local debts and admit
the exact successor inventory. Global origin debts remain open.

Reproduce from repository root with `.venv/bin/python` and
`PYTHONDONTWRITEBYTECODE=1`:

```sh
.venv/bin/python implementation/investigations/grc9v4-constitutive-design/scripts/check_atc_cip_opening.py
.venv/bin/python implementation/investigations/grc9v4-constitutive-design/scripts/check_atc_cip_opening.py --check
```

The first emits a fresh bounded run to stdout; the second checks retained
identities only. Neither creates accepted graph authority. See the
[evidence index](../evidence/atc-cip/README.md).

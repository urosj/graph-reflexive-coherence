# CIP-1 — combined source-selected fission and return

2026-09-23. **Prepared for independent review; no scientific/source admission
or aggregate ATC-2 closure.** The user authorizes CIP-1 after the
[CIP-0 preparation](ATCCIPCoupledProgram.md). This proceeds on its locally
checked hypotheses; it does not invent an independent CIP-0 review.
No accepted CI/PC record, CIP-0 record, native source or specification changes.

## 1. Fixed experiment, before evaluating the target

The [preregistration](../evidence/atc-cip/CIP1-Preregistration.json) is pinned
in the checker with SHA-256
`c983589eead8283051674bcb63255ee23b573491a23c64bc4290e20b3784cec2`.
It fixes the complete current/reset inputs, profile, requests and sole carrier
law before any causal-chain evaluation. No target tuning, operation search,
PSD fallback or desired allocator value is permitted.

Use the accepted paired five-node source and six-node double-star target,
with the same full incidence, WLS positions, unit reference weights and ridge
one. Source order is four leaves followed by parent. The current role is

$$
C=(61/50,61/50,6/5,6/5,104/25),\quad
W=(97/100,97/100,99/100,99/100),\quad Z=I_4/16384.
$$

The independently declared reset role is

$$
C^r=(9/8,9/8,231/200,231/200,111/25),\quad
W^r=(49/50,49/50,97/100,97/100),\quad Z^r=I_4/24576.
$$

Both have exact charge nine and exact decorated pairing. Reset is neither
the current state nor a vote in event selection. Fix alpha=beta=3/8192,
gamma=3/4096, chi=3/64, kappa_H=1/2, kappa_Ah=3/4, a=19/4,
nu=1/65536, zeta=rho_inst=1 and tau_A=tau_PC=1/(8 log 2).
The source takes one request h=1/8. Each actual target role takes h=1/8
then h=3/25, exercising a genuinely non-half second writer coefficient.

## 2. Coupled execution, not a CI/PC splice

The [research module](../research/atc_cip_chain.py) evaluates the full graph
Candidate-A fixed-H equations, then solves

$$
J=b(H)/(1-\chi q(H)),\qquad
H=I+\kappa_H[Z+\operatorname{Star}(H^{-1}\chi q(H)J)].
$$

Z is fixed throughout each joint solve. The a-priori CIP-0 contraction
constant encloses the root using residual/(1-L), not observed convergence.
Both joint residuals must enclose zero. State/profile/carrier/certificate
identities and the entire selected-root digest are retained. No standalone
CI solve, PC fixed-carrier read or OS corrector substitutes for this root.

An ordinary call executes its own selected root, continuity, post-C W writer,
one old-Z/held-source carrier write, and full fresh restart root. Only then
does it return a certified successor. It accepts no caller-supplied output,
selected root or proof receipt. Exact C/W predicates are kept separate from
outward numerical boxes using the hardened predicate machinery; the new
operation supplies CIP-specific execution/theorem bindings. Those containers
and the conservative transfer are shared algebra, not CI dynamics.

The carrier constructor enforces exact decorated support and symmetry and
the new narrower radius. Symmetry intersections use the proved equivariance,
never overlapping intervals as evidence of physical equality. This is a
bounded research proof interface, not a hostile-code sandbox. CIP-2 retains
the wider closed-boundary and represented-number conformance obligations.

The fresh post-onset root supplies positive inward sector currents and its
own uniquely resolved round-even k/65536 in [31/64,33/64]. It must equal
the complete ordinary restart root, while differing from the consumed
pre-continuity current. The preregistration does not demand 33615 or 33616.

## 3. Reused lemmas and new coupled induction

The CI-2 fixed-H estimates use only total norm(H-I)<=1/4096 and the declared
C/W/profile hypotheses. CIP-0 guarantees precisely that total ball even
with old Z present. Thus the **same geometry-uniform estimates**, not the
CI realization's dynamics, apply to each combined root.

### Source obstruction

While the unsplit source remains positive, the shared estimate gives

$$
x^+\ge(65/64)x,\qquad 3(65/64)^{71}>9.
$$

The W writer preserves [24/25,1]. CIP-0's held-source bound preserves the
decorated Z ball under the actual writer. Root existence is uniform on this
domain. Hence an unsplit positive continuation starting in x>=3 cannot
survive 71 further proposals, because positive charge-nine resources require
x<9. This is a resource obstruction, not a solver nonconvergence claim.
It does not require executing 71 numerical steps.

### Transfer and both-role readmission

The current alone selects k. Independently for current and reset, preserve
the four leaf resources and split that role's parent using k/65536. Preserve
old W by exact edge lineage and seed only the bridge at W=1. The common
transfer interval gives child funding at least 1303/1600 and target X<3/2.

Use the accepted sign-faithful PC relational map without modification:
c_target=c_source, exact inverse on its image and Frobenius isometry. Each
role's transported Z therefore remains in the CIP ball. Its signed carrier
need not be PSD; the live event witness explicitly checks a negative 2×2
principal minor. SPD belongs to the *combined H*, secured by CIP-0.

Reconstruct and admit each role's full combined target root before returning
the event result. The event takes zero time and performs no ordinary W/Z
write. The five-dimensional image is not a target invariant: the subsequent
ordinary writer may enter the seven-dimensional decorated target ball.

### Indefinite target continuation

Let X=norm(C-(3/2)1), z=norm(Z), and

$$
q=\frac{577621057}{641433600}<1,\quad b=25/37,\quad
s=\left[\frac{(1/783)(4+(5/2)(1/2048)+(125/8)(1/4096))}{1-1/4096}\right]^2.
$$

The shared first-entry lemma gives X_1<2/3 (its retained sharper bound is
10771945/17104896). The ordinary target estimates give

$$
X_{n+1}\le qX_n,\qquad
\|S_n\|_F\le sX_n^2,\qquad
z_{n+1}\le a_nz_n+(1-a_n)sX_n^2,
\quad 0<a_n\le b<q^2<1.
$$

These estimates depend on total H, not on whether its deviation arose from
persistent or instantaneous structure. In particular, geometry acts on
resource differences, which vanish at constant C; there is **no independent
additive Z forcing** in the resource estimate. No new small-gain ansatz is
needed. The Z ball remains invariant because s(3/2)^2<R_Z. Together with
the W invariant and resource floor 5/6 after entry, this is a closed induction
for all later exact-real target steps and requests in [3/25,1/8].

For variable requests, a safe convolution uses 1-a_n<=1 separately:

$$
z_n\le b^n z_0+sX_0^2\frac{q^{2n}-b^n}{q^2-b}\longrightarrow0.
$$

We do not replace a_n by b in both terms of the exact recurrence. Since
S_n→0, H_n-I=kappa_H(Z_n+S_n)→0, and the uniform current bound gives J_n→0.
The post-C conductance exponent tends to 3 alpha/2. The log-W writer has
coefficient at most b, hence W_n→exp(-3 alpha/2). Therefore

$$
C_n\to(3/2)\mathbf1,\quad J_n\to0,\quad Z_n\to0,\quad
H_n\to I,\quad W_n\to e^{-3\alpha/2}\mathbf1.
$$

The conditional bounds cover the CIP-0 box; **formation and allocator
resolution over that entire box are not claimed**. The executed source is
the single frozen profile. The two target beats are numerical witnesses to
the bounded dynamics, not empirical substitutes for this induction.

## 4. Controls and negative pressure

At the committed post-onset source, apply once: no intervention, W reset to
one, Z reset to zero, or both. Keep the same CI+PC profile and writer active.
All four remain in the invariant obstruction cone. Execute one further
ordinary beat for each, and retain the uniform 71-proposal impossibility
bound. The zero-Z controls must regenerate nonzero Z: resetting history once
does not turn the continuation into CI or repeatedly clamp it.

The checker also rejects the prebeat inactive guard, alternate carrier policy,
an interior PC-admitted carrier outside the smaller CIP radius, a
standalone-CI-only gain and an actual
reset role outside the transfer domain. Inject final ordinary reconstruction
and reset-only target-root rejection; no partial result is returned and
captured immutable input roles remain unchanged. This is preparation/return
atomicity in a pure research operation, **not public native owner lifecycle
coverage**. The latter reference/replay/covariance/representation work belongs
to CIP-2 and then downstream Phase 9 under its separate authority.

## 5. Evidence and pending claim/debt route

The [certificate](../evidence/atc-cip/ATCCIP1Certificate.json) retains the
exact selector, both-role event roots, signed-carrier receipts, ordinary
selected/restart roots, evolving C/W/Z, controls and negative cases. It pins
the frozen input, CIP-0 record and transitive research sources.

Proposed `ATC-CIP-CHAIN-01` follows proposed ROOT-00 and applicable accepted
CI-DOMAIN-02 / PC-CARRIER-03 lemmas. Pending debt routes are
DB-02/03/04/06/07/08/13/14/15/16/19/26. No local or global discharge is made.
CIP-2's independent reference, lifecycle and finite-representation checks,
independent review and all-28 scoped adjudication/source admission remain.

From repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python implementation/investigations/grc9v4-constitutive-design/scripts/check_atc_cip_chain.py
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python implementation/investigations/grc9v4-constitutive-design/scripts/check_atc_cip_chain.py --check
```

The first emits fresh evidence; the second checks retained identities only.

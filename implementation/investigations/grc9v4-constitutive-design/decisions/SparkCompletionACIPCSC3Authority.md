# SC-3 — A_CI_PC completion applicability adjudication

2026-11-01. The user instructs “accept and commit”. Admit the three bounded
conditional claims below and resolve A_CI_PC research applicability debt.
Research checkpoint `8faa7497` preserves the original equations, full
product proof, compressed runs, optimization preflight and validation.
Validation is author-side; no independent external reviewer or duplicate long
trajectory replay is claimed. SC-1 and the seven earlier accepted families remain
unchanged. The earlier A_OS domain retains its separate review status, and its
below-100 investigation remains paused. [Machine authority](./spark-completion-a-ci-pc/Authority.json).

## SC-ACIPC-EC-DOMAIN

`SC-ACIPC-CL-C-DOMAIN` is accepted as conditional mathematics on the declared source/target graphs, signed carrier ball and conditional resource/conductance box. No global resource invariance or arbitrary-graph theorem is admitted.

Use eta=1/1024, h=tau_A=tau_PC=32, kappa_c=kappa_Ah=1/64,
chi=zeta=kappa_H=1/2, alpha=beta=gamma=1/32768, W_floor=1/2,
and site(C)=(C−2)^3−(C−2). Let B be oriented incidence, O=|B|^T|B|,
L=log W and D the incoming-W weighted fixed-row means. The joint equation is

```
S(f)_ij = O_ij f_i f_j/4
H(f,Z) = I + (Z+S(f))/2
Phi = B diag(W) B^T C/64 − site(C) + B(H−I)B^T C/64
j0 = −diag(W) B^T Phi/1024
G_e(C,W,j) = max(1/2, exp(−(C_u+C_v+||D_u−D_v||²+j_e²)/65536))
q_e = (W_e−G_e(C,W,j0))/(W_e+G_e(C,W,j0))
J_e = j0_e/(1−q_e/4)
F(C,W,Z,f) = H(f,Z)^(-1)(q*J/2),       f=F(C,W,Z,f).

C+ = C − 32 B J
L+ = exp(−1) L + (1−exp(−1)) log G(C+,W,J)
Z+ = exp(−1) Z + (1−exp(−1)) S(f).
```

The same selected f defines the instantaneous geometry and held carrier source.
Incoming Z is held fixed during the root; incoming W supplies both current
stages and the final-C W writer. Both newly written histories are consumed
at the next read. Independent equations distinguish the composite from PC
with the immediate source dropped and CI with the incoming carrier dropped.
This matches the native composite structural-input convention in
`grc_v4_ci._effective_source` without altering native completion support.

On each concrete graph take C in [0,4], W in [.99,1.01], symmetric
star-supported ||Z||_F≤R=1/64 and ||f||_infinity≤r=1/32. Write
ell=||B^T B||_infinity, m=number of edges and s=max_i sum_j O_ij/8.
Cauchy–Schwarz bounds the held-carrier infinity norm using ceil(sqrt(m)).
The exact rational bounds are

```
z = ceil(sqrt(m)) R/2,   h0=z+s r² < 1,   u=1/(1−h0)
j = wh (12+4 ell wh/64+4 ell h0/64)/1024
g = 1−(8+192+j²)/65536 > 1/2
a = max(wh−g,1−wl)/(wl+g),   den=1−a/4,   Jmax=j/den
image = u a Jmax/2 < r
jH = 4 wh ell/65536
qj = 4 wh j/(65536 (wl+g)²)
Jj = 1/den+j qj/(4 den²)
FH = u ((a Jj+Jmax qj) jH/2+image)
root_q = 2 s r FH < 1.
```

The geometry variation satisfies ||dH||_infinity≤2sr||df||_infinity.
Both geometry consumers are included: the potential through jH and inverse
lowering through image. These bounds prove one root in the declared flat
ball uniformly over the state domain, without asserting global uniqueness.
The norm bound ||S(f)||_F≤m image²/2<R makes the signed carrier ball invariant
under its convex writer. If C+ stays in [0,4], the conductance drive is at
least 1−(200+Jmax²)/65536>.99 and at most one. The resource box is conditional;
every actual state and the trap verify its required bounds.

O is a Gram matrix, so S(f) is positive semidefinite. Thus H has eigenvalues
at least 1−R/2 even for signed incoming Z, and at most 1+R/2+mr²/4.
The conservative selector factor .99*(127/128) is checked on source and target.
The trap uses its sharper carrier radius for selector separation.

Newton computations at 128,256,…8192 bits only propose a midpoint fhat.
At the actual full input intervals, evaluate residual=||F(fhat)−fhat||_infinity
and enclose the root with error=residual/(1−root_q). The radius check is strict.
The saved `residual` interval encloses the outward upper bound on this norm.
Every returned geometry, source, current and physical update uses the full
root enclosure. There are at most 12 Newton iterations per declared stage.
No midpoint is substituted for a physical state and no fallback increases
trajectory precision.

## SC-ACIPC-EC-FULL-STATE-RETURN

`SC-ACIPC-CL-C-FULL-TRAP` is accepted as conditional mathematics for the full 76-dimensional implicit, exact charge-21 C/W/Z product return, including all conductance and symmetric-star carrier directions and both independent writers.

Borrow only the exact rational center and C/W shape from
`earlier-closure/AOSAnisotropicDomain.json`, authenticating its old operands.
The exact charge chart x=x0+Sx u has U Sx=I30 and sum C=21. Extend it to

```
K = { x=x0+Sx u, ||u||_infinity≤1, ||Z||_F≤rho }, rho=1/2^30
norm(delta x,delta Z) = max(||U delta x||_infinity, ||delta Z||_F/rho).
```

There are 14 independent resource, 16 conductance and 46 symmetric-star
carrier directions. Diagonal carrier basis entries are one; paired
off-diagonal entries are 1/sqrt(2), giving Frobenius-orthonormal coordinates.
The derivative enclosure covers an outer coordinate box containing K.

At fixed f, include the direct C/W/Z partials Jx and Fx. In particular each
carrier direction has dH=dZ/2. Differentiate the immediate source through Ff
and Jf. Compute the implicit derivative by a single multiple-right-hand-side
solve, then propagate continuity, the final-C W writer and the shared source:

```
df = (I−Ff)^(-1) Fx
 dJ = Jx + Jf df
 dS_ij = O_ij (df_i f_j+f_i df_j)/4
 dZ+ = exp(−1) dZ + (1−exp(−1)) dS.
```

The proof freshly checks ||Ff||_infinity<root_q. Neither a CI-only nor a
PC-only Jacobian is reused. For the resulting full return derivative use

```
a = ||U Txx Sx||_infinity
b = rho max_i ||(U TxZ)_i||_2
c = sqrt(30) ||TZx Sx||_F/rho
d = exp(−1)+||TZZ−exp(−1) I46||_F
q = max(a+b,c+d).
```

The 512-bit FLINT/Arb proof gives contraction upper bound 0.995941466143 and strict
unit image margin at least 0.004058533857, after the enclosed center defect. The
first composite product-domain candidate passed before the pilot or either
full trajectory; there was no composite domain search or tolerance change.

Exact support over Sx proves every fixed edge order. Weighted row bounds prove
the complete basin predicates. Both chiral charts give p:{p,private} and
satellite/2:{n2,n8,satellite/2}. Identical ordered incidence, row assignments
and carrier bases permit a shared trajectory; both predicate charts are checked.

At any full-map fixed point, BJ=0 and J=−D B^T Phi with positive diagonal D.
The quadratic identity forces J=0, hence f=S=0. Stationary Z=S then gives
Z=0 and H=I; the W writer forces W=G(C,W,0). In general stationary composite
geometry has Z+S=2S, which is why both source contributions must be kept.
Neither history direction is frozen in the neighborhood proof.

## SC-ACIPC-EC-COMPLETION

`SC-ACIPC-CL-C-COMPLETION` is accepted as conditional mathematics for the declared actual source/event/two-history transfer/approach/window chain. Current, reset and read-only replay remain distinct; reset and replay earn no live gain.

A fresh composite ordinary beat starts from exact SC2 resource prestates,
current W=4097/4096 and diagonal Z=1/65536. The reset prestate uses
W=8191/8192 and diagonal Z=−1/131072, and is independently unadvanced.
A fresh selected root on committed current C/W/Z supplies the event read.
Complete parent qualification, saturation and strict trigger margins are checked.

D11 resource shares are 1/128,63/64,1/128 with zero core and copied exterior.
Every old edge preserves its W, while three new internal edges start at one.
Both entire nonzero source carriers are archived with digests; the whole target
carrier is zeroed under an explicit `carrier_history_loss` disposition.
Conductance preservation and carrier loss are recorded separately.

Allocation alone earns no new child. Fresh interval evolution gives current
entry 375, two-beat window end 377 and one local child; reset
entry 372, window end 374 and zero live gain. Campaign wall times
are 120.43 and 118.82 seconds respectively. Matching earlier witness
times are obtained independently. The positive window has elapsed time 64;
these sufficient witness times are not earliest-completion claims.

The fixed declaration uses 8192-bit trajectories, 512-bit trapping arithmetic,
a 1024-beat horizon and one-hour cap per role. The eight-step preflight checks
exact graph/domain cache hits, reused weighted rows, staged root proposals,
exact-full-state read reuse and batched geometry/implicit solves. Every beat
uses one selected root and separate W/Z updates. No pilot or old-family state
is reused. Runs stop after the positive window; no redundant large campaign
is added to this bounded construction.

All 751 states retain outward 112-bit C/logW/Z inspection intervals,
while full-precision intervals remain recurrence operands. 11,203,812 bytes of
execution evidence compress losslessly to 1,077,016 bytes in XZ. The checker
rebuilds source/transfer and the full trap, checks every saved transition,
recomputes complete basins and entry from all coordinates, verifies root/read
checkpoints, and rejects 27 altered-evidence controls. Transition/root overlaps
are consistency checks; the source-bound outward producer supplies enclosure
provenance. No duplicate long trajectory or independent external review is claimed.

Six equation tests include a separate 110-digit Picard implementation, all
76 physical derivative directions and all 16 flat-root directions for both
geometry consumers. The side-tool adds a read-only research API, browser
panel and notebook cell, authenticating retained sources without numerical
refresh. The original accepted A_PC and historical projections are preserved
through an exact finite metadata successor.

## Research debt and forward implementation

Resolve `SC-APP-DEBT-A_CI_PC` for the bounded composite root/writer domain, complete C/W/Z
product return, self-consistent stationary W and Z, actual source/event/two-
history transfer, positive completion window, user acceptance and scoped
propagation. This contributes to organization, stability, nonempty-domain and
temporal-lifecycle debts without closing their aggregate native portions.

`SC-ACIPC-VO-NATIVE-NUMERICS` remains pending at P9-9.1a: Explicit quartic/profile identity; uniform selected joint root with incoming signed star-supported carrier and both geometry consumers, same selected source for immediate geometry and carrier writer, incoming-W fixed rows, one selected root for continuity and both independent writers; final-C/incoming-W conductance update and same-read carrier source; positive W/H, closure, floor and carrier envelope domains; full represented 76-dimensional C/W/Z-map error within the strict image margin; exact represented charge and certified spatial predicates. Read residuals or overlap consistency alone are insufficient.

`SC-ACIPC-VO-NATIVE-LIFECYCLE` remains pending there: Actual current/reset histories; exact old-edge W preservation and three new-edge seeds; whole source carrier archives and canonical whole-target zero reset with explicit carrier_history_loss; separate dispositions for the two history channels; lawful resource shares, committed positive windows and elapsed time, invalidation, actual occurrence identity, at-most-once gain, atomic publication with rollback and replay/import/reset conformance.
Research hashes are not universal event occurrence IDs.

Authority → proposal/paper → specification closes bounded A_CI_PC SC-3 scientific
scope, reusing the v2 completion schema. Eight scientific families are accepted;
C_RG2b and A_RG2b remain open. C_RG2b is next. Native completion,
hierarchy, aggregate P9-10.5/10.6 and G4 remain open. The pre-existing broader
audit drift remains documented and unwaived. Acceptance reruns no trajectory.

# A_CI_PC spark-completion applicability — bounded research

2026-11-01. Continue `investigation/grc9v4-spark-completion` after accepted
A_PC (`65382c48`). This is one declared composite construction, pending
scientific adjudication. Seven earlier families remain accepted. The below-100
A_OS investigation stays paused and its earlier-domain review stays separate.

## Composite root and independent writers

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

## Uniform root selection and conditional writer bounds

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

## Full 76-dimensional implicit return

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

## Actual event, transfer and completion

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

## Optimization, evidence and review

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

`SC-APP-DEBT-A_CI_PC` remains open for scientific adjudication. If accepted,
authority → proposal/paper → specification propagation follows. Native
P9-9.1a completion, lifecycle/error/conservation obligations, hierarchy and G4
remain forward. The broader repository audit's pre-existing basin source drift
at `specs/README.md` remains unwaived. C_RG2b is next after review; no RG2b
campaign is started by this work.

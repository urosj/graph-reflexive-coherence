# Spark-completion proposal supplement — A_PC applicability

2026-11-01. Derived from [A_PC authority](../decisions/SparkCompletionAPCSC3Authority.md), and extracted into the [paper](./2026-11-GRC9V4-Spark-Completion-APC.md).

## SC-APC-EC-DOMAIN

`SC-APC-CL-C-DOMAIN` is accepted as conditional mathematics on the declared source/target graphs, signed carrier ball and conditional resource/conductance box. No global resource invariance or arbitrary-graph theorem is admitted.

Use the same positive A parameters as the preceding construction:
eta=1/1024, h=tau_A=tau_PC=32, kappa_c=kappa_Ah=1/64,
chi=zeta=kappa_H=1/2, alpha=beta=gamma=1/32768, W_floor=1/2,
and site(C)=(C−2)^3−(C−2). All 16 conductances and all 46 independent
symmetric, star-supported carrier coordinates remain physical variables.
Their signs are unrestricted within the declared carrier ball.

Let B be oriented incidence, O=|B|^T|B|, and L=log W. Incoming Z alone
selects the physical geometry. Incoming W supplies the weighted fixed-row
means D. The single selected read is

```
H = I + Z/2
Phi = B diag(W) B^T C/64 − site(C) + B(H−I)B^T C/64
j0 = −diag(W) B^T Phi/1024
G_e(C,W,j) = max(1/2, exp(−(C_u+C_v+||D_u−D_v||²+j_e²)/65536))
q_e = (W_e−G_e(C,W,j0))/(W_e+G_e(C,W,j0))
J_e = j0_e/(1−q_e/4)
f = H^(-1)(q*J/2)
S_ij = O_ij f_i f_j/4.
```

Continuity and the two separate writers consume that same read:

```
C+ = C − 32 B J
L+ = exp(−1) L + (1−exp(−1)) log G(C+,W,J)
Z+ = exp(−1) Z + (1−exp(−1)) S.
```

The W writer uses final C+, incoming W and selected J. The Z writer uses
S from the selected incoming-state read. Newly written W and Z are consumed
only by the next ordinary read. There is no CI root iteration or OS predictor
substitution. A read cannot be reused for a different C/L/Z object. These are
investigation equations; existing native machinery is not promoted by this work.

On each concrete graph assume 0≤C≤4, .99≤W≤1.01 and ||Z||_F≤R=1/64,
with symmetric star support. Then 1−R/2≤lambda(H)≤1+R/2, so H is positive
definite even for signed carriers. Put ell=||B^T B||_infinity, m=number of
edges, h0=mR/2, hmin=1−R/2, wl=.99, wh=1.01. Exact rational bounds are

```
j = wh (12 + 4 ell wh/64 + 4 ell h0/64)/1024
g = 1 − (8+192+j²)/65536
a = max(wh−g,1−wl)/(wl+g),       den = 1−a/4
Jmax = j/den
F2 = m (a Jmax/(2 hmin))²
||S||_F ≤ F2/2 < R.
```

The weighted row differences contribute at most 192 and exp(−z)≥1−z
provides the strictly floor-inactive lower bound g>1/2. The source estimate
uses O_ij/4≤1/2 and ||f f^T||_F=||f||_2². The exact convex carrier update
therefore preserves the signed Frobenius ball. Conditional on C+ remaining
in [0,4], the W writer has drive at least 1−(8+192+Jmax²)/65536>.99 and
at most one, preserving its log interval. No global resource-box invariance
is claimed. Actual trajectory states and the certified trap verify that premise.

Weighted selector separation is checked with the conservative factor
.99*(127/128) on both concrete graphs. The trap uses the sharper carrier
radius stated below. Positive carrier geometry and its selector separation
are additional checks beyond the weighted spatial basin predicates.

## SC-APC-EC-FULL-STATE-RETURN

`SC-APC-CL-C-FULL-TRAP` is accepted as conditional mathematics for the full 76-dimensional, exact charge-21 C/W/Z product return, including all conductance and symmetric-star carrier directions and both independent writers.

Borrow only the exact rational C/W center, basis and positive axis radii
from `earlier-closure/AOSAnisotropicDomain.json`. Authenticate the old producer
and operands. Write the full charge-relative C/W domain as
x=x0+Sx u, ||u||_infinity≤1, U Sx=I30. Here x=(C,L), sum C=21.
Extend it by the independently signed carrier ball

```
K = { x=x0+Sx u, ||u||_infinity≤1, ||Z||_F≤rho }, rho=1/2^30.
||delta(x,Z)|| = max(||U delta x||_infinity, ||delta Z||_F/rho).
```

The domain includes 14 resource, 16 conductance and 46 carrier directions.
Carrier columns use the Frobenius-orthonormal symmetric star basis:
diagonal entries one and paired off-diagonal entries 1/sqrt(2). An outer
coordinate box includes K; the derivative is enclosed on that whole box.
The inverse derivative is computed by one multiple-right-hand-side solve:

```
df = H^(-1)((diag(q) dJ + diag(J) dq)/2 − dH f).
```

Both uses of H in the physical read, W-dependent row means, continuity,
final-C W writer and same-read Z source are differentiated. With the full
Jacobian blocks transformed into u and Frobenius carrier coordinates, use

```
a = ||U Txx Sx||_infinity
b = rho * max_i ||(U TxZ)_i||_2
c = sqrt(30) * ||TZx Sx||_F / rho
d = exp(−1) + ||TZZ − exp(−1) I46||_F
q = max(a+b,c+d) < 1.
```

FLINT/Arb at 512 bits proves q<0.995942 and strict unit image margin
>0.004058. The exact rational center defect is enclosed separately. The
first product-domain candidate passes; no trajectory-guided domain search
or tolerance change is used. Source-bound records retain exact outward bounds.

Every edge order is proved by exact support over the actual anisotropic
C/W domain. Weighted row boxes prove seeds, anchors and barriers. Both chiral
charts give the complete basins p:{p,private} and
satellite/2:{n2,n8,satellite/2}. Identical ordered incidence, weighted row
assignments and carrier bases justify sharing evolution across the charts;
both predicate charts are checked separately.

At the full-map fixed point, BJ=0 and J=−D B^T Phi for positive diagonal D.
The quadratic identity Phi^T B D B^T Phi=0 gives J=0, hence f=S=0. Stationary
carrier decay forces Z=0 and H=I; the other writer forces W=G(C,W,0).
This establishes the stationary conductance writer and carrier together.
Neither history channel is frozen in the neighborhood proof.

## SC-APC-EC-COMPLETION

`SC-APC-CL-C-COMPLETION` is accepted as conditional mathematics for the declared actual source/event/two-history transfer/approach/window chain. Current, reset and read-only replay remain distinct; reset and replay earn no live gain.

SC2 exact resource prestates initialize a fresh A_PC source beat. Current W
starts at 4097/4096 and current Z has diagonal 1/65536. Independent reset W
starts at 8191/8192 and reset Z has diagonal −1/131072. Reset is not advanced.
A fresh read of committed current C/W/Z supplies the event subject. Complete
parent qualification, saturation, and both strict trigger margins are checked.

The declared D11 resource shares are 1/128,63/64,1/128, with zero core and
copied exterior. Each old edge keeps its own W; exactly three new internal
edges start at W=1. Both complete nonzero source carriers are archived with
their digests, and each complete target carrier is canonically zeroed. The
carrier channel explicitly records `carrier_history_loss`; the conductance
channel records preservation. There is no untyped resizing or erased loss.

Allocation alone gives no new qualified child. Fresh outward interval
trajectories give current entry **375**, window end **377**, local gain **one**;
reset entry **372**, window end **374**, local gain **zero**. Both runs take
about **33 seconds**, versus about 101 seconds for A_CI. Matching beat numbers
are independently obtained, not borrowed A_CI or A_OS execution evidence.
The positive window is two beats and elapsed time 64. These are sufficient
witness times, not earliest-completion claims.

The declaration fixes 8192-bit trajectories, 512-bit trapping arithmetic,
a 1024-beat horizon and one-hour wall caps for each role. No midpoint evolves
the physical state, automatic fallback or precision escalation is used.
Exact graph/domain caches, weighted-row reuse, one selected poststate read
per beat, batched derivative solves and chiral identity pass an eight-step
preflight before either full run. Each beat performs one W update and one
Z update. No pilot or earlier-family trajectory supplies campaign states.

All 751 states retain outward 112-bit C/logW/Z inspection enclosures; the
full-precision intervals remain recurrence operands. Raw execution records
are 11,059,258 bytes, losslessly XZ compressed to 1,070,264 bytes. The checker
rebuilds source/transfer and the full product trap, recomputes all coordinates,
complete basins and entries, checks every transition and whole selected-read
checkpoint, and rejects 21 altered-evidence controls. Saved overlap is
consistency evidence; source-bound outward recurrence supplies enclosure
provenance. There is no independent duplicate long trajectory or external
reviewer claim. Five equation tests include a separate 110-digit implementation
and every one of the 76 physical derivative directions.

## Research debt and forward implementation

Resolve `SC-APP-DEBT-A_PC` for the bounded read/writer domain, complete C/W/Z
product return, self-consistent stationary W and Z, actual source/event/two-
history transfer, positive completion window, user acceptance and scoped
propagation. This contributes to organization, stability, nonempty-domain and
temporal-lifecycle debts without closing their aggregate native portions.

`SC-APC-VO-NATIVE-NUMERICS` remains pending at P9-9.1a: Explicit quartic/profile identity; incoming signed star-supported carrier geometry, incoming-W fixed rows, one selected read for continuity and both independent writers; final-C/incoming-W conductance update and same-read carrier source; positive W/H, closure, floor and carrier envelope domains; full represented 76-dimensional C/W/Z-map error within the strict image margin; exact represented charge and certified spatial predicates. Read residuals or overlap consistency alone are insufficient.

`SC-APC-VO-NATIVE-LIFECYCLE` remains pending there: Actual current/reset histories; exact old-edge W preservation and three new-edge seeds; whole source carrier archives and canonical whole-target zero reset with explicit carrier_history_loss; separate dispositions for the two history channels; lawful resource shares, committed positive windows and elapsed time, invalidation, actual occurrence identity, at-most-once gain, atomic publication with rollback and replay/import/reset conformance.
Research hashes are not universal event occurrence IDs.

Authority → proposal/paper → specification closes bounded A_PC SC-3 scientific
scope, reusing the v2 completion schema. Seven scientific families are accepted;
A_CI_PC, C_RG2b and A_RG2b remain open. A_CI_PC is next. Native completion,
hierarchy, aggregate P9-10.5/10.6 and G4 remain open. The pre-existing broader
audit drift remains documented and unwaived. Acceptance reruns no trajectory.

# A_PC spark-completion applicability — bounded research

2026-11-01. Continue the spark-completion branch after accepted A_CI. This is
one declared A_PC construction, pending scientific adjudication. It does not
change SC-1, earlier accepted authority, native completion or G4. The below-100
A_OS investigation remains paused.

## Actual A_PC equations and independent histories

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

## Uniform read and writer domain

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

## Full 76-dimensional product trap

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

## Actual source, event and transfer

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

## Optimization, retained evidence and limits

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

Inspect `APCResearchProgress.json`, `APCChecks.json`, `APCValidation.json`, the
side-tool A_PC research panel/API and notebook cell. Earlier accepted and
historical views retain their exact identities through a finite metadata
successor. A_PC research debt remains open for scientific adjudication and,
if accepted, authority → proposal/paper → specification propagation. Native
error/conservation, both history lifecycles, occurrence accounting, atomicity,
hierarchy and aggregate G4 remain forward. The broader repository audit's
pre-existing `specs/README.md` source drift remains unwaived. A_CI_PC is next
after review; no campaign for that family is started here.

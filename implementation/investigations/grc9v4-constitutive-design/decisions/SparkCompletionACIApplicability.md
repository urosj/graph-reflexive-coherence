# A_CI spark-completion applicability — bounded research

2026-10-31. Research on the existing spark-completion branch, pending scientific
review and adjudication. The accepted scientific families remain C_OS, C_CI,
C_PC, C_CI_PC and A_OS. SC-APP-DEBT-A_CI remains open. Native completion,
hierarchy, aggregate P9-10.5/10.6 and G4 receive no new support.

The user requested the next family after committing the earlier A_OS domain
at `8d1a0e12`. The below-100 A_OS investigation remains paused. This work uses
the existing SC-1 definition, including its uniform ordering requirement.

## Actual A_CI law and selected root

All A parameters are unchanged from the declared positive A_OS construction:
eta=1/1024, h=tau_A=32, kappa_c=kappa_Ah=1/64, chi=zeta=kappa_H=1/2,
alpha=beta=gamma=1/32768, W_floor=1/2 and site(C)=(C−2)^3−(C−2).
For incoming C,W, weighted fixed-row means are formed on the declared port
chart. Put O=|B|^T|B| and

```
H(f) = I + diag(f) O diag(f)/8
Phi = B diag(W) B^T C/64 − site(C) + B(H−I)B^T C/64
j0 = −diag(W) B^T Phi/1024
G_e = max(1/2, exp(−(C_u+C_v+||D_u−D_v||²+j0_e²)/65536))
q_e = (W_e−G_e)/(W_e+G_e),       J_e = j0_e/(1−q_e/4)
F(C,logW,f) = H(f)^(-1) (q*J/2),       f = F(C,logW,f).
```

Geometry, its contribution to Phi, the flat/current closure, continuity and
the writer use this **one selected joint root**. There is no OS predictor or
corrector substitution. Continuity is C+=C−32BJ. The writer uses final C+,
incoming W and that same J:

```
logW+ = exp(−1) logW + (1−exp(−1)) log G(C+,W,J).
```

Newly written W is available only to the next ordinary read. The local API
rejects use of a root with a different C/logW object.

## Uniform root selection and enclosure

The exact rational root-domain calculation applies to both concrete graphs,
uniformly for 0≤C≤4, 99/100≤W≤101/100 and ||f||∞≤r=1/32. Let
ell=||B^T B||∞, S=max_i sum_j O_ij/8, h0=S r² and u=1/(1−h0).
Then ||H−I||∞≤h0 and ||H^(-1)||∞≤u. Define the rational bounds

```
j = Wmax (12 + 4 ell Wmax/64 + 4 ell h0/64)/1024
g = 1 − (8 + 192 + j²)/65536
a = max(Wmax−g, 1−Wmin)/(Wmin+g),       d = 1−a/4
Jmax = j/d,       M = u a Jmax/2
jH = 4 Wmax ell/65536
qj = 4 Wmax j/(65536 (Wmin+g)²)
Jj = 1/d + j qj/(4d²)
FH = u ((a Jj + Jmax qj) jH/2 + M)
Lroot = 2 S r FH.
```

The bound 192 comes from three differences of weighted row means, each at
most eight in absolute value. The site bound is six. The rational inequality
exp(−z)≥1−z supplies g>1/2, so the floor is strictly inactive throughout
the root domain. The computed M<r and Lroot<1 prove existence and uniqueness
**within this declared ball**. No global root uniqueness is asserted. The
target root bound is below 2.29×10^-6. H is also positive definite because O
is a Gram matrix; the Neumann bound provides an explicit infinity-norm estimate.

Newton calculations propose a rational midpoint fhat. Only proposals use
the fixed precision sequence 128,256,…,8192, with at most twelve iterations
per precision. At full precision, the residual is evaluated on the **actual
input intervals**, giving ||f−fhat||∞≤||F(C,logW,fhat)−fhat||∞/(1−Lroot).
Every selected read then uses that entire root enclosure. The physical
trajectory is never replaced by midpoint states, and there is no automatic
precision escalation, fallback or tolerance widening.

## Implicit full-state return

The A_OS rational center and anisotropic domain are borrowed as an explicit
candidate. Their scientific conclusion, derivative and trajectory are not
borrowed. Write x=(C,logW), restrict only by exact charge 21, and retain all
14 resource plus 16 conductance directions. The borrowed exact rational
matrices give K={x0+S z: ||z||∞≤1}, with U S=I30. Positive radii and the exact
inverse give a positive relative neighborhood in every independent coordinate.

Differentiate the joint root, including both uses of H:

```
df/dx = (I−F_f)^(-1) F_x
dJ/dx = J_x + J_f (I−F_f)^(-1) F_x.
```

The partial H derivatives use one multi-right-hand-side solve. The same
selected J and its total derivative are then differentiated through C+ and
the final-C/incoming-W writer. FLINT/Arb encloses the resulting full map
Jacobian throughout a coordinate box containing K. The transformed row sums
bound ||U DT(x) S||∞ by q<0.995934130. The center defect gives a strict unit
image margin greater than 0.00406587. Root contraction and ordinary physical
contraction are distinct bounds, both freshly proved for A_CI.

Both chiral charts have identical ordered incidence and weighted-row
assignments. This justifies sharing physical evolution; predicates are checked
for both charts. Exact linear support over K proves every edge order, and
weighted row enclosures resolve all seeds, anchors and barriers. The complete
basins are p:{p,private} and satellite/2:{n2,n8,satellite/2}. W remains between
0.99 and 1.01, with the weighted selector separated from the fixed cutoff.

At a full-map fixed point, BJ=0 and J=−D B^T Phi with positive diagonal D.
Thus Phi^T B D B^T Phi=0 implies J=0. The **joint** root then gives f=0 and
H=I; the writer forces W=G(C,W,0). This establishes a self-consistent stationary
writer rather than freezing a history channel.

## Source, event, transfer and retained result

Exact SC2 resource prestates supply inputs to a fresh A_CI ordinary source
beat, not a reused A_OS state. Current W starts at 4097/4096; reset W starts
independently at 8191/8192 and is not advanced. A fresh joint root on the
committed source C/W supplies the event trigger. The weighted classifier
qualifies the complete parent p, and saturation and both strict trigger
margins are checked on that same source.

The declared D11 allocation is 1/128,63/64,1/128 with zero core and copied
exterior. It preserves each old edge's own W through literal edge identity,
and seeds exactly three new internal edges at W=1. Allocation alone has only
the original qualified basin and earns no gain. Charge conservation follows
from incidence and rational shares, without numerical normalization.

Current enters at **375** and completes its positive window at **377**,
earning one local child. Reset enters at **372** and ends at **374**, earning
zero live gain. Both fresh campaigns took about **101 seconds**. The 751
retained states and whole-root checkpoints occupy 5,916,381 raw bytes,
compressed to 760,524 bytes. These matching A_OS times are independently
obtained A_CI results, not reused entries.

Campaign results and validation are recorded in `ACIResearchProgress.json`,
`ACI-current.json.xz`, `ACI-reset.json.xz`, `ACIChecks.json` and
`ACIValidation.json`. The declaration fixes 8192-bit trajectory arithmetic,
512-bit trapping arithmetic, a 1024-beat horizon, one-hour caps per role and
a two-beat positive completion window. The source-bound optimization preflight
must pass before either full run. All stored C/logW coordinates are outward
112-bit views; full-precision intervals remain the recurrence operands.

Graph constants and rational root domains are cached. Weighted rows are
reused within each root proposal, and full roots are reused only on an
identical physical subject. Each target beat consumes one root, performs
one writer update and computes exactly one next-state root. Earlier-family
trajectories and pilot states never feed either campaign. Large evidence is
losslessly XZ compressed.

The retained checker rebuilds the source and transfer, independently rechecks
the full implicit trap, recomputes both basin rosters and entry from all
coordinates, and checks every saved transition and whole-root checkpoint.
Transition overlap is consistency evidence; the bound producer's outward
recurrence supplies enclosure provenance. Independent 110-digit equations
and a Picard root, all thirty physical derivative directions, all sixteen
flat-coordinate partials, and staging/lineage controls support review. No
independent external reviewer or duplicate long trajectory replay is claimed.

## Inspection and next action

The read-only side-tool API `/api/spark-completion/applicability/a-ci/research`,
browser panel and notebook cell `spark-completion-a-ci-research` expose the
source-bound result without numerical reruns. A finite metadata successor
preserves earlier accepted, historical research and anisotropic A_OS views.
The historical A_OS helper download returns its reviewed Git bytes.

Review/adjudicate this bounded A_CI result next; authority → proposal/paper →
specification propagation follows only if accepted. A_PC is the next family
afterward. Native numerical/lifecycle obligations remain at P9-9.1a, and
hierarchy/G4 remain separate. The pre-existing repository audit failure at
`specs/README.md` remains documented and unwaived.

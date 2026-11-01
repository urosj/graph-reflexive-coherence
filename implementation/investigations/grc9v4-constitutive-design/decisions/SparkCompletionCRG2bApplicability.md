# C_RG2b completion applicability — research, pending review

This construction selects a fresh quartic, completion-relative C_RG2b section
on the 12-vertex source and 15-vertex expansion. Physical state is C alone.
Geometry is derived separately on each graph; no geometry history is carried
through the event. The accepted eight-family authority remains unchanged.
A_RG2b follows this family. Native completion, hierarchy and G4 remain forward.

## Frozen completion and section

Use eta=1/1024, duration=8, kappa_Phi=1/64, kappa_M=0 and the existing quartic
site law (C−2)^3−(C−2). With B the outward-tail incidence and D=B^T B,
M=3I/4+HD, phi=BHB^T C/64−site(C), j0=−eta B^T phi,
y=M^-1 j0, J=j0+y/4, f=−8BJ, flat=H^-1 y/2 and
G=I+O_ij flat_i flat_j/8. Both geometry consumers are included.

The auxiliary completion is Fhat(X,H)=X+f(PX,H), Ghat(X,H)=G(PX,H).
P retracts the argument coordinatewise to the declared closed box. It does
not clip the physical trajectory. The source argument box is [1/2,7/2],
K_minus=[7/8,25/8], K=[9/16,55/16]. The target argument box is
[−1/16,65/16], K_minus=[−1/32,129/32], K=[−3/64,259/64]. U is the
open argument box; both nested inclusions are strict. The source displacement
bound and target separable cubic image calculation, with the uniform H
perturbation added, certify F(K_minus) inside K. These are agreement charts,
not claims that every resource box is forward invariant. The signed target
chart accommodates the zero event core.

Geometry uses the symmetric star-supported matrix space with induced infinity
norm, radius rho=1/1024 about I. Sections have Lipschitz constant at most
L=1/256 on all auxiliary X. Neumann bounds certify both inverses; the graph
spectral lower bound times (1−rho) exceeds 1/64, with kappa_M=0. Global
quartic bounds A_X,A_H,G_X,G_H are derived anew in the implementation.
Let e=A_X+A_H L and v=1/(1−e). Exact rational checks establish e<1,
V<rho, L_image=(G_X+G_H L)v<=L and
q=G_H+(G_X+G_H L)v A_H<1. Thus each completed base map is globally
invertible, and graph transform T gamma=Ghat∘(id,gamma)∘F_gamma^-1
is a contraction in the sup norm on the closed bounded Lipschitz class.
Its unique fixed point Gamma satisfies Gamma(F(C,Gamma(C)))=G(C,Gamma(C))
on the physical agreement domain. This is a C0/Lipschitz argument: there is
no assumed classical derivative of Gamma, no section spectrum and no reuse
of the native zero-site inverse bounds.

## Finite evaluation and error tubes

Sixteen transform levels start from the identity section. Proposal chains
have X0=C and H16=I. Each inverse uses Newton on fixed H, with operators
reused within that inverse; this derivative concerns a fixed-H polynomial,
not Gamma. At most eight simultaneous geometry sweeps run at 256 bits.
An early-stop test only reduces proposal work. Every returned chain is
checked afresh at 512 bits, including retraction, symmetry, support, both
boundary conditions and both residuals. With residual maxima rX,rH,
E <= (rH+L rX)/(1−q)+q^16 V.
Indeed, comparing level i with its exact finite iterate gives
error_(i−1)<=rH+L_image rX+q error_i, and terminal error is zero.
The geometric tail then reaches the invariant section. A midpoint never
stands in for the physical section or exact trajectory.

Immutable graph algebra uses FLINT rational matrices. Only identity-H
operators have a reusable precision-keyed numerical cache. Other fixed-H
operators are local to a proposal inverse. A selected read is reused only
on the identical center. No section, state or trajectory result is cached.

Let A0=B(I+(3I/4+D)^-1/4)B^T and Pmetric=(A0+11^T/n)^-1 restricted to
the exact charge-21 tangent. Its eigenvalue bounds are 1/trace<=lambda(A0)
<=amax, where trace=tr(Pmetric)−1. Tubes enclose the physical state by
||C−center||_P<=r. Dyadic centers have exactly charge 21; all projection and
rounding defects enter r. A coordinate box has width sqrt(amax) r.
The recurrence is r_next>=q_return r+sqrt(trace)||F(center,Gamma(center))
−center_next||_2, rounded upward. Finite section and arithmetic errors enter
the second term. Event allocation transports the radius with the explicit
linear operator norm, including conversion error. Rational reset input is
enclosed before its dyadic conversion and is not advanced at the source.

For q_return, the fixed-I derivative I−eta*duration*A0*(diag(site')−BB^T/64)
is self-adjoint in this metric. Eigenvalue bounds on the entire coordinate
box give its norm. Fixed-H perturbations include the change in the current
inverse and BHB^T, and the separate H difference term uses only the proved
section Lipschitz bound. A smaller local section bound comes from the whole
inverse footprint R=v*(sqrt(amax)r+||f(center,Gamma(center))||_infinity).
Uniform local G_X,G_H on that footprint give
L_local<=min(L,(G_X_local+G_H_local L)v). This controls differences between
any two query points; it does not differentiate Gamma. Conversion between
Euclidean and P norms uses sqrt(amax*trace).

## Full return, event and observation window

The candidate fixed-point center is freshly proposed from the equilibrium
equations. The target radius is 1/8192. The full return bound must satisfy
q_return<1 and (1−q_return)radius−center_defect>0. Both chiral charts must
certify complete basins p:{p,private} and satellite/2:{n2,n8,satellite/2}
on the whole ball. All fourteen independent resource directions are covered.

Duration eight is an explicit new declaration, chosen to satisfy the quartic
completion inverse bounds. A new exact prestate is proposed by the fixed-I
inverse toward the supplied source candidate, then frozen before campaigns.
The actual source section/read/beat, fresh poststate trigger and complete
parent are checked. The lawful target shares are 1/64,31/32,1/64, core zero.
No previous-family entry, trajectory or completion decision is reused.
Positive target beats stay in the agreement chart, with exact charge and
strict positivity. Two further ordinary beats after certified trap entry
provide the positive observation window, elapsed time 16. Reset earns no
live gain. Horizons are 8192 beats and caps one hour per role; failures do
not trigger an automatic fallback or relaxed tolerance.

All exact centers, outward radii and complete basin observations are retained
in XZ evidence. Complete finite chains at source/event/entry/completion make
section error claims inspectable. Each checkpoint also retains a physical
read widened by the section Lipschitz constant times the whole tube width. Retained transition checking recomputes
selected sections and checks every tube step; it is a consistency check,
not a separately implemented duplicate trajectory proof. Source-bound FLINT/
Arb execution supplies enclosure provenance. Independent equation, inverse,
section-invariance and perturbation controls supplement it; no independent
external reviewer is claimed. Scientific adjudication remains pending.

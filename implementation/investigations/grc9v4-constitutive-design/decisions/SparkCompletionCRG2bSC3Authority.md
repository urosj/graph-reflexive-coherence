# SC-3 — C_RG2b direct completion adjudication

2026-11-01. The user instructs “awesome, let's accept and commit”. Admit the
three bounded conditional claims below. Research checkpoint `54a8cdb3`
preserves the direct certificate, compressed 392-step prefixes, historical
records, exact generators and validation. The acceptance is completion-relative
and assumes no differentiability of Gamma. Author-side validation includes two
same-implementation prefix replays; no independent external review is claimed.
[Machine authority](./spark-completion-c-rg2b/Authority.json).

## SC-CRG2B-EC-DOMAIN

`SC-CRG2B-CL-C-DOMAIN` is accepted as conditional mathematics for the declared quartic source/target completion, unique Lipschitz section and certified physical evaluation. No section derivative, global resource-box invariance or arbitrary-graph theorem is admitted.

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

## SC-CRG2B-EC-FULL-STATE-RETURN

`SC-CRG2B-CL-C-FULL-TRAP` is accepted for the direct continuous domain on the exact charge-21 hyperplane, with every one of its fourteen independent physical directions, a common pairwise contraction and strict self-map.

### Domain and direct self-map

On the charge-21 hyperplane, write

- `B` for incidence, `D=BᵀB`, `L=BBᵀ`, `M₀=(3I/4+D)⁻¹`;
- `A=B(I+M₀/4)Bᵀ`, `P=(A+11ᵀ/n)⁻¹`;
- `F₀(C)=C+h A[L C/64−((C−2)³−(C−2))]`, `h=1/128`.

The declared exact rational polynomial `p(s)` has degree 40 in the Chebyshev
basis `T_k(2s−1)`. Its coefficients sum to 21 for degree zero and zero otherwise.
The domain is

`K={p(s)+v: 0≤s≤1, 1ᵀv=0, vᵀPv≤R²}`, with `R=1/4096`.

This is a compact continuum of full 14-dimensional balls. It is not a finite
list of subsequent executed states. Floating collocation proposed the curve
using only the stationary reference proposal and the current endpoint at 390.
No future trajectory was used as collocation data. The exact coefficients are
fixed inputs; SciPy and floating proposals are outside the trusted checker.

Set `ρ=999/1000`. Exact Chebyshev multiplication and composition give every
coefficient of the degree-120 residual

`r(s)=F₀(p(s))−p(ρs)`.

Since `|T_k|≤1`, `sup ||r(s)||_P ≤ Σ_k sqrt(r_kᵀ P r_k)`.
The checker obtains approximately `3.35685e−13`. This bound covers all real
parameters in `[0,1]`, not a numerical sampling grid. The reference origin is
not assumed to be an exact fixed point; its residual is included.

The complete physical map is `F(C)=F_H(C,Γ(C))`. The estimates below give a
common pairwise contraction `q≈0.99739692045` on the convex hull of K, and
`sup_s ||F(p(s))−F₀(p(s))||_P ≤ 1.44791e−8`. Consequently,

`||F(p(s)+v)−p(ρs)||_P ≤ qR + δ < R`,

where `δ` includes both the exact polynomial residual and the physical geometry
correction. The strict margin is greater than `6.21038e−7`. Since `ρs∈[0,1]`,
every image lies in the relative interior of K. The common contraction applies
to every pair in K, even if they belong to different constituent balls. Thus the
original SC-1 contract and Banach argument apply without any later trajectory.

### Local geometry bound without differentiating Γ

The original global graph-transform proof and its unique section are retained.
In particular its global Lipschitz constant is `1/256` and its global value
radius is approximately `0.0001851984`. The sharper bounds below concern that
same section; they do not define a new completion.

Let `c=p(0)`. The convex hull of K is within the cube `||C−c||∞<7/50`.
For every query in this cube, certify its inverse in the larger cube
`||X−c||∞≤1/5`. Both cubes lie inside physical argument agreement, so the
argument retraction is inactive there.

For the fixed section, the inverse iteration is
`X ↦ Y−f(X,Γ(X))`. The checker bounds its Lipschitz constant by

`a = ||h A D_loc||∞ + physical-H perturbation + A_H,global Lip(Γ)`,

where `D_loc=L/64−diag(3(X−2)²−1)` on the inverse cube. It proves both `a<1`
and `7/50+||f(c,Γ(c))||∞+a/5<1/5`. Hence this iteration has a unique inverse
in that cube, with Lipschitz constant at most `1/(1−a)≈1.310375721`.
Uniqueness of the original global inverse identifies this local inverse with
the frozen completion inverse. No assumption about a future orbit enters.

For completeness, the implemented local current bounds use exact cached
matrices `M₀Bᵀ` and `M₀D`, retaining their cancellations. Put `V=V_global`,
`ε=||M₀||∞ V ||D||∞`, and let `R_x=1/5`, `z=sup||BᵀX||∞` on that cube.
Writing `y=(3I/4+HD)⁻¹j₀`, with `j₀=−ηBᵀΦ_H`, gives

`Y ≤ (||y(c,I)||∞ + Y_X,0 R_x + η||M₀D||∞ V z/64)/(1−ε)`,

`Y_X ≤ (Y_X,0 + 2η||M₀D||∞ V/64)/(1−ε)`,

where `Y_X,0=||−ηM₀BᵀD_loc||∞`. These follow directly from
`(I+M₀(H−I)D)y=M₀j₀`; they are not scalar approximations to its inverse.
For the H partial bound use

`||Dy||∞ ≤ min(||D||∞Y, ||H⁻¹||∞ (||j₀||∞+3Y/4))`,

`Y_H ≤ ||(3I/4+HD)⁻¹||∞ (η||D||∞ z/64+||Dy||∞)`.

For `flat=H⁻¹y/2`, bound its value and both partials, then the symmetric-star
outer-product geometry `G=I+star(flat flatᵀ)/8`. With `s_star` the maximum
overlap-row sum divided by eight,

`G_X ≤ 2 s_star flat_bound flat_X`,
`G_H ≤ 2 s_star flat_bound flat_H`.

The section invariance equation, composed with the proved inverse, yields

`Lip(Γ)_local ≤ (G_X+G_H Lip(Γ)_global)/(1−a) ≈ 1.31248e−6`,

`||Γ−I||∞,local ≤ s_star flat_bound² ≈ 9.95611e−8`.

Only partial derivatives of the smooth two-input physical maps are used.
Γ remains merely Lipschitz; no derivative or C1 regularity of Γ is assumed.

### Full physical contraction and geometry correction

On the hull box, exact rational LDL checks prove the charge-tangent Rayleigh
inequalities

`(1/3)P < diag(3(C−2)²−1)−L/64 < 64P`.

The fixed-identity derivative is self-adjoint in the P metric, so its norm is
at most `max(|1−h/3|,|1−64h|)`. The checker adds the fixed-H perturbation and
the H partial slope times the local section Lipschitz bound. The latter is a
difference estimate, not a chain rule for Γ. Both physical H consumers—the
potential `BHBᵀC/64` and the current inverse `(3I/4+HD)⁻¹`—are included.
Conversions use `||v||₂≤sqrt(||A||∞)||v||_P` and
`||w||_P≤sqrt(trace(P|1⊥))||w||₂` for tangent vectors.

The same H slope, integrated on the segment from I to Γ(C), gives the absolute
physical geometry correction used in the functional residual. All matrices on
this segment remain in the proved symmetric geometry ball.

### Uniform spatial predicates and entry

The checker converts the exact curve to Bernstein form and subdivides into
64 closed parameter intervals. For every linear functional `wᵀC`, Bernstein
coefficient extrema bound `wᵀp(s)`, and the exact tangent support function is
`R sqrt(wᵀAw)` because `APA=A` and `A1=0`. This preserves coordinate
correlations; a coordinate box alone would lose some small edge inequalities.

These bounds certify every fixed-row seed predicate, resource/contrast
barrier, edge direction, destination set and complete basin roster, for both
chiral charts and every state in K. The minimum edge margin is greater than
`6.68989e−5`. The two qualified basins remain `p:{p,private}` and
`satellite/2:{n2,n8,satellite/2}`. All 14 independent resource directions have
positive radius, and all resources remain positive within physical agreement.

Fresh current and reset prefixes enclose the full physical trajectories using
Arb at 512 bits. Exact charge, section-tail/rounding errors and strict tube
transfers are retained. Section reuse follows the invariant-section equation,
including center-shift error, with fresh rebuilds at 1,390,392. Explicit tube
membership is checked at 390,391,392 against parameters `1,ρ,ρ²`.
The reset endpoint distance is about `0.000213746`, strictly below `1/4096`.
Reset and read-only replays earn zero live gain.

## SC-CRG2B-EC-COMPLETION

`SC-CRG2B-CL-C-COMPLETION` is accepted for the declared actual source/event/resource transfer, physical approach and positive window. Current earns one local child; reset and read-only replay earn zero live gain.

The exact prestates and allocation are fixed in `CRG2bDirectDeclaration.json`.
They equal the selected faster construction: shares 5/2048,1021/1024,1/2048,
zero target core, copied exterior and exact total charge 21. An actual positive
source beat supplies the committed current state; a fresh section/read verifies
the complete parent, saturation and strict trigger. The reset prestate is
independently declared and not advanced at the source. The target section is
rebuilt on the new graph; geometry is derived and is never transported as history.
Allocation alone earns no new child.

Both fresh physical prefixes enter the direct domain at 390 and finish the
positive two-beat window at 392. Ordinary duration is 8, window elapsed time 16,
and elapsed target time 3136. These are sufficient witness times, not an
optimality or earliest-completion theorem. Every physical center, propagated
error tube and section enclosure through 392 matches the earlier selected
prefix. The domain and both roles require zero subsequent supporting steps.

Certified section reuse follows Gamma(F(C,Gamma(C)))=G(C,Gamma(C)), with the
complete generated-geometry enclosure error and Lipschitz center-shift error.
The stored proposal is dyadic 256-bit; physical certification is 512-bit Arb.
Every inherited finite-section, allocation, quantization and roundoff error
is propagated in an exact-charge P-metric tube. Fresh rebuilds at 1,390,392
check consistency. Explicit tube membership at parameters 1,rho,rho² verifies
390,391,392, with uniform complete basins in both chiral charts. No midpoint
stands for the exact physical trajectory or section.

Both complete 392-step prefixes were freshly replayed with the same
implementation. Six direct scientific tests exercise exact polynomial
identities, all fourteen directions, whole-domain/order/inverse failures and
tail isolation; seven surface tests preserve prior accepted/research views.
The exact domain checker accepts no trajectory input. No independent external
review is asserted. Immutable graph algebra, precision-keyed identity
operators and invariant-section reuse remain active. The one-hour cap is
retained; the selected prefixes took about 11 seconds each.

Only 784 selected states are retained in full, XZ compressed from 32,765,080 to
2,622,836 bytes. Superseded baseline and finite-union runs retain their original
hashes, parameters, check records, summaries and exact generators. Their full
payloads are absent and not rechecked. The accepted certificate has no dependency
on the former 2089-step supporting trajectories. Duration 32 remains uncertified;
no short steps are relabelled as long beats and eta is unchanged.

## Research debt and forward implementation

Resolve `SC-APP-DEBT-C_RG2b` for the bounded completion-relative Lipschitz
section, direct full-state domain, actual source/event/approach/window chain,
user acceptance and authority → proposal/paper → specification propagation.
The original SC-1 contract and v2 completion schema are unchanged. Nine
scientific families are now accepted; A_RG2b is the remaining family and next
research task. Its section/writer bounds need their own proof.

`SC-CRG2B-VO-NATIVE-NUMERICS` remains pending at P9-9.1a: Explicit quartic/profile, duration 8 and frozen completion identity; certified unique Lipschitz section with both physical geometry consumers, local inverse/value/difference bounds and finite-chain/reuse errors; full represented 14-dimensional charge-tangent map error inside the direct polynomial-domain image margin, exact charge and certified spatial predicates. No C1 Gamma assumption, frozen-H substitution, sampled-parameter test or later-trajectory dependency may replace the proved full-map contract.

`SC-CRG2B-VO-NATIVE-LIFECYCLE` remains pending there: Actual committed source beat/read and separately declared reset; lawful exact resource shares and rebuilt target section with no geometry-history transport; entry 390 and positive two-beat window ending 392 at duration 8, elapsed time and invalidation, actual occurrence identity, at-most-once gain, atomic publication with rollback, and replay/import/reset conformance. Reset/replay earn zero live gain.

These are scientific/design contracts, not a native implementation promotion.
Hierarchy, aggregate P9-10.5/10.6 and G4 remain open. Research hashes are not
universal occurrence IDs. The existing specs/README.md source drift remains
unwaived. Acceptance performs no numerical campaign; the reviewed compressed
prefixes, historical records and all original flags remain unchanged. Earlier
accepted proofs remain valid; A_OS below 100 stays paused.

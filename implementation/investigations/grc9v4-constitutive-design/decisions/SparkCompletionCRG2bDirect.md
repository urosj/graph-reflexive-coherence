# C_RG2b direct closure at 390 → 392

Status: demonstrated bounded research, pending scientific review. No acceptance,
native completion, G4 admission or new live gain from replay is asserted.

Both current and reset now require only 392 executed target steps. A direct
invariant domain contains the state at 390; the unchanged two-beat window ends
at 392. The certificate does not load or require states 393–2089. Duration is
still 8, so elapsed ordinary time to completion is 3136. The source preparation,
allocation, graph, physical coefficients and unique invariant-section completion
are exactly those of `CRG2bFasterDeclaration.json`. Duration 32 remains
uncertified. This work strengthens the certificate for the same trajectories.

## Domain and direct self-map

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

## Local geometry bound without differentiating Γ

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

## Full physical contraction and geometry correction

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

## Uniform spatial predicates and entry

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

## Reproduction and retention

Run from the repository root:

```sh
.venv/bin/python implementation/investigations/grc9v4-constitutive-design/scripts/check_spark_completion_c_rg2b_direct.py
.venv/bin/python implementation/investigations/grc9v4-constitutive-design/scripts/check_spark_completion_c_rg2b_direct.py --replay
.venv/bin/python implementation/investigations/grc9v4-constitutive-design/scripts/test_spark_completion_c_rg2b_direct.py
```

`--generate` recreates the fixed declaration's certificate and compressed
392-step prefixes. `--export-proposal-inputs /tmp/crg-curve-inputs.json`
exports only graph algebra, the reference center and endpoint390 for the
optional `propose_spark_completion_c_rg2b_curve.py --inputs ... --output ...`
SciPy proposal search. Exact certification uses only FLINT/Arb.

Superseded 2089-step payloads are unnecessary for this certificate. Their run
summaries, original digests, check records, declarations and unchanged
scientific generators are retained as history. Only the selected direct
prefixes are retained in full. Historical verification is not presented as a
fresh check of deleted payloads. A full same-implementation replay and mutation
controls are recorded in `CRG2bDirectChecks.json`; no independent external
scientific review is claimed.

The general curved-domain lemma can be reused for another realization, but
its polynomial, metric, section bounds and physical error estimates must be
certified for that realization. Existing accepted certificates remain valid;
this result does not require retroactively changing them.

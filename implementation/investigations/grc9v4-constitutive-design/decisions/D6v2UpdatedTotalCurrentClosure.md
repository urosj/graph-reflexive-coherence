# D6-v2 Updated Total-Current Closure

Status: `accepted_bounded`.

Record: `GRC9V4-CD-D6V2-v1`.

## Gate Question

D5-v2 leaves three candidate-local directional operators:

```text
A = unchanged diagonal retained-mobility contrast
B = metric-raised signed bilinear carrier
C = retained-sector-conditioned Hodge response under a non-isometric map
```

D6-v2 asks whether each can participate in a regular same-beat total-current
closure without hiding geometry re-entry, adding an independent current state,
or confusing exact invertibility with robust physical conditioning.

The bounded result is:

```text
A = accepted D6 closure carried unchanged
B = bounded regular algebraic closure admitted
C = bounded retained-mediated regular algebraic closure admitted

D7-v2 eligible candidates = [A, B, C]
current temporalization selected = false
candidate ranking performed = false
```

This is a constitutive design result. It is not runtime reachability, a complete
candidate transition, global `H_4`, structural cultivation, or architecture
selection.

## Common Solve Order

For candidate `a`, the selected current equation is

```text
J_C,a = J0,a(X_pre,a) + zeta_a chi_a R_a J_C,a

L_a = I - zeta_a chi_a R_a

J_C,a = inverse(L_a) J0,a.
```

The following objects are frozen before the solve:

```text
retained representation
candidate-local geometry or mobility
metric identification
topology, boundary, and live current space
baseline current J0
declared read context
```

`R_a` denotes the intrinsic ungated operator in this gate. D5-v2 sometimes
writes the gated response as `chi_a R_a`; D6-v2 factorizes that notation and
applies `chi_a` exactly once in `L_a` and `j_a`.

The following paths are not inside this reduced same-beat solve:

```text
J_C -> retained-state write -> R
j -> K_4 -> h_4 or h_a -> J0
J_C -> selector or metric identification
j tensor j -> geometry -> current
```

Under that staging, the complete effective current block is exactly

```text
B_eff,a = zeta_a chi_a R_a.
```

If a later gate moves any excluded path inside the solve, D6-v2 must be
reopened. Endpoint compatibility between two stages is not evidence that their
crossing is already inside the effective block.

Only solved `J_C` enters continuity and boundary accounting. `J0` and `zeta j`
are constitutive terms in that one current, not two additional coherence
resources. Postsolve `J_C` is authoritative for continuity and declared later
consequences. Explicit `j` may enter only the future declared graph-local
`zeta (j tensor j)` path and telemetry/analysis. When `zeta = 0`, diagnostic
`j` has no causal consumer.

Every admitted row is a unique exact linear inverse on its declared regular
profile. Solver seed, prior current, damping, preconditioning, and iteration
history have no constitutive authority, and numerical iteration is not a
physical clock. A future numerical realization must pass both a predeclared
condition margin and a scaled residual before atomic commit.

## Candidate A: Exact Reuse

D4-v2 and D5-v2 changed no A causal object. They did not alter A's current
space, operator, pre-read staging, gain, or support contract, and common `H_4`
has not yet entered any candidate solve. D6-v2 therefore reuses the accepted
D6 A row exactly rather than inventing an ornamental A-v2 equation.

The source candidate row has canonical SHA-256:

```text
82bea78821e721c52f9d54addb21a78dcff823e82d2b9a3cf695479c4825fa6f
```

Its closure remains:

```text
q_A,e = (W_A,e - W_hat,e) / (W_A,e + W_hat,e)

J_C,A,e = J0,A,e / (1 - zeta_A chi_A q_A,e).
```

For `0 <= zeta_A <= zeta_bar,A < 1`, the accepted uniform margin remains

```text
sigma_min(L_A) >= 1 - zeta_bar,A.
```

A remains D7-v2 eligible. Any later global metric, support, or staging change
that reaches A requires named revalidation rather than implicit reuse.

## Candidate B: Signed Riesz Closure

### Operator and exact domain

D5-v2 supplied the metric-raised endomorphism

```text
A_B = H_1,pre^-1 T_B

Theta_B = H_1,pre^-1/2 T_B H_1,pre^-1/2.
```

`A_B` is self-adjoint in the `H_1,pre` inner product. The total-current closure
is therefore

```text
J_C,B = J0,B + zeta_B chi_B A_B J_C,B

L_B = I - zeta_B chi_B A_B

J_C,B = inverse(L_B) J0,B

j_B = chi_B A_B J_C,B.
```

Let `lambda_i` be the generalized eigenvalues

```text
T_B v_i = lambda_i H_1,pre v_i.
```

The exact regularity condition is

```text
1 - zeta_B chi_B lambda_i != 0  for every i.
```

The exact metric margin is

```text
min_i |1 - zeta_B chi_B lambda_i|.
```

D4-v2 supplies `|lambda_i| <= t_B,max`. Consequently,

```text
|zeta_B| t_B,max < 1
```

is a sufficient uniform region, with

```text
sigma_min,H1pre(L_B) >= 1 - |zeta_B| t_B,max

||inverse(L_B)||_H1pre <= 1 / (1 - |zeta_B| t_B,max).
```

This capacity bound is not a necessary invertibility condition. Exact
generalized eigenvalues remain authoritative. In the selected nonnegative-gain
profile, a negative `lambda_i` does not approach a positive-gain singularity;
it increases the corresponding denominator. A positive mode is singular at
`zeta_B chi_B = 1 / lambda_i` when that point lies in the profile. Under active
read `chi_B = 1`, this reduces to `zeta_B = 1 / lambda_i`.

### Support and accounting

Unlike A's diagonal response, B's `A_B` may redistribute current between
radius-one neighbors in the line graph. The solved inverse
`(I - zeta_B chi_B A_B)^-1` need not retain that one-hop locality: repeated
couplings may transmit baseline influence throughout the connected live-edge
component. D6-v2 therefore claims component confinement, not edgewise or
one-hop support preservation. It requires that B:

```text
acts only on the declared live edge space
creates no absent edge
does not couple disconnected components
uses the solved J_C,B once in continuity
```

The carrier, metric-raised operator, closure block, and exact inverse transform
covariantly under signed edge reorientation and graph relabeling. The solved
current therefore transforms as the same physical one-cochain rather than as
an array-index artifact.

### Direct, explicit, and tensor paths

B has three separately staged relations:

```text
direct retained path:
  T_B -> kappa_B T_B -> candidate K_4,B payload
  held outside the D6-v2 solve pending D7G global H_4/h_4

explicit current path:
  T_B -> A_B -> j_B -> J_C,B

future tensor path:
  postsolve j_B -> graph-local j_B tensor j_B -> K_4
```

Their controls remain independent:

```text
chi_B = 0:
  explicit current and future tensor paths off
  direct kappa_B T_B path preserved

zeta_B = 0:
  J_C,B = J0,B
  diagnostic j_B may remain, with no causal consumer

kappa_B = 0:
  direct-path ablation only
  not an admissible positive B profile
```

`J0,B` is constructed on the frozen common `h_4,pre` current space. D4-v2
admitted the direct `K_4,B` payload but did not close its crossing through
global `H_4/h_4`; D6-v2 therefore gives that payload no same-beat baseline
effect. D7G must derive the crossing and reopen D6-v2 if the accepted global
metric changes B's pre-read current block.

### The sign discriminator is stage-specific

At a fixed probe current, or under the gain-off control,

```text
T_B -> -T_B
A_B -> -A_B
j_B -> -j_B
j_B tensor j_B -> unchanged.
```

That is the valid D5-v2 path discriminator. It separates B's sign-odd direct
linear carrier from a fixed-probe sign-even quadratic tensor.

It is not the parity of the active solved feedback loop. For active read
`chi_B = 1` and fixed `J0,B`, define

```text
j_+(T_B) = A_B (I - zeta_B A_B)^-1 J0,B

j_-(T_B) = -A_B (I + zeta_B A_B)^-1 J0,B.
```

Where both closures are regular,

```text
closed-loop odd part
  = A_B (I - zeta_B^2 A_B^2)^-1 J0,B

closed-loop even part
  = zeta_B A_B^2 (I - zeta_B^2 A_B^2)^-1 J0,B.
```

The even part is generally nonzero. Thus the active `j_B` does not simply flip
sign, and the two active `j_B tensor j_B` values are not generally equal.
D7G must assemble the tensor from the actual solved current and may not import
the fixed-probe parity as a full-loop symmetry.

This is a clarification of scope, not a rejection of the D5-v2 discriminator.

### B witness

For the accepted two-edge witness,

```text
H_1,pre = diag(2, 3)
T_B = [[0.5, 0.2], [0.2, -0.3]]
J0,B = [1, -0.5]
zeta_B = 0.5
t_B,max = 0.3
```

the generalized spectrum and closure are

```text
Spec(Theta_B) = [-0.1181105038, 0.2681105038]
Spec(L_B) = [1.0590552519, 0.8659447481]
uniform capacity margin = 0.85
exact observed margin = 0.8659447481

J_C,B = [1.1176737846, -0.4407087687]
j_B   = [0.2353475693, 0.1185824625].
```

Under `T_B -> -T_B`, the solved response is

```text
J_C,B = [0.9137055838, -0.5583756345]
j_B   = [-0.1725888325, -0.1167512690].
```

The resulting nonzero even component is

```text
[0.0313793684, 0.0009155967].
```

The witness verifies the algebra and the parity boundary. It is not runtime
evidence or an empirical acceptance margin.

## Candidate C: Similarity and Physical Conditioning

### Exact closure

D4-v2/D5-v2 supplied

```text
I = I_4M^pre = H_1,M H_1,pre^-1

R_C,M = (I + tau_C Delta_1,M)^-1

Rbar_C = I^-1 R_C,M I.
```

`I` is invertible on the selected positive fixed-rank profile, but it is not
assumed isometric. The physical closure is

```text
J_C,C = J0,C + zeta_C chi_C Rbar_C J_C,C

Lbar_C = I - zeta_C chi_C Rbar_C.
```

Define the retained-space block

```text
L_C,M = I - zeta_C chi_C R_C,M.
```

Then

```text
Lbar_C = I^-1 L_C,M I

inverse(Lbar_C) = I^-1 inverse(L_C,M) I.
```

Exact invertibility is therefore similarity-invariant. It does not require an
isometric identification. If

```text
r_i = 1 / (1 + tau_C nu_i),
```

then exact regularity requires

```text
1 - zeta_C chi_C r_i != 0  for every i.
```

For `tau_C > 0` and `0 <= zeta_C <= zeta_bar,C < 1`,

```text
sigma_min,H1M(L_C,M) >= 1 - zeta_bar,C.
```

Harmonic modes retain `r_i = 1`; `zeta_C chi_C = 1` is therefore singular on
that sector. Under active read `chi_C = 1`, this reduces to `zeta_C = 1`, and
increasing `tau_C` cannot regularize it.

### Exact is not the same as robust

Similarity preserves eigenvalues and exact invertibility. It does not preserve
physical singular values under a non-isometric map.

Define the cross-metric identification condition

```text
kappa_4M^pre
  = ||I||_(H1pre -> H1M) ||I^-1||_(H1M -> H1pre).
```

For a preregistered finite bound `kappa_4M^pre <= kappa_bar,C`,

```text
||inverse(Lbar_C)||_H1pre
  <= kappa_bar,C / (1 - zeta_bar,C)

sigma_min,H1pre(Lbar_C)
  >= (1 - zeta_bar,C) / kappa_bar,C.
```

Thus C has two separate admission statements:

```text
exact branch regularity:
  inherited through similarity whenever I is invertible

robust physical conditioning:
  requires a finite declared cross-metric condition bound
```

An exactly invertible but arbitrarily ill-conditioned row fails the robust
profile. D6-v2 does not call retained-space contraction physical-space
contraction.

### C path factorization

C retains three separate stages:

```text
direct baseline:
  T_C -> H_M -> pre-read h_M-conditioned J0,C

explicit read:
  T_C -> H_M -> R_C,M -> Rbar_C -> j_C,phys

future tensor:
  postsolve j_C,phys -> graph-local j_C,phys tensor j_C,phys -> K_4
```

The fixed selector, `H_M`, `I_4M^pre`, and `J0,C` are prepared before the
current solve. Present `J_C` cannot alter them inside D6-v2. If that order is
changed, the reduced similarity block is incomplete and D6-v2 must reopen.

The switch meanings are:

```text
kappa_M,C = 0:
  remove T_C conditioning from H_M, J0,C, Rbar_C, and I
  a reference Hodge response may remain

chi_C = 0:
  remove explicit j_C and its current contribution
  preserve T_C-conditioned J0,C

zeta_C = 0:
  J_C,C = J0,C
  diagnostic j_C has no causal consumer
```

Raw retained-coordinate arrays cannot enter physical continuity or common
`K_4`; the inverse identification is required. The nonlocal response may
redistribute current inside a positive-mobility connected component, but it
cannot reopen a closed or absent edge or couple disconnected components.
The identification, retained response, physical closure, and exact inverse all
transform consistently under signed edge and graph relabeling.

### C witness

The selected three-node path witness uses:

```text
C_selected = [1.2, 1.0, 0.8]
kappa_M,C = 0.5
tau_C = 0.25
zeta_C = 0.5
H_1,pre = I.
```

It gives:

```text
diag(H_1,M) = [1.4900537464, 1.4281897476]
Spec(R_C,M) = [0.4774210572, 0.7328505884]

cond_2(I) = 1.0433163723
cross-metric kappa(I) = 1.0656731751

Spec(L_C,M) = [0.7612894714, 0.6335747058]
physical singular values(Lbar_C)
  = [0.7614302828, 0.6334575387]

declared cross-metric lower bound = 0.46918699999.
```

For `J0,C = [1, -0.4]`,

```text
J_C,C = [1.3906950457, -0.4396646248]
j_C   = [0.7813900914, -0.0793292497]

closure residual = 5.55e-17
similarity error = 0
inverse-similarity error = 2.22e-16.
```

This checks exact similarity, conditioning separation, and the solve residual.
It does not supply runtime formation, persistence, or empirical mediation.

## Slaving, Singularity, and Failure

All three initial candidates use regular algebraic same-beat slaving. No
independent current coordinate is added.

This means only that current is a unique function of the frozen pre-read
package on the admitted domain. It does not establish a normally attracting
fast sector, current persistence, temporal stability, or a complete reflexive
loop.

Loss of the declared regularity or physical conditioning margin fails closed.
It does not authorize:

```text
pseudoinverse
mode deletion
gain clipping
epsilon regularization
stale-current reuse
automatic current temporalization
spark or topology-event relabeling
```

Failure is atomic: no current, retained state, geometry, or observable is
partially committed.

## Controls and Pressure

D6-v2 consumes 67 unchanged D6 controls by exact D6 record digest, supersedes
five controls whose B/C premises changed, and adds 40 changed-lane controls.
The active control surface therefore contains 107 controls.

The accepted D6 pressure audit contributes 90 unchanged rows. Six B/C rows are
superseded, and D6-v2 adds 40 explicit rows, for 130 active pressure rows.

The new pressure surface covers:

```text
A unchanged-object proof
B generalized-spectrum regularity and capacity bounds
B fixed-probe versus closed-loop parity
B direct/read/tensor path separation
C exact similarity versus physical conditioning
C non-isometric backmap and harmonic boundary
candidate-local support and resource accounting
pre-read stage closure and no geometry re-entry
atomic failure and non-relabels
complete debt preservation
```

All new controls fail closed. No runtime or prototype probe was executed.

## Debt Lifecycle

D6-v2 dispositions all 19 current D5-v2 debts. Fifteen unchanged obligations
are copied into the current ledger as exact D5-v2 rows, including their IDs,
wording, status fields, blocker flags, and resolution gates. The remaining four
predecessor obligations are explicitly superseded or narrowed into seven
D6-v2 debts; none disappears. D6-v2 also preserves the exact two immediate and
20 transitive rows carried through D5-v2 by predecessor digest, file hash, row
ID, status, and blocker flag. Absence from the current debt array is not
resolution.

The current ledger contains 22 typed debts. Together with the 22 inherited
rows, the complete live union is 44 rows.

D6-v2 closes:

```text
B total-current regularity on the selected H_1,pre profile
C exact similarity closure and bounded physical conditioning on the selected profile
candidate-local current gain and support semantics
```

It leaves explicit:

```text
D7-v2:
  B and C writers, lifecycle-local staging, and complete transitions

D7G:
  B direct/read/tensor composition
  common K_4 normalization
  global H_4/h_4
  B capacity and C identification-condition revalidation

D8/D9:
  comparative spectra, absorbability, selector/topology boundaries,
  reduction, reset, serialization, and event lifecycle

post-spec:
  runtime reachability and physical channel attribution
```

## D7-v2 Handoff

After human acceptance, D7-v2 receives:

```text
A:
  unchanged accepted algebraic current closure
  accepted A recurrence remains to be integrated comparatively

B:
  exact signed generalized-eigenvalue closure
  bounded H_1,pre inverse domain
  solved authoritative J_C,B
  explicit j_B with mixed active-loop sign parity
  direct and future tensor paths still separate

C:
  exact similarity-invariant closure
  finite cross-metric robust physical bound
  solved authoritative physical J_C,C
  retained-mediated explicit j_C
  fixed-selector and non-isometric identification boundaries
```

D7-v2 must write or close each candidate's complete cross-beat transition. It
may not treat this same-beat current solve as write-back or global structural
closure.

## Claim Boundary

D6-v2 supports only:

```text
three candidate-specific bounded regular algebraic total-current closures
exact A unchanged-object reuse
exact B signed-spectrum regularity with a sufficient capacity envelope
exact C similarity regularity with a separate robust physical condition bound
explicit support, stage, path, and failure semantics
```

It does not support:

```text
runtime implementation or reachability
independent temporal current persistence
write-back or a complete cross-beat loop
temporal or structural stability
global H_4 or structural cultivation
physical nonabsorbability of any explicit Read-Back channel
candidate ranking or architecture selection
normative GRC9V4 specification
```

D7-v2 is authorized but not started. D7G and later gates remain blocked.

Decision digest:
`ad02150010c4759d1c0ac4ba079c81cff99bad1f35b715f52b980aaf404eac0a`.

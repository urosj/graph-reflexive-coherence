# D5-v2 Candidate-Specific Directional Read-Back Completion

Status: `accepted_bounded`.

Record: `GRC9V4-CD-D5V2-v1`.

## Gate Question

D4-v2 admitted two causal objects that did not exist at accepted D5-v1:

```text
B:
  a bounded graph-local symmetric bilinear carrier T_B
  on the physical pre-read one-form space

C:
  a retained-sector-conditioned Hodge package H_M
  plus the canonical non-isometric identification I_4M^pre
```

D5-v2 asks whether each object can condition a typed directional response to
present current without borrowing another candidate's equations, adding hidden
state, or pretending that an operator definition is already a closed runtime
loop.

The answer is bounded and positive for both candidates:

```text
A = accepted D5 operator carried unchanged
B = bounded Riesz Read-Back operator admitted
C = retained-mediated physical Hodge Read-Back operator admitted
```

No candidate is selected or ranked.

## Theory Boundary

The controlling Read-Back reconstruction requires:

```text
retained organization
  + present current
  -> directional response

present current = 0
  -> read-back current = 0
```

It also states that the exact nonlinear closure is open. A Hodge-spectral
one-form response is a canonical candidate, not a unique theorem.

D5-v2 uses that boundary in two different ways.

Candidate B is an explicitly admitted revision-level extension. Its independent
nonresource carrier is not part of the coherence-only core ontology. D5-v2 may
therefore complete a constrained V4 response for B, but may not call it an
inherited core relation.

Candidate C remains coherence-only. Its retained sector is a deterministic
projection of `C`, and its Hodge package is derived from that sector. C may
therefore close a retained-conditioned operator without adding a second state,
provided the complete `T_C -> H_M -> response` attribution is shown.

## Candidate A

Candidate A is not rewritten.

Its accepted operator remains:

```text
q_A = (W_A - W_hat) / (W_A + W_hat)
R_A = chi_A Diag(q_A)
j_A = R_A J_trial
```

The causal object did not change in D4-v2. D6-v2 may reuse accepted A closure
only after recording an explicit unchanged-causal-object proof. No ornamental
`A-v2` formula is introduced to make the rows look symmetric.

## Candidate B

### Why a bilinear carrier is not yet an operator

`T_B` is a symmetric bilinear form with the same units as the pre-read edge
Hodge star `H_1,pre`. Raw matrix multiplication by `T_B` would silently confuse
a bilinear form with a dimensionless endomorphism.

The metric supplies the canonical conversion. Define `A_B` by the Riesz
relation:

```text
<u, A_B v>_H1pre = T_B(u, v)
```

Therefore:

```text
A_B = H_1,pre^-1 T_B
```

and, in orthonormal coordinates,

```text
Theta_B = H_1,pre^-1/2 T_B H_1,pre^-1/2

A_B = H_1,pre^-1/2 Theta_B H_1,pre^1/2
```

D5-v2 selects:

```text
R_B = chi_B A_B
j_B = chi_B H_1,pre^-1 T_B J_trial
```

This selection is canonical once the D4-v2 bilinear carrier and metric are
accepted. It is still a revision-specific V4 completion because core theory did
not uniquely choose Candidate B or require an independent carrier.

### Properties

The response is:

- dimensionally correct;
- graph- and signed-edge-covariant;
- self-adjoint in the `H_1,pre` inner product;
- bounded by the admitted `Theta_B` capacity;
- odd in present physical current;
- zero when `J_trial = 0`;
- zero when `T_B = 0`;
- compatibility-selective, because a nonzero carrier change in the probe's
  null direction need not change `j_B`.

Positivity is not imposed. D4-v2 admitted a signed generalized spectrum, so B
may support or inhibit different current modes. That sign does not establish
continuation hardening, softening, temporal stability, or global structural
effect.

### Family pressure

The selected Riesz map is narrower than the alternatives:

| Family | Disposition | Reason |
|---|---|---|
| raw `T_B J` | rejected | metric raising and units are missing |
| raw `Theta_B J` | rejected | orthonormal and physical coordinates are conflated |
| `I + A_B` | not selected | leaves ordinary identity response at neutral B |
| scalar trace/norm response | not selected | erases route relations and directional compatibility |
| nonlinear spectral function | admissible successor | adds an unnecessary response-shape parameter |
| `H_1,pre^-1 T_B` | selected | canonical metric-raised use of the admitted carrier |

### Direct and current-mediated structural paths

B now has two distinct possible structural relations:

```text
direct retained path:
  T_B -> kappa_B T_B -> K_4^B

current-mediated path:
  T_B -> R_B -> j_B
      -> later graph-local j_B tensor j_B -> K_4
```

Only the first path was admitted by D4-v2. The second is now typed but remains
pending D6-v2 current closure and D7G local tensor assembly.

The controls keep them distinct:

```text
chi_B = 0:
  explicit j_B off
  direct kappa_B T_B path preserved

kappa_B = 0:
  direct T_B structural path off
  R_B and diagnostic j_B preserved

zeta_B = 0:
  diagnostic j_B preserved
  j_B has no total-current or current-tensor consequence
```

Neither path is evidence for the other. A future common structural sum must
retain separate switches, units, and attribution.

The `kappa_B = 0` row is an algebraic path-ablation control, not an admissible
positive B profile. D4-v2 still requires finite preregistered nonzero `kappa_B`
for the candidate itself.

### Algebraic witness

On a two-edge path, use:

```text
H_1,pre = diag(2, 3)
T_B = [[0.5, 0.2], [0.2, -0.3]]
J_trial = [1, -0.5]
chi_B = 1
t_B,max = 0.3
```

Then:

```text
Spec(Theta_B) = [-0.1181105038, 0.2681105038]
j_B = [0.2, 0.1166666667]
```

The observed operator norm is below the declared `t_B,max` capacity.

Reorienting only the second edge produces:

```text
j_B' = [0.2, -0.1166666667]
```

with zero covariance error. This is a deterministic typing and existence
witness. It is not runtime formation, reachability, persistence, or empirical
mediation evidence.

## Candidate C

### The earlier gap

D5-v1 admitted a parameterized Hodge response:

```text
R_C,M = chi_C (I + tau_C Delta_1,M)^-1
```

but did not have a completed causal map from `T_C` to `H_M`. The response was
therefore typed as a family indexed by an external regular `h_M`; it did not
yet prove retained-sector mediation.

D4-v2 supplied:

```text
T_C -> H_M(T_C) -> (H_0,M, H_1,M)
```

and the canonical identification:

```text
I_4M^pre = H_1,M H_1,pre^-1
```

D5-v2 retains the accepted Hodge family and closes its physical representation:

```text
Delta_1,M = B^T H_0,M^-1 B H_1,M

R_C,M = chi_C (I + tau_C Delta_1,M)^-1

Rbar_C = (I_4M^pre)^-1 R_C,M I_4M^pre

j_C,phys = Rbar_C J_trial,phys
```

Raw `h_M` coordinate arrays never become physical current merely because the
edge dimensions match.

### Norm boundary

In retained geometry, `R_C,M` is positive, `H_1,M`-self-adjoint, and
contracting for positive `tau_C`.

The physical operator `Rbar_C` is similar to `R_C,M`, so it has the same
spectrum. But `I_4M^pre` is not assumed isometric. D5-v2 therefore does not
promote retained-space self-adjointness or contraction into the `H_1,pre`
physical norm. That bound must be rebuilt in D6-v2.

### On-manifold retained mediation

On the fixed-selector smooth stratum, take a resource-preserving retained
tangent:

```text
delta_C,M in Ran(P_M^Delta)
delta_T_C = P_M^Delta delta_C,M
```

For the D4-v2 edge profile:

```text
delta r_C,e = 1/2 sum_endpoints(
  sech^2(T_C / C_ref) delta_T_C / C_ref
)

delta H_1,M,e = kappa_M,C delta r_C,e H_1,M,e
```

The Hodge response changes by:

```text
delta R_C,M = -tau_C R_C,M (delta Delta_1,M) R_C,M

delta Delta_1,M = B^T H_0,pre^-1 B delta H_1,M
```

The physical derivative also includes both identification derivatives:

```text
delta Rbar_C =
  delta(I^-1) R I
  + I^-1 delta(R) I
  + I^-1 R delta(I)
```

Dropping those terms would silently restore the isometry assumption rejected by
D4-v2.

### Selected-content and complement witness

Use a three-node path with identity pre-read Hodge stars. The selector contains
the constant mode and first nonconstant path mode. Compare equal-resource,
positive states:

```text
C_base     = [1.0, 1.0, 1.0]
C_selected = [1.2, 1.0, 0.8]
C_complement = [1.1, 0.8, 1.1]
```

The selected variation lies in `Ran(P_M^Delta)`. The complement variation lies
in its kernel, so its projected `T_C` remains `[1, 1, 1]`.

With:

```text
C_ref = 1
kappa_M,C = 0.5
tau_C = 0.25
chi_C = 1
J_trial,phys = [1, -0.4]
```

the physical outputs are:

```text
j_base     = [0.5533580485, -0.1140752267]
j_selected = [0.5518299666, -0.1082388352]

||j_selected - j_base||_2 = 0.0060331169
```

The matched complement produces exactly zero output difference. Setting
`kappa_M,C = 0` also removes the selected-content difference. Setting
`tau_C = 0` reduces the composite response to the identity up to floating-point
roundoff and removes retained selectivity.

The numeric difference is not an empirical margin or acceptance threshold. Its
role is to prove that the declared constitutive chain has at least one lawful
load-bearing retained tangent while rejecting the matched complement.

This is an existential compatible-probe requirement, not a universal one.
Read-Back remains compatibility-selective: a lawful retained change may lie in
the null direction of a particular probe and leave that output unchanged. C is
blocked only if no preregistered compatible probe changes under any lawful
selected-content variation, not because one null-direction control remains
unchanged.

### Switch semantics

The three C switches remain distinct:

```text
kappa_M,C = 0:
  removes T_C conditioning from H_M, I_4M^pre, R_C,M, and J_0,C
  may leave a reference Hodge response

chi_C = 0:
  removes explicit R_C,M and j_C
  preserves T_C-conditioned H_M -> J_0,C

zeta_C = 0:
  preserves diagnostic j_C and H_M -> J_0,C
  blocks j_C from total current and later current-tensor K_4
```

The residual response at `kappa_M,C = 0` is not evidence for retention. The
retention-specific evidence is the matched response difference generated by
the `T_C -> H_M` path.

## Evidence Classification

D5-v2 supports:

```text
A:
  unchanged bounded operator-level retained mediation

B:
  bounded revision-specific Riesz Read-Back operator
  operator-level retained mediation

C:
  bounded revision-specific retained-mediated Hodge Read-Back operator
  on the declared fixed-rank smooth selector stratum
```

It does not support:

- a solved total-current recurrence;
- physical nonabsorbability or empirical channel identification;
- B or C write-back and release;
- complete candidate transitions;
- common `H_4` or physical `h_4`;
- continuation hardening, temporal retention, stability, or basin formation;
- runtime reachability or numerical implementation;
- unique core-theory status for any selected formula;
- candidate ranking or GRC9V4 architecture selection.

## Debt And Lineage

The record dispositions all 16 current chronological D4-v2 debts and all 27
debts from the superseded D5-v1 gate. It also rebinds, by exact ID, status,
blocker flag, accepted D4-v2 digest, and authoritative D7 source SHA, the 2
independently carried immediate rows and 20 transitive rows that D4-v2 kept
live outside its `open_debt` array. Counts alone are not an admissible handoff.

The complete live union is therefore:

```text
19 current D5-v2 typed debts
+ 2 independently carried immediate rows
+ 20 transitive rows
= 41 live debt rows
```

B's missing operator debt is closed at the constitutive-operator level. C's
missing `H_M` and lawful-counterfactual debts are closed at that same level.
The old D7 D8-analysis and current-singular-successor debts are explicitly
superseded by widened D5-v2 IDs rather than being rhetorically carried while
absent from the current debt array.

The unresolved work is explicit:

```text
D6-v2:
  B and C gains, support, conservation, regular current closure,
  C physical-space norm, and direct/read path factorization

D7-v2:
  B and C writers and complete candidate-local transitions

D7G:
  local tensor normalization, common K_4 sum, H_4, h_4,
  and metric-relative capacity readmission

D8/D9:
  comparative spectra, selector and topology boundaries,
  lifecycle, reduction, and event semantics

post-spec:
  runtime reachability and physical channel attribution
```

## Next Gate

D5-v2 is accepted bounded and D6-v2 is authorized but not started. D6-v2 must
rebuild the effective current closure for B and C. It must also record why A's
accepted D6 object remains unchanged before reusing it.

In particular, D6-v2 must not infer physical regularity for C from retained-space
contraction, and must not combine B's direct `T_B -> K_4` relation with its
new current-mediated route without independent gains and controls.

The exact handoff is sharper than a generic small-gain audit:

```text
B:
  singularity is classified by 1 - zeta_B lambda_i(A_B) = 0
  |zeta_B| t_B,max < 1 is a sufficient uniform regularity region

  T_B -> -T_B:
    direct kappa_B T_B path changes sign
    j_B changes sign
    j_B tensor j_B does not

C:
  I - zeta_C Rbar_C
    = inverse(I_4M^pre) (I - zeta_C R_C,M) I_4M^pre

  exact invertibility transfers through similarity
  physical conditioning may still worsen with cond(I_4M^pre)
```

D6-v2 must keep exact regularity distinct from robust conditioning and preserve
the direct-`J_0`, explicit-`j`, and future-current-tensor stages without
same-beat geometry re-entry.

Decision digest:
`212c7db173fbe286816965070a4beebd1e5ba8e39ccc3ffb73bbecde8410cf1c`.

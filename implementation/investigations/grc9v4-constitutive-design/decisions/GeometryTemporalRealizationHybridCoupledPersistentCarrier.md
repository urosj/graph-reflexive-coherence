# GRC9V4 Coupled-Implicit Plus Persistent-Carrier Pressure

**Gate:** `GTRS-CI-PC`  
**Record:** `GRC9V4-GTRS-CI-PC-v1`  
**Status:** `accepted_bounded`  
**Decision digest:** `5f003ff5f4dbbb60788ac50827b5a3ccff7ff7e194173721f15503bc6024682a`

## Purpose

COMP established that geometry/current timing and independent history authority
are analytically separable, but did not assume they compose. It identified one
pair whose missing capability combination was material enough to pressure before
D9:

```text
coupled-implicit same-beat closure
+
persistent K_4 history
```

GTRS-CI-PC pressures only that pair for Candidates A and C. It is not a reopened
family search and does not investigate OS+PC or RG+PC.

## Primary Hybrid

The complete state is:

```text
A: (C_k, W_A,k, Z_4,A,k)
C: (C_k, Z_4,C,k), with T_C derived
```

The joint unknown remains:

```text
Y_a = (J_a, h_a)
```

The primary profile freezes a dimensionless composition switch:

```text
rho_inst = 1   primary hybrid
rho_inst = 0   PC ablation
```

`rho_inst` is profile metadata, not runtime state and not a tunable post-result
coefficient.

The common geometry equation is:

```text
F_h,a = h_a
        - H_profile(
            K_4,base
            + Z_4,a,k
            + rho_inst,a Delta_K_4,a(J_a,h_a)
          )
        = 0
```

`F_J,a = 0` is the accepted candidate-specific CI current equation evaluated at
the same trial geometry. After a valid root, the carrier writer is:

```text
Z_4,a,k+1
  = a_PC,a,k Z_4,a,k
    + (1-a_PC,a,k) Delta_K_4,a(J_a,h_a)

a_PC,a,k = exp(-Delta_t_k / tau_PC,a)
```

New `Z_4,k+1` is never read in the same beat.

## Why The Sum Is Not Automatic Double Counting

The two terms have different temporal authority:

```text
Z_4,k:
  prior committed structural history

rho_inst Delta_K_4(J,h):
  source-current same-beat structural increment
```

The current increment has two declared temporal consequences:

1. it contributes to the current beat's joint geometry through `rho_inst`;
2. after a valid root, it contributes to future beats through the carrier
   writer.

That is the capability the hybrid is meant to test. It is not two same-beat
writes to one authority.

The gain audit is exact:

```text
chi_a:
  once inside the accepted j_flat path

zeta_a:
  already once inside Delta_K_4,a

rho_inst,a:
  once on the immediate profile source only

kappa_H:
  once when H_profile consumes the total K_4 argument

a_PC,a:
  once in the post-root carrier writer
```

The writer does not reapply `rho_inst` or `zeta`. No clipping, normalization, or
post-hoc attenuation is introduced.

This authority separation is not amplitude neutrality. Under a constant source
`S` and `0 < a_PC < 1`, the carrier converges to `Z_k -> S`, so:

```text
K_eff -> K_4,base + (1 + rho_inst) S
```

For the preregistered `rho_inst=1` profile, the steady structural argument is
`K_4,base + 2S`. The hybrid is a parallel fast plus slow response with unit gain
on each path. It is not amplitude-equivalent to CI or PC, and later comparison
must not attribute the whole difference to persistence alone.

A general profile can expose both gains as:

```text
K_eff = K_4,base + g_H Z + g_I S
```

The current result is `(g_H,g_I)=(1,1)`. A normalized comparison such as
`(1-theta)Z + theta S`, with `0 < theta < 1`, may be considered at D10 if
like-for-like steady amplitude becomes necessary. It is not a replacement for
the preregistered row and is not accepted here.

## Composite Domain

PC previously admitted the separate bounds:

```text
Z_4 in B_R
Delta_K_4 in B_R
```

The hybrid root must admit their sum and prove, rather than assume, that its
same-root source remains inside `B_R`. Define:

```text
Y_a(X,Z;kappa_H) = (J_a,h_a)

M_a,0
  = sup_(X in K_X,a)
      ||S_a(J_a,ref(X),h_ref)||_K
```

At `kappa_H=0`, `h=h_ref`, so the reference source is independent of `Z`.
Choose `R_a` with strict source slack:

```text
M_a,0 <= R_a - delta_a
delta_a > 0
```

For the hybrid roots define:

```text
m_a^H(R_a,kappa_H)
  = sup_(X in K_X,a, Z in B_R,a)
      ||S_a(Y_a(X,Z;kappa_H))||_K
```

Uniform continuity of the root and source maps on the compact chart gives
`epsilon_S,a > 0` such that:

```text
|kappa_H| < epsilon_S,a
  implies m_a^H(R_a,kappa_H) <= R_a
```

The source-ball condition is therefore an output of the local theorem, not part
of the root chart's definition. For fixed `rho_inst`:

```text
||Z_4 + rho_inst Delta_K_4||_K
  <= (1 + |rho_inst|) R
```

The primary `rho_inst=1` profile therefore requires:

```text
H_profile(K_4,base + B_2R) subset H_adm
```

and uniform candidate current regularity over the resulting geometry domain.
The old PC `B_R` profile condition alone is insufficient.

The resulting closed implication is:

```text
Z_4,k in B_R
  -> same-root S_k in B_R
  -> Z_4,k+1 in B_R
```

The last step follows because the writer is a convex combination of old `Z_4`
and the now-proved same-root source bound.

## Local Root Theorem

Treat `Z_4` as committed input, not as a joint-root unknown. At:

```text
kappa_H = 0
h = h_ref
```

for every admitted `Z_4` and source, the joint derivative has the accepted
triangular reference form:

```text
[[L_a, B_a],
 [  0,   I]]
```

`L_a` is the accepted A or C current block. It is invertible on the source
candidate charts. On a compact candidate chart and carrier ball satisfying
strict reference source slack plus the `B_2R` profile and current-domain
conditions, continuity and the implicit function theorem give a nonzero uniform
small-`|kappa_H|` envelope with a unique local `C1` joint root. Shrinking that
envelope to the source-continuity radius proves the same-root source lies in
`B_R`.

This is a constructive parametric theorem. It does not instantiate numeric
`R`, source bounds, singular margins, conditioning, or a global root domain.

## Both Paths Are Root-Level Load-Bearing

Write the hybrid residual as:

```text
F_H,a(Y;X,Z,rho_inst) = 0
Y = (J,h)
B_H,a = D_Y F_H,a
```

On the regular enabled root domain, `B_H,a` is invertible. Since retained `Z`
enters only through the geometry equation:

```text
D_Z F_H,a[delta Z]
  = (0, -D_K H_profile[delta Z])

D_Z Y_a[delta Z]
  = B_H,a^-1 (0, D_K H_profile[delta Z])
```

For the immediate-path coefficient:

```text
D_rho F_H,a
  = (0, -D_K H_profile[S_a])

D_rho Y_a
  = B_H,a^-1 (0, D_K H_profile[S_a])
```

For the enabled affine profile, `D_K H_profile = kappa_H I`. Therefore:

```text
kappa_H != 0 and delta Z != 0
  -> D_Z Y_a[delta Z] != 0

kappa_H != 0 and S_a != 0
  -> D_rho Y_a != 0
```

Both historical and instantaneous paths are analytically nonannihilated at the
joint-root pair. This does not yet prove a nonzero committed `C`/`W` endpoint
difference; that complete-chain obligation remains open.

## Candidate A

Candidate A uses:

```text
F_J,A
  = J_A
    - J0_A,CI(C_k,W_A,k,h_A)
    - zeta_A j_A(J_A,h_A)
  = 0

F_h,A
  = h_A
    - H_profile(
        K_4,base + Z_4,A,k
        + rho_inst,A Delta_K_4,A(J_A,h_A)
      )
  = 0
```

Every residual evaluation refreshes the full accepted chain:

```text
h
-> Delta_0
-> Phi_A,CI
-> J0_A,CI
-> W_hat_A
-> q_A
-> j_A
-> Delta_K_4,A
```

`W_A` remains the only mobility authority. After continuity, all differential
surfaces consumed by the accepted D7 `W_A` writer are rebuilt from `C_k+1`.
The final atomic commit is:

```text
(C_k+1, W_A,k+1, Z_4,A,k+1)
```

Disposition:

```text
A_CI_PC = bounded_complete_hybrid_realization
```

## Candidate C

Candidate C uses:

```text
F_J,C
  = J_C
    - J0_C(C_k,T_C(h_C),h_C)
    - zeta_C j_C(J_C,h_C)
  = 0

F_h,C
  = h_C
    - H_profile(
        K_4,base + Z_4,C,k
        + rho_inst,C Delta_K_4,C(J_C,h_C)
      )
  = 0
```

Every residual evaluation refreshes:

```text
h
-> P_M
-> T_C
-> H_M
-> I_4M
-> Rhat_C,M
-> G_J
-> j_C
-> Delta_K_4,C
```

`T_C` remains derived and is never serialized. The atomic commit is:

```text
(C_k+1, Z_4,C,k+1)
```

Poststate `T_C` is rederived when requested.

Disposition:

```text
C_CI_PC = bounded_complete_hybrid_realization
```

## Exact Ablations

The profile has exact family boundaries:

```text
rho_inst = 0, PC enabled:
  accepted PC realization

PC disabled, Z_4 = 0, rho_inst = 1:
  accepted CI realization

rho_inst = 0, PC disabled, Z_4 = 0:
  accepted fixed-reference-geometry candidate transition
```

Other controls preserve history correctly:

```text
chi = 0 or zeta = 0:
  no new source;
  retained Z_4 remains explicit and decays through the carrier writer

kappa_H = 0:
  geometry is reference and Z_4 is causally inert;
  exact state reduction still requires PC disablement or explicit migration
```

Turning off current read-back is not permission to erase past state. A disabled
PC profile with nonzero `Z_4` fails closed unless an explicit migration handles
the carrier.

## Atomicity And Lifecycle

The step order is:

```text
validate
-> joint (J,h) root
-> retain same-root Delta_K_4
-> continuity
-> candidate poststate writer/derivation
-> carrier writer
-> validate
-> one atomic commit
```

Any domain loss, singular or underconditioned root block, failed residual,
nonfinite value, continuity failure, candidate-writer failure, or carrier-writer
failure commits nothing.

The hybrid snapshot and restoration identity include:

```text
candidate state
current Z_4
reset-baseline Z_4
graph and K_4 representation identity
CI+PC profile identity
rho_inst
tau_PC
enabled status
```

`reset()` returns to the construction baseline. `set_state()` does not rebase
that baseline unless explicitly requested. Duplicate state has no shared mutable
carrier.

Migrations remain explicit:

```text
CI -> hybrid:
  Z_4 = 0; no prior history reconstructed

PC -> hybrid:
  preserve compatible Z_4; enable rho_inst=1;
  re-admit because same-beat geometry changes

hybrid -> CI:
  archive/drop Z_4 explicitly; not native release

hybrid -> PC:
  rho_inst=0; preserve compatible Z_4;
  record changed timing semantics
```

Legacy snapshots are never silently relabelled as hybrid snapshots.

## Context And Events

Representation-preserving context changes retain `Z_4`, refresh every derived
surface, and solve the new declared root. Same-space nonsmooth changes require a
deterministic admitted map and terminate classical derivative claims.

Carrier-space-changing topology, reindexing, split, merge, birth, or death
requires typed `L_event^K4` plus a newly admitted joint-root chart. Otherwise the
step aborts before mutation. Event termination is not carrier transport.

## Result Boundary

The result supports local composability for the named pair:

```text
A_CI_PC = bounded_complete_hybrid_realization
C_CI_PC = bounded_complete_hybrid_realization
```

It does not establish universal timing/history composability. The other hybrid
statuses remain:

```text
OS+PC = unpressured; reactivate for solver-cost/failure/latency selection
RG+PC = unpressured; reactivate for state-conditioned lagged-geometry selection
```

No candidate or architecture is selected.

## Debt And Disposition

All 43 predecessor live debts are dispositioned:

```text
42 carried
1 resolved: GTRS-COMP-DEBT-CI-PC-HYBRID-PAIR
```

Five current debts remain:

```text
A quantitative composite envelope
C quantitative composite envelope
hybrid complete-chain and architecture-local analysis
D9 hybrid lifecycle integration
normative composition-profile status
```

The composition-profile debt records that the primary unit-plus-unit profile
has steady-source structural gain two and is not amplitude-equivalent to CI or
PC. It must be classified at D10 entry before candidate selection or
specification authorization. A normalized two-gain profile remains a possible
comparison, not current evidence.

The live union is `42 + 5 = 47`.

Machine disposition:

```text
status = accepted_bounded
candidate_A = bounded_complete_hybrid_realization
candidate_C = bounded_complete_hybrid_realization
local_CI_PC_composability_supported = true
universal_timing_history_composability_supported = false
controls = 93
predecessor_live_debts = 43
predecessor_debts_dispositioned = 43
current_debts = 5
live_debt_union = 47
human_acceptance_recorded = true
D9_ready_after_human_acceptance = true
D9_authorized = true
D10_authorized = false
runtime_or_src_changed = false
```

Human acceptance is recorded and authorizes D9. It does not authorize D10,
specification writing, implementation, or runtime/source changes.

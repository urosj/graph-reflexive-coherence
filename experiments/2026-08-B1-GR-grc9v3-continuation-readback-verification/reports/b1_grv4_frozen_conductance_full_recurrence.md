# B1-GR GRV4 Frozen-Conductance Versus Full Recurrence

## Result

```text
gate = GRV4
mechanical_status = passed
scientific_acceptance = awaiting_human_review
branches_audited = 48
standalone_frozen_comparators = 48
primary_full_map_comparisons = 32
full_map_comparisons_blocked_by_GRV3 = 16
primary_no_resolved_difference_within_uncertainty_count = 32
primary_resolved_bounded_difference_count = 0
primary_equivalence_supported = false
verified_strong_disagreement_count = 0
runtime_sign_classification = P_G_increases_and_negative_P_G_decreases_weakly_over_tested_discrete_sweep
GRV_C4_candidate = true
continuation = unsupported
retention = unsupported
readback = unsupported
writeback = unsupported
runtime_change_authorized = false
```

GRV4 constructs an experiment-local whole-beat fixed-conductance clamp. It does
not alter `GRC9V3.step()` and does not treat the comparator as native runtime
state, algebraic elimination, or fast-slaved reduction. The runtime sign follows
directly from the implemented equations:
`Phi = gradient(P_G)`, `J = -eta W grad(Phi)`, and continuity therefore
gives `dC/dt = eta L_W gradient(P_G)`. Thus `P_G` is weakly
nondecreasing in the semidiscrete fixed-`W` reduction and `-P_G` is weakly
nonincreasing. Stationary rows count as equality, not strict increase.

## Discrete And Runtime-Stage Audit

The preregistered amplitude/timestep matrix contains 3072 rows.
The maximum staged-runtime versus explicit-map error is `2.10942e-15`.
The minimum finite-step functional delta is `-6.39488e-15`.
The audit calls the existing potential, flux, and continuity stages while
holding the accepted branch conductance fixed; it excludes conductance
reconstruction and every semantic/topology stage by declaration.
Canonical zero-sum, structural-eigenvector, and deterministic mixed directions
are probed in both signs. Positivity remains preserved and budget projection,
clipping, and boundary stages are absent from every comparator row.

## Functional, Structural, And Temporal Separation

`H_P` is checked against the finite-difference derivative of the runtime
potential. The restoring comparator is recorded separately as `H_cont=-H_P`.
Maximum absolute tangent-Hessian error is `9.28939e-10`; near-zero rows use the preregistered absolute gate.
Maximum directional functional error is `7.07858e-09` and maximum site `V''` error is `1.30751e-09`.
Structural curvature, semidiscrete relaxation `A_W H_cont`, and discrete
multipliers `I-dt A_W H_cont` are classified separately. The mobility/Hessian
commutator relative norm is at most `8.64296e-17` in this envelope.
The self-adjoint modes and projectors are mapped back through the declared
mobility square-root relation before physical `C` comparison; maximum mapped
projector idempotence error is `5.60635e-16`.

## Branch, Conductance, And Fixed-Point Controls

Every row consumes authoritative `base_conductance` from its accepted branch
snapshot and verifies exact duplicate port-edge consistency. All 48 weighted
graphs are connected and have positive-definite mobility on the GRV3 zero-sum
tangent. Maximum exact frozen-map fixed-point residual is `1.11609e-11`.

## Frozen/Full Boundary

All 48 accepted branches receive a frozen structural comparator. Only the
32 branches with a GRV3-admitted `C` transition matrix receive the primary
full-recurrence comparison. The 16 exact-zero-current boundary branches are
retained as blocked comparisons rather than silently removed. `C-W` is a
secondary diagnostic of evolving-conductance recurrence and never supports
a joint mode or conductance-eliminability claim.

The comparison uses the accepted GRV3 block metric, explicit `C` embedding and
projection, real invariant planes for complex pairs, clustered slow subspaces,
and uncertainty-aware unit-circle classes. Deadbeat overwrite modes are counted
separately (55 across 29 admitted secondary rows) and excluded from slow disagreement.
The primary unit-circle uncertainty range is `1e-06` to `1e-06`; maximum primary metric subspace angle is `2.10734e-08` radians.
Matrix-level symmetry conjugacy passes for `H_cont`, mobility, the frozen map,
and every admitted full `C` map.

## Interpretation

No verified branch changes stability class or slow-subspace identity within the admitted comparison envelope.
The 32 primary rows show no resolved difference within the admitted first-order
uncertainty envelope; this is not an equivalence result. The more structurally
informative frozen stable/unstable cases remain among the 16 rows whose full
GRV3 Jacobians are blocked. GRV4 opens no continuation, retention, read-back,
or write-back claim and does not establish global `W` eliminability. Finite-
amplitude `J^2 -> W` inscription remains open for later gates.

## Provenance

- Input execution revision: `01389d9877bfdf68daa3e31786f832ab17742c86`
- GRV3 result revision: `0dedbf96f2a067442ec42ab67707aa694a35fdec`
- GRV3 receipt: `83a2650f57fe3d1a814155bf6e8621881d01468b36cde0f1b460af02339b92cc`
- GRV3 acceptance anchor commit: `8b82df4f077cecf3af780165e71bfb42b6bf5575`
- Runtime source/spec/test paths: unchanged under `protected_path_manifest_v4.json`

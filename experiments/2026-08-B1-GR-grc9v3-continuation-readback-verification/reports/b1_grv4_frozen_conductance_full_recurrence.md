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
primary_agreement_count = 32
primary_bounded_difference_count = 0
verified_strong_disagreement_count = 0
runtime_sign_classification = P_G_increases_and_negative_P_G_decreases_weakly_over_tested_discrete_sweep
GRV_C4_candidate = true
continuation = unsupported
retention = unsupported
readback = unsupported
writeback = unsupported
runtime_change_authorized = false
```

GRV4 constructs an experiment-local fixed-conductance comparator. It does
not alter `GRC9V3.step()` and does not treat the comparator as native runtime
state. The runtime sign follows directly from the implemented equations:
`Phi = gradient(P_G)`, `J = -eta W grad(Phi)`, and continuity therefore
gives `dC/dt = eta L_W gradient(P_G)`. Thus `P_G` is weakly
nondecreasing in the semidiscrete fixed-`W` reduction and `-P_G` is weakly
nonincreasing. Stationary rows count as equality, not strict increase.

## Discrete And Runtime-Stage Audit

The preregistered amplitude/timestep matrix contains 1536 rows.
The maximum staged-runtime versus explicit-map error is `1.77636e-15`.
The minimum finite-step functional delta is `-6.39488e-15`.
The audit calls the existing potential, flux, and continuity stages while
holding the accepted branch conductance fixed; it excludes conductance
reconstruction and every semantic/topology stage by declaration.

## Frozen/Full Boundary

All 48 accepted branches receive a frozen structural comparator. Only the
32 branches with a GRV3-admitted `C` transition matrix receive the primary
full-recurrence comparison. The 16 exact-zero-current boundary branches are
retained as blocked comparisons rather than silently removed. `C-W` is a
secondary diagnostic of evolving-conductance recurrence and never supports
a joint mode or conductance-eliminability claim.

## Interpretation

No verified branch changes stability class or slow-subspace identity within the admitted comparison envelope.
Agreement is a bounded result, not proof that frozen conductance is the full
core continuation operator. GRV4 opens no continuation, retention, read-back,
or write-back claim and does not establish global `W` eliminability.

## Provenance

- Input execution revision: `e21ec2cd9f3dcfdacb2b707d707b6480ce856bf0`
- GRV3 result revision: `0dedbf96f2a067442ec42ab67707aa694a35fdec`
- GRV3 receipt: `83a2650f57fe3d1a814155bf6e8621881d01468b36cde0f1b460af02339b92cc`
- GRV3 acceptance anchor commit: `8b82df4f077cecf3af780165e71bfb42b6bf5575`
- Runtime source/spec/test paths: unchanged under `protected_path_manifest_v4.json`

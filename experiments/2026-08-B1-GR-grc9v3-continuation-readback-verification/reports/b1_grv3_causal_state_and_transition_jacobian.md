# B1-GR GRV3 Causal State And Transition-Jacobian Gate

## Result

```text
gate = GRV3
mechanical_status = passed
scientific_acceptance = awaiting_human_review
branches_audited = 48
bounded_causal_closure_candidates = 48
full_C_W_J_square_jacobians_admitted = 0
reduced_coordinate_matrices_admitted = 64
admitted_reduced_symmetry_orbits = 16
branches_with_reduced_temporal_coordinates = 32
spectral_convergence_pass_matrices = 61
temporal_mode_interpretation_pass_matrices = 61
response_convergence_pass_matrices = 64
finite_horizon_nonnormal_pass_matrices = 64
individual_eigenvector_condition_block_matrices = 2
cluster_interpretation_pass_matrices = 62
phase_operator_pass_matrices = 64
basis_covariance_pass_matrices = 64
symmetry_covariance_pass_pairs = 32
symmetry_covariance_failed_or_blocked_pairs = 0
omitted_state_decomposition_pass_branches = 48
branches_without_admitted_temporal_coordinates = 16
continuation = unsupported
retention = unsupported
readback = unsupported
writeback = unsupported
runtime_change_authorized = false
```

GRV3 begins with causal closure rather than a numerical Jacobian. All 48
accepted GRV2 rows are consumed in committed registry order. The 32 symmetry
orbits remain an interpretation of dependence and do not reduce execution
scope or select branches after outcomes are visible.

## GRV3-A: Causal Closure

The branch-relative `(C,W,J)` codec is tested for round trip, reached-state
canonicalization, and complete-step commutation on `48`
of `48` branches through horizons `1, 2, 5, 10`.
This is bounded branch-envelope evidence only. It does not establish global
Markov sufficiency or global eliminability of omitted runtime fields.
P3.4 additionally removes every cache key one at a time and audits the
unknown placeholder fields over the same horizons. A passing omission row
means reconstructed or inert on this declared envelope, never globally
causally absent. The whole cache dictionary is not admitted as state.

## GRV3-B: Classical Derivative Admission

All accepted rows satisfy the GRV2 authoritative zero-current tolerance;
`16` rows are exactly on the
current-sign boundary, while the remaining rows retain only small numerical
distance from it. Every full `(C,W,J)` chart has at least one blocked column,
so no complete `(C,W,J)` matrix is emitted. A failed stratum column is blocked,
not reported as an unconverged derivative.

The frozen reduction audit admits `64`
reduced matrices across `32`
branches and `16` symmetry orbits.
The matrix count includes both `C-W` and `C` candidate charts for each
admitted branch; it is not a count of independent branches. Both candidates
are retained where admitted; GRV3 does
not select one primary coordinate after seeing spectra. These are bounded
branch-envelope reductions, not global elimination of `W` or `J`.
Each admitted matrix is separately gated on column, matrix, eigenvalue-set,
near-unit/fast invariant-subspace, response-surface, and finite-horizon
nonnormal convergence. Ill-conditioned eigenvector matrices block individual
eigenvector interpretation; converged cluster spans are reported separately
and neither object is promoted to retention evidence.
Every admitted reduced matrix is also recomputed at administrative phase
offsets 0, 1, 2, and 4. Fixed-operator spectral interpretation is allowed
only when those derivatives agree within the frozen phase bound. Decoder
correction, RNG consumption equality, and formed-branch residual relative
to each finite-difference step are column-local fail-closed gates.
An alternate orthonormal zero-sum basis must reproduce each matrix by
conjugacy, and every multirow symmetry orbit must satisfy its declared
node/edge transport relation. Raw and branch-scale-normalized block
participation remain diagnostic; no joint C-W mode claim is admitted.
`3`
otherwise admitted matrices remain interpretation-blocked by those gates;
their branch and coordinate identities are retained in the machine summary.

## GRV3-C: Response And Categorical Surfaces

Smooth response Jacobians are computed only for admitted reduced-coordinate
matrices, audited at every preregistered finite-difference step, and supported
only when adjacent-step convergence passes. They remain blocked for unavailable
charts. Current-sign, sink, basin,
event, and budget-active-set behavior is retained as categorical threshold
evidence rather than inserted into an eigensystem.
Odd first-order and sign-even quadratic J responses are recorded separately.
An unresolved complete-beat response does not erase the GRV1 stage-local
J^2 path and cannot support J eliminability.

## Claim Boundary

A GRV3-A pass may support a bounded causal-strong-branch candidate after human
review. It does not by itself complete GRV-C4, which also requires admitted
GRV3-B/C evidence and GRV4 frozen/full comparison. A blocked Jacobian is a
scientific boundary result, not stability, continuation, retention, read-back,
or write-back evidence.

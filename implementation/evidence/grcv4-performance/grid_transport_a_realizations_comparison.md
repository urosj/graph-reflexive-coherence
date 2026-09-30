# Candidate A: matrix reuse on configurable grids

All new measurements use **4×5, 20 nodes, 31 edges, five evolving strict public steps**. Each cache-enabled/disabled pair uses exactly the same identity-bound declaration. Across realizations the geometry gains differ; RG2b also changes eta and dt.

| Realization | Reuse disabled: 5 steps | Reuse enabled: 5 steps | Speedup | Time saved |
|---|---:|---:|---:|---:|
| A_OS (previous run) | 61.42 s | 32.79 s | 1.87× | 46.6% |
| A_CI | 333.24 s | 153.38 s | 2.17× | 54.0% |
| A_PC | 72.68 s | 72.24 s | 1.01× | 0.6% |
| A_CI_PC | 370.35 s | 161.75 s | 2.29× | 56.3% |
| A_RG2b | 287.41 s | 224.30 s | 1.28× | 22.0% |

Step totals exclude declaration admission, public-owner setup, diagnostics, progress output and final snapshotting. These are single-run local measurements, not confidence intervals or universal speedups.

## Matrix preparation volume

Every lookup in the disabled control recomputes both the exact inverse and the conditioning proof. The ordinary bounded LRU lookup is evaluated before its result is discarded, so repeat counts identify the preparations the enabled path can avoid. All right-hand sides and their residual checks still run. Counts exclude initial-owner setup and count only the shared solver preparation, not unrelated model proofs.

| Realization | Preparations without reuse | With reuse | Avoided | Reduction |
|---|---:|---:|---:|---:|
| A_CI | 105 | 19 | 86 | 81.9% |
| A_PC | 15 | 14 | 1 | 6.7% |
| A_CI_PC | 102 | 18 | 84 | 82.4% |
| A_RG2b | 65 | 19 | 46 | 70.8% |

CI and CI+PC have repeated coefficient matrices during root construction, so the bounded operation cache removes many preparations. PC has only one repeat in the entire five-step run; its continuing steps prepare different read/reset/post-carrier geometries. Its roughly one-percent timing difference should be treated as no material speedup in this single-run measurement.

The preparation counter covers the shared solve helper. In particular, CI/RG2b analytic residuals still call _c_inverse(h) directly in src/pygrc/models/grc_v4_ci.py::_analytic_residual, bypassing that helper. The cost of these calls was not separately profiled here. No production optimization or architectural extension was made in this benchmark task.

## Evolving step times

| Realization | Enabled steps 1–5 (s) | Disabled steps 1–5 (s) | Public setup enabled / disabled (s) |
|---|---|---|---|
| A_CI | 26.78, 32.24, 30.67, 33.79, 29.90 | 70.08, 70.69, 66.33, 62.02, 64.12 | 42.98 / 42.81 |
| A_PC | 7.72, 18.33, 16.93, 14.24, 15.02 | 8.04, 17.82, 17.38, 14.64, 14.80 | 1.05 / 0.99 |
| A_CI_PC | 28.41, 36.28, 34.69, 35.73, 26.64 | 84.75, 72.03, 77.00, 76.92, 59.65 | 53.69 / 56.43 |
| A_RG2b | 33.84, 48.31, 46.55, 47.30, 48.28 | 60.24, 57.37, 55.59, 56.26, 57.94 | 26.54 / 28.17 |

## Strictness and reproducibility

All four pairs have exactly equal full input declarations, differential references, C/W/Z values at every step, clock/receipt counts, and final snapshot byte counts and SHA-256 digests. Every operation committed through the production public lifecycle. No solver tolerance, certificate or validation was relaxed to enable reuse.

Declaration admission passed for all four realizations at 2×3, 3×4 and 6×6; each also completed a strict public step at 2×3. The 4×5 initial C/W and reference graph match the existing OS example. Other sizes bound the resource contrast and scale conservative declarations; admission can fail closed.

Production runtime revision and source hashes are retained in [the machine-readable comparison](grid_transport_a_realizations_comparison.json). The production working tree has no changes in this benchmark task.

## Declarations

| Realization | Physical dt | Geometry gain | eta |
|---|---:|---:|---:|
| A_CI | 0.015625 | 0.09375 | 0.125 |
| A_PC | 0.015625 | 0.000244140625 | 0.125 |
| A_CI_PC | 0.015625 | 0.000244140625 | 0.125 |
| A_RG2b | 1.52587890625e-05 | 1.52587890625e-05 | 0.02 |

## Reports

- A_CI: [reuse enabled](grid_transport_a_ci_4x5_5.json), [disabled control](grid_transport_a_ci_4x5_5_reuse_disabled.json).
- A_PC: [reuse enabled](grid_transport_a_pc_4x5_5.json), [disabled control](grid_transport_a_pc_4x5_5_reuse_disabled.json).
- A_CI_PC: [reuse enabled](grid_transport_a_ci_pc_4x5_5.json), [disabled control](grid_transport_a_ci_pc_4x5_5_reuse_disabled.json).
- A_RG2b: [reuse enabled](grid_transport_a_rg2b_4x5_5.json), [disabled control](grid_transport_a_rg2b_4x5_5_reuse_disabled.json).
- [Additional dimensions and public-step checks](grid_transport_a_general_validation.json).

Use examples/grcv4/grid_realizations_a.py for the ordinary run and scripts/benchmark_grcv4_grid_a.py for the disabled control, with --realization, --rows, --cols and --steps. Candidate C is measured separately in [its configurable-grid comparison](grid_transport_c_realizations_comparison.md).

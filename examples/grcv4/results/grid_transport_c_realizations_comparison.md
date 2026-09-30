# Candidate C on configurable strict-public grids

The configurable [Candidate C runner](../grid_realizations_c.py) uses the same grid topology, reference edge weights, and initial resource pulse as the [Candidate A grid](../grid_realizations_a.py). C has no A edge history. Its selector cutoff is proposed between the first two positive reference stiffness eigenvalues, giving a nonconstant sector; production exact inertia and the realization's domain certificate decide admission. The admitted declaration is fixed for every public step. These are distinct physical experiments, even at the same grid size.

These measurements precede the [exact conditioning-certificate optimization](grid_transport_c_exact_psd_comparison.md). The paired measurements below use **3×4, 12 nodes, 17 edges, and five evolving strict public steps** in fresh processes. Step totals exclude declaration admission, owner setup, result/snapshot digest capture, and final snapshotting. Each control discards operation-local inverse and conditioning lookup results in the benchmark observer; production admission, RHS, residuals, certificates, and publication are unchanged. Results are single local samples, not statistical speedup estimates.

| C realization | Reuse disabled: five steps | Automatic reuse: five steps | Ratio |
| --- | ---: | ---: | ---: |
| OS | 102.93 s | 81.49 s | 1.26× |
| CI | 126.91 s | 60.42 s | 2.10× |
| PC | 81.35 s | 64.24 s | 1.27× |
| CI+PC | 129.24 s | 61.98 s | 2.09× |
| RG2b | 274.81 s | 217.39 s | 1.26× |

The corresponding exact matrix preparation counts are:

| C realization | Inverses, disabled → enabled | Conditioning proofs, disabled → enabled | Combined reduction |
| --- | ---: | ---: | ---: |
| OS | 275 → 145 | 200 → 111 | 46.1% |
| CI | 570 → 123 | 360 → 66 | 79.7% |
| PC | 180 → 100 | 120 → 67 | 44.3% |
| CI+PC | 585 → 119 | 360 → 62 | 80.8% |
| RG2b | 590 → 222 | 360 → 128 | 63.2% |

Every enabled/disabled pair has an identical complete declaration, final snapshot digest, and **every step's complete public result and snapshot digest**. All five resource trajectories change by nonzero amounts; PC and CI+PC also develop nonzero carriers. The [machine-readable comparison](grid_transport_c_realizations_comparison.json) preserves per-step times, the count method, declaration hashes, source hashes, and links to each full report.

## Bounded continuation, measured separately

The continuation control retains normal operation-local reuse and discards only the facts selected for the next step. Fresh scientific checks and full public outputs match exactly between each pair.

| C realization | Operation-local only | With continuation | Ratio | Inverses | Conditioning proofs |
| --- | ---: | ---: | ---: | ---: | ---: |
| PC | 69.98 s | 68.03 s | 1.03× | 108 → 100 | 75 → 67 |
| CI+PC | 71.56 s | 73.24 s | 0.98× | 123 → 119 | 66 → 62 |
| RG2b | 195.73 s | 193.03 s | 1.01× | 227 → 222 | 136 → 128 |

PC retained four facts per step; CI+PC retained two; RG2b retained four after the first and three after later steps. The smaller computation counts are real, but **these single timing samples do not show a material continuation speedup for C**. In particular, CI+PC's enabled time is slightly higher. The [continuation comparison](grid_transport_c_continuation_comparison.json) retains all per-step times, numerical work counts, fresh-check counts, retention counts, source hashes, and links to the full paired reports. Its observer adds overhead, so its absolute times should be compared only within its own pairs, not against the first table.

## Size and remaining numerical cost

Before the exact certificate optimization, one admitted strict C_OS step on **4×5, 20 nodes and 31 edges** took **140.41 s** for declaration admission, **74.64 s** for owner setup, and **226.33 s** for the public step. The [one-step 4×5 report](grid_transport_c_os_4x5_1.json) keeps the declaration, state, receipt count, and final snapshot digest. This is a single step, not an extrapolated five-step total. It also uses C's own physics and cannot be read as an A-versus-C algorithmic speed ratio.

A focused [3×4 C_OS step profile](grid_transport_c_stage_cost_3x4_os_1.json) measured 16.10 s for one public step. Five Candidate C selector constructions took 0.21 s; 19 exact conditioning proofs took 8.88 s and 25 exact inversions took 4.38 s. Those two matrix preparation bodies account for about 82% of that observed step. Nested current/algebra/selector timings overlap, so they are not additive. This identifies the expensive work at 3×4; the 4×5 run was timed end to end, not stage-profiled. It would be premature to assign the same 82% share to 4×5 without measuring it.

## Reproduce

From the repository root, with the existing environment:

```bash
PYTHONPATH=src:.:tests .venv/bin/python examples/grcv4/grid_realizations_c.py --realization OS --rows 3 --cols 4 --steps 5
PYTHONPATH=src:.:tests .venv/bin/python examples/grcv4/benchmark_grid_c.py --realization CI --rows 3 --cols 4 --steps 5
PYTHONPATH=src:.:tests .venv/bin/python examples/grcv4/benchmark_grid_c.py --realization CI --rows 3 --cols 4 --steps 5 --reuse
PYTHONPATH=src:.:tests .venv/bin/python examples/grcv4/benchmark_grid_continuation.py --candidate C --realization PC --rows 3 --cols 4 --steps 5 --disable-continuation
PYTHONPATH=src:.:tests .venv/bin/python examples/grcv4/benchmark_grid_continuation.py --candidate C --realization PC --rows 3 --cols 4 --steps 5
```

Replace `--realization` with `OS`, `CI`, `PC`, `CI+PC`, or `RG2b` for the ordinary/reuse example; continuation applies to `PC`, `CI+PC`, and `RG2b`. A rejected declaration or public step aborts the example rather than entering its timing table. The 4×5 C_OS command is the same ordinary runner with `--rows 4 --cols 5 --steps 1`.

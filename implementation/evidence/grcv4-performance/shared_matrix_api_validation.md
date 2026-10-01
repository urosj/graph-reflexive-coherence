# Shared V4 matrix API validation

Baseline: `1898dc786257cca2f5d5ab28e8413debb353a18c`. Refactor is uncommitted at validation time.

## Scope

All ten A/C realizations call `grc_v4_numerics` for shared exact matrix arithmetic.
The private implementation is `_grc_v4_matrix`; realization imports of it are rejected by a boundary test.
Inverse and conditioning facts reuse the existing operation store automatically.
An explicit `MatrixReuse.FRESH` scope bypasses lookup, seeding, and continuation retention.
Nested public operations inherit the policy and retain separate stores.
RHS, residual, positivity, scientific admission, and stage certificate checks remain fresh.
The bounds remain 64 facts per operation and four retained facts between eligible steps.

## Exact compatibility with the committed implementation

The committed `src`, `tests`, and `specs` were exported with `git archive`, then run
in a separate process using the same interpreter as the refactor. Both runs used
`tests.models.test_grc_v4_generic_lifecycle.fixture/model` and the lifecycle request
helper, with request IDs `matrix-api-baseline-0` through `matrix-api-baseline-2`.
The initial snapshot, all three complete public results, and all three snapshots
were compared as exact canonical UTF-8 strings. Every comparison passed.

The following SHA-256 digests identify the matching final snapshot bytes:

| Family | Final snapshot SHA-256 |
| --- | --- |
| `A_OS` | `f81ca146fa72decec63817ae6260efcb23b2eb7fef8c4ddb154485179d465e8b` |
| `C_OS` | `ed1f77f42dfee98b1d0021a75cf5394e969d0c90525202b0b2339db521434c9c` |
| `A_CI` | `530865a4bd8d3924fc57f1171515598afc42634062cb2ff8a5c7fe4dc8bd34dd` |
| `C_CI` | `dcacf6277b4fcf6b95448241492c9ae9fef6188155efbdf0e3a63d764efaf408` |
| `A_RG2b` | `b9e96a8cea2f9d94a9d7bee7980995fcf27dc993a07c554f15800e470c35645b` |
| `C_RG2b` | `d5ea2b555ae97e6824325b17684a656b099c5f54ecd81991c1096b79dadd1f86` |
| `A_PC` | `7a6851bcd2a945c184b9cfd9a8449593b29c32706851502d16971605c0b18a12` |
| `C_PC` | `a97c044ea4a059cd7bd0974f4914da92fa25bfcaa4da76048bb55c57e1097366` |
| `A_CI_PC` | `e6d61860399fa28b3a62c3b66dec6beafd4039ff59409f23e0b86d946c44ed7c` |
| `C_CI_PC` | `b0c70e2d0ffff392d799010d20d1651c4c1e33c84e2b5055a032d7efa28ec3a0` |

An additional regression test compares automatic and fresh calculation for two
evolving public steps in every family, including complete result bytes, snapshots,
and empty continuation in fresh mode.

## Regression and static checks

- The full V4 discovery run completed 991 tests in 1100.581 seconds, with four optional tests skipped.
- That initial run exposed four failing test methods: two source-capture tests needed the new files in the Git preimage, one observer test used the old arithmetic alias, and one fault injection needed to target the intended OS audit boundary after the SPD solve became shared. The harnesses were corrected.
- The final affected regression run passed all 59 tests in 62.615 seconds. It includes all four corrected methods, the new API tests, linear-fact tests, continuation tests, and OS split audit tests.
- Strict mypy passed for the numerical API, private implementation, and fact store.
- Ruff passed for the new/refactored numerical modules, API/fact/continuation tests, and benchmark observer. Existing production files gained no Ruff diagnostics relative to the baseline.
- `git diff --check` passed.

The skipped tests are the three opt-in wheel/sdist installation or reconstruction
campaigns and the opt-in 32-vertex RG2b campaign. A second full discovery run was
not performed after the harness corrections; the affected suites were rerun.

## Benchmark observer smoke check

Command: `PYTHONPATH=src:.:tests .venv/bin/python scripts/benchmark_grcv4_grid_continuation.py --realization CI+PC --rows 2 --cols 2 --steps 2`.

The strict public run admitted both steps on four nodes and four edges.
Both steps retained two facts. Across the steps, the shared observer recorded
9 actual inverse computations and 1 actual conditioning computations,
with 24 fresh condition certificates and 60 residual checks.
This verifies the observer migration; it is not a new speedup comparison.
Previous retained performance reports describe the earlier reuse optimization.

## Runtime source digests

| File | SHA-256 |
| --- | --- |
| `src/pygrc/models/grc_v4_linear.py` | `3b17cfd76fb92d9656c214d2eab5e9dfd82dafe28c2a370a50d536452e62b232` |
| `src/pygrc/models/grc_v4_numerics.py` | `65367617a53583776544277416a6cd536caac39cc8abb9be7897cb51f97a1291` |
| `src/pygrc/models/_grc_v4_matrix.py` | `7a20684e0c439e40deb5adc7b2dc6505ee1183f2ae0fb638236228c0b8475c79` |
| `src/pygrc/models/grc_v4_codec.py` | `46785802cfd7482b10204b228df6aab62da4be8f8e4f5705eda7284ba132c4a4` |
| `src/pygrc/models/grc_v4_lifecycle.py` | `f99c23babc29ce44f41818b1dc7b4cf205c7af6479a470923513ebb1e4fcd2f5` |
| `src/pygrc/models/grc_v4_pc.py` | `60a82e21c972348304d41d75e46d521f4e7b5605d59113f132ea2760fe42e2ab` |
| `src/pygrc/models/grc_v4_ci.py` | `f4089568e989d2386297c25624e02a20da6522707beeaef527e2650274bd2bf8` |
| `src/pygrc/models/grc_v4_rg2b.py` | `adcd6535180afd4f0694c5f3200a12130aea514c5756c1eeb79fcfd9f1437fba` |
| `src/pygrc/models/grc_v4_rg2b_graph.py` | `7e950e2055a91656907d98f464cd0191cb123d13f2f248be96bab08de49e1d7e` |
| `src/pygrc/models/grc_v4_candidate_a.py` | `67ce9f78841f6935c675b8251c4ab520558e25c18baa31f7db1a73d8ad66cefc` |
| `src/pygrc/models/grc_v4_candidate_c.py` | `96a7b72e03d55475690a93009ee00c1ec86ccf723064afe877688f55c671b338` |

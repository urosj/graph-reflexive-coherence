# Phase 5 Representative Runtime Lane

## Purpose

Iteration 11 needs one real `GRCV3` runtime lane that is deterministic and
reproducible enough to support later `GRC9V3` hybrid work.

This note records that first lane and the minimum evidence it must leave
behind.

## Selected Lane

The first representative lane uses a conservative seed, not a reduced step
loop:

- intrinsic three-node chain
- `geometry = induced_local_frame`
- `differential_summary = weighted_least_squares`
- `metric = tensor_exponential`
- `spark = signed_hessian_plus_attractor_delta`, but effectively suppressed by
  a very large `eps_spark`
- `choice = disabled`
- no host embedding requirement
- no hierarchy growth expectation

The exact Phase 5 reference step loop is documented in
[Phase-5-StepLoop.md](./Phase-5-StepLoop.md). This lane is meant to prove that
the full baseline loop:

- can execute real steps,
- preserves deterministic replay,
- survives save/load,
- and produces reproducible snapshots under fixed inputs.

That includes the current deterministic budget-closure heuristic described in
[Phase-5-StepLoop.md](./Phase-5-StepLoop.md), not an unspecified abstract
`enforce_budget` placeholder.

## Representative Seed

The lane uses a three-node chain with monotonically decreasing coherence:

- left node: `1.2`
- center node: `0.75`
- right node: `0.35`

Initial edge conductances are both `1.0`.

The seed is intentionally simple because Iteration 11 is an execution sanity
gate, not yet a full experiment program. Simplicity of the seed should not be
read as looseness in the constitutive runtime semantics.

## Required Evidence

Iteration 11 should leave enough evidence to show the lane is real:

1. deterministic repeated runs under identical initial conditions
2. save/load replay agreement after an intermediate snapshot
3. reproducible final snapshot digest
4. a small reconstruction script that can rerun the lane without rebuilding the
   setup manually

## Reconstruction Script

The representative reconstruction entrypoint is:

- [scripts/run_grcv3_representative_smoke.py](../scripts/run_grcv3_representative_smoke.py)

It writes a compact evidence bundle under:

- `outputs/<experiment_id>/grcv3/`

with:

- `final_snapshot.json`
- `report.json`

## Deliberate Limits

This lane does not attempt to prove:

- spark-rich geometry growth,
- choice/collapse dynamics under active ambiguity,
- hierarchy branching under runtime splits,
- or telemetry-grade experiment coverage

Those remain later-phase concerns. Iteration 11 establishes that the family now
runs as a deterministic executable reference lane rather than as a unit-test-
only semantic shell.

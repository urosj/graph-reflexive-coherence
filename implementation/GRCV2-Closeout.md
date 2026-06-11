# `GRCV2` Closeout

This note records the implementation-facing closeout state of `GRCV2`.

It exists so that later work does not have to reconstruct, from scattered
phase documents, whether `GRCV2` is still exploratory or whether it is already
an operational baseline.

## Status

`GRCV2` should now be treated as **closed as the first executable family
baseline**.

That does not mean every downstream surface is feature-complete. It means the
family is no longer blocked on missing core semantics, missing runtime
evidence, or missing reconstruction discipline.

## What Is Closed

The following implementation slices are in place and should be treated as
established baseline capability rather than open design space:

- the strict `GRCV2` step loop and state evolution path
- paper-aligned tensor / metric / potential / flux / sink / basin baseline
- deterministic replay under fixed params, seed input, and RNG seed
- stable save/load and canonical artifact identity
- landscape-seed projection for representative seeds
- PDE-informed parameter-family bridge sufficient to run the first canonical
  lanes
- telemetry capture, summaries, reports, and experiment artifact layout
- graph-checkpoint export for topology / flow evidence
- artifact-driven representative visualization for both behavior and graph
  surfaces

## Operational Evidence

`GRCV2` is not closed merely because the code compiles or the tests pass.

It is closed because the project now has a full executable evidence lane:

- canonical representative seeds:
  - `cell-1`
  - `cell-4`
- canonical parameter family:
  - `balanced_baseline`
- canonical representative envelope:
  - `num_steps = 100`
  - `rng_seed = 7`
- deterministic replay confirmed across repeated full-envelope runs
- byte-identical scalar telemetry under same-envelope reruns
- byte-identical dense graph-checkpoint payloads under same-envelope reruns
- reproducible artifact generation through:
  - [`../scripts/run_representative_fulltest.py`](../scripts/run_representative_fulltest.py)

This is the threshold that makes `GRCV2` a real baseline rather than a draft
implementation.

## What Remains Open But Non-Blocking

The following items remain legitimate future work, but they should no longer be
treated as reasons to hold `GRCV2` open:

- visualization polish and presentation refinement
- richer telemetry/report features closer to the PDE-side `25*`
  classification discipline
- denser or more configurable visualization surfaces
- additional experiment lanes and parameter-family exploration
- stronger automated reconstruction / regression scripts around the current
  representative lane

These are important, but they are **post-baseline improvements**, not missing
family fundamentals.

## What Phase 5 Must Assume

`GRCV3` should start from the assumption that `GRCV2` already provides:

- the executable weighted-graph reference family
- the first authoritative determinism story
- the first authoritative artifact and replay story
- the first representative experiment lane
- and the first artifact-backed visualization lane

Phase 5 should therefore extend the baseline, not reopen it casually.

If Phase 5 discovers a genuine contradiction in shared semantics, the burden is
to state that contradiction explicitly. It should not silently treat `GRCV2` as
still provisional.

## Practical Reading

If someone needs the shortest implementation-facing statement of where things
stand:

`GRCV2` is operational, reproducible, and evidence-backed. It may still be
refined, but it no longer needs more work before later families can be built on
top of it.

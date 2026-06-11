# Phase T GRCV3 Telemetry Closeout

## Purpose

This note closes the first `GRCV3` telemetry slice completed in Phase T
Iterations 16 through 19.

The goal of this slice was not graph-visible telemetry. It was to prove that
the shared telemetry framework can describe, persist, and compare an executable
`GRCV3` lane without changing model semantics.

## What Was Implemented

The completed `GRCV3` telemetry slice now provides:

- an explicit family-extension contract for:
  - step rows
  - event rows
  - run summaries
- recorder support for:
  - shared run-level family extensions
  - per-step family extensions
  - per-event family extensions
  - run-summary family extensions
- a representative telemetry-backed `GRCV3` experiment helper:
  - `run_grcv3_representative_experiment(...)`
- a reconstruction script:
  - [scripts/run_grcv3_representative_telemetry.py](../scripts/run_grcv3_representative_telemetry.py)
- artifact-backed experiment and comparison reports for the Phase 5 reference
  runtime lane

## Validated Evidence

The representative closeout lane was executed with:

- lane name: `phase_t_iter19_closeout`
- steps: `3`
- comparison surface: `primary` vs `replay`

The reconstruction command used was:

```bash
./.venv/bin/python scripts/run_grcv3_representative_telemetry.py \
  --outputs-root outputs \
  --lane-name phase_t_iter19_closeout \
  --steps 3
```

The run produced:

- primary run id:
  - `39a6b9a14f598f9b6523b4049ce2d98c352362c2fdf9ee25212d27b4b99aa12f`
- replay run id:
  - `dd9a83557e5ee88b29d0668f90bbcb0aa67afdbfe40a4ad9f6540f359435af4e`
- matching final snapshot digest on both sides:
  - `09364e2b22779d26185666d767a3dc54e512992301bc5a4f9ad53efc45594dd9`

Artifact-backed inspection confirmed:

- identical final observables between `primary` and `replay`
- identical `grcv3` run-summary family extensions between `primary` and
  `replay`
- zero event-count delta in the comparison report
- zero lifecycle counts in the saved representative lane
- step rows preserving the full Phase 5 canonical step order
- `grcv3` family-extension payloads present on saved step rows and run
  summaries

The concrete saved artifact lane is:

- `outputs/representative/grcv3/phase_t_iter19_closeout/primary/.../telemetry/`
- `outputs/representative/grcv3/phase_t_iter19_closeout/replay/.../telemetry/`

## What This Validates

This closeout justifies the following claims:

1. `GRCV3` can now emit the shared Phase T telemetry dialect plus explicit
   family extensions without touching `GRCV3.step()`.
2. The first `GRCV3` telemetry lane is replay-stable at the artifact level,
   not just in memory.
3. Post-processing and comparison helpers can consume `GRCV3` telemetry without
   a second family-local reporting stack.
4. The shared telemetry framework is now broad enough for later families to add
   per-step, per-event, and per-summary extensions without reworking the core
   recorder.

The zero-event outcome in this closeout lane should be read carefully:

- it is produced by the representative configuration
  - notably `eps_spark = 1e6`
- it is not evidence that the event-extension path is missing
- it means the first closeout lane validates deterministic behavior-facing
  telemetry before moving to more eventful phenomenology

The representative identity is also intentionally synthetic in this slice:

- `seed_path` is recorded as `synthetic/grcv3/<lane_name>/<role>`
- `param_family` is `None`
- `rng_seed` is `None`

This reflects that the closeout lane is the Phase 5 reference runtime rather
than a landscape-seed-driven experiment family.

## Deferred Boundary

The following remain intentionally deferred after this first `GRCV3` telemetry
slice:

- landscape-seed-driven `GRCV3` telemetry lanes
- broader `GRCV3` parameter-lane comparison campaigns
- cross-family comparison claims beyond what the summary surface can honestly
  support

These are not hidden gaps in the current slice. They are the deliberate next
boundary.

## Later Checkpoint Follow-On Status

The representative checkpoint-telemetry follow-on planned later in Phase T has
now also been completed for the synthetic representative `GRCV3` lane.

That later slice adds:

- representative `GRCV3` graph checkpoint export
- checkpoint-level honest flow overlays when realized edge flux exists
- explicit `grcv3` family checkpoint extensions
- loadable representative graph-checkpoint artifacts without live model state

What remains deferred after that later checkpoint slice is narrower:

- graph-visible rendering and layout policy on top of saved `GRCV3` checkpoint
  artifacts
- ambient chart/layout hints for the synthetic representative lane
- richer hierarchy/spark/choice overlay groups beyond the first checkpoint
  contract

## Final Landscape Checkpoint Follow-On Status

The final Phase T follow-on for the seed-driven `GRCV3` landscape lane has now
also been completed.

That final slice adds:

- seed-driven `cell-1` / `cell-4` `GRCV3` checkpoint export
- landscape-lane honest flow overlays when realized edge flux exists
- loadable real-seed checkpoint artifacts without live model state
- the final telemetry-side handoff back to Phase V landscape graph rendering

The concrete landscape checkpoint lane recorded here used:

- experiment path:
  - `outputs/representative/grcv3_landscape_checkpoint/seed_baseline/`
- steps:
  - `3`
- checkpoint cadence:
  - `every_step`
- cell-1 run id:
  - `3f87fb9dbb4e3724d9c3c973b7885ac500bc89304af13eea4caf8e6fe138f823`
- cell-4 run id:
  - `8046610fa18891bd036ffbcba29bf9e762186f4bcae4bfe34973c7cec75dc5a4`

The reconstruction command used was:

```bash
./.venv/bin/python scripts/run_grcv3_landscape_telemetry.py \
  --outputs-root outputs \
  --experiment-path representative/grcv3_landscape_checkpoint \
  --profile seed_baseline \
  --steps 3 \
  --record-graph-checkpoints \
  --checkpoint-every-step \
  --include-flow-overlays
```

Artifact-backed inspection confirmed:

- both `cell-1` and `cell-4` emit loadable checkpoint packs
- each run emits four checkpoints:
  - `initial`
  - `interval`
  - `interval`
  - `final`
- initial checkpoints declare:
  - `flow_representation = not_available_pre_step`
- post-step checkpoints declare:
  - `flow_representation = signed_edge_flux`
- checkpoint family extensions preserve:
  - `grcv3.contract_version = phase_t_iter26_v1`

What remains deferred after this final Phase T slice is now purely downstream:

- Phase V landscape graph rendering on top of these saved checkpoint artifacts
- any richer checkpoint overlay families beyond the first contract

## Downstream Implication

For visualization:

- current Phase V work may use the saved `GRCV3` step/event/report artifacts
  for behavior-facing visual outputs
- representative graph-visible `GRCV3` visualization is already unblocked
- seed-driven landscape graph-visible `GRCV3` visualization is now also
  unblocked on the telemetry side and depends only on the remaining Phase V
  landscape graph lane

For later families:

- the shared telemetry recorder is now ready for another family to attach
  explicit per-step, per-event, and per-summary extensions
- a later family does not need to repeat the Phase T infrastructure build,
  only the family-extension contract and representative lane work

## Next Justified Step

The next justified step depends on the immediate goal:

- if the goal is to show the current `GRCV3` results honestly:
  - do Phase V behavior-facing visualization first from the saved minimal
    telemetry lane
- if the goal is `GRCV3` graph/flow visualization after that:
  - implement `GRCV3` checkpoint telemetry before returning to graph-facing
    Phase V work
- if the goal is to continue family implementation:
  - the current shared telemetry boundary is sufficient to proceed, because the
    minimal behavior-facing telemetry lane is now established for `GRCV3`

So the correct sequence is:

1. `GRCV3` behavior-facing visualization from current artifacts
2. representative `GRCV3` checkpoint telemetry and graph visualization
3. landscape `GRCV3` checkpoint telemetry
4. landscape `GRCV3` graph-visible visualization

That sequence is now complete. The telemetry/visualization side of `GRCV3` is
closed end to end; the next justified `GRCV3` work is projector-side and
`GRCL-v3` semantic refinement rather than additional Phase T infrastructure.

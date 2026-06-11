# Phase 7 Representative Runtime Evidence

## Purpose

Iteration 8 records the first artifact-backed `GRC9V3` runtime lane.

This is core Phase 7 evidence, not Phase T telemetry and not Phase V
visualization. The lane proves that the executable hybrid loop can:

- run deterministically from a saved seed,
- trigger one hybrid spark,
- mechanically expand the saturated parent identity,
- stabilize two post-expansion daughter sinks,
- preserve the quadrature budget,
- and replay from the initial snapshot with matching step/event rows and final
  digest.

## Fixture

Fixture name:

- `appendix_e_cell_division`

Builder:

- `build_representative_hybrid_model()` in
  [scripts/run_grc9v3_representative_runtime.py](../scripts/run_grc9v3_representative_runtime.py)

The fixture follows Appendix E of `papers/2026-04-GRC-9.md`:

- one pre-spark saturated parent identity,
- nine occupied parent ports,
- boundary support around the parent basin,
- deterministic bipolarization through custom expansion weights
  `(0.5, 0.0, 0.5)`,
- weak internal expansion bond weight `w_bond = 0.05`,
- and the normal post-expansion reflexive loop produces the daughter sinks.

The event does not directly create daughter sinks. The spark action creates the
mechanical module; the subsequent identity pass identifies two stabilized module
sinks.

## Replay Command

```bash
PYTHONPATH=src ./.venv/bin/python scripts/run_grc9v3_representative_runtime.py --outputs-root outputs --experiment-id phase7-grc9v3-representative --steps 3
```

## Artifact Root

The lane writes artifacts under:

```text
outputs/phase7-grc9v3-representative/grc9v3/appendix_e_cell_division/
```

Artifacts:

- `initial_snapshot.json`
- `final_snapshot.json`
- `steps.jsonl`
- `events.jsonl`
- `run_summary.json`
- `report.json`
- `checkpoints/step-00000000.json`
- `checkpoints/step-00000001.json`
- `checkpoints/step-00000002.json`
- `checkpoints/step-00000003.json`

## Observed Result

The three-step representative run produced:

- `hybrid_spark_candidate`: 1
- `hybrid_mechanical_expansion`: 1
- `hybrid_spark_completed`: 1
- `choice_detected`: 3
- `collapse`: 1

The completed hybrid spark stabilized two daughter sinks:

- daughter sink node ids: `12`, `16`
- module basin mass: `12 -> 72.0`, `16 -> 36.0`
- hierarchy update: `root -> [12, 16]`

Budget evidence:

- budget target: `108.0`
- final budget: `108.0`

Replay evidence:

- step rows match replay: `true`
- event rows match replay: `true`
- final snapshot digests match replay: `true`
- final digest:
  `8e596eba7c37d1dc6465768c2ff10139ec12e8ebfec51f34aecbfafd8018cdfb`

## Boundary

This evidence does not claim Phase T-GRC9V3 telemetry, Phase V-GRC9V3
visualization, GRC9V3 phenomenology discovery coverage, or GRCL/source-seed
lowering. At core Phase 7 closeout time, those were downstream tracks rather
than part of this representative runtime artifact.

Current status: those downstream tracks are now closed as the post-core Phase 7
completion track. This document remains the core-runtime representative
evidence anchor; the final source/lowering handoff is
[GRCL-9V3-Handoff.md](./GRCL-9V3-Handoff.md).

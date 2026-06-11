# Phase T GRC9V3 Representative Telemetry

## Purpose

This note records the first artifact-backed `GRC9V3` telemetry lane for Phase T.

The lane is intentionally narrow:

- reuse the completed Phase 7 `appendix_e_cell_division` runtime fixture
- prove that `family_extensions["grc9v3"]` is emitted on step, event, and
  run-summary rows
- keep `GRC9V3.step()` telemetry-agnostic
- record replay checks for step rows, event rows, and final snapshot digest
- keep this evidence distinct from the earlier Phase 7 runtime-only evidence

## Selected Lane

The representative fixture is:

- `appendix_e_cell_division`
- source runtime script:
  `scripts/run_grc9v3_representative_runtime.py`
- Phase T telemetry script:
  `scripts/run_grc9v3_representative_telemetry.py`

The default run uses `3` steps. This window captures:

- one hybrid spark candidate
- one mechanical expansion
- one completed hybrid spark
- choice/collapse evidence after expansion
- final Appendix E daughter sinks `12` and `16`

This lane is not a new phenomenology-discovery run. It is the Phase 7
representative runtime replayed through the Phase T-GRC9V3 telemetry contract.

## Replay Command

Run from the repository root:

```bash
PYTHONPATH=src ./.venv/bin/python scripts/run_grc9v3_representative_telemetry.py --outputs-root outputs --steps 3
```

The command prints a JSON report containing the run id, artifact paths, replay
flags, and final snapshot digest.

## Current Artifact Instance

The current checked run was produced with the default command above.

- run id:
  `2646c58bb897cefe70765eec4f87fec0fba322afeb7431f6c524881864f99d98`
- artifact root:
  `outputs/phase-t-grc9v3/representative/appendix_e_cell_division/2646c58bb897cefe70765eec4f87fec0fba322afeb7431f6c524881864f99d98/`
- final snapshot digest:
  `8e596eba7c37d1dc6465768c2ff10139ec12e8ebfec51f34aecbfafd8018cdfb`
- replay step rows match: `true`
- replay event rows match: `true`
- replay final digest match: `true`

## Artifact Layout

Artifacts are written under:

```text
outputs/phase-t-grc9v3/representative/appendix_e_cell_division/<run_id>/
```

The standard telemetry layout is:

```text
telemetry/steps.jsonl
telemetry/events.jsonl
telemetry/run_summary.json
telemetry/experiment_report.json
telemetry/graph_checkpoints/index.json
telemetry/graph_checkpoints/step-00000000.json
telemetry/graph_checkpoints/step-00000001.json
telemetry/graph_checkpoints/step-00000002.json
telemetry/graph_checkpoints/step-00000003.json
snapshots/initial_snapshot.json
snapshots/final_snapshot.json
```

The graph checkpoints in Iteration 5 are basic `port_graph` checkpoints. The
GRC9V3-specific checkpoint overlays were added in Iteration 6 and are enabled
by default. Use `--disable-checkpoint-overlays` to write basic `port_graph`
checkpoints without the GRC9V3 overlay payloads.

Each checkpoint `family_extensions["grc9v3"]` may include:

- `node_overlay`
- `port_overlay`
- `edge_overlay`
- `module_overlay`
- `choice_overlay`

Post-Lane-B note: runs using the opt-in
`spark_lane = "grc9v3_column_h_assisted"` may also expose Lane B column-H
proxy-branch diagnostics through candidate payloads, step
`hybrid_spark_state`, and node-overlay fields such as `spark_lane`, `column_h`,
`min_abs_column_h`, and `column_h_branch_hit`. The original representative
artifact remains a Phase T Lane A representative lane unless regenerated with
Lane B config.

## Contract Surface Used

Each step row carries `family_extensions["grc9v3"]` with:

- lane context
- backend configuration
- port chart summary
- row-basis differential summary
- hybrid tensor summary
- transport summary
- identity/basin summary
- hybrid spark state
- hierarchy state
- choice/collapse state
- growth state
- budget correction summary
- coarse-cache state

Each event row carries `family_extensions["grc9v3"]` with:

- event domain
- lifecycle stage
- ownership
- mutation flags
- raw-event evidence groups where applicable

The run summary carries `family_extensions["grc9v3"]` with:

- final backend, port, differential, identity, hierarchy, choice/collapse, and
  budget summaries
- lifecycle event counts
- representative Appendix E summary

The field-level contract remains in:

- [Phase-T-GRC9V3-TelemetryContract.md](./Phase-T-GRC9V3-TelemetryContract.md)

## Replay Checks

The script runs a primary trajectory, reloads the saved initial snapshot, and
runs a replay trajectory with the same telemetry identity.

The report records:

- `replay_step_rows_match`
- `replay_event_rows_match`
- `replay_digest_match`

The run-summary Appendix E block records `replay_digest_match` only when all
three replay checks pass.

## Current Limits

This representative surface does not yet provide:

- visualization-ready checkpoint indices beyond basic graph state
- Phase V-GRC9V3 visual outputs
- new GRC9V3 phenomenology discovery seeds

Those remain later Phase T, Phase V, or discovery work. Checkpoint overlays are
now present by default and are no longer a current limit.

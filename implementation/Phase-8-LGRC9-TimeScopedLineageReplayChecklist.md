# Phase 8 LGRC9 Time-Scoped Lineage Replay Checklist

Companion plan:

- [`Phase-8-LGRC9-TimeScopedLineageReplayPlan.md`](./Phase-8-LGRC9-TimeScopedLineageReplayPlan.md)

## Iteration 73. Baseline And N04 Boundary

Status: Complete.

- [x] Consume N04 Iteration 20 output.
- [x] Record primary boundary:
  `multi_topology_event_time_scoped_producer_lineage_replay_blocked`.
- [x] Confirm N04 runtime/budget multi-topology lane passed.
- [x] Confirm the failed path is artifact-only validator stale-read semantics,
  not runtime mutation or budget drift.
- [x] Preserve claim boundary: no choice, agency, RC identity collapse,
  locomotion-like, biological, identity-acceptance, inherited-N03, or
  unrestricted movement claim.

## Iteration 74. Time-Scoped Validator Semantics

Status: Complete.

- [x] Update surface-lineage artifact replay so producer stale-read checks are
  scoped by producer scheduler order.
- [x] Accept producer records that read a surface before a later topology event
  transports that surface.
- [x] Continue rejecting producer records that read the stale source surface at
  or after transport.
- [x] Continue validating transported-successor producer reads.
- [x] Preserve topology-state reabsorption digest validation for scheduled
  post-topology packet work.
- [x] Add focused regression coverage:
  `test_surface_lineage_artifact_validator_time_scopes_producer_reads`.
- [x] Preserve stale-source negative coverage:
  `test_surface_lineage_artifact_validator_rejects_source_read_after_transport`.

Run record:

```json
{
  "iteration": 74,
  "status": "passed",
  "changed_file": "src/pygrc/models/lgrc_9_v3_runtime.py",
  "validator": "validate_lgrc9v3_causal_pulse_substrate_surface_lineage_artifacts",
  "new_semantics": "producer stale-read validation is time-scoped by scheduler order"
}
```

## Iteration 75. Closeout And N04 Return

Status: Complete.

- [x] Focused runtime validator tests pass.
- [x] N04 Iteration 20 rerun passes with multi-topology artifact replay.
- [x] N04 taxonomy inventory and tag schema regenerated.
- [x] N04 handoff/README/checklist/plan updated to resume at Iteration 21.
- [x] Closeout artifacts written.

Verification:

```text
.venv/bin/python -m pytest tests/models/test_lgrc_9_v3_runtime.py -q -k "time_scopes_producer_reads or rejects_source_read_after_transport or topology_state_reabsorption_artifact_validator_reconstructs_chain"
3 passed, 109 deselected

.venv/bin/python -m pytest tests/models/test_lgrc_9_v3_runtime.py -q
112 passed

.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/run_n04_iter20_topology_mutating_repeatability_stress.py
passed
```

Closeout:

- [`Phase-8-LGRC9-TimeScopedLineageReplayCloseout.md`](./Phase-8-LGRC9-TimeScopedLineageReplayCloseout.md)
- [`Phase-8-LGRC9-TimeScopedLineageReplayCloseout.json`](./Phase-8-LGRC9-TimeScopedLineageReplayCloseout.json)

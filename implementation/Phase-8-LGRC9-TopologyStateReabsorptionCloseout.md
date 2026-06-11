# Phase 8 LGRC9 Topology-State Reabsorption Closeout

Date: 2026-05-18

Status: closed.

This continuation closes the runtime gap exposed by N04 Iteration 19-D:

```text
packet_ledger_state_reabsorption_mismatch_after_topology_event
ledger node total = 6.0
active state node total = 5.9
delta = 0.1
```

LGRC9V3 now supports default-off native topology-state reabsorption. Committed
LGRC-3 topology events can rebase active node/edge state and packet-ledger
accounting through explicit lineage maps, preserve node-plus-packet
conservation, and allow post-topology packet work to be scheduled from
lineage-current, reabsorbed state.

This is runtime support only. It does not by itself validate
topology-mutating movement.

## What Closed

- Iteration 66 froze the current N04 19-D blocker before source changes.
- Iteration 67 added default-off schema, policy flags, digest, and idempotency
  support.
- Iteration 68 added committed-topology-event-owned active state
  reabsorption.
- Iteration 69 rebased packet ledger and active runtime state through the same
  topology event and lineage map.
- Iteration 70 gated coupling and feedback producers on transported surface
  evidence plus a matching topology-state reabsorption record.
- Iteration 71 validated snapshot, telemetry, artifact replay, controls, and
  compatibility.
- Iteration 72 records this closeout and the N04 return path.

## Capability Boundary

Supported:

```text
native_topology_state_reabsorption_supported = true
```

Still blocked:

```text
movement_claim_allowed = false
adaptive_topology_movement_claim_allowed = false
topology_mutating_movement_claim_allowed = false
native_lgrc_choice_selection_claim_allowed = false
rc_identity_collapse_claim_allowed = false
agency_claim_allowed = false
locomotion_like_claim_allowed = false
biological_claim_allowed = false
identity_acceptance_claim_allowed = false
```

The runtime can now make post-topology packet work valid. N04 still has to
rerun the movement ladder before any topology-mutating movement claim can be
accepted.

## Artifact Replay Scope

The artifact-only validator reconstructs:

```text
packet event
-> source surface row
-> topology event
-> topology-state reabsorption record
-> transported/superseded surface row
-> producer record
-> scheduled packet
-> processed packet
```

It uses exported artifacts only:

```text
artifact_only = true
runtime_state_used = false
```

Current producer records do not serialize a canonical `producer_record_digest`.
Producer records are therefore validated by strict linkage:

```text
causal_surface_digest
topology_event_digest
topology_state_reabsorption_record_digest
reason_code
scheduler order
scheduled_packet_id, if scheduling occurs
```

This is sufficient for the current producer contract, but weaker than full
producer-record digest replay.

## Verification

Focused runtime and telemetry:

```text
.venv/bin/python -m pytest tests/models/test_lgrc_9_v3_runtime.py tests/telemetry/test_lgrc9v3_contract.py -q
117 passed
```

Focused Phase 8 compatibility:

```text
.venv/bin/python -m pytest tests/models/test_lgrc_9_v3_contract.py tests/models/test_lgrc_9_v3_runtime.py tests/models/test_lgrc_9_v3_native_packet_loop_baseline.py tests/models/test_lgrc_9_v3_module_split.py tests/telemetry/test_lgrc9v3_contract.py -q
238 passed, 39 subtests passed
```

Lint and diff checks:

```text
uv run ruff check src/pygrc/models/lgrc_9_v3_contract.py src/pygrc/models/lgrc_9_v3_runtime.py src/pygrc/models/lgrc_9_v3_runtime_state.py src/pygrc/models/__init__.py src/pygrc/telemetry/lgrc9v3_contract.py tests/models/test_lgrc_9_v3_runtime.py tests/telemetry/test_lgrc9v3_contract.py --extend-ignore F401,F403,F405
passed

git diff --check
passed
```

Full repository regression remains a commit-time housekeeping item.

## Worktree State

Closeout was recorded on:

```text
head = 2736641f9738312897b52f428907a46fcd4fef04
cwd = .
python = .venv/bin/python
```

The worktree is dirty because this development session includes source,
tests, Phase 8 docs, and N04 handoff/taxonomy artifacts. Unrelated Obsidian
workspace/diary files are also dirty and were not touched by this closeout.

## N04 Return

N04 should resume with a strict follow-up topology-mutating movement probe,
recorded as likely Iteration 19-E.

The next N04 question is:

```text
Does strict topology-mutating movement pass after native topology-state
reabsorption is available and enabled?
```

Until that N04 validator passes, the N04 ceiling remains:

```text
adaptive_topology_entry_candidate
```

## Future Hardening

- Add canonical `producer_record_digest` and validate producer records by
  digest as well as linkage.
- Add an independent packet-ledger-by-digest artifact index for stronger
  artifact replay diagnostics.
- Run the full repository test suite before committing the Phase 8 checkpoint.

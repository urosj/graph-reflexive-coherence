# Phase 8 LGRC9 Native Route Arbitration Candidate Emission

Status: passed.

Iteration 78 adds candidate route-set emission from runtime-visible evidence.
It emits candidate records and deterministic candidate-set records only. It
does not select a route, commit topology events, schedule packets, mutate
state, or promote movement/choice/agency claims.

## Runtime Surface

Added `LGRC9V3.emit_native_route_candidate_set(...)`.

The emitter is policy-gated by:

```text
native_lgrc_route_arbitration_enabled = true
native_lgrc_route_arbitration_policy = score_ordered_topology_route_candidates
```

When route arbitration is disabled, no candidate route or candidate-set logs
are emitted and the result carries
`native_route_arbitration_policy_disabled`.

## Evidence Rules

- Candidate routes must cite a committed source surface digest.
- Runtime-visible policy id is serialized on every candidate.
- Source producer record id is serialized when supplied.
- Topology-state reabsorption digest is serialized and checked when supplied.
- Candidate scores and score components are serialized, and score must equal
  the component sum.
- Candidate budget prediction is explicit and mandatory.
- Candidate lineage maps must cover transferred nodes.
- Hidden fixture arrays, experiment `if/else`, preselected sinks, report code,
  and post-hoc thresholds are rejected with
  `native_route_arbitration_hidden_input_rejected`.
- Candidate-set order is deterministic by declared order key:
  `score_desc_then_candidate_id` or `digest_ascending`.
- Duplicate candidate route records and candidate sets are idempotently
  suppressed.

## Runtime State

Runtime snapshots now carry:

```text
native_route_candidate_log
native_route_candidate_set_log
```

These are evidence logs only. They are not route-arbitration records and do
not authorize topology events.

## Non-Actions

Candidate emission does not emit route-arbitration records, select a topology
event, schedule packets, mutate runtime state, or promote claims.

`candidate_selected_sink_id` is candidate-local proposed topology payload only.
Run selection requires a native route-arbitration record in Iteration 79.

## Scope Limitation

Producer linkage is serialized when supplied. Current producer records do not
carry a canonical `producer_record_digest`, so Iteration 78 does not validate
producer records by digest.

## Verification

```text
.venv/bin/python -m pytest tests/models/test_lgrc_9_v3_runtime.py -q -k "native_route_candidate"
12 passed, 112 deselected

.venv/bin/python -m pytest tests/models/test_lgrc_9_v3_contract.py tests/models/test_lgrc_9_v3_runtime.py -q -k "native_route or time_scopes_producer_reads or rejects_source_read_after_transport or topology_state_reabsorption_artifact_validator_reconstructs_chain"
25 passed, 222 deselected, 20 subtests passed

git diff --check
passed
```

## Claim Boundary

This is candidate evidence only. Movement, semantic choice, agency, RC identity
collapse, identity acceptance, locomotion-like, biological, and unrestricted
movement claims remain blocked.

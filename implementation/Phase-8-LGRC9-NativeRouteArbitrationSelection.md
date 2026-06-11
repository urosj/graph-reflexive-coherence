# Phase 8 LGRC9 Native Route Arbitration Selection

Status: passed.

Iteration 79 adds native route arbitration over an existing candidate set. It
selects one candidate route through serialized runtime-visible policy and emits
a route-arbitration record. It does not commit topology events, schedule
packets, mutate state, or promote semantic choice/agency/movement claims.

## Runtime Surface

Added `LGRC9V3.arbitrate_native_route_candidate_set(...)`.

The method is policy-gated by:

```text
native_lgrc_route_arbitration_enabled = true
native_lgrc_route_arbitration_policy = score_ordered_topology_route_candidates
```

When route arbitration is disabled, no route-arbitration records are emitted
and the result carries `native_route_arbitration_policy_disabled`.

## Selection Rules

- Arbitration requires a committed candidate set and committed candidate route
  records.
- Highest-score selection emits
  `native_route_arbitration_selected_highest_score`.
- The selected candidate digest is contained in the committed candidate set,
  exactly one candidate is selected, and the selection is replayable from the
  serialized score, rule, rejected digests, and runtime-visible inputs.
- Rejected candidate route digests remain serialized on the arbitration record.
- Unresolved ties fail closed with `native_route_arbitration_unresolved_tie`
  unless the candidate set declares a deterministic runtime-visible tie-breaker.
- Declared tie-breaker selection emits
  `native_route_arbitration_selected_declared_local_preference`.
- No-candidate, budget-invalid, order-invalid, and hidden-input arbitration
  fail closed with distinct reason codes.
- Replaying the same candidate-set arbitration suppresses duplicate
  route-arbitration log records through the canonical idempotency key.

## Topology Boundary

The arbitration record serializes exactly one selected topology event id and
digest for selected records. That event is authorized, not committed. Topology
commit is deferred to Iteration 80.

## Runtime State

Runtime snapshots now carry:

```text
native_route_arbitration_log
```

Old snapshots without this log still load with an empty route-arbitration log.

## Verification

```text
.venv/bin/python -m pytest tests/models/test_lgrc_9_v3_runtime.py -q -k "native_route_arbitration"
10 passed, 124 deselected

.venv/bin/python -m pytest tests/models/test_lgrc_9_v3_contract.py tests/models/test_lgrc_9_v3_runtime.py -q -k "native_route or time_scopes_producer_reads or rejects_source_read_after_transport or topology_state_reabsorption_artifact_validator_reconstructs_chain"
35 passed, 222 deselected, 20 subtests passed

git diff --check
passed
```

## Claim Boundary

This is route-selection infrastructure only. Movement, semantic choice, agency,
RC identity collapse, identity acceptance, locomotion-like, biological, and
unrestricted movement claims remain blocked.

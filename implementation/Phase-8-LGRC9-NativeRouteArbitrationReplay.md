# Phase 8 LGRC9 Native Route Arbitration Replay

## Iteration 81 Result

Status: passed.

Iteration 81 persists, exports, reloads, and artifact-validates native route
arbitration evidence. The route-arbitration chain is reconstructable from
artifacts only:

```text
candidate route records
-> candidate set record
-> route-arbitration record
-> selected topology event
-> surface lineage record
-> topology-state reabsorption record
-> producer record
-> scheduled/processed packet
```

The artifact validator is
`validate_lgrc9v3_native_route_arbitration_artifacts`. It does not inspect live
runtime state. It restores candidate, candidate-set, and arbitration records by
canonical digest, validates selected topology-event linkage, delegates surface
lineage and topology-state reabsorption checks to the existing artifact-only
lineage validator, and verifies post-arbitration producer linkage through
transported surface digest, topology-event digest, reabsorption digest, and
scheduled packet evidence.

## Snapshot And Reload

Snapshot/load preserves:

- native route candidate logs;
- candidate-set logs;
- route-arbitration logs;
- selected topology events;
- surface lineage records;
- topology-state reabsorption records;
- idempotency caches.

Continue-after-load does not duplicate route-arbitration records, selected
topology events, surface lineage records, topology-state reabsorption records,
or producer scheduling from the same pending transported surface.

## Telemetry

Telemetry was updated in the separate telemetry namespace:

```text
src/pygrc/telemetry/lgrc9v3_contract.py
tests/telemetry/test_lgrc9v3_contract.py
```

Default-off route-arbitration telemetry remains omitted. When native route
arbitration is enabled, LGRC9V3 telemetry exports a compact
`native_route_arbitration` summary in step and run-summary extensions, and graph
checkpoints include candidate route logs, candidate-set logs, and
route-arbitration logs. Event extensions also expose selected-route topology
backreferences when topology events carry them.

## Controls

Controls remain fail-closed with distinct route-arbitration or delegated
lineage blockers:

```text
disabled policy -> native_route_arbitration_policy_disabled
no candidates -> native_route_arbitration_no_candidates
unresolved tie -> native_route_arbitration_unresolved_tie
hidden input -> native_route_arbitration_hidden_input_rejected
budget mismatch -> native_route_candidate_budget_mismatch
order inversion -> native_route_arbitration_order_invalid
duplicate arbitration -> duplicate_native_route_arbitration
topology drift -> selected_topology_event_candidate_mismatch
stale state -> delegated surface-lineage/topology-state reabsorption blocker
direct rewrite -> delegated lineage replay direct-rewrite blocker
claim promotion -> native_route_arbitration_claim_promotion_blocked
```

Identical topology-event artifacts from event rows and topology logs are
deduplicated by event id and digest. Conflicting duplicate topology artifacts
fail artifact replay.

## Claim Boundary

Iteration 81 validates runtime support only. It does not emit semantic choice,
agency, RC identity collapse, identity acceptance, locomotion-like, biological,
unrestricted movement, or claim-promotion flags.

## Verification

```text
.venv/bin/python -m pytest tests/models/test_lgrc_9_v3_runtime.py -q -k "native_route_arbitration"
26 passed, 125 deselected

.venv/bin/python -m pytest tests/models/test_lgrc_9_v3_runtime.py -q
151 passed

.venv/bin/python -m pytest tests/models/test_lgrc_9_v3_contract.py tests/models/test_lgrc_9_v3_runtime.py -q -k "native_route or time_scopes_producer_reads or rejects_source_read_after_transport or topology_state_reabsorption_artifact_validator_reconstructs_chain"
48 passed, 222 deselected, 20 subtests passed

.venv/bin/python -m pytest tests/models/test_lgrc_9_v3_contract.py -q
123 passed, 59 subtests passed

.venv/bin/python -m pytest tests/telemetry/test_lgrc9v3_contract.py -q
7 passed
```

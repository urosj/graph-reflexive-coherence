# Phase 8 LGRC9 Native Route Arbitration Commit

Status: passed.

Iteration 80 commits the topology event authorized by a native
route-arbitration record. The route is still selected only by Iteration 79's
arbitration record; Iteration 80 consumes that record, commits the selected
topology event, and verifies that surface lineage, topology-state reabsorption,
and producers use the selected event.

## Runtime Surface

Added `LGRC9V3.commit_native_route_arbitration_selection(...)`.

The method requires:

```text
committed native route-arbitration record
selected_candidate_route_digest
selected candidate still present in the committed candidate set
selected topology-event digest matching the arbitration record
```

Duplicate commit attempts are idempotent and do not append duplicate topology,
surface-lineage, or topology-state reabsorption records.

## Selected Topology Event

The committed topology event serializes:

```text
native_route_arbitration_record_id
native_route_arbitration_digest
native_route_selected_candidate_route_id
native_route_selected_candidate_route_digest
native_route_candidate_set_digest
```

The committed topology-event digest matches the digest authorized by the
route-arbitration record. Surface-lineage transport and topology-state
reabsorption consume that selected event digest.

The commit check also verifies exactly one selected topology event is committed
for the arbitration record and that rejected candidate digests do not appear as
committed selected topology-event provenance.

## Lineage Continuity

The selected candidate's declared lineage map is preserved through the full
chain:

```text
candidate route record
-> selected topology event
-> surface lineage record
-> topology-state reabsorption record
```

Source, target, and retired node sets on the topology-state reabsorption record
match the selected candidate route record.

## Producer Boundary

After commit, the coupling producer reads the transported surface digest and
verified topology-state reabsorption record before scheduling. The producer
schedules through LGRC scheduling only; `step()` processes the scheduled
post-arbitration packet work.

The producer evidence keeps these false:

```text
producer_mutated_coherence
direct_topology_write
direct_claim_write
movement_claim_allowed
```

## Controls

- Duplicate commit over the same arbitration record is idempotent.
- A stale candidate set where the selected candidate is no longer present fails
  closed before topology commit.
- A missing selected candidate record fails closed before topology commit.
- Candidate digest drift after arbitration fails closed before topology commit.
- A selected topology event cannot carry a native route-arbitration record id
  that is not present in the committed arbitration log.

## Budget

Budget remains exact across:

```text
selected topology event
surface lineage
topology-state reabsorption
producer scheduling
step() packet processing
```

## Verification

```text
.venv/bin/python -m pytest tests/models/test_lgrc_9_v3_runtime.py -q -k "native_route_arbitration"
15 passed, 125 deselected

.venv/bin/python -m pytest tests/models/test_lgrc_9_v3_contract.py tests/models/test_lgrc_9_v3_runtime.py -q -k "native_route or time_scopes_producer_reads or rejects_source_read_after_transport or topology_state_reabsorption_artifact_validator_reconstructs_chain"
41 passed, 222 deselected, 20 subtests passed

git diff --check
passed
```

## Claim Boundary

This is route-arbitration runtime support only. Movement, semantic choice,
agency, RC identity collapse, identity acceptance, locomotion-like, biological,
and unrestricted movement claims remain blocked.

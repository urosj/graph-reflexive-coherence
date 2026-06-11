# Phase 8 LGRC9 Time-Scoped Lineage Replay Plan

Status: Closed.

This continuation is opened by N04 Iteration 20. Iteration 20 showed that
runtime topology-state reabsorption can handle multiple committed topology
events in one run, but the artifact-only surface-lineage validator was too
global: it treated an earlier producer read as stale after a later topology
event transported the same source surface row.

## Goal

Make producer stale-read validation time-scoped:

```text
producer read is stale only if the referenced surface row was already
superseded or transported at the producer's scheduler/event time.
```

Later topology transports must not invalidate producer records that were valid
when they ran. Producer records after topology transport must still reference
the lineage-current transported successor.

## Non-Goals

- Do not change runtime producer behavior.
- Do not change packet budget semantics.
- Do not promote movement, choice, agency, identity, locomotion-like, or
  biological claims.
- Do not add native choice-selection policy.

## Iteration 73. Baseline And N04 Boundary

Freeze the N04 Iteration 20 blocker:

```text
multi_topology_event_time_scoped_producer_lineage_replay_blocked
```

Record that the runtime/budget path passed and artifact-only replay failed
only because the validator evaluated stale producer reads from final topology
state rather than producer-time state.

## Iteration 74. Time-Scoped Validator Semantics

Update `validate_lgrc9v3_causal_pulse_substrate_surface_lineage_artifacts` so
producer references are evaluated against lineage records with scheduler order:

- producer before later transport or supersession remains historically valid;
- producer at/after transport reading the stale source row fails;
- producer after transport reading transported successor passes;
- scheduled packet references and topology-state reabsorption digests remain
  validated by the existing artifact-only chain.

## Iteration 75. Closeout And N04 Return

Close the continuation when:

- focused validator regression tests pass;
- stale-read-after-transport controls still fail;
- N04 Iteration 20 reruns with multi-topology artifact replay passing;
- claim boundaries remain unchanged.

Return to N04 Iteration 21 after closeout.

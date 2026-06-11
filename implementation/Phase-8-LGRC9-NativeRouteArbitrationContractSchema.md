# Phase 8 LGRC9 Native Route Arbitration Contract Schema

Status: passed.

Iteration 77 adds the default-off native route-arbitration contract surface. It
does not emit candidate routes, arbitrate routes, commit topology events,
schedule packets, or promote movement/choice/agency claims.

## Default Flags

```text
native_lgrc_route_arbitration_enabled = false
native_lgrc_route_arbitration_policy = disabled
native_lgrc_route_arbitration_validated = false
native_lgrc_route_arbitration_supported = false
```

## Added Contract Artifacts

| Artifact | Kind | Digest |
|---|---|---|
| Candidate route | `lgrc9v3_native_route_candidate_record` | `candidate_route_digest` |
| Candidate set | `lgrc9v3_native_route_candidate_set_record` | `candidate_set_digest` |
| Route arbitration | `lgrc9v3_native_route_arbitration_record` | `native_route_arbitration_digest` |

Candidate sets and route-arbitration records also carry canonical
idempotency keys.

Candidate route digests in a candidate set are an ordered list, not accidental
container order. The order is governed by `candidate_set_order_key`. Supported
v1 order keys are:

```text
score_desc_then_candidate_id
digest_ascending
```

`digest_ascending` records must serialize route digests in sorted order. Other
order keys are deterministic policy orders and must be produced by the future
candidate emitter from runtime-visible score/order fields.

## Schema Guards

- Native route arbitration is default-off.
- Enabling requires LGRC-3 and `topology_changing_causal_history`.
- Enabling requires supported surface-lineage transport and topology-state
  reabsorption.
- Candidate scores must come from serialized, runtime-visible score
  components.
- Hidden fixture arrays, experiment `if/else`, preselected sinks, report code,
  and post-hoc thresholds are rejected as native route-arbitration inputs.
- Candidate budget predictions must preserve node-plus-packet accounting.
- Candidate lineage maps must be declared and cover transferred nodes.
- Route-arbitration records may select exactly one candidate for selected
  reason codes.
- Unresolved ties fail closed unless the serialized policy declares a
  deterministic runtime-visible tie-breaker.
- Claim-promotion fields are rejected, including semantic choice, agency, RC
  identity, topology-mutating movement, locomotion-like, biological, identity
  acceptance, and unrestricted movement flags.

## Verification

```text
.venv/bin/python -m pytest tests/models/test_lgrc_9_v3_contract.py -q
123 passed, 59 subtests passed

.venv/bin/python -m pytest tests/models/test_lgrc_9_v3_contract.py tests/models/test_lgrc_9_v3_runtime.py -q -k "native_route or time_scopes_producer_reads or rejects_source_read_after_transport or topology_state_reabsorption_artifact_validator_reconstructs_chain"
13 passed, 222 deselected, 20 subtests passed

git diff --check
passed
```

## Claim Boundary

This is runtime contract support only. Movement, semantic choice, agency, RC
identity collapse, identity acceptance, locomotion-like, biological, and
unrestricted movement claims remain blocked.

# Phase 8 LGRC9 Native Route Arbitration Closeout

Status: Closed.

Date: 2026-05-22.

## Summary

This continuation closes the N04 Iteration 21 runtime-support blocker:

```text
native_lgrc_topology_route_selection_not_exposed
```

LGRC9V3 now has default-off native route arbitration for LGRC-3 topology
work. The supported chain is:

```text
committed runtime evidence
-> candidate topology-route set
-> native route-arbitration record
-> selected topology event
-> surface lineage transport/supersession
-> topology-state reabsorption
-> producer scheduling from lineage-current reabsorbed state
-> step() processed packet work
```

This is runtime route arbitration support only. It does not promote semantic
choice, agency, RC identity collapse, identity acceptance, locomotion-like
behavior, biological behavior, unrestricted movement, or claim-promotion flags.

## Supported Capability

The closeout support capability is:

```text
native_lgrc_route_arbitration_supported = true
```

This means positive route-arbitration replay and the fail-closed control matrix
passed under the current artifact contract. It does not mean native choice or
semantic agency is validated.

The support gate requires:

- candidate route and candidate-set records from runtime-visible evidence;
- exactly one selected route from a native route-arbitration record;
- selected topology event backreferences to the arbitration record and digest;
- selected-event consumption by surface lineage and topology-state reabsorption;
- producer scheduling only from lineage-current, reabsorbed evidence;
- artifact-only replay with no private runtime state;
- distinct negative-control blockers for disabled policy, no candidates,
  unresolved tie, hidden input, budget mismatch, order inversion, duplicate
  arbitration, stale state, direct rewrite, and claim promotion.

## Verification

Focused model and telemetry closeout suite:

```text
.venv/bin/python -m pytest tests/models/test_lgrc_9_v3_runtime.py tests/models/test_lgrc_9_v3_contract.py tests/telemetry/test_lgrc9v3_contract.py -q
281 passed, 59 subtests passed
```

Route-arbitration runtime slice:

```text
.venv/bin/python -m pytest tests/models/test_lgrc_9_v3_runtime.py -q -k "native_route_arbitration"
26 passed, 125 deselected
```

Runtime suite:

```text
.venv/bin/python -m pytest tests/models/test_lgrc_9_v3_runtime.py -q
151 passed
```

Telemetry route-arbitration namespace:

```text
.venv/bin/python -m pytest tests/telemetry/test_lgrc9v3_contract.py -q
7 passed
```

Diff hygiene:

```text
git diff --check
passed
```

## Claim Boundary

The following remain false:

```text
semantic_choice_claim_allowed = false
native_lgrc_choice_selection_claim_allowed = false
agency_claim_allowed = false
rc_identity_collapse_claim_allowed = false
identity_acceptance_claim_allowed = false
locomotion_like_claim_allowed = false
biological_claim_allowed = false
unrestricted_movement_claim_allowed = false
```

## N04 Return

Return to:

```text
N04 Iteration 21-B: native LGRC route-arbitration rerun
```

The immediate N04 question is whether the previous Iteration 21 choice-boundary
probe can now be rerun with native route-arbitration records as the causal
selection source instead of experiment-side topology-event arguments.

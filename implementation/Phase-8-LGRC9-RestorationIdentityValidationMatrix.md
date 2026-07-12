# Phase 8 LGRC9 Restoration Identity Validation Matrix

Status: Passed; Iteration 93 complete, Iteration 94 closeout pending.

## Scope

This matrix validates `lgrc9v3_restoration_identity_v1` as a bounded native
restoration identity for supported LGRC9V3 snapshots. It does not require raw
snapshot equality and does not claim unrestricted behavioral equivalence.

Executable sources:

```text
tests/models/test_lgrc_9_v3_restoration_matrix.py
scripts/audit_lgrc9v3_restoration_identity_matrix.py
```

Retained RCAE source-fixture result:

```text
implementation/Phase-8-LGRC9-RestorationIdentityRCAEReplayMatrix.json
```

Artifact integrity:

```text
audit script:
  51c022184120019a0b55a165f21c34e602fd4d58bbbbfc4097f7daa418d0f593
local matrix tests:
  b5c740545022c3be11e256d95645b57954bce993a46e7cc26edcca33517eb154
RCAE replay matrix:
  a0ec3183fba78e21110a948cd349c380553383051cd3e6958d04618076bbc426
```

## Positive Matrix

| Check | Result |
|---|---|
| Composite identity before save equals identity after load | passed |
| Composite identity is fixed across three repeated native loads | passed |
| Current native LGRC runtime artifact remains exact | passed |
| LGRC events remain exact | passed |
| LGRC observables remain exact | passed |
| Equal-input continuation twins remain equivalent | passed |
| Repeated artifact and digest construction is deterministic | passed |
| Original RCAE C02 projection remains equal | passed |

The retained RCAE fixture produced four raw snapshot digests but one native
restoration identity digest:

```text
raw snapshots:
  37ac41bce4a0c8b4ae93bb0435b2abb0312e189b5d73380a46533b0ae5486a87
  bd316a368afc4728cd8a60b00abd1fdb3bd8deb1a45ba24c23fd9a5edfee6f9d
  efa8171d1c366fb23e2059c2c6418ba7a8c3f73a6e43dd119390159132c12e04
  bd316a368afc4728cd8a60b00abd1fdb3bd8deb1a45ba24c23fd9a5edfee6f9d

restoration identity, all four rows:
  4a48db62f9ab59b39fae8ecde7570afb3c07f30fe7208b39d74b934d83600301
```

## Sensitivity Matrix

Identity changed for every tested included-state mutation:

```text
topology payload
next stable allocation ID
node/basin state
base conductance
constitutive edge-label mode
potential
sink set
basin membership
budget target
remainder
RNG state
state-owned event log
state-owned observables
load-bearing cached quantity
LGRC event queue
LGRC scheduler clock
LGRC packet ledger
LGRC causal route
LGRC topology history
LGRC producer/cache record
source-current causal pulse surface
outer LGRC events
outer LGRC observables
```

The source-current surface row is generated through the native runtime API,
not inserted as a report label.

## Normalization Matrix

Identity remained stable for:

```text
undirected endpoint reversal plus nonzero signed-flux reversal
deterministic parameter-identity materialization
deterministic RNG materialization
declared budget-source materialization
mapping insertion-order reversal
basin-membership order reversal
raw duplicate base-event/base-observable view changes that the native loader
  does not restore as state
```

Signed zero outside oriented port-edge flux remained exact and changed the
identity. Version 1 therefore does not widen the I90 signed-zero exclusion.

## Compatibility Finding

I93 found one bounded implementation gap in the I92 composition path:
supported older LGRC runtime artifacts may omit logs that the native runtime
restorer deterministically materializes as empty. Copying the raw runtime
block caused identity to differ after load.

The correction remains LGRC-only:

```text
raw runtime artifact
  -> existing restore_lgrc9v3_runtime_state_artifact
  -> canonical to_artifact
  -> restoration identity
```

Current runtime artifacts remain exact at the JSON data level. Older
supported artifacts now reach the same identity as their restored models. No
loader, runtime-state, snapshot, GRC9V3, or abstract-interface code changed.

## Negative Controls

The following fail closed:

```text
missing embedded base state
wrong model family
malformed LGRC runtime artifact
raw snapshot digest as restoration identity
RCAE experiment projection as native identity
restoration identity as unrestricted behavioral equivalence
restoration identity as RC identity, selfhood, agency, or shared-medium proof
```

## Verification

```text
I93 matrix:
  19 passed, 5 subtests passed

I91-I93 focused matrix:
  235 passed, 25 subtests passed

core + models regression:
  857 passed, 260 subtests passed

RCAE retained replay:
  11 / 11 checks passed

ruff:
  passed

mypy:
  passed

git diff --check:
  passed
```

The earlier complete repository run remains affected only by absent,
gitignored discovery/telemetry session outputs. Core and model regressions are
fully green.

## I93 Classification

```text
restoration_identity_matrix_passed = true
lgrc9v3_restoration_identity_v1_candidate_supported_pending_closeout = true
lgrc9v3_restoration_identity_v1_supported = false
support_blocker = iteration_94_closeout_not_run
raw_snapshot_byte_identity_required = false
unrestricted_behavioral_equivalence = false
rc_identity_supported = false
selfhood_supported = false
agency_supported = false
native_shared_medium_supported = false
```

The final `supported = true` freeze and RCAE P2-I2 handoff remain Iteration 94
work.

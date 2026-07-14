# PyGRC Reset-Baseline Persistence Specification

Status: Implemented and validated as a repository-wide persistence-contract
correction.

This specification defines how PyGRC preserves the declared state used by
`reset()` across snapshot save/load. That baseline begins as construction-time
state and can be replaced only by explicit rebase. The contract applies to
`GRCV2`, `GRCV3`, `GRC9`, `GRC9V3`, and `LGRC9V3`.

It does not change GRC or LGRC dynamics. It changes which scientific lifecycle
state is persisted and how restoration identity accounts for that state.

## Problem

Before this contract, a constructed model retained its original
`_initial_state`, while `snapshot()` serialized only current state. `load()`
constructed a model from that current state, which implicitly made the loaded
checkpoint its new reset baseline.

Consequently, two models could have equal current-state restoration identity
and continue equally under the same inputs, yet diverge after `reset()`:

```text
constructed model reset -> original construction baseline
loaded model reset      -> saved checkpoint state
```

That behavior made reset semantics depend on whether a save/load boundary had
occurred.

## Required Lifecycle Semantics

For snapshots emitted under this contract:

```text
reset(before save) == reset(after load)
```

where equality is family-valid state equality under the persisted parameter
identity.

The lifecycle operations have distinct meanings:

```text
set_state(state)
  changes current state only
  preserves the existing reset baseline

rebase_reset_baseline()
  explicitly replaces the reset baseline with current state

reset()
  restores the persisted or explicitly rebased reset baseline
```

No implicit operation may rebase the baseline merely because current state was
replaced, saved, or loaded.

The common interface adds `rebase_reset_baseline()` as a non-abstract default
that raises `NotImplementedError`. This keeps existing third-party
`GRCModel` subclasses instantiable. All concrete PyGRC runtime families
implement the operation.

## Snapshot Group

The shared `pygrc.snapshot` version remains version 1. A new additive,
versioned top-level group carries reset lifecycle state:

```text
reset_baseline_schema = "pygrc.reset_baseline"
reset_baseline_version = 1
model_family = <outer model family>
status = "available" | "unavailable"
```

For `status = "available"`, the group contains:

```text
snapshot = <complete same-family baseline snapshot without reset_baseline>
```

The nested snapshot preserves the same family-specific state surface used for
ordinary persistence. It must:

- use the same model family as the outer snapshot;
- use the same `params_hash` as the outer snapshot;
- satisfy the shared snapshot contract; and
- omit its own `reset_baseline` group.

Recursive baseline nesting is forbidden.

For `status = "unavailable"`, the group contains:

```text
unavailable_reason = <non-empty compatibility reason>
```

and must not contain a baseline snapshot.

## Legacy Compatibility

Snapshots that predate this group remain loadable. Their current state remains
available for inspection and continuation. PyGRC must not silently claim that
the legacy checkpoint was the original construction baseline.

The loaded model therefore records:

```text
reset baseline status = unavailable
reason = legacy_snapshot_missing_reset_baseline
```

Calling `reset()` then fails with `SnapshotCompatibilityError` until the caller
explicitly invokes `rebase_reset_baseline()`.

If such a model is saved again before rebasing, its snapshot emits an explicit
`status = "unavailable"` group. Legacy absence is not converted into false
baseline provenance.

Malformed, recursive, wrong-family, or parameter-mismatched baseline data is
not legacy absence. It fails snapshot validation and load.

## Rebase Semantics And Provenance Boundary

Rebasing a legacy model is a prospective repair, not historical recovery:

```text
legacy current checkpoint
  -- explicit rebase_reset_baseline() -->
new declared reset baseline equal to that current checkpoint
```

After that operation, `reset()` is well-defined and later snapshots can carry
an available baseline. Subsequent save/load cycles can therefore preserve v2
restoration identity without requiring raw snapshot byte equality.

Rebasing does not:

- reconstruct the construction baseline omitted by the legacy snapshot;
- prove that the new baseline equals that historical baseline;
- retroactively make an earlier legacy artifact reset-complete;
- turn v1 into a reset-aware identity; or
- establish unrestricted behavioral equivalence.

The lifecycle/identity states are:

| Snapshot/model state | `reset()` | V1 identity | V2 identity | Baseline meaning |
| --- | --- | --- | --- | --- |
| Current snapshot with persisted baseline | available | available | available | Preserved construction or previously explicit baseline |
| Legacy snapshot before rebase | blocked | available | unavailable | Historical construction baseline unknown |
| Legacy snapshot after explicit rebase | available | available | available | New baseline explicitly adopted from current checkpoint |
| Rebased model after later save/load | available | available | available and expected stable | The explicitly adopted baseline, preserved prospectively |

Two models can therefore have equal v1 identity while:

- one has an available construction baseline and the other has none; or
- their available reset baselines differ.

In the first case v2 is unavailable for the baseline-missing model. In the
second case their v2 identities differ. If both models explicitly rebase to the
same current state, their later v2 identities may match, but that match proves
the same declared current/reset state only. It does not prove a shared
construction history.

The reset-baseline snapshot group identifies baseline state and availability;
it does not encode a complete operation history. A consumer that admits a
rebased legacy snapshot should separately record:

```text
reset_baseline_admission = explicit_rebase_from_legacy_checkpoint
historical_construction_baseline_recovered = false
```

## Restoration Identity Versions

`lgrc9v3_restoration_identity_v1` remains unchanged. It identifies current
scientific and continuation-relevant LGRC9V3 state and deliberately ignores the
new reset-baseline group.

The new contract is:

```text
lgrc9v3_restoration_identity_v2
```

Its payload includes:

```text
current_state_restoration_identity = lgrc9v3_restoration_identity_v1(current)
reset_baseline_restoration_identity = lgrc9v3_restoration_identity_v1(baseline)
```

V2 requires an available baseline. Legacy or explicitly unavailable baselines
cannot produce v2 identity.

This versioning preserves two distinct questions:

```text
v1: did save/load restore the same current scientific state?
v2: did save/load restore the same current scientific state and reset lifecycle?
```

Raw snapshot digests remain separately observable and are not either identity.

For a rebased legacy model, v2 provides a prospective restoration guarantee:
the declared current state and newly adopted reset baseline are represented by
the identity and should remain stable across subsequent save/load cycles. It
does not provide a retroactive guarantee about the missing historical baseline.
As with v1, bounded continuation or reset replay remains a separate validation
step when a downstream claim depends on behavior rather than state identity.

## Validation Requirements

The implementation is required to demonstrate:

- construction-baseline preservation for every concrete model family;
- current-state preservation at load;
- identical original/restored reset results;
- repeated save/load baseline preservation;
- `set_state()` baseline preservation;
- explicit rebase behavior;
- prospective v2 stability after legacy rebase and later save/load;
- no claim that rebase recovers historical construction provenance;
- legacy load plus fail-closed reset;
- malformed, recursive, wrong-family, and wrong-parameter rejection;
- unchanged LGRC9V3 v1 identity semantics;
- v2 sensitivity to reset-baseline differences; and
- deterministic canonical serialization of the new group.

## Claim Boundary

This contract supports:

```text
versioned PyGRC save/load preservation of current state and reset lifecycle
state, with explicit legacy compatibility and LGRC9V3 restoration identity v2
```

It does not support raw snapshot byte identity, unrestricted continuation
equivalence, semantic identity, selfhood, agency, ecology, native support, or
completion of Phase 8.

# PyGRC Reset-Baseline Persistence Plan

Status: Implemented.

Record class: Repository-wide implementation correction.

## Purpose

Correct the repository-wide save/load/reset contract so a loaded model resets
to the same declared reset baseline as the model that produced the snapshot.
That baseline is construction-time state unless an explicit rebase has
replaced it.

This is a core persistence correction across all concrete PyGRC families. It
is not a Phase 8 LGRC dynamics extension and does not modify GRC9V3 theory or
runtime equations.

## Scope

In scope:

- a shared versioned `reset_baseline` snapshot group;
- baseline restoration for `GRCV2`, `GRCV3`, `GRC9`, `GRC9V3`, and `LGRC9V3`;
- explicit `rebase_reset_baseline()` lifecycle operation;
- additive interface compatibility for third-party model subclasses;
- fail-closed legacy reset behavior;
- unchanged `set_state()` baseline semantics;
- LGRC9V3 restoration identity v2;
- compatibility, sensitivity, and regression tests; and
- RCAE re-admission guidance.

Out of scope:

- changes to GRC/LGRC evolution equations;
- event, producer, topology, or basin policy changes;
- forcing raw snapshot or re-snapshot byte identity;
- changing the meaning of `lgrc9v3_restoration_identity_v1`;
- treating a legacy checkpoint as an original baseline; and
- modifying RCAE from this repository.

## Work Packages

### 1. Shared Contract

Add the versioned group schema, canonical builder, validator, and reader.
Require same-family, same-parameter, non-recursive nested snapshots.

### 2. Family Integration

Persist and restore the baseline in every concrete runtime family. Preserve
baseline under `set_state()`. Make rebasing explicit. Keep legacy snapshots
loadable while making baseline absence visible and reset fail closed.
Treat legacy rebasing as explicit adoption of a new baseline, not recovery of
the omitted construction baseline. Preserve that distinction in downstream
handoff language.

### 3. Identity Versioning

Freeze v1 semantics. Add v2 as composition of current-state v1 identity and
baseline-state v1 identity. Reject v2 when baseline provenance is unavailable.

### 4. Verification

Test all families, repeated cycles, legacy compatibility, malformed data,
parameter mismatch, v1 stability, v2 sensitivity, targeted lint, and
regression. Verify prospective v2 stability without claiming historical
baseline recovery.

### 5. Handoff

Document that RCAE P2-I2 should explicitly adopt v2 through a graph revision
and provider-schema transition. No silent fallback to v1 or the C02 projection
is allowed when reset-equivalent restoration is required. If RCAE consumes a
legacy checkpoint through explicit rebase, require it to distinguish that new
declared baseline from a directly persisted construction baseline and to keep
historical-baseline recovery false.

## Acceptance State

The tranche is complete when:

```text
all_concrete_families_preserve_reset_baseline = true
set_state_implicitly_rebases = false
explicit_rebase_available = true
legacy_rebase_creates_new_declared_baseline = true
legacy_rebase_recovers_historical_baseline = false
post_rebase_v2_guarantee_is_prospective = true
equal_v2_implies_equal_construction_history = false
legacy_snapshots_loadable = true
legacy_reset_without_rebase_allowed = false
malformed_baseline_fails_closed = true
lgrc9v3_identity_v1_redefined = false
lgrc9v3_identity_v2_supported = true
runtime_dynamics_changed = false
```

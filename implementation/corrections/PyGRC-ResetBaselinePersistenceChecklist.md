# PyGRC Reset-Baseline Persistence Checklist

Status: Complete.

Record class: Repository-wide implementation correction.

## Shared Contract

- [x] Add `pygrc.reset_baseline` version 1 schema constants.
- [x] Add the group to canonical snapshot ordering.
- [x] Support explicit `available` and `unavailable` states.
- [x] Reject recursive baseline snapshots.
- [x] Reject family mismatch.
- [x] Reject parameter-identity mismatch.
- [x] Preserve legacy top-level snapshots without the group.

## Runtime Families

- [x] Persist and restore the GRCV2 baseline.
- [x] Persist and restore the GRCV3 baseline.
- [x] Persist and restore the GRC9 baseline.
- [x] Persist and restore the GRC9V3 baseline.
- [x] Persist and restore the LGRC9V3 baseline.
- [x] Preserve baseline under `set_state()`.
- [x] Add explicit `rebase_reset_baseline()`.
- [x] Keep the new common-interface method non-abstract for additive subclass compatibility.
- [x] Fail `reset()` when legacy baseline provenance is unavailable.
- [x] Preserve unavailable provenance through a later save/load cycle.
- [x] Define legacy rebase as adoption of a new baseline, not historical recovery.

## Restoration Identity

- [x] Keep `lgrc9v3_restoration_identity_v1` unchanged.
- [x] Add `lgrc9v3_restoration_identity_v2`.
- [x] Add its canonical digest helper.
- [x] Include both current-state and reset-baseline v1 identities.
- [x] Reject v2 when the baseline is unavailable.
- [x] Record that v1 equality does not imply equal reset behavior.
- [x] Record that post-rebase v2 is prospective, not retroactive provenance proof.

## Verification

- [x] Test every concrete model family.
- [x] Test current-state preservation and equal reset results.
- [x] Test repeated save/load cycles.
- [x] Test `set_state()` and explicit rebase semantics.
- [x] Test legacy loading and fail-closed reset.
- [x] Test malformed, recursive, wrong-family, and wrong-parameter baselines.
- [x] Test v1 invariance and v2 sensitivity.
- [x] Test v2 stability across a later save/load cycle.
- [x] Update prior snapshot-shape assertions.
- [x] Run targeted lint and tests.
- [x] Run core/model regressions.

## Documentation And Handoff

- [x] Add the core reset-baseline persistence specification.
- [x] Update the common runtime interface.
- [x] Update LGRC9V3 restoration identity documentation.
- [x] Record that the correction is outside Phase 8 dynamics scope.
- [x] Add explicit RCAE P2-I2 re-admission instructions.
- [x] Require legacy-rebase admission to remain distinct from persisted construction provenance.
- [x] Record that equal post-rebase v2 does not prove common construction history.
- [x] Update the changelog.

## Closeout State

```text
reset_baseline_persistence_supported = true
supported_model_families = GRCV2, GRCV3, GRC9, GRC9V3, LGRC9V3
lgrc9v3_restoration_identity_v1_supported_unchanged = true
lgrc9v3_restoration_identity_v2_supported = true
legacy_snapshot_current_state_load_supported = true
legacy_snapshot_reset_supported_without_explicit_rebase = false
legacy_rebase_creates_new_declared_baseline = true
legacy_rebase_recovers_historical_construction_baseline = false
post_rebase_v2_is_prospective_restoration_identity = true
equal_post_rebase_v2_proves_common_construction_history = false
consumer_must_disclose_explicit_legacy_rebase = true
raw_snapshot_byte_identity_required = false
runtime_dynamics_changed = false
phase8_semantics_changed = false
```

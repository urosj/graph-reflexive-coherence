# Phase 8 LGRC9 Restoration Identity Closeout

Status: Closed.

Date: 2026-07-12.

## Result

Iterations 90-94 close the bounded additive restoration-identity tranche:

```text
lgrc9v3_restoration_identity_v1_supported = true
raw_snapshot_byte_identity_required = false
snapshot_schema_changed = false
runtime_behavior_changed = false
old_snapshots_loadable = true
equal_input_continuation_validated = true
rcae_p2_i2_native_identity_handoff_ready = true
```

The public API is:

```python
from pygrc.models import (
    digest_lgrc9v3_restoration_identity_v1,
    lgrc9v3_restoration_identity_v1,
)
```

Both helpers accept an `LGRC9V3` model or a complete LGRC9V3
`pygrc.snapshot` version 1 mapping. A plain GRC9V3 snapshot remains loadable
as GRC9V3 but is not accepted by this LGRC-specific identity helper.

## What The Identity Means

The identity composes:

```text
LGRC9V3-owned canonical projection of embedded GRC9V3 state
+ canonical native LGRC9V3 runtime artifact
+ events
+ observables
```

Current runtime artifacts remain exact. Older supported LGRC9V3 version 1
snapshots may omit later-added deterministic empty logs; those artifacts reach
the same identity through the existing, unchanged runtime-state restorer.

This is a restoration identity, not a raw-file identity. The retained RCAE
fixture produced three raw snapshot digests across repeated native loads while
all representations produced one identity digest. The identity is a fixed
point even though raw representation cycling remains observable.

## Validation Scope

The matrix validates:

- before-save versus after-load identity equality;
- repeated-load identity fixed point;
- exact current LGRC runtime artifacts;
- event and observable preservation;
- sensitivity to included scientific and continuation state;
- invariance under declared representation normalization;
- old supported snapshot loading;
- malformed and wrong-family fail-closed controls; and
- equal-input continuation for the retained RCAE branch and a local
  queued-arrival twin.

This is bounded continuation validation. It does not establish unrestricted
behavioral equivalence for arbitrary future inputs, policies, or external
state.

## C01 And C02

The source classifications do not change:

```text
C01 = bounded incomplete because its raw full-snapshot equality predicate was
      broader than the scientific restoration question

C02 = passed with an RCAE-owned versioned restoration projection and bounded
      equal-input continuation
```

I94 does not retroactively turn the C02 projection into native PyGRC evidence.
It adds a new library-owned identity that later work may adopt explicitly.

## RCAE P2-I2 Return

P2-I1 remains unchanged. P2-I2 may use the new identity only through an
explicit realization-profile transition:

```text
previous provider = RCAE C02 restoration projection
new provider = pygrc.models.lgrc9v3_restoration_identity_v1
silent upgrade = forbidden
```

RCAE-owned medium, pool, intervention, and other external experiment state
remain outside native PyGRC identity and must be composed separately.

The versioned C02 projection remains a valid fallback for older graph
revisions or environments where the native helper is unavailable. That
fallback may not be relabeled as native PyGRC identity.

## Verification

```text
I93 matrix: 19 passed, 5 subtests passed
I91-I93 focused matrix: 235 passed, 25 subtests passed
core + models regression: 857 passed, 260 subtests passed
RCAE retained replay: 11 / 11 checks passed
ruff: passed
mypy: passed
```

The earlier repository-wide run recorded `1621 passed, 741 subtests passed,
25 failed`; all 25 failures were missing gitignored output prerequisites and
were not restoration-identity failures.

## Claim Boundary

The strongest supported claim is:

```text
versioned PyGRC restoration identity for supported LGRC9V3 snapshots,
including a read-only embedded-GRC9V3 state component, with bounded
continuation validation
```

The closeout does not support raw snapshot byte identity, unrestricted
continuation equivalence, RC identity, selfhood, identity acceptance, agency,
native shared-medium organization, ecology, organism/life, or completion of
Phase 8 as a whole.

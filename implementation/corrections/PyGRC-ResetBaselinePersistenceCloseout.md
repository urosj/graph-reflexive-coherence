# PyGRC Reset-Baseline Persistence Closeout

Status: Closed.

Record class: Repository-wide implementation correction.

Date: 2026-07-14.

## Result

PyGRC snapshots now preserve both current state and the declared baseline used
by `reset()` across save/load for every concrete runtime family. The declared
baseline is construction-time state unless it has been explicitly rebased.

```text
reset_baseline_persistence_supported = true
set_state_preserves_baseline = true
explicit_rebase_supported = true
legacy_snapshot_current_state_load_supported = true
legacy_reset_without_explicit_rebase = false
lgrc9v3_restoration_identity_v1_redefined = false
lgrc9v3_restoration_identity_v2_supported = true
runtime_dynamics_changed = false
```

## Compatibility Policy

New snapshots contain a versioned `reset_baseline` group. Legacy snapshots
remain loadable as current-state checkpoints, but PyGRC does not invent their
missing construction provenance. `reset()` fails closed until the caller
explicitly rebases.

Malformed baseline data is not treated as legacy data. Family mismatch,
parameter mismatch, recursion, or invalid nested snapshot shape rejects the
snapshot.

## Identity Policy

V1 continues to answer current-state restoration equality. V2 answers current
state plus reset-lifecycle equality. Raw snapshot digests remain separate.

The versions identify different scientific state surfaces; they are not two
different reset implementations:

| Contract state | V1 | V2 | `reset()` after load |
| --- | --- | --- | --- |
| Current snapshot with persisted baseline | available | available | restores the persisted construction or explicitly rebased baseline |
| Legacy snapshot before explicit rebase | available | unavailable | blocked because baseline provenance is absent |
| Legacy snapshot after explicit rebase | available | available | restores the newly declared checkpoint baseline |

Equal v1 identity does not imply equal reset behavior. Equal v2 identity means
equal declared current state and reset-baseline state under the versioned
identity projection. It does not imply raw snapshot-byte equality,
construction-history equality, or unrestricted behavioral equivalence.

## Rebase Guarantee Boundary

For a legacy snapshot with current checkpoint `C` and omitted historical
construction baseline `H`, the state transition is:

```text
before explicit rebase:
  current state = C
  historical reset baseline = unknown
  v1(C) = available
  v2 = unavailable
  reset() = blocked

after rebase_reset_baseline():
  current state = C
  newly declared reset baseline = C
  v1(C) = available
  v2(C, C) = available
  reset() = restores C

after later evolution to D and save/load:
  current state = D
  declared reset baseline = C
  v2(D, C) = expected stable across restoration
  reset() = restores C
```

This is a prospective lifecycle repair. It guarantees that the explicitly
adopted baseline is represented, persisted, and restored by later snapshots.
It does not:

- recover `H` from a legacy artifact that never serialized it;
- prove that `C == H`;
- retroactively make the original legacy snapshot reset-complete;
- establish that independently rebased models share construction history;
- redefine v1 as reset-aware; or
- replace behavioral replay when a claim depends on continuation or reset
  behavior rather than state identity.

Therefore a rebased legacy model can earn v2 identity only for the declared
post-rebase lifecycle. The guarantee begins at the explicit rebase operation;
it does not reach backward into unknown provenance.

## RCAE Return

Before RCAE P2-I2 proceeds, the affected I02 lane should be reopened through a
named re-admission record that declares:

```text
graph_revision = <revision containing this closeout>
restoration_identity_provider = pygrc.models.lgrc9v3_restoration_identity_v2
restoration_identity_schema = lgrc9v3_restoration_identity_v2
previous_C02_projection_silently_upgraded = false
v1_used_as_reset_equivalent_identity = false
reset_baseline_admission = persisted_construction_baseline | explicit_rebase_from_legacy_checkpoint
historical_construction_baseline_recovered = false
post_rebase_v2_used_prospectively = true | not_applicable
```

RCAE should rerun current-state, reset-equivalence, repeated save/load, and
affected continuation checks before starting I03. RCAE-owned medium, pool,
intervention, and experiment state remains outside the PyGRC identity and must
still be composed separately.

When RCAE admits a rebased legacy checkpoint, it should select
`explicit_rebase_from_legacy_checkpoint`, set historical recovery to `false`,
and keep that provenance distinct from a current snapshot that directly
persisted its construction baseline. Equal v2 digests after rebase do not erase
that admission distinction.

## Verification

```text
cross-family reset/identity contract: 49 passed, 27 subtests passed
affected persistence/runtime matrix: 99 passed, 52 subtests passed
core + models regression: 868 passed, 284 subtests passed
compileall: passed
ruff over changed Python files: passed
git diff --check: passed
```

The repository-wide lint/type backlog outside the changed files is not part of
this closeout. No unrelated cleanup is counted as reset-baseline evidence.

## Claim Boundary

This closeout establishes a persistence and restoration-identity contract. It
does not change GRC/LGRC mechanics or support semantic identity, selfhood,
agency, ecology, native support, or Phase 8 completion.

# B1-GR GRV2 Strong Formed Branches

## Result

```text
gate = GRV2
mechanical_status = passed
scientific_acceptance = awaiting_human_review
candidate_closeout_ceiling = GRV-C3
positive_branch_evidence_candidate = true
positive_evidence_opened = false_pending_human_acceptance
causal_strong_branch = deferred_to_GRV3
continuation = unsupported
retention = unsupported
readback = unsupported
writeback = unsupported
runtime_change_authorized = false
```

GRV2 certifies formed fixed-branch candidates against the unchanged public
`GRC9V3.step()` and a fresh staged replay of every load-bearing runtime stage.
A formed branch is a state that remains physically fixed under this bounded
runtime envelope. Its existence does not show that a perturbation continues,
is retained, is read later, or writes back into the substrate.

## Search Accounting

- `F1`: 16 rows, 16 accepted branch rows, 0 rejected rows, nonuniform found = `false`.
- `F2`: 64 rows, 16 accepted branch rows, 48 rejected rows, nonuniform found = `true`.
- `F3`: 64 rows, 16 accepted branch rows, 48 rejected rows, nonuniform found = `true`.

The nonuniform search is bounded to the committed seed, parameter, solver,
and compute envelope. Rejected rows and an absent family would not establish
global nonexistence.

## Certification

- Accepted branch rows: `48`
- Held-out fresh-process rows: `3` (all passed)
- Symmetry/port controls: `9` (all passed)
- Budget correction is a numerical no-op on every accepted branch.
- Every accepted branch emits no event and preserves topology.
- Every accepted branch passes save/load and one-step replay.
- Every accepted branch passes raw-to-canonical load-bearing-state admission,
  authoritative zero-current/conductance checks, and explicit budget active-set controls.
- Every accepted branch passes the declared four-beat unperturbed physical hold; maximum cumulative physical `L_inf` = `6.537703711728682e-10`.
- Accepted rows occupy `32` symmetry orbits; row count is not claimed as an independent-branch count.
- Zero-current branches lie on a basin/sink identity boundary; GRV3 must
  admit a causal stratum before any causal-branch upgrade or derivative claim.
- Cache refresh and complete causal-state closure remain GRV3 debt; the hold is
  not a stability, retention, continuation, or causal fixed-state test.

## Claim Boundary

This result supports only a provisional candidate for the existence and local
source identity of GRC formed fixed branches. `causal_strong_branch` remains
deferred to GRV3. No continuation, retention, read-back, write-back, memory,
learning, agency, organism, or life claim follows from GRV2.

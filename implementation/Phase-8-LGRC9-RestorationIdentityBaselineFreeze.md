# Phase 8 LGRC9 Restoration Identity Baseline Freeze

Status: passed.

Iteration 90 freezes current LGRC9V3 restoration behavior before the additive
identity implementation begins.

Machine record:

- [`Phase-8-LGRC9-RestorationIdentityBaselineFreeze.json`](./Phase-8-LGRC9-RestorationIdentityBaselineFreeze.json)

## Boundary

RCAE P2-I1 C01 compared complete native snapshots across save/load and stopped
before scientific execution. C02 replaced that experiment predicate with a
fixture-bounded projection plus equal-input continuation twins.

Iteration 90 reproduces the same branch point from the retained RCAE fixture:

```text
fixture = P-W-A-B
seed = 211
cell = candidate-conditioning
window = post-writer feedback-surface branch point
```

RCAE is consumed read-only as the fixture and gap source. Its C02 projection
does not define the native PyGRC identity.

## First Native Load

Raw snapshot digests differ:

```text
before save       37ac41bce4a0c8b4ae93bb0435b2abb0312e189b5d73380a46533b0ae5486a87
after first load  bd316a368afc4728cd8a60b00abd1fdb3bd8deb1a45ba24c23fd9a5edfee6f9d
```

The type- and signed-zero-sensitive comparison finds seven canonical leaves:

| Path suffix | Before | After | Classification |
| --- | --- | --- | --- |
| `cached_quantities.budget_target_source` | absent | `explicit_state` | deterministic default materialization |
| `params_identity` | `null` | resolved digest | deterministic identity materialization |
| `port_edges.1.flux_uv` | `+0.0` | `-0.0` | signed zero from endpoint canonicalization |
| `port_edges.1.node_u` | `1` | `0` | undirected endpoint canonicalization |
| `port_edges.1.node_v` | `0` | `1` | undirected endpoint canonicalization |
| `dynamics.state.rng_state` | `null` | deterministic RNG state | deterministic RNG materialization |
| `metadata.rng_state` | absent | deterministic RNG state | deterministic RNG metadata materialization |

C01 reported six leaves because ordinary Python equality treats `+0.0` and
`-0.0` as equal. Canonical JSON preserves their textual distinction, so their
digests differ.

## Repeated-Load Representation Cycle

Repeated native loads do not reach a raw canonical fixed point for this
fixture:

```text
after first load   bd316a368afc4728cd8a60b00abd1fdb3bd8deb1a45ba24c23fd9a5edfee6f9d  (-0.0)
after second load  efa8171d1c366fb23e2059c2c6418ba7a8c3f73a6e43dd119390159132c12e04  (+0.0)
after third load   bd316a368afc4728cd8a60b00abd1fdb3bd8deb1a45ba24c23fd9a5edfee6f9d  (-0.0)
```

The sole repeated-load difference is:

```text
caches.base_grc9v3_snapshot.dynamics.state.port_edges.1.flux_uv
```

Python value equality still passes because `-0.0 == +0.0`. The raw digest
cycle is representation-level zero-sign orientation, not evidence of changed
flux magnitude or direction.

This result tightens the extension contract:

```text
raw snapshot fixed point = observed but not required
restoration identity fixed point = required in Iteration 93
```

No GRC9V3 correction is opened. The LGRC9V3 identity projection must collapse
signed zero canonically without mutating the embedded substrate.

## Preserved State

Across the first load, all outer scientific groups compare exactly:

```text
metadata = equal
topology = equal
basin_attributes = equal
edge_labels = equal
dynamics.lgrc9v3_runtime = equal
observables = equal
events = equal
```

The exact LGRC9V3 runtime artifact is preserved. The RCAE C02 projection also
compares equal, as expected. Iteration 90 therefore reproduces no lost
scientific state in this tested path, while making no general unrestricted
continuation-equivalence claim.

## Public Surface Baseline

Before implementation:

```text
lgrc9v3_restoration_identity_v1 = absent
general GRC9V3 restoration identity API = absent and out of scope
raw snapshot digest = present
native LGRC9V3 save/load = present
bounded continue-after-load tests = present
```

## Change Boundary

Iteration 90 opens no source changes:

```text
git diff --name-only HEAD -- src tests examples
    no output
```

Iteration 91 remains LGRC-only. Its initial source envelope is:

```text
src/pygrc/models/lgrc_9_v3_restoration.py
src/pygrc/models/lgrc_9_v3_runtime.py
src/pygrc/models/__init__.py
tests/models/test_lgrc_9_v3_runtime.py
specs/lgrc-9-v3-spec.md
specs/lgrc-9-v3-restoration-identity.md
docs/reference/LGRC9V3-CausalHistory-ReferenceGuide.md
```

Protected invariants include:

- unchanged `src/pygrc/models/grc_9_v3.py` and GRC9V3 public API;
- unchanged GRC9V3 behavior and snapshot output;
- unchanged LGRC9V3 snapshot schema, loader, and runtime dynamics;
- unchanged packet/node budget and event/topology ordering; and
- old snapshot compatibility.

## Verification

```text
.venv/bin/python scripts/audit_lgrc9v3_restoration_baseline.py
    passed
    seven first-load canonical differences
    one signed-zero repeated-load representation cycle

.venv/bin/python -m pytest \
  tests/core/test_serialization_contract.py \
  tests/models/test_grc_9_v3_state.py \
  tests/models/test_lgrc_9_v3_runtime.py -q
    203 passed, 17 subtests passed

git diff --check
    passed
```

## Claim Boundary

Iteration 90 is baseline evidence only. Restoration identity is not yet
implemented or supported. Raw byte identity, unrestricted continuation
equivalence, RC identity, selfhood, identity acceptance, agency, native shared
medium, ecology, organism/life, and Phase 8 completion remain unsupported.

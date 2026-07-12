# Phase 8 LGRC9 Restoration Identity Checklist

This checklist tracks:

- [`Phase-8-LGRC9-RestorationIdentityPlan.md`](./Phase-8-LGRC9-RestorationIdentityPlan.md)
- [`../specs/lgrc-9-v3-restoration-identity.md`](../specs/lgrc-9-v3-restoration-identity.md)

## Ground Rules

- [x] Treat C01 as an over-broad RCAE equality predicate, not evidence of lost
  scientific state in its tested continuation.
- [x] Treat C02 as fixture-bounded evidence, not the general PyGRC identity
  definition.
- [x] Keep raw snapshot identity distinct from restoration identity.
- [x] Keep restoration identity distinct from bounded continuation replay.
- [x] Include embedded GRC9V3 state through an LGRC9V3-owned read-only
  projection.
- [x] Keep GRC9V3 source, behavior, and public API outside Phase 8 changes.
- [x] Do not exclude the complete nested base snapshot merely because it is
  stored under `caches`.
- [x] Preserve snapshot format, loader behavior, runtime dynamics, budgets,
  topology semantics, events, observables, and compatibility.
- [x] Keep external ecology medium/pool state outside native PyGRC identity.
- [x] Keep RC identity, selfhood, identity acceptance, agency, ecology, and
  Phase 8 completion claims blocked.

## Iteration 90. Baseline And Contract Freeze

Status: pending.

### Documentation Definition

- [x] Add the dedicated restoration-identity specification.
- [x] Define raw snapshot identity versus restoration identity.
- [x] Define LGRC9V3 ownership and the read-only GRC9V3 boundary.
- [x] Define explicit inclusion and exclusion policy.
- [x] Define compatibility and claim boundaries.
- [x] Define the P2-I2 adoption/fallback decision boundary.

### Baseline Work

- [ ] Record exact source revision and clean-worktree state.
- [ ] Reproduce the C01 fixture observation against current source.
- [ ] Record raw before/after snapshot digests.
- [ ] Record recursive difference paths and values.
- [ ] Confirm exact LGRC runtime-artifact equality.
- [ ] Confirm outer topology, basin attributes, edge labels, events, and
  observables agree.
- [ ] Confirm existing bounded continue-after-load tests pass.
- [ ] Test and record second-load normalization fixed point.
- [ ] Confirm no restoration-identity public callable exists.
- [ ] Record source diff outside implementation/spec records as empty.
- [ ] Write baseline freeze JSON and Markdown artifacts.

### Required Baseline Artifacts

```text
implementation/Phase-8-LGRC9-RestorationIdentityBaselineFreeze.json
implementation/Phase-8-LGRC9-RestorationIdentityBaselineFreeze.md
```

## Iteration 91. Embedded GRC9V3 State Projection

Status: pending.

- [ ] Freeze exact public callable names and artifact schema.
- [ ] Add the internal `lgrc9v3_embedded_grc9v3_state_v1` component.
- [ ] Include canonical resolved parameter identity.
- [ ] Include complete topology and stable allocation state.
- [ ] Include node, basin, hierarchy, and expansion state.
- [ ] Include canonical port edges with signed flux orientation.
- [ ] Include analytic edge labels and constitutive modes.
- [ ] Include potential, sink set, and basin membership.
- [ ] Include choice and collapse registries.
- [ ] Include step/time, budget target, and remainder.
- [ ] Include RNG state and parameter identity after deterministic
  normalization.
- [ ] Include base-state events and observables represented by current GRC9V3
  state.
- [ ] Include load-bearing/evidence-bearing cached quantities and coarse state.
- [ ] Record every representation-only exclusion explicitly.
- [ ] Confirm identity construction does not mutate model or snapshot input.
- [ ] Reject malformed and wrong-family inputs.
- [ ] Add deterministic artifact and digest tests.
- [ ] Confirm `src/pygrc/models/grc_9_v3.py` is unchanged.
- [ ] Confirm GRC9V3 public exports are unchanged.
- [ ] Confirm GRC9V3 behavior and snapshot outputs are unchanged.

## Iteration 92. LGRC9V3 Composite Restoration Identity

Status: pending.

- [ ] Add `lgrc9v3_restoration_identity_v1`.
- [ ] Consume the internal embedded-GRC9V3 state component.
- [ ] Include the exact LGRC runtime artifact.
- [ ] Include LGRC event state.
- [ ] Include LGRC observables.
- [ ] Include source snapshot schema/version provenance.
- [ ] Include explicit inclusion/exclusion manifest.
- [ ] Keep raw snapshot digest outside the identity digest.
- [ ] Export the concrete helper through the public models facade.
- [ ] Do not change the abstract `GRCModel` interface.
- [ ] Do not change `snapshot()`, `save()`, or `load()` payload or behavior.
- [ ] Add deterministic repeated-construction tests.

## Iteration 93. Replay, Sensitivity, And Compatibility Matrix

Status: pending.

### Positive Matrix

- [ ] `identity(before_save) == identity(after_load)`.
- [ ] Native LGRC runtime artifacts remain exact.
- [ ] Events and observables remain exact.
- [ ] Equal-input continuation twins remain equivalent.
- [ ] Repeated identity construction is deterministic.
- [ ] First restored snapshot is a second-load fixed point.

### Sensitivity Matrix

- [ ] Topology mutation changes identity.
- [ ] Stable allocation-ID mutation changes identity.
- [ ] Node/basin mutation changes identity.
- [ ] Nonzero signed port-edge flux mutation changes identity.
- [ ] Edge-label or constitutive-mode mutation changes identity.
- [ ] Potential, sink-set, or basin-membership mutation changes identity.
- [ ] Budget target or remainder mutation changes identity.
- [ ] RNG mutation changes identity.
- [ ] Event or observable mutation changes identity.
- [ ] LGRC queue, clock, ledger, surface, topology-history, route, or producer
  mutation changes identity.
- [ ] A mutation hidden under a cache container still changes identity when
  that field is load-bearing or evidence-bearing.

### Normalization Controls

- [ ] Equivalent undirected endpoint reversal plus signed-flux reversal keeps
  identity stable.
- [ ] Deterministic parameter-identity materialization keeps identity stable.
- [ ] Deterministic RNG materialization keeps identity stable.
- [ ] Declared budget-source materialization keeps identity stable.
- [ ] Mapping/set insertion-order changes keep identity stable.

### Compatibility And Negative Controls

- [ ] Old supported GRC9V3 snapshots remain loadable.
- [ ] Old supported LGRC9V3 snapshots remain loadable.
- [ ] Raw full-snapshot digest remains observable and may differ.
- [ ] Missing included state fails closed.
- [ ] Wrong model family fails closed.
- [ ] Malformed runtime artifact fails closed.
- [ ] Raw digest cannot be relabeled as restoration identity.
- [ ] Experiment projection cannot be relabeled as native identity.
- [ ] Equal restoration identity cannot be relabeled as unrestricted
  behavioral equivalence.
- [ ] Full focused and regression suites pass.
- [ ] `git diff --check` passes.

## Iteration 94. Closeout And RCAE Return

Status: pending.

- [ ] Produce closeout JSON and Markdown artifacts.
- [ ] Record exact supported snapshot families and versions.
- [ ] Record exact identity schema version and public callable paths.
- [ ] Record raw snapshot identity as separate observational data.
- [ ] Record normalization fixed-point status.
- [ ] Record bounded continuation-validation scope.
- [ ] Record old-snapshot compatibility status.
- [ ] Confirm snapshot schema unchanged.
- [ ] Confirm runtime behavior unchanged.
- [ ] Confirm C01/C02 classifications unchanged.
- [ ] Record explicit P2-I2 realization-profile transition requirements.
- [ ] Record the C02 projection fallback if native identity cannot close
  without broad redesign.
- [ ] Update Phase 8 plan, checklist, handoff, specs, and reference guide.
- [ ] Keep all unsafe claim flags false.

## Unsafe Claim Flags

The closeout must force false:

```text
raw_snapshot_byte_identity_required
unrestricted_continuation_equivalence
rc_identity_supported
selfhood_supported
identity_acceptance_supported
agency_supported
native_shared_medium_supported
ecology_supported
organism_or_life_supported
phase8_complete
```

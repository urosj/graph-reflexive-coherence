# N12 Native Naturalization And Producer Dissolution Implementation Checklist

This checklist tracks implementation of
`2026-06-N12-lgrc-native-naturalization-and-producer-dissolution`.

Status keys:

```text
Pending     not started
In Progress work has begun
Complete    implemented, run, and recorded
Blocked     cannot proceed without a decision or upstream result
Deferred    intentionally postponed
```

## Global Constraints

- [ ] Keep N12 as a bridge experiment, not an agency claim experiment.
- [ ] Keep N12 experiment-local unless a separate Phase 8/core task is opened.
- [ ] Stop before changing `src/*`.
- [ ] If Phase 8 is opened later, inspect `src/pygrc/telemetry` as a first-class
      native surface namespace.
- [ ] Treat N11 GALI7 as artifact-only source evidence, not native support.
- [ ] Treat N05-N11 producer-layer evidence as scaffolding until Phase 8
      implements and validates native support.
- [ ] Preserve compatibility with RC causality, coherence, LGRC geometry,
      packet scheduling, topology lineage, and budget conservation.
- [ ] Reject candidate rows that require non-RC quantities.
- [ ] Require `non_rc_quantity_audit` for every candidate row.
- [ ] Treat `phase8_ready` as derived from `nat_level = NAT4`, not as a
      competing primary class.
- [ ] Keep `NAT` levels as naturalization/readiness classifications, not agency
      or native support flags.
- [ ] Record source artifacts, source reports, and SHA-256 digests for every
      accepted N12 inventory row.
- [ ] Split essential producer decisions from bookkeeping fields for every
      candidate row.
- [ ] Preserve separated memory, proxy, support, route, artifact replay, and
      node-plus-packet budget surfaces.
- [ ] Require artifact-only replay or source-current reconstruction gates where
      applicable.
- [ ] Block hidden producer mutation, stale source use, native relabeling,
      budget ambiguity, and claim promotion with distinct blockers.
- [ ] Keep route conductance memory distinct from intention, ACO, or ant-colony
      behavior.
- [ ] Keep response magnitude policy distinct from intention or semantic goal
      ownership.
- [ ] Keep support survival distinct from identity acceptance.
- [ ] Keep native integration meta-policy deferred until component native
      policies exist and pass validators.
- [ ] Do not promote agency, intention, semantic goal ownership, identity
      acceptance, biological behavior, personhood, unrestricted agency, or
      fully native agentic-like integration claims.
- [ ] Record exact replay commands for every generated artifact.
- [ ] Before closing any file-editing turn, run `git diff --check`.
- [ ] Before closing any file-editing turn, run `git diff -- src`.

## Iteration 0. Planning And Stubs

Status: Complete.

- [x] Create N12 experiment root.
- [x] Create N12 root README.
- [x] Create implementation README.
- [x] Create implementation plan.
- [x] Create implementation checklist.
- [x] Create `configs/`, `outputs/`, `reports/`, `scripts/`, and
      `hypotheses/` stubs.
- [x] Record N12 as a bridge experiment.
- [x] Record N12 as Phase 8 gate definition, not Phase 8 implementation.
- [x] Record the local `NAT0-NAT6` naturalization ladder.
- [x] Record N12's target as `NAT4`, not `NAT6`.
- [x] Record N11 GALI7 as the direct source boundary.
- [x] Record Hypothesis A/B/C split.
- [x] Record concrete Hypothesis B candidate seeds.
- [x] Record theory-sensitive Hypothesis C blocker seeds.
- [x] Record claim boundaries and native support blockers.

Acceptance statement:

```text
N12 starts from N11's GALI7 artifact-only closeout and opens only a
source-backed native naturalization inventory, candidate partition, and
Phase 8 readiness track. A valid N12 positive result requires explicit
producer-decision splits, RC-compatible native policy surfaces, serialized
thresholds, budget/replay gates, negative controls, and no agency, intention,
identity acceptance, biological, personhood, unrestricted-agency, or fully
native claim promotion.
```

Acceptance status:

```text
Achieved. The N12 experiment skeleton, README, implementation plan,
implementation checklist, hypotheses records, and artifact stubs were created.
No N12 inventory builders, probes, validators, or Phase 8 implementation have
been run. No `src/*` changes are required for Iteration 0.
```

Implementation record:

- Added `experiments/2026-06-N12-lgrc-native-naturalization-and-producer-dissolution/README.md`.
- Added `implementation/README.md`.
- Added `implementation/NativeNaturalizationAndProducerDissolutionImplementationPlan.md`.
- Added `implementation/NativeNaturalizationAndProducerDissolutionImplementationChecklist.md`.
- Added `hypotheses/README.md`.
- Added `hypotheses/hypothesis_a_native_absorption_inventory.md`.
- Added `hypotheses/hypothesis_b_phase8_readiness_contracts.md`.
- Added `hypotheses/hypothesis_c_deferred_theory_sensitive_boundaries.md`.
- Added stub README files for `configs/`, `outputs/`, `reports/`, and
  `scripts/`.
- Created the N12 experiment directory layout.
- No implementation scripts or probes have been run yet.

## Iteration 1. Baseline And Mechanism Inventory

Status: Complete.

- [x] Inventory N11 Iteration 11 native gap rows.
- [x] Inventory N11 Iteration 12 final blocker set and handoff.
- [x] Inventory N10 native contract rows referenced by N11.
- [x] Inventory N05-N11 producer/artifact scaffolds consumed by N11.
- [x] Record source artifact paths, report paths, and SHA-256 digests.
- [x] Record claim ceilings and blocked claims.
- [x] Record native blockers.
- [x] Record producer-mediated, validator-local, artifact-local, and native
      selection-only classifications.
- [x] Record essential producer decisions.
- [x] Record bookkeeping-only fields.
- [x] Record thresholds to serialize.
- [x] Record runtime-visible surfaces needed.
- [x] Record the provisional Iteration 1 row shape for every row.
- [x] Record `non_rc_quantity_audit` for every row.
- [x] Confirm no Phase 8 contract acceptance occurs in Iteration 1.
- [x] Confirm `src/*` remains clean for Iteration 1.

Expected artifacts:

- [x] `outputs/n12_native_naturalization_inventory.json`
- [x] `reports/n12_native_naturalization_inventory.md`
- [x] `scripts/build_n12_native_naturalization_inventory.py`

Acceptance statement:

```text
Iteration 1 passes if every mechanism row is source-backed and N12 records the
inherited native gaps using the provisional row shape, with non-RC audits and
without promoting them into native support.
```

Acceptance state:

```text
Achieved. Iteration 1 built a five-row source-backed inventory from N11
Iteration 11, N11 Iteration 12, and N10 Iterations 13-15. The inventory records
two NAT3 native absorption candidates, three NAT2 scaffold/blocker rows, zero
NAT4 rows, zero Phase 8-ready rows, required non-RC audits, and no new N12
native support. Inherited N11 route-arbitration support remains selection-only.
```

Implementation record:

- Added and ran `scripts/build_n12_native_naturalization_inventory.py`.
- Generated `outputs/n12_native_naturalization_inventory.json`.
- Generated `reports/n12_native_naturalization_inventory.md`.
- Command:

```text
.venv/bin/python experiments/2026-06-N12-lgrc-native-naturalization-and-producer-dissolution/scripts/build_n12_native_naturalization_inventory.py
```

- Status: `passed`.
- Output digest:

```text
cd58000592e06cb4a48f3059b9c8e8538f93b2589d37c242137eec2aed8dfb9a
```

- Artifact SHA-256:

```text
outputs/n12_native_naturalization_inventory.json 22c5ba0797cbbea75d06e138c6e570a3a446e31381fe4d0c4716093868de4f01
reports/n12_native_naturalization_inventory.md 784e6a10654058e3e367957dc9910e61a14cbfdebd5d0403629712abf7418ef1
scripts/build_n12_native_naturalization_inventory.py 93fcea26cdd64479c50a4705ee2ff68671d008f902a12e42fd0419a1e375eeba
```

## Iteration 2. Naturalization Schema And Ladder

Status: Complete.

- [x] Freeze the `NAT0-NAT6` ladder.
- [x] Freeze candidate row schema.
- [x] Freeze primary disposition fields.
- [x] Freeze `primary_disposition` values:
      `scaffold`, `native_absorption_candidate`, `theory_sensitive_blocker`,
      and `blocked_missing_source_or_gate`.
- [x] Freeze `phase8_ready` as derived from `nat_level = NAT4`.
- [x] Freeze secondary classification tags.
- [x] Freeze claim flags.
- [x] Freeze native-readiness criteria.
- [x] Freeze RC-compatibility fields.
- [x] Freeze rejection rules for non-RC quantities.
- [x] Freeze `non_rc_quantity_audit` fields.
- [x] Freeze mutation/scheduling boundary fields.
- [x] Freeze NAT3 gates.
- [x] Freeze NAT4 hard criteria.
- [x] Freeze blocked-claim fields.
- [x] Freeze runtime-visible surface fields.
- [x] Freeze serialized-threshold fields.
- [x] Freeze budget/replay fields.
- [x] Freeze fail-closed blocker tags.
- [x] Reject native support flags without Phase 8 source.
- [x] Reject claim-promotion fields.
- [x] Declare no-native-implementation boundary.

Expected artifacts:

- [x] `outputs/n12_naturalization_schema_v1.json`
- [x] `reports/n12_naturalization_schema_v1.md`
- [x] `scripts/build_n12_naturalization_schema_v1.py`

Acceptance statement:

```text
Iteration 2 passes if the N12 schema and ladder are frozen before candidate
evaluation or Phase 8 implementation work.
```

Acceptance state:

```text
Achieved. Iteration 2 froze the NAT0-NAT6 ladder, final row fields,
non-overlapping primary disposition model, derived phase8_ready rule, NAT3 and
NAT4 gates, non-RC quantity audit schema, mutation boundary schema, forced-false
claim flags, rejection rules, validation-scope note, and planned artifacts for
Iterations 3-7.
```

Implementation record:

- Added and ran `scripts/build_n12_naturalization_schema_v1.py`.
- Generated `outputs/n12_naturalization_schema_v1.json`.
- Generated `reports/n12_naturalization_schema_v1.md`.
- Command:

```text
.venv/bin/python experiments/2026-06-N12-lgrc-native-naturalization-and-producer-dissolution/scripts/build_n12_naturalization_schema_v1.py
```

- Status: `passed`.
- Output digest:

```text
f6e025deff124593dee73891fa15a196338d0c05351119556e905ebf6e525327
```

- Artifact SHA-256:

```text
outputs/n12_naturalization_schema_v1.json 1054be3cc71946e00be6e4d78a08111ec9d2d75c19fd535fd9b4898f86e4df80
reports/n12_naturalization_schema_v1.md e3a3d0c126f71f150930f402d2c41b6a78b650d90047ba9dd846a728393c8a8c
scripts/build_n12_naturalization_schema_v1.py d6dd3ba0803a91c540ab4209b3a9bf14ede115b52bce2be1da921e65c91a5db4
```

## Iteration 3. Route Conductance Memory Candidate

Status: Pending.

- [ ] Evaluate N08 memory trail / affordance source rows.
- [ ] Record route-use-linked memory update rule.
- [ ] Record memory relaxation or decay rule.
- [ ] Record route-scope runtime-visible policy requirement.
- [ ] Record conductance eligibility threshold.
- [ ] Record route conductance memory budget surface.
- [ ] Split producer-side route memory pattern from native geometry/conductance
      policy candidate.
- [ ] Split native geometry/conductance policy candidate from native
      coherence/flux mechanism.
- [ ] Record geometry-vs-bookkeeping decision.
- [ ] Record mutation boundary.
- [ ] Record producer-or-policy may schedule only.
- [ ] Record `step()` or topology event ownership of state mutation.
- [ ] Record route memory `non_rc_quantity_audit`.
- [ ] Check RC causality/coherence/geometry compatibility.
- [ ] Define controls against ACO and ant-colony relabeling.
- [ ] Define controls against intention, agency, and native support relabeling.
- [ ] If assigning `NAT4`, require every NAT4 gate frozen in Iteration 2.
- [ ] Assign supported NAT level for route conductance memory.

Expected artifacts:

- [ ] `outputs/n12_route_conductance_memory_candidate.json`
- [ ] `reports/n12_route_conductance_memory_candidate.md`
- [ ] `scripts/build_n12_route_conductance_memory_candidate.py`

Acceptance statement:

```text
Iteration 3 passes if route conductance memory is classified at its supported
NAT level with source links, RC-compatible policy surfaces, serialized
thresholds, geometry-vs-bookkeeping split, mutation boundary, non-RC audit,
controls, and no native support claim.
```

## Iteration 4. Response Magnitude Candidate

Status: Pending.

- [ ] Evaluate N09-N11 regulation sizing source rows.
- [ ] Record proxy measurement surface.
- [ ] Record target band.
- [ ] Record response gain.
- [ ] Record max correction per window.
- [ ] Record error trend.
- [ ] Record saturation status.
- [ ] Record overcorrection status.
- [ ] Record bounded window.
- [ ] Record out-of-envelope blocker threshold.
- [ ] Record response packet scheduling boundary.
- [ ] Record mutation boundary.
- [ ] Record producer-or-policy may schedule only.
- [ ] Record `step()` or topology event ownership of state mutation.
- [ ] Record proxy and node-plus-packet budget surfaces.
- [ ] Record response magnitude `non_rc_quantity_audit`.
- [ ] Audit whether proxy measurement is a derived observable or new state.
- [ ] Audit whether target band is exogenous or runtime-visible policy.
- [ ] Audit whether response gain is serialized and replayable.
- [ ] Audit whether correction debits node-plus-packet budget.
- [ ] Audit whether response sizing requires hidden optimization or external
      controller state.
- [ ] Check RC causality/coherence/scheduling compatibility.
- [ ] Define controls against goal ownership, intention, and agency relabeling.
- [ ] Define controls against unbounded response and native support relabeling.
- [ ] If assigning `NAT4`, require every NAT4 gate frozen in Iteration 2.
- [ ] Assign supported NAT level for response magnitude policy.

Expected artifacts:

- [ ] `outputs/n12_response_magnitude_candidate.json`
- [ ] `reports/n12_response_magnitude_candidate.md`
- [ ] `scripts/build_n12_response_magnitude_candidate.py`

Acceptance statement:

```text
Iteration 4 passes if response magnitude policy is classified at its supported
NAT level with source links, RC-compatible policy surfaces, serialized
thresholds, trend/stability fields, mutation boundary, non-RC audit, controls,
and no native support claim.
```

## Iteration 5. Identity Acceptance Boundary

Status: Pending.

- [ ] Record why identity acceptance is not Phase 8-ready yet.
- [ ] Separate support survival from identity acceptance.
- [ ] Separate identity continuity from runtime acceptance.
- [ ] Block RC identity collapse claims.
- [ ] Identify validator-local support fields.
- [ ] Record missing formal acceptance semantics.
- [ ] Record theory gates required before Phase 8 entry.
- [ ] Confirm no identity acceptance claim opens.

Expected artifacts:

- [ ] `outputs/n12_identity_acceptance_boundary.json`
- [ ] `reports/n12_identity_acceptance_boundary.md`
- [ ] `scripts/build_n12_identity_acceptance_boundary.py`

Acceptance statement:

```text
Iteration 5 passes if identity acceptance remains blocked with explicit theory
entry gates and no identity acceptance claim.
```

## Iteration 6. Agentic-Like Integration Boundary

Status: Pending.

- [ ] Record why full native agentic-like integration is a meta-gap.
- [ ] Keep component native policies separate from integration meta-policy.
- [ ] Keep artifact-only replay separate from fully native integration.
- [ ] Block semantic agency claims.
- [ ] Separate budget/replay contract from agency semantics.
- [ ] Record missing composition replay prerequisites.
- [ ] Confirm no fully native agentic-like integration claim opens.

Expected artifacts:

- [ ] `outputs/n12_agentic_like_integration_boundary.json`
- [ ] `reports/n12_agentic_like_integration_boundary.md`
- [ ] `scripts/build_n12_agentic_like_integration_boundary.py`

Acceptance statement:

```text
Iteration 6 passes if full native agentic-like integration remains blocked
until component native policies exist and composition replay validates them.
```

## Iteration 7. Phase 8 Readiness Package, No Implementation

Status: Pending.

- [ ] Produce Phase 8-ready contract list.
- [ ] Produce blocker list.
- [ ] Produce fail-closed control list.
- [ ] Produce telemetry requirements, including `src/pygrc/telemetry` surfaces.
- [ ] Produce test gates.
- [ ] Produce route conductance memory readiness row.
- [ ] Produce response magnitude policy readiness row.
- [ ] Produce identity acceptance blocked row.
- [ ] Produce native integration meta-policy blocked row.
- [ ] Decide which rows, if any, reach `NAT4`.
- [ ] Confirm `src_diff_empty = true`.
- [ ] Confirm `native_supported_flags = false`.
- [ ] Confirm `phase8_opened = false`.

Expected artifacts:

- [ ] `outputs/n12_phase8_readiness_matrix.json`
- [ ] `reports/n12_phase8_readiness_matrix.md`
- [ ] `scripts/build_n12_phase8_readiness_matrix.py`

Acceptance statement:

```text
Iteration 7 passes if route conductance memory and response magnitude policy
are either classified as Phase 8-ready contracts or fail closed with distinct
missing-gate blockers, while identity acceptance and full native integration
remain blocked and no implementation has been opened.
```

## Iteration 8. N12 Closeout And Handoff

Status: Pending.

- [ ] Close Hypothesis A.
- [ ] Close Hypothesis B.
- [ ] Close Hypothesis C.
- [ ] Freeze final NAT levels.
- [ ] Confirm every seed row is classified.
- [ ] Record final native absorption candidates.
- [ ] Record final Phase 8-ready contracts.
- [ ] Record final experiment-local scaffolds.
- [ ] Record final theory-sensitive blockers.
- [ ] Confirm every Phase 8-ready row has controls, telemetry requirements,
      and tests.
- [ ] Confirm every deferred row has a blocker and rationale.
- [ ] Record final native support flags as false unless separate Phase 8 source
      exists.
- [ ] Record final claim flags as false for unsafe claims.
- [ ] Update roadmap if needed.
- [ ] Decide whether next work is targeted Phase 8 or N13.
- [ ] Confirm `src_diff_empty = true`.
- [ ] Confirm `native_supported_flags = false`.
- [ ] Confirm `phase8_opened = false`.
- [ ] Confirm `src/*` remains clean for N12.

Expected artifacts:

- [ ] `outputs/n12_closeout_and_handoff.json`
- [ ] `reports/n12_closeout_and_handoff.md`
- [ ] `scripts/build_n12_closeout_and_handoff.py`

Acceptance statement:

```text
Iteration 8 passes if N12 closes with source-backed naturalization gates and a
claim-clean handoff, without implementing Phase 8 or promoting N11 artifact-only
evidence into native LGRC support.
```

# GRCL-v3 Implementation Checklist

This document tracks the first executable implementation slice of
`GRCL-v3`.

It is intentionally narrower than a full phase checklist.
The purpose here is not to “finish rich seeds.”
The purpose is to test the central hypothesis honestly:

- whether a small, theory-facing `GRCV3`-rich seed can preserve geometry-bearing
  source intent strongly enough to survive lowering into a seed-driven
  `GRCV3` sparkable local state

This checklist executes the first narrow lane defined in:

- [GRCL-V3-ImplementationPlan.md](./GRCL-V3-ImplementationPlan.md)
- [GRCL-V3-Vocabulary.md](./GRCL-V3-Vocabulary.md)
- [GRCL-V3-LoweringArchitectureDecision.md](./GRCL-V3-LoweringArchitectureDecision.md)
- [GRCL-V3-FamilyNativeLoweringRefactorPlan.md](./GRCL-V3-FamilyNativeLoweringRefactorPlan.md)

## Usage Rules

- Do not expand the accepted field surface just because implementation becomes
  convenient.
- Do not change `GRCV3` runtime equations as part of this checklist.
- Do not relax spark thresholds merely to “make the rich seed work.”
- Do not let `GRCV3` silently downgrade a `rich_required` seed to a
  neutral/common-only realization path.
- Record every executable constitutive choice here when it becomes real.
- If the first rich-seed gate fails, stop and document why before broadening the
  schema.
- Evaluate further `GRCL-v3` work against the recorded architecture target:
  - weaker schemas may remain interpretive
  - `grcv3.rich.v2+` should move toward family-native lowering rather than
    weaker-blueprint semantic dependence
  - mature `grcv3.rich.v3+` should move toward direct family-native assembly
    with minimal interpretation
  - if `grcv3.rich.v4` is introduced, it should be introduced only as a
    direct-translation contract, not as another projector/lowering refinement
    lane
- Treat the family-native lowering refactor as the next architectural lane once
  the current checklist has localized the seed-vs-runtime gap clearly enough.

## Iteration Template

Copy this section for each new iteration.

```markdown
## Iteration N. <Short Name>

### Goal

<What this iteration is intended to complete>

### Checks

- [ ] <Concrete task 1>
- [ ] <Concrete task 2>
- [ ] <Concrete task 3>

### Implementation Notes

- <Important implementation detail, decision, or constraint>

### Verification

- [ ] <Import / test / review check>
- [ ] <Boundary / acceptance check>

### Summary

<Short outcome summary once iteration is complete>
```

## Iteration 0. Checklist Bootstrap

### Goal

Create the execution checklist for the first `GRCL-v3` lane and bind it to the
already-written plan and vocabulary note.

### Checks

- [x] Create `GRCL-V3-ImplementationChecklist.md`
- [x] State explicitly that this checklist is limited to the first minimal rich
  seed lane
- [x] Link the checklist to the `GRCL-v3` plan and vocabulary docs
- [x] Record that the exit condition is a diagnostic gate, not full
  schema/projector completion
- [x] Record that implementation must keep:
  - one common seed language
  - one typed `GRCV3` extension layer
  - and one seed/projector-only visibility boundary for rich data

### Implementation Notes

- The rich-seed lane is intentionally narrower than the earlier phase plans.
- This avoids declaring “full `GRCL-v3`” before the first geometry-preservation
  gate is even tested.
- The acceptance target here is:
  - minimal rich-seed vocabulary
  - minimal validation
  - one fixture
  - one lowering path
  - one diagnostic comparison against the manual spark probe
- The architecture boundary is now explicit:
  - common seed parsing/loading remains in `pygrc.landscapes`
  - typed `GRCV3` extension parsing belongs under a landscapes extension module
  - only the extension parser and `GRCV3` projector should know about rich-seed
    structure directly

### Verification

- [x] The checklist exists under `implementation/`
- [x] The document references the existing plan and vocabulary note
- [x] The scope is explicitly smaller than full `GRCL-v3` capability

### Summary

`GRCL-v3` now has an execution checklist for the first minimal rich-seed lane.
The scope is intentionally constrained to one honest geometry-preservation test.

## Iteration 1. Lock The First Accepted Rich-Field Surface

### Goal

Freeze the first field subset that the implementation is allowed to consume.

### Checks

- [x] Lock the top-level accepted fields:
  - `extensions.grcv3.contract_version`
  - `extensions.grcv3.rich_required`
- [x] Lock the versioning rule:
  - `seed_version` governs the neutral/common language
  - `extensions.grcv3.contract_version` governs only the rich `GRCV3` contract
- [x] Lock the primitive-level accepted fields:
  - `realization.kind`
  - `realization.support_count`
  - `realization.radius_scale`
  - `realization.branch_order`
  - `local_geometry.frame_mode`
  - `local_geometry.weak_axis_role`
  - `interfaces.branch_targets`
- [x] Lock the code-organization rule:
  - common seed runtime model stays in `landscapes/seed.py`
  - common file parsing/loading stays in `landscapes/io.py`
  - rich-seed typed parsing/validation goes under `landscapes/extensions/grcv3.py`
- [x] Record which rich-vocabulary groups remain explicitly out of scope for the
  first executable slice
- [x] State the first allowed primitive kinds for the minimal probe

### Implementation Notes

- The first slice should be smaller than the full vocabulary note.
- Curvature-intent and boundary/channel specializations may remain documented but
  not yet executable if they are not required for the first spark-preserving
  probe.
- The first slice should prefer one motif family, not many.
- The likely initial target is a junction/saddle-local rich seed because that
  is where the current neutral/common contract demonstrably loses the needed
  weak-axis geometry.
- The field lock should happen before new dataclasses or parser functions land,
  otherwise the code will define the contract implicitly instead of explicitly.
- Locked first contract version:
  - `grcv3.rich.v1`
- Locked first primitive scope:
  - `junction`
  - `saddle`
- Locked out-of-scope vocabulary for this first executable slice:
  - top-level:
    - `lowering_policy`
    - `projection_goal`
  - realization:
    - `attachment_mode`
    - `support_angles`
  - local geometry:
    - `axis_roles`
    - `symmetry_class`
    - `center_role`
  - all of:
    - `curvature_intent`
    - `boundary_geometry`
    - `channel_geometry`
- Rationale:
  - the first test should isolate the geometry-preservation problem around one
    spark-relevant local stencil rather than open the full `GRCL-v3` surface at
    once.

### Verification

- [x] The accepted field subset is written explicitly in code-facing terms
- [x] Out-of-scope rich fields are named so schema drift cannot happen silently
- [x] The first field surface is smaller than the full vocabulary note

### Summary

Iteration 1 is now locked. The first consumed `GRCL-v3` contract is
`grcv3.rich.v1`, limited to one junction/saddle-local rich-seed slice with a
minimal top-level and primitive-level field set, while richer vocabulary groups
remain documented but explicitly out of scope.

## Iteration 2. Validation Boundary And Failure Modes

### Goal

Define how the first rich-field subset is validated and how unsupported or
malformed rich seeds fail.

### Checks

- [x] Decide whether rich-field validation lives inside the neutral seed
  validator or in a `GRCV3`-specific validation pass
- [x] Decide how the common loader preserves raw `extensions.grcv3` while the
  `GRCV3` extension layer turns supported fields into typed objects
- [x] Define required-vs-optional behavior for the accepted rich fields
- [x] Define explicit rejection behavior for:
  - unknown required rich values
  - malformed branch-target mappings
  - invalid support counts
  - illegal `weak_axis_role` references
- [x] Define the meaning of `rich_required=true`
- [x] Define behavior for `rich_required=false` with partial rich data
- [x] Define contract-version dispatch behavior for unsupported or older/newer
  `extensions.grcv3.contract_version` values

### Implementation Notes

- The critical boundary is:
  - unknown `extensions.grcv3` data may be preserved by neutral/common loading
  - but once `GRCV3` claims to consume the supported subset, malformed data must
    fail explicitly
- The first implementation should strongly prefer “consume or fail” over silent
  fallback.
- The projector should only be allowed to approximate supported instructions if
  that approximation is documented and deterministic.
- The neutral/common loader should remain reusable for both old v2-capable seeds
  and new v3-capable seeds; only the `GRCV3` extension extraction layer should
  branch on rich contract version.
- Locked validation architecture:
  - `landscapes/validation.py` remains neutral/common only
  - `landscapes/extensions/grcv3.py` owns rich extraction, typed parsing,
    contract-version dispatch, and rich-field validation
- Locked required-field rule for the first contract:
  - top-level:
    - `contract_version`
    - `rich_required`
  - primitive-level:
    - `realization.kind`
    - `realization.support_count`
    - `realization.radius_scale`
    - `realization.branch_order`
    - `local_geometry.frame_mode`
    - `local_geometry.weak_axis_role`
    - `interfaces.branch_targets`
- Locked consume-or-fail rule:
  - absent `extensions.grcv3` -> neutral/common projection
  - present + `rich_required=false` -> raw extension may be preserved without
    rich lowering support
  - present + `rich_required=true` -> supported contract must be consumed or
    projection fails explicitly
- Locked version-dispatch rule:
  - unknown `contract_version` + `rich_required=true` -> fail explicitly
  - unknown `contract_version` + `rich_required=false` -> preserve, do not
    consume
- Locked malformed-supported-field rule:
  - invalid `support_count`, `branch_order`, `weak_axis_role`, or
    `branch_targets` fail explicitly once `GRCV3` claims to consume the rich
    contract

### Verification

- [x] Validation rules distinguish preserved unknown data from consumed rich data
- [x] `rich_required=true` has a concrete enforcement meaning
- [x] Failure modes are explicit enough to test later

### Summary

Iteration 2 is now locked. Neutral/common seed loading remains permissive and
shared, while `GRCV3` rich-seed support becomes a typed extension-validation
layer with explicit contract-version dispatch and consume-or-fail semantics.

## Iteration 3. Minimal Rich Seed Fixture

### Goal

Author one minimal rich seed fixture that preserves the manual spark-probe
intent in shareable source form.

### Checks

- [x] Choose the minimal source fixture shape:
  - standalone manual-rich probe
  - or landscape-flavored cross probe with explicit `extensions.grcv3`
- [x] Add one seed fixture under `configs/landscapes/seed/`
- [x] Keep the fixture minimal:
  - one central spark-relevant primitive
  - only the neighbor structure needed for the first gate
- [x] Encode only the Iteration 1 accepted rich fields
- [x] Record why the fixture expresses something neutral/common `GRCL` could not

### Implementation Notes

- This fixture is not yet a representative cell.
- It is a proof fixture for the first geometry-preservation gate.
- The fixture should be small enough that failures remain interpretable.
- The rich seed should not depend on hidden projector assumptions not documented
  in the vocabulary note.
- Implemented fixture:
  - `configs/landscapes/seed/grcv3-rich-junction-probe.seed.yaml`
- Chosen fixture shape:
  - landscape-flavored cross probe with explicit `extensions.grcv3`
- Chosen primitive focus:
  - one hostless `saddle` primitive `decision_core`
  - four basin neighbors
  - four valley carriers
- Extra meaning preserved beyond neutral/common `GRCL`:
  - explicit `grcv3.rich.v1` top-level contract
  - explicit branch order
  - explicit weak-axis role
  - explicit branch-target mapping from local roles to semantic neighbors
- The fixture intentionally remains within the current neutral/common primitive
  dataclass surface:
  - no new neutral/common primitive fields were introduced
  - the rich content lives only under `extensions.grcv3`

### Verification

- [x] The fixture is valid as a seed document
- [x] The fixture uses only the accepted `GRCL-v3` field subset
- [x] The fixture’s extra meaning over neutral/common `GRCL` is explicit

### Summary

Iteration 3 is complete. The first rich seed fixture now exists as a minimal
hostless saddle/junction probe with only the locked `grcv3.rich.v1` field
surface and no neutral/common schema drift.

## Iteration 4. First Projector Lowering Path

### Goal

Implement the first `GRCV3` lowering path that consumes the accepted rich-field
subset without changing runtime equations.

### Checks

- [x] Add a `GRCV3`-specific rich-seed lowering path in the landscape projector
- [x] Introduce a typed `GRCV3` extension extraction boundary rather than
  reading raw nested extension mappings throughout projector code
- [x] Enforce `rich_required=true` as consume-or-fail, not ignore-and-fallback
- [x] Lower the accepted realization fields into a deterministic motif
- [x] Lower branch/interface mapping into deterministic attachment structure
- [x] Persist enough realized metadata to inspect whether lowering preserved the
  intended local roles

### Implementation Notes

- The lowering path should preserve meaning, not merely copy rich fields into
  metadata.
- If the rich seed declares a weak-axis-bearing branch order, the realized local
  stencil must visibly depend on it.
- The first implementation should stay narrow enough that failures can be tied
  to one lowering rule rather than to a large mixed projector surface.
- The rest of `GRCV3` should see only lowered runtime state plus explicit
  projector metadata, not the rich-seed parsing details themselves.
- Implemented typed extension boundary:
  - `src/pygrc/landscapes/extensions/__init__.py`
  - `src/pygrc/landscapes/extensions/grcv3.py`
- Implemented projector consumption path:
  - `src/pygrc/models/grc_v3_landscape.py`
- Implemented first rich lowering behavior:
  - typed extraction of `grcv3.rich.v1`
  - explicit branch-node count from `support_count`
  - explicit branch radius scaling from `radius_scale`
  - branch layout by `branch_order`
  - explicit branch-target to valley attachment before geometric fallback
- Implemented runtime/projector diagnostics:
  - `landscape_grcv3_rich_contract_version`
  - `landscape_grcv3_rich_required`
  - `landscape_grcv3_rich_primitive_ids`
  - `landscape_grcv3_branch_node_ids_by_target`
  - rich-specific realization mode string when the contract is consumed

### Verification

- [x] The rich seed lowers deterministically across repeated runs
- [x] `rich_required=true` does not silently downgrade to neutral/common
  realization
- [x] Realized metadata is sufficient to inspect center/support/interface roles

Focused verification executed with:

- `./.venv/bin/python -m unittest tests.landscapes.test_grcv3_extensions tests.models.test_grc_v3_landscape_runtime`
- result: `Ran 16 tests ... OK`

### Summary

Iteration 4 is complete. The first typed `grcv3.rich.v1` extraction boundary
exists, and the `GRCV3` landscape projector now consumes the minimal rich-seed
contract for junction/saddle-local lowering without changing runtime equations.

## Iteration 5. Diagnostic Gate Against Manual Spark Probe

### Goal

Test whether the lowered rich seed preserves enough constitutive geometry to
cross the first honest sparkability gate.

### Checks

- [x] Run the lowered rich seed through a focused diagnostic path
- [x] Compare the realized rich-seed local state against the existing manual
  spark probe
- [x] Check at least:
  - interior point with usable neighborhood
  - low enough gradient
  - near-degenerate signed curvature on the intended axis
  - stable orthogonal curvature
- [x] Record whether the result reaches:
  - geometric seed detection
  - spark candidate detection
  - and, if honest, first spark lifecycle events
- [x] Decide explicitly whether Gate A and Gate B from the plan pass or fail

### Implementation Notes

- Passing this iteration does **not** mean full `GRCL-v3` is done.
- It means the rich-seed hypothesis has crossed its first honest gate and is now
  justified to broaden.
- Failing this iteration is still useful if the failure is well localized and
  documented.
- Diagnostic commands used:
  - `./.venv/bin/python scripts/diagnose_grcv3_landscape_seed.py configs/landscapes/seed/grcv3-rich-junction-probe.seed.yaml --profile seed_baseline --steps 20 --limit 12`
  - `./.venv/bin/python scripts/probe_grcv3_manual_spark.py --probe single-node --advance 2`
  - `./.venv/bin/python scripts/probe_grcv3_manual_spark.py --probe three-node --advance 2`
- Rich-seed diagnostic outcome:
  - the lowered seed realizes a nontrivial `decision_core` motif with one
    `junction_center` interior node and four explicit branch/interface
    attachments
  - the center node has zero gradient but no usable signed-Hessian stencil yet
    (`eig=[]`), so it does not qualify as a geometric seed
  - nearby branch/channel nodes do produce tiny signed eigenvalues, but their
    gradients remain well above the baseline `eps_gradient=1e-3` threshold and
    none of them validate as basin seeds
  - over a 20-step diagnostic run the lowered seed remains at:
    - `geometric_seed_count=0`
    - `geometric_validated_basin_count=0`
    - `spark_event_count=0`
    - `candidate_count=0`
- Manual-probe comparison:
  - the `single-node` manual probe still crosses the full spark path under the
    same baseline thresholds: `spark_candidate -> split_init -> spark ->
    split_progress -> split_complete`
  - the `three-node` manual probe still crosses the candidate/init path and
    remains `spark_pending`, which confirms that the spark machinery itself is
    operational once the local geometry is constitutively adequate
  - this localizes the failure to the lowered rich seed, not to disabled spark
    code, threshold loosening, or hidden manual state edits inside the normal
    runtime loop
- Gate outcome:
  - Gate A: `PASS`
    - the rich seed expresses branch order, weak-axis role, and explicit
      branch-target attachment that the neutral/common seed could not express
    - that extra content survives lowering into distinct runtime topology and
      cached diagnostics
  - Gate B: `FAIL`
    - the first minimal rich seed does not yet produce the target geometric
      condition honestly through the projector boundary
    - the remaining gap is constitutive: richer source-local geometry is still
      needed if the lowered seed is expected to generate sparkable curvature
      without post-projection intervention

### Verification

- [x] The result is attributable to rich-seed geometry, not threshold loosening
- [x] The comparison against the manual spark probe is written down explicitly
- [x] The outcome is recorded as pass/fail for Gate A and Gate B

### Summary

Iteration 5 closes with a split outcome. `grcv3.rich.v1` has crossed the first
reality gate because its extra geometry-bearing content survives projection in a
real, inspectable way, but it has **not** yet crossed the operational spark gate.
The manual probes still prove the baseline `GRCV3` spark machinery works; the
remaining failure is that the first rich seed does not yet encode enough local
geometry to produce a genuine geometric seed through the landscape projector
alone.

## Recorded Follow-On Decision

The project explicitly records the next step rather than leaving it implicit:

- `grcv3.rich.v1` is accepted as a real, projector-facing extension surface
- the current checklist is **not** treated as the end of `GRCL-v3`
- because Gate A passed and Gate B failed, the decided next move is to broaden
  the rich-seed capability surface
- that broadening must happen through explicit vocabulary and validation growth,
  not through threshold loosening or hidden projector-side constitutive hacks

This means the outcome of Iteration 5 is not “stop” and not “done.” It is:

1. keep the current minimal rich seed as a validated probe
2. open the next capability slice that adds the missing constitutive local
   geometry
3. only after that rerun the honest sparkability gate

## Iteration 6. Lock The Second Capability Slice

### Goal

Define the next accepted `GRCL-v3` surface explicitly before any additional
projector work begins.

### Checks

- [x] Bump the rich contract version for the broadened slice
- [x] Lock which new `local_geometry` fields become executable
- [x] Lock which new `curvature_intent` fields become executable
- [x] Lock which new `interfaces` fields become executable
- [x] Lock which `channel_geometry` fields become executable
- [x] Lock which `boundary_geometry` fields become executable
- [x] Record which documented fields remain out of scope even after this lift

### Implementation Notes

- The broadened slice should be versioned explicitly rather than expanding
  `grcv3.rich.v1` invisibly.
- The likely next version is `grcv3.rich.v2`.
- This iteration is still a contract-lock step, not a code-lowering step.
- Locked broadened contract version:
  - `grcv3.rich.v2`
- Locked new executable `local_geometry` fields:
  - `axis_roles`
  - `symmetry_class`
  - `center_role`
- Locked new executable `curvature_intent` fields:
  - `class`
  - `stable_axis_roles`
  - `weak_axis_role`
  - `ordering`
- Locked new executable `interfaces` fields:
  - `boundary_roles`
  - `channel_roles`
  - `preferred_attachment_sites`
- Locked new executable `channel_geometry` fields:
  - `realization_kind`
  - `interior_count`
  - `waypoint_policy`
  - `entry_role`
  - `exit_role`
- Locked new executable `boundary_geometry` fields:
  - `realization_kind`
  - `normal_role`
  - `tangent_role`
  - `arc_span`
  - `support_distribution`
- Locked primitive scope for `grcv3.rich.v2`:
  - `basin`
  - `plateau`
  - `junction`
  - `saddle`
  - `ridge`
  - `valley`
- Explicitly still out of scope after this lift:
  - top-level:
    - `lowering_policy`
    - `projection_goal`
  - realization:
    - `attachment_mode`
    - `support_angles`
  - any solved differential state, solved transport state, runtime identity
    state, or projector-private hidden blobs
- Code-facing records:
  - [implementation/GRCL-V3-Vocabulary.md](./GRCL-V3-Vocabulary.md)
  - [src/pygrc/landscapes/extensions/grcv3.py](../src/pygrc/landscapes/extensions/grcv3.py)

### Verification

- [x] The next executable field set is written down in code-facing terms
- [x] The versioning rule for the broadened slice is explicit
- [x] Remaining out-of-scope vocabulary is named so drift cannot happen silently

### Summary

Iteration 6 is locked. The second executable `GRCL-v3` slice is now explicitly
versioned as `grcv3.rich.v2`, with a narrowly defined expansion into
local-geometry, curvature-intent, interface, channel-geometry, and
boundary-geometry fields, while the remaining source-vs-runtime boundary stays
explicitly closed.

## Iteration 7. Validation And Fixture Lift For `grcv3.rich.v2`

### Goal

Make the second slice real at the schema and validation layer before projector
generalization begins.

### Checks

- [x] Extend typed parsing/validation for the newly accepted `grcv3.rich.v2`
  fields
- [x] Define explicit failure modes for malformed or contradictory rich data
- [x] Add at least one richer seed fixture beyond the minimal junction probe
- [x] Verify that neutral/common seed loading remains backward-compatible

### Implementation Notes

- Rich fixtures in this iteration should still be theory-facing probes, not yet
  representative runs.
- The fixture set should expose the new local-geometry burden rather than hide
  it in projector defaults.
- Typed validation/runtime additions landed in:
  - [src/pygrc/landscapes/extensions/grcv3.py](../src/pygrc/landscapes/extensions/grcv3.py)
  - [src/pygrc/landscapes/extensions/__init__.py](../src/pygrc/landscapes/extensions/__init__.py)
- New richer probe fixture:
  - [configs/landscapes/seed/grcv3-rich-basin-boundary-channel-probe.seed.yaml](../configs/landscapes/seed/grcv3-rich-basin-boundary-channel-probe.seed.yaml)
- Validation now covers:
  - `grcv3.rich.v1`
  - `grcv3.rich.v2`
  - primitive-specific allowed-key sets
  - role-membership consistency across `local_geometry` and `curvature_intent`
  - attachment-site consistency for `interfaces`
  - explicit rejection of malformed `channel_geometry` and `boundary_geometry`
- Backward-compatibility signal:
  - neutral/common seed loading still yields `None` for
    `extract_grcv3_seed_extension(...)`
  - existing `GRCV3` rich-junction runtime tests remain green, so the broadened
    parsing boundary did not break the `grcv3.rich.v1` projector path
- Verification command:
  - `./.venv/bin/python -m unittest tests.landscapes.test_grcv3_extensions tests.models.test_grc_v3_landscape_runtime`
  - `Ran 21 tests in 1.280s`
  - `OK`

### Verification

- [x] Invalid `grcv3.rich.v2` payloads fail explicitly
- [x] Valid broadened fixtures parse deterministically
- [x] The new fixture set is small but sufficient to exercise the broadened
  contract

### Summary

Iteration 7 is complete. `grcv3.rich.v2` now exists as a real parsing and
validation boundary with one richer basin/boundary/channel probe fixture and
explicit failure modes, while neutral/common seed loading and the existing
`grcv3.rich.v1` runtime path remain intact.

## Iteration 8. Basin And Channel Lowering

### Goal

Lower the newly explicit source-local geometry into basin-local and channel-local
motifs that preserve directional interior structure.

### Checks

- [x] Extend basin-local lowering to consume the newly accepted local-geometry
  and curvature-intent fields
- [x] Extend channel lowering to consume the newly accepted channel-geometry and
  attachment fields
- [x] Preserve deterministic attachment from channel roles / preferred
  attachment sites into lowered node topology
- [x] Record approximation metadata where source meaning cannot be realized
  exactly

### Implementation Notes

- This iteration should change realized topology, not thresholds.
- The objective is to improve constitutive geometry honesty at the projector
  boundary.
- Lowering updates landed in:
  - [src/pygrc/models/grc_v3_landscape.py](../src/pygrc/models/grc_v3_landscape.py)
- Basin-local lowering changes:
  - `grcv3.rich.v2` basin primitives with declared `axis_roles` now realize
    support nodes from the declared role order rather than the legacy fixed
    three-support patch
  - basin support nodes now record `grcv3_role_label`, weak-axis metadata,
    curvature class metadata, and preferred-attachment metadata
- Channel lowering changes:
  - `channel_geometry.interior_count` now controls realized channel-node count
  - `channel_geometry.waypoint_policy` is consumed through deterministic
    polyline sampling
  - endpoint attachment now resolves in this order:
    1. source/target primitive `preferred_attachment_sites`
    2. explicit local role labels on realized motif nodes
    3. geometric fallback
- New runtime checks were added in:
  - [tests/models/test_grc_v3_landscape_runtime.py](../tests/models/test_grc_v3_landscape_runtime.py)
  - these verify `core_basin` role-node realization plus left/right channel
    attachment onto the expected `west` / `east` support nodes in the richer
    `grcv3.rich.v2` probe

### Verification

- [x] Lowered basin/channel motifs are inspectable from cached diagnostics
- [x] Realized attachment follows source-declared local roles
- [x] No hidden manual state injection is introduced

### Summary

Iteration 8 is complete. Basin-local and channel-local `grcv3.rich.v2`
lowering now changes realized topology and attachment structure directly, with
role-aware support-node realization and deterministic source-to-runtime channel
attachment semantics.

## Iteration 9. Ridge / Boundary Lowering

### Goal

Realize boundary-support structure explicitly so ridge meaning is no longer
mostly semantic.

### Checks

- [x] Extend ridge lowering to consume the newly accepted boundary-geometry
  fields
- [x] Realize support arcs / barrier stencils deterministically
- [x] Record approximation notes whenever the lowered boundary is only an
  approximation of the source intent
- [x] Expose enough diagnostics to inspect realized boundary support structure

### Implementation Notes

- This iteration is about explicit support geometry, not solved metric import.
- Boundary realism matters because basin-local sparkability depends on how
  support and interface constraints are actually laid out.
- Ridge/boundary lowering changes:
  - `boundary_geometry.realization_kind`, `normal_role`, `tangent_role`, and
    `arc_span` now drive constructive ridge support-point placement
  - `support_arc` and related boundary modes now lower into role-oriented
    support-node arcs around the owner primitive rather than the previous
    midpoint-only fallback
  - ridge attachment uses source-side preferred boundary attachment when
    available, then explicit local role labels, then geometric fallback
- Diagnostics now include:
  - `landscape_grcv3_role_node_ids_by_primitive_id`
  - `landscape_grcv3_lowering_notes`
  - `landscape_realization_mode = basin_patch_valley_channel_junction_ridge_grcv3_rich_v2`
- Verification command:
  - `./.venv/bin/python -m unittest tests.landscapes.test_grcv3_extensions tests.models.test_grc_v3_landscape_runtime`
  - `Ran 23 tests in 1.465s`
  - `OK`

### Verification

- [x] Realized ridge structure is attributable to source boundary geometry
- [x] Boundary diagnostics are inspectable without re-reading raw seed YAML
- [x] The lowered result stays deterministic

### Summary

Iteration 9 is complete. Ridge/boundary support structure is now lowered as an
explicit, inspectable geometric construct in the `grcv3.rich.v2` path rather
than remaining mostly semantic metadata, while staying deterministic and
backward-compatible with the earlier `v1` route.

## Iteration 10. Honest Sparkability Rerun

### Goal

Rerun the honest sparkability gate after the richer source-local geometry exists.

### Checks

- [x] Run the broadened rich-seed fixtures through the focused diagnostic path
- [x] Compare the realized local states against the manual spark probes again
- [x] Check whether the broadened seeds now reach:
  - geometric seed detection
  - spark candidate detection
  - and, if honest, first spark lifecycle events
- [x] Decide explicitly whether Gate B now passes or still fails

### Implementation Notes

- The same baseline thresholds should be used unless a theory-facing reason is
  documented to change them.
- A “pass” here must come from richer source-local geometry, not looser
  acceptance rules.
- Diagnostic commands used:
  - `./.venv/bin/python scripts/diagnose_grcv3_landscape_seed.py configs/landscapes/seed/grcv3-rich-basin-boundary-channel-probe.seed.yaml --profile seed_baseline --steps 40 --limit 16`
  - `./.venv/bin/python scripts/probe_grcv3_manual_spark.py --probe single-node --advance 2`
  - `./.venv/bin/python scripts/probe_grcv3_manual_spark.py --probe three-node --advance 2`
- Pure-runtime control rerun:
  - rerunning Iteration 10 without any landscape projection is equivalent to
    rerunning the manual `GRCV3` spark probes, because those probes construct
    the runtime graph/state directly through `GRCV3.from_state(...)`
  - under that pure-runtime path the same baseline spark backend remains
    demonstrably active:
    - `single-node` still crosses the full spark path:
      - `spark_candidate`
      - `split_init`
      - `spark`
      - `split_progress`
      - `split_complete`
    - `three-node` still crosses the partial spark path:
      - `spark_candidate`
      - `split_init`
      - `spark_pending`
      - then split progression/completion without satisfying the stricter
        completion criterion
  - this pure-runtime rerun therefore confirms the same constitutive
    conclusion as the earlier comparison:
    - the failure in Gate B is not a missing `GRCV3` spark loop
    - it remains a seed-to-runtime lowering limitation
- Explicit lane comparison:
  - pure-runtime lane:
    - the control probes construct a directly sparkable weak-axis interior
      state
    - `single-node` starts from:
      - `gradient_norm = 0.0`
      - signed Hessian spectrum `[0.0001, 2.0]`
    - and immediately crosses:
      - `spark_candidate`
      - `split_init`
      - `spark`
    - the `three-node` probe likewise reaches:
      - `spark_candidate`
      - `split_init`
      - `spark_pending`
  - projected rich-seed lane:
    - the broadened `grcv3.rich.v2` seed lowers into a richer runtime carrier
      (`24` nodes / `36` edges) with explicit basin supports, channel chains,
      and ridge support arcs
    - but its lowest-gradient node is a boundary-support extremum rather than
      a sparkable interior probe:
      - `primitive = upper_membrane`
      - `role = ridge_support`
      - `gradient_norm = 0.0`
      - signed Hessian spectrum `[-0.0, -0.0]`
    - meanwhile the nodes carrying stronger anisotropic curvature remain far
      above the baseline gradient gate:
      - `core_basin` support nodes sit around `grad ≈ 0.248..0.298`
      - while `eps_gradient = 0.001`
  - constitutive interpretation:
    - the projector now succeeds structurally:
      - richer topology
      - richer support roles
      - richer channel/boundary attachment
    - but it still fails constitutively:
      - it does not lower into the same sparkable weak-axis interior regime
        that pure runtime `GRCV3` can represent directly
      - the unresolved gap is therefore not “missing topology,” but missing
        constructive interior geometry in the source contract / lowering path
- Broadened rich-seed diagnostic outcome:
  - the `grcv3.rich.v2` probe now lowers into a materially richer runtime
    surface (`24` nodes / `36` edges) with explicit basin-role supports,
    channel chains, and boundary support arcs
  - the lowest-gradient node is now an explicit `upper_membrane` ridge-support
    node with `grad=0`, but its signed spectrum remains flat
    (`eig=[-0.0, -0.0]`), so it still does not qualify as a geometric seed
  - the intended `core_basin` support nodes do now carry strong anisotropic
    curvature, but their gradients remain far above the baseline
    `eps_gradient=1e-3` gate, so they also do not validate as basin seeds
  - over a 40-step diagnostic run the broadened seed remains at:
    - `geometric_seed_count=0`
    - `geometric_validated_basin_count=0`
    - `spark_event_count=0`
    - `candidate_count=0`
- Manual-probe comparison:
  - the `single-node` manual probe still crosses the full spark path under the
    same baseline thresholds: `spark_candidate -> split_init -> spark ->
    split_progress -> split_complete`
  - the `three-node` manual probe still crosses the candidate/init path and
    remains `spark_pending`
  - this keeps the causal diagnosis the same as in Iteration 5: the spark loop
    works, but the seed-driven lowered geometry still does not reach the needed
    constitutive regime honestly through the projector boundary
- Gate outcome:
  - Gate B: `FAIL`
    - the broadened `grcv3.rich.v2` vocabulary improves topology and local-role
      attachment honesty, but it still does not produce geometric seeds or
      spark candidates under the unchanged baseline thresholds
    - the remaining gap is now narrower and more specific:
      - richer support geometry alone is not sufficient
      - the source contract still lacks whatever additional constructive
        semantics are needed to drive a sparkable weak-axis interior rather
        than a flat boundary-support extremum

### Verification

- [x] The rerun result is attributable to the broadened rich vocabulary
- [x] The comparison against manual probes is written down explicitly
- [x] Gate B is recorded as pass/fail after the rerun

### Summary

Iteration 10 closes with another honest Gate B failure. The broadened
`grcv3.rich.v2` surface clearly improves the lowered geometry and local
attachment semantics, but under the same baseline thresholds it still does not
generate a geometric seed or spark candidate. The failure is now better
localized: the projector can realize richer support structure, yet the source
contract still does not encode enough constructive interior geometry to produce
the sparkable weak-axis regime that the manual probes demonstrate. A direct
pure-runtime rerun confirms the control side of that diagnosis: raw `GRCV3`
still produces the expected spark lifecycle when the geometry-bearing runtime
state is constructed explicitly, so the unresolved gap remains squarely at the
seed/lowering boundary rather than in the runtime spark machinery itself. The
side-by-side lane comparison makes the difference precise: the projected lane
is now structurally richer, but the pure lane is still the only one that
actually realizes a sparkable interior weak-axis state.

## Iteration 11. Generalization And Gate C Decision

### Goal

Decide whether the broadened capability is still only a probe path or is now
broad enough to justify the full `GRCL-v3` commitment.

### Checks

- [x] Verify the projector now supports more than one handcrafted constitutive
  case
- [x] Verify at least one richer seed beyond the minimal junction probe lowers
  honestly
- [x] Decide explicitly whether Gate C passes or fails
- [x] Record the next project decision based on that result

### Implementation Notes

- This iteration is the commitment boundary.
- If Gate C still fails, the broadened path may remain a probe without being
  called full `GRCL-v3`.
- Evidence carried into this decision:
  - `grcv3.rich.v2` now generalizes beyond the original junction-only probe to
    cover:
    - basin-local geometry
    - junction/saddle-local geometry
    - interface/channel realization
    - boundary/ridge realization
  - the native-lowering refactor also proves that `grcv3.rich.v2+` is no longer
    a thin compatibility alias; it is a real family-native lane
- However, the commitment criterion is stricter than “schema breadth exists.”
  It also requires that the broadened capability is not merely a special-case
  probe surface.
- Generalization assessment:
  - criterion 1: “more than one handcrafted constitutive case”
    - `PASS`
    - there is now more than one rich constitutive surface:
      - the original minimal junction probe
      - the broadened basin/boundary/channel probe
    - and the projector/lowering code now supports more than one local motif
      family
  - criterion 2: “at least one richer seed beyond the minimal junction probe
    lowers honestly”
    - `FAIL`
    - the broadened `grcv3.rich.v2` seed lowers structurally and honestly into
      a richer runtime carrier
    - but it still does not lower honestly into a sparkable weak-axis interior
      regime under the unchanged baseline thresholds
    - therefore the broadened seed is still evidence of projector-facing
      expressivity, not yet evidence of fully sufficient constitutive lowering
- Gate decision:
  - Gate C: `FAIL`
    - the broadened capability is real and valuable
    - but it is still a probe-capability lane rather than a justified “full
      `GRCL-v3` capability” claim
- Next project decision:
  - keep the broadened `grcv3.rich.v2+` surface as the accepted projector-facing
    and family-native probe layer
  - do **not** call the current state full `GRCL-v3`
  - next work should target the now-localized missing piece:
    - constructive interior geometry semantics that can lower into a sparkable
      weak-axis interior state
  - this means the next justified lane is:
    - richer family-native `GRCV3` source semantics
    - not further branding/generalization of the current probe surface as
      complete

### Verification

- [x] The Gate C decision is written down explicitly
- [x] The commitment boundary is recorded in both plan and checklist terms
- [x] The outcome is actionable rather than implied

### Summary

Closed. Gate C is explicitly `FAIL`. The broadened `grcv3.rich.v2+` lane is no
longer just a single handcrafted junction probe and now covers basin, channel,
and boundary-local geometry as a real family-native lowering surface. But that
is still not enough to justify the full `GRCL-v3` commitment, because no richer
seed beyond the original probe yet lowers honestly into the sparkable interior
regime that pure runtime `GRCV3` can realize directly. The accepted outcome is
therefore: keep the current lane as a real probe-capability surface, and direct
future work toward constructive interior geometry rather than claiming full
`GRCL-v3` closure prematurely.

## Exit Condition

This checklist closes only when one of the following is recorded explicitly:

1. **Pass**
   - the first minimal rich seed preserves enough geometry to justify broader
     `GRCL-v3` implementation work

2. **Fail**
   - the first minimal rich seed still cannot preserve the required geometry,
     and the failure is documented precisely enough to justify a revised
     vocabulary or a narrower constitutive target

Anything weaker than that should not be treated as completion.

## Recorded Example. Rich-v3 Collapse Fixture

The first dedicated rich-v3 collapse example is now recorded as:

- `configs/landscapes/seed/grcv3-rich-collapse-example.seed.yaml`

What it records:

- the same explicit branch-ordered hostless routing core used in the verified
  rich-v1 junction probe lane
- a source-side geometry construction that can enter a choice regime and then
  collapse under a documented runtime envelope

What it does not do:

- encode collapse as source truth
- extend the `grcv3.rich.v1` contract with runtime-backend parameters

The recorded runtime envelope for the example is:

- `profile_name = "hot_exploratory"`
- `choice = sink_compatibility`
- `epsilon_choice = 0.15`
- `epsilon_collapse = 0.14`

Observed baseline transition:

- `choice_detected` on steps `1` and `2`
- `collapse` on step `3`
- later re-entry into new choice regimes is allowed and remains consistent with
  the RC/GRC choice semantics being studied

## Iteration 12. Lock The Third Capability Slice

### Goal

Define the next accepted rich contract explicitly as `grcv3.rich.v3` and make
the direct-assembly target concrete before implementation resumes.

### Checks

- [x] Version the interior-shaping follow-on as `grcv3.rich.v3`
- [x] Lock which `primitive.extensions.grcv3.interior_geometry` fields become
      executable first
- [x] Keep the forbidden solved-state boundary explicit in the checklist
- [x] Record the direct-family-native-assembly target for `grcv3.rich.v3+`

### Implementation Notes

- This iteration should define the contract before parser or lowering work
  begins.
- The new slice should remain constructive and source-side.
- It must not allow solved differential or transport state to leak into the
  seed.
- Locked first executable `interior_geometry` field set:
  - `probe_mode`
  - `support_profile`
  - `attachment_isolation`
  - `interior_clearance_class`
  - `support_connectivity`
  - `support_role_groups`
- Locked first executable semantics:
  - `support_profile` must cover the full declared local-role universe
  - `support_role_groups` must partition the full declared local-role universe
  - `probe_mode` must agree with `local_geometry.center_role`
  - `grcv3.rich.v3+` is the point where `GRCV3` should move toward direct
    family-native assembly rather than projector-style reinterpretation

### Verification

- [x] The `rich.v3` slice is named explicitly in the vocabulary, plan, and
      checklist
- [x] The first executable `interior_geometry` field set is narrow and
      defensible

### Summary

`grcv3.rich.v3` is now locked as the third capability slice. The first
executable `interior_geometry` surface stays constructive and narrow, and the
architecture target is explicit: mature `grcv3.rich.v3+` should move toward
direct family-native assembly rather than projector-style reinterpretation.

## Iteration 13. Validation And Fixture Lift For `grcv3.rich.v3`

### Goal

Make the third slice real at the schema and validation layer.

### Checks

- [x] Add typed parsing/validation for `interior_geometry`
- [x] Reject malformed or contradictory `interior_geometry` payloads
- [x] Add at least one dedicated `grcv3.rich.v3` spark-oriented probe seed
- [x] Keep weaker contracts (`grcv3.rich.v1` / `grcv3.rich.v2`) stable

### Implementation Notes

- This iteration should stop at schema/validation plus seed fixtures.
- It should not yet broaden into runtime compensation or relaxed thresholds.
- Added typed `GRCV3RichInteriorGeometry` parsing under
  `src/pygrc/landscapes/extensions/grcv3.py`.
- The first validation rules are intentionally strict:
  - `support_profile` keys must match the declared local-role universe exactly
  - `support_role_groups` must be non-overlapping and cover that universe
  - `probe_mode` must agree with `local_geometry.center_role`
  - `interface_roles_only` attachment requires declared interfaces
- Added the dedicated YAML fixture:
  - `configs/landscapes/seed/grcv3-rich-v3-interior-spindle-probe.seed.yaml`
- Existing `grcv3.rich.v1` and `grcv3.rich.v2` fixtures remain part of the
  regression set.
- Language boundary clarified from runtime probing:
  - `interfaces.branch_targets` are not generic adjacency labels
  - they currently bind only to incident valley/channel neighbors of a
    junction/saddle branch surface
  - ridge-adjacent shells must be represented through boundary-side vocabulary,
    not through `branch_targets`

### Verification

- [x] Valid `grcv3.rich.v3` payloads parse cleanly
- [x] Invalid `grcv3.rich.v3` payloads fail explicitly
- [x] Existing rich-v1/rich-v2 fixtures still load and validate

### Summary

The `grcv3.rich.v3` schema/validation layer is now real. `interior_geometry`
is typed and strictly validated, and a dedicated spark-oriented YAML probe
exists, while runtime lowering remains intentionally untouched until the next
batch.

## Iteration 14. Direct Interior-Geometry Assembly

### Goal

Implement the first direct family-native assembly path for
`primitive.extensions.grcv3.interior_geometry`.

### Checks

- [x] Assemble support-role groups deterministically from `interior_geometry`
- [x] Realize support-spacing / confinement asymmetry from `support_profile`
- [x] Implement attachment-isolation handling deterministically
- [x] Emit diagnostics showing how the declared interior motif was assembled

### Implementation Notes

- This is the first slice that should move beyond projector-style
  reinterpretation and toward direct family-native assembly.
- The assembly path should remain deterministic and inspectable.
- `GRCV3NativeBasinLikePlan` now carries typed `interior_geometry` directly.
- Native basin lowering now changes:
  - support radii by role from `support_profile`
  - support spoke weights with explicit clearance scaling
  - support-support topology from `support_connectivity`
  - support-pair grouping from `support_role_groups`
- Native ridge/valley attachment now respects the declared attachment policy:
  - `center_allowed` keeps anchor fallback available
  - `support_only` / `interface_roles_only` suppress silent center fallback
- Diagnostics now surface through:
  - `landscape_grcv3_interior_geometry_summary`
  - `landscape_runtime_assembly_summary["interior_geometry_primitive_ids"]`
  - explicit `landscape_grcv3_lowering_notes` for the `rich.v3` path

### Verification

- [x] The assembled motif reflects the declared interior roles directly
- [x] No solved runtime state is injected through the seed
- [x] The new path is artifact-diagnosable rather than hidden

### Summary

Direct `rich.v3` interior assembly is now executable. The native basin patch no
longer lowers as a symmetric support ring when `interior_geometry` is present;
it now realizes role-indexed support spacing, role-group connectivity, and
attachment-policy constraints directly in the family-native assembly path.

## Iteration 15. Weak-Axis Spark Gate

### Goal

Test whether the first `grcv3.rich.v3` direct-assembly seed can move from a
valid interior geometric seed into an actual spark-candidate regime.

### Checks

- [x] Rerun the spark-oriented `grcv3.rich.v3` seed against the baseline
      thresholds
- [x] Compare the result against the basin-centered weak-axis `rich.v2` probe
- [x] Record the gate outcome classification explicitly
- [x] Record the next missing constructive field explicitly if the gate still
      fails

### Implementation Notes

- This gate should remain honest.
- A pass must come from richer constructive interior semantics and direct
  assembly, not from threshold loosening.
- Reproducible gate envelope used for comparison:
  - `profile_name = seed_baseline`
  - default `GRCV3` thresholds
  - `num_steps = 50`
- Comparison result:
  - `rich.v2` basin-centered probe:
    - `geometric_seed_count = 1`
    - `validated_basin_count = 1`
    - `spark_candidate_events = 0`
    - `spark_events = 0`
  - `rich.v3` direct-assembly spindle probe:
    - `geometric_seed_count = 0`
    - `validated_basin_count = 0`
    - `spark_candidate_events = 0`
    - `spark_events = 0`
- Recorded gate classification:
  - `rich.v2` remains an honest validated-seed / non-spark near-miss
  - `rich.v3` direct assembly is a different near-miss:
    - near-degenerate anchor Hessian
    - but not a validated geometric seed because the center remains too gradient-loaded
- The direct `rich.v3` assembly changed the local stencil honestly:
  - support-only attachment is enforced
  - support-support connectivity became spindle-like rather than ring-like
  - the anchor Hessian moved very close to degeneracy
- But the center still failed the low-gradient condition:
  - the `spindle_core` anchor remained too gradient-loaded to qualify as a
    geometric seed
- The next missing constructive field is now narrower:
  - we need an explicit way to separate interior probe shielding from
    support-surface load routing
  - in practice this points toward a stronger constructive group than the
    current first `interior_geometry` slice, likely a two-tier interior
    structure or equivalent load-partition semantics

### Verification

- [x] The result is reproducible under the documented profile/envelope
- [x] The gate outcome is recorded explicitly as pass/fail or near-miss

### Summary

Iteration 15 closed as an honest near-miss rather than a pass. `rich.v3`
direct assembly is materially different from `rich.v2`, but it still does not
reach a sparkable weak-axis interior under baseline thresholds. The missing
piece is no longer generic “more richness”; it is a more precise constructive
way to keep the center low-gradient while the support surface carries the load.

## Iteration 16. Lock The Interior-Partition Slice

### Goal

Define the next constructive source group that follows the first executable
`interior_geometry` slice.

### Checks

- [x] Lock `primitive.extensions.grcv3.interior_partition` as the next
      vocabulary group
- [x] Lock the first allowed executable field set for `interior_partition`
- [x] Keep the solved-state boundary explicit
- [x] Record why this is a new group rather than a silent expansion of
      `support_profile`

### Implementation Notes

- This iteration should stay theory-facing.
- The new group exists because the remaining failure mode is about
  probe-versus-load layering, not just support spacing.
- Locked first executable field set:
  - `partition_mode`
  - `load_role_groups`
  - `load_transfer_mode`
  - `probe_protection_class`
  - `attachment_transfer_roles`
- Locked first scope:
  - basin-centered probes that already use `interior_geometry`
  - ridge/valley load routing into that basin-centered structure
- Explicitly out of scope for the first executable slice:
  - `probe_shell_count`
  - arbitrary multi-shell constructions
  - junction-specific partition semantics
- Why this is a separate group:
  - `support_profile` changes spacing / confinement on one support surface
  - `interior_partition` changes which tier is allowed to carry load before it
    reaches the probe
  - those are different constitutive questions and should stay separately
    visible in the language

### Verification

- [x] The vocabulary, plan, and checklist all name the new group explicitly
- [x] The first field set is constructive and narrow

### Summary

Iteration 16 is now locked. `interior_partition` is the next source-side group,
and its first executable slice stays narrow: it declares the outer load-bearing
tier and transfer policy for basin-centered probes without broadening into
general multi-shell motif authoring.

## Iteration 17. Validation And Fixture Lift For Interior Partition

### Goal

Make the next constructive group real at the parser/fixture layer before
runtime lowering expands again.

### Checks

- [x] Add typed parsing/validation for `interior_partition`
- [x] Reject contradictory probe/load partition payloads
- [x] Add one dedicated probe seed that uses both `interior_geometry` and
      `interior_partition`
- [x] Keep existing `rich.v1` / `rich.v2` / first `rich.v3` fixtures stable

### Implementation Notes

- This iteration should still stop short of new runtime assembly.
- The purpose is to freeze the next semantics before code starts consuming
  them.
- Added typed `GRCV3RichInteriorPartition` parsing under
  `src/pygrc/landscapes/extensions/grcv3.py`.
- Locked first validation boundary:
  - `interior_partition` is currently supported only for basin/plateau
    primitives with `local_geometry.center_role = interior_probe`
  - `interior_partition` requires `interior_geometry` to exist first
  - `load_role_groups` currently cover the declared local-role universe so the
    outer load-bearing tier is unambiguous in the first executable slice
  - `attachment_transfer_roles` must belong to the declared outer load-bearing
    roles
  - `single_surface` requires `direct_open` plus `probe_protection_class = open`
  - `shielded` is incompatible with `direct_open`
- Added the dedicated YAML fixture:
  - `configs/landscapes/seed/grcv3-rich-v3-partitioned-spindle-probe.seed.yaml`
- Existing `rich.v1`, `rich.v2`, and first `rich.v3` fixtures remain part of
  the regression set.

### Verification

- [x] Valid `interior_partition` payloads parse cleanly
- [x] Invalid partition payloads fail explicitly
- [x] Existing fixtures remain stable

### Summary

Iteration 17 is now real at the schema layer. `interior_partition` is typed,
strictly validated, and exercised through a dedicated YAML probe, while runtime
assembly remains intentionally unchanged until the next batch.

## Iteration 18. Two-Tier Native Assembly And Spark Gate

### Goal

Test whether a source-declared inner-probe / outer-load partition can preserve
both low-gradient interior behavior and weak-axis degeneracy.

### Checks

- [x] Implement the first native `interior_partition` assembly path
- [x] Rerun the weak-axis gate under the same baseline envelope
- [x] Compare the result against:
  - [x] the `rich.v2` validated-seed near-miss
  - [x] the first `rich.v3` near-degenerate/high-gradient near-miss
- [x] Record the next missing constructive field explicitly if this still
      fails

### Implementation Notes

- This gate should remain honest.
- The target is not “make a spark at any cost.”
- The target is a more truthful source-side construction of probe shielding
  versus load-bearing surface.
- Implemented first native `interior_partition` path:
  - `src/pygrc/models/grc_v3_landscape.py`
  - `src/pygrc/models/grc_v3_landscape_native.py`
  - `tests/models/test_grc_v3_landscape_runtime.py`
- Locked first runtime meaning:
  - existing `interior_geometry` support nodes remain the inner probe shell
  - `interior_partition` adds a second outer load shell with the same role
    order
  - transport and boundary attachments resolve against the outer load shell
  - basin-patch spokes and support-support connectivity still use the inner
    probe shell as the weak-axis stencil
  - explicit probe-to-load transfer edges are added according to
    `attachment_transfer_roles`
- Added artifact/runtime diagnostics:
  - `landscape_grcv3_probe_role_node_ids_by_primitive_id`
  - `landscape_grcv3_load_role_node_ids_by_primitive_id`
  - `landscape_grcv3_interior_partition_summary`
  - `landscape_runtime_assembly_summary["interior_partition_primitive_ids"]`
- Reproducible gate envelope used for comparison:
  - `profile_name = seed_baseline`
  - default `GRCV3` thresholds
  - `num_steps = 50`
- Gate comparison result:
  - `grcv3-rich-weak-axis-basin-spark-probe.seed.yaml`
    - `geometric_seed_count = 1`
    - `geometric_validated_basin_count = 1`
    - `spark_candidate_events = 0`
    - `spark_events = 0`
    - center gradient norm after 50 steps: `~1.8e-06`
  - `grcv3-rich-v3-interior-spindle-probe.seed.yaml`
    - `geometric_seed_count = 0`
    - `geometric_validated_basin_count = 0`
    - `spark_candidate_events = 0`
    - `spark_events = 0`
    - center gradient norm after 50 steps: `~5.53e-01`
  - `grcv3-rich-v3-partitioned-spindle-probe.seed.yaml`
    - `geometric_seed_count = 0`
    - `geometric_validated_basin_count = 0`
    - `spark_candidate_events = 0`
    - `spark_events = 0`
    - center gradient norm after 50 steps: `~5.72e-01`
- Interpretation:
  - the first two-tier shell is real and observable
  - but it still does not restore a low-gradient center
  - the center Hessian changes materially, yet the center remains too
    gradient-loaded to become a validated geometric seed
- Narrowed next missing constructive field:
  - role-aligned inner/outer shells are still too coupled
  - the next source-side field likely needs to express non-coincident
    load-carrier placement or transfer topology, so attachment load can land on
    outer shell carriers without projecting straight back onto the same
    probe-axis stencil

### Verification

- [x] The result is reproducible under the documented baseline envelope
- [x] The outcome is recorded explicitly as pass, near-miss, or failure

### Summary

Iteration 18 closed as another honest near-miss, not a pass. The first native
`interior_partition` slice successfully separated the runtime into an inner
probe shell and an outer load shell, and artifact diagnostics now expose that
split explicitly. But under the same baseline gate envelope the partitioned
probe still produced:

- no validated geometric seed
- no spark candidates
- no sparks

So `interior_partition` improved the source/runtime vocabulary boundary, but it
did not yet solve the remaining constructive problem. The next justified step
is not threshold loosening. It is richer source-side control over how outer
load carriers are placed and how transfer from load shell to probe shell is
topologically mediated.

## Iteration 19. Lock The Load-Carrier Slice

### Goal

Define the next constructive group after `interior_partition` explicitly, so
the next strengthening remains source-side and does not leak back into runtime
heuristics.

### Checks

- [x] Lock `primitive.extensions.grcv3.interior_load_carriers` as the next
      theory-facing vocabulary group
- [x] Lock the first allowed executable field set:
  - [x] `carrier_layout_mode`
  - [x] `carrier_anchor_policy`
  - [x] `transfer_topology_mode`
  - [x] `transfer_role_pairs`
  - [x] `carrier_attachment_roles`
- [x] Keep the solved-state boundary explicit
- [x] Keep the first scope narrow:
  - [x] basin-centered interior probes already using `interior_geometry`
  - [x] basin-centered interior probes already using `interior_partition`

### Implementation Notes

- This slice should answer a more precise question than Iteration 18:
  - not merely “which tier takes load?”
  - but “where do the load-bearing carriers sit, and how do they couple back to
    the probe shell?”
- The goal is not free-form graph authoring.
- The goal is explicit constructive control over:
  - carrier placement relative to the probe shell
  - carrier-to-probe transfer topology
  - attachment ingress onto the carrier layer
- Locked vocabulary location:
  - `primitive.extensions.grcv3.interior_load_carriers`
- Locked first executable field set:
  - `carrier_layout_mode`
  - `carrier_anchor_policy`
  - `transfer_topology_mode`
  - `transfer_role_pairs`
  - `carrier_attachment_roles`
- Locked first-slice scope:
  - basin/plateau only
  - `grcv3.rich.v3` only
  - requires:
    - `local_geometry.center_role='interior_probe'`
    - `interior_geometry`
    - `interior_partition`
- Locked solved-state boundary:
  - no solved carrier coordinates as runtime truth
  - no solved transfer weights
  - no solved gradients/Hessians/fluxes
  - no explicit spark/collapse labels

### Verification

- [x] The new group is stated explicitly in the vocabulary
- [x] The first executable slice is narrow enough to validate cleanly
- [x] The next iteration boundary is clear from the checklist alone

### Summary

Iteration 19 is now locked. The next source-side strengthening is no longer
about tier membership, but about explicit load-carrier placement and mediation.
The first executable slice stays narrow enough that later failures remain
diagnostic rather than becoming free-form graph-authoring noise.

## Iteration 20. Validation And Fixture Lift For Load Carriers

### Goal

Make the next constructive group real at the schema and fixture layer before
runtime lowering changes resume.

### Checks

- [x] Add typed parsing/validation for `interior_load_carriers`
- [x] Add explicit rejection for contradictory carrier-layout payloads
- [x] Add explicit rejection for contradictory transfer-topology payloads
- [x] Add one dedicated probe seed that uses:
  - [x] `interior_geometry`
  - [x] `interior_partition`
  - [x] `interior_load_carriers`
- [x] Keep existing `rich.v1` / `rich.v2` / `rich.v3` fixtures stable

### Implementation Notes

- The first validator should prefer “consume or fail” over fallback.
- The first fixture should stay small enough that the carrier-vs-probe geometry
  remains interpretable by inspection.
- This iteration should not yet claim that the new slice is enough to spark.
- It only needs to make the language and fixture boundary real.
- Implemented parser boundary:
  - `src/pygrc/landscapes/extensions/grcv3.py`
- Added typed field:
  - `GRCV3RichInteriorLoadCarriers`
- Added first validator rules:
  - supported only for basin/plateau primitives
  - supported only for `grcv3.rich.v3`
  - requires `interior_geometry`
  - requires `interior_partition`
  - requires `local_geometry.center_role='interior_probe'`
  - `carrier_attachment_roles` must belong to the declared outer load-role universe
  - `transfer_role_pairs` must be explicit, unique, and cover all attachment roles
  - `group_bridge` pairs must stay inside one support-role group
  - `nearest_probe_role` requires identity carrier/probe pairs
  - `cross_axis_bridge` requires at least one non-identity pair
  - `group_centroid` anchor policy requires `group_midpoints` or `staggered_arc`
- Added dedicated fixture:
  - `configs/landscapes/seed/grcv3-rich-v3-load-carrier-spindle-probe.seed.yaml`
- Updated fixture index:
  - `configs/landscapes/seed/README.md`
- Added tests:
  - extraction of valid load-carrier payloads
  - rejection when `interior_partition` is missing
  - rejection of invalid `group_bridge` cross-group transfer pairs
  - deterministic parsing of the YAML fixture
- Test command:
  - `source .venv/bin/activate && python -m unittest tests.landscapes.test_grcv3_extensions`
- Result:
  - `Ran 22 tests ... OK`

### Verification

- [x] Valid `interior_load_carriers` payloads parse cleanly
- [x] Invalid `interior_load_carriers` payloads fail explicitly
- [x] The first dedicated fixture is deterministic and shareable

### Summary

Iteration 20 is now real at the schema/fixture layer. `interior_load_carriers`
is typed, validated, and documented by a dedicated rich-v3 probe seed. The next
runtime step can now consume a stable source contract rather than inventing one
while lowering.

## Iteration 21. Carrier-Aware Native Assembly And Spark Gate

### Goal

Test whether non-coincident load-carrier placement plus explicit transfer
topology can restore a low-gradient center while preserving weak-axis
degeneracy.

### Checks

- [x] Implement the first native `interior_load_carriers` assembly path
- [x] Rerun the weak-axis gate under the documented baseline envelope
- [x] Compare the result against:
  - [x] the `rich.v2` validated-seed near-miss
  - [x] the first `rich.v3` high-gradient near-miss
  - [x] the partitioned `rich.v3` two-tier near-miss
- [x] Record the next missing constructive field explicitly if this still
      fails

### Implementation Notes

- This gate should stay honest for the same reason as Iterations 15 and 18.
- The target is not “invent a spark.”
- The target is a more truthful source-side construction of:
  - non-coincident outer load carriers
  - explicit carrier-to-probe transfer topology
  - attachment ingress onto the carrier layer before probe influence
- Implemented first native `interior_load_carriers` path:
  - `src/pygrc/models/grc_v3_landscape_native.py`
  - `src/pygrc/models/grc_v3_landscape.py`
  - `tests/models/test_grc_v3_landscape_runtime.py`
- Locked first runtime meaning:
  - when `interior_load_carriers` is present, the outer attachment-facing layer
    is realized as explicit non-coincident carrier nodes
  - the probe shell remains the same weak-axis stencil used for basin-patch
    coupling
  - external channel and boundary attachments resolve against carrier nodes
  - carrier-to-probe influence is mediated only through explicit
    `transfer_role_pairs`
- Added artifact/runtime diagnostics:
  - `landscape_grcv3_carrier_role_node_ids_by_primitive_id`
  - `landscape_grcv3_interior_load_carrier_summary`
  - `landscape_runtime_assembly_summary["interior_load_carrier_primitive_ids"]`
- Added runtime regression:
  - `test_grcv3_rich_v3_load_carrier_probe_realizes_noncoincident_carriers`
- Reproducible gate envelope used for comparison:
  - `profile_name = seed_baseline`
  - default `GRCV3` thresholds
  - `num_steps = 50`
- Gate comparison result:
  - `grcv3-rich-weak-axis-basin-spark-probe.seed.yaml`
    - `geometric_seed_count = 1`
    - `geometric_validated_basin_count = 1`
    - `spark_candidate_events = 0`
    - `spark_events = 0`
    - center gradient norm after 50 steps: `~1.8e-06`
  - `grcv3-rich-v3-interior-spindle-probe.seed.yaml`
    - `geometric_seed_count = 0`
    - `geometric_validated_basin_count = 0`
    - `spark_candidate_events = 0`
    - `spark_events = 0`
    - center gradient norm after 50 steps: `~5.53e-01`
  - `grcv3-rich-v3-partitioned-spindle-probe.seed.yaml`
    - `geometric_seed_count = 0`
    - `geometric_validated_basin_count = 0`
    - `spark_candidate_events = 0`
    - `spark_events = 0`
    - center gradient norm after 50 steps: `~5.72e-01`
  - `grcv3-rich-v3-load-carrier-spindle-probe.seed.yaml`
    - `geometric_seed_count = 0`
    - `geometric_validated_basin_count = 0`
    - `spark_candidate_events = 0`
    - `spark_events = 0`
    - center gradient norm after 50 steps: `~5.72e-01`
- Interpretation:
  - the first carrier-aware assembly is real and visible in runtime artifacts
  - but under the first executable meaning it behaves almost identically to the
    partitioned near-miss
  - the center remains too gradient-loaded to become a validated geometric seed
- Narrowed next missing constructive field:
  - non-coincident carrier placement alone is not enough when transfer remains
    effectively identity-preserving
  - the next source-side step likely needs stronger expressive control over
    carrier-to-probe remapping or transfer weighting, so load ingress can stop
    collapsing back into the same role-indexed probe coupling pattern
  - a narrower follow-on sweep around the best current near-miss confirms that
    remapping matters, but also shows a local ceiling inside the current
    `rich.v3` slice:
    - `scripts/sweep_grcv3_transfer_gradient.py`
    - `configs/landscapes/seed/grcv3-rich-v3-load-carrier-weak-to-stable-probe.seed.yaml`
    - identity transfer stays in the `~5.72e-01` center-gradient regime with a
      stable eigenvalue near `1.78e-06`
    - all tested non-identity remaps move to a better but still insufficient
      regime around:
      - center gradient `~5.40e-01`
      - stable eigenvalue `~6.07e-04`
    - therefore the remaining gap is no longer just “choose a better transfer
      permutation”; it is likely a stronger source-side control over transfer
      mediation itself

### Verification

- [x] The result is reproducible under the documented baseline envelope
- [x] The outcome is recorded explicitly as pass, near-miss, or failure

### Summary

Iteration 21 closed as another honest near-miss. The first
`interior_load_carriers` slice successfully moved the attachment-facing outer
layer onto explicit non-coincident carrier nodes and preserved explicit
carrier-to-probe transfer topology in runtime artifacts. But under the same
baseline gate envelope it did not improve the center regime materially beyond
the partitioned `rich.v3` result:

- no validated geometric seed
- no spark candidates
- no sparks

So the new slice improved source/runtime honesty again, but it still did not
cross the spark gate. The next justified move is not runtime compensation. It
is stronger source-side control over how carrier transfer remaps or weights load
before it reaches the probe shell. A follow-on transfer-focused sweep confirms
that point more sharply: non-identity remaps clearly improve the Hessian
regime, but they all plateau in roughly the same still-too-gradient-loaded
state, which is exactly the kind of evidence rich.v4 should now be designed
around.

## Short Retrospective

The main lesson from this checklist is that the first `GRCV3` source problem
was not “the runtime cannot spark.” It was “the weaker source/lowering path
cannot yet express enough interior geometry to reach the sparkable regime
honestly.”

What this checklist established clearly:

- pure runtime `GRCV3` probes can realize spark/collapse-capable local states
- compatibility/enrichment lowering is useful, but it has a real semantic limit
- broadening `grcv3.rich.v2+` helped, but did not by itself justify claiming
  full `GRCL-v3` closure
- once richer source semantics exist, `GRCV3` should prefer family-native
  lowering rather than continued semantic dependence on a `GRCV2`-shaped
  meaning layer
- if `rich.v4` is opened, it should be opened only as a direct-translation
  contract with no projector-style semantic lowering

That means later `GRCL-v3` work should not reopen baseline `GRCV3` runtime
equations casually. The next justified work is richer source semantics and
lowering precision, not runtime compensation for weak seeds.

## Iteration 22. Lock The `rich.v4` Direct-Translation Boundary

### Goal

Define the first post-`rich.v3` lane explicitly as `grcv3.rich.v4` and make
the no-lowering rule executable before any new schema or runtime work starts.

### Checks

- [x] Version the next lane explicitly as `grcv3.rich.v4`
- [x] Record that `rich.v4` is a direct-translation-only contract
- [x] Record that `rich.v4` must not depend on:
  - [x] projector-style semantic lowering
  - [x] compatibility-path blueprint authority
  - [x] heuristic recovery of underspecified interior meaning
- [x] Define the first intended semantic gap `rich.v4` is allowed to address:
  - [x] the center-gradient plateau that remained after `rich.v3`
        transfer-remap sweeps
- [x] Record the first allowed field family only in terms of semantics that can
      be translated directly into native assembly:
  - [x] `primitive.extensions.grcv3.transfer_mediation`
  - [x] first executable field set:
    - [x] `mediation_mode`
    - [x] `pair_mediation_classes`
    - [x] `probe_guard_class`
    - [x] `lateral_spill_policy`
- [x] Record the theory-facing correctness rule for the first `rich.v4` slice:
  - [x] it may shape ingress structure
  - [x] it may not override the normal `GRCV3` conductance / potential / flux
        loop

### Implementation Notes

- This iteration is a contract-lock step, not a code step.
- The purpose is to stop `rich.v4` from becoming “one more projector
  refinement.”
- Any proposed field that only gives the projector more room to guess should be
  treated as out of bounds.
- Locked first `rich.v4` semantic family:
  - `primitive.extensions.grcv3.transfer_mediation`
- Rationale:
  - `rich.v3` geometry, partition, and carrier placement already exposed the
    remaining near-miss honestly
  - non-identity transfer remaps improved Hessian behavior but plateaued in
    nearly the same still-too-gradient-loaded regime
  - therefore the next missing source-side degree of freedom is not “more
    geometry” but direct control over transfer mediation itself
- Locked first executable meanings:
  - every declared `transfer_role_pair` must receive an explicit mediation class
  - no omitted pair may be synthesized by projector logic
  - no mediation class may be inferred from geometry alone
  - `transfer_mediation` is theory-correct only if it remains a source-side
    structural constraint on ingress, not a constitutive transport override
  - the new slice is allowed to describe:
    - transfer attenuation class
    - probe guarding class
    - lateral spill constraint
  - the new slice is not allowed to describe:
    - solved numeric transfer weights
    - solved flux schedules
    - runtime transport outcomes
    - direct `w_ij` / `Phi_i` / `J_ij` prescriptions disguised as mediation

### Verification

- [x] The direct-translation rule is written explicitly in the plan,
      vocabulary, and checklist terms
- [x] The intended `rich.v4` target is narrower than “general source richness”

### Summary

Iteration 22 is now locked. `grcv3.rich.v4` is defined as a
direct-translation-only lane, and its first justified semantic family is
`transfer_mediation`, not another geometry-profile or projector-refinement
surface. The allowed scope is deliberately narrow: explicit mediation class on
already-declared transfer pairs, explicit probe guarding, and explicit lateral
spill policy. Anything weaker would drift back into projector guessing, which
is exactly what `rich.v4` is meant to forbid.

## Iteration 23. Validation And Fixture Lift For `rich.v4`

### Goal

Make the first `rich.v4` slice real at the schema and fixture layer without
reintroducing projector-style interpretation.

### Checks

- [x] Add typed parsing/validation for the first `grcv3.rich.v4` field group
- [x] Add explicit rejection for underdetermined `rich.v4` payloads
- [x] Add one dedicated `rich.v4` probe seed aimed at the current
      gradient-loaded near-miss
- [x] Add one invalid fixture that proves unsupported `rich.v4` payloads fail
      explicitly rather than downgrade into projector behavior
- [x] Add schema/extension tests for deterministic parsing and explicit failure

### Implementation Notes

- This iteration should still avoid runtime assembly changes.
- The first success condition is honest source contract enforcement, not
  immediate spark generation.
- Implemented first `rich.v4` schema surface in:
  - `src/pygrc/landscapes/extensions/grcv3.py`
- Added typed contract elements:
  - `GRCV3_RICH_V4_CONTRACT_VERSION`
  - `GRCV3RichTransferMediation`
  - `primitive.extensions.grcv3.transfer_mediation`
- Locked first executable field set:
  - `mediation_mode`
  - `pair_mediation_classes`
  - `probe_guard_class`
  - `lateral_spill_policy`
- Locked first validation rule:
  - `transfer_mediation` is valid only when `interior_load_carriers` already
    declares the transfer surface explicitly
  - every declared `transfer_role_pair` must receive an explicit mediation
    class
  - no undeclared pair may appear
  - no mediation class may be inferred by fallback logic
- Added first valid `rich.v4` fixture:
  - `configs/landscapes/seed/grcv3-rich-v4-transfer-mediation-probe.seed.yaml`
- Added first invalid validation fixture:
  - `configs/landscapes/seed/grcv3-rich-v4-invalid-underdetermined-mediation.seed.yaml`
- Added regression/validation coverage in:
  - `tests/landscapes/test_grcv3_extensions.py`
- Also updated fixture index:
  - `configs/landscapes/seed/README.md`

### Verification

- [x] Valid `rich.v4` payloads parse deterministically
- [x] Invalid or underdetermined `rich.v4` payloads fail explicitly
- [x] Existing `rich.v1` / `rich.v2` / `rich.v3` fixtures remain stable
- [x] `source .venv/bin/activate && python -m unittest tests.landscapes.test_grcv3_extensions`
- [x] `source .venv/bin/activate && python -m unittest tests.models.test_grc_v3_landscape_runtime`

### Summary

Iteration 23 is complete. The first `rich.v4` slice is now real at the
schema/fixture layer and still respects the boundary set in Iteration 22:
`transfer_mediation` is accepted only as direct structural source semantics
over an already-declared transfer surface, not as a transport override.
Underdetermined payloads now fail explicitly, a valid `rich.v4` probe fixture
exists, and existing `rich.v1` / `rich.v2` / `rich.v3` fixtures remain stable
under the updated extractor.

## Iteration 24. First `rich.v4` Native Assembly Gate

### Goal

Test whether the first direct-translation-only `rich.v4` slice can move the
best current near-miss beyond the `rich.v3` plateau honestly.

### Checks

- [x] Implement the first native runtime assembly path for the new `rich.v4`
      semantics
- [x] Rerun the weak-axis spark gate under the documented baseline envelope
- [x] Compare the result against:
  - [x] `grcv3-rich-v3-load-carrier-spindle-probe.seed.yaml`
  - [x] `grcv3-rich-v3-load-carrier-weak-to-stable-probe.seed.yaml`
- [x] Record explicitly whether the new semantics:
  - [x] reduce center gradient materially
  - [x] preserve or improve weak-axis degeneracy
  - [x] create a validated geometric seed or spark candidate
- [x] Record the next missing direct source semantic explicitly if this still
      fails

### Implementation Notes

- This gate should be judged by the same honesty standard as the earlier
  `rich.v2` / `rich.v3` gates.
- The target is not “force a spark.”
- The target is “see whether direct source semantics can break the current
  plateau without projector interpretation.”
- Implemented first runtime meaning for `transfer_mediation` in:
  - `src/pygrc/models/grc_v3_landscape_native.py`
  - `src/pygrc/models/grc_v3_landscape.py`
- Locked first runtime meaning:
  - transfer mediation only changes assembled ingress structure over the
    already-declared carrier/probe transfer surface
  - it does this through:
    - pair-class-weighted carrier-to-probe transfer edges
    - explicit spill edges from carrier roles to additional probe roles as
      constrained by `lateral_spill_policy`
    - guarded spoke scaling on impacted probe roles as constrained by
      `probe_guard_class`
  - it does not alter the later constitutive transport loop
- Added runtime artifact visibility:
  - `landscape_runtime_assembly_summary["transfer_mediation_primitive_ids"]`
  - `landscape_grcv3_transfer_mediation_summary`
  - `landscape_realization_mode = basin_patch_valley_channel_junction_ridge_grcv3_rich_v4`
- Added runtime regression coverage in:
  - `tests/models/test_grc_v3_landscape_runtime.py`
- Baseline gate comparison result (`num_steps = 50`):
  - `grcv3-rich-v3-load-carrier-weak-to-stable-probe.seed.yaml`
    - final observables:
      - `geometric_seed_count = 0`
      - `geometric_validated_basin_count = 0`
      - `spark_event_count = 0`
    - event counts:
      - none
  - `grcv3-rich-v4-transfer-mediation-probe.seed.yaml`
    - final observables:
      - `geometric_seed_count = 0`
      - `geometric_validated_basin_count = 0`
      - `spark_event_count = 0`
    - lifecycle events:
      - `spark_candidate = 2`
      - `spark = 2`
      - `split_init = 2`
      - `split_progress = 4`
      - `split_complete = 2`
- Interpretation:
  - the first `rich.v4` slice breaks the behavioral plateau honestly
  - the seed-driven lane now produces real spark lifecycle events under the
    baseline gate
  - the remaining open question is narrower:
    - not whether direct source semantics can spark
    - but whether later `rich.v4` work is needed to stabilize explicit
      geometric validation earlier in the trajectory

### Verification

- [x] The result is reproducible under the documented baseline envelope
- [x] The outcome is recorded explicitly as pass, near-miss, or failure
- [x] `source .venv/bin/activate && python -m unittest tests.landscapes.test_grcv3_extensions tests.models.test_grc_v3_landscape_runtime`
- [x] `source .venv/bin/activate && python - <<'PY' ... run_grcv3_landscape_seed(<rich.v3>, num_steps=50); run_grcv3_landscape_seed(<rich.v4>, num_steps=50) ... PY`

### Summary

Iteration 24 is a real pass. The first `rich.v4` direct-translation slice does
more than move numbers around inside the old `rich.v3` near-miss: it produces
real seed-driven spark lifecycle events under the baseline gate, while the best
current `rich.v3` comparison fixture remains completely event-flat. The new
slice therefore breaks the `rich.v3` plateau honestly at the behavioral level.
What remains open is narrower and more useful: how to improve explicit
geometric validation or observability of the transient seed-to-spark path,
not whether direct source semantics can reach the spark machinery at all.

## Iteration 25. Consolidate The First `rich.v4` Pass

### Goal

Turn the Iteration 24 result into an explicit closure boundary before any
further `rich.v4` growth happens.

### Checks

- [x] Record Iteration 24 as the first successful direct-translation spark gate
- [x] Record explicitly what is now closed:
  - [x] direct source semantics can reach real spark lifecycle events
  - [x] the `rich.v4` lane is no longer only a theoretical proposal
- [x] Record explicitly what is still open:
  - [x] transient seed-to-spark observability
  - [x] earlier geometric validation visibility
  - [x] whether any further source-side broadening is needed inside
        `transfer_mediation`
- [x] Record that “full `rich.v4` content” is not yet the next move
- [x] Record that any immediate next work must stay inside the
      `transfer_mediation` family unless evidence later forces a different
      direct semantic group

### Implementation Notes

- This iteration is documentation/closure work, not runtime broadening.
- The purpose is to stop the project from treating the first `rich.v4` pass as
  either:
  - total closure
  - or a license to add unrelated semantics immediately
- The right boundary after Iteration 24 is:
  - behavioral reachability is proven
  - transient-path evidence is still thin
  - later broadening, if any, should be evidence-led and local to
    `transfer_mediation`
- Recorded closure boundary:
  - closed:
    - the project now has a real direct-translation `rich.v4` lane
    - direct source semantics are sufficient to reach spark lifecycle events
      under the normal `GRCV3` runtime loop
  - still open:
    - why explicit geometric validation remains weak or late relative to the
      spark lifecycle
    - how the interior regime moves before candidate/spark onset
    - whether any later `rich.v4` broadening is needed after that transient
      path is made more observable
- Recorded next-step rule:
  - do not open unrelated semantic families yet
  - do not treat “full `rich.v4` content” as a planning target by itself
  - continue next with observability first, then broaden only
    `transfer_mediation` if the evidence still points there
- Recorded closure note location:
  - `implementation/GRCV3-RichSeed-Rationale.md`

### Verification

- [x] The closure boundary is explicit in the checklist and rationale notes
- [x] The next work is framed as consolidation first, not capability sprawl

### Summary

Iteration 25 is complete. The first `rich.v4` pass is now recorded as a real
closure boundary rather than as either total completion or merely another
probe. What is closed is precise:

- direct-translation source semantics can reach real `GRCV3` spark lifecycle
  events
- `rich.v4` is a real executable family-native lane

What remains open is equally precise:

- transient seed-to-spark observability
- earlier and clearer geometric-validation visibility
- and only then, if still justified, a controlled broadening inside
  `transfer_mediation`

## Iteration 26. Seed-To-Spark Observability Lift

### Goal

Make the first `rich.v4` pass inspectable enough that later language growth is
driven by evidence rather than by guesswork.

### Checks

- [x] Define the minimum observability surface for the transient path:
  - [x] center-gradient evolution
  - [x] signed-curvature evolution on the intended weak axis
  - [x] transfer-surface realization summaries
  - [x] event-aligned summaries around candidate/spark/split onset
- [x] Decide which of those belong to:
  - [x] runtime artifact metadata
  - [x] telemetry summaries
  - [x] later visualization overlays
- [x] Keep this iteration downstream-only:
  - [x] no runtime-equation changes
  - [x] no new source-schema fields
  - [x] no heuristic projector compensation
- [x] Record the comparison baseline explicitly:
  - [x] `grcv3-rich-v3-load-carrier-weak-to-stable-probe.seed.yaml`
  - [x] `grcv3-rich-v4-transfer-mediation-probe.seed.yaml`

### Implementation Notes

- The first `rich.v4` pass already answers “can it spark?”
- This iteration answers the next question:
  - “what interior regime change happened before the spark events?”
- The observability lift should explain the path, not amplify it artificially.
- If later visualization work is needed, this iteration should still define the
  artifact contract first.
- Recorded artifact placement rule:
  - runtime artifact metadata:
    - graph checkpoints now expose:
      - `family_extensions["grcv3"]["landscape_monitoring_surface_kind"]`
      - `family_extensions["grcv3"]["landscape_monitored_node_ids_by_primitive_id"]`
    - rationale:
      - checkpoints already carry raw per-node `gradient`, `gradient_norm`, and
        `hessian`
      - they only need the deterministic pointer to the monitored interior site
  - telemetry step summaries:
    - `family_extensions["grcv3"]["transient_landscape"]`
    - carries:
      - `monitoring_surface_kind`
      - per-step `observed_sites`
      - each site includes:
        - `gradient_norm`
        - `min_signed_eigenvalue`
        - `max_signed_eigenvalue`
        - `weak_mode_signed_curvature`
        - `gradient_gate_pass`
        - `geometric_validation_pass`
        - `spark_candidate_regime`
  - telemetry run summary:
    - `family_extensions["grcv3"]["transient_landscape"]`
    - carries:
      - monitored-node mapping
      - static surface-realization summary
      - per-primitive trajectory summary
      - first event-aligned observations for:
        - `spark_candidate`
        - `spark`
        - `split_init`
        - `split_complete`
  - later visualization:
    - should consume the step/run-summary transient surface first
    - should use checkpoint raw node state only when graph-visible detail is
      required
- Recorded operational weak-axis rule:
  - the “intended weak axis” is exported as the runtime weak mode actually used
    by spark detection
  - concretely, Iteration 26 reports the minimum signed-Hessian eigenvalue
    rather than pretending a source role label is the runtime eigenbasis
- Implemented surfaces in:
  - `src/pygrc/telemetry/grcv3_contract.py`
  - `src/pygrc/telemetry/experiments.py`
  - `src/pygrc/models/grc_v3_checkpoints.py`
  - `scripts/run_grcv3_rich_fulltest.py`
- Contract-version lift:
  - telemetry family contract:
    - `phase_t_iter26_v1`
  - checkpoint family contract:
    - `phase_t_iter26_v1`
- Baseline probe readout under the same first-pass gate envelope
  (`seed_baseline`, `50` steps):
  - `grcv3-rich-v4-transfer-mediation-probe.seed.yaml`
    - monitoring surface: `transfer_mediation`
    - monitored node map:
      - `spindle_core -> 16`
    - first event-aligned observations:
      - `spark_candidate` at step `6`
      - `spark` at step `6`
      - `split_init` at step `6`
      - `split_complete` at step `7`
    - transient primitive summary for `spindle_core`:
      - `initial_gradient_norm ~ 4.63e-01`
      - `min_gradient_norm ~ 4.63e-01`
      - `final_gradient_norm ~ 5.42e-01`
- Interpretation:
  - the new surface does what Iteration 26 needed:
    - it makes the transient path inspectable
    - and it shows clearly that the first `rich.v4` spark path is not currently
      a “low-gradient-center first, then spark” story
  - the open question is therefore sharper:
    - whether later direct source semantics should reduce that monitored center
      load regime
    - or whether sparkability here is already being mediated through another
      transient structural route the new observability surface now allows us to
      inspect honestly

### Verification

- [x] A later reviewer can inspect the transient seed-to-spark path without
      rereading runtime code
- [x] The observability surface remains strictly descriptive, not constitutive

### Summary

Iteration 26 is complete. The project now has a real transient-path
observability surface for rich `GRCV3` landscape runs, and it lands cleanly in
the downstream layers where it belongs:

- checkpoints point to the monitored interior site
- step telemetry records per-step interior metrics
- run summaries record event-aligned onset snapshots and trajectory rollups

The most important outcome is not just that more fields exist. It is that the
first `rich.v4` spark lane is now inspectable enough to guide the next
decision honestly. The current evidence says:

- spark lifecycle events are real
- but the monitored `spindle_core` center does not currently move into a
  low-gradient regime before those events

So Iteration 26 closes with a sharper residual question for Iteration 27:
whether any further broadening inside `transfer_mediation` is justified by that
now-visible transient path.

## Iteration 27. Controlled `transfer_mediation` Broadening

### Goal

Broaden `rich.v4` only if the Iteration 26 evidence shows a real residual gap
inside transfer mediation itself.

### Checks

- [x] Decide whether the current first-pass `transfer_mediation` slice is
      already sufficient or needs one more direct semantic degree of freedom
- [x] If broadening is justified, keep it inside:
  - [x] `primitive.extensions.grcv3.transfer_mediation`
- [x] Reject broadening attempts that would:
  - [x] open unrelated semantic families
  - [x] reintroduce projector-style interpretation
  - [x] encode solved runtime state
- [x] Require every proposed new field to have:
  - [x] direct native-assembly meaning
  - [x] a specific residual gap it is meant to address
  - [x] a deterministic acceptance path
- [x] Add at least one follow-on probe only if the new field set is justified

### Implementation Notes

- This iteration is intentionally conditional.
- If Iteration 26 shows the current `transfer_mediation` slice is already
  explanatory enough, the correct move may be to stop rather than broaden.
- If broadening is justified, it should remain a narrow source-side change with
  explicit comparison against the current first-pass `rich.v4` probe.
- Added one new direct field only:
  - `center_coupling_classes`
- Locked meaning:
  - per-probe-role refinement of center-spoke participation for
    already-declared transfer mediation
- Explicitly rejected meanings:
  - new carrier placement rules
  - new transfer-pair invention
  - solved runtime transport overrides
- Added follow-on probe fixture:
  - `configs/landscapes/seed/grcv3-rich-v4-center-coupling-probe.seed.yaml`
- Follow-on comparison under the same `seed_baseline` / `num_steps = 50` gate:
  - baseline `grcv3-rich-v4-transfer-mediation-probe.seed.yaml`
    - spark lifecycle events present:
      - `spark_candidate = 2`
      - `spark = 2`
      - `split_init = 2`
      - `split_complete = 2`
    - monitored center gradient:
      - initial `~4.63e-01`
      - minimum `~4.63e-01`
  - center-coupling follow-on with:
    - `center_coupling_classes = [[north, blocked], [south, blocked]]`
    - support spokes realized only for `east` and `west`
    - monitored center gradient:
      - initial `~4.26e-01`
      - minimum `~4.22e-01`
    - lifecycle events:
      - none
  - weaker stable-axis center coupling (`weak`) was also checked as a temporary
    comparison lane:
    - it suppressed the spark path without improving the center regime
- Interpretation:
  - the residual gap really does live inside transfer mediation strongly enough
    to justify one more direct field
  - but center-coupling suppression is not automatically an improvement
  - the new field is therefore accepted as a direct explanatory degree of
    freedom, not promoted as a new default recipe

### Verification

- [x] Any broadened field set is still direct-translation-only
- [x] The broadened slice remains deterministic and family-native
- [x] `source .venv/bin/activate && python -m unittest tests.landscapes.test_grcv3_extensions tests.models.test_grc_v3_landscape_runtime`

### Summary

Iteration 27 is complete. The first `transfer_mediation` broadening was
justified, kept strictly inside direct source semantics, and turned into a real
follow-on probe plus regression coverage. The result is intentionally mixed:

- `center_coupling_classes` changes the native assembly exactly where intended
- blocked stable-axis center coupling lowers the monitored center gradient
- but it also over-guards the lane and suppresses sparks

So the field is worth keeping because it exposes a real residual degree of
freedom inside transfer mediation, but the evidence does not justify treating
it as a generally better default than the first-pass `rich.v4` probe.

## Iteration 28. `rich.v4` Breadth Decision

### Goal

Decide whether the now-consolidated `rich.v4` work is broad enough to stand as
a stable `GRCV3` rich-source family, or whether one more direct semantic cycle
is still needed.

### Checks

- [x] Review the first-pass gate, the observability lift, and any controlled
      `transfer_mediation` broadening together
- [x] Decide whether the remaining gaps still live inside `transfer_mediation`
      or justify opening a new direct semantic family
- [x] Record explicitly whether `rich.v4` remains:
  - [ ] a narrow but real probe family
  - [x] a stable family-level authoring surface
  - [ ] or an incomplete intermediate step
- [x] Keep the decision evidence-based rather than “feature complete”-based

### Implementation Notes

- “Full content” is not the target.
- The target is a stable direct-translation boundary whose remaining gaps are
  well understood.
- This iteration should prevent the project from drifting back into
  unbounded vocabulary growth.
- Reviewed evidence together:
  - first-pass `rich.v4` gate:
    - direct source semantics produce spark lifecycle events under the
      baseline gate
  - observability lift:
    - transient path is inspectable and shows the center remains
      gradient-loaded before spark onset
  - controlled `transfer_mediation` broadening:
    - `center_coupling_classes` is a real direct semantic degree of freedom
    - but over-guarding can suppress sparks entirely
- Recorded breadth decision:
  - `grcv3.rich.v4` is no longer only a narrow probe family
  - `grcv3.rich.v4` is now a stable narrow family-level authoring surface
  - `grcv3.rich.v4` is not yet a fully general-purpose `GRCV3` rich language
- Recorded next-step rule:
  - keep later growth evidence-led
  - remain inside `transfer_mediation` only if the already-visible transient
    evidence continues to localize the gap there
  - otherwise open the next direct semantic family intentionally rather than
    by drift

### Verification

- [x] The breadth decision is recorded explicitly rather than implied
- [x] The recorded next step follows from evidence already gathered

### Summary

Iteration 28 is complete. The current evidence is strong enough to classify
`grcv3.rich.v4` as a stable narrow family-level authoring surface.

That is deliberately stronger than “still only a probe family” and
deliberately weaker than “fully general-purpose rich `GRCV3` language.”

The remaining gaps are now well localized:

- the lane is behaviorally real
- the lane is observably inspectable
- the lane survives one controlled evidence-led broadening
- but later growth must still be justified by transient-path evidence rather
  than vocabulary expansion pressure

### Post-28 Next-Step Guidance

The next justified `rich.v4` work is now narrower than “add more vocabulary”.

What should happen next:

- use the saved rich-v4 artifact lane as the reference evidence surface:
  - `outputs/grcv3-rich-v4-spark-visual/grcv3-rich/seed_baseline/...`
- treat that lane as the comparison baseline for any later `rich.v4` candidate
- prefer only two classes of next move:
  - one more `transfer_mediation` cycle if transient-path evidence still
    localizes the remaining issue to ingress structure
  - or one intentionally opened new direct semantic family if the evidence no
    longer points to transfer mediation

What should not happen next:

- generic “more rich.v4 content”
- reopening projector-style interpretation
- runtime/constitutive loosening to compensate for source weakness
- adding fields whose only role is to make the current good lane easier to
  tune without a new semantic claim

Recorded candidate if one more `rich.v4` cycle is justified:

- stay inside `primitive.extensions.grcv3.transfer_mediation`
- prefer a structural slice centered on **carrier-to-probe path structure**
  rather than opening a new family immediately

Candidate structural surface:

- `path_roles`
- `path_mode`
- `path_topology`

Candidate value style:

- direct assembly terms such as:
  - `direct`
  - `single_intermediate`
  - `double_intermediate`
  - `fan_in`
  - `buffered_chain`

Rejected framing for now:

- effect-oriented names such as:
  - `interior_spoke_compliance`
  - `flexible`
  - `damping`

Reason for the rejection:

- the currently observed residual still looks like ingress-path assembly
  structure, not yet a clearly separate semantic family
- so splitting that concern too early would risk dividing one semantic problem
  into two labels without enough evidence

Promotion rule:

- only if this path-structure slice proves too large or semantically distinct
  to fit cleanly inside `transfer_mediation` should it be promoted later into a
  separate direct semantic family

## Iteration 29. `rich.v4` Path-Structured Transfer Mediation

### Goal

Define the first post-28 candidate slice explicitly before any new `rich.v4`
implementation lands.

This iteration stays inside:

- `primitive.extensions.grcv3.transfer_mediation`

Its purpose is to test whether the next remaining ingress-local gap is best
described as **carrier-to-probe path structure**, not as broader geometry
growth and not yet as a separate direct semantic family.

### Checks

- [x] Lock the first accepted path-structure surface under
  `primitive.extensions.grcv3.transfer_mediation`
- [x] Keep the new surface strictly direct-assembly-facing rather than
  effect-facing
- [x] Decide the first allowed path-structure field names
- [x] Decide the first allowed direct structural values
- [x] Record which existing `rich.v4` meanings the new slice must not reopen:
  - [x] pair coverage
  - [x] carrier placement
  - [x] probe geometry
  - [x] runtime transport laws
- [x] Add one follow-on probe lane that uses the new path-structure slice
- [x] Compare that follow-on probe explicitly against the saved baseline
  `grcv3-rich-v4-transfer-mediation-probe` lane
- [x] Record whether the new slice:
  - [x] stays ingress-local
  - [x] remains deterministic and family-native
  - [ ] preserves the current spark lane
  - [ ] improves the current spark lane
  - [x] over-guards / suppresses the current spark lane

### Implementation Notes

- This iteration is a boundary-definition step first, not a generic
  expressivity step.
- Locked first executable path-structure field set:
  - `primitive.extensions.grcv3.transfer_mediation.path_topology`
- Locked first deferred candidate fields:
  - `path_roles`
  - `path_mode`
- Reason for the narrower lock:
  - `transfer_role_pairs` already declare role coverage explicitly
  - so the first Iteration 29 slice should change only assembled path shape,
    not reopen role-surface definition
- The baseline evidence lane remains:
  - `outputs/grcv3-rich-v4-spark-visual/grcv3-rich/seed_baseline/...`
- The candidate semantic target is:
  - explicit path structure between already-declared load carriers and the
    already-declared probe shell
- The slice must remain inside `transfer_mediation` only if the meaning stays:
  - structural
  - ingress-local
  - and directly translatable into family-native assembly
- The slice must **not** introduce:
  - effect-oriented names such as `compliance`, `flexible`, or `damping`
  - free-form transfer matrices
  - constitutive transport overrides
  - reopened projector-style interpretation
- Candidate field family to evaluate:
  - `path_topology`
- Locked field encoding:
  - `path_topology` is a list of explicit
    `[carrier_role, probe_role, topology_class]` triples
  - if present, it must cover exactly the already-declared
    `interior_load_carriers.transfer_role_pairs`
- Locked first executable topology classes:
  - `direct`
  - `single_intermediate`
  - `fan_in`
- Locked deferred topology classes:
  - `double_intermediate`
  - `buffered_chain`
- Locked direct assembly meanings:
  - `direct`
    - realize the existing carrier-to-probe edge directly
  - `single_intermediate`
    - realize one dedicated intermediate node on that declared pair before the
      probe role
  - `fan_in`
    - realize a shared intermediate node for all declared pairs that target the
      same probe role
- Locked validation rule for `fan_in`:
  - a `fan_in` assignment is valid only when at least two declared pairs share
    that target probe role inside the same primitive
- The first executable slice should still stay narrower than that full
  candidate set if a smaller surface is sufficient.
- Promotion rule:
  - if the path-structure semantics no longer fit cleanly inside
    `transfer_mediation`, stop and name the new direct semantic family
    explicitly before coding
- Implemented typed Iteration 29 path-surface support in:
  - `src/pygrc/landscapes/extensions/grcv3.py`
- Implemented family-native path-node assembly in:
  - `src/pygrc/models/grc_v3_landscape.py`
- Added the follow-on probe lane:
  - `configs/landscapes/seed/grcv3-rich-v4-path-topology-probe.seed.yaml`
- Added focused regression coverage in:
  - `tests/landscapes/test_grcv3_extensions.py`
  - `tests/models/test_grc_v3_landscape_runtime.py`
- Executed first realized path-topology slice:
  - all four declared transfer pairs use `fan_in`
  - north-targeting pairs share one realized ingress node
  - south-targeting pairs share one realized ingress node
  - direct carrier-to-probe edges are replaced by:
    - carrier-to-path ingress edges
    - shared path-to-probe egress edges
  - spill semantics remain on the existing `transfer_mediation` surface
- Baseline comparison against the saved first-pass `rich.v4` lane over
  `50` steps:
  - baseline `grcv3-rich-v4-transfer-mediation-probe`:
    - `spark_candidate=2`
    - `spark=2`
    - `split_init=2`
    - `split_complete=2`
  - Iteration 29 `grcv3-rich-v4-path-topology-probe`:
    - `spark_candidate=0`
    - `spark=0`
    - `split_init=0`
    - `split_complete=0`
- Immediate comparison note:
  - the initial monitored center gradient remains unchanged relative to the
    baseline lane
  - so this first `fan_in` path-structure slice changes ingress topology
    truthfully but does not improve the baseline gate and instead suppresses
    the current spark lane entirely

### Verification

- [x] The accepted field set is written down before implementation
- [x] Every accepted field has a direct assembly meaning
- [x] The iteration records an explicit comparison target against the saved
  `rich.v4` baseline lane
- [x] The iteration keeps the post-28 discipline:
  - [x] evidence-led growth
  - [x] structure before effect-language
  - [x] no runtime compensation for weak source semantics

Focused verification executed with:

- `./.venv/bin/python -m unittest tests.landscapes.test_grcv3_extensions tests.models.test_grc_v3_landscape_runtime`
- result: `Ran 63 tests ... OK`

### Summary

Iteration 29 is complete. Path-structured `transfer_mediation` is now a real
executed follow-on slice rather than only a recorded idea.

The result is intentionally mixed:

- the slice stays narrow and direct-translation-only
- the slice remains deterministic and family-native
- the slice clearly changes assembled ingress topology in a truthful,
  inspectable way
- but the first `fan_in` path-topology probe suppresses the current baseline
  spark lane entirely instead of improving it

So Iteration 29 does **not** justify promoting this first path-topology slice
as a better default than the saved baseline `rich.v4` lane.

What it does justify is narrower than that:

- `path_topology` is a real ingress-local structural degree of freedom inside
  `transfer_mediation`
- but the first executable `fan_in` realization over-guards the lane
- so any later return to path-structured mediation should be treated as a
  controlled follow-on, not as an automatic broadening win

## Iteration 30. `single_intermediate` Diagnostic Isolation

### Goal

Determine whether the Iteration 29 suppression is caused by:

- path-node presence in general
- or specifically by shared `fan_in` aggregation

This iteration remains inside:

- `primitive.extensions.grcv3.transfer_mediation.path_topology`

It is a diagnostic-isolation step, not a coefficient-tuning step.

### Checks

- [x] Add one follow-on `rich.v4` probe that changes only `path_topology`
  from `fan_in` to `single_intermediate`
- [x] Keep all non-path-topology source semantics identical to the saved
  baseline `grcv3-rich-v4-transfer-mediation-probe` lane
- [x] Keep all non-source runtime coefficients unchanged from Iteration 29
- [x] Compare the new probe explicitly against:
  - [x] the saved baseline `grcv3-rich-v4-transfer-mediation-probe`
  - [x] the Iteration 29 `fan_in` probe
- [x] Record whether `single_intermediate`:
  - [ ] restores spark/split events
  - [x] still suppresses the lane
  - [x] changes initial monitored center gradient
    - result: no
  - [x] changes the realized ingress path structure without reopening other
        semantics
- [x] Decide explicitly which hypothesis survives:
  - [ ] suppression is specific to shared `fan_in` aggregation
  - [x] suppression is general to added path intermediacy

### Implementation Notes

- The purpose here is variable isolation.
- This iteration should answer one narrower question before any new tuning:
  - is the problematic factor the existence of intermediate path nodes
  - or the shared hub structure of `fan_in`
- Locked probe rule:
  - change only `transfer_mediation.path_topology`
- Locked Iteration 30 probe target:
  - `configs/landscapes/seed/grcv3-rich-v4-single-intermediate-probe.seed.yaml`
- Locked topology assignment for the diagnostic probe:
  - every declared transfer pair uses `single_intermediate`
- What must remain unchanged relative to the baseline lane:
  - `mediation_mode`
  - `pair_mediation_classes`
  - `probe_guard_class`
  - `lateral_spill_policy`
  - carrier placement
  - transfer-role coverage
  - interior geometry / partition / load-carrier semantics
  - runtime constitutive equations
- Explicitly deferred for this iteration:
  - path-node mass tuning
  - path-node offset tuning
  - guard/spill coefficient tuning
  - any new semantic fields under `transfer_mediation`
- Reason for the deferment:
  - coefficient changes would conflate structural diagnosis with constructive
    tuning and would weaken the evidence value of the result
- Implemented Iteration 30 diagnostic probe:
  - `configs/landscapes/seed/grcv3-rich-v4-single-intermediate-probe.seed.yaml`
- Added focused Iteration 30 coverage in:
  - `tests/landscapes/test_grcv3_extensions.py`
  - `tests/models/test_grc_v3_landscape_runtime.py`
- Realized Iteration 30 path structure:
  - every declared transfer pair gets one dedicated intermediate node
  - direct carrier-to-probe edges are replaced by:
    - carrier-to-path ingress edges
    - path-to-probe egress edges
  - unlike Iteration 29:
    - no pairs share a fan-in hub node
- Three-way `50`-step comparison:
  - baseline `grcv3-rich-v4-transfer-mediation-probe`:
    - `spark_candidate=2`
    - `spark=2`
    - `split_init=2`
    - `split_complete=2`
  - Iteration 29 `grcv3-rich-v4-path-topology-probe` (`fan_in`):
    - `spark_candidate=0`
    - `spark=0`
    - `split_init=0`
    - `split_complete=0`
  - Iteration 30 `grcv3-rich-v4-single-intermediate-probe`:
    - `spark_candidate=0`
    - `spark=0`
    - `split_init=0`
    - `split_complete=0`
- Initial monitored center-gradient comparison:
  - baseline:
    - `0.4625384255208662`
  - Iteration 29 `fan_in`:
    - `0.4625384255208662`
  - Iteration 30 `single_intermediate`:
    - `0.4625384255208662`
- Surviving diagnostic conclusion:
  - the suppression is not specific to shared `fan_in` aggregation
  - the suppression is general to added path intermediacy in the current
    assembly realization
- Consequence for the next step:
  - do not tune global/runtime coefficients first
  - if this lane is revisited, the next justified focus is the constructive
    realization of path intermediates themselves:
    - path-node mass
    - path-node placement
    - or edge-weight partitioning across ingress/egress

### Verification

- [x] The new probe differs from the baseline lane only in `path_topology`
- [x] Structural tests confirm that one dedicated intermediate node is realized
  for each declared transfer pair
- [x] Focused comparison records event counts for:
  - [x] baseline
  - [x] Iteration 29 `fan_in`
  - [x] Iteration 30 `single_intermediate`
- [x] The iteration ends with an explicit kept/rejected hypothesis rather than
  an implied interpretation

Focused verification executed with:

- `./.venv/bin/python -m unittest tests.landscapes.test_grcv3_extensions tests.models.test_grc_v3_landscape_runtime`
- result: `Ran 67 tests ... OK`

### Summary

Iteration 30 is complete.

Its job was not to improve the lane immediately.
Its job was to isolate whether spark suppression comes from shared `fan_in`
aggregation or from added transfer-path intermediacy more generally.

That isolation now has a clear answer:

- `single_intermediate` changes the ingress structure truthfully and
  deterministically
- but it suppresses the lane just like `fan_in`
- and it does so without changing the initial monitored center gradient

So the surviving hypothesis is:

- the current suppression is general to added path intermediacy in this
  assembly realization, not specific to shared `fan_in` aggregation

That means the next justified move, if this lane is pursued further, is not a
generic runtime coefficient adjustment.
It is a narrower constructive diagnostic around how intermediate path nodes are
realized.

## Iteration 31. Path-Node Realization Sensitivity

### Goal

Determine whether the Iteration 30 suppression is caused by:

- path-node mass / inertia in the current realization
- path-edge coupling / partitioning in the current realization
- or extra-hop path intermediacy itself

This iteration does **not** open new `GRCL-v3` source semantics.

It is a realization-sensitivity diagnostic inside the existing
`single_intermediate` lane.

### Checks

- [x] Keep using the existing Iteration 30
  `grcv3-rich-v4-single-intermediate-probe` source lane
- [x] Do not add new `GRCL-v3` vocabulary or new rich-seed semantic fields
- [x] Do not create a new seed fixture merely to encode runtime tuning
- [x] Run one mass-only realization diagnostic
- [x] Run one coupling-only realization diagnostic
- [x] Compare each diagnostic explicitly against:
  - [x] the saved baseline `grcv3-rich-v4-transfer-mediation-probe`
  - [x] Iteration 29 `fan_in`
  - [x] Iteration 30 `single_intermediate`
- [x] Record whether either diagnostic:
  - [ ] restores spark/split events
  - [x] changes initial monitored center gradient
    - result: no
  - [x] leaves the lane suppressed
- [x] Decide explicitly which explanation survives:
  - [ ] the current failure is mainly path-node mass / inertia
  - [ ] the current failure is mainly ingress/egress coupling partitioning
  - [x] the current failure is mainly extra-hop topology itself

### Implementation Notes

- This iteration is about constructive realization, not new source meaning.
- Locked source boundary:
  - reuse the existing `single_intermediate` probe without semantic changes
- Locked architectural boundary:
  - changes live only in the family-native assembly realization in
    `src/pygrc/models/grc_v3_landscape.py`
- Locked diagnostic order:
  - 31A: mass-only diagnostic
  - 31B: coupling-only diagnostic
- Locked 31A diagnostic target:
  - reduce path-node realized mass only
  - keep edge scaling otherwise unchanged
- Locked 31B diagnostic target:
  - strengthen path ingress/egress coupling only
  - keep path-node mass unchanged
- Explicitly forbidden in this iteration:
  - changing both mass and coupling in the same diagnostic pass
  - global/runtime family coefficient tuning outside the path-node realization
  - bypassing `transfer_mediation` semantics wholesale
  - introducing new effect-oriented source classes such as `light_path` or
    `strong_path`
- Reason for the narrower lock:
  - if mass and coupling change together, the result loses diagnostic value
  - if a realization tweak helps, that still does not by itself justify a new
    source-semantic class
- Implemented realization-only diagnostic knobs in:
  - `src/pygrc/models/grc_v3_landscape.py`
- Added focused runtime diagnostic coverage in:
  - `tests/models/test_grc_v3_landscape_runtime.py`
- Realized diagnostic controls:
  - 31A mass-only:
    - `_TRANSFER_PATH_NODE_MASS_SCALE`
    - baseline `0.8`
    - diagnostic `0.2`
  - 31B coupling-only:
    - `_TRANSFER_PATH_EDGE_WEIGHT_SCALE`
    - baseline `1.0`
    - diagnostic `1.0 / 0.68`
- Isolation checks confirmed:
  - 31A lowers realized path-node mass while leaving path-edge conductance
    unchanged
  - 31B strengthens path ingress/egress conductance while leaving path-node
    mass unchanged
- Five-way `50`-step comparison:
  - baseline `grcv3-rich-v4-transfer-mediation-probe`:
    - `spark_candidate=2`
    - `spark=2`
    - `split_init=2`
    - `split_complete=2`
  - Iteration 29 `fan_in`:
    - `spark_candidate=0`
    - `spark=0`
    - `split_init=0`
    - `split_complete=0`
  - Iteration 30 `single_intermediate`:
    - `spark_candidate=0`
    - `spark=0`
    - `split_init=0`
    - `split_complete=0`
  - Iteration 31A mass-only diagnostic:
    - `spark_candidate=0`
    - `spark=0`
    - `split_init=0`
    - `split_complete=0`
  - Iteration 31B coupling-only diagnostic:
    - `spark_candidate=0`
    - `spark=0`
    - `split_init=0`
    - `split_complete=0`
- Initial monitored center-gradient comparison:
  - baseline:
    - `0.4625384255208662`
  - Iteration 29 `fan_in`:
    - `0.4625384255208662`
  - Iteration 30 `single_intermediate`:
    - `0.4625384255208662`
  - Iteration 31A mass-only:
    - `0.4625384255208662`
  - Iteration 31B coupling-only:
    - `0.4625384255208662`
- Surviving conclusion:
  - neither lower path-node mass nor stronger path-edge coupling restores the
    lane
  - so the current failure is not localized to those realization magnitudes
  - the strongest remaining explanation is the extra-hop topology itself

### Verification

- [x] The source lane remains unchanged from Iteration 30
- [x] 31A changes only path-node realized mass
- [x] 31B changes only path ingress/egress coupling realization
- [x] Focused comparison records event counts for:
  - [x] baseline
  - [x] Iteration 29 `fan_in`
  - [x] Iteration 30 `single_intermediate`
  - [x] Iteration 31A mass-only diagnostic
  - [x] Iteration 31B coupling-only diagnostic
- [x] The iteration ends with one explicit surviving explanation, not multiple
  mixed interpretations

Focused verification executed with:

- `./.venv/bin/python -m unittest tests.landscapes.test_grcv3_extensions tests.models.test_grc_v3_landscape_runtime`
- result: `Ran 69 tests ... OK`

### Summary

Iteration 31 is complete.

Its job was not to broaden `path_topology`.
Its job was to test whether the current failure is a constructive realization
problem under the already-accepted `single_intermediate` surface, or whether
extra-hop path intermediacy is itself incompatible with the current lane.

That diagnostic now has a clear result:

- lowering path-node mass alone does not restore the lane
- strengthening path ingress/egress coupling alone does not restore the lane
- neither diagnostic changes the initial monitored center gradient

So the strongest surviving explanation is:

- the current failure is mainly the extra-hop topology itself in the present
  `GRCV3` lane, not merely the current path-node mass or path-edge coupling
  magnitude

That means the next justified move, if this line of work continues, is no
longer another simple magnitude tweak.
It would need to confront the topological incompatibility directly, or else
stop treating path intermediacy as a promising near-term continuation of this
`rich.v4` lane.

## Iteration 32. Path Intermediacy Failure Trace

### Goal

Localize exactly where the `single_intermediate` lane diverges from the saved
baseline direct lane during early evolution.

This iteration does **not** open new `GRCL-v3` source semantics.

It is an observability / failure-trace iteration inside the already-accepted
`rich.v4` lanes.

### Checks

- [x] Keep the source comparison restricted to already-existing lanes:
  - [x] saved baseline `grcv3-rich-v4-transfer-mediation-probe`
  - [x] Iteration 30 `grcv3-rich-v4-single-intermediate-probe`
- [x] Do not add new `GRCL-v3` vocabulary or new transfer-mediation semantics
- [x] Add focused early-step observability for the path-mediated lane
- [x] Compare baseline vs `single_intermediate` on:
  - [x] center gradient norm trajectory
  - [x] signed eigenvalue / weak-axis trajectory
  - [x] spark-candidate gate-relevant quantities
  - [x] support-spoke conductance / contribution context
  - [x] path ingress / egress edge conductance and flux context
  - [x] path-node coherence / potential / gradient context
  - [x] probe-shell node gradient / flux context
- [x] Record the earliest step where the two lanes diverge materially
- [x] Decide explicitly which failure mode best matches the trace:
  - [ ] ingress never reaches the probe shell strongly enough
  - [x] probe-shell ingress arrives but fails to form the needed weak-axis
        geometry
  - [ ] the final candidate transition is blocked after geometry is otherwise
        near-correct

### Implementation Notes

- This iteration is meant to reduce ambiguity before any new semantic probe.
- Locked comparison scope:
  - baseline direct lane vs `single_intermediate` only
- Reason for the narrower scope:
  - Iterations 29 to 31 already established that path intermediacy suppresses
    the lane
  - the remaining rigorous question is where that suppression enters the
    evolution, not yet which new semantic variant might escape it
- Preferred artifact style:
  - step-aligned machine-readable summaries first
  - optional human-readable script/report second
- Preferred step window:
  - the earliest portion of the run where the baseline lane is moving toward
    `spark_candidate`
- Explicitly deferred for this iteration:
  - new mediation-mode / guard-class combinations
  - new source fixtures
  - new topology classes
  - further realization-magnitude tuning
- Decision rule after this iteration:
  - only if the trace specifically implicates guarding or another already-named
    semantic boundary should a new semantic comparison be opened next

### Verification

- [x] The compared source lanes are unchanged from prior iterations
- [x] The new observability surface is sufficient to name one earliest material
  divergence
- [x] The iteration ends with one explicit failure-mode diagnosis rather than a
  generic statement that the lane “fails”
- [x] Any later semantic experiment is justified by this trace, not by
  speculation

Focused verification executed with:

- `./.venv/bin/python -m unittest tests.telemetry.test_experiments tests.landscapes.test_grcv3_extensions tests.models.test_grc_v3_landscape_runtime`
- result: `Ran 83 tests ... OK`

### Summary

Iteration 32 is complete.

Its job was not to rescue path intermediacy immediately.
Its job was to locate where the `single_intermediate` lane departs from the
baseline direct lane strongly enough that the next hypothesis is chosen from
evidence rather than from guesswork.

That trace now has a concrete result:

- the earliest material divergence occurs at step `0`
- the earliest material divergence is already visible in probe-shell gradient
  norms, not in the monitored center gradient
- by step `1`, ingress is clearly present in the path-mediated lane:
  - `basin_patch_transfer_path_egress total_abs_flux = 1.1172450775807445`
  - `basin_patch_transfer_mediation_spill total_abs_flux = 0.9591525628214026`
  - baseline direct transfer over the same step remains
    `basin_patch_load_carrier_transfer total_abs_flux = 0.883519657076351`
- despite that surviving ingress, the monitored center fails to develop the
  baseline weak-axis curvature:
  - baseline step `1` `min_signed_eigenvalue = -0.643843054198469`
  - `single_intermediate` step `1` `min_signed_eigenvalue = 5.492859163990358e-11`

So Iteration 32 rules out a simple “ingress never reaches the probe shell”
story for this lane.

The explicit failure-mode diagnosis is now:

- probe-shell ingress arrives, but the added path intermediacy fails to form
  the weak-axis geometry required for the spark lifecycle

That means any next semantic experiment should be justified only if it is
targeted at the geometry-forming boundary revealed by this trace, not at
generic transport magnitude or undefined “path suppression” intuition.

This also clarifies why the post-closeout `GRCL-V3` work is still worth doing.

The point is no longer just to “make another `GRCV3` structure work.”
The point is to understand which distinctions can be stated truthfully in
landscape/source language and which differences remain only constructive or
runtime facts.

So this lane is now explicitly a landscape-semantics side-quest:

- it helps determine how to talk about behavior in landscape terms without
  silently smuggling runtime mechanism into the source vocabulary
- it helps separate real source-bearing distinctions from realization-only
  tuning choices
- and it improves the translation discipline for later families by showing
  where a plausible landscape phrase does or does not correspond to the actual
  dynamical mechanism

Any continuation after Iteration 32 should therefore be judged not only by
whether it recovers a spark lane, but by whether it makes the landscape
language more behavior-truthful.

## Iteration 33. Guard-Regime Compatibility Comparison

### Goal

Test whether the Iteration 32 geometry failure is mainly:

- a guard-regime interaction with path-mediated ingress
- or a stronger incompatibility of added path intermediacy itself

This iteration opens one new semantic comparison only.

It does **not** reopen realization tuning, path-node mass, path-edge coupling,
or any new `GRCL-v3` vocabulary.

### Checks

- [x] Keep the guarded baseline comparison explicit:
  - [x] saved baseline direct lane:
        `grcv3-rich-v4-transfer-mediation-probe`
  - [x] suppressed guarded path lane:
        `grcv3-rich-v4-single-intermediate-probe`
- [x] Add one valid open-regime direct control lane
- [x] Add one matching open-regime path lane
- [x] Use only allowed `rich.v4` semantic combinations
- [x] Do not use the invalid combination:
  - [x] `mediation_mode='guarded_pairs'` with `probe_guard_class='open_center'`
- [x] Hold path structure fixed inside each comparison pair:
  - [x] direct vs direct
  - [x] `single_intermediate` vs `single_intermediate`
- [x] Hold the open-regime semantics matched between the new control/probe:
  - [x] same `mediation_mode`
  - [x] same `probe_guard_class`
  - [x] same spill policy
  - [x] same pair-mediation classes
- [x] Compare all four lanes on the same step window:
  - [x] guarded direct baseline
  - [x] guarded `single_intermediate`
  - [x] open-regime direct control
  - [x] open-regime `single_intermediate`
- [x] Record which explanation survives:
  - [ ] guard-path interaction is the main issue
  - [ ] extra-hop path topology remains the main issue
  - [x] both guard regime and path topology matter materially

### Implementation Notes

- This iteration is justified by Iteration 32 only.
- Reason:
  - Iteration 32 showed that path ingress survives while weak-axis geometry
    fails to form
  - that makes a guard-regime semantic probe evidence-led rather than
    speculative
- Locked semantic question:
  - does a less restrictive valid guard regime make path-mediated ingress
    geometrically productive?
- Locked comparison rule:
  - do not test only the path lane
  - always add the matching direct control under the same open regime
- Preferred valid open-regime target:
  - `mediation_mode='attenuated_pairs'`
  - `probe_guard_class='open_center'`
- Reason for that target:
  - it stays inside already-allowed `rich.v4` vocabulary
  - it avoids the invalid
    `guarded_pairs + open_center` combination
  - it gives a cleaner semantic comparison than reopening multiple fields
- Locked path comparison surface:
  - reuse the existing `single_intermediate` meaning only
- Explicitly deferred for this iteration:
  - new topology classes
  - new guard classes
  - new mediation families
  - realization-only tuning
  - runtime constitutive changes
- Decision rule:
  - if the open-regime direct control improves but the open-regime
    `single_intermediate` lane still fails, extra-hop topology remains the
    stronger incompatibility
  - if the open-regime `single_intermediate` lane recovers materially, the
    issue is mainly guard-path interaction
  - if both open-regime lanes shift materially but the path lane still lags,
    record that both semantics contribute and do not collapse them into one
    explanation

### Verification

- [x] The new comparison uses only valid `rich.v4` source combinations
- [x] The iteration adds matched direct and path lanes under the same open
  semantic regime
- [x] The result is recorded as a semantic-boundary finding, not as generic
  “more/less spark”
- [x] Any later continuation stays tied to the landscape claim the comparison
  actually supports

Focused verification executed with:

- `./.venv/bin/python -m unittest tests.landscapes.test_grcv3_extensions tests.models.test_grc_v3_landscape_runtime tests.telemetry.test_experiments`
- result: `Ran 87 tests ... OK`

### Summary

Iteration 33 is complete.

Its job was not to “open the guard” generically.
Its job was to decide whether path-mediated intermediacy fails because the
current guarded regime makes the ingress geometrically non-productive, or
whether extra-hop topology remains incompatible even under a matched valid open
regime.

That comparison now has a clear result:

- guarded direct baseline:
  - `spark_candidate=2`
  - `spark=2`
  - `split_init=2`
  - `split_complete=2`
- guarded `single_intermediate`:
  - `spark_candidate=0`
  - `spark=0`
  - `split_init=0`
  - `split_complete=0`
- open-regime direct control:
  - `spark_candidate=0`
  - `spark=0`
  - `split_init=0`
  - `split_complete=0`
- open-regime `single_intermediate`:
  - `spark_candidate=0`
  - `spark=0`
  - `split_init=0`
  - `split_complete=0`

So the valid open-regime comparison does **not** support the simple story:

- “the current guarded regime is the thing blocking path-mediated ingress”

Instead, the open semantic regime suppresses the direct control lane as well.

The open path lane still shows the same Iteration 32 failure signature:

- earliest material divergence remains at step `0`
- earliest divergence reason remains:
  - `probe_shell_gradient_norm_divergence`
- diagnosed failure mode remains:
  - `probe_shell_ingress_arrives_but_fails_to_form_weak_axis_geometry`

At the same time, the open direct control does not behave like the guarded
baseline:

- open direct step `1` center `min_signed_eigenvalue = -0.42593100404921846`
- guarded direct step `1` center `min_signed_eigenvalue = -0.643843054198469`

So Iteration 33 lands on the third explanation:

- both guard regime and path topology matter materially

More specifically:

- changing to a valid open regime weakens or destabilizes the direct baseline
  lane enough to suppress spark
- while `single_intermediate` path mediation still fails to convert surviving
  ingress into the needed weak-axis geometry

That means the next semantic question, if this side-quest continues, is no
longer “is `guarded_center` simply too restrictive?”

It is narrower:

- what landscape statement, if any, can describe a transfer regime that
  remains compatible with direct weak-axis formation while also making
  intermediated ingress geometrically productive

Until that is answered, the current evidence does not justify treating
“openness” as a simple monotone rescue knob for path-mediated transfer.

## Iteration 34. Asymmetric Center-Coupling Refinement

### Goal

Test whether a narrower `center_coupling_classes` refinement can:

- preserve the direct guarded baseline lane
- while making `single_intermediate` path-mediated ingress geometrically more
  compatible with weak-axis formation

This iteration stays entirely inside existing `transfer_mediation` semantics.

It does **not** open a new semantic family.
It does **not** reopen guard-regime switching.
It does **not** touch runtime realization magnitudes.

### Checks

- [x] Keep the guarded direct baseline explicit:
  - [x] saved baseline direct lane:
        `grcv3-rich-v4-transfer-mediation-probe`
  - [x] suppressed guarded path lane:
        `grcv3-rich-v4-single-intermediate-probe`
- [x] Add one refined direct control lane using only
  `center_coupling_classes`
- [x] Add one matching refined `single_intermediate` lane using the same
  `center_coupling_classes`
- [x] Keep all other transfer semantics fixed:
  - [x] same `mediation_mode`
  - [x] same `probe_guard_class`
  - [x] same spill policy
  - [x] same pair-mediation classes
- [x] Keep path structure fixed inside each comparison pair:
  - [x] direct vs direct
  - [x] `single_intermediate` vs `single_intermediate`
- [x] Use a refinement that is narrower than the already-rejected blunt probes:
  - [x] not full open-regime switching
  - [x] not symmetric stable-axis blocking
  - [x] not realization-only tuning
- [x] Compare all four lanes on the same step window:
  - [x] guarded direct baseline
  - [x] guarded `single_intermediate`
  - [x] refined direct control
  - [x] refined `single_intermediate`
- [x] Record which explanation survives:
  - [x] asymmetric center-coupling can preserve direct spark and materially
        improve path geometry
  - [ ] asymmetric center-coupling still fails to matter materially
  - [ ] asymmetric center-coupling destabilizes the direct baseline too

### Implementation Notes

- This iteration is justified by Iteration 33.
- Reason:
  - broad semantic regime switching proved too blunt
  - symmetric center-coupling changes also over-guarded the direct lane
  - so the next semantic move must be narrower than both
- Locked semantic surface:
  - `transfer_mediation.center_coupling_classes` only
- Locked refinement target:
  - an asymmetric stable-axis coupling assignment
- Preferred first diagnostic assignment:
  - `[north, strong]`
  - `[south, weak]`
- Reason for that first assignment:
  - it preserves the direct spark lane in the current evidence sweep
  - and it moves the `single_intermediate` lane away from the previous
    near-zero weak-axis curvature failure
- Explicitly deferred for this iteration:
  - new guard classes
  - new mediation modes
  - new topology classes
  - multiple competing refinement fixtures in one pass
  - realization-only tuning
- Decision rule:
  - if the refined direct control keeps spark while the refined path lane shows
    materially improved weak-axis geometry, record that
    `center_coupling_classes` is a real finer-grained semantic lever even if
    spark is not yet restored
  - if the refined direct control collapses, reject the refinement as still too
    blunt
  - if neither direct nor path behavior changes materially, reject the
    refinement as semantically uninformative

### Verification

- [x] The iteration changes only `center_coupling_classes`
- [x] The refined direct control remains a valid comparison against the guarded
  baseline
- [x] The refined path lane is judged on geometric movement, not only event
  counts
- [x] The result is recorded as a semantic-refinement finding rather than a
  generic parameter tweak

Focused verification executed with:

- `./.venv/bin/python -m unittest tests.landscapes.test_grcv3_extensions tests.models.test_grc_v3_landscape_runtime tests.telemetry.test_experiments`
- result: `Ran 91 tests ... OK`

### Summary

Iteration 34 is complete.

Its job was not to broaden semantics again.
Its job was to test whether a finer-grained, already-valid semantic refinement
inside `transfer_mediation` can preserve the direct lane while making
path-mediated ingress more geometrically productive than the current
`single_intermediate` realization.

That refinement now has a clear result.

Implemented refined comparison lanes:

- direct refined control:
  - `grcv3-rich-v4-asymmetric-center-coupling-probe`
- matching path lane:
  - `grcv3-rich-v4-asymmetric-center-coupling-single-intermediate-probe`
- locked refinement:
  - `center_coupling_classes = [[north, strong], [south, weak]]`

Observed `50`-step event counts:

- guarded direct baseline:
  - `spark_candidate=2`
  - `spark=2`
  - `split_init=2`
  - `split_complete=2`
- guarded `single_intermediate`:
  - `spark_candidate=0`
  - `spark=0`
  - `split_init=0`
  - `split_complete=0`
- refined direct control:
  - `spark_candidate=2`
  - `spark=2`
  - `split_init=2`
  - `split_complete=2`
- refined `single_intermediate`:
  - `spark_candidate=0`
  - `spark=0`
  - `split_init=0`
  - `split_complete=0`

So the refined direct control stays behavior-compatible with the guarded
baseline.

At the same time, the refined path lane moves materially in geometry:

- guarded `single_intermediate` step `1`
  `min_signed_eigenvalue = 5.492859163990358e-11`
- refined `single_intermediate` step `1`
  `min_signed_eigenvalue = -0.4178743887154774`
- refined direct control step `1`
  `min_signed_eigenvalue = -0.404853768501391`

This is the first post-Iteration-30 result showing that a narrow semantic
refinement inside `transfer_mediation` can move the path lane away from the
earlier “no weak-axis geometry forms” failure.

The trace diagnosis changes accordingly:

- earliest material divergence still occurs at step `0`
- earliest divergence reason still begins at probe-shell gradient structure
- but the diagnosed failure mode shifts from:
  - `probe_shell_ingress_arrives_but_fails_to_form_weak_axis_geometry`
- to:
  - `final_candidate_transition_blocked_after_geometry_near_correct`

So Iteration 34 establishes a stronger semantic result than Iteration 33:

- asymmetric `center_coupling_classes` is a real finer-grained semantic lever
- it can preserve the direct spark lane
- and it can materially improve path-mediated weak-axis geometry
- but it still does not restore the full spark lifecycle for the current
  `single_intermediate` lane

That means the next question, if this side-quest continues, is no longer:

- can path-mediated ingress form the right weak-axis geometry at all?

It is narrower:

- what semantic boundary separates “geometry is now near-correct” from
  “spark-candidate transition and downstream lifecycle still do not trigger”

## Iteration 35. Candidate-Transition Failure Trace

### Goal

Locate the first point where the refined direct lane enters the spark pipeline
while the refined `single_intermediate` lane stays behind.

This iteration is downstream of Iteration 34.

It does **not** open new `GRCL-v3` semantics yet.
It does **not** tune runtime coefficients.
It does **not** revisit broad guard-regime switching.

Its job is to make the remaining transition failure explicit before any new
semantic refinement is proposed.

### Checks

- [x] Keep the comparison restricted to the Iteration 34 refined pair:
  - [x] refined direct control:
        `grcv3-rich-v4-asymmetric-center-coupling-probe`
  - [x] refined path lane:
        `grcv3-rich-v4-asymmetric-center-coupling-single-intermediate-probe`
- [x] Identify the first step where the refined direct lane emits
  `spark_candidate`
- [x] Record the actual candidate-site payloads from that direct-lane step
- [x] Compare the same semantic sites in the refined path lane on that step
- [x] Compare candidate-transition-relevant quantities on:
  - [x] monitored center gradient / signed eigenvalues
  - [x] candidate-site gradient norms
  - [x] candidate-site signed eigenvalues
  - [x] candidate-site flux / potential context
  - [x] probe-role asymmetry context
  - [x] path-egress vs spill flux context
  - [x] support-spoke participation context
- [x] Record whether the remaining failure is best described as:
  - [x] candidate sites never settle enough to enter the spark gate
  - [ ] candidate sites settle but fail a later runtime transition
  - [ ] the monitored center proxy is not the operative transition site

### Implementation Notes

- This iteration is justified by Iteration 34 only.
- Reason:
  - Iteration 34 showed that path-lane weak-axis geometry can become
    near-correct
  - but the spark pipeline still does not start
  - so the remaining ambiguity now lives at the candidate-transition boundary
    itself
- Locked comparison rule:
  - compare the refined direct lane against the refined path lane only
- Locked artifact preference:
  - machine-readable transition trace first
  - optional human-readable script second
- Expected semantic importance:
  - if the path lane fails because the actual candidate-capable sites do not
    settle, the next semantic refinement should target localization or
    candidate-site settlement rather than center geometry in the abstract
- Explicitly deferred for this iteration:
  - new semantic fixtures beyond the existing refined pair
  - new topology classes
  - new mediation modes
  - runtime constitutive changes

### Verification

- [x] The trace is anchored to the first real `spark_candidate` step in the
  refined direct lane
- [x] The comparison includes the actual candidate-capable sites, not only the
  monitored center proxy
- [x] The result ends with one explicit transition-blocker diagnosis
- [x] Any later semantic refinement is justified by this transition trace, not
  by another broad guess

Focused verification:

- `./.venv/bin/python -m unittest tests.telemetry.test_experiments`
- `./.venv/bin/python scripts/trace_grcv3_candidate_transition_failure.py --baseline-seed configs/landscapes/seed/grcv3-rich-v4-asymmetric-center-coupling-probe.seed.yaml --comparison-seed configs/landscapes/seed/grcv3-rich-v4-asymmetric-center-coupling-single-intermediate-probe.seed.yaml --profile seed_baseline --steps 8`
- `./.venv/bin/python -m unittest tests.landscapes.test_grcv3_extensions tests.models.test_grc_v3_landscape_runtime tests.telemetry.test_experiments`

Verification result:

- `Ran 19 tests in 27.348s ... OK`
- machine-readable transition trace emitted successfully
- `Ran 94 tests in 127.280s ... OK`

### Summary

Iteration 35 is complete.

The transition trace shows that the first real `spark_candidate` step in the
refined direct lane is step `6`.

The operative candidate-capable sites are not the monitored center.
They are the realized `basin_load_carrier` nodes:

- `spindle_core::carrier:0` (`north`)
- `spindle_core::carrier:2` (`south`)

At step `6`, both direct-lane carrier sites pass the candidate gate with:

- `gradient_norm = 0.0004501151590211475`
- `signed_eigenvalues = [-0.453633948452125, 0.42169087835430163]`

At the same semantic sites in the refined `single_intermediate` lane, the
center still shows sustained negative curvature, but the candidate-capable
carrier sites do not settle into gate-passing states:

- `spindle_core::carrier:0`:
  - `gradient_norm = 0.019097964156250428`
  - `signed_eigenvalues = [0.049353307116097575, 0.04942021450403506]`
- `spindle_core::carrier:2`:
  - `gradient_norm = 0.01922080978815861`
  - `signed_eigenvalues = [0.048792158174801495, 0.048857067196722406]`

The center proxy therefore stops being the decisive diagnostic site for this
lane.
Both refined lanes hold negative center curvature through the candidate step
window, with center negative-curvature run length `7` in both cases, but only
the direct lane localizes that geometry into carrier-site settlement.

So the remaining blocker is now explicit:

- `candidate_sites_never_settle_enough_to_enter_spark_gate`

The next semantic question is therefore narrower than “can weak-axis geometry
form.”
It is:

- what semantic boundary controls localization or settlement at the actual
  candidate-capable carrier sites once the center geometry is already
  near-correct

## Iteration 36. Asymmetric Pair-Mediation Localization

### Goal

Test whether a narrower `pair_mediation_classes` refinement can:

- preserve at least one valid direct spark lane
- while making `single_intermediate` path-mediated ingress settle at the
  actual candidate-capable carrier sites

This iteration is downstream of Iteration 35.

It stays inside existing `transfer_mediation` semantics.
It does **not** reopen center-geometry refinement as the main question.
It does **not** switch guard regime.
It does **not** touch runtime realization magnitudes.

### Checks

- [x] Keep the comparison anchored to the Iteration 34 refined pair:
  - [x] refined direct control:
        `grcv3-rich-v4-asymmetric-center-coupling-probe`
  - [x] refined path lane:
        `grcv3-rich-v4-asymmetric-center-coupling-single-intermediate-probe`
- [x] Add one pair-localized direct control lane using only
  `pair_mediation_classes`
- [x] Add one matching pair-localized `single_intermediate` lane using the
  same `pair_mediation_classes`
- [x] Keep all other transfer semantics fixed:
  - [x] same `mediation_mode`
  - [x] same `probe_guard_class`
  - [x] same spill policy
  - [x] same `center_coupling_classes`
  - [x] same `path_topology` inside each comparison pair
- [x] Use a refinement that explicitly targets carrier-site localization:
  - [x] strengthen one stable-axis direct pair
  - [x] block the opposite stable-axis direct pair
  - [x] keep only the matching transport-side cross pair weakly active
- [x] Compare all four lanes on the same step window:
  - [x] Iteration 34 refined direct control
  - [x] Iteration 34 refined `single_intermediate`
  - [x] pair-localized direct control
  - [x] pair-localized `single_intermediate`
- [x] Record which explanation survives:
  - [ ] pair-localized mediation preserves direct spark and rescues path
        candidate settlement
  - [x] pair-localized mediation preserves direct spark but path candidate
        settlement still fails
  - [ ] pair-localized mediation is too blunt and collapses even the direct
        lane

### Implementation Notes

- This iteration is justified by Iteration 35 only.
- Reason:
  - Iteration 35 showed that the monitored center is no longer the decisive
    failure site
  - the remaining blocker lives at the actual candidate-capable carrier sites
  - so the next semantic refinement should act on carrier-to-probe pair
    coverage before any broader semantic change is considered
- Locked semantic surface:
  - `transfer_mediation.pair_mediation_classes` only
- Locked starting refinement:
  - `[north, north, strong]`
  - `[south, south, blocked]`
  - `[east, north, weak]`
  - `[west, south, blocked]`
- Reason for that first assignment:
  - it remains theory-correct as a direct declaration of how already-declared
    transfer pairs are allowed to pass load
  - it preserves a direct spark lane in the current evidence sweep
  - it tests whether explicit one-sided pair localization can settle the path
    lane at an operative candidate site rather than only at the center proxy
- Explicitly deferred for this iteration:
  - spill-policy switching
  - new center-coupling refinements
  - new topology classes
  - realization-only tuning
  - multi-fixture semantic sweeps in the recorded lane

### Verification

- [x] The iteration changes only `pair_mediation_classes`
- [x] The direct control still emits at least one valid spark lifecycle event
- [x] The path lane is judged on candidate-site settlement, not only event
  counts
- [x] The result is recorded as a carrier-site localization finding rather than
  a generic parameter tweak

Focused verification:

- `./.venv/bin/python -m unittest tests.landscapes.test_grcv3_extensions tests.models.test_grc_v3_landscape_runtime tests.telemetry.test_experiments`
- `./.venv/bin/python scripts/trace_grcv3_candidate_transition_failure.py --baseline-seed configs/landscapes/seed/grcv3-rich-v4-asymmetric-pair-mediation-probe.seed.yaml --comparison-seed configs/landscapes/seed/grcv3-rich-v4-asymmetric-pair-mediation-single-intermediate-probe.seed.yaml --profile seed_baseline --steps 12`

Verification result:

- `Ran 98 tests in 150.062s ... OK`
- machine-readable transition trace emitted successfully

### Summary

Iteration 36 is complete.

Its job was to test whether source-level pair localization can move the
remaining blocker from “candidate sites never settle” to an actual path-lane
candidate transition, while keeping the Iteration 34 center-coupling
refinement fixed.

Implemented comparison lanes:

- pair-localized direct control:
  - `grcv3-rich-v4-asymmetric-pair-mediation-probe`
- matching pair-localized path lane:
  - `grcv3-rich-v4-asymmetric-pair-mediation-single-intermediate-probe`
- locked refinement:
  - `pair_mediation_classes = [[north, north, strong], [south, south, blocked], [east, north, weak], [west, south, blocked]]`

The semantic result is clear.

The localized direct control still supports a valid spark lifecycle, but it is
no longer bilaterally distributed.
The first real `spark_candidate` step moves to step `8`, and only one
candidate-capable carrier site remains operative:

- `spindle_core::carrier:0` (`north`)

At that step, the localized direct lane passes the candidate gate there with:

- `gradient_norm = 0.00033992890868225317`
- `signed_eigenvalues = [-0.48204195220843327, 0.44447845876383224]`

The matching localized `single_intermediate` lane still does not settle that
same semantic site into the spark gate:

- `gradient_norm = 0.01993850079138037`
- `signed_eigenvalues = [0.049230882904539745, 0.04929392485210711]`

So Iteration 36 strengthens the localization diagnosis:

- `pair_mediation_classes` is a real semantic lever for direct carrier-site
  localization
- it can collapse the direct lane from two operative candidate sites to one
- but even explicit one-sided pair localization does not rescue the current
  path-mediated lane

The surviving blocker remains:

- `candidate_sites_never_settle_enough_to_enter_spark_gate`

That means the remaining gap is now narrower again.
It is no longer just “more localization.”
It is:

- what source-language distinction, if any, describes why path-mediated
  ingress can form near-correct center geometry and even tolerate explicit
  pair localization, yet still fails to settle the operative carrier site

## Iteration 37. Spill-Branch Semantics Boundary

### Goal

Determine whether the missing source distinction still belongs inside
`primitive.extensions.grcv3.transfer_mediation` by asking one narrower
question:

- does the landscape language need to say where lateral spill branches from in
  a path-mediated lane?

This iteration is downstream of Iteration 36.

It does **not** add runtime tuning.
It does **not** reopen center-coupling or pair-localization refinement.
It does **not** guess a solved “settlement retention” effect.

### Checks

- [x] Keep the comparison anchored to the Iteration 36 localized pair:
  - [x] direct localized control:
        `grcv3-rich-v4-asymmetric-pair-mediation-probe`
  - [x] path-localized `single_intermediate` lane:
        `grcv3-rich-v4-asymmetric-pair-mediation-single-intermediate-probe`
- [x] Add one narrow new `transfer_mediation` distinction:
  - [x] `spill_branch_mode`
- [x] Keep all other transfer semantics fixed:
  - [x] same `mediation_mode`
  - [x] same `pair_mediation_classes`
  - [x] same `probe_guard_class`
  - [x] same `lateral_spill_policy`
  - [x] same `center_coupling_classes`
  - [x] same `path_topology` inside each comparison pair
- [x] Use a source-structural branch-point distinction rather than an
  effect-oriented name:
  - [x] current/default branch point:
        `spill_branch_mode = carrier_branch`
  - [x] new probe branch point:
        `spill_branch_mode = mediated_branch`
- [x] Compare all four lanes on the same step window:
  - [x] Iteration 36 localized direct control
  - [x] Iteration 36 localized `single_intermediate`
  - [x] mediated-branch direct control
  - [x] mediated-branch `single_intermediate`
- [x] Record which explanation survives:
  - [x] the missing distinction still belongs inside `transfer_mediation`
  - [x] it is about spill branch point, not generic settlement strength
  - [x] mediated spill branching changes the operative candidate site in the
        path lane

### Implementation Notes

- This iteration is justified by Iteration 36 only.
- Reason:
  - Iteration 36 showed that even explicit one-sided pair localization does not
    make the path lane settle the direct-lane carrier site
  - but the current assembly still sends lateral spill directly from the
    carrier even when the ingress path is intermediated
  - so the remaining source question is whether spill branches before or after
    that mediated path
- Locked semantic surface:
  - `transfer_mediation.spill_branch_mode`
- Implemented field:
  - `spill_branch_mode`
- Implemented allowed values:
  - `carrier_branch`
  - `mediated_branch`
- Direct translation rule:
  - `carrier_branch` keeps lateral spill sourced from the carrier site
  - `mediated_branch` sources spill from the realized intermediated path node
    when the pair uses `single_intermediate` or `fan_in`
  - direct/no-path lanes keep the current direct spill structure
- Explicitly deferred for this iteration:
  - new topology classes
  - new center-coupling classes
  - new pair-mediation refinements
  - realization-only tuning

### Verification

- [x] The iteration adds one new direct source field under `transfer_mediation`
- [x] The matched direct control remains behavior-compatible
- [x] The path lane is judged on operative candidate-site identity, not only
  raw event counts
- [x] The result answers whether the missing meaning still belongs inside
  `transfer_mediation`

Focused verification:

- `./.venv/bin/python -m unittest tests.landscapes.test_grcv3_extensions tests.models.test_grc_v3_landscape_runtime tests.telemetry.test_experiments`
- `./.venv/bin/python scripts/trace_grcv3_candidate_transition_failure.py --baseline-seed configs/landscapes/seed/grcv3-rich-v4-mediated-spill-branch-probe.seed.yaml --comparison-seed configs/landscapes/seed/grcv3-rich-v4-mediated-spill-branch-single-intermediate-probe.seed.yaml --profile seed_baseline --steps 12`

Verification result:

- `Ran 102 tests in 184.262s ... OK`
- machine-readable transition trace emitted successfully

### Summary

Iteration 37 is complete.

It answers the Iteration 36 question directly.

The missing source-language distinction **does** still belong inside
`transfer_mediation`, and the right direct meaning is:

- where lateral spill branches from in a mediated lane

Implemented semantic field:

- `primitive.extensions.grcv3.transfer_mediation.spill_branch_mode`

Implemented values:

- `carrier_branch`
- `mediated_branch`

Implemented comparison lanes:

- mediated-branch direct control:
  - `grcv3-rich-v4-mediated-spill-branch-probe`
- mediated-branch path lane:
  - `grcv3-rich-v4-mediated-spill-branch-single-intermediate-probe`

The result closes the boundary cleanly.

The mediated-branch direct control remains valid and still enters the spark
lifecycle, with first direct `spark_candidate` at step `8`.

The mediated-branch `single_intermediate` lane now also enters the spark
lifecycle.
Its first `spark_candidate` occurs at step `5`.

Interpretation note:

- Iteration 37 does **not** say:
  - the previously tracked carrier site now settles
- Iteration 37 **does** say:
  - the path-mediated lane as a whole now reaches `spark_candidate` / `spark`
  - but it does so through a different operative site

So there are two different claims here and they must not be conflated:

- old carrier-site claim:
  - still false in the path lane
- whole-lane recovery claim:
  - now true in the path lane

Critically, the recovered path lane does **not** settle the old operative
carrier site first.
At the direct lane's carrier site (`spindle_core::carrier:0`), the comparison
lane still shows:

- `gradient_norm = 0.02334522909124525`
- `signed_eigenvalues = [-1.1905263379249812e-11, 2.095036232149816e-11]`

So the Iteration 36 carrier-site blocker remains true at that direct-lane site.

But the comparison lane now reaches `spark_candidate` through a **different**
operative site:

- motif role:
  - `basin_transfer_path_node`
- realized key:
  - `spindle_core::transfer_path:east:north`
- first comparison `spark_candidate` step:
  - `5`
- candidate payload:
  - `gradient_norm = 0.00028255202622410843`
  - `signed_eigenvalues = [-0.031741335252358914, 0.03294850294541024]`

So Iteration 37 gives the closure the side-quest needed:

- the missing meaning was not “more settlement strength”
- it was a direct structural distinction about spill branch point
- and that distinction still fits cleanly inside `transfer_mediation`

The deeper lesson is sharper than “the path lane works now.”
It is:

- `carrier_branch` keeps the operative settlement burden on the carrier site
- `mediated_branch` allows the operative settlement locus to migrate onto the
  intermediated path itself
- so the language requirement is not only “can ingress spark?”
- it is also:
  - “where is the language saying the operative settlement locus lives?”

Implementation-vs-theory clarification:

- in native assembly, the mediated case is realized by inserting a real
  `basin_transfer_path_node` into the ingress route
- but the intended language meaning is not merely “add a node on an edge”
- the intended meaning is:
  - direct ingress is immediately carrier-to-probe
  - mediated ingress passes through an intermediate local structural site
- `GRCV3` realizes that site as a node because basin-chart nodes are where
  local differential structure, settlement, and spark semantics can actually
  live
- relative to RC itself, this is a discrete realization of an intermediate
  operative region along ingress, not a claim that the continuum theory has a
  literal path-node primitive

So the answer to the Iteration 36 question is now explicit:

- the source-language distinction is the branch point of lateral spill along
  mediated ingress

## Iteration 38. Settlement-Locus Regime Characterization

Iteration 38 is complete.

Goal:

- characterize the two spark-forming regimes exposed by Iteration 37 without
  adding new `rich.v4` semantics
- describe where the first spark lifecycle anchors, whether that anchor stays
  stable through `split_complete`, and whether later candidate migration occurs

Implementation:

- added `build_grcv3_landscape_settlement_locus_regime_trace(...)` to
  `pygrc.telemetry.experiments`
- exported the helper through `pygrc.telemetry`
- added `scripts/trace_grcv3_settlement_locus_regimes.py`
- added focused telemetry coverage for the characterization trace

Comparison lanes:

- carrier-site regime reference:
  - `grcv3-rich-v4-mediated-spill-branch-probe`
- path-node regime reference:
  - `grcv3-rich-v4-mediated-spill-branch-single-intermediate-probe`

The result is clear: Iteration 37 did not merely recover “one more working
path lane.” It exposed two distinct spark-forming settlement regimes.

Carrier-site regime:

- first `spark_candidate`:
  - step `8`
- first `split_complete`:
  - step `9`
- first lifecycle anchor:
  - motif role `basin_load_carrier`
  - realized key `spindle_core::carrier:0`
- anchor stability:
  - remains the same site through the first
    `spark_candidate -> split_init -> spark -> split_complete` lifecycle
- later migration:
  - none observed over 12 steps

Path-node regime:

- first `spark_candidate`:
  - step `5`
- first `split_complete`:
  - step `6`
- first lifecycle anchor:
  - motif role `basin_transfer_path_node`
  - realized key `spindle_core::transfer_path:east:north`
- anchor stability:
  - remains the same site through the first
    `spark_candidate -> split_init -> spark -> split_complete` lifecycle
- later migration:
  - yes
  - by step `11`, later `spark_candidate` events occur on split children of the
    first path-node anchor

Pre-first-candidate signature comparison:

- carrier-site regime:
  - last pre-candidate step `7`
  - center weak-axis signed curvature `-0.0019706776466451013`
  - probe-gradient spread `0.017712896238265552`
  - path-node count `0`
- path-node regime:
  - last pre-candidate step `4`
  - center weak-axis signed curvature `-0.001513192604532173`
  - probe-gradient spread `0.021912722253211392`
  - path-node count `4`

Interpretation:

- the first lifecycle anchor is stable in both regimes
- the semantic difference is not just “which site happens to win first”
- it is a real difference in operative settlement locus:
- direct lane: carrier-site settlement regime
- mediated-branch path lane: path-node settlement regime
- only the path-node regime shows subsequent migration onto split children

Authoritative characterization:

- the direct lane stays on the carrier-site regime
- the mediated path lane first anchors on the path node at step `5`
- and later migrates onto split children at step `11`

This description is the core Iteration 38 result.
The saved visuals are supporting evidence, but the important closure is the
language-level regime statement above.

So Iteration 38 strengthens the language result from Iteration 37:

- `transfer_mediation` now needs to talk not only about whether mediated
  ingress can spark
- it also needs to support truthful description of where the first operative
  settlement locus lives and whether that regime later propagates onto derived
  child sites

This was a characterization iteration only.
No new source vocabulary or runtime family behavior was introduced beyond the
observability needed to describe the two regimes.

## Iteration 39. Settlement-Regime Multiplicity Under Spill Policy

Goal:

- determine whether Iteration 38 revealed the full settlement-regime space now
  visible inside `transfer_mediation`, or only the first productive split
- test whether `lateral_spill_policy` exposes additional regime types beyond:
  - stable carrier-site regime
  - path-node regime with later migration onto split children

This iteration stays inside existing `rich.v4` semantics.

It does **not** open a new semantic family.

Reference point:

- the direct language result from Iteration 38:
  - the direct lane stays on the carrier-site regime
  - the mediated path lane first anchors on the path node at step `5`
  - and later migrates onto split children at step `11`

Question:

- is that two-regime split the whole currently justified language result?
- or does `lateral_spill_policy` reveal further distinct settlement-locus
  regimes under otherwise matched mediation semantics?

Planned comparison surface:

- matched direct/path controls under the same already-validated
  `transfer_mediation` structure
- vary only:
  - `lateral_spill_policy`
- keep fixed:
  - `path_topology`
  - `pair_mediation_classes`
  - `center_coupling_classes`
  - `spill_branch_mode`
  - all geometry / carrier-placement semantics

Preferred comparison lanes:

- `carrier_branch + role_locked`
- `carrier_branch + axis_locked`
- `mediated_branch + role_locked`
- `mediated_branch + axis_locked`

Optional follow-on only if valid and still theory-clean:

- `mediated_branch + open`

Acceptance questions:

- where does first `spark_candidate` anchor?
- does the first lifecycle anchor stay stable through `split_complete`?
- does later migration occur?
- if migration occurs, where does it go?
  - no migration
  - path node -> split child
  - carrier site -> split child
  - another still-unnamed regime

Interpretation rule:

- judge the result as a language-level regime map, not as “which parameter set
  performs best”
- if new settlement-locus regimes appear under `lateral_spill_policy`, record
  them as additional `transfer_mediation` regime distinctions
- only if this space is exhausted without closure should a new direct semantic
  family be considered

### Verification

- [x] Added the missing role-locked comparison fixtures for both:
  - carrier-branch direct/path
  - mediated-branch direct/path
- [x] Verified the new fixtures parse as valid `rich.v4` transfer-mediation
  seeds
- [x] Compared the four branch/policy combinations over both:
  - 12-step settlement-locus traces
  - 50-step event-count runs
- [x] Recorded whether any new settlement regime appears

Focused verification:

- `./.venv/bin/python -m unittest tests.landscapes.test_grcv3_extensions tests.models.test_grc_v3_landscape_runtime tests.telemetry.test_experiments`
- `./.venv/bin/python scripts/trace_grcv3_settlement_locus_regimes.py --baseline-seed configs/landscapes/seed/grcv3-rich-v4-role-locked-asymmetric-pair-mediation-probe.seed.yaml --comparison-seed configs/landscapes/seed/grcv3-rich-v4-role-locked-asymmetric-pair-mediation-single-intermediate-probe.seed.yaml --profile seed_baseline --steps 12`
- `./.venv/bin/python scripts/trace_grcv3_settlement_locus_regimes.py --baseline-seed configs/landscapes/seed/grcv3-rich-v4-role-locked-mediated-spill-branch-probe.seed.yaml --comparison-seed configs/landscapes/seed/grcv3-rich-v4-role-locked-mediated-spill-branch-single-intermediate-probe.seed.yaml --profile seed_baseline --steps 12`

Verification result:

- `Ran 111 tests in 223.675s ... OK`
- both role-locked trace commands emitted machine-readable regime traces with:
  - no `spark_candidate`
  - no regime label
  - no later migration

### Summary

Iteration 39 is complete.

It does **not** reveal a third productive settlement regime.

Instead, it closes the multiplicity question more sharply:

- `carrier_branch + axis_locked`
  - direct lane:
    - stable carrier-site regime
  - path lane:
    - no productive regime
- `mediated_branch + axis_locked`
  - direct lane:
    - stable carrier-site regime
  - path lane:
    - stable path-node regime
    - later migration onto split children
- `carrier_branch + role_locked`
  - direct lane:
    - no productive regime
  - path lane:
    - no productive regime
- `mediated_branch + role_locked`
  - direct lane:
    - no productive regime
  - path lane:
    - no productive regime

50-step event-count comparison:

- `carrier_branch + axis_locked`
  - direct:
    - `spark_candidate=1`, `spark=1`, `split_complete=1`
  - path:
    - all `0`
- `mediated_branch + axis_locked`
  - direct:
    - `spark_candidate=1`, `spark=1`, `split_complete=1`
  - path:
    - `spark_candidate=7`, `spark=7`, `split_complete=7`
- both `role_locked` comparisons:
  - direct:
    - all `0`
  - path:
    - all `0`

So the Iteration 38 two-regime result survives intact.

What Iteration 39 adds is the stronger language boundary:

- `lateral_spill_policy` is behavior-bearing
- but in this lane it does **not** multiply the settlement-regime space beyond
  the two already identified productive regimes
- instead, `role_locked` acts as a closure boundary:
  - it suppresses not only the path-node regime
  - but even the direct carrier-site regime

This means the important `transfer_mediation` statement is now:

- productive settlement here requires some structurally permitted lateral spill
- and the only productive regime split found so far remains:
  - carrier-site regime
  - path-node regime with later migration onto split children

So Iteration 39 exhausts the next justified spill-policy question without
opening a new direct semantic family.

## Iteration 40. Topology Portability Of The Path-Node Regime

Goal:

- determine whether the productive path-node regime found in Iterations 37 to
  39 is specific to `single_intermediate`
- or whether it survives under another already-implemented path topology

This iteration stays inside existing `rich.v4` semantics.

It does **not** open a new semantic family.

Reference point:

- current productive path-node regime:
  - `spill_branch_mode = mediated_branch`
  - `lateral_spill_policy = axis_locked`
  - `path_topology = single_intermediate`
- current regime description:
  - first `spark_candidate` anchors on a path node
  - first lifecycle remains stable through `split_complete`
  - later migration occurs onto split children

Question:

- is that path-node regime a general mediated-path phenomenon?
- or is it specific to pair-local path structure under
  `single_intermediate`?

Planned comparison surface:

- matched direct/path controls under the same already-validated
  `transfer_mediation` structure
- keep fixed:
  - `spill_branch_mode = mediated_branch`
  - `lateral_spill_policy = axis_locked`
  - `pair_mediation_classes`
  - `center_coupling_classes`
  - all geometry / carrier-placement semantics
- vary only:
  - `path_topology`

Preferred comparison lanes:

- direct control:
  - current mediated-branch direct control
- productive path reference:
  - current mediated-branch `single_intermediate`
- portability probe:
  - `mediated_branch + axis_locked + fan_in`

Acceptance questions:

- does first `spark_candidate` still anchor on a path node?
- does the first lifecycle remain stable through `split_complete`?
- does later migration still occur?
- if the regime changes, is the change:
  - no productive regime
  - same path-node regime
  - a different still-unnamed path-mediated regime

Interpretation rule:

- judge the result as a topology-portability statement about an already-known
  regime, not as a generic “better topology” comparison
- if `fan_in` preserves the path-node regime, record that the regime is
  portable across more than one mediated path realization
- if `fan_in` fails while `single_intermediate` succeeds, record that the
  current path-node regime is topology-specific inside `transfer_mediation`

### Verification

- [x] Added one focused `fan_in` probe that differs from the productive
  mediated-branch `single_intermediate` lane only in `path_topology`
- [x] Verified the new probe parses as a valid `rich.v4` transfer-mediation
  seed
- [x] Compared:
  - mediated-branch direct control
  - mediated-branch `single_intermediate`
  - mediated-branch `fan_in`
- [x] Judged the result on settlement-locus regime portability, not on generic
  event counts alone

Focused verification:

- `./.venv/bin/python -m unittest tests.landscapes.test_grcv3_extensions tests.models.test_grc_v3_landscape_runtime tests.telemetry.test_experiments`
- `./.venv/bin/python scripts/trace_grcv3_settlement_locus_regimes.py --baseline-seed configs/landscapes/seed/grcv3-rich-v4-mediated-spill-branch-probe.seed.yaml --comparison-seed configs/landscapes/seed/grcv3-rich-v4-mediated-spill-branch-fan-in-probe.seed.yaml --profile seed_baseline --steps 12`

### Summary

Iteration 40 is complete.

The productive path-node regime is **not** topology-portable across the current
implemented path-topology space.

Comparison result:

- direct control:
  - stable carrier-site regime
- mediated-branch `single_intermediate`:
  - stable path-node regime
  - first `spark_candidate` at step `5`
  - later migration onto split children
- mediated-branch `fan_in`:
  - no productive regime
  - no `spark_candidate`
  - no regime label
  - no later migration

50-step event-count comparison:

- direct control:
  - `spark_candidate=1`, `spark=1`, `split_complete=1`
- mediated-branch `single_intermediate`:
  - `spark_candidate=7`, `spark=7`, `split_complete=7`
- mediated-branch `fan_in`:
  - all `0`

So the Iteration 38 path-node regime survives only under the current
pair-local mediated-path realization.

What Iteration 40 adds is the sharper topology statement:

- the path-node regime is real
- but it is currently specific to `single_intermediate`
- `fan_in` does not preserve it even when:
  - `spill_branch_mode = mediated_branch`
  - `lateral_spill_policy = axis_locked`
  - the same pair and center-coupling semantics are held fixed

That means the current language result is:

- `transfer_mediation` can describe a productive path-node settlement regime
- but that regime is not yet portable across all currently implemented path
  topologies
- so `path_topology` remains a genuine behavior-bearing distinction, not merely
  an alternative realization of one stable regime

### Transfer-Mediation Closure Note

At this point the current `transfer_mediation` lane should be treated as
substantively exhausted for the spindle spark side-quest.

That does **not** mean the family failed.
It means the lane has already yielded the important language results it was
able to yield:

- `path_topology` is real and behavior-bearing
- `spill_branch_mode` is real and behavior-bearing
- `lateral_spill_policy` is real and behavior-bearing
- two productive settlement regimes are now clearly described:
  - carrier-site regime
  - path-node regime with later migration onto split children
- `role_locked` is a closure boundary
- the productive path-node regime is topology-specific to
  `single_intermediate`, not portable to `fan_in`

So the next justified move is **not** “one more `transfer_mediation` tweak.”

The next justified move is:

- either record this family as closed for the current side-quest
- or intentionally name the next direct semantic family that addresses the
  remaining unexplained behavior

The strongest current candidate for that next family is not another geometry or
mediation refinement.
It is a family about operative settlement ownership:

- `primitive.extensions.grcv3.settlement_regime`
- or, if narrowed further, `primitive.extensions.grcv3.settlement_locus`

Reason:

- the remaining question is no longer mainly:
  - how ingress reaches the probe
  - or how declared mediation structure is guarded
- it is now:
  - where productive settlement lives
  - whether it stays anchored or migrates
  - and whether later migration onto split children belongs to the
    source-language description

Why not the previously established families:

- `interior_geometry`
  - explains probe/support construction, not operative settlement ownership
- `interior_partition`
  - explains tier membership, not operative settlement ownership
- `interior_load_carriers`
  - explains carrier placement and declared coupling surface, not operative
    settlement ownership after ingress
- `boundary_geometry`
  - explains local clamp/boundary support construction, not the presently
    observed carrier-site versus path-node regime split

This candidate-family note has now been promoted into Iteration 41 below.

## Iteration 41. Lock The Settlement-Regime Family

### Goal

Promote the post-`transfer_mediation` candidate into an explicit next
`GRCL-v3` family-definition entry, while keeping the step theory-facing and
doc-only.

### Checks

- [x] Lock the preferred next family name:
  - [x] `primitive.extensions.grcv3.settlement_regime`
- [x] Record why `settlement_regime` is preferred over the narrower
      `settlement_locus`
- [x] Record what this family is expected to answer
- [x] Record why the previously established families are weaker next choices
- [x] Keep the solved-state/runtime-override boundary explicit
- [x] Defer any executable slice, seed design, or runtime implementation to a
      later iteration

### Implementation Notes

- Preferred family name:
  - `primitive.extensions.grcv3.settlement_regime`
- Narrower fallback label if later needed for one sub-surface only:
  - `primitive.extensions.grcv3.settlement_locus`
- Why `settlement_regime` is preferred:
  - the present evidence is not only about first candidate anchor location
  - it is also about whether settlement stays anchored or migrates
  - and whether later migration onto split children is part of the
    source-language description
- So the next family should be expected to answer:
  - what kind of site may become the operative settlement locus
  - whether settlement remains anchored at the first operative site or later
    migrates during spark/split
  - whether split children may inherit the operative settlement locus
  - whether that migration belongs to source semantics rather than being treated
    only as incidental runtime phenomenology
- Expected responsibilities of the already-established neighboring families:
  - `interior_geometry`
    - probe/support stencil, spacing, grouping, connectivity
  - `interior_partition`
    - tier existence and which tier is allowed to take load first
  - `interior_load_carriers`
    - carrier placement and declared transfer surface
  - `boundary_geometry`
    - local clamp/boundary support construction
  - `channel_geometry`
    - transport corridor realization and attachment path structure
  - `transfer_mediation`
    - how already-declared transfer pairs are mediated, guarded, and allowed to
      spill
- Why those others are weaker next choices here:
  - they remain important families
  - but the current remaining question is no longer mainly about geometry,
    partition, carrier placement, channel routing, or mediation structure
  - it is about operative settlement ownership and migration
- Explicitly still forbidden at this family-definition step:
  - solved spark/collapse outcomes as source truth
  - solved thresholds or gate states
  - direct numeric transport/gating overrides
  - source declarations that a specific runtime node must spark

### Verification

- [x] The next family is now named explicitly rather than left only as a
      recorded candidate
- [x] The naming choice is justified against the narrower alternative
- [x] The boundary against neighboring families remains explicit

### Summary

Iteration 41 is now locked at the vocabulary/checklist level.
The next direct semantic family is defined as
`primitive.extensions.grcv3.settlement_regime`, with
`primitive.extensions.grcv3.settlement_locus` retained only as a possible
narrower sub-surface name later.
No executable slice was opened in this step.

## Iteration 42. First Executable Settlement-Regime Slice

### Goal

Open the first narrow executable slice of
`primitive.extensions.grcv3.settlement_regime` and keep it tied directly to the
two productive regimes already evidenced by Iterations 37 to 40.

### Checks

- [x] Lock the first executable field set to:
  - [x] `settlement_regime.regime_class`
- [x] Keep the first allowed regime classes narrow:
  - [x] `carrier_site_regime`
  - [x] `path_node_regime`
- [x] Keep the first scope narrow:
  - [x] basin-centered interior probes in `grcv3.rich.v4`
  - [x] requires `interior_load_carriers`
  - [x] requires `transfer_mediation`
- [x] Keep the runtime meaning structural:
  - [x] candidate-site eligibility only
  - [x] split-child inheritance only where the regime implies it
- [x] Reject contradictory path-node declarations explicitly
- [x] Add matched direct/path regime fixtures and focused tests

### Implementation Notes

- Locked first executable field:
  - `primitive.extensions.grcv3.settlement_regime.regime_class`
- Locked first executable classes:
  - `carrier_site_regime`
    - first operative settlement must localize on `basin_load_carrier` sites
    - later split-child candidate inheritance is not part of the first slice
  - `path_node_regime`
    - first operative settlement must localize on `basin_transfer_path_node`
      sites
    - later split-child candidate inheritance is part of the first slice
- Explicit runtime meaning:
  - this slice does **not** prescribe solved thresholds, solved candidate
    scores, or direct spark outcomes
  - it constrains which realized site classes may enter the spark-candidate
    gate under the declared regime
- Explicit narrow validation boundary:
  - `path_node_regime` currently requires at least one non-direct
    `transfer_mediation.path_topology` assignment
  - otherwise the source claim is contradictory because no realized path-node
    settlement surface exists
- Implemented schema/validation in:
  - `src/pygrc/landscapes/extensions/grcv3.py`
- Implemented family-native plan/runtime support in:
  - `src/pygrc/models/grc_v3_landscape_native.py`
  - `src/pygrc/models/grc_v3_landscape.py`
  - `src/pygrc/models/grc_v3.py`
- Added matched positive fixtures:
  - `configs/landscapes/seed/grcv3-rich-v4-carrier-site-settlement-regime-probe.seed.yaml`
  - `configs/landscapes/seed/grcv3-rich-v4-path-node-settlement-regime-single-intermediate-probe.seed.yaml`
- Focused verification landed in:
  - `tests/landscapes/test_grcv3_extensions.py`
  - `tests/models/test_grc_v3_landscape_runtime.py`
  - `tests/telemetry/test_experiments.py`

### Verification

- [x] The first slice is executable rather than vocabulary-only
- [x] The direct carrier-site lane remains productive under
      `carrier_site_regime`
- [x] The productive single-intermediate path lane remains productive under
      `path_node_regime`
- [x] The path-node lane still shows later migration onto split children
- [x] Forcing `carrier_site_regime` onto the productive path lane suppresses
      the lane rather than silently preserving the old path-node behavior

### Summary

Iteration 42 is complete.
`settlement_regime` now has its first executable slice through
`regime_class`, and that slice is behavior-bearing rather than post-hoc
description.

The direct matched probe remains a `carrier_site_regime`:

- first `spark_candidate` anchors on `basin_load_carrier`
- the lane remains productive

The path matched probe remains a `path_node_regime`:

- first `spark_candidate` anchors on `basin_transfer_path_node`
- later `spark_candidate` events occur on split children
- the lane remains productive

And the new negative control matters:

- forcing `carrier_site_regime` onto the productive single-intermediate path
  lane suppresses `spark_candidate` entirely

So the first executable `settlement_regime` slice is now justified as direct
source semantics:

- it can preserve already-known productive regimes when matched correctly
- and it can close a lane when the declared operative settlement ownership is
  mismatched

## Iteration 43. Settlement-Regime Decomposition

### Goal

Determine whether the new `settlement_regime` family still bundles two facts
together:

- first operative settlement locus
- later split-child inheritance / migration

or whether those are already separable source distinctions.

### Checks

- [x] Keep the decomposition inside `settlement_regime`
- [x] Introduce the first narrow split:
  - [x] `initial_locus_class`
  - [x] `split_inheritance_mode`
- [x] Keep the first allowed values narrow:
  - [x] `initial_locus_class: carrier_site | path_node`
  - [x] `split_inheritance_mode: anchored | split_child_inheriting`
- [x] Preserve `regime_class` as a backward-compatible alias
- [x] Add an explicit `path_node + split_child_inheriting` control
- [x] Add the key mismatch probe:
  - [x] `path_node + anchored`

### Implementation Notes

- Implemented decomposition fields in:
  - `src/pygrc/landscapes/extensions/grcv3.py`
- Implemented runtime use in:
  - `src/pygrc/models/grc_v3.py`
- Added explicit decomposition fixtures:
  - `configs/landscapes/seed/grcv3-rich-v4-path-node-split-child-inheriting-settlement-probe.seed.yaml`
  - `configs/landscapes/seed/grcv3-rich-v4-path-node-anchored-settlement-probe.seed.yaml`
- Backward-compatibility rule:
  - `regime_class` still works as the coarse alias
  - when present, it lowers to:
    - `carrier_site_regime`
      - `initial_locus_class=carrier_site`
      - `split_inheritance_mode=anchored`
    - `path_node_regime`
      - `initial_locus_class=path_node`
      - `split_inheritance_mode=split_child_inheriting`
- Runtime meaning after decomposition:
  - `initial_locus_class` constrains where first productive settlement may
    enter the spark-candidate gate
  - `split_inheritance_mode` separately constrains whether later split children
    may re-enter that gate

### Verification

- [x] The explicit `path_node + split_child_inheriting` control remains
      productive
- [x] The explicit `path_node + anchored` probe still sparks
- [x] The anchored probe keeps first settlement on the same path node
- [x] The anchored probe suppresses later split-child candidate migration

### Summary

Iteration 43 is complete.
The result is stronger than a minor refinement:

- `initial_locus_class` and `split_inheritance_mode` are separable
  source-side distinctions
- they are not one inseparable bundled regime fact

The explicit control,
`path_node + split_child_inheriting`, preserves the productive repeated
path-node lane:

- `spark_candidate=3`
- `spark=3`
- `split_complete=3`
- later candidate migration onto split children still occurs

The key mismatch probe,
`path_node + anchored`, remains productive but changes the regime materially:

- first `spark_candidate` still anchors on the same path node at step `5`
- `split_init` and `spark` still begin at step `5`
- `split_complete` still occurs at step `6`
- but later split-child candidate migration no longer occurs
- total lifecycle counts contract to:
  - `spark_candidate=1`
  - `spark=1`
  - `split_complete=1`

So the Iteration 42 result can now be decomposed more honestly:

- path-node first settlement is one source distinction
- split-child inheritance is another
- and the current productive repeated path-node regime requires both together

## Iteration 44. Settlement-Regime Matrix Completion

### Goal

Complete the first `settlement_regime` matrix by testing the missing corner:

- `initial_locus_class=carrier_site`
- `split_inheritance_mode=split_child_inheriting`

The point is to determine whether split-child inheritance is a fully
independent semantic axis, or whether it still depends on initial settlement
locus in the current spindle lane.

### Checks

- [x] Add an explicit `carrier_site + split_child_inheriting` probe
- [x] Compare it against the existing `carrier_site + anchored` control
- [x] Record whether later split-child candidate migration occurs
- [x] Record whether a new repeated regime appears or not

### Implementation Notes

- Added explicit matrix-completion fixture:
  - `configs/landscapes/seed/grcv3-rich-v4-carrier-site-split-child-inheriting-settlement-probe.seed.yaml`
- Focused verification landed in:
  - `tests/landscapes/test_grcv3_extensions.py`
  - `tests/models/test_grc_v3_landscape_runtime.py`
  - `tests/telemetry/test_experiments.py`
- No new runtime fields were required for this step.
- The current runtime decomposition from Iteration 43 was sufficient to test the
  missing corner directly.

### Verification

- [x] The explicit `carrier_site + split_child_inheriting` probe still sparks
- [x] First settlement still anchors on a `basin_load_carrier`
- [x] Later split-child candidate migration still does **not** occur
- [x] No new repeated carrier-to-split-child regime appears

### Summary

Iteration 44 is complete.
The missing matrix corner does **not** open a third productive regime in the
current spindle lane.

`carrier_site + split_child_inheriting` behaves like this:

- first `spark_candidate` anchors on the same carrier site at step `8`
- `split_init` and `spark` also occur at step `8`
- `split_complete` occurs at step `9`
- total lifecycle counts remain:
  - `spark_candidate=1`
  - `spark=1`
  - `split_complete=1`
- later split-child candidate migration does not occur

So the stronger language result is:

- `split_inheritance_mode` is not a fully free semantic axis across initial
  loci in this lane
- it is productive as an independent distinction on the `path_node` side
- but it does not create a corresponding repeated inherited regime on the
  `carrier_site` side

That means the current regime space is **not** a full Cartesian product.
More specifically:

- only `path_node + split_child_inheriting` is currently a repeating regime
- `carrier_site + anchored` is productive but one-shot
- `path_node + anchored` is productive but one-shot
- `carrier_site + split_child_inheriting` is productive but one-shot

## Iteration 45. Settlement-Regime Post-Split Reentry Boundary

### Goal

Determine why only the productive
`initial_locus_class=path_node + split_inheritance_mode=split_child_inheriting`
lane re-enters through derived split children, while the productive
`carrier_site + split_child_inheriting` lane remains one-shot.

The point is to keep the next step diagnostic before naming another semantic
field:

- do the two inherited lanes differ because child sites never persist
- because child sites persist but never settle enough
- because child sites settle but do not form the right eigen signature
- or because they pass the candidate gate and still fail at a later runtime
  transition

### Checks

- [x] Add a focused post-split reentry trace for:
  - baseline `path_node + split_child_inheriting`
  - comparison `carrier_site + split_child_inheriting`
- [x] Record the first `split_complete` step in both lanes
- [x] Record the first descendant split-child gate-pass step in both lanes
- [x] Record the first descendant split-child `spark_candidate` step in both
  lanes
- [x] Diagnose the earliest surviving blocker in the comparison lane

### Implementation Notes

- Added the reusable helper:
  - `src/pygrc/telemetry/experiments.py`
    - `build_grcv3_landscape_settlement_reentry_trace(...)`
- Exported it through:
  - `src/pygrc/telemetry/__init__.py`
- Added a runnable trace script:
  - `scripts/trace_grcv3_settlement_reentry_boundary.py`
- Focused verification landed in:
  - `tests/telemetry/test_experiments.py`
- No runtime/source-semantic changes were required for this iteration.
- This step is observability-only inside the already-defined
  `settlement_regime` family.

### Verification

- [x] Baseline `path_node + split_child_inheriting` first completes its initial
  split at step `6`
- [x] Baseline descendant split children first pass the candidate gate at step
  `10`
- [x] Baseline descendant split children first emit `spark_candidate` at step
  `11`
- [x] Comparison `carrier_site + split_child_inheriting` first completes its
  initial split at step `9`
- [x] Comparison descendant split children persist through step `12`
- [x] Comparison descendant split children never pass the candidate gate
- [x] The diagnosed blocker is
  `derived_child_sites_never_settle_enough_to_enter_spark_gate`

### Summary

Iteration 45 is complete.

The current `settlement_regime` matrix is now characterized more truthfully by
post-split reentry behavior:

- `path_node + split_child_inheriting` is the only currently repeating regime
- it re-enters because derived split children eventually settle below the
  gradient threshold and then emit new `spark_candidate` events
- `carrier_site + split_child_inheriting` is not blocked by lack of child-site
  persistence
- it is blocked because those derived child sites never settle enough to
  re-enter the spark gate

So the next unresolved source-language question, if this family continues, is
no longer whether split-child inheritance exists.
It is whether there is another truthful semantic distinction behind
post-split reentry readiness itself.

## Iteration 46. Settlement-Regime Reentry Neighborhood Boundary

### Goal

Determine whether the surviving difference in post-split reentry readiness is
visible as a distinct derived-child neighborhood signature, rather than only as
an internal gate metric.

The point is to make the next remaining boundary more explicit before naming
another field:

- do repeating inherited child sites keep a distinct neighbor-role mix
- does that mix already differ at the matched descendant step where the
  repeating lane first becomes gate-ready
- and is the comparison lane still one-shot while retaining a different
  support-neighborhood burden

### Checks

- [x] Add a focused reentry-neighborhood trace for:
  - baseline `path_node + split_child_inheriting`
  - comparison `carrier_site + split_child_inheriting`
- [x] Record the matched descendant step where the baseline lane first passes
  the candidate gate again
- [x] Summarize descendant child-site neighborhood signatures at that matched
  step
- [x] Record the strongest surviving neighborhood boundary, if any

### Implementation Notes

- Added the reusable helper:
  - `src/pygrc/telemetry/experiments.py`
    - `build_grcv3_landscape_settlement_reentry_neighborhood_trace(...)`
- Extended descendant site summaries so they now carry neighborhood signatures:
  - neighbor site kinds
  - neighbor motif roles
  - edge kinds
  - mean conductance weight grouped by neighbor role/site kind
- Exported the helper through:
  - `src/pygrc/telemetry/__init__.py`
- Added the runnable trace script:
  - `scripts/trace_grcv3_settlement_reentry_neighborhood_boundary.py`
- Focused verification landed in:
  - `tests/telemetry/test_experiments.py`
- No runtime/source-semantic changes were required for this iteration.

### Verification

- [x] The matched post-split descendant step is step `10`
- [x] At step `10`, the repeating path-descendant lane has common neighbor
  motif roles:
  - `basin_support`
  - `basin_load_carrier`
- [x] At the same matched step, the one-shot carrier-descendant lane has common
  neighbor motif roles:
  - `basin_support`
  - `ridge_support`
- [x] The path-descendant mean gradient norm at the matched step is lower than
  the carrier-descendant mean gradient norm
- [x] The diagnosed neighborhood boundary is:
  `derived_child_reentry_correlates_with_carrier_neighbor_vs_ridge_support_neighbor_mix`

### Summary

Iteration 46 is complete.

The strongest surviving explanatory signature is now more explicit:

- repeating inherited child sites do not differ only by later gate outcome
- they already differ by retained neighborhood role mix at the matched
  descendant step
- the repeating path-descendant lane keeps:
  - `basin_support`
  - `basin_load_carrier`
  neighbors
- the one-shot carrier-descendant lane keeps:
  - `basin_support`
  - `ridge_support`
  neighbors

So the current boundary is sharper again:

- post-split reentry readiness is not yet explained just by inheritance
  existence
- and not only by child-site internal geometry/eigen signature
- it also correlates with a distinct inherited neighborhood role mix

That is not yet enough to justify a new source field on its own.
But it does identify the narrowest remaining question if this family
continues:

- whether `settlement_regime` needs a truthful source-side distinction around
  inherited child-site reentry support / neighborhood class

## Iteration 47. Settlement-Regime Descendant Support Isolation

### Goal

Narrow the Iteration 46 neighborhood result further by isolating whether the
behavior-bearing difference lives in:

- retained common support burden itself
- or the secondary non-support neighbor class attached to inherited child sites

The point is to avoid prematurely naming a broader “neighborhood class” field
if the actual surviving distinction is already narrower.

### Checks

- [x] Add a focused descendant support-isolation trace for:
  - baseline `path_node + split_child_inheriting`
  - comparison `carrier_site + split_child_inheriting`
- [x] Record whether both lanes keep the same descendant degree at the matched
  step
- [x] Record whether both lanes keep similar `basin_support` weight at the
  matched step
- [x] Record the isolated secondary non-support role in each lane
- [x] Diagnose the strongest surviving isolated support boundary

### Implementation Notes

- Added the reusable helper:
  - `src/pygrc/telemetry/experiments.py`
    - `build_grcv3_landscape_settlement_reentry_support_isolation_trace(...)`
- The new helper reuses the Iteration 46 neighborhood trace and reduces it to:
  - matched descendant degree
  - common `basin_support` weight
  - secondary non-support role identity
- Exported it through:
  - `src/pygrc/telemetry/__init__.py`
- Added the runnable trace script:
  - `scripts/trace_grcv3_settlement_reentry_support_isolation.py`
- Focused verification landed in:
  - `tests/telemetry/test_experiments.py`
- No runtime/source-semantic changes were required for this iteration.

### Verification

- [x] At the matched descendant step, both lanes keep degree set `[3]`
- [x] At the same step, both lanes keep nearly equal `basin_support` weight
  (difference `< 0.05`)
- [x] The repeating path-descendant lane isolates:
  - `secondary_roles = [basin_load_carrier]`
- [x] The one-shot carrier-descendant lane isolates:
  - `secondary_roles = [ridge_support]`
- [x] The diagnosed support-isolation boundary is:
  `reentry_correlates_with_secondary_carrier_neighbor_rather_than_secondary_ridge_support`

### Summary

Iteration 47 is complete.

The Iteration 46 neighborhood result now narrows further:

- the repeating and one-shot inherited child sites do **not** mainly differ in
  total common `basin_support` burden
- and they do **not** differ in descendant degree at the matched step
- the surviving isolated difference is the secondary non-support neighbor class

So the sharpest current reading is:

- repeating reentry correlates with retained secondary
  `basin_load_carrier` adjacency
- one-shot post-split behavior correlates with retained secondary
  `ridge_support` adjacency

That is the narrowest direct language boundary we have reached so far inside
`settlement_regime`.
If the family continues, the next decision is whether that isolated secondary
support class is direct enough to justify a new source-side distinction.

## Iteration 48. Settlement-Regime Secondary Support Counterfactual

### Goal

Run the decisive counterfactual implied by Iteration 47:

- if the repeating lane loses reentry when its retained secondary
  `basin_load_carrier` adjacency is removed, then that class is behavior-bearing
- if the one-shot lane still fails after removing its retained secondary
  `ridge_support` adjacency, then ridge absence alone is not sufficient to open
  reentry

The point is to decide whether the current isolated secondary support class is
already strong enough to count as the end-stop boundary for this family slice.

### Checks

- [x] Add a focused secondary-support counterfactual trace for:
  - repeating `path_node + split_child_inheriting`
  - one-shot `carrier_site + split_child_inheriting`
- [x] Remove descendant secondary `basin_load_carrier` adjacency after the
  first split in the repeating lane
- [x] Remove descendant secondary `ridge_support` adjacency after the first
  split in the one-shot lane
- [x] Record whether post-split reentry survives either counterfactual
- [x] Record the decisive diagnosed boundary

### Implementation Notes

- Added the reusable helper:
  - `src/pygrc/telemetry/experiments.py`
    - `build_grcv3_landscape_settlement_reentry_secondary_support_counterfactual_trace(...)`
- The new helper keeps the change telemetry-only:
  - after the first split completes, it prunes descendant edges matching the
    targeted secondary motif role
  - then refreshes transport/identity and continues the run
- Exported it through:
  - `src/pygrc/telemetry/__init__.py`
- Added the runnable trace script:
  - `scripts/trace_grcv3_settlement_reentry_secondary_support_counterfactual.py`
- Focused verification landed in:
  - `tests/telemetry/test_experiments.py`
- No runtime/source-semantic changes were required for this iteration.

### Verification

- [x] Natural repeating lane still re-enters at step `11`
- [x] Repeating-lane counterfactual applies at step `6`
- [x] Repeating-lane counterfactual removes only descendant
  `basin_load_carrier` edges
- [x] Repeating-lane counterfactual no longer re-enters
- [x] Natural one-shot lane still does not re-enter
- [x] One-shot-lane counterfactual applies at step `9`
- [x] One-shot-lane counterfactual removes only descendant `ridge_support`
  edges
- [x] One-shot-lane counterfactual still does not re-enter
- [x] The diagnosed counterfactual boundary is:
  `secondary_basin_load_carrier_is_necessary_but_removing_secondary_ridge_support_is_not_sufficient`

### Summary

Iteration 48 is complete.

The current boundary now looks decisive enough to treat as an end-stop for this
slice:

- retained secondary `basin_load_carrier` support is necessary for the current
  repeating reentry lane
- merely removing retained secondary `ridge_support` is not sufficient to
  rescue the one-shot lane

So the sharpest current language result is:

- the isolated secondary support class is not merely a correlated trace marker
- it is behavior-bearing in the strong sense needed for this family exercise

If `settlement_regime` continues from here, the next step should probably stop
being “one more diagnostic.”
It should become an explicit decision:

- either promote inherited secondary support class into a direct source-side
  distinction
- or stop and record that this is the present closure boundary

### Settlement-Regime Closure Note

The current preference is to **stop here and record Iteration 48 as the
present closure boundary** for this `settlement_regime` slice rather than
promoting a new field immediately.

Reason:

- Iteration 48 proves a behavior-bearing runtime necessity
- but it does **not yet** prove that inherited secondary support class is a
  clean direct-translation source contract the seed author should declare
- promoting it immediately would risk encoding a traced runtime requirement as
  source truth before the source-translation gap is shown explicitly

So the next justified step is no longer “add one more `settlement_regime`
field.”
It is:

- test whether existing structural vocabulary can already author the required
  secondary `basin_load_carrier` adjacency
- or whether that adjacency reveals a genuine translation gap that would justify
  a new field later

## Iteration 49. Secondary Support Structural Authorability Test

### Goal

Determine whether the currently necessary descendant secondary
`basin_load_carrier` support can be authored through **existing** structural
families, or whether a real source-language gap remains after Iteration 48.

The point is to keep the direct-translation discipline intact:

- if existing source structure can already force the required secondary support
  condition, no new `settlement_regime` field is justified
- if it cannot, then a new field becomes justified by a real authoring gap
  rather than by post-hoc runtime interpretation

### Checks

- [x] Treat the current Iteration 48 result as the target runtime condition:
  - descendant split children retain secondary `basin_load_carrier` adjacency
  - and the lane remains reentry-capable
- [x] Test whether that condition can be authored through existing structural
  families only, with priority on:
  - `transfer_mediation`
  - `interior_load_carriers`
  - `channel_geometry`
  - `boundary_geometry`
- [x] Record which of those families are expected to contribute and why
- [x] Record whether the target condition is:
  - already structurally authorable
  - or still a genuine translation gap

### Preferred Outcome

- If existing structural vocabulary can author the condition:
  - keep `settlement_regime` unchanged
  - record inherited secondary support class as a downstream structural
    consequence, not a new field
- If existing structural vocabulary cannot author the condition:
  - record that failure explicitly
  - and only then consider opening a new source-side distinction

### Implementation Notes

- Added the reusable helper:
  - `src/pygrc/telemetry/experiments.py`
    - `build_grcv3_landscape_secondary_support_authorability_trace(...)`
- The helper compares four lanes:
  - structural path lane before `settlement_regime`
  - explicit path lane after `settlement_regime`
  - structural direct control before `settlement_regime`
  - explicit direct control after `settlement_regime`
- It records:
  - whether the target secondary `basin_load_carrier` reentry condition is
    present
  - whether the structural and explicit path lanes match
  - which existing family payloads actually differ across the decisive path vs
    direct comparison
- Exported it through:
  - `src/pygrc/telemetry/__init__.py`
- Added the runnable trace script:
  - `scripts/trace_grcv3_secondary_support_authorability.py`
- Focused verification landed in:
  - `tests/telemetry/test_experiments.py`
- No runtime/source-semantic changes were required for this iteration.

### Verification

- [x] The pre-`settlement_regime` structural path lane already shows:
  - first reentry candidate at step `11`
  - secondary roles `[basin_load_carrier]`
- [x] The later explicit path lane shows the same target condition
- [x] The structural and explicit direct controls both lack the target
  condition
- [x] Between the structural and explicit path seeds, `transfer_mediation`
  remains the same and the only added family is `settlement_regime`
- [x] Between the structural path and structural direct seeds:
  - `transfer_mediation` differs
  - `interior_load_carriers` remains the same
  - `channel_geometry` remains the same
  - `boundary_geometry` remains the same
- [x] The diagnosed authorability result is:
  `existing_transfer_mediation_already_authors_descendant_secondary_basin_load_carrier_support_condition`

### Summary

Iteration 49 is complete.

The target condition is already structurally authorable through existing
vocabulary.

More specifically:

- the pre-`settlement_regime` structural path lane already produces the same
  repeating descendant secondary `basin_load_carrier` support condition as the
  later explicit path lane
- the later `settlement_regime` declaration does not introduce the condition;
  it only names and constrains a behavior already authored by existing
  structure
- among the candidate existing families considered here, the decisive
  discriminatory family is `transfer_mediation`
- `interior_load_carriers`, `channel_geometry`, and `boundary_geometry` remain
  background structure in this lane rather than the direct authoring gap

So the Iteration 48 boundary should **not** be promoted into a new
`settlement_regime` field.
The honest closure is:

- inherited secondary `basin_load_carrier` support is a downstream consequence
  of already-authorable `transfer_mediation` structure in this lane
- there is no present translation gap here

### Settlement-Regime Clean Closure

`primitive.extensions.grcv3.settlement_regime` should now be treated as
cleanly closed for the current spindle side-quest.

That means:

- keep the family as the executable language for:
  - `initial_locus_class`
  - `split_inheritance_mode`
- do **not** add a further field for descendant secondary support class
- reopen the family only if a later lane reveals a genuine authoring gap that
  existing structure still cannot express

## Iteration 50. Collapse-Regime Characterization Pass

### Goal

Start the next post-closeout `GRCL-v3` lane with a collapse-side language
audit rather than with another family expansion.

The point is to ask the same source-language question already asked for spark,
split, settlement locus, and reentry:

- what collapse-side distinctions are already authored by the present language
- what collapse behavior is only a downstream consequence of existing
  structure
- and whether collapse exposes a genuine next translation gap

### Checks

- [x] Lock the restart rule for this iteration:
  - [x] keep `transfer_mediation` closed by default
  - [x] keep `settlement_regime` closed by default
  - [x] do not open a new family before the collapse audit is complete
- [x] Choose the primary comparison lanes from the saved spindle evidence with
  direct controls kept explicit
- [x] Record the first observed collapse step for each comparison lane
- [x] Record the collapse source locus for each comparison lane
- [x] Record the collapse sink locus for each comparison lane
- [x] Test whether collapse stays in the same locus family as spark or shifts
  to a different operative locus
- [x] Test whether carrier-site and path-node regimes collapse differently
- [x] Test whether split children participate in later collapse or only in
  spark/reentry
- [x] Conclude whether the collapse-side result is:
  - [x] already authored by existing structure
  - [ ] an extension of an existing family
  - [ ] a genuine new collapse-relevant translation gap

### Implementation Notes

- This iteration is a characterization pass first, not a schema-expansion pass.
- Prefer saved evidence and targeted trace helpers before adding any new rich
  field.
- Keep the forbidden solved-state boundary explicit:
  - traced collapse outcomes are evidence
  - not source truth
- If a new collapse-side distinction is proposed later, the justification must
  state why existing source vocabulary cannot already author it honestly.
- Added the reusable helper:
  - `src/pygrc/telemetry/experiments.py`
    - `build_grcv3_landscape_collapse_regime_trace(...)`
- Added the runnable trace script:
  - `scripts/trace_grcv3_collapse_regimes.py`
- Focused verification landed in:
  - `tests/telemetry/test_experiments.py`
- Selected comparison lanes:
  - direct structural control:
    - `grcv3-rich-v4-mediated-spill-branch-probe.seed.yaml`
  - path structural lane:
    - `grcv3-rich-v4-mediated-spill-branch-single-intermediate-probe.seed.yaml`
  - explicit split-child path regime:
    - `grcv3-rich-v4-path-node-split-child-inheriting-settlement-probe.seed.yaml`
  - explicit split-child direct regime:
    - `grcv3-rich-v4-carrier-site-split-child-inheriting-settlement-probe.seed.yaml`
- Recorded collapse-side result under the shared choice envelope:
  - `choice = sink_compatibility`
  - `epsilon_choice = 0.15`
  - `epsilon_collapse = 0.14`
- Scope guard for this iteration:
  - this is a spindle-lane characterization pass, not a full inventory of every
    collapse-capable `GRCV3` rich seed already recorded elsewhere
  - broader family evidence already includes:
    - the saved rich-v4 spark/split/collapse artifact lane centered on
      `grcv3-rich-v4-transfer-mediation-probe.seed.yaml`
    - the dedicated early-collapse example
      `grcv3-rich-collapse-example.seed.yaml`
- Observed pattern in the `24`-step audit window:
  - both carrier-site direct lanes keep choice activity but do not collapse
  - both path-regime lanes first collapse on step `17`
  - in both path-regime lanes, collapse source locus is `basin_support`
  - in both path-regime lanes, collapse sink locus is `carrier_site`
  - collapse does **not** stay in the same locus family as the first spark
    site:
    - first spark locus: `path_node`
    - first collapse source locus: `basin_support`
  - later split children do not participate in the observed collapse events

### Verification

- [x] The selected comparison lanes include at least one direct control and one
  mediated/path regime lane
- [x] The recorded collapse summaries are aligned to concrete steps/loci rather
  than only visual impressions
- [x] The iteration ends with an explicit planning decision:
  - [x] no new family yet
  - [ ] extend an existing family
  - [ ] open a new collapse-relevant family with a stated source-side gap

### Summary

Iteration 50 is complete.

The collapse-side audit does **not** currently justify a new collapse family.

What it revealed instead is narrower and more useful:

- collapse is regime-sensitive in the current spindle lane
- the path-regime lanes collapse while the matched carrier-site direct controls
  do not collapse in the same audit window
- the observed collapse does not occur at the original spark locus family
  (`path_node`)
- instead, the observed collapse resolves later from `basin_support` sites into
  `carrier_site` sinks
- and split children do not participate in the recorded collapse events

So the current honest read is:

- collapse is presently a downstream support-to-carrier resolution pattern
  in the specific spindle lanes audited here
- that pattern is already separated by existing structure rather than by a new
  collapse-specific source-language gap
- and the next move should still be **no new family yet**, unless a later lane
  shows collapse behavior that existing structural vocabulary still cannot
  author or distinguish honestly

This does **not** mean:

- only one seed can collapse
- or only the path-regime family can ever collapse

It means only that, for the four matched spindle lanes chosen here, the
collapse-side difference is not yet a new source-language gap.

### Broadened Evidence Note

After the narrow spindle audit, the broader recorded collapse-capable lanes were
checked as well:

- `grcv3-rich-collapse-example.seed.yaml`
  - `hot_exploratory`
  - first collapse on step `3`
  - collapse from `basin_support` into `junction_branch`
  - no prior spark
- `grcv3-rich-v4-transfer-mediation-probe.seed.yaml`
  - `seed_baseline`
  - first collapse on step `71`
  - collapse from `basin_center` into `basin_support`
  - collapse happens after spark/split, but not from the same locus family as
    the first spark site
- `grcv3-rich-basin-boundary-channel-probe.seed.yaml`
  - `seed_baseline`
  - first collapse on step `100`
  - collapse from `basin_support` into `ridge_support`
  - no prior spark

So the broadened Iteration 50 result is:

- collapse-capable lanes in the repo are already plural
- but their collapse source/sink patterns are heterogeneous
- and the original collapse questions therefore remain open at the broader
  family level

That still does **not** justify a new family immediately.
It means the next honest collapse follow-on should use controlled comparisons
between these broader lane clusters rather than promoting vocabulary from a
single widened survey pass.

## Iteration 51. Collapse Cluster Decomposition

Purpose:

- compare the two recorded `collapse_without_prior_spark` lanes as one
  controlled collapse cluster
- ask whether their sink difference is already authored by existing structure
  or whether it exposes the first real collapse-side source-language gap

Questions:

- why do both lanes collapse before any prior spark?
- why does one lane collapse from `basin_support` into `junction_branch`
  while the other collapses from `basin_support` into `ridge_support`?
- is that sink difference already explained by existing:
  - realization structure
  - interface structure
  - boundary/channel geometry
  - local neighborhood around the collapsing support site
- or does the pair force a new collapse-relevant family?

Implementation:

- [x] trace the dedicated early-collapse example lane:
  - seed: `grcv3-rich-collapse-example.seed.yaml`
  - profile: `hot_exploratory`
  - primitive: `decision_core`
  - steps: `10`
- [x] trace the basin/boundary/channel comparison lane:
  - seed: `grcv3-rich-basin-boundary-channel-probe.seed.yaml`
  - profile: `seed_baseline`
  - primitive: `core_basin`
  - steps: `160`
- [x] record for both lanes:
  - first choice step
  - first collapse step
  - first collapse source locus
  - first collapse sink locus
  - local neighborhood summary around the collapse source site
- [x] compare the seed-side family payloads most likely to author the sink
  difference:
  - `realization`
  - `local_geometry`
  - `interfaces`
  - `boundary_geometry`
  - `channel_geometry`
- [x] close with an explicit planning decision on whether the sink difference
  requires new collapse vocabulary

### Verification

- [x] both selected lanes are confirmed `collapse_without_prior_spark`
- [x] both selected lanes collapse from the same source locus family
  (`basin_support`)
- [x] the traced sink difference is tied to explicit source-side family and
  neighborhood differences rather than visual inspection alone
- [x] the iteration ends with an explicit planning decision:
  - [x] no new family yet
  - [ ] extend an existing family
  - [ ] open a new collapse-relevant family with a stated source-side gap

### Summary

Iteration 51 is complete.

The controlled pre-spark collapse pair still does **not** justify a new
collapse family.

What the comparison shows is:

- both lanes remain `collapse_without_prior_spark`
- both lanes first detect choice on step `1`
- both lanes first collapse from `basin_support`
- but their sinks diverge under already-different authored structure

The traced pair is:

- `grcv3-rich-collapse-example.seed.yaml`
  - first collapse on step `3`
  - collapse from `basin_support` into `junction_branch`
  - source neighborhood mixes `basin_center`, `basin_support`, and
    `valley_channel`
- `grcv3-rich-basin-boundary-channel-probe.seed.yaml`
  - first collapse on step `100`
  - collapse from `basin_support` into `ridge_support`
  - source neighborhood mixes `basin_center`, `basin_support`, and
    `ridge_support`

The decisive source-side comparison is also already structured:

- `realization` differs
- `local_geometry` differs
- `interfaces` differ
- `boundary_geometry` differs
- `channel_geometry` differs

So the current honest read is:

- the shared pre-spark collapse source family is real
- but the sink difference tracks existing `junction` vs
  `boundary/channel` structure rather than an unexpressed collapse-side gap
- therefore Iteration 51 still closes as **no new collapse family yet**

This narrows the remaining collapse question further:

- the pre-spark collapse cluster now looks structurally explainable
- so the strongest remaining open collapse-side comparison is the post-spark
  cluster represented by the rich-v4 transfer-mediation artifact lane

## Iteration 52. Post-Spark Collapse Boundary

Purpose:

- define the narrowed collapse question left open after Iteration 51
- test whether the recorded rich-v4 post-spark collapse behavior is already
  fully authored by present structure or still exposes a genuine
  collapse-side source-language gap

Target cluster:

- `grcv3-rich-v4-transfer-mediation-probe.seed.yaml`
  - recorded post-spark collapse lane
  - first spark already occurs before collapse
  - first collapse observed from `basin_center` into `basin_support`
- plus one or more controlled comparison lanes that preserve as much of the
  same rich-v4 structure as possible while removing or relocating the observed
  post-spark collapse

Questions:

- what is the first decisive post-spark divergence between the collapsing lane
  and its closest non-collapsing or differently-collapsing control?
- does the later collapse from `basin_center` into `basin_support` track an
  already-authored difference in:
  - `transfer_mediation`
  - `settlement_regime`
  - split/reentry structure
  - local support/carrier neighborhood
  - existing geometry/interface families
- or is there a residual post-spark collapse distinction that current source
  structure still cannot state honestly?

Planned checks:

- [x] choose the richest controlled comparison lane or lane set around
  `grcv3-rich-v4-transfer-mediation-probe.seed.yaml`
- [x] trace first spark, first split, and first collapse steps
  across that controlled pair/set
- [x] record the first collapse source/sink summaries and local neighborhood
  around the collapsing source site
- [x] compare seed-side payload differences with priority on:
  - [x] `transfer_mediation`
  - [ ] `settlement_regime`
  - [x] `interfaces`
  - [x] `boundary_geometry`
  - [x] `channel_geometry`
- [x] close with an explicit planning decision:
  - [x] no new family yet
  - [ ] extend an existing family
  - [ ] open a new post-spark collapse family with a stated source-side gap

### Summary

Iteration 52 is complete.

The narrowed post-spark collapse question also closes as **no new family yet**.

The tightest controlled comparison around the saved rich-v4 artifact lane is:

- baseline:
  - `grcv3-rich-v4-transfer-mediation-probe.seed.yaml`
- blocked direct control:
  - `grcv3-rich-v4-center-coupling-probe.seed.yaml`
- refined direct control:
  - `grcv3-rich-v4-asymmetric-center-coupling-probe.seed.yaml`

What the trace shows is:

- all three lanes first detect choice on step `1`
- the baseline and refined lanes first spark on step `6` at the same
  `carrier_site` locus
- the blocked control first sparks much later on step `99` at a
  `basin_support` locus
- the baseline lane first splits on step `7` and first collapses on step `71`
  from `left_reservoir::center` into `left_reservoir::support:2`
- the refined control first splits on step `7` and first collapses on step
  `72` with the same `basin_center -> basin_support` source/sink pattern
- the blocked control first collapses on step `99` from
  `spindle_core::carrier:0` into `upper_clamp::ridge_support:0`, and only
  then completes its first split on step `100`

The local collapse neighborhoods also separate cleanly:

- baseline and refined collapse from a `basin_center` whose neighbors are only
  `basin_support`
- the blocked control collapses from a `carrier_site` whose neighbors are
  `ridge_support` and `split_child`

Most importantly, the seed-side comparison is already narrow:

- baseline vs blocked differs in `transfer_mediation`
- baseline vs refined differs in `transfer_mediation`
- `interfaces`, `boundary_geometry`, `channel_geometry`,
  `interior_load_carriers`, and `local_geometry` stay the same across those
  comparisons

So the current honest read is:

- the post-spark collapse boundary is already authored inside existing
  `transfer_mediation`
- specifically, the decisive source-side lever here is
  `transfer_mediation.center_coupling_classes`
- no new post-spark collapse family is justified by the current evidence

## Iteration 53. Late-Window Post-Spark Stability Check

Purpose:

- widen the Iteration 52 post-spark trio to `150` steps
- test whether the blocked direct control stays distinct after its late
  step-`99/100` events or eventually converges into the same collapse pattern
  seen in the baseline and refined lanes

Implementation:

- [x] rerun the same post-spark trio used in Iteration 52 at `150` steps:
  - `grcv3-rich-v4-transfer-mediation-probe.seed.yaml`
  - `grcv3-rich-v4-center-coupling-probe.seed.yaml`
  - `grcv3-rich-v4-asymmetric-center-coupling-probe.seed.yaml`
- [x] record post-`100` collapse counts and first late-window collapse records
  for each lane
- [x] record the first post-`100` collapse that matches the baseline
  `basin_center -> basin_support` pattern
- [x] decide whether the blocked control remains distinct through `150` or only
  partially converges later

### Summary

Iteration 53 is complete.

The widened late-window run changes the practical read of Iteration 52:

- the blocked control does **not** stay cleanly distinct through `150`
- but it also does **not** simply behave like the baseline/refined lanes once
  the late window opens

The widened trace shows:

- baseline:
  - first collapse on step `71`
  - one post-`100` collapse on step `116`
  - that late collapse is again `basin_center -> basin_support`
- refined:
  - first collapse on step `72`
  - one post-`100` collapse on step `117`
  - that late collapse is again `basin_center -> basin_support`
- blocked control:
  - first collapse on step `99` as `carrier_site -> ridge_support`
  - first split complete on step `100`
  - five post-`100` collapse records
  - first post-`100` collapse on step `101` as `carrier_site -> split_child`
  - later post-`100` collapse records still include `split_child -> split_child`
  - only on step `121` does it first reach the baseline-style
    `basin_center -> basin_support` pattern

So the widened honest read is:

- the blocked control eventually reaches the same broad collapse pattern family
  as the baseline/refined lanes
- but only after a distinct late carrier/split-child cascade
- therefore the post-spark collapse question is still **not** a new family
  question
- but the collapse-side interpretation is also **not yet fully closed**

What remains open after Iteration 53 is narrower:

- not whether a new collapse family is needed
- but why the blocked center-coupling control delays convergence behind that
  distinct late cascade before eventually reaching the same
  `basin_center -> basin_support` regime

## Iteration 54. Late-Cascade Delay Authorability

Purpose:

- decide whether the blocked lane’s late carrier/split-child cascade is already
  authored by existing source structure
- close the remaining post-spark collapse interpretation question without
  opening a new family unnecessarily

Implementation:

- [x] compare the matched direct controls:
  - `grcv3-rich-v4-center-coupling-probe.seed.yaml`
  - `grcv3-rich-v4-asymmetric-center-coupling-probe.seed.yaml`
- [x] reuse the widened `150`-step late-window collapse trace
- [x] compare seed-side payloads across:
  - `transfer_mediation`
  - `interfaces`
  - `boundary_geometry`
  - `channel_geometry`
  - `interior_load_carriers`
  - `local_geometry`
- [x] close with an explicit authorability decision on whether the late delay
  already fits inside existing `transfer_mediation`

### Summary

Iteration 54 is complete.

The remaining late-cascade question also closes as **already authored by
existing structure**.

The decisive comparison is now very narrow:

- blocked direct control:
  - `grcv3-rich-v4-center-coupling-probe.seed.yaml`
  - `center_coupling_classes = [[north, blocked], [south, blocked]]`
- refined direct control:
  - `grcv3-rich-v4-asymmetric-center-coupling-probe.seed.yaml`
  - `center_coupling_classes = [[north, strong], [south, weak]]`

Everything else relevant in the matched direct controls stays the same:

- `interfaces`
- `boundary_geometry`
- `channel_geometry`
- `interior_load_carriers`
- `local_geometry`

And the late-window behavior separates exactly where those center-coupling
classes separate:

- the blocked control shows a distinct late cascade before convergence:
  - post-`100` carrier-site into split-child collapse
  - additional split-child collapses
  - only later reaches `basin_center -> basin_support`
- the refined control does **not** show that distinct pre-convergence cascade
  before reaching the shared late collapse pattern

So the current honest read is:

- the blocked lane’s delay is already authored inside existing
  `transfer_mediation`
- more specifically, it is already separable by
  `transfer_mediation.center_coupling_classes`
- no new collapse family is needed for this delayed-convergence behavior

This means the collapse-side arc is now materially closed at the family level:

- collapse remains plural and runtime-rich
- but the currently investigated distinctions all close inside existing
  structure
- no new collapse-side source family is justified by Iterations 50 through 54

## Iteration 55. Geometry-Mediated Post-Collapse Exclusion

Purpose:

- ask the stricter phenomenology question raised after Iteration 54:
  - not whether runtime rules can forbid reentry
  - but how geometry shifts preference away from the initial collapsed sink
- test whether that geometric reroute is already authored by existing source
  structure

Implementation:

- [x] compare the blocked and refined direct controls only:
  - `grcv3-rich-v4-center-coupling-probe.seed.yaml`
  - `grcv3-rich-v4-asymmetric-center-coupling-probe.seed.yaml`
- [x] enrich collapse records with per-event source/sink neighborhood summaries
- [x] trace three blocked-lane moments:
  - initial collapse into `ridge_support`
  - first reroute into `split_child`
  - first later shared-pattern collapse into `basin_support`
- [x] compare those moments against the refined lane and against the matched
  source-side family payloads

### Summary

Iteration 55 is complete.

The geometry phenomenology also closes inside existing structure.

What the blocked lane now shows explicitly is a sink reroute sequence:

- initial collapse:
  - `carrier_site -> ridge_support`
- first reroute after the initial collapse step:
  - `carrier_site -> split_child`
- later shared-pattern collapse:
  - `basin_center -> basin_support`

The relevant local geometry changes across that reroute:

- at the initial blocked collapse, the source carrier sees
  `basin_support`, `ridge_support`, and `split_child`
- at the first reroute into `split_child`, the source carrier now sees
  `split_child` and `valley_channel`
- by the later shared-pattern collapse, the source basin center sees only
  `basin_support`

So the observed “anti-reentry” is not a hard prohibition.
It is a geometric preference shift:

- the blocked lane does not keep collapsing back into the original
  `ridge_support` sink after the first collapse
- instead, local connectivity and neighbor roles reroute the collapse path
  first through `split_child`
- and only later into the shared `basin_support` regime

The matched-control authorability check stays narrow:

- blocked vs refined still differs only in `transfer_mediation`
- more specifically in `transfer_mediation.center_coupling_classes`
- while `interfaces`, `boundary_geometry`, `channel_geometry`,
  `interior_load_carriers`, and `local_geometry` remain the same

So the current honest read is:

- geometry-mediated shift away from the initially chosen sink is already
  authorable in existing source structure
- no explicit anti-reentry rule is needed to explain the current phenomenon
- and no new collapse-side family is justified by this stronger phenomenology

### Closure Record

Collapse exploration is now complete for the current `GRCL-v3` discovery arc.

- [x] record the collapse-side family search as closed after Iterations 50
  through 55
- [x] record that the current evidence supports only existing-family
  explanations:
  - plural collapse-capable lanes
  - post-spark and pre-spark variation
  - geometry-mediated rerouting away from an initial collapsed sink
- [x] record that no new collapse-side source family is justified by the
  present evidence bundle
- [x] leave any future collapse work in the category of artifact maintenance or
  later runtime interpretation, not immediate family discovery

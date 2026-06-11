# GRCL-v3 Family-Native Lowering Refactor Checklist

This document tracks execution of the `GRCL-v3` family-native lowering
refactor.

It is intentionally separate from:

- [GRCL-V3-ImplementationChecklist.md](./GRCL-V3-ImplementationChecklist.md)

because that earlier checklist established:

- the first rich-seed lane,
- the `grcv3.rich.v1` and `grcv3.rich.v2` schema surface,
- the first honest sparkability gates,
- and the evidence that richer source semantics now justify an architectural
  path split

This checklist starts **after** that proof.

Its purpose is not to broaden rich vocabulary further.
Its purpose is to migrate `grcv3.rich.v2+` from:

- weaker-blueprint semantic dependence

to:

- family-native lowering with common seed parsing only

as defined in:

- [GRCL-V3-LoweringArchitectureDecision.md](./GRCL-V3-LoweringArchitectureDecision.md)
- [GRCL-V3-FamilyNativeLoweringRefactorPlan.md](./GRCL-V3-FamilyNativeLoweringRefactorPlan.md)

## Usage Rules

- Do not change `GRCV3` runtime equations as part of this checklist.
- Do not relax spark thresholds to compensate for projector refactoring.
- Keep weaker-schema compatibility visible at every iteration.
- Treat `grcv3.rich.v2+` semantic dependence on `GRCV2LandscapeBlueprint` as
  technical debt to be removed deliberately, not gradually forgotten.
- Record all remaining temporary compatibility bridges explicitly.
- If a step requires temporary code reuse from the old blueprint path, record
  whether that reuse is:
  - implementation-only reuse
  - or still semantic dependence
- The target is not “different code.” The target is:
  - explicit two-lane lowering architecture
  - with `grcv3.rich.v2+` no longer semantically defined through the weaker
    blueprint

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

Create the dedicated refactor checklist and bind it to the architecture
decision and refactor plan.

### Checks

- [x] Create `GRCL-V3-FamilyNativeLoweringRefactorChecklist.md`
- [x] Link this checklist from the top-level implementation index
- [x] Link this checklist from the `GRCL-v3` refactor plan and active
  implementation notes
- [x] Record that this checklist begins only after the first rich-seed lane
  proved the need for a path split

### Implementation Notes

- This checklist is a migration lane, not a schema-expansion lane.
- The core architectural split must remain visible throughout:
  - compatibility path for weaker schemas
  - family-native lowering path for `grcv3.rich.v2+`

### Verification

- [x] The checklist exists under `implementation/`
- [x] The checklist is discoverable from the active `GRCL-v3` docs
- [x] The scope is explicitly architectural rather than vocabulary-facing

### Summary

Closed. The refactor lane now has its own execution tracker, linked from the
main implementation phase index and the `GRCL-v3` plan/checklist documents.
This checklist starts after rich-seed viability was already proven and is
scoped only to the lowering-architecture split.

## Iteration 1. Explicit Path Dispatcher

### Goal

Create an explicit two-lane lowering dispatcher in `grc_v3_landscape.py`.

### Checks

- [x] Add explicit lowering-lane selection for:
  - neutral/common seeds
  - `grcv3.rich.v1`
  - `grcv3.rich.v2+`
- [x] Record the chosen path in cached diagnostics / snapshot-visible metadata
- [x] Keep weaker seeds on the compatibility path by design
- [x] Keep `grcv3.rich.v2+` on the native path by design

### Implementation Notes

- This iteration is about path authority, not primitive migration yet.
- It should become impossible for a `grcv3.rich.v2+` seed to “accidentally”
  take the old path without that being visible.
- Implemented via explicit lane constants and selection helpers in
  `src/pygrc/models/grc_v3_landscape_native.py`, then threaded through
  `_resolve_grcv3_lowering_context(...)` in
  `src/pygrc/models/grc_v3_landscape.py`.
- Cached diagnostics now record:
  - `landscape_lowering_lane`
  - `landscape_lowering_semantic_authority`
  - `landscape_compatibility_blueprint_usage`
  - `landscape_grcv3_native_surface_summary`
- The current lane split is:
  - common / neutral seeds -> `compatibility`
  - `grcv3.rich.v1` -> `compatibility`
  - `grcv3.rich.v2+` -> `family_native`

### Verification

- [x] Path selection is explicit in code, not inferred indirectly
- [x] Diagnostics expose which lane was used
- [x] Existing weaker-lane tests still pass

Verification commands:

- `./.venv/bin/python -m unittest tests.models.test_grc_v3_landscape_runtime`
- `./.venv/bin/python -m unittest tests.landscapes.test_grcv3_extensions tests.models.test_grc_v3_landscape_runtime`

### Summary

Closed. Lane selection is now explicit and artifact-visible. Common seeds and
`grcv3.rich.v1` remain on the interpretive compatibility path, while
`grcv3.rich.v2+` is forced onto a family-native lane with separate diagnostics.

## Iteration 2. Native Primitive Input Surface

### Goal

Define the direct primitive input surface for the family-native lane.

### Checks

- [x] Define native lowering helpers that consume direct seed primitives rather
  than `GRCV2LandscapeBlueprint`
- [x] Decide the helper/module split for:
  - basin / plateau
  - junction / saddle
  - valley
  - ridge
- [x] Record which old helper functions may still be reused purely as
  implementation utilities
- [x] Record which old helper functions are no longer allowed to remain
  semantically authoritative for `grcv3.rich.v2+`

### Implementation Notes

- This iteration should lock the migration boundary before detailed code moves.
- Temporary code reuse is allowed, but semantic authority must be direct from:
  - primitive fields
  - `extensions.grcv3`
- Implemented `GRCV3NativePrimitiveSurface` in
  `src/pygrc/models/grc_v3_landscape_native.py` as the direct primitive-facing
  boundary for the native lane.
- The surface currently records:
  - rich contract version
  - primitive index
  - primitive IDs grouped by source type
  - junction-like primitive IDs
  - rich-extended primitive IDs
  - temporary blueprint-only utility functions
  - prohibited blueprint semantic authorities
- Temporary blueprint implementation reuse currently remains limited to utility
  helpers such as:
  - `_edge_weight_from_blueprint`
  - `_euclidean_length`
  - `_freeze_optional_mapping`
  - `_transport_intent_metadata`
- The following are now explicitly prohibited from remaining semantically
  authoritative for `grcv3.rich.v2+`:
  - `GRCV2LandscapeBlueprint`
  - `realize_grcv2_landscape_blueprint`

### Verification

- [x] The native surface is defined in code-facing terms
- [x] The allowed temporary reuse boundary is written down explicitly
- [x] No new semantic dependence on the weaker blueprint is introduced

Verification commands:

- `./.venv/bin/python -m unittest tests.models.test_grc_v3_landscape_runtime`
- `./.venv/bin/python -m unittest tests.landscapes.test_grcv3_extensions tests.models.test_grc_v3_landscape_runtime`

### Summary

Closed. The family-native lane now has an explicit direct-primitive input
surface and a written implementation-utility boundary. `grcv3.rich.v2+` still
uses the old blueprint only as a temporary bridge for runtime assembly, not as
semantic authority.

## Iteration 3. Native Basin / Plateau Lowering

### Goal

Move basin/plateau lowering for `grcv3.rich.v2+` onto the family-native lane.

### Checks

- [x] Lower basin-local geometry directly from seed primitives and
  `extensions.grcv3`
- [x] Lower plateau hosting/containment directly from seed primitives and
  `extensions.grcv3` where applicable
- [x] Preserve direct role-node realization for declared local axes
- [x] Record approximation notes for any constructive discretization choices

### Implementation Notes

- This iteration should remove semantic dependence on weaker blueprint basin
  semantics for the native lane.
- Discretization choices remain allowed, but they must be traceable to source
  meaning or explicit lowering policy.
- Added direct family-native basin/plateau plans to
  `src/pygrc/models/grc_v3_landscape_native.py` and switched the native lane to
  consume those plans rather than `GRCV2LandscapeNodeBlueprint` meaning.
- Native basin/plateau lowering now uses:
  - direct `coherence_prior`
  - direct `depth_hint`
  - direct `chart_center_hint` / `chart_scale_hint`
  - direct `local_geometry.axis_roles`
  - direct curvature and attachment metadata from `extensions.grcv3`
- Plateaus on the native lane now realize the same direct role-node surface as
  basins when rich local geometry is declared, while containment remains
  attached to the semantic anchor node through `contained_primitive_ids` and
  `contained_node_ids`.
- The constructive discretization remains explicit:
  - declared local axes are lowered as a deterministic support ring
  - the ring is a constitutive sampling choice, not a claim of exact metric
    reconstruction

### Verification

- [x] Native basin/plateau lowering no longer requires weaker semantic
  blueprint meaning
- [x] Role-node diagnostics remain inspectable
- [x] Compatibility path remains unchanged for weaker schemas

Verification commands:

- `./.venv/bin/python -m unittest tests.models.test_grc_v3_landscape_runtime`
- `./.venv/bin/python -m unittest tests.landscapes.test_grcv3_extensions tests.models.test_grc_v3_landscape_runtime`

### Summary

Closed. Basin/plateau meaning for `grcv3.rich.v2+` is now lowered directly
from the seed and `extensions.grcv3`, with direct role-node realization and
plateau containment preserved on the native lane. The compatibility lane
remains unchanged.

## Iteration 4. Native Junction / Saddle Lowering

### Goal

Move junction/saddle lowering for `grcv3.rich.v2+` onto the family-native lane.

### Checks

- [x] Lower explicit branch order, branch targets, and local-role semantics
  directly from the rich seed
- [x] Preserve hostless/hosted routing semantics on the native lane
- [x] Keep `grcv3.rich.v1` on the compatibility lane unless explicitly
  promoted later
- [x] Record any remaining temporary helper reuse from the old path

### Implementation Notes

- Junction/saddle lowering is the clearest place where weaker-blueprint
  dependence must stop being semantically authoritative.
- This iteration should keep the current rich-junction tests meaningful but
  reinterpret them under the native lane.
- Added direct family-native junction plans carrying:
  - host/hostless status
  - branch order
  - branch targets
  - support count / radius scale
  - local weak-axis semantics
- Native junction lowering now builds branch-node motifs directly from the rich
  seed rather than reconstructing junction meaning from valley adjacency.
- `grcv3.rich.v1` intentionally remains on the compatibility lane, and the
  existing `rich.v1` junction tests now explicitly prove that it still uses the
  weaker semantic path.
- Temporary old-path reuse remains limited to implementation utilities such as
  edge-weight bootstrap and edge directionality labels, not branch semantics.

### Verification

- [x] Native junction/saddle lowering is driven directly by source-rich fields
- [x] `grcv3.rich.v1` compatibility remains intact
- [x] Path diagnostics prove the lanes are distinct

Verification commands:

- `./.venv/bin/python -m unittest tests.models.test_grc_v3_landscape_runtime`
- `./.venv/bin/python -m unittest tests.landscapes.test_grcv3_extensions tests.models.test_grc_v3_landscape_runtime`

### Summary

Closed. Junction/saddle meaning for `grcv3.rich.v2+` now lowers from direct
branch-order and branch-target source fields, while `grcv3.rich.v1` remains on
the compatibility lane by design and continues to pass its existing tests.

## Iteration 5. Native Valley Lowering

### Goal

Move channel/valley lowering for `grcv3.rich.v2+` onto the family-native lane.

### Checks

- [x] Lower channel geometry directly from seed valley primitives and
  `channel_geometry`
- [x] Preserve direct endpoint attachment from preferred sites / local roles
- [x] Keep channel interior sampling deterministic and documented
- [x] Record approximation notes where waypoint policies imply discrete choices

### Implementation Notes

- This iteration should remove weaker-blueprint semantic dependence for
  `grcv3.rich.v2+` valley/channel meaning.
- The native lane should still produce inspectable attachment diagnostics.
- Added direct family-native valley plans carrying:
  - direct endpoints
  - waypoints
  - channel role
  - `channel_geometry`
  - preferred attachment sites
- Native channel-node sampling now consumes direct waypoint sequences and the
  typed `channel_geometry` contract. `midpoint_only` remains a deterministic
  constructive approximation rather than a hidden heuristic.
- Endpoint attachment on the native lane now resolves in this order:
  - explicit junction branch target
  - preferred attachment site
  - entry/exit role from `channel_geometry`
  - geometric fallback

### Verification

- [x] Native valley lowering uses source-declared roles without weaker
  semantic reconstruction
- [x] Attachment diagnostics remain explicit
- [x] Weaker-lane channel tests remain green

Verification commands:

- `./.venv/bin/python -m unittest tests.models.test_grc_v3_landscape_runtime`
- `./.venv/bin/python -m unittest tests.landscapes.test_grcv3_extensions tests.models.test_grc_v3_landscape_runtime`

### Summary

Closed. Valley/channel lowering for `grcv3.rich.v2+` now uses direct source
channel semantics and deterministic waypoint policies on the native lane, while
compatibility-lane channel behavior remains green.

## Iteration 6. Native Ridge Lowering

### Goal

Move ridge/boundary lowering for `grcv3.rich.v2+` onto the family-native lane.

### Checks

- [x] Lower boundary support structure directly from ridge primitives and
  `boundary_geometry`
- [x] Preserve direct normal/tangent / attachment semantics from the source
- [x] Keep constructive arc/stencil realization deterministic
- [x] Record any remaining compatibility-only ridge behavior for weaker schemas

### Implementation Notes

- This iteration should make the native lane authoritative for rich boundary
  semantics while leaving weaker ridge lanes intact.
- Added direct family-native ridge plans carrying:
  - owner/adjacent relationships
  - ridge kind and coherence hints
  - `boundary_geometry`
  - boundary-role / preferred-attachment metadata
- Native ridge lowering now samples support nodes directly from the source
  normal/tangent roles instead of treating the weaker edge blueprint as the
  semantic source.
- Compatibility-only ridge behavior remains explicit:
  - metadata-only ridges with no adjacent structure still do not realize a
    support arc on the native lane at this stage
  - old-path utility reuse remains limited to weight/bootstrap helpers

### Verification

- [x] Native ridge lowering no longer depends semantically on weaker blueprint
  ridge meaning
- [x] Boundary diagnostics remain inspectable
- [x] Compatibility behavior for weaker seeds is preserved

Verification commands:

- `./.venv/bin/python -m unittest tests.models.test_grc_v3_landscape_runtime`
- `./.venv/bin/python -m unittest tests.landscapes.test_grcv3_extensions tests.models.test_grc_v3_landscape_runtime`

### Summary

Closed. Ridge/boundary meaning for `grcv3.rich.v2+` now lowers from direct
boundary geometry and attachment semantics on the native lane, with the
remaining metadata-only ridge limitation recorded explicitly.

## Iteration 7. Native Topology Assembly And Budget Closure

### Goal

Move topology assembly and initial state construction fully into the
family-native lane.

### Checks

- [x] Assemble native-lane node/edge topology without semantic dependence on
  `GRCV2LandscapeBlueprint`
- [x] Keep budget scaling / mass distribution explicit and deterministic
- [x] Keep initial edge conductance/bootstrap labels explicit
- [x] Record path-specific lowering notes in cached diagnostics

### Implementation Notes

- This iteration is where “native lowering” becomes real in runtime state
  construction, not just in primitive-local helpers.
- Diagnostics should make the chosen path and remaining approximations explicit.
- The native lane now constructs its own runtime assembly carrier via
  `_build_native_runtime_blueprint(...)` from `GRCV3NativePrimitiveSurface`
  instead of calling `realize_grcv2_landscape_blueprint(...)`.
- Native runtime assembly now uses:
  - `node_carrier_ids`
  - `edge_carrier_ids`
  - direct basin/junction/valley/ridge plans
  - native ridge ownership / metadata-only ridge diagnostics
- Budget closure remains unchanged in form but is now driven by native-lane
  node specs and native carrier ordering, not the older `GRCV2` projector.
- Initial edge conductance/bootstrap rules are now explicit on the native lane:
  - basin/plateau patch edges use deterministic spoke/ring weights
  - valley edges use `_native_edge_weight_from_valley_plan(...)`
  - ridge edges use `_native_edge_weight_from_ridge_plan(...)`
- The native lane still uses some shared assembly carriers/utilities:
  - `GRCV2LandscapeNodeBlueprint`
  - `GRCV2LandscapeEdgeBlueprint`
  - `GRCV2LandscapeBlueprint`
  These are now implementation carriers only for runtime assembly, not the
  source of rich-lane semantics.

### Verification

- [x] Native-lane topology assembly is executable end to end
- [x] Budget closure still holds exactly
- [x] Diagnostics expose path and approximation choices

Verification commands:

- `./.venv/bin/python -m unittest tests.models.test_grc_v3_landscape_runtime`
- `./.venv/bin/python -m unittest tests.landscapes.test_grcv3_extensions tests.models.test_grc_v3_landscape_runtime`

### Summary

Closed. The native lane now assembles runnable topology and initial state from
its own family-native carrier set and no longer calls the old `GRCV2`
landscape projector. Remaining shared `GRCV2Landscape*` dataclass usage is now
implementation-only carrier reuse and should be evaluated as final technical
debt during Iterations 8–10.

## Iteration 8. Compatibility Lane Regression

### Goal

Prove the interpretive compatibility path still works for weaker schemas.

### Checks

- [x] Verify neutral/common seeds still take the compatibility path
- [x] Verify `grcv3.rich.v1` still takes the compatibility path
- [x] Verify path-specific diagnostics/snapshots remain stable
- [x] Record any intentional compatibility limitations explicitly

### Implementation Notes

- This iteration is about preserving weaker-lane behavior while the native lane
  grows.
- If anything breaks here, stop and document it before moving on.
- The compatibility lane remains intentionally interpretive:
  - neutral/common seeds still lower through
    `realize_grcv2_landscape_blueprint(...)`
  - `grcv3.rich.v1` also remains on that path by design
  - compatibility artifacts therefore continue to expose
    `landscape_runtime_assembly_mode="compatibility_blueprint"`
    and
    `landscape_compatibility_blueprint_usage="authoritative_semantic_intermediate"`
- Runtime regression coverage now includes an explicit guard that the
  compatibility lane still calls the old projector, while the native lane does
  not.
- Intentional limitation recorded:
  - weaker schemas continue to accept interpretive enrichment and therefore do
    not yet provide family-native topology authority

### Verification

- [x] Existing weaker-lane tests remain green
- [x] Path selection matches the architecture decision
- [x] Compatibility limits are explicit, not accidental

Verification commands:

- `./.venv/bin/python -m unittest tests.models.test_grc_v3_landscape_runtime`
- `./.venv/bin/python -m unittest tests.landscapes.test_grcv3_extensions tests.models.test_grc_v3_landscape_runtime`

### Summary

Closed. Neutral/common seeds and `grcv3.rich.v1` still take the compatibility
lane, the path selection is now asserted directly in runtime tests, and the
remaining interpretive behavior of weaker schemas is explicit rather than an
accidental side effect of the refactor.

## Iteration 9. Native Lane Regression And Determinism

### Goal

Prove the family-native lane is stable, deterministic, and distinct.

### Checks

- [x] Verify `grcv3.rich.v2+` seeds take the native lane
- [x] Verify direct lowering tests pass for all migrated primitive families
- [x] Verify deterministic snapshot / digest behavior on the native lane
- [x] Verify native-lane diagnostics do not silently depend on compatibility
  artifacts

### Implementation Notes

- The success criterion is not just “tests pass.” It is:
  - the native lane is visibly different in architecture
  - while still reproducible and inspectable
- Native-lane regression coverage now asserts all of the following:
  - `grcv3.rich.v2+` lowers through `family_native`
  - runtime artifacts expose
    `landscape_runtime_assembly_mode="native_runtime_blueprint"`
  - native diagnostics mark blueprint usage as
    `implementation_carrier_reuse_only`
  - patching `realize_grcv2_landscape_blueprint(...)` to raise does not break
    the native lane
  - repeated native runs with the same seed and params produce identical
    snapshots/digests
- The native lane remains inspectable through:
  - `landscape_runtime_assembly_summary`
  - `landscape_node_ids_by_primitive_id`
  - `landscape_support_node_ids_by_primitive_id`
  - `landscape_edge_ids_by_primitive_id`

### Verification

- [x] Native-lane tests pass
- [x] Snapshot determinism holds
- [x] The two-lane architecture is observable from artifacts/diagnostics

Verification commands:

- `./.venv/bin/python -m unittest tests.models.test_grc_v3_landscape_runtime`
- `./.venv/bin/python -m unittest tests.landscapes.test_grcv3_extensions tests.models.test_grc_v3_landscape_runtime`

### Summary

Closed. `grcv3.rich.v2+` now behaves as a real native lane: it is selected by
contract version, executes without calling the old projector, remains
deterministic for fixed seed/params, and exposes enough diagnostics to make the
two-lane architecture visible from artifacts rather than inferred from code.

## Iteration 10. Boundary Closeout

### Goal

Record what technical debt remains and whether the semantic boundary has been
met.

### Checks

- [x] Verify whether any semantic dependence on `GRCV2LandscapeBlueprint`
  remains for `grcv3.rich.v2+`
- [x] Classify any remaining old-path code reuse as:
  - implementation utility only
  - or unresolved semantic dependence
- [x] Record the remaining debt explicitly
- [x] Record whether the family-native lowering boundary is now satisfied

### Implementation Notes

- The closeout should be strict.
- If semantic dependence remains, document it precisely instead of calling the
  refactor “done.”
- Strict closeout result:
  - `grcv3.rich.v2+` no longer depends semantically on
    `GRCV2LandscapeBlueprint`
  - direct seed parsing plus family-native lowering plans are now the
    authoritative semantic surface
  - remaining `GRCV2Landscape*` reuse is implementation-carrier reuse inside
    runtime assembly only
- Remaining old-path reuse is classified as follows.
  Implementation utility only:
  - `GRCV2LandscapeNodeBlueprint`
  - `GRCV2LandscapeEdgeBlueprint`
  - `GRCV2LandscapeBlueprint`
  - `_euclidean_length(...)`
  - `_freeze_optional_mapping(...)`
  - `_to_plain_data(...)`
  - `_transport_intent_metadata(...)`
  Compatibility-lane-only semantic authority:
  - `realize_grcv2_landscape_blueprint(...)`
  - `_edge_weight_from_blueprint(...)`
  - `_edge_directionality_semantics(...)`
  - `_required_node_mass(...)` when reconstructing compatibility-lane runtime
    carriers
- Naming debt kept intentionally for continuity:
  - `landscape_compatibility_blueprint_usage` remains the field name even when
    the native value is `implementation_carrier_reuse_only`
  - `landscape_blueprint_summary` remains available for compatibility with
    existing artifact readers, while `landscape_runtime_assembly_summary` is
    the clearer boundary-facing diagnostic
- Boundary verdict:
  - semantic boundary satisfied
  - implementation-carrier cleanup remains optional future debt, not a blocker
    for native lowering correctness

### Verification

- [x] The remaining debt list is explicit
- [x] The semantic-boundary decision is explicit
- [x] The outcome is actionable, not implied

Verification commands:

- `./.venv/bin/python -m unittest tests.models.test_grc_v3_landscape_runtime`
- `./.venv/bin/python -m unittest tests.landscapes.test_grcv3_extensions tests.models.test_grc_v3_landscape_runtime`

### Summary

Closed. The refactor boundary is now satisfied: `grcv3.rich.v2+` lowers through
family-native semantics, the compatibility lane remains isolated and explicit,
and the only remaining overlap with `GRCV2` is documented implementation-carrier
reuse plus compatibility-path support. There are no unresolved semantic loose
ends left from the refactor.

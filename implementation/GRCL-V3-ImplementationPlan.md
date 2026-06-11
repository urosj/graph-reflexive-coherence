# GRCL-v3 Implementation Plan

## Purpose

This document defines the next implementation lane after the Phase 5
`GRCV3` landscape-projector diagnostic boundary.

Its purpose is not to replace the family-neutral/common `GRCL` seed layer.
Its purpose is to define how `PyGRC` should add a **`GRCV3`-rich seed
capability** when the shared seed layer is no longer expressive enough to
preserve the geometry that `GRCV3` actually needs.

This matters because a high-level language is only useful if its distinctions
can be translated into the raw geometric and constitutive structure that
actually drives `GRCV3` behavior.
`GRCL-v3` is therefore not just a naming scheme layered on top of runtime.
It is a source-side language for authoring, constraining, and studying the
structural conditions under which particular raw-geometry phenomenology can or
cannot emerge.

The governing decision is:

- if a **small `GRCV3`-rich seed** can preserve and realize sparkable local
  geometry through the normal seed-driven path,
- then the project should proceed to **full `GRCL-v3` capability** rather than
  treating that rich seed as a one-off probe.

## 1. Why This Is The Right Next Step

This plan follows directly from the evidence recorded in:

- [GRCV3-RichSeed-Rationale.md](./GRCV3-RichSeed-Rationale.md)
- [GRCV3-Landscape-ProjectorProposal.md](./GRCV3-Landscape-ProjectorProposal.md)
- [GRCL-V3-Vocabulary.md](./GRCL-V3-Vocabulary.md)
- [GRCL-V3-LoweringArchitectureDecision.md](./GRCL-V3-LoweringArchitectureDecision.md)
- [GRCL-V3-FamilyNativeLoweringRefactorPlan.md](./GRCL-V3-FamilyNativeLoweringRefactorPlan.md)

The current state is:

1. manual `GRCV3` spark states work
2. richer family-local projection from neutral/common `GRCL` improves topology
   but does not recover sparkable local geometry reliably
3. richer neutral/common probes still fail to induce the needed weak-axis
   structure

So the next open question is no longer:

- “can the neutral/common projector be tuned a little more?”

It is:

- “can a documented `GRCV3`-rich seed surface preserve the geometry-bearing
  information that the neutral/common seed intentionally does not encode?”

That makes a dedicated `GRCL-v3` plan the right next artifact.

## 2. Core Decision

`GRCL-v3` should be developed as a **family-specific extension surface** built
on top of the existing neutral/common seed schema.

It should **not**:

- fork the neutral/common seed schema,
- replace `GRCL` as the shared cross-family layer,
- or inject solved runtime state into the source seed.

It **should**:

- live under the existing extension policy already allowed by
  [LandscapeSeedSchema.md](./LandscapeSeedSchema.md),
- use `extensions.grcv3` at top-level and primitive-level,
- preserve geometry-bearing source intent that is specific to `GRCV3`,
- and let the `GRCV3` landscape projector act as a deterministic lowerer of
  rich source structure rather than a heuristic guesser.

## 2.1 Recorded Architecture Decision

The current architecture target is explicitly recorded in:

- [GRCL-V3-LoweringArchitectureDecision.md](./GRCL-V3-LoweringArchitectureDecision.md)

The short form is:

- weaker schemas may continue to use an interpretation-heavy projector path
- `grcv3.rich.v1` remains a transitional compatibility/probe lane
- `grcv3.rich.v2+` should move toward family-native lowering with common seed
  parsing only
- once the rich contract is strong enough (`grcv3.rich.v3+` or later), the
  preferred boundary should move further toward direct family-native assembly
  rather than projector-style semantic interpretation

This now has a stricter next-step consequence:

- `grcv3.rich.v4` is justified only if it is specified and implemented as
  direct translation from explicit source semantics into `GRCV3`
  family-native assembly
- if a proposed `rich.v4` slice still relies on projector-style semantic
  lowering or heuristic projection, it should be rejected as the wrong next
  step

This does **not** eliminate constructive discretization.
It means explicit `GRCV3` source semantics should stop being semantically
flattened through the weaker `GRCV2` blueprint as the long-term target shape.

## 2.2 Recorded Refactor Direction

The concrete migration plan for that architecture is recorded in:

- [GRCL-V3-FamilyNativeLoweringRefactorPlan.md](./GRCL-V3-FamilyNativeLoweringRefactorPlan.md)
- [GRCL-V3-FamilyNativeLoweringRefactorChecklist.md](./GRCL-V3-FamilyNativeLoweringRefactorChecklist.md)

That note defines:

- the two-lane lowering split
- what remains shared
- what stops being authoritative for `grcv3.rich.v2+`
- the staged migration from compatibility-path lowering to family-native
  lowering

## 3. Target Outcome

The target outcome is larger than “make one spark probe work.”

The actual target is a staged proof:

1. a minimal `GRCV3`-rich seed can reproduce a seed-driven sparkable local
   geometry,
2. the same mechanism is documented cleanly enough to be reused,
3. and therefore the project can proceed to a **full `GRCL-v3` capability**
   instead of accumulating ad-hoc projector exceptions.

If that staged proof fails, the failure should still tell us exactly what
source-side information remains missing.

For the post-`rich.v3` step, that proof standard is now stronger:

- `rich.v4` should not be used to add another refinement layer on top of
  projector behavior
- it should be used only to make the source contract explicit enough that
  runtime assembly becomes a direct translation problem

## 4. Scope Boundary

### 4.1 What Stays In Neutral/Common `GRCL`

The following remain part of the shared seed layer:

- basin / plateau / ridge / valley / junction / saddle ontology
- containment and hierarchy references
- coherence priors
- neutral chart hints
- transport intent
- top-level constitutive profile

### 4.2 What Moves Into `GRCL-v3`

`GRCL-v3` should carry only the information that is:

- genuinely geometry-bearing,
- necessary for `GRCV3` differential reconstruction or spark formation,
- and not safely reconstructible from the neutral/common layer alone.

Expected examples:

- local motif realization intent
- explicit support-node geometry around a semantic center
- weak-axis or branch-interface layout intent
- local frame orientation or axis-role intent
- boundary/support placement intent for ridge-bearing regions
- channel interior stencil intent when a valley must realize as more than a
  neutral chain

### 4.3 What Must Still Be Forbidden

Even in `GRCL-v3`, the seed should still not store runtime results as source
truth.

That means:

- no solved per-step flux fields,
- no mutable runtime caches,
- no direct serialization of “current basin attributes” as if they were source
  ontology,
- and no undocumented projector-private blobs.

The rich seed may carry constructive geometry instructions.
It should not smuggle in post-solve state.

For `grcv3.rich.v4`, this implies an even tighter boundary:

- add only source semantics that can be translated directly into native
  assembly
- do not add fields whose only purpose is to give the projector more room to
  guess

## 5. Design Principles

### 5.1 Preserve Meaning Before Tuning Thresholds

The rich seed should add missing geometric meaning first.
It should not be used as a substitute for loosening `eps_gradient`,
`eps_hessian`, or `eps_spark`.

### 5.2 Projector As Lowerer, Not Guesser

Given a `GRCL-v3` block, the projector should mostly preserve and lower the
described local structure.

It should not rely on:

- unstable heuristics,
- topology-only reconstruction when geometry was explicitly provided,
- or silent fallback to neutral/common realization if that would erase the
  relevant `GRCV3` information.

For `grcv3.rich.v4`, this principle becomes stricter:

- there should be no projector-style semantic lowering at all
- only direct translation from explicit `rich.v4` declarations into native
  runtime assembly

### 5.3 Neutral/Common Compatibility Must Remain Intact

Other families must still be able to read the same seed and ignore
`extensions.grcv3` safely.

### 5.4 Determinism Must Stay First-Class

Rich-seed lowering must be deterministic under:

- primitive ordering,
- realized node ordering,
- realized edge ordering,
- support placement,
- and snapshot/telemetry emission.

### 5.5 One Common Language, Typed Family Extension

The code organization must preserve one seed language rather than creating
separate “v2 seeds” and “v3 seeds.”

The correct rule is:

- neutral/common `GRCL` remains the only shared seed language
- `GRCL-v3` is a typed family extension under `extensions.grcv3`

This means:

- `GRCV2` continues to consume only the neutral/common seed layer
- `GRCV3` may consume the neutral/common layer plus `extensions.grcv3`
- other families may ignore `extensions.grcv3` without reinterpretation

The project should not create:

- a second top-level seed schema for `GRCV3`
- a separate seed file format just for `GRCV3`
- or duplicated common parsing/loading paths

### 5.6 Typed Extension Parsing, Not Raw Mapping Reach-Through

The implementation should preserve the current seed boundary:

- `src/pygrc/landscapes/seed.py`
- `src/pygrc/landscapes/io.py`
- `src/pygrc/landscapes/validation.py`

and add a typed family-extension layer under `landscapes`, not under runtime
models.

Recommended module shape:

```text
src/pygrc/landscapes/
  seed.py
  io.py
  validation.py
  extensions/
    __init__.py
    grcv3.py
```

`grcv3.py` should own:

- typed top-level and primitive-level `GRCV3` rich-seed dataclasses
- extraction helpers from raw `extensions.grcv3`
- contract-version dispatch
- `GRCV3`-specific extension validation

The projector should consume typed extension objects, not raw nested dicts
scattered throughout projector logic.

### 5.7 Two-Level Versioning

Versioning must stay split cleanly between:

1. **common seed version**
   - `seed_schema`
   - `seed_version`
2. **family extension contract version**
   - `extensions.grcv3.contract_version`

The common seed version changes only when the neutral/common language changes.

The `GRCV3` contract version changes when the `GRCL-v3` rich extension surface
changes without changing the shared seed language.

This prevents a `GRCV3` extension change from forcing an unnecessary bump of the
common seed version.

### 5.8 Invisibility Boundary To The Rest Of GRC

Rich-seed details should be visible only to:

- seed loading/normalization
- extension extraction/validation
- family-local projector code

They should be invisible to:

- runtime step loops
- state-update logic
- telemetry code beyond projector metadata
- visualization code beyond already-lowered runtime artifacts

In practice, this means:

- no raw `primitive.extensions["grcv3"]` access in runtime model code
- no `seed_version` branching inside `GRCV3.step()`
- no rich-seed parsing logic scattered through telemetry or visualization

The rest of `GRCV3` should receive only:

- a constructed `GRCV3State`
- plus any projector metadata explicitly attached for diagnostics

## 6. Minimum Viable `GRCL-v3`

The minimum viable `GRCL-v3` surface should be intentionally small.

It should support one decisive experiment:

- a seed-driven structure that is rich enough to preserve the local geometry of
  a known sparkable `GRCV3` motif.

That minimum viable surface should likely include:

1. **primitive-level `extensions.grcv3.realization`**
   - motif kind
   - support count
   - support radius / relative scale
   - support angles or branch ordering

2. **primitive-level `extensions.grcv3.local_geometry`**
   - local axis intent
   - preferred weak axis
   - branch-interface labeling
   - optional center/support role semantics

3. **edge-carrier or channel realization hints**
   - channel interior node count
   - waypoint preservation policy
   - interface attachment policy

4. **ridge/boundary realization hints**
   - support arc placement rule
   - normal/tangent orientation intent
   - barrier-support distribution rule

The exact field names should be chosen only once they can be justified against
the first minimal rich-seed probe.

### 6.1 First Executable Contract Lock

Before any rich-seed code lands, the first executable contract is now fixed as
follows.

Top-level accepted fields:

- `extensions.grcv3.contract_version`
- `extensions.grcv3.rich_required`

Primitive-level accepted fields:

- `extensions.grcv3.realization.kind`
- `extensions.grcv3.realization.support_count`
- `extensions.grcv3.realization.radius_scale`
- `extensions.grcv3.realization.branch_order`
- `extensions.grcv3.local_geometry.frame_mode`
- `extensions.grcv3.local_geometry.weak_axis_role`
- `extensions.grcv3.interfaces.branch_targets`

Locked first contract version value:

- `extensions.grcv3.contract_version = "grcv3.rich.v1"`

First allowed primitive kinds for the minimal probe:

- `junction`
- `saddle`

This keeps the first lane focused on the currently demonstrated failure mode:

- junction/saddle-local geometry that neutral/common projection cannot preserve
  well enough for `GRCV3` spark formation

Explicitly out of scope for the first executable slice:

- `lowering_policy`
- `projection_goal`
- `realization.attachment_mode`
- `realization.support_angles`
- `local_geometry.axis_roles`
- `local_geometry.symmetry_class`
- `local_geometry.center_role`
- all of `curvature_intent`
- all of `boundary_geometry`
- all of `channel_geometry`

These remain part of the theory-facing vocabulary, but they are not part of the
first consumed contract.

### 6.2 First Validation Boundary

Validation is now fixed as a two-layer boundary.

Layer 1. Neutral/common seed validation:

- `src/pygrc/landscapes/validation.py`
- validates the common seed contract only
- preserves unknown `extensions.*` payloads permissively

Layer 2. `GRCV3` extension validation:

- `src/pygrc/landscapes/extensions/grcv3.py`
- extracts supported `extensions.grcv3` data into typed extension objects
- validates only the consumed rich-field subset
- performs contract-version dispatch

This means the common loader remains reusable for:

- old v2-capable seeds
- new v3-capable seeds

without creating parallel load paths.

### 6.3 First Failure Rules

The first executable failure policy is:

- if `extensions.grcv3` is absent:
  - `GRCV3` uses neutral/common projection
- if `extensions.grcv3` is present and `rich_required = false`:
  - unsupported rich content may be preserved but not consumed
  - supported consumed fields must still validate if the projector claims them
- if `extensions.grcv3` is present and `rich_required = true`:
  - the supported rich contract must be consumed successfully
  - otherwise projection fails explicitly

Unsupported contract-version behavior:

- if `contract_version` is unknown and `rich_required = true`:
  - fail explicitly
- if `contract_version` is unknown and `rich_required = false`:
  - preserve the raw extension payload
  - do not claim rich lowering support

Malformed supported-field behavior:

- invalid `support_count`
- invalid `branch_order`
- invalid `weak_axis_role`
- invalid `branch_targets`

must fail explicitly once `GRCV3` claims to consume the supported contract.

## 7. Implementation Ladder

The implementation should proceed in a strict order.

### Stage 0. Vocabulary And Boundary Note

Deliverable:

- one design note that defines the allowed `extensions.grcv3` vocabulary and
  explicitly distinguishes:
  - constructive source geometry
  - versus forbidden solved runtime state
- one architecture note, within this plan, that defines:
  - common language plus typed extension layering
  - two-level versioning
  - and the invisibility boundary to the rest of `GRC`

Acceptance:

- the allowed rich-seed categories are documented
- the non-goals are documented
- the extension sits cleanly on top of the neutral/common schema
- code organization and versioning boundaries are explicit before parser/projector
  work starts

### Stage 1. Minimal Spark-Preserving Rich Seed

Deliverables:

- one minimal `GRCL-v3` seed fixture
- one projector lowering path that consumes only the minimal rich fields
- one diagnostic script or test that proves seed-driven sparkability is
  preserved
- one typed extension module under `src/pygrc/landscapes/extensions/grcv3.py`

Acceptance:

- the rich seed lowers deterministically
- the resulting `GRCV3` state reaches at least:
  - geometric seed detection
  - spark candidate detection
- and ideally the first spark lifecycle events under documented thresholds

### Stage 2. Manual-State Equivalence Check

Deliverables:

- a comparison note between:
  - the manual spark probe state
  - and the state realized from the minimal rich seed

Acceptance:

- equivalence is not required at raw-field identity level
- but the realized seed must preserve the key constitutive geometry:
  - interior point with usable neighborhood
  - low enough gradient
  - near-degenerate signed curvature on the intended axis
  - stable orthogonal curvature

### Stage 3. Schema And Validation Lift

Deliverables:

- schema updates or a dedicated `GRCL-v3` extension note
- validation rules for supported `extensions.grcv3` fields
- clear rejection behavior for malformed rich-seed data
- typed extraction/dispatch for `extensions.grcv3.contract_version`

Acceptance:

- invalid rich fields fail explicitly
- unknown rich fields are either preserved or rejected under a documented mode
- neutral/common loaders remain backward-compatible

### Stage 4. Projector Generalization

Deliverables:

- richer `GRCV3` projector support for:
  - basin-local motifs
  - junction/saddle-local motifs
  - ridge-support realization
  - valley/channel realization

Acceptance:

- projector no longer depends on one handcrafted probe
- multiple rich-seed fixtures can be lowered through the same rules

### Stage 5. Full `GRCL-v3` Capability Commitment

This stage becomes justified only if Stages 1–4 succeed.

Deliverables:

- explicit project decision that `GRCL-v3` is now a supported family-specific
  extension surface
- broader source examples
- family-facing documentation for authoring `GRCV3`-rich seeds

Acceptance:

- `GRCL-v3` is no longer treated as an experiment-only probe format
- it is treated as the proper geometry-bearing seed layer for `GRCV3`

## 8. Success Gates

The gates should be strict.

### Gate A. Minimal Rich Seed Is Real

Pass only if:

- the rich seed expresses something the neutral/common seed could not express
- and that extra content survives projection in a nontrivial way

### Gate B. Minimal Rich Seed Is Operational

Pass only if:

- the seed-driven lowered state produces the target geometric condition
- and the effect is not due merely to threshold loosening or manual state
  injection behind the projector boundary

### Gate C. Full `GRCL-v3` Capability Is Justified

Pass only if:

- the first rich seed is not an isolated special case
- and the extension vocabulary generalizes to at least:
  - basin-local geometry
  - junction/saddle-local geometry
  - interface/channel realization

If Gate C fails, the project should keep the minimal rich-seed path as a probe
tool and stop short of calling it “full `GRCL-v3` capability.”

### Recorded Decision After Gate A / Gate B Split

If Gate A passes but Gate B fails, the project should **not** treat that as
closure. It should record an explicit follow-on decision:

- the minimal rich-seed path is accepted as a real projector-facing extension
  surface
- the next step is to broaden the rich vocabulary deliberately, not by hidden
  projector heuristics
- that broadening should target the missing constitutive local geometry needed
  for honest geometric-seed and spark-candidate emergence

In other words:

- `grcv3.rich.v1` is validated as a real starting contract
- but it is **not yet** sufficient to call the `GRCL-v3` effort complete
- the project should proceed into a broader `GRCL-v3` capability slice rather
  than treating the minimal probe as the final surface

## 8.1 Next Execution Sequence After The Gate Split

The next work should be executed as a second explicit slice rather than as
ad-hoc projector growth.

### Iteration 6. Lock The Second Capability Slice

Purpose:

- define the next accepted rich contract explicitly before implementation

Scope:

- version the broadened contract as `grcv3.rich.v2`
- decide which previously documented fields now become executable
- keep the remaining vocabulary out of scope explicitly

Expected new executable groups:

- `primitive.extensions.grcv3.local_geometry`
  - `axis_roles`
  - `symmetry_class`
  - `center_role`
- `primitive.extensions.grcv3.curvature_intent`
  - `class`
  - `stable_axis_roles`
  - `weak_axis_role`
  - `ordering`
- `primitive.extensions.grcv3.interfaces`
  - `boundary_roles`
  - `channel_roles`
  - `preferred_attachment_sites`
- `primitive.extensions.grcv3.channel_geometry`
  - `realization_kind`
  - `interior_count`
  - `waypoint_policy`
  - `entry_role`
  - `exit_role`
- `primitive.extensions.grcv3.boundary_geometry`
  - `realization_kind`
  - `normal_role`
  - `tangent_role`
  - `arc_span`
  - `support_distribution`

### Iteration 7. Validation And Fixture Lift For `grcv3.rich.v2`

Purpose:

- make the second slice real at the schema and validation layer

Deliverables:

- typed parsing/validation updates for the newly accepted groups
- rejection behavior for malformed or contradictory rich data
- at least one richer seed fixture beyond the minimal probe, authored against
  the new contract

### Iteration 8. Basin And Channel Lowering

Purpose:

- lower the newly explicit local geometry into basin-local and channel-local
  motifs that can preserve directional interior structure

Deliverables:

- basin-local realization updates
- explicit channel realization updates
- deterministic attachment from channel roles / preferred attachment sites into
  lowered node topology

### Iteration 9. Ridge / Boundary Lowering

Purpose:

- realize boundary-support structure explicitly rather than leaving ridge meaning
  mostly semantic

Deliverables:

- ridge-support lowering using boundary geometry vocabulary
- explicit approximation notes where source meaning must be discretized
- diagnostic visibility for realized support arcs / barrier stencils

### Iteration 10. Honest Sparkability Rerun

Purpose:

- rerun the geometric-seed and sparkability gate after the richer source-local
  geometry exists

Deliverables:

- richer-seed diagnostics against the same baseline thresholds
- comparison against the manual spark probes
- explicit rerun of Gate B

### Iteration 11. Generalization And Gate C Decision

Purpose:

- decide whether the broadened capability is still only a probe path or is now
  broad enough to justify the full `GRCL-v3` commitment

Acceptance target:

- at least one richer seed beyond the minimal junction probe lowers honestly
- the projector supports more than a single handcrafted constitutive case
- Gate C can be decided explicitly, not inferred

Recorded outcome:

- Gate C: `FAIL`
- rationale:
  - the broadened `grcv3.rich.v2+` capability now genuinely generalizes the
    source/lowering surface beyond the original minimal junction probe
  - but no richer seed beyond that original probe yet lowers honestly into the
    sparkable weak-axis interior regime required for full constitutive closure
- project consequence:
  - keep the broadened lane as a real projector-facing and family-native probe
    capability
  - do not treat the current state as full `GRCL-v3`
  - the next justified work targets constructive interior geometry semantics,
    not broader claims of generalization

### Iteration 12. Lock The Third Capability Slice

Purpose:

- define the next accepted rich contract explicitly as `grcv3.rich.v3`
- and make the direct-assembly target concrete before implementation resumes

Scope:

## 8.5 Next Execution Sequence After The First `rich.v4` Pass

Iteration 24 changes the project state materially.

The important result is now:

- direct source semantics can reach real `GRCV3` spark lifecycle events under
  the normal runtime loop

That means the next step is **not**:

- open “full `rich.v4` content” immediately
- add unrelated new semantic families
- or fall back into projector-style enrichment under a new name

The next step **is**:

- consolidate the first `rich.v4` win
- make the transient seed-to-spark path more observable
- and broaden `rich.v4` only inside the same
  `primitive.extensions.grcv3.transfer_mediation` family until the remaining
  gap is understood clearly

### Iteration 25. `rich.v4` Pass Consolidation And Closure Boundary

Purpose:

- record Iteration 24 as the first successful direct-translation gate
- define what is now considered closed
- define what is still explicitly open

Deliverables:

- a short closeout note in the checklist and rationale that distinguishes:
  - spark reachability
  - geometric validation visibility
  - future vocabulary growth
- an explicit rule that `rich.v4` is not broadened yet by opening unrelated
  semantic groups

Acceptance:

- the project records clearly that the open problem is no longer
  “can direct source semantics reach spark?”
- the remaining problem is described as:
  - transient-path observability
  - and possible later strengthening of transfer mediation only

### Iteration 26. Seed-To-Spark Observability Lift

Purpose:

- make the first `rich.v4` pass inspectable enough that later broadening is
  guided by evidence rather than guesswork

Deliverables:

- explicit runtime/telemetry-facing diagnostics for the transient
  seed-to-spark path, especially:
  - center-gradient evolution
  - signed-curvature evolution on the intended weak axis
  - transfer-surface realization summaries
  - event-aligned snapshots or summaries around candidate/spark/split onset
- recorded comparison guidance for:
  - `rich.v3` event-flat lane
  - first `rich.v4` spark lane

Acceptance:

- a later reviewer can see not only that spark events happened, but how the
  interior regime moved before they happened
- the observability lift remains downstream-only:
  - no runtime-equation changes
  - no source-schema broadening

### Iteration 27. Controlled `transfer_mediation` Broadening

Purpose:

- broaden `rich.v4` only if the Iteration 26 evidence shows a real remaining
  source-side gap inside transfer mediation itself

Allowed direction:

- additional `transfer_mediation` semantics that can still be translated
  directly into native assembly

Forbidden direction:

- opening unrelated rich semantic families before the current one is exhausted
- reintroducing heuristic projector interpretation
- encoding solved runtime state

Expected deliverables:

- one or more additional direct-translation fields inside
  `primitive.extensions.grcv3.transfer_mediation`
- likely first candidate if the residual remains center-ingress specific:
  - `center_coupling_classes`
- at least one follow-on probe that uses those fields
- explicit comparison against the current first-pass
  `grcv3-rich-v4-transfer-mediation-probe` lane

Acceptance:

- each new field has a direct assembly meaning
- each new field is justified by an observed residual gap, not by speculation
- the expanded lane remains deterministic and family-native
- if `center_coupling_classes` is used, it must operate only on already-declared
  probe roles and center-spoke participation; it must not reopen geometry or
  carrier-placement families

### Iteration 28. `rich.v4` Breadth Decision

Purpose:

- decide whether `rich.v4` is now broad enough to be treated as a stable
  `GRCV3` rich-source family, or whether more work is still needed

Acceptance target:

- direct source semantics remain the authority
- the transfer-mediation family is no longer only a one-off probe
- the evidence is strong enough to justify either:
  - staying inside `transfer_mediation` for one more cycle
  - or opening the next direct-translation semantic family intentionally

Recorded rule:

- “full content” is not a planning goal by itself
- the only justified growth is evidence-led growth from already-confirmed
  direct semantic gaps
- the strongest likely current outcome is:
  - `grcv3.rich.v4` should be treated as a **narrow but stable**
    family-level authoring surface
  - not merely a disposable probe family
  - and not yet a fully general-purpose rich authoring surface for every
    `GRCV3` interior regime

Recorded breadth-decision guidance:

- if the first direct-translation lane can:
  - produce seed-driven spark lifecycle behavior
  - remain deterministic
  - survive observability review
  - and accept one controlled evidence-led broadening without losing its
    semantic boundary
- then it has crossed from “probe only” into “stable narrow family”
- later growth should therefore be judged against that stable narrow boundary,
  not against an expectation of immediate full semantic coverage

Recorded next-step guidance after Iteration 28:

- do not broaden `rich.v4` immediately just because a new field could be added
- first exploit the now-existing rich-v4 evidence lane more fully:
  - use the saved spark/split/collapse artifacts as the baseline reference lane
  - compare later candidates against that lane rather than against only
    pre-artifact intuition
- if `rich.v4` grows again, prefer one of two directions only:
  - one more transfer-mediation cycle, but only if transient evidence still
    localizes the residual issue to ingress structure
  - or one intentionally opened new direct semantic family, with the same
    explicit source/runtime boundary discipline
- do not reopen:
  - generic geometry widening
  - projector-style interpretation
  - or constitutive/runtime compensation for weak source structure

Recorded candidate for the next evidence-led `rich.v4` cycle:

- the strongest currently plausible next move is **not** a new family named
  around phenomenological effects such as “compliance” or “damping”
- it is more likely one additional direct-translation slice **inside**
  `primitive.extensions.grcv3.transfer_mediation`
- target meaning:
  - explicit carrier-to-probe path structure between the load-carrier layer
    and the probe shell
- reason:
  - current `rich.v4` already controls:
    - pair coverage
    - guard/spill structure
    - center-spoke participation
  - but it does not yet explicitly describe the assembled path shape of those
    mediated routes

Preferred structural vocabulary for such a candidate, if opened later:

- `path_roles`
- `path_mode`
- `path_topology`

Preferred value style:

- structural / assembly-facing values such as:
  - `direct`
  - `single_intermediate`
  - `double_intermediate`
  - `fan_in`
  - `buffered_chain`

Explicitly discouraged framing:

- naming the next slice around effect-oriented semantics such as:
  - `interior_spoke_compliance`
  - `flexible`
  - `damping`
- because those names describe hoped-for dynamics rather than direct source
  structure

Promotion rule:

- only if this path-structure slice becomes too large or semantically distinct
  to fit cleanly under `transfer_mediation` should it be promoted into a new
  direct semantic family

### 8.6 Post-Closeout Meaning Of The Continuing `GRCL-v3` Arc

The post-Iteration-28 `GRCL-v3` work should not be read as “Phase 5 failed to
close” or as an attempt to keep extending `GRCV3` runtime scope indefinitely.

Its role is narrower and more valuable than that:

- it is a landscape-semantics continuation of the `GRCL-v3` arc
- it is testing which distinctions can be stated truthfully in
  source/landscape language
- and it is separating genuine source-bearing semantics from constructive or
  runtime-only realization choices

Iterations 29 to 32 make that explicit:

- `path_topology` is a real source-side structural distinction
- but added intermediacy suppresses the current spark lane
- and the failure trace shows that the problem is not simple lack of ingress
  transport
- instead, ingress survives while the needed weak-axis geometry fails to form

So the value of this arc is no longer only:

- “can one more field recover the spark lane?”

It is also:

- “what landscape language corresponds truthfully to the behavior we are
  actually seeing?”

This matters for the whole `GRCL-v3` program:

- successful semantic probes strengthen the authoring surface by adding real
  source-side distinctions
- failed semantic probes can still strengthen the boundary by showing where a
  plausible landscape phrase does **not** match the actual dynamical mechanism
- and later family-local seed work is safer when these failed translations are
  recorded explicitly rather than forgotten once a lane does not recover

The continuation rule after Iteration 32 is therefore:

- judge any new `GRCL-v3` semantic probe not only by whether it restores a
  visible behavior lane
- but also by whether it makes the landscape language more behavior-truthful

After Iterations 37 to 40, that continuation rule has a stronger practical
corollary:

- `transfer_mediation` should now be treated as close to exhausted for the
  current spindle spark side-quest
- not because it failed, but because it already produced the main language
  distinctions it could justify
- the next step should therefore be to identify the next direct semantic family
  intentionally, unless a clearly missing `transfer_mediation` distinction is
  named more directly than a family change

Current recorded candidate for that next family:

- `primitive.extensions.grcv3.settlement_regime`
- or, if a narrower name is preferred,
  `primitive.extensions.grcv3.settlement_locus`

Reason:

- the remaining unexplained behavior is now about operative settlement locus
  and migration, not mainly about geometry, partition, carrier placement, or
  transfer mediation itself
- this candidate should be recorded first as a theory-facing proposal before
  any concrete Iteration 41 is opened

After Iterations 41 to 42, that proposal is no longer only a naming choice:

- the next family is now explicitly locked as
  `primitive.extensions.grcv3.settlement_regime`
- and its first executable slice is now real through
  `settlement_regime.regime_class`
- that first slice is intentionally narrow:
  - `carrier_site_regime`
  - `path_node_regime`
- and it is already behavior-bearing in the current spindle lane rather than
  serving only as retrospective trace commentary

After Iteration 43, the next planning rule inside that family becomes:

- prefer decomposition of already-proven regime facts before inventing a third
  regime label
- specifically, treat:
  - first settlement locus
  - and later split-child inheritance
  as separately testable source distinctions when the evidence supports it

Current practical result:

- `path_node + anchored` still sparks
- but it no longer shows later split-child candidate migration

So future `settlement_regime` growth should favor explicit factorization of
regime structure over prematurely naming more coarse composite regimes.

After Iteration 44, one more planning constraint is now explicit:

- do not assume the decomposed regime fields define a full freely-combinable
  matrix just because both fields are executable
- check whether each new combination opens a genuinely new productive regime or
  only a productive but non-repeating variant

Current matrix-completion result:

- `carrier_site + split_child_inheriting` does not open a new repeated regime
- so the currently productive repeating space remains narrower than the full
  two-field cross-product
- more specifically, only
  `path_node + split_child_inheriting` currently repeats
- while:
  - `carrier_site + anchored`
  - `path_node + anchored`
  - `carrier_site + split_child_inheriting`
  are all productive but one-shot

After Iteration 45, the next planning constraint sharpens again:

- do not infer the reason for non-repetition from the regime matrix alone
- trace post-split descendant behavior directly before naming another semantic
  field

Current post-split reentry result:

- the repeating `path_node + split_child_inheriting` lane re-enters because
  derived split children eventually settle enough to pass the candidate gate
- the one-shot `carrier_site + split_child_inheriting` lane still forms and
  retains derived child sites
- but those child sites never settle enough to re-enter the spark gate

After Iteration 46, one more planning constraint becomes explicit:

- before naming any further `settlement_regime` field, check whether the
  remaining difference is already visible as a stable descendant neighborhood
  signature

Current neighborhood-boundary result:

- at the matched descendant step where the repeating path-derived children first
  become gate-ready, they share:
  - `basin_support`
  - `basin_load_carrier`
  neighbors
- the one-shot carrier-derived children at the same matched step instead share:
  - `basin_support`
  - `ridge_support`
  neighbors
- so the current strongest explanatory signature is not only internal child-site
  readiness, but also inherited neighborhood role mix

After Iteration 47, the narrowing rule becomes sharper still:

- before proposing a broad inherited-neighborhood field, first isolate whether
  the real difference survives after factoring out common support burden

Current support-isolation result:

- at the matched descendant step, both lanes keep the same descendant degree
- and nearly identical common `basin_support` weight
- the surviving isolated difference is the secondary non-support role:
  - repeating lane: `basin_load_carrier`
  - one-shot lane: `ridge_support`

After Iteration 48, the remaining planning fork becomes explicit:

- if the isolated secondary support class survives a decisive counterfactual,
  stop treating it as mere correlated observability

Current counterfactual result:

- pruning the repeating lane's descendant secondary `basin_load_carrier`
  adjacency removes reentry
- pruning the one-shot lane's descendant secondary `ridge_support` adjacency
  does not rescue reentry
- so the current end-stop result is:
  - retained secondary `basin_load_carrier` support is necessary
  - removing secondary `ridge_support` is not sufficient

Current planning preference after Iteration 48:

- do **not** immediately promote inherited secondary support class into a new
  `settlement_regime` field
- instead, treat Iteration 48 as the present closure boundary for this slice
- then ask the translation-gap question directly:
  - can existing structural families already author the required secondary
    `basin_load_carrier` adjacency?
  - or is a new field genuinely needed?

So the next justified iteration is an **existing-vocabulary structural
authorability test**, not a direct schema expansion.

After Iteration 49, the planning consequence is now explicit:

- the required descendant secondary `basin_load_carrier` support condition is
  already authorable through existing structure
- so there is no present reason to add a new `settlement_regime` field for it

Current authorability result:

- the pre-`settlement_regime` structural path lane already shows the same
  repeating descendant secondary-support condition as the later explicit path
  lane
- between those two path seeds, the only added family is `settlement_regime`
- among the candidate existing families compared here, the decisive
  discriminatory family is `transfer_mediation`
- `interior_load_carriers`, `channel_geometry`, and `boundary_geometry` remain
  unchanged across the decisive path/direct comparison

So the current planning read is:

- `settlement_regime` is now cleanly closed for this spindle side-quest
- the family should remain at:
  - `initial_locus_class`
  - `split_inheritance_mode`
- and any later reopening should require a new genuine translation gap, not a
  traced downstream consequence of existing structure

Recorded next-step guidance after Iteration 49:

- do **not** continue by default inside `transfer_mediation`
- do **not** continue by default inside `settlement_regime`
- and do **not** open another structural family by default before checking
  collapse from the same language perspective

The next move should instead be a collapse-side language audit.

Its purpose is to ask the same direct-translation question already asked for
spark, split, settlement locus, and reentry:

- which collapse-side distinctions are already described by the present
  language?
- which collapse behaviors are only downstream consequences of already-authored
  structure?
- and does collapse expose a genuine next translation gap that the earlier
  spindle-lane work did not already settle?

The preferred next execution slice is therefore:

- an Iteration 50 collapse-regime characterization pass focused on:
  - first collapse step
  - collapse source locus
  - collapse sink locus
  - whether collapse stays in the same locus family as spark
  - whether carrier-site and path-node regimes collapse differently
  - whether split children participate in later collapse or only in
    spark/reentry

Planning rule for that pass:

- keep direct controls active while comparing collapse behavior
- prefer trace/authorability tests before proposing any new collapse field
- and treat traced runtime necessity as insufficient by itself for vocabulary
  promotion

Only after that collapse-side audit should the project decide whether the next
move is:

- no new family at all
- a narrow extension of existing family structure
- or a genuinely new collapse-relevant structural family

After Iteration 50, the current collapse-side result is:

- the matched carrier-site direct lanes do not collapse in the current audit
  window
- the matched path-regime lanes do collapse
- the observed path-lane collapse first appears on step `17`
- the collapse source locus is `basin_support`
- the collapse sink locus is `carrier_site`
- so collapse does **not** stay in the same locus family as the first spark
  site in those lanes:
  - first spark locus: `path_node`
  - first collapse source locus: `basin_support`
- later split children do not participate in the recorded collapse events

So the current planning read after Iteration 50 is:

- collapse is visible as a downstream support-to-carrier resolution pattern in
  the specific spindle lanes audited here
- the present evidence does **not** justify a new collapse-specific family yet
- and any later collapse-side promotion should require a real authoring gap
  that existing structure still cannot distinguish or produce honestly

This should not be over-read as a full collapse census.

Broader family records already preserve multiple collapse-capable lanes,
including:

- the saved rich-v4 spark/split/collapse artifact lane built from
  `grcv3-rich-v4-transfer-mediation-probe.seed.yaml`
- the dedicated early-collapse probe
  `grcv3-rich-collapse-example.seed.yaml`

So the remaining Iteration 50 follow-on is not “prove collapse exists.”
It is to broaden the collapse audit across those already-recorded lanes and ask
whether the original collapse questions still close without opening a new
family:

- first collapse step across additional collapse-capable seeds
- collapse source locus and sink locus outside the narrow spindle controls
- whether any recorded lane collapses from the same locus family as spark
- and whether a broader collapse comparison reveals a genuine source-language
  gap rather than only more downstream variation

Broadened recorded-lane review now makes one more fact explicit:

- the broader collapse-capable seeds do **not** all show the same collapse
  pattern
- the dedicated collapse example collapses early from `basin_support` into
  `junction_branch` without prior spark
- the rich-v4 transfer-mediation artifact lane collapses later from
  `basin_center` into `basin_support` after spark/split
- the older basin/boundary/channel fulltest lane collapses from
  `basin_support` into `ridge_support` without prior spark

So the broadened read is:

- collapse evidence is plural
- but it is already heterogeneous enough that the original Iteration 50
  questions remain open outside the narrow spindle controls
- and the next useful move should be controlled comparison **within**
  collapse-pattern clusters before any collapse-specific schema promotion is
  considered

Iteration 51 now closes the first of those controlled cluster comparisons:

- it compares the two recorded `collapse_without_prior_spark` lanes directly:
  - `grcv3-rich-collapse-example.seed.yaml`
  - `grcv3-rich-basin-boundary-channel-probe.seed.yaml`
- both lanes first detect choice on step `1`
- both lanes collapse without prior spark
- both lanes first collapse from `basin_support`
- but the early-collapse example collapses into `junction_branch` on step `3`
- while the basin/boundary/channel lane collapses into `ridge_support` on step
  `100`

The controlling comparison is not just runtime timing.
The seed-side authored structure also differs across the pair in:

- `realization`
- `local_geometry`
- `interfaces`
- `boundary_geometry`
- `channel_geometry`

So the current plan-level read after Iteration 51 is:

- the pre-spark collapse cluster is now better explained
- its sink difference already tracks existing `junction` vs
  `boundary/channel` structure and neighborhood mix
- so it still does **not** justify a new collapse-specific family

That pushes the remaining collapse-side frontier to the other cluster:

- the post-spark collapse behavior represented by the rich-v4
  transfer-mediation artifact lane
- and any later comparison that can test whether that post-spark behavior is
  also fully authored by present structure or still exposes a genuine
  source-language gap

The next preferred execution slice is therefore Iteration 52:

- a post-spark collapse boundary pass centered on
  `grcv3-rich-v4-transfer-mediation-probe.seed.yaml`
- using the closest controlled rich-v4 comparison lane or lane set available
  to isolate the first decisive post-spark divergence
- with priority on whether the later `basin_center -> basin_support` collapse
  is already explained by existing:
  - `transfer_mediation`
  - `settlement_regime`
  - split/reentry structure
  - local support/carrier neighborhood
  - geometry/interface families

Planning rule for Iteration 52:

- prefer the tightest controlled post-spark comparison over another broad
  survey
- treat runtime sequence alone as insufficient for schema promotion
- and only propose a new collapse-side family if the post-spark comparison
  leaves a concrete source-language distinction that current authored
  structure still cannot express

Iteration 52 now closes that post-spark comparison as well:

- the saved artifact lane
  `grcv3-rich-v4-transfer-mediation-probe.seed.yaml`
  is best compared against two direct controls inside the same
  `transfer_mediation` lineage:
  - `grcv3-rich-v4-center-coupling-probe.seed.yaml`
  - `grcv3-rich-v4-asymmetric-center-coupling-probe.seed.yaml`
- all three lanes first detect choice on step `1`
- the baseline and refined lanes first spark on step `6` at the same
  `carrier_site` locus and later collapse from `basin_center` into
  `basin_support` on steps `71` and `72`
- the blocked center-coupling control instead first sparks on step `99` at
  `basin_support`, first collapses on step `99` from `carrier_site` into
  `ridge_support`, and only then completes its first split on step `100`

The decisive point is that this comparison is already authored by existing
source structure:

- baseline vs blocked differs in `transfer_mediation`
- baseline vs refined differs in `transfer_mediation`
- the comparison stays the same in `interfaces`, `boundary_geometry`,
  `channel_geometry`, `interior_load_carriers`, and `local_geometry`

So the current plan-level read after Iteration 52 is:

- the remaining post-spark collapse boundary does **not** require a new family
- it is already expressible inside existing `transfer_mediation`
- more specifically, the current evidence points to
  `transfer_mediation.center_coupling_classes` as the decisive source-side
  lever for this collapse boundary

Iteration 53 widens that same trio to `150` steps and refines the planning
read again:

- the baseline and refined lanes each add one late collapse
  (`116` / `117`), and both remain in the same
  `basin_center -> basin_support` pattern
- the blocked center-coupling control does **not** stay cleanly distinct
  through the widened window
- instead, after its late step-`99/100` spark/split boundary it runs through a
  distinct carrier/split-child collapse cascade:
  - `101` carrier-site into split-child
  - additional split-child collapses
- and only later, on step `121`, does it first reach the same broad
  `basin_center -> basin_support` collapse pattern as the other two lanes

So the current plan-level read after Iteration 53 is:

- collapse-side work still does **not** justify a new family
- the decisive source-side lever remains inside existing
  `transfer_mediation.center_coupling_classes`
- but collapse interpretation is not fully closed yet, because the blocked
  control reaches the shared late pattern only after a distinct late cascade

That suggests the next useful move is no longer another family hunt.
It is a narrower late-cascade interpretation pass on the blocked
center-coupling lane:

- explain why that lane delays convergence behind carrier/split-child collapse
  events
- and determine whether that delay is already authored by existing
  `transfer_mediation` structure or only by downstream runtime sequencing

Iteration 54 closes that remaining interpretation question:

- the decisive matched comparison is between the two direct controls
  that differ only in `transfer_mediation.center_coupling_classes`:
  - blocked: `[[north, blocked], [south, blocked]]`
  - refined: `[[north, strong], [south, weak]]`
- `interfaces`, `boundary_geometry`, `channel_geometry`,
  `interior_load_carriers`, and `local_geometry` remain the same
- the blocked lane uniquely shows the late carrier/split-child cascade before
  reaching the shared `basin_center -> basin_support` pattern
- the refined lane reaches that shared late pattern without the distinct
  pre-convergence cascade

So the current plan-level read after Iteration 54 is:

- the late blocked-lane delay is already authored by existing
  `transfer_mediation.center_coupling_classes`
- the collapse-side arc does **not** justify a new family
- and the collapse family question is now materially closed under the current
  evidence bundle

Any future return to collapse should therefore require a genuinely new
unaccounted-for collapse distinction, not just another runtime-rich variation
inside the structures already traced here

Iteration 55 adds the stricter phenomenology question about post-collapse
“prevention” and still closes it inside the same source structure:

- the blocked lane does not need an explicit anti-reentry rule to stop
  preferring the original `ridge_support` sink
- instead, its collapse path is rerouted geometrically:
  - first `carrier_site -> ridge_support`
  - then `carrier_site -> split_child`
  - later `basin_center -> basin_support`
- the relevant neighborhood around the collapsing source shifts accordingly:
  - initial carrier sees `basin_support`, `ridge_support`, `split_child`
  - rerouted carrier sees `split_child`, `valley_channel`
  - later basin center sees only `basin_support`

And the matched-control comparison remains narrow:

- blocked vs refined still differs only in
  `transfer_mediation.center_coupling_classes`
- while the compared geometry/interface/carrier families remain the same

So the current plan-level read after Iteration 55 is:

- post-collapse exclusion can be understood as geometry-mediated rerouting of
  preference, not as a missing persistence rule
- that rerouting is already authorable inside existing
  `transfer_mediation.center_coupling_classes`
- and the collapse-side phenomenology remains materially closed at the family
  level under the current evidence bundle

That is enough to mark collapse exploration done for the current planning
window:

- Iterations 50 through 55 answered the open collapse-side family question
- no new collapse-side source family is presently justified
- and collapse is no longer the default next exploration lane unless a later
  artifact exposes a genuinely new source-side distinction

The previously discussed interior-shaping direction remains a plausible later
structural follow-on, but not the default immediate step:

- `primitive.extensions.grcv3.interior_geometry`
  - `probe_mode`
  - `support_profile`
  - `attachment_isolation`
  - `interior_clearance_class`
  - `support_connectivity`
  - `support_role_groups`

### Iteration 13. Validation And Fixture Lift For `grcv3.rich.v3`

Purpose:

- make the third slice real at the schema and validation layer

Deliverables:

- typed parsing/validation for `interior_geometry`
- explicit rejection of malformed or self-contradictory interior-shaping data
- one dedicated `grcv3.rich.v3` spark-oriented probe seed

### Iteration 14. Direct Interior-Geometry Assembly

Purpose:

- implement the first direct family-native assembly path for
  `interior_geometry`

Deliverables:

- deterministic assembly of support-role groups
- deterministic support-spacing / confinement realization from
  `support_profile`
- deterministic attachment-isolation handling
- explicit diagnostics showing how the declared interior motif was assembled

### Iteration 15. Weak-Axis Spark Gate

Purpose:

- test whether the first `grcv3.rich.v3` direct-assembly seed can move from a
  merely valid interior geometric seed into an actual spark candidate regime

Deliverables:

- rerun against the same baseline thresholds
- compare against the basin-centered weak-axis probe
- record whether the result is:
  - still only a validated interior seed
  - or a real `spark_candidate`
  - or an actual `spark` event lane

Acceptance target:

- at least one `grcv3.rich.v3` seed lowers through the direct-assembly path
  honestly enough to produce either:
  - a real spark candidate
  - or a documented near-miss that localizes the next missing constructive
    field precisely

### Iteration 16. Lock The Interior-Partition Slice

Purpose:

- define the next constructive group after the first executable
  `interior_geometry` slice

Deliverables:

- lock `primitive.extensions.grcv3.interior_partition` as the next
  theory-facing vocabulary group
- define the first allowed executable field set:
  - `partition_mode`
  - `load_role_groups`
  - `load_transfer_mode`
  - `probe_protection_class`
  - `attachment_transfer_roles`
- keep the solved-state boundary explicit
- keep the first scope narrow:
  - basin-centered interior probes already using `interior_geometry`
  - channel/ridge load routing into that structure

### Iteration 17. Validation And Fixture Lift For Interior Partition

Purpose:

- make the next constructive group real at the schema and fixture layer before
  runtime lowering changes resume

Deliverables:

- typed parsing/validation for `interior_partition`
- explicit rejection of contradictory probe-vs-load partition payloads
- one dedicated probe seed that uses both:
  - `interior_geometry`
  - `interior_partition`

### Iteration 18. Two-Tier Native Assembly And Spark Gate

Purpose:

- test whether a source-declared inner-probe / outer-load partition can keep
  the center low-gradient while preserving a weak-axis stencil

Deliverables:

- direct native assembly for the first `interior_partition` slice
- rerun of the weak-axis spark gate under the same baseline envelope
- explicit comparison against:
  - `rich.v2` validated-seed near-miss
  - first `rich.v3` near-degenerate / high-gradient near-miss

Acceptance target:

- either:
  - a real validated geometric seed with improved weak-axis degeneracy
  - or a still narrower, explicitly recorded missing constructive field

### Iteration 19. Lock The Load-Carrier Slice

Purpose:

- define the next constructive group after `interior_partition`
- keep the next strengthening source-side rather than compensating in runtime

Deliverables:

- lock `primitive.extensions.grcv3.interior_load_carriers` as the next
  theory-facing vocabulary group
- define the first allowed executable field set:
  - `carrier_layout_mode`
  - `carrier_anchor_policy`
  - `transfer_topology_mode`
  - `transfer_role_pairs`
  - `carrier_attachment_roles`
- keep the solved-state boundary explicit
- keep the first scope narrow:
  - basin-centered interior probes already using:
    - `interior_geometry`
    - `interior_partition`

### Iteration 20. Validation And Fixture Lift For Load Carriers

Purpose:

- make the next constructive group real at the schema and fixture layer before
  native runtime assembly changes resume

Deliverables:

- typed parsing/validation for `interior_load_carriers`
- explicit rejection of contradictory carrier-layout or transfer-topology
  payloads
- one dedicated probe seed that uses:
  - `interior_geometry`
  - `interior_partition`
  - `interior_load_carriers`

### Iteration 21. Carrier-Aware Native Assembly And Spark Gate

Purpose:

- test whether non-coincident outer load carriers plus explicit transfer
  topology can restore a low-gradient center while preserving weak-axis
  degeneracy

Deliverables:

- direct native assembly for the first `interior_load_carriers` slice
- rerun of the same weak-axis spark gate under the documented baseline
  envelope
- explicit comparison against:
  - `rich.v2` validated-seed near-miss
  - first `rich.v3` high-gradient near-miss
  - partitioned `rich.v3` two-tier near-miss

Acceptance target:

- either:
  - a real validated geometric seed with materially improved weak-axis
    degeneracy
  - or a still narrower, explicitly recorded missing constructive field

### Iteration 22. Lock The `rich.v4` Direct-Translation Boundary

Purpose:

- define the first post-`rich.v3` lane explicitly as `grcv3.rich.v4`
- make the architectural rule executable before any new schema/code lands

Deliverables:

- lock `grcv3.rich.v4` as a direct-translation-only contract
- state explicitly that `rich.v4` must not depend on:
  - projector-style semantic lowering
  - compatibility-path blueprint authority
  - heuristic recovery of underspecified interior meaning
- identify the first new field family only in terms of semantics that can be
  translated directly into native assembly:
  - `primitive.extensions.grcv3.transfer_mediation`
- lock the first intended executable field set:
  - `mediation_mode`
  - `pair_mediation_classes`
  - `probe_guard_class`
  - `lateral_spill_policy`
- state the theory-facing correctness rule explicitly:
  - `transfer_mediation` may constrain assembled ingress structure
  - but it may not override the normal `GRCV3` constitutive transport loop
- record which `rich.v3` near-miss the new surface is intended to close:
  - the persistent center-gradient regime after transfer remapping plateaus

Acceptance target:

- the next lane is defined tightly enough that any proposed `rich.v4` field can
  be rejected if it merely gives the projector more room to guess
- and tightly enough that any proposed field can also be rejected if it solves
  transport directly instead of shaping the structure from which transport
  should emerge

### Iteration 23. Validation And Fixture Lift For `rich.v4`

Purpose:

- make the first `rich.v4` slice real at the schema and fixture layer before
  runtime/native-assembly work resumes

Deliverables:

- typed parsing/validation for:
  - `primitive.extensions.grcv3.transfer_mediation`
- explicit rejection of fields that cannot be lowered by direct translation
- one dedicated `rich.v4` probe seed aimed at the known gradient-loaded
  near-miss
- one negative fixture proving that underspecified `rich.v4` payloads fail
  rather than silently downgrading into projector behavior

Acceptance target:

- valid `rich.v4` payloads parse deterministically
- invalid or underdetermined payloads fail explicitly

### Iteration 24. First `rich.v4` Native Assembly Gate

Purpose:

- test whether the first direct-translation-only `rich.v4` slice can move the
  best current near-miss beyond the `rich.v3` plateau honestly

Deliverables:

- first native runtime assembly path that consumes the new `rich.v4` semantics
  directly
- rerun of the weak-axis spark gate under the same documented baseline envelope
- explicit comparison against:
  - `grcv3-rich-v3-load-carrier-spindle-probe.seed.yaml`
  - `grcv3-rich-v3-load-carrier-weak-to-stable-probe.seed.yaml`
- explicit recording of whether the new semantics:
  - reduce center gradient materially
  - preserve or improve weak-axis degeneracy
  - create a validated geometric seed or spark candidate

Acceptance target:

- either:
  - the first `rich.v4` direct-translation slice breaks the current `rich.v3`
    plateau honestly
  - or the next still-missing direct source semantic is recorded more narrowly
    than “more transfer refinement”

## 9. Recommended First Deliverables

The first concrete deliverables should be:

1. a `GRCL-v3` extension vocabulary note
2. one minimal rich-seed fixture that aims to preserve the manual spark motif
3. one projector update that lowers only that vocabulary
4. one deterministic diagnostic run proving whether the rich seed crosses the
   spark gate

Only after that should the project broaden into:

- richer landscape examples,
- representative reruns,
- telemetry extensions,
- and visualization surfaces for `GRCV3`-rich source structures

If the first diagnostic round produces the Gate A / Gate B split above, the
very next artifact should be a broader theory-facing capability note and
checklist update for the next executable `GRCL-v3` slice.

## 10. Non-Goals

This plan does not authorize:

- silent schema drift in the neutral/common seed
- changing `GRCV3` runtime equations to compensate for weak seeds
- importing solved Hessian or flux state directly into source seeds
- declaring `GRCL-v3` complete before the minimal rich-seed gate is passed

## 11. Recommended Next Artifact

The immediate next artifact after this plan should be:

- a theory-facing `GRCL-v3` vocabulary note:
  [GRCL-V3-Vocabulary.md](./GRCL-V3-Vocabulary.md)

That vocabulary note is now in place.
The immediate execution artifact is:

- [GRCL-V3-ImplementationChecklist.md](./GRCL-V3-ImplementationChecklist.md)

That note should answer one question precisely:

- what information may a `GRCV3`-rich seed express that the neutral/common
  seed intentionally cannot?

Once that is written, implementation can proceed with one minimal rich-seed
probe and its projector lowering path.

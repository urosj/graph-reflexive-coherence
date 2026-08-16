# Phase 8 GRC/LGRC Causal Pathway Contract Consolidation Plan

**Status:** Complete through Iteration 111 pressure-consumer closeout

**Runtime behavior changes:** None planned
**Predecessor:** Event-Local Geometry Integration closed without runtime change

## Purpose

Make the existing GRC/LGRC causal pathways legible, selectable, and honest to
compose without replacing them with one universal mechanism.

The repository already contains several valid ways to reconstruct current,
transport coherence, evaluate compatibility, schedule work, commit topology,
retain history, and restore state. Their authority, timing, scope, and claim
boundaries differ. Future experiments need one canonical place to see those
differences before choosing or composing a pathway.

The primary outputs are a pathway contract registry, authority map,
composition matrix, selection guide, source/test/evidence crosswalk, and
conformance rules.

## Separate Identity From The Closed Tranche

The Event-Local Geometry Integration tranche remains permanently closed at:

```text
disposition = close_without_runtime_change
C2 implementation-ready = false
Iteration 97 opened = false
N32 selected = false
```

Its prospective Iterations 97-104 remain historical design pressure owned by
that closed tranche. They are not reused here. This new Phase 8 tranche starts
at Iteration 105.

The predecessor audit contributes a diagnostic coordinate system:

```text
direction | funding | eligibility | scheduling | commitment | reception
```

It does not contribute a generic runtime block or an ownership model.

## Problem Statement

Several source surfaces can look equivalent from outside while carrying
different semantics:

```text
native GRC flux != LGRC packet work
sink compatibility != current generation
route arbitration != native route formation
event scheduling != departure eligibility
runtime mutation authority != causal-work authority
diagnostic reconstruction != causal LGRC execution
persistent basin assignment != transport-causal retained formation
ledger history != history consumed by constitutive dynamics
```

The consolidation should make these distinctions inspectable before an
experiment composes them.

## Scope

The tranche covers documentation and conformance over existing behavior:

- pathway identities and purposes;
- consumed and produced state;
- time and spatial semantics;
- distributed authority coordinates;
- native, producer-mediated, diagnostic, utility, or experimental status;
- restoration and replay identity;
- supported and blocked claims;
- source, specification, test, and evidence pointers;
- lawful, adapter-mediated, unsupported, and misleading compositions;
- selection guidance for future experiments.

### Registry Scope V1

The first registry version is intentionally narrower than the title's eventual
cross-family direction:

```text
in scope:
  GRC9V3
  LGRC9V3
  directly consumed shared PyGRC state, restoration, timing, topology,
  provenance, and telemetry-contract utilities

out of scope unless directly consumed by an admitted pathway:
  GRCV2
  GRCV3
  earlier GRC9 variants
  GRCL9 and other lowering families
```

The title may remain GRC/LGRC because the contract form can later admit other
families. Version 1 must describe itself as the GRC9V3/LGRC9V3 initial registry
scope and must not imply full-family coverage.

## Non-Goals

This tranche does not:

- invent a universal causal-work admission API;
- select a causal-work owner;
- reopen Event-Local Geometry Integration;
- implement source-local current eligibility;
- turn the authority grammar into runtime state;
- erase mechanism-specific eligibility semantics;
- promote producer or diagnostic pathways to native behavior;
- assign ecological meanings to transport mechanics;
- choose L04 support representation;
- select or preserve N32 through relabelling;
- change `src/`, tests, examples, telemetry, visualization, or behavioral
  specifications. Any discrepancy discovered here is conformance or
  maintenance debt and must open a separate repair identity. Explanatory and
  index documentation may change here; behavioral correction may not.

## Canonical Pathway Contract

The consolidation artifacts have separate authority.

### Registry Authority

The registry owns intrinsic pathway facts:

```text
pathway_id
entry_version
name
purpose
substrate_layer
contract_kind
mechanism_ownership
availability
activation
state_consumed
state_produced
time_semantics
spatial_scope
trigger_surface
event_locus
causal_information_scope
stage_sequence
configured_residue
producer_residue
naturalization_debt
budget_and_invariants
state_identity_fields
history_consumed
history_retained_but_not_consumed
fail_closed_conditions
restoration_and_serialization_identity
supported_claims
blocked_claims
evidence_refs
composition_refs
catalog_relation_refs
source_commit
source_digest
last_verified_commit
staleness_state
supersedes
superseded_by
```

Every load-bearing stage should expose:

```text
stage_id
trigger
state_consumed
state_produced
direction_authority
funding_authority
eligibility_authority
scheduling_authority
commit_authority
reception_authority
action_scope
mutation_scope
time_semantics
spatial_scope
failure_or_noop_semantics
```

Pathway-level authority coordinates are summaries or derived views over the
stage sequence. They are not a substitute for stage-local ownership when
authority changes during candidate formation, eligibility, scheduling, debit,
in-flight transport, arrival, credit, or later mutation.

The schema must preserve both distinctions:

```text
information visible to the runtime
  != information causally available to the mechanism

history retained in state or a ledger
  != history consumed by constitutive dynamics
```

Common analytical fields do not imply common implementation or ontology.

### Crosswalk Authority

The source/test/evidence crosswalk owns:

```text
source files and source revision
specification pointers
test source and revision
test execution status and revision
latest known result
experiment and negative evidence
evidence owner
evidence gaps
```

### Composition-Matrix Authority

The composition matrix owns directional inter-pathway relations. The registry
may contain stable `composition_refs`, but it must not duplicate composition
facts.

### Selection-Guide Authority

The selection guide is derived from the registry, crosswalk, and composition
matrix. It may explain a decision but must not introduce new pathway,
evidence, or composition facts.

## Pathway Registry Versus Experiment Catalog

A pathway contract describes how a substrate transition executes and where
authority resides. A primitive, building block, motif, or regime describes an
evidence-backed capacity that may consume one or more pathways.

Therefore:

- one pathway may support several catalog entries;
- one catalog entry may require several pathways;
- pathway existence does not establish primitive or building-block admission;
- catalog admission does not make every consumed pathway native;
- `catalog_relation_refs` never upgrade either surface.

## Initial Pathway Families

The initial admission census starts with, but is not limited to:

1. synchronous GRC transport;
2. GRC sink-compatibility choice and collapse;
3. explicit LGRC packet transport;
4. configured causal-route continuation;
5. route-aspect surplus packet production;
6. producer-mediated feedback or eligibility;
7. native candidate arbitration;
8. flux-conditioned boundary birth;
9. spark diagnostics and topology integration;
10. collapse/reabsorption and topology-state transport;
11. diagnostic GRC reconstruction over LGRC state;
12. restoration, replay, and reset-baseline identity.

The census may add pathways when source inspection shows a distinct
load-bearing contract. It should not split pathways merely because two callers
use different labels.

## Orthogonal Status Vocabulary

Pathway status must not compress ownership, availability, activation, and
evidence into one label.

Mechanism ownership:

```text
native
native_with_configured_semantics
producer
external_adapter
diagnostic
utility
```

Availability:

```text
installed
experiment_local
bounded_external
historical
absent
```

Activation:

```text
default_on
default_off
explicit_call
externally_orchestrated
```

Evidence status belongs to the crosswalk:

```text
current_source_passed
current_source_not_run
historical_passed
historical_failed
experiment_evidence_only
producer_evidence_only
source_without_test
documentation_only
unsupported
```

Composition relations should use:

```text
lawful_native
lawful_with_explicit_adapter
diagnostic_only
producer_mediated
unsupported_missing_crossing
invalid_relabel
```

`unsupported_missing_crossing` and `invalid_relabel` are composition results,
not pathway statuses.

## Iteration 105. Baseline Freeze And Source Census

Freeze the current source authority and the closed predecessor boundary.

Deliver:

- source hashes for load-bearing GRC/LGRC modules;
- explicit `src_diff_empty` and behavior-change state;
- initial pathway-family census;
- statement that Iterations 97-104 remain closed historical design pressure;
- no runtime implementation authority.

Iteration 105 freezes the admitted starting population, not the final pathway
decomposition:

```text
runtime source anchor = passed
closed predecessor boundary = passed
initial twelve-family admission census = passed
final pathway decomposition = unresolved by design
normative contract anchor = pending Iteration 106
Iteration 106 ready = true
```

## Iteration 106. Contract Schema And Registry Seed

Complete a source/authority-surface audit, then freeze the pathway-entry schema
and add entries for every source-backed family admitted by that audit.

Required completeness artifacts:

```text
Phase-8-GRCLGRC-CausalPathwayConsolidationSourceManifest.json
Phase-8-GRCLGRC-CausalPathwayConsolidationUnmappedSurfaceReport.md
```

The source manifest should record repository HEAD and tree, full
`git status --short`, path, SHA-256, surface kind, behavioral/descriptive role,
and exactly one mapping:

```text
pathway
cross-cutting contract
explicit exclusion with reason
```

Schema freeze is blocked until there are zero unclassified behavior-changing
surfaces in the declared V1 scope. The audit must cover runtime state, timing,
topology, identity, lowering/provenance surfaces when directly consumed, and
telemetry contracts where they define observability rather than behavior.

At minimum classify each of these current-source surfaces as a pathway,
cross-cutting contract, or explicit exclusion:

```text
src/pygrc/models/grc_9_v3_state.py
src/pygrc/models/grc_9_v3_sparks.py
src/pygrc/models/lgrc_9_v3.py
src/pygrc/models/lgrc_9_v3_identity.py
src/pygrc/models/lgrc_9_v3_runtime_state.py
src/pygrc/models/lgrc_9_v3_timing.py
src/pygrc/models/lgrc_9_v3_topology.py
src/pygrc/models/grc_9_v3_grcl9v3_lowering.py
src/pygrc/models/grc_9_v3_grcl9v3_provenance.py
src/pygrc/telemetry/lgrc9v3_contract.py
```

This is a minimum set, not a closed allowlist.

Freeze separate authority anchors: committed pre-I106 normative and
predecessor inputs at repository `HEAD`, plus final working-tree bytes for
contracts modified by I106. `HEAD` alone is not enough for modified
specifications, plans, or generation logic, while output bytes must not be
misrepresented as pre-I106 input authority.

Require:

- stage-local authority and derived pathway summaries;
- time, spatial, action, mutation, event-locus, and causal-information scope;
- orthogonal mechanism-ownership, availability, and activation axes;
- configured and producer residue plus naturalization debt;
- retained-history versus consumed-history separation;
- budget, identity, invariant, and fail-closed fields;
- claim ceiling and blocked relabels;
- stable composition and evidence references;
- versioning, source digest, verification revision, and staleness fields.

No entry may infer behavior from another entry or from the registry itself.

Iteration 106 result:

```text
declared V1 source surfaces = 71
pathway-mapped source surfaces = 10
cross-cutting contract surfaces = 40
explicit exclusions = 21
unclassified behavior-changing surfaces = 0
initial pathway families = 12
frozen pathway contracts = 23
authority-bearing stages = 52
runtime behavior changed = false
Iteration 107 ready = true
```

Artifacts:

- [`Phase-8-GRCLGRC-CausalPathwayConsolidationIteration106.md`](./investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration106.md)
- [`Phase-8-GRCLGRC-CausalPathwayConsolidationIteration106.json`](./investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration106.json)
- [`Phase-8-GRCLGRC-CausalPathwayConsolidationIteration106ArtifactFreeze.json`](./investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration106ArtifactFreeze.json)
- [`Phase-8-GRCLGRC-CausalPathwayConsolidationSourceManifest.json`](./investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationSourceManifest.json)
- [`Phase-8-GRCLGRC-CausalPathwayConsolidationUnmappedSurfaceReport.md`](./investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationUnmappedSurfaceReport.md)
- [`grc-lgrc-causal-pathway-contracts.json`](../specs/grc-lgrc-causal-pathway-contracts.json)

## Iteration 107. Source, Test, And Evidence Crosswalk

Resolve every entry to existing source and the strongest available tests,
negative evidence, or bounded experiment evidence. Test presence and test
execution are separate facts.

Evidence attachment is stage-local. A pathway-level row is allowed only when
the cited evidence genuinely covers every load-bearing stage; otherwise use
the stable `(pathway_id, stage_id)` target. Record at least:

```text
pathway_id
stage_id
evidence_scope
pathway_implementation_refs
cross_cutting_dependency_refs
test_source_present
test_source_revision
test_execution_status
test_execution_revision
experiment_evidence_refs
negative_or_blocked_evidence_refs
latest_known_result
evidence_owner
strongest_supported_claim
claim_ceiling
```

Freeze an identity-migration map from the twelve I105 family labels to the 23
I106 pathways:

```text
initial_family_id
final_pathway_ids
migration_relation = unchanged | renamed | split | merged | newly_exposed
historical_evidence_attachment_rule
```

Historical artifacts retain their original terminology. Evidence from a split
family is inspected and attached only to the successor stages it actually
tested. Cross-cutting dependency evidence remains distinct from pathway
implementation evidence, and the 21 explicit exclusions remain exclusions
from this declared V1 closure rather than claims of irrelevance across PyGRC.

The crosswalk may expose maintenance debt. It does not authorize source repair.

Iteration 107 result:

```text
exact I105 family IDs migrated = 12
newly exposed I106 pathways = 5
final pathway contracts covered = 23
authority-bearing stage rows covered = 52
stage rows with current-source executed tests = 52
targeted tests = 528 passed
targeted subtests = 231 passed
bounded V1 exclusions retained = 21
runtime behavior changed = false
Iteration 108 ready = true
```

The crosswalk is additive and does not modify the I106 registry or its artifact
freeze. Configured semantics, producer ownership, diagnostic scope, and utility
scope remain visible even where current-source tests pass. Evidence attachment
does not establish composition.

Artifacts:

- [`grc-lgrc-causal-pathway-evidence-crosswalk.json`](../specs/grc-lgrc-causal-pathway-evidence-crosswalk.json)
- [`Phase-8-GRCLGRC-CausalPathwayConsolidationIteration107.md`](./investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration107.md)
- [`Phase-8-GRCLGRC-CausalPathwayConsolidationIteration107.json`](./investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration107.json)
- [`Phase-8-GRCLGRC-CausalPathwayConsolidationIteration107TestExecution.json`](./investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration107TestExecution.json)
- [`Phase-8-GRCLGRC-CausalPathwayConsolidationIteration107ArtifactFreeze.json`](./investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration107ArtifactFreeze.json)

## Iteration 108. Composition Matrix

Classify representative compositions as lawful native, adapter-mediated,
diagnostic, producer-mediated, unsupported, or invalid relabels.

Iteration 108 starts from grounded endpoints. It no longer asks whether the
I106 pathways exist or whether their named stages have current-source tests;
I107 substantially answers those questions. It asks what happens at the
crossing between independently grounded pathways.

The governing evidence rule is:

> Endpoint test coverage of both pathways is not evidence for the crossing.
> A composition is `lawful_native` only when the crossing itself exists in
> source semantics and current evidence supports that crossing.

If the crossing is not source-current and evidenced, classify it as one of:

```text
lawful_with_explicit_adapter
producer_mediated
diagnostic_only
unsupported_missing_crossing
invalid_relabel
```

Every row is directional and should record:

```text
composition_id
from_pathway_id
to_pathway_id
composition_order
state_identity_mapping
temporal_compatibility
spatial_compatibility
budget_or_invariant_compatibility
authority_retained
authority_transferred
adapter_id
adapter_owner
information_lost_or_compressed
shared_carrier_surface
visible_interaction_term
separable_and_combined_controls
endpoint_evidence_refs
crossing_source_refs
crossing_evidence_refs
crossing_negative_control_refs
endpoint_coverage_used_as_crossing_evidence = false
evidence_status
claim_ceiling
blocked_relabels
```

Each row should distinguish at least state compatibility, time compatibility,
budget compatibility, authority transfer, adapter ownership, information loss
or compression, and composition/crossing evidence.

`A -> B` never implies `B -> A`. A valid row must expose hidden producers,
transfer scope, timescale compatibility, and budget conflicts rather than
relying only on a composition-status label.

The tranche evidence ladder is now:

```text
I106 = complete bounded causal-pathway decomposition
I107 = current-source stage-local evidence grounding
I108 = composition and crossing evidence
I109 = selection semantics
I110 = machine-enforced conformance and maintenance
I111 = independent usability under real pressure consumers
```

At minimum cover:

- GRC flux to synchronous continuity;
- explicit packet to LGRC debit/arrival;
- GRC flux to bounded packet adapter;
- LGRC event to diagnostic reconstruction;
- diagnostic reconstruction to ordinary LGRC claim;
- sink compatibility to route scheduling;
- native arbitration over external candidate scores;
- basin assignment to later transport;
- queue mutation to causal eligibility;
- configured route to native formed role;
- history functional to temporary conductance;
- ledger presence to native Read-Back.

Iteration 108 result:

```text
directional composition rows = 26
lawful native = 10
lawful with explicit adapter = 1
diagnostic only = 2
producer mediated = 4
unsupported missing crossing = 3
invalid relabel = 6
crossing-specific tests = 37 passed
crossing-specific subtests = 5 passed
runtime behavior changed = false
Iteration 109 ready = true
```

The 20 seed cases were reinspected rather than inherited. Six additional
source-current crossings cover packet-to-surface emission, lineage-aware
feedback, collapse-to-surface reabsorption, arbitration-to-multi-basin
diagnostics, restoration lifecycle validation, and explicit GRC-to-LGRC
front-capacity construction. The matrix is representative, directional, and
not a universal pairwise composition algebra.

Artifacts:

- [`grc-lgrc-causal-pathway-composition-matrix.json`](../specs/grc-lgrc-causal-pathway-composition-matrix.json)
- [`GRC-LGRC-CompositionMatrix.md`](../docs/reference/GRC-LGRC-CompositionMatrix.md)
- [`Phase-8-GRCLGRC-CausalPathwayConsolidationIteration108.md`](./investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration108.md)
- [`Phase-8-GRCLGRC-CausalPathwayConsolidationIteration108.json`](./investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration108.json)
- [`Phase-8-GRCLGRC-CausalPathwayConsolidationIteration108TestExecution.json`](./investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration108TestExecution.json)
- [`Phase-8-GRCLGRC-CausalPathwayConsolidationIteration108ArtifactFreeze.json`](./investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration108ArtifactFreeze.json)

## Iteration 109. Pathway Selection Guide

Build a reader-facing decision guide around:

- required temporal semantics;
- whether route is explicit, arbitrated, or expected to form;
- which part of the composition is claimed native;
- what retained relation is required;
- which adapters or producer cuts remain visible.

The guide must be generated or audited against registry, crosswalk, and matrix
references. It cannot become an independent source of pathway facts.

Exercise selection with at least one worked case for every I108 composition
status:

```text
lawful_native
lawful_with_explicit_adapter
diagnostic_only
producer_mediated
unsupported_missing_crossing
invalid_relabel
```

Include deliberately similar demands where one crossing is diagnostic and a
nearby crossing is behavioral. The guide must recover the distinction from
the registered crossing, authority, and evidence records rather than from a
friendly label.

Each worked result should expose:

```text
required temporal semantics
selected pathway IDs
required directional composition ID
composition status
adapter or producer owner
configured residue
claim ceiling
blocked nearby interpretation
missing relation = none | exact composition ID
```

The selection result must distinguish an existing pathway, an existing lawful
composition, and two existing endpoint pathways whose registered crossing is
unsupported. It must not treat `lawful_native` as a maturity score or
`unsupported_missing_crossing` as automatic extension authorization.

Iteration 109 result:

```text
worked selection cases = 10
I108 composition statuses exercised = 6 / 6
diagnostic-versus-behavioral confusion pairs = 1
unregistered pair control = passed
ambiguous registered pair control = passed
I108 predecessor bundle reconciliation = passed
runtime behavior changed = false
Iteration 110 ready = true
```

The guide also distinguishes an unregistered directional pair from a
registered `unsupported_missing_crossing`. It refuses first-match selection
when multiple matrix rows share endpoints. Those controls preserve the I108
representative-scope boundary rather than turning the matrix into a universal
composition algebra.

The accepted I108 predecessor bundle `79bc60...` supersedes the pre-review
working bundle `475ba6...`. The transition changed claim-boundary wording in
the I108 builder and human reports, while the matrix digest, result digest,
37-test receipt, and runtime behavior remained unchanged.

Artifacts:

- [`grc-lgrc-causal-pathway-selection-guide.json`](../specs/grc-lgrc-causal-pathway-selection-guide.json)
- [`GRC-LGRC-CausalPathwayGuide.md`](../docs/reference/GRC-LGRC-CausalPathwayGuide.md)
- [`Phase-8-GRCLGRC-CausalPathwayConsolidationIteration109.md`](./investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration109.md)
- [`Phase-8-GRCLGRC-CausalPathwayConsolidationIteration109.json`](./investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration109.json)
- [`Phase-8-GRCLGRC-CausalPathwayConsolidationIteration109ValidationExecution.json`](./investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration109ValidationExecution.json)
- [`Phase-8-GRCLGRC-CausalPathwayConsolidationIteration108ArtifactBundleSupersession.json`](./investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration108ArtifactBundleSupersession.json)
- [`Phase-8-GRCLGRC-CausalPathwayConsolidationIteration109ArtifactFreeze.json`](./investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration109ArtifactFreeze.json)

## Iteration 110. Conformance Rules And Repository Integration

Define prospective checks without imposing a universal runtime API.

Recommended rule:

> Every newly promoted GRC/LGRC mechanism should reuse an existing pathway
> contract or update the registry, composition relation, claim boundary, and
> conformance evidence before promotion.

Substantial experiments should be able to declare consumed pathway IDs,
producer additions, diagnostic-only surfaces, attempted compositions, and any
unsupported crossing under investigation. These declarations guide review;
they are not mandatory experiment boilerplate when they add no value.

Update reference/spec indexes and claim-boundary guidance.

Require mechanical maintenance fields:

```text
registry_schema_version
entry_version
source_commit
source_digest
last_verified_commit
staleness_state
supersedes
superseded_by
```

A relevant source digest change must produce
`stale_pending_review`; it must not silently preserve trusted status.

Mechanically preserve the I109 selection boundaries:

```text
unregistered pair != unsupported_missing_crossing
ambiguous registered pair != arbitrary first match
diagnostic_only != behavioral
producer_mediated retains producer owner
lawful_with_explicit_adapter retains adapter owner
composition status != maturity
selection != extension authorization
substrate selection != ecological interpretation
all selected IDs resolve to current registry/matrix identities
stale registry, crosswalk, matrix, or predecessor digests fail closed
```

Any behavioral discrepancy found here remains debt and opens a separate repair
identity. Iterations 105-111 do not modify runtime, tests, examples, telemetry,
or behavioral specifications.

Result:

```text
conformance rules = 20 / 20 passed
deliberate negative controls = 20 / 20 failed closed
non-digest rule-isolation controls = 19 / 19 failed closed independently
I109 predecessor reconciliation = passed
legal stale-to-reviewed lifecycle = frozen
pathways = 23
stages = 52
compositions = 26
selection cases = 10
runtime dispatcher created = false
runtime behavior changed = false
Iteration 111 ready = true
```

The conformance policy checks accepted artifact identities, repository-relative
source and evidence references, stage-local authority coordinates, ownership,
composition status, selector projection, staleness, supersession, and the
no-runtime-change boundary. Every rule has a deliberate mutation that must fail
closed. A second pass activates only the intended target rule for each
`CF-002` through `CF-020` mutation, proving that those rules reject
independently of the `CF-001` digest envelope. `CF-001` retains its own global
stale-digest control.

The accepted I109 bundle `e5cc2fb6...` explicitly supersedes the pre-review
working bundle `6e6aa217...`. The machine reconciliation records the old and
new full bundle, selector, and result digests; the changed and added artifact
surfaces; and that selection cases, selection semantics, scientific claims,
and runtime behavior did not change.

The policy also freezes legal re-admission. Relevant drift first blocks the
affected dependency closure as `stale_pending_review`. A reviewed continuation
then reruns the affected I106 classification, I107 evidence, I108 crossings,
and I109 selections; issues versioned successor/supersession artifacts; updates
accepted digests prospectively; and passes full I110 conformance and controls.
Dependency scoping is allowed only where references are complete; uncertain
coverage requires a broader re-audit. A stale artifact cannot authorize its
own re-admission.

The checker validates the frozen architecture artifacts; it does not execute
pathways, repair behavior, authorize extensions, or infer ecological meaning.

Artifacts:

- [`grc-lgrc-causal-pathway-conformance.json`](../specs/grc-lgrc-causal-pathway-conformance.json)
- [`check_grc_lgrc_causal_pathway_conformance.py`](../scripts/check_grc_lgrc_causal_pathway_conformance.py)
- [`Phase-8-GRCLGRC-CausalPathwayConsolidationIteration109ArtifactBundleSupersession.json`](./investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration109ArtifactBundleSupersession.json)
- [`Phase-8-GRCLGRC-CausalPathwayConsolidationIteration110.md`](./investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration110.md)
- [`Phase-8-GRCLGRC-CausalPathwayConsolidationIteration110.json`](./investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration110.json)
- [`Phase-8-GRCLGRC-CausalPathwayConsolidationIteration110ConformanceExecution.json`](./investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration110ConformanceExecution.json)
- [`Phase-8-GRCLGRC-CausalPathwayConsolidationIteration110NegativeControlExecution.json`](./investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration110NegativeControlExecution.json)
- [`Phase-8-GRCLGRC-CausalPathwayConsolidationIteration110ArtifactFreeze.json`](./investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration110ArtifactFreeze.json)

## Iteration 111. Pressure-Consumer Dry Runs And Closeout

Use representative future demands only as acceptance probes:

- RCAE L04 support-side demand;
- boundary-conditioned exchange;
- circulation;
- AP4/AP5;
- shared-medium response;
- route/role formation;
- one future N32 candidate class without selecting N32.

Include deliberately confusable consumer-language demands for:

```text
diagnostic reconstruction versus behavioral update
configured route versus formed route
native arbitration versus native candidate formation
ledger history versus constitutively consumed history
```

For each, ask whether the guide selects an existing pathway, requires an
explicit adapter, or exposes a precise missing substrate relation. Do not
implement the consumer.

Preserve the 22 expert-normalized pressure cases, then add a smaller raw-domain
demand layer. The raw descriptions should not contain pathway, composition,
adapter, or expected-resolution identifiers. Their expert-owned interpretation
may recover an existing pathway or composition, but must also permit:

```text
producer-mediated relation
precise registered missing crossing
declared ambiguity
unregistered_not_classified
```

Include one pathway-only raw demand to prove the guide does not over-compose,
and one genuinely unregistered demand to prove novelty is not relabeled as an
already registered missing crossing.

Add a blind low-context independent replay. Give the replay process only the
guide, registry, composition matrix, and a consumer input containing ordinary
language plus declared substrate constraints. The blind input must not contain
pathway, composition, guide-case, status, adapter, owner, or expected-recovery
answers. Require recovery of:

```text
selected pathway IDs
required adapter and owner
producer cuts
native claim
blocked claims
missing crossing
why nearby alternatives are wrong
```

Freeze the replay artifact before creating or loading the expected-recovery
oracle. A separate validator may then compare the frozen replay with the
physically separate oracle. The validator must not rerun selection or load the
blind input, guide, registry, or matrix.

Close only if the registry and matrix improve selection without erasing
mechanism differences or promoting claims, all pressure consumers route, no
hidden source reading is needed for ordinary selection, ambiguity remains
within a declared threshold, and the independent replay passes.

Result:

```text
expert-normalized pressure descriptions = 22
consumer categories = 11
raw-domain demands = 7
misrouted descriptions = 0
declared unresolved ambiguities = 1 / 1 allowed
unregistered raw demand = correctly unregistered_not_classified
pathway-only raw demand = selected without composition
blind low-context replay = passed
post-freeze oracle validation = passed
hidden source/test reading for ordinary selection = false
I110 artifact-bundle provenance = reconciled
I106-I111 builder path relocation = reconciled
runtime behavior changed = false
tranche closed = true
```

The pressure corpus covers every declared demand and confusion class. It
preserves lawful native, explicit-adapter, producer-mediated, diagnostic,
missing-crossing, invalid-relabel, and ambiguous outcomes rather than treating
them as one maturity order. The sole unresolved ambiguity is deliberate:
arbitration-to-collapse endpoints do not identify direct commit versus
lineage-aware transport without additional crossing semantics.

The raw-domain layer adds seven consumer-language demands and an explicit,
expert-owned demand-to-substrate interpretation step. It includes both a
single-pathway packet-transport result and a route-surplus/arbitration demand
that remains `unregistered_not_classified`. This layer tests usable starting
points without claiming a universal language parser or automatic ontology
discovery.

The blind replay consumed only the machine guide, registry, matrix, and one
bounded L04 support-side input containing declared time, route, and retained-
relation constraints. It uniquely recovered `SEL-05`, the two pathway IDs,
`CMP-20`, installed-producer ownership, residue, claim ceiling, blocked claims,
and rejected nearby alternatives. The input contained no expected answer. The
replay was frozen before a separate validator loaded the recovery oracle. It
read no source, tests, crosswalk, earlier iteration reports, or oracle during
selection. This validates blind bounded post-decomposition selection; it does
not create a natural-language selector.

The accepted I110 bundle identity is explicitly reconciled with its superseded
pre-review identity before I111 consumes it. The reconciliation records a
conformance-strengthening revision without presenting the unavailable older
per-file manifest as reconstructed evidence.

The I106-I111 reproducibility builders live under `scripts/`. The essential
plan, checklist, baseline freeze, and closeout remain at the `implementation/`
root, while source-audit and I106-I111 supporting records live in
`implementation/investigations/causal-pathway-consolidation/`. A single layout
relocation record maps the pre-relocation bundle chain through the builder-only
intermediate chain to the accepted package-layout chain and records that
registry contents, evidence rows, composition classifications, selection
meanings, conformance meanings, pressure outcomes, and runtime behavior did not
change.

Artifacts:

- [`Phase-8-GRCLGRC-CausalPathwayConsolidationIteration111.md`](./investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration111.md)
- [`Phase-8-GRCLGRC-CausalPathwayConsolidationIteration111.json`](./investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration111.json)
- [`Phase-8-GRCLGRC-CausalPathwayConsolidationLayoutRelocation.json`](./investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationLayoutRelocation.json)
- [`Phase-8-GRCLGRC-CausalPathwayConsolidationIteration110ArtifactBundleSupersession.json`](./investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration110ArtifactBundleSupersession.json)
- [`Phase-8-GRCLGRC-CausalPathwayConsolidationIteration111PressureConsumerDescriptions.json`](./investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration111PressureConsumerDescriptions.json)
- [`Phase-8-GRCLGRC-CausalPathwayConsolidationIteration111PressureConsumerExecution.json`](./investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration111PressureConsumerExecution.json)
- [`Phase-8-GRCLGRC-CausalPathwayConsolidationIteration111RawDemandDescriptions.json`](./investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration111RawDemandDescriptions.json)
- [`Phase-8-GRCLGRC-CausalPathwayConsolidationIteration111RawDemandExecution.json`](./investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration111RawDemandExecution.json)
- [`Phase-8-GRCLGRC-CausalPathwayConsolidationIteration111IndependentConsumerBlindInput.json`](./investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration111IndependentConsumerBlindInput.json)
- [`Phase-8-GRCLGRC-CausalPathwayConsolidationIteration111IndependentBlindReplayExecution.json`](./investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration111IndependentBlindReplayExecution.json)
- [`Phase-8-GRCLGRC-CausalPathwayConsolidationIteration111IndependentBlindReplayFreeze.json`](./investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration111IndependentBlindReplayFreeze.json)
- [`Phase-8-GRCLGRC-CausalPathwayConsolidationIteration111IndependentConsumerExpectedRecovery.json`](./investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration111IndependentConsumerExpectedRecovery.json)
- [`Phase-8-GRCLGRC-CausalPathwayConsolidationIteration111IndependentBlindValidationExecution.json`](./investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration111IndependentBlindValidationExecution.json)
- [`Phase-8-GRCLGRC-CausalPathwayConsolidationCloseout.md`](./Phase-8-GRCLGRC-CausalPathwayConsolidationCloseout.md)
- [`Phase-8-GRCLGRC-CausalPathwayConsolidationIteration111ArtifactFreeze.json`](./investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration111ArtifactFreeze.json)
- [`build_phase8_causal_pathway_i111.py`](../scripts/build_phase8_causal_pathway_i111.py)

## Verification

Documentation-only iterations should run:

- JSON parse and schema consistency;
- source-path and source-hash checks;
- Markdown link checks;
- machine-local path audit;
- registry/composition reference integrity;
- source-manifest coverage and zero unclassified behavior-changing surfaces;
- normative-contract and predecessor-evidence anchor hashes;
- staleness-state checks against frozen source digests;
- separation of registry, crosswalk, matrix, and guide authority;
- `git diff --check`;
- protected source envelope check.

Runtime tests are not required when no runtime or test source changes. Existing
test results are evidence pointers, not rerun results, unless explicitly rerun.

## Maximum Claim

The strongest possible closeout claim is:

> A versioned documentation and conformance surface identifies existing
> GRC/LGRC pathways, their distributed authorities, composition boundaries,
> and source/test evidence so future work can select them without hidden
> authority or claim promotion.

This is architecture legibility. It is not a new runtime mechanism, native
admission, Read-Back, agency, ecology, support, role formation, or N32.

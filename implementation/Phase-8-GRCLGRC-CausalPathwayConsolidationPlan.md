# Phase 8 GRC/LGRC Causal Pathway Contract Consolidation Plan

**Status:** Initialized; Iteration 105 source anchor and initial admission census frozen

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

Freeze a separate normative-contract and predecessor-evidence anchor over the
current uncommitted bytes consumed by the registry. `HEAD` alone is not enough
for modified specifications, plans, handoffs, claim boundaries, or
investigation records.

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

## Iteration 107. Source, Test, And Evidence Crosswalk

Resolve every entry to existing source and the strongest available tests,
negative evidence, or bounded experiment evidence. Test presence and test
execution are separate facts. Record at least:

```text
test_source_present
test_source_revision
test_execution_status
test_execution_revision
latest_known_result
evidence_owner
```

The crosswalk may expose maintenance debt. It does not authorize source repair.

## Iteration 108. Composition Matrix

Classify representative compositions as lawful native, adapter-mediated,
diagnostic, producer-mediated, unsupported, or invalid relabels.

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
evidence_status
claim_ceiling
blocked_relabels
```

`A -> B` never implies `B -> A`. A valid row must expose hidden producers,
transfer scope, timescale compatibility, and budget conflicts rather than
relying only on a composition-status label.

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

## Iteration 109. Pathway Selection Guide

Build a reader-facing decision guide around:

- required temporal semantics;
- whether route is explicit, arbitrated, or expected to form;
- which part of the composition is claimed native;
- what retained relation is required;
- which adapters or producer cuts remain visible.

The guide must be generated or audited against registry, crosswalk, and matrix
references. It cannot become an independent source of pathway facts.

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

Any behavioral discrepancy found here remains debt and opens a separate repair
identity. Iterations 105-111 do not modify runtime, tests, examples, telemetry,
or behavioral specifications.

## Iteration 111. Pressure-Consumer Dry Runs And Closeout

Use representative future demands only as acceptance probes:

- RCAE L04 support-side demand;
- boundary-conditioned exchange;
- circulation;
- AP4/AP5;
- shared-medium response;
- route/role formation;
- one future N32 candidate class without selecting N32.

For each, ask whether the guide selects an existing pathway, requires an
explicit adapter, or exposes a precise missing substrate relation. Do not
implement the consumer.

Add a low-context independent replay. Give a participant only the guide,
registry, composition matrix, and one bounded consumer description. Require
recovery of:

```text
selected pathway IDs
required adapter and owner
producer cuts
native claim
blocked claims
missing crossing
why nearby alternatives are wrong
```

Close only if the registry and matrix improve selection without erasing
mechanism differences or promoting claims, all pressure consumers route, no
hidden source reading is needed for ordinary selection, ambiguity remains
within a declared threshold, and the independent replay passes.

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

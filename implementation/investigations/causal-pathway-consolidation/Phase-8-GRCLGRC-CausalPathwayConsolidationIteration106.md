# Phase 8 GRC/LGRC Causal Pathway Consolidation Iteration 106

**Status:** Passed

## Purpose

Iteration 106 freezes the V1 causal-pathway contract schema and replaces the
Iteration 105 twelve-family admission census with a source-complete,
stage-local registry. This is documentation and conformance work. It does not
change GRC9V3, LGRC9V3, tests, examples, or runtime behavior.

## Source Completeness Gate

The audit recursively followed internal `pygrc` imports from all
`grc_9_v3*` and `lgrc_9_v3*` model modules plus the LGRC9V3 telemetry
contract. The resulting source closure was classified before the schema was
accepted:

```text
source surfaces = 71
pathway-mapped surfaces = 10
cross-cutting contracts = 40
explicit exclusions = 21
unclassified surfaces = 0
unclassified behavior-changing surfaces = 0
```

Cross-cutting contracts include state, construction, lowering, provenance,
serialization, and observability surfaces consumed by pathways without
becoming independent causal pathways. Explicit exclusions are transitive
package re-exports or fixture/example providers reached through broad imports
but not consumed as V1 runtime pathways.

The manifest anchors repository branch `main`, HEAD
`e234fde9fd8c2e894eb4eba305ea90f7e4156ae5`, tree
`47631f0d6d7ba9089c6a921702ab40609af63930`, every source hash, the committed
normative inputs, and the closed predecessor evidence. It separately hashes
the final I106 plan, checklist, contract specification, and reproducible build
script from the working tree so those output contracts are not mistaken for
the pre-I106 committed authority.

## Registry Result

```text
Iteration 105 initial families = 12
Iteration 106 frozen pathways = 23
authority-bearing stages = 52
registry schema frozen = true
```

The increase is decomposition, not claim widening. Source inspection exposed
contracts that the initial family names compressed together:

| Initial area | Iteration 106 decomposition |
| --- | --- |
| synchronous GRC transport | synchronous update, identity/basin reconstruction, sink compatibility, hybrid spark refinement, legacy inactive-port growth, front-capacity growth |
| LGRC timing/history | causal-history annotation and fixed-topology eligibility |
| producer feedback | pulse-substrate coupling and feedback eligibility |
| spark/topology | GRC hybrid spark refinement and LGRC causal spark topology integration |
| identity | proper-time evaluation and separately policy-gated acceptance |
| topology records | causal-pulse surface lineage and multi-basin record validation |
| restoration | versioned snapshot, reset, restoration, identity, and replay utility |

Each pathway now has a stage sequence. Every stage declares its trigger, state
transform, direction/funding/eligibility/scheduling/commit/reception
authorities, action and mutation scope, temporal and spatial scope, and
failure/no-op behavior. Pathway-level authority is derived from those stages
and lists every distinct stage authority when authority changes inside the
pathway.

## Frozen Classification

The former single `status_class` has been replaced with three orthogonal axes:

```text
mechanism ownership:
  native | native_with_configured_semantics | producer |
  external_adapter | diagnostic | utility

availability:
  installed | experiment_local | bounded_external | historical | absent

activation:
  default_on | default_off | explicit_call | externally_orchestrated
```

This prevents an installed default-off pathway, native mechanics with supplied
semantics, or a successful producer from being collapsed into one misleading
status. Evidence status remains an Iteration 107 crosswalk fact. Composition
status remains an Iteration 108 matrix fact.

## Authority Boundaries

The registry owns intrinsic pathway and stage facts. The source manifest owns
source closure and source classification. The crosswalk will own source,
specification, test, and evidence relations, including the distinction between
test presence and test execution. The composition matrix will own directional
inter-pathway relations. The guide is derived and cannot establish new facts.

Retained history is separated from history consumed by later constitutive
behavior. Configured residue, producer residue, and naturalization debt remain
separate. Registry records are not evidence and pathway contracts are not
primitive, building-block, motif, or regime admissions.

## Deferred Work

Iteration 106 deliberately leaves these authorities open:

```text
source/test/evidence crosswalk = Iteration 107
directional composition matrix = Iteration 108
selection guide = Iteration 109
pressure-consumer conformance = Iteration 110
independent low-context replay = Iteration 111
```

Any behavioral defect found by those passes must open a separate repair
identity. It cannot be repaired silently inside this consolidation tranche.

## Evidence Consequence And I107 Handoff

The stronger I106 claim is bounded source completeness:

> Within the declared GRC9V3/LGRC9V3 dependency closure, every reached source
> surface and every behavior-changing pathway implementation has been
> classified under the frozen source revision.

This does not mean that 23 mechanisms have been separately validated. They are
23 source-backed pathway contracts extracted from 10 behavior-changing
implementation surfaces and decomposed into 52 authority-bearing stages.

I107 therefore attaches evidence to `(pathway_id, stage_id)` wherever an
artifact proves only one stage. It will also preserve the I105-to-I106 identity
migration, prevent broad-family evidence from automatically flowing to both
successors after a split, and distinguish pathway implementation evidence from
cross-cutting dependency evidence. The 21 exclusions remain bounded to this
declared closure; they are not claims that those files have no role elsewhere
in PyGRC.

The exact I106 output bundle is frozen by SHA-256 in
[`Phase-8-GRCLGRC-CausalPathwayConsolidationIteration106ArtifactFreeze.json`](./Phase-8-GRCLGRC-CausalPathwayConsolidationIteration106ArtifactFreeze.json).
The freeze includes the machine registry, specification, result, report,
source manifest, unmapped-surface report, and reproducible builder. The freeze
record excludes its own hash to avoid recursive identity.

## Claim Boundary

Iteration 106 supports a source-complete V1 pathway schema and registry. It
does not support a universal causal-work API, generic native admission,
causal-work ownership, event-local runtime implementation, catalog admission,
ecological coordination, agency, or N32.

## Result

```text
status = passed
runtime_behavior_changed = false
protected_source_test_example_diff_empty = true
schema_frozen = true
crosswalk_complete = false
composition_matrix_complete = false
selection_guide_complete = false
iteration_107_ready = true
```

Machine result:
[`Phase-8-GRCLGRC-CausalPathwayConsolidationIteration106.json`](./Phase-8-GRCLGRC-CausalPathwayConsolidationIteration106.json)

Artifact freeze:
[`Phase-8-GRCLGRC-CausalPathwayConsolidationIteration106ArtifactFreeze.json`](./Phase-8-GRCLGRC-CausalPathwayConsolidationIteration106ArtifactFreeze.json)

Source manifest:
[`Phase-8-GRCLGRC-CausalPathwayConsolidationSourceManifest.json`](./Phase-8-GRCLGRC-CausalPathwayConsolidationSourceManifest.json)

Frozen registry:
[`grc-lgrc-causal-pathway-contracts.json`](../../../specs/grc-lgrc-causal-pathway-contracts.json)

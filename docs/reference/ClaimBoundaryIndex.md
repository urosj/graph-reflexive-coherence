# Claim Boundary Index

This guide preserves the detailed evidence pointers behind the compact claim
map in the top-level README. It is an index over committed sources, reports,
specs, and implementation closeouts; it is not a new evidence source and does
not relax any claim boundary.

## Runtime Families

Bounded claim: `GRCV2`, `GRCV3`, `GRC9`, `GRC9V3`, and `LGRC9V3` are executable
reference runtime families with committed specs, tests, and package surfaces.

Evidence pointers:

- [Specs index](../../specs/README.md): Start here for the canonical runtime
  specification map and the model-family documents that define each runtime's
  intended behavior.
- [Runtime reference guide](GRC-Runtime-ReferenceGuide.md): Operator-facing
  guide to runtime families, package surfaces, and where implementation claims
  are documented.
- [Runtime model package](../../src/pygrc/models): The actual Python runtime
  implementations and facades behind the reference-family claim.
- [Model tests](../../tests/models): Regression and behavior tests that
  exercise the model families rather than only documenting them.
- [Reset-baseline persistence specification](../../specs/grc-reset-baseline-persistence.md):
  Defines current-state versus declared-reset-baseline persistence, explicit
  legacy rebase, and the prospective provenance boundary.
- [Reset-baseline persistence closeout](../../implementation/corrections/PyGRC-ResetBaselinePersistenceCloseout.md):
  Records the cross-family correction, LGRC9V3 restoration identity v2, test
  scope, and downstream re-admission requirements.
- [Release notes](../../RELEASE-NOTES.md): Publication-snapshot status and
  current package/release boundaries.

Claim ceiling: reference implementation and research runtime surface. This does
not claim a stabilized black-box product API. Reset-aware restoration identity
does not establish raw snapshot byte equality, recovered legacy construction
history, unrestricted behavioral equivalence, or semantic identity.

## Landscape, Telemetry, And Visualization

Bounded claim: landscape-authored seeds can be lowered, stepped, captured, and
rendered. Telemetry, checkpoints, and visualization act as evidence consumers
over runtime artifacts.

Evidence pointers:

- [Quickstart script](../../examples/quickstart/spark_a_cell.py): Minimal
  runnable example showing landscape lowering, runtime stepping, telemetry
  capture, and graph rendering in one path.
- [Quickstart smoke test](../../tests/smoke/test_quickstart.py): Test coverage
  that keeps the quickstart executable rather than documentation-only.
- [Quickstart final graph](../assets/quickstart-graph-final.png): Static
  rendered output from the quickstart, useful for checking what the visual
  evidence layer is supposed to display.
- [Corrected hybrid seed](../../configs/landscapes/seed/grcl9v3-corrected-hybrid-full-composition.seed.yaml):
  Example committed seed input for landscape-authored runtime construction.
- [Telemetry reference guide](Telemetry-ReferenceGuide.md): Field and artifact
  expectations for evidence capture, checkpointing, replay, and reports.
- [Graph visualization reference guide](GraphVisualization-ReferenceGuide.md):
  Visual rendering contracts and what graph images/animations can and cannot
  prove.
- [Phase T implementation plan](../../implementation/Phase-T-ImplementationPlan.md):
  Implementation tranche that introduced the telemetry package and evidence
  capture discipline.
- [Phase V implementation plan](../../implementation/Phase-V-ImplementationPlan.md):
  Implementation tranche that introduced visualization surfaces over telemetry
  artifacts.
- [Visualization tests](../../tests/visualization): Tests that protect visual
  package behavior and artifact-driven rendering.

Claim ceiling: evidence capture and rendering infrastructure. Visuals are not an
independent proof layer and do not establish a complete agent architecture.

## LGRC9V3 Causal-History Substrate

Bounded claim: `LGRC9V3` supports packet/event queue experiments,
causal-history surfaces, topology and child-basin telemetry, and the current
agency-adjacent runtime evidence lanes.

Evidence pointers:

- [LGRC-9 paper](../../papers/2026-05-LGRC-9.md): The theory-facing source for
  the LGRC-9 substrate and why causal-history surfaces matter.
- [LGRC9V3 spec](../../specs/lgrc-9-v3-spec.md): Implementation-facing contract
  for the LGRC9V3 runtime family.
- [LGRC9V3 causal-history reference guide](LGRC9V3-CausalHistory-ReferenceGuide.md):
  Reader-oriented guide to causal-history artifacts, packet/event queues, and
  runtime evidence lanes.
- [Phase 8 LGRC9 closeout](../../implementation/Phase-8-LGRC9-Closeout.md):
  Closeout for the earlier LGRC9 Phase 8 implementation tranche and its claim
  ceiling.
- [Phase 8 multi-basin formation closeout](../../implementation/Phase-8-LGRC9-MultiBasinFormationCloseout.md):
  Closeout for the later multi-basin runtime extension added after N25/N25.1.
- [LGRC9V3 examples](../../examples/lgrc9v3/README.md): Runnable examples and
  visual bundles for causal-history, topology, packet-loop, and multi-basin
  surfaces.
- [LGRC9V3 runtime tests](../../tests/models/test_lgrc_9_v3_runtime.py): Runtime
  test coverage for LGRC9V3 behavior.
- [LGRC9V3 telemetry contract tests](../../tests/telemetry/test_lgrc9v3_contract.py):
  Tests for telemetry contract surfaces used by LGRC9V3 evidence records.

Claim ceiling: causal-history and topology-capable substrate. This does not
claim general agency, intention, biological identity, personhood, sentience, or
native support.

## GRC/LGRC Causal Pathway Contracts

Bounded claim: the repository has consolidated existing GRC/LGRC execution,
diagnostic, producer, topology, and restoration pathways through a common
analytical registry and composition matrix. The common coordinates make
distributed authority visible; they do not define a universal mechanism.

Evidence and contract pointers:

- [Consolidation plan](../../implementation/Phase-8-GRCLGRC-CausalPathwayConsolidationPlan.md):
  Defines the separate Phase 8 documentation/conformance tranche and preserves
  the closed event-local implementation boundary.
- [Iteration 105 baseline](../../implementation/Phase-8-GRCLGRC-CausalPathwayConsolidationBaselineFreeze.md):
  Freezes current source behavior and the initial pathway census.
- [Iteration 106 schema freeze](../../implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration106.md):
  Freezes the source-complete V1 audit, 23 intrinsic pathway contracts, and 52
  stage-local authority records without changing runtime behavior.
- [Causal pathway contract specification](../../specs/grc-lgrc-causal-pathway-contracts.md):
  Defines pathway coordinates, orthogonal status axes, stage contracts, and
  claim boundaries.
- [Machine registry](../../specs/grc-lgrc-causal-pathway-contracts.json):
  Frozen intrinsic pathway entries for conformance work; not evidence.
- [Iteration 107 evidence crosswalk](../../implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration107.md):
  Grounds pathway stages in current source, tests, controls, and bounded
  historical evidence.
- [Iteration 108 composition matrix](../../implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration108.md):
  Separates endpoint evidence from directional crossing evidence.
- [Iteration 109 selection result](../../implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration109.md):
  Validates all six composition statuses plus unregistered and ambiguous
  crossing controls.
- [Iteration 110 conformance result](../../implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration110.md):
  Mechanically validates artifact identities, references, authority,
  ownership, crossing status, selection boundaries, and staleness with 20
  global fail-closed controls and 19 target-only rule-isolation controls.
- [Iteration 111 pressure-consumer result](../../implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration111.md):
  Routes 22 expert-normalized demands across 11 categories, interprets seven
  raw-domain demands without hiding ownership, preserves pathway-only and
  unregistered outcomes, and passes an answer-free blind replay whose recovery
  is validated only after replay freeze. Missing crossings, ambiguity, and
  blocked ecological claims remain explicit.
- [Causal pathway consolidation closeout](../../implementation/Phase-8-GRCLGRC-CausalPathwayConsolidationCloseout.md):
  Closes the documentation/conformance tranche without creating a runtime
  dispatcher, generic admission mechanism, ecological success, or N32 choice.
- [Iteration 109 bundle supersession](../../implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration109ArtifactBundleSupersession.json):
  Reconciles the pre-review and accepted I109 identities while recording that
  selection semantics and scientific claims did not change.
- [Iteration 110 bundle supersession](../../implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration110ArtifactBundleSupersession.json):
  Reconciles the review-reported pre-revision bundle identity with the accepted
  I110 identity while preserving the absence of an unavailable old per-file
  manifest.
- [I106-I111 layout relocation](../../implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationLayoutRelocation.json):
  Maps the original evidence bundles through the builder-only intermediate
  chain to the accepted chain after moving builders to `scripts/` and
  supporting records into the indexed investigation package; it records no
  scientific, conformance-semantic, pressure-outcome, or runtime change.
- [Conformance policy](../../specs/grc-lgrc-causal-pathway-conformance.json):
  Frozen maintenance rules for the registry, crosswalk, composition matrix,
  and selector; not a runtime dispatcher or evidence source.
- [Selection guide](GRC-LGRC-CausalPathwayGuide.md): Derives temporal, route,
  native-claim, retention, and crossing selections without creating source
  facts.
- [Composition matrix](GRC-LGRC-CompositionMatrix.md): Classifies lawful,
  adapter-mediated, diagnostic, producer-mediated, unsupported, and invalid
  compositions.
- [Native admission audit](../../implementation/investigations/event-local-geometry-integration/Phase-8-LGRC9-EventLocalGeometryIntegrationCausalWorkAdmissionPatternAudit.md):
  Source audit that found a recurring distributed grammar but no generic
  native current-source admission block.

Claim ceiling: architecture legibility and composition honesty over existing
mechanisms, with machine-checked maintenance boundaries. Passing conformance is
not behavioral evidence. This does not claim a universal causal-work API,
causal-work owner, generic native admission, route formation, Read-Back,
ecological support, shared-medium coordination, agency, or N32.

## Causal-Pathway Binding And Claim Provenance

Bounded claim: evidence-bearing consumers can bind exact admitted pathways and
executable registered compositions, declare consumer-owned dynamic
alternatives, or retain distinct unregistered work as experimental provenance.
Locks freeze expected architecture before execution; receipts derive actual
use, row-specific witnesses, a use graph, and a conservative claim envelope.

Evidence and usage pointers:

- [Stable binding reference](GRC-LGRC-CausalPathwayBinding-ReferenceGuide.md):
  Public API, exact artifact-field contracts, claim qualification, candidate
  contract, and independent conformance requirements.
- [User and agent guide](GRC-LGRC-CausalPathwayBinding-User-Agent-Guide.md):
  The `select -> bind -> lock -> execute -> seal -> validate` workflow,
  failure interpretation, debugging, and safe extension rules.
- [Runnable binder examples](../../examples/causal_pathway_binding/README.md):
  Admitted pathway, registered composition, dynamic choice, unregistered
  candidate, and direct-unbound comparisons.
- [Binding map](../../specs/grc-lgrc-causal-pathway-bindings.json): Exact
  content-addressed stage and crossing linkage authority.
- [Binding conformance policy](../../specs/grc-lgrc-causal-pathway-binding-conformance.json):
  Independent prospective rules for locks, receipts, witnesses, candidates,
  use graphs, and claim envelopes.
- [Binding acceptance anchor](../../implementation/evidence/causal-pathway-binding/binding-acceptance-anchor.json):
  Reviewed binding-map, source-manifest, semantic, and effect-contract
  identity; its expected digest must arrive through separate trust input.
- [Iteration and audit evidence index](../../implementation/evidence/causal-pathway-binding-iterations/README.md):
  Accepted I112-I125 iteration records and the final independent audit,
  separated from the frozen machine-evidence corpus.
- [Independent I125 audit](../../implementation/evidence/causal-pathway-binding-iterations/CausalPathwayBindingIndependentAudit.md):
  Accepts the modular binder with zero blockers, zero majors, and one
  nonblocking historical-harness retention debt.
- [Evidence layout relocation](../../implementation/evidence/causal-pathway-binding-iterations/CausalPathwayBindingIterationEvidenceLayoutRelocation.json):
  Maps the former top-level iteration and audit paths into the indexed evidence
  package without changing production behavior, claims, or the frozen
  machine-evidence tree.
- [Binding closeout](../../implementation/Phase-8-GRCLGRC-CausalPathwayBindingClaimProvenanceCloseout.md):
  Accepted I112-I125 delivery, modularization, guidance, pressure, and final
  claim boundary.

Claim ceiling: versioned, operation-scoped pathway binding and conservative
claim provenance for represented verified calls. `claim_scope =
bound_invocations_only` does not establish whole-run causal closure, absence of
unbound influences, generic work admission, automatic selection, candidate
promotion, native route formation, agency, Read-Back, or N32.

## N05-N11 Foundation Arc

Bounded claim: N05-N11 record a bounded LGRC agentic-like foundation arc with
explicit ceilings over coherence waves, semantic-route choice, identity
attractor invariance, memory trails, goal-proxy regulation, integration, and
general agentic-like integration.

Evidence pointers:

- [N05-N11 roadmap](../../experiments/N05-N11-LGRC-AgenticLikeFoundationRoadmap.md):
  Overview of the foundation arc and how N05-N11 were sequenced.
- [N10 README](../../experiments/2026-05-N10-lgrc-agentic-like-integration/README.md):
  Experiment entry point for the first agentic-like integration stage.
- [N11 README](../../experiments/2026-05-N11-lgrc-general-agentic-like-integration/README.md):
  Experiment entry point for the broader general agentic-like integration
  stage.
- [N11 final closeout report](../../experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_12_final_closeout_and_handoff.md):
  Human-readable final N11 claim ceiling and handoff state.
- [N11 final closeout JSON](../../experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_12_final_closeout_and_handoff.json):
  Structured final N11 closeout data for exact field-level inspection.

Claim ceiling: bounded foundation evidence. This does not claim unbounded
agency, hidden-steering-free native general intelligence, personhood, or
biological agency.

## N12-N19 Review Arc

Bounded claim: N12-N19 close the artifact-level agency-prerequisite and
native-readiness review stack, including AP3-AP8 classification discipline and
native-readiness boundaries. AP4/AP5 NAT4 gaps remain blockers for later work.

Evidence pointers:

- [Experiments index](../../experiments/README.md): Current experiment catalogue,
  visual evidence gallery, and roadmap/handoff status.
- [N12-N18 roadmap](../../experiments/N12-N18-LGRC-AgencyPrerequisitesRoadmap.md):
  Roadmap for the agency-prerequisite AP arc before the native-readiness review.
- [N12-N18 handoff](../../experiments/N12-N18-LGRC-AgencyPrerequisitesHandoff.md):
  Historical handoff file showing the state before N19's NAT review.
- [N12 closeout](../../experiments/2026-06-N12-lgrc-native-naturalization-and-producer-dissolution/reports/n12_closeout_and_handoff.md):
  Native-naturalization and producer-dissolution review closeout.
- [N13 closeout](../../experiments/2026-06-N13-lgrc-self-maintenance-and-support-seeking-regulation/reports/n13_closeout_and_handoff.md):
  Self-maintenance/support-seeking regulation closeout and bounded handoff.
- [N14 closeout](../../experiments/2026-06-N14-lgrc-consequence-sensitive-route-selection/reports/n14_closeout_and_handoff.md):
  Consequence-sensitive route-selection closeout and AP4-relevant boundary.
- [N15 closeout](../../experiments/2026-06-N15-lgrc-endogenous-proxy-formation/reports/n15_closeout_and_handoff.md):
  Endogenous proxy-formation closeout and AP5-relevant boundary.
- [N16 closeout](../../experiments/2026-06-N16-lgrc-self-environment-boundary/reports/n16_closeout_and_handoff.md):
  Self/environment boundary AP6 closeout.
- [N17 closeout](../../experiments/2026-06-N17-lgrc-closed-boundary-engagement-loop/reports/n17_closeout_and_handoff.md):
  Closed-boundary engagement loop AP7 closeout.
- [N18 closeout](../../experiments/2026-06-N18-lgrc-long-horizon-agentic-like-closure-stress-test/reports/n18_closeout_and_handoff.md):
  Limited h4/L5 AP8 long-horizon stress closeout.
- [N19 closeout JSON](../../experiments/2026-06-N19-lgrc-native-naturalization-review-ap3-ap8/outputs/n19_closeout_and_handoff.json):
  Structured NAT review classification data across AP3-AP8.
- [N19 closeout report](../../experiments/2026-06-N19-lgrc-native-naturalization-review-ap3-ap8/reports/n19_closeout_and_handoff.md):
  Human-readable summary of what N13-N18 do and do not support natively.

Claim ceiling: artifact-level agency-prerequisite and native-readiness review.
This does not claim full native AP3-AP8 ladder generation, agency, native
support, Phase 8 implementation, identity acceptance, or unrestricted autonomy.

## N20-N29 Becoming/Ecology Bridge Arc

Bounded claim: N20-N29 close bounded becoming-primitive evidence through N28
and close N29 at `EB6` / `N29-C6` with a prototype atlas and first ecology probe
contracts. The arc turns earlier experiment evidence into reusable patterns,
composition contracts, and explicit naturalization debt for downstream ecology
work.

Evidence pointers:

- [N20-N29 roadmap](../../experiments/N20-N29-LGRC-BecomingAgencyEcologyRoadmap.md):
  Arc-level map for becoming primitives, producer/naturalization accounting,
  and the ecology bridge.
- [N20-N29 handoff](../../experiments/N20-N29-LGRC-BecomingAgencyEcologyHandoff.md):
  Current handoff state across the becoming/ecology arc.
- [N20 README](../../experiments/2026-06-N20-lgrc-becoming-primitive-producer-translation-contract/README.md):
  Translation contract from agency-of-becoming diagnostics into LGRC-visible
  primitive requirements.
- [N20 closeout](../../experiments/2026-06-N20-lgrc-becoming-primitive-producer-translation-contract/reports/n20_closeout_and_n21_handoff.md):
  Final N20 contract state and N21 handoff.
- [N21 README](../../experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/README.md):
  Withdrawal-resistance and naturalization-depth experiment entry point.
- [N21 closeout](../../experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/reports/n21_closeout_and_n22_handoff.md):
  WR/ND closeout, including what remains naturalization debt.
- [N22 README](../../experiments/2026-06-N22-lgrc-susceptibility-update-durable-geometry-modification/README.md):
  Susceptibility-update and durable-geometry-modification experiment entry
  point.
- [N22 closeout](../../experiments/2026-06-N22-lgrc-susceptibility-update-durable-geometry-modification/reports/n22_closeout_and_n23_handoff.md):
  Durable susceptibility closeout and N23 bridge state.
- [N23 README](../../experiments/2026-06-N23-lgrc-live-continuation-collapse-selection-geometry/README.md):
  Live-continuation collapse and AP4 bridge experiment entry point.
- [N23 closeout](../../experiments/2026-06-N23-lgrc-live-continuation-collapse-selection-geometry/reports/n23_closeout_and_n24_handoff.md):
  Live-continuation collapse closeout and AP4 candidate boundary.
- [N24 README](../../experiments/2026-06-N24-lgrc-abundance-surplus-supported-optionality/README.md):
  Abundance/surplus-supported optionality experiment entry point.
- [N24 closeout](../../experiments/2026-06-N24-lgrc-abundance-surplus-supported-optionality/reports/n24_closeout_and_n25_handoff.md):
  AB/N24-C closeout, including native and producer-assisted flux framing.
- [N25 README](../../experiments/2026-06-N25-lgrc-spark-sub-basin-new-basin-formation/README.md):
  Spark, sub-basin, and early new-basin formation experiment entry point.
- [N25 closeout](../../experiments/2026-06-N25-lgrc-spark-sub-basin-new-basin-formation/reports/n25_closeout_and_n26_handoff.md):
  N25 closeout showing why native multi-basin formation still needed Phase 8
  extension work.
- [N25.1 README](../../experiments/2026-06-N25.1-lgrc9v3-multi-basin-formation-extension-requirements/README.md):
  Requirements experiment for the Phase 8 multi-basin formation extension.
- [N25.1 closeout](../../experiments/2026-06-N25.1-lgrc9v3-multi-basin-formation-extension-requirements/reports/n25_1_closeout_and_phase8_extension_handoff.md):
  Handoff from N25/N25.1 into the implementation tranche.
- [N25.2 README](../../experiments/2026-06-N25.2-lgrc9v3-mb6-validation-bridge/README.md):
  Validation bridge for the implemented Phase 8 multi-basin runtime surfaces.
- [N25.2 closeout](../../experiments/2026-06-N25.2-lgrc9v3-mb6-validation-bridge/reports/n25_2_closeout_and_n26_handoff.md):
  MB6 validation closeout showing native runtime multi-basin evidence after
  the Phase 8 addition.
- [N26 README](../../experiments/2026-06-N26-lgrc-proxy-divergence-proxy-collapse/README.md):
  Proxy divergence/proxy collapse experiment entry point.
- [N26 closeout](../../experiments/2026-06-N26-lgrc-proxy-divergence-proxy-collapse/reports/n26_closeout_and_n27_handoff.md):
  PD closeout and transfer toward configuration/substrate transfer.
- [N27 README](../../experiments/2026-06-N27-lgrc-configuration-substrate-transfer/README.md):
  Configuration/substrate transfer experiment entry point.
- [N27 closeout](../../experiments/2026-06-N27-lgrc-configuration-substrate-transfer/reports/n27_closeout_and_n28_handoff.md):
  CT closeout and handoff to generative/extractive persistence.
- [N28 README](../../experiments/2026-06-N28-lgrc-generative-vs-extractive-persistence/README.md):
  Generative, extractive, competitive, and neutral persistence experiment entry
  point.
- [N28 closeout](../../experiments/2026-06-N28-lgrc-generative-vs-extractive-persistence/reports/n28_closeout_and_n29_handoff.md):
  GE closeout and handoff to the ecology bridge.
- [N29 README](../../experiments/2026-06-N29-lgrc-agentic-ecology-convergence-bridge/README.md):
  Agentic ecology convergence bridge entry point, including prototype atlas and
  bridge-contract scope.
- [N29 closeout JSON](../../experiments/2026-06-N29-lgrc-agentic-ecology-convergence-bridge/outputs/n29_closeout_and_ecology_handoff_i18.json):
  Structured final N29 closeout fields and `EB6` / `N29-C6` classification.
- [N29 closeout report](../../experiments/2026-06-N29-lgrc-agentic-ecology-convergence-bridge/reports/n29_closeout_and_ecology_handoff_i18.md):
  Human-readable final N29 synthesis, prototype atlas, claim ceiling, and
  downstream ecology handoff.
- [Phase 8 multi-basin formation closeout](../../implementation/Phase-8-LGRC9-MultiBasinFormationCloseout.md):
  Runtime implementation closeout that underwrites the native multi-basin
  substrate used by later experiments.

Claim ceiling: bounded becoming-primitive and ecology-bridge evidence. This does
not claim executed ecology runtime, native ant/colony agency, biological agency,
organism/life, resource economy, cooperation/exploitation, native shared-medium
coordination, semantic learning, semantic choice, semantic goals, AP4/AP5 NAT4
gap resolution, Phase 8 completion, or unrestricted autonomy.

## N30 Minimal Shared-Medium Participation

Bounded claim: N30 closes at `N30-C6` as artifact-level minimal shared-medium
participation evidence. The supported relation is:

```text
participant continuity
  -> non-private medium surface perturbation
  -> source-current trace / surface change
  -> later eligibility or susceptibility depends on that changed surface
  -> replay/control validation
```

This makes "shared medium" a source-backed LGRC relation form rather than only
a planning phrase. It can be consumed as a bounded minimal shared-medium
participation candidate and as trace-mediated eligibility primitive /
building-block candidate input for later demand mapping.

Evidence pointers:

- [N30 README](../../experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/README.md):
  Experiment entry point, core question, claim ceiling, and cross-project
  spiral handoff.
- [N30 I8 closeout report](../../experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/reports/n30_closeout_and_spiral_handoff_i8.md):
  Human-readable final closeout, margin context, and claim-boundary summary.
- [N30 I8 closeout JSON](../../experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/outputs/n30_closeout_and_spiral_handoff_i8.json):
  Structured final N30-C6 closeout and post-N30 spiral handoff fields.
- [N30 I7 replay/control report](../../experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/reports/n30_replay_controls_i7.md):
  Replay/control and medium-debt matrix that supports the N30-C5 candidate
  consumed by I8.
- [N30 I7 replay/control JSON](../../experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/outputs/n30_replay_controls_i7.json):
  Structured per-row replay/control evidence across original generative-edge
  and alternative circulatory candidate families.
- [N30 implementation checklist](../../experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/implementation/MinimalSharedMediumParticipationImplementationChecklist.md):
  Iteration-by-iteration evidence record, closeout interpretation, and
  closure-continuation positioning.
- [N30+ shared-medium ecology handoff](../../experiments/N30_plus_LGRC_SharedMediumEcologyHandoff.md):
  Active continuation record through N31, including the cross-project spiral,
  N31 return status, and the explicit RCAE re-admission boundary.

Claim ceiling: bounded artifact-level minimal shared-medium participation
candidate. This does not claim shared-medium coordination, communication,
cooperation, agency, native shared-medium organization, parent-basin
modulation, resonance, sentience, organism/life, ecology regime, executed
agentic ecology runtime, fixed N31 selection, Phase 8 completion, or
unrestricted autonomy.

Continuation boundary at N30 closeout: N30 exposed a candidate N31+ interface
without selecting N31 by default. The subsequent ecology demand pass selected
decay semantics, which N31 now closes below.

## N31 Decay Semantics And RCAE Return

Bounded claim: N31 closes at `N31-C6` after separating six non-equivalent decay
meanings. Native D0a supports route-local formation and persistence at `DR2`
without autonomous weakening. D0b supports an exact-derived fading observable
at `DR3` without causal mediation. B-R and C.2 reach producer-mediated `DR5`
under replay/control validation and receive separate `DR6_contract_only`
consumer contracts.

Evidence pointers:

- [N31 README](../../experiments/2026-07-N31-lgrc9v3-derived-decay-and-primitive-semantics/README.md): Experiment question, semantic taxonomy, current state, and claim boundary.
- [N31 I12 closeout report](../../experiments/2026-07-N31-lgrc9v3-derived-decay-and-primitive-semantics/reports/n31_closeout_and_rcae_return_i12.md): Reader-facing final classification and RCAE re-admission boundary.
- [N31 I12 machine return](../../experiments/2026-07-N31-lgrc9v3-derived-decay-and-primitive-semantics/outputs/n31_closeout_and_rcae_return_i12.json): Structured 107-field return, exact authorities, lane-qualified rungs, semantic-completeness checks, debts, and provider-contract recommendation.
- [N31 B-R contract](../../experiments/2026-07-N31-lgrc9v3-derived-decay-and-primitive-semantics/outputs/n31_i12_closeout_and_rcae_return_artifacts/n31_i12_B_R_reusable_contract.json): Conservative coherence redistribution contract with explicit destination, local route weakening, and producer-owned export lifecycle; organization transfer to the destination remains unsupported.
- [N31 C.2 contract](../../experiments/2026-07-N31-lgrc9v3-derived-decay-and-primitive-semantics/outputs/n31_i12_closeout_and_rcae_return_artifacts/n31_i12_C2_reusable_contract.json): Exact-history susceptibility/effective-geometry contract with producer-owned constitutive insertion.
- [N31 I10 replay/control report](../../experiments/2026-07-N31-lgrc9v3-derived-decay-and-primitive-semantics/reports/n31_added_mechanism_replay_controls_i10.md): Executed DR5 evidence and control matrix consumed by I11/I12.

Claim ceiling: bounded graph-side decay-semantic classification and
authority-qualified RCAE return contracts. `DR6_contract_only` does not mean
cross-context execution or native support. N31 does not establish autonomous
native decay, ordinary D0-R, one general decay law, trail/stigmergy, memory,
communication, coordination, ecology, learning, agency, selfhood, sentience,
organism/life, Phase 8 completion, or automatic RCAE adoption.

Continuation boundary: RCAE P2-I3 may explicitly re-admit the exact B-R or C.2
provider contract under its versioned identity. N31 positive evidence is not
re-admitted. RCAE must generate new ecology-side evidence; a combined B-R+C.2
provider is a new composition requiring separate controls. N32 remains
unselected.

## B1-GR Continuation And Read-Back Verification

Bounded claim: B1-GR closes at `GRV-C6` after a nine-gate verification over
unchanged `GRC9V3`. It accepts bounded fixed-topology formed branches, exact
stage-local current recurrence, bounded L3 causal closure, reduced
continuation/transition diagnostics, and synthetic `C`-dominated neutral
persistence at `GRR2`. Native current recurrence is a real reflexive mechanism
but is not the core Read-Back relation.

Evidence pointers:

- [B1-GR README](../../experiments/2026-08-B1-GR-grc9v3-continuation-readback-verification/README.md): Experiment state, serial gate history, bounded claim summary, and final route position.
- [GRV8 closeout report](../../experiments/2026-08-B1-GR-grc9v3-continuation-readback-verification/reports/b1_grv8_closeout.md): Final human closeout disposition, `GRV-C6` assignment, and non-authorization boundary.
- [GRV8 classification report](../../experiments/2026-08-B1-GR-grc9v3-continuation-readback-verification/reports/b1_grc9v3_verification_report.md): Arrow-by-arrow causal roles, extension routes, contradiction handling, and maximum supported scientific claims.
- [Evidence-grounded successor specification](../../experiments/2026-08-B1-GR-grc9v3-continuation-readback-verification/implementation/GRC9V3ContinuationReadBackVerificationSpecification_EvidenceGrounded_v1.md): Accepted assumption, claim, debt, contradiction, and extension classification over the preserved pre-execution specification.
- [Nine-gate evidence bundle](../../experiments/2026-08-B1-GR-grc9v3-continuation-readback-verification/outputs/evidence_bundle_manifest.json): Non-self-referential manifest over 130 verified artifacts and all nine accepted gate anchors.
- [General next-route handoff](../../experiments/2026-08-B1-GR-grc9v3-continuation-readback-verification/outputs/continuation_readback_next_route_handoff.json): GRC-first route order and positive/negative downstream consumption boundaries.
- [Closeout acceptance anchor](../../experiments/2026-08-B1-GR-grc9v3-continuation-readback-verification/outputs/gates/grv8_closeout_acceptance_anchor.json): Authority-bearing acceptance of the immutable Stage 2 package.

Claim ceiling: bounded verification and route classification for unchanged
`GRC9V3`. B1-GR does not establish a native Read-Back operator, write-back,
closed read/write loop, unique retained projector, full-state classical
Jacobian across categorical boundaries, unrestricted continuation, or global
orbit nonexistence. `GRV-C6` does not authorize a runtime extension, B1-L,
N32, `l04`, memory, learning, agency, organism/life, or any LGRC claim.

Continuation boundary: the accepted handoff orders unchanged-GRC
constructibility first, target-conditioned selectable GRC extensions second,
analysis/identifiability debt third, and LGRC-specific investigation fourth.
Closing B1-GR selects none of those routes automatically. B1-L is a deferred
LGRC-specific scaffold, not the umbrella handoff.

## GRCv4/GRC9v4 Constitutive Design

Bounded claim: B2-GR closes its preregistered unchanged-`GRC9V3`
constructibility search at `B2-C6` without a confirmed retained-carrier
candidate, a new GRR rung, or an extension selection. The subsequent D0-D10.2
constitutive investigation accepts a profile-explicit design population and
earns, for that current population, the factorization:

```text
GRCv4 ->[nine-port specialization] GRC9v4 ->[disabled V4 profile] GRC9v3
```

The accepted D10 topology contains 39 claims across normative, optional,
conditional, open, and negative classes. D10.2 binds those claims to 67
normatively load-bearing parent objects and 152 normative equation/contract
rows, with no promotion-pending row. General GRC content is separated from
deliberate GRC9 compatibility and intrinsically nine-port mechanics.

Evidence pointers:

- [B2-GR accepted boundary](../../experiments/2026-08-B2-GR-grc9v3-retention-mediation-constructibility/README.md): Bounded unchanged-runtime search result and its non-global negative boundary.
- [Constitutive design investigation](../../implementation/investigations/grc9v4-constitutive-design/README.md): D0-D10.2 lineage, current disposition, candidate/realization history, and continuation route.
- [D10 design synthesis](../../implementation/investigations/grc9v4-constitutive-design/decisions/D10DesignSynthesisAndSpecWritingDecision.md): Claim topology, profile grammar, architecture population, and specification authorization decision.
- [D10.2 full substrate-provenance audit](../../implementation/investigations/grc9v4-constitutive-design/decisions/D10_2FullSubstrateProvenanceAndPromotionAudit.md): Equation/contract-level GRC promotion, GRC9 specialization, disabled reduction, and final factorization evidence.
- [D10.2 machine record](../../implementation/investigations/grc9v4-constitutive-design/decisions/D10_2FullSubstrateProvenanceAndPromotionAudit.json): Accepted structured disposition, exact counts, controls, identities, and digest.
- [Constitutive design plan](../../implementation/investigations/grc9v4-constitutive-design/GRC9V4ConstitutiveDesignPlan.md): Gate sequence, accepted current-population route, and successor reopening rules for the still-unwritten V4 specifications.
- [Accepted exploratory side tool](../../implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/README.md): Read-only forensic reconstruction, lineage navigation, and precomputed structural-counterfactual playback over the accepted D0-D10.2 snapshot. It is a consumption surface, not additional scientific evidence or specification/runtime conformance.

Claim ceiling: accepted design, claim-topology, lifecycle, and substrate-
provenance closure for the current D10 initial specification population. It
does not establish a V4 runtime, implementation conformance, formed-branch
reachability, numerical spectra or stability, unique candidate/realization
preference, core-theory uniqueness, or a future-exhaustive V4 taxonomy. It
does not establish that nine-port mechanics are unnecessary; those mechanics
remain GRC9 specialization content.

Continuation boundary: write the GRCv4 normative specification first, then the
substantive GRC9v4 nine-port specialization with exact disabled-profile
compatibility to GRC9v3. Any future profile outside the accepted D10 population
must reopen provenance and the earliest affected accepted contract.
Implementation planning and `src/` changes remain unauthorized.

## Forward Catalog Orientation

The N30+ roadmap package is a planning and ontology layer for future
experiments. It defines catalog layers, candidate directions, debt/failure
language, and claim-hygiene expectations, but it is not itself a source of
evidence for future N31+ claims. N30 is the first source-backed closeout under
that roadmap, and N31 is the first completed demand-to-return cycle.

Pointers:

- [N30+ Experiment Catalog Roadmap](../../experiments/N30_plus_experiment_catalog_roadmap.md):
  Catalog ontology for primitives, building blocks, motifs, regimes, debt, and
  claim discipline after N29/N30.
- [N30+ Candidate Directions](../../experiments/N30_plus_candidate_directions.md):
  Candidate shared-medium ecology directions for future experiments.
- [N30+ Shared-Medium Ecology Handoff](../../experiments/N30_plus_LGRC_SharedMediumEcologyHandoff.md):
  Active handoff through the N31 closeout and back to RCAE re-admission.

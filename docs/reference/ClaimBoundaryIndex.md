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
- [Release notes](../../RELEASE-NOTES.md): Publication-snapshot status and
  current package/release boundaries.

Claim ceiling: reference implementation and research runtime surface. This does
not claim a stabilized black-box product API.

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

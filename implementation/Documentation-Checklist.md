# Documentation Checklist

Status: complete through Iteration 9; Iteration 10 draft opened

This checklist tracks the operator-facing reference documentation layer. The canonical home for user/reference guides is `docs/reference/`. The `implementation/` directory remains the engineering-history and phase-planning record.

## Documentation Principles

- [x] Keep implementation history separate from operator reference.
- [x] Store reference/user guides under `docs/reference/`.
- [x] Preserve existing implementation guides while adding canonical docs copies.
- [x] Every reference guide states scope, audience, authority boundaries, supported APIs/CLIs, output artifacts, examples, parameters, limitations, and validation commands.
- [x] Every guide links to the implementation plan/checklist or evidence sessions that justify the documented behavior.
- [x] Every guide distinguishes accepted behavior from legacy, diagnostic, provisional, or future-refinement behavior.

## Iteration 1: Docs Tree And Existing Guides

- [x] Create `docs/`.
- [x] Create `docs/reference/`.
- [x] Add top-level documentation index.
- [x] Add reference-guide index.
- [x] Copy `LandscapeInference-ReferenceGuide.md` into `docs/reference/`.
- [x] Copy `Motion-ReferenceGuide.md` into `docs/reference/`.
- [x] Update implementation plan/checklist links to point at the docs reference copies.
- [x] Verify all copied guide links remain valid or have a documented migration note.

## Iteration 2: Landscape Language Reference

- [x] Add `docs/reference/LandscapeLanguage-ReferenceGuide.md`.
- [x] Document `LandscapeSeed` vocabulary, primitive roles, extensions, non-claims, and source/runtime boundary.
- [x] Include API examples for loading, validating, saving, and inspecting seeds.
- [x] Include script/CLI examples for common seed workflows.
- [x] Link canonical seed directories, including motion seeds under `configs/landscapes/seed/motion/`.

## Iteration 3: Landscape Compiler And Lowering Reference

- [x] Add `docs/reference/LandscapeCompiler-ReferenceGuide.md`.
- [x] Document GRCL/landscape compilation direction: authored examples to source schema to lowered runtime state.
- [x] Document lowering manifests, provenance caches, expected-region caches, and replay sessions.
- [x] Include examples for GRCL-9, GRCL-9V3, and landscape-inference seed workflows where available.

## Iteration 4: Telemetry Reference

- [x] Add `docs/reference/Telemetry-ReferenceGuide.md`.
- [x] Document step rows, event rows, run summaries, checkpoint packs, replay digests, and family extensions.
- [x] Cover GRCV3, GRC9, GRC9V3, GRCL, landscape inference, and motion telemetry surfaces.
- [x] Include script examples for loading telemetry, replaying sessions, and comparing artifacts.

## Iteration 5: Graph Visualization Reference

- [x] Add `docs/reference/GraphVisualization-ReferenceGuide.md`.
- [x] Document static graph outputs, dense/sparse graph modes, animation outputs, overlays, and visual claim boundaries.
- [x] Include examples for representative GRC9/GRC9V3 visualization, landscape inference visualization, and motion visualization.

## Iteration 6: GRC Runtime Reference

- [x] Add `docs/reference/GRC-Runtime-ReferenceGuide.md`.
- [x] Document supported runtime families: GRCV2, GRCV3, GRC9, GRC9V3, and extension status.
- [x] Document `.step()` loop shape, parameters, capabilities, front/pressure-boundary growth semantics, coarse graining, and known legacy modes.
- [x] Include minimal API examples for constructing states, running steps, and recording telemetry.

Status: complete. The guide records the shared `GRCModel` API, family-specific
step-loop surfaces, accepted corrected front/pressure-boundary growth semantics,
legacy broad-growth boundaries, GRCV3 opt-in frontier birth behavior,
GRC9/GRC9V3 coarse-graining and Split usage, telemetry capture examples, and
runtime validation commands.

## Iteration 7: GRCL Reference

- [x] Add `docs/reference/GRCL-ReferenceGuide.md`.
- [x] Document GRCL-9 and GRCL-9V3 source layers, vocabulary, lowering controls, deterministic examples, and selector validation.
- [x] Explain legacy growth quarantine and corrected front/pressure-boundary semantics.
- [x] Include replay commands for source-language sessions.

Status: complete. The guide records GRCL-9 and GRCL-9V3 schema modules,
construct vocabularies, fixture names, lowering manifests, growth semantics,
legacy quarantine, replay commands, selector validation commands, output
artifacts, API examples, and validation commands.

## Iteration 8: Catalogs And Evidence Reference

- [x] Add `docs/reference/Catalogs-And-Evidence-ReferenceGuide.md`.
- [x] Document mechanism ledgers, selector catalogs, reviewed motif catalogs, motion catalogs, confidence labels, and diagnostic-only records.
- [x] Include examples for locating accepted vs. diagnostic vs. rejected evidence.

Status: complete. The guide records the evidence authority order, common review
labels, mechanism ledgers, hypothesis catalogs, selector validation artifacts,
GRC9/GRC9V3 reviewed runtime catalogs, GRCL-9/GRCL-9V3 lowered catalogs,
corrected growth supersession, landscape-inference reports, motion reviewed
catalogs, current evidence anchors, and validation commands.

## Iteration 9: Cross-Link Closeout

- [x] Add cross-links from `docs/README.md` to every completed guide.
- [x] Add cross-links from relevant implementation checklists to the canonical guide paths.
- [x] Run a link/path sanity check with `rg` and targeted file existence checks.
- [x] Record remaining missing guides and planned follow-up order.

Status: complete. `docs/README.md` and `docs/reference/README.md` list every
completed guide, `implementation/ImplementationPhases.md` now points to the
canonical reference index and major guide paths, stale "will cover" forward
references were replaced with current links, and local markdown/file link
checks passed.

Remaining missing guides: none in the current documentation checklist. Future
guide candidates should be opened as new checklist iterations rather than
reopening this closeout.

## Iteration 10: GRC/LGRC Causal Pathway Reference

- [x] Complete the [causal pathway selection guide](../docs/reference/GRC-LGRC-CausalPathwayGuide.md).
- [x] Complete the [causal pathway composition matrix](../docs/reference/GRC-LGRC-CompositionMatrix.md).
- [x] Freeze the supporting registry and source/test/evidence crosswalk under the
  separate Phase 8 consolidation tranche.
- [x] Validate that the guides preserve configured, producer-mediated,
  diagnostic, and native-behavior distinctions.

Status: selection and conformance surfaces complete. Phase 8 Iteration 110 froze
the source-complete V1 audit, 23-pathway registry, 52-row stage-local evidence
crosswalk, 26-row directional composition matrix, evidence-derived worked
selection guide, and 20-rule machine conformance policy. Iteration 111 then
closed the tranche with 22 expert-normalized pressure descriptions across 11
categories, seven raw-domain demands, and one answer-free blind replay frozen
before separate oracle validation. The raw layer includes pathway-only and
genuinely unregistered outcomes. The conformance surface includes 20 global
negative controls, 19 target-only rule-isolation controls, explicit I109/I110
provenance reconciliation, and versioned stale-to-reviewed re-admission.
The six I106-I111 reproducibility builders are stored under `scripts/`, with
their source-audit and supporting evidence indexed under
`implementation/investigations/causal-pathway-consolidation/` and their
path-only evidence-identity migrations recorded explicitly.

## Iteration 11: GRC/LGRC Causal Pathway Binding Reference

- [x] Add the [binding and claim-provenance guide](../docs/reference/GRC-LGRC-CausalPathwayBinding-ReferenceGuide.md).
- [x] Explain the Knowledge, Binding, and Execution planes.
- [x] Document admitted pathway/composition binding and explicit candidates.
- [x] Document locks, receipts, use graphs, dynamic choice, and conformance.
- [x] Preserve unbound compatibility while rejecting unbound claim provenance.
- [x] Add the [binding user and agent guide](../docs/reference/GRC-LGRC-CausalPathwayBinding-User-Agent-Guide.md).
- [x] Add [five runnable binder examples](../examples/causal_pathway_binding/README.md).
- [x] Document the stable public surface, exact artifact fields, final
      candidate contract, and operation-scoped provenance warning.

Status: complete through Phase 8 Iteration 125. The binding layer consumes the
closed I105-I111 knowledge plane and delegates unchanged mechanism-specific
runtime callables. Accepted causal-pathway claims require a valid receipt;
unrelated code and internal mechanism calls do not acquire binding boilerplate.
The stable reference and task-oriented guide explicitly preserve the
`bound_invocations_only` claim boundary. Iteration 125 independently accepted
the I124 guidance with I125-N01 retained as nonblocking evidence-reproducibility
debt.

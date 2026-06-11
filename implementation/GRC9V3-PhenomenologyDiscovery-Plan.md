# GRC9V3 Phenomenology Discovery Plan

This document defines the downstream discovery track for `GRC9V3` hybrid
phenomenology.

The execution checklist is
[`GRC9V3-PhenomenologyDiscovery-Checklist.md`](./GRC9V3-PhenomenologyDiscovery-Checklist.md).

Replayable experiment sessions should be indexed in
`outputs/grc9v3/phenomenology_discovery/ExperimentalLog.md`.
Session artifacts should live under
`outputs/grc9v3/phenomenology_discovery/sessions/S0001/`.

This track begins after:

- core Phase 7 has made `GRC9V3` executable,
- Phase T-GRC9V3 has made hybrid runtime state observable through telemetry,
- Phase V-GRC9V3 has made saved telemetry and checkpoints inspectable through
  deterministic visualization.

The goal is to discover and name repeatable `GRC9V3` motifs from theory-derived
runtime structures and their telemetry evidence. It is not a GRCL/source-seed
track. Source-language claims should wait until reviewed runtime motifs exist.

## Purpose

GRC9V3 phenomenology discovery should identify repeatable hybrid structures and
windows in generated `GRC9V3` runs:

- hybrid spark candidate windows,
- hybrid spark completion after mechanical expansion and child-basin
  stabilization,
- Appendix E style cell-division trajectories,
- mechanical expansion with semantic hierarchy update,
- choice/collapse regimes after expansion,
- growth loci on inactive GRC9 ports under GRCV3 semantic state,
- quadrature-budget correction regimes on a changing port graph,
- row-basis Hessian backend comparison effects,
- signed-crossing spark behavior when the runtime capability is enabled,
- transport-driven basin and successor changes,
- coarse-cache invalidation after hybrid topology or value changes,
- quiescent hybrid controls that should not spark, expand, grow, or collapse.

Discovery outputs should be:

- a mechanism ledger,
- a seeded runtime-structure hypothesis catalog,
- deterministic pure-runtime fixture lanes,
- replayable telemetry and checkpoint sessions,
- selector reports comparing predicted and observed signatures,
- visual indexes for reviewed candidates,
- and a reviewed motif catalog.

The reviewed catalog now feeds the GRCL/source-seed layer for `GRC9V3`, but
that layer remains separate from this discovery responsibility. Discovery
itself stays runtime-facing; the downstream source/lowering closeout is
[GRCL-9V3-Handoff.md](./GRCL-9V3-Handoff.md).

## Inputs

Authoritative implementation and contract inputs:

- [`Phase-7-ImplementationPlan.md`](./Phase-7-ImplementationPlan.md)
- [`Phase-7-EquationMap.md`](./Phase-7-EquationMap.md)
- [`Phase-7-StepLoop.md`](./Phase-7-StepLoop.md)
- [`Phase-7-RepresentativeRuntime.md`](./Phase-7-RepresentativeRuntime.md)
- [`Phase-7-Closeout.md`](./Phase-7-Closeout.md)
- [`Phase-T-GRC9V3-ImplementationPlan.md`](./Phase-T-GRC9V3-ImplementationPlan.md)
- [`Phase-T-GRC9V3-TelemetryContract.md`](./Phase-T-GRC9V3-TelemetryContract.md)
- [`Phase-T-GRC9V3-RepresentativeTelemetry.md`](./Phase-T-GRC9V3-RepresentativeTelemetry.md)
- [`Phase-T-GRC9V3-Closeout.md`](./Phase-T-GRC9V3-Closeout.md)
- [`Phase-V-ImplementationPlan.md`](./Phase-V-ImplementationPlan.md)
- [`Phase-V-GRC9V3-ImplementationPlan.md`](./Phase-V-GRC9V3-ImplementationPlan.md)
- [`../specs/grc-9-v3-spec.md`](../specs/grc-9-v3-spec.md)
- [`../specs/grc-9-spec.md`](../specs/grc-9-spec.md)
- [`../specs/grc-v3-spec.md`](../specs/grc-v3-spec.md)

Available representative lane:

- `outputs/phase-t-grc9v3/representative/appendix_e_cell_division/`

That lane proves the telemetry and visualization machinery. It can be used as a
reference artifact, but it should not define the whole search space. Discovery
must build its own structures by reasoning from the Phase 7 equations and step
loop to the graph and state conditions that should emit each target
phenomenon.

## Boundaries

This discovery track must not claim:

- GRCL/source-language expressiveness for GRC9V3,
- source lowering correctness,
- Lorentzian causal-layer behavior,
- observer-local semantics,
- FRC sigma-layer behavior,
- GRC9 boundary `barrier` or `ghost` semantics unless the runtime capability
  is implemented and telemetry exposes it,
- parent-family semantics without ownership tags,
- a motif from a visual image without matching telemetry evidence.

Pure runtime examples may include explicit synthetic initial state, port graph
structure, coherence, basin fields, hierarchy fields, and configuration
parameters. They must not include source constructs or source-level meaning.

## Ownership Rule

Every mechanism and motif must state which layer owns the evidence:

- `grc9_mechanical`: nine-port chart, saturation, mechanical expansion,
  reassignment, inactive-port growth, port graph transport.
- `grcv3_semantic`: signed Hessian, basin seed validity, hierarchy,
  choice/collapse, quadrature budget interpretation.
- `grc9v3_hybrid`: behavior that exists only when the GRC9 substrate and GRCV3
  semantic lift interact, such as saturation plus basin/Hessian spark gates,
  child-basin stabilization after mechanical expansion, and hierarchy-aware
  port graph refinement.

Discovery should not flatten a hybrid event into "GRC9 plus metadata" or
"GRCV3 on another graph."

## Runtime Gap Constraints

Currently testable:

- saturation plus signed-Hessian hybrid spark candidates,
- row-basis diagonal Hessian spark gates,
- weighted-least-squares Hessian comparison backend when selected,
- mechanical expansion after a hybrid candidate,
- post-expansion child-basin stabilization,
- completed hybrid sparks,
- hierarchy update after stabilized refinement,
- choice/collapse logic after expansion,
- inactive-port growth when enabled,
- prune boundary behavior,
- quadrature budget enforcement,
- coarse-cache invalidation,
- graph checkpoints with GRC9V3 overlays.

Capability-gated:

- signed-crossing spark criteria,
- boundary barrier or ghost behavior,
- richer Hessian/backend comparison claims beyond the implemented backends,
- long-window growth plus collapse cascades if the runtime fixture cannot
  preserve them deterministically.

Deferred or out of scope:

- GRCL/source lowering,
- source vocabulary for hybrid phenomena,
- Lorentzian causal interpretation,
- observer-local views,
- FRC sigma-layer behavior.

Mechanisms outside the currently testable set should still appear in the
mechanism ledger, but their `runtime_status` must be `capability_gated`,
`deferred`, or `out_of_scope`, and they must not produce accepted motifs.

## Theory-First Structure Deduction

Each target phenomenon should start as an inverse-design question:

```text
Phase 7 mechanism -> hybrid graph/state precondition -> predicted telemetry
signature -> deterministic GRC9V3 runtime seed -> observed validation
```

Examples:

- Hybrid spark:
  - infer the saturated nine-port node, basin-interior condition, signed
    Hessian degeneracy, and optional signed-crossing history needed for a
    candidate.
  - generate a runtime state whose port occupancy and basin fields realize
    those gates.
  - predict `hybrid_spark_state`, event-row spark evidence, and Hessian fields.

- Completed hybrid spark:
  - infer the expansion module and child-basin stabilization conditions needed
    after a candidate.
  - generate a candidate whose mechanical expansion should produce stable
    daughter sinks.
  - predict candidate, expansion, completed-spark, hierarchy, and budget
    evidence in order.

- Choice/collapse:
  - infer post-expansion identity geometry with competing sinks and a
    deterministic compatibility winner.
  - generate a state where choice is detected before continuity and collapse is
    expected in a bounded window.
  - predict `choice_collapse` summaries and choice/collapse event rows.

- Growth:
  - infer inactive GRC9 ports with high outward pressure in a semantic basin
    context.
  - generate a port graph where growth is enabled and below/above-threshold
    controls differ only in pressure or `lambda_birth`.
  - predict growth events, child attachment, and post-growth cache invalidation.

- Hessian backend comparison:
  - infer a structure where row-basis diagonal and weighted-least-squares
    Hessian summaries should disagree meaningfully.
  - run paired fixtures with the same graph and different `hessian_backend`.
  - predict different spark-gate or basin-seed outcomes.

The generated runtime state is the experiment. Existing representative lanes
prove machinery; they are not enough to define the catalog.

## Hybrid Seed Family Catalog

The first seed catalog should cover the following runtime families.

Hybrid spark gate seed:

- saturated candidate node with all nine ports occupied,
- controllable signed-Hessian minimum,
- basin-interior pass/fail controls,
- optional previous signed-Hessian history when the capability is enabled,
- expected candidate event and `hybrid_spark_state` activation.

Spark-to-expansion seed:

- hybrid candidate that mechanically expands,
- controlled target effective degree and distribution mode,
- expected expansion evidence, module overlays, and budget correction summary.

Appendix E cell-division seed:

- one spark producing two daughter sinks or sink-capable regions,
- child-basin stabilization evidence,
- hierarchy parent/children update,
- expected Appendix E run-summary block and visual graph sequence.

Choice/collapse seed:

- post-expansion or synthetic two-attractor geometry,
- deterministic compatibility-score separation,
- negative control with ambiguous compatibility,
- expected choice and collapse evidence.

Growth pressure seed:

- inactive parent port with high outward pressure,
- low-pressure or low-`lambda_birth` negative control,
- expected growth event, child node attachment, and topology mutation.

Budget-preservation seed:

- expansion, growth, or continuity step with controlled budget perturbation,
- uniform-shift and simplex-projection policy controls when available,
- expected budget-before/after and correction path evidence.

Hessian-backend comparison seed:

- fixed graph and coherence field,
- paired row-basis diagonal and weighted-least-squares backend runs,
- expected difference in signed-Hessian summaries, basin seed validity, or
  spark-gate outcome.

Transport/basin rerouting seed:

- asymmetric conductance port graph with competing successor paths,
- expected successor-map, sink, basin, and flux-summary changes.

Coarse-cache invalidation seed:

- topology or value mutation that must invalidate or refresh coarse/cache
  surfaces,
- expected coarse invalidation reason after expansion, growth, or continuity.

Quiescent hybrid control:

- stable port graph with no saturated spark source, no Hessian degeneracy, low
  outward pressure, and no choice/collapse ambiguity,
- expected no lifecycle events beyond routine observables.

## Seed Generator Contract

Seed generators should be deterministic helpers that return a `GRC9V3`-ready
initial state plus metadata. The exact code location can be chosen during
implementation, but the public shape should be stable:

```python
seed = generate_grc9v3_seed(
    seed_family="hybrid_spark_gate",
    seed_name="hybrid_spark_gate_positive_control",
    parameters={...},
)
```

The returned object should include:

- a `GRC9V3` initial state or constructor payload,
- `seed_family`,
- `seed_name`,
- `seed_parameters`,
- `expected_runtime_config`,
- `ownership_tags`,
- `graph_preconditions`,
- `state_preconditions`,
- `predicted_signatures`,
- `negative_control_of` when applicable,
- `perturbation_of` when applicable.

Common controllable parameters:

- node count and live edge list,
- nine-port occupancy and saturation pattern,
- inactive-port pattern,
- conductance assignment,
- coherence placement and quadrature budget target,
- basin ids, basin masses, sink set, and hierarchy depth,
- row-basis gradient and signed-Hessian target regimes,
- `hessian_backend`,
- spark threshold and signed-crossing capability flag,
- expansion distribution mode and target effective degree,
- child-basin stabilization threshold,
- choice/collapse compatibility separation,
- growth enablement and `lambda_birth`,
- boundary mode,
- budget preservation policy,
- coarse-cache mode.

Pre-run validation checklist:

- every edge respects the nine-port chart constraints,
- graph connectivity matches the hypothesis,
- saturation and inactive-port counts match the intended control,
- basin and sink fields are internally consistent,
- hierarchy fields do not claim stabilization before the run unless the fixture
  explicitly starts post-expansion,
- coherence and quadrature budget target are finite and fixed,
- requested capabilities are present in `GRC9V3.list_capabilities()`,
- expected telemetry fields exist in the Phase T-GRC9V3 contract,
- positive and negative controls differ in the smallest useful parameter set.

## Evidence Surfaces

Primary evidence comes from Phase T-GRC9V3 telemetry.

Step-row surfaces:

- `family_extensions.grc9v3.lane_context`
- `family_extensions.grc9v3.backend_config`
- `family_extensions.grc9v3.port_chart`
- `family_extensions.grc9v3.row_basis_differential`
- `family_extensions.grc9v3.hybrid_tensor`
- `family_extensions.grc9v3.transport`
- `family_extensions.grc9v3.identity_basin`
- `family_extensions.grc9v3.hybrid_spark_state`
- `family_extensions.grc9v3.hierarchy_state`
- `family_extensions.grc9v3.choice_collapse`
- `family_extensions.grc9v3.growth_state`
- `family_extensions.grc9v3.budget_correction`
- `family_extensions.grc9v3.coarse_cache`

Event-row surfaces:

- event domain,
- lifecycle stage,
- ownership,
- mutation flags,
- candidate/expansion/completion/choice/collapse/growth/budget/coarse evidence
  groups when present.

Run-summary surfaces:

- lifecycle event counts,
- final backend, port, differential, identity, hierarchy, choice/collapse,
  growth, budget, and coarse summaries,
- representative Appendix E summary when applicable.

Graph-checkpoint surfaces:

- node overlay,
- port overlay,
- edge overlay,
- module overlay,
- choice overlay,
- checkpoint links for exact or nearest-before/after motif windows.

Visualization surfaces:

- trajectory panels,
- event timelines,
- report panels,
- graph snapshot sequences,
- graph animation,
- final interactive graph view.

Visualizations are inspection aids. They support a motif only when the telemetry
surface already contains the predicted evidence.

## Selector Field Mapping

Initial selectors should be field-backed and should report `missing_surface`
instead of inferring from images or live model state.

| Selector | Surface | Field Path Or Query | Type |
|---|---|---|---|
| saturated node count | `steps.jsonl` | `family_extensions.grc9v3.port_chart.saturated_node_count` | int |
| hessian backend | `steps.jsonl` | `family_extensions.grc9v3.backend_config.hessian_backend` | string |
| signed Hessian minimum | `steps.jsonl` | `family_extensions.grc9v3.row_basis_differential.signed_hessian_min` | float |
| current min signed Hessian | `steps.jsonl` | `family_extensions.grc9v3.row_basis_differential.current_min_signed_hessian_min` | float |
| previous min signed Hessian available | `steps.jsonl` | `family_extensions.grc9v3.row_basis_differential.previous_min_signed_hessian_available` | bool |
| signed Hessian history pruned count | `steps.jsonl` | `family_extensions.grc9v3.row_basis_differential.signed_hessian_history_pruned_count` | int |
| WLS Hessian available | `steps.jsonl` | `family_extensions.grc9v3.row_basis_differential.weighted_least_squares_hessian_available` | bool |
| tensor anisotropy | `steps.jsonl` | `family_extensions.grc9v3.hybrid_tensor.tensor_anisotropy_max` | float |
| tensor trace mean | `steps.jsonl` | `family_extensions.grc9v3.hybrid_tensor.tensor_trace_mean` | float |
| row mismatch maximum | `steps.jsonl` | `family_extensions.grc9v3.hybrid_tensor.row_mismatch_sum_max` | float |
| tensor hotspot sample | `steps.jsonl` | `family_extensions.grc9v3.hybrid_tensor.tensor_hotspot_node_ids_sample` | list |
| flux absolute sum | `steps.jsonl` | `family_extensions.grc9v3.transport.flux_abs_sum` | float |
| potential minimum | `steps.jsonl` | `family_extensions.grc9v3.transport.potential_min` | float |
| potential maximum | `steps.jsonl` | `family_extensions.grc9v3.transport.potential_max` | float |
| positive flux edge count | `steps.jsonl` | `family_extensions.grc9v3.transport.positive_flux_edge_count` | int |
| sink count | `steps.jsonl` | `family_extensions.grc9v3.identity_basin.sink_count` | int |
| basin count | `steps.jsonl` | `family_extensions.grc9v3.identity_basin.basin_count` | int |
| basin size max | `steps.jsonl` | `family_extensions.grc9v3.identity_basin.basin_size_max` | int |
| geometric seed count | `steps.jsonl` | `family_extensions.grc9v3.identity_basin.geometric_seed_count` | int |
| validated basin count | `steps.jsonl` | `family_extensions.grc9v3.identity_basin.validated_basin_count` | int |
| spark candidates | `steps.jsonl` | `family_extensions.grc9v3.hybrid_spark_state.hybrid_spark_candidate_count` | int |
| signed crossing status | `steps.jsonl` | `family_extensions.grc9v3.hybrid_spark_state.signed_crossing_status` | string/object |
| spark candidate event | `events.jsonl` | `family_extensions.grc9v3.event_domain == "spark"` and `lifecycle_stage == "candidate"` | event |
| expansion event | `events.jsonl` | `family_extensions.grc9v3.event_domain == "expansion"` | event |
| completed hybrid spark | `events.jsonl` | `family_extensions.grc9v3.event_domain == "spark"` and `lifecycle_stage == "completed"` | event |
| daughter sink count | `run_summary.json` | `family_extensions.grc9v3.representative_appendix_e_summary.daughter_sink_count` | int |
| hierarchy depth | `steps.jsonl` | `family_extensions.grc9v3.hierarchy_state.max_hierarchy_depth` | int |
| choice detected | `events.jsonl` | `family_extensions.grc9v3.event_domain == "choice"` | event |
| collapse event | `events.jsonl` | `family_extensions.grc9v3.event_domain == "collapse"` | event |
| collapse registry count | `steps.jsonl` | `family_extensions.grc9v3.choice_collapse.collapse_registry_count` | int |
| growth event | `events.jsonl` | `family_extensions.grc9v3.event_domain == "growth"` | event |
| growth count | `steps.jsonl` | `family_extensions.grc9v3.growth_state.growth_event_count` | int |
| budget correction | `events.jsonl` | `family_extensions.grc9v3.event_domain == "budget"` | event |
| budget error | `steps.jsonl` | `family_extensions.grc9v3.budget_correction.budget_error` | float |
| coarse cache state | `steps.jsonl` | `family_extensions.grc9v3.coarse_cache.coarse_cache_state` | string |
| coarse invalidation | `steps.jsonl` | `family_extensions.grc9v3.coarse_cache.coarse_cache_invalidated` | bool |
| coarse invalidation reason | `steps.jsonl` | `family_extensions.grc9v3.coarse_cache.coarse_cache_invalidation_reason` | string |
| replay digest match | `run_summary.json` | `family_extensions.grc9v3.representative_appendix_e_summary.replay_digest_match` | bool |
| contract version | `steps.jsonl`, `events.jsonl`, `run_summary.json` | `family_extensions.grc9v3.contract_version == "phase_t_grc9v3_iter1_v1"` | bool |

If an exact field name changes in the typed telemetry contract, this mapping
must be updated before selector implementation.

## Manifest Draft

Discovery should write a manifest like:

```json
{
  "manifest_version": "grc9v3_phenomenology_discovery_v1",
  "source_artifacts": [
    {
      "artifact_role": "representative_reference",
      "path": "outputs/phase-t-grc9v3/representative/appendix_e_cell_division/",
      "used_for_discovery": false
    }
  ],
  "run_scope": {
    "family": "grc9v3",
    "profile_naming": "grc9v3_discovery_<phenomenon>_v<integer>",
    "lane_naming": "<seed_family>_<control_role>",
    "profiles": [],
    "lanes": []
  },
  "structure_hypotheses": [
    {
      "hypothesis_id": "grc9v3_hypothesis_hybrid_spark_gate_v1",
      "target_phenomenon": "hybrid_spark_gate",
      "runtime_status": "testable",
      "ownership": ["grc9_mechanical", "grcv3_semantic", "grc9v3_hybrid"],
      "mechanism_id": "grc9v3_mech_hybrid_spark_gate",
      "graph_preconditions": {
        "requires_full_saturation": true,
        "requires_basin_interior": true,
        "requires_signed_hessian_degeneracy": true
      },
      "state_preconditions": {
        "hessian_backend": "row_basis_diagonal"
      },
      "seed_family": "hybrid_spark_gate",
      "seed_parameters": {
        "control_role": "positive_control"
      },
      "predicted_signatures": [
        {
          "field_path": "family_extensions.grc9v3.hybrid_spark_state.hybrid_spark_candidate_count",
          "predicate": "> 0"
        }
      ]
    }
  ],
  "selectors": [],
  "motifs": [],
  "review_history": []
}
```

Recommended output locations:

- `outputs/grc9v3/phenomenology_discovery/grc9v3_phenomenology_manifest.json`
- `outputs/grc9v3/phenomenology_discovery/grc9v3_phenomenology_report.md`
- `outputs/grc9v3/phenomenology_discovery/mechanism_ledger.json`
- `outputs/grc9v3/phenomenology_discovery/reviewed_motif_catalog.json`
- `outputs/grc9v3/phenomenology_discovery/reviewed_motif_catalog.md`
- `outputs/grc9v3/phenomenology_discovery/sessions/S0001/`

Every generated run that becomes evidence should have a session id before it is
referenced by a motif. Session ids use the stable zero-padded form `S0001`,
`S0002`, and so on. Categorical metadata belongs in `session_manifest.json` and
index files, not in the path structure beyond the session id.

## Prediction Confidence Scoring

Use the same ordinal scoring pattern as GRC9 discovery:

- `0`: no run evidence or required telemetry surface missing.
- `1`: generated seed ran, but primary predicted fields are absent or
  contradicted.
- `2`: one primary predicted field matches, but event timing or graph evidence
  is weak.
- `3`: primary predicted fields match and event timing is plausible.
- `4`: primary predicted fields, event evidence, run summary, and checkpoint
  evidence agree.
- `5`: score `4` plus positive/negative controls or perturbations separate
  cleanly.

Confidence labels:

- `0-1`: `rejected` or `needs_rerun`,
- `2`: `weak_candidate`,
- `3`: `candidate`,
- `4`: `strong_candidate`,
- `5`: `accepted_after_review`.

## Iteration Plan

### Iteration 1: Discovery Plan And Checklist

- Add this plan.
- Add the execution checklist.
- Link the track from `ImplementationPhases.md`.
- Lock the boundary as pure-runtime GRC9V3 discovery before source claims.

### Iteration 2: Mechanism Ledger

- Build a mechanism ledger from Phase 7 equations, the step loop, and the
  GRC9/GRCV3 parent specs.
- Record mechanism ids, equation references, ownership, graph/state
  preconditions, parameter knobs, predicted telemetry fields, runtime status,
  and blockers.
- Write the ledger under `outputs/grc9v3/phenomenology_discovery/`.

### Iteration 3: Runtime Structure Hypothesis Catalog

- Define seed families for hybrid spark, spark-to-expansion, Appendix E
  division, choice/collapse, growth, budget, Hessian backend comparison,
  transport/basin rerouting, coarse invalidation, and quiescent controls.
- Record positive and negative controls for each family.
- Record predicted signatures before generation.

### Iteration 4: Deterministic GRC9V3 Runtime Seed Builders

- Implement deterministic pure-runtime seed builders.
- Validate nine-port topology, basin fields, hierarchy fields, budget target,
  and capability requirements.
- Preserve seed parameters in session manifests.

### Iteration 5: First Control Sessions

- Run small positive/negative control sessions for each testable seed family.
- Capture telemetry, graph checkpoints, experiment reports, and replay flags.
- Record all sessions in the experimental log.
- Reports should include first-pass control interpretation: quiescent no-event
  confirmations, eventful negative controls that need selector scoring, stable
  checkpoint-surface naming, and replay-environment notes.

### Iteration 5.1: Theory-First Seed Refinement

- Treat the first generated-run session as a smoke test, not final evidence for
  every family.
- Refine seed families that produced only diagnostic telemetry when their
  intended behavior is lifecycle-facing.
- Target the actual Phase 7 gates for choice/collapse, growth, budget
  correction, coarse-cache invalidation, transport rerouting, and Hessian
  backend divergence.
- Preserve diagnostic-only classification when a family has no lifecycle event
  by design, but make that explicit in the session report.
- Rerun refined controls as a new replayable session before selector
  implementation.

### Iteration 5.2: Appendix E Pass/Fail Separation

- Treat `S0005` as evidence that the Appendix E negative lane is not yet a
  usable negative control: it emits the same completed division summary as the
  positive lane.
- Keep the positive Appendix E cell-division fixture unchanged.
- Add a strict Appendix E no-completion negative control that fails an explicit
  runtime precondition instead of claiming a source-level daughter-min-mass
  evaluator that the runtime does not yet implement.
- Rerun all refined controls as the next monotonic session and verify the
  Appendix E positive lane completes while the negative lane has no completed
  hybrid spark and no representative Appendix E completion summary.

### Iteration 6: Field-Backed Selectors

- Implement selectors over saved session artifacts.
- Compare predicted and observed signatures.
- Score candidates and record misses or ambiguities.
- Status: complete in S0007. The selector pass reads S0006 artifacts and
  produces `selector_manifest.json`, `selector_validation_report.json`, and
  `selector_validation_summary.md` under
  `outputs/grc9v3/phenomenology_discovery/sessions/S0007/`.
- S0007 currently validates 19 lanes, records 19 candidate motifs, and has no
  missing selector expectations. The selectors cover lifecycle events,
  Appendix E daughter sinks/hierarchy, choice/collapse, growth, budget,
  Hessian backend comparison, hybrid tensor, transport, identity/basin,
  signed-crossing prerequisites, coarse-cache state, no-event controls,
  contract version, and lane naming.
- Selector reports distinguish `missing_surface` from `predicate_failed`,
  preserve `control_role` and `evidence_mode`, treat signed-crossing as
  capability-status evidence when disabled, and use paired transport selectors
  to distinguish reroute and non-reroute controls.

### Iteration 7: Complex Hybrid Examples

- Compose multiple runtime mechanisms into longer examples.
- Prefer causal chains such as spark -> expansion -> completed-spark
  hierarchy-state evidence -> choice -> collapse, or expansion -> growth ->
  budget -> coarse invalidation.
- Keep graphs connected unless a fixture explicitly tests a boundary case.
- Status: complete in S0008/S0009.
- S0008 records seven connected pure-runtime examples: spark/expansion/
  completed-spark hierarchy-state evidence, spark/expansion/choice/collapse,
  expansion/growth/budget/coarse, paired Hessian backends on the same graph,
  and two targeted perturbations.
- S0009 applies the field-backed selectors to S0008; all seven complex lanes
  score as `strong_candidate` with zero missing surfaces.
- Complex-lane reports include `event_sequence_analysis` so additional
  lifecycle side effects are explicit instead of hidden by selector success.

### Iteration 8: Visual Review

- Generate Phase V-style behavior and checkpoint graph visuals for candidate
  motifs.
- Link exact or nearest checkpoints to motif windows.
- Use visuals only as evidence companions to telemetry.
- Status: complete in S0010.
- S0010 renders complete behavior panels, event timelines, graph sequences,
  graph animations, graph layout JSON, and final interactive graph HTML for all
  seven S0009 complex GRC9V3 candidate motifs.
- S0010 links the reviewed motifs to 20 exact S0008 graph checkpoints with
  zero missing exact checkpoint steps and enabled GRC9V3 overlays on every
  indexed record.
- The visual review index is written to:
  - `outputs/grc9v3/phenomenology_discovery/sessions/S0010/visual_index.json`

### Iteration 8.1: Hessian Comparator Review

- Reclassify the S0008 Hessian backend pair as diagnostic comparator evidence,
  not lifecycle event phenomenology.
- Run a paired eventful Hessian backend probe on matching graph/state inputs.
- Preserve any no-delta result as negative backend-event-delta evidence.
- Status: complete in S0011.
- S0011 records the S0008 Hessian pair as `diagnostic_comparator` with no
  lifecycle events.
- S0011 eventful probe emits spark -> expansion -> completed-spark under both
  `row_basis_diagonal` and `weighted_least_squares`, so it records
  `eventful_no_backend_event_delta`.
- Iteration 9 review rule:
  - backend/tensor evidence alone can enter the catalog as diagnostic evidence,
    but a Hessian lifecycle motif requires backend-dependent event sequence or
    backend-dependent lifecycle outcome.

### Iteration 9: Reviewed Motif Catalog

- Deduplicate motifs by phenomenon, seed family, predicted signature, and
  observed event sequence.
- Record accepted, strong candidate, rejected, duplicate, and needs-rerun
  statuses.
- Publish JSON and Markdown reviewed catalogs.
- Status: complete in S0012.
- S0012 publishes 7 reviewed records:
  - 3 accepted lifecycle motifs,
  - 2 strong negative-control candidates,
  - 2 Hessian diagnostic comparators.
- Accepted records link telemetry/selector evidence from S0009,
  visual/checkpoint evidence from S0010, and carry explicit non-claims against
  source lowering, Lorentzian semantics, and visual-only promotion.
- Hessian diagnostic records follow the Iteration 8.1 rule: backend/tensor
  evidence is diagnostic unless backend choice changes a lifecycle event
  sequence or lifecycle outcome.

### Iteration 9.1: Catalog Breadth Expansion

- Fold validated simple-control evidence from S0007 back into the reviewed
  motif catalog.
- Preserve S0012 complex-control review records as the base catalog.
- Promote eventful positive simple controls to accepted runtime motifs when
  selector evidence is complete.
- Preserve no-event controls, negative controls, and Hessian backend comparison
  controls as strong-candidate or diagnostic evidence rather than collapsing
  them into lifecycle motifs.
- Status: complete in S0013.
- S0013 publishes 26 expanded records:
  - 11 accepted motifs,
  - 11 strong candidates,
  - 4 diagnostic comparators,
  - 0 rejected and 0 needs-rerun records.
- The expanded catalog keeps GRC9V3 smaller than GRC9, but resolves the
  breadth issue by including validated simple controls alongside complex
  motifs.

### Iteration 10: Source-Language Handoff

- Produce a handoff note for the then-later GRCL/source-seed work.
- List which runtime motifs are suitable for source expression.
- Do not implement source lowering in this discovery track.
- Status: complete in S0014.
- S0014 reviews all 26 S0013 expanded catalog records:
  - 8 source-expression candidates,
  - 12 records requiring new source vocabulary,
  - 6 runtime-only records.
- Every handoff entry remains `runtime_evidence_only`; no GRCL/source lowering
  is claimed or implemented in this discovery phase.
- Post-completion status: the downstream GRCL-9V3 source/lowering track has
  since been implemented and closed separately. The source handoff remains the
  bridge from runtime evidence into that layer, not a retroactive source claim
  inside discovery.

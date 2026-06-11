# GRC9 Phenomenology Discovery Plan

This document defines the downstream discovery track for `GRC9` mechanical
phenomenology.

The execution checklist is
[`GRC9-PhenomenologyDiscovery-Checklist.md`](./GRC9-PhenomenologyDiscovery-Checklist.md).

Replayable experiment sessions are indexed in
`outputs/grc9/phenomenology_discovery/ExperimentalLog.md` when top-level
scratch outputs are present locally.
Session artifacts live under
`outputs/grc9/phenomenology_discovery/sessions/S0001/`.

It begins after Phase T-GRC9 has made the relevant mechanics observable in
telemetry, and after Phase V has made saved GRC9 artifact lanes inspectable
through deterministic visualization. The goal is to discover and name
GRC9-native motifs from theory-derived generated structures and their telemetry
evidence, not to extend the renderer or start GRCL-9 translation early.

Important correction: this is not primarily an artifact-mining phase. There are
not yet canonical GRC9 lanes to inspect, rank, or choose from. Existing GRC9
lanes are smoke and regression fixtures for telemetry and visualization only.
The discovery track must build its own GRC9 structures by reasoning from the
paper mathematics to the graph conditions that should emit the target
phenomenology.

Those generated structures should begin as deterministic GRC9 seeds, following
the same broad experimental pattern used for GRCV2/GRCV3 seed lanes. The key
difference is semantic level: these are pure GRC9 mechanical graph seeds, not
GRCL-level source objects and not lowered high-level programs.

Growth correction note: early discovery sessions that used broad inactive-port
growth remain historical diagnostics. Paper-facing growth claims now require
`growth_parent_eligibility_mode = "grc9_front_capacity"` and front-capacity
provenance. Corrected GRC9 growth evidence is published in
`outputs/grc9/phenomenology_discovery/sessions/S0035/corrected_grc9_growth_catalog.json`;
legacy broad-growth records are superseded by the migration summary in
`outputs/grcl9/lowering/sessions/S0037/growth_correction_supersession_summary.json`.

## Purpose

GRC9 phenomenology discovery should identify repeatable structures and windows
in generated GRC9 runs:

- spark precursor windows,
- spark and expansion neighborhoods,
- expansion-module morphology,
- column-preserving boundary reassignment patterns,
- growth loci on inactive ports,
- outward-flux and birth-probability regimes,
- row-tensor and column-diagnostic regimes,
- coarse-graining and profile-sparsity regimes,
- budget-correction regimes,
- fission-candidate and fission-confirmed persistence windows,
- quiescent basins, stable sinks, and transport pathways.

Discovery outputs should be structure hypotheses, generated GRC9 graph lanes,
evidence manifests, and review reports. Those outputs may later drive targeted
visualization panels and may later inform GRCL-9 translation work, but neither
of those is part of this discovery plan's first responsibility.

## Inputs

Authoritative implementation and contract inputs:

- [`Phase-T-GRC9-ImplementationPlan.md`](./Phase-T-GRC9-ImplementationPlan.md)
- [`Phase-T-GRC9-TelemetryContract.md`](./Phase-T-GRC9-TelemetryContract.md)
- [`Phase-T-GRC9-Closeout.md`](./Phase-T-GRC9-Closeout.md)
- [`Phase-V-ImplementationPlan.md`](./Phase-V-ImplementationPlan.md)
- [`Phase-V-GRC9-RepresentativeVisualization.md`](./Phase-V-GRC9-RepresentativeVisualization.md)
- [`../papers/2026-04-GRC-9.md`](../papers/2026-04-GRC-9.md)
- [`../specs/grc-9-spec.md`](../specs/grc-9-spec.md)

Available smoke and regression lanes:

- `outputs/representative/grc9/phase_t_grc9_iter6_representative/`
- `outputs/representative/grc9_landscape/phase_t_grc9_iter7_seed/`
- `outputs/representative/grc9_landscape_cell4_100/phase_t_grc9_iter7_seed/`

These lanes are not discovery inputs in the scientific sense. They can validate
that telemetry capture, graph checkpoint capture, and visualization work, but
they should not define the search space. The `cell-1` / `cell-4` lanes are
structural graft fixtures and must remain labeled as such.

Primary discovery inputs are instead:

- paper equations and phenomenology descriptions,
- the GRC9 implementation/spec contract,
- known telemetry fields from Phase T-GRC9,
- graph constraints imposed by the nine-port chart,
- deterministic GRC9 seed families and seed parameters,
- and explicit hypotheses about what local structure should produce each
  target behavior.

## Evidence Surfaces

Discovery has two evidence layers:

- predicted evidence, derived before a run from the paper mathematics and the
  proposed GRC9 graph structure,
- observed evidence, captured after running generated structures through the
  Phase T-GRC9 telemetry contract.

Visualizations are inspection aids; they do not create independent claims
without matching predicted and observed telemetry evidence.

Step-row surfaces:

- `family_extensions.grc9.backend_config`
- `family_extensions.grc9.port_chart`
- `family_extensions.grc9.row_tensor`
- `family_extensions.grc9.column_diagnostic`
- `family_extensions.grc9.transport`
- `family_extensions.grc9.identity_abundance`
- `family_extensions.grc9.coarse_graining`
- `family_extensions.grc9.budget_correction`

Event-row surfaces:

- spark evidence,
- expansion evidence,
- growth evidence,
- budget correction evidence,
- coarse-cache invalidation evidence when present.

Run-summary surfaces:

- lifecycle event counts,
- expansion summary,
- growth summary,
- calibration summary,
- fission summary,
- diagnostic status summary.

Graph-checkpoint surfaces:

- `port_graph` checkpoint identity,
- port occupancy and inactive-capacity overlays,
- module core/satellite/helper overlays,
- reassigned boundary edges,
- internal module edges,
- conductance overlays,
- signed-flux overlays when exported,
- basin and sink overlays when exported.

Visualization surfaces:

- trajectory panels,
- event timelines,
- report and comparison panels,
- graph snapshot sequences,
- final interactive graph views,
- graph comparison panels,
- checkpoint animations.

## Checkpoint Requirements By Motif Type

Discovery runs should default to graph checkpoint capture at every step for
short generated seeds. For longer perturbation sweeps, the minimum acceptable
cadence is:

- initial checkpoint,
- every event step,
- one checkpoint before and after each event step when available,
- final checkpoint,
- and every `10` steps as a fallback cadence.

Required checkpoint payload:

- `graph_kind = "port_graph"`
- `checkpoint_payload = "port_chart_module_overlay_v1"`
- node and edge payloads sufficient for stable graph rendering
- `port_overlays` for port occupancy and inactive-capacity inspection
- `module_overlays` when expansion modules exist
- `latest_reassignments` when boundary reassignment is expected

Motif-specific requirements:

- spark precursor:
  - every-step checkpoints through the predicted spark window,
  - port occupancy overlays,
  - conductance overlays,
  - signed-flux overlays when the selector depends on flux direction.
- expansion module:
  - checkpoint immediately before expansion,
  - checkpoint at module creation,
  - checkpoint immediately after boundary reassignment,
  - module overlays and reassignment overlays required.
- growth locus:
  - every-step checkpoints through the predicted birth window,
  - inactive-port and parent-port overlays required,
  - signed-flux overlays required when outward pressure is part of the claim.
- row/column regime:
  - enough cadence to show the regime is stable rather than a one-step spike,
  - port overlays and conductance overlays required.
- coarse-graining/profile-sparsity:
  - checkpoints are useful but not primary evidence,
  - telemetry fields carry the primary claim.
- budget-correction:
  - checkpoints are optional unless the correction is coupled to expansion or
    growth topology.
- fission candidate:
  - every-step checkpoints through the persistence window,
  - basin/sink overlays required when exported by the checkpoint path.

Motif windows should link to checkpoint ids by exact step match first. If no
exact checkpoint exists, link the nearest checkpoint before and after the
window and record the missing exact checkpoint as an evidence limitation.

## Boundaries

This discovery track must not claim:

- GRCV3 hierarchy, split/collapse, choice, or observer semantics,
- GRCL-9 lowering,
- Lorentzian causal-layer behavior,
- FRC sigma-layer behavior,
- boundary-horizon or ghost semantics,
- native meaning for `cell-1` or `cell-4` beyond their structural graft role,
- a motif from an image without telemetry fields that justify it.

Reserved future work may add observer-local views, GRCL-9 translation, or
cross-family semantic comparison, but those need separate plans.

## Runtime Gap Constraints

Discovery must distinguish currently testable GRC9 mechanics from paper-facing
or reserved phenomena that the runtime cannot yet exercise.

Currently testable:

- instantaneous spark and expansion behavior,
- fixed nine-port chart occupancy and saturation behavior,
- column-preserving reassignment when expansion events expose reassignment
  evidence,
- growth events driven by outward flux pressure and birth probability,
- row tensor and column diagnostics exposed in step rows,
- coarse-graining diagnostics and profile sparsity as telemetry diagnostics,
- budget correction path summaries and budget correction events,
- identity fission persistence diagnostics from the current evaluator,
- transport summaries and label availability exposed by telemetry.

Currently constrained:

- adiabatic expansion schedule:
  - seeds may record the desired schedule,
  - only instantaneous expansion should be treated as testable until the
    runtime implements adiabatic substeps.
- boundary barrier or ghost modes:
  - reserved future,
  - generated seeds should use currently implemented boundary behavior such as
    `prune` unless the runtime grows a new boundary mode.
- near-saturation relaxation:
  - optional and deferred,
  - spark precursor seeds should rely on full saturation unless telemetry shows
    the near-saturation rule is implemented for the run.
- sign-crossing spark:
  - testable only when the runtime stores enough prior column diagnostic
    history to identify sign crossing.
- profile sparsity compression:
  - diagnostic only,
  - seeds may test sparsity fields but not compressed storage behavior.
- ternary identity tree extraction:
  - reserved future,
  - not a discovery target in this track.
- scale-weighted abundance:
  - testable only when the seed records the gamma used for the run.
- identity fission persistence:
  - testable with the current evaluator,
  - seed parameters must record `identity_fission_persistence_delta` and
    `identity_fission_min_basin_mass`.

Mechanisms outside the currently testable set should still appear in the
mechanism ledger, but their `runtime_status` must be `deferred` or
`reserved_future` and they must not produce accepted motifs.

## Theory-First Structure Deduction

Each target phenomenon should start as an inverse-design question:

```text
paper mechanism -> required local graph condition -> predicted telemetry
signature -> deterministic GRC9 seed -> observed telemetry validation
```

Examples:

- Spark precursor:
  - infer the column imbalance, sign crossing, instability gate, and effective
    degree conditions that should make a spark candidate inevitable or likely.
  - generate port-chart seed structures whose column interfaces and
    conductances realize those conditions.
  - predict the `column_diagnostic`, `spark_evidence`, and
    `expansion_evidence` fields before running.

- Expansion module:
  - infer the external port capacity and boundary reassignment pressure needed
    for a specific module size.
  - generate a seed neighborhood with the target `D_eff`, old boundary edge
    pattern, and transfer ratios.
  - predict module node count, reassigned edge count, internal edge count,
    conductance initialization, and coherence transfer ratios.

- Growth locus:
  - infer inactive-port neighborhoods where outward flux pressure should
    exceed the birth rule's effective threshold.
  - generate a seed boundary with controlled outward flux and parent-port
    competition.
  - predict `outward_flux_pressure`, `birth_probability`, selected parent port,
    and growth event timing.

- Fission candidate:
  - infer the expansion and basin geometry needed for two stable sinks to
    persist through the Appendix E window.
  - generate seed structures with competing basin attractors and controlled
    post-expansion connectivity.
  - predict candidate count, confirmed count, and persistence length.

The generated seed graph is the experiment. Existing smoke lanes are useful
only to prove that the experiment machinery can record and display the result.

Seed rules:

- seeds are deterministic and parameterized,
- seeds are expressed directly in GRC9 mechanical graph terms,
- seeds may be grouped into positive controls, negative controls, and
  perturbation families,
- seeds may reuse the same artifact/run-lane pattern as GRCV2/GRCV3,
- seeds must not claim GRCL-9 source semantics,
- seeds must preserve their construction parameters in the discovery manifest.

## Seed Family Catalog

The first seed catalog should cover every phenomenon listed in the purpose
section. Each seed family should define node count, row/column occupancy,
conductance assignment, boundary edge pattern, coherence placement, expected
lifecycle, positive controls, negative controls, and perturbations.

Spark precursor seed:

- construct a saturated or near-saturated parent neighborhood in one or more
  columns,
- tune column imbalance and sign-crossing conditions,
- vary `D_eff`, spark threshold, and conductance symmetry,
- expect column diagnostic activation followed by spark evidence.

Expansion module seed:

- construct a parent sink with controlled external degree,
- choose boundary edges whose columns should be preserved during reassignment,
- vary module size, transfer ratios, and internal bond initialization,
- expect expansion evidence, module overlays, and reassignment overlays.

Column-preserving reassignment seed:

- construct boundary edge families with distinct column labels and conductance
  weights,
- vary edge-count imbalance, saturation distribution, and weak/strong boundary
  conductance,
- expect reassigned edges to preserve column families and expose reassignment
  counts by expansion event and checkpoint overlay.

Growth pressure seed:

- construct inactive ports with controlled outward-flux gradients,
- vary birth rule lambda, parent-port competition, and boundary flux magnitude,
- include negative controls below effective birth pressure,
- expect growth evidence with selected parent port and birth probability.

Row-tensor and column-diagnostic seed:

- construct row-heavy, column-heavy, and balanced connectivity patterns,
- isolate row anisotropy from column-proxy activation where possible,
- vary row mismatch and conductance asymmetry,
- expect row tensor extrema and column diagnostic counts to separate cleanly.

Coarse-graining/profile-sparsity seed:

- construct fields with dense, mixed, and near-one-hot intra-column profiles,
- vary field type across nonnegative, signed lossless, and signed compressed
  diagnostic modes when available,
- test Split round-trip diagnostics for conductance-like, flux-like, and
  coherence-like fields,
- expect profile sparsity and coarse field type telemetry to reflect the
  designed field structure.

Budget-correction seed:

- construct expansion or growth actions with controlled budget perturbation,
- vary budget preservation policy between uniform shift and simplex projection
  when the runtime supports both paths,
- include a no-correction control,
- expect budget correction summary and event evidence to distinguish policy
  and before/after error.

Quiescent basin seed:

- construct stable sinks with balanced conductance, no saturated spark source,
  low outward pressure, and conserved budget,
- include small perturbations that should remain below event thresholds,
- expect stable sink and basin counts with no spark, expansion, or growth
  events.

Transport pathway seed:

- construct asymmetric conductance landscapes with competing short and long
  paths,
- vary edge labels and conductance ratios,
- expect transport summaries and optional signed-flux overlays to distinguish
  the chosen routing regime.

Fission candidate seed:

- construct post-expansion neighborhoods with two basin attractors,
- vary persistence window, minimum basin mass, and bridge conductance,
- include one control where the basins quickly merge,
- expect fission candidate and confirmed counts only when the two sinks persist
  through the configured window.

## Seed Generator Contract

Seed generators should be deterministic, importable helpers that return a
GRC9-ready initial condition plus metadata. The exact code location can be
chosen during implementation, but the public shape should be stable:

```python
seed = generate_grc9_seed(
    seed_family="spark_precursor",
    seed_name="spark_precursor_positive_control",
    parameters={...},
)
```

The returned object should include:

- a GRC9 initial state or constructor input,
- `seed_family`,
- `seed_name`,
- `seed_parameters`,
- `expected_runtime_config`,
- `graph_preconditions`,
- `predicted_signatures`,
- `negative_control_of` when applicable,
- `perturbation_of` when applicable.

Common controllable parameters:

- `node_count`,
- row and column occupancy pattern,
- active and inactive port pattern,
- edge list and boundary edge list,
- conductance assignment mode,
- coherence placement and total budget,
- `D_eff` or target effective degree,
- expansion transfer ratios,
- internal bond mode and fixed bond weight,
- spark threshold and threshold mode,
- birth rule and birth lambda,
- metric/curvature coefficients when runtime configurable,
- budget preservation policy,
- scale-weighted abundance gamma,
- identity fission persistence delta,
- identity fission minimum basin mass.

Pre-run validation checklist:

- every node and edge respects the nine-port chart constraints,
- row and column occupancy match the declared seed parameters,
- graph connectivity matches the hypothesis,
- boundary edges are valid port-pair assignments,
- conductance values are finite and nonnegative where required,
- signed flux fields are represented only through supported runtime paths,
- coherence budget is finite and conserved at initialization,
- saturation and inactive-port counts match the intended control condition,
- runtime config can actually test the requested mechanism,
- positive and negative controls differ in exactly the intended parameters
  where practical.

Perturbation strategy:

- scalar perturbations should start with small deterministic deltas such as
  `-10%`, `0%`, and `+10%`,
- discrete port perturbations should add or remove one occupied port at a time,
- edge perturbations should add, remove, or reweight one boundary family at a
  time,
- coherence perturbations should redistribute budget without changing total
  budget unless the seed is explicitly a budget-correction seed,
- every perturbation seed should record its parent seed and changed parameters.

## Discovery Method

1. Paper mechanism extraction.
   - Read the GRC9 paper/spec mechanism by mechanism.
   - Record equations, required inequalities, thresholds, and policy choices.
   - Translate each mechanism into graph-local preconditions.

2. Seeded structure hypothesis drafting.
   - Define a minimal graph family expected to emit each phenomenon.
   - Record port roles, row/column placement, edge conductances, coherence
     placement, boundary edges, and expected lifecycle path.
   - Record the seed family and parameter ranges that instantiate the
     hypothesis.
   - Record explicit predicted telemetry signatures before running anything.

3. Generated seed lane construction.
   - Implement or configure deterministic GRC9 seed generators.
   - Produce one narrow lane per hypothesis family.
   - Include control seeds that should not emit the phenomenon.

4. Run and capture.
   - Run generated structures through Phase T-GRC9 telemetry.
   - Capture step rows, event rows, run summaries, and graph checkpoints.
   - Render Phase V visuals only after telemetry capture succeeds.

5. Prediction-to-observation comparison.
   - Compare predicted field signatures to observed telemetry.
   - Record matches, mismatches, missing fields, and unexpected events.
   - Keep failed hypotheses; they are evidence about the mechanism.

6. Cross-surface evidence assembly.
   - Attach predicted fields, observed step fields, event ids, run-summary
     fields, and checkpoint ids.
   - Attach visual artifact paths only after telemetry evidence exists.
   - Score confidence based on prediction quality and cross-surface agreement.

7. Human review.
   - Mark candidates as accepted, rejected, duplicate, or needs-rerun.
   - Add short notes for field interpretation and non-claims.
   - Promote stable motifs to the catalog only after review.

8. Handoff.
   - Visualization can consume reviewed manifests for targeted motif panels.
   - GRCL-9 translation planning can consume reviewed GRC9-native motifs.

## Manifest Draft

Discovery should write a manifest like:

```json
{
  "manifest_version": "grc9_phenomenology_discovery_v1",
  "source_artifacts": [
    {
      "artifact_role": "smoke_reference",
      "path": "outputs/representative/grc9/phase_t_grc9_iter6_representative/",
      "used_for_discovery": false
    }
  ],
  "run_scope": {
    "family": "grc9",
    "profile_naming": "grc9_discovery_<phenomenon>_v<integer>",
    "lane_naming": "<seed_family>_<control_role>",
    "profiles": ["grc9_discovery_spark_precursor_v1"],
    "lanes": ["spark_precursor_positive_control"]
  },
  "structure_hypotheses": [
    {
      "hypothesis_id": "grc9-hypothesis-0001",
      "target_phenomenon": "spark_precursor",
      "runtime_status": "testable",
      "paper_sources": [
        {
          "source": "papers/2026-04-GRC-9.md",
          "section": "",
          "equation": ""
        }
      ],
      "graph_preconditions": {
        "column_imbalance_threshold": null,
        "requires_saturation": true,
        "requires_sign_crossing_history": false,
        "target_effective_degree": null
      },
      "seed_family": "spark_precursor",
      "seed_parameters": {
        "control_role": "positive_control"
      },
      "generator": "generate_grc9_seed",
      "predicted_signatures": [
        {
          "field_path": "family_extensions.grc9.column_diagnostic.column_proxy_candidate_count",
          "predicate": "> 0"
        }
      ]
    }
  ],
  "selectors": [
    {
      "selector_id": "spark_confirmed_events",
      "surface": "events.jsonl",
      "query": "family_extensions.grc9.event_domain == 'spark'",
      "expected_type": "event_row"
    }
  ],
  "motifs": [
    {
      "motif_id": "grc9-motif-0001",
      "hypothesis_id": "grc9-hypothesis-0001",
      "phenomenon": "spark_precursor",
      "family": "grc9",
      "profile": "grc9_discovery_spark_precursor_v1",
      "lane": "spark_precursor_positive_control",
      "run_id": "",
      "seed_name": "generated_spark_precursor_0001",
      "step_window": [0, 0],
      "event_ids": [],
      "checkpoint_ids": [],
      "predicted_evidence_fields": [],
      "observed_evidence_fields": [],
      "evidence_fields": {
        "predicted": [],
        "observed": [],
        "missing": []
      },
      "visual_artifacts": [],
      "confidence_score": 0,
      "confidence_label": "candidate",
      "review_status": "unreviewed",
      "rejection_reason": null,
      "rerun_requested": false,
      "non_claims": [],
      "notes": {
        "field_interpretation": "",
        "parameter_sensitivity": "",
        "reproduction": ""
      }
    }
  ],
  "review_history": [
    {
      "motif_id": "grc9-motif-0001",
      "from_status": "unreviewed",
      "to_status": "candidate",
      "reviewer": "",
      "reason": "",
      "timestamp_utc": ""
    }
  ]
}
```

Profile and lane naming:

- discovery profiles should use `grc9_discovery_<phenomenon>_v<integer>`,
- generated lanes should use `<seed_family>_<control_role>`,
- perturbation lanes should append the changed parameter name, for example
  `spark_precursor_positive_control_conductance_plus10`,
- smoke and regression lanes may be referenced in `source_artifacts`, but they
  must set `used_for_discovery = false` unless they were generated by this
  discovery track.

`evidence_fields` is the grouped union of predicted, observed, and missing
field evidence. `predicted_evidence_fields` and `observed_evidence_fields`
remain as compact compatibility lists for consumers that do not need the
grouped form.

Recommended output locations:

- `outputs/grc9/phenomenology_discovery/grc9_phenomenology_manifest.json`
- `outputs/grc9/phenomenology_discovery/grc9_phenomenology_report.md`
- `outputs/grc9/phenomenology_discovery/visual_index.json`
- `outputs/grc9/phenomenology_discovery/generated_seed_lanes/`
- `outputs/grc9/phenomenology_discovery/mechanism_ledger.json`
- `outputs/grc9/phenomenology_discovery/grcl9_suitability_catalog.md`

Replayable session output locations:

- `outputs/grc9/phenomenology_discovery/sessions/S0001/session_manifest.json`
- `outputs/grc9/phenomenology_discovery/sessions/S0001/README.md`
- `outputs/grc9/phenomenology_discovery/sessions/S0001/telemetry/`
- `outputs/grc9/phenomenology_discovery/sessions/S0001/graph_checkpoints/`
- `outputs/grc9/phenomenology_discovery/sessions/S0001/visualization/`
- `outputs/grc9/phenomenology_discovery/sessions/S0001/reports/`

Every test or generated discovery run should have a session id before it is
used as evidence in the manifest. Session ids use the stable zero-padded form
`S0001`, `S0002`, and so on. Categorical metadata such as iteration,
phenomenon, seed family, and control role belongs in `session_manifest.json`
and the `indexes/` views.

## Selector Families

Initial selector families should stay simple and field-backed.

Spark selectors:

- spark candidate or confirmation events,
- instability gate pass,
- column-proxy gate pass,
- sign-crossing gate pass,
- predicted module size or target effective degree.

Expansion selectors:

- expansion event presence,
- module node count,
- internal edge count,
- reassigned edge count,
- coherence transfer ratios,
- internal conductance stats,
- target effective degree.

Growth selectors:

- growth event presence,
- selected parent port,
- outward flux pressure,
- birth probability,
- birth rule.

Column and row regime selectors:

- row tensor mean or anisotropy extrema,
- row mismatch extrema,
- column proxy candidate count,
- sign crossing candidate count,
- column profile sparsity.

Identity and fission selectors:

- sink count changes,
- max basin size changes,
- successor tie count,
- identity fission candidate count,
- identity fission confirmed count,
- max persistence steps.

Budget and coarse selectors:

- budget correction events,
- budget error before and after correction,
- coarse field count,
- coarse field types,
- profile compression mode,
- profile sparsity changes.

## Selector Field Mapping

Selectors should be implemented as programmatic queries over saved telemetry
artifacts. The initial mapping is:

| Selector | Surface | Field Path Or Query | Type |
|---|---|---|---|
| spark candidate event | `events.jsonl` | `family_extensions.grc9.event_domain == "spark"` and `lifecycle_stage == "candidate"` | event |
| spark confirmed event | `events.jsonl` | `family_extensions.grc9.event_domain == "spark"` and `lifecycle_stage == "confirmed"` | event |
| spark instability gate | `events.jsonl` | `family_extensions.grc9.spark_evidence.instability_gate_pass` | bool |
| spark column-proxy gate | `events.jsonl` | `family_extensions.grc9.spark_evidence.column_proxy_gate_pass` | bool |
| spark sign-crossing gate | `events.jsonl` | `family_extensions.grc9.spark_evidence.sign_crossing_gate_pass` | bool |
| predicted module size | `events.jsonl` | `family_extensions.grc9.spark_evidence.predicted_module_size` | int |
| predicted effective degree | `events.jsonl` | `family_extensions.grc9.spark_evidence.predicted_D_eff` | int |
| target effective degree | `events.jsonl` | `family_extensions.grc9.expansion_evidence.target_effective_degree` | int |
| expansion event | `events.jsonl` | `family_extensions.grc9.event_domain == "expansion"` | event |
| module node count | `events.jsonl` | `family_extensions.grc9.expansion_evidence.module_node_count` | int |
| internal edge count | `events.jsonl` | `family_extensions.grc9.expansion_evidence.internal_edge_count` | int |
| reassigned edge count | `events.jsonl` | `family_extensions.grc9.expansion_evidence.reassigned_edge_count` | int |
| coherence transfer ratios | `events.jsonl` | `family_extensions.grc9.expansion_evidence.coherence_transfer_ratios` | list[float] |
| internal conductance stats | `events.jsonl` | `family_extensions.grc9.expansion_evidence.internal_conductance_stats` | object |
| growth event | `events.jsonl` | `family_extensions.grc9.event_domain == "growth"` | event |
| selected parent port | `events.jsonl` | `family_extensions.grc9.growth_evidence.selected_parent_port` | int/string |
| outward flux pressure | `events.jsonl` | `family_extensions.grc9.growth_evidence.outward_flux_pressure` | float |
| birth probability | `events.jsonl` | `family_extensions.grc9.growth_evidence.birth_probability` | float |
| birth rule | `events.jsonl` | `family_extensions.grc9.growth_evidence.birth_rule` | string |
| row tensor mean | `steps.jsonl` | `family_extensions.grc9.row_tensor.row_tensor_mean` | float |
| row tensor anisotropy | `steps.jsonl` | `family_extensions.grc9.row_tensor.row_tensor_anisotropy_max` | float |
| row mismatch max | `steps.jsonl` | `family_extensions.grc9.row_tensor.row_mismatch_term_max` | float |
| column proxy candidates | `steps.jsonl` | `family_extensions.grc9.column_diagnostic.column_proxy_candidate_count` | int |
| sign crossing candidates | `steps.jsonl` | `family_extensions.grc9.column_diagnostic.sign_crossing_candidate_count` | int |
| column profile sparsity | `steps.jsonl` | `family_extensions.grc9.column_diagnostic.column_profile_sparsity` | float |
| sink count | `steps.jsonl` | `family_extensions.grc9.identity_abundance.sink_count` | int |
| basin size maximum | `steps.jsonl` | `family_extensions.grc9.identity_abundance.basin_size_max` | int |
| successor tie count | `steps.jsonl` | `family_extensions.grc9.identity_abundance.successor_tie_count` | int |
| scale-weighted abundance | `steps.jsonl` | `family_extensions.grc9.identity_abundance.scale_weighted_abundance` | float |
| fission candidate count | `run_summary.json` | `family_extensions.grc9.expansion_summary.identity_fission_candidate_count` | int |
| fission confirmed count | `run_summary.json` | `family_extensions.grc9.expansion_summary.identity_fission_confirmed_count` | int |
| fission max persistence | `run_summary.json` | `family_extensions.grc9.expansion_summary.identity_fission_max_persistence_steps` | int |
| budget correction event | `events.jsonl` | `family_extensions.grc9.event_domain == "budget"` and `lifecycle_stage == "corrected"` | event |
| budget error | `steps.jsonl` | `family_extensions.grc9.budget_correction.budget_error` | float |
| budget correction path | `steps.jsonl` | `family_extensions.grc9.budget_correction.last_budget_correction_path` | string |
| budget before/after | `events.jsonl` | `family_extensions.grc9.budget_evidence.budget_error_before/after` | float |
| coarse field count | `steps.jsonl` | `len(family_extensions.grc9.coarse_graining.coarse_fields_list)` | int |
| coarse field types | `steps.jsonl` | `family_extensions.grc9.coarse_graining.coarse_field_types` | object |
| profile compression mode | `steps.jsonl` | `family_extensions.grc9.coarse_graining.profile_compression_mode` | string |
| label availability | `steps.jsonl` | `family_extensions.grc9.transport.label_availability` | object |
| signed flux absolute sum | `steps.jsonl` | `family_extensions.grc9.transport.flux_abs_sum` | float |

If a field is absent in a run, the selector should report `missing_surface`
rather than infer the value from a graph image or from live model state.

## Prediction Confidence Scoring

Iteration 6 should use a simple ordinal confidence score:

- `0`: no run evidence or required telemetry surface missing.
- `1`: generated seed ran, but primary predicted fields are absent or
  contradicted.
- `2`: one primary predicted field matches, but event timing or graph evidence
  is weak.
- `3`: primary predicted fields match and event timing is plausible.
- `4`: primary predicted fields, event evidence, run summary, and checkpoint
  evidence agree.
- `5`: score `4` plus perturbation/control seeds separate cleanly from the
  positive control.

Confidence labels should be derived from score:

- `0-1`: `rejected` or `needs-rerun`,
- `2`: `weak_candidate`,
- `3`: `candidate`,
- `4`: `strong_candidate`,
- `5`: `accepted_after_review`.

## Iteration Plan

### Iteration 1: Discovery Plan And Manifest Schema

- Add this plan.
- Define the initial manifest fields.
- Link the plan from Phase V GRC9 downstream documentation.

### Iteration 2: Mechanism Ledger

- Build a mechanism ledger from the GRC9 paper and spec.
- For each target phenomenon, record equations, thresholds, policy choices,
  graph-local preconditions, and expected telemetry fields.
- Mark which mechanisms can be tested with current runtime support.
- The ledger's `runtime_status` is authoritative for the hypothesis catalog;
  each `structure_hypotheses[].runtime_status` should be copied from the
  corresponding mechanism ledger record unless a later runtime change is
  explicitly recorded.
- Write the ledger to:
  - `outputs/grc9/phenomenology_discovery/mechanism_ledger.json`
- Use one record per mechanism with:
  - `mechanism_id`,
  - `phenomenon`,
  - `paper_sources`,
  - `spec_sources`,
  - `equations`,
  - `inequalities`,
  - `thresholds`,
  - `policy_choices`,
  - `graph_preconditions`,
  - `predicted_telemetry_fields`,
  - `runtime_status`,
  - `runtime_blockers`,
  - `testable_with_current_runtime`.

### Iteration 3: Seeded Structure Hypothesis Catalog

- Define minimal graph families for spark, expansion, growth, fission,
  budget, and coarse-graining regimes.
- Define deterministic seed families and seed parameters for each graph family.
- Include negative-control seeds for each family.
- Record predicted telemetry signatures before generation.
- Cover the full seed family catalog:
  - spark precursor,
  - expansion module,
  - column-preserving reassignment,
  - growth pressure,
  - row tensor and column diagnostic,
  - coarse-graining/profile sparsity,
  - budget correction,
  - quiescent basin,
  - transport pathway,
  - fission candidate.

### Iteration 4: Deterministic GRC9 Seed Generators

- Implement deterministic GRC9 seed generators for the hypothesis catalog.
- Emit generated run lanes under the discovery output tree.
- Preserve generator parameters in the manifest.
- Current implementation:
  - generator module:
    `src/pygrc/discovery/grc9_seed_generator.py`,
  - public entrypoints:
    `generate_grc9_seed(...)` and `generate_grc9_seed_perturbation(...)`,
  - generated constructor payloads validate through `GRC9.from_state(...)`,
  - `column_diagnostic_regime` has dedicated near-cancellation geometry,
  - `budget_error_magnitude` records the minimal correction perturbation
    magnitude used by budget seeds,
  - topology payloads expose `edge_roles` for selector visibility,
  - replayable seed-generation session:
    `outputs/grc9/phenomenology_discovery/sessions/S0003/`.
- Acceptance:
  - every generated seed passes pre-run validation,
  - positive and negative controls differ in documented parameters,
  - generator output is deterministic for the same seed parameters,
  - generated lane names follow the discovery naming convention.

### Iteration 5: Generated Runs And Telemetry Capture

- Run generated structures through Phase T-GRC9 telemetry.
- Capture graph checkpoints and Phase V visuals.
- Keep smoke/regression lanes separate from generated discovery lanes.
- Allocate an `S0001`-style session id in the experimental log before running.
- Write replay metadata to
  `outputs/grc9/phenomenology_discovery/sessions/S0001/session_manifest.json`.
- Current low-step control pass:
  - runner:
    `src/pygrc/discovery/grc9_discovery_runner.py`,
  - session:
    `outputs/grc9/phenomenology_discovery/sessions/S0004/`,
  - replay:
    `PYTHONPATH=src ./.venv/bin/python -m pygrc.discovery.grc9_discovery_runner --session-id S0004`,
  - result:
    22 control lanes, 198 total steps, 220 graph checkpoints, 6 total events,
    all `growth` events in fission-candidate lanes.
- Acceptance:
  - every generated lane records step rows, event rows, run summary, and
    graph checkpoint index,
  - every generated lane is associated with a replayable `S0001`-style
    session,
  - checkpoint cadence meets the motif-specific requirement,
  - missing runtime surfaces are recorded in the manifest.

### Iteration 5.1: Theory-First Lifecycle Emitter Repair

S0004 proved that the first generated structures were valid GRC9 graphs but
were too generic as event emitters. The corrective pass must redesign the seed
families from the runtime/paper predicates backward, not by random
perturbation around the S0004 graphs.

- Preserve S0004 as negative evidence:
  - 22 control lanes,
  - 198 total steps,
  - 220 graph checkpoints,
  - 6 total lifecycle events,
  - all events were `growth` in fission-candidate lanes,
  - spark, expansion, reassignment, and growth-pressure lanes produced
    telemetry but no lifecycle events.
- Add explicit emitter variants:
  - `spark_column_proxy_emitter`,
  - `spark_instability_emitter`,
  - `spark_to_expansion_emitter`,
  - `growth_pressure_emitter`,
  - `post_expansion_fission_emitter`.
- Spark emitters must satisfy runtime spark gates after recomputation:
  - detected identity sink survives `_detect_identities`,
  - active degree is exactly 9,
  - column proxy satisfies `min_b |H_s^(b)| < eps_spark`, or instability
    satisfies `cut_out / (cut_out + support_in) >= tau_instability`,
  - runtime parameter damping does not erase the intended potential/flux
    orientation.
- Expansion and reassignment emitters must be downstream of spark:
  - use one canonical saturated sink that emits `spark`,
  - preserve old boundary edges by column,
  - set `D_eff_target`, transfer ratios, and internal bond policy explicitly,
  - require `expansion` lifecycle events before claiming reassignment evidence.
- Growth emitters must satisfy birth predicates:
  - at least one inactive parent port,
  - positive outward flux pressure on the intended parent,
  - high enough `lambda_birth` for deterministic low-step emission,
  - no accidental dependence on fission geometry.
- Fission emitters must be post-expansion diagnostic structures:
  - disable unrelated birth with `lambda_birth = 0`,
  - include an expansion-registry entry or force a spark-to-expansion prelude,
  - construct two persistent sink basins,
  - run at least `identity_fission_persistence_delta + buffer`.
- Budget correction and coarse-cache invalidation are diagnostic unless runtime
  event rows are explicitly added:
  - keep summary/step selectors for the initial pass,
  - only add lifecycle event expectations after runtime emits event rows.
- Acceptance:
  - each emitter has a written theory-to-runtime predicate note,
  - each emitter records why the corresponding S0004 lane failed to emit,
  - S0005 replay runs the repaired emitters with the same low-step policy,
  - spark/expansion/growth/fission expected-event lanes emit their intended
    lifecycle event or record a concrete remaining predicate failure.
- Completed repair run:
  - session:
    `outputs/grc9/phenomenology_discovery/sessions/S0005/`,
  - replay:
    `PYTHONPATH=src ./.venv/bin/python -m pygrc.discovery.grc9_discovery_runner --session-id S0005 --emitter-repair`,
  - result:
    5 repaired emitter lanes, 22 total steps, 27 graph checkpoints, 11
    lifecycle event rows,
  - spark emitters produced `spark` plus `expansion`,
  - growth emitter produced `growth`,
  - post-expansion fission emitter produced confirmed fission summary with no
    unrelated growth events.

### Iteration 5.2: Lifecycle Emitter Perturbation Sweep

After S0005 establishes theory-first lifecycle emitters, run one deterministic
perturbation envelope around the repaired emitters. These are not random
perturbations. Each variant changes a paper/runtime predicate whose direction
is known in advance, then checks whether the observed telemetry preserves or
suppresses the expected lifecycle signature.

- Perturbation families:
  - `spark_column_proxy_eps_pass` / `spark_column_proxy_eps_fail`:
    move `eps_spark` across the strict column-proxy threshold,
  - `spark_instability_tau_pass` / `spark_instability_tau_fail`:
    move `tau_instability` around the constructed instability ratio,
  - `spark_to_expansion_d_eff_low` / `spark_to_expansion_d_eff_high`:
    change `D_eff_target` and compare expansion module size,
  - `growth_pressure_lambda_high` / `growth_pressure_lambda_low`:
    move `lambda_birth` between deterministic and suppressed birth regimes,
  - `post_expansion_fission_min_mass_pass` /
    `post_expansion_fission_min_mass_fail`:
    move the fission basin-mass threshold across the constructed basin masses.
- Acceptance:
  - pass variants preserve the relevant `spark`, `expansion`, `growth`, or
    fission-summary signature,
  - fail variants suppress the targeted signature without changing the parent
    graph family,
  - expansion `D_eff` variants produce different `module_node_count` telemetry,
  - every perturbation records `perturbation_of`, runtime overrides, and
    expected perturbation effect,
  - S0006 is replayable from the session manifest.
- Completed perturbation run:
  - session:
    `outputs/grc9/phenomenology_discovery/sessions/S0006/`,
  - replay:
    `PYTHONPATH=src ./.venv/bin/python -m pygrc.discovery.grc9_discovery_runner --session-id S0006 --emitter-perturbation`,
  - result:
    10 perturbation lanes, 44 total steps, 54 graph checkpoints, 13 lifecycle
    event rows,
  - spark threshold pass variants produced `spark` plus `expansion`,
  - spark threshold fail variants emitted no lifecycle events,
  - `D_eff` low/high variants produced module sizes `5` and `6`,
  - high birth-rate growth emitted 5 `growth` events while low birth-rate
    growth emitted none,
  - fission min-mass pass confirmed one fission window while fail suppressed
    confirmation.

### Iteration 5.3: Lifecycle Combination Examples

Before writing selectors, add composed examples that combine repaired lifecycle
mechanisms in a single run. The goal is to make Iteration 6 validate event
coexistence, ordering, run-summary effects, and cross-surface side effects
instead of only checking isolated event emitters.

- Combination families:
  - `spark_growth_combo`:
    column-proxy spark/expansion plus outward-flux growth pressure,
  - `dual_spark_combo`:
    one column-proxy spark and one instability spark in the same step,
  - `spark_fission_combo`:
    spark/expansion plus a pre-registered post-expansion fission module,
  - `growth_fission_combo`:
    growth pressure plus a pre-registered post-expansion fission module,
  - `spark_growth_fission_combo`:
    spark/expansion, growth pressure, and fission persistence together.
- Acceptance:
  - every combo is a deterministic pure GRC9 graph seed,
  - combo seeds remain replayable with graph checkpoints and telemetry,
  - each combo records component names and predicted telemetry signatures,
  - selectors can use combo runs to validate coexistence and summary-level
    effects,
  - observed expansion-induced fission summaries are recorded as expected
    cross-surface behavior under the current runtime.
- Completed combination run:
  - session:
    `outputs/grc9/phenomenology_discovery/sessions/S0007/`,
  - replay:
    `PYTHONPATH=src ./.venv/bin/python -m pygrc.discovery.grc9_discovery_runner --session-id S0007 --lifecycle-combo`,
  - result:
    5 combination lanes, 24 total steps, 29 graph checkpoints, 156 lifecycle
    event rows,
  - `spark_growth_combo` emitted `spark`, `expansion`, and a growth cascade,
  - `dual_spark_combo` emitted two `spark` and two `expansion` events,
  - `spark_fission_combo` emitted `spark`/`expansion` and confirmed fission,
  - `growth_fission_combo` emitted growth and confirmed fission,
  - `spark_growth_fission_combo` emitted all three event families and confirmed
    two fission windows.
- Topology correction:
  - S0007 remains a historical telemetry session, but its combo graph
    checkpoints are superseded for graph-valid evidence because the composed
    mechanism regions were disconnected components.
  - The combo generator now connects regions with negligible-conductance bridge
    edges so every combo is a single connected GRC9 graph.
  - corrected replay:
    `PYTHONPATH=src ./.venv/bin/python -m pygrc.discovery.grc9_discovery_runner --session-id S0021 --lifecycle-combo`,
  - corrected result:
    5 combination lanes, 24 total steps, 29 connected graph checkpoints, 130
    lifecycle event rows,
  - S0021 replaces S0007 for selector, checkpoint, review, and handoff evidence.

### Iteration 6: Prediction Validation And Candidate Selectors

- Compare predicted signatures with observed telemetry.
- Implement field-backed selectors over generated lanes.
- Write motif candidates into the manifest draft.
- Apply the confidence scoring rubric.
- Current implementation:
  - selector module:
    `src/pygrc/discovery/grc9_selector_validation.py`,
  - selector replay:
    `PYTHONPATH=src ./.venv/bin/python -m pygrc.discovery.grc9_selector_validation --session-id S0008`,
  - selector session:
    `outputs/grc9/phenomenology_discovery/sessions/S0008/`,
  - source sessions:
    `S0004`, `S0005`, `S0006`, `S0007`,
  - result:
    42 validated lanes, 23 selectors, 36 motif candidates, 10 strong
    candidates, 26 candidates, 6 rejected lanes.
- Selector fixture interpretation:
  - S0004 generic positive lanes are rejected when expected lifecycle
    signatures do not appear,
  - S0004 negative/no-event lanes are retained as no-lifecycle candidates,
  - S0005 isolated emitters are candidates,
  - S0006 threshold pass/fail pairs are strong candidates,
  - S0007 combination examples are candidates for coexistence validation.
- Connected evidence replay:
  - S0022 rebuilds selector validation from `S0004`, `S0005`, `S0006`,
    `S0021`, `S0010`, and `S0020`,
  - S0022 validates 57 lanes and 51 motif candidates with 10 strong
    candidates,
  - S0022 supersedes selector/review evidence that depended on disconnected
    S0007 or S0012 graph checkpoints.
- Acceptance:
  - selectors use only saved telemetry artifacts,
  - each candidate records predicted, observed, and missing evidence fields,
  - controls and perturbations are included in the score when available.

### Iteration 6.1: Selector Feedback Targeting

Run the selector feedback loop over `S0008` before adding new examples:

- inspect selector misses and ambiguities,
- decide whether each miss is already covered by existing targeted fixtures,
- identify only the new examples needed for unresolved selector ambiguity,
- do not add random perturbations.

Current implementation:

- feedback module:
  `src/pygrc/discovery/grc9_selector_feedback.py`,
- replay:
  `PYTHONPATH=src ./.venv/bin/python -m pygrc.discovery.grc9_selector_feedback --session-id S0009`,
- session:
  `outputs/grc9/phenomenology_discovery/sessions/S0009/`,
- result:
  11 feedback items:
  - 6 lifecycle misses covered by existing targeted examples from
    `S0005`-`S0007`,
  - 5 diagnostic selector ambiguities that need targeted diagnostic fixture
    pairs.

Targeted diagnostic examples proposed by S0009:

- `row_tensor_strong_anisotropy_control` / `row_tensor_flat_control`,
- `column_proxy_near_zero_control` / `column_proxy_nonzero_control`,
- `coarse_cache_populated_sparse_profile_control` /
  `coarse_cache_populated_dense_profile_control`,
- `budget_uniform_shift_trigger_control` /
  `budget_simplex_projection_trigger_control`,
- `transport_short_path_dominant_control` /
  `transport_long_path_dominant_control`.

Acceptance:

- feedback analysis uses only saved selector validation artifacts,
- lifecycle misses are not used to justify random perturbation,
- proposed new examples are named and tied to concrete selector ambiguity.

### Iteration 6.2: Targeted Diagnostic Fixture Generation

Generate only the targeted diagnostic fixtures proposed by S0009, then replay
selector validation with those fixtures included.

Current implementation:

- fixture generator:
  `generate_grc9_targeted_diagnostic_fixture` in
  `src/pygrc/discovery/grc9_seed_generator.py`,
- runner mode:
  `PYTHONPATH=src ./.venv/bin/python -m pygrc.discovery.grc9_discovery_runner --session-id S0010 --targeted-diagnostic`,
- selector replay:
  `PYTHONPATH=src ./.venv/bin/python -m pygrc.discovery.grc9_selector_validation --session-id S0011 --source-session-id S0004 --source-session-id S0005 --source-session-id S0006 --source-session-id S0007 --source-session-id S0010`,
- fixture session:
  `outputs/grc9/phenomenology_discovery/sessions/S0010/`,
- validation session:
  `outputs/grc9/phenomenology_discovery/sessions/S0011/`.

S0010 fixture lanes:

- row tensor contrast:
  `row_tensor_strong_anisotropy_control`,
  `row_tensor_flat_control`,
- column proxy contrast:
  `column_proxy_near_zero_control`,
  `column_proxy_nonzero_control`,
- coarse/profile contrast:
  `coarse_cache_populated_sparse_profile_control`,
  `coarse_cache_populated_dense_profile_control`,
- budget correction contrast:
  `budget_uniform_shift_trigger_control`,
  `budget_simplex_projection_trigger_control`,
- transport path contrast:
  `transport_short_path_dominant_control`,
  `transport_long_path_dominant_control`.

Important runtime constraint:

- coarse/profile fixtures are zero-step warm-cache captures because normal
  GRC9 runtime steps invalidate the coarse cache at the end of each step.

S0011 result:

- 52 validated lanes across `S0004`, `S0005`, `S0006`, `S0007`, and `S0010`,
- 46 motif candidates,
- 10 strong candidates,
- all 10 targeted diagnostic fixtures pass their lane-specific selectors as
  candidates.

Acceptance:

- fixtures are deterministic and replayable,
- selectors query saved telemetry fields only,
- transport dominance is field-backed by `strongest_flux_edges_sample`,
- budget contrast uses `steps.jsonl` budget correction extension fields,
- coarse/profile contrast uses warm-cache `run_summary.json` fields.

### Iteration 6.3: Complex All-Event Stability Probe

Build one larger graph that combines the event-producing mechanisms from the
repaired emitters into a single run, then perturb it lightly to check that the
selector evidence still appears outside pairwise examples.

Current implementation:

- complex fixture generator:
  `generate_grc9_complex_event_stability_fixture` in
  `src/pygrc/discovery/grc9_seed_generator.py`,
- runner mode:
  `PYTHONPATH=src ./.venv/bin/python -m pygrc.discovery.grc9_discovery_runner --session-id S0012 --complex-event-stability`,
- selector replay:
  `PYTHONPATH=src ./.venv/bin/python -m pygrc.discovery.grc9_selector_validation --session-id S0013 --source-session-id S0004 --source-session-id S0005 --source-session-id S0006 --source-session-id S0007 --source-session-id S0010 --source-session-id S0012`,
- generated-run session:
  `outputs/grc9/phenomenology_discovery/sessions/S0012/`,
- validation session:
  `outputs/grc9/phenomenology_discovery/sessions/S0013/`.

Topology correction:

- S0012/S0013 remain historical selector evidence, but their complex graph
  checkpoints are superseded for visualization because the fixture regions were
  disconnected components.
- S0020 reruns the same complex fixture family after adding low-conductance
  bridge edges between regions, making every saved checkpoint a connected GRC9
  graph while preserving the event profile.
- corrected replay command:
  `PYTHONPATH=src ./.venv/bin/python -m pygrc.discovery.grc9_discovery_runner --session-id S0020 --complex-event-stability`,
- corrected visualization root:
  `outputs/grc9/phenomenology_discovery/sessions/S0020/visualization/complex_all_events_connected/`.

S0012 lanes:

- `all_events_complex_control`,
- `all_events_complex_extra_leaf_perturbation_control`,
- `all_events_complex_coherence_jitter_perturbation_control`,
- `all_events_complex_soft_threshold_perturbation_control`,
- `all_events_complex_high_degree_perturbation_control`.

S0012 result:

- 5 complex lanes,
- 30 total steps,
- 406 event rows,
- each lane emitted at least two spark events, two expansion events, growth,
  and confirmed fission-summary evidence,
- high-degree parameter perturbation increased maximum expansion module size
  from 5 to 6 while retaining all event evidence.

S0013 result:

- 57 validated lanes across `S0004`, `S0005`, `S0006`, `S0007`, `S0010`,
  and `S0012`,
- 51 motif candidates,
- all 5 S0012 complex fixtures pass all 6 lane-specific selectors:
  dual spark, dual expansion, column-proxy spark, instability spark, growth,
  and fission summary.

S0020 connected replay result:

- 5 complex lanes,
- 30 total steps,
- 35 connected graph checkpoints,
- 406 event rows,
- every lane retained spark, expansion, growth, and fission-summary evidence.

Acceptance:

- complex graph includes column-proxy spark, instability spark, growth, and
  pre-registered fission components,
- perturbations include at least one node addition, one coherence perturbation,
  and two runtime-parameter perturbations,
- validation uses saved telemetry fields only.

### Iteration 6.4: Discovery Harness Hardening

Close the small implementation gaps found after the 6.x selector and fixture
work, without adding new scientific examples.

Current implementation:

- perturbation hardening:
  - `generate_grc9_seed_perturbation` now rejects unknown seed parameters,
  - `_apply_delta` now rejects non-numeric base parameters instead of returning
    the raw delta string,
- runner hardening:
  - `run_grc9_discovery_control_session` validates that every planned lane has
    a configured step count before running,
- selector hardening:
  - selector validation reports `no_expectation_lane_count`,
  - selector validation reports `no_expectation_lanes`,
  - summary markdown includes a missing-expectations section when needed.

Replay:

- `PYTHONPATH=src ./.venv/bin/python -m pygrc.discovery.grc9_selector_validation --session-id S0015 --source-session-id S0004 --source-session-id S0005 --source-session-id S0006 --source-session-id S0007 --source-session-id S0010 --source-session-id S0012`

S0015 result:

- 57 lanes validated,
- 51 motif candidates,
- 0 lanes without selector expectations.

Connected replacement:

- S0015 remains historical hardening evidence, but it depended on S0007 and
  S0012 graph fixtures that were later found to be disconnected.
- S0022 rebuilds the same selector surface from connected replacements:
  `S0004`, `S0005`, `S0006`, `S0021`, `S0010`, and `S0020`.
- S0022 result:
  57 lanes validated, 51 motif candidates, 10 strong candidates, and 0 lanes
  without selector expectations.

Deferred to Iteration 8:

- immutable manifest update helpers,
- motif deduplication and cross-session review linkage.

### Iteration 7: Checkpoint Evidence And Visual Index

- Generate a visual index for generated Phase V outputs.
- Link motif windows to nearest graph checkpoints.
- Include checkpoint ids and graph artifact paths.
- Keep visual paths secondary to telemetry evidence fields.
- Current implementation:
  - checkpoint/visual index module:
    `src/pygrc/discovery/grc9_checkpoint_visual_index.py`,
  - replay:
    `PYTHONPATH=src ./.venv/bin/python -m pygrc.discovery.grc9_checkpoint_visual_index --session-id S0014 --selector-session-id S0013`,
  - session:
    `outputs/grc9/phenomenology_discovery/sessions/S0014/`,
  - inputs:
    `outputs/grc9/phenomenology_discovery/sessions/S0013/selector_manifest.json`,
  - outputs:
    `visual_index.json`,
    `reports/checkpoint_visual_index_report.json`,
    `reports/checkpoint_visual_index_summary.md`.
- S0014 result:
  - 51 motif candidates indexed,
  - 145 checkpoint links recorded,
  - 0 records with missing exact checkpoint coverage,
  - all 51 records currently report `visual_status = not_rendered`.
- Iteration 7 hardening:
  - `src/pygrc/discovery/__init__.py` lazily exports the checkpoint index
    and selector feedback runners without preloading their CLI modules,
  - missing top-level selector manifests and selector reports now raise clear
    `FileNotFoundError` messages,
  - malformed individual motifs, including missing `notes.artifact_root`, are
    skipped and recorded instead of failing the whole index,
  - `nearest_before_after` keeps integer step keys internally and stringifies
    them only in JSON output,
  - checkpoint summaries report skipped motifs, total missing exact checkpoint
    steps, and nearest-checkpoint distance max/mean,
  - selector feedback records whether proposed targeted examples are already
    present in the source selector session.
- Hardening replays:
  - `PYTHONPATH=src ./.venv/bin/python -m pygrc.discovery.grc9_checkpoint_visual_index --session-id S0016 --selector-session-id S0015`
    produced 51 motif records, 145 checkpoint links, 0 skipped motifs, and
    0 missing exact checkpoint steps,
  - `PYTHONPATH=src ./.venv/bin/python -m pygrc.discovery.grc9_selector_feedback --session-id S0017 --source-session-id S0015`
    confirmed all 10 diagnostic proposed examples are available in the S0015
    validation surface.
- Connected replacement replays:
  - `PYTHONPATH=src ./.venv/bin/python -m pygrc.discovery.grc9_checkpoint_visual_index --session-id S0023 --selector-session-id S0022`
    produced 51 motif records, 145 checkpoint links, 0 skipped motifs, and
    0 missing exact checkpoint steps,
  - `PYTHONPATH=src ./.venv/bin/python -m pygrc.discovery.grc9_selector_feedback --session-id S0024 --source-session-id S0022`
    produced the same 11 feedback items against the connected selector surface.
- Interpretation:
  - Iteration 7 is an artifact-indexing pass, not a rendering pass,
  - saved graph checkpoints are now linked to motif windows and event steps,
  - visual artifacts remain absent until a downstream rendering pass consumes
    this index.
- Acceptance:
  - every visual link has a corresponding telemetry window,
  - exact and nearest checkpoint matches are distinguished,
  - graph evidence limitations are recorded explicitly.

### Iteration 8: Reviewed Motif Catalog

- Add review status transitions.
- Promote accepted candidates to a stable motif catalog.
- Record rejected and duplicate motifs without deleting them.
- Current implementation:
  - immutable manifest update helpers:
    `GRC9DiscoveryManifest.add_motif`,
    `GRC9DiscoveryManifest.update_motif`, and
    `GRC9DiscoveryManifest.add_review_history`,
  - review module:
    `src/pygrc/discovery/grc9_reviewed_motif_catalog.py`,
  - replay:
    `PYTHONPATH=src ./.venv/bin/python -m pygrc.discovery.grc9_reviewed_motif_catalog --session-id S0018 --selector-session-id S0015`,
  - session:
    `outputs/grc9/phenomenology_discovery/sessions/S0018/`,
  - inputs:
    `outputs/grc9/phenomenology_discovery/sessions/S0015/selector_manifest.json`,
    `outputs/grc9/phenomenology_discovery/sessions/S0015/reports/selector_validation_report.json`,
  - outputs:
    `reviewed_manifest.json`,
    `reviewed_motif_catalog.json`,
    `reports/reviewed_motif_catalog_report.json`,
    `reports/reviewed_motif_catalog_summary.md`.
- Review policy:
  - score-5 motifs become `accepted` and `accepted_after_review`,
  - score-4 motifs become `strong_candidate`,
  - rejected selector validations are restored as rejected motif records with
    explicit `rejection_reason`,
  - duplicate structural signatures are preserved as `duplicate` with
    `notes.duplicate_of`,
  - missing telemetry surfaces become `needs-rerun` and set
    `rerun_requested = true`.
- Review metadata:
  - `reviewer` and `review_timestamp_utc` are runner/CLI parameters,
  - the defaults remain `phase_i08_review_policy` and
    `2026-04-25T00:00:00Z` so S0018 is deterministic and replayable.
- Duplicate semantics:
  - duplicate detection is structural-signature dedupe, not artifact-level
    dedupe,
  - the current key is `(phenomenon, seed_name, predicted_evidence_fields)`,
  - repeated artifacts of the same seed and predicted field family are
    duplicates; distinct seed names remain separate even when they share
    selector fields.
- S0018 result:
  - 57 motifs reviewed,
  - 57 review-history entries recorded,
  - 10 accepted motifs,
  - 41 strong candidates,
  - 6 rejected motifs,
  - 0 duplicates and 0 needs-rerun records in the S0015 source surface.
- Connected replacement:
  - `PYTHONPATH=src ./.venv/bin/python -m pygrc.discovery.grc9_reviewed_motif_catalog --session-id S0025 --selector-session-id S0022`
    rebuilds the reviewed motif catalog from connected selector evidence,
  - S0025 result:
    57 motifs reviewed, 10 accepted motifs, 41 strong candidates, 6 rejected
    motifs, and 0 duplicates or needs-rerun records.
- Acceptance:
  - review history records every status transition,
  - rejected motifs include `rejection_reason`,
  - `needs-rerun` motifs set `rerun_requested = true`,
  - accepted motifs have confidence score `5` or a documented reviewer
    override.

### Iteration 9: GRCL-9 Translation Handoff

- Summarize accepted GRC9-native motifs.
- Identify which motifs are suitable for a later GRCL-9 translation plan.
- Keep translation implementation out of this discovery track.
- Current implementation:
  - handoff module:
    `src/pygrc/discovery/grc9_grcl9_handoff.py`,
  - replay:
    `PYTHONPATH=src ./.venv/bin/python -m pygrc.discovery.grc9_grcl9_handoff --session-id S0019 --reviewed-session-id S0018`,
  - session:
    `outputs/grc9/phenomenology_discovery/sessions/S0019/`,
  - input:
    `outputs/grc9/phenomenology_discovery/sessions/S0018/reviewed_motif_catalog.json`,
  - outputs:
    `grcl9_suitability_catalog.md`,
    `grcl9_suitability_catalog.json`,
    `reports/grcl9_handoff_report.json`.
- The handoff artifact should list:
  - accepted motif id,
  - GRC9 graph preconditions,
  - seed family and parameters,
  - structural properties that a future source lowering would need to preserve,
  - telemetry fields that validated the motif,
  - explicit non-claims.
- S0019 result:
  - 10 accepted GRC9-native motifs included,
  - 0 strong-candidate or rejected motifs included,
  - all entries marked
    `translation_candidate_after_source_lowering_design`,
  - every entry cites telemetry paths, seed parameter path, observed validation
    fields, graph preconditions, and non-claims.
- Connected replacement:
  - `PYTHONPATH=src ./.venv/bin/python -m pygrc.discovery.grc9_grcl9_handoff --session-id S0026 --reviewed-session-id S0025`
    rebuilds the planning handoff from connected reviewed evidence,
  - S0026 result:
    10 accepted GRC9-native motifs included, all still marked
    `translation_candidate_after_source_lowering_design`, with no GRCL-9
    lowering implemented.
- Boundary:
  - the handoff does not implement GRCL-9 lowering,
  - the handoff does not claim any source-language construct exists,
  - accepted motifs remain native GRC9 mechanical graph motifs.

## Acceptance Criteria

- Every candidate motif cites generated telemetry artifact paths.
- Every candidate motif cites a replayable `S0001`-style experiment session.
- Every candidate motif cites a structure hypothesis and predicted telemetry
  signature.
- Every candidate motif cites the deterministic GRC9 seed family and seed
  parameters that generated it.
- Every candidate motif cites observed telemetry field paths as validation
  evidence.
- Graph and visual paths are linked only when the corresponding artifacts
  exist.
- Missing telemetry surfaces are recorded explicitly rather than inferred.
- `cell-1` and `cell-4` are labeled as structural graft fixtures.
- No candidate claims GRCV3, GRCL-9, observer, Lorentzian, FRC, ghost, or
  boundary-horizon semantics.
- No seed is treated as a high-level source object or GRCL lowering.
- The first GRCL-9 planning handoff starts from reviewed GRC9-native motifs,
  not from hand-picked visualization images.

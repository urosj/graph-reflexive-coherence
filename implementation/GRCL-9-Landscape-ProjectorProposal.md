# GRCL-9 Landscape Projector Proposal

## Purpose

This note defines the proposed source-facing `GRCL-9 -> GRC9` landscape
projector boundary.

The goal is precise:

- do not treat current neutral `LandscapeSeed -> GRC9State` projection as
  GRCL-9 lowering,
- do not add source syntax merely to name runtime events directly,
- do not inject solved spark, expansion, growth, or fission outcomes,
- instead define a deterministic family-native assembly contract that can lower
  source-declared GRCL-9 landscape structure into GRC9 mechanical graph
  preconditions.

The first source of truth for the target GRC9 mechanisms is the connected
discovery evidence chain:

- `S0021`: connected lifecycle combination replay,
- `S0020`: connected complex all-event replay,
- `S0022`: selector validation over connected evidence,
- `S0025`: reviewed GRC9-native motif catalog,
- `S0026`: GRCL-9 suitability handoff.

## Evidence And Reference Anchors

This proposal is anchored in these documents and artifacts:

- Vocabulary boundary:
  [GRCL-9-Vocabulary.md](./GRCL-9-Vocabulary.md).
- Existing neutral/family projector boundary:
  [Phase-L-ProjectorBoundary.md](./Phase-L-ProjectorBoundary.md).
- Current neutral GRC9 landscape implementation:
  `src/pygrc/models/grc_9_landscape.py`.
- Current GRC9 runtime mechanism implementation:
  `src/pygrc/models/grc_9.py`.
- Current GRC9 expansion policy helpers:
  `src/pygrc/models/grc_9_expansion.py`.
- Current GRC9 telemetry contract dataclasses:
  `src/pygrc/telemetry/grc9_contract.py`.
- Current GRC9 telemetry extension builders:
  `src/pygrc/telemetry/_grc9_extensions.py`.
- Current GRC9 telemetry contract:
  [Phase-T-GRC9-TelemetryContract.md](./Phase-T-GRC9-TelemetryContract.md).
- GRC9 paper-facing telemetry/implementation track:
  [Phase-T-GRC9-ImplementationPlan.md](./Phase-T-GRC9-ImplementationPlan.md)
  and
  [Phase-T-GRC9-ImplementationChecklist.md](./Phase-T-GRC9-ImplementationChecklist.md).
- GRC9 phenomenology discovery track:
  [GRC9-PhenomenologyDiscovery-Plan.md](./GRC9-PhenomenologyDiscovery-Plan.md)
  and
  [GRC9-PhenomenologyDiscovery-Checklist.md](./GRC9-PhenomenologyDiscovery-Checklist.md).
- Connected experiment log:
  `outputs/grc9/phenomenology_discovery/ExperimentalLog.md`.
- Connected combo replay:
  `outputs/grc9/phenomenology_discovery/sessions/S0021/`.
- Connected complex replay and visualization:
  `outputs/grc9/phenomenology_discovery/sessions/S0020/`.
- Connected selector validation:
  `outputs/grc9/phenomenology_discovery/sessions/S0022/reports/selector_validation_summary.md`.
- Connected checkpoint index:
  `outputs/grc9/phenomenology_discovery/sessions/S0023/reports/checkpoint_visual_index_summary.md`.
- Connected reviewed motif catalog:
  `outputs/grc9/phenomenology_discovery/sessions/S0025/reports/reviewed_motif_catalog_summary.md`.
- GRCL-9 planning handoff:
  `outputs/grc9/phenomenology_discovery/sessions/S0026/grcl9_suitability_catalog.md`.
- Architectural precedent for family-native source layers:
  [GRCL-V3-LoweringArchitectureDecision.md](./GRCL-V3-LoweringArchitectureDecision.md).
- Projector proposal precedent:
  [GRCV3-Landscape-ProjectorProposal.md](./GRCV3-Landscape-ProjectorProposal.md).

The proposal should be read as downstream of S0025/S0026: accepted GRC9-native
motifs identify the mechanical preconditions a future GRCL-9 source layer must
be able to request. They do not themselves become source syntax automatically.

## 1. Current State

There is already a `GRC9` landscape projector in code:

- `src/pygrc/models/grc_9_landscape.py`

That projector consumes neutral `LandscapeSeed` objects and builds a GRC9
port-graph state with:

- one GRC9 node per realized neutral node blueprint,
- one port edge per realized neutral edge blueprint,
- deterministic row-major port assignment,
- conductance from neutral edge mass and transport intent,
- cached provenance such as `landscape_node_id_by_primitive_id` and
  `landscape_edge_id_by_primitive_id`.

This is useful and should remain as a neutral/common landscape path.

It is not yet GRCL-9 lowering.

The current projector:

- bootstraps through `realize_grcv2_landscape_blueprint(...)`,
- does not expose GRCL-9 source constructs,
- does not intentionally assemble spark/growth/expansion/fission precondition
  motifs,
- and does not claim source-language semantics.

Evidence anchors:

- Code surface:
  `src/pygrc/models/grc_9_landscape.py`.
- Projector boundary:
  [Phase-L-ProjectorBoundary.md](./Phase-L-ProjectorBoundary.md).
- Non-claim precedent:
  `outputs/grc9/phenomenology_discovery/sessions/S0026/grcl9_suitability_catalog.md`.

## 2. Diagnosis

GRC9 is not just a weighted graph target. It is a fixed nine-port mechanical
family whose interesting behavior depends on preconditions such as:

- saturated local port charts,
- column-specific diagnostic cancellation or imbalance,
- row-tensor instability evidence,
- inactive port availability for birth,
- expansion module policy,
- column-preserving boundary reassignment,
- and post-expansion two-sink persistence windows.

A neutral landscape projector can preserve basin/channel/support meaning while
still missing these GRC9-specific mechanical preconditions.

So the next source-facing step should not be another generic projector tuning
pass. It should define what a GRCL-9 landscape source is allowed to say so that
lowering can assemble GRC9-native mechanical motifs deterministically.

Evidence anchors:

- Accepted GRC9-native motifs:
  `outputs/grc9/phenomenology_discovery/sessions/S0025/reviewed_motif_catalog.json`.
- Handoff preservation requirements:
  `outputs/grc9/phenomenology_discovery/sessions/S0026/grcl9_suitability_catalog.md`.
- GRC9 telemetry field contract:
  [Phase-T-GRC9-TelemetryContract.md](./Phase-T-GRC9-TelemetryContract.md).

## 3. Boundary Conditions

### 3.1 What Stays Unchanged

- GRC9 runtime equations.
- GRC9 telemetry contract.
- GRC9 graph checkpoint contract.
- Existing neutral `LandscapeSeed` parsing and validation.
- Existing neutral `LandscapeSeed -> GRC9State` projector.
- Connected discovery artifacts S0020-S0026 as evidence, not source syntax.

### 3.2 What Changes

The GRCL-9 track introduces a family-specific source layer and lowering
contract:

- source-visible GRC9 motif declarations,
- deterministic assembly of those declarations into connected GRC9 port graphs,
- explicit source-to-runtime provenance,
- and validation against Phase T-GRC9 telemetry fields.

### 3.3 What Is Explicitly Deferred

- Lorentzian causal-layer semantics.
- Observer-local views.
- GRCL-9 execution semantics beyond lowering to GRC9 initial state.
- Runtime-state injection of solved fluxes, sparks, expansions, fissions, or
  observer conclusions.
- General cross-family projector abstraction.

## 4. Architectural Principle

For GRCL-9, the target should be:

- deterministic family-native assembly

not:

- heuristic interpretation of underspecified neutral landscape structure.

This mirrors the mature `GRCL-v3` boundary: once a family-specific source layer
exists, the lowering step should construct explicit local motifs instead of
guessing them from weaker intermediate semantics.

The source should be allowed to declare structural intent that is specific to
GRC9, such as:

- saturated candidate chart,
- column proxy,
- instability chart,
- expansion module policy,
- birth locus,
- fission persistence geometry.

The source should not declare:

- "spark happened",
- "growth happened",
- "fission confirmed",
- solved current flux values,
- solved row/column diagnostic values,
- or final runtime classifications.

Those remain observed runtime/telemetry outcomes.

Evidence anchors:

- Vocabulary classification:
  [GRCL-9-Vocabulary.md](./GRCL-9-Vocabulary.md).
- Family-native lowering precedent:
  [GRCL-V3-LoweringArchitectureDecision.md](./GRCL-V3-LoweringArchitectureDecision.md).

## 5. Proposed Source Constructs

Revision 1 should introduce only the source constructs needed to reproduce the
accepted S0025 motifs.

Evidence anchors:

- Accepted motif summary:
  `outputs/grc9/phenomenology_discovery/sessions/S0025/reports/reviewed_motif_catalog_summary.md`.
- Suitability catalog:
  `outputs/grc9/phenomenology_discovery/sessions/S0026/grcl9_suitability_catalog.md`.

### 5.1 `spark_candidate_region`

Source purpose:

- declare a local GRC9 region intended to become spark-capable.

Lowering responsibilities:

- assemble one saturated candidate node with all nine ports occupied,
- record deterministic neighbor identities,
- expose port-row and port-column ownership,
- keep the graph connected,
- preserve source provenance for every lowered edge.

Required source knobs:

- candidate id,
- coherence allocation,
- neighbor/coherence profile,
- spark gate intent:
  - `saturation_column_proxy`,
  - `saturation_instability`,
  - optionally reserved `saturation_sign_crossing`.

The intent names intentionally align with the current GRC9 `SparkKind` enum.
`combined` is not a runtime spark kind in Revision 1. A later source schema may
provide a composite fixture helper, but it must lower to runtime-aligned spark
gate intents rather than introducing a new event kind.

Non-claim:

- the source does not claim the spark will fire.

### 5.2 `column_proxy_profile`

Source purpose:

- request the column-diagnostic structure needed for the column-proxy spark
  family.

Lowering responsibilities:

- assign ports in a fixed nine-port chart,
- create controlled column cancellation/imbalance across ports,
- preserve the specific column whose diagnostic should be near the threshold,
- parameterize the construction against the runtime diagnostic:

  ```text
  H_s^(b) = sum_r w(s, p(r,b)) * (C_neighbor(p(r,b)) - C_s)
  ```

  where `s` is the candidate sink, `b` is the chart column, and missing ports
  contribute no term,
- record expected telemetry fields:
  - `family_extensions.grc9.final_column_diagnostic_summary.column_proxy_candidate_count`,
  - spark event evidence `spark_kind`,
  - `family_extensions.grc9.lifecycle_event_counts.spark_column_proxy_count`.

This formula is part of the lowering contract because it distinguishes three
different source designs that otherwise look similar: low-conductance columns,
balanced coherence differences, and deliberate row asymmetry.

Non-claim:

- the source declares structure, not observed diagnostic pass/fail.

### 5.3 `instability_profile`

Source purpose:

- request a saturated chart whose row-tensor/instability branch can be tested.

Lowering responsibilities:

- assemble a saturated candidate node,
- attach an anisotropic support/cut neighborhood,
- preserve threshold parameterization for `tau_instability`,
- parameterize row tensor construction against the runtime row basis:

  ```text
  T_row = lambda_c * C_s
        + xi_c * sum_row w(s,j) * (C_j - C_s)^2
        + zeta_c * (sum_row flux(s,j))^2
  ```

- parameterize cut/support geometry against the runtime instability proxy:

  ```text
  Instability(s) = cut_out(U) / max(cut_out(U) + support_in(U), eps)
  U = {s} union neighbors(s)
  ```

- record expected telemetry fields:
  - `family_extensions.grc9.final_row_tensor_summary`,
  - `spark_evidence.instability_score`,
  - `family_extensions.grc9.lifecycle_event_counts.spark_instability_count`.

Non-claim:

- the source does not write a pre-solved instability score.

### 5.4 `expansion_refinement_region`

Source purpose:

- declare a region where a spark-triggered expansion should be mechanically
  meaningful if runtime predicates pass.

Lowering responsibilities:

- preserve a saturated parent chart,
- record `target_effective_degree`,
- record the runtime node-count formula policy:

  ```text
  n_req = max(1, ceil((D_eff - 2) / 7))
  ```

  with the representative runtime applying its module floor when constructing
  the actual module,
- lower module policy fields:
  - `module_size_formula`,
  - `bond_weight_mode`,
  - `coherence_transfer_mode`,
  - `coherence_transfer_ratios` when declared,
- map source `coherence_transfer_ratios` to normalized runtime
  `distribution_weights`; `equal` lowers to `(1/3, 1/3, 1/3)` and `custom`
  lowers to the normalized custom tuple,
- preserve column-family boundary reassignment.

Expected telemetry fields:

- expansion event evidence `target_effective_degree`,
- expansion event evidence `predicted_module_size`,
- expansion event evidence `coherence_transfer_ratios`,
- `family_extensions.grc9.lifecycle_event_counts.expansion_count`,
- `family_extensions.grc9.expansion_summary.max_module_node_count`.

Non-claim:

- the source does not pre-create a completed runtime expansion unless it is
  explicitly declaring an initial graph motif for a fission test fixture.

### 5.5 `growth_locus`

Source purpose:

- declare an inactive-port birth locus with outward flux pressure potential.

Lowering responsibilities:

- assemble a parent with at least one inactive port,
- create a directional pressure landscape without solved runtime flux injection,
- expose birth rule parameters:
  - `birth_rule`,
  - `lambda_birth`,
  - optional birth threshold controls.
- parameterize controls against the runtime birth probability:

  ```text
  p_birth = 1 - exp(-lambda_birth * outward_flux_pressure)
  ```

Expected telemetry fields:

- growth event evidence `outward_flux_pressure`,
- growth event evidence `birth_probability` when emitted,
- `family_extensions.grc9.lifecycle_event_counts.growth_count`,
- optional `family_extensions.grc9.growth_summary.birth_probability_max` when
  the run summary emits birth-probability statistics.

Non-claim:

- the source does not claim a birth occurs.

### 5.6 `post_expansion_fission_geometry`

Source purpose:

- declare a post-expansion-like two-sink geometry suitable for Appendix E
  persistence-window evaluation.

Lowering responsibilities:

- assemble or reference a refined module region,
- preserve two candidate sink basins,
- expose evaluator parameters:
  - `identity_fission_persistence_delta`,
  - `identity_fission_min_basin_mass`,
- record source provenance for the module and basin members.

Expected telemetry fields:

- `family_extensions.grc9.expansion_summary.identity_fission_confirmed_count`,
- `family_extensions.grc9.expansion_summary.identity_fission_max_persistence_steps`,
- `family_extensions.grc9.identity_abundance.basin_size_max`.

Non-claim:

- the source does not claim GRCV3 hierarchy or GRCL-9 observer semantics.
- the source does not claim fission confirmation; Phase T-GRC9 telemetry may
  evaluate persistence-window evidence after runtime observations exist.

## 6. Connected-Graph Rule

Every lowered GRCL-9 source graph must be connected unless the source contract
explicitly introduces a future multi-component universe concept. Revision 1
does not introduce that concept.

This rule is now mandatory because the disconnected S0007 and S0012 fixtures
were valid as historical telemetry experiments but invalid as graph-valid GRC9
source candidates.

Lowering may use negligible-conductance bridge edges to preserve mechanism
isolation, but those edges must be:

- explicit,
- source-provenanced,
- recorded in graph metadata,
- visible in checkpoints,
- and excluded from claims about strong transport unless telemetry supports
  such a claim.

Revision 1 should represent bridge identity with explicit carriers, not only a
conductance threshold:

- lowered edge payload `grcl9_edge_kind = "bridge"`,
- lowered edge payload `grcl9_bridge = true`,
- optional lowered edge payload `grcl9_bridge_role`,
- `cached_quantities.grcl9_bridge_edge_ids`.

The bridge conductance may be small, but small conductance alone is not enough
to classify an edge as a GRCL-9 bridge.

Evidence anchors:

- Connected replacement log:
  `outputs/grc9/phenomenology_discovery/ExperimentalLog.md`.
- Connected combo replay:
  `outputs/grc9/phenomenology_discovery/sessions/S0021/`.
- Connected complex replay:
  `outputs/grc9/phenomenology_discovery/sessions/S0020/`.
- Checkpoint index over connected evidence:
  `outputs/grc9/phenomenology_discovery/sessions/S0023/reports/checkpoint_visual_index_summary.md`.

## 7. Budget And Port Constraints

GRCL-9 lowering must preserve the GRC9 mechanical constraints.

Required rules:

- no node may exceed nine occupied ports,
- port assignment must be deterministic,
- row and column identity must be stable,
- initialized coherence must preserve declared budget,
- any motif expansion must partition source mass rather than copying it,
- budget preservation policy must be recorded.

Budget partitioning means source mass is conserved across lowered motifs and
runtime expansion policies. In expansion fixtures, parent coherence must be
removed from the parent and distributed to satellites by normalized
`distribution_weights`; it must not be copied into every satellite.

The lowering contract should record the budget policy and observed correction
path taxonomy separately from source intent. Revision 1 should recognize:

- `none`,
- `uniform_shift`,
- `simplex_projection`,
- `proportional_removal`,
- `negative_mass_clamp`,
- `remainder_tracking`.

Only paths actually implemented or observed by the runtime should be claimed in
telemetry; the others remain contract labels for future compatibility.

The first projector revision should reject a source construct if it cannot be
lowered without violating nine-port capacity.

Evidence anchors:

- GRC9 telemetry backend/config and port-chart fields:
  [Phase-T-GRC9-TelemetryContract.md](./Phase-T-GRC9-TelemetryContract.md).
- Current GRC9 landscape port assignment:
  `src/pygrc/models/grc_9_landscape.py`.

## 8. Provenance Contract

Every lowered node and edge should record:

- source construct id,
- source construct kind,
- lowered motif role,
- source-to-GRC9 node/edge membership,
- projector revision,
- and any deterministic assembly policy used.

Concrete carriers for Revision 1:

- top-level `extensions.grcl9` on the source seed,
- primitive-level `extensions.grcl9` on source primitives,
- lowered node/edge payload fields:
  - `grcl9_source_construct_id`,
  - `grcl9_source_construct_kind`,
  - `grcl9_motif_id`,
  - `grcl9_motif_role`,
  - `grcl9_projector_revision`,
- `cached_quantities.grcl9_provenance`,
- `cached_quantities.grcl9_motif_registry`,
- `cached_quantities.grcl9_assembly_policy`,
- `cached_quantities.grcl9_expected_saturated_node_ids`,
- `cached_quantities.grcl9_expected_column_proxy_candidate_ids`,
- `cached_quantities.grcl9_bridge_edge_ids`.

`grcl9_motif_registry` should map motif ids to node ids, edge ids, source
construct ids, and lowered roles. `grcl9_assembly_policy` should record at
least `port_assignment_mode`, `mass_partition_mode`, `bridge_edge_policy`,
`module_size_formula`, `distribution_weight_mode`, and
`budget_preservation_policy`.

Run summaries should expose a compact lowering summary:

- `grcl9_source_schema_version`,
- `grcl9_projector_revision`,
- `grcl9_construct_count_by_kind`,
- `grcl9_lowered_node_count_by_construct`,
- `grcl9_lowered_edge_count_by_construct`,
- `grcl9_bridge_edge_count`,
- `grcl9_non_claims`.

The saturation and column-proxy candidate caches above are expected-lowering
sets, not runtime event registries. Runtime validation should compare them with
port-chart, column-diagnostic, spark, and checkpoint evidence after execution.

This should be separate from GRC9 runtime telemetry. The source-lowering
summary explains construction; Phase T-GRC9 telemetry explains observed
runtime behavior.

Evidence anchors:

- GRC9 family extension pattern:
  [Phase-T-GRC9-TelemetryContract.md](./Phase-T-GRC9-TelemetryContract.md).
- Discovery selector/manifest outputs:
  `outputs/grc9/phenomenology_discovery/sessions/S0022/`.

## 9. Acceptance Criteria

### 9.1 Structural Acceptance

- Lowered graphs are connected.
- No node exceeds nine ports.
- Source-to-node and source-to-edge provenance is complete.
- The same source file lowers deterministically to the same graph.
- Budget preservation is exact within runtime tolerance.

### 9.2 Telemetry Acceptance

For the first accepted GRCL-9 lowering fixtures, telemetry must reproduce the
same classes of evidence as S0025:

- column-proxy spark pass/fail distinction,
- instability spark pass/fail distinction,
- `D_eff` expansion module-size distinction,
- birth-rate growth pass/fail distinction,
- fission persistence pass/fail distinction.

The validation should use field-backed selectors, not visual inspection.

Evidence anchors:

- Connected selector validation:
  `outputs/grc9/phenomenology_discovery/sessions/S0022/reports/selector_validation_summary.md`.
- Connected reviewed motif catalog:
  `outputs/grc9/phenomenology_discovery/sessions/S0025/reports/reviewed_motif_catalog_summary.md`.
- GRCL-9 suitability handoff:
  `outputs/grc9/phenomenology_discovery/sessions/S0026/grcl9_suitability_catalog.md`.

### 9.3 Checkpoint/Visualization Acceptance

- Graph checkpoints exist for every lowered fixture.
- Checkpoints show connected graphs.
- Visuals are rendered only after telemetry/checkpoint evidence exists.
- Visuals are inspection aids, not proof of source semantics.

### 9.4 Boundary Acceptance

Every artifact must state:

- no Lorentzian causal layer,
- no observer-local semantics,
- no GRCV3 hierarchy semantics,
- no solved runtime event injection,
- no GRCL-9 execution semantics beyond lowering to GRC9 state.

## 10. Recommended Iteration Plan

### Iteration 1: Proposal And Contract

- Record this proposal.
- Define the Revision 1 GRCL-9 source construct vocabulary.
- Define a JSON/YAML schema draft or dataclass contract.
- Define lowering non-claims.

### Iteration 2: Lowering Manifest

- Convert S0026 accepted motif requirements into a source-lowering manifest.
- Map each source construct to required GRC9 graph preconditions.
- Map each construct to expected telemetry fields.

### Iteration 3: Minimal Source Fixtures

Create source fixtures for:

- column-proxy spark pass/fail,
- instability spark pass/fail,
- expansion `D_eff` low/high,
- growth `lambda_birth` high/low,
- fission min-mass pass/fail.

These should be source files, not hand-built GRC9 state payloads.

### Iteration 4: Projector Revision 1

Implement a deterministic `GRCL-9 -> GRC9State` assembly path.

The implementation should initially support only the constructs needed by the
Iteration 3 fixtures.

### Iteration 5: Telemetry Replay

Run the lowered fixtures through Phase T-GRC9 telemetry.

Acceptance:

- connected checkpoints,
- selector pass/fail behavior matches source fixture intent,
- no source artifact claims runtime events before observation.

### Iteration 6: Visualization

Render graph and trajectory visuals for accepted lowered fixtures.

Acceptance:

- visuals consume saved telemetry and graph checkpoints,
- graph visuals are connected,
- labels remain GRC9/GRCL-9-boundary accurate.

### Iteration 7: Review And Handoff

Promote only telemetry-validated lowered fixtures into a GRCL-9 source motif
catalog.

This catalog should become the input for any later GRCL-9 language design or
source-authoring work.

## 11. Recommended Next Step

Start with Iteration 1 as a document-only contract slice:

1. accept or revise this proposal,
2. define the GRCL-9 source construct schema,
3. define the lowering manifest fields,
4. define fixture names and expected selectors,
5. only then implement projector code.

That keeps the boundary clean: GRC9 discovery tells us which mechanical
structures matter; GRCL-9 lowering defines how a source can ask for those
structures without pretending the runtime conclusions are known in advance.

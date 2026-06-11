# GRCL-9 Vocabulary

## Purpose

This document defines the theory-facing vocabulary for `GRCL-9`, the proposed
`GRC9`-specific source and lowering surface that sits on top of the neutral
landscape seed layer.

It answers one question precisely:

- what may a `GRCL-9` source express before the GRC9 runtime runs?

This note supports:

- [GRCL-9-Landscape-ProjectorProposal.md](./GRCL-9-Landscape-ProjectorProposal.md)
- `outputs/grc9/phenomenology_discovery/sessions/S0026/grcl9_suitability_catalog.md`
- `src/pygrc/models/grc_9.py`
- `src/pygrc/models/grc_9_expansion.py`
- `src/pygrc/telemetry/grc9_contract.py`

It is not an implementation checklist. It is the vocabulary boundary that later
schema, validation, projector, telemetry, and visualization work must obey.

## 1. Classification Rule

Every GRCL-9 term must be classified as one or more of:

- `source-facing`
  - allowed in GRCL-9 source syntax/schema.
- `lowering-facing`
  - allowed in projector or assembly metadata, but not necessarily in source.
- `runtime-facing`
  - a GRC9 state, parameter, or lifecycle concept produced/used by the runtime.
- `telemetry-facing`
  - an observed field or evidence surface.
- `non-claim`
  - explicitly excluded from GRCL-9 Revision 1 semantics.

This classification is mandatory because GRCL-9 has an easy failure mode:
turning observed GRC9 events into source declarations.

The core rule:

- GRCL-9 source may declare mechanical preconditions and constructive intent.
- GRCL-9 source may not declare solved runtime outcomes.

## 2. Core Distinction

The correct distinction is:

- neutral/common `GRCL` expresses portable landscape ontology,
- `GRCL-9` expresses GRC9-specific mechanical construction intent,
- `GRC9` runtime produces events and state transitions,
- Phase T-GRC9 telemetry records observed evidence.

So `GRCL-9` may say:

- build a saturated nine-port candidate region,
- arrange a column proxy profile,
- assemble a growth locus with inactive port availability,
- preserve expansion module policy,
- preserve a two-sink fission test geometry.

It may not say:

- a spark has occurred,
- a birth has occurred,
- an expansion has completed,
- fission is confirmed,
- this flux value is solved,
- this row tensor or column diagnostic has a fixed runtime value.

## 3. Placement In The Seed Schema

The preferred placement for GRCL-9 Revision 1 is:

- top-level `extensions.grcl9`,
- primitive-level `extensions.grcl9`,
- and, where needed, a GRCL-9 source fixture format that still records its
  neutral landscape seed ancestry.

No GRCL-9 field should be promoted into the neutral/common seed kernel unless
it later proves cross-family.

## 4. Source-Facing Terms

### 4.1 `source_construct`

Classification: `source-facing`

A named GRCL-9 source object that requests a GRC9 mechanical construction.

Examples:

- `spark_candidate_region`
- `column_proxy_profile`
- `growth_locus`

Rules:

- it must be known before runtime,
- it must lower deterministically,
- it must not encode an observed runtime event.

### 4.2 `spark_candidate_region`

Classification: `source-facing`, `lowering-facing`

A source-declared local GRC9 region intended to be mechanically capable of
sparking if runtime predicates pass.

Allowed meaning:

- saturated or near-specified local nine-port chart,
- coherence placement,
- neighbor profile,
- source-side spark gate intent.

Forbidden meaning:

- "this region sparks."

Related telemetry:

- `family_extensions.grc9.lifecycle_event_counts.spark_confirmed_count`
- `family_extensions.grc9.lifecycle_event_counts.spark_column_proxy_count`
- `family_extensions.grc9.lifecycle_event_counts.spark_instability_count`

### 4.3 `spark_gate_intent`

Classification: `source-facing`

Qualitative source-side declaration of which spark mechanism the lowered
structure is intended to test.

Allowed values for Revision 1:

- `saturation_column_proxy`
- `saturation_instability`

Reserved value:

- `saturation_sign_crossing`

The value names intentionally align with the current GRC9 `SparkKind` enum.
Revision 1 may reserve `saturation_sign_crossing`, but it should not require
sign-crossing fixture success until the runtime/telemetry history needed for
that branch is explicitly available.

Deferred value:

- `combined`

`combined` is not a current runtime event kind. A future source schema may use
it as a composite fixture intent, but it must lower to runtime-aligned
mechanism intents rather than inventing a new spark kind.

Forbidden meaning:

- a pass/fail assertion about the runtime gate.

### 4.4 `column_proxy_profile`

Classification: `source-facing`, `lowering-facing`

A source-side profile that asks lowering to build controlled column diagnostic
structure in a fixed nine-port chart.

Allowed meaning:

- target column identity,
- cancellation or imbalance pattern,
- coherence distribution by port group,
- references to `column_diagnostic` and `column_diagnostic_formula`,
- expected diagnostic field paths.

Forbidden meaning:

- solved column diagnostic magnitude.

Related telemetry:

- `family_extensions.grc9.final_column_diagnostic_summary`
- `family_extensions.grc9.lifecycle_event_counts.spark_column_proxy_count`
- spark event evidence fields.

### 4.5 `instability_profile`

Classification: `source-facing`, `lowering-facing`

A source-side profile that asks lowering to build row-tensor or support-cut
anisotropy for the instability spark branch.

Allowed meaning:

- anisotropic support layout,
- threshold parameter references,
- saturated candidate association.
- references to `row_tensor_basis`, `instability_proxy`, and
  `instability_proxy_formula`.

Forbidden meaning:

- solved instability score.

Related telemetry:

- `family_extensions.grc9.final_row_tensor_summary`
- `family_extensions.grc9.lifecycle_event_counts.spark_instability_count`
- spark event instability evidence.

### 4.6 `expansion_refinement_region`

Classification: `source-facing`, `lowering-facing`

A source-side declaration that a local candidate region should lower with the
policy information needed for controlled GRC9 expansion.

Allowed meaning:

- `target_effective_degree`,
- module-size policy reference,
- bond-weight policy,
- coherence transfer policy,
- column-preserving boundary reassignment requirement.

Forbidden meaning:

- a claim that expansion has occurred.

Related telemetry:

- `family_extensions.grc9.expansion_summary.max_module_node_count`
- expansion event evidence fields such as `target_effective_degree`,
  `predicted_module_size`, and `coherence_transfer_ratios`.

### 4.7 `growth_locus`

Classification: `source-facing`, `lowering-facing`

A source-side declaration of a birth-capable region.

Allowed meaning:

- inactive parent port availability,
- directional pressure structure,
- birth rule parameterization,
- source-side distinction between pass and fail controls.

Forbidden meaning:

- a claim that a new runtime node is born.

Related telemetry:

- `family_extensions.grc9.lifecycle_event_counts.growth_count`
- `family_extensions.grc9.growth_summary.birth_probability_max` when emitted
- growth event evidence `birth_probability` when emitted

### 4.8 `post_expansion_fission_geometry`

Classification: `source-facing`, `lowering-facing`

A source-side declaration of a two-sink geometry suitable for the GRC9
identity-fission persistence evaluator.

Allowed meaning:

- refined-module-like local structure,
- two candidate sink basins,
- persistence window parameter,
- minimum basin mass parameter.

Forbidden meaning:

- GRCV3 hierarchy,
- source-level identity split,
- observer-local fission event.

Related telemetry:

- `family_extensions.grc9.expansion_summary.identity_fission_confirmed_count`
- `family_extensions.grc9.expansion_summary.identity_fission_max_persistence_steps`

### 4.9 `structural_collapse_probe`

Classification: `source-facing`, `lowering-facing`, `reserved_future`

A source-side structural probe for collapse-adjacent GRC9 geometry.

Allowed meaning:

- membrane/ridge weakening or rupture intent,
- basin merge pressure,
- support-loss or sink-dominance-loss geometry,
- failed fission persistence setup,
- saddle pressure without GRCV3 choice semantics.

Forbidden meaning:

- runtime collapse occurred,
- GRCV3 choice collapse,
- source-level ComposingCells dysfunction has been solved by GRC9.

Related status:

- no current Phase T-GRC9 `collapse` lifecycle domain,
- no current Phase T-GRC9 `collapse_evidence` group,
- planned for the next GRCL-9 work batch, where it may become
  structural-only, diagnostic-only, or deferred after the collapse
  observability review.

## 5. Lowering-Facing Terms

### 5.1 `lowered_motif`

Classification: `lowering-facing`

The concrete GRC9 graph fragment assembled from one or more source constructs.

Rules:

- it must be deterministic,
- it must preserve provenance,
- it must obey nine-port capacity,
- it must not include solved runtime conclusions.
- it should be represented concretely by `grcl9_motif_registry` and by
  node/edge payload fields such as `grcl9_motif_id` and `grcl9_motif_role`.

### 5.2 `assembly_policy`

Classification: `lowering-facing`

The deterministic rule used to turn a source construct into GRC9 nodes, ports,
edges, coherence allocation, and metadata.

Examples:

- port ordering policy,
- mass partition policy,
- bridge edge policy,
- module-size formula policy.

Concrete carrier:

- `cached_quantities.grcl9_assembly_policy`

Expected fields:

- `port_assignment_mode`
- `mass_partition_mode`
- `bridge_edge_policy`
- `module_size_formula`
- `distribution_weight_mode`
- `budget_preservation_policy`

### 5.3 `bridge_edge`

Classification: `lowering-facing`, `runtime-facing`

A low-conductance edge used to keep separately testable mechanism regions in a
single connected GRC9 graph.

Rules:

- it must be explicit,
- it must be source-provenanced or projector-provenanced,
- it must be visible in checkpoints,
- it must not be used as evidence of strong transport unless telemetry supports
  that claim.

Concrete carriers:

- edge payload field `grcl9_edge_kind = "bridge"`
- edge payload field `grcl9_bridge = true`
- optional edge payload field `grcl9_bridge_role`
- `cached_quantities.grcl9_bridge_edge_ids`

Bridge identity should be explicit metadata, not inferred only from a
conductance threshold.

### 5.4 `source_provenance`

Classification: `lowering-facing`, `telemetry-facing`

Metadata linking each lowered node/edge back to a source construct.

Recommended fields:

- source construct id,
- source construct kind,
- lowered motif role,
- projector revision,
- source member path.

Concrete carriers:

- top-level `extensions.grcl9`
- primitive-level `extensions.grcl9`
- lowered node/edge payload fields `grcl9_source_construct_id`,
  `grcl9_source_construct_kind`, and `grcl9_motif_role`
- `cached_quantities.grcl9_provenance`

### 5.5 `projector_revision`

Classification: `lowering-facing`, `telemetry-facing`

Stable identifier for a deterministic GRCL-9 lowering implementation.

Example:

- `grcl9_projector_rev1`

Changing assembly rules should change the projector revision or add an explicit
revision note.

### 5.6 `grcl9_motif_registry`

Classification: `lowering-facing`, `telemetry-facing`

Concrete lowered-state registry that maps each lowered motif id to its lowered
node ids, edge ids, source construct ids, and motif roles.

Recommended carrier:

- `cached_quantities.grcl9_motif_registry`

### 5.7 `grcl9_expected_saturated_node_ids`

Classification: `lowering-facing`, `telemetry-facing`

Lowering-side expectation set for nodes that were intentionally assembled as
saturated nine-port candidates.

This is not a runtime event registry. Runtime validation should compare it
against port-chart telemetry and checkpoint topology.

Recommended carrier:

- `cached_quantities.grcl9_expected_saturated_node_ids`

### 5.8 `grcl9_expected_column_proxy_candidate_ids`

Classification: `lowering-facing`, `telemetry-facing`

Lowering-side expectation set for nodes intentionally assembled to exercise the
column-proxy diagnostic branch.

This does not claim a column-proxy spark. Runtime validation should use
column-diagnostic telemetry and spark event evidence.

Recommended carrier:

- `cached_quantities.grcl9_expected_column_proxy_candidate_ids`

## 6. Runtime-Facing Terms

These terms belong to GRC9 runtime mechanics. GRCL-9 may create preconditions
for them, but should not claim their occurrence before runtime.

### 6.1 `spark`

Classification: `runtime-facing`, `telemetry-facing`

A GRC9 lifecycle event emitted by the runtime.

Source rule:

- use `spark_candidate_region`, not `spark`, in source.

### 6.2 `expansion`

Classification: `runtime-facing`, `telemetry-facing`

A GRC9 lifecycle event that refines a spark-triggered parent into a module.

Source rule:

- use `expansion_refinement_region`, not `expansion_completed`, in source.

### 6.3 `growth`

Classification: `runtime-facing`, `telemetry-facing`

A GRC9 lifecycle event that creates a new node through birth dynamics.

Source rule:

- use `growth_locus`, not `birth_event`, in source.

### 6.4 `identity_fission_confirmation`

Classification: `runtime-facing`, `telemetry-facing`

Run-summary evidence that the persistence-window evaluator observed a stable
two-sink condition.

Source rule:

- use `post_expansion_fission_geometry`, not `fission_confirmed`, in source.

Boundary:

- this is telemetry/run-summary evidence, not a GRCL-9 source semantic and not
  a claim of GRCV3 hierarchy.

### 6.5 `target_effective_degree`

Classification: `source-facing`, `runtime-facing`, `telemetry-facing`

The `D_eff` value used by GRC9 expansion policy.

This is allowed in source because it is a policy parameter, not a solved event.

### 6.6 `coherence_transfer_ratios`

Classification: `source-facing`, `runtime-facing`, `telemetry-facing`

Expansion policy ratios used for distributing coherence among satellite nodes.

Allowed in source only as a policy declaration. Observed ratios remain runtime
event evidence.

Runtime mapping:

- source-declared `coherence_transfer_ratios` lower to GRC9 expansion
  `distribution_weights`.
- the runtime record stores the normalized tuple as
  `ExpansionRecord.distribution_weights`.

### 6.7 `birth_rule`

Classification: `source-facing`, `runtime-facing`, `telemetry-facing`

The rule family used to compute birth probability.

Revision 1 expected value:

- `outward_flux_pressure`

Allowed in source as a rule selection, not as a birth event claim.

### 6.8 `column_diagnostic`

Classification: `runtime-facing`, `telemetry-facing`

The GRC9 per-column diagnostic targeted by `column_proxy_profile`.

Source rule:

- source may request structures intended to make this diagnostic small or
  imbalanced, but may not assert the solved diagnostic value.

### 6.9 `column_diagnostic_formula`

Classification: `lowering-facing`, `runtime-facing`, `telemetry-facing`

For a candidate sink `s` and chart column `b`, the runtime computes a column
sum over the three row ports in that column:

```text
H_s^(b) = sum_r w(s, p(r,b)) * (C_neighbor(p(r,b)) - C_s)
```

Missing ports contribute no term. This formula lets a source author distinguish
low-conductance cancellation, balanced coherence differences, and deliberate
row asymmetry.

### 6.10 `instability_proxy`

Classification: `runtime-facing`, `telemetry-facing`

The GRC9 instability score targeted by `instability_profile`.

Source rule:

- source may create support/cut geometry intended to raise or lower the proxy,
  but may not assert the solved score.

### 6.11 `instability_proxy_formula`

Classification: `lowering-facing`, `runtime-facing`, `telemetry-facing`

For sink `s`, with `U = {s} union neighbors(s)`, the runtime proxy is:

```text
Instability(s) = cut_out(U) / max(cut_out(U) + support_in(U), eps)
```

This makes anisotropic support and cut geometry first-class lowering concerns
without turning their result into a source claim.

### 6.12 `row_tensor_basis`

Classification: `lowering-facing`, `runtime-facing`, `telemetry-facing`

The row tensor diagonal uses three runtime terms per row:

```text
T_row = lambda_c * C_s
      + xi_c * sum_row w(s,j) * (C_j - C_s)^2
      + zeta_c * (sum_row flux(s,j))^2
```

Lowering may target the coherence, mismatch, or flux-feedback term by graph
construction, but telemetry decides the observed row tensor values.

### 6.13 `birth_probability_formula`

Classification: `lowering-facing`, `runtime-facing`, `telemetry-facing`

For growth dynamics, the runtime computes:

```text
p_birth = 1 - exp(-lambda_birth * outward_flux_pressure)
```

Source may declare `lambda_birth` and a pressure-producing structure, not an
observed birth.

### 6.14 `expansion_node_count_formula`

Classification: `lowering-facing`, `runtime-facing`, `telemetry-facing`

The runtime expansion helper maps effective degree to requested node count:

```text
n_req = max(1, ceil((D_eff - 2) / 7))
```

The representative runtime then applies its module floor when constructing the
actual module. Source fixtures should record both `target_effective_degree` and
the module-size formula policy.

### 6.15 `expansion_distribution_weights`

Classification: `source-facing`, `runtime-facing`, `telemetry-facing`

The normalized runtime tuple used to distribute parent coherence among the
three canonical expansion satellites.

Mapping:

- source `coherence_transfer_ratios` -> normalized runtime
  `distribution_weights`
- source `expansion_distribution_mode = "equal"` -> `(1/3, 1/3, 1/3)`
- source `expansion_distribution_mode = "custom"` -> normalized custom tuple

### 6.16 `budget_preservation_policy`

Classification: `lowering-facing`, `runtime-facing`, `telemetry-facing`

Policy and correction path used to keep coherence budget exact within runtime
tolerance.

Revision 1 should distinguish:

- `none`
- `uniform_shift`
- `simplex_projection`
- `proportional_removal`
- `negative_mass_clamp`
- `remainder_tracking`

Source lowering must partition source mass rather than copying it. During
expansion, parent coherence is removed from the parent and distributed to
satellites by `expansion_distribution_weights`.

## 7. Telemetry-Facing Terms

### 7.1 `observed_evidence_field`

Classification: `telemetry-facing`

A field path observed in saved telemetry and used for validation.

Examples:

- `family_extensions.grc9.lifecycle_event_counts.spark_confirmed_count`
- `family_extensions.grc9.expansion_summary.max_module_node_count`
- `family_extensions.grc9.growth_summary.birth_probability_max` when emitted

### 7.2 `expected_selector`

Classification: `telemetry-facing`, `lowering-facing`

A field-backed query that a lowered fixture is expected to satisfy after
runtime execution.

Rules:

- selectors must query telemetry artifacts,
- selectors must not inspect source declarations alone,
- selectors must distinguish expected absence from missing evidence.

### 7.3 `graph_checkpoint`

Classification: `telemetry-facing`, `runtime-facing`

A saved graph-state artifact used to verify topology, port occupancy, and
visualization inputs.

GRCL-9 acceptance requires connected checkpoints for lowered fixtures.

## 8. Non-Claims

The following terms are explicitly not GRCL-9 Revision 1 semantics.

### 8.1 `observer_local_view`

Classification: `non-claim`

Not part of GRCL-9 Revision 1.

### 8.2 `lorentzian_causal_layer`

Classification: `non-claim`

Not part of GRCL-9 Revision 1.

### 8.3 `grcv3_hierarchy`

Classification: `non-claim`

GRC9 fission telemetry must not be described as GRCV3 hierarchy.

### 8.4 `solved_flux`

Classification: `non-claim`

GRCL-9 source may declare transport intent or pressure structure, but not
pre-solved runtime flux.

### 8.5 `solved_diagnostic`

Classification: `non-claim`

GRCL-9 source may declare a diagnostic-generating structure, but not a solved
row tensor, column diagnostic, instability score, or spark gate result.

### 8.6 `event_injection`

Classification: `non-claim`

GRCL-9 source must not inject spark, expansion, growth, or fission events into
runtime history.

### 8.7 `runtime_collapse`

Classification: `non-claim`

Not part of GRCL-9 Revision 1 unless a later Phase T-GRC9 contract explicitly
defines GRC9-native collapse evidence.

GRCL-9 may author `structural_collapse_probe` fixtures, but those fixtures are
not proof that collapse occurred.

## 9. Term Mapping

| GRCL-9 Term | Classification | GRC9 Runtime/Telemetry Surface |
|---|---|---|
| `spark_candidate_region` | source, lowering | spark event evidence after runtime |
| `column_proxy_profile` | source, lowering | column diagnostic and spark-column-proxy telemetry |
| `instability_profile` | source, lowering | row tensor and spark-instability telemetry |
| `expansion_refinement_region` | source, lowering | expansion event and run-summary telemetry |
| `growth_locus` | source, lowering | growth event and birth-probability telemetry |
| `post_expansion_fission_geometry` | source, lowering | fission persistence run-summary telemetry |
| `structural_collapse_probe` | source, lowering, reserved_future | no current collapse telemetry; possible future diagnostic-only surface |
| `lowered_motif` | lowering | `cached_quantities.grcl9_motif_registry`, graph checkpoint topology |
| `assembly_policy` | lowering | `cached_quantities.grcl9_assembly_policy` |
| `bridge_edge` | lowering, runtime | edge payload `grcl9_edge_kind`, `cached_quantities.grcl9_bridge_edge_ids`, checkpoint edge records |
| `source_provenance` | lowering, telemetry | `extensions.grcl9`, lowered node/edge payloads, `cached_quantities.grcl9_provenance` |
| `column_diagnostic_formula` | lowering, runtime, telemetry | column diagnostic telemetry |
| `instability_proxy_formula` | lowering, runtime, telemetry | spark instability evidence |
| `row_tensor_basis` | lowering, runtime, telemetry | final row tensor summary |
| `birth_probability_formula` | lowering, runtime, telemetry | growth event evidence and optional growth summary |
| `expansion_node_count_formula` | lowering, runtime, telemetry | expansion evidence and summary |
| `expansion_distribution_weights` | source, runtime, telemetry | expansion event distribution weights / coherence transfer ratios |
| `budget_preservation_policy` | lowering, runtime, telemetry | backend config and budget correction telemetry |
| `observed_evidence_field` | telemetry | selector validation |

## 10. Vocabulary Gate

Before adding a new GRCL-9 term, answer:

1. Is it known before runtime?
2. Is it structural or policy-level rather than solved state?
3. Does it lower deterministically into GRC9 graph/state preconditions?
4. Does telemetry, not source syntax, decide whether the intended behavior
   actually occurred?
5. Is it free of GRCV3, observer, and Lorentzian claims?

If any answer is "no", the term does not belong in GRCL-9 Revision 1.

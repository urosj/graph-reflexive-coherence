# GRCL-9V3 Vocabulary

## Purpose

This document defines the first vocabulary boundary for **GRCL-9V3**, the
source-seed layer that should lower authored GRCL/Morse-style source
statements into deterministic `GRC9V3` runtime seeds.

`GRCL-9V3` is not a new runtime family and not a replacement for `GRC9V3`.
It is a source/lowering layer downstream of:

- `GRC9V3` core runtime,
- Phase T-GRC9V3 telemetry,
- Phase V-GRC9V3 visualization,
- GRC9V3 phenomenology discovery,
- and the S0014 source-language handoff.

The source layer may declare structure, policy, and intended preconditions.
It must not declare solved runtime outcomes.

## Source Boundary

Allowed source statements:

- a saturated critical region should exist,
- a row-basis Hessian/tensor gate should be made structurally plausible,
- a boundary stratum should expose inactive-port outward pressure,
- two basin regions should be separated by a weak saddle/bridge,
- a collapse target selector should be configured by source-side basin geometry,
- a refinement locus should request an effective degree target.

Forbidden source statements:

- spark happened,
- expansion happened,
- choice happened,
- collapse happened,
- growth happened,
- a daughter sink was confirmed,
- a signed-Hessian value or flux field is solved in source,
- telemetry event counts are embedded in the source fixture.

Runtime events remain observations recorded through Phase T-GRC9V3 telemetry.

## Vocabulary Strata

GRCL-9V3 should keep three strata separate.

### GRCL/Morse Source Terms

These terms describe authored landscape structure:

- `critical_region`
- `stable_basin`
- `unstable_direction`
- `separatrix`
- `saddle_bridge`
- `boundary_stratum`
- `gradient_pressure`
- `refinement_locus`
- `post_refinement_two_sink_region`
- `choice_basin_pair`
- `collapse_target_region`
- `hybrid_tensor_hotspot`

These are source-facing terms. They do not carry runtime event claims.

### GRCL-9V3 Source Constructs

These are family-native source constructs that can lower into `GRC9V3` graph
and state structure:

- `hybrid_spark_region`
- `row_basis_hessian_profile`
- `hybrid_tensor_profile`
- `column_proxy_fallback_profile`
- `expansion_refinement_region`
- `choice_collapse_region`
- `growth_locus`
- `transport_rerouting_region`
- `appendix_e_division_region`
- `quiescent_hybrid_region`

These constructs should live under:

```text
src/pygrc/landscapes/extensions/grcl9v3/
```

They should not live under `src/pygrc/grcl9v3/`.

### Runtime Observations

These are not source vocabulary. They are observed after replay:

- `hybrid_spark_candidate`
- `hybrid_mechanical_expansion`
- `hybrid_spark_completed`
- `choice_detected`
- `collapse`
- `growth`
- lifecycle event counts
- tensor summaries
- row-basis differential summaries
- transport summaries
- hierarchy summaries
- budget and coarse-cache diagnostics

## Source Constructs

### `hybrid_spark_region`

Purpose:

- declare a saturated candidate region whose local geometry can trigger the
  hybrid spark gate.

Lowering must preserve:

- nine-port saturation,
- row/column occupancy,
- source construct id,
- candidate node provenance,
- expected telemetry selectors.

Related runtime evidence:

- `family_extensions.grc9v3.lifecycle_event_counts.hybrid_spark_candidate_count`
- `family_extensions.grc9v3.lifecycle_event_counts.hybrid_mechanical_expansion_count`
- `family_extensions.grc9v3.lifecycle_event_counts.hybrid_spark_completed_count`
- `family_extensions.grc9v3.hybrid_spark_state`

### `row_basis_hessian_profile`

Purpose:

- declare row-basis differential structure that targets the Appendix G
  Hessian/tensor spark gate.

Lowering must preserve:

- row-basis direction labels,
- Hessian backend policy,
- signed-Hessian history capability status,
- source-side distinction between row-basis diagonal and WLS comparison lanes.

Related runtime evidence:

- `family_extensions.grc9v3.row_basis_differential`
- `family_extensions.grc9v3.hybrid_tensor`
- `family_extensions.grc9v3.hybrid_spark_state.signed_crossing_status`

### `hybrid_tensor_profile`

Purpose:

- declare tensor anisotropy or row-mismatch concentration without embedding a
  solved tensor.

Lowering must preserve:

- row mismatch intent,
- anisotropy target direction,
- tensor hotspot candidate provenance.

Related runtime evidence:

- `family_extensions.grc9v3.hybrid_tensor.tensor_trace_mean`
- `family_extensions.grc9v3.hybrid_tensor.tensor_anisotropy_max`
- `family_extensions.grc9v3.hybrid_tensor.row_mismatch_sum_max`

### `column_proxy_fallback_profile`

Purpose:

- allow a GRC9-style column proxy fallback to be present as a source
  precondition, while making clear that the hybrid gate is GRC9V3-specific.

Lowering must preserve:

- target column,
- near-cancellation or imbalance mode,
- column/row occupancy intent,
- fallback-only status when the primary Hessian gate is under test.

Related runtime evidence:

- `family_extensions.grc9v3.hybrid_spark_state`
- `family_extensions.grc9v3.hybrid_tensor.row_mismatch_sum_max`

### `expansion_refinement_region`

Purpose:

- declare an effective-degree refinement locus and expansion policy.

Lowering must preserve:

- target effective degree,
- expansion distribution mode,
- internal module conductance policy,
- source-to-module provenance.

Related runtime evidence:

- `family_extensions.grc9v3.lifecycle_event_counts.hybrid_mechanical_expansion_count`
- `family_extensions.grc9v3.expansion_summary`
- `family_extensions.grc9v3.hierarchy_state`

### `choice_collapse_region`

Purpose:

- declare a Morse-style competing-basin condition and a collapse target region.

Lowering must preserve:

- candidate basin pair,
- compatibility/collapse selector policy,
- target-region provenance,
- no claim that choice or collapse already happened.

Related runtime evidence:

- `family_extensions.grc9v3.lifecycle_event_counts.choice_detected_count`
- `family_extensions.grc9v3.lifecycle_event_counts.collapse_count`
- `family_extensions.grc9v3.choice_collapse`
- `family_extensions.grc9v3.final_identity_basin_summary`

### `growth_locus`

Purpose:

- declare a boundary stratum with inactive port availability and outward flux
  pressure.

Lowering must preserve:

- inactive parent port,
- outward pressure direction,
- `lambda_birth` policy,
- child attachment provenance.

Related runtime evidence:

- `family_extensions.grc9v3.lifecycle_event_counts.growth_count`
- `family_extensions.grc9v3.growth_state`
- `family_extensions.grc9v3.transport`

### `transport_rerouting_region`

Purpose:

- declare source-side route or basin-rerouting pressure without claiming a
  runtime route result.

Lowering must preserve:

- high/low conductance corridor contrast,
- potential gradient intent,
- basin redirection source labels.

Related runtime evidence:

- `family_extensions.grc9v3.transport.flux_abs_sum`
- `family_extensions.grc9v3.transport.potential_min`
- `family_extensions.grc9v3.transport.potential_max`
- `family_extensions.grc9v3.final_identity_basin_summary`

### `appendix_e_division_region`

Purpose:

- declare an Appendix E-style source condition for a spark/refinement region
  that can form daughter sink evidence.

Lowering must preserve:

- parent region,
- daughter candidate regions,
- module basin support,
- hierarchy provenance,
- non-claim that source itself confirms daughter sinks.

Related runtime evidence:

- `family_extensions.grc9v3.representative_appendix_e_summary`
- `family_extensions.grc9v3.hierarchy_state`
- `family_extensions.grc9v3.final_identity_basin_summary`

### `quiescent_hybrid_region`

Purpose:

- declare a negative/no-event source control that should remain below spark,
  growth, choice, and collapse thresholds.

Lowering must preserve:

- sub-saturation or stable-support source condition,
- no-event expectation as a fixture role, not a runtime claim,
- threshold margin notes for later selector review.

Related runtime evidence:

- zero lifecycle counts in `family_extensions.grc9v3.lifecycle_event_counts`
- stable budget and identity summaries.

## Runtime-Only Records

The S0014 handoff marks some records as runtime-only. These should not become
first-class source constructs in Revision 1:

- Hessian backend comparator records,
- budget preservation diagnostics,
- coarse-cache invalidation diagnostics.

They may still influence source fixture validation, but they should remain
runtime invariants or implementation diagnostics unless a later handoff shows a
source-facing construct is actually needed.

## Required Non-Claims

Every GRCL-9V3 source document should carry:

- `no_grcl9v3_lowering_result_claim`
- `no_runtime_event_claim`
- `no_lorentzian_causal_layer_claim`
- `no_visual_only_promotion`
- `runtime_evidence_required`


# N25.1 Iteration 1 - Source Crosswalk And Gap Inventory

Status: `passed`

Acceptance state: `accepted_source_crosswalk_gap_inventory_no_runtime_implementation`

Output digest: `125a487cb0514535616ee5c7385f6ea566eca6fedac4c1657a77a75693bd845c`

Crosswalk rows: `11`; source records: `13`.

## Interpretation

I1 is a source/spec inventory only. It confirms that RC/GRC/GRC9V3 already contain spark and mechanical-refinement machinery, and that LGRC9V3 already has causal spark-candidate and refinement-transport surfaces. The missing target is narrower: a native LGRC9V3 extension that carries causal refinement through child-basin extraction, merge/leakage controls, replay, and N26-ready multi-basin substrate evidence.

This artifact does not implement that extension and does not open runtime multi-basin evidence.

## Source Rows

| Row | Source | Classification | Decision | Gap Contribution |
| --- | --- | --- | --- | --- |
| `n25_1_i1_row_01_grc9_mechanical_spark_refinement` | `papers/2026-04-GRC-9.md` | `theory_and_mechanical_spec` | `supported_as_requirements_source` | Provides refinement mechanics but leaves child-basin formation to later flow, persistence, and controls. |
| `n25_1_i1_row_02_grcv3_basin_attribute_child_identity_semantics` | `papers/2026-02-GRC-V3.md` | `theory_and_semantic_spec` | `supported_as_requirements_source` | Defines what child-basin semantics must mean, but does not itself provide LGRC9V3 causal runtime evidence. |
| `n25_1_i1_row_03_lgrc9_causal_history_constraints` | `papers/2026-05-LGRC-9.md` | `causal_history_theory_spec` | `supported_as_requirements_source` | Future multi-basin formation must be causal-history-safe, not a synchronous relabel or checkpoint artifact. |
| `n25_1_i1_row_04_native_packet_loop_specialization` | `papers/2026-05-LGRC9V3-Native-Packet-Loops.md` | `validated_implementation_specialization` | `supported_as_requirements_source` | Shows a valid producer/step boundary and packet budget model that a future multi-basin extension must preserve. |
| `n25_1_i1_row_05_causal_pulse_surface_proposal` | `papers/2026-05-LGRC9V3-Causal-Pulse-Substrate-Surfaces.md` | `proposed_implementation_specialization` | `supported_as_requirements_source` | Provides a disciplined extension pattern but cannot be used as runtime evidence that a multi-basin surface already exists. |
| `n25_1_i1_row_06_grc9v3_spec_current_hybrid_spark_contract` | `specs/grc-9-v3-spec.md` | `implementation_spec` | `supported_as_requirements_source` | Establishes that spark/refinement is not invented by N25.1; the missing part is the LGRC9V3 causal extension surface. |
| `n25_1_i1_row_07_lgrc9v3_spec_current_slice_boundary` | `specs/lgrc-9-v3-spec.md` | `current_implementation_spec_and_boundary` | `supported_as_gap_boundary_source` | This is the central N25.1 gap: causal spark evidence exists, but the extension surface from causal refinement to replayable child-basin persistence is missing. |
| `n25_1_i1_row_08_phase7_grc9v3_representative_evidence` | `implementation/Phase-7-Closeout.md` | `historical_runtime_evidence` | `supported_as_historical_context` | Confirms GRC9V3 spark-ish behavior exists, but keeps N25.1 from relabeling old synchronous evidence as LGRC9V3 native multi-basin formation. |
| `n25_1_i1_row_09_phase8_lgrc9_implementation_plan_boundary` | `implementation/Phase-8-LGRC9-ImplementationPlan.md` | `implementation_plan_boundary` | `supported_as_requirements_source` | N25.1 should follow the same explicit extension discipline rather than modifying the main runtime silently. |
| `n25_1_i1_row_10_lgrc9v3_examples_spark_and_transport_surfaces` | `examples/lgrc9v3/README.md` | `current_example_boundary` | `supported_as_current_example_context` | Confirms N25.1 must not pretend sparks are absent; it must specify the missing child-basin formation and persistence surface after the existing spark/transport boundary. |
| `n25_1_i1_row_11_n25_closeout_scope_boundary` | `experiments/2026-06-N25-lgrc-spark-sub-basin-new-basin-formation/outputs/n25_closeout_and_n26_handoff.json` | `current_experiment_closeout` | `supported_as_current_boundary_source` | N25.1 exists because N25 reached N26 readiness only under scope constraints; independent multi-basin substrate requires a new extension contract. |

## Existing Spark Surface Boundary

```text
GRC-9 mechanical sparks: present as theory/spec.
GRC9V3 hybrid sparks and child stabilization: present in spec and Phase 7 evidence.
LGRC9V3 causal spark candidates: present in current examples/spec.
LGRC9V3 refinement packet transport: present as a bounded surface.
N25.1 gap: not spark absence; missing native causal multi-basin formation extension.
```

## Missing Runtime Surfaces

| Surface | Status | Required By |
| --- | --- | --- |
| `causal_refinement_event_to_topology_integration` | `missing_as_native_multi_basin_extension_surface` | `MB1, MB2` |
| `post_refinement_child_basin_extraction` | `missing_as_replayable_child_basin_surface` | `MB3` |
| `merge_leakage_and_relabel_controls` | `missing_as_control_matrix_for_multi_basin_claim` | `MB4, MB5, MB6` |

## Claim Boundary

```text
runtime_implementation_opened = false
phase8_extension_implemented = false
multi_basin_evidence_opened = false
native_multi_basin_formation_supported = false
BF6_supported = false
```

## Checks

| Check | Passed |
| --- | --- |
| `all_cited_sources_exist` | `true` |
| `n25_closeout_consumed_as_boundary_not_success_upgrade` | `true` |
| `existing_spark_surfaces_preserved` | `true` |
| `missing_multi_basin_runtime_surface_recorded` | `true` |
| `runtime_implementation_remains_closed` | `true` |
| `unsafe_claim_flags_false` | `true` |
| `no_absolute_paths_in_records` | `true` |

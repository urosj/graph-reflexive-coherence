# GRCv4 Exploratory Side Tool

**Status:** Iterations 0-6 accepted; Iteration 7 authorized

This investigation defines a read-only exploratory tool over the accepted
GRCv4/GRC9v4 constitutive-design records. It is a side tool for understanding
the investigation, tracing provenance, and exploring bounded structural
counterfactuals. It is not a runtime model, a specification, or a new evidence
source.

The tool has two front ends over one validated Python graph kernel:

```text
accepted decisions/*.json
  -> schema-specific source adapters
  -> validated claim/debt/gate/object/profile lineage graph
  -> forensic Python and notebook reports
  -> deterministic ripple-table compiler
  -> static Cytoscape.js navigation client
```

The admitted D0-D10.2 source bundle is an immutable, reproducible snapshot; the
constitutive investigation itself is not assumed final. Before loading or
serving a bundle, the tool will compare its admitted source inventory with the
repository and flag new unprocessed records, changed identities, missing
sources, or unreadable observations. New material cannot enter the graph until
a named adapter/readmission and complete processing/rebuild cycle succeeds.

The browser renders generated tables and never computes scientific
consequences. Counterfactual propagation may invalidate known claims, reactivate
recorded debts, or identify a gate that must be rerun. It may not fabricate the
result of that rerun.

The tool is intended to be portable. Its implementation contract uses minimum
supported tool versions and tested ranges; lockfiles provide reproducible
dependency resolution without making one machine's Python, Node, OS, or path
part of scientific identity.

Python packages use the repository-root, ignored `.venv`. Node, package-manager
state, frontend dependencies, browser binaries, caches, test output, and
generated bundles remain tool-local and ignored. Nothing is installed globally,
into the Python user site, or committed as installed state.

No tool command may run under global Python, Node, or npm. A compatible host
Python has one bootstrap-only role on a clean checkout: create `.venv` and
immediately re-execute bootstrap there. Managed Node and its bundled npm are
always invoked by explicit paths below `tool/.tooling/`.

A clean checkout will use one idempotent bootstrap command that creates or
validates the repository `.venv`, verifies downloaded Node runtime checksums,
installs compatible locked dependencies, runs a doctor check, and prints the
commands for normal use. It must work from a different repository path without
manual Node installation or manual environment-variable configuration.

From the repository root:

```bash
TOOL=implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool
python3 "$TOOL/scripts/bootstrap.py"
.venv/bin/python "$TOOL/scripts/run.py" verify-iteration6
.venv/bin/python "$TOOL/scripts/run.py" serve-iteration6
```

The first command is the only permitted host-Python entry point; it immediately
re-executes under `.venv`. The dispatcher rejects every later global-Python
invocation and resolves Node, npm, Playwright, and Chromium exclusively from
the tool-local managed installation.

Start with:

- [implementation plan](./GRCV4ExploratorySideToolImplementationPlan.md)
- [implementation checklist](./GRCV4ExploratorySideToolImplementationChecklist.md)
- [user scenarios and plan-coverage validation](./GRCV4ExploratorySideToolUserScenarios.md)
- [Iteration 0 source and layout contract](./records/ETC0SourceAndLayoutContract.md)
- [accepted Iteration 1 source-adapter admission](./records/ETC1SourceAdapterAdmission.md)
- [accepted Iteration 2 validated graph](./records/ETC2ValidatedGraphKernel.md)
- [accepted Iteration 3 forensic reconstruction](./records/ETC3ForensicReconstructionSurface.md)
- [Iteration 3 forensic scenario report](./records/ETC3ForensicScenarioReport.md)
- [accepted Iteration 4 bounded counterfactual kernel](./records/ETC4BoundedCounterfactualKernel.md)
- [Iteration 4 counterfactual scenario report](./records/ETC4CounterfactualScenarioReport.md)
- [accepted Iteration 5 ripple and scenario contract](./records/ETC5RippleAndScenarioContract.md)
- [Iteration 5 canonical scenario bundle](./records/ETC5ScenarioBundle.json)
- [Iteration 5 deterministic ripple index](./records/ETC5RippleShardIndex.json)
- [accepted Iteration 6 static navigation surface](./records/ETC6StaticNavigationSurface.md)
- [Iteration 6 canonical browser bundle](./records/ETC6StaticNavigationBundle.json)
- [Iteration 6 cross-surface parity record](./records/ETC6CrossSurfaceParity.json)
- [accepted constitutive-design investigation](../../README.md)
- [accepted D10 claim topology](../../decisions/D10NormativeClaimTopology.json)
- [accepted D10 debt transformations](../../decisions/D10DebtClaimTransformationLedger.json)
- [accepted D10.2 provenance audit](../../decisions/D10_2FullSubstrateProvenanceAndPromotionAudit.json)

Current authorization:

```text
plan_and_checklist = frozen
iteration_0 = accepted
ET_C0_record_digest = 2cd1b8c313ee86dba807d4f57e7db7eae3c8596fed457fabfa1bdc0ec4ab1028
source_records_may_be_read = true
source_records_may_be_modified = false
source_adapter_implementation = accepted
source_observation = current_bundle_exact
ET_C1_source_bundle_digest = 79e84f7839e1b65f3e55eeadb980e6d8d9b57d240aced93a8bf3a7e82851dffc
ET_C1_relationship_witness_digest = 1793217d1f0726e8735a1c8d18c1b8c70148d30559037e293a33fc799b47997f
graph_kernel_implementation = accepted
ET_C2_graph_digest = 2776d2aa1aca51f7759c94ed0e9677a04934429b070bb8ea47683cbcd8f218ae
ET_C2_invariants = 14_of_14_passed
ET_C2_independent_relationship_audit = 2670_of_2670_exact
forensic_API_implementation = accepted
ET_C3_scenario_report_digest = ddd91b4ec63894f955b9423caf71f4fc27df559ac74d54a822d4f32042055f14
ET_C3_candidate_record_digest = 250723350ac838abcdb83ec96a48b4eaa734dfb3c287c9e19183bbc2b4b4eef9
ET_C3_independent_audit = 10018_checks_101_rows_1205_edge_refs
ET_C3_focused_tests = 15_of_15_passed
ET_C3_notebook_recipes = 2_passed_output_envelope_closed
iteration_3 = accepted
ET_C4_scenario_report_digest = fbcb0471725157f42daae0954889082b03e164659df14cb6bdc5c5205f8ea15c
ET_C4_record_digest = 4eea388fd9ee610a19d17efe48ed3512b2afb81f0f6fefcae89d5494dad46f89
ET_C4_independent_audit = 1775_checks_169_edge_references
ET_C4_focused_tests = 38_of_38_passed
iteration_4 = accepted
ET_C5_scenario_bundle_digest = 52630207a8e2d2510c799d81de313a2515088ba5790d0f383fadd7eb827dfee3
ET_C5_aggregate_digest = e8f067860bb62c6263fd213ca10e605f5ea088557f3d6ca98a0bd2d6fc542c2b
ET_C5_shard_index_digest = 882d4e3e2e254083fcef8b249b640e60f4561cad4b0ca7acffa440cbd9a8ba4e
ET_C5_record_digest = 1da09db7cea385d8e7818e38c0c8f2c7a6b2c77ee8fa4518415cdd7d02ba33fa
ET_C5_population = 25_scenarios_24_rows_3_shards
ET_C5_independent_audit = 4133_checks_836_edge_references
ET_C5_focused_tests = 89_of_89_passed
iteration_5 = accepted
ET_C6_static_bundle_digest = 45a96e782a1ecdd5fb693e171052a020bfdbffa76d21ca07e0a307b9cc96684c
ET_C6_parity = 7_of_7_byte_identical
ET_C6_independent_audit = 44895_checks
ET_C6_focused_tests = 47_python_8_node
ET_C6_browser_pressure = desktop_mobile_passed
ET_C6_accepted_record_digest = 6353caaf1cb67b4228bfd9d74a4898a72a8ba886dcb84b55757d019b0d1c3629
iteration_6 = accepted
iteration_7 = authorized_not_implemented
src_pygrc_changes = forbidden
specification_changes = forbidden
new_scientific_claims = forbidden
browser_side_propagation = forbidden
```

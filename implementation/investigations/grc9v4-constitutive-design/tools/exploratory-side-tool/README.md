# GRCv4 Exploratory Side Tool

**Status:** Iterations 0-10 accepted; Iteration 11 UX candidate implemented

This investigation defines a read-only exploratory tool over the accepted
GRCv4/GRC9v4 constitutive-design records. It is a side tool for understanding
the investigation, tracing provenance, and exploring bounded structural
counterfactuals. It is not a runtime model, a specification, or a new evidence
source.

The historical tool has two front ends over one validated Python graph kernel;
the D11 successor cycle extends the same pattern without rewriting it:

```text
accepted decisions/*.json
  -> schema-specific source adapters
  -> validated claim/debt/gate/object/profile lineage graph
  -> forensic Python and notebook reports
  -> deterministic ripple-table compiler
  -> static Cytoscape.js navigation client
accepted ET-C10 D11 overlay
  -> successor forensic API
  -> ET-C11 D11 notebook and static browser workspace
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
.venv/bin/python "$TOOL/scripts/run.py" verify-iteration9
.venv/bin/python "$TOOL/scripts/run.py" notebook-iteration3
.venv/bin/python "$TOOL/scripts/run.py" notebook-iteration11-d11
.venv/bin/python "$TOOL/scripts/run.py" serve-iteration11-d11
```

`serve-iteration11-d11` serves the latest ET-C11 candidate with the historical
Explore/Lineage interfaces plus the new D11 workspace. `serve-iteration8`
remains the historical entry point and should not refresh the shared
distribution after ET-C11 has been built.

`tool/web/dist` is the static distribution for the latest built iteration. A
later browser build necessarily changes asset and Vite-manifest hashes, so an
older iteration's full-dist manifest is historical rather than a validator for
the current distribution. Current verification uses the latest build manifest
and reruns predecessor source/layer-focused regressions separately.

The first command is the only permitted host-Python entry point; it immediately
re-executes under `.venv`. The dispatcher rejects every later global-Python
invocation and resolves Node, npm, Playwright, and Chromium exclusively from
the tool-local managed installation.

Start with:

- [user guide](./docs/UserGuide.md)
- [agentic query guide](./docs/AgenticQueryGuide.md)
- [D11 API, notebook, and browser UX guide](./docs/D11UXGuide.md)
- [forensic recipes notebook](./tool/notebooks/forensic_recipes.ipynb)
- [D11 successor notebook](./tool/notebooks/d11_successor_recipes.ipynb)
- [implementation plan](./GRCV4ExploratorySideToolImplementationPlan.md)
- [implementation checklist](./GRCV4ExploratorySideToolImplementationChecklist.md)
- [user scenarios and plan-coverage validation](./GRCV4ExploratorySideToolUserScenarios.md)
- [D11 successor forensic scenarios](./GRCV4ExploratorySideToolD11SuccessorScenarios.md)
- [D11 API/notebook/browser UX scenarios](./GRCV4ExploratorySideToolD11UXScenarios.md)
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
- [accepted Iteration 7 claim-ceiling and alternative layer](./records/ETC7ClaimCeilingAlternativeNavigation.md)
- [Iteration 7 verification receipt](./records/ETC7VerificationReceipt.json)
- [accepted Iteration 8 lineage and ripple layer](./records/ETC8LineageAndRippleNavigation.md)
- [Iteration 8 compiled lineage/playback layer](./records/ETC8LineagePlaybackLayer.json)
- [Iteration 8 verification receipt](./records/ETC8VerificationReceipt.json)
- [accepted Iteration 9 closeout](./records/ETC9CloseoutReport.md)
- [Iteration 9 scenario coverage](./records/ETC9ScenarioCoverageAndUsability.json)
- [Iteration 9 environment conformance](./records/ETC9EnvironmentConformance.json)
- [Iteration 9 verification receipt](./records/ETC9VerificationReceipt.json)
- [accepted Iteration 10 D11 forensic admission](./records/ETC10D11ForensicAdmission.md)
- [Iteration 11 D11 UX candidate](./records/ETC11D11UXCandidate.md)
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
ET_C7_locked_surfaces = 90
ET_C7_alternatives = 144
ET_C7_candidate_careers = 3
ET_C7_layer_digest = 6d694de0e7ffbdea653543668472534ac6fde4be0ea1e1aedc6e1cf561cecc9f
ET_C7_independent_audit = 2173_checks
ET_C7_focused_tests = 477_python_12_node
ET_C7_browser_pressure = 4_tests_desktop_mobile_6_screenshots
ET_C7_accepted_record_digest = 504e8474166c9f71018304f81251d1a65c9777b9e8eb70e71a7b5edb360ba688
ET_C7_verification_receipt_digest = 1eefce7345bc315022f15061ebeffd8f5c51d8d5fb8df47b1f6c53116dbe14be
iteration_7 = accepted
ET_C8_accepted_gate_records = 33
ET_C8_spine_positions = 26
ET_C8_companion_branches = 7
ET_C8_claim_reconstructions = 68
ET_C8_precomputed_playbacks = 24
ET_C8_layer_digest = 5c5c29a9c636c5a91e2cf37921c323f97ef42ddb9d21442b4e44e17426b50faa
ET_C8_independent_audit = 1049_structural_plus_33192_per_edge_checks
ET_C8_focused_tests = 185_python_17_node
ET_C8_browser_pressure = 8_tests_desktop_mobile_10_screenshots
ET_C8_web_manifest_digest = dc1456e975c0851d1ecc817422f2cedb9c25e0b182c3cbca2147b4d634f7bee7
ET_C8_accepted_record_digest = a11d390de18469210c82e85fe7c8d2e41eddb20ae811541923db0325fb3a2c20
ET_C8_verification_receipt_digest = 7fcd3f3df3a8f2a0c14c1ffcb2aa05d98db85f310c3b73772326556e8430e608
iteration_8 = accepted
iteration_9 = accepted
ET_C9_scenario_coverage = 35_of_35_reconciled
ET_C9_forensic_API_coverage = 9_of_9
ET_C9_web_view_coverage = 8_of_8
ET_C9_user_guide = 13_complete_workflows_including_notebook_with_6_verified_screenshots
ET_C9_agentic_guide = 12_complete_workflows_including_notebook_with_9_query_executable_walkthrough
ET_C9_scenario_documentation = canonical_35_scenario_contract_linked_without_duplication
ET_C9_coverage_digest = a4608d728c9b9e356421adb2d6b98390794c0916e90c299ad88467720f3c7404
ET_C9_accepted_record_digest = 7e9fb5a8dada805b1cd1b86e877bf1d23cfc16c4a6c0a1ef97d8f518e6ee0288
ET_C9_verification_receipt_digest = c0ae8b45a0d501d988845ce9565a3c89752a815a9a77676551c503870953266a
iteration_10_D11_forensic_overlay = accepted
ET_C10_D11_graph_digest = 44d8c7d33950af5e5f7c61caa4fe6fbd14fc9aedf14218d0a11de7c705542e09
iteration_11_D11_UX = candidate_implemented_verified_human_acceptance_pending
ET_C11_D11_UX_catalog = 69
ET_C11_API_notebook_browser_identity = 6_of_6_byte_exact
ET_C11_browser_pressure = 16_of_16_desktop_mobile_passed
src_pygrc_changes = forbidden
specification_changes = forbidden
new_scientific_claims = forbidden
browser_side_propagation = forbidden
```

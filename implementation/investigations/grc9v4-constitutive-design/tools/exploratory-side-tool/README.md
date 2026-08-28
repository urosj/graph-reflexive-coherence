# GRCv4 Exploratory Side Tool

**Status:** Iteration 0 accepted; Iteration 1 authorized

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

The accepted investigation remains immutable. The browser renders generated
tables and never computes scientific consequences. Counterfactual propagation
may invalidate known claims, reactivate recorded debts, or identify a gate that
must be rerun. It may not fabricate the result of that rerun.

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

Start with:

- [implementation plan](./GRCV4ExploratorySideToolImplementationPlan.md)
- [implementation checklist](./GRCV4ExploratorySideToolImplementationChecklist.md)
- [user scenarios and plan-coverage validation](./GRCV4ExploratorySideToolUserScenarios.md)
- [Iteration 0 source and layout contract](./records/ETC0SourceAndLayoutContract.md)
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
source_adapter_implementation = authorized_under_iteration_1
graph_kernel_implementation = blocked_until_ET_C1_acceptance
src_pygrc_changes = forbidden
specification_changes = forbidden
new_scientific_claims = forbidden
browser_side_propagation = forbidden
```

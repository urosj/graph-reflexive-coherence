# GRCv4 Exploratory Side Tool

**Status:** Initialized; plan and checklist frozen for implementation review

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

Start with:

- [implementation plan](./GRCV4ExploratorySideToolImplementationPlan.md)
- [implementation checklist](./GRCV4ExploratorySideToolImplementationChecklist.md)
- [accepted constitutive-design investigation](../../README.md)
- [accepted D10 claim topology](../../decisions/D10NormativeClaimTopology.json)
- [accepted D10 debt transformations](../../decisions/D10DebtClaimTransformationLedger.json)
- [accepted D10.2 provenance audit](../../decisions/D10_2FullSubstrateProvenanceAndPromotionAudit.json)

Current authorization:

```text
plan_and_checklist = initialized
source_records_may_be_read = true
source_records_may_be_modified = false
tool_implementation_may_begin_after_plan_review = true
src_pygrc_changes = forbidden
specification_changes = forbidden
new_scientific_claims = forbidden
browser_side_propagation = forbidden
```

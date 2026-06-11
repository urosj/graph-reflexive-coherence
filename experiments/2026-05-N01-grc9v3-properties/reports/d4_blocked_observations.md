# D4 Blocked Observations

| Observation | Status | Artifact Source | Reconstruction Attempt | Notes |
| --- | --- | --- | --- | --- |
| direct column-H saturation gate | blocked | Lane A Experiment C rows | Checked derived column diagnostic fields and Lane A gate formula. | Current gate is active degree plus basin-interior and signed-Hessian degeneracy; canonical column-H is a deferred Lane B. |
| active-degree-8 near-saturation policy | blocked | near_saturation_policy field | Read Experiment C near_saturation_policy for all rows. | Experiment C records not_implemented_in_lane_a; D4 reports canonical and optional near-saturation separately. |
| column diagnostic as gate evidence | blocked | derived_column_diagnostic_v1 | Extracted column pressure and cancellation diagnostics. | Column diagnostics are analysis_diagnostic_only under Lane A and are not used as the gate predicate. |
| identity-level consequence of D4 expansion | inconclusive | Experiment C event rows | Checked completed identity event count and child-basin fields. | D4 classifies event-level mechanical expansion only; identity emergence belongs to D8. |

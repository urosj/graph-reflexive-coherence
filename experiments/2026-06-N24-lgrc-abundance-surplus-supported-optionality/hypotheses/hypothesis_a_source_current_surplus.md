# Hypothesis A - Source-Current Surplus Above Maintenance Floors

N24 can produce source-backed evidence that surplus support/coherence exists
above declared maintenance floors in LGRC-visible geometry.

Support requires:

```text
N20 surplus_supported_optionality contract consumed without redefinition
N23 closeout consumed as bounded LC6 selection-geometry context only
N23 closeout artifact exists and validates ready_for_n24 before context is
consumed
N23 lower-rung or missing closeout downgrades N24 to contract-only or AB0
maintenance floors declared before use
optionality window declared before use
source_current_inputs recorded
row_specific_thresholds_declared_before_use = true
support_surplus_margin = observed_support - support_floor_value
coherence_surplus_margin = observed_coherence - coherence_floor_value
support_surplus_margin_trace present
maintenance_floor_trace present
coherence floor preserved
boundary integrity under optionality preserved or not yet opened
flux/leakage bound preserved or not yet opened
surplus margin attributable to source-current geometry or declared producer
surface, not hidden budget relief
surplus budget owner recorded with rung ceiling
artifact_manifest present for positive rows
all_artifact_sha256_match_file_contents = true
derived_report_only = false for positive rows
unsafe claim flags false
```

Failure conditions:

```text
surplus is declared only in prose
surplus is computed after outcome inspection
maintenance floors are missing or post-hoc
support/coherence floor is crossed and relabeled as abundance
support/coherence floors are lowered or renormalized after outcome inspection
maintenance basin identity shifts while surplus is claimed
surplus is produced by hidden budget relief
reward/proxy label is treated as support surplus
N23 branch/collapse context is treated as N24 surplus evidence
semantic abundance, choice, agency, goal, or native support labels are used as
evidence
```

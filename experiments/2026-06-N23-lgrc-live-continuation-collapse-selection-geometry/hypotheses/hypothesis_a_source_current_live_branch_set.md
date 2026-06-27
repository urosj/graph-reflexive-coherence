# Hypothesis A - Source-Current Live Branch Set

N23 can produce source-backed evidence that at least two live continuation
branches exist before collapse in LGRC-visible geometry.

Support requires:

```text
N20 live_continuation_collapse contract consumed without redefinition
N22 closeout consumed as producer-mediated susceptibility context only
branch window declared before use
source_current_inputs recorded
row_specific_thresholds_declared_before_use = true
live_branch_set_trace present
live branches recorded in the same source-current run
live branches recorded in the same declared branch window
live branches recorded before collapse-window start
branch_support_coherence_traces present
branch_boundary_flux_traces present
at least two branch records are source-current and boundary-distinguishable
branch alternatives are not producer labels
replay forks may audit counterfactuals but cannot create the original live
branch set
same-basin continuation contract preserved
support/coherence/boundary/flux gates preserved
derived_report_only = false
unsafe claim flags false
```

Failure conditions:

```text
only one branch exists and is relabeled as a choice
alternatives are report-built or post-hoc
alternatives are assembled across independent runs
alternatives are created by replay forks and then counted as original live
branches
alternatives are producer preference labels without source-current traces
branches are not boundary-distinguishable
branch support/coherence traces are missing
same-basin continuation fails
support/coherence/boundary/flux gates fail
semantic choice, intention, agency, or native support labels are used as
evidence
```

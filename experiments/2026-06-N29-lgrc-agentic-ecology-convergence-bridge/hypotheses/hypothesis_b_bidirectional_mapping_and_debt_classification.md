# Hypothesis B - Coverage / Debt Matrix And Bridge Motif Correctness

N29 can connect ecology demands to `N05-N28` capability supply through a
coverage matrix and bridge motif library without hiding debt or overclaiming
ecology.

Expected support:

```text
each ecology demand receives coverage status:
  source_backed
  prototype_candidate
  producer_mediated
  medium_debt
  naturalization_debt
  native_ready_surface
  control_only
  missing_runtime_surface
  not_applicable
  blocked_relabel

bridge motifs connect demand rows to capability rows with explicit order,
controls, debt, and claim ceiling
```

Every row must record:

```text
source_experiment_or_spec
ecology_demand
candidate_capability_sources
bridge_motif
agency_diagnostic_role
producer_residue
medium_debt
native_readiness_status
claim_ceiling
blocked_relabels
```

Failure conditions:

```text
unsupported ecology component marked covered
bridge motif lacks source-backed capability supply
producer residue treated as native ecology
medium debt treated as shared-medium coordination
N12/N19 native-readiness blockers bypassed
AP4/AP5 NAT4 gaps hidden by ecology language
```

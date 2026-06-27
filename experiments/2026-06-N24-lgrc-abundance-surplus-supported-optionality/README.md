# N24 - LGRC Abundance As Surplus-Supported Optionality

N24 is a becoming-primitive experiment after N23. It consumes the N20
`surplus_supported_optionality` contract and the N23 closeout only as bounded
live-continuation collapse / selection-geometry context, then tests whether
surplus support and coherence above maintenance floors can open optional
continuation space without collapsing basin integrity.

Current state:

```text
status = initialized
source_contract_row = n20_i4_row_05_surplus_supported_optionality
source_consumable_contract_row = n20_i5_row_05_surplus_supported_optionality
n20_contract_status = complete
n23_context = expected LC6/N23-C6 bounded live-continuation collapse evidence,
  subject to Iteration 1 source-inventory validation
target_primitive = surplus_supported_optionality
target_reading = abundance
local_ladder = AB0...AB6
closeout_ladder = N24-C0...N24-C6
next_experiment = N25_spark_sub_basin_new_basin_formation
```

Core question:

```text
Can surplus support above the maintenance floor open optional continuations
without collapsing basin integrity?
```

N24 is not a reward maximization, goal, semantic choice, agency, native
support, sentience, Phase 8, or ant-ecology experiment. `Abundance` may be used
only as a bounded LGRC reading for surplus-supported optionality:

```text
support/coherence surplus that permits optionality, exploration, repair,
specialization, or splitting without dropping below maintenance floors
```

## Source Boundary

Primary source artifacts:

```text
experiments/2026-06-N20-lgrc-becoming-primitive-producer-translation-contract/outputs/n20_native_function_proxy_contract.json
experiments/2026-06-N20-lgrc-becoming-primitive-producer-translation-contract/outputs/n20_same_basin_continuation_contract.json
experiments/2026-06-N23-lgrc-live-continuation-collapse-selection-geometry/outputs/n23_closeout_and_n24_handoff.json
experiments/N20-N29-LGRC-BecomingAgencyEcologyHandoff.md
experiments/N20-N29-LGRC-BecomingAgencyEcologyRoadmap.md
```

N24 must consume:

```text
N20 source contract row = n20_i4_row_05_surplus_supported_optionality
N20 consumable same-basin row = n20_i5_row_05_surplus_supported_optionality
N23 closeout context = LC6/N23-C6 bounded live-continuation collapse evidence,
  AP4 bridge candidate context, ready_for_n24
```

N23 evidence is prerequisite context only. It can provide bounded branch-set,
counterfactual-retention, collapse, and AP4 selection-geometry context. It
cannot satisfy N24 surplus/abundance evidence and must not be relabeled as
semantic choice, agency, free will, native support, sentience, Phase 8, or ant
ecology.

N23 consumption is conditional, not assumed. Iteration 1 must fail closed if
the closeout is absent or lower than the expected handoff:

```text
n23_closeout_required = true
n23_closeout_artifact_required =
  experiments/2026-06-N23-lgrc-live-continuation-collapse-selection-geometry/outputs/n23_closeout_and_n24_handoff.json

if n23_closeout_missing:
  n24_source_inventory_status = blocked_by_missing_n23_closeout
  n23_context_consumption = not_available
  max_ab_rung = AB0

if n23_final_lc_ladder_rung < LC6 or n23_closeout_ladder_rung < N23-C6:
  n23_context_consumption = bounded_lower_rung_context_only
  n23_ap4_bridge_status = not_consumable_as_bridge_candidate
  n24_claim_ceiling = contract_only_or_downgraded_context
```

## Required Source-Current Fields

Positive N24 rows must provide source-current evidence for:

```text
source_current_inputs
row_specific_thresholds_declared_before_use
surplus_supported_optionality.support_surplus_margin_trace
surplus_supported_optionality.optional_continuation_set_trace
surplus_supported_optionality.maintenance_floor_trace
surplus_supported_optionality.boundary_integrity_under_optionality_trace
```

Evidence must come from LGRC runtime or replay artifacts. Optional branch
labels, reward/proxy labels, producer enumeration, hidden budget relief,
report-built rows, or semantic abundance claims are not evidence.

## Primitive Reading

Surplus-supported optionality means:

```text
the maintenance basin remains above declared support/coherence/boundary/flux
floors while surplus opens more than one source-current optional continuation
path, and those optional continuations remain auditable without draining the
maintenance basin below floor.
```

For N24, original optional continuation space counts only when it is recorded:

```text
in the same source-current run
inside a declared optionality window
with maintenance support and coherence floors already declared
with branch-specific support/coherence and boundary/flux traces
with surplus margin attributable to source-current support/coherence, not
hidden producer budget relief
```

Declared replay families may validate replay stability, repeatability, and
stress behavior. They may not create the original optional continuation set for
`AB3`.

Optional branches assembled from labels, reward/proxy scores, independent runs,
or post-hoc report construction do not count as N24 optionality evidence.

N24 distinguishes available optionality from the stronger jointly admissible
case:

```text
optional_continuation_availability_count =
  count of source-current optional alternatives available in the same window

jointly_admissible_optional_continuation_count =
  count of alternatives jointly admissible under the same maintenance surplus
  and budget envelope

AB3 requires optional_continuation_availability_count >= 2
AB5 requires jointly_admissible_optional_continuation_count >= 2 under stress
```

Positive rows must predeclare surplus calculations:

```text
support_surplus_margin =
  observed_support - support_floor_value

coherence_surplus_margin =
  observed_coherence - coherence_floor_value

residual_support_margin_under_optionality =
  min_support_during_optionality_window - support_floor_value

residual_coherence_margin_under_optionality =
  min_coherence_during_optionality_window - coherence_floor_value

optional_flux_drain_margin =
  flux_or_leakage_bound - observed_optional_flux_drain
```

`AB2` requires positive surplus margin. `AB3` requires residual support and
coherence margins to remain positive while optional branches are open.
Changing the maintenance basin identity, lowering floors, or renormalizing
units after outcome inspection cannot create surplus evidence.

## Local N24 Ladder

N24 uses a local abundance / surplus optionality ladder:

```text
AB0 = no source-current surplus optionality evidence
AB1 = run artifact with possible surplus or optionality context
AB2 = source-current surplus above declared maintenance floor
AB3 = surplus opens source-current optional continuation set while floors hold
AB4 = replay/control-backed surplus-supported optionality candidate
AB5 = stress/threshold-backed abundance candidate with hidden-budget, proxy,
      and floor-crossing controls clean
AB6 = N25-ready bounded surplus-supported optionality evidence
```

Rows below `AB3` cannot support surplus-supported optionality. Rows below `AB4`
cannot support replay/control-backed abundance evidence. `AB6` is a handoff
rung for N25, not agency, semantic choice, native support, or Phase 8.

## N24 Closeout Ladder

N24 also uses a tranche-level closeout ladder:

```text
N24-C0 = contract-only closeout
N24-C1 = active-null/control discipline established
N24-C2 = surplus partial
N24-C3 = source-current optional continuation candidate
N24-C4 = replay/control-backed surplus optionality candidate
N24-C5 = stress/threshold-backed abundance candidate
N24-C6 = N25-ready bounded surplus-supported optionality evidence
```

The closeout ladder classifies the whole N24 tranche. It must not convert an
AB row into reward maximization, semantic choice, intention, agency, native
support, sentience, Phase 8, or ant-ecology evidence.

## AP Gap Boundary

N24 must preserve the AP gap split inherited from N19/N20/N23:

```text
AP4:
  N23 provides AP4 bridge candidate context for bounded selection geometry.
  N24 may consume that context but must not claim final global AP4
  reclassification.

  ap4_context_status =
    n23_bridge_candidate_consumed |
    lower_n23_context_consumed |
    not_applicable |
    missing_blocks_row

  final_global_ap4_reclassification_supported = false

AP5:
  conditional AP5 dependency must be carried row-locally when proxy derivation,
  reward/proxy labels, target formation, or proxy-valued optionality
  participates.
```

N24 may contribute evidence about surplus-supported optionality, not semantic
goal ownership or endogenous target formation.

## Evidence Standard

Good N24 evidence requires:

```text
actual LGRC/source-current run artifacts
predeclared maintenance floors and optionality windows
source_current_inputs recorded
row_specific_thresholds_declared_before_use = true
artifact_manifest with path, sha256, and artifact_role
all_artifact_sha256_match_file_contents = true
support surplus margin trace
maintenance floor trace
optional continuation set trace
optional branch records with source-current trace origin
optional_continuation_availability_count >= 2 for AB3+
jointly_admissible_optional_continuation_count >= 2 for AB5+
branch-specific support/coherence traces
boundary integrity under optionality trace
flux/leakage trace proving optional branches do not drain maintenance support
same-basin continuation preserved
artifact replay
snapshot/load replay where applicable
duplicate replay where applicable
negative controls that fail closed
```

Insufficient evidence:

```text
optional branch labels without geometry
reward/proxy improvement while maintenance floor or boundary fails
hidden budget relief
surplus declared after outcome inspection
floor-crossing survival relabeled as abundance
maintenance basin shift relabeled as surplus
floor or unit renormalization relabeled as surplus
independent-run optional branches assembled as one same-window optional set
N23 selected-branch evidence relabeled as optionality
semantic choice or agency labels used as evidence
```

## Claim Ceiling

Allowed claim, if supported:

```text
bounded artifact-level surplus-supported optionality / abundance candidate
```

Blocked claims:

```text
semantic choice
semantic goal
semantic intention
agency
free will
selfhood
identity acceptance
native support
sentience
organism/life
Phase 8 implementation
ant ecology implementation
native ant agency
native colony agency
unrestricted autonomy
reward maximization
final global AP4 reclassification
general AP5 target/proxy formation
```

# N28 Generative Vs Extractive Persistence Implementation Plan

## Purpose

N28 tests the N20 `generative_extractive_persistence` primitive. The goal is
to produce source-current evidence that a focal basin can persist while its
environment or neighborhood gains basin-forming capacity, and to distinguish
that from competitive persistence, extractive persistence, merge/leakage, and
focal survival alone.

N28 must not treat N27 transfer success as N28 evidence. N27 provides bounded
CT6 transfer evidence and a claim-clean side-effect precursor, but it
explicitly keeps `n28_generative_persistence_supported = false`.

## Generative Vs Extractive Persistence

Persistence alone means:

```text
the focal basin remains stable
```

That is not enough for N28.

Generative persistence means:

```text
the focal basin remains stable
AND neighboring / sub-basin / environment capacity improves
AND that improvement is not merge, leakage, relabeling, or hidden producer support
```

So the focal basin persists in a way that leaves the surrounding geometry more
capable of forming or preserving basins.

Expected source-current evidence includes:

```text
neighbor_basin_distinguishability increases
neighbor_support_floor improves
neighbor_boundary_integrity improves
environment_basin_forming_capacity increases
focal_extraction_cost stays low
merge/leakage stays below ceiling
```

Extractive persistence means:

```text
the focal basin remains stable
BUT it does so by draining, flattening, merging, or suppressing surrounding capacity
```

So the focal basin survives, but the neighborhood becomes less basin-capable.

Expected source-current evidence includes:

```text
focal stability preserved
neighbor support drops
neighbor distinguishability decreases
neighbor boundary integrity weakens
extractive_flattening_score rises
merge/leakage rises
focal_extraction_cost rises
```

The classification boundary is:

```text
focal survives + neighborhood capacity improves = generative
focal survives + neighborhood capacity degrades = extractive
focal survives + neighborhood unchanged = persistence only, not generative
focal survives + neighbor labels change only = blocked relabel
```

The hardest N28 false positive is:

```text
focal basin survived, therefore it was generative
```

That is false. N28 must show source-current neighborhood capacity improvement,
not just focal survival.

## Three-Axis Regime Classifier

N28 should classify persistence regimes through three source-current axes:

```text
focal persistence axis:
  focal basin stable or not

neighborhood capacity axis:
  neighbor / sub-basin / environment capacity improves, degrades, or remains neutral

extraction / leakage axis:
  focal persistence preserves the medium or drains, flattens, leaks, or merges it
```

The shared classification rule is:

```text
stable focal + improved neighborhood + low extraction/leakage = generative
stable focal + degraded neighborhood + high extraction/flattening/leakage = extractive
stable focal + unchanged/mixed neighborhood = neutral or competitive
unstable focal = no persistence regime
```

This is the classifier N28 should try to freeze in Iteration 2 and then test
without retuning labels, thresholds, or boundaries to fit desired outcomes.

Generative and extractive persistence are not separate experiment targets.
They are complementary outcomes in one regime space. Splitting them into
separate experiments would risk proving isolated cases while missing the
dependency of conditions that distinguishes them.

The N28 target is therefore the shared regime boundary:

```text
under what conditions does focal persistence become generative,
under what conditions does it become extractive,
and what distinguishes both from neutral / competitive persistence?
```

N28 should first test whether one measurement and control discipline can cover
all regimes:

```text
same focal-stability logic
same neighborhood-capacity metrics
same extraction / flattening / leakage accounting
same replay and control rules
same AP / claim boundary
same threshold family
```

This is an evidence question, not an assumption. If one shared policy can
classify generative, extractive, and competitive/neutral rows, that is the
strongest result. If the regimes require split policy surfaces, N28 should
record that explicitly as a policy-divergence finding rather than retuning
silently.

Allowed shared-policy outcomes:

```text
shared_regime_policy_status = supported
  one source-current policy classifies all measured regimes

shared_regime_policy_status = partially_supported
  one policy covers some regimes, but a declared blocker prevents full coverage

shared_regime_policy_status = split_policy_required
  generative / extractive / competitive regimes require distinct declared
  policy surfaces

shared_regime_policy_status = blocked
  classification depends on post-hoc thresholds, hidden labels, or relabeling
```

The strongest N28 result is not:

```text
we found a generative case
we found an extractive case
```

It is:

```text
the same source-current policy can classify different persistence regimes
over comparable conditions without changing the rules to fit the label
```

But if that is not true, N28 should say so. A clean split-policy result is
still useful because it identifies which regime distinctions are not yet
captured by one shared LGRC-visible measurement policy.

## Paired-Regime Evidence Requirement

N28 must not close from a single positive-looking generative row. A strong N28
result needs source-current evidence for both sides of the distinction, plus
one alternative setup for each measured regime:

```text
primary generative candidate:
  focal basin remains stable
  neighborhood / sub-basin capacity improves
  extraction, flattening, merge, and leakage stay below ceiling

strengthening generative candidate:
  a distinct setup or neighborhood variant strengthens the I4 generative
  evidence by reaching the same classification under the same frozen policy
  family, without threshold retuning or relabeling the primary row

primary extractive contrast:
  focal basin remains stable
  neighborhood / sub-basin capacity degrades
  extraction, flattening, merge, or leakage explains the focal persistence

strengthening extractive contrast:
  a distinct degradation mechanism or neighborhood variant strengthens the I4-B
  extractive evidence by reaching the same extractive classification under the
  same frozen policy family, without threshold retuning or being promoted to
  generative persistence

primary competitive_or_neutral contrast:
  focal basin remains stable
  neighborhood does not materially improve
  row is classified below generative support

alternative competitive_or_neutral contrast:
  a distinct setup or mixed-capacity variant stays non-generative and does not
  collapse into label-only or extractive classification by accident
```

The extractive and competitive rows are not merely negative controls. They are
measured regimes. Their alternatives are also measured regime evidence, not
retuned duplicates. They should fail closed only if someone tries to promote
them to generative persistence. Otherwise they are useful classification
evidence:

```text
extractive row classified as extractive = valid contrast evidence
extractive row classified as generative = failed-open blocker
competitive/neutral row classified as non-generative = valid contrast evidence
competitive/neutral row classified as generative = failed-open blocker
```

N28-C5 / GE5 should require all of the following unless an explicit blocker is
recorded:

```text
primary and strengthening generative candidates survive replay and stress
primary and strengthening extractive contrasts are source-current and classified distinctly
primary and alternative competitive_or_neutral contrasts are source-current and classified distinctly
regime boundary stays stable under replay, controls, and stress
transfer success alone does not classify as generative
```

## Generative Persistence Vs Transfer

N28 is not a transfer experiment.

`configuration / topology transfer` asks whether the same basin signature
survives a declared mapping:

```text
pre-transfer basin signature
declared mapping before use
post-transfer basin signature
boundary mapping trace
support/coherence preservation
flux discipline
```

`generative / extractive persistence` asks what happens to the surrounding
basin-forming capacity while the focal basin persists:

```text
focal basin stability
neighbor or sub-basin distinguishability
neighbor support / coherence / boundary integrity
environment basin-forming capacity
focal extraction cost
extractive flattening
merge/leakage pressure
capacity attribution trace
```

The core N28 false positive is focal survival being relabeled as generativity.
N28 must require source-current neighborhood capacity traces and fail-closed
controls for label-only neighbor changes, merge/leakage masquerading as
support, hidden producer attribution, and extractive flattening.

## Source Rules

N28 may consume:

```text
N20 I3 generative/extractive persistence producer-residue and naturalization-debt ledger
N20 I4 native-function / proxy descriptor
N20 I5 same-basin continuation contract
N27 bounded CT6 configuration/topology transfer closeout
N27 side-effect precursor evaluation and claim classification
N27 focal-stability-with-neighbor-capacity metrics context
```

N28 must not consume:

```text
N27 transfer success as N28 generative persistence
N27 side-effect precursor as final N28 evidence
focal survival alone as generativity
neighbor label/count change as basin-forming capacity
merge/leakage as neighbor support
semantic cooperation as evidence
agency as evidence
native support as evidence
ant ecology behavior as evidence
Phase 8 completion as evidence
```

For I2 onward, source precedence is strict:

```text
N20 I5 same-basin continuation contract = normative
N20 I4 native-function / proxy descriptor = descriptor context
N20 I3 producer-residue ledger = residue / debt context
N27 closeout = prerequisite / precursor context
N27 side-effect rows = context and comparison baseline, not N28 support
roadmap/handoff = context only
```

## Required Evidence Fields

Every positive candidate row must record:

```text
row_id
iteration
row_decision
ge_ladder_rung
n28_closeout_ceiling
regime_label = generative | extractive | competitive | neutral | blocked
regime_evidence_role = positive_candidate | measured_contrast | active_null | control
shared_regime_policy_id
shared_regime_policy_status
policy_divergence_record
source_current_inputs
source_inventory_output_digest
source_ledger_row_digest
descriptor_contract_row_digest
consumable_contract_row_digest
source_output_digest
n20_producer_residue_row_digest
n20_native_function_proxy_row_digest
n20_same_basin_continuation_row_digest
n27_closeout_output_digest
n27_side_effect_precursor_output_digest
run_artifact_id
runtime_config_digest
artifact_manifest
all_artifact_sha256_match_file_contents
derived_report_only
row_specific_thresholds_declared_before_use
focal_basin_id
focal_basin_signature_trace
focal_basin_stability_trace
focal_support_coherence_floor_trace
neighbor_or_sub_basin_scope
neighbor_basin_distinguishability_trace
neighbor_support_floor_trace
neighbor_boundary_integrity_trace
environment_basin_forming_capacity_trace
neighborhood_capacity_delta_trace
focal_extraction_cost_trace
extractive_flattening_trace
merge_leakage_trace
capacity_attribution_trace
medium_debt_record
producer_residue_record
generative_classification_policy_digest
generative_classification_declared_before_use
generative_classification_result
regime_boundary_trace
policy_retuned_for_label
label_specific_thresholds_used
post_hoc_boundary_shift_used
generative_extractive_core
generative_extractive_core_digest
focal_survival_only_rejected
neighbor_label_only_rejected
merge_leakage_as_support_rejected
extractive_flattening_masked_rejected
transfer_success_as_n28_success_rejected
semantic_cooperation_relabel_rejected
replay_result
control_results
ap4_dependency_status
ap4_condition_reason
ap5_dependency_status
ap5_condition_reason
claim_ceiling
unsafe_claim_flags
```

## Classification Core

Every positive row must include a reusable classification-core object:

```text
generative_extractive_core:
  focal_basin_id
  focal_signature_digest
  focal_stability_digest
  neighbor_scope_digest
  neighbor_distinguishability_digest
  neighbor_support_digest
  neighbor_boundary_digest
  environment_capacity_digest
  neighborhood_capacity_delta_digest
  extraction_cost_digest
  extractive_flattening_digest
  merge_leakage_digest
  capacity_attribution_digest
  classification_policy_digest
  classification_result
  regime_evidence_role
```

Positive rows must also record `generative_extractive_core_digest`; replay,
control, and stress rows should reference the canonical core by digest rather
than reconstructing it in prose.

The core must fail closed if the row only shows focal survival, neighbor
labels, transfer success, visual similarity, merge/leakage, or producer
attribution.

## Local Ladder

```text
GE0 = no source-current generative/extractive persistence evidence
GE1 = focal persistence trace present, environment-side effect not measured
GE2 = focal persistence plus source-current neighborhood capacity metrics observed
GE3 = provisional source-current regime classification candidate
GE4 = replay/control-backed regime-separation candidate
GE5 = stress/variant-backed paired-regime separation candidate
GE6 = N29-ready bounded generative/extractive persistence evidence with claim-clean handoff
```

Closeout ladder:

```text
N28-C0 = initialized contract only
N28-C1 = source inventory and generative/extractive contract admission passed
N28-C2 = schema, controls, and classification policy frozen
N28-C3 = active nulls fail closed
N28-C4 = source-current generative/extractive candidate supported
N28-C5 = replay/control/stress-backed generative/extractive candidate supported
N28-C6 = N29-ready bounded generative/extractive closeout
```

## Required Control Families

N28 must instantiate these controls before positive support can close:

```text
source_digest_mismatch_control
derived_report_only_positive_row_control
artifact_manifest_failure_control
threshold_declared_after_outcome_control
missing_focal_stability_digest_control
missing_neighbor_capacity_digest_control
missing_extraction_cost_digest_control
missing_merge_leakage_digest_control
missing_capacity_attribution_digest_control
malformed_generative_extractive_core_digest_control
policy_retuning_to_fit_label_control
label_specific_threshold_control
post_hoc_regime_boundary_shift_control
focal_survival_only_as_generative_control
neighbor_label_only_as_capacity_control
neighbor_count_only_as_capacity_control
merge_leakage_as_support_control
extractive_flattening_masked_control
competitive_persistence_as_generative_control
transfer_success_as_n28_success_control
hidden_capacity_attribution_policy_control
producer_generativity_label_control
medium_segmentation_policy_hidden_control
environment_capacity_budget_mismatch_control
neighbor_support_floor_missing_control
neighbor_boundary_integrity_missing_control
replay_failure_control
stress_variant_failure_control
semantic_cooperation_relabel_control
semantic_choice_goal_relabel_control
native_support_relabel_control
ant_ecology_relabel_control
phase8_completion_relabel_control
native_ap5_relabel_control
ap5_nat4_gap_resolution_relabel_control
```

## AP4 / AP5 Boundary

N28 inherits the N19/N26 AP gap discipline:

```text
AP4/N14 NAT4 gap resolved = false
AP5/N15 NAT4 gap resolved = false
native_AP5_supported = false
AP5_NAT4_gap_resolution_supported = false
```

Rows must record row-local AP dependency status:

```text
ap4_dependency_status =
  required_recorded |
  not_applicable |
  missing_blocks_row

ap5_dependency_status =
  conditional_required_recorded |
  not_applicable |
  missing_blocks_row
```

Route/selection-conditioned rows require AP4 reason. Proxy/target-conditioned
rows require AP5 reason. Prose-only AP handling blocks the row.

## Iteration Plan

### Iteration 1. Source Inventory And Contract Admission

Inventory N20, N27, roadmap, and handoff sources. Freeze source roles,
digests, consumption boundaries, and non-claims. Treat N20 I5 as the
normative consumable contract, N20 I4 as descriptor context, and N20 I3 as the
producer-residue/debt ledger. No positive evidence opens.

### Iteration 2. Schema And Control Freeze

Freeze `GE0...GE6`, `N28-C0...N28-C6`, required fields, classification core,
threshold formulas, artifact roles, control families, medium-debt records,
producer-residue records, AP4/AP5 statuses, and claim boundary.

### Iteration 3. Active Nulls And Failure Baselines

Instantiate all controls as active nulls. Every false-positive path must fail
closed before positive rows are admitted.

### Iteration 4. Primary Generative Candidate Probe

Generate the first source-current generative candidate where focal basin
stability is preserved while neighbor capacity metrics improve and
extraction/flattening/merge/leakage remain below ceiling. Keep the row
provisional below replay/control closeout.

### Iteration 4-A. Generative Strengthening Candidate Probe

Generate a distinct source-current generative candidate whose job is to
strengthen I4, not merely provide variety. The row should test whether the I4
generative predicate repeats under a different neighborhood, schedule, fixture,
or capacity-formation setup while preserving the same frozen policy family.

I4-A should record whether its margins are comparable to or stronger than I4 on
the load-bearing axes: focal stability, neighbor distinguishability, neighbor
support, neighbor boundary integrity, environment basin-forming capacity,
extraction cost, flattening, and merge/leakage. It must not replace I4, import
I4 outcomes, widen thresholds, or relabel the primary row. If the same policy
family cannot classify the strengthening row, record a policy-divergence blocker
instead of retuning.

### Iteration 4-A2. Generative Mechanism-Diversity Probe

Generate a source-current generative candidate through a different geometric
mechanism, not by optimizing the I4 or I4-A trace. The row should test whether
the generative predicate holds when neighboring capacity is produced by split
shell capacity growth, delayed boundary thickening, or another declared
mechanism that differs from the single-shell/local-shell capacity increase used
by I4 and I4-A.

I4-A2 should pass only if the same frozen policy family is preserved, the
mechanism class is source-current and differs from I4/I4-A, focal persistence
and neighbor capacity gain remain trace-backed, extraction/flattening/leakage
stay below ceiling, and no thresholds are retuned. This strengthens the
generative side by mechanism diversity, not by replacing I4/I4-A or requiring
every margin to be larger than the previous best row.

### Iteration 4-B. Primary Extractive Persistence Contrast Probe

Generate a source-current extractive contrast where focal basin stability is
preserved while neighborhood capacity degrades or flattening/extraction rises.
The row is valid contrast evidence only if it is classified as extractive and
not promoted to generative persistence.

### Iteration 4-C. Extractive Strengthening Contrast Probe

Generate a distinct source-current extractive contrast whose job is to
strengthen I4-B, not merely provide variety. The row should test whether the
I4-B extractive predicate repeats under a different degradation mechanism,
neighborhood, fixture, schedule, or capacity-attribution route while preserving
the same frozen policy family.

I4-C should record whether its extractive margins are comparable to or stronger
than I4-B on the load-bearing axes: focal stability preservation, neighbor
distinguishability loss, neighbor support loss, neighbor boundary loss,
environment capacity loss, extraction cost, flattening, and merge/leakage. It
must not replace I4-B, import I4-B outcomes, widen thresholds, or relabel the
primary extractive contrast. If the same policy family cannot classify the
strengthening contrast, record a policy-divergence blocker instead of retuning.

### Iteration 4-C2. Extractive Mechanism-Diversity Probe

Generate a source-current extractive contrast through a different degradation
mechanism, not by optimizing I4-B or I4-C margins. The row should test whether
the extractive predicate holds when neighborhood degradation is produced by
merge/leakage-dominant boundary flattening or another declared mechanism that
differs from the local shell drain and cross-shell directional drain already
used by I4-B and I4-C.

I4-C2 should pass only if the same frozen policy family is preserved, the
mechanism class is source-current and differs from I4-B/I4-C, focal persistence
and neighbor capacity loss remain trace-backed, extraction/flattening/leakage
expose the degrading mechanism, and no thresholds are retuned. This strengthens
the extractive side by mechanism diversity, not by replacing I4-B/I4-C or
requiring every extractive margin to be larger than the previous best row.

### Iteration 4-D. Primary Competitive / Neutral Persistence Contrast Probe

Generate a source-current competitive or neutral contrast where the focal basin
persists but neighborhood capacity does not materially improve. The row should
be classified below generative support while remaining useful for regime
separation.

### Iteration 4-E. Competitive / Neutral Mechanism-Diversity Probe

Generate a second competitive or neutral contrast through a distinct mechanism,
not merely a tuned copy of I4-D. The target is a source-current neutral or
competitive processing regime, such as balanced multi-lobe circulation, where
the focal basin persists and local capacity is redistributed without material
aggregate enrichment or depletion.

I4-E should pass only if it preserves the same frozen policy family, records
source-current mechanism fields that differ from I4-D, stays non-generative
without becoming label-only or extractive by hidden drain, and does not retune
thresholds to force a neutral label. This strengthens the competitive/neutral
side by mechanism diversity, not by replacing I4-D.

### Iteration 5. Replay And Capacity Attribution Matrix

Replay I4 through I4-E regime rows, including I4-A2 and I4-C2, and test whether
the generative candidates, extractive contrasts, and competitive/neutral
contrasts survive artifact-only, snapshot/load, duplicate, and
attribution-specific controls. Record whether one shared policy still
classifies the replayed rows or whether split policies are required.

### Iteration 5-A. Artifact-Only Reconstruction Replay Probe

Confirm that N28 classification cannot be reconstructed from reports, labels,
or N27 transfer success alone.

### Iteration 6. Stress / Regime-Separation Matrix

Stress focal stability, neighbor capacity, leakage, extraction, and boundary
integrity across the generative and contrast rows. First test the shared policy
family without retuning thresholds to win; if that fails, record a
policy-divergence result rather than silently moving the boundary.

### Iteration 6-A. Regime Boundary / Transition Matrix

Vary the declared stress or capacity envelope to show where rows remain
generative, become neutral/competitive, or become extractive. This tests the
classification boundary directly instead of treating extractive persistence as
only a late negative control.

This iteration is also where `shared_regime_policy_status` should be decided
provisionally:

```text
supported | partially_supported | split_policy_required | blocked
```

### Iteration 7. Controls, AP4/AP5 Dependency, And Claim Classification

Classify all candidate rows, active nulls, contrasts, AP dependencies, and
unsafe claim boundaries.

### Iteration 8. Closeout And N29 Handoff

Freeze final `GE` and `N28-C` rung if warranted, record all blockers, preserve
claim ceiling, and hand bounded primitive evidence to N29 without opening ant
ecology implementation.

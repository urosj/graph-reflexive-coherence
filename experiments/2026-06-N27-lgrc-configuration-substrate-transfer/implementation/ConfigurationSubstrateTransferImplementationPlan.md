# N27 Configuration / Substrate Transfer Implementation Plan

## Purpose

N27 tests the N20 `configuration_substrate_transfer` primitive. The goal is to
produce source-current evidence that a basin signature can persist across a
declared configuration, fixture, topology, or substrate mapping while preserving
support/coherence floors, boundary mapping, replay, and claim discipline.

N27 must not use transfer as a semantic identity claim. It must also not treat
N26 proxy divergence evidence as transfer evidence.

## Basin Movement Vs Transfer

N27 is not a basin-movement experiment.

`basin movement` is a within-frame continuity question:

```text
same substrate
same coordinate/frame rules
basin center or boundary shifts
continuity trace links old and new location
```

The question is whether the same basin moves through existing geometry.

`configuration / substrate transfer` is a cross-frame mapping question:

```text
pre-transfer basin signature
declared mapping before use
post-transfer basin signature
boundary mapping trace
support/coherence preservation
flux discipline
hidden support reconstruction rejected
same-label/different-basin rejected
```

The question is whether the same basin signature survives when the surrounding
fixture, topology, configuration, or substrate representation changes.

In compact LGRC terms:

```text
movement:
  node/region A -> nearby node/region B in the same graph

configuration transfer:
  basin signature in graph/config X -> mapped basin signature in graph/config Y

substrate transfer:
  basin signature in substrate representation X -> declared mapped signature in
  substrate representation Y
```

The core N27 false positive is a same label appearing after mapping. That is not
transfer by itself. N27 must require source-current boundary mapping,
support/coherence preservation, flux discipline, and fail-closed controls for
same-label/different-basin, fixture-equivalence label-only, hidden support
reconstruction, and proxy-score relabel.

## Source Rules

N27 may consume:

```text
N20 I5 configuration/substrate transfer contract
N20 I5 same-basin continuation rule for transfer
N26 PD6 proxy divergence / proxy collapse closeout
N26 scoped artifact AP5 bridge context
N26 proxy-pressure controls
N26 source-current proxy/basin contrast context
```

N27 must not consume:

```text
N26 as native AP5
N26 as AP5 NAT4 gap resolution
N25.2 as unscoped multi-basin substrate
proxy score as basin transfer
fixture-equivalence label as mapping evidence
hidden producer support as transfer
semantic identity as basin signature
```

For I2 onward, source precedence is strict:

```text
N20 I5 consumable transfer contract = normative
N20 I4 transfer descriptor = context / descriptor only
```

Deferred or incomplete I4 descriptor fields cannot weaken transfer gates. Any
positive row must consume the complete N20 I5 transfer contract for same-basin
continuation, support/scaffold boundaries, proxy-only blockers, and hidden
producer support blockers.

N25.2 remains available only through N26 scoped context:

```text
n25_2_direct_transfer_consumption_used = false
n25_2_consumed_only_through_n26_context = true
```

## Required Evidence Fields

Every positive candidate row must record:

```text
row_id
iteration
row_decision
ct_ladder_rung
n27_closeout_ceiling
source_current_inputs
source_inventory_output_digest
source_contract_row_digest
source_output_digest
descriptor_contract_row_digest
consumable_contract_row_digest
n26_closeout_output_digest
run_artifact_id
runtime_config_digest
artifact_manifest
all_artifact_sha256_match_file_contents
derived_report_only
row_specific_thresholds_declared_before_use
transfer_scope
transfer_core
transfer_core_digest
transfer_mapping_id
transfer_mapping_digest
mapping_declared_before_use
mapping_source_backed
pre_transfer_basin_signature_trace
post_transfer_basin_signature_trace
boundary_mapping_trace
support_preservation_trace
coherence_preservation_trace
flux_balance_trace
original_fixture_support_change_trace
reconstructed_support_ledger
hidden_support_reconstruction_absent
same_basin_signature_preserved_under_mapping
same_label_different_basin_rejected
proxy_score_relabel_rejected
configuration_label_only_rejected
support_reconstruction_as_transfer_rejected
signature_preservation_margin_formula
boundary_mapping_tolerance_formula
support_floor_margin_formula
coherence_floor_margin_formula
flux_balance_bound_formula
threshold_record_digest
replay_result
control_results
ap4_dependency_status
ap4_condition_reason
ap5_dependency_status
ap5_condition_reason
claim_ceiling
unsafe_claim_flags
```

## Transfer Core

Every positive row must include a reusable transfer-core object so the claim is
about source-current mapped basin continuity rather than scattered labels:

```text
transfer_core:
  transfer_scope
  transfer_mapping_id
  transfer_mapping_digest
  mapping_declared_before_use
  mapping_source_backed
  pre_signature_digest
  post_signature_digest
  boundary_mapping_digest
  support_preservation_digest
  coherence_preservation_digest
  flux_balance_digest
```

Positive rows must also record `transfer_core_digest`; replay, control, and
stress rows should reference the canonical transfer core by digest rather than
reconstructing it in prose.

The core must fail closed if the row only shows same label, visual similarity,
nearby movement, proxy-score preservation, or hidden support reconstruction.

## Threshold And Formula Records

For I4 onward, N27 must freeze row-specific measurement records before outcome
inspection:

```text
signature_preservation_margin_formula
boundary_mapping_tolerance_formula
support_floor_margin_formula
coherence_floor_margin_formula
flux_balance_bound_formula
threshold_record_digest
row_specific_thresholds_declared_before_use = true
```

This makes "same basin under mapping" measurable rather than interpretive.

## Rung-Specific Artifact Roles

Early transfer candidates must not be blocked by later-stage artifact
requirements, but each rung has a strict minimum artifact surface:

```text
CT1:
  transfer_mapping_trace
  pre_transfer_basin_signature_trace
  threshold_record

CT2:
  CT1 +
  post_transfer_basin_signature_trace
  boundary_mapping_trace
  support_preservation_trace
  coherence_preservation_trace
  flux_balance_trace

CT3:
  CT2 +
  replay_trace

CT4:
  CT3 +
  control_trace

CT5:
  CT4 +
  stress_variant_trace

CT6:
  CT5 +
  closeout
  N28_handoff_record
```

Positive rows must record `artifact_manifest` entries with roles matching the
claimed rung.

## Transfer Scope

Primary scope:

```text
configuration_or_topology_transfer_inside_LGRC
```

Allowed row scopes:

```text
configuration
fixture
topology
substrate
```

`substrate` rows require:

```text
declared source-backed substrate mapping
mapping source artifact digest
explicit boundary-side assignment mapping
explicit support/coherence interpretation mapping
```

If those are absent, a substrate row must be blocked or demoted to a
configuration-only row.

## Support Preservation Vs Reconstruction

N27 must separate preserved support from rebuilt support:

```text
support_preservation_trace
original_fixture_support_change_trace
reconstructed_support_ledger
hidden_support_reconstruction_absent
support_reconstruction_as_transfer_rejected
```

A post-transfer basin rebuilt by hidden producer support or post-hoc support
reconstruction is not transfer. It must be rejected or demoted even if support,
coherence, or proxy scores look preserved.

## AP4/AP5 Dependency Semantics

AP dependencies are row-local:

```text
ap4_dependency_status =
  required_recorded | missing_blocks_row | not_applicable

ap5_dependency_status =
  required_recorded | missing_blocks_row | not_applicable
```

`not_applicable` requires an explicit row-local reason. Route/selection
participation requires AP4 handling. Proxy/target formation participation
requires AP5 handling. N26 scoped AP5 bridge context cannot be promoted into
native AP5 or AP5 NAT4-gap resolution.

## Local Ladder

```text
CT0 = no source-current transfer evidence
CT1 = declared mapping and pre-transfer basin signature present
CT2 = source-current post-transfer signature and boundary mapping observed
CT3 = replay-backed same-basin transfer candidate
CT4 = control-backed configuration/topology transfer candidate
CT5 = stress/variant-backed transfer candidate across multiple declared mappings
CT6 = N28-ready bounded transfer evidence with claim-clean handoff
```

## Closeout Ladder

```text
N27-C0 = initialized contract only
N27-C1 = source inventory and transfer contract admission passed
N27-C2 = transfer schema and controls frozen
N27-C3 = active nulls fail closed
N27-C4 = source-current transfer candidate supported
N27-C5 = replay/control/stress-backed transfer candidate supported
N27-C6 = N28-ready bounded transfer closeout
```

## Iteration Plan

### Iteration 1 - Source Inventory And Transfer Contract Admission

Inventory N20/N26 sources and freeze what N27 may consume. No positive transfer
evidence opens in I1.

### Iteration 2 - Transfer Schema And Control Freeze

Freeze CT ladder, N27-C ladder, evidence fields, transfer scopes, replay
requirements, AP4/AP5 dependency statuses, transfer-core fields,
rung-specific artifact roles, support-preservation/reconstruction separation,
source digest pins, N20 I5 normative consumption, and fail-closed control
families.

### Iteration 3 - Active Nulls And Failure Baselines

Instantiate active nulls for false transfer paths:

```text
same_label_different_basin
fixture_equivalence_label_only
mapping_declared_after_outcome
proxy_score_relabel_as_transfer
hidden_support_reconstruction
support_reconstruction_as_transfer
boundary_mapping_missing
post_transfer_signature_missing
source_current_inputs_missing
cross_substrate_mapping_missing
AP4_dependency_omitted
AP5_dependency_omitted
semantic_identity_relabel
native_support_relabel
Phase8_or_ant_ecology_relabel
```

All active nulls must fail closed and assign no positive CT rung.

Controls should remain orthogonal. Each null should reject one false-positive
path rather than saying only "not transfer":

```text
same_label_different_basin -> rejects label identity
fixture_equivalence_label_only -> rejects mapping-free fixture similarity
proxy_score_relabel_as_transfer -> rejects proxy preservation
hidden_support_reconstruction -> rejects hidden rebuilding
support_reconstruction_as_transfer -> rejects post-hoc reconstruction
boundary_mapping_missing -> rejects unmapped boundary
```

I3 must instantiate every frozen I2 control, including replay/stress controls
as active-null/failure-baseline rows where the relevant blocker is present. It
passes only if `failed_open_controls = 0`, positive transfer evidence remains
closed, and no CT rung is assigned.

### Iteration 4 - Minimal Configuration Transfer Probe

Run the first positive configuration/fixture transfer probe. Required result is
at most `CT2` or `CT3` pending replay/control validation.

### Iteration 4-A - Topology / Fixture Variant Transfer Probe

Run at least one distinct mapping variant so N27 is not only a single fixture
label. This probes whether the transfer signature is mapping-specific and
source-current.

### Iteration 5 - Replay And Same-Basin Mapping Matrix

Replay I4/I4-A candidates and test whether same-basin signature, boundary
mapping, support/coherence floors, and flux balance survive artifact replay,
snapshot/load replay, and duplicate replay.

### Iteration 6 - Stress / Mapping-Variant Transfer Matrix

Stress declared mapping windows, boundary tolerance, support preservation, and
configuration/topology variants. This should distinguish narrow transfer from
variant-backed transfer.

### Iteration 7 - Controls, AP4/AP5 Dependency, And Claim Classification

Run the full control matrix and classify the strongest CT rung. AP4/AP5
dependencies must remain row-local. Native AP5 and AP5 NAT4-gap resolution stay
blocked unless separately source-backed.

### Iteration 8 - Closeout And N28 Handoff

Close N27 if warranted and hand off to N28 generative/extractive persistence.
N28 may consume N27 only as bounded transfer evidence, not semantic identity or
agency.

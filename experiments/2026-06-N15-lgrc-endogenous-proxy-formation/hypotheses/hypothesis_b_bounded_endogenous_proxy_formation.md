# Hypothesis B - Bounded Endogenous Proxy Formation

## Statement

```text
A proxy or target condition can be generated deterministically from
source-current runtime-visible state under bounded drift, freshness, budget,
and replay constraints rather than from declared target fixtures.
```

## N15-Specific Meaning

This hypothesis is about the AP5 transition. It requires more than a source
inventory. N15 must show that the target condition itself is derived from the
runtime-visible state surface and remains bounded, replayable, and budget-clean.

The expected formation surface is:

```text
evidence_strategy
old_best_claim_inputs
runtime_state_surface_id
source_current
endogenous_derivation_policy
dependency_trace
target_condition_surface
target_center
target_band
target_tolerance
drift_bound
drift_update_rule
drift_clamp_policy
replay_digest_inputs
replay_digest_algorithm
idempotency_digest_plan
budget_validity
artifact_only_replay_status
snapshot_load_status
order_inversion_replay_status
```

## Acceptance Requirements

Hypothesis B can be supported only if:

```text
target condition is generated before downstream use
target condition is derived from serialized source-current state inputs
constructed candidates preserve the closed claim ceilings of their source
experiments
the derivation policy is deterministic and replayable
dependency trace links every target field to source state or a declared bound
idempotency digest scope is recorded and reproducible
artifact-only replay reconstructs the generated target
external target injection controls fail closed
post-hoc proxy formation controls fail closed
unbounded target drift controls fail closed
budget-surface ambiguity controls fail closed
snapshot/load replay reproduces the same target condition
order-inversion replay does not change the target without a valid state change
rank or regulation behavior can consume the generated target without relabeling
it as semantic goal ownership
```

## Rejection Conditions

Reject or defer the hypothesis if:

```text
target condition is copied from an experiment fixture
target condition appears only after route or regulation outcome is known
target drift is unconstrained
budget validity is missing or evaluated after target use
dependency trace omits a target field
construction from prior experiments relabels AP3/AP4 evidence as goal
ownership, intention, agency, or native support
replay cannot reconstruct the generated target from serialized inputs
producer code directly mutates the target without recording derivation
```

## Claim Boundary

```text
bounded endogenous proxy formation != semantic goal ownership
runtime-derived target != intention
support-derived target != agency
artifact-level AP5 != native support
```

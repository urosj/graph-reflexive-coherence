# Hypothesis A - Withdrawal Resistance Under Declared Support Reduction

N21 can construct source-backed evidence that a declared basin signature remains
the same basin through a bounded withdrawal window when declared support is
weakened or removed.

## Expected Support

Hypothesis A is supported only if a withdrawal row records all of:

```text
N20 I5 withdrawal_resistance contract consumed
WR rung assigned only from source-backed N21 evidence
row-specific thresholds declared before use
declared support weakening or removal visible before evaluation
basin_signature_trace preserved within the same-basin rule
support/coherence floors preserved
boundary integrity preserved
flux/leakage not explaining apparent persistence
withdrawal replay reconstructs from declared source-current fields
WR4 replay requirement satisfied by artifact replay AND snapshot/load replay
AND duplicate replay
hidden support control fails closed
proxy-only success control fails closed
label-only continuation control fails closed
unsafe claim flags false
Hypothesis C passes
```

## Failure Conditions

Hypothesis A fails if any positive row depends on:

```text
changing the N20 basin signature
post-hoc continuation labels
hidden producer support
proxy improvement without same-basin continuation
support floor crossing
coherence floor crossing
boundary integrity failure
artifact replay, snapshot/load replay, or duplicate replay missing or failed
native support relabel
semantic agency or willpower relabel
Hypothesis C fails
```

## Claim Ceiling

The strongest admissible claim is:

```text
artifact-level withdrawal-resistance primitive candidate
```

This corresponds to the upper WR ladder only when replay, controls, producer
residue, naturalization debt, and unsafe-claim blockers are all recorded.

Blocked:

```text
agency
willpower
selfhood
identity acceptance
native support
Phase 8 implementation
sentience
```

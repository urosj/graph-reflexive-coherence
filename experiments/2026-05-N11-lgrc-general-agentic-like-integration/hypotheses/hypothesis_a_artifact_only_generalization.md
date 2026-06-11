# Hypothesis A: Artifact-Only Generalization

N10 proved a bounded artifact-only integration candidate. Hypothesis A asks
whether that integration can be replayed across declared variations without
private runtime state.

## Question

```text
Can the N10 route-memory-support-regulation composition remain replay-valid
when route context, support state, or proxy condition varies within a declared
generalization envelope?
```

## Required Evidence

```text
N10 source artifact digests
declared context/support/proxy variants
transfer row schema
artifact-only replay chain
budget-surface separation
source-current validation
distinct blockers for failed transfer lanes
claim flags all false
```

## Required Controls

```text
hidden context substitution -> blocked
stale support state -> blocked
stale proxy state -> blocked
out-of-envelope proxy target -> blocked
budget ambiguity -> blocked
claim promotion -> blocked
```

## Expected Conservative Result

```text
Some transfer lanes may pass.
Some transfer lanes may fail closed.
The useful result is the boundary of generalization, not universal success.
```


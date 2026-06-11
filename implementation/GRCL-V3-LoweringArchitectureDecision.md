# GRCL-v3 Lowering Architecture Decision

## Purpose

This note records the architectural boundary for `GRCL-v3` lowering after the
`grcv3.rich.v2` capability lift.

It answers one specific question:

- when does `GRCV3` stop relying semantically on the weaker `GRCV2` landscape
  blueprint path and move to family-native lowering?

## Decision

For `grcv3.rich.v2+`, `GRCV3` should move from:

- `GRCV2` blueprint + family enrichment

toward:

- family-native lowering with common seed parsing only

This decision now has a stronger long-term follow-on:

- neutral/common `GRCL` may remain on an interpretive lowering path
- weaker `grcv3.rich.v1` / `grcv3.rich.v2` may still require transitional
  projector logic
- but mature `grcv3.rich.v3+` should move toward **direct family-native
  assembly** rather than projector-style semantic interpretation

The important distinction is therefore not:

- lowering versus no lowering

It is:

- interpretive lowering
  versus
- deterministic family-native assembly

`GRCL-v3` does not become the runtime graph directly.
A construction step still exists.
But for mature `grcv3.rich.v3+`, that step should act more like:

- deterministic assembly of explicitly declared local motifs

and less like:

- heuristic interpretation of what a richer seed probably meant

This means:

- common seed parsing, normalization, loading, and version dispatch remain
  shared
- but explicit `GRCV3`-rich source semantics should no longer be flattened into
  a weaker `GRCV2` semantic blueprint and reconstructed afterward

## Schema Boundary

The boundary is intentionally tiered.

### 1. Neutral/Common Seeds And Weaker Rich Seeds

This includes:

- neutral/common `GRCL`
- `grcv2`
- transitional `grcv3.rich.v1`

These lanes may still use an interpretation-heavy projector path.

The projector is allowed to:

- infer missing attachment structure
- approximate local roles more aggressively
- enrich weaker source descriptions into executable topology

### 2. Family-Rich `grcv3.rich.v2+`

This lane should no longer rely on semantic interpretation of information the
seed already makes explicit.

The lowering path should behave as:

- deterministic family-native construction

not as:

- heuristic semantic enrichment

### 3. Mature `grcv3.rich.v3+`

Once the source contract is strong enough to describe the local constructive
motif directly, the preferred boundary becomes:

- direct family-native assembly

This still does **not** permit solved runtime-state injection.

It does **not** allow:

- solved gradients
- solved Hessians
- solved fluxes
- pre-declared spark/collapse runtime conclusions

It does allow:

- direct constructive specification of the local stencil that runtime
  differential state should emerge from

## What Remains Allowed Under Family-Native Lowering

`grcv3.rich.v2+` does **not** eliminate constructive discretization.

The lowering path may still make explicit, documented choices such as:

- how many support nodes realize a support arc
- how motif mass is distributed across lowered members
- how a channel polyline is sampled into interior nodes
- how initial conductance is assigned across lowered support edges
- how deterministic approximation is recorded when one source concept requires
  a discrete stencil

These are constitutive lowering choices, not semantic reinterpretation.

For mature `grcv3.rich.v3+`, the long-term goal is to reduce even these choices
to explicit assembly policy wherever practical, so that the remaining
construction step is visible, deterministic, and minimally interpretive.

## What Should Stop For `grcv3.rich.v2+`

Once the seed declares source semantics explicitly, the projector should stop:

- inferring the weak axis when the seed already names it
- inferring attachment sites when the seed already names them
- collapsing basin/channel/boundary roles into a weaker intermediate semantic
  surface and rebuilding them later
- relying on a weaker family blueprint as the authoritative semantic model for a
  richer family-specific seed

## Current State

The current implementation is still transitional.

At present, `GRCV3` still bootstraps through:

- `realize_grcv2_landscape_blueprint(...)`

before applying `GRCV3`-specific lowering.

That is acceptable for:

- neutral/common seeds
- `grcv3.rich.v1`

but it should be treated as a compatibility bridge rather than the long-term
shape for `grcv3.rich.v2+`.

## Implication For Ongoing Work

Future `GRCL-v3` work should follow this rule:

1. keep common seed parsing/loading shared
2. keep weaker schemas on the interpretive projector path
3. move `grcv3.rich.v2+` toward direct family-native lowering
4. treat any remaining `GRCV2` blueprint dependence in `grcv3.rich.v2+` as
   technical debt to be removed deliberately, not as the target architecture
5. treat `grcv3.rich.v3+` as the point where the preferred boundary becomes
   direct family-native assembly rather than projector-style interpretation

## Why This Matters

This boundary makes failures more honest.

If a `grcv3.rich.v2+` seed fails to spark, that should mean:

- either the source semantics are still insufficient
- or the family-native lowering choices are still wrong

It should not mean:

- a weaker intermediate blueprint silently normalized away the very geometry the
  richer seed was trying to preserve

## Status

This is a recorded design decision.

It does **not** yet mean the full codebase has completed the transition.
It means all further `GRCL-v3` work should be evaluated against this target
architecture.

## Addendum: `grcv3.rich.v4` Boundary

The next capability slice after the current `rich.v3` line should be accepted
only under a stricter rule.

For `grcv3.rich.v4`, the target is no longer:

- better projector tuning
- richer semantic lowering
- or another family-specific enrichment pass

The target is:

- direct translation from explicit `grcv3.rich.v4` source semantics into
  deterministic `GRCV3` family-native assembly

So `rich.v4` should **not** depend on:

- projector-style semantic interpretation
- compatibility-path blueprint authority
- heuristic reconstruction of interior intent from weaker source structure
- or iterative refinement of lowering rules

It may still contain a deterministic construction step, but that step must be
understood as:

- direct assembly of explicitly declared source structure

not as:

- semantic projection of an underspecified source into a guessed runtime motif

The working rule is therefore:

- neutral/common `GRCL` and weaker rich schemas may remain interpretive
- `grcv3.rich.v3` is the last acceptable transitional direct-assembly lane
- `grcv3.rich.v4` should be introduced only as a **direct-translation
  contract** with no projector-style semantic lowering

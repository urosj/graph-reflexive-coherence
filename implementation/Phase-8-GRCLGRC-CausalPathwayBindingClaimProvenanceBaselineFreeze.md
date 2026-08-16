# Phase 8 GRC/LGRC Causal Pathway Binding And Claim Provenance Baseline Freeze

**Iteration:** 112

**Status:** Passed

**Date:** 2026-08-16

**Source behavior changed:** No

## Authority Boundary

This tranche begins after the accepted causal-pathway consolidation closeout
at `f612a93154ba31b5b62fa0f7d3b7590035468d3a`. It consumes the final accepted
registry, crosswalk, matrix, selector, conformance policy/checker, Iteration 111
result, closeout, and current claim/reference documents. It does not rewrite or
supersede them.

The final embedded authority digests are:

```text
registry  = a266b33da10778e8caf5ad7d4a4bfe4b71aed9d0df563fd6c74e7d4ed6cb486b
crosswalk = 0036dcdf54f4663bed183387db1c8f657eb44a694252ef44421be56fb239ff06
matrix    = d1dbbdcb911cf34b399562c2dfe5122606c0de8d48d9634bc6af1e3d92e09e90
selector  = f57545997fac63c9e465d21e0c840971aee073bd89aff135fb5d93a1ce134e1b
policy    = 7227c764e41b3d9964f306eff2830ded17afd8ace30df2eec4a58b0296ababf9
```

The accepted consolidation checker passes all 20 rules with zero issues and
conformance digest
`14a4ee2a4cc2dc4beca4ce056a15548df90ed4f0d33a707d33facc1a1ce1c6b2`.
No historical intermediate bundle digest is used as current authority.

## Protected State

```text
branch = feat/causal-pathway-binding-claim-provenance
HEAD = f612a93154ba31b5b62fa0f7d3b7590035468d3a
tree = 40cfb7cdf72dbe5e0149362bd22fe37d0a6d7286
src/test/example diff = empty
runtime behavior changed = false
```

| Tree | Git tree | Files | Sorted file-hash manifest digest |
| --- | --- | ---: | --- |
| `src` | `3e712f89f9a99c2eef6366409d21b40c55f34311` | 174 | `ef368a2bbc79a43eb433c984edaa7f4dadd8d8cb252c3ff716932c2889f27f79` |
| `tests` | `5c7b4078951045a590d1e2881fc3d6491f5595f3` | 175 | `8db6c54e209d8b663b473d71af53c30dbb1e6086b5d42ed245a096ecf3bc64bb` |
| `examples` | `bc31ce3a8567a6bb896805571501e31d24e0242e` | 32 | `847a31fc48bf0299f36a64ab8adf2f32af8b3b82ea2310ac82fbb13093b56365` |

The machine freeze records each authority file hash and the dependency-input
hashes from `pyproject.toml`, `requirements*.txt`, and `uv.lock`.

## Pre-Change Test Freeze

The repository environment was created at `.venv` from the package metadata in
`pyproject.toml` through the repository's editable requirements chain.

```text
focused accepted GRC/LGRC suite = 528 passed in 12.536 seconds
full repository suite = 1,211 passed in 309.891 seconds
accepted consolidation conformance = 20 / 20 passed, 0 issues
```

An earlier system-interpreter collection attempt failed before running tests
because the checkout initially had no environment and `networkx` was absent.
It is an environment setup failure, not baseline scientific evidence. All
accepted results above use `.venv/bin/python`.

## I112 Decision

One structural model survived the required pathway-only, producer-mediated,
and unregistered-candidate pressure cases: an explicit linker that resolves a
declared stage to a verified mechanism-specific callable and records use around
delegation. The model needs no common execution interface and does not choose a
pathway for the caller.

Iteration 113 may now implement the separate binding-symbol map and minimal
linker. This readiness does not authorize registry changes, candidate
promotion, generic causal admission, ecological interpretation, or N32.

## Machine Record

See
[`Phase-8-GRCLGRC-CausalPathwayBindingClaimProvenanceBaselineFreeze.json`](./Phase-8-GRCLGRC-CausalPathwayBindingClaimProvenanceBaselineFreeze.json).

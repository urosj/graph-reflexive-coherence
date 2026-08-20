# Phase 8 GRC/LGRC Causal Pathway Binding And Claim Provenance Iteration 120

**Iteration:** 120 — Effects And Authority

**Status:** Passed

**Date:** 2026-08-20

**Production runtime behavior changed:** No

## Outcome

Iteration 120 extracts effect contracts and conservative result classification
into `effects.py`, then extracts accepted authority and binding-map admission
into `authority.py`. Both providers are session-independent and sit above the
I119 identity foundation without a reciprocal dependency.

The change starts from the reviewed I119 checkpoint `69f53b2`. The temporary
compatibility implementation falls from 5,880 to 4,979 lines. The permanent
provider layer now consists of the unchanged 459-line `identity.py`, the new
317-line `effects.py`, and the new 664-line `authority.py`, behind the 113-line
public compatibility facade.

## Effect Provider

[`binding/effects.py`](../src/pygrc/causal_pathways/binding/effects.py) owns:

- the three public return/effect category constants;
- `EffectOutcomeContract` parsing, validation, canonical records, and
  claim-qualifying outcome limits;
- stable Python return-shape classification;
- boolean-attribute and bound-instance snapshot-digest effect evidence; and
- trusted exact-symbol returned-effect classification through a narrow
  structural provider protocol.

The structural protocol exposes only `effect_outcome_contract(symbol_id)`.
Consequently, effect classification does not import or know about
`CausalPathwayAuthority`, the session, scopes, candidates, or artifacts.

## Authority Provider

[`binding/authority.py`](../src/pygrc/causal_pathways/binding/authority.py) owns:

- the six-file authority-path map and JSON authority loading;
- `BindingAcceptanceAnchor` parsing, trusted-digest validation, accepted
  source-map semantics, source-manifest comparison, and effect-contract set;
- `CausalPathwayAuthority` artifact-digest validation, stage/crossing closure,
  source verification, staleness checks, and admitted pathway/composition,
  symbol, crossing, invalid-relabel, and effect-contract lookup; and
- `UnknownPathwayError` and `UnknownCompositionError`.

Loaded authority collections remain top-level `MappingProxyType` views,
symbol/crossing records remain frozen or tuple-valued, public pathway and
composition lookups return defensive deep copies, artifact identities are
read-only, and the frozen acceptance anchor returns a defensive record copy.
The candidate subsystem's temporary JSON helper was renamed
`_load_candidate_evidence_json` so generic authority loading no longer remains
in `_legacy.py`.

## Dependency Boundary

The permanent provider direction is:

```text
identity -> effects -> authority
    \_________________^
```

The arrows express foundation-to-consumer layering. In import terms,
`identity.py` is a leaf, `effects.py` imports only identity,
and `authority.py` imports effects and identity. `_legacy.py` consumes all
three providers, while none of them imports `_legacy.py` or references
`PathwayBindingSession`.

The public facade imports provider-owned public objects directly. All 48 root
and facade exports retain exact object identity, signatures, exception
hierarchy, and I118-observed behavior. Internal defining-module paths remain
noncontractual.

## Architecture Enforcement

[I120 architecture tests](../tests/integrations/test_causal_pathway_binding_i120.py)
enforce:

- the exact acyclic import graph across identity, effects, authority, legacy,
  and facade modules;
- effect and authority public ownership plus root/facade/provider identity;
- ownership of private effect classification and authority-loading helpers;
- absence of extracted definitions and constants from `_legacy.py`; and
- read-only loaded authority collections and defensive public record returns.

## Verification

All commands used the repository `.venv` and `PYTHONPATH=src:.` where package
loading required it.

| Gate | Result |
| --- | --- |
| I118 API/artifact/runtime/checker freeze | Passed; 48 exports, 12 cases, 26 files |
| I120 architecture tests | 5/5 passed |
| Complete focused binding suite | 119/119 passed in 37.806 seconds |
| Binding conformance | 20/20 passed, zero issues; digest `eb54f646569cf4b91e5f410fe94d6bbd0aae6706871e83431ee9d919cc42c823` |
| Predecessor conformance | 20/20 passed, zero issues; digest `14a4ee2a4cc2dc4beca4ce056a15548df90ed4f0d33a707d33facc1a1ce1c6b2` |
| Binder-scoped Ruff | Passed |
| Binder-focused mypy under Python 3.12 | Passed; 11 source files |
| `compileall src tests scripts examples` | Passed |
| Standard-library provider discovery | Passed |
| `git diff --check` | Passed |

The full project suite is intentionally not repeated in I120. The tranche plan
requires it after structural completion in I123 and again at I125 closeout.

## I121 Boundary

Iteration 121 may extract candidate declarations, reviews, mechanism evidence,
verified mechanisms, request wrappers, typed-default and source-consumption
proofs, and invalid-relabel controls into `candidates.py`. It must depend only
on permanent providers and narrow recorder/factory protocols rather than a
concrete session, replay the R4-B01 through R8-B01 pressures, and preserve the
I118 oracle and every I120 dependency rule.

I120 authorizes no candidate, scope, artifact, session, claim-envelope, or
conformance semantic change.

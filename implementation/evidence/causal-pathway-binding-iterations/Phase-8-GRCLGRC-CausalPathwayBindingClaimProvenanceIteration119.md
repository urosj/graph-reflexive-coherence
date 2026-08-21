# Phase 8 GRC/LGRC Causal Pathway Binding And Claim Provenance Iteration 119

**Iteration:** 119 — Package Boundary And Identity Foundation

**Status:** Passed

**Date:** 2026-08-20

**Production runtime behavior changed:** No

## Outcome

Iteration 119 atomically replaces `pygrc.causal_pathways.binding` as a single
module with a package behind the same import path. The package exposes the same
48-object public surface, retains not-yet-extracted behavior in a private
compatibility module, and establishes `identity.py` as the first permanent,
session-independent provider.

The change starts from the reviewed I118 checkpoint `82c6322`. The removed
6,282-line `binding.py` has source SHA-256
`84d5499687888b68e91809b15ea79d8b06e197f7876da5a875ee44bb7b23f979`.
Its remaining responsibilities now occupy the temporary 5,880-line
`binding/_legacy.py`; identity responsibility occupies the 459-line
`binding/identity.py`; and `binding/__init__.py` is the explicit compatibility
facade.

## Package Boundary

- [`binding/__init__.py`](../../../src/pygrc/causal_pathways/binding/__init__.py)
  preserves all imports from `pygrc.causal_pathways.binding` and object identity
  with the root `pygrc.causal_pathways` exports.
- [`binding/identity.py`](../../../src/pygrc/causal_pathways/binding/identity.py) owns
  canonical digests, binding-semantic and source-manifest digests, source-file
  hashing and verification, callable definition/owner resolution, callable
  identities and cached guards, source-symbol bindings, crossing bindings, and
  the errors required to fail those operations closed.
- the I119 `binding/_legacy.py` compatibility implementation was removed by
  I123; its remaining responsibilities now live in
  [`binding/session.py`](../../../src/pygrc/causal_pathways/binding/session.py).
  `identity.py` retains no reciprocal package dependency and no session
  reference.
- The former `src/pygrc/causal_pathways/binding.py` no longer exists, so Python
  never has to choose between a same-named module and package.

Internal defining-module paths are intentionally noncontractual. Public import
paths, identities, signatures, exceptions, runtime results, and serialized
artifacts remain contractual through the I118 oracle.

## Compatibility Details

All 48 public exports retain root/facade object identity and match the I118
behavioral freeze. All 12 regenerated lock/receipt pairs remain byte-identical,
and the 26-file inherited evidence manifest remains unchanged.

Candidate request wrappers are still implemented temporarily in `_legacy.py`.
Their runtime descriptor preserves the historical
`pygrc.causal_pathways.binding._CandidateRequestMapping` type label because
that label is embedded in accepted receipt bytes. This is a serialization
compatibility rule, not a claim or schema change.

The focused tests no longer patch `pygrc.causal_pathways.binding._load_json` or
reach through `binding.inspect`. Authority-drift tests now substitute bytes at
the filesystem-read boundary, while source-cache tests patch the responsible
identity provider or Python's standard `inspect` module. The broader mypy
scope that previously reported two private-hook findings is now clean.

## Architecture Enforcement

[I119 architecture tests](../../../tests/integrations/test_causal_pathway_binding_i119.py)
enforce:

- exclusive package layout with no same-named `binding.py`;
- exact public root/facade export identity;
- ownership of ten public and five private identity primitives by
  `identity.py`;
- absence of extracted definitions from `_legacy.py`;
- a leaf identity provider with no relative package imports or session
  dependency; and
- absence of the former private monolith patch hooks from the compatibility
  facade and focused tests.

## Verification

All commands used the repository `.venv` and `PYTHONPATH=src:.` where package
loading required it.

| Gate | Result |
| --- | --- |
| I118 API/artifact/runtime/checker freeze | Passed; 48 exports, 12 cases, 26 files |
| I119 architecture tests | 5/5 passed |
| Complete focused binding suite | 114/114 passed in 33.196 seconds |
| Binding conformance | 20/20 passed, zero issues; digest `eb54f646569cf4b91e5f410fe94d6bbd0aae6706871e83431ee9d919cc42c823` |
| Predecessor conformance | 20/20 passed, zero issues; digest `14a4ee2a4cc2dc4beca4ce056a15548df90ed4f0d33a707d33facc1a1ce1c6b2` |
| Binder-scoped Ruff | Passed |
| Binder-focused mypy under Python 3.12 | Passed; 8 source files |
| `compileall src tests scripts examples` | Passed |
| Standard-library package discovery | Passed |
| `git diff --check` | Passed |

The full project suite is intentionally not repeated in I119. The tranche plan
requires it at the accepted I118 baseline, after structural completion in
I123, and again at I125 closeout.

## I120 Boundary

Iteration 120 may extract effect contracts and effect classification into
`effects.py`, then authority and acceptance-anchor loading into `authority.py`.
It must establish the permanent dependency chain `identity -> effects ->
authority`, retain the public facade and temporary compatibility module, and
pass the same I118/focused/conformance/static gates without changing accepted
artifact bytes or runtime behavior.

I119 authorizes no candidate, scope, artifact, session, claim-envelope, or
conformance semantic change.

# Phase 8 GRC/LGRC Causal Pathway Binding And Claim Provenance Iteration 118

**Iteration:** 118 — Compatibility And Refactor Baseline

**Status:** Passed

**Date:** 2026-08-20

**Production source behavior changed:** No

## Outcome

Iteration 118 freezes the accepted binder before modularization. It adds a
reproducible public behavioral API contract, a byte-exact artifact and runtime
corpus, explicit fail-closed exception observations, context-manager and return
type observations, and a guard that keeps the independent conformance checker
separate from binder derivation logic.

The baseline is rooted at source commit
`8e07e17688db3d49420d933f41ba936e5dab9dcb`, source tree
`984df49232285e0f63e48c98c37606b04873bd84`, and binder source SHA-256
`84d5499687888b68e91809b15ea79d8b06e197f7876da5a875ee44bb7b23f979`.
No file under `src/` changed during I118.

## Frozen Contracts

- Public behavioral API: 48 exports, import identity, class/function/method
  signatures, dataclass fields, and exception hierarchy. Freeze digest:
  `45254d8b627fad7bc0afef7e0a0e858537318d44146a7070f4371fb257d62812`.
- Artifact and runtime corpus: 26 canonical I115/I116 files, 12 regenerated
  cases, seven exception conditions, and three context managers. Freeze digest:
  `5808866c4567db959700a51ea896daae3d502e9a970c16c4ee36ceb75b38550e`.
- Checker independence: direct/dynamic import inventory and exact checker source
  identity, with zero binder imports. Freeze digest:
  `13af63b147b83cea4d7883116617c379e02732089b170031ed0115e8e5043397`.

The public freeze deliberately records import paths and behavior without making
future internal defining-module paths contractual. The checker freeze is
stricter than the minimum harmless-schema-sharing allowance: the accepted
checker currently imports no `pygrc.causal_pathways` implementation at all.

## Regenerated Corpus

The builder regenerates and compares exact JSON bytes for:

1. a simple native pathway;
2. producer-mediated `CMP-20`;
3. explicit-adapter `CMP-26`;
4. diagnostic-only `CMP-04`;
5. ambiguous crossing with unused declarations;
6. an unregistered candidate composition;
7. explicit dynamic A/B choice;
8. a multi-edge graph;
9. a reviewed invalid-pair candidate over the `CMP-05` endpoints;
10. a declared-but-unused candidate pathway;
11. a returned non-qualifying effect; and
12. a raised effect.

The first eight must remain byte-identical to the accepted I116 artifacts. The
last four are retained under
`implementation/evidence/causal-pathway-binding/i118/corpus/`.
Together they cover every semantic family required by the Iteration 118 plan.

## Public Behavioral Pressure

The freeze independently exercises seven important fail-closed conditions:
untrusted acceptance-anchor digest, unknown pathway, unknown composition,
unsupported composition, invalid candidate kind, declaration after lock, and
missing source symbol. It also freezes the return object types of authority
loading, session/pathway/link creation, lock and receipt creation, bound
invocation, record projection, and unbound classification.

Composition, alternative-selection, and candidate execution scopes each
return themselves from `__enter__`, return `False` from a normal `__exit__`,
and leave the session in its locked phase. Those behaviors are now part of the
I118 compatibility oracle.

## Verification

All accepted commands used the repository `.venv` and the package metadata in
`pyproject.toml`.

| Gate | Result |
| --- | --- |
| I118 freeze self-check | Passed; 48 exports, 12 cases, 26 files |
| Focused binding suite | 109 passed in 32.052 seconds |
| Full project suite | 1,320 passed in 444.848 seconds |
| Binding conformance | 20/20 passed, zero issues |
| Predecessor conformance | 20/20 passed, zero issues |
| Binder-scoped Ruff | Passed |
| Binder/I118 mypy under active Python 3.12 | Passed |
| `compileall` | Passed |
| `git diff --check` | Passed |

The machine execution record preserves the exact commands and digests in
[I118BaselineExecution.json](../causal-pathway-binding/i118/I118BaselineExecution.json).

## Static-Scope Note

Repository-wide Ruff and unscoped mypy are not clean baselines in this checkout.
Ruff reports 3,471 pre-existing findings across unrelated examples and tests.
Unscoped mypy reports missing third-party stubs, existing landscape fixture
import problems, and a Python-target mismatch with the installed NumPy stubs.
The broader binding-focused mypy command under Python 3.12 additionally exposes
two existing test references to the private `binding.inspect` import.

I118 does not alter unrelated files to conceal those conditions. The accepted
I118 static surface covers the binder and the new enforcement test, while I119
already requires migration away from private monolith patch points.

## Reproduction

```bash
PYTHONPATH=src:. .venv/bin/python \
  scripts/build_phase8_causal_pathway_binding_i118.py --check
```

The builder writes freezes only with explicit `--write`; normal enforcement
uses `--check` and writes regenerated artifacts only to a temporary directory.

## I119 Boundary

Iteration 119 may now atomically replace `binding.py` with the compatibility
package, retain the unchanged monolith temporarily behind
`binding/__init__.py`, and extract `identity.py`. It must pass the I118 public
API, artifact/runtime, checker-independence, focused, conformance, and static
gates before closing.

I118 authorizes no semantic change, artifact schema change, candidate
promotion, generic dispatcher, process-wide causal-monitor claim, or expansion
of the accepted claim envelope.

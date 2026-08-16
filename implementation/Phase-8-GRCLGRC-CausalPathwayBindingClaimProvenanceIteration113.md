# Phase 8 GRC/LGRC Causal Pathway Binding And Claim Provenance Iteration 113

**Status:** Passed

## Result

Iteration 113 adds the separate binding-symbol authority and minimal explicit
linker without changing GRC9V3 or LGRC9V3 mechanism implementations.

```text
admitted pathways mapped = 23 / 23
authority-bearing stages mapped = 52 / 52
exact callable links = 55
unknown pathway/composition = rejected
unsupported/invalid registered composition = rejected as admitted binding
candidate canonical collision = rejected
producer policy mismatch = rejected before delegation
focused binding/import tests = 11 passed
runtime numerical behavior changed = false
```

## Binding Surface

`pygrc.causal_pathways` loads the accepted registry, crosswalk, composition
matrix, selector, policy, and separate binding map. Loading recomputes every
internal artifact digest, verifies that the binding map consumes the current
accepted digests, checks exact stage closure, hashes every bound source file,
imports every qualified symbol, and requires each target to remain callable.

The public binding operations are exact:

```text
bind_pathway(pathway_id, declared stages)
bind_composition(composition_id)
declare_candidate(distinct candidate identity and debt)
declare_alternatives(explicit set and selection authority)
```

The alternative declaration has no selection method. The caller remains the
selection authority. Unsupported missing crossings and invalid relabel rows
cannot be bound as executable compositions.

## Mechanism-Specific Delegation

A bound pathway exposes `symbol(stage_id, ...)`, returning a verified Python
callable link to the exact recorded source symbol. Calling the link delegates
the native arguments and result unchanged. There is no pathway-level
`execute`, causal-work argument schema, or intent router.

The focused native-pathway test schedules an LGRC packet through the existing
`LGRC9V3.schedule_packet_departure` method and records the exact admitted
pathway, stage, and symbol. The runtime queue behavior remains the existing
implementation's behavior.

Multiplexed producer links carry exact required keyword arguments. The CMP-20
feedback producer link rejects a flux-route policy and accepts only the
registered feedback-eligibility producer policy, retaining `CMP-20`,
`feedback_eligibility_producer`, and `installed_producer` identities.

## Candidate Boundary

Candidate declarations require a distinct noncanonical identity, purpose,
owner, evidence owner, admitted constituents, and—for composition candidates—
explicit endpoints and a genuinely new relation description. All six authority
coordinates are present; omitted coordinates become `unresolved` rather than
native defaults. The claim ceiling is fixed to `experimental_unregistered` and
promotion status to `none`.

## Verification

```text
.venv/bin/ruff check selected I113 source/tests = passed
.venv/bin/python -m py_compile selected I113 source = passed
.venv/bin/mypy --python-version 3.12 selected I113 source/tests = passed
PYTHONPATH=src .venv/bin/python -m unittest -q
  tests.integrations.test_causal_pathway_binding
  tests.core.test_import_smoke = 11 passed
git diff --check = passed
```

The explicit mypy Python version matches the active `.venv` interpreter. The
repository default declares Python 3.11, while the locally installed newest
NumPy stubs use Python 3.12 type-statement syntax.

## Remaining Boundary

I113 invocation records are in-memory linkage proof only. Iteration 114 still
owns the exact pre-execution lock, use graph, durable receipt, structured claim
envelope, declared-but-unused reporting, candidate use, and dynamic-choice
receipt semantics. No I113 result is yet an accepted final binding receipt.

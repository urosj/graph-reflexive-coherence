# Phase 8 GRC/LGRC Causal Pathway Binding And Claim Provenance Iteration 114

**Status:** Passed

## Result

Iteration 114 adds the pre-execution lock, actual-use receipt, pathway-use
graph, and structured conservative claim envelope on top of the exact I113
callable linker.

```text
bound calls before lock = rejected
declarations or symbol selection after lock = rejected
actual link absent from exact lock = rejected
authority/source drift at lock or receipt = rejected
declaration without successful use = visible but not claim-qualified
failed invocation = recorded but not behavioral evidence
candidate relation = visibly experimental_unregistered
dynamic A/B branch = caller-selected and receipt-recorded
chained registered compositions = no synthesized larger claim
focused binding/import tests = 19 passed
```

## Exact Lock

`freeze_lock()` closes the declaration phase before execution. Its canonical
JSON record freezes the source revision; registry, crosswalk, matrix, selector,
conformance-policy, and binding-map digests; declared pathway and stage IDs;
registered composition IDs; expected exact callable symbols and source hashes;
allowed dynamic alternatives and their selection authority; explicit producer
and adapter cuts; configured and producer residue; candidate declarations;
blocked claims; and the pre-execution claim envelope.

The lock digest is computed over canonical sorted JSON. A verified callable
checks its complete pathway, stage, symbol, composition, and binding identity
against the immutable lock record before delegation. Reloading the authority
at lock and receipt boundaries catches knowledge-artifact, binding-map, and
source-link drift.

## Receipt And Use Graph

`build_receipt()` seals the session and links the receipt to the exact lock
digest. It records returned and raised mechanism-specific invocations, actual
successful pathway/stage/symbol use, registered compositions whose required
endpoint stages all returned, producer and adapter cuts used, candidate uses,
dynamic alternatives actually taken, declared-but-unused bindings, artifact
identities, blocked claims, and a canonical receipt digest.

Admitted graph nodes retain the pathway identity, actual stages and symbols,
availability/activation/staleness status, mechanism ownership, and configured
and producer residue. Registered edges retain the matrix identity and status,
adapter and producer ownership, authority transfer/retention, information
compression, matrix claim ceiling, and blocked relabels. Candidate nodes and
edges use a distinct `experimental_unregistered_candidate` kind and retain
their unresolved authority and residue debt.

Endpoint co-use does not create an edge. A composition appears as exercised
only when every required endpoint stage has returned through its composition
binding. Two registered compositions can coexist in one lock or receipt, but
the artifact explicitly records that it did not synthesize a larger chain
claim.

## Conservative Claims

Pathway-only receipts carry only each registry contract's supported claims and
blocked claims. Registered crossings use the matrix row's claim ceiling rather
than an intersection of endpoint claims. Producer-mediated `CMP-20` retains
the feedback producer identity, `installed_producer` owner, transferred
eligibility/direction/threshold/schedule authority, and the blocked
`lawful_native` relabel.

Any exercised candidate forces `experimental_unregistered = true`, overall
status `experimental_unregistered`, promotion status `none`, and explicit
blocked native/admitted claims. A failed callable invocation remains visible
in the receipt but does not make the pathway a successful behavioral use.

## Dynamic Choice Pressure

The consumer declares both allowed pathways and an explicit selection
authority before locking. The alternatives object exposes no selection
operation. In the pressure test, consumer code calls only the snapshot branch;
the receipt reports that branch as actually used and the packet branch as
declared but unused.

## Verification

```text
.venv/bin/ruff check selected I114 source/tests = passed
.venv/bin/python -m py_compile selected I114 source = passed
.venv/bin/mypy --python-version 3.12 selected I114 source/tests = passed
PYTHONPATH=src .venv/bin/python -m unittest -q
  tests.integrations.test_causal_pathway_binding
  tests.core.test_import_smoke = 19 passed
```

No GRC9V3 or LGRC9V3 execution implementation was changed. Iteration 115 owns
prospective artifact conformance, target-isolated negative controls, and the
post-source-change affected/consolidation/full-suite verification.

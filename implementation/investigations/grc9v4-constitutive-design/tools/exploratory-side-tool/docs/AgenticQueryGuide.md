# Agentic Query Guide

This guide describes how an automated research agent can query the accepted
GRCv4 exploratory side-tool API. The primary API is a local Python interface;
the Phase 9 web service exposes read-only projections of selected results.
The API reconstructs accepted evidence and evaluates a closed set of
structural counterfactuals; it does not create scientific evidence or predict a
gate that has not been rerun.

## ATC bounded research successor

For the current admitted five-realization Candidate-A research context use
`grcv4_explorer.atc_rgatc.load_current_forensic_context` and the
[ATC query guide](./ATCQueryGuide.md). `atc_rgatc.reconstruction_path` follows
accepted ancestry; choose `atc`, `atc_pc`, `atc_ci`, `atc_cip` or
`atc_rgatc.debt_lifecycle` explicitly for the intended profile-local debt view.
These are bounded research results, including a retained A_OS negative
exclusion, not native ATC support. `atc-rgatc-query discover` observes the
RGATC inventory; `audit` validates its complete predecessor chain;
`summary` returns five source-bound program-closure rows.
Older ATC commands retain their frozen scopes.
Ordinary historical discovery does not cover ATC evidence. The loaders below
retain pre-ATC authority and cannot resolve these research claims.

## Pre-ATC P9 initializer, abundance and receipt-parent authority

P9-7.2a now admits the accepted **optional initializer design**, not implemented
C→A migration. Use `grcv4_explorer.a_initializer.load_current_forensic_context`
for the complete pre-ATC graph. Existing current-loader imports from `abundance`
and `receipt_parents` delegate to it. The explicit
`abundance.load_abundance_forensic_context` preserves the pinned P9-4.9.1a
historical graph and cannot resolve the new initializer IDs.

After the root/side setup below:

```python
from grcv4_explorer.a_initializer import load_current_forensic_context, initializer_authority
from grcv4_explorer.forensic import contract_provenance, debt_lifecycle

context = load_current_forensic_context(root, side)
contract = contract_provenance(context, "P9-EC-A-INITIALIZER-REFERENCE-PASS")
debt = debt_lifecycle(context, "P9-7.2a-DEBT-A-INITIALIZER-SOURCE")
views = initializer_authority(root, side)
```

`P9-7.2a-CL-O-INIT-001` remains optional. The debt trace separates its
design-resolved producer choice from a `forward_verification_routing` row for
`P9-7.2a-VO-A-INITIALIZER-INTEGRATION`; the latter is not backward evidence.
`P9-O-A-INITIALIZER-REFERENCE-PASS` has a typed object-dependents trace.
The HTTP `/api/a-initializer`, notebook `a-initializer-authority` cell and
**Load initializer authority** browser button/selectors expose exactly these
traces. Source/admission/design drift holds current queries, and failed refresh
clears old output. Payload/spec binding, positive C→A and aggregate 7.2a remain
pending; no G2/G3 or specialization support is inferred. Historical graph rows,
contracts and source identities are unchanged.

P9-4.9.1a is an accepted append-only availability contract.
`grcv4_explorer.abundance.load_current_forensic_context` remains a compatible
current import, now delegating to the initializer successor.
`load_parent_forensic_context` reconstructs only the pinned historical P9-4.9.2
layer. Current discovery must include all admitted sources and fails closed on changed,
missing or unprocessed source; there is no historical fallback.

```python
from grcv4_explorer.abundance import load_current_forensic_context, abundance_authority

context = load_current_forensic_context(root, side)
views = abundance_authority(root, side)
```

After the root/side setup below, query `P9-4.9.1a-CL-N-001`,
`P9-4.9.1a-DEBT-ABUNDANCE`, `P9-O-ABUNDANCE-INTERFACE` or
`P9-EC-ABUNDANCE-INTERFACE`, `P9-EC-ABUNDANCE-OBSERVATION` and
`P9-EC-ABUNDANCE-FAILURE-AND-CEILING` with the existing typed functions.
The debt is resolved at bounded design scope, with implementation/product review
still distinct. No numeric definition, GRC9V4 runtime support or G2 is inferred.
**Load abundance authority** in the Phase 9 browser and the notebook's
`abundance-authority` cell expose those same traces, including classifications,
source/edge references and trace digests; failure clears stale output.

For current claim investigations, use the append-only P9 context below. The
existing `load_successor_forensic_context` intentionally reconstructs D11 only;
`load_forensic_context` reconstructs ET-C2. Neither silently admits new sources.

```python
from pathlib import Path
import sys

root = Path.cwd()  # repository root
side = root / "implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool"
sys.path.insert(0, str(side / "tool/src"))
from grcv4_explorer.receipt_parents import load_current_forensic_context, parent_authority
from grcv4_explorer.forensic import contract_provenance, debt_lifecycle

context = load_current_forensic_context(root, side)
contract = contract_provenance(context, "P9-EC-RECEIPT-PARENT-CHAIN")
debt = debt_lifecycle(context, "P9-4.9.2-DEBT-PARENTS")
views = parent_authority(root, side)  # same typed traces as notebook/browser
```

`P9-4.9.2-CL-N-001` is accepted bounded structural authority. It resolves absent
parent-selection authority, not a D10/D11 extraction omission. The new chain,
admission and ceiling contracts have explicit required support; historical
contract dispositions and graph rows remain unchanged. This does not establish
public-facade, other-profile, GRC9V4 or G2 conformance. Current loading checks
exact source discovery and pinned admission; missing, changed or unprocessed
sources hold it without a historical fallback.
This P9 overlay is admitted for the forensic queries shown here. Historical
counterfactual scenarios are not silently promoted into predictions about the
new parent policy or its runtime implementation.

`run.py discover-sources` observes the current admitted source inventory.
Use `--scope d11` or `--scope et-c0` only for an explicitly historical discovery
comparison; newer files correctly appear as unprocessed relative to that scope.

Open `run.py serve-phase9` and use **Load parent authority** to select the claim,
debt, object or one of the three contracts. The existing Phase 9 notebook has
the same executable query. Both clear stale output on failure and retain
classification, source/edge references and trace digests.

## Short Glossary

| Term | Meaning in this tool |
| --- | --- |
| **spine** | The readable accepted-gate path used for orientation; it is not the complete lineage DAG. |
| **companion branch** | An accepted branch beside the spine, including successors, corrections, realizations, or provenance work. |
| **bearing debt** | A source-linked obligation that bears on a stronger claim and must remain attached to its claim lineage. |
| **claim ceiling** | The strongest claim currently earned; stronger relabels remain blocked. |
| **provenance hardening** | A source-owned lock against promoting an equation, role, or lineage beyond demonstrated provenance. |
| **resolved negative** | An accepted negative boundary, not missing data and not a generic rejection of all future alternatives. |

## Authority Boundary

Every historical forensic result is bound to:

- the accepted ET-C1 source-bundle digest;
- the validated ET-C2 graph digest;
- an exact source record and JSON pointer for every row; and
- exact graph-edge witnesses.

Post-D11 queries add an `authority_extension_digest` bound to the accepted
ET-C10 D11 source contract, source-bundle manifest, and append-only graph
extension. The ET-C2 identity remains present as the immutable historical base;
it is not relabeled as if D11 had existed at ET-C2.

Treat `source_ref`, `edge_refs`, and the trace digest as part of the answer.
Do not summarize a row as an accepted claim without retaining its
`classification`. Verification obligations are forward work, not backward
evidence. A counterfactual result ends at `unknown_beyond_evidence_frontier` or
`requires_reexecution_from_gate`; an agent may not fill in what happens after
that point.

## Environment

From the repository root:

```bash
TOOL=implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool
python3 "$TOOL/scripts/bootstrap.py"
.venv/bin/python "$TOOL/scripts/run.py" doctor
.venv/bin/python "$TOOL/scripts/run.py" discover-sources
```

The first command may use host Python only to create and re-enter the
repository `.venv`. Every subsequent command uses `.venv`; Node and npm remain
tool-local.

`discover-sources` defaults to the current admitted inventory, including the
initializer. Explicit `--scope et-c0` retains the historical observation and
reports later sources as unprocessed; ET-C0 is not rewritten. The historical
D11 admission remains independently verifiable through:

```bash
.venv/bin/python "$TOOL/scripts/run.py" audit-iteration10-d11
.venv/bin/python "$TOOL/scripts/run.py" test-iteration10-d11
```

Any record outside the current admitted inventory still requires an explicit
successor adapter/readmission cycle.

The interactive command remains `serve-iteration8` because ET-C8 owns the
latest accepted browser distribution. `verify-iteration9` verifies that ET-C8
distribution together with the complete accepted reconstruction chain, these
guides, and the accepted ET-C9 closeout. ET-C9 is a verification/closeout
layer, not a second browser build.

## Loading The API

The package is investigation-local and is not installed globally. In a query
script run from the repository root, add the tool's `src` directory explicitly:

```python
from pathlib import Path
import sys

TOOL_ROOT = Path(
    "implementation/investigations/grc9v4-constitutive-design/"
    "tools/exploratory-side-tool/tool"
).resolve()
SIDE_TOOL_ROOT = TOOL_ROOT.parent
sys.path.insert(0, str(TOOL_ROOT / "src"))

from grcv4_explorer.successor import load_successor_forensic_context
from grcv4_explorer.paths import repository_root

repo_root = repository_root()
context = load_successor_forensic_context(repo_root, SIDE_TOOL_ROOT)
```

`load_successor_forensic_context` revalidates ET-C1/ET-C2, rebuilds the ET-C10
D11 manifest and graph in memory, and requires byte identity with the accepted
ET-C10 artifacts. Use it for the explicitly D11-scoped claim surface, including
`D11-C-CL-O-001` and `D11-G9-CL-N-001`.

`grcv4_explorer.forensic.load_forensic_context` remains available when the
question is explicitly historical: it exposes the accepted D10/ET-C2 snapshot
and correctly raises `KeyError` for D11 IDs. Choosing the historical loader is
an authority-boundary choice, not a package-version fallback.

For disposable scripts and output, use the ignored `tool/generated/`
directory. Do not write query output into `records/`, accepted decisions,
`src/`, `specs/`, or repository tests.

## Forensic API

The nine admitted query functions all return a canonical
`forensic_evidence_trace`.

The same nine functions accept either context. The successor context adds the
D11 claims, local debts, investigation candidates, selected profiles,
normative objects, equation contracts, and forward obligations without changing
the D10 classifications.

| Function | Input | Question answered |
| --- | --- | --- |
| `gate_act` | accepted record ID | What did this gate accept and what authority boundary did it set? |
| `gate_contribution` | accepted record ID | What did the gate add, inherit, supersede, or route? |
| `debt_lifecycle` | transformed debt ID | How did this debt transform, and was work routed forward? |
| `reconstruction_path` | current or historical claim ID | Which accepted records, contracts, and transformations support this claim? |
| `candidate_career` | candidate ID | How did a candidate's disposition change without treating routing as rejection? |
| `pruned_choices_at` | accepted record ID | Which alternatives and relabels were explicitly excluded at this gate? |
| `negative_claims` | no argument | Which negative claims and provenance locks are accepted? |
| `object_dependents` | normative object ID | Which contracts and graph objects depend on this parent object? |
| `contract_provenance` | equation-contract ID | Where did this contract come from, and under which support semantics? |

Known query IDs can be discovered without interpreting graph edges:

```python
def identifiers(kind: str) -> list[str]:
    return sorted(
        row["identifier"]
        for row in context.nodes.values()
        if row["kind"] == kind
    )

print(identifiers("current_claim"))
print(identifiers("debt_transformation"))
print(identifiers("gate_record"))
print(identifiers("candidate"))
print(identifiers("normative_object"))
print(identifiers("equation_contract"))
```

For the paper-propagation audit, typical source-exact D11 queries are:

```python
from grcv4_explorer.forensic import (
    contract_provenance,
    debt_lifecycle,
    reconstruction_path,
)

c_claim = reconstruction_path(context, "D11-C-CL-O-001")
g9_claim = reconstruction_path(context, "D11-G9-CL-N-001")
c_debt = debt_lifecycle(
    context, "D11-C-DEBT-BASELINE-TRANSPORT-AUTHORITY"
)
g9_contract = contract_provenance(
    context, "D11-G9-EC-EXACT-OLD-PORT-MAP"
)
```

The D11 debt traces deliberately return the preregistered opening, bounded
resolution, and still-forward verification rows separately. Do not compress
those rows into a claim that implementation conformance has been completed.

Use graph rows for ID discovery only. Prefer the typed functions for scientific
interpretation; direct ad hoc traversal can flatten support semantics or treat
annotations as causal edges.

## Complete Forensic Workflows

The canonical definitions and ownership of all 35 governed F/N/C/D/E scenarios
remain in the
[user-scenario contract](../GRCV4ExploratorySideToolUserScenarios.md). The
workflows below provide reusable executable API paths instead of repeating that
catalog.

The tracked walkthrough performs the complete operating path for every
forensic use case:

```bash
WALK=implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/docs/examples/agentic_query_walkthrough.py
.venv/bin/python "$WALK" all
```

For each operation it:

1. discovers the repository and side-tool roots;
2. loads and revalidates the accepted ET-C1/ET-C2 context;
3. executes one typed query with a known admitted ID;
4. validates output class, row count, trace digest presence, source references,
   and edge witnesses;
5. prints classifications rather than flattening them into one answer; and
6. writes a canonical trace under `tool/generated/agent-guide/`.

Run one workflow by replacing `all` with the name below.

### Use Case 1: What did a gate accept?

```bash
.venv/bin/python "$WALK" gate-act
```

The example queries `GRC9V4-CD-D7V2-v1` with `gate_act`. Open
`tool/generated/agent-guide/gate-act.json` and follow this path:

1. Confirm `operation == "gate_act"`.
2. Read `accepted_gate_act` for the gate-level act.
3. Read `accepted_authority` for the nested decision boundary.
4. Preserve the gate's `claim_ceiling` and `authorization_effect` when present.
5. Cite each row's `source_ref` and `edge_refs`.

Stop at the accepted act. Do not infer everything that later gates eventually
did from this query.

### Use Case 2: What did a gate add, inherit, supersede, or route?

```bash
.venv/bin/python "$WALK" gate-contribution
```

The output `gate-contribution.json` uses `gate_contribution` on the same D7-v2
gate. Group rows by their exact classifications: `added`, `inherited`,
`superseded`, and `routed`. Report all present classes. A routed row is not an
accepted addition and is not automatically a rejection.

Use this workflow with `gate_act`, not instead of it: one answers authority;
the other answers the gate's relationship to prior and future content.

### Use Case 3: How did a debt change?

```bash
.venv/bin/python "$WALK" debt-lifecycle
```

The example traces
`GTRS-COMP-DEBT-MATCHED-RUNTIME-DISCRIMINATION`. In
`debt-lifecycle.json`:

1. Read the debt row's transformation classification.
2. Retain predecessor and successor claim IDs from the payload.
3. If a `forward_verification_routing` row is present, report it separately.
4. Do not count the forward obligation as evidence supporting the current
   claim.
5. State whether the debt was resolved, narrowed, split, replaced, negatively
   resolved, or routed; do not reduce every transformation to "closed".

### Use Case 4: Why is a claim currently supportable?

```bash
.venv/bin/python "$WALK" reconstruction-path
```

The example reconstructs `D10-CL-N-001`. In `reconstruction-path.json`:

1. Confirm `accepted_backward_reconstruction`.
2. Read the start claim node from the payload.
3. Inspect the accepted nodes and support edges in the row.
4. Confirm `verification_obligations_excluded == true`.
5. Follow source references to the accepted records if a claim summary needs
   more context.

The reconstruction is a support path, not a proof-ranking score. Node or edge
count does not establish stronger evidence.

### Use Case 5: What happened to a candidate?

```bash
.venv/bin/python "$WALK" candidate-career
```

The example follows `V4-B-independent-derived-carrier`. Read
`candidate-career.json` in source-record order while preserving every row's
classification. The terminal result includes routed and
`current_tranche_closed_missing_constitutive_derivation` states; it does not
authorize the label `rejected`. The `parallel_realization_branches` row also
states that branches are not ranked.

To query A or C programmatically, change only the candidate ID passed to
`candidate_career`; do not generalize Candidate A's explicit D10.2 hardening
projection into a rule for every candidate.

### Use Case 6: Which choices were explicitly pruned at a gate?

```bash
.venv/bin/python "$WALK" pruned-choices
```

The D1 example writes `pruned-choices.json`. Separate:

- `pruned_alternative` rows;
- `blocked_relabel` rows; and
- the `resolved_negative_uninstantiated_slot` row for V4-D.

These are source-recorded exclusions. Do not generate additional alternatives
from absent graph branches or reinterpret V4-D as an implemented candidate.

### Use Case 7: Which negative claims and locks are accepted?

```bash
.venv/bin/python "$WALK" negative-claims
```

`negative-claims.json` contains `resolved_negative` claim rows and
`conditioned` D10.2 provenance-hardening rows. Report the machine value and
source key for a hardening lock. A readable paraphrase may accompany it but may
not replace it.

This query does not mean all non-normative possibilities are disproved. It
returns only accepted negatives and exact provenance locks.

### Use Case 8: What depends on a normative parent object?

```bash
.venv/bin/python "$WALK" object-dependents
```

The example queries `CORE-C-AUTHORITY`. In `object-dependents.json`:

1. Read `direct_contract_nodes` for immediate contract children.
2. Read `dependent_nodes` for the bounded exact graph relation.
3. Retain the source object and edge witnesses.
4. Preserve `dependency_reach_is_not_importance_or_ranking == true`.

Use the result to locate contracts, not to score the parent object's scientific
importance.

### Use Case 9: Where did an equation contract come from?

```bash
.venv/bin/python "$WALK" contract-provenance
```

The example queries `D10.2-EC-PARENT-CORE-C-AUTHORITY`. In
`contract-provenance.json`:

1. Read the source record and JSON pointer from `source_ref`.
2. Read the contract node and admitted scopes from the payload.
3. Preserve `accepted_claim_support_semantics` exactly.
4. If `support_disposition` is `indeterminate_requires_review`, report that
   boundary instead of choosing a stronger semantic.

The parent object and contract are different graph layers; do not collapse the
contract into its parent object's label.

## Programmatic Query Recipes

### Reconstruct an accepted claim

```python
from grcv4_explorer.forensic import reconstruction_path

trace = reconstruction_path(context, "D10-CL-N-001")
print(trace["operation"], trace["row_count"], trace["trace_digest"])
for row in trace["rows"]:
    print(row["classification"])
    print(row["source_ref"]["record_id"])
    print(row["source_ref"]["source_json_pointer"])
```

The reconstruction deliberately excludes forward-only verification
obligations.

### Compare a gate act with its contribution

```python
from grcv4_explorer.forensic import gate_act, gate_contribution

record_id = "GRC9V4-CD-D7V2-v1"
act = gate_act(context, record_id)
contribution = gate_contribution(context, record_id)

print([row["classification"] for row in act["rows"]])
print([row["classification"] for row in contribution["rows"]])
```

The first query reports accepted authority. The second separates added,
inherited, superseded, and routed content.

### Trace debt and candidate histories

```python
from grcv4_explorer.forensic import candidate_career, debt_lifecycle

debt = debt_lifecycle(
    context,
    "GTRS-COMP-DEBT-MATCHED-RUNTIME-DISCRIMINATION",
)
candidate = candidate_career(context, "V4-B-independent-derived-carrier")

print([row["classification"] for row in debt["rows"]])
print([row["classification"] for row in candidate["rows"]])
```

Do not map `routed` to `rejected`. Candidate B is the main control for that
mistake.

### Inspect a parent object and one contract

```python
from grcv4_explorer.forensic import contract_provenance, object_dependents

parent = object_dependents(context, "CORE-C-AUTHORITY")
contract = contract_provenance(
    context,
    "D10.2-EC-PARENT-CORE-C-AUTHORITY",
)

print(parent["rows"][0]["payload"]["direct_contract_nodes"])
print(contract["rows"][0]["payload"]["support_disposition"])
```

Dependency reach is not an importance, priority, or ranking score.

### Write a canonical trace

```python
from grcv4_explorer.forensic import negative_claims, write_trace

trace = negative_claims(context)
write_trace(
    TOOL_ROOT / "generated/agent-queries/negative-claims.json",
    trace,
)
```

`write_trace` accepts only a valid forensic trace with a matching digest.

## Use Case 10: Evaluate A Bounded Structural Counterfactual

Counterfactuals are typed qualitative mutations over accepted structure. They
are not parameter simulation and may not contain numerical effect claims.

```python
from grcv4_explorer.counterfactual import (
    evaluate_mutation,
    load_counterfactual_context,
    make_mutation,
)

cf_context = load_counterfactual_context(repo_root, SIDE_TOOL_ROOT)
mutation = make_mutation(
    cf_context,
    target_id="D10.2-EC-CI-A-CONTRACTION",
    target_kind="equation_contract",
    mutation_type="remove_term",
    baseline_record_id="GRC9V4-CD-D10.2-v1",
    profile_scope=["A_CI"],
    candidate_scope=["V4-A-temporalized-W"],
    realization_scope=["comparison:A-CI"],
    declared_payload={"term_id": "bounded_contraction_condition"},
)
result = evaluate_mutation(cf_context, mutation)

print(result["result_statuses"])
print(result["result_digest"])
```

Complete the path as follows:

1. Load `load_counterfactual_context`; this revalidates ET-C3 plus ET-C1/ET-C2.
2. Create the mutation only with `make_mutation`, which adds the baseline digest
   and validates the closed schema.
3. Run `evaluate_mutation`.
4. Read `result_statuses` before inspecting consequences.
5. Separate `claims_invalidated`, `debts_reactivated`, `routes_changed`,
   `blocked_overreads_at_risk`, and `verification_obligations_at_risk` in the
   structural result.
6. Report `earliest_gates_to_reopen` and
   `unknown_beyond_evidence_frontier` as stopping boundaries.
7. Preserve the mutation, source/graph digests, claim boundary, and
   `result_digest` with any summary.

If the result contains `invalid_mutation`, report its `invalid_reason` and stop.
Do not repair the request by widening scope or changing the baseline.

Admitted mutation kinds are `remove_term`, `replace_operator`,
`change_authority`, `change_stage`, `change_normalization`,
`change_profile_parameterization`, `add_derivation`, `remove_derivation`, and
`change_candidate_disposition`. Each has a closed target-kind and payload
schema. Unknown fields, stale baselines, scope leakage, arbitrary numeric
payloads, and unsupported targets fail closed.

The stronger browser workflows use precompiled ET-C5 scenario/ripple rows.
Agents should prefer those rows when an equivalent scenario already exists;
do not compile an alternate consequence and present it as accepted playback.

## Use Case 11: Detect New Or Changed Source

Run the observational command before a new research session:

```bash
.venv/bin/python "$TOOL/scripts/run.py" discover-sources
```

Then:

1. Read `source_observation_state` from the terminal.
2. Preserve the observation digest and generated
   `tool/generated/source-observation.json`.
3. Continue normally only for `current_bundle_exact`.
4. For `new_unprocessed_source_available`, report the new paths but do not load
   them as authority.
5. For changed, missing, or unreadable admitted source, stop forensic use and
   report that readmission or repair is required.

The required successor path is schema/authority classification, adapter update
or addition, successor bundle admission, graph/reference conformance, complete
derived rebuild, audit, and human acceptance. Discovery alone performs none of
those actions.

## Use Case 12: Execute And Consume The Forensic Notebook

The accepted notebook surface is
[forensic_recipes.ipynb](../tool/notebooks/forensic_recipes.ipynb). It is a
two-recipe orchestration layer over the pure forensic API, not a second parser,
graph kernel, or scientific authority.

Run the governed path:

```bash
.venv/bin/python "$TOOL/scripts/run.py" discover-sources
.venv/bin/python "$TOOL/scripts/run.py" notebook-iteration3
```

The runner revalidates the source context, supplies `repo_root`,
`side_tool_root`, and `output_dir` to the notebook cells, executes them without
a Jupyter dependency, and rejects any write outside the generated-output
envelope. It emits:

```text
tool/generated/iteration3-notebook/normative-claim.json
tool/generated/iteration3-notebook/candidate-B.json
```

Consume the outputs canonically:

```python
from grcv4_explorer.canonical import load_json_object

claim_trace = load_json_object(
    TOOL_ROOT / "generated/iteration3-notebook/normative-claim.json"
)
candidate_trace = load_json_object(
    TOOL_ROOT / "generated/iteration3-notebook/candidate-B.json"
)

assert claim_trace["output_class"] == "forensic_evidence_trace"
assert candidate_trace["output_class"] == "forensic_evidence_trace"
print(claim_trace["trace_digest"])
print(candidate_trace["trace_digest"])
```

The first trace reconstructs `D10-CL-N-001`; the second follows
`V4-B-independent-derived-carrier`. Preserve every row's classification,
`source_ref`, `edge_refs`, and trace digest. Cross-check either identifier in
the ET-C8 browser when a human-readable presentation is useful.

Do not execute the tracked notebook directly under arbitrary or global
Jupyter. Jupyter is not a current locked dependency, and direct execution would
omit the governed namespace and output-envelope checks. For additional
programmatic queries, use the tracked walkthrough or a disposable script under
`tool/generated/`. No second counterfactual-authoring notebook is currently
admitted; the governed Python API owns counterfactual authoring, and ET-C5 owns
the canonical scenario round-trip used by notebook/Python and browser surfaces.

### D11 API, notebook, and browser UX

ET-C11 adds a separate D11 forensic notebook and a read-only browser projection
without changing the historical ET-C3 notebook. Run the notebook with:

```bash
.venv/bin/python "$TOOL/scripts/run.py" notebook-iteration11-d11
```

It emits six D11-C/D11-G9 claim, debt, and contract traces under
`tool/generated/iteration11-notebook/`. The runner compares every file
canonically with the direct successor API output and browser payload.

For interactive inspection, run:

```bash
.venv/bin/python "$TOOL/scripts/run.py" serve-iteration11-d11
```

Select **D11**, then filter by investigation and authority kind or search an
identifier. The browser shows precomputed API rows, exact source references,
support edges, and output digests. Profile and verification-obligation entries
use source-bound graph projections because the forensic API has no dedicated
operation for those two kinds. Do not describe those projections as new API
claims or scientific inference.

See [D11UXGuide.md](./D11UXGuide.md) for commands and surface behavior.


## Reading A Trace Safely

Every forensic trace contains:

```text
operation
query
source_bundle_digest
graph_digest
ET_C2_record_digest
authority_extension_digest  # present for the ET-C10 successor context
row_count
rows[]
trace_digest
```

Each row contains a `classification`, payload, exact `source_ref`, and
`edge_refs`. Preserve these fields when extracting an answer. A useful agent
response distinguishes:

```text
accepted source statement
source location and identity
support semantic
bounded interpretation
open verification or evidence frontier
```

Never infer ranking from counts, dependency reach, row order, visibility, or
graph position.

## Failure Handling

- `KeyError`: the requested ID is absent or ambiguous in the admitted graph.
- `SourceAdmissionError`: accepted source identity or schema admission failed.
- `GraphInvariantError`: the graph no longer satisfies its accepted contract.
- `MutationValidationError`: a mutation request is outside the closed algebra.
- `invalid_mutation` result: evaluation rejected a supplied mutation without
  changing source state.
- `new_unprocessed_source_available` from the historical ET-C0 discovery:
  consult the ET-C10 contract before concluding that the record is unadmitted.
  The eight hash-bound D11 records are admitted only through ET-C10; any other
  added record still requires a successor processing cycle.

The safe fallback is to report the boundary and exact failed query. Do not
repair source records, broaden scopes, or substitute a semantically similar ID.

## Reproducibility

Before relying on a batch of answers, run:

```bash
.venv/bin/python "$TOOL/scripts/run.py" verify-iteration9
```

The verification entry point preserves the accepted ET-C9 historical closeout,
independently rebuilds the accepted ET-C10 D11 overlay, then rebuilds and tests
the ET-C11 API/notebook/browser candidate. It runs desktop/mobile D11 browser
pressure alongside historical regressions and checks the active post-D11
paper-propagation boundary. It does not promote a scientific claim or treat
pending paper/specification/runtime work as evidence.

## Tranche 8 implementation evidence (not claim authority)

For 8.1 mechanics, 8.2 allocation, all ten bounded 8.3 integrations and current
8.4 acceptance/coverage, use the [Tranche 8 API, CLI, notebook and browser](./Tranche8EvidenceGuide.md).
Its retained traces preserve classification and provenance, but the projection
is not a new forensic trace or scientific claim. Continue using the typed
contract/debt/object queries above for claim investigation.

### P9-8.5 selected lifecycle evidence

Use `tranche8_status(repo_root, family="C_OS", checkpoint="8.5")`, or
`tranche8_evidence.py status --family C_OS --checkpoint 8.5`. The browser has a
**Check 8.5 lifecycle** action with a C_OS/C_CI/A_CI/A_PC selector; the
verification notebook exposes the same four selected queries.
This authenticates retained execution/source bytes and scope, without running
numerics. Families outside this first group fail closed until their own records exist. Read indexed
sources through `tranche8_source` with the same selection.

The internal event checkpoint and generic step/reset snapshot have an explicit
seed link and separate ledgers. Do not call them a unified public GRC9V4 snapshot.
Exact OS split rejection and Arb256 `CertificationInconclusive` are different
outcomes; both rollback checks pass, without automatic fallback. This evidence
grants no scientific claim, public profile support, G2/G3 or aggregate closure.

All four first-group 8.5 families are user-accepted on 2026-10-26.
`first_group_closed=true` is separate from all-ten `aggregate_closed=false`. The
C_OS lifecycle source is the original hash-verified Git blob at `5b8a432e`,
returned by indexed source retrieval. Its acceptance is not a claim about
current-code conformance. C_CI/A_CI/A_PC bind the current integration source.

The A-family manifests also bind an imported maintenance-policy module. Its
original bytes are retained in `P9-8.5-ExecutionMaintenancePolicy.py.txt`, with
the original digest verified before projection. `execution_metadata_sources`
explicitly maps that source to the indexed snapshot; current numerical/runtime
source checks are not waived. Each selected API check runs in an isolated
metadata worker so historical adapters cannot affect parallel family queries.

### P9-8.6 bounded conformance decision

Use `tranche8_status(repo_root, family="first_group", checkpoint="8.6")`, or
select C_OS, C_CI, A_CI or A_PC. The **Check 8.6 conformance** browser selector
and notebook use the same retained endpoint. The result is bounded conformance
accepted for the first group; all-ten closure remains false. Source hashes,
exact subjects, numerical limits and accepted lifecycle predecessors are checked;
no native trajectories or independent numerical proofs are rerun. For indexed
sources with multiple historical revisions, select an individual family rather
than an ambiguous first-group source. The historical 8.4i/8.5 views keep their
own decisions; 8.6 neither rewrites those nor grants public support.

The first-group 8.6 projection includes the separate user acceptance dated
2026-10-27. The original decision retains its pre-acceptance flags; the outer
projection is accepted only against the pinned acceptance record.

### Final Tranche 8 first-group reviews

`from grcv4_explorer.tranche8_end import tranche8_end_reviews, tranche8_end_source`

Call `tranche8_end_reviews(repo_root)` or use **Check final reviews** in the
browser and the final notebook cell. The API authenticates pinned mechanism
and performance records plus their sources without numerical execution.
`tranche8_end_source(repo_root, path)` serves only a listed repository-relative
source. The final reviews are accepted, closing bounded first-group Tranche 8 on
2026-10-27; the projection includes their pinned acceptance separately from 8.6. Smaller C_CI path discrimination does not remove the large-run
resolution limit, and A_PC ratios do not grant a robust parameter neighborhood.


### Tranche 9 first-group lifecycle evidence

`from grcv4_explorer.tranche9 import tranche9_status, tranche9_source` exposes
P9-9.1b for C_OS, C_CI, A_CI and A_PC. Use `tranche9_status(repo_root)` for
retained integrity and `tranche9_source(repo_root, indexed_path)` for exact
repository-relative sources. `/api/tranche9` and the Phase 9 browser/notebook
provide the same view. These queries do not rerun kernels, grant acceptance,
or settle the sixteen pending disabled-compatibility cells. For scientific
authority continue using the typed forensic API and its support dispositions.

### P9-9.2 disabled compatibility

Use `grcv4_explorer.tranche9.tranche9_compatibility_status(repo_root)` or
`GET /api/tranche9/compatibility` for all forty cells: sixteen native delegate
results bounded acceptance recorded, twenty-four unselected. Sources are accessible
through `tranche9_compatibility_source` / `/api/tranche9/compatibility/source`.
These checks authenticate retained evidence without rerunning native execution.
Explicit disabled seeds do not establish an enabled/disabled crossing; that
work remains P9-9.4. The browser and verification notebook expose the same scope.

### P9-9.3 matrix reconciliation

The existing `tranche9_compatibility_status(repo_root)` and
`/api/tranche9/compatibility` now also check `P9-9.3-Matrix.json` against the
frozen catalog/spec and 9.2 acceptance. `matrix_reconciliation` reports the
separate 9.3 disposition: passing reconciliation, user-accepted on 2026-10-27,
no native execution. All forty cells remain visible. Its matrix/review are
indexed sources. This does not grant branch crossings or public runtime support.


### P9-9.4a branch crossings

Use `grcv4_explorer.tranche9.tranche9_crossing_status(repo_root)` or
`GET /api/tranche9/crossings` for four actual same-graph entry/return executions.
`tranche9_crossing_source` and `/api/tranche9/crossings/source` serve indexed
repository-relative evidence. Browser and notebook expose the same view.
Integrity checks do not execute kernels, confer acceptance, or deliver the
public runtime API planned for P9-9.4b. The negative native timestep excludes
C_CI at return admission and the other three at their next enabled step.

### P9-9.4b public runtime integration

`grcv4_explorer.tranche9.tranche9_public_status(repo_root)` and
`GET /api/tranche9/public` authenticate four native public family suites, shared
boundary checks and the all-ten contract suite. Indexed `/source?path=...` downloads retain content hashes.
The browser **Check ten-family contracts / four-family execution** and notebook use the same
projection. This is retained-integrity verification, not a native rerun or a
G3/full-conformance grant. Runtime usage/reproduction is in
`implementation/phase-9-grcv4/tranche-9/P9-9.4b-Review.md`.

For P9-9.4b, `contract_matrix` describes all ten existing candidate/realization
schemas and their authority fields; `families` remains the four-family native
execution scope. The extra `contracts` evidence group validates all ten data
contracts without executing the six unselected native lifecycles. Do not infer
native conformance from configuration round trips or contract discovery.

The `architecture` projection authenticates nine tests for execution selection,
transition/artifact transfer, dispatch, sole branch ownership, rollback, and
accepted mixed/crossing checkpoint parity. Its
`replay_assessment` is one small three-action case, not a scaling benchmark.
The source index includes `P9-9.4b-Architecture.md`, which records the possible
consolidation of standalone and branch checkpoint formats after all ten
families are fully enabled.


## P9-9.5 public legacy conflict evidence

`grcv4_explorer.tranche9.tranche9_conflict_status(repo_root)` authenticates the
four C_OS/C_CI/A_CI/A_PC public refusal records; `tranche9_conflict_source` reads
only their indexed repository-relative sources. `/api/tranche9/conflict`, its
`/source?path=...` route, the browser control and notebook expose the same view.
These checks run no native trajectories. A passing test means the undefined
legacy expansion was rejected with full rollback, not that an event committed.
Bounded user acceptance is recorded on 2026-10-28; its pinned decision is
separate from original execution flags. P9-9.6 support review remains separate. The trace for
`D11-G9-EC-LEGACY-DEFINED-DOMAIN` retains its bounded compatibility authority.

## P9-9.6 bounded support reconciliation

`grcv4_explorer.tranche9.tranche9_support_status(repo_root)` authenticates the
accepted Tranche 8/9 evidence and exact source/expanded-target identities for
C_OS/C_CI/A_CI/A_PC. `tranche9_support_source` serves only indexed, hash-checked
repository-relative sources. `/api/tranche9/support`, its `/source?path=...`
route, the browser control and notebook expose the same review without native
execution. The verdict is bounded evidence reconciled, full conformance held;
bounded user acceptance is recorded on 2026-10-28 through a separate pinned
decision, preserving the original review flags. Next: P9-10.1a/b/c.

The sixteen accepted disabled cells apply to their exact source identities;
expanded targets have enabled evidence and no corresponding disabled-cell grant.
The required public `basin_attributes` / `basin_identity` surface is missing;
this is separate from optional completed sparks/hierarchy. The frozen umbrella
compatibility capability requires all forty vectors, while twenty-four remain
unselected. These three items are routed to P9-10.1. A successful integrity check
does not remove them, promote D10.2 indeterminate traces or grant full conformance.

## P9-10.1a accepted baseline basin diagnostic authority

The [spark-completion research opening](../../../decisions/SparkCompletionDefinitionAndFeasibility.md)
(2026-10-31) consumes this accepted context without extending it. Its new
provisional claims/debts live in the linked research ledger, not in the accepted
query graph. Reproduce its five typed provenance/debt queries and small exact
screen with `scripts/check_spark_completion_feasibility.py --check` from the
investigation, using the full repository-relative script path from the repository
root. Do not interpret the baseline basin ceiling as completion authority or
reopen the resolved diagnostic-design debt. New completion authority and its
API/browser/notebook exposure require consolidated scientific adjudication and
explicit successor admission, propagation and applicable conformance.

The [SC-1 candidate](../../../decisions/SparkCompletionSC1Contract.md) adds
sixteen continuity/staging, completion/row, basin/seed and A/C constitutive
authority queries, with
exact pressure through `scripts/check_spark_completion_sc1.py --check`.
The proposed geometric-basin identity rule, spatial-attraction lemma and
conditional full-state completion theorem remain outside the accepted graph.
The successor ledger records the supplied SC-1 definition without closing debts
or treating a CI solver contraction as contraction of the ordinary state update.
The [SC-1 adjudication](../../../decisions/SparkCompletionSC1Adjudication.md)
subsequently selects this bounded scientific definition and conditional A.7 bridge.
Its [successor ledger](../../../evidence/spark-completion/SC1Adjudication.json)
resolves only the organization-definition portion; the prior ledger/evidence
remain unchanged. Reproduce its bindings and scope with
`scripts/check_spark_completion_sc1_adjudication.py --check` (use the full
repository-relative path from the root). These IDs are local research decisions,
not accepted query-graph nodes. SC-3 must perform the authority/schema successor
admission; do not publish new completion support through API/browser/notebook
from this selection alone.
The [SC-1 pressure resolution](../../../decisions/SparkCompletionSC1EquilibriumExclusion.md)
records the conditional mathematical pass and the scoped equilibrium exclusion.
Its 112 retained-declaration checks are not native reruns; proposed exclusion
claims are not accepted graph nodes. Mathematical review does not grant
completion support or invalidate prior finite-horizon mechanical evidence.

The [SC-2 mechanism proposal](../../../decisions/SparkCompletionSC2MechanismAnalysis.md)
and `scripts/check_spark_completion_sc2.py --check` trace the existing potential,
geometry, Read-Back and staging contracts. The homogeneous nonlinear site
binding, equilibrium and local-return claims remain proposed research, not
queryable accepted nodes or enabled native evaluators. Do not promote the
existing equation's site-potential parameter into arbitrary evaluator authority.
The [SC-2 review](../../../evidence/spark-completion/review/SC2ScientificPressureReview.md)
passes the conditional mathematics; it does not admit the binding. Local checks
reproduce 120 stable branch boxes and a no-basin control, while the review's
physical-box escape remains an attributed result without a local execution
package. Source/event reachability and completion debts remain open.
The [SC-2 event preflight](../../../decisions/SparkCompletionSC2EventCompatibility.md)
adds nine typed source queries plus exact parent/port/charge checks on both
chiral D11 targets. Use `scripts/check_spark_completion_event_preflight.py --check`.
Its local claims remain proposed and outside the accepted graph. Allocation-kernel
execution and conditional target equilibrium bounds are not a committed event,
constitutive admission or organized-branch entry. The D10.2 provenance remains
indeterminate; the D11 mechanics retain their accepted bounded support.
The [SC-2 continuation successor](../../../decisions/SparkCompletionSC2Continuation.md)
and [record](../../../evidence/spark-completion/SC2Continuation.json) retain the
original strict-split exclusion and one declared mobility/duration companion.
Its 128 enclosed exact-equation steps per role have no organizing gain in either
chiral chart. `scripts/check_spark_completion_continuation.py --check` recomputes
that bounded evidence and source bindings. Its local claim handles are research
only, not newly queryable accepted nodes. SC-1 stays closed; no completion debt,
site binding, native support or G4 gate is closed by this result.
The [constructive successor](../../../decisions/SparkCompletionSC2PositiveCandidate.md)
adds positive exact-equation target entry and a quantitative full-map trap for
a declared charge-21 preparation. Local handles `SC2-CL-C-POSITIVE-D11-ENTRY`
and `SC2-CL-C-FULL-OS-TRAP` remain conditional research outside the accepted
graph. Its compressed record distinguishes the checked target result from the
open ordinary-beat/fresh-source link and downstream native numerical/lifecycle
work. `scripts/check_spark_completion_positive.py --check` recomputes allocation
and trapping math; `--rerun` additionally replays the enclosed trajectories.
The [ordinary-source successor](../../../decisions/SparkCompletionSC2SourceBeat.md)
now establishes that formerly open source link: one exact ordinary beat, fresh
capture, unchanged reset, actual current transfer and organized trap entry.
Use `scripts/check_spark_completion_source_beat.py --check` for exact source
recomputation/bindings, or `--rerun` for the changed current-target path as well.
Its four forensic traces retain their existing authority dispositions. Local
handles `SC2-CL-C-ORDINARY-SOURCE-LINK` and `SC2-CL-C-SOURCE-EVENT-TRAP-CHAIN`
are conditional research ready for adjudication, not accepted graph additions
or native completion support. No debt is silently closed by the execution record.
The [independent target review](../../../evidence/spark-completion/review/SC2PositiveScientificPressureReview.md)
passes the predecessor's target mathematics, not the later source-chain adjudication.
Both fast checkers now recompute entry distance from saved coordinates and fresh
metric, check complete checkpoint basins, and require both chart keys at every
observation. These retained-consistency checks do not replay the long recurrence;
use `--rerun` for that. Local research claims retain their existing status.
The [complete witness](../../../decisions/SparkCompletionSC2CompleteWitness.md)
adds a two-beat enclosed current window and an event-bound research completion
decision: one new stable child, local gain one, no additional replay gain.
`scripts/check_spark_completion_complete.py --check` executes that short window
and its composition controls while reusing the bound long approach/reset.
`SC2-CL-C-EXACT-SPARK-COMPLETION` and its scientific debt progress are recorded in
`evidence/spark-completion/SC2CompleteWitness.json`; they are local conditional
research, not accepted forensic nodes or native completed-spark support.

Use the explicit basin successor context. It preserves the pre-basin and ATC
loaders and their historical pins; it does not silently enlarge those views.
The accepted source is in the separately inventoried `decisions/p9-basin-interface/`
collection. Unexpected JSON there, changed source/design/acceptance or a changed
admission fails closed.

```python
from grcv4_explorer.basin import load_basin_forensic_context, basin_authority
from grcv4_explorer.forensic import contract_provenance, debt_lifecycle
context = load_basin_forensic_context(repo_root, side_tool_root)
contract_provenance(context, "P9-EC-GRC9-BASIN-MEMBERSHIP")
debt_lifecycle(context, "P9-10.1a-DEBT-BASIN-IDENTITY")
basin_authority(repo_root, side_tool_root)
```

`P9-10.1a-CL-N-BASIN-001` is normative bounded diagnostic authority. The design debt
is resolved; this historical design context retains `P9-10.1a-VO-BASIN-NATIVE`
as pending at design acceptance. The native acceptance successor below resolves
it for the four families; it is never backward scientific support. `GRC_basin_identity` remains an unresolved historical premise
reference: the new producer is explicit successor authority, not its retroactive
resolution. D10/D11 support dispositions are preserved.

The actual `/api/basin` endpoint, Phase 9 browser's **baseline basin authority**
panel and notebook `basin-authority` cell expose the same checked traces. Source
links use `/api/basin/source?path=...` and only the indexed relative paths. Failed
loads clear stale results. The [spec/schema successor](../../../../../../specs/grc-9-v4-basin-interface.md)
and proposal/paper A.5.1 are propagated; no native capability is granted.

The original review checker `--check` addresses the pre-propagation Git subject
`1275bd1f`. Use the current `verify_p9101a_propagation.py --check` for source-chain
integrity; graph-rule tests remain directly runnable through unittest. Do not
relabel the original source audit as a current-source audit after propagation.

### Native basin implementation evidence

```python
from grcv4_explorer.basin_native import basin_native_status, basin_native_source
view = basin_native_status(repo_root)
raw, ref = basin_native_source(repo_root, view["records"][0]["path"])
```

This is a separate native execution projection. `check_mode` explicitly means
retained integrity and independent classification recomputation, not a native numerical
rerun. `original_tests_run` and `pressure_tests_run` separate the earlier native
checks from saved-state/equation/row/lifecycle pressure. Records above 1 MB use XZ;
`basin_native_source` returns their checked compressed bytes for `lzma.decompress`.
The records include fresh current/reset
operands and exact source hashes. `/api/basin/native`, its `/source` route, the
browser native-evidence button and notebook `basin-native` cell expose it.
P9-10.1a is bounded accepted. `view["verification_obligation_resolution"]`
exposes the checked `resolved_bounded_native` disposition and its exact source
for `P9-10.1a-VO-BASIN-NATIVE`; `view["acceptance"]` binds the user decision.
The original design context and execution records retain their historical flags.
P9-10.1b/c remain open. Do not infer support promotion, all-ten execution,
completed sparks or attracting basins from a passing native record.


## P9-10.4 public example publication

Use `grcv4_explorer.tranche10_examples.tranche10_examples_status(repo_root)` or
`GET /api/tranche10/examples` to inspect the exact all-ten tutorial run roster,
guide and output references. The browser's **P9-10.4 — learn GRC9V4** panel and
notebook cell `p9104-examples` expose the guide and code without executing
trajectories. The source endpoint accepts only the publication's indexed paths.

Start at `examples/grc9v4/README.md` for positive evolution, family-specific
histories, seeds/sparks, basin observations, native expansion and lifecycle.
This is example evidence, not additional normative claim authority, an automatic
ATC scheduler, completed-spark support or a G4 decision. Use the existing forensic
claim surfaces for scientific authority; do not infer it from tutorial success.

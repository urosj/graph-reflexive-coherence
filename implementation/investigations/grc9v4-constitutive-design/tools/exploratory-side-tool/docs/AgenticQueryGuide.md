# Agentic Query Guide

This guide describes how an automated research agent can query the accepted
GRCv4 exploratory side-tool API. The API is a local Python interface, not an
HTTP service. It reconstructs accepted evidence and evaluates a closed set of
structural counterfactuals; it does not create scientific evidence or predict a
gate that has not been rerun.

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

`discover-sources` is the historical ET-C0 observation command. After accepted
D11 it deliberately continues to report those records as unprocessed relative
to ET-C0; ET-C0 is not rewritten. D11 admission is instead verified through:

```bash
.venv/bin/python "$TOOL/scripts/run.py" audit-iteration10-d11
.venv/bin/python "$TOOL/scripts/run.py" test-iteration10-d11
```

Any record outside both the ET-C0 inventory and the ET-C10 D11 contract still
requires a new successor adapter/readmission cycle.

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
ET-C10 artifacts. Use it for the current claim surface, including
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

"""C_OS capacity-boundary targets and bounded native continuation.

Reuses accepted numerical comparators, not an ATC law or rigorous error tube.
Only --run executes native trajectories. --check recomputes dense expectations
and captured-consumer consistency; status() checks pinned retained structure.
"""

import argparse
from copy import deepcopy
import json
from fractions import Fraction
from importlib.metadata import version
import platform

import p984b_runtime as base
import p984b_cos_successor as consumer
import prepare_p984c_boundaries as boundary
from tests.models.test_grc_9_v4_expansion import independent_tree

SELF = base.HERE + "p984c_cos.py"
TEST = base.HERE + "test_p984c_cos.py"
INPUTS = base.BASE + "P9-8.4c-COSCases.json"
RESULTS = base.BASE + "P9-8.4c-COSResults.json"
REVIEW = base.BASE + "P9-8.4c-COSReview.md"


def target_oracle(source, template, request, layout):
    """Literal chart/tree oracle; no production expansion plan or allocator."""
    identity = deepcopy(template["oracle"]["event_identity"])
    for field in ("target_effective_degree", "module_chirality", "growth_phase"):
        identity[field] = request[field]
    identity["canonical_module_node_count"] = layout["expected"]["module_nodes"]
    event = "grc-event-sha256:" + base.digest(identity)
    graph = deepcopy(source["inputs"]["reference"]["graph"])
    old = request["source_node_id"]
    for edge in graph["edges"]:
        for side in ("tail", "head"):
            endpoint = edge[side]
            if endpoint["node_id"] == old:
                endpoint["node_id"] = event + f"/satellite/{(endpoint['port'] - 1) % 3 + 1}"
    nodes = {n for n in graph["live_node_ids"] if n != old}
    for name, tail, head, port in independent_tree(tuple(layout["expected"]["branch_extras"]), layout["chirality"]):
        nodes.update((event + "/" + tail, event + "/" + head))
        graph["edges"].append(dict(edge_id=event + "/" + name,
            kind="tree" if "/extra/" in name else "spine",
            tail=dict(node_id=event + "/" + tail, port=port),
            head=dict(node_id=event + "/" + head, port=port)))
    graph["live_node_ids"] = sorted(nodes, key=lambda n: (isinstance(n, str), base.canonical_json_bytes(n)))
    graph["edges"].sort(key=lambda e: e["edge_id"].encode("utf-16-be"))
    return dict(event_identity=identity, event_id=event, target_graph=graph)


def make_manifest():
    contract = base.read(boundary.OUTPUT)
    old = base.read(base.INPUTS)
    base.check_bindings(old["source_bindings"])
    family = next(f for f in contract["families"] if f["family"] == "C_OS")
    cases, reuse = [], []
    for layout in contract["layouts"]:
        template = next(c for c in old["cases"] if
            (c["request"]["target_effective_degree"], c["request"]["module_chirality"], c["request"]["growth_phase"])
            == (45 if layout["degree"] == 45 else 31, layout["chirality"], layout["phase"]))
        case = deepcopy(template)
        case.update(case_id=layout["id"] + "::C_OS", fixture_id=layout["id"],
            coverage_binding=dict(record_digest=contract["record_digest"],
                cell_ids=[layout["id"] + "::C_OS::" + r for r in boundary.ROLES]),
            comparison=family["comparison"], execution_budget_seconds=family["execution_budget_seconds"])
        case["request"]["target_effective_degree"] = layout["degree"]
        if layout["degree"] != 45:
            case["request"]["operation_id"] = "p984c-cos-" + layout["id"]
        case["oracle"] = target_oracle(old["expected_source"], template, case["request"], layout)
        # D45 uses precisely the accepted source/request/graph/reference/schedule,
        # not a normalized isomorphism or merely an equal module-node count.
        if layout["degree"] == 45:
            base.require(case["request"] == template["request"] and case["oracle"] == template["oracle"], "D45 is not exact reuse")
            reuse.append(dict(case_id=case["case_id"], previous_case_id=template["case_id"]))
        cases.append(case)
    paths = {r["path"] for r in old["source_bindings"]} | {
        SELF, TEST, consumer.SELF, boundary.OUTPUT, base.INPUTS, base.RESULTS,
        "tests/models/test_grc_9_v4_expansion.py"}
    return base.seal(dict(schema="p984c-cos-cases-v1", boundary_digest=contract["record_digest"],
        source_bindings=base.bind(sorted(paths)), initial_inputs=old["initial_inputs"],
        expected_source=old["expected_source"], cases=cases, exact_reuse=reuse,
        user_accepted=False, aggregate_closed=False))


def compact(value):
    """Store repeated reference/Hodge operands once, with exact round trip."""
    contexts = {}
    def visit(x):
        if isinstance(x, list):
            return [visit(v) for v in x]
        if not isinstance(x, dict):
            return x
        out = {}
        for k, v in x.items():
            if k in ("reference", "H1_form") and isinstance(v, (dict, list)):
                key = base.digest(v)
                contexts[key] = v
                out[k] = {"p984c_context": key}
            else:
                out[k] = visit(v)
        return out
    packed = visit(value)
    return dict(contexts=contexts, payload=packed)


def expand(value):
    contexts, used = value["contexts"], set()
    base.require(set(value) == {"contexts", "payload"}, "compact envelope fields")
    for key, item in contexts.items():
        base.require(base.digest(item) == key, "context digest drift")
    def visit(x):
        if isinstance(x, list):
            return [visit(v) for v in x]
        if not isinstance(x, dict):
            return x
        if "p984c_context" in x:
            base.require(set(x) == {"p984c_context"} and x["p984c_context"] in contexts, "unknown context")
            used.add(x["p984c_context"])
            return deepcopy(contexts[x["p984c_context"]])
        return {k: visit(v) for k, v in x.items()}
    out = visit(value["payload"])
    base.require(used == set(contexts), "unused retained context")
    return out


def reused(manifest):
    previous = base.read(base.RESULTS)
    rows = {r["case_id"]: r for r in previous["cases"]}
    return [dict(**link, previous_record_digest=previous["record_digest"],
        previous_row_digest=base.digest(rows[link["previous_case_id"]]),
        passed=rows[link["previous_case_id"]]["outcome"] == "passed_named_case")
        for link in manifest["exact_reuse"]]


def preflight(manifest):
    rows = []
    for case in manifest["cases"]:
        target = base.independent_target(manifest, case)
        source = base.GeometryStageInputs.from_payload(manifest["expected_source"]["inputs"])
        for role in boundary.ROLES:
            base.require(sum(map(Fraction, getattr(source, role).C)) == sum(map(Fraction, getattr(target, role).C)), "target charge map")
        rows.append(dict(case_id=case["case_id"], target_digest=base.digest(target.to_payload()),
            dense_screen=consumer.dense_preflight(target)))
    return rows


def status(manifest, record):
    """Cheap integrity view, explicitly neither dense nor native rerun."""
    base.check_digest(manifest)
    base.check_bindings(manifest["source_bindings"])
    base.require(manifest == make_manifest(), "changed boundary subjects/budgets")
    base.check_digest(record)
    base.require(record["schema"] == "p984c-cos-results-v1" and record["manifest_digest"] == manifest["record_digest"], "foreign results")
    base.require(record["user_accepted"] is False and record["aggregate_closed"] is False, "acceptance promotion")
    execution = expand(record["execution"])
    base.check_digest(execution)
    new = [c["case_id"] for c in manifest["cases"] if c["case_id"] not in {r["case_id"] for r in manifest["exact_reuse"]}]
    base.require(execution["requested_case_ids"] == new and [r["case_id"] for r in execution["cases"]] == new, "missing/extra/reordered cases")
    base.require(record["reuse"] == reused(manifest) and all(r["passed"] for r in record["reuse"]), "D45 reuse drift")
    base.require([r["case_id"] for r in record["preflight"]] == [c["case_id"] for c in manifest["cases"]], "preflight roster")
    for row in execution["cases"]:
        success = row["outcome"] == "passed_named_case"
        base.require(row["case_passed"] == success, "case/event conflation")
        if success:
            base.require(row["event_committed"] and row["first_failure"] is None and not row["unexecuted_dependent_stages"]
                and len(row["stages"]) == 16 and all(s["outcome"] == "passed_named_stage" for s in row["stages"]), "false successful case")
    return dict(family="C_OS", native_cases=len(new), passed_cases=sum(r["case_passed"] for r in execution["cases"]),
        exact_reuse_cases=len(record["reuse"]), accepted_cells=0,
        native_trajectories_rerun=False, dense_comparisons_rerun=False,
        cases=[{k: r[k] for k in ("case_id", "case_passed", "event_committed", "first_failure")} for r in execution["cases"]])


def check(manifest, record):
    summary = status(manifest, record)
    base.require(record["preflight"] == preflight(manifest), "preflight target or dense screen drift")
    execution = expand(record["execution"])
    base.validate_results(manifest, execution)
    cases = {c["case_id"]: c for c in manifest["cases"]}
    for row in execution["cases"]:
        if row["case_passed"]:
            consumer.check_consumption(row, manifest, cases[row["case_id"]])
    # Recheck the exact accepted D45 operands/results, without pretending that
    # historical evidence included successor consumer captures.
    old = base.read(base.INPUTS)
    previous = base.read(base.RESULTS)
    names = [r["previous_case_id"] for r in record["reuse"]]
    selected = base.seal(dict(previous, requested_case_ids=names,
        cases=[next(r for r in previous["cases"] if r["case_id"] == name) for name in names]))
    base.validate_results(old, selected)
    return {**summary, "dense_comparisons_rerun": True, "retained_integrity": "passed"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--prepare", action="store_true")
    group.add_argument("--run", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.prepare:
        base.write_new(INPUTS, make_manifest())
        print("C_OS boundary subjects prepared; no native execution")
    elif args.run:
        base.require(not (base.ROOT / RESULTS).exists(), "refuse to overwrite retained run")
        manifest = base.read(INPUTS)
        base.require(manifest == make_manifest(), "manifest drift")
        screens = preflight(manifest)
        rows = []
        reused_ids = {r["case_id"] for r in manifest["exact_reuse"]}
        for case in manifest["cases"]:
            if case["case_id"] in reused_ids:
                continue
            row = consumer.execute(manifest, case)
            rows.append(row)
            print(case["case_id"], row["outcome"], row["first_failure"], flush=True)
        execution = base.seal(dict(manifest_digest=manifest["record_digest"],
            requested_case_ids=[r["case_id"] for r in rows], cases=rows,
            user_accepted=False, aggregate_closed=False))
        packed = compact(execution)
        base.require(expand(packed) == execution, "lossy compaction")
        record = base.seal(dict(schema="p984c-cos-results-v1", manifest_digest=manifest["record_digest"],
            preflight=screens, execution=packed, reuse=reused(manifest),
            environment=dict(python=platform.python_version(), numpy=version("numpy"), python_flint=version("python-flint")),
            user_accepted=False, aggregate_closed=False))
        base.require(len(json.dumps(record, indent=2).encode()) < 64_000_000, "retention budget exceeded")
        base.write_new(RESULTS, record)
        print(json.dumps(status(manifest, record), indent=2))
    else:
        print(json.dumps(check(base.read(INPUTS), base.read(RESULTS)), indent=2))


if __name__ == "__main__":
    main()

"""Independent A_OS boundary expectations; review precedes native execution.

Reuses the accepted paper evaluator and separate interval equations. No
production current, OS pass, writer, allocator or lifecycle owner is executed.
"""

import argparse
from copy import deepcopy
from contextlib import ExitStack
import json
from unittest.mock import patch

import p984b_aos_oracle as previous
import prepare_p984c_boundaries as boundary
from tests.models.test_grc_9_v4_expansion import independent_tree

base, aos = previous.common, previous.aos
SELF = base.HERE + "p984c_aos_oracle.py"
TEST = base.HERE + "test_p984c_aos_oracle.py"
INPUTS = base.BASE + "P9-8.4c-AOSOracleInputs.json"
RESULTS = base.BASE + "P9-8.4c-AOSOracleResults.json"
REVIEW = base.BASE + "P9-8.4c-AOSOracleReview.md"
PRODUCERS = (
    "pygrc.models.grc_v4_candidate_a.CandidateACurrent",
    "pygrc.models.grc_v4_realizations.CandidateAOSPass",
    "pygrc.models.grc_v4_step.ProvisionalCandidateAOSStep",
    "pygrc.models.grc_9_v4_expansion.GRC9V4ExpansionPlan",
    "pygrc.models.grc_9_v4_lifecycle.GRC9V4AOSOperation",
)


def fixture(source, layout):
    """Independent literal chart and creation-order scan, not native FIFO."""
    event = "independent-boundary-template"
    graph = deepcopy(source["port_graph"])
    graph["live_node_ids"].remove("source-s")
    nodes = set(graph["live_node_ids"])
    for edge in graph["edges"]:
        for side in ("tail", "head"):
            endpoint = edge[side]
            if endpoint["node_id"] == "source-s":
                endpoint["node_id"] = event + f"/satellite/{(endpoint['port'] - 1) % 3 + 1}"
    for name, tail, head, port in independent_tree(tuple(layout["expected"]["branch_extras"]), layout["chirality"]):
        nodes.update((event + "/" + tail, event + "/" + head))
        graph["edges"].append(dict(edge_id=event + "/" + name,
            kind="tree" if "/extra/" in name else "spine",
            tail=dict(node_id=event + "/" + tail, port=port),
            head=dict(node_id=event + "/" + head, port=port)))
    graph["live_node_ids"] = sorted(nodes)
    graph["edges"].sort(key=lambda e: e["edge_id"])
    return dict(fixture_id=layout["id"],
        request=dict(target_effective_degree=layout["degree"], module_chirality=layout["chirality"], growth_phase=layout["phase"]),
        event_identity_payload=dict(canonical_module_node_count=layout["expected"]["module_nodes"]),
        expected=dict(event_id=event, identity_payloads=dict(target_graph=graph)))


def make_manifest():
    old = previous.predecessor()
    accepted = base.read(previous.INPUTS)
    base.check_bindings(accepted["source_bindings"])
    contract = base.read(boundary.OUTPUT)
    family = next(f for f in contract["families"] if f["family"] == "A_OS")
    cases, reuse = [], []
    for layout in contract["layouts"]:
        vector = fixture(old["source"], layout)
        if layout["degree"] == 45:
            template = next(c for c in accepted["cases"] if
                (c["request"]["target_effective_degree"], c["request"]["module_chirality"]) == (45, layout["chirality"]))
            vector["fixture_id"] = template["fixture_id"]
        case = previous.case_for(vector, old, contract)
        if layout["degree"] != 45:
            case["request"]["operation_id"] = "p984c-aos-" + layout["id"]
        if layout["degree"] == 45:
            for key in ("request", "event_id", "event_identity_payload", "target", "comparison"):
                base.require(case[key] == template[key], "D45 exact expectation reuse changed: " + key)
            reuse.append(dict(case_id=layout["id"] + "::A_OS", previous_case_id=template["case_id"]))
        case.update(case_id=layout["id"] + "::A_OS", fixture_id=layout["id"],
            coverage_binding=dict(record_digest=contract["record_digest"], cell_ids=[layout["id"] + "::A_OS::" + role for role in previous.ROLES]),
            changes_from_A1="boundary layout and identities only; source, supplied shares, history policy, parameters, dt and budgets unchanged")
        base.require(case["comparison"] == family["comparison"], "frozen boundary comparison changed")
        recipe = next(c for c in contract["cases"] if c["id"] == case["case_id"])["request_recipe"]
        base.require(case["request"]["resource_distribution"] == recipe["resource_distribution"], "frozen share recipe changed")
        cases.append(case)
    paths = {r["path"] for r in accepted["source_bindings"]} | {
        previous.INPUTS, previous.RESULTS, previous.REVIEW, SELF, TEST,
        boundary.OUTPUT, "tests/models/test_grc_9_v4_expansion.py"}
    return base.seal(dict(schema="p984c-aos-oracle-inputs-v1", family="A_OS",
        source_bindings=base.bind(sorted(paths)), shared=accepted["shared"],
        boundary_digest=contract["record_digest"], cases=cases, exact_reuse=reuse,
        user_accepted=False, native_runtime_executed=False,
        runtime_gate="independent_oracle_review_and_user_acceptance_before_new_A_scope",
        stage_meaning=accepted["stage_meaning"]))


def check_manifest(manifest):
    base.check_digest(manifest)
    base.check_bindings(manifest["source_bindings"])
    base.require(manifest == make_manifest(), "boundary oracle subject/budget/history drift")


def reuse_rows(manifest):
    old = base.read(previous.RESULTS)
    rows = {r["case_id"]: r for r in old["cases"]}
    return [dict(**link, previous_record_digest=old["record_digest"],
        previous_row_digest=base.digest(rows[link["previous_case_id"]])) for link in manifest["exact_reuse"]]


def reused_case(case, previous_id):
    old = next(r for r in base.read(previous.RESULTS)["cases"] if r["case_id"] == previous_id)
    base.require(old["outcome"] == "passed_bounded_oracle", "cannot reuse a failed oracle")
    return {**deepcopy(old), "case_id": case["case_id"], "input_digest": base.digest(case), "coverage_binding": case["coverage_binding"]}


def materialize(manifest, results):
    values = {r["case_id"]: r for r in results["cases"]}
    reuse = {r["case_id"]: r["previous_case_id"] for r in results["reuse"]}
    return base.seal(dict(manifest_digest=manifest["record_digest"],
        shared_observations=base.read(previous.RESULTS)["shared_observations"],
        cases=[reused_case(c, reuse[c["case_id"]]) if c["case_id"] in reuse else values[c["case_id"]] for c in manifest["cases"]],
        native_runtime_executed=False, user_accepted=False))


def validate(manifest, results, *, recheck_numerics=False):
    check_manifest(manifest)
    base.check_digest(results)
    base.require(results["schema"] == "p984c-aos-oracle-results-v1" and results["manifest_digest"] == manifest["record_digest"], "foreign boundary oracle")
    base.require(results["native_runtime_executed"] is False and results["user_accepted"] is False, "scope promotion")
    base.require(results["reuse"] == reuse_rows(manifest), "reuse lineage drift")
    expected_ids = [c["case_id"] for c in manifest["cases"] if c["case_id"] not in {r["case_id"] for r in manifest["exact_reuse"]}]
    base.require([r["case_id"] for r in results["cases"]] == expected_ids, "missing/reordered/extra native-free oracle case")
    summary = previous.validate(manifest, materialize(manifest, results), recheck_numerics=recheck_numerics)
    return {**summary, "oracle_cases_required": 32, "new_oracle_cases": 30,
        "exact_reuse_cases": 2, "runtime_cells_closed": 0}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--prepare", action="store_true")
    group.add_argument("--run-oracle", action="store_true")
    group.add_argument("--check-retained", action="store_true")
    parser.add_argument("--recheck-numerics", action="store_true")
    parser.add_argument("--manifest", default=INPUTS)
    parser.add_argument("--output", default=RESULTS)
    args = parser.parse_args()
    base.require(not args.recheck_numerics or args.check_retained, "recheck requires retained mode")
    for name in (args.manifest, args.output):
        base.require(not base.Path(name).is_absolute() and ".." not in base.Path(name).parts, "repository-relative output required")
    with ExitStack() as stack:
        for name in PRODUCERS:
            stack.enter_context(patch(name, side_effect=AssertionError("native producer forbidden: " + name)))
        if args.prepare:
            base.write_new(args.manifest, make_manifest())
            print("A_OS boundary oracle subjects prepared; no native execution")
            return
        manifest = base.read(args.manifest)
        check_manifest(manifest)
        if args.check_retained:
            print(json.dumps(validate(manifest, base.read(args.output), recheck_numerics=args.recheck_numerics), indent=2))
            return
        base.require(not (base.ROOT / args.output).exists(), "refuse to overwrite oracle result")
        reuse_ids = {r["case_id"] for r in manifest["exact_reuse"]}
        rows = []
        for case in manifest["cases"]:
            if case["case_id"] in reuse_ids:
                continue
            row = previous.run_case(case)
            rows.append(row)
            print(case["case_id"], row["outcome"], row["first_failure"], flush=True)
        record = base.seal(dict(schema="p984c-aos-oracle-results-v1", manifest_digest=manifest["record_digest"],
            cases=rows, reuse=reuse_rows(manifest), native_runtime_executed=False, user_accepted=False))
        base.require(len(json.dumps(record, indent=2).encode()) < 64_000_000, "retention budget exceeded")
        base.write_new(args.output, record)
        print(json.dumps(validate(manifest, record), indent=2))


if __name__ == "__main__":
    main()

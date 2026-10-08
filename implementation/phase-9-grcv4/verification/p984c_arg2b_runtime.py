"""A_RG2b capacity-boundary campaign using the accepted coupled C/Y-chain, W-writer and lagged-invariance comparator.

Thirty new native cases, two exact D45 reuses; no new scientific declaration.
Nominal predictions precede each event. Saved read/step operands support
independent pointwise interval, signed Read-Back and inverse-chain rechecking, not a uniform
parameter or accumulated trajectory error theorem.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from contextlib import contextmanager
from copy import deepcopy
from importlib.metadata import version
import json
import platform
from unittest.mock import patch

import p984b_arg2b_runtime as r
import p984c_cos as construction
import prepare_p984c_boundaries as boundary
from p984c_cci_runtime import expand

b = r.b
SELF = b.HERE + "p984c_arg2b_runtime.py"
TEST = b.HERE + "test_p984c_arg2b_runtime.py"
INPUTS = b.BASE + "P9-8.4c-ARG2bCases.json"
RESULTS = b.BASE + "P9-8.4c-ARG2bResults.json"
REVIEW = b.BASE + "P9-8.4c-ARG2bRuntimeReview.md"
ACCEPTANCE_SHA = "9692b616a09a3c764cede9b109d3fbcb6fe849844c383dc97f84a9fe6e89f295"
PREDECESSOR_DIGEST = "91c634e6692afade225b637f3cdcd54f995c62fdc0d55cb26e9272121c1a6446"


def compact(value):
    """Intern exact repeated RG chains/certificates as well as matrix context.

    The accepted generic expander authenticates all entries and reconstructs
    identical operands. No chain level, residual or uncertainty is discarded.
    """
    contexts = {}

    def visit(x):
        if isinstance(x, list):
            return [visit(v) for v in x]
        if not isinstance(x, dict):
            return x
        out = {}
        for key, item in x.items():
            if key in ("reference", "H1_form", "H", "source", "generated",
                    "chain", "independent_certificate") and isinstance(item, (dict, list)):
                token = b.digest(item)
                contexts[token] = item
                out[key] = {"cci_boundary_context": token}
            else:
                out[key] = visit(item)
        return out

    payload = visit(value)
    return dict(contexts=contexts, payload=payload)


def predecessor():
    b.require(b.sha((b.ROOT / r.REVIEW).read_bytes()) == ACCEPTANCE_SHA, "A_RG2b predecessor acceptance drift")
    manifest, result = b.read(r.INPUTS), b.read(r.RESULTS)
    b.check_digest(manifest)
    b.check_bindings(manifest["source_bindings"])
    b.check_digest(result)
    b.require(result["record_digest"] == PREDECESSOR_DIGEST
        and result["manifest_digest"] == manifest["record_digest"]
        and len(result["cases"]) == 16 and all(v["case_passed"] for v in result["cases"]),
        "incomplete accepted A_RG2b predecessor")
    return manifest, result


def make_manifest():
    old, result = predecessor()
    contract = b.read(boundary.OUTPUT)
    b.check_digest(contract)
    family = next(v for v in contract["families"] if v["family"] == "A_RG2b")
    source = result["shared"]["actual_source"]
    cases, reuse = [], []
    for layout in contract["layouts"]:
        template = next(v["executed_case"] for v in result["cases"] if
            (v["executed_case"]["request"]["target_effective_degree"], v["executed_case"]["request"]["module_chirality"], v["executed_case"]["request"]["growth_phase"])
            == (45 if layout["degree"] == 45 else 31, layout["chirality"], layout["phase"]))
        case = deepcopy(template)
        case.update(case_id=layout["id"] + "::A_RG2b", fixture_id=layout["id"],
            subject_kind="native_boundary_companion",
            coverage_binding=dict(record_digest=contract["record_digest"],
                cell_ids=[layout["id"] + "::A_RG2b::" + role for role in r.ROLES]),
            comparison=family["comparison"], execution_budget_seconds=family["execution_budget_seconds"],
            changes_from_frozen=["boundary_layout_and_event_identity_only"])
        case["request"]["target_effective_degree"] = layout["degree"]
        if layout["degree"] != 45:
            case["request"]["operation_id"] = "p984c-arg2b-" + layout["id"]
        case["oracle"] = construction.target_oracle(source, template, case["request"], layout)
        case["independent_graph_chart"] = r.chart_record(r.independent_target(r.state(source), case).inputs)
        recipe = next(v for v in contract["cases"] if v["id"] == case["case_id"])["request_recipe"]
        b.require(case["request"]["resource_distribution"] == recipe["resource_distribution"], "boundary shares drift")
        if layout["degree"] == 45:
            for key in ("request", "oracle", "schedule", "comparison", "execution_budget_seconds", "independent_graph_chart"):
                b.require(case[key] == template[key], "D45 scientific operand drift: " + key)
            reuse.append(dict(case_id=case["case_id"], previous_case_id=template["case_id"]))
        cases.append(case)
    paths = {v["path"] for v in old["source_bindings"]} | {
        SELF, TEST, r.INPUTS, r.RESULTS, r.REVIEW, construction.SELF,
        boundary.OUTPUT, b.HERE + "p984c_cci_runtime.py", "tests/models/test_grc_9_v4_expansion.py"}
    return b.seal(dict(schema="p984c-arg2b-runtime-inputs-v1", family="A_RG2b",
        initial_inputs=old["initial_inputs"], nominal_source=old["nominal_source"], expected_source=source,
        source_bindings=b.bind(sorted(paths)), boundary_digest=contract["record_digest"],
        cases=cases, exact_reuse=reuse,
        source_execution=dict(path=r.RESULTS, record_digest=result["record_digest"],
            shared_digest=b.digest(result["shared"]), new_source_steps=0),
        user_accepted=False, aggregate_closed=False))


def check_manifest(manifest):
    b.check_digest(manifest)
    b.check_bindings(manifest["source_bindings"])
    b.require(manifest == make_manifest(), "boundary manifest drift")


def reuse_rows(manifest, shared):
    _, old = predecessor()
    b.require(shared == old["shared"], "accepted source drift")
    links = []
    for link in manifest["exact_reuse"]:
        original = next(v["executed_case"] for v in old["cases"] if v["case_id"] == link["previous_case_id"])
        row = next(v for v in old["cases"] if v["case_id"] == link["previous_case_id"])
        case = next(v for v in manifest["cases"] if v["case_id"] == link["case_id"])
        for key in ("request", "oracle", "schedule", "comparison", "execution_budget_seconds", "independent_graph_chart"):
            b.require(case[key] == original[key], "D45 exact scientific reuse drift")
        b.require(row["case_passed"] and row["event_committed"] and row["first_failure"] is None, "incomplete reuse")
        links.append(dict(**link, previous_record_digest=old["record_digest"], previous_row_digest=b.digest(row)))
    return links


def materialize(manifest, record):
    execution = expand(record["execution"])
    b.check_digest(execution)
    _, old = predecessor()
    rows = {v["case_id"]: v for v in execution["cases"]}
    for link in record["reuse"]:
        original = next(v for v in old["cases"] if v["case_id"] == link["previous_case_id"])
        case = next(v for v in manifest["cases"] if v["case_id"] == link["case_id"])
        rows[case["case_id"]] = dict(deepcopy(original), case_id=case["case_id"],
            input_digest=b.digest(case), coverage_binding=case["coverage_binding"], executed_case=deepcopy(case))
    return b.seal(dict(execution, cases=[rows[c["case_id"]] for c in manifest["cases"]]))


def status(manifest, record):
    check_manifest(manifest)
    b.check_digest(record)
    b.require(record["schema"] == "p984c-arg2b-runtime-results-v1"
        and record["manifest_digest"] == manifest["record_digest"]
        and record["user_accepted"] is False and record["aggregate_closed"] is False, "runtime scope drift")
    execution = expand(record["execution"])
    b.check_digest(execution)
    b.require(execution["manifest_digest"] == manifest["record_digest"]
        and execution["native_runtime_executed"] is True
        and execution["user_accepted"] is False and execution["aggregate_closed"] is False, "execution scope drift")
    b.require(record["reuse"] == reuse_rows(manifest, execution["shared"]), "reuse lineage drift")
    reused = {v["case_id"] for v in record["reuse"]}
    wanted = [v for v in manifest["cases"] if v["case_id"] not in reused]
    b.require([v["case_id"] for v in execution["cases"]] == [v["case_id"] for v in wanted], "native case roster drift")
    for case, row in zip(wanted, execution["cases"], strict=True):
        b.require(row["input_digest"] == b.digest(case) and row["executed_case"] == case
            and row["coverage_binding"] == case["coverage_binding"]
            and row["user_accepted"] is False and row["aggregate_closed"] is False, "case scope/input drift")
        success = row["outcome"] == "passed_named_case"
        b.require(row["case_passed"] is success, "event/case conflation")
        if success:
            b.require(row["event_committed"] is True and row["first_failure"] is None
                and [(v["role"], v["index"]) for v in row["continuation"]]
                == [(role, i) for role in r.ROLES for i in range(1, 11)]
                and set(row["final_reads"]) == set(r.ROLES), "incomplete native schedule")
        else:
            b.require(row["outcome"] == "incomplete_case" and row["first_failure"] is not None, "hidden native failure")
    passed = sum(v["case_passed"] for v in execution["cases"])
    return dict(family="A_RG2b", native_cases=len(wanted), passed_cases=passed,
        exact_reuse_cases=len(reused), successful_history_cells=2*(passed+len(reused)),
        accepted_cells=0, native_trajectories_rerun=False, interval_equations_recomputed=False,
        cases=[{k: row[k] for k in ("case_id", "case_passed", "event_committed", "first_failure")} for row in execution["cases"]])


def bind_case(seed, case, manifest):
    """Frozen independent graph with actual (not nominal) source/history."""
    b.require(seed.to_payload() == manifest["expected_source"], "actual source/history drift")
    expected = next(c for c in manifest["cases"] if c["case_id"] == case["case_id"])
    b.require(case == expected, "boundary declaration drift")
    request = case["request"]
    b.require(request["source_state_digest"] == seed.scientific_digest
        and request["history_policy"] == r.history_policy(seed),
        "source binding drift")
    return deepcopy(expected)


@contextmanager
def data_adapter(manifest):
    # Supply only frozen declaration data. Numerical/native producers unchanged.
    with patch.object(r, "bind_case", lambda seed, case: bind_case(seed, case, manifest)):
        yield


def check(manifest, record, *, numerics=False):
    summary = status(manifest, record)
    execution = materialize(manifest, record)
    with data_adapter(manifest):
        checked = r.validate(manifest, execution, numerics=numerics)
    return {**summary, **checked, "cases_required": len(manifest["cases"])}


def run_case(job):
    manifest, shared, case = job
    with b.exact_backend(b.ExactBackend.FLINT), data_adapter(manifest):
        row = r.execute_case(r.state(shared["actual_source"]), case)
    print(case["case_id"], row["outcome"], row["first_failure"],
        f"seconds={row['elapsed_seconds']:.2f}", flush=True)
    return row


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--prepare", action="store_true")
    mode.add_argument("--run", action="store_true")
    mode.add_argument("--check-retained", action="store_true")
    parser.add_argument("--recheck-numerics", action="store_true")
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    b.require(not args.recheck_numerics or args.check_retained, "recheck requires retained mode")
    b.require(1 <= args.workers <= 8, "worker count outside 1..8")
    if args.prepare:
        r.write_new(INPUTS, make_manifest())
        print("A_RG2b boundary inputs frozen; no native execution")
        return
    manifest = b.read(INPUTS)
    check_manifest(manifest)
    if args.check_retained:
        with r.native_disabled():
            print(json.dumps(check(manifest, b.read(RESULTS), numerics=args.recheck_numerics), indent=2))
        return
    b.require(not (b.ROOT / RESULTS).exists(), "refuse to overwrite retained execution")
    _, old = predecessor()
    shared = old["shared"]
    reused = {v["case_id"] for v in manifest["exact_reuse"]}
    jobs = [(manifest, shared, c) for c in manifest["cases"] if c["case_id"] not in reused]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        rows = list(pool.map(run_case, jobs))
    b.require(all(v["case_passed"] for v in rows), "incomplete campaign; no final evidence published")
    execution = b.seal(dict(manifest_digest=manifest["record_digest"], shared=shared, cases=rows,
        native_runtime_executed=True, user_accepted=False, aggregate_closed=False))
    record = dict(schema="p984c-arg2b-runtime-results-v1", manifest_digest=manifest["record_digest"],
        environment=dict(python=platform.python_version(), numpy=version("numpy"),
            mpmath=version("mpmath"), python_flint=version("python-flint")),
        execution=compact(execution), reuse=reuse_rows(manifest, shared),
        user_accepted=False, aggregate_closed=False)
    record = b.seal(record)
    with r.native_disabled():
        summary = check(manifest, record)
    b.require(len(b.canonical_json_bytes(record)) < 128_000_000, "retention budget exceeded")
    r.write_new(RESULTS, record)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    with b.exact_backend(b.ExactBackend.FLINT):
        main()

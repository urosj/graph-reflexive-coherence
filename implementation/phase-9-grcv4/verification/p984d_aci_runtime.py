"""Native A_CI deep single-event campaign against its accepted joint oracle.

Reuses unchanged native producers and scientific checks. Only input binding and
independent prediction lookup are adapted. No successive-event or sibling credit.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from copy import deepcopy
from importlib.metadata import version
import json
import platform

import p984d_aci_oracle as preparation
import p984c_aci_runtime as previous

r, b = previous.r, previous.b
SELF = b.HERE + "p984d_aci_runtime.py"
TEST = b.HERE + "test_p984d_aci_runtime.py"
INPUTS = b.BASE + "P9-8.4d-ACICases.json"
RESULTS = b.BASE + "P9-8.4d-ACIResults.json"
REVIEW = b.BASE + "P9-8.4d-ACIRuntimeReview.md"
ACCEPTANCE_SHA = "17bd90f66ccea96e26c0c2d0207f25fa66c6720a56d322b3999d7b178c9022c2"
ORACLE_DIGEST = "daf8d3299ea9e6a12e3f1b35c6376d2a25fd9249d1956a28d5a49ff96ef2e1d8"


def accepted_oracle():
    b.require(b.sha((b.ROOT / preparation.REVIEW).read_bytes()) == ACCEPTANCE_SHA,
        "accepted deep A_CI oracle review changed")
    inputs, result = b.read(preparation.INPUTS), b.read(preparation.RESULTS)
    summary = preparation.status(inputs, result)
    b.require(result["record_digest"] == ORACLE_DIGEST and summary["passed_cases"] == 20,
        "incomplete/changed accepted deep oracle")
    return inputs, result


def predecessor():
    old = b.read(previous.INPUTS)
    b.check_digest(old)
    b.check_bindings(old["source_bindings"])
    _, result = previous.preparation.predecessor()
    b.require(result["shared"]["actual_source"] == old["expected_source"], "source reuse drift")
    return old, result["shared"]


def make_manifest():
    ready, result = accepted_oracle()
    old, shared = predecessor()
    b.require(shared["actual_source"] == ready["expected_source"], "oracle source mismatch")
    cases = deepcopy(ready["cases"])
    for case in cases:
        case["subject_kind"] = "native_boundary_companion"
    paths = {v["path"] for v in ready["source_bindings"]} | {
        preparation.SELF, preparation.INPUTS, preparation.RESULTS, preparation.REVIEW,
        SELF, TEST, previous.SELF, b.HERE + "p984c_cci_runtime.py",
        previous.preparation.previous.RESULTS}
    return b.seal(dict(schema="p984d-aci-runtime-inputs-v1", family="A_CI",
        source_bindings=b.bind(sorted(paths)), initial_inputs=old["initial_inputs"],
        nominal_source=old["nominal_source"], expected_source=ready["expected_source"],
        oracle_inputs_digest=ready["record_digest"], oracle_results_digest=result["record_digest"],
        acceptance=dict(path=preparation.REVIEW, sha256=ACCEPTANCE_SHA, scope="oracle_only"),
        cases=cases, source_reused=True, source_execution=dict(new_source_steps=0,
            path=previous.preparation.previous.RESULTS, shared_digest=b.digest(shared)),
        scope=dict(required_cases=20, required_history_cells=40, target_beats_per_role=10,
            successive_events=False, arbitrary_depth=False, retention_budget_bytes=64_000_000),
        user_accepted=False, aggregate_closed=False))


def check_manifest(manifest):
    b.check_digest(manifest)
    b.check_bindings(manifest["source_bindings"])
    b.require(manifest == make_manifest(), "deep A_CI native subject/law/budget drift")


def status(manifest, record):
    check_manifest(manifest)
    b.check_digest(record)
    b.require(record["schema"] == "p984d-aci-runtime-results-v1"
        and record["manifest_digest"] == manifest["record_digest"]
        and record["user_accepted"] is False and record["aggregate_closed"] is False,
        "runtime scope drift")
    execution = previous.expand(record["execution"])
    b.check_digest(execution)
    b.require(execution["manifest_digest"] == manifest["record_digest"]
        and execution["native_runtime_executed"] is True
        and execution["user_accepted"] is False and execution["aggregate_closed"] is False,
        "execution scope drift")
    _, shared = predecessor()
    b.require(execution["shared"] == shared, "source execution drift")
    rows = execution["cases"]
    b.require([v["case_id"] for v in rows] == [c["case_id"] for c in manifest["cases"]], "case roster drift")
    for case, row in zip(manifest["cases"], rows, strict=True):
        b.require(row["input_digest"] == b.digest(case) and row["actual_case"] == case
            and row["coverage_binding"] == case["coverage_binding"]
            and row["user_accepted"] is False and row["aggregate_closed"] is False, "case input/scope drift")
        success = row["outcome"] == "passed_named_case"
        b.require(row["case_passed"] is success, "event/case conflation")
        if success:
            b.require(row["event_committed"] is True and row["first_failure"] is None
                and [(v["role"], v["index"]) for v in row["continuation"]]
                == [(role, i) for role in r.ROLES for i in range(1, 11)]
                and set(row["final_reads"]) == set(r.ROLES), "incomplete native schedule")
        else:
            b.require(row["outcome"] == "incomplete_case" and row["first_failure"] is not None,
                "hidden native failure")
    passed = sum(v["case_passed"] for v in rows)
    return dict(family="A_CI", status="implemented_pending_acceptance" if passed == 20 else "incomplete_campaign",
        native_cases=20, passed_cases=passed, required_cells=40, successful_history_cells=2*passed,
        accepted_cells=0, passing_pending_cells=2*passed, target_steps=sum(len(v["continuation"]) for v in rows),
        final_reads=sum(len(v["final_reads"]) for v in rows), degrees=[59,66,73,94], maximum_core_depth=4,
        native_trajectories_rerun=False, interval_equations_recomputed=False,
        successive_events=False, arbitrary_depth=False, user_accepted=False, aggregate_closed=False,
        failures=[{k: row[k] for k in ("case_id", "event_committed", "first_failure")} for row in rows if not row["case_passed"]])


def check(manifest, record, *, numerics=False):
    summary = status(manifest, record)
    ready, result = accepted_oracle()
    execution = previous.expand(record["execution"])
    expected = {v["case_id"]: previous.predictions(v) for v in result["cases"]}
    for row in execution["cases"]:
        if row["case_passed"]:
            b.require(row["predictions"] == expected[row["case_id"]], "accepted prediction drift")
    with previous.data_adapter(ready, result):
        checked = r.validate(manifest, execution, numerics=numerics)
    b.require(checked["cases_passed"] == summary["passed_cases"], "consumer/summary mismatch")
    return dict(summary, retained_integrity="passed", interval_equations_recomputed=numerics)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--prepare", action="store_true")
    group.add_argument("--run", action="store_true")
    group.add_argument("--check-retained", action="store_true")
    parser.add_argument("--recheck-numerics", action="store_true")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--output", default=RESULTS)
    args = parser.parse_args()
    b.require(1 <= args.workers <= 4, "workers outside 1..4")
    b.require(not args.recheck_numerics or args.check_retained, "recheck requires retained mode")
    b.require(not b.Path(args.output).is_absolute() and ".." not in b.Path(args.output).parts, "relative output required")
    if args.prepare:
        b.write_new(INPUTS, make_manifest())
        print("20 native A_CI deep subjects bound to accepted oracle")
        return
    manifest = b.read(INPUTS)
    check_manifest(manifest)
    if args.check_retained:
        print(json.dumps(check(manifest, b.read(args.output), numerics=args.recheck_numerics), indent=2))
        return
    b.require(not (b.ROOT / args.output).exists(), "refuse to overwrite execution")
    ready, result = accepted_oracle()
    _, shared = predecessor()
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        rows = list(pool.map(previous.run_case,
            [(ready, result, shared["actual_source"], case) for case in manifest["cases"]]))
    execution = b.seal(dict(manifest_digest=manifest["record_digest"], shared=shared, cases=rows,
        native_runtime_executed=True, user_accepted=False, aggregate_closed=False))
    packed = previous.compact(execution)
    b.require(previous.expand(packed) == execution, "lossy compaction")
    record = b.seal(dict(schema="p984d-aci-runtime-results-v1", manifest_digest=manifest["record_digest"],
        execution=packed, environment=dict(python=platform.python_version(), numpy=version("numpy"),
            mpmath=version("mpmath"), python_flint=version("python-flint"), workers=args.workers),
        user_accepted=False, aggregate_closed=False))
    b.require(len(json.dumps(record,indent=2).encode()) < manifest["scope"]["retention_budget_bytes"], "retention budget")
    b.write_new(args.output, record)
    report = check(manifest, record)
    print(json.dumps(report, indent=2))
    if report["passed_cases"] != 20:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

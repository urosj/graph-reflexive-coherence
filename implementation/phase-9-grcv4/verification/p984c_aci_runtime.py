"""Native A_CI boundary campaign against the separately accepted joint oracle.

Only --run executes new native trajectories. The source beat and two D45 cases
are exact accepted reuse. Adapters supply frozen data, never numerical results.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from contextlib import ExitStack, contextmanager
from copy import deepcopy
from importlib.metadata import version
import json
import platform
from unittest.mock import patch

import p984c_aci_oracle as preparation
from p984c_cci_runtime import compact, expand

r, b = preparation.previous, preparation.b
SELF = b.HERE + "p984c_aci_runtime.py"
TEST = b.HERE + "test_p984c_aci_runtime.py"
INPUTS = b.BASE + "P9-8.4c-ACICases.json"
RESULTS = b.BASE + "P9-8.4c-ACIResults.json"
REVIEW = b.BASE + "P9-8.4c-ACIRuntimeReview.md"
ACCEPTANCE_SHA = "ca4f78d414b5f751219b103a34bbbeb5fe716e5e936450d19ee7b3276ed1043c"
ORACLE_RESULT_DIGEST = "5791b2531aa13a37a01466d2bc3ca6c780cf1874b9b1b7c71f148ac4c89b885a"


def accepted_oracle():
    b.require(b.sha((b.ROOT / preparation.REVIEW).read_bytes()) == ACCEPTANCE_SHA,
        "accepted A_CI boundary oracle review changed")
    inputs, result = b.read(preparation.INPUTS), b.read(preparation.RESULTS)
    summary = preparation.status(inputs, result)
    b.require(result["record_digest"] == ORACLE_RESULT_DIGEST
        and summary["passed_cases"] == 30 and summary["exact_accepted_target_reuses"] == 2,
        "incomplete or changed accepted oracle")
    return inputs, result


def make_manifest():
    ready, result = accepted_oracle()
    old, _ = preparation.predecessor()
    cases = deepcopy(ready["cases"])
    for case in cases:
        case["subject_kind"] = "native_boundary_companion"
    paths = {v["path"] for v in ready["source_bindings"]} | {
        preparation.SELF, preparation.INPUTS, preparation.RESULTS, preparation.REVIEW,
        SELF, TEST, b.HERE + "p984c_cci_runtime.py"}
    return b.seal(dict(schema="p984c-aci-runtime-inputs-v1", family="A_CI",
        source_bindings=b.bind(sorted(paths)), initial_inputs=old["initial_inputs"],
        nominal_source=old["nominal_source"], expected_source=ready["expected_source"],
        oracle_inputs_digest=ready["record_digest"], oracle_results_digest=result["record_digest"],
        acceptance=dict(path=preparation.REVIEW, sha256=ACCEPTANCE_SHA, scope="oracle_only"),
        cases=cases, exact_reuse=ready["exact_reuse"], source_reused=True,
        source_execution="exact accepted source beat reused; every event reads it afresh",
        user_accepted=False, aggregate_closed=False))


def check_manifest(manifest):
    b.check_digest(manifest)
    b.check_bindings(manifest["source_bindings"])
    b.require(manifest == make_manifest(), "native boundary manifest drift")


def bind_case(seed, case, ready):
    """Exact accepted source and independent port graph, not the old vector roster."""
    b.require(seed.to_payload() == ready["expected_source"], "actual source/history identity drift")
    expected = next(v for v in ready["cases"] if v["case_id"] == case["case_id"])
    expected = dict(expected, subject_kind="native_boundary_companion")
    b.require(case == expected, "boundary case/transfer/oracle drift")
    request = case["request"]
    b.require(request["source_state_digest"] == seed.scientific_digest
        and request["history_policy"] == r.oracle.history_policy(
            b.authority_payload(seed.inputs.current), b.authority_payload(seed.inputs.reset)),
        "request source/history binding drift")
    return deepcopy(expected)


def predictions(row):
    return {role: [dict(index=v["index"], output=v["output"], domain=v["certificate"]["domain"])
        for v in row["observations"] if v["role"] == role and v["index"] <= 10]
        for role in r.ROLES}


@contextmanager
def data_adapter(ready, result):
    by_target = {v["target_digest"]: predictions(v) for v in result["cases"]}
    def preflight(target):
        key = b.digest(target.to_payload())
        b.require(key in by_target, "target absent from accepted oracle")
        return deepcopy(by_target[key])
    # Only data binding and precomputed independent expectations are adapted.
    # Native current/root/step/event producers and scientific checks are unchanged.
    with patch.object(r, "bind_case", lambda seed, case: bind_case(seed, case, ready)), \
            patch.object(r, "preflight", preflight):
        yield


def reuse_rows(manifest, shared):
    _, old = preparation.predecessor()
    b.require(shared == old["shared"], "accepted source execution drift")
    ready, _ = accepted_oracle()
    rows = preparation.reuse_rows(ready)
    b.require([{k: row[k] for k in ("case_id", "previous_case_id")} for row in rows]
        == manifest["exact_reuse"], "reuse population drift")
    return rows


def materialize(manifest, record):
    execution = expand(record["execution"])
    b.check_digest(execution)
    rows = {v["case_id"]: v for v in execution["cases"]}
    _, old = preparation.predecessor()
    for link in record["reuse"]:
        original = next(v for v in old["cases"] if v["case_id"] == link["previous_case_id"])
        case = next(v for v in manifest["cases"] if v["case_id"] == link["case_id"])
        for key in ("request", "oracle", "comparison", "schedule", "execution_budget_seconds"):
            b.require(original["actual_case"][key] == case[key], "D45 scientific operand drift")
        rows[case["case_id"]] = dict(deepcopy(original), case_id=case["case_id"],
            input_digest=b.digest(case), coverage_binding=case["coverage_binding"], actual_case=deepcopy(case))
    return b.seal(dict(execution, cases=[rows[c["case_id"]] for c in manifest["cases"]]))


def status(manifest, record):
    """Pinned retained identities/roster, not numerical recomputation or rerun."""
    check_manifest(manifest)
    b.check_digest(record)
    b.require(record["schema"] == "p984c-aci-runtime-results-v1"
        and record["manifest_digest"] == manifest["record_digest"]
        and record["user_accepted"] is False and record["aggregate_closed"] is False,
        "runtime scope drift")
    execution = expand(record["execution"])
    b.check_digest(execution)
    b.require(execution["manifest_digest"] == manifest["record_digest"]
        and execution["native_runtime_executed"] is True
        and execution["user_accepted"] is False and execution["aggregate_closed"] is False,
        "execution scope drift")
    b.require(record["reuse"] == reuse_rows(manifest, execution["shared"]), "native reuse lineage drift")
    reused = {v["case_id"] for v in record["reuse"]}
    wanted = [v for v in manifest["cases"] if v["case_id"] not in reused]
    b.require([v["case_id"] for v in execution["cases"]] == [v["case_id"] for v in wanted],
        "native case roster drift")
    for case, row in zip(wanted, execution["cases"], strict=True):
        b.require(row["input_digest"] == b.digest(case) and row["actual_case"] == case
            and row["coverage_binding"] == case["coverage_binding"]
            and row["user_accepted"] is False and row["aggregate_closed"] is False,
            "case scope/input drift")
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
    passed = sum(v["case_passed"] for v in execution["cases"])
    return dict(family="A_CI", native_cases=len(wanted), passed_cases=passed,
        exact_reuse_cases=len(record["reuse"]), successful_history_cells=2*(passed+len(record["reuse"])),
        accepted_cells=0, native_trajectories_rerun=False, interval_equations_recomputed=False,
        cases=[{k: row[k] for k in ("case_id", "case_passed", "event_committed", "first_failure")}
            for row in execution["cases"]])


def check(manifest, record, *, numerics=False):
    summary = status(manifest, record)
    ready, result = accepted_oracle()
    expected = {v["case_id"]: predictions(v) for v in result["cases"]}
    for row in expand(record["execution"])["cases"]:
        if row["case_passed"]:
            b.require(row["predictions"] == expected[row["case_id"]], "accepted prediction drift")
    with data_adapter(ready, result):
        checked = r.validate(manifest, materialize(manifest, record), numerics=numerics)
    return {**summary, **checked, "cases_required": len(manifest["cases"])}


def run_case(job):
    ready, result, payload, case = job
    with b.exact_backend(b.ExactBackend.FLINT), data_adapter(ready, result):
        row = r.execute_case(r.state(payload), case)
    print(case["case_id"], row["outcome"], row["first_failure"], flush=True)
    return row


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
    b.require(not args.recheck_numerics or args.check_retained, "recheck requires retained mode")
    b.require(1 <= args.workers <= 8, "worker count outside 1..8")
    b.require(not b.Path(args.output).is_absolute() and ".." not in b.Path(args.output).parts,
        "repository-relative output required")
    if args.prepare:
        b.write_new(INPUTS, make_manifest())
        print("A_CI native boundary inputs bound to accepted oracle; no native execution")
        return
    manifest = b.read(INPUTS)
    check_manifest(manifest)
    if args.check_retained:
        with ExitStack() as stack:
            for name in preparation.PRODUCERS:
                stack.enter_context(patch(name, side_effect=AssertionError("native producer disabled")))
            stack.enter_context(patch.object(r.native, "ProvisionalCandidateCIStep",
                side_effect=AssertionError("native producer disabled")))
            print(json.dumps(check(manifest, b.read(args.output), numerics=args.recheck_numerics), indent=2))
        return
    b.require(not (b.ROOT / args.output).exists(), "refuse to overwrite execution")
    ready, result = accepted_oracle()
    _, previous = preparation.predecessor()
    shared = previous["shared"]
    reuse = reuse_rows(manifest, shared)
    reused = {v["case_id"] for v in reuse}
    jobs = [(ready, result, shared["actual_source"], case)
        for case in manifest["cases"] if case["case_id"] not in reused]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        rows = list(pool.map(run_case, jobs))
    execution = b.seal(dict(manifest_digest=manifest["record_digest"], shared=shared,
        cases=rows, native_runtime_executed=True, user_accepted=False, aggregate_closed=False))
    packed = compact(execution)
    b.require(expand(packed) == execution, "lossy native compaction")
    record = b.seal(dict(schema="p984c-aci-runtime-results-v1", manifest_digest=manifest["record_digest"],
        execution=packed, reuse=reuse, environment=dict(python=platform.python_version(),
            numpy=version("numpy"), mpmath=version("mpmath"), python_flint=version("python-flint"),
            workers=args.workers), user_accepted=False, aggregate_closed=False))
    b.write_new(args.output, record)
    report = status(manifest, record)
    print(json.dumps(report, indent=2))
    if report["successful_history_cells"] != 64:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

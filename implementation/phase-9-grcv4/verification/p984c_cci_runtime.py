"""Native C_CI boundary events and continuation on the prepared targets.

The accepted source beat and two D45 cases are exact reuse. Only --run executes
new trajectories. Retained checks disable native numerical/event producers.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from contextlib import ExitStack
from copy import deepcopy
from importlib.metadata import version
import json
import platform
from unittest.mock import patch

import p984c_cci_preparation as preparation

r, b = preparation.r, preparation.b
SELF = b.HERE + "p984c_cci_runtime.py"
TEST = b.HERE + "test_p984c_cci_runtime.py"
INPUTS = b.BASE + "P9-8.4c-CCICases.json"
RESULTS = b.BASE + "P9-8.4c-CCIResults.json"
REVIEW = b.BASE + "P9-8.4c-CCIRuntimeReview.md"


def compact(value):
    """Intern exact repeated matrices/references, without rounding or pruning."""
    contexts = {}

    def visit(x):
        if isinstance(x, list):
            return [visit(v) for v in x]
        if not isinstance(x, dict):
            return x
        out = {}
        for key, item in x.items():
            if key in ("reference", "H1_form", "H", "source", "generated") and isinstance(item, (dict, list)):
                token = b.digest(item)
                contexts[token] = item
                out[key] = {"cci_boundary_context": token}
            else:
                out[key] = visit(item)
        return out

    payload = visit(value)
    return dict(contexts=contexts, payload=payload)


def expand(value):
    b.require(set(value) == {"contexts", "payload"}, "compact envelope fields")
    contexts, used = value["contexts"], set()
    for token, item in contexts.items():
        b.require(b.digest(item) == token, "context digest drift")

    def visit(x):
        if isinstance(x, list):
            return [visit(v) for v in x]
        if not isinstance(x, dict):
            return x
        if "cci_boundary_context" in x:
            token = x["cci_boundary_context"]
            b.require(set(x) == {"cci_boundary_context"} and token in contexts, "unknown context")
            used.add(token)
            return deepcopy(contexts[token])
        return {k: visit(v) for k, v in x.items()}

    result = visit(value["payload"])
    b.require(used == set(contexts), "unused retained context")
    return result


def make_manifest():
    ready, result = b.read(preparation.INPUTS), b.read(preparation.RESULTS)
    summary = preparation.status(ready, result)
    b.require(summary["passed_cases"] == 30 and summary["exact_reuse_cases"] == 2,
        "incomplete C_CI preparation")
    old, _ = preparation.predecessor()
    cases = deepcopy(ready["cases"])
    for case in cases:
        case["subject_kind"] = "native_boundary_companion"
    paths = {v["path"] for v in ready["source_bindings"]} | {
        preparation.SELF, preparation.INPUTS, preparation.RESULTS, SELF, TEST}
    return b.seal(dict(schema="p984c-cci-runtime-inputs-v1", family="C_CI",
        source_bindings=b.bind(sorted(paths)), initial_inputs=old["initial_inputs"],
        expected_source=ready["expected_source"], preparation_digest=result["record_digest"],
        preparation_inputs_digest=ready["record_digest"], cases=cases,
        exact_reuse=ready["exact_reuse"], source_execution=ready["source_execution"],
        shared_source_rule="exact accepted source beat reused; each new event reads it afresh",
        user_accepted=False, aggregate_closed=False))


def check_manifest(manifest):
    b.check_digest(manifest)
    b.check_bindings(manifest["source_bindings"])
    b.require(manifest == make_manifest(), "native boundary manifest drift")


def reuse_rows(manifest, shared):
    _, old = preparation.predecessor()
    b.require(shared == old["shared"], "accepted source execution drift")
    rows = preparation.reuse_rows(manifest, old)
    old_manifest = b.read(preparation.previous.INPUTS)
    for link in rows:
        row = next(v for v in old["cases"] if v["case_id"] == link["previous_case_id"])
        original = next(v for v in old_manifest["cases"] if v["case_id"] == link["previous_case_id"])
        case = next(v for v in manifest["cases"] if v["case_id"] == link["case_id"])
        b.require(row["case_passed"] and row["event_committed"] and row["first_failure"] is None,
            "incomplete D45 evidence")
        for key in ("request", "oracle", "schedule", "comparison", "execution_budget_seconds"):
            b.require(case[key] == original[key], "D45 scientific operand drift")
    return rows


def materialize(manifest, record):
    execution = expand(record["execution"])
    b.check_digest(execution)
    rows = {v["case_id"]: v for v in execution["cases"]}
    _, old = preparation.predecessor()
    for link in record["reuse"]:
        original = next(v for v in old["cases"] if v["case_id"] == link["previous_case_id"])
        case = next(v for v in manifest["cases"] if v["case_id"] == link["case_id"])
        rows[case["case_id"]] = dict(deepcopy(original), case_id=case["case_id"],
            input_digest=b.digest(case), coverage_binding=case["coverage_binding"])
    return b.seal(dict(execution, cases=[rows[c["case_id"]] for c in manifest["cases"]]))


def status(manifest, record):
    """Identity/roster checks, not native execution or interval recomputation."""
    check_manifest(manifest)
    b.check_digest(record)
    b.require(record["schema"] == "p984c-cci-runtime-results-v1"
        and record["manifest_digest"] == manifest["record_digest"]
        and record["user_accepted"] is False and record["aggregate_closed"] is False, "runtime scope drift")
    execution = expand(record["execution"])
    b.check_digest(execution)
    b.require(execution["manifest_digest"] == manifest["record_digest"]
        and execution["native_runtime_executed"] is True
        and execution["user_accepted"] is False and execution["aggregate_closed"] is False, "execution scope drift")
    b.require(record["reuse"] == reuse_rows(manifest, execution["shared"]), "native reuse lineage drift")
    reused = {v["case_id"] for v in record["reuse"]}
    wanted = [v for v in manifest["cases"] if v["case_id"] not in reused]
    b.require([v["case_id"] for v in execution["cases"]] == [v["case_id"] for v in wanted], "native case roster drift")
    for case, row in zip(wanted, execution["cases"], strict=True):
        b.require(row["input_digest"] == b.digest(case)
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
            b.require(row["outcome"] == "incomplete_case" and row["first_failure"] is not None,
                "hidden native failure")
    passed = sum(v["case_passed"] for v in execution["cases"])
    return dict(family="C_CI", native_cases=len(wanted), passed_cases=passed,
        exact_reuse_cases=len(record["reuse"]), successful_history_cells=2*(passed+len(record["reuse"])),
        accepted_cells=0, native_trajectories_rerun=False, interval_equations_recomputed=False,
        cases=[{k: row[k] for k in ("case_id", "case_passed", "event_committed", "first_failure")} for row in execution["cases"]])


def check(manifest, record, *, numerics=False):
    summary = status(manifest, record)
    execution = materialize(manifest, record)
    ready = b.read(preparation.INPUTS)
    predictions = preparation.materialize(ready, b.read(preparation.RESULTS))
    for case, row, prepared in zip(manifest["cases"], execution["cases"], predictions, strict=True):
        if row["case_passed"]:
            b.require(row["predictions"] == prepared["predictions"], "prepared prediction drift")
            preparation.check_predictions(preparation.target_for(manifest, case), row["predictions"])
    checked = r.validate(manifest, execution, numerics=numerics)
    return {**summary, **checked, "cases_required": len(manifest["cases"])}


def run_case(args):
    payload, case = args
    with b.exact_backend(b.ExactBackend.FLINT):
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
    b.require(not b.Path(args.output).is_absolute() and ".." not in b.Path(args.output).parts, "repository-relative output required")
    if args.prepare:
        b.write_new(INPUTS, make_manifest())
        print("C_CI native boundary inputs frozen; no native execution")
        return
    manifest = b.read(INPUTS)
    check_manifest(manifest)
    if args.check_retained:
        with ExitStack() as stack:
            for module, name in ((r, "CandidateCIRoot"), (r, "ProvisionalCandidateCIStep"),
                (r.native, "GRC9V4CCIOperation"), (r.native, "ProvisionalCandidateCIStep")):
                stack.enter_context(patch.object(module, name, side_effect=AssertionError("native producer disabled")))
            print(json.dumps(check(manifest, b.read(args.output), numerics=args.recheck_numerics), indent=2))
        return
    b.require(not (b.ROOT / args.output).exists(), "refuse to overwrite execution")
    _, previous = preparation.predecessor()
    shared = previous["shared"]
    reuse = reuse_rows(manifest, shared)
    reused = {v["case_id"] for v in reuse}
    jobs = [(shared["actual_source"], case) for case in manifest["cases"] if case["case_id"] not in reused]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        rows = list(pool.map(run_case, jobs))
    execution = b.seal(dict(manifest_digest=manifest["record_digest"], shared=shared,
        cases=rows, native_runtime_executed=True, user_accepted=False, aggregate_closed=False))
    packed = compact(execution)
    b.require(expand(packed) == execution, "lossy native compaction")
    record = b.seal(dict(schema="p984c-cci-runtime-results-v1", manifest_digest=manifest["record_digest"],
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

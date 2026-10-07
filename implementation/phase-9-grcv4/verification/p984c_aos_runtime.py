"""Native A_OS boundary campaign against the separately accepted oracle.

Only --run executes trajectories. Retained checking reuses the accepted A_OS
consumer checker with new oracle data, not patched numerical producers.
"""

import argparse
from copy import deepcopy
from importlib.metadata import version
import json
import platform
from unittest.mock import patch

import p984b_aos_runtime as previous
import p984c_aos_oracle as oracle

base = previous.base
SELF = base.HERE + "p984c_aos_runtime.py"
TEST = base.HERE + "test_p984c_aos_runtime.py"
INPUTS = base.BASE + "P9-8.4c-AOSCases.json"
RESULTS = base.BASE + "P9-8.4c-AOSResults.json"
REVIEW = base.BASE + "P9-8.4c-AOSRuntimeReview.md"
ACCEPTANCE_SHA = "ac3b85a497a4828eb6c5dbf3ebe4683b833050790952d03b9022fef55c5c1ecf"
ORACLE_RESULT_DIGEST = "0228df9a34d714456a83b4042211608ded91902475cb9c3721b6c33e31f5ae4b"
PREVIOUS_ACCEPTANCE_SHA = "e731466f1ffed685a29281a7651a0db4508d7d63d50cb2e4ea85e8680cfd09c8"


def compact(value):
    """Intern exact repeated references and matrices; no rounding or pruning."""
    contexts = {}
    def visit(x):
        if isinstance(x, list):
            return [visit(v) for v in x]
        if not isinstance(x, dict):
            return x
        out = {}
        for key, item in x.items():
            if key in ("reference", "H1_form", "H", "regenerated", "base", "increment") and isinstance(item, (dict, list)):
                token = base.digest(item)
                contexts[token] = item
                out[key] = {"aos_boundary_context": token}
            else:
                out[key] = visit(item)
        return out
    payload = visit(value)
    return dict(contexts=contexts, payload=payload)


def expand(value):
    base.require(set(value) == {"contexts", "payload"}, "compact envelope fields")
    contexts, used = value["contexts"], set()
    for token, item in contexts.items():
        base.require(base.digest(item) == token, "context digest drift")
    def visit(x):
        if isinstance(x, list):
            return [visit(v) for v in x]
        if not isinstance(x, dict):
            return x
        if "aos_boundary_context" in x:
            token = x["aos_boundary_context"]
            base.require(set(x) == {"aos_boundary_context"} and token in contexts, "unknown context")
            used.add(token)
            return deepcopy(contexts[token])
        return {k: visit(v) for k, v in x.items()}
    result = visit(value["payload"])
    base.require(used == set(contexts), "unused retained context")
    return result


def accepted_oracle():
    base.require(base.sha((base.ROOT / oracle.REVIEW).read_bytes()) == ACCEPTANCE_SHA,
        "accepted boundary oracle review changed")
    inputs, results = base.read(oracle.INPUTS), base.read(oracle.RESULTS)
    oracle.check_manifest(inputs)
    base.check_digest(results)
    base.require(results["record_digest"] == ORACLE_RESULT_DIGEST
        and results["manifest_digest"] == inputs["record_digest"], "oracle result drift")
    # Recheck the old accepted prerequisite and G2; do not rewrite its records.
    previous.accepted_oracle()
    return inputs, oracle.materialize(inputs, results)


def make_manifest():
    accepted, _ = accepted_oracle()
    old = base.read(previous.INPUTS)
    base.check_bindings(old["source_bindings"])
    base.require(base.sha((base.ROOT / previous.REVIEW).read_bytes()) == PREVIOUS_ACCEPTANCE_SHA,
        "accepted D45 native review changed")
    old_oracle = base.read(previous.oracle.INPUTS)
    cases, reuse = [], []
    links = {r["case_id"]: r["previous_case_id"] for r in accepted["exact_reuse"]}
    for c in accepted["cases"]:
        case = dict(case_id=c["case_id"], fixture_id=c["fixture_id"],
            oracle_case_digest=base.digest(c), coverage_binding=c["coverage_binding"],
            target_steps_per_role=10, final_read_only=True, execution_budget_seconds=120)
        cases.append(case)
        if c["case_id"] in links:
            prior = next(v for v in old_oracle["cases"] if v["case_id"] == links[c["case_id"]])
            for key in ("request", "event_id", "event_identity_payload", "target", "comparison"):
                base.require(c[key] == prior[key], "D45 scientific oracle operand drift")
            old_case = next(v for v in old["cases"] if v["fixture_id"] == prior["fixture_id"])
            for key in ("target_steps_per_role", "final_read_only", "execution_budget_seconds"):
                base.require(case[key] == old_case[key], "D45 native schedule drift")
            reuse.append(dict(case_id=case["case_id"], previous_case_id=old_case["case_id"]))
    paths = {r["path"] for r in old["source_bindings"]} | {
        oracle.SELF, oracle.INPUTS, oracle.RESULTS, oracle.REVIEW,
        previous.INPUTS, previous.RESULTS, previous.REVIEW,
        SELF, TEST}
    return base.seal(dict(schema="p984c-aos-runtime-inputs-v1", source_bindings=base.bind(sorted(paths)),
        oracle_inputs_digest=accepted["record_digest"], oracle_results_digest=ORACLE_RESULT_DIGEST,
        acceptance=dict(path=oracle.REVIEW, sha256=ACCEPTANCE_SHA, scope="oracle_only"),
        initial_inputs=old["initial_inputs"], specialization=old["specialization"],
        source_steps=1, source_execution="one_shared_native_beat_then_detached_event_owners",
        cases=cases, exact_reuse=reuse, exact_backend="flint", public_support_widened=False,
        user_accepted=False, aggregate_closed=False))


def check_manifest(manifest):
    base.check_digest(manifest)
    base.check_bindings(manifest["source_bindings"])
    base.require(manifest == make_manifest(), "boundary native manifest drift")


def reuse_rows(manifest, shared):
    old = base.read(previous.RESULTS)
    base.check_digest(old)
    base.require(old["shared"]["actual_source"] == shared["actual_source"],
        "D45 native source is not exact reuse")
    accepted, _ = accepted_oracle()
    seed = previous.seed_from_payload(shared["actual_source"])
    rows = []
    for link in manifest["exact_reuse"]:
        row = next(r for r in old["cases"] if r["case_id"] == link["previous_case_id"])
        case = next(c for c in accepted["cases"] if c["case_id"] == link["case_id"])
        base.require(row["case_passed"] is True and row["event_committed"] is True
            and row["first_failure"] is None, "cannot reuse incomplete native evidence")
        base.require(row["actual_request"] == previous.fresh_request(seed, case).to_payload(),
            "D45 actual request/history is not exact reuse")
        rows.append(dict(**link, previous_record_digest=old["record_digest"],
            previous_row_digest=base.digest(row)))
    return rows


def materialize(manifest, record):
    execution = expand(record["execution"])
    base.check_digest(execution)
    rows = {r["case_id"]: r for r in execution["cases"]}
    old = base.read(previous.RESULTS)
    for link in record["reuse"]:
        original = next(r for r in old["cases"] if r["case_id"] == link["previous_case_id"])
        case = next(c for c in manifest["cases"] if c["case_id"] == link["case_id"])
        # Rebind only the coverage wrapper; all scientific/native bytes stay exact.
        rows[case["case_id"]] = dict(deepcopy(original), case_id=case["case_id"],
            input_digest=base.digest(case), coverage_binding=case["coverage_binding"])
    return base.seal(dict(execution, cases=[rows[c["case_id"]] for c in manifest["cases"]]))


def status(manifest, record):
    """Retained identities and roster only; no native or interval recomputation."""
    check_manifest(manifest)
    base.check_digest(record)
    base.require(record["schema"] == "p984c-aos-runtime-results-v1"
        and record["manifest_digest"] == manifest["record_digest"]
        and record["user_accepted"] is False and record["aggregate_closed"] is False,
        "runtime record scope drift")
    execution = expand(record["execution"])
    base.check_digest(execution)
    base.require(execution["manifest_digest"] == manifest["record_digest"]
        and execution["native_runtime_executed"] is True
        and execution["user_accepted"] is False and execution["aggregate_closed"] is False,
        "execution scope drift")
    reuse_ids = {r["case_id"] for r in manifest["exact_reuse"]}
    wanted = [c for c in manifest["cases"] if c["case_id"] not in reuse_ids]
    base.require([r["case_id"] for r in execution["cases"]] == [c["case_id"] for c in wanted],
        "missing/extra/reordered boundary cases")
    base.require(record["reuse"] == reuse_rows(manifest, execution["shared"]), "native reuse lineage drift")
    for case, row in zip(wanted, execution["cases"], strict=True):
        base.require(row["input_digest"] == base.digest(case) and row["coverage_binding"] == case["coverage_binding"]
            and row["user_accepted"] is False and row["aggregate_closed"] is False, "case scope/operand drift")
        success = row["outcome"] == "passed_named_case"
        base.require(row["case_passed"] is success, "event/case conflation")
        if success:
            base.require(row["event_committed"] is True and row["first_failure"] is None
                and [(r["role"], r["index"]) for r in row["continuation"]]
                == [(r, i) for r in oracle.previous.ROLES for i in range(1, 11)]
                and set(row["final_reads"]) == set(oracle.previous.ROLES), "false successful native case")
        else:
            base.require(row["outcome"] == "incomplete_case" and row["first_failure"] is not None,
                "incomplete native case lacks failure")
    passed = sum(r["case_passed"] for r in execution["cases"])
    return dict(family="A_OS", native_cases=len(wanted), passed_cases=passed,
        exact_reuse_cases=len(record["reuse"]), successful_history_cells=2*(passed+len(record["reuse"])),
        accepted_cells=0, native_trajectories_rerun=False, interval_equations_recomputed=False,
        cases=[{k: r[k] for k in ("case_id", "case_passed", "event_committed", "first_failure")} for r in execution["cases"]])


def check(manifest, record, *, numerics=False):
    summary = status(manifest, record)
    accepted = accepted_oracle()
    # Compatibility adapter supplies the new accepted data to the unchanged
    # scientific/lifecycle checker. No solver, current, capture or test is mocked.
    with patch.object(previous, "accepted_oracle", return_value=accepted):
        checked = previous.validate(manifest, materialize(manifest, record), numerics=numerics)
    return {**summary, **checked, "cases_required": 32}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--prepare", action="store_true")
    group.add_argument("--run", action="store_true")
    group.add_argument("--check-retained", action="store_true")
    parser.add_argument("--recheck-numerics", action="store_true")
    parser.add_argument("--output", default=RESULTS)
    args = parser.parse_args()
    base.require(not args.recheck_numerics or args.check_retained, "recheck requires retained mode")
    base.require(not base.Path(args.output).is_absolute() and ".." not in base.Path(args.output).parts,
        "repository-relative output required")
    if args.prepare:
        base.write_new(INPUTS, make_manifest())
        print("A_OS boundary native subjects bound to accepted oracle; no native execution")
        return
    manifest = base.read(INPUTS)
    check_manifest(manifest)
    if args.check_retained:
        print(json.dumps(check(manifest, base.read(args.output), numerics=args.recheck_numerics), indent=2))
        return
    base.require(not (base.ROOT / args.output).exists(), "refuse to overwrite native evidence")
    accepted, expected = accepted_oracle()
    rows = []
    with base.exact_backend(base.ExactBackend.FLINT):
        shared, seed = previous.run_source(manifest, expected)
        reuse = reuse_rows(manifest, shared)
        reused_ids = {r["case_id"] for r in reuse}
        for case, oracle_case, nominal in zip(manifest["cases"], accepted["cases"], expected["cases"], strict=True):
            if case["case_id"] in reused_ids:
                continue
            row = previous.execute_case(seed, case, oracle_case, nominal, expected["shared_observations"])
            rows.append(row)
            print(case["case_id"], row["outcome"], row["first_failure"], flush=True)
    execution = base.seal(dict(manifest_digest=manifest["record_digest"], shared=shared, cases=rows,
        native_runtime_executed=True, user_accepted=False, aggregate_closed=False))
    packed = compact(execution)
    base.require(expand(packed) == execution, "lossy native compaction")
    record = base.seal(dict(schema="p984c-aos-runtime-results-v1", manifest_digest=manifest["record_digest"],
        execution=packed, reuse=reuse, environment=dict(python=platform.python_version(),
            numpy=version("numpy"), mpmath=version("mpmath"), python_flint=version("python-flint")),
        user_accepted=False, aggregate_closed=False))
    base.require(len(json.dumps(record, indent=2).encode()) < 64_000_000, "native retention budget exceeded")
    base.write_new(args.output, record)
    report = status(manifest, record)
    print(json.dumps(report, indent=2))
    if report["successful_history_cells"] != 64:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

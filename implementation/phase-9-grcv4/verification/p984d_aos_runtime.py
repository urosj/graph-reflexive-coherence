"""Fresh native A_OS deep events and continuation against independent equations."""

import argparse
from concurrent.futures import ProcessPoolExecutor
import json
import lzma
from unittest.mock import patch

import p984b_aos_runtime as runtime
import p984c_aos_runtime as storage
import p984d_aos_oracle as oracle

b = oracle.b
SELF = b.HERE + "p984d_aos_runtime.py"
TEST = b.HERE + "test_p984d_aos_runtime.py"
INPUTS = b.BASE + "P9-8.4d-AOSCases.json"
RESULTS = b.BASE + "P9-8.4d-AOSResults.json.xz"


def oracle_data():
    m, r = oracle.read(oracle.INPUTS), oracle.read(oracle.RESULTS)
    status = oracle.check(m, r)
    b.require(status["oracle_cases_passed"] == 20, "independent deep prerequisite incomplete")
    return m, r


def make_manifest():
    m, r = oracle_data()
    prior = oracle.read(runtime.INPUTS)
    b.check_digest(prior)
    paths = {v["path"] for v in prior["source_bindings"]}
    paths |= {SELF, TEST, oracle.SELF, oracle.INPUTS, oracle.RESULTS,
              storage.SELF, runtime.SELF, runtime.CAPTURE}
    # Raw historical results may now exist only as their exact XZ archives.
    paths = {p if (b.ROOT / p).exists() else p + ".xz" for p in paths}
    return b.seal(dict(schema="p984d-aos-runtime-inputs-v1", family="A_OS",
        source_bindings=b.bind(paths), oracle_inputs_digest=m["record_digest"],
        oracle_results_digest=r["record_digest"], initial_inputs=prior["initial_inputs"],
        specialization=prior["specialization"], source_steps=1,
        cases=[dict(case_id=c["case_id"], fixture_id=c["fixture_id"],
                    oracle_case_digest=b.digest(c), coverage_binding=c["coverage_binding"],
                    target_steps_per_role=10, final_read_only=True,
                    execution_budget_seconds=600) for c in m["cases"]],
        exact_backend="flint", user_accepted=False, aggregate_closed=False))


def check_manifest(m):
    b.check_digest(m)
    b.check_bindings(m["source_bindings"])
    b.require(m == make_manifest(), "deep native declaration drift")


def execute(args):
    source, case, declared, expected, shared = args
    with b.exact_backend(b.ExactBackend.FLINT):
        return runtime.execute_case(runtime.seed_from_payload(source), case, declared, expected, shared)


def check(m, record, *, numerics=False):
    check_manifest(m)
    b.check_digest(record)
    b.require(record["schema"] == "p984d-aos-runtime-results-v1"
              and record["manifest_digest"] == m["record_digest"]
              and not record["user_accepted"] and not record["aggregate_closed"], "native scope drift")
    execution = storage.expand(record["execution"])
    # Supply declared data to the unchanged scientific consumer, never replace
    # a numerical producer, lifecycle operation or result.
    with patch.object(runtime, "accepted_oracle", return_value=oracle_data()):
        status = runtime.validate(m, execution, numerics=numerics)
    return dict(status, cases_required=20)


def run(m, workers):
    check_manifest(m)
    b.require(not (b.ROOT / RESULTS).exists(), "refuse overwrite")
    declared, expected = oracle_data()
    with b.exact_backend(b.ExactBackend.FLINT):
        shared, _ = runtime.run_source(m, expected)
    args = [(shared["actual_source"], case, oc, er, expected["shared_observations"])
            for case, oc, er in zip(m["cases"], declared["cases"], expected["cases"], strict=True)]
    first = next(a for a in args if a[1]["fixture_id"] == "P984D-D94-E1-P1")
    row = execute(first)
    print(row["case_id"], row["outcome"], row["first_failure"], flush=True)
    b.require(row["case_passed"], "deepest native prerequisite failed")
    rows = {row["case_id"]: row}
    with ProcessPoolExecutor(max_workers=workers) as pool:
        for row in pool.map(execute, [a for a in args if a != first]):
            rows[row["case_id"]] = row
            print(row["case_id"], row["outcome"], row["first_failure"], flush=True)
    execution = b.seal(dict(manifest_digest=m["record_digest"], shared=shared,
        cases=[rows[c["case_id"]] for c in m["cases"]], native_runtime_executed=True,
        user_accepted=False, aggregate_closed=False))
    compact = storage.compact(execution)
    b.require(storage.expand(compact) == execution, "lossy compaction")
    record = b.seal(dict(schema="p984d-aos-runtime-results-v1",
        manifest_digest=m["record_digest"], execution=compact, user_accepted=False, aggregate_closed=False))
    status = check(m, record)
    b.require(status["cases_passed"] == 20, "incomplete campaign; do not publish")
    with (b.ROOT / RESULTS).open("xb") as stream:
        stream.write(lzma.compress(json.dumps(record, separators=(",", ":"), allow_nan=False).encode() + b"\n"))
    return status


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("prepare", "run", "check"))
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--numerics", action="store_true")
    args = parser.parse_args()
    b.require(1 <= args.workers <= 4, "workers outside 1..4")
    b.require(not args.numerics or args.action == "check", "numerics requires check")
    if args.action == "prepare":
        b.write_new(INPUTS, make_manifest())
    elif args.action == "run":
        print(json.dumps(run(oracle.read(INPUTS), args.workers), indent=2))
    else:
        print(json.dumps(check(oracle.read(INPUTS), oracle.read(RESULTS), numerics=args.numerics), indent=2))

"""Independent A_OS deep expectations, using the existing paper/interval pair.

New inputs bind today's evaluator. Accepted source data remain historical
subjects; they are not relabeled as current native execution. Only ``run``
evaluates trajectories, and no mode grants user acceptance.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from contextlib import ExitStack
from copy import deepcopy
import json
import lzma
from unittest.mock import patch

import p984b_aos_oracle as equations
import p984c_aos_oracle as boundary
import p984d_cos as construction

b = equations.common
SELF = b.HERE + "p984d_aos_oracle.py"
TEST = b.HERE + "test_p984d_aos_oracle.py"
PLAN = b.BASE + "P9-AOS-Tranches8-9-Plan.md"
INPUTS = b.BASE + "P9-8.4d-AOSOracleInputs.json"
RESULTS = b.BASE + "P9-8.4d-AOSOracleResults.json.xz"
ROLES = equations.ROLES


def read(name):
    path = b.ROOT / name
    if not path.exists() and name.endswith(".json"):
        path = path.with_suffix(".json.xz")
    raw = path.read_bytes()
    return json.loads(lzma.decompress(raw) if path.suffix == ".xz" else raw)


def predecessor():
    # Exact accepted mathematical source, independent of later native kernels.
    raw = (b.ROOT / equations.aos.RECORD).read_bytes()
    b.require(b.sha(raw) == equations.OLD_ORACLE_SHA, "accepted A_OS source changed")
    old = json.loads(raw)
    b.check_digest(old)
    return old


def make_case(layout, old):
    source = deepcopy(old)
    source["request"]["resource_distribution"] = layout["shares"]
    case = equations.case_for(boundary.fixture(source["source"], layout), source,
                              {"record_digest": b.digest(construction.layouts())})
    case.update(case_id=layout["id"] + "::A_OS", fixture_id=layout["id"],
                execution_budget_seconds=600,
                changes_from_A1="declared deep layout and dyadic simplex; unchanged A_OS source, W, dt and equation budgets")
    case["mechanics"] = construction.mechanics(layout)
    return case


def make_manifest():
    old = predecessor()
    accepted = read(equations.INPUTS)
    b.check_digest(accepted)
    b.require(accepted["predecessor_record_digest"] == old["record_digest"], "source lineage")
    paths = {x["path"] for x in accepted["source_bindings"]}
    paths |= {SELF, TEST, PLAN, boundary.SELF, construction.SELF,
              "tests/models/test_grc_9_v4_expansion.py"}
    return b.seal(dict(schema="p984d-aos-oracle-inputs-v1", family="A_OS",
        source_bindings=b.bind(paths), shared=accepted["shared"],
        source_record_digest=old["record_digest"],
        cases=[make_case(layout, old) for layout in construction.layouts()],
        scope=dict(required_cases=20, required_history_cells=40, steps_per_role=10,
                   observations_per_case=22, maximum_core_depth=4,
                   maximum_target_vertices=23, successive_events=False,
                   uniform_trajectory_enclosure=False),
        native_runtime_executed=False, user_accepted=False, aggregate_closed=False))


def check_manifest(manifest):
    b.check_digest(manifest)
    b.check_bindings(manifest["source_bindings"])
    b.require(manifest == make_manifest(), "A_OS deep declaration drift")


def shared_observations():
    old = read(equations.RESULTS)
    b.check_digest(old)
    return old["shared_observations"]


def check(manifest, result, *, numerics=False):
    check_manifest(manifest)
    b.require(result["schema"] == "p984d-aos-oracle-results-v1"
              and result["aggregate_closed"] is False, "oracle scope drift")
    status = equations.validate(manifest, result, recheck_numerics=numerics)
    return dict(status, oracle_cases_required=20,
                independent_observations=sum(len(c["expectations"]) for c in result["cases"]))


def execute(case):
    with ExitStack() as stack:
        for producer in boundary.PRODUCERS:
            stack.enter_context(patch(producer, side_effect=AssertionError("native producer forbidden")))
        return equations.run_case(case)


def run(manifest, workers):
    check_manifest(manifest)
    b.require(not (b.ROOT / RESULTS).exists(), "refuse overwrite")
    cases = manifest["cases"]
    # Most demanding declared subject first. A failure is evidence, not success.
    first = next(c for c in cases if c["fixture_id"] == "P984D-D94-E1-P1")
    row = execute(first)
    print(row["case_id"], row["outcome"], row["first_failure"], flush=True)
    b.require(row["outcome"] == "passed_bounded_oracle", "deepest prerequisite failed; inspect before campaign")
    rows = {row["case_id"]: row}
    with ProcessPoolExecutor(max_workers=workers) as pool:
        for row in pool.map(execute, [c for c in cases if c != first]):
            rows[row["case_id"]] = row
            print(row["case_id"], row["outcome"], row["first_failure"], flush=True)
    result = b.seal(dict(schema="p984d-aos-oracle-results-v1",
        manifest_digest=manifest["record_digest"], shared_observations=shared_observations(),
        cases=[rows[c["case_id"]] for c in cases], native_runtime_executed=False,
        user_accepted=False, aggregate_closed=False))
    status = check(manifest, result)
    b.require(status["oracle_cases_passed"] == 20, "incomplete oracle campaign; do not publish")
    raw = json.dumps(result, separators=(",", ":"), allow_nan=False).encode() + b"\n"
    with (b.ROOT / RESULTS).open("xb") as stream:
        stream.write(lzma.compress(raw))
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
        print(json.dumps(run(read(INPUTS), args.workers), indent=2))
    else:
        print(json.dumps(check(read(INPUTS), read(RESULTS), numerics=args.numerics), indent=2))

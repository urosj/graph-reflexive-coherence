"""A_CI independent joint-root expectations on the twenty deep single-event layouts.

No native events, roots or steps. The largest target is evaluated first and its
result reused, not rerun. Review this oracle scope before native execution.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from copy import deepcopy
import json

import p984c_aci_oracle as previous
import p984c_aci_runtime as predecessor_runtime
import p984d_cos as construction

b = previous.b
SELF = b.HERE + "p984d_aci_oracle.py"
TEST = b.HERE + "test_p984d_aci_oracle.py"
INPUTS = b.BASE + "P9-8.4d-ACIOracleInputs.json"
RESULTS = b.BASE + "P9-8.4d-ACIOracleResults.json"
REVIEW = b.BASE + "P9-8.4d-ACIOracleReview.md"
ACCEPTANCE_SHA = "b83315cc8715b8ef8c6fd09bed32e3108abd50f48b4f1c86bbb1b54fea3512af"
ROLES = previous.previous.ROLES


def make_manifest():
    old = b.read(predecessor_runtime.INPUTS)
    b.check_digest(old)
    b.check_bindings(old["source_bindings"])
    review = (b.ROOT / predecessor_runtime.REVIEW).read_bytes()
    b.require(b.sha(review) == ACCEPTANCE_SHA and b"## Scoped user acceptance" in review,
        "A_CI predecessor acceptance drift")
    layouts = construction.layouts()
    cases = []
    for layout in layouts:
        template = deepcopy(next(c for c in old["cases"] if
            c["request"]["module_chirality"] == layout["chirality"]
            and c["request"]["growth_phase"] == 1))
        template["oracle"]["event_identity"]["resource_distribution"] = layout["shares"]
        case = deepcopy(template)
        case.update(case_id=layout["id"] + "::A_CI", fixture_id=layout["id"],
            subject_kind="independent_deep_expectation_not_native_event",
            coverage_binding=dict(record_digest=b.digest(layouts),
                cell_ids=[layout["id"] + "::A_CI::" + role for role in ROLES]),
            execution_budget_seconds=1800)
        case["request"].update(target_effective_degree=layout["degree"],
            module_chirality=layout["chirality"], growth_phase=layout["phase"],
            resource_distribution=layout["shares"], operation_id="p984d-aci-" + layout["id"])
        case["oracle"] = construction.previous.target_oracle(old["expected_source"], template, case["request"], layout)
        case["mechanics"] = construction.mechanics(layout)
        cases.append(case)
    paths = {v["path"] for v in old["source_bindings"]} | {
        SELF, TEST, previous.SELF, predecessor_runtime.SELF,
        predecessor_runtime.INPUTS, predecessor_runtime.REVIEW,
        construction.SELF, construction.previous.SELF}
    return b.seal(dict(schema="p984d-aci-oracle-inputs-v1", family="A_CI",
        source_bindings=b.bind(sorted(paths)), expected_source=old["expected_source"],
        predecessor_digest=old["record_digest"], source_reused=True,
        layouts=layouts, cases=cases,
        scope=dict(required_cases=20, history_roles=40, nominal_steps_per_role=10,
            entry_reads_per_role=11, maximum_target_vertices=23, maximum_core_depth=4,
            retention_budget_bytes=64_000_000, successive_events=False, arbitrary_depth=False,
            trajectory_error_tube=False),
        runtime_gate="review_deep_A_CI_oracle_before_native_execution",
        native_runtime_executed=False, user_accepted=False, aggregate_closed=False))


def check_manifest(manifest):
    b.check_digest(manifest)
    b.check_bindings(manifest["source_bindings"])
    b.require(manifest == make_manifest(), "deep A_CI oracle subject/law/budget drift")


def status(manifest, record):
    check_manifest(manifest)
    b.check_digest(record)
    b.require(record["schema"] == "p984d-aci-oracle-results-v1"
        and record["manifest_digest"] == manifest["record_digest"]
        and all(record[k] is False for k in ("native_runtime_executed", "user_accepted", "aggregate_closed")),
        "oracle scope drift")
    b.require([v["case_id"] for v in record["cases"]] == [v["case_id"] for v in manifest["cases"]],
        "oracle roster drift")
    for case, row in zip(manifest["cases"], record["cases"], strict=True):
        b.require(row["input_digest"] == b.digest(case)
            and all(row[k] == 0 for k in ("native_steps", "native_roots", "topology_events", "runtime_cells_closed")),
            "false native credit/input drift")
        b.require(row["outcome"] == "passed_bounded_oracle" and row["first_failure"] is None
            and len(row["observations"]) == 22, "incomplete oracle; no native readiness credit")
    return dict(family="A_CI", status="oracle_pending_review", cases_required=20,
        passed_cases=20, independent_observations=440, native_steps=0, native_roots=0,
        topology_events=0, runtime_cells_closed=0, user_accepted=False, aggregate_closed=False,
        native_trajectories_rerun=False, interval_equations_recomputed=False)


def check(manifest, record, *, numerics=False):
    summary = status(manifest, record)
    for case, row in zip(manifest["cases"], record["cases"], strict=True):
        target = previous.target_for(manifest, case)
        b.require(row["target_digest"] == b.digest(target.to_payload()), "target binding drift")
        b.require([(v["role"], v["index"], v["stage"]) for v in row["observations"]]
            == [(role, i, "nominal_update" if i <= 10 else "final_entry_read_with_hypothetical_update")
                for role in ROLES for i in range(1, 12)], "oracle schedule drift")
        for role in ROLES:
            state = getattr(target.inputs, role)
            entry = dict(C=list(state.C), W_A=list(state.W_A))
            for value in (v for v in row["observations"] if v["role"] == role):
                previous.check_observation(case["oracle"]["target_graph"], entry, value, numerics=numerics)
                entry = {k: value["output"][k] for k in ("C", "W_A")}
    return dict(summary, retained_integrity="passed", interval_equations_recomputed=numerics)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--prepare", action="store_true")
    mode.add_argument("--run-oracle", action="store_true")
    mode.add_argument("--check-retained", action="store_true")
    parser.add_argument("--recheck-numerics", action="store_true")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--output", default=RESULTS)
    args = parser.parse_args()
    b.require(1 <= args.workers <= 4, "workers outside 1..4")
    b.require(not args.recheck_numerics or args.check_retained, "recheck requires retained mode")
    b.require(not b.Path(args.output).is_absolute() and ".." not in b.Path(args.output).parts,
        "repository-relative output required")
    if args.prepare:
        b.write_new(INPUTS, make_manifest())
        print("20 deep A_CI oracle subjects frozen; no native execution")
        return
    manifest = b.read(INPUTS)
    check_manifest(manifest)
    if args.check_retained:
        print(json.dumps(check(manifest, b.read(args.output), numerics=args.recheck_numerics), indent=2))
        return
    b.require(not (b.ROOT / args.output).exists(), "refuse to overwrite evidence")
    first = next(c for c in manifest["cases"] if "D94-E1-P1" in c["case_id"])
    initial = previous.execute_case((manifest, first))
    rows = {first["case_id"]: initial}
    if initial["outcome"] == "passed_bounded_oracle":
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            for row in pool.map(previous.execute_case,
                    [(manifest, c) for c in manifest["cases"] if c != first]):
                rows[row["case_id"]] = row
    record = b.seal(dict(schema="p984d-aci-oracle-results-v1", manifest_digest=manifest["record_digest"],
        cases=[rows[c["case_id"]] for c in manifest["cases"] if c["case_id"] in rows],
        native_runtime_executed=False, user_accepted=False, aggregate_closed=False))
    b.require(len(json.dumps(record).encode()) < manifest["scope"]["retention_budget_bytes"], "retention budget")
    b.write_new(args.output, record)
    print(json.dumps(check(manifest, record), indent=2))


if __name__ == "__main__":
    main()

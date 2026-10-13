"""A_PC deep-event gate with graph-specific carrier bounds and retained failures.

Reuses unchanged native producers and scientific checks. Only input binding is
adapted; existing per-case independent preflight is unchanged. No successive-event
or sibling credit.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from copy import deepcopy
from importlib.metadata import version
import json
import platform

import p984d_cos as construction
import p984c_apc_runtime as previous

r, b = previous.r, previous.b
SELF = b.HERE + "p984d_apc_runtime.py"
TEST = b.HERE + "test_p984d_apc_runtime.py"
INPUTS = b.BASE + "P9-8.4d-APCCases.json"
RESULTS = b.BASE + "P9-8.4d-APCResults.json"
REVIEW = b.BASE + "P9-8.4d-APCRuntimeReview.md"
PRESSURE = b.BASE + "P9-8.4d-APCPreflightPressure.json"
ACCEPTANCE_SHA = "cefe1d6e94b81c6797e8f5828ff9e6d78c2daa1f1c347a52ecaf5efebabd8c15"


def predecessor():
    old = b.read(previous.INPUTS)
    b.check_digest(old)
    b.check_bindings(old["source_bindings"])
    review = (b.ROOT / previous.REVIEW).read_bytes()
    b.require(b.sha(review) == ACCEPTANCE_SHA and b"## Scoped user acceptance" in review,
        "accepted A_PC boundary review drift")
    _, result = previous.predecessor()
    b.require(result["shared"]["actual_source"] == old["expected_source"], "source reuse drift")
    return old, result["shared"]


def make_manifest():
    old, shared = predecessor()
    layouts = construction.layouts()
    cases = []
    for layout in layouts:
        template = deepcopy(next(c for c in old["cases"] if
            c["request"]["module_chirality"] == layout["chirality"]
            and c["request"]["growth_phase"] == 1))
        template["oracle"]["event_identity"]["resource_distribution"] = layout["shares"]
        case = deepcopy(template)
        case.update(case_id=layout["id"] + "::A_PC", fixture_id=layout["id"],
            subject_kind="native_boundary_companion",
            changes_from_frozen=["deep_layout_resource_shares_and_event_identity_only"],
            coverage_binding=dict(record_digest=b.digest(layouts),
                cell_ids=[layout["id"] + "::A_PC::" + role for role in r.ROLES]),
            execution_budget_seconds=1800)
        case["request"].update(target_effective_degree=layout["degree"],
            module_chirality=layout["chirality"], growth_phase=layout["phase"],
            resource_distribution=layout["shares"], operation_id="p984d-apc-" + layout["id"])
        case["oracle"] = construction.previous.target_oracle(old["expected_source"], template, case["request"], layout)
        case["mechanics"] = construction.mechanics(layout)
        case["independent_whole_chart"] = r.oracle.whole_chart(case["oracle"]["target_graph"])
        cases.append(case)
    paths = {v["path"] for v in old["source_bindings"]} | {
        SELF, TEST, previous.SELF, previous.INPUTS, previous.REVIEW,
        r.RESULTS, construction.SELF, construction.previous.SELF}
    return b.seal(dict(schema="p984d-apc-runtime-inputs-v1", family="A_PC",
        source_bindings=b.bind(sorted(paths)), initial_inputs=old["initial_inputs"],
        nominal_source=old["nominal_source"], expected_source=old["expected_source"],
        cases=cases, layouts=layouts, source_reused=True,
        source_execution=dict(new_source_steps=0, path=r.RESULTS, shared_digest=b.digest(shared)),
        scope=dict(required_cases=20, required_history_cells=40, target_beats_per_role=10,
            successive_events=False, arbitrary_depth=False, retention_budget_bytes=64_000_000),
        user_accepted=False, aggregate_closed=False))


def check_manifest(manifest):
    b.check_digest(manifest)
    b.check_bindings(manifest["source_bindings"])
    b.require(manifest == make_manifest(), "deep A_PC native subject/law/budget drift")


def status(manifest, record):
    check_manifest(manifest)
    b.check_digest(record)
    b.require(record["schema"] == "p984d-apc-runtime-results-v1"
        and record["manifest_digest"] == manifest["record_digest"]
        and record["user_accepted"] is False and record["aggregate_closed"] is False,
        "runtime scope drift")
    execution = previous.expand(record["execution"])
    b.check_digest(execution)
    native = any("event" in row for row in execution["cases"])
    b.require(execution["manifest_digest"] == manifest["record_digest"]
        and execution["native_runtime_executed"] is native
        and execution["user_accepted"] is False and execution["aggregate_closed"] is False,
        "execution scope drift")
    _, shared = predecessor()
    b.require(execution["shared"] == shared, "source execution drift")
    rows = execution["cases"]
    pilot = next(c for c in manifest["cases"] if "D94-E-1-P3" in c["case_id"])
    halted = len(rows) == 1 and rows[0]["case_id"] == pilot["case_id"] and not rows[0]["case_passed"]
    expected = [pilot] if halted else manifest["cases"]
    b.require([v["case_id"] for v in rows] == [c["case_id"] for c in expected], "case roster drift")
    for case, row in zip(expected, rows, strict=True):
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
            if row["first_failure"]["stage"] == "independent_preflight":
                b.require(row["event_committed"] is False and "event" not in row
                    and row["continuation"] == [] and row["final_reads"] == {},
                    "preflight rejection cannot confer native credit")
    passed = sum(v["case_passed"] for v in rows)
    return dict(family="A_PC", status="implemented_pending_acceptance" if passed == 20 else "incomplete_campaign",
        native_cases=sum("event" in row for row in rows), attempted_cases=len(rows),
        unattempted_cases=20-len(rows), cases_required=20,
        passed_cases=passed, required_cells=40, successful_history_cells=2*passed,
        accepted_cells=0, passing_pending_cells=2*passed, target_steps=sum(len(v["continuation"]) for v in rows),
        final_reads=sum(len(v["final_reads"]) for v in rows), degrees=[59,66,73,94], maximum_core_depth=4,
        native_trajectories_rerun=False, interval_equations_recomputed=False,
        successive_events=False, arbitrary_depth=False, user_accepted=False, aggregate_closed=False,
        failures=[{k: row[k] for k in ("case_id", "event_committed", "first_failure")} for row in rows if not row["case_passed"]])


def check(manifest, record, *, numerics=False):
    summary = status(manifest, record)
    execution = previous.expand(record["execution"])
    if summary["unattempted_cases"]:
        row = execution["cases"][0]
        b.require(row["first_failure"]["stage"] == "independent_preflight"
            and row["first_failure"]["message"] == "negative next resource",
            "unresolved partial campaign; no supported retained check")
        if numerics:
            seed = r.state(execution["shared"]["actual_source"])
            try:
                r.preflight(r.independent_target(seed, row["actual_case"]))
            except ValueError as error:
                b.require(str(error) == "negative next resource", "preflight failure changed")
            else:
                raise ValueError("retained exclusion no longer reproduced")
        return dict(summary, retained_integrity="passed", numerical_case_status="failed_preflight",
            interval_equations_recomputed=numerics)
    with previous.data_adapter(manifest):
        checked = r.validate(manifest, execution, numerics=numerics)
    if numerics:
        seed = r.state(execution["shared"]["actual_source"])
        for case, row in zip(manifest["cases"], execution["cases"], strict=True):
            if row["case_passed"]:
                b.require(row["predictions"] == r.preflight(r.independent_target(seed, case)),
                    "independent nominal prediction drift")
    b.require(checked["cases_passed"] == summary["passed_cases"], "consumer/summary mismatch")
    return dict(summary, retained_integrity="passed", interval_equations_recomputed=numerics)


def preflight_pressure(manifest):
    """Two declared D94 controls, both roles, at most two independent updates.

    A zero first update at depth four is not strict positivity. Full enabled
    interval equations, not the exploratory baseline stencil, decide exclusion.
    No native producer is used and no successful family cells are credited.
    """
    case = next(c for c in manifest["cases"] if "D94-E-1-P3" in c["case_id"])
    seed = r.state(manifest["expected_source"])
    samples = []
    for label, shares in (("original", case["request"]["resource_distribution"]),
            ("balanced_control_not_successor", [21/64, 21/64, 22/64])):
        declared = deepcopy(case)
        if label != "original":
            layout = deepcopy(next(v for v in manifest["layouts"] if v["id"] == case["fixture_id"]))
            layout["shares"] = shares
            declared["request"].update(resource_distribution=shares,
                operation_id=case["request"]["operation_id"] + "-balanced-control")
            declared["oracle"]["event_identity"]["resource_distribution"] = shares
            declared["oracle"] = construction.previous.target_oracle(
                manifest["expected_source"], declared, declared["request"], layout)
        target = r.independent_target(seed, declared)
        graph = declared["oracle"]["target_graph"]
        paper = r.oracle.PaperAPC(graph)
        high = r.oracle.IntervalRows(r.oracle.model_for(graph))
        for role in r.ROLES:
            state = getattr(target.inputs, role)
            c, w, z = list(state.C), list(state.W_A), list(state.Z_4)
            for index in (1, 2):
                output = paper.step(c, w, z)
                ci, wi = r.oracle.vector(c), r.oracle.vector(w)
                zi = r.oracle.IV.matrix(r.np.asarray(z).reshape(len(w), len(w)).tolist())
                h = high.I + r.oracle.number(r.oracle.KAPPA_H) * zi
                read = high.read("A", ci, wi, h)
                cn = ci - r.oracle.number(b.DT) * high.B * read["J"]
                intervals = [[str(r.oracle.endpoint(x, side)) for side in (0, 1)] for x in cn]
                excluded = [graph["live_node_ids"][j] for j, pair in enumerate(intervals) if r.Q(pair[1]) < 0]
                error = None
                try:
                    r.oracle.check_step(graph, c, w, z, output)
                except ValueError as caught:
                    error = str(caught)
                b.require((error == "negative next resource") if excluded else error is None,
                    "preflight pressure has a different or unresolved failure")
                samples.append(dict(control=label, role=role, index=index,
                    request=declared["request"], graph=graph,
                    entry=dict(C=c, W_A=w, Z_4=z), output=output,
                    resource_intervals=intervals, excluded_nodes=excluded,
                    outcome="negative_resource_certified" if excluded else "passed_pointwise_step",
                    first_failure=error))
                if excluded:
                    break
                c, w, z = output["C"], output["W_A"], output["Z_4"]
    return b.seal(dict(schema="p984d-apc-preflight-pressure-v1",
        manifest_digest=manifest["record_digest"], samples=samples,
        native_steps=0, topology_events=0, runtime_cells_closed=0,
        general_infeasibility_proved=False, user_accepted=False, aggregate_closed=False))


def check_pressure(manifest, record, *, numerics=False):
    b.check_digest(record)
    b.require(record["schema"] == "p984d-apc-preflight-pressure-v1"
        and record["manifest_digest"] == manifest["record_digest"]
        and all(record[k] == 0 for k in ("native_steps", "topology_events", "runtime_cells_closed"))
        and all(record[k] is False for k in ("general_infeasibility_proved", "user_accepted", "aggregate_closed")),
        "pressure scope drift")
    expected = [("original", "current", 1), ("original", "reset", 1), ("original", "reset", 2),
        ("balanced_control_not_successor", "current", 1), ("balanced_control_not_successor", "current", 2),
        ("balanced_control_not_successor", "reset", 1), ("balanced_control_not_successor", "reset", 2)]
    b.require([(v["control"],v["role"],v["index"]) for v in record["samples"]] == expected,
        "pressure schedule drift")
    for row in record["samples"]:
        bounds = [(r.Q(a),r.Q(z)) for a,z in row["resource_intervals"]]
        b.require(len(bounds) == len(row["graph"]["live_node_ids"])
            and all(a <= z for a,z in bounds), "invalid resource intervals")
        nodes = [row["graph"]["live_node_ids"][j] for j,(a,z) in enumerate(bounds) if z < 0]
        b.require(nodes == row["excluded_nodes"] and row["outcome"] ==
            ("negative_resource_certified" if nodes else "passed_pointwise_step")
            and row["first_failure"] == ("negative next resource" if nodes else None), "exclusion drift")
    b.require([(v["control"],v["role"],v["index"]) for v in record["samples"] if v["excluded_nodes"]]
        == [("original", "current", 1), ("balanced_control_not_successor", "current", 2)],
        "lost negative control")
    if numerics:
        b.require(record == preflight_pressure(manifest), "pressure equation/operand drift")
    return dict(controls=2, independent_pointwise_steps=7, certified_exclusions=2,
        native_steps=0, runtime_cells_closed=0, general_infeasibility_proved=False,
        interval_equations_recomputed=numerics)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--prepare", action="store_true")
    group.add_argument("--run", action="store_true")
    group.add_argument("--check-retained", action="store_true")
    group.add_argument("--pressure", action="store_true")
    parser.add_argument("--recheck-numerics", action="store_true")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--output", default=RESULTS)
    args = parser.parse_args()
    b.require(1 <= args.workers <= 4, "workers outside 1..4")
    b.require(not args.recheck_numerics or args.check_retained, "recheck requires retained mode")
    b.require(not b.Path(args.output).is_absolute() and ".." not in b.Path(args.output).parts, "relative output required")
    if args.prepare:
        b.write_new(INPUTS, make_manifest())
        print("20 native A_PC deep subjects with graph-specific carrier bounds")
        return
    manifest = b.read(INPUTS)
    check_manifest(manifest)
    if args.pressure:
        value = preflight_pressure(manifest)
        b.write_new(PRESSURE, value)
        print(json.dumps(check_pressure(manifest, value), indent=2))
        return
    if args.check_retained:
        report = check(manifest, b.read(args.output), numerics=args.recheck_numerics)
        report["pressure"] = check_pressure(manifest, b.read(PRESSURE), numerics=args.recheck_numerics)
        print(json.dumps(report, indent=2))
        return
    b.require(not (b.ROOT / args.output).exists(), "refuse to overwrite execution")
    _, shared = predecessor()
    # The largest topology goes first; each case's independent interval preflight
    # precedes its native event. No new solver or chart theorem is introduced.
    first = next(c for c in manifest["cases"] if "D94-E-1-P3" in c["case_id"])
    initial = previous.run_case((manifest, shared, first))
    rows_by_id = {first["case_id"]: initial}
    if initial["case_passed"]:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            for row in pool.map(previous.run_case,
                    [(manifest, shared, case) for case in manifest["cases"] if case != first]):
                rows_by_id[row["case_id"]] = row
    rows = [rows_by_id[c["case_id"]] for c in manifest["cases"] if c["case_id"] in rows_by_id]
    execution = b.seal(dict(manifest_digest=manifest["record_digest"], shared=shared, cases=rows,
        native_runtime_executed=any("event" in row for row in rows), user_accepted=False, aggregate_closed=False))
    packed = previous.compact(execution)
    b.require(previous.expand(packed) == execution, "lossy compaction")
    record = b.seal(dict(schema="p984d-apc-runtime-results-v1", manifest_digest=manifest["record_digest"],
        execution=packed, environment=dict(python=platform.python_version(), numpy=version("numpy"),
            mpmath=version("mpmath"), python_flint=version("python-flint"), workers=args.workers),
        user_accepted=False, aggregate_closed=False))
    b.require(len(json.dumps(record,indent=2).encode()) < manifest["scope"]["retention_budget_bytes"], "retention budget")
    b.write_new(args.output, record)
    if len(rows) != len(manifest["cases"]):
        print(json.dumps(dict(status="halted_first_case", failure=initial["first_failure"]), indent=2))
        raise SystemExit(1)
    report = check(manifest, record)
    print(json.dumps(report, indent=2))
    if report["passed_cases"] != 20:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

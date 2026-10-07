"""Independent A_CI boundary expectations before new native event scope.

Thirty new layouts use the accepted paper CI and independent interval equations.
Two D45 target subjects reuse exact accepted native evidence, not new oracle runs.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from contextlib import ExitStack
from copy import deepcopy
from fractions import Fraction as Q
import json
from unittest.mock import patch

import p984b_aci_runtime as previous
import p984c_cos as construction
import prepare_p984c_boundaries as boundary

b, oracle = previous.b, previous.oracle
SELF = b.HERE + "p984c_aci_oracle.py"
TEST = b.HERE + "test_p984c_aci_oracle.py"
INPUTS = b.BASE + "P9-8.4c-ACIOracleInputs.json"
RESULTS = b.BASE + "P9-8.4c-ACIOracleResults.json"
REVIEW = b.BASE + "P9-8.4c-ACIOracleReview.md"
ACCEPTANCE_SHA = "db5e7ef7529bd2412df49f7db6f1b153d1787737f9e19118f54a4ff07cb84003"
PRODUCERS = (
    "pygrc.models.grc_v4_candidate_a.CandidateACurrent",
    "pygrc.models.grc_v4_ci.CandidateCIRoot",
    "pygrc.models.grc_v4_ci.ProvisionalCandidateCIStep",
    "pygrc.models.grc_9_v4_expansion.GRC9V4ExpansionPlan",
    "pygrc.models.grc_9_v4_lifecycle.GRC9V4ACIOperation",
    "p984b_aci_runtime.CandidateCIRoot",
    "p984b_aci_runtime.ProvisionalCandidateCIStep",
)


def predecessor():
    b.require(b.sha((b.ROOT / previous.REVIEW).read_bytes()) == ACCEPTANCE_SHA,
        "A_CI predecessor acceptance drift")
    manifest, result = b.read(previous.INPUTS), b.read(previous.RESULTS)
    b.check_digest(manifest)
    b.check_bindings(manifest["source_bindings"])
    b.check_digest(result)
    b.require(result["manifest_digest"] == manifest["record_digest"]
        and len(result["cases"]) == 16 and all(v["case_passed"] for v in result["cases"]),
        "incomplete A_CI predecessor")
    previous.predecessor()
    return manifest, result


def make_manifest():
    old, result = predecessor()
    source = result["shared"]["actual_source"]
    contract = b.read(boundary.OUTPUT)
    b.check_digest(contract)
    family = next(v for v in contract["families"] if v["family"] == "A_CI")
    cases, reuse = [], []
    for layout in contract["layouts"]:
        original = next(v for v in result["cases"] if
            (v["actual_case"]["request"]["target_effective_degree"],
             v["actual_case"]["request"]["module_chirality"],
             v["actual_case"]["request"]["growth_phase"])
            == (45 if layout["degree"] == 45 else 31, layout["chirality"], layout["phase"]))
        template = original["actual_case"]
        case = deepcopy(template)
        case.update(case_id=layout["id"] + "::A_CI", fixture_id=layout["id"],
            subject_kind="independent_boundary_expectation_not_native_event",
            coverage_binding=dict(record_digest=contract["record_digest"],
                cell_ids=[layout["id"] + "::A_CI::" + role for role in previous.ROLES]))
        case["request"]["target_effective_degree"] = layout["degree"]
        if layout["degree"] != 45:
            case["request"]["operation_id"] = "p984c-aci-" + layout["id"]
        case["oracle"] = construction.target_oracle(source, template, case["request"], layout)
        recipe = next(v for v in contract["cases"] if v["id"] == case["case_id"])["request_recipe"]
        b.require(case["request"]["resource_distribution"] == recipe["resource_distribution"], "boundary shares drift")
        b.require(case["comparison"] == family["comparison"]
            and case["execution_budget_seconds"] == family["execution_budget_seconds"], "boundary budgets drift")
        if layout["degree"] == 45:
            for key in ("request", "oracle", "comparison", "schedule", "execution_budget_seconds"):
                b.require(case[key] == template[key], "D45 exact reuse drift: " + key)
            reuse.append(dict(case_id=case["case_id"], previous_case_id=original["case_id"]))
        cases.append(case)
    paths = {v["path"] for v in old["source_bindings"]} | {
        previous.INPUTS, previous.RESULTS, previous.REVIEW, construction.SELF,
        boundary.OUTPUT, SELF, TEST, "tests/models/test_grc_9_v4_expansion.py"}
    return b.seal(dict(schema="p984c-aci-oracle-inputs-v1", family="A_CI",
        source_bindings=b.bind(sorted(paths)), expected_source=source, cases=cases,
        exact_reuse=reuse, boundary_digest=contract["record_digest"],
        predecessor_digest=result["record_digest"], source_reused=True,
        runtime_gate="review_new_A_oracle_scope_before_native_boundary_execution",
        native_runtime_executed=False, user_accepted=False, aggregate_closed=False))


def check_manifest(manifest):
    b.check_digest(manifest)
    b.check_bindings(manifest["source_bindings"])
    b.require(manifest == make_manifest(), "A_CI boundary oracle manifest drift")


def target_for(manifest, case):
    seed = previous.state(manifest["expected_source"])
    target = previous.independent_target(seed, case)
    source_graph = seed.inputs.geometry.reference.graph
    graph = target.inputs.geometry.reference.graph
    b.require(target.inputs.current != target.inputs.reset, "lost distinct history roles")
    for role in previous.ROLES:
        old, new = getattr(seed.inputs, role), getattr(target.inputs, role)
        history = dict(zip(source_graph.live_edge_ids, old.W_A, strict=True))
        b.require(sum(map(Q, old.C)) == sum(map(Q, new.C)) and min(new.C) >= 0,
            "resource transport drift")
        b.require(new.Z_4 is None and new.W_A == tuple(history.get(e,
            seed.specialization.resolved["expansion"]["bond_seed"]) for e in graph.live_edge_ids),
            "history lineage/seed drift")
    return target


def produce(paper, c, w):
    output = paper.step(c, w)
    h, read = paper.root(c, w)
    causal = paper.mp.matrix([(paper.mp.mpf(weight)-g)/(paper.mp.mpf(weight)+g)*j/16
        for weight, g, j in zip(w, read["drive"], read["current"], strict=True)])
    output["readback"] = list(map(float, causal))
    output["flat"] = list(map(float, paper.mp.lu_solve(h, causal)))
    return output


def certificate(graph, entry, output):
    checked = oracle.check_step(graph, entry["C"], entry["W_A"], output)
    truth = checked["truth"]
    bounds = {k: str(v) for k, v in truth["certificate"].items()}
    for name, key in (("current", "J"), ("baseline", "baseline"), ("source", "source")):
        error = (oracle.numerical.matrix_error(oracle.np.array(output[name]), truth["read"][key])
            if name == "source" else oracle.full_error(output[name], truth["read"][key]))
        bounds[name + "_error"] = str(error)
    drive = truth["high"].conductance(truth["c"], truth["w"], truth["read"]["baseline"])
    causal = oracle.IV.matrix([(w-g)/(w+g)*j/16
        for w, g, j in zip(truth["w"], drive, truth["read"]["J"], strict=True)])
    for name, exact in (("readback", causal), ("flat", oracle.inverse(truth["H"]) * causal),
            ("resource", checked["C"]), ("history", checked["W_A"])):
        field = {"resource": "C", "history": "W_A"}.get(name, name)
        bounds[name + "_error"] = str(oracle.full_error(output[field], exact))
    value = dict(input_digest=b.digest(dict(graph=graph, **entry)), output_digest=b.digest(output),
        selected_joint_point_digest=b.digest(dict(H=output["H"], J=output["current"])),
        bounds=bounds, domain=checked["domain"],
        C_lower=str(min(oracle.endpoint(x, 0) for x in checked["C"])),
        W_lower=str(min(oracle.endpoint(x, 0) for x in checked["W_A"])))
    check_certificate(value)
    return value


def check_certificate(value):
    bounds, domain = value["bounds"], value["domain"]
    b.require(all(0 <= Q(bounds[k]) < limit for k, limit in previous.LIMITS.items()), "oracle error ceiling")
    b.require(0 <= Q(bounds["joint_residual"]) <= Q(oracle.TOLERANCE)
        and 0 <= Q(bounds["contraction"]) < 1, "joint root not admitted")
    b.require(domain["norm"] == "frobenius" and Q(domain["radius"]) == Q(oracle.RADIUS)
        and 0 <= Q(domain["displacement_upper"]) <= Q(oracle.RADIUS)
        and 0 <= Q(domain["contraction_upper"]) < 1 and domain["floor_chart"] == "inactive"
        and Q(domain["current_margin_lower"]) > 0
        and 0 < Q(domain["conditioning_upper"]) <= 10**8, "whole-domain failure")
    b.require(Q(value["C_lower"]) > 0 and Q(value["W_lower"]) > 0, "nonpositive continuation")


def check_observation(graph, entry, row, *, numerics=False):
    b.require(row["entry"] == entry, "entry/history stage drift")
    output, cert = row["output"], row["certificate"]
    b.require(cert["input_digest"] == b.digest(dict(graph=graph, **entry))
        and cert["output_digest"] == b.digest(output)
        and cert["selected_joint_point_digest"] == b.digest(dict(H=output["H"], J=output["current"])),
        "oracle operand/joint-root binding drift")
    check_certificate(cert)
    for field, shape in (("C", (len(graph["live_node_ids"]),)), ("W_A", (len(graph["edges"]),)),
            ("current", (len(graph["edges"]),)), ("baseline", (len(graph["edges"]),)),
            ("readback", (len(graph["edges"]),)), ("flat", (len(graph["edges"]),)),
            ("H", (len(graph["edges"]),)*2), ("source", (len(graph["edges"]),)*2)):
        oracle.numerical.finite_array(oracle.np.array(output[field]), shape)
    b.require(min(output["C"]) > 0 and min(output["W_A"]) > 0, "invalid predicted state")
    if numerics:
        b.require(cert == certificate(graph, entry, output), "independent certificate drift")


def execute_case(args):
    manifest, case = args
    row = dict(case_id=case["case_id"], input_digest=b.digest(case),
        outcome="incomplete_oracle", first_failure=None, observations=[], native_steps=0,
        native_roots=0, topology_events=0, runtime_cells_closed=0)
    stage = "target_transfer"
    with ExitStack() as stack:
        for name in PRODUCERS:
            stack.enter_context(patch(name, side_effect=AssertionError("native producer forbidden: " + name)))
        try:
            with b.budget(case["execution_budget_seconds"]):
                target = target_for(manifest, case)
                row["target_digest"] = b.digest(target.to_payload())
                graph = case["oracle"]["target_graph"]
                paper = oracle.PaperACI(graph)
                for role in previous.ROLES:
                    state = getattr(target.inputs, role)
                    entry = dict(C=list(state.C), W_A=list(state.W_A))
                    for index in range(1, 12):
                        stage = f"{role}_{index}"
                        output = produce(paper, entry["C"], entry["W_A"])
                        row["observations"].append(dict(role=role, index=index,
                            stage="nominal_update" if index <= 10 else "final_entry_read_with_hypothetical_update",
                            entry=entry, output=output, certificate=certificate(graph, entry, output)))
                        entry = dict(C=output["C"], W_A=output["W_A"])
                row["outcome"] = "passed_bounded_oracle"
        except Exception as exc:
            row["first_failure"] = dict(stage=stage, type=type(exc).__name__,
                message=str(exc).replace(str(b.ROOT), "<repository>"))
    print(case["case_id"], row["outcome"], row["first_failure"], flush=True)
    return row


def reuse_rows(manifest):
    _, old = predecessor()
    rows = []
    for link in manifest["exact_reuse"]:
        row = next(v for v in old["cases"] if v["case_id"] == link["previous_case_id"])
        case = next(v for v in manifest["cases"] if v["case_id"] == link["case_id"])
        b.require(row["case_passed"] and row["event_committed"] and row["first_failure"] is None,
            "incomplete D45 reuse")
        b.require(row["event"]["actual_target"] == target_for(manifest, case).to_payload(), "D45 target mismatch")
        rows.append(dict(**link, previous_record_digest=old["record_digest"],
            previous_row_digest=b.digest(row), evidence_kind="exact_accepted_native_case_not_new_oracle"))
    return rows


def status(manifest, record):
    check_manifest(manifest)
    b.check_digest(record)
    b.require(record["schema"] == "p984c-aci-oracle-results-v1"
        and record["manifest_digest"] == manifest["record_digest"]
        and record["native_runtime_executed"] is False and record["user_accepted"] is False
        and record["aggregate_closed"] is False, "oracle scope drift")
    b.require(record["reuse"] == reuse_rows(manifest), "reuse lineage drift")
    reused = {v["case_id"] for v in manifest["exact_reuse"]}
    wanted = [v for v in manifest["cases"] if v["case_id"] not in reused]
    b.require([v["case_id"] for v in record["cases"]] == [v["case_id"] for v in wanted], "oracle roster drift")
    for case, row in zip(wanted, record["cases"], strict=True):
        b.require(row["input_digest"] == b.digest(case)
            and row["native_steps"] == row["native_roots"] == row["topology_events"] == row["runtime_cells_closed"] == 0, "false native credit")
        if row["outcome"] == "passed_bounded_oracle":
            b.require(row["first_failure"] is None and len(row["observations"]) == 22, "incomplete oracle")
        else:
            b.require(row["outcome"] == "incomplete_oracle" and row["first_failure"] is not None, "hidden oracle failure")
    return dict(family="A_CI", cases_required=32, new_oracle_cases=30,
        passed_cases=sum(v["outcome"] == "passed_bounded_oracle" for v in record["cases"]),
        exact_accepted_target_reuses=len(record["reuse"]), native_steps=0, native_roots=0,
        topology_events=0, runtime_cells_closed=0, user_accepted=False,
        native_trajectories_rerun=False, interval_equations_recomputed=False)


def check(manifest, record, *, numerics=False):
    summary = status(manifest, record)
    cases = {v["case_id"]: v for v in manifest["cases"]}
    for row in record["cases"]:
        if row["outcome"] != "passed_bounded_oracle":
            continue
        case = cases[row["case_id"]]
        target = target_for(manifest, case)
        b.require(row["target_digest"] == b.digest(target.to_payload()), "target binding drift")
        b.require([(v["role"], v["index"], v["stage"]) for v in row["observations"]]
            == [(role, i, "nominal_update" if i <= 10 else "final_entry_read_with_hypothetical_update")
                for role in previous.ROLES for i in range(1, 12)], "oracle stage schedule drift")
        for role in previous.ROLES:
            state = getattr(target.inputs, role)
            entry = dict(C=list(state.C), W_A=list(state.W_A))
            for value in (v for v in row["observations"] if v["role"] == role):
                check_observation(case["oracle"]["target_graph"], entry, value, numerics=numerics)
                entry = {k: value["output"][k] for k in ("C", "W_A")}
    return {**summary, "retained_integrity": "passed", "interval_equations_recomputed": numerics}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--prepare", action="store_true")
    group.add_argument("--run-oracle", action="store_true")
    group.add_argument("--check-retained", action="store_true")
    parser.add_argument("--recheck-numerics", action="store_true")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--output", default=RESULTS)
    args = parser.parse_args()
    b.require(not args.recheck_numerics or args.check_retained, "recheck requires retained mode")
    b.require(1 <= args.workers <= 8, "worker count outside 1..8")
    b.require(not b.Path(args.output).is_absolute() and ".." not in b.Path(args.output).parts, "repository-relative output required")
    with ExitStack() as stack:
        for name in PRODUCERS:
            stack.enter_context(patch(name, side_effect=AssertionError("native producer forbidden: " + name)))
        if args.prepare:
            b.write_new(INPUTS, make_manifest())
            print("A_CI boundary oracle subjects frozen; no native execution")
            return
        manifest = b.read(INPUTS)
        check_manifest(manifest)
        if args.check_retained:
            print(json.dumps(check(manifest, b.read(args.output), numerics=args.recheck_numerics), indent=2))
            return
        b.require(not (b.ROOT / args.output).exists(), "refuse to overwrite oracle evidence")
        reused = {v["case_id"] for v in manifest["exact_reuse"]}
        jobs = [(manifest, c) for c in manifest["cases"] if c["case_id"] not in reused]
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            rows = list(pool.map(execute_case, jobs))
        record = b.seal(dict(schema="p984c-aci-oracle-results-v1", manifest_digest=manifest["record_digest"],
            cases=rows, reuse=reuse_rows(manifest), native_runtime_executed=False,
            user_accepted=False, aggregate_closed=False))
        b.write_new(args.output, record)
        report = check(manifest, record)
        print(json.dumps(report, indent=2))
        if report["passed_cases"] != 30:
            raise SystemExit(1)


if __name__ == "__main__":
    main()

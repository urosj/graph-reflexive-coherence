"""Independent A_OS expectations for P9-8.4b; no native event or trajectory.

Reuse the accepted 100-digit paper equations and separate 60-digit interval
checker, extending only the bound layout/request population. New A scope must
be reviewed before runtime comparison. Retained integrity is not reexecution.
"""

import argparse
from copy import deepcopy
from fractions import Fraction as Q
from importlib.metadata import version
import json
import platform
import time

import p984b_runtime as common
import verify_p983a_aos_oracle as aos

SELF = common.HERE + "p984b_aos_oracle.py"
TEST = common.HERE + "test_p984b_aos_oracle.py"
INPUTS = common.BASE + "P9-8.4b-AOSOracleInputs.json"
RESULTS = common.BASE + "P9-8.4b-AOSOracleResults.json"
REVIEW = common.BASE + "P9-8.4b-AOSOracleReview.md"
OLD_ORACLE_SHA = "ce7f4ae309d9256d93ce7d96f10073e4380f92b26a9af548df1269f98507a06e"
LIMITS = {
    "C": aos.RESOURCE_ERROR,
    "W_A": aos.HISTORY_ERROR,
    "current": aos.CURRENT_ERROR,
    "baseline": aos.CURRENT_ERROR,
    "H": aos.HISTORY_ERROR,
    "regenerated": aos.HISTORY_ERROR,
    "predictor_current": aos.CURRENT_ERROR,
    "predictor_readback": aos.CURRENT_ERROR,
    "corrector_readback": aos.CURRENT_ERROR,
}
ROLES = ("current", "reset")


def predecessor():
    common.require(
        common.sha((common.ROOT / aos.RECORD).read_bytes()) == OLD_ORACLE_SHA,
        "accepted A_OS oracle bytes changed",
    )
    record = common.read(aos.RECORD)
    common.check_digest(record)
    common.check_bindings(record["source_bindings"])
    return record


def case_for(vector, old, coverage):
    """Literal frozen target topology, new independent event identity and maps."""
    fixture = vector["fixture_id"]
    request = deepcopy(old["request"])
    for key in ("target_effective_degree", "module_chirality", "growth_phase"):
        request[key] = vector["request"][key]
    if fixture != common.PINNED:
        request["operation_id"] = "p984b-aos-" + fixture
    if (request["target_effective_degree"], request["growth_phase"]) == (52, 1):
        # Separately named simplex recipe: avoid concentrating the half-share
        # on the doubly extended branch. Independently certify A, not reuse C.
        request["resource_distribution"] = [0.25, 0.5, 0.25]
    event_payload = deepcopy(old["event_identity_payload"])
    for key in event_payload:
        if key in request and key != "schema_version":
            event_payload[key] = request[key]
    event_payload["canonical_module_node_count"] = vector["event_identity_payload"][
        "canonical_module_node_count"
    ]
    event = aos.payload_identity("expansion_event_identity_payload", event_payload)
    graph = deepcopy(vector["expected"]["identity_payloads"]["target_graph"])
    old_event = vector["expected"]["event_id"]

    def rename(value):
        return (
            event + value[len(old_event) :]
            if value.startswith(old_event + "/")
            else value
        )

    graph["live_node_ids"] = sorted(map(rename, graph["live_node_ids"]))
    for edge in graph["edges"]:
        edge["edge_id"] = rename(edge["edge_id"])
        for end in ("tail", "head"):
            edge[end]["node_id"] = rename(edge[end]["node_id"])
    graph["edges"].sort(key=lambda edge: edge["edge_id"])
    reference = aos.reference(graph)
    source = old["source"]["port_graph"]
    target_roles = {}
    shares = {
        event + f"/satellite/{i}": Q(s)
        for i, s in enumerate(request["resource_distribution"], 1)
    }
    for role in ROLES:
        state = old["source"][role]
        resources = dict(zip(source["live_node_ids"], state["C"], strict=True))
        weights = dict(
            zip((e["edge_id"] for e in source["edges"]), state["W_A"], strict=True)
        )
        currents = dict(
            zip(
                (e["edge_id"] for e in source["edges"]),
                old["source_reference_reads"][role]["current"],
                strict=True,
            )
        )
        target_roles[role] = {
            "authoritative": aos.authority(
                [
                    resources[n]
                    if n in resources
                    else float(Q(resources["source-s"]) * shares.get(n, 0))
                    for n in graph["live_node_ids"]
                ],
                [weights.get(e["edge_id"], 1.0) for e in graph["edges"]],
            ),
            "incoming_reference_current": [
                currents.get(e["edge_id"], 0.0) for e in graph["edges"]
            ],
        }
        common.require(
            sum(map(Q, target_roles[role]["authoritative"]["C"]))
            == sum(map(Q, state["C"])),
            "exact role charge changed",
        )
    identities = aos.native_identity(
        reference,
        old["specialization"]["specialization_id"],
        target_roles["current"]["authoritative"],
        target_roles["reset"]["authoritative"],
    )
    return {
        "case_id": "P984B-AOS-ORACLE-" + fixture,
        "fixture_id": fixture,
        "family": "A_OS",
        "subject_kind": "independent_native_companion_expectation",
        "coverage_binding": {
            "record_digest": coverage["record_digest"],
            "cell_ids": [fixture + "::A_OS::" + role for role in ROLES],
        },
        "request": request,
        "event_identity_payload": event_payload,
        "event_id": event,
        "target": {
            "port_graph": graph,
            "reference": reference.to_payload(),
            "descriptor": aos.descriptor(graph),
            "roles": target_roles,
            **identities,
        },
        "comparison": {
            "norm": "maximum_coordinate_absolute_full_formula_error",
            "budgets": {k: str(v) for k, v in LIMITS.items()},
            "dt": aos.DT,
            "target_steps_per_role": 10,
            "point_digits": 100,
            "interval_digits": 60,
            "split_tolerance": str(Q(aos.SPLIT)),
            "accumulated_trajectory_error_bound": False,
        },
        "execution_budget_seconds": 120,
        "native_source_rule": "run source beat then rebuild request/history/event identities from actual output; never borrow nominal seed IDs",
        "changes_from_frozen": [
            "A_OS_profile_and_history",
            "source_current_and_reset",
            "specialization_and_bond_seed",
            "resource_shares",
            "event_and_target_identities",
        ],
        "changes_from_A1": "layout/chirality/phase and resulting target; phase-one D52 alone uses [1/4,1/2,1/4]; source/profile/dt/budgets unchanged",
    }


def make_manifest():
    old = predecessor()
    coverage = common.read(common.COVERAGE)
    common.check_digest(coverage)
    common.check_bindings(coverage["source_bindings"])
    # Literal C_PC reset is not applicable to A_OS; all sixteen shared cases are.
    wanted = {
        row["fixture_id"]
        for row in coverage["coverage_cells"]
        if row["owner"] == "P9-8.4b" and row["applicable"] and row["family"] == "A_OS"
    }
    cases = [
        case_for(v, old, coverage)
        for v in common.read(common.VECTORS)["grc9_expansion_vectors"]
        if v["fixture_id"] in wanted
    ]
    common.require(len(cases) == 16, "A_OS must bind all sixteen shared layouts")
    baseline = next(c for c in cases if c["fixture_id"] == common.PINNED)
    for key in ("request", "event_id", "event_identity_payload", "target"):
        common.require(
            baseline[key] == old[key], "accepted D52 A_OS expectation changed: " + key
        )
    paths = list(aos.SOURCES) + [
        aos.RECORD,
        aos.REVIEW,
        common.COVERAGE,
        common.HERE + "verify_p983a_aos_oracle.py",
        common.HERE + "test_p983a_aos_oracle.py",
        common.SELF,
        SELF,
        TEST,
        "pyproject.toml",
    ]
    return common.seal(
        {
            "schema": "p984b-aos-oracle-inputs-v1",
            "family": "A_OS",
            "predecessor_record_digest": old["record_digest"],
            "source_bindings": common.bind(paths),
            "shared": {
                key: deepcopy(old[key])
                for key in (
                    "initial",
                    "source_step",
                    "source",
                    "specialization",
                    "template",
                    "source_reference_reads",
                    "candidate_detection",
                    "side_tool_provenance",
                )
            },
            "cases": cases,
            "user_accepted": False,
            "native_runtime_executed": False,
            "runtime_gate": "independent_oracle_review_and_user_acceptance_before_new_A_scope",
            "stage_meaning": "source step and 10 target steps are paper predictions; source references/target admission/final reads perform no physical writes",
        }
    )


def check_manifest(manifest):
    common.check_digest(manifest)
    common.check_bindings(manifest["source_bindings"])
    common.require(manifest == make_manifest(), "A_OS oracle input/case/budget drift")


def interval_certificate(graph, c, w, output):
    """Reused independent interval formulas, with retained exact error bounds."""
    model = aos.StagedRows(graph["live_node_ids"], deepcopy(graph["edges"]), aos.PARAMS)
    high = aos.IntervalRows(model)
    cn, wn, stages = high.ordinary_os("A", aos.vector(tuple(c)), aos.vector(tuple(w)))
    truths = {
        "C": cn,
        "W_A": wn,
        "current": stages["read"]["J"],
        "baseline": stages["read"]["baseline"],
        "H": stages["H"],
        "regenerated": high.I + 0.5 * stages["read"]["source"],
    }
    for label, point in (
        ("predictor", stages["predictor"]),
        ("corrector", stages["read"]),
    ):
        drive = high.conductance(aos.vector(c), aos.vector(w), point["baseline"])
        truths[label + "_readback"] = aos.IV.matrix(
            [
                (weight - g) / (weight + g) * j / 16
                for weight, g, j in zip(aos.vector(w), drive, point["J"], strict=True)
            ]
        )
    truths["predictor_current"] = stages["predictor"]["J"]
    errors = {}
    for name, truth in truths.items():
        expected_shape = (
            (len(graph["edges"]), len(graph["edges"]))
            if name in ("H", "regenerated")
            else (len(graph["live_node_ids"]) if name == "C" else len(graph["edges"]),)
        )
        actual = aos.np.asarray(output[name])
        common.require(
            actual.shape == expected_shape and aos.np.isfinite(actual).all(),
            "invalid numerical shape/value: " + name,
        )
        error = aos.full_error(actual.reshape(-1), aos.IV.matrix(list(truth)))
        common.require(
            error < LIMITS[name], "full formula error exceeds bound: " + name
        )
        errors[name] = str(error)
    certificate = {
        "full_formula_errors": errors,
        "split_upper": str(stages["split_bound"]),
        "geometry_upper": str(stages["geometry_bound"]),
        "regularity_lower": str(stages["read"]["regularity"]),
        "C_lower": str(min(aos.endpoint(x, 0) for x in cn)),
        "W_lower": str(min(aos.endpoint(x, 0) for x in wn)),
        "represented_split_admitted": aos.split_admitted(
            aos.np.asarray(output["H"]),
            aos.np.asarray(output["regenerated"]),
            model.I,
            Q(aos.SPLIT),
        ),
        "operand_digest": common.digest({"graph": graph, "C": list(c), "W_A": list(w)}),
        "output_digest": common.digest(output),
        "scope": "full_formula_error_at_this_saved_entry_only_not_a_native_run_or_uniform_tube",
    }
    check_certificate(certificate)
    return certificate


def check_certificate(cert):
    common.require(
        set(cert["full_formula_errors"]) == set(LIMITS), "missing full error quantity"
    )
    common.require(
        all(
            0 <= Q(cert["full_formula_errors"][k]) < budget
            for k, budget in LIMITS.items()
        ),
        "invalid full error ceiling",
    )
    common.require(
        0 <= Q(cert["split_upper"]) < Q(aos.SPLIT)
        and 0 <= Q(cert["geometry_upper"]) < Q(1, 2)
        and Q(cert["regularity_lower"]) > Q(1, 2)
        and Q(cert["C_lower"]) >= 0
        and Q(cert["W_lower"]) > 0
        and cert["represented_split_admitted"] is True,
        "oracle admission/domain certificate failed",
    )


def evaluate(paper, state, stage, role, index):
    # Capture entry operands before invoking the producer, including a faulty one.
    c, w = tuple(state["C"]), tuple(state["W_A"])
    output = paper.step(c, w)
    predictor = paper.read(c, w)
    corrector = paper.read(c, w, paper.I + predictor["source"] / 2)
    output["predictor_current"] = list(map(float, predictor["current"]))
    for label, point in (("predictor", predictor), ("corrector", corrector)):
        output[label + "_readback"] = [
            float(
                (paper.mp.mpf(weight) - drive) / (paper.mp.mpf(weight) + drive) * j / 16
            )
            for weight, drive, j in zip(
                w, point["drive"], point["current"], strict=True
            )
        ]
    cert = interval_certificate(paper.graph, c, w, output)
    return {
        "stage": stage,
        "role": role,
        "index": index,
        "entry": aos.authority(c, w),
        "output": output,
        "certificate": cert,
    }


def run_case(case):
    rows = []
    stage, role, index = "target_readmission", "current", 0
    start = time.monotonic()
    result = {
        "case_id": case["case_id"],
        "input_digest": common.digest(case),
        "coverage_binding": case["coverage_binding"],
        "expectations": rows,
        "outcome": "incomplete_oracle",
        "first_failure": None,
        "native_event_committed": False,
        "native_steps": 0,
    }
    try:
        with common.budget(case["execution_budget_seconds"]):
            paper = aos.PaperAOS(case["target"]["port_graph"])
            for role in ROLES:
                state = deepcopy(case["target"]["roles"][role]["authoritative"])
                for index in range(1, 11):
                    stage = "target_continuation"
                    row = evaluate(paper, state, stage, role, index)
                    rows.append(row)
                    state = aos.authority(row["output"]["C"], row["output"]["W_A"])
                stage, index = "final_read", 0
                rows.append(evaluate(paper, state, stage, role, index))
            result["outcome"] = "passed_bounded_oracle"
    except Exception as exc:
        result["first_failure"] = {
            "stage": stage,
            "role": role,
            "index": index,
            "type": type(exc).__name__,
            "message": str(exc).replace(str(common.ROOT), "<repository>"),
            "kind": "operational_timeout"
            if isinstance(exc, common.BudgetExpired)
            else "oracle_or_domain_failure",
        }
    result["elapsed_seconds"] = time.monotonic() - start
    # First-step read stages also cover target entry admission: same saved C/W,
    # not a second physical step or an executed event.
    result["target_admission_expectation_indices"] = {
        role: next(
            (i for i, r in enumerate(rows) if r["role"] == role and r["index"] == 1),
            None,
        )
        for role in ROLES
    }
    return result


def check_observation(graph, entry, row, *, recheck_numerics=False):
    common.require(row["entry"] == entry, "oracle entry/history chain drift")
    cert = row["certificate"]
    check_certificate(cert)
    common.require(
        cert["operand_digest"]
        == common.digest({"graph": graph, "C": entry["C"], "W_A": entry["W_A"]})
        and cert["output_digest"] == common.digest(row["output"]),
        "oracle operand/output binding drift",
    )
    if recheck_numerics:
        expected = interval_certificate(
            graph, tuple(entry["C"]), tuple(entry["W_A"]), row["output"]
        )
        common.require(cert == expected, "independent interval certificate drift")


def validate(manifest, results, *, recheck_numerics=False):
    common.check_digest(results)
    common.require(
        results["manifest_digest"] == manifest["record_digest"]
        and results["native_runtime_executed"] is False
        and results["user_accepted"] is False,
        "oracle scope/manifest promotion",
    )
    common.require(
        [r["case_id"] for r in results["cases"]]
        == [c["case_id"] for c in manifest["cases"]],
        "missing/reordered A_OS layout",
    )
    source = manifest["shared"]["source"]["port_graph"]
    expected_source = [
        ("source_step", "current", manifest["shared"]["initial"]["current"])
    ] + [
        ("source_reference_read", role, manifest["shared"]["source"][role])
        for role in ROLES
    ]
    common.require(
        len(results["shared_observations"]) == 3, "missing shared source expectation"
    )
    for row, (stage, role, entry) in zip(
        results["shared_observations"], expected_source, strict=True
    ):
        common.require(
            (row["stage"], row["role"], row["index"]) == (stage, role, 0),
            "source stage mismatch",
        )
        check_observation(source, entry, row, recheck_numerics=recheck_numerics)
        pinned = (
            manifest["shared"]["source_step"]
            if stage == "source_step"
            else manifest["shared"]["source_reference_reads"][role]
        )
        common.require(
            {key: row["output"][key] for key in pinned} == pinned,
            "accepted source expectations changed",
        )
    for case, result in zip(manifest["cases"], results["cases"], strict=True):
        common.require(
            result["input_digest"] == common.digest(case)
            and result["coverage_binding"] == case["coverage_binding"]
            and result["native_event_committed"] is False
            and result["native_steps"] == 0,
            "case binding or native execution claim drift",
        )
        sequence = [
            (stage, role, i)
            for role in ROLES
            for stage, i in [("target_continuation", i) for i in range(1, 11)]
            + [("final_read", 0)]
        ]
        rows = result["expectations"]
        actual = [(r["stage"], r["role"], r["index"]) for r in rows]
        common.require(
            actual == sequence[: len(actual)], "target expectation schedule drift"
        )
        if result["outcome"] == "passed_bounded_oracle":
            common.require(
                len(rows) == 22 and result["first_failure"] is None,
                "incomplete oracle called a pass",
            )
        else:
            common.require(
                result["outcome"] == "incomplete_oracle"
                and result["first_failure"] is not None,
                "unknown oracle outcome",
            )
        expected_admissions = {
            role: next(
                (
                    i
                    for i, row in enumerate(rows)
                    if row["role"] == role and row["index"] == 1
                ),
                None,
            )
            for role in ROLES
        }
        common.require(
            result["target_admission_expectation_indices"] == expected_admissions,
            "missing/foreign target admission expectation",
        )
        states = {r: case["target"]["roles"][r]["authoritative"] for r in ROLES}
        for row in rows:
            role = row["role"]
            check_observation(
                case["target"]["port_graph"],
                states[role],
                row,
                recheck_numerics=recheck_numerics,
            )
            if row["stage"] != "final_read":
                states[role] = aos.authority(row["output"]["C"], row["output"]["W_A"])
    return {
        "retained_integrity": "passed",
        "interval_equations_recomputed": recheck_numerics,
        "native_runtime_executed": False,
        "oracle_cases_passed": sum(
            r["outcome"] == "passed_bounded_oracle" for r in results["cases"]
        ),
        "oracle_cases_required": 16,
        "runtime_cells_closed": 0,
        "user_accepted": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--prepare", action="store_true")
    action.add_argument("--run-oracle", action="store_true")
    action.add_argument("--check-retained", action="store_true")
    parser.add_argument(
        "--recheck-numerics",
        action="store_true",
        help="with --check-retained: recompute every independent interval certificate, not native execution",
    )
    parser.add_argument("--manifest", default=INPUTS)
    parser.add_argument("--output", default=RESULTS)
    args = parser.parse_args()
    common.require(
        not args.recheck_numerics or args.check_retained,
        "recheck requires retained mode",
    )
    for name in (args.manifest, args.output):
        common.require(
            not common.Path(name).is_absolute() and ".." not in common.Path(name).parts,
            "artifact paths must be repository-relative",
        )
    if args.prepare:
        common.write_new(args.manifest, make_manifest())
        print("AOS_ORACLE_INPUTS_BOUND native_runtime_executed=false")
        return
    manifest = common.read(args.manifest)
    check_manifest(manifest)
    if args.check_retained:
        print(
            json.dumps(
                validate(
                    manifest,
                    common.read(args.output),
                    recheck_numerics=args.recheck_numerics,
                ),
                indent=2,
            )
        )
        return
    common.require(
        not (common.ROOT / args.output).exists(),
        "refusing to replace retained evidence",
    )
    common.require(
        aos.A_G2
        in aos.admission.accepted(common.ROOT)["accepted_generic_runtime_support"],
        "A_OS prerequisite absent from G3",
    )
    # Query unchanged D11 authority once. Do not promote its claim status.
    common.require(
        aos.provenance() == manifest["shared"]["side_tool_provenance"],
        "forensic authority trace drift",
    )
    shared = manifest["shared"]
    paper = aos.PaperAOS(shared["source"]["port_graph"])
    observations = [
        evaluate(paper, shared["initial"]["current"], "source_step", "current", 0)
    ]
    observations += [
        evaluate(paper, shared["source"][role], "source_reference_read", role, 0)
        for role in ROLES
    ]
    results = {
        "schema": "p984b-aos-oracle-results-v1",
        "manifest_digest": manifest["record_digest"],
        "command": [".venv/bin/python", SELF, *common.sys.argv[1:]],
        "dependencies": {
            "python": platform.python_version(),
            **{p: version(p) for p in ("mpmath", "numpy", "rfc8785")},
        },
        "native_runtime_executed": False,
        "user_accepted": False,
        "shared_observations": observations,
        "cases": [],
    }
    for case in manifest["cases"]:
        row = run_case(case)
        results["cases"].append(row)
        print(row["case_id"], row["outcome"], row["first_failure"], flush=True)
    results = common.seal(results)
    common.write_new(args.output, results)
    report = validate(manifest, results)
    report["oracle_numerics_executed_in_this_command"] = True
    print(json.dumps(report, indent=2))
    if any(row["outcome"] != "passed_bounded_oracle" for row in results["cases"]):
        raise SystemExit(1)


if __name__ == "__main__":
    main()

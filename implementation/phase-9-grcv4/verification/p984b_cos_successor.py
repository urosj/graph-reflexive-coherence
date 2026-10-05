"""P9-8.4b retained-status clarity and two separately bound C_OS successors.

The original sixteen-case campaign and its hash-bound runner remain unchanged.
Only --run executes native trajectories. --check-retained checks records and
dense expectations, including consumption evidence where it was actually captured.
Neither mode confers acceptance, a rigorous error certificate, or all-ten closure.
"""

import argparse
from copy import deepcopy
from dataclasses import replace
from importlib.metadata import version
import json
import os
import platform
from unittest.mock import patch

import p984b_runtime as base

SELF = base.HERE + "p984b_cos_successor.py"
TEST = base.HERE + "test_p984b_cos_successor.py"
INPUTS = base.BASE + "P9-8.4b-COSPhaseOneCases.json"
RESULTS = base.BASE + "P9-8.4b-COSPhaseOneResults.json"
SHARES = [1 / 4, 1 / 2, 1 / 4]


def point_capture(point):
    return {
        "descriptor": point.to_payload(),
        "point_identity": point.identity,
        "current": list(point.current.values),
        "read_current": list(point.read.current.values),
        "read_source_identity": point.read.source_identity,
        "causal_flat": list(point.read.causal_flat.values),
        "read_flux": list(point.read.flux.values),
    }


def check_point(value, policy):
    """Bind two read surfaces to their actual operand and the dense equations."""
    descriptor = value["descriptor"]
    base.require(
        descriptor["descriptor_version"] == "grcv4-c-fixed-stage-v1"
        and descriptor["numerics"] == "grcv4-c-stage-exact-linear-binary64-v1",
        "foreign point descriptor",
    )
    identity = "grcv4-c-fixed-stage-sha256:" + base.digest(descriptor)
    base.require(
        value["point_identity"] == value["read_source_identity"] == identity
        and value["current"] == value["read_current"],
        "read operand/source identity mismatch",
    )
    inputs = base.GeometryStageInputs.from_payload(descriptor["inputs"])
    h = base.np.asarray(inputs.geometry.one_form_hodge.matrix)
    # Alternate read surface: the typed causal one-form, raised with its Hodge.
    base.comparison(value["read_flux"], h @ value["causal_flat"], policy, "read_sharp")
    expected = base.dense_current_oracle(inputs)
    base.comparison(value["current"], expected["current"], policy, "point_J")
    base.comparison(value["read_flux"], expected["read"], policy, "point_readback")
    return inputs


def pass_capture(passed):
    return {
        "inputs": passed.inputs.to_payload(),
        "predictor": point_capture(passed.predictor),
        "corrector": point_capture(passed.corrector),
    }


def check_pass(value, policy):
    before = base.GeometryStageInputs.from_payload(value["inputs"])
    predictor = check_point(value["predictor"], policy)
    corrector = check_point(value["corrector"], policy)
    base.require(
        predictor == replace(before, stage="os_predictor")
        and corrector
        == replace(before, geometry=corrector.geometry, stage="os_corrector"),
        "predictor/corrector operand substitution",
    )
    base.require(
        before.geometry == before.geometry.reference.geometry(),
        "OS predictor must consume reference geometry",
    )
    # Rebuild generated H from the captured predictor read, not from a reported H.
    b = base.np.asarray(before.geometry.reference.graph.incidence)
    lowered = base.np.linalg.solve(
        base.np.asarray(predictor.geometry.one_form_hodge.matrix),
        value["predictor"]["read_flux"],
    )
    overlap = abs(b).T @ abs(b) / 2
    assembly = base.np.array(
        [
            [
                float(
                    base.Fraction(float(w))
                    * base.Fraction(float(x))
                    * base.Fraction(float(y))
                )
                for w, y in zip(row, lowered, strict=True)
            ]
            for row, x in zip(overlap, lowered, strict=True)
        ]
    )
    params = before.geometry.reference.profile.params_resolved
    generated = base.np.asarray(before.geometry.reference.pairings.one_form.matrix) + (
        params.geometry.kappa_H * (params.candidate.zeta_C * assembly)
    )
    base.comparison(
        corrector.geometry.one_form_hodge.matrix, generated, policy, "consumed_H"
    )
    return before, corrector


def step_capture(step):
    return {
        "pass": pass_capture(step.os_pass),
        "resource_prestate": step.resource.prestate.to_payload(),
        "selection": step.resource.selection.to_payload(),
        "resource": base.authority_payload(step.resource.provisional_state),
        "continuity_evaluations": step.resource.continuity_evaluations,
        "poststate": step.next_inputs.to_payload(),
        "final": point_capture(step.final),
    }


def check_step(value, policy):
    before, corrector = check_pass(value["pass"], policy)
    selection = value["selection"]
    base.require(
        value["resource_prestate"] == before.to_payload()
        and selection["inputs"] == corrector.to_payload()
        and selection["solver_disposition"] == "valid_root"
        and selection["current"] == value["pass"]["corrector"]["current"]
        and value["continuity_evaluations"] == 1,
        "continuity did not consume the captured corrector",
    )
    # Reconstruct staged binary64 continuity from oriented edges, not step.os_pass.
    # Keep multiplication/subtraction rounding separate, as in the native contract.
    graph = before.geometry.reference.graph
    terms = {node: [] for node in graph.live_node_ids}
    for edge, j in zip(graph.oriented_edges, selection["current"], strict=True):
        # Repository convention: B is +1 at the tail and -1 at the head.
        terms[edge.tail_node_id].append(j)
        terms[edge.head_node_id].append(-j)
    computed = [
        c - before.dt * sum(terms[node])
        for node, c in zip(graph.live_node_ids, before.current.C, strict=True)
    ]
    base.require(
        value["resource"]["C"] == computed, "selected-current continuity mismatch"
    )
    state = base.GRCV4AuthoritativeState(tuple(computed), None, None)
    post = replace(
        before,
        current=state,
        step_index=before.step_index + 1,
        time=before.time + before.dt,
    )
    base.require(
        value["resource"] == base.authority_payload(state)
        and value["poststate"] == post.to_payload(),
        "delivered poststate differs from consumed resource",
    )
    final = check_point(value["final"], policy)
    base.require(
        final == replace(corrector, current=state, stage="post_continuity"),
        "final refresh did not consume written resource and corrector geometry",
    )
    return before, post


def zero_node_stencil(target, role):
    """Exact L^2 C at H=I, kappa_M=zeta=0: design diagnostic, not full-law proof."""
    graph = target.geometry.reference.graph
    b = base.np.asarray(graph.incidence, dtype=int)
    laplacian = b @ b.T
    state = getattr(target, role)
    lc = [
        sum(
            (int(a) * base.Fraction(c) for a, c in zip(row, state.C, strict=True)),
            base.Fraction(),
        )
        for row in laplacian
    ]
    rates = [
        sum((int(a) * c for a, c in zip(row, lc, strict=True)), base.Fraction())
        for row in laplacian
    ]
    return [
        {"node": n, "uncoupled_rate_exact": str(rate)}
        for n, c, rate in zip(graph.live_node_ids, state.C, rates, strict=True)
        if c == 0
    ]


def dense_preflight(target):
    """Bind finite enabled-law predictions before any successor native event."""
    result = {}
    for role in ("current", "reset"):
        inputs = replace(target, current=getattr(target, role), dt=base.DT)
        minima = []
        for _ in range(10):
            expected = base.dense_os(inputs)
            minima.append(float(min(expected["C"])))
            base.require(minima[-1] > 0, "successor dense preflight is not positive")
            inputs = replace(
                inputs,
                current=base.GRCV4AuthoritativeState(
                    tuple(map(float, expected["C"])), None, None
                ),
                step_index=inputs.step_index + 1,
                time=inputs.time + base.DT,
            )
        result[role] = {"minimum_C_by_beat": minima, "final_C": list(inputs.current.C)}
    return {
        "kind": "finite_dense_prediction_not_native_admission_or_rigorous_error_bound",
        "roles": result,
    }


def make_manifest():
    previous = base.read(base.INPUTS)
    base.check_manifest(previous)
    old_results = base.read(base.RESULTS)
    base.check_digest(old_results)
    vectors = {
        v["fixture_id"]: v for v in base.read(base.VECTORS)["grc9_expansion_vectors"]
    }
    manifest = deepcopy(previous)
    manifest["schema"] = "p984b-cos-phase-one-manifest-v1"
    manifest["predecessor"] = {
        "manifest": previous["record_digest"],
        "results": old_results["record_digest"],
        "disposition": "original_two_failures_preserved_not_reclassified",
    }
    manifest["cases"] = []
    for original in previous["cases"]:
        if (
            original["request"]["target_effective_degree"],
            original["request"]["growth_phase"],
        ) != (52, 1):
            continue
        case = deepcopy(original)
        case["case_id"] = "P984B-COS-PHASE1-SHARES-" + original["fixture_id"]
        case["predecessor_case_id"] = original["case_id"]
        case["request"]["resource_distribution"] = SHARES
        case["request"]["operation_id"] = (
            "p984b-cos-phase1-shares-" + original["fixture_id"]
        )
        case["oracle"] = base.construction_oracle(
            vectors[case["fixture_id"]],
            case["request"],
            manifest["expected_source"]["specialization"],
        )
        target = base.independent_target(manifest, case)
        old_target = base.independent_target(previous, original)
        case["design"] = {
            "change": "only simplex shares and operation/event namespaces; source/profile/dt/horizon/tolerances unchanged",
            "choice": "quarter share on doubly extended branch 1; half share on next branch 2; no search or automatic topology policy",
            "stencil_scope": "uncoupled identity-Hodge L^2 C only, not an enabled-law error bound",
            "original_zero_node_rates": {
                r: zero_node_stencil(old_target, r) for r in ("current", "reset")
            },
            "successor_zero_node_rates": {
                r: zero_node_stencil(target, r) for r in ("current", "reset")
            },
        }
        case["enabled_dense_preflight"] = dense_preflight(target)
        manifest["cases"].append(case)
    base.require(
        len(manifest["cases"]) == 2, "expected exactly two phase-one successors"
    )
    manifest["source_bindings"] = base.bind(
        [r["path"] for r in previous["source_bindings"]]
        + [base.INPUTS, base.RESULTS, SELF, TEST]
    )
    return base.seal(manifest)


def check_manifest(manifest):
    base.check_digest(manifest)
    base.check_bindings(manifest["source_bindings"])
    base.require(
        manifest == make_manifest(), "successor manifest differs from fixed design"
    )


def execute(manifest, case):
    captures = []
    native_step = base.ProvisionalCandidateCOSStep
    native_pass = base.CandidateCOSPass

    def checked_step(inputs):
        result = native_step(inputs)
        capture = step_capture(result)
        check_step(capture, case["comparison"])
        captures.append({"kind": "step", "value": capture})
        return result

    def checked_final(inputs):
        result = native_pass(inputs)
        # Admission observations also call this name. Only the declared final
        # reads have step_index 11; admission remains separately recorded.
        if inputs.step_index == 11 and inputs.dt == base.DT:
            capture = pass_capture(result)
            check_pass(capture, case["comparison"])
            captures.append({"kind": "final_read", "value": capture})
        return result

    with (
        patch.object(base, "ProvisionalCandidateCOSStep", checked_step),
        patch.object(base, "CandidateCOSPass", checked_final),
    ):
        row = base.execute_cos(manifest, case)
    row["consumption_evidence"] = captures
    row["case_passed"] = row["outcome"] == "passed_named_case"
    return row


def check_consumption(row, manifest, case):
    captures = row["consumption_evidence"]
    observations = row["observations"]
    base.require(
        len(captures) == len(observations), "missing/extra consumption evidence"
    )
    target = base.independent_target(manifest, case)
    incoming = {
        r: replace(target, current=getattr(target, r), dt=base.DT)
        for r in ("current", "reset")
    }
    for captured, observation in zip(captures, observations, strict=True):
        final = observation["stage"] == "final_read"
        base.require(
            captured["kind"] == ("final_read" if final else "step"),
            "wrong capture kind",
        )
        value = captured["value"]
        passed = value if final else value["pass"]
        if final:
            before, _ = check_pass(passed, case["comparison"])
            base.require(
                before.to_payload() == observation["final_inputs"], "foreign final read"
            )
        else:
            before, post = check_step(value, case["comparison"])
        expected = (
            base.GeometryStageInputs.from_payload(manifest["initial_inputs"])
            if observation["stage"] == "source_schedule"
            else incoming[observation["role"]]
        )
        base.require(before == expected, "consumption chain changed operand")
        actuals = {c["quantity"]: c["actual"] for c in observation["comparisons"]}
        delivered = {
            "predictor_J": passed["predictor"]["current"],
            "predictor_readback": passed["predictor"]["read_flux"],
            "H": passed["corrector"]["descriptor"]["inputs"]["H1_form"],
            "corrector_J": passed["corrector"]["current"],
            "corrector_readback": passed["corrector"]["read_flux"],
        }
        if not final:
            delivered["C"] = list(post.current.C)
            if observation["stage"] == "source_schedule":
                base.require(
                    replace(post, dt=0).to_payload()
                    == manifest["expected_source"]["inputs"],
                    "source capture differs from event source",
                )
            else:
                incoming[observation["role"]] = post
        base.require(
            actuals == delivered, "reported actual differs from captured consumer"
        )


def summary(manifest, results, *, native_rerun=False):
    passed = sum(r["outcome"] == "passed_named_case" for r in results["cases"])
    return {
        "retained_integrity": "passed",
        "native_trajectories_rerun": native_rerun,
        "complete_cases": passed,
        "executed_cases": len(results["cases"]),
        "required_cases": len(manifest["cases"]),
        "all_required_cases_passed": passed == len(manifest["cases"]),
        "events_committed": sum(r["event_committed"] for r in results["cases"]),
        "user_accepted": False,
        "P9_8_4b_closed": False,
        "cases": [
            {
                "case_id": r["case_id"],
                "event_committed": r["event_committed"],
                "case_passed": r["outcome"] == "passed_named_case",
                "outcome": r["outcome"],
                "first_failure": r["first_failure"],
                "consumption_evidence": "captured"
                if "consumption_evidence" in r
                else "not_captured_in_original_run",
            }
            for r in results["cases"]
        ],
    }


def validate(manifest, results):
    base.validate_results(manifest, results)
    cases = {c["case_id"]: c for c in manifest["cases"]}
    for row in results["cases"]:
        base.require(
            row["case_passed"] is (row["outcome"] == "passed_named_case"),
            "false case summary",
        )
        check_consumption(row, manifest, cases[row["case_id"]])
    return summary(manifest, results)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_mutually_exclusive_group(required=True)
    actions.add_argument("--prepare", action="store_true")
    actions.add_argument("--run", action="store_true")
    actions.add_argument(
        "--check-retained",
        action="store_true",
        help="no native trajectory rerun; integrity success is not case success",
    )
    parser.add_argument(
        "--original",
        action="store_true",
        help="report the unchanged original campaign, with its two failures",
    )
    parser.add_argument("--manifest", default=INPUTS)
    parser.add_argument("--output", default=RESULTS)
    args = parser.parse_args()
    for name in (args.manifest, args.output):
        base.require(
            not base.Path(name).is_absolute() and ".." not in base.Path(name).parts,
            "artifact paths must be repository-relative",
        )
    if args.original:
        base.require(args.check_retained, "--original is retained-only")
        manifest, results = base.read(base.INPUTS), base.read(base.RESULTS)
        base.check_manifest(manifest)
        base.validate_results(manifest, results)
        print(json.dumps(summary(manifest, results), indent=2))
        return
    if args.prepare:
        base.write_new(args.manifest, make_manifest())
        print("SUCCESSOR_CASES_BOUND native_trajectories_rerun=false")
        return
    manifest = base.read(args.manifest)
    check_manifest(manifest)
    if args.check_retained:
        print(json.dumps(validate(manifest, base.read(args.output)), indent=2))
        return
    base.require(
        not (base.ROOT / args.output).exists(),
        "refusing to replace retained results; use a fresh output path",
    )
    results = {
        "schema": "p984b-cos-phase-one-results-v1",
        "manifest_digest": manifest["record_digest"],
        "command": [".venv/bin/python", SELF, *base.sys.argv[1:]],
        "dependencies": {
            "python": platform.python_version(),
            **{
                p: version(p)
                for p in ("numpy", "python-flint", "rfc8785", "jsonschema")
            },
        },
        "thread_environment": {
            k: os.environ.get(k) for k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS")
        },
        "backend": "flint",
        "requested_case_ids": [c["case_id"] for c in manifest["cases"]],
        "user_accepted": False,
        "aggregate_closed": False,
        "cases": [],
        "limits": "two named C_OS successors only; no rigorous error/effect bound or other-family closure",
    }
    for case in manifest["cases"]:
        row = execute(manifest, case)
        results["cases"].append(row)
        print(
            row["case_id"],
            "event_committed=" + str(row["event_committed"]),
            "case_passed=" + str(row["case_passed"]),
            row["first_failure"],
            flush=True,
        )
    results = base.seal(results)
    base.write_new(args.output, results)
    validate(manifest, results)
    print(json.dumps(summary(manifest, results, native_rerun=True), indent=2))
    if not all(r["case_passed"] for r in results["cases"]):
        raise SystemExit(1)


if __name__ == "__main__":
    main()

"""C_CI boundary target/reference/domain preparation, not an event campaign.

Thirty new targets receive both-role native joint-root proposals checked by
independent interval equations. D45 preparation reuses exact accepted operands.
Ten-step independent predictions are not native continuation or a trajectory bound.
"""

import argparse
from contextlib import ExitStack
from copy import deepcopy
from dataclasses import replace
from fractions import Fraction as Q
from importlib.metadata import version
import json
import platform
import time
from unittest.mock import patch

import numpy as np
import p984b_cci_completion as previous
import p984c_cos as construction
import prepare_p984c_boundaries as boundary

r, b = previous.r, previous.b
SELF = b.HERE + "p984c_cci_preparation.py"
TEST = b.HERE + "test_p984c_cci_preparation.py"
INPUTS = b.BASE + "P9-8.4c-CCIPreparationInputs.json"
RESULTS = b.BASE + "P9-8.4c-CCIPreparationResults.json"
REVIEW = b.BASE + "P9-8.4c-CCIPreparationReview.md"
ACCEPTANCE_SHA = "fbf40e6e109fbbc9c7bad9492807a770a3e2fab7db2d734f3767631517dce679"


def predecessor():
    b.require(b.sha((b.ROOT / r.REVIEW).read_bytes()) == ACCEPTANCE_SHA, "C_CI predecessor acceptance drift")
    manifest, result = b.read(previous.INPUTS), b.read(previous.RESULTS)
    b.check_digest(manifest)
    b.check_bindings(manifest["source_bindings"])
    b.check_digest(result)
    b.require(result["manifest_digest"] == manifest["record_digest"]
        and len(result["cases"]) == 16 and all(row["case_passed"] for row in result["cases"]), "incomplete accepted C_CI predecessor")
    b.require(result["shared"]["actual_source"] == manifest["expected_source"], "accepted source drift")
    return manifest, result


def make_manifest():
    old, result = predecessor()
    contract = b.read(boundary.OUTPUT)
    b.check_digest(contract)
    family = next(f for f in contract["families"] if f["family"] == "C_CI")
    cases, reuse = [], []
    for layout in contract["layouts"]:
        template = next(c for c in old["cases"] if
            (c["request"]["target_effective_degree"], c["request"]["module_chirality"], c["request"]["growth_phase"])
            == (45 if layout["degree"] == 45 else 31, layout["chirality"], layout["phase"]))
        case = deepcopy(template)
        case.update(case_id=layout["id"] + "::C_CI", fixture_id=layout["id"],
            subject_kind="boundary_target_preparation_not_native_event",
            coverage_binding=dict(record_digest=contract["record_digest"],
                cell_ids=[layout["id"] + "::C_CI::" + role for role in r.ROLES]),
            execution_budget_seconds=family["execution_budget_seconds"], comparison=family["comparison"],
            changes_from_frozen=["boundary_layout_and_event_identity_only"])
        case["request"]["target_effective_degree"] = layout["degree"]
        if layout["degree"] != 45:
            case["request"]["operation_id"] = "p984c-cci-" + layout["id"]
        case["oracle"] = construction.target_oracle(old["expected_source"], template, case["request"], layout)
        recipe = next(c for c in contract["cases"] if c["id"] == case["case_id"])["request_recipe"]
        b.require(case["request"]["resource_distribution"] == recipe["resource_distribution"], "boundary shares changed")
        if layout["degree"] == 45:
            for key in ("request", "oracle", "schedule", "comparison", "execution_budget_seconds"):
                b.require(case[key] == template[key], "D45 exact scientific reuse drift: " + key)
            reuse.append(dict(case_id=case["case_id"], previous_case_id=template["case_id"]))
        cases.append(case)
    paths = {v["path"] for v in old["source_bindings"]} | {
        previous.INPUTS, previous.RESULTS, r.REVIEW, construction.SELF,
        "tests/models/test_grc_9_v4_expansion.py", boundary.OUTPUT, SELF, TEST}
    return b.seal(dict(schema="p984c-cci-preparation-inputs-v1", family="C_CI",
        source_bindings=b.bind(sorted(paths)), boundary_digest=contract["record_digest"],
        expected_source=old["expected_source"], cases=cases, exact_reuse=reuse,
        source_execution=dict(path=previous.RESULTS, record_digest=result["record_digest"],
            shared_digest=b.digest(result["shared"]), new_source_steps=0),
        stage_scope="both_role_target_joint_roots_and_nominal_predictions_not_native_events_or_continuation",
        user_accepted=False, aggregate_closed=False))


def check_manifest(manifest):
    b.check_digest(manifest)
    b.check_bindings(manifest["source_bindings"])
    b.require(manifest == make_manifest(), "boundary preparation manifest drift")


def target_for(manifest, case):
    target = b.independent_target(manifest, case)
    ref = target.geometry.reference
    source = b.GeometryStageInputs.from_payload(manifest["expected_source"]["inputs"])
    b.require(ref.profile.identity_payload.profile_family_id == "C_CI", "wrong target family")
    b.require(set(ref.profile.params_resolved.candidate.W_C_tr) == set(ref.graph.live_edge_ids), "incomplete target reference")
    b.require(target.current != target.reset, "lost distinct current/reset histories")
    for role in r.ROLES:
        old, new = getattr(source, role), getattr(target, role)
        b.require(new.W_A is None and new.Z_4 is None and min(new.C) >= 0, "invalid C_CI target authority")
        b.require(sum(map(Q, old.C)) == sum(map(Q, new.C)), "nonconserving target resource map")
    return target


def execute_case(manifest, case):
    started = time.monotonic()
    row = dict(case_id=case["case_id"], input_digest=b.digest(case), outcome="incomplete_preparation",
        first_failure=None, native_root_reads=0, native_steps=0, topology_events=0, runtime_cells_closed=0)
    stage = "independent_target"
    try:
        with b.budget(case["execution_budget_seconds"]):
            target = target_for(manifest, case)
            row["target_digest"] = b.digest(target.to_payload())
            stage = "independent_nominal_prediction"
            row["predictions"] = r.preflight(target)
            row["roles"] = {}
            for role in r.ROLES:
                stage = role + "_joint_root_and_independent_certificate"
                operand = replace(target, current=getattr(target, role))
                root = r.certified_root(r.CandidateCIRoot(operand))
                r.check_root(operand, root)
                row["roles"][role] = root
                row["native_root_reads"] += 1
            row["outcome"] = "passed_target_preparation"
    except Exception as exc:
        row["first_failure"] = dict(stage=stage, type=type(exc).__name__,
            message=str(exc).replace(str(b.ROOT), "<repository>"))
    row["elapsed_seconds"] = time.monotonic() - started
    return row


def reuse_rows(manifest, old):
    rows = {v["case_id"]: v for v in old["cases"]}
    return [dict(**link, previous_record_digest=old["record_digest"],
        previous_row_digest=b.digest(rows[link["previous_case_id"]])) for link in manifest["exact_reuse"]]


def materialize(manifest, record):
    _, old = predecessor()
    rows = {v["case_id"]: v for v in record["cases"]}
    for link in record["reuse"]:
        original = next(v for v in old["cases"] if v["case_id"] == link["previous_case_id"])
        case = next(c for c in manifest["cases"] if c["case_id"] == link["case_id"])
        target = target_for(manifest, case)
        b.require(original["event"]["actual_target"]["inputs"] == target.to_payload(), "D45 target is not exact reuse")
        reads = original["event"]["admission_reads"][1]
        rows[case["case_id"]] = dict(case_id=case["case_id"], input_digest=b.digest(case),
            target_digest=b.digest(target.to_payload()), predictions=original["predictions"],
            roles=dict(current=reads["root"], reset=reads["reset_root"]),
            outcome="passed_target_preparation", first_failure=None,
            native_root_reads=0, native_steps=0, topology_events=0, runtime_cells_closed=0)
    return [rows[c["case_id"]] for c in manifest["cases"]]


def status(manifest, record):
    """Pinned structure/identity view, not a numerical root or interval rerun."""
    check_manifest(manifest)
    b.check_digest(record)
    b.require(record["schema"] == "p984c-cci-preparation-results-v1"
        and record["manifest_digest"] == manifest["record_digest"]
        and record["user_accepted"] is False and record["aggregate_closed"] is False,
        "preparation scope drift")
    _, old = predecessor()
    b.require(record["reuse"] == reuse_rows(manifest, old), "preparation reuse drift")
    reused_ids = {v["case_id"] for v in manifest["exact_reuse"]}
    cases = [c for c in manifest["cases"] if c["case_id"] not in reused_ids]
    b.require([v["case_id"] for v in record["cases"]] == [c["case_id"] for c in cases], "preparation roster drift")
    for case, row in zip(cases, record["cases"], strict=True):
        b.require(row["input_digest"] == b.digest(case)
            and row["native_steps"] == row["topology_events"] == row["runtime_cells_closed"] == 0, "false runtime credit")
        if row["outcome"] == "passed_target_preparation":
            b.require(row["first_failure"] is None and row["native_root_reads"] == 2
                and set(row["roles"]) == set(r.ROLES), "incomplete both-role preparation")
        else:
            b.require(row["outcome"] == "incomplete_preparation" and row["first_failure"] is not None, "hidden preparation failure")
    return dict(family="C_CI", cases_required=32,
        new_preparation_cases=len(cases), passed_cases=sum(v["outcome"] == "passed_target_preparation" for v in record["cases"]),
        exact_reuse_cases=len(record["reuse"]), new_native_root_reads=sum(v["native_root_reads"] for v in record["cases"]),
        native_steps=0, topology_events=0, runtime_cells_closed=0, user_accepted=False,
        native_trajectories_rerun=False, interval_equations_recomputed=False)


def check_predictions(target, rows):
    b.require(set(rows) == set(r.ROLES), "missing prediction role")
    model = r.independent_model(target)
    for role in r.ROLES:
        b.require([v["index"] for v in rows[role]] == list(range(1, 11)), "prediction schedule drift")
        c = np.array(getattr(target, role).C)
        for value in rows[role]:
            j = np.asarray(value["J"])
            after = np.asarray(value["C"])
            b.require(j.shape == (len(model.edges),) and after.shape == c.shape
                and np.isfinite(j).all() and np.isfinite(after).all() and min(after) >= 0, "invalid predicted state/current")
            b.require(np.array_equal(after, c - b.DT * r.numerical.product(model.B, j)), "prediction continuity drift")
            c = after


def check(manifest, record, *, numerics=False):
    summary = status(manifest, record)
    for case, row in zip(manifest["cases"], materialize(manifest, record), strict=True):
        if row["outcome"] != "passed_target_preparation":
            continue
        target = target_for(manifest, case)
        b.require(row["target_digest"] == b.digest(target.to_payload()), "target binding drift")
        check_predictions(target, row["predictions"])
        for role in r.ROLES:
            operand = replace(target, current=getattr(target, role))
            r.check_root(operand, row["roles"][role], numerics=numerics)
        if numerics:
            b.require(row["predictions"] == r.preflight(target), "independent nominal prediction drift")
    return {**summary, "retained_integrity": "passed", "interval_equations_recomputed": numerics}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--prepare", action="store_true")
    group.add_argument("--run-prerequisites", action="store_true")
    group.add_argument("--check-retained", action="store_true")
    parser.add_argument("--recheck-numerics", action="store_true")
    parser.add_argument("--output", default=RESULTS)
    args = parser.parse_args()
    b.require(not args.recheck_numerics or args.check_retained, "recheck requires retained mode")
    b.require(not b.Path(args.output).is_absolute() and ".." not in b.Path(args.output).parts, "repository-relative output required")
    with ExitStack() as stack:
        for owner, name in ((r, "ProvisionalCandidateCIStep"), (r.native, "ProvisionalCandidateCIStep"),
            (r.native.GRC9V4CCIOperation, "__init__"), (b, "GRC9V4ExpansionPlan")):
            stack.enter_context(patch.object(owner, name, side_effect=AssertionError("native event/step forbidden: " + name)))
        if not args.run_prerequisites:
            stack.enter_context(patch.object(r, "CandidateCIRoot", side_effect=AssertionError("native root forbidden in preparation/integrity mode")))
        if args.prepare:
            b.write_new(INPUTS, make_manifest())
            print("C_CI boundary subjects prepared; no numerical execution")
            return
        manifest = b.read(INPUTS)
        check_manifest(manifest)
        if args.check_retained:
            print(json.dumps(check(manifest, b.read(args.output), numerics=args.recheck_numerics), indent=2))
            return
        b.require(not (b.ROOT / args.output).exists(), "refuse to overwrite preparation evidence")
        reused_ids = {v["case_id"] for v in manifest["exact_reuse"]}
        rows = []
        with b.exact_backend(b.ExactBackend.FLINT):
            for case in manifest["cases"]:
                if case["case_id"] in reused_ids:
                    continue
                row = execute_case(manifest, case)
                rows.append(row)
                print(case["case_id"], row["outcome"], row["first_failure"], flush=True)
        _, old = predecessor()
        record = b.seal(dict(schema="p984c-cci-preparation-results-v1", manifest_digest=manifest["record_digest"],
            cases=rows, reuse=reuse_rows(manifest, old),
            environment=dict(python=platform.python_version(), numpy=version("numpy"), mpmath=version("mpmath"), python_flint=version("python-flint")),
            user_accepted=False, aggregate_closed=False))
        b.require(len(json.dumps(record, indent=2).encode()) < 10_000_000, "compact preparation budget exceeded")
        b.write_new(args.output, record)
        print(json.dumps(status(manifest, record), indent=2))


if __name__ == "__main__":
    main()

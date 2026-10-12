"""C_CI deep single-event subjects, using the accepted full joint-root checker.

Only --run executes new events/steps. Retained checks consume saved operands;
--recheck-numerics additionally recomputes interval equations and predictions.
No C_OS numerical evidence, successive-event or arbitrary-depth credit.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from contextlib import ExitStack
from copy import deepcopy
from importlib.metadata import version
import json
import platform
from unittest.mock import patch

import p984c_cci_runtime as previous
import p984d_cos as construction
import p984d_cci_certificate as certificate

r, b = previous.r, previous.b
SELF = b.HERE + "p984d_cci.py"
TEST = b.HERE + "test_p984d_cci.py"
INPUTS = b.BASE + "P9-8.4d-CCICases.json"
RESULTS = b.BASE + "P9-8.4d-CCIResults.json"
REVIEW = b.BASE + "P9-8.4d-CCIReview.md"


def predecessor():
    manifest = b.read(previous.INPUTS)
    b.check_digest(manifest)
    b.check_bindings(manifest["source_bindings"])
    review = (b.ROOT / previous.REVIEW).read_text()
    b.require(b.sha(review.encode()) == "3707b3f42692eb76f31ea86ee573de0b13078fb4f386cb8f1c9ddb829bdd1fa7", "C_CI acceptance drift")
    b.require("## Scoped user acceptance" in review, "C_CI predecessor not accepted")
    _, old = previous.preparation.predecessor()
    b.require(old["shared"]["actual_source"] == manifest["expected_source"], "source reuse drift")
    return manifest, old["shared"]


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
        case.update(case_id=layout["id"] + "::C_CI", fixture_id=layout["id"],
            subject_kind="named_deep_single_event_companion",
            coverage_binding=dict(record_digest=b.digest(layouts),
                cell_ids=[layout["id"] + "::C_CI::" + role for role in r.ROLES]),
            execution_budget_seconds=1800,
            changes_from_frozen=["deep_layout", "explicit_depth_dependent_simplex_tuple", "fresh_event_identity", "operational_budget_only"])
        case["request"].update(target_effective_degree=layout["degree"],
            module_chirality=layout["chirality"], growth_phase=layout["phase"],
            resource_distribution=layout["shares"], operation_id="p984d-cci-" + layout["id"])
        case["oracle"] = construction.previous.target_oracle(old["expected_source"], template, case["request"], layout)
        case["mechanics"] = construction.mechanics(layout)
        cases.append(case)
    paths = {v["path"] for v in old["source_bindings"]} | {
        SELF, TEST, previous.SELF, previous.INPUTS, previous.REVIEW,
        b.HERE + "p984d_cci_certificate.py",
        construction.SELF, construction.previous.SELF,
        previous.preparation.previous.RESULTS,
    }
    return b.seal(dict(schema="p984d-cci-inputs-v1", family="C_CI",
        source_bindings=b.bind(sorted(paths)), initial_inputs=old["initial_inputs"],
        expected_source=old["expected_source"], layouts=layouts, cases=cases,
        source_execution=dict(path=previous.preparation.previous.RESULTS,
            shared_digest=b.digest(shared), new_source_steps=0),
        scope=dict(required_cases=20, required_history_cells=40, target_beats_per_role=10,
            successive_events=False, arbitrary_depth=False, retention_budget_bytes=64_000_000,
            consumer="p984b_cci_runtime.validate, check_root/check_step/check_event; lossless compact expansion"),
        user_accepted=False, aggregate_closed=False))


def check_manifest(manifest):
    b.check_digest(manifest)
    b.check_bindings(manifest["source_bindings"])
    b.require(manifest == make_manifest(), "deep C_CI subjects/law/budget drift")


def status(manifest, record):
    check_manifest(manifest)
    b.check_digest(record)
    b.require(record["schema"] == "p984d-cci-results-v1"
        and record["manifest_digest"] == manifest["record_digest"]
        and record["user_accepted"] is False and record["aggregate_closed"] is False, "result scope drift")
    execution = previous.expand(record["execution"])
    b.check_digest(execution)
    b.require(execution["manifest_digest"] == manifest["record_digest"]
        and execution["native_runtime_executed"] is True
        and execution["user_accepted"] is False and execution["aggregate_closed"] is False,
        "execution scope drift")
    _, shared = predecessor()
    b.require(execution["shared"] == shared, "shared source drift")
    rows = execution["cases"]
    b.require([v["case_id"] for v in rows] == [c["case_id"] for c in manifest["cases"]], "case roster drift")
    for case, row in zip(manifest["cases"], rows, strict=True):
        b.require(row["input_digest"] == b.digest(case) and row["coverage_binding"] == case["coverage_binding"]
            and row["user_accepted"] is False and row["aggregate_closed"] is False, "case input/scope drift")
        b.require(row["case_passed"] is True and row["outcome"] == "passed_named_case"
            and row["event_committed"] is True and row["first_failure"] is None,
            "not a completed successful campaign; an event alone is insufficient")
        b.require([(v["role"], v["index"]) for v in row["continuation"]]
            == [(role, i) for role in r.ROLES for i in range(1, 11)]
            and set(row["final_reads"]) == set(r.ROLES), "incomplete native schedule")
    return dict(family="C_CI", status="implemented_pending_acceptance", native_cases=20,
        passed_cases=20, required_cells=40, successful_history_cells=40,
        accepted_cells=0, passing_pending_cells=40, target_steps=400, final_reads=40,
        degrees=list(construction.DEGREES), maximum_core_depth=4,
        native_trajectories_rerun=False, interval_equations_recomputed=False,
        successive_events=False, arbitrary_depth=False, user_accepted=False, aggregate_closed=False)


def check(manifest, record, *, numerics=False):
    summary = status(manifest, record)
    execution = previous.expand(record["execution"])
    for case, row in zip(manifest["cases"], execution["cases"], strict=True):
        target = previous.preparation.target_for(manifest, case)
        previous.preparation.check_predictions(target, row["predictions"])
        if numerics:
            b.require(row["predictions"] == r.preflight(target), "prediction drift")
    with certificate.checker():
        checked = r.validate(manifest, execution, numerics=numerics)
    b.require(checked["cases_passed"] == 20, "incomplete captured-consumer validation")
    return dict(summary, retained_integrity="passed", interval_equations_recomputed=numerics)


def run_case(args):
    payload, case = args
    with b.exact_backend(b.ExactBackend.FLINT), certificate.checker():
        row = r.execute_case(r.state(payload), case)
    print(case["case_id"], row["outcome"], round(row["elapsed_seconds"], 2), row["first_failure"], flush=True)
    return row


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--prepare", action="store_true")
    group.add_argument("--run", action="store_true")
    group.add_argument("--check-retained", action="store_true")
    parser.add_argument("--recheck-numerics", action="store_true")
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    b.require(1 <= args.workers <= 4, "workers outside 1..4")
    b.require(not args.recheck_numerics or args.check_retained, "recheck requires retained mode")
    if args.prepare:
        b.write_new(INPUTS, make_manifest())
        print("C_CI 20 deep subjects frozen, no native credit")
        return
    manifest = b.read(INPUTS)
    check_manifest(manifest)
    if args.check_retained:
        with ExitStack() as stack:
            for module, name in ((r, "CandidateCIRoot"), (r, "ProvisionalCandidateCIStep"),
                (r.native, "GRC9V4CCIOperation"), (r.native, "ProvisionalCandidateCIStep")):
                stack.enter_context(patch.object(module, name, side_effect=AssertionError("native producer disabled")))
            print(json.dumps(check(manifest, b.read(RESULTS), numerics=args.recheck_numerics), indent=2))
        return
    b.require(not (b.ROOT / RESULTS).exists(), "refuse to overwrite completed evidence")
    _, shared = predecessor()
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        rows = list(pool.map(run_case, [(shared["actual_source"], c) for c in manifest["cases"]]))
    b.require(all(row["case_passed"] for row in rows), "incomplete campaign: report first failures; do not publish a progress dump")
    execution = b.seal(dict(manifest_digest=manifest["record_digest"], shared=shared, cases=rows,
        native_runtime_executed=True, user_accepted=False, aggregate_closed=False))
    packed = previous.compact(execution)
    b.require(previous.expand(packed) == execution, "lossy compaction")
    record = b.seal(dict(schema="p984d-cci-results-v1", manifest_digest=manifest["record_digest"],
        execution=packed, environment=dict(python=platform.python_version(), numpy=version("numpy"),
            mpmath=version("mpmath"), python_flint=version("python-flint"), workers=args.workers),
        user_accepted=False, aggregate_closed=False))
    b.require(len(json.dumps(record, indent=2).encode()) < manifest["scope"]["retention_budget_bytes"], "retention budget exceeded")
    print(json.dumps(check(manifest, record), indent=2))
    b.write_new(RESULTS, record)


if __name__ == "__main__":
    main()

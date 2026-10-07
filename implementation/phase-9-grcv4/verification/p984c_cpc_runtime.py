"""C_PC capacity-boundary campaign using the accepted carrier law/comparator.

Thirty new native cases, two exact D45 reuses; no new scientific declaration.
Nominal predictions precede each event. Saved read/step operands support
independent pointwise interval and signed Read-Back rechecking, not a uniform
parameter or accumulated trajectory error theorem.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from contextlib import ExitStack
from copy import deepcopy
from importlib.metadata import version
import json
import platform
from unittest.mock import patch

import p984b_cpc_runtime as r
import p984b_cpc_pressure as signed
import p984c_cos as construction
import prepare_p984c_boundaries as boundary
from p984c_cci_runtime import compact, expand

b = r.b
SELF = b.HERE + "p984c_cpc_runtime.py"
TEST = b.HERE + "test_p984c_cpc_runtime.py"
INPUTS = b.BASE + "P9-8.4c-CPCCases.json"
RESULTS = b.BASE + "P9-8.4c-CPCResults.json"
REVIEW = b.BASE + "P9-8.4c-CPCRuntimeReview.md"
ACCEPTANCE_SHA = "4343ca0bc237f1627c2a8a7a724f04b4174b5bc69fc95c6aab3a3cfa1f0f1d27"
PREDECESSOR_DIGEST = "58ce40b25febdc95c9ec7d1212c744c7d31df707d639eb6f64be1333818bc129"


def predecessor():
    b.require(b.sha((b.ROOT / r.REVIEW).read_bytes()) == ACCEPTANCE_SHA, "C_PC predecessor acceptance drift")
    manifest, result = b.read(r.INPUTS), b.read(r.RESULTS)
    b.check_digest(manifest)
    b.check_bindings(manifest["source_bindings"])
    b.check_digest(result)
    b.require(result["record_digest"] == PREDECESSOR_DIGEST
        and result["manifest_digest"] == manifest["record_digest"]
        and len(result["cases"]) == 17 and all(v["case_passed"] for v in result["cases"])
        and result["shared"]["actual_source"] == manifest["expected_source"], "incomplete accepted C_PC predecessor")
    return manifest, result


def make_manifest():
    old, result = predecessor()
    contract = b.read(boundary.OUTPUT)
    b.check_digest(contract)
    family = next(v for v in contract["families"] if v["family"] == "C_PC")
    cases, reuse = [], []
    for layout in contract["layouts"]:
        template = next(c for c in old["cases"] if
            (c["request"]["target_effective_degree"], c["request"]["module_chirality"], c["request"]["growth_phase"])
            == (45 if layout["degree"] == 45 else 31, layout["chirality"], layout["phase"]))
        case = deepcopy(template)
        case.update(case_id=layout["id"] + "::C_PC", fixture_id=layout["id"],
            subject_kind="native_boundary_companion",
            coverage_binding=dict(record_digest=contract["record_digest"],
                cell_ids=[layout["id"] + "::C_PC::" + role for role in r.ROLES]),
            comparison=family["comparison"], execution_budget_seconds=family["execution_budget_seconds"],
            changes_from_frozen=["boundary_layout_and_event_identity_only"])
        case["request"]["target_effective_degree"] = layout["degree"]
        if layout["degree"] != 45:
            case["request"]["operation_id"] = "p984c-cpc-" + layout["id"]
        case["oracle"] = construction.target_oracle(old["expected_source"], template, case["request"], layout)
        recipe = next(v for v in contract["cases"] if v["id"] == case["case_id"])["request_recipe"]
        b.require(case["request"]["resource_distribution"] == recipe["resource_distribution"], "boundary shares drift")
        if layout["degree"] == 45:
            for key in ("request", "oracle", "schedule", "comparison", "execution_budget_seconds"):
                b.require(case[key] == template[key], "D45 scientific operand drift: " + key)
            reuse.append(dict(case_id=case["case_id"], previous_case_id=template["case_id"]))
        cases.append(case)
    paths = {v["path"] for v in old["source_bindings"]} | {
        SELF, TEST, r.INPUTS, r.RESULTS, r.REVIEW, signed.SELF, construction.SELF,
        boundary.OUTPUT, b.HERE + "p984c_cci_runtime.py", "tests/models/test_grc_9_v4_expansion.py"}
    return b.seal(dict(schema="p984c-cpc-runtime-inputs-v1", family="C_PC",
        initial_inputs=old["initial_inputs"], expected_source=old["expected_source"],
        source_bindings=b.bind(sorted(paths)), boundary_digest=contract["record_digest"],
        cases=cases, exact_reuse=reuse,
        source_execution=dict(path=r.RESULTS, record_digest=result["record_digest"],
            shared_digest=b.digest(result["shared"]), new_source_steps=0),
        user_accepted=False, aggregate_closed=False))


def check_manifest(manifest):
    b.check_digest(manifest)
    b.check_bindings(manifest["source_bindings"])
    b.require(manifest == make_manifest(), "boundary manifest drift")


def reuse_rows(manifest, shared):
    old_manifest, old = predecessor()
    b.require(shared == old["shared"], "accepted source drift")
    links = []
    for link in manifest["exact_reuse"]:
        original = next(v for v in old_manifest["cases"] if v["case_id"] == link["previous_case_id"])
        row = next(v for v in old["cases"] if v["case_id"] == link["previous_case_id"])
        case = next(v for v in manifest["cases"] if v["case_id"] == link["case_id"])
        for key in ("request", "oracle", "schedule", "comparison", "execution_budget_seconds"):
            b.require(case[key] == original[key], "D45 exact scientific reuse drift")
        b.require(row["case_passed"] and row["event_committed"] and row["first_failure"] is None, "incomplete reuse")
        links.append(dict(**link, previous_record_digest=old["record_digest"], previous_row_digest=b.digest(row)))
    return links


def materialize(manifest, record):
    execution = expand(record["execution"])
    b.check_digest(execution)
    _, old = predecessor()
    rows = {v["case_id"]: v for v in execution["cases"]}
    for link in record["reuse"]:
        original = next(v for v in old["cases"] if v["case_id"] == link["previous_case_id"])
        case = next(v for v in manifest["cases"] if v["case_id"] == link["case_id"])
        rows[case["case_id"]] = dict(deepcopy(original), case_id=case["case_id"],
            input_digest=b.digest(case), coverage_binding=case["coverage_binding"])
    return b.seal(dict(execution, cases=[rows[c["case_id"]] for c in manifest["cases"]]))


def status(manifest, record):
    check_manifest(manifest)
    b.check_digest(record)
    b.require(record["schema"] == "p984c-cpc-runtime-results-v1"
        and record["manifest_digest"] == manifest["record_digest"]
        and record["user_accepted"] is False and record["aggregate_closed"] is False, "runtime scope drift")
    execution = expand(record["execution"])
    b.check_digest(execution)
    b.require(execution["manifest_digest"] == manifest["record_digest"]
        and execution["native_runtime_executed"] is True
        and execution["user_accepted"] is False and execution["aggregate_closed"] is False, "execution scope drift")
    b.require(record["reuse"] == reuse_rows(manifest, execution["shared"]), "reuse lineage drift")
    reused = {v["case_id"] for v in record["reuse"]}
    wanted = [v for v in manifest["cases"] if v["case_id"] not in reused]
    b.require([v["case_id"] for v in execution["cases"]] == [v["case_id"] for v in wanted], "native case roster drift")
    for case, row in zip(wanted, execution["cases"], strict=True):
        b.require(row["input_digest"] == b.digest(case)
            and row["coverage_binding"] == case["coverage_binding"]
            and row["user_accepted"] is False and row["aggregate_closed"] is False, "case scope/input drift")
        success = row["outcome"] == "passed_named_case"
        b.require(row["case_passed"] is success, "event/case conflation")
        if success:
            b.require(row["event_committed"] is True and row["first_failure"] is None
                and [(v["role"], v["index"]) for v in row["continuation"]]
                == [(role, i) for role in r.ROLES for i in range(1, 11)]
                and set(row["final_reads"]) == set(r.ROLES), "incomplete native schedule")
        else:
            b.require(row["outcome"] == "incomplete_case" and row["first_failure"] is not None, "hidden native failure")
    passed = sum(v["case_passed"] for v in execution["cases"])
    return dict(family="C_PC", native_cases=len(wanted), passed_cases=passed,
        exact_reuse_cases=len(reused), successful_history_cells=2*(passed+len(reused)),
        accepted_cells=0, native_trajectories_rerun=False, interval_equations_recomputed=False,
        cases=[{k: row[k] for k in ("case_id", "case_passed", "event_committed", "first_failure")} for row in execution["cases"]])


def vectors(manifest, execution, retained=None, *, numerics=False):
    """Certify each distinct signed intermediate; outer products hide signs."""
    rows = {}
    for _, before, value in signed.read_rows(manifest, execution):
        key = b.digest([before.identity, value["record_digest"]])
        if key in rows:
            continue
        if retained is None or numerics:
            certificate = signed.check_vectors(before, value)
            if retained is not None:
                b.require(certificate == retained[key], "signed certificate drift")
        else:
            certificate = retained[key]
        b.require(certificate["input_identity"] == before.identity
            and certificate["read_record_digest"] == value["record_digest"]
            and all(0 <= r.Q(certificate[k]) < signed.LIMIT for k in ("readback_error", "flat_error")),
            "signed certificate binding or error budget drift")
        rows[key] = certificate
    b.require(retained is None or set(rows) == set(retained), "signed certificate roster drift")
    return rows


def check(manifest, record, *, numerics=False):
    summary = status(manifest, record)
    execution = materialize(manifest, record)
    checked = r.validate(manifest, execution, numerics=numerics)
    # Saved predictions are checked against their independent producer, not
    # merely compared with the native values they purport to predict.
    for case, row in zip(manifest["cases"], execution["cases"], strict=True):
        b.require(row["predictions"] == r.preflight(r.independent_target(manifest, case)), "nominal prediction drift")
    certificates = vectors(manifest, execution, record["signed_read_certificates"], numerics=numerics)
    return {**summary, **checked, "cases_required": len(manifest["cases"]), "signed_reads": len(certificates)}


def run_case(job):
    shared, case = job
    with b.exact_backend(b.ExactBackend.FLINT):
        row = r.execute_case(r.state(shared["actual_source"]), case)
    print(case["case_id"], row["outcome"], row["first_failure"], flush=True)
    return row


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--prepare", action="store_true")
    mode.add_argument("--run", action="store_true")
    mode.add_argument("--check-retained", action="store_true")
    parser.add_argument("--recheck-numerics", action="store_true")
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    b.require(not args.recheck_numerics or args.check_retained, "recheck requires retained mode")
    b.require(1 <= args.workers <= 8, "worker count outside 1..8")
    if args.prepare:
        r.write_new(INPUTS, make_manifest())
        print("C_PC boundary inputs frozen; no native execution")
        return
    manifest = b.read(INPUTS)
    check_manifest(manifest)
    if args.check_retained:
        with ExitStack() as stack:
            for module, name in ((r, "CandidatePCRead"), (r, "ProvisionalCandidatePCStep"),
                    (r.native, "GRC9V4CPCOperation")):
                stack.enter_context(patch.object(module, name, side_effect=AssertionError("native producer disabled")))
            print(json.dumps(check(manifest, b.read(RESULTS), numerics=args.recheck_numerics), indent=2))
        return
    b.require(not (b.ROOT / RESULTS).exists(), "refuse to overwrite retained execution")
    _, old = predecessor()
    shared = old["shared"]
    reused = {v["case_id"] for v in manifest["exact_reuse"]}
    jobs = [(shared, c) for c in manifest["cases"] if c["case_id"] not in reused]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        rows = list(pool.map(run_case, jobs))
    b.require(all(v["case_passed"] for v in rows), "incomplete campaign; no final evidence published")
    execution = b.seal(dict(manifest_digest=manifest["record_digest"], shared=shared, cases=rows,
        native_runtime_executed=True, user_accepted=False, aggregate_closed=False))
    record = dict(schema="p984c-cpc-runtime-results-v1", manifest_digest=manifest["record_digest"],
        environment=dict(python=platform.python_version(), numpy=version("numpy"),
            mpmath=version("mpmath"), python_flint=version("python-flint")),
        execution=compact(execution), reuse=reuse_rows(manifest, shared),
        user_accepted=False, aggregate_closed=False)
    record["signed_read_certificates"] = vectors(manifest, materialize(manifest, record))
    record = b.seal(record)
    summary = check(manifest, record)
    b.require(len(b.canonical_json_bytes(record)) < 64_000_000, "retention budget exceeded")
    r.write_new(RESULTS, record)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

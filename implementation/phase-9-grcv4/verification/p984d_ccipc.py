"""Seventh-realization deep C_CI_PC campaign, with independent signed equations.

The accepted small declarations supply data only. Every source step, event,
ten-step current/reset continuation and final read is executed afresh. Frozen
predecessor records are never rewritten or promoted to new evidence.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor
from copy import deepcopy
import json
import lzma
from pathlib import Path
import time

import p984b_ccipc_runtime as r
import p984c_ccipc_runtime as previous
import p984c_cos as construction
import p984d_cos as layouts
from p9_ccipc_compute import worker
from p9_ccipc_capture import portable
from unittest.mock import patch

b = r.b
SELF = b.HERE + "p984d_ccipc.py"
INPUTS = b.BASE + "P9-8.4d-CCIPCCases.json"
RESULTS = b.BASE + "P9-8.4d-CCIPCResults.json.xz"
PREFLIGHT = b.BASE + "P9-8.4d-CCIPCPreflight.json"


def read(path):
    p = b.ROOT / path
    return json.loads(lzma.decompress(p.read_bytes()) if p.suffix == ".xz" else p.read_bytes())


def save(path, value):
    raw = json.dumps(portable(value), separators=(",", ":"), allow_nan=False).encode() + b"\n"
    if str(path).endswith(".xz"):
        raw = lzma.compress(raw)
    with (b.ROOT / path).open("xb") as stream:
        stream.write(raw)


def numerical_paths():
    # Public registration and subsequent UI wiring do not alter these equations.
    omitted = {"grc_9_v4_api_lifecycle.py", "grc_9_v4_legacy.py", "grc_9_v4_owner.py"}
    paths = {str(p.relative_to(b.ROOT)) for p in (b.ROOT / "src/pygrc/models").glob("grc*v4*.py")
             if p.name not in omitted}
    paths |= {SELF, r.SELF, previous.SELF, construction.SELF,
              layouts.SELF, b.SELF, b.HERE + "p984b_cci_runtime.py",
              b.HERE + "p984c_cci_runtime.py", b.HERE + "p9_ccipc_compute.py", b.HERE + "p9_ccipc_capture.py",
              b.HERE + "verify_p983ccipc_native.py", b.HERE + "p984b_cpc_runtime.py",
              b.HERE + "p9_cpc_compute.py", b.HERE + "p9_cpc_covariance_compute.py",
              b.HERE + "p9_cpc_wire_reuse.py", b.HERE + "p984h_cpc.py",
              b.HERE + "p984h_validation_reuse.py", b.HERE + "test_p980_os_effect_witness.py",
              b.HERE + "test_p980_os_numerical_feasibility.py",
              "tests/models/test_grc_9_v4_lifecycle.py", "tests/models/test_grc_9_v4_expansion.py",
              r.INPUTS, previous.INPUTS}
    return paths


def make_manifest():
    old, boundary = read(r.INPUTS), read(previous.INPUTS)
    b.check_digest(old)
    b.check_digest(boundary)
    b.require(old["expected_source"] == boundary["expected_source"], "predecessor source drift")
    declared = layouts.layouts()
    # The inherited D94 shares sum to one, but their three rounded products
    # lose 2^-52 at the actual evolved C_CI_PC source. This nearby dyadic simplex
    # preserves the exact represented charge and passes both-role feasibility.
    for layout in declared:
        if layout["degree"] == 94:
            layout["shares"] = [{17: 1087, 24: 1537, 23: 1472}[round(x*64)] / 4096
                                for x in layout["shares"]]
    cases = []
    for layout in declared:
        template = deepcopy(next(c for c in old["cases"] if
            c["request"]["module_chirality"] == layout["chirality"]
            and c["request"]["growth_phase"] == 1))
        template["oracle"]["event_identity"]["resource_distribution"] = layout["shares"]
        case = deepcopy(template)
        case.update(case_id=layout["id"] + "::C_CI_PC", fixture_id=layout["id"],
                    subject_kind="named_deep_single_event_companion", execution_budget_seconds=900,
                    coverage_binding=dict(record_digest=b.digest(declared),
                        cell_ids=[layout["id"] + "::C_CI_PC::" + role for role in r.ROLES]))
        case["request"].update(target_effective_degree=layout["degree"],
            module_chirality=layout["chirality"], growth_phase=layout["phase"],
            resource_distribution=layout["shares"], operation_id="p984d-ccipc-" + layout["id"])
        case["oracle"] = construction.target_oracle(old["expected_source"], template, case["request"], layout)
        case["independent_target_chart"] = r.chart_record(r.independent_target(old, case))
        cases.append(case)
    return b.seal(dict(schema="p984d-ccipc-inputs-v1", family="C_CI_PC",
        source_bindings=b.bind(sorted(numerical_paths())),
        predecessor_inputs=[old["record_digest"], boundary["record_digest"]],
        layouts=[dict(layout=v, mechanics=layouts.mechanics(v)) for v in declared],
        allocation_note="D94: 17/64,24/64,23/64 -> 1087/4096,1537/4096,1472/4096 in branch order; exact represented charge",
        initial_inputs=old["initial_inputs"], expected_source=old["expected_source"], cases=cases,
        exact_backend="flint", user_accepted=False, aggregate_closed=False))


def check_manifest(m):
    b.check_digest(m)
    b.check_bindings(m["source_bindings"])
    b.require(m == make_manifest(), "deep C_CI_PC declaration drift")


def preflight(m):
    check_manifest(m)
    start = time.monotonic()
    with worker() as policy:
        rows = []
        for c in m['cases']:
            target = r.independent_target(m, c)
            predictions = r.preflight(target)
            rows.append(dict(case_id=c['case_id'], input_digest=b.digest(target.to_payload()),
                             predictions=predictions, prediction_digest=b.digest(predictions)))
            print('preflight', c['case_id'], flush=True)
    return b.seal(dict(schema="p984d-ccipc-preflight-v1", manifest_digest=m["record_digest"],
        policy=policy, cases=rows, elapsed_seconds=time.monotonic()-start,
        native_runtime_executed=False, user_accepted=False))


def execute(job):
    source, case, prediction = job
    def reused(target):
        b.require(b.digest(target.to_payload()) == prediction['input_digest'], 'preflight operand drift')
        b.require(b.digest(prediction['predictions']) == prediction['prediction_digest'], 'preflight result drift')
        return deepcopy(prediction['predictions'])
    with worker(), patch.object(r, 'preflight', reused):
        row = portable(r.execute_case(r.state(source), case))
    print(row['case_id'], row['outcome'], row['first_failure'], round(row['elapsed_seconds'], 3), flush=True)
    return row


def check(m, record, *, numerics=False):
    check_manifest(m)
    b.check_digest(record)
    b.require(record["schema"] == "p984d-ccipc-results-v1"
        and record["manifest_digest"] == m["record_digest"]
        and not record["user_accepted"] and not record["aggregate_closed"], "scope drift")
    execution = previous.expand(record["execution"])
    with worker():
        status = r.validate(m, execution, numerics=numerics)
        predictions = {v['case_id']: v for v in read(PREFLIGHT)['cases']}
        for case, row in zip(m['cases'], execution['cases'], strict=True):
            retained = predictions[case['case_id']]
            b.require(row['predictions'] == retained['predictions'], 'nominal prediction drift')
            if numerics:
                b.require(row['predictions'] == r.preflight(r.independent_target(m, case)), 'nominal equation drift')

    b.require(status["cases_passed"] == 20, "incomplete deep campaign")
    return dict(status, cases_required=20, signed_checks="full_joint_root_certificates")


def run(m, workers):
    check_manifest(m)
    b.require(not (b.ROOT / RESULTS).exists(), "refuse overwrite")
    p = read(PREFLIGHT)
    b.check_digest(p)
    b.require(p["manifest_digest"] == m["record_digest"] and len(p["cases"]) == 20, "preflight required")
    journal = b.ROOT / "implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool/generated/phase9-verification" / ('ccipc-deep-' + m['record_digest'])
    journal.mkdir(parents=True, exist_ok=True)
    def keep(name, value):
        record = b.seal(dict(manifest_digest=m['record_digest'], value=portable(value)))
        save(journal / (name+'.json.xz'), record)
    def retained(name):
        path = journal / (name+'.json.xz')
        if not path.exists(): return None
        record = read(path); b.check_digest(record)
        b.require(record['manifest_digest'] == m['record_digest'], 'journal manifest drift')
        return record['value']
    with worker() as policy:
        shared = retained('source')
        if shared is None:
            shared, _ = r.run_source(m)
            keep('source', shared)
        else:
            r.check_step(b.GeometryStageInputs.from_payload(m['initial_inputs']), shared['source_step'])
            b.require(shared['actual_source'] == m['expected_source'], 'journal source drift')
    predictions = {v['case_id']: v for v in p['cases']}
    jobs = [(shared['actual_source'], c, predictions[c['case_id']]) for c in m['cases']]
    rows = {}
    for _, case, _ in jobs:
        row = retained(case['fixture_id'])
        if row is not None:
            b.require(row['input_digest'] == b.digest(case) and row['case_passed'], 'journal case incomplete')
            rows[row['case_id']] = row
    first = next(j for j in jobs if j[1]['fixture_id'] == 'P984D-D94-E1-P1')
    if first[1]['case_id'] not in rows:
        pilot = execute(first); keep(first[1]['fixture_id'], pilot)
        b.require(pilot['case_passed'], 'deepest C_CI_PC pilot failed')
        rows[pilot['case_id']] = pilot
    with ProcessPoolExecutor(max_workers=workers) as pool:
        remaining = [j for j in jobs if j[1]['case_id'] not in rows]
        for job, row in zip(remaining, pool.map(execute, remaining), strict=True):
            keep(job[1]['fixture_id'], row)
            rows[row['case_id']] = row
    b.require(all(row["case_passed"] for row in rows.values()), "incomplete campaign")
    execution = b.seal(dict(manifest_digest=m["record_digest"], shared=shared,
        cases=[rows[c["case_id"]] for c in m["cases"]], native_runtime_executed=True,
        user_accepted=False, aggregate_closed=False))
    packed = previous.compact(execution)
    b.require(previous.expand(packed) == execution, "lossy compaction")
    record = b.seal(dict(schema="p984d-ccipc-results-v1", manifest_digest=m["record_digest"],
        preflight_digest=p["record_digest"], policy=policy, execution=packed,
        user_accepted=False, aggregate_closed=False))
    status = check(m, record)
    save(RESULTS, record)
    return status


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("prepare", "preflight", "run", "check"))
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--numerics", action="store_true")
    args = parser.parse_args()
    b.require(1 <= args.workers <= 4, "workers outside 1..4")
    if args.action == "prepare":
        save(INPUTS, make_manifest())
    elif args.action == "preflight":
        result = preflight(read(INPUTS))
        save(PREFLIGHT, result)
        print(json.dumps(result, indent=2))
    else:
        print(json.dumps(run(read(INPUTS), args.workers) if args.action == "run"
                         else check(read(INPUTS), read(RESULTS), numerics=args.numerics), indent=2))

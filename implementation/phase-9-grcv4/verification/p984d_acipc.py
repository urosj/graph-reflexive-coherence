"""Eighth-realization deep A_CI_PC campaign, with independent signed equations.

The accepted small declarations supply data only. Every source step, event,
ten-step current/reset continuation and final read is executed afresh. Frozen
predecessor records are never rewritten or promoted to new evidence.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from copy import deepcopy
import json
import lzma
from pathlib import Path
import time

import p984b_acipc_runtime as r
import p984c_acipc_runtime as previous
import p984c_cos as construction
import p984d_cos as layouts
from p9_acipc_compute import worker
from p9_ccipc_capture import portable
from unittest.mock import patch
import p984d_acipc_feasibility as feasibility

b = r.b
SELF = b.HERE + "p984d_acipc.py"
INPUTS = b.BASE + "P9-8.4d-ACIPCCases.json"
RESULTS = b.BASE + "P9-8.4d-ACIPCResults.json.xz"
PREFLIGHT = b.BASE + "P9-8.4d-ACIPCPreflight.json"


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
              b.HERE + "p984c_cci_runtime.py", b.HERE + "p9_acipc_compute.py", b.HERE + "p9_ccipc_capture.py",
              b.HERE + "verify_p983acipc_native.py", b.HERE + "p984b_cpc_runtime.py",
              b.HERE + "p9_cpc_compute.py", b.HERE + "p9_cpc_covariance_compute.py",
              b.HERE + "p9_cpc_wire_reuse.py", b.HERE + "p984h_cpc.py",
              b.HERE + "p984h_validation_reuse.py", b.HERE + "test_p980_os_effect_witness.py",
              b.HERE + "test_p980_os_numerical_feasibility.py",
              "tests/models/test_grc_9_v4_lifecycle.py", "tests/models/test_grc_9_v4_expansion.py",
              r.INPUTS, previous.INPUTS, feasibility.SELF, feasibility.SOURCE,
              b.HERE+"p984d_apc_joint.py",b.HERE+"p984d_apc_feasibility.py"}
    paths |= {ref["path"] for ref in read(r.INPUTS)["source_bindings"]}
    return paths


def make_manifest():
    old, boundary = read(r.INPUTS), read(previous.INPUTS)
    b.check_digest(old)
    b.check_digest(boundary)
    b.require(old["initial_inputs"] == boundary["initial_inputs"], "predecessor source drift")
    companion = read(feasibility.SOURCE)
    b.check_digest(companion)
    b.check_bindings(companion['source_bindings'])
    old["expected_source"]=boundary["expected_source"]
    companion_fields={key:companion[key] for key in ("initial_inputs","nominal_source","expected_source")}
    declared = layouts.layouts()
    cases = []
    for layout in declared:
        seed=r.state(companion["expected_source"] if layout["degree"]==94 else old["expected_source"])
        template = deepcopy(next(c for c in old["cases"] if
            c["request"]["module_chirality"] == layout["chirality"]
            and c["request"]["growth_phase"] == 1))
        template["oracle"]["event_identity"]["resource_distribution"] = layout["shares"]
        case = deepcopy(template)
        case.update(case_id=layout["id"] + "::A_CI_PC", fixture_id=layout["id"],
                    subject_kind="named_deep_single_event_companion", execution_budget_seconds=3600,
                    coverage_binding=dict(record_digest=b.digest(declared),
                        cell_ids=[layout["id"] + "::A_CI_PC::" + role for role in r.ROLES]))
        case["request"].update(target_effective_degree=layout["degree"],
            module_chirality=layout["chirality"], growth_phase=layout["phase"],
            resource_distribution=layout["shares"], operation_id="p984d-acipc-" + layout["id"])
        if layout['degree'] == 94:
            selected = feasibility.derive(seed,case,layout)
            layout['shares'] = selected['shares']
            case['allocation_selection'] = selected['selection']
        case = feasibility.rebind(seed,case,layout)
        case["independent_whole_chart"] = r.oracle.whole_chart(case["oracle"]["target_graph"])
        cases.append(case)
    return b.seal(dict(schema="p984d-acipc-inputs-v1", family="A_CI_PC",
        source_bindings=b.bind(sorted(numerical_paths())),
        predecessor_inputs=[old["record_digest"], boundary["record_digest"]],
        layouts=[dict(layout=v, mechanics=layouts.mechanics(v)) for v in declared],
        allocation_note="Frozen D94 current first step is negative; stronger current W history and ten-step frozen-W inequalities select a separate companion, with full enabled interval preflight still required.",
        source_companion_digest=companion['record_digest'],companion_fields=companion_fields,
        source_selection="original_for_D59_D66_D73_companion_for_D94",
        nominal_source=old["nominal_source"],
        initial_inputs=old["initial_inputs"], expected_source=old["expected_source"], cases=cases,
        exact_backend="flint", user_accepted=False, aggregate_closed=False))


def check_manifest(m):
    b.check_digest(m)
    b.check_bindings(m["source_bindings"])
    b.require(m == make_manifest(), "deep A_CI_PC declaration drift")


def selected_manifest(m,case):
    return dict(m,**m["companion_fields"]) if case["request"]["target_effective_degree"]==94 else m


def preflight_case(job):
    m, c = job
    m=selected_manifest(m,c)
    with worker():
        target = r.independent_target(r.state(m["expected_source"]), c)
        predictions = r.preflight(target)
        row = dict(case_id=c['case_id'], input_digest=b.digest(target.to_payload()),
                   predictions=predictions, prediction_digest=b.digest(predictions))
    print('preflight', c['case_id'], flush=True)
    return row


def preflight(m, workers=4):
    check_manifest(m)
    start = time.monotonic()
    journal = b.ROOT / 'implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool/generated/phase9-verification' / ('acipc-preflight-'+m['record_digest'])
    journal.mkdir(parents=True,exist_ok=True)
    rows = {}
    for c in m['cases']:
        path=journal/(c['fixture_id']+'.json.xz')
        if path.exists():
            row=read(path)
            b.require(row['case_id']==c['case_id'] and row['input_digest']==b.digest(r.independent_target(r.state(selected_manifest(m,c)['expected_source']),c).to_payload())
                      and row['prediction_digest']==b.digest(row['predictions']), 'preflight resume binding')
            rows[c['case_id']]=row
    pilot=b.ROOT/(b.BASE+'P9-8.4d-ACIPCPilotPreflight.json')
    if pilot.exists():
        row=read(pilot); c=next(c for c in m['cases'] if c['case_id']==row['case_id'])
        b.require(row['input_digest']==b.digest(r.independent_target(r.state(selected_manifest(m,c)['expected_source']),c).to_payload())
                  and row['prediction_digest']==b.digest(row['predictions']), 'pilot operand binding')
        rows[row['case_id']]=row
    with worker() as policy, ProcessPoolExecutor(max_workers=workers) as pool:
        pending={pool.submit(preflight_case,(m,c)):c for c in m['cases'] if c['case_id'] not in rows}
        for future in as_completed(pending):
            c=pending[future]; row=future.result()
            save(journal/(c['fixture_id']+'.json.xz'),row)
            rows[c['case_id']]=row
    return b.seal(dict(schema="p984d-acipc-preflight-v1", manifest_digest=m["record_digest"],
        policy=policy, cases=[rows[c['case_id']] for c in m['cases']], elapsed_seconds=time.monotonic()-start,
        native_runtime_executed=False, user_accepted=False))


def execute(job):
    m, source, case, prediction = job
    m=selected_manifest(m,case)
    def reused(target):
        b.require(b.digest(target.to_payload()) == prediction['input_digest'], 'preflight operand drift')
        b.require(b.digest(prediction['predictions']) == prediction['prediction_digest'], 'preflight result drift')
        return deepcopy(prediction['predictions'])
    with worker(), previous.data_adapter(m), patch.object(r, 'preflight', reused):
        row = portable(r.execute_case(r.state(source), case))
    print(row['case_id'], row['outcome'], row['first_failure'], round(row['elapsed_seconds'], 3), flush=True)
    return row


def check(m, record, *, numerics=False):
    check_manifest(m)
    b.check_digest(record)
    b.require(record["schema"] == "p984d-acipc-results-v1"
        and record["manifest_digest"] == m["record_digest"]
        and not record["user_accepted"] and not record["aggregate_closed"], "scope drift")
    execution = previous.expand(record["execution"])
    b.check_digest(execution)
    predictions = {v['case_id']:v for v in read(PREFLIGHT)['cases']}
    status=[]
    for companion in (False,True):
        cases=[c for c in m['cases'] if (c['request']['target_effective_degree']==94)==companion]
        local=b.seal(dict(selected_manifest(m,cases[0]),cases=cases))
        rows=[row for row in execution['cases'] if row['case_id'] in {c['case_id'] for c in cases}]
        sub=b.seal(dict(manifest_digest=local['record_digest'],shared=execution['shared_companion' if companion else 'shared'],
            cases=rows,native_runtime_executed=True,user_accepted=False,aggregate_closed=False))
        with worker(),previous.data_adapter(local):status.append(r.validate(local,sub,numerics=numerics))
        for case,row in zip(cases,rows,strict=True):
            b.require(row['predictions']==predictions[case['case_id']]['predictions'],'nominal prediction drift')
            if numerics:
                b.require(row['predictions']==r.preflight(r.independent_target(r.state(local['expected_source']),case)), 'nominal equation drift')
    passed=sum(s['cases_passed'] for s in status)
    b.require(passed==20,'incomplete deep campaign')
    return dict(cases_passed=passed,cases_required=20,source_witnesses=2,target_steps=400,final_reads=40,
        signed_checks='full_joint_root_certificates',retained_integrity='passed',user_accepted=False,aggregate_closed=False)


def run(m, workers):
    check_manifest(m)
    b.require(not (b.ROOT / RESULTS).exists(), "refuse overwrite")
    p = read(PREFLIGHT)
    b.check_digest(p)
    b.require(p["manifest_digest"] == m["record_digest"] and len(p["cases"]) == 20, "preflight required")
    journal = b.ROOT / "implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool/generated/phase9-verification" / ('acipc-deep-' + m['record_digest'])
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
            shared,_=r.run_source(m)
            b.require(shared['actual_source']==m['expected_source'],'source drift')
            keep('source', shared)
        else:
            r.check_step(b.GeometryStageInputs.from_payload(m['initial_inputs']), shared['source_step'])
            b.require(shared['actual_source'] == m['expected_source'], 'journal source drift')
    predictions = {v['case_id']: v for v in p['cases']}
    companion=read(feasibility.SOURCE)['shared']
    jobs = [(m, (companion if c['request']['target_effective_degree']==94 else shared)['actual_source'], c, predictions[c['case_id']]) for c in m['cases']]
    rows = {}
    for _, _, case, _ in jobs:
        row = retained(case['fixture_id'])
        if row is not None:
            b.require(row['input_digest'] == b.digest(case) and row['case_passed'], 'journal case incomplete')
            rows[row['case_id']] = row
    first = next(j for j in jobs if j[2]['fixture_id'] == 'P984D-D94-E1-P1')
    if first[2]['case_id'] not in rows:
        pilot = execute(first); keep(first[2]['fixture_id'], pilot)
        b.require(pilot['case_passed'], 'deepest A_CI_PC pilot failed')
        rows[pilot['case_id']] = pilot
    with ProcessPoolExecutor(max_workers=workers) as pool:
        remaining = [j for j in jobs if j[2]['case_id'] not in rows]
        for job, row in zip(remaining, pool.map(execute, remaining), strict=True):
            keep(job[2]['fixture_id'], row)
            rows[row['case_id']] = row
    b.require(all(row["case_passed"] for row in rows.values()), "incomplete campaign")
    execution = b.seal(dict(manifest_digest=m["record_digest"], shared=shared,shared_companion=companion,
        cases=[rows[c["case_id"]] for c in m["cases"]], native_runtime_executed=True,
        user_accepted=False, aggregate_closed=False))
    packed = previous.compact(execution)
    b.require(previous.expand(packed) == execution, "lossy compaction")
    record = b.seal(dict(schema="p984d-acipc-results-v1", manifest_digest=m["record_digest"],
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
    b.require(1 <= args.workers <= 12, "workers outside 1..12")
    if args.action == "prepare":
        save(INPUTS, make_manifest())
    elif args.action == "preflight":
        result = preflight(read(INPUTS), args.workers)
        save(PREFLIGHT, result)
        print(json.dumps(dict(cases=len(result['cases']),elapsed_seconds=result['elapsed_seconds'])))
    else:
        print(json.dumps(run(read(INPUTS), args.workers) if args.action == "run"
                         else check(read(INPUTS), read(RESULTS), numerics=args.numerics), indent=2))

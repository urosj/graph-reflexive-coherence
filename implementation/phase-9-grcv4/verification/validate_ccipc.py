"""Final source-bound C_CI_PC validation; completed numerical campaigns are consumed."""
import argparse
from contextlib import nullcontext
import json
from pathlib import Path
import time
import unittest
import p9_ccipc_review as review
from p984h_validation_reuse import validation_reuse
import p9_ccipc_integration_compute as integration_compute

b=review.b
SELF=b.HERE+'validate_ccipc.py'
PATH=review.integration.BASE+'P9-CCIPC-Validation.json'
GROUPS={
    'science':('test_p9_ccipc_science','test_p9_ccipc_event_reuse','test_p9_cpc_wire_reuse',
        'test_p984h_validation_reuse','tests.models.test_grc_v4_solve_reuse'),
    'integration':('tests.models.test_grc_9_v4_contracts','tests.models.test_grc_9_v4_architecture',
        'tests.models.test_grc_9_v4_owner','tests.models.test_grc_9_v4_legacy',
        'tests.models.test_grc_9_v4_crossing','tests.models.test_grc_9_v4'),
    'surfaces':('test_p9_ccipc_review','test_p9_aos_acceptance','test_p9_aos_g2_sources',
        'test_p9101c_support_reconciliation'),
}


def run_group(name):
    started=time.monotonic()
    suite=unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromName(mod) for mod in GROUPS[name])
    paths={SELF,integration_compute.SELF,integration_compute.PREFLIGHT}
    if name!='integration':paths.add(review.SELF)
    paths|={p.relative_to(b.ROOT).as_posix() for p in (b.ROOT/'src').rglob('*.py')}
    for module in GROUPS[name]:
        source=__import__(module,fromlist=['__file__']);paths.add(Path(source.__file__).resolve().relative_to(b.ROOT).as_posix())
    refs=b.bind(paths)
    with b.budget(1800), b.exact_backend(b.ExactBackend.FLINT), (integration_compute.worker() if name=='integration' else nullcontext()):
        result=unittest.TextTestRunner(verbosity=2).run(suite)
    b.require(result.wasSuccessful() and (name=='integration' or not result.skipped),'validation group failed: '+name)
    b.check_bindings(refs)
    return b.seal(dict(group=name,modules=list(GROUPS[name]),tests_run=result.testsRun,
        failures=len(result.failures),errors=len(result.errors),
        skipped=[dict(test=str(t),reason=why) for t,why in result.skipped],
        seconds=time.monotonic()-started,cap_seconds=1800,outcome='passed',source_bindings=refs))


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('action',choices=('group','finish'))
    parser.add_argument('--group',choices=GROUPS);parser.add_argument('--output');parser.add_argument('--inputs',nargs='+')
    args=parser.parse_args()
    if args.action=='group':
        b.require(args.output and args.group,'group and output required');value=run_group(args.group)
        with Path(args.output).open('x') as stream:json.dump(value,stream,indent=2);stream.write('\n')
        return
    b.require(args.inputs and len(args.inputs)==len(GROUPS),'three group records required')
    values=[json.loads(Path(name).read_bytes()) for name in args.inputs]
    for value in values:
        b.check_digest(value);b.check_bindings(value['source_bindings'])
        b.require(value['outcome']=='passed' and not value['failures'] and not value['errors'],'validation failure')
    b.require({v['group'] for v in values}==set(GROUPS),'validation roster')
    evidence=review.checked()
    for key in review.integration.GROUPS:review.integration.check(key)
    refs={ref['path']:ref['sha256'] for value in values for ref in value['source_bindings']}
    paths=set(refs)|{SELF,review.PATH}
    record=b.seal(dict(schema='p9-ccipc-validation-v1',groups=values,new_integration_tests=22,
        source_bindings=b.bind(paths),review_digest=evidence['record_digest'],exact_backend='flint',
        outcome='passed',user_accepted=False,aggregate_closed=False))
    b.write_new(PATH,record)
    print(json.dumps(dict(outcome='passed',tests=sum(v['tests_run'] for v in values),new_integration_tests=22)))


if __name__=='__main__':main()

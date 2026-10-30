"""Focused final A_CI_PC regressions; native campaign records are consumed, not rerun."""
import argparse
import json
import time
import unittest
from pathlib import Path
import p9_acipc_review as review
import p9_acipc_integration_compute as compute
b=review.b
SELF=b.HERE+'validate_acipc.py'
PATH=review.integration.BASE+'P9-ACIPC-Validation.json'
GROUPS={'regression':('test_p9_acipc_science','tests.models.test_grc_9_v4_contracts','tests.models.test_grc_9_v4_architecture'),
        'surfaces':('test_p9_acipc_review.ACIPCReviewTests','test_p9_ccipc_acceptance','test_p9_acipc_history')}


def group(name):
    start=time.monotonic();modules=GROUPS[name]
    suite=unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromName(x) for x in modules)
    with compute.worker():result=unittest.TextTestRunner(verbosity=2).run(suite)
    b.require(result.wasSuccessful() and not result.skipped,'focused validation failed')
    return b.seal(dict(group=name,modules=list(modules),tests=result.testsRun,failures=len(result.failures),errors=len(result.errors),
        seconds=time.monotonic()-start,outcome='passed',source_bindings=b.bind({SELF,compute.SELF,review.SELF,
            *(p.relative_to(b.ROOT).as_posix() for p in (b.ROOT/'src').rglob('*.py'))})))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=('group','finish'));p.add_argument('--group',choices=GROUPS);p.add_argument('--output');p.add_argument('--inputs',nargs='+');args=p.parse_args()
    if args.action=='group':
        value=group(args.group);Path(args.output).write_text(json.dumps(value,indent=2)+'\n')
    else:
        rows=[json.loads(Path(x).read_bytes()) for x in args.inputs]
        b.require({r['group'] for r in rows}==set(GROUPS),'group roster')
        for r in rows:b.check_digest(r);b.check_bindings(r['source_bindings']);b.require(r['outcome']=='passed','validation status')
        value=review.checked()
        for k in review.integration.GROUPS:review.integration.check(k)
        final=b.seal(dict(schema='p9-acipc-validation-v1',groups=rows,new_integration_tests=22,
            review_digest=value['record_digest'],source_bindings=b.bind({SELF,review.PATH,*[r['path'] for row in rows for r in row['source_bindings']]}),
            outcome='passed',user_accepted=False,aggregate_closed=False))
        b.write_new(PATH,final);print('A_CI_PC focused validation passed')

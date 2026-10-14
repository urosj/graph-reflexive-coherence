"""Corrected-policy successor; reuse the native runner, never old execution."""
import argparse
import hashlib
from unittest.mock import patch
import p984g_aci_native as base
import p984g_pre_aci_residual_sources as history

ROOT,BASE,HERE=base.ROOT,base.BASE,base.HERE
SELF=HERE+'p984g_aci_native_successor.py'
PLAN=BASE+'P9-8.4g-ACINativeSuccessorPlan.md'
DIRECTORY=BASE+'P9-8.4g-ACINativeSuccessor/'
_BINDINGS=base.bindings


def bindings():
    result=_BINDINGS()
    for name in (SELF,PLAN,HERE+'p984g_pre_aci_residual_sources.py',
                 'tests/models/test_grc_v4_ci_residual_policy.py'):
        result[name]=hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
    return result


def case_path(graph,role):
    base.require((graph,role) in base.CASES,'case roster')
    return DIRECTORY+graph+'-'+role+'.json.xz'


def worker(pipe,graph,role):
    # Only predecessor validation is historical. ProvisionalCandidateCIStep,
    # certificates, residuals and physical operations execute current src/.
    with patch.object(base.oracle,'check_retained',history.check_staged):
        base.worker(pipe,graph,role)


def run(graph,role):
    with patch.object(base,'bindings',bindings),patch.object(base,'case_path',case_path),patch.object(base,'worker',worker):
        base.run(graph,role)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=['run'])
    p.add_argument('--graph',choices=['source','target'],required=True);p.add_argument('--role',choices=['current','reset'],required=True)
    args=p.parse_args();run(args.graph,args.role)

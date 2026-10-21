"""Comparison-only successor: fix local `subject` shadowing, preserve event.

The predecessor completed native steps but raised UnboundLocalError before
retention. No success credit or failed-session artifact follows. This module
changes only the comparison function; every production step still runs fresh.
"""
import argparse
from copy import deepcopy
import json
import lzma
import signal
import time
from unittest.mock import patch
import p984h_cos_covariance as parent

SELF=parent.HERE+'p984h_cos_covariance_continuation.py'
TEST=parent.HERE+'test_p984h_cos_covariance_continuation.py'
INPUTS=parent.BASE+'P9-8.4h-COSCovarianceContinuationInputs.json'


def path(role):
    parent.require(role in parent.ROLES,'unknown role')
    return parent.BASE+f'P9-8.4h-COSCovariance-combined-{role}-successor.json.xz'


def read(role):
    return json.loads(lzma.decompress((parent.ROOT/path(role)).read_bytes()))


def compare_step(kind,role,row,after,geometry):
    _,_,_,eid,expected=parent.subject(kind);d=parent.declaration(kind)
    original=parent.continuation.initial(role);baseline=parent.continuation.read(role,1)
    ni,ei,sign=parent.mapping(original.to_payload()['reference']['graph'],expected.to_payload()['reference']['graph'],d,parent.base()[1]['event_id'],eid)
    errors={stage:parent.compare_point(baseline['observation'][stage],row[stage],ei,sign) for stage in ('predictor','corrector','final')}
    np=parent.native.np
    target=np.asarray(baseline['next_inputs']['current']['C'])[ni]
    parent.require(np.allclose(after.current.C,target,atol=2e-11,rtol=2e-11),'resource covariance')
    parent.require(row['split_admitted'] and min(after.current.C)>0 and after.reset==expected.reset,'target admission/reset')
    dense_subject=dict(graph=original.geometry.reference.graph.port_graph.to_payload(),profile=original.geometry.reference.profile.to_payload())
    incidence,params=parent.native.oracle.old.graph_data(dense_subject)
    h=parent.native.oracle.old.generated_h(incidence,np.array(baseline['observation']['predictor']['causal_flat']),params)
    transported=h[np.ix_(ei,ei)]*np.outer(sign,sign)
    actual=np.array(geometry['corrector'])
    parent.require(np.isfinite(actual).all() and np.allclose(actual,transported,atol=2e-11,rtol=2e-11),'generated geometry covariance')
    for stage in ('predictor','corrector','final'):
        parent.require(parent.digest(geometry[stage])==row[stage]['input_hodge_digest'],'geometry capture identity')
    parent.require(geometry['predictor']==expected.to_payload()['H1_form'] and geometry['final']==geometry['corrector'],'geometry staging')
    return dict(points=errors,resources=float(np.max(abs(np.asarray(after.current.C)-target))),
        generated_geometry=float(np.max(abs(actual-transported))))


def manifest():
    old=parent.native.oracle.old.read(parent.INPUTS)
    parent.require(old==parent.manifest(),'predecessor sources changed')
    m=deepcopy(old);m.pop('record_digest')
    m.update(parent_manifest_digest=old['record_digest'],correction='comparison_local_name_shadowing_only',
        numerical_law_changed=False,parent_event_reexecuted=False)
    for name in (SELF,TEST,parent.INPUTS,parent.path('combined','event')):
        m['source_bindings'][name]=parent.native.oracle.sha(name)
    return parent.seal(m)


def check(record,m,role):
    parent.require(m==manifest(),'continuation successor source drift')
    with patch.object(parent,'compare_step',compare_step):parent.check_record(record,m,'combined',role)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=('prepare','run','check'))
    parser.add_argument('--role',choices=parent.ROLES)
    args=parser.parse_args()
    with parent.native.oracle.exact_backend(parent.native.oracle.ExactBackend.FLINT),parent.native.oracle.numerical_policy(parent.native.oracle.NumericalPolicy.CERTIFIED_ARB_256):
        if args.action=='prepare':parent.native.oracle.old.write_new(INPUTS,manifest());return
        parent.require(args.role in parent.ROLES,'select role')
        m=parent.native.oracle.old.read(INPUTS);parent.require(m==manifest(),'source drift')
        if args.action=='check':check(read(args.role),m,args.role);return
        p=parent.ROOT/path(args.role);parent.require(not p.exists(),'refuse overwrite')
        def expired(*_):raise TimeoutError('unchanged 600-second cap; no fallback')
        signal.signal(signal.SIGALRM,expired);signal.alarm(m['step_cap_seconds']);started=time.monotonic()
        try:
            with parent.native.matrix_operation(),patch.object(parent,'compare_step',compare_step):
                e=parent.execute_step('combined',args.role)
        finally:signal.alarm(0)
        elapsed=time.monotonic()-started;parent.require(elapsed<=m['step_cap_seconds'],'cap exceeded')
        r=parent.seal(dict(schema='p984h-cos-covariance-results-v1',manifest_digest=m['record_digest'],kind='combined',segment=args.role,
            outcome='completed',execution=e,elapsed_seconds=elapsed,user_accepted=False,aggregate_closed=False))
        check(r,m,args.role)
        packed=lzma.compress(json.dumps(r,separators=(',',':'),allow_nan=False).encode()+b'\n')
        with p.open('xb') as stream:stream.write(packed)
        parent.require(len(packed)<=2000000,'complete record retained; compressed budget exceeded')
        print(json.dumps(dict(role=args.role,seconds=elapsed,compressed_bytes=len(packed),errors=e['covariance_errors'],minimum_resource=e['observation']['minimum_resource'])),flush=True)


if __name__=='__main__':main()

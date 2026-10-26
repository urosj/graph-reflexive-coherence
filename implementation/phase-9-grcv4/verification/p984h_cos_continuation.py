"""Resumable native target histories from the successful larger C_OS event.

Each successful step is retained once. No failed-session dumps or implicit
retry; an interruption leaves already completed steps available for resumption.
"""
import argparse
from dataclasses import replace
import json
import lzma
import math
import os
import signal
import time

import flint
import p984h_cos_event_successor as event
from pygrc.models.grc_v4_realizations import CandidateCOSPass

native=event.native
ROOT,BASE,HERE=native.ROOT,native.BASE,native.HERE
SELF=HERE+'p984h_cos_continuation.py'
TEST=HERE+'test_p984h_cos_continuation.py'
PLAN=BASE+'P9-8.4h-COSContinuationPlan.md'
INPUTS=BASE+'P9-8.4h-COSContinuationInputs.json'
ROLES=('current','reset')
CAP=600
require,seal,digest=native.require,native.seal,native.digest


def path(role,step):
    require(role in ROLES and (type(step) is int and 1<=step<=10 or step=='final'),'unknown segment')
    return BASE+f'P9-8.4h-COSContinuation-{role}-{step}.json.xz'


def read(role,step):
    return json.loads(lzma.decompress((ROOT/path(role,step)).read_bytes()))


def manifest():
    upstream=native.oracle.old.read(event.INPUTS)
    require(upstream==event.manifest(),'event source drift')
    result=event.read()
    require(result==seal(result) and result['manifest_digest']==upstream['record_digest']
            and result['outcome']=='completed','event prerequisite')
    paths={SELF,TEST,PLAN,event.SELF,event.INPUTS,event.RESULTS,*upstream['source_bindings']}
    return seal(dict(schema='p984h-cos-continuation-inputs-v1',
        source_bindings={p:native.oracle.sha(p) for p in sorted(paths)},
        event_record_digest=result['record_digest'],event_id=result['execution']['event_id'],
        roles=list(ROLES),steps_per_role=10,final_reads_per_role=1,
        seconds_per_step_or_final_read=CAP,max_role_workers=2,threads_per_worker=1,
        numerical_policy='certified_arb_256_weighted_v1',backend='flint',
        comparison=dict(atol=2e-11,rtol=2e-11),detached_continuation=True,
        covariance_executed=False,user_accepted=False,aggregate_closed=False))


def initial(role):
    target=native.state(event.read()['execution']['checkpoint']['state'])
    dt=native.oracle.old.read(native.oracle.old.PREPARED)['selected_configuration']['ordinary_dt']
    return replace(target.inputs,current=getattr(target.inputs,role),dt=dt)


def expected(role):
    return next(c for c in native.oracle.read_result()['cases'] if c['role']==role)['steps'][0]


def validate(record,m,role,step,before,predecessor):
    require(record==seal(record) and record['manifest_digest']==m['record_digest']
            and record['schema']=='p984h-cos-continuation-segment-v1','segment identity')
    require(record['role']==role and record['step']==step and record['predecessor_digest']==predecessor
            and record['event_record_digest']==m['event_record_digest'],'segment linkage')
    require(record['outcome']=='completed' and 0<=record['elapsed_seconds']<=CAP
            and not record['user_accepted'] and not record['aggregate_closed']
            and not record['covariance_executed'] and record['native_events']==0
            and record['detached_continuation'] is True,'segment scope')
    if step=='final':
        require(record['native_steps']==0 and record['final_reads']==1
                and record['input_digest']==digest(before.to_payload())
                and record['split_admitted'] is True,'final read scope/input')
        require(record['predictor']['input_hodge_digest']==digest(before.geometry.one_form_hodge.matrix),
                'final fresh reference geometry')
        for stage in ('predictor','corrector'):
            for field in ('current','baseline','read_flux','causal_flat'):
                require(len(record[stage][field])==len(before.geometry.reference.graph.live_edge_ids)
                        and all(math.isfinite(x) for x in record[stage][field]),'final read vector')
        return before
    require(record['native_steps']==1 and record['final_reads']==0,'step count')
    row=record['observation']
    after=native.validate_steps([row],before)
    require(record['next_inputs']==after.to_payload(),'complete continuation poststate')
    require(row['minimum_resource']>0,'strict represented positivity')
    if step==1:
        oracle=expected(role)
        require(row['corrector']['current']==oracle['current'] and row['after_C']==oracle['after_C'],
                'certified first-step oracle mismatch')
    return after


def checked_role(m,role,through=10):
    before=initial(role);predecessor=m['event_record_digest'];rows=[]
    for step in range(1,through+1):
        if not (ROOT/path(role,step)).exists():break
        record=read(role,step)
        before=validate(record,m,role,step,before,predecessor)
        predecessor=record['record_digest'];rows.append(record)
    # Reject holes, rather than silently counting a later file as a prefix.
    require(not any((ROOT/path(role,s)).exists() for s in range(len(rows)+2,11)), 'noncontiguous continuation')
    if len(rows)==10 and (ROOT/path(role,'final')).exists():
        validate(read(role,'final'),m,role,'final',before,predecessor)
    elif (ROOT/path(role,'final')).exists():require(False,'final read without ten steps')
    return before,predecessor,rows


def final_read(before):
    old=digest(before.to_payload())
    passed=CandidateCOSPass(before)
    require(digest(before.to_payload())==old and passed.residual.admitted,'final mutation/split')
    subject=dict(graph=before.geometry.reference.graph.port_graph.to_payload(),
                 profile=before.geometry.reference.profile.to_payload())
    b,params=native.oracle.old.graph_data(subject)
    c=native.np.array(before.current.C)
    predictor=native.oracle.old.dense_point(b,c,native.np.eye(b.shape[1]),params['candidate'])
    h=native.oracle.old.generated_h(b,predictor['causal_flat'],params)
    corrector=native.oracle.old.dense_point(b,c,h,params['candidate'])
    points=dict(predictor=native.capture.point(passed.predictor),corrector=native.capture.point(passed.corrector))
    errors={}
    for stage,ref in (('predictor',predictor),('corrector',corrector)):
        for field in ('current','baseline','read_flux','causal_flat'):
            a,e=native.np.asarray(points[stage][field]),native.np.asarray(ref[field])
            require(native.np.allclose(a,e,atol=2e-11,rtol=2e-11),'final dense mismatch')
            errors[stage+'/'+field]=float(native.np.max(abs(a-e)))
    return dict(points,input_digest=old,split_admitted=True,
        split_certificate=passed.residual.execution_certificate.to_dict(),
        split_values_digest=digest(passed.residual.exact_values),dense_errors=errors)


def execute_one(m,role,step,before,predecessor):
    require(not (ROOT/path(role,step)).exists(),'refuse overwrite')
    def expired(*_):raise TimeoutError('explicit 600-second segment cap; no fallback')
    started=time.monotonic();signal.signal(signal.SIGALRM,expired);signal.alarm(CAP)
    print(json.dumps(dict(role=role,step=step,stage='started')),flush=True)
    try:
        with native.matrix_operation():
            if step=='final':fields=final_read(before);after=before
            else:
                row,after=native.observe_step(before,expected(role) if step==1 else None)
                require(row['minimum_resource']>0,'strict represented positivity')
                fields=dict(observation=row,next_inputs=after.to_payload())
        elapsed=time.monotonic()-started
        require(elapsed<=CAP,'segment exceeded cap')
    except Exception as exc:
        print(json.dumps(dict(role=role,step=step,outcome='failed',type=type(exc).__name__,
                             message=str(exc),seconds=time.monotonic()-started)),flush=True)
        raise
    finally:signal.alarm(0)
    record=seal(dict(fields,schema='p984h-cos-continuation-segment-v1',
        manifest_digest=m['record_digest'],event_record_digest=m['event_record_digest'],
        predecessor_digest=predecessor,role=role,step=step,outcome='completed',
        runtime=dict(python_flint=flint.__version__,threads=1),elapsed_seconds=elapsed,
        native_steps=int(step!='final'),native_events=0,final_reads=int(step=='final'),
        detached_continuation=True,covariance_executed=False,user_accepted=False,aggregate_closed=False))
    require(m==manifest(),'source changed during segment')
    raw=json.dumps(record,separators=(',',':'),allow_nan=False).encode()+b'\n'
    packed=lzma.compress(raw)
    with (ROOT/path(role,step)).open('xb') as stream:stream.write(packed)
    require(len(packed)<=2000000,'complete segment retained; inspect exceeded compressed budget before continuing')
    print(json.dumps(dict(role=role,step=step,outcome='completed',seconds=elapsed,
        minimum_resource=min(after.current.C),record_digest=record['record_digest'])),flush=True)
    return after,record['record_digest']


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=('prepare','run','check'))
    parser.add_argument('--role',choices=ROLES)
    parser.add_argument('--through',type=int,choices=(1,10),default=1)
    args=parser.parse_args()
    with native.oracle.exact_backend(native.oracle.ExactBackend.FLINT), native.oracle.numerical_policy(native.oracle.NumericalPolicy.CERTIFIED_ARB_256):
        if args.action=='prepare':
            event.check()  # Full retained checkpoint check once, no numerical event replay.
            native.oracle.old.write_new(INPUTS,manifest());return
        m=native.oracle.old.read(INPUTS);require(m==manifest(),'continuation source drift')
        if args.action=='check':
            summary={}
            for role in ROLES:
                _,_,rows=checked_role(m,role)
                summary[role]=dict(native_steps=len(rows),final_reads=int((ROOT/path(role,'final')).exists()))
            print(json.dumps(dict(roles=summary,native_numerics_rerun=False)));return
        require(args.role in ROLES,'role required')
        require(all(os.environ.get(k)=='1' for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS')),'single thread')
        if args.through==10:
            for role in ROLES:
                require((ROOT/path(role,1)).exists(),'both oracle-matched first steps required')
                before=initial(role);validate(read(role,1),m,role,1,before,m['event_record_digest'])
        before,predecessor,rows=checked_role(m,args.role)
        require(len(rows)<=args.through,'requested scope already exceeded')
        for step in range(len(rows)+1,args.through+1):
            before,predecessor=execute_one(m,args.role,step,before,predecessor)
        if args.through==10 and not (ROOT/path(args.role,'final')).exists():
            execute_one(m,args.role,'final',before,predecessor)


if __name__=='__main__':main()

"""Four bounded native A_PC prerequisite steps; no live owner or event."""
import argparse
from dataclasses import replace
import hashlib
import json
import lzma
import multiprocessing as mp
import os
import signal
import time
from unittest.mock import patch
import p984g_apc_hardening as h
import p984g_aci_native as harness
import p984g_aci_native_check as charge_helpers

p=h.p
ROOT,BASE,HERE=h.ROOT,h.BASE,h.HERE
SELF=HERE+'p984g_apc_native.py';TEST=HERE+'test_p984g_apc_native.py'
PLAN=BASE+'P9-8.4g-APCNativePlan.md';NOTE=BASE+'P9-8.4g-APCNative.md'
DIRECTORY=BASE+'P9-8.4g-APCNative/';RESULTS=BASE+'P9-8.4g-APCNativeResults.json'
CASES=p.prior.rows.shared.CASES
q,require,digest,seal=p.q,p.require,p.digest,p.prior.seal


def bindings():
    names=[SELF,TEST,PLAN,h.SELF,h.RESULTS,p.SELF,p.feasible.SELF,
        HERE+'prepare_p983_all_realizations.py',harness.SELF,charge_helpers.SELF,
        'specs/grc-v4-numerical-policy.md']
    names += [str(x.relative_to(ROOT)) for x in (ROOT/'src/pygrc/models').glob('*grc*v4*.py')]
    return {s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest() for s in sorted(set(names))}


def case_path(graph,role):
    require((graph,role) in CASES,'case roster');return DIRECTORY+graph+'-'+role+'.json.xz'


def inputs_for(subject,role):
    from pygrc.models.grc_v4_pc import carrier_geometry
    d=p.feasible.mechanical;old=p.prior.read(p.prior.PREPARED)
    graph=d.GRC9V4PortGraph.from_envelope(subject['graph'])
    profile=d.GRCV4Profile.from_canonical_bytes(d.canonical_json_bytes(subject['profile']))
    spec=d.native.GRC9V4Specialization(d.FrozenJSONMap(old['specialization']['resolved']),d.FrozenJSONMap(old['specialization']['identity_payload']))
    roles={r:d.authority(subject['roles'][r],len(graph.edges)) for r in ('current','reset')}
    state=d.make_state(graph,profile,spec,roles,'A_PC')
    before=replace(state.inputs,current=roles[role],geometry=carrier_geometry(state.inputs,roles[role]),
        dt=old['selected_configuration']['ordinary_dt'],stage='pre_read')
    return before,d.GRC9V4CandidateADifferentialReference(graph)


def point_record(read):
    point=read.point;n=len(point.current.values);authority=point.inputs.current
    out={k:list(v) for k,v in dict(potential=point.potential.values,baseline=point.baseline.values,
        drive=point.W_hat_A,current=point.current.values,flux=point.read.flux.values,flat=point.read.causal_flat.values).items()}
    out.update(C=list(authority.C),W_A=list(authority.W_A),Z=p.sparse([list(authority.Z_4[i*n:(i+1)*n]) for i in range(n)]),
        H=p.sparse([list(row) for row in point.inputs.geometry.one_form_hodge.matrix]),
        source=p.sparse([list(row) for row in read.structural_source.increment]),certificate=read.certificate.bounds.to_dict())
    out['point_digest']=digest(dict(C=out['C'],W_A=out['W_A'],Z=out['Z'],H=out['H'],current=out['current'],
        readback=out['flux'],flat=out['flat'],source=out['source']))
    return out


def compare_point(actual,expected,c,w,z,subject):
    require(set(actual)=={'potential','baseline','drive','current','flux','flat','C','W_A','Z','H','source','certificate','point_digest'},'point fields')
    for key in ('potential','baseline','drive','current','flux','flat','H','source','point_digest'):
        require(actual[key]==expected[key],'native/oracle '+key+' mismatch')
    require(actual['C']==c and actual['W_A']==w and actual['Z']==z,'point authoritative state')
    h.bind_final(subject,'current',dict(C=c,W_A=w,Z=z,final=actual))
    cert=actual['certificate'];params=subject['profile']['params_resolved'];pc=params['realization']
    radius=q(params['geometry']['kappa_H'])*q(pc['radius']);gain=abs(q(params['candidate']['zeta_A'])*q(params['candidate']['chi_A']))
    require(q(cert['hodge_lower'])==1-radius and q(cert['hodge_upper'])==1+radius,'whole-chart Hodge bounds')
    require(q(cert['current_inverse_upper'])==1/(1-gain) and q(cert['current_conditioning_upper'])==(1+gain)/(1-gain),'whole-chart current bounds')
    require(0<=q(cert['source_norm_upper'])<=q(cert['carrier_radius'])==q(pc['radius']),'whole-chart source envelope')


def initial_z(subject,role):
    n=len(subject['graph']['edges']);diag=p.prior.carrier(subject,role,n)
    return p.sparse([[float(diag[i]) if i==j else 0. for j in range(n)] for i in range(n)])


def compare_result(r,graph,role,oracle):
    subject=oracle['subjects'][graph];expected={(c['graph'],c['role']):c['result'] for c in oracle['cases']};e=expected[(graph,role)]
    require(set(r['reads'])=={'reset','current','final'},'read roster')
    for key,which in (('reset','reset'),('current',role)):
        s=subject['roles'][which];compare_point(r['reads'][key],expected[(graph,which)]['initial'],s['C'],s['W_A'],initial_z(subject,which),subject)
    compare_point(r['reads']['final'],e['final'],e['C'],e['W_A'],e['Z'],subject)
    require(r['after_C']==e['C'] and r['after_W_A']==e['W_A'] and r['after_Z']==e['Z'],'two-writer final authority')
    require(r['writer_target']==e['writer_target'],'post-C selected-current W drive')
    require(r['exact_stored_charge_drift']==e['exact_stored_charge_drift'],'exact charge drift')
    charge=charge_helpers.pairwise(r['after_C']);target=charge_helpers.pairwise(subject['roles'][role]['C']);cp=subject['profile']['params_resolved']['charge']
    require(r['Q_target']==target and r['charge']==dict(target_charge=target,admitted_charge=charge,residual=float(q(charge)-q(target))),'charge receipt')
    require(abs(q(charge)-q(target))<=q(cp['absolute_tolerance'])+q(cp['relative_tolerance'])*max(abs(q(target)),q(1)),'charge admission')
    dt=p.prior.read(p.prior.PREPARED)['selected_configuration']['ordinary_dt']
    require(r['dt']==dt and r['after_step_index']==r['before_step_index']+1 and r['after_time']==r['before_time']+dt,'clock/index')
    require(r['reset_unchanged'] and r['input_unchanged'] and r['continuity_evaluations']==r['history_writes']==r['carrier_writes']==1,'step authority/counts')
    return dict(minimum_resource=min(r['after_C']),charge=r['charge'],exact_stored_charge_drift=r['exact_stored_charge_drift'],
        full_point_parity=True,reset_preserved=True,native_reads=3,native_steps=1)


def execute(graph,role,progress):
    from pygrc.models.grc_v4_numerics import exact_backend,ExactBackend,numerical_policy,NumericalPolicy,matrix_operation
    from pygrc.models.grc_v4_pc import ProvisionalCandidatePCStep
    oracle=h.check_retained();subject=oracle['subjects'][graph]
    with exact_backend(ExactBackend.FLINT),numerical_policy(NumericalPolicy.CERTIFIED_ARB_256),matrix_operation():
        before,backend=inputs_for(subject,role);original=digest(before.to_payload());progress('materialized')
        step=ProvisionalCandidatePCStep(before,backend);after=step.next_inputs;progress('native_step_completed')
        result=dict(reads={name:point_record(read) for name,read in (('reset',step.reset_read),('current',step.read),('final',step.restart))},
            after_C=list(after.current.C),after_W_A=list(after.current.W_A),after_Z=point_record(step.restart)['Z'],
            writer_target=list(step.writer.W_drv_A),dt=before.dt,Q_target=before.Q_target,charge=step.resource.charge.receipt_values(),
            exact_stored_charge_drift=str(sum(map(q,after.current.C),q(0))-sum(map(q,before.current.C),q(0))),
            input_unchanged=original==digest(before.to_payload()),reset_unchanged=after.reset==before.reset,
            continuity_evaluations=step.resource.continuity_evaluations,history_writes=int(step.writer is not None),
            carrier_writes=step.carrier_writes,before_step_index=before.step_index,after_step_index=after.step_index,
            before_time=before.time,after_time=after.time)
        compare_result(result,graph,role,oracle);progress('full_point_writer_charge_comparison_completed');return result


def worker(pipe,graph,role):
    # Reuse only timeout stack/error transport; production PC methods are untouched.
    with patch.object(harness,'execute',execute):harness.worker(pipe,graph,role)


def run(graph,role):
    path=ROOT/case_path(graph,role);require(not path.exists(),'no overwrite')
    require(os.environ.get('OPENBLAS_NUM_THREADS')==os.environ.get('OMP_NUM_THREADS')=='1','single thread')
    bound=bindings();context=mp.get_context('spawn');receive,send=context.Pipe(False)
    process=context.Process(target=worker,args=(send,graph,role));start=time.monotonic();process.start();send.close()
    events=[];last_sample=0;result=None;error=None
    def consume():
        nonlocal result,error
        kind,value=receive.recv()
        if kind=='result':result=value
        elif kind=='error':error=value;print(json.dumps(value),flush=True)
        else:events.append(dict(kind=kind,value=value));print(json.dumps(dict(graph=graph,role=role,kind=kind,value=value)),flush=True)
    while process.is_alive() and time.monotonic()-start<600:
        if receive.poll(.2):
            try:consume()
            except EOFError:break
        if time.monotonic()-start-last_sample>=60:
            os.kill(process.pid,signal.SIGUSR1);last_sample=time.monotonic()-start
    timed_out=process.is_alive() and time.monotonic()-start>=600
    if timed_out:process.terminate()
    process.join(5)
    if process.is_alive():process.kill();process.join()
    while receive.poll():
        try:consume()
        except EOFError:break
    require(bound==bindings(),'sources changed during execution')
    record=seal(dict(schema='p984g-apc-native-v1',family='A_PC',graph=graph,role=role,source_bindings=bound,
        cap_seconds=600,seconds=time.monotonic()-start,timed_out=timed_out,exit_code=process.exitcode,
        outcome='completed' if result is not None and error is None and process.exitcode==0 else 'incomplete',
        result=result,error=error,events=events,numerical_policy='certified_arb_256_weighted_v1',exact_backend='flint',
        committed_steps=0,native_events=0,user_accepted=False,ready_for_8_4h=False))
    path.parent.mkdir(exist_ok=True);path.write_bytes(lzma.compress((json.dumps(record,separators=(',',':'))+'\n').encode(),preset=6))
    print(json.dumps({k:record[k] for k in ('outcome','seconds','timed_out','exit_code')}),flush=True)


def assess(v,oracle):
    require(v==seal(v) and v['source_bindings']==bindings(),'native record/source drift')
    require(v['schema']=='p984g-apc-native-v1' and v['family']=='A_PC' and (v['graph'],v['role']) in CASES,'native schema/case')
    require(v['committed_steps']==v['native_events']==0 and not v['user_accepted'] and not v['ready_for_8_4h'],'scope promotion')
    require(v['cap_seconds']==600 and v['seconds']>=0 and v['numerical_policy']=='certified_arb_256_weighted_v1' and v['exact_backend']=='flint','execution policy')
    if v['outcome']=='completed':
        require(not v['timed_out'] and v['exit_code']==0 and v['error'] is None and v['result'] is not None,'incomplete success')
        return dict(outcome='completed',**compare_result(v['result'],v['graph'],v['role'],oracle))
    require(v['outcome']=='incomplete' and (v['timed_out'] or v['error'] is not None or v['exit_code']!=0),'unexplained failure')
    return dict(outcome='incomplete',native_steps=0,native_reads=0,error=v['error'],timed_out=v['timed_out'])


def summary():
    oracle=h.check_retained();cases=[]
    for graph,role in CASES:
        name=case_path(graph,role);path=ROOT/name
        if not path.exists():cases.append(dict(graph=graph,role=role,outcome='not_run',native_steps=0,native_reads=0));continue
        raw=path.read_bytes();v=json.loads(lzma.decompress(raw));require((v['graph'],v['role'])==(graph,role),'filename/case mismatch')
        cases.append(dict(graph=graph,role=role,**assess(v,oracle),path=name,sha256=hashlib.sha256(raw).hexdigest(),record_digest=v['record_digest'],seconds=v['seconds']))
    return seal(dict(schema='p984g-apc-native-summary-v1',family='A_PC',cases=cases,source_bindings=bindings(),
        hardening_digest=oracle['record_digest'],native_steps=sum(c['native_steps'] for c in cases),native_reads=sum(c['native_reads'] for c in cases),
        native_prerequisites_complete=all(c['outcome']=='completed' for c in cases),scope='prepared_role_steps_not_postbeat_event_or_uniform_domain',
        native_events=0,committed_steps=0,user_accepted=False,ready_for_8_4h=False,retained_check_only=True,native_trajectories_rerun=False))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('mode',choices=('run','summarize','check'))
    parser.add_argument('--graph',choices=('source','target'));parser.add_argument('--role',choices=('current','reset'));args=parser.parse_args()
    if args.mode=='run':run(args.graph,args.role)
    else:
        value=summary()
        if args.mode=='summarize':
            require(not (ROOT/RESULTS).exists(),'no overwrite');(ROOT/RESULTS).write_text(json.dumps(value,indent=2)+'\n')
        else:require(value==json.loads((ROOT/RESULTS).read_text()),'summary drift')
        print(json.dumps({k:value[k] for k in ('native_steps','native_reads','native_prerequisites_complete')}))

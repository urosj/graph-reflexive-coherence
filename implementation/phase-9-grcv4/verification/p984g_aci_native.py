"""Bounded native A_CI steps and independent whole-joint/writer checks."""
import argparse
from copy import deepcopy
from dataclasses import replace
import hashlib
import json
import lzma
import math
import multiprocessing as mp
import os
from pathlib import Path
import signal
import time
import traceback
import p984g_aci_staged as oracle

f=oracle.feasible
ROOT,BASE,HERE=oracle.ROOT,oracle.BASE,oracle.HERE
SELF=HERE+'p984g_aci_native.py'
PLAN=BASE+'P9-8.4g-ACINativePlan.md'
DIRECTORY=BASE+'P9-8.4g-ACINative/'
CASES=oracle.prior.shared.CASES
q,a,require,seal=oracle.q,oracle.a,oracle.require,oracle.prior.seal
digest=oracle.prior.shared.digest


def bindings():
    names=[SELF,PLAN,oracle.SELF,oracle.RESULTS,f.SELF,f.RESULTS,f.prior.SELF,
           f.prior.PREPARED,HERE+'prepare_p983_all_realizations.py',
           'specs/grc-v4-numerical-policy.md']
    names += [str(p.relative_to(ROOT)) for p in (ROOT/'src/pygrc/models').glob('*grc*v4*.py')]
    return {p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sorted(set(names))}


def case_path(graph,role):
    require((graph,role) in CASES,'unknown case')
    return DIRECTORY+graph+'-'+role+'.json.xz'


def inputs_for(graph,role):
    p=f.prepared;retained=f.check_retained();old=f.prior.read(f.prior.PREPARED)
    subject=retained[graph]
    port=p.GRC9V4PortGraph.from_envelope(subject['graph'])
    profile=p.GRCV4Profile.from_canonical_bytes(p.canonical_json_bytes(subject['profile']))
    spec=p.native.GRC9V4Specialization(p.FrozenJSONMap(old['specialization']['resolved']),
                                     p.FrozenJSONMap(old['specialization']['identity_payload']))
    roles={r:p.authority(subject['roles'][r],len(port.edges)) for r in ('current','reset')}
    state=p.make_state(port,profile,spec,roles,'A_CI')
    before=replace(state.inputs,current=getattr(state.inputs,role),stage='pre_read',
                   dt=old['selected_configuration']['ordinary_dt'])
    return before,subject,p.GRC9V4CandidateADifferentialReference(port)


def compare_root(root,subject,role,expected):
    point=root.selected.point;inputs=point.inputs
    actual={k:list(v) for k,v in dict(potential=point.potential.values,
        baseline=point.baseline.values,drive=point.W_hat_A,current=point.current.values,
        flux=point.read.flux.values,flat=point.read.causal_flat.values).items()}
    require(root.evaluations==2 and expected['two_consecutive_independent_residual_passes'],
            'native fixed-row stopping differs from oracle')
    require(all(actual[k]==expected['confirming'][k] for k in actual),'native primitive/oracle mismatch')
    h=[list(row) for row in inputs.geometry.one_form_hodge.matrix]
    joint=digest(dict(graph=subject['graph'],profile=subject['profile'],C=list(inputs.current.C),
                      W_A=list(inputs.current.W_A),H=h,J=actual['current']))
    require(joint==expected['selected_joint_point_digest'],'native whole selected point mismatch')
    require(inputs.current.C==tuple(subject['roles'][role]['C']) and
            inputs.current.W_A==tuple(subject['roles'][role]['W_A']),'native root role/state mismatch')
    params=subject['profile']['params_resolved'];cert=root.certificate.bounds.to_dict()
    require(q(cert['radius'])==q(float.fromhex(params['realization']['contraction_domain_id'].split(':',1)[1]))
        and 0<=q(cert['displacement_upper'])<=q(cert['radius'])
        and 0<=q(cert['contraction_upper'])<1 and cert['reference_connected']
        and cert['regular_reduced_root'] and cert['norm']=='joint_current_geometry_l2_v1'
        and cert['scope']=='analytic_local_reference_ball','native certificate domain')
    require(q(str(root.selected.residual_squared))<=q(params['realization']['tolerance'])**2,'native residual')
    return dict(evaluations=root.evaluations,identity=root.identity,certificate=cert,
        native_residual_squared=str(root.selected.residual_squared),selected_joint_point_digest=joint,
        represented_geometry_digest=digest(h),actual=actual,
        independent_stages=expected['stages'],state_digest=digest(subject['roles'][role]),
        native_stopping_matches_oracle=True)


def writer_oracle(subject,role,after_c,current,dt):
    changed=deepcopy(subject);changed['roles'][role]['C']=list(after_c)
    md=oracle.model(changed,role);p=md['p'];desc=[[q(oracle.rn(x)) for x in row] for row in md['desc']]
    drives=[]
    for i,(u,v) in enumerate(md['ends']):
        exponent=-(q(p['alpha'])*(q(after_c[u])+q(after_c[v]))+
            q(p['beta'])*sum(((x-y)**2 for x,y in zip(desc[u],desc[v])),q(0))+
            q(p['gamma'])*q(current[i])**2)/2
        drives.append(max(p['W_floor'],math.exp(oracle.rn(exponent))))
    with oracle.ctx.workprec(oracle.BITS):
        enclosed=f.log_writer(list(map(a,md['w'])),list(map(a,drives)),dt,p['tau_A'])
        weights=[oracle.unique(x) for x in enclosed]
    return dict(descriptors=[[float(x) for x in row] for row in desc],drive=drives,W_A=weights)


def execute(graph,role,progress):
    from pygrc.models.grc_v4_numerics import exact_backend,ExactBackend,numerical_policy,NumericalPolicy,matrix_operation
    from pygrc.models.grc_v4_ci import ProvisionalCandidateCIStep
    retained=oracle.check_retained()
    expected={(c['graph'],c['role']):c['result'] for c in retained['cases']}
    with exact_backend(ExactBackend.FLINT),numerical_policy(NumericalPolicy.CERTIFIED_ARB_256),matrix_operation():
        before,subject,backend=inputs_for(graph,role);before_digest=digest(before.to_payload())
        progress('materialized')
        step=ProvisionalCandidateCIStep(before,backend);after=step.next_inputs
        progress('native_step_completed')
        require(digest(before.to_payload())==before_digest,'input mutation')
        require(after.reset==before.reset and after.current.Z_4 is None and step.carrier_writes==0,'authority mutation')
        require(after.geometry==before.geometry and step.resource.continuity_evaluations==1,'geometry/continuity count')
        require(after.time==before.time+before.dt and after.step_index==before.step_index+1,'clock/index')
        roots={name:compare_root(root,subject,r,expected[(graph,r)]) for name,root,r in
               (('reset',step.reset_root,'reset'),('current',step.root,role))}
        final=deepcopy(subject);final['roles']['current']=dict(C=list(after.current.C),W_A=list(after.current.W_A),Z_4=None)
        with oracle.ctx.workprec(oracle.BITS):final_oracle=oracle.analyze(final,'current',before.dt)
        roots['final']=compare_root(step.restart,final,'current',final_oracle)
        bv=oracle.model(subject,role)['bv']
        literal=[float(c)-before.dt*sum(float(x)*j for x,j in zip(row,step.root.current.values))
                 for c,row in zip(before.current.C,bv)]
        require(literal==list(after.current.C) and min(literal)>=0,'literal continuity')
        writer=writer_oracle(subject,role,after.current.C,step.root.current.values,before.dt)
        require(writer['W_A']==list(after.current.W_A) and writer['drive']==list(step.writer.W_drv_A)
            and writer['descriptors']==[list(row) for row in step.writer.descriptors],'writer mismatch')
        wrong=writer_oracle(subject,role,before.current.C,step.root.current.values,before.dt)
        baseline=writer_oracle(subject,role,after.current.C,step.root.selected.point.baseline.values,before.dt)
        progress('independent_joint_and_writer_checks_completed')
        result=dict(before_digest=before_digest,after_digest=digest(after.to_payload()),roots=roots,
            initial_C=list(before.current.C),initial_W_A=list(before.current.W_A),reset_C=list(before.reset.C),
            reset_W_A=list(before.reset.W_A),after_C=list(after.current.C),after_W_A=list(after.current.W_A),
            dt=before.dt,Q_target=before.Q_target,charge=step.resource.charge.receipt_values(),
            exact_resource_sum_delta=str(sum((q(x) for x in after.current.C),q(0))-sum((q(x) for x in before.current.C),q(0))),
            final_oracle=final_oracle,writer=writer,
            writer_wrong_prestate_drive_changed=sum(x!=y for x,y in zip(wrong['drive'],writer['drive'])),
            writer_wrong_baseline_drive_changed=sum(x!=y for x,y in zip(baseline['drive'],writer['drive'])),
            reset_unchanged=True,final_C_and_W_rebuilt=True,continuity_evaluations=1,carrier_writes=0,
            history_writes=1,before_step_index=before.step_index,after_step_index=after.step_index,
            before_time=before.time,after_time=after.time)
        if graph=='source':
            old=f.prior.read(f.prior.PREPARED);old['source']=subject
            with oracle.ctx.workprec(oracle.BITS):result['poststep_trigger']=f.trigger(old,list(map(a,after.current.C)),list(map(a,after.current.W_A)))
            require(result['poststep_trigger']['small_gradient'] and result['poststep_trigger']['strict_hessian_condition'],'actual poststep trigger')
        return result


def worker(pipe,graph,role):
    started=time.monotonic()
    def sample(_signum,frame):
        def relative(name):
            try:return str(Path(name).relative_to(ROOT))
            except ValueError:return 'external-runtime/'+Path(name).name
        pipe.send(('stack',dict(seconds=time.monotonic()-started,frames=[dict(file=relative(x.filename),line=x.lineno,function=x.name) for x in traceback.extract_stack(frame)[-6:]])))
    signal.signal(signal.SIGUSR1,sample)
    try:pipe.send(('result',execute(graph,role,lambda stage:pipe.send(('progress',dict(stage=stage,seconds=time.monotonic()-started))))))
    except Exception as exc:pipe.send(('error',dict(type=type(exc).__name__,message=str(exc),stage=getattr(exc,'stage',None),disposition=getattr(exc,'disposition',None))))
    finally:pipe.close()


def run(graph,role):
    path=ROOT/case_path(graph,role);require(not path.exists(),'no overwrite')
    require(os.environ.get('OPENBLAS_NUM_THREADS')=='1' and os.environ.get('OMP_NUM_THREADS')=='1','single thread')
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
    require(bound==bindings(),'source changed during run')
    record=seal(dict(schema='p984g-aci-native-prerequisite-v1',graph=graph,role=role,source_bindings=bound,
        cap_seconds=600,seconds=time.monotonic()-start,timed_out=timed_out,exit_code=process.exitcode,
        outcome='completed' if result is not None and error is None and process.exitcode==0 else 'incomplete',
        result=result,error=error,events=events,numerical_policy='certified_arb_256_weighted_v1',exact_backend='flint',
        committed_steps=0,native_events=0,user_accepted=False,ready_for_8_4h=False))
    path.parent.mkdir(exist_ok=True);path.write_bytes(lzma.compress((json.dumps(record,indent=2)+'\n').encode(),preset=6))
    print(json.dumps({k:record[k] for k in ('outcome','seconds','timed_out','exit_code')}))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=['run']);p.add_argument('--graph',choices=['source','target'],required=True)
    p.add_argument('--role',choices=['current','reset'],required=True);args=p.parse_args();run(args.graph,args.role)

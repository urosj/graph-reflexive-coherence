"""Native C_CI numerical admission with independent joint-root checks."""
import argparse
from copy import deepcopy
from dataclasses import replace
import hashlib
import json
import lzma
import multiprocessing as mp
import os
import signal
import time
import traceback

import p984g_cci_native as setup
import p984g_cci_feasibility as f
import p984g_cos_native as cos

ROOT,BASE,HERE=setup.ROOT,setup.BASE,setup.HERE
SELF=HERE+'p984g_cci_closure.py'
PLAN=BASE+'P9-8.4g-CCIClosurePlan.md'
RESULTS=BASE+'P9-8.4g-CCIClosureResults.json'
REVIEW=BASE+'P9-8.4g-CCIClosure.md'
DIRECTORY=BASE+'P9-8.4g-CCIClosure/'
CASES=f.staged.CASES
q,require,read,seal=f.q,f.require,f.read,f.seal


def bindings():
    names=[SELF,PLAN,setup.SELF,f.SELF,f.RESULTS,f.prior.SELF,f.staged.SELF,f.iv.SELF,
        f.prior.shared.SELF,cos.SELF,HERE+'prepare_p983_all_realizations.py',
        'specs/grc-v4-numerical-policy.md']
    names += [str(p.relative_to(ROOT)) for p in (ROOT/'src/pygrc/models').glob('*grc*v4*.py')]
    return {p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sorted(set(names))}


def case_path(graph,role):
    require((graph,role) in CASES,'unknown case')
    return DIRECTORY+graph+'-'+role+'.json.xz'


def independent_root(root,subject):
    point=root.selected.point;inputs=point.inputs
    require(root.evaluations==1 and inputs.geometry==inputs.geometry.reference.geometry(),
            'unexpected root iteration/geometry: investigate, never substitute')
    updated=deepcopy(subject);updated['roles']['current']=dict(C=list(inputs.current.C),W_A=None,Z_4=None)
    bv,params=f.prior.shared.graph_data(updated);p=params['candidate']
    with f.staged.ctx.workprec(f.iv.BITS):
        b=f.iv.matrix(bv);h=f.iv.eye(b.ncols());j=f.iv.matrix([[x] for x in root.current.values])
        c=f.iv.matrix([[x] for x in inputs.current.C])
        mean=sum((q(x) for x in inputs.current.C),q(0))/b.nrows()
        t=(f.iv.a(p['kappa_M_C'])*(f.iv.a(mean)/f.iv.a(p['C_ref'])).tanh()).exp()
        j0=-f.iv.a(p['eta_C'])*f.iv.a(p['kappa_Phi_C'])*t*b.transpose()*b*b.transpose()*c
        response=f.staged.response(b,h,j,p,t);flat=f.iv.a(p['chi_C'])*response
        fj=j-j0-f.iv.a(q(p['zeta_C'])*q(p['chi_C']))*response
        fh=h-f.iv.generated(b,flat,params,staged=False)
        ej,eh=f.iv.hi(f.staged.norm2(fj)),f.iv.hi(f.staged.norm2(fh))
        bounds=f.prior.certificate(updated,'current')['bounds']
        bridge=f.staged.bridge(bounds,p['chi_C'],q(p['zeta_C'])*q(p['chi_C']),
            q(params['geometry']['kappa_H'])*q(p['zeta_C']),ej,eh)
        require(ej*ej+eh*eh<=q(params['realization']['tolerance'])**2,'independent joint residual failed')
    return dict(evaluations=root.evaluations,identity=root.identity,
        native_residual_squared=str(root.selected.residual_squared),
        independent_residual_squared_upper=str(ej*ej+eh*eh),
        independent_current_residual_upper=str(ej),independent_geometry_residual_upper=str(eh),
        joint_root_error=bridge,certificate=root.certificate.bounds.to_dict(),
        point=cos.point(point),resource_digest=f.prior.shared.digest(list(inputs.current.C)),
        consumed_reference_geometry=True)


def execute(graph,role,progress):
    from pygrc.models.grc_v4_numerics import exact_backend,ExactBackend,numerical_policy,NumericalPolicy,matrix_operation
    from pygrc.models.grc_v4_ci import ProvisionalCandidateCIStep
    with exact_backend(ExactBackend.FLINT),numerical_policy(NumericalPolicy.CERTIFIED_ARB_256),matrix_operation():
        before,subject,declaration=setup.inputs_for(graph,role)
        before_digest=f.prior.shared.digest(before.to_payload())
        progress('materialized')
        step=ProvisionalCandidateCIStep(before);after=step.next_inputs
        progress('native_step_completed')
        require(f.prior.shared.digest(before.to_payload())==before_digest,'input mutation')
        require(after.reset==before.reset and after.current.W_A is None and after.current.Z_4 is None,'authority mutation')
        require(after.geometry==before.geometry and step.carrier_writes==0 and step.writer is None,'unexpected history/geometry write')
        require(step.resource.continuity_evaluations==1,'continuity count')
        require(after.time==before.time+before.dt and after.step_index==before.step_index+1,'clock/index')
        require(step.restart.inputs.current==after.current and step.reset_root.inputs.current==before.reset,'root role mismatch')
        roots={name:independent_root(root,subject) for name,root in
               (('reset',step.reset_root),('current',step.root),('final',step.restart))}
        progress('independent_joint_checks_completed')
        result=dict(declaration=declaration,before_digest=before_digest,after_digest=f.prior.shared.digest(after.to_payload()),
            roots=roots,initial_C=list(before.current.C),reset_C=list(before.reset.C),after_C=list(after.current.C),
            dt=before.dt,Q_target=before.Q_target,charge=step.resource.charge.receipt_values(),
            exact_resource_sum_delta=str(sum((q(x) for x in after.current.C),q(0))-sum((q(x) for x in before.current.C),q(0))),
            reset_unchanged=True,final_C_rebuilt=True,continuity_evaluations=1,carrier_writes=0,
            continuation_reference_geometry=True,before_step_index=before.step_index,after_step_index=after.step_index,
            before_time=before.time,after_time=after.time)
        if graph=='source':
            old,_,_,_=f.companion(f.DEFICIT)
            with f.staged.ctx.workprec(f.iv.BITS):
                result['poststep_trigger']=f.trigger_envelope(old,[f.iv.a(x) for x in after.current.C])
            require(result['poststep_trigger']['small_gradient'] and result['poststep_trigger']['strict_hessian_condition'],
                    'actual source poststep trigger failed')
        return result


def worker(pipe,graph,role):
    start=time.monotonic()
    def sample(signum,frame):
        pipe.send(('stack',dict(seconds=time.monotonic()-start,
            frames=[dict(file=x.filename.split('/graph-reflexive-coherence/')[-1],line=x.lineno,function=x.name)
                    for x in traceback.extract_stack(frame)[-6:]])))
    signal.signal(signal.SIGUSR1,sample)
    try:pipe.send(('result',execute(graph,role,lambda stage:pipe.send(('progress',dict(stage=stage,seconds=time.monotonic()-start))))))
    except Exception as exc:
        pipe.send(('error',dict(type=type(exc).__name__,message=str(exc),stage=getattr(exc,'stage',None),
            disposition=getattr(exc,'disposition',None),code=getattr(exc,'code',None))))
    finally:pipe.close()


def run(graph,role):
    path=ROOT/case_path(graph,role);require(not path.exists(),'no overwrite')
    require(os.environ.get('OPENBLAS_NUM_THREADS')=='1' and os.environ.get('OMP_NUM_THREADS')=='1','single thread')
    bound=bindings();context=mp.get_context('spawn');receive,send=context.Pipe(False)
    process=context.Process(target=worker,args=(send,graph,role));start=time.monotonic();process.start();send.close()
    events=[];last_sample=0;result=None;error=None
    while process.is_alive() and time.monotonic()-start<600:
        if receive.poll(.2):
            try:kind,value=receive.recv()
            except EOFError:break
            if kind=='result':result=value
            elif kind=='error':error=value;print(json.dumps(value),flush=True)
            else:
                events.append(dict(kind=kind,value=value))
                print(json.dumps(dict(graph=graph,role=role,kind=kind,value=value)),flush=True)
        if time.monotonic()-start-last_sample>=60:
            os.kill(process.pid,signal.SIGUSR1);last_sample=time.monotonic()-start
    timed_out=process.is_alive() and time.monotonic()-start>=600
    if timed_out:process.terminate()
    process.join(5)
    if process.is_alive():process.kill();process.join()
    while receive.poll():
        try:kind,value=receive.recv()
        except EOFError:break
        if kind=='result':result=value
        elif kind=='error':error=value
        else:events.append(dict(kind=kind,value=value))
    require(bound==bindings(),'source changed during run')
    record=seal(dict(schema='p984g-cci-native-admission-v1',graph=graph,role=role,source_bindings=bound,
        cap_seconds=600,seconds=time.monotonic()-start,timed_out=timed_out,exit_code=process.exitcode,
        outcome='completed' if result is not None and error is None and process.exitcode==0 else 'incomplete',
        result=result,error=error,events=events,numerical_policy='certified_arb_256_weighted_v1',exact_backend='flint',
        committed_steps=0,native_events=0,user_accepted=False,ready_for_8_4h=False))
    path.parent.mkdir(exist_ok=True)
    path.write_bytes(lzma.compress((json.dumps(record,indent=2)+'\n').encode(),preset=6))
    print(json.dumps({k:record[k] for k in ('outcome','seconds','timed_out','exit_code')}))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=['run']);p.add_argument('--graph',choices=['source','target'],required=True)
    p.add_argument('--role',choices=['current','reset'],required=True);args=p.parse_args();run(args.graph,args.role)

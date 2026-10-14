"""Independent represented CI joint-root investigation; never native execution."""
import argparse
import hashlib
import json
import math
import multiprocessing as mp
import os
import platform
import time
from flint import arb, ctx, fmpq
import p984g_cci_investigation as prior
import p984g_cos_bounds as iv

ROOT,BASE,HERE=prior.ROOT,prior.BASE,prior.HERE
SELF=HERE+'p984g_cci_staged.py'
TEST=HERE+'test_p984g_cci_staged.py'
PLAN=BASE+'P9-8.4g-CCIStagedPlan.md'
REVIEW=BASE+'P9-8.4g-CCIStagedReview.md'
RESULTS=BASE+'P9-8.4g-CCIStagedResults.json'
DIRECTORY=BASE+'P9-8.4g-CCIStaged/'
require,read,seal,q=prior.require,prior.read,prior.seal,iv.q
CASES=prior.shared.CASES


def bindings():
    names=[SELF,TEST,PLAN,prior.SELF,prior.RESULTS,prior.PREPARED,iv.SELF,
           prior.shared.SELF,'src/pygrc/models/grc_v4_ci.py',
           'src/pygrc/models/grc_v4_candidate_c.py','src/pygrc/models/grc_v4_transport.py']
    return {n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in names}


def norm2(x):
    return sum((x[i,j]**2 for i in range(x.nrows()) for j in range(x.ncols())),arb(0)).sqrt()


def unique(x):
    require(all(iv.lo(x[i,0])==iv.hi(x[i,0]) for i in range(x.nrows())),
            'represented vector rounding inconclusive')
    values=[float(iv.lo(x[i,0])) for i in range(x.nrows())]
    require(all(math.isfinite(v) and q(v)==iv.lo(x[i,0]) for i,v in enumerate(values)), 'not binary64')
    return values


def response(b,h,j,p,t):
    """Exact-real physical resolvent applied to any trial current, vertex solve."""
    k=iv.a(p['tau_C'])*t
    return j-k*h*b.transpose()*(iv.eye(b.nrows())+k*b*h*b.transpose()).solve(b*j)


def bridge(bounds,chi,beta,gain,current_residual,geometry_residual):
    """Full approximate-current correction, before reduced contraction use."""
    l,u=q(bounds['hodge_lower']),q(bounds['hodge_upper'])
    similarity=prior.upper(iv.a(u/l).sqrt())
    margin=1-q(beta)*similarity
    require(margin>0,'physical inverse margin')
    delta_j=q(current_residual)/margin
    delta_f=abs(q(chi))*similarity/l*delta_j
    source_defect=abs(q(gain))*(2*q(bounds['flat_upper'])+delta_f)*delta_f
    contraction=q(bounds['contraction_upper'])
    require(0<=contraction<1,'strict contraction required')
    h_error=(q(geometry_residual)+source_defect)/(1-contraction)
    j_error=delta_j+q(bounds['current_lipschitz_upper'])*h_error
    return dict(current_defect_upper=str(delta_j),flat_defect_upper=str(delta_f),
        source_defect_upper=str(source_defect),geometry_error_upper=str(h_error),
        current_error_upper=str(j_error),
        joint_error_upper=str(prior.upper(iv.a(h_error*h_error+j_error*j_error).sqrt())))


def analyze(subject,role,dt,progress=lambda stage:None):
    bv,params=prior.shared.graph_data(subject);p=params['candidate']
    bounds=prior.certificate(subject,role)['bounds']
    b=iv.matrix(bv);m=b.ncols();h0=iv.eye(m)
    cs=subject['roles'][role]['C'];c=iv.matrix([[x] for x in cs])
    mean=sum((q(x) for x in cs),q(0))/len(cs)
    t=(iv.a(p['kappa_M_C'])*(iv.a(mean)/iv.a(p['C_ref'])).tanh()).exp()
    rho=math.tanh(float(mean)/p['C_ref'])
    deformation=math.exp((.5*p['kappa_M_C'])*(.5*(rho+rho)))
    beta=q(p['zeta_C'])*q(p['chi_C']);gain=q(params['geometry']['kappa_H'])*q(p['zeta_C'])
    jhat,_,fhat,domain=iv.staged_read(b,c,h0,p,deformation)
    represented,flat_values=unique(jhat),unique(fhat)
    progress('reference_staged_read')
    generated=prior.shared.generated_h(bv,flat_values,params)
    gh=iv.matrix(generated)
    # Analytic residual at the represented pair: use exact nonlinear t, trial
    # current response, and unrounded star assembly, not rounded H generation.
    j0=-iv.a(p['eta_C'])*iv.a(p['kappa_Phi_C'])*b.transpose()*b*(t*h0)*b.transpose()*c
    trial_response=response(b,h0,jhat,p,t)
    fj=jhat-j0-iv.a(beta)*trial_response
    analytic_flat=iv.a(p['chi_C'])*trial_response  # H=I
    analytic_image=iv.generated(b,analytic_flat,params,staged=False)
    fj_norm,fh_norm=norm2(fj),norm2(h0-analytic_image)
    residual=(fj_norm**2+fh_norm**2).sqrt()
    errors=bridge(bounds,p['chi_C'],beta,gain,iv.hi(fj_norm),iv.hi(fh_norm))
    # Independent exact first Picard image. q*d/(1-q) encloses the unseen
    # geometry tail from H1 to H*, not from the reference H0 to H*.
    jref,_,fref,_=iv.real_read(b,c,h0,p,t)
    h1=iv.generated(b,fref,params,staged=False)
    distance=iv.hi(norm2(h1-h0));contraction=q(bounds['contraction_upper'])
    tail_h=contraction*distance/(1-contraction)
    tail_j=q(bounds['current_lipschitz_upper'])*tail_h
    j1,_,_,_=iv.real_read(b,c,h1,p,t)
    require(iv.hi(norm2(h1-h0))<=q(bounds['radius']),'Picard image outside declared ball')
    root_j=[arb(j1[i,0].mid(),j1[i,0].rad()+iv.a(tail_j)) for i in range(m)]
    effects=[root_j[i]-jref[i,0] for i in range(m)]
    abs_bounds=[(iv.lo(abs(x)),iv.hi(abs(x))) for x in effects]
    coordinate=max(range(m),key=lambda i:abs_bounds[i][0])
    root_current_error=iv.hi(sum(((iv.a(represented[i])-root_j[i])**2 for i in range(m)),arb(0)).sqrt())
    progress('analytic_residual_and_root_enclosure')
    counter,_,_,counter_domain=iv.staged_read(b,c,gh,p,deformation)
    counter_values=unique(counter)
    progress('counterfactual_staged_read')
    max_condition=max(q(domain['condition_squared_upper']),q(counter_domain['condition_squared_upper']))
    require(max_condition<=q(params['solver']['conditioning_limit'])**2,'conditioning exceeds declared limit')
    after,values=iv.represented_continuity(b,cs,jhat,dt)
    require(values==represented,'continuity current mismatch')
    delta_diag=int(sum(generated[i,i]!=1 for i in range(m)))
    delta_off=int(sum(generated[i,j]!=0 for i in range(m) for j in range(m) if i!=j))
    squared=sum((q(generated[i,j])-int(i==j))**2 for i in range(m) for j in range(m))
    return dict(reference_current=represented,reference_flat=flat_values,
        counterfactual_current=counter_values,generated_hodge_digest=prior.shared.digest(generated.tolist()),
        generated_geometry_residual_squared=str(squared),generated_changed_diagonals=delta_diag,
        generated_nonzero_offdiagonals=delta_off,
        counterfactual_changed_current_coordinates=sum(x!=y for x,y in zip(represented,counter_values,strict=True)),
        analytic_current_residual_upper=str(iv.hi(fj_norm)),analytic_geometry_residual_upper=str(iv.hi(fh_norm)),
        analytic_joint_residual_upper=str(iv.hi(residual)),tolerance=str(q(params['realization']['tolerance'])),
        independent_analytic_residual_pass=bool(iv.hi(residual)<=q(params['realization']['tolerance'])),
        joint_root_bridge=errors,exact_picard_displacement_upper=str(distance),
        exact_root_geometry_tail_upper=str(tail_h),exact_root_current_tail_upper=str(tail_j),
        reference_to_root_current_error_upper=str(root_current_error),
        exact_feedback_current_max_lower=str(max(x[0] for x in abs_bounds)),
        exact_feedback_current_max_upper=str(max(x[1] for x in abs_bounds)),
        exact_feedback_nonzero_coordinates=sum(x[0]>0 for x in abs_bounds),
        effect_witness=dict(edge_index=coordinate,lower=str(abs_bounds[coordinate][0]),
            upper=str(abs_bounds[coordinate][1]),reference_ulp=str(q(math.ulp(represented[coordinate])))),
        reference_continuity_proposal=unique(after),condition_squared_upper=str(max_condition),
        native_deformation=deformation,scalar_host=platform.python_version(),
        native_stopping_outcome_verified=False)


def worker(pipe,graph,role):
    try:
        declaration=read(prior.PREPARED)
        with ctx.workprec(iv.BITS):
            result=analyze(declaration[graph],role,declaration['selected_configuration']['ordinary_dt'],
                           lambda stage:pipe.send(('progress',stage)))
        pipe.send(('result',result))
    except Exception as e:pipe.send(('error',dict(type=type(e).__name__,message=str(e))))
    finally:pipe.close()


def case_path(graph,role):
    require((graph,role) in CASES,'unknown case')
    return DIRECTORY+graph+'-'+role+'.json'


def run_case(graph,role):
    path=ROOT/case_path(graph,role);require(not path.exists(),'no overwrite')
    require(os.environ.get('OPENBLAS_NUM_THREADS')=='1' and os.environ.get('OMP_NUM_THREADS')=='1' and ctx.threads==1,'single-threaded research required')
    bound=bindings();start=time.monotonic();context=mp.get_context('spawn')
    receive,send=context.Pipe(False);process=context.Process(target=worker,args=(send,graph,role));process.start();send.close()
    result=None;error=None;stages=[]
    while time.monotonic()-start<600:
        if receive.poll(.2):
            try:kind,value=receive.recv()
            except EOFError:break
            if kind=='progress':
                stages.append(dict(stage=value,seconds=time.monotonic()-start));print(json.dumps(stages[-1]),flush=True)
            elif kind=='result':result=value;break
            else:error=value;break
        elif not process.is_alive():break
    process.join(timeout=1)
    timed_out=process.is_alive()
    if timed_out:process.terminate();process.join()
    require(bindings()==bound,'source changed during research')
    record=seal(dict(schema='p984g-cci-staged-case-v1',graph=graph,role=role,source_bindings=bound,
        precision_bits=iv.BITS,worker_cap_seconds=600,worker_seconds=time.monotonic()-start,
        outcome='completed' if result is not None and not timed_out and process.exitcode==0 else 'incomplete',
        error=error,exit_code=process.exitcode,timed_out=timed_out,stages=stages,result=result,
        native_roots=0,native_steps=0,native_events=0,ready_for_8_4h=False,user_accepted=False))
    raw=json.dumps(record,indent=2)+'\n';require(len(raw.encode())<1000000,'compress evidence before retaining')
    path.parent.mkdir(exist_ok=True);path.write_text(raw)
    print(json.dumps(dict(graph=graph,role=role,outcome=record['outcome'],seconds=record['worker_seconds'])),flush=True)


def check_case(value):
    require(value==seal(value) and value['source_bindings']==bindings(),'research digest/source drift')
    require((value['graph'],value['role']) in CASES and value['outcome']=='completed'
        and value['exit_code']==0 and not value['timed_out'] and value['error'] is None,'incomplete research')
    require(value['precision_bits']==iv.BITS and value['worker_cap_seconds']==600,'execution policy drift')
    for k in ('native_roots','native_steps','native_events','ready_for_8_4h','user_accepted'):require(value[k]==0,'scope promotion')
    r=value['result'];subject=read(prior.PREPARED)[value['graph']];role=value['role']
    bv,params=prior.shared.graph_data(subject);m=bv.shape[1]
    for field in ('reference_current','reference_flat','counterfactual_current'):
        require(len(r[field])==m and all(math.isfinite(x) for x in r[field]),'vector shape/finiteness')
    h=prior.shared.generated_h(bv,r['reference_flat'],params)
    require(prior.shared.digest(h.tolist())==r['generated_hodge_digest'],'generated geometry drift')
    squared=sum((q(h[i,j])-int(i==j))**2 for i in range(m) for j in range(m))
    require(str(squared)==r['generated_geometry_residual_squared'],'geometry residual drift')
    require(r['generated_changed_diagonals']==sum(h[i,i]!=1 for i in range(m))
        and r['generated_nonzero_offdiagonals']==sum(h[i,j]!=0 for i in range(m) for j in range(m) if i!=j),'geometry counts')
    require(r['counterfactual_changed_current_coordinates']==sum(x!=y for x,y in zip(r['reference_current'],r['counterfactual_current'],strict=True)),'counterfactual count')
    require(r['native_stopping_outcome_verified'] is False,'native stopping promotion')
    require(r['tolerance']==str(q(params['realization']['tolerance'])) and
        r['independent_analytic_residual_pass']==(q(r['analytic_joint_residual_upper'])<=q(r['tolerance'])),'residual status')
    dt=read(prior.PREPARED)['selected_configuration']['ordinary_dt']
    rates=[sum(float(w)*j for w,j in zip(row,r['reference_current'],strict=True)) for row in bv]
    require(r['reference_continuity_proposal']==[float(c)-float(dt)*v for c,v in zip(subject['roles'][role]['C'],rates,strict=True)],'continuity proposal drift')
    require(0<=q(r['exact_feedback_current_max_lower'])<=q(r['exact_feedback_current_max_upper'])
        and 0<=r['exact_feedback_nonzero_coordinates']<=m,'feedback enclosure invalid')
    require(q(r['condition_squared_upper'])<=q(params['solver']['conditioning_limit'])**2,'condition limit')
    with ctx.workprec(iv.BITS):
        bounds=prior.certificate(subject,role)['bounds'];p=params['candidate']
        expected=bridge(bounds,p['chi_C'],q(p['zeta_C'])*q(p['chi_C']),q(params['geometry']['kappa_H'])*q(p['zeta_C']),
                        r['analytic_current_residual_upper'],r['analytic_geometry_residual_upper'])
        require(expected==r['joint_root_bridge'],'current-defect/root-error bridge drift')
        contraction=q(bounds['contraction_upper'])
        tail=contraction*q(r['exact_picard_displacement_upper'])/(1-contraction)
        require(str(tail)==r['exact_root_geometry_tail_upper'] and
            str(q(bounds['current_lipschitz_upper'])*tail)==r['exact_root_current_tail_upper'],'root-tail drift')
    return dict(graph=value['graph'],role=role,outcome=value['outcome'],
        analytic_joint_residual_upper=r['analytic_joint_residual_upper'],
        independent_analytic_residual_pass=r['independent_analytic_residual_pass'],
        joint_root_bridge=r['joint_root_bridge'],
        exact_feedback_current_max_lower=r['exact_feedback_current_max_lower'],
        exact_feedback_current_max_upper=r['exact_feedback_current_max_upper'],
        counterfactual_changed_current_coordinates=r['counterfactual_changed_current_coordinates'],
        generated_changed_diagonals=r['generated_changed_diagonals'],
        generated_nonzero_offdiagonals=r['generated_nonzero_offdiagonals'],
        minimum_continuity_proposal=min(r['reference_continuity_proposal']),worker_seconds=value['worker_seconds'])


def summarize():
    cases=[]
    for graph,role in CASES:
        path=case_path(graph,role);r=read(path)
        cases.append(dict(check_case(r),path=path,sha256=hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),record_digest=r['record_digest']))
    return seal(dict(schema='p984g-cci-staged-results-v1',family='C_CI',cases=cases,
        scope='independent_staged_reference_and_counterfactual_not_native_stopping',
        native_roots=0,native_steps=0,native_events=0,ready_for_8_4h=False,user_accepted=False,aggregate_closed=False))


def check():
    value=read(RESULTS);require(value==summarize(),'staged summary drift');return value


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=('run-case','summarize','check'))
    p.add_argument('--graph',choices=('source','target'));p.add_argument('--role',choices=('current','reset'));args=p.parse_args()
    if args.mode=='run-case':run_case(args.graph,args.role)
    elif args.mode=='summarize':
        require(not (ROOT/RESULTS).exists(),'no summary overwrite');(ROOT/RESULTS).write_text(json.dumps(summarize(),indent=2)+'\n')
    else:check()


if __name__=='__main__':main()

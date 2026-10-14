"""Independent two-stage fixed-row A_CI oracle; no native root or step."""
import argparse
import hashlib
import json
import lzma
import math
import platform
import signal
import time
from flint import arb, arb_mat, ctx, fmpq_mat
import p984g_aci_feasibility as feasible

prior=feasible.prior
ROOT,BASE,HERE=prior.ROOT,prior.BASE,prior.HERE
SELF=HERE+'p984g_aci_staged.py'
TEST=HERE+'test_p984g_aci_staged.py'
PLAN=BASE+'P9-8.4g-ACIStagedPlan.md'
NOTE=BASE+'P9-8.4g-ACIStaged.md'
RESULTS=BASE+'P9-8.4g-ACIStagedResults.json.xz'
q,a,lo,hi,require=feasible.q,feasible.a,feasible.lo,feasible.hi,feasible.require
BITS=192


def rn(x):
    x=q(x);v=int(x.p)/int(x.q)
    require(math.isfinite(v),'represented overflow');return v


def unique(x):
    left,right=rn(lo(x)),rn(hi(x))
    require(left==right,'binary64 rounding not certified; no fallback')
    return left


def matrix(rows):
    return arb_mat([[a(x) for x in row] for row in rows])


def eye(n):return arb_mat([[int(i==j) for j in range(n)] for i in range(n)])


def entries(m):return [m[i,j] for i in range(m.nrows()) for j in range(m.ncols())]


def norm(m):return feasible.norm(entries(m))


def model(subject,role):
    bv,ends,c,w,desc=prior.operands(subject,role)
    return dict(subject=subject,role=role,bv=bv,ends=ends,c=c,w=w,desc=desc,
        b=matrix(bv.tolist()),p=subject['profile']['params_resolved']['candidate'],
        params=subject['profile']['params_resolved'],mask=abs(bv).T@abs(bv)/2)


def image(model,flat,*,staged):
    n=len(model['w']);out=eye(n);p=model['p']
    zeta,kh=q(p['zeta_A']),q(model['params']['geometry']['kappa_H'])
    for i in range(n):
        for j in range(n):
            k=q(float(model['mask'][i,j]))
            if not k:continue
            if staged:
                star=rn(k*q(flat[i])*q(flat[j]));inc=rn(zeta*q(star))
                out[i,j]=a(float(i==j)+rn(kh*q(inc)))
            else:out[i,j]+=a(kh*zeta*k)*flat[i,0]*flat[j,0]
    return out


def analytic(model,h,trial=None):
    b,p,c,w=model['b'],model['p'],model['c'],model['w'];m=len(w)
    gradient=b.transpose()*matrix([[x] for x in c])
    potential=arb_mat([[a(p['kappa_c'])*a(w[i]) if i==j else arb(0) for j in range(m)] for i in range(m)])+a(p['kappa_Ah'])*(h-eye(m))
    raw=b.transpose()*(b*(potential*gradient))
    j0=[-a(p['eta'])*a(wi)*raw[i,0] for i,wi in enumerate(w)]
    drive=feasible.drive(p,model['ends'],list(map(a,c)),[[a(x) for x in row] for row in model['desc']],j0)
    contrast=[(a(wi)-g)/(a(wi)+g) for wi,g in zip(w,drive)]
    block=[1-a(p['zeta_A'])*a(p['chi_A'])*x for x in contrast]
    require(all(lo(x)>0 for x in block),'analytic physical margin')
    current=arb_mat([[j/d] for j,d in zip(j0,block)]) if trial is None else matrix([[x] for x in trial])
    flux=arb_mat([[a(p['chi_A'])*x*current[i,0]] for i,x in enumerate(contrast)])
    flat=h.solve(flux,algorithm='lu')
    return dict(J=current,baseline=j0,block=block,flat=flat,
        fj=arb_mat([[block[i]*current[i,0]-j0[i]] for i in range(m)]),generated=image(model,flat,staged=False))


def represented(model,h):
    """Explicit primitive staging, not a production current/geometry call."""
    p,c,w,ends=model['p'],model['c'],model['w'],model['ends'];m=len(w)
    hq=fmpq_mat([[q(unique(h[i,j])) for j in range(m)] for i in range(m)])
    d=fmpq_mat([[c[u]-c[v]] for u,v in ends])
    delta=(hq-fmpq_mat([[int(i==j) for j in range(m)] for i in range(m)]))*d
    phi=[q(0) for _ in c];dp=[q(0) for _ in c]
    for i,(u,v) in enumerate(ends):
        term=q(p['kappa_c'])*w[i]*d[i,0];phi[u]+=term;phi[v]-=term
        term=q(p['kappa_Ah'])*delta[i,0];dp[u]+=term;dp[v]-=term
    phi=[rn(x+y) for x,y in zip(phi,dp)]
    baseline=[rn(-q(rn(q(p['eta'])*wi))*(q(phi[u])-q(phi[v]))) for wi,(u,v) in zip(w,ends)]
    desc=[[q(rn(x)) for x in row] for row in model['desc']]
    drives=[]
    for i,(u,v) in enumerate(ends):
        exponent=-(q(p['alpha'])*(c[u]+c[v])+q(p['beta'])*sum(((x-y)**2 for x,y in zip(desc[u],desc[v])),q(0))+q(p['gamma'])*q(baseline[i])**2)/2
        require(-1000<exponent<1000,'bounded staged exponent')
        drives.append(max(p['W_floor'],math.exp(rn(exponent))))
    contrast=[(x-q(y))/(x+q(y)) for x,y in zip(w,drives)]
    block=[1-q(p['zeta_A'])*q(p['chi_A'])*x for x in contrast]
    require(min(block)>0 and max(block)/min(block)<=q(model['params']['solver']['conditioning_limit']),'staged physical block')
    current=[rn(q(j)/d) for j,d in zip(baseline,block)]
    flux=[rn(q(p['chi_A'])*x*q(j)) for x,j in zip(contrast,current)]
    solution=h.solve(matrix([[x] for x in flux]),algorithm='lu')
    flat=[unique(solution[i,0]) for i in range(m)]
    # Retained solve residual and H-ball check are independent of native policy.
    solve_residual=norm(h*matrix([[x] for x in flat])-matrix([[x] for x in flux]))
    solver=model['params']['solver'];rhsnorm=feasible.norm(list(map(a,flux)))
    require(solve_residual<=q(solver['absolute_tolerance'])+q(solver['relative_tolerance'])*rhsnorm,'flat residual')
    return dict(potential=phi,baseline=baseline,drive=drives,current=current,flux=flux,flat=flat,
        flat_residual_upper=str(solve_residual))


def bridge(bounds,p,geometry_gain,fj,fh):
    """Correct the current defect before applying the reduced-map theorem."""
    r=q(bounds['radius']);margin=q(bounds['current_margin_lower']);contraction=q(bounds['contraction_upper'])
    require(0<=r<1 and margin>0 and 0<=contraction<1 and q(fj)>=0 and q(fh)>=0,'bridge hypotheses')
    dj=q(fj)/margin
    # |(W-G)/(W+G)|<1 for positive operands; sufficient uniform bound.
    df=abs(q(p['chi_A']))/(1-r)*dj
    source=abs(q(geometry_gain)*q(p['zeta_A']))*(2*q(bounds['flat_upper'])+df)*df
    dh=(q(fh)+source)/(1-contraction);djroot=dj+q(bounds['current_lipschitz_upper'])*dh
    return dict(current_defect_upper=str(dj),flat_defect_upper=str(df),source_defect_upper=str(source),
        geometry_error_upper=str(dh),current_error_upper=str(djroot),joint_error_upper=str(prior.norm([dh,djroot])))


def stage(model,h,point,bounds):
    exact=analytic(model,h,point['current']);fj,fh=norm(exact['fj']),norm(h-exact['generated'])
    joint=prior.norm([fj,fh]);tol=q(model['params']['realization']['tolerance'])
    require(norm(h-eye(len(model['w'])))<=q(bounds['radius']),'trial outside declared ball')
    return dict(analytic_current_residual_upper=str(fj),analytic_geometry_residual_upper=str(fh),
        analytic_joint_residual_upper=str(joint),analytic_residual_pass=joint<=tol,
        joint_root_bridge=bridge(bounds,model['p'],model['params']['geometry']['kappa_H'],fj,fh))


def analyze(subject,role,dt):
    md=model(subject,role);bounds=prior.certificate(subject,role,dt)['bounds'];n=len(md['w']);identity=eye(n)
    first=represented(md,identity);h1=image(md,first['flat'],staged=True)
    confirm=represented(md,h1);h2=image(md,confirm['flat'],staged=True)
    checks=[stage(md,h,point,bounds) for h,point in ((identity,first),(h1,confirm))]
    # Exact-real first Picard image and certified tail, independent of staged H1.
    ref=analytic(md,identity);exact_h1=ref['generated'];one=analytic(md,exact_h1)
    contraction=q(bounds['contraction_upper']);displacement=norm(exact_h1-identity)
    tail_h=contraction*displacement/(1-contraction);tail_j=q(bounds['current_lipschitz_upper'])*tail_h
    root=[feasible.inflate(one['J'][i,0],tail_j) for i in range(n)]
    effects=[root[i]-ref['J'][i,0] for i in range(n)]
    effect_lowers=[lo(abs(x)) for x in effects];witness=max(range(n),key=lambda i:effect_lowers[i])
    error=[hi(abs(a(x)-y)) for x,y in zip(confirm['current'],root)]
    separated=max(range(n),key=lambda i:effect_lowers[i]-error[i])
    bv=md['bv'];rates=[sum(float(z)*j for z,j in zip(row,confirm['current'])) for row in bv]
    after=[float(c)-float(dt)*rate for c,rate in zip(md['c'],rates)]
    resource=[]
    for i,row in enumerate(bv):
        exact=a(md['c'][i])-a(dt)*sum((int(z)*j for z,j in zip(row,root)),arb(0))
        resource.append(dict(lower=str(lo(exact)),upper=str(hi(exact)),represented=after[i],
            represented_error_upper=str(hi(abs(a(after[i])-exact)))))
    hrows=[[unique(h1[i,j]) for j in range(n)] for i in range(n)]
    return dict(reference=first,confirming=confirm,stages=checks,
        represented_geometry_digest=prior.shared.digest(hrows),
        selected_joint_point_digest=prior.shared.digest(dict(graph=subject['graph'],profile=subject['profile'],
            C=subject['roles'][role]['C'],W_A=subject['roles'][role]['W_A'],H=hrows,J=confirm['current'])),
        generated_changed_diagonals=sum(hrows[i][i]!=1 for i in range(n)),
        generated_nonzero_offdiagonals=sum(hrows[i][j]!=0 for i in range(n) for j in range(n) if i!=j),
        confirming_changed_current_coordinates=sum(x!=y for x,y in zip(first['current'],confirm['current'])),
        represented_regeneration_distance_upper=str(norm(h2-h1)),
        two_consecutive_independent_residual_passes=all(x['analytic_residual_pass'] for x in checks),
        exact_picard_displacement_upper=str(displacement),exact_root_geometry_tail_upper=str(tail_h),
        exact_root_current_tail_upper=str(tail_j),selected_current_error_upper=str(max(error)),
        exact_feedback_current_max_lower=str(max(effect_lowers)),exact_feedback_current_max_upper=str(max(hi(abs(x)) for x in effects)),
        feedback_coordinates_above_selected_error=sum(x>y for x,y in zip(effect_lowers,error)),
        separated_effect_witness=dict(edge_index=separated,lower=str(effect_lowers[separated]),
            selected_coordinate_error_upper=str(error[separated]),
            above_selected_coordinate_error=effect_lowers[separated]>error[separated]),
        effect_witness=dict(edge_index=witness,lower=str(effect_lowers[witness]),
            upper=str(hi(abs(effects[witness]))),reference_ulp=str(q(math.ulp(first['current'][witness]))),
            selected_coordinate_error_upper=str(error[witness]),above_selected_coordinate_error=effect_lowers[witness]>error[witness]),
        resources=resource,represented_minimum_resource=min(after),
        exact_root_minimum_resource_lower=str(min(q(x['lower']) for x in resource)),
        native_stopping_outcome_verified=False)


def bindings():
    names=[SELF,TEST,PLAN,NOTE,prior.SELF,feasible.SELF,feasible.RESULTS,
        'src/pygrc/models/grc_v4_ci.py','src/pygrc/models/grc_v4_candidate_a.py',
        'src/pygrc/models/grc_v4_geometry.py','src/pygrc/models/grc_v4_transport.py']
    return {s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest() for s in names}


def calculate():
    old=feasible.check_retained();dt=prior.read(prior.PREPARED)['selected_configuration']['ordinary_dt'];cases=[]
    require(ctx.threads==1,'single FLINT thread required')
    def timeout(*_):raise TimeoutError('300-second research cap; no fallback')
    saved=signal.signal(signal.SIGALRM,timeout)
    try:
        for graph,role in prior.shared.CASES:
            signal.alarm(300);start=time.monotonic()
            with ctx.workprec(BITS):result=analyze(old[graph],role,dt)
            signal.alarm(0)
            print(graph,role,'research complete',round(time.monotonic()-start,2),'s',flush=True)
            cases.append(dict(graph=graph,role=role,result=result))
    finally:signal.alarm(0);signal.signal(signal.SIGALRM,saved)
    return prior.seal(dict(schema='p984g-aci-staged-v1',family='A_CI',cases=cases,source_bindings=bindings(),
        precision_bits=BITS,linear_solve='rigorous_Arb_LU_single_RHS_unique_binary64_no_fallback',
        host_python=platform.python_version(),scope='independent_staged_two_trial_oracle_not_native_stopping',
        native_roots=0,native_steps=0,native_events=0,ready_for_8_4h=False,user_accepted=False,
        open_obligations=['native certificate/two-pass stopping comparison',
            'history writer, final-C admission and represented charge',
            '8.4h fresh postbeat event/transfer and continuation']))


def read():return json.loads(lzma.decompress((ROOT/RESULTS).read_bytes()))


def check_retained(value=None):
    value=read() if value is None else value
    require(value==prior.seal(value) and value['source_bindings']==bindings(),'staged source/digest drift')
    require(value['schema']=='p984g-aci-staged-v1' and value['family']=='A_CI' and value['precision_bits']==BITS,'staged schema/precision')
    require([(c['graph'],c['role']) for c in value['cases']]==list(prior.shared.CASES),'four-case roster')
    require(all(value[k]==0 for k in ('native_roots','native_steps','native_events','ready_for_8_4h','user_accepted')),'scope promotion')
    companion=feasible.check_retained()
    for c in value['cases']:
        r=c['result'];require(r['native_stopping_outcome_verified'] is False,'native stopping promotion')
        require(r['two_consecutive_independent_residual_passes'] and all(s['analytic_residual_pass'] for s in r['stages']),'independent residual hold')
        require(r['represented_minimum_resource']>0 and q(r['exact_root_minimum_resource_lower'])>0,'resource hold')
        subject=companion[c['graph']];md=model(subject,c['role']);m=len(md['w'])
        with ctx.workprec(BITS):
            bounds=prior.certificate(subject,c['role'],1)['bounds']
            for s in r['stages']:
                fj,fh=q(s['analytic_current_residual_upper']),q(s['analytic_geometry_residual_upper'])
                require(q(s['analytic_joint_residual_upper'])==prior.norm([fj,fh])
                    and q(s['analytic_joint_residual_upper'])<=q(md['params']['realization']['tolerance']),'joint residual drift')
                require(s['joint_root_bridge']==bridge(bounds,md['p'],md['params']['geometry']['kappa_H'],fj,fh),'bridge drift')
            for point in (r['reference'],r['confirming']):
                for name in ('baseline','drive','current','flux','flat'):
                    require(len(point[name])==m and all(math.isfinite(x) for x in point[name]),'represented coordinate drift')
            h=image(md,r['reference']['flat'],staged=True);hrows=[[unique(h[i,j]) for j in range(m)] for i in range(m)]
            require(r['represented_geometry_digest']==prior.shared.digest(hrows),'geometry digest drift')
            require(r['selected_joint_point_digest']==prior.shared.digest(dict(graph=subject['graph'],profile=subject['profile'],
                C=subject['roles'][c['role']]['C'],W_A=subject['roles'][c['role']]['W_A'],H=hrows,J=r['confirming']['current'])),'whole joint point drift')
            require(r['confirming_changed_current_coordinates']==sum(x!=y for x,y in zip(r['reference']['current'],r['confirming']['current'])),'changed current count')
    return value


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('mode',choices=('run','check','recompute'));args=parser.parse_args()
    if args.mode=='run':
        require(not (ROOT/RESULTS).exists(),'no evidence overwrite')
        result=calculate();check_retained(result)
        (ROOT/RESULTS).write_bytes(lzma.compress((json.dumps(result,indent=2)+'\n').encode(),preset=6))
    elif args.mode=='recompute':require(read()==calculate(),'staged numerical recomputation mismatch')
    else:check_retained()


if __name__=='__main__':main()

"""Independent represented A_PC chain; no native read, step or event owner."""
import argparse
from copy import deepcopy
import hashlib
import json
import lzma
import math
import platform
import signal
import time
from flint import arb, arb_mat, ctx
import p984g_apc_feasibility as feasible
import p984g_aci_staged as fixed

prior=feasible.prior
ROOT,BASE,HERE=prior.ROOT,prior.BASE,prior.HERE
SELF=HERE+'p984g_apc_staged.py';TEST=HERE+'test_p984g_apc_staged.py'
PLAN=BASE+'P9-8.4g-APCStagedPlan.md';NOTE=BASE+'P9-8.4g-APCStaged.md'
RESULTS=BASE+'P9-8.4g-APCStagedResults.json.xz'
q,a,lo,hi,require=feasible.q,feasible.a,feasible.lo,feasible.hi,feasible.require
rn,unique,matrix,eye=fixed.rn,fixed.unique,fixed.matrix,fixed.eye
BITS=256
digest=prior.rows.shared.digest


def model(subject,role,c=None,w=None):
    s=deepcopy(subject)
    if c is not None:s['roles'][role]['C']=c
    if w is not None:s['roles'][role]['W_A']=w
    bv,ends,c,w,desc=prior.operands(s,role)
    return dict(subject=s,role=role,bv=bv,ends=ends,c=c,w=w,desc=desc,
        b=matrix(bv.tolist()),p=s['profile']['params_resolved']['candidate'],
        params=s['profile']['params_resolved'],mask=abs(bv).T@abs(bv)/2)


def sparse(rows):
    return dict(size=len(rows),entries=[[i,j,x] for i,row in enumerate(rows) for j,x in enumerate(row) if x!=0])


def unpack(value):
    n=value['size'];require(type(n) is int and n>0,'matrix size')
    rows=[[0.]*n for _ in range(n)];seen=set()
    for i,j,x in value['entries']:
        require(type(i) is type(j) is int and 0<=i<n and 0<=j<n and (i,j) not in seen
            and type(x) in (float,int) and math.isfinite(x) and x!=0,'noncanonical sparse matrix')
        seen.add((i,j));rows[i][j]=x
    require(value==sparse(rows),'sparse ordering')
    return rows


def norm(xs):return prior.scalar.norm(xs)
def maxerr(actual,expected):return max(hi(abs(a(x)-y)) for x,y in zip(actual,expected))


def hodge(z,kh):
    n=len(z);require(all(len(row)==n for row in z),'square carrier')
    require(all(z[i][j]==z[j][i] for i in range(n) for j in range(i)),'symmetric carrier')
    real=eye(n)+a(kh)*matrix(z)
    rows=[[float(i==j)+rn(q(kh)*q(z[i][j])) for j in range(n)] for i in range(n)]
    radius=max(sum((abs(q(x)-int(i==j)) for j,x in enumerate(row)),q(0)) for i,row in enumerate(rows))
    require(radius<1,'represented Hodge SPD bound inconclusive')
    return matrix(rows),real,rows,(1+radius)/(1-radius)


def analytic(md,h):
    """Full dense fixed-H law, including rounded-geometry error separately."""
    b,p,c,w=md['b'],md['p'],md['c'],md['w'];n=len(w)
    d=b.transpose()*matrix([[x] for x in c])
    potential=arb_mat([[a(p['kappa_c'])*a(w[i]) if i==j else arb(0) for j in range(n)] for i in range(n)])+a(p['kappa_Ah'])*(h-eye(n))
    raw=b.transpose()*(b*(potential*d))
    baseline=[-a(p['eta'])*a(wi)*raw[i,0] for i,wi in enumerate(w)]
    drive=prior.floored_drive(p,md['ends'],list(map(a,c)),[[a(x) for x in r] for r in md['desc']],baseline)
    contrast=[(a(wi)-g)/(a(wi)+g) for wi,g in zip(w,drive)]
    blocks=[1-a(p['zeta_A'])*a(p['chi_A'])*x for x in contrast]
    require(min(lo(x) for x in blocks)>0,'analytic current margin')
    current=[j/d for j,d in zip(baseline,blocks)]
    flux=[a(p['chi_A'])*x*j for x,j in zip(contrast,current)]
    flat=h.solve(matrix([[x] for x in flux]),algorithm='lu')
    return dict(baseline=baseline,current=current,flux=flux,flat=[flat[i,0] for i in range(n)])


def source(md,flat,*,represented):
    n=len(flat);zeta=q(md['p']['zeta_A']);out=[[0. if represented else arb(0) for _ in flat] for _ in flat]
    for i in range(n):
        for j in range(n):
            k=q(float(md['mask'][i,j]))
            if k:out[i][j]=rn(zeta*q(rn(k*q(flat[i])*q(flat[j])))) if represented else a(zeta*k)*flat[i]*flat[j]
    return out


def read(md,z,*,controls=True):
    h,real,hrows,condition=hodge(z,md['params']['geometry']['kappa_H'])
    require(condition<=q(md['params']['solver']['conditioning_limit']),'Hodge condition bound')
    value=fixed.represented(md,h);exact=analytic(md,real);n=len(z)
    s=source(md,value['flat'],represented=True);es=source(md,exact['flat'],represented=False)
    errors={key:str(maxerr(value[key],exact[key])) for key in ('baseline','current','flux','flat')}
    errors['source']=str(maxerr([x for row in s for x in row],[x for row in es for x in row]))
    errors['geometry']=str(maxerr([x for row in hrows for x in row],fixed.entries(real)))
    cp=md['p'];residual=[a(j)-a(j0)-a(cp['zeta_A'])*a(f) for j,j0,f in zip(value['current'],value['baseline'],value['flux'])]
    tol=q(md['params']['solver']['absolute_tolerance'])+q(md['params']['solver']['relative_tolerance'])*norm(list(map(a,value['baseline'])))
    require(norm(residual)<=tol,'represented Read-Back closure residual')
    effects={}
    if controls:
        # These two exact-real controls change only the named mechanism.
        carrier_off=analytic(md,eye(n))['current']
        for key,other in (('carrier',carrier_off),('readback',exact['baseline'])):
            lowers=[max(q(0),lo(abs(x-y))) for x,y in zip(exact['current'],other)]
            errors_i=[hi(abs(a(x)-y)) for x,y in zip(value['current'],exact['current'])]
            i=max(range(n),key=lambda i:lowers[i]-errors_i[i])
            effects[key]=dict(maximum_lower=str(max(lowers)),witness=i,lower=str(lowers[i]),
                represented_error_upper=str(errors_i[i]),separated_coordinates=sum(x>e for x,e in zip(lowers,errors_i)))
    out=dict(**value,H=sparse(hrows),source=sparse(s),errors=errors,effects=effects,
        hodge_condition_upper=str(condition),readback_closure_residual_upper=str(norm(residual)))
    out['point_digest']=digest(dict(C=list(map(float,md['c'])),W_A=list(map(float,md['w'])),Z=sparse(z),
        H=out['H'],current=value['current'],readback=value['flux'],flat=value['flat'],source=out['source']))
    return out


def writer_drive(md,c,current):
    # Fixed-row descriptors use incoming W but post-continuity C.
    fresh=model(md['subject'],md['role'],c,list(map(float,md['w'])))
    desc=[[q(rn(x)) for x in row] for row in fresh['desc']];p=md['p'];out=[]
    for k,(u,v) in enumerate(md['ends']):
        exponent=-(q(p['alpha'])*(q(c[u])+q(c[v]))+q(p['beta'])*sum(((x-y)**2 for x,y in zip(desc[u],desc[v])),q(0))+q(p['gamma'])*q(current[k])**2)/2
        require(-1000<exponent<1000,'bounded writer exponent')
        out.append(max(p['W_floor'],math.exp(rn(exponent))))
    return out


def write_w(w,drive,dt,tau):
    require(dt>=0 and tau>0 and len(w)==len(drive) and min(w+drive)>0,'log writer domain')
    decay=(-a(dt)/a(tau)).exp()
    real=[a(x) if x==y else (decay*a(x).log()+(1-decay)*a(y).log()).exp() for x,y in zip(w,drive)]
    out=[unique(x) for x in real]
    return out,str(maxerr(out,real))


def write_z(z,s,dt,tau):
    require(dt>=0 and tau>0 and len(z)==len(s),'ZOH domain')
    decay=(-a(dt)/a(tau)).exp();rows=[];err=q(0)
    for left,right in zip(z,s):
        require(len(left)==len(z)==len(right),'ZOH shape')
        real=[a(x) if x==y else a(y)+decay*(a(x)-a(y)) for x,y in zip(left,right)]
        values=[unique(x) for x in real];err=max(err,maxerr(values,real));rows.append(values)
    return rows,str(err)


def analyze(subject,role,dt):
    md=model(subject,role);n=len(md['w']);diag=prior.carrier(subject,role,n)
    z=[[float(diag[i]) if i==j else 0. for j in range(n)] for i in range(n)]
    before=read(md,z)
    # GRCV4Differential.divergence sums binary64 terms in graph edge order.
    rates=[sum(float(x)*j for x,j in zip(row,before['current'])) for row in md['bv']]
    c=[float(x)-float(dt)*r for x,r in zip(md['c'],rates)]
    require(min(c)>0,'represented resource failure')
    drive=writer_drive(md,c,before['current'])
    w,we=write_w(list(map(float,md['w'])),drive,dt,md['p']['tau_A'])
    znew,ze=write_z(z,unpack(before['source']),dt,md['params']['realization']['tau_PC'])
    M,wl,wu,R,_=prior.chart(subject)
    require(sum((q(x)**2 for x in c),q(0))<=M*M and all(wl<=q(x)<=wu for x in w),'final base chart')
    znorm=norm([a(x) for row in znew for x in row]);require(znorm<=R,'final carrier chart')
    aftermd=model(subject,role,c,w);final=read(aftermd,znew)
    stale=fixed.represented(aftermd,matrix(unpack(before['H'])))
    offdiag=sum(x!=0 for i,row in enumerate(znew) for j,x in enumerate(row) if i!=j)
    exact_rates=[sum((int(x)*a(j) for x,j in zip(row,before['current'])),arb(0)) for row in md['bv']]
    continuity_error=maxerr(c,[a(x)-a(dt)*r for x,r in zip(md['c'],exact_rates)])
    result=dict(initial=before,final=final,C=c,W_A=w,Z=sparse(znew),writer_target=drive,
        history_writer_stage='postcontinuity_C_incoming_W_selected_current',carrier_writer_stage='incoming_PC_read_held_source',
        history_writer_rounding_error_upper=we,carrier_writer_rounding_error_upper=ze,
        continuity_staging_error_upper=str(continuity_error),minimum_resource=min(c),
        exact_stored_charge_drift=str(sum(map(q,c),q(0))-sum(md['c'],q(0))),
        carrier_norm_upper=str(znorm),nonzero_offdiagonal_carrier_entries=offdiag,
        stale_Z_final_current_changed_coordinates=sum(x!=y for x,y in zip(stale['current'],final['current'])),
        full_chain_digest=digest(dict(initial=before,C=c,W_A=w,Z=sparse(znew),final=final)),
        final_read_executed=True,native_admission=False)
    return result


def bindings():
    names=[SELF,TEST,PLAN,feasible.SELF,feasible.RESULTS,prior.SELF,fixed.SELF,prior.rows.SELF,prior.scalar.SELF,
        'src/pygrc/models/grc_v4_candidate_a.py','src/pygrc/models/grc_v4_pc.py',
        'src/pygrc/models/grc_v4_geometry.py','src/pygrc/models/grc_v4_transport.py']
    return {s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest() for s in names}


def calculate():
    v=feasible.check_retained();dt=prior.read(prior.PREPARED)['selected_configuration']['ordinary_dt'];cases=[]
    require(ctx.threads==1,'one FLINT thread')
    def timeout(*_):raise TimeoutError('300-second case cap; no fallback')
    saved=signal.signal(signal.SIGALRM,timeout)
    try:
        for graph,role in prior.rows.shared.CASES:
            signal.alarm(300);start=time.monotonic()
            with ctx.workprec(BITS):r=analyze(v[graph],role,dt)
            signal.alarm(0);print(graph,role,'complete',round(time.monotonic()-start,2),'s',flush=True)
            cases.append(dict(graph=graph,role=role,result=r))
    finally:signal.alarm(0);signal.signal(signal.SIGALRM,saved)
    return prior.seal(dict(schema='p984g-apc-staged-v1',family='A_PC',precision_bits=BITS,cases=cases,
        source_bindings=bindings(),feasibility_digest=v['record_digest'],host_python=platform.python_version(),
        scope='independent_represented_PC_four_prepared_roles_not_native_or_event',
        linear_solve='fixed_256_bit_Arb_LU_unique_binary64_no_fallback',native_steps=0,native_events=0,
        ready_for_8_4h=False,user_accepted=False,aggregate_closed=False,
        open_obligations=['review independent oracle and compare native complete steps/charge admission',
            '8.4h fresh actual postbeat identity, both-role archive/transfer/readmission and continuation']))


def load():return json.loads(lzma.decompress((ROOT/RESULTS).read_bytes()))


def check_retained(v=None):
    v=load() if v is None else v
    require(v==prior.seal(v) and v['source_bindings']==bindings(),'staged identity/source drift')
    require(v['schema']=='p984g-apc-staged-v1' and v['family']=='A_PC' and v['precision_bits']==BITS
        and v['scope']=='independent_represented_PC_four_prepared_roles_not_native_or_event','staged scope')
    require(v['feasibility_digest']==feasible.check_retained()['record_digest'],'feasibility binding')
    require([(x['graph'],x['role']) for x in v['cases']]==list(prior.rows.shared.CASES),'case roster')
    require(all(v[k]==0 for k in ('native_steps','native_events','ready_for_8_4h','user_accepted','aggregate_closed')),'promotion')
    for case in v['cases']:
        r=case['result'];z=unpack(r['Z'])
        require(r['minimum_resource']==min(r['C'])>0 and r['final_read_executed'] and not r['native_admission'],'resource/read scope')
        require(r['history_writer_stage']=='postcontinuity_C_incoming_W_selected_current' and
            r['carrier_writer_stage']=='incoming_PC_read_held_source','writer stages')
        require(r['full_chain_digest']==digest(dict(initial=r['initial'],C=r['C'],W_A=r['W_A'],Z=r['Z'],final=r['final'])),'whole-chain drift')
        require(r['nonzero_offdiagonal_carrier_entries']==sum(x!=0 for i,row in enumerate(z) for j,x in enumerate(row) if i!=j)>0,'full carrier missing')
        for point in (r['initial'],r['final']):
            unpack(point['H']);unpack(point['source'])
            require(all(q(e)>=0 for e in point['errors'].values()),'error bound sign')
    return v


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('mode',choices=('run','check','recompute'));args=parser.parse_args()
    if args.mode=='run':
        require(not (ROOT/RESULTS).exists(),'no overwrite');v=calculate();check_retained(v)
        raw=(json.dumps(v,separators=(',',':'))+'\n').encode();require(len(raw)<=8000000,'raw evidence budget')
        (ROOT/RESULTS).write_bytes(lzma.compress(raw,preset=6))
    elif args.mode=='recompute':require(load()==calculate(),'staged recomputation drift')
    else:check_retained()

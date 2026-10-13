"""Bounded regularity proof and full-law / staged-arithmetic C_OS enclosures.

Research successor: no change to production sources or prior retained evidence.
Arb ball solves are rigorous (never algorithm='approx'). Binary64 rounding is
enclosed at every declared linear/read/geometry/continuity stage.
"""
import argparse
import hashlib
import json
import math
from copy import deepcopy
from flint import arb, arb_mat, ctx, fmpq, fmpq_mat
import p984g_cos as prior

ROOT, BASE, HERE = prior.ROOT, prior.BASE, prior.HERE
SELF, TEST = HERE+'p984g_cos_bounds.py', HERE+'test_p984g_cos_bounds.py'
PLAN, REVIEW = BASE+'P9-8.4g-COSBoundsPlan.md', BASE+'P9-8.4g-COSBoundsReview.md'
INPUTS, RESULTS = BASE+'P9-8.4g-COSBoundsInputs.json', BASE+'P9-8.4g-COSBoundsResults.json'
BITS=192
require=prior.require


def q(x):
    return x if isinstance(x,fmpq) else fmpq(x) if isinstance(x,(int,str)) else prior.q(x)


def a(x):return arb(q(x))
def lo(x):return x.lower().fmpq()
def hi(x):return x.upper().fmpq()
def magnitude(x):return max(abs(lo(x)),abs(hi(x)))
def eye(n):return arb_mat([[int(i==j) for j in range(n)] for i in range(n)])
def matrix(rows):return arb_mat([[a(x) for x in row] for row in rows])


def norm(x):
    return max((sum((magnitude(x[i,j]) for j in range(x.ncols())),fmpq(0)) for i in range(x.nrows())),default=fmpq(0))


def rounded(x):
    require(x.is_finite(),'nonfinite interval')
    left,right=float(lo(x)),float(hi(x))
    require(math.isfinite(left) and math.isfinite(right),'represented overflow')
    # Monotonic round-to-nearest maps every member to these endpoint bounds.
    return a(left).union(a(right))


def rounded_matrix(x):
    return arb_mat([[rounded(x[i,j]) for j in range(x.ncols())] for i in range(x.nrows())])


def spd_margin(rows):
    """Exact symmetric strict diagonal-dominance witness; sufficient, not iff."""
    rows=[[q(x) for x in row] for row in rows];n=len(rows)
    require(n>0 and all(len(row)==n for row in rows),'square SPD witness required')
    require(all(rows[i][j]==rows[j][i] for i in range(n) for j in range(i)), 'symmetric SPD witness required')
    margin=min(row[i]-sum((abs(x) for j,x in enumerate(row) if j!=i),fmpq(0)) for i,row in enumerate(rows))
    require(margin>0,'positive diagonal-dominance witness unavailable')
    return margin


def regularity(b,h0,hm,beta,tau):
    """Exact boolean equivalent on the explicitly witnessed SPD domain.

    Positive s: similarity to sI+tau Hm^(1/2) B^T H0^-1 B Hm^(1/2).
    Other s: exact rank at zero, otherwise Sylvester's determinant identity.
    No floating determinant and no inverse merely to decide regularity.
    """
    s=1-q(beta);tau=q(tau)
    require(tau>=0,'nonnegative tau required')
    lower0,lowerm=spd_margin(h0),spd_margin(hm)
    b=fmpq_mat([[q(x) for x in row] for row in b]);n,m=b.nrows(),b.ncols()
    require(n==len(h0) and m==len(hm),'regularity coordinate mismatch')
    if s>0:
        return dict(nonsingular=True,method='positive_similarity',s=str(s),
                    h0_lower=str(lower0),hm_lower=str(lowerm),inverse_constructed=False)
    if s==0:
        ok=m==0 or tau>0 and b.rank()==m
        return dict(nonsingular=bool(ok),method='exact_incidence_rank',s='0',inverse_constructed=False)
    # m can be smaller than n; either determinant is equivalent for s != 0.
    # These fallback tests are bounded small pressure cases, not the large path.
    h0m,hmm=(fmpq_mat([[q(x) for x in row] for row in value]) for value in (h0,hm))
    vertex=h0m*s+tau*b*hmm*b.transpose()
    return dict(nonsingular=vertex.det()!=0,method='exact_vertex_determinant',s=str(s),inverse_constructed=False)


def gap(b,h,cutoff):
    deviation=norm(h-eye(h.nrows()))
    bound=(1-deviation)/q(b.nrows()*(b.nrows()-1))
    require(deviation<1 and 0<q(cutoff)<bound,'constant selector gap unproved')
    return dict(geometry_deviation_upper=str(deviation),selector_gap_lower=str(bound-q(cutoff)))


def real_read(b,c,h,p,t):
    """Exact-real constant-selector law with an n-vertex solve, not m-edge inverse."""
    domain=gap(b,h,p['Lambda_C'])
    beta=a(p['zeta_C'])*a(p['chi_C']);s=1-beta
    require(lo(s)>0,'positive-s real reduction required')
    bt=b.transpose();k=a(p['tau_C'])*t
    j0=-a(p['eta_C'])*a(p['kappa_Phi_C'])*bt*b*(t*h)*bt*c
    v=(j0-k*h*bt*(s*eye(b.nrows())+k*b*h*bt).solve(b*j0))/s
    j=j0+beta*v;flux=a(p['chi_C'])*v
    return j,flux,h.solve(flux),domain


def staged_read(b,c,h,p,deformation):
    """Enclose the actual declared binary64 linear stages, not a fused formula."""
    domain=gap(b,h,p['Lambda_C']);m=h.nrows();ident=eye(m);bt=b.transpose()
    hm=rounded_matrix(a(deformation)*h*a(deformation))
    # Strict Gershgorin lower bound certifies all Hm members even if intervals
    # are represented independently. Actual native Hm is symmetric by construction.
    hm_margin=min(lo(hm[i,i])-sum((magnitude(hm[i,j]) for j in range(m) if j!=i),fmpq(0)) for i in range(m))
    require(hm_margin>0 and 1-q(p['zeta_C'])*q(p['chi_C'])>0,'staged regularity proof unavailable')
    domain['retained_hodge_lower']=str(hm_margin)
    phi=rounded_matrix(a(p['kappa_Phi_C'])*b*hm*bt*c)
    j0=rounded_matrix(-a(p['eta_C'])*bt*phi)
    bounds=[]
    def solve(coef,rhs):
        inverse=coef.inv()
        condition_squared=norm(coef)*norm(coef.transpose())*norm(inverse)*norm(inverse.transpose())
        bounds.append(condition_squared)
        return rounded_matrix(inverse*rhs)
    flat=solve(h,ident)
    identification=solve(h,hm.transpose()).transpose()
    inverse_ident=solve(identification,ident)
    metric=rounded_matrix(identification*flat)
    # H0=I in the retained declaration; its exact solve leaves B unchanged.
    laplacian=rounded_matrix(bt*rounded_matrix(b*hm))
    response=solve(rounded_matrix(ident+a(p['tau_C'])*laplacian),ident)
    if p['tau_C']==0:
        flux_response=ident
    else:
        flux_response=solve(metric,rounded_matrix(response*metric))
    block=rounded_matrix(ident-a(p['zeta_C'])*a(p['chi_C'])*flux_response)
    current=solve(block,j0)
    structural_flat=rounded_matrix(flat*current)
    selected=rounded_matrix(identification*structural_flat)
    response_form=rounded_matrix(response*selected)
    ungated=structural_flat if p['tau_C']==0 else rounded_matrix(inverse_ident*response_form)
    causal=rounded_matrix(a(p['chi_C'])*ungated)
    flux=rounded_matrix(a(p['chi_C'])*current) if p['tau_C']==0 else rounded_matrix(h*causal)
    domain['condition_squared_upper']=str(max(bounds))
    return current,flux,causal,domain


def generated(b,flat,params,*,staged):
    m=flat.nrows();out=eye(m)
    overlap=matrix([[abs(b[i,j].mid().fmpq()) for j in range(m)] for i in range(b.nrows())])
    overlap=overlap.transpose()*overlap/2
    for i in range(m):
        for j in range(m):
            if overlap[i,j].is_zero():continue
            star=overlap[i,j]*flat[i,0]*flat[j,0]
            increment=a(params['candidate']['zeta_C'])*(rounded(star) if staged else star)
            term=a(params['geometry']['kappa_H'])*(rounded(increment) if staged else increment)
            out[i,j]=rounded(out[i,j]+rounded(term)) if staged else out[i,j]+term
    return out


def encode_column(x):
    return [dict(lower=str(lo(x[i,0])),upper=str(hi(x[i,0]))) for i in range(x.nrows())]


def represented_continuity(b,cs,current,dt):
    # _matvec uses Python's builtin sum, NOT an exact dot rounded once.
    # Require a unique binary64 current before replaying that literal operation;
    # this avoids assuming an unproved summation error or a different staging.
    require(all(lo(current[i,0])==hi(current[i,0]) for i in range(current.nrows())),
            'represented continuity requires uniquely enclosed current')
    values=[float(lo(current[i,0])) for i in range(current.nrows())]
    rates=[sum(float(b[i,j])*x for j,x in enumerate(values)) for i in range(len(cs))]
    outputs=[float(c)-float(dt)*rate for c,rate in zip(cs,rates,strict=True)]
    require(all(math.isfinite(x) for x in outputs),'represented continuity overflow')
    return matrix([[x] for x in outputs]),values


def interval_case(subject,role,dt,old):
    bv,params=prior.graph_data(subject);b=matrix(bv);n,m=b.nrows(),b.ncols()
    p=params['candidate'];cs=subject['roles'][role]['C'];c=matrix([[x] for x in cs])
    mean=sum((q(x) for x in cs),fmpq(0))/n
    t=(a(p['kappa_M_C'])*(a(mean)/a(p['C_ref'])).tanh()).exp()
    # Native kernel-mode projector rounds the exact component mean once.
    rho=math.tanh(float(mean)/p['C_ref'])
    deformation=math.exp((0.5*p['kappa_M_C'])*(0.5*(rho+rho)))
    require(math.isfinite(deformation) and deformation>0,'native scalar deformation domain')
    row={}
    for staged in (False,True):
        name='staged' if staged else 'exact_real'
        def read(h):
            return staged_read(b,c,h,p,deformation) if staged else real_read(b,c,h,p,t)
        predictor,_,flat,pdomain=read(eye(m))
        h=generated(b,flat,params,staged=staged)
        current,flux,flat,domain=read(h)
        regenerated=generated(b,flat,params,staged=staged)
        split=norm(h-regenerated)
        require(split<=q(params['realization']['tolerance']),'split interval exceeds unchanged tolerance')
        if staged:
            after,values=represented_continuity(b,cs,current,dt)
            require(all(q(d['condition_squared_upper'])<=q(params['solver']['conditioning_limit'])**2
                        for d in (pdomain,domain)),'condition bound exceeds declared limit')
        else:after=c-a(dt)*b*current
        errors=[max(abs(q(x)-lo(after[i,0])),abs(q(x)-hi(after[i,0]))) for i,x in enumerate(old['continuity_proposal'])]
        row[name]=dict(resources=encode_column(after),minimum_lower=str(min(lo(after[i,0]) for i in range(n))),
            maximum_width=str(max(hi(after[i,0])-lo(after[i,0]) for i in range(n))),
            oracle_coordinate_error_upper=str(max(errors)),
            minimum_oracle_sign_separation=str(min(lo(after[i,0])-errors[i] for i in range(n))),
            positive=bool(all(lo(after[i,0])>0 for i in range(n))),
            negative_nodes=[subject['graph']['live_node_ids'][i] for i in range(n) if hi(after[i,0])<0],
            unresolved_nodes=[subject['graph']['live_node_ids'][i] for i in range(n) if lo(after[i,0])<=0<=hi(after[i,0])],
            split_upper=str(split),predictor_domain=pdomain,corrector_domain=domain)
        if staged:row[name]['uniquely_enclosed_current']=values
    # Concrete exact research kernel for the declared reference operand; the
    # interval proof above separately covers every corrector geometry member.
    retained=[[float(q(deformation)**2)*int(i==j) for j in range(m)] for i in range(m)]
    row['regularity']=regularity(bv,[[int(i==j) for j in range(n)] for i in range(n)],
        retained,q(p['zeta_C'])*q(p['chi_C']),p['tau_C'])
    row['native_deformation']=deformation
    return row


def make_manifest():
    paths=[SELF,TEST,PLAN,prior.SELF,prior.TEST,prior.INPUTS,prior.RESULTS,prior.PREPARED,
        'src/pygrc/models/grc_v4_candidate_c.py','src/pygrc/models/grc_v4_realizations.py',
        'src/pygrc/models/grc_v4_numerics.py','src/pygrc/models/_grc_v4_matrix.py',
        'src/pygrc/models/grc_v4_geometry.py','src/pygrc/models/grc_v4_transport.py',
        'specs/grc-v4-spec.md']
    return prior.seal(dict(schema='p984g-cos-bounds-inputs-v1',cases=[list(x) for x in prior.CASES],
        bits=BITS,source_bindings=[dict(path=x,sha256=hashlib.sha256((ROOT/x).read_bytes()).hexdigest()) for x in paths],
        source_configuration='unchanged_P9_8_3_C_OS',consumer=SELF,retained_budget_bytes=500000,
        native_implementation_changed=False,native_admission=False,ready_for_8_4h=False,
        scope='pointwise_full_law_and_conditional_staged_outputs_not_trajectory_or_lifecycle'))


def calculate():
    prepared=prior.read(prior.PREPARED);old=prior.read(prior.RESULTS)
    rows=[]
    with ctx.workprec(BITS):
        for (graph,role),previous in zip(prior.CASES,old['cases'],strict=True):
            require((previous['graph'],previous['role'])==(graph,role),'predecessor roster mismatch')
            row=interval_case(prepared[graph],role,prepared['selected_configuration']['ordinary_dt'],previous)
            rows.append(dict(graph=graph,role=role,**row))
            print(graph,role,'exact-real positive',row['exact_real']['positive'],
                'staged positive',row['staged']['positive'],flush=True)
    return prior.seal(dict(schema='p984g-cos-bounds-v1',inputs_digest=make_manifest()['record_digest'],cases=rows,
        native_admission=False,native_implementation_changed=False,native_events=0,native_steps=0,
        ready_for_8_4h=False,user_accepted=False,aggregate_closed=False))


def check(m,r):
    require(m==make_manifest() and r==prior.seal(r) and r['inputs_digest']==m['record_digest'],'bounds source/identity drift')
    require(r['schema']=='p984g-cos-bounds-v1' and [(x['graph'],x['role']) for x in r['cases']]==list(prior.CASES),'bounds schema/coverage')
    require(all(r[x] is False for x in ('native_admission','native_implementation_changed','ready_for_8_4h','user_accepted','aggregate_closed'))
        and r['native_events']==r['native_steps']==0,'bounds scope promotion')
    for row in r['cases']:
        require(row['regularity']['nonsingular'] and not row['regularity']['inverse_constructed'],'regularity drift')
        subject=prior.read(prior.PREPARED)[row['graph']]
        previous=next(x for x in prior.read(prior.RESULTS)['cases'] if (x['graph'],x['role'])==(row['graph'],row['role']))
        n=len(subject['graph']['live_node_ids']);params=subject['profile']['params_resolved']
        for field in ('exact_real','staged'):
            c=row[field];require(len(c['resources'])==n,'resource roster drift')
            require(q(c['minimum_lower'])==min(q(x['lower']) for x in c['resources']),'minimum bound drift')
            require(c['positive']==all(q(x['lower'])>0 for x in c['resources']),'positivity drift')
            require(all(q(x['lower'])<=q(x['upper']) for x in c['resources']),'invalid interval')
            require(q(c['maximum_width'])==max(q(x['upper'])-q(x['lower']) for x in c['resources']),'width drift')
            errors=[max(abs(q(v)-q(x['lower'])),abs(q(v)-q(x['upper']))) for v,x in zip(previous['continuity_proposal'],c['resources'],strict=True)]
            require(q(c['oracle_coordinate_error_upper'])==max(errors) and
                q(c['minimum_oracle_sign_separation'])==min(q(x['lower'])-e for x,e in zip(c['resources'],errors,strict=True)),'oracle error bound drift')
            require(0<=q(c['split_upper'])<=q(params['realization']['tolerance']),'split bound drift')
            for d in (c['predictor_domain'],c['corrector_domain']):
                delta=q(d['geometry_deviation_upper'])
                require(0<=delta<1 and q(d['selector_gap_lower'])==(1-delta)/(n*(n-1))-q(params['candidate']['Lambda_C'])>0,'selector gap drift')
                if field=='staged':require(q(d['retained_hodge_lower'])>0 and 1<=q(d['condition_squared_upper'])<=q(params['solver']['conditioning_limit'])**2,'staged domain drift')
            nodes=subject['graph']['live_node_ids']
            require(c['negative_nodes']==[node for node,x in zip(nodes,c['resources'],strict=True) if q(x['upper'])<0]
                and c['unresolved_nodes']==[node for node,x in zip(nodes,c['resources'],strict=True) if q(x['lower'])<=0<=q(x['upper'])],'sign classification drift')
            if field=='staged':
                b,_=prior.graph_data(subject)
                outputs,_=represented_continuity(b,subject['roles'][row['role']]['C'],matrix([[x] for x in c['uniquely_enclosed_current']]),prior.read(prior.PREPARED)['selected_configuration']['ordinary_dt'])
                require(encode_column(outputs)==c['resources'],'staged continuity drift')
    return dict(status='pointwise_bounds_completed',family='C_OS',cases=4,
        exact_real_positive=sum(c['exact_real']['positive'] for c in r['cases']),
        staged_positive=sum(c['staged']['positive'] for c in r['cases']),
        native_admission=False,ready_for_8_4h=False,native_steps=0,native_events=0,
        user_accepted=False,aggregate_closed=False,intervals_recomputed=False)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=('prepare','run','check'))
    parser.add_argument('--recheck-numerics',action='store_true')
    args=parser.parse_args();require(not args.recheck_numerics or args.action=='check','invalid mode')
    if args.action=='prepare':prior.write_new(INPUTS,make_manifest())
    elif args.action=='run':
        require(not (ROOT/RESULTS).exists(),'refuse to overwrite evidence')
        m=prior.read(INPUTS);require(m==make_manifest(),'input drift')
        r=calculate();check(m,r);prior.write_new(RESULTS,r)
    else:
        m,r=prior.read(INPUTS),prior.read(RESULTS);summary=check(m,r)
        if args.recheck_numerics:
            require(calculate()==r,'interval reconstruction drift');summary['intervals_recomputed']=True
        print(json.dumps(summary,indent=2))


if __name__=='__main__':main()

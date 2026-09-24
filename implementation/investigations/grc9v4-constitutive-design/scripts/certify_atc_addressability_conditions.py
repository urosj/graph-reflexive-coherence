#!/usr/bin/env python3
"""Exact sufficient-condition pressure; no repeated F/D/N or native campaign.

Uniformly check a nonzero interval of potentials p_lambda(c)=p_0(c)+lambda*c.
This is a new mathematical family, NOT a change to the pinned execution law.
"""
from fractions import Fraction as F
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
INV=ROOT/'implementation/investigations/grc9v4-constitutive-design'
REFS=INV/'evidence/autonomous-topology-change'


def canonical(v):
    return json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False).encode()


def sha(v):
    return hashlib.sha256(v).hexdigest()


def run():
    certificate_path=REFS/'ATCSupportFixtureCertificate.json'
    old=json.loads(certificate_path.read_text())
    assert old['record_digest']=='f0414b6fa38dbe9c57e265530d96580f12d1f58b9bdb927ee06c8e1f167d4d37'
    assert old['record_digest']==sha(canonical({k:v for k,v in old.items() if k!='record_digest'}))
    helper_path=INV/'scripts/certify_atc_support_fixture.py'
    expected=next(v['sha256'] for v in old['source_bindings'] if v['path']==helper_path.relative_to(ROOT).as_posix())
    assert sha(helper_path.read_bytes())==expected
    spec=importlib.util.spec_from_file_location('addressability_bernstein',helper_path)
    helper=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    p=tuple(map(F,old['binding']['site_derivative_coefficients_ascending']))
    dp=tuple(i*p[i] for i in range(1,len(p)))
    r,x=F(1),F(3,2)
    kappa,eta,h,epsilon=F(1,1024),F(1,4),F(1,64),F(1,4096)
    lam=F(1,8192)
    outer=helper.bernstein(dp,F(31,32),F(33,32))
    child=helper.bernstein(dp,F(47,32),F(49,32))
    mo,mc=F(outer['lower'])-lam,F(child['lower'])-lam
    M=max(F(outer['upper']),F(child['upper']))+lam
    mu=min(mo,mc)-4*kappa
    assert mu>0

    def value(c,l):return sum((a*c**i for i,a in enumerate(p)),F())+l*c
    def g(t,l):return value(x+t,l)-value(r-t,l)-2*kappa*(x-r+2*t)
    g0_upper=max(g(F(),l) for l in (-lam,lam))
    gend_lower=min(g(F(1,256),l) for l in (-lam,lam))
    assert g0_upper<0<gend_lower
    assert mo+mc-4*kappa>0
    j_source_lower=min(eta*(3*kappa*(2*x-r)+value(r,l)-value(2*x,l)) for l in (-lam,lam))
    j_target_lower=min(eta*(2*kappa*(x-r)+value(r,l)-value(x,l)) for l in (-lam,lam))
    assert j_source_lower>0 and x-r>0

    B=((1,0,0),(0,-1,0),(-1,0,1),(0,1,-1))
    L=tuple(tuple(sum(a*b for a,b in zip(row,other,strict=True)) for other in B) for row in B)
    def mm(a,b):return tuple(tuple(sum(a[i][k]*b[k][j] for k in range(4)) for j in range(4)) for i in range(4))
    L3=mm(mm(L,L),L)
    w=tuple(tuple(-L[j][i] for j in range(4)) for i in (2,3))
    assert tuple(L3[i][i] for i in (2,3))==(19,19)
    gram=tuple(tuple(sum(a*b for a,b in zip(row,other,strict=True)) for other in w) for row in w)
    assert gram==((6,-4),(-4,6)) and gram[0][0]*gram[1][1]-gram[0][1]**2==20

    delta0=max(abs(g(F(),l)) for l in (-lam,lam))
    e0=delta0**2/(2*mu)
    r0=delta0/mu  # exact sqrt(2*e0/mu)
    R,dstar=F(1,64),F(7,256)
    D=5*epsilon  # strictly exceeds sqrt(20)*epsilon, simplifying rational checks
    cap=mu*R**2/2
    loaded=e0+M*r0*D+M*D**2/2
    assert e0<cap and r0+D<dstar and loaded<cap
    assert (1+4*h*eta*M)*R<dstar and 4*h*eta*M<2
    response_lower=h*eta/2*(5*mc+mo-19*kappa)
    contraction=1-h*eta*mu*(1-2*h*eta*M)
    assert response_lower>0 and 0<contraction<1
    # Both p_0(r) and p_0(x) were zero. Any nonzero lambda destroys that exact coincidence.
    assert value(r,lam)!=0 and value(x,lam)!=0 and value(2*x,lam)!=0

    paths=[Path(__file__).resolve(),helper_path,certificate_path]
    record=dict(schema='grcv4_atc_addressability_sufficient_conditions_v1',
        status='passed_uniform_exact_inequalities',scientific_status='proposed_conditional_theorem_not_universal_or_admitted',
        scope='same degree-two binary fission and zero-channel exact equations; arbitrary smooth-p criterion with one uniformly certified perturbation family',
        family=dict(p='p_0(c)+lambda*c',coefficients_p0=list(map(str,p)),
            lambda_interval=[str(-lam),str(lam)],uniformity='p, p_prime and bracket values depend affinely on lambda; endpoint bounds cover the full interval, not sampled trajectories',
            r=str(r),x=str(x),kappa=str(kappa),eta=str(eta),h=str(h),epsilon=str(epsilon),
            no_pinned_binding_change=True,no_new_runtime_profile=True),
        source=dict(current_lower=str(j_source_lower),funding_margin=str(x-r)),
        target=dict(initial_exterior_current_lower=str(j_target_lower),outer_slope_lower=str(mo),
            child_slope_lower=str(mc),mu=str(mu),M=str(M),
            equilibrium_t_bracket=['0','1/256'],g_at_zero_upper=str(g0_upper),
            g_at_upper_endpoint_lower=str(gend_lower),g_prime_lower=str(mo+mc-4*kappa)),
        trapping=dict(initial_excess_upper=str(e0),initial_radius_upper=str(r0),R=str(R),
            boundary_clearance_lower=str(dstar),joint_load_norm_upper=str(D),
            loaded_excess_upper=str(loaded),sublevel_cap=str(cap),
            one_step_distance_factor=str(1+4*h*eta*M),contraction_factor_upper=str(contraction)),
        operations=dict(directions=w,gram=gram,gram_determinant=20,L3_child_diagonals=[19,19],
            individual_Q_lower=str(response_lower),joint_claim='one signed joint load followed by exact return; no positive-intake claim for every joint combination'),
        exclusions=['higher_degree_partition','nonzero_geometry_or_history_feedback','all_ten_families',
            'child_identity','universal_F2_justification','rounded_infinite_return','global_stability'],
        ordinary_updates=0,native_steps=0,production_changes=False,
        source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p.read_bytes())) for p in paths])
    record['record_digest']=sha(canonical(record))
    return record


if __name__=='__main__':
    print(json.dumps(run(),separators=(',',':'),ensure_ascii=True,allow_nan=False))

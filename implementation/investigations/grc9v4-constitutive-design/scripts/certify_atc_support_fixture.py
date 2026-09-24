#!/usr/bin/env python3
"""Exact certificates for a PROPOSED nonlinear A_OS mathematical fixture.

No production potential evaluator, native run, new accepted claim or F2 change.
Polynomial/Bernstein arithmetic checks the bounds used in the companion proof.
"""
from fractions import Fraction as F
from math import comb
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import sys

ROOT = Path(__file__).resolve().parents[4]
INV = ROOT/'implementation/investigations/grc9v4-constitutive-design'


def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False).encode()


def sha(x):
    return hashlib.sha256(x).hexdigest()


def value(p,x):
    return sum((c*x**i for i,c in enumerate(p)),F())


def bernstein(p,a,b):
    """Exact power-to-Bernstein enclosure on the entire interval, not samples."""
    n = len(p)-1
    power = [sum((p[i]*comb(i,k)*a**(i-k)*(b-a)**k
                  for i in range(k,n+1)),F()) for k in range(n+1)]
    coefficients = [sum((power[k]*F(comb(i,k),comb(n,k))
                        for k in range(i+1)),F()) for i in range(n+1)]
    return dict(interval=[str(a),str(b)],coefficients=list(map(str,coefficients)),
                lower=str(min(coefficients)),upper=str(max(coefficients)))


def run():
    # Fixed resource levels are intrinsic to every site; no node-ID potential.
    roots = list(map(F,('1','5/4','3/2','9/4','3')))
    p = [F(1)]
    for r in roots:
        q = [F()]*(len(p)+1)
        for i,c in enumerate(p): q[i] -= r*c; q[i+1] += c
        p = q
    derivative = [i*p[i] for i in range(1,len(p))]
    for r in (F(1),F(3,2),F(3)):
        assert value(p,r) == 0 and value(derivative,r) > 0
    for r in (F(5,4),F(9,4)):
        assert value(p,r) == 0 and value(derivative,r) < 0
    h,eta,kappa = F(1,64),F(1,4),F(1,1024)
    outer = bernstein(derivative,F(31,32),F(33,32))
    child = bernstein(derivative,F(47,32),F(49,32))
    bo,bc = F(outer['lower']),F(child['lower'])
    upper = max(F(outer['upper']),F(child['upper']))
    mu = min(bo,bc)-4*kappa
    assert mu > 0

    # C*=(1-t,1-t,3/2+t,3/2+t), unique root in the stated local box.
    def equilibrium(t):
        r,x = 1-t,F(3,2)+t
        return value(p,x)-value(p,r)-2*kappa*(x-r)
    bracket = (F(0),F(1,256))
    endpoint = tuple(equilibrium(t) for t in bracket)
    assert endpoint[0] < 0 < endpoint[1]
    assert bo+bc-4*kappa > 0

    # Four-node target path, fixed order (a,c,v0,v1).
    B = [[1,0,0],[0,-1,0],[-1,0,1],[0,1,-1]]
    L = [[sum(B[i][e]*B[j][e] for e in range(3)) for j in range(4)] for i in range(4)]
    L2 = [[sum(L[i][k]*L[k][j] for k in range(4)) for j in range(4)] for i in range(4)]
    w = [[-L[j][i] for j in range(4)] for i in (2,3)]
    assert all(sum(v)==0 and sum(x*x for x in v)==6 for v in w)
    assert sum(x*y for x,y in zip(*w)) == -4
    assert all(sum(L2[i][j]*w[i-2][j] for j in range(4)) == -19 for i in (2,3))

    # Energy sublevel trapping. Every ensuing ordinary step stays in the same
    # box by the step-displacement bound, then energy descent closes induction.
    radius, boundary_distance = F(1,64),F(7,256)
    initial_excess = kappa*kappa/(2*mu)
    cap = mu*radius*radius/2
    assert initial_excess < cap
    assert (1+h*eta*4*upper)*radius < boundary_distance
    assert h*eta*4*upper < 2
    # One encounter at ANY unencountered age; two loads allowed simultaneously.
    # ||a*w0+b*w1|| <= sqrt(20)*epsilon < 5*epsilon.
    epsilon = F(1,4096)
    loaded_excess = initial_excess+upper*kappa/mu*5*epsilon+upper*10*epsilon**2
    assert kappa/mu+5*epsilon < boundary_distance
    assert loaded_excess < cap

    # Per-child delivered fraction, separately challenged (not co-use intake).
    # D_j is the average p' on the load segment, enclosed by the full box.
    response_lower = h*eta/2*(5*bc+bo-19*kappa)
    assert response_lower > 0
    neutral = bernstein(derivative,F(5,4)-2*epsilon,F(5,4)+epsilon)
    neutral_response_upper = h*eta/2*(6*F(neutral['upper'])-19*kappa)
    assert neutral_response_upper < 0
    neutral_slope_norm = max(abs(F(neutral['lower'])),abs(F(neutral['upper'])))
    neutral_update_bound = h*eta*4*(neutral_slope_norm+4*kappa)*2*epsilon
    assert F(5,4)-2*epsilon-neutral_update_bound > 0
    # lambda_2(L)=2-sqrt(2)>1/2; this rational lower bound suffices.
    energy_contraction = 1-h*eta*mu*(1-2*h*eta*upper)
    assert 0 < energy_contraction < 1

    # Unchanged production-independent F2 evaluator on the literal source read.
    rule_path = INV/'scripts/probe_atc_source_fission.py'
    spec = importlib.util.spec_from_file_location('support_fixture_f2',rule_path)
    rule = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rule)
    from pygrc.models.grc_v4_geometry import GRCV4Graph,OrientedEdge
    graph = GRCV4Graph(('a','b','c'),(OrientedEdge('ab','a','b'),OrientedEdge('bc','b','c')))
    source_j = (6*eta*kappa,-6*eta*kappa)
    choice = rule.source_prescription(graph,(1.,3.,1.),tuple(map(float,source_j)))
    assert choice['outcome']=='resolved' and choice['prescription']['shares']==['1/2','1/2']
    assert choice['prescription']['allocated_current']==['3/2','3/2']

    paths = {Path(__file__).resolve(),rule_path}
    for module in tuple(sys.modules.values()):
        name = getattr(module,'__file__',None)
        if name:
            path = Path(name).resolve()
            if path.is_relative_to(ROOT) and '/.venv/' not in str(path) and path.suffix=='.py': paths.add(path)
    record = dict(schema='grcv4_atc_support_fixture_certificate_v1',status='passed',
        scientific_status='proposed_mathematical_binding_not_native_or_accepted',
        arithmetic='exact rational polynomial and Bernstein coefficients',python=platform.python_version(),
        fixture_id='ATC-SUP-MW-AOS-v1',candidate_rule='ATC-CAN-F2-v1 unchanged',
        binding=dict(candidate='A',realization='OS',unit_measure=True,context='constant_zero',
            current_W='all_one_invariant',alpha='0',beta='0',gamma='0',chi_A='0',zeta_A='0',
            retained_carrier=None,H='identity',kappa_Ah='0',eta=str(eta),kappa_c=str(kappa),
            gauge='component zero mean: Phi=kappa_c*L*C-p(C)+mean(p(C))*ones',
            dt=str(h),charge='5',site_derivative_roots=list(map(str,roots)),
            site_derivative_coefficients_ascending=list(map(str,p)),
            site_potential='integral of the displayed p, identical at every vertex',
            equation='C_next=C-dt*eta*L*(p(C)-kappa_c*L*C)',
            state_domain='nonnegative fixed-charge C with positive all-one W; fixed graph per ordinary step',
            profile_binding='research equations only; no production complete-profile identity'),
        source=dict(C=['1','3','1'],J=list(map(str,source_j)),prescription=choice),
        target=dict(order=['a','c','v0','v1'],C=['1','1','3/2','3/2'],incidence=B,
            degree_bound=2,initial_J=[str(eta*kappa),str(-eta*kappa),'0']),
        slope_bounds=dict(outer=outer,child=child),
        equilibrium=dict(parameter='t',bracket=list(map(str,bracket)),endpoint_values=list(map(str,endpoint)),
            C_star=['1-t','1-t','3/2+t','3/2+t'],uniqueness='within the declared convex box'),
        energy=dict(form='sum V(C_i)-kappa_c*C^T*L*C/2',mu=str(mu),upper_hessian=str(upper),
            initial_excess_bound=str(initial_excess),trapping_cap=str(cap),
            radius=str(radius),boundary_distance_lower=str(boundary_distance),
            one_step_distance_factor=str(1+h*eta*4*upper),loaded_excess_bound=str(loaded_excess),
            contraction_factor_upper=str(energy_contraction)),
        encounter=dict(directions=w,amplitude_upper=str(epsilon),
            claim='any one unencountered age; independent signed simultaneous loads admitted and return',
            positive_individual_response_lower=str(response_lower),
            horizon='one-update response and analytical return tail; 16-update native observation is proposed, not executed',
            repeated_load_schedule='not certified'),
        neutral_control=dict(C=['5/4']*4,same_graph_charge_W_law=True,
            slope_bounds=neutral,positive_load_response_upper=str(neutral_response_upper),
            one_update_resource_change_bound=str(neutral_update_bound),
            interpretation='analytical formation-neutral preparation, not an erased native history'),
        not_established=['native_potential_implementation','new_basin_creation','split_necessity',
            'two_independent_identities','sibling_removal_autonomy','all_ten_domains','F2_acceptance'],
        production_changes=False,native_admissions=0,native_steps=0,native_events=0,
        source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p.read_bytes()))
            for p in sorted(paths)])
    record['record_digest'] = sha(canonical(record))
    return record


if __name__ == '__main__':
    print(json.dumps(run(),separators=(',',':'),ensure_ascii=True,allow_nan=False))

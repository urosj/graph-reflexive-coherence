#!/usr/bin/env python3
"""Bounded A current-squared history feedback: exact proof bounds and staging.

No production backend, registered potential, trajectory campaign or event.
The Decimal checks are finite research diagnostics, not certified binary64
execution; all invariant/return/response bounds are rational inequalities.
"""
from decimal import Decimal as D, localcontext
from fractions import Fraction as F
import hashlib
import json
from math import comb
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
INV = ROOT / 'implementation/investigations/grc9v4-constitutive-design'
REFS = INV / 'evidence/autonomous-topology-change'


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=True, allow_nan=False).encode()


def sha(value):
    return hashlib.sha256(value).hexdigest()


def mv(a, v):
    return tuple(sum(x*y for x, y in zip(row, v, strict=True)) for row in a)


def mm(a, b):
    return tuple(tuple(sum(x*y for x, y in zip(row, col, strict=True))
                       for col in zip(*b)) for row in a)


def bernstein(coeff, lo, hi):
    n = len(coeff)-1
    power = [sum((coeff[k]*comb(k, j)*lo**(k-j)*(hi-lo)**j
                  for k in range(j, n+1)), F()) for j in range(n+1)]
    return tuple(sum((power[j]*F(comb(i, j), comb(n, j))
                      for j in range(i+1)), F()) for i in range(n+1))


def run():
    old_path = REFS / 'ATCSupportFixtureCertificate.json'
    old = json.loads(old_path.read_text())
    assert old['record_digest'] == 'f0414b6fa38dbe9c57e265530d96580f12d1f58b9bdb927ee06c8e1f167d4d37'
    assert old['record_digest'] == sha(canonical({k: v for k, v in old.items() if k != 'record_digest'}))
    coeff = tuple(map(F, old['binding']['site_derivative_coefficients_ascending']))
    derivative = tuple(i*coeff[i] for i in range(1, len(coeff)))
    for bounds in old['slope_bounds'].values():
        lo, hi = map(F, bounds['interval'])
        assert bernstein(derivative, lo, hi) == tuple(map(F, bounds['coefficients']))
    p = lambda c: sum((a*c**i for i, a in enumerate(coeff)), F())
    kappa, eta, h = F(1, 1024), F(1, 4), F(1, 64)
    g = lambda t: p(F(3, 2)+t)-p(1-t)-2*kappa*(F(1, 2)+2*t)
    tmax = F(1, 256)
    assert g(F()) == F(-1, 1024) and g(tmax) > 0
    mo = F(old['slope_bounds']['outer']['lower'])
    mc = F(old['slope_bounds']['child']['lower'])
    M = F(old['energy']['upper_hessian'])
    mu = min(mo, mc)-4*kappa
    assert mu == F(old['energy']['mu']) > 0 and mo+mc-4*kappa > 0

    B = tuple(tuple(map(F, row)) for row in old['target']['incidence'])
    BT = tuple(zip(*B))
    A = mm(BT, B)
    assert A == ((F(2), F(0), F(-1)), (F(0), F(2), F(-1)), (F(-1), F(-1), F(2)))
    # A has eigenvalues 2, 2+-sqrt(2); 1/2 < lambda_min and lambda_max < 4.
    assert F(3, 2)**2 > 2
    assert h*eta*4*M < 1
    R, bbar, weight = F(1, 128), F(1, 128), F(1, 1024)
    rho, gamma_max, epsilon = F(1, 2), F(256), F(1, 4096)
    T = F(3, 2)*(F(1, 2)+2*tmax)
    assert T == F(195, 256)
    assert 2*R < F(old['energy']['boundary_distance_lower'])
    resource_lower = 1-tmax-2*R
    assert resource_lower == F(251, 256) > 0
    assert 1-bbar > F(1, 2)  # exp(-bbar) >= 1-bbar > W_floor.

    A0 = 4*M+16*kappa
    Aj = 4*M+16*kappa*bbar
    Dw = 4*kappa*T
    qx = 1-h*eta*(mu/2-A0*bbar)
    coupling = h*eta*Dw
    jmax = eta*(Aj*R+Dw*bbar)
    drive_upper = gamma_max*jmax*jmax/2
    c = (1-rho)*gamma_max*eta*eta/2*(Aj*R+Dw*bbar)
    q_resource = qx+weight*c*Aj
    q_history = coupling/weight+rho+c*Dw
    q = max(q_resource, q_history)
    x_margin = R-qx*R-coupling*bbar
    y_margin = bbar-drive_upper
    assert 0 < qx < 1 and 0 < q < 1
    assert x_margin > 0 and y_margin > 0

    loads_edge = (tuple(-row[2] for row in BT), tuple(-row[3] for row in BT))
    gram = mm(loads_edge, tuple(zip(*loads_edge)))
    assert gram == ((F(2), F(-1)), (F(-1), F(2)))
    load_norm_bound = F(5, 2)*epsilon  # sqrt(6) < 5/2.
    assert F(5, 2)**2 > 6
    reference_J = eta*kappa
    init_a = gamma_max*reference_J**2/2
    source_reference_J = 3*eta*kappa*(3-1)
    source_log_bound = gamma_max*source_reference_J**2/2
    source_inflow_lower = source_reference_J*(1-source_log_bound)**2
    assert source_reference_J == F(3, 2048) and source_log_bound < bbar
    assert source_inflow_lower > 0 and F(3, 2)-1 == F(1, 2)
    initial_S = F(3, 2)*tmax+weight*init_a  # sqrt(2)*t < 3*tmax/2.
    assert initial_S+load_norm_bound < R
    response_original = F(old['encounter']['positive_individual_response_lower'])
    response_loss = h*eta*5*bbar*(M+8*kappa)
    response_lower = response_original-response_loss
    assert response_lower == F(43636135, 34359738368) > 0

    # A larger gamma fails THIS sufficient bound, not necessarily the dynamics.
    q_512 = max(qx+weight*(2*c)*Aj, coupling/weight+rho+(2*c)*Dw)
    assert q_512 > 1
    # Exact nonannihilation lower bounds for the reference-pass prepared case.
    writer_log_gap_lower = init_a*(1-4*init_a)/2
    next_weight_gap_lower = (1-init_a/2)*init_a*(1-4*init_a)/4
    next_read_bracket_lower = 2*kappa*(1-init_a)-2*M*h*reference_J
    next_current_gap_lower = eta*next_weight_gap_lower*next_read_bracket_lower
    assert min(writer_log_gap_lower, next_weight_gap_lower, next_read_bracket_lower,
               next_current_gap_lower) > 0

    # Four finite staged-map evaluations: two matched gamma-on/off pairs.
    # Dense expanded-polynomial evaluation is checked against independent
    # symmetric closed forms. No output is passed off as native execution.
    examples = []
    with localcontext() as ctx:
        ctx.prec = 80
        dec = lambda f: D(F(f).numerator)/D(F(f).denominator)
        db, dbt = tuple(tuple(map(dec, row)) for row in B), tuple(tuple(map(dec, row)) for row in BT)
        de, dk, dh = dec(eta), dec(kappa), dec(h)
        dc = tuple(map(dec, coeff))
        roots = tuple(map(dec, (F(1), F(5, 4), F(3, 2), F(9, 4), F(3))))
        tol = D('1e-70')

        def factored_p(value):
            product = D(1)
            for root in roots:
                product *= value-root
            return product

        def read(C, y, frozen_stiffness=False):
            w = tuple(v.exp() for v in y)
            edge_C = mv(dbt, C)
            stiff = mv(db, edge_C if frozen_stiffness else tuple(v*z for v, z in zip(w, edge_C)))
            grad = tuple(sum(a*c**i for i, a in enumerate(dc))-dk*l for c, l in zip(C, stiff))
            return tuple(de*v*z for v, z in zip(w, mv(dbt, grad)))

        def step(C, y, gamma):
            J = read(C, y)
            Cnext = tuple(c-dh*v for c, v in zip(C, mv(db, J)))
            drive = tuple(-dec(gamma)*v*v/2 for v in J)
            assert min(drive) >= -dec(bbar) > -D(2).ln()
            ynext = tuple((v+z)/2 for v, z in zip(y, drive))
            return Cnext, ynext, J

        C0 = (D(1), D(1), D('1.5'), D('1.5'))
        a = dec(init_a)
        for label, old_log in (('supplied_neutral_history_control', D(0)),
                               ('reference_pass_prepared_target', -a)):
            y0 = (old_log, old_log, D(0))
            Cnext, yon, J = step(C0, y0, gamma_max)
            Ccontrol, yoff, Jcontrol = step(C0, y0, 0)
            assert Cnext == Ccontrol and J == Jcontrol
            j = dec(reference_J)*(2*old_log).exp()
            u = dh*j
            expected_C = (1-u, 1-u, D('1.5')+u, D('1.5')+u)
            expected_y = (old_log-a*(4*old_log).exp())/2
            assert max(abs(x-z) for x, z in zip(Cnext, expected_C)) < tol
            assert abs(yon[0]-expected_y) < tol and abs(yon[1]-expected_y) < tol
            assert yon[2] == yoff[2] == 0
            assert yoff[0]-yon[0] > 0 and min(Cnext) > 0
            next_on, next_off = read(Cnext, yon), read(Cnext, yoff)
            delta_p = factored_p(D('1.5')+u)-factored_p(1-u)
            for ynext, next_J in ((yon, next_on), (yoff, next_off)):
                wnext = ynext[0].exp()
                scalar_J = de*wnext*(2*dk*wnext*(D('0.5')+2*u)-delta_p)
                assert max(abs(x-z) for x, z in zip(next_J, (scalar_J, -scalar_J, D(0)))) < tol
            assert next_off[0]-next_on[0] > dec(next_current_gap_lower)
            assert read(C0, yon) != J  # New W would change the old beat: forbidden staging.
            wrong_J = read(Cnext, y0)
            wrong_y = tuple((v-dec(gamma_max)*j*j/2)/2 for v, j in zip(y0, wrong_J))
            assert wrong_y != yon  # The writer must use the selected, not next, current.
            if old_log != 0:
                assert read(C0, y0, frozen_stiffness=True) != J
                assert old_log < yon[0] < yoff[0]  # Release can still have a causal forming contribution.
            else:
                assert yon[0] < 0 == yoff[0]
            examples.append(dict(label=label, C=list(map(str, C0)), old_log_W=list(map(str, y0)),
                selected_J=list(map(str, J)), C_next=list(map(str, Cnext)),
                log_W_next_gamma_on=list(map(str, yon)), log_W_next_gamma_off=list(map(str, yoff)),
                next_J_gamma_on=list(map(str, next_on)), next_J_gamma_off=list(map(str, next_off)),
                same_current_and_resource_update_before_writer=True,
                next_current_matches_factored_scalar_oracle=True,
                wrong_next_current_writer_discriminated=True, premature_new_W_read_discriminated=True))

    # Typed forensic queries retain their exact authority ceilings.
    side = INV / 'tools/exploratory-side-tool'
    sys.path.insert(0, str(side/'tool/src'))
    from grcv4_explorer.a_initializer import load_current_forensic_context
    from grcv4_explorer.forensic import contract_provenance
    context = load_current_forensic_context(ROOT, side)
    keys = ('D10.2-EC-PARENT-A-GW-FUNCTIONAL', 'D10.2-EC-PARENT-A-WRITER-TARGET',
            'D10.2-EC-PARENT-A-RETAINED-WRITER', 'P9-EC-A-INITIALIZER-REFERENCE-PASS')
    traces = [contract_provenance(context, key) for key in keys]
    assert all(t['rows'][0]['payload']['support_disposition'] == 'indeterminate_requires_review'
               for t in traces[:3])
    assert traces[3]['rows'][0]['payload']['support_disposition'] == ['required']

    paths = {Path(__file__).resolve(), old_path, ROOT/'specs/grc-v4-spec.md',
        INV/'drafts/2026-09-GRC-V4.md', ROOT/'src/pygrc/models/grc_v4_candidate_a.py',
        side/'tool/src/grcv4_explorer/forensic.py', side/'tool/src/grcv4_explorer/a_initializer.py'}
    paths.update(ROOT/row['source_ref']['path'] for t in traces for row in t['rows'])
    record = dict(schema='grcv4_atc_a_history_feedback_certificate_v1',
        status='passed_exact_sufficient_bounds_and_finite_staging_checks',
        scientific_status='proposed_coupled_mathematics_pending_independent_review',
        research_contract='ATC-A-CURRENT-SQUARED-HISTORY-v1_not_runtime_registered',
        predecessor_digest=old['record_digest'],
        scope=dict(candidate='A', realization='OS reduced zero-geometry-source slice',
            active_channel='gamma*selected_current_squared in the retained logarithmic writer',
            alpha='0', beta='0', chi_A='0', zeta_A='0', kappa_Ah='0', carrier=None,
            p_coefficients=list(map(str, coeff)), kappa=str(kappa), eta=str(eta), h=str(h),
            tau_A='h/log(2) in exact mathematics', rho=str(rho), gamma_interval=['0', str(gamma_max)],
            W_floor='1/2', incidence=B, independent_state='C and log(W), with W in (0,1]',
            native_potential_and_initializer_still_unadmitted=True, old_binding_unchanged=True),
        equilibrium=dict(C='(1-t,1-t,3/2+t,3/2+t)', t_bracket=['0','1/256'],
            W='all ones', J='zero', complete_state_returns=True,
            linearization='upper triangular in (edge-charge displacement,log W); gamma forcing is quadratic at J=0'),
        bounds=dict(mu=str(mu), M=str(M), edge_radius=str(R), log_radius=str(bbar),
            auxiliary_history_weight=str(weight), equilibrium_edge_contrast_bound=str(T),
            resource_lower=str(resource_lower), mobility_lower='exp(-1/128)>127/128',
            A0=str(A0), Aj=str(Aj), Dw=str(Dw), qx=str(qx), coupling=str(coupling),
            current_norm_upper=str(jmax), writer_drive_log_magnitude_upper=str(drive_upper),
            writer_linearization_bound_c=str(c), q_resource=str(q_resource), q_history=str(q_history),
            coupled_contraction_upper=str(q), resource_invariance_margin=str(x_margin),
            history_invariance_margin=str(y_margin), initial_S_upper=str(initial_S),
            one_encounter_edge_norm_upper=str(load_norm_bound), loaded_S_upper=str(initial_S+load_norm_bound),
            individual_response_loss_upper=str(response_loss), individual_Q_lower=str(response_lower)),
        activation=dict(gamma=str(gamma_max), target_reference_current=str(reference_J),
            reference_pass_log_magnitude=str(init_a), writer_log_gap_lower=str(writer_log_gap_lower),
            next_weight_gap_lower=str(next_weight_gap_lower), next_read_bracket_lower=str(next_read_bracket_lower),
            next_current_gap_lower=str(next_current_gap_lower),
            control='matched gamma-off law from the identical incoming C,W, not a reinitialized control'),
        source_preparation=dict(reference_inflow=str(source_reference_J),
            initialized_log_magnitude_upper=str(source_log_bound), actual_inflow_lower=str(source_inflow_lower),
            shares=['1/2', '1/2'], funding_margin='1/2',
            scope='formula-level mathematical preparation, not native construction or history transport'),
        beyond_bound_control=dict(gamma='512', q_bound=str(q_512),
            disposition='not_certified_by_this_sufficient_bound_not_a_proof_of_instability'),
        decimal_diagnostics=dict(precision=80, not_a_certified_rounding_enclosure=True, examples=examples),
        authority_traces=traces,
        claim_ceiling=['one fixed degree-two target and retained-mobility channel',
            'exact-arithmetic joint return after one bounded encounter at any unencountered age',
            'not arbitrary repeated loads, gamma<0, W>1, other tau, or all feedback channels',
            'no native potential/initializer admission, event, all-family closure or independent identities'],
        counts=dict(finite_research_step_evaluations=4, next_read_comparisons=2,
            trajectory_campaigns=0, native_steps=0, topology_events=0),
        production_changes=False,
        source_bindings=[dict(path=p.relative_to(ROOT).as_posix(), sha256=sha(p.read_bytes())) for p in sorted(paths)])
    # Rational matrix entries must have a portable JSON representation.
    record['scope']['incidence'] = [list(map(str, row)) for row in B]
    record['record_digest'] = sha(canonical(record))
    return record


if __name__ == '__main__':
    print(json.dumps(run(), sort_keys=True, separators=(',', ':'), allow_nan=False))

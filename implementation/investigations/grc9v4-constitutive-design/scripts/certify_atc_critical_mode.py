#!/usr/bin/env python3
"""Bounded source critical-mode and selected-refinement mathematics.

Stdout only. No native run, automatic event, authority change or target search.
Reviewed predecessor identities are checked, not rewritten or rerun.
"""
from decimal import Decimal as D, localcontext
from fractions import Fraction as F
import json
from pathlib import Path
import sys

from certify_atc_os_geometry_feedback import canonical, mv, sha, solve, stringify

ROOT = Path(__file__).resolve().parents[4]
INV = ROOT / 'implementation/investigations/grc9v4-constitutive-design'
REFS = INV / 'evidence/autonomous-topology-change'
EDGES = tuple((i, 4) for i in range(4)) + tuple(
    (i, j) for i in (0, 1) for j in (2, 3) for _ in range(2))
TARGET_EDGES = tuple((i, 4 if i < 2 else 5) for i in range(4)) + EDGES[4:] + ((4, 5),)
PHI = (1, 1, -1, -1, 0)
MODES = ((1, 1, 1, 1, 1), (-1, -1, -1, -1, 4),
         (1, -1, 0, 0, 0), (0, 0, 1, -1, 0), PHI)
EIGS = (0, 5, 5, 5, 9)


def incidence(n, edges):
    return tuple(tuple(int(i == u)-int(i == v) for u, v in edges) for i in range(n))


BS, BT = incidence(5, EDGES), incidence(6, TARGET_EDGES)


def lap(B, weights):
    return tuple(tuple(sum(bi*w*bj for bi, bj, w in zip(ri, rj, weights, strict=True))
                       for rj in B) for ri in B)


def dec(value):
    f = F(value)
    return D(f.numerator)/D(f.denominator)


def signatures(B, phi):
    edge = mv(tuple(zip(*B)), phi)
    return tuple(tuple(b*e for b, e in zip(row, edge) if b) for row in B)


def exact_checks():
    # Predecessor inequality, summed instead of rerunning its trajectories.
    cstar = F(5015, 21888)
    time_bound = 5/(20*cstar)
    assert time_bound == F(5472, 5015)
    L = lap(BS, (F(1),)*12)
    for v, eigenvalue in zip(MODES, EIGS):
        assert mv(L, v) == tuple(eigenvalue*x for x in v)
    for i, v in enumerate(MODES):
        assert sum(x*x for x in v) > 0
        for z in MODES[:i]:
            assert sum(x*y for x, y in zip(v, z)) == 0
    sig = signatures(BS, PHI)
    assert [i for i, s in enumerate(sig) if min(s) < 0 < max(s)] == [4]
    assert sig[4] == (-1, -1, 1, 1)
    # Exact edge-orientation and vertex/edge-order covariance.
    vp, ep = (4, 2, 0, 3, 1), tuple(reversed(range(12)))
    signs = tuple((-1)**i for i in range(12))
    moved = tuple(tuple(BS[i][j]*s for j, s in zip(ep, signs)) for i in vp)
    image = signatures(moved, tuple(PHI[i] for i in vp))
    for i, row in enumerate(moved):
        expected = tuple(BS[vp[i]][j]*mv(tuple(zip(*BS)), PHI)[j] for j in ep if BS[vp[i]][j])
        assert image[i] == expected
    assert signatures(BS, tuple(-x for x in PHI))[4] == (1, 1, -1, -1)

    a, h, w0 = F(15, 2), F(1, 32), F(3, 4)
    assert F(6, 7)**2 < w0 and F(5, 6)**2 < w0
    assert 1+h*9*w0*(9*w0-a) == F(431, 512)
    assert 1+h*5*w0*(5*w0-a) == F(287, 512)
    assert 9*F(6, 7)*(9*F(6, 7)-a) == F(81, 49)
    # Exact odd-sector identity at three distinct weights (quadratic generator).
    p, q = (1, 1, -1, -1, 0, 0), (0, 0, 0, 0, 1, -1)
    target_rows = []
    for w in (F(6, 7), F(5, 6), F(1)):
        Lt = lap(BT, (w,)*12+(F(1),))
        assert mv(Lt, p) == tuple(9*w*x-2*w*y for x, y in zip(p, q))
        assert mv(Lt, q) == tuple(-w*x+(2*w+2)*y for x, y in zip(p, q))
        odd = ((9*w, -w), (-2*w, 2*w+2))
        characteristic_at_source = (odd[0][0]-9*w)*(odd[1][1]-9*w)-odd[0][1]*odd[1][0]
        assert characteristic_at_source == -2*w*w < 0
        aa, bb, dd = 83*w*w-F(135, 2)*w, w*(11*w-F(11, 2)), 6*w*w-7*w-11
        for vector, coordinates in ((p, (1, 0)), (tuple(-x for x in q), (0, 1))):
            actual = mv(Lt, tuple(x-a*y for x, y in zip(mv(Lt, vector), vector)))
            z, t = coordinates
            expected = tuple((aa*z+bb*t)*x-(2*bb*z+dd*t)*y for x, y in zip(p, q))
            assert actual == expected
        target_rows.append(dict(w=w, odd_laplacian=odd,
                                sign_rectified_generator=((aa, bb), (2*bb, dd))))
    w = F(6, 7)
    assert 83*w*w-F(135, 2)*w == F(153, 49)
    assert w*(11*w-F(11, 2)) == F(165, 49)
    assert 6*w*w-7*w-11 == F(-617, 49)
    # Derivatives of all three entries are positive throughout [6/7,1].
    assert 166*w-F(135, 2) > 0 and 22*w-F(11, 2) > 0 and 12*w-7 > 0
    assert 1-h*F(617, 49) > 0
    parent_C = F(5)
    original_energy = a*parent_C**2/2
    conserved_measure_energy = 2*(a*(parent_C/2)**2/(2*F(1, 2)))
    unit_site_energy = 2*(a*(parent_C/2)**2/2)
    assert conserved_measure_energy == original_energy == 2*unit_site_energy
    return dict(adaptive_predecessor_time_upper=time_bound, source_incidence=BS,
        source_laplacian=L, eigenbasis=MODES, eigenvalues=EIGS,
        source_contact_signatures=sig, unique_mixed_sign_parent=4,
        covariance=dict(vertex_order=vp, edge_order=ep, orientation_signs=signs,
                        parent_signature_after_change=image[0]),
        critical_mobility=F(5, 6), source_multiplier_lower_after_crossing=1+h*F(81, 49),
        target_incidence=BT, target_odd_sector_checks=target_rows,
        target_positive_cone_multiplier_lower=1+h*F(153, 49),
        target_lower_diagonal_multiplier=1-h*F(617, 49),
        measure_example=dict(parent_amount=parent_C, parent_measure=1,
            child_amounts=(parent_C/2,)*2, conserved_child_measures=(F(1, 2),)*2,
            original_local_energy=original_energy, conserved_measure_energy=conserved_measure_energy,
            unit_site_energy=unit_site_energy, extensive_constant_difference=0,
            no_measure_transport_authority_inferred=True))


def diagnostics():
    with localcontext() as context:
        context.prec = 96
        a, h, R, gamma = D(15)/2, D(1)/32, D(9)/5, D(1)/65536
        tol, epsilon = D('1e-75'), D('1e-12')
        counts = dict(full_background_and_derivative_reads=0, full_continuation_reads=0,
            source_positive_updates=0, target_positive_updates=0,
            source_rejected_proposals=0, target_rejected_proposals=0,
            retained_writer_updates=0, native_steps=0, topology_events=0)

        def read(B, C, y, g, chi):
            n = len(y); w = tuple(v.exp() for v in y)
            eye = tuple(tuple(D(i == j) for j in range(n)) for i in range(n))
            dC = mv(tuple(zip(*B)), C)

            def star(flat):
                return tuple(tuple(sum(D(bool(row[i] and row[j])) for row in B)*flat[i]*flat[j]/2
                                   for j in range(n)) for i in range(n))

            def stage(H):
                Lc = mv(B, tuple(x*z for x, z in zip(w, dC)))
                delta = tuple(tuple(x-y for x, y in zip(row, ref)) for row, ref in zip(H, eye))
                geometrical = mv(B, mv(delta, dC))  # kappa_Ah=1
                potential = tuple(x-a*c+z for x, c, z in zip(Lc, C, geometrical))
                v = tuple(-x*z for x, z in zip(w, mv(tuple(zip(*B)), potential)))
                hat = tuple((-g*z*z/2).exp() for z in v)
                assert min(hat) > D('0.5')
                q = tuple((x-z)/(x+z) for x, z in zip(w, hat))
                J = tuple(x/(1-chi*z) for x, z in zip(v, q))
                flat = solve(H, tuple(chi*z*j for z, j in zip(q, J)))
                return J, flat

            J0, flat0 = stage(eye)
            S = star(flat0)
            H = tuple(tuple(x+y for x, y in zip(row, other)) for row, other in zip(eye, S))
            J, flat = stage(H)
            next_C = tuple(c-h*j for c, j in zip(C, mv(B, J)))
            residual = sum((x-y)**2 for row, other in zip(S, star(flat)) for x, y in zip(row, other))
            return dict(C=C, log_W=y, current=J, proposed_C=next_C, residual_squared=residual,
                        predictor_current=J0)

        def writer(y, J, g):
            return tuple(old/2-g*j*j/4 for old, j in zip(y, J))

        derivative_rows = []
        for w in (D(3)/4, D(5)/6, (D(3)/4).sqrt()):
            y = (w.ln(),)*12
            base = read(BS, (R,)*5, y, gamma, D(1)/2)
            counts['full_background_and_derivative_reads'] += 1
            assert base['current'] == (D(0),)*12 and base['proposed_C'] == (R,)*5
            q = (w-1)/(w+1)
            for phi, eig in zip(MODES[1:], EIGS[1:]):
                plus = read(BS, tuple(R+epsilon*x for x in phi), y, gamma, D(1)/2)
                minus = read(BS, tuple(R-epsilon*x for x in phi), y, gamma, D(1)/2)
                counts['full_background_and_derivative_reads'] += 2
                m = 1+h*w*eig*(w*eig-a)/(1-q/2)
                fd = tuple((x-z)/(2*epsilon) for x, z in zip(plus['proposed_C'], minus['proposed_C']))
                error = max(abs(x-m*z) for x, z in zip(fd, phi))
                history_error = max(abs(x-z)/(2*epsilon) for x, z in zip(
                    writer(y, plus['current'], gamma), writer(y, minus['current'], gamma)))
                assert error < D('1e-20') and history_error < D('1e-70')
                assert plus['residual_squared'] < D(1)/512**2
                derivative_rows.append(dict(w=w, eigenvalue=eig, eigenvector=phi,
                    expected_step_multiplier=m, centered_difference_error=error,
                    history_cross_derivative_error=history_error))
        y = ((D(3)/4).ln(),)*12
        yp = tuple(v+epsilon*(i == 0) for i, v in enumerate(y))
        ym = tuple(v-epsilon*(i == 0) for i, v in enumerate(y))
        hp, hm = read(BS, (R,)*5, yp, gamma, D(1)/2), read(BS, (R,)*5, ym, gamma, D(1)/2)
        counts['full_background_and_derivative_reads'] += 2
        assert hp['current'] == hm['current'] == (D(0),)*12
        history_fd = tuple((x-z)/(2*epsilon) for x, z in zip(writer(yp, hp['current'], gamma), writer(ym, hm['current'], gamma)))
        assert max(abs(x-D(i == 0)/2) for i, x in enumerate(history_fd)) < tol

        trajectories = {}
        first_successor = None
        for name, B in (('source', BS), ('selected_target', BT)):
            if name == 'source':
                C = tuple(R+D(v)/16 for v in PHI); y = ((D(3)/4).ln(),)*12
            else:
                C0, y0 = first_successor
                C = C0[:4]+(C0[4]/2,)*2; y = y0+(D(0),)
                assert abs(sum(C)-9) < tol
            rows = []
            for attempt in range(1, 129):
                counts['full_continuation_reads'] += 1
                row = read(B, C, y, D(0), D(0))
                w = y[0].exp(); next_C = row['proposed_C']
                if name == 'source':
                    amplitude = (C[0]-C[2])/2
                    expected_amplitude = (1+h*9*w*(9*w-a))*amplitude
                    assert max(abs(c-R-amplitude*v) for c, v in zip(C, PHI)) < tol
                    expected = tuple(R+expected_amplitude*v for v in PHI)
                    row['independent_modal_next_C'] = expected
                    assert max(abs(c-z) for c, z in zip(next_C, expected)) < tol
                else:
                    z, t = (C[0]-C[2])/2, -(C[4]-C[5])/2
                    aa, bb, dd = 83*w*w-D(135)/2*w, w*(11*w-D(11)/2), 6*w*w-7*w-11
                    expected_z = (1+h*aa)*z+h*bb*t
                    expected_t = 2*h*bb*z+(1+h*dd)*t
                    assert abs((next_C[0]-next_C[2])/2-expected_z) < tol
                    assert abs(-(next_C[4]-next_C[5])/2-expected_t) < tol
                    assert z > 0 and t >= -tol and expected_z >= dec(F(1721, 1568))*z-tol
                    row['independent_odd_next_coordinates'] = (expected_z, expected_t)
                assert abs(sum(next_C)-9) < tol and row['residual_squared'] == 0
                row['attempt'] = attempt
                key = 'source' if name == 'source' else 'target'
                if min(next_C) <= 0:
                    row.update(disposition='resource_domain_exit_no_update', retained_writer_executed=False)
                    counts[key+'_rejected_proposals'] += 1
                    rows.append(row)
                    break
                new_y = writer(y, row['current'], D(0))
                row.update(disposition='positive_mathematical_update', retained_writer_executed=True,
                           retained_C_after=next_C, retained_log_W_after=new_y)
                counts[key+'_positive_updates'] += 1
                counts['retained_writer_updates'] += 1
                C, y = next_C, new_y
                if name == 'source' and attempt == 1:
                    first_successor = (C, y)
                rows.append(row)
            assert rows[-1]['disposition'] == 'resource_domain_exit_no_update'
            trajectories[name] = rows
        assert counts['full_background_and_derivative_reads'] == 29
        assert counts['source_positive_updates'] == 12
        return stringify(dict(precision=96, interval_certified=False, counts=counts,
            enabled_background_derivative_checks=derivative_rows,
            history_direction_derivative=history_fd, trajectories=trajectories,
            target_map_timed_at_first_successful_source_commit=True,
            targets_searched=0, selected_target_maps_evaluated=1,
            no_rejected_state_committed=True, no_event_executed=True))


def run():
    prior_path = REFS/'ATCUnsplitViabilityCertificate.json'
    prior = json.loads(prior_path.read_text())
    expected = '1351c25a8765f2eb41f09b63e976127342c15cd35246057e6ee26ad6e759f2d5'
    assert prior['record_digest'] == expected == sha(canonical({k:v for k,v in prior.items() if k != 'record_digest'}))
    for binding in prior['source_bindings']:
        assert sha((ROOT/binding['path']).read_bytes()) == binding['sha256'], binding['path']
    bounds = exact_checks()
    finite = diagnostics()
    side = INV/'tools/exploratory-side-tool'
    sys.path.insert(0, str(side/'tool/src'))
    from grcv4_explorer.a_initializer import load_current_forensic_context
    from grcv4_explorer.forensic import contract_provenance
    ctx = load_current_forensic_context(ROOT, side)
    inherited = []
    for ref in prior['authority_trace_refs']:
        old = json.loads((ROOT/ref['record_path']).read_text())
        assert old['record_digest'] == ref['record_digest'] == sha(canonical({k:v for k,v in old.items() if k != 'record_digest'}))
        value = old
        for part in ref['json_pointer'].strip('/').split('/'):
            value = value[int(part)] if isinstance(value, list) else value[part]
        assert canonical(contract_provenance(ctx, ref['query']['contract_id'])) == canonical(value)
        inherited.append(ref)
    for i, trace in enumerate(prior['authority_traces']):
        assert canonical(contract_provenance(ctx, trace['query']['contract_id'])) == canonical(trace)
        inherited.append(dict(record_path=prior_path.relative_to(ROOT).as_posix(), record_digest=expected,
                              json_pointer=f'/authority_traces/{i}', query=trace['query']))
    ids = ('D10.2-EC-PARENT-CORE-UNIT-MEASURE', 'D10.2-EC-PARENT-CORE-GENERAL-CHARGE',
           'D10.2-EC-GEOM-HODGE-UPDATE', 'D10.2-EC-PARENT-CORE-EXTERNAL-EVENT-CHARGE')
    traces = [contract_provenance(ctx, id_) for id_ in ids]
    paths = {ROOT/b['path'] for b in prior['source_bindings']}
    paths.update((prior_path, Path(__file__).resolve(), ROOT/'specs/grc-v4-spec.md',
                  INV/'drafts/2026-09-GRC-V4.md', ROOT/'src/pygrc/models/grc_v4_geometry.py'))
    record = stringify(dict(schema='grcv4_atc_critical_mode_certificate_v1',
        status='passed_exact_checks_and_focused_diagnostics',
        scientific_status='proposed_conditional_mathematics_pending_independent_review',
        predecessor=dict(path=prior_path.relative_to(ROOT).as_posix(), record_digest=expected,
            review='mathematical PASS; independent bounds/energy/modes/scalar trajectory, not end-to-end checker'),
        exact_checks=bounds, decimal_diagnostics=finite,
        scope=dict(candidate='A', realization='one-pass OS', p='15*C/2',
            h='1/32', tau_A='h/log(2)', alpha=0, beta=0, eta=1, kappa_c=1, zeta_A=1,
            carrier=None, W_reference='all one', H0='identity', K4_adapter='identity normalized common star',
            source_edges=EDGES, target_edges=TARGET_EDGES,
            finite_trajectory_gamma=0, finite_trajectory_chi_A=0, kappa_H=1, kappa_Ah=1,
            enabled_derivative_domain='homogeneous C=9/5 with uniform W in [3/4,1], gamma<=2^-16, chi_A<=1/2',
            initial_source_C=['149/80','149/80','139/80','139/80','9/5'],
            initial_source_W='3/4', target_map='first source successor; halve parent; old W retained; bridge W=1',
            no_native_profile_admission=True, no_K0_consumer_or_schedule_change=True),
        authority_trace_refs=inherited, measure_authority_traces=traces,
        claim_ceiling=['predecessor obstruction extends to non-Zeno positive adaptive schedules',
            'new source ordinary history recovery crosses one simple contact-resolving mode',
            'finite-amplitude obstruction and selected-target counterexample proved in zero-read control',
            'enabled feedback result is homogeneous step linearization only',
            'sign rectification is orientation invariant; raw oriented signs would be invalid',
            'unit-site split counterexample is not a measure-conservative subdivision theorem',
            'not autonomous fission, accepted spectral guard or restoration of continuation'],
        source_bindings=[dict(path=p.relative_to(ROOT).as_posix(), sha256=sha(p.read_bytes())) for p in sorted(paths)],
        production_changes=False))
    record['record_digest'] = sha(canonical(record))
    return record


if __name__ == '__main__':
    print(json.dumps(run(), sort_keys=True, separators=(',', ':'), allow_nan=False))

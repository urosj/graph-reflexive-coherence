#!/usr/bin/env python3
"""Focused CAN-LSF lift: exact conditional bounds + finite Decimal diagnostics.

Research only. No production execution, graph admission or target search.
The declared point/box and stopping criteria are in the pinned proposal.
Stdout is the record; this script never writes files or refreshes old evidence.
"""
from decimal import Decimal as D, localcontext
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path

from certify_atc_os_geometry_feedback import mv, solve

ROOT = Path(__file__).resolve().parents[4]
INV = Path('implementation/investigations/grc9v4-constitutive-design')
REFS = INV / 'evidence/autonomous-topology-change'
SOURCE = ((0, 4), (1, 4), (2, 4), (3, 4))
TARGET = ((0, 4), (1, 4), (2, 5), (3, 5), (4, 5))


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def serial(value):
    if isinstance(value, (D, F)):
        return str(value)
    if isinstance(value, dict):
        return {k: serial(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(v) for v in value]
    return value


def target_bounds():
    a, h, radius, log_radius = F(19, 4), F(1, 8), F(2, 3), F(1, 8)
    c, g, qcap, A, L, N = F(1, 16), F(1, 1024), F(1, 15), F(4), F(73, 16), F(5, 2)
    low = (1-log_radius)*F(7, 16)
    q0 = 1-h*min(low*(a-low), L*(a-L))
    assert q0 == F(1829, 2048) and 1-h*a*a/4 > 0
    assert 4*a**3/27 < A*A and L < N*N
    r, M = c*qcap/(1-c*qcap), A*radius
    E = L*N*radius*r*r*M
    gain = F(201, 200)
    assert (log_radius+g*M*M/2)/2 < qcap
    assert (log_radius+g*((1+E)*M)**2/2)/2 < qcap
    assert (1+E)/(1-c*qcap) < gain
    qx = q0+h*N*(gain-1)*A
    assert qx == q0+F(1, 160) < F(9, 10)
    drive = g*(gain*M)**2/2
    assert drive < log_radius < F(1, 2)  # exp(-b)>1-b>W_floor.
    residual = (r*M)**2+(c*qcap*gain*M)**2
    assert residual < F(1, 512)
    return dict(status='exact_sufficient_inequalities_pass',
        theorem_scope='uniform conditional target return only, not source or target entry',
        parameter_box=dict(chi_A=['1/32', '1/16'], gamma=['1/2048', '1/1024'],
                           kappa_H=['1/2', '1'], kappa_Ah=['1/2', '1']),
        a=a, h=h, radius=radius, log_history_radius=log_radius, spectral_lower=low,
        spectral_upper=L, contrast_upper=qcap, read_ratio=r, relative_geometry_error=E,
        selected_gain=gain, reduced_contraction=q0, resource_contraction=qx,
        writer_drive_upper=drive, split_residual_upper=residual,
        split_tolerance=F(1, 512), positive_resource_lower=F(5, 6),
        joint_state_contraction_claimed=False, uniform_source_chain_certified=False)


def incidence(n, edges):
    return tuple(tuple(D(i == u)-D(i == v) for u, v in edges) for i in range(n))


def star(f, B):
    return tuple(tuple(sum(D(bool(row[i] and row[j])) for row in B)*f[i]*f[j]/2
                       for j in range(len(f))) for i in range(len(f)))


def norm2(values):
    return sum(v*v for v in values)


def stage(C, W, H, B, chi, gamma, kah):
    BT = tuple(zip(*B))
    d = mv(BT, C)
    stiffness = mv(B, tuple(w*v for w, v in zip(W, d)))
    delta = tuple(tuple(v-D(i == j) for j, v in enumerate(row)) for i, row in enumerate(H))
    geometry_phi = tuple(kah*v for v in mv(B, mv(delta, d)))
    phi = tuple(v-D(19)/4*c+g for c, v, g in zip(C, stiffness, geometry_phi))
    baseline = tuple(-w*v for w, v in zip(W, mv(BT, phi)))
    target = tuple(max(D('0.5'), (-gamma*v*v/2).exp()) for v in baseline)
    q = tuple((w-t)/(w+t) for w, t in zip(W, target))
    J = tuple(v/(1-chi*x) for v, x in zip(baseline, q))
    read = tuple(chi*x*v for x, v in zip(q, J))
    flat = solve(H, read)
    assert max(abs(a-b) for a, b in zip(mv(H, flat), read)) < D('1e-80')
    return dict(baseline=baseline, W_hat=target, contrast=q, current=J,
                read_flux=read, flat=flat, geometry_phi=geometry_phi)


def step(C, W, B, *, chi=D(1)/16, gamma=D(1)/1024, kh=D(1), kah=D(1)):
    I = tuple(tuple(D(i == j) for j in range(len(W))) for i in range(len(W)))
    pred = stage(C, W, I, B, chi, gamma, kah)
    S = star(pred['flat'], B)
    H = tuple(tuple(a+kh*b for a, b in zip(row, other)) for row, other in zip(I, S))
    corr = stage(C, W, H, B, chi, gamma, kah)
    S1 = star(corr['flat'], B)
    residual2 = sum((kh*(a-b))**2 for row, other in zip(S, S1) for a, b in zip(row, other))
    Cnext = tuple(c-D(1)/8*v for c, v in zip(C, mv(B, corr['current'])))
    writer = tuple(max(D('0.5'), (-gamma*j*j/2).exp()) for j in corr['current'])
    # Proposed output only. Publication is separately admitted below.
    Wnext = tuple(((w.ln()+t.ln())/2).exp() for w, t in zip(W, writer))
    failure = ('os_split_residual' if residual2 > (D(1)/512)**2 else
               'resource_nonpositive' if min(Cnext) <= 0 else None)
    assert abs(sum(Cnext)-sum(C)) < D('1e-80')
    return dict(C=C, W=W, reference=pred, generated_edge_hodge=H, fresh=corr,
        split_residual_frobenius_squared=residual2, C_proposed=Cnext, W_proposed=Wnext,
        writer_target=writer, first_failure=failure, published=failure is None,
        current_stage_gap_squared=norm2(tuple(a-b for a, b in zip(corr['current'], pred['current']))),
        readback_gap_squared=norm2(tuple(a-b for a, b in zip(pred['current'], pred['baseline']))),
        geometry_increment_squared=sum((x-D(i == j))**2 for i, row in enumerate(H) for j, x in enumerate(row)),
        geometry_consumption_squared=norm2(corr['geometry_phi']))


def source_test(C, W, chi=D(1)/16, gamma=D(1)/1024):
    B = incidence(5, SOURCE)
    I = tuple(tuple(D(i == j) for j in range(4)) for i in range(4))
    read = stage(C, W, I, B, chi, gamma, D(1))
    paired = C[0] == C[1] and C[2] == C[3] and W[0] == W[1] and W[2] == W[3]
    assert paired  # Symmetry is structural, never a fitted chooser tolerance.
    margins = dict(sector_separation=W[2]-W[0], spectral=D(5)/2*(W[0]+W[2])-D(19)/4,
                   inward=min(read['current']), x=C[4]-(C[0]+C[2])/2, y=(C[0]-C[2])/2)
    active = (margins['sector_separation'] > 0 and margins['spectral'] > 0
              and margins['inward'] > 0 and margins['x'] > 0 and margins['y'] >= 0)
    out = dict(stage='selected_reference_current_recomputed_from_committed_state',
               guard_passes=active, paired_equalities=paired, margins=margins, read=read,
               full_feedback_obstruction_certified=False)
    if active:
        activity = (sum(read['current'][:2]), sum(read['current'][2:]))
        ratio = 65536*activity[0]/sum(activity)
        k = int(ratio.to_integral_value(rounding='ROUND_HALF_EVEN'))
        shares = (D(k)/65536, D(65536-k)/65536)
        out.update(k=k, shares=shares, dyadic_distance_to_tie=D('0.5')-abs(ratio-k),
                   funding=(shares[0]*C[4]-C[0], shares[1]*C[4]-C[2]))
    return out


def counterfactual(C, W, B):
    rows = []
    for attempt in range(1, 17):
        row = step(C, W, B)
        rows.append(dict(attempt=attempt, minimum_proposed_C=min(row['C_proposed']),
                         split_residual_frobenius_squared=row['split_residual_frobenius_squared'],
                         first_failure=row['first_failure'], published=row['published']))
        if row['first_failure']:
            break
        C, W = row['C_proposed'], row['W_proposed']
    return dict(rows=rows, conclusion=rows[-1]['first_failure'] or 'no_failure_in_bounded_horizon',
                diagnostic_only=True, no_event_operand=True)


def compact_step(row):
    """Retain decisive values, not repeated dense intermediate matrices."""
    fields = ('C', 'W', 'C_proposed', 'W_proposed', 'writer_target', 'first_failure',
              'published', 'split_residual_frobenius_squared', 'current_stage_gap_squared',
              'readback_gap_squared', 'geometry_increment_squared', 'geometry_consumption_squared')
    return dict(**{key: row[key] for key in fields},
                baseline_reference=row['reference']['baseline'],
                selected_reference=row['reference']['current'],
                baseline_fresh=row['fresh']['baseline'], selected_fresh=row['fresh']['current'])


def diagnostics():
    with localcontext() as ctx:
        ctx.prec = 96
        C0 = (D(1),)*4+(D(5),)
        W0 = ((D(19)/20)**2,)*2+((D(77)/80)**2,)*2
        B = incidence(5, SOURCE)
        initial = source_test(C0, W0)
        first = step(C0, W0, B)
        assert not initial['guard_passes'] and first['published']
        C1, W1 = first['C_proposed'], first['W_proposed']
        selected = source_test(C1, W1)
        assert selected['guard_passes'] and min(selected['funding']) > 0
        assert selected['dyadic_distance_to_tie'] > 0
        assert all(first[k] > 0 for k in ('current_stage_gap_squared', 'readback_gap_squared',
                                         'geometry_increment_squared', 'geometry_consumption_squared'))
        assert any(w < 1 for w in first['writer_target'])
        zero_chi = step(C0, W0, B, chi=D(0))
        zero_consumer = step(C0, W0, B, kah=D(0))
        assert zero_chi['geometry_increment_squared'] == zero_chi['current_stage_gap_squared'] == 0
        assert zero_consumer['current_stage_gap_squared'] == 0
        assert first['C_proposed'] != zero_consumer['C_proposed']
        homogeneous = source_test((D(9)/5,)*5, W1)
        assert not homogeneous['guard_passes'] and homogeneous['margins']['inward'] == 0
        shares = selected['shares']
        roles = {}
        for name, C, W in (('current', C1, W1), ('reset', C0, W0)):
            target_C = C[:4]+(shares[0]*C[4], shares[1]*C[4])
            target_W = W+(D(1),)
            # Dyadic transfer is conservative in exact reals. Decimal rounding
            # is diagnostic arithmetic, not represented native charge admission.
            assert abs(sum(target_C)-9) < D('1e-80') and target_W[:-1] == W
            rows = []
            for _ in range(3):
                row = step(target_C, target_W, incidence(6, TARGET))
                assert row['published']
                X2 = norm2(tuple(c-D('1.5') for c in row['C_proposed']))
                entry = X2 < (D(2)/3)**2 and all(-D(1)/8 <= w.ln() <= 0 for w in row['W_proposed'])
                rows.append(dict(**compact_step(row), deviation_squared=X2, conditional_return_domain_entered=entry))
                assert entry
                target_C, target_W = row['C_proposed'], row['W_proposed']
            roles[name] = rows
        return dict(status='finite_diagnostic_checks_pass', precision=96, interval_certified=False,
            native_steps=0, physical_target_search=False, initial=initial, first_ordinary=compact_step(first),
            source_selection=selected, target_roles=roles,
            controls=dict(zero_chi=compact_step(zero_chi), zero_geometry_consumer=compact_step(zero_consumer), homogeneous=homogeneous,
                          no_split=counterfactual(C0, W0, B),
                          history_reset_without_split=counterfactual(C1, (D(1),)*4, B)),
            full_feedback_guard_theorem_proved=False, full_parameter_box_chain_certified=False)


def main():
    acceptance_path = REFS / 'ATCSectorConstitutiveAdjudication.json'
    acceptance = json.loads((ROOT / acceptance_path).read_text())
    payload = dict(acceptance)
    digest = payload.pop('record_digest')
    assert hashlib.sha256(canonical(payload)).hexdigest() == digest
    assert acceptance['scientific_acceptance'] and not acceptance['graph_admission']
    for binding in acceptance['source_bindings']:
        assert hashlib.sha256((ROOT / binding['path']).read_bytes()).hexdigest() == binding['sha256'], binding['path']
    paths = [Path(__file__).relative_to(ROOT), acceptance_path,
             INV / 'decisions/ATCSectorReadBackLiftProposal.md',
             REFS / 'review/CAN-LSF-ReadBack-Lift-Review.md',
             INV / 'scripts/certify_atc_os_geometry_feedback.py',
             Path('src/pygrc/models/grc_v4_candidate_a.py'),
             Path('src/pygrc/models/grc_v4_realizations.py'),
             Path('src/pygrc/models/grc_v4_geometry.py')]
    result = serial(dict(schema='grcv4_atc_sector_readback_lift_checks_v1',
        status='research_results_pending_review_not_adjudicated',
        predecessor_scoped_adjudication=digest, conditional_target_bounds=target_bounds(),
        enabled_point=diagnostics(), scientific_acceptance=False, graph_admission=False,
        ATC2_closed=False, second_claim_debt_adjudication_performed=False,
        source_bindings=[dict(path=str(p), sha256=hashlib.sha256((ROOT/p).read_bytes()).hexdigest()) for p in paths]))
    result['record_digest'] = hashlib.sha256(canonical(result)).hexdigest()
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()

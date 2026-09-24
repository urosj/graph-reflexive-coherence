#!/usr/bin/env python3
"""Bounded resource/history competition in a fresh A_OS source read.

Investigation-local mathematics, not a native profile or fission law. Exact
inequalities prove the stated domain; Decimal reads are finite diagnostics.
Reviewed predecessors are hash-checked, never rewritten or rerun.
"""
from decimal import Decimal as D, localcontext
from fractions import Fraction as F
import json
from pathlib import Path
import sys

from certify_atc_os_geometry_feedback import canonical, mv, sha, solve, stringify
from certify_atc_source_partition import PARTITIONS, choose, partition_payload, score

ROOT = Path(__file__).resolve().parents[4]
INV = ROOT / 'implementation/investigations/grc9v4-constitutive-design'
REFS = INV / 'evidence/autonomous-topology-change'
PR = [[0, 1], [2, 3]]
PW = [[0, 2], [1, 3]]
PW_ROTATED = [[0, 3], [1, 2]]
B0 = tuple(tuple(int(i == e)-int(i == 4) for e in range(4)) for i in range(5))


def exact_bounds():
    theta_max, theta_min = F(1, 512), F(1, 1024)
    jmax, component_max, dmax = F(17, 8), F(9, 8), F(9)
    # gamma <= 2^-16 <= theta/64; |log W| <= theta/(1-theta).
    q_coefficient = (1/(1-theta_max) + component_max**2/128)/2
    assert q_coefficient < F(33, 64)
    denominator = 1-F(33, 128)*theta_max
    read_ratio_coefficient = F(33, 128)/denominator
    assert read_ratio_coefficient < F(17, 64)
    read_error_coefficient = F(17, 64)*jmax
    assert read_error_coefficient == F(289, 512)
    geometry_coefficient = 5*dmax*read_error_coefficient**2
    assert geometry_coefficient*theta_max < F(1, 32)
    # First the predictor; then geometry perturbation; then the fresh corrector.
    assert 2*(1+theta_max/16)+theta_max/32 < jmax
    assert 1+theta_max/16+theta_max/32 < component_max
    baseline_min = 1-13*theta_max-theta_max/16-theta_max/32
    assert baseline_min > F(31, 32)
    activity_min = baseline_min/(1+F(33, 128)*theta_max)
    assert activity_min > F(15, 16)
    assert F(1, 65536)*component_max**2/2 < F(1, 2)
    # exp(-x) >= 1-x > 1/2 certifies the pre-read conductance floor.
    residual = 2*(read_error_coefficient*theta_max)**2
    assert residual < F(1, 512)
    # Ideal history-only baseline levels H=1-8 theta, L=1-13 theta+12 theta^2.
    gap_coefficient_min = 5-12*theta_max
    assert gap_coefficient_min == F(637, 128)
    # ||v0(u)-v0(0)|| <= 8 delta <= theta/8.
    error_coefficient = F(1, 8)+F(1, 32)+read_error_coefficient
    assert error_coefficient == F(369, 512)
    gap_lower = F(2, 3)*gap_coefficient_min**2-20*error_coefficient-2*error_coefficient**2
    noisy_error = error_coefficient+F(1, 64)
    noisy_gap_lower = F(2, 3)*gap_coefficient_min**2-20*noisy_error-2*noisy_error**2
    assert gap_lower == F(415981, 393216) > 0
    assert noisy_gap_lower == F(275197, 393216) > 0
    assert activity_min-theta_max/64 > 0

    # Exact anchor algebra: independent incidence baseline versus scalar formula.
    anchors = [(theta_min, theta_min/128), (F(3, 2048), F(3, 2048)*F(3, 256)),
               (theta_max, theta_max/64)]
    for theta, delta in anchors:
        C = (1+delta, 1+delta, 1-delta, 1-delta, F(5))
        W = (F(1), 1-theta, F(1), 1-theta)
        d = mv(tuple(zip(*B0)), C)
        phi = tuple(s-F(19, 4)*c for s, c in zip(mv(B0, tuple(w*x for w, x in zip(W, d))), C))
        matrix = tuple(-w*x for w, x in zip(W, mv(tuple(zip(*B0)), phi)))
        H, L = 1-8*theta, (1-theta)*(1-12*theta)
        expected = tuple((H if w == 1 else L)+w*(F(19, 4)-w)*(c-1)
                         for w, c in zip(W, C))
        assert matrix == expected
        assert choose(C[:4])['minimizers'] == frozenset((frozenset(map(frozenset, PR)),))
    return dict(theta_interval=[theta_min, theta_max], delta_over_theta_interval=[F(1, 128), F(1, 64)],
        gamma_max=F(1, 65536), contrast_over_theta_upper=F(33, 64),
        contrast_estimate_coefficient=q_coefficient, denominator_lower=denominator,
        baseline_norm_upper=jmax, baseline_component_upper=component_max,
        edge_difference_norm_upper=dmax, read_ratio_over_theta_upper=F(17, 64),
        read_error_over_theta_upper=read_error_coefficient,
        geometry_error_over_theta_squared_upper=geometry_coefficient,
        geometry_error_over_theta_upper=F(1, 32), corrector_component_lower=baseline_min,
        selected_activity_lower=activity_min, residual_upper=residual,
        research_residual_tolerance=F(1, 512), ideal_history_gap_over_theta_lower=gap_coefficient_min,
        total_activity_error_over_theta_upper=error_coefficient,
        selected_partition_gap_over_theta_squared_lower=gap_lower,
        additional_activity_error_radius_over_theta=F(1, 64),
        noisy_partition_gap_over_theta_squared_lower=noisy_gap_lower,
        exact_scalar_baseline_anchors=len(anchors))


def dec(value):
    value = F(value)
    return D(value.numerator)/D(value.denominator)


def selection(values):
    exact = tuple(F(v) for v in values)
    result = choose(exact)
    return dict(state=result['state'], minimizers=sorted(partition_payload(p) for p in result['minimizers']),
        minimum=dec(result['minimum']), uniqueness_gap=dec(result['uniqueness_gap']))


def source_read(C_exact, W_exact, theta, *, B=B0, gains=None):
    """Declared source box only; no continuity, history writer or topology edit."""
    if gains is None:
        gains = (F(1, 65536), F(1, 2), F(1), F(1))
    if (len(C_exact) != 5 or len(W_exact) != 4 or
            any(type(x) is not F for x in (*C_exact, *W_exact, theta, *gains))):
        raise ValueError('exact rational source and parameters required')
    gamma0, chi0, kh0, kah0 = gains
    if not (F(1, 1024) <= theta <= F(1, 512) and 0 <= gamma0 <= F(1, 65536)
            and 0 <= chi0 <= F(1, 2) and 0 <= kh0 <= 1 and 0 <= kah0 <= 1):
        raise ValueError('outside declared gain/history domain')
    parent = next(i for i, row in enumerate(B) if sum(bool(x) for x in row) == 4)
    leaves = tuple(next(i for i, row in enumerate(B) if i != parent and row[e]) for e in range(4))
    u = tuple(C_exact[i]-1 for i in leaves)
    if (C_exact[parent] != 5 or sum(C_exact) != 9 or max(map(abs, u)) > theta/64
            or min(W_exact) < 1-theta or max(W_exact) > 1
            or sum(W_exact) != 4-2*theta or sum(w*x for w, x in zip(W_exact, u)) != 0):
        raise ValueError('outside balanced resource/history source family')
    C, W = tuple(map(dec, C_exact)), tuple(map(dec, W_exact))
    gamma, chi, kh, kah = map(dec, gains)
    I = tuple(tuple(D(i == j) for j in range(4)) for i in range(4))
    BT = tuple(zip(*B))
    d = mv(BT, C)
    tolerance = D('1e-80')

    def star(flat):
        return tuple(tuple(sum(D(bool(row[i] and row[j])) for row in B)*flat[i]*flat[j]/2
                           for j in range(4)) for i in range(4))

    def stage(H):
        stiffness = mv(B, tuple(w*x for w, x in zip(W, d)))
        difference = tuple(tuple(x-y for x, y in zip(row, ref)) for row, ref in zip(H, I))
        phi_geom = mv(B, mv(difference, d))
        phi = tuple(s-D(19)/4*c+kah*g for s, c, g in zip(stiffness, C, phi_geom))
        baseline = tuple(-w*x for w, x in zip(W, mv(BT, phi)))
        W_hat = tuple((-gamma*v*v/2).exp() for v in baseline)
        q = tuple((w-hat)/(w+hat) for w, hat in zip(W, W_hat))
        J = tuple(v/(1-chi*x) for v, x in zip(baseline, q))
        read = tuple(chi*x*j for x, j in zip(q, J))
        flat = solve(H, read)
        assert min(W_hat) > D('0.5')
        assert max(map(abs, q)) < dec(F(33, 64)*theta)
        assert max(map(abs, baseline)) < dec(F(9, 8))
        assert sum(v*v for v in baseline) < dec(F(17, 8))**2
        assert max(abs(a-b) for a, b in zip(mv(H, flat), read)) < tolerance
        return dict(baseline=baseline, W_hat=W_hat, contrast=q, current=J, read=read, structural_flat=flat)

    pred = stage(I)
    S = star(pred['structural_flat'])
    H1 = tuple(tuple(x+kh*y for x, y in zip(row, other)) for row, other in zip(I, S))
    corr = stage(H1)
    assert sum((x-y)**2 for x, y in zip(corr['baseline'], pred['baseline'])) < dec(theta/32)**2
    assert sum(x*x for x in corr['read']) <= dec(F(289, 512)*theta)**2
    regen = star(corr['structural_flat'])
    defect = tuple(tuple(kh*(x-y) for x, y in zip(row, other)) for row, other in zip(S, regen))
    assert sum(x*x for row in defect for x in row) <= dec(2*(F(289, 512)*theta)**2)**2 < dec(F(1, 512))**2
    activities = tuple(-b*j for b, j in zip(B[parent], corr['current']))
    assert min(activities) > dec(F(15, 16))

    # Independent reduced-star baseline and geometry computation, no incidence matrices.
    ud = tuple(map(dec, u))
    v0 = tuple(w*((4-x)*(w-D(19)/4)+sum(wj*(4-uj) for wj, uj in zip(W, ud)))
               for w, x in zip(W, ud))
    hat = tuple((-gamma*v*v/2).exp() for v in v0)
    q = tuple((w-z)/(w+z) for w, z in zip(W, hat))
    f = tuple(chi*x*v/(1-chi*x) for x, v in zip(q, v0))
    dot = sum(fi*(-4+x) for fi, x in zip(f, ud))
    Sd = tuple((fi*fi*(-4+x)+fi*dot)/2 for fi, x in zip(f, ud))
    v1 = tuple(v-kah*kh*w*(z+sum(Sd)) for v, w, z in zip(v0, W, Sd))
    for stage_values, expected in ((pred['baseline'], v0), (corr['baseline'], v1)):
        assert max(abs(-b*v-z) for b, v, z in zip(B[parent], stage_values, expected)) < tolerance

    # Continuity generator only, not an executed ordinary update.
    rate = tuple(-x for x in mv(B, corr['current']))
    assert abs(sum(rate)) < tolerance
    assert max(abs(rate[i]+a) for i, a in zip(leaves, activities)) < tolerance
    scores = {}
    for partition in PARTITIONS:
        projected = tuple(next(sum(rate[leaves[j]] for j in block)/len(block)
                               for block in partition if i in block) for i in range(4))
        error = sum((rate[leaves[i]]-projected[i])**2 for i in range(4))
        assert abs(error-dec(score(tuple(map(F, activities)), partition))) < tolerance
        scores[str(partition_payload(partition))] = error
    return dict(C=C, W=W, theta=dec(theta), gains=dict(gamma=gamma, chi_A=chi, kappa_H=kh, kappa_Ah=kah),
        predictor=pred, generated_geometry=H1, corrector=corr, split_defect=defect,
        inward_activities=activities, resource_selection=selection(tuple(C[i] for i in leaves)),
        history_selection=selection(W), current_selection=selection(activities),
        continuity_generator=rate, rate_projection_errors=scores, reduced_star_oracle_matches=True)


def finite_reads(bounds):
    with localcontext() as ctx:
        ctx.prec = 96
        rows = {}
        for name, theta, ratio in [('lower_corner', F(1, 1024), F(1, 128)),
                                   ('interior', F(3, 2048), F(3, 256)),
                                   ('upper_corner', F(1, 512), F(1, 64))]:
            delta = theta*ratio
            C = (1+delta, 1+delta, 1-delta, 1-delta, F(5))
            W = (F(1), 1-theta, F(1), 1-theta)
            row = source_read(C, W, theta)
            assert row['resource_selection']['minimizers'] == [PR]
            assert row['current_selection']['minimizers'] == [PW]
            assert row['history_selection']['minimizers'] == [PW]
            assert row['current_selection']['uniqueness_gap'] > dec(bounds['selected_partition_gap_over_theta_squared_lower']*theta**2)
            ideal = tuple(dec(1-8*theta if w == 1 else (1-theta)*(1-12*theta)) for w in W)
            assert sum((x-y)**2 for x, y in zip(row['inward_activities'], ideal)) < dec(F(369, 512)*theta)**2
            assert row['corrector']['current'] != row['predictor']['current']
            rows[name] = row

        theta, delta = F(1, 512), F(1, 32768)
        C = (1+delta, 1+delta, 1-delta, 1-delta, F(5))
        W = (F(1), 1-theta, F(1), 1-theta)
        uniform_W = (1-theta/2,)*4
        uniform_C = (F(1),)*4+(F(5),)
        rows['reassigned_history'] = source_read(C, (F(1), 1-theta, 1-theta, F(1)), theta)
        assert rows['reassigned_history']['current_selection']['minimizers'] == [PW_ROTATED]
        assert rows['reassigned_history']['resource_selection']['minimizers'] == [PR]
        rows['uniform_history'] = source_read(C, uniform_W, theta)
        assert rows['uniform_history']['current_selection']['minimizers'] == [PR]
        rows['uniform_resources'] = source_read(uniform_C, W, theta)
        assert rows['uniform_resources']['current_selection']['minimizers'] == [PW]
        assert len(rows['uniform_resources']['resource_selection']['minimizers']) == 7
        rows['fully_symmetric'] = source_read(uniform_C, uniform_W, theta)
        assert len(rows['fully_symmetric']['current_selection']['minimizers']) == 7

        for name, gains in [('read_off', (F(1, 65536), F(0), F(1), F(1))),
                            ('geometry_off', (F(1, 65536), F(1, 2), F(0), F(1))),
                            ('geometry_unconsumed', (F(1, 65536), F(1, 2), F(1), F(0))),
                            ('gamma_zero', (F(0), F(1, 2), F(1), F(1)))]:
            rows[name] = source_read(C, W, theta, gains=gains)
            assert rows[name]['current_selection']['minimizers'] == [PW]
        assert rows['read_off']['predictor']['baseline'] == rows['read_off']['corrector']['current']
        assert rows['geometry_off']['corrector']['current'] == rows['geometry_unconsumed']['corrector']['current']
        assert rows['geometry_off']['generated_geometry'] != rows['geometry_unconsumed']['generated_geometry']
        assert rows['upper_corner']['corrector']['current'] != rows['geometry_off']['corrector']['current']

        vp, ep, signs = (4, 2, 0, 3, 1), (2, 0, 3, 1), (-1, 1, -1, 1)
        B = tuple(tuple(B0[i][j]*s for j, s in zip(ep, signs)) for i in vp)
        moved = source_read(tuple(C[i] for i in vp), tuple(W[i] for i in ep), theta, B=B)
        original = rows['upper_corner']
        tolerance = D('1e-80')
        for stage in ('predictor', 'corrector'):
            for field in ('baseline', 'current', 'read', 'structural_flat'):
                assert max(abs(x-original[stage][field][i]*s) for x, i, s in zip(moved[stage][field], ep, signs)) < tolerance
            for field in ('W_hat', 'contrast'):
                assert max(abs(x-original[stage][field][i]) for x, i in zip(moved[stage][field], ep)) < tolerance
        for i, old_i in enumerate(ep):
            for j, old_j in enumerate(ep):
                assert abs(moved['generated_geometry'][i][j]-signs[i]*signs[j]*original['generated_geometry'][old_i][old_j]) < tolerance
        inverse = {old: new for new, old in enumerate(ep)}
        moved_partition = lambda p: sorted(sorted(inverse[i] for i in block) for block in p)
        assert moved['current_selection']['minimizers'] == [moved_partition(PW)]
        assert moved['resource_selection']['minimizers'] == [moved_partition(PR)]
        rows['signed_reordered'] = moved

        rejections = 0
        for bad_C, bad_W, bad_theta in [(C[:-1]+(F(6),), W, theta),
                                       (C, (F(1),)*4, theta), (C, W, F(0))]:
            try:
                source_read(bad_C, bad_W, bad_theta)
            except ValueError:
                rejections += 1
            else:
                raise AssertionError('out-of-domain source admitted')
        assert len(rows) == 12 and rejections == 3
        return stringify(dict(precision=96, certified_rounding_enclosure=False,
            finite_complete_source_reads=len(rows), source_domain_rejections=rejections,
            coordinate_action=dict(vertex_order=vp, edge_order=ep, signs=signs), rows=rows,
            continuity_generators_are_observations_not_updates=True,
            ordinary_steps=0, retained_writes=0, target_reads=0, topology_events=0, native_steps=0))


def run():
    predecessor_path = REFS / 'ATCSourcePartitionCertificate.json'
    prior = json.loads(predecessor_path.read_text())
    expected = '787fd13f12f446dfd5313bec7fbe528bb3e88ac8bd8ec99c103817a0c63e6c5b'
    assert prior['record_digest'] == expected == sha(canonical({k: v for k, v in prior.items() if k != 'record_digest'}))
    for binding in prior['source_bindings']:
        assert sha((ROOT/binding['path']).read_bytes()) == binding['sha256'], binding['path']
    bounds = exact_bounds()
    diagnostics = finite_reads(bounds)
    side = INV / 'tools/exploratory-side-tool'
    sys.path.insert(0, str(side/'tool/src'))
    from grcv4_explorer.a_initializer import load_current_forensic_context
    from grcv4_explorer.forensic import contract_provenance
    context = load_current_forensic_context(ROOT, side)
    for ref in prior['authority_trace_refs']:
        old = json.loads((ROOT/ref['record_path']).read_text())
        assert old['record_digest'] == ref['record_digest'] == sha(canonical({k: v for k, v in old.items() if k != 'record_digest'}))
        value = old
        for part in ref['json_pointer'].strip('/').split('/'):
            value = value[int(part)] if isinstance(value, list) else value[part]
        trace = contract_provenance(context, ref['query']['contract_id'])
        assert canonical(trace) == canonical(value)
        assert trace['rows'][0]['payload']['support_disposition'] == 'indeterminate_requires_review'
    continuity = contract_provenance(context, 'D10.2-EC-PARENT-CORE-INCIDENCE-CONTINUITY')
    assert continuity['rows'][0]['payload']['support_disposition'] == 'indeterminate_requires_review'
    paths = {ROOT/b['path'] for b in prior['source_bindings']}
    paths.update((Path(__file__).resolve(), predecessor_path))
    record = stringify(dict(schema='grcv4_atc_competing_source_information_v1',
        status='passed_exact_bounds_and_finite_source_diagnostics',
        scientific_status='proposed_conditional_mathematics_pending_independent_review',
        predecessor=dict(path=predecessor_path.relative_to(ROOT).as_posix(), record_digest=expected),
        authority_trace_refs=prior['authority_trace_refs'], authority_traces=[continuity],
        exact_bounds=bounds, decimal_diagnostics=diagnostics,
        scope=dict(graph='four-leaf simple star, parent C=5, charge=9',
            resource_pattern='u=(delta,delta,-delta,-delta)', history_pattern='W=(1,1-theta,1,1-theta)',
            gamma_interval=['0', '1/65536'], chi_A_interval=['0', '1/2'],
            kappa_H_interval=['0', '1'], kappa_Ah_interval=['0', '1'],
            potential_derivative='p(c)=19c/4', eta=1, kappa_c=1, alpha=0, beta=0, zeta_A=1,
            W_floor='1/2', carrier=None, reference_H0='identity', reference_H1='identity',
            reference_weights='ones', K4_adapter='identity on normalized common star-tensor coordinates',
            realization='one-pass OS, selected fresh corrector only', source_only=True,
            history_is_supplied_not_generated=True, no_native_profile_admission=True),
        claim_ceiling=['resources do not determine this current-based grouping across the declared retained histories',
            'variance of activities is exactly the two-block least-squares error of instantaneous leaf continuity rates',
            'the operational meaning is conditional on equal weighting and two-block rate representation',
            'history-only grouping also agrees in this history-dominated family; no general optimality claimed',
            'no derived refinement trigger, allocation, target viability, history formation or native topology authority'],
        source_bindings=[dict(path=p.relative_to(ROOT).as_posix(), sha256=sha(p.read_bytes())) for p in sorted(paths)],
        production_changes=False))
    record['record_digest'] = sha(canonical(record))
    return record


if __name__ == '__main__':
    print(json.dumps(run(), sort_keys=True, separators=(',', ':'), allow_nan=False))

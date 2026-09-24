#!/usr/bin/env python3
"""Exact sufficient bounds plus finite Decimal diagnostics for A OS feedback.

Investigation-local mathematics, not a registered potential, native execution,
or a trajectory campaign. Reviewed predecessors are read, never rerun/rewritten.
"""
from decimal import Decimal as D, localcontext
from fractions import Fraction as F
import hashlib
import json
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


def solve(a, b):
    rows = [list(row)+[value] for row, value in zip(a, b, strict=True)]
    n = len(b)
    for i in range(n):
        pivot = rows[i][i]
        assert pivot > 0  # Positive pivots of the SPD stage matrix.
        rows[i] = [x/pivot for x in rows[i]]
        for j in range(i+1, n):
            factor = rows[j][i]
            rows[j] = [x-factor*y for x, y in zip(rows[j], rows[i])]
    out = [D(0)]*n
    for i in reversed(range(n)):
        out[i] = rows[i][-1]-sum(rows[i][j]*out[j] for j in range(i+1, n))
    return tuple(out)


def stringify(value):
    if isinstance(value, (D, F)):
        return str(value)
    if isinstance(value, dict):
        return {k: stringify(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [stringify(v) for v in value]
    return value


def run():
    history_path = REFS/'ATCHistoryFeedbackCertificate.json'
    history = json.loads(history_path.read_text())
    assert history['record_digest'] == 'b2e3ca3131d46d04a92febaf65556a8a9d9b9ff848d5b39b51a5ed41956a9c83'
    assert history['record_digest'] == sha(canonical({k: v for k, v in history.items() if k != 'record_digest'}))
    for binding in history['source_bindings']:
        assert sha((ROOT/binding['path']).read_bytes()) == binding['sha256'], binding['path']
    b = {k: F(v) for k, v in history['bounds'].items() if k != 'mobility_lower'}
    eta, kappa, h, rho = F(1, 4), F(1, 1024), F(1, 64), F(1, 2)
    gamma_max, chi_max, kh_max, kah_max = F(256), F(1, 2), F(1), F(1)
    R, log_radius, K = b['edge_radius'], b['log_radius'], b['auxiliary_history_weight']
    jmax, Aj, Dc = b['current_norm_upper'], b['Aj'], b['Dw']
    edge_contrast_max = b['equilibrium_edge_contrast_bound']+4*R
    qcap = F(1, 200)
    denominator_lower = 1-chi_max*qcap
    read_ratio = chi_max*qcap/denominator_lower
    assert read_ratio == F(1, 399)
    geometry_relative = 4*eta*kah_max*kh_max*edge_contrast_max*read_ratio**2*jmax
    assert (log_radius+gamma_max*jmax**2/2)/2 < qcap
    assert (log_radius+gamma_max*((1+geometry_relative)*jmax)**2/2)/2 < qcap
    L = F(1003, 1000)
    assert (1+geometry_relative)/denominator_lower < L
    assert denominator_lower == F(399, 400)
    assert (1+chi_max*qcap)/denominator_lower < F(101, 100)
    assert gamma_max*((1+geometry_relative)*jmax)**2/2 < log_radius

    qx = b['qx']+h*eta*(L-1)*Aj
    coupling = b['coupling']+h*eta*(L-1)*Dc
    c = b['writer_linearization_bound_c']*L**2
    q_resource = qx+K*c*Aj
    q_history = coupling/K+rho+c*Dc
    q = max(q_resource, q_history)
    resource_margin = R-qx*R-coupling*log_radius
    history_margin = log_radius-gamma_max*(L*jmax)**2/2
    assert 0 < q < 1 and resource_margin > 0 and history_margin > 0
    epsilon = F(1, 4096)
    initial_S = F(3, 2)*F(1, 256)+K*log_radius
    loaded_S = initial_S+F(5, 2)*epsilon
    assert loaded_S < R
    response_loss = h*F(3, 2)/epsilon*(L-1)*jmax
    response_lower = b['individual_Q_lower']-response_loss
    assert response_lower == F(180242767, 858993459200) > 0
    split_upper = kh_max*((read_ratio*jmax)**2+(chi_max*qcap*L*jmax)**2)
    split_tolerance = F(1, 2**30)
    assert split_upper < split_tolerance

    # Strict exact activation bounds for two symmetric, matched prestates.
    jref = F(1, 4096)
    init_a = gamma_max*jref**2/2
    activation_bounds = {}
    for label, depression in (('reference_pass_prepared', init_a), ('inherited_depression', F(1, 256))):
        if label == 'reference_pass_prepared':
            contrast_lower = depression**2/2  # tanh(a*(1-exp(-4a))/2) >= a^2/2.
            assert 4*depression < 1
        else:
            contrast_lower = (depression-init_a)/4
            assert 0 < depression-init_a < 1
        predictor_lower = jref*(1-depression)**2/(1+chi_max*qcap)
        structural_flat_lower = chi_max*contrast_lower*predictor_lower
        baseline_gap_lower = eta*(1-depression)*structural_flat_lower**2
        current_gap_lower = baseline_gap_lower/(1+chi_max*qcap)
        assert current_gap_lower > 0
        activation_bounds[label] = dict(log_depression=depression,
            absolute_predictor_contrast_lower=contrast_lower,
            absolute_predictor_flat_lower=structural_flat_lower,
            corrector_baseline_gap_lower=baseline_gap_lower,
            corrector_current_gap_lower=current_gap_lower)

    coeff = tuple(map(F, history['scope']['p_coefficients']))
    incidence = tuple(tuple(map(F, row)) for row in history['scope']['incidence'])
    examples, controls = [], {}
    counts = dict(complete_mathematical_steps=0, diagnostic_second_corrector_reads=0,
                  native_steps=0, topology_events=0, trajectory_campaigns=0)
    with localcontext() as ctx:
        ctx.prec = 96
        dec = lambda f: D(F(f).numerator)/D(F(f).denominator)
        e, k, dt = dec(eta), dec(kappa), dec(h)
        gamma, chi = dec(gamma_max), dec(chi_max)
        B = tuple(tuple(map(dec, row)) for row in incidence)
        I = tuple(tuple(D(i == j) for j in range(3)) for i in range(3))
        dc = tuple(map(dec, coeff))
        roots = tuple(map(dec, (F(1), F(5, 4), F(3, 2), F(9, 4), F(3))))
        tol = D('1e-80')

        def factored_p(value):
            product = D(1)
            for root in roots:
                product *= value-root
            return product

        def star(flat, matrix):
            stars = [tuple(i for i, v in enumerate(row) if v) for row in matrix]
            return tuple(tuple(D(sum(i in s and j in s for s in stars))/2*flat[i]*flat[j]
                               for j in range(3)) for i in range(3))

        def stage(C, y, H, matrix, chi_value, kah):
            BT = tuple(zip(*matrix))
            w = tuple(value.exp() for value in y)
            dC = mv(BT, C)
            stiffness = mv(matrix, tuple(a*z for a, z in zip(w, dC)))
            delta_H = tuple(tuple(a-z for a, z in zip(row, ref)) for row, ref in zip(H, I))
            geometry_phi = tuple(kah*v for v in mv(matrix, mv(delta_H, dC)))
            p = tuple(sum(a*c**i for i, a in enumerate(dc)) for c in C)
            assert max(abs(v-factored_p(c)) for v, c in zip(p, C)) < tol
            phi = tuple(k*s-v+g for s, v, g in zip(stiffness, p, geometry_phi))
            baseline = tuple(-e*a*z for a, z in zip(w, mv(BT, phi)))
            what = tuple((-gamma*j*j/2).exp() for j in baseline)
            assert min(what) > D('0.5')
            contrast = tuple((a-z)/(a+z) for a, z in zip(w, what))
            assert max(map(abs, contrast)) <= dec(qcap)
            denominator = tuple(1-chi_value*q for q in contrast)
            assert min(denominator) >= dec(denominator_lower)
            total = tuple(j/d for j, d in zip(baseline, denominator))
            read = tuple(chi_value*q*j for q, j in zip(contrast, total))
            flat = solve(H, read)
            assert max(abs(a-z) for a, z in zip(mv(H, flat), read)) < tol
            assert max(abs(a-z-t) for a, z, t in zip(total, baseline, read)) < tol
            return dict(baseline=baseline, W_hat=what, contrast=contrast, current=total,
                        read_flux=read, structural_flat=flat, geometry_potential=geometry_phi)

        def step(C, y, *, kh=D(1), kah=D(1), chi_value=chi, matrix=B):
            counts['complete_mathematical_steps'] += 1
            predictor = stage(C, y, I, matrix, chi_value, kah)
            source = star(predictor['structural_flat'], matrix)
            assert abs(sum(source[i][i] for i in range(3))
                       -sum(v*v for v in predictor['structural_flat'])) < tol
            H = tuple(tuple(a+kh*z for a, z in zip(row, delta)) for row, delta in zip(I, source))
            corrector = stage(C, y, H, matrix, chi_value, kah)
            regen_source = star(corrector['structural_flat'], matrix)
            defect = tuple(tuple(kh*(a-z) for a, z in zip(row, other)) for row, other in zip(source, regen_source))
            assert sum(abs(v) for row in defect for v in row) < dec(split_tolerance)
            J = corrector['current']
            assert sum(j*j for j in J) <= dec((L*jmax)**2)
            Cnext = tuple(c-dt*j for c, j in zip(C, mv(matrix, J)))
            drive = tuple(-gamma*j*j/2 for j in J)
            assert min(drive) > -dec(log_radius)
            ynext = tuple((v+z)/2 for v, z in zip(y, drive))
            assert min(Cnext) > 0 and abs(sum(Cnext)-sum(C)) < tol
            assert all(-dec(log_radius) <= v <= 0 for v in ynext)
            return dict(C=C, log_W=y, predictor=predictor, predictor_source=source,
                        H1=H, corrector=corrector, split_defect=defect,
                        C_next=Cnext, log_W_next=ynext)

        C0 = (D(1), D(1), D('1.5'), D('1.5'))
        base_cases = {}
        for label, depression in (('reference_pass_prepared', dec(init_a)),
                                   ('inherited_depression', D(1)/256)):
            y = (-depression, -depression, D(0))
            result = step(C0, y)
            # Independent symmetric scalar oracle; potential evaluated factored.
            w = (-depression).exp()
            a0 = e*w*(2*k*w*(C0[2]-C0[0])+factored_p(C0[0])-factored_p(C0[2]))
            what0 = (-gamma*a0*a0/2).exp()
            q0 = (w-what0)/(w+what0)
            jp = a0/(1-chi*q0)
            flat0 = chi*q0*jp
            a1 = a0+2*e*w*flat0*flat0*(C0[2]-C0[0])
            what1 = (-gamma*a1*a1/2).exp()
            q1 = (w-what1)/(w+what1)
            jc = a1/(1-chi*q1)
            assert abs(result['predictor']['current'][0]-jp) < tol
            assert abs(result['corrector']['baseline'][0]-a1) < tol
            assert abs(result['corrector']['current'][0]-jc) < tol
            assert abs(result['H1'][0][0]-(1+flat0**2)) < tol
            assert abs(result['corrector']['structural_flat'][0]-chi*q1*jc/(1+flat0**2)) < tol
            assert jc-jp >= dec(activation_bounds[label]['corrector_current_gap_lower'])
            assert result['corrector']['W_hat'] != result['predictor']['W_hat']
            assert result['corrector']['contrast'] != result['predictor']['contrast']
            assert result['corrector']['geometry_potential'] != (0, 0, 0, 0)
            assert any(v for row in result['split_defect'] for v in row)
            stale_q_current = tuple(a/(1-chi*q) for a, q in zip(result['corrector']['baseline'], result['predictor']['contrast']))
            assert stale_q_current != result['corrector']['current']
            wrong_writer = tuple((v-gamma*j*j/2)/2 for v, j in zip(y, result['predictor']['current']))
            assert wrong_writer != result['log_W_next']
            wrong_writer_baseline = tuple((v-gamma*j*j/2)/2 for v, j in zip(y, result['corrector']['baseline']))
            assert wrong_writer_baseline != result['log_W_next']
            wrong_preread = tuple((-gamma*j*j/2).exp() for j in result['corrector']['current'])
            assert wrong_preread != result['corrector']['W_hat']
            result['label'] = label
            result['geometry_current_gap'] = jc-jp
            result['factored_scalar_oracle_matches'] = True
            result['stale_predictor_contrast_discriminated'] = True
            result['predictor_current_writer_discriminated'] = True
            result['baseline_current_writer_discriminated'] = True
            result['selected_current_preread_discriminated'] = True
            base_cases[label] = result
            examples.append(result)

        incoming = base_cases['inherited_depression']
        for label, args in (('geometry_pushforward_off', {'kh': D(0)}),
                            ('geometry_potential_consumer_off', {'kah': D(0)}),
                            ('readback_off', {'chi_value': D(0)})):
            result = step(C0, incoming['log_W'], **args)
            if label == 'readback_off':
                assert result['corrector']['current'] == result['corrector']['baseline']
                assert result['H1'] == I
            else:
                assert result['corrector']['current'] == incoming['predictor']['current']
            assert result['C_next'] != incoming['C_next']
            if label == 'geometry_potential_consumer_off':
                assert result['H1'] == incoming['H1'] != I
            result['label'] = label
            controls[label] = result

        # The forbidden extra corrector is observed, never used to improve OS.
        regenerated = tuple(tuple(a-z for a, z in zip(row, delta))
                            for row, delta in zip(incoming['H1'], incoming['split_defect']))
        second = stage(C0, incoming['log_W'], regenerated, B, chi, D(1))
        counts['diagnostic_second_corrector_reads'] += 1
        assert second['current'] != incoming['corrector']['current']
        controls['forbidden_second_corrector'] = dict(current=second['current'],
            selected=False, reason='OS split residual is diagnostic, not an iteration trigger')

        continued = step(incoming['C_next'], incoming['log_W_next'])
        continued['label'] = 'next_ordinary_reconstruction'
        assert continued['H1'] != incoming['H1']
        assert continued['predictor']['geometry_potential'] == (0, 0, 0, 0)
        examples.append(continued)

        C_asym = tuple(c+z for c, z in zip(C0, mv(B, (dec(epsilon), D(0), D(0)))))
        y_asym = (-D(1)/256, -D(1)/512, -D(1)/1024)
        asymmetric = step(C_asym, y_asym)
        asymmetric['label'] = 'nonuniform_history_and_resource'
        assert asymmetric['H1'][0][2] and asymmetric['H1'][1][2]
        assert max(abs(a-z) for a, z in zip(asymmetric['corrector']['read_flux'], asymmetric['corrector']['structural_flat'])) > D('1e-35')
        examples.append(asymmetric)
        # Signed-edge and vertex/edge reordering pressure on the dense path.
        vp, ep, signs = (2, 0, 3, 1), (2, 0, 1), (-1, 1, -1)
        changed_B = tuple(tuple(B[i][j]*s for j, s in zip(ep, signs)) for i in vp)
        changed = step(tuple(C_asym[i] for i in vp), tuple(y_asym[i] for i in ep), matrix=changed_B)
        assert max(abs(a-asymmetric['C_next'][i]) for a, i in zip(changed['C_next'], vp)) < tol
        assert max(abs(a-asymmetric['log_W_next'][i]) for a, i in zip(changed['log_W_next'], ep)) < tol
        assert max(abs(a-asymmetric['corrector']['current'][i]*s)
                   for a, i, s in zip(changed['corrector']['current'], ep, signs)) < tol
        for i, e_old in enumerate(ep):
            for j, f_old in enumerate(ep):
                assert abs(changed['H1'][i][j]-signs[i]*signs[j]*asymmetric['H1'][e_old][f_old]) < tol
        controls['coordinate_action'] = dict(vertex_order=vp, edge_order=ep, edge_signs=signs, passed=True)

        responses = []
        for child in (2, 3):
            edge_load = tuple(-row[child] for row in zip(*B))
            load = mv(B, edge_load)
            C_loaded = tuple(c+dec(epsilon)*v for c, v in zip(C0, load))
            loaded = step(C_loaded, incoming['log_W'])
            # Subtract the imposed resource displacement before measuring restoration.
            Q = ((loaded['C_next'][child]-C_loaded[child])-(incoming['C_next'][child]-C0[child]))/(2*dec(epsilon))
            assert Q >= dec(response_lower)
            responses.append(dict(child=child, Q=Q, C_loaded=C_loaded, C_next=loaded['C_next']))
        assert counts['complete_mathematical_steps'] == 10

    side = INV/'tools/exploratory-side-tool'
    sys.path.insert(0, str(side/'tool/src'))
    from grcv4_explorer.a_initializer import load_current_forensic_context
    from grcv4_explorer.forensic import contract_provenance
    context = load_current_forensic_context(ROOT, side)
    keys = ('D10.2-EC-PARENT-A-READ-CLOSURE', 'D10.2-EC-GEOM-K4-ASSEMBLY',
            'D10.2-EC-GEOM-HODGE-UPDATE', 'D10.2-EC-OS-A-CORRECTOR',
            'D10.2-EC-OS-STAGE-ORDER', 'D10.2-EC-OS-NO-SECOND-ITERATION')
    traces = [contract_provenance(context, key) for key in keys]
    assert all(t['rows'][0]['payload']['support_disposition'] == 'indeterminate_requires_review' for t in traces)
    paths = {Path(__file__).resolve(), history_path, INV/'scripts/certify_atc_a_history_feedback.py',
             ROOT/'specs/grc-v4-spec.md', ROOT/'specs/grc-v4-a-initializer-spec.md',
             INV/'drafts/2026-09-GRC-V4.md', ROOT/'src/pygrc/models/grc_v4_candidate_a.py',
             ROOT/'src/pygrc/models/grc_v4_geometry.py', ROOT/'src/pygrc/models/grc_v4_realizations.py',
             side/'tool/src/grcv4_explorer/forensic.py', side/'tool/src/grcv4_explorer/a_initializer.py'}
    paths.update(ROOT/row['source_ref']['path'] for t in traces for row in t['rows'])
    record = stringify(dict(schema='grcv4_atc_os_geometry_feedback_certificate_v1',
        status='passed_exact_bounds_and_finite_staged_diagnostics',
        scientific_status='proposed_conditional_mathematics_pending_independent_review',
        research_contract='ATC-A-OS-READBACK-GEOMETRY-HISTORY-v1_not_runtime_registered',
        predecessor_digest=history['record_digest'],
        domain=dict(candidate='A', realization='one-pass OS', incidence=incidence,
            p_coefficients=coeff, alpha=0, beta=0, zeta_A=1,
            eta=eta, kappa_c=kappa, h=h, rho=rho, tau_A='h/log(2) in exact arithmetic',
            gamma=[F(0), gamma_max], chi_A=[F(0), chi_max], kappa_H=[F(0), kh_max],
            kappa_Ah=[F(0), kah_max], W_floor=F(1, 2), W_ref='all ones', H0='identity',
            K4_adapter='identity in the declared common star-tensor coordinates',
            edge_displacement_radius=R, log_history_interval=[-log_radius, F(0)],
            geometry_is_derived_not_retained=True, carrier=None),
        bounds=dict(edge_contrast_max=edge_contrast_max, reference_baseline_norm_upper=jmax,
            contrast_absolute_upper=qcap, denominator_lower=denominator_lower,
            predictor_read_relative_upper=read_ratio, geometry_relative_baseline_error=geometry_relative,
            selected_current_gain_upper=L, qx=qx, history_to_resource=coupling,
            writer_majorant_c=c, q_resource=q_resource, q_history=q_history, q=q,
            resource_invariance_margin=resource_margin, history_invariance_margin=history_margin,
            initial_S_all_depressed_histories=initial_S, loaded_S_upper=loaded_S,
            fixed_load_epsilon=epsilon, finite_response_extra_loss=response_loss,
            individual_Q_lower=response_lower, split_residual_norm_upper=split_upper,
            declared_split_tolerance=split_tolerance),
        activation_bounds=activation_bounds,
        decimal_diagnostics=dict(precision=96, not_a_certified_rounding_enclosure=True,
            examples=examples, matched_controls=controls, individual_load_responses=responses),
        counts=counts, authority_traces=traces,
        source_bindings=[dict(path=p.relative_to(ROOT).as_posix(), sha256=sha(p.read_bytes())) for p in sorted(paths)],
        claim_ceiling=['fixed-tree conductance-depressed exact-real return with active retained, explicit-read and OS geometry channels',
            'one bounded signed joint encounter; finite individual response at the declared epsilon',
            'not native potential/initializer admission, CAN-B mode/partition closure, or topology execution',
            'no all-family, cyclic, repeated-load, adaptive-load, or independent persistent identity claim'],
        production_changes=False))
    record['record_digest'] = sha(canonical(record))
    return record


if __name__ == '__main__':
    print(json.dumps(run(), sort_keys=True, separators=(',', ':'), allow_nan=False))

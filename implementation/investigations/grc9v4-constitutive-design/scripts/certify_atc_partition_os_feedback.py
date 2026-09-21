#!/usr/bin/env python3
"""Bounded supplied-partition/A_OS mathematics; no native events or campaign.

Exact rational sufficient bounds prove the stated domain. Decimal96 stages
are finite discrimination diagnostics, not certified rounding enclosures.
Reviewed predecessors are hash-checked, never executed or overwritten.
"""
from decimal import Decimal as D, localcontext
from fractions import Fraction as F
import json
from pathlib import Path
import sys

from certify_atc_partition_stability import determinant, double_star, mm, shifted
from certify_atc_os_geometry_feedback import canonical, mv, sha, solve, stringify

ROOT = Path(__file__).resolve().parents[4]
INV = ROOT / 'implementation/investigations/grc9v4-constitutive-design'
REFS = INV / 'evidence/autonomous-topology-change'


def incidence(m, n):
    edges = [(i, m+n) for i in range(m)]
    edges += [(i, m+n+1) for i in range(m, m+n)] + [(m+n, m+n+1)]
    return tuple(tuple(F(i == u)-F(i == v) for u, v in edges)
                 for i in range(m+n+2))


def exact_bounds():
    slope, h, rho = F(19, 4), F(1, 8), F(1, 2)
    radius, return_radius, log_radius = F(3), F(1), F(1, 256)
    gamma, chi, qcap = F(1, 65536), F(1, 2), F(1, 256)
    bnorm, lnorm, baseline_norm, history_error = F(5, 2), F(6), F(4), F(19)
    # Max of lambda*(slope-lambda)^2 on [0,6]: endpoints and slope/3.
    assert max(F(0), 6*(slope-6)**2, 4*slope**3/27) < baseline_norm**2
    A = baseline_norm+history_error*log_radius
    jmax = A*radius
    denominator = 1-chi*qcap
    read_ratio = chi*qcap/denominator
    E = lnorm*bnorm*radius*read_ratio**2*jmax
    gain = F(201, 200)
    assert (log_radius+gamma*jmax**2/2)/2 < qcap
    assert (log_radius+gamma*((1+E)*jmax)**2/2)/2 < qcap
    assert (1+E)/denominator < gain
    history_drive = gamma*(gain*jmax)**2/2
    assert history_drive < log_radius < F(1, 2)  # exp(-b)>1-b>W_floor.
    residual = (read_ratio*jmax)**2+(chi*qcap*gain*jmax)**2
    tolerance = F(1, 512)
    assert residual < tolerance
    delta = h*bnorm*(history_error*log_radius+(gain-1)*A)
    q0 = F(29, 32)
    qx = q0+delta
    writer_c = gamma/4*(gain*A)**2*radius
    full_q = max(qx+writer_c, rho)
    assert full_q < 1
    # Common certificate controls the outer radius 3; positive return uses 1.
    assert qx*return_radius < return_radius
    assert rho*log_radius+gamma/4*(gain*A*return_radius)**2 < log_radius
    epsilon = F(1, 64)
    load_bound = 6*epsilon
    assert F(3) < F(7, 4)**2
    entry = F(11, 32)*F(7, 4)+delta*F(7, 4)
    loaded_entry_S = F(11, 32)*F(7, 4)+q0*load_bound+delta*(F(7, 4)+load_bound)+log_radius
    later_loaded_S = entry+log_radius+load_bound
    assert max(loaded_entry_S, later_loaded_S) < return_radius
    # Derivative bound at fixed incoming history, including both fresh reads.
    read_derivative = chi*qcap/denominator+chi*gamma*((1+E)*jmax)**2/(2*denominator**2)
    t = F(1, 384)
    assert read_derivative < t
    fmax = read_ratio*jmax
    geometry_derivative = lnorm*(2*fmax*t*A*bnorm*radius+fmax**2*bnorm)
    current_derivative_error = history_error*log_radius+geometry_derivative+t*(A+geometry_derivative)
    response_error = h*bnorm*current_derivative_error*F(5, 4)
    assert F(3, 2) < F(5, 4)**2  # sqrt((degree+1)/degree), degree>=2.
    assert response_error < F(3, 16) < F(7, 24)
    assert F(49, 8) < F(5, 2)**2
    assert F(66211, 8192) > F(14, 5)**2
    unstable_distance_lower = F(14, 5)-delta*F(5, 2)
    assert unstable_distance_lower > F(5, 2)
    exact_rows = []
    for m, n in ((2, 2), (1, 3)):
        B = incidence(m, n)
        lap = double_star(m, n)
        assert mm(B, list(zip(*B))) == lap
        for value in map(F, range(7)):
            assert determinant(shifted(lap, value)) == (value-1)**2*value*(value**3-8*value**2+(m*n+13)*value-6)
        C = (F(1),)*4+(F(5*m, 4), F(5*n, 4))
        z = tuple(c-F(3, 2) for c in C)
        a0 = mv(tuple(zip(*B)), mv(shifted(lap, slope), C))
        after = tuple(c-h*v for c, v in zip(C, mv(B, a0)))
        dist0 = sum(v*v for v in z)
        dist1 = sum((c-F(3, 2))**2 for c in after)
        L2, L3 = mm(lap, lap), mm(mm(lap, lap), lap)
        responses = [h/(block+1)*(slope*L2[i][i]-L3[i][i])
                     for i, block in ((4, m), (5, n))]
        if m == 2:
            assert dist0 == 3 and dist1 == F(363, 1024)
            assert responses == [F(7, 24)]*2
            assert mv(lap, z) == tuple(3*v for v in z)
        else:
            assert determinant(shifted(lap, F(5))) == -80
            assert dist0 == F(49, 8) and dist1 == F(66211, 8192)
            assert responses == [F(15, 32), F(-3, 16)]
            assert min(after)-delta*F(5, 2) > 0
            # Individual load segments stay inside the outer bound.
            assert F(5, 2)+5*epsilon < radius
        exact_rows.append(dict(partition=[m, n], incidence=B, C=C,
            zero_feedback_C_next=after, D0_squared=dist0, D1_squared=dist1,
            child_Q=responses))
    # Symmetric source scalar bounds, separate from the target radius domain.
    source_baseline_lower = 4*(1-log_radius)*(5*(1-log_radius)-slope)
    source_corrector_upper = 1+50*read_ratio**2
    assert source_baseline_lower > 0
    assert (log_radius+gamma*source_corrector_upper**2/2)/2 < qcap
    assert source_corrector_upper < jmax
    source_residual_upper = 4*read_ratio**2+4*(chi*qcap*source_corrector_upper/denominator)**2
    assert source_residual_upper < tolerance
    # Strict geometry-consumption witness at the fully enabled corner only.
    # y=-1/512 on old edges; symmetric bridge current is zero.
    depression = F(1, 512)
    predictor_baseline_lower = F(3, 2)*(1-depression)*(slope-3)
    assert F(3, 2)*(slope-3*(1-depression)) < 3
    contrast_lower = (depression-gamma*9/2)/4
    assert 0 < contrast_lower < 1
    flat_lower = chi*contrast_lower*predictor_baseline_lower/(1+chi*qcap)
    geometry_gap_lower = F(27, 4)*(1-depression)*flat_lower**2
    selected_gap_lower = geometry_gap_lower/(1+chi*qcap)
    assert selected_gap_lower > 0
    return dict(slope=slope, eta=F(1), kappa_c=F(1), h=h, rho=rho,
        outer_radius=radius, positive_return_radius=return_radius, log_radius=log_radius,
        gamma_max=gamma, chi_max=chi, qcap=qcap, B_norm_upper=bnorm,
        laplacian_norm_upper=lnorm, baseline_operator_upper=baseline_norm,
        history_operator_error_coefficient=history_error, A=A, jmax=jmax,
        denominator_lower=denominator, read_ratio=read_ratio,
        relative_geometry_error=E, selected_gain=gain, history_drive_upper=history_drive,
        split_residual_upper=residual, research_split_tolerance=tolerance,
        resource_update_error=delta, reference_contraction=q0, resource_contraction=qx,
        writer_majorant=writer_c, full_state_contraction=full_q,
        epsilon=epsilon, joint_load_norm_upper=load_bound, first_entry_upper=entry,
        initial_loaded_entry_S_upper=loaded_entry_S, later_loaded_S_upper=later_loaded_S,
        read_derivative_upper=read_derivative, read_derivative_rational_majorant=t,
        geometry_derivative_upper=geometry_derivative,
        current_derivative_error=current_derivative_error, child_Q_error=response_error,
        stable_child_Q_lower=F(7, 24)-response_error,
        unstable_small_child_Q_lower=F(15, 32)-response_error,
        unstable_large_child_Q_upper=F(-3, 16)+response_error,
        unstable_first_distance_lower=unstable_distance_lower,
        source_baseline_lower=source_baseline_lower,
        source_corrector_upper=source_corrector_upper,
        source_split_residual_upper=source_residual_upper,
        activation_contrast_lower=contrast_lower,
        activation_baseline_gap_lower=geometry_gap_lower,
        activation_selected_gap_lower=selected_gap_lower,
        activation_outer_resource_gap_lower=h*selected_gap_lower,
        exact_partition_rows=exact_rows)


def diagnostics(bounds):
    counts = dict(complete_mathematical_steps=0, unselected_extra_correctors=0,
                  premature_history_stage_reads=0, exact_reference_images=2,
                  native_steps=0, topology_events=0, trajectory_campaigns=0)
    with localcontext() as ctx:
        ctx.prec = 96
        dec = lambda f: D(F(f).numerator)/D(F(f).denominator)
        h, gamma, chi = map(dec, (bounds['h'], bounds['gamma_max'], bounds['chi_max']))
        slope, eps = dec(bounds['slope']), dec(bounds['epsilon'])
        tol = D('1e-80')

        def star(f, B):
            return tuple(tuple(sum(D(bool(row[i] and row[j])) for row in B)*f[i]*f[j]/2
                               for j in range(len(f))) for i in range(len(f)))

        def stage(C, y, H, B, *, g=gamma, ch=chi, consumer=D(1)):
            BT = tuple(zip(*B)); n = len(y)
            w = tuple(v.exp() for v in y)
            dc = mv(BT, C)
            stiffness = mv(B, tuple(a*v for a, v in zip(w, dc)))
            dh = tuple(tuple(v-D(i == j) for j, v in enumerate(row)) for i, row in enumerate(H))
            geometry_phi = tuple(consumer*v for v in mv(B, mv(dh, dc)))
            phi = tuple(l-slope*c+v for l, c, v in zip(stiffness, C, geometry_phi))
            baseline = tuple(-a*v for a, v in zip(w, mv(BT, phi)))
            what = tuple((-g*v*v/2).exp() for v in baseline)
            q = tuple((a-b)/(a+b) for a, b in zip(w, what))
            current = tuple(v/(1-ch*c) for v, c in zip(baseline, q))
            read = tuple(ch*c*v for c, v in zip(q, current))
            flat = solve(H, read)
            assert min(what) > D('0.5')
            assert max(map(abs, q)) < dec(bounds['qcap'])
            assert max(abs(a-b) for a, b in zip(mv(H, flat), read)) < tol
            return dict(baseline=baseline, W_hat=what, contrast=q, current=current,
                        read_flux=read, structural_flat=flat, geometry_potential=geometry_phi)

        def step(C, y, B, *, g=gamma, ch=chi, kh=D(1), consumer=D(1)):
            counts['complete_mathematical_steps'] += 1
            n = len(y)
            I = tuple(tuple(D(i == j) for j in range(n)) for i in range(n))
            pred = stage(C, y, I, B, g=g, ch=ch, consumer=consumer)
            S = star(pred['structural_flat'], B)
            assert abs(sum(S[i][i] for i in range(n))-sum(v*v for v in pred['structural_flat'])) < tol
            H = tuple(tuple(a+kh*v for a, v in zip(row, other)) for row, other in zip(I, S))
            corr = stage(C, y, H, B, g=g, ch=ch, consumer=consumer)
            regenerated = star(corr['structural_flat'], B)
            defect = tuple(tuple(kh*(a-b) for a, b in zip(row, other)) for row, other in zip(S, regenerated))
            # Frobenius controls spectral norm; this is still a Decimal diagnostic.
            assert sum(v*v for row in defect for v in row) < dec(bounds['research_split_tolerance'])**2
            J = corr['current']
            Cnext = tuple(c-h*v for c, v in zip(C, mv(B, J)))
            ynext = tuple(v/2-g*j*j/4 for v, j in zip(y, J))
            assert min(Cnext) > 0 and abs(sum(Cnext)-sum(C)) < tol
            assert all(-dec(bounds['log_radius']) <= v <= 0 for v in ynext)
            if len(C) == 6:
                z = tuple(c-D('1.5') for c in C)
                X2 = sum(v*v for v in z)
                assert X2 <= dec(bounds['outer_radius'])**2
                assert sum(v*v for v in J) <= (dec(bounds['selected_gain']*bounds['A']))**2*X2
                lap_z = mv(B, mv(tuple(zip(*B)), z))
                reference_J = mv(tuple(zip(*B)), tuple(slope*v-l for v, l in zip(z, lap_z)))
                reference_after = tuple(c-h*v for c, v in zip(C, mv(B, reference_J)))
                error2 = sum((a-b)**2 for a, b in zip(Cnext, reference_after))
                assert error2 <= dec(bounds['resource_update_error'])**2*X2+tol
                degrees = sorted(sum(bool(v) for v in row) for row in B)
                if degrees == [1, 1, 1, 1, 3, 3]:
                    assert sum((v-D('1.5'))**2 for v in Cnext) <= dec(bounds['resource_contraction'])**2*X2+tol
            return dict(C=C, log_W=y, predictor=pred, H1=H, corrector=corr,
                        split_defect=defect, C_next=Cnext, log_W_next=ynext)

        examples, controls, responses = {}, {}, []
        incoming_y = (-D(1)/512,)*4+(D(0),)
        for m, n in ((2, 2), (1, 3)):
            key = f'{m}+{n}'; B = tuple(tuple(map(dec, row)) for row in incidence(m, n))
            C = (D(1),)*4+(D(5*m)/4, D(5*n)/4)
            on = step(C, incoming_y, B)
            D0 = sum((v-D('1.5'))**2 for v in C)
            D1 = sum((v-D('1.5'))**2 for v in on['C_next'])
            assert (D1 < D0) == (m == 2)
            if m == 2:
                assert D1 < 1
            on['D0_squared'], on['D1_squared'] = D0, D1
            examples[key] = on
            controls[key] = {}
            for label, args in [('geometry_off', dict(kh=D(0))),
                                ('consumer_off', dict(consumer=D(0))),
                                ('readback_off', dict(ch=D(0))),
                                ('gamma_off', dict(g=D(0)))]:
                off = step(C, incoming_y, B, **args)
                assert off['C_next'] != on['C_next']
                if label in ('geometry_off', 'consumer_off'):
                    assert off['corrector']['current'] == on['predictor']['current']
                if label == 'consumer_off':
                    assert off['H1'] == on['H1']
                controls[key][label] = {k: off[k] for k in ('C_next', 'log_W_next', 'H1')}
                controls[key][label]['selected_current'] = off['corrector']['current']
            reference = step(C, (D(0),)*5, B, g=D(0), ch=D(0), kh=D(0), consumer=D(0))
            exact = next(r for r in bounds['exact_partition_rows'] if r['partition'] == [m, n])
            assert max(abs(v-dec(w)) for v, w in zip(reference['C_next'], exact['zero_feedback_C_next'])) < tol
            controls[key]['zero_feedback_reference'] = dict(C_next=reference['C_next'],
                selected_current=reference['corrector']['current'], exact_oracle_matches=True)
            # Each complete OS read reconstructs both stages; history held fixed.
            for child, block in ((4, m), (5, n)):
                edge_load = tuple(-row[child] for row in zip(*B))
                load = mv(B, edge_load)
                loaded_C = tuple(c+eps*v for c, v in zip(C, load))
                loaded = step(loaded_C, incoming_y, B)
                Q = ((loaded['C_next'][child]-loaded_C[child])-(on['C_next'][child]-C[child]))/((block+1)*eps)
                reference_Q = dec(exact['child_Q'][child-4])
                assert abs(Q-reference_Q) < dec(bounds['child_Q_error'])
                assert (Q > 0) == (m == 2 or child == 4)
                responses.append(dict(partition=[m, n], child=child, Q=Q, C_loaded=loaded_C,
                    C_next=loaded['C_next'], selected_current=loaded['corrector']['current']))

        # Independent group-scalar oracle for the symmetric 2+2 read.
        sym = examples['2+2']; w = (-D(1)/512).exp(); d = D('-1.5')
        a0 = w*(slope-3*w)*d
        q0 = (w-(-gamma*a0*a0/2).exp())/(w+(-gamma*a0*a0/2).exp())
        jp = a0/(1-chi*q0); f = chi*q0*jp
        # The two old edges at each child share half their outer product.
        a1 = a0-w*D('4.5')*f*f*d
        q1 = (w-(-gamma*a1*a1/2).exp())/(w+(-gamma*a1*a1/2).exp())
        jc = a1/(1-chi*q1)
        assert max(abs(v-jc) for v in sym['corrector']['current'][:4]) < tol
        assert abs(sym['corrector']['current'][4]) < tol
        assert sym['H1'][0][1] != 0 and abs(sym['H1'][0][1]-f*f/2) < tol
        assert abs(sym['corrector']['structural_flat'][0]-chi*q1*jc/(1+D('1.5')*f*f)) < tol
        assert jc != jp
        assert jc-jp >= dec(bounds['activation_selected_gap_lower'])
        scalar = dict(predictor=jp, corrector=jc, current_gap=jc-jp,
                      each_outer_resource_gap=-h*(jc-jp), each_child_resource_gap=2*h*(jc-jp))

        # Uniform source history keeps the four activities equal, without IDs.
        Bs = tuple(tuple(D(i == e)-D(i == 4) for e in range(4)) for i in range(5))
        source = step((D(1),)*4+(D(5),), incoming_y[:4], Bs)
        source_a = 4*w*(5*w-slope)
        source_q = (w-(-gamma*source_a*source_a/2).exp())/(w+(-gamma*source_a*source_a/2).exp())
        source_j = source_a/(1-chi*source_q); source_f = chi*source_q*source_j
        source_b = source_a+50*w*source_f*source_f
        assert max(abs(v-source_b) for v in source['corrector']['baseline']) < tol
        assert len(set(source['corrector']['current'])) == 1 and min(source['corrector']['current']) > 0

        B = tuple(tuple(map(dec, row)) for row in incidence(2, 2))
        continued = step(sym['C_next'], sym['log_W_next'], B)
        assert continued['predictor']['geometry_potential'] == (D(0),)*6
        assert continued['H1'] != sym['H1']
        old_history = step(sym['C_next'], sym['log_W'], B)
        assert continued['corrector']['current'] != old_history['corrector']['current']
        controls['frozen_history_next_read'] = dict(C=old_history['C'], log_W=old_history['log_W'],
            selected_current=old_history['corrector']['current'], C_next=old_history['C_next'])

        # Pressure freshness, writer role and forbidden same-beat iteration.
        stale = tuple(v/(1-chi*q) for v, q in zip(sym['corrector']['baseline'], sym['predictor']['contrast']))
        assert stale != sym['corrector']['current']
        assert tuple(v/2-gamma*j*j/4 for v, j in zip(sym['log_W'], sym['predictor']['current'])) != sym['log_W_next']
        assert tuple(v/2-gamma*j*j/4 for v, j in zip(sym['log_W'], sym['corrector']['baseline'])) != sym['log_W_next']
        assert tuple((-gamma*j*j/2).exp() for j in sym['corrector']['current']) != sym['corrector']['W_hat']
        early = stage(sym['C'], sym['log_W_next'], sym['H1'], B)
        counts['premature_history_stage_reads'] += 1
        assert early['current'] != sym['corrector']['current']
        regenH = tuple(tuple(h-d for h, d in zip(row, defect)) for row, defect in zip(sym['H1'], sym['split_defect']))
        second = stage(sym['C'], sym['log_W'], regenH, B)
        counts['unselected_extra_correctors'] += 1
        assert second['current'] != sym['corrector']['current']

        # Nonuniform W and a signed/reordered representation of the same state.
        y_asym = tuple(-D(i+1)/2048 for i in range(5))
        C_asym = (D(1)+eps, D(1), D(1), D(1), D('2.5')-eps, D('2.5'))
        asym = step(C_asym, y_asym, B)
        vp, ep, signs = (5, 2, 0, 4, 1, 3), (4, 2, 0, 3, 1), (-1, 1, -1, 1, -1)
        changed_B = tuple(tuple(B[i][j]*s for j, s in zip(ep, signs)) for i in vp)
        changed = step(tuple(C_asym[i] for i in vp), tuple(y_asym[i] for i in ep), changed_B)
        assert max(abs(v-asym['C_next'][i]) for v, i in zip(changed['C_next'], vp)) < tol
        assert max(abs(v-asym['log_W_next'][i]) for v, i in zip(changed['log_W_next'], ep)) < tol
        for i, old_i in enumerate(ep):
            assert abs(changed['corrector']['current'][i]-signs[i]*asym['corrector']['current'][old_i]) < tol
            for j, old_j in enumerate(ep):
                assert abs(changed['H1'][i][j]-signs[i]*signs[j]*asym['H1'][old_i][old_j]) < tol
        assert counts['complete_mathematical_steps'] == 21
        return stringify(dict(precision=96, certified_rounding_enclosure=False,
            incoming_history_meaning='old edges inherit the same supplied log-W; new bridge log-W=0; no native event policy inferred',
            examples=examples, matched_controls=controls, child_responses=responses,
            symmetric_scalar_oracle=scalar, source_equal_activity=source,
            continued_step=continued, nonuniform_state=asym,
            coordinate_action=dict(vertex_order=vp, edge_order=ep, signs=signs, passed=True),
            staging_pressure=dict(stale_contrast=True, predictor_writer=True, baseline_writer=True,
                selected_current_preread=True, premature_new_history=True, extra_corrector=True),
            extra_corrector_current=second['current'], extra_corrector_selected=False,
            counts=counts))


def run():
    predecessors = [('ATCPartitionStabilityReviewCertificate.json', '666e648576159f99c1c041772290174abd1f367d5a0d616046380ee2c51e911a'),
                    ('ATCOSGeometryFeedbackCertificate.json', 'c78185f49678aeba71dbc2045cac9831ffaeefe44d9f741383bd4333ee1207e6')]
    for name, expected in predecessors:
        record = json.loads((REFS/name).read_text())
        assert record['record_digest'] == expected == sha(canonical({k: v for k, v in record.items() if k != 'record_digest'}))
        for binding in record['source_bindings']:
            assert sha((ROOT/binding['path']).read_bytes()) == binding['sha256'], binding['path']
    bounds = exact_bounds()
    finite = diagnostics(bounds)
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
    # The predecessor retains the complete identical source/edge/payload rows.
    # Bind those bytes, rather than duplicating six large unchanged traces.
    previous = json.loads((REFS/'ATCOSGeometryFeedbackCertificate.json').read_text())
    trace_refs = []
    for trace in traces:
        index = next(i for i, old in enumerate(previous['authority_traces']) if old['query'] == trace['query'])
        assert canonical(trace) == canonical(previous['authority_traces'][index])
        trace_refs.append(dict(operation=trace['operation'], query=trace['query'],
            trace_digest=trace['trace_digest'], support_disposition='indeterminate_requires_review',
            record_path=(REFS/'ATCOSGeometryFeedbackCertificate.json').relative_to(ROOT).as_posix(),
            record_digest=previous['record_digest'], json_pointer=f'/authority_traces/{index}',
            freshly_queried_equal_to_retained_trace=True))
    paths = {Path(__file__).resolve(), INV/'scripts/certify_atc_partition_stability.py',
             INV/'scripts/certify_atc_partition_review.py', INV/'scripts/certify_atc_os_geometry_feedback.py',
             ROOT/'specs/grc-v4-spec.md', ROOT/'specs/grc-v4-a-initializer-spec.md',
             INV/'drafts/2026-09-GRC-V4.md', ROOT/'src/pygrc/models/grc_v4_candidate_a.py',
             ROOT/'src/pygrc/models/grc_v4_geometry.py', ROOT/'src/pygrc/models/grc_v4_realizations.py',
             side/'tool/src/grcv4_explorer/forensic.py', side/'tool/src/grcv4_explorer/a_initializer.py'}
    paths.update(REFS/name for name, _ in predecessors)
    paths.update(ROOT/row['source_ref']['path'] for trace in traces for row in trace['rows'])
    record = stringify(dict(schema='grcv4_atc_partition_os_feedback_certificate_v1',
        status='passed_exact_bounds_and_finite_staged_diagnostics',
        scientific_status='proposed_conditional_mathematics_pending_independent_review',
        research_contract='ATC-A-OS-AFFINE-PARTITION-FEEDBACK-v1_not_runtime_registered',
        predecessors=[dict(path=(REFS/name).relative_to(ROOT).as_posix(), record_digest=digest) for name, digest in predecessors],
        domain=dict(candidate='A', realization='one-pass OS', source_C=[1, 1, 1, 1, 5],
            partitions=[[2, 2], [1, 3]], target_charge=9, target_equilibrium='(3/2)*ones(6)',
            potential_derivative='p(c)=(19/4)c, not the degree-two multiwell potential',
            eta=1, kappa_c=1, h='1/8', rho='1/2', tau_A='h/log(2) in exact arithmetic',
            gamma=['0', '1/65536'], chi_A=['0', '1/2'], kappa_H=['0', '1'], kappa_Ah=['0', '1'],
            alpha=0, beta=0, zeta_A=1, W_floor='1/2', log_W=['-1/256', '0'],
            reference_edge_weights='ones', reference_H0='identity', reference_H1='identity',
            K4_adapter='identity on overlap-normalized common star-tensor coordinates',
            persistent_carrier=None, geometry_retained=False,
            positive_return_domain='2+2: ||C-(3/2)1||_2<=1; whole declared log-W interval',
            outer_bound_domain='||C-(3/2)1||_2<=3; not asserted all-positive or invariant',
            residual_norm='reference-relative edge operator norm', residual_tolerance='1/512, research only'),
        exact_bounds=bounds, decimal_diagnostics=finite, authority_trace_refs=trace_refs,
        source_bindings=[dict(path=p.relative_to(ROOT).as_posix(), sha256=sha(p.read_bytes())) for p in sorted(paths)],
        claim_ceiling=['same-source supplied-map partition discrimination with full OS history/read/geometry feedback',
            '2+2 positive full-state return after one entry step and one bounded fixed-reference encounter',
            '1+3 expanding linearized mode and positive-resource first-step expansion; not indefinite positive divergence',
            'uniform return/sign bounds over the declared gain box; activation witnesses only at the fully enabled corner',
            'not autonomous partition selection, CAN-B closure, native conformance or accepted authority'],
        production_changes=False))
    record['record_digest'] = sha(canonical(record))
    return record


if __name__ == '__main__':
    print(json.dumps(run(), sort_keys=True, separators=(',', ':'), allow_nan=False))

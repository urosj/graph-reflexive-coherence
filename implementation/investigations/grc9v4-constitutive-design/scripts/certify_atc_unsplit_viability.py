#!/usr/bin/env python3
"""Source viability obstruction and cross-topology energy ambiguity.

Investigation-local A_OS mathematics. No automatic event, native substrate
change, topology chooser or claim admission. Reviewed evidence is only read.
"""
from decimal import Decimal as D, localcontext
from fractions import Fraction as F
import json
from pathlib import Path
import sys

from certify_atc_os_geometry_feedback import canonical, mv, sha, solve, stringify

ROOT = Path(__file__).resolve().parents[4]
INV = ROOT/'implementation/investigations/grc9v4-constitutive-design'
REFS = INV/'evidence/autonomous-topology-change'
B0 = tuple(tuple(int(i == e)-int(i == 4) for e in range(4)) for i in range(5))


def exact_bounds():
    b, gamma, Q, chi, dt = F(1, 256), F(1, 65536), F(1, 256), F(1, 2), F(1, 8)
    w_lower = 1-b
    baseline_coefficient = w_lower*(5*w_lower-F(19, 4))
    lower = baseline_coefficient/(1+chi*Q)
    assert lower == F(5015, 21888) > 0
    denominator = 1-chi*Q
    read_ratio = chi*Q/denominator
    assert read_ratio == F(1, 511)
    v0max, v1max = F(9, 4), F(5, 2)
    geometry = F(225, 2)*(read_ratio*v0max)**2
    assert (b+gamma*v0max**2/2)/2 < Q
    assert v0max+geometry < v1max
    assert (b+gamma*v1max**2/2)/2 < Q
    assert 1-gamma*v1max**2/2 > F(1, 2)
    jmax = v1max/denominator
    writer_drive = gamma*jmax**2/2
    assert writer_drive == F(25, 522242) < b
    residual = 4*((read_ratio*v0max)**2+(read_ratio*v1max)**2)
    assert residual == F(181, 1044484) < F(1, 512)
    multiplier = 1+5*dt*lower
    assert multiplier == F(200179, 175104)
    assert 4*multiplier**6 < 9 < 4*multiplier**7
    assert 4*F(37, 32)**5 < 9 < 4*F(37, 32)**6
    # Frozen-W, read-off source concentration and leaf-contrast eigenmodes.
    lap = tuple(tuple(sum(B0[i][e]*B0[j][e] for e in range(4)) for j in range(5)) for i in range(5))
    modes = [(tuple(map(F, (-1, -1, -1, -1, 4))), F(5))]
    modes += [(tuple(F(i == 0)-F(i == j) for i in range(5)), F(1)) for j in (1, 2, 3)]
    for v, eig in modes:
        assert mv(lap, v) == tuple(eig*x for x in v)
        rate = mv(lap, tuple(x-F(19, 4)*y for x, y in zip(mv(lap, v), v)))
        assert rate == tuple(eig*(eig-F(19, 4))*x for x in v)
    return dict(log_history_radius=b, gamma_max=gamma, contrast_cap=Q,
        denominator_lower=denominator, baseline_coefficient_lower=baseline_coefficient,
        predictor_component_upper=v0max, corrector_component_upper=v1max,
        geometry_component_increment_upper=geometry, selected_current_component_upper=jmax,
        selected_current_over_concentration_lower=lower, writer_drive_magnitude_upper=writer_drive,
        residual_upper=residual, research_tolerance=F(1, 512),
        step_duration=dt, lower_concentration_multiplier=multiplier,
        resource_exit_attempt_bound=7, zero_channel_exit_attempt=6,
        zero_channel_concentration_rate=F(5, 4), zero_channel_leaf_contrast_rate=F(-15, 4),
        zero_channel_concentration_multiplier=F(37, 32),
        zero_channel_leaf_contrast_multiplier=F(17, 32),
        continuous_zero_channel_boundary_time='(4/5)*log(9/4)',
        arbitrary_positive_fixed_step='x_next >= (1+5*dt*c_min)*x; history writer is a convex combination',
        infinite_positive_continuation=False, initial_present_read_is_admissible=True)


def energy_checks(prior):
    def energy(C, B, mu=F(0)):
        d = mv(tuple(zip(*B)), C)
        return F(19, 8)*sum(c*c for c in C)-sum(x*x for x in d)/2+len(C)*mu

    source = (F(1),)*4+(F(5),)
    states = [('source', source, B0)]
    for row in prior['exact_bounds']['exact_partition_rows']:
        states.append(('target_'+''.join(map(str, row['partition'])), tuple(map(F, row['C'])),
                       tuple(tuple(map(F, r)) for r in row['incidence'])))
    values, gradient_checks = {}, 0
    for name, C, B in states:
        d = mv(tuple(zip(*B)), C)
        gradient = tuple(F(19, 4)*c-z for c, z in zip(C, mv(B, d)))
        values[name] = dict(C=C, energy_mu_zero=energy(C, B), energies={str(mu): energy(C, B, F(mu)) for mu in (0, 3, 5)})
        for mu in map(F, (0, 3, 5)):
            for i in range(len(C)):
                plus = tuple(c+F(j == i, 64) for j, c in enumerate(C))
                minus = tuple(c-F(j == i, 64) for j, c in enumerate(C))
                assert (energy(plus, B, mu)-energy(minus, B, mu))/F(1, 32) == gradient[i]
                gradient_checks += 1
    assert values['source']['energy_mu_zero'] == F(295, 8)
    assert values['target_22']['energy_mu_zero'] == F(555, 16)
    assert values['target_13']['energy_mu_zero'] == F(2055, 64)
    differences = {name: row['energy_mu_zero']-values['source']['energy_mu_zero']
                   for name, row in values.items() if name != 'source'}
    assert differences == dict(target_22=F(-35, 16), target_13=F(-305, 64))
    assert differences['target_13'] < differences['target_22'] < 0
    assert differences['target_22']+3 > 0 and differences['target_13']+5 > 0
    return dict(functional='E_mu=sum_i(19*C_i^2/8+mu)-sum_edges(dC)^2/2',
        scope='unit-W read-off reference energy; not a Lyapunov claim for full feedback',
        states=values, split_energy_differences_mu_zero=differences,
        split_difference_offset='Delta_E_mu=Delta_E_0+mu for one added unit-measure vertex',
        exact_gradient_offset_checks=gradient_checks,
        energy_ranking_prefers_known_13_counterexample=True,
        full_declared_read_and_writer_depend_on_derivatives_not_mu=True,
        topological_creation_energy_not_fixed_by_fixed_graph_dynamics=True,
        new_target_dynamic_runs=0)


def dec(f):
    f = F(f)
    return D(f.numerator)/D(f.denominator)


def finite_continuations(bounds):
    with localcontext() as ctx:
        ctx.prec = 96
        b, gamma, dt = dec(bounds['log_history_radius']), dec(bounds['gamma_max']), dec(bounds['step_duration'])
        tol = D('1e-78')
        counts = dict(complete_source_reads=0, positive_ordinary_updates=0, rejected_resource_proposals=0,
                      retained_writer_updates=0, native_steps=0, events=0, new_target_dynamic_runs=0)

        def read(C, y, *, gains, B=B0):
            counts['complete_source_reads'] += 1
            g, chi, kh, kah = gains
            parent = next(i for i, row in enumerate(B) if sum(bool(v) for v in row) == 4)
            leaves = [i for i in range(5) if i != parent]
            assert len(set(C[i] for i in leaves)) == 1 and len(set(y)) == 1
            assert abs(sum(C)-9) < tol and min(C) > 0 and -b <= y[0] <= 0
            x = C[parent]-C[leaves[0]]
            assert 0 <= x < 9
            w = y[0].exp()
            I = tuple(tuple(D(i == j) for j in range(4)) for i in range(4))
            BT = tuple(zip(*B)); d = mv(BT, C)

            def star(flat):
                return tuple(tuple(sum(D(bool(row[i] and row[j])) for row in B)*flat[i]*flat[j]/2
                                   for j in range(4)) for i in range(4))

            def stage(H):
                stiffness = mv(B, tuple(w*z for z in d))
                delta = tuple(tuple(z-r for z, r in zip(row, ref)) for row, ref in zip(H, I))
                geom = mv(B, mv(delta, d))
                phi = tuple(s-D(19)/4*c+kah*z for s, c, z in zip(stiffness, C, geom))
                v = tuple(-w*z for z in mv(BT, phi))
                what = tuple((-g*z*z/2).exp() for z in v)
                q = tuple((w-hat)/(w+hat) for hat in what)
                J = tuple(z/(1-chi*t) for z, t in zip(v, q))
                r = tuple(chi*t*j for t, j in zip(q, J))
                flat = solve(H, r)
                assert min(what) > D('0.5') and max(map(abs, q)) < dec(bounds['contrast_cap'])
                assert max(map(abs, v)) < dec(bounds['corrector_component_upper'])
                return dict(baseline=v, W_hat=what, contrast=q, current=J, structural_flat=flat)

            pred = stage(I)
            S = star(pred['structural_flat'])
            H = tuple(tuple(v+kh*s for v, s in zip(row, other)) for row, other in zip(I, S))
            corr = stage(H)
            regenerated = star(corr['structural_flat'])
            residual_squared = sum((kh*(a-z))**2 for row, other in zip(S, regenerated) for a, z in zip(row, other))
            assert residual_squared <= dec(bounds['residual_upper'])**2
            activities = tuple(-v*j for v, j in zip(B[parent], corr['current']))
            assert len(set(activities)) == 1

            # Independent symmetric scalar reconstruction, not a matrix self-comparison.
            v0 = w*(5*w-D(19)/4)*x
            q0 = (w-(-g*v0*v0/2).exp())/(w+(-g*v0*v0/2).exp())
            f0 = chi*q0*v0/(1-chi*q0)
            v1 = v0+D(25)/2*kah*kh*w*x*f0*f0
            q1 = (w-(-g*v1*v1/2).exp())/(w+(-g*v1*v1/2).exp())
            selected = v1/(1-chi*q1)
            assert abs(activities[0]-selected) < tol
            assert abs(-B[parent][0]*pred['baseline'][0]-v0) < tol
            assert abs(-B[parent][0]*corr['baseline'][0]-v1) < tol
            assert selected+tol >= dec(bounds['selected_current_over_concentration_lower'])*x
            return dict(C=C, log_W=y, concentration=x, predictor=pred, H1=H, corrector=corr,
                        inward_activity=selected, activity_variance_all_partitions=D(0),
                        residual_frobenius_squared=residual_squared, scalar_oracle_matches=True)

        trajectories = {}
        enabled = (gamma, D('0.5'), D(1), D(1))
        for name, y0, gains in [('enabled', -D(1)/512, enabled),
                                ('zero_channel', D(0), (D(0),)*4)]:
            C, y = (D(1),)*4+(D(5),), (y0,)*4
            rows = []
            for attempt in range(1, 8):
                row = read(C, y, gains=gains)
                candidate = tuple(c-dt*f for c, f in zip(C, mv(B0, row['corrector']['current'])))
                assert abs(sum(candidate)-9) < tol
                row.update(attempt=attempt, proposed_C=candidate)
                if min(candidate) <= 0:
                    counts['rejected_resource_proposals'] += 1
                    row.update(disposition='resource_domain_exit_no_update', retained_writer_executed=False,
                               retained_C_after=C, retained_log_W_after=y)
                    rows.append(row)
                    break
                new_y = tuple(old/2-gains[0]*j*j/4 for old, j in zip(y, row['corrector']['current']))
                assert all(-b <= z <= 0 for z in new_y)
                if name == 'enabled':
                    assert new_y != y
                    assert row['corrector']['current'] != row['predictor']['current']
                else:
                    exact_x = dec(4*F(37, 32)**attempt)
                    assert abs(candidate[4]-candidate[0]-exact_x) < tol
                    assert new_y == (D(0),)*4
                C, y = candidate, new_y
                counts['positive_ordinary_updates'] += 1
                counts['retained_writer_updates'] += 1
                row.update(disposition='positive_mathematical_update', retained_writer_executed=True,
                           retained_C_after=C, retained_log_W_after=y)
                rows.append(row)
            assert rows[-1]['disposition'] == 'resource_domain_exit_no_update'
            trajectories[name] = rows
        assert len(trajectories['zero_channel']) == 6

        homogeneous = read((D(9)/5,)*5, (-D(1)/512,)*4, gains=enabled)
        assert homogeneous['inward_activity'] == 0
        assert homogeneous['corrector']['current'] == (D(0),)*4
        # Read-only homogeneous control: do not count an unexecuted writer.
        homogeneous['predicted_history_update'] = tuple(y/2 for y in homogeneous['log_W'])

        original = trajectories['enabled'][0]
        vp, ep, signs = (4, 2, 0, 3, 1), (2, 0, 3, 1), (-1, 1, -1, 1)
        B = tuple(tuple(B0[i][j]*s for j, s in zip(ep, signs)) for i in vp)
        moved = read(tuple(original['C'][i] for i in vp), tuple(original['log_W'][i] for i in ep), gains=enabled, B=B)
        assert abs(moved['inward_activity']-original['inward_activity']) < tol
        for stage in ('predictor', 'corrector'):
            assert max(abs(v-original[stage]['current'][i]*s) for v, i, s in zip(moved[stage]['current'], ep, signs)) < tol
        proposed = tuple(c-dt*v for c, v in zip(moved['C'], mv(B, moved['corrector']['current'])))
        assert max(abs(v-original['proposed_C'][i]) for v, i in zip(proposed, vp)) < tol
        return stringify(dict(precision=96, certified_rounding_enclosure=False, counts=counts,
            trajectories=trajectories, homogeneous_read=homogeneous,
            signed_coordinate_read=moved, coordinate_action=dict(vertex_order=vp, edge_order=ep, signs=signs),
            no_rejected_state_is_committed=True, no_fission_guard_implemented=True))


def run():
    prior_path = REFS/'ATCPartitionOSFeedbackCertificate.json'
    prior = json.loads(prior_path.read_text())
    expected = '76e5ece4e49a64b73d53f61b198ac2117474bbb3c9b1416929aeadcd525c85c8'
    assert prior['record_digest'] == expected == sha(canonical({k:v for k,v in prior.items() if k != 'record_digest'}))
    for binding in prior['source_bindings']:
        assert sha((ROOT/binding['path']).read_bytes()) == binding['sha256'], binding['path']
    bounds = exact_bounds()
    energy = energy_checks(prior)
    diagnostics = finite_continuations(bounds)
    side = INV/'tools/exploratory-side-tool'
    sys.path.insert(0, str(side/'tool/src'))
    from grcv4_explorer.a_initializer import load_current_forensic_context
    from grcv4_explorer.forensic import contract_provenance
    ctx = load_current_forensic_context(ROOT, side)
    for ref in prior['authority_trace_refs']:
        old = json.loads((ROOT/ref['record_path']).read_text())
        assert old['record_digest'] == ref['record_digest'] == sha(canonical({k:v for k,v in old.items() if k != 'record_digest'}))
        value = old
        for part in ref['json_pointer'].strip('/').split('/'):
            value = value[int(part)] if isinstance(value, list) else value[part]
        assert canonical(contract_provenance(ctx, ref['query']['contract_id'])) == canonical(value)
    traces = [contract_provenance(ctx, id_) for id_ in ('D10.2-EC-PARENT-CORE-INCIDENCE-CONTINUITY',
                                                     'D10.2-EC-PARENT-A-WRITER-TARGET')]
    assert all(t['rows'][0]['payload']['support_disposition'] == 'indeterminate_requires_review' for t in traces)
    paths = {ROOT/b['path'] for b in prior['source_bindings']}
    paths.update((Path(__file__).resolve(), prior_path, INV/'decisions/ATC1CausalBoundaryProposal.md'))
    record = stringify(dict(schema='grcv4_atc_unsplit_viability_certificate_v1',
        status='passed_conditional_viability_bounds_and_energy_ambiguity_checks',
        scientific_status='proposed_conditional_mathematics_pending_independent_review',
        predecessor=dict(path=prior_path.relative_to(ROOT).as_posix(), record_digest=expected),
        authority_trace_refs=prior['authority_trace_refs'], authority_traces=traces,
        exact_bounds=bounds, reference_energy=energy, decimal_diagnostics=diagnostics,
        scope=dict(candidate='A', realization='one-pass OS', potential_derivative='p(c)=19c/4',
            eta=1, kappa_c=1, alpha=0, beta=0, zeta_A=1, carrier=None, W_floor='1/2',
            gamma=['0','1/65536'], chi_A=['0','1/2'], kappa_H=['0','1'], kappa_Ah=['0','1'],
            graph='unit-reference four-leaf simple star', charge=9,
            source_C='(r,r,r,r,s), r=(9-x)/5, s=(9+4*x)/5, 0<x<9',
            initial_C=[1,1,1,1,5], log_W='uniform y in [-1/256,0]',
            dt='1/8', tau_A='(1/8)/log(2)',
            general_dt_extension='same fixed tau_A, writer convexity for every rho=1-exp(-dt/tau_A) in (0,1)',
            positive_resource_requirement='declared research continuation domain, not universal V4 authority',
            reference_H0='identity', reference_H1='identity', K4_adapter='identity on normalized common star-tensor coordinates',
            no_native_profile_admission=True, no_K0_schedule_change=True),
        inherited_target_result=dict(source='same s=5 prestate, not a later post-beat source',
            supplied_22='positive full-state return in the reviewed gain box',
            supplied_13='expanding mode and positive first-step expansion; not absence of every possible continuation',
            new_target_runs=0, mechanically_selected_partition=False),
        claim_ceiling=['loss of indefinite positive closed fixed-topology continuation in this declared family',
            'not an empty instantaneous read set, a new instability onset or all-family necessity',
            'uniform source activity has zero variance even along the failing continuation',
            'symmetry and unstable concentration mode do not induce a binary half-edge partition',
            'cross-topology energy offset requires additional constitutive authority',
            'not an autonomous split mechanism, native event, target search or accepted claim'],
        source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p.read_bytes())) for p in sorted(paths)],
        production_changes=False))
    record['record_digest'] = sha(canonical(record))
    return record


if __name__ == '__main__':
    print(json.dumps(run(), sort_keys=True, separators=(',', ':'), allow_nan=False))

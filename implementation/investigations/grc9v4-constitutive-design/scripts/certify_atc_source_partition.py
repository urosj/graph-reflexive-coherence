#!/usr/bin/env python3
"""Source-only symmetry/partition mathematics; no target, writer or event.

The variance rule is a proposed consumer, not accepted refinement authority.
Exact combinatorics/bounds prove the stated scope. Decimal96 source reads
are diagnostics, not certified rounding or native conformance.
"""
from decimal import Decimal as D, localcontext
from fractions import Fraction as F
from itertools import permutations, product
import json
from pathlib import Path
import sys

from certify_atc_os_geometry_feedback import canonical, mv, sha, solve, stringify

ROOT = Path(__file__).resolve().parents[4]
INV = ROOT/'implementation/investigations/grc9v4-constitutive-design'
REFS = INV/'evidence/autonomous-topology-change'
E = frozenset(range(4))


def bipartitions():
    # One representative of each unordered pair. Index 0 is only a duplicate
    # elimination convention: every partition is scored, never first-wins.
    return tuple(frozenset((block, E-block)) for mask in range(1, 16, 2)
                 if (block := frozenset(i for i in E if mask & (1 << i))) != E)


PARTITIONS = bipartitions()


def score(activities, partition):
    return sum(sum((activities[i]-sum(activities[j] for j in block)/len(block))**2
                   for i in block) for block in partition)


def choose(activities):
    if not isinstance(activities, tuple) or len(activities) != 4 or any(type(v) is not F for v in activities):
        raise ValueError('four exact rational activities required')
    if min(activities) <= 0:
        return dict(state='outside_proposed_partition_domain', minimizers=frozenset(),
                    reason='not four strict inflows; not a no-event certificate')
    values = {p: score(activities, p) for p in PARTITIONS}
    minimum = min(values.values())
    winners = frozenset(p for p, v in values.items() if v == minimum)
    gap = min(v-minimum for p, v in values.items() if p not in winners) if len(winners) < 7 else F(0)
    return dict(state='resolved' if len(winners) == 1 else 'unresolved',
                minimizers=winners, minimum=minimum, separation_to_nonminimizers=gap,
                # Several tied winners have zero uniqueness margin regardless
                # of separation from the other candidates.
                uniqueness_gap=gap if len(winners) == 1 else F(0))


def permute_partition(p, action):
    return frozenset(frozenset(action[i] for i in block) for block in p)


def partition_payload(p):
    return sorted([sorted(block) for block in p])


def selection_payload(r):
    return {**{k: stringify(v) for k, v in r.items() if k != 'minimizers'},
            'minimizers': sorted(partition_payload(p) for p in r['minimizers'])}


def exact_checks():
    actions = tuple(permutations(range(4)))
    assert len(set(PARTITIONS)) == 7
    orbits = {p: frozenset(permute_partition(p, action) for action in actions) for p in PARTITIONS}
    assert sorted(set(len(v) for v in orbits.values())) == [3, 4]
    assert all(len(v) > 1 for v in orbits.values())  # No S4-fixed partition.
    normalized_star = tuple(tuple(F(1) if i == j else F(1, 2) for j in range(4)) for i in range(4))
    assert mv(normalized_star, (F(1),)*4) == (F(5, 2),)*4
    contrast_basis = [(F(1), F(-1), F(0), F(0)),
                      (F(0), F(1), F(-1), F(0)),
                      (F(0), F(0), F(1), F(-1))]
    for vector in contrast_basis:
        assert mv(normalized_star, vector) == tuple(v/2 for v in vector)
    cases = {
        'symmetric': (F(1),)*4,
        'two_plus_two': (F(1), F(1), F(2), F(2)),
        'one_plus_three': (F(2), F(1), F(1), F(1)),
        'asymmetric_tie': (F(1), F(2), F(2), F(3)),
        'four_distinct': (F(1), F(2), F(3), F(4)),
    }
    results = {name: choose(a) for name, a in cases.items()}
    assert len(results['symmetric']['minimizers']) == 7
    assert results['two_plus_two']['uniqueness_gap'] == F(2, 3)
    assert results['one_plus_three']['uniqueness_gap'] == F(1, 2)
    assert len(results['asymmetric_tie']['minimizers']) == 2
    assert results['asymmetric_tie']['uniqueness_gap'] == 0
    assert results['four_distinct']['state'] == 'resolved'
    covariance_count = 0
    for name, values in cases.items():
        for action in actions:
            moved = [F(0)]*4
            for old, new in enumerate(action):
                moved[new] = values[old]
            expected = frozenset(permute_partition(p, action) for p in results[name]['minimizers'])
            for signs in product((-1, 1), repeat=4):
                # Canonical incident edges point toward parent (B_parent=-1).
                incidence_row = tuple(-s for s in signs)
                oriented_J = tuple(s*v for s, v in zip(signs, moved))
                inward = tuple(-b*j for b, j in zip(incidence_row, oriented_J))
                assert choose(inward)['minimizers'] == expected
                covariance_count += 1
        assert choose(tuple(3*v+7 for v in values))['minimizers'] == results[name]['minimizers']
    # Exact bounded data-error controls; not claims these perturbed activities
    # have been realized by a native source.
    noise_count = 0
    for name in ('two_plus_two', 'one_plus_three'):
        for signs in product((-1, 1), repeat=4):
            error = tuple(F(s, 20) for s in signs)
            assert sum(v*v for v in error) == F(1, 100)
            changed = tuple(v+e for v, e in zip(cases[name], error))
            assert choose(changed)['minimizers'] == results[name]['minimizers']
            noise_count += 1
    assert 4*F(1, 10)+2*F(1, 10)**2 == F(21, 50) < F(1, 2) < F(2, 3)
    invalid_count = 0
    for value in [(), (F(1),)*3, (F(1),)*5, [F(1)]*4,
                  (True, F(1), F(1), F(1)), (float('nan'), F(1), F(1), F(1))]:
        try:
            choose(value)
        except ValueError:
            invalid_count += 1
        else:
            raise AssertionError('malformed partition input admitted')
    for values in ((F(0),)*4, (F(-1), F(1), F(1), F(1))):
        assert choose(values)['state'] == 'outside_proposed_partition_domain'

    # All-positive current-source cube; u lives in the zero-sum leaf subspace.
    b, radius, gamma, chi, Q = F(1, 256), F(1, 64), F(1, 65536), F(1, 2), F(1, 256)
    denominator = 1-chi*Q
    read_ratio = chi*Q/denominator
    jmax, dmax, anorm, kmax = F(17, 8), F(9), F(5), F(4)
    kmin = (1-b)*F(15, 4)
    baseline_min = 4*(1-b)*(5*(1-b)-F(19, 4))-kmax*radius
    geom = anorm*dmax*(read_ratio*jmax)**2
    assert baseline_min-geom > 0
    activity_min = (baseline_min-geom)/(1+chi*Q)
    assert (3/denominator)/10 < activity_min
    assert (b+gamma*jmax**2/2)/2 < Q
    assert jmax+geom < 3
    assert (b+gamma*9/2)/2 < Q
    assert gamma*9/2 < b < F(1, 2)
    t_exact = chi*Q/denominator+chi*gamma*9/(2*denominator**2)
    t = F(1, 500)
    assert t_exact < t
    G = anorm*(2*read_ratio*jmax*t*kmax*dmax+(read_ratio*jmax)**2)
    derivative_error = G+t*(kmax+G)
    separation = kmin-derivative_error
    assert separation > F(37, 10)
    residual = (read_ratio*jmax)**2+(chi*Q*3/denominator)**2
    assert residual < F(1, 512)
    return dict(
        enumeration=dict(unordered_binary_partitions=7, S4_size=24,
            one_plus_three_orbit_size=4, two_plus_two_orbit_size=3, fixed_partitions=0,
            covariance_checks=covariance_count, activity_noise_corners=noise_count,
            malformed_rejections=invalid_count, outside_domain_checks=2),
        symmetric_geometry=dict(normalized_star=normalized_star, uniform_eigenvalue=F(5, 2),
            contrast_eigenvalue=F(1, 2), contrast_multiplicity=3,
            preferred_contrast_direction=False),
        exact_cases={name: dict(activities=stringify(a), selection=selection_payload(results[name])) for name, a in cases.items()},
        source_bounds=dict(log_radius=b, leaf_deviation_radius=radius, gamma_max=gamma,
            chi_max=chi, contrast_cap=Q, denominator_lower=denominator,
            predictor_current_norm_upper=jmax, edge_contrast_norm_upper=dmax,
            baseline_component_lower=baseline_min, geometry_baseline_error_upper=geom,
            corrector_baseline_component_lower=baseline_min-geom,
            selected_inward_activity_lower=activity_min,
            read_derivative_error_upper=t_exact, read_derivative_majorant=t,
            geometry_derivative_upper=G, selected_derivative_error_upper=derivative_error,
            baseline_leaf_slope_lower=kmin, strict_activity_separation_lower=separation,
            residual_upper=residual, research_tolerance=F(1, 512)),
        robustness=dict(score_error_difference_upper='4*||a-mean(a)||_2*epsilon+2*epsilon^2',
            two_level_22_gap_coefficient=F(2, 3), two_level_13_gap_coefficient=F(1, 2),
            certified_error_radius='D/10, where D is the exact activity-level separation',
            requires_perturbed_strict_inflow_domain=True,
            normalized_error_bound=F(21, 50), no_uniform_margin_at_symmetry=True))


def finite_reads(bounds):
    with localcontext() as ctx:
        ctx.prec = 96
        dec = lambda f: D(F(f).numerator)/D(F(f).denominator)
        gamma, chi = dec(bounds['gamma_max']), dec(bounds['chi_max'])
        tol = D('1e-80')
        B0 = tuple(tuple(D(i == e)-D(i == 4) for e in range(4)) for i in range(5))
        I = tuple(tuple(D(i == j) for j in range(4)) for i in range(4))
        y0 = (-D(1)/512,)*4
        count = 0

        def star(flat, B):
            return tuple(tuple(sum(D(bool(row[i] and row[j])) for row in B)*flat[i]*flat[j]/2
                               for j in range(4)) for i in range(4))

        def stage(C, y, B, H):
            BT = tuple(zip(*B)); w = tuple(v.exp() for v in y); d = mv(BT, C)
            stiffness = mv(B, tuple(a*v for a, v in zip(w, d)))
            delta = tuple(tuple(a-b for a, b in zip(row, ref)) for row, ref in zip(H, I))
            phi_geom = mv(B, mv(delta, d))
            phi = tuple(s-D(19)/4*c+g for s, c, g in zip(stiffness, C, phi_geom))
            v = tuple(-a*z for a, z in zip(w, mv(BT, phi)))
            what = tuple((-gamma*z*z/2).exp() for z in v)
            q = tuple((a-b)/(a+b) for a, b in zip(w, what))
            J = tuple(z/(1-chi*c) for z, c in zip(v, q))
            read = tuple(chi*c*j for c, j in zip(q, J))
            flat = solve(H, read)
            assert min(what) > D('0.5') and max(map(abs, q)) < dec(bounds['contrast_cap'])
            assert max(abs(a-b) for a, b in zip(mv(H, flat), read)) < tol
            return dict(baseline=v, W_hat=what, contrast=q, current=J, structural_flat=flat)

        def source_read(C, y, B):
            nonlocal count
            count += 1
            assert len(C) == 5 and len(y) == 4 and sum(C) == 9
            assert len(set(y)) == 1 and -dec(bounds['log_radius']) <= y[0] <= 0
            parent = next(i for i, row in enumerate(B) if sum(bool(v) for v in row) == 4)
            assert C[parent] == 5
            assert all(abs(c-1) <= dec(bounds['leaf_deviation_radius']) for i, c in enumerate(C) if i != parent)
            pred = stage(C, y, B, I)
            S = star(pred['structural_flat'], B)
            H = tuple(tuple(a+b for a, b in zip(row, other)) for row, other in zip(I, S))
            corr = stage(C, y, B, H)
            regen = star(corr['structural_flat'], B)
            defect = tuple(tuple(a-b for a, b in zip(row, other)) for row, other in zip(S, regen))
            assert sum(v*v for row in defect for v in row) < dec(bounds['research_tolerance'])**2
            activities = tuple(-b*j for b, j in zip(B[parent], corr['current']))
            assert min(activities) > 0
            selection = choose(tuple(F(a) for a in activities))
            return dict(C=C, log_W=y, predictor=pred, H1=H, corrector=corr,
                split_defect=defect, inward_activities=activities, selection=selection_payload(selection))

        patterns = {'symmetric': (D(0),)*4}
        expected = {}
        for other in (1, 2, 3):
            block = frozenset((0, other))
            name = f'pair_0_{other}'
            patterns[name] = tuple(D(1 if i in block else -1)/64 for i in range(4))
            expected[name] = frozenset((block, E-block))
        patterns['one_plus_three'] = (D(3)/256, -D(1)/256, -D(1)/256, -D(1)/256)
        expected['one_plus_three'] = frozenset((frozenset((0,)), frozenset((1, 2, 3))))
        rows = {}
        for name, u in patterns.items():
            C = tuple(1+v for v in u)+(D(5),)
            row = source_read(C, y0, B0)
            # Independent reduced-star scalar computation of the geometry
            # baseline, separate from incidence/Hodge multiplication above.
            w = y0[0].exp(); a = D(19)/4
            baselines = tuple(4*w*(5*w-a)+w*(a-w)*v for v in u)
            q = tuple((w-(-gamma*v*v/2).exp())/(w+(-gamma*v*v/2).exp()) for v in baselines)
            f = tuple(chi*c*v/(1-chi*c) for c, v in zip(q, baselines))
            d = tuple(-4+v for v in u)
            dot = sum(a*b for a, b in zip(f, d))
            Sd = tuple((a*a*b+a*dot)/2 for a, b in zip(f, d))
            rebuilt = tuple(v-w*(s+sum(Sd)) for v, s in zip(baselines, Sd))
            assert max(abs(a-b) for a, b in zip(rebuilt, row['corrector']['baseline'])) < tol
            assert row['corrector']['current'] != row['predictor']['current']
            row['reduced_star_oracle_matches'] = True
            if name == 'symmetric':
                assert len(set(row['inward_activities'])) == 1
                assert len(row['selection']['minimizers']) == 7
            else:
                assert row['selection']['state'] == 'resolved'
                assert row['selection']['minimizers'] == [partition_payload(expected[name])]
                gap = max(row['inward_activities'])-min(row['inward_activities'])
                assert gap >= dec(bounds['strict_activity_separation_lower'])*(max(u)-min(u))
                row['activity_gap'] = gap
                row['certified_activity_error_radius_lower'] = dec(bounds['strict_activity_separation_lower'])*(max(u)-min(u))/10
            rows[name] = row
        # Each domain case was a present read, not an ordinary update.
        action_rows = []
        for name in ('pair_0_1', 'one_plus_three'):
            vp, ep, signs = (4, 2, 0, 3, 1), (2, 0, 3, 1), (-1, 1, -1, 1)
            B = tuple(tuple(B0[i][j]*s for j, s in zip(ep, signs)) for i in vp)
            original = rows[name]
            changed = source_read(tuple(original['C'][i] for i in vp), y0, B)
            assert max(abs(v-original['corrector']['current'][i]*s)
                       for v, i, s in zip(changed['corrector']['current'], ep, signs)) < tol
            inverse = {old: new for new, old in enumerate(ep)}
            expected_moved = permute_partition(expected[name], inverse)
            assert changed['selection']['minimizers'] == [partition_payload(expected_moved)]
            for i, old_i in enumerate(ep):
                for j, old_j in enumerate(ep):
                    assert abs(changed['H1'][i][j]-signs[i]*signs[j]*original['H1'][old_i][old_j]) < tol
            action_rows.append(dict(case=name, vertex_order=vp, edge_order=ep, signs=signs,
                                   selected=changed['selection'], passed=True))
        assert count == 7
        return stringify(dict(precision=96, certified_rounding_enclosure=False,
            exact_selector_on_represented_decimal_inputs=True,
            mathematical_domain_proved_separately=True, source_reads=rows,
            coordinate_actions=action_rows, complete_present_reads=count,
            ordinary_steps=0, retained_writes=0, target_reads=0, topology_events=0,
            native_steps=0, trajectory_campaigns=0))


def run():
    predecessor_path = REFS/'ATCPartitionOSFeedbackCertificate.json'
    prior = json.loads(predecessor_path.read_text())
    expected = '76e5ece4e49a64b73d53f61b198ac2117474bbb3c9b1416929aeadcd525c85c8'
    assert prior['record_digest'] == expected == sha(canonical({k: v for k, v in prior.items() if k != 'record_digest'}))
    for binding in prior['source_bindings']:
        assert sha((ROOT/binding['path']).read_bytes()) == binding['sha256'], binding['path']
    exact = exact_checks()
    finite = finite_reads(exact['source_bounds'])
    side = INV/'tools/exploratory-side-tool'
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
    paths = {Path(__file__).resolve(), predecessor_path,
        INV/'scripts/certify_atc_os_geometry_feedback.py', INV/'scripts/certify_atc_partition_os_feedback.py',
        INV/'decisions/ATC1CausalBoundaryProposal.md', INV/'decisions/ATCSourceFissionProposal.md',
        ROOT/'specs/grc-v4-spec.md', INV/'drafts/2026-09-GRC-V4.md',
        side/'tool/src/grcv4_explorer/forensic.py', side/'tool/src/grcv4_explorer/a_initializer.py'}
    record = stringify(dict(schema='grcv4_atc_source_partition_certificate_v1',
        status='passed_exact_symmetry_bounds_and_source_diagnostics',
        scientific_status='proposed_mathematics_and_partition_hypothesis_pending_independent_review',
        proposed_rule='ATC-PARTITION-SOURCE-ACTIVITY-VARIANCE-v1_not_runtime_registered',
        predecessor=dict(path=predecessor_path.relative_to(ROOT).as_posix(), record_digest=expected),
        authority_trace_refs=prior['authority_trace_refs'],
        scope=dict(graph='degree-four simple source star', source_C='(1+u0,...,1+u3,5), sum(u)=0, |u_i|<=1/64',
            potential_derivative='p(c)=19c/4', eta=1, kappa_c=1,
            realization='one-pass OS present read; no continuity or retained writer invoked',
            gamma=['0', '1/65536'], chi_A=['0', '1/2'], kappa_H=['0', '1'], kappa_Ah=['0', '1'],
            alpha=0, beta=0, zeta_A=1, log_W='uniform y in [-1/256,0]', W_floor='1/2',
            reference_H0='identity', reference_H1='identity', reference_weights='ones',
            K4_adapter='identity on normalized common star-tensor coordinates', carrier=None,
            proposed_input='four strict inward activities a_e=-B_parent,e J_e from selected source read',
            no_target_filter=True, no_child_ordering=True, no_automatic_event=True),
        exact_checks=exact, decimal_diagnostics=finite,
        source_bindings=[dict(path=p.relative_to(ROOT).as_posix(), sha256=sha(p.read_bytes())) for p in sorted(paths)],
        claim_ceiling=['no deterministic equivariant singleton partition at the fully S4-symmetric source',
            'source activity variance is a proposed physical grouping criterion, not a derived fission necessity',
            'nonzero source resource differences survive the declared coupled source read and can give a unique partition',
            'equal activity alone is not full-source symmetry; discarded source information may matter elsewhere',
            'no target viability, onset, spontaneous asymmetry formation, all-family or native topology closure'],
        production_changes=False))
    record['record_digest'] = sha(canonical(record))
    return record


if __name__ == '__main__':
    print(json.dumps(run(), sort_keys=True, separators=(',', ':'), allow_nan=False))

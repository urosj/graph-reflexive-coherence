#!/usr/bin/env python3
"""Bounded successor: preserve old W, distinguish pressure from funding.

Investigation-local mathematics only. The reviewed HRESET checker/certificate
remain unchanged. No native initializer, owner, target search or claim admission.
"""
from decimal import Decimal as D, localcontext
from fractions import Fraction as F
import json
from pathlib import Path

import certify_atc_localized_sector_fission as base
from certify_atc_os_geometry_feedback import canonical, mv, sha, stringify

ROOT, INV, REFS = base.ROOT, base.INV, base.REFS
A, H = base.A, base.H
PREDECESSOR = '66e7faa8899da3ab0aa636a5f943fcc97cd1451adeb2ff0a93cc09cd96cab0af'


def prescribe(n, edges, C, W):
    """Adapt the reviewed source-only diagnostics, not its funding-filtered vote.

    A certified obstructed locus remains present even if its transfer is blocked.
    Selection precedes funding: a funded runner-up cannot bypass another locus.
    These are research statuses, not additions to the accepted native K0 schema.
    """
    prior = base.prescribe(n, edges, C, W)
    if 'diagnostics' not in prior:
        return dict(prior, obstruction_status='undetermined',
                    decomposition_status='undetermined', transfer_admission='not_reached')
    rows, candidates, ambiguous = [], [], False
    for diagnostic in prior['diagnostics']:
        row = dict(diagnostic, obstruction_status='not_certified',
                   decomposition_status='not_reached', transfer_admission='not_reached')
        reason = row['reason']
        if reason in ('response_partition_unresolved', 'within_sector_resource_mismatch'):
            ambiguous = True
            row.update(obstruction_status='undetermined', decomposition_status='unresolved')
        elif reason in ('active_localized_sector_fission', 'child_funding_not_strict'):
            parent = row['parent']
            es = tuple(e for e, edge in enumerate(edges) if parent in edge)
            weights = sorted({W[e] for e in es})
            blocks = [tuple(e for e in es if W[e] == w) for w in weights]
            activities = [sum(row['inward'][e] for e in block) for block in blocks]
            k = round(base.GRID*activities[0]/sum(activities))
            shares = (F(k, base.GRID), F(base.GRID-k, base.GRID))
            resources = [C[next(v for v in edges[block[0]] if v != parent)] for block in blocks]
            margins = tuple(s*C[parent]-r for s, r in zip(shares, resources, strict=True))
            candidates.append(dict(parent=parent, blocks=blocks, shares=shares, k=k,
                sector_W=weights, activities=activities, funding_margins=margins))
            row.update(obstruction_status='certified_present', decomposition_status='resolved',
                       transfer_admission='admitted' if min(margins) > 0 else 'blocked',
                       funding_margins=margins)
        else:
            assert reason in ('spectral_certificate_inactive', 'not_four_strict_inflows',
                              'outside_declared_obstruction_cone'), reason
        rows.append(row)
    result = dict(outcome='no_event', prescription=None, diagnostics=rows,
        current=prior['current'], pressure_loci=[p['parent'] for p in candidates],
        obstruction_status='certified_present' if candidates else 'undetermined' if ambiguous else 'not_certified',
        decomposition_status='not_reached', transfer_admission='not_reached')
    if ambiguous or len(candidates) > 1:
        result.update(outcome='unresolved', decomposition_status='unresolved',
                      reason='unresolved_partition_or_multiple_pressure_loci')
    elif candidates:
        selected = candidates[0]
        result.update(prescription=selected, decomposition_status='resolved')
        if min(selected['funding_margins']) <= 0:
            result.update(outcome='blocked_transfer', transfer_admission='blocked',
                          reason='child_funding_not_strict')
        elif n+1 > 16 or len(edges)+1 > 32:
            result.update(outcome='uncertified', transfer_admission='blocked',
                          reason='selected_target_size_bound')
        else:
            result.update(outcome='resolved', transfer_admission='admitted')
    return result


def build(selected, n, edges, current_C, reset_C, current_W, reset_W):
    """Fixed graph/resource recipe, old-edge lineage, new bridge seed only.

    Reuse the reviewed pure topology/T constructor, not its history policy.
    Its all-one history fields are not consumed or published. No physical write
    or initializer call occurs inside that constructor or this research adapter.
    """
    assert selected['outcome'] == 'resolved'
    topology = base.build(selected['prescription'], n, edges, current_C, reset_C)
    target = {key: topology[key] for key in
              ('edges', 'transfer', 'current_C', 'reset_C', 'reference_weights')}
    for role, values in (('current', current_W), ('reset', reset_W)):
        assert len(values) == len(edges) and all(F(1, 2) <= w <= 1 for w in values)
        target[role+'_W'] = tuple(values)+(F(1),)
    target.update(history_disposition='old_edge_lineage_transport_new_bridge_seed_one',
        old_edge_lineage=tuple((e, e) for e in range(len(edges))),
        new_bridge_edge=len(edges), native_initializer_or_owner_called=False)
    return target


def exact_checks():
    B = base.incidence(5, base.SOURCE_EDGES)
    initial = prescribe(5, base.SOURCE_EDGES, base.C0, base.W0)
    assert initial['outcome'] == 'no_event'
    C1 = base.next_C(B, base.C0, initial['current'])
    selected = prescribe(5, base.SOURCE_EDGES, C1, base.W1)
    assert selected['outcome'] == 'resolved'
    assert selected['prescription'] == base.prescribe(5, base.SOURCE_EDGES, C1, base.W1)['prescription']
    assert selected['prescription']['k'] == 30876
    target = build(selected, 5, base.SOURCE_EDGES, C1, base.C0, base.W1, base.W0)
    assert target['current_W'][:-1] == base.W1 != base.W0 == target['reset_W'][:-1]
    assert target['current_C'] != target['reset_C']
    BT = base.incidence(6, target['edges'])
    # Common bounds for BOTH independent roles and every subsequent sqrt write.
    # mu*L(1) <= L(W_n) <= L(1); sqrt(17)<33/8 bounds its nonzero spectrum.
    mu = min(base.W0)
    low, high = mu*F(7, 16), F(73, 16)
    assert F(33, 8)**2 > 17 and 0 < low < high < A
    endpoint_products = (low*(A-low), high*(A-high))
    q_upper = 1-H*min(endpoint_products)  # lambda*(a-lambda) is concave.
    m_lower = 1-H*A*A/4
    assert q_upper == F(1829, 2048) < 1 and m_lower == F(151, 512) > 0
    entries = {}
    for role in ('current', 'reset'):
        C, W = target[role+'_C'], target[role+'_W']
        assert all(mu <= w <= 1 for w in W)
        J = base.read(BT, C, W)
        after = base.next_C(BT, C, J)
        L = base.lap(BT, W)
        M = tuple(tuple(F(i == j)+H*(sum(L[i][k]*L[k][j] for k in range(6))-A*L[i][j])
                        for j in range(6)) for i in range(6))
        assert after == mv(M, C) and min(after) > 0 and sum(after) == 9
        before_norm2 = sum((x-F(3, 2))**2 for x in C)
        norm2 = sum((x-F(3, 2))**2 for x in after)
        assert norm2 < F(2, 5) < F(4, 9)
        assert norm2 <= q_upper*q_upper*before_norm2
        entries[role] = dict(initial_W=W, initial_norm_squared=before_norm2,
            first_current=J, first_C=after, first_min=min(after), first_norm_squared=norm2)
    review_reset = base.next_C(BT, target['reset_C'], base.read(BT, target['reset_C'], base.W1+(F(1),)))
    review_norm2 = sum((x-F(3, 2))**2 for x in review_reset)
    assert entries['reset']['first_norm_squared'] < review_norm2 < F(2, 5)

    blocked_C = (F(1),)*4+(F(11, 10),)
    blocked = prescribe(5, base.SOURCE_EDGES, blocked_C, base.W1)
    assert base.prescribe(5, base.SOURCE_EDGES, blocked_C, base.W1)['outcome'] == 'no_event'
    assert blocked['outcome'] == 'blocked_transfer' and blocked['obstruction_status'] == 'certified_present'
    assert blocked['decomposition_status'] == 'resolved' and blocked['prescription'] is not None
    # No target may be constructed for the blocked prescription.
    try:
        build(blocked, 5, base.SOURCE_EDGES, blocked_C, base.C0, base.W1, base.W0)
    except AssertionError:
        pass
    else:
        raise AssertionError('blocked transfer constructed a target')
    edges2 = base.SOURCE_EDGES+tuple((u+5, v+5) for u, v in base.SOURCE_EDGES)
    controls = dict(blocked_funding=blocked,
        funded_and_unfunded_loci=prescribe(10, edges2, C1+blocked_C, base.W1+base.W1),
        two_unfunded_loci=prescribe(10, edges2, blocked_C+blocked_C, base.W1+base.W1),
        homogeneous=prescribe(5, base.SOURCE_EDGES, (F(9, 5),)*5, base.W1),
        ambiguous_partition=prescribe(5, base.SOURCE_EDGES, base.C0, (F(1),)*4),
        target_size_bound=prescribe(16, base.SOURCE_EDGES, C1+(F(1),)*11, base.W1),
        changed_graph=prescribe(6, target['edges'], target['current_C'], target['current_W']))
    for name in ('funded_and_unfunded_loci', 'two_unfunded_loci'):
        assert controls[name]['outcome'] == 'unresolved' and controls[name]['pressure_loci'] == [4, 9]
        assert controls[name]['prescription'] is None
    assert controls['homogeneous']['outcome'] == controls['changed_graph']['outcome'] == 'no_event'
    assert controls['ambiguous_partition']['outcome'] == 'unresolved'
    assert controls['target_size_bound']['outcome'] == 'uncertified'
    assert controls['target_size_bound']['obstruction_status'] == 'certified_present'
    covariance = []
    for vp in ((4, 0, 1, 2, 3), (2, 3, 0, 1, 4), (1, 3, 4, 0, 2)):
        inv = {old:new for new, old in enumerate(vp)}
        for ep in ((3, 1, 0, 2), (2, 3, 0, 1)):
            for signs in ((1, 1, 1, 1), (-1, 1, -1, 1)):
                edges = tuple(tuple(inv[x] for x in (base.SOURCE_EDGES[e] if s == 1 else base.SOURCE_EDGES[e][::-1]))
                              for e, s in zip(ep, signs, strict=True))
                W, R = tuple(base.W1[e] for e in ep), tuple(base.W0[e] for e in ep)
                cur, rst = tuple(C1[v] for v in vp), tuple(base.C0[v] for v in vp)
                sel = prescribe(5, edges, cur, W)
                assert sel['outcome'] == 'resolved'
                assert vp[sel['prescription']['parent']] == 4
                assert sel['prescription']['shares'] == selected['prescription']['shares']
                assert [set(ep[e] for e in b) for b in sel['prescription']['blocks']] == [set(b) for b in selected['prescription']['blocks']]
                t = build(sel, 5, edges, cur, rst, W, R)
                assert t['current_W'] == W+(F(1),) and t['reset_W'] == R+(F(1),)
                blocked_perm = prescribe(5, edges, tuple(blocked_C[v] for v in vp), W)
                assert blocked_perm['outcome'] == 'blocked_transfer'
                assert vp[blocked_perm['pressure_loci'][0]] == 4
                covariance.append(dict(vertex_order=vp, edge_order=ep, orientation_signs=signs))
    return dict(initial=initial, selected=selected, target=target, entries=entries,
        uniform_bounds=dict(mobility_lower=mu, lambda_lower=low, lambda_upper=high,
            multiplier_lower=m_lower, q_upper=q_upper, radius=F(2, 3), resource_lower=F(5, 6)),
        review_reset_clarification=dict(review_used_current_W=True,
            review_comparator_norm_squared=review_norm2, actual_reset_uses_W0=True),
        controls=controls, covariance_checks=covariance, blocked_target_rejected=True)


def finite_checks(exact):
    """Three changing-history steps per role; proof, not horizon, gives closure."""
    with localcontext() as ctx:
        ctx.prec = 96
        def dec(value):
            value = F(value)
            return D(value.numerator)/D(value.denominator)
        target = exact['target']; B = base.incidence(6, target['edges'])
        a, h, q = dec(A), dec(H), dec(exact['uniform_bounds']['q_upper'])
        tol = D('1e-75'); runs = {}
        for role in ('current', 'reset'):
            C, W = tuple(map(dec, target[role+'_C'])), tuple(map(dec, target[role+'_W']))
            rows = []
            for step in range(1, 4):
                J = base.read(B, C, W, a); after = base.next_C(B, C, J, h)
                L = base.lap(B, W)
                # Independently expand M_n C; unlike HRESET, M changes each step.
                LC = mv(L, C); L2C = mv(L, LC)
                oracle = tuple(c+h*(ll-a*l) for c, ll, l in zip(C, L2C, LC, strict=True))
                assert max(abs(x-y) for x, y in zip(after, oracle, strict=True)) < tol
                norm2 = sum((x-D('1.5'))**2 for x in after)
                assert norm2 <= q*q*sum((x-D('1.5'))**2 for x in C)+tol
                assert norm2 < dec(F(4, 9)) and min(after) > dec(F(5, 6))
                assert abs(sum(after)-9) < tol
                W_after = tuple(w.sqrt() for w in W)
                assert all(dec(F(361, 400)) <= w <= wp <= 1 for w, wp in zip(W, W_after, strict=True))
                if step == 1:
                    assert abs(norm2-dec(exact['entries'][role]['first_norm_squared'])) < tol
                rows.append(dict(step=step, C=C, W=W, current=J, C_after=after,
                                 W_after=W_after, norm_squared_after=norm2))
                C, W = after, W_after
            runs[role] = rows
        return dict(precision=96, interval_certified=False, runs=runs,
            counts=dict(reduced_reads=6, positive_updates=6, history_writes=6, native_steps=0, native_events=0),
            exact_anchor_checks_recorded_separately=True)


def run():
    path = REFS/'ATCLocalizedSectorFissionCertificate.json'
    prior = json.loads(path.read_text())
    assert prior['record_digest'] == PREDECESSOR == sha(canonical({k:v for k,v in prior.items() if k != 'record_digest'}))
    paths = {path, Path(__file__).resolve()}
    for binding in prior['source_bindings']:
        p = ROOT/binding['path']
        assert sha(p.read_bytes()) == binding['sha256'], binding['path']
        paths.add(p)
    exact = exact_checks()
    record = stringify(dict(schema='grcv4_atc_sector_lineage_certificate_v1',
        status='passed_bounded_lineage_preserving_restoration_and_pressure_separation',
        scientific_status='review_corrections_checked_successor_pending_independent_review',
        predecessor=dict(path=path.relative_to(ROOT).as_posix(), record_digest=PREDECESSOR),
        review_scope='reported independent exact_stage and finite_runs execution, not repository forensic run',
        exact=exact, decimal_diagnostics=finite_checks(exact),
        authority='inherited authority ceilings unchanged; no new normative claim or native admission',
        ceilings=['sector-to-site remains a new constitutive postulate, not ordinary V4 authority',
            'prepared history, exact two-sector symmetry, zero read-back, one actual source boundary',
            'lineage/new-bridge history recipe is a research proposal, not an accepted native consumer',
            'funding admission does not prove restoration at every eligible source',
            'no formation, general feedback, repeated fission, all-family or ATC-2 closure'],
        source_bindings=[dict(path=p.relative_to(ROOT).as_posix(), sha256=sha(p.read_bytes())) for p in sorted(paths)],
        production_changes=False, target_search=False))
    record['record_digest'] = sha(canonical(record))
    return record


if __name__ == '__main__':
    print(json.dumps(run(), sort_keys=True, separators=(',', ':'), allow_nan=False))

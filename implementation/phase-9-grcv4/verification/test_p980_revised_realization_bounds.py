"""Research-only CI/PC/CI+PC bounds for the revised D52 parameter package.

One interval tube per candidate encloses every geometry in the declared ball,
not a simulated CI root or a silently reused OS trajectory. Old carrier is fixed
in each root solve. No native evaluator, profile admission or event is executed.
"""
from fractions import Fraction as Q
from dataclasses import replace
import json
import unittest
from unittest.mock import patch

from test_p980_os_effect_witness import (
    IV, PARAMS, HISTORY_OFFSET, RESOURCE_RADIUS, HISTORY_RADIUS,
    IntervalRows, StagedRows, bounds, box, number, endpoint, upper_abs,
    vector, infinity, inverse,
)


GEOMETRY_RADIUS = Q(1, 2**20)
CARRIER_RADIUS = Q(1, 2**22)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def geometry_box(model, radius=GEOMETRY_RADIUS):
    """Entrywise superset of the symmetric/star-supported infinity-norm ball.

    Independent interval entries do not assert an unrestricted matrix domain.
    Analytical inverse/gap bounds below use the actual symmetric norm ball.
    """
    return IV.matrix([[box(Q(i == j), radius if model.mask[i, j] else Q(0))
                       for j in range(len(model.edges))] for i in range(len(model.edges))])


def assert_geometry_ball_covered(model, enclosure, radius):
    """RR-F1 control from the review; derive support from endpoints, not mask.

    Each diagonal extreme and each single symmetric supported pair attains
    +/-radius in the actual norm ball. The independent-entry enclosure must
    cover these coordinates, but need NOT itself satisfy the row-norm bound.
    """
    m = len(model.edges)
    if (m == 0 or getattr(enclosure, 'rows', None) != m
            or getattr(enclosure, 'cols', None) != m or radius <= 0):
        raise AssertionError('invalid geometry enclosure shape/radius')
    ends = [{edge['tail']['node_id'], edge['head']['node_id']}
            for edge in model.edges]
    for i in range(m):
        for j in range(m):
            lower, upper = endpoint(enclosure[i, j], 0), endpoint(enclosure[i, j], 1)
            if lower > upper:
                raise AssertionError('reversed geometry interval')
            center = Q(i == j)
            if ends[i] & ends[j]:
                if lower > center-radius or upper < center+radius:
                    raise AssertionError(f'geometry ball not covered at ({i}, {j})')
            elif lower != 0 or upper != 0:
                raise AssertionError(f'disjoint geometry entry not exactly zero at ({i}, {j})')


def assert_current_frobenius_aggregation(source, squared_bound):
    """RR-F2 control: independent traversal for the declared entry-sum bound.

    This is deliberately not the producer's flattened iteration/upper_abs
    path. A different correlation-aware estimator would need its own proof.
    """
    if (getattr(source, 'rows', 0) <= 0
            or source.rows != getattr(source, 'cols', None)):
        raise AssertionError('source is not a nonempty square matrix')
    expected = Q(0)
    for i in range(source.rows):
        for j in range(source.cols):
            lower, upper = endpoint(source[i, j], 0), endpoint(source[i, j], 1)
            if lower > upper:
                raise AssertionError('reversed source interval')
            expected += max(abs(lower), abs(upper))**2
    if squared_bound != expected:
        raise AssertionError('reported Frobenius bound is not the complete interval-entry square sum')
    return expected


def read_bounds(model, candidate, c, w, radius=GEOMETRY_RADIUS):
    require(candidate in ('A', 'C'), 'unknown candidate')
    require(model.params == PARAMS, 'revised parameter binding mismatch')
    n, m = len(model.nodes), len(model.edges)
    require(c.rows == n and c.cols == 1, 'resource shape mismatch')
    require(0 < radius < Q(1, 2), 'geometry radius outside strict-gap chart')
    require(all(0 <= endpoint(x, 0) <= endpoint(x, 1) <= 4 for x in c),
            'physical resource chart not certified')
    require(m <= 16 and n <= 17, 'graph-size bound exceeded')
    if candidate == 'A':
        require(w is not None and w.rows == m and w.cols == 1, 'history shape mismatch')
        require(all(Q(99, 100) < endpoint(x, 0) <= endpoint(x, 1) < Q(1001, 1000) for x in w),
                'positive history chart not certified')
    else:
        require(w is None, 'Candidate C has no W history')
    h = geometry_box(model, radius)
    assert_geometry_ball_covered(model, h, radius)
    r = model.read(candidate, c, w, h)
    b = model.B.T*c
    bmax, dnorm = infinity(b), infinity(model.D)
    jmax, base = infinity(r['J']), infinity(r['baseline'])
    hinv = 1/(1-radius)
    if candidate == 'A':
        chi, zeta = PARAMS.chi_a, PARAMS.zeta_a
        drive = model.conductance(c, w, r['baseline'])
        q = IV.matrix([(x-g)/(x+g) for x, g in zip(w, drive, strict=True)])
        qmax = infinity(q)
        theta = zeta*chi*qmax
        require(theta < Q(1, 2), 'current inverse margin not certified')
        baseline_lip = infinity(w)*bounds.KAPPA_AH*dnorm*bmax
        # q=(W-G)/(W+G), G=exp(-epsilon*(...+J0^2)/2).
        q_drive = max(upper_abs(2*x/(x+g)**2) for x, g in zip(w, drive, strict=True))
        response_lip = q_drive*infinity(drive)*PARAMS.coefficient*base*baseline_lip
        current_lip = (baseline_lip+zeta*chi*response_lip*jmax)/(1-theta)
        causal = number(chi)*IV.matrix([x*y for x, y in zip(q, r['J'], strict=True)])
        causal_lip = chi*(response_lip*jmax+qmax*current_lip)
    else:
        chi, zeta = PARAMS.chi_c, PARAMS.zeta_c
        e = IV.exp(2*sum(c)/n)
        t = IV.exp(number(bounds.KAPPA_M)*(e-1)/(e+1))
        response = inverse(model.I+t*h*model.D)
        response_norm = infinity(response)
        theta = zeta*chi*response_norm
        require(theta < Q(1, 2), 'current inverse margin not certified')
        baseline_lip = upper_abs(t)*dnorm*bmax
        response_lip = response_norm**2*upper_abs(t)*dnorm
        current_lip = (baseline_lip+zeta*chi*response_lip*jmax)/(1-theta)
        causal = number(chi)*response*r['J']
        causal_lip = chi*(response_lip*jmax+response_norm*current_lip)
    require(theta < Q(1, 2), 'current inverse margin not certified')
    flat = inverse(h)*causal
    flat_max = infinity(flat)
    flat_lip = hinv*causal_lip+hinv**2*infinity(causal)
    mask_norm = max(sum(Q(float(x)) for x in row) for row in model.mask)
    source_lip = 2*zeta*mask_norm*flat_max*flat_lip
    source_norm_squared = sum(upper_abs(x)**2 for x in r['source'])
    return r, dict(source_frobenius_squared=source_norm_squared,
                   source_infinity=infinity(r['source']), current_max=jmax,
                   current_lip=current_lip, source_lip=source_lip,
                   contraction=bounds.KAPPA_H*source_lip,
                   regularity=1-theta, geometry_radius=radius)


def realization_budgets(budget, carrier_radius=CARRIER_RADIUS):
    require(carrier_radius > 0, 'carrier radius must be positive')
    radius, s = budget['geometry_radius'], budget['source_infinity']
    # sqrt(m) <= 4 converts the Frobenius carrier radius to induced infinity.
    images = dict(CI=bounds.KAPPA_H*s,
                  PC=bounds.KAPPA_H*4*carrier_radius,
                  CI_PC=bounds.KAPPA_H*(4*carrier_radius+s))
    require(budget['source_frobenius_squared'] < carrier_radius**2,
            'source does not fit carrier ball')
    require(all(x < radius for x in images.values()), 'geometry image escapes ball')
    require(budget['contraction'] < 1, 'joint root contraction unresolved')
    return images


def carrier_admitted(model, entries, radius=CARRIER_RADIUS):
    """Exact rational domain control; magnitude never replaces tensor type."""
    m = len(model.edges)
    try:
        require(len(entries) == m and all(len(row) == m for row in entries), 'carrier shape mismatch')
        z = [[Q(x) for x in row] for row in entries]
    except (TypeError, OverflowError, ValueError):
        return False
    return (radius > 0 and all(z[i][j] == z[j][i] and (model.mask[i, j] or not z[i][j])
                              for i in range(m) for j in range(m))
            and sum(x*x for row in z for x in row) <= radius**2)


class RevisedRealizationBoundTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        bounds.FixedRowBoundTests.setUpClass()
        source = bounds.FixedRowBoundTests.source
        layout = bounds.FixedRowBoundTests.layouts[-1]
        if layout['request']['target_effective_degree'] != 52:
            raise ValueError('D52 layout binding changed')
        edges, nodes = bounds.normalized_target(layout)
        cls.source = IntervalRows(StagedRows(source['live_node_ids'], source['edges'], PARAMS))
        cls.target = IntervalRows(StagedRows(nodes, edges, PARAMS))

    def test_uniform_geometry_tubes_both_roles(self):
        report = {}
        for candidate in ('A', 'C'):
            for role, center in (('current', Q(3)), ('reset', Q(2))):
                src, dst = self.source, self.target
                desired = {n: center if n == 'source-s' else center+bounds.OUTSIDE_OFFSET for n in src.nodes}
                initial = bounds.preimage(src.edges, desired) if role == 'current' else desired
                c = vector([initial[n] for n in src.nodes], RESOURCE_RADIUS)
                w = vector([1-HISTORY_OFFSET]*len(src.edges), HISTORY_RADIUS) if candidate == 'A' else None
                records = []

                def admit(model, c, w, stage):
                    r, budget = read_bounds(model, candidate, c, w)
                    assert_current_frobenius_aggregation(r['source'], budget['source_frobenius_squared'])
                    images = realization_budgets(budget)
                    # Outward rational reporting ceilings, not rounded output
                    # promoted to proof. Each is checked on every stage box.
                    self.assertLess(budget['source_frobenius_squared'], Q(8, 10**8)**2)
                    self.assertLess(budget['contraction'], Q(2, 10**6))
                    self.assertGreater(budget['regularity'], Q(99998, 100000))
                    records.append(dict(stage=stage, **{k: float(v) for k, v in budget.items()},
                                        images={k: float(v) for k, v in images.items()},
                                        resource_lower=float(min(endpoint(x, 0) for x in c)),
                                        resource_upper=float(max(endpoint(x, 1) for x in c))))
                    return r

                r = admit(src, c, w, 'source')
                if role == 'current':
                    c = c-number(bounds.DT)*src.B*r['J']
                    w = src.write(c, w, r['J']) if w is not None else None
                    # Fresh admission and detection, not the predecessor's OS state.
                    admit(src, c, w, 'source_poststate')
                    row = src.rows(c, w if w is not None else vector([1]*len(src.edges)))[src.index['source-s']]
                    self.assertTrue(all(endpoint(x, 0) > 0 for x in row))
                    self.assertLess(sum(upper_abs(x)**2 for x in row), Q(1, 4))
                lineage = dict(zip((e['edge_id'] for e in src.edges), w, strict=True)) if w is not None else {}
                c = IV.matrix([c[src.index[n]] if n.startswith('outside-') else
                               c[src.index['source-s']]/3 if n.startswith('satellite/') else number(0)
                               for n in dst.nodes])
                w = IV.matrix([lineage.get(e['edge_id'], number(1)) for e in dst.edges]) if w is not None else None
                for k in range(bounds.HORIZON):
                    r = admit(dst, c, w, f'target_{k}')
                    c = c-number(bounds.DT)*dst.B*r['J']
                    w = dst.write(c, w, r['J']) if w is not None else None
                    self.assertGreater(min(endpoint(x, 0) for x in c), bounds.RESOURCE_MARGIN/2)
                    self.assertLess(max(endpoint(x, 1) for x in c), 4)
                # Reconstruction after the last writer is an additional obligation.
                admit(dst, c, w, f'target_{bounds.HORIZON}')
                report[candidate+'_'+role] = records
        type(self).report = report

    def test_geometry_enclosure_coverage(self):
        for graph, model in (('source', self.source), ('target', self.target)):
            m, rho = len(model.edges), GEOMETRY_RADIUS
            enclosure = geometry_box(model)
            assert_geometry_ball_covered(model, enclosure, rho)
            # The full independent-entry box really is larger than the domain.
            # Rejecting it for excess row width would be the wrong control.
            self.assertGreater(infinity(enclosure-model.I), rho)
            variants = dict(identity=model.I.copy(), half_width=geometry_box(model, rho/2),
                            diagonal_only=IV.matrix([[box(Q(i == j), rho if i == j else Q(0))
                                                      for j in range(m)] for i in range(m)]))
            for kind, bad in variants.items():
                with self.subTest(graph=graph, mutation=kind), self.assertRaisesRegex(
                        AssertionError, 'geometry ball not covered'):
                    assert_geometry_ball_covered(model, bad, rho)
            with self.subTest(graph=graph, mutation='support_mask'):
                # A corrupted producer mask must not also corrupt the oracle.
                with patch.object(model, 'mask', model.mask*0):
                    with self.assertRaisesRegex(AssertionError, 'geometry ball not covered'):
                        assert_geometry_ball_covered(model, geometry_box(model), rho)
        model = self.target
        ends = [{e['tail']['node_id'], e['head']['node_id']} for e in model.edges]
        i, j = next((i, j) for i in range(len(ends)) for j in range(len(ends)) if not ends[i] & ends[j])
        bad = geometry_box(model)
        bad[i, j] = box(0, GEOMETRY_RADIUS)
        with self.assertRaisesRegex(AssertionError, 'disjoint geometry entry'):
            assert_geometry_ball_covered(model, bad, GEOMETRY_RADIUS)
        for bad in ([], IV.matrix(0, 0), IV.matrix(1, 2)):
            with self.assertRaisesRegex(AssertionError, 'shape/radius'):
                assert_geometry_ball_covered(model, bad, GEOMETRY_RADIUS)
        with self.assertRaisesRegex(AssertionError, 'shape/radius'):
            assert_geometry_ball_covered(model, geometry_box(model), Q(0))
        bad = geometry_box(model)
        bad[0, 0] = IV.mpf('inf')
        with self.assertRaisesRegex(ValueError, 'nonfinite'):
            assert_geometry_ball_covered(model, bad, GEOMETRY_RADIUS)

    def test_complete_source_frobenius_aggregation(self):
        model = self.target
        c = vector([bounds.resources(model.nodes, Q(3))[n] for n in model.nodes])
        old = {e['edge_id'] for e in self.source.edges}
        w = vector([1-HISTORY_OFFSET if e['edge_id'] in old else 1 for e in model.edges])
        for candidate in ('A', 'C'):
            r, budget = read_bounds(model, candidate, c, w if candidate == 'A' else None)
            assert_current_frobenius_aggregation(r['source'], budget['source_frobenius_squared'])
            false_bound = max(upper_abs(x)**2 for x in r['source'])
            with self.subTest(candidate=candidate), self.assertRaisesRegex(AssertionError, 'complete interval-entry'):
                assert_current_frobenius_aggregation(r['source'], false_bound)
        # Synthetic matrices check aggregation, not physical source admission.
        pair = IV.matrix([[number(1), number(Q(1, 2))], [number(Q(1, 2)), number(1)]])
        self.assertEqual(assert_current_frobenius_aggregation(pair, Q(5, 2)), Q(5, 2))
        for false_bound in (Q(1), Q(2), Q(9, 4)):
            with self.assertRaisesRegex(AssertionError, 'complete interval-entry'):
                assert_current_frobenius_aggregation(pair, false_bound)
        final = IV.matrix(3, 3)
        final[2, 2] = number(2)
        self.assertEqual(assert_current_frobenius_aggregation(final, Q(4)), Q(4))
        with self.assertRaisesRegex(AssertionError, 'complete interval-entry'):
            assert_current_frobenius_aggregation(final, Q(0))
        # Both interval signs must count; do not square only an upper endpoint.
        signed = IV.matrix([[box(-2, 1)]])
        self.assertEqual(assert_current_frobenius_aggregation(signed, Q(9)), Q(9))
        with self.assertRaisesRegex(AssertionError, 'complete interval-entry'):
            assert_current_frobenius_aggregation(signed, Q(1))
        self.assertEqual(assert_current_frobenius_aggregation(IV.matrix(2, 2), Q(0)), Q(0))
        for bad in ([], IV.matrix(0, 0), IV.matrix(1, 2)):
            with self.assertRaisesRegex(AssertionError, 'nonempty square'):
                assert_current_frobenius_aggregation(bad, Q(0))
        with self.assertRaisesRegex(ValueError, 'nonfinite'):
            assert_current_frobenius_aggregation(IV.matrix([[IV.mpf('inf')]]), Q(0))

    def test_tube_rejects_enclosure_and_aggregation_substitutions(self):
        original_box, original_read = geometry_box, read_bounds
        variants = dict(
            identity=lambda model, radius: model.I.copy(),
            diagonal_only=lambda model, radius: IV.matrix([
                [box(Q(i == j), radius if i == j else Q(0)) for j in range(len(model.edges))]
                for i in range(len(model.edges))]),
            half_width=lambda model, radius: original_box(model, radius/2))
        for name, producer in variants.items():
            with self.subTest(mutation=name), patch(__name__+'.geometry_box', producer):
                with self.assertRaisesRegex(AssertionError, 'geometry ball not covered'):
                    self.test_uniform_geometry_tubes_both_roles()

        def false_norm(*args, **kwargs):
            r, budget = original_read(*args, **kwargs)
            return r, dict(budget, source_frobenius_squared=max(upper_abs(x)**2 for x in r['source']))

        # Alter the RETURNED scalar: a check only inside its producer could be
        # bypassed by this mutation. The actual tube consumer must reject it.
        with patch(__name__+'.read_bounds', false_norm):
            with self.assertRaisesRegex(AssertionError, 'complete interval-entry'):
                self.test_uniform_geometry_tubes_both_roles()

    def test_graph_gap_and_parameter_binding(self):
        for model in (self.source, self.target):
            # Verify the connected tree hypothesis needed by the gap bound.
            n, m = len(model.nodes), len(model.edges)
            self.assertEqual(m, n-1)
            self.assertEqual(len(set(model.nodes)), n)
            self.assertEqual(len({e['edge_id'] for e in model.edges}), m)
            seen = {model.nodes[0]}
            while True:
                expanded = seen | {end['node_id'] for e in model.edges
                                   if e['tail']['node_id'] in seen or e['head']['node_id'] in seen
                                   for end in (e['tail'], e['head'])}
                if expanded == seen:
                    break
                seen = expanded
            self.assertEqual(seen, set(model.nodes))
            self.assertGreater(Q(1, n*(n-1)), Q(1, 512))
            self.assertLess(GEOMETRY_RADIUS, Q(1, 2))
        changed = IntervalRows(StagedRows(self.target.nodes, self.target.edges,
                                        replace(PARAMS, chi_c=Q(0))))
        c = vector([1]*len(changed.nodes))
        with self.assertRaisesRegex(ValueError, 'parameter binding'):
            read_bounds(changed, 'C', c, None)
        for candidate, resources, history in (
                ('X', c, None), ('C', vector([1]), None),
                ('C', c, vector([1]*len(changed.edges))),
                ('C', vector([-1]*len(changed.nodes)), None),
                ('A', c, None), ('A', c, vector([0]*len(changed.edges)))):
            with self.subTest(candidate=candidate), self.assertRaises(ValueError):
                read_bounds(self.target, candidate, resources, history)

    def test_carrier_type_ball_and_convex_writer(self):
        model = self.target
        m = len(model.edges)
        zero = [[Q(0)]*m for _ in range(m)]
        self.assertTrue(carrier_admitted(model, zero))
        boundary = [row.copy() for row in zero]
        boundary[0][0] = CARRIER_RADIUS
        self.assertTrue(carrier_admitted(model, boundary))
        too_large = [row.copy() for row in boundary]
        too_large[0][0] += Q(1, 2**60)
        self.assertFalse(carrier_admitted(model, too_large))
        for allowed in (True, False):
            i, j = next((i, j) for i in range(m) for j in range(i+1, m)
                        if bool(model.mask[i, j]) == allowed)
            z = [row.copy() for row in zero]
            z[i][j] = CARRIER_RADIUS/4
            self.assertFalse(carrier_admitted(model, z))  # small but nonsymmetric
            z[j][i] = z[i][j]
            self.assertEqual(carrier_admitted(model, z), allowed)
        for bad in ([], [[0]], [[float('nan')]*m for _ in range(m)],
                    [[float('inf')]*m for _ in range(m)]):
            self.assertFalse(carrier_admitted(model, bad))
        a = IV.exp(-number(bounds.DT))  # tau_PC=1
        self.assertGreater(endpoint(a, 0), 0)
        self.assertLess(endpoint(a, 1), 1)
        # The actual exponential writer therefore is a convex combination;
        # rational endpoints exercise exact equality/zero-duration limits too.
        for weight in (Q(0), Q(1), endpoint(a, 0), endpoint(a, 1)):
            z = [[weight*x+(1-weight)*y for x, y in zip(u, v, strict=True)]
                 for u, v in zip(boundary, zero, strict=True)]
            self.assertTrue(carrier_admitted(model, z))

    def test_realization_budget_boundaries(self):
        b = dict(geometry_radius=GEOMETRY_RADIUS, source_infinity=CARRIER_RADIUS/2,
                 source_frobenius_squared=CARRIER_RADIUS**2/4, contraction=Q(1, 10))
        images = realization_budgets(b)
        self.assertEqual(images['CI_PC'], images['CI']+images['PC'])
        self.assertGreater(images['CI_PC'], images['PC'])
        for changed, message in (
                (dict(b, source_frobenius_squared=CARRIER_RADIUS**2), 'source'),
                (dict(b, geometry_radius=images['CI_PC']), 'image'),
                (dict(b, contraction=Q(1)), 'contraction')):
            with self.subTest(message=message), self.assertRaisesRegex(ValueError, message):
                realization_budgets(changed)
        # The old-carrier contribution is additive, not a second derivative.
        larger = realization_budgets(b, CARRIER_RADIUS*Q(3, 2))
        self.assertGreater(larger['CI_PC'], images['CI_PC'])
        self.assertEqual(larger['CI'], images['CI'])
        zero = dict(b, source_infinity=Q(0), source_frobenius_squared=Q(0), contraction=Q(0))
        self.assertEqual(realization_budgets(zero)['CI'], 0)

    def test_geometry_lipschitz_bounds_against_finite_differences(self):
        model = self.target
        c = vector([bounds.resources(model.nodes, Q(3))[n] for n in model.nodes])
        # Use explicit source edge identities rather than assuming a prefix.
        old_ids = {e['edge_id'] for e in self.source.edges}
        w = vector([1-HISTORY_OFFSET if e['edge_id'] in old_ids else 1 for e in model.edges])
        m = len(model.edges)
        i, j = next((i, j) for i in range(m) for j in range(i+1, m) if model.mask[i, j])
        directions = []
        for signed in (Q(1), Q(-1)):
            d = IV.matrix(m, m)
            d[i, i], d[j, j] = number(signed), number(-signed)
            directions.append(d)
        d = IV.matrix(m, m)
        d[i, j] = d[j, i] = number(1)
        directions.append(d)
        for candidate in ('A', 'C'):
            history = w if candidate == 'A' else None
            _, b = read_bounds(model, candidate, c, history)
            original = model.read(candidate, c, history, model.I)
            for d in directions:
                h = model.I+number(GEOMETRY_RADIUS/2)*d
                perturbed = model.read(candidate, c, history, h)
                distance = infinity(h-model.I)
                self.assertLess(infinity(perturbed['J']-original['J']), b['current_lip']*distance)
                self.assertLess(infinity(perturbed['source']-original['source']), b['source_lip']*distance)
                # Not a solver/ULP certificate: exact-real interval separation
                # establishes that the consumer is not silently disabled here.
                self.assertTrue(any(endpoint(x, 0) > 0 or endpoint(x, 1) < 0
                                    for x in perturbed['J']-original['J']))


if __name__ == '__main__':
    import sys
    reporting = '--report' in sys.argv
    if reporting:
        sys.argv.remove('--report')
    result = unittest.main(exit=False)
    if reporting and result.result.wasSuccessful():
        print(json.dumps({key: dict(
            admitted_stage_boxes=len(rows),
            source_frobenius_squared_upper=max(r['source_frobenius_squared'] for r in rows),
            contraction_upper=max(r['contraction'] for r in rows),
            current_regularity_lower=min(r['regularity'] for r in rows),
            composite_image_upper=max(r['images']['CI_PC'] for r in rows),
            positive_target_resource_lower=min(r['resource_lower'] for r in rows
                                               if r['stage'].startswith('target_') and r['stage'] != 'target_0'),
            final_resource_upper=rows[-1]['resource_upper'],
        ) for key, rows in RevisedRealizationBoundTests.report.items()}, indent=2))
    sys.exit(not result.result.wasSuccessful())

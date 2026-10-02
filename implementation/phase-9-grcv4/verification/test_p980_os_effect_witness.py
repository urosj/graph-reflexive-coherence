"""Separate OS successor: interval neighborhoods and full-output effect gates.

Research only. Unchanged D52 topology, resource map, ordinary duration and
binary64 arithmetic. Old defaults/loss regressions remain in their own owner.
The interval evaluator encloses the entire displayed constitutive formulas;
it never treats a current-block residual as a whole-evaluation error bound.
"""
from fractions import Fraction as Q
import json
import math
import unittest
from unittest.mock import patch

from mpmath.ctx_iv import MPIntervalContext
import numpy as np

from test_p980_os_numerical_feasibility import (
    ResearchParameters, StagedRows, SPLIT_TOLERANCE, bounds, product,
    split_admitted,
)


PARAMS = ResearchParameters(coefficient=Q(1, 2**24), chi_c=Q(16), zeta_c=Q(1, 2**37))
HISTORY_OFFSET = Q(1, 2**10)
RESOURCE_RADIUS, HISTORY_RADIUS = Q(1, 2**32), Q(1, 2**36)
RESOURCE_ROUND_BUDGET, HISTORY_ROUND_BUDGET = Q(1, 2**40), Q(1, 2**48)
IV = MPIntervalContext()
IV.dps = 60


def number(x):
    return IV.mpf(x.numerator)/x.denominator if isinstance(x, Q) else IV.mpf(float(x))


def endpoint(x, side):
    sign, mantissa, exponent, bitcount = x._mpi_[side]
    if bitcount < 0:
        raise ValueError('nonfinite interval endpoint')
    return Q((-1 if sign else 1)*int(mantissa))*Q(2)**int(exponent)


def upper_abs(x):
    return max(abs(endpoint(x, 0)), abs(endpoint(x, 1)))


def box(x, radius=Q(0)):
    x, radius = number(x), number(radius)
    return IV.mpf([ (x-radius).a, (x+radius).b ])


def vector(xs, radius=Q(0)):
    return IV.matrix([box(x, radius) for x in xs])


def inflate(a, radius):
    """Outward hull; retains exact trajectories as well as the nominal run."""
    r = number(radius)
    return IV.matrix([IV.mpf([(x-r).a, (x+r).b]) for x in a])


def infinity(a):
    return max(sum(upper_abs(a[i, j]) for j in range(a.cols)) for i in range(a.rows))


def inverse(a):
    """Interval Gauss-Jordan; zero-containing pivots fail closed.

    At every elimination, interval operations contain the exact elimination
    for each input in the box. Pivots are selected only if bounded away from
    zero. No floating inverse is asserted to be an enclosure.
    """
    n = a.rows
    work = [[a[i, j] for j in range(n)]+[number(int(i == j)) for j in range(n)] for i in range(n)]
    for k in range(n):
        choices = [i for i in range(k, n) if endpoint(work[i][k], 0) > 0 or endpoint(work[i][k], 1) < 0]
        if not choices:
            raise ValueError('interval inverse has no certified pivot')
        i = max(choices, key=lambda i: min(abs(endpoint(work[i][k], 0)), abs(endpoint(work[i][k], 1))))
        work[k], work[i] = work[i], work[k]
        pivot = work[k][k]
        work[k] = [x/pivot for x in work[k]]
        work[k][k] = number(1)
        for i in range(n):
            if i == k:
                continue
            multiplier = work[i][k]
            work[i] = [x-multiplier*y for x, y in zip(work[i], work[k])]
            work[i][k] = number(0)
    return IV.matrix([row[n:] for row in work])


class IntervalRows:
    def __init__(self, staged):
        self.nodes, self.edges, self.index = staged.nodes, staged.edges, staged.index
        self.B, self.I, self.D = IV.matrix(staged.B.tolist()), IV.eye(len(self.edges)), IV.matrix(staged.D.tolist())
        self.mask, self.params = staged.mask, staged.params

    def rows(self, c, w):
        numerator = [[number(0) for _ in range(3)] for _ in self.nodes]
        denominator = [[number(0) for _ in range(3)] for _ in self.nodes]
        for k, e in enumerate(self.edges):
            for end, other in ((e['tail'], e['head']), (e['head'], e['tail'])):
                i, j = self.index[end['node_id']], self.index[other['node_id']]
                a = (end['port']-1)//3
                numerator[i][a] += w[k]*(c[j]-c[i])
                denominator[i][a] += w[k]
        if any(endpoint(x, 0) <= 0 for x in w):
            raise ValueError('positive descriptor weights not certified')
        return [[numerator[i][a]/denominator[i][a] if endpoint(denominator[i][a], 0) > 0 else number(0)
                 for a in range(3)] for i in range(len(self.nodes))]

    def conductance(self, c, w, j):
        rows = self.rows(c, w)
        out = []
        for k, e in enumerate(self.edges):
            u, v = self.index[e['tail']['node_id']], self.index[e['head']['node_id']]
            contrast = sum((x-y)**2 for x, y in zip(rows[u], rows[v]))
            exponent = number(self.params.coefficient)*(c[u]+c[v]+contrast+j[k]**2)/2
            drive = IV.exp(-exponent)
            # This bounded witness must certify the inactive floor, not
            # silently evaluate a different smooth completion at its boundary.
            if endpoint(drive, 0) <= Q(1, 2) or endpoint(exponent, 0) < 0:
                raise ValueError('physical inactive-floor exponent domain not certified')
            out.append(drive)
        return IV.matrix(out)

    def read(self, candidate, c, w, h, *, geometry=True, feedback=True, modulation=True):
        chi = number(self.params.chi_a if candidate == 'A' else self.params.chi_c)
        zeta = number(self.params.zeta_a if candidate == 'A' else self.params.zeta_c)
        b = self.B.T*c
        if candidate == 'A':
            mobility = IV.diag(list(w))
            phi = self.B*mobility*b
            if geometry:
                phi += number(bounds.KAPPA_AH)*self.B*(h-self.I)*b
            baseline = -mobility*self.B.T*phi
            drive = self.conductance(c, w, baseline)
            q = [(x-g)/(x+g) for x, g in zip(w, drive)]
            diagonals = [1-zeta*chi*x if feedback else number(1) for x in q]
            if min(endpoint(x, 0) for x in diagonals) <= Q(1, 2):
                raise ValueError('A current regularity not certified')
            j = IV.matrix([x/d for x, d in zip(baseline, diagonals)])
            causal = IV.matrix([chi*x*y for x, y in zip(q, j)]) if feedback else IV.matrix(len(j), 1)
            regularity = min(endpoint(x, 0) for x in diagonals)
        else:
            e = IV.exp(2*sum(c)/len(c))
            t = IV.exp(number(bounds.KAPPA_M)*(e-1)/(e+1)) if modulation else number(1)
            baseline = -self.B.T*self.B*(t*(h if geometry else self.I))*b
            response = inverse(self.I+t*h*self.D)
            contraction = infinity(zeta*chi*response) if feedback else Q(0)
            if contraction >= Q(1, 2):
                raise ValueError('C current inverse bound not certified')
            j = inverse(self.I-zeta*chi*response)*baseline if feedback else baseline
            causal = chi*response*j if feedback else IV.matrix(len(j), 1)
            regularity = 1-contraction
        flat = inverse(h)*causal
        source = IV.matrix([[zeta*number(self.mask[i, k])*flat[i]*flat[k]
                             for k in range(len(flat))] for i in range(len(flat))])
        return dict(J=j, baseline=baseline, source=source, regularity=regularity)

    def write(self, c, w, j):
        drive, a = self.conductance(c, w, j), IV.exp(-number(bounds.DT))
        return IV.matrix([IV.exp(a*IV.ln(x)+(1-a)*IV.ln(g)) for x, g in zip(w, drive)])

    def ordinary_os(self, candidate, c, w):
        p = self.read(candidate, c, w, self.I)
        h = self.I+number(bounds.KAPPA_H)*p['source']
        # Exact-real symmetry plus this norm bound proves SPD and preserves
        # the constant-sector C gap, before using that reduced selector.
        if infinity(h-self.I) >= Q(1, 2):
            raise ValueError('generated geometry/selector chart not certified')
        r = self.read(candidate, c, w, h)
        regenerated = self.I+number(bounds.KAPPA_H)*r['source']
        after = c-number(bounds.DT)*self.B*r['J']
        return after, self.write(after, w, r['J']) if candidate == 'A' else None, dict(
            H=h, read=r, predictor=p, split_bound=infinity(h-regenerated),
            geometry_bound=infinity(h-self.I))


def staged_write(model, c, w, j):
    a = math.exp(-float(bounds.DT))
    return np.array([math.exp(a*math.log(float(x))+(1-a)*math.log(float(g)))
                     for x, g in zip(w, model.conductance(c, w, j))])


def geometry_expected(source, kappa):
    """Review control: exact dyadic assembly, independent of NumPy addition.

    At this binding kappa=1/2, scalar multiplication is an exponent shift
    (with binary64 subnormal rounding). This check does not assert equivalence
    of single and double rounding for arbitrary gains.
    """
    if kappa != Q(1, 2):
        raise ValueError('represented assembly control requires kappa_H=1/2')
    a = np.asarray(source)
    if (a.ndim != 2 or not a.size or a.shape[0] != a.shape[1]
            or a.dtype.kind not in 'fiu' or not np.all(np.isfinite(a))):
        raise ValueError('source must be a nonempty finite real square matrix')
    return np.array([[float(Q(i == j)+kappa*Q(float(a[i, j])))
                      for j in range(a.shape[1])] for i in range(a.shape[0])])


def check_geometry_stages(stages, size):
    """Bind each output to its distinct source before deciding split admission."""
    for field, stage in (('H', 'predictor'), ('regenerated', 'read')):
        expected = geometry_expected(stages[stage]['source'], bounds.KAPPA_H)
        actual = np.asarray(stages[field])
        if (expected.shape != (size, size) or actual.shape != expected.shape
                or actual.dtype.kind not in 'fiu' or not np.all(np.isfinite(actual))
                or not np.array_equal(actual, expected)):
            raise AssertionError(f'{field} is not assembled from {stage} source')


def represented_vector(values):
    a = np.asarray(values)
    if (a.ndim != 1 or not a.size or a.dtype.kind not in 'fiu'
            or (a.dtype.kind == 'f' and a.dtype.itemsize > 8)
            or not np.all(np.isfinite(a))):
        raise ValueError('effect operands must be nonempty finite real binary64 vectors')
    return tuple(float(x) for x in a)


def full_error(represented, enclosure):
    represented = represented_vector(represented)
    if (getattr(enclosure, 'rows', None) != len(represented)
            or getattr(enclosure, 'cols', None) != 1):
        raise ValueError('enclosure must cover every coordinate as a column vector')
    for value in enclosure:
        if not hasattr(value, '_mpi_'):
            raise ValueError('enclosure must contain finite real intervals')
        endpoint(value, 0)
        endpoint(value, 1)
    return max(upper_abs(number(x)-y) for x, y in zip(represented, enclosure, strict=True))


def separation(enabled, control, exact_enabled, exact_control):
    """Exact represented delta; both full formula errors and an 8-ULP margin."""
    enabled, control = represented_vector(enabled), represented_vector(control)
    if len(enabled) != len(control):
        raise ValueError('enabled/control vector sizes differ')
    delta = max(abs(Q(x)-Q(y)) for x, y in zip(enabled, control, strict=True))
    error = full_error(enabled, exact_enabled)+full_error(control, exact_control)
    ulp = max(Q(math.ulp(float(x))) for x in [*enabled, *control])
    if delta <= 4*error+8*ulp:
        raise AssertionError(f'full effect margin unresolved: delta={float(delta):.4g}, errors={float(error):.4g}, ulp={float(ulp):.4g}')
    return dict(represented_difference=float(delta), combined_full_error=float(error),
                exact_effect_lower=float(delta-error), minimum_margin_ratio=float(delta/(4*error+8*ulp)))


class OSEffectWitnessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        bounds.FixedRowBoundTests.setUpClass()
        cls.source_data = bounds.FixedRowBoundTests.source
        cls.layout = bounds.FixedRowBoundTests.d52

    def models(self):
        source = StagedRows(self.source_data['live_node_ids'], self.source_data['edges'], PARAMS)
        edges, nodes = bounds.normalized_target(self.layout)
        self.assertEqual(self.layout['request']['target_effective_degree'], 52)
        return source, StagedRows(nodes, edges, PARAMS)

    def test_interval_arithmetic_controls(self):
        self.assertLessEqual(endpoint(number(Q(1, 3)), 0), Q(1, 3))
        self.assertGreaterEqual(endpoint(number(Q(1, 3)), 1), Q(1, 3))
        a = IV.matrix([[box(2, Q(1, 100)), number(1)], [number(1), box(3, Q(1, 100))]])
        enclosed = inverse(a)
        for x in (Q(199, 100), Q(201, 100)):
            for y in (Q(299, 100), Q(301, 100)):
                exact = [[y/(x*y-1), -1/(x*y-1)], [-1/(x*y-1), x/(x*y-1)]]
                for i in range(2):
                    for j in range(2):
                        self.assertLessEqual(endpoint(enclosed[i, j], 0), exact[i][j])
                        self.assertGreaterEqual(endpoint(enclosed[i, j], 1), exact[i][j])
        with self.assertRaises(ValueError):
            inverse(IV.matrix([[box(0, 1)]]))
        with self.assertRaises(ValueError):
            endpoint(IV.mpf('inf'), 0)
        with self.assertRaises(AssertionError):
            separation([1.0], [1.0], vector([1]), vector([1]))
        with self.assertRaises(AssertionError):
            separation([1.0], [math.nextafter(1.0, 2.0)], vector([1]), vector([math.nextafter(1.0, 2.0)]))
        self.assertEqual(PARAMS.chi_c*PARAMS.zeta_c, bounds.CHI_C*bounds.ZETA)
        self.assertEqual(PARAMS.coefficient, Q(1, 2**24))

    def test_geometry_bindings_and_substitution(self):
        source, target = self.models()
        for candidate in ('A', 'C'):
            desired = {n: Q(3) if n == 'source-s' else Q(3)+bounds.OUTSIDE_OFFSET for n in source.nodes}
            c = source.vector(bounds.preimage(source.edges, desired))
            w = np.full(len(source.edges), float(1-HISTORY_OFFSET)) if candidate == 'A' else None
            post, wp, source_stages = source.ordinary_os(candidate, c, w)
            lineage = dict(zip((e['edge_id'] for e in source.edges), wp, strict=True)) if wp is not None else {}
            ct = target.vector({n: post[source.index[n]] if n.startswith('outside-') else
                                post[source.index['source-s']]/3 if n.startswith('satellite/') else 0 for n in target.nodes})
            wt = np.array([lineage.get(e['edge_id'], 1.0) for e in target.edges]) if candidate == 'A' else None
            target_stages = target.ordinary_os(candidate, ct, wt)[2]
            for label, model, stages in (('source', source, source_stages), ('first_target', target, target_stages)):
                with self.subTest(candidate=candidate, stage=label):
                    check_geometry_stages(stages, len(model.edges))
                    forged = dict(stages, regenerated=stages['H'].copy())
                    # The exact residual gate alone accepts this substitution.
                    self.assertTrue(split_admitted(forged['H'], forged['regenerated'], model.I, SPLIT_TOLERANCE))
                    with self.assertRaisesRegex(AssertionError, 'regenerated is not assembled from read source'):
                        check_geometry_stages(forged, len(model.edges))
                    with self.assertRaisesRegex(AssertionError, 'H is not assembled from predictor source'):
                        check_geometry_stages(dict(stages, H=stages['regenerated'].copy()), len(model.edges))
        # Equal geometries are lawful when each is assembled from its source.
        zero = np.zeros((2, 2))
        equal = dict(H=np.eye(2), regenerated=np.eye(2), predictor=dict(source=zero), read=dict(source=zero))
        check_geometry_stages(equal, 2)
        self.assertTrue(split_admitted(equal['H'], equal['regenerated'], np.eye(2), SPLIT_TOLERANCE))
        for invalid in ([], [[0, 0]], [[float('nan')]], [[float('inf')]], [[1j]]):
            with self.subTest(invalid_source=repr(invalid)), self.assertRaises(ValueError):
                geometry_expected(invalid, bounds.KAPPA_H)

    def test_verification_paths_reject_regeneration_substitution(self):
        original = StagedRows.ordinary_os

        def forged_regeneration(model, candidate, c, w):
            after, history, stages = original(model, candidate, c, w)
            return after, history, dict(stages, regenerated=stages['H'].copy())

        # Exercise actual call sites, not merely the standalone new helper.
        for method in ('test_full_effect_margins_and_history_continuation',
                       'test_certified_both_role_neighborhoods'):
            with self.subTest(path=method), patch.object(StagedRows, 'ordinary_os', forged_regeneration):
                with self.assertRaisesRegex(AssertionError, 'regenerated is not assembled from read source'):
                    getattr(self, method)()

    def test_effect_comparisons_reject_malformed_vectors(self):
        on, off = [0., 1.], [0., 0.]
        ei, ci = vector(on), vector(off)
        valid = separation(on, off, ei, ci)
        self.assertEqual(valid['represented_difference'], 1)
        self.assertEqual(full_error([0., 2.], ei), 1)
        for enabled, control in (([1., 1.], [0.]), ([1.], [0., 0.])):
            with self.subTest(shape=(len(enabled), len(control))), self.assertRaisesRegex(ValueError, 'vector sizes differ'):
                separation(enabled, control, vector(enabled), vector(control))
        for bad in ([], 1., [[1., 1.]], [[1.], [1.]], [float('nan')],
                    [float('inf')], [-float('inf')], [1j], ['1']):
            with self.subTest(represented=repr(bad)):
                for call in (lambda: full_error(bad, ei),
                             lambda: separation(bad, off, ei, ci),
                             lambda: separation(on, bad, ei, ci)):
                    with self.assertRaises(ValueError):
                        call()
        for bad in (vector([0]), vector([0, 1, 2]), IV.matrix([[0, 1]]),
                    IV.matrix([[0, 0], [1, 1]]), [0, 1],
                    IV.matrix([number(0), IV.mpf('inf')]),
                    IV.matrix([number(0), IV.mpf('-inf')]),
                    IV.matrix([number(0), IV.mpf('nan')])):
            with self.subTest(enclosure=str(bad)):
                for call in (lambda: full_error(on, bad),
                             lambda: separation(on, off, bad, ci),
                             lambda: separation(on, off, ei, bad)):
                    with self.assertRaises(ValueError):
                        call()

    def test_effect_threshold_equality_remains_rejected(self):
        # Audit control: shape hardening must not change the strict threshold.
        u = Q(math.ulp(1.0))
        error = (1-8*u)/4
        with self.assertRaisesRegex(AssertionError, 'full effect margin unresolved'):
            separation([1.], [0.], vector([1-error]), vector([0]))
        result = separation([1.], [0.], vector([1-error+Q(1, 2**60)]), vector([0]))
        self.assertGreater(result['exact_effect_lower'], 0)

    def test_certified_both_role_neighborhoods(self):
        source, target = self.models()
        src, dst = IntervalRows(source), IntervalRows(target)
        report = {}

        def advance(low, high, candidate, cf, wf, c, w):
            for represented, enclosure in zip(cf, c):
                self.assertLessEqual(endpoint(enclosure, 0), Q(float(represented)))
                self.assertGreaterEqual(endpoint(enclosure, 1), Q(float(represented)))
            if wf is not None:
                for represented, enclosure in zip(wf, w):
                    self.assertLessEqual(endpoint(enclosure, 0), Q(float(represented)))
                    self.assertGreaterEqual(endpoint(enclosure, 1), Q(float(represented)))
            # Point full-formula enclosure measures all staged evaluation
            # error on this actual nominal step, not merely solve residual.
            point_c, point_w, _ = high.ordinary_os(candidate, vector(cf), vector(wf) if wf is not None else None)
            cf, wf, sf = low.ordinary_os(candidate, cf, wf)
            check_geometry_stages(sf, len(low.edges))
            c_error = full_error(cf, point_c)
            self.assertLess(c_error, RESOURCE_ROUND_BUDGET)
            w_error = full_error(wf, point_w) if wf is not None else Q(0)
            self.assertLess(w_error, HISTORY_ROUND_BUDGET)
            c, w, stages = high.ordinary_os(candidate, c, w)
            self.assertTrue(split_admitted(sf['H'], sf['regenerated'], low.I, SPLIT_TOLERANCE))
            stages.update(resource_round_error=float(c_error), history_round_error=float(w_error))
            return cf, wf, inflate(c, RESOURCE_ROUND_BUDGET), inflate(w, HISTORY_ROUND_BUDGET) if w is not None else None, stages

        for candidate in ('A', 'C'):
            for role, s in (('current', Q(3)), ('reset', Q(2))):
                desired = {n: s if n == 'source-s' else s+bounds.OUTSIDE_OFFSET for n in source.nodes}
                initial = bounds.preimage(source.edges, desired) if role == 'current' else desired
                c = vector([initial[n] for n in source.nodes], RESOURCE_RADIUS)
                w = vector([1-HISTORY_OFFSET]*len(source.edges), HISTORY_RADIUS) if candidate == 'A' else None
                cf = source.vector(initial)
                wf = np.full(len(source.edges), float(1-HISTORY_OFFSET)) if candidate == 'A' else None
                if role == 'current':
                    cf, wf, c, w, stages = advance(source, src, candidate, cf, wf, c, w)
                    self.assertLess(stages['split_bound'], SPLIT_TOLERANCE)
                    self.assertGreater(min(endpoint(x, 0) for x in c), 0)
                    row = src.rows(c, w if w is not None else vector([1]*len(source.edges)))[source.index['source-s']]
                    self.assertTrue(all(endpoint(x, 0) > 0 for x in row))
                    self.assertLess(sum(upper_abs(x)**2 for x in row), Q(1, 4))
                lineage = dict(zip((e['edge_id'] for e in source.edges), w)) if w is not None else {}
                lineage_f = dict(zip((e['edge_id'] for e in source.edges), wf)) if wf is not None else {}
                cf = target.vector({n: cf[source.index[n]] if n.startswith('outside-') else
                                    cf[source.index['source-s']]/3 if n.startswith('satellite/') else 0 for n in target.nodes})
                wf = np.array([lineage_f.get(e['edge_id'], 1.0) for e in target.edges]) if candidate == 'A' else None
                c = IV.matrix([c[source.index[n]] if n.startswith('outside-') else
                               c[source.index['source-s']]/3 if n.startswith('satellite/') else number(0) for n in target.nodes])
                w = IV.matrix([lineage.get(e['edge_id'], number(1)) for e in target.edges]) if candidate == 'A' else None
                rows = []
                for _ in range(bounds.HORIZON):
                    cf, wf, c, w, stages = advance(target, dst, candidate, cf, wf, c, w)
                    lower, upper = min(endpoint(x, 0) for x in c), max(endpoint(x, 1) for x in c)
                    self.assertGreater(lower, bounds.RESOURCE_MARGIN/2)
                    self.assertLess(upper, 4)
                    self.assertLess(stages['split_bound'], SPLIT_TOLERANCE)
                    self.assertGreater(stages['read']['regularity'], Q(1, 2))
                    for x, represented in zip(c, cf):
                        self.assertLessEqual(endpoint(x, 0), Q(float(represented)))
                        self.assertGreaterEqual(endpoint(x, 1), Q(float(represented)))
                    if w is not None:
                        self.assertGreater(min(endpoint(x, 0) for x in w), Q(99, 100))
                        self.assertLess(max(endpoint(x, 1) for x in w), Q(1001, 1000))
                        for x, represented in zip(w, wf):
                            self.assertLessEqual(endpoint(x, 0), Q(float(represented)))
                            self.assertGreaterEqual(endpoint(x, 1), Q(float(represented)))
                    rows.append(dict(resource_lower=float(lower), resource_upper=float(upper),
                                     geometry_bound=float(stages['geometry_bound']), split_bound=float(stages['split_bound']),
                                     resource_round_error=stages['resource_round_error'], history_round_error=stages['history_round_error']))
                report[candidate+'_'+role] = rows
        type(self).neighborhood_report = report

    def test_full_effect_margins_and_history_continuation(self):
        source, target = self.models()
        report = {}
        for candidate in ('A', 'C'):
            desired = {n: Q(3) if n == 'source-s' else Q(3)+bounds.OUTSIDE_OFFSET for n in source.nodes}
            c = source.vector(bounds.preimage(source.edges, desired))
            w = np.full(len(source.edges), float(1-HISTORY_OFFSET)) if candidate == 'A' else None
            post, wp, source_stages = source.ordinary_os(candidate, c, w)
            check_geometry_stages(source_stages, len(source.edges))
            lineage = dict(zip((e['edge_id'] for e in source.edges), wp)) if candidate == 'A' else {}
            ct = target.vector({n: post[source.index[n]] if n.startswith('outside-') else
                                post[source.index['source-s']]/3 if n.startswith('satellite/') else 0 for n in target.nodes})
            wt = np.array([lineage.get(e['edge_id'], 1.0) for e in target.edges]) if candidate == 'A' else None
            for label, model, c, w in (('source', source, c, w), ('target', target, ct, wt)):
                certified = IntervalRows(model)
                ci, wi = vector(c), vector(w) if w is not None else None
                after, wn, low = model.ordinary_os(candidate, c, w)
                check_geometry_stages(low, len(model.edges))
                ai, wni, high = certified.ordinary_os(candidate, ci, wi)
                self.assertTrue(split_admitted(low['H'], low['regenerated'], model.I, SPLIT_TOLERANCE))
                no_geom = model.read(candidate, c, w, low['H'], geometry=False)
                no_geom_i = certified.read(candidate, ci, wi, high['H'], geometry=False)
                key = candidate+'_'+label
                report[key+'_geometry'] = separation(low['read']['J'], no_geom['J'], high['read']['J'], no_geom_i['J'])
                off = model.read(candidate, c, w, low['H'], feedback=False)
                off_i = certified.read(candidate, ci, wi, high['H'], feedback=False)
                report[key+'_readback'] = separation(low['read']['J'], off['J'], high['read']['J'], off_i['J'])
                if candidate == 'C':
                    off = model.read(candidate, c, None, low['H'], modulation=False)
                    off_i = certified.read(candidate, ci, None, high['H'], modulation=False)
                    report[key+'_modulation'] = separation(low['read']['J'], off['J'], high['read']['J'], off_i['J'])
                if candidate == 'A' and label == 'target':
                    for stage in ('baseline_current', 'stale_resource'):
                        wc = staged_write(model, after if stage == 'baseline_current' else c, w,
                                          low['read']['baseline'] if stage == 'baseline_current' else low['read']['J'])
                        wci = certified.write(ai if stage == 'baseline_current' else ci, wi,
                                              high['read']['baseline'] if stage == 'baseline_current' else high['read']['J'])
                        report[stage+'_final_history'] = separation(wn, wc, wni, wci)
                        next_on_stages = model.ordinary_os(candidate, after, wn)[2]
                        next_off_stages = model.ordinary_os(candidate, after, wc)[2]
                        check_geometry_stages(next_on_stages, len(model.edges))
                        check_geometry_stages(next_off_stages, len(model.edges))
                        next_on = next_on_stages['read']['J']
                        next_off = next_off_stages['read']['J']
                        next_on_i = certified.ordinary_os(candidate, ai, wni)[2]['read']['J']
                        next_off_i = certified.ordinary_os(candidate, ai, wci)[2]['read']['J']
                        report[stage+'_next_current'] = separation(next_on, next_off, next_on_i, next_off_i)
        type(self).effect_report = report


if __name__ == '__main__':
    import sys
    emit = '--report' in sys.argv
    if emit:
        sys.argv.remove('--report')
    program = unittest.main(exit=False)
    if emit and program.result.wasSuccessful():
        print(json.dumps(dict(neighborhoods=OSEffectWitnessTests.neighborhood_report,
                              effects=OSEffectWitnessTests.effect_report), indent=2))
    sys.exit(not program.result.wasSuccessful())

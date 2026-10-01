"""Bounded OS numerical pressure, not native profile admission.

The unchanged nine-port construction is evaluated at explicit binary64 stage
boundaries. Dot products round each product, then use math.fsum; linear blocks
use mpmath's pure Python binary64 fp context (not arbitrary precision).
This deliberately separates linear-solve accuracy from loss of a constitutive
effect. libm exp/log/tanh remain platform operations, not certified intervals.
No production candidate, realization, geometry or numerical evaluator is used.
"""
from fractions import Fraction as Q
from dataclasses import dataclass
import json
import math
import unittest

import mpmath as mp
import numpy as np

import test_p980_fixed_row_bounds as bounds


SPLIT_TOLERANCE = Q(1, 2**40)


@dataclass(frozen=True)
class ResearchParameters:
    """Explicit inputs; defaults preserve the reviewed numerical-loss case."""
    coefficient: Q = bounds.COEFFICIENT
    chi_a: Q = bounds.CHI_A
    chi_c: Q = bounds.CHI_C
    zeta_a: Q = bounds.ZETA
    zeta_c: Q = bounds.ZETA


def product(a, b):
    """Declared scalar product order; no BLAS reduction or hidden precision."""
    a, b = np.asarray(a), np.asarray(b)
    vector = b.ndim == 1
    if vector:
        b = b[:, None]
    out = np.array([[math.fsum(float(x)*float(y) for x, y in zip(row, col))
                     for col in b.T] for row in a])
    return out[:, 0] if vector else out


def rounded_solve(a, b):
    """Explicit binary64 LU; exact residual bounds are checked separately."""
    return np.array(list(mp.fp.lu_solve(mp.fp.matrix(a.tolist()), mp.fp.matrix(b.tolist()))))


def current_solve_bound(read):
    """Exact dyadic Neumann/residual enclosure for the represented J block.

    Does not enclose coefficient construction, libm or the constitutive law.
    """
    a = [[Q(float(x)) for x in row] for row in read['block']]
    x = [Q(float(v)) for v in read['J']]
    b = [Q(float(v)) for v in read['baseline']]
    theta = max(sum(abs(v-Q(i == j)) for j, v in enumerate(row)) for i, row in enumerate(a))
    if theta >= 1:
        raise ValueError('current inverse enclosure unresolved')
    residual = max(abs(sum(v*y for v, y in zip(row, x))-rhs) for row, rhs in zip(a, b))
    return residual/(1-theta)


def psd(a):
    """Exact symmetric Schur test, including singular/equality boundaries."""
    a = [list(map(Q, row)) for row in a]
    n = len(a)
    if any(a[i][j] != a[j][i] for i in range(n) for j in range(n)):
        return False
    for k in range(n):
        pivot = a[k][k]
        if pivot < 0:
            return False
        if not pivot:
            if any(a[k][j] for j in range(k+1, n)):
                return False
            continue
        for i in range(k+1, n):
            for j in range(i, n):
                a[i][j] -= a[i][k]*a[k][j]/pivot
                a[j][i] = a[i][j]
    return True


def split_admitted(h, regenerated, reference, tolerance):
    """The actual edge_l2_v1 inequality, without rounded subtraction/eigenvalues.

    ||Href^-1/2 (h-regenerated) Href^-1/2||_2 <= tolerance iff both
    tolerance*Href +/- (h-regenerated) are PSD, for SPD Href.
    """
    residual = [[Q(float(x))-Q(float(y)) for x, y in zip(row, other)]
                for row, other in zip(h, regenerated)]
    return all(psd([[tolerance*Q(float(x))+sign*r for x, r in zip(row, defect)]
                    for row, defect in zip(reference, residual)])
               for sign in (-1, 1))


def maximum(a):
    return float(np.max(np.abs(a)))


class StagedRows:
    """Independent fixed-row binary64 evaluator of the reviewed OS binding."""
    def __init__(self, nodes, edges, params=ResearchParameters()):
        self.params = params
        self.nodes, self.edges = tuple(nodes), tuple(edges)
        self.index = {n: i for i, n in enumerate(nodes)}
        self.B = np.zeros((len(nodes), len(edges)))
        self.mask = np.zeros((len(edges), len(edges)))
        ends = [{e['tail']['node_id'], e['head']['node_id']} for e in edges]
        for e, edge in enumerate(edges):
            self.B[self.index[edge['tail']['node_id']], e] = 1
            self.B[self.index[edge['head']['node_id']], e] = -1
            for f in range(len(edges)):
                self.mask[e, f] = 1 if e == f else 0.5 if ends[e] & ends[f] else 0
        self.I = np.eye(len(edges))
        self.D = product(self.B.T, self.B)

    def vector(self, values):
        return np.array([float(values[n]) for n in self.nodes])

    def conductance(self, c, w, j):
        cells = [[[] for _ in range(3)] for _ in self.nodes]
        for k, e in enumerate(self.edges):
            for end, other in ((e['tail'], e['head']), (e['head'], e['tail'])):
                i, v = self.index[end['node_id']], self.index[other['node_id']]
                cells[i][(end['port']-1)//3].append((float(w[k]), float(c[v]-c[i])))
        rows = [[math.fsum(w*d for w, d in cell)/math.fsum(w for w, _ in cell)
                 if cell else 0.0 for cell in node] for node in cells]
        drive = []
        for k, e in enumerate(self.edges):
            u, v = self.index[e['tail']['node_id']], self.index[e['head']['node_id']]
            contrast = math.fsum((x-y)**2 for x, y in zip(rows[u], rows[v]))
            exponent = float(self.params.coefficient)*(float(c[u]+c[v])+contrast+float(j[k])**2)/2
            drive.append(max(0.5, math.exp(-exponent)))
        return np.array(drive)

    def read(self, candidate, c, w, h, *, geometry=True, feedback=True, modulation=True):
        chi = self.params.chi_a if candidate == 'A' else self.params.chi_c
        zeta = self.params.zeta_a if candidate == 'A' else self.params.zeta_c
        b = product(self.B.T, c)
        if candidate == 'A':
            phi = product(self.B, w*b)
            if geometry:
                phi += float(bounds.KAPPA_AH)*product(self.B, product(h-self.I, b))
            baseline = -w*product(self.B.T, phi)
            drive = self.conductance(c, w, baseline)
            q = (w-drive)/(w+drive)
            block = np.diag(1-float(zeta*chi)*q) if feedback else self.I
            j = rounded_solve(block, baseline)
            causal = float(chi)*q*j if feedback else np.zeros_like(j)
            extra = dict(q=q, drive=drive)
        else:
            t = math.exp(float(bounds.KAPPA_M)*math.tanh(math.fsum(c)/len(c))) if modulation else 1.0
            retained = t*(h if geometry else self.I)
            baseline = -product(self.B.T, product(self.B, product(retained, b)))
            # Proved physical response (I+t H B^T B)^-1. This avoids
            # attributing similarity-rounding artifacts to a physical effect.
            response_block = self.I+t*product(h, self.D)
            response = np.column_stack([rounded_solve(response_block, col) for col in self.I])
            block = self.I-float(zeta*chi)*response if feedback else self.I
            j = rounded_solve(block, baseline)
            causal = float(chi)*product(response, j) if feedback else np.zeros_like(j)
            extra = dict(t=t, response=response)
        flat = rounded_solve(h, causal)
        source = float(zeta)*self.mask*np.outer(flat, flat)
        return dict(J=j, baseline=baseline, causal=causal, source=source,
                    block=block, **extra)

    def ordinary_os(self, candidate, c, w):
        predictor = self.read(candidate, c, w, self.I)
        h = self.I+float(bounds.KAPPA_H)*predictor['source']
        read = self.read(candidate, c, w, h)
        regenerated = self.I+float(bounds.KAPPA_H)*read['source']
        after = c-float(bounds.DT)*product(self.B, read['J'])
        drive, next_w = None, None
        if candidate == 'A':
            drive = self.conductance(after, w, read['J'])
            decay = math.exp(-float(bounds.DT))
            next_w = np.array([math.exp(decay*math.log(float(old))+(1-decay)*math.log(float(g)))
                               for old, g in zip(w, drive)])
        return after, next_w, dict(predictor=predictor, read=read, H=h,
                                   regenerated=regenerated, writer_drive=drive)


def measurements(model, candidate, c, w, after, next_w, stages):
    p, r, h = stages['predictor'], stages['read'], stages['H']
    no_geometry = model.read(candidate, c, w, h, geometry=False)
    no_feedback = model.read(candidate, c, w, h, feedback=False)
    defect = [[Q(float(x))-Q(float(y)) for x, y in zip(row, other)]
              for row, other in zip(h, stages['regenerated'])]
    result = dict(
        split_admitted=split_admitted(h, stages['regenerated'], model.I, SPLIT_TOLERANCE),
        split_row_bound=float(max(sum(abs(x) for x in row) for row in defect)),
        geometry_diagonals=sum(h[i, i] != 1 for i in range(len(h))),
        geometry_offdiagonal=maximum(h-np.diag(np.diag(h))),
        predictor_corrector=maximum(r['J']-p['J']),
        geometry_baseline=maximum(r['baseline']-no_geometry['baseline']),
        geometry_current=maximum(r['J']-no_geometry['J']),
        feedback_current=maximum(r['J']-no_feedback['J']),
        causal_current=maximum(r['causal']),
        source=maximum(r['source']),
        current_block_error=float(current_solve_bound(r)),
    )
    if candidate == 'A':
        result.update(history_change=maximum(next_w-w),
                      writer_fresh_resource=maximum(stages['writer_drive']-model.conductance(c, w, r['J'])),
                      writer_selected_current=maximum(stages['writer_drive']-model.conductance(after, w, r['baseline'])))
    else:
        plain = model.read(candidate, c, None, h, modulation=False)
        result['modulation_current'] = maximum(r['J']-plain['J'])
    return result


class OSNumericalFeasibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        bounds.FixedRowBoundTests.setUpClass()
        cls.source_data = bounds.FixedRowBoundTests.source
        cls.vector_data = bounds.FixedRowBoundTests.layouts[-1]

    def test_normalized_contract_including_equality_and_nonidentity_reference(self):
        b = bounds.exact_budgets()
        for candidate in ('a', 'c'):
            self.assertLess(b[candidate+'_geometry_contraction']*bounds.KAPPA_H*b[candidate+'_source'], SPLIT_TOLERANCE/128)
        self.assertTrue(split_admitted([[1.25]], [[1.0]], [[1.0]], Q(1, 4)))
        self.assertFalse(split_admitted([[math.nextafter(1.25, math.inf)]], [[1.0]], [[1.0]], Q(1, 4)))
        # Raw spectral defect 1/4 passes an unnormalized tolerance 1/2,
        # but normalized defect is one: a raw-norm implementation must fail.
        self.assertFalse(split_admitted([[1.25]], [[1.0]], [[0.25]], Q(1, 2)))
        self.assertTrue(split_admitted([[1.25]], [[1.0]], [[4.0]], Q(1, 8)))
        self.assertFalse(psd([[0, Q(1, 8)], [Q(1, 8), 1]]))
        self.assertTrue(psd([[1, 1], [1, 1]]))

    def test_review_matrix_controls(self):
        i = np.eye(2)
        h = [[1, 0.25], [0.25, 1]]
        self.assertTrue(split_admitted(h, i, i, Q(1, 4)))
        n = math.nextafter(0.25, math.inf)
        self.assertFalse(split_admitted([[1, n], [n, 1]], i, i, Q(1, 4)))
        # Spectral norm is 1/4; Frobenius is sqrt(2)/4, so 5/16
        # distinguishes the actual contract from an overly strong proxy.
        self.assertTrue(split_admitted([[1.25, 0], [0, 1.25]], i, i, Q(5, 16)))
        self.assertFalse(split_admitted(h, i, [[0.25, 0], [0, 1]], Q(1, 4)))
        href = [[1, 0.5], [0.5, 1]]
        self.assertTrue(split_admitted([[1.25, 0.125], [0.125, 1.25]], i, href, Q(1, 4)))

    def test_review_writer_ceiling(self):
        b = bounds.exact_budgets()
        theta = bounds.ZETA*bounds.CHI_A*b['qmax']
        ceiling = ((1+bounds.WIDTH)*bounds.DT*bounds.COEFFICIENT*1024**2/2
                   *((1-theta)**-2-1))
        self.assertGreater(ceiling, Q(1694, 10**24))
        self.assertLess(ceiling, Q(1695, 10**24))
        self.assertLess(ceiling/Q(1, 2**53), Q(153, 10**7))

    def test_binary64_source_and_target_mechanisms(self):
        """Loss is an expected finding, never relabeled enabled conformance."""
        report = {}
        source = StagedRows(self.source_data['live_node_ids'], self.source_data['edges'])
        edges, nodes = bounds.normalized_target(self.vector_data)
        self.assertEqual(self.vector_data['request']['target_effective_degree'], 52)
        target = StagedRows(nodes, edges)
        for candidate in ('A', 'C'):
            desired = {n: Q(3) if n == 'source-s' else Q(3)+bounds.OUTSIDE_OFFSET for n in source.nodes}
            c = source.vector(bounds.preimage(source.edges, desired))
            w = np.full(len(source.edges), float(1-bounds.WIDTH)) if candidate == 'A' else None
            post, wp, stages = source.ordinary_os(candidate, c, w)
            record = measurements(source, candidate, c, w, post, wp, stages)
            report[candidate+'_source'] = record
            self.assertTrue(record['split_admitted'])
            self.assertEqual(record['geometry_diagonals'], 0)
            self.assertGreater(record['geometry_offdiagonal'], 0)
            self.assertEqual(record['geometry_baseline'], 0)
            self.assertEqual(record['geometry_current'], 0)
            self.assertEqual(record['predictor_corrector'], 0)
            self.assertGreater(record['feedback_current'], 0)
            self.assertGreater(record['feedback_current'], 100*record['current_block_error'])
            self.assertGreater(record['causal_current'], 0)
            self.assertGreater(record['source'], 0)
            if candidate == 'C':
                self.assertGreater(record['modulation_current'], 0)
            for role, s in (('current', Q(3)), ('reset', Q(2))):
                # Only current takes the ordinary source beat. Reset transfer
                # starts independently from its supplied source resources.
                values = post if role == 'current' else source.vector({n: s if n == 'source-s' else s+bounds.OUTSIDE_OFFSET for n in source.nodes})
                old_w = wp if role == 'current' else w
                c = target.vector({n: values[source.index[n]] if n.startswith('outside-') else
                                   values[source.index['source-s']]/3 if n.startswith('satellite/') else 0 for n in nodes})
                lineage = dict(zip((e['edge_id'] for e in source.edges), old_w)) if candidate == 'A' else {}
                wt = np.array([lineage.get(e['edge_id'], 1.0) for e in edges]) if candidate == 'A' else None
                rows = []
                for _ in range(bounds.HORIZON):
                    after, wn, stages = target.ordinary_os(candidate, c, wt)
                    row = measurements(target, candidate, c, wt, after, wn, stages)
                    rows.append(row)
                    self.assertTrue(row['split_admitted'])
                    self.assertLess(row['split_row_bound'], float(SPLIT_TOLERANCE))
                    self.assertEqual(row['geometry_diagonals'], 0)
                    self.assertGreater(row['geometry_offdiagonal'], 0)
                    self.assertEqual(row['geometry_baseline'], 0)
                    self.assertEqual(row['geometry_current'], 0)
                    self.assertEqual(row['predictor_corrector'], 0)
                    self.assertGreater(row['feedback_current'], 0)
                    self.assertGreater(row['feedback_current'], 100*row['current_block_error'])
                    self.assertGreater(min(after), float(bounds.RESOURCE_MARGIN/2))
                    self.assertLess(max(after), 4)
                    if candidate == 'C':
                        self.assertGreater(row['modulation_current'], 0)
                    else:
                        self.assertGreater(row['history_change'], 0)
                        self.assertEqual(row['writer_selected_current'], 0)
                    c, wt = after, wn
                report[candidate+'_'+role+'_target'] = rows
        type(self).report = report

    def test_resolvable_geometry_controls_against_independent_oracle(self):
        """The numerical evaluator must consume H when an effect is resolvable.

        These supplied-H controls are not OS-generated-geometry closure.
        High precision is a cross-check, not an outward error certificate.
        """
        with mp.workdps(70):
            high, c, w, h, _ = bounds.FixedRowBoundTests().audit_inputs()
            low = StagedRows(high.nodes, high.edges)
            cf, wf = np.array(list(map(float, c))), np.array(list(map(float, w)))
            hf = np.array(h.tolist(), dtype=float)
            # Feed identical represented inputs to both evaluators.
            c, w, h = mp.matrix(cf.tolist()), mp.matrix(wf.tolist()), mp.matrix(hf.tolist())
            for candidate in ('A', 'C'):
                warg = wf if candidate == 'A' else None
                actual = low.read(candidate, cf, warg, hf)
                control = low.read(candidate, cf, warg, hf, geometry=False)
                reference = high.read(candidate, c, w if candidate == 'A' else None, h)
                identity_read = high.read(candidate, c, w if candidate == 'A' else None, high.I)
                change = actual['baseline']-control['baseline']
                wanted = np.array(list(map(float, reference['baseline']-identity_read['baseline'])))
                self.assertGreater(maximum(change), 1e-9)
                self.assertLess(maximum(change-wanted), 1e-13)
                self.assertGreater(maximum(actual['J']-control['J']), 1e-9)
                self.assertLess(maximum(actual['J']-np.array(list(map(float, reference['J'])))), 1e-13)
                self.assertLess(float(current_solve_bound(actual)), 1e-13)

    def test_source_exact_effect_and_whole_step_comparison(self):
        """Same binary64 inputs, full independent 70-digit OS step.

        Demonstrates that exact mechanism absence is NOT the explanation.
        The comparison allowance is not the OS split tolerance.
        """
        with mp.workdps(70):
            low = StagedRows(self.source_data['live_node_ids'], self.source_data['edges'])
            high = bounds.FixedRows(low.nodes, low.edges)
            desired = {n: Q(3) if n == 'source-s' else Q(3)+bounds.OUTSIDE_OFFSET for n in low.nodes}
            c = low.vector(bounds.preimage(low.edges, desired))
            for candidate in ('A', 'C'):
                w = np.full(len(low.edges), float(1-bounds.WIDTH)) if candidate == 'A' else None
                ca, wa, actual = low.ordinary_os(candidate, c, w)
                cr, wr, reference = high.ordinary_os(candidate, mp.matrix(c.tolist()), mp.matrix(w.tolist()) if w is not None else None)
                self.assertGreater(mp.norm(reference['H']-high.I), 0)
                self.assertGreater(bounds.norm_inf(reference['read']['J']-reference['predictor']['J']), 0)
                self.assertEqual(maximum(actual['read']['J']-actual['predictor']['J']), 0)
                self.assertLess(maximum(ca-np.array(list(map(float, cr)))), 1e-13)
                self.assertLess(maximum(actual['read']['J']-np.array(list(map(float, reference['read']['J'])))), 1e-13)
                if w is not None:
                    self.assertLess(maximum(wa-np.array(list(map(float, wr)))), 1e-15)
                    exact_wrong = high.conductance(cr, mp.matrix(w.tolist()), reference['read']['baseline'])
                    self.assertGreater(bounds.norm_inf(reference['writer_drive']-exact_wrong), 0)

    def test_current_error_enclosure_is_exact_not_a_mechanism_test(self):
        # One dyadic block can have an arbitrarily accurate solve and still
        # say nothing about a missing constitutive consumer before the solve.
        r = dict(block=np.array([[0.75]]), baseline=np.array([1.0]), J=np.array([4.0/3.0]))
        bound = current_solve_bound(r)
        self.assertGreater(bound, 0)
        self.assertEqual(bound, abs(Q(4, 3)-Q(float(r['J'][0]))))
        r['J'][0] += 1e-4
        self.assertGreater(current_solve_bound(r), Q(1, 20000))


if __name__ == '__main__':
    import sys
    if '--report' in sys.argv:
        sys.argv.remove('--report')
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(OSNumericalFeasibilityTests)
        result = unittest.TextTestRunner().run(suite)
        if result.wasSuccessful():
            print(json.dumps(OSNumericalFeasibilityTests.report, indent=2, default=int))
        sys.exit(not result.wasSuccessful())
    unittest.main()

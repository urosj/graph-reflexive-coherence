"""Nine-port research oracle and exact bounds, not a production backend.

No production candidate, current, writer, or realization evaluator supplies
expected outputs. Fraction budgets are proofs' arithmetic checks; 70-digit
mpmath evaluations are numerical pressure, not interval/representation proofs.
"""
import ast
import copy
from fractions import Fraction as Q
from pathlib import Path
import unittest
from unittest.mock import patch

import mpmath as mp

import test_p980_boundary_continuation as boundary
from test_p980_boundary_continuation import (
    DT, HORIZON, OUTSIDE_OFFSET, RESOURCE_MARGIN,
    normalized_target, preimage, resources, step,
)

WIDTH = RHO = Q(1, 2**24)
COEFFICIENT = Q(1, 2**48)
CHI_A, CHI_C, ZETA = Q(1, 16), Q(1, 2**32), Q(1, 2)
KAPPA_M, KAPPA_H, KAPPA_AH = RHO, Q(1, 2), Q(1, 2)
CARRIER_RADIUS = Q(1, 2**25)


def exact_budgets():
    qmax = WIDTH / (1-WIDTH)
    theta_a = ZETA * CHI_A * qmax
    theta_c = ZETA * CHI_C * 8
    # d_max <= 9 on source AND targets; m <= 16. ||C||inf <= 4.
    a_base = 1296*WIDTH*(2+WIDTH) + 2592*(1+WIDTH)*RHO
    a_read = 9*1024*theta_a/(1-theta_a)
    c_base = 1296*(2*KAPPA_M + (1+2*KAPPA_M)*4*RHO)
    c_read = 9*1024*theta_c/(1-theta_c)
    q_h = COEFFICIENT*1024*300
    a_flat = 5*CHI_A*qmax*2048
    a_flat_h = 5*CHI_A*(qmax*400+q_h*2048)+5*CHI_A*qmax*2048
    c_flat = 5*CHI_C*8*2048
    c_flat_h = 5*CHI_C*(9216*2048+8*4096)+5*CHI_C*8*2048
    return dict(qmax=qmax, a_rate_error=a_base+a_read,
                c_rate_error=c_base+c_read,
                exponent=COEFFICIENT*(10+1200+2048**2)/2,
                a_source=ZETA*16*(5*CHI_A*qmax*2048)**2,
                c_source=ZETA*16*(5*CHI_C*8*2048)**2,
                a_geometry_contraction=KAPPA_H*32*ZETA*a_flat*a_flat_h,
                c_geometry_contraction=KAPPA_H*32*ZETA*c_flat*c_flat_h)


def number(x):
    return mp.mpf(x.numerator)/x.denominator if isinstance(x, Q) else mp.mpf(x)


def norm_inf(v):
    return max(abs(x) for x in v)


class FixedRows:
    def __init__(self, nodes, edges):
        self.nodes, self.edges = tuple(nodes), tuple(edges)
        self.index = {n: i for i, n in enumerate(nodes)}
        self.B = mp.matrix(len(nodes), len(edges))
        for e, edge in enumerate(edges):
            self.B[self.index[edge['tail']['node_id']], e] = 1
            self.B[self.index[edge['head']['node_id']], e] = -1
        self.L = self.B*self.B.T
        self.I = mp.eye(len(edges))

    def vector(self, values):
        return mp.matrix([number(values[n]) for n in self.nodes])

    def rows(self, C, weights):
        result = mp.matrix(len(self.nodes), 3)
        denom = mp.matrix(len(self.nodes), 3)
        for e, edge in enumerate(self.edges):
            for end, other in ((edge['tail'], edge['head']), (edge['head'], edge['tail'])):
                i, j = self.index[end['node_id']], self.index[other['node_id']]
                a = (end['port']-1)//3
                result[i, a] += weights[e]*(C[j]-C[i])
                denom[i, a] += weights[e]
        for i in range(len(self.nodes)):
            for a in range(3):
                result[i, a] = result[i, a]/denom[i, a] if denom[i, a] else 0
        return result

    def conductance(self, C, weights, J):
        descriptor = self.rows(C, weights)
        out = []
        for e, edge in enumerate(self.edges):
            u, v = self.index[edge['tail']['node_id']], self.index[edge['head']['node_id']]
            contrast = sum((descriptor[u, a]-descriptor[v, a])**2 for a in range(3))
            exponent = number(COEFFICIENT)*(C[u]+C[v]+contrast+J[e]**2)/2
            out.append(max(mp.mpf('0.5'), mp.exp(-exponent)))
        return mp.matrix(out)

    def star(self, v):
        endpoints = [{e['tail']['node_id'], e['head']['node_id']} for e in self.edges]
        return mp.matrix([[v[i]*v[j]*(1 if i == j else mp.mpf('0.5')
                          if endpoints[i] & endpoints[j] else 0)
                          for j in range(len(self.edges))] for i in range(len(self.edges))])

    def read(self, candidate, C, W, H):
        if candidate == 'A':
            mobility = mp.diag(W)
            phi = self.B*mobility*self.B.T*C + number(KAPPA_AH)*self.B*(H-self.I)*self.B.T*C
            baseline = -mobility*self.B.T*phi
            drive = self.conductance(C, W, baseline)
            q = mp.matrix([(w-g)/(w+g) for w, g in zip(W, drive)])
            J = mp.matrix([b/(1-number(ZETA*CHI_A)*s) for b, s in zip(baseline, q)])
            causal = number(CHI_A)*mp.diag(q)*J
            extra = dict(q=q, drive=drive)
        else:
            # The proved constant-sector chart gives T=mean(C)*1, hence
            # D_C is scalar. Keep the full normative Q similarity here;
            # a separate test checks the independently simplified inverse.
            t = mp.exp(number(KAPPA_M)*mp.tanh(sum(C)/len(C)))
            retained = t*H
            phi = self.B*retained*self.B.T*C
            baseline = -self.B.T*phi
            ident = retained*(H**-1)
            Qmap = ident*(H**-1)
            response = (self.I + self.B.T*self.B*retained)**-1
            flux_response = Qmap**-1*response*Qmap
            J = mp.lu_solve(self.I-number(ZETA*CHI_C)*flux_response, baseline)
            causal = number(CHI_C)*flux_response*J
            extra = dict(t=t, flux_response=flux_response)
        flat = mp.lu_solve(H, causal)
        source = number(ZETA)*self.star(flat)
        return dict(J=J, baseline=baseline, causal=causal, source=source, **extra)

    def ordinary_os(self, candidate, C, W):
        predictor = self.read(candidate, C, W, self.I)
        H = self.I+number(KAPPA_H)*predictor['source']
        read = self.read(candidate, C, W, H)
        after = C-number(DT)*self.B*read['J']
        if candidate == 'A':
            # Incoming W is the proposed frozen descriptor-weight binding.
            # Final C is fresh, selected corrector J is retained, one writer.
            drive = self.conductance(after, W, read['J'])
            decay = mp.exp(-number(DT))  # tau_A = 1
            next_W = mp.matrix([mp.exp(decay*mp.log(w)+(1-decay)*mp.log(g))
                                for w, g in zip(W, drive)])
        else:
            drive, next_W = None, None
        return after, next_W, dict(predictor=predictor, read=read, H=H, writer_drive=drive)


def independent_drive(model, C, W, J):
    """Review-supplied endpoint-row oracle; never calls rows()/conductance()."""
    cells = [[[] for _ in range(3)] for _ in model.nodes]
    for e, edge in enumerate(model.edges):
        for end, other in ((edge['tail'], edge['head']), (edge['head'], edge['tail'])):
            i, j = model.index[end['node_id']], model.index[other['node_id']]
            cells[i][(end['port']-1)//3].append((W[e], C[j]-C[i]))
    rows = [[sum(w*c for w,c in cell)/sum(w for w,c in cell) if cell else mp.mpf(0)
             for cell in vertex] for vertex in cells]
    values = []
    for e, edge in enumerate(model.edges):
        u, v = model.index[edge['tail']['node_id']], model.index[edge['head']['node_id']]
        contrast = sum((rows[u][a]-rows[v][a])**2 for a in range(3))
        exponent = number(COEFFICIENT)*(C[u]+C[v]+contrast+J[e]**2)/2
        values.append(max(mp.mpf('0.5'), mp.exp(-exponent)))
    return mp.matrix(values)


class _AuditMutation(ast.NodeTransformer):
    """Four review-supplied kernel mutations; no constants/files are changed."""
    def __init__(self, mode):
        self.mode, self.method, self.hits = mode, None, 0

    def visit_FunctionDef(self, node):
        old = self.method
        self.method = node.name
        out = self.generic_visit(node)
        self.method = old
        return out

    def visit_Assign(self, node):
        if (self.mode == 'C_constant_modulation' and self.method == 'read'
                and any(isinstance(t, ast.Name) and t.id == 't' for t in node.targets)):
            node.value = ast.parse('mp.mpf(1)', mode='eval').body
            self.hits += 1
        if (self.mode == 'A_frozen_writer' and self.method == 'ordinary_os'
                and any(isinstance(t, ast.Name) and t.id == 'next_W' for t in node.targets)):
            node.value = ast.parse('W.copy()', mode='eval').body
            self.hits += 1
        return self.generic_visit(node)

    def visit_Call(self, node):
        if (self.mode == 'A_no_geometry_consumer' and self.method == 'read'
                and isinstance(node.func, ast.Name) and node.func.id == 'number'
                and len(node.args) == 1 and isinstance(node.args[0], ast.Name)
                and node.args[0].id == 'KAPPA_AH'):
            self.hits += 1
            return ast.copy_location(ast.Constant(value=0), node)
        if (self.mode == 'A_stale_wrong_current_writer' and self.method == 'ordinary_os'
                and isinstance(node.func, ast.Attribute) and node.func.attr == 'conductance'):
            node.args = ast.parse("(C,W,read['baseline'])", mode='eval').body.elts
            self.hits += 1
        return self.generic_visit(node)


class FixedRowBoundTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        boundary.BoundaryContinuationTests.setUpClass()
        cls.layouts = boundary.BoundaryContinuationTests.layouts
        cls.source = boundary.BoundaryContinuationTests.source

    def test_exact_uniform_budgets_close_the_finite_horizon(self):
        b = exact_budgets()
        self.assertLess(b['exponent'], WIDTH)
        self.assertLess(b['a_rate_error'], Q(1, 96))
        self.assertLess(b['c_rate_error'], Q(1, 96))
        self.assertLess(b['a_source'], CARRIER_RADIUS)
        self.assertLess(b['c_source'], CARRIER_RADIUS)
        self.assertLess(2*(1+WIDTH)*(72*(1+WIDTH)+144*RHO),1024)
        self.assertLess(144*(1+2*KAPPA_M)*(1+4*RHO),1024)
        self.assertLess(288*(1+WIDTH),300)
        theta_a = ZETA*CHI_A*b['qmax']
        q_h = COEFFICIENT*1024*300
        self.assertLess(300/(1-theta_a)+1024*ZETA*CHI_A*q_h/(1-theta_a)**2,400)
        theta_c = ZETA*CHI_C*8
        self.assertLess((2048+ZETA*CHI_C*9216*2048)/(1-theta_c),4096)
        self.assertLess(b['a_geometry_contraction'],Q(1,100000))
        self.assertLess(b['c_geometry_contraction'],Q(1,100000))
        self.assertLess(4/(1-RHO)**2, 5)
        self.assertLess(2*KAPPA_H*CARRIER_RADIUS, RHO)
        K = 1+100*DT
        self.assertLess(K**HORIZON, 2)
        self.assertLess(sum(K**k for k in range(HORIZON)), 12)
        self.assertLess(14*DT/96, RESOURCE_MARGIN/2)
        self.assertLess(K**HORIZON*Q(193,64)+14*DT/96, 4)
        self.assertLess(Q(4)+DT*(1296+Q(1,96)), 5)
        self.assertGreater(OUTSIDE_OFFSET-2*DT/96, 0)

    def test_fixed_rows_match_exact_weighted_formula_on_all_layouts(self):
        with mp.workdps(70):
            for row in self.layouts:
                edges, nodes = normalized_target(row)
                model = FixedRows(nodes, edges)
                vals = {n: Q((i*7)%13, 5) for i,n in enumerate(nodes)}
                weights = [Q(2+i, 19) for i in range(len(edges))]
                actual = model.rows(model.vector(vals), mp.matrix(list(map(number, weights))))
                for n in nodes:
                    for a in range(3):
                        terms = []
                        for e, edge in enumerate(edges):
                            for end, other in ((edge['tail'], edge['head']), (edge['head'], edge['tail'])):
                                if end['node_id'] == n and (end['port']-1)//3 == a:
                                    terms.append((weights[e], vals[other['node_id']]-vals[n]))
                        expected = sum(w*c for w,c in terms)/sum(w for w,c in terms) if terms else Q(0)
                        self.assertLess(abs(actual[model.index[n],a]-number(expected)), mp.mpf('1e-65'))

    def test_fixed_geometry_current_and_writer_stage_discriminators(self):
        with mp.workdps(70):
            edges, nodes = normalized_target(self.layouts[-1])
            model = FixedRows(nodes, edges)
            C = model.vector(resources(nodes,Q(3)))
            W = mp.matrix([number(1-WIDTH)]*len(edges))
            H = model.I.copy()
            # A genuine supported non-diagonal perturbation, not a scalar H.
            pair = next((i,j) for i,e in enumerate(edges) for j,f in enumerate(edges)
                        if i < j and {e['tail']['node_id'],e['head']['node_id']} &
                        {f['tail']['node_id'],f['head']['node_id']})
            for i in pair:
                for j in pair:
                    H[i,j] += number(RHO)/8
            eigenvalues = mp.eigsy(model.B*H*model.B.T, eigvals_only=True)
            self.assertLess(abs(eigenvalues[0]), mp.mpf('1e-65'))
            self.assertGreater(eigenvalues[1], mp.mpf(1)/512)
            for candidate in ('A','C'):
                r = model.read(candidate,C,W if candidate == 'A' else None,H)
                if candidate == 'A':
                    independent = mp.lu_solve(model.I-number(ZETA*CHI_A)*mp.diag(r['q']),r['baseline'])
                    after = C-number(DT)*model.B*r['J']
                    fresh = model.conductance(after,W,r['J'])
                    stale_C = model.conductance(C,W,r['J'])
                    wrong_J = model.conductance(after,W,r['baseline'])
                    self.assertGreater(norm_inf(fresh-stale_C),mp.mpf('1e-30'))
                    self.assertGreater(norm_inf(fresh-wrong_J),mp.mpf('1e-35'))
                else:
                    independent_response = (model.I+r['t']*H*model.B.T*model.B)**-1
                    self.assertLess(mp.norm(independent_response-r['flux_response']),mp.mpf('1e-65'))
                    independent = mp.lu_solve(model.I-number(ZETA*CHI_C)*independent_response,r['baseline'])
                self.assertLess(norm_inf(independent-r['J']),mp.mpf('1e-65'))
                self.assertGreater(mp.norm(r['source']),0)
                self.assertLess(mp.norm(r['source']),number(CARRIER_RADIUS))
                error = -model.B*r['J']-model.L**2*C
                self.assertLess(norm_inf(error),number(exact_budgets()[candidate.lower()+'_rate_error']))

    def audit_inputs(self):
        """Review's nondegenerate fixture, using the actual D52 vector ports."""
        vector = self.layouts[-1]
        self.assertEqual(vector['request']['target_effective_degree'], 52)
        edges, nodes = normalized_target(vector)
        model = FixedRows(nodes, edges)
        C = model.vector(resources(nodes, Q(3)))
        W = mp.matrix([number(1+WIDTH*((e % 3)-1)) for e in range(len(edges))])
        ends = [{e['tail']['node_id'], e['head']['node_id']} for e in edges]
        # Find a supported test perturbation with nonzero affine response.
        # This fixture search is neither a topology selector nor a root solve.
        for i in range(len(edges)):
            for j in range(i+1, len(edges)):
                if not ends[i] & ends[j]:
                    continue
                D = mp.matrix(len(edges), len(edges))
                for k in (i, j):
                    for ell in (i, j):
                        D[k,ell] = number(RHO)/8
                effect = -number(KAPPA_AH)*mp.diag(W)*(model.B.T*model.B)*D*(model.B.T*C)
                if norm_inf(effect) > mp.mpf('1e-12'):
                    return model, C, W, model.I+D, effect
        self.fail('Test fixture supplies no nonzero supported A geometry discriminator')

    def test_a_geometry_is_consumed_by_the_baseline(self):
        with mp.workdps(70):
            model, C, W, H, want = self.audit_inputs()
            at_H = model.read('A', C, W, H)
            at_I = model.read('A', C, W, model.I)
            got = at_H['baseline']-at_I['baseline']
            self.assertGreater(norm_inf(want), mp.mpf('1e-12'))
            self.assertLess(norm_inf(got-want), mp.mpf('1e-60'),
                            'A baseline must consume geometry')

    def test_c_selected_modulation_is_consumed(self):
        with mp.workdps(70):
            model, C, W, H, _ = self.audit_inputs()
            result = model.read('C', C, None, H)
            t = mp.exp(number(KAPPA_M)*mp.tanh(sum(C)/len(C)))
            unmodulated = -(model.B.T*model.B)*H*(model.B.T*C)
            want = t*unmodulated
            self.assertGreater(abs(t-1), mp.mpf('1e-9'))
            self.assertGreater(norm_inf(want-unmodulated), mp.mpf('1e-9'))
            self.assertLess(abs(result['t']-t), mp.mpf('1e-60'),
                            'C modulation must be computed from selected content')
            self.assertLess(norm_inf(result['baseline']-want), mp.mpf('1e-60'),
                            'C baseline must consume modulation')

    def test_os_writer_uses_fresh_resource_selected_current_and_old_weights(self):
        with mp.workdps(70):
            model, C, W, H, _ = self.audit_inputs()
            after, actual_W, stages = model.ordinary_os('A', C, W)
            selected = stages['read']['J']
            wanted_drive = independent_drive(model, after, W, selected)
            a = mp.exp(-number(DT))
            wanted_W = mp.matrix([mp.exp(a*mp.log(w)+(1-a)*mp.log(g))
                                  for w,g in zip(W,wanted_drive)])
            stale = independent_drive(model, C, W, selected)
            wrong_J = independent_drive(model, after, W, stages['read']['baseline'])
            self.assertGreater(norm_inf(wanted_drive-stale), mp.mpf('1e-40'))
            self.assertGreater(norm_inf(wanted_drive-wrong_J), mp.mpf('1e-40'))
            self.assertGreater(norm_inf(wanted_W-W), mp.mpf('1e-14'))
            self.assertLess(norm_inf(stages['writer_drive']-wanted_drive), mp.mpf('1e-60'),
                            'OS writer drive must use fresh C and selected J')
            self.assertLess(norm_inf(actual_W-wanted_W), mp.mpf('1e-60'),
                            'OS retained history must execute the log writer')

    def test_review_mutations_are_rejected_on_actual_vector_inputs(self):
        source = next(n for n in ast.parse(Path(__file__).read_text()).body
                      if isinstance(n, ast.ClassDef) and n.name == 'FixedRows')
        cases = (
            ('A_no_geometry_consumer', 'test_a_geometry_is_consumed_by_the_baseline',
             'A baseline must consume geometry'),
            ('C_constant_modulation', 'test_c_selected_modulation_is_consumed',
             'C modulation must be computed from selected content'),
            ('A_frozen_writer', 'test_os_writer_uses_fresh_resource_selected_current_and_old_weights',
             'OS retained history must execute the log writer'),
            ('A_stale_wrong_current_writer', 'test_os_writer_uses_fresh_resource_selected_current_and_old_weights',
             'OS writer drive must use fresh C and selected J'),
        )
        for mode, method, message in cases:
            with self.subTest(mutation=mode):
                mutation = _AuditMutation(mode)
                changed = mutation.visit(copy.deepcopy(source))
                self.assertEqual(mutation.hits, 1)
                # Compile only the mutated class into a separate namespace;
                # unlike the isolated review, use the real repository setup.
                namespace = dict(globals())
                tree = ast.fix_missing_locations(ast.Module(body=[changed], type_ignores=[]))
                exec(compile(tree, '<in-memory-audit-mutation>', 'exec'), namespace)
                with patch.dict(globals(), {'FixedRows': namespace['FixedRows']}):
                    with self.assertRaisesRegex(AssertionError, message):
                        getattr(self, method)()

    def test_raw_split_bound_and_source_publication_rounding_limit(self):
        with mp.workdps(70):
            source = FixedRows(self.source['live_node_ids'], self.source['edges'])
            desired = {n: Q(3) if n == 'source-s' else Q(3)+OUTSIDE_OFFSET
                       for n in source.nodes}
            C = source.vector(preimage(source.edges, desired))
            budgets = exact_budgets()
            for candidate in ('A', 'C'):
                with self.subTest(candidate=candidate):
                    W = mp.matrix([number(1-WIDTH)]*len(source.edges)) if candidate == 'A' else None
                    _, _, stages = source.ordinary_os(candidate, C, W)
                    H = stages['H']
                    raw = mp.norm(H-(source.I+number(KAPPA_H)*stages['read']['source']))
                    key = candidate.lower()
                    ceiling = budgets[key+'_geometry_contraction']*KAPPA_H*budgets[key+'_source']
                    self.assertLess(raw, number(ceiling))
                    self.assertGreater(mp.norm(H-source.I), 0)
                    self.assertGreater(norm_inf(stages['predictor']['J']-stages['read']['J']), 0)
                    # Publication-only binary64 comparison, NOT a staged
                    # native solve or a claim that the whole H becomes I.
                    self.assertEqual(tuple(map(float, stages['predictor']['J'])),
                                     tuple(map(float, stages['read']['J'])))
                    self.assertTrue(all(float(H[i,i]) == 1 for i in range(H.rows)))
                    self.assertTrue(any(float(H[i,j]) != 0 for i in range(H.rows)
                                        for j in range(H.cols) if i != j))

    def test_enabled_os_source_event_and_ten_step_research_chains(self):
        with mp.workdps(70):
            edges, nodes = normalized_target(self.layouts[-1])
            target = FixedRows(nodes,edges)
            source = FixedRows(self.source['live_node_ids'],self.source['edges'])
            for candidate in ('A','C'):
                for role,S in (('current',Q(3)),('reset',Q(2))):
                    with self.subTest(candidate=candidate,role=role):
                        desired = {n:S if n=='source-s' else S+OUTSIDE_OFFSET for n in source.nodes}
                        W = mp.matrix([number(1-WIDTH)]*len(source.edges)) if candidate=='A' else None
                        if role == 'current':
                            before = source.vector(preimage(source.edges,desired))
                            post, Wpost, _ = source.ordinary_os(candidate,before,W)
                        else:
                            # Reset is independently supplied, NOT evolved by
                            # the live ordinary beat. Its later continuation
                            # below is a separate hypothetical reset-and-run.
                            post, Wpost = source.vector(desired), W
                        self.assertLess(norm_inf(post-source.vector(desired)),number(DT/96))
                        center = source.index['source-s']
                        if role == 'current':
                            rows = source.rows(post,Wpost if candidate=='A' else mp.matrix([1]*len(source.edges)))
                            self.assertTrue(all(rows[center,a]>0 for a in range(3)))
                            self.assertLess(sum(rows[center,a]**2 for a in range(3)),mp.mpf('0.25'))
                        values = {n:post[source.index[n]] if n.startswith('outside-') else
                                  post[center]/3 if n.startswith('satellite/') else 0 for n in nodes}
                        C = target.vector(values)
                        old_history = {e['edge_id']:Wpost[i] for i,e in enumerate(source.edges)} if candidate=='A' else {}
                        self.assertTrue(set(old_history) <= {e['edge_id'] for e in edges})
                        W = mp.matrix([old_history.get(e['edge_id'],mp.mpf(1)) for e in edges]) if candidate=='A' else None
                        reference = resources(nodes,S)
                        charge = sum(post)
                        for k in range(1,HORIZON+1):
                            C,W,stages = target.ordinary_os(candidate,C,W)
                            reference = step(edges,reference)
                            self.assertGreater(min(C),number(RESOURCE_MARGIN/2))
                            self.assertLess(max(C),4)
                            self.assertLess(abs(sum(C)-charge),mp.mpf('1e-60'))
                            self.assertLess(norm_inf(C-target.vector(reference)),number(14*DT/96))
                            self.assertGreater(mp.norm(stages['H']-target.I),0)
                            self.assertLess(mp.norm(stages['H']-target.I),number(RHO))
                            self.assertGreater(mp.norm(stages['read']['causal']),0)
                            if candidate=='A':
                                self.assertGreaterEqual(min(W),number(1-WIDTH))
                                self.assertLessEqual(max(W),number(1+WIDTH))


if __name__ == '__main__':
    unittest.main()

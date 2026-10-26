"""Certified solution reuse cannot substitute for fresh scientific admission."""
from concurrent.futures import ThreadPoolExecutor
from contextlib import ExitStack
from dataclasses import replace
import importlib.util
import math
import unittest
from unittest.mock import patch

if importlib.util.find_spec('flint') is None:
    raise unittest.SkipTest('explicit FLINT policy required')

from pygrc.models import grc_v4_certification as cert
from pygrc.models import grc_v4_numerics as num
from pygrc.models import grc_v4_linear as linear
from pygrc.models.grc_v4_codec import _OPERATION_CONTEXT
from tests.models.test_grc_v4_candidate_c import current_fixture

A=((3.,1.),(1.,3.))
B=((1.,),(2.,))


class CertifiedSolveReuseTests(unittest.TestCase):
    def setUp(self):
        self.stack=ExitStack()
        self.addCleanup(self.stack.close)
        self.stack.enter_context(num.exact_backend(num.ExactBackend.FLINT))
        self.stack.enter_context(num.numerical_policy(num.NumericalPolicy.CERTIFIED_ARB_256))
        self.policy=current_fixture().geometry.reference.profile.params_resolved.solver

    def solve(self,a=A,b=B,policy=None,label='test'):
        certificates=[]
        result=num.solve(a,b,policy or self.policy,label,certificates)
        return result,certificates

    def test_identical_operands_hit_but_every_residual_and_label_is_fresh(self):
        with num.matrix_operation(), patch.object(cert,'rounded_solve',wraps=cert.rounded_solve) as solve, patch.object(num,'residual_pass',wraps=num.residual_pass) as residual:
            first=self.solve()
            same_a=tuple(tuple(x for x in row) for row in A)
            self.assertEqual(self.solve(same_a),first)
            renamed=self.solve(label='new stage')
            self.assertEqual(renamed[0],first[0])
            self.assertTrue(all(c['block']=='new stage' for c in renamed[1]))
            self.assertEqual(solve.call_count,1)
            self.assertEqual(residual.call_count,3)
            self.assertEqual(len(_OPERATION_CONTEXT.get().matrix_facts._solves),1)

    def test_changed_inputs_and_fresh_policy(self):
        with num.matrix_operation(), patch.object(cert,'rounded_solve',wraps=cert.rounded_solve) as solve:
            self.solve()
            self.solve(b=((math.nextafter(1.,2.),),(2.,)))
            self.solve(a=((math.nextafter(3.,4.),1.),(1.,3.)))
            self.assertEqual(solve.call_count,3)
        with num.matrix_operation(reuse=num.MatrixReuse.FRESH), patch.object(cert,'rounded_solve',wraps=cert.rounded_solve) as solve:
            first=self.solve()
            self.assertEqual(self.solve(),first)
            self.assertEqual(solve.call_count,2)
            self.assertFalse(_OPERATION_CONTEXT.get().matrix_facts._solves)

    def test_stricter_conditions_and_residuals_still_fail_after_warm_success(self):
        with num.matrix_operation(), patch.object(cert,'rounded_solve',wraps=cert.rounded_solve) as solve:
            self.solve()
            with self.assertRaises(cert.CertificationInconclusive):
                self.solve(policy=replace(self.policy,conditioning_limit=1.))
            self.solve(a=((3.,),),b=((1.,),))
            for _ in range(2):
                with self.assertRaises(num.MatrixError):
                    self.solve(a=((3.,),),b=((1.,),),policy=replace(self.policy,absolute_tolerance=0.,relative_tolerance=0.))
            self.assertEqual(solve.call_count,2)

    def test_failures_never_populate_cache_or_fall_back(self):
        with num.matrix_operation(), patch.object(cert,'rounded_solve',side_effect=cert.CertificationInconclusive('pressure')) as solve, patch.object(num._backend,'inverse',side_effect=AssertionError('hidden fallback')):
            for _ in range(2):
                with self.assertRaises(cert.CertificationInconclusive):self.solve()
            self.assertEqual(solve.call_count,2)
            self.assertFalse(_OPERATION_CONTEXT.get().matrix_facts._solves)
        with num.matrix_operation():
            with self.assertRaises(num.MatrixError):
                self.solve(a=((3.,),),b=((1.,),),policy=replace(self.policy,absolute_tolerance=0.,relative_tolerance=0.))
            self.assertFalse(_OPERATION_CONTEXT.get().matrix_facts._solves)

    def test_scope_nesting_exception_cleanup_and_execution_identity(self):
        with patch.object(cert,'rounded_solve',wraps=cert.rounded_solve) as solve:
            with num.matrix_operation():
                self.solve()
                parent=_OPERATION_CONTEXT.get()
                with self.assertRaisesRegex(RuntimeError,'abort'),num.matrix_operation():
                    self.solve()
                    raise RuntimeError('abort')
                self.assertIs(_OPERATION_CONTEXT.get(),parent)
                self.solve()
                with num.numerical_policy(num.NumericalPolicy.LEGACY_EXACT):
                    with self.assertRaisesRegex(TypeError,'numerical policy'):
                        parent.matrix_facts.find_solve(num.exact_matrix(A),num.exact_matrix(B))
                with num.exact_backend(num.ExactBackend.PYTHON):
                    with self.assertRaisesRegex(TypeError,'backend'):
                        parent.matrix_facts.find_solve(num.exact_matrix(A),num.exact_matrix(B))
                continuation=parent.matrix_facts.retain(num.exact_matrix(A),num.exact_matrix(A),num.exact_number(self.policy.conditioning_limit))
                self.assertTrue(all(type(f) is not linear._RoundedSolveFact for f in continuation.facts))
            self.assertIsNone(_OPERATION_CONTEXT.get())
            self.solve()
            self.solve()
            self.assertEqual(solve.call_count,4)

    def test_lru_and_cell_budgets_are_bounded_and_do_not_affect_results(self):
        with num.matrix_operation(),patch.object(linear,'_MAX_ROUNDED_SOLVES',1),patch.object(cert,'rounded_solve',wraps=cert.rounded_solve) as solve:
            original=self.solve()
            self.solve(b=((2.,),(1.,)))
            self.assertEqual(self.solve(),original)
            self.assertEqual(solve.call_count,3)
            store=_OPERATION_CONTEXT.get().matrix_facts
            self.assertEqual(len(store._solves),1)
            self.assertEqual(store._solve_cells,8)
        with num.matrix_operation(),patch.object(linear,'_MAX_ROUNDED_SOLVE_CELLS',7):
            self.assertEqual(self.solve(),original)
            self.assertFalse(_OPERATION_CONTEXT.get().matrix_facts._solves)

    def test_thread_scopes_do_not_share_solutions(self):
        def run(_):
            with num.exact_backend(num.ExactBackend.FLINT),num.numerical_policy(num.NumericalPolicy.CERTIFIED_ARB_256),num.matrix_operation():
                result=self.solve()
                store=_OPERATION_CONTEXT.get().matrix_facts
                return result,store
        with ThreadPoolExecutor(2) as pool: rows=list(pool.map(run,range(2)))
        self.assertEqual(rows[0][0],rows[1][0])
        self.assertIsNot(rows[0][1],rows[1][1])


if __name__=='__main__':unittest.main()

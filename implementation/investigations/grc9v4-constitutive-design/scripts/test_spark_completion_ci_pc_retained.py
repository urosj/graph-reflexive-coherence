"""Regression for outward residual diagnostics and complete retained reads."""
from copy import deepcopy
import unittest
from flint import ctx
import check_spark_completion_ci_pc_retained as retained
from spark_completion_ci_pc_campaign import read_payload


class RetainedDiagnostics(unittest.TestCase):
    def test_outward_negative_lower_bound_and_independent_proposal_diagnostics(self):
        with ctx.workprec(512):
            _,_,targets=retained.fixture();m=retained.CCIPCReference(targets['1']['graph'])
            C=m.matrix([[m.q(1)+m.q(i,32)]for i in range(m.n)])
            fresh=m.ccipc_read(C,m.zero());saved=read_payload(fresh)
            self.assertLess(retained.F(saved['root_residual'][0]),0)
            retained.check_read(saved,fresh)
            # These scalars describe different proposal/input-width bounds.
            diagnostic=deepcopy(saved);diagnostic['root_residual']=['0','0']
            retained.check_read(diagnostic,fresh)
            for field in ('root_residual','root_error'):
                bad=deepcopy(saved);bad[field]=['-1/1024','-1/1024']
                with self.assertRaises(ValueError):retained.check_read(bad,fresh)
            for field in ('H','J','flat','S'):
                bad=deepcopy(saved);bad[field][0][0]=['2','2']
                with self.assertRaises(ValueError):retained.check_read(bad,fresh)


if __name__=='__main__':unittest.main()

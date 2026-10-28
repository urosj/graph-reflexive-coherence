"""Pressure signed OS covariance, unsigned W, and exact target transport."""
from copy import deepcopy
import unittest
import p984h_aos_covariance as c


class AOSLargeCovarianceTests(unittest.TestCase):
    def test_saved_signed_counterpart_and_mutations(self):
        m=c.n.g.storage.read(c.INPUTS)
        with c.n.policy():
            for segment in ('event',*c.ROLES):
                v=c.read('signed',segment)
                self.assertEqual(v['covariance_errors'],c.check(v,'signed',segment,m))
            for field in ('W_A','C'):
                v=deepcopy(c.read('signed','current'))
                v['execution']['after']['current'][field][0]+=1e-4
                with self.subTest(field=field),self.assertRaises(ValueError):
                    c.check(c.b.seal(v),'signed','current',m)
            v=deepcopy(c.read('signed','event'));v['execution']['request']['resource_distribution']=[.5,.25,.25]
            with self.assertRaises(ValueError):c.check(c.b.seal(v),'signed','event',m)


if __name__=='__main__':unittest.main()

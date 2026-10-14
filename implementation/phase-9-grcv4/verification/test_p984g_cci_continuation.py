"""Sign pressure: exact nominal resource, whole-root error, no clipping."""
import unittest
from copy import deepcopy
import p984g_cci_continuation as p


class ContinuationBounds(unittest.TestCase):
    def test_row_norm_error_and_zero_boundary(self):
        with p.staged.ctx.workprec(192):
            rows=p.enclose([[1,-1]], [0], [1,0], p.q('1/4'), p.q('1/10'))
            self.assertLess(rows[0][1],0)
            uncertain=p.enclose([[1,-1]], [0], [1,0], p.q('1/4'),1)
            self.assertLess(uncertain[0][0],0);self.assertGreater(uncertain[0][1],0)
            self.assertEqual(p.enclose([[1,-1]],[0],[1,1],1,0),[(0,0)])
            # Error must include both entries, not just a chosen bad edge.
            self.assertGreater(rows[0][1]-p.q('-1/4'),p.q('1/40'))
            with self.assertRaises(ValueError):p.enclose([[1]],[0],[1],1,-1)

    def test_no_rounding_before_nominal_continuity(self):
        # Built-in floating sums can lose this half-ULP correction; proof uses
        # exact dyadics and the retained whole-root error, not the rounded sign.
        v=1+2**-52
        rows=p.enclose([[1]],[1],[v],1,0)
        self.assertEqual(rows,[(-p.q(2**-52),-p.q(2**-52))])

    def test_retained_exclusion_cannot_be_promoted_or_erased(self):
        value=p.check()
        targets=[c for c in value['cases'] if c['graph']=='target']
        self.assertEqual(len(targets),2)
        for c in targets:
            self.assertLess(p.q(c['exact_root_resource_minimum_upper']),0)
            self.assertTrue(c['certified_negative_vertices'][0]['excluded_for_every_positive_dt_at_this_state'])
        changed=deepcopy(value);changed['cases'][2]['certified_negative_vertices']=[]
        with self.assertRaises(ValueError):p.check(p.staged.seal(changed))


if __name__=='__main__':unittest.main()

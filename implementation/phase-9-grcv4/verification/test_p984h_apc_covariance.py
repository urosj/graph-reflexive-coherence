"""Small transport pressure before the bounded large counterpart batch."""
from contextlib import ExitStack
from dataclasses import replace
import unittest
from unittest.mock import patch
import numpy as np
import p984h_apc_covariance as v
from test_p984h_apc_campaign import fixture


class CovarianceTests(unittest.TestCase):
    def test_continuation_uses_actual_event_target_without_rebuilding_source(self):
        from unittest.mock import patch
        with patch.object(v,'subject',side_effect=AssertionError('source reconstruction forbidden')), \
                patch.object(v,'step_inputs',return_value=('actual_target','event_digest')), \
                patch.object(v.c,'observe',return_value={'native_steps':1}) as observed:
            self.assertEqual(v.execute('reflect','reset',lambda s:None),({'native_steps':1},'event_digest'))
            observed.assert_called_once_with('actual_target')

    def setUp(self):
        self.stack=ExitStack();self.addCleanup(self.stack.close)
        p=v.c.prep
        self.stack.enter_context(p.exact_backend(p.ExactBackend.FLINT))
        self.stack.enter_context(p.numerical_policy(p.NumericalPolicy.CERTIFIED_ARB_256))
        self.stack.enter_context(p.matrix_operation())

    def test_signed_carrier_geometry_and_unsigned_history_are_distinct(self):
        before=fixture();z=(.001,.0002,0.,.0002,-.001,.0001,0.,.0001,.002)
        authority=replace(before.current,Z_4=z)
        before=replace(before,current=authority,geometry=v.c.pc.carrier_geometry(before,authority))
        payload=before.to_payload();base=({'inputs':payload},{})
        with patch.object(v,'baseline',return_value=base),v.transport():
            for kind in v.KINDS:
                d=v.maps.declaration(kind);graph=v.maps.graph_image(payload['reference']['graph'],d,source=True)
                mapped=v.input_image(payload,graph,d)
                ni,ei,sign=v.maps.mapping(payload['reference']['graph'],graph,d)
                self.assertEqual(mapped.current.W_A,tuple(before.current.W_A[i] for i in ei))
                expected=np.array(z).reshape(3,3)[np.ix_(ei,ei)]*np.outer(sign,sign)
                self.assertEqual(v.c.zrows(mapped.current),expected.tolist())
                self.assertEqual(mapped.geometry,v.c.pc.carrier_geometry(mapped,mapped.current))
                self.assertNotEqual(mapped.current,mapped.reset)
                if kind=='signed':self.assertNotEqual(v.c.zrows(mapped.current),np.array(z).reshape(3,3).tolist())

    def test_controls_and_roster_fail_closed(self):
        self.assertEqual(len(v.KINDS),8)
        self.assertEqual(v.conjugate([[1.,2.],[2.,3.]],[1,0],[-1,1]),[[3.,-2.],[-2.,1.]])
        self.assertEqual(v.compare([1.],[1.],'equal'),0.)
        for a,b in (([1.],[2.]),([float('nan')],[0.]),([1.],[1.,2.])):
            with self.assertRaises(ValueError):v.compare(a,b,'bad')
        with self.assertRaises(ValueError):v.path('unknown','event')


if __name__=='__main__':unittest.main()

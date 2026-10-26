import math
from types import SimpleNamespace
import unittest
import p984h_aci_charge_successor as s
from pygrc.models.grc_v4_transport import ChargeEvaluation
from pygrc.models.grc_v4_geometry import VertexScalar


class ChargeTests(unittest.TestCase):
    def test_exact_boundary_and_just_outside(self):
        policy=SimpleNamespace(absolute_tolerance=1e-11,relative_tolerance=0.)
        self.assertEqual(s.charge_fields([0.],0.,policy)['residual'],0.)
        self.assertEqual(s.charge_fields([1e-11],0.,policy)['residual'],1e-11)
        with self.assertRaises(ValueError):s.charge_fields([math.nextafter(1e-11,math.inf)],0.,policy)
        relative=SimpleNamespace(absolute_tolerance=0.,relative_tolerance=2**-40)
        s.charge_fields([200.+2**-33],200.,relative)
        with self.assertRaises(ValueError):s.charge_fields([200.+2**-31],200.,relative)

    def test_real_profile_native_agreement_and_receipt_mutations(self):
        before,_=s.c.incoming('step','current',8)
        profile=before.geometry.reference.profile;graph=before.geometry.reference.graph
        values=[r['represented'] for r in s.c.read('step','current',7)['execution']['roots']['final']['oracle']['resources']]
        fields=s.charge_fields(values,before.Q_target,profile.params_resolved.charge)
        native=ChargeEvaluation(VertexScalar(graph,tuple(values)),before.Q_target,profile)
        self.assertTrue(native.admitted);self.assertEqual(fields,native.receipt_values())
        self.assertEqual(fields['residual'],2**-45)
        after=SimpleNamespace(current=SimpleNamespace(C=values))
        e=dict(charge=fields,exact_resource_sum_delta=str(sum(map(s.c.q,values),s.c.q(0))-sum(map(s.c.q,before.current.C),s.c.q(0))))
        s.check_charge(e,before,after)
        with self.assertRaises(ValueError):s.check_charge({**e,'charge':{**fields,'residual':0.}},before,after)
        with self.assertRaises(ValueError):s.check_charge({**e,'exact_resource_sum_delta':'0'},before,after)


if __name__=='__main__':unittest.main()

from copy import deepcopy
import unittest

import p984h_ccipc_math as v
import p984b_ccipc_runtime as r
from p9_ccipc_compute import worker


class CompositeCertificateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with worker():
            cls.before = v.b.GeometryStageInputs.from_payload(v.b.read(r.INPUTS)['initial_inputs'])
            root = r.CandidateCIRoot(cls.before)
            cls.value = v.capture_read(root)
            cls.original = r.independent_certificate(cls.before,cls.value)

    def test_independent_joint_bridge_and_signed_equations(self):
        with worker():
            v.check_read(self.before,self.value,numerics=True)
        bridge = self.value['certificate']['joint_root_error']
        self.assertLessEqual(v.q(self.original['bounds']['geometry_error']),v.q(bridge['geometry_error_upper']))

    def test_signed_read_corruption_is_detected(self):
        value = deepcopy(self.value)
        value['readback'] = [-x for x in value['readback']]
        with self.assertRaises(ValueError):
            v.certificate(self.before,value)

    def test_incorrect_fixed_carrier_is_detected(self):
        value = deepcopy(self.value)
        value['generated'][0][0] += 1e-6
        value = v.b.seal(value)
        with self.assertRaises(ValueError):
            v.check_read(self.before,value)


if __name__ == '__main__':
    unittest.main()

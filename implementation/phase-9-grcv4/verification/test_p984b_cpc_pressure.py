"""Outer-product sign blindness must not certify a signed intermediate."""

import unittest
from copy import deepcopy

import p984b_cpc_pressure as p


class SignedPressureTests(unittest.TestCase):
    def test_global_flat_sign_is_detected_even_when_source_is_identical(self):
        r, b = p.r, p.b
        manifest = r.make_manifest()
        before = b.GeometryStageInputs.from_payload(manifest["initial_inputs"])
        with b.exact_backend(b.ExactBackend.FLINT):
            value = r.certified_read(r.CandidatePCRead(before))
        p.check_vectors(before, value)
        for key in ("flat", "readback"):
            changed = deepcopy(value)
            changed[key] = [-x for x in changed[key]]
            self.assertEqual(changed["source"], value["source"])
            with (
                self.subTest(key=key),
                self.assertRaisesRegex(ValueError, "signed intermediate"),
            ):
                p.check_vectors(before, changed)


if __name__ == "__main__":
    unittest.main()

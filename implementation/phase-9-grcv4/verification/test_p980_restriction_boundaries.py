"""Focused R1–R7 boundaries; acceptance/provenance are not runtime predicates."""

import copy
import json
import unittest
from fractions import Fraction as Q

import numpy as np
import test_p980_ci_event_companion as ci
import test_p980_event_companion as common
import test_p980_realization_numerical as numerical
import test_p980_rg2b_numerical as rg
from test_p980_os_effect_witness import vector


class RestrictionBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.shared = json.loads(common.INPUT_PATH.read_text())
        cls.source, cls.target = ci.build_models(copy.deepcopy(cls.shared))

    def test_scope_and_schedule_neighbours_are_not_silently_admitted(self):
        common.validate_inputs(self.shared)
        cases = (
            [("request", "target_effective_degree", value) for value in (0, 51, 53, 58)]
            + [("request", "module_chirality", value) for value in (-1, 0)]
            + [("request", "growth_phase", value) for value in (2, 4)]
            + [("ordinary", "target_steps", value) for value in (0, 9, 11)]
            + [("ordinary", "source_current_steps", value) for value in (0, 2)]
            + [
                ("ordinary", "source_reset_steps", 1),
                ("ordinary", "duration", "1/2048"),
                ("ordinary", "split_tolerance", "1/549755813888"),
            ]
        )
        for section, field, value in cases:
            changed = copy.deepcopy(self.shared)
            changed[section][field] = value
            with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                common.validate_inputs(changed)
        self.assertEqual(len(cases), 16)

    def test_closed_carrier_ball_one_ulp_and_tiny_support_violations(self):
        radius = float(numerical.exact.CARRIER_RADIUS)
        for model in (self.source, self.target):
            m = len(model.edges)
            for value in (0.0, -0.0, np.nextafter(radius, 0), radius, -radius):
                z = np.zeros((m, m))
                z[0, 0] = value
                numerical.carrier_input(model, z)
            for value in (np.nextafter(radius, np.inf), np.nextafter(-radius, -np.inf)):
                z = np.zeros((m, m))
                z[0, 0] = value
                with self.subTest(value=value, edges=m), self.assertRaises(ValueError):
                    numerical.carrier_input(model, z)
        # A subnormal is small enough to disappear in naive squared norms, but
        # exact support and symmetry are mandatory independently of magnitude.
        m = len(self.target.edges)
        tiny = np.nextafter(0.0, 1.0)
        for supported in (True, False):
            i, j = next(
                (i, j)
                for i in range(m)
                for j in range(i + 1, m)
                if bool(self.target.mask[i, j]) == supported
            )
            z = np.zeros((m, m))
            z[i, j] = tiny
            with self.assertRaises(ValueError):
                numerical.carrier_input(self.target, z)
            z[j, i] = tiny
            if supported:
                numerical.carrier_input(self.target, z)
            else:
                with self.assertRaises(ValueError):
                    numerical.carrier_input(self.target, z)

    def test_rg_physical_resource_face_is_distinct_from_auxiliary_completion(self):
        # Physical resources admit zero but exclude four; the auxiliary global
        # completion's [-1,5] clamp never expands this physical query contract.
        for value in (0.0, -0.0, np.nextafter(0.0, 1.0), np.nextafter(4.0, 0.0)):
            rg.physical_input(vector([value]), None)
        for value in (
            -np.nextafter(0.0, 1.0),
            4.0,
            np.nextafter(4.0, np.inf),
            -1.0,
            5.0,
        ):
            with self.subTest(value=value), self.assertRaises(ValueError):
                rg.physical_input(vector([value]), None)
        rg.physical_input(vector([0]), vector([1]))
        for value in (0, -1, Q(1, 2), 2):
            with self.subTest(history=value), self.assertRaises(ValueError):
                rg.physical_input(vector([0]), vector([value]))


if __name__ == "__main__":
    unittest.main()

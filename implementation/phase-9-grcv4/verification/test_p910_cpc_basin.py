"""C_PC: committed carrier read, independent equations, and exact target crossings."""
from contextlib import ExitStack
from copy import copy, deepcopy
from dataclasses import replace
from fractions import Fraction
import unittest
from unittest.mock import patch

from pygrc.models import grc_9_v4_basin as basin
from pygrc.models.grc_v4_exact import ExactBackend, exact_backend
from pygrc.models.grc_v4_geometry import GRCV4Geometry, OneFormHodge
from tests.models import test_grc_9_v4 as public
from tests.models import test_grc_9_v4_basin as native
from tests.models import test_grc_9_v4_cpc_integration as prior
import p9101a_basin_oracle as oracle
import p9101c_target_basin as direct
import test_p9101b_target_compatibility as targets
import test_p910_aos_basin as shared

EVIDENCE = {}


def source_configuration(family):
    if family != "C_PC":
        raise ValueError("C_PC fixture provider")
    return dict(initial=targets.target_seed(family)["initial"],
                exact_backend="flint", numerical_policy="legacy_exact_v1")


class CPCNativeBasin(native.NativeBasinTests):
    FAMILY = "C_PC"

    @classmethod
    def setUpClass(cls):
        stack = ExitStack(); cls.addClassCleanup(stack.close)
        stack.enter_context(patch.object(native, "configuration", source_configuration))
        stack.enter_context(patch.object(native, "seed", targets.target_seed))
        stack.enter_context(patch.object(public, "native_config", prior.legacy_config))
        super().setUpClass()

    def test_committed_carrier_and_independent_equations(self):
        import pygrc.models.grc_v4_pc as pc
        from test_p980_os_effect_witness import IntervalRows
        model = self.model()
        saved = model._operation._published.owner.state
        before, lifetime = deepcopy(saved.to_payload()), model.lifecycle_digest
        with exact_backend(ExactBackend.FLINT), patch.object(pc.ProvisionalCandidatePCStep, "__post_init__",
                side_effect=AssertionError("diagnostic invoked writer")):
            pair = basin.capture_pair(saved)
            equations = {}
            for role, captured in zip(("current", "reset"), pair, strict=True):
                read, point = captured.read, captured.point
                self.assertIs(read.point, point)
                self.assertIsNone(point.inputs.current.W_A)
                self.assertTrue(any(point.inputs.current.Z_4))
                self.assertEqual(point.inputs.current.Z_4, getattr(saved.inputs, role).Z_4)
                self.assertEqual(point.inputs.stage, "pc_old_history")
                self.assertEqual(point.inputs, replace(read.inputs, stage="pc_old_history"))
                oracle.captured_inputs(saved, role, captured.observation.to_dict(), read, point)
                equations[role] = oracle.equation_check(saved, role, point)
                self.assertIn("pc-read", captured.observation["binding"]["root_certificate_binding"])
            self.assertNotEqual(saved.inputs.current.Z_4, saved.inputs.reset.Z_4)
            # A lawful zero-carrier counterfactual changes only committed Z.
            z = saved.inputs.current.Z_4
            from pygrc.models.grc_v4_lifecycle import _fresh_geometry
            changed = replace(saved, inputs=_fresh_geometry(replace(saved.inputs, current=replace(
                saved.inputs.current, Z_4=tuple(0.0 for _ in z)))))
            other = basin.capture(changed, "current")
            changed_equation = oracle.equation_check(changed, "current", other.point)
            separation = max(abs(Fraction(a)-Fraction(b)) for a, b in zip(
                pair[0].point.current.values, other.point.current.values, strict=True))
            error = Fraction(equations["current"]["current_error_upper"]) + Fraction(changed_equation["current_error_upper"])
            self.assertGreater(separation, error)
            # Using the older C fixture coefficient must not pass this oracle.
            original_read = IntervalRows.read
            def wrong_coefficient(high, *args, **kwargs):
                high.params = replace(high.params, zeta_c=Fraction(1, 2**37))
                return original_read(high, *args, **kwargs)
            with patch.object(IntervalRows, "read", wrong_coefficient):
                with self.assertRaisesRegex(AssertionError, "independent current equation"):
                    oracle.equation_check(saved, "current", pair[0].point)
            # H is part of the scientific read even if J is kept byte-identical.
            point = pair[0].point
            bad = copy(point)
            h = [list(r) for r in point.inputs.geometry.one_form_hodge.matrix]
            h[-1][-1] += 2**-8
            geometry = GRCV4Geometry(point.inputs.geometry.reference,
                OneFormHodge(point.inputs.geometry.reference.graph, tuple(map(tuple, h))))
            with self.assertRaisesRegex(ValueError, "old committed history"):
                replace(point.inputs, geometry=geometry)
            forged_inputs = copy(point.inputs)
            object.__setattr__(forged_inputs, "geometry", geometry)
            object.__setattr__(bad, "inputs", forged_inputs)
            self.assertEqual(bad.current, point.current)
            with self.assertRaisesRegex(AssertionError, "independent (current|geometry) equation"):
                oracle.equation_check(saved, "current", bad)
            # A read from another Z state is not attributable to the saved state.
            with patch.object(basin, "_read_once", return_value=(other.read, other.point)):
                with self.assertRaisesRegex(ValueError, "captured role inputs"):
                    model.compute_observables()
        self.assertEqual(model._operation._published.owner.state.to_payload(), before)
        self.assertEqual(model.lifecycle_digest, lifetime)
        EVIDENCE["scientific"] = dict(source_state=before, source_role_equations=equations,
            changed_history_equation=changed_equation, history_discrimination=True,
            committed_carrier_read=True, writer_not_invoked=True, no_A_history=True,
            zeta_C=str(Fraction(1, 2**30)), carrier_current_separation=str(separation),
            combined_current_error_upper=str(error), wrong_C_coefficient_rejected=True,
            unchanged_J_corrupt_H_rejected=True, wrong_carrier_read_rejected=True,
            observation_nonmutating=True)


class CPCTargetCompatibility(shared.AOSTargetCompatibility):
    FAMILY = "C_PC"

    @classmethod
    def setUpClass(cls):
        stack = ExitStack(); cls.addClassCleanup(stack.close)
        stack.enter_context(patch.object(targets, "legacy_config", prior.legacy_config))
        stack.enter_context(patch.object(shared, "EVIDENCE", EVIDENCE))


class CPCRetainedChecks(unittest.TestCase):
    def test_resealed_carrier_certificate_parameter_and_scope_mutations(self):
        import p910_family_basin as campaign
        value = campaign.check("C_PC")
        for kind in ("carrier", "certificate", "geometry", "coefficient", "scope"):
            bad = deepcopy(value)
            case = bad["direct_target"]["observations"][0]
            selected = case["selected_roots"]["current"]
            if kind == "carrier":
                selected["recipe"]["inputs"]["current"]["Z_4"][0] += 0.01
            elif kind == "certificate":
                selected["certificate"] = {}
            elif kind == "geometry":
                selected["H1_form"][-1][-1] = (2.).hex()
            elif kind == "coefficient":
                selected["recipe"]["inputs"]["reference"]["profile"]["params_resolved"]["candidate"]["zeta_C"] = 2**-37
            else:
                case["role_equations"]["current"]["exact_root_signs_claimed"] = True
            bad["direct_target"] = campaign.seal(bad["direct_target"])
            with self.subTest(kind=kind), self.assertRaises((ValueError, AssertionError)):
                campaign.validate(campaign.seal(bad), sources=False)


if __name__ == "__main__":
    unittest.main()

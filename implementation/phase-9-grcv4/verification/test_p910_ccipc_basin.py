"""Composite C basin: full joint root, old carrier, exact target lifecycle."""
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
from tests.models import test_grc_9_v4_ccipc_integration as prior
import p9101a_basin_oracle as oracle
import p9101c_target_basin as direct
import test_p9101b_target_compatibility as targets
import test_p910_aos_basin as shared

EVIDENCE = {}


def source_configuration(family):
    if family != "C_CI_PC":
        raise ValueError("C_CI_PC fixture provider")
    return dict(initial=targets.target_seed(family)["initial"],
                exact_backend="flint", numerical_policy="legacy_exact_v1")


class CCIPCNativeBasin(native.NativeBasinTests):
    FAMILY = "C_CI_PC"

    @classmethod
    def setUpClass(cls):
        stack = ExitStack(); cls.addClassCleanup(stack.close)
        stack.enter_context(patch.object(native, "configuration", source_configuration))
        stack.enter_context(patch.object(native, "seed", targets.target_seed))
        stack.enter_context(patch.object(public, "native_config", prior.legacy_config))
        super().setUpClass()

    def test_composite_full_root_and_independent_equations(self):
        import pygrc.models.grc_v4_ci as ci
        from pygrc.models.grc_v4_lifecycle import _fresh_geometry
        from test_p980_os_effect_witness import IntervalRows
        model = self.model()
        saved = model._operation._published.owner.state
        before, lifetime = deepcopy(saved.to_payload()), model.lifecycle_digest
        equations, roots = {}, {}
        with exact_backend(ExactBackend.FLINT), patch.object(ci.ProvisionalCandidateCIStep, "__post_init__",
                side_effect=AssertionError("diagnostic invoked writer")):
            pair = basin.capture_pair(saved)
            for role, captured in zip(("current", "reset"), pair, strict=True):
                read, point = captured.read, captured.point
                self.assertIs(read.selected.point, point)
                self.assertEqual(read.selected.inputs, point.inputs)
                self.assertEqual(point.inputs.trial_current, point.current)
                self.assertEqual(point.inputs.stage, "cipc_trial")
                self.assertIsNone(point.inputs.current.W_A)
                self.assertEqual(point.inputs.current.Z_4, getattr(saved.inputs, role).Z_4)
                self.assertTrue(any(point.inputs.current.Z_4))
                oracle.captured_inputs(saved, role, captured.observation.to_dict(), read, point)
                equations[role] = oracle.equation_check(saved, role, point)
                payload, certificate = oracle.root_payload(read, point)
                roots[role] = dict(digest=oracle.digest(payload), certificate=certificate,
                    evaluations=read.evaluations, residual_squared=str(read.selected.residual_squared))
                fresh = ci.CandidateCIRoot(read.inputs)
                self.assertEqual(oracle.root_payload(fresh, fresh.selected.point), (payload, certificate))
                self.assertLessEqual(Fraction(str(read.selected.residual_squared)),
                    Fraction(saved.inputs.geometry.reference.profile.params_resolved.realization.tolerance)**2)
            self.assertNotEqual(saved.inputs.current.Z_4, saved.inputs.reset.Z_4)
            z = saved.inputs.current.Z_4
            changed = replace(saved, inputs=_fresh_geometry(replace(saved.inputs, current=replace(
                saved.inputs.current, Z_4=tuple(0.0 for _ in z)))))
            other = basin.capture(changed, "current")
            changed_equation = oracle.equation_check(changed, "current", other.point)
            separation = max(abs(Fraction(a)-Fraction(b)) for a, b in zip(
                pair[0].point.current.values, other.point.current.values, strict=True))
            error = Fraction(equations["current"]["current_error_upper"]) + Fraction(changed_equation["current_error_upper"])
            self.assertGreater(separation, error)
            # Omission controls are evaluated independently at the selected H.
            # Their relation to the solver tolerance is retained, not inferred.
            for eq in equations.values():
                self.assertGreater(Fraction(eq["carrier_omission_residual_lower"]),
                                   Fraction(eq["geometry_residual_upper"]))
                self.assertGreater(Fraction(eq["instantaneous_omission_residual_lower"]),
                                   Fraction(eq["geometry_residual_upper"]))
            original_read = IntervalRows.read
            def wrong_coefficient(high, *args, **kwargs):
                high.params = replace(high.params, zeta_c=Fraction(1, 2**37))
                return original_read(high, *args, **kwargs)
            with patch.object(IntervalRows, "read", wrong_coefficient):
                with self.assertRaisesRegex(AssertionError, "independent current equation"):
                    oracle.equation_check(saved, "current", pair[0].point)
            # An unchanged J is insufficient: corrupt only the selected H.
            read, point = pair[0].read, pair[0].point
            bad = copy(point); h = [list(r) for r in point.inputs.geometry.one_form_hodge.matrix]
            h[-1][-1] += 2**-8
            bad_inputs = copy(point.inputs)
            object.__setattr__(bad_inputs, "geometry", GRCV4Geometry(point.inputs.geometry.reference,
                OneFormHodge(point.inputs.geometry.reference.graph, tuple(map(tuple, h)))))
            object.__setattr__(bad, "inputs", bad_inputs)
            self.assertEqual(bad.current, point.current)
            with self.assertRaisesRegex(AssertionError, "independent (current|geometry) equation"):
                oracle.equation_check(saved, "current", bad)
            with patch.object(basin, "_read_once", return_value=(read, bad)):
                with self.assertRaisesRegex(ValueError, "joint CI root"):
                    model.compute_observables()
            with patch.object(basin, "_read_once", return_value=(other.read, other.point)):
                with self.assertRaisesRegex(ValueError, "captured role inputs"):
                    model.compute_observables()
        self.assertEqual(model._operation._published.owner.state.to_payload(), before)
        self.assertEqual(model.lifecycle_digest, lifetime)
        EVIDENCE["scientific"] = dict(source_state=before, source_role_equations=equations,
            full_root_reconstruction=roots, fresh_full_root_equality=True,
            changed_history_equation=changed_equation, history_discrimination=True,
            writer_not_invoked=True, no_A_history=True, old_Z_held_during_root=True,
            zeta_C=str(Fraction(1, 2**30)), carrier_selected_current_separation=str(separation),
            combined_fixed_geometry_current_error_upper=str(error),
            joint_solver_tolerance=str(Fraction(saved.inputs.geometry.reference.profile.params_resolved.realization.tolerance)),
            exact_root_effect_claimed=False, wrong_C_coefficient_rejected=True,
            unchanged_J_corrupt_H_rejected=True, wrong_carrier_read_rejected=True,
            observation_nonmutating=True)


class CCIPCTargetCompatibility(shared.AOSTargetCompatibility):
    FAMILY = "C_CI_PC"

    @classmethod
    def setUpClass(cls):
        stack = ExitStack(); cls.addClassCleanup(stack.close)
        stack.enter_context(patch.object(targets, "legacy_config", prior.legacy_config))
        stack.enter_context(patch.object(shared, "EVIDENCE", EVIDENCE))


class CCIPCRetainedChecks(unittest.TestCase):
    def test_resealed_root_carrier_domain_and_scope_mutations(self):
        import p910_family_basin as campaign
        value = campaign.check("C_CI_PC")
        for kind in ("carrier", "certificate", "geometry", "domain", "scope"):
            bad = deepcopy(value)
            case = bad["direct_target"]["observations"][0]
            selected = case["selected_roots"]["current"]
            if kind == "carrier":
                selected["recipe"]["inputs"]["current"]["Z_4"][0] += 0.01
            elif kind == "certificate":
                selected["certificate"] = {}
            elif kind == "geometry":
                selected["selected_inputs"]["H1_form"][-1][-1] = 2.
            elif kind == "domain":
                selected["recipe"]["inputs"]["reference"]["profile"]["params_resolved"]["realization"]["contraction_domain_id"] = "unbound"
            else:
                case["role_equations"]["current"]["exact_root_signs_claimed"] = True
            bad["direct_target"] = campaign.seal(bad["direct_target"])
            with self.subTest(kind=kind), self.assertRaises((ValueError, AssertionError)):
                campaign.validate(campaign.seal(bad), sources=False)


if __name__ == "__main__":
    unittest.main()

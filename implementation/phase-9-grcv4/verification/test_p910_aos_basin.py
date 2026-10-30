"""A_OS basin integration using the accepted lifecycle and independent oracles."""

from contextlib import ExitStack
from copy import copy, deepcopy
from dataclasses import replace
from fractions import Fraction
import unittest
from unittest.mock import patch

from pygrc.models import GRC9V4
from pygrc.models import grc_9_v4_basin as basin
from pygrc.models.grc_v4_exact import ExactBackend, exact_backend
from pygrc.models.grc_v4_geometry import GRCV4Geometry, OneFormHodge
from tests.models import test_grc_9_v4 as public
from tests.models import test_grc_9_v4_basin as native
from tests.models import test_grc_9_v4_aos_integration as prior
import p9101a_basin_oracle as oracle
import p9101c_target_basin as direct
import p9102_verification as verification
import test_p9101b_target_compatibility as targets

EVIDENCE = {}


def source_configuration(family):
    if family != "A_OS":
        raise ValueError("this fixture provider selects A_OS")
    return dict(initial=targets.target_seed(family)["initial"],
                exact_backend="flint", numerical_policy="legacy_exact_v1")


class AOSNativeBasin(native.NativeBasinTests):
    FAMILY = "A_OS"

    @classmethod
    def setUpClass(cls):
        # Adapt only the independent fixture/configuration providers. Every
        # producer, lifecycle operation, replay and inherited assertion is real.
        stack = ExitStack()
        cls.addClassCleanup(stack.close)
        stack.enter_context(patch.object(native, "configuration", source_configuration))
        stack.enter_context(patch.object(native, "seed", targets.target_seed))
        stack.enter_context(patch.object(public, "native_config", prior.legacy_config))
        super().setUpClass()

    def test_a_history_reference_restart_and_independent_equations(self):
        model = self.model()
        saved = model._operation._published.owner.state
        before = deepcopy(saved.to_payload())
        lifetime = model.lifecycle_digest
        with exact_backend(ExactBackend.FLINT):
            pair = basin.capture_pair(saved)
            equations = {}
            for role, captured in zip(("current", "reset"), pair, strict=True):
                point = captured.point
                self.assertIs(captured.read, point)
                self.assertEqual(point.inputs.geometry, saved.inputs.geometry.reference.geometry())
                self.assertEqual(point.inputs.current, getattr(saved.inputs, role))
                self.assertIsNone(point.inputs.current.Z_4)
                oracle.captured_inputs(saved, role, captured.observation.to_dict(), point, point)
                equations[role] = oracle.equation_check(saved, role, point)
                self.assertIn("differential_reference", point.to_payload())
                self.assertIsNone(captured.observation["binding"]["root_certificate_binding"])
            # Change only source W. Do not fit a new partition or use a step's
            # consumed current. The admitted independent equation must move too.
            weights = saved.inputs.current.W_A
            changed = replace(saved, inputs=replace(saved.inputs, current=replace(
                saved.inputs.current, W_A=(weights[0] * 9 / 8, *weights[1:]))))
            other = basin.capture(changed, "current")
            self.assertNotEqual(other.point.current, pair[0].point.current)
            changed_equation = oracle.equation_check(changed, "current", other.point)
            self.assertNotEqual(other.observation["binding"]["read_identity"],
                                pair[0].observation["binding"]["read_identity"])
            # Ordinary OS evolution is not the diagnostic's stage. Its
            # corrector is a plausible wrong current, not a fresh restart.
            from pygrc.models.grc_v4_realizations import CandidateAOSPass
            point = pair[0].point
            wrong = CandidateAOSPass(replace(point.inputs, dt=2**-12),
                                    point.differential_reference).corrector
            self.assertNotEqual(wrong.current, point.current)
            with patch.object(basin, "_read_once", return_value=(wrong, wrong)):
                with self.assertRaisesRegex(ValueError, "captured role inputs"):
                    model.compute_observables()
            # Keep J exactly; corrupt H alone. Neither the full native binding
            # nor the independent reference-geometry equation may accept it.
            bad = copy(point)
            h = [list(r) for r in point.inputs.geometry.one_form_hodge.matrix]
            h[-1][-1] += 2**-8
            bad_inputs = replace(point.inputs, geometry=GRCV4Geometry(
                point.inputs.geometry.reference,
                OneFormHodge(point.inputs.geometry.reference.graph, tuple(map(tuple, h)))))
            object.__setattr__(bad, "inputs", bad_inputs)
            self.assertEqual(bad.current, point.current)
            with patch.object(basin, "_read_once", return_value=(bad, bad)):
                with self.assertRaisesRegex(ValueError, "captured role inputs"):
                    model.compute_observables()
            with self.assertRaisesRegex(AssertionError, "independent (current|geometry) equation"):
                oracle.equation_check(saved, "current", bad)
        self.assertEqual(model._operation._published.owner.state.to_payload(), before)
        self.assertEqual(model.lifecycle_digest, lifetime)
        EVIDENCE["scientific"] = dict(
            source_state=before, source_role_equations=equations,
            changed_history_equation=changed_equation,
            fresh_reference_geometry=True, fixed_row_A_backend=True,
            history_discrimination=True, OS_corrector_substitution_rejected=True,
            unchanged_J_corrupt_H_rejected=True, observation_nonmutating=True)


class AOSTargetCompatibility(targets.TargetCompatibility):
    FAMILY = "A_OS"

    @classmethod
    def setUpClass(cls):
        stack = ExitStack()
        cls.addClassCleanup(stack.close)
        stack.enter_context(patch.object(targets, "legacy_config", prior.legacy_config))

    def model(self):
        old = targets.target(self.FAMILY)
        model = GRC9V4.from_config(dict(initial=old, exact_backend="flint",
                                       numerical_policy="legacy_exact_v1"))
        self.assertEqual(model._operation._published.owner.state.to_payload(), old)
        self.assertEqual(model.active_model_identity, old["model_identity"])
        self.assertEqual((len(model.configuration.current.C),
                          len(model.configuration.reference.graph.live_edge_ids)), (17, 16))
        return model

    def roundtrip(self, enabled_basin):
        if not enabled_basin:
            return super().roundtrip(False)
        cases = []
        migrate = GRC9V4.migrate_basin_policy
        branch = GRC9V4.migrate_branch

        def policy(model, *args, **kwargs):
            result = migrate(model, *args, **kwargs)
            if result.committed:
                cases.append(direct.capture(model, direct.LABELS[0]))
            return result

        def crossing(model, request):
            result = branch(model, request)
            if result.committed and request.to_payload()["direction"] == "enable":
                cases.append(direct.capture(model, direct.LABELS[1]))
            return result

        # Capture the exact two required boundaries during the compatibility
        # execution itself. No second reconstruction/crossing campaign for 10.1c.
        with patch.object(GRC9V4, "migrate_basin_policy", policy), \
             patch.object(GRC9V4, "migrate_branch", crossing):
            super().roundtrip(True)
        self.assertEqual([c["label"] for c in cases], list(direct.LABELS))
        EVIDENCE["exact_target"] = dict(observations=cases)


class AOSRetainedChecks(unittest.TestCase):
    def test_resealed_boundary_history_geometry_and_receipt_mutations(self):
        import p910_family_basin as campaign
        value = campaign.check("A_OS")
        for kind in ("subject", "boundary", "history", "geometry", "rows", "scope"):
            bad = deepcopy(value)
            case = bad["direct_target"]["observations"][1]
            if kind == "subject":
                bad["direct_target"]["subject"]["model_identity"] = "unrelated"
            elif kind == "boundary":
                bad["direct_target"]["observations"][1] = deepcopy(bad["direct_target"]["observations"][0])
                bad["direct_target"]["observations"][1]["label"] = direct.LABELS[1]
            elif kind == "history":
                case["selected_roots"]["current"]["recipe"]["inputs"]["current"]["W_A"][0] *= 2
            elif kind == "geometry":
                case["selected_roots"]["current"]["H1_form"][-1][-1] = (2.).hex()
            elif kind == "rows":
                case["observations"]["current_observation"]["witness"]["rows"][0]["gradient"][0] = (7.).hex()
            else:
                case["role_equations"]["current"]["exact_root_signs_claimed"] = True
            bad["direct_target"] = direct.predecessor.seal(bad["direct_target"])
            with self.subTest(kind=kind), self.assertRaises((ValueError, AssertionError)):
                campaign.validate(verification.seal(bad), equations=False, sources=False)
        old = value["target_compatibility"]["v2"]
        owner = deepcopy(old["final_checkpoint"]["owner"])
        owner["receipts"][-1]["identity_payload"]["core"]["parent_receipt_ids"] = []
        with self.assertRaises(ValueError):
            verification.ledger_check(owner, old["enabled_continuation"])


if __name__ == "__main__":
    unittest.main()

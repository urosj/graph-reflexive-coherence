from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "src"))

from artifact_io import assert_payload_digest  # noqa: E402
from grv5_methods import (  # noqa: E402
    activity_amplitude_from_target,
    activity_write_stage,
    coherence_vector,
    conductance_vector,
    difference_in_differences,
    direct_conductance_intervention,
    match_C_and_J_preserving_W,
    old_current_intervention,
)
from pygrc.models import GRC9V3  # noqa: E402


class GRV5PreparationPersistenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = json.loads(
            (ROOT / "configs/grv5_preparation_persistence.json").read_text(
                encoding="utf-8"
            )
        )
        registry = json.loads(
            (ROOT / "outputs/fixed_branch_registry.json").read_text(encoding="utf-8")
        )["payload"]
        cls.branch = registry["branches"][0]
        cls.model = GRC9V3.load(str(REPO_ROOT / cls.branch["state_snapshot_path"]))

    def test_method_is_all_branch_and_claim_bounded(self) -> None:
        self.assertEqual(48, self.config["source_scope"]["expected_branch_count"])
        self.assertEqual(
            "all_certified_branches_no_post_outcome_selection",
            self.config["source_scope"]["branch_selection"],
        )
        self.assertFalse(
            self.config["present_current_convention"][
                "native_external_present_current_input_available"
            ]
        )
        self.assertFalse(
            self.config["claim_boundary"]["native_readback_supported"]
        )
        self.assertFalse(
            self.config["claim_boundary"]["frozen_W_result_can_upgrade_native"]
        )

    def test_direct_conductance_intervention_is_clone_first(self) -> None:
        before_c = coherence_vector(self.model).copy()
        before_w = conductance_vector(self.model).copy()
        changed = direct_conductance_intervention(
            self.model,
            signed_relative_amplitude=self.config["preparation"][
                "direct_conductance_relative_amplitude"
            ],
        )
        self.assertTrue(np.array_equal(before_c, coherence_vector(changed)))
        self.assertFalse(np.array_equal(before_w, conductance_vector(changed)))
        self.assertTrue(np.array_equal(before_w, conductance_vector(self.model)))

    def test_activity_write_is_stage_local_sign_even_and_not_complete_step_retained(self) -> None:
        amplitude = activity_amplitude_from_target(
            self.model,
            self.config["preparation"][
                "activity_write_target_log_conductance_exponent"
            ],
        )
        positive = activity_write_stage(self.model, amplitude=amplitude)
        negative = activity_write_stage(self.model, amplitude=-amplitude)
        zero = activity_write_stage(self.model, amplitude=0.0)
        self.assertTrue(
            np.allclose(
                conductance_vector(positive),
                conductance_vector(negative),
                atol=1e-14,
                rtol=0.0,
            )
        )
        self.assertGreater(
            np.linalg.norm(conductance_vector(positive) - conductance_vector(zero)),
            1e-6,
        )
        full_positive = old_current_intervention(self.model, amplitude=amplitude)
        full_zero = old_current_intervention(self.model, amplitude=0.0)
        full_positive.step()
        full_zero.step()
        self.assertTrue(
            np.allclose(
                conductance_vector(full_positive),
                conductance_vector(full_zero),
                atol=1e-10,
                rtol=0.0,
            )
        )

    def test_matched_pair_preserves_W_but_native_stage_reconstructs_it(self) -> None:
        amplitude = self.config["preparation"]["direct_conductance_relative_amplitude"]
        first = direct_conductance_intervention(
            self.model, signed_relative_amplitude=amplitude
        )
        second = direct_conductance_intervention(
            self.model, signed_relative_amplitude=-amplitude
        )
        first, second = match_C_and_J_preserving_W(first, second)
        self.assertTrue(np.array_equal(coherence_vector(first), coherence_vector(second)))
        self.assertFalse(np.array_equal(conductance_vector(first), conductance_vector(second)))
        native = difference_in_differences(
            first,
            second,
            lane="native_immediate_transport_stage_probe",
            probe_kind="coherence_or_potential_probe",
            amplitude=0.002,
        )
        reduced = difference_in_differences(
            first,
            second,
            lane="frozen_W_probe",
            probe_kind="coherence_or_potential_probe",
            amplitude=0.002,
        )
        self.assertLessEqual(native["difference_in_differences_l2"], 1e-10)
        self.assertGreater(reduced["difference_in_differences_l2"], 1e-10)
        self.assertEqual("substrate_reduced", reduced["substrate_class"])

    def test_review_artifact_remains_bounded_when_present(self) -> None:
        path = ROOT / "outputs/conductance_retention_probe.json"
        if not path.exists():
            self.skipTest("GRV5 has not executed from its clean P5 revision")
        envelope = json.loads(path.read_text(encoding="utf-8"))
        assert_payload_digest(envelope)
        payload = envelope["payload"]
        self.assertFalse(payload["summary"]["native_readback_supported"])
        self.assertFalse(payload["summary"]["closed_loop_supported"])
        self.assertTrue(
            payload["claim_boundary"]["frozen_W_sensitivity_does_not_upgrade_native"]
        )


if __name__ == "__main__":
    unittest.main()

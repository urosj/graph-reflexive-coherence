"""Native CI numerical bridge and the shared atomic lifecycle, bounded only."""

import sys
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

from flint import arb_mat, ctx, fmpq

from pygrc.models import grc_9_v4_spark_owner as owner
from pygrc.models.grc_9_v4 import GRC9V4
from pygrc.models.grc_v4_certification import (
    _ARB_CONTEXT_LOCK,
    CertificationInconclusive,
)
from pygrc.models.grc_v4_spark_cci import SparkCCIKernel
from pygrc.models.grc_v4_spark_cos import SparkCOSKernel
from pygrc.models.grc_v4_spark_state import ExactResources
from tests.models import test_grc_9_v4_spark_completion as shared

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "implementation/phase-9-grcv4/verification"))
from cci_native_spark_oracle import CCIReference, verify_step
from p991a6_cci_subjects import configuration, profile


class NativeCCITests(shared.NativeSparkCompletionTests):
    @classmethod
    def setUpClass(cls):
        cls.config = configuration()
        cls.source_model = GRC9V4(cls.config)
        assert cls.source_model.step().committed
        cls.event_model = cls.source_model.duplicate()
        assert cls.event_model.expand(shared.request(cls.event_model)).committed
        cls.certificates, cls.center = shared.certificate_pair(cls.event_model)

    def test_independent_full_jacobian_at_exact_center(self):
        with _ARB_CONTEXT_LOCK, ctx.workprec(256):
            k = owner.kernel(self.event_model.configuration)
            C = arb_mat([[fmpq(x)] for x in self.center.C])
            _, actual, _, _ = k.analytic(C)
        with _ARB_CONTEXT_LOCK, ctx.workprec(768):
            m = CCIReference(self.center.graph.to_payload())
            expected, _ = m.full_jacobian(C)
            self.assertTrue(
                all(
                    a.contains(b)
                    for a, b in zip(actual.entries(), expected.entries(), strict=True)
                )
            )
            # A frozen-geometry derivative cannot replace the implicit one.
            root = m.root(C)
            _, _, _, _, JC = m.partials(C, root["flat"])
            n = len(self.center.C)
            frozen = (
                arb_mat([[int(i == j) for j in range(n)] for i in range(n)])
                - 32 * m.B * JC
            )
            self.assertTrue(
                any(
                    not a.overlaps(b)
                    for a, b in zip(expected.entries(), frozen.entries(), strict=True)
                )
            )

    def test_independent_joint_roots_before_and_after_both_roles_chiralities(self):
        for chirality in (1, -1):
            model = self.source_model.duplicate()
            self.assertTrue(model.expand(shared.request(model, chirality)).committed)
            k = owner.kernel(model.configuration)
            for role in ("current", "reset"):
                state = getattr(model.configuration, role)
                step = k.step(state)
                self.assertTrue(verify_step(step)["full_step_bound"])
                self.assertNotEqual(step.root, step.restart_root)
        verify_step(owner.kernel(self.config).step(self.config.current))

    def test_no_os_stages_and_fail_closed_joint_root(self):
        k = owner.kernel(self.config)
        with patch.object(
            SparkCOSKernel, "step", side_effect=AssertionError("OS step used")
        ):
            k.step(self.config.current)
        short = SparkCCIKernel(
            k.graph,
            profile(
                k.graph,
                realization={"iteration_limit": 1},
                solver={"iteration_limit": 1},
            ),
        )
        with self.assertRaises(CertificationInconclusive):
            short.step(self.config.current)
        values = list(self.config.current.C)
        values = ["21"] + ["0"] * (len(values) - 1)
        with self.assertRaises(CertificationInconclusive):
            k.step(ExactResources(k.graph, tuple(values), "21"))
        tight = SparkCCIKernel(
            k.graph, profile(k.graph, solver={"conditioning_limit": 1})
        )
        with self.assertRaises(CertificationInconclusive):
            tight.readmission(self.config.current)

    def test_policy_and_family_cannot_cross(self):
        migrated = GRC9V4(self.config)
        self.assertTrue(
            migrated.migrate_spark_configuration(shared.configuration()).committed
        )
        self.assertEqual(
            migrated.numerical_policy, shared.configuration().reference.profile.NUMERICS
        )
        self.assertTrue(migrated.migrate_spark_configuration(self.config).committed)
        self.assertEqual(
            migrated.numerical_policy, self.config.reference.profile.NUMERICS
        )
        self.assertEqual(
            self.source_model.support_status()["execution_families"], ["C_CI"]
        )
        self.assertFalse(self.source_model.support_status()["current_occurrence_completed"])
        self.assertFalse(self.source_model.support_status()["universal_entry_guarantee"])
        with self.assertRaises(ValueError):
            replace(self.config, specialization=shared.configuration().specialization)
        with self.assertRaises(ValueError):
            SparkCCIKernel(
                self.config.reference.graph,
                profile(
                    self.config.reference.graph, solver={"absolute_tolerance": 1e-8}
                ),
            )
        cos = GRC9V4(shared.configuration())
        cos.step()
        cos.expand(shared.request(cos))
        cos_pair, _ = shared.certificate_pair(cos)
        self.assertFalse(
            self.event_model.install_completion_certificates(*cos_pair).committed
        )

    def test_root_domain_cache_is_graph_bound_and_never_a_root_cache(self):
        k = owner.kernel(self.config)
        initial = k.root_cache_info()
        same = owner.kernel(self.config)
        self.assertGreater(same.root_cache_info()["hits"], initial["hits"])
        target = owner.kernel(self.event_model.configuration)
        self.assertNotEqual(k.root_domain, target.root_domain)
        with patch.object(
            SparkCCIKernel, "_root", autospec=True, side_effect=SparkCCIKernel._root
        ) as spy:
            k.step(self.config.current)
            self.assertEqual(spy.call_count, 2)

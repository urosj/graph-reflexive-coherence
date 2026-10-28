"""All-ten public contract fit, without enabling six unselected native owners."""

from copy import deepcopy
from dataclasses import replace
import unittest
from unittest.mock import patch

from examples.grcv4.catalog import Catalog
from examples.grcv4.run_selection import configuration_from_selection
from pygrc.models.grc_9_v4 import (
    GRC9V4,
    GRC9V4Configuration,
    GRC9V4ExecutionOptions,
    GRC9V4ExecutionUnavailable,
    describe_families,
    describe_family,
)
from pygrc.models.grc_v4_codec import canonical_json_bytes
from pygrc.models.grc_v4_state import GRCV4AuthoritativeState
from tests.models.test_grc_9_v4 import migration_request

EVIDENCE = {}


class PublicContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        catalog = Catalog()
        cls.configs = {
            f.profile_family_id: configuration_from_selection(
                catalog.selection("native-small-" + f.profile_family_id, "source"),
                exact_backend="flint",
                numerical_policy="legacy_exact_v1",
            )
            for f in describe_families()
        }

    def test_ten_complete_typed_configurations_roundtrip(self):
        import hashlib

        rows = []
        self.assertEqual(
            set(self.configs),
            {c + "_" + r for c in "AC" for r in ("OS", "CI", "PC", "CI_PC", "RG2b")},
        )
        for name, cfg in self.configs.items():
            with self.subTest(family=name):
                family = cfg.family
                self.assertIs(
                    type(cfg.profile.params_resolved.candidate),
                    family.candidate_parameters,
                )
                self.assertIs(
                    type(cfg.profile.params_resolved.realization),
                    family.realization_parameters,
                )
                raw = cfg.to_payload()
                self.assertEqual(
                    raw, GRC9V4Configuration.from_payload(raw).to_payload()
                )
                raw["current"]["C"][0] = -1
                self.assertGreaterEqual(cfg.current.C[0], 0)
                with self.assertRaises(ValueError):
                    GRC9V4Configuration.from_payload(raw)
                rows.append(
                    dict(
                        **family.to_payload(),
                        configuration_digest=hashlib.sha256(
                            canonical_json_bytes(cfg.to_payload())
                        ).hexdigest(),
                        roundtrip=True,
                    )
                )
        EVIDENCE["families"] = rows

    def test_candidate_and_carrier_axes_are_independent(self):
        for name, cfg in self.configs.items():
            e = len(cfg.reference.graph.oriented_edges)
            with self.subTest(family=name):
                wrong_w = None if name.startswith("A_") else (1.0,) * e
                wrong_z = None if cfg.family.persistent else (0.0,) * (e * e)
                for role in ("current", "reset"):
                    state = getattr(cfg, role)
                    with self.assertRaises(ValueError):
                        replace(cfg, **{role: replace(state, W_A=wrong_w)})
                    with self.assertRaises(ValueError):
                        replace(cfg, **{role: replace(state, Z_4=wrong_z)})
                    with self.assertRaises(ValueError):
                        replace(cfg, **{role: replace(state, C=state.C[:-1])})
                if cfg.family.persistent:
                    with self.assertRaises(ValueError):
                        replace(
                            cfg, current=replace(cfg.current, Z_4=cfg.current.Z_4[:-1])
                        )
                self.assertEqual(
                    cfg.family.authoritative_fields,
                    ("C",)
                    + (("W_A",) if name.startswith("A_") else ())
                    + (("Z_4",) if cfg.family.persistent else ()),
                )

    def test_realization_parameters_do_not_collapse_to_common_solver_knobs(self):
        for candidate in "AC":
            configs = [
                self.configs[candidate + "_" + r]
                for r in ("OS", "CI", "PC", "CI_PC", "RG2b")
            ]
            self.assertEqual(
                len({type(c.profile.params_resolved.realization) for c in configs}), 5
            )
            self.assertEqual(len({c.family.solve_kind for c in configs}), 5)
            for cfg in configs:
                bad = deepcopy(cfg.to_payload())
                bad["reference"]["profile"]["params_resolved"]["realization"][
                    "invented_common_knob"
                ] = 1
                with self.assertRaises(ValueError):
                    GRC9V4Configuration.from_payload(bad)
            self.assertEqual(
                configs[1].family.solve_kind, "joint_current_geometry_root"
            )
            self.assertFalse(configs[1].family.persistent)
            self.assertTrue(configs[3].family.persistent)
            self.assertFalse(configs[4].family.persistent)

    def test_known_unavailable_families_reject_before_execution(self):
        from pygrc.models.grc_9_v4_owner import GRC9V4EnabledOperation

        self.assertEqual(
            set(GRC9V4.execution_scope()), {"C_OS", "C_CI", "A_CI", "A_PC", "A_OS"}
        )
        unavailable = []
        with patch.object(
            GRC9V4EnabledOperation,
            "__init__",
            side_effect=AssertionError("unselected numerical admission"),
        ):
            for name, cfg in self.configs.items():
                if name in GRC9V4.execution_scope():
                    continue
                with (
                    self.subTest(family=name),
                    self.assertRaises(GRC9V4ExecutionUnavailable) as caught,
                ):
                    GRC9V4.from_config(cfg)
                self.assertEqual(caught.exception.family.profile_family_id, name)
                unavailable.append(name)
        with self.assertRaises(ValueError) as caught:
            describe_family("A_UNKNOWN")
        self.assertNotIsInstance(caught.exception, GRC9V4ExecutionUnavailable)
        EVIDENCE["execution_scope"] = dict(
            available=list(GRC9V4.execution_scope()),
            known_unavailable=unavailable,
            no_unselected_execution=True,
        )

    def test_known_target_declaration_is_not_runtime_support(self):
        source = self.configs["C_OS"]
        target = self.configs["C_PC"].reference
        m = GRC9V4.from_config(replace(source, targets=(target,)))
        tid = target.profile.complete_profile_id
        self.assertIn(tid, {p.complete_profile_id for p in m.list_declared_profiles()})
        self.assertNotIn(tid, m.list_supported_profiles())
        snapshot = m.snapshot()
        self.assertEqual(GRC9V4.from_state(snapshot).snapshot(), snapshot)
        request = migration_request(m, target)
        with self.assertRaises(GRC9V4ExecutionUnavailable):
            m.migrate_profile(request)
        self.assertEqual(m.snapshot(), snapshot)
        self.assertEqual(len(m.support_status()["declared_families"]), 10)
        self.assertEqual(len(m.support_status()["execution_families"]), 5)

    def test_contract_wire_and_execution_options_are_closed(self):
        cfg = self.configs["C_OS"]
        for key in ("current", "reset", "execution", "specialization"):
            bad = deepcopy(cfg.to_payload())
            bad[key]["unknown"] = 1
            with self.assertRaises(ValueError):
                GRC9V4Configuration.from_payload(bad)
        for clock in (True, -1, 2**53):
            with self.assertRaises(ValueError):
                replace(cfg, step_index=clock)
        with self.assertRaises(ValueError):
            replace(cfg, time=float("nan"))
        with self.assertRaises(ValueError):
            GRC9V4ExecutionOptions("auto", "legacy_exact_v1")
        with self.assertRaises(ValueError):
            GRC9V4ExecutionOptions("flint", "fallback")
        with self.assertRaises(TypeError):
            replace(cfg, current={"C": []})
        with self.assertRaises(ValueError):
            replace(cfg, current=GRCV4AuthoritativeState((1,), None, None))
        with self.assertRaises(ValueError):
            GRC9V4.from_config({"schema_version": "grc9v4-configuration-v1"})


if __name__ == "__main__":
    unittest.main()

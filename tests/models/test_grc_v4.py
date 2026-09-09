"""V4 record contracts, lifecycle integration and mapped-vector correction audits."""

from __future__ import annotations

from collections.abc import Callable
import ast
from copy import copy, deepcopy
from dataclasses import FrozenInstanceError, fields, is_dataclass, replace
from decimal import Decimal, localcontext
import json
from hashlib import sha256
from importlib.util import resolve_name
import math
from pathlib import Path
import pickle
import random
import struct
from typing import Any
import unittest
from unittest.mock import patch

from pygrc.models import grc_v4 as api
from pygrc.models import grc_v4_step as admission
from pygrc.models.grc_v4_codec import (
    V4DecodeShapeError, V4SchemaError, V4WireError, canonical_json_bytes,
    decode_record_payload,
)
from pygrc.models.grc_v4_profile import list_supported_profiles
from pygrc.models.grc_v4_state import FrozenJSONMap

STEP_RECORDS: tuple[type[api._StepRequestRecord], ...] = (
    api.GRCV4StepRequestInput, api.GRCV4StepRequest,
)

def step_input(dt: Any = 0.25) -> dict[str, Any]:
    return {"schema_version": "grcv4-step-request-input-v1", "operation_id": "step:1",
            "dt": dt, "context_value": {"x": [True, {"n": 1}]},
            "boundary_input": None, "external_source": None}


def migration() -> dict[str, Any]:
    def channel(subject: str) -> dict[str, Any]:
        return {"schema_version": "grcv4-history-channel-policy-v1", "subject": subject,
                "policy_id": "test_absent_history_v1", "disposition": "not_applicable",
                "source_history_digest": None, "target_initializer_id": None,
                "information_loss": "none"}
    return {"schema_version": "grcv4-migration-request-v1", "operation_id": "migration:1",
            "source_state_digest": "grcv4-state-sha256:" + "0" * 64,
            "target_profile_id": "grcv4-profile-sha256:" + "1" * 64,
            "migration_policy": {"schema_version": "grcv4-migration-policy-v1",
                                 "policy_id": "typed_bidirectional_profile_migration_v1",
                                 "resource_policy_id": "identity_resource_transport_v1",
                                 "target_readmission_policy_id": "full_target_fail_closed_v1"},
            "history_policy": {"schema_version": "grcv4-history-bundle-policy-v1",
                               "candidate": channel("candidate"), "carrier": channel("carrier")},
            "target_context_value": {"x": [True, {"n": 1}]}}


class FoundationIntegrationTests(unittest.TestCase):
    """P9-2.6 record integration, not an executable model acceptance test.

    Stage-local registry/import assertions must be replaced by exact supported
    profile/facade checks when those consumers are authorized (P9-4.4/4.5/4.7a).
    """

    def test_no_ambient_support_after_templates_prefix_controls_and_inspection(self) -> None:
        from pygrc.models import grc_v4_profile as profiles
        from pygrc.models.grc_v4_codec import load_contract_schema
        from pygrc.models.grc_v4_state import GRCV4StepResult
        from tests.models import grcv4_conformance_harness as harness
        from tests.models.grcv4_reference_oracles import prefix_fixture
        from tests.models.test_grc_v4_profile import bundle
        from tests.models.test_grc_v4_state import result_fixture

        self.assertEqual(profiles.list_supported_profiles(), frozenset())
        for row in bundle()["identity_vectors"]:
            if row["schema_ref"] == "#/$defs/profile_template_payload":
                template = profiles.GRCV4ProfileTemplate.from_payload(row["payload"])
                self.assertEqual(template.profile_template_id, row["expected_identifier"])
                with self.assertRaisesRegex(ValueError, "unsupported executable"):
                    profiles.get_supported_profile(template.profile_template_id)
        load_contract_schema()
        fixture = harness.Fixture.from_payload(prefix_fixture())
        report = harness.run_negative(fixture)
        self.assertTrue(report["passed"])
        self.assertEqual(report["evidence_class"], "executed_negative_duration_prefix")
        imported = GRCV4StepResult.from_payload(report["actual"]["result"])
        control = harness.run_negative(fixture, operation=lambda request, subject: imported)
        self.assertTrue(control["passed"])
        self.assertEqual(control["evidence_class"], "harness_mutation_control")
        successful = GRCV4StepResult(**result_fixture())
        GRCV4StepResult.from_payload(successful.to_payload())
        with patch.object(harness, "run_negative", side_effect=AssertionError("inspection executed")):
            inspected = harness.inspect_run(
                Path(__file__).resolve().parents[2],
                "implementation/phase-9-grcv4/evidence/P9-2.5/audit-corrected-prefix")
        self.assertEqual(inspected["evidence_class"], "executed_negative_duration_prefix")
        self.assertFalse(inspected["runtime_profile_conformance"])
        self.assertFalse(inspected["parent_lineage_validated"])
        discovery = profiles.list_supported_profiles()
        with self.assertRaises(AttributeError):
            getattr(discovery, "add")("C_OS")
        self.assertEqual(profiles.list_supported_profiles(), frozenset())

    def test_shared_acyclic_wide_context_survives_projection_and_reconstruction(self) -> None:
        shared: dict[str, Any] = {"nested": [True, {"weight": 0.125}]}
        payload = step_input()
        payload["context_value"] = {f"edge-{i}": shared for i in range(1024)}
        request = api.GRCV4StepRequestInput.from_payload(payload)
        before = request.to_canonical_bytes()
        with patch.object(FrozenJSONMap, "__getitem__",
                          side_effect=AssertionError("per-key traversal")):
            self.assertEqual(request.to_canonical_bytes(), before)
            self.assertEqual(canonical_json_bytes(request.to_payload()), before)
        restored = api.GRCV4StepRequestInput.from_canonical_bytes(before)
        shared["nested"].clear()
        projected = restored.to_payload()
        assert isinstance(projected["context_value"], dict)
        projected["context_value"].clear()
        self.assertEqual(restored.to_canonical_bytes(), before)
        self.assertEqual(request.to_canonical_bytes(), before)
        cyclic: dict[str, Any] = {}
        cyclic["self"] = cyclic
        payload["context_value"] = cyclic
        with self.assertRaises(ValueError):
            api.GRCV4StepRequestInput.from_payload(payload)

    def test_distinct_current_reset_history_and_carrier_ownership(self) -> None:
        from pygrc.models.grc_v4_state import GRCV4AuthoritativeState, GRCV4LifecycleState
        from tests.models.test_grc_v4_state import fixture

        for candidate, realization in (("C","OS"),("A","OS"),("C","PC"),("A","CI+PC")):
            data = fixture(candidate, realization)
            live: Any = {"C": [1.,2.], "W_A": [.5] if candidate=="A" else None,
                         "Z_4": [-.25,.5] if realization in ("PC","CI+PC") else None}
            reset: Any = {"C": [2.,1.], "W_A": [.75] if candidate=="A" else None,
                          "Z_4": [.125,.25] if realization in ("PC","CI+PC") else None}
            data["current"] = GRCV4AuthoritativeState(**live)
            data["reset"] = replace(data["reset"],authoritative=GRCV4AuthoritativeState(**reset))
            record = GRCV4LifecycleState(**data)
            for key in live:
                if live[key] is not None:
                    self.assertNotEqual(getattr(record.current,key),getattr(record.reset.authoritative,key))
                    live[key].clear()
                    reset[key].clear()
                    self.assertTrue(getattr(record.current,key))
                    self.assertTrue(getattr(record.reset.authoritative,key))

    def test_selected_guard_mutations_are_detected_at_the_intended_boundary(self) -> None:
        from pygrc.models import grc_v4_profile as profiles
        from pygrc.models.grc_v4_codec import V4IdentityError
        from pygrc.models.grc_v4_state import GRCV4Event
        from tests.models.test_grc_v4_profile import fixture

        declared = profiles.resolve_profile(*fixture())
        def unsupported_guard() -> None:
            with self.assertRaises(V4IdentityError):
                profiles.get_supported_profile(declared.complete_profile_id)
        unsupported_guard()
        # Isolated Python test doubles, not passing integration providers.
        with patch.object(profiles,"get_supported_profile",return_value=declared):
            with self.assertRaises(AssertionError):
                unsupported_guard()
        event = GRCV4Event("test",0,FrozenJSONMap({"nested":[1]}))
        def detached_guard() -> None:
            a,b = event.to_common_event(),event.to_common_event()
            a.payload.clear()
            self.assertEqual(b.payload,{"nested":[1]})
        detached_guard()
        cached = event.to_common_event()
        with patch.object(GRCV4Event,"to_common_event",return_value=cached):
            with self.assertRaises(AssertionError):
                detached_guard()

    def test_ten_declarations_and_parameter_variants_do_not_register_support(self) -> None:
        from pygrc.models.grc_v4_codec import V4IdentityError
        from pygrc.models.grc_v4_profile import (
            GRCV4Profile, get_supported_profile, resolve_profile,
        )
        from tests.models.test_grc_v4_profile import family_fixture, reidentify

        ids: set[str] = set()
        for candidate in ("A", "C"):
            for realization in ("CI", "OS", "RG2b", "PC", "CI+PC"):
                for tolerance in (0, 0.125):
                    params, identity = family_fixture(candidate, realization)
                    params["solver"]["absolute_tolerance"] = tolerance
                    reidentify(params, identity)
                    declared = resolve_profile(params, identity)
                    restored = GRCV4Profile.from_canonical_bytes(declared.to_canonical_bytes())
                    ids.add(restored.complete_profile_id)
                    for label in (restored.complete_profile_id, identity["profile_family_id"],
                                  candidate, realization):
                        with self.subTest(candidate=candidate, realization=realization,
                                          tolerance=tolerance, label=label):
                            with self.assertRaisesRegex(V4IdentityError, "unsupported executable"):
                                get_supported_profile(label)
                    self.assertEqual(list_supported_profiles(), frozenset())
        self.assertEqual(len(ids), 20)

    def test_duration_validation_still_does_not_admit_a_profile_or_context(self) -> None:
        from pygrc.models.grc_v4_codec import V4IdentityError
        from pygrc.models.grc_v4_profile import get_supported_profile
        from tests.models.test_grc_v4_step import scientific_fixture

        # These shape-valid declarations intentionally contain unresolved
        # context/domain labels. There is no graph input on this prefix API.
        for dt in (0.0, 5e-324, 1.7976931348623157e308):
            payload = step_input(dt)
            payload["context_value"] = {"domain": "unresolved", "profile": "C_OS"}
            request = api.GRCV4StepRequestInput.from_payload(payload)
            strict = admission.admit_step_request(
                request, source_state_digest="grcv4-state-sha256:" + "f" * 64)
            self.assertIs(type(strict), api.GRCV4StepRequest)
            self.assertFalse(hasattr(strict, "committed"))
            self.assertFalse(hasattr(strict, "admitted_profile"))
            with self.assertRaises(V4IdentityError):
                get_supported_profile("C_OS")
            # No fake success/no-op result is supplied by the negative prefix.
            fixture = scientific_fixture()
            with self.assertRaisesRegex(V4SchemaError, "requires full step admission"):
                admission.negative_duration_result(
                    request, prestate=fixture, receipt_ledger=[],
                    active_profile_id=fixture["active_model_identity"])
        from pygrc.core.interfaces import GRCModel
        self.assertTrue(issubclass(api.GRCV4, GRCModel))

    def test_recursive_ownership_across_records_and_common_projections(self) -> None:
        from collections.abc import Mapping
        from pygrc.core.types import GRCState, StepResult
        from pygrc.models.grc_v4_profile import resolve_profile
        from pygrc.models.grc_v4_state import (
            GRCStateSurface, GRCV4LifecycleState, GRCV4State,
            GRCV4StepResult, StepResultSurface,
        )
        from tests.models.test_grc_v4_profile import fixture as profile_fixture
        from tests.models.test_grc_v4_state import (
            fixture as state_fixture, mutate, result_fixture,
        )

        profile = resolve_profile(*profile_fixture())
        raw = state_fixture()
        raw["profile"] = profile.to_payload()
        # Align the shape fixture's reset identity without claiming admission.
        raw["reset"] = replace(raw["reset"], active_model_identity=profile.complete_profile_id)
        lifecycle = GRCV4LifecycleState(**raw)
        state = GRCV4State(lifecycle)
        event_input = result_fixture()
        result = GRCV4StepResult(**event_input)
        request = api.GRCV4StepRequestInput.from_payload(step_input())
        migration_record = api.GRCV4MigrationRequest.from_payload(migration())

        def frozen_tree(value: Any) -> None:
            if value is None or type(value) in (str, int, float, bool):
                return
            self.assertNotIsInstance(value, (dict, list, set, bytearray))
            if is_dataclass(value):
                self.assertTrue(getattr(value, "__dataclass_params__").frozen)
                self.assertFalse(hasattr(value, "__dict__"))
                for field in fields(value):
                    with self.assertRaises((FrozenInstanceError, AttributeError, TypeError)):
                        setattr(value, field.name, None)
                    frozen_tree(getattr(value, field.name))
            elif isinstance(value, Mapping):
                self.assertIs(type(value), FrozenJSONMap)
                for key, item in value.items():
                    frozen_tree(item)
                    with self.assertRaises(TypeError):
                        mutate(value, key, None)
            elif type(value) is tuple:
                for item in value:
                    frozen_tree(item)
            else:
                self.fail(f"unexpected retained storage type: {type(value).__name__}")

        for record in (profile, lifecycle, state, result, request, migration_record):
            frozen_tree(record)
        self.assertIsInstance(state, GRCStateSurface)
        self.assertIsInstance(result, StepResultSurface)
        self.assertNotIsInstance(state, GRCState)
        self.assertNotIsInstance(result, StepResult)
        self.assertEqual([f.name for f in fields(state)], ["lifecycle"])
        self.assertEqual(state.budget_target, lifecycle.Q_target)
        self.assertIsNone(state.remainder)
        before = canonical_json_bytes(result.to_payload())
        event_input["events"][0].payload["nested"].clear()
        result.events[0].payload.clear()
        result.to_payload().clear()
        raw["graph"]["live_node_ids"].clear()
        raw["profile"].clear()
        self.assertEqual(before, canonical_json_bytes(result.to_payload()))
        self.assertEqual(lifecycle.graph["live_node_ids"], ("v0", "v1"))
        self.assertEqual(lifecycle.profile["complete_profile_id"], profile.complete_profile_id)

    def test_consumed_legacy_imports_and_replacement_boundary(self) -> None:
        # Exact direct source consumption, not the already-imported legacy
        # package initializer's transitive modules. New uses need review.
        root = Path(__file__).resolve().parents[2]
        for name in ("grc_v4", "grc_v4_codec", "grc_v4_profile", "grc_v4_state", "grc_v4_step"):
            source = (root / f"src/pygrc/models/{name}.py").read_text()
            tree = ast.parse(source)
            legacy: list[str] = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    legacy.extend(alias.name for alias in node.names
                                  if alias.name.startswith("pygrc."))
                if isinstance(node, ast.ImportFrom):
                    module = resolve_name("." * node.level + (node.module or ""),
                                          "pygrc.models")
                    if module.startswith("pygrc.") and not module.startswith("pygrc.models.grc_v4"):
                        legacy.extend(f"{module}.{alias.name}" for alias in node.names)
            expected = {
                "grc_v4_state": ["pygrc.core.events.GRCEvent"],
                "grc_v4": ["pygrc.core.interfaces.GRCModel"],
            }
            self.assertEqual(legacy, expected.get(name, []))
            self.assertNotIn("type: ignore[override]", source)
            self.assertNotIn("mypy: ignore-errors", source)
        from pygrc.core.serialization import canonical_json_dumps
        self.assertEqual(canonical_json_dumps({"x": "é"}), '{"x":"\\u00e9"}')
        self.assertEqual(canonical_json_bytes({"x": "é"}), '{"x":"é"}'.encode())

    def test_explicit_legacy_baseline_and_package_exports_remain_unchanged(self) -> None:
        root = Path(__file__).resolve().parents[2]
        register = json.loads((root / "implementation/phase-9-grcv4/tranche-1/"
                               "P9-1.5-OwnershipAndLegacyBaseline.json").read_text())
        # pyproject's reviewed V4-only extra is checked by the successor audit.
        # P9-4.9.1 adds exactly one V4 export; legacy bytes remain intact after
        # stripping the explicit lazy export, not a new mutable baseline.
        checked = 0
        for row in register["legacy_bindings"]:
            if row["path"] == "pyproject.toml":
                continue
            with self.subTest(path=row["path"]):
                data = (root / row["path"]).read_bytes()
                if row["path"] == "src/pygrc/models/__init__.py":
                    addition = (b'\n\ndef __getattr__(name):\n'
                                b'    if name == "GRCV4":\n'
                                b'        from .grc_v4 import GRCV4\n'
                                b'        return GRCV4\n'
                                b'    raise AttributeError(name)\n')
                    self.assertTrue(data.endswith(addition))
                    data = data[:-len(addition)]
                    from pygrc.models import GRCV4
                    self.assertIs(GRCV4, api.GRCV4)
                self.assertEqual(sha256(data).hexdigest(), row["sha256"])
            checked += 1
        self.assertEqual(checked, 134)


class PublicFacadeTests(unittest.TestCase):
    """P9-4.9.1 actual-receiver integration, not the full G2 catalog."""

    @staticmethod
    def initial(default: dict[str, Any] | None = None) -> Any:
        from tests.models.test_grc_v4_realizations import os_fixture
        return replace(os_fixture(
            candidate={"tau_C": 0, "chi_C": 1, "zeta_C": 3},
            geometry={"kappa_H": 0},
            solver={"absolute_tolerance": 0, "relative_tolerance": 0},
            charge={"absolute_tolerance": 0, "relative_tolerance": 0},
            common={"default_step_request": default},
        ), dt=0.125)

    @staticmethod
    def strict(dt: float = 0.125, operation_id: str = "public-step") -> api.GRCV4StepRequest:
        return api.GRCV4StepRequest(
            "grcv4-step-request-v1", operation_id, dt, FrozenJSONMap({})
        )

    def bytes(self, model: api.GRCV4) -> bytes:
        return canonical_json_bytes(model.snapshot())

    def test_construction_protocols_and_exact_discovery(self) -> None:
        import inspect
        from pygrc.core.interfaces import GRCModel
        from pygrc.core.types import GRCState, StepResult
        from pygrc.models.grc_v4_state import GRCStateSurface, StepResultSurface, GRCV4State
        initial = self.initial()
        config = {"initial": initial.to_payload(), "targets": []}
        model = api.GRCV4.from_config(config)
        self.assertIsInstance(model, GRCModel)
        state = model.get_state()
        self.assertIs(type(state), GRCV4State)
        self.assertIsInstance(state, GRCStateSurface)
        self.assertNotIsInstance(state, GRCState)
        self.assertEqual((state.step_index, state.time, state.budget_target, state.remainder),
                         (0, 0, 4, None))
        self.assertEqual(model.active_model_identity, model.active_profile_id)
        self.assertEqual(model.list_supported_profiles(), frozenset({model.active_profile_id}))
        self.assertEqual(model.list_supported_model_identities(), model.list_supported_profiles())
        self.assertEqual(model.get_supported_profile(model.active_profile_id), initial.geometry.reference.profile)
        for invalid in ("C_OS", "A_OS", "grcv4-profile-sha256:" + "0" * 64):
            with self.assertRaises(ValueError):
                model.get_supported_profile(invalid)
        self.assertEqual(list_supported_profiles(), frozenset())  # accepted set still empty
        self.assertEqual(model.list_capabilities(), {
            "profile_explicit_v4", "single_resource_ledger", "authoritative_current",
            "structural_hodge_geometry", "typed_topology_events", "profile_migration",
            "quadrature_budget", "v4_candidate_c_derived_sector", "v4_realization_os",
        })
        for method, args in (("step", ["self"]), ("run", ["self", "num_steps"]),
                             ("step_v4", ["self", "request"]),
                             ("run_v4", ["self", "requests"]),
                             ("from_state", ["state", "params"])):
            self.assertEqual(list(inspect.signature(getattr(api.GRCV4, method)).parameters), args)
        config["initial"].clear()
        self.assertEqual(model.state, state)
        result = model.step_v4(self.strict())
        self.assertIsInstance(result, StepResultSurface)
        self.assertNotIsInstance(result, StepResult)
        self.assertEqual(model.state.lifecycle.current.C, (2.5, 1.5))  # exact dyadic oracle

    def test_construction_and_restoration_fail_closed(self) -> None:
        from tests.models.test_grc_v4_candidate_c import current_fixture
        from pygrc.models.grc_v4_state import GRCV4AuthoritativeState
        initial = self.initial()
        for config in (None, [], {}, {"initial": initial.to_payload(), "default_step_request": {}},
                       {"initial": initial.to_payload(), "targets": ()}):
            with self.subTest(config=config), self.assertRaises((TypeError, ValueError)):
                api.GRCV4.from_config(config)
        for bad in (replace(initial, stage="os_corrector"),
                    replace(initial, current=GRCV4AuthoritativeState((3, 2), None, None)),
                    replace(initial, receipt_ids=("grc-receipt-sha256:" + "0" * 64,)),
                    current_fixture(realization="CI")):
            with self.assertRaises((TypeError, ValueError)):
                api.GRCV4(bad)
        model = api.GRCV4(initial)
        saved = model.snapshot()
        for key in ("reset", "receipt_parent_policy_id", "reference_registry"):
            bad = deepcopy(saved)
            del bad[key]
            with self.assertRaises(ValueError):
                api.GRCV4.from_state(bad, model.get_params().to_payload())
        with self.assertRaises(ValueError):
            api.GRCV4.from_state(saved, {})
        self.assertEqual(model.snapshot(), saved)

    def test_strict_input_duration_edges_and_atomic_rejection(self) -> None:
        model = api.GRCV4(self.initial())
        before = self.bytes(model)
        for request in ({}, None, step_input(), api.GRCV4StepRequestInput.from_payload(step_input())):
            with self.assertRaises(TypeError):
                model.step_v4(request)
        for dt in (-1.0, -5e-324, -1.7976931348623157e308):
            value = api.GRCV4StepRequestInput.from_payload(step_input(dt))
            result = model.step_v4_input(value)
            self.assertFalse(result.committed)
            self.assertEqual(result.failure.code, "invalid_duration")
            self.assertEqual(self.bytes(model), before)
        for dt in (True, -0.0, float("nan"), float("inf"), 2**53):
            with self.assertRaises(ValueError):
                self.strict(dt)
        for dt in (0.0, 5e-324):
            instance = api.GRCV4(self.initial())
            result = instance.step_v4(self.strict(dt))
            self.assertTrue(result.committed, result.failure)
            self.assertEqual(instance.state.time, dt)
            self.assertEqual(instance.state.step_index, int(dt > 0))
            self.assertEqual(instance.state.lifecycle.current.C, (3, 1))
            self.assertEqual(len(instance.state.lifecycle.receipt_ledger), 4)
        extreme = model.step_v4(self.strict(1.7976931348623157e308))
        self.assertFalse(extreme.committed)
        self.assertEqual(extreme.failure.code, "nonfinite_value")
        self.assertEqual(self.bytes(model), before)
        for field, value in (("context_value", {"unimplemented": 1}),
                             ("boundary_input", {}), ("external_source", {})):
            payload = self.strict().to_payload()
            payload[field] = value
            result = model.step_v4(api.GRCV4StepRequest.from_payload(payload))
            self.assertFalse(result.committed)
            self.assertEqual(result.failure.code, "domain_failure")
            self.assertEqual(self.bytes(model), before)

    def test_fixed_default_common_run_and_missing_request(self) -> None:
        missing = api.GRCV4(self.initial())
        before = self.bytes(missing)
        for call in (missing.step, lambda: missing.run(1)):
            with self.assertRaises(api.MissingV4StepRequest):
                call()
        self.assertEqual(self.bytes(missing), before)
        self.assertEqual(missing.run(0), [])
        for n in (True, 1.5, "2", None):
            with self.assertRaises(TypeError):
                missing.run(n)
        with self.assertRaises(ValueError):
            missing.run(-1)
        default = self.strict().to_payload()
        model = api.GRCV4(self.initial(default))
        default["dt"] = 0  # caller alias cannot alter profile/default identity
        explicit = api.GRCV4(self.initial(self.strict().to_payload()))
        results = model.run(2)
        expected = explicit.run_v4(iter([self.strict(), self.strict()]))
        self.assertEqual([r.to_payload() for r in results], [r.to_payload() for r in expected])
        self.assertEqual(model.snapshot(), explicit.snapshot())
        restored = api.GRCV4.from_state(model.snapshot(), model.get_params().to_payload())
        self.assertEqual(restored.step().to_payload(), model.step().to_payload())
        restored.reset()
        self.assertEqual(restored.get_params().common.default_step_request["dt"], 0.125)
        self.assertTrue(restored.step().committed)

    def test_run_v4_is_lazy_and_does_not_rollback_consumed_commits(self) -> None:
        model = api.GRCV4(self.initial())
        seen = []
        def requests():
            seen.append(model.state.step_index)
            yield self.strict()
            seen.append(model.state.step_index)
            payload = self.strict().to_payload()
            payload["context_value"] = {"invalid": 1}
            yield api.GRCV4StepRequest.from_payload(payload)
            seen.append(model.state.step_index)
            yield self.strict(0)
        results = model.run_v4(requests())
        self.assertEqual([r.committed for r in results], [True, False, True])
        self.assertEqual(seen, [0, 1, 1])
        def broken():
            yield self.strict()
            raise RuntimeError("iterator stopped")
        with self.assertRaisesRegex(RuntimeError, "iterator stopped"):
            model.run_v4(broken())
        self.assertEqual(model.state.step_index, 2)
        with self.assertRaises(TypeError):
            model.run_v4([self.strict(0), {}])
        self.assertEqual(len(model.state.lifecycle.receipt_ledger), 16)

    def test_observables_are_fresh_staged_detached_and_prepublication(self) -> None:
        from pygrc.models import grc_v4_lifecycle as lifecycle
        model = api.GRCV4(self.initial())
        before = self.bytes(model)
        obs = model.compute_observables()
        self.assertEqual((obs["budget_current"], obs["charge_current"], obs["budget_error"],
                          obs["num_nodes"], obs["num_edges"]), (4, 4, 0, 2, 1))
        self.assertIsNone(obs["abundance"])
        self.assertEqual(obs["abundance_status"], "not_defined_by_v4_contract")
        self.assertIsNone(obs["solver_disposition"])
        self.assertEqual(obs["authoritative_current"]["values"], [4])
        self.assertFalse(obs["authoritative_current"]["consumed_by_continuity"])
        obs["authoritative_current"]["values"].clear()
        self.assertEqual(self.bytes(model), before)
        # A facade must not compute a fallible result projection after commit.
        with patch.object(lifecycle, "_public_observables", side_effect=RuntimeError("projection")):
            with self.assertRaisesRegex(RuntimeError, "projection"):
                model.step_v4(self.strict())
        self.assertEqual(self.bytes(model), before)
        result = model.step_v4(self.strict())
        self.assertEqual(result.observables["authoritative_current"]["stage"], "os_corrector")
        self.assertTrue(result.observables["authoritative_current"]["consumed_by_continuity"])
        self.assertEqual(result.observables["authoritative_current"]["values"], (4,))
        after = self.bytes(model)
        fresh = model.compute_observables()
        self.assertEqual(fresh["authoritative_current"]["stage"], "read_only_reference")
        self.assertEqual(fresh["authoritative_current"]["values"], [2])
        self.assertEqual(len(fresh["receipt_ledger"]), 4)
        fresh["receipt_ledger"].clear()
        self.assertEqual(self.bytes(model), after)
        self.assertNotIn("authoritative_current", model.snapshot())

    def test_public_lifecycle_restore_assignment_and_receipt_parent_delegation(self) -> None:
        from pygrc.models.grc_v4_state import GRCV4State
        from tests.models.test_grc_v4_lifecycle import _p946_assignment
        model = api.GRCV4(self.initial())
        model.set_state(GRCV4State(_p946_assignment(model._operation, (1, 3))))
        self.assertEqual(model.state.lifecycle.current.C, (1, 3))
        self.assertEqual(model.state.lifecycle.receipt_ledger, ())
        before = self.bytes(model)
        with self.assertRaises(TypeError):
            model.set_state(model.state.lifecycle)
        with self.assertRaises(ValueError):
            model.set_state(GRCV4State(replace(model.state.lifecycle, time=1)))
        self.assertEqual(self.bytes(model), before)
        model.rebase_reset_baseline()
        model.step_v4(self.strict())
        model.reset()
        self.assertEqual(model.state.lifecycle.current.C, (1, 3))
        ledger = model.snapshot()["receipt_ledger"]
        # Public reset/rebase and steps share the previous-primary owner.
        for offset in range(0, len(ledger), 4):
            expected = [] if offset == 0 else [ledger[offset - 4]["receipt_id"]]
            for row in ledger[offset:offset + 4]:
                self.assertEqual(row["identity_payload"]["core"]["parent_receipt_ids"], expected)
        for duplicate in (copy(model), deepcopy(model),
                          api.GRCV4.from_state(model.snapshot(), model.get_params().to_payload())):
            self.assertEqual(duplicate.snapshot(), model.snapshot())
            self.assertIsNot(duplicate._operation, model._operation)
            self.assertTrue(duplicate.step_v4(self.strict(0)).committed)
        self.assertEqual(len(model.snapshot()["receipt_ledger"]), 12)

    def test_save_load_defaults_and_actual_crossings(self) -> None:
        import tempfile
        from tests.models.test_grc_v4_lifecycle import event_request, event_target, migration_request
        from tests.models.test_grc_v4_realizations import os_fixture
        target = os_fixture(candidate={"chi_C": 0, "zeta_C": 0}, geometry={"kappa_H": 0},
                            common={"default_step_request": self.strict(0, "target-default").to_payload()}).geometry.reference
        event_ref = event_target()
        model = api.GRCV4(self.initial(), targets=(target, event_ref))
        migrated = model.migrate_profile(migration_request(model._operation, target))
        self.assertTrue(migrated.committed, migrated.failure)
        self.assertEqual(model.active_profile_id, target.profile.complete_profile_id)
        self.assertTrue(model.step().committed)
        before = self.bytes(model)
        bad = migration_request(model._operation, target, target_profile_id="grcv4-profile-sha256:" + "0" * 64)
        self.assertFalse(model.migrate_profile(bad).committed)
        self.assertEqual(self.bytes(model), before)
        event = event_request(model._operation, event_ref, [1, 0, 0, 1, 0, 0], [0, 0, 0.5])
        result = model.apply_topology_event(event)
        self.assertTrue(result.committed, result.failure)
        self.assertEqual(model.state.lifecycle.current.C, (3, 1, 0.5))
        self.assertEqual(model.state.budget_target, 4.5)
        self.assertEqual(model.compute_observables()["num_nodes"], 3)
        with self.assertRaises(api.MissingV4StepRequest):
            model.step()  # target has no default; never reuse the source profile's
        # File paths are transient test resources, never embedded in snapshots.
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / "snapshot.json")
            model.save(path)
            restored = api.GRCV4.load(path)
            self.assertEqual(restored.snapshot(), model.snapshot())
            self.assertEqual(restored.list_supported_profiles(), model.list_supported_profiles())
            self.assertTrue(restored.step_v4(self.strict(0)).committed)
        model.reset()
        self.assertEqual(model.state.lifecycle.current.C, (3, 1, 0.5))


class RequestTests(unittest.TestCase):
    def test_input_and_strict_types_are_distinct_on_all_construction_paths(self) -> None:
        for number in [0, 0.0, 1, 1.0, 0.125, 5e-324, float(2**53 - 1), 1e20]:
            for kind in STEP_RECORDS:
                data = step_input(number)
                if kind is api.GRCV4StepRequest:
                    data["schema_version"] = "grcv4-step-request-v1"
                a, b = kind.from_payload(data), kind(**data)
                with self.subTest(number=number, kind=kind.__name__):
                    self.assertIs(type(a.dt), float)
                    self.assertEqual(a, b)
                    self.assertEqual(a.to_canonical_bytes(), canonical_json_bytes(data))
                    self.assertEqual(kind.from_canonical_bytes(a.to_canonical_bytes()), a)
        self.assertNotIsInstance(api.GRCV4StepRequestInput.from_payload(step_input()),
                                 api.GRCV4StepRequest)

    def test_negative_duration_is_input_not_strict_record(self) -> None:
        for dt in [-1, -0.25, -5e-324, -1e20]:
            data = step_input(dt)
            self.assertLess(api.decode_step_request_input(json.dumps(data)).dt, 0)
            data["schema_version"] = "grcv4-step-request-v1"
            constructors: list[Callable[[dict[str, Any]], object]] = [
                api.GRCV4StepRequest.from_payload,
                lambda v: api.GRCV4StepRequest(**v)]
            for construct in constructors:
                with self.assertRaises(V4SchemaError):
                    construct(data)

    def test_strict_and_input_schemas_cannot_be_interchanged(self) -> None:
        data = step_input()
        with self.assertRaises(V4SchemaError):
            api.GRCV4StepRequest.from_payload(data)
        data["schema_version"] = "grcv4-step-request-v1"
        with self.assertRaises(V4DecodeShapeError):
            api.decode_step_request_input(json.dumps(data))

    def test_all_missing_extra_and_wrong_shape_inputs_fail_before_admission(self) -> None:
        bad: list[object] = []
        for key in step_input():
            data = step_input(-1)
            del data[key]
            bad.append(data)
        for key, value in [("dt", True), ("dt", "-1"), ("dt", None),
                           ("operation_id", ""), ("operation_id", True),
                           ("schema_version", "unknown"), ("context_value", []),
                           ("boundary_input", 0), ("external_source", False),
                           ("topology_event", {}), ("harness_fault", {}),
                           ("__reduce__", "not_a_deserializer")]:
            data = step_input(-1)
            data[key] = value
            bad.append(data)
        bad.extend([[], None, False, 1, "request"])
        for value in bad:
            with self.subTest(value=value), patch.object(admission, "admit_step_request") as enter:
                with self.assertRaises(V4DecodeShapeError):
                    admission.admit_step_request(api.decode_step_request_input(json.dumps(value)),
                                                 source_state_digest="unused")
                enter.assert_not_called()

    def test_malformed_wire_is_not_a_semantic_failure(self) -> None:
        bad: list[bytes | str] = [b"\xff", b"{", b"\xef\xbb\xbf{}", "{\"dt\":1,\"dt\":2}",
               '{"x":1,"\\u0078":2}', '"\\ud800"', "NaN", "1e999", "-0", "-0.0",
               "9007199254740992", '{"nested":{"x":1,"x":2}}']
        for wire in bad:
            with self.subTest(wire=wire), self.assertRaises(V4WireError):
                api.decode_step_request_input(wire)

    def test_native_numeric_rejections_cannot_be_erased_by_conversion(self) -> None:
        class Coercible:
            def __float__(self) -> float:
                raise AssertionError("numeric hook must not run")
        for dt in [True, False, -0.0, float("inf"), float("nan"), 2**53,
                   -2**63, "1", Coercible()]:
            for kind in STEP_RECORDS:
                data = step_input(dt)
                if kind is api.GRCV4StepRequest:
                    data["schema_version"] = "grcv4-step-request-v1"
                routes: list[Callable[[dict[str, Any]], object]] = [
                    kind.from_payload, lambda d: kind(**d)]
                for route in routes:
                    with self.subTest(dt=dt, kind=kind.__name__):
                        with self.assertRaises((V4WireError, V4SchemaError)):
                            route(data)

    def test_nonzero_wire_underflow_cannot_become_zero_duration_or_context(self) -> None:
        for token in ["1e-4000", "-1e-4000", "1E-4000", "1e-324", "2e-324"]:
            wire = json.dumps(step_input()).replace('0.25', token)
            with self.subTest(token=token), self.assertRaisesRegex(V4WireError, "underflows"):
                api.decode_step_request_input(wire)
            wire = json.dumps(step_input()).replace('"n": 1', '"n": ' + token)
            with self.assertRaises(V4WireError):
                api.decode_step_request_input(wire)
        for token, expected in [("0e-4000", 0.0), ("0.0e100", 0.0), ("5e-324", 5e-324)]:
            wire = json.dumps(step_input()).replace('0.25', token)
            self.assertEqual(api.decode_step_request_input(wire).dt, expected)

    def test_numeric_routes_are_explicit_without_automatic_fallback(self) -> None:
        for dt in [float(2**53), 1e20, 2.0**68, math.nextafter(1e21, 0),
                   1e21, 1.7976931348623157e308, 5e-324, -5e-324]:
            data = step_input(dt)
            data["context_value"] = {"large": 1e20, "tiny": -5e-324}
            raw = canonical_json_bytes(data)
            with self.subTest(dt=dt):
                restored = api.decode_step_request_input(raw, encoding="canonical")
                self.assertEqual(restored.to_canonical_bytes(), raw)
                with self.assertRaises(V4WireError):
                    api.decode_step_request_input(raw)
        for encoding in [True, None, "auto", "json"]:
            with self.assertRaises(TypeError):
                api.decode_step_request_input(b"{}", encoding=encoding)  # type: ignore[arg-type]
        raw = canonical_json_bytes(step_input(1))
        with self.assertRaises(V4WireError):
            api.decode_step_request_input(b" " + raw, encoding="canonical")

    def test_configuration_accepts_subnormals_and_large_exponents_in_isolation(self) -> None:
        # Unlike the mixed-context test above, no other field contains an
        # oversized integer token. A subnormal does not require canonical mode.
        for token, expected in [("5e-324", 5e-324), ("1e308", 1e308),
                                ("1e20", 1e20), ("100000000000000000000.0", 1e20)]:
            wire = json.dumps(step_input()).replace("0.25", token)
            with self.subTest(token=token):
                decoded = api.decode_step_request_input(wire)
                self.assertEqual(decoded.dt, expected)
                raw = decoded.to_canonical_bytes()
                self.assertEqual(api.decode_step_request_input(raw, encoding="canonical"), decoded)
                if expected == 1e20:
                    with self.assertRaises(V4WireError):
                        api.decode_step_request_input(raw)
                else:
                    self.assertEqual(api.decode_step_request_input(raw), decoded)

    def test_int_and_float_duration_have_identical_pinned_jcs_bytes(self) -> None:
        for kind in STEP_RECORDS:
            a, b = step_input(1), step_input(1.0)
            if kind is api.GRCV4StepRequest:
                a["schema_version"] = b["schema_version"] = "grcv4-step-request-v1"
            self.assertEqual(canonical_json_bytes(a), canonical_json_bytes(b))
            self.assertEqual(kind.from_payload(a), kind.from_payload(b))
            self.assertEqual(kind.from_payload(a).to_canonical_bytes(), canonical_json_bytes(b))

    def test_exact_underflow_midpoint_applies_to_duration_and_nested_data(self) -> None:
        with localcontext() as ctx:
            ctx.prec = 1200
            midpoint = Decimal(2) ** -1075
            below, above = midpoint - Decimal(10) ** -1100, midpoint + Decimal(10) ** -1100
        for location in ["duration", "context"]:
            for token, allowed in [(str(below), False), (str(midpoint), False), (str(above), True)]:
                wire = json.dumps(step_input()).replace(
                    "0.25" if location == "duration" else '"n": 1',
                    token if location == "duration" else '"n": ' + token)
                with self.subTest(location=location, token=token[:40]):
                    if not allowed:
                        with self.assertRaises(V4WireError):
                            api.decode_step_request_input(wire)
                    else:
                        expected = step_input(5e-324 if location == "duration" else 0.25)
                        if location == "context":
                            expected["context_value"]["x"][1]["n"] = 5e-324
                        self.assertEqual(api.decode_step_request_input(wire).to_canonical_bytes(),
                                         canonical_json_bytes(expected))

    def test_migration_is_declaration_only_and_uses_explicit_numeric_routes(self) -> None:
        data = migration()
        data["target_context_value"] = {"tiny": 5e-324, "large": 1e20}
        # These grammar-valid labels need not denote a live source, supported
        # target or existing history. Decoding does not call step admission.
        data["history_policy"]["candidate"]["disposition"] = "exact_transport"
        with patch.object(admission, "admit_step_request") as enter:
            decoded = api.decode_migration_request(json.dumps(data))
            enter.assert_not_called()
        self.assertEqual(decoded.to_payload(), data)
        raw = canonical_json_bytes(data)
        self.assertEqual(api.decode_migration_request(raw, encoding="canonical"), decoded)
        with self.assertRaises(V4WireError):
            api.decode_migration_request(raw)
        self.assertEqual(list_supported_profiles(), frozenset())
        for name in ["admitted", "committed", "dt", "state", "commit_id"]:
            self.assertFalse(hasattr(decoded, name))

    def test_typed_and_json_identity_preserve_boolean_number_distinctions(self) -> None:
        left = step_input()
        right = deepcopy(left)
        right["context_value"]["x"][0] = 1
        a, b = (api.GRCV4StepRequestInput.from_payload(d) for d in [left, right])
        self.assertNotEqual(a, b)
        self.assertNotEqual(a.to_canonical_bytes(), b.to_canonical_bytes())
        self.assertEqual(len({a, b}), 2)
        with self.assertRaises(V4SchemaError):
            replace(a, dt=True)

    def test_seeded_binary64_transport_and_admission_composition(self) -> None:
        rng = random.Random(923)
        for _ in range(128):
            value = struct.unpack(">d", rng.getrandbits(64).to_bytes(8, "big"))[0]
            if not math.isfinite(value) or value == 0:
                continue
            data = step_input(value)
            decoded = api.decode_step_request_input(canonical_json_bytes(data),
                                                     encoding="canonical")
            with self.subTest(value=value):
                self.assertEqual(struct.pack(">d", decoded.dt), struct.pack(">d", value))
                result = admission.admit_step_request(
                    decoded, source_state_digest="grcv4-state-sha256:" + "0" * 64)
                self.assertIs(type(result), admission.FailureReceipt if value < 0
                              else api.GRCV4StepRequest)

    def test_nested_sources_projections_and_copies_do_not_alias(self) -> None:
        data = step_input()
        data["boundary_input"] = {"b": [1]}
        data["external_source"] = {"s": [2]}
        a = api.GRCV4StepRequestInput.from_payload(data)
        before = a.to_canonical_bytes()
        data["context_value"]["x"].clear()
        data["boundary_input"]["b"].clear()
        data["external_source"]["s"].clear()
        a.to_payload().clear()
        self.assertEqual(before, a.to_canonical_bytes())
        self.assertEqual(a, copy(a))
        self.assertEqual(a, deepcopy(a))
        with self.assertRaises(FrozenInstanceError):
            setattr(a, "dt", -1)

    def test_cycles_arbitrary_objects_and_pickle_never_enter_request_decoding(self) -> None:
        data = step_input()
        data["context_value"]["loop"] = data
        with self.assertRaises(V4WireError):
            api.GRCV4StepRequestInput.from_payload(data)
        for value in [pickle.dumps(step_input()), step_input(), object(), memoryview(b"{}")]:
            with self.assertRaises(V4WireError):
                api.decode_step_request_input(value)  # type: ignore[arg-type]

    def test_harness_payload_is_not_a_production_request_or_hidden_hook(self) -> None:
        fault = {"schema_version": "grcv4-conformance-harness-fault-v1",
                 "stage": "charge_admission", "kind": "force_charge_mismatch"}
        for data in [fault, {**step_input(), "harness_fault": fault},
                     {**step_input(), "target_graph": {}}]:
            with self.assertRaises(V4DecodeShapeError):
                api.decode_step_request_input(json.dumps(data))
        # Opaque context is ordinary identity-bearing data, never interpreted
        # as a fault hook. Its actual contract remains the later owner's job.
        data = step_input()
        data["context_value"] = {"harness_fault": fault}
        value = api.decode_step_request_input(json.dumps(data))
        self.assertEqual(value.context_value.to_dict(), data["context_value"])
        self.assertEqual(list_supported_profiles(), frozenset())
        self.assertTrue(hasattr(api, "GRCV4"))

    def test_migration_nested_typed_declaration_and_roundtrip(self) -> None:
        data = migration()
        a = api.GRCV4MigrationRequest.from_payload(data)
        b = api.GRCV4MigrationRequest(**data)
        self.assertEqual(a, b)
        self.assertIs(type(a.migration_policy), api.GRCV4MigrationPolicy)
        self.assertIs(type(a.history_policy), api.ResolvedHistoryBundlePolicy)
        self.assertIs(type(a.history_policy.candidate), api.ResolvedHistoryChannelPolicy)
        self.assertEqual(api.decode_migration_request(canonical_json_bytes(data),
                                                     encoding="canonical"), a)
        data["target_context_value"]["x"].clear()
        data["history_policy"]["candidate"]["policy_id"] = "changed"
        self.assertNotEqual(a.to_payload(), data)
        self.assertEqual(a.target_context_value, FrozenJSONMap({"x": [True, {"n": 1}]}))

    def test_migration_closed_fields_channels_and_exact_reference_grammar(self) -> None:
        bad = []
        for key in migration():
            data = migration()
            del data[key]
            bad.append(data)
        for field in ["source_state_digest", "target_profile_id"]:
            for suffix in ["\n", "\r", " ", "x"]:
                data = migration()
                data[field] += suffix
                bad.append(data)
        for key, val in [("subject", "carrier"), ("information_loss", "carrier_history_loss"),
                         ("source_history_digest", "grcv4-history-content-sha256:" + "0" * 64),
                         ("target_initializer_id", "forbidden_when_absent")]:
            data = migration()
            data["history_policy"]["candidate"][key] = val
            bad.append(data)
        for data in bad:
            with self.subTest(data=data), self.assertRaises(V4DecodeShapeError):
                api.decode_migration_request(json.dumps(data))

    def test_typed_nested_migration_inputs_are_copied_and_cannot_bypass_validation(self) -> None:
        a = api.GRCV4MigrationRequest.from_payload(migration())
        b = replace(a)
        self.assertIsNot(a.history_policy, b.history_policy)
        self.assertIsNot(a.history_policy.candidate, b.history_policy.candidate)
        object.__setattr__(a.history_policy.candidate, "subject", "carrier")
        with self.assertRaises(V4SchemaError):
            replace(a)
        self.assertEqual(b.history_policy.candidate.subject, "candidate")

    def test_decode_shape_error_retains_cause_not_dependency_failure(self) -> None:
        with self.assertRaises(V4DecodeShapeError) as seen:
            decode_record_payload("step_request_input", "{}")
        self.assertIsInstance(seen.exception.__cause__, V4SchemaError)
        from pygrc.models import grc_v4_codec as codec
        with patch.object(codec, "load_contract_schema", side_effect=codec.V4AssetError("asset")):
            with self.assertRaises(codec.V4AssetError):
                api.decode_step_request_input(json.dumps(step_input()))
        for schema in ["conformance_harness_fault", "step_request", "scientific_state_payload",
                       "expansion_event_request_input", "unknown", "../schema"]:
            with self.assertRaises(V4SchemaError):
                decode_record_payload(schema, b"{}")


def _precorrection_artifact(relative: str) -> bytes:
    """Historical audit inputs remain exact after the successor release."""
    import subprocess

    return subprocess.check_output([
        "git", "show", "f10d105bbed71da7e9a58d851b18e9799a952e0c:" + relative,
    ], cwd=Path(__file__).resolve().parents[2])


def _precorrection_builder() -> dict[str, Any]:
    root = Path(__file__).resolve().parents[2]
    name = "implementation/investigations/grc9v4-constitutive-design/scripts/build_grcv4_specification_vectors.py"
    namespace: dict[str, Any] = {"__file__": str(root / name), "__name__": "precorrection_vector_builder"}
    exec(compile(_precorrection_artifact(name), str(root / name), "exec"), namespace)
    namespace["file_sha256"] = lambda path: sha256(_precorrection_artifact(path.relative_to(root).as_posix())).hexdigest()
    return namespace


def _audit_identity(prefix: str, payload: Any) -> str:
    return prefix + ":" + sha256(canonical_json_bytes(payload)).hexdigest()


class LifecycleCompositionAuditTests(unittest.TestCase):
    """Cross-record integration; original lifecycle capture stays reconstructible."""

    def test_mixed_reference_charge_lineage_and_continuation(self) -> None:
        from fractions import Fraction
        import tempfile
        from pygrc.models.grc_v4_codec import V4IdentityError
        from pygrc.models.grc_v4_lifecycle import CandidateCOSOperation
        identity = _audit_identity
        from tests.models.test_grc_v4_geometry import stage_reference_fixture
        from tests.models.test_grc_v4_lifecycle import (
            dyadic_fixture, event_request, event_target, migration_request,
            request,
        )

        from tests.models.test_grc_v4_realizations import os_fixture

        initial = dyadic_fixture()
        migrated = os_fixture(
            candidate={"chi_C": 0, "zeta_C": 0}, geometry={"kappa_H": 0}
        ).geometry.reference
        target = event_target()
        target_migrated = stage_reference_fixture(
            graph=target.graph, weights={"e": 2, "f": 2}, gain=0,
            changes={
                "candidate": {"tau_C": 0, "chi_C": 0, "zeta_C": 0, "kappa_M_C": 0},
                "charge": {"absolute_tolerance": 0, "relative_tolerance": 0},
                "solver": {"iteration_limit": 2},
            },
        )
        self.assertEqual(len({r.profile.complete_profile_id for r in (
            initial.geometry.reference, migrated, target, target_migrated,
        )}), 4)
        owner = CandidateCOSOperation(initial, targets=(migrated, target, target_migrated))
        last_primary = last_ordinary = None
        crossing_commits: list[str] = []
        receipts: list[dict[str, Any]] = []
        references = [initial.geometry.reference, migrated, target, target_migrated]

        def checkpoint(result: Any, kind: str, current: tuple[float, ...],
                       reset: tuple[float, ...], ref: Any, q: float,
                       index: int, time: float, parent: str | None) -> None:
            nonlocal last_primary, last_ordinary
            if result is not None:
                self.assertTrue(result.committed, result)
            else:
                self.assertIn(kind, ("reset", "rebase_reset_baseline"))
            snap = owner.snapshot()
            self.assertEqual(owner.reference, ref)
            self.assertEqual(owner.state.current.C, current)
            self.assertEqual(owner.state.reset.authoritative.C, reset)
            self.assertEqual((owner.state.Q_target, owner.state.step_index, owner.state.time),
                             (q, index, time))
            reset_payload = {
                "schema_version": "grcv4-reset-baseline-v1",
                "active_model_identity": ref.profile.complete_profile_id,
                "graph_digest": ref.graph.graph_digest,
                "orientation_identity": ref.graph.orientation_identity,
                "authoritative": {"C": list(reset), "W_A": None, "Z_4": None},
                "Q_target": q, "context_contract_id": "constant_zero_context_v1",
            }
            self.assertEqual(owner.state.reset.reset_digest,
                             identity("grcv4-reset-sha256", reset_payload))
            delta = snap["receipt_ledger"][len(receipts):]
            if result is not None:
                self.assertEqual(delta, [r.to_payload() for r in result.emitted_receipts])
            self.assertEqual(len(delta), 4)
            schemas = {"ordinary_step": "grcv4-step-commit-receipt-v1",
                       "migration": "grcv4-profile-migration-receipt-v1",
                       "mapped_topology_event": "grcv4-topology-event-receipt-v1",
                       "reset": "grcv4-reset-receipt-v1",
                       "rebase_reset_baseline": "grcv4-rebase-receipt-v1"}
            self.assertEqual(delta[0]["identity_payload"]["schema_version"], schemas[kind])
            for row in delta:
                core = row["identity_payload"]["core"]
                self.assertEqual(core["parent_receipt_ids"], [] if parent is None else [parent])
                self.assertEqual(core["target_state_digest"], owner.state.scientific_state_digest)
                self.assertEqual(core["target_model_identity"], ref.profile.complete_profile_id)
                self.assertEqual(core["target_graph_digest"], ref.graph.graph_digest)
            receipts.extend(delta)
            self.assertEqual(snap["receipt_ledger"], receipts)
            self.assertEqual(len(snap["commit_records"]), len(receipts) // 4)
            if kind in ("migration", "mapped_topology_event"):
                crossing_commits.append(snap["commit_records"][-1]["commit_id"])
            self.assertEqual([r["commit_id"] for r in snap["transition_records"]], crossing_commits)
            self.assertEqual(len(snap["reference_registry"]), len(references))
            last_primary = delta[0]["receipt_id"]
            if kind == "ordinary_step":
                last_ordinary = last_primary

        checkpoint(owner.step_v4(request(1 / 8, "mixed-step-1")), "ordinary_step",
                   (2.5, 1.5), (3, 1), references[0], 4, 1, 1 / 8, None)
        checkpoint(owner.migrate_profile(migration_request(owner, migrated)), "migration",
                   (2.5, 1.5), (3, 1), migrated, 4, 1, 1 / 8, last_primary)
        stale = event_request(owner, target, [1, 0, 0, 1, 0, 0], [0, 0, .5])
        checkpoint(owner.apply_topology_event(stale), "mapped_topology_event",
                   (2.5, 1.5, .5), (3, 1, .5), target, 4.5, 1, 1 / 8, last_primary)
        # A failed crossing inside a mixed ledger cannot perturb any archive.
        saved = owner.snapshot()
        failure = owner.apply_topology_event(stale)
        self.assertFalse(failure.committed)
        assert failure.failure is not None
        self.assertEqual(failure.failure.code, "invalid_identity")
        self.assertEqual(owner.snapshot(), saved)
        owner.reset()
        checkpoint(None, "reset", (3, 1, .5), (3, 1, .5), target,
                   4.5, 1, 1 / 8, last_primary)
        owner.rebase_reset_baseline()
        checkpoint(None, "rebase_reset_baseline",
                   (3, 1, .5), (3, 1, .5), target, 4.5, 1, 1 / 8, last_primary)
        checkpoint(owner.migrate_profile(migration_request(owner, target_migrated)),
                   "migration", (3, 1, .5), (3, 1, .5), target_migrated,
                   4.5, 1, 1 / 8, last_primary)

        def evolved(c: tuple[float, ...]) -> tuple[float, ...]:
            # eta=1/2 and edge weights=(2,2): dC/dt = (1/2) L^2 C.
            # This literal matrix is independent of the production step/solver.
            matrix = ((4, -6, 2), (-6, 12, -6), (2, -6, 4))
            return tuple(float(Fraction(c[i]) + sum(
                (Fraction(a) * Fraction(x) / 1024 for a, x in zip(row, c, strict=True)),
                Fraction(),
            )) for i, row in enumerate(matrix))

        c = evolved((3, 1, .5))
        checkpoint(owner.step_v4(request(1 / 1024, "mixed-step-2")), "ordinary_step",
                   c, (3, 1, .5), target_migrated, 4.5, 2, 129 / 1024, last_ordinary)
        # Rebase with a changed current makes the otherwise identity rebase
        # above non-vacuous; the following reset must retain this new baseline.
        owner.rebase_reset_baseline()
        checkpoint(None, "rebase_reset_baseline",
                   c, c, target_migrated, 4.5, 2, 129 / 1024, last_primary)
        final = owner.snapshot()
        for mode in ("reverse", "missing", "duplicate", "wrong_commit"):
            altered = deepcopy(final)
            rows = altered["transition_records"]
            if mode == "reverse":
                rows.reverse()
            elif mode == "missing":
                rows.pop(1)
            elif mode == "duplicate":
                rows[1] = deepcopy(rows[0])
            else:
                rows[1]["commit_id"] = final["commit_records"][0]["commit_id"]
            with self.subTest(archive=mode), self.assertRaises(V4IdentityError):
                CandidateCOSOperation.from_state(altered)
        with tempfile.TemporaryDirectory(prefix="p947 mixed replay ") as scratch:
            path = Path(scratch) / "saved state.json"
            owner.save(str(path))
            restored = CandidateCOSOperation.load(str(path))
            self.assertEqual(restored.snapshot(), final)
            for actor in (owner, restored):
                self.assertTrue(actor.step_v4(request(1 / 1024, "mixed-continuation")).committed)
                self.assertEqual(actor.state.current.C, evolved(c))
                self.assertEqual(actor.state.reset.authoritative.C, c)
                actor.reset()
                self.assertEqual(actor.state.current.C, c)
                # Return to an earlier graph AND exact profile (A -> B -> A).
                # Registry reuse must not collapse distinct crossing commits.
                back = actor.apply_topology_event(event_request(
                    actor, references[0], [1, 0, 0, 0, 1, 1], [0, -.5],
                    operation_id="mixed-return-event",
                ))
                self.assertTrue(back.committed, back)
                returned = (3 + 7 / 1024, 1 - 7 / 1024)
                self.assertEqual(actor.state.current.C, returned)
                self.assertEqual(actor.state.reset.authoritative.C, returned)
                self.assertEqual(actor.state.Q_target, 4)
                self.assertEqual(actor.reference, references[0])
                self.assertEqual(len(actor.snapshot()["transition_records"]), 4)
                self.assertTrue(actor.step_v4(request(1 / 8, "mixed-return-step")).committed)
                difference = Fraction(returned[0]) - Fraction(returned[1])
                self.assertEqual(actor.state.current.C, (
                    float(Fraction(returned[0]) - difference / 4),
                    float(Fraction(returned[1]) + difference / 4),
                ))
            self.assertEqual(owner.snapshot(), restored.snapshot())
            self.assertEqual(CandidateCOSOperation.from_state(owner.snapshot()).snapshot(), owner.snapshot())


def mapped_vector_correction(*, tolerance: float = 2**-40) -> dict[str, Any]:
    """Proposed inputs only. Never rewrite or promote the frozen release."""
    identity = _audit_identity

    builder = _precorrection_builder()
    original = json.loads(_precorrection_artifact("specs/grc-v4-conformance-vectors.json"))[
        "grcv4_mapped_topology_event_vectors"][0]
    graphs = [
        {"schema_version": "grcv4-serialized-graph-v1", "live_node_ids": ["u", "v"],
         "oriented_edges": [{"edge_id": "e-uv", "tail_node_id": "u", "head_node_id": "v"}]},
        original["request"]["target_graph"],
    ]
    references = []
    for graph, weights in zip(graphs, ({"e-uv": 1}, {"e-uv": 1, "e-vw": 2}), strict=True):
        n = len(graph["oriented_edges"])
        k4 = [[int(i == j) for j in range(n)] for i in range(n)]
        params = builder["resolved_params"](weights)
        params["geometry"]["K4_base_digest"] = identity(
            "grcv4-k4-sha256", {"schema_version": "grcv4-k4-identity-v1", "K4_base": k4})
        params["solver"].update(absolute_tolerance=tolerance, relative_tolerance=tolerance)
        profile = builder["profile_payload"](identity("grcv4-params-sha256", params))
        references.append({
            "graph": graph, "params": params, "profile": profile,
            "profile_id": identity("grcv4-profile-sha256", profile),
            "K4_base": k4, "edge_weights": weights,
            "orientation_descriptor": {
                "descriptor_version": "grcv4-ordered-outward-incidence-v1",
                "graph": graph, "positive_flux": "tail_to_head",
                "incidence_tail": 1, "incidence_head": -1,
            },
        })
    states = []
    for ref, resource, q in zip(references, ([1, 2], [1, 2, .5]), (3, 3.5), strict=True):
        reset = {
            "schema_version": "grcv4-reset-baseline-v1",
            "active_model_identity": ref["profile_id"],
            "graph_digest": identity("grc-graph-sha256", ref["graph"]),
            "orientation_identity": identity("grcv4-orientation-sha256", ref["orientation_descriptor"]),
            "authoritative": {"C": resource, "W_A": None, "Z_4": None},
            "Q_target": q, "context_contract_id": "constant_zero_context_v1",
        }
        science = {
            **reset, "schema_version": "grcv4-scientific-state-v1",
            "reset_digest": identity("grcv4-reset-sha256", reset),
            "step_index": 0, "time": 0, "context_value_digest": None,
        }
        states.append({"reset": reset, "science": science,
                       "state_id": identity("grcv4-state-sha256", science)})
    request_payload = {
        **original["request"], "source_state_digest": states[0]["state_id"],
        "target_profile_id": references[1]["profile_id"],
    }
    event_payload = {**original["event_identity_payload"],
                     "source_state_digest": states[0]["state_id"],
                     "target_profile_id": references[1]["profile_id"]}
    return {
        "status": "correction_candidate_not_authoritative",
        "fixture_id": original["fixture_id"],
        "references": references, "states": states,
        "request": request_payload, "event_identity_payload": event_payload,
        "event_identity_canonical_jcs_utf8": canonical_json_bytes(event_payload).decode(),
        "expected": {**original["expected"], "event_id": identity("grc-event-sha256", event_payload)},
    }


def mapped_candidate_owner(candidate: dict[str, Any]) -> Any:
    from pygrc.models.grc_v4_geometry import (
        GRCV4Context, GRCV4Graph, GRCV4ReferenceGeometry, GeometryStageInputs,
    )
    from pygrc.models.grc_v4_profile import resolve_profile
    from pygrc.models.grc_v4_state import GRCV4AuthoritativeState
    from pygrc.models.grc_v4_lifecycle import CandidateCOSOperation

    refs = [GRCV4ReferenceGeometry(
        GRCV4Graph.from_payload(row["graph"]), resolve_profile(row["params"], row["profile"]),
        GRCV4Context("constant_zero_context_v1", FrozenJSONMap({})),
        tuple(tuple(r) for r in row["K4_base"]), FrozenJSONMap(row["edge_weights"]),
    ) for row in candidate["references"]]
    resource = GRCV4AuthoritativeState(tuple(candidate["expected"]["source_resource"]), None, None)
    initial = GeometryStageInputs(
        refs[0].geometry(), refs[0].context, resource, resource,
        "mapped-vector-correction", 3, (), 0, 0, 0, "pre_read", 0, None,
    )
    return CandidateCOSOperation(initial, targets=(refs[1],))


def mapped_builder_correction() -> tuple[str, str]:
    """Exact, bounded successor patch, returned for review without applying it."""
    import difflib

    name = "implementation/investigations/grc9v4-constitutive-design/scripts/build_grcv4_specification_vectors.py"
    original = _precorrection_artifact(name).decode()
    helper = '''def mapped_runtime_params(weights: dict[str, float]) -> dict[str, Any]:
    """Complete binary64-admissible references for the generic mapped fixture."""
    params = resolved_params(weights)
    size = len(weights)
    params["geometry"]["K4_base_digest"] = wrapped_digest(
        "grcv4-k4-sha256", "grcv4-k4-identity-v1", "K4_base",
        [[int(i == j) for j in range(size)] for i in range(size)],
    )
    params["solver"].update(absolute_tolerance=2**-40, relative_tolerance=2**-40)
    return params


def mapped_orientation(graph: dict[str, Any]) -> str:
    return identity("grcv4-orientation-sha256", {
        "descriptor_version": "grcv4-ordered-outward-incidence-v1",
        "graph": graph, "positive_flux": "tail_to_head",
        "incidence_tail": 1, "incidence_head": -1,
    })


'''
    source = original.replace("def build() -> dict[str, Any]:\n", helper + "def build() -> dict[str, Any]:\n")
    start = source.index("    generic_source_params = resolved_params(")
    end = source.index("    first_expansion_payloads =", start)
    block = source[start:end]
    if block.count('"orientation_identity": "tail_to_head_edge_id_order_v1"') != 2:
        raise ValueError("frozen mapped builder orientation slots changed")
    block = block.replace("= resolved_params(", "= mapped_runtime_params(")
    block = block.replace('"orientation_identity": "tail_to_head_edge_id_order_v1"',
                          '"orientation_identity": mapped_orientation(generic_source_graph)')
    marker = '            "event_identity_payload": mapped_event_payload,'
    inputs = '''            "runtime_inputs": {
                "source_graph": generic_source_graph,
                "source_params": generic_source_params,
                "source_profile": generic_source_profile_payload,
                "source_K4_base": [[1]],
                "source_reference_edge_weights": {"e-uv": 1},
                "source_reset": generic_source_reset_payload,
                "source_state": generic_source_state_payload,
                "target_params": generic_target_params,
                "target_profile": generic_target_profile_payload,
                "target_K4_base": [[1, 0], [0, 1]],
                "target_reference_edge_weights": {"e-uv": 1, "e-vw": 2},
            },
'''
    if block.count(marker) != 1:
        raise ValueError("frozen mapped builder row changed")
    block = block.replace(marker, inputs + marker)
    source = source[:start] + block + source[end:]
    delta = "".join(difflib.unified_diff(original.splitlines(True), source.splitlines(True),
                                        fromfile="a/" + name, tofile="b/" + name))
    return source, delta


class MappedVectorCorrectionAuditTests(unittest.TestCase):
    def test_proposed_tolerance_checks_every_solve_without_changing_physics(self) -> None:
        from fractions import Fraction
        from pygrc.models import grc_v4_candidate_c as numerical

        candidate = mapped_vector_correction()
        # Execute the proposed builder patch in memory. Its exact row agrees
        # with independently assembled inputs; the one dependent negative keeps
        # rejecting a foreign params hash. All other vector content stays intact.
        root = Path(__file__).resolve().parents[2]
        builder_path = root / "implementation/investigations/grc9v4-constitutive-design/scripts/build_grcv4_specification_vectors.py"
        proposed, _ = mapped_builder_correction()
        namespace: dict[str, Any] = {"__file__": str(builder_path), "__name__": "mapped_correction_candidate"}
        exec(compile(proposed, str(builder_path), "exec"), namespace)
        namespace["file_sha256"] = _precorrection_builder()["file_sha256"]
        rebuilt = namespace["build"]()
        frozen = json.loads(_precorrection_artifact("specs/grc-v4-conformance-vectors.json"))
        row = rebuilt["grcv4_mapped_topology_event_vectors"][0]
        for field in ("request", "event_identity_payload", "event_identity_canonical_jcs_utf8", "expected"):
            self.assertEqual(row[field], candidate[field])
        self.assertEqual(row["runtime_inputs"]["source_params"], candidate["references"][0]["params"])
        self.assertEqual(row["runtime_inputs"]["target_params"], candidate["references"][1]["params"])
        rebuilt["grcv4_mapped_topology_event_vectors"] = frozen["grcv4_mapped_topology_event_vectors"]
        from pygrc.models.grc_v4_profile import resolve_profile

        negative = rebuilt["semantic_admission"]["negative_vectors"][4]
        self.assertEqual(negative["vector_id"], "SEMANTIC-REJECT-PROFILE-PARAMS-HASH-MISMATCH")
        self.assertIn(negative["input"]["profile_identity"]["params_hash"],
                      [r["profile"]["params_hash"] for r in candidate["references"]])
        with self.assertRaises(ValueError):
            resolve_profile(negative["input"]["resolved_params"], negative["input"]["profile_identity"])
        negative["input"]["profile_identity"]["params_hash"] = frozen["semantic_admission"]["negative_vectors"][4]["input"]["profile_identity"]["params_hash"]
        self.assertEqual(rebuilt, frozen)
        original_solve = numerical._c_solve
        observed: set[str] = set()

        def measured(matrix: Any, rhs: Any, policy: Any, label: str, certificates: Any) -> Any:
            result = original_solve(matrix, rhs, policy, label, certificates)
            observed.add(label)
            for col in range(len(rhs[0])):
                residual = [sum((Fraction(a) * Fraction(result[j][col])
                                 for j, a in enumerate(row)), Fraction()) - Fraction(rhs[i][col])
                            for i, row in enumerate(matrix)]
                # Independent squared norm of A*x-b for every source/target,
                # current/reset readmission solve; no rounded norm comparison.
                self.assertLess(sum((x*x for x in residual), Fraction()), Fraction(2)**-90, label)
            return result

        with patch.object(numerical, "_c_solve", measured):
            owner = mapped_candidate_owner(candidate)
            result = owner.apply_topology_event(api.GRCV4MappedTopologyEventRequest.from_payload(candidate["request"]))
            self.assertTrue(result.committed, result)
        self.assertTrue({"structural flat map", "pre-to-retained identification",
                         "inverse retained identification", "physical current solve"} <= observed)
        # All scientific controls survive the correction; tolerances are explicit
        # profile authority, not a receiver fallback or a zeroed mobility control.
        for row in candidate["references"]:
            c = row["params"]["candidate"]
            self.assertEqual((c["chi_C"], c["zeta_C"], c["kappa_M_C"], c["tau_C"]), (1, .5, .5, 0))
            self.assertEqual(row["params"]["geometry"]["kappa_H"], .5)
            self.assertEqual(row["params"]["solver"]["absolute_tolerance"], 2**-40)

    def test_candidate_exact_identity_execution_and_complete_preimages(self) -> None:
        from pygrc.models.grc_v4_lifecycle import CandidateCOSOperation
        from pygrc.models.grc_v4_candidate_c import CandidateCCurrent
        from pygrc.models.grc_v4_lifecycle import _state_inputs
        from fractions import Fraction

        candidate = mapped_vector_correction()
        owner = mapped_candidate_owner(candidate)
        self.assertEqual(owner.state.scientific_state_digest, candidate["states"][0]["state_id"])
        self.assertEqual(owner.reference.profile.complete_profile_id, candidate["references"][0]["profile_id"])
        declaration = api.GRCV4MappedTopologyEventRequest.from_payload(candidate["request"])
        result = owner.apply_topology_event(declaration)
        self.assertTrue(result.committed, result)
        self.assertEqual(owner.state.current.C, (1, 2, .5))
        self.assertEqual(owner.state.reset.authoritative.C, (1, 2, .5))
        self.assertEqual((owner.state.Q_target, owner.state.step_index, owner.state.time), (3.5, 0, 0))
        self.assertEqual(owner.state.scientific_state_digest, candidate["states"][1]["state_id"])
        primary: Any = result.emitted_receipts[0].to_payload()["identity_payload"]
        self.assertEqual(primary["event_id"], candidate["expected"]["event_id"])
        self.assertEqual(primary["core"]["actual_charge_delta"], .5)
        self.assertEqual(owner.reference.profile.complete_profile_id, candidate["references"][1]["profile_id"])
        self.assertEqual(len(result.emitted_receipts), 4)
        restored = CandidateCOSOperation.from_state(owner.snapshot())
        self.assertEqual(restored.snapshot(), owner.snapshot())
        restored.reset()
        self.assertEqual(restored.state.current.C, (1, 2, .5))
        # Independently evaluate the emitted binary64 solution residual with
        # rational arithmetic, far below the proposed declared tolerance.
        for actor in (mapped_candidate_owner(candidate), owner):
            inputs = _state_inputs(actor.reference, actor.state, "residual-oracle")
            solved = CandidateCCurrent(inputs)
            matrix, current = solved.algebra.current_block, solved.current.values
            residual = [sum((Fraction(a) * Fraction(x) for a, x in zip(row, current, strict=True)),
                            Fraction()) - Fraction(b)
                        for row, b in zip(matrix, solved.algebra.baseline.values, strict=True)]
            self.assertLess(sum((x * x for x in residual), Fraction()), Fraction(2)**-90)
            self.assertLess(Fraction(solved.closure_residual_squared), Fraction(2)**-90)

    def test_k4_only_and_zero_tolerance_alternatives_do_not_earn_vector_credit(self) -> None:
        from fractions import Fraction
        from pygrc.models.grc_v4_candidate_c import CandidateCStageError
        identity = _audit_identity

        zero = mapped_vector_correction(tolerance=0)
        with self.assertRaisesRegex(CandidateCStageError, "inverse retained identification"):
            mapped_candidate_owner(zero)
        candidate = mapped_vector_correction()
        owner = mapped_candidate_owner(candidate)
        # A named convention is schema-valid; it is a different representation
        # identity, not a proof that the specification prohibits named strings.
        reset = deepcopy(candidate["states"][0]["reset"])
        reset["orientation_identity"] = "tail_to_head_edge_id_order_v1"
        science = {**candidate["states"][0]["science"],
                   "orientation_identity": reset["orientation_identity"],
                   "reset_digest": identity("grcv4-reset-sha256", reset)}
        changed = {**candidate["request"], "source_state_digest": identity("grcv4-state-sha256", science)}
        before = owner.snapshot()
        result = owner.apply_topology_event(api.GRCV4MappedTopologyEventRequest.from_payload(changed))
        self.assertFalse(result.committed)
        self.assertEqual(result.failure.code, "invalid_identity")
        self.assertEqual(owner.snapshot(), before)
        # For the scalar source, retained identification is a binary64 h.
        # Its rounded reciprocal generally cannot have exact product one.
        deformation = math.exp(.25 * math.tanh(1.5))
        h = float(Fraction(deformation) ** 2)
        x = float(Fraction(1) / Fraction(h))
        residual = abs(Fraction(h) * Fraction(x) - 1)
        self.assertGreater(residual, 0)
        self.assertLess(residual, Fraction(2)**-52)

    def test_dimension_fault_blast_radius_and_graph_coordinate_alternatives(self) -> None:
        from collections import Counter
        from pygrc.models.grc_v4_geometry import (
            GRCV4Context, GRCV4Graph, GRCV4ReferenceGeometry, OrientedEdge,
        )
        from pygrc.models.grc_v4_profile import resolve_profile
        identity = _audit_identity

        builder = _precorrection_builder()
        original = builder["resolved_params"]
        counts: Counter[tuple[str, int]] = Counter()

        def measured(weights: dict[str, Any], profile_family: str = "C_OS") -> dict[str, Any]:
            counts[(profile_family, len(weights))] += 1
            return dict(original(weights, profile_family))

        builder["build"].__globals__["resolved_params"] = measured
        rebuilt = builder["build"]()
        self.assertEqual(rebuilt, json.loads(_precorrection_artifact("specs/grc-v4-conformance-vectors.json")))
        self.assertEqual(sum(counts.values()), 23)
        self.assertEqual(sum(v for (_, n), v in counts.items() if n != 2), 22)
        self.assertEqual(counts[("C_PC", 9)], 1)
        self.assertEqual(counts[("C_PC", 12)], 1)
        # Rank and vertex count do not size K4: repeated/loop coordinates count
        # as full distinct edges, including a graph with one vertex.
        for n in (1, 2, 3, 9):
            graph = GRCV4Graph(("only",), tuple(
                OrientedEdge(f"e-{n-i}", "only", "only") for i in range(n)))
            weights = {edge: 1 for edge in graph.live_edge_ids}
            params = original(weights)
            frozen_profile = resolve_profile(params, builder["profile_payload"](
                identity("grcv4-params-sha256", params)))
            context = GRCV4Context("constant_zero_context_v1", FrozenJSONMap({}))
            if n != 2:
                with self.subTest(edges=n), self.assertRaisesRegex(ValueError, "K4|shape"):
                    GRCV4ReferenceGeometry(graph, frozen_profile, context,
                                           ((1, 0), (0, 1)), FrozenJSONMap(weights))
            k4 = tuple(tuple(int(i == j) for j in range(n)) for i in range(n))
            params["geometry"]["K4_base_digest"] = identity("grcv4-k4-sha256", {
                "schema_version": "grcv4-k4-identity-v1", "K4_base": [list(r) for r in k4]})
            profile = resolve_profile(params, builder["profile_payload"](
                identity("grcv4-params-sha256", params)))
            reference = GRCV4ReferenceGeometry(graph, profile, context, k4, FrozenJSONMap(weights))
            self.assertEqual(len(reference.K4_base), n)
            self.assertEqual(reference.graph.live_edge_ids, graph.live_edge_ids)


class AuthoritativeMappedVectorTests(unittest.TestCase):
    def test_current_release_executes_published_request_and_exact_event_identity(self) -> None:
        from pygrc.models.grc_v4 import GRCV4MappedTopologyEventRequest
        from pygrc.models.grc_v4_codec import RELEASE_ID, load_contract_schema
        from pygrc.models.grc_v4_geometry import (
            GRCV4Context, GRCV4Graph, GRCV4ReferenceGeometry, GeometryStageInputs,
        )
        from pygrc.models.grc_v4_profile import resolve_profile
        from pygrc.models.grc_v4_state import GRCV4AuthoritativeState
        from pygrc.models.grc_v4_lifecycle import CandidateCOSOperation
        from tests.models.test_grc_v4_lifecycle import request

        root = Path(__file__).resolve().parents[2]
        release = json.loads((root / "specs/grc-v4-specification-release.json").read_text())
        self.assertEqual(release["release_id"], RELEASE_ID)
        self.assertEqual(RELEASE_ID, "grcv4-spec-release-sha256:f777519824f86c3e9382bcf9b45cba28554351506f354d3f778746e2aaff5c6b")
        load_contract_schema()
        vector = json.loads((root / "specs/grc-v4-conformance-vectors.json").read_text())[
            "grcv4_mapped_topology_event_vectors"][0]
        self.assertEqual(vector["fixture_id"], "GENERIC-MAPPED-EVENT-NONZERO-RESOURCE-INCREMENT")
        inputs = vector["runtime_inputs"]
        context = GRCV4Context("constant_zero_context_v1", FrozenJSONMap({}))
        refs = [GRCV4ReferenceGeometry(
            GRCV4Graph.from_payload(graph),
            resolve_profile(inputs[prefix + "_params"], inputs[prefix + "_profile"]), context,
            tuple(tuple(row) for row in inputs[prefix + "_K4_base"]),
            FrozenJSONMap(inputs[prefix + "_reference_edge_weights"]),
        ) for prefix, graph in (("source", inputs["source_graph"]), ("target", vector["request"]["target_graph"]))]
        c = GRCV4AuthoritativeState(tuple(vector["expected"]["source_resource"]), None, None)
        initial = GeometryStageInputs(refs[0].geometry(), context, c, c, "authoritative-vector",
                                      3, (), 0, 0, 0, "pre_read", 0, None)
        self.assertEqual(initial.scientific_state_preimage, inputs["source_state"])
        self.assertEqual(initial.reset_preimage, inputs["source_reset"])
        self.assertEqual(initial.scientific_state_id, vector["request"]["source_state_digest"])
        self.assertEqual(refs[1].profile.complete_profile_id, vector["request"]["target_profile_id"])
        owner = CandidateCOSOperation(initial, targets=(refs[1],))
        # Consume the actual published request without changing a single identity.
        declaration = GRCV4MappedTopologyEventRequest.from_payload(vector["request"])
        result = owner.apply_topology_event(declaration)
        self.assertTrue(result.committed, result)
        primary: Any = result.emitted_receipts[0].to_payload()["identity_payload"]
        self.assertEqual(primary["event_id"], vector["expected"]["event_id"])
        self.assertEqual(primary["event_id"], "grc-event-sha256:583d7337ff5d3910fb189ee1aad0f81485a4722bdb889d5623e82828a759807c")
        self.assertEqual(primary["core"]["actual_charge_delta"], .5)
        self.assertEqual(owner.state.current.C, (1, 2, .5))
        self.assertEqual(owner.state.reset.authoritative.C, (1, 2, .5))
        self.assertEqual((owner.state.Q_target, owner.state.step_index, owner.state.time), (3.5, 0, 0))
        self.assertEqual(len(owner.snapshot()["transition_records"]), 1)
        restored = CandidateCOSOperation.from_state(owner.snapshot())
        for actor in (owner, restored):
            actor.reset()
            self.assertEqual(actor.state.current.C, (1, 2, .5))
            self.assertTrue(actor.step_v4(request(0, "authoritative-continuation")).committed)
        self.assertEqual(owner.snapshot(), restored.snapshot())


_P947_AUDIT_METHODS = {
    "LifecycleCompositionAuditTests": (
        "test_mixed_reference_charge_lineage_and_continuation",
    ),
    "MappedVectorCorrectionAuditTests": (
        "test_candidate_exact_identity_execution_and_complete_preimages",
        "test_dimension_fault_blast_radius_and_graph_coordinate_alternatives",
        "test_k4_only_and_zero_tolerance_alternatives_do_not_earn_vector_credit",
        "test_proposed_tolerance_checks_every_solve_without_changing_physics",
    ),
}


def capture_p947_audit(output: str, *, corrected: bool = False) -> int:
    """Additive source-bound pressure; preserve the original 135-method run."""
    from datetime import datetime, timezone
    import importlib
    import importlib.metadata
    import os
    import platform
    import subprocess
    from tests.models.test_grc_v4_candidate_c import _p941_execute

    root = Path(__file__).resolve().parents[2]
    generated = root / (
        "implementation/investigations/grc9v4-constitutive-design/"
        "tools/exploratory-side-tool/tool/generated"
    )
    destination = (root / output).resolve()
    if (not destination.is_relative_to(generated.resolve())
            or destination == generated.resolve() or destination.exists()):
        raise ValueError("capture requires a fresh repository-local generated destination")
    base = "f10d105bbed71da7e9a58d851b18e9799a952e0c"
    scopes = [
        "src", "tests", "specs", "pyproject.toml", "uv.lock",
        "implementation/investigations/grc9v4-constitutive-design/drafts/2026-09-GRC-V4.md",
        "implementation/investigations/grc9v4-constitutive-design/scripts/build_grcv4_specification_vectors.py",
    ]
    overrides = {
        "src/pygrc/models/grc_v4.py", "src/pygrc/models/grc_v4_codec.py",
        "src/pygrc/models/grc_v4_lifecycle.py", "tests/models/test_grc_v4_lifecycle.py",
        "tests/models/test_grc_v4.py",
    }
    if corrected:
        correction_paths = {
            "implementation/phase-9-grcv4/verification/build_mapped_vector_release.py",
            "implementation/phase-9-grcv4/tranche-4/P9-4.7b-SpecificationCorrection.json",
        }
        scopes.extend(sorted(correction_paths))
        overrides |= correction_paths | {
            "implementation/investigations/grc9v4-constitutive-design/scripts/build_grcv4_specification_vectors.py",
            "tests/models/grcv4_reference_oracles.py",
            "tests/models/grcv4_conformance_harness.py",
            "specs/README.md", "specs/grc-v4-conformance-vectors.json",
            "specs/grc-v4-specification-release.json", "specs/grc-v4-specification-release.sha256",
            "src/pygrc/models/grc_v4_assets/grc-v4-specification-release.json",
            "src/pygrc/models/grc_v4_assets/grc-v4-specification-release.sha256",
            "src/pygrc/models/grc_v4_assets/asset-index.json",
        }

    def git(*args: str) -> str:
        return subprocess.check_output(["git", *args], cwd=root, text=True)

    def snapshot() -> dict[str, str]:
        return {n: sha256((root / n).read_bytes()).hexdigest() for n in sorted(set(
            git("ls-files", "--cached", "--others", "--exclude-standard", "--", *scopes).splitlines()))}

    subprocess.run(["git", "merge-base", "--is-ancestor", base, "HEAD"], cwd=root, check=True)
    before = snapshot()
    baseline = set(git("ls-tree", "-r", "--name-only", base, "--", *scopes).splitlines())
    changed = set(git("diff", "--name-only", base, "--", *scopes).splitlines())
    if (changed | (set(before) - baseline)) - overrides or baseline - set(before):
        raise ValueError("source differs outside the P9-4.7 audit reconstruction envelope")
    predecessor = ast.parse(git("show", base + ":tests/models/test_grc_v4.py"))
    prefix = "tests.models.test_grc_v4."
    required = {
        prefix + c.name + "." + n.name
        for c in predecessor.body if isinstance(c, ast.ClassDef)
        and c.name in {"FoundationIntegrationTests", "RequestTests"}
        for n in c.body if isinstance(n, ast.FunctionDef) and n.name.startswith("test_")
    } | {prefix + cls + "." + method for cls, methods in _P947_AUDIT_METHODS.items() for method in methods}
    if corrected:
        required -= {prefix + cls + "." + method for cls, methods in _P947_AUDIT_METHODS.items() for method in methods}
        required |= {
            prefix + "AuthoritativeMappedVectorTests.test_current_release_executes_published_request_and_exact_event_identity",
            prefix + "MappedVectorCorrectionAuditTests.test_proposed_tolerance_checks_every_solve_without_changing_physics",
            prefix + "MappedVectorCorrectionAuditTests.test_dimension_fault_blast_radius_and_graph_coordinate_alternatives",
            "tests.models.test_grc_v4_lifecycle.CandidateCOSCrossingTests.test_published_affine_vector_identities_and_admitted_runtime_companion",
        }
        codec_tests = ast.parse(git("show", base + ":tests/models/test_grc_v4_codec.py"))
        required |= {
            "tests.models.test_grc_v4_codec.CodecTests." + n.name
            for c in codec_tests.body if isinstance(c, ast.ClassDef) and c.name == "CodecTests"
            for n in c.body if isinstance(n, ast.FunctionDef) and n.name.startswith("test_")
        }
    importlib.import_module("tests.models.test_grc_v4_lifecycle")
    importlib.import_module("tests.models.test_grc_v4_transport")
    suite = unittest.defaultTestLoader.loadTestsFromNames(sorted(required))
    started = datetime.now(timezone.utc).isoformat()
    record: dict[str, Any] = {
        "schema": "phase9_leaf_focused_run_v1", "iteration_id": "P9-4.7b audit follow-up",
        "source": {
            "base_commit": base, "scopes": scopes,
            "overrides_sha256": {n: before[n] for n in sorted(overrides)},
            "manifest_sha256": sha256(canonical_json_bytes(before)).hexdigest(), "file_count": len(before),
            "reconstruction": "Overlay only the five hash-matching files from the commit containing this run onto base_commit, then verify the scoped manifest. Before commit use the reviewed working tree. The original 135-method run reconstructs separately with its original four-file overlay.",
        },
        "required_ids": sorted(required), "started_utc": started,
        "python": platform.python_version(), "platform": platform.platform(),
        "dependencies": sorted(f"{d.metadata['Name']}=={d.version}" for d in importlib.metadata.distributions()),
        "environment": {k: os.environ.get(k) for k in ("PYTHONHASHSEED", "OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS")},
        "replay_command": [".venv/bin/python", "-m", "tests.models.test_grc_v4", "--capture-p947-audit", str(destination.relative_to(root))],
        "claim_ceiling": "Mixed C_OS lifecycle composition and a NONAUTHORITATIVE mapped-vector correction candidate. No acceptance of the mandatory frozen row, dependent child, P9-4.8, or runtime support set. No GRC9 runtime execution or blanket fixture repair.",
    }
    if corrected:
        from pygrc.models.grc_v4_codec import RELEASE_ID

        record["iteration_id"] = "P9-4.7b authoritative corrected mapped vector"
        record["release_id"] = RELEASE_ID
        record["replay_command"][3] = "--capture-p947-corrected"
        record["source"]["reconstruction"] = "Overlay exactly the listed hash-matching files from the commit containing this run onto base_commit and verify the scoped manifest. Before commit use the reviewed working tree. Earlier runs retain their separate predecessor-source reconstruction."
        record["claim_ceiling"] = "Exact published mandatory mapped event executed under the accepted successor specification release, plus codec/installed-asset and request/integration regressions. Historical dimension/tolerance controls remain explicitly predecessor-scoped. No P9-4.8, generic parent-DAG, support-set or GRC9 conformance claim."
    record.update(_p941_execute(root, before, required, suite, snapshot, extra_modules=frozenset({
        "pygrc.models.grc_v4", "tests.models.test_grc_v4",
        "pygrc.models.grc_v4_codec", "pygrc.models.grc_v4_state",
        "pygrc.models.grc_v4_geometry", "pygrc.models.grc_v4_transport",
        "pygrc.models.grc_v4_step", "pygrc.models.grc_v4_realizations",
        "pygrc.models.grc_v4_lifecycle", "tests.models.test_grc_v4_lifecycle",
        "tests.models.test_grc_v4_realizations",
    } | ({"tests.models.test_grc_v4_codec"} if corrected else set()))))
    if record["status"] == "passed" and not corrected:
        record["correction_candidate"] = mapped_vector_correction()
        record["proposed_builder_patch"] = mapped_builder_correction()[1]
    elif record["status"] == "passed":
        vector = json.loads((root / "specs/grc-v4-conformance-vectors.json").read_text())["grcv4_mapped_topology_event_vectors"][0]
        record["authoritative_fixture"] = {"fixture_id": vector["fixture_id"], "request_modified": False,
                                            "event_id": vector["expected"]["event_id"], "mandatory_row_waived": False}
    record["completed_utc"] = datetime.now(timezone.utc).isoformat()
    record["live_source_check_limits"] = (
        "Accepted source-slot/live-code and before/after disk/roster guards; not hostile-interpreter attestation. Relocated checkout/fresh interpreter reuse installed dependencies; no fresh-install or different-platform claim."
    )
    if record.get("loaded_sources_before") == record.get("loaded_sources_after"):
        record["loaded_sources"] = record.pop("loaded_sources_before")
        record.pop("loaded_sources_after")
    destination.mkdir(parents=True, exist_ok=False)
    (destination / "run.json").write_text(json.dumps(record, indent=2) + "\n")
    print("P9-4.7 audit", record["status"], json.dumps(record.get("results", {})), flush=True)
    if record["status"] != "passed":
        print(record.get("capture_error", record.get("failure_output", "")), flush=True)
    return 0 if record["status"] == "passed" else 1


if __name__ == "__main__":
    import sys

    if len(sys.argv) == 3 and sys.argv[1] == "--capture-p947-audit":
        raise SystemExit(capture_p947_audit(sys.argv[2]))
    if len(sys.argv) == 3 and sys.argv[1] == "--capture-p947-corrected":
        raise SystemExit(capture_p947_audit(sys.argv[2], corrected=True))
    unittest.main()

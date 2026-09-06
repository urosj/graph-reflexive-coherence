"""Production request transport/shape tests; no live model admission."""

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
        # These are current-stage assertions only, not a ban on later facades.
        self.assertFalse(hasattr(api, "GRCV4"))

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
            self.assertEqual(legacy, ["pygrc.core.events.GRCEvent"] if name == "grc_v4_state" else [])
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
        # No facade exists at this stage, so exports require no edit either.
        checked = 0
        for row in register["legacy_bindings"]:
            if row["path"] == "pyproject.toml":
                continue
            with self.subTest(path=row["path"]):
                self.assertEqual(sha256((root / row["path"]).read_bytes()).hexdigest(),
                                 row["sha256"])
            checked += 1
        self.assertEqual(checked, 134)


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
        self.assertFalse(hasattr(api, "GRCV4"))

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


if __name__ == "__main__":
    unittest.main()

"""Production request transport/shape tests; no live model admission."""

from __future__ import annotations

from collections.abc import Callable
from copy import copy, deepcopy
from dataclasses import FrozenInstanceError, replace
from decimal import Decimal, localcontext
import json
import math
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

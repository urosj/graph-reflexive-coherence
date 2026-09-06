"""Local admission and exact failure identities, not a complete beat test."""

from __future__ import annotations

from collections.abc import Callable
from copy import deepcopy
from dataclasses import replace
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, cast, get_args
import unittest

from pygrc.models.grc_v4 import GRCV4StepRequest, GRCV4StepRequestInput, decode_step_request_input
from pygrc.models.grc_v4_codec import (
    V4IdentityError, V4SchemaError, V4WireError, canonical_json_bytes, payload_identity,
)
from pygrc.models.grc_v4_state import FrozenJSONMap
from pygrc.models.grc_v4_step import (
    FailureCode, FailureReceipt, FailureReceiptIdentityPayload, OperationStage,
    admit_step_request,
)
from tests.models.test_grc_v4 import step_input

SOURCE = "grcv4-state-sha256:" + "a" * 64


def negative_vector() -> dict[str, Any]:
    bundle = json.loads((Path(__file__).resolve().parents[2] /
                         "specs/grc-v4-conformance-vectors.json").read_text())
    return next(v for v in bundle["atomic_failure_vectors"]
                if v["fixture_id"] == "COMMON-NEGATIVE-DURATION")


class StepAdmissionTests(unittest.TestCase):
    def test_published_negative_duration_exact_receipt(self) -> None:
        vector = negative_vector()
        source = vector["expected"]["prestate_digest"]
        result = admit_step_request(decode_step_request_input(json.dumps(vector["request_input"])),
                                    source_state_digest=source)
        self.assertIs(type(result), FailureReceipt)
        assert isinstance(result, FailureReceipt)
        self.assertEqual(result.to_payload(), vector["expected"]["failure_receipt"])
        # Independent stdlib calculation for this ASCII-only frozen preimage.
        raw = json.dumps(vector["expected"]["failure_receipt"]["identity_payload"],
                         sort_keys=True, separators=(",", ":")).encode()
        self.assertEqual(result.receipt_id, "grc-receipt-sha256:" + sha256(raw).hexdigest())

    def test_negative_duration_is_rejected_without_solver_or_ledger_authority(self) -> None:
        for dt in [-5e-324, -0.125, -1, -1e20]:
            value = GRCV4StepRequestInput.from_payload(step_input(dt))
            before = value.to_canonical_bytes()
            result = admit_step_request(value, source_state_digest=SOURCE)
            assert isinstance(result, FailureReceipt)
            self.assertEqual(result.identity_payload.stage, "admission")
            self.assertEqual(result.identity_payload.code, "invalid_duration")
            self.assertEqual(result.identity_payload.source_state_digest,
                             result.identity_payload.observed_poststate_digest)
            self.assertEqual(value.to_canonical_bytes(), before)
            for name in ["solver_disposition", "commit_id", "committed", "ledger"]:
                self.assertFalse(hasattr(result, name))

    def test_positive_and_zero_produce_strict_requests_not_executed_states(self) -> None:
        for dt in [0, 0.0, 5e-324, 1, 1.0, float(2**53), 1e20, 1e308]:
            value = GRCV4StepRequestInput.from_payload(step_input(dt))
            before = value.to_canonical_bytes()
            result = admit_step_request(value, source_state_digest=SOURCE)
            self.assertIs(type(result), GRCV4StepRequest)
            assert isinstance(result, GRCV4StepRequest)
            self.assertIs(type(result.dt), float)
            self.assertEqual(result.dt, dt)
            self.assertEqual(value.to_canonical_bytes(), before)
            # The only current consumer produces a declaration, no proof of
            # graph/profile/context admission, even at zero or extreme dt.
            self.assertEqual(set(result.to_payload()), set(step_input()))
            for name in ["committed", "admitted", "state", "solver_disposition",
                         "commit_id", "ledger", "source_state_digest"]:
                self.assertFalse(hasattr(result, name))

    def test_admission_detaches_input_even_after_unsupported_reinitialization(self) -> None:
        value = GRCV4StepRequestInput.from_payload(step_input())
        result = admit_step_request(value, source_state_digest=SOURCE)
        assert isinstance(result, GRCV4StepRequest)
        before = result.to_canonical_bytes()
        # Explicit reinitialization is not an admission API. Even misuse of
        # the caller's input cannot mutate the separately owned strict record.
        FrozenJSONMap.__init__(value.context_value, {"mutated": True})
        self.assertEqual(before, result.to_canonical_bytes())
        self.assertIsNot(value.context_value, result.context_value)

    def test_wrong_python_types_and_forged_objects_raise_without_receipt(self) -> None:
        for value in [step_input(-1), None, b"{}", object()]:
            with self.assertRaises(TypeError):
                admit_step_request(value, source_state_digest=SOURCE)  # type: ignore[arg-type]
        data = step_input()
        data["schema_version"] = "grcv4-step-request-v1"
        with self.assertRaises(TypeError):
            admit_step_request(GRCV4StepRequest.from_payload(data),  # type: ignore[arg-type]
                               source_state_digest=SOURCE)
        for bad in [True, "-1", -0.0, float("nan"), 2**53]:
            value = GRCV4StepRequestInput.from_payload(step_input())
            object.__setattr__(value, "dt", bad)
            with self.assertRaises((V4SchemaError, V4WireError)):
                admit_step_request(value, source_state_digest=SOURCE)

    def test_bad_source_context_never_becomes_synthetic_failure_evidence(self) -> None:
        for dt in [-1, 0, 1]:
            for digest in ["", SOURCE + "\n", SOURCE.upper(), True, None, "0" * 64]:
                with self.subTest(dt=dt, digest=digest):
                    with self.assertRaises((V4SchemaError, V4WireError)):
                        admit_step_request(GRCV4StepRequestInput.from_payload(step_input(dt)),
                                           source_state_digest=digest)  # type: ignore[arg-type]

    def test_failure_envelope_reconstruction_checks_all_content_fields(self) -> None:
        result = admit_step_request(GRCV4StepRequestInput.from_payload(step_input(-1)),
                                    source_state_digest=SOURCE)
        assert isinstance(result, FailureReceipt)
        self.assertEqual(FailureReceipt.from_payload(result.to_payload()), result)
        self.assertEqual(FailureReceipt(**result.to_payload()), result)  # type: ignore[arg-type]
        for mode in ["wrong_id", "bool_id", "extra", "wrong_operation", "stage", "source_newline"]:
            data = result.to_payload()
            assert isinstance(data["identity_payload"], dict)
            if mode == "wrong_id":
                data["receipt_id"] = "grc-receipt-sha256:" + "0" * 64
            elif mode == "bool_id":
                data["receipt_id"] = True
            elif mode == "extra":
                data["commit_id"] = "grc-commit-sha256:" + "0" * 64
            elif mode == "wrong_operation":
                data["identity_payload"]["operation_id"] = "other"
            elif mode == "stage":
                data["identity_payload"]["stage"] = "unknown"
            else:
                data["identity_payload"]["source_state_digest"] = SOURCE + "\n"
            with self.subTest(mode=mode), self.assertRaises((V4SchemaError, V4IdentityError)):
                FailureReceipt.from_payload(data)

    def test_receipt_equality_does_not_identify_the_request(self) -> None:
        left = GRCV4StepRequestInput.from_payload(step_input(-1))
        data = step_input(-2)
        data["context_value"] = {"different": True}
        right = GRCV4StepRequestInput.from_payload(data)
        self.assertNotEqual(left.to_canonical_bytes(), right.to_canonical_bytes())
        a, b = (admit_step_request(q, source_state_digest=SOURCE) for q in [left, right])
        assert isinstance(a, FailureReceipt) and isinstance(b, FailureReceipt)
        self.assertEqual(a, b)
        self.assertEqual(a.receipt_id, b.receipt_id)
        self.assertNotIn("dt", a.identity_payload.to_payload())
        self.assertNotIn("context_value", a.identity_payload.to_payload())

    def test_receipt_content_is_not_source_or_execution_authentication(self) -> None:
        request = GRCV4StepRequestInput.from_payload(step_input(-1))
        other_source = "grcv4-state-sha256:" + "b" * 64
        a, b = (admit_step_request(request, source_state_digest=d)
                for d in [SOURCE, other_source])
        assert isinstance(a, FailureReceipt) and isinstance(b, FailureReceipt)
        self.assertNotEqual(a.receipt_id, b.receipt_id)
        self.assertEqual(b.identity_payload.source_state_digest, other_source)
        # No live state exists here to determine which label is true. An
        # imported, rehashed stage is content-valid, not a causal trace.
        data = a.to_payload()
        assert isinstance(data["identity_payload"], dict)
        data["identity_payload"]["stage"] = "commit"
        data["receipt_id"] = payload_identity("failure_receipt_identity_payload",
                                               data["identity_payload"])
        imported = FailureReceipt.from_payload(data)
        self.assertEqual(imported.identity_payload.stage, "commit")
        self.assertEqual(imported.identity_payload.code, "invalid_duration")
        emitted = admit_step_request(request, source_state_digest=SOURCE)
        self.assertEqual(emitted, a)
        self.assertNotEqual(imported, emitted)

    def test_failure_vocabulary_matches_schema_not_executed_failure_modes(self) -> None:
        from pygrc.models.grc_v4_codec import load_contract_schema
        schema = cast(dict[str, Any], load_contract_schema())
        properties = schema["$defs"]["failure_receipt_identity_payload"]["properties"]
        self.assertEqual(set(get_args(OperationStage)), set(properties["stage"]["enum"]))
        self.assertEqual(set(get_args(FailureCode)), set(properties["code"]["enum"]))
        # Construction of a vocabulary member is not execution of that stage.
        for dt in [-5e-324, -1, -1e308]:
            result = admit_step_request(GRCV4StepRequestInput.from_payload(step_input(dt)),
                                        source_state_digest=SOURCE)
            assert isinstance(result, FailureReceipt)
            self.assertEqual((result.identity_payload.stage, result.identity_payload.code),
                             ("admission", "invalid_duration"))

    def test_rehashing_does_not_admit_nonatomic_failure_evidence(self) -> None:
        data = deepcopy(negative_vector()["expected"]["failure_receipt"])
        data["identity_payload"]["observed_poststate_digest"] = SOURCE
        data["receipt_id"] = payload_identity("failure_receipt_identity_payload",
                                               data["identity_payload"])
        routes: list[Callable[[dict[str, Any]], object]] = [
            FailureReceipt.from_payload, lambda v: FailureReceipt(**v)]
        for route in routes:
            with self.assertRaisesRegex(V4IdentityError, "prestate"):
                route(data)

    def test_failure_payload_nested_ownership_and_no_self_digest(self) -> None:
        result = admit_step_request(GRCV4StepRequestInput.from_payload(step_input(-1)),
                                    source_state_digest=SOURCE)
        assert isinstance(result, FailureReceipt)
        other = replace(result)
        self.assertIsNot(result.identity_payload, other.identity_payload)
        before = canonical_json_bytes(other.to_payload())
        object.__setattr__(result.identity_payload, "observed_poststate_digest",
                           "grcv4-state-sha256:" + "b" * 64)
        with self.assertRaises(V4IdentityError):
            replace(result)
        self.assertEqual(before, canonical_json_bytes(other.to_payload()))
        self.assertNotIn("receipt_id", other.identity_payload.to_payload())
        self.assertIs(type(other.identity_payload), FailureReceiptIdentityPayload)


if __name__ == "__main__":
    unittest.main()

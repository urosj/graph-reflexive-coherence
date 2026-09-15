"""Local admission and exact failure identities, not a complete beat test."""

from __future__ import annotations

from collections import UserList, UserString
from collections.abc import Callable, Iterator
from copy import deepcopy
from dataclasses import fields, is_dataclass, replace
from hashlib import sha256
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from typing import Any, cast, get_args
from types import MappingProxyType
import unittest
from unittest.mock import patch
import venv

from pygrc.models.grc_v4 import (
    GRCV4StepRequest,
    GRCV4StepRequestInput,
    decode_step_request_input,
)
from pygrc.models.grc_v4_codec import (
    V4IdentityError,
    V4SchemaError,
    V4WireError,
    canonical_json_bytes,
    payload_identity,
)
from pygrc.core.events import GRCEvent
from pygrc.models.grc_v4_state import FrozenJSONMap, GRCV4Event
from pygrc.models.grc_v4_step import (
    CommitPayload,
    CurrentSelection,
    FailureCode,
    FailureReceipt,
    FailureReceiptIdentityPayload,
    GRCV4Failure,
    OperationStage,
    ProvisionalResourceStep,
    ResourceBoundaryError,
    StepResultEvidence,
    SuccessfulReceiptEnvelope,
    admit_step_request,
    bind_step_result,
    make_commit_receipts,
    negative_duration_result,
)
from pygrc.models.grc_v4_state import GRCV4LifecycleResult, GRCV4StepResult
from pygrc.models.grc_v4_state import GRCV4AuthoritativeState, SolverDisposition
from pygrc.models.grc_v4_geometry import (
    GRCV4Graph,
    GeometryStage,
    GeometryStageCache,
    GeometryStageInputs,
    H_profile,
    K4Tensor,
    OneForm,
    OrientedEdge,
    PhysicalFlux,
)
from pygrc.models.grc_v4_profile import list_supported_profiles
from pygrc.models.grc_v4_transport import provisional_continuity
from tests.models.test_grc_v4_geometry import (
    stage_inputs_fixture,
    stage_reference_fixture,
)
from tests.models.test_grc_v4 import step_input
from tests.models.test_grc_v4_state import (
    fixture_id,
    result_fixture,
    successful_fixture,
)

SOURCE = "grcv4-state-sha256:" + "a" * 64


def negative_vector() -> dict[str, Any]:
    bundle = json.loads(
        (
            Path(__file__).resolve().parents[2]
            / "specs/grc-v4-conformance-vectors.json"
        ).read_text()
    )
    return next(
        v
        for v in bundle["atomic_failure_vectors"]
        if v["fixture_id"] == "COMMON-NEGATIVE-DURATION"
    )


class StepAdmissionTests(unittest.TestCase):
    def test_published_negative_duration_exact_receipt(self) -> None:
        vector = negative_vector()
        source = vector["expected"]["prestate_digest"]
        result = admit_step_request(
            decode_step_request_input(json.dumps(vector["request_input"])),
            source_state_digest=source,
        )
        self.assertIs(type(result), FailureReceipt)
        assert isinstance(result, FailureReceipt)
        self.assertEqual(result.to_payload(), vector["expected"]["failure_receipt"])
        # Independent stdlib calculation for this ASCII-only frozen preimage.
        raw = json.dumps(
            vector["expected"]["failure_receipt"]["identity_payload"],
            sort_keys=True,
            separators=(",", ":"),
        ).encode()
        self.assertEqual(
            result.receipt_id, "grc-receipt-sha256:" + sha256(raw).hexdigest()
        )

    def test_negative_duration_is_rejected_without_solver_or_ledger_authority(
        self,
    ) -> None:
        for dt in [-5e-324, -0.125, -1, -1e20]:
            value = GRCV4StepRequestInput.from_payload(step_input(dt))
            before = value.to_canonical_bytes()
            result = admit_step_request(value, source_state_digest=SOURCE)
            assert isinstance(result, FailureReceipt)
            self.assertEqual(result.identity_payload.stage, "admission")
            self.assertEqual(result.identity_payload.code, "invalid_duration")
            self.assertEqual(
                result.identity_payload.source_state_digest,
                result.identity_payload.observed_poststate_digest,
            )
            self.assertEqual(value.to_canonical_bytes(), before)
            for name in ["solver_disposition", "commit_id", "committed", "ledger"]:
                self.assertFalse(hasattr(result, name))

    def test_positive_and_zero_produce_strict_requests_not_executed_states(
        self,
    ) -> None:
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
            for name in [
                "committed",
                "admitted",
                "state",
                "solver_disposition",
                "commit_id",
                "ledger",
                "source_state_digest",
            ]:
                self.assertFalse(hasattr(result, name))

    def test_admission_detaches_input_even_after_unsupported_reinitialization(
        self,
    ) -> None:
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
            admit_step_request(
                GRCV4StepRequest.from_payload(data),  # type: ignore[arg-type]
                source_state_digest=SOURCE,
            )
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
                        admit_step_request(
                            GRCV4StepRequestInput.from_payload(step_input(dt)),
                            source_state_digest=digest,  # type: ignore[arg-type]
                        )

    def test_failure_envelope_reconstruction_checks_all_content_fields(self) -> None:
        result = admit_step_request(
            GRCV4StepRequestInput.from_payload(step_input(-1)),
            source_state_digest=SOURCE,
        )
        assert isinstance(result, FailureReceipt)
        self.assertEqual(FailureReceipt.from_payload(result.to_payload()), result)
        self.assertEqual(FailureReceipt(**result.to_payload()), result)  # type: ignore[arg-type]
        for mode in [
            "wrong_id",
            "bool_id",
            "extra",
            "wrong_operation",
            "stage",
            "source_newline",
        ]:
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
            with (
                self.subTest(mode=mode),
                self.assertRaises((V4SchemaError, V4IdentityError)),
            ):
                FailureReceipt.from_payload(data)

    def test_receipt_equality_does_not_identify_the_request(self) -> None:
        left = GRCV4StepRequestInput.from_payload(step_input(-1))
        data = step_input(-2)
        data["context_value"] = {"different": True}
        right = GRCV4StepRequestInput.from_payload(data)
        self.assertNotEqual(left.to_canonical_bytes(), right.to_canonical_bytes())
        a, b = (
            admit_step_request(q, source_state_digest=SOURCE) for q in [left, right]
        )
        assert isinstance(a, FailureReceipt) and isinstance(b, FailureReceipt)
        self.assertEqual(a, b)
        self.assertEqual(a.receipt_id, b.receipt_id)
        self.assertNotIn("dt", a.identity_payload.to_payload())
        self.assertNotIn("context_value", a.identity_payload.to_payload())

    def test_receipt_content_is_not_source_or_execution_authentication(self) -> None:
        request = GRCV4StepRequestInput.from_payload(step_input(-1))
        other_source = "grcv4-state-sha256:" + "b" * 64
        a, b = (
            admit_step_request(request, source_state_digest=d)
            for d in [SOURCE, other_source]
        )
        assert isinstance(a, FailureReceipt) and isinstance(b, FailureReceipt)
        self.assertNotEqual(a.receipt_id, b.receipt_id)
        self.assertEqual(b.identity_payload.source_state_digest, other_source)
        # No live state exists here to determine which label is true. An
        # imported, rehashed stage is content-valid, not a causal trace.
        data = a.to_payload()
        assert isinstance(data["identity_payload"], dict)
        data["identity_payload"]["stage"] = "commit"
        data["receipt_id"] = payload_identity(
            "failure_receipt_identity_payload", data["identity_payload"]
        )
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
        self.assertEqual(
            set(get_args(OperationStage)), set(properties["stage"]["enum"])
        )
        self.assertEqual(set(get_args(FailureCode)), set(properties["code"]["enum"]))
        # Construction of a vocabulary member is not execution of that stage.
        for dt in [-5e-324, -1, -1e308]:
            result = admit_step_request(
                GRCV4StepRequestInput.from_payload(step_input(dt)),
                source_state_digest=SOURCE,
            )
            assert isinstance(result, FailureReceipt)
            self.assertEqual(
                (result.identity_payload.stage, result.identity_payload.code),
                ("admission", "invalid_duration"),
            )

    def test_rehashing_does_not_admit_nonatomic_failure_evidence(self) -> None:
        data = deepcopy(negative_vector()["expected"]["failure_receipt"])
        data["identity_payload"]["observed_poststate_digest"] = SOURCE
        data["receipt_id"] = payload_identity(
            "failure_receipt_identity_payload", data["identity_payload"]
        )
        routes: list[Callable[[dict[str, Any]], object]] = [
            FailureReceipt.from_payload,
            lambda v: FailureReceipt(**v),
        ]
        for route in routes:
            with self.assertRaisesRegex(V4IdentityError, "prestate"):
                route(data)

    def test_failure_payload_nested_ownership_and_no_self_digest(self) -> None:
        result = admit_step_request(
            GRCV4StepRequestInput.from_payload(step_input(-1)),
            source_state_digest=SOURCE,
        )
        assert isinstance(result, FailureReceipt)
        other = replace(result)
        self.assertIsNot(result.identity_payload, other.identity_payload)
        before = canonical_json_bytes(other.to_payload())
        object.__setattr__(
            result.identity_payload,
            "observed_poststate_digest",
            "grcv4-state-sha256:" + "b" * 64,
        )
        with self.assertRaises(V4IdentityError):
            replace(result)
        self.assertEqual(before, canonical_json_bytes(other.to_payload()))
        self.assertNotIn("receipt_id", other.identity_payload.to_payload())
        self.assertIs(type(other.identity_payload), FailureReceiptIdentityPayload)


def scientific_fixture() -> dict[str, Any]:
    return {
        "schema_version": "grcv4-scientific-state-v1",
        "active_model_identity": "grcv4-profile-sha256:" + "1" * 64,
        "graph_digest": "grc-graph-sha256:" + "2" * 64,
        "orientation_identity": "tail-to-head",
        "step_index": 3,
        "time": 0.75,
        "authoritative": {"C": [1, 2], "W_A": None, "Z_4": None},
        "reset_digest": "grcv4-reset-sha256:" + "3" * 64,
        "Q_target": 3,
        "context_contract_id": "constant-zero",
        "context_value_digest": None,
    }


def positive_fixture() -> tuple[GRCV4StepResult, dict[str, Any]]:
    """Hand-computed transition example, not a candidate solve or runtime vector."""
    source = scientific_fixture()
    target = deepcopy(source)
    target.update(step_index=4, time=1)
    target["authoritative"]["C"] = [1.25, 1.75]
    payload = successful_fixture()["identity_payload"]
    core = payload["core"]
    for prefix, state in [("source", source), ("target", target)]:
        core[prefix + "_state_digest"] = fixture_id("grcv4-state-sha256", state)
        core[prefix + "_graph_digest"] = state["graph_digest"]
        core[prefix + "_model_identity"] = state["active_model_identity"]
        core[prefix + "_reset_digest"] = state["reset_digest"]
        core[prefix + "_authoritative_digest"] = fixture_id(
            "grcv4-authoritative-sha256",
            {
                "schema_version": "grcv4-authoritative-state-identity-v1",
                "authoritative": state["authoritative"],
            },
        )
    receipt_id = fixture_id("grc-receipt-sha256", payload)
    commit = {
        "schema_version": "grcv4-commit-payload-v1",
        "operation_id": "test:step",
        "source_state_digest": core["source_state_digest"],
        "target_state_digest": core["target_state_digest"],
        "emitted_receipt_ids": [receipt_id],
        "target_step_index": 4,
        "target_time": 1,
    }
    commit_id = fixture_id("grc-commit-sha256", commit)
    envelope = {
        "schema_version": "grcv4-successful-receipt-envelope-v1",
        "receipt_id": receipt_id,
        "commit_id": commit_id,
        "identity_payload": payload,
    }
    request = step_input(0.25) | {"operation_id": "test:step"}
    data = result_fixture() | {
        "step_index": 4,
        "time": 1,
        "events": [],
        "commit_id": commit_id,
        "emitted_receipts": [envelope],
    }
    prior = [successful_fixture()]
    return GRCV4StepResult(**data), {
        "request": GRCV4StepRequestInput.from_payload(request),
        "prestate": source,
        "poststate": target,
        "pre_ledger": prior,
        "post_ledger": prior + [deepcopy(envelope)],
        "observed_stage": "commit",
        "observed_code": None,
        "observed_solver": "valid_root",
        "commit_payload": commit,
    }


class ResultCompositionTests(unittest.TestCase):
    def published_results(self) -> list[dict[str, Any]]:
        return cast(
            list[dict[str, Any]],
            json.loads(
                (
                    Path(__file__).resolve().parents[2]
                    / "specs/grc-v4-conformance-vectors.json"
                ).read_text()
            )["step_result_vectors"],
        )

    def test_published_result_preimages_and_solver_operation_split(self) -> None:
        for row in self.published_results():
            data = row["result"]
            result = GRCV4StepResult.from_payload(data)
            self.assertEqual(result.to_payload(), data)
            self.assertEqual(result.to_canonical_bytes(), canonical_json_bytes(data))
            self.assertEqual(
                GRCV4StepResult.from_canonical_bytes(result.to_canonical_bytes()),
                result,
            )
            self.assertIsInstance(result.failure, GRCV4Failure)
            self.assertFalse(result.committed)
        before, after = (
            GRCV4StepResult.from_payload(r["result"]) for r in self.published_results()
        )
        self.assertIsNone(before.solver_disposition)
        self.assertEqual(after.solver_disposition, "valid_root")

    def test_direct_factory_and_canonical_reconstruction_share_validation(self) -> None:
        for row in self.published_results():
            data = deepcopy(row["result"])
            direct = dict(data)
            del direct["schema_version"]
            self.assertEqual(
                GRCV4StepResult(**direct), GRCV4StepResult.from_payload(data)
            )
            for mode in ["solver", "receipt", "lifecycle", "operation", "events"]:
                bad = deepcopy(data)
                if mode == "solver":
                    bad["solver_disposition"] = "singular"
                elif mode == "receipt":
                    bad["emitted_receipts"] = []
                elif mode == "lifecycle":
                    bad["failure"]["post_lifecycle_digest"] = (
                        "grcv4-lifecycle-sha256:" + "0" * 64
                    )
                elif mode == "operation":
                    bad["failure"]["failure_receipt"]["identity_payload"][
                        "operation_id"
                    ] = "other"
                else:
                    bad["events"] = [
                        {
                            "kind": "unexpected",
                            "step_index": 1,
                            "payload": {},
                            "source_family": "GRCV4",
                        }
                    ]
                with (
                    self.subTest(mode=mode),
                    self.assertRaises((V4SchemaError, V4IdentityError)),
                ):
                    GRCV4StepResult.from_payload(bad)

    def test_all_result_missing_extra_and_numeric_fields_reject(self) -> None:
        data = self.published_results()[0]["result"]
        for key in data:
            bad = deepcopy(data)
            del bad[key]
            with self.subTest(key=key), self.assertRaises(V4SchemaError):
                GRCV4StepResult.from_payload(bad)
        for key, bad_value in [
            ("extra", 1),
            ("time", True),
            ("step_index", True),
            ("step_index", 2**53),
            ("time", -0.0),
            ("time", float("nan")),
            ("active_profile_id", data["active_profile_id"] + "\n"),
        ]:
            with self.subTest(key=key), self.assertRaises((V4SchemaError, V4WireError)):
                GRCV4StepResult.from_payload(data | {key: bad_value})
        result = GRCV4StepResult.from_payload(data | {"step_index": 1.0})
        self.assertIs(type(result.step_index), int)

    def test_failure_nested_tampering_rehash_does_not_repair_detail(self) -> None:
        data = deepcopy(self.published_results()[0]["result"]["failure"])
        for field, replacement in [("stage", "commit"), ("code", "charge_failure")]:
            bad = deepcopy(data)
            payload = bad["failure_receipt"]["identity_payload"]
            payload[field] = replacement
            bad["failure_receipt"]["receipt_id"] = fixture_id(
                "grc-receipt-sha256", payload
            )
            with self.assertRaises(V4IdentityError):
                GRCV4Failure.from_payload(bad)

    def test_solver_failures_cannot_continue_or_be_relabelled_as_postsolve(
        self,
    ) -> None:
        codes = {
            "domain_failure": "domain_failure",
            "singular": "singular_solver",
            "conditioning_failure": "conditioning_failure",
            "nonfinite": "nonfinite_value",
            "no_admitted_root": "no_admitted_root",
            "multiple_admitted_roots": "multiple_admitted_roots",
        }
        for solver, code in codes.items():
            data = deepcopy(self.published_results()[0]["result"])
            failure = data["failure"]
            failure.update(
                stage="candidate_solve", code=code, solver_disposition=solver
            )
            payload = failure["failure_receipt"]["identity_payload"]
            payload.update(stage="candidate_solve", code=code)
            failure["failure_receipt"]["receipt_id"] = fixture_id(
                "grc-receipt-sha256", payload
            )
            data.update(
                solver_disposition=solver,
                emitted_receipts=[deepcopy(failure["failure_receipt"])],
            )
            result = GRCV4StepResult.from_payload(data)
            self.assertFalse(result.committed)
            with self.assertRaises(V4SchemaError):
                GRCV4StepResult.from_payload(data | {"committed": True})
            failure["solver_disposition"] = data["solver_disposition"] = "valid_root"
            with self.assertRaises(V4SchemaError):
                GRCV4StepResult.from_payload(data)

    def test_negative_duration_composes_result_with_real_payload_hashes(self) -> None:
        state = scientific_fixture()
        ledger = [successful_fixture()]
        before = canonical_json_bytes({"state": state, "ledger": ledger})
        for dt in [-5e-324, -1, -1e308]:
            request = GRCV4StepRequestInput.from_payload(step_input(dt))
            result, evidence = negative_duration_result(
                request,
                prestate=state,
                receipt_ledger=ledger,
                active_profile_id=state["active_model_identity"],
            )
            self.assertIsNone(result.solver_disposition)
            self.assertIsNone(result.commit_id)
            assert result.failure is not None
            self.assertEqual(
                result.failure.prestate_digest, fixture_id("grcv4-state-sha256", state)
            )
            self.assertEqual(evidence.request_bytes, request.to_canonical_bytes())
            self.assertEqual(evidence.prestate_bytes, evidence.poststate_bytes)
            self.assertEqual(evidence.pre_ledger_bytes, evidence.post_ledger_bytes)
            self.assertEqual(len(result.emitted_receipts), 1)
            self.assertEqual(
                canonical_json_bytes({"state": state, "ledger": ledger}), before
            )

    def test_zero_subnormal_and_extreme_requests_are_not_completed_by_prefix(
        self,
    ) -> None:
        for dt in [0, 5e-324, 1e308]:
            with (
                self.subTest(dt=dt),
                self.assertRaisesRegex(V4SchemaError, "full step"),
            ):
                negative_duration_result(
                    GRCV4StepRequestInput.from_payload(step_input(dt)),
                    prestate=scientific_fixture(),
                    receipt_ledger=[],
                    active_profile_id=scientific_fixture()["active_model_identity"],
                )

    def test_distinct_negative_requests_keep_distinct_evidence_when_receipts_match(
        self,
    ) -> None:
        results = [
            negative_duration_result(
                GRCV4StepRequestInput.from_payload(step_input(dt)),
                prestate=scientific_fixture(),
                receipt_ledger=[],
                active_profile_id=scientific_fixture()["active_model_identity"],
            )
            for dt in [-1, -2]
        ]
        self.assertEqual(results[0][0].emitted_receipts, results[1][0].emitted_receipts)
        self.assertNotEqual(results[0][1].request_bytes, results[1][1].request_bytes)

    def test_result_binding_rejects_wrong_state_foreign_operation_and_causal_labels(
        self,
    ) -> None:
        state = scientific_fixture()
        request = GRCV4StepRequestInput.from_payload(step_input(-1))
        result, _ = negative_duration_result(
            request,
            prestate=state,
            receipt_ledger=[],
            active_profile_id=state["active_model_identity"],
        )
        args: dict[str, Any] = {
            "request": request,
            "prestate": state,
            "poststate": state,
            "pre_ledger": [],
            "post_ledger": [],
            "observed_stage": "admission",
            "observed_code": "invalid_duration",
            "observed_solver": None,
        }
        changed = deepcopy(state)
        changed["authoritative"]["C"] = [2, 1]
        mutations: list[dict[str, Any]] = [
            {"prestate": changed},
            {"poststate": changed},
            {"prestate": changed, "poststate": changed},
            {
                "request": GRCV4StepRequestInput.from_payload(
                    step_input(-1) | {"operation_id": "other"}
                )
            },
            {"observed_stage": "commit"},
            {"observed_code": "charge_failure"},
            {"observed_solver": "valid_root"},
            {"post_ledger": result.emitted_receipts},
        ]
        for changes in mutations:
            with (
                self.subTest(changes=changes),
                self.assertRaises((V4IdentityError, V4SchemaError)),
            ):
                bind_step_result(result, **(args | changes))

    def test_postsolver_charge_rejection_retains_valid_root_with_no_ledger_append(
        self,
    ) -> None:
        state = scientific_fixture()
        request = GRCV4StepRequestInput.from_payload(step_input(0.25))
        result, _ = negative_duration_result(
            GRCV4StepRequestInput.from_payload(step_input(-1)),
            prestate=state,
            receipt_ledger=[],
            active_profile_id=state["active_model_identity"],
        )
        data = result.to_payload()
        failure = data["failure"]
        failure.update(
            stage="charge_admission",
            code="charge_failure",
            solver_disposition="valid_root",
        )
        payload = failure["failure_receipt"]["identity_payload"]
        payload.update(stage="charge_admission", code="charge_failure")
        failure["failure_receipt"]["receipt_id"] = fixture_id(
            "grc-receipt-sha256", payload
        )
        data.update(
            solver_disposition="valid_root",
            emitted_receipts=[deepcopy(failure["failure_receipt"])],
        )
        result = GRCV4StepResult.from_payload(data)
        evidence = bind_step_result(
            result,
            request=request,
            prestate=state,
            poststate=state,
            pre_ledger=[],
            post_ledger=[],
            observed_stage="charge_admission",
            observed_code="charge_failure",
            observed_solver="valid_root",
        )
        self.assertEqual(evidence.pre_ledger_bytes, b"[]")
        self.assertEqual(evidence.post_ledger_bytes, b"[]")
        self.assertFalse(result.committed)

    def test_receipt_commit_then_envelope_order_matches_independent_preimages(
        self,
    ) -> None:
        result, args = positive_fixture()
        expected = args["commit_payload"]
        commit, receipts = make_commit_receipts(
            [r.to_payload()["identity_payload"] for r in result.emitted_receipts],
            operation_id=expected["operation_id"],
            source_state_digest=expected["source_state_digest"],
            target_state_digest=expected["target_state_digest"],
            target_step_index=4,
            target_time=1,
        )
        self.assertEqual(commit.to_payload(), expected)
        self.assertEqual(receipts, result.emitted_receipts)
        self.assertNotIn("commit_id", commit.to_payload())
        self.assertNotIn("receipt_id", receipts[0].identity_payload)
        evidence = bind_step_result(result, **args)
        self.assertNotEqual(evidence.prestate_bytes, evidence.poststate_bytes)
        self.assertEqual(len(json.loads(evidence.pre_ledger_bytes)), 1)
        self.assertEqual(len(json.loads(evidence.post_ledger_bytes)), 2)

    def test_commit_payload_counts_and_receipt_sequence_are_not_mutably_aliased(
        self,
    ) -> None:
        _, args = positive_fixture()
        data = args["commit_payload"]
        data["target_step_index"] = 4.0
        value = CommitPayload.from_payload(data)
        self.assertIs(type(value.target_step_index), int)
        before = value.to_payload()
        data["emitted_receipt_ids"].clear()
        self.assertEqual(value.to_payload(), before)
        for number in [True, 1.5, float(2**53)]:
            with self.assertRaises(V4SchemaError):
                CommitPayload.from_payload(before | {"target_step_index": number})

    def test_committed_result_cannot_include_failures_or_foreign_envelopes(
        self,
    ) -> None:
        result, _ = positive_fixture()
        for mode in ["empty", "commit", "failure", "foreign_kind"]:
            data = result.to_payload()
            if mode == "empty":
                data["emitted_receipts"] = []
            elif mode == "commit":
                data["emitted_receipts"][0]["commit_id"] = (
                    "grc-commit-sha256:" + "f" * 64
                )
            elif mode == "failure":
                data["emitted_receipts"] = self.published_results()[0]["result"][
                    "emitted_receipts"
                ]
            else:
                p = data["emitted_receipts"][0]["identity_payload"]
                p.update(
                    schema_version="grcv4-reset-receipt-v1",
                    reset_baseline_digest="grcv4-reset-sha256:" + "1" * 64,
                )
                data["emitted_receipts"][0]["receipt_id"] = fixture_id(
                    "grc-receipt-sha256", p
                )
            with (
                self.subTest(mode=mode),
                self.assertRaises((V4IdentityError, V4SchemaError)),
            ):
                GRCV4StepResult.from_payload(data)

    def test_recomputed_commit_does_not_repair_wrong_receipt_state_binding(
        self,
    ) -> None:
        result, args = positive_fixture()
        for field in [
            "source_graph_digest",
            "target_model_identity",
            "source_authoritative_digest",
            "target_reset_digest",
        ]:
            data = result.to_payload()
            receipt = data["emitted_receipts"][0]
            core = receipt["identity_payload"]["core"]
            core[field] = core[field].split(":")[0] + ":" + "f" * 64
            receipt["receipt_id"] = fixture_id(
                "grc-receipt-sha256", receipt["identity_payload"]
            )
            commit = deepcopy(args["commit_payload"])
            commit["emitted_receipt_ids"] = [receipt["receipt_id"]]
            data["commit_id"] = receipt["commit_id"] = fixture_id(
                "grc-commit-sha256", commit
            )
            altered = GRCV4StepResult.from_payload(data)
            with self.subTest(field=field), self.assertRaises(V4IdentityError):
                bind_step_result(
                    altered,
                    **(
                        args
                        | {
                            "post_ledger": args["pre_ledger"] + [receipt],
                            "commit_payload": commit,
                        }
                    ),
                )

    def test_ledger_prefix_delta_and_commit_links_checked_both_directions(self) -> None:
        result, args = positive_fixture()
        for changes in [
            {"post_ledger": args["pre_ledger"]},
            {"post_ledger": args["post_ledger"][::-1]},
            {"post_ledger": args["post_ledger"] * 2},
            {"commit_payload": None},
            {"commit_payload": args["commit_payload"] | {"emitted_receipt_ids": []}},
        ]:
            with (
                self.subTest(changes=changes),
                self.assertRaises((V4IdentityError, V4SchemaError)),
            ):
                bind_step_result(result, **(args | changes))

    def test_events_bind_delta_receipt_graph_profile_clock_and_commit(self) -> None:
        result, args = positive_fixture()
        data = result.to_payload()
        receipt = data["emitted_receipts"][0]
        core = receipt["identity_payload"]["core"]
        payload = {
            k: core[k]
            for k in [
                "source_graph_digest",
                "target_graph_digest",
                "source_model_identity",
                "target_model_identity",
            ]
        }
        payload.update(
            receipt_id=receipt["receipt_id"],
            commit_id=receipt["commit_id"],
            source_profile_id=result.active_profile_id,
            target_profile_id=result.active_profile_id,
        )
        event = {
            "kind": "step",
            "step_index": result.step_index,
            "payload": payload,
            "source_family": "GRCV4",
        }
        data["events"] = [event]
        value = GRCV4StepResult.from_payload(data)
        bind_step_result(value, **args)
        for field in payload:
            bad = deepcopy(data)
            del bad["events"][0]["payload"][field]
            with self.subTest(field=field), self.assertRaises(V4IdentityError):
                bind_step_result(GRCV4StepResult.from_payload(bad), **args)
        value.events[0].payload.clear()
        self.assertEqual(value.to_payload(), data)

    def test_lifecycle_result_has_no_invented_solver_or_persistent_failure_receipt(
        self,
    ) -> None:
        data = self.published_results()[0]["result"]
        body = {
            k: data[k]
            for k in [
                "operation_disposition",
                "committed",
                "commit_id",
                "failure",
                "emitted_receipts",
            ]
        }
        value = GRCV4LifecycleResult.from_payload(body)
        self.assertEqual(value.to_payload(), body)
        self.assertFalse(hasattr(value, "solver_disposition"))
        with self.assertRaises(V4SchemaError):
            GRCV4LifecycleResult.from_payload(body | {"solver_disposition": None})
        bad = deepcopy(body)
        bad["failure"]["solver_disposition"] = "valid_root"
        with self.assertRaises(V4SchemaError):
            GRCV4LifecycleResult.from_payload(bad)

    def test_boolean_number_payload_equality_and_projection_ownership(self) -> None:
        result, _ = positive_fixture()
        a = result.to_payload()
        b = deepcopy(a)
        a["observables"] = {"flag": True}
        b["observables"] = {"flag": 1}
        left, right = GRCV4StepResult.from_payload(a), GRCV4StepResult.from_payload(b)
        self.assertNotEqual(left, right)
        self.assertEqual(len({left, right}), 2)
        projected = left.to_payload()
        projected["observables"].clear()
        projected["emitted_receipts"][0]["identity_payload"]["core"][
            "parent_receipt_ids"
        ].append("bad")
        self.assertEqual(left.to_payload(), a)

    def test_imported_typed_records_revalidated_before_consumption(self) -> None:
        result, args = positive_fixture()
        receipt = result.emitted_receipts[0]
        self.assertIsInstance(receipt, SuccessfulReceiptEnvelope)
        object.__setattr__(receipt, "receipt_id", "grc-receipt-sha256:" + "0" * 64)
        with self.assertRaises(V4IdentityError):
            bind_step_result(result, **args)

    def test_failure_compares_full_ledger_even_when_receipt_ids_match(self) -> None:
        state = scientific_fixture()
        prior = [successful_fixture()]
        request = GRCV4StepRequestInput.from_payload(step_input(-1))
        result, _ = negative_duration_result(
            request,
            prestate=state,
            receipt_ledger=prior,
            active_profile_id=state["active_model_identity"],
        )
        changed = deepcopy(prior)
        changed[0]["commit_id"] = "grc-commit-sha256:" + "f" * 64
        self.assertEqual(changed[0]["receipt_id"], prior[0]["receipt_id"])
        with self.assertRaisesRegex(V4IdentityError, "persistent ledger"):
            bind_step_result(
                result,
                request=request,
                prestate=state,
                poststate=state,
                pre_ledger=prior,
                post_ledger=changed,
                observed_stage="admission",
                observed_code="invalid_duration",
                observed_solver=None,
            )

    def test_specialization_profile_cannot_be_inferred_from_model_label(self) -> None:
        state = scientific_fixture()
        state["active_model_identity"] = "grc9v4-model-sha256:" + "1" * 64
        with self.assertRaisesRegex(V4SchemaError, "specialization"):
            negative_duration_result(
                GRCV4StepRequestInput.from_payload(step_input(-1)),
                prestate=state,
                receipt_ledger=[],
                active_profile_id="grcv4-profile-sha256:" + "2" * 64,
            )

    def test_multi_receipt_order_and_information_loss_order_are_identity_bearing(
        self,
    ) -> None:
        result, args = positive_fixture()
        step = result.emitted_receipts[0].to_payload()["identity_payload"]
        charge = deepcopy(step)
        assert isinstance(charge, dict)
        charge.update(
            schema_version="grcv4-charge-receipt-v1",
            target_charge=3,
            admitted_charge=3,
            residual=0,
        )
        commit_args = {
            k: args["commit_payload"][k]
            for k in [
                "operation_id",
                "source_state_digest",
                "target_state_digest",
                "target_step_index",
                "target_time",
            ]
        }
        commit, receipts = make_commit_receipts([step, charge], **commit_args)
        reversed_commit, _ = make_commit_receipts([charge, step], **commit_args)
        self.assertNotEqual(
            payload_identity("commit_payload", commit.to_payload()),
            payload_identity("commit_payload", reversed_commit.to_payload()),
        )
        data = result.to_payload()
        data.update(
            commit_id=receipts[0].commit_id,
            emitted_receipts=[r.to_payload() for r in receipts],
        )
        updated_args = args | {
            "commit_payload": commit.to_payload(),
            "post_ledger": args["pre_ledger"] + data["emitted_receipts"],
        }
        bind_step_result(GRCV4StepResult.from_payload(data), **updated_args)
        data["emitted_receipts"].reverse()
        with self.assertRaises(V4IdentityError):
            bind_step_result(GRCV4StepResult.from_payload(data), **updated_args)
        for losses in [
            ["none"],
            ["candidate_history_loss", "candidate_history_loss"],
            ["carrier_history_loss", "candidate_history_loss"],
        ]:
            bad = deepcopy(step)
            assert isinstance(bad, dict) and isinstance(bad["core"], dict)
            cast(dict[str, Any], bad["core"])["information_losses"] = losses
            with self.assertRaises(V4SchemaError):
                make_commit_receipts([bad], **commit_args)


class AuditBoundaryTests(unittest.TestCase):
    """P924 F1/F2 regressions and explicit composition-only characterizations."""

    def result_payloads(self) -> list[dict[str, Any]]:
        positive, _ = positive_fixture()
        negative, _ = negative_duration_result(
            GRCV4StepRequestInput.from_payload(step_input(-1)),
            prestate=scientific_fixture(),
            receipt_ledger=[],
            active_profile_id=scientific_fixture()["active_model_identity"],
        )
        return [positive.to_payload(), negative.to_payload()]

    def direct(self, data: dict[str, Any]) -> GRCV4StepResult:
        values = dict(data)
        del values["schema_version"]
        return GRCV4StepResult(**values)

    def test_original_index_numbers_reject_before_normalization(self) -> None:
        bad = [
            -0.0,
            True,
            False,
            1.5,
            -1,
            -1.0,
            2**53,
            2**53 + 1,
            float(2**53),
            math.nextafter(float(2**53), math.inf),
            float("nan"),
            float("inf"),
            float("-inf"),
            "4",
            None,
        ]
        for data in self.result_payloads():
            for value in bad:
                for construct in (self.direct, GRCV4StepResult.from_payload):
                    with self.subTest(
                        status=data["committed"], value=value, route=construct.__name__
                    ):
                        with self.assertRaises((TypeError, ValueError)):
                            construct(data | {"step_index": value})
                # A primitive decoder must also see, not erase, the bad spelling.
                with self.assertRaises((TypeError, ValueError)):
                    GRCV4StepResult.from_canonical_bytes(
                        json.dumps(
                            data | {"step_index": value},
                            separators=(",", ":"),
                            sort_keys=True,
                        )
                    )

    def test_legal_integral_indices_keep_canonical_identity(self) -> None:
        for data in self.result_payloads():
            for value in [0, 0.0, 4, 4.0, 2**53 - 1, float(2**53 - 1)]:
                expected = canonical_json_bytes(data | {"step_index": int(value)})
                for construct in (self.direct, GRCV4StepResult.from_payload):
                    with self.subTest(
                        status=data["committed"], value=value, route=construct.__name__
                    ):
                        result = construct(data | {"step_index": value})
                        self.assertIs(type(result.step_index), int)
                        self.assertEqual(result.to_canonical_bytes(), expected)
                        self.assertEqual(
                            GRCV4StepResult.from_canonical_bytes(expected), result
                        )

    def test_real_time_is_not_restricted_to_safe_integer_domain(self) -> None:
        for data in self.result_payloads():
            for value in [0.0, 0.25, 1e20, float.fromhex("0x1.fffffffffffffp+1023")]:
                for construct in (self.direct, GRCV4StepResult.from_payload):
                    self.assertEqual(construct(data | {"time": value}).time, value)

    def test_unordered_and_raw_event_containers_reject(self) -> None:
        event = GRCV4Event("step", 4, FrozenJSONMap({"n": 1}), "GRCV4")
        for data in self.result_payloads():
            for value in [
                {},
                set(),
                frozenset(),
                "",
                b"",
                bytearray(),
                memoryview(b""),
                UserString(""),
                {event: "discarded"},
                {event},
                frozenset([event]),
                "event",
                b"event",
                bytearray(b"event"),
                memoryview(b"event"),
            ]:
                with self.subTest(
                    status=data["committed"], container=type(value).__name__
                ):
                    with self.assertRaises(TypeError):
                        self.direct(data | {"events": value})

    def test_event_iterators_reject_without_consumption(self) -> None:
        consumed: list[bool] = []

        def events() -> Iterator[GRCEvent]:
            consumed.append(True)
            yield GRCEvent("step", 4, {})

        for data in self.result_payloads():
            iterator = events()
            with self.assertRaises(TypeError):
                self.direct(data | {"events": iterator})
            self.assertEqual(consumed, [])
            iterator.close()  # type: ignore[attr-defined]

    def test_ordered_event_sequences_preserve_order_and_detach(self) -> None:
        data = self.result_payloads()[0]
        for sequence in (list, tuple, UserList):
            first = GRCEvent("first", 4, {"nested": [1]})
            second = GRCV4Event("second", 4, FrozenJSONMap({"nested": [2]}))
            events = sequence([second, first])
            result = self.direct(data | {"events": events})
            before = result.to_canonical_bytes()
            first.payload["nested"].append(9)
            result.events[1].payload["nested"].clear()
            if isinstance(events, (list, UserList)):
                events.clear()
            self.assertEqual([e.kind for e in result.events], ["second", "first"])
            self.assertEqual(result.to_canonical_bytes(), before)
            self.assertEqual(GRCV4StepResult.from_payload(result.to_payload()), result)
        for data in self.result_payloads():
            for sequence in (list, tuple, UserList):
                self.assertEqual(self.direct(data | {"events": sequence()}).events, ())

    def test_primitive_event_input_cannot_smuggle_an_outer_adapter(self) -> None:
        for data in self.result_payloads():
            for value in [{}, set(), "", b"", bytearray(), memoryview(b""), iter(())]:
                with self.subTest(container=type(value).__name__):
                    with self.assertRaises((TypeError, ValueError)):
                        GRCV4StepResult.from_payload(data | {"events": value})

    def test_builder_commit_binds_in_typed_and_primitive_forms(self) -> None:
        result, args = positive_fixture()
        expected = args["commit_payload"]
        commit, receipts = make_commit_receipts(
            [r.to_payload()["identity_payload"] for r in result.emitted_receipts],
            **{
                k: expected[k]
                for k in (
                    "operation_id",
                    "source_state_digest",
                    "target_state_digest",
                    "target_step_index",
                    "target_time",
                )
            },
        )
        self.assertEqual(receipts, result.emitted_receipts)
        primitive = bind_step_result(
            result, **(args | {"commit_payload": commit.to_payload()})
        )
        typed = bind_step_result(result, **(args | {"commit_payload": commit}))
        self.assertEqual(typed, primitive)
        for field, value in [
            ("operation_id", "foreign"),
            ("target_step_index", -0.0),
            ("emitted_receipt_ids", ()),
        ]:
            forged = CommitPayload.from_payload(expected)
            object.__setattr__(forged, field, value)
            with self.assertRaises((TypeError, ValueError)):
                bind_step_result(result, **(args | {"commit_payload": forged}))

    def test_direct_evidence_requires_exact_bytes_without_granting_authority(
        self,
    ) -> None:
        values = {
            f.name: b"arbitrary, unvalidated bytes" for f in fields(StepResultEvidence)
        }
        self.assertEqual(StepResultEvidence(**values), StepResultEvidence(**values))
        for field in values:
            for value in [bytearray(b"x"), memoryview(b"x"), "x", None, 1]:
                with self.subTest(field=field, value=type(value).__name__):
                    with self.assertRaises(TypeError):
                        StepResultEvidence(**cast(Any, values | {field: value}))
        result, args = positive_fixture()
        evidence = bind_step_result(result, **args)
        self.assertTrue(
            all(type(getattr(evidence, f.name)) is bytes for f in fields(evidence))
        )

    def test_parent_references_are_content_not_lineage_certification(self) -> None:
        # Characterization, not an oracle accepting these parents as real lineage.
        # Parent scope/order must be settled by P9-7.6 before lineage conformance.
        result, args = positive_fixture()
        data = result.to_payload()
        for parents in [
            [],
            ["grc-receipt-sha256:" + "f" * 64],
            [args["pre_ledger"][0]["receipt_id"]],
        ]:
            payload = deepcopy(data["emitted_receipts"][0]["identity_payload"])
            payload["core"]["parent_receipt_ids"] = parents
            receipt_id = fixture_id("grc-receipt-sha256", payload)
            commit = args["commit_payload"] | {"emitted_receipt_ids": [receipt_id]}
            commit_id = fixture_id("grc-commit-sha256", commit)
            envelope = data["emitted_receipts"][0] | {
                "identity_payload": payload,
                "receipt_id": receipt_id,
                "commit_id": commit_id,
            }
            built, receipts = make_commit_receipts(
                [payload],
                **{
                    k: commit[k]
                    for k in (
                        "operation_id",
                        "source_state_digest",
                        "target_state_digest",
                        "target_step_index",
                        "target_time",
                    )
                },
            )
            self.assertEqual(built.to_payload(), commit)
            self.assertEqual(receipts[0].to_payload(), envelope)
            composed = GRCV4StepResult.from_payload(
                data | {"commit_id": commit_id, "emitted_receipts": [envelope]}
            )
            evidence = bind_step_result(
                composed,
                **(
                    args
                    | {
                        "commit_payload": commit,
                        "post_ledger": args["pre_ledger"] + [envelope],
                    }
                ),
            )
            self.assertEqual(
                json.loads(evidence.result_bytes)["emitted_receipts"][0][
                    "identity_payload"
                ]["core"]["parent_receipt_ids"],
                parents,
            )
            with self.assertRaises(V4IdentityError):
                SuccessfulReceiptEnvelope.from_payload(
                    envelope | {"receipt_id": "grc-receipt-sha256:" + "e" * 64}
                )
        for invalid_parents in [
            [True],
            ["not-a-receipt"],
            {"parent": "grc-receipt-sha256:" + "f" * 64},
        ]:
            bad = deepcopy(data["emitted_receipts"][0])
            bad["identity_payload"]["core"]["parent_receipt_ids"] = invalid_parents
            with self.assertRaises((TypeError, ValueError)):
                SuccessfulReceiptEnvelope.from_payload(bad)

    def test_consistent_records_do_not_prove_a_numerical_transition(self) -> None:
        # Carry these as later live-step oracle negatives, not new passing step vectors.
        result, args = positive_fixture()
        for name, changes, dt in [
            ("wrong_elapsed_time", {"time": 99}, 0.25),
            ("unchanged_index", {"step_index": 3}, 0.25),
            ("backward_clock", {"time": 0.25, "step_index": 2}, 0.25),
            ("zero_dt_changed_state", {}, 0.0),
        ]:
            with self.subTest(case=name):
                target = deepcopy(args["poststate"])
                target.update(changes)
                payload = result.emitted_receipts[0].to_payload()["identity_payload"]
                assert isinstance(payload, dict) and isinstance(payload["core"], dict)
                payload["core"]["target_state_digest"] = fixture_id(
                    "grcv4-state-sha256", target
                )
                receipt_id = fixture_id("grc-receipt-sha256", payload)
                commit = args["commit_payload"] | {
                    "target_state_digest": payload["core"]["target_state_digest"],
                    "target_step_index": target["step_index"],
                    "target_time": target["time"],
                    "emitted_receipt_ids": [receipt_id],
                }
                commit_id = fixture_id("grc-commit-sha256", commit)
                envelope = result.emitted_receipts[0].to_payload() | {
                    "identity_payload": payload,
                    "receipt_id": receipt_id,
                    "commit_id": commit_id,
                }
                content = GRCV4StepResult.from_payload(
                    result.to_payload()
                    | {
                        "step_index": target["step_index"],
                        "time": target["time"],
                        "commit_id": commit_id,
                        "emitted_receipts": [envelope],
                    }
                )
                request = GRCV4StepRequestInput.from_payload(
                    args["request"].to_payload() | {"dt": dt}
                )
                evidence = bind_step_result(
                    content,
                    **(
                        args
                        | {
                            "request": request,
                            "poststate": target,
                            "commit_payload": commit,
                            "post_ledger": args["pre_ledger"] + [envelope],
                        }
                    ),
                )
                self.assertEqual(json.loads(evidence.poststate_bytes), target)


# P9-3.3: supplied current results, not candidate/root or full-step fixtures.


def resource_selection(
    before: GeometryStageInputs, values: tuple[float, ...] = (1.0, 0.5)
) -> CurrentSelection:
    stages = {
        "OS": "os_corrector",
        "CI": "ci_trial",
        "PC": "pc_old_history",
        "CI+PC": "cipc_trial",
        "RG2b": "rg2b_section",
    }
    flux = PhysicalFlux(before.geometry.reference.graph, values)
    stage = stages[before.geometry.reference.profile.identity_payload.realization]
    geometry = before.geometry
    if stage == "pc_old_history":
        ref = geometry.reference
        n = len(ref.graph.oriented_edges)
        history = before.current.Z_4
        assert history is not None
        increment = tuple(tuple(history[i * n : (i + 1) * n]) for i in range(n))
        geometry = H_profile(
            K4Tensor(ref.graph, ref.K4_base, increment),
            reference=ref,
            profile=ref.profile,
            context=ref.context,
        )
    chosen = replace(
        before,
        stage=cast(GeometryStage, stage),
        geometry=geometry,
        trial_current=flux if stage in ("ci_trial", "cipc_trial") else None,
    )
    return CurrentSelection(chosen, "valid_root", flux)


def resource_replay_input() -> dict[str, Any]:
    before = stage_inputs_fixture()
    return {
        "prestate": before.to_payload(),
        "selection": resource_selection(before).to_payload(),
    }


def reconstruct_resource(data: dict[str, Any]) -> dict[str, Any]:
    """Recompute from full portable inputs; no fixture or cached output is read."""
    if set(data) != {"prestate", "selection"}:
        raise ValueError("resource replay requires only the full operation inputs")
    before = GeometryStageInputs.from_payload(data["prestate"])
    selected = (
        None
        if data["selection"] is None
        else CurrentSelection.from_payload(data["selection"])
    )
    result = ProvisionalResourceStep(before, selected)
    result.consume(expected_prestate=before, expected_selection=selected)
    return result.to_payload()


def preservation_snapshot(value: Any) -> tuple[Any, ...]:
    """Independent observation of values AND sharing; not a scientific hash.

    Traverse actual containers/record fields, never their serializers. Preserve
    float bits, container types/order, aliases and cycles, including malformed
    inputs which the scientific codec must reject. No process-local IDs escape.
    This observer makes no claim about an unavailable live lifecycle owner.
    """
    import struct

    seen: dict[int, int] = {}

    def freeze(item: Any) -> tuple[Any, ...]:
        kind = type(item)
        if kind in (type(None), bool, int, str, bytes):
            return (kind.__name__, item)
        if kind is float:
            return ("float64", struct.pack("!d", item))
        if id(item) in seen:
            return ("alias", seen[id(item)])
        seen[id(item)] = len(seen)
        if kind in (dict, MappingProxyType):
            return (
                kind.__name__,
                tuple((freeze(k), freeze(v)) for k, v in item.items()),
            )
        if kind in (list, tuple):
            return (kind.__name__, tuple(freeze(v) for v in item))
        if is_dataclass(item) and not isinstance(item, type):
            return (
                kind.__module__,
                kind.__qualname__,
                tuple((f.name, freeze(getattr(item, f.name))) for f in fields(item)),
            )
        raise TypeError("unobserved preservation type: " + kind.__qualname__)

    return freeze(value)


def preservation_fixture(candidate: str, realization: str) -> GeometryStageInputs:
    """Unequal live/reset coordinates, nonzero histories, clocks and ledger.

    Ten typed declarations exercise ownership shapes, not runtime support.
    Both C sums are exactly 18; all history matrices are strictly positive.
    """
    base = stage_inputs_fixture(stage_reference_fixture(candidate, realization))
    return replace(
        base,
        current=GRCV4AuthoritativeState(
            (8.0, 6.0, 4.0),
            (2.0, 5.0) if candidate == "A" else None,
            (0.25, 0.0, 0.0, 0.5) if realization in ("PC", "CI+PC") else None,
        ),
        reset=GRCV4AuthoritativeState(
            (4.0, 8.0, 6.0),
            (3.0, 7.0) if candidate == "A" else None,
            (0.75, 0.0, 0.0, 0.25) if realization in ("PC", "CI+PC") else None,
        ),
        Q_target=18.0,
        dt=0.25,
        time=0.75,
        step_index=3,
        receipt_ids=tuple(r["receipt_id"] for r in preservation_ledger()),
    )


def preservation_ledger() -> list[dict[str, Any]]:
    """Two distinct content-valid envelopes; no invented lineage validation."""
    first, second = successful_fixture(), successful_fixture()
    second["identity_payload"]["core"]["operation_id"] = "test:second-step"
    second["receipt_id"] = fixture_id("grc-receipt-sha256", second["identity_payload"])
    return [first, second]


class PrestatePreservationTests(unittest.TestCase):
    """P9-3.5: executed local boundaries, plus explicit observer controls."""

    def test_capture_requires_each_reviewed_preservation_method(self) -> None:
        from tests.models.test_grc_v4_geometry import _p934_coverage

        required = p935_required(Path(__file__).resolve().parents[2])
        names = sorted(required)
        rows = [{"test": n, "status": "passed"} for n in names]
        self.assertTrue(_p934_coverage(required, names, rows)["passed"])
        own = next(i for i, n in enumerate(names) if ".PrestatePreservationTests." in n)
        self.assertFalse(
            _p934_coverage(required, names[:own] + names[own + 1 :], rows)["passed"]
        )
        self.assertFalse(_p934_coverage(required, names + [names[own]], rows)["passed"])
        for status in (
            "started",
            "failed",
            "error",
            "skipped",
            "expected_failure",
            "unexpected_success",
        ):
            bad = deepcopy(rows)
            bad[own]["status"] = status
            self.assertFalse(_p934_coverage(required, names, bad)["passed"])

    def rejected(
        self,
        invoke: Callable[[], Any],
        captured: Any,
        error: type[Exception] | tuple[type[Exception], ...],
        *,
        outcome: tuple[str, str] | None = None,
        repeats: int = 2,
    ) -> Exception:
        entry = preservation_snapshot(captured)
        caught_error: Exception | None = None
        diagnostics: list[tuple[Any, ...]] = []
        retained: list[Any] = []
        for attempt in range(repeats):
            try:
                with self.assertRaises(error) as caught:
                    invoke()
                caught_error = caught.exception
                if outcome is not None:
                    self.assertIsInstance(caught_error, ResourceBoundaryError)
                    assert isinstance(caught_error, ResourceBoundaryError)
                    self.assertEqual((caught_error.stage, caught_error.code), outcome)
                    diagnostic = caught_error.charge
                    diagnostics.append(preservation_snapshot(diagnostic))
                    retained.append(diagnostic)
                    self.assertTrue(all(d == diagnostics[0] for d in diagnostics))
                    for original, snapshot in zip(retained, diagnostics, strict=True):
                        self.assertEqual(preservation_snapshot(original), snapshot)
            finally:
                self.assertEqual(preservation_snapshot(captured), entry, attempt)
        assert caught_error is not None
        return caught_error

    def test_observer_detects_each_coordinate_alias_type_and_cycle_change(self) -> None:
        import struct

        before = preservation_fixture("A", "CI+PC")
        raw = before.to_payload()

        # Every payload scalar is independently perturbed: resources alone,
        # claimed digest labels, and shared before/after pointers cannot suffice.
        def leaves(value: Any, path: tuple[Any, ...] = ()) -> Iterator[tuple[Any, ...]]:
            if isinstance(value, dict):
                for key, child in value.items():
                    yield from leaves(child, (*path, key))
            elif isinstance(value, list):
                for index, child in enumerate(value):
                    yield from leaves(child, (*path, index))
            else:
                yield path

        snapshot = preservation_snapshot(raw)
        paths = list(leaves(raw))
        self.assertGreater(len(paths), 100)
        for path in paths:
            changed = deepcopy(raw)
            parent: Any = changed
            for key in path[:-1]:
                parent = parent[key]
            parent[path[-1]] = {"observer_control": True}
            self.assertNotEqual(preservation_snapshot(changed), snapshot, path)
        shared: list[Any] = [1.0]
        self.assertNotEqual(
            preservation_snapshot([shared, shared]),
            preservation_snapshot([shared, list(shared)]),
        )
        for a, b in ((True, 1), (1, 1.0), (0.0, -0.0), ([1], (1,))):
            self.assertNotEqual(preservation_snapshot(a), preservation_snapshot(b))
        backing = {"nested": [1.0]}
        proxy = MappingProxyType(backing)
        observed = preservation_snapshot(proxy)
        self.assertNotEqual(observed, preservation_snapshot(backing))
        backing["nested"][0] = 2.0
        self.assertNotEqual(observed, preservation_snapshot(proxy))
        shared.append(shared)
        cyclic = preservation_snapshot(shared)
        shared[0] = 2.0
        self.assertNotEqual(preservation_snapshot(shared), cyclic)

        # Observe both argument roots together; splitting and merging equal
        # mutable storage must each differ from that attempt's own baseline.
        left, right = [1.0], [1.0]
        roots = [left, right]
        separate = preservation_snapshot(roots)
        roots[1] = left
        merged = preservation_snapshot(roots)
        self.assertNotEqual(merged, separate)
        roots[1] = right
        self.assertNotEqual(preservation_snapshot(roots), merged)
        self.assertEqual(preservation_snapshot(roots), separate)

        # Malformed floating values still have observable bits. Repeated
        # observation must neither canonicalize them nor consume input.
        patterns = ("7ff8000000000001", "7ff8000000000002", "fff8000000000001")
        nans = [struct.unpack("!d", bytes.fromhex(bits))[0] for bits in patterns]
        self.assertTrue(all(math.isnan(value) for value in nans))
        self.assertEqual(len({preservation_snapshot(value) for value in nans}), 3)
        raw_graph = [proxy, shared, nans, roots]
        saved = preservation_snapshot(raw_graph)
        for _ in range(3):
            self.assertEqual(preservation_snapshot(raw_graph), saved)
        self.assertEqual(
            [struct.pack("!d", value).hex() for value in nans], list(patterns)
        )

        def detached(value: Any) -> None:
            self.assertIn(type(value), (tuple, type(None), bool, int, str, bytes))
            if type(value) is tuple:
                for child in value:
                    detached(child)

        detached(saved)
        iterator = iter(["first", "second"])
        with self.assertRaisesRegex(TypeError, "unobserved preservation type"):
            preservation_snapshot(iterator)
        self.assertEqual(next(iterator), "first")
        self.assertEqual(preservation_snapshot(raw_graph), saved)

    def test_all_failed_dispositions_preserve_ten_full_prestates_and_selection(
        self,
    ) -> None:
        codes: dict[str, str] = {
            "domain_failure": "domain_failure",
            "singular": "singular_solver",
            "conditioning_failure": "conditioning_failure",
            "nonfinite": "nonfinite_value",
            "no_admitted_root": "no_admitted_root",
            "multiple_admitted_roots": "multiple_admitted_roots",
        }
        self.assertEqual(set(codes), set(get_args(SolverDisposition)) - {"valid_root"})
        for candidate in ("A", "C"):
            for realization in ("OS", "CI", "PC", "CI+PC", "RG2b"):
                before = preservation_fixture(candidate, realization)
                valid = resource_selection(before)
                for disposition, code in codes.items():
                    for current in (None, valid.current):
                        with self.subTest(
                            candidate=candidate,
                            realization=realization,
                            disposition=disposition,
                            current=current is not None,
                        ):
                            selected = replace(
                                valid,
                                solver_disposition=cast(SolverDisposition, disposition),
                                current=current,
                            )
                            with patch(
                                "pygrc.models.grc_v4_step.provisional_continuity",
                                side_effect=AssertionError(
                                    "failed solve reached continuity"
                                ),
                            ):
                                self.rejected(
                                    lambda: ProvisionalResourceStep(before, selected),
                                    (before, selected, valid),
                                    ResourceBoundaryError,
                                    outcome=("candidate_solve", code),
                                )
                result = ProvisionalResourceStep(before, valid)
                self.assertEqual(result.provisional_state.C, (7.75, 6.125, 4.125))
                self.assertEqual(result.continuity_evaluations, 1)

    def test_admission_and_missing_selection_preserve_both_histories(self) -> None:
        for candidate in ("A", "C"):
            for realization in ("OS", "CI", "PC", "CI+PC", "RG2b"):
                before = preservation_fixture(candidate, realization)
                valid = resource_selection(before)
                for field in ("current", "reset"):
                    # Nonnegative typed state is constructible but its sum is
                    # wrong. Negative raw state rejects before operation creation.
                    for resource, code in (((4.0, 8.0, 7.0), "charge_failure"),):
                        with self.subTest(
                            candidate=candidate,
                            realization=realization,
                            field=field,
                            code=code,
                        ):
                            bad = replace(
                                before,
                                **{field: replace(getattr(before, field), C=resource)},
                            )
                            self.rejected(
                                lambda: ProvisionalResourceStep(bad, valid),
                                (before, bad, valid),
                                ResourceBoundaryError,
                                outcome=("admission", code),
                            )
                    raw_negative = {
                        "C": [-1.0, 9.0, 10.0],
                        "W_A": getattr(before, field).W_A,
                        "Z_4": getattr(before, field).Z_4,
                    }
                    self.rejected(
                        lambda: GRCV4AuthoritativeState(**raw_negative),
                        (before, valid, raw_negative),
                        ValueError,
                    )
                self.rejected(
                    lambda: ProvisionalResourceStep(before, None), before, TypeError
                )
                zero = replace(before, dt=0.0)
                self.rejected(
                    lambda: ProvisionalResourceStep(zero, valid),
                    (before, zero, valid),
                    ResourceBoundaryError,
                    outcome=("admission", "domain_failure"),
                )
                identity = ProvisionalResourceStep(zero, None)
                self.assertEqual(identity.provisional_state, before.current)
                self.assertEqual(identity.continuity_evaluations, 0)

    def test_stale_selection_preserves_request_reference_history_and_order(
        self,
    ) -> None:
        before = preservation_fixture("A", "CI+PC")
        valid = resource_selection(before)
        variants: dict[str, Any] = {
            "operation_id": "different-attempt",
            "dt": 0.5,
            "time": 1.0,
            "step_index": 4,
            "Q_target": 19.0,
            "current": replace(before.current, W_A=(2.0, 6.0)),
            "reset": replace(before.reset, Z_4=(0.5, 0.0, 0.0, 0.25)),
            "receipt_ids": tuple(reversed(before.receipt_ids)),
            "stage": "post_continuity",
            "trial_current": PhysicalFlux(before.geometry.reference.graph, (0.0, 0.0)),
        }
        for name, value in variants.items():
            with self.subTest(field=name):
                selected = replace(valid, inputs=replace(valid.inputs, **{name: value}))
                self.rejected(
                    lambda: ProvisionalResourceStep(before, selected),
                    (before, valid, selected),
                    ResourceBoundaryError,
                    outcome=("candidate_solve", "stale_cache"),
                )
        bad_stage = replace(before, stage="post_continuity")
        self.rejected(
            lambda: ProvisionalResourceStep(bad_stage, valid),
            (before, bad_stage, valid),
            ResourceBoundaryError,
            outcome=("admission", "stale_cache"),
        )

    def test_late_resource_failures_preserve_inputs_and_detach_charge_diagnostics(
        self,
    ) -> None:
        for candidate in ("A", "C"):
            for realization in ("OS", "CI", "PC", "CI+PC", "RG2b"):
                before = preservation_fixture(candidate, realization)
                for duration, flux, stage, code in (
                    (1.0, (9.0, 0.0), "charge_admission", "domain_failure"),
                    (1e308, (2.0, 0.0), "continuity", "nonfinite_value"),
                ):
                    bad = replace(before, dt=duration)
                    selected = resource_selection(bad, flux)
                    self.rejected(
                        lambda: ProvisionalResourceStep(bad, selected),
                        (before, bad, selected),
                        ResourceBoundaryError,
                        outcome=(stage, code),
                    )
                    zero = resource_selection(bad, (0.0, 0.0))
                    retry_entry = preservation_snapshot((before, bad, zero))
                    try:
                        recovery = ProvisionalResourceStep(bad, zero)
                    finally:
                        self.assertEqual(
                            preservation_snapshot((before, bad, zero)), retry_entry
                        )
                    self.assertEqual(recovery.provisional_state, before.current)
                    self.assertEqual(recovery.continuity_evaluations, 1)
                    self.assertTrue(recovery.charge.admitted)
        # Exact transfer conserves charge; the declared binary64 tree increases
        # its result by two. This is an actual late charge gate, not an injection.
        graph = GRCV4Graph(("a", "b", "c", "d"), (OrientedEdge("ad", "a", "d"),))
        base = stage_inputs_fixture(
            stage_reference_fixture(
                graph=graph,
                changes={
                    "charge": {"absolute_tolerance": 0.0, "relative_tolerance": 0.0}
                },
            )
        )
        state = replace(base.current, C=(float(2**53), 1.0, 1.0, 1.0))
        bad = replace(base, current=state, reset=state, Q_target=float(2**53 + 2))
        selected = resource_selection(bad, (1.0,))
        error = self.rejected(
            lambda: ProvisionalResourceStep(bad, selected),
            (bad, selected),
            ResourceBoundaryError,
            outcome=("charge_admission", "charge_failure"),
        )
        assert isinstance(error, ResourceBoundaryError) and error.charge is not None
        diagnostic = error.charge.receipt_values()
        saved = preservation_snapshot((bad, selected, error.charge))
        diagnostic["residual"] = 0.0
        self.assertEqual(error.charge.residual, 2.0)
        self.assertEqual(preservation_snapshot((bad, selected, error.charge)), saved)
        # Retry from the same captured authority with a genuinely new current.
        self.assertEqual(
            ProvisionalResourceStep(
                bad, resource_selection(bad, (0.0,))
            ).provisional_state,
            state,
        )

    def test_consumption_rejection_preserves_cache_and_independent_expectations(
        self,
    ) -> None:
        before = preservation_fixture("A", "CI+PC")
        selected = resource_selection(before)
        provisional = ProvisionalResourceStep(before, selected)
        flux = PhysicalFlux(before.geometry.reference.graph, (1.0, 0.5))
        cache = GeometryStageCache(before, "flat", flux)
        foreign = replace(before, receipt_ids=tuple(reversed(before.receipt_ids)))
        self.rejected(
            lambda: provisional.consume(
                expected_prestate=foreign, expected_selection=selected
            ),
            (provisional, before, foreign, selected, cache),
            ResourceBoundaryError,
            outcome=("final_reconstruction", "stale_cache"),
        )
        self.rejected(
            lambda: provisional.consume(
                expected_prestate=before, expected_selection=None
            ),
            (provisional, before, selected, cache),
            ResourceBoundaryError,
            outcome=("final_reconstruction", "stale_cache"),
        )
        self.rejected(
            lambda: cache.consume(
                expected_inputs=foreign, expected_kind="flat", expected_operand=flux
            ),
            (cache, foreign, before, flux, provisional),
            ValueError,
        )
        self.assertEqual(
            provisional.consume(expected_prestate=before, expected_selection=selected),
            provisional.provisional_state,
        )
        self.assertEqual(
            cache.consume(
                expected_inputs=before, expected_kind="flat", expected_operand=flux
            ),
            cache.value,
        )

    def test_reconstruction_rejection_preserves_raw_nested_aliases_and_live_records(
        self,
    ) -> None:
        before = preservation_fixture("A", "CI+PC")
        selected = resource_selection(before)
        raw = selected.to_payload()
        # Shared caller arrays are legal inputs; the reconstructed records detach.
        raw["inputs"]["reset"]["W_A"] = raw["inputs"]["current"]["W_A"]
        # Claimed identities are now stale. Rejection must not repair these inputs.
        self.rejected(
            lambda: CurrentSelection.from_payload(raw),
            (raw, before, selected),
            ValueError,
        )
        for field, value in (
            ("solver_disposition", "fallback"),
            ("current", [math.inf, 0.0]),
            ("current", [True, 0.0]),
        ):
            malformed = selected.to_payload() | {field: value}
            self.rejected(
                lambda: CurrentSelection.from_payload(malformed),
                (malformed, before, selected),
                (TypeError, ValueError),
            )
        restored = CurrentSelection.from_payload(selected.to_payload())
        entry = preservation_snapshot((before, selected, restored))
        exposed = restored.to_payload()
        exposed["inputs"]["current"]["C"][0] = -999.0
        exposed["inputs"]["reset"]["Z_4"][0] = 999.0
        exposed["inputs"]["receipt_ids"].reverse()
        exposed["current"][0] = 1e308
        self.rejected(
            lambda: CurrentSelection.from_payload(exposed),
            (exposed, before, selected, restored),
            ValueError,
        )
        self.assertEqual(preservation_snapshot((before, selected, restored)), entry)
        self.assertEqual(
            ProvisionalResourceStep(before, restored).provisional_state.C,
            (7.75, 6.125, 4.125),
        )

    def test_malformed_wire_rejection_preserves_cyclic_and_shared_input(self) -> None:
        for value in (True, "-1", -0.0, math.nan, math.inf, 2**53):
            raw = step_input(-1) | {"dt": value}
            self.rejected(
                lambda: GRCV4StepRequestInput.from_payload(raw),
                raw,
                (V4WireError, V4SchemaError),
            )
        shared: list[Any] = [1, {"nested": [2]}]
        raw = step_input(-1) | {"context_value": {"first": shared, "second": shared}}
        request = GRCV4StepRequestInput.from_payload(raw)
        entry = preservation_snapshot(request)
        shared.append(shared)
        self.rejected(
            lambda: GRCV4StepRequestInput.from_payload(raw), (raw, request), V4WireError
        )
        proxy = MappingProxyType(raw)
        self.rejected(
            lambda: GRCV4StepRequestInput.from_payload(proxy),
            (proxy, raw, shared, request),
            V4WireError,
        )
        self.assertEqual(preservation_snapshot(request), entry)

    def test_negative_attempts_preserve_full_payload_and_result_isolation(self) -> None:
        stage = preservation_fixture("A", "CI+PC")
        state = cast(dict[str, Any], stage.scientific_state_preimage)
        ledger = preservation_ledger()
        self.assertEqual(stage.receipt_ids, tuple(r["receipt_id"] for r in ledger))
        raw = step_input(-1) | {"context_value": {"nested": [1, {"flag": True}]}}
        request = GRCV4StepRequestInput.from_payload(raw)
        captured = (stage, state, ledger, raw, request)
        entry = preservation_snapshot(captured)
        results = []
        for dt in (-5e-324, -1.0, -1e308):
            expected_raw = deepcopy(raw) | {"dt": dt}
            req = GRCV4StepRequestInput.from_payload(expected_raw)
            request_entry = preservation_snapshot(req)
            self.assertEqual(req.dt, dt)
            self.assertEqual(req.operation_id, raw["operation_id"])
            try:
                result, evidence = negative_duration_result(
                    req,
                    prestate=state,
                    receipt_ledger=ledger,
                    active_profile_id=state["active_model_identity"],
                )
            finally:
                self.assertEqual(preservation_snapshot(req), request_entry)
            self.assertEqual(preservation_snapshot(captured), entry)
            self.assertEqual(json.loads(evidence.request_bytes), expected_raw)
            self.assertEqual(
                preservation_snapshot(
                    json.loads(evidence.request_bytes)["context_value"]
                ),
                preservation_snapshot(expected_raw["context_value"]),
            )
            self.assertEqual(json.loads(evidence.request_bytes)["dt"], dt)
            self.assertEqual(
                json.loads(evidence.request_bytes)["context_value"],
                raw["context_value"],
            )
            self.assertEqual(evidence.prestate_bytes, evidence.poststate_bytes)
            self.assertEqual(evidence.pre_ledger_bytes, evidence.post_ledger_bytes)
            self.assertEqual(evidence.request_bytes, req.to_canonical_bytes())
            results.append((result, evidence))
        saved = preservation_snapshot(results)
        state["authoritative"]["C"][0] = 99.0
        ledger.clear()
        raw["context_value"]["nested"][1]["flag"] = False
        results[0][0].to_payload()["emitted_receipts"].clear()
        self.assertEqual(preservation_snapshot(results), saved)
        self.assertEqual(len({e.request_bytes for _, e in results}), 3)
        self.assertEqual(len({e.result_bytes for _, e in results}), 1)

    def test_binding_detects_full_state_changes_without_mutating_either_observation(
        self,
    ) -> None:
        stage = preservation_fixture("A", "CI+PC")
        state = cast(dict[str, Any], stage.scientific_state_preimage)
        request = GRCV4StepRequestInput.from_payload(step_input(-1))
        ledger = preservation_ledger()
        result, _ = negative_duration_result(
            request,
            prestate=state,
            receipt_ledger=ledger,
            active_profile_id=state["active_model_identity"],
        )
        changes = {
            "Q_target": 19.0,
            "time": 1.0,
            "step_index": 4,
            "reset_digest": "grcv4-reset-sha256:" + "4" * 64,
            "graph_digest": "grc-graph-sha256:" + "4" * 64,
            "context_value_digest": "grcv4-context-sha256:" + "4" * 64,
            "authoritative": state["authoritative"] | {"W_A": [2.0, 6.0]},
        }
        for field, value in changes.items():
            changed = deepcopy(state) | {field: value}
            self.assertEqual(changed["authoritative"]["C"], state["authoritative"]["C"])
            self.rejected(
                lambda: bind_step_result(
                    result,
                    request=request,
                    prestate=state,
                    poststate=changed,
                    pre_ledger=ledger,
                    post_ledger=ledger,
                    observed_stage="admission",
                    observed_code="invalid_duration",
                    observed_solver=None,
                ),
                (state, changed, ledger, result, request),
                (V4SchemaError, V4IdentityError),
            )
        appended = [*ledger, result.emitted_receipts[0].to_payload()]
        self.rejected(
            lambda: bind_step_result(
                result,
                request=request,
                prestate=state,
                poststate=state,
                pre_ledger=ledger,
                post_ledger=appended,
                observed_stage="admission",
                observed_code="invalid_duration",
                observed_solver=None,
            ),
            (state, ledger, appended, result, request),
            V4SchemaError,
        )
        for after in (
            list(reversed(ledger)),
            [ledger[0], ledger[0]],
            [*ledger, ledger[1]],
        ):
            self.rejected(
                lambda: bind_step_result(
                    result,
                    request=request,
                    prestate=state,
                    poststate=state,
                    pre_ledger=ledger,
                    post_ledger=after,
                    observed_stage="admission",
                    observed_code="invalid_duration",
                    observed_solver=None,
                ),
                (state, ledger, after, result, request),
                V4IdentityError,
            )
        detached = deepcopy(ledger)
        entry = preservation_snapshot((state, ledger, detached, result, request))
        bind_step_result(
            result,
            request=request,
            prestate=state,
            poststate=deepcopy(state),
            pre_ledger=ledger,
            post_ledger=detached,
            observed_stage="admission",
            observed_code="invalid_duration",
            observed_solver=None,
        )
        self.assertEqual(
            preservation_snapshot((state, ledger, detached, result, request)), entry
        )

    def test_independent_observer_exposes_mutating_and_lying_serializers(self) -> None:
        raw = step_input(-1) | {"context_value": {"token": "original"}}
        state = scientific_fixture()
        request = GRCV4StepRequestInput.from_payload(raw)
        original = GRCV4StepRequestInput.to_payload
        entry = preservation_snapshot(request)

        def mutating(value: GRCV4StepRequestInput) -> dict[str, Any]:
            data = original(value)
            object.__setattr__(value, "dt", -2.0)
            return data

        with patch.object(GRCV4StepRequestInput, "to_payload", mutating):
            negative_duration_result(
                request,
                prestate=state,
                receipt_ledger=[],
                active_profile_id=state["active_model_identity"],
            )
        self.assertNotEqual(preservation_snapshot(request), entry)
        request = GRCV4StepRequestInput.from_payload(raw)
        entry = preservation_snapshot(request)

        def lying(value: GRCV4StepRequestInput) -> dict[str, Any]:
            return original(value) | {"context_value": {"token": "foreign"}}

        with patch.object(GRCV4StepRequestInput, "to_payload", lying):
            _, evidence = negative_duration_result(
                request,
                prestate=state,
                receipt_ledger=[],
                active_profile_id=state["active_model_identity"],
            )
            # The production serializer agrees with its own wrong observation.
            self.assertEqual(evidence.request_bytes, request.to_canonical_bytes())
        self.assertEqual(preservation_snapshot(request), entry)
        # The independently held caller expectation exposes the false evidence.
        self.assertNotEqual(
            json.loads(evidence.request_bytes)["context_value"], raw["context_value"]
        )

    def test_harness_catches_nonresource_reset_ledger_and_exception_mutations(
        self,
    ) -> None:
        from tests.models.grcv4_conformance_harness import Fixture, run_negative
        from tests.models.grcv4_reference_oracles import prefix_fixture

        fixture = Fixture.from_payload(prefix_fixture())
        self.assertTrue(run_negative(fixture)["passed"])

        def mutation(which: str) -> Callable[..., GRCV4StepResult]:
            def invoke(
                req: GRCV4StepRequestInput, subject: dict[str, Any]
            ) -> GRCV4StepResult:
                result, _ = negative_duration_result(
                    req,
                    prestate=subject["state"],
                    receipt_ledger=subject["ledger"],
                    active_profile_id=subject["state"]["active_model_identity"],
                )
                if which == "ledger":
                    subject["ledger"].append(result.emitted_receipts[0].to_payload())
                elif which == "reset":
                    subject["reset"]["authoritative"]["C"].reverse()
                    subject["reset"]["authoritative"]["C"][0] += 1
                else:
                    subject["state"]["time"] += 0.25
                    if which == "raise":
                        raise RuntimeError("controlled mutation before exception")
                return result

            return invoke

        for which in ("ledger", "reset", "clock", "raise"):
            with self.subTest(control=which):
                actual = run_negative(fixture, operation=mutation(which))
                self.assertFalse(actual["passed"])
        self.assertTrue(run_negative(fixture)["passed"])


class ResourceBoundaryTests(unittest.TestCase):
    def test_zero_rounded_residual_can_hide_exact_stored_sum_growth(self) -> None:
        from fractions import Fraction

        # Pair with test_conservative_real_transfer_can_fail_the_binary64_charge_gate.
        # Neither implication between exact conservation and gate admission holds.
        for magnitude, duration in ((float(2**53), 0.5), (1e20, 1.0)):
            for vertices in (("rich", "small"), ("small", "rich")):
                for reversed_edge in (False, True):
                    with self.subTest(
                        magnitude=magnitude,
                        vertices=vertices,
                        reversed_edge=reversed_edge,
                    ):
                        tail, head = (
                            ("small", "rich") if reversed_edge else ("rich", "small")
                        )
                        graph = GRCV4Graph(vertices, (OrientedEdge("e", tail, head),))
                        ref = stage_reference_fixture(
                            graph=graph,
                            changes={
                                "charge": {
                                    "absolute_tolerance": 0.0,
                                    "relative_tolerance": 0.0,
                                }
                            },
                        )
                        base = stage_inputs_fixture(ref)
                        state = replace(
                            base.current,
                            C=tuple(
                                magnitude if v == "rich" else 0.0 for v in vertices
                            ),
                        )
                        before = replace(
                            base,
                            current=state,
                            reset=state,
                            Q_target=magnitude,
                            dt=duration,
                        )
                        selected = resource_selection(
                            before, (-1.0 if reversed_edge else 1.0,)
                        )
                        result = ProvisionalResourceStep(before, selected)
                        expected = tuple(
                            magnitude if v == "rich" else duration for v in vertices
                        )
                        self.assertEqual(result.provisional_state.C, expected)
                        self.assertEqual(
                            sum(map(Fraction, expected)) - sum(map(Fraction, state.C)),
                            Fraction(duration),
                        )
                        self.assertTrue(result.charge.admitted)
                        self.assertEqual(
                            (result.charge.actual, result.charge.residual),
                            (magnitude, 0.0),
                        )
                        self.assertIsNone(result.charge.remainder)
                        self.assertEqual(result.continuity_evaluations, 1)

    def test_distinct_live_reset_resources_and_histories_across_ten_declarations(
        self,
    ) -> None:
        for candidate in ("A", "C"):
            for realization in ("OS", "CI", "PC", "CI+PC", "RG2b"):
                with self.subTest(candidate=candidate, realization=realization):
                    base = stage_inputs_fixture(
                        stage_reference_fixture(candidate, realization)
                    )
                    live = GRCV4AuthoritativeState(
                        (8.0, 6.0, 4.0),
                        (2.0, 5.0) if candidate == "A" else None,
                        (0.25, 0.0, 0.0, 0.5)
                        if realization in ("PC", "CI+PC")
                        else None,
                    )
                    reset = GRCV4AuthoritativeState(
                        (4.0, 8.0, 6.0),
                        (3.0, 7.0) if candidate == "A" else None,
                        (0.75, 0.0, 0.0, 0.25)
                        if realization in ("PC", "CI+PC")
                        else None,
                    )
                    before = replace(
                        base, current=live, reset=reset, Q_target=18.0, dt=0.25
                    )
                    selected = resource_selection(before)
                    original = canonical_json_bytes(before.to_payload())
                    selected_original = canonical_json_bytes(selected.to_payload())
                    with patch(
                        "pygrc.models.grc_v4_step.provisional_continuity",
                        wraps=provisional_continuity,
                    ) as write:
                        result = ProvisionalResourceStep(before, selected)
                        for _ in range(3):
                            value = result.consume(
                                expected_prestate=before, expected_selection=selected
                            )
                            self.assertEqual(value.C, (7.75, 6.125, 4.125))
                            self.assertEqual(
                                (value.W_A, value.Z_4), (live.W_A, live.Z_4)
                            )
                        self.assertEqual(write.call_count, 1)
                    self.assertEqual(
                        canonical_json_bytes(before.to_payload()), original
                    )
                    self.assertEqual(
                        canonical_json_bytes(selected.to_payload()), selected_original
                    )
                    self.assertEqual(result.charge.actual, 18.0)

    def test_cycle_circulation_with_same_resource_cannot_borrow_selection(self) -> None:
        graph = GRCV4Graph(
            ("a", "b", "c"),
            (
                OrientedEdge("ab", "a", "b"),
                OrientedEdge("bc", "b", "c"),
                OrientedEdge("ca", "c", "a"),
            ),
        )
        before = stage_inputs_fixture(stage_reference_fixture(graph=graph))
        zero = resource_selection(before, (0.0,) * 3)
        cycle = resource_selection(before, (3.0,) * 3)
        first = ProvisionalResourceStep(before, zero)
        second = ProvisionalResourceStep(before, cycle)
        self.assertEqual(first.provisional_state, second.provisional_state)
        self.assertEqual(first.charge.receipt_values(), second.charge.receipt_values())
        self.assertNotEqual(
            canonical_json_bytes(first.to_payload()),
            canonical_json_bytes(second.to_payload()),
        )
        for result, foreign in ((first, cycle), (second, zero)):
            with self.assertRaises(ResourceBoundaryError) as caught:
                result.consume(expected_prestate=before, expected_selection=foreign)
            self.assertEqual(
                (caught.exception.stage, caught.exception.code),
                ("final_reconstruction", "stale_cache"),
            )

    def test_exact_zero_divergence_can_overflow_before_cancellation(self) -> None:
        from fractions import Fraction

        graph = GRCV4Graph(
            ("a", "b"), tuple(OrientedEdge(f"e{i}", "a", "b") for i in range(4))
        )
        base = stage_inputs_fixture(stage_reference_fixture(graph=graph))
        state = replace(base.current, C=(4.0, 4.0))
        before = replace(base, current=state, reset=state, Q_target=8.0)
        # Exact scatter is zero in every order. The accepted native aggregation
        # still has a finite-intermediate envelope; no compensating fallback.
        for values, overflows in (
            ((1e308, 1e308, -1e308, -1e308), True),
            ((-1e308, -1e308, 1e308, 1e308), True),
            ((1e308, -1e308, 1e308, -1e308), False),
            ((-1e308, 1e308, -1e308, 1e308), False),
        ):
            with self.subTest(values=values):
                self.assertEqual(sum(map(Fraction, values)), 0)
                selected = resource_selection(before, values)
                if overflows:
                    self.assert_rejection(
                        before, selected, "continuity", "nonfinite_value", evaluations=1
                    )
                else:
                    result = ProvisionalResourceStep(before, selected)
                    self.assertEqual(result.provisional_state, state)
                    self.assertEqual(result.charge.residual, 0.0)

    def assert_rejection(
        self,
        before: GeometryStageInputs,
        chosen: CurrentSelection | None,
        stage: str,
        code: str,
        *,
        evaluations: int = 0,
    ) -> ResourceBoundaryError:
        original = preservation_snapshot((before, chosen))
        with patch(
            "pygrc.models.grc_v4_step.provisional_continuity",
            wraps=provisional_continuity,
        ) as write:
            with self.assertRaises(ResourceBoundaryError) as caught:
                ProvisionalResourceStep(before, chosen)
            self.assertEqual(write.call_count, evaluations)
        self.assertEqual((caught.exception.stage, caught.exception.code), (stage, code))
        self.assertEqual(preservation_snapshot((before, chosen)), original)
        return caught.exception

    def test_ten_declarations_write_once_preserve_nonresource_authority(self) -> None:
        for candidate in ("A", "C"):
            for realization in ("OS", "CI", "PC", "CI+PC", "RG2b"):
                with self.subTest(candidate=candidate, realization=realization):
                    before = stage_inputs_fixture(
                        stage_reference_fixture(candidate, realization)
                    )
                    selected = resource_selection(before)
                    original = canonical_json_bytes(before.to_payload())
                    with patch(
                        "pygrc.models.grc_v4_step.provisional_continuity",
                        wraps=provisional_continuity,
                    ) as write:
                        result = ProvisionalResourceStep(before, selected)
                        self.assertEqual(write.call_count, 1)
                    self.assertEqual(result.provisional_state.C, (0, 2.5, 3.5))
                    self.assertEqual(result.provisional_state.W_A, before.current.W_A)
                    self.assertEqual(result.provisional_state.Z_4, before.current.Z_4)
                    self.assertEqual(result.continuity_evaluations, 1)
                    self.assertEqual(
                        result.charge.receipt_values(),
                        {
                            "target_charge": 6.0,
                            "admitted_charge": 6.0,
                            "residual": 0.0,
                        },
                    )
                    self.assertIsNone(result.charge.remainder)
                    self.assertEqual(
                        canonical_json_bytes(before.to_payload()), original
                    )
                    self.assertEqual(
                        result.consume(
                            expected_prestate=before, expected_selection=selected
                        ),
                        result.provisional_state,
                    )
        self.assertEqual(list_supported_profiles(), frozenset({'grcv4-profile-sha256:a6b853ee382895eb78b1a7955a0df22f95d68b27cb0f762503e8c424c2f59b6d', 'grcv4-profile-sha256:e4c04a83240a33d77c50a26ca6effbb6ce142774bd01f0966861dd517a94e2c4', 'grcv4-profile-sha256:16ed65f7f65d4716e1be3e384f6fa0f957d26dd7b7a3f7e1b43ad1aa3f250946', 'grcv4-profile-sha256:a56ef981821478cc50a3551a914dd6240e0dc62c9ca69d52305bd59a3405f69e', 'grcv4-profile-sha256:058ae6b1f923c85952ffdfa083af74e3b56dd450f309190f307c3ea56ac2aa75', 'grcv4-profile-sha256:6105daf6f5111fdc51640194298b1b8398d608684791050d85b696bcd681f64f', 'grcv4-profile-sha256:5f2f848af0f482699ac6cb88e4e1bd1a66458774bac2c3cc6df9f74cc47d7689', 'grcv4-profile-sha256:3a7a084788c59a55b4232fb98e9c5529c1aa4c7c71074c9d3288982fa2fd2a5b', 'grcv4-profile-sha256:12abb2946bfaa616df2a42bd571732e2be3000736f5078d45f8dbf53682b212b', 'grcv4-profile-sha256:413497bec4f219ec402d82d5cd2aced01dca25a58d2ab906c348472b98d596b0'}))

    def test_every_failed_solver_disposition_blocks_fallback_before_continuity(
        self,
    ) -> None:
        before = stage_inputs_fixture()
        chosen = resource_selection(before)
        codes = {
            "domain_failure": "domain_failure",
            "singular": "singular_solver",
            "conditioning_failure": "conditioning_failure",
            "nonfinite": "nonfinite_value",
            "no_admitted_root": "no_admitted_root",
            "multiple_admitted_roots": "multiple_admitted_roots",
        }
        self.assertEqual(set(codes), set(get_args(SolverDisposition)) - {"valid_root"})
        for disposition, code in codes.items():
            for current in (None, chosen.current):
                self.assert_rejection(
                    before,
                    replace(
                        chosen,
                        solver_disposition=cast(SolverDisposition, disposition),
                        current=current,
                    ),
                    "candidate_solve",
                    code,
                )
        self.assert_rejection(
            before, replace(chosen, current=None), "candidate_solve", "domain_failure"
        )

    def test_predictor_and_postcontinuity_cannot_supply_selected_current(self) -> None:
        before = stage_inputs_fixture()
        chosen = resource_selection(before)
        for stage in ("os_predictor", "post_continuity", "pre_read"):
            self.assert_rejection(
                before,
                replace(chosen, inputs=replace(before, stage=stage)),
                "candidate_solve",
                "stale_cache",
            )
        self.assert_rejection(
            replace(before, stage="os_corrector"), chosen, "admission", "stale_cache"
        )

    def test_full_prestate_clock_reset_ledger_and_request_are_bound(self) -> None:
        before = stage_inputs_fixture()
        chosen = resource_selection(before)
        foreign_state = GRCV4AuthoritativeState((2.0, 1.0, 3.0), None, None)
        variations: dict[str, Any] = {
            "operation_id": "foreign",
            "dt": 0.5,
            "time": 0.5,
            "step_index": 1,
            "Q_target": 7.0,
            "current": foreign_state,
            "reset": foreign_state,
            "receipt_ids": ("grc-receipt-sha256:" + "1" * 64,),
        }
        for name, value in variations.items():
            with self.subTest(field=name):
                self.assert_rejection(
                    before,
                    replace(chosen, inputs=replace(chosen.inputs, **{name: value})),
                    "candidate_solve",
                    "stale_cache",
                )
        ref = stage_reference_fixture(gain=1.0)
        foreign = resource_selection(stage_inputs_fixture(ref))
        self.assert_rejection(before, foreign, "candidate_solve", "stale_cache")

    def test_corrected_hodge_is_allowed_with_same_reference_and_authority(self) -> None:
        before = stage_inputs_fixture()
        ref = before.geometry.reference
        geometry = H_profile(
            K4Tensor(ref.graph, ref.K4_base, ((1.0, 0.0), (0.0, 1.0))),
            reference=ref,
            profile=ref.profile,
            context=ref.context,
        )
        chosen = resource_selection(before)
        corrected = replace(chosen, inputs=replace(chosen.inputs, geometry=geometry))
        self.assertNotEqual(corrected.inputs.geometry, before.geometry)
        self.assertEqual(
            ProvisionalResourceStep(before, corrected).provisional_state.C,
            (0, 2.5, 3.5),
        )

    def test_joint_selection_must_equal_exact_bound_trial(self) -> None:
        for realization in ("CI", "CI+PC"):
            before = stage_inputs_fixture(
                stage_reference_fixture(realization=realization)
            )
            chosen = resource_selection(before)
            changed = PhysicalFlux(before.geometry.reference.graph, (1.0, 0.25))
            self.assert_rejection(
                before,
                replace(chosen, current=changed),
                "candidate_solve",
                "stale_cache",
            )

    def test_prestate_and_reset_charge_gate_precedes_current_consumption(self) -> None:
        before = stage_inputs_fixture()
        chosen = resource_selection(before)
        self.assert_rejection(
            replace(before, Q_target=7.0), chosen, "admission", "charge_failure"
        )
        reset = replace(before.reset, C=(1.0, 2.0, 4.0))
        self.assert_rejection(
            replace(before, reset=reset), chosen, "admission", "charge_failure"
        )
        overflow = replace(before.current, C=(1e308, 1e308, 0.0))
        self.assert_rejection(
            replace(before, current=overflow), chosen, "admission", "nonfinite_value"
        )

    def test_postcontinuity_negative_and_overflow_reject_before_exposure(self) -> None:
        before = stage_inputs_fixture()
        self.assert_rejection(
            before,
            resource_selection(before, (2.0, 0.0)),
            "charge_admission",
            "domain_failure",
            evaluations=1,
        )
        huge = replace(before, dt=1e308)
        self.assert_rejection(
            huge,
            resource_selection(huge, (2.0, 0.0)),
            "continuity",
            "nonfinite_value",
            evaluations=1,
        )

    def test_conservative_real_transfer_can_fail_the_binary64_charge_gate(self) -> None:
        # Exact conservation is insufficient: the prescribed reduction changes
        # from 2**53+2 to 2**53+4. A passing tolerance must never repair C.
        graph = GRCV4Graph(("a", "b", "c", "d"), (OrientedEdge("e", "a", "d"),))
        for tolerance in (0.0, 2.0):
            ref = stage_reference_fixture(
                graph=graph,
                changes={
                    "charge": {
                        "absolute_tolerance": tolerance,
                        "relative_tolerance": 0.0,
                    }
                },
            )
            before = stage_inputs_fixture(ref)
            state = replace(before.current, C=(float(2**53), 1.0, 1.0, 1.0))
            before = replace(
                before, current=state, reset=state, Q_target=float(2**53 + 2)
            )
            chosen = resource_selection(before, (1.0,))
            if tolerance == 0:
                error = self.assert_rejection(
                    before, chosen, "charge_admission", "charge_failure", evaluations=1
                )
                assert error.charge is not None
                self.assertEqual(error.charge.residual, 2.0)
            else:
                result = ProvisionalResourceStep(before, chosen)
                self.assertEqual(
                    result.provisional_state.C, (float(2**53 - 1), 1.0, 1.0, 2.0)
                )
                self.assertEqual(result.charge.actual, float(2**53 + 4))
                self.assertEqual(result.charge.residual, 2.0)
                self.assertIsNone(result.charge.remainder)

    def test_zero_duration_is_locally_admitted_identity_without_selection(self) -> None:
        for realization in ("OS", "CI", "PC", "CI+PC", "RG2b"):
            before = replace(
                stage_inputs_fixture(stage_reference_fixture(realization=realization)),
                dt=0.0,
            )
            with patch(
                "pygrc.models.grc_v4_step.provisional_continuity",
                side_effect=AssertionError("zero wrote resource"),
            ):
                result = ProvisionalResourceStep(before, None)
            self.assertEqual(result.provisional_state, before.current)
            self.assertEqual(result.continuity_evaluations, 0)
            self.assert_rejection(
                before, resource_selection(before), "admission", "domain_failure"
            )
            self.assert_rejection(
                replace(before, Q_target=7.0), None, "admission", "charge_failure"
            )
        with self.assertRaises(TypeError):
            ProvisionalResourceStep(stage_inputs_fixture(), None)

    def test_consumer_requires_independent_exact_inputs_even_if_output_matches(
        self,
    ) -> None:
        before = stage_inputs_fixture()
        chosen = resource_selection(before)
        result = ProvisionalResourceStep(before, chosen)
        for expected_prestate, expected_selection in (
            (replace(before, operation_id="other"), chosen),
            (before, None),
            (
                before,
                replace(chosen, inputs=replace(chosen.inputs, operation_id="other")),
            ),
        ):
            with self.assertRaises(ResourceBoundaryError) as caught:
                result.consume(
                    expected_prestate=expected_prestate,
                    expected_selection=expected_selection,
                )
            self.assertEqual(
                (caught.exception.stage, caught.exception.code),
                ("final_reconstruction", "stale_cache"),
            )

    def test_selection_reconstruction_revalidates_roles_shape_and_forged_types(
        self,
    ) -> None:
        before = stage_inputs_fixture()
        chosen = resource_selection(before)
        raw = chosen.to_payload()
        self.assertEqual(CurrentSelection.from_payload(raw), chosen)
        for data in (
            raw | {"extra": 1},
            raw | {"solver_disposition": "fallback"},
            raw | {"current": [1.0]},
            raw | {"current": [True, 0.0]},
            raw | {"current": [math.inf, 0.0]},
        ):
            with self.assertRaises((TypeError, ValueError)):
                CurrentSelection.from_payload(data)
        with self.assertRaises(TypeError):
            CurrentSelection(
                chosen.inputs,
                "valid_root",
                cast(Any, OneForm(before.geometry.reference.graph, (1.0, 0.5))),
            )
        forged = replace(chosen)
        object.__setattr__(forged, "solver_disposition", "fallback")
        with self.assertRaises(ValueError):
            ProvisionalResourceStep(before, forged)
        raw["current"][0] = 999
        self.assertEqual(
            chosen.current, PhysicalFlux(before.geometry.reference.graph, (1.0, 0.5))
        )
        output = ProvisionalResourceStep(before, chosen).to_payload()
        output["provisional_state"]["C"][0] = 999
        self.assertEqual(
            reconstruct_resource(resource_replay_input())["provisional_state"]["C"],
            [0.0, 2.5, 3.5],
        )

    def test_charge_values_fit_frozen_receipt_without_inventing_commit(self) -> None:
        result, args = positive_fixture()
        before = stage_inputs_fixture()
        charge = ProvisionalResourceStep(before, resource_selection(before)).charge
        # A content fixture proves schema integration only, never a live commit.
        core = cast(
            dict[str, Any], result.emitted_receipts[0].to_payload()["identity_payload"]
        )["core"]
        payload = {
            "schema_version": "grcv4-charge-receipt-v1",
            "core": core,
            **charge.receipt_values(),
        }
        old = args["commit_payload"]
        _, envelopes = make_commit_receipts(
            [payload],
            **{
                k: old[k]
                for k in (
                    "operation_id",
                    "source_state_digest",
                    "target_state_digest",
                    "target_step_index",
                    "target_time",
                )
            },
        )
        self.assertEqual(envelopes[0].to_payload()["identity_payload"], payload)


class ResourceReconstructionTests(unittest.TestCase):
    def test_resource_reconstruction_outside_checkout_with_three_hash_seeds(
        self,
    ) -> None:
        root = Path(__file__).resolve().parents[2]
        supplied = resource_replay_input()
        expected = reconstruct_resource(supplied)
        with tempfile.TemporaryDirectory(prefix="p933-replay-") as directory:
            input_path = Path(directory) / "inputs.json"
            input_path.write_text(json.dumps(supplied))
            for seed in ("0", "1", "933"):
                environment = dict(
                    os.environ,
                    PYTHONHASHSEED=seed,
                    PYTHONPATH=os.pathsep.join((str(root / "src"), str(root))),
                )
                process = subprocess.run(
                    [
                        sys.executable,
                        str(Path(__file__).resolve()),
                        "--reconstruct-resource",
                        str(input_path),
                    ],
                    cwd=directory,
                    env=environment,
                    text=True,
                    capture_output=True,
                    timeout=60,
                )
                self.assertEqual(process.returncode, 0, process.stderr)
                self.assertEqual(json.loads(process.stdout), expected)

    @unittest.skipUnless(
        os.environ.get("GRCV4_PACKAGE_TESTS") == "1",
        "opt-in clean resource wheel/sdist replay",
    )
    def test_clean_installed_wheel_and_sdist_resource_boundary(self) -> None:
        root = Path(__file__).resolve().parents[2]
        supplied = resource_replay_input()
        expected = reconstruct_resource(supplied)
        source_names = ("grc_v4_transport", "grc_v4_step")
        hashes = {
            name: sha256(
                (root / f"src/pygrc/models/{name}.py").read_bytes()
            ).hexdigest()
            for name in source_names
        }
        consumer = """
import hashlib, importlib, json, pathlib, sys
from dataclasses import replace
from pygrc.models.grc_v4_geometry import GeometryStageInputs
from pygrc.models.grc_v4_step import CurrentSelection, ProvisionalResourceStep, ResourceBoundaryError
from pygrc.models.grc_v4_profile import list_supported_profiles
data=json.load(sys.stdin)
for name, digest in data['hashes'].items():
    path=pathlib.Path(importlib.import_module('pygrc.models.'+name).__file__).resolve()
    assert path.is_relative_to(pathlib.Path(sys.prefix).resolve())
    assert hashlib.sha256(path.read_bytes()).hexdigest()==digest
before=GeometryStageInputs.from_payload(data['inputs']['prestate'])
selected=CurrentSelection.from_payload(data['inputs']['selection'])
result=ProvisionalResourceStep(before,selected)
assert result.provisional_state.C==(0.,2.5,3.5)
assert result.charge.residual==0. and result.charge.remainder is None
try: ProvisionalResourceStep(before,replace(selected,solver_disposition='singular'))
except ResourceBoundaryError as error: assert (error.stage,error.code)==('candidate_solve','singular_solver')
else: raise AssertionError('installed fallback current was consumed')
assert list_supported_profiles() == frozenset({'grcv4-profile-sha256:a6b853ee382895eb78b1a7955a0df22f95d68b27cb0f762503e8c424c2f59b6d', 'grcv4-profile-sha256:e4c04a83240a33d77c50a26ca6effbb6ce142774bd01f0966861dd517a94e2c4', 'grcv4-profile-sha256:16ed65f7f65d4716e1be3e384f6fa0f957d26dd7b7a3f7e1b43ad1aa3f250946', 'grcv4-profile-sha256:a56ef981821478cc50a3551a914dd6240e0dc62c9ca69d52305bd59a3405f69e', 'grcv4-profile-sha256:058ae6b1f923c85952ffdfa083af74e3b56dd450f309190f307c3ea56ac2aa75', 'grcv4-profile-sha256:6105daf6f5111fdc51640194298b1b8398d608684791050d85b696bcd681f64f', 'grcv4-profile-sha256:5f2f848af0f482699ac6cb88e4e1bd1a66458774bac2c3cc6df9f74cc47d7689', 'grcv4-profile-sha256:3a7a084788c59a55b4232fb98e9c5529c1aa4c7c71074c9d3288982fa2fd2a5b', 'grcv4-profile-sha256:12abb2946bfaa616df2a42bd571732e2be3000736f5078d45f8dbf53682b212b', 'grcv4-profile-sha256:413497bec4f219ec402d82d5cd2aced01dca25a58d2ab906c348472b98d596b0'})
print(json.dumps(result.to_payload(),sort_keys=True))
"""
        environment = {
            k: v for k, v in os.environ.items() if k not in {"PYTHONPATH", "PYTHONHOME"}
        }
        with tempfile.TemporaryDirectory(prefix="p933-package-") as directory:
            temporary = Path(directory)
            source = temporary / "source"
            source.mkdir()
            shutil.copytree(
                root / "src",
                source / "src",
                ignore=shutil.ignore_patterns("__pycache__", "*.egg-info"),
            )
            for name in ("pyproject.toml", "README.md", "LICENSE"):
                shutil.copyfile(root / name, source / name)

            def run(command: list[str], cwd: Path, stdin: str | None = None) -> str:
                process = subprocess.run(
                    command,
                    cwd=cwd,
                    env=environment,
                    input=stdin,
                    text=True,
                    capture_output=True,
                    timeout=240,
                )
                self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
                return process.stdout

            dist = temporary / "dist"
            run(
                [
                    sys.executable,
                    "-m",
                    "build",
                    "--no-isolation",
                    "--outdir",
                    str(dist),
                ],
                source,
            )
            for archive in (next(dist.glob("*.whl")), next(dist.glob("*.tar.gz"))):
                with self.subTest(archive=archive.name):
                    isolated = temporary / (archive.name + "-env")
                    venv.EnvBuilder(with_pip=True).create(isolated)
                    python = isolated / "bin/python"
                    outside = temporary / (archive.name + "-consumer")
                    outside.mkdir()
                    run(
                        [
                            str(python),
                            "-m",
                            "pip",
                            "install",
                            "--no-index",
                            "--find-links",
                            str(Path(os.environ["GRCV4_WHEELHOUSE"]).resolve()),
                            str(archive) + "[v4]",
                        ],
                        outside,
                    )
                    actual = json.loads(
                        run(
                            [str(python), "-I", "-c", consumer],
                            outside,
                            json.dumps({"inputs": supplied, "hashes": hashes}),
                        )
                    )
                    self.assertEqual(actual, expected)
                    run([str(python), "-m", "pip", "check"], outside)


def export_p933_audit(output: Path) -> dict[str, Any]:
    """Export current sources/assets/evidence without a machine-local environment."""
    import zipfile

    root = Path(__file__).resolve().parents[2]
    output = output.resolve()
    if output.is_relative_to(root):
        ignored = subprocess.run(
            ["git", "check-ignore", "--quiet", "--", str(output.relative_to(root))],
            cwd=root,
            check=False,
        )
        if ignored.returncode != 0:
            raise ValueError("export to ignored storage to avoid recursive evidence")
    paths = (
        subprocess.check_output(
            ["git", "ls-files", "-c", "-o", "--exclude-standard", "-z"], cwd=root
        )
        .decode()
        .split("\0")
    )
    prefixes = (
        "src/",
        "tests/",
        "specs/",
        "implementation/phase-9-grcv4/",
        "implementation/investigations/grc9v4-constitutive-design/",
        "implementation/Phase-9-GRCV4-",
    )
    metadata = {"README.md", "LICENSE", "pyproject.toml", "MANIFEST.in"}
    names = sorted(
        {p for p in paths if p and (p in metadata or p.startswith(prefixes))}
    )
    manifest: dict[str, Any] = {
        "schema": "p933_review_packet_v1",
        "base_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=root, text=True
        ).strip(),
        "scope": "Current source, dependency declarations, fixtures, frozen assets, scientific sources and retained evidence. No virtual environments, dependency wheels, Git history or managed browsers.",
        "authority_limit": "Standalone numerical reconstruction; historical acceptance and permission replay require the stated Git base and protected history.",
        "review": "implementation/phase-9-grcv4/tranche-3/P9-3.3-Review.md",
        "files": [],
    }

    def write(archive: zipfile.ZipFile, name: str, data: bytes) -> None:
        entry = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
        entry.compress_type = zipfile.ZIP_DEFLATED
        entry.external_attr = 0o100644 << 16
        archive.writestr(entry, data)

    with zipfile.ZipFile(output, mode="x") as archive:
        for name in names:
            path = root / name
            if path.is_symlink() or not path.is_file():
                raise ValueError(f"non-regular packet input: {name}")
            data = path.read_bytes()
            manifest["files"].append(
                {"path": name, "sha256": sha256(data).hexdigest(), "bytes": len(data)}
            )
            write(archive, name, data)
        write(
            archive,
            "BUNDLE-MANIFEST.json",
            (json.dumps(manifest, indent=2) + "\n").encode(),
        )
    return {
        "files": len(names),
        "bytes": output.stat().st_size,
        "sha256": sha256(output.read_bytes()).hexdigest(),
    }


def capture_p933(output: Path, *, audit_only: bool = False) -> int:
    """Capture a reconstructible numerical run as it executes; never overwrite.

    Run from a checkout with the declared extra/dev/build dependencies. Set
    GRCV4_PACKAGE_TESTS=1 and GRCV4_WHEELHOUSE to exercise clean offline installs.
    Permission/browser checks have their own existing runner and subject.
    """
    from datetime import datetime, timezone
    import importlib.metadata
    import platform
    import re
    import time

    root = Path(__file__).resolve().parents[2]
    if audit_only and (
        os.environ.get("GRCV4_PACKAGE_TESTS") != "1"
        or not Path(os.environ.get("GRCV4_WHEELHOUSE", "<missing>")).is_dir()
    ):
        raise ValueError(
            "audit capture requires both clean package tests and a wheelhouse"
        )
    output.mkdir(parents=True, exist_ok=False)
    tool = (
        root
        / "implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool"
    )
    paper = "implementation/investigations/grc9v4-constitutive-design/drafts/2026-09-GRC-V4.md"
    scopes = [
        "src",
        "tests",
        "specs",
        "pyproject.toml",
        "README.md",
        "LICENSE",
        paper,
        str((tool / "src").relative_to(root)),
    ]

    def git(*arguments: str) -> str:
        return subprocess.check_output(["git", *arguments], cwd=root, text=True)

    paths = git("ls-files", "--", *scopes).splitlines()
    hashes = {p: sha256((root / p).read_bytes()).hexdigest() for p in paths}
    supplied = resource_replay_input()
    subject = {
        "base_commit": git("rev-parse", "HEAD").strip(),
        "patch": git("diff", "--binary", "HEAD", "--", *scopes),
        "tracked_file_sha256": hashes,
        "untracked_source_files": git(
            "ls-files", "--others", "--exclude-standard", "--", *scopes
        ).splitlines(),
    }
    if subject["untracked_source_files"]:
        raise ValueError(
            "capture requires any new source to be tracked for base-plus-patch reconstruction"
        )
    (output / "inputs.json").write_text(
        json.dumps({"subject": subject, "resource_replay": supplied}, indent=2) + "\n"
    )
    record: dict[str, Any] = {
        "schema": "phase9_leaf_run_v1",
        "iteration_id": "P9-3.3",
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "status": "running",
        "subject_inputs": "inputs.json",
        "scope": "transport/step audit follow-up"
        if audit_only
        else "complete repository regression",
        "python": sys.version,
        "platform": platform.platform(),
        "dependencies": sorted(
            f"{d.metadata['Name']}=={d.version}"
            for d in importlib.metadata.distributions()
        ),
        "environment": {
            k: os.environ.get(k)
            for k in ("GRCV4_PACKAGE_TESTS", "GRCV4_WHEELHOUSE", "PYTHONHASHSEED")
        },
        "commands": [],
        "wheelhouse_sha256": {
            p.name: sha256(p.read_bytes()).hexdigest()
            for p in sorted(Path(os.environ["GRCV4_WHEELHOUSE"]).iterdir())
            if p.is_file()
        }
        if os.environ.get("GRCV4_WHEELHOUSE")
        else {},
        "claim_ceiling": "local resource/charge boundary, regression and installed reconstruction; supplied current results are not root certificates or full runtime support",
    }

    def retain() -> None:
        (output / "run.json").write_text(json.dumps(record, indent=2) + "\n")

    retain()
    changed = [
        f"{prefix}/grc_v4_{module}.py"
        if prefix == "src/pygrc/models"
        else f"{prefix}/test_grc_v4_{module}.py"
        for prefix in ("src/pygrc/models", "tests/models")
        for module in ("transport", "step")
    ]
    commands = [
        [
            sys.executable,
            "-m",
            "unittest",
            "tests.models.test_grc_v4_transport",
            "tests.models.test_grc_v4_step",
        ]
        if audit_only
        else [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-t", "."],
        [sys.executable, "-m", "ruff", "check", *changed],
        [sys.executable, "-m", "mypy", "--strict", *changed],
        [sys.executable, "-m", "pip", "check"],
    ]
    try:
        for command in commands:
            started = time.monotonic()
            print("Executing", " ".join(command), flush=True)
            process = subprocess.run(
                command, cwd=root, text=True, capture_output=True, timeout=2400
            )
            transcript = process.stdout + process.stderr
            tests = re.search(r"Ran (\d+) tests? in", transcript)
            record["commands"].append(
                {
                    "argv": ["<venv-python>", *command[1:]],
                    "cwd": "<checkout>",
                    "exit_status": process.returncode,
                    "elapsed_seconds": round(time.monotonic() - started, 3),
                    "tests_run": None if tests is None else int(tests.group(1)),
                    "output": transcript if process.returncode else transcript[-1500:],
                }
            )
            retain()
            if process.returncode:
                raise RuntimeError("validation command failed; see run.json")
        sys.path.insert(0, str(tool / "src"))
        successor = importlib.import_module("grcv4_explorer.successor")
        forensic = importlib.import_module("grcv4_explorer.forensic")
        context = successor.load_successor_forensic_context(root, tool.parent)
        contracts = [
            "D10.2-EC-PARENT-CORE-GENERAL-CHARGE",
            "D10.2-EC-PARENT-CORE-INCIDENCE-CONTINUITY",
            "D10.2-EC-PARENT-L-AUTHORITATIVE-CURRENT",
            "D10.2-EC-PARENT-L-CONTINUITY-WRITE",
            "D10.2-EC-PARENT-L-POSTCONTINUITY-REFRESH",
            "D10.2-EC-CHARGE-BUDGET-STAGE",
        ]
        traces = [forensic.contract_provenance(context, name) for name in contracts]
        record["forensic_queries"] = [
            {
                "operation": "contract_provenance",
                "contract_id": trace["query"]["contract_id"],
                "trace_digest": trace["trace_digest"],
                "source_bundle_digest": trace["source_bundle_digest"],
                "authority_extension_digest": trace["authority_extension_digest"],
                "source_ref": trace["rows"][0]["source_ref"],
                "support_disposition": trace["rows"][0]["payload"][
                    "support_disposition"
                ],
            }
            for trace in traces
        ]
        record["forensic_loader"] = (
            "grcv4_explorer.successor.load_successor_forensic_context"
        )
        (output / "actual.json").write_text(
            json.dumps(reconstruct_resource(supplied), indent=2) + "\n"
        )
        record["source_unchanged_during_run"] = all(
            sha256((root / p).read_bytes()).hexdigest() == digest
            for p, digest in hashes.items()
        )
        if not record["source_unchanged_during_run"]:
            raise RuntimeError("validation source changed during capture")
        record["status"] = "passed"
    except Exception as error:
        record["status"] = "failed"
        record["error"] = str(error)
    record["completed_utc"] = datetime.now(timezone.utc).isoformat()
    record["artifacts"] = {
        p.name: sha256(p.read_bytes()).hexdigest()
        for p in sorted(output.iterdir())
        if p.name != "run.json"
    }
    retain()
    return int(record["status"] != "passed")


_P935_METHODS = (
    "test_capture_requires_each_reviewed_preservation_method",
    "test_observer_detects_each_coordinate_alias_type_and_cycle_change",
    "test_all_failed_dispositions_preserve_ten_full_prestates_and_selection",
    "test_admission_and_missing_selection_preserve_both_histories",
    "test_stale_selection_preserves_request_reference_history_and_order",
    "test_late_resource_failures_preserve_inputs_and_detach_charge_diagnostics",
    "test_consumption_rejection_preserves_cache_and_independent_expectations",
    "test_reconstruction_rejection_preserves_raw_nested_aliases_and_live_records",
    "test_malformed_wire_rejection_preserves_cyclic_and_shared_input",
    "test_negative_attempts_preserve_full_payload_and_result_isolation",
    "test_binding_detects_full_state_changes_without_mutating_either_observation",
    "test_harness_catches_nonresource_reset_ledger_and_exception_mutations",
    "test_independent_observer_exposes_mutating_and_lying_serializers",
)


def p935_required(root: Path) -> set[str]:
    from tests.models.test_grc_v4_geometry import _p934_required

    return _p934_required(root) | {
        "tests.models.test_grc_v4_step.PrestatePreservationTests." + name
        for name in _P935_METHODS
    }


def capture_p935(output: Path) -> int:
    """Capture full regression, installed reconstruction and source queries.

    Passing method identities are reconstructed from the pinned P9-3.4 roster
    plus the explicit additions above. Only nonpassing method details repeat in
    the manifest. A current pass requires exact discovery/execution agreement,
    no skips, live-code checks, and unchanged source bytes throughout execution.
    """
    from datetime import datetime, timezone
    import importlib
    import importlib.metadata
    import io
    import platform
    import time
    from tests.models.test_grc_v4_geometry import (
        _P934Result,
        _P934_BASELINE,
        _P934_BASELINE_SHA256,
        _p934_coverage,
        _p934_ids,
        _p934_loaded_sources,
    )

    root = Path(__file__).resolve().parents[2]
    output = output.resolve()
    wheelhouse = Path(os.environ.get("GRCV4_WHEELHOUSE", "<missing>")).resolve()
    if not output.is_relative_to(root) or not wheelhouse.is_relative_to(root):
        raise ValueError("capture and dependency inputs must be repository-local")
    if os.environ.get("GRCV4_PACKAGE_TESTS") != "1" or not wheelhouse.is_dir():
        raise ValueError("capture requires clean package tests and their wheelhouse")
    tool = (
        root
        / "implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool"
    )
    scopes = [
        "src",
        "tests",
        "specs",
        "pyproject.toml",
        "uv.lock",
        "README.md",
        "LICENSE",
        "implementation/investigations/grc9v4-constitutive-design/drafts/2026-09-GRC-V4.md",
        str((tool / "src").relative_to(root)),
    ]
    if any(
        output == root / name or output.is_relative_to(root / name) for name in scopes
    ):
        raise ValueError("capture output cannot occupy an observed source scope")

    def git(*args: str) -> str:
        return subprocess.check_output(["git", *args], cwd=root, text=True)

    def save(name: str, value: Any) -> None:
        (output / name).write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")

    if git("ls-files", "--others", "--exclude-standard", "--", *scopes).strip():
        raise ValueError("new source needs a tracked Git reconstruction preimage")
    hashes = {
        p: sha256((root / p).read_bytes()).hexdigest()
        for p in git("ls-files", "--", *scopes).splitlines()
    }
    output.mkdir(parents=True, exist_ok=False)
    save(
        "inputs.json",
        {
            "base_commit": git("rev-parse", "HEAD").strip(),
            "patch": git("diff", "--binary", "HEAD", "--", *scopes),
            "source_sha256": hashes,
            "reviewed_roster": {
                "path": _P934_BASELINE,
                "sha256": _P934_BASELINE_SHA256,
            },
            "reconstruction": "In a separate clone, checkout base_commit, apply patch, verify every source_sha256. Install recorded dependencies for the active platform, build the repository-local wheelhouse, and execute replay_command with a fresh output directory.",
        },
    )
    record: dict[str, Any] = {
        "schema": "phase9_leaf_run_v1",
        "iteration_id": "P9-3.5",
        "status": "running",
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "inputs": {
            "path": "inputs.json",
            "sha256": sha256((output / "inputs.json").read_bytes()).hexdigest(),
        },
        "python": sys.version,
        "platform": platform.platform(),
        "dependencies": sorted(
            f"{d.metadata['Name']}=={d.version}"
            for d in importlib.metadata.distributions()
        ),
        "environment": {
            "GRCV4_PACKAGE_TESTS": "1",
            "GRCV4_WHEELHOUSE": str(wheelhouse.relative_to(root)),
            **{
                key: os.environ.get(key)
                for key in ("PYTHONHASHSEED", "OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS")
            },
        },
        "wheelhouse_sha256": {
            p.name: sha256(p.read_bytes()).hexdigest()
            for p in sorted(wheelhouse.iterdir())
            if p.is_file()
        },
        "replay_command": [
            ".venv/bin/python",
            "-m",
            "tests.models.test_grc_v4_step",
            "--capture-p935",
            "<fresh-repository-relative-output>",
        ],
        "claim_ceiling": "Full preservation of observed inputs at implemented local rejection boundaries. Supplied solver dispositions, immutable constructors and harness mutation controls do not execute a complete candidate solve or live lifecycle rollback; this local check does not extend the separately accepted P9-4.8B runtime scope.",
        "commands": [],
    }
    save("run.json", record)
    try:
        required = p935_required(root)
        suite = unittest.defaultTestLoader.discover(
            str(root / "tests"), top_level_dir=str(root)
        )
        names = _p934_ids(suite)
        record["coverage"] = _p934_coverage(required, names)
        if not record["coverage"]["passed"]:
            raise RuntimeError("discovered tests differ from reviewed roster")
        record["loaded_sources_before"] = _p934_loaded_sources(root, hashes)
        stream = io.StringIO()
        start = time.monotonic()
        result = cast(
            _P934Result,
            unittest.TextTestRunner(stream=stream, resultclass=_P934Result).run(suite),
        )
        record["coverage"] = _p934_coverage(required, names, result.rows)
        record["test_results"] = {
            "required_roster": "p935_required in the captured test module; inherited pinned roster plus explicit P9-3.4 and P9-3.5 additions",
            "executed_ids_sha256": sha256(
                json.dumps(
                    sorted(r["test"] for r in result.rows), separators=(",", ":")
                ).encode()
            ).hexdigest(),
            "passing_methods": sum(r["status"] == "passed" for r in result.rows),
            "nonpassing_methods": [r for r in result.rows if r["status"] != "passed"],
        }
        record["commands"].append(
            {
                "operation": "unittest discover tests with repository top level",
                "tests_run": result.testsRun,
                "failures": len(result.failures),
                "errors": len(result.errors),
                "skips": len(result.skipped),
                "elapsed_seconds": round(time.monotonic() - start, 3),
                "output": stream.getvalue().replace(str(root), "<checkout>"),
            }
        )
        save("run.json", record)
        if (
            not result.wasSuccessful()
            or result.skipped
            or not record["coverage"]["passed"]
            or result.testsRun != len(names)
        ):
            raise RuntimeError("required tests missing, failed or skipped")
        for args in (
            ["ruff", "check", "tests/models/test_grc_v4_step.py"],
            ["mypy", "--strict", "tests/models/test_grc_v4_step.py"],
            ["pip", "check"],
        ):
            process = subprocess.run(
                [sys.executable, "-m", *args],
                cwd=root,
                capture_output=True,
                text=True,
                timeout=600,
            )
            record["commands"].append(
                {
                    "argv": [".venv/bin/python", "-m", *args],
                    "exit_status": process.returncode,
                    "output": (process.stdout + process.stderr).replace(
                        str(root), "<checkout>"
                    ),
                }
            )
            if process.returncode:
                raise RuntimeError("static/environment validation failed")
        sys.path.insert(0, str(tool / "src"))
        successor = importlib.import_module("grcv4_explorer.successor")
        forensic = importlib.import_module("grcv4_explorer.forensic")
        forensic_canonical = importlib.import_module("grcv4_explorer.canonical")
        context = successor.load_successor_forensic_context(root, tool.parent)
        traces = [
            forensic.contract_provenance(context, "D10.2-EC-PARENT-" + name)
            for name in ("L-ATOMICITY", "L-SINGULAR-FAIL-CLOSED", "L-SNAPSHOT-RESET")
        ]
        expected_digests = (
            "62a376f2a8e613b18a0999ce6bd16367ac45d0566c6b7b76d092fc64fbd11a57",
            "246a2cc325da80a6c79a0445ada4eb2d85ef26012399d7606e0418cc9693055b",
            "724545426e8380628505c85d0e3b560eec4388d4cacc711c1b4047a5066bf7dc",
        )
        if tuple(t["trace_digest"] for t in traces) != expected_digests or any(
            t["trace_digest"]
            != forensic_canonical.digest(
                {k: v for k, v in t.items() if k != "trace_digest"}
            )
            for t in traces
        ):
            raise RuntimeError(
                "forensic traces differ from independently reviewed source queries"
            )
        record["forensic_queries"] = traces
        if any(
            sha256((root / p).read_bytes()).hexdigest() != h for p, h in hashes.items()
        ):
            raise RuntimeError("source changed during execution")
        if git("ls-files", "--others", "--exclude-standard", "--", *scopes).strip():
            raise RuntimeError("new source appeared during execution")
        record["loaded_sources_after"] = _p934_loaded_sources(root, hashes)
        if any(
            record["loaded_sources_after"].get(n) != v
            for n, v in record["loaded_sources_before"].items()
        ):
            raise RuntimeError("loaded sources changed during execution")
        record["status"] = "passed"
        record["source_unchanged_during_run"] = True
    except BaseException as exc:
        record["status"] = "failed"
        record["failure"] = {
            "type": type(exc).__name__,
            "reason": str(exc).replace(str(root), "<checkout>"),
        }
        raise
    finally:
        record["completed_utc"] = datetime.now(timezone.utc).isoformat()
        save("run.json", record)
    print(
        f"P935_PRESERVATION_VALIDATION_PASS tests={result.testsRun} skips=0", flush=True
    )
    return 0


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] in ("--capture-p933", "--capture-p933-audit"):
        raise SystemExit(
            capture_p933(
                Path(sys.argv[2]).resolve(),
                audit_only=sys.argv[1] == "--capture-p933-audit",
            )
        )
    elif len(sys.argv) == 3 and sys.argv[1] == "--capture-p935":
        raise SystemExit(capture_p935(Path(sys.argv[2])))
    elif len(sys.argv) == 3 and sys.argv[1] == "--export-p933-audit":
        print(json.dumps(export_p933_audit(Path(sys.argv[2])), sort_keys=True))
    elif len(sys.argv) == 3 and sys.argv[1] == "--reconstruct-resource":
        print(
            json.dumps(
                reconstruct_resource(json.loads(Path(sys.argv[2]).read_text())),
                sort_keys=True,
            )
        )
    else:
        unittest.main()

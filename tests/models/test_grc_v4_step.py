"""Local admission and exact failure identities, not a complete beat test."""

from __future__ import annotations

from collections import UserList, UserString
from collections.abc import Callable, Iterator
from copy import deepcopy
from dataclasses import fields, replace
from hashlib import sha256
import json
import math
from pathlib import Path
from typing import Any, cast, get_args
import unittest

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
    FailureCode,
    FailureReceipt,
    FailureReceiptIdentityPayload,
    GRCV4Failure,
    OperationStage,
    StepResultEvidence,
    SuccessfulReceiptEnvelope,
    admit_step_request,
    bind_step_result,
    make_commit_receipts,
    negative_duration_result,
)
from pygrc.models.grc_v4_state import GRCV4LifecycleResult, GRCV4StepResult
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


if __name__ == "__main__":
    unittest.main()

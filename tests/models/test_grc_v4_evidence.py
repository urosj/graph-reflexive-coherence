"""Operation facts must preserve wire identities, failure guards and isolation."""

import unittest
from concurrent.futures import ThreadPoolExecutor
from dataclasses import FrozenInstanceError, replace
from types import SimpleNamespace
from unittest.mock import patch

from pygrc.models import _grc_v4_evidence as evidence
from pygrc.models import grc_v4_codec as codec
from pygrc.models import grc_v4_geometry as geometry
from pygrc.models import grc_v4_lifecycle as lifecycle
from pygrc.models import grc_v4_step as step
from pygrc.models.grc_v4_linear import _MatrixFacts
from pygrc.models.grc_v4_state import FrozenJSONMap
from tests.models.test_grc_v4_generic_lifecycle import FAMILIES, fixture, model
from tests.models.test_grc_v4_lifecycle import request

STATE = "grcv4-state-sha256:" + "0" * 64
OTHER_STATE = "grcv4-state-sha256:" + "1" * 64
RECEIPTS = tuple("grc-receipt-sha256:" + f"{i:064x}" for i in range(400))


class OperationEvidenceTests(unittest.TestCase):
    def test_exact_legacy_identity_for_ordered_prefixes_and_changed_states(self):
        scope = evidence._OperationEvidence()
        for ids in ((), RECEIPTS[:1], RECEIPTS, tuple(reversed(RECEIPTS))):
            for state in (STATE, OTHER_STATE):
                expected = codec.payload_identity("lifecycle_envelope_payload", evidence._envelope(state, ids))
                with self.subTest(length=len(ids), state=state):
                    self.assertEqual(scope.lifecycle(state, ids), expected)
                    self.assertEqual(scope.lifecycle(state, tuple(value for value in ids)), expected)

    def test_prefix_schema_admission_once_and_no_full_scan_on_identity_hit(self):
        scope = evidence._OperationEvidence()
        original = codec.validate_payload
        lengths = []

        def validate(name, value):
            if name == "lifecycle_envelope_payload":
                lengths.append(len(value["receipt_ids"]))
            return original(name, value)

        with patch.object(codec, "validate_payload", side_effect=validate):
            first = scope.lifecycle(STATE, RECEIPTS)
            self.assertEqual(scope.lifecycle(STATE, RECEIPTS), first)
            scope.lifecycle(OTHER_STATE, RECEIPTS)
            self.assertEqual(scope.lifecycle(STATE, tuple(value for value in RECEIPTS)), first)
        self.assertEqual(lengths, [400, 0, 0])
        with patch.object(codec, "canonical_json_bytes", side_effect=AssertionError("history encoded again")):
            self.assertEqual(scope.lifecycle(STATE, RECEIPTS), first)

    def test_changed_or_invalid_inputs_cannot_hit_an_admitted_fact(self):
        scope = evidence._OperationEvidence()
        scope.lifecycle(STATE, RECEIPTS)
        for state, ids in (("forged", RECEIPTS), (STATE, RECEIPTS + ("forged",)), (STATE, (True,))):
            with self.subTest(state=state, ids=ids[-1:]), self.assertRaises(codec.V4SchemaError):
                scope.lifecycle(state, ids)
        mutable = list(RECEIPTS[:1])
        scope.lifecycle(STATE, mutable)
        mutable[0] = "forged"
        with self.assertRaises(codec.V4SchemaError):
            scope.lifecycle(STATE, mutable)
        self.assertEqual(scope.lifecycle(STATE, RECEIPTS), codec.payload_identity("lifecycle_envelope_payload", evidence._envelope(STATE, RECEIPTS)))

    def test_warm_identity_still_checks_assets_and_dependencies(self):
        scope = evidence._OperationEvidence()
        scope.lifecycle(STATE, RECEIPTS)
        error = codec.V4AssetError("changed installed asset")
        with patch.object(codec, "_load_contract_schema", side_effect=error), self.assertRaises(codec.V4AssetError):
            scope.lifecycle(STATE, RECEIPTS)
        with patch.object(codec, "_dependency", side_effect=RuntimeError("dependency changed")), self.assertRaisesRegex(RuntimeError, "dependency changed"):
            scope.lifecycle(STATE, RECEIPTS)

    def test_scope_is_discarded_on_failure_and_nested_scopes_are_independent(self):
        observed = []

        @evidence._operation_evidence
        def inner():
            observed.append(evidence._scope())
            raise RuntimeError("operation failed")

        @evidence._operation_evidence
        def outer():
            scope = evidence._scope()
            with self.assertRaisesRegex(RuntimeError, "operation failed"):
                inner()
            self.assertIs(evidence._scope(), scope)
            return scope

        self.assertIsNone(evidence._scope())
        outer_scope = outer()
        self.assertIsNot(outer_scope, observed[0])
        self.assertIsNone(evidence._scope())
        with ThreadPoolExecutor(max_workers=2) as pool:
            scopes = list(pool.map(lambda _: outer(), range(2)))
        self.assertIsNot(scopes[0], scopes[1])
        self.assertIsNone(evidence._scope())

    def test_retained_cache_is_bounded(self):
        scope = evidence._OperationEvidence()
        for i in range(270):
            state = "grcv4-state-sha256:" + f"{i:064x}"
            scope.lifecycle(state, RECEIPTS)
        self.assertLessEqual(len(scope.identities), 256)
        for i in range(140):
            scope.lifecycle(STATE, tuple(value for value in RECEIPTS))
        self.assertLessEqual(len(scope.aliases), 128)
        for i in range(12):
            ids = RECEIPTS[:i]
            self.assertEqual(scope.lifecycle(STATE, ids), codec.payload_identity("lifecycle_envelope_payload", evidence._envelope(STATE, ids)))
        self.assertLessEqual(len(scope.prefixes), 8)

    def test_incremental_hash_keeps_exact_bytes_and_prior_prefix_on_failure(self):
        prefix = evidence._ReceiptEvidence.from_ids(())
        for end in range(4, 401, 4):
            previous = prefix.identity(STATE)
            prefix = prefix.extend(RECEIPTS[end - 4:end])
            self.assertEqual(prefix.identity(OTHER_STATE), codec.payload_identity("lifecycle_envelope_payload", evidence._envelope(OTHER_STATE, RECEIPTS[:end])))
            self.assertNotEqual(prefix.identity(STATE), previous)
        saved = prefix.identity(STATE)
        with self.assertRaises(codec.V4SchemaError):
            prefix.extend(("forged",))
        self.assertEqual(prefix.identity(STATE), saved)
        with patch.object(codec, "canonical_json_bytes", wraps=codec.canonical_json_bytes) as encode:
            prefix.identity(OTHER_STATE)
        self.assertEqual(encode.call_count, 1)
        self.assertEqual(encode.call_args.args, (evidence._envelope(OTHER_STATE, ()),))

    def test_prefix_builder_uses_the_detached_admission_not_a_second_caller_read(self):
        class ChangingIDs(list):
            def __init__(self):
                super().__init__(RECEIPTS[:1])
                self.reads = 0

            def __iter__(self):
                self.reads += 1
                return iter(RECEIPTS[:1] if self.reads == 1 else ("forged",))

        expected = codec.payload_identity("lifecycle_envelope_payload", evidence._envelope(STATE, RECEIPTS[:1]))
        for extend in (False, True):
            ids = ChangingIDs()
            prefix = (evidence._ReceiptEvidence.from_ids(()).extend(ids) if extend
                      else evidence._ReceiptEvidence.from_ids(ids))
            self.assertEqual(prefix.identity(STATE), expected)
            self.assertEqual(ids.reads, 1)

    def test_seeded_prefix_only_validates_the_bounded_state_suffix(self):
        prefix = evidence._ReceiptEvidence.from_ids(RECEIPTS)
        scope = evidence._OperationEvidence()
        scope.seed(prefix, RECEIPTS)
        original = codec.validate_payload
        lengths = []

        def validate(name, value):
            if name == "lifecycle_envelope_payload":
                lengths.append(len(value["receipt_ids"]))
            return original(name, value)

        with patch.object(codec, "validate_payload", side_effect=validate):
            scope.lifecycle(STATE, RECEIPTS)
            scope.lifecycle(OTHER_STATE, RECEIPTS)
        self.assertEqual(lengths, [0, 0])

    def test_native_step_checks_bindings_without_building_discarded_evidence_bytes(self):
        owner = model("A_OS")
        with patch.object(step, "StepResultEvidence", side_effect=AssertionError("unused full evidence")):
            result = owner.step_v4_input(request(fixture("A_OS")[0].dt, "no-unused-evidence"))
        self.assertTrue(result.committed, result.failure)

    def test_ordinary_publication_constructs_one_target_state(self):
        owner = model("A_OS")
        with patch.object(lifecycle, "_lifecycle_state", wraps=lifecycle._lifecycle_state) as project:
            result = owner.step_v4_input(request(fixture("A_OS")[0].dt, "one-public-target"))
        self.assertTrue(result.committed, result.failure)
        self.assertEqual(project.call_count, 1)

    def test_direct_publication_comparison_rejects_every_changed_state_field(self):
        owner = model("A_OS")
        owner.step_v4_input(request(fixture("A_OS")[0].dt, "compare-public-target"))
        state = owner.state.lifecycle
        archive = owner._operation._owned.archive
        after = lifecycle._state_inputs(owner._operation._owned.reference, state)
        archive.check_target_state(after, state, archive.receipts, ())
        changes = {
            "step_index": state.step_index + 1,
            "time": state.time + 1,
            "graph": FrozenJSONMap({"wrong": True}),
            "graph_digest": "wrong",
            "orientation_identity": "wrong",
            "profile": FrozenJSONMap({"wrong": True}),
            "context_contract_id": "wrong",
            "context_value_digest": "wrong",
            "current": replace(state.current, C=tuple(value + 1 for value in state.current.C)),
            "reset": replace(state.reset, Q_target=state.Q_target + 1),
            "Q_target": state.Q_target + 1,
            "receipt_ledger": state.receipt_ledger[::-1],
            "scientific_state_digest": "wrong",
            "lifecycle_digest": "wrong",
        }
        for name, value in changes.items():
            changed = replace(state)
            object.__setattr__(changed, name, value)
            with self.subTest(field=name), self.assertRaises(codec.V4IdentityError):
                archive.check_target_state(after, changed, archive.receipts, ())
        # Bool must not compare equal to the previously admitted numeric clock.
        row = state.receipt_ledger[0].to_dict()
        row["identity_payload"]["core"]["target_step_index"] = True
        bad = replace(state, receipt_ledger=(FrozenJSONMap(row),) + state.receipt_ledger[1:])
        with self.assertRaises(codec.V4IdentityError):
            archive.check_target_state(after, bad, archive.receipts, ())

    def test_direct_frozen_tokens_match_wire_content_and_detect_forced_mutation(self):
        record = FrozenJSONMap({"b": [1, {"value": False}], "a": None})
        token = lifecycle._CheckedArchive._token
        self.assertEqual(token(record), token(record.to_dict()))
        object.__setattr__(record, "_items", tuple(reversed(record._items)))
        self.assertEqual(token(record), token(record.to_dict()))
        before = token(record)
        object.__setattr__(record, "_items", (("b", (True,)), ("a", None)))
        self.assertNotEqual(token(record), before)
        self.assertEqual(token(record), token(record.to_dict()))

    def test_stage_capture_and_asset_reads_are_once_per_boundary(self):
        owner = model("A_OS")
        command = request(fixture("A_OS")[0].dt, "bounded-capture")
        capture = geometry.GeometryStageInputs.from_payload
        with (patch.object(geometry.GeometryStageInputs, "from_payload", wraps=capture) as captures,
              patch.object(codec, "_read_contract_schema", wraps=codec._read_contract_schema) as reads):
            result = owner.step_v4_input(command)
        self.assertTrue(result.committed, result.failure)
        self.assertEqual(captures.call_count, 1)
        self.assertEqual(reads.call_count, 4)
        self.assertIsNone(codec._OPERATION_CONTEXT.get())
        self.assertIsNone(evidence._scope())

    def test_asset_failure_at_publication_preserves_owned_state(self):
        owner = model("A_OS")
        before = owner.snapshot()
        command = request(fixture("A_OS")[0].dt, "changed-assets")
        read = codec._read_contract_schema
        reads = 0

        def changed():
            nonlocal reads
            reads += 1
            if codec._OPERATION_CONTEXT.get() is not None:
                raise codec.V4AssetError("changed installed asset")
            return read()

        with (patch.object(codec, "_read_contract_schema", side_effect=changed),
              self.assertRaisesRegex(codec.V4AssetError, "changed installed asset")):
            owner.step_v4_input(command)
        self.assertEqual(owner.snapshot(), before)
        self.assertIsNone(codec._OPERATION_CONTEXT.get())
        self.assertIsNone(evidence._scope())

    def test_public_schema_lookup_is_fresh_even_inside_operation(self):
        with (codec._operation_contract_assets(),
              patch.object(codec, "_read_contract_schema", side_effect=codec.V4AssetError("changed asset")),
              self.assertRaisesRegex(codec.V4AssetError, "changed asset")):
            codec.load_contract_schema()

    def test_unowned_stage_capture_uses_full_admission(self):
        inputs = fixture("A_OS")[0]
        with patch.object(geometry.GeometryStageInputs, "from_payload", wraps=geometry.GeometryStageInputs.from_payload) as captures:
            captured = geometry._capture_stage_inputs(inputs)
        self.assertEqual(captures.call_count, 1)
        self.assertIsNot(captured.geometry.reference, inputs.geometry.reference)
        self.assertEqual(captured.to_payload(), inputs.to_payload())

    def test_owned_stage_capture_retains_field_and_hodge_admission(self):
        inputs = geometry.GeometryStageInputs.from_payload(fixture("A_OS")[0].to_payload())
        with codec._operation_contract_assets(evidence._OperationEvidence()):
            self.assertFalse(evidence._owns_stage_reference(None))
            self.assertFalse(evidence._owns_stage_reference(inputs.geometry.reference))
            evidence._own_stage_reference(inputs.geometry.reference)
            for field, value in (("dt", float("nan")), ("step_index", -1), ("stage", "forged")):
                forged = replace(inputs)
                object.__setattr__(forged, field, value)
                with self.subTest(field=field), self.assertRaises(ValueError):
                    geometry._capture_stage_inputs(forged)
            forged = replace(inputs)
            object.__setattr__(forged.geometry.one_form_hodge, "matrix", ((-1.0,),))
            with self.assertRaises(ValueError):
                geometry._capture_stage_inputs(forged)

    def test_all_owned_pointer_writes_verify_before_swap(self):
        owner = model("A_OS")
        operation = owner._operation
        before = operation._owned
        state = owner.state
        command = request(fixture("A_OS")[0].dt, "central-publication")
        actions = (
            lambda: owner.step_v4_input(command),
            owner.reset,
            owner.rebase_reset_baseline,
            lambda: owner.set_state(state),
            lambda: setattr(operation, "_owned", before),
            lambda: object.__setattr__(operation, "_owned", before),
        )
        for action in actions:
            with (self.subTest(action=action),
                  patch.object(lifecycle, "_verify_contract_assets", side_effect=codec.V4AssetError("changed asset")),
                  self.assertRaisesRegex(codec.V4AssetError, "changed asset")):
                action()
            self.assertIs(operation._owned, before)
            self.assertIsNone(codec._OPERATION_CONTEXT.get())

    def test_publication_verification_and_swap_stay_inside_the_existing_lock(self):
        owner = model("A_OS")
        operation = owner._operation
        verify = lifecycle._verify_contract_assets
        observed = []

        def guarded():
            observed.append(operation._lock.locked())
            self.assertTrue(operation._lock.locked())
            return verify()

        actions = (
            lambda: owner.step_v4_input(request(fixture("A_OS")[0].dt, "locked-publication")),
            owner.reset,
            owner.rebase_reset_baseline,
            lambda: owner.set_state(owner.state),
        )
        with patch.object(lifecycle, "_verify_contract_assets", side_effect=guarded):
            for action in actions:
                action()
        self.assertEqual(observed, [True] * len(actions))

    def test_projection_rejects_an_unhandled_future_state_field(self):
        inputs = fixture("A_OS")[0]
        actual = lifecycle.fields(lifecycle.GRCV4LifecycleState)
        with (patch.object(lifecycle, "fields", return_value=actual + (SimpleNamespace(name="future_field"),)),
              self.assertRaisesRegex(codec.V4IdentityError, "cover every state field")):
            lifecycle._lifecycle_state(inputs, ())

    def test_receipt_evidence_is_frozen_and_canonical_layout_fails_closed(self):
        prefix = evidence._ReceiptEvidence.from_ids(RECEIPTS[:1])
        with self.assertRaises(FrozenInstanceError):
            prefix.count = 2
        before = prefix.identity(STATE)
        with (patch.object(codec, "canonical_json_bytes", return_value=b'{"changed_layout":[]}'),
              self.assertRaisesRegex(codec.V4IdentityError, "canonical lifecycle envelope layout")):
            prefix.identity(STATE)
        self.assertEqual(prefix.identity(STATE), before)

    def test_all_realizations_match_without_operation_reuse(self):
        def full(_scope, state, ids):
            return codec.payload_identity("lifecycle_envelope_payload", evidence._envelope(state, ids))

        for family in FAMILIES:
            with self.subTest(family=family):
                owner = model(family)
                other = model(family)
                dt = fixture(family)[0].dt
                for index, duration in enumerate((dt, dt, 0)):
                    command = request(duration, f"operation-evidence-{index}")
                    result = owner.step_v4_input(command)
                    with (patch.object(_MatrixFacts, "find", return_value=None),
                          patch.object(evidence._OperationEvidence, "lifecycle", full),
                          patch.object(geometry, "_owns_stage_reference", return_value=False),
                          patch.object(codec, "_load_contract_schema", side_effect=codec._read_contract_schema)):
                        expected = other.step_v4_input(command)
                    self.assertTrue(result.committed, result.failure)
                    self.assertEqual(result.to_canonical_bytes(), expected.to_canonical_bytes())
                    self.assertEqual(owner.snapshot(), other.snapshot())


if __name__ == "__main__":
    unittest.main()

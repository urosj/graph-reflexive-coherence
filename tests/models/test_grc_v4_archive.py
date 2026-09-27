"""Incremental private archive facts retain full import and rollback strictness."""

import unittest
from copy import deepcopy
from dataclasses import replace
from unittest.mock import patch

from pygrc.models import grc_v4_codec as codec
from pygrc.models import grc_v4_lifecycle as lifecycle
from pygrc.models.grc_v4_state import FrozenJSONMap
from tests.models.test_grc_v4_generic_lifecycle import FAMILIES, fixture, model, restore
from tests.models.test_grc_v4_lifecycle import request


class CheckedArchiveTests(unittest.TestCase):
    def test_all_families_check_only_the_new_commit(self):
        original = lifecycle._CheckedArchive._check_commits
        for family in FAMILIES:
            owner = model(family)
            groups = []

            def check(records, *args, groups=groups, **kwargs):
                groups.append(len(records))
                return original(records, *args, **kwargs)

            with self.subTest(family=family), patch.object(
                lifecycle._CheckedArchive, "_check_commits", staticmethod(check)
            ):
                for index in range(3):
                    result = owner.step_v4_input(request(fixture(family)[0].dt, f"archive-{index}"))
                    self.assertTrue(result.committed, result.failure)
                self.assertEqual(groups, [1, 1, 1])
            snapshot = owner.snapshot()
            self.assertNotIn("archive", snapshot)
            self.assertEqual(restore(snapshot).snapshot(), snapshot)

    def test_full_import_seeds_the_same_append_path(self):
        owner = model("C_OS")
        for index in range(3):
            self.assertTrue(owner.step_v4_input(request(0, f"seed-{index}")).committed)
        groups = []
        original = lifecycle._CheckedArchive._check_commits

        def check(records, *args, **kwargs):
            groups.append(len(records))
            return original(records, *args, **kwargs)

        with patch.object(lifecycle._CheckedArchive, "_check_commits", staticmethod(check)):
            clone = restore(owner.snapshot())
            self.assertTrue(clone.step_v4_input(request(0, "after-load")).committed)
        self.assertEqual(groups, [3, 1])
        self.assertEqual(restore(clone.snapshot()).snapshot(), clone.snapshot())

    def test_assignment_reset_and_rebase_keep_the_archive_fact(self):
        owner = model("A_CI_PC")
        self.assertTrue(owner.step_v4_input(request(0, "seed-admin")).committed)
        original_archive = owner._operation._owned.archive
        owner.set_state(owner.state)
        self.assertIs(owner._operation._owned.archive, original_archive)
        groups = []
        original = lifecycle._CheckedArchive._check_commits

        def check(records, *args, **kwargs):
            groups.append(len(records))
            return original(records, *args, **kwargs)

        with patch.object(lifecycle._CheckedArchive, "_check_commits", staticmethod(check)):
            owner.reset()
            owner.rebase_reset_baseline()
            self.assertTrue(owner.step_v4_input(request(0, "after-admin")).committed)
        self.assertEqual(groups, [1, 1, 1])
        self.assertEqual(restore(owner.snapshot()).snapshot(), owner.snapshot())

    def test_fact_mismatch_runs_full_validation_and_reestablishes_the_fact(self):
        owner = model("A_OS")
        for index in range(2):
            self.assertTrue(owner.step_v4_input(request(0, f"seed-fallback-{index}")).committed)
        old = owner._operation._owned
        owner._operation._owned = replace(old, archive=replace(old.archive, prefix=replace(old.archive.prefix, binding=b"mismatch")))
        groups = []
        original = lifecycle._CheckedArchive._check_commits

        def check(records, *args, **kwargs):
            groups.append(len(records))
            return original(records, *args, **kwargs)

        with patch.object(lifecycle._CheckedArchive, "_check_commits", staticmethod(check)):
            self.assertTrue(owner.step_v4_input(request(0, "reestablish-fact")).committed)
            self.assertTrue(owner.step_v4_input(request(0, "reuse-new-fact")).committed)
        self.assertEqual(groups, [3, 1])
        self.assertEqual(restore(owner.snapshot()).snapshot(), owner.snapshot())

    def test_forced_public_receipt_mutation_cannot_reuse_or_poison_the_fact(self):
        owner = model("C_OS")
        self.assertTrue(owner.step_v4_input(request(0, "seed-alias")).committed)
        publication = owner._operation._owned
        archive = publication.archive
        exposed = owner.state.lifecycle.receipt_ledger[0]
        original_items = exposed._items
        changed = FrozenJSONMap(exposed.to_dict() | {"commit_id": "grc-commit-sha256:" + "0" * 64})
        object.__setattr__(exposed, "_items", changed._items)
        try:
            with self.assertRaises(codec.V4IdentityError):
                owner.step_v4_input(request(0, "reject-changed-prefix"))
            self.assertIs(owner._operation._owned, publication)
            self.assertIs(owner._operation._owned.archive, archive)
        finally:
            object.__setattr__(exposed, "_items", original_items)
        self.assertTrue(owner.step_v4_input(request(0, "after-alias-restored")).committed)
        self.assertEqual(restore(owner.snapshot()).snapshot(), owner.snapshot())

    def test_failed_publication_does_not_change_the_prior_indexes(self):
        owner = model("A_OS")
        self.assertTrue(owner.step_v4_input(request(0, "seed-rollback")).committed)
        publication = owner._operation._owned
        archive = publication.archive
        saved = deepcopy((archive.science.components, archive.science.clocks))
        error = RuntimeError("publication control")
        with (
            patch.object(lifecycle, "_OwnedCOS", side_effect=error),
            self.assertRaises(RuntimeError) as caught,
        ):
            owner.step_v4_input(request(0, "failed-publish"))
        self.assertIs(caught.exception, error)
        self.assertIs(owner._operation._owned, publication)
        self.assertEqual((archive.science.components, archive.science.clocks), saved)
        self.assertTrue(owner.step_v4_input(request(0, "retry-publish")).committed)

    def test_public_binder_captures_request_before_reading_caller_ledgers(self):
        from pygrc.models.grc_v4 import GRCV4StepRequestInput
        from pygrc.models.grc_v4_step import bind_step_result
        from tests.models.test_grc_v4_step import positive_fixture

        result, arguments = positive_fixture()
        original_id = arguments["request"].operation_id
        incoming = GRCV4StepRequestInput.from_payload(
            arguments["request"].to_payload() | {"operation_id": "foreign-before-capture"}
        )

        class MutatingLedger(dict):
            def items(self):
                object.__setattr__(incoming, "operation_id", original_id)
                return super().items()

        rows = [row.to_payload() if hasattr(row, "to_payload") else row
                for row in arguments["pre_ledger"]]
        rows[0] = MutatingLedger(rows[0])
        with self.assertRaises(codec.V4IdentityError):
            bind_step_result(result, **(arguments | {"request": incoming, "pre_ledger": rows}))

    def test_private_receipts_are_not_exposed_in_state_or_result(self):
        owner = model("A_OS")
        result = owner.step_v4_input(request(0, "capture-private-receipts"))
        self.assertTrue(result.committed)
        archive = owner._operation._owned.archive
        private = archive.receipts[0]
        self.assertIsNot(private, result.emitted_receipts[0])
        before = owner.snapshot()
        object.__setattr__(result.emitted_receipts[0], "receipt_id", "forged-result")
        self.assertEqual(owner.snapshot(), before)
        self.assertTrue(owner.step_v4_input(request(0, "after-result-forgery")).committed)
        self.assertEqual(restore(owner.snapshot()).snapshot(), owner.snapshot())

    def test_prefix_tokens_do_not_confuse_forbidden_or_changed_scalars(self):
        token = lifecycle._CheckedArchive._token
        self.assertEqual(token({"n": 1}), token({"n": 1.0}))
        self.assertNotEqual(token({"n": 1}), token({"n": True}))
        self.assertNotEqual(token({"n": 0.0}), token({"n": -0.0}))
        self.assertNotEqual(token({"n": float(2**53)}), token({"n": 2**53}))
        self.assertNotEqual(token({"n": 1.0}), token({"n": float("inf")}))
        self.assertNotEqual(token({"n": 1.0}), token({"n": float("nan")}))
        self.assertEqual(token({"a": [1], "b": False}), token({"b": False, "a": (1,)}))
        detached = {"nested": [1, {"flag": True}]}
        saved = token(detached)
        detached["nested"][1]["flag"] = False
        self.assertNotEqual(token(detached), saved)

    def test_warm_archive_still_checks_assets(self):
        owner = model("A_OS")
        append = lifecycle._CheckedArchive.append
        captured = []

        def capture(archive, **kwargs):
            captured.append((archive, kwargs))
            return append(archive, **kwargs)

        with patch.object(lifecycle._CheckedArchive, "append", capture):
            self.assertTrue(owner.step_v4_input(request(0, "capture-asset-guard")).committed)
        archive, arguments = captured[0]
        error = codec.V4AssetError("asset control")
        with (
            patch.object(codec, "_load_contract_schema", side_effect=error),
            self.assertRaises(codec.V4AssetError) as caught,
        ):
            archive.append(**arguments)
        self.assertIs(caught.exception, error)


if __name__ == "__main__":
    unittest.main()

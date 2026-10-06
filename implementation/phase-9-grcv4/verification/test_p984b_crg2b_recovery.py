"""Recovery must bind original evidence and reject forged checkpoint credit."""

import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

import p984b_crg2b_recheck as checks
import p984b_crg2b_resume as recovery

b = recovery.b


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.case = {"case_id": "one", "execution_budget_seconds": 900}
        self.manifest = b.seal({"cases": [self.case]})
        self.header = b.seal(
            {
                "manifest_digest": self.manifest["record_digest"],
                "cases": [],
                "shared": {"source": "original"},
                "native_runtime_executed": True,
                "user_accepted": False,
                "aggregate_closed": False,
            }
        )
        self.row = {
            "case_id": "one",
            "input_digest": b.digest(self.case),
            "case_passed": True,
            "first_failure": None,
        }

    def journal(self, row=None):
        return (
            b"\n".join(
                b.canonical_json_bytes(b.seal(x))
                for x in (self.header, self.row if row is None else row)
            )
            + b"\n"
        )

    def test_completed_prefix_preserves_exact_rows(self):
        header, rows = recovery.decode_journal(self.journal(), self.manifest)
        self.assertEqual(header, self.header)
        self.assertEqual(rows, [self.row])

    def test_partial_write_is_not_a_completed_case(self):
        with self.assertRaisesRegex(ValueError, "partial journal"):
            recovery.decode_journal(self.journal()[:-1], self.manifest)

    def test_rehashed_foreign_failed_and_changed_input_rows_reject(self):
        for changes in (
            {"case_id": "foreign"},
            {"case_passed": False},
            {"first_failure": {"stage": "event"}},
            {"input_digest": "false"},
        ):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                recovery.decode_journal(
                    self.journal({**self.row, **changes}), self.manifest
                )

    def test_unsealed_edit_and_extra_case_reject(self):
        raw = self.journal().replace(b'"case_passed":true', b'"case_passed":false')
        with self.assertRaises(ValueError):
            recovery.decode_journal(raw, self.manifest)
        with self.assertRaisesRegex(ValueError, "foreign journal"):
            recovery.decode_journal(
                self.journal() + b.canonical_json_bytes(b.seal(self.row)) + b"\n",
                self.manifest,
            )

    def test_prefix_validation_uses_retained_owner_without_numerical_rerun(self):
        with patch.object(
            recovery.r, "validate", return_value={"cases_passed": 1}
        ) as validate:
            recovery.validate_prefix(self.manifest, self.header, [self.row])
        manifest, result = validate.call_args.args
        self.assertEqual(result["manifest_digest"], manifest["record_digest"])
        self.assertEqual(result["shared"], self.header["shared"])
        self.assertEqual(result["cases"], [self.row])
        self.assertEqual(validate.call_args.kwargs, {})

    def test_checkpoint_rehash_cannot_change_source_subject_or_claims(self):
        context = {"shared_digest": "shared", "source_bindings": [{"sha256": "code"}]}
        check = {
            "case_id": "one",
            "case_digest": b.digest(self.row),
            "shared_digest": "shared",
            "successful_history_cells": 2,
            "interval_equations_recomputed": True,
            "native_trajectories_rerun": False,
        }
        record = b.seal({"context": context, "check": check})
        self.assertEqual(
            checks.check_checkpoint(record, context, self.case, self.row), check
        )
        for field, value in (
            ("case_digest", "forged"),
            ("shared_digest", "different"),
            ("interval_equations_recomputed", False),
            ("native_trajectories_rerun", True),
        ):
            wrong = deepcopy(record)
            wrong["check"][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                checks.check_checkpoint(b.seal(wrong), context, self.case, self.row)
        with self.assertRaisesRegex(ValueError, "source/subject"):
            checks.check_checkpoint(
                record, {**context, "source_bindings": []}, self.case, self.row
            )

    def test_numeric_one_is_not_a_boolean_checkpoint_claim(self):
        context = {"shared_digest": "shared"}
        check = {
            "case_id": "one",
            "case_digest": b.digest(self.row),
            "shared_digest": "shared",
            "successful_history_cells": 2,
            "interval_equations_recomputed": 1,
            "native_trajectories_rerun": False,
        }
        with self.assertRaisesRegex(ValueError, "case/scope"):
            checks.check_checkpoint(
                b.seal({"context": context, "check": check}),
                context,
                self.case,
                self.row,
            )

    def test_atomic_publication_refuses_overwriting_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "case.json"
            recovery.publish(path, self.row)
            with self.assertRaises(FileExistsError):
                recovery.publish(path, {"forged": True})
            self.assertEqual(json.loads(path.read_text()), self.row)
            self.assertEqual(list(Path(directory).iterdir()), [path])


if __name__ == "__main__":
    unittest.main()

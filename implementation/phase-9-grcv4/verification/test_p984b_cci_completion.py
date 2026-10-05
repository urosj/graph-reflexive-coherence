"""Operational continuation must not rewrite successes or scientific inputs."""

from copy import deepcopy
import unittest
from unittest.mock import patch

import p984b_cci_completion as c


class CompletionTests(unittest.TestCase):
    def test_only_execution_budget_and_case_label_change(self):
        old, execution = c.predecessor()
        new = c.make_manifest()
        self.assertEqual(new["cases"][:8], old["cases"][:8])
        self.assertEqual(new["initial_inputs"], old["initial_inputs"])
        self.assertEqual(new["expected_source"], old["expected_source"])
        for a, b in zip(old["cases"][8:], new["cases"][8:], strict=True):
            self.assertEqual(
                b,
                {
                    **a,
                    "case_id": a["case_id"] + "-BUDGET480",
                    "execution_budget_seconds": 480,
                },
            )
        self.assertTrue(execution["cases"][8]["event_committed"])
        self.assertFalse(execution["cases"][8]["case_passed"])

    def test_reuse_and_timeout_cannot_be_rewritten(self):
        manifest = c.make_manifest()
        _, old = c.predecessor()
        value = dict(
            shared=old["shared"],
            cases=old["cases"][:8],
            execution_partition=dict(
                retained_cases=8,
                newly_executed_cases=8,
                retained_source_beats=1,
                new_source_beats=0,
                predecessor_record_digest=old["record_digest"],
            ),
            original_first_failure=old["cases"][8]["first_failure"],
        )
        with patch.object(c.r, "validate", return_value={}):
            c.validate(manifest, value)
            for key in (
                "shared",
                "cases",
                "execution_partition",
                "original_first_failure",
            ):
                wrong = deepcopy(value)
                wrong[key] = [] if key == "cases" else {}
                with self.subTest(key=key), self.assertRaises(ValueError):
                    c.validate(manifest, wrong)


if __name__ == "__main__":
    unittest.main(verbosity=2)

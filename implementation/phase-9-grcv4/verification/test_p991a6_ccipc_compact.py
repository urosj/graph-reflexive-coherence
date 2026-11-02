"""Compact mathematical witnesses reject corruptions without native simulation."""

import json
import lzma
import unittest
from copy import deepcopy
from hashlib import sha256
from unittest.mock import patch

from flint import fmpq as Q
from p991a6_ccipc_compact import ROOT, campaign, context, full_samples, read_stream

from pygrc.models.grc_v4_spark_ccipc import SparkCCIPCKernel


class CCIPCCompactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.e = context()
        with lzma.open(ROOT / campaign.RECORD, "rt") as f:
            v = json.load(f)
        cls.full = (
            next(full_samples("current"))
            if "storage" in v
            else next(read_stream("current"))
        )
        cls.row = cls.e.project(cls.full)
        cls.before = cls.e.initial("current")

    def test_exact_state_and_closed_shared_declaration(self):
        self.assertEqual(
            self.e.state(self.row).to_payload(), self.full["stage"]["after"]
        )
        bad = deepcopy(self.full)
        bad["stage"]["consumed_read"]["root_domain"]["carrier_radius"] = "1/64"
        with self.assertRaisesRegex(ValueError, "shared root domain"):
            self.e.project(bad)
        bad = deepcopy(self.row)
        bad["Z"].pop()
        with self.assertRaisesRegex(ValueError, "complete compact C/Z"):
            self.e.verify(self.before, bad, "current")

    def test_independent_verifier_uses_no_native_step_or_read(self):
        with (
            patch.object(
                SparkCCIPCKernel, "step", side_effect=AssertionError("native step")
            ),
            patch.object(
                SparkCCIPCKernel, "_root", side_effect=AssertionError("native root")
            ),
            patch.object(
                SparkCCIPCKernel,
                "_admitted_read",
                side_effect=AssertionError("native read"),
            ),
        ):
            after, report = self.e.verify(self.before, self.row, "current")
        self.assertEqual(after.to_payload(), self.full["stage"]["after"])
        self.assertLessEqual(
            Q(report["full_step_error_upper"]),
            Q(self.e.certs["current"].proof["full_step_error"]),
        )

    def test_semantic_witness_corruptions_reject_after_rebinding(self):
        cases = []
        bad = deepcopy(self.row)
        bad["roots"][0]["root_error"] = ["0", "0"]
        cases.append((bad, "Banach error"))
        bad = deepcopy(self.row)
        bad["roots"][0]["proposal_residual"] = ["0", "0"]
        cases.append((bad, "proposal residual"))
        bad = deepcopy(self.row)
        bad["roots"][0]["current_midpoint"][-1] = str(
            Q(bad["roots"][0]["current_midpoint"][-1]) + Q(1, 2**180)
        )
        cases.append((bad, "current midpoint"))
        bad = deepcopy(self.row)
        bad["writer_midpoint"][-1] = str(Q(bad["writer_midpoint"][-1]) + Q(1, 2**210))
        cases.append((bad, "exponential writer midpoint"))
        bad = deepcopy(self.row)
        bad["C"][-1] = str(Q(bad["C"][-1]) + Q(1, 2**128))
        bad["C"][0] = str(Q(bad["C"][0]) - Q(1, 2**128))
        cases.append((bad, "incidence write"))
        bad = deepcopy(self.row)
        bad["roots"][1] = deepcopy(bad["roots"][0])
        cases.append((bad, "proposal residual"))
        for bad, message in cases:
            subjects = [
                sha256(s.to_canonical_bytes()).hexdigest()
                for s in (self.before, self.e.state(bad))
            ]
            bad["staging"]["read_inputs"] = subjects
            for witness, digest in zip(bad["roots"], subjects, strict=True):
                witness["subject_digest"] = digest
            with (
                self.subTest(message=message),
                self.assertRaisesRegex(ValueError, message),
            ):
                self.e.verify(self.before, bad, "current")

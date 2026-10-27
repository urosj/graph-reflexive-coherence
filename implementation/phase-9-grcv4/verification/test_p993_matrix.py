"""Pressure catalog completeness, accepted identity binding and scope projection."""

from copy import deepcopy
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import p993_matrix as m

ROOT = Path(__file__).resolve().parents[3]


class MatrixTests(unittest.TestCase):
    def test_complete_reconciliation_without_native_execution(self):
        from pygrc.models.grc_9_v4_legacy import GRC9V4LegacyDelegate

        with patch.object(
            GRC9V4LegacyDelegate, "step", side_effect=AssertionError("no native run")
        ):
            v = m.check(ROOT)
            view = m.status(ROOT)
        self.assertEqual(
            v["counts"],
            dict(
                total=40,
                bounded_accepted=16,
                unselected_not_executed=24,
                failed=0,
                unaccounted=0,
            ),
        )
        self.assertEqual(len({r["contract_id"] for r in v["cells"]}), 40)
        self.assertFalse(view["matrix_reconciliation"]["user_accepted"])
        self.assertTrue(
            view["user_accepted"]
        )  # Original 9.2 decision remains separate.
        for r in v["cells"]:
            if r["disposition"] == "unselected_not_executed":
                self.assertIsNone(r["execution"])
                self.assertIsNone(r["acceptance"])
                self.assertIsNone(r["complete_profile_id"])
                self.assertIsNone(r["model_identity"])

    def test_rehashed_matrix_cannot_omit_duplicate_relabel_or_promote(self):
        good = m.check(ROOT)
        changes = [
            ("missing", lambda v: v["cells"].pop()),
            ("duplicate", lambda v: v["cells"].__setitem__(1, deepcopy(v["cells"][0]))),
            ("contract", lambda v: v["cells"][0].__setitem__("contract_id", "other")),
            (
                "profile",
                lambda v: v["cells"][0].__setitem__("complete_profile_id", "other"),
            ),
            ("model", lambda v: v["cells"][0].__setitem__("model_identity", "other")),
            (
                "evidence",
                lambda v: v["cells"][0]["execution"].__setitem__(
                    "record_digest", "0" * 64
                ),
            ),
            (
                "acceptance",
                lambda v: v["cells"][0]["acceptance"].__setitem__("cell_id", "other"),
            ),
            ("count", lambda v: v["counts"].__setitem__("bounded_accepted", 40)),
            ("support", lambda v: v["new_runtime_support"].append("A_OS")),
        ]
        for key in (
            "user_accepted",
            "native_execution",
            "aggregate_closed",
            "full_GRC9V4_conformance",
            "public_API_implemented",
            "crossings_executed",
        ):
            changes.append((key, lambda v, k=key: v.__setitem__(k, True)))
        for name, alter in changes:
            with self.subTest(name=name):
                v = deepcopy(good)
                alter(v)
                with self.assertRaises(ValueError):
                    m.check(ROOT, m.c.seal(v))

    def test_catalog_missing_duplicate_or_wrong_surface_rejects(self):
        original = json.loads((ROOT / m.CATALOG).read_bytes())
        read = Path.read_bytes
        for kind in (
            "missing_family",
            "duplicate_family",
            "missing_surface",
            "wrong_surface",
        ):
            v = deepcopy(original)
            rows = v["disabled_compatibility"]["matrix"]
            if kind == "missing_family":
                rows.pop()
            elif kind == "duplicate_family":
                rows[1] = deepcopy(rows[0])
            elif kind == "missing_surface":
                rows[0].pop("state")
            else:
                rows[0]["state"] = rows[0]["transition"]

            def altered(path, value=v):
                return (
                    json.dumps(value).encode()
                    if path == ROOT / m.CATALOG
                    else read(path)
                )

            with self.subTest(kind=kind), patch.object(Path, "read_bytes", altered):
                with self.assertRaises(ValueError):
                    m.catalog(ROOT)

    def test_projection_cannot_promote_unselected_or_hide_cells(self):
        good = m.acceptance.status(ROOT)
        for kind in ("promote", "omit", "duplicate"):
            v = deepcopy(good)
            if kind == "promote":
                next(r for r in v["cells"] if r["state"] == "unselected")["state"] = (
                    "bounded_accepted"
                )
            elif kind == "omit":
                v["cells"].pop()
            else:
                v["cells"][1] = deepcopy(v["cells"][0])
            with (
                self.subTest(kind=kind),
                patch.object(m.acceptance, "status", return_value=v),
            ):
                with self.assertRaises(ValueError):
                    m.status(ROOT)


if __name__ == "__main__":
    unittest.main()

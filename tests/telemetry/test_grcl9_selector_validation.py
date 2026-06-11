"""Tests for corrected GRCL-9 selector validation."""

from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from pygrc import telemetry
from pygrc.telemetry.grcl9_selector_validation import (
    GRCL9SelectorResult,
    _SELECTORS,
    _pressure_boundary_growth_provenance,
    _run_selector,
    _score_lane,
)


class GRCL9SelectorValidationTest(unittest.TestCase):
    def test_selector_validation_accepts_corrected_and_supersedes_legacy(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "grcl9" / "lowering"
            telemetry.run_grcl9_lowering_replay_session(
                session_id="S0001",
                output_root=root,
                source_mode="landscape_seed_examples",
                fixture_names=("corrected_front_growth_positive_high",),
                requested_steps=3,
            )
            telemetry.run_grcl9_lowering_replay_session(
                session_id="S0002",
                output_root=root,
                source_mode="legacy_growth_landscape_seed_examples",
                fixture_names=("growth_pressure_lambda_high",),
                requested_steps=1,
                force_legacy_growth=True,
            )

            with self.assertRaisesRegex(ValueError, "force-legacy-growth"):
                telemetry.run_grcl9_selector_validation(
                    session_id="S0003",
                    source_session_ids=("S0001", "S0002"),
                    output_root=root,
                )

            session = telemetry.run_grcl9_selector_validation(
                session_id="S0003",
                source_session_ids=("S0001", "S0002"),
                output_root=root,
                force_legacy_growth=True,
            )

            self.assertEqual("S0003", session.session_id)
            self.assertEqual(2, len(session.validations))
            self.assertEqual(1, session.accepted_count)
            self.assertEqual(1, session.superseded_legacy_count)
            self.assertEqual(0, session.missing_surface_count)
            self.assertTrue(session.manifest_path.exists())
            self.assertTrue(session.report_path.exists())
            self.assertTrue(session.summary_path.exists())

            by_lane = {item.lane_name: item for item in session.validations}
            corrected = by_lane["corrected_front_growth_positive_high"]
            self.assertEqual("accepted", corrected.evidence_status)
            self.assertEqual("strong_candidate", corrected.confidence_label)
            self.assertIn("front_capacity_mode", corrected.passed_selector_ids)
            self.assertIn(
                "front_growth_provenance_consistent",
                corrected.passed_selector_ids,
            )
            self.assertIsNotNone(corrected.motif_id)

            legacy = by_lane["growth_pressure_lambda_high"]
            self.assertEqual(
                "legacy_broad_growth_non_evidence",
                legacy.evidence_status,
            )
            self.assertEqual("superseded_legacy", legacy.confidence_label)
            self.assertIsNone(legacy.motif_id)
            self.assertNotIn("front_capacity_mode", legacy.passed_selector_ids)

            manifest = _read_json(session.manifest_path)
            self.assertEqual("grcl9_selector_validation_v1", manifest["manifest_version"])
            self.assertEqual(1, len(manifest["motifs"]))
            self.assertEqual(1, len(manifest["legacy_records"]))
            session_manifest = _read_json(root / "sessions" / "S0003" / "session_manifest.json")
            self.assertTrue(session_manifest["force_legacy_growth"])
            self.assertEqual(["S0002"], session_manifest["legacy_source_session_ids"])

            summary = session.summary_path.read_text(encoding="utf-8")
            self.assertIn("Accepted corrected records: 1", summary)
            self.assertIn("Superseded legacy records: 1", summary)

    def test_selector_validation_output_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "grcl9" / "lowering"
            telemetry.run_grcl9_lowering_replay_session(
                session_id="S0001",
                output_root=root,
                source_mode="landscape_seed_examples",
                fixture_names=("corrected_front_growth_no_growth_low",),
                requested_steps=3,
            )

            telemetry.run_grcl9_selector_validation(
                session_id="S0002",
                source_session_ids=("S0001",),
                output_root=root,
            )
            first = (
                root
                / "sessions"
                / "S0002"
                / "reports"
                / "selector_validation_report.json"
            ).read_text(encoding="utf-8")
            telemetry.run_grcl9_selector_validation(
                session_id="S0002",
                source_session_ids=("S0001",),
                output_root=root,
            )
            second = (
                root
                / "sessions"
                / "S0002"
                / "reports"
                / "selector_validation_report.json"
            ).read_text(encoding="utf-8")

            self.assertEqual(first, second)

    def test_missing_surface_partial_pass_scores_ambiguous(self) -> None:
        score, label, status = _score_lane(
            {"legacy_broad_growth_non_evidence": False, "summary": {}},
            (
                GRCL9SelectorResult(
                    selector_id="replay_selector_report_passed",
                    passed=True,
                    field_path="selector_report.status",
                    observed_value="passed",
                ),
                GRCL9SelectorResult(
                    selector_id="front_capacity_mode",
                    passed=False,
                    field_path="family_extensions.grcl9.growth_parent_eligibility_mode",
                    observed_value=None,
                    failure_kind="missing_surface",
                ),
            ),
        )

        self.assertEqual((3, "ambiguous", "missing_surface"), (score, label, status))

    def test_pressure_boundary_selector_requires_declared_source_and_growth(self) -> None:
        passed, observed = _pressure_boundary_growth_provenance(
            {
                "expected_selector_ids": ("pressure_boundary_growth_provenance",),
                "event_counts_by_kind": {"growth": 1},
                "summary": {
                    "family_extensions": {
                        "grc9": {
                            "growth_summary": {
                                "front_capacity_growth_count": 1,
                                "pressure_boundary_growth_count": 1,
                            }
                        },
                        "grcl9": {
                            "growth_parent_eligibility_mode": "grc9_front_capacity",
                            "growth_parent_capacity_sources": {
                                "0": {
                                    "front_capacity_source": "pressure_boundary",
                                    "inactive_parent_port": 4,
                                }
                            }
                        },
                    }
                },
            }
        )

        self.assertTrue(passed)
        self.assertEqual("checked", observed["status"])
        self.assertEqual(1, observed["pressure_boundary_source_count"])
        self.assertEqual(1, observed["pressure_boundary_growth_count"])

    def test_pressure_boundary_selector_fails_without_growth(self) -> None:
        passed, observed = _pressure_boundary_growth_provenance(
            {
                "expected_selector_ids": ("pressure_boundary_growth_provenance",),
                "event_counts_by_kind": {"growth": 0},
                "summary": {
                    "family_extensions": {
                        "grc9": {
                            "growth_summary": {
                                "front_capacity_growth_count": 0,
                                "pressure_boundary_growth_count": 0,
                            }
                        },
                        "grcl9": {
                            "growth_parent_eligibility_mode": "grc9_front_capacity",
                            "growth_parent_capacity_sources": {
                                "0": {
                                    "front_capacity_source": "pressure_boundary",
                                    "inactive_parent_port": 4,
                                }
                            },
                        },
                    }
                },
            }
        )

        self.assertFalse(passed)
        self.assertEqual("checked", observed["status"])
        self.assertEqual(0, observed["growth_count"])

    def test_pressure_boundary_selector_reports_predicate_failed_without_growth(self) -> None:
        selector = next(
            item
            for item in _SELECTORS
            if item.selector_id == "pressure_boundary_growth_provenance"
        )

        result = _run_selector(
            selector,
            {
                "expected_selector_ids": ("pressure_boundary_growth_provenance",),
                "event_counts_by_kind": {"growth": 0},
                "summary": {
                    "family_extensions": {
                        "grc9": {
                            "growth_summary": {
                                "front_capacity_growth_count": 0,
                                "pressure_boundary_growth_count": 0,
                            }
                        },
                        "grcl9": {
                            "growth_parent_eligibility_mode": "grc9_front_capacity",
                            "growth_parent_capacity_sources": {
                                "0": {
                                    "front_capacity_source": "pressure_boundary",
                                    "inactive_parent_port": 4,
                                }
                            },
                        },
                    }
                },
            },
        )

        self.assertFalse(result.passed)
        self.assertEqual("predicate_failed", result.failure_kind)

    def test_pressure_boundary_selector_fails_outside_front_capacity_mode(self) -> None:
        passed, observed = _pressure_boundary_growth_provenance(
            {
                "expected_selector_ids": ("pressure_boundary_growth_provenance",),
                "event_counts_by_kind": {"growth": 1},
                "summary": {
                    "family_extensions": {
                        "grc9": {
                            "growth_summary": {
                                "front_capacity_growth_count": 1,
                                "pressure_boundary_growth_count": 1,
                            }
                        },
                        "grcl9": {
                            "growth_parent_eligibility_mode": "legacy_any_inactive_port",
                            "growth_parent_capacity_sources": {
                                "0": {
                                    "front_capacity_source": "pressure_boundary",
                                    "inactive_parent_port": 4,
                                }
                            },
                        },
                    }
                },
            }
        )

        self.assertFalse(passed)
        self.assertEqual(
            "legacy_any_inactive_port",
            observed["growth_parent_eligibility_mode"],
        )

    def test_pressure_boundary_selector_is_neutral_without_expected_selector(self) -> None:
        passed, observed = _pressure_boundary_growth_provenance(
            {
                "expected_selector_ids": (),
                "event_counts_by_kind": {"growth": 0},
                "summary": {"family_extensions": {}},
            }
        )

        self.assertTrue(passed)
        self.assertEqual("not_applicable", observed["status"])


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

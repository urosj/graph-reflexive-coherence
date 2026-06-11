"""Tests for GRCL-9V3 lowered-source selector validation."""

from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from pygrc import telemetry
from pygrc.landscapes.extensions.grcl9v3 import (
    GRCL9V3_SELECTOR_EXPANSION_VERSION,
    GRCL9V3_SOURCE_SELECTOR_EXPANSIONS,
)
from pygrc.telemetry.grcl9v3_selector_validation import (
    GRCL9V3SelectorResult,
    _failure_kind,
    _growth_before_collapse_observed,
    _relay_roles,
    _score_results,
    _selector_by_id,
    _validate_lane,
)


class GRCL9V3SelectorValidationTest(unittest.TestCase):
    def test_selector_validation_writes_source_linked_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            telemetry.run_grcl9v3_lowering_replay_session(
                session_id="S0001",
                output_root=root,
                fixture_names=(
                    "growth_pressure_positive_control",
                    "quiescent_hybrid_control_no_event_control",
                ),
                requested_steps=1,
            )

            session = telemetry.run_grcl9v3_selector_validation(
                session_id="S0002",
                source_session_ids=("S0001",),
                output_root=root,
            )

            self.assertEqual("S0002", session.session_id)
            self.assertEqual(2, len(session.validations))
            self.assertTrue(session.manifest_path.exists())
            self.assertTrue(session.report_path.exists())
            self.assertTrue(session.summary_path.exists())

            report = _read_json(session.report_path)
            self.assertEqual("grcl9v3_selector_validation_v1", report["validation_version"])
            self.assertEqual(2, report["lane_count"])
            self.assertEqual(0, report["missing_surface_count"])

            by_lane = {item.lane_name: item for item in session.validations}
            growth = by_lane["growth_pressure_positive_control"]
            self.assertIn("growth_events", growth.source_expected_selector_ids)
            self.assertIn("growth_event_present", growth.expanded_selector_ids)
            self.assertIn("grcl9v3_source_fixture_link_present", growth.passed_selector_ids)
            self.assertIn("grcl9v3_expected_region_caches_present", growth.passed_selector_ids)
            self.assertTrue(growth.source_fixture_path.endswith("growth_pressure_positive_control.json"))
            self.assertEqual("strong_candidate", growth.confidence_label)

            quiescent = by_lane["quiescent_hybrid_control_no_event_control"]
            self.assertIn("no_lifecycle_events", quiescent.passed_selector_ids)
            self.assertEqual("strong_candidate", quiescent.confidence_label)

            manifest = _read_json(session.manifest_path)
            self.assertIn("selector_expansions", manifest)
            self.assertEqual(
                GRCL9V3_SELECTOR_EXPANSION_VERSION,
                manifest["selector_expansion_version"],
            )
            self.assertIn("growth_events", manifest["selector_expansions"])
            self.assertEqual(
                list(GRCL9V3_SOURCE_SELECTOR_EXPANSIONS["growth_events"]),
                manifest["selector_expansions"]["growth_events"],
            )
            self.assertEqual(
                ["growth_reduction_observed"],
                manifest["selector_expansions"]["growth_reduction"],
            )
            self.assertEqual(
                ["growth_before_collapse_observed"],
                manifest["selector_expansions"]["growth_before_collapse"],
            )
            self.assertEqual(
                ["learning_state_present", "collapsed_sink_recorded"],
                manifest["selector_expansions"]["basin_assignment_learning"],
            )
            self.assertEqual(
                [
                    "growth_child_later_collapsed_sink",
                    "collapsed_sink_later_growth_parent",
                    "full_growth_collapse_relay",
                ],
                manifest["selector_expansions"]["growth_collapse_relay_diagnostics"],
            )
            self.assertEqual(2, len(manifest["motifs"]))

            session_manifest = _read_json(root / "sessions" / "S0002" / "session_manifest.json")
            self.assertIn("--source-session-ids S0001", session_manifest["replay_command"])
            self.assertIn("S0001", session_manifest["source_session_ids"])

            summary = session.summary_path.read_text(encoding="utf-8")
            self.assertIn("Source selector ids remain vocabulary-facing", summary)

    def test_selector_validation_expands_hessian_probe_selectors(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            telemetry.run_grcl9v3_lowering_replay_session(
                session_id="S0013",
                output_root=root,
                fixture_names=(
                    "hessian_probe_anisotropic_spark_row_basis_control",
                    "hessian_probe_anisotropic_spark_weighted_least_squares_control",
                ),
                requested_steps=1,
                source_mode="hessian_backend_probe",
            )

            session = telemetry.run_grcl9v3_selector_validation(
                session_id="S0014",
                source_session_ids=("S0013",),
                output_root=root,
            )

            by_lane = {item.lane_name: item for item in session.validations}
            row_basis = by_lane["hessian_probe_anisotropic_spark_row_basis_control"]
            wls = by_lane[
                "hessian_probe_anisotropic_spark_weighted_least_squares_control"
            ]
            self.assertIn("hessian_row_basis_diagnostic", row_basis.source_expected_selector_ids)
            self.assertIn("hessian_row_basis_backend", row_basis.passed_selector_ids)
            self.assertIn(
                "hessian_weighted_least_squares_diagnostic",
                wls.source_expected_selector_ids,
            )
            self.assertIn(
                "hessian_weighted_least_squares_backend",
                wls.passed_selector_ids,
            )
            self.assertEqual("strong_candidate", row_basis.confidence_label)
            self.assertEqual("strong_candidate", wls.confidence_label)

    def test_event_order_selectors_use_step_before_event_index(self) -> None:
        lane = {
            "events": [
                {
                    "event_index": 9,
                    "step_index": 0,
                    "event_kind": "growth",
                    "payload": {"parent_node_id": 7, "child_node_id": 11},
                },
                {
                    "event_index": 0,
                    "step_index": 1,
                    "event_kind": "collapse",
                    "payload": {"collapsed_sink_id": 7},
                },
            ]
        }

        passed, observed = _growth_before_collapse_observed(lane)
        self.assertTrue(passed)
        self.assertEqual(0, observed["first_collapse_after_growth_event_index"])
        relay = _relay_roles(lane)
        self.assertEqual(0, relay["collapsed_sink_later_growth_parent_count"])

    def test_selector_validation_output_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            telemetry.run_grcl9v3_lowering_replay_session(
                session_id="S0001",
                output_root=root,
                fixture_names=("quiescent_hybrid_control_no_event_control",),
                requested_steps=1,
            )

            telemetry.run_grcl9v3_selector_validation(
                session_id="S0002",
                source_session_ids=("S0001",),
                output_root=root,
            )
            first = (root / "sessions" / "S0002" / "reports" / "selector_validation_report.json").read_text(
                encoding="utf-8"
            )
            telemetry.run_grcl9v3_selector_validation(
                session_id="S0002",
                source_session_ids=("S0001",),
                output_root=root,
            )
            second = (root / "sessions" / "S0002" / "reports" / "selector_validation_report.json").read_text(
                encoding="utf-8"
            )

            self.assertEqual(first, second)

    def test_missing_surface_failures_are_classified(self) -> None:
        selector = _selector_by_id("grcl9v3_expected_region_caches_present")
        lane = {
            "summary": {"family_extensions": {"grcl9v3": {}}},
            "steps": (),
            "events": (),
            "event_counts_by_kind": {},
        }

        passed, _ = selector.predicate(lane)

        self.assertFalse(passed)
        self.assertEqual("missing_surface", _failure_kind(lane, selector, passed))

    def test_pressure_boundary_selector_passes_with_source_metadata_and_growth(self) -> None:
        selector = _selector_by_id("pressure_boundary_growth_provenance_present")
        lane = {
            "summary": {
                "family_extensions": {
                    "grc9v3": {
                        "lifecycle_event_counts": {
                            "front_capacity_growth_count": 1,
                            "pressure_boundary_growth_count": 1,
                            "legacy_broad_growth_count": 0,
                        },
                    },
                    "grcl9v3": {
                        "growth_semantics_status": "front_capacity",
                        "growth_parent_eligibility_mode": "grcl9v3_front_capacity",
                        "growth_parent_capacity_sources": {
                            "7": {
                                "front_capacity_source": "pressure_boundary",
                                "inactive_parent_port": 6,
                            }
                        },
                        "front_growth_eligible_ports": {"7": [6]},
                        "expected_region_caches": {
                            "grcl9v3_expected_pressure_boundary_region_ids": [7]
                        },
                    }
                }
            },
            "steps": (),
            "events": (),
            "event_counts_by_kind": {"growth": 1},
        }

        passed, observed = selector.predicate(lane)

        self.assertTrue(passed)
        self.assertEqual("passed", _failure_kind(lane, selector, passed))
        self.assertEqual(1, observed["pressure_boundary_source_count"])
        self.assertEqual(1, observed["pressure_boundary_growth_count"])

    def test_pressure_boundary_selector_reports_missing_surface(self) -> None:
        selector = _selector_by_id("pressure_boundary_growth_provenance_present")
        lane = {
            "summary": {
                "family_extensions": {
                    "grcl9v3": {
                        "growth_semantics_status": "front_capacity",
                        "growth_parent_capacity_sources": {},
                    }
                }
            },
            "steps": (),
            "events": (),
            "event_counts_by_kind": {"growth": 1},
        }

        passed, _ = selector.predicate(lane)

        self.assertFalse(passed)
        self.assertEqual("missing_surface", _failure_kind(lane, selector, passed))

    def test_pressure_boundary_selector_fails_without_growth(self) -> None:
        selector = _selector_by_id("pressure_boundary_growth_provenance_present")
        lane = _pressure_boundary_selector_lane(
            event_growth_count=0,
            front_capacity_growth_count=0,
            pressure_boundary_growth_count=0,
            eligibility_mode="grcl9v3_front_capacity",
            source_label="pressure_boundary",
        )

        passed, observed = selector.predicate(lane)

        self.assertFalse(passed)
        self.assertEqual("predicate_failed", _failure_kind(lane, selector, passed))
        self.assertEqual(0, observed["growth_count"])

    def test_zero_growth_pressure_boundary_pipeline_returns_predicate_failed(self) -> None:
        lane = _pressure_boundary_selector_lane(
            event_growth_count=0,
            front_capacity_growth_count=0,
            pressure_boundary_growth_count=0,
            eligibility_mode="grcl9v3_front_capacity",
            source_label="pressure_boundary",
        )
        lane.update(
            {
                "source_session_id": "S0041",
                "lane_name": "pressure_boundary_growth_fixture",
                "fixture_name": "pressure_boundary_growth_fixture",
                "manifest_entry_id": "composed_grcl9v3_hybrid_composition_v1",
                "control_role": "positive_control",
                "run_id": "grcl9v3-pressure-boundary-zero-growth",
                "requested_steps": 1,
                "source_expected_selector_ids": (
                    "pressure_boundary_growth_provenance",
                ),
                "source_fixture_path": "source_fixtures/pressure_boundary.json",
                "lowered_state_path": "lowered_states/pressure_boundary.json",
                "telemetry_root": "lanes/pressure_boundary/telemetry",
            }
        )
        lane["summary"]["family_extensions"]["grc9v3"][
            "contract_version"
        ] = telemetry.GRC9V3_TELEMETRY_CONTRACT_VERSION
        lane["summary"]["family_extensions"]["grc9v3"]["lane_context"] = {
            "source_runtime_artifact": "source_fixtures/pressure_boundary.json"
        }
        lane["summary"]["family_extensions"]["grcl9v3"][
            "fixture_name"
        ] = "pressure_boundary_growth_fixture"

        validation = _validate_lane(lane)
        result = next(
            item
            for item in validation.selector_results
            if item.selector_id == "pressure_boundary_growth_provenance_present"
        )

        self.assertFalse(result.passed)
        self.assertEqual("predicate_failed", result.failure_kind)
        self.assertNotIn(
            "pressure_boundary_growth_provenance_present",
            validation.missing_surface_selector_ids,
        )

    def test_pressure_boundary_selector_fails_outside_front_capacity_mode(self) -> None:
        selector = _selector_by_id("pressure_boundary_growth_provenance_present")
        lane = _pressure_boundary_selector_lane(
            event_growth_count=1,
            front_capacity_growth_count=1,
            pressure_boundary_growth_count=1,
            eligibility_mode="legacy_any_inactive_port",
            source_label="pressure_boundary",
        )

        passed, observed = selector.predicate(lane)

        self.assertFalse(passed)
        self.assertEqual("predicate_failed", _failure_kind(lane, selector, passed))
        self.assertEqual(
            "legacy_any_inactive_port",
            observed["growth_parent_eligibility_mode"],
        )

    def test_pressure_boundary_selector_fails_for_generic_front_capacity_growth(self) -> None:
        selector = _selector_by_id("pressure_boundary_growth_provenance_present")
        lane = _pressure_boundary_selector_lane(
            event_growth_count=1,
            front_capacity_growth_count=1,
            pressure_boundary_growth_count=0,
            eligibility_mode="grcl9v3_front_capacity",
            source_label="spark_expansion_front",
        )

        passed, observed = selector.predicate(lane)

        self.assertFalse(passed)
        self.assertEqual("predicate_failed", _failure_kind(lane, selector, passed))
        self.assertEqual(0, observed["pressure_boundary_growth_count"])

    def test_missing_surface_partial_pass_scores_ambiguous(self) -> None:
        score, label = _score_results(
            ("contract_version_valid", "grcl9v3_expected_region_caches_present"),
            (
                GRCL9V3SelectorResult(
                    selector_id="contract_version_valid",
                    passed=True,
                    field_path="family_extensions.grc9v3.contract_version",
                    observed_value="phase_t_grc9v3_iter1_v1",
                ),
                GRCL9V3SelectorResult(
                    selector_id="grcl9v3_expected_region_caches_present",
                    passed=False,
                    field_path="family_extensions.grcl9v3.expected_region_caches",
                    observed_value=None,
                    failure_kind="missing_surface",
                ),
            ),
        )

        self.assertEqual((3, "ambiguous"), (score, label))


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _pressure_boundary_selector_lane(
    *,
    event_growth_count: int,
    front_capacity_growth_count: int,
    pressure_boundary_growth_count: int,
    eligibility_mode: str,
    source_label: str,
) -> dict:
    return {
        "summary": {
            "family_extensions": {
                "grc9v3": {
                    "lifecycle_event_counts": {
                        "front_capacity_growth_count": front_capacity_growth_count,
                        "pressure_boundary_growth_count": pressure_boundary_growth_count,
                        "legacy_broad_growth_count": (
                            event_growth_count - front_capacity_growth_count
                        ),
                    },
                },
                "grcl9v3": {
                    "growth_semantics_status": "front_capacity",
                    "growth_parent_eligibility_mode": eligibility_mode,
                    "growth_parent_capacity_sources": {
                        "7": {
                            "front_capacity_source": source_label,
                            "inactive_parent_port": 6,
                        }
                    },
                    "front_growth_eligible_ports": {"7": [6]},
                    "expected_region_caches": {
                        "grcl9v3_expected_pressure_boundary_region_ids": [7]
                    },
                },
            }
        },
        "steps": (),
        "events": (),
        "event_counts_by_kind": {"growth": event_growth_count},
    }


if __name__ == "__main__":
    unittest.main()

"""Tests for corrected GRC9 growth catalog generation."""

from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from pygrc.discovery import (
    GRC9_CORRECTED_GROWTH_CATALOG_VERSION,
    run_grc9_corrected_growth_catalog,
)
from pygrc.discovery.grc9_corrected_growth_catalog import (
    review_corrected_grc9_growth_lane,
)


class GRC9CorrectedGrowthCatalogTest(unittest.TestCase):
    def test_lane_review_accepts_only_front_capacity_growth(self) -> None:
        lane = {
            "artifact_root": "lane/root",
            "lane_name": "front_capacity_growth_positive_control",
            "event_counts_by_kind": {"growth": 1},
            "run_id": "run-1",
            "requested_steps": 3,
        }
        run_summary = _run_summary(mode="grc9_front_capacity", growth=1, front=1, legacy=0)
        events = (_growth_event(front=True, legacy=False),)

        record = review_corrected_grc9_growth_lane(
            source_session_id="S9001",
            lane=lane,
            run_summary=run_summary,
            events=events,
            superseded=(),
        )

        self.assertEqual("accepted_corrected_growth", record["review_status"])
        self.assertEqual(
            1,
            record["front_capacity_evidence"]["front_capacity_growth_count"],
        )
        self.assertEqual([], record["failure_reasons"])

    def test_lane_review_rejects_legacy_growth(self) -> None:
        lane = {
            "artifact_root": "lane/root",
            "lane_name": "legacy_growth",
            "event_counts_by_kind": {"growth": 1},
        }
        run_summary = _run_summary(
            mode="legacy_any_inactive_port",
            growth=1,
            front=0,
            legacy=1,
        )
        events = (_growth_event(front=False, legacy=True),)

        record = review_corrected_grc9_growth_lane(
            source_session_id="S9001",
            lane=lane,
            run_summary=run_summary,
            events=events,
            superseded=(),
        )

        self.assertEqual("rejected", record["review_status"])
        self.assertIn(
            "growth parent eligibility mode is not grc9_front_capacity",
            record["failure_reasons"],
        )

    def test_runner_writes_corrected_growth_catalog_with_supersession_links(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "outputs" / "grc9" / "phenomenology_discovery" / "sessions"
            source_root = root / "S9001"
            _write_source_lane(
                source_root=source_root,
                lane_name="front_capacity_growth_positive_control",
                run_summary=_run_summary(
                    mode="grc9_front_capacity",
                    growth=1,
                    front=1,
                    legacy=0,
                ),
                events=[_growth_event(front=True, legacy=False)],
            )
            _write_source_lane(
                source_root=source_root,
                lane_name="front_capacity_growth_zero_birth_control",
                run_summary=_run_summary(
                    mode="grc9_front_capacity",
                    growth=0,
                    front=0,
                    legacy=0,
                ),
                events=[],
            )
            _write_source_lane(
                source_root=source_root,
                lane_name="legacy_growth",
                run_summary=_run_summary(
                    mode="legacy_any_inactive_port",
                    growth=1,
                    front=0,
                    legacy=1,
                ),
                events=[_growth_event(front=False, legacy=True)],
            )
            classification_path = Path(temp_dir) / "classification.json"
            _write_json(
                classification_path,
                {
                    "superseded_records": [
                        {
                            "family": "grc9",
                            "record_name": "growth_pressure_lambda_high",
                            "old_motif_id": "old-high",
                        },
                        {
                            "family": "grc9",
                            "record_name": "growth_pressure_lambda_low",
                            "old_motif_id": "old-low",
                        },
                    ]
                },
            )

            session = run_grc9_corrected_growth_catalog(
                session_id="S9002",
                discovery_session_root=root,
                source_session_ids=("S9001",),
                growth_classification_path=classification_path,
            )

            catalog = _read_json(session.catalog_path)
            self.assertEqual(
                GRC9_CORRECTED_GROWTH_CATALOG_VERSION,
                catalog["catalog_version"],
            )
            self.assertEqual(1, session.accepted_growth_count)
            self.assertEqual(1, session.accepted_control_count)
            self.assertEqual(1, session.rejected_count)
            self.assertEqual(2, session.supersession_link_count)
            growth = catalog["accepted_corrected_growth_motifs"][0]
            control = catalog["accepted_corrected_control_motifs"][0]
            self.assertEqual(["old-high"], growth["supersedes_old_motif_ids"])
            self.assertEqual(["old-low"], control["supersedes_old_motif_ids"])
            self.assertEqual(0, catalog["summary"]["accepted_legacy_broad_growth_count"])
            self.assertTrue((session.session_root / "session_manifest.json").exists())
            self.assertTrue((root.parent / "ExperimentalLog.md").exists())

    def test_runner_is_exported_from_discovery_package(self) -> None:
        from pygrc.discovery.grc9_corrected_growth_catalog import (
            run_grc9_corrected_growth_catalog as direct_runner,
        )

        self.assertIs(run_grc9_corrected_growth_catalog, direct_runner)


def _run_summary(*, mode: str, growth: int, front: int, legacy: int) -> dict:
    return {
        "identity": {"run_id": "run-id"},
        "family_extensions": {
            "grc9": {
                "backend_summary": {"growth_parent_eligibility_mode": mode},
                "growth_summary": {
                    "growth_count": growth,
                    "front_capacity_growth_count": front,
                    "legacy_broad_growth_count": legacy,
                    "lowest_port_attachment_count": front,
                },
                "lifecycle_event_counts": {"growth_count": growth},
            }
        },
    }


def _growth_event(*, front: bool, legacy: bool) -> dict:
    return {
        "event_kind": "growth",
        "family_extensions": {
            "grc9": {
                "growth_evidence": {
                    "parent_eligibility_mode": (
                        "grc9_front_capacity" if front else "legacy_any_inactive_port"
                    ),
                    "parent_capacity_source": (
                        "spark_refinement_boundary_front" if front else "legacy_any_inactive_port"
                    ),
                    "front_growth_provenance_present": front,
                    "legacy_broad_growth": legacy,
                    "selected_parent_port": 3,
                    "birth_probability": 1.0,
                }
            }
        },
    }


def _write_source_lane(
    *,
    source_root: Path,
    lane_name: str,
    run_summary: dict,
    events: list[dict],
) -> None:
    artifact_root = source_root / "generated_lanes" / lane_name
    telemetry_root = artifact_root / "telemetry"
    telemetry_root.mkdir(parents=True, exist_ok=True)
    _write_json(telemetry_root / "run_summary.json", run_summary)
    _write_text(
        telemetry_root / "events.jsonl",
        "".join(json.dumps(event, sort_keys=True) + "\n" for event in events),
    )
    _write_text(telemetry_root / "steps.jsonl", "")
    (telemetry_root / "graph_checkpoints").mkdir(parents=True, exist_ok=True)
    _write_json(telemetry_root / "graph_checkpoints" / "index.json", {})
    report_path = source_root / "reports" / "run_report.json"
    if report_path.exists():
        report = _read_json(report_path)
    else:
        report = {"session_id": source_root.name, "lanes": []}
    report["lanes"].append(
        {
            "artifact_root": str(artifact_root),
            "lane_name": lane_name,
            "seed_name": lane_name,
            "profile": "test_profile",
            "requested_steps": 3,
            "run_id": f"run-{lane_name}",
            "event_counts_by_kind": {"growth": len(events)} if events else {},
        }
    )
    _write_json(report_path, report)


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

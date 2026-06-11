"""Tests for corrected GRCL-9 growth catalog generation."""

from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from pygrc.telemetry import (
    GRCL9_CORRECTED_GROWTH_CATALOG_VERSION,
    run_grcl9_corrected_growth_catalog,
)
from pygrc.telemetry.grcl9_corrected_growth_catalog import (
    review_corrected_grcl9_growth_record,
)


class GRCL9CorrectedGrowthCatalogTest(unittest.TestCase):
    def test_record_review_accepts_front_capacity_source_growth(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            motif = _write_lane(root, "corrected_cell_growth", growth=1, front=1, legacy=0)

            record = review_corrected_grcl9_growth_record(motif=motif)

            self.assertEqual("accepted_corrected_growth", record["review_status"])
            self.assertEqual(
                "grc9_front_capacity",
                record["front_capacity_evidence"]["grcl9_growth_parent_eligibility_mode"],
            )
            self.assertEqual(1, record["front_capacity_evidence"]["growth_event_row_count"])
            self.assertEqual([], record["failure_reasons"])

    def test_record_review_rejects_legacy_growth_source(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            motif = _write_lane(
                root,
                "legacy_cell_growth",
                growth=1,
                front=0,
                legacy=1,
                mode="legacy_any_inactive_port",
                selector_ids=("replay_selector_report_passed",),
            )

            record = review_corrected_grcl9_growth_record(motif=motif)

            self.assertEqual("rejected", record["review_status"])
            self.assertIn(
                "required front-capacity selector ids did not pass",
                record["failure_reasons"],
            )
            self.assertIn(
                "GRCL-9 growth parent eligibility mode is not grc9_front_capacity",
                record["failure_reasons"],
            )

    def test_runner_publishes_catalog_and_links_superseded_records(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "outputs" / "grcl9" / "lowering"
            source_session = root / "sessions" / "S9101"
            growth = _write_lane(
                source_session,
                "corrected_cell_growth",
                growth=1,
                front=1,
                legacy=0,
                source_session_id="S9101",
            )
            control = _write_lane(
                source_session,
                "corrected_cell_no_growth",
                growth=0,
                front=0,
                legacy=0,
                source_session_id="S9101",
                has_growth_construct=False,
            )
            rejected = _write_lane(
                source_session,
                "legacy_cell_growth",
                growth=1,
                front=0,
                legacy=1,
                mode="legacy_any_inactive_port",
                source_session_id="S9101",
                selector_ids=("replay_selector_report_passed",),
            )
            selector_manifest = root / "sessions" / "S9102" / "selector_manifest.json"
            _write_json(
                selector_manifest,
                {
                    "source_session_ids": ["S9101"],
                    "motifs": [growth, control, rejected],
                },
            )
            classification_path = root / "sessions" / "S9103" / "growth_record_classification.json"
            _write_json(
                classification_path,
                {
                    "superseded_records": [
                        {
                            "family": "grcl9",
                            "record_name": "cell_growth",
                            "old_motif_id": "old-growth",
                        },
                        {
                            "family": "grcl9",
                            "record_name": "cell_no_growth",
                            "old_motif_id": "old-control",
                        },
                    ]
                },
            )

            session = run_grcl9_corrected_growth_catalog(
                session_id="S9104",
                output_root=root,
                selector_manifest_path=selector_manifest,
                growth_classification_path=classification_path,
            )

            catalog = _read_json(session.catalog_path)
            self.assertEqual(
                GRCL9_CORRECTED_GROWTH_CATALOG_VERSION,
                catalog["catalog_version"],
            )
            self.assertEqual(1, session.accepted_growth_count)
            self.assertEqual(1, session.accepted_control_count)
            self.assertEqual(1, session.rejected_count)
            self.assertEqual(2, session.supersession_link_count)
            self.assertEqual(
                ["old-growth"],
                catalog["accepted_corrected_growth_motifs"][0]["supersedes_old_motif_ids"],
            )
            self.assertEqual(
                ["old-control"],
                catalog["accepted_corrected_control_motifs"][0][
                    "supersedes_old_motif_ids"
                ],
            )
            self.assertEqual(0, catalog["summary"]["accepted_legacy_broad_growth_count"])
            self.assertTrue((session.session_root / "session_manifest.json").exists())
            self.assertTrue((root / "ExperimentalLog.md").exists())

    def test_runner_is_exported_from_telemetry_package(self) -> None:
        from pygrc.telemetry.grcl9_corrected_growth_catalog import (
            run_grcl9_corrected_growth_catalog as direct_runner,
        )

        self.assertIs(run_grcl9_corrected_growth_catalog, direct_runner)


def _write_lane(
    root: Path,
    fixture_name: str,
    *,
    growth: int,
    front: int,
    legacy: int,
    mode: str = "grc9_front_capacity",
    selector_ids: tuple[str, ...] = (
        "replay_selector_report_passed",
        "grcl9_source_link_present",
        "front_capacity_mode",
        "no_legacy_broad_growth",
        "front_growth_provenance_consistent",
    ),
    source_session_id: str = "S9001",
    has_growth_construct: bool = True,
) -> dict:
    telemetry_root = root / "lanes" / fixture_name / "telemetry"
    source_fixture_path = root / "source_fixtures" / f"{fixture_name}.json"
    lowered_state_path = root / "lowered_states" / f"{fixture_name}.json"
    telemetry_root.mkdir(parents=True, exist_ok=True)
    source_fixture_path.parent.mkdir(parents=True, exist_ok=True)
    lowered_state_path.parent.mkdir(parents=True, exist_ok=True)
    events = [_growth_event(mode=mode, front=front > 0, legacy=legacy > 0) for _ in range(growth)]
    _write_json(telemetry_root / "run_summary.json", _run_summary(mode, growth, front, legacy))
    _write_text(
        telemetry_root / "events.jsonl",
        "".join(json.dumps(event, sort_keys=True) + "\n" for event in events),
    )
    _write_text(telemetry_root / "steps.jsonl", "")
    (telemetry_root / "graph_checkpoints").mkdir(parents=True, exist_ok=True)
    _write_json(telemetry_root / "graph_checkpoints" / "index.json", {})
    _write_json(source_fixture_path, _source_fixture(fixture_name, mode, has_growth_construct))
    _write_json(lowered_state_path, {"cached_quantities": {}})
    return {
        "fixture_name": fixture_name,
        "motif_id": f"grcl9-corrected-motif-{fixture_name}",
        "source_session_id": source_session_id,
        "confidence_label": "strong_candidate",
        "evidence_status": "accepted",
        "event_counts_by_kind": {"growth": growth} if growth else {},
        "passed_selector_ids": list(selector_ids),
        "expected_selector_ids": ["growth_count"],
        "source_fixture_path": str(source_fixture_path),
        "lowered_state_path": str(lowered_state_path),
        "telemetry_root": str(telemetry_root),
        "manifest_entry_id": "grcl9_lowering_growth_pressure_v1",
        "run_id": f"run-{fixture_name}",
        "requested_steps": 3,
    }


def _run_summary(mode: str, growth: int, front: int, legacy: int) -> dict:
    return {
        "family_extensions": {
            "grc9": {
                "backend_summary": {"growth_parent_eligibility_mode": mode},
                "growth_summary": {
                    "growth_count": growth,
                    "front_capacity_growth_count": front,
                    "legacy_broad_growth_count": legacy,
                    "lowest_port_attachment_count": front,
                },
            },
            "grcl9": {
                "fixture_name": "fixture",
                "growth_parent_eligibility_mode": mode,
                "growth_semantics_status": "front_capacity" if front else "none",
                "legacy_broad_growth_non_evidence": bool(legacy),
                "growth_replay_metadata": {
                    "front_capacity_construct_count": 1 if mode == "grc9_front_capacity" else 0,
                    "legacy_growth_construct_count": 1 if mode != "grc9_front_capacity" else 0,
                },
            },
        }
    }


def _growth_event(*, mode: str, front: bool, legacy: bool) -> dict:
    return {
        "event_kind": "growth",
        "family_extensions": {
            "grc9": {
                "growth_evidence": {
                    "parent_eligibility_mode": mode,
                    "parent_capacity_source": "preexisting_front" if front else "legacy",
                    "front_growth_provenance_present": front,
                    "legacy_broad_growth": legacy,
                    "selected_parent_port": 5,
                }
            },
            "grcl9": {
                "growth_parent_eligibility_mode": mode,
                "growth_semantics_status": "front_capacity" if front else "legacy_growth_locus",
                "legacy_broad_growth_non_evidence": legacy,
            },
        },
    }


def _source_fixture(fixture_name: str, mode: str, has_growth_construct: bool) -> dict:
    constructs = []
    if has_growth_construct:
        constructs.append(
            {
                "construct_id": f"{fixture_name}_growth_locus",
                "construct_kind": "growth_locus",
                "growth_semantics": (
                    "front_capacity" if mode == "grc9_front_capacity" else "legacy_growth_locus"
                ),
                "front_capacity_source": (
                    "preexisting_front" if mode == "grc9_front_capacity" else ""
                ),
            }
        )
    return {"fixture_name": fixture_name, "constructs": constructs}


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


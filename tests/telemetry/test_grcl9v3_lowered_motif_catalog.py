"""Tests for reviewed GRCL-9V3 lowered-source motif catalog generation."""

from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from pygrc.telemetry import (
    GRCL9V3_REVIEWED_LOWERED_MOTIF_CATALOG_VERSION,
    run_grcl9v3_lowering_replay_session,
    run_grcl9v3_reviewed_lowered_motif_catalog,
    run_grcl9v3_selector_validation,
)
from pygrc.visualization import render_grcl9v3_lowering_visual_review


class GRCL9V3LoweredMotifCatalogTest(unittest.TestCase):
    def test_catalog_accepts_corrected_front_growth_and_non_growth_records(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_root = Path(temp_dir) / "grcl9v3" / "lowering"
            replay = run_grcl9v3_lowering_replay_session(
                session_id="S9401",
                output_root=output_root,
                fixture_names=(
                    "corrected_front_growth_positive_control",
                    "quiescent_hybrid_control_no_event_control",
                ),
                requested_steps=3,
                source_mode="landscape_seed_examples",
            )
            selectors = run_grcl9v3_selector_validation(
                session_id="S9402",
                output_root=output_root,
                source_session_ids=(replay.session_id,),
            )
            render_grcl9v3_lowering_visual_review(
                session_id="S9403",
                output_root=output_root,
                selector_session_id=selectors.session_id,
                render_visuals=False,
            )

            catalog_session = run_grcl9v3_reviewed_lowered_motif_catalog(
                session_id="S9404",
                output_root=output_root,
                selector_session_ids=(selectors.session_id,),
                visual_session_ids_by_selector={selectors.session_id: "S9403"},
            )

            catalog = _read_json(catalog_session.catalog_path)
            self.assertEqual(
                GRCL9V3_REVIEWED_LOWERED_MOTIF_CATALOG_VERSION,
                catalog["catalog_version"],
            )
            self.assertEqual(2, catalog_session.accepted_count)
            self.assertEqual(0, catalog_session.superseded_count)
            by_fixture = {
                item["fixture_name"]: item for item in catalog["accepted_motifs"]
            }
            growth = by_fixture["corrected_front_growth_positive_control"]
            self.assertEqual("accepted", growth["review_status"])
            self.assertEqual("corrected_front_growth", growth["growth_review"]["status"])
            self.assertTrue(growth["growth_review"]["paper_facing_eligible"])
            self.assertIn("front growth remains runtime-observed", " ".join(growth["non_claims"]))
            self.assertTrue(growth["artifact_links"]["compiled_source"])
            self.assertTrue(growth["artifact_links"]["graph_checkpoints"]["index"])
            self.assertTrue(catalog_session.summary_path.exists())

    def test_catalog_quarantines_legacy_standalone_growth_as_superseded(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_root = Path(temp_dir) / "grcl9v3" / "lowering"
            replay = run_grcl9v3_lowering_replay_session(
                session_id="S9411",
                output_root=output_root,
                fixture_names=("multi_center_delayed_collapse_learning",),
                requested_steps=1,
                source_mode="legacy_growth_landscape_seed_examples",
            )
            selectors = run_grcl9v3_selector_validation(
                session_id="S9412",
                output_root=output_root,
                source_session_ids=(replay.session_id,),
            )

            catalog_session = run_grcl9v3_reviewed_lowered_motif_catalog(
                session_id="S9413",
                output_root=output_root,
                selector_session_ids=(selectors.session_id,),
                visual_session_ids_by_selector={},
            )

            catalog = _read_json(catalog_session.catalog_path)
            self.assertEqual(0, catalog_session.accepted_count)
            self.assertEqual(1, catalog_session.superseded_count)
            superseded = catalog["superseded_motifs"][0]
            self.assertEqual(
                "superseded_by_growth_semantics_correction",
                superseded["review_status"],
            )
            self.assertFalse(superseded["growth_review"]["paper_facing_eligible"])
            self.assertIn(
                "legacy standalone growth is diagnostic",
                " ".join(superseded["non_claims"]),
            )

    def test_catalog_runner_is_exported_from_telemetry_package(self) -> None:
        from pygrc.telemetry.grcl9v3_lowered_motif_catalog import (
            run_grcl9v3_reviewed_lowered_motif_catalog as direct_runner,
        )

        self.assertIs(run_grcl9v3_reviewed_lowered_motif_catalog, direct_runner)


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

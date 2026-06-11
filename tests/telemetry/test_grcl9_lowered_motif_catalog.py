"""Tests for reviewed GRCL-9 lowered motif catalog generation."""

from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from pygrc.telemetry import (
    GRCL9_REVIEWED_LOWERED_MOTIF_CATALOG_VERSION,
    run_grcl9_lowering_replay_session,
    run_grcl9_reviewed_lowered_motif_catalog,
)
from pygrc.visualization import render_grcl9_lowering_visual_session


class GRCL9LoweredMotifCatalogTest(unittest.TestCase):
    def test_catalog_promotes_selector_backed_lowered_motifs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_root = Path(temp_dir) / "grcl9" / "lowering"
            replay = run_grcl9_lowering_replay_session(
                session_id="S9301",
                output_root=output_root,
                fixture_names=(
                    "spark_column_proxy_eps_pass",
                    "cell_boundary_ridge_membrane_spark_pass",
                ),
                requested_steps=6,
                source_mode="landscape_seed_examples",
            )
            render_grcl9_lowering_visual_session(session_root=replay.session_root)

            catalog_session = run_grcl9_reviewed_lowered_motif_catalog(
                session_id="S9302",
                output_root=output_root,
                source_session_ids=("S9301",),
            )

            catalog = _read_json(catalog_session.catalog_path)
            self.assertEqual(
                GRCL9_REVIEWED_LOWERED_MOTIF_CATALOG_VERSION,
                catalog["catalog_version"],
            )
            self.assertEqual(2, catalog_session.accepted_count)
            self.assertEqual(0, catalog_session.rejected_count)
            self.assertTrue(catalog_session.summary_path.exists())
            evidence_classes = {
                item["fixture_name"]: item["evidence_class"]
                for item in catalog["accepted_motifs"]
            }
            self.assertEqual(
                "mechanism_probe",
                evidence_classes["spark_column_proxy_eps_pass"],
            )
            self.assertEqual(
                "composing_cells_seed",
                evidence_classes["cell_boundary_ridge_membrane_spark_pass"],
            )
            for motif in catalog["accepted_motifs"]:
                with self.subTest(motif=motif["motif_id"]):
                    self.assertEqual("accepted", motif["review_status"])
                    self.assertEqual("passed", motif["selector_status"])
                    self.assertTrue(motif["artifact_links"]["compiled_source"])
                    self.assertTrue(motif["artifact_links"]["graph_checkpoints"]["index"])
                    self.assertIn("no_runtime_event_injection", motif["non_claims"])

    def test_catalog_runner_is_exported_from_telemetry_package(self) -> None:
        from pygrc.telemetry.grcl9_lowered_motif_catalog import (
            run_grcl9_reviewed_lowered_motif_catalog as direct_runner,
        )

        self.assertIs(run_grcl9_reviewed_lowered_motif_catalog, direct_runner)

    def test_catalog_records_collapse_diagnostic_without_runtime_claim(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_root = Path(temp_dir) / "grcl9" / "lowering"
            replay = run_grcl9_lowering_replay_session(
                session_id="S9303",
                output_root=output_root,
                fixture_names=(
                    "cell_basin_merge_runtime_collapse_probe",
                    "cell_basin_merge_runtime_stability_control",
                ),
                requested_steps=1,
                source_mode="landscape_seed_examples",
            )
            render_grcl9_lowering_visual_session(session_root=replay.session_root)

            catalog_session = run_grcl9_reviewed_lowered_motif_catalog(
                session_id="S9304",
                output_root=output_root,
                source_session_ids=("S9303",),
            )

            catalog = _read_json(catalog_session.catalog_path)
            self.assertEqual(2, catalog["summary"]["collapse_diagnostic_count"])
            self.assertIn(
                "collapse diagnostics are source-role loss observations",
                " ".join(catalog["non_claims"]),
            )
            by_fixture = {
                item["fixture_name"]: item for item in catalog["accepted_motifs"]
            }
            collapse = by_fixture[
                "cell_basin_merge_runtime_collapse_probe"
            ]["collapse_diagnostic"]
            control = by_fixture[
                "cell_basin_merge_runtime_stability_control"
            ]["collapse_diagnostic"]

            self.assertEqual(
                "runtime_collapse_like_diagnostic",
                collapse["status"],
            )
            self.assertEqual(
                "runtime_collapse_like_observed",
                collapse["classification"],
            )
            self.assertEqual(["fission_sink_b"], collapse["lost_source_sink_roles"])
            self.assertEqual("structural_only_control", control["status"])
            self.assertEqual("structural_only", control["classification"])
            self.assertIn("no GRC9 collapse event", " ".join(collapse["non_claims"]))

    def test_catalog_links_phase_diagram_context_for_s0024_style_lanes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_root = Path(temp_dir) / "grcl9" / "lowering"
            replay = run_grcl9_lowering_replay_session(
                session_id="S9305",
                output_root=output_root,
                fixture_names=("cell_full_capacity_phase_threshold_nominal_growth",),
                requested_steps=24,
                source_mode="legacy_growth_landscape_seed_examples",
                force_legacy_growth=True,
            )
            with self.assertRaisesRegex(ValueError, "force-legacy-growth"):
                render_grcl9_lowering_visual_session(session_root=replay.session_root)
            render_grcl9_lowering_visual_session(
                session_root=replay.session_root,
                force_legacy_growth=True,
            )

            with self.assertRaisesRegex(ValueError, "force-legacy-growth"):
                run_grcl9_reviewed_lowered_motif_catalog(
                    session_id="S9306",
                    output_root=output_root,
                    source_session_ids=("S9305",),
                )

            catalog_session = run_grcl9_reviewed_lowered_motif_catalog(
                session_id="S9306",
                output_root=output_root,
                source_session_ids=("S9305",),
                force_legacy_growth=True,
            )

            catalog = _read_json(catalog_session.catalog_path)
            self.assertTrue(catalog["force_legacy_growth"])
            self.assertEqual(["S9305"], catalog["legacy_source_session_ids"])
            motif = catalog["accepted_motifs"][0]
            diagnostic = motif["collapse_diagnostic"]
            phase = diagnostic["phase_context"]

            self.assertEqual(
                "runtime_collapse_like_diagnostic",
                diagnostic["status"],
            )
            self.assertEqual("threshold", phase["basin_regime"])
            self.assertEqual("nominal_growth", phase["growth_regime"])
            self.assertEqual("active", phase["event_amplification_class"])
            self.assertTrue(phase["phase_diagram_summary"].endswith("phase_diagram_summary.json"))
            self.assertIn("## Collapse Diagnostics", catalog_session.summary_path.read_text())


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

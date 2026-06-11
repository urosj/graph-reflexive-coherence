"""Tests for built-in GRCL-9V3 Revision 1 source fixtures."""

from __future__ import annotations

import json
import unittest
from typing import Any

from pygrc.landscapes.extensions.grcl9v3 import (
    GRCL9V3_SOURCE_FIXTURE_NAMES,
    GRCL9V3AppendixEDivisionRegion,
    GRCL9V3ChoiceCollapseRegion,
    GRCL9V3GrowthLocus,
    GRCL9V3SourceDocument,
    GRCL9V3TransportReroutingRegion,
    GRCL9V3QuiescentHybridRegion,
    default_grcl9v3_lowering_manifest,
    default_grcl9v3_source_fixtures,
    grcl9v3_source_fixture_by_name,
    validate_grcl9v3_source_document_against_manifest,
)


FORBIDDEN_RUNTIME_KEYS = {
    "birth_event",
    "choice_happened",
    "collapse_happened",
    "current_flux",
    "daughter_sink_confirmed",
    "event_counts_by_kind",
    "event_history",
    "expansion_happened",
    "growth_happened",
    "hybrid_spark_completed",
    "runtime_events",
    "solved_diagnostic",
    "solved_flux",
    "solved_hessian",
    "solved_tensor",
    "spark_happened",
}


class GRCL9V3SourceFixturesTest(unittest.TestCase):
    def test_default_fixture_names_are_complete_and_ordered(self) -> None:
        fixtures = default_grcl9v3_source_fixtures()

        self.assertEqual(
            GRCL9V3_SOURCE_FIXTURE_NAMES,
            tuple(fixture.fixture_name for fixture in fixtures),
        )
        self.assertEqual(12, len(fixtures))
        self.assertEqual(
            set(GRCL9V3_SOURCE_FIXTURE_NAMES),
            set(grcl9v3_source_fixture_by_name()),
        )

    def test_fixtures_round_trip_through_schema(self) -> None:
        for fixture in default_grcl9v3_source_fixtures():
            with self.subTest(fixture=fixture.fixture_name):
                payload = fixture.to_mapping()
                restored = GRCL9V3SourceDocument.from_mapping(json.loads(json.dumps(payload)))
                self.assertEqual(payload, restored.to_mapping())
                self.assertEqual("grcl9v3.source.v1", restored.source_schema_version)

    def test_fixtures_link_to_manifest_entries_or_future_records(self) -> None:
        manifest = default_grcl9v3_lowering_manifest()
        future_by_motif = {
            record.motif_id: record for record in manifest.future_vocabulary_records
        }
        manifest_entry_count = 0
        future_record_count = 0

        for fixture in default_grcl9v3_source_fixtures():
            with self.subTest(fixture=fixture.fixture_name):
                summary = validate_grcl9v3_source_document_against_manifest(
                    fixture,
                    manifest,
                    allow_future_vocabulary=True,
                )
                self.assertTrue(summary["motif_ids"])
                self.assertTrue(fixture.expected_selector_ids)
                if summary["linkage_kind"] == "manifest_entry":
                    manifest_entry_count += 1
                elif summary["linkage_kind"] == "future_vocabulary_record":
                    future_record_count += 1
                    motif_id = fixture.constructs[0].motif_id  # type: ignore[attr-defined]
                    record = future_by_motif[motif_id]
                    self.assertEqual(
                        f"future_vocabulary_{record.phenomenon}_v1",
                        fixture.manifest_entry_id,
                    )
                    self.assertEqual((), fixture.expected_telemetry)
                    self.assertIn("selector_dependency", fixture.notes)
                else:
                    self.fail(f"unexpected linkage kind {summary['linkage_kind']!r}")

        self.assertEqual(5, manifest_entry_count)
        self.assertEqual(7, future_record_count)

    def test_fixtures_do_not_contain_runtime_histories_or_solved_results(self) -> None:
        for fixture in default_grcl9v3_source_fixtures():
            with self.subTest(fixture=fixture.fixture_name):
                self.assertEqual([], _forbidden_paths(fixture.to_mapping()))

    def test_pass_fail_controls_use_distinct_source_preconditions(self) -> None:
        fixtures = grcl9v3_source_fixture_by_name()
        spark_pass = fixtures["hybrid_spark_gate_positive_control"]
        spark_fail = fixtures["hybrid_spark_gate_negative_control"]
        expansion_pass = fixtures["spark_to_expansion_positive_control"]
        expansion_fail = fixtures["spark_to_expansion_negative_control"]

        pass_degree = spark_pass.constructs[0].saturation_profile["active_degree"]  # type: ignore[attr-defined]
        fail_degree = spark_fail.constructs[0].saturation_profile["active_degree"]  # type: ignore[attr-defined]
        self.assertGreater(pass_degree, fail_degree)

        pass_expansion = expansion_pass.constructs[1]
        fail_expansion = expansion_fail.constructs[1]
        self.assertEqual(
            pass_expansion.target_effective_degree,  # type: ignore[attr-defined]
            fail_expansion.target_effective_degree,  # type: ignore[attr-defined]
        )
        self.assertGreater(
            expansion_pass.constructs[0].saturation_profile["active_degree"],  # type: ignore[attr-defined]
            expansion_fail.constructs[0].saturation_profile["active_degree"],  # type: ignore[attr-defined]
        )

    def test_expected_construct_types_are_present(self) -> None:
        fixtures = grcl9v3_source_fixture_by_name()

        self.assertTrue(
            any(
                isinstance(construct, GRCL9V3AppendixEDivisionRegion)
                for construct in fixtures["appendix_e_cell_division_positive_control"].constructs
            )
        )
        self.assertIsInstance(
            fixtures["choice_collapse_positive_control"].constructs[0],
            GRCL9V3ChoiceCollapseRegion,
        )
        self.assertIsInstance(
            fixtures["growth_pressure_positive_control"].constructs[0],
            GRCL9V3GrowthLocus,
        )
        self.assertIsInstance(
            fixtures["transport_basin_rerouting_positive_control"].constructs[0],
            GRCL9V3TransportReroutingRegion,
        )
        self.assertIsInstance(
            fixtures["quiescent_hybrid_control_no_event_control"].constructs[0],
            GRCL9V3QuiescentHybridRegion,
        )

    def test_growth_and_appendix_e_controls_preserve_control_knobs(self) -> None:
        fixtures = grcl9v3_source_fixture_by_name()
        growth_pass = fixtures["growth_pressure_positive_control"].constructs[0]
        growth_fail = fixtures["growth_pressure_negative_control"].constructs[0]
        appendix_pass = fixtures["appendix_e_cell_division_positive_control"].constructs[2]
        appendix_fail = fixtures["appendix_e_cell_division_negative_control"].constructs[2]

        self.assertGreater(growth_pass.lambda_birth, growth_fail.lambda_birth)  # type: ignore[attr-defined]
        self.assertNotEqual(
            appendix_pass.module_basin_support,  # type: ignore[attr-defined]
            appendix_fail.module_basin_support,  # type: ignore[attr-defined]
        )


def _forbidden_paths(value: Any, prefix: str = "") -> list[str]:
    if isinstance(value, dict):
        paths: list[str] = []
        for key, item in value.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            if str(key) in FORBIDDEN_RUNTIME_KEYS:
                paths.append(path)
            paths.extend(_forbidden_paths(item, path))
        return paths
    if isinstance(value, list):
        paths = []
        for index, item in enumerate(value):
            paths.extend(_forbidden_paths(item, f"{prefix}[{index}]"))
        return paths
    return []


if __name__ == "__main__":
    unittest.main()

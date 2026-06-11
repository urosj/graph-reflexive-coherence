"""Tests for built-in GRCL-9 Revision 1 source fixtures."""

from __future__ import annotations

import json
import unittest
from typing import Any

from pygrc.landscapes.extensions.grcl9 import (
    GRCL9_SOURCE_FIXTURE_NAMES,
    GRCL9SourceDocument,
    default_grcl9_lowering_manifest,
    default_grcl9_source_fixtures,
    grcl9_source_fixture_by_name,
)


FORBIDDEN_RUNTIME_KEYS = {
    "birth_event",
    "current_flux",
    "event_counts_by_kind",
    "event_history",
    "expansion_completed",
    "fission_confirmed",
    "runtime_events",
    "solved_diagnostic",
    "solved_flux",
    "spark_happened",
}


class GRCL9SourceFixturesTest(unittest.TestCase):
    def test_default_fixture_names_are_complete_and_ordered(self) -> None:
        fixtures = default_grcl9_source_fixtures()

        self.assertEqual(
            GRCL9_SOURCE_FIXTURE_NAMES,
            tuple(fixture.fixture_name for fixture in fixtures),
        )
        self.assertEqual(10, len(fixtures))
        self.assertEqual(set(GRCL9_SOURCE_FIXTURE_NAMES), set(grcl9_source_fixture_by_name()))

    def test_fixtures_round_trip_through_schema(self) -> None:
        for fixture in default_grcl9_source_fixtures():
            with self.subTest(fixture=fixture.fixture_name):
                payload = fixture.to_mapping()
                restored = GRCL9SourceDocument.from_mapping(json.loads(json.dumps(payload)))
                self.assertEqual(payload, restored.to_mapping())
                self.assertEqual("grcl9.source.v1", restored.source_schema_version)

    def test_fixtures_link_to_manifest_entries_and_controls(self) -> None:
        manifest = default_grcl9_lowering_manifest()
        entries = manifest.by_entry_id()

        for fixture in default_grcl9_source_fixtures():
            with self.subTest(fixture=fixture.fixture_name):
                self.assertIn(fixture.manifest_entry_id, entries)
                entry = entries[fixture.manifest_entry_id]
                control_names = {control.source_fixture_name for control in entry.controls}
                self.assertIn(fixture.fixture_name, control_names)
                self.assertEqual(entry.expected_telemetry, fixture.expected_telemetry)
                self.assertTrue(fixture.expected_selector_ids)

    def test_fixtures_do_not_contain_runtime_histories_or_solved_results(self) -> None:
        for fixture in default_grcl9_source_fixtures():
            with self.subTest(fixture=fixture.fixture_name):
                self.assertEqual([], _forbidden_paths(fixture.to_mapping()))

    def test_fission_fixtures_are_min_mass_controls_only(self) -> None:
        fixtures = grcl9_source_fixture_by_name()
        fission_pass = fixtures["post_expansion_fission_min_mass_pass"]
        fission_fail = fixtures["post_expansion_fission_min_mass_fail"]

        self.assertEqual(
            "grcl9_lowering_post_expansion_fission_v1",
            fission_pass.manifest_entry_id,
        )
        self.assertEqual(
            "grcl9_lowering_post_expansion_fission_v1",
            fission_fail.manifest_entry_id,
        )
        self.assertIn("no_source_level_fission_confirmation", fission_pass.non_claims)
        self.assertEqual(1, len(fission_pass.constructs))
        self.assertEqual(1, len(fission_fail.constructs))
        self.assertLess(
            fission_pass.constructs[0].identity_fission_min_basin_mass,  # type: ignore[attr-defined]
            fission_fail.constructs[0].identity_fission_min_basin_mass,  # type: ignore[attr-defined]
        )

    def test_growth_birth_probability_summary_is_optional(self) -> None:
        fixture = grcl9_source_fixture_by_name()["growth_pressure_lambda_high"]

        optional_fields = {
            expectation.field_path
            for expectation in fixture.expected_telemetry
            if not expectation.required
        }

        self.assertIn(
            "family_extensions.grc9.growth_summary.birth_probability_max",
            optional_fields,
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

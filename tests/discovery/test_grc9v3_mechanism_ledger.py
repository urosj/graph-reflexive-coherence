"""Tests for the GRC9V3 phenomenology mechanism ledger."""

from __future__ import annotations

import json
import unittest

from pygrc import telemetry
from pygrc.discovery import (
    GRC9V3MechanismLedger,
    GRC9V3_RUNTIME_CAPABILITY_GATED,
    GRC9V3_RUNTIME_DEFERRED,
    GRC9V3_RUNTIME_OUT_OF_SCOPE,
    GRC9V3_RUNTIME_TESTABLE,
    default_grc9v3_mechanism_ledger,
    hypothesis_runtime_status_matches_grc9v3_ledger,
)


class GRC9V3MechanismLedgerTest(unittest.TestCase):
    def test_default_ledger_round_trips_through_json(self) -> None:
        ledger = default_grc9v3_mechanism_ledger()
        payload = ledger.to_mapping()
        restored = GRC9V3MechanismLedger.from_mapping(json.loads(json.dumps(payload)))

        self.assertEqual(payload, restored.to_mapping())

    def test_default_ledger_covers_required_discovery_phenomena(self) -> None:
        ledger = default_grc9v3_mechanism_ledger()
        phenomena = {entry.phenomenon for entry in ledger.entries}

        self.assertTrue(
            {
                "hybrid_spark_gate",
                "spark_to_expansion",
                "column_diagnostic_proxy",
                "appendix_e_cell_division",
                "choice_collapse",
                "growth_pressure",
                "quadrature_budget_preservation",
                "hessian_backend_comparison",
                "signed_crossing_spark",
                "transport_basin_rerouting",
                "coarse_cache_invalidation",
                "quiescent_hybrid_control",
            }.issubset(phenomena)
        )

    def test_runtime_statuses_cover_testable_capability_deferred_and_out_of_scope(self) -> None:
        ledger = default_grc9v3_mechanism_ledger()
        statuses = {entry.runtime_status for entry in ledger.entries}

        self.assertIn(GRC9V3_RUNTIME_TESTABLE, statuses)
        self.assertIn(GRC9V3_RUNTIME_CAPABILITY_GATED, statuses)
        self.assertIn(GRC9V3_RUNTIME_DEFERRED, statuses)
        self.assertIn(GRC9V3_RUNTIME_OUT_OF_SCOPE, statuses)
        for entry in ledger.entries:
            if entry.runtime_status == GRC9V3_RUNTIME_TESTABLE:
                self.assertTrue(entry.testable_with_current_runtime)
                self.assertGreater(len(entry.predicted_telemetry_fields), 0)
                self.assertEqual((), entry.runtime_blockers)
            else:
                self.assertFalse(entry.testable_with_current_runtime)
                self.assertGreater(len(entry.runtime_blockers), 0)

    def test_testable_mechanisms_cite_sources_ownership_and_telemetry_fields(self) -> None:
        ledger = default_grc9v3_mechanism_ledger()

        for entry in ledger.entries:
            self.assertGreater(len(entry.ownership), 0)
            self.assertGreater(len(entry.phase7_sources), 0)
            self.assertGreater(len(entry.parent_family_sources), 0)
            if entry.runtime_status == GRC9V3_RUNTIME_TESTABLE:
                for signature in entry.predicted_telemetry_fields:
                    self.assertTrue(
                        signature.field_path.startswith("family_extensions.grc9v3.")
                        or signature.field_path.startswith("checkpoint.")
                    )

    def test_capability_gated_mechanisms_name_capability_blockers(self) -> None:
        ledger = default_grc9v3_mechanism_ledger()

        gated_entries = [
            entry
            for entry in ledger.entries
            if entry.runtime_status == GRC9V3_RUNTIME_CAPABILITY_GATED
        ]

        self.assertGreaterEqual(len(gated_entries), 1)
        for entry in gated_entries:
            self.assertTrue(
                any("capability" in blocker for blocker in entry.runtime_blockers)
            )

    def test_column_diagnostic_proxy_is_not_directly_testable_without_hsb_telemetry(self) -> None:
        entry = default_grc9v3_mechanism_ledger().by_id()[
            "grc9v3_mech_column_diagnostic_proxy"
        ]

        self.assertEqual(GRC9V3_RUNTIME_CAPABILITY_GATED, entry.runtime_status)
        self.assertFalse(entry.testable_with_current_runtime)
        self.assertTrue(any("H_s^(b)" in blocker for blocker in entry.runtime_blockers))

    def test_flagged_predicted_fields_match_current_grc9v3_telemetry_contract(self) -> None:
        differential = telemetry.GRC9V3RowBasisDifferentialSummary(
            gradient_norm_min=0.0,
            gradient_norm_max=1.0,
            gradient_norm_mean=0.5,
            signed_hessian_min=-1.0,
            signed_hessian_max=1.0,
            signed_hessian_mean=0.0,
            current_min_signed_hessian_min=-1.0,
            hessian_backend="row_basis_diagonal",
            hessian_sign=-1,
            previous_min_signed_hessian_available=True,
            signed_hessian_history_pruned_count=0,
            weighted_least_squares_hessian_available=False,
        ).to_mapping()
        spark_state = telemetry.GRC9V3HybridSparkStateSummary(
            hybrid_spark_candidate_count=1,
            completed_hybrid_spark_count=0,
            last_candidate_saturation_gate=True,
            last_candidate_basin_interior_gate=True,
            last_candidate_signed_hessian_gate=True,
            last_child_stabilization_pass=False,
            signed_crossing_status="disabled",
        ).to_mapping()
        coarse_cache = telemetry.GRC9V3CoarseCacheSummary(
            coarse_cache_state="invalidated",
            coarse_cache_invalidated=True,
            coarse_cache_invalidation_reason="topology_changed",
        ).to_mapping()

        self.assertIn("previous_min_signed_hessian_available", differential)
        self.assertIn("weighted_least_squares_hessian_available", differential)
        self.assertIn("signed_crossing_status", spark_state)
        self.assertIn("coarse_cache_state", coarse_cache)

    def test_theory_specific_entries_keep_paper_equations_precise(self) -> None:
        by_id = default_grc9v3_mechanism_ledger().by_id()

        expansion = by_id["grc9v3_mech_spark_to_expansion"]
        self.assertIn("Eq. 13: n=ceil((D_eff - 2) / 7)", expansion.equations)
        self.assertFalse(any("max(4" in equation for equation in expansion.equations))

        signed_crossing = by_id["grc9v3_mech_signed_crossing_spark"]
        self.assertIn(
            "H_s^(b)(k) * H_s^(b)(k-1) < 0 for some column b",
            signed_crossing.equations,
        )
        self.assertFalse(any("H_min" in equation for equation in signed_crossing.equations))

        hybrid_spark = by_id["grc9v3_mech_hybrid_spark_gate"]
        self.assertTrue(any("Eq. G8" in equation for equation in hybrid_spark.equations))
        self.assertTrue(any("Eq. 12" in equation for equation in hybrid_spark.equations))

    def test_coarse_cache_ledger_tracks_primary_invalidation_reason(self) -> None:
        entry = default_grc9v3_mechanism_ledger().by_id()[
            "grc9v3_mech_coarse_cache_invalidation"
        ]
        paths = {signature.field_path for signature in entry.predicted_telemetry_fields}

        self.assertIn(
            "family_extensions.grc9v3.coarse_cache.coarse_cache_invalidation_reason",
            paths,
        )

    def test_notes_are_populated_for_reference_use(self) -> None:
        for entry in default_grc9v3_mechanism_ledger().entries:
            self.assertNotEqual("", entry.notes)

    def test_hypothesis_runtime_status_copies_ledger_entry(self) -> None:
        ledger_entry = default_grc9v3_mechanism_ledger().by_id()[
            "grc9v3_mech_hybrid_spark_gate"
        ]
        hypothesis = {
            "hypothesis_id": "grc9v3_hypothesis_hybrid_spark_gate_v1",
            "runtime_status": ledger_entry.runtime_status,
        }

        self.assertTrue(
            hypothesis_runtime_status_matches_grc9v3_ledger(hypothesis, ledger_entry)
        )


if __name__ == "__main__":
    unittest.main()

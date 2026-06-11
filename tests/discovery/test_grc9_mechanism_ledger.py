"""Tests for the GRC9 phenomenology mechanism ledger."""

from __future__ import annotations

import json
import unittest

from pygrc.discovery import (
    GRC9MechanismLedger,
    GRC9StructureHypothesis,
    RUNTIME_DEFERRED,
    RUNTIME_OUT_OF_SCOPE,
    RUNTIME_RESERVED_FUTURE,
    RUNTIME_TESTABLE,
    default_grc9_mechanism_ledger,
    hypothesis_runtime_status_matches_ledger,
)
from pygrc import telemetry


class GRC9MechanismLedgerTest(unittest.TestCase):
    def test_default_ledger_round_trips_through_json(self) -> None:
        ledger = default_grc9_mechanism_ledger()
        payload = ledger.to_mapping()
        restored = GRC9MechanismLedger.from_mapping(json.loads(json.dumps(payload)))

        self.assertEqual(payload, restored.to_mapping())

    def test_default_ledger_covers_required_discovery_phenomena(self) -> None:
        ledger = default_grc9_mechanism_ledger()
        phenomena = {entry.phenomenon for entry in ledger.entries}

        self.assertTrue(
            {
                "spark_precursor",
                "expansion_module",
                "column_preserving_reassignment",
                "growth_pressure",
                "row_tensor_regime",
                "column_diagnostic_regime",
                "coarse_graining_profile_sparsity",
                "budget_correction",
                "quiescent_basin",
                "transport_pathway",
                "fission_candidate",
            }.issubset(phenomena)
        )

    def test_runtime_statuses_separate_testable_from_deferred_and_reserved(self) -> None:
        ledger = default_grc9_mechanism_ledger()
        statuses = {entry.runtime_status for entry in ledger.entries}

        self.assertIn(RUNTIME_TESTABLE, statuses)
        self.assertIn(RUNTIME_DEFERRED, statuses)
        self.assertIn(RUNTIME_RESERVED_FUTURE, statuses)
        self.assertIn(RUNTIME_OUT_OF_SCOPE, statuses)
        for entry in ledger.entries:
            if entry.runtime_status == RUNTIME_TESTABLE:
                self.assertTrue(entry.testable_with_current_runtime)
                self.assertGreater(len(entry.predicted_telemetry_fields), 0)
            else:
                self.assertFalse(entry.testable_with_current_runtime)
                self.assertGreater(len(entry.runtime_blockers), 0)

    def test_testable_mechanisms_cite_paper_spec_and_telemetry_fields(self) -> None:
        ledger = default_grc9_mechanism_ledger()

        for entry in ledger.entries:
            self.assertGreater(len(entry.paper_sources), 0)
            self.assertGreater(len(entry.spec_sources), 0)
            if entry.runtime_status == RUNTIME_TESTABLE:
                for signature in entry.predicted_telemetry_fields:
                    self.assertTrue(
                        signature.field_path.startswith("family_extensions.grc9.")
                        or signature.field_path.startswith("checkpoint.")
                    )

    def test_flagged_predicted_fields_match_current_grc9_telemetry_contract(self) -> None:
        budget_payload = telemetry.GRC9BudgetEvidence(
            budget_error_before=1.0,
            budget_error_after=0.0,
        ).to_mapping()
        coarse_payload = telemetry.GRC9CoarseGrainingSummary(
            coarse_fields_list=("conductance",),
            coarse_cache_state="warm",
            coarse_cache_invalidation_reason=None,
            exact_split_supported_fields=("conductance",),
            signed_flux_mode="signed_lossless",
            profile_compression_mode="full",
        ).to_mapping()
        transport_payload = telemetry.GRC9TransportSummary(
            conductance_min=0.0,
            conductance_max=1.0,
            conductance_mean=0.5,
            flux_abs_sum=1.0,
            flux_signed_balance=0.0,
            positive_flux_edge_count=1,
            negative_flux_edge_count=0,
            strongest_flux_edges_sample=(),
            label_availability=telemetry.GRC9LabelAvailability(
                overall="partial",
                geometric_length_available=True,
                temporal_delay_available=False,
                flux_coupling_available=True,
            ),
        ).to_mapping()

        self.assertIn("budget_error_before", budget_payload)
        self.assertIn("profile_compression_mode", coarse_payload)
        self.assertIn("label_availability", transport_payload)

    def test_hypothesis_runtime_status_copies_ledger_entry(self) -> None:
        ledger_entry = default_grc9_mechanism_ledger().by_id()[
            "grc9_mech_spark_precursor"
        ]
        hypothesis = GRC9StructureHypothesis(
            hypothesis_id="grc9_hypothesis_0001",
            target_phenomenon="spark_precursor",
            runtime_status=ledger_entry.runtime_status,
            paper_sources=ledger_entry.paper_sources,
            graph_preconditions=ledger_entry.graph_preconditions,
            seed_family="spark_precursor",
            seed_parameters={"control_role": "positive_control"},
            generator="generate_grc9_seed",
            predicted_signatures=ledger_entry.predicted_telemetry_fields,
        )

        self.assertTrue(hypothesis_runtime_status_matches_ledger(hypothesis, ledger_entry))


if __name__ == "__main__":
    unittest.main()

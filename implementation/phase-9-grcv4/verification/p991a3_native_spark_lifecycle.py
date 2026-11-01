"""Bounded public source/event and synthetic-window controls, never a campaign."""

import argparse
import io
import json
import sys
import unittest
from hashlib import sha256
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
for directory in (ROOT, ROOT / "src"):
    sys.path.insert(0, str(directory))
RECORD = "implementation/phase-9-grcv4/tranche-9/P9-9.1a.3-Verification.json"
SCRIPT = "implementation/phase-9-grcv4/verification/p991a3_native_spark_lifecycle.py"


LIFECYCLE_ROSTER = (
    "test_all_terminal_paths_excluded_anchors_and_ties",
    "test_certificate_tampering_full_coordinates_and_bindings",
    "test_cold_checkpoint_replay_actual_source_and_event",
    "test_concurrent_duplicate_completion_is_one_atomic_claim",
    "test_duplicate_before_completion_single_shared_credit",
    "test_full_domain_mathematics_and_exact_membership",
    "test_independent_full_jacobian_at_exact_center",
    "test_late_failure_rolls_back_state_window_consumption_and_children",
    "test_lawful_source_event_preserves_both_exact_roles",
    "test_opposite_chiral_event_uses_actual_graph_certificate",
    "test_optional_schema_static_v3_and_round_trip",
    "test_save_load_replay_and_stale_import_reconcile_occurrence",
    "test_two_positive_beats_after_entry_and_atomic_child",
    "test_wrong_role_pair_and_forced_requests_cannot_advance",
    "test_zero_inspection_failure_reset_rebase_and_policy_replacement",
)

PRESSURE_ROSTER = (
    "test_atomic_failures_at_preparation_window_and_publication",
    "test_charge_chart_faces_and_charge_normal_projection_trap",
    "test_checkpoints_at_each_window_boundary_and_observer_noninterference",
    "test_cycle_current_mutation_preserves_state_but_fails_current_oracle",
    "test_duplicate_delivery_is_noop_in_ancestry_and_failed_request_retries",
    "test_flat_sign_mutation_preserves_geometry_but_fails_flat_oracle",
    "test_generic_spectral_split_boundary_and_frobenius_conservatism",
    "test_independent_classifier_diamonds_unqualified_ties_singletons_thresholds",
    "test_inside_domain_without_event_cannot_earn_gain",
    "test_literal_both_chiral_events_and_actual_role_transfer",
    "test_native_execution_without_research_imports_or_trajectory_reads",
    "test_predictor_current_mutation_and_wrong_fixed_geometry_equations",
    "test_public_equation_stages_outward_error_and_fresh_restart",
    "test_rehashed_certificate_semantic_corruption",
    "test_reset_only_event_and_certificate_failures_are_atomic",
)


def required_suite(case, roster):
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(case)
    names = tuple(t._testMethodName for t in suite)
    if not names or names != roster:
        raise ValueError("mandatory native test roster differs: " + repr(names))
    return suite


def seal(value):
    body = {k: v for k, v in value.items() if k != "record_digest"}
    return dict(
        body,
        record_digest=sha256(
            json.dumps(
                body, sort_keys=True, separators=(",", ":"), ensure_ascii=True
            ).encode()
        ).hexdigest(),
    )


def run():
    import flint
    from test_cos_native_spark_pressure import COSNativePressureTests

    from tests.models.test_grc_9_v4_spark_completion import NativeSparkCompletionTests

    suite = unittest.TestSuite(
        (
            required_suite(NativeSparkCompletionTests, LIFECYCLE_ROSTER),
            required_suite(COSNativePressureTests, PRESSURE_ROSTER),
        )
    )
    names = list(LIFECYCLE_ROSTER)
    output = io.StringIO()
    result = unittest.TextTestRunner(stream=output, verbosity=2).run(suite)
    if (
        not result.wasSuccessful()
        or result.skipped
        or result.expectedFailures
        or result.testsRun != len(LIFECYCLE_ROSTER) + len(PRESSURE_ROSTER)
    ):
        raise ValueError(output.getvalue())
    model = NativeSparkCompletionTests.event_model
    certificates = NativeSparkCompletionTests.certificates
    from p991a2_native_spark_numerics import RECORD as NUMERICS_RECORD
    from p991a2_native_spark_numerics import read
    from p991a3_native_spark_epoch import CHANGED

    inv = "implementation/investigations/grc9v4-constitutive-design/"
    paths = {
        *CHANGED,
        SCRIPT,
        "implementation/phase-9-grcv4/verification/p991a3_native_spark_epoch.py",
        "tests/models/test_grc_9_v4_spark_completion.py",
        "specs/grc-v4-conformance-vectors.json",
        "implementation/phase-9-grcv4/verification/cos_native_spark_oracle.py",
        "implementation/phase-9-grcv4/verification/test_cos_native_spark_pressure.py",
        "tests/models/test_grc_v4_realizations.py",
        "tests/models/test_grc_v4_candidate_c.py",
        *(
            inv + "research/" + name + ".py"
            for name in ("spark_completion_positive", "spark_completion_continuation")
        ),
        inv
        + "evidence/spark-completion/review/constructive-candidate/positive_candidate.py",
        "src/pygrc/models/grc_v4_assets/grc-9-v4-spark-completion-schema.json",
        *(
            "src/pygrc/models/" + name + ".py"
            for name in (
                "grc_9_v4_completion",
                "grc_9_v4_completion_codec",
                "grc_9_v4_completion_certificate",
                "grc_9_v4_spark_contracts",
                "grc_9_v4_spark_owner",
            )
        ),
        *(r["path"] for r in read(NUMERICS_RECORD)["source_bindings"]),
    }
    cp = model._operation._published.completion
    return seal(
        {
            "schema": "grc9v4-native-spark-lifecycle-verification-v1",
            "leaf": "P9-9.1a.3",
            "status": "implemented_verified_pending_review",
            "user_accepted": False,
            "native_completion_support": False,
            "native_endpoint_verified": False,
            "full_trajectory_runs": 0,
            "actual_public_source_beats": 1,
            "actual_public_events": 1,
            "target_vertices": 15,
            "target_edges": 16,
            "exact_charge": "21",
            "duration": "32",
            "event_id": cp.event["event_id"],
            "target_graph_digest": model.configuration.reference.graph.graph_digest,
            "target_profile_id": model.active_profile_id,
            "certificate_ids": [c.certificate_id for c in certificates],
            "certificate_q": certificates[0].proof["q"],
            "image_margin": certificates[0].proof["image_margin"],
            "full_step_error": certificates[0].proof["full_step_error"],
            "certificate_precision_bits": 512,
            "tests_passed": result.testsRun,
            "controls": names,
            "pressure_tests_passed": len(PRESSURE_ROSTER),
            "pressure_controls": list(PRESSURE_ROSTER),
            "mandatory_roster_checked": True,
            "skipped_mandatory_tests": 0,
            "pressure_measurements": COSNativePressureTests.measurements,
            "source_configuration": NativeSparkCompletionTests.config.to_payload(),
            "numerical_backend": "FLINT",
            "flint_version": flint.__version__,
            "oracle_precision_bits": 512,
            "entry_revision": "32376cd4",
            "working_tree_binding": "individual source_bindings below",
            "duplicate_delivery_rejected": True,
            "pressure_scope": "bounded equations/numerics/event/classifier/certificate/lifecycle; no native closure campaign",
            "fixture_counts_scope": "canonical retained source/event fixture; excludes repeated independent fault controls",
            "deferred_pressure": [
                "same-subject runtime estimate",
                "uninterrupted source-to-completion campaign",
                "per-transition named-witness reproduction and accumulated error",
                "explicit physical-flow and converged-CI substitutions",
                "exhaustive event/profile/binding mutation matrix",
            ],
            "positive_window_fixture": "synthetic target center plus actual event provenance; no source-to-center execution claimed",
            "duplicate_before_completion_single_credit": True,
            "atomic_child_registration": True,
            "late_failure_rollback": True,
            "cold_source_event_replay": True,
            "accounting_scope": "process_shared_publication_v1",
            "cross_process_global_uniqueness": False,
            "source_bindings": [
                {"path": p, "sha256": sha256((ROOT / p).read_bytes()).hexdigest()}
                for p in sorted(paths)
            ],
            "next_leaf": "P9-9.1a.4",
            "timing_scope": "bounded correctness controls; not a campaign estimate",
        }
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = run()
    if args.write:
        (ROOT / RECORD).write_text(json.dumps(value, indent=2) + "\n")
    elif args.check and json.loads((ROOT / RECORD).read_bytes()) != value:
        raise ValueError("native lifecycle verification differs from retained record")
    print(
        json.dumps(
            {
                k: value[k]
                for k in (
                    "status",
                    "tests_passed",
                    "native_endpoint_verified",
                    "next_leaf",
                )
            }
        )
    )


if __name__ == "__main__":
    main()

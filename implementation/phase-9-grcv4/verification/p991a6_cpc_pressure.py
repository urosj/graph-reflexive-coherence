"""Run the bounded mandatory PC pressure roster and retain source-bound results."""

import argparse
import io
import json
import lzma
import sys
import time
import unittest
from hashlib import sha256
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / "src")]
from p991a6_cpc_preflight import check as preflight_check
from p991a6_cpc_preflight import seal
from test_cpc_native_spark_pressure import CPCNativePressureTests

BASE = "implementation/phase-9-grcv4/tranche-9/"
HERE = "implementation/phase-9-grcv4/verification/"
RECORD = BASE + "P9-9.1a.6-CPC-Pressure.json"
EVIDENCE = BASE + "P9-9.1a.6-CPC-PressureSamples.json.xz"
SCRIPT = HERE + "p991a6_cpc_pressure.py"
ROSTER = (
    "test_actual_source_beat_preserves_distinct_reset_history",
    "test_actual_stages_frozen_inputs_and_complete_joint_error",
    "test_all_PC_transaction_faults_preserve_whole_publication",
    "test_archive_and_whole_target_mutations",
    "test_atomic_failures_at_preparation_window_and_publication",
    "test_checkpoints_at_each_window_boundary_and_observer_noninterference",
    "test_duplicate_delivery_is_noop_in_ancestry_and_failed_request_retries",
    "test_equal_C_equal_norm_trace_different_patterns_and_roles",
    "test_event_whole_actual_archive_changed_support_and_regeneration",
    "test_every_source_target_signed_direction_and_simultaneous_history",
    "test_exact_norm_boundaries_and_packed_offdiagonal_discriminator",
    "test_full_60_direction_finite_segments_and_cross_couplings",
    "test_held_source_and_writer_mutations",
    "test_independent_classifier_diamonds_unqualified_ties_singletons_thresholds",
    "test_inside_domain_without_event_cannot_earn_gain",
    "test_invalid_carrier_payloads_and_wrong_graph_binding",
    "test_joint_trap_boundary_all_coordinates_and_relabelled_proofs",
    "test_native_step_without_research_import_or_trajectory_read",
    "test_nonfinite_or_unresolved_reads_and_writers_fail_closed",
    "test_observer_snapshot_aliasing_zero_duration_and_migration",
    "test_read_mutations_have_specific_constitutive_discriminators",
    "test_reset_only_and_target_admission_faults",
    "test_signed_edge_permutation_covariance_and_untransported_binding",
    "test_uniform_signed_history_releases_without_resource_motion",
    "test_writer_primitive_held_source_semigroup_and_cancellation",
    "test_zero_formation_next_consumption_and_signed_source",
)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def run():
    import flint

    flint.ctx.threads = 1
    preflight = preflight_check(ROOT)
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(CPCNativePressureTests)
    need(
        tuple(t._testMethodName for t in suite) == ROSTER,
        "mandatory PC pressure roster differs",
    )
    output = io.StringIO()
    start = time.perf_counter()
    result = unittest.TextTestRunner(stream=output, verbosity=2).run(suite)
    need(
        result.wasSuccessful()
        and result.testsRun == len(ROSTER)
        and not result.skipped
        and not result.expectedFailures,
        output.getvalue(),
    )
    elapsed = time.perf_counter() - start
    need(elapsed < 180, "bounded pressure exceeded 180-second cap")
    print(output.getvalue(), flush=True)
    evidence = CPCNativePressureTests.evidence
    need(
        len(evidence["actual_steps"]) == 4, "four actual captured target steps required"
    )
    raw = lzma.compress(
        json.dumps(evidence, sort_keys=True, separators=(",", ":")).encode(), preset=6
    )
    (ROOT / EVIDENCE).write_bytes(raw)
    paths = {r["path"] for r in preflight["source_bindings"]} | {
        BASE + "P9-9.1a.6-CPC-Preflight.json",
        SCRIPT,
        HERE + "cpc_native_spark_pressure_oracle.py",
        HERE + "test_cpc_native_spark_pressure.py",
        HERE + "test_cos_native_spark_pressure.py",
        "specs/grc-9-v4-spark-completion-applicability-source-manifest.json",
        "specs/grc-9-v4-spark-completion-earlier-source-manifest.json",
    }
    value = seal(
        {
            "schema": "grc9v4-native-cpc-pressure-v1",
            "family": "C_PC",
            "status": "verified_pending_review",
            "tests_passed": result.testsRun,
            "test_roster": list(ROSTER),
            "elapsed_seconds": elapsed,
            "native_endpoint_verified": False,
            "native_completion_support": False,
            "full_trajectory_runs": 0,
            "production_precision_bits": 256,
            "oracle_precision_bits": 768,
            "runtime_changed": False,
            "sampling_cap_seconds": 180,
            "fixed_H_oracle_arithmetic": "exact FLINT rational",
            "preflight_record_digest": preflight["record_digest"],
            "measurements": CPCNativePressureTests.measurements,
            "scope": "bounded full-history/read/writer/domain/event/certificate/lifecycle pressure; synthetic windows are not source-to-entry executions",
            "pending_campaign": {
                "leaf": "P9-9.1a.6-C_PC.5",
                "current": [374, 376],
                "reset": [375, 377],
                "expected_endpoints_verified": False,
                "required": "actual source-to-entry/window states and checkpoint pressure at those actual boundaries",
            },
            "source_bindings": [
                {"path": p, "sha256": sha256((ROOT / p).read_bytes()).hexdigest()}
                for p in sorted(paths)
            ],
            "evidence": {"path": EVIDENCE, "sha256": sha256(raw).hexdigest()},
        }
    )
    (ROOT / RECORD).write_text(json.dumps(value, indent=2) + "\n")
    print(
        "C_PC_PRESSURE_PASS tests="
        + str(result.testsRun)
        + " seconds="
        + str(round(elapsed, 2)),
        flush=True,
    )
    return value


def check(root=ROOT, numerical=False):
    from p991a6_cpc_campaign_epoch import previous_bytes

    root = Path(root)
    v = json.loads((root / RECORD).read_bytes())
    need(
        v == seal(v) and v["schema"] == "grc9v4-native-cpc-pressure-v1",
        "unsealed pressure record",
    )
    need(
        v["test_roster"] == list(ROSTER) and v["tests_passed"] == len(ROSTER),
        "pressure roster mismatch",
    )
    need(
        v["full_trajectory_runs"] == 0
        and v["native_endpoint_verified"] is False
        and v["native_completion_support"] is False,
        "pressure endpoint scope",
    )
    for row in [*v["source_bindings"], v["evidence"]]:
        need(
            sha256(previous_bytes(root, row["path"])).hexdigest() == row["sha256"],
            "changed pressure subject: " + row["path"],
        )
    if numerical:
        from cpc_native_spark_oracle import from_transition
        from cpc_native_spark_pressure_oracle import audit_event, audit_step

        from pygrc.models.grc_9_v4_completion_certificate import CompletionCertificate
        from pygrc.models.grc_9_v4_spark_contracts import GRC9V4SparkConfiguration

        evidence = json.loads(lzma.decompress((root / EVIDENCE).read_bytes()))
        for row in [*evidence["actual_steps"], evidence["source_step"]]:
            step = from_transition(row["step"])
            config = GRC9V4SparkConfiguration.from_payload(row["subject"])
            cert = (
                CompletionCertificate.from_payload(row["certificate"])
                if "certificate" in row
                else None
            )
            need(
                audit_step(config, step.before, step, cert, row["role"])
                == row["audit"],
                "retained full C/Z audit differs",
            )
        for row in evidence["events"]:
            source = GRC9V4SparkConfiguration.from_payload(row["source"])
            target = GRC9V4SparkConfiguration.from_payload(row["target"])
            need(
                audit_event(source, target, row["event"]) == row["audit"],
                "retained history/event audit differs",
            )

    return v


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--numerical", action="store_true")
    args = parser.parse_args()
    run() if args.run else check(numerical=args.numerical)

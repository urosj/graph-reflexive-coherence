"""Run the bounded CI+PC pressure roster and retain source-bound results."""

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
from p991a6_ccipc_preflight import check as preflight_check
from p991a6_ccipc_preflight import seal
from test_ccipc_native_spark_pressure import CCIPCNativePressureTests

BASE = "implementation/phase-9-grcv4/tranche-9/"
HERE = "implementation/phase-9-grcv4/verification/"
RECORD = BASE + "P9-9.1a.6-CCIPC-Pressure.json"
EVIDENCE = BASE + "P9-9.1a.6-CCIPC-PressureSamples.json.xz"
SCRIPT = HERE + "p991a6_ccipc_pressure.py"
ROSTER = (
    "test_actual_C_and_Z_input_uncertainty_in_root_certificate",
    "test_actual_source_beat_preserves_distinct_reset_history",
    "test_actual_stages_frozen_inputs_and_complete_joint_error",
    "test_all_composite_transaction_faults_preserve_whole_publication",
    "test_archive_and_whole_target_mutations",
    "test_atomic_failures_at_preparation_window_and_publication",
    "test_checkpoints_at_each_window_boundary_and_observer_noninterference",
    "test_composite_norm_boundary_and_offdiagonal_factor",
    "test_duplicate_delivery_is_noop_in_ancestry_and_failed_request_retries",
    "test_equal_C_equal_norm_trace_different_patterns_and_roles",
    "test_event_whole_actual_archive_changed_support_and_regeneration",
    "test_exact_geometry_cancellation_retains_nonzero_writer",
    "test_independent_classifier_diamonds_unqualified_ties_singletons_thresholds",
    "test_inside_domain_without_event_cannot_earn_gain",
    "test_invalid_carrier_payloads_and_wrong_graph_binding",
    "test_joint_trap_boundary_all_coordinates_and_relabelled_proofs",
    "test_mixed_derivatives_and_rehashed_borrowed_certificates",
    "test_native_step_without_research_import_or_trajectory_read",
    "test_observer_snapshot_aliasing_zero_duration_and_migration",
    "test_rehashed_tuple_proposal_domain_and_noncommuting_mutations",
    "test_same_source_two_uses_and_gain_placement",
    "test_semantic_reset_target_and_poststate_failures",
    "test_signed_edge_permutation_covariance_and_untransported_binding",
    "test_solver_work_variants_failures_and_workspace_isolation",
    "test_uniform_signed_history_releases_without_resource_motion",
    "test_writer_primitive_held_source_semigroup_and_cancellation",
    "test_zero_Z_CI_read_then_history_is_consumed",
)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def run():
    import flint

    flint.ctx.threads = 1
    preflight = preflight_check(ROOT)
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(CCIPCNativePressureTests)
    need(
        tuple(t._testMethodName for t in suite) == ROSTER,
        "mandatory CI+PC pressure roster differs",
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
    need(elapsed < 300, "bounded pressure exceeded 300-second sampling allowance")
    print(output.getvalue(), flush=True)
    evidence = CCIPCNativePressureTests.evidence
    need(
        len(evidence["actual_steps"]) == 4, "four actual captured target steps required"
    )
    raw = lzma.compress(
        json.dumps(evidence, sort_keys=True, separators=(",", ":")).encode(), preset=6
    )
    (ROOT / EVIDENCE).write_bytes(raw)
    paths = {r["path"] for r in preflight["source_bindings"]} | {
        BASE + "P9-9.1a.6-CCIPC-Preflight.json",
        SCRIPT,
        HERE + "ccipc_native_spark_audit.py",
        HERE + "test_ccipc_native_spark_pressure.py",
        HERE + "test_cos_native_spark_pressure.py",
        HERE + "cpc_native_spark_pressure_oracle.py",
        "specs/grc-9-v4-spark-completion-applicability-source-manifest.json",
        "specs/grc-9-v4-spark-completion-earlier-source-manifest.json",
    }
    value = seal(
        {
            "schema": "grc9v4-native-ccipc-pressure-v1",
            "family": "C_CI_PC",
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
            "baseline_tests": preflight["tests"]["count"],
            "prior_60_direction_certificate_checks_retained": True,
            "sampling_cap_seconds": 300,
            "fixed_H_oracle_arithmetic": "exact FLINT rational",
            "preflight_record_digest": preflight["record_digest"],
            "measurements": CCIPCNativePressureTests.measurements,
            "scope": "bounded composite root, same-source geometry/writer, signed cancellation, C/Z uncertainty, event and lifecycle pressure; synthetic windows are not source-to-entry executions",
            "pending_campaign": {
                "leaf": "P9-9.1a.6-C_CI_PC.5",
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
        "C_CI_PC_PRESSURE_PASS tests="
        + str(result.testsRun)
        + " seconds="
        + str(round(elapsed, 2)),
        flush=True,
    )
    return value


def check(root=ROOT, numerical=False):
    previous_bytes = lambda root, name: (root / name).read_bytes()

    root = Path(root)
    v = json.loads((root / RECORD).read_bytes())
    need(
        v == seal(v) and v["schema"] == "grc9v4-native-ccipc-pressure-v1",
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
        from ccipc_native_spark_audit import audit_event, audit_step
        from ccipc_native_spark_oracle import from_transition

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
        # Cancellation is an additional exact rational supplied-state kernel
        # control, not a naturally reached trajectory or equilibrium.
        from pygrc.models.grc_v4_spark_carrier import exact_state

        cancellation = evidence["cancellation"]
        step = from_transition(cancellation["step"])
        from dataclasses import replace

        from p991a6_ccipc_subjects import configuration

        config = replace(configuration(), current=exact_state(cancellation["subject"]))
        need(
            audit_step(config, step.before, step) == cancellation["audit"],
            "cancellation audit differs",
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

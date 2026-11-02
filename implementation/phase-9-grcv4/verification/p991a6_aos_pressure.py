"""Run the bounded A_OS pressure roster and retain source-bound results."""

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
from p991a6_aos_preflight import check as preflight_check
from p991a6_aos_preflight import decoded, seal
from test_aos_native_spark_pressure import AOSNativePressureTests

BASE = "implementation/phase-9-grcv4/tranche-9/"
HERE = "implementation/phase-9-grcv4/verification/"
RECORD = BASE + "P9-9.1a.6-AOS-Pressure.json"
EVIDENCE = BASE + "P9-9.1a.6-AOS-PressureSamples.json.xz"
SCRIPT = HERE + "p991a6_aos_pressure.py"
ROSTER = (
    "test_OS_geometry_ownership_provisional_W_and_writer_retention_mutations",
    "test_all_transaction_faults_preserve_complete_C_W_publication",
    "test_corrector_current_and_pre_read_reference_mutations",
    "test_each_W_role_is_individually_discriminated",
    "test_equal_C_same_sum_W_and_next_read_consumes_written_history",
    "test_exact_weighted_rows_ports_empty_parallel_and_log_derivative",
    "test_fixed_H_W_roles_and_noncommuting_flat",
    "test_frozen_public_OS_stages_and_complete_map",
    "test_full_chart_near_faces_all_W_coordinates_and_relabelled_proofs",
    "test_log_writer_held_target_composition_and_no_arithmetic_average",
    "test_matched_total_current_formation_and_geometric_relaxation",
    "test_mixed_C_logW_derivatives_away_from_equilibrium",
    "test_native_execution_without_research_files_or_imports",
    "test_neutral_signed_and_extreme_contrast_primitives",
    "test_nonuniform_event_lineage_both_roles_and_chiralities",
    "test_observers_aliasing_equal_C_roles_and_unsupported_durations",
    "test_rehashed_event_allocation_and_history_mutations_reject",
    "test_reset_only_event_failure_is_atomic_and_preserves_old_histories",
    "test_signed_edge_reindexing_permutes_W_without_sign",
    "test_smooth_floor_and_invalid_history_domains_fail_closed",
    "test_spectral_split_equality_outside_and_Frobenius_distinction",
    "test_uniform_C_writes_W_without_current_or_resource_motion",
    "test_weighted_classifier_thresholds_and_committed_history",
    "test_window_replay_replacement_and_once_only_accounting",
    "test_writer_stage_alternatives_are_resolved_and_rejected",
)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def run():
    import flint

    flint.ctx.threads = 1
    preflight = preflight_check(ROOT)
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(AOSNativePressureTests)
    need(
        tuple(t._testMethodName for t in suite) == ROSTER,
        "mandatory A_OS pressure roster differs",
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
    AOSNativePressureTests.measurements["mutations"].sort()
    elapsed = time.perf_counter() - start
    need(elapsed < 300, "bounded pressure exceeded 300-second sampling allowance")
    print(output.getvalue(), flush=True)
    evidence = AOSNativePressureTests.evidence
    need(len(evidence["events"]) == 2, "two nonuniform chiral event archives")
    need(
        len(evidence["actual_steps"]) == 4, "four actual captured target steps required"
    )
    raw = lzma.compress(
        json.dumps(evidence, sort_keys=True, separators=(",", ":")).encode(), preset=6
    )
    (ROOT / EVIDENCE).write_bytes(raw)
    paths = {r["path"] for r in preflight["source_bindings"]} | {
        BASE + "P9-9.1a.6-AOS-Preflight.json.xz",
        SCRIPT,
        HERE + "aos_native_spark_audit.py",
        HERE + "test_aos_native_spark_pressure.py",
        HERE + "test_cos_native_spark_pressure.py",
        HERE + "cpc_native_spark_pressure_oracle.py",
        "specs/grc-9-v4-spark-completion-applicability-source-manifest.json",
        "specs/grc-9-v4-spark-completion-earlier-source-manifest.json",
    }
    value = seal(
        {
            "schema": "grc9v4-native-aos-pressure-v1",
            "family": "A_OS",
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
            "prior_30_direction_certificate_checks_retained": True,
            "sampling_cap_seconds": 300,
            "fixed_H_oracle_arithmetic": "independent FLINT/Arb768 edge assembly",
            "preflight_record_digest": preflight["record_digest"],
            "measurements": AOSNativePressureTests.measurements,
            "mutation_detectors": len(AOSNativePressureTests.measurements["mutations"]),
            "scope": "bounded complete W causal loop, exact weighted rows, OS staging, log writer, full C/logW map, lineage, classifier and lifecycle pressure; synthetic windows are not source-to-entry executions",
            "pending_campaign": {
                "leaf": "P9-9.1a.6-A_OS.5",
                "current": [375, 377],
                "reset": [372, 374],
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
        "A_OS_PRESSURE_PASS tests="
        + str(result.testsRun)
        + " seconds="
        + str(round(elapsed, 2)),
        flush=True,
    )
    return value


def check(root=ROOT, numerical=False):
    from p991a6_aci_epoch import previous_bytes

    root = Path(root)
    v = json.loads((root / RECORD).read_bytes())
    need(
        v == seal(v) and v["schema"] == "grc9v4-native-aos-pressure-v1",
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
        from aos_native_spark_audit import audit_event, audit_step

        from pygrc.models.grc_9_v4_completion_certificate import CompletionCertificate
        from pygrc.models.grc_9_v4_spark_contracts import GRC9V4SparkConfiguration

        evidence = json.loads(lzma.decompress((root / EVIDENCE).read_bytes()))
        for row in [*evidence["actual_steps"], evidence["source_step"]]:
            step = decoded(row["step"])
            config = GRC9V4SparkConfiguration.from_payload(row["subject"])
            cert = (
                CompletionCertificate.from_payload(row["certificate"])
                if "certificate" in row
                else None
            )
            need(
                audit_step(config, step.before, step, cert, row["role"])
                == row["audit"],
                "retained full C/W audit differs",
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

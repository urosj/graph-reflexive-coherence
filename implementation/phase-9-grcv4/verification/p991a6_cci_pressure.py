"""Run the bounded mandatory CI pressure roster and retain source-bound results."""

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
from p991a6_cci_preflight import check as preflight_check
from p991a6_cci_preflight import seal
from test_cci_native_spark_pressure import CCINativePressureTests

BASE = "implementation/phase-9-grcv4/tranche-9/"
HERE = "implementation/phase-9-grcv4/verification/"
RECORD = BASE + "P9-9.1a.6-CCI-Pressure.json"
EVIDENCE = BASE + "P9-9.1a.6-CCI-PressureSamples.json.xz"
SCRIPT = HERE + "p991a6_cci_pressure.py"
ROSTER = (
    "test_CI_specific_faults_roll_back_and_retry_final_window",
    "test_OS_source_poststate_and_split_admission_do_not_substitute_CI",
    "test_actual_frozen_input_two_roots_one_write_and_error_decomposition",
    "test_atomic_failures_at_preparation_window_and_publication",
    "test_charge_chart_faces_and_charge_normal_projection_trap",
    "test_checkpoints_at_each_window_boundary_and_observer_noninterference",
    "test_cold_load_root_failure_registers_no_partial_owner",
    "test_duplicate_delivery_is_noop_in_ancestry_and_failed_request_retries",
    "test_fixed_H_or_regenerated_H_alone_is_not_joint_root_authority",
    "test_full_implicit_derivative_all_14_finite_segments",
    "test_graph_same_sizes_profile_migration_and_no_proposal_history",
    "test_independent_classifier_diamonds_unqualified_ties_singletons_thresholds",
    "test_inside_domain_without_event_cannot_earn_gain",
    "test_literal_both_chiral_events_and_role_transfer",
    "test_native_execution_has_no_research_or_saved_trajectory_dependency",
    "test_rehashed_certificate_semantic_corruption",
    "test_rehashed_root_mutations_have_specific_mathematical_discriminators",
    "test_residual_upper_endpoint_and_graph_specific_root_bounds",
    "test_root_contraction_cannot_replace_physical_certificate",
    "test_stagnation_nonfinite_and_iteration_limit_fail_without_progress",
    "test_target_and_reset_only_reconstruction_are_atomic",
    "test_uniform_root_is_not_a_child_or_event",
)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def run():
    import flint

    flint.ctx.threads = 1
    preflight = preflight_check(ROOT)
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(CCINativePressureTests)
    need(
        tuple(t._testMethodName for t in suite) == ROSTER,
        "mandatory CI pressure roster differs",
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
    print(output.getvalue(), flush=True)
    evidence = CCINativePressureTests.evidence
    need(
        len(evidence["actual_steps"]) == 4, "four actual captured target steps required"
    )
    raw = lzma.compress(
        json.dumps(evidence, sort_keys=True, separators=(",", ":")).encode(), preset=6
    )
    (ROOT / EVIDENCE).write_bytes(raw)
    paths = {r["path"] for r in preflight["source_bindings"]} | {
        BASE + "P9-9.1a.6-CCI-Preflight.json",
        SCRIPT,
        HERE + "cci_native_spark_pressure_oracle.py",
        HERE + "test_cci_native_spark_pressure.py",
        HERE + "test_cos_native_spark_pressure.py",
        "specs/grc-9-v4-spark-completion-applicability-source-manifest.json",
        "specs/grc-9-v4-spark-completion-earlier-source-manifest.json",
    }
    value = seal(
        {
            "schema": "grc9v4-native-cci-pressure-v1",
            "family": "C_CI",
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
            "preflight_record_digest": preflight["record_digest"],
            "measurements": CCINativePressureTests.measurements,
            "scope": "bounded root/map/freshness/certificate/event/lifecycle pressure; synthetic windows are not source-to-entry executions",
            "pending_campaign": {
                "leaf": "P9-9.1a.6-C_CI.5",
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
        "C_CI_PRESSURE_PASS tests="
        + str(result.testsRun)
        + " seconds="
        + str(round(elapsed, 2)),
        flush=True,
    )
    return value


def check(root=ROOT, numerical=False):
    root = Path(root)
    v = json.loads((root / RECORD).read_bytes())
    need(
        v == seal(v) and v["schema"] == "grc9v4-native-cci-pressure-v1",
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
            sha256((root / row["path"]).read_bytes()).hexdigest() == row["sha256"],
            "changed pressure subject: " + row["path"],
        )
    if numerical:
        from cci_native_spark_pressure_oracle import audit_step

        from pygrc.models.grc_9_v4_completion_certificate import CompletionCertificate
        from pygrc.models.grc_9_v4_spark_contracts import GRC9V4SparkConfiguration
        from pygrc.models.grc_v4_geometry import GRCV4Graph
        from pygrc.models.grc_v4_spark_cci import SparkCCIStep
        from pygrc.models.grc_v4_spark_state import ExactResources
        from pygrc.models.grc_v4_state import FrozenJSONMap

        def state(x):
            return ExactResources(
                GRCV4Graph.from_payload(x["graph"]), tuple(x["C"]), x["charge"]
            )

        evidence = json.loads(lzma.decompress((root / EVIDENCE).read_bytes()))
        for row in [*evidence["actual_steps"], evidence["source_discriminator"]]:
            data = row["step"]
            step = SparkCCIStep(
                state(data["before"]),
                state(data["after"]),
                data["profile_id"],
                data["duration"],
                tuple(data["flux"]),
                tuple(data["componentwise_error_bounds"]),
                FrozenJSONMap(data["root"]),
                FrozenJSONMap(data["restart_root"]),
                tuple(tuple(x) for x in data["final_current"]),
                tuple(data["reference_current"]),
            )
            config = GRC9V4SparkConfiguration.from_payload(row["subject"])
            cert = (
                CompletionCertificate.from_payload(row["certificate"])
                if "certificate" in row
                else None
            )
            need(
                audit_step(config, step.before, step, cert, role=row["role"])
                == row["audit"],
                "retained full-root audit differs",
            )
    return v


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--numerical", action="store_true")
    args = parser.parse_args()
    run() if args.run else check(numerical=args.numerical)

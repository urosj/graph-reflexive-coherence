"""Retain the bounded A_RG2b pressure roster and its independently replayable operands."""

import argparse
import json
import lzma
import sys
import time
import unittest
from hashlib import sha256
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / "src")]
from p991a6_arg2b_preflight import check as preflight_check
from p991a6_arg2b_preflight import decoded, seal
from test_arg2b_native_spark_pressure import ARG2bPressureTests

BASE = "implementation/phase-9-grcv4/tranche-9/"
HERE = "implementation/phase-9-grcv4/verification/"
RECORD = BASE + "P9-9.1a.6-ARG2b-Pressure.json"
EVIDENCE = BASE + "P9-9.1a.6-ARG2b-PressureSamples.json.xz"
SCRIPT = HERE + "p991a6_arg2b_pressure.py"
ROSTER = (
    "test_Taylor_factorials_cell_scaling_and_full_writer_series",
    "test_actual_event_lineage_and_committed_W_classifier",
    "test_all_thirty_tube_directions_and_history_scale",
    "test_bounded_completion_window_no_source_endpoint_claim",
    "test_cache_full_history_displacement_state_only_and_detached_values",
    "test_continuous_certificate_rehashed_corruptions_and_common_hull",
    "test_deep_history_auxiliary_writer_and_postwriter_failures_atomic",
    "test_every_inverse_history_coordinate_and_separate_tail",
    "test_final_C_writer_is_not_retracted_again",
    "test_fixed_H_map_duration_decay_and_writer_stage_discriminators",
    "test_full_physical_error_independent_writer_and_charge",
    "test_manufactured_joint_chains_and_history_only_counterfeit",
    "test_reset_only_event_failure_equal_C_different_W_and_observation_purity",
    "test_scaled_history_clipping_and_exterior_base_identity",
    "test_scaled_logW_derivatives_and_unfrozen_weighted_rows",
    "test_shared_parameter_membership_not_separate_projections",
    "test_unrounded_time_shift_and_two_W_routes",
    "test_vertex_chart_transport_and_wrong_source_chart",
)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def run():
    import flint

    flint.ctx.threads = 1
    need(
        not (ROOT / RECORD).exists() and not (ROOT / EVIDENCE).exists(),
        "refuse pressure overwrite",
    )
    preflight = preflight_check(ROOT)
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(ARG2bPressureTests)
    need(tuple(t._testMethodName for t in suite) == ROSTER, "mandatory pressure roster")
    start = time.perf_counter()
    result = unittest.TextTestRunner(stream=sys.stdout, verbosity=2).run(suite)
    need(
        result.wasSuccessful()
        and result.testsRun == len(ROSTER)
        and not result.skipped
        and not result.expectedFailures,
        "bounded pressure failed",
    )
    elapsed = time.perf_counter() - start
    need(elapsed < 600, "bounded sampling allowance exceeded")
    measurements = ARG2bPressureTests.measurements
    measurements["mutations"].sort(key=lambda row: row["label"])
    evidence = ARG2bPressureTests.evidence
    raw = lzma.compress(
        json.dumps(evidence, sort_keys=True, separators=(",", ":")).encode(), preset=6
    )
    (ROOT / EVIDENCE).write_bytes(raw)
    paths = {r["path"] for r in preflight["source_bindings"]} | {
        BASE + "P9-9.1a.6-ARG2b-Preflight.json.xz",
        SCRIPT,
        HERE + "arg2b_native_spark_pressure_oracle.py",
        HERE + "test_arg2b_native_spark_pressure.py",
    }
    value = seal(
        {
            "schema": "grc9v4-native-arg2b-pressure-v1",
            "family": "A_RG2b",
            "status": "verified_pending_review",
            "tests_passed": len(ROSTER),
            "test_roster": list(ROSTER),
            "elapsed_seconds": elapsed,
            "sampling_cap_seconds": 600,
            "runtime_changed": False,
            "native_endpoint_verified": False,
            "native_completion_support": False,
            "full_trajectory_runs": 0,
            "production_precision_bits": 256,
            "oracle_precision_bits": 768,
            "duration": "16",
            "state_channels": ["C", "W_A"],
            "baseline_tests": preflight["tests"]["count"],
            "preflight_record_digest": preflight["record_digest"],
            "measurements": measurements,
            "scope": "bounded joint inverse C/scaled-logW residuals and full writer, finite manufactured chains, unrounded time shift, history cache isolation, shared-parameter continuous domain and atomic lifecycle; both .5 campaigns deferred",
            "deferred_campaigns": ["C_RG2b.5", "A_RG2b.5"],
            "pending_campaign": {
                "leaf": "P9-9.1a.6-A_RG2b.5",
                "current": [300, 302],
                "reset": [300, 302],
                "expected_endpoints_verified": False,
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
        f"A_RG2b_PRESSURE_PASS tests={len(ROSTER)} seconds={elapsed:.2f} evidence_bytes={len(raw)}",
        flush=True,
    )
    return value


def check(root=ROOT, numerical=False):
    root = Path(root)
    value = json.loads((root / RECORD).read_bytes())
    need(
        value == seal(value) and value["schema"] == "grc9v4-native-arg2b-pressure-v1",
        "pressure seal",
    )
    need(
        value["test_roster"] == list(ROSTER) and value["tests_passed"] == len(ROSTER),
        "pressure roster",
    )
    need(
        value["native_endpoint_verified"] is False
        and value["native_completion_support"] is False
        and value["full_trajectory_runs"] == 0
        and value["runtime_changed"] is False,
        "pressure scope",
    )
    preflight = preflight_check(root)
    need(
        value["preflight_record_digest"] == preflight["record_digest"],
        "preflight binding",
    )
    for row in [*value["source_bindings"], value["evidence"]]:
        p = root / row["path"]
        need(
            p.resolve().is_relative_to(root.resolve())
            and sha256(p.read_bytes()).hexdigest() == row["sha256"],
            "changed pressure source: " + row["path"],
        )
    if numerical:
        import arg2b_native_spark_pressure_oracle as audit
        from arg2b_native_spark_oracle import verify_step
        from flint import ctx

        from pygrc.models.grc_9_v4_completion_certificate import CompletionCertificate
        from pygrc.models.grc_9_v4_spark_contracts import GRC9V4SparkConfiguration

        e = json.loads(lzma.decompress((root / EVIDENCE).read_bytes()))
        subject = GRC9V4SparkConfiguration.from_payload(e["subject"])
        source = subject.reference.graph.to_payload()
        CompletionCertificate.from_payload(e["certificate"])
        with ctx.workprec(768):
            for fixture in e["manufactured"].values():
                audit.manufactured_check(source, fixture)
            for role, row in e["steps"].items():
                step = decoded(row)
                need(step.before == getattr(subject, role), "external role subject")
                for state, witness in (
                    (step.before, step.section),
                    (step.after, step.restart_section),
                ):
                    audit.audit_read(
                        subject.reference.graph.to_payload(),
                        subject.reference.profile.to_payload(),
                        state,
                        witness,
                    )
                verify_step(subject, step.before, step)
            need(
                audit.time_shift(
                    subject.reference.graph.to_payload(),
                    subject.reference.profile.to_payload(),
                    subject.current,
                    decoded(e["steps"]["current"]).section,
                )
                == e["time_shift"],
                "joint time-shift replay",
            )
    return value


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--numerical", action="store_true")
    args = parser.parse_args()
    if args.check:
        check(numerical=args.numerical)
        print("A_RG2b_PRESSURE_CHECK_PASS")
    else:
        run()

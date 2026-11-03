"""Retain the bounded C_RG2b pressure roster and its independently replayable operands."""

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
from p991a6_crg2b_preflight import check as preflight_check
from p991a6_crg2b_preflight import decoded, seal
from test_crg2b_native_spark_pressure import CRG2bPressureTests

BASE = "implementation/phase-9-grcv4/tranche-9/"
HERE = "implementation/phase-9-grcv4/verification/"
RECORD = BASE + "P9-9.1a.6-CRG2b-Pressure.json"
EVIDENCE = BASE + "P9-9.1a.6-CRG2b-PressureSamples.json.xz"
SCRIPT = HERE + "p991a6_crg2b_pressure.py"
ROSTER = (
    "test_actual_event_preserves_both_source_allocations_and_reset",
    "test_all_chain_levels_and_separate_error_terms",
    "test_all_tangent_directions_boundary_parameters_and_charge",
    "test_argument_only_clipping_signed_auxiliary_and_overlap_multiplicity",
    "test_cache_poison_is_detached_and_cross_subject_reuse_rejected",
    "test_certificate_rejects_sampled_truncated_and_reference_only_proofs",
    "test_cold_warm_cleared_state_only_reconstruction",
    "test_corrected_charts_duration_and_complete_external_binding",
    "test_deepest_inverse_fixed_solve_and_returned_failures_retry_atomically",
    "test_exact_chebyshev_composition_and_degree120_residual",
    "test_exact_manufactured_one_and_two_inverse_levels",
    "test_full_represented_error_and_exact_charge_are_separate",
    "test_reset_only_event_readmission_failure_and_observer_purity",
    "test_time_shift_on_unrounded_image_not_same_state_root",
    "test_wrong_CI_and_OS_geometry_substitutions",
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
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(CRG2bPressureTests)
    need(tuple(t._testMethodName for t in suite) == ROSTER, "mandatory pressure roster")
    output = io.StringIO()
    start = time.perf_counter()
    result = unittest.TextTestRunner(stream=output, verbosity=2).run(suite)
    print(output.getvalue(), flush=True)
    need(
        result.wasSuccessful()
        and result.testsRun == len(ROSTER)
        and not result.skipped
        and not result.expectedFailures,
        "bounded pressure failed",
    )
    elapsed = time.perf_counter() - start
    need(elapsed < 600, "bounded sampling allowance exceeded")
    measurements = CRG2bPressureTests.measurements
    measurements["mutations"].sort()
    evidence = CRG2bPressureTests.evidence
    raw = lzma.compress(
        json.dumps(evidence, sort_keys=True, separators=(",", ":")).encode(), preset=6
    )
    (ROOT / EVIDENCE).write_bytes(raw)
    paths = {r["path"] for r in preflight["source_bindings"]} | {
        BASE + "P9-9.1a.6-CRG2b-Preflight.json.xz",
        SCRIPT,
        HERE + "crg2b_native_spark_pressure_oracle.py",
        HERE + "test_crg2b_native_spark_pressure.py",
    }
    value = seal(
        {
            "schema": "grc9v4-native-crg2b-pressure-v1",
            "family": "C_RG2b",
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
            "duration": "8",
            "state_channels": ["C"],
            "baseline_tests": preflight["tests"]["count"],
            "preflight_record_digest": preflight["record_digest"],
            "measurements": measurements,
            "scope": "bounded exact finite chains, time-shift law at the unrounded image, complete chain and external subject audit, C-only cache independence, continuous curved-domain proof and atomic lifecycle; no .5 trajectory",
            "pending_campaign": {
                "leaf": "P9-9.1a.6-C_RG2b.5",
                "current": [390, 392],
                "reset": [390, 392],
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
        f"C_RG2b_PRESSURE_PASS tests={len(ROSTER)} seconds={elapsed:.2f} evidence_bytes={len(raw)}",
        flush=True,
    )
    return value


def check(root=ROOT, numerical=False):
    root = Path(root)
    value = json.loads((root / RECORD).read_bytes())
    need(
        value == seal(value) and value["schema"] == "grc9v4-native-crg2b-pressure-v1",
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
        import crg2b_native_spark_pressure_oracle as audit
        from crg2b_native_spark_oracle import verify_step
        from flint import ctx
        from p991a6_crg2b_subjects import configuration

        from pygrc.models.grc_9_v4_completion_certificate import CompletionCertificate
        from pygrc.models.grc_9_v4_spark_contracts import GRC9V4SparkConfiguration

        e = json.loads(lzma.decompress((root / EVIDENCE).read_bytes()))
        subject = GRC9V4SparkConfiguration.from_payload(e["subject"])
        source = configuration().reference.graph.to_payload()
        for rows in e["manufactured"].values():
            audit.exact_chain(source, rows)
        CompletionCertificate.from_payload(e["certificate"])
        with ctx.workprec(768):
            for role, row in e["steps"].items():
                step = decoded(row)
                need(step.before == getattr(subject, role), "external role subject")
                audit.audit_read(
                    subject.reference.graph.to_payload(),
                    subject.reference.profile.to_payload(),
                    step.before,
                    step.section,
                )
                audit.audit_read(
                    subject.reference.graph.to_payload(),
                    subject.reference.profile.to_payload(),
                    step.after,
                    step.restart_section,
                )
                verify_step(step, fresh=False)
            need(
                audit.time_shift(
                    subject.reference.graph.to_payload(),
                    subject.reference.profile.to_payload(),
                    subject.current,
                    decoded(e["steps"]["current"]).section,
                )
                == e["time_shift"],
                "time-shift replay",
            )
    return value


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--numerical", action="store_true")
    args = parser.parse_args()
    if args.check:
        check(numerical=args.numerical)
        print("C_RG2b_PRESSURE_CHECK_PASS")
    else:
        run()

"""Run the bounded A_CI_PC pressure roster and retain source-bound results."""

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
from p991a6_acipc_preflight import check as preflight_check
from p991a6_acipc_preflight import decoded, seal
from test_acipc_native_spark_pressure import ACIPCNativePressureTests

BASE = "implementation/phase-9-grcv4/tranche-9/"
HERE = "implementation/phase-9-grcv4/verification/"
RECORD = BASE + "P9-9.1a.6-ACIPC-Pressure.json"
EVIDENCE = BASE + "P9-9.1a.6-ACIPC-PressureSamples.json.xz"
SCRIPT = HERE + "p991a6_acipc_pressure.py"
ROSTER = (
    "test_all_76_directions_mixed_segments_and_nine_jacobian_blocks",
    "test_complete_root_tuple_sign_and_cross_writer_identity",
    "test_detached_writer_order_and_conditional_independences",
    "test_every_native_trial_refreshes_A_chain_on_frozen_inputs",
    "test_floor_and_carrier_boundaries_are_independent",
    "test_four_cross_history_inputs_and_four_returned_consumers",
    "test_frozen_public_two_writer_stages_and_complete_map",
    "test_frozen_reference_counterfeit_converges_and_is_rejected",
    "test_full_state_admission_and_last_off_diagonal_frobenius_weight",
    "test_late_three_coordinate_failures_roll_back_and_retry_once",
    "test_manufactured_reference_H_and_equal_current_twin",
    "test_nonuniform_event_lineage_and_complete_carrier_loss_both_chiralities",
    "test_observers_and_archives_do_not_alias_or_advance_either_history",
    "test_proposals_stagnation_and_trial_work_do_not_acquire_authority",
    "test_rehashed_event_history_and_allocation_mutations",
    "test_reset_only_and_event_archive_failures_are_atomic",
    "test_signed_carrier_cancellation_encloses_without_projection",
    "test_signed_reindexing_permutes_W_and_conjugates_Z",
    "test_source_Z_effect_survives_event_in_transferred_C_W",
    "test_tiny_authoritative_Z_is_not_recovered_from_H",
    "test_tiny_contrast_does_not_hide_conductance_writer_activity",
    "test_trial_chain_derivative_reference_and_residual_purity",
    "test_unequal_time_constants_only_at_configurable_primitives",
    "test_uniform_resource_simultaneous_history_relaxation",
    "test_wrong_writer_time_stages_reject_after_rehash",
    "test_zero_carrier_target_requires_composite_readmission",
)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def run():
    import flint

    flint.ctx.threads = 1
    need(
        not (ROOT / RECORD).exists() and not (ROOT / EVIDENCE).exists(),
        "refuse to overwrite retained pressure evidence",
    )
    preflight = preflight_check(ROOT)
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(ACIPCNativePressureTests)
    need(
        tuple(t._testMethodName for t in suite) == ROSTER,
        "mandatory A_CI_PC pressure roster differs",
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
    ACIPCNativePressureTests.measurements["mutations"].sort()
    elapsed = time.perf_counter() - start
    need(elapsed < 300, "bounded pressure exceeded 300-second sampling allowance")
    print(output.getvalue(), flush=True)
    evidence = ACIPCNativePressureTests.evidence
    from acipc_native_spark_pressure_oracle import audit_counterfeit, audit_twins

    with flint.ctx.workprec(768):
        evidence["manufactured_audit"] = audit_twins(evidence["manufactured"])
        evidence["counterfeit_audit"] = audit_counterfeit(evidence["counterfeit"])
    need(len(evidence["events"]) == 2, "two nonuniform chiral event archives")
    need(
        len(evidence["actual_steps"]) == 4, "four actual captured target steps required"
    )
    raw = lzma.compress(
        json.dumps(evidence, sort_keys=True, separators=(",", ":")).encode(), preset=6
    )
    (ROOT / EVIDENCE).write_bytes(raw)
    paths = {r["path"] for r in preflight["source_bindings"]} | {
        BASE + "P9-9.1a.6-ACIPC-Preflight.json.xz",
        SCRIPT,
        HERE + "acipc_native_spark_audit.py",
        HERE + "acipc_native_spark_pressure_oracle.py",
        HERE + "aci_native_spark_oracle.py",
        "src/pygrc/models/grc_v4_candidate_a.py",
        "src/pygrc/models/grc_v4_pc.py",
        HERE + "test_acipc_native_spark_pressure.py",
        HERE + "cpc_native_spark_pressure_oracle.py",
        "specs/grc-9-v4-spark-completion-applicability-source-manifest.json",
        "specs/grc-9-v4-spark-completion-earlier-source-manifest.json",
    }
    value = seal(
        {
            "schema": "grc9v4-native-acipc-pressure-v1",
            "family": "A_CI_PC",
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
            "prior_76_direction_certificate_checks_retained": True,
            "sampling_cap_seconds": 300,
            "fixed_H_oracle_arithmetic": "independent FLINT/Arb768 edge assembly; explicit polynomial multiplication on zero-crossing intervals",
            "preflight_record_digest": preflight["record_digest"],
            "measurements": ACIPCNativePressureTests.measurements,
            "operand_trace_retained": True,
            "mutation_detectors": len(
                ACIPCNativePressureTests.measurements["mutations"]
            ),
            "scope": "bounded composite root and dual-history pressure, manufactured equal-current roots, frozen-reference counterfeit, 240 finite segments, event readmission and full-state rollback; no source-to-entry campaign",
            "pending_campaign": {
                "leaf": "P9-9.1a.6-A_CI_PC.5",
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
        "A_CI_PC_PRESSURE_PASS tests="
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
        v == seal(v) and v["schema"] == "grc9v4-native-acipc-pressure-v1",
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
        from acipc_native_spark_audit import (
            audit_event,
            audit_step,
            audit_trace,
            audit_trials,
        )

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
                "retained full C/W/Z audit differs",
            )
        need(
            audit_trace(
                decoded(evidence["actual_steps"][0]["step"]), evidence["operand_trace"]
            )
            == evidence["operand_trace_audit"],
            "retained root/drive operand trace differs",
        )
        from acipc_native_spark_pressure_oracle import audit_counterfeit, audit_twins
        from flint import ctx

        with ctx.workprec(768):
            need(
                audit_twins(evidence["manufactured"]) == evidence["manufactured_audit"],
                "retained manufactured twin audit differs",
            )
            need(
                audit_counterfeit(evidence["counterfeit"])
                == evidence["counterfeit_audit"],
                "retained counterfeit audit differs",
            )
        trials = evidence["root_trials"]
        need(
            audit_trials(decoded(trials["step"]), trials["roots"]) == trials["audit"],
            "retained trial chain differs",
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

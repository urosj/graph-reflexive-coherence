"""Bounded native A_CI_PC contract/numerics/lifecycle/preflight; never a campaign."""

import argparse
import io
import json
import lzma
import platform
import sys
import time
import unittest
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / "src")]
import flint
from acipc_native_spark_oracle import verify_step

comparison_verify = verify_step
from p991a4_native_spark_preflight import estimate as base_estimate
from p991a4_native_spark_preflight import need, rss, seal, timed
from p991a6_acipc_subjects import certificate_pair, configuration, request

from pygrc.models import grc_9_v4_completion_certificate as certificates
from pygrc.models import grc_9_v4_spark_owner as owner
from pygrc.models import grc_v4_spark_acipc as acipc
from pygrc.models.grc_9_v4 import GRC9V4
from pygrc.models.grc_9_v4_completion_certificate import CompletionCertificate
from pygrc.models.grc_v4_spark_adaptive_carrier import (
    ACIPC_NUMERICAL_POLICY,
    ExactAdaptiveCarrierState,
)
from pygrc.models.grc_v4_spark_conductance import _fixed_rows
from pygrc.models.grc_v4_spark_cos import _reference_facts
from pygrc.models.grc_v4_spark_cpc import _decay
from tests.models.test_grc_v4_spark_acipc import NativeACIPCTests

BASE = "implementation/phase-9-grcv4/tranche-9/"
HERE = "implementation/phase-9-grcv4/verification/"
RECORD = BASE + "P9-9.1a.6-ACIPC-Preflight.json.xz"
EVIDENCE = BASE + "P9-9.1a.6-ACIPC-Samples.json.xz"
SCRIPT = HERE + "p991a6_acipc_preflight.py"


def estimate(*args, cold_restore_seconds=0, sample_count=40):
    value = base_estimate(*args)
    # The preceding C_CI campaign needed two expensive pressure/checkpoint
    # phases. Reserve four minutes in addition to measured sampling costs.
    value["pressure_checkpoint_reserve_seconds"] = 240
    value["central_seconds"] += 240
    value["upper_seconds"] += 240
    cold = 2 * 400 / sample_count * cold_restore_seconds
    value["cold_replay_allowance"] = {
        "assumed_full_journal_restores": 2,
        "measured_sample_checkpoint_seconds": cold_restore_seconds,
        "sample_target_steps": sample_count,
        "central_seconds": cold,
        "upper_seconds": 2 * cold,
        "scope": "linear early-journal extrapolation; remeasure actual late checkpoints before .5",
    }
    value["central_seconds"] += cold
    value["upper_seconds"] += 2 * cold
    value["within_budget"] = value["upper_seconds"] < 1800
    value["profiling_target_seconds"] = value.pop("campaign_cap_seconds")
    value["timing_policy"] = (
        "profile_and_reestimate; valid execution is not stopped for exceeding 30 minutes"
    )
    value["cold_restore_scope"] = (
        "early checkpoint measured; re-estimate late journal replay and publication before .5"
    )
    return value


def independent_membership(model, certificate):
    from acipc_native_spark_oracle import classify as independent_classify
    from cos_native_spark_oracle import matrix
    from flint import arb, arb_mat, ctx
    from flint import fmpq as Q

    from pygrc.models.grc_9_v4_completion import classify
    from pygrc.models.grc_v4_certification import _ARB_CONTEXT_LOCK

    state = model.configuration.current
    inside, native_upper = certificate.membership(state)
    with _ARB_CONTEXT_LOCK, ctx.workprec(768):
        delta = arb_mat(
            [
                [Q(x) - Q(c)]
                for x, c in zip(state.C, certificate.operands["center"], strict=True)
            ]
            + [
                [arb(Q(w)).log() - Q(c)]
                for w, c in zip(
                    state.W_A, certificate.operands["logW_center"], strict=True
                )
            ]
        )
        coordinates = arb_mat(matrix(certificate.operands["U"])) * delta
        upper = max(abs(x).upper().fmpq() for x in coordinates.entries())
        lower = max(abs(x).lower().fmpq() for x in coordinates.entries())
        zsq = (
            sum(Q(x) ** 2 for row in state.Z_4 for x in row)
            / Q(certificate.operands["carrier_radius"]) ** 2
        )
        upper, lower = max(upper * upper, zsq), max(lower * lower, zsq)
        need(
            upper <= Q(native_upper)
            and ((inside and upper <= 1) or (not inside and lower > 1)),
            "independent complete logarithmic membership",
        )
    expected = independent_classify(
        state.graph.to_payload(),
        state.C,
        state.W_A,
        model.configuration.policy.to_payload(),
    )
    actual = classify(state, model.configuration.policy)
    need(
        (actual.basins, actual.terminals, [x.to_dict() for x in actual.rows])
        == expected,
        "independent exact weighted classification",
    )
    return {
        "norm_upper": native_upper,
        "independent_upper": str(upper),
        "inside": inside,
        "row": actual.to_payload(),
    }


def transition(step):
    return {
        "before": step.before.to_payload(),
        "after": step.after.to_payload(),
        "duration": step.duration,
        "profile_id": step.profile_id,
        "flux": list(step.flux),
        "componentwise_error_bounds": list(step.componentwise_error_bounds),
        "consumed_read": step.consumed_read.to_dict(),
        "writer": step.writer.to_dict(),
        "restart_read": step.restart_read.to_dict(),
        "log_conductance_component_error": step.log_conductance_component_error,
        "carrier_component_error": step.carrier_component_error,
        "carrier_writer": step.carrier_writer.to_dict(),
        "final_current": [list(x) for x in step.final_current],
        "reference_current": [list(x) for x in step.reference_current],
        "numerical_policy_id": step.numerical_policy_id,
    }


def compact_transition(step):
    value = transition(step)
    for name in ("consumed_read", "restart_read"):
        value[name] = {
            k: value[name][k]
            for k in (
                "subject_digest",
                "current_midpoint",
                "precision_bits",
                "numerical_policy_id",
                "residual_upper",
                "conditioning_upper",
                "domain",
                "proposal",
                "root_error",
                "proposal_residual",
                "joint_residual_upper",
                "iterations",
            )
        }
    value["writer"] = {
        k: v
        for k, v in value["writer"].items()
        if k not in ("selected_current", "exponent", "ideal")
    }
    value["carrier_writer"] = {
        k: v for k, v in value["carrier_writer"].items() if k not in ("source", "ideal")
    }
    return value


def decoded(value):
    from pygrc.models.grc_v4_spark_carrier import exact_state
    from pygrc.models.grc_v4_state import FrozenJSONMap

    data = dict(value)
    data.pop("numerical_policy_id")
    for name in ("before", "after"):
        data[name] = exact_state(data[name])
    for name in ("consumed_read", "restart_read", "writer", "carrier_writer"):
        data[name] = FrozenJSONMap(data[name])
    for name in ("flux", "componentwise_error_bounds"):
        data[name] = tuple(data[name])
    for name in ("final_current", "reference_current"):
        data[name] = tuple(tuple(x) for x in data[name])
    return acipc.SparkACIPCStep(**data)


def encoded(value):
    return lzma.compress(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode(), preset=3
    )


def precision_comparison():
    """An experimental precision override, never an execution-policy certificate."""
    rows = []
    for bits in (256, 512):
        with patch.object(acipc, "PRECISION", bits):
            certificates._verify.cache_clear()
            model = GRC9V4(configuration())
            need(model.step().committed, "precision source")
            need(model.expand(request(model)).committed, "precision event")
            (pair, _), seconds = timed(certificate_pair, model)
            states = {}
            costs = []
            for role in ("current", "reset"):
                state = getattr(model.configuration, role)
                k = owner.kernel(model.configuration)
                for _ in range(3):
                    step, cost = timed(k.step, state)
                    comparison_verify(step)
                    state = step.after
                    costs.append(cost)
                states[role] = state.to_payload()
            rows.append(
                {
                    "bits": bits,
                    "experimental_override": True,
                    "step_seconds": costs,
                    "certificate_seconds": seconds,
                    "q": pair[0].proof["q"],
                    "image_margin": pair[0].proof["image_margin"],
                    "final_states": states,
                    "fresh_independent_checks": 6,
                }
            )
    need(
        rows[0]["final_states"] == rows[1]["final_states"],
        "precision changed represented samples",
    )
    certificates._verify.cache_clear()
    return {
        "rows": rows,
        "identical_represented_states": True,
        "production_precision_bits": 256,
        "scope": "six bounded target steps per precision; no trajectory or automatic precision fallback",
    }


def run_tests():
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(NativeACIPCTests)
    names = [t._testMethodName for t in suite]
    need(len(names) == 33, "mandatory A_CI_PC test roster count")
    output = io.StringIO()
    start = time.perf_counter()
    result = unittest.TextTestRunner(stream=output, verbosity=2).run(suite)
    need(result.wasSuccessful() and not result.skipped, output.getvalue())
    return {
        "count": result.testsRun,
        "names": names,
        "seconds": time.perf_counter() - start,
        "passed": True,
    }


def benchmark(count=40):
    flint.ctx.threads = 1
    acipc.root_domain.cache_clear()
    _reference_facts.cache_clear()
    _fixed_rows.cache_clear()
    _decay.cache_clear()
    certificates._verify.cache_clear()
    start = time.perf_counter()
    setup = {}
    retained = []
    full_samples = []
    config, setup["configuration"] = timed(configuration)
    model, setup["initialization_cold"] = timed(GRC9V4, config)
    cold = acipc.SparkACIPCKernel.cache_info()["graph"]
    rows_cold = _fixed_rows.cache_info()._asdict()
    root_cold = acipc.root_domain.cache_info()._asdict()
    _, setup["initialization_warm"] = timed(GRC9V4, config)
    warm = acipc.SparkACIPCKernel.cache_info()["graph"]
    rows_warm = _fixed_rows.cache_info()._asdict()
    root_warm = acipc.root_domain.cache_info()._asdict()
    need(
        root_warm["hits"] > root_cold["hits"],
        "no static composite root-domain cache hit",
    )
    need(rows_warm["hits"] > rows_cold["hits"], "no immutable row cache hit")
    need(warm["hits"] > cold["hits"], "no static graph cache hit")
    source_steps = []
    source_step = acipc.SparkACIPCKernel.step

    def capture_source(k, *args):
        value = source_step(k, *args)
        source_steps.append(value)
        return value

    with patch.object(acipc.SparkACIPCKernel, "step", capture_source):
        result, setup["source_beat"] = timed(model.step)
    need(result.committed, result.reason)
    source_report, setup["source_independent_audit"] = timed(
        verify_step, source_steps[0]
    )
    result, setup["event"] = timed(model.expand, request(model))
    need(result.committed, result.reason)
    (pair, _center), setup["certification_cold_pair"] = timed(certificate_pair, model)
    proof_cold = certificates._verify.cache_info()._asdict()
    _, setup["certification_warm_pair"] = timed(
        lambda: tuple(CompletionCertificate.from_payload(c.to_payload()) for c in pair)
    )
    proof_warm = certificates._verify.cache_info()._asdict()
    need(proof_warm["hits"] >= proof_cold["hits"] + 2, "no certificate proof reuse")
    need(
        model.install_completion_certificates(*pair).committed,
        "certificate installation",
    )
    reset, setup["reset_fork"] = timed(model.duplicate)
    result, setup["reset_readmission"] = timed(reset.reset)
    need(result.committed, result.reason)
    need(
        reset._operation._published.completion.event is None,
        "reset event must be cleared",
    )
    roles = {"current": model, "reset": reset}
    samples = {r: [] for r in roles}
    oracles = {r: [] for r in roles}
    encodings = {r: [] for r in roles}
    checkpoints = {}
    originals = (
        acipc.SparkACIPCKernel.step,
        acipc.SparkACIPCKernel._admitted_read,
        acipc.SparkACIPCKernel._conductance_writer,
        ExactAdaptiveCarrierState.advance_histories,
        acipc.SparkACIPCKernel._carrier_writer,
    )
    captured = []
    read_calls = []
    writer_calls = []
    carrier_writer_calls = []
    writes = []
    backends = set()

    def capture(k, *args, **kw):
        value = originals[0](k, *args, **kw)
        captured.append(value)
        return value

    def count_read(k, state):
        from pygrc.models.grc_v4_exact import current_exact_backend

        backends.add(current_exact_backend().value)
        read_calls.append(state.to_canonical_bytes())
        return originals[1](k, state)

    def count_writer(k, *args):
        writer_calls.append(True)
        return originals[2](k, *args)

    def count_carrier_writer(k, *args):
        carrier_writer_calls.append(True)
        return originals[4](k, *args)

    def count_write(state, *args):
        writes.append(True)
        return originals[3](state, *args)

    with (
        patch.object(acipc.SparkACIPCKernel, "step", capture),
        patch.object(acipc.SparkACIPCKernel, "_admitted_read", count_read),
        patch.object(acipc.SparkACIPCKernel, "_conductance_writer", count_writer),
        patch.object(acipc.SparkACIPCKernel, "_carrier_writer", count_carrier_writer),
        patch.object(ExactAdaptiveCarrierState, "advance_histories", count_write),
    ):
        for i in range(count):
            for role, m in roles.items():
                need(
                    time.perf_counter() - start < 300, "bounded preflight sampling cap"
                )
                captured.clear()
                read_calls.clear()
                writer_calls.clear()
                carrier_writer_calls.clear()
                writes.clear()
                before = m.configuration.current
                result, seconds = timed(m.step)
                need(result.committed and result.local_gain == 0, result.reason)
                need(
                    len(captured) == 1
                    and len(read_calls) == 2
                    and len(writer_calls)
                    == len(carrier_writer_calls)
                    == len(writes)
                    == 1,
                    "one physical C/W/Z write, two separate writers and two fresh selected reads required",
                )
                step = captured[0]
                need(
                    step.before == before and step.after == m.configuration.current,
                    "captured actual execution mismatch",
                )
                cert = pair[0 if role == "current" else 1]
                (checked, observed), oracle = timed(
                    lambda step=step, cert=cert, role=role, m=m: (
                        verify_step(step, cert, role),
                        independent_membership(m, cert),
                    )
                )
                payload = compact_transition(step)
                need(
                    transition(decoded(payload)) == payload, "compact typed round trip"
                )
                if i in (0, 19, 39):
                    full_samples.append(
                        {"role": role, "index": i + 1, "transition": transition(step)}
                    )
                raw, coding = timed(encoded, payload)
                samples[role].append(
                    {
                        "total_seconds": seconds,
                        "fresh_reads": 2,
                        "writer_calls": 1,
                        "carrier_writer_calls": 1,
                        "full_state_writes": 1,
                        "compressed_bytes": len(raw),
                    }
                )
                oracles[role].append(oracle)
                encodings[role].append(coding)
                retained.append(
                    {
                        "role": role,
                        "index": i + 1,
                        "transition": payload,
                        "independent": checked,
                        "membership": observed,
                    }
                )
            if i == 0:
                print(
                    "One-step gate passed; continuing bounded changing-state samples.",
                    flush=True,
                )
    for role, m in roles.items():
        _, checkpoints[role] = timed(lambda m=m: encoded(m.snapshot()))
    need(backends == {"flint"}, "native execution left FLINT")
    need(acipc.root_domain.cache_info().hits > 0, "no immutable carrier-domain reuse")
    snapshot = model.snapshot()
    restore_digest_calls = []
    original_digest = owner.digest

    def counted_digest(value):
        if value == snapshot["owner"]["publication"]:
            restore_digest_calls.append(True)
        return original_digest(value)

    with patch.object(owner, "digest", counted_digest):
        restored, setup["warm_checkpoint_restore"] = timed(GRC9V4.from_state, snapshot)
    need(
        restored.snapshot() == snapshot and len(restore_digest_calls) == 1,
        "warm restore must hash the requested publication once and preserve the checkpoint",
    )
    # Cold validation really replays the public journal; do not count a warm hit.
    with patch.object(owner, "_SCOPES", {}):
        _, setup["cold_checkpoint_restore"] = timed(GRC9V4.from_state, snapshot)
    # Use the measured full tests as an intentionally conservative window allowance.
    checkpoints["synthetic_completed"] = max(checkpoints.values())
    need(time.perf_counter() - start < 300, "preflight exceeded sampling cap")
    info = {
        "samples": samples,
        "oracle_seconds": oracles,
        "transition_encoding_seconds": encodings,
        "setup_seconds": setup,
        "checkpoint_seconds": checkpoints,
        "elapsed_seconds": time.perf_counter() - start,
        "caches": {
            "root_domain_cold": root_cold,
            "root_domain_warm": root_warm,
            "rows_cold": rows_cold,
            "rows_warm": rows_warm,
            "root_domain_final": acipc.root_domain.cache_info()._asdict(),
            "rows_final": _fixed_rows.cache_info()._asdict(),
            "domain_cold": cold,
            "domain_warm": warm,
            "domain_final": acipc.SparkACIPCKernel.cache_info()["graph"],
            "decay_final": acipc.SparkACIPCKernel.cache_info()["decay"],
            "final_graph": _reference_facts.cache_info()._asdict(),
            "proof_cold": proof_cold,
            "proof_warm": proof_warm,
        },
        "memory": {"final_peak_mib": rss(), "cap_mib": 1024},
        "checkpoint_hash_optimization": {
            "publication_digest_calls": len(restore_digest_calls),
            "admitted_publications": len(
                model._operation._spark_scope.published.admitted
            ),
            "exact_checkpoint_preserved": True,
        },
        "certificates": [c.to_payload() for c in pair],
    }
    need(rss() < 1024, "memory cap")
    return info, {
        "samples": retained,
        "full_samples": full_samples,
        "source_transition": transition(source_steps[0]),
        "source_independent": source_report,
        "event": model._operation._published.completion.event.to_dict(),
        "initial": config.to_payload(),
        "target": model.configuration.reference.to_payload(),
    }


def bindings():
    # Freeze numerical inputs, not mutable publication metadata or prior epochs.
    paths = {str(p) for p in (ROOT / "src/pygrc/models").glob("*spark*.py")}
    paths = {str(Path(p).relative_to(ROOT)) for p in paths}
    paths.update(
        str(p.relative_to(ROOT))
        for p in (ROOT / "src/pygrc/models").glob("grc_9_v4_completion*.py")
    )
    paths.update(
        {
            SCRIPT,
            "src/pygrc/models/grc_9_v4.py",
            HERE + "p991a6_acipc_subjects.py",
            HERE + "acipc_native_spark_oracle.py",
            HERE + "aos_native_spark_oracle.py",
            HERE + "cpc_native_spark_pressure_oracle.py",
            "specs/grc-9-v4-spark-completion-a-ci-pc-source-manifest.json",
            HERE + "cci_native_spark_pressure_oracle.py",
            HERE + "cos_native_spark_oracle.py",
            HERE + "p991a2_native_spark_numerics.py",
            HERE + "p991a4_native_spark_preflight.py",
            "tests/models/test_grc_v4_spark_acipc.py",
            "tests/models/test_grc_9_v4_spark_completion.py",
            "specs/grc-v4-spark-native-a-ci-pc-numerical-policy.md",
            "specs/grc-9-v4-spark-completion-a-ci-pc.md",
            "specs/grc-9-v4-spark-completion-earlier.md",
            BASE + "P9-9.1a.6-ACIPC-Contract.md",
        }
    )
    prior = json.loads((ROOT / (BASE + "P9-9.1a.6-CPC-Preflight.json")).read_bytes())
    paths.update(
        r["path"]
        for r in prior["source_bindings"]
        if "/research/" in r["path"] or "/evidence/" in r["path"]
    )
    paths.add(
        "implementation/investigations/grc9v4-constitutive-design/research/spark_completion_a_os.py"
    )
    base = "implementation/investigations/grc9v4-constitutive-design/"
    paths.update(
        base + name
        for name in (
            "evidence/spark-completion/applicability/AOS-current.json.xz",
            "evidence/spark-completion/applicability/earlier-closure/AOSAnisotropicDomain.json",
            "research/spark_completion_a_os_earlier.py",
        )
    )

    return [
        {"path": p, "sha256": sha256((ROOT / p).read_bytes()).hexdigest()}
        for p in sorted(paths)
    ]


def run():
    need(
        not (ROOT / RECORD).exists() and not (ROOT / EVIDENCE).exists(),
        "do not overwrite a retained preflight",
    )
    tests = run_tests()
    print("33 native A_CI_PC tests passed.", flush=True)
    comparison = precision_comparison()
    print("256/512 comparison passed.", flush=True)
    info, evidence = benchmark()
    forecasts = estimate(
        info["samples"],
        sum(info["setup_seconds"].values()),
        info["oracle_seconds"],
        info["transition_encoding_seconds"],
        tests["seconds"],
        info["checkpoint_seconds"],
        info["setup_seconds"]["warm_checkpoint_restore"],
        cold_restore_seconds=info["setup_seconds"]["cold_checkpoint_restore"],
    )
    raw = encoded(evidence)
    (ROOT / EVIDENCE).write_bytes(raw)
    value = seal(
        dict(
            schema="grc9v4-native-acipc-preflight-v1",
            family="A_CI_PC",
            leaf="P9-9.1a.6-A_CI_PC",
            status="implemented_verified_pending_review",
            user_accepted=False,
            native_endpoint_verified=False,
            native_completion_support=False,
            full_trajectory_runs=0,
            exact_backend="flint",
            state_channels=["C", "W_A", "Z_4"],
            full_domain_dimension=76,
            evidence_storage={
                "format": "compact_acipc_full_root_and_two_writer_witness_v1",
                "exact_transitions": 80,
                "complete_diagnostic_samples": 6,
                "full_campaign_runs": 0,
            },
            oracle_precision_bits=768,
            endpoint_expectations_verified=False,
            target_vertices=15,
            target_edges=16,
            duration="32",
            exact_charge="21",
            numerical_policy_id=ACIPC_NUMERICAL_POLICY,
            certificate_precision_bits=acipc.PRECISION,
            machine={
                "python": platform.python_version(),
                "flint": flint.__version__,
                "flint_threads": flint.ctx.threads,
            },
            tests=tests,
            precision_comparison=comparison,
            estimate=forecasts,
            sampling_cap_seconds=180,
            synthetic_window_scope="unit fixtures near certificate center, no source-to-entry claim",
            reset_scope="public reset, no live event and zero gain",
            stop_conditions=[
                "Stop on read/writer/enclosure/admission failure.",
                "At the 400-step planning horizon, diagnose membership before extending; never assume endpoint entry.",
                "Re-estimate timing drift against the 1800-second profiling target; preserve valid results. Investigate memory above 1024 MiB.",
            ],
            expected_endpoints={"current": [375, 377], "reset": [372, 374]},
            source_bindings=bindings(),
            evidence={"path": EVIDENCE, "sha256": sha256(raw).hexdigest()},
            **info,
        )
    )
    (ROOT / RECORD).write_bytes(encoded(value))
    print(
        json.dumps(
            {
                "record": RECORD,
                "elapsed": info["elapsed_seconds"],
                "estimate": forecasts,
            },
            indent=2,
        ),
        flush=True,
    )
    return value


def check(root=ROOT):
    previous_bytes = lambda root, name: (root / name).read_bytes()

    root = Path(root)
    value = json.loads(lzma.decompress((root / RECORD).read_bytes()))
    need(
        value == seal(value) and value["schema"] == "grc9v4-native-acipc-preflight-v1",
        "unsealed A_CI_PC preflight",
    )
    need(
        value["native_endpoint_verified"] is False
        and value["native_completion_support"] is False
        and value["full_trajectory_runs"] == 0,
        "preflight scope changed",
    )
    for row in [*value["source_bindings"], value["evidence"]]:
        need(
            sha256(previous_bytes(root, row["path"])).hexdigest() == row["sha256"],
            "changed A_CI_PC subject: " + row["path"],
        )
    need(
        all(len(rows) == 40 for rows in value["samples"].values()),
        "mandatory sample count",
    )
    need(value["tests"]["count"] == 33 and value["tests"]["passed"], "mandatory tests")
    forecast = estimate(
        value["samples"],
        sum(value["setup_seconds"].values()),
        value["oracle_seconds"],
        value["transition_encoding_seconds"],
        value["tests"]["seconds"],
        value["checkpoint_seconds"],
        value["setup_seconds"]["warm_checkpoint_restore"],
        cold_restore_seconds=value["setup_seconds"]["cold_checkpoint_restore"],
    )
    need(forecast == value["estimate"], "forecast differs from measured inputs")
    return value


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", action="store_true")
    args = parser.parse_args()
    run() if args.run else check()

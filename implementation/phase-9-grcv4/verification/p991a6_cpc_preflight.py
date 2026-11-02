"""Bounded native C_PC contract/numerics/lifecycle/preflight; never a campaign."""

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
from cpc_native_spark_oracle import verify_step
from p991a4_native_spark_preflight import estimate as base_estimate
from p991a4_native_spark_preflight import need, rss, seal, timed
from p991a6_cpc_subjects import certificate_pair, configuration, request

from pygrc.models import grc_9_v4_completion_certificate as certificates
from pygrc.models import grc_9_v4_spark_owner as owner
from pygrc.models import grc_v4_spark_cpc as pc
from pygrc.models.grc_9_v4 import GRC9V4
from pygrc.models.grc_9_v4_completion_certificate import CompletionCertificate
from pygrc.models.grc_v4_spark_carrier import ExactCarrierState
from pygrc.models.grc_v4_spark_cos import _reference_facts
from pygrc.models.grc_v4_spark_state import PC_NUMERICAL_POLICY
from tests.models.test_grc_v4_spark_cpc import NativeCPCTests

BASE = "implementation/phase-9-grcv4/tranche-9/"
HERE = "implementation/phase-9-grcv4/verification/"
RECORD = BASE + "P9-9.1a.6-CPC-Preflight.json"
EVIDENCE = BASE + "P9-9.1a.6-CPC-Samples.json.xz"
SCRIPT = HERE + "p991a6_cpc_preflight.py"


def estimate(*args):
    value = base_estimate(*args)
    # The preceding C_CI campaign needed two expensive pressure/checkpoint
    # phases. Reserve four minutes in addition to measured sampling costs.
    value["pressure_checkpoint_reserve_seconds"] = 240
    value["central_seconds"] += 240
    value["upper_seconds"] += 240
    value["within_budget"] = value["upper_seconds"] < 1800
    return value


def independent_membership(model, certificate):
    from flint import fmpq as Q
    from flint import fmpq_mat as M

    state = model.configuration.current
    U = M([[Q(x) for x in row] for row in certificate.operands["U"]])
    delta = M(
        [
            [Q(x) - Q(c)]
            for x, c in zip(state.C, certificate.operands["center"], strict=True)
        ]
    )
    resource2 = max(abs(x) for x in (U * delta).entries()) ** 2
    carrier2 = (
        sum(Q(x) ** 2 for row in state.Z_4 for x in row)
        / Q(certificate.operands["carrier_radius"]) ** 2
    )
    norm2 = max(resource2, carrier2)
    need(
        certificate.membership(state) == (norm2 <= 1, str(norm2)),
        "full independent product membership",
    )
    from cos_native_spark_oracle import classify as independent_classify

    from pygrc.models.grc_9_v4_completion import classify

    expected = independent_classify(
        state.graph.to_payload(), state.C, model.configuration.policy.to_payload()
    )
    actual = classify(state, model.configuration.policy)
    need(
        (actual.basins, actual.terminals, [x.to_dict() for x in actual.rows])
        == expected,
        "independent row classification",
    )
    return {
        "squared_max_product_norm": str(norm2),
        "inside": norm2 <= 1,
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
        "carrier_component_error": step.carrier_component_error,
        "final_current": step.final_current,
        "reference_current": step.reference_current,
        "numerical_policy_id": step.numerical_policy_id,
    }


def encoded(value):
    return lzma.compress(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode(), preset=3
    )


def precision_comparison():
    """An experimental precision override, never an execution-policy certificate."""
    rows = []
    for bits in (256, 512):
        with patch.object(pc, "PRECISION", bits):
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
                    verify_step(step)
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
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(NativeCPCTests)
    names = [t._testMethodName for t in suite]
    need(len(names) == 22, "mandatory PC test roster count")
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
    _reference_facts.cache_clear()
    pc._domain.cache_clear()
    pc._decay.cache_clear()
    certificates._verify.cache_clear()
    start = time.perf_counter()
    setup = {}
    retained = []
    config, setup["configuration"] = timed(configuration)
    model, setup["initialization_cold"] = timed(GRC9V4, config)
    cold = pc.SparkCPCKernel.domain_cache_info()
    _, setup["initialization_warm"] = timed(GRC9V4, config)
    warm = pc.SparkCPCKernel.domain_cache_info()
    need(warm["hits"] > cold["hits"], "no static carrier-domain cache hit")
    result, setup["source_beat"] = timed(model.step)
    need(result.committed, result.reason)
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
        pc.SparkCPCKernel.step,
        pc.SparkCPCKernel._admitted_read,
        pc.SparkCPCKernel._writer,
        ExactCarrierState.advance_carrier,
    )
    captured = []
    root_calls = []
    writer_calls = []
    writes = []
    backends = set()

    def capture(k, *args, **kw):
        value = originals[0](k, *args, **kw)
        captured.append(value)
        return value

    def count_root(k, state):
        from pygrc.models.grc_v4_exact import current_exact_backend

        backends.add(current_exact_backend().value)
        root_calls.append(state.to_canonical_bytes())
        return originals[1](k, state)

    def count_writer(k, *args):
        writer_calls.append(True)
        return originals[2](k, *args)

    def count_write(state, *args):
        writes.append(True)
        return originals[3](state, *args)

    with (
        patch.object(pc.SparkCPCKernel, "step", capture),
        patch.object(pc.SparkCPCKernel, "_admitted_read", count_root),
        patch.object(pc.SparkCPCKernel, "_writer", count_writer),
        patch.object(ExactCarrierState, "advance_carrier", count_write),
    ):
        for i in range(count):
            for role, m in roles.items():
                need(
                    time.perf_counter() - start < 180, "bounded preflight sampling cap"
                )
                captured.clear()
                root_calls.clear()
                writer_calls.clear()
                writes.clear()
                before = m.configuration.current
                result, seconds = timed(m.step)
                need(result.committed and result.local_gain == 0, result.reason)
                need(
                    len(captured) == 1
                    and len(root_calls) == 3
                    and len(writer_calls) == len(writes) == 1,
                    "one physical C/Z write, one writer and three fresh reads required",
                )
                step = captured[0]
                need(
                    step.before == before and step.after == m.configuration.current,
                    "captured actual execution mismatch",
                )
                cert = pair[0 if role == "current" else 1]
                (checked, observed), oracle = timed(
                    lambda: (
                        verify_step(step, cert, role),
                        independent_membership(m, cert),
                    )
                )
                payload = transition(step)
                raw, coding = timed(encoded, payload)
                samples[role].append(
                    {
                        "total_seconds": seconds,
                        "fresh_reads": 3,
                        "writer_calls": 1,
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
    snapshot = model.snapshot()
    _, setup["warm_checkpoint_restore"] = timed(GRC9V4.from_state, snapshot)
    # Use the measured full tests as an intentionally conservative window allowance.
    checkpoints["synthetic_completed"] = max(checkpoints.values())
    need(time.perf_counter() - start < 180, "preflight exceeded sampling cap")
    info = {
        "samples": samples,
        "oracle_seconds": oracles,
        "transition_encoding_seconds": encodings,
        "setup_seconds": setup,
        "checkpoint_seconds": checkpoints,
        "elapsed_seconds": time.perf_counter() - start,
        "caches": {
            "domain_cold": cold,
            "domain_warm": warm,
            "domain_final": pc.SparkCPCKernel.domain_cache_info(),
            "decay_final": pc.SparkCPCKernel.decay_cache_info(),
            "final_graph": _reference_facts.cache_info()._asdict(),
            "proof_cold": proof_cold,
            "proof_warm": proof_warm,
        },
        "memory": {"final_peak_mib": rss(), "cap_mib": 1024},
        "certificates": [c.to_payload() for c in pair],
    }
    need(rss() < 1024, "memory cap")
    return info, {
        "samples": retained,
        "initial": config.to_payload(),
        "target": model.configuration.reference.to_payload(),
    }


def bindings():
    prior = json.loads((ROOT / (BASE + "P9-9.1a.6-CCI-Preflight.json")).read_bytes())
    paths = {r["path"] for r in prior["source_bindings"]}
    paths.update(
        [
            SCRIPT,
            HERE + "cpc_native_spark_oracle.py",
            HERE + "p991a6_cpc_subjects.py",
            HERE + "p991a6_cpc_epoch.py",
            "tests/models/test_grc_v4_spark_cpc.py",
            "specs/grc-v4-spark-native-pc-numerical-policy.md",
            "specs/grc-9-v4-spark-completion-pc.md",
            "specs/grc-9-v4-spark-completion-earlier.md",
            BASE + "P9-9.1a.6-CPC-Contract.md",
            "src/pygrc/models/grc_v4_spark.py",
            "src/pygrc/models/grc_v4_spark_cpc.py",
            "src/pygrc/models/grc_v4_spark_carrier.py",
            "src/pygrc/models/grc_9_v4_completion_cpc.py",
            "src/pygrc/models/grc_9_v4_spark_carrier_event.py",
            "implementation/investigations/grc9v4-constitutive-design/research/spark_completion_pc.py",
        ]
    )
    return [
        {"path": p, "sha256": sha256((ROOT / p).read_bytes()).hexdigest()}
        for p in sorted(paths)
    ]


def run():
    tests = run_tests()
    print("22 native C_PC tests passed.", flush=True)
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
    )
    raw = encoded(evidence)
    (ROOT / EVIDENCE).write_bytes(raw)
    value = seal(
        dict(
            schema="grc9v4-native-cpc-preflight-v1",
            family="C_PC",
            leaf="P9-9.1a.6-C_PC",
            status="implemented_verified_pending_review",
            user_accepted=False,
            native_endpoint_verified=False,
            native_completion_support=False,
            full_trajectory_runs=0,
            exact_backend="flint",
            state_channels=["C", "Z_4"],
            full_domain_dimension=60,
            oracle_precision_bits=768,
            endpoint_expectations_verified=False,
            target_vertices=15,
            target_edges=16,
            duration="32",
            exact_charge="21",
            numerical_policy_id=PC_NUMERICAL_POLICY,
            certificate_precision_bits=pc.PRECISION,
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
                "Stop on root/enclosure/admission failure.",
                "Stop at 400 target steps per role without completion.",
                "Stop if rolling estimate exceeds 1800 seconds or peak memory exceeds 1024 MiB.",
            ],
            expected_endpoints={"current": [374, 376], "reset": [375, 377]},
            source_bindings=bindings(),
            evidence={"path": EVIDENCE, "sha256": sha256(raw).hexdigest()},
            **info,
        )
    )
    (ROOT / RECORD).write_text(json.dumps(value, indent=2) + "\n")
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
    root = Path(root)
    value = json.loads((root / RECORD).read_bytes())
    need(
        value == seal(value) and value["schema"] == "grc9v4-native-cpc-preflight-v1",
        "unsealed PC preflight",
    )
    need(
        value["native_endpoint_verified"] is False
        and value["native_completion_support"] is False
        and value["full_trajectory_runs"] == 0,
        "preflight scope changed",
    )
    for row in [*value["source_bindings"], value["evidence"]]:
        need(
            sha256((root / row["path"]).read_bytes()).hexdigest() == row["sha256"],
            "changed PC subject: " + row["path"],
        )
    need(
        all(len(rows) == 40 for rows in value["samples"].values()),
        "mandatory sample count",
    )
    need(value["tests"]["count"] == 22 and value["tests"]["passed"], "mandatory tests")
    forecast = estimate(
        value["samples"],
        sum(value["setup_seconds"].values()),
        value["oracle_seconds"],
        value["transition_encoding_seconds"],
        value["tests"]["seconds"],
        value["checkpoint_seconds"],
        value["setup_seconds"]["warm_checkpoint_restore"],
    )
    need(forecast == value["estimate"], "forecast differs from measured inputs")
    return value


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", action="store_true")
    args = parser.parse_args()
    run() if args.run else check()

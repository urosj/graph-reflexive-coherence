"""Bounded native C_CI contract/numerics/lifecycle/preflight; never a campaign."""

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
from cci_native_spark_oracle import verify_step
from p991a4_native_spark_preflight import estimate, need, rss, seal, timed
from p991a6_cci_subjects import configuration

from pygrc.models import grc_9_v4_completion_certificate as certificates
from pygrc.models import grc_9_v4_spark_owner as owner
from pygrc.models import grc_v4_spark_cci as ci
from pygrc.models.grc_9_v4 import GRC9V4
from pygrc.models.grc_9_v4_completion_certificate import CompletionCertificate
from pygrc.models.grc_v4_spark_cos import _reference_facts
from pygrc.models.grc_v4_spark_state import CI_NUMERICAL_POLICY
from tests.models.test_grc_9_v4_spark_completion import certificate_pair, request
from tests.models.test_grc_v4_spark_cci import NativeCCITests

BASE = "implementation/phase-9-grcv4/tranche-9/"
HERE = "implementation/phase-9-grcv4/verification/"
RECORD = BASE + "P9-9.1a.6-CCI-Preflight.json"
EVIDENCE = BASE + "P9-9.1a.6-CCI-Samples.json.xz"
SCRIPT = HERE + "p991a6_cci_preflight.py"


def transition(step):
    return {
        "before": step.before.to_payload(),
        "after": step.after.to_payload(),
        "duration": step.duration,
        "profile_id": step.profile_id,
        "flux": list(step.flux),
        "componentwise_error_bounds": list(step.componentwise_error_bounds),
        "root": step.root.to_dict(),
        "restart_root": step.restart_root.to_dict(),
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
        with patch.object(ci, "PRECISION", bits):
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
                states[role] = list(state.C)
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
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(NativeCCITests)
    names = [t._testMethodName for t in suite]
    need(len(names) == 19, "mandatory CI test roster count")
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
    ci._root_domain.cache_clear()
    certificates._verify.cache_clear()
    start = time.perf_counter()
    setup = {}
    retained = []
    config, setup["configuration"] = timed(configuration)
    model, setup["initialization_cold"] = timed(GRC9V4, config)
    cold = ci.SparkCCIKernel.root_cache_info()
    _, setup["initialization_warm"] = timed(GRC9V4, config)
    warm = ci.SparkCCIKernel.root_cache_info()
    need(warm["hits"] > cold["hits"], "no static root-domain cache hit")
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
    originals = ci.SparkCCIKernel.step, ci.SparkCCIKernel._root
    captured = []
    root_calls = []

    def capture(k, *args, **kw):
        value = originals[0](k, *args, **kw)
        captured.append(value)
        return value

    def count_root(k, C):
        root_calls.append(tuple(str(x) for x in C.entries()))
        return originals[1](k, C)

    with (
        patch.object(ci.SparkCCIKernel, "step", capture),
        patch.object(ci.SparkCCIKernel, "_root", count_root),
    ):
        for i in range(count):
            for role, m in roles.items():
                need(
                    time.perf_counter() - start < 180, "bounded preflight sampling cap"
                )
                captured.clear()
                root_calls.clear()
                before = m.configuration.current
                result, seconds = timed(m.step)
                need(result.committed and result.local_gain == 0, result.reason)
                need(
                    len(captured) == 1 and len(root_calls) == 2,
                    "exactly one physical step, two fresh root admissions required",
                )
                step = captured[0]
                need(
                    step.before == before and step.after == m.configuration.current,
                    "captured actual execution mismatch",
                )
                checked, oracle = timed(verify_step, step)
                payload = transition(step)
                raw, coding = timed(encoded, payload)
                samples[role].append(
                    {
                        "total_seconds": seconds,
                        "root_calls": 2,
                        "iterations": step.root["iterations"],
                        "restart_iterations": step.restart_root["iterations"],
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
                    }
                )
            if i == 0:
                print(
                    "One-step gate passed; continuing bounded changing-state samples.",
                    flush=True,
                )
    for role, m in roles.items():
        _, checkpoints[role] = timed(lambda m=m: encoded(m.snapshot()))
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
            "root_cold": cold,
            "root_warm": warm,
            "root_final": ci.SparkCCIKernel.root_cache_info(),
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
    prior = json.loads((ROOT / (BASE + "P9-9.1a.4-Preflight.json")).read_bytes())
    paths = {r["path"] for r in prior["source_bindings"]}
    paths.update(
        [
            SCRIPT,
            HERE + "cci_native_spark_oracle.py",
            HERE + "p991a6_cci_subjects.py",
            HERE + "p991a6_cci_epoch.py",
            "tests/models/test_grc_v4_spark_cci.py",
            "specs/grc-v4-spark-native-ci-numerical-policy.md",
            "specs/grc-9-v4-spark-completion-ci.md",
            "specs/grc-9-v4-spark-completion-earlier.md",
            BASE + "P9-9.1a.6-CCI-Contract.md",
            "src/pygrc/models/grc_v4_spark.py",
            "src/pygrc/models/grc_v4_spark_cci.py",
            "implementation/investigations/grc9v4-constitutive-design/research/spark_completion_ci.py",
        ]
    )
    return [
        {"path": p, "sha256": sha256((ROOT / p).read_bytes()).hexdigest()}
        for p in sorted(paths)
    ]


def run():
    tests = run_tests()
    print("19 native C_CI tests passed.", flush=True)
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
            schema="grc9v4-native-cci-preflight-v1",
            family="C_CI",
            leaf="P9-9.1a.6-C_CI",
            status="implemented_verified_pending_review",
            user_accepted=False,
            native_endpoint_verified=False,
            native_completion_support=False,
            full_trajectory_runs=0,
            endpoint_expectations_verified=False,
            target_vertices=15,
            target_edges=16,
            duration="32",
            exact_charge="21",
            numerical_policy_id=CI_NUMERICAL_POLICY,
            certificate_precision_bits=ci.PRECISION,
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
        value == seal(value) and value["schema"] == "grc9v4-native-cci-preflight-v1",
        "unsealed CI preflight",
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
            "changed CI subject: " + row["path"],
        )
    need(
        all(len(rows) == 40 for rows in value["samples"].values()),
        "mandatory sample count",
    )
    need(value["tests"]["count"] == 19 and value["tests"]["passed"], "mandatory tests")
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

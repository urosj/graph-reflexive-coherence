"""Bounded A_RG2b native preflight and cost estimate; both RG2b .5 runs deferred."""

import argparse
import io
import json
import lzma
import platform
import statistics
import sys
import time
import unittest
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / "src")]
import flint
from arg2b_native_spark_oracle import _proof, fresh, verify_step
from p991a4_native_spark_preflight import need, rss, seal, timed
from p991a6_arg2b_subjects import certificate_pair, configuration, request

from pygrc.models import grc_9_v4_completion_certificate as certificates
from pygrc.models import grc_9_v4_spark_owner as owner
from pygrc.models import grc_v4_spark_arg2b as native
from pygrc.models.grc_9_v4 import GRC9V4
from pygrc.models.grc_9_v4_completion_arg2b import _common_verify, membership_details
from pygrc.models.grc_v4_codec import canonical_json_bytes
from pygrc.models.grc_v4_spark_conductance import (
    ARG2B_NUMERICAL_POLICY,
    ExactConductanceState,
)
from pygrc.models.grc_v4_state import FrozenJSONMap
from tests.models.test_grc_v4_spark_arg2b import NativeARG2bTests

BASE = "implementation/phase-9-grcv4/tranche-9/"
HERE = "implementation/phase-9-grcv4/verification/"
INV = "implementation/investigations/grc9v4-constitutive-design/"
RECORD = BASE + "P9-9.1a.6-ARG2b-Preflight.json.xz"
EVIDENCE = BASE + "P9-9.1a.6-ARG2b-Samples.json.xz"
SCRIPT = HERE + "p991a6_arg2b_preflight.py"
SAMPLE_COUNT = 12
SAMPLING_CAP = 600


def encoded(v):
    return lzma.compress(
        json.dumps(v, sort_keys=True, separators=(",", ":")).encode(), preset=6
    )


def transition(step):
    out = {
        k: getattr(step, k)
        for k in (
            "profile_id",
            "duration",
            "flux",
            "componentwise_error_bounds",
            "log_conductance_component_error",
            "final_current",
            "reference_current",
        )
    }
    out.update(
        before=step.before.to_payload(),
        after=step.after.to_payload(),
        section=step.section.to_dict(),
        writer=step.writer.to_dict(),
        restart_section=step.restart_section.to_dict(),
    )
    return out


def decoded(row):
    data = dict(row)
    for key in ("before", "after"):
        data[key] = ExactConductanceState.from_canonical_bytes(
            canonical_json_bytes(data[key])
        )
    for key in ("section", "writer", "restart_section"):
        data[key] = FrozenJSONMap(data[key])
    for key in ("flux", "componentwise_error_bounds"):
        data[key] = tuple(data[key])
    for key in ("final_current", "reference_current"):
        data[key] = tuple(tuple(x) for x in data[key])
    return native.SparkARG2bStep(**data)


def compact(value, previous):
    data = dict(value)
    if previous:
        need(
            value["before"] == previous["after"]
            and value["section"] == previous["restart_section"],
            "exact adjacent continuity",
        )
        del data["before"]
        del data["section"]
    return data


def expand(value, previous):
    data = dict(value)
    if previous:
        need(
            "before" not in data and "section" not in data,
            "canonical adjacent factoring",
        )
        data.update(before=previous["after"], section=previous["restart_section"])
    return data


def run_tests():
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(NativeARG2bTests)
    names = [t._testMethodName for t in suite]
    need(len(names) == 21, "mandatory A_RG2b roster")
    stream = io.StringIO()
    start = time.perf_counter()
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    print(stream.getvalue(), flush=True)
    need(
        result.wasSuccessful() and not result.skipped and not result.expectedFailures,
        "native A_RG2b checks failed",
    )
    return {
        "count": result.testsRun,
        "names": names,
        "seconds": time.perf_counter() - start,
        "passed": True,
    }


def estimate(v):
    roles = {}
    total = 0
    upper = 0
    for role, rows in v["samples"].items():
        normal = [
            r["native_seconds"] + r["audit_seconds"] + r["encoding_seconds"]
            for r in rows
            if not r["fresh_depth24"]
        ]
        mean = statistics.mean(normal)
        maximum = max(normal)
        replay = v["cold_replay_seconds"] / (SAMPLE_COUNT + 1)
        # A forecast includes both ordinary work and cold recovery, plus fresh
        # late-state checks. It is a planning envelope, not an endpoint result.
        deep = sum(r["audit_seconds"] for r in rows if r["fresh_depth24"]) / 2
        central = (
            302 * (mean + replay)
            + 12 * deep
            + v["setup"]["certification_cold_pair"] / 2
            + 30
        )
        conservative = 302 * (2 * maximum + 2 * replay) + 24 * deep + 60
        roles[role] = {
            "horizon": 302,
            "mean_audited_seconds": mean,
            "maximum_audited_seconds": maximum,
            "replay_seconds_per_step": replay,
            "central_seconds": central,
            "upper_seconds": conservative,
        }
        total += central
        upper += conservative
    return {
        "roles": roles,
        "central_seconds": total,
        "upper_seconds": upper,
        "profiling_target_seconds": 3600,
        "full_run_authorized": False,
        "late_state_profile_required": True,
        "meaning": "bounded-prefix extrapolation with cold replay and independent-check reserves; not a confidence interval",
    }


def benchmark():
    for cache in (
        native._section_witness,
        native._reference_facts,
        native._fixed_rows,
        native.global_domain,
        certificates._verify,
        _common_verify,
        fresh,
        _proof,
    ):
        cache.cache_clear()
    start = time.perf_counter()
    setup = {}
    captured = []
    reads = []
    writes = []
    backends = set()
    config, setup["configuration"] = timed(configuration)
    model, setup["initialization_cold"] = timed(GRC9V4, config)
    cold = native.SparkARG2bKernel.cache_info()
    _, setup["initialization_warm"] = timed(GRC9V4, config)
    warm = native.SparkARG2bKernel.cache_info()
    for key in ("graph", "rows", "domain", "section"):
        need(warm[key]["hits"] > cold[key]["hits"], "cache not active: " + key)
    original = native.SparkARG2bKernel.step
    original_read = native.SparkARG2bKernel._admitted_section
    original_write = ExactConductanceState.advance_conductance

    def capture(k, *args, **kwargs):
        s = original(k, *args, **kwargs)
        captured.append(s)
        return s

    def read(k, state):
        from pygrc.models.grc_v4_exact import current_exact_backend

        backends.add(current_exact_backend().value)
        reads.append(1)
        return original_read(k, state)

    def write(state, *args, **kwargs):
        writes.append(1)
        return original_write(state, *args, **kwargs)

    with patch.object(native.SparkARG2bKernel, "step", capture):
        r, setup["source_beat"] = timed(model.step)
    need(r.committed, r.reason)
    source = captured[0]
    source_report, setup["source_independent_audit"] = timed(
        verify_step, config, config.current, source, fresh_check=True
    )
    r, setup["event"] = timed(model.expand, request(model))
    need(r.committed, r.reason)
    event = model._operation._published.completion.event.to_dict()
    (pair, _), setup["certification_cold_pair"] = timed(certificate_pair, model)
    cache_before = certificates._verify.cache_info()._asdict()
    _, setup["certification_warm_pair"] = timed(
        lambda: tuple(
            certificates.CompletionCertificate.from_payload(c.to_payload())
            for c in pair
        )
    )
    cache_after = certificates._verify.cache_info()._asdict()
    need(cache_after["hits"] >= cache_before["hits"] + 2, "certificate cache")
    need(
        model.install_completion_certificates(*pair).committed,
        "native certificate install",
    )
    reset = model.duplicate()
    need(reset.reset().committed, "real reset fork")
    need(
        reset._operation._published.completion.event is None, "reset clears occurrence"
    )
    roles = {"current": model, "reset": reset}
    initial = {r: m.snapshot() for r, m in roles.items()}
    samples = {r: [] for r in roles}
    retained = {r: [] for r in roles}
    prior = dict.fromkeys(roles)
    with (
        patch.object(native.SparkARG2bKernel, "step", capture),
        patch.object(native.SparkARG2bKernel, "_admitted_section", read),
        patch.object(ExactConductanceState, "advance_conductance", write),
    ):
        for i in range(SAMPLE_COUNT):
            for role, m in roles.items():
                need(
                    time.perf_counter() - start < SAMPLING_CAP, "bounded profiling cap"
                )
                captured.clear()
                reads.clear()
                writes.clear()
                before = m.configuration
                result, seconds = timed(m.step)
                need(result.committed and result.local_gain == 0, result.reason)
                need(
                    len(captured) == 1 and len(reads) == 2 and len(writes) == 1,
                    "two admitted sections and one full C/W update",
                )
                step = captured[0]
                need(
                    step.before == before.current
                    and step.after == m.configuration.current,
                    "captured public subject",
                )
                deep = i in (0, SAMPLE_COUNT - 1)
                report, audit_seconds = timed(
                    verify_step, before, before.current, step, fresh_check=deep
                )
                payload = transition(step)
                value = compact(payload, prior[role])
                raw, encoding_seconds = timed(encoded, value)
                prior[role] = payload
                detail = membership_details(
                    pair[0 if role == "current" else 1], step.after
                )
                retained[role].append(
                    {"transition": value, "independent": report, "membership": detail}
                )
                samples[role].append(
                    {
                        "step": i + 1,
                        "native_seconds": seconds,
                        "audit_seconds": audit_seconds,
                        "encoding_seconds": encoding_seconds,
                        "compressed_bytes": len(raw),
                        "fresh_depth24": deep,
                        "fresh_reads": len(reads),
                        "full_state_writes": len(writes),
                        "inside_domain": detail["inside"],
                        "local_gain": result.local_gain,
                    }
                )
                print(
                    f"A_RG2b bounded {role} {i + 1}/{SAMPLE_COUNT}: native={seconds:.3f}s audit={audit_seconds:.3f}s",
                    flush=True,
                )
    checkpoint = model.snapshot()
    origin = checkpoint["owner"]["origin"]
    with owner._SCOPES_LOCK:
        scope = owner._SCOPES.pop(origin)
    native._section_witness.cache_clear()
    try:
        restored, replay = timed(GRC9V4.from_state, checkpoint)
        need(restored.snapshot() == checkpoint, "cold complete journal replay")
    finally:
        with owner._SCOPES_LOCK:
            owner._SCOPES[origin] = scope
    elapsed = time.perf_counter() - start
    need(elapsed < SAMPLING_CAP, "bounded sample allowance")
    evidence = {
        "source_configuration": config.to_payload(),
        "source_transition": transition(source),
        "source_independent": source_report,
        "event": event,
        "initial_snapshots": initial,
        "samples": retained,
        "certificates": [c.to_payload() for c in pair],
        "final_states": {
            r: m.configuration.current.to_payload() for r, m in roles.items()
        },
    }
    info = {
        "setup": setup,
        "samples": samples,
        "cold_replay_seconds": replay,
        "elapsed_seconds": elapsed,
        "caches": {
            "cold": cold,
            "warm": warm,
            "final": native.SparkARG2bKernel.cache_info(),
            "certificate": cache_after,
            "common_certificate": _common_verify.cache_info()._asdict(),
            "independent_proof": _proof.cache_info()._asdict(),
        },
        "exact_backends": sorted(backends),
        "memory": {"final_peak_mib": rss()},
    }
    return info, evidence


def bindings():
    paths = {
        str(p.relative_to(ROOT))
        for pattern in ("*spark*.py", "grc_9_v4_completion*.py")
        for p in (ROOT / "src/pygrc/models").glob(pattern)
    }
    paths.update(
        {
            SCRIPT,
            HERE + "p991a6_arg2b_subjects.py",
            HERE + "arg2b_native_spark_oracle.py",
            HERE + "crg2b_native_spark_oracle.py",
            HERE + "p991a4_native_spark_preflight.py",
            HERE + "p991a2_native_spark_numerics.py",
            "src/pygrc/models/grc_9_v4.py",
            "tests/models/test_grc_v4_spark_arg2b.py",
            "tests/models/test_grc_9_v4_spark_completion.py",
            BASE + "P9-9.1a.6-ARG2b-Contract.md",
            "specs/grc-v4-spark-native-a-rg2b-numerical-policy.md",
        }
    )
    previous = json.loads(
        lzma.decompress(
            (ROOT / (BASE + "P9-9.1a.6-CRG2b-Preflight.json.xz")).read_bytes()
        )
    )
    paths.update(
        r["path"]
        for r in previous["source_bindings"]
        if "/research/" in r["path"] or "/evidence/" in r["path"]
    )
    paths.update(
        INV + p
        for p in (
            "research/spark_completion_a_rg2b.py",
            "research/spark_completion_a_os.py",
            "evidence/spark-completion/applicability/ARG2bDeclaration.json",
            "evidence/spark-completion/applicability/ARG2bDirectDomain.json",
        )
    )
    return [
        {"path": p, "sha256": sha256((ROOT / p).read_bytes()).hexdigest()}
        for p in sorted(paths)
    ]


def run():
    flint.ctx.threads = 1
    need(
        not (ROOT / RECORD).exists() and not (ROOT / EVIDENCE).exists(),
        "refuse retained evidence overwrite",
    )
    tests = run_tests()
    info, evidence = benchmark()
    raw = encoded(evidence)
    (ROOT / EVIDENCE).write_bytes(raw)
    value = seal(
        dict(
            schema="grc9v4-native-arg2b-preflight-v1",
            family="A_RG2b",
            status="verified_pending_review",
            user_accepted=False,
            native_endpoint_verified=False,
            native_completion_support=False,
            full_trajectory_runs=0,
            endpoint_expectations_verified=False,
            duration="16",
            state_channels=["C", "W_A"],
            target_vertices=15,
            target_edges=16,
            full_domain_dimension=30,
            expected_endpoints={"current": [300, 302], "reset": [300, 302]},
            deferred_campaigns=["C_RG2b.5", "A_RG2b.5"],
            numerical_policy_id=ARG2B_NUMERICAL_POLICY,
            certificate_precision_bits=256,
            sampling_cap_seconds=SAMPLING_CAP,
            tests=tests,
            **info,
            estimate=estimate(info),
            machine={
                "platform": platform.platform(),
                "flint": flint.__version__,
                "flint_threads": flint.ctx.threads,
            },
            source_bindings=bindings(),
            evidence={"path": EVIDENCE, "sha256": sha256(raw).hexdigest()},
            evidence_storage={
                "codec": "xz",
                "compressed_bytes": len(raw),
                "factoring": "only exact adjacent state and section equality; full chain/writer witnesses retained",
            },
            stop_conditions=[
                "Reject incomplete joint inverse, writer, current or returned admission.",
                "Reprofile late-state, independent audit and cold recovery before a separately authorized .5 run.",
            ],
            synthetic_window_scope="actual near-domain map/lifecycle only; no source-to-entry claim",
            reset_scope="unadvanced source reset; retained old-edge W and seeded internal W; real reset fork has no live event",
        )
    )
    (ROOT / RECORD).write_bytes(encoded(value))
    print(
        f"A_RG2b_PREFLIGHT_PASS native_tests={tests['count']} samples=12+12 seconds={info['elapsed_seconds']:.2f} bytes={len(raw)}",
        flush=True,
    )
    return value


def check(root=ROOT, *, numerical=False):
    root = Path(root)
    v = json.loads(lzma.decompress((root / RECORD).read_bytes()))
    need(
        v == seal(v) and v["schema"] == "grc9v4-native-arg2b-preflight-v1",
        "preflight seal",
    )
    need(
        v["native_endpoint_verified"] is False
        and v["native_completion_support"] is False
        and v["full_trajectory_runs"] == 0
        and v["deferred_campaigns"] == ["C_RG2b.5", "A_RG2b.5"],
        "deferred endpoint scope",
    )
    need(
        v["tests"]["count"] == 21
        and v["tests"]["passed"]
        and all(len(r) == SAMPLE_COUNT for r in v["samples"].values()),
        "mandatory bounded roster",
    )
    for row in [*v["source_bindings"], v["evidence"]]:
        need(
            sha256((root / row["path"]).read_bytes()).hexdigest() == row["sha256"],
            "changed A_RG2b input: " + row["path"],
        )
    need(estimate(v) == v["estimate"], "measured forecast drift")
    if numerical:
        from pygrc.models.grc_9_v4_spark_contracts import GRC9V4SparkConfiguration

        e = json.loads(lzma.decompress((root / EVIDENCE).read_bytes()))
        c = GRC9V4SparkConfiguration.from_payload(e["source_configuration"])
        verify_step(c, c.current, decoded(e["source_transition"]), fresh_check=True)
        for role, rows in e["samples"].items():
            c = GRC9V4SparkConfiguration.from_payload(
                e["initial_snapshots"][role]["owner"]["publication"]["configuration"]
            )
            previous = None
            for row in rows:
                payload = expand(row["transition"], previous)
                step = decoded(payload)
                verify_step(
                    c,
                    step.before,
                    step,
                    fresh_check=row["independent"]["fresh_depth24"],
                )
                previous = payload
            need(
                previous["after"] == e["final_states"][role], "exact retained final C/W"
            )
        for p in e["certificates"]:
            certificates.CompletionCertificate.from_payload(p)
    return v


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--numerical", action="store_true")
    args = parser.parse_args()
    run() if args.run else check(numerical=args.numerical)

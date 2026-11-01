"""Bounded, changing-state public C_OS timings; never a closure campaign."""

import argparse
import json
import lzma
import math
import os
import platform
import resource
import statistics
import subprocess
import sys
import time
from contextlib import ExitStack
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
for directory in (ROOT, ROOT / "src"):
    sys.path.insert(0, str(directory))

import flint
from cos_native_spark_oracle import Equations, contains, matrix, vector
from flint import arb_mat, ctx, fmpq

from pygrc.models import grc_9_v4_completion_certificate as certificate_module
from pygrc.models import grc_9_v4_spark_owner as owner
from pygrc.models import grc_v4_numerics as numerics
from pygrc.models import grc_v4_spark_cos as kernel_module
from pygrc.models.grc_9_v4 import GRC9V4
from pygrc.models.grc_9_v4_completion_certificate import CompletionCertificate
from pygrc.models.grc_v4_certification import _ARB_CONTEXT_LOCK
from pygrc.models.grc_v4_codec import canonical_json_bytes
from pygrc.models.grc_v4_exact import current_exact_backend
from pygrc.models.grc_v4_geometry import GRCV4Graph
from pygrc.models.grc_v4_spark_cos import SparkCOSKernel
from pygrc.models.grc_v4_spark_state import NUMERICAL_POLICY
from tests.models.test_grc_9_v4_spark_completion import (
    certificate_pair,
    configuration,
    request,
)

HERE = "implementation/phase-9-grcv4/verification/"
BASE = "implementation/phase-9-grcv4/tranche-9/"
RECORD = BASE + "P9-9.1a.4-Preflight.json"
EVIDENCE = BASE + "P9-9.1a.4-Samples.json.xz"
SCRIPT = HERE + "p991a4_native_spark_preflight.py"
SAMPLING_CAP_SECONDS = 180
CAMPAIGN_CAP_SECONDS = 1800
MEMORY_CAP_MIB = 1024
HORIZON = {"current": 400, "reset": 400}


def seal(value):
    body = {k: v for k, v in value.items() if k != "record_digest"}
    return dict(
        body,
        record_digest=sha256(
            json.dumps(
                body, sort_keys=True, separators=(",", ":"), ensure_ascii=True
            ).encode()
        ).hexdigest(),
    )


def timed(function, *args, **kwargs):
    start = time.perf_counter()
    result = function(*args, **kwargs)
    return result, time.perf_counter() - start


def need(condition, message):
    if not condition:
        raise ValueError(message)


def rss():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024


def summary(values):
    need(
        bool(values) and all(math.isfinite(x) and x >= 0 for x in values),
        "finite nonempty timings required",
    )
    ordered = sorted(values)
    return {
        "count": len(values),
        "minimum": min(values),
        "median": statistics.median(values),
        "mean": statistics.mean(values),
        "p95": ordered[math.ceil(0.95 * len(values)) - 1],
        "maximum": max(values),
    }


def estimate(
    samples,
    setup_seconds,
    oracle_seconds,
    evidence_seconds,
    window_seconds,
    checkpoint_seconds,
    restore_seconds,
):
    """Conservative planning envelope, not a statistical confidence interval."""
    roles = {}
    for role, rows in samples.items():
        stats = summary([r["total_seconds"] for r in rows])
        overhead = max(oracle_seconds[role]) + max(evidence_seconds[role])
        mean = HORIZON[role] * (
            stats["mean"]
            + statistics.mean(oracle_seconds[role])
            + statistics.mean(evidence_seconds[role])
        )
        upper = HORIZON[role] * (1.5 * stats["maximum"] + 2 * overhead)
        roles[role] = {
            "step_seconds": stats,
            "horizon": HORIZON[role],
            "central_seconds": mean,
            "upper_seconds": upper,
            "oracle_per_step_upper": max(oracle_seconds[role]),
            "evidence_per_step_upper": max(evidence_seconds[role]),
        }
    checkpoint_unit = max(
        *(checkpoint_seconds[r] * HORIZON[r] / len(samples[r]) for r in HORIZON),
        checkpoint_seconds["synthetic_completed"],
    )
    persistence = 24 * checkpoint_unit + 8 * restore_seconds
    central = (
        setup_seconds
        + sum(r["central_seconds"] for r in roles.values())
        + window_seconds
        + persistence
    )
    upper = (
        2 * setup_seconds
        + sum(r["upper_seconds"] for r in roles.values())
        + 3 * window_seconds
        + 2 * persistence
    )
    return {
        "roles": roles,
        "central_seconds": central,
        "upper_seconds": upper,
        "campaign_cap_seconds": CAMPAIGN_CAP_SECONDS,
        "within_budget": upper <= CAMPAIGN_CAP_SECONDS,
        "persistence": {
            "checkpoint_writes": 24,
            "warm_restores": 8,
            "checkpoint_seconds": checkpoint_unit,
            "central_seconds": persistence,
            "upper_seconds": 2 * persistence,
            "scope": "snapshot/serialization/xz; checkpoint cost scaled to 400 beats; local write latency covered by safety allowance",
        },
        "method": "400 steps per role; 1.5x observed maximum step, 2x maximum oracle/evidence, 2x setup, 3x synthetic window, explicit checkpoint/restore allowance",
        "scope": "planning envelope from bounded early trajectories; not a confidence interval or endpoint proof",
    }


class Meter:
    """Delegating spies preserve public execution and record inclusive costs."""

    def __init__(self):
        self.parts, self.counts, self.backends, self.geometry_keys = {}, {}, set(), []
        self.last_step = None

    def reset(self):
        self.parts, self.counts, self.geometry_keys = {}, {}, []

    def wrap(self, target, name, label, stack):
        original = getattr(target, name)

        def execute(*args, **kwargs):
            start = time.perf_counter()
            try:
                result = original(*args, **kwargs)
                if label == "evolution":
                    self.last_step = result
                return result
            finally:
                self.parts[label] = (
                    self.parts.get(label, 0) + time.perf_counter() - start
                )
                self.counts[label] = self.counts.get(label, 0) + 1

        stack.enter_context(patch.object(target, name, execute))

    def install(self, stack):
        for target, name, label in (
            (SparkCOSKernel, "step", "evolution"),
            (SparkCOSKernel, "readmission", "readmission"),
            (owner, "progress", "completion"),
            (owner, "publish", "publication"),
            (numerics, "inverse", "inverse"),
        ):
            self.wrap(target, name, label, stack)
        original = SparkCOSKernel._read

        def read(k, C, H, operators):
            self.backends.add(current_exact_backend().value)
            self.counts["fixed_geometry_reads"] = (
                self.counts.get("fixed_geometry_reads", 0) + 1
            )
            return original(k, C, H, operators)

        stack.enter_context(patch.object(SparkCOSKernel, "_read", read))
        operators = SparkCOSKernel._operators

        def selected(k, H, reference=False):
            if not reference:
                self.geometry_keys.append(
                    sha256(canonical_json_bytes(kernel_module._rows(H))).hexdigest()
                )
            return operators(k, H, reference=reference)

        stack.enter_context(patch.object(SparkCOSKernel, "_operators", selected))


def transition(step):
    return {
        "before": step.before.to_payload(),
        "after": step.after.to_payload(),
        "duration": step.duration,
        "flux": list(step.flux),
        "exact_current": list(step.exact_current),
        "predictor_flat": list(step.predictor_flat),
        "selected_geometry": step.selected_geometry,
        "final_current": list(step.final_current),
        "reference_current": list(step.reference_current),
        "split_frobenius_squared": step.split_frobenius_squared,
    }


def encode_transition(step):
    data = transition(step)
    raw = canonical_json_bytes(data)
    return data, len(raw), len(lzma.compress(raw, preset=3))


def encode_checkpoint(model):
    data = model.snapshot()
    raw = canonical_json_bytes(data)
    lzma.compress(raw, preset=3)
    return data


def oracle_check(step, certificate):
    with _ARB_CONTEXT_LOCK, ctx.workprec(512):
        expected = Equations(step.before.graph.to_payload(), outward=True).step(
            step.before.C
        )
        need(
            contains(expected["corrector_current"], vector(step.exact_current)),
            "independent current mismatch",
        )
        error = arb_mat(matrix(certificate.operands["U"])) * (
            arb_mat(vector(step.after.C)) - expected["after"]
        )
        upper = max(abs(x).upper().fmpq() for x in error.entries())
        need(
            upper <= fmpq(certificate.proof["full_step_error"]),
            "full-step numerical bound failed",
        )
        return str(upper)


def benchmark(max_steps=40):
    need(
        max_steps in (20, 40),
        "preflight permits only 20 or 40 bounded samples per role",
    )
    ctx.threads = 1
    started = time.perf_counter()
    cache = kernel_module._reference_facts
    proof_cache = certificate_module._verify
    cache.cache_clear()
    proof_cache.cache_clear()
    meter = Meter()
    evidence, retained, oracles, encodings = (
        {},
        {},
        {r: [] for r in HORIZON},
        {r: [] for r in HORIZON},
    )
    setup, samples, checkpoint_seconds = {}, {r: [] for r in HORIZON}, {}
    with ExitStack() as stack:
        meter.install(stack)
        config, setup["configuration"] = timed(configuration)
        model, setup["initialization_cold"] = timed(GRC9V4, config)
        cold_cache = cache.cache_info()._asdict()
        _, setup["initialization_warm"] = timed(GRC9V4, config)
        result, setup["source_beat"] = timed(model.step)
        need(result.committed and result.local_gain == 0, "source step failed")
        event_request = request(model)
        result, setup["event"] = timed(model.expand, event_request)
        need(result.committed and result.local_gain == 0, "event failed")
        target = model.configuration
        (certificates, center), setup["certification_cold_pair"] = timed(
            certificate_pair, model
        )
        proof_cold = proof_cache.cache_info()._asdict()
        _, setup["certification_warm_pair"] = timed(
            lambda: tuple(
                CompletionCertificate.from_payload(c.to_payload()) for c in certificates
            )
        )
        proof_warm = proof_cache.cache_info()._asdict()
        need(
            proof_warm["hits"] >= proof_cold["hits"] + 2,
            "certificate proof reuse not active",
        )
        result, setup["certificate_installation"] = timed(
            model.install_completion_certificates, *certificates
        )
        need(result.committed, result.reason)
        reset, setup["reset_fork"] = timed(model.duplicate)
        result, setup["reset_readmission"] = timed(reset.reset)
        need(
            result.committed and reset._operation._published.completion.event is None,
            "reset comparison must have no live event",
        )
        roles = {"current": model, "reset": reset}
        certs = dict(zip(HORIZON, certificates, strict=True))
        initial = {r: m.configuration.current.to_payload() for r, m in roles.items()}
        proof_before_steps = proof_cache.cache_info()._asdict()
        rss_before = rss()

        def one(role):
            m, cert = roles[role], certs[role]
            before = m.configuration.current
            meter.reset()
            begin = time.perf_counter()
            result = m.step()
            need(
                result.committed and result.local_gain == 0,
                "early sample failed or unexpectedly completed",
            )
            comparison = 0
            if role == "reset":
                t = time.perf_counter()
                cert.require_binding(
                    owner.kernel(m.configuration),
                    m.configuration.policy,
                    "reset",
                    m.configuration.current.charge,
                )
                cert.membership(m.configuration.current)
                owner.classify(m.configuration.current, m.configuration.policy)
                comparison = time.perf_counter() - t
            elapsed = time.perf_counter() - begin
            state = m.configuration.current
            need(
                before != state,
                "repeated identical-state read is not a changing-state sample",
            )
            need(sum(map(fmpq, state.C)) == 21, "exact charge changed")
            need(
                meter.counts.get("inverse") == 2
                and meter.counts.get("fixed_geometry_reads") == 4,
                "selected inverse/reconstruction reuse changed",
            )
            parts = {
                key: meter.parts.get(key, 0)
                for key in ("evolution", "completion", "publication")
            }
            parts["reset_comparison"] = comparison
            parts["other"] = elapsed - sum(parts.values())
            need(parts["other"] >= 0, "overlapping main cost categories")
            row = {
                "beat": len(samples[role]) + 1,
                "total_seconds": elapsed,
                "parts_seconds": parts,
                "selected_geometry_key": meter.geometry_keys[0],
                "exact_charge": "21",
                "state_sha256": sha256(
                    canonical_json_bytes(state.to_payload())
                ).hexdigest(),
                "resource_bits": max(
                    max(
                        abs(fmpq(x).numerator).bit_length(),
                        fmpq(x).denominator.bit_length(),
                    )
                    for x in state.C
                ),
                "peak_rss_mib": rss(),
                "inverse_calls": 2,
                "fixed_geometry_reads": 4,
            }
            samples[role].append(row)
            if row["beat"] in (1, 20, 40):
                error, seconds = timed(oracle_check, meter.last_step, cert)
                oracles[role].append(seconds)
                (data, raw_bytes, compressed_bytes), seconds = timed(
                    encode_transition, meter.last_step
                )
                encodings[role].append(seconds)
                row.update(
                    oracle_error_upper=error,
                    oracle_seconds=oracles[role][-1],
                    transition_raw_bytes=raw_bytes,
                    transition_xz_bytes=compressed_bytes,
                    transition_encoding_seconds=seconds,
                )
                retained[role + "-" + str(row["beat"])] = data

        for role in HORIZON:
            one(role)
        first_cost = sum(samples[r][0]["total_seconds"] for r in HORIZON)
        elapsed = time.perf_counter() - started
        predicted = elapsed + 1.5 * first_cost * 19 + 25
        need(
            predicted < SAMPLING_CAP_SECONDS,
            "first-step estimate exceeds short sampling cap; optimize/re-estimate",
        )
        print(
            json.dumps(
                {
                    "stage": "first_steps",
                    "seconds_by_role": {
                        r: samples[r][0]["total_seconds"] for r in HORIZON
                    },
                    "projected_twenty_step_preflight_seconds": predicted,
                    "cap_seconds": SAMPLING_CAP_SECONDS,
                }
            ),
            flush=True,
        )
        target_count = 20
        while True:
            for role in HORIZON:
                while len(samples[role]) < target_count:
                    remaining = sum(
                        target_count - len(rows) for rows in samples.values()
                    )
                    worst = max(
                        row["total_seconds"]
                        for rows in samples.values()
                        for row in rows
                    )
                    need(
                        time.perf_counter() - started + remaining * worst + 15
                        < SAMPLING_CAP_SECONDS,
                        "short cap no longer fits sample; stop and re-estimate",
                    )
                    one(role)
                    need(rss() < MEMORY_CAP_MIB, "preflight memory cap reached")
            elapsed = time.perf_counter() - started
            worst_sum = sum(
                max(row["total_seconds"] for row in rows) for rows in samples.values()
            )
            if (
                target_count == 20
                and max_steps == 40
                and elapsed + 1.5 * 20 * worst_sum + 25 < SAMPLING_CAP_SECONDS
            ):
                target_count = 40
                print(
                    json.dumps(
                        {
                            "stage": "extend_to_forty",
                            "elapsed_seconds": elapsed,
                            "projected_seconds": elapsed + 1.5 * 20 * worst_sum + 25,
                        }
                    ),
                    flush=True,
                )
            else:
                break
        proof_after_steps = proof_cache.cache_info()._asdict()
        need(
            proof_before_steps == proof_after_steps,
            "full certificate unexpectedly reproved per step",
        )
        need(meter.backends == {"flint"}, "native read left FLINT backend")
        for role, rows in samples.items():
            need(
                len({r["selected_geometry_key"] for r in rows}) == len(rows),
                "changed geometry reused a stale inverse",
            )
            evidence[role], checkpoint_seconds[role] = timed(
                encode_checkpoint, roles[role]
            )
        _, setup["warm_checkpoint_restore"] = timed(
            GRC9V4.from_state, evidence["current"]
        )

        # A changed port chart must miss the graph-key cache, even when B agrees.
        graph = target.reference.graph.to_payload()
        from copy import deepcopy

        changed = deepcopy(graph)
        for edge in changed["edges"]:
            if edge["kind"] == "spine":
                old = edge["tail"]["port"]
                new = {2: 3, 6: 4, 7: 8}[old]
                edge["tail"]["port"] = edge["head"]["port"] = new
        before_changed = cache.cache_info()._asdict()
        SparkCOSKernel(GRCV4Graph.from_payload(changed), target.reference.profile)
        after_changed = cache.cache_info()._asdict()
        need(
            after_changed["misses"] == before_changed["misses"] + 1,
            "graph operand cache invalidation failed",
        )
        altered = deepcopy(certificates[0].operands.to_dict())
        altered["binding"]["duration"] = "64"
        from pygrc.models.grc_v4_state import FrozenJSONMap

        before_bad = proof_cache.cache_info()._asdict()
        try:
            CompletionCertificate(FrozenJSONMap(altered))
        except ValueError:
            pass
        else:
            raise ValueError("changed certificate duration admitted")
        after_bad = proof_cache.cache_info()._asdict()
        need(
            after_bad["misses"] == before_bad["misses"] + 1
            and after_bad["currsize"] == before_bad["currsize"],
            "invalid proof cached",
        )

        # Cost only: explicitly synthetic in-domain lifecycle, never a witness prefix.
        from tests.models.test_grc_9_v4_spark_completion import (
            NativeSparkCompletionTests,
        )

        fixture = NativeSparkCompletionTests()
        fixture.event_model, fixture.certificates, fixture.center = (
            model,
            certificates,
            center,
        )
        synthetic, setup["synthetic_window_setup"] = timed(
            fixture.synthetic_window_fixture
        )
        window = []
        for i in range(3):
            meter.reset()
            result, seconds = timed(synthetic.step)
            need(
                result.committed and result.local_gain == int(i == 2),
                "synthetic window cost probe failed",
            )
            window.append(
                {
                    "seconds": seconds,
                    "parts": dict(meter.parts),
                    "gain": result.local_gain,
                }
            )
        _, checkpoint_seconds["synthetic_completed"] = timed(
            encode_checkpoint, synthetic
        )
        need(
            time.perf_counter() - started < SAMPLING_CAP_SECONDS,
            "preflight exceeded declared short cap",
        )

    estimated = estimate(
        samples,
        sum(setup.values()),
        oracles,
        encodings,
        sum(x["seconds"] for x in window),
        checkpoint_seconds,
        setup["warm_checkpoint_restore"],
    )
    native_record = json.loads(
        (ROOT / (BASE + "P9-9.1a.3-Verification.json")).read_bytes()
    )
    paths = {
        SCRIPT,
        HERE + "cos_native_spark_oracle.py",
        HERE + "p991a2_native_spark_numerics.py",
        BASE + "P9-9.1a.3-Verification.json",
    }
    paths.update(
        row["path"]
        for row in native_record["source_bindings"]
        if row["path"].startswith(("src/", "specs/", "tests/"))
        or "/research/" in row["path"]
        or "/evidence/" in row["path"]
    )
    raw_evidence = canonical_json_bytes(
        {
            "initial_roles": initial,
            "checkpoints": evidence,
            "selected_transitions": retained,
        }
    )
    compressed = lzma.compress(raw_evidence, preset=3)
    data = {
        "schema": "grc9v4-native-spark-preflight-v1",
        "leaf": "P9-9.1a.4",
        "family": "C_OS",
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "entry_revision": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "status": "preflight_pass_budgeted"
        if estimated["within_budget"]
        else "preflight_over_budget",
        "native_endpoint_verified": False,
        "native_completion_support": False,
        "full_trajectory_runs": 0,
        "numerical_policy_id": NUMERICAL_POLICY,
        "exact_backend": "flint",
        "flux_bits": 128,
        "certificate_precision_bits": 512,
        "machine": {
            "platform": platform.platform(),
            "python": platform.python_version(),
            "flint": flint.__version__,
            "flint_threads": ctx.threads,
            "cpu_count": os.cpu_count(),
            "thread_environment": {
                k: os.environ.get(k)
                for k in (
                    "OMP_NUM_THREADS",
                    "OPENBLAS_NUM_THREADS",
                    "MKL_NUM_THREADS",
                    "NUMEXPR_NUM_THREADS",
                )
            },
        },
        "source_vertices": 12,
        "source_edges": 13,
        "target_vertices": 15,
        "target_edges": 16,
        "exact_charge": "21",
        "duration": "32",
        "source_configuration_digest": config.scientific_digest,
        "target_graph_digest": target.reference.graph.graph_digest,
        "target_profile_id": target.reference.profile.complete_profile_id,
        "certificate_ids": [c.certificate_id for c in certificates],
        "expected_endpoints": {"current": [374, 376], "reset": [375, 377]},
        "endpoint_expectations_verified": False,
        "sampling_cap_seconds": SAMPLING_CAP_SECONDS,
        "elapsed_seconds": time.perf_counter() - started,
        "setup_seconds": setup,
        "samples": samples,
        "oracle_seconds": oracles,
        "transition_encoding_seconds": encodings,
        "checkpoint_seconds": checkpoint_seconds,
        "synthetic_window": window,
        "synthetic_window_scope": "cost probe at supplied center; no source-to-entry trajectory",
        "reset_scope": "public reset invalidates event; reset-certificate comparison only, zero live gain",
        "caches": {
            "cold_graph": cold_cache,
            "final_graph": cache.cache_info()._asdict(),
            "proof_cold": proof_cold,
            "proof_warm": proof_warm,
            "proof_before_steps": proof_before_steps,
            "proof_after_steps": proof_after_steps,
            "graph_change_before": before_changed,
            "graph_change_after": after_changed,
            "invalid_certificate_before": before_bad,
            "invalid_certificate_after": after_bad,
            "selected_inverse_calls_per_step": 2,
            "fixed_geometry_reads_per_step": 4,
            "changing_geometry_keys_unique": True,
            "active_backends": sorted(meter.backends),
        },
        "memory": {
            "before_sample_peak_mib": rss_before,
            "final_peak_mib": rss(),
            "cap_mib": MEMORY_CAP_MIB,
            "scope": "process peak RSS; no full-horizon memory guarantee",
        },
        "estimate": estimated,
        "next_leaf": "P9-9.1a.5",
        "stop_conditions": [
            "400 target beats per role without expected result: investigate, never force completion",
            "rolling 8-step mean above 1.5 times sampled maximum: stop/re-estimate",
            "remaining upper projection exceeds 30-minute combined campaign cap: stop/re-estimate",
            "RSS above 1024 MiB or resource bit size above twice sampled maximum: stop/re-estimate",
            "failed numerical/certificate/charge admission or changed graph/profile/policy: stop",
        ],
        "evidence": {
            "path": EVIDENCE,
            "sha256": sha256(compressed).hexdigest(),
            "compressed_bytes": len(compressed),
            "raw_bytes": len(raw_evidence),
        },
        "source_bindings": [
            {"path": p, "sha256": sha256((ROOT / p).read_bytes()).hexdigest()}
            for p in sorted(paths)
        ],
    }
    return seal(data), compressed


def check(root=ROOT):
    root = Path(root)
    value = json.loads((root / RECORD).read_bytes())
    need(
        value == seal(value) and value["schema"] == "grc9v4-native-spark-preflight-v1",
        "unsealed preflight",
    )
    need(
        value["full_trajectory_runs"] == 0
        and value["native_endpoint_verified"] is False
        and value["native_completion_support"] is False,
        "preflight cannot grant endpoint support",
    )
    for row in [*value["source_bindings"], value["evidence"]]:
        need(
            sha256((root / row["path"]).read_bytes()).hexdigest() == row["sha256"],
            "changed preflight subject: " + row["path"],
        )
    recomputed = estimate(
        value["samples"],
        sum(value["setup_seconds"].values()),
        value["oracle_seconds"],
        value["transition_encoding_seconds"],
        sum(x["seconds"] for x in value["synthetic_window"]),
        value["checkpoint_seconds"],
        value["setup_seconds"]["warm_checkpoint_restore"],
    )
    need(recomputed == value["estimate"], "estimate differs from retained timings")
    need(
        all(len(rows) in (20, 40) for rows in value["samples"].values()),
        "bounded mandatory sample count",
    )
    return value


def main():
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--run", action="store_true")
    mode.add_argument("--check", action="store_true")
    parser.add_argument("--max-steps", type=int, choices=(20, 40), default=40)
    args = parser.parse_args()
    if args.run:
        value, raw = benchmark(args.max_steps)
        (ROOT / EVIDENCE).write_bytes(raw)
        (ROOT / RECORD).write_text(json.dumps(value, indent=2) + "\n")
    else:
        value = check()
    print(
        json.dumps(
            {
                k: value[k]
                for k in (
                    "status",
                    "elapsed_seconds",
                    "estimate",
                    "memory",
                    "next_leaf",
                )
            }
        )
    )


if __name__ == "__main__":
    main()

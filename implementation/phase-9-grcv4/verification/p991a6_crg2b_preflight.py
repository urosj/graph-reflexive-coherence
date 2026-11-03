"""Bounded C_RG2b native preflight; exact section witnesses, no endpoint grant."""

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
from crg2b_native_spark_oracle import _audited_read, selected, verify_step
from p991a2_native_spark_numerics import row_oracle
from p991a4_native_spark_preflight import estimate as base_estimate
from p991a4_native_spark_preflight import need, rss, seal, timed
from p991a6_crg2b_subjects import certificate_pair, configuration, request

from pygrc.models import grc_9_v4_completion_certificate as certificates
from pygrc.models import grc_9_v4_spark_owner as owner
from pygrc.models import grc_v4_spark_crg2b as native
from pygrc.models.grc_9_v4 import GRC9V4
from pygrc.models.grc_9_v4_completion_crg2b import membership_details
from pygrc.models.grc_v4_codec import canonical_json_bytes
from pygrc.models.grc_v4_spark_state import CRG2B_NUMERICAL_POLICY, ExactResources
from pygrc.models.grc_v4_state import FrozenJSONMap
from tests.models.test_grc_v4_spark_crg2b import NativeCRG2bTests

BASE = "implementation/phase-9-grcv4/tranche-9/"
HERE = "implementation/phase-9-grcv4/verification/"
INV = "implementation/investigations/grc9v4-constitutive-design/"
RECORD = BASE + "P9-9.1a.6-CRG2b-Preflight.json.xz"
EVIDENCE = BASE + "P9-9.1a.6-CRG2b-Samples.json.xz"
SCRIPT = HERE + "p991a6_crg2b_preflight.py"
REFERENCE = BASE + "P9-9.1a.6-CRG2b-PerformanceReference.json.xz"
OPTIMIZATION_PATCH = BASE + "P9-9.1a.6-CRG2b-Optimization.patch"
SAMPLE_COUNT = 20
SAMPLING_CAP = 600


def encoded(value):
    return lzma.compress(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode(), preset=3
    )


def transition(step):
    return {
        "before": step.before.to_payload(),
        "after": step.after.to_payload(),
        "profile_id": step.profile_id,
        "duration": step.duration,
        "flux": list(step.flux),
        "componentwise_error_bounds": list(step.componentwise_error_bounds),
        "section": step.section.to_dict(),
        "restart_section": step.restart_section.to_dict(),
        "final_current": [list(x) for x in step.final_current],
        "reference_current": list(step.reference_current),
    }


def decoded(value):
    data = dict(value)
    for key in ("before", "after"):
        data[key] = ExactResources.from_canonical_bytes(canonical_json_bytes(data[key]))
    for key in ("section", "restart_section"):
        data[key] = FrozenJSONMap(data[key])
    for key in ("flux", "componentwise_error_bounds", "reference_current"):
        data[key] = tuple(data[key])
    data["final_current"] = tuple(tuple(x) for x in data["final_current"])
    return native.SparkCRG2bStep(**data)


def compact(value, previous):
    """Only exact repeated fields are omitted; all chain residuals are retained."""
    data = dict(value)
    if previous is not None:
        need(value["before"] == previous["after"], "stream state continuity")
        need(
            value["section"] == previous["restart_section"],
            "pure section reuse changed witness",
        )
        data.pop("before")
        data.pop("section")
    return data


def expand(value, previous):
    data = dict(value)
    if previous is not None:
        need(
            "before" not in data and "section" not in data,
            "noncanonical repeated stream fields",
        )
        data["before"] = previous["after"]
        data["section"] = previous["restart_section"]
    return data


def independent_membership(model, certificate):
    """Re-evaluate the proposed parameter and exact metric without native curve code."""
    from flint import fmpq as Q
    from flint import fmpq_mat as M

    state = model.configuration.current
    actual = membership_details(certificate, state)
    graph = state.graph.to_payload()
    B = M(
        [
            [
                int(e["tail"]["node_id"] == n) - int(e["head"]["node_id"] == n)
                for e in graph["edges"]
            ]
            for n in graph["live_node_ids"]
        ]
    )
    n, m = B.nrows(), B.ncols()
    I = M([[int(i == j) for j in range(m)] for i in range(m)])
    A = B * (I + (Q(3, 4) * I + B.transpose() * B).inv() / 4) * B.transpose()
    P = (A + M([[Q(1, n)] * n for _ in range(n)])).inv()
    x = 2 * Q(actual["parameter"]) - 1
    t = [Q(1), x]
    rows = certificate.operands["curve"]
    for _ in range(2, len(rows[0])):
        t.append(2 * x * t[-1] - t[-2])
    point = [sum(Q(c) * v for c, v in zip(row, t, strict=True)) for row in rows]
    d = M([[Q(c) - p] for c, p in zip(state.C, point, strict=True)])
    sq = (d.transpose() * P * d)[0, 0] / Q(certificate.operands["radius"]) ** 2
    need(
        str(sq) == actual["squared_norm"] and actual["inside"] == (sq <= 1),
        "independent exact curved witness",
    )
    row_oracle(state)
    return actual


def run_tests():
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(NativeCRG2bTests)
    names = [t._testMethodName for t in suite]
    need(len(names) == 23, "mandatory C_RG2b roster")
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


def estimate(info, tests):
    value = base_estimate(
        info["samples"],
        sum(info["setup_seconds"].values()),
        info["oracle_seconds"],
        info["transition_encoding_seconds"],
        tests["seconds"],
        info["checkpoint_seconds"],
        info["setup_seconds"]["warm_checkpoint_restore"],
    )
    for role, rows in info["samples"].items():
        costs = {
            flag: [
                x
                for row, x in zip(rows, info["oracle_seconds"][role], strict=True)
                if row["fresh_depth40"] is flag
            ]
            for flag in (False, True)
        }
        need(
            all(costs.values()),
            "both proof-only and deeper-cross-check timings required",
        )
        target = value["roles"][role]
        old_central, old_upper = target["central_seconds"], target["upper_seconds"]
        counts = {False: 378, True: 22}
        central_audit = sum(
            counts[flag] * statistics.mean(costs[flag]) for flag in counts
        )
        upper_audit = sum(counts[flag] * 2 * max(costs[flag]) for flag in counts)
        target["central_seconds"] = (
            400
            * (
                target["step_seconds"]["mean"]
                + statistics.mean(info["transition_encoding_seconds"][role])
            )
            + central_audit
        )
        target["upper_seconds"] = (
            400
            * (
                1.5 * target["step_seconds"]["maximum"]
                + 2 * max(info["transition_encoding_seconds"][role])
            )
            + upper_audit
        )
        target["audit_workload"] = {
            "complete_proof_checks": 400,
            "additional_depth40_cross_checks": 22,
            "rule": "initial/final and every 20 beats; all 400 beats retain full independent chain/error checks",
            "proof_only_mean_seconds": statistics.mean(costs[False]),
            "deep_comparison_mean_seconds": statistics.mean(costs[True]),
            "central_seconds": central_audit,
            "upper_seconds": upper_audit,
        }
        value["central_seconds"] += target["central_seconds"] - old_central
        value["upper_seconds"] += target["upper_seconds"] - old_upper
    value["method"] += (
        "; stratified complete proof checks and periodic extra depth40 solves, each charged separately"
    )
    cold = 2 * 400 / SAMPLE_COUNT * info["setup_seconds"]["cold_checkpoint_restore"]
    value["cold_replay_allowance"] = {
        "measured_early_seconds": info["setup_seconds"]["cold_checkpoint_restore"],
        "assumed_full_restores": 2,
        "sample_steps": SAMPLE_COUNT,
        "central_seconds": cold,
        "upper_seconds": 2 * cold,
        "scope": "linear early-journal extrapolation; remeasure late checkpoint cost before .5",
    }
    value["pressure_checkpoint_reserve_seconds"] = 240
    value["central_seconds"] += cold + 240
    value["upper_seconds"] += 2 * cold + 240
    value["profiling_target_seconds"] = value.pop("campaign_cap_seconds")
    value["within_budget"] = value["upper_seconds"] < value["profiling_target_seconds"]
    value["timing_policy"] = (
        "profile and re-estimate; thirty minutes is advisory, never an artificial loss of valid results"
    )
    return value


def benchmark():
    flint.ctx.threads = 1
    for cache in (
        native._section_witness,
        native._reference_facts,
        native._algebra_facts,
        native._matrix_facts,
        native.global_domain,
        certificates._verify,
        selected,
        _audited_read,
    ):
        cache.cache_clear()
    start = time.perf_counter()
    setup = {}
    config, setup["configuration"] = timed(configuration)
    model, setup["initialization_cold"] = timed(GRC9V4, config)
    cold = native.SparkCRG2bKernel.cache_info()
    _, setup["initialization_warm"] = timed(GRC9V4, config)
    warm = native.SparkCRG2bKernel.cache_info()
    for key in ("graph", "domain", "section"):
        need(
            warm[key]["hits"] > cold[key]["hits"],
            "no complete-subject/static cache hit: " + key,
        )
    original_step = native.SparkCRG2bKernel.step
    captured = []
    reads = []
    writes = []
    backends = set()
    original_read = native.SparkCRG2bKernel._admitted_section
    original_write = ExactResources.advance

    def capture(k, *args, **kwargs):
        value = original_step(k, *args, **kwargs)
        captured.append(value)
        return value

    def read(k, state):
        from pygrc.models.grc_v4_exact import current_exact_backend

        backends.add(current_exact_backend().value)
        reads.append(state.to_canonical_bytes())
        return original_read(k, state)

    def write(state, *args, **kwargs):
        writes.append(True)
        return original_write(state, *args, **kwargs)

    with patch.object(native.SparkCRG2bKernel, "step", capture):
        result, setup["source_beat"] = timed(model.step)
    need(result.committed, result.reason)
    source = transition(captured[0])
    source_report, setup["source_independent_audit"] = timed(verify_step, captured[0])
    result, setup["event"] = timed(model.expand, request(model))
    need(result.committed, result.reason)
    event = model._operation._published.completion.event.to_dict()
    (pair, _), setup["certification_cold_pair"] = timed(certificate_pair, model)
    proof_cold = certificates._verify.cache_info()._asdict()
    _, setup["certification_warm_pair"] = timed(
        lambda: tuple(
            certificates.CompletionCertificate.from_payload(c.to_payload())
            for c in pair
        )
    )
    proof_warm = certificates._verify.cache_info()._asdict()
    need(
        proof_warm["hits"] >= proof_cold["hits"] + 2,
        "full certificate proof not reused",
    )
    need(
        model.install_completion_certificates(*pair).committed,
        "certificate installation",
    )
    reset, setup["reset_fork"] = timed(model.duplicate)
    result, setup["reset_readmission"] = timed(reset.reset)
    need(
        result.committed and reset._operation._published.completion.event is None,
        "real reset must clear event",
    )
    roles = {"current": model, "reset": reset}
    initial = {r: m.snapshot() for r, m in roles.items()}
    samples = {r: [] for r in roles}
    oracles = {r: [] for r in roles}
    encodings = {r: [] for r in roles}
    retained = {r: [] for r in roles}
    prior = dict.fromkeys(roles)
    full_costs = []
    with (
        patch.object(native.SparkCRG2bKernel, "step", capture),
        patch.object(native.SparkCRG2bKernel, "_admitted_section", read),
        patch.object(ExactResources, "advance", write),
    ):
        for i in range(SAMPLE_COUNT):
            for role, m in roles.items():
                need(
                    time.perf_counter() - start < SAMPLING_CAP,
                    "bounded preflight time cap",
                )
                captured.clear()
                reads.clear()
                writes.clear()
                before = m.configuration.current
                result, seconds = timed(m.step)
                need(result.committed and result.local_gain == 0, result.reason)
                need(
                    len(captured) == 1 and len(reads) == 2 and len(writes) == 1,
                    "two selected reads and exactly one physical C write required",
                )
                step = captured[0]
                need(
                    step.before == before and step.after == m.configuration.current,
                    "actual execution capture",
                )
                (audit, observed), oracle = timed(
                    lambda step=step, m=m, role=role, i=i: (
                        verify_step(step, fresh=i in (0, SAMPLE_COUNT - 1)),
                        independent_membership(m, pair[0 if role == "current" else 1]),
                    )
                )
                payload = transition(step)
                need(
                    transition(decoded(payload)) == payload,
                    "typed transition round trip",
                )
                compacted = compact(payload, prior[role])
                need(
                    expand(compacted, prior[role]) == payload,
                    "lossless witness factoring",
                )
                raw, coding = timed(encoded, compacted)
                prior[role] = payload
                samples[role].append(
                    {
                        "total_seconds": seconds,
                        "fresh_reads": 2,
                        "full_state_writes": 1,
                        "fresh_depth40": i in (0, SAMPLE_COUNT - 1),
                        "compressed_bytes": len(raw),
                    }
                )
                oracles[role].append(oracle)
                encodings[role].append(coding)
                retained[role].append(
                    {
                        "transition": compacted,
                        "independent": audit,
                        "membership": observed,
                    }
                )
                full_costs.append(seconds + oracle + coding)
            if i == 1:
                remaining = 2 * (SAMPLE_COUNT - 2)
                projected = (
                    time.perf_counter()
                    - start
                    + 1.5 * remaining * max(full_costs[-2:])
                    + 45
                )
                need(
                    projected < SAMPLING_CAP,
                    "two-step measured audit/storage forecast does not fit bounded cap",
                )
                print(
                    json.dumps(
                        {
                            "stage": "two-step gate",
                            "projected_seconds": projected,
                            "cache_reuse": True,
                        }
                    ),
                    flush=True,
                )
            if (i + 1) % 5 == 0:
                print(
                    json.dumps(
                        {
                            "stage": "bounded samples",
                            "per_role": i + 1,
                            "elapsed": time.perf_counter() - start,
                        }
                    ),
                    flush=True,
                )
    checkpoints = {}
    for role, m in roles.items():
        _, checkpoints[role] = timed(lambda m=m: encoded(m.snapshot()))
    checkpoints["synthetic_completed"] = max(checkpoints.values())
    snapshot = model.snapshot()
    restored, setup["warm_checkpoint_restore"] = timed(GRC9V4.from_state, snapshot)
    need(restored.snapshot() == snapshot, "warm restore mismatch")
    with patch.object(owner, "_SCOPES", {}):
        restored, setup["cold_checkpoint_restore"] = timed(GRC9V4.from_state, snapshot)
        need(restored.snapshot() == snapshot, "cold journal replay mismatch")
    need(backends == {"flint"}, "left exact FLINT backend")
    need(
        _audited_read.cache_info().hits >= 2 * (SAMPLE_COUNT - 1),
        "identical independent witness proofs not reused",
    )
    need(
        time.perf_counter() - start < SAMPLING_CAP and rss() < 1024,
        "bounded runtime/memory",
    )
    info = {
        "samples": samples,
        "oracle_seconds": oracles,
        "transition_encoding_seconds": encodings,
        "setup_seconds": setup,
        "checkpoint_seconds": checkpoints,
        "elapsed_seconds": time.perf_counter() - start,
        "caches": {
            "cold": cold,
            "warm": warm,
            "final": native.SparkCRG2bKernel.cache_info(),
            "independent_final": selected.cache_info()._asdict(),
            "independent_witness_final": _audited_read.cache_info()._asdict(),
            "proof_cold": proof_cold,
            "proof_warm": proof_warm,
        },
        "memory": {"final_peak_mib": rss(), "cap_mib": 1024},
        "certificates": [c.to_payload() for c in pair],
    }
    return info, {
        "samples": retained,
        "source_transition": source,
        "source_independent": source_report,
        "source_configuration": config.to_payload(),
        "event": event,
        "initial_snapshots": initial,
        "final_states": {
            r: m.configuration.current.to_payload() for r, m in roles.items()
        },
    }


def bindings():
    paths = {
        str(p.relative_to(ROOT))
        for pattern in ("*spark*.py", "grc_9_v4_completion*.py")
        for p in (ROOT / "src/pygrc/models").glob(pattern)
    }
    paths.update(
        {
            SCRIPT,
            REFERENCE,
            OPTIMIZATION_PATCH,
            HERE + "p991a6_crg2b_subjects.py",
            HERE + "crg2b_native_spark_oracle.py",
            HERE + "p991a2_native_spark_numerics.py",
            HERE + "p991a4_native_spark_preflight.py",
            HERE + "cos_native_spark_oracle.py",
            "src/pygrc/models/grc_9_v4.py",
            "tests/models/test_grc_v4_spark_crg2b.py",
            "tests/models/test_grc_9_v4_spark_completion.py",
            BASE + "P9-9.1a.6-CRG2b-Contract.md",
            "specs/grc-v4-spark-native-c-rg2b-numerical-policy.md",
        }
    )
    # Bind the independent research dependency closure as frozen inputs.
    prior = json.loads((ROOT / (BASE + "P9-9.1a.6-CPC-Preflight.json")).read_bytes())
    paths.update(
        r["path"]
        for r in prior["source_bindings"]
        if "/research/" in r["path"] or "/evidence/" in r["path"]
    )
    paths.update(
        INV + p
        for p in (
            "research/spark_completion_c_rg2b.py",
            "research/spark_completion_ci_campaign.py",
            "evidence/spark-completion/applicability/CRG2bDirectDomain.json",
            "evidence/spark-completion/applicability/CRG2bDirectDeclaration.json",
        )
    )
    return [
        {"path": p, "sha256": sha256((ROOT / p).read_bytes()).hexdigest()}
        for p in sorted(paths)
    ]


def performance_comparison(evidence):
    baseline = json.loads(lzma.decompress((ROOT / REFERENCE).read_bytes()))
    need(baseline == seal(baseline), "unsealed development reference")
    need(
        {k: evidence["source_transition"][k] for k in ("flux", "after")}
        == baseline["source"],
        "source output changed under optimization",
    )
    for role, rows in evidence["samples"].items():
        need(
            [{k: r["transition"][k] for k in ("flux", "after")} for r in rows]
            == baseline["traces"][role],
            "represented target trajectory changed under optimization: " + role,
        )
    return {
        "reference": REFERENCE,
        "patch": OPTIMIZATION_PATCH,
        "identical_source_and_40_target_outputs": True,
        "baseline_elapsed_seconds": baseline["measurements"]["elapsed_seconds"],
        "baseline_step_mean_seconds": statistics.mean(
            r["total_seconds"]
            for rows in baseline["measurements"]["samples"].values()
            for r in rows
        ),
        "baseline_audit_mean_seconds": statistics.mean(
            x
            for rows in baseline["measurements"]["oracle_seconds"].values()
            for x in rows
        ),
        "fixed_production_precision_bits": 256,
        "fixed_current_error_bits": 160,
        "fixed_flux_bits": 128,
        "full_chain_residuals_checked_everywhere": True,
        "periodic_deep_solves_are_additional_checks": True,
        "baseline_bulk_evidence_retained": False,
    }


def run():
    need(
        not (ROOT / RECORD).exists() and not (ROOT / EVIDENCE).exists(),
        "do not overwrite retained preflight",
    )
    tests = run_tests()
    print("23 native C_RG2b tests passed.", flush=True)
    info, evidence = benchmark()
    comparison = performance_comparison(evidence)
    raw = encoded(evidence)
    value = seal(
        dict(
            schema="grc9v4-native-crg2b-preflight-v1",
            family="C_RG2b",
            leaf="P9-9.1a.6-C_RG2b",
            status="implemented_verified_pending_review",
            user_accepted=False,
            native_endpoint_verified=False,
            native_completion_support=False,
            full_trajectory_runs=0,
            endpoint_expectations_verified=False,
            expected_endpoints={"current": [390, 392], "reset": [390, 392]},
            exact_backend="flint",
            state_channels=["C"],
            full_domain_dimension=14,
            target_vertices=15,
            target_edges=16,
            duration="8",
            exact_charge="21",
            numerical_policy_id=CRG2B_NUMERICAL_POLICY,
            certificate_precision_bits=256,
            oracle_precision_bits=768,
            machine={
                "python": platform.python_version(),
                "flint": flint.__version__,
                "flint_threads": flint.ctx.threads,
            },
            tests=tests,
            optimization=comparison,
            estimate=estimate(info, tests),
            sampling_cap_seconds=SAMPLING_CAP,
            synthetic_window_scope="near-curve fixtures only; no source-to-entry claim",
            reset_scope="public reset, cleared event, zero gain",
            evidence_storage={
                "format": "lossless_exact_section_stream_v1",
                "exact_target_transitions": 40,
                "section_depth": 32,
                "adjacent_duplicate_state_and_section_omitted": True,
                "future_supporting_steps": 0,
                "complete_independent_chain_checks": 40,
                "fresh_depth40_target_transitions": 4,
            },
            stop_conditions=[
                "Stop on failed section, inverse, enclosure or admission.",
                "Re-estimate late trajectory, checkpoint, oracle and storage costs before .5.",
                "At 400 steps diagnose membership before extending; never assume endpoint entry.",
            ],
            source_bindings=bindings(),
            evidence={"path": EVIDENCE, "sha256": sha256(raw).hexdigest()},
            **info,
        )
    )
    (ROOT / EVIDENCE).write_bytes(raw)
    (ROOT / RECORD).write_bytes(encoded(value))
    print(
        json.dumps(
            {
                "record": RECORD,
                "elapsed": info["elapsed_seconds"],
                "estimate": value["estimate"],
                "evidence_bytes": len(raw),
            },
            indent=2,
        ),
        flush=True,
    )
    return value


def check(root=ROOT, *, numerical=False):
    from p991a6_arg2b_epoch import previous_bytes
    root = Path(root)
    value = json.loads(lzma.decompress((root / RECORD).read_bytes()))
    need(
        value == seal(value) and value["schema"] == "grc9v4-native-crg2b-preflight-v1",
        "unsealed C_RG2b preflight",
    )
    need(
        value["native_endpoint_verified"] is False
        and value["native_completion_support"] is False
        and value["full_trajectory_runs"] == 0
        and value["endpoint_expectations_verified"] is False,
        "preflight scope changed",
    )
    for row in [*value["source_bindings"], value["evidence"]]:
        need(
            sha256(previous_bytes(root, row["path"])).hexdigest() == row["sha256"],
            "changed C_RG2b input: " + row["path"],
        )
    need(
        all(len(rows) == SAMPLE_COUNT for rows in value["samples"].values()),
        "mandatory sample count",
    )
    need(value["tests"]["count"] == 23 and value["tests"]["passed"], "mandatory tests")
    need(
        estimate(value, value["tests"]) == value["estimate"],
        "measured forecast mismatch",
    )
    if numerical:
        data = json.loads(lzma.decompress((root / EVIDENCE).read_bytes()))
        need(
            performance_comparison(data) == value["optimization"],
            "optimization trace comparison mismatch",
        )
        verify_step(decoded(data["source_transition"]))
        for role, rows in data["samples"].items():
            prior = None
            for row in rows:
                payload = expand(row["transition"], prior)
                verify_step(
                    decoded(payload),
                    fresh=row["independent"]["incoming"]["fresh_depth40"],
                )
                prior = payload
            need(
                prior["after"] == data["final_states"][role],
                "stream final state mismatch",
            )
    return value


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--numerical", action="store_true")
    args = parser.parse_args()
    run() if args.run else check(numerical=args.numerical)

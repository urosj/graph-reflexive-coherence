"""Measure all ten V4 realization fixtures at numerical and public boundaries.

Run in an isolated process from the repository root:
    PYTHONPATH=src:.:tests .venv/bin/python scripts/profile_grc_v4_families.py

Input construction, snapshot restoration and output hashing are excluded from
step timing. Default repetitions execute the same input. With --evolving, repetitions are
successive ordinary public steps followed by one fresh profiled step.
Exclusive timer categories subtract nested measured work. Separate inclusive
identity/projection observations overlap those categories. Instrumentation
patches are temporary and restored after each step; use only in this benchmark.
"""

import argparse
import copy
import cProfile
import functools
import hashlib
import json
import pstats
import statistics
import sys
import time
from collections import defaultdict
from pathlib import Path

from pygrc.models import grc_v4_candidate_a as ca
from pygrc.models import grc_v4_candidate_c as cc
from pygrc.models import grc_v4_ci as ci
from pygrc.models import grc_v4_codec as codec
from pygrc.models import grc_v4_numerics as numerics
from pygrc.models.grc_v4_geometry import GeometryStageInputs
from pygrc.models.grc_v4_lifecycle import _profile_step
from tests.models.test_grc_v4_generic_lifecycle import FAMILIES, fixture, model, restore
from tests.models.test_grc_v4_lifecycle import request

DEST = Path("/tmp/grcv4-cost-analysis/families")
REPEATS = 5
patches = []
stack = []
exclusive = defaultdict(float)
counts = defaultdict(int)
inclusive = defaultdict(float)
seen = {}


def measured(fn, label):
    @functools.wraps(fn)
    def call(*args, **kwargs):
        frame = [time.perf_counter(), 0.0]
        stack.append(frame)
        try:
            return fn(*args, **kwargs)
        finally:
            elapsed = time.perf_counter() - frame[0]
            stack.pop()
            exclusive[label] += elapsed - frame[1]
            counts[label] += 1
            if stack:
                stack[-1][1] += elapsed

    return call


def observed(fn, label, identity=False):
    @functools.wraps(fn)
    def call(*args, **kwargs):
        category = label
        if identity:
            obj = args[0]
            key = id(obj)
            category += ":repeat" if key in seen else ":first"
            seen[key] = obj
        start = time.perf_counter()
        try:
            return fn(*args, **kwargs)
        finally:
            inclusive[category] += time.perf_counter() - start
            counts[category] += 1

    return call


def install():
    modules = [
        m
        for n, m in tuple(sys.modules.items())
        if n.startswith("pygrc.models.grc_v4") and m
    ]

    def aliases(fn, label):
        wrapped = measured(fn, label)
        for mod in modules:
            for name, value in tuple(vars(mod).items()):
                if value is fn:
                    patches.append((mod, name, value))
                    setattr(mod, name, wrapped)

    for name, label in [
        ("json_value", "json_copy"),
        ("canonical_json_bytes", "encoding"),
        ("_canonical_validated_bytes", "encoding"),
        ("_load_contract_schema", "assets"),
        ("_validation_result", "schema"),
    ]:
        aliases(getattr(codec, name), label)
    aliases(copy.deepcopy, "deep_copy")
    aliases(numerics.solve, "selected_arithmetic")
    aliases(ci._analytic_residual, "selected_arithmetic")
    for cls in (ca.CandidateACurrent, cc.CandidateCCurrent):
        descriptor = cls.__dict__["identity"]
        patches.append((cls, "identity", descriptor))
        cls.identity = property(
            observed(descriptor.fget, cls.__name__ + ".identity", identity=True)
        )
    for name in ("to_payload", "from_payload"):
        descriptor = GeometryStageInputs.__dict__[name]
        patches.append((GeometryStageInputs, name, descriptor))
        if isinstance(descriptor, classmethod):
            wrapped = classmethod(observed(descriptor.__func__, "stage." + name))
        else:
            wrapped = observed(descriptor, "stage." + name)
        setattr(GeometryStageInputs, name, wrapped)


def uninstall():
    for obj, name, original in reversed(patches):
        setattr(obj, name, original)
    patches.clear()


def digest(payload):
    return hashlib.sha256(codec.canonical_json_bytes(payload)).hexdigest()


def timed(run):
    start = time.perf_counter()
    result = run()
    return result, time.perf_counter() - start


def analyze(family, boundary, prepare, payload):
    # Warm complete operation once. Every repetition receives the same input.
    result = prepare()()
    expected = digest(payload(result))
    plain = []
    for _ in range(REPEATS):
        result, elapsed = timed(prepare())
        plain.append(elapsed)
        if digest(payload(result)) != expected:
            raise RuntimeError("measurement changed the output hash")
    instrumented = []
    for _ in range(REPEATS):
        run = prepare()  # construction/readmission is outside measurement
        exclusive.clear()
        counts.clear()
        inclusive.clear()
        seen.clear()
        install()
        try:
            result, elapsed = timed(run)
        finally:
            uninstall()
        instrumented.append(
            {
                "elapsed": elapsed,
                "exclusive": dict(exclusive),
                "inclusive": dict(inclusive),
                "counts": dict(counts),
            }
        )
        if digest(payload(result)) != expected:
            raise RuntimeError("measurement changed the output hash")
    run = prepare()
    profiler = cProfile.Profile()
    start = time.perf_counter()
    result = profiler.runcall(run)
    profiled_elapsed = time.perf_counter() - start
    if digest(payload(result)) != expected:
        raise RuntimeError("profiling changed the output hash")
    profiler.dump_stats(str(DEST / f"{family}-{boundary}.prof"))
    stats = pstats.Stats(profiler)
    top = sorted(stats.stats.items(), key=lambda item: item[1][2], reverse=True)[:15]
    names = set().union(*(r["exclusive"] for r in instrumented))
    observed_names = set().union(*(r["inclusive"] for r in instrumented))
    report = {
        "family": family,
        "boundary": boundary,
        "plain_seconds": plain,
        "median_seconds": statistics.median(plain),
        "instrumented_seconds": [r["elapsed"] for r in instrumented],
        "mean_instrumented_seconds": statistics.mean(
            r["elapsed"] for r in instrumented
        ),
        "mean_exclusive_seconds": {
            n: statistics.mean(r["exclusive"].get(n, 0) for r in instrumented)
            for n in names
        },
        "mean_inclusive_seconds": {
            n: statistics.mean(r["inclusive"].get(n, 0) for r in instrumented)
            for n in observed_names
        },
        "counts": instrumented[-1]["counts"],
        "total_calls": stats.total_calls,
        "profiled_seconds": profiled_elapsed,
        "output_sha256": expected,
        "top_exclusive": [
            {
                "file": k[0],
                "line": k[1],
                "name": k[2],
                "calls": v[1],
                "self_seconds": v[2],
                "cumulative_seconds": v[3],
            }
            for k, v in top
        ],
    }
    (DEST / f"{family}-{boundary}.json").write_text(json.dumps(report, indent=2))
    print(
        json.dumps(
            {
                k: report[k]
                for k in (
                    "family",
                    "boundary",
                    "median_seconds",
                    "total_calls",
                    "output_sha256",
                )
            }
        ),
        flush=True,
    )
    return report


def public_payload(result):
    owner, receipt = result
    if not receipt.committed:
        raise RuntimeError(str(receipt.failure))
    return owner.snapshot()


def profile_evolving(count, destination, families=FAMILIES):
    """Time new states/results; profile a subsequent fresh public step."""
    reports = []
    for family in families:
        inputs, _ = fixture(family)
        owner = model(family)
        seconds = []
        hashes = []
        for index in range(count + 1):
            command = request(inputs.dt, f"benefit-comparison-{index}")
            profiler = cProfile.Profile() if index == count else None
            started = time.perf_counter()
            result = (
                profiler.runcall(owner.step_v4_input, command)
                if profiler is not None
                else owner.step_v4_input(command)
            )
            elapsed = time.perf_counter() - started
            if not result.committed:
                raise RuntimeError(str(result.failure))
            if profiler is None:
                seconds.append(elapsed)
            hashes.append(digest(owner.snapshot()))
        profiler.dump_stats(str(destination / f"{family}.prof"))
        report = {
            "family": family,
            "seconds": seconds,
            "median_seconds": statistics.median(seconds),
            "profiled_seconds": elapsed,
            "total_calls": pstats.Stats(profiler).total_calls,
            "snapshot_sha256": hashes,
        }
        reports.append(report)
        (destination / "results.json").write_text(json.dumps(reports, indent=2))
        print(
            json.dumps(
                {
                    key: report[key]
                    for key in ("family", "median_seconds", "total_calls")
                }
            ),
            flush=True,
        )
    print("complete", flush=True)


def main():
    global DEST, REPEATS
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repetitions", type=int, default=5)
    parser.add_argument("--output", type=Path, default=DEST)
    parser.add_argument(
        "--family",
        choices=FAMILIES,
        action="append",
        help="select a family; repeat to select several (default: all)",
    )
    parser.add_argument(
        "--evolving",
        action="store_true",
        help="measure successive public steps, then profile one fresh step",
    )
    args = parser.parse_args()
    if args.repetitions < 1:
        parser.error("--repetitions must be positive")
    REPEATS = args.repetitions
    DEST = args.output
    DEST.mkdir(parents=True, exist_ok=True)
    if args.evolving:
        profile_evolving(REPEATS, DEST, args.family or FAMILIES)
        return
    reports = []
    for family in args.family or FAMILIES:
        inputs, backend = fixture(family)
        numerical = analyze(
            family,
            "numerical",
            lambda inputs=inputs, backend=backend: (
                lambda: _profile_step(inputs, backend)
            ),
            lambda step: step.next_inputs.to_payload(),
        )
        reports.append(numerical)
        baseline = model(family).snapshot()
        command = request(inputs.dt, "cost-analysis")

        def public_prepare(baseline=baseline, command=command):
            owner = restore(baseline)

            def run():
                return owner, owner.step_v4_input(command)

            return run

        reports.append(analyze(family, "public", public_prepare, public_payload))
        (DEST / "results.json").write_text(json.dumps(reports, indent=2))
    print("complete", flush=True)


if __name__ == "__main__":
    main()

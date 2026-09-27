"""Profile the two-step Candidate A CI fixture from the performance investigation.

Run from the repository root with the V4 extra installed:
    PYTHONPATH=src:.:tests .venv/bin/python scripts/profile_grc_v4_ci.py

Fixture construction and output hashing are outside the step timings. The first
step is timed normally; the final step runs under cProfile (two steps by default). Compare matching rows
and output hashes across revisions; profiler time is not ordinary wall time.
"""

import argparse
import cProfile
import hashlib
import io
import json
import pstats
import time
from dataclasses import replace

from pygrc.models.grc_v4_ci import ProvisionalCandidateCIStep
from pygrc.models.grc_v4_codec import canonical_json_bytes
from tests.models.test_grc_v4_ci import fixture


def profile_event_validation(count: int) -> None:
    from pygrc.models.grc_v4_event_codec import POLICY_ID, validate_event_payload

    payload = {
        "schema_version": "grcv4-coordinate-map-v1", "policy_id": POLICY_ID,
        "source_graph_digest": "grc-graph-sha256:" + "a" * 64,
        "target_graph_digest": "grc-graph-sha256:" + "b" * 64,
        "vertex_map": [], "edge_map": [],
    }
    # Closed wire validation only; these declarations do not admit a graph map.
    validate_event_payload("representation/correspondence_payload", payload)
    started = time.perf_counter()
    for _ in range(count):
        result = validate_event_payload("representation/correspondence_payload", payload)
    elapsed = time.perf_counter() - started
    digest = hashlib.sha256(canonical_json_bytes(result)).hexdigest()
    print(json.dumps({"lookups": count, "seconds": elapsed, "sha256": digest}))


def profile_families() -> None:
    from tests.models.test_grc_v4_generic_lifecycle import FAMILIES, model, restore
    from tests.models.test_grc_v4_generic_lifecycle import fixture as family_fixture
    from tests.models.test_grc_v4_lifecycle import request

    for family in FAMILIES:
        owner = model(family)
        command = request(family_fixture(family)[0].dt, "performance")
        started = time.perf_counter()
        result = owner.step_v4_input(command)
        elapsed = time.perf_counter() - started
        if not result.committed:
            raise RuntimeError(f"{family}: {result.failure}")
        snapshot = owner.snapshot()
        started = time.perf_counter()
        restored = restore(snapshot)
        restore_elapsed = time.perf_counter() - started
        if canonical_json_bytes(restored.snapshot()) != canonical_json_bytes(snapshot):
            raise RuntimeError(f"{family}: restoration changed the snapshot")
        print(json.dumps({
            "family": family, "step_seconds": elapsed,
            "restore_seconds": restore_elapsed,
            "snapshot_sha256": hashlib.sha256(canonical_json_bytes(snapshot)).hexdigest(),
        }), flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--event-validation", type=int, metavar="N",
        help="time N repeated additive-event schema validations instead of CI steps",
    )
    parser.add_argument(
        "--families", action="store_true",
        help="time public step and restore boundaries for all ten accepted V4 families",
    )
    parser.add_argument(
        "--steps", type=int, metavar="N",
        help="run N CI steps and profile the final step (default: 2)",
    )
    args = parser.parse_args()
    if args.steps is not None:
        if args.steps < 2:
            parser.error("--steps must be at least 2")
        if args.families or args.event_validation is not None:
            parser.error("--steps applies to the CI fixture only")
    if args.families:
        if args.event_validation is not None:
            parser.error("--families and --event-validation are mutually exclusive")
        profile_families()
        return
    if args.event_validation is not None:
        if args.event_validation <= 0:
            parser.error("--event-validation must be positive")
        profile_event_validation(args.event_validation)
        return
    started = time.perf_counter()
    before, backend = fixture(
        "A", C=(3.0, 1.0), W=(2.0,), gain=0.25, radius=0.25,
        changes={"candidate": {"eta": 0.025}},
    )
    before = replace(before, dt=0.5)
    print(f"fixture: {time.perf_counter() - started:.6f}s", flush=True)
    profiler = cProfile.Profile()
    count = 2 if args.steps is None else args.steps
    for index in range(count):
        started = time.perf_counter()
        if index == count - 1:
            profiler.enable()
        try:
            step = ProvisionalCandidateCIStep(before, backend)
        finally:
            profiler.disable()
        elapsed = time.perf_counter() - started
        before = step.next_inputs
        digest = hashlib.sha256(canonical_json_bytes(before.to_payload())).hexdigest()
        print(json.dumps({
            "step": index + 1, "seconds": elapsed, "profiled": index == count - 1,
            "next_inputs_sha256": digest,
        }), flush=True)
    stream = io.StringIO()
    pstats.Stats(profiler, stream=stream).sort_stats("cumulative").print_stats(30)
    print(stream.getvalue(), flush=True)


if __name__ == "__main__":
    main()

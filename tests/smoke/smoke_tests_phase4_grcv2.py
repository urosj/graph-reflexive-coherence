#!/usr/bin/env python3
"""Phase 4 deep smoke tests for the executable GRCV2 loop."""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from pygrc.core import digest_snapshot
from pygrc.models import GRCV2


PASS = 0
FAIL = 0


def check(name: str, condition: bool, details: str = "") -> None:
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  OK   {name}")
    else:
        FAIL += 1
        print(f"  FAIL {name}")
        if details:
            print(f"       {details}")


def section(title: str) -> None:
    print(f"\n{title}")
    print("-" * len(title))


def valid_grcv2_config() -> dict[str, object]:
    return {
        "dt": 0.1,
        "evolution": {
            "alpha": 1.0,
            "beta": 1.0,
            "gamma": 1.0,
            "delta": 1.0,
            "eta": 1.0,
            "kappa_c": 1.0,
            "lambda_c": 1.0,
            "xi_c": 1.0,
            "zeta_c": 1.0,
            "site_potential_selection": "quadratic",
            "site_potential_params": {"mu": 0.0},
            "eps_spark": 0.01,
            "h_thr": 0.0,
            "tau_split": 2.0,
            "lambda_birth": 1e9,
            "alpha_seed": 0.5,
            "eps_prune": 0.001,
            "rng_seed": 0,
            "spark_backend": "cheeger_proxy",
        },
        "constitutive_semantic_modes": {
            "curvature_backend": "none",
            "frame_mode": "combinatorial",
            "boundary_mode": "prune",
            "split_distribution_mode": "equal",
            "edge_label_selection": "all",
        },
    }


def executable_state() -> dict[str, object]:
    return {
        "topology": {
            "nodes": [{"node_id": 0, "payload": {}}, {"node_id": 1, "payload": {}}],
            "edges": [{"edge_id": 0, "node_a": 0, "node_b": 1, "payload": {}}],
            "incidence": {"0": [0], "1": [0]},
        },
        "nodes": {"0": 2.0, "1": 1.0},
        "edges": {"0": 1.0},
    }


def build_model() -> GRCV2:
    config = valid_grcv2_config()
    config["state"] = executable_state()
    return GRCV2.from_config(config)


def event_kinds(step_result) -> list[str]:
    return [event.kind for event in step_result.events]


def run_step_sequence(model: GRCV2, steps: int) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for _ in range(steps):
        result = model.step()
        records.append(
            {
                "step_index": result.step_index,
                "time": result.time,
                "event_kinds": event_kinds(result),
                "observables": dict(result.observables),
                "node_ids": tuple(model.get_state().topology.iter_live_node_ids()),
                "edge_ids": tuple(model.get_state().topology.iter_live_edge_ids()),
                "nodes": dict(model.get_state().nodes),
                "edges": dict(model.get_state().edges),
            }
        )
    return records


def main() -> int:
    section("1. End-to-End Deterministic Loop")
    model_a = build_model()
    model_b = build_model()
    records_a = run_step_sequence(model_a, 4)
    records_b = run_step_sequence(model_b, 4)
    check("Loop-repeatable", records_a == records_b)
    check(
        "Loop-produces-topology-events",
        any("split_init" in record["event_kinds"] or "birth" in record["event_kinds"] for record in records_a),
    )
    check(
        "Loop-budget-preserved",
        all(abs(record["observables"]["budget_error"]) <= 1e-12 for record in records_a),
    )

    section("2. Snapshot, Digest, And Resume")
    model_c = build_model()
    pre_records = run_step_sequence(model_c, 2)
    snapshot_1 = model_c.snapshot()
    snapshot_2 = model_c.snapshot()
    digest_1 = digest_snapshot(snapshot_1)
    digest_2 = digest_snapshot(snapshot_2)
    check("Snapshot-repeatable", snapshot_1 == snapshot_2)
    check("Digest-repeatable", digest_1 == digest_2)
    check("Snapshot-has-events", len(snapshot_1["events"]) > 0)

    with tempfile.TemporaryDirectory() as temp_dir:
        path = Path(temp_dir) / "grcv2-smoke.json"
        model_c.save(str(path))
        restored = GRCV2.load(str(path))

    cont_original = run_step_sequence(model_c, 2)
    cont_restored = run_step_sequence(restored, 2)
    check("Resume-records-match", cont_original == cont_restored)
    check(
        "Resume-counters-match",
        restored.get_state().topology.next_node_id == model_c.get_state().topology.next_node_id
        and restored.get_state().topology.next_edge_id == model_c.get_state().topology.next_edge_id,
    )

    section("3. Reset Baseline")
    model_d = build_model()
    initial_snapshot = model_d.snapshot()
    run_step_sequence(model_d, 3)
    model_d.reset()
    check("Reset-restores-snapshot", model_d.snapshot() == initial_snapshot)

    print("\n" + "=" * 48)
    print(f"Phase 4 smoke results: {PASS} passed, {FAIL} failed")
    if FAIL:
        print("Phase 4 smoke failed.")
        return 1
    print("All Phase 4 smoke tests passed. OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

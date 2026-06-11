#!/usr/bin/env python3
"""Paper-alignment smoke tests for the executable GRCV2 loop."""

from __future__ import annotations

import math
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

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


def base_config() -> dict[str, object]:
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
            "tau_split": 2.0,
            "lambda_birth": 0.25,
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


def build_model(state: dict[str, object], *, evolution_overrides: dict[str, object] | None = None) -> GRCV2:
    config = base_config()
    if evolution_overrides:
        config["evolution"].update(evolution_overrides)
    config["state"] = state
    return GRCV2.from_config(config)


def simple_two_node_state() -> dict[str, object]:
    return {
        "topology": {
            "nodes": [{"node_id": 0, "payload": {}}, {"node_id": 1, "payload": {}}],
            "edges": [{"edge_id": 0, "node_a": 0, "node_b": 1, "payload": {}}],
            "incidence": {"0": [0], "1": [0]},
        },
        "nodes": {"0": 2.0, "1": 1.0},
        "edges": {"0": 1.0},
    }


def main() -> int:
    section("1. Canonical Step Order")
    model = build_model(simple_two_node_state(), evolution_overrides={"lambda_birth": 0.0})
    result = model.step()
    expected_order = (
        "compute_geometry",
        "compute_metric",
        "compute_edge_labels",
        "build_laplacian",
        "compute_potential",
        "compute_flux",
        "detect_identities",
        "detect_events",
        "apply_topology_changes",
        "apply_front_birth",
        "apply_boundary_behavior",
        "apply_continuity",
        "enforce_budget",
        "compute_observables",
    )
    check("Step-order", result.bookkeeping["step_order"] == expected_order)

    section("2. Eq.(4) Potential And Eq.(5) Flux")
    metric_state = simple_two_node_state()
    metric_state["flux"] = {"0:0": 0.5, "0:1": -0.5}
    model = build_model(metric_state, evolution_overrides={"lambda_birth": 0.0})
    model.step()
    state = model.get_state()
    conductance = state.edges[0]
    node_tensor_0 = state.cached_quantities["node_tensors"][0]
    node_tensor_1 = state.cached_quantities["node_tensors"][1]
    expected_conductance = math.exp(
        -1.0 * (2.0 + 1.0) / 2.0
        - 1.0 * ((2.0 - 1.0) ** 2) / 2.0
        - 1.0 * (0.5**2) / 2.0
        - 1.0 * 0.0
    )
    phi_0 = conductance * (2.0 - 1.0) - (2.0 * 2.0)
    phi_1 = conductance * (1.0 - 2.0) - (2.0 * 1.0)
    flux_01 = -1.0 * conductance * (phi_0 - phi_1)
    check(
        "Eq1-tensor-node0",
        node_tensor_0["tensor_diagonal"] == (3.25,),
        f"got {node_tensor_0['tensor_diagonal']}",
    )
    check(
        "Eq1-tensor-node1",
        node_tensor_1["tensor_diagonal"] == (2.25,),
        f"got {node_tensor_1['tensor_diagonal']}",
    )
    check(
        "Eq2-conductance",
        math.isclose(state.edges[0], expected_conductance, rel_tol=1e-12, abs_tol=1e-12),
        f"expected {expected_conductance}, got {state.edges[0]}",
    )
    check(
        "Eq4-potential-node0",
        math.isclose(state.potential[0], phi_0, rel_tol=1e-12, abs_tol=1e-12),
        f"expected {phi_0}, got {state.potential[0]}",
    )
    check(
        "Eq4-potential-node1",
        math.isclose(state.potential[1], phi_1, rel_tol=1e-12, abs_tol=1e-12),
        f"expected {phi_1}, got {state.potential[1]}",
    )
    check(
        "Eq5-flux",
        math.isclose(state.flux[(0, 0)], flux_01, rel_tol=1e-12, abs_tol=1e-12),
        f"expected {flux_01}, got {state.flux[(0, 0)]}",
    )
    check(
        "Eq5-antisymmetry",
        math.isclose(state.flux[(0, 0)], -state.flux[(0, 1)], rel_tol=1e-12, abs_tol=1e-12),
    )

    section("3. Identity Basins From Directed Flux")
    identity_state = {
        "topology": {
            "nodes": [
                {"node_id": 0, "payload": {}},
                {"node_id": 1, "payload": {}},
                {"node_id": 2, "payload": {}},
            ],
            "edges": [
                {"edge_id": 0, "node_a": 0, "node_b": 1, "payload": {}},
                {"edge_id": 1, "node_a": 1, "node_b": 2, "payload": {}},
            ],
            "incidence": {"0": [0], "1": [0, 1], "2": [1]},
        },
        "nodes": {"0": 3.0, "1": 2.0, "2": 1.0},
        "edges": {"0": 1.0, "1": 1.0},
    }
    model = build_model(identity_state, evolution_overrides={"lambda_birth": 0.0})
    model.step()
    state = model.get_state()
    check("Sink-set", state.sink_set == {2}, f"got {state.sink_set}")
    check("Basins", state.basins == {2: {0, 1, 2}}, f"got {state.basins}")
    check(
        "Successor-map",
        state.cached_quantities.get("successor_map") == {0: 1, 1: 2, 2: None},
        f"got {state.cached_quantities.get('successor_map')}",
    )

    section("4. Spark To Soft Split Progression")
    spark_state = {
        "topology": {
            "nodes": [
                {"node_id": 0, "payload": {}},
                {"node_id": 1, "payload": {}},
                {"node_id": 2, "payload": {}},
                {"node_id": 3, "payload": {}},
            ],
            "edges": [
                {"edge_id": 0, "node_a": 0, "node_b": 1, "payload": {}},
                {"edge_id": 1, "node_a": 2, "node_b": 3, "payload": {}},
            ],
            "incidence": {"0": [0], "1": [0], "2": [1], "3": [1]},
        },
        "nodes": {"0": 2.0, "1": 1.0, "2": 2.0, "3": 1.0},
        "edges": {"0": 1.0, "1": 1.0},
    }
    model = build_model(
        spark_state,
        evolution_overrides={
            "h_thr": 0.1,
            "lambda_birth": 1e9,
        },
    )
    step_1 = model.step()
    kinds_1 = [event.kind for event in step_1.events]
    check("Spark-emitted", "spark" in kinds_1, f"got {kinds_1}")
    check("Split-init-emitted", "split_init" in kinds_1, f"got {kinds_1}")
    check(
        "Split-registry-created",
        len(model.get_state().split_registry) == 2,
        f"got {len(model.get_state().split_registry)}",
    )
    step_2 = model.step()
    kinds_2 = [event.kind for event in step_2.events]
    check("Split-progress-emitted", "split_progress" in kinds_2, f"got {kinds_2}")
    step_3 = model.step()
    kinds_3 = [event.kind for event in step_3.events]
    check("Split-complete-emitted", "split_complete" in kinds_3, f"got {kinds_3}")

    section("5. Birth, Continuity, And Budget Closure")
    model = build_model(simple_two_node_state(), evolution_overrides={"h_thr": 0.0, "lambda_birth": 1e9})
    step = model.step()
    state = model.get_state()
    check("Birth-event", "birth" in [event.kind for event in step.events])
    check(
        "Continuity-delta-present",
        "last_continuity_delta" in state.cached_quantities,
    )
    check(
        "Budget-closed",
        abs(step.observables["budget_error"]) <= 1e-12,
        f"got {step.observables['budget_error']}",
    )
    check("Birth-rule-explicit", state.cached_quantities.get("birth_rule_mode") == "bernoulli_probability")
    check(
        "Non-negative-coherence",
        all(value >= 0.0 for value in state.nodes.values()),
        f"got {state.nodes}",
    )

    section("6. Persistence And Replay")
    model = build_model(simple_two_node_state(), evolution_overrides={"h_thr": 0.0})
    first_records = []
    for _ in range(2):
        result = model.step()
        first_records.append(
            {
                "observables": dict(result.observables),
                "events": [(event.kind, dict(event.payload)) for event in result.events],
            }
        )
    snapshot_before = model.snapshot()
    with tempfile.TemporaryDirectory() as temp_dir:
        path = Path(temp_dir) / "paper-alignment.json"
        model.save(str(path))
        restored = GRCV2.load(str(path))
    continued_original = model.step()
    continued_restored = restored.step()
    check("Snapshot-repeatable-family", snapshot_before["metadata"]["model_family"] == "GRCV2")
    check(
        "Replay-observables",
        continued_original.observables == continued_restored.observables,
    )
    check(
        "Replay-events",
        [(event.kind, event.payload) for event in continued_original.events]
        == [(event.kind, event.payload) for event in continued_restored.events],
    )

    section("7. Honest Scope Note")
    print("  NOTE Node-tensor bookkeeping and the exponential conductance law now follow the paper-aligned baseline realization checked above.")
    print("  NOTE Front birth now follows the Bernoulli rule with deterministic replay through explicit RNG state / seed handling.")
    print("  NOTE Curvature backends now use in-house Forman and Ollivier implementations on the weighted graph substrate.")
    print("  NOTE This smoke validates loop structure and the tightened constitutive core under deterministic replay conditions.")

    print("\n" + "=" * 60)
    print(f"Phase 4 paper-alignment smoke results: {PASS} passed, {FAIL} failed")
    if FAIL:
        print("Phase 4 paper-alignment smoke failed.")
        return 1
    print("All Phase 4 paper-alignment smoke tests passed. OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

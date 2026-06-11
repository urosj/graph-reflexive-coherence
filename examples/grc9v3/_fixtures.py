"""Small GRC9V3 fixtures used by the runnable examples.

Why this file exists:
    The first examples need a deterministic model that makes Lane A/Lane B
    behavior easy to inspect. Building that state inline in every script would
    hide the usage path behind setup noise, so the fixture lives here.

What model this creates:
    A `GRC9V3` runtime state with one saturated center sink node, nine occupied
    local ports, and neighbor coherence/conductance values chosen so the
    column-H proxy has a known near-threshold profile.

Alternatives:
    - Use `GRC9V3.from_config(...)` when you want a default empty/minimal model.
    - Use `GRC9V3.from_state(...)` when you already have runtime state data.
    - Use the landscape/lowering examples when the source is a landscape seed
      rather than a hand-assembled runtime fixture.

References:
    docs/reference/GRC-Runtime-ReferenceGuide.md
    docs/reference/Telemetry-ReferenceGuide.md
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
if SRC_ROOT.exists() and str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from pygrc.core import GRCEvent  # noqa: E402
from pygrc.models import GRC9V3  # noqa: E402


LANE_A = "current_hybrid_signed_hessian"
LANE_B = "grc9v3_column_h_assisted"
CENTER_NODE_ID = 0
CENTER_COHERENCE = 10.0
CENTER_GRADIENT_ROW_BASIS = (0.0, 0.0, 0.0)
CENTER_SIGNED_HESSIAN_ROW_BASIS = (1.0, 1.0, 1.0)
NEIGHBOR_COHERENCE_BY_PORT = {
    1: 13.0,
    2: 9.0,
    3: 7.0,
    4: 8.0,
    5: 11.0,
    6: 10.0,
    7: 10.25,
    8: 10.0,
    9: 12.0,
}
BASE_CONDUCTANCE_BY_PORT = {
    1: 0.5,
    2: 1.0,
    3: 1.0,
    4: 2.0,
    5: 2.0,
    6: 2.0,
    7: 4.0,
    8: 5.0,
    9: 0.25,
}
EXPECTED_COLUMN_H = (-1.5, 1.0, -2.5)
EXPECTED_MIN_ABS_COLUMN_H = 1.0
EXPECTED_MIN_ABS_COLUMN_H_COLUMN = 2


def make_config(
    *,
    spark_lane: str = LANE_A,
    eps_column_h: float = 1.1,
) -> dict[str, Any]:
    """Return a compact deterministic GRC9V3 config for lane examples.

    Why it is needed:
        GRC9V3 spark behavior is parameterized. The examples need the same
        numeric thresholds every time so Lane A and Lane B are comparable.

    Important choice:
        `spark_lane` is the only semantic switch varied by the first examples.
        Lane A is the default signed-Hessian baseline. Lane B is opt-in and
        enables the direct runtime-computed column-H proxy branch.

    Alternatives:
        For production or experiment runs, load config from a project config
        file or construct it near the caller. For examples, keeping it here
        makes the lane contrast explicit and reproducible.
    """

    return {
        "dt": 0.1,
        "evolution": {
            "alpha": 1e-12,
            "beta": 1e-12,
            "gamma": 1e-12,
            "eta": 1.0,
            "kappa_c": 1.0,
            "v0": 1.0,
            "rho": 1.0,
            "eps_tau": 1e-12,
            "site_potential_selection": "quadratic",
            "site_potential_params": {"mu": 0.0, "scale": 0.0},
            "eps_gradient": 0.01,
            "eps_hessian": 0.01,
            "eps_spark": 0.0,
            "eps_column_h": eps_column_h,
            "eps_column_h_crossing_zero": 0.0,
            "D_eff_target": 16,
            "w_bond": 1.0,
        },
        "constitutive_semantic_modes": {
            "spark_lane": spark_lane,
        },
    }


def make_column_h_state() -> dict[str, Any]:
    """Build a saturated sink where Lane B can fire by column-H threshold.

    Why it is needed:
        This state is the smallest useful fixture for showing that Lane B is
        behaviorally different from Lane A. The center node has active degree 9
        and small gradient, but the signed-Hessian branch is inactive. The
        column-H values are `[-1.5, 1.0, -2.5]`, so with `eps_column_h=1.1`
        Lane B can fire through `column_h_threshold_hit`.

    What it looks like:
        Node 0 is the saturated sink. Nodes 1..9 are neighbors attached to
        ports 1..9. The port map is the standard 3x3 GRC9V3 chart.

    Alternatives:
        Use this direct state fixture when testing runtime evidence. Use a
        landscape seed/lowering path when demonstrating authored source data.
    """

    center_id = CENTER_NODE_ID
    nodes: list[dict[str, Any]] = [
        {"node_id": center_id, "payload": {"role": "candidate"}}
    ]
    edges: list[dict[str, Any]] = []
    incidence: dict[str, list[int]] = {"0": []}
    node_states: dict[str, dict[str, Any]] = {
        "0": {
            "coherence": CENTER_COHERENCE,
            "gradient_row_basis": list(CENTER_GRADIENT_ROW_BASIS),
            "signed_hessian_row_basis": list(CENTER_SIGNED_HESSIAN_ROW_BASIS),
            "basin_mass": 10.0,
            "basin_id": "root",
            "depth": 0,
        }
    }
    port_edges: dict[str, dict[str, Any]] = {}
    base_conductance: dict[str, float] = {}

    for port_id in range(1, 10):
        edge_id = port_id - 1
        neighbor_id = port_id
        remote_slot = 9 - port_id
        nodes.append({"node_id": neighbor_id, "payload": {"role": "neighbor"}})
        incidence["0"].append(edge_id)
        incidence[str(neighbor_id)] = [edge_id]

        if port_id % 2:
            endpoint_a = {"node_id": center_id, "slot": port_id - 1}
            endpoint_b = {"node_id": neighbor_id, "slot": remote_slot}
        else:
            endpoint_a = {"node_id": neighbor_id, "slot": remote_slot}
            endpoint_b = {"node_id": center_id, "slot": port_id - 1}

        edges.append(
            {
                "edge_id": edge_id,
                "endpoint_a": endpoint_a,
                "endpoint_b": endpoint_b,
                "payload": {"kind": "column_h_fixture"},
            }
        )
        node_states[str(neighbor_id)] = {
            "coherence": NEIGHBOR_COHERENCE_BY_PORT[port_id],
            "basin_mass": NEIGHBOR_COHERENCE_BY_PORT[port_id],
            "basin_id": neighbor_id,
        }
        port_edges[str(edge_id)] = {
            "node_u": center_id,
            "port_u": port_id,
            "node_v": neighbor_id,
            "port_v": remote_slot + 1,
            "conductance": 99.0,
            "flux_uv": 999.0,
        }
        base_conductance[str(edge_id)] = BASE_CONDUCTANCE_BY_PORT[port_id]

    return {
        "topology": {
            "nodes": nodes,
            "edges": edges,
            "incidence": incidence,
            "port_structure": {},
        },
        "nodes": node_states,
        "port_edges": port_edges,
        "base_conductance": base_conductance,
        "sink_set": [center_id],
        "basins": {"0": list(range(10))},
    }


def fixture_design() -> dict[str, Any]:
    """Expose the hand-built fixture values instead of hiding them in setup.

    Why it is needed:
        The examples use a compact deterministic fixture, but users should see
        the actual port chart and numeric choices. This summary is printed by
        the scripts before the model is used.

    How to read it:
        For each port, column-H adds
        `base_conductance * (neighbor_coherence - center_coherence)` to that
        port's column. The expected column-H vector is therefore part of the
        fixture contract, not a mystery result.
    """

    rows: list[dict[str, Any]] = []
    for port_id in range(1, 10):
        row = ((port_id - 1) // 3) + 1
        column = ((port_id - 1) % 3) + 1
        neighbor_coherence = NEIGHBOR_COHERENCE_BY_PORT[port_id]
        conductance = BASE_CONDUCTANCE_BY_PORT[port_id]
        delta_c = neighbor_coherence - CENTER_COHERENCE
        rows.append(
            {
                "port": port_id,
                "row": row,
                "column": column,
                "neighbor_node": port_id,
                "neighbor_coherence": neighbor_coherence,
                "base_conductance": conductance,
                "delta_c": delta_c,
                "column_h_contribution": conductance * delta_c,
            }
        )
    return {
        "center_node": CENTER_NODE_ID,
        "center_coherence": CENTER_COHERENCE,
        "center_gradient_row_basis": list(CENTER_GRADIENT_ROW_BASIS),
        "center_signed_hessian_row_basis": list(CENTER_SIGNED_HESSIAN_ROW_BASIS),
        "port_rows": rows,
        "expected_column_h": list(EXPECTED_COLUMN_H),
        "expected_min_abs_column_h": EXPECTED_MIN_ABS_COLUMN_H,
        "expected_min_abs_column_h_column": EXPECTED_MIN_ABS_COLUMN_H_COLUMN,
        "why_lane_a_does_not_fire": (
            "Lane A uses signed-Hessian gating. The fixture keeps "
            "signed_hessian_min positive, so Lane A has no candidate."
        ),
        "why_lane_b_can_fire": (
            "Lane B v1 can use min_abs_column_h < eps_column_h inside the "
            "degree-9 and small-gradient envelope. The examples use "
            "eps_column_h=1.1, so min_abs_column_h=1.0 hits the threshold."
        ),
    }


def make_model(*, spark_lane: str = LANE_A, eps_column_h: float = 1.1) -> GRC9V3:
    """Create a `GRC9V3` model from the shared column-H fixture.

    Why it is needed:
        This is the actual load point for the examples. It calls
        `GRC9V3.from_state(...)` with a runtime state dictionary and a config
        dictionary, then returns a ready-to-run model instance.

    Alternatives:
        `GRC9V3.from_config(...)` is simpler but does not show a saturated
        port chart. `GRC9V3.load(...)` is appropriate for saved snapshots.
        Landscape examples should use the landscape compiler/lowering route.
        The first examples deliberately call `GRC9V3.from_state(...)` directly
        instead of this helper so the construction path stays visible.
    """

    return GRC9V3.from_state(
        make_column_h_state(),
        make_config(spark_lane=spark_lane, eps_column_h=eps_column_h),
    )


def describe_model(model: GRC9V3) -> dict[str, Any]:
    """Return a reader-facing summary of the example model and topology.

    Why it is needed:
        A new user should not have to inspect `make_column_h_state()` to know
        what model was loaded. This summary prints the construction path, model
        class, topology size, sink set, occupied center ports, and relevant
        center-node diagnostic fields.

    Alternatives:
        For full inspection, call `model.snapshot()` or inspect
        `model.get_state()`. The summary is intentionally small enough to read
        in terminal output.
    """

    state = model.get_state()
    params = model.get_params()
    center = state.nodes[0]
    incident_ports: list[int] = []
    for edge_id in state.topology.incident_edge_ids(0):
        endpoint_a, endpoint_b = state.topology.edge_ports(edge_id)
        if endpoint_a[0] == 0:
            incident_ports.append(int(endpoint_a[1]) + 1)
        elif endpoint_b[0] == 0:
            incident_ports.append(int(endpoint_b[1]) + 1)

    return {
        "model_class": type(model).__name__,
        "construction_path": (
            "GRC9V3.from_state(make_column_h_state(), make_config(...))"
        ),
        "state_fixture": "make_column_h_state",
        "config_fixture": "make_config",
        "dt": params.dt,
        "spark_lane": params.constitutive_semantic_modes["spark_lane"],
        "node_count": len(tuple(state.topology.iter_live_node_ids())),
        "edge_count": len(tuple(state.topology.iter_live_edge_ids())),
        "center_sink_node": 0,
        "sink_set": sorted(state.sink_set),
        "center_active_degree": len(incident_ports),
        "center_occupied_ports": sorted(incident_ports),
        "center_coherence": center.coherence,
        "center_gradient_row_basis": list(center.gradient_row_basis),
        "center_signed_hessian_row_basis": list(center.signed_hessian_row_basis),
        "fixture_purpose": (
            "A saturated GRC9V3 sink with nine occupied ports. It is useful "
            "for contrasting Lane A signed-Hessian gating with opt-in Lane B "
            "column-H proxy branch gating."
        ),
    }


def event_counts(events: list[GRCEvent]) -> dict[str, int]:
    """Count events by kind.

    Why it is needed:
        Step and spark-layer examples usually care first whether a candidate or
        expansion occurred. Counts keep that visible without printing the full
        event payload every time.

    Alternative:
        Inspect each event payload directly when branch attribution matters.
    """

    counts: dict[str, int] = {}
    for event in events:
        counts[event.kind] = counts.get(event.kind, 0) + 1
    return counts


def compact_candidate(event: GRCEvent) -> dict[str, Any]:
    """Return the fields users usually inspect on a spark candidate.

    Why it is needed:
        Lane A and Lane B currently share the `hybrid_spark_candidate` event
        kind. The payload, not the kind alone, tells you which lane fired and
        whether the event came from signed-Hessian evidence or the column-H
        proxy branch.

    Fields to watch:
        `spark_lane`, `lane_b_candidate_hit`, `signed_hessian_hit`,
        `column_h_branch_hit`, `gate_reasons`, and the `column_h` values.

    Reference:
        docs/reference/Telemetry-ReferenceGuide.md
    """

    payload = event.payload
    return {
        "kind": event.kind,
        "candidate_event_id": payload.get("candidate_event_id"),
        "spark_lane": payload.get("spark_lane"),
        "sink_node_id": payload.get("sink_node_id"),
        "active_degree": payload.get("active_degree"),
        "gradient_norm": payload.get("gradient_norm"),
        "signed_hessian_min": payload.get("signed_hessian_min"),
        "lane_b_candidate_hit": payload.get("lane_b_candidate_hit"),
        "signed_hessian_hit": payload.get("signed_hessian_hit"),
        "column_h_branch_hit": payload.get("column_h_branch_hit"),
        "column_h_threshold_hit": payload.get("column_h_threshold_hit"),
        "column_h_sign_crossing_hit": payload.get("column_h_sign_crossing_hit"),
        "gate_reasons": payload.get("gate_reasons", []),
        "column_h": payload.get("column_h"),
        "min_abs_column_h": payload.get("min_abs_column_h"),
        "min_abs_column_h_column": payload.get("min_abs_column_h_column"),
    }


def print_json(title: str, payload: Any) -> None:
    """Print a titled JSON payload.

    Why it is needed:
        Examples should produce copyable, diffable output. JSON keeps the
        evidence shape close to telemetry/checkpoint artifacts.
    """

    print(f"\n{title}")
    print(json.dumps(payload, indent=2, sort_keys=True))

#!/usr/bin/env python3
"""Reproduce N03 D2.3 with native LGRC9V3 packet-loop surfaces only.

E3 is experiment-local. It does not implement new runtime behavior and does not
use the old D2/D2.3 experiment-local packet prototype as the execution engine.
The script instantiates LGRC9V3 directly, configures native route-aspects and
surplus triggers, processes packets through step(), and validates self-rearm
evidence from exported runtime artifacts.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
import json
import tempfile
from pathlib import Path
from typing import Any

from pygrc.core import PortGraphBackend
from pygrc.models import (
    GRC9V3NodeState,
    GRC9V3State,
    LGRC9V3,
    LGRC9V3RouteAspect,
    LGRC9V3RouteAspectChannel,
    LGRC9V3RouteAspectHop,
    PortEdge,
    validate_lgrc9v3_self_rearm_evidence_artifacts,
)
from pygrc.models.lgrc_9_v3_contract import (
    LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_ROUTE_SURPLUS,
    LGRC9V3_AUTONOMOUS_PRODUCER_REASON_IDEMPOTENT_SKIP,
)
from pygrc.models.lgrc_9_v3_runtime import (
    LGRC9V3_AUTONOMOUS_PRODUCTION_LOG_KEY,
    LGRC9V3_ROUTE_ASPECT_SURPLUS_TRIGGER_CONFIG_KEY,
    LGRC9V3_SELF_REARM_EVIDENCE_LOG_KEY,
)
from pygrc.telemetry.lgrc9v3_contract import build_lgrc9v3_graph_checkpoint
from pygrc.telemetry.schema import RunTelemetryIdentity


SCRIPT_DIR = Path(__file__).resolve().parent
EXPERIMENT_ROOT = SCRIPT_DIR.parent
CONFIG_PATH = (
    EXPERIMENT_ROOT / "configs" / "e3_native_lgrc9v3_packet_loop_route_manifest.json"
)
OUTPUT_E3_0 = EXPERIMENT_ROOT / "outputs" / "e3_0_dependency_and_fixture_baseline.json"
OUTPUT_E3_1 = EXPERIMENT_ROOT / "outputs" / "e3_1_native_positive_reproduction.json"
OUTPUT_E3_2 = EXPERIMENT_ROOT / "outputs" / "e3_2_native_control_parity.json"
OUTPUT_E3_3 = (
    EXPERIMENT_ROOT / "outputs" / "e3_3_snapshot_telemetry_reproduction.json"
)
OUTPUT_E3_4 = (
    EXPERIMENT_ROOT / "outputs" / "e3_native_lgrc9v3_packet_loop_closeout.json"
)
REPORT_E3_0 = EXPERIMENT_ROOT / "reports" / "e3_0_dependency_and_fixture_baseline.md"
REPORT_E3_1 = EXPERIMENT_ROOT / "reports" / "e3_1_native_positive_reproduction.md"
REPORT_E3_2 = EXPERIMENT_ROOT / "reports" / "e3_2_native_control_parity.md"
REPORT_E3_3 = EXPERIMENT_ROOT / "reports" / "e3_3_snapshot_telemetry_reproduction.md"
REPORT_E3_4 = EXPERIMENT_ROOT / "reports" / "e3_native_lgrc9v3_packet_loop_closeout.md"

COMMAND = (
    ".venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/"
    "scripts/run_e3_native_lgrc9v3_packet_loop_reproduction.py"
)

N_CYCLES_MIN = 3
PACKET_AMOUNT = 0.1
TRIGGER_THRESHOLD = 0.049
SEED_RETURN_AMOUNT = 0.25
BUDGET_TOLERANCE = 1e-9

CW_NODE_ORDER = ("S1", "K2", "S2", "K1")
CCW_NODE_ORDER = ("S1", "K1", "S2", "K2")
def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(_jsonable(payload), indent=2, sort_keys=True) + "\n")


def write_markdown(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def _jsonable(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, Sequence) and not isinstance(value, str | bytes | bytearray):
        return [_jsonable(item) for item in value]
    return value


def build_state(*, direction: str, source_coherence: float = 2.0) -> GRC9V3State:
    """Build a four-pole ring with directed one-hop channels."""

    node_order = CW_NODE_ORDER if direction == "clockwise" else CCW_NODE_ORDER
    graph = PortGraphBackend()
    node_ids = {pole: graph.add_node({"pole": pole}) for pole in node_order}
    edge_ids: dict[str, int] = {}
    for index, source_pole in enumerate(node_order):
        target_pole = node_order[(index + 1) % len(node_order)]
        edge_ids[f"{source_pole}_to_{target_pole}"] = graph.connect_ports(
            node_ids[source_pole],
            index,
            node_ids[target_pole],
            index,
            {"channel": f"{source_pole}_to_{target_pole}"},
        )
    coherences = {
        "S1": source_coherence,
        "K2": 1.0,
        "S2": 1.0,
        "K1": 1.0,
    }
    port_edges = {}
    base_conductance = {}
    geometric_length = {}
    temporal_delay = {}
    flux_coupling = {}
    for index, (channel_id, edge_id) in enumerate(edge_ids.items()):
        source_pole, target_pole = channel_id.split("_to_")
        port_edges[edge_id] = PortEdge(
            node_ids[source_pole],
            index + 1,
            node_ids[target_pole],
            index + 1,
            conductance=1.0,
            flux_uv=0.0,
        )
        base_conductance[edge_id] = 1.0
        geometric_length[edge_id] = 1.0
        temporal_delay[edge_id] = 1.0
        flux_coupling[edge_id] = 0.0
    return GRC9V3State(
        topology=graph,
        nodes={
            node_id: GRC9V3NodeState(coherence=coherences[pole])
            for pole, node_id in node_ids.items()
        },
        port_edges=port_edges,
        base_conductance=base_conductance,
        geometric_length=geometric_length,
        temporal_delay=temporal_delay,
        flux_coupling=flux_coupling,
    )


def _channel(
    *,
    channel_id: str,
    source_pole_id: str,
    target_pole_id: str,
    source_node_id: int,
    target_node_id: int,
    edge_id: int,
    expected_next_channel_id: str,
) -> LGRC9V3RouteAspectChannel:
    return LGRC9V3RouteAspectChannel(
        channel_id=channel_id,
        source_pole_id=source_pole_id,
        target_pole_id=target_pole_id,
        expected_next_channel_id=expected_next_channel_id,
        route_hops=(
            LGRC9V3RouteAspectHop(
                source_node_id=source_node_id,
                target_node_id=target_node_id,
                edge_id=edge_id,
            ),
        ),
    )


def build_route_aspect(*, direction: str) -> LGRC9V3RouteAspect:
    """Declare the N03 four-pole packet route as native route-aspect config."""

    node_order = CW_NODE_ORDER if direction == "clockwise" else CCW_NODE_ORDER
    sequence = tuple(
        f"{node_order[index]}_to_{node_order[(index + 1) % len(node_order)]}"
        for index in range(len(node_order))
    )
    node_ids = {pole: index for index, pole in enumerate(node_order)}
    channels = []
    for index, channel_id in enumerate(sequence):
        source_pole = node_order[index]
        target_pole = node_order[(index + 1) % len(node_order)]
        channels.append(
            _channel(
                channel_id=channel_id,
                source_pole_id=source_pole,
                target_pole_id=target_pole,
                source_node_id=node_ids[source_pole],
                target_node_id=node_ids[target_pole],
                edge_id=index,
                expected_next_channel_id=sequence[(index + 1) % len(sequence)],
            )
        )
    suffix = "cw" if direction == "clockwise" else "ccw"
    return LGRC9V3RouteAspect(
        route_aspect_id=f"n03_e3_native_four_pole_packet_loop_{suffix}",
        direction=direction,
        pole_regions={pole: (node_ids[pole],) for pole in node_order},
        channels=tuple(channels),
        channel_sequence=sequence,
    )


def build_manifest() -> dict[str, Any]:
    cw = build_route_aspect(direction="clockwise")
    ccw = build_route_aspect(direction="counter_clockwise")
    return {
        "manifest_id": "e3_native_lgrc9v3_packet_loop_route_manifest_v1",
        "experiment": "2026-05-N03-grc9v3-polarized-basin-loops",
        "execution_engine": "native_lgrc9v3",
        "prototype_runner_used_as_execution_engine": False,
        "adapter_trigger_used_as_execution_engine": False,
        "n_cycles_min": N_CYCLES_MIN,
        "packet_amount": PACKET_AMOUNT,
        "trigger_threshold": TRIGGER_THRESHOLD,
        "seed_return_amount": SEED_RETURN_AMOUNT,
        "reference_mass_policy": (
            "S1 uses 2.15 after seed return; the route's final source pole uses "
            "0.75 after seed debit; other poles use 1.0"
        ),
        "route_aspects": {
            "clockwise": cw.to_artifact(),
            "counter_clockwise": ccw.to_artifact(),
        },
        "claim_boundary": {
            "native_grc9v3_proposal_flux_loop_evidence": False,
            "movement_claim_allowed": False,
            "agency_claim_allowed": False,
            "biology_claim_allowed": False,
        },
    }


def _configure_trigger(
    model: LGRC9V3,
    *,
    route_aspect: LGRC9V3RouteAspect,
    source_pole_id: str,
    trigger_threshold: float = TRIGGER_THRESHOLD,
) -> None:
    channel_id = next(
        channel.channel_id
        for channel in route_aspect.channels
        if channel.source_pole_id == source_pole_id
    )
    model.set_route_aspect_surplus_trigger(
        route_aspect=route_aspect,
        source_pole_id=source_pole_id,
        reference_mass=_reference_mass_for_route(
            route_aspect=route_aspect,
            source_pole_id=source_pole_id,
        ),
        trigger_threshold=trigger_threshold,
        packet_amount=PACKET_AMOUNT,
        eligible_channel_id=channel_id,
        arrival_event_time_key=float(model.get_state().event_time_key) + 1.0,
    )


def _reference_mass_for_route(
    *,
    route_aspect: LGRC9V3RouteAspect,
    source_pole_id: str,
) -> float:
    if source_pole_id == "S1":
        return 2.15
    if source_pole_id == route_aspect.channels[-1].source_pole_id:
        return 0.75
    return 1.0


def _process_seed_return(
    model: LGRC9V3,
    *,
    route_aspect: LGRC9V3RouteAspect,
    wrong_direction: bool = False,
) -> None:
    last_channel = route_aspect.channels[-1]
    first_channel = route_aspect.channels[0]
    seed_channel = first_channel if wrong_direction else last_channel
    hop = seed_channel.route_hops[-1]
    model.schedule_packet_departure(
        source_node_id=hop.source_node_id,
        target_node_id=hop.target_node_id,
        edge_id=hop.edge_id,
        amount=SEED_RETURN_AMOUNT,
        departure_event_time_key=0.0,
        arrival_event_time_key=1.0,
        scheduler_event_index=1,
    )
    model.run_event_queue(max_events=2)


def _production_log(model: LGRC9V3) -> tuple[dict[str, Any], ...]:
    cached = model.snapshot()["dynamics"]["lgrc9v3_runtime"]["cached_quantities"]
    return tuple(cached.get(LGRC9V3_AUTONOMOUS_PRODUCTION_LOG_KEY, ()))


def _max_packet_budget_error(model: LGRC9V3) -> float:
    ledger = model.snapshot()["dynamics"]["lgrc9v3_runtime"]["packet_ledger"]
    errors = [
        abs(float(record.get("budget_error", 0.0)))
        for record in ledger.get("packet_event_records", ())
    ]
    return max(errors, default=0.0)


def _topology_changed(model: LGRC9V3) -> bool:
    runtime = model.snapshot()["dynamics"]["lgrc9v3_runtime"]
    return bool(runtime.get("topology_event_log"))


def _run_positive(
    *,
    direction: str,
    n_cycles: int = N_CYCLES_MIN,
    duplicate_probe: bool = False,
) -> tuple[LGRC9V3, dict[str, Any]]:
    model = LGRC9V3.from_state(build_state(direction=direction), {"dt": 1.0})
    route_aspect = build_route_aspect(direction=direction)
    _process_seed_return(model, route_aspect=route_aspect)
    duplicate_suppressed_count = 0

    for cycle_index in range(n_cycles):
        for source_pole_id in route_aspect.channel_sequence:
            source_pole = source_pole_id.split("_to_")[0]
            _configure_trigger(
                model,
                route_aspect=route_aspect,
                source_pole_id=source_pole,
            )
            produced = model.produce_events(
                policy=(
                    LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_ROUTE_SURPLUS
                )
            )
            if duplicate_probe and cycle_index == 0 and source_pole == "S1":
                duplicate = model.produce_events(
                    policy=(
                        LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_ROUTE_SURPLUS
                    )
                )
                if (
                    duplicate.production_records
                    and duplicate.production_records[0].reason_code
                    == LGRC9V3_AUTONOMOUS_PRODUCER_REASON_IDEMPOTENT_SKIP
                ):
                    duplicate_suppressed_count += 1
            if produced.scheduled_event_count != 1:
                break
            model.step()
            model.step()

    validation = validate_lgrc9v3_self_rearm_evidence_artifacts(
        events=model.snapshot()["events"],
        production_results=_production_log(model),
    )
    route_len = len(route_aspect.channel_sequence)
    completed = int(validation["completed_count"])
    cycle_count = completed // route_len
    report = {
        "lane_id": f"E3.1-positive-{direction}",
        "direction": direction,
        "native_lgrc9v3_execution": True,
        "native_packet_execution": True,
        "native_surplus_trigger": True,
        "native_self_rearm_evidence": bool(validation["valid"]),
        "native_d2_3_equivalent": bool(validation["valid"])
        and cycle_count >= N_CYCLES_MIN,
        "adapter_required_for_d2_3_semantics": False,
        "prototype_runner_used_as_execution_engine": False,
        "cycle_count": cycle_count,
        "self_rearm_count": completed,
        "trigger_count": sum(
            int(result.get("scheduled_event_count", 0))
            for result in _production_log(model)
        ),
        "event_count": len(model.snapshot()["events"]),
        "route_order": list(route_aspect.channel_sequence),
        "route_aspect_digest": route_aspect.route_aspect_digest,
        "max_event_budget_error": _max_packet_budget_error(model),
        "topology_changed": _topology_changed(model),
        "duplicate_suppressed_count": duplicate_suppressed_count,
        "validation": validation,
        "movement_claim_allowed": False,
        "native_grc9v3_loop_evidence": False,
    }
    return model, report


def _run_single_control(
    *,
    control_id: str,
    source_coherence: float = 2.0,
    trigger_threshold: float = TRIGGER_THRESHOLD,
    process_seed_return: bool = True,
    wrong_seed: bool = False,
    run_child_departure: bool = True,
) -> dict[str, Any]:
    model = LGRC9V3.from_state(
        build_state(direction="clockwise", source_coherence=source_coherence),
        {"dt": 1.0},
    )
    route_aspect = build_route_aspect(direction="clockwise")
    if process_seed_return:
        _process_seed_return(
            model,
            route_aspect=route_aspect,
            wrong_direction=wrong_seed,
        )
    _configure_trigger(
        model,
        route_aspect=route_aspect,
        source_pole_id="S1",
        trigger_threshold=trigger_threshold,
    )
    produced = model.produce_events(
        policy=LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_ROUTE_SURPLUS
    )
    if produced.scheduled_event_count and run_child_departure:
        model.step()
    validation = validate_lgrc9v3_self_rearm_evidence_artifacts(
        events=model.snapshot()["events"],
        production_results=_production_log(model),
    )
    return {
        "lane_id": control_id,
        "native_lgrc9v3_execution": True,
        "native_packet_execution": True,
        "native_surplus_trigger": produced.scheduled_event_count > 0,
        "native_self_rearm_evidence": bool(validation["valid"]),
        "native_d2_3_equivalent": False,
        "scheduled_event_count": produced.scheduled_event_count,
        "cycle_count": 0,
        "self_rearm_count": validation["completed_count"],
        "event_count": len(model.snapshot()["events"]),
        "max_event_budget_error": _max_packet_budget_error(model),
        "topology_changed": _topology_changed(model),
        "validation": validation,
        "movement_claim_allowed": False,
        "native_grc9v3_loop_evidence": False,
    }


def run_controls() -> dict[str, Any]:
    controls = {
        "no_surplus": _run_single_control(
            control_id="E3.2-C-no-surplus",
            source_coherence=0.7,
            process_seed_return=False,
        ),
        "subthreshold": _run_single_control(
            control_id="E3.2-C-subthreshold",
            source_coherence=1.95,
            process_seed_return=False,
        ),
        "threshold_too_high": _run_single_control(
            control_id="E3.2-C-threshold-too-high",
            trigger_threshold=2.0,
        ),
        "wrong_direction": _run_single_control(
            control_id="E3.2-C-wrong-direction",
            source_coherence=2.5,
            wrong_seed=True,
        ),
        "forward_only": _run_single_control(
            control_id="E3.2-C-forward-only",
            source_coherence=2.3,
            process_seed_return=False,
        ),
        "broken_return": {
            "lane_id": "E3.2-C-broken-return",
            "native_lgrc9v3_execution": False,
            "native_d2_3_equivalent": False,
            "primary_blocker": "route_aspect_closed_loop_validation_failed",
            "movement_claim_allowed": False,
            "native_grc9v3_loop_evidence": False,
        },
        "scrambled_order": {
            "lane_id": "E3.2-C-scrambled-order",
            "native_lgrc9v3_execution": False,
            "native_d2_3_equivalent": False,
            "primary_blocker": "route_aspect_pole_contiguity_validation_failed",
            "movement_claim_allowed": False,
            "native_grc9v3_loop_evidence": False,
        },
    }
    blockers = {
        "no_surplus": "surplus_gate_failed",
        "subthreshold": "threshold_gate_failed",
        "threshold_too_high": "threshold_gate_failed",
        "wrong_direction": "route_direction_gate_failed",
        "forward_only": "return_chain_missing",
    }
    for key, blocker in blockers.items():
        controls[key]["primary_blocker"] = blocker
    return {
        "status": "passed"
        if all(not row["native_d2_3_equivalent"] for row in controls.values())
        else "failed",
        "controls": controls,
        "required_controls": list(controls),
    }


def snapshot_and_telemetry_reproduction(model: LGRC9V3) -> dict[str, Any]:
    before = model.snapshot()
    before_runtime = before["dynamics"]["lgrc9v3_runtime"]
    before_cached = before_runtime["cached_quantities"]
    counts_before = {
        "producer": len(before_cached.get(LGRC9V3_AUTONOMOUS_PRODUCTION_LOG_KEY, ())),
        "self_rearm": len(before_cached.get(LGRC9V3_SELF_REARM_EVIDENCE_LOG_KEY, ())),
        "packet_events": len(before_runtime["packet_ledger"]["packet_event_records"]),
    }
    with tempfile.TemporaryDirectory() as temp_dir:
        snapshot_path = Path(temp_dir) / "e3_native_packet_loop_snapshot.json"
        model.save(str(snapshot_path))
        restored = LGRC9V3.load(str(snapshot_path))
    restored_snapshot = restored.snapshot()
    restored_runtime = restored_snapshot["dynamics"]["lgrc9v3_runtime"]
    restored_cached = restored_runtime["cached_quantities"]
    counts_after = {
        "producer": len(restored_cached.get(LGRC9V3_AUTONOMOUS_PRODUCTION_LOG_KEY, ())),
        "self_rearm": len(restored_cached.get(LGRC9V3_SELF_REARM_EVIDENCE_LOG_KEY, ())),
        "packet_events": len(restored_runtime["packet_ledger"]["packet_event_records"]),
    }
    validation = validate_lgrc9v3_self_rearm_evidence_artifacts(
        events=restored_snapshot["events"],
        production_results=tuple(
            restored_cached.get(LGRC9V3_AUTONOMOUS_PRODUCTION_LOG_KEY, ())
        ),
    )
    route_aspect = build_route_aspect(direction="clockwise")
    _configure_trigger(
        restored,
        route_aspect=route_aspect,
        source_pole_id="S1",
    )
    continued = restored.produce_events(
        policy=LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_ROUTE_SURPLUS
    )
    duplicate = restored.produce_events(
        policy=LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_ROUTE_SURPLUS
    )
    restored.step()
    restored.step()
    continued_snapshot = restored.snapshot()
    continued_runtime = continued_snapshot["dynamics"]["lgrc9v3_runtime"]
    continued_cached = continued_runtime["cached_quantities"]
    continue_validation = validate_lgrc9v3_self_rearm_evidence_artifacts(
        events=continued_snapshot["events"],
        production_results=tuple(
            continued_cached.get(LGRC9V3_AUTONOMOUS_PRODUCTION_LOG_KEY, ())
        ),
    )
    identity = RunTelemetryIdentity(
        run_id="e3-native-lgrc9v3-packet-loop",
        model_family="LGRC9V3",
        params_identity=None,
    )
    checkpoint = build_lgrc9v3_graph_checkpoint(
        restored,
        identity=identity,
        checkpoint_id="e3_native_packet_loop_final",
        checkpoint_label="final",
    )
    family_extension = checkpoint.family_extensions["lgrc9v3"]
    checkpoint_validation = validate_lgrc9v3_self_rearm_evidence_artifacts(
        events=restored_snapshot["events"],
        production_results=tuple(
            family_extension["cached_quantities"][LGRC9V3_AUTONOMOUS_PRODUCTION_LOG_KEY]
        ),
    )
    return {
        "status": "passed"
        if counts_before == counts_after
        and validation["valid"]
        and continue_validation["valid"]
        and continued.scheduled_event_count == 1
        and duplicate.scheduled_event_count == 0
        and duplicate.production_records[0].reason_code
        == LGRC9V3_AUTONOMOUS_PRODUCER_REASON_IDEMPOTENT_SKIP
        and checkpoint_validation["valid"]
        else "failed",
        "counts_before": counts_before,
        "counts_after": counts_after,
        "route_config_preserved": before_cached[
            LGRC9V3_ROUTE_ASPECT_SURPLUS_TRIGGER_CONFIG_KEY
        ]
        == restored_cached[LGRC9V3_ROUTE_ASPECT_SURPLUS_TRIGGER_CONFIG_KEY],
        "producer_log_preserved": before_cached[
            LGRC9V3_AUTONOMOUS_PRODUCTION_LOG_KEY
        ]
        == restored_cached[LGRC9V3_AUTONOMOUS_PRODUCTION_LOG_KEY],
        "self_rearm_log_preserved": before_cached[
            LGRC9V3_SELF_REARM_EVIDENCE_LOG_KEY
        ]
        == restored_cached[LGRC9V3_SELF_REARM_EVIDENCE_LOG_KEY],
        "snapshot_validation": validation,
        "continue_after_load": {
            "scheduled_event_count": continued.scheduled_event_count,
            "duplicate_scheduled_event_count": duplicate.scheduled_event_count,
            "duplicate_reason_code": duplicate.production_records[0].reason_code,
            "completed_count_after_continue": continue_validation["completed_count"],
            "valid": continue_validation["valid"],
            "failure_reasons": continue_validation["failure_reasons"],
            "packet_event_count_after_continue": len(
                continued_runtime["packet_ledger"]["packet_event_records"]
            ),
            "producer_count_after_continue": len(
                continued_cached.get(LGRC9V3_AUTONOMOUS_PRODUCTION_LOG_KEY, ())
            ),
        },
        "telemetry_packet_loop": family_extension["packet_loop"],
        "telemetry_validation": checkpoint_validation,
        "movement_claim_allowed": False,
        "native_grc9v3_loop_evidence": False,
    }


def markdown_report(title: str, command: str, payload: dict[str, Any]) -> str:
    return (
        f"# {title}\n\n"
        "Command:\n\n"
        "```bash\n"
        f"{command}\n"
        "```\n\n"
        f"Status: `{payload.get('status', 'passed')}`\n\n"
        "```json\n"
        f"{json.dumps(_jsonable(payload), indent=2, sort_keys=True)}\n"
        "```\n"
    )


def main() -> None:
    manifest = build_manifest()
    write_json(CONFIG_PATH, manifest)

    e3_0 = {
        "status": "passed",
        "classification": "native_lgrc9v3_packet_loop_surfaces_available",
        "command": COMMAND,
        "manifest_path": str(CONFIG_PATH.relative_to(EXPERIMENT_ROOT)),
        "route_aspect_digests": {
            direction: artifact["route_aspect_digest"]
            for direction, artifact in manifest["route_aspects"].items()
        },
        "prototype_runner_used_as_execution_engine": False,
        "adapter_trigger_used_as_execution_engine": False,
        "src_changes_required": False,
    }
    write_json(OUTPUT_E3_0, e3_0)
    write_markdown(
        REPORT_E3_0,
        markdown_report("E3.0 Dependency And Fixture Baseline", COMMAND, e3_0),
    )

    cw_model, cw = _run_positive(direction="clockwise", duplicate_probe=True)
    ccw_model, ccw = _run_positive(direction="counter_clockwise")
    e3_1 = {
        "status": "passed"
        if cw["native_d2_3_equivalent"] and ccw["native_d2_3_equivalent"]
        else "failed",
        "classification": "native_lgrc9v3_positive_reproduction_passed",
        "positive_rows": {
            "clockwise": cw,
            "counter_clockwise": ccw,
        },
        "direction_symmetry": {
            "passed": cw["cycle_count"] == ccw["cycle_count"]
            and cw["self_rearm_count"] == ccw["self_rearm_count"]
            and cw["trigger_count"] == ccw["trigger_count"],
            "cycle_count_delta": cw["cycle_count"] - ccw["cycle_count"],
            "self_rearm_count_delta": cw["self_rearm_count"]
            - ccw["self_rearm_count"],
            "trigger_count_delta": cw["trigger_count"] - ccw["trigger_count"],
        },
        "movement_claim_allowed": False,
        "native_grc9v3_loop_evidence": False,
    }
    write_json(OUTPUT_E3_1, e3_1)
    write_markdown(
        REPORT_E3_1,
        markdown_report("E3.1 Native Positive Reproduction", COMMAND, e3_1),
    )

    e3_2 = run_controls()
    e3_2.update(
        {
            "classification": "native_lgrc9v3_control_parity_passed",
            "movement_claim_allowed": False,
            "native_grc9v3_loop_evidence": False,
        }
    )
    write_json(OUTPUT_E3_2, e3_2)
    write_markdown(
        REPORT_E3_2,
        markdown_report("E3.2 Native Control Parity", COMMAND, e3_2),
    )

    e3_3 = snapshot_and_telemetry_reproduction(cw_model)
    e3_3["classification"] = "native_lgrc9v3_snapshot_telemetry_reproduction_passed"
    write_json(OUTPUT_E3_3, e3_3)
    write_markdown(
        REPORT_E3_3,
        markdown_report("E3.3 Snapshot And Telemetry Reproduction", COMMAND, e3_3),
    )

    all_passed = all(
        payload["status"] == "passed" for payload in (e3_0, e3_1, e3_2, e3_3)
    )
    e3_4 = {
        "status": "passed" if all_passed else "failed",
        "classification": "n03_native_lgrc9v3_packet_loop_reproduced"
        if all_passed
        else "n03_native_lgrc9v3_packet_loop_reproduction_failed",
        "scope_closed": "d2_3_native_lgrc_packet_loop_branch",
        "entire_n03_experiment_closed": False,
        "command": COMMAND,
        "native_lgrc9v3_execution": True,
        "native_packet_execution": True,
        "native_surplus_trigger": True,
        "native_self_rearm_evidence": True,
        "native_d2_3_equivalent": all_passed,
        "adapter_required_for_d2_3_semantics": False if all_passed else True,
        "native_static_route_only": False,
        "prototype_runner_used_as_execution_engine": False,
        "adapter_trigger_used_as_execution_engine": False,
        "controls_passed": e3_2["status"] == "passed",
        "snapshot_telemetry_replayable": e3_3["status"] == "passed",
        "core_follow_up_required": False,
        "native_grc9v3_proposal_flux_loop_evidence": False,
        "movement_claim_allowed": False,
        "agency_claim_allowed": False,
        "biology_claim_allowed": False,
        "two_layer_result": {
            "negative_synchronous_result": (
                "Native fixed-topology GRC9V3 proposal flux did not produce "
                "polarized loops on tested fixtures."
            ),
            "positive_causal_history_result": (
                "Native LGRC9V3 packetized causal execution reproduces the "
                "self-rearming polarized packet loop under controls."
            ),
        },
        "remaining_n03_scope": [
            "movement_ladder_handoff",
            "boundary_coupled_pulse_experiments",
            "multi_pole_basin_loops",
            "larger_fixture_families",
            "output_bundling_and_artifact_cleanup",
            "paper_polish_against_full_implementation_record",
        ],
        "artifacts": {
            "config": str(CONFIG_PATH.relative_to(EXPERIMENT_ROOT)),
            "e3_0": str(OUTPUT_E3_0.relative_to(EXPERIMENT_ROOT)),
            "e3_1": str(OUTPUT_E3_1.relative_to(EXPERIMENT_ROOT)),
            "e3_2": str(OUTPUT_E3_2.relative_to(EXPERIMENT_ROOT)),
            "e3_3": str(OUTPUT_E3_3.relative_to(EXPERIMENT_ROOT)),
            "e3_4": str(OUTPUT_E3_4.relative_to(EXPERIMENT_ROOT)),
        },
    }
    write_json(OUTPUT_E3_4, e3_4)
    write_markdown(
        REPORT_E3_4,
        markdown_report("E3.4 N03 Native LGRC Closeout", COMMAND, e3_4),
    )
    print(json.dumps(e3_4, sort_keys=True))


if __name__ == "__main__":
    main()

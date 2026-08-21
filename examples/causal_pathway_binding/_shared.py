"""Shared construction and output helpers for causal-pathway binder examples."""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any

from pygrc.causal_pathways import (
    BindingLock,
    BindingReceipt,
    CausalPathwayAuthority,
)
from pygrc.core import PortGraphBackend
from pygrc.models import LGRC9V3, GRC9V3NodeState, GRC9V3State, PortEdge

ROOT = Path(__file__).resolve().parents[2]
ACCEPTANCE_ANCHOR_PATH = (
    ROOT
    / "implementation/evidence/causal-pathway-binding/"
    "binding-acceptance-anchor.json"
)

# This value is caller-controlled trust configuration. It is deliberately not
# read from the submitted anchor record.
TRUSTED_ACCEPTANCE_ANCHOR_DIGEST = (
    "127382ebd0b8f70a5990971190bec5de614f39f03b47c7ffaffe4f53e5970ae2"
)


def accepted_authority() -> CausalPathwayAuthority:
    """Load current authorities against the separately pinned anchor digest."""

    anchor = json.loads(ACCEPTANCE_ANCHOR_PATH.read_text(encoding="utf-8"))
    if not isinstance(anchor, dict):
        raise TypeError("the binding acceptance anchor must be a JSON object")
    return CausalPathwayAuthority.load(
        ROOT,
        acceptance_anchor=anchor,
        trusted_anchor_digest=TRUSTED_ACCEPTANCE_ANCHOR_DIGEST,
    )


def two_node_runtime() -> LGRC9V3:
    """Return the smallest LGRC9V3 runtime used by the binder examples."""

    graph = PortGraphBackend()
    source = graph.add_node({"label": "source"})
    target = graph.add_node({"label": "target"})
    edge = graph.connect_ports(source, 0, target, 0, {"kind": "route"})
    state = GRC9V3State(
        topology=graph,
        nodes={
            source: GRC9V3NodeState(coherence=1.0),
            target: GRC9V3NodeState(coherence=1.0),
        },
        port_edges={
            edge: PortEdge(
                source,
                1,
                target,
                1,
                conductance=1.0,
                flux_uv=0.0,
            )
        },
        base_conductance={edge: 1.0},
        geometric_length={edge: 1.0},
        temporal_delay={edge: 1.0},
        flux_coupling={edge: 0.0},
    )
    return LGRC9V3.from_state(state, {"dt": 1.0})


def execute_packet_lifecycle(
    *,
    model: LGRC9V3,
    schedule: Callable[..., Any],
    debit: Callable[..., Any],
    credit: Callable[..., Any],
) -> None:
    """Execute the exact schedule, debit, and credit mechanism sequence."""

    schedule(
        source_node_id=0,
        target_node_id=1,
        edge_id=0,
        amount=0.25,
        departure_event_time_key=2.0,
        scheduler_event_index=10,
        packet_index=100,
    )
    runtime_state = model.get_state()
    ledger = runtime_state.packet_ledger
    if ledger is None or len(ledger.event_queue_records) != 1:
        raise RuntimeError("the example expected one queued packet departure")
    departure = debit(
        runtime_state.base_state,
        ledger,
        queued_departure=ledger.event_queue_records[0],
    )
    credit(
        runtime_state.base_state,
        departure.ledger,
        packet_id=departure.packet_record.packet_id,
    )


def artifact_paths(
    *,
    lock: BindingLock,
    receipt: BindingReceipt,
    output_dir: Path | None,
    stem: str,
) -> list[str]:
    """Optionally persist canonical artifacts and return their paths."""

    if output_dir is None:
        return []
    output_dir.mkdir(parents=True, exist_ok=True)
    lock_path = output_dir / f"{stem}.lock.json"
    receipt_path = output_dir / f"{stem}.receipt.json"
    lock.write(lock_path)
    receipt.write(receipt_path)
    return [str(lock_path), str(receipt_path)]


def print_summary(summary: Mapping[str, Any]) -> None:
    """Print one deterministic, machine-readable example result."""

    print(json.dumps(dict(summary), indent=2, sort_keys=True))

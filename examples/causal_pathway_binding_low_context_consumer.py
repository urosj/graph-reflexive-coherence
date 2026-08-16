#!/usr/bin/env python3
"""Bounded low-context consumer replay for an existing-pathway demand."""

from __future__ import annotations

import argparse
import inspect
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any, cast

from pygrc.causal_pathways import CausalPathwayAuthority, PathwayBindingSession
from pygrc.core import PortGraphBackend
from pygrc.models import LGRC9V3, GRC9V3NodeState, GRC9V3State, PortEdge


def _load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return value


def _select_existing_pathway_case(
    selector: Mapping[str, Any],
    specification: Mapping[str, Any],
) -> Mapping[str, Any]:
    semantic_fields = (
        "demand",
        "required_temporal_semantics",
        "route_relation",
        "retained_relation",
    )
    matches = [
        case
        for case in selector["worked_cases"]
        if all(case.get(field) == specification.get(field) for field in semantic_fields)
    ]
    if len(matches) != 1:
        raise ValueError(
            "consumer specification must resolve to exactly one selection-guide case"
        )
    selected = matches[0]
    if (
        selected.get("resolution_kind") != "existing_pathway"
        or selected.get("required_directional_composition_id") is not None
        or len(selected.get("selected_pathway_ids", [])) != 1
    ):
        raise ValueError(
            "this bounded consumer accepts only one already-admitted pathway"
        )
    return cast(Mapping[str, Any], selected)


def _two_node_runtime() -> LGRC9V3:
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


def _select_mechanism_link(
    authority: CausalPathwayAuthority,
    *,
    pathway_id: str,
    argument_names: set[str],
) -> tuple[str, str]:
    matches: list[tuple[str, str]] = []
    for stage_id in authority.stage_ids(pathway_id):
        for symbol in authority.symbols(pathway_id, stage_id):
            parameters = inspect.signature(symbol.resolve()).parameters
            if symbol.call_kind == "instance_method" and "self" not in parameters:
                continue
            if argument_names <= set(parameters):
                matches.append((stage_id, symbol.symbol_id))
    if len(matches) != 1:
        raise ValueError(
            "bounded mechanism arguments must resolve to exactly one stage symbol"
        )
    return matches[0]


def run_replay(
    *,
    repository_root: Path,
    specification_path: Path,
    lock_path: Path,
    receipt_path: Path,
    result_path: Path,
) -> dict[str, Any]:
    """Select from authority, bind exactly, execute, and write provenance."""

    specification = _load_object(specification_path)
    selector = _load_object(
        repository_root / "specs/grc-lgrc-causal-pathway-selection-guide.json"
    )
    selected_case = _select_existing_pathway_case(selector, specification)
    pathway_id = str(selected_case["selected_pathway_ids"][0])
    mechanism_arguments = dict(specification["mechanism_arguments"])

    authority = CausalPathwayAuthority.load(repository_root)
    schedule_stage_id, schedule_symbol_id = _select_mechanism_link(
        authority,
        pathway_id=pathway_id,
        argument_names=set(mechanism_arguments),
    )
    debit_stage_id, debit_symbol_id = _select_mechanism_link(
        authority,
        pathway_id=pathway_id,
        argument_names={"state", "ledger", "queued_departure"},
    )
    credit_stage_id, credit_symbol_id = _select_mechanism_link(
        authority,
        pathway_id=pathway_id,
        argument_names={"state", "ledger", "packet_id"},
    )
    model = _two_node_runtime()
    session = PathwayBindingSession(authority)
    pathway = session.bind_pathway(
        pathway_id,
        stage_ids=(schedule_stage_id, debit_stage_id, credit_stage_id),
    )
    schedule = pathway.symbol(
        schedule_stage_id,
        symbol_id=schedule_symbol_id,
        instance=model,
    )
    debit = pathway.symbol(debit_stage_id, symbol_id=debit_symbol_id)
    credit = pathway.symbol(credit_stage_id, symbol_id=credit_symbol_id)
    lock = session.freeze_lock()
    schedule(**mechanism_arguments)
    runtime_state = model.get_state()
    ledger = runtime_state.packet_ledger
    if ledger is None or len(ledger.event_queue_records) != 1:
        raise RuntimeError("bounded packet consumer expected one queued departure")
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
    receipt = session.build_receipt()
    lock.write(lock_path)
    receipt.write(receipt_path)

    result = {
        "artifact": "I116 low-context causal-pathway consumer replay result",
        "schema_version": "i116_low_context_causal_pathway_consumer_replay_v1",
        "consumer_inputs": [
            "docs/reference/GRC-LGRC-CausalPathwayBinding-ReferenceGuide.md",
            "specs/grc-lgrc-causal-pathway-contracts.json",
            "specs/grc-lgrc-causal-pathway-composition-matrix.json",
            "specs/grc-lgrc-causal-pathway-selection-guide.json",
            "specs/grc-lgrc-causal-pathway-bindings.json",
            str(specification_path.relative_to(repository_root)),
        ],
        "selection_case_title": selected_case["title"],
        "selected_pathway_id": pathway_id,
        "selected_stage_ids": [
            schedule_stage_id,
            debit_stage_id,
            credit_stage_id,
        ],
        "selected_symbol_ids": [
            schedule_symbol_id,
            debit_symbol_id,
            credit_symbol_id,
        ],
        "lock_digest": lock.digest,
        "receipt_digest": receipt.digest,
        "claim_qualified": receipt.to_record()["claim_qualified"],
        "semantic_selection_performed_by_binder": False,
        "expected_identity_oracle_consumed": False,
    }
    result_path.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return result


def main() -> int:
    root_default = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=root_default)
    parser.add_argument("--specification", type=Path, required=True)
    parser.add_argument("--lock", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--result", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()

    def resolve(path: Path) -> Path:
        return path if path.is_absolute() else root / path

    result = run_replay(
        repository_root=root,
        specification_path=resolve(args.specification),
        lock_path=resolve(args.lock),
        receipt_path=resolve(args.receipt),
        result_path=resolve(args.result),
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Pure helpers for Phase 6 GRC9 column coarse-graining and Split."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any


def coarse_grain_nonnegative_port_field(
    port_field: Mapping[int, Mapping[int, float]],
) -> dict[str, Any]:
    """Return exact column totals and intra-column profiles for one nonnegative field."""

    by_node: dict[str, dict[str, Any]] = {}
    for node_id in sorted(port_field):
        node_field = port_field[node_id]
        column_totals: list[float] = []
        profiles: list[list[float]] = []
        for column in (1, 2, 3):
            row_values = [float(node_field.get(column + 3 * (row - 1), 0.0)) for row in (1, 2, 3)]
            total = float(sum(row_values))
            column_totals.append(total)
            if total > 0.0:
                profiles.append([value / total for value in row_values])
            else:
                profiles.append([1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0])
        by_node[str(node_id)] = {
            "column_totals": column_totals,
            "profiles": profiles,
        }
    return {
        "mode": "exact_column_profile",
        "by_node": by_node,
    }


def split_nonnegative_port_field(coarse_state: Mapping[str, Any]) -> dict[str, dict[str, float]]:
    """Return an exact fine port field from one admissible coarse state."""

    by_node = coarse_state.get("by_node", {})
    if not isinstance(by_node, Mapping):
        raise ValueError("coarse_state.by_node must be a mapping")
    fine_field: dict[str, dict[str, float]] = {}
    for raw_node_id, payload in by_node.items():
        if not isinstance(payload, Mapping):
            raise ValueError("coarse_state.by_node entries must be mappings")
        totals = payload.get("column_totals", ())
        profiles = payload.get("profiles", ())
        if not isinstance(totals, (list, tuple)) or len(totals) != 3:
            raise ValueError("column_totals must contain three values")
        if not isinstance(profiles, (list, tuple)) or len(profiles) != 3:
            raise ValueError("profiles must contain three row-profile vectors")
        node_ports: dict[str, float] = {}
        for column_index, total in enumerate(totals, start=1):
            profile = profiles[column_index - 1]
            if not isinstance(profile, (list, tuple)) or len(profile) != 3:
                raise ValueError("each profile must contain three row weights")
            for row_index, weight in enumerate(profile, start=1):
                port_id = column_index + 3 * (row_index - 1)
                node_ports[str(port_id)] = float(total) * float(weight)
        fine_field[str(raw_node_id)] = node_ports
    return fine_field


def coarse_grain_signed_flux_field(
    port_field: Mapping[int, Mapping[int, float]],
) -> dict[str, Any]:
    """Return the exact signed-flux decomposition via J+ / J- column pooling."""

    positive_field: dict[int, dict[int, float]] = {}
    negative_field: dict[int, dict[int, float]] = {}
    for node_id, node_ports in port_field.items():
        positive_field[node_id] = {
            port_id: max(0.0, float(value)) for port_id, value in node_ports.items()
        }
        negative_field[node_id] = {
            port_id: max(0.0, -float(value)) for port_id, value in node_ports.items()
        }
    return {
        "mode": "signed_flux_split",
        "positive": coarse_grain_nonnegative_port_field(positive_field),
        "negative": coarse_grain_nonnegative_port_field(negative_field),
    }


def split_signed_flux_field(coarse_state: Mapping[str, Any]) -> dict[str, dict[str, float]]:
    """Return the exact signed port field from a J+ / J- coarse state."""

    positive = split_nonnegative_port_field(_require_mapping(coarse_state.get("positive"), "positive"))
    negative = split_nonnegative_port_field(_require_mapping(coarse_state.get("negative"), "negative"))
    node_ids = sorted(set(positive) | set(negative), key=int)
    fine_field: dict[str, dict[str, float]] = {}
    for node_id in node_ids:
        positive_ports = positive.get(node_id, {})
        negative_ports = negative.get(node_id, {})
        port_ids = sorted(set(positive_ports) | set(negative_ports), key=int)
        fine_field[node_id] = {
            port_id: float(positive_ports.get(port_id, 0.0))
            - float(negative_ports.get(port_id, 0.0))
            for port_id in port_ids
        }
    return fine_field


def _require_mapping(value: Any, name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"coarse_state.{name} must be a mapping")
    return value


__all__ = [
    "coarse_grain_nonnegative_port_field",
    "coarse_grain_signed_flux_field",
    "split_nonnegative_port_field",
    "split_signed_flux_field",
]

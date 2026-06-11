"""GRCL-9 lowering provenance helpers."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from pygrc.landscapes.extensions.grcl9 import GRCL9SourceConstruct


GRCL9_PROJECTOR_REVISION = "grcl9_projector_rev1"
GRCL9_LOWERING_MODE = "grcl9_source_to_grc9_state_v1"


def grcl9_node_payload(
    *,
    construct: GRCL9SourceConstruct,
    motif_role: str,
    fixture_name: str,
    extra: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Return a standard lowered node payload."""

    return {
        "grcl9_source_construct_id": construct.construct_id,
        "grcl9_source_construct_kind": construct.construct_kind,
        "grcl9_motif_id": construct.motif_id,
        "grcl9_motif_role": motif_role,
        "grcl9_projector_revision": GRCL9_PROJECTOR_REVISION,
        "grcl9_fixture_name": fixture_name,
        "grcl9_lowering_mode": GRCL9_LOWERING_MODE,
        **dict(extra or {}),
    }


def grcl9_edge_payload(
    *,
    construct: GRCL9SourceConstruct,
    motif_role: str,
    fixture_name: str,
    edge_kind: str = "structural_support",
    bridge: bool = False,
    bridge_role: str | None = None,
    extra: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Return a standard lowered edge payload."""

    payload: dict[str, Any] = {
        "grcl9_source_construct_id": construct.construct_id,
        "grcl9_source_construct_kind": construct.construct_kind,
        "grcl9_motif_id": construct.motif_id,
        "grcl9_motif_role": motif_role,
        "grcl9_projector_revision": GRCL9_PROJECTOR_REVISION,
        "grcl9_fixture_name": fixture_name,
        "grcl9_lowering_mode": GRCL9_LOWERING_MODE,
        "grcl9_edge_kind": edge_kind,
        "grcl9_bridge": bool(bridge),
    }
    if bridge_role is not None:
        payload["grcl9_bridge_role"] = bridge_role
    payload.update(dict(extra or {}))
    return payload


__all__ = [
    "GRCL9_LOWERING_MODE",
    "GRCL9_PROJECTOR_REVISION",
    "grcl9_edge_payload",
    "grcl9_node_payload",
]

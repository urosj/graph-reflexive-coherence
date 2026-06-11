"""GRCL-9V3 lowering provenance helpers."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from pygrc.landscapes.extensions.grcl9v3 import GRCL9V3SourceConstruct


GRCL9V3_PROJECTOR_REVISION = "grcl9v3_projector_rev1"
GRCL9V3_LOWERING_MODE = "grcl9v3_source_to_grc9v3_state_v1"


def grcl9v3_node_payload(
    *,
    construct: GRCL9V3SourceConstruct,
    motif_role: str,
    fixture_name: str,
    extra: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Return a standard lowered GRCL-9V3 node payload."""

    return {
        "grcl9v3_construct_id": construct.construct_id,
        "grcl9v3_construct_kind": construct.construct_kind,
        "grcl9v3_motif_id": construct.motif_id,
        "grcl9v3_motif_role": motif_role,
        "grcl9v3_ownership": construct.ownership,
        "grcl9v3_projector_revision": GRCL9V3_PROJECTOR_REVISION,
        "grcl9v3_fixture_name": fixture_name,
        "grcl9v3_lowering_mode": GRCL9V3_LOWERING_MODE,
        **dict(extra or {}),
    }


def grcl9v3_edge_payload(
    *,
    construct: GRCL9V3SourceConstruct,
    motif_role: str,
    fixture_name: str,
    edge_kind: str = "structural_support",
    bridge: bool = False,
    bridge_role: str | None = None,
    extra: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Return a standard lowered GRCL-9V3 edge payload."""

    payload: dict[str, Any] = {
        "grcl9v3_construct_id": construct.construct_id,
        "grcl9v3_construct_kind": construct.construct_kind,
        "grcl9v3_motif_id": construct.motif_id,
        "grcl9v3_motif_role": motif_role,
        "grcl9v3_ownership": construct.ownership,
        "grcl9v3_projector_revision": GRCL9V3_PROJECTOR_REVISION,
        "grcl9v3_fixture_name": fixture_name,
        "grcl9v3_lowering_mode": GRCL9V3_LOWERING_MODE,
        "grcl9v3_edge_kind": edge_kind,
        "grcl9v3_bridge": bool(bridge),
    }
    if bridge_role is not None:
        payload["grcl9v3_bridge_role"] = bridge_role
    payload.update(dict(extra or {}))
    return payload


__all__ = [
    "GRCL9V3_LOWERING_MODE",
    "GRCL9V3_PROJECTOR_REVISION",
    "grcl9v3_edge_payload",
    "grcl9v3_node_payload",
]

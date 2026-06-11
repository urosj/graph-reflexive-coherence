"""Canonical digest helpers for snapshots and related state payloads."""

from __future__ import annotations

import hashlib
from typing import Any

from .serialization import canonical_json_dumps


DIGEST_ALGORITHM = "sha256"


def digest_canonical_data(data: Any) -> str:
    """Digest one value through the shared canonical JSON representation."""

    return hashlib.sha256(canonical_json_dumps(data).encode("utf-8")).hexdigest()


def digest_snapshot(snapshot: Any) -> str:
    """Digest one full snapshot through the canonical serializer path."""

    return digest_canonical_data(snapshot)


def digest_topology(topology: Any) -> str:
    """Digest one topology group through the canonical serializer path."""

    return digest_canonical_data(topology)

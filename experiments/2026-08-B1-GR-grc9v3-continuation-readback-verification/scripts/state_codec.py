"""Experiment-local canonical state clone/codec primitives for later GRV3 use."""

from __future__ import annotations

from copy import deepcopy
import json
from typing import Any

from artifact_io import canonical_json_bytes


FIRST_SCIENTIFIC_GATE = "GRV3"


def encode_json_state(state: Any) -> bytes:
    return canonical_json_bytes(state)


def decode_json_state(encoded: bytes) -> Any:
    return json.loads(encoded.decode("utf-8"))


def canonical_clone(state: Any) -> Any:
    return decode_json_state(encode_json_state(state))


def exact_deep_clone(state: Any) -> Any:
    return deepcopy(state)

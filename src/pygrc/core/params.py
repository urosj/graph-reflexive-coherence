"""Shared parameter abstractions for PyGRC.

Phase 1 fixes the contract boundary for core model parameters here:

- core model params are immutable,
- raw config and resolved params are distinguishable,
- canonical params identity is produced centrally,
- runtime/tooling domains are rejected from the core params object.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
from types import MappingProxyType
from typing import Any, Final, TypeAlias

from .serialization import canonical_json_dumps, canonicalize_json_value


FrozenValue: TypeAlias = Any

CORE_PARAM_DOMAINS: Final[tuple[str, ...]] = (
    "evolution",
    "constitutive_semantic_modes",
    "numerical_backend",
)

EXCLUDED_PARAM_DOMAINS: Final[tuple[str, ...]] = (
    "runtime",
    "observer",
    "tooling",
)


def _freeze_value(value: Any) -> FrozenValue:
    """Recursively freeze nested parameter values into immutable structures."""
    if isinstance(value, MappingProxyType):
        return value
    if isinstance(value, dict):
        frozen_items = {key: _freeze_value(value[key]) for key in sorted(value)}
        return MappingProxyType(frozen_items)
    if isinstance(value, list | tuple):
        return tuple(_freeze_value(item) for item in value)
    if isinstance(value, set | frozenset):
        return tuple(sorted(canonicalize_json_value(item) for item in value))
    return value


@dataclass(frozen=True)
class GRCParams:
    """Immutable core model parameters shared across model families."""

    dt: float
    evolution: MappingProxyType[str, FrozenValue] = field(
        default_factory=lambda: MappingProxyType({})
    )
    constitutive_semantic_modes: MappingProxyType[str, FrozenValue] = field(
        default_factory=lambda: MappingProxyType({})
    )
    numerical_backend: MappingProxyType[str, FrozenValue] = field(
        default_factory=lambda: MappingProxyType({})
    )
    raw_config: MappingProxyType[str, FrozenValue] = field(
        default_factory=lambda: MappingProxyType({}),
        repr=False,
        compare=False,
    )
    resolved_config: MappingProxyType[str, FrozenValue] = field(
        default_factory=lambda: MappingProxyType({})
    )
    params_hash: str = field(default="", init=False)

    def __post_init__(self) -> None:
        if self.dt <= 0:
            raise ValueError("dt must be positive")
        params_hash = hashlib.sha256(
            canonical_json_dumps(self.resolved_config).encode()
        ).hexdigest()
        object.__setattr__(self, "params_hash", params_hash)

    @classmethod
    def from_mapping(cls, config: dict[str, Any]) -> "GRCParams":
        """Resolve a JSON/YAML-friendly core param mapping into immutable params."""
        for domain in EXCLUDED_PARAM_DOMAINS:
            if domain in config:
                raise ValueError(
                    f"core params must not include excluded domain '{domain}'"
                )

        dt = config.get("dt")
        if not isinstance(dt, int | float):
            raise ValueError("config must include numeric dt")

        raw_config = _freeze_value(dict(config))
        evolution = _freeze_value(dict(config.get("evolution", {})))
        constitutive_semantic_modes = _freeze_value(
            dict(config.get("constitutive_semantic_modes", {}))
        )
        numerical_backend = _freeze_value(dict(config.get("numerical_backend", {})))

        resolved_config = _freeze_value(
            {
                "dt": float(dt),
                "evolution": canonicalize_json_value(evolution),
                "constitutive_semantic_modes": canonicalize_json_value(
                    constitutive_semantic_modes
                ),
                "numerical_backend": canonicalize_json_value(numerical_backend),
            }
        )

        return cls(
            dt=float(dt),
            evolution=evolution,
            constitutive_semantic_modes=constitutive_semantic_modes,
            numerical_backend=numerical_backend,
            raw_config=raw_config,
            resolved_config=resolved_config,
        )

    def canonical_identity(self) -> str:
        """Return the canonical identity hash for the resolved params."""
        return self.params_hash

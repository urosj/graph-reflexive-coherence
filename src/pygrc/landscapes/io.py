"""Configuration-layer load/save boundary for normalized landscape seeds."""

from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path
from typing import Any

import yaml

from pygrc.core import InvalidLandscapeSeedError, canonical_json_dumps

from .seed import (
    BasinSeedPrimitive,
    JunctionSeedPrimitive,
    LandscapePrimitive,
    LandscapeSeed,
    PlateauSeedPrimitive,
    PRIMITIVE_BASIN,
    PRIMITIVE_JUNCTION,
    PRIMITIVE_PLATEAU,
    PRIMITIVE_RIDGE,
    PRIMITIVE_SADDLE,
    PRIMITIVE_VALLEY,
    RidgeSeedPrimitive,
    SeedConstitutiveProfile,
    SeedDocumentMeta,
    SeedGeometryHints,
    SeedPotential,
    SeedTransportIntent,
    ValleySeedPrimitive,
)
from .validation import validate_landscape_seed


_YAML_SUFFIXES = {".yaml", ".yml"}
_JSON_SUFFIXES = {".json"}


def _require_mapping(value: Any, *, context: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise InvalidLandscapeSeedError(f"{context} must be a mapping")
    return dict(value)


def _build_primitive_from_data(data: dict[str, Any]) -> LandscapePrimitive:
    primitive_type = data.get("type")
    try:
        if primitive_type == PRIMITIVE_BASIN:
            return BasinSeedPrimitive(**data)
        if primitive_type == PRIMITIVE_PLATEAU:
            return PlateauSeedPrimitive(**data)
        if primitive_type == PRIMITIVE_RIDGE:
            return RidgeSeedPrimitive(**data)
        if primitive_type == PRIMITIVE_VALLEY:
            return ValleySeedPrimitive(**data)
        if primitive_type in {PRIMITIVE_JUNCTION, PRIMITIVE_SADDLE}:
            return JunctionSeedPrimitive(**data)
    except TypeError as exc:
        raise InvalidLandscapeSeedError(
            f"primitive payload for type {primitive_type!r} is malformed"
        ) from exc
    raise InvalidLandscapeSeedError(
        f"unknown landscape primitive type {primitive_type!r}"
    )


def _require_key(
    mapping: dict[str, Any],
    key: str,
    *,
    context: str,
) -> Any:
    if key not in mapping:
        raise InvalidLandscapeSeedError(f"{context} is missing required key {key!r}")
    return mapping[key]


def _build_meta_from_data(data: dict[str, Any]) -> SeedDocumentMeta:
    try:
        return SeedDocumentMeta(**data)
    except TypeError as exc:
        raise InvalidLandscapeSeedError("seed.meta payload is malformed") from exc


def _build_potential_from_data(data: dict[str, Any]) -> SeedPotential:
    try:
        return SeedPotential(**data)
    except TypeError as exc:
        raise InvalidLandscapeSeedError(
            "seed.constitutive_profile.potential payload is malformed"
        ) from exc


def _build_constitutive_profile_from_data(
    data: dict[str, Any],
) -> SeedConstitutiveProfile:
    potential_data = _require_mapping(
        _require_key(
            data,
            "potential",
            context="seed.constitutive_profile",
        ),
        context="seed.constitutive_profile.potential",
    )
    payload = dict(data)
    payload.pop("potential", None)
    try:
        return SeedConstitutiveProfile(
            potential=_build_potential_from_data(potential_data),
            **payload,
        )
    except TypeError as exc:
        raise InvalidLandscapeSeedError(
            "seed.constitutive_profile payload is malformed"
        ) from exc


def _build_transport_intent_from_data(data: dict[str, Any]) -> SeedTransportIntent:
    try:
        return SeedTransportIntent(**data)
    except TypeError as exc:
        raise InvalidLandscapeSeedError(
            "seed.transport_intent item payload is malformed"
        ) from exc


def _build_geometry_hints_from_data(data: dict[str, Any]) -> SeedGeometryHints:
    try:
        return SeedGeometryHints(**data)
    except TypeError as exc:
        raise InvalidLandscapeSeedError(
            "seed.geometry_hints payload is malformed"
        ) from exc


def landscape_seed_from_data(
    data: dict[str, Any],
    *,
    validate: bool = True,
) -> LandscapeSeed:
    """Construct one runtime seed object from normalized mapping data."""

    mapping = _require_mapping(data, context="seed data")
    meta = _build_meta_from_data(
        _require_mapping(
            _require_key(mapping, "meta", context="seed data"),
            context="seed.meta",
        )
    )
    constitutive_profile = _build_constitutive_profile_from_data(
        _require_mapping(
            _require_key(
                mapping,
                "constitutive_profile",
                context="seed data",
            ),
            context="seed.constitutive_profile",
        )
    )
    primitive_payloads = _require_key(mapping, "primitives", context="seed data")
    if not isinstance(primitive_payloads, list):
        raise InvalidLandscapeSeedError("seed.primitives must be a list")
    primitives = [
        _build_primitive_from_data(
            _require_mapping(item, context=f"seed.primitives[{index}]")
        )
        for index, item in enumerate(primitive_payloads)
    ]
    transport_payloads = mapping.get("transport_intent", [])
    if not isinstance(transport_payloads, list):
        raise InvalidLandscapeSeedError("seed.transport_intent must be a list")
    transport_intent = [
        _build_transport_intent_from_data(
            _require_mapping(item, context=f"seed.transport_intent[{index}]")
        )
        for index, item in enumerate(transport_payloads)
    ]
    geometry_hints_data = mapping.get("geometry_hints")
    geometry_hints = None
    if geometry_hints_data is not None:
        geometry_hints = _build_geometry_hints_from_data(
            _require_mapping(geometry_hints_data, context="seed.geometry_hints")
        )
    try:
        seed = LandscapeSeed(
            seed_schema=_require_key(mapping, "seed_schema", context="seed data"),
            seed_version=_require_key(mapping, "seed_version", context="seed data"),
            meta=meta,
            constitutive_profile=constitutive_profile,
            primitives=primitives,
            transport_intent=transport_intent,
            geometry_hints=geometry_hints,
            extensions=_require_mapping(
                mapping.get("extensions", {}),
                context="seed.extensions",
            ),
        )
    except TypeError as exc:
        raise InvalidLandscapeSeedError("seed payload is malformed") from exc
    if validate:
        validate_landscape_seed(seed)
    return seed


def landscape_seed_to_data(
    seed: LandscapeSeed,
    *,
    validate: bool = True,
) -> dict[str, Any]:
    """Convert one runtime seed object into plain mapping data."""

    if validate:
        validate_landscape_seed(seed)
    return asdict(seed)


def landscape_seed_to_canonical_json(
    seed: LandscapeSeed,
    *,
    validate: bool = True,
) -> str:
    """Encode one runtime seed object to canonical derived JSON."""

    return canonical_json_dumps(landscape_seed_to_data(seed, validate=validate))


def load_landscape_seed(path: str | Path, *, validate: bool = True) -> LandscapeSeed:
    """Load one normalized landscape seed from YAML or JSON."""

    seed_path = Path(path)
    suffix = seed_path.suffix.lower()
    text = seed_path.read_text(encoding="utf-8")
    try:
        if suffix in _YAML_SUFFIXES:
            payload = yaml.safe_load(text)
        elif suffix in _JSON_SUFFIXES:
            payload = json.loads(text)
        else:
            raise ValueError(
                "unsupported landscape seed file suffix; expected one of "
                f"{sorted(_YAML_SUFFIXES | _JSON_SUFFIXES)}"
            )
    except (json.JSONDecodeError, yaml.YAMLError) as exc:
        raise InvalidLandscapeSeedError(
            f"failed to parse landscape seed file {seed_path}"
        ) from exc
    if payload is None:
        raise InvalidLandscapeSeedError(
            f"landscape seed file {seed_path} did not contain a document mapping"
        )
    if not isinstance(payload, dict):
        raise InvalidLandscapeSeedError(
            f"landscape seed file {seed_path} must decode to a mapping"
        )
    return landscape_seed_from_data(payload, validate=validate)


def save_landscape_seed(
    seed: LandscapeSeed,
    path: str | Path,
    *,
    validate: bool = True,
) -> None:
    """Save one normalized landscape seed to YAML or JSON."""

    seed_path = Path(path)
    suffix = seed_path.suffix.lower()
    data = landscape_seed_to_data(seed, validate=validate)
    seed_path.parent.mkdir(parents=True, exist_ok=True)
    if suffix in _YAML_SUFFIXES:
        rendered = yaml.safe_dump(
            data,
            sort_keys=False,
            allow_unicode=False,
        )
    elif suffix in _JSON_SUFFIXES:
        rendered = json.dumps(data, indent=2, sort_keys=False, ensure_ascii=True)
        rendered += "\n"
    else:
        raise ValueError(
            "unsupported landscape seed file suffix; expected one of "
            f"{sorted(_YAML_SUFFIXES | _JSON_SUFFIXES)}"
        )
    seed_path.write_text(rendered, encoding="utf-8")


__all__ = [
    "landscape_seed_from_data",
    "landscape_seed_to_canonical_json",
    "landscape_seed_to_data",
    "load_landscape_seed",
    "save_landscape_seed",
]

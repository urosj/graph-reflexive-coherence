"""Canonical JSON and digest helpers shared by source-admission code."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, cast

from .errors import SourceAdmissionError


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def file_sha256(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def load_json_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise SourceAdmissionError(f"cannot read JSON object: {path.name}") from error
    if not isinstance(value, dict):
        raise SourceAdmissionError(f"JSON root is not an object: {path.name}")
    return cast(dict[str, Any], value)


def record_digest(data: dict[str, Any], field: str) -> str:
    return digest({key: value for key, value in data.items() if key != field})

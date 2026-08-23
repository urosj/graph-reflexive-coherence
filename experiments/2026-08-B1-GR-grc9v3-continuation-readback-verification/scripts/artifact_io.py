"""Canonical artifact and repository-path utilities for B1-GR."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
from typing import Any, Iterable


EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = EXPERIMENT_ROOT.parents[1]


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def semantic_digest(value: Any) -> str:
    return sha256_bytes(canonical_json_bytes(value))


def artifact_envelope(
    payload: Any,
    *,
    schema_version: str,
    generating_command: str,
    reproducibility_class: str = "byte_reproducible",
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "schema_version": schema_version,
        "metadata": {
            "generating_command": generating_command,
            "reproducibility_class": reproducibility_class,
            **(metadata or {}),
        },
        "payload": payload,
        "payload_sha256": semantic_digest(payload),
    }


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(
        value,
        sort_keys=True,
        indent=2,
        ensure_ascii=False,
        allow_nan=False,
    )
    path.write_text(rendered + "\n", encoding="utf-8")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def require_repo_relative(value: str) -> str:
    normalized = value.replace("\\", "/")
    candidate = PurePosixPath(normalized)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise ValueError(f"path must be repository-relative: {value!r}")
    if re.match(r"^[A-Za-z]:/", normalized) or "://" in normalized:
        raise ValueError(f"path must not be a drive path or URI: {value!r}")
    return candidate.as_posix()


def repo_relative(path: Path) -> str:
    return require_repo_relative(path.resolve().relative_to(REPO_ROOT).as_posix())


def find_machine_local_path(value: Any, location: str = "$") -> list[str]:
    findings: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            findings.extend(find_machine_local_path(child, f"{location}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            findings.extend(find_machine_local_path(child, f"{location}[{index}]"))
    elif isinstance(value, str):
        normalized = value.replace("\\", "/")
        if normalized.startswith("/") or re.match(r"^[A-Za-z]:/", normalized):
            findings.append(location)
    return findings


def git(*args: str, cwd: Path = REPO_ROOT) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return result.stdout.strip()


def tracked_files(prefixes: Iterable[str], *, cwd: Path = REPO_ROOT) -> list[str]:
    files = git("ls-files", "--", *prefixes, cwd=cwd).splitlines()
    return sorted(require_repo_relative(path) for path in files if path)


def file_manifest(paths: Iterable[str], *, root: Path = REPO_ROOT) -> dict[str, Any]:
    entries = []
    for relative in sorted(set(paths)):
        safe = require_repo_relative(relative)
        path = root / safe
        if not path.is_file():
            raise FileNotFoundError(path)
        entries.append({"path": safe, "sha256": sha256_file(path), "size_bytes": path.stat().st_size})
    return {"files": entries, "tree_sha256": semantic_digest(entries)}


def assert_payload_digest(envelope: dict[str, Any]) -> None:
    expected = semantic_digest(envelope["payload"])
    if envelope.get("payload_sha256") != expected:
        raise ValueError("artifact payload digest mismatch")


def assert_required_fields(value: dict[str, Any], fields: Iterable[str]) -> None:
    missing = sorted(set(fields) - set(value))
    if missing:
        raise ValueError(f"missing required fields: {missing}")

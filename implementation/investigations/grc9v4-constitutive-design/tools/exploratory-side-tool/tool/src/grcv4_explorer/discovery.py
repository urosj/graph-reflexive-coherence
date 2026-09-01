"""Detect repository source evolution without interpreting new content."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

from .canonical import digest, file_sha256
from .paths import decisions_root, repo_path


SAFE_METADATA_FIELDS = (
    "schema_version",
    "schema",
    "status",
    "record_id",
    "artifact_id",
    "gate_id",
)

REFRESH_STEPS = (
    "classify_schema_and_authority",
    "implement_or_update_schema_specific_adapter",
    "admit_successor_source_bundle_identity",
    "rerun_reference_and_graph_conformance",
    "rebuild_all_derived_artifacts",
    "accept_successor_processing_cycle",
)


def _safe_metadata(path: Path) -> tuple[dict[str, Any], bool]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return {}, False
    if not isinstance(value, dict):
        return {}, False
    return {
        key: value[key]
        for key in SAFE_METADATA_FIELDS
        if key in value and isinstance(value[key], (str, int, float, bool, type(None)))
    }, True


def discover_sources(
    repo_root: Path,
    admitted: list[dict[str, Any]],
) -> dict[str, Any]:
    expected = {cast(str, row["path"]): row for row in admitted}
    observed_paths = sorted(decisions_root(repo_root).glob("*.json"))
    observed = {repo_path(path, repo_root): path for path in observed_paths}

    added: list[dict[str, Any]] = []
    changed: list[dict[str, Any]] = []
    missing: list[dict[str, Any]] = []
    unreadable: list[dict[str, Any]] = []

    for relative, row in sorted(expected.items()):
        path = observed.get(relative)
        if path is None:
            missing.append(
                {
                    "path": relative,
                    "source_id": row["source_id"],
                    "expected_file_sha256": row["file_sha256"],
                }
            )
            continue
        observed_sha = file_sha256(path)
        if observed_sha == row["file_sha256"]:
            continue
        metadata, readable = _safe_metadata(path)
        target = {
            "path": relative,
            "source_id": row["source_id"],
            "expected_file_sha256": row["file_sha256"],
            "observed_file_sha256": observed_sha,
            "observed_metadata": metadata,
        }
        changed.append(target)
        if not readable:
            unreadable.append({"path": relative, "admission": "admitted"})

    for relative, path in sorted(observed.items()):
        if relative in expected:
            continue
        metadata, readable = _safe_metadata(path)
        added.append(
            {
                "path": relative,
                "file_sha256": file_sha256(path),
                "observed_metadata": metadata,
            }
        )
        if not readable:
            unreadable.append({"path": relative, "admission": "unadmitted"})

    if unreadable:
        state = "source_observation_unreadable"
    elif missing:
        state = "admitted_source_missing"
    elif changed:
        state = "admitted_source_identity_changed"
    elif added:
        state = "new_unprocessed_source_available"
    else:
        state = "current_bundle_exact"

    payload: dict[str, Any] = {
        "schema": "grcv4_explorer_source_observation_v1",
        "state": state,
        "admitted_record_count": len(expected),
        "observed_record_count": len(observed),
        "added_unprocessed": added,
        "changed_admitted": changed,
        "missing_admitted": missing,
        "unreadable_observations": unreadable,
        "current_repository_state_complete": state == "current_bundle_exact",
        "historical_snapshot_only": state != "current_bundle_exact",
        "live_rebuild_allowed": state == "current_bundle_exact",
        "automatic_admission_allowed": False,
        "refresh_requirement": {
            "required": state != "current_bundle_exact",
            "steps": list(REFRESH_STEPS) if state != "current_bundle_exact" else [],
        },
        "observation_digest": None,
    }
    payload["observation_digest"] = digest(
        {key: value for key, value in payload.items() if key != "observation_digest"}
    )
    return payload

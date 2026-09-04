#!/usr/bin/env python3
"""Build the content-addressed GRCV4/GRC9V4 specification release manifest."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[4]
OUTPUT = ROOT / "specs/grc-v4-specification-release.json"
CHECKSUM = ROOT / "specs/grc-v4-specification-release.sha256"
SOURCE_MANIFEST = ROOT / "specs/grc-v4-source-manifest.json"
READINESS_AUDIT_SHA256 = (
    "32cea1b2752361864b02651cb7d38df85929210adc213aa76ee1307babcb5196"
)

SPECIFICATION_MEMBERS = (
    ("generic_v4_specification", "specs/grc-v4-spec.md"),
    ("grc9v4_specialization", "specs/grc-9-v4-spec.md"),
    ("v4_interface_extension", "specs/grc-common-interface-v4-ext.md"),
    ("fixture_coverage_catalog", "specs/grc-v4-conformance-fixtures.json"),
    ("concrete_conformance_vectors", "specs/grc-v4-conformance-vectors.json"),
    ("implementation_contract_schema", "specs/grc-v4-contract-schema.json"),
    ("source_identity_manifest", "specs/grc-v4-source-manifest.json"),
    ("specification_registry", "specs/README.md"),
    (
        "post_d10_phase_boundary",
        "implementation/investigations/grc9v4-constitutive-design/specification/"
        "PostD10SpecificationBoundary.json",
    ),
    (
        "d11_specification_extraction_gate",
        "implementation/investigations/grc9v4-constitutive-design/specification/"
        "D11PaperPropagationAndSpecificationExtractionGate.json",
    ),
    (
        "specification_engineering_correction_gate",
        "implementation/investigations/grc9v4-constitutive-design/specification/"
        "GRCV4SpecificationEngineeringCorrectionGate.json",
    ),
    (
        "phase_aware_specification_audit",
        "implementation/investigations/grc9v4-constitutive-design/scripts/"
        "audit_grcv4_post_d10_specifications.py",
    ),
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def jcs_subset(value: Any) -> str:
    """Canonicalize the string/bool/list/dict-only release identity payload."""
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    if isinstance(value, list):
        return "[" + ",".join(jcs_subset(item) for item in value) + "]"
    if isinstance(value, dict):
        return (
            "{"
            + ",".join(
                f"{jcs_subset(key)}:{jcs_subset(value[key])}" for key in sorted(value)
            )
            + "}"
        )
    raise TypeError(f"unsupported release identity value: {type(value)!r}")


def member(role: str, relative_path: str) -> dict[str, str]:
    path = ROOT / relative_path
    if not path.is_file():
        raise FileNotFoundError(relative_path)
    return {
        "role": role,
        "path": relative_path,
        "sha256": sha256_file(path),
    }


def source_byte_members(source_manifest: dict[str, Any]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    groups = (
        "sources",
        "successor_investigation_history",
        "accepted_successor_sources",
    )
    seen: set[str] = set()
    for group in groups:
        for entry in source_manifest[group]:
            relative_path = entry["path"]
            if relative_path in seen:
                continue
            seen.add(relative_path)
            row = member(entry["role"], relative_path)
            declared = entry["file_sha256"]
            if row["sha256"] != declared:
                raise ValueError(
                    f"source manifest mismatch for {relative_path}: "
                    f"{row['sha256']} != {declared}"
                )
            rows.append(row)
    return sorted(rows, key=lambda row: row["path"])


def git_head() -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def build() -> dict[str, Any]:
    source_manifest = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
    artifact_members = [member(role, path) for role, path in SPECIFICATION_MEMBERS]
    source_members = source_byte_members(source_manifest)
    creation_tools = [
        member(
            "deterministic_vector_builder",
            "implementation/investigations/grc9v4-constitutive-design/scripts/"
            "build_grcv4_specification_vectors.py",
        ),
        member(
            "deterministic_release_builder",
            "implementation/investigations/grc9v4-constitutive-design/scripts/"
            "build_grcv4_specification_release.py",
        ),
    ]
    ordered_bindings = [
        {"path": row["path"], "sha256": row["sha256"]}
        for row in sorted(
            [*artifact_members, *source_members, *creation_tools],
            key=lambda row: row["path"],
        )
    ]
    identity_payload = {
        "schema": "grcv4_specification_release_identity_v1",
        "artifact_bindings": ordered_bindings,
        "readiness_audit_sha256": READINESS_AUDIT_SHA256,
    }
    canonical = jcs_subset(identity_payload).encode("utf-8")
    release_id = f"grcv4-spec-release-sha256:{sha256_bytes(canonical)}"
    return {
        "schema": "grcv4_specification_release_manifest_v1",
        "status": "normative_preimplementation_release",
        "release_id": release_id,
        "repository": source_manifest["repository"],
        "repository_base_commit": git_head(),
        "release_tree_commit": None,
        "release_tree_commit_semantics": (
            "optional_external_locator_assigned_after_commit; content release_id is authoritative"
        ),
        "branch_at_build": "spec/grcv4-grc9v4",
        "canonicalization": "RFC8785_JCS_over_I_JSON",
        "release_identity_payload": identity_payload,
        "release_identity_canonical_jcs_utf8": canonical.decode("utf-8"),
        "artifact_members": artifact_members,
        "packaged_source_bytes": source_members,
        "source_packaging_semantics": (
            "every controlling source is present at the listed repository path; "
            "commit reachability is provenance-only and is not required to reconstruct bytes"
        ),
        "readiness_audit": {
            "name": "GRCV4-updated-specification-stack-implementation-readiness-audit.md",
            "sha256": READINESS_AUDIT_SHA256,
            "role": "external_correction_input_not_scientific_authority",
        },
        "creation_tools": creation_tools,
        "rebuild_command": (
            "python implementation/investigations/grc9v4-constitutive-design/scripts/"
            "build_grcv4_specification_release.py"
        ),
        "bundle_digest": f"sha256:{sha256_bytes(canonical)}",
        "claim_ceiling": (
            "specification_release_not_runtime_implementation_or_execution_evidence"
        ),
    }


def main() -> int:
    payload = build()
    data = (
        json.dumps(payload, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
    ).encode("utf-8")
    OUTPUT.write_bytes(data)
    checksum = sha256_bytes(data)
    CHECKSUM.write_text(
        f"{checksum}  {OUTPUT.relative_to(ROOT)}\n",
        encoding="utf-8",
    )
    print(
        "GRCV4_SPECIFICATION_RELEASE_BUILT "
        f"release_id={payload['release_id']} manifest_sha256={checksum}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

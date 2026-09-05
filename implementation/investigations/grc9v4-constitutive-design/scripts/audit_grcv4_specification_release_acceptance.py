#!/usr/bin/env python3
"""Verify the append-only acceptance and freeze of the GRCV4 specification release."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[4]
INVESTIGATION = ROOT / "implementation/investigations/grc9v4-constitutive-design"
GATE = INVESTIGATION / "specification/GRCV4SpecificationReleaseAcceptanceGate.json"
BOUNDARY = INVESTIGATION / "specification/PostGRCV4SpecificationAcceptanceBoundary.json"
RELEASE = ROOT / "specs/grc-v4-specification-release.json"
CHECKSUM = ROOT / "specs/grc-v4-specification-release.sha256"

ACCEPTED_RELEASE_ID = (
    "grcv4-spec-release-sha256:"
    "9f4c8fe5b57b1c477d834a3e4dae3f98a2b18c70e6e7f598e3c9652170c8645f"
)
ACCEPTED_RELEASE_SHA256 = (
    "bba0bb649bc2e80c5bfa99f96bd5824bbdda3b3fbc87fb68c3e3a59da1cee46b"
)
ACCEPTED_CHECKSUM_SHA256 = (
    "50b20509b84a6b21f3036ecb1d7e13861f662bc8319873c5321fc0317ada7e33"
)
ACCEPTED_COMMIT = "f1817b8cf41e439cbb18ad82dfab6b39a77ae43d"
ACCEPTANCE_AUDIT_SHA256 = (
    "f136c8552e1c7ef59570c11b26d592430e42058a9d9994e75a09560fda84242e"
)
PREDECESSOR_GATE_SHA256 = (
    "57f2e8e634ae362933e94e72f634141e989dc357858940a4e5a4342dfc530f73"
)
PREDECESSOR_BOUNDARY_SHA256 = (
    "f4fb7d5b5a4b5d9ad38105cec89f6e2b16eaad3afc02af4da8f51dffe6fa277e"
)
DECISION_RECORD_DIGEST = (
    "914761881649b34bd7d0e80ef006551696c30190308544587d267800634faa11"
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def canonical_json(value: Any, *, ensure_ascii: bool) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=ensure_ascii,
        allow_nan=False,
    ).encode("utf-8")


def git_bytes(revision: str, relative_path: str) -> bytes:
    return subprocess.run(
        ["git", "show", f"{revision}:{relative_path}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    ).stdout


def verify_release() -> dict[str, Any]:
    require(sha256_file(RELEASE) == ACCEPTED_RELEASE_SHA256, "release byte drift")
    require(
        sha256_file(CHECKSUM) == ACCEPTED_CHECKSUM_SHA256,
        "detached checksum file drift",
    )
    checksum_parts = CHECKSUM.read_text(encoding="utf-8").strip().split()
    require(
        checksum_parts
        == [ACCEPTED_RELEASE_SHA256, "specs/grc-v4-specification-release.json"],
        "detached checksum target drift",
    )

    release = json.loads(RELEASE.read_text(encoding="utf-8"))
    require(release.get("release_id") == ACCEPTED_RELEASE_ID, "release ID drift")
    identity_payload = release["release_identity_payload"]
    identity_digest = sha256_bytes(canonical_json(identity_payload, ensure_ascii=False))
    require(
        ACCEPTED_RELEASE_ID == f"grcv4-spec-release-sha256:{identity_digest}",
        "release identity payload drift",
    )
    require(
        release.get("bundle_digest") == f"sha256:{identity_digest}",
        "release bundle digest drift",
    )

    bound_rows = [
        *release["artifact_members"],
        *release["packaged_source_bytes"],
        *release["creation_tools"],
    ]
    paths = [row["path"] for row in bound_rows]
    require(len(paths) == len(set(paths)), "duplicate release-bound path")
    for row in bound_rows:
        path = ROOT / row["path"]
        require(path.is_file(), f"missing release-bound path: {row['path']}")
        require(
            sha256_file(path) == row["sha256"],
            f"release-bound worktree drift: {row['path']}",
        )
    require(
        sha256_bytes(git_bytes(ACCEPTED_COMMIT, str(RELEASE.relative_to(ROOT))))
        == ACCEPTED_RELEASE_SHA256,
        "accepted commit does not contain accepted release bytes",
    )
    ancestor = subprocess.run(
        ["git", "merge-base", "--is-ancestor", ACCEPTED_COMMIT, "HEAD"],
        cwd=ROOT,
        check=False,
    )
    require(ancestor.returncode == 0, "accepted release commit is not an ancestor")
    return release


def verify_gate(audit_file: Path) -> dict[str, Any]:
    require(audit_file.is_file(), "final narrow acceptance audit is missing")
    require(
        sha256_file(audit_file) == ACCEPTANCE_AUDIT_SHA256,
        "final narrow acceptance audit hash drift",
    )
    gate = json.loads(GATE.read_text(encoding="utf-8"))
    require(gate.get("status") == "accepted_frozen", "acceptance status drift")
    declared_digest = gate.get("decision_record_digest")
    payload = dict(gate)
    payload.pop("decision_record_digest", None)
    require(
        sha256_bytes(canonical_json(payload, ensure_ascii=True)) == declared_digest,
        "acceptance decision-record digest drift",
    )
    require(declared_digest == DECISION_RECORD_DIGEST, "acceptance digest mismatch")
    sources = gate["source_identities"]
    require(
        sources["predecessor_gate"]["sha256"] == PREDECESSOR_GATE_SHA256,
        "predecessor gate binding drift",
    )
    require(
        sources["accepted_release"]["release_id"] == ACCEPTED_RELEASE_ID
        and sources["accepted_release"]["file_sha256"] == ACCEPTED_RELEASE_SHA256,
        "accepted release binding drift",
    )
    require(
        sources["final_narrow_acceptance_audit"]["sha256"] == ACCEPTANCE_AUDIT_SHA256,
        "acceptance audit binding drift",
    )
    decision = gate["decision"]
    effect = gate["authorization_effect"]
    require(
        decision["specification_release_accepted"] is True
        and decision["specification_release_state"]
        == "frozen_normative_preimplementation_contract"
        and decision["implementation_phase_activated"] is False,
        "acceptance decision drift",
    )
    require(
        effect["specification_release_frozen"] is True
        and effect["specification_mutation_authorized"] is False
        and effect["implementation_review_ready"] is True
        and effect["implementation_review_activated"] is False
        and effect["implementation_authorized"] is False
        and effect["runtime_or_src_tests_change_authorized"] is False,
        "acceptance authorization boundary drift",
    )
    return gate


def verify_boundary(gate: dict[str, Any]) -> None:
    boundary = json.loads(BOUNDARY.read_text(encoding="utf-8"))
    require(
        boundary.get("status")
        == "accepted_specification_frozen_awaiting_branch_closure",
        "post-acceptance boundary status drift",
    )
    require(
        boundary.get("active_phase") == "specification_release_accepted",
        "live governance phase drift",
    )
    require(
        boundary["predecessor_phase_boundary"]["sha256"] == PREDECESSOR_BOUNDARY_SHA256,
        "predecessor boundary binding drift",
    )
    phase_authority = boundary["phase_authority"]
    require(
        phase_authority["sha256"] == sha256_file(GATE)
        and phase_authority["decision_record_digest"] == gate["decision_record_digest"],
        "acceptance gate/boundary binding drift",
    )
    accepted_release = boundary["accepted_release"]
    require(
        accepted_release["release_id"] == ACCEPTED_RELEASE_ID
        and accepted_release["file_sha256"] == ACCEPTED_RELEASE_SHA256,
        "boundary release binding drift",
    )
    transition = boundary["state_transition"]
    require(
        transition["from"] == "specification_correction"
        and transition["to"] == "specification_release_accepted"
        and transition["correction_gate_closed"] is True
        and transition["implementation_review_ready"] is True
        and transition["implementation_review_activated"] is False
        and transition["implementation_authorized"] is False,
        "post-acceptance state transition drift",
    )
    branch = boundary["branch_closure"]
    require(
        branch["ready"] is True and branch["completed"] is False,
        "specification branch closure state drift",
    )
    require(
        boundary.get("next_gate") == "GRCV4_GRC9V4_implementation_review",
        "post-acceptance next gate drift",
    )
    verification = boundary["acceptance_verification"]
    require(
        verification["path"] == str(Path(__file__).resolve().relative_to(ROOT))
        and verification["sha256"] == sha256_file(Path(__file__).resolve()),
        "acceptance verifier binding drift",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--audit-file",
        type=Path,
        required=True,
        help="Exact final narrow acceptance audit whose SHA is bound by the gate.",
    )
    args = parser.parse_args()
    release = verify_release()
    gate = verify_gate(args.audit_file.resolve())
    verify_boundary(gate)
    require(
        re.fullmatch(r"grcv4-spec-release-sha256:[0-9a-f]{64}", ACCEPTED_RELEASE_ID)
        is not None,
        "accepted release ID format drift",
    )
    print(
        "GRCV4_SPECIFICATION_RELEASE_ACCEPTANCE_AUDIT_PASS "
        f"release_id={release['release_id']} "
        f"artifacts={len(release['artifact_members'])} "
        "state=accepted_frozen branch_closure_ready=true "
        "implementation_authorized=false"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

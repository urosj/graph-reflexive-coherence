"""Deterministic P9-4.9.2 successor of the accepted mapped-vector release.

This is the current release builder, not a rewrite of the old correction's
checker or acceptance. Historical inputs remain available at their Git subject.
"""

from copy import deepcopy
import argparse
import ast
import json
from pathlib import Path
import subprocess

from build_mapped_vector_release import (
    ASSETS,
    CHECKSUM,
    CODEC,
    RELEASE,
    ROOT,
    canonical,
    pretty,
    sha,
)

INV = "implementation/investigations/grc9v4-constitutive-design/"
SOURCE = INV + "decisions/P9ReceiptParentAuthority.json"
ADMISSION = INV + "tools/exploratory-side-tool/records/P9492ReceiptParentAdmission.json"
GENERATOR = "implementation/phase-9-grcv4/verification/build_receipt_parent_release.py"
SOURCE_MANIFEST = "specs/grc-v4-source-manifest.json"
CHANGED = {
    INV + "drafts/GRCV4-proposal.md",
    INV + "drafts/2026-09-GRC-V4.md",
    "specs/grc-v4-spec.md",
    "specs/grc-common-interface-v4-ext.md",
    "specs/README.md",
    SOURCE_MANIFEST,
}
PREDECESSOR_COMMIT = "280f46cec28b06ffd65b6ee04ba8caadc3d8d069"
PREDECESSOR_RELEASE = "grcv4-spec-release-sha256:7b8b4d4e32e48fd35f70421cce7f547eebb21dd81389764061efe6e1a8c19886"
PARENT_AUTHORITY_DIGEST = (
    "ba7d69189c527153828b02c2bb3311899b036a634446de9ad8f36af6592c28f8"
)


def build(root=ROOT):
    source = json.loads((root / SOURCE).read_text())
    if (
        source["record_digest"]
        != sha(canonical({k: v for k, v in source.items() if k != "record_digest"}))
        or source["record_digest"] != PARENT_AUTHORITY_DIGEST
        or source["predecessor_release_id"] != PREDECESSOR_RELEASE
        or source["predecessor_commit"] != PREDECESSOR_COMMIT
    ):
        raise ValueError("untrusted parent authority")
    predecessor = json.loads(
        subprocess.check_output(
            ["git", "show", PREDECESSOR_COMMIT + ":" + RELEASE], cwd=root
        )
    )
    if predecessor["release_id"] != PREDECESSOR_RELEASE:
        raise ValueError("receipt-parent predecessor mismatch")
    value = deepcopy(predecessor)
    groups = ("artifact_members", "packaged_source_bytes", "creation_tools")
    for group in groups:
        for row in value[group]:
            current = sha((root / row["path"]).read_bytes())
            if row["path"] not in CHANGED and current != row["sha256"]:
                raise ValueError("unrelated release member changed: " + row["path"])
            row["sha256"] = current
    manifest = json.loads((root / SOURCE_MANIFEST).read_text())
    for group in (
        "sources",
        "successor_investigation_history",
        "accepted_successor_sources",
    ):
        for row in manifest[group]:
            if sha((root / row["path"]).read_bytes()) != row["file_sha256"]:
                raise ValueError("source manifest stale: " + row["path"])
    for role, path, group in (
        ("accepted_receipt_parent_authority", SOURCE, "packaged_source_bytes"),
        ("receipt_parent_forensic_admission", ADMISSION, "packaged_source_bytes"),
        ("receipt_parent_successor_release_builder", GENERATOR, "creation_tools"),
    ):
        value[group].append(
            {"role": role, "path": path, "sha256": sha((root / path).read_bytes())}
        )
    identity = {
        "schema": "grcv4_specification_release_identity_v3",
        "artifact_bindings": sorted(
            (
                {"path": row["path"], "sha256": row["sha256"]}
                for group in groups
                for row in value[group]
            ),
            key=lambda r: r["path"],
        ),
        "predecessor_release_id": PREDECESSOR_RELEASE,
        "accepted_parent_authority_digest": PARENT_AUTHORITY_DIGEST,
        "receipt_parent_policy_id": source["policy_id"],
    }
    encoded = canonical(identity)
    value.update(
        status="normative_bounded_receipt_parent_successor_release",
        release_id="grcv4-spec-release-sha256:" + sha(encoded),
        release_identity_payload=identity,
        release_identity_canonical_jcs_utf8=encoded.decode(),
        bundle_digest="sha256:" + sha(encoded),
        predecessor_release_id=PREDECESSOR_RELEASE,
        repository_base_commit=PREDECESSOR_COMMIT,
        branch_at_build="impl/phase-9-grcv4-tranche-4-closure",
        accepted_parent_authority={
            "path": SOURCE,
            "record_digest": PARENT_AUTHORITY_DIGEST,
        },
        receipt_parent_policy_id=source["policy_id"],
        rebuild_command=".venv/bin/python " + GENERATOR + " --check",
        claim_ceiling="Accepted structural parent contract; bounded C_OS implementation only. Public facade, complete-profile evidence and G2 remain pending; no other-profile or specialization support.",
    )
    for key in ("readiness_audit", "pressure_audit", "final_acceptance_audit"):
        value[key]["scope"] = (
            "historical_predecessor_only_not_review_of_parent_successor"
        )
    data = pretty(value)
    checksum = (sha(data) + "  " + RELEASE + "\n").encode()
    index = {
        "schema": "grcv4-packaged-assets-v1",
        "release_id": value["release_id"],
        "files": [
            {
                "name": "grc-v4-contract-schema.json",
                "sha256": sha(
                    (root / "specs/grc-v4-contract-schema.json").read_bytes()
                ),
            },
            {"name": Path(RELEASE).name, "sha256": sha(data)},
            {"name": Path(CHECKSUM).name, "sha256": sha(checksum)},
        ],
    }
    return value["release_id"], {
        RELEASE: data,
        CHECKSUM: checksum,
        ASSETS + Path(RELEASE).name: data,
        ASSETS + Path(CHECKSUM).name: checksum,
        ASSETS + "asset-index.json": pretty(index),
    }


def verify(root=ROOT):
    release_id, outputs = build(root)
    for name, data in outputs.items():
        if (root / name).read_bytes() != data:
            raise ValueError("parent successor output changed: " + name)
    codec = ast.parse((root / CODEC).read_text())
    pins = {
        target.id: ast.literal_eval(node.value)
        for node in codec.body
        if isinstance(node, ast.Assign)
        for target in node.targets
        if isinstance(target, ast.Name) and target.id in {"RELEASE_ID", "_INDEX_SHA256"}
    }
    if pins.get("RELEASE_ID") != release_id or pins.get("_INDEX_SHA256") != sha(
        outputs[ASSETS + "asset-index.json"]
    ):
        raise ValueError("codec does not pin the parent successor release")
    return release_id


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", required=True)
    parser.parse_args()
    print("P9492_PARENT_RELEASE_PASS release_id=" + verify())

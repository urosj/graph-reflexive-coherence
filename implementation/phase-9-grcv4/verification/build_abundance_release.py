"""Deterministic P9-4.9.1a successor of the accepted receipt-parent release.

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
SOURCE = INV + "decisions/P9AbundanceInterfaceAuthority.json"
ADMISSION = INV + "tools/exploratory-side-tool/records/P9491aAbundanceAdmission.json"
GENERATOR = "implementation/phase-9-grcv4/verification/build_abundance_release.py"
SOURCE_MANIFEST = "specs/grc-v4-source-manifest.json"
CHANGED = {
    INV + "drafts/GRCV4-proposal.md",
    INV + "drafts/2026-09-GRC-V4.md",
    "specs/grc-v4-spec.md",
    "specs/grc-9-v4-spec.md",
    "specs/grc-common-interface-v4-ext.md",
    "specs/README.md",
    SOURCE_MANIFEST,
}
PREDECESSOR_COMMIT = "7905e7e22bb2fb37f09d0de01f3f161b83332618"
PREDECESSOR_RELEASE = "grcv4-spec-release-sha256:f777519824f86c3e9382bcf9b45cba28554351506f354d3f778746e2aaff5c6b"
ABUNDANCE_AUTHORITY_DIGEST = (
    "d9488700be9624da8500c1e533aa65d33b4f36a3307748ad12fd66449d8fe053"
)


def build(root=ROOT):
    source = json.loads((root / SOURCE).read_text())
    if (
        source["record_digest"]
        != sha(canonical({k: v for k, v in source.items() if k != "record_digest"}))
        or source["record_digest"] != ABUNDANCE_AUTHORITY_DIGEST
        or source["predecessor_release_id"] != PREDECESSOR_RELEASE
        or source["predecessor_commit"] != PREDECESSOR_COMMIT
    ):
        raise ValueError("untrusted abundance authority")
    predecessor = json.loads(
        subprocess.check_output(
            ["git", "show", PREDECESSOR_COMMIT + ":" + RELEASE], cwd=root
        )
    )
    if predecessor["release_id"] != PREDECESSOR_RELEASE:
        raise ValueError("abundance-interface predecessor mismatch")
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
        ("accepted_abundance_interface_authority", SOURCE, "packaged_source_bytes"),
        ("abundance_interface_forensic_admission", ADMISSION, "packaged_source_bytes"),
        ("abundance_interface_successor_release_builder", GENERATOR, "creation_tools"),
    ):
        value[group].append(
            {"role": role, "path": path, "sha256": sha((root / path).read_bytes())}
        )
    identity = {
        "schema": "grcv4_specification_release_identity_v4",
        "artifact_bindings": sorted(
            (
                {"path": row["path"], "sha256": row["sha256"]}
                for group in groups
                for row in value[group]
            ),
            key=lambda r: r["path"],
        ),
        "predecessor_release_id": PREDECESSOR_RELEASE,
        "accepted_abundance_authority_digest": ABUNDANCE_AUTHORITY_DIGEST,
        "abundance_interface_policy_id": source["policy_id"],
    }
    encoded = canonical(identity)
    value.update(
        status="normative_bounded_abundance_interface_successor_release",
        release_id="grcv4-spec-release-sha256:" + sha(encoded),
        release_identity_payload=identity,
        release_identity_canonical_jcs_utf8=encoded.decode(),
        bundle_digest="sha256:" + sha(encoded),
        predecessor_release_id=PREDECESSOR_RELEASE,
        repository_base_commit=PREDECESSOR_COMMIT,
        branch_at_build="impl/phase-9-grcv4-tranche-4-closure",
        accepted_abundance_authority={
            "path": SOURCE,
            "record_digest": ABUNDANCE_AUTHORITY_DIGEST,
        },
        abundance_interface_policy_id=source["policy_id"],
        rebuild_command=".venv/bin/python " + GENERATOR + " --check",
        claim_ceiling="Accepted abundance availability contract; no numeric functional. Bounded C_OS projection only; final fixture reconciliation and G2 remain pending; no other-profile or specialization support.",
    )
    for key in ("readiness_audit", "pressure_audit", "final_acceptance_audit"):
        value[key]["scope"] = (
            "historical_predecessor_only_not_review_of_abundance_successor"
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
            raise ValueError("abundance successor output changed: " + name)
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
        raise ValueError("codec does not pin the abundance successor release")
    return release_id


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", required=True)
    parser.parse_args()
    print("P9491A_ABUNDANCE_RELEASE_PASS release_id=" + verify())

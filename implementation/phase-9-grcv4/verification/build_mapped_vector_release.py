"""Reconstruct the accepted, bounded P9-4.7b vector-correction release."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
import re
import runpy
import subprocess

ROOT = Path(__file__).resolve().parents[3]
DECISION = "implementation/phase-9-grcv4/tranche-4/P9-4.7b-SpecificationCorrection.json"
GENERATOR = "implementation/phase-9-grcv4/verification/build_mapped_vector_release.py"
INV = "implementation/investigations/grc9v4-constitutive-design/"
RELEASE = "specs/grc-v4-specification-release.json"
CHECKSUM = "specs/grc-v4-specification-release.sha256"
ASSETS = "src/pygrc/models/grc_v4_assets/"
CODEC = "src/pygrc/models/grc_v4_codec.py"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()


def pretty(value):
    return (json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode()


def build(root=ROOT):
    decision = json.loads((root / DECISION).read_text())
    payload = {k: v for k, v in decision.items() if k != "record_digest"}
    if decision["record_digest"] != sha(canonical(payload)):
        raise ValueError("stale mapped-vector correction decision")
    if decision["status"] != "accepted_by_user_for_implementation":
        raise ValueError("mapped-vector correction is not accepted")
    for row in decision["evidence_bindings"] + decision["corrected_artifacts"]:
        if sha((root / row["path"]).read_bytes()) != row["sha256"]:
            raise ValueError("mapped-vector correction binding changed: " + row["path"])
    predecessor = json.loads(subprocess.check_output(
        ["git", "show", decision["predecessor_commit"] + ":" + RELEASE], cwd=root
    ))
    if predecessor["release_id"] != decision["predecessor_release_id"]:
        raise ValueError("mapped-vector correction predecessor mismatch")
    base = runpy.run_path(str(root / INV / "scripts/build_grcv4_specification_release.py"))
    value = base["build"]()
    additions = [
        {"role": "accepted_mapped_vector_correction", "path": DECISION, "sha256": sha((root / DECISION).read_bytes())},
        {"role": "bounded_successor_release_builder", "path": GENERATOR, "sha256": sha((root / GENERATOR).read_bytes())},
    ]
    value["artifact_members"].append(additions[0])
    value["creation_tools"].append(additions[1])
    identity = value["release_identity_payload"]
    identity["artifact_bindings"] = sorted(identity["artifact_bindings"] + [
        {"path": row["path"], "sha256": row["sha256"]} for row in additions
    ], key=lambda row: row["path"])
    identity["predecessor_release_id"] = decision["predecessor_release_id"]
    identity["accepted_correction_digest"] = decision["record_digest"]
    encoded = canonical(identity)
    value.update(
        status="normative_bounded_specification_correction_release",
        release_id="grcv4-spec-release-sha256:" + sha(encoded),
        release_identity_canonical_jcs_utf8=encoded.decode(),
        bundle_digest="sha256:" + sha(encoded),
        predecessor_release_id=decision["predecessor_release_id"],
        repository_base_commit=decision["predecessor_commit"],
        branch_at_build="impl/phase-9-grcv4-tranche-4",
        accepted_correction={"path": DECISION, "record_digest": decision["record_digest"]},
        rebuild_command=".venv/bin/python " + GENERATOR,
        claim_ceiling=decision["claim_ceiling"],
    )
    for name in ("readiness_audit", "pressure_audit", "final_acceptance_audit"):
        value[name]["scope"] = "predecessor_release_only_not_a_review_of_this_correction"
    data = pretty(value)
    checksum = (sha(data) + "  " + RELEASE + "\n").encode()
    index = {
        "schema": "grcv4-packaged-assets-v1", "release_id": value["release_id"],
        "files": [
            {"name": "grc-v4-contract-schema.json", "sha256": sha((root / "specs/grc-v4-contract-schema.json").read_bytes())},
            {"name": Path(RELEASE).name, "sha256": sha(data)},
            {"name": Path(CHECKSUM).name, "sha256": sha(checksum)},
        ],
    }
    return value["release_id"], {
        RELEASE: data, CHECKSUM: checksum,
        ASSETS + Path(RELEASE).name: data, ASSETS + Path(CHECKSUM).name: checksum,
        ASSETS + "asset-index.json": pretty(index),
    }


def verify(root=ROOT, expected_release_id=None):
    release_id, outputs = build(root)
    if expected_release_id is not None and release_id != expected_release_id:
        raise ValueError("untrusted mapped-vector successor release")
    for name, data in outputs.items():
        if (root / name).read_bytes() != data:
            raise ValueError("mapped-vector successor output changed: " + name)
    codec = ast.parse((root / CODEC).read_text())
    pins = {target.id: ast.literal_eval(node.value) for node in codec.body
            if isinstance(node, ast.Assign) for target in node.targets
            if isinstance(target, ast.Name) and target.id in {"RELEASE_ID", "_INDEX_SHA256"}}
    if pins.get("RELEASE_ID") != release_id or pins.get("_INDEX_SHA256") != sha(outputs[ASSETS + "asset-index.json"]):
        raise ValueError("packaged successor release is not pinned by the codec")
    return release_id


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        release_id = verify()
    else:
        release_id, outputs = build()
        for name, data in outputs.items():
            (ROOT / name).write_bytes(data)
        path = ROOT / CODEC
        source = path.read_text()
        source, count = re.subn(
            r'(RELEASE_ID = \(\n    "grcv4-spec-release-sha256:"\n    ")[0-9a-f]{64}("\n\))',
            lambda match: match[1] + release_id.split(":")[1] + match[2], source,
        )
        if count != 1:
            raise ValueError("codec release pin declaration changed")
        source, count = re.subn(
            r'_INDEX_SHA256 = "[0-9a-f]{64}"',
            '_INDEX_SHA256 = "' + sha(outputs[ASSETS + "asset-index.json"]) + '"', source,
        )
        if count != 1:
            raise ValueError("codec index pin declaration changed")
        path.write_text(source)
        verify()
    print("P947_MAPPED_VECTOR_RELEASE_PASS release_id=" + release_id)


if __name__ == "__main__":
    main()

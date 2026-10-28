"""Exact basin design propagation; preserve historical document/release subjects.

No native trajectory, runtime support or new executable release is inferred.
"""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
INV = "implementation/investigations/grc9v4-constitutive-design/"
SIDE = INV + "tools/exploratory-side-tool/"
MANIFEST = "specs/grc-9-v4-basin-interface-source-manifest.json"
MANIFEST_DIGEST = "e534ea538bd20ab42a7fd598be2a4c88ce0120b465679844a6b47e3bd737b9d5"
DOCUMENTS = (
    INV + "drafts/GRCV4-proposal.md",
    INV + "drafts/2026-09-GRC-V4.md",
    "specs/README.md",
    INV + "GRC9V4ConstitutiveDesignPlan.md",
    INV + "GRC9V4ConstitutiveDesignChecklist.md",
    INV + "GRC9V4ConstitutiveDesignDecisionLedger.md",
)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def seal(value):
    body = {k: v for k, v in value.items() if k != "record_digest"}
    return {
        **body,
        "record_digest": sha(
            json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
        ),
    }


def checked_manifest(root=ROOT):
    root = Path(root)
    value = json.loads((root / MANIFEST).read_bytes())
    if value != seal(value) or value["record_digest"] != MANIFEST_DIGEST:
        raise ValueError(
            "basin propagation manifest is not the pinned design successor"
        )
    for row in value["artifacts"]:
        path = root / row["path"]
        if (
            not path.resolve().is_relative_to(root.resolve())
            or sha(path.read_bytes()) != row["sha256"]
        ):
            raise ValueError("basin propagation source drift: " + row["path"])
    return value


def predecessor_document_bytes(root, name):
    """Only the exact bound insertion may differ; no generic path exemption."""
    root = Path(root)
    if name not in DOCUMENTS:
        return (root / name).read_bytes()
    value = checked_manifest(root)
    row = next(r for r in value["document_successors"] if r["path"] == name)
    current = (root / name).read_bytes()
    start, end = row["start"].encode(), row["end"].encode()
    if current.count(start) != 1 or current.count(end) != 1:
        raise ValueError("basin document insertion is not unique: " + name)
    a, b = current.index(start), current.index(end)
    insertion = current[a:b]
    if a >= b or sha(insertion) != row["insertion_sha256"]:
        raise ValueError("basin document insertion drift: " + name)
    historical = subprocess.check_output(
        [
            "git",
            "show",
            row.get("predecessor_commit", value["predecessor_commit"]) + ":" + name,
        ],
        cwd=root,
    )
    if (
        sha(historical) != row["before_sha256"]
        or current[:a] + current[b:] != historical
    ):
        raise ValueError("unrelated scientific document changed: " + name)
    return historical


def predecessor_checker_bytes(root, name):
    """Original release builder bytes after its explicit provenance-reader update."""
    from p994b_runtime_successor import SOURCES, historical_source

    row = SOURCES[name]
    expected, revision = next(iter(row["predecessors"].items()))
    if historical_source(root, name, expected) != expected:
        raise ValueError("unbound historical release-builder successor: " + name)
    return subprocess.check_output(["git", "show", revision + ":" + name], cwd=root)


def check(root=ROOT):
    root = Path(root)
    value = checked_manifest(root)
    for name in DOCUMENTS:
        predecessor_document_bytes(root, name)
    sections = []
    for name in DOCUMENTS[:2]:
        s = (root / name).read_text()
        sections.append(
            s[s.index("### A.5.1 ") : s.index("### A.6 Mechanical expansion")]
        )
    if sections[0] != sections[1]:
        raise ValueError("basin paper differs from the propagated proposal")
    sys.path.insert(0, str(root / SIDE / "tool/src"))
    from grcv4_explorer.basin import basin_authority

    view = basin_authority(root, root / SIDE)
    if view["authority_record_digest"] != value["authority_record_digest"]:
        raise ValueError("basin authority/propagation mismatch")
    release = value["predecessor_executable_release"]
    if sha((root / release["path"]).read_bytes()) != release["sha256"]:
        raise ValueError("executable release changed during design propagation")
    import jsonschema

    schema = json.loads(
        (root / "specs/grc-9-v4-basin-interface-schema.json").read_bytes()
    )
    jsonschema.Draft202012Validator.check_schema(schema)
    return dict(
        status="passed_design_propagation",
        authority_record_digest=view["authority_record_digest"],
        claim_id="P9-10.1a-CL-N-BASIN-001",
        contracts=len(view["contracts"]),
        design_debt="resolved_bounded_design",
        native_conformance=False,
        P9_10_1a_closed=False,
        runtime_release_unchanged=True,
        proposal_paper_section_identical=True,
        manifest_digest=value["record_digest"],
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", required=True)
    parser.parse_args()
    print(json.dumps(check()))

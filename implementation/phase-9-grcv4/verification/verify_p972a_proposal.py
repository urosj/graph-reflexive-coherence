"""Review-stage proposal fidelity, separate from the unchanged executable release."""

import argparse
import ast
import json
import sys

import phase9_implementation_policy as p
from build_mapped_vector_release import ASSETS, CHECKSUM, CODEC, RELEASE, canonical
from verify_p972a_initializer_authority import historical_blobs

BASE = "f36b3ba7c7087ca457177c6644bb9a3093085744"
PROPOSAL = p.INV + "drafts/GRCV4-proposal.md"
PAPER = p.INV + "drafts/2026-09-GRC-V4.md"
SOURCE_MANIFEST = "specs/grc-v4-source-manifest.json"
PROPOSAL_SHA256 = "09c080fd835d096372cff6204e42ddf0baba2b2da674fee905c7b5df2c83ed84"
PROJECTION_DIGEST = "fa59abda356446daca516b33028a07a48ec63aaacb8f961cd274a425dca48dd1"
GROUPS = ("artifact_members", "packaged_source_bytes", "creation_tools")


def proposal_status():
    """Exact review candidate and typed attribution, not automatic semantic proof."""
    p.require(p.sha((p.ROOT / PROPOSAL).read_bytes()) == PROPOSAL_SHA256,
              "unreviewed proposal candidate drift")
    sys.path.insert(0, str(p.ROOT / p.SIDE / "tool/src"))
    from grcv4_explorer.a_initializer import initializer_authority
    view = initializer_authority(p.ROOT, p.ROOT / p.SIDE)
    p.require(view["projection_digest"] == PROJECTION_DIGEST,
              "proposal initializer authority drift")
    return dict(proposal_status="accepted", proposal_path=PROPOSAL,
                proposal_sha256=PROPOSAL_SHA256, proposal_revision_accepted=True,
                source_projection_digest=view["projection_digest"],
                paper_propagated=False, specification_propagated=False,
                semantic_review_automated=False)


def verify_release():
    """Retain the exact release and its original source bytes; never rebuild it
    from a newer draft or relabel this as a new generator/runtime execution.
    Only the proposal source is read from its explicitly declared Git subject.
    Every other released member and packaged asset must still match live bytes.
    """
    frozen = historical_blobs([RELEASE, PROPOSAL], commit=BASE)
    raw = (p.ROOT / RELEASE).read_bytes()
    p.require(raw == frozen[RELEASE], "accepted executable release changed")
    release = json.loads(raw)
    p.require(release["release_id"] == p.ABUNDANCE_RELEASE_ID,
              "wrong executable release")
    rows = [row for group in GROUPS for row in release[group]]
    p.require(len({row["path"] for row in rows}) == len(rows), "duplicate release member")
    identity = release["release_identity_payload"]
    bindings = sorted([dict(path=row["path"], sha256=row["sha256"]) for row in rows],
                      key=lambda row: row["path"])
    p.require(identity["artifact_bindings"] == bindings and
              release["release_identity_canonical_jcs_utf8"] == canonical(identity).decode() and
              release["release_id"] == "grcv4-spec-release-sha256:" + p.sha(canonical(identity)),
              "released identity is not exact")

    def subject_bytes(name):
        return frozen[PROPOSAL] if name == PROPOSAL else p.safe_path(p.ROOT, name).read_bytes()

    for row in rows:
        p.require(p.sha(subject_bytes(row["path"])) == row["sha256"],
                  "released source/member changed: " + row["path"])
    manifest = json.loads(subject_bytes(SOURCE_MANIFEST))
    for group in ("sources", "successor_investigation_history", "accepted_successor_sources"):
        for row in manifest[group]:
            p.require(p.sha(subject_bytes(row["path"])) == row["file_sha256"],
                      "released source manifest mismatch: " + row["path"])

    checksum = (p.sha(raw) + "  " + RELEASE + "\n").encode()
    p.require((p.ROOT / CHECKSUM).read_bytes() == checksum, "release checksum changed")
    p.require((p.ROOT / ASSETS / "grc-v4-specification-release.json").read_bytes() == raw and
              (p.ROOT / ASSETS / "grc-v4-specification-release.sha256").read_bytes() == checksum,
              "packaged release changed")
    index_path = ASSETS + "asset-index.json"
    index_bytes = (p.ROOT / index_path).read_bytes()
    # The index is an accepted output too, not merely a freely rehashed roster.
    p.require(index_bytes == historical_blobs([index_path], commit=BASE)[index_path],
              "packaged index changed")
    index = json.loads(index_bytes)
    p.require(index["release_id"] == release["release_id"], "packaged release ID changed")
    for row in index["files"]:
        p.require(p.sha(p.safe_path(p.ROOT, ASSETS + row["name"]).read_bytes()) == row["sha256"],
                  "packaged member changed: " + row["name"])
    tree = ast.parse((p.ROOT / CODEC).read_text())
    pins = {target.id: ast.literal_eval(node.value)
            for node in tree.body if isinstance(node, ast.Assign)
            for target in node.targets if isinstance(target, ast.Name)
            and target.id in {"RELEASE_ID", "_INDEX_SHA256"}}
    p.require(pins == dict(RELEASE_ID=release["release_id"], _INDEX_SHA256=p.sha(index_bytes)),
              "codec release pins changed")
    return dict(release_id=release["release_id"], release_status="unchanged_accepted_release",
                released_proposal_commit=BASE, released_proposal_sha256=p.sha(frozen[PROPOSAL]),
                released_members=len(rows), release_regenerated=False,
                generator_rerun=False, runtime_support_changed=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check-release", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check_release:
        # Normal current-boundary callers also require this exact review draft;
        # the released source and candidate keep separate identities and status.
        proposal_status()
        print("P972A_RELEASE_SUBJECT_PASS release_id=" + verify_release()["release_id"])
    else:
        from verify_p972a_initializer_authority import check
        print(json.dumps(check()))

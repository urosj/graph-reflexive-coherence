"""Portable presentations of selected historical evidence, with Git preimages.

Location changes never replace historical hashes, outcomes or source identities.
The manifest permits only specific original/presented blobs, not arbitrary edits.
"""

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess


PHASE = "implementation/phase-9-grcv4/"
MANIFEST = PHASE + "verification/Phase9PathPresentation.json"
MANIFEST_DIGEST = "e5ebbb8cb9dd3a1fd2bb46687cc624a1faacc712775fed2ba3cff8ed19f4e8f8"
PROFILE = "phase9_repository_locations_v1"
SCRATCH = (
    "implementation/investigations/grc9v4-constitutive-design/"
    "tools/exploratory-side-tool/tool/generated/phase9-portability"
)


def sha(content):
    return hashlib.sha256(content).hexdigest()


def blob_id(content):
    return hashlib.sha1(
        b"blob " + str(len(content)).encode() + b"\0" + content
    ).hexdigest()


def digest(value):
    return sha(json.dumps(value, sort_keys=True, separators=(",", ":")).encode())


def normalize_text(text):
    """Locations are relative to the project root, including recorded cwd/argv.

    External cache, wheel-build and system-font paths are descriptive labels,
    not invented repository inputs. Temporary suffixes keep distinct runs apart.
    """
    home = r"/(?:home|Users)/[^/\s\"'\\]+"
    checkout = home + r"/(?:[^/\s\"'\\]+/)*graph-reflexive-coherence"
    text = re.sub(checkout + r"/", "", text)
    text = re.sub(checkout + r"(?=[\s\"'\\<>]|$)", ".", text)
    text = text.replace(
        "/mnt/data/p931_audit/stress.py",
        PHASE
        + "evidence/P9-3.1/audit-1-inputs/inputs.json#/attachments/2/utf8_content",
    )
    text = text.replace("/tmp/", SCRATCH + "/temporary/")
    text = re.sub(home + r"/\.cache/", "<user-cache>/", text)
    text = re.sub(
        r"/opt/_internal/cpython-[^/\s\"'\\]+/",
        "<numpy-build-environment>/",
        text,
    )
    return text.replace("/usr/share/fonts/", "<system-fonts>/")


def present(content):
    text = normalize_text(content.decode())
    if text == content.decode():
        raise ValueError("presentation requires a location change")
    value = json.loads(text)
    if "path_presentation" in value:
        raise ValueError("input already has a path presentation")
    value["path_presentation"] = MANIFEST
    return (json.dumps(value, indent=2, ensure_ascii=True) + "\n").encode()


def safe_path(root, name):
    path = PurePosixPath(name)
    if path.is_absolute() or ".." in path.parts or str(path) != name:
        raise ValueError("unsafe presentation path")
    result = root / name
    if result.is_symlink() or not result.resolve().is_relative_to(root.resolve()):
        raise ValueError("presentation path escapes repository")
    return result


def load_manifest(root):
    value = json.loads(safe_path(root, MANIFEST).read_bytes())
    if digest(value) != MANIFEST_DIGEST or value["profile"] != PROFILE:
        raise ValueError("untrusted path presentation manifest")
    names = [row["path"] for row in value["files"]]
    if len(names) != len(set(names)) or any(
        not name.startswith(PHASE + "evidence/") for name in names
    ):
        raise ValueError("invalid presentation roster")
    return value


def original_bytes(root, manifest, row):
    content = subprocess.check_output(
        ["git", "show", manifest["source_revision"] + ":" + row["path"]], cwd=root
    )
    if (
        sha(content) != row["original_sha256"]
        or blob_id(content) != row["original_blob"]
    ):
        raise ValueError("historical presentation source mismatch")
    return content


def permits(manifest, name, previous_blob, current_blob):
    return any(
        row["path"] == name
        and (row["original_blob"], row["presented_blob"])
        == (previous_blob, current_blob)
        for row in manifest["files"]
    )


def verify(root, manifest=None):
    root = Path(root)
    manifest = load_manifest(root) if manifest is None else manifest
    if digest(manifest) != MANIFEST_DIGEST:
        raise ValueError("untrusted path presentation manifest")
    for row in manifest["files"]:
        current = safe_path(root, row["path"]).read_bytes()
        if (
            sha(current) != row["presented_sha256"]
            or blob_id(current) != row["presented_blob"]
        ):
            raise ValueError("presented evidence binding mismatch: " + row["path"])
        if present(original_bytes(root, manifest, row)) != current:
            raise ValueError(
                "evidence changed beyond path presentation: " + row["path"]
            )
    return {"profile": PROFILE, "files": len(manifest["files"]), "status": "verified"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--extract-originals",
        help="New repository-relative directory for exact historical replay inputs",
    )
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[3]
    manifest = load_manifest(root)
    result = verify(root, manifest)
    if args.extract_originals:
        output = safe_path(root, args.extract_originals)
        cache = (root / SCRATCH).resolve()
        if not output.resolve().is_relative_to(cache):
            raise ValueError(
                "extract originals under the declared ignored scratch directory"
            )
        output.mkdir(parents=True, exist_ok=False)
        for row in manifest["files"]:
            destination = output / row["path"]
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(original_bytes(root, manifest, row))
        result["extracted_to"] = args.extract_originals
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()

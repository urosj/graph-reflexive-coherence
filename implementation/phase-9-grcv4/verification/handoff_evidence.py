"""Check selected, published execution evidence without rerunning its subject.

This is an integrity/retrieval check, not an acceptance or runtime gate. Generated
debugging attempts remain disposable; only deliberately published evidence is
listed in the manifest. No network service or optional package is needed.
"""

import argparse
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import zipfile


HERE = Path(__file__).resolve().parent
MANIFEST = HERE / "handoff/P9-G1-manifest.json"
MANIFEST_DIGEST = "34e7dfb209be2a42137fd5a17465b481fa3dc45bde63e64d3c71f6d8cb61a37e"
REVIEW_INPUT = "implementation/phase-9-grcv4/verification/inputs/P9-PlanningReview.md"
AUDIT_INPUT = "implementation/phase-9-grcv4/verification/inputs/GRCV4-final-narrow-specification-acceptance-audit.md"
NORMALIZATION = "phase9_machine_locations_v1"


def normalize_text(text):
    """Normalize locations, not outcomes, IDs, hashes, or temporary-root identity."""
    home = r"/(?:home|Users)/[^/\s\"\\]+"
    # Keep checkout roles explicit before resolving external input filenames.
    text = re.sub(
        home + r"/[^\"\\<>\n]*?/graph-reflexive-coherence(?=/|[\s\"\\<>]|$)",
        "<checkout>",
        text,
    )
    # These filenames belong to the two already hash-bound inputs of this
    # selected bundle. Their former parent directories have no significance.
    for filename, target in [
        ("pasted-text.txt", REVIEW_INPUT),
        (PurePosixPath(AUDIT_INPUT).name, AUDIT_INPUT),
    ]:
        text = re.sub(
            home + r"/(?:[^/\"\\<>\n]+/)*" + re.escape(filename) + r"(?=[\s\"\\<>]|$)",
            target,
            text,
        )
    text = re.sub(home + r"(?=/)", "<user-home>", text)
    text = text.replace("/tmp/", "<temporary>/")
    return re.sub(
        r"dependency on a particular user's [^\n]+ directory; the input remains",
        "dependency on machine-local input locations; the input remains",
        text,
    )


def normalize_member(content):
    """Preserve text formatting and historical digest fields; leave binary alone."""
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        return content
    return normalize_text(text).encode("utf-8")


def normalized_snapshot(content):
    """A published presentation, not a replacement historical replay subject."""
    value = json.loads(content)
    for row in value["files"]:
        normalized = normalize_text(row["utf8"])
        if normalized != row["utf8"]:
            row["utf8"] = normalized
            row["normalized_sha256"] = sha(normalized.encode())
    value["normalization"] = {
        "profile": NORMALIZATION,
        "original_sha256": sha(content),
        "hash_semantics": "sha256 and snapshot_digest identify original historical bytes; changed embedded files also have normalized_sha256; unchanged files retain their original bytes",
    }
    return value


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(content):
    return hashlib.sha256(content).hexdigest()


def digest(value, field):
    payload = {k: v for k, v in value.items() if k != field}
    return sha(
        json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode()
    )


def verify(manifest_path=MANIFEST, repo_root=None, original_archive=None):
    """Validate archive bytes and historical input bindings; never run old code."""
    manifest_path = Path(manifest_path)
    require(not manifest_path.is_symlink(), "handoff manifest cannot be a symlink")
    manifest = json.loads(manifest_path.read_bytes())
    require(
        manifest["schema"] == "phase9_selected_execution_evidence_v2"
        and manifest["normalization"]["profile"] == NORMALIZATION,
        "unsupported handoff manifest",
    )
    archive = manifest["archive"]
    require(Path(archive["file"]).name == archive["file"], "unsafe archive path")
    archive_path = manifest_path.parent / archive["file"]
    require(not archive_path.is_symlink(), "handoff archive cannot be a symlink")
    payload = archive_path.read_bytes()
    require(
        len(payload) == archive["bytes"] and sha(payload) == archive["sha256"],
        "handoff archive binding mismatch",
    )
    rows = manifest["artifacts"]
    require(len({r["member"] for r in rows}) == len(rows), "duplicate evidence member")
    contents = {}
    with zipfile.ZipFile(io.BytesIO(payload)) as bundle:
        names = bundle.namelist()
        require(len(names) == len(set(names)), "duplicate archive member")
        require(
            set(names) == {r["member"] for r in rows}, "archive member roster drift"
        )
        for row in rows:
            name = PurePosixPath(row["member"])
            require(
                not name.is_absolute()
                and ".." not in name.parts
                and str(name) == row["member"],
                "unsafe evidence member",
            )
            require(
                bundle.getinfo(str(name)).file_size == row["bytes"],
                "evidence size mismatch: " + str(name),
            )
            content = bundle.read(str(name))
            require(
                sha(content) == row["sha256"], "evidence hash mismatch: " + str(name)
            )
            contents[str(name)] = content
            require(
                normalize_member(content) == content,
                "machine-local path in published evidence: " + str(name),
            )
    for subject in manifest["subjects"]:
        receipt = json.loads(contents[subject["receipt"]])
        report = json.loads(contents[subject["pressure_report"]])
        require(
            receipt["receipt_digest"] == subject["receipt_digest"],
            "historical receipt identity mismatch",
        )
        require(
            report["report_digest"] == subject["report_digest"]
            and report["run_id"] == subject["run_id"],
            "historical pressure identity mismatch",
        )
        require(
            digest(receipt, "receipt_digest") == subject["normalized_receipt_digest"]
            and digest(report, "report_digest") == subject["normalized_report_digest"],
            "normalized execution digest mismatch",
        )
        require(
            receipt["policy_digest"]
            == report["policy_digest"]
            == subject["policy_digest"]
            and receipt["tree"] == report["tree"] == subject["tree"],
            "historical input identity mismatch",
        )
        require(
            receipt["status"] == "passed"
            and all(c["exit_code"] == 0 for c in receipt["commands"]),
            "selected receipt is not a passing execution",
        )
        require(
            report.get("failed", 0) == 0
            and report.get("passed", report.get("passed_count"))
            == len(report["cases"]),
            "selected pressure report is not a passing execution",
        )
        inputs = {
            r["path"]: r["sha256"]
            for r in manifest["input_bindings"]
            if r["revision"] == subject["source_revision"]
        }
        tree_rows = [{"path": n, "sha256": inputs[n]} for n in subject["tree_paths"]]
        require(
            subject["tree_paths"] == sorted(set(subject["tree_paths"])),
            "historical input roster drift",
        )
        require(
            sha(
                json.dumps(
                    tree_rows, sort_keys=True, separators=(",", ":"), ensure_ascii=False
                ).encode()
            )
            == subject["tree"]["current_artifact_digest"],
            "historical input tree mismatch",
        )
    if repo_root is not None:
        # Read exact historical Git blobs, not today's checker or a fresh rerun.
        bindings = manifest["input_bindings"]
        queries = [r["revision"] + ":" + r["path"] for r in bindings]
        require(all("\n" not in q for q in queries), "invalid Git input locator")
        result = subprocess.run(
            ["git", "cat-file", "--batch"],
            cwd=repo_root,
            input=("\n".join(queries) + "\n").encode(),
            capture_output=True,
            check=True,
        )
        stream = io.BytesIO(result.stdout)
        for row in bindings:
            header = stream.readline().split()
            require(
                len(header) == 3 and header[1] == b"blob",
                "historical input unavailable",
            )
            content = stream.read(int(header[2]))
            require(
                stream.read(1) == b"\n" and sha(content) == row["sha256"],
                "historical input binding mismatch: " + row["path"],
            )
        require(stream.read() == b"", "unexpected historical input data")
    require(
        digest(manifest, "manifest_digest") == MANIFEST_DIGEST,
        "handoff manifest identity mismatch",
    )
    if original_archive is not None:
        original = Path(original_archive).read_bytes()
        require(
            sha(original) == archive["original_sha256"]
            and len(original) == archive["original_bytes"],
            "original archive binding mismatch",
        )
        with zipfile.ZipFile(io.BytesIO(original)) as bundle:
            require(
                sorted(bundle.namelist()) == sorted(contents),
                "original archive roster mismatch",
            )
            for row in rows:
                raw = bundle.read(row["member"])
                require(
                    sha(raw) == row["original_sha256"]
                    and len(raw) == row["original_bytes"]
                    and normalize_member(raw) == contents[row["member"]],
                    "path-only normalization mismatch: " + row["member"],
                )
    return {
        "artifacts": len(rows),
        "subjects": len(manifest["subjects"]),
        "archive_sha256": archive["sha256"],
        "original_archive_sha256": archive["original_sha256"],
        "original_bytes_verified": original_archive is not None,
        "new_acceptance": False,
    }


def status(repo_root, manifest_path=MANIFEST):
    """Report archive integrity independently of any implementation authority."""
    try:
        return {"status": "verified", **verify(manifest_path, repo_root)}
    except (FileNotFoundError, PermissionError):
        return {
            "status": "unavailable",
            "detail": "Selected handoff files are unavailable; no archive integrity pass is claimed.",
        }
    except (
        ValueError,
        KeyError,
        TypeError,
        OSError,
        zipfile.BadZipFile,
        subprocess.CalledProcessError,
    ):
        return {
            "status": "invalid",
            "detail": "Selected handoff evidence failed integrity/retrieval verification; run handoff_evidence.py for details.",
        }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--repo-root", type=Path, default=HERE.parents[2])
    parser.add_argument("--original-archive", type=Path)
    args = parser.parse_args()
    result = verify(args.manifest, args.repo_root, args.original_archive)
    print("PHASE9_HANDOFF_EVIDENCE_PASS " + json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()

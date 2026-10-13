"""Lossless storage for large evidence; expanded files are local, ignored data."""

from __future__ import annotations

import argparse
import bz2
import gzip
import hashlib
import io
import json
import lzma
import os
import re
import subprocess
import tempfile
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = "artifact-storage.json"
LIMIT = 1_000_000  # Compress new/changed raw files above decimal 1 MB.


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def safe_path(root: Path, name: str) -> Path:
    require(type(name) is str and bool(name), "invalid artifact path")
    path = PurePosixPath(name)
    require(
        not path.is_absolute() and ".." not in path.parts and all(ord(c) >= 32 for c in name)
        and str(path) == name and "\\" not in name,
        "repository-relative artifact path required",
    )
    target = root.resolve() / name
    require(target.resolve() == target and not target.is_symlink(), "artifact symlink")
    return target


def entries(root: Path) -> list[dict]:
    value = json.loads(safe_path(root, MANIFEST).read_bytes())
    legacy = (
        set(value) == {"schema", "max_git_file_bytes", "files"}
        and value["schema"] == "exact-evidence-storage-v1"
        and type(value["max_git_file_bytes"]) is int
        and value["max_git_file_bytes"] == 10_000_000
    )
    require(legacy or (
        set(value) == {"schema", "compression_threshold_bytes", "files"}
        and value["schema"] == "exact-evidence-storage-v2"
        and type(value["compression_threshold_bytes"]) is int
        and value["compression_threshold_bytes"] == LIMIT),
        "unsupported evidence storage manifest",
    )
    rows = value["files"]
    require(type(rows) is list, "invalid storage roster")
    names: set[str] = set()
    for row in rows:
        require(
            type(row) is dict and set(row) == {
                "path", "size", "sha256", "storage_path", "storage_size",
                "storage_sha256",
            },
            "invalid storage entry",
        )
        for key in ("path", "storage_path"):
            safe_path(root, row[key])
        require(row["storage_path"] == row["path"] + ".xz", "archive path mismatch")
        require(not names.intersection((row["path"], row["storage_path"])), "duplicate artifact")
        names.update((row["path"], row["storage_path"]))
        require(
            type(row["size"]) is int and row["size"] > LIMIT
            and type(row["storage_size"]) is int and row["storage_size"] > 0,
            "invalid artifact size",
        )
        for key in ("sha256", "storage_sha256"):
            require(type(row[key]) is str and re.fullmatch(r"[0-9a-f]{64}", row[key]), "invalid hash")
    return rows


def packed_bytes(root: Path, row: dict) -> bytes:
    data = safe_path(root, row["storage_path"]).read_bytes()
    require(len(data) == row["storage_size"] and sha(data) == row["storage_sha256"],
            "compressed evidence drift: " + row["storage_path"])
    return data


def unpack(data: bytes, row: dict) -> bytes:
    decoder = lzma.LZMADecompressor(format=lzma.FORMAT_XZ, memlimit=128 * 1024**2)
    raw = decoder.decompress(data, max_length=row["size"] + 1)
    require(decoder.eof and not decoder.unused_data, "truncated or trailing archive data")
    require(len(raw) == row["size"] and sha(raw) == row["sha256"],
            "expanded evidence drift: " + row["path"])
    return raw


def check_expanded(path: Path, row: dict) -> None:
    require(path.stat().st_size == row["size"] and sha(path.read_bytes()) == row["sha256"],
            "existing expanded evidence drift; refusing overwrite: " + row["path"])


def write_metadata(path: Path, text: str) -> None:
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
        temporary = Path(stream.name)
        stream.write(text.encode())
        stream.flush()
        os.fsync(stream.fileno())
    try:
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def restore(root: Path = ROOT, *, prefix: str = "") -> dict:
    """Restore missing files atomically; never overwrite an edited local result.

    Existing files and compressed sources are authenticated on every call.
    The separate verify command always decompresses every archive as well.
    """
    root = Path(root)
    rows = [row for row in entries(root) if row["path"].startswith(prefix)]
    restored = 0
    for row in rows:
        packed = packed_bytes(root, row)
        path = safe_path(root, row["path"])
        if path.exists():
            check_expanded(path, row)
            continue
        raw = unpack(packed, row)
        path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        try:
            try:
                os.link(temporary, path)
                restored += 1
            except FileExistsError:
                # Another reader may have restored the same checked evidence.
                safe_path(root, row["path"])
                check_expanded(path, row)
        finally:
            temporary.unlink()
    return {"files": len(rows), "restored": restored}


def verify(root: Path = ROOT) -> dict:
    root = Path(root)
    rows = entries(root)
    for row in rows:
        unpack(packed_bytes(root, row), row)
        path = safe_path(root, row["path"])
        if path.exists():
            check_expanded(path, row)
    return {"files": len(rows), "original_bytes": sum(r["size"] for r in rows),
            "stored_bytes": sum(r["storage_size"] for r in rows), "byte_exact": True}


def git_size_check(root: Path = ROOT) -> dict:
    """Check new/changed staged blobs; unchanged HEAD subjects are grandfathered.

Compressed files may exceed LIMIT. Validate the staged bytes, not just a suffix
or a smaller working copy. No historical Git objects are rewritten.
"""
    root = Path(root)
    head = subprocess.run(["git", "rev-parse", "--verify", "HEAD"], cwd=root, capture_output=True)
    previous = {}
    if head.returncode == 0:
        tree = subprocess.run(["git", "ls-tree", "-rz", "HEAD"], cwd=root, check=True, capture_output=True)
        for entry in filter(None, tree.stdout.split(b"\0")):
            metadata, name = entry.split(b"\t", 1)
            _, kind, oid = metadata.decode().split()
            if kind == 'blob':
                previous[name.decode()] = oid
    result = subprocess.run(["git", "ls-files", "--stage", "-z"], cwd=root,
                            check=True, capture_output=True)
    blobs: dict[str, list[str]] = {}
    for entry in filter(None, result.stdout.split(b"\0")):
        metadata, name = entry.split(b"\t", 1)
        mode, oid, stage = metadata.decode().split()
        require(stage == "0", "unmerged index entry: " + name.decode())
        if mode != "160000":  # Submodules refer to commits, not file blobs.
            if previous.get(name.decode()) != oid:
                blobs.setdefault(oid, []).append(name.decode())
    result = subprocess.run(["git", "cat-file", "--batch-check=%(objectname) %(objectsize)"],
                            input="\n".join(blobs) + ("\n" if blobs else ""), cwd=root,
                            check=True, capture_output=True, text=True)
    oversized = []
    for line in result.stdout.splitlines():
        oid, size = line.split()
        if int(size) > LIMIT:
            data = subprocess.run(['git', 'cat-file', 'blob', oid], cwd=root, check=True, capture_output=True).stdout
            for name in blobs[oid]:
                if not valid_compressed(name, data):
                    oversized.append(f"{name} ({size} bytes)")
    require(not oversized, "New/changed raw Git files exceed compression threshold:\n" + "\n".join(oversized))
    return {"changed_git_files": sum(map(len, blobs.values())), "compression_threshold_bytes": LIMIT,
            "compressed_size_limited": False}


def valid_compressed(name: str, data: bytes) -> bool:
    """Recognized lossless containers, not a rename-based size-gate bypass."""
    try:
        if name.endswith('.xz'):
            remaining = data
            if not remaining:
                return False
            while remaining:
                decoder = lzma.LZMADecompressor(format=lzma.FORMAT_XZ)
                decoder.decompress(remaining)
                if not decoder.eof:
                    return False
                remaining = decoder.unused_data
        elif name.endswith(('.gz', '.tgz')):
            gzip.decompress(data)
        elif name.endswith(('.bz2', '.tbz2')):
            remaining = data
            if not remaining:
                return False
            while remaining:
                decoder = bz2.BZ2Decompressor()
                decoder.decompress(remaining)
                if not decoder.eof:
                    return False
                remaining = decoder.unused_data
        elif name.endswith('.zip'):
            with zipfile.ZipFile(io.BytesIO(data)) as archive:
                if archive.testzip() is not None:
                    return False
        else:
            return False
        return True
    except (OSError, EOFError, ValueError, RuntimeError, zipfile.BadZipFile, lzma.LZMAError):
        return False


def pack(root: Path, names: list[str]) -> dict:
    """Pack explicit new results; never rewrite a registered scientific subject."""
    root = Path(root)
    manifest = safe_path(root, MANIFEST)
    rows = entries(root) if manifest.exists() else []
    registered = {r["path"]: r for r in rows}
    for name in names:
        source = safe_path(root, name)
        if name in registered:
            check_expanded(source, registered[name])
            unpack(packed_bytes(root, registered[name]), registered[name])
            continue
        raw = source.read_bytes()
        require(len(raw) > LIMIT, "artifact does not exceed compression threshold: " + name)
        require(not valid_compressed(name, raw), "already compressed: " + name)
        packed = lzma.compress(raw, preset=6)
        destination = safe_path(root, name + ".xz")
        row = {"path": name, "size": len(raw), "sha256": sha(raw),
               "storage_path": name + ".xz", "storage_size": len(packed),
               "storage_sha256": sha(packed)}
        require(unpack(packed, row) == raw, "archive round-trip failed")
        if destination.exists():
            # A previous interrupted pack may have written this exact archive.
            require(destination.read_bytes() == packed, "existing archive differs")
        else:
            with destination.open("xb") as stream:
                stream.write(packed)
        rows.append(row)
        registered[name] = row
    value = {"schema": "exact-evidence-storage-v2", "compression_threshold_bytes": LIMIT,
             "files": sorted(rows, key=lambda r: r["path"])}
    write_metadata(manifest, json.dumps(value, indent=2) + "\n")
    ignore = safe_path(root, ".gitignore")
    content = ignore.read_text() if ignore.exists() else ""
    additions = []
    for row in rows:
        name = row["path"]
        for token in ("[", "]", "*", "?"):
            name = name.replace(token, "\\" + token)
        rule = "/" + name
        if rule not in content.splitlines():
            additions.append(rule)
    if additions:
        write_metadata(ignore, content.rstrip() + "\n\n# Expanded evidence; see artifact-storage.json\n"
                       + "\n".join(additions) + "\n")
    return {"files": len(rows), "stored_bytes": sum(r["storage_size"] for r in rows),
            "next_step": "For previously tracked raw files, git rm --cached -- <path>; keep the local file."}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("restore", "verify", "check", "pack"))
    parser.add_argument("paths", nargs="*")
    args = parser.parse_args()
    if args.action == "pack":
        if not args.paths:
            parser.error("pack requires explicit artifact paths")
        print(json.dumps(pack(ROOT, args.paths), indent=2))
        return
    if args.paths:
        parser.error("paths apply only to pack")
    result = restore() if args.action == "restore" else verify()
    if args.action == "check":
        result.update(git_size_check())
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

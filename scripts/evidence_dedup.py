"""Content-addressed JSON storage; original record and XZ identities survive.

Only byte-round-trippable minified JSON is admitted by the writer. Readers
assemble stored byte fragments, never reserialize numbers or run model code.
"""
from __future__ import annotations

from collections import OrderedDict
import hashlib
import io
import json
import lzma
from pathlib import Path, PurePosixPath
import re
import zipfile

SCHEMA = "exact-json-object-store-v1"
HASH = re.compile(r"[0-9a-f]{64}")
ROW_KEYS = {"path", "size", "sha256", "storage_path", "storage_size", "storage_sha256"}
CACHE_BYTES = 64 * 1024**2


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def path(root, name):
    require(type(name) is str and bool(name), "invalid shared-storage path")
    p = PurePosixPath(name)
    require(not p.is_absolute() and ".." not in p.parts and str(p) == name
            and "\\" not in name and all(ord(c) >= 32 for c in name), "unsafe shared-storage path")
    target = Path(root).resolve() / name
    require(target.resolve() == target and not target.is_symlink(), "shared-storage symlink")
    return target


def dumps(value):
    return json.dumps(value, ensure_ascii=True, allow_nan=False, separators=(",", ":")).encode()


def add(parts, part):
    if type(part) is str and parts and type(parts[-1]) is str:
        parts[-1] += part
    else:
        parts.append(part)


class Builder:
    def __init__(self, archive, minimum):
        self.archive, self.minimum = archive, minimum
        self.seen = set()

    def node(self, raw, parts=None, *, force=False):
        if not force and len(raw) < self.minimum:
            return raw, raw.decode("utf-8")
        # Object hashes address stored fragments/recipes, not approximate values.
        encoded = b"R" + dumps(parts) if parts and any(type(x) is dict for x in parts) else b"L" + raw
        key = sha(encoded)
        if key not in self.seen:
            info = zipfile.ZipInfo("objects/" + key, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_STORED
            info.external_attr = 0o100644 << 16
            self.archive.writestr(info, encoded)
            self.seen.add(key)
        return raw, {"ref": key}

    def encode(self, value):
        if not isinstance(value, (dict, list)) or (
                isinstance(value, list) and all(not isinstance(x, (dict, list)) for x in value)):
            return self.node(dumps(value))
        parts, raw = [], []
        opening, closing = ("{", "}") if isinstance(value, dict) else ("[", "]")
        add(parts, opening); raw.append(opening.encode())
        for i, item in enumerate(value.items() if isinstance(value, dict) else value):
            if i:
                add(parts, ","); raw.append(b",")
            if isinstance(value, dict):
                key, item = item
                prefix = dumps(key) + b":"
                add(parts, prefix.decode()); raw.append(prefix)
            child, token = self.encode(item)
            add(parts, token); raw.append(child)
        add(parts, closing); raw.append(closing.encode())
        return self.node(b"".join(raw), parts)

    def record(self, raw):
        value = json.loads(raw)
        body, token = self.encode(value)
        suffix = raw[len(body):]
        require(raw == body + suffix and suffix in (b"", b"\n"),
                "JSON is not byte-round-trippable minified ASCII serialization")
        # Compare the body explicitly: equal lengths alone cannot normalize input.
        require(raw[:len(body)] == body, "JSON serialization would change original bytes")
        _, root = self.node(raw, [token, suffix.decode()], force=True)
        return root["ref"]


class Store:
    """Authenticated immutable store, with a bounded byte cache per operation."""
    def __init__(self, root, descriptor, rows):
        require(set(descriptor) == {"path", "sha256"} and HASH.fullmatch(descriptor["sha256"]),
                "invalid object-store descriptor")
        self.root = Path(root).resolve()
        raw = path(root, descriptor["path"]).read_bytes()
        self.manifest_size = len(raw)
        require(sha(raw) == descriptor["sha256"], "object-store manifest drift")
        self.manifest = m = json.loads(raw)
        require(set(m) == {"schema", "minimum_object_bytes", "archive", "records"}
                and m["schema"] == SCHEMA and type(m["minimum_object_bytes"]) is int
                and m["minimum_object_bytes"] > 0 and type(m["records"]) is list,
                "invalid object-store schema")
        a = m["archive"]
        require(set(a) == {"path", "size", "sha256", "objects", "expanded_size"}
                and type(a["size"]) is int and a["size"] > 0
                and type(a["expanded_size"]) is int and a["expanded_size"] > 0
                and type(a["objects"]) is int and a["objects"] > 0
                and HASH.fullmatch(a["sha256"]), "invalid object archive descriptor")
        packed = path(root, a["path"]).read_bytes()
        require(len(packed) == a["size"] and sha(packed) == a["sha256"], "object archive drift")
        decoder = lzma.LZMADecompressor(format=lzma.FORMAT_XZ, memlimit=128 * 1024**2)
        expanded = decoder.decompress(packed, max_length=a["expanded_size"] + 1)
        require(decoder.eof and not decoder.unused_data and len(expanded) == a["expanded_size"],
                "invalid shared archive size/termination")
        self.archive = zipfile.ZipFile(io.BytesIO(expanded))
        members = self.archive.infolist()
        require(len(members) == a["objects"] and len({x.filename for x in members}) == len(members)
                and all(x.filename.startswith("objects/") and HASH.fullmatch(x.filename[8:])
                        and x.compress_type == zipfile.ZIP_STORED
                        and not x.is_dir() and not x.flag_bits & 1 for x in members), "object member roster drift")
        known = {r["path"]: r for r in rows}
        self.records = {}
        for r in m["records"]:
            require(type(r) is dict and set(r) == ROW_KEYS | {"root"}
                    and type(r["root"]) is str and HASH.fullmatch(r["root"]), "invalid shared record")
            require(r["path"] in known and {k: r[k] for k in ROW_KEYS} == known[r["path"]],
                    "shared record changed original identity")
            require(r["path"] not in self.records and "objects/" + r["root"] in self.archive.namelist(),
                    "duplicate or absent shared record")
            self.records[r["path"]] = r
        require(bool(self.records), "empty shared store")
        self.cache, self.cache_bytes = OrderedDict(), 0

    def _object(self, key, limit):
        require(type(key) is str and HASH.fullmatch(key), "invalid object reference")
        if key in self.cache:
            value = self.cache.pop(key); self.cache[key] = value
            return value
        try:
            info = self.archive.getinfo("objects/" + key)
        except KeyError as exc:
            raise ValueError("missing shared object " + key) from exc
        # A recipe can contain escaped literals; bound decoding before allocating.
        require(0 < info.file_size <= 8 * limit + 4096, "oversized object")
        value = self.archive.read(info)
        require(sha(value) == key, "shared object hash mismatch")
        while self.cache and self.cache_bytes + len(value) > CACHE_BYTES:
            _, old = self.cache.popitem(last=False); self.cache_bytes -= len(old)
        if len(value) <= CACHE_BYTES:
            self.cache[key] = value; self.cache_bytes += len(value)
        return value

    def _expand(self, key, active, limit):
        require(key not in active and len(active) < 128, "cyclic or excessively deep object recipe")
        value = self._object(key, limit)
        if value[:1] == b"L":
            result = value[1:]
        else:
            require(value[:1] == b"R", "unknown object encoding")
            parts = json.loads(value[1:])
            require(type(parts) is list and bool(parts), "invalid object recipe")
            chunks, size = [], 0
            for part in parts:
                if type(part) is str:
                    chunk = part.encode("utf-8")
                else:
                    require(type(part) is dict and set(part) == {"ref"}, "invalid recipe reference")
                    chunk = self._expand(part["ref"], active | {key}, limit - size)
                size += len(chunk)
                require(size <= limit, "expanded recipe exceeds original size")
                chunks.append(chunk)
            result = b"".join(chunks)
        require(len(result) <= limit, "object exceeds original size")
        return result

    def raw(self, row):
        r = self.records[row["path"]]
        raw = self._expand(r["root"], set(), row["size"])
        require(len(raw) == row["size"] and sha(raw) == row["sha256"], "reconstructed record drift")
        return raw

    def xz(self, row, raw=None):
        raw = self.raw(row) if raw is None else raw
        packed = lzma.compress(raw, format=lzma.FORMAT_XZ, check=lzma.CHECK_CRC64, preset=6)
        require(len(packed) == row["storage_size"] and sha(packed) == row["storage_sha256"],
                "XZ encoder cannot reproduce original transport identity; JSON record remains exact")
        return packed


def build(root, rows, directory, *, minimum=4096):
    """Write a new immutable store; publication/registration is the caller's step."""
    require(type(minimum) is int and minimum > 0 and bool(rows), "invalid deduplication request")
    folder = path(root, directory)
    require(not folder.exists(), "refusing to overwrite an existing object store")
    folder.mkdir(parents=True)
    archive_path = directory + "/objects.zip.xz"
    manifest_path = directory + "/records.json"
    refs = []
    try:
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as archive:
            builder = Builder(archive, minimum)
            for row in rows:
                packed = path(root, row["storage_path"]).read_bytes()
                require(len(packed) == row["storage_size"] and sha(packed) == row["storage_sha256"],
                        "original archive drift")
                raw = lzma.decompress(packed)
                require(len(raw) == row["size"] and sha(raw) == row["sha256"], "original record drift")
                refs.append(dict(row, root=builder.record(raw)))
            count = len(builder.seen)
        expanded = buffer.getvalue()
        packed = lzma.compress(expanded, preset=6)
        path(root, archive_path).write_bytes(packed)
        manifest = dict(schema=SCHEMA, minimum_object_bytes=minimum,
                        archive=dict(path=archive_path, size=len(packed), sha256=sha(packed),
                                     objects=count, expanded_size=len(expanded)),
                        records=refs)
        path(root, manifest_path).write_bytes(dumps(manifest) + b"\n")
        descriptor = dict(path=manifest_path, sha256=sha(path(root, manifest_path).read_bytes()))
        store = Store(root, descriptor, rows)
        for row in rows:
            raw = store.raw(row)
            require(store.xz(row, raw) == path(root, row["storage_path"]).read_bytes(),
                    "original XZ round trip failed")
        return descriptor
    except Exception:
        # Only files created by this unsuccessful writer are removed.
        for name in (archive_path, manifest_path):
            path(root, name).unlink(missing_ok=True)
        folder.rmdir()
        raise

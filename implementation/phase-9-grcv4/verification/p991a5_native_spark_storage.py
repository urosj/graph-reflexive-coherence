"""Lossless archive repacking; preserve the original execution record verbatim."""

import argparse
import json
import lzma
import tempfile
import time
from copy import deepcopy
from hashlib import sha256
from pathlib import Path

from p991a5_native_spark_campaign import BASE, FILES, HERE, RECORD, ROOT, seal
from p991a5_native_spark_verify import need

SELF = HERE + "p991a5_native_spark_storage.py"
EXECUTION = BASE + "P9-9.1a.5-Execution.json"
PRESET = 4


def expanded_digest(path):
    digest, size = sha256(), 0
    with lzma.open(path, "rb") as stream:
        for raw in iter(lambda: stream.read(2**20), b""):
            digest.update(raw)
            size += len(raw)
    return {"bytes": size, "sha256": digest.hexdigest()}


def check(root=ROOT):
    root = Path(root)
    value = json.loads((root / RECORD).read_bytes())
    original_raw = (root / EXECUTION).read_bytes()
    original = json.loads(original_raw)
    need(
        value == seal(value) and original == seal(original),
        "unsealed storage provenance",
    )
    packaging = value["storage_repack"]
    need(
        packaging["schema"] == "native-cos-lossless-storage-v1"
        and packaging["preset"] == PRESET
        and packaging["execution_record_digest"] == original["record_digest"]
        and packaging["path"] == FILES["reset"],
        "changed repacking scope",
    )
    extra = [
        {"path": EXECUTION, "sha256": sha256(original_raw).hexdigest()},
        {"path": SELF, "sha256": sha256((root / SELF).read_bytes()).hexdigest()},
    ]
    restored = deepcopy(value)
    restored.pop("storage_repack")
    need(
        restored["source_bindings"] == original["source_bindings"] + extra,
        "changed execution sources",
    )
    restored["source_bindings"] = original["source_bindings"]
    for old, new in zip(original["streams"], restored["streams"], strict=True):
        raw = (root / new["path"]).read_bytes()
        need(
            len(raw) == new["compressed_bytes"]
            and sha256(raw).hexdigest() == new["sha256"],
            "changed archive",
        )
        if new["path"] == packaging["path"]:
            need(old == packaging["original_stream"], "changed original stream")
            need(
                expanded_digest(root / new["path"]) == packaging["expanded"],
                "changed expanded trace",
            )
            new.update(sha256=old["sha256"], compressed_bytes=old["compressed_bytes"])
        need(new == old, "changed trace chain or scope")
    need(seal(restored) == original, "repacking changed execution results")
    return value


def repack():
    started = time.perf_counter()
    need(not (ROOT / EXECUTION).exists(), "execution provenance already retained")
    original_raw = (ROOT / RECORD).read_bytes()
    original = json.loads(original_raw)
    need(original == seal(original), "unsealed original execution")
    row = next(r for r in original["streams"] if r["path"] == FILES["reset"])
    path = ROOT / row["path"]
    need(
        sha256(path.read_bytes()).hexdigest() == row["sha256"],
        "changed original archive",
    )
    digest, size = sha256(), 0
    with tempfile.NamedTemporaryFile(
        dir=path.parent, prefix=".p991a5-", suffix=".xz.tmp", delete=False
    ) as temporary:
        target = Path(temporary.name)
    try:
        with (
            lzma.open(path, "rb") as source,
            lzma.open(target, "wb", preset=PRESET) as destination,
        ):
            for raw in iter(lambda: source.read(2**20), b""):
                need(
                    time.perf_counter() - started < 600,
                    "storage repack exceeded ten-minute cap",
                )
                digest.update(raw)
                size += len(raw)
                destination.write(raw)
        expanded = {"bytes": size, "sha256": digest.hexdigest()}
        need(expanded_digest(target) == expanded, "lossless re-encoding failed")
        packed = target.read_bytes()
        need(
            len(packed) < 100 * 2**20 and len(packed) < row["compressed_bytes"],
            "archive remains too large",
        )
        value = deepcopy(original)
        new = next(r for r in value["streams"] if r["path"] == row["path"])
        new.update(sha256=sha256(packed).hexdigest(), compressed_bytes=len(packed))
        value["source_bindings"].extend(
            [
                {"path": EXECUTION, "sha256": sha256(original_raw).hexdigest()},
                {
                    "path": SELF,
                    "sha256": sha256((ROOT / SELF).read_bytes()).hexdigest(),
                },
            ]
        )
        value["storage_repack"] = {
            "schema": "native-cos-lossless-storage-v1",
            "preset": PRESET,
            "path": row["path"],
            "original_stream": row,
            "expanded": expanded,
            "execution_record_digest": original["record_digest"],
            "elapsed_seconds": time.perf_counter() - started,
            "numerical_steps_executed": 0,
        }
        (ROOT / EXECUTION).write_bytes(original_raw)
        target.replace(path)
        (ROOT / RECORD).write_text(json.dumps(seal(value), indent=2) + "\n")
    finally:
        target.unlink(missing_ok=True)
    return check()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--repack", action="store_true")
    args = parser.parse_args()
    result = repack() if args.repack else check()
    print(json.dumps(result["storage_repack"]))

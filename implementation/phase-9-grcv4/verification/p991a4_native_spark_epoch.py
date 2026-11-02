"""Finite metadata succession after committed native lifecycle verification."""

import json
import subprocess
from functools import lru_cache
from hashlib import sha256
from pathlib import Path

REVISION = "59c35997"
HERE = "implementation/phase-9-grcv4/verification/"
SIDE = "implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool/"
SELF = HERE + "p991a4_native_spark_epoch.py"
PATH = "implementation/phase-9-grcv4/tranche-9/P9-9.1a.4-SourceEpoch.json"
CHANGED = frozenset(
    {
        HERE + "p991a3_native_spark_epoch.py",
        HERE + "p991a3_native_spark_lifecycle.py",
        SIDE + "src/grcv4_explorer/basin.py",
        SIDE + "src/grcv4_explorer/spark_earlier_sc3_metadata.py",
    }
)


def sha(raw):
    return sha256(raw).hexdigest()


@lru_cache(maxsize=8)
def original(root, name):
    return subprocess.check_output(["git", "show", REVISION + ":" + name], cwd=root)


def seal(value):
    body = {k: v for k, v in value.items() if k != "record_digest"}
    return dict(
        body,
        record_digest=sha(
            json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
        ),
    )


def manifest(root):
    from p991a5_native_spark_epoch import previous_bytes as campaign_previous
    root = Path(root).resolve()
    return seal(
        {
            "schema": "p991a4-native-spark-metadata-epoch-v1",
            "predecessor": REVISION,
            "checker_sha256": sha(campaign_previous(root, SELF)),
            "sources": {
                name: {
                    "before_sha256": sha(original(root, name)),
                    "after_sha256": sha(campaign_previous(root, name)),
                }
                for name in sorted(CHANGED)
            },
            "runtime_changed": False,
            "old_execution_relabelled": False,
        }
    )


def previous_bytes(root, name):
    from p991a5_native_spark_epoch import previous_bytes as campaign_previous
    root = Path(root).resolve()
    if name not in CHANGED:
        return campaign_previous(root, name)
    if json.loads((root / PATH).read_bytes()) != manifest(root):
        raise ValueError("unbound native preflight metadata successor")
    return original(root, name)

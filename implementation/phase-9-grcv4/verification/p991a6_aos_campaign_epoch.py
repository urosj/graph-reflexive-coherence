"""Finite A_OS campaign publication successor; historical execution stays pinned."""

import json
import subprocess
from functools import lru_cache
from hashlib import sha256
from pathlib import Path

REVISION = "5aea075a"
HERE = "implementation/phase-9-grcv4/verification/"
SIDE = "implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool/"
SELF = HERE + "p991a6_aos_campaign_epoch.py"
PATH = "implementation/phase-9-grcv4/tranche-9/P9-9.1a.6-AOS.5-SourceEpoch.json"
CHANGED = frozenset(
    {
        HERE + "p991a6_aos_epoch.py",
        SIDE + "src/grcv4_explorer/spark_earlier_sc3_metadata.py",
    }
)


def sha(raw):
    return sha256(raw).hexdigest()


@lru_cache(maxsize=32)
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
    root = Path(root).resolve()
    return seal(
        {
            "schema": "p991a6-aos-campaign-epoch-v1",
            "predecessor": REVISION,
            "checker_sha256": sha((root / SELF).read_bytes()),
            "sources": {
                name: {
                    "before_sha256": sha(original(root, name)),
                    "after_sha256": sha((root / name).read_bytes()),
                }
                for name in sorted(CHANGED)
            },
            "runtime_changed": False,
            "old_execution_relabelled": False,
        }
    )


def previous_bytes(root, name):
    root = Path(root).resolve()
    if name not in CHANGED:
        return (root / name).read_bytes()
    if json.loads((root / PATH).read_bytes()) != manifest(root):
        raise ValueError("unbound A_OS campaign publication successor")
    return original(root, name)

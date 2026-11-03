"""Finite public-duration/campaign successor; accepted execution stays pinned."""

import json
import subprocess
from functools import lru_cache
from hashlib import sha256
from pathlib import Path

REVISION = "7152812a"
HERE = "implementation/phase-9-grcv4/verification/"
SIDE = "implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool/"
SELF = HERE + "p991a6_rg2b_campaign_epoch.py"
PATH = "implementation/phase-9-grcv4/tranche-9/P9-9.1a.6-RG2b.5-SourceEpoch.json"
CHANGED = frozenset(
    {
        HERE + "p991a5_native_spark_compact_epoch.py",
        HERE + "crg2b_native_spark_oracle.py",
        "src/pygrc/models/grc_9_v4.py",
        "src/pygrc/models/grc_9_v4_api_lifecycle.py",
        SIDE + "src/grcv4_explorer/spark_earlier_sc3_metadata.py",
        SIDE + "src/grcv4_explorer/spark_native_arg2b.py",
        SIDE + "src/grcv4_explorer/spark_native_arg2b_pressure.py",
        SIDE + "scripts/serve_phase9.py",
    }
)


def sha(raw):
    return sha256(raw).hexdigest()


def seal(value):
    body = {k: v for k, v in value.items() if k != "record_digest"}
    return dict(
        body,
        record_digest=sha(
            json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
        ),
    )


@lru_cache(maxsize=32)
def original(root, name):
    return subprocess.check_output(["git", "show", REVISION + ":" + name], cwd=root)


def manifest(root):
    root = Path(root).resolve()
    return seal(
        {
            "schema": "p991a6-rg2b-campaign-runtime-epoch-v1",
            "predecessor": REVISION,
            "checker_sha256": sha((root / SELF).read_bytes()),
            "sources": {
                p: {
                    "before_sha256": sha(original(root, p)),
                    "after_sha256": sha((root / p).read_bytes()),
                }
                for p in sorted(CHANGED)
            },
            "runtime_changed": True,
            "old_execution_relabelled": False,
        }
    )


def previous_bytes(root, name):
    root = Path(root).resolve()
    if name not in CHANGED:
        return (root / name).read_bytes()
    value = json.loads((root / PATH).read_bytes())
    raw = original(root, name)
    if (
        value != seal(value)
        or value["schema"] != "p991a6-rg2b-campaign-runtime-epoch-v1"
        or value["predecessor"] != REVISION
        or set(value["sources"]) != CHANGED
        or value["checker_sha256"] != sha((root / SELF).read_bytes())
        or value["runtime_changed"] is not True
        or value["old_execution_relabelled"] is not False
        or value["sources"][name]
        != {"before_sha256": sha(raw), "after_sha256": sha((root / name).read_bytes())}
    ):
        raise ValueError("unbound RG2b campaign successor")
    return raw

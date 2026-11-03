"""Finite regression-publication successor; native execution bytes unchanged."""

import json
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import subprocess

REVISION = "f41346da"
HERE = "implementation/phase-9-grcv4/verification/"
SIDE = "implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool/"
SELF = HERE + "p9103_native_spark_epoch.py"
PATH = "implementation/phase-9-grcv4/tranche-10/P9-10.3-NativeSpark-SourceEpoch.json"
CHANGED = frozenset(
    {
        HERE + "p991a7_support_epoch.py",
        HERE + "p991a5_native_spark_compact_epoch.py",
        SIDE + "src/grcv4_explorer/spark_earlier_sc3_metadata.py",
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
        dict(
            schema="p9103-native-spark-publication-epoch-v1",
            predecessor=REVISION,
            checker_sha256=sha((root / SELF).read_bytes()),
            runtime_changed=False,
            old_execution_relabelled=False,
            sources={
                p: dict(
                    before_sha256=sha(original(root, p)),
                    after_sha256=sha((root / p).read_bytes()),
                )
                for p in sorted(CHANGED)
            },
        )
    )


def previous_bytes(root, name):
    root = Path(root).resolve()
    if name not in CHANGED:
        return (root / name).read_bytes()
    value = json.loads((root / PATH).read_bytes())
    if value != manifest(root):
        raise ValueError("unbound native spark regression publication")
    return original(root, name)

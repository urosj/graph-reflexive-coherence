"""Finite native debt reconciliation successor; numerical evidence unchanged."""

import json
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import subprocess

REVISION = "215509f4"
HERE = "implementation/phase-9-grcv4/verification/"
SIDE = "implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool/"
SELF = HERE + "p9105_native_spark_epoch.py"
PATH = "implementation/phase-9-grcv4/tranche-10/P9-10.5-NativeSpark-SourceEpoch.json"
CHANGED = frozenset(
    {
        HERE + "p9104_native_spark_epoch.py",
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
    from p9106_release_epoch import previous_bytes as successor

    root = Path(root).resolve()
    return seal(
        dict(
            schema="p9105-native-spark-debt-epoch-v1",
            predecessor=REVISION,
            checker_sha256=sha(successor(root, SELF)),
            runtime_changed=False,
            old_execution_relabelled=False,
            sources={
                p: dict(
                    before_sha256=sha(original(root, p)),
                    after_sha256=sha(successor(root, p)),
                )
                for p in sorted(CHANGED)
            },
        )
    )


def previous_bytes(root, name):
    from p9106_release_epoch import previous_bytes as successor

    root = Path(root).resolve()
    if name not in CHANGED:
        return successor(root, name)
    value = json.loads((root / PATH).read_bytes())
    if value != manifest(root):
        raise ValueError("unbound native spark debt reconciliation")
    return original(root, name)

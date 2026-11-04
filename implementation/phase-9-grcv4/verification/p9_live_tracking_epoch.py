"""Finite live-tracking cleanup successor; accepted evidence and ATC unchanged."""

import json
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import subprocess

REVISION = "e65dd3c3"
HERE = "implementation/phase-9-grcv4/verification/"
SIDE = "implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool/"
SELF = HERE + "p9_live_tracking_epoch.py"
PATH = HERE + "Phase9LiveTrackingSourceEpoch.json"
CHANGED = frozenset(
    {
        HERE + "p9106_release_epoch.py",
        HERE + "p991a5_native_spark_compact_epoch.py",
        SIDE + "src/grcv4_explorer/spark_earlier_sc3_metadata.py",
        "implementation/ImplementationPhases.md",
        "implementation/investigations/grc9v4-constitutive-design/README.md",
        "implementation/investigations/grc9v4-constitutive-design/GRC9V4ConstitutiveDesignPlan.md",
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
            schema="phase9-live-tracking-epoch-v1",
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
        raise ValueError("unbound live-tracking cleanup")
    return original(root, name)

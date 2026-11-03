"""Finite A_CI_PC runtime successor; historical execution stays pinned."""

import json
import subprocess
from functools import lru_cache
from hashlib import sha256
from pathlib import Path

REVISION = "10277f05"
HERE = "implementation/phase-9-grcv4/verification/"
SIDE = "implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool/"
SELF = HERE + "p991a6_acipc_epoch.py"
PATH = "implementation/phase-9-grcv4/tranche-9/P9-9.1a.6-ACIPC-SourceEpoch.json"
CHANGED = frozenset(
    [
        "implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool/src/grcv4_explorer/basin.py",
        "implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool/src/grcv4_explorer/spark_earlier_sc3_metadata.py",
        "implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool/src/grcv4_explorer/spark_native_apc.py",
        "implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool/src/grcv4_explorer/spark_native_apc_campaign.py",
        "implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool/src/grcv4_explorer/spark_native_apc_pressure.py",
        "implementation/phase-9-grcv4/verification/p991a6_apc_campaign.py",
        "implementation/phase-9-grcv4/verification/p991a6_apc_campaign_cost.py",
        "implementation/phase-9-grcv4/verification/p991a6_apc_campaign_epoch.py",
        "implementation/phase-9-grcv4/verification/p991a6_apc_preflight.py",
        "implementation/phase-9-grcv4/verification/p991a6_apc_pressure.py",
        "src/pygrc/models/grc_9_v4_completion_certificate.py",
        "src/pygrc/models/grc_9_v4_completion_codec.py",
        "src/pygrc/models/grc_9_v4_spark_contracts.py",
        "src/pygrc/models/grc_9_v4_spark_owner.py",
        "src/pygrc/models/grc_v4_spark.py",
        "src/pygrc/models/grc_v4_spark_adaptive_carrier.py",
    ]
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
    from p991a6_acipc_campaign_epoch import previous_bytes as successor

    root = Path(root).resolve()
    return seal(
        {
            "schema": "p991a6-acipc-runtime-epoch-v1",
            "predecessor": REVISION,
            "checker_sha256": sha(successor(root, SELF)),
            "sources": {
                name: {
                    "before_sha256": sha(original(root, name)),
                    "after_sha256": sha(successor(root, name)),
                }
                for name in sorted(CHANGED)
            },
            "runtime_changed": True,
            "old_execution_relabelled": False,
        }
    )


def previous_bytes(root, name):
    """Authenticate the requested preimage without recursively rereading other files.

    Every returned predecessor binds both its live successor and Git preimage.
    The complete manifest is independently checked at publication; unchanged
    sources pass through for the historical caller's own content check.
    """
    from p991a6_acipc_campaign_epoch import previous_bytes as successor

    root = Path(root).resolve()
    if name not in CHANGED:
        return successor(root, name)
    value = json.loads((root / PATH).read_bytes())
    raw = original(root, name)
    if (
        set(value)
        != {
            "schema",
            "predecessor",
            "checker_sha256",
            "sources",
            "runtime_changed",
            "old_execution_relabelled",
            "record_digest",
        }
        or value != seal(value)
        or value["schema"] != "p991a6-acipc-runtime-epoch-v1"
        or value["predecessor"] != REVISION
        or value["runtime_changed"] is not True
        or value["old_execution_relabelled"] is not False
        or set(value["sources"]) != CHANGED
        or value["checker_sha256"] != sha(successor(root, SELF))
        or value["sources"][name]
        != {
            "before_sha256": sha(raw),
            "after_sha256": sha(successor(root, name)),
        }
    ):
        raise ValueError("unbound A_CI_PC runtime successor")
    return raw

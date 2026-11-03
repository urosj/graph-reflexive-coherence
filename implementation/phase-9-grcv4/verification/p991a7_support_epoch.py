"""Finite capability-reporting successor; accepted execution stays pinned."""

import json
import subprocess
from functools import lru_cache
from hashlib import sha256
from pathlib import Path

REVISION = "528736b9"
HERE = "implementation/phase-9-grcv4/verification/"
SIDE = "implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool/"
SELF = HERE + "p991a7_support_epoch.py"
PATH = "implementation/phase-9-grcv4/tranche-9/P9-9.1a.7-SourceEpoch.json"
CHANGED = frozenset(
    {
        HERE + "p991a5_native_spark_compact_epoch.py",
        HERE + "p991a6_rg2b_campaign_epoch.py",
        HERE + "p991a6_rg2b_campaign.py",
        "src/pygrc/models/grc_9_v4.py",
        "tests/models/test_grc_v4_spark_aos.py",
        "tests/models/test_grc_v4_spark_aci.py",
        "tests/models/test_grc_v4_spark_acipc.py",
        "tests/models/test_grc_v4_spark_cci.py",
        "tests/models/test_grc_v4_spark_cpc.py",
        "tests/models/test_grc_v4_spark_apc.py",
        SIDE + "src/grcv4_explorer/basin.py",
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
        {
            "schema": "p991a7-support-reporting-epoch-v1",
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
        or value["schema"] != "p991a7-support-reporting-epoch-v1"
        or value["predecessor"] != REVISION
        or set(value["sources"]) != CHANGED
        or value["checker_sha256"] != sha((root / SELF).read_bytes())
        or value["runtime_changed"] is not True
        or value["old_execution_relabelled"] is not False
        or value["sources"][name]
        != {"before_sha256": sha(raw), "after_sha256": sha((root / name).read_bytes())}
    ):
        raise ValueError("unbound native support successor")
    return raw

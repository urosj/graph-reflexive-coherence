"""Finite native completion source epoch; retained runs keep their old producer."""
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path
import subprocess

REVISION = "32376cd4"
HERE = "implementation/phase-9-grcv4/verification/"
PATH = "implementation/phase-9-grcv4/tranche-9/P9-9.1a.3-SourceEpoch.json"
SELF = HERE + "p991a3_native_spark_epoch.py"
SIDE = "implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool/"
CHANGED = frozenset({
    *("src/pygrc/models/"+name+".py" for name in (
        "grc_9_v4", "grc_9_v4_api_lifecycle", "grc_9_v4_contracts", "grc_9_v4_crossing",
        "grc_9_v4_identity", "grc_9_v4_lifecycle", "grc_v4_spark_state", "grc_v4_spark_cos")),
    HERE + "p9_spark_document_epoch.py",
    HERE + "p991a2_native_spark_numerics.py",
    SIDE + "src/grcv4_explorer/spark_native_cos.py",
    SIDE + "src/grcv4_explorer/basin.py",
    *(SIDE + "src/grcv4_explorer/"+name+".py" for name in (
        "spark_aci_metadata", "spark_apc_sc3_metadata", "spark_earlier_sc3_metadata",
        "spark_earlier_c_metadata", "spark_apc_metadata", "spark_crg2b_sc3_metadata",
        "spark_crg2b_metadata", "spark_cipc_sc3_metadata", "spark_aos_sc3_metadata",
        "spark_acipc_sc3_metadata", "spark_arg2b_sc3_metadata", "spark_acipc_metadata",
        "spark_arg2b_metadata", "spark_aci_sc3_metadata")),
    *(SIDE + "src/grcv4_explorer/"+name+".py" for name in (
        "spark_aos_earlier_metadata", "spark_cipc_metadata", "spark_aos_metadata")),
})


def sha(raw):
    return sha256(raw).hexdigest()


@lru_cache(maxsize=32)
def original(root, name):
    return subprocess.check_output(["git", "show", REVISION+":"+name], cwd=root)


def seal(value):
    body = {k: v for k, v in value.items() if k != "record_digest"}
    return dict(body, record_digest=sha(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()))


def manifest(root):
    from p991a4_native_spark_epoch import previous_bytes as preflight_previous
    root = Path(root).resolve()
    return seal(dict(schema="p991a3-native-spark-source-epoch-v1", predecessor=REVISION,
        checker_sha256=sha(preflight_previous(root, SELF)),
        sources={name: dict(before_sha256=sha(original(root, name)), after_sha256=sha(preflight_previous(root, name)))
                 for name in sorted(CHANGED)}, old_execution_relabelled=False, acceptance_inferred=False))


def previous_bytes(root, name):
    from p991a4_native_spark_epoch import previous_bytes as preflight_previous
    root = Path(root).resolve()
    if name not in CHANGED:
        return preflight_previous(root, name)
    if json.loads((root/PATH).read_bytes()) != manifest(root):
        raise ValueError("unbound native spark source successor")
    return original(root, name)


def peel_sha(root, name, present):
    if name not in CHANGED:
        return present
    previous = previous_bytes(root, name)
    return sha(previous) if present == sha((Path(root)/name).read_bytes()) else present

"""Finite C_OS storage successor; runtime and historical execution stay pinned."""

import json
import subprocess
from contextlib import contextmanager
from contextvars import ContextVar
from functools import lru_cache
from hashlib import sha256
from pathlib import Path

REVISION = "90e54da1"
HERE = "implementation/phase-9-grcv4/verification/"
SIDE = "implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool/"
SELF = HERE + "p991a5_native_spark_compact_epoch.py"
PATH = "implementation/phase-9-grcv4/tranche-9/P9-9.1a.5-CompactSourceEpoch.json"
CHANGED = frozenset(
    [
        "implementation/phase-9-grcv4/verification/p991a6_arg2b_epoch.py",
        "implementation/phase-9-grcv4/verification/p991a5_native_spark_campaign.py",
        "implementation/phase-9-grcv4/verification/p991a5_native_spark_storage.py",
        "implementation/phase-9-grcv4/verification/test_p991a5_native_spark_campaign.py",
        "implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool/src/grcv4_explorer/basin.py",
        "implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool/src/grcv4_explorer/spark_native_campaign.py",
        "implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool/src/grcv4_explorer/spark_earlier_sc3_metadata.py",
        "implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool/phase9-web/spark-native-campaign.js",
        "implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool/scripts/serve_phase9.py",
        "scripts/evidence_storage.py",
        "tests/test_evidence_storage.py",
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
    from p991a6_rg2b_campaign_epoch import previous_bytes as successor

    root = Path(root).resolve()
    return seal(
        {
            "schema": "p991a5-cos-compact-metadata-epoch-v1",
            "predecessor": REVISION,
            "checker_sha256": sha(successor(root, SELF)),
            "sources": {
                name: {
                    "before_sha256": sha(original(root, name)),
                    "after_sha256": sha(successor(root, name)),
                }
                for name in sorted(CHANGED)
            },
            "runtime_changed": False,
            "old_execution_relabelled": False,
        }
    )


def previous_bytes(root, name):
    """Authenticate the requested preimage without recursively rereading other files.

    Every returned predecessor binds both its live successor and Git preimage.
    The complete manifest is independently checked at publication; unchanged
    sources pass through for the historical caller's own content check.
    """
    from p991a6_rg2b_campaign_epoch import previous_bytes as successor

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
        or value["schema"] != "p991a5-cos-compact-metadata-epoch-v1"
        or value["predecessor"] != REVISION
        or value["runtime_changed"] is not False
        or value["old_execution_relabelled"] is not False
        or set(value["sources"]) != CHANGED
        or value["checker_sha256"] != sha(successor(root, SELF))
        or value["sources"][name]
        != {
            "before_sha256": sha(raw),
            "after_sha256": sha(successor(root, name)),
        }
    ):
        raise ValueError("unbound C_OS storage successor")
    return raw


# Newest first. Each historical manifest remains byte-identical to the accepted
# merged baseline; this audit evaluates the same hash edges once, not recursively.
HISTORY = (
    ("p991a6_arg2b_epoch.py", "P9-9.1a.6-ARG2b-SourceEpoch.json"),
    ("p991a6_crg2b_epoch.py", "P9-9.1a.6-CRG2b-SourceEpoch.json"),
    ("p991a6_acipc_campaign_epoch.py", "P9-9.1a.6-ACIPC.5-SourceEpoch.json"),
    ("p991a6_acipc_epoch.py", "P9-9.1a.6-ACIPC-SourceEpoch.json"),
    ("p991a6_apc_campaign_epoch.py", "P9-9.1a.6-APC.5-SourceEpoch.json"),
    ("p991a6_apc_epoch.py", "P9-9.1a.6-APC-SourceEpoch.json"),
    ("p991a6_aci_campaign_epoch.py", "P9-9.1a.6-ACI.5-SourceEpoch.json"),
    ("p991a6_aci_epoch.py", "P9-9.1a.6-ACI-SourceEpoch.json"),
    ("p991a6_aos_campaign_epoch.py", "P9-9.1a.6-AOS.5-SourceEpoch.json"),
    ("p991a6_aos_epoch.py", "P9-9.1a.6-AOS-SourceEpoch.json"),
    ("p991a6_ccipc_campaign_epoch.py", "P9-9.1a.6-CCIPC.5-SourceEpoch.json"),
    ("p991a6_ccipc_epoch.py", "P9-9.1a.6-CCIPC-SourceEpoch.json"),
    ("p991a6_cpc_campaign_epoch.py", "P9-9.1a.6-CPC.5-SourceEpoch.json"),
    ("p991a6_cpc_epoch.py", "P9-9.1a.6-CPC-SourceEpoch.json"),
    ("p991a6_cci_campaign_epoch.py", "P9-9.1a.6-CCI.5-SourceEpoch.json"),
    ("p991a6_cci_epoch.py", "P9-9.1a.6-CCI-SourceEpoch.json"),
    ("p991a5_native_spark_epoch.py", "P9-9.1a.5-SourceEpoch.json"),
    ("p991a4_native_spark_epoch.py", "P9-9.1a.4-SourceEpoch.json"),
    ("p991a3_native_spark_epoch.py", "P9-9.1a.3-SourceEpoch.json"),
)


@lru_cache(maxsize=512)
def git_blob(root, revision, name):
    # Only immutable Git preimages are cached. Live sources/manifests are reread.
    return subprocess.check_output(["git", "show", revision + ":" + name], cwd=root)


def _validated_history(root):
    """Authenticate a fresh live snapshot against every frozen before/after edge."""
    root = Path(root).resolve()
    import p9103_native_spark_epoch as regression
    regression_value = json.loads((root / regression.PATH).read_bytes())
    if regression_value != regression.manifest(root):
        raise ValueError("unbound native spark regression publication")
    import p991a7_support_epoch as support
    support_value = json.loads((root / support.PATH).read_bytes())
    if support_value != support.manifest(root):
        raise ValueError("unbound native support successor")
    import p991a6_rg2b_campaign_epoch as latest
    successor = json.loads((root / latest.PATH).read_bytes())
    if successor != latest.manifest(root):
        raise ValueError("unbound RG2b campaign successor")
    current = json.loads((root / PATH).read_bytes())
    if current != manifest(root):
        raise ValueError("unbound C_OS storage successor")
    epochs = [(regression.SELF, regression_value), (support.SELF, support_value),
              (latest.SELF, successor), (SELF, current)]
    for checker, filename in HISTORY:
        name = "implementation/phase-9-grcv4/tranche-9/" + filename
        raw = (root / name).read_bytes()
        if raw != git_blob(root, REVISION, name):
            raise ValueError("changed accepted source epoch: " + name)
        value = json.loads(raw)
        if value != seal(value):
            raise ValueError("unsealed historical source epoch")
        epochs.append((HERE + checker, value))
    names = {checker for checker, _ in epochs} | {
        name for _, value in epochs for name in value["sources"]
    }
    snapshot = {name: (root / name).read_bytes() for name in names}
    versions = {name: {sha(raw): raw} for name, raw in snapshot.items()}
    for checker, value in epochs:
        if sha(snapshot[checker]) != value["checker_sha256"]:
            raise ValueError("changed historical checker: " + checker)
        prior = {}
        for name, binding in value["sources"].items():
            before = git_blob(root, value["predecessor"], name)
            if binding != {
                "before_sha256": sha(before),
                "after_sha256": sha(snapshot[name]),
            }:
                raise ValueError("changed historical source edge: " + name)
            prior[name] = before
            versions[name][sha(before)] = before
        snapshot.update(prior)
    return versions


_SNAPSHOT = ContextVar("native_source_history_snapshot", default=None)


def validated_history(root):
    root = Path(root).resolve()
    snapshot = _SNAPSHOT.get()
    if snapshot is not None and snapshot[0] == root:
        return snapshot[1]
    return _validated_history(root)


@contextmanager
def history_snapshot(root):
    """Reuse one authenticated read batch; reject any source drift at its end."""
    root = Path(root).resolve()
    versions = _validated_history(root)
    token = _SNAPSHOT.set((root, versions))
    try:
        yield versions
    finally:
        _SNAPSHOT.reset(token)
        if _validated_history(root) != versions:
            raise ValueError("native source history changed during inspection")


def reviewed_bytes(root, name, expected):
    history = validated_history(root)
    if name not in history:
        return None
    # An older scientific version may precede this finite native chain. Its
    # caller must authenticate it through its own explicit source successor;
    # returning no match is not returning current bytes under an older identity.
    return history[name].get(expected)


def check_sources(root, references):
    root = Path(root).resolve()
    history = validated_history(root)
    for ref in references:
        name, expected = ref["path"], ref["sha256"]
        live = (root / name).read_bytes()
        if sha(live) != expected and expected not in history.get(name, {}):
            raise ValueError("changed campaign source: " + name)

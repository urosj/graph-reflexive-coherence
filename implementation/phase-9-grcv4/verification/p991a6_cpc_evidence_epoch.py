"""Finite publication cleanup; derive discarded prefixes from successful evidence."""

import base64
import json
import lzma
from functools import lru_cache
from hashlib import sha256
from pathlib import Path

BASE = "implementation/phase-9-grcv4/tranche-9/"
SELF = "implementation/phase-9-grcv4/verification/p991a6_cpc_evidence_epoch.py"
PATH = BASE + "P9-9.1a.6-CPC.5-EvidenceEpoch.json"
RECORD = BASE + "P9-9.1a.6-CPC.5-Campaign.json.xz"
EXECUTION_DIGEST = "0f835ad60e0e3d7dcff2aeff731ad2449494d434c4f62ca8c23a5e8c39cc7b0d"
CHANGED = frozenset(
    [
        "implementation/phase-9-grcv4/verification/p991a6_cpc_campaign.py",
        "implementation/phase-9-grcv4/verification/p991a6_cpc_campaign_cost.py",
        "implementation/phase-9-grcv4/verification/p991a6_cpc_resume_cost.py",
        "implementation/phase-9-grcv4/verification/p991a6_cpc_resume_epoch.py",
    ]
)
PREFIXES = {
    BASE + "P9-9.1a.6-CPC.5-reset-prefix.jsonl.xz": (
        BASE + "P9-9.1a.6-CPC.5-reset.jsonl.xz",
        191,
    ),
    BASE + "P9-9.1a.6-CPC.5-checkpoints-prefix.jsonl.xz": (
        BASE + "P9-9.1a.6-CPC.5-checkpoints.jsonl.xz",
        14,
    ),
}


def seal(value):
    body = {k: v for k, v in value.items() if k != "record_digest"}
    return dict(
        body,
        record_digest=sha256(
            json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
    )


def execution(root):
    value = json.loads(lzma.decompress((root / RECORD).read_bytes()))
    if value != seal(value) or value["record_digest"] != EXECUTION_DIGEST:
        raise ValueError("unbound successful C_PC evidence")
    return value


def previous_bytes(root, name):
    root = Path(root)
    if name not in CHANGED:
        return (root / name).read_bytes()
    value = json.loads((root / PATH).read_bytes())
    pins = {r["path"]: r["sha256"] for r in execution(root)["source_bindings"]}
    if (
        value != seal(value)
        or set(value["sources"]) != CHANGED
        or value["checker_sha256"] != sha256((root / SELF).read_bytes()).hexdigest()
    ):
        raise ValueError("unbound evidence cleanup successor")
    for path, row in value["sources"].items():
        raw = base64.b64decode(row["before_base64"], validate=True)
        if (
            sha256(raw).hexdigest() != pins[path]
            or sha256((root / path).read_bytes()).hexdigest() != row["after_sha256"]
        ):
            raise ValueError("changed evidence cleanup source")
    return base64.b64decode(value["sources"][name]["before_base64"], validate=True)


@lru_cache(maxsize=2)
def prefix(raw, count):
    # Streaming and one-shot XZ use the same deterministic preset. Preserve
    # exact original JSONL bytes, including record digests and line endings.
    lines = lzma.decompress(raw).splitlines(keepends=True)
    if len(lines) < count:
        raise ValueError("truncated successful trace")
    return lzma.compress(b"".join(lines[:count]), preset=3)


def evidence_bytes(root, name):
    root = Path(root)
    if name not in PREFIXES:
        return previous_bytes(root, name)
    target, count = PREFIXES[name]
    record = execution(root)
    expected = next(r["sha256"] for r in record["streams"] if r["path"] == target)
    raw = (root / target).read_bytes()
    if sha256(raw).hexdigest() != expected:
        raise ValueError("changed successful trace supplying historical prefix")
    return prefix(raw, count)

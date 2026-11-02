"""Finite adoption of user-authorized profiling semantics after measured cost."""

import base64
import json
from hashlib import sha256
from pathlib import Path

SELF = "implementation/phase-9-grcv4/verification/p991a6_cpc_resume_epoch.py"
PATH = "implementation/phase-9-grcv4/tranche-9/P9-9.1a.6-CPC.5-ResumeSourceEpoch.json"
COST = "implementation/phase-9-grcv4/tranche-9/P9-9.1a.6-CPC.5-ResumeCost.json"
CHANGED = frozenset(
    [
        "implementation/phase-9-grcv4/verification/p991a6_cpc_campaign_resume.py",
        "implementation/phase-9-grcv4/verification/p991a6_cpc_resume_cost.py",
    ]
)
MEASURED_RECORD_DIGEST = (
    "7b392cb0b0198960785cb6f9651096d57c34b8a199ae713cbd1df55bb7e88d50"
)


def seal(value):
    body = {k: v for k, v in value.items() if k != "record_digest"}
    return dict(
        body,
        record_digest=sha256(
            json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
    )


def previous_bytes(root, name):
    from p991a6_cpc_evidence_epoch import previous_bytes as cleanup_previous

    root = Path(root)
    if name not in CHANGED:
        return cleanup_previous(root, name)
    value = json.loads((root / PATH).read_bytes())
    cost = json.loads((root / COST).read_bytes())
    if (
        value != seal(value)
        or cost != seal(cost)
        or cost["record_digest"] != MEASURED_RECORD_DIGEST
        or set(value["sources"]) != CHANGED
        or value["checker_sha256"] != sha256(cleanup_previous(root, SELF)).hexdigest()
    ):
        raise ValueError("unbound profiling policy successor")
    pinned = {r["path"]: r["sha256"] for r in cost["source_bindings"]}
    for path, row in value["sources"].items():
        raw = base64.b64decode(row["before_base64"], validate=True)
        if (
            sha256(raw).hexdigest() != pinned[path]
            or sha256(cleanup_previous(root, path)).hexdigest() != row["after_sha256"]
        ):
            raise ValueError("changed profiling policy source")
    return base64.b64decode(value["sources"][name]["before_base64"], validate=True)

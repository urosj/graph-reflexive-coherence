"""Bounded user decision over unchanged execution records; no numerical rerun."""

import hashlib
import json
from pathlib import Path

BASE = "implementation/phase-9-grcv4/tranche-9/"
FAMILIES = ("C_OS", "C_CI", "A_CI", "A_PC")
PATH = BASE + "P9-9.1b-Acceptance.json"
DECISION_DIGEST = "cb2bc3e4f78320100bab748539c83e5fa884410c624bf71c5e89e50045afc1c7"
CONTEXT = {
    "implementation/phase-9-grcv4/verification/" + name
    for name in (
        "p991b_lifecycle.py",
        "phase9_implementation_policy.py",
        "phase9_specialization_acceptance.py",
    )
}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def seal(value):
    return sha(
        json.dumps(
            {k: v for k, v in value.items() if k != "record_digest"},
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode()
    )


def decision(root):
    value = json.loads((Path(root) / PATH).read_bytes())
    if (
        value["record_digest"] != seal(value)
        or value["record_digest"] != DECISION_DIGEST
        or not value["user_accepted"]
        or value["families"] != list(FAMILIES)
        or not value["bounded_leaf_closed"]
        or value["aggregate_closed"]
        or value["full_GRC9V4_conformance"]
        or set(value["execution_context_preimages"]) != CONTEXT
    ):
        raise ValueError("invalid bounded lifecycle acceptance")
    for preimage in value["execution_context_preimages"].values():
        if sha(preimage["text"].encode()) != preimage["sha256"]:
            raise ValueError("accepted executor preimage mismatch")
    return value


def check(root, family):
    root = Path(root).resolve()
    accepted = decision(root)
    if family not in FAMILIES:
        raise ValueError("unaccepted family")
    ref = accepted["executions"][family]
    if ref["path"] != BASE + "P9-9.1b-" + family + ".json":
        raise ValueError("unexpected execution path")
    raw = (root / ref["path"]).read_bytes()
    value = json.loads(raw)
    if (
        sha(raw) != ref["sha256"]
        or value["record_digest"] != ref["record_digest"]
        or seal(value) != value["record_digest"]
    ):
        raise ValueError("accepted execution changed")
    for row in value["source_refs"] + value["input_refs"]:
        name = row["path"]
        path = (root / name).resolve()
        if Path(name).is_absolute() or not path.is_relative_to(root):
            raise ValueError("nonportable execution input")
        if name in CONTEXT:
            actual = accepted["execution_context_preimages"][name]["sha256"]
        else:
            actual = sha(path.read_bytes())
        if actual != row["sha256"]:
            raise ValueError("accepted execution input drift: " + name)
    return value
